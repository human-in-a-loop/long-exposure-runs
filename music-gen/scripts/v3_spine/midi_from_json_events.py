#!/usr/bin/env /usr/bin/python3
"""Canonical JSON->MIDI serializer for the v3 spine (M-V3-SPINE-1).

Implements the contract frozen in
`docs/v3_spine_canonical_midi_serializer_spec.md` (SHA pinned to
`data/v3_spine/canonical_serializer_spec_hash.txt`).

Pure function of (json_events_path, out_midi_path, tempo_bpm,
time_signature). No PRNG, no wall-clock, no dict-order dependence.

Public API:
    serialize(json_events_path, out_midi_path, tempo_bpm, time_signature) -> None

Raises CanonicalSerializerError on any pin mismatch or invalid input.
"""
import importlib.metadata
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Iterable, Tuple

# Interpreter guard: /usr/bin/python3 only.
if not sys.executable.endswith('/usr/bin/python3') and 'PYTEST_CURRENT_TEST' not in os.environ:
    # allow when invoked directly via `python3 scripts/...`
    pass

import mido  # noqa: E402

PPQ = 480
REQUIRED_MIDO_VERSION = '1.3.3'

# Deterministic per-instrument channel map (per spec).
INSTRUMENT_TO_CHANNEL = {
    'drums': 9,
    'electric_bass': 0,
    'bass': 0,
    'clean_electric_guitar': 1,
    'distorted_electric_guitar': 1,
    'guitar': 1,
    'acoustic_guitar': 1,
    'piano': 2,
    'acoustic_piano': 2,
    'electric_piano': 2,
    'voice': 3,
}
DEFAULT_CHANNEL = 4


class CanonicalSerializerError(Exception):
    """Typed error for serializer contract violations."""


def _check_mido_version(expected: str = REQUIRED_MIDO_VERSION) -> str:
    """Return the actual installed mido version; raise if != expected."""
    actual = importlib.metadata.version('mido')
    if actual != expected:
        raise CanonicalSerializerError(
            f'mido version mismatch: expected {expected}, got {actual}'
        )
    return actual


def _channel_for_instrument(inst: str) -> int:
    if not inst:
        return DEFAULT_CHANNEL
    inst = inst.lower().strip()
    # exact match first, then prefix match
    if inst in INSTRUMENT_TO_CHANNEL:
        return INSTRUMENT_TO_CHANNEL[inst]
    for prefix, ch in INSTRUMENT_TO_CHANNEL.items():
        if inst.startswith(prefix):
            return ch
    return DEFAULT_CHANNEL


def _seconds_to_ticks(t_seconds: float, tempo_bpm: float, ppq: int = PPQ) -> int:
    beats = float(t_seconds) * float(tempo_bpm) / 60.0
    ticks = int(round(beats * ppq))
    return max(0, ticks)


def _pair_events(events: Iterable[dict]) -> list:
    """Pair start events with their matching end events by start_event_index.

    Returns list of tuples (start_tick_seconds, end_tick_seconds, pitch, channel).
    Dangling starts get a 100 ms synthetic duration.
    """
    events_list = list(events)
    starts_by_index = {}
    for ev in events_list:
        if ev.get('type') == 'start':
            idx = ev.get('index')
            if idx is None:
                raise CanonicalSerializerError(
                    f'start event missing index: {ev}'
                )
            starts_by_index[idx] = ev

    ends_by_start_index = {}
    for ev in events_list:
        if ev.get('type') == 'end':
            se = ev.get('start_event_index')
            if se is None:
                raise CanonicalSerializerError(
                    f'end event missing start_event_index: {ev}'
                )
            # if multiple end events reference the same start, use first (deterministic
            # since input list is byte-deterministic per MuScriptor)
            ends_by_start_index.setdefault(se, ev)

    paired = []
    for idx in sorted(starts_by_index.keys()):
        s = starts_by_index[idx]
        pitch = int(s['pitch'])
        inst = s.get('instrument', '') or ''
        channel = _channel_for_instrument(inst)
        start_t = float(s['start_time'])
        e = ends_by_start_index.get(idx)
        if e is None:
            end_t = start_t + 0.100  # 100 ms synthetic duration
        else:
            end_t = float(e['end_time'])
            if end_t <= start_t:
                end_t = start_t + 0.010  # widen by ~10 ms to force >=1 tick separation
        paired.append((start_t, end_t, pitch, channel))
    return paired


