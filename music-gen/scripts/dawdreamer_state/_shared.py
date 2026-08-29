#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:20:00Z
# cycle: 33
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround
# ---
"""Shared helpers for cycle-33 DawDreamer state-extraction probes.

Zero PRNG. The cycle-9 effects chain (scripts.tex.render_effects_layered)
is a read-only anchor for this branch and is NEVER imported here.
BLAS pins are set at import time so downstream `import dawdreamer`
(if the caller imports it after this module) sees single-thread BLAS.
"""
from __future__ import annotations

import hashlib
import json
import os
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Tuple

# BLAS + thread pins — set BEFORE any numeric library import.
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

# Interpreter guard — probes must run under /usr/bin/python3.
assert sys.executable == '/usr/bin/python3', (
    f"scripts/dawdreamer_state requires /usr/bin/python3; got {sys.executable}"
)

# Fixed rendering pipeline (rubric §4).
SAMPLE_RATE = 44100
DURATION_S = 8.0
SAMPLE_COUNT = int(SAMPLE_RATE * DURATION_S)  # 352800
CHANNELS = 2
DEFAULT_BLOCK_SIZE = 512
BPM = 120.0
NOTE_LEN_S = 0.5
NOTE_ON_LEN_S = 0.45
VELOCITY = 96
DIATONIC_SEMITONES = (0, 2, 4, 5, 7, 9, 11)  # C D E F G A B
# 16-note ascending diatonic C-major starting at C4 (MIDI 60) — matches c31.
NOTES: list[int] = []
_octave = 0
for _i in range(16):
    _step = _i % 7
    if _i > 0 and _step == 0:
        _octave += 1
    NOTES.append(60 + 12 * _octave + DIATONIC_SEMITONES[_step])

# The plugins under probe.
PLUGINS: Tuple[Tuple[str, str], ...] = (
    ("surge_xt", "/usr/lib/vst3/Surge XT.vst3"),
    ("dexed",    "/usr/lib/vst3/Dexed.vst3"),
)

# Reference SHA-256 of the fixed 8 s test-input MIDI file (rubric §4).
# Computed deterministically from write_test_midi() below; asserted in
# tests/test_dawdreamer_state_extraction.py::test_midi_input_reference_sha.
MIDI_INPUT_SHA256_REFERENCE = (
    # Filled in after first probe run; helper below computes it on demand.
    None
)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_of_path(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json_bytes(obj: Any) -> bytes:
    """Canonical JSON: sorted keys, compact separators. UTF-8 bytes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_json_sha(obj: Any) -> str:
    return sha256_bytes(canonical_json_bytes(obj))


def fresh_temp_dir(prefix: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix))


def _varint(n: int) -> bytes:
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def write_test_midi(out_path: Path, ppq: int = 480) -> Path:
    """Write the fixed 8 s test-input MIDI file deterministically.

    Format-0, single track, 120 bpm, 16 ascending diatonic notes.
    Matches scripts/palette_probe/_shared.write_test_midi byte-for-byte.
    """
    mspq = 500_000
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, ppq)
    events = bytearray()
    events += _varint(0) + bytes([0xFF, 0x51, 0x03]) + mspq.to_bytes(3, "big")
    ticks_per_note_on_off = int(round(ppq * NOTE_ON_LEN_S / NOTE_LEN_S))
    ticks_beat = ppq
    ticks_off = ticks_per_note_on_off
    ticks_gap = ticks_beat - ticks_off
    for i, midi_note in enumerate(NOTES):
        delta = 0 if i == 0 else ticks_gap
        events += _varint(delta) + bytes([0x90, midi_note & 0x7F, VELOCITY])
        events += _varint(ticks_off) + bytes([0x80, midi_note & 0x7F, 0])
    events += _varint(0) + bytes([0xFF, 0x2F, 0x00])
    track = b"MTrk" + struct.pack(">I", len(events)) + bytes(events)
    out_path.write_bytes(header + track)
    return out_path


def make_plugin(plugin_path: str, block_size: int = DEFAULT_BLOCK_SIZE):
    """Create a DawDreamer PluginProcessor with the fixed engine config.

    Import of dawdreamer happens lazily inside the function so bare
    module-import of _shared is cheap and safe for the AST-grep and
    interpreter-guard tests that don't want to spin up an engine.
    """
    import dawdreamer as daw  # noqa: WPS433
    engine = daw.RenderEngine(SAMPLE_RATE, block_size)
    plugin = engine.make_plugin_processor("t", plugin_path)
    return engine, plugin


def data_dir() -> Path:
    """Workspace-relative data root for this branch's artifacts."""
    return Path(__file__).resolve().parents[2] / "data" / "dawdreamer_state"


def per_plugin_dir(plugin_key: str) -> Path:
    p = data_dir() / "per_plugin" / plugin_key
    p.mkdir(parents=True, exist_ok=True)
    return p


def append_fetchability(row: Dict[str, Any]) -> None:
    p = data_dir() / "fetchability_ladder.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def compute_reference_midi_sha() -> str:
    """Deterministic SHA-256 of the fixed test MIDI (§4)."""
    tmp = fresh_temp_dir("dawdstate-midiref-")
    p = write_test_midi(tmp / "input.mid")
    return sha256_of_path(p)
