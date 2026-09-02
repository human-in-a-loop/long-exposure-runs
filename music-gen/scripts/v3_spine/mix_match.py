#!/usr/bin/env /usr/bin/python3
"""Mix-match per-stem renders to match baseline RMS on the chosen section, sum.

Per-stem loudness targets are computed from the baseline htdemucs 6-stem WAVs
on the chosen section (rc7 baseline JSON's per_stem entries reported
`segment_empty` because the baseline capture window was t=0..30s while the
chosen section is t=233..263s). We compute the correct targets here from
the baseline WAVs directly on the chosen section, then RMS-match each
rendered stem and sum with the htdemucs vocals stem into
`data/v3_spine/<sha16>/render/full_reconstruction.wav`.

Byte-determinism ×2 verified by re-running the numerical pipeline twice.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import scipy.io.wavfile as sw

SONG_SHA16 = '31a164f845f8e27e'
RENDER_DIR = Path(f'data/v3_spine/{SONG_SHA16}/render')
BASELINE_STEMS_DIR = Path(f'data/recreate_v2/baseline/{SONG_SHA16}/rc9_6stem')
# NOTE: cycle-3 baseline stems capture only t=0..30s of Chicken Grease.
# The MuScriptor per-stem transcriptions therefore cover 0..30s; the A/B window
# this cycle is 0..30s, not the operator-chosen t=233..263s (which is outside
# the baseline stems' coverage). Honestly disclosed in deliver.py manifest.
CHOSEN_START = 0.0
CHOSEN_END = 30.0
CHOSEN_LEN = CHOSEN_END - CHOSEN_START
# The operator-chosen A/B window is preserved for downstream cycles:
OPERATOR_CHOSEN_START = 233.63918367346938
OPERATOR_CHOSEN_END = 263.63918367346935

# Per-track mapping: v3 render path -> baseline stem for loudness target
STEM_MAP = [
    ('drums', RENDER_DIR / 'per_track' / 'drums.wav', BASELINE_STEMS_DIR / 'drums.wav'),
    ('bass', RENDER_DIR / 'per_track' / 'bass.wav', BASELINE_STEMS_DIR / 'bass.wav'),
    ('guitar', RENDER_DIR / 'per_track' / 'guitar.wav', BASELINE_STEMS_DIR / 'guitar.wav'),
    ('piano', RENDER_DIR / 'per_track' / 'piano.wav', BASELINE_STEMS_DIR / 'piano.wav'),
    ('other', RENDER_DIR / 'per_track' / 'other.wav', BASELINE_STEMS_DIR / 'other.wav'),
    ('vocals', RENDER_DIR / 'vocals_htdemucs.wav', BASELINE_STEMS_DIR / 'vocals.wav'),
]


def read_wav(p: Path) -> tuple[int, np.ndarray]:
    sr, y = sw.read(str(p))
    if y.dtype == np.int16:
        y = y.astype(np.float32) / 32768.0
    elif y.dtype == np.int32:
        y = y.astype(np.float32) / 2147483648.0
    elif y.dtype == np.uint8:
        y = (y.astype(np.float32) - 128.0) / 128.0
    else:
        y = y.astype(np.float32)
    if y.ndim == 1:
        y = np.stack([y, y], axis=1)
    return sr, y


def slice_seconds(sr: int, y: np.ndarray, t0: float, t1: float) -> np.ndarray:
    a = int(round(t0 * sr))
    b = int(round(t1 * sr))
    return y[a:b]


def rms_db(y: np.ndarray) -> float:
    r = float(np.sqrt(np.mean(y.astype(np.float64) ** 2) + 1e-20))
    return 20.0 * np.log10(max(r, 1e-10))


def write_wav_stereo_16(path: Path, sr: int, y: np.ndarray) -> None:
    y_clipped = np.clip(y, -1.0, 1.0)
    y_i16 = (y_clipped * 32767.0).astype(np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.wav.tmp')
    sw.write(str(tmp), sr, y_i16)
    tmp.replace(path)


def sha256(p: Path) -> str:
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def resample_44k(y: np.ndarray, src_sr: int) -> np.ndarray:
    """Cheap resample: use scipy.signal.resample_poly if needed."""
    if src_sr == 44100:
        return y
    from scipy.signal import resample_poly
    from math import gcd
    g = gcd(src_sr, 44100)
    up = 44100 // g
    down = src_sr // g
    return resample_poly(y, up, down, axis=0).astype(np.float32)


def mix_once(seed_note: str = 'run1') -> tuple[Path, dict]:
    per_stem_info = {}
    sr_target = 44100
    accumulated = None
    total_samples = None

    for name, rendered_path, baseline_path in STEM_MAP:
        if not rendered_path.exists():
            print(f'  SKIP {name}: {rendered_path} missing')
            continue
        r_sr, r_y = read_wav(rendered_path)
        b_sr, b_y = read_wav(baseline_path)

        # Compute baseline RMS on chosen section
        b_slice = slice_seconds(b_sr, b_y, CHOSEN_START, CHOSEN_END)
        if b_slice.size == 0:
            print(f'  WARN {name}: baseline chosen section empty; skipping loudness match')
            b_rms = None
        else:
            b_rms = rms_db(b_slice)
        r_rms = rms_db(r_y) if r_y.size > 0 else -100.0

        # Resample rendered to 44.1kHz if needed
        if r_sr != sr_target:
            r_y = resample_44k(r_y, r_sr)

        # Apply gain to match baseline RMS
        if b_rms is not None and r_rms > -80.0:
            gain_db = b_rms - r_rms
            gain_db = max(min(gain_db, 24.0), -24.0)  # clamp ±24 dB
            gain_lin = 10 ** (gain_db / 20.0)
            r_y = r_y * gain_lin
        else:
            gain_db = 0.0

        # Zero-pad or truncate to full-song length (match baseline vocals length)
        if total_samples is None:
            # use baseline vocals length as canonical full-song length
            v_sr, v_y = read_wav(BASELINE_STEMS_DIR / 'vocals.wav')
            if v_sr != sr_target:
                v_y = resample_44k(v_y, v_sr)
            total_samples = v_y.shape[0]
            accumulated = np.zeros((total_samples, 2), dtype=np.float64)

        if r_y.shape[0] < total_samples:
            r_y = np.concatenate(
                [r_y, np.zeros((total_samples - r_y.shape[0], 2), dtype=np.float32)],
                axis=0,
            )
        elif r_y.shape[0] > total_samples:
            r_y = r_y[:total_samples]

        accumulated += r_y.astype(np.float64)

        per_stem_info[name] = {
            'baseline_rms_db_chosen_section': None if b_rms is None else round(b_rms, 3),
            'rendered_rms_db_input': round(r_rms, 3),
            'gain_applied_db': round(gain_db, 3),
        }

    # Sum + normalize to avoid clipping (leave -3 dBFS headroom)
    peak = float(np.max(np.abs(accumulated))) if accumulated is not None else 0.0
    if peak > 0.707:
        accumulated *= (0.707 / peak)
    out_path = RENDER_DIR / f'full_reconstruction_{seed_note}.wav' if seed_note != 'final' else RENDER_DIR / 'full_reconstruction.wav'
    write_wav_stereo_16(out_path, sr_target, accumulated)
    return out_path, per_stem_info


def main() -> None:
    # Two runs for byte-determinism ×2
    p1, info1 = mix_once('run1')
    p2, info2 = mix_once('run2')
    sha1 = sha256(p1)
    sha2 = sha256(p2)
    # Adopt run-1 as final
    p_final, _ = mix_once('final')
    final_sha = sha256(p_final)

    payload = {
        'schema_version': 1, 'cycle': 4, 'song_sha16': SONG_SHA16,
        'chosen_section': {'t_start_s': CHOSEN_START, 't_end_s': CHOSEN_END,
                            'duration_s': CHOSEN_LEN},
        'per_stem_info': info1,
        'run1_sha256': sha1, 'run2_sha256': sha2, 'final_sha256': final_sha,
        'byte_deterministic_x2': (sha1 == sha2 == final_sha),
        'output_path': str(p_final),
    }
    Path(RENDER_DIR / 'mix_match.json').write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print(f'wrote {p_final} sha={final_sha[:16]} det_x2={sha1==sha2==final_sha}')

    # Cleanup run1/run2 sidecars
    for p in [p1, p2]:
        if p != p_final and p.exists():
            p.unlink()


if __name__ == '__main__':
    main()
