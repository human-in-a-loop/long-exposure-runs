#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T00:35:00Z
# cycle: 14
# run_id: run-2026-09-04T003000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-piano-null-finding-grounded-c14
# ---
"""Measure per-stem audibility of a WAV under 7-key env pins.

Emits a JSON sidecar with:
  - rms_dbfs (mono mixdown; 20*log10 of RMS on [-1,1])
  - peak_dbfs
  - lufs_i (via pyloudnorm.Meter.integrated_loudness) OR None with fallback_reason
  - method: "lufs_i" or "rms_fallback"
  - silence_floor_db (frozen: -60 dB RMS)
  - verdict_audible: True iff rms_dbfs > silence_floor_db

Discipline:
  - env pins BEFORE any observed import
  - /usr/bin/python3 interpreter guard
  - no PRNG, no wall clock affecting output
  - no sidecar_nonfactor imports
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(
        f"measure_stem_audibility requires /usr/bin/python3 (got {sys.executable})"
    )

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402

_LOUDNORM_AVAILABLE = False
_LOUDNORM_ERR: str | None = None
try:
    import pyloudnorm as _pyln  # noqa: E402
    _LOUDNORM_AVAILABLE = True
except Exception as _exc:  # pragma: no cover
    _LOUDNORM_ERR = f"{type(_exc).__name__}:{_exc}"


SILENCE_FLOOR_DB = -60.0


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _env_pin_sha256() -> str:
    payload = {"env": {k: os.environ.get(k) for k in _PINS}}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def measure(wav_path: Path) -> dict:
    y, sr = sf.read(str(wav_path), always_2d=False)
    if y.ndim > 1:
        y_mono = y.mean(axis=1).astype(np.float64)
    else:
        y_mono = y.astype(np.float64)
    rms = float(np.sqrt(np.mean(y_mono ** 2) + 1e-24))
    peak = float(np.max(np.abs(y_mono))) if len(y_mono) else 0.0
    rms_dbfs = 20.0 * float(np.log10(max(rms, 1e-12)))
    peak_dbfs = 20.0 * float(np.log10(max(peak, 1e-12)))
    lufs_i = None
    method = "rms_fallback"
    fallback_reason = None
    if _LOUDNORM_AVAILABLE:
        try:
            meter = _pyln.Meter(sr)
            lufs = float(meter.integrated_loudness(y_mono))
            if np.isfinite(lufs):
                lufs_i = lufs
                method = "lufs_i"
            else:
                fallback_reason = f"lufs_non_finite={lufs}"
        except Exception as exc:
            fallback_reason = f"{type(exc).__name__}:{str(exc)[:80]}"
    else:
        fallback_reason = _LOUDNORM_ERR or "pyloudnorm_unavailable"
    verdict_audible = bool(rms_dbfs > SILENCE_FLOOR_DB)
    return {
        "wav_path": str(wav_path),
        "wav_sha256": _sha256(wav_path),
        "sample_rate": int(sr),
        "n_samples": int(len(y_mono)),
        "duration_s": float(len(y_mono) / sr) if sr else 0.0,
        "rms_dbfs": rms_dbfs,
        "peak_dbfs": peak_dbfs,
        "lufs_i": lufs_i,
        "method": method,
        "fallback_reason": fallback_reason,
        "silence_floor_db": SILENCE_FLOOR_DB,
        "verdict_audible": verdict_audible,
        "env_pin_sha256": _env_pin_sha256(),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Per-stem audibility measurement.")
    ap.add_argument("--wav", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    for k, v in _PINS.items():
        if os.environ.get(k) != v:
            raise RuntimeError(f"env pin drift {k}={os.environ.get(k)!r} expected {v!r}")
    result = measure(args.wav)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(f"AUDIBLE={result['verdict_audible']} rms_dbfs={result['rms_dbfs']:.2f} "
          f"method={result['method']} out={args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
