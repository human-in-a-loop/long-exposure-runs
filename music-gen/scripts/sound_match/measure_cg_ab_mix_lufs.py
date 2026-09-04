#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T04:30:00Z
# cycle: 18
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-V4-SHOWCASE-1
# purpose: c18 Track 4 (OPTIONAL) — LUFS-I diagnostic sidecar for the
#           c17 CG A/B mix. DIAGNOSTIC ONLY: does not mutate audio bytes,
#           does not apply gain, does not re-render. cg_ab_mix.wav SHA
#           byte-identical pre==post.
# ---
"""LUFS-I diagnostic on cg_ab_mix.wav + per-cell source WAVs.

If pyloudnorm is unavailable in the current interpreter, write a
FETCH_FAIL row per the c11+ fetchability-ladder convention rather than
attempting an install.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import wave
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
for k, v in _PINS.items():
    os.environ.setdefault(k, v)
_ENV_PIN_SHA = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"

ROOT = Path(__file__).resolve().parents[2]
SONG_SHA16 = "31a164f845f8e27e"
DELIVERY = ROOT / "data/v4/deliveries" / SONG_SHA16
MIX = DELIVERY / "cg_ab_mix.wav"
STEMS = ROOT / "data/v3/deliveries" / SONG_SHA16 / "cert_run1" / "stems_6s"


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_pcm(p: Path):
    with wave.open(str(p), "rb") as w:
        nch, sr = w.getnchannels(), w.getframerate()
        sw = w.getsampwidth()
        n = w.getnframes()
        raw = w.readframes(n)
    assert sw == 2, f"expected 16-bit, got sampwidth={sw}"
    import numpy as np
    ints = np.frombuffer(raw, dtype=np.int16)
    if nch == 2:
        data = ints.reshape(-1, 2).astype(np.float32) / 32768.0
    else:
        data = ints.astype(np.float32) / 32768.0
    return data, sr, nch


def main() -> int:
    out_path = DELIVERY / "cg_ab_mix.lufs_diagnostic.json"
    mix_sha_pre = sha256_of(MIX)

    result: dict = {
        "kind": "cg_ab_v4_lufs_diagnostic",
        "cycle": 18,
        "run_id": "run-2026-08-28T040704Z",
        "created": "2026-09-04T04:30:00Z",
        "song_sha16": SONG_SHA16,
        "env_pin_sha256": _ENV_PIN_SHA,
        "diagnostic_only": True,
        "does_not_mutate_audio": True,
        "cg_ab_mix_wav_sha256_pre": mix_sha_pre,
    }

    try:
        import pyloudnorm as pyln  # noqa: F401
        import numpy as np  # noqa: F401
    except Exception as exc:  # pragma: no cover
        result["fetch_status"] = "FETCH_FAIL"
        result["fetch_status_reason"] = f"import failed: {type(exc).__name__}: {exc}"
        result["measurements"] = None
        result["cg_ab_mix_wav_sha256_post"] = sha256_of(MIX)
        out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        print(f"FETCH_FAIL -> {out_path}")
        return 0

    import pyloudnorm as pyln

    measurements: dict = {}

    def measure(label: str, path: Path):
        data, sr, nch = load_pcm(path)
        meter = pyln.Meter(sr)
        try:
            lufs_i = float(meter.integrated_loudness(data))
        except Exception as exc:
            lufs_i = None
            reason = f"{type(exc).__name__}: {exc}"
        else:
            reason = None
        measurements[label] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256_of(path),
            "sr_hz": sr,
            "n_channels": nch,
            "n_frames": data.shape[0],
            "duration_s": round(data.shape[0] / sr, 6),
            "lufs_i": lufs_i,
            "lufs_i_error": reason,
        }

    measure("cg_ab_mix", MIX)
    for stem in ("bass", "drums", "guitar", "vocals"):
        p = STEMS / f"{stem}.wav"
        if p.exists():
            measure(f"stem_{stem}", p)

    # Also NULL cells for symmetry: piano/other are silent per-track so
    # measurement of the *reference* htdemucs stems is informative for the
    # audibility-grounding record.
    for stem in ("piano", "other"):
        p = STEMS / f"{stem}.wav"
        if p.exists():
            measure(f"stem_{stem}_reference_only_null_in_mix", p)

    result["fetch_status"] = "OK"
    result["fetch_status_reason"] = None
    result["measurements"] = measurements
    result["cg_ab_mix_wav_sha256_post"] = sha256_of(MIX)
    assert result["cg_ab_mix_wav_sha256_pre"] == result["cg_ab_mix_wav_sha256_post"], (
        "audio bytes must not mutate during LUFS diagnostic"
    )

    out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(f"WROTE {out_path}")
    for k, v in measurements.items():
        print(f"  {k:60s}  LUFS-I={v['lufs_i']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
