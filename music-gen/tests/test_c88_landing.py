#!/usr/bin/python3
"""c88 (= harness c132) landing tests — F3 `--f3` wiring + iteration 4 on the n=23 chain with the adopted PD / Disco A tempos.

created: 2026-09-10T06:30:00Z
cycle: 88
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F3-guitar-piano-other

Run: PYTHONPATH=. /usr/bin/python3 tests/test_c88_landing.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
IT4 = Path("data/v5/gen/iteration_04")
BD = Path("data/v5/gen/byte_determinism_c88.json")
PREREG = Path("data/v5/gen/f3_prereg_c88.json")
GEN = Path("scripts/v5/generate_v5.py")
PARTS = ("guitar", "piano", "other")
ADOPTED = {"88d247468cb6d49f": 122.197271, "cdd2717e52820ff6": 120.272335}
PINS = {"harmony_chain": "330b9d46", "groove_model": "57072025", "form_plan": "d6c14f9a", "comping_model": "01024254", "velocity_profiles": "6b2fc502",
        "bass_pitch": "96d34b3b", "melody_vomm": "48157c6f", "tempo_overrides": "ef52f2a0", "harmony_prereg": "b32cf397", "groove_prereg": "995acc5b"}


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _j(p):
    return json.loads(Path(p).read_text())


def _song_dirs() -> list:
    return sorted(d for d in IT4.iterdir() if d.is_dir() and d.name.startswith("gen_v5_song_"))


def _note_ons(mid: Path) -> int:
    import mido
    return sum(1 for t in mido.MidiFile(str(mid)).tracks for m in t if m.type == "note_on" and m.velocity > 0)


def test_01_prereg_mtime_precedes_every_f3_output() -> None:
    t = PREREG.stat().st_mtime
    outs = [p for p in IT4.rglob("*") if p.is_file() and p.name != "plot_iter04_parts_c88.py"]
    assert len(outs) >= 40, len(outs)
    late = [str(p) for p in outs if p.stat().st_mtime <= t]
    assert not late, late[:5]
    pr = _j(PREREG)
    assert pr["enum"].keys() >= {"F3_LANDS", "F3_PARTIAL", "F3_FAILS"} and pr["render_level_test"]["n_note_on_min"] == 32 and pr["render_level_test"]["audibility_floor_dbfs"] == -60.0
    assert _j(IT4 / "iteration_rollup.json")["f3"]["prereg_sha256"] == _sha(PREREG)
    print(f"test_01 PASS: f3_prereg_c88.json mtime precedes all {len(outs)} iteration-4 outputs; rollup pins the prereg sha")


def test_02_argparse_f3_default_off_and_subflag_rejection() -> None:
    env = dict(os.environ, PYTHONPATH=str(_ROOT))
    h = subprocess.run(["/usr/bin/python3", str(GEN), "--help"], capture_output=True, text=True, env=env)
    assert h.returncode == 0 and "--f3" in h.stdout and "--comping-model" in h.stdout and "--tempo-overrides" in h.stdout and "--harmony-prereg" in h.stdout
    r = subprocess.run(["/usr/bin/python3", str(GEN), "--comping-model", "data/v5/rules/comping_v5.json", "--out", "/tmp/never"], capture_output=True, text=True, env=env)
    assert r.returncode == 2 and "--comping-model requires --f3" in r.stderr, r.stderr[-300:]
    r2 = subprocess.run(["/usr/bin/python3", str(GEN), "--velocity-mode", "f2", "--out", "/tmp/never"], capture_output=True, text=True, env=env)
    assert r2.returncode == 2 and "require --f2" in r2.stderr  # c87 guard still in place
    src = GEN.read_text()
    assert 'ap.add_argument("--f3", action="store_true"' in src and 'ap.add_argument("--comping-model", default=None' in src
    assert not Path("/tmp/never").exists()
    print("test_02 PASS: --f3 default off (store_true); --comping-model rejected without --f3; c87 --f2 guard intact")


def test_03_parts_present_in_midi_5_of_5_and_program_policy() -> None:
    pr = _j(PREREG)["program_policy"]["per_song"]
    n = 0
    for d in _song_dirs():
        man = _j(d / "ab_mix.manifest.json")
        donor = man["donor_song_sha16"]
        assert man["milestone"] == "M-V5-GEN-1/F3-guitar-piano-other" and man["seed"] == 3
        for p in PARTS:
            st = man["f3"]["parts"][p]
            n_on = _note_ons(d / "generated_midi" / f"{p}.mid")
            assert n_on == st["n_note_on"] >= 32, (d.name, p, n_on, st["n_note_on"])
            assert st["audible"] is True and st["normalised_track_rms_dbfs"] > -60.0, (d.name, p, st)
            assert st["program"] == pr[donor]["parts"][p]["program"], (d.name, p, st["program"], pr[donor]["parts"][p])
            if pr[donor]["parts"][p]["source"] == "donor_pinned_profile":
                assert st["program_source"].endswith(f"{p}.json") and _sha(st["program_source"]) == pr[donor]["parts"][p]["sha256"]
            else:
                assert st["program_source"].startswith("shim:")
            assert man["midi_sha256"][p] == _sha(d / "generated_midi" / f"{p}.mid")
        assert set(man["midi_sha256"]) == {"drums", "bass", "keys", "melody", *PARTS} and man["f3"]["per_song_ok"] is True
        n += 1
    assert n == 5
    print("test_03 PASS: guitar/piano/other MIDI present 5/5 (>= 32 note_on, audible, programs per the pre-registered policy: CG guitar pinned prog 28, else GM shims)")


def test_04_f3_off_reproduces_iteration_3_and_2_under_post_edit_image() -> None:
    bd = _j(BD)
    it3 = {f"{s['generated_song_id']}_donor_{s['donor']}": s["ab_mix_sha256"] for s in _j("data/v5/gen/iteration_03/iteration_rollup.json")["songs"]}
    fo = bd["entries"]["iteration_03_flag_off_replay"]
    # c89 re-pin (disclosed): the c88 post-edit image is now the c89 turn-start pin (generate_v5.py moved again for F5); on-disk == c89 post-edit
    assert fo["generate_v5_sha256"] == bd["post_edit_script_sha256"]["generate_v5"] == _j("data/v5/gen/byte_determinism_c89.json")["turn_start_pins"]["generate_v5_pre_edit"]["sha256"]
    assert "--f3" not in fo["command"] and "--f2" in fo["command"] and fo["n_equal"] == 5 and fo["all_equal"]
    for k, a in it3.items():
        assert fo["per_song"][k]["recorded_sha256"] == a == fo["per_song"][k]["flag_off_sha256"] == _sha(f"data/v5/gen/iteration_03/{k}/ab_mix.wav"), k
    fo2 = bd["entries"]["iteration_02_flag_off_replay"]
    assert fo2["n_equal"] == 5 and "--f2" not in fo2["command"] and "--f3" not in fo2["command"]
    assert bd["turn_start_pins"]["generate_v5_pre_edit"]["sha256"].startswith("f261690c1f534611") and bd["post_edit_script_sha256"]["generate_v5"] != bd["turn_start_pins"]["generate_v5_pre_edit"]["sha256"]
    print(f"test_04 PASS: F3-off under the post-edit image ({_sha(GEN)[:12]}…) reproduces iteration 3 5/5 and iteration 2 5/5; iteration-3 anchors unchanged")


def test_05_manifests_carry_n23_shas_and_adopted_tempos() -> None:
    to = _j("data/v5/corpus/tempo_overrides_c86.json")
    for d in _song_dirs():
        man = _j(d / "ab_mix.manifest.json")
        rs = man["rules_sha256"]
        for k, pre in PINS.items():
            assert rs[k].startswith(pre), (d.name, k, rs[k][:8], pre)
        assert rs["comping_builder"] == _sha("scripts/v5/comping_gen_v5.py") and man["f3"]["comping_builder_sha256"] == rs["comping_builder"]
        donor = man["donor_song_sha16"]
        if donor in ADOPTED:
            assert man["tempo_bpm"] == ADOPTED[donor] == to[donor] and man["tempo_source"].startswith("tempo_overrides_c86.json") and man["tempo_overrides"]["applied"] is True
        else:
            assert man["tempo_source"] == "tempo_v5.bpm_v5" and man["tempo_overrides"]["applied"] is False
        assert man["env_pin_sha256"] == "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca" and man["f2"]["velocity_mode"] == "f2"
    roll = _j(IT4 / "iteration_rollup.json")
    assert roll["tempo_overrides"]["overrides"] == to and roll["rules_sha256"]["harmony_chain"].startswith("330b9d46") and roll["harmony_verdict"] == "NON_DEGENERATE" and roll["groove_overfits_disclosed"] is True
    print("test_05 PASS: 5/5 manifests pin harmony n=23 330b9d46… / groove n=23 57072025… / form d6c14f9a… / comping 01024254…; PD + Disco A at the adopted tempos, others at bpm_v5")


def test_06_byte_det_x2_with_post_edit_sha_and_enum() -> None:
    bd = _j(BD)
    roll = _j(IT4 / "iteration_rollup.json")
    assert roll["generator_hash"] == bd["post_edit_script_sha256"]["generate_v5"] == _j("data/v5/gen/byte_determinism_c89.json")["turn_start_pins"]["generate_v5_pre_edit"]["sha256"]  # c89 re-pin (disclosed)
    it4 = bd["entries"]["iteration_04_renders"]
    assert it4["n_equal"] == 5 and it4["all_equal"]
    for d in _song_dirs():
        pr = _j(d / "ab_mix.replay_proof.json")
        assert pr["verdict"] == "REPLAY_PROOF_HOLDS" and pr["run1_sha256"] == pr["run2_sha256"] == _sha(d / "ab_mix.wav") and pr["run2_tempdir"].startswith("/tmp/gen_v5_replay_")
        assert pr["run2_midi_equal"] and pr["run2_per_track_equal"] and pr["cycle"] == 88
    assert bd["f3_enum_final"] in ("F3_LANDS", "F3_PARTIAL", "F3_FAILS") and roll["f3"]["f3_enum_per_song"] in ("F3_LANDS_pending_flagoff", "F3_PARTIAL", "F3_FAILS")
    if bd["f3_enum_final"] == "F3_LANDS":
        assert roll["f3"]["n_songs_all_per_song_clauses"] == 5 and bd["entries"]["iteration_03_flag_off_replay"]["all_equal"]
    assert bd["entries"]["iteration_04_ear_scores_table"]["equal"] is True and bd["entries"]["iteration_04_ear_scores_table"]["informational_only"] is True
    print(f"test_06 PASS: 5/5 REPLAY_PROOF_HOLDS in fresh tempdirs under the post-edit sha; F3 enum {bd['f3_enum_final']}; scores table ×2 equal (informational)")


def test_07_discipline_ast_scan_and_interpreter_guard() -> None:
    bad = re.compile(r"\b(random\.|np\.random|numpy\.random|time\.time\(|get_state\(|save_state\(|load_state\(|set_state\(|save_preset\()")
    imp = re.compile(r"^\s*(from|import)\s+.*sidecar_nonfactor", re.M)  # import-level check (the docstrings name the discipline)
    for s in ("scripts/v5/generate_v5.py", "scripts/v5/comping_gen_v5.py", "data/v5/gen/iteration_04/plot_iter04_parts_c88.py", "tools/_register_c88_por_rows.py"):
        src = Path(s).read_text()
        tree = ast.parse(src)
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        hits = [m.group(0) for m in bad.finditer(code) if m.start() > 0]
        assert not hits, (s, hits)
        assert not imp.search(src), s
        names = {n.names[0].name.split(".")[0] for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) and n.names}
        assert "random" not in names, s
        assert '"/usr/bin/python3"' in src or s.startswith("tools/"), s
        m = re.search(r"^created: (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)Z", src, re.M)
        assert m, s
    for d in _song_dirs():
        man = _j(d / "ab_mix.manifest.json")
        assert man["sampling"].startswith("SHA-256 inverse-CDF") and man["f3"]["velocity_source"].startswith("F2 keys-by-slot")
    print("test_07 PASS: no PRNG / sidecar_nonfactor / VST3 state APIs in the c88 code paths; interpreter guard + created stamps present; SHA-256 inverse-CDF sampling declared")


def test_08_por_f4_row_amended_and_c85_verdict_anchor_untouched() -> None:
    rows = [l for l in Path("plan_of_record.md").read_text().splitlines() if l.startswith("| M-V5-GEN-1/F4-tempo-fix | G5 |")]
    assert len(rows) == 1
    row = rows[0]
    assert "F4_HALF_DOUBLE_AMBIGUOUS" in row and "c86 RESOLVED" in row and "122.197271" in row and "120.272335" in row and "eb78cfc0" in row and "F4 CLOSED" in row
    assert _sha("data/v5/corpus/tempo_f4_verdict_c85.json").startswith("bec3631a") and _sha("data/v5/corpus/recanonicalization_blocked.json").startswith("eb78cfc0")
    assert _sha("data/v5/corpus/stale/recanonicalization_blocked.c80_c85.json").startswith("2fbabc07")
    print("test_08 PASS: POR F4 row keeps the c85 wording and carries the additive c86 RESOLVED clause; c85 verdict + blocked-file anchors untouched")


def test_09_stall_4_of_12_f6_entry_listening_copies_and_figure() -> None:
    sc = _j("data/v5/gen/stall_counter.json")
    assert sc["iterations"] >= 4 and sc["budget"] == 12 and sc["passers"] == 0 and len(sc["history"]) >= 4  # c89 re-pin (disclosed): the counter advances by design (5/12)
    h = sc["history"][3]
    assert h["iteration"] == 4 and h["cycle"] == 88 and h["seed"] == 3 and h["feature"] == "F3 guitar+piano+other" and h["passers_declared"] == 0
    assert h["rules_sha256"]["harmony_chain"].startswith("330b9d46") and h["rules_sha256"]["groove_model"].startswith("57072025") and h["form_plan_sha256"].startswith("d6c14f9a")
    assert h["donor_map_sha256"].startswith("8c0b54cd") and h["f3"]["comping_model_sha256"].startswith("01024254") and h["tempo_overrides_sha256"].startswith("ef52f2a0")
    lm = _j("data/v4/generated/v5_iter_04/listening_manifest.json")
    assert lm["cycle"] == 88 and lm["iteration"] == 4 and len(lm["samples"]) == 5 and lm["milestone"] == "M-V5-GEN-1/F3-guitar-piano-other"
    for smp in lm["samples"]:
        for fn, sha in smp["copied_sha256"].items():
            assert _sha(Path(smp["dest"]) / fn) == sha, (smp["dest"], fn)
    fig = IT4 / "fig_iter04_parts_c88.png"
    assert fig.exists() and fig.stat().st_size > 10_000 and fig.stat().st_mtime > (IT4 / "iteration_rollup.json").stat().st_mtime
    assert "--out" in (IT4 / "plot_iter04_parts_c88.py").read_text()
    print("test_09 PASS: stall 4/12 with the F6 entry (F3, seed 3, rules/form/donor/comping/tempo SHAs); 5 listening copies SHA-verified; figure via --out")


def test_10_iteration_1_to_3_and_read_only_anchors_byte_identical() -> None:
    n = 0
    for it in ("iteration_01", "iteration_02", "iteration_03"):
        for s in _j(f"data/v5/gen/{it}/iteration_rollup.json")["songs"]:
            k = f"{s['generated_song_id']}_donor_{s['donor']}"
            assert _sha(f"data/v5/gen/{it}/{k}/ab_mix.wav") == s["ab_mix_sha256"], (it, k)
            n += 1
    assert n == 15
    pins = _j(BD)["turn_start_pins"]
    drift = [k for k, v in pins.items() if k not in ("generate_v5_pre_edit", "plan_of_record_at_open") and _sha(v["path"]) != v["sha256"]]
    assert not drift, drift
    assert _sha("scripts/v5/velocity_v5.py").startswith("dd94336d") and _sha("data/v5/gen/form_prereg_c85.json").startswith("e71eda9b")
    print("test_10 PASS: 15 iteration-1..3 WAVs byte-identical to their rollups; all turn-start READ-ONLY pins unchanged (only generate_v5.py + POR moved)")


if __name__ == "__main__":
    fails = 0
    names = sorted(k for k, v in globals().items() if k.startswith("test_") and callable(v))
    for name in names:
        try:
            globals()[name]()
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"{name} FAIL: {type(exc).__name__}: {exc}")
    print(f"{len(names) - fails}/{len(names)} PASS")
    sys.exit(1 if fails else 0)
