"""Tests for M-INGEST-1/egress-ready-automation.

Run: PYTHONPATH=. /usr/bin/python3 tests/test_egress_ready_state.py

Six named scenarios drive both the detector (rung 1) and the full state
machine with monkey-patched hooks (rung 2). Persistence, byte-determinism,
crash-resumption, and human-override are covered as separate blocks.

NO REAL SUBPROCESS.RUN: the module patches subprocess.run at import time
with a guard that raises if any test unintentionally invokes it.

created: 2026-08-28
cycle: 8
milestone: M-INGEST-1/egress-ready-automation
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WS))

# --- Guard: no real subprocess.run in this test module -----------------------
_ORIGINAL_SUBPROCESS_RUN = subprocess.run

class _SubprocessRunForbidden(RuntimeError):
    pass

def _guard(*a, **kw):
    raise _SubprocessRunForbidden(
        f"real subprocess.run was called with args={a[0] if a else kw.get('args')!r}; "
        "tests must monkey-patch every hook"
    )

subprocess.run = _guard  # type: ignore[assignment]

# Now import the module under test. Its default SubprocessHooks would try
# to subprocess.run in production; we always inject a mock subclass below.
from scripts.egress_ready.state import (  # noqa: E402
    Clock,
    EgressReadyMachine,
    InvalidTransition,
    Persisted,
    State,
    TRANSITIONS,
    force_idle,
    force_trigger,
    reset_failure,
    resume,
)
from scripts.egress_ready.subprocess_hooks import HookResult, SubprocessHooks  # noqa: E402
from scripts.egress_ready.trigger import (  # noqa: E402
    TriggerDecision,
    TriggerKind,
    detect_trigger,
    load_jsonl,
)

# --- Test infrastructure -----------------------------------------------------
FIXTURE_DIR = WS / "tests" / "fixtures" / "egress_status"
# "now" reference for the fixtures. Choose 2026-08-28T10:00:00Z so:
#   - fixtures dated 09:00 through 09:04 are all fresh (~1h old)
#   - a fixture dated 2026-08-27T09:00:00Z is exactly 25h old -> stale.
NOW_UTC = datetime(2026, 8, 28, 10, 0, 0, tzinfo=timezone.utc)
FROZEN_CLOCK = Clock(now=lambda: NOW_UTC)

_fail = 0
def check(cond, msg):
    global _fail
    if cond:
        print("PASS", msg)
    else:
        print("FAIL", msg)
        _fail += 1


class OkHooks(SubprocessHooks):
    def __init__(self):
        super().__init__()
        self.calls = []
    def run_harvest(self):
        self.calls.append("run_harvest")
        return HookResult(True, "", 0.0, 0)
    def run_chunker(self):
        self.calls.append("run_chunker")
        return HookResult(True, "", 0.0, 0)
    def run_classifier(self):
        self.calls.append("run_classifier")
        return HookResult(True, "", 0.0, 0)
    def write_ready_flag(self):
        self.calls.append("write_ready_flag")
        return HookResult(True, "", 0.0, 0)


class FailAtHooks(OkHooks):
    """Fail at the named hook (harvest/chunker/classifier); ok otherwise."""
    def __init__(self, failing: str):
        super().__init__()
        self.failing = failing
    def _maybe_fail(self, name):
        if name == self.failing:
            return HookResult(False, "boom\ntraceback tail here", 0.01, 1)
        return HookResult(True, "", 0.0, 0)
    def run_harvest(self):
        self.calls.append("run_harvest")
        return self._maybe_fail("run_harvest")
    def run_chunker(self):
        self.calls.append("run_chunker")
        return self._maybe_fail("run_chunker")
    def run_classifier(self):
        self.calls.append("run_classifier")
        return self._maybe_fail("run_classifier")


def _tempdir():
    return Path(tempfile.mkdtemp(prefix="egress_ready_test_"))


def _new_machine(tmp: Path, fixture: Path, hooks: SubprocessHooks) -> EgressReadyMachine:
    return EgressReadyMachine(
        state_path=tmp / "state.json",
        transitions_path=tmp / "transitions.jsonl",
        egress_status_path=fixture,
        hooks=hooks,
        clock=FROZEN_CLOCK,
        diagnostic_dir=tmp,
    )


# --- 0. TRANSITIONS map sanity ----------------------------------------------
check(TRANSITIONS[State.IDLE] == {State.ARMED, State.TRIGGERED},
      "TRANSITIONS: IDLE -> {ARMED, TRIGGERED}")
check(State.HARVESTING in TRANSITIONS[State.TRIGGERED],
      "TRANSITIONS: TRIGGERED -> HARVESTING legal")
check(State.CHUNKING in TRANSITIONS[State.HARVESTING],
      "TRANSITIONS: HARVESTING -> CHUNKING legal")
check(State.CLASSIFYING in TRANSITIONS[State.CHUNKING],
      "TRANSITIONS: CHUNKING -> CLASSIFYING legal")
check(State.READY in TRANSITIONS[State.CLASSIFYING],
      "TRANSITIONS: CLASSIFYING -> READY legal")
check(State.FAILED in TRANSITIONS[State.HARVESTING],
      "TRANSITIONS: HARVESTING -> FAILED legal")


# --- Named scenarios (rung 1 = detector; rung 2 = full drive) ---------------
SCENARIOS = [
    ("all-false",                  "all_false.jsonl",                 TriggerKind.NONE,      State.IDLE),
    ("single-true-then-back",      "single_true_then_back.jsonl",     TriggerKind.NONE,      State.IDLE),
    ("two-consecutive-triggers",   "two_consecutive_triggers.jsonl",  TriggerKind.TRIGGERED, State.READY),
    # scenario 4 is exercised as two calls (drive first, then re-scan with an appended F)
    # via a special block below.
    ("interleaved-then-true-true", "interleaved_then_true_true.jsonl", TriggerKind.TRIGGERED, State.READY),
    ("stale-row-does-not-count",   "stale_row_does_not_count.jsonl",  TriggerKind.NONE,      State.IDLE),  # note: fresh row alone is ARMED, but sole-fresh -> ARMED not NONE; see refined check below
]

# Rung 1: detector only.
for name, fname, expected_kind, _ in SCENARIOS:
    rows = load_jsonl(FIXTURE_DIR / fname)
    dec = detect_trigger(rows, NOW_UTC)
    # Special: stale_row_does_not_count actually has one fresh true -> ARMED, not NONE.
    if name == "stale-row-does-not-count":
        check(dec.kind == TriggerKind.ARMED,
              f"scenario {name}: detector -> ARMED (stale row invisible, sole fresh true)")
    else:
        check(dec.kind == expected_kind,
              f"scenario {name}: detector -> {expected_kind.value} (got {dec.kind.value})")

# Extra explicit detector checks against the falsification criteria.
check(detect_trigger([], NOW_UTC).kind == TriggerKind.NONE,
      "detector: empty rows -> NONE")
check(detect_trigger([{"ts": "2026-08-28T09:59:00Z", "media_ok": True}], NOW_UTC).kind
      == TriggerKind.ARMED,
      "detector: single fresh true -> ARMED (not TRIGGERED)")
check(detect_trigger(
      [{"ts": "2026-08-28T09:00:00Z", "media_ok": True},
       {"ts": "2026-08-28T09:01:00Z", "media_ok": False},
       {"ts": "2026-08-28T09:02:00Z", "media_ok": True}], NOW_UTC).kind
      == TriggerKind.ARMED,
      "detector: [T, F, T] -> ARMED (not TRIGGERED; not consecutive)")
check(detect_trigger(
      [{"ts": "2026-08-28T09:00:00Z", "media_ok": True},
       {"ts": "2026-08-28T09:01:00Z", "media_ok": True},
       {"ts": "2026-08-28T09:02:00Z", "media_ok": False}], NOW_UTC).kind
      == TriggerKind.NONE,
      "detector: [T, T, F] -> NONE (trailing false breaks the streak)")

# Rung 2: full end-to-end drive for each scenario.
for name, fname, _expected_kind, expected_terminal in SCENARIOS:
    tmp = _tempdir()
    try:
        hooks = OkHooks()
        m = _new_machine(tmp, FIXTURE_DIR / fname, hooks)
        result = m.scan_and_advance()
        expected = State.ARMED if name == "stale-row-does-not-count" else expected_terminal
        check(result == expected,
              f"drive {name}: terminal state {expected.value} (got {result.value})")
        # state.json is written on every transition. When we started IDLE and
        # remained IDLE (no transition), state.json is legitimately absent.
        state_json_should_exist = (expected != State.IDLE)
        if state_json_should_exist:
            s = json.loads((tmp / "state.json").read_text())
            check(s["state"] == expected.value,
                  f"drive {name}: state.json state={expected.value}")
            check((tmp / "transitions.jsonl").is_file(),
                  f"drive {name}: transitions.jsonl written")
        else:
            check(not (tmp / "state.json").exists(),
                  f"drive {name}: no transition -> no state.json (in-memory IDLE)")
        # Second construction from same disk state -> idempotent.
        hooks2 = OkHooks()
        m2 = _new_machine(tmp, FIXTURE_DIR / fname, hooks2)
        result2 = m2.scan_and_advance()
        check(result2 == expected,
              f"drive {name}: idempotent second construction returns {expected.value}")
        check(hooks2.calls == [] or expected == State.READY and hooks2.calls == [],
              f"drive {name}: second construction does not re-fire any hook (calls={hooks2.calls})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- Scenario 4: already-triggered-then-false -------------------------------
# Drive to TRIGGERED->READY via the two-consecutive fixture, then re-scan against
# a variant that has an appended trailing F: the machine must remain in READY
# and MUST NOT retract state.
tmp = _tempdir()
try:
    fx = tmp / "egress_status.jsonl"
    shutil.copy(FIXTURE_DIR / "two_consecutive_triggers.jsonl", fx)
    hooks = OkHooks()
    m = _new_machine(tmp, fx, hooks)
    r = m.scan_and_advance()
    check(r == State.READY, "scenario already-triggered-then-false: initial drive -> READY")
    # Append a trailing false row.
    with open(fx, "a") as fh:
        fh.write(json.dumps({"ts": "2026-08-28T09:03:00Z", "media_ok": False, "http_code": 403}) + "\n")
    hooks2 = OkHooks()
    m2 = _new_machine(tmp, fx, hooks2)
    r2 = m2.scan_and_advance()
    check(r2 == State.READY,
          "scenario already-triggered-then-false: re-scan with trailing F stays READY (idempotent)")
    check(hooks2.calls == [],
          f"scenario already-triggered-then-false: no hook re-fired on re-scan (calls={hooks2.calls})")
finally:
    shutil.rmtree(tmp, ignore_errors=True)


# --- Byte-determinism: two --watch invocations produce identical transitions -
tmp = _tempdir()
try:
    hooks = OkHooks()
    m = _new_machine(tmp, FIXTURE_DIR / "two_consecutive_triggers.jsonl", hooks)
    m.scan_and_advance()
    first_bytes = (tmp / "transitions.jsonl").read_bytes()
    first_hash = hashlib.sha256(first_bytes).hexdigest()
finally:
    tmp1 = tmp
tmp = _tempdir()
try:
    hooks = OkHooks()
    m = _new_machine(tmp, FIXTURE_DIR / "two_consecutive_triggers.jsonl", hooks)
    m.scan_and_advance()
    second_bytes = (tmp / "transitions.jsonl").read_bytes()
    second_hash = hashlib.sha256(second_bytes).hexdigest()
    check(first_hash == second_hash,
          f"byte-determinism: transitions.jsonl SHA-256 equal across independent runs "
          f"({first_hash[:12]}=={second_hash[:12]})")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.rmtree(tmp1, ignore_errors=True)


# --- Atomic write of state.json: monkey-patched os.replace raises mid-write --
import scripts.egress_ready.state as state_mod
tmp = _tempdir()
try:
    hooks = OkHooks()
    m = _new_machine(tmp, FIXTURE_DIR / "all_false.jsonl", hooks)
    # First scan lands in IDLE without writing state.json (was already IDLE), so
    # to get a baseline state.json we force ARMED via a manual transition first.
    # But ARMED requires a real ARMED signal; easier: bootstrap a baseline
    # state.json by dropping IDLE.  scan_and_advance stays IDLE (no persist).
    # Instead, drive to ARMED using single-true fixture.
    m2 = _new_machine(tmp, FIXTURE_DIR / "single_true_then_back.jsonl", hooks)
    # single_true_then_back trailing is False -> NONE. Use stale_row_does_not_count
    # whose sole fresh row is True -> ARMED.
    m3 = _new_machine(tmp, FIXTURE_DIR / "stale_row_does_not_count.jsonl", hooks)
    r = m3.scan_and_advance()
    check(r == State.ARMED, "atomic-write baseline: reached ARMED")
    check((tmp / "state.json").is_file(), "atomic-write baseline: state.json written")
    baseline_bytes = (tmp / "state.json").read_bytes()

    # Now monkey-patch os.replace to raise, then attempt another transition.
    orig_replace = os.replace
    def _boom(*a, **kw):
        raise OSError("simulated mid-write crash")
    os.replace = _boom  # type: ignore[assignment]
    try:
        # Force a transition (ARMED -> IDLE via force_idle should attempt to
        # atomically write and fail).
        raised = False
        try:
            force_idle(m3)
        except OSError:
            raised = True
        check(raised, "atomic-write: os.replace failure surfaces as OSError")
        # Baseline state.json is intact.
        check((tmp / "state.json").read_bytes() == baseline_bytes,
              "atomic-write: previous state.json intact after simulated crash")
    finally:
        os.replace = orig_replace  # type: ignore[assignment]
finally:
    shutil.rmtree(tmp, ignore_errors=True)


# --- Human-override API ------------------------------------------------------
# force_idle from ARMED
tmp = _tempdir()
try:
    hooks = OkHooks()
    m = _new_machine(tmp, FIXTURE_DIR / "stale_row_does_not_count.jsonl", hooks)
    m.scan_and_advance()
    check(m.persisted.state == State.ARMED, "override baseline: ARMED reached")
    force_idle(m)
    check(m.persisted.state == State.IDLE, "override: force_idle from ARMED -> IDLE")
    # Audit log records the reason field 'human_override'.
    lines = (tmp / "transitions.jsonl").read_text().splitlines()
    last = json.loads(lines[-1])
    check("human_override" in last["reason"],
          f"override: transitions.jsonl records human_override reason (got {last['reason']!r})")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# force_trigger from IDLE bypasses two-consecutive-true.
tmp = _tempdir()
try:
    hooks = OkHooks()
    m = _new_machine(tmp, FIXTURE_DIR / "all_false.jsonl", hooks)
    check(m.persisted.state == State.IDLE, "override baseline: IDLE")
    force_trigger(m)
    check(m.persisted.state == State.READY,
          f"override: force_trigger from IDLE drives to READY (got {m.persisted.state.value})")
    check(hooks.calls == ["run_harvest", "run_chunker", "run_classifier", "write_ready_flag"],
          f"override: force_trigger chain ran in order (calls={hooks.calls})")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# reset_failure without --force-idle refuses.
tmp = _tempdir()
try:
    hooks = FailAtHooks("run_chunker")
    m = _new_machine(tmp, FIXTURE_DIR / "two_consecutive_triggers.jsonl", hooks)
    m.scan_and_advance()
    check(m.persisted.state == State.FAILED, "reset-failure baseline: FAILED reached")
    check(m.persisted.failed_stage == State.CHUNKING.value,
          f"reset-failure baseline: failed_stage=CHUNKING (got {m.persisted.failed_stage})")
    refused = False
    try:
        reset_failure(m, force_idle_ack=False)
    except InvalidTransition:
        refused = True
    check(refused, "override: reset_failure without --force-idle raises InvalidTransition")
    # With ack it succeeds.
    reset_failure(m, force_idle_ack=True)
    check(m.persisted.state == State.IDLE,
          "override: reset_failure with --force-idle -> IDLE")
finally:
    shutil.rmtree(tmp, ignore_errors=True)


# --- Failure recovery via --resume: FAILED restarts exact failing stage -----
tmp = _tempdir()
try:
    # First run: fail at chunker.
    hooks = FailAtHooks("run_chunker")
    m = _new_machine(tmp, FIXTURE_DIR / "two_consecutive_triggers.jsonl", hooks)
    m.scan_and_advance()
    check(m.persisted.state == State.FAILED, "resume: FAILED after chunker error")
    check(m.persisted.failed_stage == State.CHUNKING.value,
          f"resume: failed_stage=CHUNKING (got {m.persisted.failed_stage})")
    diag = m.persisted.diagnostic_path
    check(diag and Path(diag).is_file(),
          f"resume: diagnostic file persisted at {diag!r}")
    diag_j = json.loads(Path(diag).read_text())
    check(diag_j["failed_at_stage"] == "CHUNKING",
          f"resume: diagnostic records failed_at_stage=CHUNKING (got {diag_j['failed_at_stage']!r})")
    check("boom" in diag_j["stderr_tail"],
          "resume: diagnostic captures stderr tail")

    # Now replace hooks with an OK version and --resume: only chunker onwards.
    ok = OkHooks()
    m2 = _new_machine(tmp, FIXTURE_DIR / "two_consecutive_triggers.jsonl", ok)
    check(m2.persisted.state == State.FAILED, "resume: fresh instance loads FAILED from disk")
    resume(m2)
    check(m2.persisted.state == State.READY,
          f"resume: after resume -> READY (got {m2.persisted.state.value})")
    # Should NOT have re-run harvest.
    check(ok.calls == ["run_chunker", "run_classifier", "write_ready_flag"],
          f"resume: only failing stage + downstream ran (calls={ok.calls})")
finally:
    shutil.rmtree(tmp, ignore_errors=True)


# --- Ensure NO real subprocess.run was called during any test ---------------
# (The module-level guard would have raised _SubprocessRunForbidden if any test
# had unintentionally invoked it. Reaching this line without exception is the
# positive assertion.)
check(subprocess.run is _guard,
      "isolation: subprocess.run remains guarded throughout test module")


# --- AST scan: scripts/egress_ready/*.py has zero sidecar_nonfactor refs ----
import ast, re
_egress_dir = WS / "scripts" / "egress_ready"
_bad = 0
for _p in sorted(_egress_dir.glob("*.py")):
    _src = _p.read_text(encoding="utf-8")
    for line in _src.splitlines():
        if re.match(r"^\s*(?:from\s+\S*\bsidecar_nonfactor\b|import\s+\S*\bsidecar_nonfactor\b)", line):
            _bad += 1
            print(f"  BAD import in {_p}: {line.strip()}")
check(_bad == 0, "isolation: scripts/egress_ready/*.py has zero sidecar_nonfactor imports")


print()
print(f"result: {'PASS' if _fail == 0 else 'FAIL'} ({_fail} failures)")
sys.exit(1 if _fail else 0)
