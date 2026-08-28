#!/usr/bin/env python3
"""Quick inspection of the two renders."""
import soundfile as sf
import numpy as np

for path in (
    "data/daw_spike/ardour_render.wav",
    "data/daw_spike/dawdreamer_render.wav",
):
    audio, sr = sf.read(path)
    if audio.ndim == 1:
        audio = audio[:, None]
    n = audio.shape[0]
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio**2)))
    print(f"{path}: sr={sr} shape={audio.shape} peak={peak:.4f} rms={rms:.4f}")
    half = n // 2
    print(
        f"  first-half rms={float(np.sqrt(np.mean(audio[:half]**2))):.4f} "
        f"second-half rms={float(np.sqrt(np.mean(audio[half:]**2))):.4f}"
    )
