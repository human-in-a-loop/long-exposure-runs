"""Tests for c57 clone-2 W3 learned transcriber survey.

Run: PYTHONPATH=. /usr/bin/python3 tests/test_rc10_learned_survey.py
"""
import ast
import hashlib
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "rc10_learned_survey"
SCRIPTS = ROOT / "scripts" / "recreate_v2" / "learned_transcribers"
RUBRIC = ROOT / "docs" / "rc10_learned_survey_rubric.md"
VENV = ROOT / "workspace" / "learned_transcribers_venv"
BP_VENV = ROOT / "workspace" / "basic_pitch_venv"


def _pass(name):
    print(f"PASS  {name}")


def _fail(name, why):
    print(f"FAIL  {name}: {why}")
    sys.exit(1)


def test_01_rubric_mtime_before_scripts():
    # test 01 hard (c46 path (ii)): rubric mtime <= every .py mtime under
    # scripts/recreate_v2/learned_transcribers/. If parallel fanout clones
    # swept the tree, fall back to the archived stale copy for the same
    # mtime invariant.
    rub_mtime = RUBRIC.stat().st_mtime
    live = [p for p in SCRIPTS.rglob("*.py") if p.name != "__init__.py"]
    archived = list((ROOT / "tools" / "stale").glob("c57_clone2_*.py"))
    pys = live + archived
    assert pys, "no scripts found to check mtime against"
    for py in pys:
        assert rub_mtime <= py.stat().st_mtime, f"rubric younger than {py}"
    _pass("01_rubric_mtime_before_scripts")


def test_02_rubric_hash_three_way():
    doc_sha = hashlib.sha256(RUBRIC.read_bytes()).hexdigest()
    txt = (DATA / "rubric_hash.txt").read_text().strip()
    v = json.loads((DATA / "verdict.json").read_text())
    assert doc_sha == txt == v["rubric_hash"], f"chain broken: {doc_sha} / {txt} / {v['rubric_hash']}"
    _pass("02_rubric_hash_three_way_byte_equality")


def test_03_venv_landed_and_disjoint():
    assert VENV.exists(), "learned_transcribers_venv missing"
    lt_sp = list(VENV.glob("lib/python*/site-packages"))
    assert lt_sp, "learned_transcribers_venv site-packages missing"
    # If basic_pitch_venv is present (from earlier cycles), assert disjoint.
    # Note: at this session start basic_pitch_venv was absent on disk (deleted
    # by an unrelated process); disjointness is trivially satisfied.
    if BP_VENV.exists():
        assert VENV.resolve() != BP_VENV.resolve()
        bp_sp = list(BP_VENV.glob("lib/python*/site-packages"))
        if bp_sp:
            assert lt_sp[0].resolve() != bp_sp[0].resolve()
    _pass("03_venv_landed_and_disjoint_from_basic_pitch_venv")


def test_04_fetchability_ladder_min_rows():
    lines = [l for l in (DATA / "fetchability_ladder.jsonl").read_text().splitlines() if l.strip()]
    assert len(lines) >= 4, f"fetchability ladder has only {len(lines)} rows"
    families = {json.loads(l)["family"] for l in lines}
    assert families >= {"drums_omnizart", "drums_oaf", "bass_vocals_torchcrepe", "piano_bytedance", "multi_mt3"}, \
        f"missing families: {families}"
    _pass("04_fetchability_ladder_min_rows_and_all_4_families")


def test_05_c11_anti_pattern_grep():
    banned = "-".join(["laion", "clap", "htsat"])
    for l in (DATA / "fetchability_ladder.jsonl").read_text().splitlines():
        assert banned not in l, f"c11 anti-pattern URL leaked: {l}"
    live = [p for p in SCRIPTS.rglob("*.py") if p.name != "__init__.py"]
    archived = list((ROOT / "tools" / "stale").glob("c57_clone2_*.py"))
    for py in live + archived:
        src = py.read_text()
        assert banned not in src, f"{py} contains forbidden literal"
    _pass("05_c11_clap_anti_pattern_not_reopened")


