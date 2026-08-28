#!/usr/bin/env python3
# M-RULES-1/schema — round-trip determinism + planted-invalid rejection tests.
#
# Author: cyd7bevdr@mozmail.com, cycle 6 (fork 3168fb0e47a1 / clone-1).
#
# Runs under /usr/bin/python3 with PYTHONPATH=. (repo root).
# No pytest dependency; plain assert + main() reports PASS/FAIL count.
# ≥25 synthetic instances round-trip; ≥10 planted invalids caught by name.

import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.rules import ledger as ledger_mod  # noqa: E402
from scripts.rules.ledger import (  # noqa: E402
    DEFAULT_LEDGER_PATH,
    LedgerError,
    _canonical_line,
    effective_rules,
    read_ledger,
    write_rule,
    write_supersede,
)
from scripts.rules.rule_id import canonical_json, derive_rule_id  # noqa: E402
from scripts.rules.validate import validate_batch, validate_row  # noqa: E402

EXAMPLES = _REPO / "scripts" / "rules" / "schema" / "examples"
RULE_TYPES = ["harmonic", "rhythmic", "melodic", "form", "arrangement"]

_passes = 0
_fails = 0


def _pass(msg):
    global _passes
    _passes += 1
    print(f"PASS {msg}")


def _fail(msg):
    global _fails
    _fails += 1
    print(f"FAIL {msg}", file=sys.stderr)


def _load_all_examples():
    rows = []
    for rt in RULE_TYPES:
        d = EXAMPLES / rt
        for p in sorted(d.glob("*.json")):
            with open(p) as f:
                rows.append((p, json.load(f)))
    return rows


def test_all_examples_validate():
    rows = _load_all_examples()
    per_type = {rt: 0 for rt in RULE_TYPES}
    for p, r in rows:
        errs = validate_row(r)
        if errs:
            _fail(f"validate_row {p.name}: {errs}")
            continue
        per_type[r["rule_type"]] += 1
    for rt in RULE_TYPES:
        if per_type[rt] >= 5:
            _pass(f"synthetic-instances/{rt}: {per_type[rt]} instances all validate")
        else:
            _fail(f"synthetic-instances/{rt}: only {per_type[rt]} instances (need >=5)")


def test_round_trip_determinism():
    """write→read→compare (canonical JSON identical) for every synthetic instance."""
    rows = _load_all_examples()
    for p, r in rows:
        line = _canonical_line(r)
        parsed = json.loads(line)
        if canonical_json(parsed) != canonical_json(r):
            _fail(f"round-trip {p.name}: canonical mismatch")
            return
    _pass(f"round-trip determinism: {len(rows)} instances write→read→identical")


def test_rule_id_reproducibility():
    """derive_rule_id is deterministic across two computes and matches the file."""
    rows = _load_all_examples()
    mismatch = 0
    for p, r in rows:
        a = derive_rule_id(r)
        b = derive_rule_id(r)
        if a != b:
            _fail(f"rule_id non-deterministic {p.name}: {a} != {b}")
            mismatch += 1
        if a != r.get("rule_id"):
            _fail(f"rule_id mismatch {p.name}: derived {a} != file {r.get('rule_id')}")
            mismatch += 1
    if mismatch == 0:
        _pass(f"rule_id reproducibility: {len(rows)} instances match committed value")


def _mk_valid_rule(rule_type):
    """Build a minimal valid rule of the given type for planting invalids."""
    for p, r in _load_all_examples():
        if r["rule_type"] == rule_type:
            return copy.deepcopy(r)
    raise RuntimeError(f"no example for {rule_type}")


def test_planted_invalid_unknown_rule_type():
    r = _mk_valid_rule("harmonic")
    r["rule_type"] = "symbolic"  # not in enum
    errs = validate_row(r)
    if any("rule_type" in e or "enum" in e or "'symbolic'" in e for e in errs):
        _pass("planted-invalid: unknown rule_type rejected")
    else:
        _fail(f"planted-invalid: unknown rule_type NOT rejected. errs={errs}")


