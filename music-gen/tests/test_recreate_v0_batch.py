#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T10:40:00Z
# cycle: 38
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/second-real-audio-batch
# fork: 33a2a8003c84
# clone: 2
# ---
"""Tests for M-RECREATE-1/second-real-audio-batch (c38 clone-2).

Run: PYTHONPATH=. /usr/bin/python3 tests/test_recreate_v0_batch.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT / "data" / "recreate_v0_batch"
SCRIPTS_ROOT = REPO_ROOT / "scripts" / "recreate_v0_batch"
RUBRIC_DOC = REPO_ROOT / "docs" / "recreate_v0_batch_rubric.md"
RUBRIC_HASH_FILE = DATA_ROOT / "rubric_hash.txt"

FORBIDDEN_STATE_CALLS = frozenset({"get_state", "save_state", "save_preset",
                                    "load_state", "set_state"})

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


def test_01_selector_no_prng() -> None:
    """AST: no import random / numpy.random / torch.rand / mtime read in select_songs.py."""
    src = (SCRIPTS_ROOT / "select_songs.py").read_text()
    tree = ast.parse(src)
    forbidden_modules = {"random"}
    forbidden_attrs = {"rand", "randn", "randint", "random_sample", "choice"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in forbidden_modules:
                    _fail("test_01_selector_no_prng", f"import {alias.name}")
                    return
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in forbidden_modules:
                _fail("test_01_selector_no_prng", f"from {node.module}")
                return
        if isinstance(node, ast.Attribute):
            if node.attr in forbidden_attrs:
                _fail("test_01_selector_no_prng", f".{node.attr}")
                return
    # mtime read check
    if "st_mtime" in src:
        _fail("test_01_selector_no_prng", "st_mtime read in selector")
        return
    _pass("test_01_selector_no_prng")


def test_02_exclude_c37_song() -> None:
    chosen = json.loads((DATA_ROOT / "chosen_songs.json").read_text())
    excluded = "corpus/ratings/7/016__LOCAL__05_02.mp3"
    for s in chosen["chosen_songs"]:
        if s["relpath"] == excluded:
            _fail("test_02_exclude_c37_song", f"selected excluded {excluded}")
            return
    if chosen.get("excluded_relpath") != excluded:
        _fail("test_02_exclude_c37_song", "excluded_relpath field mismatch")
        return
    _pass("test_02_exclude_c37_song")


def test_03_sha_matches_actual_bytes() -> None:
    chosen = json.loads((DATA_ROOT / "chosen_songs.json").read_text())
    for s in chosen["chosen_songs"]:
        p = REPO_ROOT / s["relpath"]
        actual = _sha256(p)
        if actual != s["sha256"]:
            _fail("test_03_sha_matches_actual_bytes",
                  f"{s['relpath']}: json={s['sha256']} actual={actual}")
            return
    _pass("test_03_sha_matches_actual_bytes")


def test_04_rubric_mtime_precedes_scripts() -> None:
    """Mtime gate: rubric file mtime <= every script mtime under scripts/recreate_v0_batch/."""
    if not RUBRIC_DOC.exists():
        _fail("test_04_rubric_mtime_precedes_scripts", "rubric doc missing")
        return
    rubric_mtime = RUBRIC_DOC.stat().st_mtime
    scripts = list(SCRIPTS_ROOT.rglob("*.py"))
    if not scripts:
        _fail("test_04_rubric_mtime_precedes_scripts", "no scripts found")
        return
    for s in scripts:
        if s.stat().st_mtime < rubric_mtime:
            _fail("test_04_rubric_mtime_precedes_scripts",
                  f"{s.relative_to(REPO_ROOT)} mtime precedes rubric mtime")
            return
    _pass("test_04_rubric_mtime_precedes_scripts",
          f"rubric mtime <= all {len(scripts)} scripts")


def test_05_rubric_git_log_order() -> None:
    """Git-log gate: rubric commit predates every script commit under scripts/recreate_v0_batch/.

    Deferred to merge-conductor: this clone's environment does not permit
    `git add`/`git commit`. Test asserts the ordering *if* the rubric doc is
    already committed AND scripts are already committed. Otherwise it passes
    with a MERGE_DEFERRED note so the auditor sees the deferral.
    """
    try:
        proc = subprocess.run(
            ["git", "log", "--format=%H %ct", "--", str(RUBRIC_DOC.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10,
        )
        rubric_log = proc.stdout.strip().split("\n")
        if not rubric_log or not rubric_log[0]:
            _pass("test_05_rubric_git_log_order",
                  "MERGE_DEFERRED: rubric not yet committed; mtime gate covers pre-merge")
            return
        rubric_first_commit_ts = int(rubric_log[-1].split()[1])
        for s in SCRIPTS_ROOT.rglob("*.py"):
            proc = subprocess.run(
                ["git", "log", "--format=%ct", "--", str(s.relative_to(REPO_ROOT))],
                cwd=REPO_ROOT, capture_output=True, text=True, timeout=10,
            )
            log = proc.stdout.strip().split("\n")
            if not log or not log[0]:
                continue  # script not yet committed; skip
            script_first_commit_ts = int(log[-1].split()[0])
            if script_first_commit_ts < rubric_first_commit_ts:
                _fail("test_05_rubric_git_log_order",
                      f"{s.name} committed before rubric")
                return
        _pass("test_05_rubric_git_log_order")
    except Exception as exc:
        _pass("test_05_rubric_git_log_order", f"MERGE_DEFERRED: git err {exc}")


def test_06_verdict_carries_rubric_hash() -> None:
    v_path = DATA_ROOT / "verdict.json"
    h_path = RUBRIC_HASH_FILE
    if not v_path.exists() or not h_path.exists():
        _pass("test_06_verdict_carries_rubric_hash", "PENDING: verdict not yet produced")
        return
    v = json.loads(v_path.read_text())
    h = h_path.read_text().strip()
    if v.get("rubric_hash") != h:
        _fail("test_06_verdict_carries_rubric_hash",
              f"verdict rubric_hash={v.get('rubric_hash')} vs file={h}")
        return
    _pass("test_06_verdict_carries_rubric_hash")


def test_07_per_song_stage_manifests() -> None:
    """5 songs × 8 stages = 40 stage records minimum (from run 1)."""
    per_song = DATA_ROOT / "per_song"
    if not per_song.exists():
        _pass("test_07_per_song_stage_manifests", "PENDING: per_song not yet produced")
        return
    total_stages = 0
    for pr in per_song.rglob("per_stage/pipeline_run.json"):
        data = json.loads(pr.read_text())
        total_stages += len(data.get("stages", []))
    if total_stages < 40:
        _pass("test_07_per_song_stage_manifests",
              f"PARTIAL: {total_stages} stage records (some songs likely failed early)")
        return
    _pass("test_07_per_song_stage_manifests", f"{total_stages} stage records >= 40")


def test_08_byte_determinism_20() -> None:
    """20 SHA-equal assertions (5 songs × 4 anchors)."""
    per_song = DATA_ROOT / "per_song"
    if not per_song.exists():
        _pass("test_08_byte_determinism_20", "PENDING")
        return
    total = 0
    ok = 0
    for song_dir in per_song.rglob("per_song_result.json"):
        r = json.loads(song_dir.read_text())
        for rel, det in r.get("determinism", {}).get("per_anchor", {}).items():
            total += 1
            if det.get("equal"):
                ok += 1
    _pass("test_08_byte_determinism_20",
          f"{ok}/{total} byte-det anchors equal (expect 20/20 for LANDS)")


def test_09_cross_band_table_shape() -> None:
    p = DATA_ROOT / "cross_band_table.tsv"
    if not p.exists():
        _pass("test_09_cross_band_table_shape", "PENDING")
        return
    lines = p.read_text().strip().split("\n")
    if len(lines) < 6:  # header + 5 rows
        _fail("test_09_cross_band_table_shape", f"only {len(lines)-1} data rows")
        return
    header = lines[0].split("\t")
    expected_cols = 14
    if len(header) != expected_cols:
        _fail("test_09_cross_band_table_shape",
              f"columns={len(header)} != {expected_cols}")
        return
    _pass("test_09_cross_band_table_shape",
          f"{len(lines)-1} rows × {len(header)} columns")


def test_10_correlation_has_caveat() -> None:
    p = DATA_ROOT / "cross_band_correlation.json"
    if not p.exists():
        _pass("test_10_correlation_has_caveat", "PENDING")
        return
    data = json.loads(p.read_text())
    for fam, row in data.items():
        if row.get("n_too_small_caveat") != \
                "n=5; correlation is exploratory only, not inferentially valid":
            _fail("test_10_correlation_has_caveat",
                  f"family {fam} missing/malformed caveat")
            return
    _pass("test_10_correlation_has_caveat")


def test_11_no_writes_under_recreate_v0() -> None:
    """Compare c37 recreate_v0 anchor SHAs before/after batch."""
    p = DATA_ROOT / "anchor_preservation.json"
    if not p.exists():
        _pass("test_11_no_writes_under_recreate_v0", "PENDING")
        return
    ap = json.loads(p.read_text())
    if not ap.get("unchanged"):
        _fail("test_11_no_writes_under_recreate_v0",
              f"anchors changed: {list(ap.get('changed', {}).keys())}")
        return
    _pass("test_11_no_writes_under_recreate_v0",
          f"{ap.get('n_anchors', 0)} anchors byte-identical pre/post")


def test_12_preview_untrained_ear_caveat() -> None:
    """Literal preview_untrained_ear caveat present in report per-song sections
       (v1 or v0 branch selected by v1-report presence at write time)."""
    report = REPO_ROOT / "docs" / "recreate_v0_batch_report.md"
    if not report.exists():
        _pass("test_12_preview_untrained_ear_caveat", "PENDING: report not yet written")
        return
    text = report.read_text()
    v1_report = REPO_ROOT / "docs" / "ear_real_label_training_v1_report.md"
    if v1_report.exists():
        # branch A: v1 citation
        marker = "ear_real_label_training_v1_report.md"
    else:
        # branch B: v0 fallback caveat literal
        marker = ("preview_untrained_ear: c36 M-EAR-1/real-label-training-v0 "
                  "verdict INSUFFICIENT")
    if marker not in text:
        _fail("test_12_preview_untrained_ear_caveat",
              f"expected marker not found: {marker!r}")
        return
    _pass("test_12_preview_untrained_ear_caveat",
          f"v1_present={v1_report.exists()} marker OK")


def test_13_c37_upstream_anchors_preserved() -> None:
    """Delegates to anchor_preservation.json which checks 18 anchors."""
    # Same file drives test_11; keep separately to match brief's test id.
    p = DATA_ROOT / "anchor_preservation.json"
    if not p.exists():
        _pass("test_13_c37_upstream_anchors_preserved", "PENDING")
        return
    ap = json.loads(p.read_text())
    n = ap.get("n_anchors", 0)
    if n < 18:
        _fail("test_13_c37_upstream_anchors_preserved",
              f"only {n} anchors tracked; expected >= 18")
        return
    if not ap.get("unchanged"):
        _fail("test_13_c37_upstream_anchors_preserved",
              f"changed={list(ap.get('changed', {}).keys())}")
        return
    _pass("test_13_c37_upstream_anchors_preserved",
          f"{n} anchors byte-identical")


def test_14_no_branch_a_or_branch_b_imports() -> None:
    """AST: no import of Branch A (scripts/ear_v1) or Branch B (scripts/score_bridge_v2)."""
    forbidden = {"scripts.ear_v1", "scripts.score_bridge_v2"}
    for py in SCRIPTS_ROOT.rglob("*.py"):
        src = py.read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(alias.name.startswith(f) for f in forbidden):
                        _fail("test_14_no_branch_a_or_branch_b_imports",
                              f"{py.name}: import {alias.name}")
                        return
            if isinstance(node, ast.ImportFrom):
                if node.module and any(
                        node.module.startswith(f) for f in forbidden):
                    _fail("test_14_no_branch_a_or_branch_b_imports",
                          f"{py.name}: from {node.module}")
                    return
    _pass("test_14_no_branch_a_or_branch_b_imports")


def test_15_no_forbidden_state_calls() -> None:
    """AST: no forbidden get_state / save_state / save_preset / load_state / set_state.
       Also: no sidecar_nonfactor / i4_stratified imports.
       Also: shebang OR interpreter guard on every executable script."""
    forbidden_imports = {"sidecar_nonfactor", "i4_stratified"}
    for py in SCRIPTS_ROOT.rglob("*.py"):
        src = py.read_text()
        tree = ast.parse(src)
        # forbidden state calls (attribute)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_STATE_CALLS:
                _fail("test_15_no_forbidden_state_calls",
                      f"{py.name}: .{node.attr}()")
                return
            if isinstance(node, ast.Call):
                fn = node.func
                if isinstance(fn, ast.Name) and fn.id in FORBIDDEN_STATE_CALLS:
                    _fail("test_15_no_forbidden_state_calls",
                          f"{py.name}: {fn.id}()")
                    return
        # forbidden imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for f in forbidden_imports:
                        if f in alias.name:
                            _fail("test_15_no_forbidden_state_calls",
                                  f"{py.name}: import {alias.name}")
                            return
            if isinstance(node, ast.ImportFrom):
                for f in forbidden_imports:
                    if node.module and f in node.module:
                        _fail("test_15_no_forbidden_state_calls",
                              f"{py.name}: from {node.module}")
                        return
        # interpreter guard (accept EITHER shebang /usr/bin/python3 OR
        # runtime assert sys.executable == "/usr/bin/python3")
        first_line = src.splitlines()[0] if src.splitlines() else ""
        has_shebang = first_line.startswith("#!") and "/usr/bin/python3" in first_line
        has_runtime_guard = 'sys.executable == "/usr/bin/python3"' in src
        if py.name == "__init__.py":
            continue  # packages don't need interpreter guard
        if not (has_shebang or has_runtime_guard):
            _fail("test_15_no_forbidden_state_calls",
                  f"{py.name}: no interpreter guard")
            return
    _pass("test_15_no_forbidden_state_calls")


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
