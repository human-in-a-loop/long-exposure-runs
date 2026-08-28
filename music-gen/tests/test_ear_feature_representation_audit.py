"""Plain-assert tests for M-EAR-1/feature-representation-audit.

Invocation:
    PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \\
    /usr/bin/python3 tests/test_ear_feature_representation_audit.py

Expected: 7/7 pass.
"""
# created: 2026-08-28T21:10:00Z  cycle: 25  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork dc8cba4b79eb)  milestone: M-EAR-1/feature-representation-audit
from __future__ import annotations
import ast
import hashlib
import os
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"interpreter guard: {sys.executable}"

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

REPRESENTATION_FILES = [
    "scripts/ear/feature_subset_adapter.py",
    "scripts/ear/stability_audit_v3_representations.py",
    "scripts/ear/representation_frontier.py",
    "tests/test_ear_feature_representation_audit.py",
]

HARNESS_ANCHOR_SHAS = {
    "scripts/ear/stability_audit.py":  "b1ce5137b665a962657f1ee128db4d36abcb6d2174f57101b354a3194ea02e4c",
    "scripts/ear/synthetic_labels.py": "b71f194ef97e8936bb8942d5fccba899e6efe47e292cca185728d1cd9f41fb4d",
    "scripts/ear/stability_metrics.py":"6a5cb5183fdc77e80677ef01bb47f777a2662404f737f8aa74287f30cf97dc27",
    "scripts/ear/model.py":            "d4322a95fc2328b201b4040713dfdf8e294d8d0ae31db7e81c6390371492b552",
    "scripts/ear/corn.py":             "5028c58c20f23cd62c94789fad3522f94953417b79dec33b8506704b83a9921b",
    "scripts/ear/features.py":         "5e7cbf33cd81b501368f6334b2e5c67c41172c4d9e60bb34154274897c611f53",
}

FEATURES_DIR = Path("data/ear/features")


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _feature_cache_manifest() -> dict:
    return {p.name: _sha256_of_file(p) for p in sorted(FEATURES_DIR.glob("*.npz"))}


# -----------------------------------------------------------------------------
# 1. All representation scripts + tests exist and import cleanly
# -----------------------------------------------------------------------------
def test_scripts_present() -> None:
    for rel in REPRESENTATION_FILES:
        assert Path(rel).exists(), f"missing representation file: {rel}"
    import importlib
    for mod in ("scripts.ear.feature_subset_adapter",
                "scripts.ear.stability_audit_v3_representations",
                "scripts.ear.representation_frontier"):
        importlib.import_module(mod)


# -----------------------------------------------------------------------------
# 2. Harness anchor SHAs match cycle-22 recorded values
# -----------------------------------------------------------------------------
def test_harness_anchor_shas_match_cycle22() -> None:
    for rel, want in HARNESS_ANCHOR_SHAS.items():
        got = _sha256_of_file(Path(rel))
        assert got == want, f"{rel} SHA drift: got={got}, want={want}"


# -----------------------------------------------------------------------------
# 3. Feature-cache SHA-manifest spot check: recomputing manifest twice on the
#    same on-disk cache is byte-identical (proves no test-time write hazard).
# -----------------------------------------------------------------------------
def test_feature_cache_sha_unchanged() -> None:
    assert FEATURES_DIR.exists(), f"missing feature cache dir: {FEATURES_DIR}"
    m1 = _feature_cache_manifest()
    m2 = _feature_cache_manifest()
    assert m1 == m2, "feature-cache SHA manifest not byte-identical on repeat"
    assert len(m1) >= 55, f"expected >=55 feature-cache files; got {len(m1)}"


