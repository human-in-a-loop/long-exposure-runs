#!/usr/bin/env python3
# ---
# created: 2026-08-28T23:10:00Z
# cycle: 28
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-hash-space-geometry
# ---
"""Test suite for cycle-28 hash-space-geometry branch.

Invocation:
    PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \
        /usr/bin/python3 tests/test_collision_model_hash_space_geometry.py

Plain asserts.  No pytest dependency.
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import re
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = pathlib.Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "scripts" / "analysis"
DATA = ROOT / "data" / "collision_model"
FIG = ROOT / "docs" / "figures"

NEW_SCRIPTS = (
    "plot_shape_mechanism_scatter.py",
    "hash_uniformity_per_rule_type.py",
    "effective_k_hash.py",
    "hash_geometry_fit.py",
    "hash_geometry_verdict.py",
    "anchor_preservation_hash.py",
)

BASELINE = json.loads((ROOT / "tests" / "fixtures" / "cycle28_util_shas.json").read_text())


def _sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_scripts_present() -> None:
    for name in NEW_SCRIPTS:
        p = ANALYSIS / name
        assert p.exists(), f"missing script: {p}"
        # Parse-check the module.
        ast.parse(p.read_text(), filename=str(p))
    print("PASS test_scripts_present")


def test_cycle26_utility_shas_unchanged() -> None:
    baseline = BASELINE["cycle_26_utilities"]
    for name, expected in baseline.items():
        p = ANALYSIS / name
        assert p.exists(), f"missing cycle-26 utility: {p}"
        got = _sha256(p)
        assert got == expected, f"cycle-26 utility drift: {name} {got} != {expected}"
    print("PASS test_cycle26_utility_shas_unchanged")


def test_cycle27_utility_shas_unchanged() -> None:
    baseline = BASELINE["cycle_27_utilities"]
    for name, expected in baseline.items():
        p = ANALYSIS / name
        assert p.exists(), f"missing cycle-27 utility: {p}"
        got = _sha256(p)
        assert got == expected, f"cycle-27 utility drift: {name} {got} != {expected}"
    print("PASS test_cycle27_utility_shas_unchanged")


def test_cycle27_data_untouched() -> None:
    baseline = BASELINE["cycle_27_data"]
    for name, expected in baseline.items():
        p = DATA / name
        assert p.exists(), f"missing cycle-27 data file: {p}"
        got = _sha256(p)
        assert got == expected, f"cycle-27 data drift: {name} {got} != {expected}"
    print("PASS test_cycle27_data_untouched")


def _get_imports(src: str) -> set[str]:
    tree = ast.parse(src)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                names.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module or "")
    return names


def test_no_prng_imports() -> None:
    banned = {"random", "numpy.random", "torch", "secrets"}
    for name in NEW_SCRIPTS:
        src = (ANALYSIS / name).read_text()
        imports = _get_imports(src)
        hit = imports & banned
        assert not hit, f"{name} imports banned PRNG modules: {hit}"
        # Also grep-check for 'np.random' patterns even without full import.
        assert not re.search(r"\bnp\.random\.", src), f"{name} uses np.random.*"
        assert not re.search(r"\brandom\.", src), f"{name} uses random.*"
    print("PASS test_no_prng_imports")


def test_no_sidecar_nonfactor_imports() -> None:
    for name in NEW_SCRIPTS:
        src = (ANALYSIS / name).read_text()
        # Reject only actual imports; docstring/discipline mentions permitted.
        assert not re.search(
            r"^\s*(import|from)\s+[^\n]*sidecar_nonfactor", src, flags=re.MULTILINE
        ), f"{name} imports sidecar_nonfactor"
    print("PASS test_no_sidecar_nonfactor_imports")


def test_i4_stratified_not_imported() -> None:
    for name in NEW_SCRIPTS:
        src = (ANALYSIS / name).read_text()
        assert not re.search(
            r"^\s*(import|from)\s+[^\n]*i4_stratified", src, flags=re.MULTILINE
        ), f"{name} imports i4_stratified"
    print("PASS test_i4_stratified_not_imported")


def test_frozen_anchor_shas() -> None:
    """The cycle-14/25 batch anchor SHA prefixes must match the plan-of-record."""
    sys.path.insert(0, str(ANALYSIS))
    import canonical_aggregate_sha as cas  # type: ignore

    expected = BASELINE["frozen_batch_shas_cycle26_baseline"]
    for rel, prefix in expected.items():
        p = ROOT / rel
        got = cas.canonical_aggregate_sha(p)
        assert got.startswith(prefix), f"{rel} SHA drift: {got[:8]} does not start with {prefix}"
    # Rules ledgers must be readable and non-empty.
    for rel in ("data/rules/ledger.jsonl", "data/rules/ledger_i3_dminor.jsonl"):
        p = ROOT / rel
        assert p.exists() and p.stat().st_size > 0, f"{rel} missing or empty"
    print("PASS test_frozen_anchor_shas")


def test_verdict_json_schema() -> None:
    v = json.loads((DATA / "hash_geometry_verdict.json").read_text())
    for field in ("verdict", "R2_M3", "per_rule_type_chi2", "rubric_thresholds", "run_stamp"):
        assert field in v, f"verdict JSON missing '{field}'"
    assert v["verdict"] in {"M3_EXPLAINS", "M3_WEAK", "M3_REFUTES"}
    # Per-rule_type chi2 covers 7 batches x 5 rule_types.
    assert len(v["per_rule_type_chi2"]) == 7 * 5, len(v["per_rule_type_chi2"])
    for row in v["per_rule_type_chi2"]:
        assert set(row.keys()) >= {"batch", "rule_type", "chi2", "dof", "p_value", "deviation_normalized"}
    print("PASS test_verdict_json_schema")


def test_alpha_pinned_at_cycle26_value() -> None:
    src = (ANALYSIS / "hash_geometry_fit.py").read_text()
    # Literal appearance of the pinned alpha.
    assert "0.7469387071101908" in src, "alpha literal 0.7469387071101908 missing from hash_geometry_fit.py"
    # Explicit "not refit" comment/language.
    assert re.search(r"pinn?ed|not refit|NOT REFIT|pinned", src), "alpha pin language missing"
    fit = json.loads((DATA / "hash_geometry_fit.json").read_text())
    assert abs(float(fit["M3"]["alpha_pinned"]) - 0.7469387071101908) < 1e-12
    print("PASS test_alpha_pinned_at_cycle26_value")


def test_backfill_figures_present() -> None:
    for name in (
        "shape_mechanism_M1_correction.png",
        "shape_mechanism_M2_correction.png",
        "hash_geometry_per_rule_type.png",
    ):
        p = FIG / name
        assert p.exists(), f"missing backfill/panel figure: {p}"
        assert p.stat().st_size > 4096, f"{p} suspiciously small ({p.stat().st_size} bytes)"
    print("PASS test_backfill_figures_present")


def test_hash_uniformity_covers_seven_batches() -> None:
    s = json.loads((DATA / "hash_uniformity_summary.json").read_text())
    expected = {
        "batch_v1",
        "batch_v2",
        "batch_v3_i3",
        "batch_v3_i4",
        "batch_v4",
        "batch_v5_n16",
        "batch_v6",
    }
    assert set(s["batches"].keys()) == expected, set(s["batches"].keys())
    for b, per_rt in s["batches"].items():
        assert set(per_rt.keys()) == {"harmonic", "rhythmic", "melodic", "form", "arrangement"}, b
    print("PASS test_hash_uniformity_covers_seven_batches")


def main() -> int:
    tests = [
        test_scripts_present,
        test_cycle26_utility_shas_unchanged,
        test_cycle27_utility_shas_unchanged,
        test_cycle27_data_untouched,
        test_no_prng_imports,
        test_no_sidecar_nonfactor_imports,
        test_i4_stratified_not_imported,
        test_frozen_anchor_shas,
        test_verdict_json_schema,
        test_alpha_pinned_at_cycle26_value,
        test_backfill_figures_present,
        test_hash_uniformity_covers_seven_batches,
    ]
    n = 0
    for t in tests:
        t()
        n += 1
    print(f"\nOK {n}/{n} tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
