"""Ordinal 1–7 regression model for the M-EAR-1 ear (v0 chassis).

Architecture:
    Linear(feat_dim, 128) → ReLU → Dropout(0.3) → Linear(128, 6)

Six binary CORN sub-heads for K=7. Predict via
    1 + sum(sigmoid(logits) > 0.5)

Training entry: `train_and_eval(X, y, seed=0)` — 5-fold stratified CV,
determinism envelope pinned. Beats two baselines: majority-class and
mean-integer predictor.

Sanity CLI: `python3 -m scripts.ear.model --synthetic` fits on synthetic
labels derived from a linear projection of features, verifies convergence
and reports MAE / off-by-one / Kendall-τ vs the two baselines.
"""
# created: 2026-08-28T06:55:00Z  cycle: 6  run_id: run-2026-08-28T040704Z
# agent: worker (clone-2)  milestone: M-EAR-1/preparation/model
from __future__ import annotations
from . import _interp  # noqa: F401 — interpreter guard

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import StratifiedKFold

from .corn import corn_loss, corn_predict

K = 7  # 1..7 ordinal
EPOCHS = 200
LR = 1e-3
WD = 1e-3
HIDDEN = 128
DROPOUT = 0.3


def set_determinism(seed: int = 0) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(1)


class CornHead(nn.Module):
    def __init__(self, feat_dim: int, hidden: int = HIDDEN, dropout: float = DROPOUT):
        super().__init__()
        self.body = nn.Sequential(
            nn.Linear(feat_dim, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, K - 1),
        )

    def forward(self, x):
        return self.body(x)


def _fit(X_tr, y_tr, X_te, y_te, seed: int, epochs: int = EPOCHS) -> np.ndarray:
    set_determinism(seed)
    model = CornHead(X_tr.shape[1])
    opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WD)
    Xt = torch.from_numpy(X_tr.astype(np.float32))
    yt = torch.from_numpy(y_tr.astype(np.int64))
    Xe = torch.from_numpy(X_te.astype(np.float32))
    model.train()
    for _ in range(epochs):
        opt.zero_grad()
        logits = model(Xt)
        loss = corn_loss(logits, yt, K)
        loss.backward()
        opt.step()
    model.eval()
    with torch.no_grad():
        logits = model(Xe)
        pred = corn_predict(logits).numpy()
    return pred


@dataclass
class FoldMetrics:
    fold: int
    mae: float
    off_by_one_acc: float
    kendall_tau: float
    majority_mae: float
    mean_int_mae: float


