#!/usr/bin/env python3
# M-RULES-1/extraction — plain-assert test suite (no pytest).
# Invocation: PYTHONPATH=. /usr/bin/python3 tests/test_rules_extraction.py

import hashlib
import os
import sys
import tempfile
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.rules.extract.from_score import run, build_rules
from scripts.rules.extract._common import (
    transcription_event_id, STEMS, SCORE_PATH, BP_DIR,
)
from scripts.rules.ledger import read_ledger, effective_rules
from scripts.rules.validate import validate_batch


PASS = FAIL = 0


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {msg}")
    else:
        FAIL += 1
        print(f"  FAIL {msg}")


def test_frozen_inputs_exist():
    print("[1] frozen inputs exist")
    check(SCORE_PATH.exists(), f"merged XML at {SCORE_PATH}")
    for stem in STEMS:
        p = BP_DIR / f"{stem}.jsonl"
        check(p.exists(), f"basic-pitch jsonl at {p}")


def test_dry_run_produces_expected_shape():
    print("[2] extractor dry-run produces >=25 rows with >=5 per rule_type")
    import music21
    score = music21.converter.parse(str(SCORE_PATH))
    rules = build_rules(score)
    check(len(rules) >= 25, f"aggregate n_rules={len(rules)} >= 25")
    per_type = {}
    for r in rules:
        per_type[r["rule_type"]] = per_type.get(r["rule_type"], 0) + 1
    for t in ("harmonic","rhythmic","melodic","form","arrangement"):
        check(per_type.get(t, 0) >= 5, f"rule_type {t} count={per_type.get(t,0)} >= 5")


def test_validation_clean():
    print("[3] every row passes validate_batch")
    import music21
    score = music21.converter.parse(str(SCORE_PATH))
    rules = build_rules(score)
    errors = validate_batch(rules)
    check(len(errors) == 0, f"validate_batch errors={len(errors)}")
    if errors:
        for e in errors[:5]:
            print("     ", e)


def test_determinism_byte_identical():
    print("[4] two independent runs produce byte-identical ledger files")
    with tempfile.TemporaryDirectory() as d:
        a = Path(d) / "a.jsonl"
        b = Path(d) / "b.jsonl"
        s1 = run(ledger_path=a)
        s2 = run(ledger_path=b)
        sha_a = hashlib.sha256(a.read_bytes()).hexdigest()
        sha_b = hashlib.sha256(b.read_bytes()).hexdigest()
        check(s1["rule_ids"] == s2["rule_ids"], "rule_id sequences equal")
        check(sha_a == sha_b, "ledger byte-hashes equal")


def test_ledger_roundtrip_and_provenance():
    print("[5] read_ledger insertion order + effective_rules + provenance resolves")
    rows = read_ledger()
    eff = effective_rules()
    check(len(rows) >= 25, f"live ledger rows n={len(rows)} >= 25")
    check(len(eff) == len(rows), f"effective_rules ({len(eff)}) == read_ledger ({len(rows)})")
    # insertion order
    first_seen = []
    prev = None
    for r in rows:
        if r.get("rule_type") != prev:
            first_seen.append(r["rule_type"])
            prev = r["rule_type"]
    expected = ["harmonic","rhythmic","melodic","form","arrangement"]
    # allow rows outside the current cycle; only require that the last five
    # first-seen types match, in order
    check(first_seen[-5:] == expected or first_seen == expected,
          f"insertion order tail matches {expected} (got {first_seen})")

    # provenance: every pointer must resolve to a recomputable
    # transcription_event_id from the frozen input files.
    known_te = {transcription_event_id(t) for t in ("score",) + STEMS}
    n_ok = n_total = 0
    for r in rows:
        for p in r.get("provenance_pointers", []):
            n_total += 1
            if p.get("transcription_event_id") in known_te:
                n_ok += 1
    check(n_ok == n_total, f"provenance {n_ok}/{n_total} resolvable")


def test_non_factor_isolation_ast():
    print("[6] extractor modules do not import scripts.classifier.sidecar_nonfactor")
    import re
    pat = re.compile(r"^\s*(?:from|import)\s+scripts\.classifier\.sidecar_nonfactor")
    ext_dir = _REPO / "scripts" / "rules" / "extract"
    for py in sorted(ext_dir.glob("*.py")):
        text = py.read_text()
        hits = [ln for ln in text.splitlines() if pat.match(ln)]
        check(len(hits) == 0, f"{py.name}: 0 sidecar_nonfactor imports (got {len(hits)})")


def test_interpreter_guard_present():
    print("[7] every extractor module carries the /usr/bin/python3 interpreter guard")
    ext_dir = _REPO / "scripts" / "rules" / "extract"
    for py in sorted(ext_dir.glob("*.py")):
        if py.name == "__init__.py":
            continue
        text = py.read_text()
        check('sys.executable == "/usr/bin/python3"' in text,
              f"{py.name}: has interpreter guard")


def main():
    test_frozen_inputs_exist()
    test_dry_run_produces_expected_shape()
    test_validation_clean()
    test_determinism_byte_identical()
    test_ledger_roundtrip_and_provenance()
    test_non_factor_isolation_ast()
    test_interpreter_guard_present()
    print(f"\n{PASS} pass, {FAIL} fail")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
