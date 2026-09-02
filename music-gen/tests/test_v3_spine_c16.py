#!/usr/bin/env python3
"""c16 heartbeat test suite. Minimum 8 cases per brief; delivers 12."""
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


C16_PROBE = _REPO / "data/v3_spine/cycle16/torch213_reproduce_probe_c16.json"
C15_PROBE = _REPO / "data/v3_spine/cycle15/torch213_reproduce_probe_c15.json"
C14_PROBE = _REPO / "data/v3_spine/cycle14/torch213_reproduce_probe_c14.json"
C13_PROBE = _REPO / "data/v3_spine/cycle13/torch213_reproduce_probe_c13.json"
C12_PROBE = _REPO / "data/v3_spine/cycle12/torch213_reproduce_probe_c12.json"
C11_PROBE = _REPO / "data/v3_spine/cycle11/torch213_reproduce_probe_c11.json"
C10_PROBE = _REPO / "data/v3_spine/cycle10/torch213_reproduce_probe_c10.json"
C9_PROBE = _REPO / "data/v3_spine/cycle9/torch213_reproduce_probe_c9.json"
C8_PROBE = _REPO / "data/v3_spine/cycle8/torch213_reproduce_probe_c8.json"
C7_PROBE = _REPO / "data/v3_spine/cycle7/torch213_reproduce_probe.json"
C16_VERDICT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle16/verdict.json"
C15_VERDICT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle15/verdict.json"
C7_VERDICT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.json"
POLICY_DOC = _REPO / "docs/wait_on_operator_cadence_policy.md"
POLICY_HASH = _REPO / "data/v3_spine/wait_on_operator_cadence_policy_hash.txt"
RUBRIC_DOC = _REPO / "docs/v3_spine_rubric_v2.md"
RUBRIC_HASH_FILE = _REPO / "data/v3_spine/rubric_hash_v2.txt"
ANCHOR_C16 = _REPO / "data/v3_spine/cycle16/anchor_preservation_c16.json"

C7_VERDICT_SHA_BEFORE_C8 = (
    "82d2b5892b364549ed7f8dc93f9f9daf9dbfe7488db6c84faae1c76f7f7b5b75"
)

C16_SCRIPTS = (
    "torch213_reproduce_probe_c16.py",
    "verdict_c16.py",
    "anchor_preservation_c16.py",
)


def test_01_torch213_c16_probe_present_and_all_checks_pass() -> None:
    _assert(C16_PROBE.is_file(), f"missing {C16_PROBE}")
    d = json.loads(C16_PROBE.read_text())
    _assert(d["cycle"] == 16, "cycle != 16")
    _assert(d["mode"] == "dry_run", "mode != dry_run")
    _assert(d["cadence_mode"] == "heartbeat", "cadence_mode != heartbeat")
    checks = d["checks_vs_baseline"]
    for k in ("torch_version_matches", "torch_file_matches",
              "command_drafted_matches",
              "venv_manifest_matches_c7_c8_c9_c10_c11_c12_c13_c14_c15"):
        _assert(checks[k] is True, f"c16 check {k} failed")
    _assert(checks["all_pass"] is True, "checks_vs_baseline.all_pass must be True")
    _assert(d["checks_all_pass"] is True, "top-level checks_all_pass must be True")
    _assert(d["attribution_verdict"]
            == "ENV_DRIFT_PROBE_CANDIDATE_FOUND_C16_DRY_RUN_ROLL_FORWARD",
            f"unexpected attribution_verdict: {d['attribution_verdict']}")
    _assert(d["network_syscall_attempted"] is False,
            "network_syscall_attempted must be False")


def test_02_venv_manifest_byte_identical_to_c7_through_c15() -> None:
    c16 = json.loads(C16_PROBE.read_text())
    c15 = json.loads(C15_PROBE.read_text())
    c14 = json.loads(C14_PROBE.read_text())
    c13 = json.loads(C13_PROBE.read_text())
    c12 = json.loads(C12_PROBE.read_text())
    c11 = json.loads(C11_PROBE.read_text())
    c10 = json.loads(C10_PROBE.read_text())
    c9 = json.loads(C9_PROBE.read_text())
    c8 = json.loads(C8_PROBE.read_text())
    c7 = json.loads(C7_PROBE.read_text())
    c16_pre = c16["venv_signature_pre"]["dir_manifest_sha256"]
    c16_post = c16["venv_signature_post"]["dir_manifest_sha256"]
    all_sha = [
        c16_pre, c16_post,
        c15["venv_signature_post"]["dir_manifest_sha256"],
        c14["venv_signature_post"]["dir_manifest_sha256"],
        c13["venv_signature_post"]["dir_manifest_sha256"],
        c12["venv_signature_post"]["dir_manifest_sha256"],
        c11["venv_signature_post"]["dir_manifest_sha256"],
        c10["venv_signature_post"]["dir_manifest_sha256"],
        c9["venv_signature_post"]["dir_manifest_sha256"],
        c8["venv_signature_post"]["dir_manifest_sha256"],
        c7["venv_signature_post"]["dir_manifest_sha256"],
    ]
    _assert(len(set(all_sha)) == 1,
            f"venv drift across ten-cycle chain: {[s[:16] for s in all_sha]}")


