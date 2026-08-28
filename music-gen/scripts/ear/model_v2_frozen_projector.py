"""CORN-frozen-projector variant of the cycle-6 CORN head.

Preprocessing (non-trainable, deterministic, content-pinned):
  - PCA-64 on the 2048-D PANNs component only (M-HEUR-1 4-D untouched).
  - Fit via `numpy.linalg.svd` on the mean-centered 55-clip cache.
  - Basis persisted as `data/ear/head_regularization_audit/pca_basis.npz`
    with SHA-256 sidecar `pca_basis.sha256`.
  - Fitting uses only the 55-clip cache; deterministic under
    OMP/MKL/OPENBLAS=1 single-thread BLAS pins.

Architecture: input [PCA_64(PANNs) ⊕ HEUR_4] (68-D)
  -> Linear(68, 32) -> ReLU -> Linear(32, 6).
Note: brief lists no explicit Dropout for variant 3.

Optimizer: Adam at cycle-6 hyperparameters (lr=1e-3, weight_decay=1e-3).
Hypothesis (registered pre-run): a lower-rank feature representation
reduces the head's freedom to fit label noise; tau rises AND MAE stays
near cycle-6.

Non-factor isolation: NO import of scripts.classifier.sidecar_nonfactor.
Interpreter guard: `/usr/bin/python3`.
"""
# created: 2026-08-28T20:22:00Z  cycle: 23  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 3fbd8c1ab57c)  milestone: M-EAR-1/head-regularization-audit
from __future__ import annotations
from . import _interp  # noqa: F401

import hashlib
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

from pathlib import Path

import numpy as np
import torch.nn as nn

from .model import K
from ._variant_core import make_fit, make_train_and_eval

VARIANT_NAME = "frozen_projector"
PCA_DIM = 64
HEUR_DIM = 4
PANNS_DIM = 2048
HEAD_INPUT_DIM = PCA_DIM + HEUR_DIM  # 68
HIDDEN = 32
WEIGHT_DECAY = 1e-3

DEFAULT_BASIS_DIR = Path("data/ear/head_regularization_audit")
BASIS_PATH = DEFAULT_BASIS_DIR / "pca_basis.npz"
BASIS_SHA_PATH = DEFAULT_BASIS_DIR / "pca_basis.sha256"


# ---------------------------------------------------------------------------
# PCA-64 fit + persist (deterministic; refuses to run on SHA drift)
# ---------------------------------------------------------------------------
def _load_full_panns_matrix() -> tuple[list[str], np.ndarray]:
    from .features import CACHE_DIR
    valset = Path("data/classifier/valset/valset_manifest.tsv")
    with valset.open() as f:
        header = f.readline().rstrip("\n").split("\t")
        rows = [dict(zip(header, ln.rstrip("\n").split("\t"))) for ln in f if ln.strip()]
    clip_ids = sorted(r["clip_id"] for r in rows)
    Xs = []
    for cid in clip_ids:
        p = CACHE_DIR / f"{cid}.npz"
        if not p.exists():
            raise SystemExit(f"[frozen_projector] missing feature cache for {cid} at {p}")
        npz = np.load(p, allow_pickle=False)
        Xs.append(np.asarray(npz["panns_embed"], dtype=np.float64))
    X_panns = np.stack(Xs, axis=0)  # (55, 2048)
    return clip_ids, X_panns


