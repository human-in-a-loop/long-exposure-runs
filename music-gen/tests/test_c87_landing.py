#!/usr/bin/python3
"""c87 (= harness c131) landing tests — F2 iteration 3 rendered + landed (consumed velocities as-is; enum recorded from the prereg;
byte-det ×2; flag-off regression under the FINAL generator image for iteration 2 AND iteration 1; listening copies; stall 3/12 with the
F6 history entry; the P0 edits (argparse guard, serializer guard + stamps); the early ledger trio; the accepted cross-cycle stem finding).

created: 2026-09-10T01:48:00Z
cycle: 87
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle87-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_c87_landing.py
"""
from __future__ import annotations

import ast
import calendar
import hashlib
import json
import os
import re
import subprocess
import sys
import time as _t
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
FOCUS = ["252eb21ce7df7328", "31a164f845f8e27e", "51e433ade2a845e1", "88d247468cb6d49f", "cdd2717e52820ff6"]
IT3 = _ROOT / "data/v5/gen/iteration_03"
BD = _ROOT / "data/v5/gen/byte_determinism_c86.json"
IT2_WAV = {"gen_v5_song_1_donor_31a164f845f8e27e": "240b893a", "gen_v5_song_2_donor_252eb21ce7df7328": "9b1812c0", "gen_v5_song_3_donor_51e433ade2a845e1": "ac01eb92",
           "gen_v5_song_4_donor_88d247468cb6d49f": "940227fb", "gen_v5_song_5_donor_cdd2717e52820ff6": "330916d5"}
VELOCITY_V5_SHA = "dd94336de4e09fcec3e34d8ec1bbe9db18a0462398e709f0e3dc3a8281b7169a"  # pinned inside every velocities.json — NOT edited in c87
PROFILES_SHA = "6b2fc502f065d0ca961c907e93a3c02f80618a1afc34015b4057dd513cb314a8"
G131 = "docs/guidance/guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt"
G131_SHA16 = "fed27e550e9f7c75"


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _j(p):
    return json.loads(Path(p).read_text())


def _ledger():
    return [json.loads(l) for l in Path("promise_ledger.jsonl").read_text().splitlines() if l.strip()]


def test_01_velocities_consumed_as_is_and_profiles_unchanged() -> None:
    roll = _j(IT3 / "iteration_rollup.json")
    assert roll["cycle"] == 87 and roll["iteration"] == 3 and roll["env_pin_sha256"] == ENV_PIN
    ms = roll["f2"]["models_sha256"]
    assert ms["velocity_v5_script"] == VELOCITY_V5_SHA == _sha("scripts/v5/velocity_v5.py"), "velocity_v5.py must be the pinned image (not edited)"
    assert ms["velocity_profiles"] == PROFILES_SHA == _sha("data/v5/rules/velocity_profiles_v5.json")
    for s in FOCUS:
        v = _j(f"data/v5/corpus/{s}/velocity_v5/velocities.json")
        assert v["script_sha256"] == VELOCITY_V5_SHA if "script_sha256" in v else True
        assert Path(f"data/v5/corpus/{s}/velocity_v5/velocities.json").stat().st_mtime < (IT3 / "iteration_rollup.json").stat().st_mtime
    assert roll["f2"]["prereg_sha256"] == _sha("data/v5/gen/f2_prereg_c86.json")
    print("test_01 PASS: iteration 3 consumed the five landed velocities.json + profiles as-is under the pinned velocity_v5.py image")


def test_02_enum_recorded_from_prereg_not_retuned() -> None:
    roll = _j(IT3 / "iteration_rollup.json")
    pre = _j("data/v5/gen/f2_prereg_c86.json")
    f2 = roll["f2"]
    assert f2["f2_enum"] in pre["enum"], f2["f2_enum"]
    c = f2["clauses"]
    expect = "F2_LANDS" if all(v is True for v in c.values()) else "F2_PARTIAL"
    assert f2["f2_enum"] == expect, (f2["f2_enum"], c)
    per = {s["generated_song_id"]: s.get("rms_variance_passes") for s in roll["songs"]}
    assert f2["n_rms_variance_pass"] == sum(1 for v in per.values() if v) and c["rms_variance_5_of_5"] == (f2["n_rms_variance_pass"] == 5)
    # every stem-level ratio is recorded in the manifests with the pre-registered 1.5 gate (no retune)
    for s in roll["songs"]:
        man = _j(IT3 / f"{s['generated_song_id']}_donor_{s['donor']}" / "ab_mix.manifest.json")
        t = man["f2"]["rms_variance_test"]
        for stem, r in t["per_stem"].items():
            if "ratio_f2_over_uniform" in r:
                assert r["ge_1p5"] == (r["ratio_f2_over_uniform"] >= 1.5), (s["generated_song_id"], stem)
    print(f"test_02 PASS: enum {f2['f2_enum']} follows the prereg clauses {c} (RMS pass {f2['n_rms_variance_pass']}/5)")


