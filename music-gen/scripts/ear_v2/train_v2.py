#!/usr/bin/python3
"""Train c6 CORN 1-7 head on per-clip v2 features under GroupKFold.

CV: 5-fold stratified leave-one-per-band per SONG (GroupKFold with
groups=song_sha256). All clips of a given song go entirely into either
the training or the held-out fold — no clip leakage across folds.

Deterministic envelope: OMP/MKL/OPENBLAS=1, torch.manual_seed(0),
torch.set_num_threads(1), torch.use_deterministic_algorithms(True,
warn_only=True). Adam(lr=1e-3, wd=1e-3), 200 epochs.

Outputs under data/ear_v2/:
  - training_result.json         (per-fold MAE + baselines + oof preds)
  - corn_head_v2.pt              (deterministic combined state_dict)
  - held_out_predictions.tsv     (clip-level OOF preds)
  - held_out_folds.json          (fold-assignment record)
"""
# created: 2026-08-29T12:07:00Z  cycle: 39  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: M-EAR-1/real-label-training-v2
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

from scripts.ear_v2.extract_features_v2 import load_matrix, FEAT_DIM

K = 7
BANDS = (4, 5, 6, 7)
HIDDEN = 128
DROPOUT = 0.3
EPOCHS = 200
LR = 1e-3
WD = 1e-3
N_FOLDS = 5
SEED = 0
DATA_DIR = Path("data/ear_v2")


