"""Plain-assert tests for M-EAR-1/head-regularization-audit.

Invocation:
    PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \\
    /usr/bin/python3 tests/test_ear_head_regularization.py

Expected: 6/6 pass.
"""
# created: 2026-08-28T21:05:00Z  cycle: 23  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 3fbd8c1ab57c)  milestone: M-EAR-1/head-regularization-audit
from __future__ import annotations
import ast
import hashlib
import json
import os
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"interpreter guard: {sys.executable}"

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

VARIANT_FILES = [
    "scripts/ear/_variant_core.py",
    "scripts/ear/model_v2_ridge.py",
    "scripts/ear/model_v2_bottleneck.py",
    "scripts/ear/model_v2_frozen_projector.py",
    "scripts/ear/stability_audit_v2_variants.py",
    "scripts/ear/tau_mae_frontier.py",
]

HARNESS_ANCHOR_SHAS = {
    "scripts/ear/stability_audit.py":  "b1ce5137b665a962657f1ee128db4d36abcb6d2174f57101b354a3194ea02e4c",
    "scripts/ear/synthetic_labels.py": "b71f194ef97e8936bb8942d5fccba899e6efe47e292cca185728d1cd9f41fb4d",
}

PCA_BASIS = Path("data/ear/head_regularization_audit/pca_basis.npz")
PCA_SHA = Path("data/ear/head_regularization_audit/pca_basis.sha256")


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# -----------------------------------------------------------------------------
def test_variant_files_present() -> None:
    for rel in VARIANT_FILES:
        assert Path(rel).exists(), f"missing variant file: {rel}"
    # Report scripts + tests + driver should also import cleanly.
    import importlib
    for mod in ("scripts.ear._variant_core", "scripts.ear.model_v2_ridge",
                "scripts.ear.model_v2_bottleneck",
                "scripts.ear.model_v2_frozen_projector",
                "scripts.ear.stability_audit_v2_variants",
                "scripts.ear.tau_mae_frontier"):
        importlib.import_module(mod)


def test_harness_anchor_shas_match_cycle22() -> None:
    for rel, want in HARNESS_ANCHOR_SHAS.items():
        got = _sha256_of_file(Path(rel))
        assert got == want, f"{rel} SHA drift: got={got}, want={want}"


def test_pca_basis_pinned() -> None:
    assert PCA_BASIS.exists(), "missing pca_basis.npz"
    assert PCA_SHA.exists(), "missing pca_basis.sha256"
    observed = _sha256_of_file(PCA_BASIS)
    pinned = PCA_SHA.read_text().strip()
    assert observed == pinned, f"PCA basis SHA drift: got={observed}, pinned={pinned}"
    # Independent regeneration in a fresh temp dir must reproduce the same SHA.
    import numpy as np
    import shutil
    import tempfile
    from scripts.ear import model_v2_frozen_projector as fp
    with tempfile.TemporaryDirectory() as td:
        tmp_basis = Path(td) / "pca_basis.npz"
        tmp_sha = Path(td) / "pca_basis.sha256"
        sha = fp.ensure_pca_basis(basis_path=tmp_basis, sha_path=tmp_sha)
        assert sha == pinned, f"regenerated PCA SHA differs: got={sha}, pinned={pinned}"


def _has_prng_call(src: str, exempt_names={"manual_seed", "seed"}) -> list[str]:
    """AST-grep for PRNG use. Return list of offending call signatures."""
    tree = ast.parse(src)
    offenders: list[str] = []
    for node in ast.walk(tree):
        # random.<x>, numpy.random.<x>, torch.randn/randperm etc.
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "random":
                    offenders.append(f"import random  (line {node.lineno})")
                elif alias.name == "secrets":
                    offenders.append(f"import secrets  (line {node.lineno})")
        if isinstance(node, ast.ImportFrom):
            if node.module in ("random", "secrets"):
                offenders.append(f"from {node.module} import ...  (line {node.lineno})")
        if isinstance(node, ast.Attribute):
            # Reject torch.randn / torch.randperm / numpy.random.<x> etc.
            if isinstance(node.value, ast.Name) and node.value.id == "torch":
                if node.attr in ("randn", "rand", "randint", "randperm"):
                    offenders.append(f"torch.{node.attr}  (line {node.lineno})")
            if isinstance(node.value, ast.Attribute) and node.value.attr == "random":
                # numpy.random.<x> -> flag unless it's np.random.seed etc.
                if node.attr not in exempt_names:
                    offenders.append(f"...random.{node.attr}  (line {node.lineno})")
    return offenders


def test_no_prng_in_variant_scripts() -> None:
    for rel in ("scripts/ear/_variant_core.py",
                "scripts/ear/model_v2_ridge.py",
                "scripts/ear/model_v2_bottleneck.py",
                "scripts/ear/model_v2_frozen_projector.py",
                "scripts/ear/stability_audit_v2_variants.py",
                "scripts/ear/tau_mae_frontier.py"):
        src = Path(rel).read_text()
        offenders = _has_prng_call(src)
        assert not offenders, f"PRNG use found in {rel}: {offenders}"


def test_no_sidecar_nonfactor_imports() -> None:
    import re
    pattern = re.compile(r"^\s*(?:from|import)\s+.*sidecar_nonfactor", re.M)
    for rel in ("scripts/ear/_variant_core.py",
                "scripts/ear/model_v2_ridge.py",
                "scripts/ear/model_v2_bottleneck.py",
                "scripts/ear/model_v2_frozen_projector.py",
                "scripts/ear/stability_audit_v2_variants.py",
                "scripts/ear/tau_mae_frontier.py"):
        src = Path(rel).read_text()
        m = pattern.search(src)
        assert m is None, f"sidecar_nonfactor import in {rel}: {m.group(0)}"


def test_byte_determinism_smoke() -> None:
    """Spot-check: two invocations of a single-fold single-recipe run under
    variant 1 produce SHA-identical predictions."""
    import numpy as np
    from scripts.ear import model_v2_ridge as ridge
    # Deterministic tiny fixture.
    rng_state = np.zeros((10, 2052), dtype=np.float32)
    # Populate deterministically (hash-derived) — no PRNG.
    for i in range(10):
        h = hashlib.sha256(f"clip-{i}".encode()).digest()
        for j in range(2052):
            rng_state[i, j] = (h[j % 32] / 255.0) * 2 - 1
    y = np.array([1, 2, 3, 4, 5, 6, 7, 1, 2, 3], dtype=np.int64)
    pred1 = ridge._fit(rng_state[:7], y[:7], rng_state[7:], y[7:], seed=0, epochs=20)
    pred2 = ridge._fit(rng_state[:7], y[:7], rng_state[7:], y[7:], seed=0, epochs=20)
    assert (pred1 == pred2).all(), f"byte-determinism smoke failed: {pred1} vs {pred2}"


TESTS = [
    ("test_variant_files_present", test_variant_files_present),
    ("test_harness_anchor_shas_match_cycle22", test_harness_anchor_shas_match_cycle22),
    ("test_pca_basis_pinned", test_pca_basis_pinned),
    ("test_no_prng_in_variant_scripts", test_no_prng_in_variant_scripts),
    ("test_no_sidecar_nonfactor_imports", test_no_sidecar_nonfactor_imports),
    ("test_byte_determinism_smoke", test_byte_determinism_smoke),
]


def main() -> int:
    passed = 0
    failed: list[str] = []
    for name, fn in TESTS:
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except Exception as e:
            print(f"FAIL  {name}: {e}")
            failed.append(name)
    print(f"---- {passed}/{len(TESTS)} passed")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
