#!/usr/bin/env python3
"""Splice validate_history into promise_check._check_lifecycle."""
import sys
assert sys.executable == '/usr/bin/python3', sys.executable
sys.path.insert(0, "/home/user/human-in-a-loop/long-exposure")

import long_exposure.tools.promise_check as m
import inspect

src = inspect.getsource(m)

# 1. Extend the SSoT import to bring in validate_history.
old_imp = '''from long_exposure.tools._ledger_schema import (  # noqa: E402
    ASSESSORS,
    CONFIDENCE_LEVELS,
    REQUIRED_EVENT_FIELDS,
    STATUS_VALUES,
)'''
new_imp = '''from long_exposure.tools._ledger_schema import (  # noqa: E402
    ASSESSORS,
    CONFIDENCE_LEVELS,
    REQUIRED_EVENT_FIELDS,
    STATUS_VALUES,
    validate_history,
)'''
assert old_imp in src, "import block anchor missing — schema module drift?"
src = src.replace(old_imp, new_imp)

# 2. In _check_lifecycle, append validate_history call after the hand-coded loop.
old_tail = '''            prev_status = status


# ---------------------------------------------------------------------------
# Plan / mtime integrity — silent-edit detection
# ---------------------------------------------------------------------------'''
new_tail = '''            prev_status = status

    # Cycle-15 (_infra/ledger-schema-hardening-v3): defer to the SSoT
    # per-milestone transition graph (validate_history / _STATE_TRANSITIONS).
    # Catches every illegal consecutive transition, not just the flagship
    # validated -> in-progress pattern the hand-coded rule above targets.
    # On a clean ledger this returns [] and adds nothing. Duplicate coverage
    # for the flagship pattern is intentional — validate_history's message
    # names the (prev, next) pair and both event_ids, so it is strictly more
    # informative than the hand-coded rule and helps the auditor triage.
    for err in validate_history(events):
        findings.err(f"ledger:transition: {err}")


# ---------------------------------------------------------------------------
# Plan / mtime integrity — silent-edit detection
# ---------------------------------------------------------------------------'''
assert old_tail in src, "lifecycle-tail anchor missing"
src = src.replace(old_tail, new_tail)

target = "/home/user/human-in-a-loop/long-exposure/long_exposure/tools/promise_check.py"
with open(target, "w") as f:
    f.write(src)
print(f"wrote {len(src)} bytes to {target}")
