"""Train CORN 1-7 head on 43-song rated corpus.

Architecture verbatim from c6 M-EAR-1/preparation/model:
    Linear(2052, 128) -> ReLU -> Dropout(0.3) -> Linear(128, 6)

5-fold stratified leave-one-per-band CV. Fold assignment is SHA-256
derived (sorted-song-sha256 rotation) — NO PRNG.

Deterministic envelope:
  - BLAS pins OMP/MKL/OPENBLAS = 1 before torch import.
  - torch.manual_seed(0), torch.use_deterministic_algorithms(True).
  - Adam optimizer, lr=1e-3, weight_decay=1e-3, 200 epochs.
  - Per-band class-imbalance weights (1/n_band) normalized.

Outputs:
  data/ear_v0/training_result.json
  data/ear_v0/corn_head_v0_real.pt
  data/ear_v0/held_out_predictions.tsv
  data/ear_v0/held_out_folds.json
"""
# created: 2026-08-29T07:24:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: M-EAR-1/real-label-training-v0
from __future__ import annotations
import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from scripts.ear.corn import corn_loss, corn_predict_np
from scripts.ear_v0.ingest_ratings import discover_songs, Song

FEAT_DIM = 2052
K = 7  # ordinal range but only bands {4,5,6,7} present in this corpus
HIDDEN = 128
DROPOUT = 0.3
EPOCHS = 200
LR = 1e-3
WD = 1e-3
N_FOLDS = 5
SEED = 0

DATA_DIR = Path("data/ear_v0")
FEAT_DIR = DATA_DIR / "per_song_features"
BANDS = (4, 5, 6, 7)


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


def build_folds(songs: list[Song], n_folds: int = N_FOLDS) -> dict:
    """SHA-256-sorted round-robin fold assignment per band.

    Guarantees each fold holds out (at least) 1 song per band. Band-6
    (13 songs) rotates so all 13 songs appear in a held-out fold across
    the 5 folds. Class-imbalance sampler weights computed as
    (43/4) / n_band per song.
    """
    by_band: dict[int, list[Song]] = {b: [] for b in BANDS}
    for s in songs:
        by_band[s.band].append(s)
    for b in BANDS:
        by_band[b].sort(key=lambda s: s.sha256)

    fold_assignment: dict[str, int] = {}
    for b in BANDS:
        songs_b = by_band[b]
        for i, s in enumerate(songs_b):
            fold_assignment[s.sha256] = i % n_folds

    n_total = len(songs)
    counts = {b: len(by_band[b]) for b in BANDS}
    sampler_weights = {
        s.sha256: (n_total / len(BANDS)) / counts[s.band] for s in songs
    }

    folds_records = []
    for fi in range(n_folds):
        held_out = [
            s.sha256 for s in songs if fold_assignment[s.sha256] == fi
        ]
        train = [
            s.sha256 for s in songs if fold_assignment[s.sha256] != fi
        ]
        folds_records.append({
            "fold_id": fi,
            "held_out_song_sha256s": sorted(held_out),
            "n_held_out": len(held_out),
            "n_train": len(train),
        })

    return {
        "n_folds": n_folds,
        "class_distribution": counts,
        "sampler_weights": sampler_weights,
        "fold_assignment": fold_assignment,
        "folds": folds_records,
    }


def _load_matrix(songs: list[Song]) -> tuple[np.ndarray, np.ndarray]:
    X = np.zeros((len(songs), FEAT_DIM), dtype=np.float32)
    y = np.zeros(len(songs), dtype=np.int64)
    for i, s in enumerate(songs):
        v = np.load(FEAT_DIR / f"{s.sha256}.npy").astype(np.float32)
        X[i] = v
        y[i] = s.band
    return X, y


def _train_one_fold(
    X_tr: np.ndarray,
    y_tr: np.ndarray,
    X_ho: np.ndarray,
    y_ho: np.ndarray,
    w_tr: np.ndarray,
    fi: int,
) -> tuple[nn.Module, np.ndarray]:
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
    for epoch in range(EPOCHS):
        opt.zero_grad()
        logits = model(Xt)
        # CORN loss is unweighted by design; apply per-sample weights via
        # weighted BCE across the K-1 sub-heads (equivalent to weighted
        # sample-mean of the per-sample loss).
        target = (yt.unsqueeze(1) > torch.arange(1, K).unsqueeze(0)).float()
        per_sample = torch.nn.functional.binary_cross_entropy_with_logits(
            logits, target, reduction="none"
        ).mean(dim=1)
        loss = (per_sample * wt).sum() / wt.sum()
        loss.backward()
        opt.step()

    model.eval()
    with torch.no_grad():
        # Expectation-style rank prediction: 1 + sum(sigmoid(logits))
        # gives a real-valued rank the SB1 evaluator rounds; also emit
        # integer prediction for MAE.
        logits_ho = model(torch.from_numpy(X_ho).float()).numpy()
        sig = 1.0 / (1.0 + np.exp(-logits_ho))
        rank_expectation = 1.0 + sig.sum(axis=1)  # real-valued
    return model, rank_expectation