def _fit_pca_64(X_panns: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return (mean, components (2048, 64)).

    Deterministic under single-thread BLAS pins. Uses full_matrices=False
    SVD on the mean-centered feature matrix and takes the top-64 right
    singular vectors.
    """
    mean_v = X_panns.mean(axis=0)
    Xc = X_panns - mean_v
    # With N=55 < D=2048, an economy SVD returns only 55 right-singular
    # vectors. The brief requests PCA-64, so we use full_matrices=True to
    # obtain a complete (2048, 2048) orthonormal basis and take the top 64
    # rows. The last (64 - min(N-1, 64)) rows lie in the null space of the
    # mean-centered feature matrix and contribute ~0 signal but are stable
    # under BLAS pins. This preserves the 64-D contract while acknowledging
    # the 55-clip corpus's rank cap.
    _, _, Vt = np.linalg.svd(Xc, full_matrices=True)
    components = Vt[:PCA_DIM, :].T.copy()  # (2048, 64)
    # Deterministic sign-fix: for each component, flip sign so the largest
    # absolute-value entry is positive. Guards against SVD sign-flip
    # non-portability across BLAS builds (identical under our pins in
    # practice; this belt-and-braces has no numerical downside).
    for k in range(components.shape[1]):
        idx = int(np.argmax(np.abs(components[:, k])))
        if components[idx, k] < 0:
            components[:, k] *= -1.0
    return mean_v.astype(np.float64), components.astype(np.float64)


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_pca_basis(basis_path: Path = BASIS_PATH, sha_path: Path = BASIS_SHA_PATH) -> str:
    """Fit + persist the PCA basis if absent; verify SHA if present.

    Returns the pinned SHA-256 string. Raises SystemExit on drift.
    """
    basis_path.parent.mkdir(parents=True, exist_ok=True)
    if not basis_path.exists():
        _, X_panns = _load_full_panns_matrix()
        mean_v, components = _fit_pca_64(X_panns)
        # Save with sorted key order for stable NPZ layout.
        np.savez(str(basis_path), mean=mean_v, components=components)
        sha = _sha256_of_file(basis_path)
        sha_path.write_text(sha + "\n")
        return sha
    sha_now = _sha256_of_file(basis_path)
    if not sha_path.exists():
        # First-time-after-manual-move: pin it.
        sha_path.write_text(sha_now + "\n")
        return sha_now
    sha_pinned = sha_path.read_text().strip()
    if sha_now != sha_pinned:
        raise SystemExit(
            f"[frozen_projector] REFUSING to run: pca_basis.npz SHA drift "
            f"(now={sha_now}, pinned={sha_pinned}). Restore basis or rebuild."
        )
    return sha_pinned


def _load_basis(basis_path: Path = BASIS_PATH) -> tuple[np.ndarray, np.ndarray]:
    ensure_pca_basis(basis_path)
    npz = np.load(str(basis_path), allow_pickle=False)
    return npz["mean"].astype(np.float32), npz["components"].astype(np.float32)


# Lazy cache of (mean, components).
_BASIS: tuple[np.ndarray, np.ndarray] | None = None


def _preprocess(X: np.ndarray) -> np.ndarray:
    """Split PANNs+HEUR, PCA-64 project PANNs, concat back to 68-D."""
    global _BASIS
    if _BASIS is None:
        _BASIS = _load_basis()
    mean_v, components = _BASIS
    X = X.astype(np.float32)
    assert X.shape[1] == PANNS_DIM + HEUR_DIM, f"expected 2052-D input, got {X.shape[1]}"
    X_panns = X[:, :PANNS_DIM] - mean_v
    X_low = X_panns @ components  # (N, 64)
    X_heur = X[:, PANNS_DIM:]
    return np.concatenate([X_low, X_heur], axis=1).astype(np.float32)


def build_head(feat_dim: int) -> nn.Module:
    # Guard: variant 3's head only accepts the 68-D preprocessed input.
    assert feat_dim == HEAD_INPUT_DIM, f"expected {HEAD_INPUT_DIM}-D, got {feat_dim}"
    return nn.Sequential(
        nn.Linear(feat_dim, HIDDEN),
        nn.ReLU(),
        nn.Linear(HIDDEN, K - 1),
    )


_fit = make_fit(build_head, weight_decay=WEIGHT_DECAY, preprocess=_preprocess)
train_and_eval = make_train_and_eval(_fit)
