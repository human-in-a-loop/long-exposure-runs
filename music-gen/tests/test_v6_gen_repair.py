#!/usr/bin/python3
"""v6 Phase 5 tests — repair.py (deterministic counterpoint repair): find_violations re-counts the validators' rules with locations;
every repair branch fixes a violation INJECTED into real label content (free bass re-pick / melody NCT re-pick / skeleton alternative
with phrase re-realisation; leap: following-note step back, leap note, skeleton; leading tone: cadence note -> tonic, note before);
a skeleton repair keeps earlier NCT repairs; repairs are byte-deterministic; seeds 0..3 x 3 fixtures x {plain, humanize} compose with
ZERO unforced cap failures (and zero forced ones) and the recurrence pass keeps the skeleton identical.

Run: /usr/bin/python3 tests/test_v6_gen_repair.py      or      /usr/bin/python3 -m pytest tests/test_v6_gen_repair.py -q
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

from scripts.v6.gen import compose_v6 as C  # noqa: E402
from scripts.v6.gen import repair as R  # noqa: E402
from scripts.v6.gen import sweep_seeds as SW  # noqa: E402
from scripts.v6.gen import validators as V  # noqa: E402
from scripts.v6.gen.bassline import REGISTER, is_parallel_perfect  # noqa: E402
from scripts.v6.gen.common import SLOTS, canonical_json, state_pcs  # noqa: E402
from scripts.v6.gen.fixtures import build_fixtures  # noqa: E402
from scripts.v6.gen.melody import MAX_LEAP  # noqa: E402
from scripts.v6.gen.planner import build_plan  # noqa: E402

FX = build_fixtures()
TONIC, MODE, BPM = 0, "major", 120.0
LT, TONIC_PC = (TONIC + 11) % 12, TONIC % 12


class _Case:
    """Label content of one fixture song (corpus-independent fixture models), repaired once so injections start from zero violations."""

    def __init__(self, seed: int):
        self.tag = f"gen_v6_song_1|donor=fixture_a|seed={seed}"
        self.vel = C.velocity_fns(None)
        self.vel["profiles"] = None
        self.plan = build_plan(FX, self.tag, BPM, 32)
        self.labels = C.compose_labels(FX, self.plan, TONIC, MODE, BPM, self.tag, self.vel)
        self.initial = R.repair_labels(FX, self.plan, self.labels, TONIC, MODE, self.flat)
        assert not self.violations(), self.violations()
        self.heard = {s["label"] for s in self.plan["form"]["sections"] if not any("melody" in a["mute"] for a in self.plan["arrangement"]["per_bar"][s["start_bar"]:s["start_bar"] + 8])}

    def flat(self) -> dict:
        return C.flatten(self.plan, self.labels, TONIC, MODE, BPM, self.vel, self.tag)

    def violations(self) -> list:
        return [v for v in R.find_violations(self.flat()) if v["rule"] not in R.GUARD_RULES]

    def repair(self) -> dict:
        return R.repair_labels(FX, self.plan, self.labels, TONIC, MODE, self.flat)

    def mel(self, lab: str) -> list:
        return sorted(self.labels[lab]["melody"]["notes"], key=lambda n: n["slot"])

    def sounding(self, lab: str, slot: int):
        return next((n for n in self.mel(lab) if n["slot"] <= slot < n["slot"] + n["dur16"]), None)

    def window(self, lab: str, note: dict) -> tuple:
        return R._window(self.labels[lab], note["phrase"], note["slot"])


def _set_melody(case: _Case, lab: str, note: dict, pitch: int, role: str | None = None) -> None:
    note["pitch"] = int(pitch)
    if role:
        note["role"] = role
    if note.get("role") in R.SKELETON_ROLES:
        mph = case.labels[lab]["melody"]["phrases"][note["phrase"]]
        rel = note["slot"] - case.plan["label_plans"][lab]["phrases"][note["phrase"]]["start_bar"] * SLOTS
        if rel in mph["skeleton"]["slots"]:
            mph["skeleton"]["pitches"][mph["skeleton"]["slots"].index(rel)] = int(pitch)


def _inject_parallel(case: _Case, want_free_second: bool, want_skeleton: bool | None = None):
    """Shift a bass note (free when want_free_second, else a forced root pair with melody roles per want_skeleton) into a parallel perfect
    with the melody sounding at consecutive bass onsets; returns (label, slot) or None."""
    for lab in sorted(case.heard):
        notes = case.labels[lab]["bass"]["notes"]
        for j in range(1, len(notes)):
            b0, b1 = notes[j - 1], notes[j]
            m0, m1 = case.sounding(lab, b0["slot"]), case.sounding(lab, b1["slot"])
            if m0 is None or m1 is None or m0["pitch"] == m1["pitch"]:
                continue
            if want_free_second:
                if b1["on_change"]:
                    continue
                ia = (m0["pitch"] - b0["pitch"]) % 12
                p1 = b0["pitch"] + (m1["pitch"] - m0["pitch"])
                if ia not in (0, 7) or not (REGISTER[0] <= p1 <= REGISTER[1]) or not is_parallel_perfect(b0["pitch"], m0["pitch"], p1, m1["pitch"]):
                    continue
                b1["pitch"], b1["cls"] = int(p1), "fifth" if ia == 7 else "octave"
                return lab, b1["slot"]
            if not (b0["on_change"] and b1["on_change"]) or b0["pitch"] == b1["pitch"]:
                continue
            if (m1.get("role") in R.SKELETON_ROLES) != bool(want_skeleton):
                continue
            lo, hi = case.window(lab, m1)
            for ia in (0, 7):
                p = m0["pitch"] + (b1["pitch"] - b0["pitch"]) if (m0["pitch"] - b0["pitch"]) % 12 == ia else None
                if p is not None and lo <= p <= hi and is_parallel_perfect(b0["pitch"], m0["pitch"], b1["pitch"], p):
                    _set_melody(case, lab, m1, p)
                    return lab, b1["slot"]
    return None


def _par_keys(case: _Case) -> set:
    return {v["key"] for v in case.violations() if v["rule"] in ("parallel_fifth", "parallel_octave")}


def test_01_find_violations_matches_validators_on_hand_made_song() -> None:
    def mel(slot, pitch, dur=4, role="skeleton"):
        return {"slot": slot, "pitch": pitch, "dur16": dur, "role": role, "section": 0, "phrase": 0}
    chord_slots = [{"bar": b, "beat": 0, "state": "0:maj" if b % 2 == 0 else "7:maj", "voicing": None} for b in range(4)]
    song = {"tonic": 0, "mode": "major", "n_bars": 4, "bars_per_section": 4, "sections": [{"index": 0, "label": "A", "start_bar": 0, "n_bars": 4}],
            "arrangement": [{"mute": [], "fill": None, "hold": False}] * 4, "beat_chords": [[c["state"]] * 4 for c in chord_slots], "chord_slots": chord_slots,
            "phrases": [{"start_bar": 0, "n_bars": 4, "cadence_planned": "authentic", "cadence_realized": "authentic", "section": 0, "label": "A",
                         "slots": [{"bar": b, "beat": 0, "state": c["state"]} for b, c in enumerate(chord_slots)]}],
            # bass C -> G (up 7) under melody C -> G (parallel 8ve: both pcs equal) ; melody leap 67 -> 76 (9) then up ; LT 71 before the cadence not to C
            "bass": [{"slot": 0, "pitch": 36, "dur16": 16, "section": 0}, {"slot": 16, "pitch": 43, "dur16": 16, "section": 0}, {"slot": 32, "pitch": 36, "dur16": 16, "section": 0}, {"slot": 48, "pitch": 43, "dur16": 16, "section": 0}],
            "melody": [mel(0, 72, 16), mel(16, 79, 8), mel(24, 76, 8, "chord_tone"), mel(32, 67, 8), mel(40, 71, 8, "chord_tone"), mel(48, 74, 16, "cadence")],
            "keys": [], "drums": []}
    viols = R.find_violations(song)
    rules = sorted(v["rule"] for v in viols)
    val_par = V.parallel_perfect_intervals(song)
    assert rules.count("parallel_octave") == val_par["breakdown"]["bass_melody_octaves"] == 1, (rules, val_par)
    assert rules.count("leap_unresolved") == V.melody_checks(song)["melodic_leaps_unresolved"] == 1, rules
    assert rules.count("leading_tone_unresolved") == V.leading_tone_unresolved_at_cadence(song)["melody"] == 1, rules
    assert all("slot" in v and "key" in v for v in viols) and viols == sorted(viols, key=lambda v: (v["slot"], v["rule"]))
    par = next(v for v in viols if v["rule"] == "parallel_octave")
    assert [n["slot"] for n in par["bass"]] == [0, 16] and [n["slot"] for n in par["melody"]] == [0, 16]
    print(f"test_01 PASS: find_violations = validators' counts with locations on a hand-made song ({rules})")


def test_02_parallel_branches_free_bass_then_melody_nct_then_skeleton() -> None:
    seen = {}
    for seed in range(6):
        case = _Case(seed)
        hit = _inject_parallel(case, want_free_second=True)
        if hit and "a_bass_free" not in seen:
            lab, slot = hit
            assert _par_keys(case), "injection must create a bass-melody parallel"
            rep = case.repair()
            e = rep["repairs"][0]
            assert e["branch"] == "a_bass_free" and e["stem"] == "bass" and e["label"] == lab and e["slot"] % (8 * SLOTS) == slot % (8 * SLOTS), e
            assert e["cls"] in ("root", "fifth", "octave", "third", "approach", "repeat") and e["before"] != e["after"] and "draw_tag" in e
            assert not _par_keys(case) and not rep["forced"], rep
            seen["a_bass_free"] = (seed, lab, slot)
        case = _Case(seed)
        hit = _inject_parallel(case, want_free_second=False, want_skeleton=False)
        if hit and "b_melody_nct" not in seen:
            assert _par_keys(case)
            rep = case.repair()
            assert rep["repairs"] and rep["repairs"][0]["branch"] in ("b_melody_nct", "a_bass_free") and not _par_keys(case) and not rep["forced"], rep
            if rep["repairs"][0]["branch"] == "b_melody_nct":
                assert rep["repairs"][0]["stem"] == "melody" and rep["repairs"][0]["role"] in ("chord_tone", "neighbour", "passing")
                seen["b_melody_nct"] = (seed,) + hit
        case = _Case(seed)
        hit = _inject_parallel(case, want_free_second=False, want_skeleton=True)
        if hit and "c_melody_skeleton" not in seen:
            assert _par_keys(case)
            rep = case.repair()
            assert rep["repairs"] and not _par_keys(case) and not rep["forced"], rep
            e = next((x for x in rep["repairs"] if x["branch"] == "c_melody_skeleton"), None)
            if e:
                assert e["phrase_rerealized"] and isinstance(e["skeleton_index"], int) and e["stem"] == "melody"
                seen["c_melody_skeleton"] = (seed,) + hit
        if len(seen) == 3:
            break
    assert set(seen) == {"a_bass_free", "b_melody_nct", "c_melody_skeleton"}, seen
    print(f"test_02 PASS: injected bass-melody parallels repaired by every branch: {seen}")


def _inject_leap(case: _Case, following_nct: bool):
    """Raise a non-skeleton melody note b by > MAX_LEAP above its predecessor a so that the following note c (NCT or skeleton) is not a step
    back; returns (label, slot of b) or None."""
    for lab in sorted(case.heard):
        notes = case.mel(lab)
        for i in range(1, len(notes) - 1):
            a, b, c = notes[i - 1], notes[i], notes[i + 1]
            if b.get("role") in R.SKELETON_ROLES or (c.get("role") in R.SKELETON_ROLES) == following_nct or a["phrase"] != b["phrase"] != c["phrase"]:
                continue
            lo, hi = case.window(lab, b)
            for p in range(a["pitch"] + MAX_LEAP + 1, hi + 1):
                if lo <= p <= hi and p != c["pitch"] and not (1 <= p - c["pitch"] <= 2):  # c is then not a step down from p
                    _set_melody(case, lab, b, p, "chord_tone" if p % 12 in (state_pcs(b["chord"], TONIC) or []) else "passing")
                    return lab, b["slot"]
    return None


def test_03_leap_branches_following_step_back_then_leap_note() -> None:
    seen = {}
    for seed in range(6):
        for following_nct in (True, False):
            case = _Case(seed)
            hit = _inject_leap(case, following_nct)
            if not hit:
                continue
            assert any(v["rule"] == "leap_unresolved" for v in case.violations()), "injection must create an unresolved leap"
            rep = case.repair()
            assert rep["repairs"] and not rep["forced"] and not any(v["rule"] == "leap_unresolved" for v in case.violations()), rep
            e = rep["repairs"][0]
            assert e["rule"] == "leap_unresolved" and e["branch"].startswith("leap_")
            seen.setdefault(e["branch"], (seed,) + hit)
    assert "leap_following_nct_step_back" in seen and ("leap_note_nct" in seen or "leap_note_skeleton" in seen or "leap_following_skeleton" in seen), seen
    print(f"test_03 PASS: injected unresolved leaps repaired: {seen}")


def _inject_leading_tone(case: _Case, want_tonic_in_final: bool, before_skeleton: bool):
    for lab in sorted(case.heard):
        L = case.labels[lab]
        for k, (ph, hp) in enumerate(zip(case.plan["label_plans"][lab]["phrases"], L["harmony"]["phrases"])):
            sl = hp["slots"]
            if len(sl) < 2:
                continue
            final_pcs = state_pcs(sl[-1]["state"], TONIC) or []
            if (TONIC_PC in final_pcs) != want_tonic_in_final:
                continue
            pen, cad = sl[-2]["bar"] * SLOTS + sl[-2]["beat"] * 4, sl[-1]["bar"] * SLOTS + sl[-1]["beat"] * 4
            notes = case.mel(lab)
            before = [n for n in notes if pen <= n["slot"] < cad and n["phrase"] == k]
            at = [n for n in notes if n["slot"] == cad and n["phrase"] == k]
            if not before or not at or (before[-1].get("role") in R.SKELETON_ROLES) != before_skeleton:
                continue
            lo, hi = case.window(lab, before[-1])
            lt = next((p for p in range(hi, lo - 1, -1) if p % 12 == LT), None)
            if lt is None:
                continue
            if want_tonic_in_final and at[0]["pitch"] % 12 == TONIC_PC:  # move the cadence note off the tonic (another chord tone in the window)
                lo2, hi2 = case.window(lab, at[0])
                alt = next((p for p in range(lo2, hi2 + 1) if p % 12 in final_pcs and p % 12 != TONIC_PC), None)
                if alt is None:
                    continue
                _set_melody(case, lab, at[0], alt)
            if not want_tonic_in_final and at[0]["pitch"] % 12 == TONIC_PC:
                continue
            _set_melody(case, lab, before[-1], lt)
            return lab, cad
    return None


def test_04_leading_tone_branches_cadence_to_tonic_then_note_before() -> None:
    seen = {}
    for seed in range(8):
        for want_tonic, before_sk in ((True, False), (True, True), (False, False), (False, True)):
            case = _Case(seed)
            hit = _inject_leading_tone(case, want_tonic, before_sk)
            if not hit:
                continue
            assert any(v["rule"] == "leading_tone_unresolved" for v in case.violations()), (seed, want_tonic, before_sk)
            rep = case.repair()
            assert not any(v["rule"] == "leading_tone_unresolved" for v in case.violations()) and not rep["forced"], (seed, rep["forced"], rep["remaining"])
            e = next(x for x in rep["repairs"] if x["rule"] == "leading_tone_unresolved")
            assert e["branch"].startswith("lt_")
            seen.setdefault(e["branch"], (seed,) + hit)
    assert "lt_cadence_note_to_tonic" in seen and ("lt_before_nct" in seen or "lt_before_skeleton" in seen), seen
    print(f"test_04 PASS: injected unresolved leading tones repaired: {seen}")


def test_05_skeleton_rerealisation_keeps_earlier_nct_repairs_and_metadata() -> None:
    case = _Case(3)
    lab = sorted(case.heard)[0]
    content = case.labels[lab]
    k = next(i for i, ph in enumerate(content["melody"]["phrases"]) if ph.get("skeleton") and any(n["phrase"] == i and n["role"] not in R.SKELETON_ROLES for n in content["melody"]["notes"]))
    nct = next(n for n in sorted(content["melody"]["notes"], key=lambda n: n["slot"]) if n["phrase"] == k and n["role"] not in R.SKELETON_ROLES)
    nct["pitch"], nct["repaired"] = nct["pitch"] + 1, "leap_unresolved"  # pretend an earlier NCT repair
    marked = (nct["slot"], nct["pitch"])
    before_onsets = sorted(n["slot"] for n in content["melody"]["notes"] if n["phrase"] == k)
    R.rerealize_phrase(content, k, list(content["melody"]["phrases"][k]["skeleton"]["pitches"]), TONIC, MODE)
    after = {n["slot"]: n for n in content["melody"]["notes"] if n["phrase"] == k}
    assert sorted(after) == before_onsets, "re-realisation keeps the onsets"
    assert after[marked[0]]["pitch"] == marked[1] and after[marked[0]]["repaired"] == "leap_unresolved", "earlier NCT repair survives"
    assert sum(1 for n in after.values() if n["position"] == "first") == 1 and sum(1 for n in after.values() if n["position"] == "last") == 1
    print("test_05 PASS: rerealize_phrase keeps onsets, earlier NCT repairs and refreshes positions")


def test_06_repairs_deterministic_and_logged_in_plan() -> None:
    a = C.compose_song(FX, "gen_v6_song_1", "fixture_a", 3, 100.0, 32)
    b = C.compose_song(FX, "gen_v6_song_1", "fixture_a", 3, 100.0, 32)
    assert canonical_json(a["plan"]["repairs"]) == canonical_json(b["plan"]["repairs"])
    assert canonical_json({k: a["song"][k] for k in ("melody", "bass", "keys")}) == canonical_json({k: b["song"][k] for k in ("melody", "bass", "keys")})
    rep = a["plan"]["repairs"]
    assert set(rep) >= {"schema_version", "passes", "n_repairs", "by_rule", "repairs", "n_forced", "forced", "remaining"} and rep["passes"] == ["labels"]
    for e in rep["repairs"]:
        assert {"rule", "branch", "stem", "section", "label", "bar", "slot", "before", "after", "pass"} <= set(e) and e["before"] != e["after"]
    assert rep["n_repairs"] == len(rep["repairs"]) == sum(rep["by_rule"].values())
    off = C.compose_song(FX, "gen_v6_song_1", "fixture_a", 3, 100.0, 32, repair_pass=False)
    assert off["plan"]["repairs"].get("skipped") is True and off["plan"]["repairs"]["n_repairs"] == 0
    h = C.compose_song(FX, "gen_v6_song_1", "fixture_a", 3, 100.0, 32, hz={"mt": None})
    assert h["plan"]["repairs"]["passes"] == ["labels", "sections"]
    assert all(e["stem"] == "bass" or e.get("role") is not None for e in h["plan"]["repairs"]["repairs"] if e["pass"] == "sections"), "recurrence pass touches NCTs / free bass only"
    assert h["validators"]["metrics"]["section_repeat_skeleton_integrity"] is True
    print(f"test_06 PASS: repairs byte-deterministic; plan.json['repairs'] schema ({rep['n_repairs']} label repairs; humanize passes {h['plan']['repairs']['passes']})")


def test_07_sweep_seeds_0_to_3_zero_unforced_violations() -> None:
    cases, summary = SW.sweep(list(range(4)), 32, list(SW.DEFAULT_BPM), [False, True], before=True, log=lambda *a: None)
    assert summary["n_cases"] == 24
    assert summary["n_cases_failing_without_forced"] == 0, summary["cases_failing_without_forced"]
    assert summary["n_forced"] == 0, summary["forced"]
    assert summary["n_realized_keys_violations"] == 0
    for r in ("parallel_fifths", "parallel_octaves", "unresolved_sevenths", "leading_tone_unresolved_at_cadence", "melodic_leaps_unresolved", "voice_crossing"):
        assert summary["per_rule"][r]["n_cases_violating"] == 0, (r, summary["per_rule"][r])
    assert summary["per_rule"]["parallel_octaves"]["before"] is not None and summary["n_repairs_total"] > 0
    md = SW.markdown(summary, {"stamp": "test", "seeds": list(range(4)), "n_bars": 32, "bpm": "100,120,152", "modes": "plain,humanize", "before": True})
    assert "| rule | cap | cases violating before | after |" in md and "none" in md
    print(f"test_07 PASS: 24 cases all caps pass (before: {summary['n_cases_all_caps_pass_before']}/24); repairs {summary['repairs_by_rule']}; 0 forced")


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
