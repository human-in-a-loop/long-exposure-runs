#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T05:20:00Z
# cycle: 4
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel/embedding
# ---
"""Perceptual embedding cosine distance.

Ladder: CLAP -> VGGish -> None (visible gap, never fabricated).

This clone lands on VGGish. CLAP install downgraded numpy from 2.4.6 to
1.26.4 (documented under _manager/M-CLASS-1-numpy-downgrade) and CLAP
itself pulls torchvision (not installed) plus a ~1.5 GB weight file;
VGGish via tensorflow_hub (loaded once, cached) was the cheaper survivor.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import warnings
from typing import Optional

import numpy as np
import librosa

from .spectral_panel import _to_mono

# --- cache for the loaded model + a rung log ----------------------------------
_MODEL = None
_RUNG: Optional[str] = None
_META: dict = {}

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNG_LOG = ROOT / "data" / "texture" / "embedding_rung.log"

CLAP_SR = 48000
VGGISH_SR = 16000

# CLAP HF-hub weight sha for reproducibility documentation (not fetched here).
CLAP_INTENDED_WEIGHT = "htsat_audioset_epoch_15.pt (LAION-CLAP)"


def _try_clap():
    """Attempt rung 1. Returns (model, meta) or (None, reason)."""
    try:
        import laion_clap  # noqa: F401
    except Exception as e:  # pragma: no cover
        return None, f"laion_clap import failed: {e!r}"
    try:  # torchvision is a hard dep of the laion_clap module tree
        from laion_clap import CLAP_Module
    except Exception as e:
        return None, f"laion_clap.CLAP_Module import failed: {e!r}"
    try:
        m = CLAP_Module(enable_fusion=False)
        m.load_ckpt()  # tries HF-hub fetch
        return m, {"kind": "clap", "sr": CLAP_SR, "note": CLAP_INTENDED_WEIGHT}
    except Exception as e:
        return None, f"CLAP weight fetch/load failed: {e!r}"


def _try_vggish():
    """Attempt rung 2."""
    try:
        os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
        import tensorflow_hub as hub
    except Exception as e:
        return None, f"tensorflow_hub import failed: {e!r}"
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m = hub.load("https://tfhub.dev/google/vggish/1")
        return m, {"kind": "vggish", "sr": VGGISH_SR,
                   "source": "https://tfhub.dev/google/vggish/1",
                   "dim": 128, "frame_s": 0.96}
    except Exception as e:
        return None, f"tfhub VGGish load failed: {e!r}"


def _load_once():
    global _MODEL, _RUNG, _META
    if _RUNG is not None:
        return
    reasons = {}
    m, meta = _try_clap()
    if m is not None:
        _MODEL, _META, _RUNG = m, meta, "clap"
    else:
        reasons["clap"] = meta
        m, meta = _try_vggish()
        if m is not None:
            _MODEL, _META, _RUNG = m, meta, "vggish"
        else:
            reasons["vggish"] = meta
            _MODEL, _META, _RUNG = None, {"reasons": reasons}, "none_available"

    # persist the rung log
    RUNG_LOG.parent.mkdir(parents=True, exist_ok=True)
    RUNG_LOG.write_text(json.dumps({
        "rung": _RUNG,
        "meta": _META,
        "reasons": reasons,
    }, indent=2, default=str))


def _embed_clap(a_mono: np.ndarray, sr: int) -> np.ndarray:
    import torch
    x = librosa.resample(a_mono.astype(np.float32), orig_sr=sr, target_sr=CLAP_SR) if sr != CLAP_SR else a_mono
    with torch.no_grad():
        emb = _MODEL.get_audio_embedding_from_data(x=x[None, :], use_tensor=False)
    return np.asarray(emb).squeeze()


def _embed_vggish(a_mono: np.ndarray, sr: int) -> np.ndarray:
    x = librosa.resample(a_mono.astype(np.float32), orig_sr=sr, target_sr=VGGISH_SR) if sr != VGGISH_SR else a_mono
    frames = _MODEL(x).numpy()   # (n_frames, 128)
    if frames.ndim == 1:
        return frames
    return frames.mean(axis=0)


def _cosine_distance(u: np.ndarray, v: np.ndarray) -> float:
    u = u.reshape(-1); v = v.reshape(-1)
    nu = np.linalg.norm(u) + 1e-12
    nv = np.linalg.norm(v) + 1e-12
    cos_sim = float(np.dot(u, v) / (nu * nv))
    # numerical clamp
    cos_sim = max(-1.0, min(1.0, cos_sim))
    return 1.0 - cos_sim  # cosine distance in [0, 2]


def embedding_cosine_distance(a: np.ndarray, b: np.ndarray, sr: int) -> tuple[Optional[float], str]:
    _load_once()
    if _RUNG == "none_available":
        return None, "none_available"
    a_m = _to_mono(a)
    b_m = _to_mono(b)
    n = min(len(a_m), len(b_m))
    a_m, b_m = a_m[:n], b_m[:n]
    if _RUNG == "clap":
        ea = _embed_clap(a_m, sr); eb = _embed_clap(b_m, sr)
    elif _RUNG == "vggish":
        ea = _embed_vggish(a_m, sr); eb = _embed_vggish(b_m, sr)
    else:
        return None, "none_available"
    return _cosine_distance(ea, eb), _RUNG


def embedding_metrics(a: np.ndarray, b: np.ndarray, sr: int) -> dict:
    dist, rung = embedding_cosine_distance(a, b, sr)
    return {
        "embedding_cosine_distance": dist,
        "embedding_rung": rung,
    }


def get_rung() -> str:
    _load_once()
    return _RUNG  # type: ignore[return-value]
