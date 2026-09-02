#!/usr/bin/env python3
"""c20 Rome: per-stem RMS + LUFS-S proxy on operator-section stems (sibling of c5)."""
from __future__ import annotations
import json
import math
from pathlib import Path
import numpy as np
import scipy.io.wavfile as sw

SHA16 = "cdd2717e52820ff6"
SEC = Path(f"data/v3_spine/{SHA16}/operator_section")
STEM_DIR = SEC / "rc9_6stem"
OUT = SEC / "rc7_per_stem_loudness_operator_section.json"


def read_wav(p):
    sr, y = sw.read(str(p))
    if y.dtype == np.int16:
        y = y.astype(np.float32) / 32768.0
    elif y.dtype == np.int32:
        y = y.astype(np.float32) / 2147483648.0
    else:
        y = y.astype(np.float32)
    if y.ndim == 1:
        y = np.stack([y, y], axis=1)
    return sr, y


def rms_db(y):
    r = float(np.sqrt(np.mean(y.astype(np.float64) ** 2) + 1e-20))
    return 20.0 * math.log10(max(r, 1e-10))


def lufs_s_approx(y, sr):
    mono = y.mean(axis=1)
    win = int(3.0 * sr)
    hop = int(1.0 * sr)
    if mono.shape[0] < win:
        return rms_db(y)
    windows = []
    for i in range(0, mono.shape[0] - win + 1, hop):
        seg = mono[i:i + win]
        pw = np.mean(seg.astype(np.float64) ** 2)
        if pw > 1e-12:
            windows.append(10.0 * math.log10(pw))
    if not windows:
        return rms_db(y)
    return float(np.mean(windows) - 0.691)


def main():
    result = {"cycle": 20, "song_sha16": SHA16, "section": "operator_section", "per_stem": {}}
    for stem in ["bass", "drums", "guitar", "other", "piano", "vocals"]:
        p = STEM_DIR / f"{stem}.wav"
        if not p.exists():
            result["per_stem"][stem] = {"status": "missing"}
            continue
        sr, y = read_wav(p)
        result["per_stem"][stem] = {
            "path": str(p),
            "sample_rate": sr,
            "n_samples": int(y.shape[0]),
            "rms_db": round(rms_db(y), 4),
            "lufs_s_proxy_db": round(lufs_s_approx(y, sr), 4),
        }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
