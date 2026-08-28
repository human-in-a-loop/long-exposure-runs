"""Feature-subset adapter for M-EAR-1/feature-representation-audit (cycle 25).

Pure slicing of the frozen 2052-D ear feature vectors into per-representation
subsets. Deterministic, content-hashed, no PRNG.

The frozen ear feature cache stores per-clip npz files with:
    panns_embed      shape (2048,)
    heuristic_vec    shape (4,)
    vggish_embed     shape (128,) or (0,)  (empty when has_vggish is False)
    has_vggish       bool

The cycle-22 harness `load_features()` builds each per-clip vector via
    np.concatenate([npz['panns_embed'], npz['heuristic_vec']])  → 2052-D
in the fixed order `[PANNs_2048 ‖ HEUR_4]`. The three representations here
slice exactly on that layout:

    R1 HEUR-only     → x[2048:2052]                  →   4-D
    R2 PANNs-only    → x[0:2048]                     → 2048-D
    R3 VGGish-only   → separate VGGish read          →  128-D
                       (raises VggishNotCached when not present)

Non-factor isolation: NO import of scripts.classifier.sidecar_nonfactor.
Interpreter guard: /usr/bin/python3 via `._interp`.
"""
# created: 2026-08-28T21:00:00Z  cycle: 25  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork dc8cba4b79eb)  milestone: M-EAR-1/feature-representation-audit
from __future__ import annotations
from . import _interp  # noqa: F401 -- interpreter guard

import hashlib
import os
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

import numpy as np


# ---------------------------------------------------------------------------
# Layout constants — must match scripts/ear/features.py
# ---------------------------------------------------------------------------
PANNS_DIM = 2048
HEUR_DIM = 4
VGGISH_DIM = 128
FULL_DIM = PANNS_DIM + HEUR_DIM  # 2052


# ---------------------------------------------------------------------------
# Slicing functions — all deterministic, no PRNG
# ---------------------------------------------------------------------------
def slice_heur_only(x: np.ndarray) -> np.ndarray:
    """Return the 4-D M-HEUR-1 mess-scale slice of a 2052-D vector.

    Layout: `[PANNs_2048 ‖ HEUR_4]` → indices [2048:2052].
    """
    if x.shape[-1] != FULL_DIM:
        raise ValueError(
            f"slice_heur_only expects (..., {FULL_DIM}) input; got shape {x.shape}"
        )
    return np.ascontiguousarray(x[..., PANNS_DIM : PANNS_DIM + HEUR_DIM]).astype(np.float32)


def slice_panns_only(x: np.ndarray) -> np.ndarray:
    """Return the 2048-D PANNs Cnn14 penultimate slice of a 2052-D vector.

    Layout: `[PANNs_2048 ‖ HEUR_4]` → indices [0:2048].
    """
    if x.shape[-1] != FULL_DIM:
        raise ValueError(
            f"slice_panns_only expects (..., {FULL_DIM}) input; got shape {x.shape}"
        )
    return np.ascontiguousarray(x[..., 0:PANNS_DIM]).astype(np.float32)


class VggishNotCached(Exception):
    """Raised when a per-clip npz does not contain a VGGish embedding.

    The audit driver treats this as a clean deferral signal rather than an
    error — the R3 representation is published as `deferred_r3_vggish_not_cached`.
    """


def load_vggish_only(cache_dir: Path, clip_ids: list[str]) -> np.ndarray:
    """Load per-clip 128-D VGGish embeddings from the frozen cache.

    Returns:
        X of shape (len(clip_ids), 128).

    Raises:
        VggishNotCached if ANY clip's npz has `has_vggish=False` or an empty
        `vggish_embed` array. This is the brief-mandated all-or-nothing gate.
    """
    xs: list[np.ndarray] = []
    for cid in clip_ids:
        p = cache_dir / f"{cid}.npz"
        if not p.exists():
            raise VggishNotCached(f"missing per-clip feature file: {p}")
        npz = np.load(p, allow_pickle=False)
        has = bool(npz["has_vggish"]) if "has_vggish" in npz.files else False
        vgg = npz["vggish_embed"] if "vggish_embed" in npz.files else np.zeros(0)
        if not has or vgg.size != VGGISH_DIM:
            raise VggishNotCached(
                f"clip {cid} has no cached VGGish embedding "
                f"(has_vggish={has}, vggish size={vgg.size})"
            )
        xs.append(np.asarray(vgg, dtype=np.float32))
    return np.stack(xs, axis=0)


# ---------------------------------------------------------------------------
# Content hash of THIS file (feature_subset_version) — deterministic
# ---------------------------------------------------------------------------
def feature_subset_version() -> str:
    """SHA-256 of THIS file, used as the versioning anchor for slicing."""
    p = Path(__file__).resolve()
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Representation registry — insertion order fixed for determinism
# ---------------------------------------------------------------------------
REPRESENTATIONS: list[dict] = [
    {"name": "heur_only", "dim": HEUR_DIM, "slicer": "slice_heur_only",
     "hypothesis": "very-low-D but semantically-meaningful; if it PASSES C2', the M-HEUR-1 battery carries ordinal signal drowned out by the 2048-D PANNs mix"},
    {"name": "panns_only", "dim": PANNS_DIM, "slicer": "slice_panns_only",
     "hypothesis": "near-cycle-6-baseline dim minus the 4 HEUR dims; if it FAILS identically to the 2052-D concat, the extra 4 HEUR dims were not the problem"},
    {"name": "vggish_only", "dim": VGGISH_DIM, "slicer": "load_vggish_only",
     "hypothesis": "mid-D perceptual embedding between HEUR-only (4-D) and PANNs-only (2048-D) in capacity"},
]


if __name__ == "__main__":
    print(f"feature_subset_version = {feature_subset_version()}")
    print(f"REPRESENTATIONS = {[(r['name'], r['dim']) for r in REPRESENTATIONS]}")
