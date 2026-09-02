#!/usr/bin/env python3
"""c6 test suite. Minimum 12 cases per brief."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
os.chdir(_REPO)

# Interpreter guard: tests themselves invoke /usr/bin/python3 for subprocesses.

FAILS: list[str] = []


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        FAILS.append(msg)


def test_01_env_drift_json_present_with_schema() -> None:
    p = _REPO / "data/v3_spine/env_drift_deep_dive.json"
    _assert(p.is_file(), f"missing {p}")
    d = json.loads(p.read_text())
    for k in ("cycle", "spec_sha256", "scan_roots_attempted",
              "candidates", "probe_status", "attribution_verdict",
              "network_syscall_attempted", "c5_torch_baseline"):
        _assert(k in d, f"env_drift missing key {k}")
    _assert(d["cycle"] == 6, "env_drift cycle != 6")


def test_02_env_drift_no_network_syscall_attempted() -> None:
    d = json.loads((_REPO / "data/v3_spine/env_drift_deep_dive.json").read_text())
    _assert(d["network_syscall_attempted"] is False, "network_syscall_attempted must be False")


def test_03_env_drift_ast_no_network_imports() -> None:
    src = (_REPO / "scripts/v3_spine/env_drift_deep_dive.py").read_text()
    tree = ast.parse(src)
    forbidden = {"urllib", "urllib.request", "socket", "requests", "http.client",
                 "httpx", "aiohttp", "smtplib", "ftplib"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                _assert(alias.name not in forbidden, f"forbidden import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            _assert(node.module not in forbidden, f"forbidden from-import {node.module}")


def test_04_env_drift_byte_determinism() -> None:
    d = json.loads((_REPO / "data/v3_spine/env_drift_deep_dive_byte_det.json").read_text())
    _assert(d["byte_deterministic_x2"] is True,
            f"env_drift byte-det failed: run1={d['run1_sha256'][:16]} run2={d['run2_sha256'][:16]}")


def test_05_method_equivalence_json_present() -> None:
    d = json.loads((_REPO / "data/v3_spine/rc7_method_equivalence.json").read_text())
    for k in ("cycle", "spec_sha256", "method_a", "method_b",
              "per_stem", "full_mix", "verdict"):
        _assert(k in d, f"rc7_method_equivalence missing key {k}")


def test_06_method_equivalence_per_stem_finite() -> None:
    d = json.loads((_REPO / "data/v3_spine/rc7_method_equivalence.json").read_text())
    for stem, m in d["per_stem"].items():
        if isinstance(m, dict) and "rms_delta_db" in m:
            _assert(m["rms_delta_db"] == m["rms_delta_db"],
                    f"per_stem {stem} rms_delta_db is NaN")
            _assert(m["max_abs_diff"] == m["max_abs_diff"],
                    f"per_stem {stem} max_abs_diff is NaN")


def test_07_rc7_v2_rerun_py_sha_unchanged() -> None:
    p = _REPO / "scripts/recreate_v2/rc7_v2_rerun.py"
    pre = json.loads((_REPO / "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c6.json").read_text())
    key = "scripts/recreate_v2/rc7_v2_rerun.py"
    _assert(key in pre["anchors"], "rc7_v2_rerun.py missing from pre-anchors")
    post = hashlib.sha256(p.read_bytes()).hexdigest()
    _assert(post == pre["anchors"][key]["sha256"],
            f"rc7_v2_rerun.py SHA drifted: pre={pre['anchors'][key]['sha256'][:16]} post={post[:16]}")


def test_08_mix_match_operator_section_sha_unchanged() -> None:
    p = _REPO / "scripts/v3_spine/mix_match_operator_section.py"
    pre = json.loads((_REPO / "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c6.json").read_text())
    key = "scripts/v3_spine/mix_match_operator_section.py"
    _assert(key in pre["anchors"], "mix_match_operator_section.py missing from pre-anchors")
    post = hashlib.sha256(p.read_bytes()).hexdigest()
    _assert(post == pre["anchors"][key]["sha256"], "mix_match_operator_section.py SHA drifted")


def test_09_render_stem_sha_unchanged() -> None:
    p = _REPO / "scripts/palette_render/render_stem.py"
    pre = json.loads((_REPO / "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c6.json").read_text())
    key = "scripts/palette_render/render_stem.py"
    _assert(key in pre["anchors"], "render_stem.py missing from pre-anchors")
    post = hashlib.sha256(p.read_bytes()).hexdigest()
    _assert(post == pre["anchors"][key]["sha256"], "render_stem.py SHA drifted")


def test_10_anchor_preservation_all_match() -> None:
    post = _REPO / "data/v3_spine/31a164f845f8e27e/anchor_preservation_post_c6.json"
    if not post.is_file():
        # Run it on the fly.
        subprocess.check_call(
            ["/usr/bin/python3", "scripts/v3_spine/anchor_preservation_post_c6.py"],
            cwd=str(_REPO))
    d = json.loads(post.read_text())
    _assert(d["all_match"] is True, f"anchor preservation failed: n_diff={d['n_diff']} diffs={d['diffs'][:3]}")


def test_11_verdict_includes_both_tracks() -> None:
    p = _REPO / "data/v3_spine/verdict_c6.json"
    _assert(p.is_file(), f"missing {p}")
    d = json.loads(p.read_text())
    _assert(d["verdict"] in ("V3_SPINE_C6_TWO_TRACK_LANDS_pending_operator",
                              "V3_SPINE_C6_PARTIAL", "V3_SPINE_C6_FAILS"),
            f"unexpected verdict: {d['verdict']}")
    _assert("env_drift_deep_dive" in d and d["env_drift_deep_dive"].get("status"),
            "verdict missing env_drift_deep_dive.status")
    _assert("rc7_method_equivalence" in d and d["rc7_method_equivalence"].get("verdict"),
            "verdict missing rc7_method_equivalence.verdict")


def test_12_rubric_hash_v2_three_way_chain() -> None:
    doc_sha = hashlib.sha256((_REPO / "docs/v3_spine_rubric_v2.md").read_bytes()).hexdigest()
    txt_sha = (_REPO / "data/v3_spine/rubric_hash_v2.txt").read_text().strip()
    verdict = json.loads((_REPO / "data/v3_spine/verdict_c6.json").read_text())
    _assert(doc_sha == txt_sha == verdict["rubric_hash_v2"],
            f"three-way rubric_hash_v2 chain broken: doc={doc_sha[:16]} "
            f"txt={txt_sha[:16]} verdict={verdict['rubric_hash_v2'][:16]}")


def test_13_verdict_blocked_on_operator() -> None:
    d = json.loads((_REPO / "data/v3_spine/verdict_c6.json").read_text())
    _assert(d["blocked_on_operator"] is True,
            "blocked_on_operator must remain True per FD-6")


def test_14_rc7_v2_rerun_v3_paths_byte_det() -> None:
    d = json.loads((_REPO / "data/v3_spine/rc7_v2_v3_paths/byte_determinism.json").read_text())
    _assert(d["byte_deterministic_x2"] is True,
            f"rc7_v2_rerun_v3_paths byte-det failed: {d['run1_full_mix_sha256'][:16]} vs {d['run2_full_mix_sha256'][:16]}")


def test_15_interpreter_guards_present() -> None:
    for rel in ("scripts/v3_spine/env_drift_deep_dive.py",
                "scripts/v3_spine/rc7_v2_rerun_v3_paths.py",
                "scripts/v3_spine/method_equivalence_rc7.py",
                "scripts/v3_spine/verdict_c6.py"):
        src = (_REPO / rel).read_text()
        _assert("/usr/bin/python3" in src, f"{rel} missing /usr/bin/python3 guard")


def test_16_spec_hash_chain_env_drift() -> None:
    doc_sha = hashlib.sha256((_REPO / "docs/v3_spine_env_drift_deep_dive_spec.md").read_bytes()).hexdigest()
    txt_sha = (_REPO / "data/v3_spine/env_drift_deep_dive_spec_hash.txt").read_text().strip()
    j = json.loads((_REPO / "data/v3_spine/env_drift_deep_dive.json").read_text())
    _assert(doc_sha == txt_sha == j["spec_sha256"],
            "env-drift spec three-way chain broken")


def test_17_spec_hash_chain_method_eq() -> None:
    doc_sha = hashlib.sha256((_REPO / "docs/v3_spine_method_equivalence_rc7_spec.md").read_bytes()).hexdigest()
    txt_sha = (_REPO / "data/v3_spine/method_equivalence_rc7_spec_hash.txt").read_text().strip()
    j = json.loads((_REPO / "data/v3_spine/rc7_method_equivalence.json").read_text())
    _assert(doc_sha == txt_sha == j["spec_sha256"],
            "method-eq spec three-way chain broken")


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
        except AssertionError as e:
            FAILS.append(f"{t.__name__}: assertion {e}")
        except Exception as e:
            FAILS.append(f"{t.__name__}: {type(e).__name__} {e}")
    if FAILS:
        for f in FAILS:
            print(f"FAIL {f}", file=sys.stderr)
        print(f"\n{len(FAILS)} failed out of {len(tests)} tests", file=sys.stderr)
        return 1
    print(f"{len(tests)}/{len(tests)} tests PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
