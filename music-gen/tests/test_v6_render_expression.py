#!/usr/bin/python3
"""v6 Phase 4 tests — expression + MIDI serializer: velocity curves widen the composer's 2-level velocities to >= 60 units
without clipping, CC64 pedal for pianos, CC11/CC1 swells for pads, none for bass; midi_io writes 480-PPQ files that round
trip (counts, CCs, offset_ms hook) and are byte-deterministic; derived parts follow the arrangement mutes.

Run: /usr/bin/python3 -m pytest tests/test_v6_render_expression.py -q
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

from scripts.v6.gen.render_v6 import expression, midi_io, parts  # noqa: E402

SONG = _ROOT / "data" / "v6" / "gen" / "iteration_01" / "gen_v6_song_1_donor_fixture_a"
BPM = 100.0


def _keys_notes():
    beat = 60.0 / BPM
    notes = []
    for i in range(64):
        for p in (55, 59, 62):
            notes.append({"index": len(notes), "pitch": p, "velocity": 88 if i % 4 == 0 else 80, "start_s": i * beat, "end_s": i * beat + beat * 0.9})
    return notes


def test_01_velocity_curve_widens_range_without_clipping() -> None:
    notes = _keys_notes()
    assert max(n["velocity"] for n in notes) - min(n["velocity"] for n in notes) == 8
    out, info = expression.realize_velocities(notes, "keys", {"velocity_layers": 32, "inventory_role": "piano"}, "t", BPM)
    vs = [n["velocity"] for n in out]
    assert info["realized_span"] >= 60 and max(vs) <= 127 and min(vs) >= 1 and len(out) == len(notes)
    assert all(n["velocity_in"] in (80, 88) for n in out)
    out2, _ = expression.realize_velocities(notes, "keys", {"velocity_layers": 32}, "t", BPM)
    assert [n["velocity"] for n in out2] == vs  # deterministic
    out3, _ = expression.realize_velocities(notes, "keys", {"velocity_layers": 32}, "t2", BPM)
    assert [n["velocity"] for n in out3] != vs  # different tag -> different jitter
    # the composer's strong beats stay louder on average than its weak beats
    strong = [n["velocity"] for n in out if n["velocity_in"] == 88]
    weak = [n["velocity"] for n in out if n["velocity_in"] == 80]
    assert sum(strong) / len(strong) > sum(weak) / len(weak)
    flat = [dict(n, velocity=100) for n in notes]
    out4, info4 = expression.realize_velocities(flat, "bass", {"velocity_layers": 1}, "t", BPM)
    assert info4["realized_span"] >= 60 and info4["stretched_to_min_span"]
    drums = [{"index": i, "pitch": 42 if i % 2 else 36, "velocity": 90, "start_s": i * 0.15, "end_s": i * 0.15 + 0.1} for i in range(64)]
    outd, _ = expression.realize_velocities(drums, "drums", {"velocity_layers": 5}, "t", BPM)
    hats = [n["velocity"] for n in outd if n["pitch"] == 42]
    kicks = [n["velocity"] for n in outd if n["pitch"] == 36]
    assert sum(hats) / len(hats) < sum(kicks) / len(kicks)
    print(f"test_01 PASS: keys 80/88 -> span {info['realized_span']} in {info['realized_range']}; flat bass stretched to {info4['realized_span']}; hats softer than kicks")


def test_02_cc_expression_per_role() -> None:
    plan = json.loads((SONG / "plan.json").read_text()) if SONG.exists() else None
    notes = _keys_notes()
    ccs, info = expression.expression_ccs(notes, "keys", {"inventory_role": "piano"}, BPM, plan, 76.8)
    assert info["cc64_pedal_downs"] > 10 and all(c == 64 for _, c, _ in ccs)
    downs = [t for t, c, v in ccs if v == 127]
    ups = [t for t, c, v in ccs if v == 0]
    assert len(downs) == len(ups) and all(u > d for d, u in zip(downs, ups))
    ccs_o, info_o = expression.expression_ccs(notes, "keys", {"inventory_role": "organ"}, BPM, plan, 76.8)
    assert info_o["cc11_swells"] > 0 and info_o["cc64_pedal_downs"] == 0 and all(c == 11 for _, c, _ in ccs_o)
    vals = [v for _, _, v in ccs_o]
    assert min(vals) >= 55 and max(vals) <= 100
    ccs_p, info_p = expression.expression_ccs(notes, "pad", {"inventory_role": "pad"}, BPM, plan, 76.8)
    assert info_p["cc11_swells"] > 0 and info_p["cc1_sweeps"] > 0 and {c for _, c, _ in ccs_p} == {1, 11}
    ccs_b, info_b = expression.expression_ccs(notes, "bass", {"inventory_role": "electric_bass"}, BPM, plan, 76.8)
    assert ccs_b == [] and info_b["n_cc"] == 0
    print(f"test_02 PASS: piano pedal {info['cc64_pedal_downs']} downs; organ {info_o['cc11_swells']} CC11 swells; pad CC11+CC1; bass none")


def test_03_midi_io_round_trip_offset_hook_and_determinism() -> None:
    import mido
    events = [{"index": 0, "instrument": "electric_piano", "pitch": 60, "start_time": 1.0, "type": "start", "velocity": 90},
              {"end_time": 1.5, "start_event_index": 0, "type": "end"},
              {"index": 1, "instrument": "electric_piano", "pitch": 64, "start_time": 1.0, "type": "start", "velocity": 70, "offset_ms": 25.0},
              {"end_time": 1.5, "start_event_index": 1, "type": "end"}]
    notes = midi_io.pair_events(events)
    assert len(notes) == 2 and abs(notes[1]["start_s"] - 1.025) < 1e-9 and abs(notes[1]["end_s"] - 1.525) < 1e-9
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "a.mid"
        m1 = midi_io.write_midi(notes, p, 120.0, channel=0, program=4, bank=0, ccs=[(0.0, 64, 127), (2.0, 64, 0)], song_len_s=4.0)
        h1 = hashlib.sha256(p.read_bytes()).hexdigest()
        midi_io.write_midi(notes, p, 120.0, channel=0, program=4, bank=0, ccs=[(0.0, 64, 127), (2.0, 64, 0)], song_len_s=4.0)
        assert hashlib.sha256(p.read_bytes()).hexdigest() == h1
        mf = mido.MidiFile(str(p))
        assert mf.ticks_per_beat == 480
        msgs = [m for m in mf.tracks[1]]
        ons = [m for m in msgs if m.type == "note_on"]
        offs = [m for m in msgs if m.type == "note_off"]
        ccs = [m for m in msgs if m.type == "control_change"]
        assert len(ons) == 2 and len(offs) == 2 and [m.control for m in ccs] == [0, 32, 7, 64, 64]
        assert [m.type for m in msgs[:4]] == ["control_change", "control_change", "program_change", "control_change"] and msgs[2].program == 4
        ticks, t = [], 0
        for m in msgs:
            t += m.time
            if m.type == "note_on":
                ticks.append(t)
        assert ticks == [960, 984]  # 1.0 s @120 BPM = 2 beats = 960 ticks; +25 ms = +24 ticks
        assert m1["n_notes"] == 2 and m1["n_cc"] == 2 and m1["end_s"] >= 4.0
        # drums: bank 128 -> channel 9, no CC0
        q = Path(td) / "d.mid"
        midi_io.write_midi([{"pitch": 36, "velocity": 100, "start_s": 0.0, "end_s": 0.1}], q, 120.0, channel=9, program=8, bank=128)
        msgs = list(mido.MidiFile(str(q)).tracks[1])
        assert msgs[0].type == "program_change" and msgs[0].channel == 9 and msgs[0].program == 8
    print("test_03 PASS: pair_events honours offset_ms; 480 PPQ; CC0/CC32/program at tick 0; byte-deterministic")


def test_04_derived_parts_follow_arrangement() -> None:
    if not SONG.exists():
        print("test_04 SKIP: fixture song missing")
        return
    plan = json.loads((SONG / "plan.json").read_text())
    keys = midi_io.pair_events(json.loads((SONG / "generated_json" / "keys.json").read_text()))
    bar = 240.0 / plan["tempo_bpm"]
    muted = {b for b, a in enumerate(plan["arrangement_per_bar"]) if "keys" in a["mute"]}
    pad = parts.pad_part(plan, plan["tempo_bpm"])
    assert pad and all(55 <= n["pitch"] <= 79 for n in pad) and not any(int(n["start_s"] // bar) in muted for n in pad)
    assert all(n["end_s"] > n["start_s"] for n in pad)
    comp = parts.comp_guitar_part(keys, plan, plan["tempo_bpm"], "t")
    assert comp and len(comp) < len(keys) and all(52 <= n["pitch"] <= 79 for n in comp) and not any(int(n["start_s"] // bar) in muted for n in comp)
    assert comp == parts.comp_guitar_part(keys, plan, plan["tempo_bpm"], "t")
    perc = parts.percussion_part(plan, plan["tempo_bpm"], {"mapped_keys": [60, 61, 62]}, "t")
    dm = {b for b, a in enumerate(plan["arrangement_per_bar"]) if "drums" in a["mute"]}
    assert perc and len({n["pitch"] for n in perc}) == 1 and not any(int(n["start_s"] // bar) in dm for n in perc)
    print(f"test_04 PASS: pad {len(pad)} notes, comp_guitar {len(comp)} (from {len(keys)} keys notes), percussion {len(perc)}; mutes respected")


if __name__ == "__main__":
    test_01_velocity_curve_widens_range_without_clipping()
    test_02_cc_expression_per_role()
    test_03_midi_io_round_trip_offset_hook_and_determinism()
    test_04_derived_parts_follow_arrangement()
