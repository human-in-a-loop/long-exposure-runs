#!/usr/bin/python3
"""c86 F2 — sibling canonical JSON->MIDI serializer with an OPTIONAL per-start `velocity` field.

created: 2026-09-09T23:05:00Z
cycle: 86
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F2-bass-melody-dynamics

The READ-ONLY c4 serializer (scripts/v3_spine/midi_from_json_events.py, spec docs/v3_spine_canonical_midi_serializer_spec.md)
hard-codes note_on velocity 100 / note_off velocity 64 and keys starts by `index`. It is NOT modified. This sibling reproduces
its output BYTE-FOR-BYTE when no start event carries `velocity` (tests/test_c86_landing.py asserts this on the iteration-2
event JSON), and otherwise emits `note_on` with `int(start['velocity'])` clipped to [1, 127]. Helpers that do not touch
velocity (`_check_mido_version`, `_channel_for_instrument`, `_seconds_to_ticks`, PPQ) are imported from the c4 module so
the two serializers cannot drift on channel mapping or tick rounding.

Public API: serialize(json_events_path, out_midi_path, tempo_bpm, time_signature, default_velocity=100) -> None
No PRNG, no wall-clock, no dict-order dependence.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Tuple

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
import mido  # noqa: E402
from scripts.v3_spine.midi_from_json_events import (  # noqa: E402  READ-ONLY c4 helpers
    PPQ, CanonicalSerializerError, _channel_for_instrument, _check_mido_version, _seconds_to_ticks)

NOTE_OFF_VELOCITY = 64


def _pair_events_with_velocity(events: list, default_velocity: int) -> list:
    """Same pairing as the c4 `_pair_events` (index-keyed starts, first end per start, 100 ms synthetic duration for
    dangling starts, 10 ms widening for end <= start) plus the per-start velocity (default when absent)."""
    starts_by_index = {}
    for ev in events:
        if ev.get("type") == "start":
            idx = ev.get("index")
            if idx is None:
                raise CanonicalSerializerError(f"start event missing index: {ev}")
            starts_by_index[idx] = ev
    ends_by_start_index = {}
    for ev in events:
        if ev.get("type") == "end":
            se = ev.get("start_event_index")
            if se is None:
                raise CanonicalSerializerError(f"end event missing start_event_index: {ev}")
            ends_by_start_index.setdefault(se, ev)
    paired = []
    for idx in sorted(starts_by_index.keys()):
        s = starts_by_index[idx]
        pitch = int(s["pitch"])
        channel = _channel_for_instrument(s.get("instrument", "") or "")
        start_t = float(s["start_time"])
        e = ends_by_start_index.get(idx)
        if e is None:
            end_t = start_t + 0.100
        else:
            end_t = float(e["end_time"])
            if end_t <= start_t:
                end_t = start_t + 0.010
        vel = s.get("velocity", default_velocity)
        vel = int(max(1, min(127, int(round(float(vel))))))
        paired.append((start_t, end_t, pitch, channel, vel))
    return paired


def serialize(json_events_path: str, out_midi_path: str, tempo_bpm: float, time_signature: Tuple[int, int],
              default_velocity: int = 100) -> None:
    _check_mido_version()
    ts_num, ts_den = time_signature
    if ts_num <= 0 or ts_den <= 0:
        raise CanonicalSerializerError(f"invalid time_signature: ({ts_num}, {ts_den})")
    if tempo_bpm <= 0:
        raise CanonicalSerializerError(f"invalid tempo_bpm: {tempo_bpm}")
    raw = Path(json_events_path).read_bytes()
    try:
        events = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise CanonicalSerializerError(f"invalid JSON in {json_events_path}: {exc}") from exc
    if not isinstance(events, list):
        raise CanonicalSerializerError(f"expected JSON array of events, got {type(events).__name__}")
    rows = []
    for start_t, end_t, pitch, ch, vel in _pair_events_with_velocity(events, default_velocity):
        s_tick = _seconds_to_ticks(start_t, tempo_bpm)
        e_tick = _seconds_to_ticks(end_t, tempo_bpm)
        if e_tick <= s_tick:
            e_tick = s_tick + 1
        rows.append((s_tick, ch, pitch, 0, vel))
        rows.append((e_tick, ch, pitch, 1, NOTE_OFF_VELOCITY))
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]))  # velocity deliberately NOT in the key (c4 order preserved)
    mf = mido.MidiFile(type=1, ticks_per_beat=PPQ)
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(float(tempo_bpm)), time=0))
    meta.append(mido.MetaMessage("time_signature", numerator=int(ts_num), denominator=int(ts_den),
                                 clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    meta.append(mido.MetaMessage("end_of_track", time=0))
    mf.tracks.append(meta)
    track = mido.MidiTrack()
    prev = 0
    for tick, ch, pitch, kind, vel in rows:
        delta = tick - prev
        track.append(mido.Message("note_on" if kind == 0 else "note_off", channel=ch, note=pitch, velocity=vel, time=delta))
        prev = tick
    track.append(mido.MetaMessage("end_of_track", time=0))
    mf.tracks.append(track)
    out_dir = os.path.dirname(os.path.abspath(out_midi_path)) or "."
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=out_dir, suffix=".mid.tmp") as tmp:
        tmp_path = tmp.name
    mf.save(tmp_path)
    os.replace(tmp_path, out_midi_path)