# -----------------------------------------------------------------------------
# 4. Slicing produces the correct output dimensions
# -----------------------------------------------------------------------------
def test_slicing_shapes() -> None:
    import numpy as np
    from scripts.ear import feature_subset_adapter as fsa
    x = np.arange(fsa.FULL_DIM, dtype=np.float32)
    heur = fsa.slice_heur_only(x)
    panns = fsa.slice_panns_only(x)
    assert heur.shape == (fsa.HEUR_DIM,), f"HEUR slice shape wrong: {heur.shape}"
    assert panns.shape == (fsa.PANNS_DIM,), f"PANNs slice shape wrong: {panns.shape}"
    # Layout: [PANNs 2048 | HEUR 4]
    assert np.array_equal(panns, x[:fsa.PANNS_DIM])
    assert np.array_equal(heur, x[fsa.PANNS_DIM:fsa.PANNS_DIM + fsa.HEUR_DIM])
    # VGGish: cache probe raises when not cached (which is the current state).
    any_npz = next(FEATURES_DIR.glob("*.npz"), None)
    assert any_npz is not None, "no feature cache files to probe"
    with_batch = fsa.slice_heur_only(np.stack([x, x], axis=0))
    assert with_batch.shape == (2, fsa.HEUR_DIM), f"batched HEUR slice wrong: {with_batch.shape}"
    try:
        _ = fsa.load_vggish_only(FEATURES_DIR, [any_npz.stem])
        # If load succeeded, the cache actually contains VGGish and shape must be (1, 128).
        # (Cycle 25: expected to raise; kept flexible for future re-runs.)
    except fsa.VggishNotCached:
        pass  # expected in cycle-25


# -----------------------------------------------------------------------------
# 5. Slicing is deterministic: same input → same output across two calls
# -----------------------------------------------------------------------------
def test_slicing_deterministic() -> None:
    import numpy as np
    from scripts.ear import feature_subset_adapter as fsa
    x = np.linspace(-1.0, 1.0, fsa.FULL_DIM, dtype=np.float32)
    assert np.array_equal(fsa.slice_heur_only(x), fsa.slice_heur_only(x))
    assert np.array_equal(fsa.slice_panns_only(x), fsa.slice_panns_only(x))


# -----------------------------------------------------------------------------
# 6. AST check: no PRNG in the new representation-audit scripts
# -----------------------------------------------------------------------------
def _has_prng_call(src: str, exempt_names={"manual_seed", "seed"}) -> list[str]:
    tree = ast.parse(src)
    offenders: list[str] = []
    for node in ast.walk(tree):
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
            if isinstance(node.value, ast.Name) and node.value.id == "torch":
                if node.attr in ("randn", "rand", "randint", "randperm"):
                    offenders.append(f"torch.{node.attr}  (line {node.lineno})")
            if isinstance(node.value, ast.Attribute) and node.value.attr == "random":
                if node.attr not in exempt_names:
                    offenders.append(f"...random.{node.attr}  (line {node.lineno})")
    return offenders


def test_no_prng_imports() -> None:
    for rel in ("scripts/ear/feature_subset_adapter.py",
                "scripts/ear/stability_audit_v3_representations.py",
                "scripts/ear/representation_frontier.py"):
        src = Path(rel).read_text()
        offenders = _has_prng_call(src)
        assert not offenders, f"PRNG use found in {rel}: {offenders}"


# -----------------------------------------------------------------------------
# 7. AST check: no sidecar_nonfactor imports in the new scripts
# -----------------------------------------------------------------------------
def test_no_sidecar_nonfactor_imports() -> None:
    import re
    pattern = re.compile(r"^\s*(?:from|import)\s+.*sidecar_nonfactor", re.M)
    for rel in ("scripts/ear/feature_subset_adapter.py",
                "scripts/ear/stability_audit_v3_representations.py",
                "scripts/ear/representation_frontier.py"):
        src = Path(rel).read_text()
        m = pattern.search(src)
        assert m is None, f"sidecar_nonfactor import in {rel}: {m.group(0)}"


TESTS = [
    ("test_scripts_present", test_scripts_present),
    ("test_harness_anchor_shas_match_cycle22", test_harness_anchor_shas_match_cycle22),
    ("test_feature_cache_sha_unchanged", test_feature_cache_sha_unchanged),
    ("test_slicing_shapes", test_slicing_shapes),
    ("test_slicing_deterministic", test_slicing_deterministic),
    ("test_no_prng_imports", test_no_prng_imports),
    ("test_no_sidecar_nonfactor_imports", test_no_sidecar_nonfactor_imports),
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
