#!/usr/bin/env python3
"""Ledger writer validation tests — cycle 10, _infra/ledger-schema-hardening.

Plain-assert style (no pytest), matching the M-RULES-1/schema convention.

Invocation:  PYTHONPATH=. /usr/bin/python3 tests/test_ledger_writer_validation.py

Contract:
    * append_ledger_event validates events against _ledger_schema.validate_event
      BEFORE opening the file (atomicity on validation failure).
    * event_id auto-generated as UUID5(namespace, canonical_json) when absent.
    * All 156 pre-existing events pass the validator (no retroactive invalidation).
    * The three documented drift patterns from cycles 7/8/9 are each rejected
      with a specific field-named error message.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path

assert sys.executable == '/usr/bin/python3', sys.executable

# Unset shadow-ledger routing so per-test tempdirs are the ledger destinations.
# In production, AGENT_FORK_ID sends writes to the clone shadow ledger; here we
# want each test's ledger isolated to its own tempdir.
os.environ.pop("AGENT_FORK_ID", None)
os.environ.pop("AGENT_INSTANCE_DIR", None)

# Bootstrap: the long_exposure package lives outside the workspace. When
# invoked as `PYTHONPATH=. /usr/bin/python3 tests/...` (the documented form),
# the caller-supplied PYTHONPATH override shadows the environment's default
# that puts long_exposure on sys.path, so we re-insert it here. Same guard
# the M-INGEST-1 §20 integration test uses.
_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"
if _LE_PARENT not in sys.path:
    sys.path.append(_LE_PARENT)

from long_exposure.tools._ledger_schema import (
    ASSESSORS,
    CONFIDENCE_LEVELS,
    REQUIRED_EVENT_FIELDS,
    STATUS_VALUES,
    _STATUS_ENUM,
    canonical_json,
    content_hash_event_id,
    validate_event,
)
from long_exposure.workspace_bootstrap import (
    LedgerAppendError,
    append_ledger_event,
    resolve_ledger_path,
)


# ------------------------------------------------------------------ scaffolding

def _tmpdir() -> Path:
    d = Path(tempfile.mkdtemp(prefix="lsh_"))
    return d


def _well_formed_event(**overrides) -> dict:
    ev = {
        "event_id": str(uuid.uuid4()),
        "ts": "2026-08-28T12:00:00Z",
        "run_id": "run-2026-08-28T040704Z",
        "cycle": 10,
        "agent": "worker",
        "milestone_id": "M-TEST-1/writer",
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": "well-formed test event",
            "assessor": "worker",
        },
        "narrative": "This event is fully well-formed.",
        "artifacts": [],
    }
    ev.update(overrides)
    return ev


PASS: list[str] = []
FAIL: list[tuple[str, str]] = []


def _run(name: str, fn) -> None:
    try:
        fn()
    except AssertionError as e:
        FAIL.append((name, str(e)))
        print(f"  FAIL: {name}: {e}")
    except Exception as e:  # unexpected error
        FAIL.append((name, f"{type(e).__name__}: {e}"))
        print(f"  ERROR: {name}: {type(e).__name__}: {e}")
    else:
        PASS.append(name)
        print(f"  PASS: {name}")


# ------------------------------------------------------------------ test cases

def test_01_well_formed_event_accepted():
    """Case 1: fully-specified event round-trips through append and is readable back."""
    ws = _tmpdir()
    try:
        ev = _well_formed_event()
        append_ledger_event(ws, ev)
        ledger = resolve_ledger_path(ws)
        assert ledger.exists(), "ledger file not created"
        lines = ledger.read_text().splitlines()
        assert len(lines) == 1, f"expected 1 line, got {len(lines)}"
        readback = json.loads(lines[0])
        assert readback["event_id"] == ev["event_id"]
        assert readback["milestone_id"] == ev["milestone_id"]
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def test_02_auto_event_id_generated():
    """Case 2: event without event_id succeeds; auto id is UUID; regeneration is stable."""
    ws = _tmpdir()
    try:
        ev = _well_formed_event()
        del ev["event_id"]
        append_ledger_event(ws, ev)
        ledger = resolve_ledger_path(ws)
        line = ledger.read_text().splitlines()[0]
        written = json.loads(line)
        # Must be a valid UUID.
        uuid.UUID(written["event_id"])
        # Must be deterministic: re-derive from ev sans event_id and ts.
        expected = content_hash_event_id(ev)
        assert written["event_id"] == expected, \
            f"auto event_id not stable: got {written['event_id']!r}, expected {expected!r}"
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def test_03_missing_run_id_rejected():
    """Case 3: missing run_id (cycle-9 drift pattern part A). Message names 'run_id'."""
    ws = _tmpdir()
    try:
        ev = _well_formed_event()
        del ev["run_id"]
        try:
            append_ledger_event(ws, ev)
        except LedgerAppendError as e:
            assert "run_id" in str(e), f"error message must name run_id, got: {e}"
        else:
            raise AssertionError("expected LedgerAppendError for missing run_id")
        # Ledger file must NOT exist — atomicity on validation failure.
        assert not resolve_ledger_path(ws).exists(), \
            "ledger file created despite validation failure"
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def test_04_missing_ts_rejected():
    """Case 4: missing ts. Message names 'ts'."""
    ws = _tmpdir()
    try:
        ev = _well_formed_event()
        del ev["ts"]
        try:
            append_ledger_event(ws, ev)
        except LedgerAppendError as e:
            assert "'ts'" in str(e) or "ts " in str(e), \
                f"error message must name ts, got: {e}"
        else:
            raise AssertionError("expected LedgerAppendError for missing ts")
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def test_05_flat_string_confidence_rejected():
    """Case 5: confidence='high' (cycle-8 drift pattern). Rejected with field-named msg."""
    ws = _tmpdir()
    try:
        ev = _well_formed_event(confidence="high")
        try:
            append_ledger_event(ws, ev)
        except LedgerAppendError as e:
            assert "confidence" in str(e), f"error must name confidence, got: {e}"
        else:
            raise AssertionError("expected LedgerAppendError for flat-string confidence")
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def test_06_confidence_missing_subfield_rejected():
    """Case 6: nested confidence lacking 'assessor'. Rejected with 'assessor' in message."""
    ws = _tmpdir()
    try:
        ev = _well_formed_event(
            confidence={"level": "high", "rationale": "no assessor here"}
        )
        try:
            append_ledger_event(ws, ev)
        except LedgerAppendError as e:
            assert "assessor" in str(e), f"error must name assessor, got: {e}"
        else:
            raise AssertionError("expected LedgerAppendError for missing subfield")
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def test_07_long_form_assessor_rejected():
    """Case 7: long-form assessor (cycle-9 drift). Canonical short-form still accepted.
    assessor_original extension field is tolerated for provenance."""
    ws = _tmpdir()
    try:
        # (a) long-form rejected
        bad = _well_formed_event(confidence={
            "level": "high",
            "rationale": "long-form assessor",
            "assessor": "cyd7bevdr@mozmail.com (worker, cycle 9, fork abc, clone 2)",
        })
        try:
            append_ledger_event(ws, bad)
        except LedgerAppendError as e:
            assert "assessor" in str(e), f"error must name assessor, got: {e}"
        else:
            raise AssertionError("expected LedgerAppendError for long-form assessor")

        # (b) short-form + assessor_original accepted
        good = _well_formed_event(confidence={
            "level": "high",
            "rationale": "canonical assessor + extension provenance",
            "assessor": "worker",
            "assessor_original": "cyd7bevdr@mozmail.com (worker, cycle 9, fork abc, clone 2)",
        })
        append_ledger_event(ws, good)  # must not raise
        lines = resolve_ledger_path(ws).read_text().splitlines()
        assert len(lines) == 1
        readback = json.loads(lines[0])
        assert readback["confidence"]["assessor_original"].startswith("cyd7bevdr@")
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def test_08_unknown_extension_field_tolerated():
    """Case 8: unknown extension fields (reporter_mode, supersedes_path) don't break validation."""
    ws = _tmpdir()
    try:
        ev = _well_formed_event(
            reporter_mode="cycles_1-3",
            supersedes_path="tools/stale/foo.py",
        )
        # Must not raise.
        append_ledger_event(ws, ev)
        readback = json.loads(resolve_ledger_path(ws).read_text().splitlines()[0])
        assert readback["reporter_mode"] == "cycles_1-3"
        assert readback["supersedes_path"] == "tools/stale/foo.py"
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def test_09_all_existing_ledger_events_pass():
    """Case 9: regression harness — every current promise_ledger.jsonl row validates.
    Catches any future change that would retroactively invalidate history."""
    ledger = Path("promise_ledger.jsonl")
    if not ledger.exists():
        # Fall back: not running from workspace root; skip with informative pass.
        print("    (no promise_ledger.jsonl in cwd; skipping)")
        return
    fails = []
    for i, raw in enumerate(ledger.read_text().splitlines(), 1):
        ev = json.loads(raw)
        errs = validate_event(ev)
        if errs:
            fails.append((i, ev.get("milestone_id"), errs))
    assert not fails, \
        f"{len(fails)} existing events fail new validator; e.g. line {fails[0][0]}: {fails[0][2]}"


