#!/usr/bin/env python3
"""Plain-assert test suite for the BP collision-model branch.

Invocation:
  PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \
      /usr/bin/python3 tests/test_collision_model_bp.py

10 tests total (brief floor is 7).  No pytest dependency.
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import shutil
import sys
import tempfile

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))

from scripts.analysis import collision_model_bp as bp  # noqa: E402
from scripts.analysis import collision_model_verdict as verdict  # noqa: E402
from scripts.analysis import canonical_aggregate_sha as cas  # noqa: E402
from scripts.analysis import anchor_preservation_bp as anchor  # noqa: E402


def _fail(msg: str):
    raise AssertionError(msg)


# ---------------------------------------------------------------------------
# 1. BP-pure formula
# ---------------------------------------------------------------------------
def test_bp_pure_formula():
    K = {"H": 5, "R": 5, "M": 5, "F": 5, "A": 5}
    per = bp.bp_pure_predict(5, K)
    for r, v in per.items():
        assert abs(v - 2.0) < 1e-12, f"{r}: expected 2.0 got {v}"
    total = sum(per.values())
    assert abs(total - 10.0) < 1e-12, f"total: expected 10.0 got {total}"
    print("[PASS] test_bp_pure_formula")


# ---------------------------------------------------------------------------
# 2. BP-pure zero pairs (N=1)
# ---------------------------------------------------------------------------
def test_bp_pure_zero_pairs():
    K = {"H": 5, "R": 5}
    per = bp.bp_pure_predict(1, K)
    for r, v in per.items():
        assert v == 0.0, f"{r}: expected 0.0 got {v}"
    print("[PASS] test_bp_pure_zero_pairs")


# ---------------------------------------------------------------------------
# 3. R^2 perfect fit
# ---------------------------------------------------------------------------
def test_r_squared_perfect_fit():
    obs = [1.0, 2.0, 3.0, 4.0]
    r2 = bp.r_squared(obs, obs)
    assert r2 is not None and abs(r2 - 1.0) < 1e-12, r2
    print("[PASS] test_r_squared_perfect_fit")


# ---------------------------------------------------------------------------
# 4. R^2 zero variance -> None
# ---------------------------------------------------------------------------
def test_r_squared_zero_variance_flag():
    obs = [3.0, 3.0, 3.0]
    pred = [1.0, 2.0, 3.0]
    r2 = bp.r_squared(obs, pred)
    assert r2 is None, f"expected None got {r2}"
    print("[PASS] test_r_squared_zero_variance_flag")


# ---------------------------------------------------------------------------
# 5. canonical_aggregate_sha determinism
# ---------------------------------------------------------------------------
def test_canonical_aggregate_sha_deterministic():
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td) / "fixture"
        d.mkdir()
        (d / "a.txt").write_text("hello\n")
        (d / "b.txt").write_text("world\n")
        sub = d / "sub"
        sub.mkdir()
        (sub / "c.txt").write_text("!\n")
        s1 = cas.canonical_aggregate_sha(d)
        s2 = cas.canonical_aggregate_sha(d)
        assert s1 == s2, f"{s1} != {s2}"
        assert len(s1) == 64 and all(c in "0123456789abcdef" for c in s1)
    print("[PASS] test_canonical_aggregate_sha_deterministic")


# ---------------------------------------------------------------------------
# 6. canonical_aggregate_sha detects change
# ---------------------------------------------------------------------------
def test_canonical_aggregate_sha_detects_change():
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td) / "fixture"
        d.mkdir()
        (d / "a.txt").write_bytes(b"hello\n")
        s1 = cas.canonical_aggregate_sha(d)
        (d / "a.txt").write_bytes(b"hellO\n")  # single-byte flip
        s2 = cas.canonical_aggregate_sha(d)
        assert s1 != s2, f"unchanged despite byte flip: {s1}"
    print("[PASS] test_canonical_aggregate_sha_detects_change")


# ---------------------------------------------------------------------------
# 7. Anchor preservation harness on synthetic ws
# ---------------------------------------------------------------------------
def test_anchor_preservation_harness_smoke():
    with tempfile.TemporaryDirectory() as td:
        ws = pathlib.Path(td)
        # Populate the 8 anchor paths with tiny fixtures
        for rel in anchor.ANCHOR_DIRS:
            p = ws / rel
            p.mkdir(parents=True)
            (p / "manifest.json").write_text('{"ok": true}\n')
        for rel in anchor.ANCHOR_FILES:
            p = ws / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('{"x": 1}\n')
        pre = anchor.capture(ws)
        post = anchor.capture(ws)
        rep = anchor.verify(pre, post)
        assert rep["overall_pass"], rep
        assert rep["count_pass"] == 8, rep
    print("[PASS] test_anchor_preservation_harness_smoke")


# ---------------------------------------------------------------------------
# 8. No PRNG in any of the four new scripts (AST)
# ---------------------------------------------------------------------------
_SCRIPTS = [
    ROOT / "scripts" / "analysis" / "canonical_aggregate_sha.py",
    ROOT / "scripts" / "analysis" / "collision_model_bp.py",
    ROOT / "scripts" / "analysis" / "collision_model_verdict.py",
    ROOT / "scripts" / "analysis" / "anchor_preservation_bp.py",
]
_FORBIDDEN_MODULES = {"random", "secrets"}
_FORBIDDEN_ATTRS = {"numpy.random", "torch.randn", "torch.rand"}


def _module_imports(tree: ast.AST) -> set[str]:
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                mods.add(n.name.split(".")[0])
                mods.add(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module.split(".")[0])
                mods.add(node.module)
    return mods


def test_no_prng_in_analysis_scripts():
    for s in _SCRIPTS:
        src = s.read_text()
        tree = ast.parse(src)
        imports = _module_imports(tree)
        forbidden = imports & _FORBIDDEN_MODULES
        assert not forbidden, f"{s.name} imports {forbidden}"
        # Substring check for attribute-style PRNG use
        for attr in _FORBIDDEN_ATTRS:
            assert attr not in src, f"{s.name} contains {attr}"
        # Also: torch import at all is forbidden here (analysis scripts)
        assert "torch" not in imports, f"{s.name} imports torch"
    print("[PASS] test_no_prng_in_analysis_scripts")


# ---------------------------------------------------------------------------
# 9. No sidecar_nonfactor imports (AST — docstrings/comments are legal)
# ---------------------------------------------------------------------------
def _imports_contain_substring(tree: ast.AST, needle: str) -> bool:
    """True iff any import statement in tree references `needle` in its
    module path (via `import X`, `import X.Y`, or `from X.Y import Z`)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                if needle in n.name:
                    return True
        elif isinstance(node, ast.ImportFrom):
            if node.module and needle in node.module:
                return True
    return False