class CornHead(nn.Module):
    """c6 CORN 1-7 head (verbatim architecture)."""
    def __init__(self, feat_dim: int = FEAT_DIM) -> None:
        super().__init__()
        self.body = nn.Sequential(
            nn.Linear(feat_dim, HIDDEN),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(HIDDEN, K - 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.body(x)


def build_song_folds(entries: list[dict]) -> dict:
    """Round-robin per band to assign each song to a fold.

    Sort per-band songs by sha256 then assign fold = i % N_FOLDS.
    Fold assignment is at the SONG level; every clip of a song
    inherits the song's fold.
    """
    # unique songs
    songs: dict[str, dict] = {}
    for e in entries:
        s = e["song_sha256"]
        if s not in songs:
            songs[s] = {"song_sha256": s, "band": int(e["band"])}
    by_band: dict[int, list[str]] = {b: [] for b in BANDS}
    for s in songs.values():
        by_band[int(s["band"])].append(s["song_sha256"])
    for b in BANDS:
        by_band[b].sort()
    fold_assignment: dict[str, int] = {}
    for b in BANDS:
        for i, ss in enumerate(by_band[b]):
            fold_assignment[ss] = i % N_FOLDS
    folds = []
    for fi in range(N_FOLDS):
        held = sorted([s for s, f in fold_assignment.items() if f == fi])
        train = sorted([s for s, f in fold_assignment.items() if f != fi])
        folds.append({
            "fold_id": fi,
            "held_out_song_sha256s": held,
            "train_song_sha256s": train,
            "n_held_out_songs": len(held),
            "n_train_songs": len(train),
        })
    return {
        "n_folds": N_FOLDS,
        "grouping": "song_sha256",
        "stratify": "band",
        "fold_assignment_song": fold_assignment,
        "folds": folds,
        "class_distribution_song": {
            b: len(by_band[b]) for b in BANDS
        },
    }


def _train_one_fold(X_tr: np.ndarray, y_tr: np.ndarray,
                    X_ho: np.ndarray, w_tr: np.ndarray, fi: int
                    ) -> tuple[CornHead, np.ndarray]:
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


def train() -> dict:
    X, y, entries = load_matrix()
    fold_info = build_song_folds(entries)
    fold_assignment_song = fold_info["fold_assignment_song"]
    # Per-clip fold vector via song lookup.
    fold_of_clip = np.array(
        [fold_assignment_song[e["song_sha256"]] for e in entries],
        dtype=np.int64,
    )
    # Per-clip class weight.
    class_counts_clip = {
        b: int(np.sum(y == b)) for b in BANDS
    }
    n_total = int(len(entries))
    weights_arr = np.array([
        (n_total / len(BANDS)) / max(1, class_counts_clip[int(y[i])])
        for i in range(n_total)
    ], dtype=np.float32)

    preds_rows: list[dict] = []
    per_fold: list[dict] = []
    fold_state_dicts: list[dict] = []

    for fi in range(N_FOLDS):
        tr_idx = np.where(fold_of_clip != fi)[0]
        ho_idx = np.where(fold_of_clip == fi)[0]
        model, rank_exp = _train_one_fold(
            X[tr_idx], y[tr_idx], X[ho_idx], weights_arr[tr_idx], fi,
        )
        int_pred = _int_preds(rank_exp)
        fold_mae = float(np.mean(np.abs(int_pred - y[ho_idx])))
        per_fold.append({
            "fold_id": fi,
            "mae": fold_mae,
            "n_held_out_clips": int(ho_idx.size),
            "n_train_clips": int(tr_idx.size),
        })
        for j, k in enumerate(ho_idx):
            e = entries[int(k)]
            preds_rows.append({
                "clip_id": e["clip_id"],
                "song_sha256": e["song_sha256"],
                "clip_idx": int(e["clip_idx"]),
                "band_true": int(y[int(k)]),
                "band_pred_expectation": float(rank_exp[j]),
                "band_pred_int": int(int_pred[j]),
                "fold_id": fi,
                "artist": e["artist"],
                "playlist_id": e["playlist_id"],
                "start_s": float(e["start_s"]),
                "end_s": float(e["end_s"]),
                "tail_anchored": bool(e["tail_anchored"]),
            })
        fold_state_dicts.append({
            k: v.detach().cpu().clone() for k, v in model.state_dict().items()
        })

    preds_rows.sort(key=lambda r: (r["fold_id"], r["clip_id"]))

    # Clip-level aggregate.
    y_true = np.array([r["band_true"] for r in preds_rows])
    y_pred = np.array([r["band_pred_int"] for r in preds_rows])
    aggregate_mae_clip = float(np.mean(np.abs(y_pred - y_true)))
    vals, cnts = np.unique(y_true, return_counts=True)
    majority = int(vals[np.argmax(cnts)])
    mean_int = int(round(float(y_true.mean())))
    majority_mae_clip = float(np.mean(np.abs(y_true - majority)))
    mean_int_mae_clip = float(np.mean(np.abs(y_true - mean_int)))

    # Song-median-aggregated view (cross-comparable with v1).
    from collections import defaultdict
    per_song_preds: dict[str, list[float]] = defaultdict(list)
    per_song_true: dict[str, int] = {}
    for r in preds_rows:
        per_song_preds[r["song_sha256"]].append(r["band_pred_expectation"])
        per_song_true[r["song_sha256"]] = r["band_true"]
    song_rows = []
    for s, exps in per_song_preds.items():
        med_exp = float(np.median(exps))
        clipped = float(np.clip(med_exp, min(BANDS), max(BANDS)))
        int_pred = int(np.rint(clipped))
        song_rows.append({
            "song_sha256": s,
            "band_true": int(per_song_true[s]),
            "band_pred_median_expectation": med_exp,
            "band_pred_int": int_pred,
        })
    song_rows.sort(key=lambda r: r["song_sha256"])
    yst = np.array([r["band_true"] for r in song_rows])
    ysp = np.array([r["band_pred_int"] for r in song_rows])
    aggregate_mae_song = float(np.mean(np.abs(ysp - yst)))
    vals_s, cnts_s = np.unique(yst, return_counts=True)
    majority_s = int(vals_s[np.argmax(cnts_s)])
    mean_int_s = int(round(float(yst.mean())))
    majority_mae_song = float(np.mean(np.abs(yst - majority_s)))
    mean_int_mae_song = float(np.mean(np.abs(yst - mean_int_s)))

    result = {
        "feature_version": "ear-v2-per-clip-v1",
        "milestone": "M-EAR-1/real-label-training-v2",
        "cycle": 39,
        "corpus_size_songs": len(per_song_true),
        "corpus_size_clips": n_total,
        "class_distribution_clips": class_counts_clip,
        "scale_bounds": {"min": min(BANDS), "max": max(BANDS),
                         "absent_bands": [1, 2, 3]},
        "model_label": "resampled_v2_preview_partial_corpus",
        "n_folds": N_FOLDS,
        "grouping": "song_sha256",
        "epochs": EPOCHS,
        "lr": LR,
        "weight_decay": WD,
        "hidden": HIDDEN,
        "dropout": DROPOUT,
        "seed": SEED,
        "per_fold_mae": per_fold,
        "clip_level": {
            "aggregate_mae": aggregate_mae_clip,
            "baseline_majority_mae": majority_mae_clip,
            "baseline_majority_value": majority,
            "baseline_mean_int_mae": mean_int_mae_clip,
            "baseline_mean_int_value": mean_int,
        },
        "song_level_median": {
            "aggregate_mae": aggregate_mae_song,
            "baseline_majority_mae": majority_mae_song,
            "baseline_majority_value": majority_s,
            "baseline_mean_int_mae": mean_int_mae_song,
            "baseline_mean_int_value": mean_int_s,
            "per_song": song_rows,
        },
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
        "per_clip_oof_predictions": preds_rows,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tsv_path = DATA_DIR / "held_out_predictions.tsv"
    with open(tsv_path, "w") as f:
        f.write(
            "clip_id\tsong_sha256\tclip_idx\tband_true\t"
            "band_pred_expectation\tband_pred_int\tfold_id\tartist\t"
            "playlist_id\tstart_s\tend_s\ttail_anchored\n"
        )
        for r in preds_rows:
            f.write(
                f"{r['clip_id']}\t{r['song_sha256']}\t{r['clip_idx']}\t"
                f"{r['band_true']}\t{r['band_pred_expectation']:.6f}\t"
                f"{r['band_pred_int']}\t{r['fold_id']}\t{r['artist']}\t"
                f"{r['playlist_id']}\t{r['start_s']:.6f}\t"
                f"{r['end_s']:.6f}\t{int(r['tail_anchored'])}\n"
            )
    combined = {}
    for fi, sd in enumerate(fold_state_dicts):
        for k, v in sd.items():
            combined[f"fold_{fi}.{k}"] = v
    torch.save(combined, DATA_DIR / "corn_head_v2.pt",
               _use_new_zipfile_serialization=True)
    with open(DATA_DIR / "training_result.json", "w") as f:
        json.dump(result, f, indent=2, sort_keys=True)
    with open(DATA_DIR / "held_out_folds.json", "w") as f:
        json.dump(fold_info, f, indent=2, sort_keys=True)
    return result


if __name__ == "__main__":
    r = train()
    print(json.dumps({
        "aggregate_mae_clip": r["clip_level"]["aggregate_mae"],
        "aggregate_mae_song": r["song_level_median"]["aggregate_mae"],
        "per_fold_mae": r["per_fold_mae"],
    }, indent=2))
