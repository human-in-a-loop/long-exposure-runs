#!/usr/bin/python3
"""v6 Phase 2 tests — voicing DP + validators: parallels avoided when a cost-free alternative exists, hand-made parallels detected,
caps table loads.

Run: /usr/bin/python3 tests/test_v6_gen_voicing.py      or      /usr/bin/python3 -m pytest tests/test_v6_gen_voicing.py -q
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

from scripts.v6.gen import validators as V  # noqa: E402
from scripts.v6.gen import voicing as VO  # noqa: E402


def _song_with_voicings(states, voicings, tonic=0, mode="major"):
    """Minimal song dict for the voicing-level validators (one chord slot per bar, no melody/bass/drums)."""
    slots = [{"bar": i, "beat": 0, "state": s, "voicing": list(v), "cost": None} for i, (s, v) in enumerate(zip(states, voicings))]
    return {"tonic": tonic, "mode": mode, "n_bars": len(states), "bars_per_section": len(states), "sections": [{"index": 0, "label": "A", "start_bar": 0, "n_bars": len(states)}],
            "arrangement": [{"mute": [], "fill": None, "hold": False} for _ in states], "beat_chords": [[s] * 4 for s in states], "chord_slots": slots,
            "phrases": [{"start_bar": 0, "n_bars": len(states), "cadence_planned": "authentic", "cadence_realized": "authentic", "conditioning_ok": True, "slots": [{"bar": r["bar"], "beat": 0} for r in slots]}],
            "harmonic_rhythm_planned": [1] * len(states), "melody": [], "bass": [], "keys": [], "drums": []}


def test_01_candidates_cover_the_chord_in_register() -> None:
    for st in ("0:maj", "2:min", "7:7", "0:maj7", "7:9", "5:sus"):
        cands = VO.candidates(st, 0)
        assert cands, st
        ct = VO.chord_tones(st, 0)
        allowed = [set(ct["pcs"])] + [set(a) for a in ct["alt_pcs"]]
        for v in cands:
            assert len(v) == 4 and all(VO.KEYS_LO <= p <= VO.KEYS_HI for p in v) and {p % 12 for p in v} in allowed and list(v) == sorted(v)
    assert VO.chord_tones("7:9", 0)["pcs"] == [7, 11, 5, 9], "9 chord drops the 5th: root, 3rd, 7th, 9th"
    assert VO.chord_tones("7:9", 0)["alt_pcs"] == [[11, 2, 5, 9]], "Phase 5: rootless 3-5-7-9 alternative (bass carries the root)"
    assert any({p % 12 for p in v} == {11, 2, 5, 9} for v in VO.candidates("7:9", 0))
    assert VO.candidates("N", 0) == []
    print("test_01 PASS: candidates cover the chord tones, 4 strictly ascending voices in 52..79")


def test_02_dp_avoids_parallel_fifths_octaves_when_a_cost_free_alternative_exists() -> None:
    # I -> ii (C -> Dm) root-position planing is the classic parallel-5th/8ve trap; contrary/oblique voicings exist at equal or lower cost.
    seqs = [["0:maj", "2:min", "0:maj", "2:min"], ["0:maj", "5:maj", "7:maj", "0:maj"], ["9:min", "7:maj", "5:maj", "4:min", "2:min", "0:maj"]]
    for states in seqs:
        out = VO.voice_sequence(states, 0, "major", [False] * len(states))
        vs = [tuple(r["voicing"]) for r in out]
        for a, b in zip(vs, vs[1:]):
            assert VO.parallel_perfects(a, b) == 0, (states, a, b)
            assert VO.crossings(a, b) == 0, (states, a, b)
        assert all(r["cost"]["parallels"] == 0.0 for r in out)
    # with a bass root line the DP also avoids parallels against the bass
    from scripts.v6.gen.bassline import root_line
    states = ["0:maj", "5:maj", "7:maj", "0:maj", "9:min", "5:maj", "7:7", "0:maj"]
    roots = root_line(states, 0)
    out = VO.voice_sequence(states, 0, "major", [False] * 8, roots)
    vs = [tuple(r["voicing"]) for r in out]
    for (a, b), (ra, rb) in zip(zip(vs, vs[1:]), zip(roots, roots[1:])):
        assert VO.parallel_perfects(a, b, ra, rb) == 0, (a, b, ra, rb)
    print("test_02 PASS: DP output has no parallel 5ths/8ves (keys-internal and vs the bass root line) nor crossings on trap sequences")


def test_03_validators_detect_hand_made_parallels_sevenths_crossings() -> None:
    # parallel fifths + octaves: C-G-C-E -> D-A-D-F (every pair planes)
    song = _song_with_voicings(["0:maj", "2:min"], [(60, 67, 72, 76), (62, 69, 74, 77)])
    par = V.parallel_perfect_intervals(song)
    assert par["parallel_fifths"] >= 1 and par["parallel_octaves"] >= 1, par
    assert VO.parallel_perfects((60, 67, 72, 76), (62, 69, 74, 77)) == 2  # (60,67)->(62,69) parallel 5th and (60,72)->(62,74) parallel 8ve
    # unresolved seventh: G7 (F = 65 is the 7th) jumping UP to G (67) instead of down to E
    song7 = _song_with_voicings(["7:7", "0:maj"], [(55, 59, 62, 65), (55, 60, 64, 67)])
    assert V.unresolved_sevenths(song7) == 1, V.unresolved_sevenths(song7)
    song7ok = _song_with_voicings(["7:7", "0:maj"], [(55, 59, 62, 65), (55, 60, 64, 64 + 0)])
    assert V.unresolved_sevenths(song7ok) == 0
    # Phase 5 semantics: a 7th RETAINED as a common tone is resolved (Em7's D held into G9, rootless 3-5-7-9 voicing)
    song7held = _song_with_voicings(["4:min7", "7:9"], [(52, 55, 59, 62), (53, 57, 59, 62)])
    assert V.unresolved_sevenths(song7held) == 0, V.unresolved_sevenths(song7held)
    # ... even when the retained pitch sits in another voice; a 7th jumping away is unresolved
    song7other = _song_with_voicings(["4:min7", "7:9"], [(52, 55, 59, 62), (57, 59, 62, 65)])
    assert V.unresolved_sevenths(song7other) == 0
    assert VO.seventh_resolvable("0:maj7", "7:sus") is False and VO.seventh_resolvable("0:maj7", "7:7") is True and VO.seventh_resolvable("4:min7", "7:9") is True
    assert VO.seventh_resolvable("7:7", "0:maj") is True and VO.seventh_resolvable("0:7", "0:maj") is False and VO.seventh_resolvable("N", "0:maj") is True
    # crossing: top voice drops below the previous alto
    songx = _song_with_voicings(["0:maj", "5:maj"], [(60, 64, 67, 72), (53, 57, 60, 65)])
    assert V.voice_crossing(songx) >= 1
    # leading tone at the cadence (B = 71 in C major) must go to C; here it falls to G
    songlt = _song_with_voicings(["7:maj", "0:maj"], [(55, 62, 67, 71), (55, 60, 64, 67)])
    assert V.leading_tone_unresolved_at_cadence(songlt)["keys"] == 1
    songlt_ok = _song_with_voicings(["7:maj", "0:maj"], [(55, 62, 67, 71), (55, 60, 67, 72)])
    assert V.leading_tone_unresolved_at_cadence(songlt_ok)["keys"] == 0
    # the DP itself resolves the leading tone at a flagged cadence
    out = VO.voice_sequence(["7:maj", "0:maj"], 0, "major", [False, True])
    a, b = tuple(out[0]["voicing"]), tuple(out[1]["voicing"])
    assert VO.unresolved_leading_tone(a, b, 0, "major", True) == 0
    print("test_03 PASS: validators detect hand-made parallel 5ths/8ves, an unresolved 7th, a crossing, an unresolved leading tone")


def test_04_caps_table_loads_and_validate_runs_on_a_clean_sequence() -> None:
    for k, c in V.CAPS.items():
        assert set(c) >= {"op", "cap", "per", "doc"} and c["op"] in ("<=", "==") and c["per"] in ("per_64_bars", "song", "fraction"), k
    states = ["0:maj", "5:maj", "7:7", "0:maj"]
    out = VO.voice_sequence(states, 0, "major", [False, False, False, True])
    song = _song_with_voicings(states, [tuple(r["voicing"]) for r in out])
    res = V.validate(song)
    assert res["metrics"]["parallel_fifths"] == 0 and res["metrics"]["unresolved_sevenths"] == 0 and res["metrics"]["voice_crossing"] == 0
    assert set(res["metrics"]) == set(V.CAPS) and set(res["cap_pass"]) == set(V.CAPS)
    agg = V.aggregate({"s1": res, "s2": res})
    assert agg["n_songs"] == 2 and "cap_pass_counts" in agg and V.format_table(agg).startswith("song")
    print("test_04 PASS: caps table complete; validate()/aggregate()/format_table() on a DP-voiced sequence")


def test_05_comping_onsets_include_chord_changes() -> None:
    on, name = VO.comping_onsets(2, [0, 8], "t|comp", None)
    assert 0 in on and 8 in on and name in VO.TEMPLATES
    on2, name2 = VO.comping_onsets(1, [0], "t|comp2", {"stats": {"pooled": {"ioi16_histogram": [0, 0, 0, 1.0] + [0] * 12}}})
    assert on2 == [0, 4, 8, 12] and name2 == "comping_v5_ioi_walk"
    print("test_05 PASS: comping onsets force chord-change slots; comping_v5 IOI walk honoured")


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
