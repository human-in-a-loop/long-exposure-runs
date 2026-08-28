#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T05:20:00Z
# cycle: 4
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel
# ---
"""Panel assembly. Returns five metrics side by side, NEVER an aggregate.

    result = {
        "mel_l1_db":                 float,
        "spectral_centroid_rmse_hz": float,
        "rms_env_rmse":              float,
        "lufs_m_rmse_lu":            float,
        "embedding_cosine_distance": float | None,
        "embedding_rung":            "clap" | "vggish" | "none_available",
        "sr_hz":                     int,
        "n_samples_compared":        int,
    }

Callers wanting an aggregate score compose it themselves — the panel refuses.
"""
from __future__ import annotations

import sys
from typing import Optional, Sequence, Union

import numpy as np

# Enforce interpreter at import time (as prescribed by the research brief).
if sys.executable != "/usr/bin/python3":  # pragma: no cover
    import warnings
    warnings.warn(
        f"texture panel expected /usr/bin/python3, got {sys.executable}. "
        "librosa/tensorflow/torch are only present on system python here.",
        RuntimeWarning,
    )

from .spectral_panel import spectral_metrics
from .envelope_panel import envelope_metrics
from .embedding_panel import embedding_metrics


PUBLIC_KEYS = (
    "mel_l1_db",
    "spectral_centroid_rmse_hz",
    "rms_env_rmse",
    "lufs_m_rmse_lu",
    "embedding_cosine_distance",
    "embedding_rung",
    "sr_hz",
    "n_samples_compared",
)

_BANNED_KEYS = {"overall", "combined", "mean", "mean_score", "weighted",
                "aggregate", "score", "total"}


def _n_samples(a: np.ndarray) -> int:
    a = np.asarray(a)
    if a.ndim == 1:
        return int(a.shape[0])
    # stereo: return sample count along the longer axis
    return int(max(a.shape))


def texture_distance(a: np.ndarray, b: np.ndarray, sr: int,
                     sr_b: Optional[int] = None) -> dict:
    """Return the five texture-panel metrics side by side.

    Length mismatch: the two inputs are truncated to ``min(len(a), len(b))``
    samples internally by each metric; results are computed on the common
    prefix. This is intentional and documented — the panel does not resample
    or DTW-align. Callers who want tempo alignment must handle it upstream.

    SR mismatch: a hard ``ValueError`` is raised. Callers must resample.

    Does NOT return an aggregate score.
    """
    if sr_b is not None and sr_b != sr:
        raise ValueError(f"sample-rate mismatch: a={sr} b={sr_b}. "
                         "Resample upstream — the panel refuses to guess.")

    n_common = min(_n_samples(a), _n_samples(b))

    result: dict = {}
    result.update({k: v for k, v in spectral_metrics(a, b, sr).items() if not k.startswith("_")})
    result.update(envelope_metrics(a, b, sr))
    result.update(embedding_metrics(a, b, sr))
    result["sr_hz"] = int(sr)
    result["n_samples_compared"] = int(n_common)

    # Refuse-aggregate contract: assert exact key set.
    if set(result.keys()) != set(PUBLIC_KEYS):
        raise RuntimeError(
            "panel contract violation: keys are "
            f"{sorted(result.keys())}, expected {sorted(PUBLIC_KEYS)}."
        )
    for banned in _BANNED_KEYS:
        if banned in result:  # pragma: no cover
            raise RuntimeError(f"panel contract violation: banned key '{banned}' present")

    return result