def test_03_no_network_imports_in_c16_scripts() -> None:
    forbidden = {"urllib", "urllib.request", "urllib.parse", "socket",
                 "http", "http.client", "requests", "httpx", "aiohttp"}
    for name in C16_SCRIPTS:
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
    pre = json.loads((_REPO / "data/v3_spine/cycle16/anchor_preservation_pre_c16.json"
                      ).read_text())
    delivery_prefixes = ("data/v3/deliveries/31a164f845f8e27e/",)
    checked = 0
    for rel, meta in pre["anchors"].items():
        if not any(rel.startswith(p) for p in delivery_prefixes):
            continue
        p = _REPO / rel
        _assert(p.is_file(), f"delivery path vanished: {rel}")
        if p.is_file():
            _assert(_sha256(p) == meta["sha256"], f"delivery SHA drift on {rel}")
            checked += 1
    _assert(checked >= 12,
            f"expected ≥12 delivery anchor rows, checked {checked}")


def test_05_locked_scripts_byte_identical_pre_post() -> None:
    pre = json.loads((_REPO / "data/v3_spine/cycle16/anchor_preservation_pre_c16.json"
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
        "scripts/v3_spine/torch213_reproduce_probe_c12.py",
        "scripts/v3_spine/torch213_reproduce_probe_c13.py",
        "scripts/v3_spine/torch213_reproduce_probe_c14.py",
        "scripts/v3_spine/torch213_reproduce_probe_c15.py",
    )
    for rel in locked:
        _assert(rel in pre["anchors"], f"locked script missing from pre snapshot: {rel}")
        if rel in pre["anchors"]:
            actual = _sha256(_REPO / rel)
            _assert(actual == pre["anchors"][rel]["sha256"],
                    f"locked script drift: {rel}")


def test_06_three_way_rubric_hash_v2_chain_holds_on_c16_verdict() -> None:
    _assert(C16_VERDICT.is_file(), f"missing {C16_VERDICT}")
    v = json.loads(C16_VERDICT.read_text())
    _assert(v["rubric_hash_v2"] == _sha256(RUBRIC_DOC),
            "c16 verdict.rubric_hash_v2 != doc SHA")
    _assert(v["rubric_hash_v2"] == RUBRIC_HASH_FILE.read_text().strip(),
            "c16 verdict.rubric_hash_v2 != pinned file")
    _assert(v.get("rubric_hash_v2_three_way_chain_holds") is True,
            "rubric_hash_v2_three_way_chain_holds must be True")


def test_07_cadence_policy_doc_sha_byte_equal_to_hash_file() -> None:
    doc_sha = _sha256(POLICY_DOC)
    pin_sha = POLICY_HASH.read_text().strip()
    _assert(doc_sha == pin_sha,
            f"cadence policy hash chain drift: doc={doc_sha[:16]} pin={pin_sha[:16]}")
    v = json.loads(C16_VERDICT.read_text())
    _assert(v["cadence_policy_sha"] == doc_sha,
            "c16 verdict.cadence_policy_sha != on-disk doc SHA")


def test_08_generic_invariant_passes_on_newest_c16_verdict() -> None:
    probe = _REPO / "tests/test_verdict_sha_fields_resolve_on_disk.py"
    _assert(probe.is_file(), f"missing generic invariant test: {probe}")
    r = subprocess.run(
        ["/usr/bin/python3", str(probe)],
        capture_output=True, text=True, cwd=str(_REPO),
    )
    _assert(r.returncode == 0,
            f"generic invariant subprocess rc={r.returncode}: {r.stdout}\n{r.stderr}")


def test_09_anchor_preservation_at_least_185_byte_identical() -> None:
    _assert(ANCHOR_C16.is_file(), f"missing {ANCHOR_C16}")
    d = json.loads(ANCHOR_C16.read_text())
    _assert(d["n_post"] >= 185, f"anchor n_post < 185: {d['n_post']}")
    _assert(d["all_match"] is True, f"anchors drifted: n_diff={d['n_diff']}")
    _assert(d["n_diff"] == 0, f"n_diff != 0: {d['n_diff']}")


def test_10_c16_verdict_blocked_on_operator_and_cycles_since_12() -> None:
    v = json.loads(C16_VERDICT.read_text())
    _assert(v["cycle"] == 16, f"cycle != 16: {v['cycle']}")
    _assert(v["blocked_on_operator"] is True, "blocked_on_operator must be True")
    _assert(v["cycles_since_last_operator_input"] == 12,
            f"cycles_since_last_operator_input != 12: "
            f"{v['cycles_since_last_operator_input']}")
    _assert(v["verdict"] == "V3_SPINE_C16_HEARTBEAT_pending_operator",
            f"unexpected verdict label: {v['verdict']}")
    _assert(v["cadence_mode"] == "heartbeat",
            f"cadence_mode != heartbeat: {v['cadence_mode']}")


def test_11_c7_verdict_still_byte_identical() -> None:
    _assert(_sha256(C7_VERDICT) == C7_VERDICT_SHA_BEFORE_C8,
            f"c7 verdict drifted: {_sha256(C7_VERDICT)[:16]}")


def test_12_c15_verdict_still_present_and_heartbeat_and_backref_matches() -> None:
    _assert(C15_VERDICT.is_file(), f"missing {C15_VERDICT}")
    v15 = json.loads(C15_VERDICT.read_text())
    _assert(v15["verdict"] == "V3_SPINE_C15_HEARTBEAT_pending_operator",
            f"c15 verdict label drift: {v15['verdict']}")
    _assert(v15["cadence_mode"] == "heartbeat",
            f"c15 cadence_mode drift: {v15['cadence_mode']}")
    v16 = json.loads(C16_VERDICT.read_text())
    _assert(v16["c15_backref_sha"] == _sha256(C15_VERDICT),
            "c15_backref_sha in c16 verdict does not resolve to on-disk c15 verdict")


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
    print("PASS: all c16 cases green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
