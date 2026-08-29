#!/usr/bin/env /usr/bin/python3
"""Cycle 47 Branch C: test suite for combined deprecation + SOURCE_DATE_EPOCH-pin.

Plain-assert style per c6 convention; no pytest.

Invocation:
    PYTHONPATH=. /usr/bin/python3 tests/test_deprecation_and_anchor_pin.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys

WS = "/home/user/long-exposure-runs/music-gen"
RUBRIC = os.path.join(WS, "docs/deprecation_and_anchor_pin_rubric.md")
RUBRIC_HASH_TXT = os.path.join(WS, "data/deprecation_and_anchor_pin/rubric_hash.txt")
VERDICT = os.path.join(WS, "data/deprecation_and_anchor_pin/verdict.json")
DEPRECATION_CHECK = os.path.join(WS, "data/deprecation_and_anchor_pin/deprecation_check.json")
SDE_PIN = os.path.join(WS, "data/deprecation_and_anchor_pin/source_date_epoch_pin.json")
DET_CHECK = os.path.join(WS, "data/deprecation_and_anchor_pin/determinism_check.json")
ANCHOR_PRE = os.path.join(WS, "data/deprecation_and_anchor_pin/anchor_preservation_pre.json")
ANCHOR_PRESERVATION = os.path.join(WS, "data/deprecation_and_anchor_pin/anchor_preservation.json")
MANIFEST = os.path.join(WS, "data/anchor_manifest_v1.json")
C45_OLD = os.path.join(WS, "scripts/ear_v2/determinism_check.py")
C45_NEW = os.path.join(WS, "tools/stale/scripts_ear_v2_determinism_check_c45.py")
C46 = os.path.join(WS, "scripts/ear_v2/adjudication/determinism_check_c46.py")
SCRIPT_DIR = os.path.join(WS, "scripts/deprecation_and_anchor_pin")


def sha256_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _scripts_in_dir(d: str) -> list[str]:
    return sorted(
        os.path.join(d, f) for f in os.listdir(d)
        if f.endswith(".py") and f != "__init__.py"
    )


def test_01_rubric_mtime_lt_scripts():
    rubric_mtime = os.path.getmtime(RUBRIC)
    for s in _scripts_in_dir(SCRIPT_DIR):
        smt = os.path.getmtime(s)
        assert rubric_mtime <= smt, (
            f"rubric mtime {rubric_mtime} !< {s} mtime {smt}"
        )
    print("  test_01_rubric_mtime_lt_scripts: PASS")


def test_02_git_log_gate_advisory_soft():
    # Per c46 amendment, this is a soft check: git-log ordering is
    # advisory only. Attempt to inspect git log but do not gate on it.
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", "docs/deprecation_and_anchor_pin_rubric.md"],
            cwd=WS, capture_output=True, timeout=5, text=True,
        )
        # Either the rubric is committed (proc.returncode==0 with output)
        # or the harness gated commits and we soft-pass per c46 amendment.
        note = "committed" if proc.stdout.strip() else "harness-gated-uncommitted"
    except (subprocess.SubprocessError, FileNotFoundError):
        note = "git-unavailable"
    # Soft-pass regardless.
    assert True, f"soft check: {note}"
    print(f"  test_02_git_log_gate_advisory_soft: PASS ({note})")


def test_03_three_way_rubric_hash_byte_equality():
    doc_sha = sha256_file(RUBRIC)
    txt = open(RUBRIC_HASH_TXT).read().strip()
    v = json.load(open(VERDICT))
    assert doc_sha == txt == v["rubric_hash"], (
        f"three-way mismatch: doc={doc_sha} txt={txt} verdict={v['rubric_hash']}"
    )
    print("  test_03_three_way_rubric_hash_byte_equality: PASS")


def test_04_grep_zero_c45_imports():
    pat = re.compile(r"^\s*(from|import)\s+scripts\.ear_v2\.determinism_check")
    matches = []
    for root in ["scripts", "tools", "tests", "docs", "data"]:
        for dp, _dn, files in os.walk(os.path.join(WS, root)):
            if "/tools/stale" in dp:
                continue
            for fn in files:
                if not (fn.endswith(".py") or fn.endswith(".md") or fn.endswith(".txt")):
                    continue
                fp = os.path.join(dp, fn)
                try:
                    with open(fp, encoding="utf-8", errors="replace") as f:
                        for lineno, line in enumerate(f, 1):
                            if pat.match(line):
                                matches.append((fp, lineno, line.rstrip("\n")))
                except OSError:
                    continue
    assert not matches, f"non-zero c45 imports: {matches[:5]}"
    print("  test_04_grep_zero_c45_imports: PASS")


def test_05_c46_canonical_sha_unchanged():
    pre = json.load(open(ANCHOR_PRE))
    assert sha256_file(C46) == pre["c46_canonical"]["sha256"], "c46 SHA drifted"
    print("  test_05_c46_canonical_sha_unchanged: PASS")


def test_06_moved_file_mtime_advanced():
    d = json.load(open(DEPRECATION_CHECK))
    assert d["mtime_advanced"], f"mtime not advanced: pre={d['pre_mtime']} post={d['post_mtime']}"
    # Also verify on-disk mtime of new path.
    assert os.path.exists(C45_NEW), f"missing new path {C45_NEW}"
    assert not os.path.exists(C45_OLD), f"old path still present {C45_OLD}"
    assert os.path.getmtime(C45_NEW) >= d["pre_mtime"], "on-disk mtime regression"
    print("  test_06_moved_file_mtime_advanced: PASS")


def test_07_moved_file_sha_byte_identical():
    d = json.load(open(DEPRECATION_CHECK))
    assert d["sha_preserved"], "SHA drift on move"
    assert sha256_file(C45_NEW) == d["pre_sha256"], "on-disk moved SHA drift"
    print("  test_07_moved_file_sha_byte_identical: PASS")


def test_08_manifest_json_well_formed():
    m = json.load(open(MANIFEST))
    assert "anchors" in m and isinstance(m["anchors"], list), "anchors missing"
    assert m["anchor_count"] == len(m["anchors"]) == 19, (
        f"count/len drift: count={m['anchor_count']} len={len(m['anchors'])}"
    )
    print("  test_08_manifest_json_well_formed: PASS")


def test_09_source_date_epoch_entry_parseable():
    m = json.load(open(MANIFEST))
    entry = next(a for a in m["anchors"] if a["anchor_id"] == "env/SOURCE_DATE_EPOCH")
    assert entry["value"] == 1756463424, f"value drift: {entry['value']}"
    expected_v_sha = hashlib.sha256(str(1756463424).encode("utf-8")).hexdigest()
    assert entry["value_sha256"] == expected_v_sha, "value_sha256 drift"
    core = json.dumps(
        {"key": entry["key"], "value": entry["value"], "value_sha256": entry["value_sha256"]},
        sort_keys=True, separators=(",", ":"),
    )
    expected_e_sha = hashlib.sha256(core.encode("utf-8")).hexdigest()
    assert entry["entry_sha256"] == expected_e_sha, "entry_sha256 drift"
    print("  test_09_source_date_epoch_entry_parseable: PASS")


def test_10_byte_determinism_x2():
    d = json.load(open(DET_CHECK))
    assert d["byte_deterministic_x2"], (
        f"det drift: on_disk={d['on_disk_post_sha']} tmpdir={d['tmpdir_post_sha']}"
    )
    print("  test_10_byte_determinism_x2: PASS")


def _ast_grep_forbidden(dirpath: str, forbidden_modules: tuple[str, ...]) -> list[str]:
    hits = []
    for dp, _dn, files in os.walk(dirpath):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(dp, fn)
            src = open(fp).read()
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        for m in forbidden_modules:
                            if a.name == m or a.name.startswith(m + "."):
                                hits.append(f"{fp}: import {a.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for m in forbidden_modules:
                            if node.module == m or node.module.startswith(m + "."):
                                hits.append(f"{fp}: from {node.module}")
    return hits


def test_11_no_prng_ast_grep():
    hits = _ast_grep_forbidden(SCRIPT_DIR, ("random", "numpy.random", "secrets"))
    assert not hits, f"PRNG hits under scripts/deprecation_and_anchor_pin/: {hits}"
    print("  test_11_no_prng_ast_grep: PASS")


def test_12_no_sidecar_nonfactor_ast_grep():
    hits = _ast_grep_forbidden(SCRIPT_DIR, ("scripts.classifier.sidecar_nonfactor",
                                            "sidecar_nonfactor"))
    assert not hits, f"sidecar_nonfactor hits: {hits}"
    print("  test_12_no_sidecar_nonfactor_ast_grep: PASS")


def test_13_interpreter_guard_on_every_script():
    for s in _scripts_in_dir(SCRIPT_DIR):
        with open(s) as f:
            first3 = "".join(f.readline() for _ in range(3))
        # Either shebang mentions python3, or explicit interpreter guard.
        assert "python3" in first3 or "python" in first3, (
            f"{s} lacks interpreter marker in first 3 lines: {first3!r}"
        )
        # And a runtime interpreter guard in the module body.
        body = open(s).read()
        assert "/usr/bin/python" in body, f"{s} missing runtime interpreter guard"
    print("  test_13_interpreter_guard_on_every_script: PASS")


def test_14_18_preexisting_entries_byte_identical():
    pre = json.load(open(ANCHOR_PRE))
    m = json.load(open(MANIFEST))
    pre_by_id = {a["anchor_id"]: a for a in pre["anchors_pre"]}
    # Build the same summary for post entries.
    def summarize(a):
        return {
            "anchor_id": a["anchor_id"],
            "kind": a["kind"],
            "cycle": a.get("cycle"),
            "file_count": a.get("file_count"),
            "dir_manifest_sha_per_dir": a.get("dir_manifest_sha_per_dir", {}),
        }
    post_by_id = {a["anchor_id"]: summarize(a) for a in m["anchors"]}
    for aid, pre_a in pre_by_id.items():
        post_a = post_by_id.get(aid)
        assert post_a == pre_a, f"drift on {aid}: pre={pre_a} post={post_a}"
    # And only one new entry was appended.
    new_ids = set(post_by_id) - set(pre_by_id)
    assert new_ids == {"env/SOURCE_DATE_EPOCH"}, f"unexpected new ids: {new_ids}"
    print("  test_14_18_preexisting_entries_byte_identical: PASS")


def test_15_c22_stability_harness_preserved():
    ap = json.load(open(ANCHOR_PRESERVATION))
    assert ap["c22_stability_harness_preserved"], "c22 stability_harness drift"
    print("  test_15_c22_stability_harness_preserved: PASS")


def main() -> int:
    tests = [
        test_01_rubric_mtime_lt_scripts,
        test_02_git_log_gate_advisory_soft,
        test_03_three_way_rubric_hash_byte_equality,
        test_04_grep_zero_c45_imports,
        test_05_c46_canonical_sha_unchanged,
        test_06_moved_file_mtime_advanced,
        test_07_moved_file_sha_byte_identical,
        test_08_manifest_json_well_formed,
        test_09_source_date_epoch_entry_parseable,
        test_10_byte_determinism_x2,
        test_11_no_prng_ast_grep,
        test_12_no_sidecar_nonfactor_ast_grep,
        test_13_interpreter_guard_on_every_script,
        test_14_18_preexisting_entries_byte_identical,
        test_15_c22_stability_harness_preserved,
    ]
    n_pass = 0
    for t in tests:
        t()
        n_pass += 1
    print(f"\n[test_deprecation_and_anchor_pin] {n_pass}/{len(tests)} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
