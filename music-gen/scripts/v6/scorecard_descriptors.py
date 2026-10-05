#!/usr/bin/python3
"""v6 Phase 1B — mix-level audio descriptors for the scorecard (split out of scorecard.py in iteration 05 so that module
stays under the 450-line budget direction; the public names are re-exported by scorecard.py unchanged).

created: 2026-10-05 (moved verbatim from scripts/v6/scorecard.py, created 2026-10-04)
milestone: M-V6-SCORECARD-1B

Per file: integrated LUFS (pyloudnorm), crest factor, spectral centroid mean, stereo width (side/mid energy, dB), L/R
correlation, peak/RMS dBFS. Cached by sha16 under data/v6/descriptors/ (schema-checked), summarised mean/sd/min/max.
"""
from __future__ import annotations

import math
import time
from pathlib import Path

import numpy as np

from scripts.v6.v6_common import read_json, write_json_atomic

DESCRIPTORS_SCHEMA_VERSION = "v6.descriptors.1"
DESCRIPTOR_KEYS = ("lufs_integrated", "crest_factor_db", "spectral_centroid_hz", "stereo_width_db",
                   "lr_correlation", "peak_dbfs", "rms_dbfs")


def audio_descriptors(path: Path) -> dict:
    """Integrated LUFS (pyloudnorm), crest factor, spectral centroid mean, stereo width, peak/RMS."""
    import soundfile as sf
    x, sr = sf.read(str(path), dtype="float32", always_2d=True)
    n, ch = x.shape
    dur = n / sr
    mono = x.mean(axis=1)
    peak = float(np.abs(x).max()) if n else 0.0
    rms = float(np.sqrt(np.mean(np.square(x, dtype=np.float64)))) if n else 0.0
    rec = {"schema_version": DESCRIPTORS_SCHEMA_VERSION, "duration_s": round(dur, 3), "sr": int(sr), "channels": int(ch),
           "peak_dbfs": 20 * math.log10(max(peak, 1e-12)), "rms_dbfs": 20 * math.log10(max(rms, 1e-12)),
           "crest_factor_db": 20 * math.log10(max(peak, 1e-12) / max(rms, 1e-12))}
    try:
        import pyloudnorm as pyln
        rec["lufs_integrated"] = float(pyln.Meter(sr).integrated_loudness(x if ch > 1 else mono)) if dur >= 0.5 else None
    except Exception as exc:  # pragma: no cover
        rec["lufs_integrated"], rec["lufs_error"] = None, f"{type(exc).__name__}: {exc}"
    if rec.get("lufs_integrated") is not None and not math.isfinite(rec["lufs_integrated"]):
        rec["lufs_integrated"] = None  # digital silence -> -inf
    import librosa
    c = librosa.feature.spectral_centroid(y=mono, sr=sr, n_fft=2048, hop_length=512)[0] if n >= 2048 else np.zeros(0)
    rec["spectral_centroid_hz"] = float(c.mean()) if c.size else None
    if ch >= 2:
        L, R = x[:, 0].astype(np.float64), x[:, 1].astype(np.float64)
        mid, side = 0.5 * (L + R), 0.5 * (L - R)
        e_mid, e_side = float(np.dot(mid, mid)), float(np.dot(side, side))
        rec["stereo_width_db"] = 10 * math.log10(max(e_side, 1e-20) / max(e_mid, 1e-20)) if e_mid > 0 else None
        den = math.sqrt(float(np.dot(L, L)) * float(np.dot(R, R)))
        rec["lr_correlation"] = float(np.dot(L, R) / den) if den > 0 else None
    else:
        rec["stereo_width_db"], rec["lr_correlation"] = None, None  # mono: width undefined
    return rec


def descriptors_for(items: list, cache_dir: Path, log) -> list[dict]:
    out = []
    for it in items:
        cpath = cache_dir / f"{it['sha16']}.json"
        rec = None
        if cpath.exists():
            try:
                rec = read_json(cpath)
                if rec.get("schema_version") != DESCRIPTORS_SCHEMA_VERSION:
                    rec = None
            except Exception:
                rec = None
        if rec is None:
            t0 = time.time()
            rec = audio_descriptors(Path(it["path"]))
            rec.update({"sha16": it["sha16"], "path": it["path"], "wall_s": round(time.time() - t0, 2)})
            write_json_atomic(cpath, rec)
            log(f"[desc] {it['sha16']} {it['label']} lufs={rec.get('lufs_integrated')} wall={rec['wall_s']}s")
        out.append(dict(rec, label=it["label"]))
    return out


def summarise_descriptors(recs: list[dict]) -> dict:
    out = {"n": len(recs)}
    for k in DESCRIPTOR_KEYS:
        v = np.asarray([r[k] for r in recs if r.get(k) is not None and math.isfinite(r[k])], dtype=np.float64)
        out[k] = ({"n": int(len(v)), "mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                   "min": float(v.min()), "max": float(v.max())} if len(v) else {"n": 0})
    return out
