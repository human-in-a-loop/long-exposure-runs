"""Deterministic CC-0 synthetic seed audio.

Three seeds exercise the three length regimes for the chunker:
- seed_short_22s.wav (< 30 s)     -> short-song single-clip branch.
- seed_mid_50s.wav   (30-60 s)    -> 2 hop clips + tail-anchored final.
- seed_long_87s.wav  (> 75 s)     -> 3 hop clips + tail-anchored 4th clip.

All content is synthesized in NumPy with a fixed RNG seed; sha256 of the
output WAV files is recorded in `docs/ingestion_chassis_report.md`.
"""
from __future__ import annotations

import numpy as np
from pathlib import Path

from scripts.ingest.wavio import write_pcm16_mono

SR = 22050
SEED_DIR = Path("data/ingestion/seed")


def _sine(freq: float, n: int, sr: int) -> np.ndarray:
    t = np.arange(n, dtype=np.float64) / sr
    return np.sin(2.0 * np.pi * freq * t).astype(np.float32)


def make_short_22s() -> np.ndarray:
    """22.0 s: decaying C-E-G triad with per-note attack-decay envelope."""
    n = int(round(22.0 * SR))
    t = np.arange(n, dtype=np.float64) / SR
    env = np.exp(-0.25 * t).astype(np.float32)          # slow decay
    chord = (_sine(261.63, n, SR)
             + _sine(329.63, n, SR)
             + _sine(392.00, n, SR)) / 3.0
    return 0.6 * env * chord


def make_mid_50s() -> np.ndarray:
    """50.0 s: 12 steps x 5 s + 2 s tail. Step boundaries at 5 s multiples
    sit inside the 5 s overlap zone, so tests can assert boundary
    presence in >=2 clips."""
    n = int(round(50.0 * SR))
    out = np.zeros(n, dtype=np.float32)
    freqs = [220.0, 246.94, 261.63, 293.66, 329.63, 349.23,
             392.00, 440.00, 493.88, 523.25, 587.33, 659.25]
    step_len = int(round(5.0 * SR))
    for i, f in enumerate(freqs):
        s = i * step_len
        e = min(s + step_len, n)
        out[s:e] = _sine(f, e - s, SR)
    # 2 s tail continues the last frequency at half amplitude
    tail_s = 12 * step_len
    if tail_s < n:
        out[tail_s:] = 0.5 * _sine(freqs[-1], n - tail_s, SR)
    return 0.5 * out


def make_long_87s() -> np.ndarray:
    """87.0 s: sine sweep 220 -> 880 Hz, amplitude-modulated by seeded
    brown noise (fixed rng)."""
    n = int(round(87.0 * SR))
    t = np.arange(n, dtype=np.float64) / SR
    dur = 87.0
    # Linear frequency sweep -> integrate phase.
    f0, f1 = 220.0, 880.0
    phase = 2.0 * np.pi * (f0 * t + 0.5 * (f1 - f0) / dur * t * t)
    tone = np.sin(phase).astype(np.float32)
    rng = np.random.default_rng(20260828)
    white = rng.standard_normal(n).astype(np.float32)
    brown = np.cumsum(white)
    brown -= brown.mean()
    brown /= (np.max(np.abs(brown)) + 1e-9)
    mod = 0.5 + 0.5 * brown       # in [0, 1] roughly
    return (0.55 * mod * tone).astype(np.float32)


SEEDS = {
    "seed_short_22s.wav": make_short_22s,
    "seed_mid_50s.wav": make_mid_50s,
    "seed_long_87s.wav": make_long_87s,
}


def generate_all(out_dir: Path = SEED_DIR) -> dict[str, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for name, fn in SEEDS.items():
        p = out_dir / name
        write_pcm16_mono(p, fn(), SR)
        written[name] = p
    return written


if __name__ == "__main__":
    import hashlib
    for name, p in generate_all().items():
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        print(f"{name}\t{p.stat().st_size} bytes\tsha256={h}")
