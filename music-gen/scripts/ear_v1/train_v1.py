#!/usr/bin/python3
"""Train the c6 CORN 1-7 head on the 43-song rated corpus (v1).

Architecture verbatim from c6 scripts/ear/model.py:
    Linear(2052, 128) -> ReLU -> Dropout(0.3) -> Linear(128, 6)

CV: 5-fold stratified leave-one-per-band across 43 songs. Fold
assignment is SHA-256 derived (sorted-song-sha256 round-robin per
band); NO PRNG. Each held-out fold covers at least 1 song per band.

Deterministic envelope: OMP/MKL/OPENBLAS = 1, torch.manual_seed(0),
torch.set_num_threads(1), torch.use_deterministic_algorithms(True,
warn_only=True). Adam(lr=1e-3, wd=1e-3), 200 epochs.

Outputs (under data/ear_v1/):
  - training_result.json  (per-fold MAE + baselines + per-song oof preds)
  - corn_head_v1.pt       (deterministic combined state_dict)
  - held_out_predictions.tsv
  - held_out_folds.json
"""
# created: 2026-08-29T11:06:00Z  cycle: 38  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0)  milestone: M-EAR-1/real-label-training-v1
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756800000")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from scripts.ear_v1.ingest_ratings import discover_songs, Song, BANDS
from scripts.ear_v1.features_v1 import load_matrix, FEAT_DIM

K = 7
HIDDEN = 128
DROPOUT = 0.3
EPOCHS = 200
LR = 1e-3
WD = 1e-3
N_FOLDS = 5
SEED = 0

DATA_DIR = Path("data/ear_v1")


class CornHead(nn.Module):
    def __init__(self, feat_dim=FEAT_DIM):
        super().__init__()
        self.body = nn.Sequential(
            nn.Linear(feat_dim, HIDDEN),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(HIDDEN, K - 1),
        )

    def forward(self, x):
        return self.body(x)


def build_folds(songs: list[Song]) -> dict:
    by_band: dict[int, list[Song]] = {b: [] for b in BANDS}
    for s in songs:
        by_band[s.band].append(s)
    for b in BANDS:
        by_band[b].sort(key=lambda s: s.sha256)
    fold_assignment: dict[str, int] = {}
    for b in BANDS:
        for i, s in enumerate(by_band[b]):
            fold_assignment[s.sha256] = i % N_FOLDS
    n_total = len(songs)
    counts = {b: len(by_band[b]) for b in BANDS}
    sampler_weights = {
        s.sha256: (n_total / len(BANDS)) / counts[s.band] for s in songs
    }
    folds_records = []
    for fi in range(N_FOLDS):
        held = sorted([s.sha256 for s in songs
                       if fold_assignment[s.sha256] == fi])
        train = [s.sha256 for s in songs
                 if fold_assignment[s.sha256] != fi]
        folds_records.append({
            "fold_id": fi, "held_out_song_sha256s": held,
            "n_held_out": len(held), "n_train": len(train),
        })
    return {
        "n_folds": N_FOLDS,
        "class_distribution": counts,
        "sampler_weights": sampler_weights,
        "fold_assignment": fold_assignment,
        "folds": folds_records,
    }


def _train_one_fold(X_tr, y_tr, X_ho, w_tr, fi):
    torch.manual_seed(SEED + fi)
    torch.set_num_threads(1)
    try:
        torch.use_deterministic_algorithms(True, warn_only=True)
    except Exception:
        pass
    model = CornHead()
    opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WD)
    Xt = torch.from_numpy(X_tr).float()
    yt = torch.from_numpy(y_tr).long()
    wt = torch.from_numpy(w_tr.astype(np.float32))
    model.train()
    for _ in range(EPOCHS):
        opt.zero_grad()
        logits = model(Xt)
        target = (yt.unsqueeze(1) > torch.arange(1, K).unsqueeze(0)).float()
        per_sample = torch.nn.functional.binary_cross_entropy_with_logits(
            logits, target, reduction="none"
        ).mean(dim=1)
        loss = (per_sample * wt).sum() / wt.sum()
        loss.backward()
        opt.step()
    model.eval()
    with torch.no_grad():
        logits_ho = model(torch.from_numpy(X_ho).float()).numpy()
        sig = 1.0 / (1.0 + np.exp(-logits_ho))
        rank_expectation = 1.0 + sig.sum(axis=1)
    return model, rank_expectation


def _int_preds(rank_exp: np.ndarray) -> np.ndarray:
    clipped = np.clip(rank_exp, min(BANDS), max(BANDS))
    return np.rint(clipped).astype(np.int64)