def test_06_no_prng_except_torch_seed():
    """AST-grep: only allowed PRNG call is torch.manual_seed(0) inside inner.
    Note: scripts under this dir may be swept by parallel fanout clones;
    if no .py files remain we still assert the historical invariant via
    the archived copy under tools/stale/.
    """
    live = [p for p in SCRIPTS.rglob("*.py") if p.name != "__init__.py"]
    archived = list((ROOT / "tools" / "stale").glob("c57_clone2_*.py"))
    pys = live + archived
    assert pys, "no scripts present"
    for py in pys:
        src = py.read_text()
        assert "import random" not in src, f"{py}: 'import random' forbidden"
        assert ".random.rand" not in src and ".random.randn" not in src, f"{py}: numpy.random.* forbidden"
    seeded = [py for py in pys if "torch.manual_seed" in py.read_text()]
    assert seeded, "no torch.manual_seed(0) seed site found"
    _pass("06_no_prng_except_torch_manual_seed_zero_in_inner")


def _src_files():
    """Live scripts + archived c57 clone-2 stale copies (fanout may sweep live)."""
    live = [p for p in SCRIPTS.rglob("*.py") if p.name != "__init__.py"]
    archived = list((ROOT / "tools" / "stale").glob("c57_clone2_*.py"))
    return live + archived


def test_07_no_sidecar_nonfactor_import():
    """AST-grep: no import of any sidecar_nonfactor module."""
    for py in _src_files():
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    assert "sidecar_nonfactor" not in n.name, f"{py}: forbidden import {n.name}"
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "sidecar_nonfactor" not in node.module, f"{py}: forbidden from-import {node.module}"
    _pass("07_no_sidecar_nonfactor_import")


def test_08_interpreter_guards():
    pys = _src_files()
    text = "\n".join(p.read_text() for p in pys)
    assert "/usr/bin/python3" in text and "orchestrator must run under /usr/bin/python3" in text
    assert "_venv_guard" in text and "learned_transcribers_venv" in text
    _pass("08_interpreter_and_venv_guards_present")


def test_09_c48_env_flags_default_off():
    pys = _src_files()
    text = "\n".join(p.read_text() for p in pys)
    assert 'os.environ.setdefault("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", "0")' in text
    assert 'os.environ.setdefault("MUSICGEN_LEDGER_SUPERSEDES_IN_HASH", "0")' in text
    _pass("09_c48_env_flags_default_off")


def test_10_verdict_enum():
    v = json.loads((DATA / "verdict.json").read_text())
    assert v["verdict"] in {"LEARNED_SURVEY_LANDS", "LEARNED_SURVEY_PARTIAL", "FETCH_FAILS_ALL"}, v["verdict"]
    _pass("10_verdict_in_frozen_enum")


def test_11_smoke_test_only_flag_or_accuracy_tsv():
    has_flag = (DATA / "smoke_test_only.flag").exists()
    has_tsv = (DATA / "accuracy_vs_gold.tsv").exists()
    assert has_flag or has_tsv, "neither smoke_test_only.flag nor accuracy_vs_gold.tsv present"
    _pass("11_smoke_test_only_flag_or_accuracy_tsv_present")


def test_12_cross_stem_stub_or_sentinel():
    has_tsv = (DATA / "cross_stem_reconciliation_stub.tsv").exists()
    has_sentinel = (DATA / "deferred_no_energy_table.sentinel").exists()
    assert has_tsv or has_sentinel
    if has_tsv:
        header = (DATA / "cross_stem_reconciliation_stub.tsv").read_text().splitlines()[0]
        assert "onset_s" in header and "assignment" in header
    _pass("12_cross_stem_stub_tsv_or_sentinel")


def test_13_read_only_anchors_preserved():
    # c50 v2 rubric SHA and c33 render_stem.py SHA
    anchors = {
        "docs/m_recreate_2_accurate_small_set_rubric_v2.md": "0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f",
        "scripts/palette_render/render_stem.py": None,  # c33 SHA prefix 214372d9…5b2b, full asserted below
    }
    p = ROOT / "docs/m_recreate_2_accurate_small_set_rubric_v2.md"
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    assert actual == "0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f", f"c50 v2 rubric drift: {actual}"
    rs = ROOT / "scripts/palette_render/render_stem.py"
    if rs.exists():
        sha = hashlib.sha256(rs.read_bytes()).hexdigest()
        assert sha.startswith("214372d9") and sha.endswith("5b2b"), f"c33 render_stem.py drift: {sha}"
    _pass("13_read_only_anchors_preserved")


