#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 1
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES
# ---
"""Objective panel wrapper (READ-ONLY over scripts.texture.panel).

Weights are literal in this module and frozen at milestone start
(M-V4-PROFILES) per docs/specs/v4_sound_matching_layer_spec.md §Objective:

    mel_l1        = 0.5
    centroid_rmse = 0.25
    embedding_cos = 0.25

`composite` = 0.5 * mel_l1_db + 0.25 * spectral_centroid_rmse_hz
              + 0.25 * (embedding_cos_dist * 100.0)

The embedding factor is scaled ×100 so its 0..2 range contributes
meaningfully next to the raw dB and Hz metrics; the composite is only
used to RANK candidates in a single (song, instrument) sweep so absolute
scale is not portable across instruments — only ordering within one
sweep is meaningful.

If the embedding rung is `none_available` the composite falls back to
the two-metric form documented in the module and the returned
`embedding_component` field is None. See spec §Objective.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# Interpreter guard.
if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(
        f"sound_match.objective requires /usr/bin/python3 (got {sys.executable})"
    )

import numpy as np
import soundfile as sf

# READ-ONLY import from the texture panel; do not vendor or copy.
from scripts.texture.panel import texture_distance

# Frozen weights (literals, not env vars).
W_MEL = 0.5
W_CENTROID = 0.25
W_EMBED = 0.25
EMBED_SCALE = 100.0

FALLBACK_W_MEL = 0.67
FALLBACK_W_CENTROID = 0.33


def _load(path: Path) -> tuple[np.ndarray, int]:
    """Load a WAV as float32; mixdown to mono for panel-safe compare."""
    y, sr = sf.read(str(path), always_2d=False)
    if y.ndim > 1:
        y = y.mean(axis=1)
    return y.astype(np.float32), int(sr)


def score_pair(candidate_wav: Path, reference_wav: Path) -> dict:
    """Return the panel keys + composite for a (candidate, reference) pair.

    Keys:
        mel_l1_db
        spectral_centroid_rmse_hz
        embedding_cos_vggish   # None if VGGish is unavailable
        embedding_cos_clap_or_none
        embedding_component    # None if embedding rung is 'none_available'
        composite
        weights                # dict of frozen weight literals used
        embedding_rung
        sr_hz
        n_samples_compared
    """
    a, sr_a = _load(Path(candidate_wav))
    b, sr_b = _load(Path(reference_wav))
    if sr_a != sr_b:
        raise ValueError(
            f"sample-rate mismatch: candidate={sr_a} reference={sr_b}"
        )
    panel = texture_distance(a, b, sr_a)

    embed_rung = panel["embedding_rung"]
    embed_cos = panel["embedding_cosine_distance"]

    embedding_cos_vggish: Optional[float]
    embedding_cos_clap: Optional[float]
    if embed_rung == "vggish":
        embedding_cos_vggish = float(embed_cos)
        embedding_cos_clap = None
    elif embed_rung == "clap":
        embedding_cos_vggish = None
        embedding_cos_clap = float(embed_cos)
    else:
        embedding_cos_vggish = None
        embedding_cos_clap = None

    if embed_cos is None:
        # Honest degradation: no embedding available. Fall back to the
        # documented two-metric composite; leave embedding_component None.
        composite = (
            FALLBACK_W_MEL * float(panel["mel_l1_db"])
            + FALLBACK_W_CENTROID * float(panel["spectral_centroid_rmse_hz"])
        )
        embedding_component: Optional[float] = None
        weights = {
            "mel_l1": FALLBACK_W_MEL,
            "centroid_rmse": FALLBACK_W_CENTROID,
            "embedding_cos": None,
            "fallback": True,
        }
    else:
        embedding_component = float(embed_cos) * EMBED_SCALE
        composite = (
            W_MEL * float(panel["mel_l1_db"])
            + W_CENTROID * float(panel["spectral_centroid_rmse_hz"])
            + W_EMBED * embedding_component
        )
        weights = {
            "mel_l1": W_MEL,
            "centroid_rmse": W_CENTROID,
            "embedding_cos": W_EMBED,
            "fallback": False,
        }

    return {
        "mel_l1_db": float(panel["mel_l1_db"]),
        "spectral_centroid_rmse_hz": float(panel["spectral_centroid_rmse_hz"]),
        "embedding_cos_vggish": embedding_cos_vggish,
        "embedding_cos_clap_or_none": embedding_cos_clap,
        "embedding_component": embedding_component,
        "composite": float(composite),
        "weights": weights,
        "embedding_rung": embed_rung,
        "sr_hz": int(panel["sr_hz"]),
        "n_samples_compared": int(panel["n_samples_compared"]),
    }
