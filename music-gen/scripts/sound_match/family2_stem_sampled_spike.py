#!/usr/bin/env /usr/bin/python3
"""c5 family-2 stem-sampled spike — smallest end-to-end proof.

Reads the READ-ONLY CG bass reference stem, pitch-shifts it to a fixed 3-note demo
(C3, E3, G3 quarter-notes at 120 bpm), sums the shifted copies at onset times, LUFS-I
normalizes to -18 dB (with RMS-dBFS fallback), writes a single WAV under
data/v4/profiles/31a164f845f8e27e/bass_family2_spike/spike.wav, and prints the panel
numbers (mel_l1_db, spectral_centroid_rmse_hz, embedding_cos_vggish) against the
reference stem to stdout.

Scope (strict): NO sweep, NO profile.json, NO leaderboard, NO replay_proof. Total
added audio ≤ 5 MB.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

# Env pin: 7 keys, verbatim per c5 brief (c3 payload + pyloudnorm PRESENT + LUFS-I=-18)
_ENV_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for k, v in _ENV_PINS.items():
    os.environ.setdefault(k, v)

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
import librosa  # noqa: E402

WORKSPACE = Path(__file__).resolve().parents[2]
REF_STEM = WORKSPACE / "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav"
OUT_DIR = WORKSPACE / "data/v4/profiles/31a164f845f8e27e/bass_family2_spike"
OUT_WAV = OUT_DIR / "spike.wav"

# Fixed 3-note demo (C3=48, E3=52, G3=55 at 120bpm, quarter = 0.5s)
DEMO_NOTES = [
    {"pitch": 48, "onset_s": 0.0},  # C3
    {"pitch": 52, "onset_s": 0.5},  # E3
    {"pitch": 55, "onset_s": 1.0},  # G3
]
NOTE_LEN_S = 0.5
LUFS_TARGET_DB = -18.0


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _estimate_f0(y: np.ndarray, sr: int) -> float:
    """Return dominant fundamental (Hz) via pyin, fallback to yin."""
    try:
        f0, voiced, _ = librosa.pyin(
            y, fmin=librosa.note_to_hz("A0"), fmax=librosa.note_to_hz("C6")
        )
        f0_voiced = f0[np.isfinite(f0) & (voiced > 0.5)]
        if f0_voiced.size >= 5:
            return float(np.median(f0_voiced))
    except Exception:
        pass
    # yin fallback
    f0 = librosa.yin(y, fmin=50.0, fmax=1000.0)
    f0 = f0[np.isfinite(f0)]
    return float(np.median(f0)) if f0.size else 110.0


def _adsr_lite(n: int, sr: int) -> np.ndarray:
    """Linear attack / release, ~5 ms each; sustains flat in the middle."""
    env = np.ones(n, dtype=np.float32)
    edge = max(1, int(0.005 * sr))
    if 2 * edge < n:
        env[:edge] = np.linspace(0.0, 1.0, edge, dtype=np.float32)
        env[-edge:] = np.linspace(1.0, 0.0, edge, dtype=np.float32)
    return env


def _lufs_normalize(y: np.ndarray, sr: int, target_db: float) -> tuple[np.ndarray, str, float]:
    """Return (y_norm, method, measured_db). Method ∈ {'pyloudnorm', 'rms_fallback'}."""
    try:
        import pyloudnorm as pyln

        meter = pyln.Meter(sr)
        measured = float(meter.integrated_loudness(y))
        if not np.isfinite(measured):
            raise ValueError("non-finite LUFS")
        gain_db = target_db - measured
        y_out = (y * (10.0 ** (gain_db / 20.0))).astype(np.float32)
        return y_out, "pyloudnorm", measured
    except Exception:
        rms = float(np.sqrt(np.mean(y.astype(np.float64) ** 2)) + 1e-12)
        rms_db = 20.0 * np.log10(rms)
        gain_db = target_db - rms_db
        y_out = (y * (10.0 ** (gain_db / 20.0))).astype(np.float32)
        return y_out, "rms_fallback", rms_db


def _build_spike(stem: np.ndarray, sr: int, stem_f0: float) -> np.ndarray:
    """Pitch-shift + sum the demo notes at their onset times."""
    # Total output length: last onset + note_len + small tail
    total_s = max(n["onset_s"] for n in DEMO_NOTES) + NOTE_LEN_S + 0.1
    n_out = int(total_s * sr)
    out = np.zeros(n_out, dtype=np.float32)

    slice_n = int(NOTE_LEN_S * sr)
    stem_slice = stem[:slice_n] if stem.size >= slice_n else np.pad(stem, (0, slice_n - stem.size))
    env = _adsr_lite(slice_n, sr)

    for note in DEMO_NOTES:
        target_hz = float(librosa.midi_to_hz(note["pitch"]))
        n_steps = 12.0 * np.log2(target_hz / stem_f0)
        shifted = librosa.effects.pitch_shift(stem_slice, sr=sr, n_steps=n_steps)
        if shifted.size < slice_n:
            shifted = np.pad(shifted, (0, slice_n - shifted.size))
        else:
            shifted = shifted[:slice_n]
        windowed = (shifted * env).astype(np.float32)
        idx0 = int(note["onset_s"] * sr)
        idx1 = idx0 + slice_n
        if idx1 > n_out:
            windowed = windowed[: n_out - idx0]
            idx1 = n_out
        out[idx0:idx1] += windowed

    # Prevent clipping headroom before normalize
    peak = float(np.max(np.abs(out))) + 1e-12
    if peak > 1.0:
        out = (out / peak).astype(np.float32)
    return out


def _compute_panel(ref_path: Path, cand_path: Path) -> dict:
    # Import here so env pins are set before any heavy backend init
    from scripts.sound_match.objective import score_pair

    # score_pair(candidate, reference) — c5 spike compares spike-vs-reference.
    return score_pair(Path(cand_path), Path(ref_path))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ref_sha = _sha256(REF_STEM)
    stem, sr = librosa.load(str(REF_STEM), sr=None, mono=True)
    stem_f0 = _estimate_f0(stem, sr)
    if not np.isfinite(stem_f0) or stem_f0 <= 0:
        stem_f0 = 110.0  # A2 default guard

    y = _build_spike(stem, sr, stem_f0)
    y, lufs_method, measured_db = _lufs_normalize(y, sr, LUFS_TARGET_DB)

    sf.write(str(OUT_WAV), y, sr, subtype="PCM_16")
    spike_sha = _sha256(OUT_WAV)
    spike_bytes = OUT_WAV.stat().st_size

    panel = _compute_panel(REF_STEM, OUT_WAV)

    summary = {
        "spike_path": str(OUT_WAV.relative_to(WORKSPACE)),
        "spike_sha256": spike_sha,
        "spike_bytes": spike_bytes,
        "reference_stem_sha256": ref_sha,
        "sample_rate": int(sr),
        "stem_f0_hz": float(stem_f0),
        "lufs_target_db": LUFS_TARGET_DB,
        "lufs_method": lufs_method,
        "lufs_measured_db_pre_normalize": float(measured_db),
        "panel": {
            "mel_l1_db": panel.get("mel_l1_db"),
            "spectral_centroid_rmse_hz": panel.get("spectral_centroid_rmse_hz"),
            "embedding_cos_vggish": panel.get("embedding_cos_vggish"),
        },
        "env_pins": _ENV_PINS,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))

    # Sidecar summary JSON so the auditor/report can pin the panel numbers.
    (OUT_DIR / "spike_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