def test_planted_invalid_missing_provenance():
    r = _mk_valid_rule("harmonic")
    r["provenance_pointers"] = []
    errs = validate_row(r)
    if any("provenance_pointers" in e and ("minItems" in e or "short" in e or "at least" in e or "non-empty" in e) for e in errs):
        _pass("planted-invalid: missing provenance_pointers (empty) rejected")
    else:
        _fail(f"planted-invalid: missing provenance NOT rejected. errs={errs}")


def test_planted_invalid_confidence_out_of_range():
    r = _mk_valid_rule("harmonic")
    r["confidence"] = 1.5
    errs = validate_row(r)
    if any("confidence" in e or "maximum" in e for e in errs):
        _pass("planted-invalid: confidence > 1 rejected")
    else:
        _fail(f"planted-invalid: confidence out-of-range NOT rejected. errs={errs}")

    r["confidence"] = -0.1
    errs = validate_row(r)
    if any("confidence" in e or "minimum" in e for e in errs):
        _pass("planted-invalid: confidence < 0 rejected")
    else:
        _fail(f"planted-invalid: negative confidence NOT rejected. errs={errs}")


def test_planted_invalid_pch_sum_mismatch():
    r = _mk_valid_rule("melodic")
    # Break sum-to-1 by shrinking bin 0 slightly.
    pch = list(r["parameters"]["pitch_class_histogram"])
    pch[0] = max(0.0, pch[0] - 0.001)
    r["parameters"]["pitch_class_histogram"] = pch
    r["rule_id"] = derive_rule_id(r)  # keep id consistent
    errs = validate_row(r)
    if any("pitch_class_histogram sum" in e for e in errs):
        _pass("planted-invalid: PCH sum != 1 rejected (Layer 2)")
    else:
        _fail(f"planted-invalid: PCH sum mismatch NOT rejected. errs={errs}")


def test_planted_invalid_form_bad_measure_order():
    r = _mk_valid_rule("form")
    r["parameters"]["sections"][0] = {"label": "A", "start_measure": 16, "end_measure": 16}
    r["rule_id"] = derive_rule_id(r)
    errs = validate_row(r)
    if any("end_measure" in e and "start_measure" in e for e in errs):
        _pass("planted-invalid: form section end_measure <= start_measure rejected")
    else:
        _fail(f"planted-invalid: bad measure order NOT rejected. errs={errs}")


def test_planted_invalid_scope_end_le_start():
    r = _mk_valid_rule("harmonic")
    r["scope"] = {"level": "section", "start_s": 30.0, "end_s": 30.0}
    r["rule_id"] = derive_rule_id(r)
    errs = validate_row(r)
    if any("scope.end_s" in e and "scope.start_s" in e for e in errs):
        _pass("planted-invalid: scope end_s <= start_s rejected (Layer 2)")
    else:
        _fail(f"planted-invalid: scope end_s <= start_s NOT rejected. errs={errs}")


def test_planted_invalid_additional_property():
    r = _mk_valid_rule("harmonic")
    r["genre"] = "rock"  # non-factor leak attempt — must be blocked by additionalProperties:false
    errs = validate_row(r)
    if any("additional" in e.lower() or "genre" in e for e in errs):
        _pass("planted-invalid: extra top-level field ('genre') rejected — non-factor leak blocked")
    else:
        _fail(f"planted-invalid: extra field NOT rejected. errs={errs}")


def test_planted_invalid_key_pattern():
    r = _mk_valid_rule("harmonic")
    r["parameters"]["key"] = "H_major"  # H is not a note letter
    r["rule_id"] = derive_rule_id(r)
    errs = validate_row(r)
    if any("key" in e.lower() or "pattern" in e for e in errs):
        _pass("planted-invalid: harmonic.key pattern violation rejected")
    else:
        _fail(f"planted-invalid: bad key pattern NOT rejected. errs={errs}")


