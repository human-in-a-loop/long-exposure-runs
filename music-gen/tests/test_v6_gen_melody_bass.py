#!/usr/bin/python3
"""v6 Phase 2 tests — melody grammar (skeleton = chord tones, single peak, resolved leaps, range) and bass (roots on every change,
register, counterpoint factors), over several seeds on the fixture models.

Run: /usr/bin/python3 tests/test_v6_gen_melody_bass.py      or      /usr/bin/python3 -m pytest tests/test_v6_gen_melody_bass.py -q
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

from scripts.v6.gen import bassline as B  # noqa: E402
from scripts.v6.gen import melody as M  # noqa: E402
from scripts.v6.gen.common import SLOTS, state_pcs  # noqa: E402
from scripts.v6.gen.compose_v6 import compose_song  # noqa: E402
from scripts.v6.gen.fixtures import build_fixtures  # noqa: E402
from scripts.v6.gen.harmony import label_harmony  # noqa: E402
from scripts.v6.gen.planner import build_plan  # noqa: E402

FX = build_fixtures()
SEEDS = range(5)


def _label_runs():
    for seed in SEEDS:
        plan = build_plan(FX, f"mt|seed={seed}", 120.0, 32)
        for lab, lp in plan["label_plans"].items():
            h = label_harmony(FX["chain"], lp, "major", f"mt{seed}|{lab}")
            roots = B.root_line([s["state"] for s in h["slots"]], 0)
            rbs = {(s["bar"], s["beat"]): r for s, r in zip(h["slots"], roots) if r is not None}
            yield seed, lab, lp, h, M.label_melody(FX, lp, h, 0, "major", lab, f"mt{seed}|{lab}", rbs)


def test_01_skeleton_notes_are_chord_tones_single_peak_leaps_resolve_range() -> None:
    n_phr = 0
    for seed, lab, lp, h, mel in _label_runs():
        for ph in mel["phrases"]:
            sk = ph["skeleton"]
            if sk is None:
                continue
            n_phr += 1
            b0 = next(p["start_bar"] for p in lp["phrases"] if p["index"] == len([x for x in mel["phrases"][:mel["phrases"].index(ph)]]))
            for s, p in zip(sk["slots"], sk["pitches"]):
                st = h["beat_chords"][b0 + s // SLOTS][(s % SLOTS) // 4]
                pcs = state_pcs(st, 0)
                assert pcs is None or p % 12 in pcs, (seed, lab, s, p, st)
                assert M.REGISTER[0] <= p <= M.REGISTER[1] + 0
            assert sk["violations"] == {"single_peak": 0, "leaps_unresolved": 0, "range": 0, "direction": 0}, (seed, lab, sk)
            assert max(sk["pitches"]) - min(sk["pitches"]) <= M.PHRASE_RANGE
            top = max(sk["pitches"])
            assert sk["pitches"].count(top) == 1
            assert M.unresolved_leaps(sk["pitches"]) == 0
    assert n_phr >= 10
    print(f"test_01 PASS: {n_phr} skeletons: all chord tones, unique peak in the middle half, leaps resolved, range <= 12")


def test_02_full_melody_roles_strong_beats_and_cadence_degrees() -> None:
    n_notes = n_strong = 0
    for seed, lab, lp, h, mel in _label_runs():
        for n in mel["notes"]:
            n_notes += 1
            assert n["role"] in ("skeleton", "cadence", "passing", "neighbour", "anticipation", "suspension", "resolution", "escape", "chord_tone")
            st = h["beat_chords"][n["slot"] // SLOTS][(n["slot"] % SLOTS) // 4]
            pcs = state_pcs(st, 0)
            if n["slot"] % 8 == 0 and n["role"] not in ("suspension", "anticipation") and pcs:
                n_strong += 1
                assert n["pitch"] % 12 in pcs, (seed, lab, n, st)
            assert n["dur16"] >= 1
        for ph, hp in zip(mel["phrases"], h["phrases"]):
            cad = [n for n in mel["notes"] if n["role"] == "cadence" and n["phrase"] == hp["phrase_index"]]
            assert len(cad) == 1, (seed, lab, hp["phrase_index"])
            assert cad[0]["dur16"] >= 8, "cadence note held >= a half note"
            table = M.CADENCE_DEGREES[ph["cadence_used"]]
            deg = ((cad[0]["pitch"] - 0) % 12)
            from scripts.v6.gen.common import degree_of
            assert degree_of(cad[0]["pitch"], 0, "major") in table or (state_pcs(hp["chords"][-1], 0) and deg in state_pcs(hp["chords"][-1], 0)), (ph["cadence_used"], cad[0])
        # melody range per phrase over ALL notes
        for hp in h["phrases"]:
            ns = [n["pitch"] for n in mel["notes"] if n["phrase"] == hp["phrase_index"]]
            if ns:
                assert max(ns) - min(ns) <= M.PHRASE_RANGE
    assert n_notes > 100 and n_strong > 30
    print(f"test_02 PASS: {n_notes} notes, {n_strong} strong-beat chord tones, cadence notes held >= half note with table degrees")


def test_03_bass_roots_on_every_change_register_and_factors() -> None:
    from scripts.v6.gen import drums as D
    for seed, lab, lp, h, mel in _label_runs():
        g = D.sample_groove_bars(FX["groove"], f"mt{seed}|{lab}|g", 8)
        roots = B.root_line([s["state"] for s in h["slots"]], 0)
        rbs = {(s["bar"], s["beat"]): r for s, r in zip(h["slots"], roots) if r is not None}
        bs = B.label_bass(FX["bass"], g, h["beat_chords"], mel["notes"], {}, 0, f"mt{seed}|{lab}", lambda t, p, c: 100, rbs)
        by_slot = {}
        for n in bs["notes"]:
            assert B.REGISTER[0] <= n["pitch"] <= B.REGISTER[1]
            assert n["cls"] in B.CLASSES
            by_slot.setdefault(n["slot"], []).append(n)
        prev = None
        for b in range(8):
            for bt in range(4):
                st = h["beat_chords"][b][bt]
                if st != prev and st != "N":
                    notes = by_slot.get(b * SLOTS + bt * 4, [])
                    assert notes and any(n["pitch"] % 12 == state_pcs(st, 0)[0] and n["cls"] == "root" for n in notes), (seed, lab, b, bt, st, notes)
                    assert notes[0]["pitch"] == rbs[(b, bt)], "forced root must equal the shared root line"
                prev = st
        assert bs["n_changes"] >= 8
    assert all(B.REGISTER[0] <= p <= B.REGISTER[1] for p in B.root_line(["0:maj", "5:maj", "7:7", "9:min", "N", "2:min"], 0) if p is not None)
    assert B.is_parallel_perfect(40, 64, 42, 66) and not B.is_parallel_perfect(40, 64, 42, 64) and not B.is_parallel_perfect(40, 65, 42, 67)
    print("test_03 PASS: bass root (class 'root', root-line pitch) sounds on every chord change; register 28..50; parallel detector")


def test_04_composed_songs_pass_melody_bass_cadence_validators() -> None:
    for i, bpm in enumerate((100.0, 120.0, 152.0)):
        res = compose_song(FX, f"gen_v6_song_{i + 1}", sorted(["fixture_a", "fixture_b", "fixture_c"])[i], 0, bpm, 32)
        m = res["validators"]["metrics"]
        assert m["melody_range_violations"] == 0 and m["melodic_leaps_unresolved"] == 0, m
        assert m["melody_strong_beat_non_chord_tones"] == 0.0, m
        assert m["bass_root_missing_on_change"] == 0 and m["cadences_realized"] == 1.0 and m["harmonic_rhythm_realized"] == 1.0, m
        assert m["unresolved_sevenths"] <= 2 and m["leading_tone_unresolved_at_cadence"] <= 1 and m["voice_crossing"] == 0, m
        assert m["section_repeat_integrity"] is True
        assert res["validators"]["detail"]["parallels"]["keys_fifths"] == 0 and res["validators"]["detail"]["parallels"]["bass_keys_fifths"] == 0
    print("test_04 PASS: 3 composed fixture songs: melody/bass/cadence/harmonic-rhythm/repeat validators all within caps")


def _run_all() -> int:
    fails = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        try:
            fn()
        except AssertionError as exc:
            fails += 1
            print(f"{name} FAIL: {exc}")
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"{name} ERROR: {type(exc).__name__}: {exc}")
    print("ALL PASS" if not fails else f"{fails} FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(_run_all())
