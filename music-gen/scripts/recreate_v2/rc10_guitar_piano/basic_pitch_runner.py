#!/usr/bin/python3
# c53 clone-1 RC10 Branch B — basic-pitch runner (defaults + tuned).
# Dispatches to the quarantined venv workspace/basic_pitch_venv via subprocess.
# NO PRNG. /usr/bin/python3 guard.
"""Run basic-pitch on a WAV under specified param preset and cache the output.

Cache key: sha256(wav_bytes) + json.dumps(params, sort_keys). Cached artifact:
  data/rc10_impl/guitar_piano/cache/bp_<preset>_<sha16>.midi  + .notes.json

Preset choices:
  * "default": vanilla predict() call.
  * "tuned_guitar": onset_threshold=0.3, frame_threshold=0.2,
      minimum_note_length=100, min_freq=80, max_freq=1300.
  * "tuned_piano":  onset_threshold=0.3, frame_threshold=0.2,
      minimum_note_length=80, min_freq=27.5, max_freq=4186.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"basic_pitch_runner requires /usr/bin/python3 (got {sys.executable})")

ROOT = Path("/home/user/long-exposure-runs/music-gen")
VENV_PY = ROOT / "workspace/basic_pitch_venv/bin/python3"
CACHE_DIR = ROOT / "data/rc10_impl/guitar_piano/cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

PRESETS = {
    "default": {},
    "tuned_guitar": {
        "onset_threshold": 0.3,
        "frame_threshold": 0.2,
        "minimum_note_length": 100,
        "minimum_frequency": 80.0,
        "maximum_frequency": 1300.0,
    },
    "tuned_piano": {
        "onset_threshold": 0.3,
        "frame_threshold": 0.2,
        "minimum_note_length": 80,
        "minimum_frequency": 27.5,
        "maximum_frequency": 4186.0,
    },
}


def _sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def cache_path(preset: str, wav_path: Path) -> tuple[Path, Path]:
    s = _sha16(wav_path)
    return (
        CACHE_DIR / f"bp_{preset}_{s}.midi",
        CACHE_DIR / f"bp_{preset}_{s}.notes.json",
    )


def run(preset: str, wav_path: Path) -> tuple[Path, Path]:
    """Run basic-pitch for (preset, wav). Returns (midi_path, notes_json_path).

    Skips subprocess if both cache artifacts already exist.
    """
    if preset not in PRESETS:
        raise ValueError(f"unknown preset {preset!r}")
    midi_p, notes_p = cache_path(preset, wav_path)
    if midi_p.exists() and notes_p.exists() and midi_p.stat().st_size > 0:
        return midi_p, notes_p
    params = PRESETS[preset]
    params_json = json.dumps(params, sort_keys=True)
    inner = ROOT / "scripts/recreate_v2/rc10_guitar_piano/_bp_inner.py"
    if not inner.exists():
        raise RuntimeError(f"missing inner runner: {inner}")
    proc = subprocess.run(
        [str(VENV_PY), str(inner), str(wav_path), str(midi_p), str(notes_p), params_json],
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "TF_CPP_MIN_LOG_LEVEL": "3",
            "TF_ENABLE_ONEDNN_OPTS": "0",
        },
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"basic-pitch failed (preset={preset}, wav={wav_path.name}): "
            f"rc={proc.returncode}\nstdout: {proc.stdout[-500:]}\nstderr: {proc.stderr[-500:]}"
        )
    return midi_p, notes_p


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: basic_pitch_runner.py <preset> <wav>")
    m, j = run(sys.argv[1], Path(sys.argv[2]))
    print(f"OK: {m} + {j}")
