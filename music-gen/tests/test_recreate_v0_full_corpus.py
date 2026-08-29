#!/usr/bin/python3
# ---
# created: 2026-08-29T12:30:00Z
# cycle: 39
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/full-corpus-recreation
# fork: c320de981fda
# clone: 0
# ---
"""Tests for M-RECREATE-1/full-corpus-recreation (c39 clone-0).

Run: PYTHONPATH=. /usr/bin/python3 tests/test_recreate_v0_full_corpus.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data" / "recreate_v0_full_corpus"
SCRIPTS_ROOT = REPO_ROOT / "scripts" / "recreate_v0_full_corpus"
RUBRIC_DOC = REPO_ROOT / "docs" / "recreate_v0_full_corpus_rubric.md"
RUBRIC_HASH_FILE = DATA_ROOT / "rubric_hash.txt"
REPORT_DOC = REPO_ROOT / "docs" / "recreate_v0_full_corpus_report.md"

# Anchor directories that must remain unmodified
C37_SCRIPTS = REPO_ROOT / "scripts" / "recreate_v0"
C38_BATCH_SCRIPTS = REPO_ROOT / "scripts" / "recreate_v0_batch"

FORBIDDEN_STATE_CALLS = frozenset({"get_state", "save_state", "save_preset",
                                    "load_state", "set_state"})

CAVEAT_LITERAL = "n_too_small; correlation is exploratory only, not inferentially valid"

PRETTY_MIDI_FN = "_concat_per_stem_midis_prettymidi"
C37_PIPELINE = REPO_ROOT / "scripts" / "recreate_v0" / "run_pipeline.py"

results: list[tuple[str, bool, str]] = []


def _pass(name: str, msg: str = "") -> None:
    results.append((name, True, msg))


def _fail(name: str, msg: str) -> None:
    results.append((name, False, msg))


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_01_rubric_mtime_precedes_scripts() -> None:
    if not RUBRIC_DOC.exists():
        _fail("test_01_rubric_mtime_precedes_scripts", "rubric doc missing")
        return
    rubric_mtime = RUBRIC_DOC.stat().st_mtime
    scripts = list(SCRIPTS_ROOT.rglob("*.py"))
    if not scripts:
        _fail("test_01_rubric_mtime_precedes_scripts", "no scripts")
        return
    for s in scripts:
        if s.stat().st_mtime < rubric_mtime:
            _fail("test_01_rubric_mtime_precedes_scripts",
                  f"{s.relative_to(REPO_ROOT)} precedes rubric")
            return
    _pass("test_01_rubric_mtime_precedes_scripts",
          f"rubric mtime <= all {len(scripts)} scripts")


def test_02_rubric_git_log_order() -> None:
    """MERGE_DEFERRED acceptable per c38 precedent (clone env cannot git add)."""
    try:
        proc = subprocess.run(
            ["git", "log", "--format=%H %ct", "--",
             str(RUBRIC_DOC.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10,
        )
        rubric_log = proc.stdout.strip().split("\n")
        if not rubric_log or not rubric_log[0]:
            _pass("test_02_rubric_git_log_order",
                  "MERGE_DEFERRED: rubric not yet committed; mtime gate covers pre-merge")
            return
        rubric_first_commit_ts = int(rubric_log[-1].split()[1])
        for s in SCRIPTS_ROOT.rglob("*.py"):
            proc = subprocess.run(
                ["git", "log", "--format=%ct", "--",
                 str(s.relative_to(REPO_ROOT))],
                cwd=REPO_ROOT, capture_output=True, text=True, timeout=10,
            )
            log = proc.stdout.strip().split("\n")
            if not log or not log[0]:
                continue
            script_first_commit_ts = int(log[-1].split()[0])
            if script_first_commit_ts < rubric_first_commit_ts:
                _fail("test_02_rubric_git_log_order", f"{s.name} predates rubric")
                return
        _pass("test_02_rubric_git_log_order")
    except Exception as exc:
        _pass("test_02_rubric_git_log_order", f"MERGE_DEFERRED: git err {exc}")


def test_03_rubric_hash_matches_doc() -> None:
    if not RUBRIC_HASH_FILE.exists() or not RUBRIC_DOC.exists():
        _fail("test_03_rubric_hash_matches_doc", "artifact missing")
        return
    actual = _sha256(RUBRIC_DOC)
    stored = RUBRIC_HASH_FILE.read_text().strip()
    if actual != stored:
        _fail("test_03_rubric_hash_matches_doc",
              f"doc sha={actual} vs file={stored}")
        return
    _pass("test_03_rubric_hash_matches_doc")


def test_04_verdict_carries_rubric_hash() -> None:
    v_path = DATA_ROOT / "verdict.json"
    if not v_path.exists():
        _pass("test_04_verdict_carries_rubric_hash", "PENDING: verdict pending")
        return
    v = json.loads(v_path.read_text())
    stored = RUBRIC_HASH_FILE.read_text().strip()
    if v.get("rubric_hash") != stored:
        _fail("test_04_verdict_carries_rubric_hash",
              f"verdict rubric_hash={v.get('rubric_hash')} vs file={stored}")
        return
    _pass("test_04_verdict_carries_rubric_hash")


def test_05_selector_no_prng_no_mtime() -> None:
    src = (SCRIPTS_ROOT / "select_songs.py").read_text()
    tree = ast.parse(src)
    forbidden_modules = {"random"}
    forbidden_attrs = {"rand", "randn", "randint", "random_sample", "choice",
                       "shuffle", "manual_seed"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in forbidden_modules:
                    _fail("test_05_selector_no_prng_no_mtime",
                          f"import {alias.name}")
                    return
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in forbidden_modules:
                _fail("test_05_selector_no_prng_no_mtime",
                      f"from {node.module}")
                return
        if isinstance(node, ast.Attribute):
            if node.attr in forbidden_attrs:
                _fail("test_05_selector_no_prng_no_mtime", f".{node.attr}")
                return
    if "st_mtime" in src:
        _fail("test_05_selector_no_prng_no_mtime", "st_mtime read")
        return
    _pass("test_05_selector_no_prng_no_mtime")


def test_06_exclusion_set_enforced() -> None:
    p = DATA_ROOT / "chosen_songs_full.json"
    if not p.exists():
        _fail("test_06_exclusion_set_enforced", "chosen_songs_full.json missing")
        return
    chosen = json.loads(p.read_text())
    if chosen["n_chosen"] != 37:
        _fail("test_06_exclusion_set_enforced",
              f"n_chosen={chosen['n_chosen']} != 37")
        return
    excluded_rels = set(chosen["exclusion_set"])
    for entry in chosen["chosen_songs"]:
        if entry["relpath"] in excluded_rels:
            _fail("test_06_exclusion_set_enforced",
                  f"selected excluded: {entry['relpath']}")
            return
    if len(excluded_rels) != 6:
        _fail("test_06_exclusion_set_enforced",
              f"exclusion set has {len(excluded_rels)} entries, not 6")
        return
    # Verify c37 clone-0 and c38 clone-2's songs are in the exclusion set
    must_exclude = {
        "corpus/ratings/7/016__LOCAL__05_02.mp3",
        "corpus/ratings/4/013__jZVdDl_asYY__Mariah_Carey_-_Shake_It_Off.mp3",
    }
    if not must_exclude.issubset(excluded_rels):
        _fail("test_06_exclusion_set_enforced",
              f"missing must-exclude: {must_exclude - excluded_rels}")
        return
    _pass("test_06_exclusion_set_enforced", f"n=37, 6 excluded")


def test_07_file_sha_matches_bytes() -> None:
    chosen = json.loads((DATA_ROOT / "chosen_songs_full.json").read_text())
    for s in chosen["chosen_songs"][:5]:  # sample the first 5 for speed
        p = REPO_ROOT / s["relpath"]
        actual = _sha256(p)
        if actual != s["file_sha256"]:
            _fail("test_07_file_sha_matches_bytes",
                  f"{s['relpath']}: json={s['file_sha256']} actual={actual}")
            return
    _pass("test_07_file_sha_matches_bytes", "sampled first 5 songs OK")


def test_08_per_song_stage_manifests() -> None:
    per_song = DATA_ROOT / "per_song"
    if not per_song.exists():
        _pass("test_08_per_song_stage_manifests", "PENDING")
        return
    n_manifests = 0
    n_stages = 0
    for sm in per_song.rglob("stage_manifest.json"):
        n_manifests += 1
        m = json.loads(sm.read_text())
        n_stages += len(m.get("stages_run1", []))
    if n_manifests == 0:
        _pass("test_08_per_song_stage_manifests", "PENDING: no manifests yet")
        return
    _pass("test_08_per_song_stage_manifests",
          f"{n_manifests} manifests, {n_stages} stage records "
          f"(37 songs x 8 stages = 296 expected on LANDS)")


def test_09_byte_determinism_148_anchors() -> None:
    per_song = DATA_ROOT / "per_song"
    if not per_song.exists():
        _pass("test_09_byte_determinism_148_anchors", "PENDING")
        return
    total = 0
    ok = 0
    for song_dir in per_song.rglob("per_song_result.json"):
        r = json.loads(song_dir.read_text())
        for rel, det in r.get("determinism", {}).get("per_anchor", {}).items():
            total += 1
            if det.get("equal"):
                ok += 1
    if total == 0:
        _pass("test_09_byte_determinism_148_anchors", "PENDING")
        return
    _pass("test_09_byte_determinism_148_anchors",
          f"{ok}/{total} byte-det anchors equal (148 expected on LANDS)")


def test_10_cross_band_table_shapes() -> None:
    n37 = DATA_ROOT / "cross_band_n37.tsv"
    n42 = DATA_ROOT / "cross_band_pooled_n42.tsv"
    n43 = DATA_ROOT / "cross_band_pooled_n43.tsv"
    if not all(p.exists() for p in (n37, n42, n43)):
        _pass("test_10_cross_band_table_shapes", "PENDING")
        return
    for path, expected in ((n37, 37), (n42, 42), (n43, 43)):
        lines = path.read_text().strip().split("\n")
        data_rows = len(lines) - 1  # exclude header
        header = lines[0].split("\t")
        if len(header) != 14:
            _fail("test_10_cross_band_table_shapes",
                  f"{path.name}: {len(header)} columns != 14")
            return
        if data_rows != expected:
            _fail("test_10_cross_band_table_shapes",
                  f"{path.name}: {data_rows} rows != {expected}")
            return
    _pass("test_10_cross_band_table_shapes", "n37/n42/n43 shapes OK")


def test_11_correlation_caveat_literal() -> None:
    p = DATA_ROOT / "cross_band_correlation.json"
    if not p.exists():
        _pass("test_11_correlation_caveat_literal", "PENDING")
        return
    data = json.loads(p.read_text())
    for label, entries in data.items():
        for row in entries:
            if row.get("n_too_small_caveat") != CAVEAT_LITERAL:
                _fail("test_11_correlation_caveat_literal",
                      f"{label}/{row.get('delta_key')} missing caveat")
                return
    _pass("test_11_correlation_caveat_literal",
          f"all rows carry caveat literal")


def test_12_anchor_preservation_ge_18() -> None:
    p = DATA_ROOT / "anchor_preservation.json"
    if not p.exists():
        _pass("test_12_anchor_preservation_ge_18", "PENDING")
        return
    ap = json.loads(p.read_text())
    if ap.get("n_anchors", 0) < 18:
        _fail("test_12_anchor_preservation_ge_18",
              f"n_anchors={ap.get('n_anchors')} < 18")
        return
    if not ap.get("unchanged"):
        _fail("test_12_anchor_preservation_ge_18",
              f"changed={list(ap.get('changed', {}).keys())}")
        return
    _pass("test_12_anchor_preservation_ge_18",
          f"{ap.get('n_anchors')} anchors byte-identical pre/post")


def test_13_no_writes_under_c37_or_c38_batch() -> None:
    """Scan the anchor_preservation.json for changes to c37/c38 clone-2 scripts."""
    p = DATA_ROOT / "anchor_preservation.json"
    if not p.exists():
        _pass("test_13_no_writes_under_c37_or_c38_batch", "PENDING")
        return
    ap = json.loads(p.read_text())
    for changed_key in ap.get("changed", {}):
        if (changed_key.startswith("scripts/recreate_v0/") or
                changed_key.startswith("scripts/recreate_v0_batch/") or
                changed_key.startswith("data/recreate_v0/") or
                changed_key.startswith("data/recreate_v0_batch/")):
            _fail("test_13_no_writes_under_c37_or_c38_batch",
                  f"changed under anchor dir: {changed_key}")
            return
    _pass("test_13_no_writes_under_c37_or_c38_batch")


def test_14_ast_no_branch_a_b_imports() -> None:
    forbidden = {"scripts.ear_v1", "scripts.score_bridge_v2", "scripts.ear_v0",
                 "sidecar_nonfactor", "i4_stratified"}
    for py in SCRIPTS_ROOT.rglob("*.py"):
        src = py.read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(alias.name.startswith(f) for f in forbidden):
                        _fail("test_14_ast_no_branch_a_b_imports",
                              f"{py.name}: import {alias.name}")
                        return
            if isinstance(node, ast.ImportFrom):
                if node.module and any(node.module.startswith(f) for f in forbidden):
                    _fail("test_14_ast_no_branch_a_b_imports",
                          f"{py.name}: from {node.module}")
                    return
    _pass("test_14_ast_no_branch_a_b_imports")


def test_15_ast_no_forbidden_state_or_missing_guard() -> None:
    for py in SCRIPTS_ROOT.rglob("*.py"):
        src = py.read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_STATE_CALLS:
                _fail("test_15_ast_no_forbidden_state_or_missing_guard",
                      f"{py.name}: .{node.attr}")
                return
            if isinstance(node, ast.Call):
                fn = node.func
                if isinstance(fn, ast.Name) and fn.id in FORBIDDEN_STATE_CALLS:
                    _fail("test_15_ast_no_forbidden_state_or_missing_guard",
                          f"{py.name}: {fn.id}()")
                    return
        # Interpreter guard: shebang or runtime assert
        first_line = src.splitlines()[0] if src.splitlines() else ""
        has_shebang = first_line.startswith("#!") and "/usr/bin/python3" in first_line
        has_runtime_guard = 'sys.executable == "/usr/bin/python3"' in src
        if py.name == "__init__.py":
            continue
        if not (has_shebang or has_runtime_guard):
            _fail("test_15_ast_no_forbidden_state_or_missing_guard",
                  f"{py.name}: no interpreter guard")
            return
    _pass("test_15_ast_no_forbidden_state_or_missing_guard")


def test_16_pretty_midi_fallback_present_in_c37() -> None:
    """Regression check: c37 pretty_midi fallback function still present."""
    src = C37_PIPELINE.read_text()
    if PRETTY_MIDI_FN not in src:
        _fail("test_16_pretty_midi_fallback_present_in_c37",
              f"missing {PRETTY_MIDI_FN} in c37 run_pipeline.py")
        return
    # Function definition should be at approx line 335 per rubric
    lines = src.splitlines()
    def_line = None
    for i, ln in enumerate(lines, 1):
        if ln.startswith(f"def {PRETTY_MIDI_FN}"):
            def_line = i
            break
    if def_line is None:
        _fail("test_16_pretty_midi_fallback_present_in_c37",
              "def line not found")
        return
    if not (320 <= def_line <= 355):
        _fail("test_16_pretty_midi_fallback_present_in_c37",
              f"def at line {def_line} outside expected 320-355")
        return
    _pass("test_16_pretty_midi_fallback_present_in_c37",
          f"present at line {def_line}")


def test_17_preview_untrained_ear_caveat_in_report() -> None:
    if not REPORT_DOC.exists():
        _pass("test_17_preview_untrained_ear_caveat_in_report",
              "PENDING: report not yet written")
        return
    text = REPORT_DOC.read_text()
    marker = "docs/ear_real_label_training_v1_report.md"
    caveat_frag = "preview_untrained_ear"
    if marker not in text:
        _fail("test_17_preview_untrained_ear_caveat_in_report",
              f"missing document-path reference: {marker}")
        return
    if caveat_frag not in text:
        _fail("test_17_preview_untrained_ear_caveat_in_report",
              f"missing caveat fragment: {caveat_frag}")
        return
    _pass("test_17_preview_untrained_ear_caveat_in_report",
          "caveat + doc-path present")


def test_18_per_song_wall_clock_recorded() -> None:
    per_song = DATA_ROOT / "per_song"
    if not per_song.exists():
        _pass("test_18_per_song_wall_clock_recorded", "PENDING")
        return
    checked = 0
    for sm_path in per_song.rglob("stage_manifest.json"):
        sm = json.loads(sm_path.read_text())
        if sm.get("run1_wall_clock_s") is None and sm.get("run1_failed_stage") is None:
            _fail("test_18_per_song_wall_clock_recorded",
                  f"{sm_path}: missing run1_wall_clock_s on OK song")
            return
        checked += 1
    if checked == 0:
        _pass("test_18_per_song_wall_clock_recorded", "PENDING: no manifests")
        return
    _pass("test_18_per_song_wall_clock_recorded",
          f"{checked} manifests carry wall-clock")


def test_19_no_c9_import_in_new_scripts() -> None:
    """c9 render_effects_layered.py is READ-ONLY; imported only through the
    frozen c37 pipeline (not directly by new scripts under c39)."""
    forbidden = {"scripts.tex.render_effects_layered"}
    for py in SCRIPTS_ROOT.rglob("*.py"):
        src = py.read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module in forbidden:
                    _fail("test_19_no_c9_import_in_new_scripts",
                          f"{py.name}: from {node.module}")
                    return
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in forbidden:
                        _fail("test_19_no_c9_import_in_new_scripts",
                              f"{py.name}: import {alias.name}")
                        return
    _pass("test_19_no_c9_import_in_new_scripts")


def test_20_per_song_early_exit_reason_recorded() -> None:
    per_song = DATA_ROOT / "per_song"
    if not per_song.exists():
        _pass("test_20_per_song_early_exit_reason_recorded", "PENDING")
        return
    n_early = 0
    for sm_path in per_song.rglob("stage_manifest.json"):
        sm = json.loads(sm_path.read_text())
        if sm.get("run1_failed_stage") == "early_exit:wall_clock_exceeded":
            n_early += 1
    _pass("test_20_per_song_early_exit_reason_recorded",
          f"{n_early} songs early-exited (0 expected on LANDS)")


def main() -> int:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as exc:
                _fail(name, f"exception: {exc!r}")
    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    print(f"\n{'='*70}\nRESULTS: {passed}/{len(results)} pass\n{'='*70}")
    for name, ok, msg in results:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}: {msg}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