def test_10_duplicate_event_id_rejected_at_writer():
    """Bonus case 10: appending an event whose event_id already exists in the file
    is rejected at the writer, not left to promise_check."""
    ws = _tmpdir()
    try:
        ev = _well_formed_event()
        append_ledger_event(ws, ev)
        # Second append with same event_id should raise.
        try:
            append_ledger_event(ws, ev)
        except LedgerAppendError as e:
            assert "duplicate" in str(e).lower() or "event_id" in str(e), \
                f"error must name event_id/duplicate, got: {e}"
        else:
            raise AssertionError("expected LedgerAppendError for duplicate event_id")
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def test_11_write_atomicity_on_validation_failure():
    """Bonus case 11: a failed append leaves the ledger byte-identical to before."""
    ws = _tmpdir()
    try:
        # Prime the ledger with one valid event.
        good = _well_formed_event()
        append_ledger_event(ws, good)
        ledger = resolve_ledger_path(ws)
        before = ledger.read_bytes()
        # Now attempt a bad append.
        bad = _well_formed_event()
        del bad["confidence"]  # missing required field
        try:
            append_ledger_event(ws, bad)
        except LedgerAppendError:
            pass
        after = ledger.read_bytes()
        assert before == after, "ledger file was modified by a failed append"
    finally:
        shutil.rmtree(ws, ignore_errors=True)