def test_planted_invalid_swing_out_of_range():
    r = _mk_valid_rule("rhythmic")
    r["parameters"]["swing_ratio"] = 0.9  # > 0.75
    r["rule_id"] = derive_rule_id(r)
    errs = validate_row(r)
    if any("swing_ratio" in e or "maximum" in e for e in errs):
        _pass("planted-invalid: rhythmic.swing_ratio out of [0.5, 0.75] rejected")
    else:
        _fail(f"planted-invalid: bad swing_ratio NOT rejected. errs={errs}")


def _fresh_ledger():
    d = tempfile.mkdtemp(prefix="rules_ledger_test_")
    p = Path(d) / "ledger.jsonl"
    return p


def test_ledger_write_and_read():
    p = _fresh_ledger()
    r = _mk_valid_rule("harmonic")
    write_rule(r, path=p)
    rows = read_ledger(p)
    if len(rows) == 1 and rows[0]["rule_id"] == r["rule_id"]:
        _pass("ledger: write_rule + read_ledger round-trips single row")
    else:
        _fail(f"ledger: round-trip failed; rows={rows}")


def test_ledger_duplicate_rule_id_rejected():
    p = _fresh_ledger()
    r = _mk_valid_rule("harmonic")
    write_rule(r, path=p)
    caught = False
    try:
        write_rule(r, path=p)
    except LedgerError as e:
        caught = "duplicate rule_id" in str(e)
    if caught:
        _pass("ledger: duplicate rule_id rejected at write time")
    else:
        _fail("ledger: duplicate rule_id NOT rejected")


def test_ledger_supersede_missing_target_rejected():
    p = _fresh_ledger()
    caught = False
    try:
        write_supersede(
            {
                "event_type": "supersede",
                "schema_v": 1,
                "event_id": "a" * 32,
                "ts": "2026-08-28T00:00:00Z",
                "extractor": "test",
                "extractor_version": "1.0.0",
                "supersedes_rule_id": "rule_" + "0" * 16,
                "reason": "test",
                "new_rule_id": "rule_" + "1" * 16,
            },
            path=p,
        )
    except LedgerError as e:
        caught = "not found in ledger" in str(e)
    if caught:
        _pass("ledger: supersede pointing at nonexistent rule_id rejected")
    else:
        _fail("ledger: supersede target-missing NOT rejected")


def test_ledger_supersede_chain_effective():
    p = _fresh_ledger()
    # Write rule A.
    A = _mk_valid_rule("harmonic")
    write_rule(A, path=p)
    # Write rule B (different content -> different rule_id).
    B = _mk_valid_rule("harmonic")
    B["parameters"]["chord_progression"] = ["I", "IV", "V", "I"]
    B["rule_id"] = derive_rule_id(B)
    # Regenerate event_id to keep it unique (hash of rule_id).
    B["event_id"] = hashlib.sha256(("event::" + B["rule_id"]).encode()).hexdigest()[:32]
    write_rule(B, path=p)
    # Write supersede A -> B.
    sup = {
        "event_type": "supersede",
        "schema_v": 1,
        "event_id": hashlib.sha256(f"sup::{A['rule_id']}::{B['rule_id']}".encode()).hexdigest()[:32],
        "ts": "2026-08-28T00:00:00Z",
        "extractor": "test",
        "extractor_version": "1.0.0",
        "supersedes_rule_id": A["rule_id"],
        "reason": "chord progression refined",
        "new_rule_id": B["rule_id"],
    }
    write_supersede(sup, path=p)
    eff = effective_rules(p)
    ids = {r["rule_id"] for r in eff}
    if ids == {B["rule_id"]} and A["rule_id"] not in ids:
        _pass("ledger: supersede chain — effective_rules returns only B (A superseded)")
    else:
        _fail(f"ledger: effective_rules incorrect; got {ids}, expected only {B['rule_id']}")


