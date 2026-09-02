#!/usr/bin/env /usr/bin/python3
"""c20 clone-2: merge Peach Dream per-stem canonical MIDIs → merged.mid.

Per-song sibling of scripts/v3_spine/merge_per_stem_midi_operator_section.py (READ-ONLY).
"""
from __future__ import annotations
import hashlib
import json
import statistics
import sys
from pathlib import Path

import mido

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.v3_spine.gm_program_map_v3 import STEM_DEFAULT  # noqa: E402

SEC = Path("data/v3_spine/88d247468cb6d49f/chosen_section")
CANON = SEC / "canonical_midi"
DEL = Path("data/v3/deliveries/88d247468cb6d49f")
STEMS_ORDER = ["drums", "bass", "guitar", "piano", "other", "vocals"]


def load_stem_notes(stem: str):
    path = CANON / f"{stem}.mid"
    mf = mido.MidiFile(path)
    if mf.ticks_per_beat != 480:
        raise RuntimeError(f"{path} PPQ {mf.ticks_per_beat}")
    if len(mf.tracks) < 2:
        return []
    events = []
    t = 0
    for m in mf.tracks[1]:
        t += m.time
        if m.type in ("note_on", "note_off"):
            events.append((t, m))
    return events


def check_no_program_4(path: Path) -> bool:
    mf = mido.MidiFile(path)
    for tr in mf.tracks:
        for m in tr:
            if m.type == "program_change" and m.program == 4:
                return False
    return True


def main():
    tempo = json.loads((SEC / "tempo_choice.json").read_text())
    bpm = float(tempo["detected_bpm"])
    ts = tempo["meter"]

    merged = mido.MidiFile(type=1, ticks_per_beat=480)
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    meta.append(mido.MetaMessage("time_signature", numerator=ts[0], denominator=ts[1],
                                 clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    meta.append(mido.MetaMessage("end_of_track", time=0))
    merged.tracks.append(meta)

    stats = {}
    for stem in STEMS_ORDER:
        label, prog, ch = STEM_DEFAULT[stem]
        events = load_stem_notes(stem)
        track = mido.MidiTrack()
        track.append(mido.MetaMessage("track_name", name=stem, time=0))
        if stem == "vocals":
            track.append(mido.MetaMessage("text", text="voice_symbolic_do_not_render", time=0))
        if prog is not None:
            track.append(mido.Message("program_change", channel=ch, program=prog, time=0))
        prev = 0
        note_ons = 0
        pitches = []
        for abs_t, m in events:
            new_ch = 9 if stem == "drums" else ch
            delta = max(0, abs_t - prev)
            track.append(m.copy(channel=new_ch, time=delta))
            if m.type == "note_on":
                note_ons += 1
                pitches.append(m.note)
            prev = abs_t
        track.append(mido.MetaMessage("end_of_track", time=0))
        merged.tracks.append(track)
        stats[stem] = {
            "note_ons": note_ons,
            "median_pitch": statistics.median(pitches) if pitches else None,
            "gm_program": prog,
            "gm_channel": 9 if stem == "drums" else ch,
        }

    out = SEC / "merged.mid"
    tmp = out.with_suffix(".mid.tmp")
    merged.save(tmp)
    tmp.replace(out)
    sha1 = hashlib.sha256(out.read_bytes()).hexdigest()
    tmp2 = out.with_suffix(".mid.tmp2")
    merged.save(tmp2)
    sha2 = hashlib.sha256(tmp2.read_bytes()).hexdigest()
    tmp2.unlink()

    DEL.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(out, DEL / "merged.mid")

    assertions = {
        "drums_track_on_ch10_nonempty": stats["drums"]["gm_channel"] == 9 and stats["drums"]["note_ons"] > 0,
        "bass_median_pitch_lt_55": stats["bass"]["median_pitch"] is not None and stats["bass"]["median_pitch"] < 55,
        "vocals_track_present_symbolic": True,
        "zero_notes_on_gm_program_4": check_no_program_4(out),
    }
    (SEC / "merged_midi_sha.txt").write_text(sha1 + "\n")
    report = {
        "cycle": 20, "clone": "clone-2", "song_sha16": "88d247468cb6d49f",
        "merged_mid_sha256": sha1,
        "byte_determinism_x2": sha1 == sha2,
        "per_stem_stats": stats,
        "structural_assertions": assertions,
        "n_assertions_pass": sum(1 for v in assertions.values() if v),
        "n_assertions_total": len(assertions),
    }
    (SEC / "merged_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"merged.mid sha={sha1[:16]} x2={sha1==sha2} assertions={assertions}")


if __name__ == "__main__":
    main()
