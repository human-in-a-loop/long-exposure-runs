#!/usr/bin/python3
"""v6 Phase 4 — minimal deterministic MIDI serializer (480 PPQ) for the realistic renderer: notes + control changes.

created: 2026-10-04
milestone: M-V6-RENDER-4/realistic-renderer

scripts/v6/gen/serialize_v6.py (Phase 3) does not exist yet, so this module owns the v5 event -> note pairing and the
mido write-out. It accepts the hooks Phase 3 will use: a start event may carry "offset_ms" (added to start AND end so
the duration is kept) and fractional "start_time"/"end_time" seconds. Program/bank forcing for sf2 patches is written
into the file (CC0/CC32 + program_change at tick 0 — what fluidsynth honours; drums go on channel 9 so fluidsynth's GS
mode picks bank 128). Event order inside a tick is CC < note_off < note_on so sustain/expression take effect before
the note and a repeated pitch is released before it is re-struck. Pure function of its inputs (mido writes are
byte-deterministic); no PRNG.
"""
from __future__ import annotations

from pathlib import Path

PPQ = 480
DRUM_CHANNEL = 9
NOTE_OFF_VELOCITY = 0
MIN_NOTE_TICKS = 1


def pair_events(events: list) -> list:
    """v5 event list -> [{index, pitch, velocity, start_s, end_s, instrument, extra}] sorted by (start, pitch, index)."""
    starts, notes = {}, []
    for ev in events:
        if ev.get("type") == "start":
            starts[int(ev["index"])] = ev
    for ev in events:
        if ev.get("type") != "end":
            continue
        s = starts.get(int(ev["start_event_index"]))
        if s is None:
            continue
        off = float(s.get("offset_ms", 0.0)) / 1000.0
        t0, t1 = float(s["start_time"]) + off, float(ev["end_time"]) + off
        notes.append({"index": int(s["index"]), "pitch": int(s["pitch"]), "velocity": int(s.get("velocity", 100)),
                      "start_s": max(0.0, t0), "end_s": max(max(0.0, t0) + 0.005, t1), "instrument": s.get("instrument", ""),
                      "extra": {k: s[k] for k in s if k not in ("index", "pitch", "velocity", "start_time", "type", "instrument", "offset_ms")}})
    notes.sort(key=lambda n: (n["start_s"], n["pitch"], n["index"]))
    return notes


def seconds_to_ticks(t: float, bpm: float, ppq: int = PPQ) -> int:
    return int(round(float(t) * float(bpm) / 60.0 * ppq))


def write_midi(notes: list, out_path: Path, bpm: float, channel: int = 0, program: int | None = None, bank: int | None = None,
               ccs: list | None = None, song_len_s: float | None = None, tail_s: float = 1.5, ppq: int = PPQ) -> dict:
    """notes: [{pitch, velocity, start_s, end_s}], ccs: [(time_s, cc_number, value)]. Returns a small manifest."""
    import mido
    rows = []  # (tick, order, kind, a, b)
    for t, cc, val in (ccs or []):
        rows.append((seconds_to_ticks(t, bpm, ppq), 0, "cc", int(cc), max(0, min(127, int(val)))))
    for n in notes:
        s_tick = seconds_to_ticks(n["start_s"], bpm, ppq)
        e_tick = max(seconds_to_ticks(n["end_s"], bpm, ppq), s_tick + MIN_NOTE_TICKS)
        vel = max(1, min(127, int(n["velocity"])))
        rows.append((s_tick, 2, "on", int(n["pitch"]), vel))
        rows.append((e_tick, 1, "off", int(n["pitch"]), NOTE_OFF_VELOCITY))
    rows.sort(key=lambda r: (r[0], r[1], r[3], r[4]))
    mf = mido.MidiFile(type=1, ticks_per_beat=ppq)
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(float(bpm)), time=0))
    meta.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    meta.append(mido.MetaMessage("end_of_track", time=0))
    mf.tracks.append(meta)
    trk = mido.MidiTrack()
    if bank is not None and bank != 128:
        trk.append(mido.Message("control_change", channel=channel, control=0, value=min(int(bank), 127), time=0))
        trk.append(mido.Message("control_change", channel=channel, control=32, value=0, time=0))
    if program is not None:
        trk.append(mido.Message("program_change", channel=channel, program=int(program), time=0))
    trk.append(mido.Message("control_change", channel=channel, control=7, value=100, time=0))
    prev = 0
    for tick, _order, kind, a, b in rows:
        delta, prev = tick - prev, tick
        if kind == "cc":
            trk.append(mido.Message("control_change", channel=channel, control=a, value=b, time=delta))
        else:
            trk.append(mido.Message("note_on" if kind == "on" else "note_off", channel=channel, note=a, velocity=b, time=delta))
    last_s = max([n["end_s"] for n in notes] + [t for t, _, _ in (ccs or [])] + [0.0])
    end_tick = seconds_to_ticks(max(last_s, song_len_s or 0.0) + tail_s, bpm, ppq)
    trk.append(mido.MetaMessage("end_of_track", time=max(0, end_tick - prev)))
    mf.tracks.append(trk)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_name(out_path.name + ".tmp")
    mf.save(str(tmp))
    tmp.replace(out_path)
    return {"n_notes": len(notes), "n_cc": len(ccs or []), "channel": channel, "program": program, "bank": bank, "ppq": ppq,
            "end_s": round(end_tick / ppq * 60.0 / float(bpm), 4)}
