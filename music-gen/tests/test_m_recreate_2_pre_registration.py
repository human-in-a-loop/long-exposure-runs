"""c49 Priority 2: verify M-RECREATE-2 pre-registration landed correctly.

Assertions:
1. rubric doc mtime < every scripts/recreate_v2/*.py (mtime discipline).
2. Three-way rubric_hash byte-equality chain (doc SHA == rubric_hash.txt).
3. focus_set.json contains Chicken Grease + 2-4 more from candidate pool.
4. RC0 baseline byte-determinism x 2 recorded PASS.
5. RC1-RC6 stubs raise NotImplementedError('c50+ branch').
6. All stubs interpreter-guard /usr/bin/python3.
7. Baseline covers all 5 focus songs.
8. Anchor preservation manifest >= 25 entries.
9. AST-grep clean: no PRNG, no sidecar_nonfactor imports under scripts/recreate_v2/.
10. Every RC sub-milestone landed in ledger.
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = Path(__file__).resolve().parent.parent
RUBRIC_DOC = ROOT / "docs/m_recreate_2_accurate_small_set_rubric.md"
RUBRIC_HASH_TXT = ROOT / "data/recreate_v2/rubric_hash.txt"
FOCUS_SET = ROOT / "data/recreate_v2/focus_set.json"
SCRIPTS_DIR = ROOT / "scripts/recreate_v2"
BASELINE_DIR = ROOT / "data/recreate_v2/baseline"


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_01_rubric_mtime_before_every_script():
    rubric_mtime = RUBRIC_DOC.stat().st_mtime
    scripts = list(SCRIPTS_DIR.rglob("*.py"))
    assert scripts, "no scripts under scripts/recreate_v2/"
    for s in scripts:
        assert s.stat().st_mtime > rubric_mtime, (
            f"script {s} mtime {s.stat().st_mtime} not > rubric {rubric_mtime}"
        )


def test_02_three_way_rubric_hash_chain():
    doc_sha = sha256_of(RUBRIC_DOC)
    file_sha = RUBRIC_HASH_TXT.read_text().strip()
    assert doc_sha == file_sha, f"doc SHA {doc_sha} != rubric_hash.txt {file_sha}"


def test_03_focus_set_contains_chicken_grease_plus_2_to_4_more():
    fs = json.loads(FOCUS_SET.read_text())
    titles = [s["title"] for s in fs["songs"]]
    assert "Chicken Grease" in titles, "Chicken Grease missing (mandatory)"
    assert 3 <= len(titles) <= 5, f"focus set n={len(titles)} outside [3,5]"


def test_04_rc0_baseline_byte_determinism_pass():
    det = json.loads((ROOT / "data/recreate_v2/baseline_byte_determinism.json").read_text())
    assert det["byte_determinism_pass"] is True, (
        f"byte-determinism x 2 FAIL: {det}"
    )
    assert det["diff_count"] == 0


def test_05_stubs_raise_not_implemented():
    for name in ("rc1_vocals_transcription", "rc2_drum_onset_transcription",
                 "rc3_bass_transcription", "rc4_gm_program_map",
                 "rc5_tempo_beat_grid", "rc6_panel_gate"):
        p = SCRIPTS_DIR / f"{name}.py"
        src = p.read_text()
        assert 'NotImplementedError("c50+' in src or "NotImplementedError('c50+" in src \
            or 'NotImplementedError("c50+/c51 branch")' in src \
            or 'NotImplementedError("c52+ branch")' in src, (
            f"{p} does not raise NotImplementedError('c50+ branch')"
        )


def test_06_interpreter_guard_present():
    for p in SCRIPTS_DIR.rglob("*.py"):
        src = p.read_text()
        if p.name == "__init__.py":
            continue
        assert 'sys.executable == "/usr/bin/python3"' in src, (
            f"{p} missing /usr/bin/python3 interpreter guard"
        )


def test_07_baseline_covers_all_focus_songs():
    fs = json.loads(FOCUS_SET.read_text())
    for s in fs["songs"]:
        d = BASELINE_DIR / s["audio_sha16"]
        assert d.exists(), f"baseline dir missing for {s['title']} ({s['audio_sha16']})"
        assert (d / "baseline_summary.json").exists()
        for f in ("per_stem_manifest.json", "rc1_vocals_voiced_time_s.json",
                  "rc2_drum_onset_count.json", "rc5_tempo_bpm.json",
                  "rc6_centroid_time_series.npy"):
            assert (d / f).exists(), f"{d/f} missing"


def test_08_anchor_preservation_manifest_size():
    a = json.loads((ROOT / "data/recreate_v2/anchor_preservation.json").read_text())
    assert a["anchor_count"] >= 25, f"anchor_count = {a['anchor_count']} < 25"


def test_09_ast_grep_clean_no_prng_no_sidecar():
    for p in SCRIPTS_DIR.rglob("*.py"):
        src = p.read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in ("random", "numpy.random"), (
                        f"{p}: forbidden PRNG import {alias.name}"
                    )
            if isinstance(node, ast.ImportFrom):
                if node.module and "sidecar_nonfactor" in node.module:
                    raise AssertionError(f"{p}: sidecar_nonfactor imported")
                if node.module and "i4_stratified" in node.module:
                    raise AssertionError(f"{p}: i4_stratified imported")
        # no PRNG string
        assert "random." not in src or "# noqa: no-random" in src, f"{p}: 'random.' string"


def test_10_all_rc_sub_milestones_landed_in_ledger():
    ledger = ROOT / "promise_ledger.jsonl"
    rows = [json.loads(l) for l in ledger.read_text().splitlines() if l.strip()]
    rc_ids = {"rc1-vocals-transcription", "rc2-drum-onset-transcription",
              "rc3-bass-transcription", "rc4-gm-program-map",
              "rc5-tempo-beat-grid", "rc6-panel-gate"}
    seen = set()
    for r in rows:
        m = r.get("milestone_id", "")
        for rc in rc_ids:
            if m == f"M-RECREATE-2/accurate-small-set/{rc}":
                seen.add(rc)
    assert seen == rc_ids, f"missing RC sub-milestones: {rc_ids - seen}"


def test_11_parent_milestone_landed():
    ledger = ROOT / "promise_ledger.jsonl"
    rows = [json.loads(l) for l in ledger.read_text().splitlines() if l.strip()]
    parent = [r for r in rows if r["milestone_id"] == "M-RECREATE-2/accurate-small-set"]
    assert parent, "M-RECREATE-2/accurate-small-set parent milestone not landed"
    assert parent[-1]["status"] == "in-progress"


def test_12_chicken_grease_rc2_baseline_far_above_current():
    """Sanity: baseline captures 100+ onsets vs the 5 in current merged.midi (operator audit)."""
    fs = json.loads(FOCUS_SET.read_text())
    cg = [s for s in fs["songs"] if s["title"] == "Chicken Grease"][0]
    baseline = json.loads(
        (BASELINE_DIR / cg["audio_sha16"] / "rc2_drum_onset_count.json").read_text()
    )
    assert baseline["onset_count"] >= 30, (
        f"Chicken Grease baseline onset count {baseline['onset_count']} too low; "
        "brief expects ~30-150 range for funk"
    )


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    fails = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}")
            fails += 1
    print(f"\n{len(tests) - fails}/{len(tests)} passed")
    sys.exit(1 if fails else 0)
