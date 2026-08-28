#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T16:15:00Z
# cycle: 15
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 392503ab7d47)
# milestone: M-GEN-1/batch-v3-i4
# ---
"""Unit tests for the I4 stratified rejection sampler.

Invocation: PYTHONPATH=. /usr/bin/python3 tests/test_i4_stratified.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import hashlib
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.rules.sampling.i4_stratified import (
    I4Sampler, sample_ruleset_i4, I4SamplerError, RULE_TYPES,
)
from scripts.gen.sample_rules import sample_ruleset


LEDGER = _REPO / "data" / "rules" / "ledger.jsonl"


def _rule_id_set(ledger_path: Path, salt: int) -> dict:
    rs = sample_ruleset(ledger_path, salt=salt)
    return rs.rule_ids()


def test_salt0_matches_batch_v2_anchor() -> None:
    """I4 at salt=0 with empty already_picked must match batch-v2 salt=0."""
    sampler = I4Sampler(LEDGER)
    rs0 = sampler.sample(0)
    anchor = _rule_id_set(LEDGER, 0)
    assert rs0.rule_ids() == anchor, f"salt=0 diverged from batch-v2 anchor: {rs0.rule_ids()} vs {anchor}"
    print("  test_salt0_matches_batch_v2_anchor: OK")


def test_determinism_same_input_same_output() -> None:
    """Two independent sampler runs must yield byte-identical selections."""
    s1 = I4Sampler(LEDGER)
    s2 = I4Sampler(LEDGER)
    for salt in range(8):
        r1 = s1.sample(salt)
        r2 = s2.sample(salt)
        assert r1.rule_ids() == r2.rule_ids(), f"nondeterminism at salt={salt}"
    print("  test_determinism_same_input_same_output: OK")


def test_distinct_salts_distinct_outputs() -> None:
    """Salts 0..7 must yield 8 distinct picks per rule_type under I4."""
    sampler = I4Sampler(LEDGER)
    per_type_ids = {rt: [] for rt in RULE_TYPES}
    for salt in range(8):
        rs = sampler.sample(salt)
        for rt, rid in rs.rule_ids().items():
            per_type_ids[rt].append(rid)
    for rt, ids in per_type_ids.items():
        assert len(ids) == 8, f"{rt}: expected 8 salts, got {len(ids)}"
        assert len(set(ids)) == 8, (
            f"{rt}: I4 produced duplicates within N=8: {ids} (this would falsify the 0-pair prediction)"
        )
    print("  test_distinct_salts_distinct_outputs: OK")


def test_stratification_predicate_on_synthetic_corpus() -> None:
    """Small synthetic corpus: sampler must skip already-picked rule_ids."""
    # Build a 6-rule ledger with 3 rule_types x 2 rules each.
    fake_rules = []
    counter = 0
    for rt in ("harmonic", "rhythmic", "melodic"):
        for i in range(2):
            rid = hashlib.sha256(f"{rt}-{i}".encode()).hexdigest()[:16]
            fake_rules.append({
                "event_type": "rule",
                "rule_id": f"rule_{rid}",
                "rule_type": rt,
                "schema_v": 1,
                "extractor_version": "test",
                "scope": {"level": "song", "start_s": 0.0, "end_s": 30.0},
                "provenance_pointers": [],
                "confidence": {"level": "high", "rationale": "synthetic", "assessor": "test"},
                "parameters": {"synthetic": True, "seed": f"{rt}-{i}"},
            })
    # Only harmonic/rhythmic/melodic used; form/arrangement will be missing —
    # sampler will raise cleanly, so we exercise sample_ruleset_i4 directly
    # by mocking the ledger with all 5 rule_types.
    for rt in ("form", "arrangement"):
        for i in range(2):
            rid = hashlib.sha256(f"{rt}-{i}".encode()).hexdigest()[:16]
            fake_rules.append({
                "event_type": "rule",
                "rule_id": f"rule_{rid}",
                "rule_type": rt,
                "schema_v": 1,
                "extractor_version": "test",
                "scope": {"level": "song", "start_s": 0.0, "end_s": 30.0},
                "provenance_pointers": [],
                "confidence": {"level": "high", "rationale": "synthetic", "assessor": "test"},
                "parameters": {"synthetic": True, "seed": f"{rt}-{i}"},
            })

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "synthetic_ledger.jsonl"
        p.write_text("\n".join(json.dumps(r, sort_keys=True) for r in fake_rules) + "\n")

        # salt=0: no exclusions -> any rule allowed
        s = I4Sampler(p)
        rs0 = s.sample(0)
        picks_0 = rs0.rule_ids()
        # salt=1: exclusion set now contains 5 rule_ids; only 5 remain (2-1=1 per type)
        rs1 = s.sample(1)
        picks_1 = rs1.rule_ids()
        for rt in RULE_TYPES:
            assert picks_0[rt] != picks_1[rt], f"{rt}: I4 failed to skip already-picked rule"
        # salt=2: every rule_type exhausted -> I4SamplerError
        raised = False
        try:
            s.sample(2)
        except I4SamplerError:
            raised = True
        assert raised, "I4 must raise when a rule_type is exhausted"
    print("  test_stratification_predicate_on_synthetic_corpus: OK")


def test_no_prng() -> None:
    """AST guard: source contains no `random`/`numpy.random`/`torch.*seed`/`secrets`."""
    src = (_REPO / "scripts" / "rules" / "sampling" / "i4_stratified.py").read_text()
    forbidden = ["import random", "from random", "numpy.random", "np.random", "torch.rand",
                 "torch.manual_seed", "secrets."]
    for tok in forbidden:
        assert tok not in src, f"I4 sampler must not use PRNG token: {tok}"
    print("  test_no_prng: OK")


def test_no_sidecar_import() -> None:
    """AST guard: source contains no sidecar_nonfactor import."""
    src = (_REPO / "scripts" / "rules" / "sampling" / "i4_stratified.py").read_text()
    import re
    # Match actual import statements only (not docstring mentions).
    pat = re.compile(r"^\s*(?:import\s+\S*sidecar_nonfactor|from\s+\S*sidecar_nonfactor)", re.M)
    assert not pat.search(src), "I4 sampler must not import sidecar_nonfactor"
    print("  test_no_sidecar_import: OK")


def _main() -> int:
    tests = [
        test_salt0_matches_batch_v2_anchor,
        test_determinism_same_input_same_output,
        test_distinct_salts_distinct_outputs,
        test_stratification_predicate_on_synthetic_corpus,
        test_no_prng,
        test_no_sidecar_import,
    ]
    passed = 0
    failed = 0
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
    print(f"\ntest_i4_stratified: {passed}/{passed + failed} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(_main())