def test_no_sidecar_nonfactor_imports():
    for s in _SCRIPTS:
        tree = ast.parse(s.read_text())
        assert not _imports_contain_substring(tree, "sidecar_nonfactor"), (
            f"{s.name} imports something matching sidecar_nonfactor"
        )
    print("[PASS] test_no_sidecar_nonfactor_imports")


# ---------------------------------------------------------------------------
# 10. i4_stratified NOT imported (AST — docstrings/comments are legal)
# ---------------------------------------------------------------------------
def test_i4_stratified_not_imported():
    for s in _SCRIPTS:
        tree = ast.parse(s.read_text())
        assert not _imports_contain_substring(tree, "i4_stratified"), (
            f"{s.name} imports something matching i4_stratified"
        )
    print("[PASS] test_i4_stratified_not_imported")


# ---------------------------------------------------------------------------
# Extra: end-to-end tiny synthetic fit
# ---------------------------------------------------------------------------
def test_end_to_end_synthetic_fit():
    K = {"H": 5, "R": 5, "M": 5, "F": 5, "A": 5}
    obs = [
        {
            "batch_id": "b_small",
            "N": 5,
            "K_by_rule_type": K,
            "sampler": "unconditioned",
            "observed_total": 10.0,
            "observed_per_rule_type": {"H": 2, "R": 2, "M": 2, "F": 2, "A": 2},
        },
        {
            "batch_id": "b_stratified",
            "N": 5,
            "K_by_rule_type": K,
            "sampler": "stratified",
            "observed_total": 0.0,
            "observed_per_rule_type": None,
        },
    ]
    result = bp.fit_bp(obs)
    assert abs(result["r2_pure"] - 1.0) < 1e-9, result["r2_pure"]
    v = verdict.apply_verdict(result, shape_batch_id="b_small")
    assert v["verdict"] == "CONFIRMS_BP_PURE", v
    print("[PASS] test_end_to_end_synthetic_fit")


ALL = [
    test_bp_pure_formula,
    test_bp_pure_zero_pairs,
    test_r_squared_perfect_fit,
    test_r_squared_zero_variance_flag,
    test_canonical_aggregate_sha_deterministic,
    test_canonical_aggregate_sha_detects_change,
    test_anchor_preservation_harness_smoke,
    test_no_prng_in_analysis_scripts,
    test_no_sidecar_nonfactor_imports,
    test_i4_stratified_not_imported,
    test_end_to_end_synthetic_fit,
]


if __name__ == "__main__":
    fails = 0
    for fn in ALL:
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"[FAIL] {fn.__name__}: {e}")
    print(f"---- {len(ALL) - fails}/{len(ALL)} tests passed")
    sys.exit(0 if fails == 0 else 1)
