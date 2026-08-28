#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T23:30:00Z
# cycle: 25
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork dc8cba4b79eb)
# milestone: M-GEN-1/batch-v6-unconditioned-n16
# ---
"""Plain-assert suite for M-GEN-1/batch-v6-unconditioned-n16.

Invocation:
    PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \\
        /usr/bin/python3 tests/test_batch_v6_unconditioned.py

Seven named cases:
  1. source ledger is I3-augmented
  2. sampler is cycle-13 unconditioned (SHA matches recorded value)
  3. i4_stratified not imported
  4. salt range is exactly range(16)
  5. no PRNG imports
  6. no sidecar_nonfactor imports
  7. anchor SHAs unchanged (frozen batches + ledgers)
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

BATCH_V6_SCRIPTS = (
    "scripts/gen/batch_v6_unconditioned_n16.py",
    "scripts/gen/collision_count_batch_v6.py",
    "scripts/gen/batch_v6_hypothesis_verdict.py",
    "scripts/gen/batch_v6_anchor_check.py",
)

# Recorded cycle-13 unconditioned sampler canonical SHA (pre-flight, cycle 25).
SAMPLER_SHA = "7dcdcc03d1b3565f1f160a1de48150642218820f2e24fd482c223e12359e2a74"

I3_LEDGER_SHA = "1233efd5fd817141b22b8c625c97819d7534261625a7ed40806fc7b2c9b84645"


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _import_names(script: Path) -> list:
    """Return module dotted names from import / from statements via AST."""
    tree = ast.parse(script.read_text(), filename=str(script))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.append(node.module)
    return out


def test_source_ledger_is_i3_augmented():
    src = (_REPO / "scripts/gen/batch_v6_unconditioned_n16.py").read_text()
    assert "ledger_i3_dminor.jsonl" in src, "driver must read I3-augmented ledger"
    # And confirm identity.
    p = _REPO / "data/rules/ledger_i3_dminor.jsonl"
    n = sum(1 for l in p.open() if l.strip())
    assert n == 86, f"I3 ledger row count {n} != 86"
    print("[test1] PASS source_ledger_is_i3_augmented")


def test_sampler_is_cycle13_unconditioned():
    p = _REPO / "scripts/gen/sample_rules.py"
    assert p.exists(), "cycle-13 sample_rules.py must exist"
    actual = _sha256(p)
    assert actual == SAMPLER_SHA, f"sampler SHA drift: {actual} != {SAMPLER_SHA}"
    # And confirm the driver imports it (rather than i4).
    driver = (_REPO / "scripts/gen/batch_v6_unconditioned_n16.py").read_text()
    assert "from scripts.gen.sample_rules import sample_ruleset" in driver
    print("[test2] PASS sampler_is_cycle13_unconditioned")


def test_i4_stratified_not_imported():
    """AST check + line-anchored `^\\s*(import|from)` grep. Docstring and
    comment mentions of the name are permitted (they document the exclusion)."""
    import_line = re.compile(r"^\s*(import|from)\s+.*\bi4_stratified\b")
    hits = {}
    for rel in BATCH_V6_SCRIPTS:
        p = _REPO / rel
        assert p.exists(), f"script {rel} missing"
        for mod in _import_names(p):
            assert "i4_stratified" not in mod, f"{rel} AST-imports {mod}"
        text_hits = []
        for i, line in enumerate(p.read_text().splitlines(), 1):
            if import_line.match(line):
                text_hits.append(f"{i}:{line.strip()}")
        if text_hits:
            hits[rel] = text_hits
    assert not hits, f"i4_stratified imported: {hits}"
    print("[test3] PASS i4_stratified_not_imported")


def test_salt_range_0_to_15():
    from scripts.gen.batch_v6_unconditioned_n16 import SALTS
    assert SALTS == tuple(range(16)), f"SALTS={SALTS} != tuple(range(16))"
    print("[test4] PASS salt_range_0_to_15")


def test_no_prng_imports():
    forbidden_modules = {"random", "numpy.random", "secrets"}
    forbidden_attrs = {"torch.randn", "torch.rand", "np.random", "numpy.random"}
    for rel in BATCH_V6_SCRIPTS:
        p = _REPO / rel
        tree = ast.parse(p.read_text(), filename=str(p))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in forbidden_modules, \
                        f"{rel} imports {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module in forbidden_modules:
                    raise AssertionError(f"{rel} imports from {node.module}")
                if node.module and node.module.startswith("random"):
                    raise AssertionError(f"{rel} imports from {node.module}")
        # Text scan for the qualified attribute forms.
        text = p.read_text()
        for tok in forbidden_attrs:
            assert tok not in text, f"{rel} contains forbidden token {tok!r}"
    print("[test5] PASS no_prng_imports")


def test_no_sidecar_nonfactor_imports():
    for rel in BATCH_V6_SCRIPTS:
        p = _REPO / rel
        for mod in _import_names(p):
            assert "sidecar_nonfactor" not in mod, f"{rel} imports {mod}"
        text = p.read_text()
        assert "sidecar_nonfactor" not in text, f"{rel} mentions sidecar_nonfactor"
    print("[test6] PASS no_sidecar_nonfactor_imports")


def test_frozen_anchor_shas_unchanged():
    # I3-augmented ledger SHA — anchored on the recorded cycle-25 pre-flight.
    p = _REPO / "data/rules/ledger_i3_dminor.jsonl"
    assert _sha256(p) == I3_LEDGER_SHA, \
        f"I3 ledger drift: {_sha256(p)} != {I3_LEDGER_SHA}"

    # Frozen batches: aggregate SHA (first 16 hex) recorded from cycle-25 pre-flight.
    RECORDED_AGGS = {
        "batch_v2":     "912e07feeb81c8b6",
        "batch_v3_i3":  "f9f01a8728d6b0de",
        "batch_v3_i4":  "61566a46a28b0cec",
        "batch_v4":     "d5e0d926b1eae5bf",
        "batch_v5_n16": "49d611c5352ccc92",
    }

    def _agg(root: Path) -> str:
        lst = []
        for p in sorted(root.rglob("*")):
            if p.is_file():
                lst.append([str(p.relative_to(root)), _sha256(p)])
        return hashlib.sha256(json.dumps(lst, sort_keys=True).encode()).hexdigest()[:16]

    for name, want in RECORDED_AGGS.items():
        got = _agg(_REPO / "data" / "gen" / name)
        assert got == want, f"{name} agg drift: {got} != {want}"
    print("[test7] PASS frozen_anchor_shas_unchanged")


def main():
    tests = [
        test_source_ledger_is_i3_augmented,
        test_sampler_is_cycle13_unconditioned,
        test_i4_stratified_not_imported,
        test_salt_range_0_to_15,
        test_no_prng_imports,
        test_no_sidecar_nonfactor_imports,
        test_frozen_anchor_shas_unchanged,
    ]
    for t in tests:
        t()
    print(f"[test_batch_v6_unconditioned] {len(tests)}/{len(tests)} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
