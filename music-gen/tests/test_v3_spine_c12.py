#!/usr/bin/env python3
"""c12 heartbeat test suite. Minimum 8 cases per brief; delivers 12."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

_REPO = Path(__file__).resolve().parents[1]
os.chdir(_REPO)

FAILS: list[str] = []


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        FAILS.append(msg)


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


C12_PROBE = _REPO / "data/v3_spine/cycle12/torch213_reproduce_probe_c12.json"
C11_PROBE = _REPO / "data/v3_spine/cycle11/torch213_reproduce_probe_c11.json"
C10_PROBE = _REPO / "data/v3_spine/cycle10/torch213_reproduce_probe_c10.json"
C9_PROBE = _REPO / "data/v3_spine/cycle9/torch213_reproduce_probe_c9.json"
C8_PROBE = _REPO / "data/v3_spine/cycle8/torch213_reproduce_probe_c8.json"
C7_PROBE = _REPO / "data/v3_spine/cycle7/torch213_reproduce_probe.json"
C12_VERDICT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle12/verdict.json"
C11_VERDICT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle11/verdict.json"
C10_VERDICT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle10/verdict.json"
C7_VERDICT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.json"
POLICY_DOC = _REPO / "docs/wait_on_operator_cadence_policy.md"
POLICY_HASH = _REPO / "data/v3_spine/wait_on_operator_cadence_policy_hash.txt"
RUBRIC_DOC = _REPO / "docs/v3_spine_rubric_v2.md"
RUBRIC_HASH_FILE = _REPO / "data/v3_spine/rubric_hash_v2.txt"
ANCHOR_C12 = _REPO / "data/v3_spine/cycle12/anchor_preservation_c12.json"

# Known-good c7 verdict SHA (pinned since c8)
C7_VERDICT_SHA_BEFORE_C8 = (
    "82d2b5892b364549ed7f8dc93f9f9daf9dbfe7488db6c84faae1c76f7f7b5b75"
)

C12_SCRIPTS = (
    "torch213_reproduce_probe_c12.py",
    "verdict_c12.py",
    "anchor_preservation_c12.py",
)


def test_01_torch213_c12_probe_present_and_all_checks_pass() -> None:
    _assert(C12_PROBE.is_file(), f"missing {C12_PROBE}")
    d = json.loads(C12_PROBE.read_text())
    _assert(d["cycle"] == 12, "cycle != 12")
    _assert(d["mode"] == "dry_run", "mode != dry_run")
    _assert(d["cadence_mode"] == "heartbeat", "cadence_mode != heartbeat")
    checks = d["checks_vs_baseline"]
    for k in ("torch_version_matches", "torch_file_matches",
              "command_drafted_matches", "venv_manifest_matches_c7_c8_c9_c10_c11"):
        _assert(checks[k] is True, f"c12 check {k} failed")
    _assert(checks["all_pass"] is True, "checks_vs_baseline.all_pass must be True")
    _assert(d["checks_all_pass"] is True, "top-level checks_all_pass must be True")
    _assert(d["attribution_verdict"]
            == "ENV_DRIFT_PROBE_CANDIDATE_FOUND_C12_DRY_RUN_ROLL_FORWARD",
            f"unexpected attribution_verdict: {d['attribution_verdict']}")
    _assert(d["network_syscall_attempted"] is False,
            "network_syscall_attempted must be False")


def test_02_venv_manifest_byte_identical_to_c7_c8_c9_c10_c11() -> None:
    c12 = json.loads(C12_PROBE.read_text())
    c11 = json.loads(C11_PROBE.read_text())
    c10 = json.loads(C10_PROBE.read_text())
    c9 = json.loads(C9_PROBE.read_text())
    c8 = json.loads(C8_PROBE.read_text())
    c7 = json.loads(C7_PROBE.read_text())
    c12_pre = c12["venv_signature_pre"]["dir_manifest_sha256"]
    c12_post = c12["venv_signature_post"]["dir_manifest_sha256"]
    c11_post = c11["venv_signature_post"]["dir_manifest_sha256"]
    c10_post = c10["venv_signature_post"]["dir_manifest_sha256"]
    c9_post = c9["venv_signature_post"]["dir_manifest_sha256"]
    c8_post = c8["venv_signature_post"]["dir_manifest_sha256"]
    c7_post = c7["venv_signature_post"]["dir_manifest_sha256"]
    _assert(c12_pre == c12_post == c11_post == c10_post == c9_post == c8_post == c7_post,
            f"venv drift: c12_pre={c12_pre[:16]} c12_post={c12_post[:16]} "
            f"c11={c11_post[:16]} c10={c10_post[:16]} c9={c9_post[:16]} "
            f"c8={c8_post[:16]} c7={c7_post[:16]}")


def test_03_no_network_imports_in_c12_scripts() -> None:
    forbidden = {"urllib", "urllib.request", "urllib.parse", "socket",
                 "http", "http.client", "requests", "httpx", "aiohttp"}
    for name in C12_SCRIPTS:
        p = _REPO / "scripts/v3_spine" / name
        _assert(p.is_file(), f"missing {p}")
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    _assert(n.name not in forbidden,
                            f"{name}: forbidden network import {n.name}")
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                _assert(mod.split(".")[0] not in {"urllib", "socket", "http",
                                                   "requests", "httpx", "aiohttp"},
                        f"{name}: forbidden network from-import {mod}")


def test_04_prior_delivery_wavs_and_verdicts_byte_identical_pre_post() -> None:
    """c4/c5/c6/c7/c8/c9/c10/c11 delivery WAVs + verdict.json SHAs byte-identical
    vs pre-c12 anchor snapshot."""
    pre = json.loads((_REPO / "data/v3_spine/cycle12/anchor_preservation_pre_c12.json"
                      ).read_text())
    delivery_prefixes = (
        "data/v3/deliveries/31a164f845f8e27e/",
    )
    checked = 0
    for rel, meta in pre["anchors"].items():
        if not any(rel.startswith(p) for p in delivery_prefixes):
            continue
        p = _REPO / rel
        _assert(p.is_file(), f"delivery path vanished: {rel}")
        if p.is_file():
            _assert(_sha256(p) == meta["sha256"],
                    f"delivery SHA drift on {rel}")
            checked += 1
    _assert(checked >= 10,
            f"expected ≥10 delivery anchor rows, checked {checked}")


def test_05_locked_scripts_byte_identical_pre_post() -> None:
    """DO-NOT-TOUCH scripts SHAs byte-identical pre-c12 == on-disk."""
    pre = json.loads((_REPO / "data/v3_spine/cycle12/anchor_preservation_pre_c12.json"
                      ).read_text())
    locked = (
        "scripts/palette_render/render_stem.py",
        "scripts/recreate_v2/rc7_v2_rerun.py",
        "scripts/recreate_v2/rc7_mix_balance.py",
        "scripts/v3_spine/mix_match_operator_section.py",
        "scripts/v3_spine/rc7_v2_rerun_v3_paths.py",
        "scripts/v3_spine/torch213_reproduce_probe.py",
        "scripts/v3_spine/torch213_reproduce_probe_c8.py",
        "scripts/v3_spine/torch213_reproduce_probe_c9.py",
        "scripts/v3_spine/torch213_reproduce_probe_c10.py",
        "scripts/v3_spine/torch213_reproduce_probe_c11.py",
    )
    for rel in locked:
        _assert(rel in pre["anchors"], f"locked script missing from pre snapshot: {rel}")
        if rel in pre["anchors"]:
            actual = _sha256(_REPO / rel)
            _assert(actual == pre["anchors"][rel]["sha256"],
                    f"locked script drift: {rel}")


def test_06_three_way_rubric_hash_v2_chain_holds_on_c12_verdict() -> None:
    _assert(C12_VERDICT.is_file(), f"missing {C12_VERDICT}")
    v = json.loads(C12_VERDICT.read_text())
    _assert(v["rubric_hash_v2"] == _sha256(RUBRIC_DOC),
            "c12 verdict.rubric_hash_v2 != doc SHA")
    _assert(v["rubric_hash_v2"] == RUBRIC_HASH_FILE.read_text().strip(),
            "c12 verdict.rubric_hash_v2 != pinned file")
    _assert(v.get("rubric_hash_v2_three_way_chain_holds") is True,
            "rubric_hash_v2_three_way_chain_holds must be True")


def test_07_cadence_policy_doc_sha_byte_equal_to_hash_file() -> None:
    doc_sha = _sha256(POLICY_DOC)
    pin_sha = POLICY_HASH.read_text().strip()
    _assert(doc_sha == pin_sha,
            f"cadence policy hash chain drift: doc={doc_sha[:16]} "
            f"pin={pin_sha[:16]}")
    v = json.loads(C12_VERDICT.read_text())
    _assert(v["cadence_policy_sha"] == doc_sha,
            "c12 verdict.cadence_policy_sha != on-disk doc SHA")


def test_08_generic_invariant_passes_on_newest_c12_verdict() -> None:
    """c8-landed generic invariant walker resolves every (sha_field, path_field)
    pair on the newest c12 verdict — contract inheritance holds through 5 cycles."""
    probe = _REPO / "tests/test_verdict_sha_fields_resolve_on_disk.py"
    _assert(probe.is_file(), f"missing generic invariant test: {probe}")
    r = subprocess.run(
        ["/usr/bin/python3", str(probe)],
        capture_output=True, text=True, cwd=str(_REPO),
    )
    _assert(r.returncode == 0,
            f"generic invariant subprocess rc={r.returncode}: {r.stdout}\n{r.stderr}")


def test_09_anchor_preservation_at_least_145_byte_identical() -> None:
    _assert(ANCHOR_C12.is_file(), f"missing {ANCHOR_C12}")
    d = json.loads(ANCHOR_C12.read_text())
    _assert(d["n_post"] >= 145, f"anchor n_post < 145: {d['n_post']}")
    _assert(d["all_match"] is True, f"anchors drifted: n_diff={d['n_diff']}")
    _assert(d["n_diff"] == 0, f"n_diff != 0: {d['n_diff']}")


def test_10_c12_verdict_blocked_on_operator_and_cycles_since_8() -> None:
    v = json.loads(C12_VERDICT.read_text())
    _assert(v["cycle"] == 12, f"cycle != 12: {v['cycle']}")
    _assert(v["blocked_on_operator"] is True,
            "blocked_on_operator must be True")
    _assert(v["cycles_since_last_operator_input"] == 8,
            f"cycles_since_last_operator_input != 8: "
            f"{v['cycles_since_last_operator_input']}")
    _assert(v["verdict"] == "V3_SPINE_C12_HEARTBEAT_pending_operator",
            f"unexpected verdict label: {v['verdict']}")
    _assert(v["cadence_mode"] == "heartbeat",
            f"cadence_mode != heartbeat: {v['cadence_mode']}")


def test_11_c7_verdict_still_byte_identical() -> None:
    """Sanity floor: c7 verdict.json still byte-identical to c8 pre-snapshot."""
    _assert(_sha256(C7_VERDICT) == C7_VERDICT_SHA_BEFORE_C8,
            f"c7 verdict drifted: {_sha256(C7_VERDICT)[:16]}")


def test_12_c11_verdict_still_present_and_heartbeat() -> None:
    """Sanity floor: c11 verdict + heartbeat status still intact."""
    _assert(C11_VERDICT.is_file(), f"missing {C11_VERDICT}")
    v = json.loads(C11_VERDICT.read_text())
    _assert(v["verdict"] == "V3_SPINE_C11_HEARTBEAT_pending_operator",
            f"c11 verdict label drift: {v['verdict']}")
    _assert(v["cadence_mode"] == "heartbeat",
            f"c11 cadence_mode drift: {v['cadence_mode']}")


def main() -> int:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                FAILS.append(f"{name}: raised {type(e).__name__}: {e}")
    if FAILS:
        print(f"FAIL: {len(FAILS)} failures")
        for m in FAILS:
            print("  -", m)
        return 1
    print("PASS: all c12 cases green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
