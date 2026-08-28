"""Plain-assert test suite for M-EAR-1/synthetic-label-stability-audit.

Run:
    PYTHONPATH=. /usr/bin/python3 tests/test_ear_stability_audit.py
"""
# created: 2026-08-28T18:00:00Z  cycle: 22  run_id: run-2026-08-28T040704Z
# agent: worker (clone-2, fork cc548ca0c2e5)  milestone: M-EAR-1/synthetic-label-stability-audit
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
from scripts.ear.synthetic_labels import (  # noqa: E402
    RECIPES,
    apply_recipe,
    salt_for,
    recipe_hash_noise,
    recipe_linear_projection,
    recipe_nonlinear,
    recipe_signed_popcount,
    _sha_int,
    _impute,
    K,
)
from scripts.ear.stability_metrics import (  # noqa: E402
    kendall_tau_exact,
    mae_envelope,
    per_clip_band_variance,
)


def _tiny_features(n_clips: int = 55, dim: int = 2052) -> dict:
    """Deterministic synthetic feature block for tests (no PRNG)."""
    ids = [f"clip_{i:04d}" for i in range(n_clips)]
    X = np.zeros((n_clips, dim), dtype=np.float32)
    for i in range(n_clips):
        for j in range(dim):
            X[i, j] = ((i * 31 + j * 17) % 991) / 991.0 - 0.5
    return {ids[i]: X[i] for i in range(n_clips)}


# ---------------------------------------------------------------------------
# 1. Recipe determinism: label_i(f, salt) == label_i(f, salt)
# ---------------------------------------------------------------------------
def test_recipe_determinism():
    feats = _tiny_features()
    for r in RECIPES:
        y1 = apply_recipe(r, feats)
        y2 = apply_recipe(r, feats)
        assert y1 == y2, f"recipe {r['idx']} is nondeterministic"


# ---------------------------------------------------------------------------
# 2. Distinct salts produce distinct label vectors
# ---------------------------------------------------------------------------
def test_recipes_are_distinct():
    feats = _tiny_features()
    labels = [apply_recipe(r, feats) for r in RECIPES]
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            assert labels[i] != labels[j], (
                f"recipes {i} and {j} produced identical labels"
            )


# ---------------------------------------------------------------------------
# 3. Rank-quantized recipes span 7 bins with equal-population (± 1)
# ---------------------------------------------------------------------------
def test_rank_quantized_span_all_7_bins():
    feats = _tiny_features()
    for r in RECIPES:
        if r["family"] == "hash-noise":
            continue  # pure hash may skip bins
        y = list(apply_recipe(r, feats).values())
        bins_present = {v for v in y}
        assert bins_present == set(range(1, K + 1)), (
            f"recipe {r['idx']} ({r['family']}) missing bins: got {sorted(bins_present)}"
        )
        # Equal population (± 1) for rank-quantize
        from collections import Counter
        cnt = Counter(y)
        counts = list(cnt.values())
        assert max(counts) - min(counts) <= 1, (
            f"recipe {r['idx']} bin populations not equal-±1: {sorted(counts)}"
        )


# ---------------------------------------------------------------------------
# 4. Kendall τ toy example (hand-verified)
# ---------------------------------------------------------------------------
def test_kendall_tau_toy():
    # Perfectly correlated
    res = kendall_tau_exact([1, 2, 3, 4], [10, 20, 30, 40])
    assert abs(res["tau_b"] - 1.0) < 1e-12, res
    # Perfectly anti-correlated
    res = kendall_tau_exact([1, 2, 3, 4], [40, 30, 20, 10])
    assert abs(res["tau_b"] - (-1.0)) < 1e-12, res
    # Hand-verified: [1,2,3,4] vs [1,3,2,4]
    # Pairs (0,1)(0,2)(0,3)(1,2)(1,3)(2,3): C=5, D=1 → τ = (5-1)/6 = 0.667
    res = kendall_tau_exact([1, 2, 3, 4], [1, 3, 2, 4])
    assert res["n_concordant"] == 5 and res["n_discordant"] == 1, res
    assert abs(res["tau_b"] - 4.0 / 6.0) < 1e-12, res
    # With ties
    res = kendall_tau_exact([1, 1, 2, 3], [1, 2, 2, 3])
    # Pairs: (0,1) a-tie,     (0,2) C,  (0,3) C,
    #        (1,2) b-tie,     (1,3) C,  (2,3) C
    # nc=4 nd=0 ta=1 tb=1
    assert res["n_concordant"] == 4 and res["n_discordant"] == 0, res
    assert res["n_tied_a"] == 1 and res["n_tied_b"] == 1, res
    # τ_b = 4 / sqrt((6-1)*(6-1)) = 0.8
    assert abs(res["tau_b"] - 0.8) < 1e-12, res


# ---------------------------------------------------------------------------
# 5. mae_envelope matches numpy percentile on synthetic sample
# ---------------------------------------------------------------------------
def test_mae_envelope_matches_numpy():
    vals = [0.5, 0.7, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5, 1.8, 2.0]
    e = mae_envelope(vals)
    assert abs(e["p05"] - float(np.percentile(vals, 5.0, method="linear"))) < 1e-12
    assert abs(e["p50"] - float(np.percentile(vals, 50.0, method="linear"))) < 1e-12
    assert abs(e["p95"] - float(np.percentile(vals, 95.0, method="linear"))) < 1e-12
    assert abs(e["mean"] - float(np.mean(vals))) < 1e-12


