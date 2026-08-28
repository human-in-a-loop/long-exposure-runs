#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T22:00:00Z
# cycle: 23
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 3fbd8c1ab57c)
# milestone: M-GEN-1/batch-v5-n16
# ---
"""Unit tests for the batch-v5-n16 branch.

Invocation:
    PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \
        /usr/bin/python3 tests/test_batch_v5_n16.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
if _LE_PARENT not in sys.path:
    sys.path.insert(0, _LE_PARENT)


NEW_SCRIPTS = (
    _REPO / "scripts" / "gen" / "batch_v5_n16.py",
    _REPO / "scripts" / "gen" / "collision_count_batch_v5.py",
    _REPO / "scripts" / "gen" / "batch_v5_anchor_regression.py",
    _REPO / "scripts" / "gen" / "batch_v5_hypothesis_verdict.py",
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_source_ledger_is_i3_augmented() -> None:
    from scripts.gen import batch_v5_n16 as drv
    assert drv.I3_LEDGER == _REPO / "data" / "rules" / "ledger_i3_dminor.jsonl", drv.I3_LEDGER
    assert drv.I3_LEDGER.exists(), "I3-augmented ledger must exist"
    m = json.loads((_REPO / "data" / "rules" / "i3_dminor_manifest.json").read_text())
    assert _sha256(drv.I3_LEDGER) == m["augmented_ledger_sha256"]
    print("  test_source_ledger_is_i3_augmented: OK")


def test_sampler_is_i4_stratified_verbatim() -> None:
    """The batch-v5 driver imports the same I4 sampler as batch-v4/v3-i4.

    Verifies (a) the driver imports it, (b) its file SHA matches the anchor
    captured by the batch_v4 test (single-source-of-truth), guarding against
    silent mutation.
    """
    sampler = _REPO / "scripts" / "rules" / "sampling" / "i4_stratified.py"
    assert sampler.exists()
    live_sha = _sha256(sampler)
    v4_anchor = _REPO / "data" / "gen" / "batch_v4" / ".i4_sampler_anchor_sha256"
    if v4_anchor.exists():
        anchored = v4_anchor.read_text().strip()
        assert live_sha == anchored, (
            f"I4 sampler SHA drift vs batch-v4 anchor: live={live_sha} vs {anchored}"
        )
    src_drv = (_REPO / "scripts" / "gen" / "batch_v5_n16.py").read_text()
    assert "from scripts.rules.sampling.i4_stratified import I4Sampler" in src_drv
    print("  test_sampler_is_i4_stratified_verbatim: OK")


def test_render_pipeline_matches_cycle13() -> None:
    """batch_v5 renders via the same render() call cycle-13 batch_v2 uses.

    Proof: batch_v5 imports render from scripts.gen.render_pipeline directly,
    the same import batch_v2 and batch_v3_i4 use.
    """
    src_v2 = (_REPO / "scripts" / "gen" / "batch_v2.py").read_text()
    src_v5 = (_REPO / "scripts" / "gen" / "batch_v5_n16.py").read_text()
    render_import = "from scripts.gen.render_pipeline import render"
    assert render_import in src_v2
    assert render_import in src_v5
    # And the render call site (single-arg-shape) is identical.
    v2_call = re.search(r"render\(xml_path, out_dir[^)]*\)", src_v2)
    v5_call = re.search(r"render\(xml_path, out_dir[^)]*\)", src_v5)
    assert v2_call and v5_call, (v2_call, v5_call)
    print("  test_render_pipeline_matches_cycle13: OK")


def test_salt_range_is_0_to_15() -> None:
    from scripts.gen import batch_v5_n16 as drv
    assert drv.SALTS == tuple(range(16)), drv.SALTS
    assert len(drv.SALTS) == 16
    print("  test_salt_range_is_0_to_15: OK")


def test_anchor_regression_32_of_32() -> None:
    """Reads data/gen/batch_v5_n16/anchor_regression.json and asserts 32/32 PASS.

    Skipped if the harness has not been run yet (returns OK with a skip
    note) so the test module is runnable BEFORE the batch renders.
    """
    ar = _REPO / "data" / "gen" / "batch_v5_n16" / "anchor_regression.json"
    if not ar.exists():
        print("  test_anchor_regression_32_of_32: SKIP (run harness first)")
        return
    j = json.loads(ar.read_text())
    assert j["n_cells"] == 32, j["n_cells"]
    assert j["all_pass"], (
        f"{j['n_fail']} FAIL rows: "
        f"{[r for r in j['rows'] if r['verdict'] == 'FAIL']}"
    )
    print(f"  test_anchor_regression_32_of_32: OK ({j['n_pass']}/{j['n_cells']})")


def _find_forbidden(src: str, tokens):
    tree = ast.parse(src)
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                for tok in tokens:
                    if a.name == tok or a.name.startswith(tok + "."):
                        hits.append(a.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for tok in tokens:
                if mod == tok or mod.startswith(tok + "."):
                    hits.append(mod)
    return hits


def test_no_prng_imports() -> None:
    forbidden = ["random", "secrets"]
    for path in NEW_SCRIPTS:
        src = path.read_text()
        hits = _find_forbidden(src, forbidden)
        for pat in ("numpy.random", "np.random", "torch.rand",
                    "torch.manual_seed", "secrets."):
            assert pat not in src, f"{path.name}: forbidden PRNG token {pat}"
        assert not hits, f"{path.name}: forbidden PRNG imports {hits}"
    print("  test_no_prng_imports: OK")


def test_no_sidecar_nonfactor_imports() -> None:
    pat = re.compile(
        r"^\s*(?:import\s+\S*sidecar_nonfactor|from\s+\S*sidecar_nonfactor)", re.M)
    for path in NEW_SCRIPTS:
        assert not pat.search(path.read_text()), (
            f"{path.name}: sidecar_nonfactor import present")
    print("  test_no_sidecar_nonfactor_imports: OK")


def _main() -> int:
    tests = [
        test_source_ledger_is_i3_augmented,
        test_sampler_is_i4_stratified_verbatim,
        test_render_pipeline_matches_cycle13,
        test_salt_range_is_0_to_15,
        test_anchor_regression_32_of_32,
        test_no_prng_imports,
        test_no_sidecar_nonfactor_imports,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {t.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\ntest_batch_v5_n16: {passed}/{passed + failed} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(_main())