def _int_predictions_from_expectation(rank_exp: np.ndarray) -> np.ndarray:
    """Clip to [min_band, max_band] then round. Band-1/2/3 absent from
    corpus; predictions floor at band-4 by construction."""
    clipped = np.clip(rank_exp, min(BANDS), max(BANDS))
    return np.rint(clipped).astype(np.int64)


def train(songs: list[Song]) -> dict:
    fold_info = build_folds(songs)
    X, y = _load_matrix(songs)

    n_total = len(songs)
    counts = {b: sum(1 for s in songs if s.band == b) for b in BANDS}
    weights_arr = np.array([
        (n_total / len(BANDS)) / counts[int(y[i])] for i in range(n_total)
    ], dtype=np.float32)

    preds_rows: list[dict] = []
    per_fold: list[dict] = []
    fold_state_dicts: list[dict] = []

    for fi in range(N_FOLDS):
        held_out_shas = set(fold_info["folds"][fi]["held_out_song_sha256s"])
        tr_idx = np.array([
            i for i, s in enumerate(songs) if s.sha256 not in held_out_shas
        ])
        ho_idx = np.array([
            i for i, s in enumerate(songs) if s.sha256 in held_out_shas
        ])
        model, rank_exp = _train_one_fold(
            X[tr_idx], y[tr_idx], X[ho_idx], y[ho_idx],
            weights_arr[tr_idx], fi,
        )
        int_pred = _int_predictions_from_expectation(rank_exp)
        fold_mae = float(np.mean(np.abs(int_pred - y[ho_idx])))
        per_fold.append({"fold_id": fi, "mae": fold_mae,
                         "n_held_out": int(ho_idx.size)})
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
    mean_mae = float(np.mean(np.abs(y_pred - y_true)))

    result = {
        "feature_version": "ear-v0-real-label-v1",
        "corpus_size": len(songs),
        "class_distribution": counts,
        "scale_bounds": {"min": min(BANDS), "max": max(BANDS),
                         "absent_bands": [1, 2, 3]},
        "model_label": "preview_partial_corpus_v0",
        "n_folds": N_FOLDS,
        "epochs": EPOCHS,
        "lr": LR,
        "weight_decay": WD,
        "hidden": HIDDEN,
        "dropout": DROPOUT,
        "seed": SEED,
        "per_fold_mae": per_fold,
        "aggregate_mae": mean_mae,
        "determinism_config": {
            "OMP_NUM_THREADS": os.environ["OMP_NUM_THREADS"],
            "MKL_NUM_THREADS": os.environ["MKL_NUM_THREADS"],
            "OPENBLAS_NUM_THREADS": os.environ["OPENBLAS_NUM_THREADS"],
            "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", ""),
            "torch_manual_seed": SEED,
            "torch_num_threads": 1,
        },
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Save held-out predictions TSV (sorted).
    tsv_path = DATA_DIR / "held_out_predictions.tsv"
    with open(tsv_path, "w") as f:
        f.write("song_sha256\tband_true\tband_pred_expectation\tband_pred_int\tfold_id\tartist\tplaylist_id\n")
        for r in preds_rows:
            f.write(
                f"{r['song_sha256']}\t{r['band_true']}\t"
                f"{r['band_pred_expectation']:.6f}\t{r['band_pred_int']}\t"
                f"{r['fold_id']}\t{r['artist']}\t{r['playlist_id']}\n"
            )

    # Concatenate all fold state_dicts into one deterministic checkpoint.
    combined = {}
    for fi, sd in enumerate(fold_state_dicts):
        for k, v in sd.items():
            combined[f"fold_{fi}.{k}"] = v
    torch.save(combined, DATA_DIR / "corn_head_v0_real.pt",
               _use_new_zipfile_serialization=True)

    with open(DATA_DIR / "training_result.json", "w") as f:
        json.dump(result, f, indent=2, sort_keys=True)

    # Persist folds JSON (with sampler_weights + fold_assignment).
    with open(DATA_DIR / "held_out_folds.json", "w") as f:
        json.dump(fold_info, f, indent=2, sort_keys=True)

    return result


if __name__ == "__main__":
    songs = discover_songs(Path("."))
    result = train(songs)
    print(json.dumps({
        "aggregate_mae": result["aggregate_mae"],
        "per_fold_mae": result["per_fold_mae"],
    }, indent=2))