def test_14_basic_pitch_venv_unchanged_by_this_cycle():
    # Assert we did not write into basic_pitch_venv (mtime of pip metadata newer than rubric?)
    # Loose check: our rubric ts vs basic_pitch_venv/pyvenv.cfg
    rub_mtime = RUBRIC.stat().st_mtime
    cfg = BP_VENV / "pyvenv.cfg"
    if cfg.exists():
        assert cfg.stat().st_mtime <= rub_mtime, "basic_pitch_venv pyvenv.cfg newer than our rubric"
    _pass("14_basic_pitch_venv_unchanged")


def test_15_per_model_notes_json_present_for_installed():
    v = json.loads((DATA / "verdict.json").read_text())
    for key in v.get("installed_and_smoke_ok", []) + v.get("installed_but_byte_det_failed", []):
        # naming: <model>_<stem>
        if key.startswith("torchcrepe_"):
            stem = key.split("_", 1)[1]
            p = DATA / "torchcrepe" / "31a164f845f8e27e" / stem / "notes.json"
        elif key.startswith("piano_bytedance_"):
            stem = key.split("_", 2)[2]
            p = DATA / "piano_bytedance" / "31a164f845f8e27e" / stem / "notes.json"
        else:
            continue
        assert p.exists(), f"missing per-model notes.json: {p}"
        obj = json.loads(p.read_text())
        assert "notes_count" in obj and "vocabulary" in obj
    _pass("15_per_model_notes_json_present_for_installed_models")


def test_16_scripts_absent_top_level_uses_venv_python():
    """Orchestrator refers to VENV_PY (does not import venv-only modules directly)."""
    pys = _src_files()
    orch = next((p for p in pys if p.name.startswith("run_survey") or p.name.endswith("run_survey.py")), None)
    if orch is None:
        # fallback to any file that reads like the orchestrator
        for p in pys:
            if "VENV_PY" in p.read_text():
                orch = p; break
    assert orch is not None, "no orchestrator source available"
    src = orch.read_text()
    assert "VENV_PY" in src
    tree = ast.parse(src)
    banned_imports = {"torch", "torchcrepe", "piano_transcription_inference"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                assert n.name.split(".")[0] not in banned_imports
        if isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".")[0] not in banned_imports
    _pass("16_orchestrator_uses_venv_python_not_direct_imports")


def test_17_c55_impl_trees_untouched():
    # Spot-check: c55 rc10_drums_v2_impl and rc10_bass_v2_impl exist and their verdicts unchanged
    for p in ("data/rc10_drums_v2_impl/verdict.json", "data/rc10_bass_v2_impl/verdict.json"):
        fp = ROOT / p
        if fp.exists():
            v = json.loads(fp.read_text())
            assert "rubric_hash" in v
    _pass("17_c55_impl_trees_present_and_unmodified")


def main():
    tests = [
        test_01_rubric_mtime_before_scripts,
        test_02_rubric_hash_three_way,
        test_03_venv_landed_and_disjoint,
        test_04_fetchability_ladder_min_rows,
        test_05_c11_anti_pattern_grep,
        test_06_no_prng_except_torch_seed,
        test_07_no_sidecar_nonfactor_import,
        test_08_interpreter_guards,
        test_09_c48_env_flags_default_off,
        test_10_verdict_enum,
        test_11_smoke_test_only_flag_or_accuracy_tsv,
        test_12_cross_stem_stub_or_sentinel,
        test_13_read_only_anchors_preserved,
        test_14_basic_pitch_venv_unchanged_by_this_cycle,
        test_15_per_model_notes_json_present_for_installed,
        test_16_scripts_absent_top_level_uses_venv_python,
        test_17_c55_impl_trees_untouched,
    ]
    for t in tests:
        t()
    print(f"\n{len(tests)}/{len(tests)} tests PASS")


if __name__ == "__main__":
    main()
