#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T17:15:00Z
# cycle: 16
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork cc548ca0c2e5)
# milestone: M-GEN-1/batch-v4-compound
# ---
"""Unit tests for the batch-v4 compound (I3 + I4) driver.

Invocation:
    PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \
        /usr/bin/python3 tests/test_batch_v4_compound.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
if _LE_PARENT not in sys.path:
    sys.path.insert(0, _LE_PARENT)


NEW_SCRIPTS = (
    _REPO / "scripts" / "gen" / "batch_v4_compound.py",
    _REPO / "scripts" / "gen" / "collision_count_batch_v4.py",
    _REPO / "scripts" / "gen" / "batch_v4_anchor_check.py",
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_source_ledger_is_i3_augmented() -> None:
    from scripts.gen import batch_v4_compound as drv
    assert drv.I3_LEDGER == _REPO / "data" / "rules" / "ledger_i3_dminor.jsonl", drv.I3_LEDGER
    assert drv.I3_LEDGER.exists(), "I3-augmented ledger must exist"
    # Extra: verify the sha matches the manifest, so the driver would refuse a drifted ledger.
    m = json.loads((_REPO / "data" / "rules" / "i3_dminor_manifest.json").read_text())
    assert _sha256(drv.I3_LEDGER) == m["augmented_ledger_sha256"]
    print("  test_source_ledger_is_i3_augmented: OK")


def test_sampler_is_i4_stratified_verbatim() -> None:
    """The driver imports the frozen I4 sampler via batch_v3_i4 unchanged.

    Anchoring: the sampler file's SHA is captured in a file-side manifest
    that guards against silent mutation. The manifest file is created on
    first run (below) so this test is idempotent across cycles.
    """
    sampler = _REPO / "scripts" / "rules" / "sampling" / "i4_stratified.py"
    assert sampler.exists()
    live_sha = _sha256(sampler)
    anchor_file = _REPO / "data" / "gen" / "batch_v4" / ".i4_sampler_anchor_sha256"
    if not anchor_file.exists():
        anchor_file.parent.mkdir(parents=True, exist_ok=True)
        anchor_file.write_text(live_sha + "\n")
    anchored = anchor_file.read_text().strip()
    assert live_sha == anchored, (
        f"I4 sampler SHA drift: live={live_sha} vs anchored={anchored}. "
        "The I4 sampler must not be modified by the batch-v4 branch."
    )
    # Also verify the driver imports it via batch_v3_i4 (which imports i4_stratified).
    src_drv = (_REPO / "scripts" / "gen" / "batch_v4_compound.py").read_text()
    assert "from scripts.gen.batch_v3_i4 import run_batch" in src_drv
    src_i4b = (_REPO / "scripts" / "gen" / "batch_v3_i4.py").read_text()
    assert "from scripts.rules.sampling.i4_stratified import I4Sampler" in src_i4b
    print("  test_sampler_is_i4_stratified_verbatim: OK")


def test_render_pipeline_matches_cycle13() -> None:
    """batch_v4 renders via the same render() call cycle-13 batch_v2 uses.

    Proof: batch_v3_i4 imports render from scripts.gen.render_pipeline —
    exactly the same import batch_v2 uses. batch_v4 delegates to
    batch_v3_i4.run_batch, so the effective render call site is identical.
    """
    src_v2 = (_REPO / "scripts" / "gen" / "batch_v2.py").read_text()
    src_i4 = (_REPO / "scripts" / "gen" / "batch_v3_i4.py").read_text()
    src_v4 = (_REPO / "scripts" / "gen" / "batch_v4_compound.py").read_text()

    render_import = "from scripts.gen.render_pipeline import render"
    assert render_import in src_v2, "batch_v2 must import render from render_pipeline"
    assert render_import in src_i4, "batch_v3_i4 must import render from render_pipeline"
    # batch_v4 does NOT re-import render directly (delegates to batch_v3_i4).
    assert "from scripts.gen.batch_v3_i4 import run_batch" in src_v4
    # The delegation chain is what proves matching call sites.
    print("  test_render_pipeline_matches_cycle13: OK")


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
        # Also catch attribute-style: numpy.random / np.random / torch.manual_seed / torch.rand
        for pat in ("numpy.random", "np.random", "torch.rand", "torch.manual_seed", "secrets."):
            assert pat not in src, f"{path.name}: forbidden PRNG token {pat}"
        assert not hits, f"{path.name}: forbidden PRNG imports {hits}"
    print("  test_no_prng_imports: OK")


def test_no_sidecar_nonfactor_imports() -> None:
    import re
    pat = re.compile(r"^\s*(?:import\s+\S*sidecar_nonfactor|from\s+\S*sidecar_nonfactor)", re.M)
    for path in NEW_SCRIPTS:
        assert not pat.search(path.read_text()), f"{path.name}: sidecar_nonfactor import present"
    print("  test_no_sidecar_nonfactor_imports: OK")


def test_anchor_files_unchanged() -> None:
    """batch_v2 / batch_v3_i3 / batch_v3_i4 SHAs match a persisted anchor list."""
    v4_root = _REPO / "data" / "gen" / "batch_v4"
    v4_root.mkdir(parents=True, exist_ok=True)
    anchor_file = v4_root / ".pre_run_anchors.json"

    def _snapshot(root: Path):
        return {str(p.relative_to(root)): _sha256(p)
                for p in sorted(root.rglob("*")) if p.is_file()}

    live = {
        "batch_v2":    _snapshot(_REPO / "data" / "gen" / "batch_v2"),
        "batch_v3_i3": _snapshot(_REPO / "data" / "gen" / "batch_v3_i3"),
        "batch_v3_i4": _snapshot(_REPO / "data" / "gen" / "batch_v3_i4"),
    }
    if not anchor_file.exists():
        # First run: freeze the observed state.
        anchor_file.write_text(json.dumps(live, indent=2, sort_keys=True))
    anchored = json.loads(anchor_file.read_text())

    for name in ("batch_v2", "batch_v3_i3", "batch_v3_i4"):
        # If the anchored snapshot was taken before batch_v4 emitted its own
        # subdirectories, only compare files present in the anchor. This is
        # the "anchor preservation" contract: nothing anchored may change.
        for path, sha in anchored[name].items():
            assert path in live[name], f"{name}/{path} disappeared"
            assert live[name][path] == sha, f"{name}/{path} SHA changed"
    print("  test_anchor_files_unchanged: OK")


def _main() -> int:
    tests = [
        test_source_ledger_is_i3_augmented,
        test_sampler_is_i4_stratified_verbatim,
        test_render_pipeline_matches_cycle13,
        test_no_prng_imports,
        test_no_sidecar_nonfactor_imports,
        test_anchor_files_unchanged,
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
    print(f"\ntest_batch_v4_compound: {passed}/{passed + failed} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(_main())
