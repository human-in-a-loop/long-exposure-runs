#!/usr/bin/env python3
# M-SCORE-1 — helper: cycle-6 basic-pitch JSONL -> per-stem .mid.
#
# Reads the FROZEN cycle-6 basic-pitch outputs (do NOT re-run basic-pitch)
# and emits one MIDI file per stem for merge_stems_to_score consumption.
#
# JSONL schema per row (empirically verified from
# data/transcribe/basic_pitch/synth_030s/bass.jsonl on cycle 8):
#   {"is_drum": bool, "onset_s": float, "offset_s": float,
#    "pitch": int (0-127), "velocity": int (0-127)}
# NOTE: brief's schema {onset_s, offset_s, pitch_midi, amplitude} did
# not match; the actual keys are `pitch` and `velocity`. This helper
# uses the actual keys.
#
# Conversion: seconds -> ticks at PPQ=480, tempo=500000 us/beat (120 BPM).
# This matches the brief's requested conversion factor.
#
# Interpreter guard: /usr/bin/python3.

import sys
assert sys.executable == '/usr/bin/python3', sys.executable

import json
from pathlib import Path
from typing import Dict, List, Tuple

import mido


DEFAULT_PPQ = 480
DEFAULT_TEMPO_US = 500000  # 120 BPM


def _load_jsonl(path: Path) -> List[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            rows.append(json.loads(ln))
    return rows


def jsonl_to_midi(
    jsonl_path,
    out_midi_path,
    *,
    ppq: int = DEFAULT_PPQ,
    tempo_us: int = DEFAULT_TEMPO_US,
    track_name: str = None,
) -> Path:
    """Read a basic-pitch JSONL file and write a single-track MIDI file.

    Notes are emitted in onset order; ties broken by (pitch, offset).
    Channel 9 is used if is_drum is True on any row (MIDI drum kit).
    """
    jsonl_path = Path(jsonl_path)
    out_midi_path = Path(out_midi_path)
    out_midi_path.parent.mkdir(parents=True, exist_ok=True)

    rows = _load_jsonl(jsonl_path)
    is_drum = any(bool(r.get("is_drum", False)) for r in rows)
    channel = 9 if is_drum else 0

    # Sort by onset, then pitch for stable output.
    rows.sort(key=lambda r: (float(r.get("onset_s", 0.0)),
                             int(r.get("pitch", 0))))

    seconds_per_tick = (tempo_us / 1_000_000.0) / ppq

    def s_to_ticks(s: float) -> int:
        return int(round(float(s) / seconds_per_tick))

    # Build a flat list of (abs_ticks, ordering, message) then convert to
    # delta ticks. `ordering` breaks ties: note_off before note_on at the
    # same tick is the safer convention (no phantom double-notes).
    events: List[Tuple[int, int, mido.Message]] = []
    for r in rows:
        onset_t = s_to_ticks(float(r["onset_s"]))
        offset_t = s_to_ticks(float(r["offset_s"]))
        if offset_t <= onset_t:
            offset_t = onset_t + 1
        pitch = int(r["pitch"])
        vel = max(1, min(127, int(r.get("velocity", 96))))
        events.append((onset_t, 1, mido.Message(
            "note_on", channel=channel, note=pitch, velocity=vel)))
        events.append((offset_t, 0, mido.Message(
            "note_off", channel=channel, note=pitch, velocity=0)))

    events.sort(key=lambda e: (e[0], e[1]))

    mid = mido.MidiFile(type=1, ticks_per_beat=ppq)
    meta_track = mido.MidiTrack()
    meta_track.append(mido.MetaMessage("set_tempo", tempo=tempo_us, time=0))
    meta_track.append(mido.MetaMessage(
        "time_signature", numerator=4, denominator=4,
        clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    mid.tracks.append(meta_track)

    note_track = mido.MidiTrack()
    if track_name:
        note_track.append(mido.MetaMessage("track_name", name=str(track_name), time=0))
    # Program change: only for non-drums. Drums use channel 9 which
    # uses the drum kit map regardless of program.
    if not is_drum:
        prog = 33 if track_name and track_name.lower() == "bass" else 0
        note_track.append(mido.Message(
            "program_change", channel=channel, program=prog, time=0))

    prev_ticks = 0
    for abs_ticks, _, msg in events:
        delta = abs_ticks - prev_ticks
        msg = msg.copy(time=max(0, delta))
        note_track.append(msg)
        prev_ticks = abs_ticks
    mid.tracks.append(note_track)
    mid.save(str(out_midi_path))
    return out_midi_path


def convert_all_stems(
    jsonl_dir,
    out_dir,
    stem_names=("drums", "bass", "other"),
) -> Dict[str, Path]:
    """Convert every {stem}.jsonl in a directory to {stem}.mid in out_dir.

    Returns dict of stem -> output MIDI path.
    """
    jsonl_dir = Path(jsonl_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {}
    for stem in stem_names:
        src = jsonl_dir / f"{stem}.jsonl"
        if not src.exists():
            continue
        dst = out_dir / f"{stem}.mid"
        jsonl_to_midi(src, dst, track_name=stem)
        result[stem] = dst
    return result


if __name__ == "__main__":
    src_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/transcribe/basic_pitch/synth_030s")
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/score/stems_from_bp")
    out = convert_all_stems(src_dir, out_dir)
    for stem, path in out.items():
        print(f"{stem}: {path}")