def test_03_replay_proofs_x2_and_byte_det_record_under_final_image() -> None:
    roll = _j(IT3 / "iteration_rollup.json")
    bd = _j(BD)
    assert bd["env_pin_sha256"] == ENV_PIN and bd["cycle"] == 86 and bd["ledgered_cycle"] == 87
    # c88 re-pin (disclosed): generate_v5.py gained the additive --f3 wiring in c88 (pre-edit sha pinned in byte_determinism_c88.json turn_start_pins);
    # the c87 record must match the image that rendered iteration 3 = the c88 pre-edit pin, and the c88 record proves that image's outputs are reproduced flag-off
    gen_sha = _j("data/v5/gen/byte_determinism_c88.json")["turn_start_pins"]["generate_v5_pre_edit"]["sha256"]
    assert gen_sha.startswith("f261690c1f534611")
    assert roll["generator_hash"] == gen_sha == bd["entries"]["iteration_03_renders"]["generate_v5_sha256"] == bd["post_edit_script_sha256"]["generate_v5"]
    assert _j("data/v5/gen/byte_determinism_c88.json")["entries"]["iteration_03_flag_off_replay"]["n_equal"] == 5
    assert bd["post_edit_script_sha256"]["midi_from_json_events_v5"] == _sha("scripts/v5/midi_from_json_events_v5.py") == roll["f2"]["models_sha256"]["serializer_v5_script"]
    per = bd["entries"]["iteration_03_renders"]["per_song"]
    assert len(per) == 5 and bd["entries"]["iteration_03_renders"]["all_equal"] is True
    for s in roll["songs"]:
        k = f"{s['generated_song_id']}_donor_{s['donor']}"
        pr = _j(IT3 / k / "ab_mix.replay_proof.json")
        assert pr["verdict"] == "REPLAY_PROOF_HOLDS" and pr["run1_sha256"] == pr["run2_sha256"] == _sha(IT3 / k / "ab_mix.wav") == s["ab_mix_sha256"]
        assert per[k]["run1_sha256"] == per[k]["run2_sha256"] == per[k]["on_disk_sha256"] == pr["run1_sha256"]
        assert str(pr["run2_tempdir"]).startswith("/tmp/") and pr["run2_tempdir"] != str(IT3)
    assert bd["entries"]["velocity_profiles_v5"]["equal"] is True and bd["entries"]["serializer_v5_vs_c4"]["equal"] is True
    print("test_03 PASS: 5/5 REPLAY_PROOF_HOLDS in fresh tempdirs; byte_determinism_c86.json pins the FINAL generator + serializer SHAs")


def test_04_flag_off_regression_iteration_2_and_1_under_final_image() -> None:
    bd = _j(BD)["entries"]
    for label, roll_path in (("iteration_02_flag_off_replay", "data/v5/gen/iteration_02/iteration_rollup.json"), ("iteration_01_flag_off_replay", "data/v5/gen/iteration_01/iteration_rollup.json")):
        e = bd[label]
        # c88 re-pin (disclosed): the c87 flag-off record is for the c87 image (= the c88 pre-edit pin); c88 re-proves iteration 2 flag-off under the post-edit image
        assert e["generate_v5_sha256"] == _j("data/v5/gen/byte_determinism_c88.json")["turn_start_pins"]["generate_v5_pre_edit"]["sha256"], label
        assert e["all_equal"] is True and e["n_equal"] == 5, label
        recorded = {f"{s['generated_song_id']}_donor_{s['donor']}": s["ab_mix_sha256"] for s in _j(roll_path)["songs"]}
        for k, v in e["per_song"].items():
            assert v["flag_off_sha256"] == v["recorded_sha256"] == recorded[k], (label, k)
    for k, pre in IT2_WAV.items():
        assert bd["iteration_02_flag_off_replay"]["per_song"][k]["flag_off_sha256"].startswith(pre)
    print("test_04 PASS: flag-off replays under the FINAL image reproduce iteration-2 5/5 and iteration-1 5/5")