# ---------------------------------------------------------------------------
# 6. Byte-determinism: two full driver invocations produce SHA-256-equal
#    stability_report.json. This is C3 itself.
# ---------------------------------------------------------------------------
def test_c3_byte_determinism():
    report = ROOT / "data" / "ear" / "stability_audit" / "stability_report.json"
    if not report.exists():
        # Test is invoked before the full run has been triggered — skip.
        print(
            "[skip] stability_report.json not yet generated;"
            " run scripts/ear/stability_audit.py first."
        )
        return
    # Re-run the driver into a scratch directory and compare SHA-256 to the
    # committed report. Uses --epochs 200 (default) so it exactly reproduces.
    scratch = ROOT / "data" / "ear" / "stability_audit_c3check"
    cmd = [
        "/usr/bin/python3", "-m", "scripts.ear.stability_audit",
        "--epochs", "200", "--out-dir", str(scratch),
    ]
    env = {
        "PATH": "/usr/bin:/bin",
        "PYTHONPATH": str(ROOT),
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "PYTHONHASHSEED": "0",
    }
    subprocess.run(cmd, check=True, cwd=ROOT, env=env)
    a = hashlib.sha256(report.read_bytes()).hexdigest()
    b = hashlib.sha256((scratch / "stability_report.json").read_bytes()).hexdigest()
    assert a == b, f"C3 byte-determinism FAILED: committed={a} rerun={b}"


# ---------------------------------------------------------------------------
# 7. Interpreter guard rejects wrong Python
# ---------------------------------------------------------------------------
def test_interpreter_guard_present():
    for mod_name in ("synthetic_labels", "stability_metrics", "stability_audit"):
        src = (ROOT / "scripts" / "ear" / f"{mod_name}.py").read_text()
        assert "from . import _interp" in src, f"{mod_name} missing _interp guard"


# ---------------------------------------------------------------------------
# 8. AST: no sidecar_nonfactor imports; no PRNG in recipe code
# ---------------------------------------------------------------------------
def test_no_sidecar_nonfactor_imports():
    for mod_name in ("synthetic_labels", "stability_metrics", "stability_audit"):
        src = (ROOT / "scripts" / "ear" / f"{mod_name}.py").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert "sidecar_nonfactor" not in (node.module or ""), (
                    f"{mod_name} imports sidecar_nonfactor"
                )
            if isinstance(node, ast.Import):
                for al in node.names:
                    assert "sidecar_nonfactor" not in al.name, (
                        f"{mod_name} imports sidecar_nonfactor"
                    )


def test_recipe_code_has_no_prng():
    """AST-check scripts/ear/synthetic_labels.py for forbidden PRNG symbols."""
    src = (ROOT / "scripts" / "ear" / "synthetic_labels.py").read_text()
    tree = ast.parse(src)
    # Forbidden names anywhere in the AST (attribute access or bare).
    banned = {"random", "secrets", "default_rng", "RandomState", "randn"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in banned:
            raise AssertionError(f"PRNG symbol used in synthetic_labels.py: .{node.attr}")
        if isinstance(node, ast.Name) and node.id in banned:
            raise AssertionError(f"PRNG symbol used in synthetic_labels.py: {node.id}")


# ---------------------------------------------------------------------------
# 9. Feature-imputation removes all NaN
# ---------------------------------------------------------------------------
def test_impute_removes_nans():
    X = np.array([[1.0, np.nan, 3.0], [np.nan, 2.0, np.nan], [5.0, 4.0, 3.0]])
    Y = _impute(X)
    assert not np.isnan(Y).any(), Y
    # Column means preserved on non-NaN
    assert Y[0, 0] == 1.0 and Y[2, 0] == 5.0
    # NaN in col 0 imputed to mean(1, 5) = 3.0
    assert abs(Y[1, 0] - 3.0) < 1e-12


# ---------------------------------------------------------------------------
# 10. Per-clip band variance shape + non-negativity
# ---------------------------------------------------------------------------
def test_per_clip_band_variance_shape():
    ranks = np.array([[1, 2, 3], [4, 4, 4], [1, 3, 5], [7, 7, 1]], dtype=np.int64)
    r = per_clip_band_variance(ranks)
    assert r["mean_rank"].shape == (4,)
    assert r["band_variance"].shape == (4,)
    assert (r["band_variance"] >= 0).all()
    assert abs(r["band_variance"][1]) < 1e-12  # constant row → 0 variance


# ---------------------------------------------------------------------------
# 11. Salt namespace is stab-audit-*
# ---------------------------------------------------------------------------
def test_salt_namespace():
    for i, r in enumerate(RECIPES):
        assert r["salt"] == f"stab-audit-{i}", r
        assert r["salt"] == salt_for(i), r


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def _run_all():
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        name = t.__name__
        try:
            t()
        except Exception as e:
            failed += 1
            print(f"FAIL  {name}: {e}")
        else:
            print(f"pass  {name}")
    if failed:
        raise SystemExit(f"{failed}/{len(tests)} tests FAILED")
    print(f"\n{len(tests)}/{len(tests)} tests passed")


if __name__ == "__main__":
    _run_all()
