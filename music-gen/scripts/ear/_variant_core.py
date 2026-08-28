"""Shared training core for M-EAR-1/head-regularization-audit variants.

Provides a build-head-parameterized `_fit` and `train_and_eval` that
mirror `scripts.ear.model._fit` / `train_and_eval` exactly except for:

  - the head factory (`build_head(feat_dim) -> nn.Module`), and
  - the Adam `weight_decay` value.

Everything else (loss, optimizer, CV splitter, determinism envelope,
seed regime, NaN imputation, majority/mean-integer baselines) is
byte-identical to the frozen cycle-6 chassis.

Non-factor isolation: NO import of scripts.classifier.sidecar_nonfactor.
Interpreter guard: `/usr/bin/python3` via `._interp`.
"""
# created: 2026-08-28T20:15:00Z  cycle: 23  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 3fbd8c1ab57c)  milestone: M-EAR-1/head-regularization-audit
from __future__ import annotations
from . import _interp  # noqa: F401 — interpreter guard

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

from typing import Callable
from collections import Counter

import numpy as np
import torch
import torch.nn as nn

from .corn import corn_loss, corn_predict
from .model import FoldMetrics, K, EPOCHS, LR, set_determinism, kendall_tau

# ---------------------------------------------------------------------------
# Preprocessing hook: variants 1 & 2 pass identity; variant 3 injects PCA.
# ---------------------------------------------------------------------------
Preprocess = Callable[[np.ndarray], np.ndarray]

def _identity(X: np.ndarray) -> np.ndarray:
    return X


def make_fit(
    build_head: Callable[[int], nn.Module],
    *,
    weight_decay: float = 1e-3,
    preprocess: Preprocess = _identity,
    lr: float = LR,
) -> Callable[..., np.ndarray]:
    """Return an `_fit` bound to a specific head-and-weight-decay pair.

    Signature matches ``scripts.ear.model._fit`` so that
    ``stability_audit._run_one_recipe``'s local
    ``from .model import _fit`` (monkey-patched at driver time) sees the
    same call convention.
    """
    def _fit(X_tr, y_tr, X_te, y_te, seed: int, epochs: int = EPOCHS) -> np.ndarray:
        set_determinism(seed)
        X_tr_p = preprocess(X_tr)
        X_te_p = preprocess(X_te)
        feat_dim = X_tr_p.shape[1]
        model = build_head(feat_dim)
        opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        Xt = torch.from_numpy(X_tr_p.astype(np.float32))
        yt = torch.from_numpy(y_tr.astype(np.int64))
        Xe = torch.from_numpy(X_te_p.astype(np.float32))
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
    return _fit


def make_train_and_eval(fit_fn: Callable[..., np.ndarray]) -> Callable[..., list[FoldMetrics]]:
    """Return a `train_and_eval` that uses the given fit_fn per fold.

    Byte-mirrors ``scripts.ear.model.train_and_eval`` except for the
    fold-fit call.
    """
    def train_and_eval(
        X: np.ndarray, y: np.ndarray, *, seed: int = 0, n_splits: int = 5, epochs: int = EPOCHS
    ) -> list[FoldMetrics]:
        from sklearn.model_selection import StratifiedKFold
        set_determinism(seed)
        X = X.astype(np.float32).copy()
        col_mean = np.nanmean(X, axis=0)
        for j in range(X.shape[1]):
            m = np.isnan(X[:, j])
            X[m, j] = 0.0 if not np.isfinite(col_mean[j]) else col_mean[j]

        strat_key = y.copy()
        cnt = Counter(strat_key.tolist())
        if any(v < n_splits for v in cnt.values()):
            strat_key = np.clip(np.round((y - 1) / 2), 0, 3).astype(int)

        kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        per_fold: list[FoldMetrics] = []
        for fi, (tr_idx, te_idx) in enumerate(kf.split(X, strat_key)):
            X_tr, y_tr = X[tr_idx], y[tr_idx]
            X_te, y_te = X[te_idx], y[te_idx]
            pred = fit_fn(X_tr, y_tr, X_te, y_te, seed=seed + fi, epochs=epochs)
            mae = float(np.mean(np.abs(pred - y_te)))
            off1 = float(np.mean(np.abs(pred - y_te) <= 1))
            tau = kendall_tau(y_te, pred)
            maj = int(np.bincount(y_tr, minlength=K + 1).argmax())
            maj_mae = float(np.mean(np.abs(maj - y_te)))
            mn_int = int(round(float(np.mean(y_tr))))
            mn_mae = float(np.mean(np.abs(mn_int - y_te)))
            per_fold.append(FoldMetrics(fi, mae, off1, tau, maj_mae, mn_mae))
        return per_fold
    return train_and_eval
