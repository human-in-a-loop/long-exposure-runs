#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T14:15:00Z
# cycle: 14
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel/embedding/content-flip-analysis
# ---
"""Per-variant M-TEX-1/panel measurement wrapper.

Loads bare_midi.wav + effects_layered.wav, calls texture_distance on the
(bare_midi, effects_layered) pair, and returns the 8-key panel dict.
Enforces the same non-silent + self-distance + key contract checks as
scripts/tex/measure_across_stages.py so panel regressions surface here.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("TF_DETERMINISTIC_OPS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

assert sys.executable == "/usr/bin/python3", sys.executable

import numpy as np
import soundfile as sf

_WS = Path(__file__).resolve().parents[3]
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))

from scripts.texture.panel import texture_distance, PUBLIC_KEYS

SELF_TOL_NUMERIC = 1e-6
SELF_TOL_EMBEDDING = 1e-4


def _load(path: Path, sr_expected: int = 44100) -> np.ndarray:
    x, sr = sf.read(str(path), always_2d=True)
    if sr != sr_expected:
        raise RuntimeError(f"{path}: expected sr={sr_expected}, got {sr}")
    if x.shape[1] == 1:
        x = np.concatenate([x, x], axis=1)
    return x.astype(np.float32)


def _check_non_silent(x: np.ndarray, tag: str) -> None:
    peak = float(np.abs(x).max())
    if peak <= 1e-4:
        raise RuntimeError(f"{tag}: silent (peak={peak:.3e})")


def _check_self(x: np.ndarray, sr: int, tag: str) -> None:
    d = texture_distance(x, x, sr)
    for k in ("mel_l1_db", "spectral_centroid_rmse_hz",
              "rms_env_rmse", "lufs_m_rmse_lu"):
        v = float(d[k])
        if not np.isfinite(v) or v > SELF_TOL_NUMERIC:
            raise RuntimeError(f"self-distance {k}={v} > tol on {tag}")
    cos = d.get("embedding_cosine_distance")
    if cos is not None and (not np.isfinite(cos) or cos > SELF_TOL_EMBEDDING):
        raise RuntimeError(f"self-embedding {cos} > tol on {tag}")


def measure(bare_wav: Path, eff_wav: Path,
            sr: int = 44100) -> Dict[str, object]:
    a = _load(bare_wav, sr)
    b = _load(eff_wav, sr)
    _check_non_silent(a, str(bare_wav))
    _check_non_silent(b, str(eff_wav))
    _check_self(a, sr, str(bare_wav))
    _check_self(b, sr, str(eff_wav))
    n = min(a.shape[0], b.shape[0])
    d = texture_distance(a[:n], b[:n], sr)
    if set(d.keys()) != set(PUBLIC_KEYS):
        raise RuntimeError(
            f"panel key contract violation: {sorted(d.keys())}"
        )
    for k in ("mel_l1_db", "spectral_centroid_rmse_hz",
              "rms_env_rmse", "lufs_m_rmse_lu",
              "embedding_cosine_distance"):
        v = d.get(k)
        if v is None:
            continue
        if not np.isfinite(float(v)):
            raise RuntimeError(f"non-finite {k}={v} in panel result")
    return d
