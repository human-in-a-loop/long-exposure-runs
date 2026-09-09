#!/usr/bin/python3
"""c86 landing tests — F2 bass + melody + dynamics (prereg gate, sibling serializer byte-equality, velocity mapping, flag-off
regression record, iteration-3 velocities / replay proofs / enum / stall, live uniform-vs-F2 RMS-variance render, --cycle required,
discipline, Route-1 profile diagnostics + anchor preservation, ledger adoption).

created: 2026-09-10T00:05:00Z
cycle: 86
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle86-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_c86_landing.py   (F4 close tests live in tests/test_c86_f4_close.py; the bass/VOMM
model tests in tests/test_c86_f2_models.py)
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
FOCUS = ["252eb21ce7df7328", "31a164f845f8e27e", "51e433ade2a845e1", "88d247468cb6d49f", "cdd2717e52820ff6"]
NEW_SCRIPTS = ["scripts/v5/velocity_v5.py", "scripts/v5/midi_from_json_events_v5.py", "scripts/v5/generate_v5.py", "scripts/v5/f2_route_gate_c86.py",
               "data/v5/rules/plot_velocity_profiles_c86.py", "data/v5/gen/iteration_03/plot_iter03_velocity_c86.py", "data/v5/corpus/plot_tempo_f4_c85.py"]
IT2, IT3 = _ROOT / "data/v5/gen/iteration_02", _ROOT / "data/v5/gen/iteration_03"
PREREG = _ROOT / "data/v5/gen/f2_prereg_c86.json"
IT2_WAV = {"gen_v5_song_1_donor_31a164f845f8e27e": "240b893ab0afde36", "gen_v5_song_2_donor_252eb21ce7df7328": "9b1812c09d25",
           "gen_v5_song_3_donor_51e433ade2a845e1": "ac01eb926aae", "gen_v5_song_4_donor_88d247468cb6d49f": "940227fb120e",
           "gen_v5_song_5_donor_cdd2717e52820ff6": "330916d5ecab"}


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _j(p):
    return json.loads(Path(p).read_text())


def test_01_prereg_before_every_f2_output_and_route_gate() -> None:
    outs = [_ROOT / "data/v5/rules/velocity_profiles_v5.json", _ROOT / "data/v5/rules/bass_pitch_v5.json", _ROOT / "data/v5/rules/melody_vomm_v5.json"]
    outs += [_ROOT / f"data/v5/corpus/{s}/velocity_v5/velocities.json" for s in FOCUS]
    outs += sorted(IT3.glob("*/ab_mix.wav")) + sorted(IT3.glob("*/ab_mix.manifest.json")) + [IT3 / "iteration_rollup.json"]
    assert len(outs) == 19, len(outs)
    for o in outs:
        assert PREREG.stat().st_mtime < o.stat().st_mtime, o
    prof = _j("data/v5/rules/velocity_profiles_v5.json")
    assert prof["prereg_sha256"] == _sha(PREREG)
    gate = _j("data/v5/gen/f2_route_gate_c86.json")
    assert gate["route"] == "ROUTE_1_STEM_AUDIO" and gate["gate_df_le_85"] and gate["gate_htdemucs_importable"] and gate["gate_separation_le_300s"]
    assert gate["guidance"]["sha16"] == "8677bb0cd3f240a0" and _sha("docs/guidance/guidance_2026-09-09_F2_velocity_decision.txt").startswith("8677bb0cd3f240a0")
    print(f"test_01 PASS: prereg predates 19 F2 outputs; route gate ROUTE_1 (df {gate['df_used_pct_driver_semantics']} %, sep {gate['separation_wall_s']} s)")


def test_02_sibling_serializer_byte_equal_without_velocities_and_carries_them() -> None:
    from scripts.v3_spine.midi_from_json_events import serialize as c4
    from scripts.v5.midi_from_json_events_v5 import serialize as v5
    import mido
    n = eq = 0
    with tempfile.TemporaryDirectory() as td:
        for j in sorted(IT2.glob("*/generated_json/*.json")):
            bpm = float(_j(j.parent.parent / "ab_mix.manifest.json")["tempo_bpm"])
            a, b = Path(td) / "a.mid", Path(td) / "b.mid"
            c4(str(j), str(a), bpm, (4, 4))
            v5(str(j), str(b), bpm, (4, 4))
            n += 1
            eq += _sha(a) == _sha(b)
        assert n == 56 and eq == n, (n, eq)
        ev = [{"index": 0, "instrument": "electric_bass", "pitch": 40, "start_time": 0.0, "type": "start", "velocity": 37},
              {"start_event_index": 0, "end_time": 0.5, "type": "end"},
              {"index": 1, "instrument": "electric_bass", "pitch": 45, "start_time": 0.5, "type": "start", "velocity": 999},
              {"start_event_index": 1, "end_time": 1.0, "type": "end"},
              {"index": 2, "instrument": "electric_bass", "pitch": 47, "start_time": 1.0, "type": "start"}]
        vj = Path(td) / "v.json"
        vj.write_text(json.dumps(ev))
        v5(str(vj), str(Path(td) / "v.mid"), 120.0, (4, 4))
        ons = [m.velocity for t in mido.MidiFile(str(Path(td) / "v.mid")).tracks for m in t if m.type == "note_on"]
        assert ons == [37, 127, 100], ons  # explicit, clipped to 127, default 100
    print(f"test_02 PASS: sibling serializer byte-equal {eq}/{n} on iteration-2 JSON; velocity field honoured + clipped + defaulted")


def test_03_velocity_mapping_p5_p95_and_degenerate_guard() -> None:
    from scripts.v5.velocity_v5 import midrank_velocities, sample_velocity, ladder
    vals = [float(i) for i in range(100)]  # 100 distinct RMS values
    v, st = midrank_velocities(vals)
    assert st["degenerate"] is False and st["spread_db"] == 90.0
    assert min(v) == 1 + 0 or min(v) >= 1 and max(v) <= 127
    # rank fraction 0.05 -> 40, 0.95 -> 110 (midrank of the 5th value = 4.5/100 = 0.045 -> 39.6 -> 40)
    assert v[4] in (39, 40) and v[94] in (110, 111), (v[4], v[94])
    assert v[0] < v[4] < v[50] < v[94] < v[99]
    same, st2 = midrank_velocities([-20.0] * 8)
    assert st2["degenerate"] is True and same == [80] * 8
    tie, _ = midrank_velocities([1.0, 2.0, 2.0, 3.0])
    assert tie[1] == tie[2], tie
    lad = ladder([60, 70, 80, 90, 100])
    assert sample_velocity(lad, 0.0) == 60 and sample_velocity(lad, 1.0) == 100 and 60 <= sample_velocity(lad, 0.5) <= 100
    assert sample_velocity({"quantiles": None}, 0.3) == 100
    print("test_03 PASS: midrank mapping p5->40 / p95->110, ties share a velocity, degenerate guard -> 80, ladder sampler bounds")


def test_04_flag_off_regression_record_matches_current_generator_image() -> None:
    bd = _j("data/v5/gen/byte_determinism_c86.json")["entries"]["iteration_02_flag_off_replay"]
    assert bd["all_equal"] is True and bd["generate_v5_sha256"] == _sha("scripts/v5/generate_v5.py"), "flag-off record must be for the CURRENT generator image"
    for k, pre in IT2_WAV.items():
        assert bd["per_song"][k]["c85_sha256"].startswith(pre) and bd["per_song"][k]["flag_off_sha256"] == bd["per_song"][k]["c85_sha256"]
        assert _sha(IT2 / k / "ab_mix.wav").startswith(pre), k  # iteration-2 WAVs untouched
    it3 = _j("data/v5/gen/byte_determinism_c86.json")["entries"]["iteration_03_renders"]
    assert it3["generate_v5_sha256"] == _sha("scripts/v5/generate_v5.py") and it3["all_equal"] is True
    print("test_04 PASS: flag-off replay reproduces the 5 iteration-2 SHAs under the current generator image; iteration-3 x2 record pinned to the same image")


def test_05_iteration_03_velocities_replay_enum_stall() -> None:
    import mido
    roll = _j(IT3 / "iteration_rollup.json")
    assert roll["seed"] == 2 and roll["cycle"] == 86 and roll["f2"]["velocity_mode"] == "f2" and roll["f2"]["route"] == "ROUTE_1_STEM_AUDIO"
    assert roll["f2"]["f2_enum"] in ("F2_LANDS", "F2_PARTIAL", "F2_FAILS")
    assert roll["rules_sha256"]["harmony_chain"].startswith("a984ee17") and roll["rules_sha256"]["groove_model"].startswith("faa0e76e")  # n=21 consumed (n=23 from iteration 4)
    n = 0
    for s in roll["songs"]:
        d = IT3 / f"{s['generated_song_id']}_donor_{s['donor']}"
        man = _j(d / "ab_mix.manifest.json")
        assert _j(d / "ab_mix.replay_proof.json")["verdict"] == "REPLAY_PROOF_HOLDS"
        assert man["f2"]["velocities_present_all_stems_with_notes"] is True
        for stem, st in man["f2"]["per_stem"].items():
            if not st["n_notes"]:
                continue
            ons = [m.velocity for t in mido.MidiFile(str(d / "generated_midi" / f"{stem}.mid")).tracks for m in t if m.type == "note_on" and m.velocity > 0]
            assert len(ons) == st["n_notes"] and len(set(ons)) == st["n_distinct_velocities"], (stem, len(ons), st)
            assert len(set(ons)) >= 2, f"{d.name}/{stem} velocities uniform"
        assert man["form_plan_sha256"].startswith("d6c14f9a") and _sha(d / "ab_mix.wav") == man["ab_mix_sha256"]
        n += 1
    assert n == 5
    sc = _j("data/v5/gen/stall_counter.json")
    assert sc["iterations"] == 3 and sc["budget"] == 12
    h = sc["history"][-1]
    assert h["iteration"] == 3 and h["seed"] == 2 and h["feature"].startswith("F2") and h["f2"]["route"] == "ROUTE_1_STEM_AUDIO"
    print(f"test_05 PASS: iteration 3 = 5/5 REPLAY_PROOF_HOLDS, velocities non-uniform on every stem with notes, enum {roll['f2']['f2_enum']}, stall 3/12")


def test_06_live_uniform_vs_f2_render_rms_variance() -> None:
    from scripts.v5.generate_v5 import frame_rms_variance
    import mido
    base = ["/usr/bin/python3", "scripts/v5/generate_v5.py", "--iteration", "3", "--seed", "2", "--form-plan", "data/v5/rules/form_plan_v5.json",
            "--cycle", "86", "--songs", "1", "--no-stall-update", "--keep-per-track", "--f2"]
    with tempfile.TemporaryDirectory(prefix="c86_t06_f2_") as ta, tempfile.TemporaryDirectory(prefix="c86_t06_uni_") as tb:
        subprocess.run(base + ["--velocity-mode", "f2", "--out", ta], check=True, capture_output=True, text=True)
        subprocess.run(base + ["--velocity-mode", "uniform", "--out", tb], check=True, capture_output=True, text=True)
        da, db = next(Path(ta).glob("gen_v5_song_1_*")), next(Path(tb).glob("gen_v5_song_1_*"))
        ma, mb = _j(da / "ab_mix.manifest.json"), _j(db / "ab_mix.manifest.json")
        assert ma["ab_mix_sha256"] == _sha(IT3 / da.name / "ab_mix.wav"), "live F2 render must reproduce the iteration-3 song 1 WAV"
        ratios = {}
        for stem, st in ma["f2"]["per_stem"].items():
            if not st["n_notes"]:
                continue
            va = [m.velocity for t in mido.MidiFile(str(da / "generated_midi" / f"{stem}.mid")).tracks for m in t if m.type == "note_on"]
            vb = [m.velocity for t in mido.MidiFile(str(db / "generated_midi" / f"{stem}.mid")).tracks for m in t if m.type == "note_on"]
            assert len(set(va)) >= 2 and set(vb) == {100}, (stem, set(vb))
            assert mb["f2"]["per_stem"][stem]["pitch_min"] == st["pitch_min"] and mb["f2"]["per_stem"][stem]["n_notes"] == st["n_notes"]  # same notes
            ra, rb = frame_rms_variance(da / "per_track" / f"{stem}.wav"), frame_rms_variance(db / "per_track" / f"{stem}.wav")
            ratios[stem] = round(ra["variance_db2"] / rb["variance_db2"], 4)
        rec = ma["f2"]["rms_variance_test"]["per_stem"] if "rms_variance_test" in ma["f2"] else _j(IT3 / da.name / "ab_mix.manifest.json")["f2"]["rms_variance_test"]["per_stem"]
        for stem, r in ratios.items():
            assert abs(rec[stem]["ratio_f2_over_uniform"] - r) < 1e-3, (stem, r, rec[stem])
        passing = {k: v >= 1.5 for k, v in ratios.items()}
    assert ratios and all(v > 1.0 for v in ratios.values()), ratios  # the null is velocity=100 everywhere: the F2 render must be strictly more dynamic
    print(f"test_06 PASS: live song-1 uniform-vs-F2 render: ratios {ratios} (>=1.5: {passing}); uniform MIDI all 100, F2 MIDI non-uniform, same notes")


def test_07_cycle_required_on_score_and_deliver() -> None:
    for script in ("scripts/v5/score_gen_batch_v5.py", "scripts/v5/deliver_v5_listening.py"):
        r = subprocess.run(["/usr/bin/python3", script, "--iteration", "3"] if "deliver" in script else ["/usr/bin/python3", script, "--renders-glob", "x"],
                           capture_output=True, text=True)
        assert r.returncode == 2 and "--cycle" in r.stderr and "required" in r.stderr, (script, r.returncode, r.stderr[-300:])
    r = subprocess.run(["/usr/bin/python3", "data/v5/corpus/plot_tempo_f4_c85.py"], capture_output=True, text=True)
    assert r.returncode == 2 and "--out" in r.stderr
    print("test_07 PASS: --cycle required on score/deliver; --out required on the c85 F4 plot")


def test_08_discipline_ast_guards_and_created_stamps() -> None:
    bad = re.compile(r"\b(random\.|np\.random|numpy\.random|sidecar_nonfactor|get_state\(|save_state\(|save_preset\(|load_state\(|set_state\()")
    for s in NEW_SCRIPTS:
        src = Path(s).read_text()
        ast.parse(src)
        assert not bad.search(src), s
        assert '"/usr/bin/python3"' in src or "'/usr/bin/python3'" in src, s
        m = re.search(r"created: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z", src)
        if m and s != "scripts/v5/generate_v5.py":
            import calendar
            import time as _t
            created = calendar.timegm(_t.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S"))
            assert created <= Path(s).stat().st_mtime, s
    for m in ("data/v5/rules/velocity_profiles_v5.json", "data/v5/gen/iteration_03/iteration_rollup.json", "data/v5/rules/bass_pitch_v5.json"):
        assert _j(m)["env_pin_sha256"] == ENV_PIN, m
    print(f"test_08 PASS: {len(NEW_SCRIPTS)} scripts clean (no PRNG / sidecar / VST3 state), guards present, env_pin pinned")


def test_09_route1_profiles_diagnostics_and_reindexed_anchors_untouched() -> None:
    prof = _j("data/v5/rules/velocity_profiles_v5.json")
    assert prof["route"] == "ROUTE_1_STEM_AUDIO" and set(prof["R1"]["drums_bass_pass_ge_4_of_5"]) == {"drums", "bass"}
    for k in ("backbeat_ge_plus_10", "hat_odd_lower_than_even", "bass_coincident_gt_non", "structureless_std_lt_5"):
        assert isinstance(prof["R2"][k], bool), k
    for cls in ("kick", "snare", "hat"):
        assert len(prof["profiles"]["drums"][cls]) == 16
    for s in FOCUS:
        v = _j(f"data/v5/corpus/{s}/velocity_v5/velocities.json")
        side = _j(f"data/v5/corpus/{s}/canonical_v5_reindexed_sha256.json")
        for stem in ("drums", "bass", "guitar", "other", "piano", "vocals"):
            assert _sha(f"data/v5/corpus/{s}/canonical_v5_reindexed/{stem}.mid") == side["midi_sha256"][stem], (s, stem)  # anchors untouched
            n_starts = v["sibling_midi"]["sha256"][stem]["n_starts"]
            assert v["sibling_midi"]["sha256"][stem]["n_velocity_assigned"] == n_starts == len(v["velocities"][stem]), (s, stem)
            assert _sha(f"data/v5/corpus/{s}/canonical_v5_velocity/{stem}.mid") == v["sibling_midi"]["sha256"][stem]["mid"]
            assert v["stem_stats"][stem]["degenerate"] in (True, False)
        sep = v["separation"]
        assert isinstance(sep["cross_cycle_x2_holds"], bool)
        if s == "252eb21ce7df7328":
            assert sep["in_cycle_x2_holds"] is True, sep.get("in_cycle_run2")
        assert v["grid_bpm"] == (122.197271 if s == "88d247468cb6d49f" else 120.272335 if s == "cdd2717e52820ff6" else v["grid_bpm"])
        assert v["stems_deleted_after_measuring"] is True
    print(f"test_09 PASS: R1 {prof['R1']['songs_passing_per_stem']} R2 {prof['R2']['backbeat_minus_odd']}/{prof['R2']['drums_slot_profile_std']}; "
          "5 songs: reindexed anchors untouched, sibling velocity MIDI counts match, WIG in-cycle x2 holds")


def test_10_route_decision_and_guidance_in_ledger() -> None:
    rows = [json.loads(l) for l in Path("promise_ledger.jsonl").read_text().splitlines() if l.strip()]
    ids = {r["milestone_id"]: r for r in rows}
    r = ids["M-V5-GEN-1/F2-velocity-route-decided-c86"]
    assert r["agent"] == "worker" and "ROUTE_1" in r["narrative"] and "8677bb0cd3f240a0" in r["narrative"] and "df" in r["narrative"]
    a = ids["_plan/adopt-operator-guidance-2026-09-09-F2-and-F4-addendum"]
    assert a["agent"] == "worker" and "8677bb0cd3f240a0" in a["narrative"] and "122.197271" in a["narrative"] and "120.272335" in a["narrative"]
    for mid in ("M-V5-GEN-1/F2-bass-melody-dynamics", "M-V5-GEN-1/F4-tempo-fix", "M-V5-CORPUS-1/tempo-f4-operator-resolved-c86", "M-V5-RULES-1/harmony-n23-c86"):
        assert mid in ids and ids[mid]["agent"] == "worker" and isinstance(ids[mid]["supersedes_path"], (str, type(None))), mid
    assert ids["M-V5-GEN-1/F4-tempo-fix"]["status"] == "validated"
    print("test_10 PASS: route decision (one ledger line) + guidance adoption + F2/F4 events present with agent=worker and str|null supersedes_path")


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"{name} FAIL: {type(e).__name__}: {e}")
    print(f"{10 - fails}/10 PASS")
    sys.exit(1 if fails else 0)
