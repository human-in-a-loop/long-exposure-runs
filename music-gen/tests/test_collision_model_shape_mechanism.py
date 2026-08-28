#!/usr/bin/env python3
"""Plain-assert test suite for the cycle-27 shape-mechanism probe branch.

Invocation:
  PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \
      /usr/bin/python3 tests/test_collision_model_shape_mechanism.py

8 tests total (brief floor is 7).  No pytest dependency.
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))

NEW_SCRIPTS = [
    "scripts/analysis/coercion_rate_per_rule_type.py",
    "scripts/analysis/effective_k_probe.py",
    "scripts/analysis/shape_mechanism_fit.py",
    "scripts/analysis/shape_mechanism_verdict.py",
    "scripts/analysis/anchor_preservation_shape.py",
]

# Frozen batch anchor SHAs (captured 2026-08-28 from ledger-recorded manifest).
FROZEN_BATCH_SHAS = {
    "data/gen/batch_v1": "b052d76716ca990d",
    "data/gen/batch_v2": "be5726ab1cc843cf",
    "data/gen/batch_v3_i3": "42bdc33d33987f4e",
    "data/gen/batch_v3_i4": "b07c231b9373818a",
    "data/gen/batch_v4": "9e9444af3af4b5c1",
    "data/gen/batch_v5_n16": "2f17ab559c37881f",
    "data/gen/batch_v6": "eeff1663d600a21d",
}

# Cycle-26 utility SHAs captured now — cycle-27 must NOT modify these files.
CYCLE_26_UTILITIES = [
    "scripts/analysis/canonical_aggregate_sha.py",
    "scripts/analysis/collision_model_bp.py",
    "scripts/analysis/collision_model_verdict.py",
]


def _file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _fail(msg):
    raise AssertionError(msg)


# 1. All five new scripts present and importable.
def test_scripts_present():
    for rel in NEW_SCRIPTS:
        p = ROOT / rel
        assert p.exists(), f"missing script: {rel}"
    # Import each module (no top-level side effects on import; entrypoints
    # are guarded by __main__).
    for mod in (
        "coercion_rate_per_rule_type",
        "effective_k_probe",
        "shape_mechanism_fit",
        "shape_mechanism_verdict",
        "anchor_preservation_shape",
    ):
        __import__(mod)
    print("[PASS] test_scripts_present")


# 2. Cycle-26 canonical_aggregate_sha utility unchanged (SHA-anchored at run
# time — the anchor is captured now against the current file so that a future
# edit trips this test).
def test_canonical_aggregate_sha_utility_untouched():
    p = ROOT / "scripts/analysis/canonical_aggregate_sha.py"
    live = _file_sha256(p)
    # Persist / read baseline on first run so future runs assert immutability.
    baseline_path = ROOT / "tests/fixtures/cycle27_util_shas.json"
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    if baseline_path.exists():
        baseline = json.loads(baseline_path.read_text())
    else:
        baseline = {}
    key = "canonical_aggregate_sha.py"
    if key in baseline:
        assert live == baseline[key], (
            f"canonical_aggregate_sha.py SHA changed: expected {baseline[key]}, got {live}"
        )
    else:
        baseline[key] = live
        baseline_path.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n")
    print("[PASS] test_canonical_aggregate_sha_utility_untouched")


# 3. Cycle-26 BP scripts unchanged.
def test_cycle26_bp_utility_untouched():
    baseline_path = ROOT / "tests/fixtures/cycle27_util_shas.json"
    baseline = json.loads(baseline_path.read_text()) if baseline_path.exists() else {}
    for rel in ("scripts/analysis/collision_model_bp.py",
                "scripts/analysis/collision_model_verdict.py"):
        p = ROOT / rel
        live = _file_sha256(p)
        key = pathlib.Path(rel).name
        if key in baseline:
            assert live == baseline[key], (
                f"{rel} SHA changed: expected {baseline[key]}, got {live}"
            )
        else:
            baseline[key] = live
    baseline_path.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n")
    print("[PASS] test_cycle26_bp_utility_untouched")


# 4. No PRNG imports in any of the 5 new scripts.
def test_no_prng_imports():
    banned = ("random", "secrets", "numpy.random", "numpy", "torch")
    # numpy/torch not strictly PRNG but we don't need them in this analytical
    # branch; keep the check strict to catch drift.
    for rel in NEW_SCRIPTS:
        src = (ROOT / rel).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    for b in banned:
                        assert not n.name.startswith(b), (
                            f"{rel} imports banned module {n.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for b in banned:
                    assert not mod.startswith(b), (
                        f"{rel} imports from banned module {mod}"
                    )
    print("[PASS] test_no_prng_imports")


def _imported_names(src: str) -> set[str]:
    names: set[str] = set()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                names.add(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module)
    return names


# 5. No sidecar_nonfactor imports (AST-level, not docstring text).
def test_no_sidecar_nonfactor_imports():
    for rel in NEW_SCRIPTS:
        src = (ROOT / rel).read_text()
        imports = _imported_names(src)
        for name in imports:
            assert "sidecar_nonfactor" not in name, (
                f"{rel} imports {name} which references sidecar_nonfactor"
            )
    print("[PASS] test_no_sidecar_nonfactor_imports")


# 6. i4_stratified.py is not imported (AST-level, not docstring text).
def test_i4_stratified_not_imported():
    for rel in NEW_SCRIPTS:
        src = (ROOT / rel).read_text()
        imports = _imported_names(src)
        for name in imports:
            assert "i4_stratified" not in name, (
                f"{rel} imports {name} which references i4_stratified"
            )
    print("[PASS] test_i4_stratified_not_imported")


# 7. Frozen batch aggregate SHAs (16-hex prefix match — sufficient discriminator).
def test_frozen_anchor_shas():
    sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
    from canonical_aggregate_sha import canonical_aggregate_sha
    for rel, expected_prefix in FROZEN_BATCH_SHAS.items():
        p = ROOT / rel
        assert p.exists(), f"anchor missing: {rel}"
        live = canonical_aggregate_sha(p)
        assert live.startswith(expected_prefix), (
            f"{rel}: expected prefix {expected_prefix}, live {live[:16]}"
        )
    print("[PASS] test_frozen_anchor_shas")


# 8. Verdict JSON has expected schema fields.
def test_shape_verdict_json_schema():
    p = ROOT / "data/collision_model/shape_mechanism_verdict.json"
    assert p.exists(), "verdict JSON missing — run scripts/analysis/shape_mechanism_verdict.py first"
    v = json.loads(p.read_text())
    for k in ("verdict", "verdict_reason", "R2_M1", "R2_M2",
              "rubric_thresholds", "rubric_definitions", "run_stamp"):
        assert k in v, f"verdict JSON missing key: {k}"
    assert v["verdict"] in (
        "M1_EXPLAINS", "M2_EXPLAINS", "BOTH_EXPLAIN", "NEITHER_EXPLAINS"
    ), f"verdict outside rubric: {v['verdict']}"
    assert v["rubric_thresholds"]["r2_min"] == 0.6, "r2_min threshold drift"
    assert v["rubric_thresholds"]["margin"] == 0.15, "margin threshold drift"
    print("[PASS] test_shape_verdict_json_schema")


def main():
    tests = [
        test_scripts_present,
        test_canonical_aggregate_sha_utility_untouched,
        test_cycle26_bp_utility_untouched,
        test_no_prng_imports,
        test_no_sidecar_nonfactor_imports,
        test_i4_stratified_not_imported,
        test_frozen_anchor_shas,
        test_shape_verdict_json_schema,
    ]
    n_pass = 0
    n_fail = 0
    for t in tests:
        try:
            t()
            n_pass += 1
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
            n_fail += 1
    print()
    print(f"result: {n_pass}/{len(tests)} PASS ({n_fail} FAIL)")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
