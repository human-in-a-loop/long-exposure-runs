#!/usr/bin/python3
"""c89 (= harness c133) landing tests — F5 interpolation demo (CG <-> PD, t = 0.5) as the 6th render of iteration 5 (seed 4).

created: 2026-09-10T03:40:00Z
cycle: 89
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F5-interpolation-demo

Run: PYTHONPATH=. /usr/bin/python3 tests/test_c89_landing.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
IT5 = Path("data/v5/gen/iteration_05")
BD = Path("data/v5/gen/byte_determinism_c89.json")
PREREG = Path("data/v5/gen/f5_prereg_c89.json")
GEN = Path("scripts/v5/generate_v5.py")
INTERP = Path("scripts/v5/interpolate_v5.py")
HELPER = Path("scripts/v5/repo_root.py")
PLOT = Path("data/v5/gen/plot_iter05_parts_c89.py")
FIG = Path("data/v5/gen/fig_iter05_parts_c89.png")
A, B, T = "31a164f845f8e27e", "88d247468cb6d49f", 0.5
DEMO = IT5 / f"gen_v5_interp_CG_PD_t050_donor_{A}"
DELIV = Path("data/v4/generated/f5_interp_CG_PD_t050_c89")
STEMS = ("drums", "bass", "keys", "melody", "guitar", "piano", "other")
PINS = {"harmony_chain": "330b9d46", "groove_model": "57072025", "form_plan": "d6c14f9a", "comping_model": "01024254", "velocity_profiles": "6b2fc502",
        "bass_pitch": "96d34b3b", "melody_vomm": "48157c6f", "tempo_overrides": "ef52f2a0", "harmony_prereg": "b32cf397", "groove_prereg": "995acc5b"}


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _j(p):
    return json.loads(Path(p).read_text())


def _song_dirs() -> list:
    return sorted(d for d in IT5.iterdir() if d.is_dir() and d.name.startswith("gen_v5_"))


def test_01_prereg_mtime_precedes_every_output_and_code_and_is_not_future_dated() -> None:
    t = PREREG.stat().st_mtime
    outs = [p for p in IT5.rglob("*") if p.is_file()] + [INTERP, HELPER, GEN, PLOT, FIG]
    assert len(outs) >= 40, len(outs)
    late = [str(p) for p in outs if p.stat().st_mtime <= t]
    assert not late, late[:5]
    pr = _j(PREREG)
    created = time.mktime(time.strptime(pr["created"], "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
    assert created <= time.time() and abs(created - t) < 300, (pr["created"], t)
    assert set(pr["verdict_enum"]) >= {"F5_LANDS", "F5_PARTIAL", "F5_FAILS"} and pr["t"] == T and pr["seed"] == 4 and pr["iteration"] == 5
    assert pr["donors"]["A"]["id"] == A and pr["donors"]["B"]["id"] == B and pr["generator_pre_edit_sha256"].startswith("3d0f3a24c2b87ed9")
    assert "no_note_level_mean" in pr["blend_semantics"] and "argmax" in pr["blend_semantics"]["harmony"]["decoding"]
    roll = _j(IT5 / "iteration_rollup.json")
    assert roll["f5"]["prereg_sha256"] == _sha(PREREG) == roll["rules_sha256"]["f5_prereg"]
    print(f"test_01 PASS: f5_prereg_c89.json (created {pr['created']}, not future-dated) precedes all {len(outs)} iteration-5 outputs + the F5 code; enum frozen; rollup pins the prereg sha")


def test_02_argparse_f5_default_off_and_subflag_rejection() -> None:
    env = dict(os.environ, PYTHONPATH=str(_ROOT))
    h = subprocess.run(["/usr/bin/python3", str(GEN), "--help"], capture_output=True, text=True, env=env)
    assert h.returncode == 0 and all(f in h.stdout for f in ("--f5", "--interp-a", "--interp-b", "--interp-t", "--f5-prereg"))
    r = subprocess.run(["/usr/bin/python3", str(GEN), "--interp-a", "CG", "--out", "/tmp/never"], capture_output=True, text=True, env=env)
    assert r.returncode == 2 and "require --f5" in r.stderr, r.stderr[-300:]
    r2 = subprocess.run(["/usr/bin/python3", str(GEN), "--f5", "--interp-a", "CG", "--interp-b", "PD", "--interp-t", "0.5", "--out", "/tmp/never"], capture_output=True, text=True, env=env)
    assert r2.returncode == 2 and "--f5 requires" in r2.stderr
    r3 = subprocess.run(["/usr/bin/python3", str(GEN), "--comping-model", "data/v5/rules/comping_v5.json", "--out", "/tmp/never"], capture_output=True, text=True, env=env)
    assert r3.returncode == 2 and "requires --f3" in r3.stderr  # c88 guard intact
    src = GEN.read_text()
    assert 'ap.add_argument("--f5", action="store_true"' in src and "from scripts.v5.interpolate_v5 import" in src
    assert src.count("from scripts.v5.interpolate_v5 import") == 1 and "if args.f5:" in src  # imported only under --f5
    assert not Path("/tmp/never").exists()
    print("test_02 PASS: --f5 default off (store_true); sub-flags rejected without --f5; --f5 requires its four sub-flags; interpolate_v5 imported only under --f5")


def test_03_demo_byte_det_x2_in_process_and_independent_process() -> None:
    bd = _j(BD)
    it5 = bd["entries"]["iteration_05_renders"]
    assert it5["n_songs"] == 6 and it5["n_equal"] == 6 and it5["all_equal"]
    for d in _song_dirs():
        pr = _j(d / "ab_mix.replay_proof.json")
        assert pr["verdict"] == "REPLAY_PROOF_HOLDS" and pr["run1_sha256"] == pr["run2_sha256"] == _sha(d / "ab_mix.wav") and pr["run2_tempdir"].startswith("/tmp/gen_v5_replay_")
        assert pr["run2_midi_equal"] and pr["run2_per_track_equal"] and pr["cycle"] == 89
    ind = bd["entries"]["iteration_05_independent_process"]
    assert ind["n_songs"] == 6 and ind["n_equal"] == 6 and ind["all_equal"] and ind["tempdir"].startswith("/tmp/gen_v5_indep_c89_")
    assert "--prove-replay" not in ind["command"] and "--f5" in ind["command"]
    dk = DEMO.name
    assert ind["per_song"][dk]["is_demo"] and ind["per_song"][dk]["f5_blend_json_equal"] and ind["per_song"][dk]["independent_sha256"] == _sha(DEMO / "ab_mix.wav")
    assert bd["f5_demo_byte_det_x2"] == {"in_process_replay": True, "independent_process": True}
    print(f"test_03 PASS: 6/6 REPLAY_PROOF_HOLDS (in-process, fresh tempdirs) and 6/6 equal from an independent second process; demo {_sha(DEMO / 'ab_mix.wav')[:12]}… byte-det ×2")


def test_04_f5_off_reproduces_iteration_4_under_post_edit_image() -> None:
    bd = _j(BD)
    it4 = {f"{s['generated_song_id']}_donor_{s['donor']}": s["ab_mix_sha256"] for s in _j("data/v5/gen/iteration_04/iteration_rollup.json")["songs"]}
    fo = bd["entries"]["iteration_04_flag_off_replay"]
    assert fo["generate_v5_sha256"] == bd["post_edit_script_sha256"]["generate_v5"] == _sha(GEN)
    assert "--f5" not in fo["command"] and "--f3" in fo["command"] and "--f2" in fo["command"] and fo["n_equal"] == 5 and fo["all_equal"]
    for k, a in it4.items():
        assert fo["per_song"][k]["recorded_sha256"] == a == fo["per_song"][k]["flag_off_sha256"] == _sha(f"data/v5/gen/iteration_04/{k}/ab_mix.wav"), k
        assert bd["iteration_04_anchor_sha256"][k] == a == _j(PREREG)["regression_targets"]["iteration_04_ab_mix_sha256"][k]
    assert bd["f5_flag_off_regression_5_of_5"] is True
    print(f"test_04 PASS: F5-off (iteration-4 command) under the post-edit image ({_sha(GEN)[:12]}…) reproduces iteration 4 5/5; iteration-4 anchors unchanged")


def test_05_generator_pre_post_and_module_shas_recorded() -> None:
    bd = _j(BD)
    pre = bd["turn_start_pins"]["generate_v5_pre_edit"]["sha256"]
    post = bd["post_edit_script_sha256"]["generate_v5"]
    assert pre.startswith("3d0f3a24c2b87ed9") and post == _sha(GEN) != pre and _j(PREREG)["generator_pre_edit_sha256"] == pre
    roll = _j(IT5 / "iteration_rollup.json")
    assert roll["generator_hash"] == post and roll["f5"]["interpolate_v5_sha256"] == _sha(INTERP) == bd["post_edit_script_sha256"]["interpolate_v5"] == roll["rules_sha256"]["interpolate_v5"]
    assert bd["post_edit_script_sha256"]["repo_root"] == _sha(HELPER)
    launch = _j("data/v5/logs/gen_iter05_c89.launch.json")
    assert launch["generate_v5_sha256_post_edit"] == post and launch["generate_v5_sha256_pre_edit"] == pre and launch["interpolate_v5_sha256"] == _sha(INTERP)
    man = _j(DEMO / "ab_mix.manifest.json")
    assert man["generator_hash"] == post and man["f5"]["interpolate_v5_sha256"] == _sha(INTERP) and man["f5"]["prereg_sha256"] == _sha(PREREG)
    assert _sha("scripts/v5/velocity_v5.py").startswith("dd94336d") and _sha("scripts/v5/comping_gen_v5.py").startswith("571cc0a4")
    for d in _song_dirs():
        rs = _j(d / "ab_mix.manifest.json")["rules_sha256"]
        for k, p in PINS.items():
            assert rs[k].startswith(p), (d.name, k)
    print(f"test_05 PASS: PRE {pre[:12]}… (== brief) → POST {post[:12]}… recorded in the prereg / byte-det / launch / rollup / manifests; interpolate_v5 + repo_root SHAs pinned; velocity_v5.py untouched")


def test_06_audibility_statistics_on_raw_render_within_prereg_bands_and_blend_reproducible() -> None:
    man = _j(DEMO / "ab_mix.manifest.json")
    pr = _j(PREREG)
    f5 = man["f5"]
    raw = f5["raw_render_rms_dbfs"]
    assert set(raw) == set(STEMS) and all(v["raw_render_rms_dbfs"] > -60.0 and v["above_floor"] and v["n_note_on"] > 0 for v in raw.values()), raw
    g, h, cl = f5["audibility"]["groove"], f5["audibility"]["harmony"], f5["audibility"]["clauses"]
    exp = T * g["d_A_only_t1"] + (1 - T) * g["d_B_only_t0"]
    assert abs(g["expected_mixture"] - exp) < 1e-6 and cl["ii_groove_density_within_tol"] == (abs(g["d_mix"] - exp) <= 2.0) and g["tol"] == 2.0
    assert cl["iii_harmony_hamming_band"] == (0.0 < h["h_A"] < 1.0 and 0.0 < h["h_B"] < 1.0 and abs(h["h_A"] - h["h_B"]) <= 0.35) and h["band"] == 0.35
    assert cl["i_raw_rms_all_stems_above_floor"] is True and f5["audibility"]["all_clauses"] == all(cl.values())
    assert h["n_bars"] == man["n_bars"] == len(man["chord_sequence"]) and len(h["A_only_chords"]) == len(h["B_only_chords"]) == h["n_bars"]
    assert man["f5"]["t"] == T and man["tonic"] == 6 and man["tonic_source"] == "donor_kk_key_from_chain" and man["tempo_source"] == "tempo_v5.bpm_v5" and abs(man["tempo_bpm"] - 92.285156) < 1e-6
    # blend reproducibility from a fresh build in this process + f5_compose mirrors the demo composition at t = 0.5
    from scripts.v5.interpolate_v5 import donor_groove_tables, donor_harmony, build_blend_from, hamming_fraction
    from scripts.v5 import generate_v5 as GV
    corpus = Path("data/v5/corpus")
    to = {k: float(v) for k, v in _j("data/v5/corpus/tempo_overrides_c86.json").items()}
    chain, groove = _j("data/v5/rules/harmony_markov_v5_full_c86.json"), _j("data/v5/rules/groove_v5_v2_full_c86.json")
    TA, TB = donor_groove_tables(corpus, A, to), donor_groove_tables(corpus, B, to)
    HA, HB = donor_harmony(corpus, A, to), donor_harmony(corpus, B, to)
    bl = build_blend_from(TA, TB, HA, HB, chain, groove, A, B, T)
    rec_sha = hashlib.sha256(json.dumps(bl["record"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert rec_sha == f5["blend_record_sha256"] == _j(IT5 / "iteration_rollup.json")["f5"]["blend_record_sha256"]
    assert _j(DEMO / "f5_blend.json") == bl["record"]
    fp = _j("data/v5/rules/form_plan_v5.json")
    comp = GV.f5_compose(bl["groove"], bl["chain"], fp, man["seed_str"])
    assert comp["chords"] == man["chord_sequence"] and comp["form"] == man["form_plan"] and abs(comp["mean_drum_onsets_per_bar"] - g["d_mix"]) < 1e-9
    b1 = build_blend_from(TA, TB, HA, HB, chain, groove, A, B, 1.0)
    a_c = GV.f5_compose(b1["groove"], b1["chain"], fp, man["seed_str"])
    assert a_c["chords"] == h["A_only_chords"] and hamming_fraction(man["chord_sequence"], a_c["chords"]) == h["h_A"]
    # semantic sanity on the blend itself: rows are distributions; t=1 reproduces donor A rows; harmony counts row sums = n_mix
    row = bl["groove"]["model"]["kick_marginal"]["probs"]["*"]
    assert abs(sum(row.values()) - 1.0) < 1e-9 and set(row) == set(bl["groove"]["model"]["kick_marginal"]["vocab"])
    ra = TA["tables"]["kick_marginal"]["probs"]["*"]
    assert all(abs(b1["groove"]["model"]["kick_marginal"]["probs"]["*"][o] - ra.get(o, 0.0)) < 1e-12 for o in row)
    st = bl["chain"]["states"]
    nA = sum(1 for _ in HA["segments"][:-1])
    assert abs(sum(sum(r) for r in bl["chain"]["segment_level_counts"]) - (T * nA + (1 - T) * (len(HB["segments"]) - 1))) < 1e-6 and len(st) == 81
    assert abs(sum(bl["chain"]["stationary_distribution"].values()) - 1.0) < 1e-6
    print(f"test_06 PASS: raw render of 7 demo stems > -60 dBFS {[v['raw_render_rms_dbfs'] for v in raw.values()]}; density mix {g['d_mix']} vs expected {g['expected_mixture']} (dev {g['abs_dev']} ≤ 2.0); "
          f"Hamming h_A {h['h_A']} / h_B {h['h_B']}; clauses {cl}; blend record + composition reproduce byte-for-byte from a fresh build")


def test_07_expected_outputs_count_matches_disk_including_figure() -> None:
    pr = _j(PREREG)["expected_outputs"]
    files = [p for p in IT5.rglob("*") if p.is_file()]
    assert len(files) == pr["iteration_05_dir_total"], (len(files), pr["iteration_05_dir_total"])
    for name, spec in pr["song_dirs"].items():
        n = sum(1 for p in (IT5 / name).rglob("*") if p.is_file())
        assert n == spec["files"], (name, n, spec["files"])
        assert _j(IT5 / name / "ab_mix.manifest.json")["form_plan"] == spec["labels"]
    assert FIG.exists() and FIG.stat().st_size > 10_000 and PLOT.exists()
    assert len(files) + 2 == pr["count_with_figure"]
    assert (DEMO / "f5_blend.json").exists() and (DEMO / "ear_score_v5.json").exists()
    print(f"test_07 PASS: {len(files)} files under iteration_05 == pre-registered {pr['iteration_05_dir_total']} (per-song 25 + 2·n_sections, demo +1); figure counted ({pr['count_with_figure']})")


def test_08_discipline_no_sidecar_no_prng_repo_root_helper_used() -> None:
    bad = re.compile(r"\b(random\.|np\.random|numpy\.random|time\.time\(|get_state\(|save_state\(|load_state\(|set_state\(|save_preset\()")
    imp = re.compile(r"^\s*(from|import)\s+.*sidecar_nonfactor", re.M)
    for s in (str(GEN), str(INTERP), str(HELPER), str(PLOT), "tools/_register_c89_por_rows.py", "tools/_emit_c89_ledger_events.py"):
        src = Path(s).read_text()
        tree = ast.parse(src)
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        hits = [m.group(0) for m in bad.finditer(code)]
        assert not hits or s.startswith("tools/"), (s, hits)  # emitters stamp ts with time.strftime only
        assert not imp.search(src), s
        names = {n.names[0].name.split(".")[0] for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) and n.names}
        assert "random" not in names, s
        assert '"/usr/bin/python3"' in src or s.startswith("tools/") or s == str(HELPER), s  # repo_root.py is a pure stdlib helper (no I/O): shebang only, no guard
        assert re.search(r"^created: (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)Z", src, re.M), s
    plot = PLOT.read_text()
    assert "from scripts.v5.repo_root import repo_root" in plot and not re.search(r"parents\[\d+\]", plot)
    for d in _song_dirs():
        man = _j(d / "ab_mix.manifest.json")
        assert "sidecar_nonfactor" not in json.dumps(man) and man["sampling"].startswith("SHA-256 inverse-CDF")
    assert "sidecar_nonfactor" not in json.dumps(_j(DEMO / "f5_blend.json"))
    print("test_08 PASS: no PRNG / sidecar_nonfactor / VST3 state APIs in the c89 code paths or manifests; interpreter guard + created stamps; plot script uses the shared repo_root helper (no parents[N])")


def test_09_stall_5_of_12_f6_entry_listening_copies_and_demo_delivery() -> None:
    sc = _j("data/v5/gen/stall_counter.json")
    assert sc["iterations"] == 5 and sc["budget"] == 12 and sc["passers"] == 0 and len(sc["history"]) == 5
    h = sc["history"][4]
    assert h["iteration"] == 5 and h["cycle"] == 89 and h["seed"] == 4 and h["feature"] == "F5 interpolation demo" and h["passers_declared"] == 0
    assert h["f5"]["donors"] == {"A": A, "B": B, "names": {"A": "CG", "B": "PD"}} and h["f5"]["t"] == T and h["f5"]["prereg_sha256"] == _sha(PREREG)
    assert h["f5"]["verdict"] in ("F5_LANDS", "F5_PARTIAL", "F5_FAILS") and h["f5"]["verdict"] == _j(BD)["f5_enum_final"]
    assert h["rules_sha256"]["harmony_chain"].startswith("330b9d46") and h["rules_sha256"]["groove_model"].startswith("57072025") and h["form_plan_sha256"].startswith("d6c14f9a")
    assert h["f5"]["comping_model_sha256"].startswith("01024254") and h["tempo_overrides_sha256"].startswith("ef52f2a0")
    lm = _j("data/v4/generated/v5_iter_05/listening_manifest.json")
    assert lm["cycle"] == 89 and lm["iteration"] == 5 and len(lm["samples"]) == 6 and lm["milestone"] == "M-V5-GEN-1/F5-interpolation-demo"
    for smp in lm["samples"]:
        for fn, sha in smp["copied_sha256"].items():
            assert _sha(Path(smp["dest"]) / fn) == sha, (smp["dest"], fn)
    dm = _j(DELIV / "delivery_manifest.json")
    assert dm["cycle"] == 89 and dm["replay_proof"] == "REPLAY_PROOF_HOLDS" and dm["demo"]["t"] == T
    for fn, sha in dm["copied_sha256"].items():
        assert _sha(DELIV / fn) == sha and (fn == "f5_prereg_c89.json" and sha == _sha(PREREG) or _sha(DEMO / fn) == sha), fn
    assert dm["copied_sha256"]["ab_mix.wav"] == _sha(DEMO / "ab_mix.wav")
    print(f"test_09 PASS: stall 5/12 with the F6 entry (F5, CG/PD, t 0.5, verdict {h['f5']['verdict']}); 6 listening copies + demo delivery dir SHA-verified")


def test_10_verdict_enum_consistent_and_por_row_updated() -> None:
    bd = _j(BD)
    final = bd["f5_enum_final"]
    assert final in ("F5_LANDS", "F5_PARTIAL", "F5_FAILS")
    demo_bd = bd["f5_demo_byte_det_x2"]["in_process_replay"] and bd["f5_demo_byte_det_x2"]["independent_process"]
    expect = ("F5_LANDS" if bd["f5_audibility_all_clauses"] else "F5_PARTIAL") if (demo_bd and bd["f5_flag_off_regression_5_of_5"]) else "F5_FAILS"
    assert final == expect, (final, expect)
    roll = _j(IT5 / "iteration_rollup.json")
    assert roll["f5"]["f5_enum_pending_bytedet"] in ("F5_LANDS_pending_bytedet", "F5_PARTIAL", "F5_FAILS") and roll["f5"]["audibility_all"] == bd["f5_audibility_all_clauses"]
    assert roll["f1_enum"] in ("FORM_PLAN_LANDS", "FORM_PLAN_PARTIAL", "FORM_PLAN_FAILS") and roll["f3"]["n_songs_all_per_song_clauses"] <= 5 and len(roll["songs"]) == 6
    assert bd["entries"]["iteration_05_ear_scores_table"]["equal"] is True and bd["entries"]["iteration_05_ear_scores_table"]["informational_only"] is True
    rows = [l for l in Path("plan_of_record.md").read_text().splitlines() if l.startswith("| M-V5-GEN-1/F5-interpolation-demo | G5 |")]
    assert len(rows) == 1 and "c89 LANDED" in rows[0] and final in rows[0] and _sha(DEMO / "ab_mix.wav")[:16] in rows[0] and _sha(PREREG)[:16] in rows[0]
    print(f"test_10 PASS: f5_enum_final {final} consistent with the mechanical clauses; F1/F2/F3 enums over the 5 regular songs; POR F5 row carries the verdict + SHAs")


def test_11_iteration_1_to_4_and_read_only_anchors_byte_identical() -> None:
    n = 0
    for it in ("iteration_01", "iteration_02", "iteration_03", "iteration_04"):
        for s in _j(f"data/v5/gen/{it}/iteration_rollup.json")["songs"]:
            k = f"{s['generated_song_id']}_donor_{s['donor']}"
            assert _sha(f"data/v5/gen/{it}/{k}/ab_mix.wav") == s["ab_mix_sha256"], (it, k)
            n += 1
    assert n == 20
    pins = _j(BD)["turn_start_pins"]
    drift = [k for k, v in pins.items() if k not in ("generate_v5_pre_edit", "plan_of_record_at_open", "stall_counter_at_open") and _sha(v["path"]) != v["sha256"]]
    assert not drift, drift
    assert _sha("data/v5/gen/f3_prereg_c88.json").startswith("1f285325") and _sha("data/v5/gen/byte_determinism_c88.json").startswith("e32805a7")
    others = sorted(p.name for p in Path("data/v4/generated").iterdir())
    assert {"v5_iter_05", "f5_interp_CG_PD_t050_c89"} <= set(others)
    print("test_11 PASS: 20 iteration-1..4 WAVs byte-identical to their rollups; all turn-start READ-ONLY pins unchanged (only generate_v5.py, POR, stall counter moved)")


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