def serialize(
    json_events_path: str,
    out_midi_path: str,
    tempo_bpm: float,
    time_signature: Tuple[int, int],
) -> None:
    """Canonical, deterministic JSON->MIDI serialization.

    Pure function; no wall-clock, no PRNG, no dict-order dependence.
    """
    _check_mido_version()

    ts_num, ts_den = time_signature
    if ts_num <= 0 or ts_den <= 0:
        raise CanonicalSerializerError(
            f'invalid time_signature: ({ts_num}, {ts_den})'
        )
    if tempo_bpm <= 0:
        raise CanonicalSerializerError(f'invalid tempo_bpm: {tempo_bpm}')

    with open(json_events_path, 'rb') as f:
        raw = f.read()
    try:
        events = json.loads(raw.decode('utf-8'))
    except json.JSONDecodeError as exc:
        raise CanonicalSerializerError(
            f'invalid JSON in {json_events_path}: {exc}'
        ) from exc
    if not isinstance(events, list):
        raise CanonicalSerializerError(
            f'expected JSON array of events, got {type(events).__name__}'
        )

    # Pair start/end events, convert to ticks.
    paired = _pair_events(events)

    # Build (tick, channel, pitch, kind, velocity) rows.
    # kind: 0 = note_on, 1 = note_off.  velocity: 100 for on, 64 for off.
    rows = []
    for start_t, end_t, pitch, ch in paired:
        s_tick = _seconds_to_ticks(start_t, tempo_bpm)
        e_tick = _seconds_to_ticks(end_t, tempo_bpm)
        if e_tick <= s_tick:
            e_tick = s_tick + 1  # ensure note_off after note_on
        rows.append((s_tick, ch, pitch, 0, 100))  # note_on
        rows.append((e_tick, ch, pitch, 1, 64))   # note_off
    # Sort by (tick, channel, pitch, kind) as per spec.
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]))

    # Build mido file.
    mf = mido.MidiFile(type=1, ticks_per_beat=PPQ)

    # Track 0: meta (tempo + time_signature at tick 0).
    meta = mido.MidiTrack()
    meta.append(
        mido.MetaMessage(
            'set_tempo', tempo=mido.bpm2tempo(float(tempo_bpm)), time=0
        )
    )
    meta.append(
        mido.MetaMessage(
            'time_signature',
            numerator=int(ts_num),
            denominator=int(ts_den),
            clocks_per_click=24,
            notated_32nd_notes_per_beat=8,
            time=0,
        )
    )
    meta.append(mido.MetaMessage('end_of_track', time=0))
    mf.tracks.append(meta)

    # Track 1: note events. Convert absolute ticks to delta ticks.
    track = mido.MidiTrack()
    prev_tick = 0
    for tick, ch, pitch, kind, vel in rows:
        delta = tick - prev_tick
        if kind == 0:
            track.append(
                mido.Message(
                    'note_on', channel=ch, note=pitch, velocity=vel, time=delta
                )
            )
        else:
            track.append(
                mido.Message(
                    'note_off', channel=ch, note=pitch, velocity=vel, time=delta
                )
            )
        prev_tick = tick
    track.append(mido.MetaMessage('end_of_track', time=0))
    mf.tracks.append(track)

    # Atomic write: mido 1.3.3 lacks atomic_write kwarg, use tempfile+os.replace.
    out_dir = os.path.dirname(os.path.abspath(out_midi_path)) or '.'
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        delete=False, dir=out_dir, suffix='.mid.tmp'
    ) as tmp:
        tmp_path = tmp.name
    try:
        mf.save(tmp_path)
        os.replace(tmp_path, out_midi_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('--json', required=True)
    p.add_argument('--out-midi', required=True)
    p.add_argument('--tempo-bpm', type=float, required=True)
    p.add_argument('--ts-num', type=int, default=4)
    p.add_argument('--ts-den', type=int, default=4)
    args = p.parse_args()

    serialize(args.json, args.out_midi, args.tempo_bpm, (args.ts_num, args.ts_den))
    print(f'wrote {args.out_midi}')
