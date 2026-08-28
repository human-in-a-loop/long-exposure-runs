"""Cross-recipe stability metrics for M-EAR-1/synthetic-label-stability-audit.

Pure numpy / stdlib; deterministic under BLAS pins. No PRNG.

Public API:
    kendall_tau_exact(a, b) -> (tau_b, n_concordant, n_discordant, n_tied_a, n_tied_b)
    mae_envelope(vals) -> {"mean": ..., "p05": ..., "p50": ..., "p95": ..., "min": ..., "max": ...}
    per_clip_band_variance(rank_matrix) -> {"mean": np.ndarray, "var": np.ndarray}
"""
# created: 2026-08-28T17:33:00Z  cycle: 22  run_id: run-2026-08-28T040704Z
# agent: worker (clone-2, fork cc548ca0c2e5)  milestone: M-EAR-1/synthetic-label-stability-audit
from __future__ import annotations
from . import _interp  # noqa: F401 -- interpreter guard

from typing import Sequence

import numpy as np


# ---------------------------------------------------------------------------
# Exact Kendall τ-b (handles ties on both sides)
# ---------------------------------------------------------------------------
def kendall_tau_exact(
    a: Sequence[float] | np.ndarray, b: Sequence[float] | np.ndarray
) -> dict:
    """Kendall τ-b via O(n^2) pair enumeration.

    Returns a dict with keys:
      tau_b, n_pairs, n_concordant, n_discordant, n_tied_a, n_tied_b, n_tied_both

    τ-b = (nc - nd) / sqrt((n_pairs - n_tied_a) * (n_pairs - n_tied_b))
    Returns tau_b = 0.0 when denominator is zero (both vectors constant).
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("a and b must be 1-D arrays of equal length")
    n = a.shape[0]
    if n < 2:
        return {
            "tau_b": 0.0, "n_pairs": 0, "n_concordant": 0, "n_discordant": 0,
            "n_tied_a": 0, "n_tied_b": 0, "n_tied_both": 0,
        }
    nc = nd = ta = tb = tab = 0
    # O(n^2) is fine for n=55.
    for i in range(n - 1):
        for j in range(i + 1, n):
            da = a[i] - a[j]
            db = b[i] - b[j]
            if da == 0 and db == 0:
                tab += 1
            elif da == 0:
                ta += 1
            elif db == 0:
                tb += 1
            elif (da > 0) == (db > 0):
                nc += 1
            else:
                nd += 1
    n_pairs = n * (n - 1) // 2
    # Ties in a include the both-tied count for the "shared" tie set.
    ta_full = ta + tab
    tb_full = tb + tab
    denom = np.sqrt(max(n_pairs - ta_full, 0) * max(n_pairs - tb_full, 0))
    tau_b = 0.0 if denom == 0 else (nc - nd) / denom
    return {
        "tau_b": float(tau_b),
        "n_pairs": int(n_pairs),
        "n_concordant": int(nc),
        "n_discordant": int(nd),
        "n_tied_a": int(ta),
        "n_tied_b": int(tb),
        "n_tied_both": int(tab),
    }


# ---------------------------------------------------------------------------
# MAE envelope percentiles (numpy default linear interpolation, pinned)
# ---------------------------------------------------------------------------
def mae_envelope(vals: Sequence[float] | np.ndarray) -> dict:
    a = np.asarray(vals, dtype=np.float64)
    if a.size == 0:
        return {k: float("nan") for k in ("mean", "p05", "p50", "p95", "min", "max", "std")}
    return {
        "mean": float(a.mean()),
        "p05": float(np.percentile(a, 5.0, method="linear")),
        "p50": float(np.percentile(a, 50.0, method="linear")),
        "p95": float(np.percentile(a, 95.0, method="linear")),
        "min": float(a.min()),
        "max": float(a.max()),
        "std": float(a.std(ddof=0)),
    }


# ---------------------------------------------------------------------------
# Per-clip band variance across recipes
# ---------------------------------------------------------------------------
def per_clip_band_variance(rank_matrix: np.ndarray) -> dict:
    """rank_matrix shape (n_clips, n_recipes) ints in {1..K}.

    Returns dict with per-clip mean_rank + band_variance (ddof=0).
    """
    if rank_matrix.ndim != 2:
        raise ValueError("rank_matrix must be 2-D (n_clips, n_recipes)")
    m = rank_matrix.astype(np.float64)
    return {
        "mean_rank": m.mean(axis=1),
        "band_variance": m.var(axis=1, ddof=0),
    }
