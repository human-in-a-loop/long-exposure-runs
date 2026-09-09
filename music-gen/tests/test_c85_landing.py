#!/usr/bin/python3
"""c85 landing tests — F1 form plan + arrangement (prereg gate, segmentation determinism on a synthetic fixture, contrast rule,
A-repeat byte-equality in iteration 2, iteration-1 flag-off replay), P0 cheap fixes (M4 no groove copy, F6 stall schema),
F4 honest AMBIGUOUS record, guidance adoption, discipline.

created: 2026-09-09T22:20:00Z
cycle: 85
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle85-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_c85_landing.py   (the F4 synthetic half/double check + --eligible-from + score_gen
--cycle/--milestone tests live in tests/test_c85_f4_m5.py)
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
NEW_SCRIPTS = ["scripts/v5/form_plan_v5.py", "scripts/v5/generate_v5.py", "scripts/v5/deliver_v5_listening.py", "scripts/v5/harmony_v5.py",
               "scripts/v5/score_gen_batch_v5.py", "scripts/v5/tempo_f4_adjudicate_c85.py", "data/v5/rules/plot_form_plan_corpus_c85.py",
               "data/v5/gen/iteration_02/plot_iter02_arrangement_c85.py"]
IT2 = _ROOT / "data/v5/gen/iteration_02"
C84_WAV = {"gen_v5_song_1_donor_31a164f845f8e27e": "f4cdb2947227a6cb", "gen_v5_song_2_donor_252eb21ce7df7328": "953dbffc886359bb",
           "gen_v5_song_3_donor_51e433ade2a845e1": "0a95411b2d20d177", "gen_v5_song_4_donor_88d247468cb6d49f": "2f21412805edc127",
           "gen_v5_song_5_donor_cdd2717e52820ff6": "aa1da38f94b09eea"}


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _j(p):
    return json.loads(Path(p).read_text())


def test_01_prereg_before_every_output() -> None:
    pre = _ROOT / "data/v5/gen/form_prereg_c85.json"
    outs = [_ROOT / "data/v5/rules/form_plan_v5.json"] + sorted(IT2.glob("*/ab_mix.manifest.json")) + sorted(IT2.glob("*/ab_mix.wav"))
    assert len(outs) == 11
    for o in outs:
        assert pre.stat().st_mtime < o.stat().st_mtime, o
    fp = _j("data/v5/rules/form_plan_v5.json")
    assert fp["prereg_sha256"] == _sha(pre)
    f4p, f4v = _ROOT / "data/v5/corpus/tempo_f4_prereg_c85.json", _ROOT / "data/v5/corpus/tempo_f4_verdict_c85.json"
    assert f4p.stat().st_mtime < f4v.stat().st_mtime and _j(f4v)["prereg_sha256"] == _sha(f4p)
    # F4 did not RESOLVE -> no c85 harmony/groove preregs, no v5c canonical dirs, blocked file byte-identical
    assert not (_ROOT / "data/v5/rules/harmony_prereg_c85.json").exists() and not (_ROOT / "data/v5/rules/groove_prereg_c85.json").exists()
    assert not list((_ROOT / "data/v5/corpus").glob("*/canonical_v5c_reindexed"))
    assert _sha("data/v5/corpus/recanonicalization_blocked.json").startswith("2fbabc07849dbe23")
    print("test_01 PASS: form + F4 preregs precede every output; no c85 rules preregs (F4 not RESOLVED); blocked file untouched")


def test_02_segmentation_recovers_known_forms_on_synthetic_fixture() -> None:
    from scripts.v5.form_plan_v5 import cosine_matrix, single_linkage, first_appearance_labels
    rng_free = {"X": np.concatenate([np.eye(66)[0], np.zeros(0)]), "Y": np.eye(66)[20], "Z": np.eye(66)[40]}
    fixture = {"song1": ("XXYXYZ", "AABABC"), "song2": ("XYXY", "ABAB"), "song3": ("XXXXYY", "AAAABB")}
    for name, (blocks, expected) in fixture.items():
        bf = np.stack([rng_free[c] + 0.05 * np.eye(66)[1] for c in blocks])  # small shared component: within-class cos 1.0, across ~0.0025
        S = cosine_matrix(bf)
        got1 = first_appearance_labels(single_linkage(S, 0.85))
        got2 = first_appearance_labels(single_linkage(cosine_matrix(bf.copy()), 0.85))
        assert got1 == got2 == expected, (name, got1, expected)
    # ties are broken by the lowest pair index (deterministic): three identical blocks -> AAA regardless of merge order
    bf = np.stack([np.eye(66)[3]] * 3)
    assert first_appearance_labels(single_linkage(cosine_matrix(bf), 0.85)) == "AAA"
    print("test_02 PASS: synthetic 3-song fixture forms recovered deterministically (AABABC / ABAB / AAAABB)")


def test_03_contrast_rule_fires_and_does_not_fire() -> None:
    from scripts.v5 import generate_v5 as GEN
    groove = _j("data/v5/rules/groove_v5_v2_full.json")
    chain = _j("data/v5/rules/harmony_markov_v5_full.json")
    fp = _j("data/v5/rules/form_plan_v5.json")
    c = GEN.contrast_section(groove, chain, fp, "fixture|seed=1", "B", 0, 1)
    assert c["harmony_contrast_ok"] and c["first_chord_root"] != 0 and c["n_allowed_start_states"] > 0
    assert c["target_tercile"] != 1 and c["density_contrast_ok"] == (c["realized_tercile"] != 1)
    assert c["contrast_rule_true"] == (c["harmony_contrast_ok"] and c["density_contrast_ok"])
    # negative: a chain whose every state shares A's dominant root cannot supply a contrasting start -> harmony clause False
    tiny = {"states": ["0:maj", "0:min"], "stationary_distribution": {"0:maj": 0.5, "0:min": 0.5}, "segment_level_counts": [[5, 10], [10, 5]], "per_song": {}}
    n = GEN.contrast_section(groove, tiny, fp, "fixture|seed=1", "B", 0, 1)
    assert not n["harmony_contrast_ok"] and n["n_allowed_start_states"] == 0 and not n["contrast_rule_true"]
    # segment-count restriction (>= 8) excludes rare roots
    rare = {"states": ["0:maj", "5:maj"], "stationary_distribution": {"0:maj": 0.9, "5:maj": 0.1}, "segment_level_counts": [[50, 3], [3, 1]], "per_song": {}}
    r = GEN.contrast_section(groove, rare, fp, "fixture|seed=1", "B", 0, 1)
    assert n["n_allowed_start_states"] == 0 and r["n_allowed_start_states"] == 0 and not r["harmony_contrast_ok"]
    print("test_03 PASS: contrast rule fires on the n=21 chain and does not fire on same-root / rare-root fixtures")


def test_04_a_repeats_byte_equal_in_iteration_02_midi() -> None:
    roll = _j(IT2 / "iteration_rollup.json")
    assert len(roll["songs"]) == 5 and roll["seed"] == 1 and roll["form_plan"]["R1_pass"] is False
    for s in roll["songs"]:
        d = IT2 / f"{s['generated_song_id']}_donor_{s['donor']}"
        m = _j(d / "ab_mix.manifest.json")
        core = m["f1"]["section_core_midi_sha256"]
        a = {k: v for k, v in core.items() if k.endswith("_A")}
        assert len(a) >= 2 and len(set(a.values())) == 1 and m["f1"]["a_repeats_byte_equal"]
        for k, v in core.items():
            i, lab = k.split("_")
            assert _sha(d / "generated_midi" / "sections" / f"section_{i}_{lab}.mid") == v
        non_a = {v for k, v in core.items() if not k.endswith("_A")}
        assert not (non_a & set(a.values())), "non-A sections must differ from A"
        assert m["form_plan"] == list("AABABCAA")[: len(m["form_plan"])] and m["bars_per_section"] == 8
        assert m["n_bars"] == 8 * len(m["form_plan"]) and m["form_plan_sha256"] == _sha("data/v5/rules/form_plan_v5.json")
        pr = _j(d / "ab_mix.replay_proof.json")
        assert pr["verdict"] == "REPLAY_PROOF_HOLDS" and pr["run1_sha256"] == pr["run2_sha256"] == _sha(d / "ab_mix.wav")
        assert not list((d / "per_track").glob("*.wav"))
    assert roll["f1_enum"] in ("FORM_PLAN_LANDS", "FORM_PLAN_PARTIAL", "FORM_PLAN_FAILS")
    n_ok = sum(1 for s in roll["songs"] if s["all_clauses"])
    assert roll["f1_enum"] == ("FORM_PLAN_LANDS" if n_ok == 5 else "FORM_PLAN_PARTIAL" if n_ok >= 3 else "FORM_PLAN_FAILS")
    print(f"test_04 PASS: A repeats byte-equal on 5/5; 5/5 REPLAY_PROOF_HOLDS; enum {roll['f1_enum']} consistent ({n_ok}/5)")


def test_05_iteration_01_flag_off_replay_and_m4() -> None:
    bd = _j("data/v5/gen/byte_determinism_c85.json")["entries"]
    e = bd["iteration_01_flag_off_replay"]
    assert e["all_equal"] and not e["groove_model_copied"]
    for k, v in e["per_song"].items():
        assert v["c84_sha256"].startswith(C84_WAV[k]) and v["equal"]
    assert not (IT2 / "groove_model_used.json").exists()  # M4
    assert (_ROOT / "data/v5/gen/iteration_01/groove_model_used.json").exists()  # never delete (reclaimable, disclosed)
    assert bd["form_plan_v5"]["equal"] and bd["iteration_02_renders"]["all_equal"] and bd["iteration_02_ear_scores_table"]["equal"]
    for key in ("form_plan_v5", "iteration_02_ear_scores_table"):
        assert bd[key]["run1_sha256"] == bd[key]["run2_sha256"] and "tempdir_run2" in bd[key]
    print("test_05 PASS: flag-off replay reproduces the 5 c84 WAV SHAs; M4 no groove copy; byte-det entries x2 with tempdirs")


def test_06_stall_history_schema_f6() -> None:
    sc = _j("data/v5/gen/stall_counter.json")
    assert sc["iterations"] == 2 and sc["budget"] == 12 and sc["passers"] == 0 and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", sc["ts"])
    h = sc["history"][-1]
    for k in ("iteration", "cycle", "seed", "feature", "donor_map_sha256", "form_plan_sha256", "rules_sha256"):
        assert k in h, k
    assert h["iteration"] == 2 and h["cycle"] == 85 and h["seed"] == 1 and h["feature"].startswith("F1")
    assert h["form_plan_sha256"] == _sha("data/v5/rules/form_plan_v5.json") and h["rules_sha256"]["harmony_chain"] == _sha("data/v5/rules/harmony_markov_v5_full.json")
    print("test_06 PASS: stall counter 2/12 with F6 history schema (feature / donor_map / form_plan / rules / seed) + ts")


def test_07_form_model_r1_record_and_targets() -> None:
    fp = _j("data/v5/rules/form_plan_v5.json")
    assert fp["n_eligible"] == 21 and fp["R1"]["pass"] is False and fp["R1"]["fallback_template"] == list("AABABCAA")
    assert fp["R1"]["focus_songs"]["31a164f845f8e27e"]["n_labels"] == 2 and fp["R1"]["focus_songs"]["51e433ade2a845e1"]["n_labels"] == 1
    assert sum(fp["length_distribution"].values()) == 21 and set(fp["length_distribution"]) <= {"4", "5", "6", "7", "8"}
    assert fp["density_tercile_bounds"][0] < fp["density_tercile_bounds"][1] and fp["boundary_fill_pool"] and not fp["fill_pool_fallback_used"]
    assert all(abs(sum(v["density_tercile_probs"]) - 1) < 1e-5 for v in fp["per_label"].values())  # probs rounded to 6 dp
    assert fp["chain_sha256"] == _sha("data/v5/rules/harmony_markov_v5_full.json") and 0 <= fp["intro_density_quantile"] <= 1
    assert (_ROOT / "data/v5/rules/fig_form_plan_corpus_c85.png").exists() and (IT2 / "fig_iter02_arrangement_c85.png").exists()
    print("test_07 PASS: R1 FAILED recorded honestly (template fallback); model targets well-formed; both figures on disk")


def test_08_f4_ambiguous_recorded_and_listening_delivered() -> None:
    v = _j("data/v5/corpus/tempo_f4_verdict_c85.json")
    assert v["verdict"] == "F4_HALF_DOUBLE_AMBIGUOUS" and v["blocked_file_touched"] is False
    assert v["recanonicalization_blocked_sha256"] == _sha("data/v5/corpus/recanonicalization_blocked.json")
    assert v["authority"]["sha256"] == _sha("docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt")
    lm = _j("data/v4/generated/v5_iter_02/listening_manifest.json")
    assert lm["cycle"] == 85 and len(lm["samples"]) == 5 and lm["milestone"] == "M-V5-GEN-1/F1-form-arrangement"
    for r in lm["samples"]:
        assert _sha(Path(r["dest"]) / "ab_mix.wav") == r["copied_sha256"]["ab_mix.wav"]
    sc = _j("data/v5/gen/gen_v5_iter02_ear_scores_c85.json")
    assert sc["cycle"] == 85 and sc["informational_only"] and sc["n_scored"] == 5
    print("test_08 PASS: F4_HALF_DOUBLE_AMBIGUOUS recorded, blocked file untouched; 5 listening copies delivered; scores informational")


def test_09_discipline_ast_guards_and_created_stamps() -> None:
    bad_mods = {"random", "numpy.random"}
    for p in NEW_SCRIPTS:
        src = Path(p).read_text()
        tree = ast.parse(src)
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                assert not any(a.name in bad_mods for a in n.names), p
            if isinstance(n, ast.ImportFrom):
                assert n.module not in bad_mods and "sidecar_nonfactor" not in (n.module or ""), p
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                assert n.func.attr not in {"get_state", "save_state", "save_preset", "load_state", "set_state"}, (p, n.func.attr)
        assert "/usr/bin/python3" in src.splitlines()[0]
        m = re.search(r"created: (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)", src)
        if m and p.endswith("c85.py") or p == "scripts/v5/form_plan_v5.py":
            import calendar, time
            created = calendar.timegm(time.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ"))
            assert created <= Path(p).stat().st_mtime, (p, "created stamp postdates mtime")
    print(f"test_09 PASS: discipline on {len(NEW_SCRIPTS)} c85 scripts; created stamps do not postdate mtimes")


def test_10_guidance_adopted_in_ledger() -> None:
    ids = {}
    for line in Path("promise_ledger.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            e = json.loads(line)
            ids[e["milestone_id"]] = e
    e = ids.get("_plan/adopt-operator-guidance-2026-09-09-F1-F7")
    assert e and e["agent"] == "worker" and e["supersedes_path"] is None
    for tok in ("A. The ear >=6 passer count is NOT the gate", "F1 LENGTH + FORM + ARRANGEMENT", "F7 M-V5-CLOSE-1 docs"):
        assert tok in e["narrative"], tok
    por = Path("plan_of_record.md").read_text()
    for row in ("M-V5-GEN-1/F1-form-arrangement", "M-V5-GEN-1/F4-tempo-fix", "M-V5-GEN-1/F6-iteration-schedule", "M-V5-GEN-1/F7-close"):
        assert f"| {row} |" in por.split("\n## Sub-milestones\n")[0], row  # line-start split (a c28 row quotes the header inline)
    print("test_10 PASS: guidance adopted verbatim in the ledger; F1..F7 POR rows registered inline")


if __name__ == "__main__":
    fails = 0
    tests = sorted((k, v) for k, v in globals().items() if k.startswith("test_"))
    for name, fn in tests:
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"{name} FAIL: {e!r}")
    print(f"{len(tests) - fails}/{len(tests)} PASS")
    sys.exit(1 if fails else 0)