def train(songs: list[Song]) -> dict:
    fold_info = build_folds(songs)
    X, y = load_matrix(songs)
    counts = {b: sum(1 for s in songs if s.band == b) for b in BANDS}
    n_total = len(songs)
    weights_arr = np.array([
        (n_total / len(BANDS)) / counts[int(y[i])] for i in range(n_total)
    ], dtype=np.float32)

    preds_rows: list[dict] = []
    per_fold: list[dict] = []
    fold_state_dicts: list[dict] = []

    for fi in range(N_FOLDS):
        held_shas = set(fold_info["folds"][fi]["held_out_song_sha256s"])
        tr_idx = np.array([
            i for i, s in enumerate(songs) if s.sha256 not in held_shas
        ])
        ho_idx = np.array([
            i for i, s in enumerate(songs) if s.sha256 in held_shas
        ])
        model, rank_exp = _train_one_fold(
            X[tr_idx], y[tr_idx], X[ho_idx], weights_arr[tr_idx], fi,
        )
        int_pred = _int_preds(rank_exp)
        fold_mae = float(np.mean(np.abs(int_pred - y[ho_idx])))
        per_fold.append({
            "fold_id": fi, "mae": fold_mae,
            "n_held_out": int(ho_idx.size),
        })
        for j, k in enumerate(ho_idx):
            s = songs[int(k)]
            preds_rows.append({
                "song_sha256": s.sha256,
                "band_true": int(y[int(k)]),
                "band_pred_expectation": float(rank_exp[j]),
                "band_pred_int": int(int_pred[j]),
                "fold_id": fi,
                "artist": s.artist,
                "playlist_id": s.playlist_id,
            })
        fold_state_dicts.append(
            {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        )

    preds_rows.sort(key=lambda r: (r["fold_id"], r["song_sha256"]))
    y_true = np.array([r["band_true"] for r in preds_rows])
    y_pred = np.array([r["band_pred_int"] for r in preds_rows])
    aggregate_mae = float(np.mean(np.abs(y_pred - y_true)))

    # Baselines (majority-class, mean-integer).
    vals, cnts = np.unique(y_true, return_counts=True)
    majority = int(vals[np.argmax(cnts)])
    mean_int = int(round(float(y_true.mean())))
    majority_mae = float(np.mean(np.abs(y_true - majority)))
    mean_int_mae = float(np.mean(np.abs(y_true - mean_int)))

    result = {
        "feature_version": "ear-v1-real-label-v1",
        "corpus_size": len(songs),
        "class_distribution": counts,
        "scale_bounds": {"min": min(BANDS), "max": max(BANDS),
                         "absent_bands": [1, 2, 3]},
        "model_label": "preview_partial_corpus_v1",
        "n_folds": N_FOLDS,
        "epochs": EPOCHS,
        "lr": LR,
        "weight_decay": WD,
        "hidden": HIDDEN,
        "dropout": DROPOUT,
        "seed": SEED,
        "per_fold_mae": per_fold,
        "aggregate_mae": aggregate_mae,
        "baseline_majority_mae": majority_mae,
        "baseline_majority_value": majority,
        "baseline_mean_int_mae": mean_int_mae,
        "baseline_mean_int_value": mean_int,
        "determinism_config": {
            "OMP_NUM_THREADS": os.environ["OMP_NUM_THREADS"],
            "MKL_NUM_THREADS": os.environ["MKL_NUM_THREADS"],
            "OPENBLAS_NUM_THREADS": os.environ["OPENBLAS_NUM_THREADS"],
            "PYTHONHASHSEED": os.environ["PYTHONHASHSEED"],
            "SOURCE_DATE_EPOCH": os.environ["SOURCE_DATE_EPOCH"],
            "TZ": os.environ["TZ"],
            "LC_ALL": os.environ["LC_ALL"],
            "torch_manual_seed": SEED,
            "torch_num_threads": 1,
        },
        "per_song_oof_predictions": preds_rows,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Held-out preds TSV, sorted.
    tsv_path = DATA_DIR / "held_out_predictions.tsv"
    with open(tsv_path, "w") as f:
        f.write("song_sha256\tband_true\tband_pred_expectation\t"
                "band_pred_int\tfold_id\tartist\tplaylist_id\n")
        for r in preds_rows:
            f.write(
                f"{r['song_sha256']}\t{r['band_true']}\t"
                f"{r['band_pred_expectation']:.6f}\t{r['band_pred_int']}\t"
                f"{r['fold_id']}\t{r['artist']}\t{r['playlist_id']}\n"
            )

    # Deterministic combined state dict.
    combined = {}
    for fi, sd in enumerate(fold_state_dicts):
        for k, v in sd.items():
            combined[f"fold_{fi}.{k}"] = v
    torch.save(combined, DATA_DIR / "corn_head_v1.pt",
               _use_new_zipfile_serialization=True)

    with open(DATA_DIR / "training_result.json", "w") as f:
        json.dump(result, f, indent=2, sort_keys=True)
    with open(DATA_DIR / "held_out_folds.json", "w") as f:
        json.dump(fold_info, f, indent=2, sort_keys=True)

    return result


if __name__ == "__main__":
    from pathlib import Path
    songs = discover_songs(Path("."))
    r = train(songs)
    print(json.dumps({"aggregate_mae": r["aggregate_mae"],
                       "per_fold_mae": r["per_fold_mae"]}, indent=2))
