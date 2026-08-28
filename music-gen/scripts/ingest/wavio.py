"""Minimal 16-bit PCM mono WAV I/O built on the stdlib `wave` module.

We deliberately avoid `soundfile` (not installed in this workspace) and
scipy. Everything downstream in the ingestion chassis assumes 16-bit PCM
mono WAV, which stdlib handles fully.
"""
from __future__ import annotations

import wave
import numpy as np
from pathlib import Path
from typing import Tuple


INT16_MAX = 32767


def write_pcm16_mono(path: Path, samples_f32: np.ndarray, sr_hz: int) -> None:
    """Write a mono 16-bit PCM WAV.

    `samples_f32` is float in [-1, 1] (values outside are hard-clipped).
    Writes are byte-deterministic given the same input array + sr_hz.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    x = np.asarray(samples_f32, dtype=np.float32)
    if x.ndim != 1:
        raise ValueError(f"expected mono 1-D array, got shape {x.shape}")
    x = np.clip(x, -1.0, 1.0)
    pcm = np.round(x * INT16_MAX).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(sr_hz))
        w.writeframes(pcm.tobytes())


def read_pcm16_mono(path: Path) -> Tuple[np.ndarray, int]:
    """Read a WAV, downmix to mono int16 -> float32 in [-1, 1]."""
    path = Path(path)
    with wave.open(str(path), "rb") as w:
        n_ch = w.getnchannels()
        sr = w.getframerate()
        sw = w.getsampwidth()
        n = w.getnframes()
        raw = w.readframes(n)
    if sw != 2:
        raise ValueError(f"{path}: only 16-bit PCM supported (got {sw*8}-bit)")
    pcm = np.frombuffer(raw, dtype="<i2")
    if n_ch > 1:
        pcm = pcm.reshape(-1, n_ch).mean(axis=1)
    samples = pcm.astype(np.float32) / INT16_MAX
    return samples, int(sr)


def encode_pcm16_bytes(samples_f32: np.ndarray) -> bytes:
    """Return the raw 16-bit PCM byte payload (no WAV header).

    Used by the chunker to compute a stable content hash independent of
    header timestamps or metadata.
    """
    x = np.clip(np.asarray(samples_f32, dtype=np.float32), -1.0, 1.0)
    return np.round(x * INT16_MAX).astype("<i2").tobytes()