# Additional sanity tests

def test_12_ssot_constants_are_shared_object():
    """SSoT check: promise_check and ledger_append import from _ledger_schema."""
    import long_exposure.tools._ledger_schema as ls
    import long_exposure.tools.promise_check as pc
    import long_exposure.tools.ledger_append as la
    assert pc.REQUIRED_EVENT_FIELDS is ls.REQUIRED_EVENT_FIELDS
    assert la.REQUIRED_EVENT_FIELDS is ls.REQUIRED_EVENT_FIELDS
    assert pc.CONFIDENCE_LEVELS is ls.CONFIDENCE_LEVELS
    assert pc.STATUS_VALUES is ls.STATUS_VALUES
    assert pc.ASSESSORS is ls.ASSESSORS


def test_13_no_import_cycles():
    """_ledger_schema.py must not import promise_check / ledger_append / workspace_bootstrap."""
    import ast
    import long_exposure.tools._ledger_schema as ls
    with open(ls.__file__) as f:
        tree = ast.parse(f.read())
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)
    forbidden = {
        "long_exposure.tools.promise_check",
        "long_exposure.tools.ledger_append",
        "long_exposure.workspace_bootstrap",
    }
    cycles = imported & forbidden
    assert not cycles, f"_ledger_schema imports forbidden modules: {cycles}"


# ------------------------------------------------------------------ cycle-14 hardening cases


def test_14_status_in_progress_accepted():
    """Case 14 (cycle-14): status='in-progress' accepted at the writer.

    'in-progress' is a canonical status — the cycle-13 drift on line 250 was
    a state-transition mistake (validated→in-progress without an intervening
    reopened event), not an enum violation. The enum accepts it; the
    state-transition check (out of scope here) is what should have caught it.
    """
    ws = _tmpdir()
    try:
        ev = _well_formed_event(status="in-progress")
        append_ledger_event(ws, ev)  # must not raise
        line = resolve_ledger_path(ws).read_text().splitlines()[0]
        assert json.loads(line)["status"] == "in-progress"
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def test_15_status_wobble_rejected():
    """Case 15 (cycle-14): unknown status 'wobble' rejected with message
    citing 'status' and the enum vocabulary."""
    ws = _tmpdir()
    try:
        ev = _well_formed_event(status="wobble")
        try:
            append_ledger_event(ws, ev)
        except LedgerAppendError as e:
            msg = str(e)
            assert "status" in msg, f"error must name status, got: {e}"
            assert "wobble" in msg, f"error must show offending value, got: {e}"
        else:
            raise AssertionError("expected LedgerAppendError for status='wobble'")
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def test_16_supersedes_path_string_accepted():
    """Case 16 (cycle-14): supersedes_path='tools/foo.py' accepted."""
    ws = _tmpdir()
    try:
        ev = _well_formed_event(supersedes_path="tools/foo.py")
        append_ledger_event(ws, ev)  # must not raise
        line = resolve_ledger_path(ws).read_text().splitlines()[0]
        assert json.loads(line)["supersedes_path"] == "tools/foo.py"
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def test_17_supersedes_path_list_rejected():
    """Case 17 (cycle-14): list-form supersedes_path rejected with message
    citing 'supersedes_path' AND 'must be' (the field-named contract)."""
    ws = _tmpdir()
    try:
        ev = _well_formed_event(
            supersedes_path=["tools/foo.py", "tools/bar.py"]
        )
        try:
            append_ledger_event(ws, ev)
        except LedgerAppendError as e:
            msg = str(e)
            assert "supersedes_path" in msg, \
                f"error must name supersedes_path, got: {e}"
            assert "must be" in msg or "str" in msg, \
                f"error must state expected type, got: {e}"
        else:
            raise AssertionError(
                "expected LedgerAppendError for list-form supersedes_path"
            )
        # Atomicity: no file written.
        assert not resolve_ledger_path(ws).exists()
    finally:
        shutil.rmtree(ws, ignore_errors=True)


