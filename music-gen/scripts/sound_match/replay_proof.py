#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 2
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-bass-sf2-replay-proof
# ---
"""Replay-proof driver: profile.json + bass MIDI -> WAV twice into fresh
tempfile.mkdtemp() dirs, assert byte-equal render_sha256.

FD-1: on failure, verdict REPLAY_PROOF_FAILS is emitted and the sf2 family
for this (song, instrument) is INVALIDATED for the campaign. No retry loop.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable

# env pins BEFORE any observed import
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
        f"replay_proof requires /usr/bin/python3 (got {sys.executable})"
    )

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.sound_match.replay import replay  # noqa: E402


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _env_pin_sha() -> str:
    body = json.dumps({k: os.environ.get(k) for k in _PINS},
                      sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def prove_replay(
    profile: dict,
    midi_path: Path,
    out_json: Path | None = None,
    *,
    replay_fn: Callable = replay,
) -> dict:
    """Run replay twice into fresh temp dirs; assert SHA equality; return verdict."""
    t_start = time.time()
    with tempfile.TemporaryDirectory(prefix="v4_replay_r1_") as td1, \
         tempfile.TemporaryDirectory(prefix="v4_replay_r2_") as td2:
        w1 = Path(td1) / "render.wav"
        w2 = Path(td2) / "render.wav"
        sha1 = replay_fn(profile, midi_path, w1)
        sha2 = replay_fn(profile, midi_path, w2)
        verdict = "REPLAY_PROOF_HOLDS" if sha1 == sha2 else "REPLAY_PROOF_FAILS"
        report = {
            "verdict": verdict,
            "run1_sha256": sha1,
            "run2_sha256": sha2,
            "tempdir_run1": td1,
            "tempdir_run2": td2,
            "midi_path": str(midi_path),
            "midi_sha256": sha256_of_file(midi_path),
            "env_pin_sha256": _env_pin_sha(),
            "env_pins": {k: os.environ.get(k) for k in _PINS},
            "profile_id": profile.get("profile_id"),
            "family": profile.get("family"),
            "wall_seconds": time.time() - t_start,
        }
    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        with open(out_json, "w") as f:
            json.dump(report, f, sort_keys=True, indent=2)
    if verdict == "REPLAY_PROOF_FAILS":
        # FD-1: hard fail, no fallback. Caller decides how to escalate.
        raise SystemExit(f"REPLAY_PROOF_FAILS: {sha1} != {sha2}")
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Prove replay determinism ×2.")
    ap.add_argument("--profile", required=True, type=Path)
    ap.add_argument("--midi", required=True, type=Path)
    ap.add_argument("--out-json", required=True, type=Path)
    args = ap.parse_args(argv)
    profile = json.loads(Path(args.profile).read_text())
    prove_replay(profile, args.midi, out_json=args.out_json)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