def test_ledger_append_only_mode():
    """A test-only inspection: ledger.py only opens files with 'a' mode.

    We can't easily "attempt an in-place edit" from a caller — but we can
    grep the source to confirm no 'w' or 'r+' open() calls exist.
    """
    src = (_REPO / "scripts" / "rules" / "ledger.py").read_text()
    # Look for the two forbidden modes as string literals in open() calls.
    bad = []
    for forbidden in ('open(path, "w"', "open(path, 'w'", 'open(p, "w"', "open(p, 'w'",
                      'open(path, "r+"', "open(path, 'r+'", 'open(p, "r+"', "open(p, 'r+'"):
        if forbidden in src:
            bad.append(forbidden)
    if not bad:
        _pass("ledger: source contains no open() with 'w' or 'r+' — append-only enforced")
    else:
        _fail(f"ledger: source contains forbidden open modes: {bad}")


def test_batch_duplicate_rule_id_via_validate_batch():
    r = _mk_valid_rule("harmonic")
    r2 = copy.deepcopy(r)
    # Change the event_id so schema passes; keep rule_id same to trigger duplicate.
    r2["event_id"] = "b" * 32
    errs = validate_batch([r, r2])
    if any("duplicate rule_id" in e for e in errs):
        _pass("batch: duplicate rule_id across rows detected by validate_batch")
    else:
        _fail(f"batch: duplicate rule_id NOT detected. errs={errs}")


def test_yaml_json_equivalence():
    import yaml as yaml_mod
    jp = _REPO / "scripts" / "rules" / "schema" / "rules_v1.json"
    yp = _REPO / "scripts" / "rules" / "schema" / "rules_v1.yaml"
    with open(jp) as f:
        j = json.load(f)
    with open(yp) as f:
        y = yaml_mod.safe_load(f)
    if y == j:
        _pass("schema: rules_v1.yaml safe_load equals rules_v1.json parse exactly")
    else:
        _fail("schema: YAML/JSON mismatch")


def test_isolation_no_sidecar_import():
    """No file under scripts/rules/ imports scripts.classifier.sidecar_nonfactor.

    Grep for actual import statements only (import ... sidecar_nonfactor,
    from ... import sidecar_nonfactor). Mentions in comments/docstrings that
    describe the isolation contract are allowed.
    """
    import re
    root = _REPO / "scripts" / "rules"
    pat_import = re.compile(r"^\s*(?:from\s+\S*\bsidecar_nonfactor\b|import\s+\S*\bsidecar_nonfactor\b)", re.MULTILINE)
    offenders = []
    for p in root.rglob("*.py"):
        if pat_import.search(p.read_text()):
            offenders.append(p)
    if not offenders:
        _pass("isolation: scripts/rules/*.py never import scripts.classifier.sidecar_nonfactor")
    else:
        _fail(f"isolation: sidecar_nonfactor import found in: {offenders}")


def main():
    print("== M-RULES-1/schema tests ==")
    # Validation + determinism
    test_all_examples_validate()
    test_round_trip_determinism()
    test_rule_id_reproducibility()
    # Planted-invalid rejections (11 checks)
    test_planted_invalid_unknown_rule_type()
    test_planted_invalid_missing_provenance()
    test_planted_invalid_confidence_out_of_range()  # +2 checks
    test_planted_invalid_pch_sum_mismatch()
    test_planted_invalid_form_bad_measure_order()
    test_planted_invalid_scope_end_le_start()
    test_planted_invalid_additional_property()
    test_planted_invalid_key_pattern()
    test_planted_invalid_swing_out_of_range()
    # Ledger
    test_ledger_write_and_read()
    test_ledger_duplicate_rule_id_rejected()
    test_ledger_supersede_missing_target_rejected()
    test_ledger_supersede_chain_effective()
    test_ledger_append_only_mode()
    test_batch_duplicate_rule_id_via_validate_batch()
    # Schema equivalence + isolation
    test_yaml_json_equivalence()
    test_isolation_no_sidecar_import()

    print(f"\nresult: {'PASS' if _fails == 0 else 'FAIL'} ({_passes} pass, {_fails} fail)")
    sys.exit(0 if _fails == 0 else 1)


if __name__ == "__main__":
    main()