def test_18_supersedes_path_absent_accepted():
    """Case 18 (cycle-14): well-formed event without supersedes_path accepted
    (field is optional). Also asserts the enum alias is the frozen constant."""
    ws = _tmpdir()
    try:
        ev = _well_formed_event()
        assert "supersedes_path" not in ev
        append_ledger_event(ws, ev)  # must not raise
        # Alias sanity: _STATUS_ENUM is STATUS_VALUES is the same frozen set.
        assert _STATUS_ENUM is STATUS_VALUES, \
            "_STATUS_ENUM must alias STATUS_VALUES (is-identity)"
        assert isinstance(_STATUS_ENUM, frozenset), \
            "_STATUS_ENUM must be frozenset"
        # The brief's proposed enum is a subset of the module's canonical enum.
        brief_enum = {"in-progress", "validated", "invalidated",
                      "reopened", "superseded"}
        assert brief_enum.issubset(_STATUS_ENUM), \
            f"brief enum not subset of _STATUS_ENUM: {_STATUS_ENUM}"
    finally:
        shutil.rmtree(ws, ignore_errors=True)


# ------------------------------------------------------------------ runner

TESTS = [
    ("test_01_well_formed_event_accepted", test_01_well_formed_event_accepted),
    ("test_02_auto_event_id_generated", test_02_auto_event_id_generated),
    ("test_03_missing_run_id_rejected", test_03_missing_run_id_rejected),
    ("test_04_missing_ts_rejected", test_04_missing_ts_rejected),
    ("test_05_flat_string_confidence_rejected", test_05_flat_string_confidence_rejected),
    ("test_06_confidence_missing_subfield_rejected", test_06_confidence_missing_subfield_rejected),
    ("test_07_long_form_assessor_rejected", test_07_long_form_assessor_rejected),
    ("test_08_unknown_extension_field_tolerated", test_08_unknown_extension_field_tolerated),
    ("test_09_all_existing_ledger_events_pass", test_09_all_existing_ledger_events_pass),
    ("test_10_duplicate_event_id_rejected_at_writer", test_10_duplicate_event_id_rejected_at_writer),
    ("test_11_write_atomicity_on_validation_failure", test_11_write_atomicity_on_validation_failure),
    ("test_12_ssot_constants_are_shared_object", test_12_ssot_constants_are_shared_object),
    ("test_13_no_import_cycles", test_13_no_import_cycles),
    ("test_14_status_in_progress_accepted", test_14_status_in_progress_accepted),
    ("test_15_status_wobble_rejected", test_15_status_wobble_rejected),
    ("test_16_supersedes_path_string_accepted", test_16_supersedes_path_string_accepted),
    ("test_17_supersedes_path_list_rejected", test_17_supersedes_path_list_rejected),
    ("test_18_supersedes_path_absent_accepted", test_18_supersedes_path_absent_accepted),
]


if __name__ == "__main__":
    print(f"Running {len(TESTS)} tests for _infra/ledger-schema-hardening...")
    for name, fn in TESTS:
        _run(name, fn)
    print()
    print(f"RESULT: {len(PASS)} pass / {len(FAIL)} fail")
    if FAIL:
        print()
        for n, msg in FAIL:
            print(f"  {n}: {msg}")
        sys.exit(1)
    sys.exit(0)
