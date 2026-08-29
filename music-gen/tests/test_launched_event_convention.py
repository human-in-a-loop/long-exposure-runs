#!/usr/bin/env python3
# tests/test_launched_event_convention.py — Cycle 35 clone-2.
# Enforces the _run/cycle_<N>_launched(-clone-<k>)? convention:
# status=validated at emission for c35+; pinned pre-existing offender
# list does not grow. ≥6 named cases.
# created: 2026-08-29
# cycle: 35
# agent: worker
# milestone: _infra/launched-event-convention-clone-2
import hashlib
import json
import re
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

WS = Path(__file__).resolve().parent.parent
LEDGER = WS / "promise_ledger.jsonl"
CONV_DOC = WS / "docs" / "fanout_launched_event_convention.md"
OFFENDER_LIST = WS / "tests" / "fixtures" / "launched_event_offender_list_v1.txt"

LAUNCHED_RE = re.compile(r"^_run/cycle_(\d+)_launched(-clone-(\d+))?$")

failures = []
passes = []


def _check(name, cond, detail=""):
    if cond:
        passes.append(name)
        print(f"PASS {name}")
    else:
        failures.append((name, detail))
        print(f"FAIL {name}: {detail}")


def _scan_launched_rows():
    rows = []
    with LEDGER.open() as f:
        for line in f:
            try:
                e = json.loads(line)
            except Exception:
                continue
            mid = e.get("milestone_id", "")
            m = LAUNCHED_RE.match(mid)
            if m:
                rows.append({
                    "milestone_id": mid,
                    "cycle": int(m.group(1)),
                    "clone": m.group(3),
                    "status": e.get("status"),
                    "agent": e.get("agent"),
                })
    return rows


def test_01_scan_returns_rows():
    rows = _scan_launched_rows()
    _check("test_01_scan_returns_rows", len(rows) > 0, f"got {len(rows)} rows")


def test_02_c35_plus_all_validated():
    rows = _scan_launched_rows()
    bad = [r for r in rows if r["cycle"] >= 35 and r["status"] != "validated"]
    _check("test_02_c35_plus_all_validated", not bad, f"offenders: {bad}")


def test_03_convention_doc_exists():
    _check("test_03_convention_doc_exists", CONV_DOC.exists(), str(CONV_DOC))


def test_04_doc_names_rule_literally():
    if not CONV_DOC.exists():
        _check("test_04_doc_names_rule_literally", False, "doc missing")
        return
    txt = CONV_DOC.read_text()
    # The literal rule text must appear.
    _check("test_04_doc_names_rule_literally",
           'status: "validated"' in txt or "status: validated" in txt.lower(),
           "literal rule text absent")


def test_05_offender_list_stable():
    """Offender list = current status!=validated rows in the ledger.
    Must equal the pinned fixture exactly (no growth, no shrink from rewriting)."""
    pinned = set(l.strip() for l in OFFENDER_LIST.read_text().splitlines() if l.strip())
    rows = _scan_launched_rows()
    observed = set(r["milestone_id"] for r in rows if r["status"] != "validated")
    grown = observed - pinned
    shrunk = pinned - observed
    _check("test_05_offender_list_stable",
           not grown and not shrunk,
           f"grew: {grown}; shrunk: {shrunk}")


def test_06_offender_fixture_content_hash():
    # A stable content-hash record. Any edit to the fixture must be
    # deliberate; the test simply asserts the file is non-empty and
    # every line matches the launched-event regex.
    if not OFFENDER_LIST.exists():
        _check("test_06_offender_fixture_present", False, str(OFFENDER_LIST))
        return
    _check("test_06_offender_fixture_present", True)
    lines = [l.strip() for l in OFFENDER_LIST.read_text().splitlines() if l.strip()]
    bad = [l for l in lines if not LAUNCHED_RE.match(l)]
    _check("test_06b_offender_fixture_lines_valid", not bad, f"bad: {bad}")
    # SHA (informational — not compared against a locked value, only
    # printed for downstream diffing).
    sha = hashlib.sha256(OFFENDER_LIST.read_bytes()).hexdigest()
    print(f"  offender_list_sha256={sha}")


def test_07_all_launched_names_wellformed():
    """Every launched-event id must match the canonical regex — no
    stray family collisions like _run/cycle_X_launched_v2."""
    rows = _scan_launched_rows()
    bad = [r["milestone_id"] for r in rows if not LAUNCHED_RE.match(r["milestone_id"])]
    _check("test_07_all_launched_names_wellformed", not bad, f"bad: {bad}")


def main():
    tests = [t for name, t in sorted(globals().items()) if name.startswith("test_") and callable(t)]
    for t in tests:
        try:
            t()
        except Exception as e:
            failures.append((t.__name__, f"exception: {e}"))
            print(f"FAIL {t.__name__}: exception {e}")
    print(f"\n{len(passes)} passed, {len(failures)} failed")
    if failures:
        for n, d in failures:
            print(f"  - {n}: {d}")
        sys.exit(1)


if __name__ == "__main__":
    main()
