#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T02:10:00Z
# cycle: 31
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/palette-instrument-determinism
# ---
"""Shared helpers for cycle-31 palette-instrument determinism probes.

Zero PRNG. The cycle-9 effects chain is a read-only anchor for this
branch and is never imported here. Every helper is pure,
byte-deterministic, and safe to import from any per-instrument probe.

BLAS pins are set at import time so downstream `import dawdreamer`
(if performed by the caller after this module loads) sees single-thread
BLAS. Callers should still `import _shared` BEFORE `import dawdreamer`.
"""
from __future__ import annotations

import hashlib
import json
import os
import struct
import sys
from pathlib import Path
from typing import Any, Dict

# BLAS + thread pins — set BEFORE any numeric library import.
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

# Interpreter guard — probes must run under /usr/bin/python3.
assert sys.executable == "/usr/bin/python3", (
    f"palette_probe requires /usr/bin/python3; got {sys.executable}"
)

SAMPLE_RATE = 44100
DURATION_S = 8.0
SAMPLE_COUNT = int(SAMPLE_RATE * DURATION_S)  # 352800
CHANNELS = 2
DEFAULT_BLOCK_SIZE = 512
BPM = 120.0
NOTE_LEN_S = 0.5           # one note per beat @ 120 bpm
NOTE_ON_LEN_S = 0.45       # short gap prevents legato tie
VELOCITY = 96
# 16-note ascending diatonic C-major starting at C4 (MIDI 60).
DIATONIC_SEMITONES = [0, 2, 4, 5, 7, 9, 11]  # C D E F G A B
NOTES: list[int] = []
_octave = 0
for _i in range(16):
    _step = _i % 7
    if _i > 0 and _step == 0:
        _octave += 1
    NOTES.append(60 + 12 * _octave + DIATONIC_SEMITONES[_step])


def sha256_of_path(p: Path) -> str:
    """SHA-256 hex digest of a file's bytes."""
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(obj: Any) -> str:
    """Canonical JSON with sorted keys and 2-space indent.

    All pinned-state JSON files use this exact format so byte-identity
    across two probe runs is testable.
    """
    return json.dumps(obj, sort_keys=True, indent=2, separators=(",", ": "))


def write_pinned_state(out_dir: Path, state: Dict[str, Any]) -> Path:
    """Write pinned_state.json under out_dir. Returns the path."""
    p = out_dir / "pinned_state.json"
    p.write_text(canonical_json(state) + "\n")
    return p


def _varint(n: int) -> bytes:
    """MIDI variable-length quantity."""
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def write_test_midi(out_path: Path, ppq: int = 480) -> Path:
    """Write the fixed 8s test-input MIDI file deterministically.

    Format-0, single track, 120 bpm, 16 ascending diatonic notes as
    documented in the rubric §4. No PRNG, no timestamps, no metadata
    that would drift between runs. Returns out_path.
    """
    # microseconds per quarter for 120 bpm
    mspq = 500_000
    # header chunk
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, ppq)
    events = bytearray()
    # tempo meta at t=0
    events += _varint(0) + bytes([0xFF, 0x51, 0x03]) + mspq.to_bytes(3, "big")
    ticks_per_note_on_off = int(round(ppq * NOTE_ON_LEN_S / NOTE_LEN_S))
    # delta ticks between consecutive events, per note:
    #   on at t=i*NOTE_LEN_S ; off at t=i*NOTE_LEN_S+NOTE_ON_LEN_S
    # We express deltas between events; start at t=0 for first note-on.
    ticks_beat = ppq  # 1 beat per note-slot
    ticks_off = ticks_per_note_on_off
    ticks_gap = ticks_beat - ticks_off  # after off, wait to next on
    last_time = 0
    for i, midi_note in enumerate(NOTES):
        # note-on (channel 0)
        delta = 0 if i == 0 else ticks_gap
        events += _varint(delta) + bytes([0x90, midi_note & 0x7F, VELOCITY])
        # note-off (channel 0), velocity 0
        events += _varint(ticks_off) + bytes([0x80, midi_note & 0x7F, 0])
    # end of track
    events += _varint(0) + bytes([0xFF, 0x2F, 0x00])
    track = b"MTrk" + struct.pack(">I", len(events)) + bytes(events)
    out_path.write_bytes(header + track)
    return out_path


def pinned_state_schema_keys() -> list[str]:
    """Canonical list of required keys in every pinned_state.json."""
    return [
        "block_size",
        "external_state_sha256",
        "loader_pathway",
        "midi_input_sha256",
        "parameter_dict",
        "plugin_binary_sha256",
        "plugin_name",
        "plugin_version",
        "preset_name",
        "sample_count",
        "sample_rate",
        "stereo",
    ]


def validate_pinned_state(state: Dict[str, Any]) -> None:
    """Raise ValueError if state doesn't match the rubric §3 schema."""
    required = pinned_state_schema_keys()
    missing = [k for k in required if k not in state]
    if missing:
        raise ValueError(f"pinned_state missing keys: {missing}")
    types = {
        "block_size": int,
        "sample_count": int,
        "sample_rate": int,
        "stereo": bool,
        "midi_input_sha256": str,
        "plugin_binary_sha256": str,
        "plugin_name": str,
        "parameter_dict": dict,
        "loader_pathway": str,
    }
    for k, T in types.items():
        if not isinstance(state[k], T):
            raise ValueError(
                f"pinned_state[{k!r}] must be {T.__name__}, got "
                f"{type(state[k]).__name__}"
            )
    # nullable
    for k in ("plugin_version", "preset_name", "external_state_sha256"):
        v = state[k]
        if v is not None and not isinstance(v, str):
            raise ValueError(f"pinned_state[{k!r}] must be str|null")
    if state["sample_rate"] != SAMPLE_RATE:
        raise ValueError("sample_rate must equal 44100")
    if state["sample_count"] != SAMPLE_COUNT:
        raise ValueError(f"sample_count must equal {SAMPLE_COUNT}")
    if state["stereo"] is not True:
        raise ValueError("stereo must be true")


def load_pinned_state(p: Path) -> Dict[str, Any]:
    """Load and validate a pinned_state.json from disk."""
    state = json.loads(p.read_text())
    validate_pinned_state(state)
    return state


def note_events_seconds() -> list[tuple[int, float, float]]:
    """Return [(midi_note, on_time_s, off_time_s), ...] for the 16 notes."""
    out = []
    for i, midi_note in enumerate(NOTES):
        on = i * NOTE_LEN_S
        off = on + NOTE_ON_LEN_S
        out.append((midi_note, on, off))
    return out