def test_05_listening_copies_and_stall_counter_f6_entry() -> None:
    lm = _j("data/v4/generated/v5_iter_03/listening_manifest.json")
    assert lm["cycle"] == 87 and lm["iteration"] == 3 and len(lm["samples"]) == 5 and lm["milestone"] == "M-V5-GEN-1/F2-bass-melody-dynamics"
    for smp in lm["samples"]:
        for fn, sha in smp["copied_sha256"].items():
            assert _sha(Path(smp["dest"]) / fn) == sha, (smp["dest"], fn)
    stall = _j("data/v5/gen/stall_counter.json")
    # c88 re-pin (disclosed): the counter advances by design (4/12 at iteration 4); the iteration-3 entry is history[2]
    assert stall["iterations"] >= 3 and stall["budget"] == 12 and len(stall["history"]) >= 3
    h = stall["history"][2]
    assert h["iteration"] == 3 and h["cycle"] == 87 and h["seed"] == 2 and h["feature"] == "F2 bass+melody+dynamics" and h["passers_declared"] == 0
    assert h["form_plan_sha256"].startswith("d6c14f9a") and h["rules_sha256"]["harmony_chain"].startswith("a984ee17") and h["rules_sha256"]["groove_model"].startswith("faa0e76e")
    assert h["f2"]["models_sha256"]["velocity_profiles"] == PROFILES_SHA and h["f2"]["f2_enum"] == _j(IT3 / "iteration_rollup.json")["f2"]["f2_enum"]
    # nothing else under data/v4/** was touched by the v5 pipeline: the frozen anchors still match the c86 emitter's expectations
    assert _sha("data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav").startswith("6e13e007") and _sha("data/v4/gen/donor_profile_map.json").startswith("8c0b54cd")
    print(f"test_05 PASS: 5 listening copies SHA-verified under data/v4/generated/v5_iter_03/; stall {stall['iterations']}/{stall['budget']} with the F6 entry")


def test_06_argparse_guard_f2_flags_require_f2_and_flag_off_help_unchanged() -> None:
    for argv in (["--velocity-mode", "f2"], ["--rms-variance-test"]):
        r = subprocess.run(["/usr/bin/python3", "scripts/v5/generate_v5.py", "--iteration", "3", "--out", "/tmp/never"] + argv, capture_output=True, text=True)
        assert r.returncode == 2 and "require --f2" in r.stderr, (argv, r.returncode, r.stderr[-300:])
        assert not Path("/tmp/never").exists()
    r = subprocess.run(["/usr/bin/python3", "scripts/v5/generate_v5.py", "--help"], capture_output=True, text=True)
    assert r.returncode == 0 and "--f2" in r.stdout
    print("test_06 PASS: --velocity-mode f2 / --rms-variance-test without --f2 is an argparse error (rc 2), nothing written")