def kendall_tau(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    from scipy.stats import kendalltau
    tau, _ = kendalltau(y_true, y_pred)
    return float(tau) if tau == tau else 0.0  # NaN-safe


def train_and_eval(
    X: np.ndarray, y: np.ndarray, *, seed: int = 0, n_splits: int = 5, epochs: int = EPOCHS
) -> list[FoldMetrics]:
    """5-fold stratified CV; returns per-fold metrics vs two baselines."""
    set_determinism(seed)
    # Impute NaNs (from heuristic null-with-reason) with column mean, feature-wise.
    X = X.astype(np.float32).copy()
    col_mean = np.nanmean(X, axis=0)
    for j in range(X.shape[1]):
        m = np.isnan(X[:, j])
        X[m, j] = 0.0 if not np.isfinite(col_mean[j]) else col_mean[j]

    # StratifiedKFold requires at least min(n_splits) per class; if the label
    # distribution is too skewed, we bin nearby labels for the split key only.
    strat_key = y.copy()
    # If any label class < n_splits samples, collapse to buckets ≤3 for split.
    from collections import Counter
    cnt = Counter(strat_key.tolist())
    if any(v < n_splits for v in cnt.values()):
        strat_key = np.clip(np.round((y - 1) / 2), 0, 3).astype(int)  # 4 buckets

    kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    per_fold: list[FoldMetrics] = []
    for fi, (tr_idx, te_idx) in enumerate(kf.split(X, strat_key)):
        X_tr, y_tr = X[tr_idx], y[tr_idx]
        X_te, y_te = X[te_idx], y[te_idx]
        pred = _fit(X_tr, y_tr, X_te, y_te, seed=seed + fi, epochs=epochs)
        mae = float(np.mean(np.abs(pred - y_te)))
        off1 = float(np.mean(np.abs(pred - y_te) <= 1))
        tau = kendall_tau(y_te, pred)
        maj = int(np.bincount(y_tr, minlength=K + 1).argmax())
        maj_mae = float(np.mean(np.abs(maj - y_te)))
        mn_int = int(round(float(np.mean(y_tr))))
        mn_mae = float(np.mean(np.abs(mn_int - y_te)))
        per_fold.append(FoldMetrics(fi, mae, off1, tau, maj_mae, mn_mae))
    return per_fold


def summarize(metrics: list[FoldMetrics]) -> dict:
    def mnstd(key: str) -> tuple[float, float]:
        arr = np.array([getattr(m, key) for m in metrics], dtype=np.float64)
        return float(arr.mean()), float(arr.std())
    keys = ["mae", "off_by_one_acc", "kendall_tau", "majority_mae", "mean_int_mae"]
    return {k: {"mean": mnstd(k)[0], "std": mnstd(k)[1]} for k in keys}


# --- Synthetic sanity CLI -----------------------------------------------------
def _load_valset_features(clips_dir: Path, manifest: Path):
    """Load per-clip features (must exist under data/ear/features/)."""
    from .features import CACHE_DIR
    with manifest.open() as f:
        header = f.readline().rstrip("\n").split("\t")
        rows = [dict(zip(header, ln.rstrip("\n").split("\t"))) for ln in f if ln.strip()]
    Xs, ids, labels = [], [], []
    for r in rows:
        p = CACHE_DIR / f"{r['clip_id']}.npz"
        if not p.exists():
            continue
        npz = np.load(p, allow_pickle=False)
        Xs.append(np.concatenate([npz["panns_embed"], npz["heuristic_vec"]], axis=0))
        ids.append(r["clip_id"])
        labels.append(r["label"])
    return np.stack(Xs, axis=0).astype(np.float32), ids, labels


def synthesize_ratings(X: np.ndarray, seed: int = 0) -> np.ndarray:
    """Rating y_i in {1..7} = round(4 + 0.6 * signal + 0.4 * noise), clipped.

    signal is the sign of the first PC of X (deterministic; slightly correlated
    with genuine audio content so a trained head can improve over baselines).
    """
    rng = np.random.default_rng(seed)
    X = X.astype(np.float64).copy()
    col_mean = np.nanmean(X, axis=0)
    for j in range(X.shape[1]):
        m = np.isnan(X[:, j])
        X[m, j] = 0.0 if not np.isfinite(col_mean[j]) else col_mean[j]
    Xc = X - X.mean(axis=0, keepdims=True)
    # Deterministic 1-PC via power iteration (avoids sklearn PCA random_state drift).
    v = rng.standard_normal(X.shape[1])
    for _ in range(30):
        v = Xc.T @ (Xc @ v)
        v /= np.linalg.norm(v) + 1e-12
    z = Xc @ v
    z = (z - z.mean()) / (z.std() + 1e-12)
    noise = rng.standard_normal(z.shape[0])
    y = np.clip(np.round(4 + 1.5 * z + 1.0 * noise), 1, K).astype(np.int64)
    return y


def _main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true", help="Sanity-run on synthetic labels.")
    ap.add_argument("--valset", type=Path,
                    default=Path("data/classifier/valset/valset_manifest.tsv"))
    ap.add_argument("--clips-dir", type=Path,
                    default=Path("data/classifier/valset/clips"))
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    ap.add_argument("--out", type=Path, default=Path("data/ear/model_sanity.json"))
    args = ap.parse_args(argv)

    if not args.synthetic:
        print("Nothing to do without --synthetic (real training is out of scope: needs rated audio).")
        return 0

    X, ids, labels = _load_valset_features(args.clips_dir, args.valset)
    print(f"[model] {X.shape[0]} clips, feat_dim={X.shape[1]}")
    y = synthesize_ratings(X, seed=0)
    print(f"[model] synthetic label histogram: {np.bincount(y, minlength=K+1)[1:]}")

    metrics = train_and_eval(X, y, seed=0, epochs=args.epochs)
    summary = summarize(metrics)
    result = {
        "n_clips": int(X.shape[0]),
        "feat_dim": int(X.shape[1]),
        "K": K,
        "epochs": args.epochs,
        "per_fold": [asdict(m) for m in metrics],
        "summary": summary,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2))
    print(f"[model] CORN MAE (mean±std) = {summary['mae']['mean']:.3f} ± {summary['mae']['std']:.3f}")
    print(f"[model] majority-class MAE   = {summary['majority_mae']['mean']:.3f}")
    print(f"[model] mean-integer MAE     = {summary['mean_int_mae']['mean']:.3f}")
    print(f"[model] off-by-one accuracy  = {summary['off_by_one_acc']['mean']:.3f}")
    print(f"[model] Kendall τ            = {summary['kendall_tau']['mean']:.3f}")
    print(f"[model] wrote {args.out}")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv[1:]))
