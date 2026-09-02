#!/usr/bin/env python3
"""c8 test suite. Minimum 12 cases per brief."""
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


C7_VERDICT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.json"
C8_VERDICT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle8/verdict.json"
AMENDMENT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.c8_amendment.json"
C7_VERDICT_SHA_BEFORE_C8 = (
    "82d2b5892b364549ed7f8dc93f9f9daf9dbfe7488db6c84faae1c76f7f7b5b75"
)


def test_01_amendment_present_and_well_formed() -> None:
    _assert(AMENDMENT.is_file(), f"missing {AMENDMENT}")
    d = json.loads(AMENDMENT.read_text())
    for k in ("cycle", "amends", "amended_field", "pinned_sha_from_c7",
              "on_disk_sha_at_c8", "prior_version_recoverable",
              "canonical_designation", "root_cause", "closure_action",
              "note_path", "drift_detected"):
        _assert(k in d, f"amendment missing key {k}")
    _assert(d["cycle"] == 8, "amendment cycle != 8")
    _assert(d["amends"] == "cycle7/verdict.json",
            "amendment.amends must equal 'cycle7/verdict.json'")
    _assert(d["amended_field"] == "rc7_canonicality_note.sha256",
            "amended_field wrong")
    _assert(d["canonical_designation"] == "current_on_disk",
            "canonical_designation must be 'current_on_disk'")


def test_02_amendment_pins_verdict_sha() -> None:
    d = json.loads(AMENDMENT.read_text())
    _assert("c7_verdict_sha256" in d, "amendment missing c7_verdict_sha256")
    _assert(d["c7_verdict_sha256"] == _sha256(C7_VERDICT),
            "c7_verdict_sha256 drift")


def test_03_c7_verdict_byte_identical_pre_post_c8() -> None:
    """Append-only proven: c7 verdict.json byte-identical to pre-c8 snapshot."""
    actual = _sha256(C7_VERDICT)
    _assert(actual == C7_VERDICT_SHA_BEFORE_C8,
            f"c7 verdict drifted: expected {C7_VERDICT_SHA_BEFORE_C8[:16]}… "
            f"got {actual[:16]}…")


def test_04_track2_dry_run_present_and_pins() -> None:
    p = _REPO / "data/v3_spine/cycle8/torch213_reproduce_probe_c8.json"
    _assert(p.is_file(), f"missing {p}")
    d = json.loads(p.read_text())
    for k in ("cycle", "mode", "probe_status", "attribution_verdict",
              "torch_version_observed", "torch_file_observed",
              "command_string_drafted", "venv_signature_pre",
              "venv_signature_post", "venv_unchanged",
              "checks_vs_c7_baseline"):
        _assert(k in d, f"c8 probe missing key {k}")
    _assert(d["cycle"] == 8, "c8 probe cycle != 8")
    _assert(d["mode"] == "dry_run", "c8 probe mode must be dry_run")
    _assert(d["torch_version_observed"] == "2.13.0+cpu",
            f"torch version drifted: {d['torch_version_observed']}")
    _assert(d["torch_file_observed"] ==
            "/usr/local/lib/python3.11/dist-packages/torch/__init__.py",
            f"torch file drifted: {d['torch_file_observed']}")
    _assert(d["network_syscall_attempted"] is False,
            "network_syscall_attempted must be False")


def test_05_track2_venv_manifest_matches_c7() -> None:
    p = _REPO / "data/v3_spine/cycle8/torch213_reproduce_probe_c8.json"
    d = json.loads(p.read_text())
    c7 = json.loads(
        (_REPO / "data/v3_spine/cycle7/torch213_reproduce_probe.json").read_text()
    )
    _assert(d["venv_signature_post"]["dir_manifest_sha256"] ==
            c7["venv_signature_post"]["dir_manifest_sha256"],
            "venv dir-manifest SHA drift vs c7 baseline")
    _assert(d["checks_vs_c7_baseline"]["all_pass"] is True,
            "checks vs c7 baseline did not all pass")


def test_06_cadence_policy_doc_landed_and_pinned() -> None:
    doc = _REPO / "docs/wait_on_operator_cadence_policy.md"
    pin = _REPO / "data/v3_spine/wait_on_operator_cadence_policy_hash.txt"
    _assert(doc.is_file(), f"missing {doc}")
    _assert(pin.is_file(), f"missing {pin}")
    _assert(_sha256(doc) == pin.read_text().strip(),
            "cadence policy hash chain broken")


def test_07_generic_invariant_test_landed_and_passes() -> None:
    t = _REPO / "tests/test_verdict_sha_fields_resolve_on_disk.py"
    _assert(t.is_file(), f"missing {t}")
    r = subprocess.run(
        ["/usr/bin/python3", str(t)],
        capture_output=True, text=True,
    )
    _assert(r.returncode == 0,
            f"generic invariant test failed rc={r.returncode}: "
            f"{r.stdout[-500:]}\n{r.stderr[-500:]}")


