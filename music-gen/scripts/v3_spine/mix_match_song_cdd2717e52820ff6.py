#!/usr/bin/env python3
"""c20 Rome: RMS-match per-stem operator-section renders to baseline; sum (sibling of c5)."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import scipy.io.wavfile as sw

SHA16 = "cdd2717e52820ff6"
SEC = Path(f"data/v3_spine/{SHA16}/operator_section")
RENDER = SEC / "render"
STEM_DIR = SEC / "rc9_6stem"

STEM_MAP = [
    ("drums", RENDER / "per_track" / "drums.wav", STEM_DIR / "drums.wav"),
    ("bass", RENDER / "per_track" / "bass.wav", STEM_DIR / "bass.wav"),
    ("guitar", RENDER / "per_track" / "guitar.wav", STEM_DIR / "guitar.wav"),
    ("piano", RENDER / "per_track" / "piano.wav", STEM_DIR / "piano.wav"),
    ("other", RENDER / "per_track" / "other.wav", STEM_DIR / "other.wav"),
    ("vocals", RENDER / "vocals_htdemucs.wav", STEM_DIR / "vocals.wav"),
]


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


def write_wav_stereo_16(path, sr, y):
    y_c = np.clip(y, -1.0, 1.0)
    y_i16 = (y_c * 32767.0).astype(np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".wav.tmp")
    sw.write(str(tmp), sr, y_i16)
    tmp.replace(path)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def resample_44k(y, src_sr):
    if src_sr == 44100:
        return y
    from scipy.signal import resample_poly
    from math import gcd
    g = gcd(src_sr, 44100)
    return resample_poly(y, 44100 // g, src_sr // g, axis=0).astype(np.float32)


def mix_once(out_name):
    per_info = {}
    sr_target = 44100
    v_sr, v_y = read_wav(STEM_DIR / "vocals.wav")
    v_y = resample_44k(v_y, v_sr)
    total = v_y.shape[0]
    accum = np.zeros((total, 2), dtype=np.float64)
    for name, rendered, baseline in STEM_MAP:
        if not rendered.exists() or not baseline.exists():
            per_info[name] = {"status": "missing"}
            continue
        r_sr, r_y = read_wav(rendered)
        b_sr, b_y = read_wav(baseline)
        b_rms = rms_db(b_y)
        r_rms = rms_db(r_y) if r_y.size > 0 else -100.0
        if r_sr != sr_target:
            r_y = resample_44k(r_y, r_sr)
        if r_rms > -80.0:
            gain_db = b_rms - r_rms
            gain_db = max(min(gain_db, 24.0), -24.0)
            r_y = r_y * (10.0 ** (gain_db / 20.0))
        else:
            gain_db = 0.0
        if r_y.shape[0] < total:
            r_y = np.concatenate([r_y, np.zeros((total - r_y.shape[0], 2), dtype=np.float32)], axis=0)
        elif r_y.shape[0] > total:
            r_y = r_y[:total]
        accum += r_y.astype(np.float64)
        per_info[name] = {
            "baseline_rms_db": round(b_rms, 3),
            "rendered_rms_db": round(r_rms, 3),
            "gain_applied_db": round(gain_db, 3),
        }
    peak = float(np.max(np.abs(accum))) if accum is not None else 0.0
    if peak > 0.707:
        accum *= 0.707 / peak
    out = RENDER / out_name
    write_wav_stereo_16(out, sr_target, accum)
    return out, per_info, peak


def main():
    p1, info1, _ = mix_once("full_reconstruction_operator_section_run1.wav")
    p2, _, _ = mix_once("full_reconstruction_operator_section_run2.wav")
    s1 = sha(p1); s2 = sha(p2)
    p_final, info_f, peak_f = mix_once("full_reconstruction_operator_section.wav")
    s_final = sha(p_final)
    (RENDER / "mix_match_operator_section.json").write_text(json.dumps({
        "cycle": 20,
        "song_sha16": SHA16,
        "chosen_section": {"t_start_s": 21.91963718820862, "t_end_s": 51.91963718820862, "duration_s": 30.0},
        "per_stem_info": info_f,
        "run1_sha256": s1,
        "run2_sha256": s2,
        "final_sha256": s_final,
        "byte_deterministic_x2": s1 == s2 == s_final,
        "peak_before_normalize": peak_f,
        "output_path": str(p_final),
    }, indent=2, sort_keys=True) + "\n")
    for p in (p1, p2):
        if p.exists() and p != p_final:
            p.unlink()
    print(f"mix sha={s_final[:16]} det_x2={s1==s2==s_final}")


if __name__ == "__main__":
    main()