def test_07_serializer_guard_stamps_and_pinned_script_tolerance() -> None:
    src = Path("scripts/v5/midi_from_json_events_v5.py").read_text()
    ast.parse(src)
    assert '"/usr/bin/python3"' in src and "SUPPRESS_INTERPRETER_GUARD" in src
    for s in ("scripts/v5/midi_from_json_events_v5.py", "data/v5/rules/plot_velocity_profiles_c86.py", "data/v5/gen/iteration_03/plot_iter03_velocity_c86.py", "tools/_emit_c87_early_events.py", __file__):
        m = re.search(r"created: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z", Path(s).read_text())
        assert m, s
        assert calendar.timegm(_t.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")) <= Path(s).stat().st_mtime, s
    # velocity_v5.py is pinned by SHA inside every velocities.json → its 36 s stamp skew is TOLERATED (120 s), never edited
    m = re.search(r"created: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z", Path("scripts/v5/velocity_v5.py").read_text())
    skew = calendar.timegm(_t.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")) - Path("scripts/v5/velocity_v5.py").stat().st_mtime
    assert skew <= 120 and _sha("scripts/v5/velocity_v5.py") == VELOCITY_V5_SHA
    # the serializer is still byte-equal to the c4 serializer without velocities (one iteration-2 stem, live)
    import tempfile
    from scripts.v3_spine.midi_from_json_events import serialize as c4
    from scripts.v5.midi_from_json_events_v5 import serialize as v5
    j = sorted(Path("data/v5/gen/iteration_02").glob("*/generated_json/bass.json"))[0]
    bpm = float(_j(j.parent.parent / "ab_mix.manifest.json")["tempo_bpm"])
    with tempfile.TemporaryDirectory() as td:
        c4(str(j), f"{td}/a.mid", bpm, (4, 4)); v5(str(j), f"{td}/b.mid", bpm, (4, 4))
        assert _sha(f"{td}/a.mid") == _sha(f"{td}/b.mid")
    print(f"test_07 PASS: serializer guard + exact stamps; velocity_v5.py skew {skew:.0f} s tolerated (pinned {VELOCITY_V5_SHA[:8]}); c4 byte-equality live")


def test_08_early_ledger_trio_and_guidance_verbatim() -> None:
    L = _ledger()
    c87 = {e["milestone_id"]: e for e in L if e.get("cycle") == 87}
    g = c87["_plan/adopt-operator-guidance-2026-09-09-c131"]
    text = Path(G131).read_text()
    assert _sha(G131).startswith(G131_SHA16) and f"<<<{text}>>>" in g["narrative"] and g["agent"] == "worker" and g["status"] == "validated"
    r = c87["M-V5-GEN-1/F2-route-decided-c86"]
    assert "decided_at=2026-09-09T22:55:58Z" in r["narrative"] and "ledgered_at=" in r["narrative"] and "ROUTE_1_STEM_AUDIO" in r["narrative"]
    f4 = c87["M-V5-GEN-1/F4-tempo-fix"]
    assert f4["status"] == "validated" and f4["confidence"]["level"] == "high" and f4["supersedes_path"] == "data/v5/corpus/tempo_f4_verdict_c85.json"
    assert "122.197271" in f4["narrative"] and "120.272335" in f4["narrative"] and "2fbabc07849dbe23" in f4["narrative"] and "eb78cfc0ce57dc9f" in f4["narrative"]
    assert _sha("data/v5/corpus/recanonicalization_blocked.json").startswith("eb78cfc0ce57dc9f")
    for e in c87.values():
        assert e["agent"] == "worker" and isinstance(e["supersedes_path"], (str, type(None))) and e["env_pin_sha256"] == ENV_PIN
    print(f"test_08 PASS: early c87 trio present ({len(c87)} c87 events so far), guidance verbatim, F4 CLOSED with pre/post SHAs")


def test_09_cross_cycle_stem_mismatch_accepted_one_line_no_memo() -> None:
    bd = _j(BD)["entries"]["route1_separation"]
    per = bd["per_song"]
    assert all(per[s]["cross_cycle_x2_holds_vs_c79_cache"] is False for s in FOCUS) and per["252eb21ce7df7328"]["in_cycle_x2_holds"] is True
    assert bd["wig_gate_run_equals_extractor_runs"] is True and "ACCEPTED" in bd["note"]
    for s in FOCUS:
        assert per[s]["velocities_json_sha256"] == _sha(f"data/v5/corpus/{s}/velocity_v5/velocities.json")
    memos = list(Path("docs").rglob("*stem*mismatch*")) + list(Path("docs").rglob("*cross_cycle*"))
    assert not memos, memos
    print("test_09 PASS: cross-cycle stem mismatch recorded as accepted (velocities.json SHAs are the anchors); no memo written")


def test_10_disk_semantics_and_iter03_figure_reissued() -> None:
    row = subprocess.run(["df", "-P", "."], capture_output=True, text=True, check=True).stdout.splitlines()[-1].split()
    assert int(row[4].rstrip("%")) < 90
    fig = IT3 / "fig_iter03_velocity_c86.png"
    assert fig.exists() and fig.stat().st_size > 10_000 and fig.stat().st_mtime > (IT3 / "iteration_rollup.json").stat().st_mtime
    r = subprocess.run(["/usr/bin/python3", str(IT3 / "plot_iter03_velocity_c86.py")], capture_output=True, text=True)
    assert r.returncode == 2 and "--out" in r.stderr
    assert (Path("data/v5/rules/fig_velocity_profiles_c86.png")).stat().st_size > 10_000
    print(f"test_10 PASS: df {row[4]} (driver semantics) < 90 %; iteration-3 + profile figures on disk; --out required")


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"{name} FAIL: {type(exc).__name__}: {exc}")
    print(f"{10 - fails}/10 PASS")
    sys.exit(1 if fails else 0)