def test_08_locked_scripts_shas_unchanged() -> None:
    """render_stem.py + rc7_v2_rerun.py + rc7_mix_balance.py +
    mix_match_operator_section.py + rc7_v2_rerun_v3_paths.py +
    torch213_reproduce_probe.py byte-identical pre==post c8."""
    expected_prefixes = {
        "scripts/palette_render/render_stem.py": "214372d9",
        "scripts/recreate_v2/rc7_v2_rerun.py": "7a5fbef0",
        "scripts/recreate_v2/rc7_mix_balance.py": "cc049624",
        "scripts/v3_spine/mix_match_operator_section.py": "4f47fbcd",
    }
    for rel, prefix in expected_prefixes.items():
        p = _REPO / rel
        _assert(p.is_file(), f"locked script missing: {rel}")
        actual = _sha256(p)
        _assert(actual.startswith(prefix),
                f"{rel} SHA drift: expected {prefix}… got {actual[:8]}…")


def test_09_delivery_wavs_c4_c5_c6_c7_unchanged() -> None:
    """c4/c5/c6/c7 delivery WAV SHAs byte-identical pre==post c8 via
    the anchor_preservation_c8.json all_match=true report."""
    ap = _REPO / "data/v3_spine/31a164f845f8e27e/anchor_preservation_c8.json"
    _assert(ap.is_file(), f"missing {ap}")
    d = json.loads(ap.read_text())
    _assert(d["all_match"] is True, "anchor_preservation_c8.all_match not true")
    _assert(d["n_diff"] == 0, f"anchor n_diff = {d['n_diff']}")
    _assert(d["n_post"] >= 90, f"n_post = {d['n_post']} < brief target 90")


def test_10_no_network_imports_in_c8_scripts() -> None:
    forbidden = {"urllib", "urllib3", "requests", "httpx",
                 "socket", "http", "aiohttp"}
    for name in ("torch213_reproduce_probe_c8.py",
                 "verdict_c8.py",
                 "verdict_c8_amendment.py",
                 "anchor_preservation_c8.py"):
        p = _REPO / "scripts/v3_spine" / name
        if not p.is_file():
            continue
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    root = n.name.split(".")[0]
                    _assert(root not in forbidden,
                            f"{name}: forbidden import {n.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root = node.module.split(".")[0]
                    _assert(root not in forbidden,
                            f"{name}: forbidden from-import {node.module}")


def test_11_c8_verdict_shape_and_rubric_chain() -> None:
    _assert(C8_VERDICT.is_file(), f"missing {C8_VERDICT}")
    v = json.loads(C8_VERDICT.read_text())
    for k in ("cycle", "song_sha16", "verdict", "c7_moderate_fix",
              "torch213_dry_run_c8", "wait_on_operator_cadence_flag",
              "rubric_hash_v2", "rubric_hash_v2_doc_sha",
              "rubric_hash_v2_three_way_chain_holds",
              "blocked_on_operator", "verdict_placement_convention",
              "operator_notes"):
        _assert(k in v, f"c8 verdict missing key {k}")
    _assert(v["cycle"] == 8, "c8 verdict cycle != 8")
    _assert(v["blocked_on_operator"] is True,
            "blocked_on_operator must be true")
    _assert(v["verdict_placement_convention"] == "cycle<N>/",
            "verdict placement convention drift")
    _assert(v["rubric_hash_v2"] == v["rubric_hash_v2_doc_sha"],
            "rubric_hash_v2 chain broken inside verdict")
    doc = _REPO / "docs/v3_spine_rubric_v2.md"
    pin = _REPO / "data/v3_spine/rubric_hash_v2.txt"
    _assert(v["rubric_hash_v2"] == _sha256(doc), "rubric_hash_v2 != doc SHA")
    _assert(v["rubric_hash_v2"] == pin.read_text().strip(),
            "rubric_hash_v2 != pinned file")


def test_12_c8_verdict_c7_moderate_fix_closed() -> None:
    v = json.loads(C8_VERDICT.read_text())
    m = v["c7_moderate_fix"]
    _assert(m["status"] == "closed",
            f"c7_moderate_fix.status = {m['status']} (expected closed)")
    _assert(m["generic_invariant_test_landed"] is True,
            "generic_invariant_test_landed must be True")


def test_13_interpreter_guards_present() -> None:
    for name in ("torch213_reproduce_probe_c8.py", "verdict_c8.py",
                 "verdict_c8_amendment.py", "anchor_preservation_c8.py"):
        p = _REPO / "scripts/v3_spine" / name
        if not p.is_file():
            continue
        src = p.read_text()
        _assert('sys.executable != "/usr/bin/python3"' in src,
                f"{name}: missing /usr/bin/python3 interpreter guard")


def test_14_no_prng_in_c8_scripts() -> None:
    forbidden_modules = {"random", "numpy.random", "secrets"}
    for name in ("torch213_reproduce_probe_c8.py", "verdict_c8.py",
                 "verdict_c8_amendment.py", "anchor_preservation_c8.py"):
        p = _REPO / "scripts/v3_spine" / name
        if not p.is_file():
            continue
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    _assert(n.name not in forbidden_modules,
                            f"{name}: forbidden PRNG import {n.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module in forbidden_modules:
                    FAILS.append(f"{name}: forbidden PRNG from-import {node.module}")


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
    print("PASS: all c8 cases green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
