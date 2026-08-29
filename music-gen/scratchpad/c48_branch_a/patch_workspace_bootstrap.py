#!/usr/bin/env python3
"""Apply c48 _infra/harness-and-writer-hardening-v3 sub-fixes 1 & 2 edits
to long_exposure/workspace_bootstrap.py.

Sub-fix 1: gate the c33 auto-suffix on ^M- ids behind
    MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION={1,true}. Default OFF preserves
    the c47 behavior of auto-suffixing every _FANOUT_INFRA_PREFIXES id
    inside a clone context.
Sub-fix 2: thread MUSICGEN_LEDGER_SUPERSEDES_IN_HASH={1,true} through the
    UUID5 event_id auto-derivation path via content_hash_event_id_v2.

Idempotent — re-running on an already-patched file is a no-op.
Public API of append_ledger_event(workspace, event) unchanged.
LedgerNamespaceViolation MRO unchanged.
"""
import pathlib

TARGET = pathlib.Path('/home/user/human-in-a-loop/long-exposure/long_exposure/workspace_bootstrap.py')

MARKER = "# --- Cycle-48 _infra/harness-and-writer-hardening-v3"

HELPERS_BLOCK = '''

# --- Cycle-48 _infra/harness-and-writer-hardening-v3 --------------------------
#
# Two env-var-gated writer switches added for c47 audit issues #2 and #3.
# Both default OFF for c48 to preserve the 793-row baseline replay contract;
# c49+ default flips to ON via a subsequent one-line change (not this cycle).
# Full semantics in docs/harness_and_writer_hardening_v3_rubric.md.


def _env_flag_truthy(value: str | None) -> bool:
    """Return True iff the env-var value is one of the canonical truthy
    tokens ("1", "true" case-insensitive). Every other value — including
    "0", empty, unset, and unrelated strings — is False.
    """
    if not value:
        return False
    return value.strip().lower() in ("1", "true")


def _substantive_exemption_active() -> bool:
    """c48 sub-fix 1: True iff the c33 auto-suffix should SKIP substantive
    ``^M-`` milestone ids inside a clone context. Read from the env-var
    ``MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION`` at every call so tests can
    round-trip the flag via ``os.environ`` mutation.
    """
    return _env_flag_truthy(os.environ.get("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION"))


def _supersedes_in_hash_active() -> bool:
    """c48 sub-fix 2: True iff the writer's UUID5 event_id derivation
    should INCLUDE the ``supersedes`` field in its canonical-JSON payload.
    Read from ``MUSICGEN_LEDGER_SUPERSEDES_IN_HASH`` at every call for the
    same round-trip reason.
    """
    return _env_flag_truthy(os.environ.get("MUSICGEN_LEDGER_SUPERSEDES_IN_HASH"))


def _should_suffix(milestone_id: str) -> bool:
    """c48 sub-fix 1: return True iff the c33 auto-suffix should fire for
    this ``milestone_id`` given the current substantive-exemption env var.

    Semantics:
        * ``^M-`` (substantive milestones): auto-suffix UNLESS the
          substantive-exemption env var is active.
        * ``^(_infra|_run|_plan|_archive|_manager)/`` (infra families):
          always auto-suffix — the exemption does not apply.
        * any other id: c33 already never suffixes; caller handles that
          via ``_FANOUT_INFRA_PREFIXES`` membership check.

    Called by ``_guard_clone_namespace`` after the prefix + idempotence +
    clone-context checks have already fired.
    """
    if milestone_id.startswith("M-"):
        return not _substantive_exemption_active()
    # All other prefixes (_infra/, _run/, _plan/, _archive/, _manager/):
    # c33 behavior verbatim, exemption does not apply.
    return True
'''

GUARD_OLD = '''    # Detect clone context.
    is_clone, k = _is_clone_context(workspace)
    if not is_clone:
        return event
    # In-context violation.
    if os.environ.get("MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE", "0") == "1":
        _canonical = f"{mid}-clone-{k}"
        raise LedgerNamespaceViolation(
            f"milestone_id={mid!r} emitted from clone context (clone_k={k}) "
            f"is missing the required -clone-<k> suffix per the c32 fanout "
            f"namespace convention (see docs/fanout_namespace_convention_v3.md); "
            f"canonical identifier would be {_canonical!r}",
            event,
        )
    # Default (proactive) mode: silently auto-suffix.
    event["milestone_id"] = f"{mid}-clone-{k}"
    return event'''

GUARD_NEW = '''    # Detect clone context.
    is_clone, k = _is_clone_context(workspace)
    if not is_clone:
        return event
    # c48 sub-fix 1: substantive-milestone exemption gate. When
    # MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION={1,true}, ids matching ``^M-``
    # skip both the strict-mode raise AND the default auto-suffix — they
    # pass through untouched. Infra-family ids (`_infra/`, `_run/`,
    # `_plan/`, `_archive/`, `_manager/`) continue to auto-suffix as before.
    if not _should_suffix(mid):
        return event
    # In-context violation.
    if os.environ.get("MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE", "0") == "1":
        _canonical = f"{mid}-clone-{k}"
        raise LedgerNamespaceViolation(
            f"milestone_id={mid!r} emitted from clone context (clone_k={k}) "
            f"is missing the required -clone-<k> suffix per the c32 fanout "
            f"namespace convention (see docs/fanout_namespace_convention_v3.md); "
            f"canonical identifier would be {_canonical!r}",
            event,
        )
    # Default (proactive) mode: silently auto-suffix.
    event["milestone_id"] = f"{mid}-clone-{k}"
    return event'''

WRITER_OLD = '''    # Imported here to keep this module import-cheap for callers that never
    # append (workspace_bootstrap is imported broadly at startup).
    from long_exposure.tools._ledger_schema import (
        content_hash_event_id,
        validate_event,
        validate_history,
    )

    # Defensive copy — callers keep their original dict unmodified.
    if not isinstance(event, dict):
        raise LedgerAppendError(
            f"event must be a JSON object, got {type(event).__name__}", None
        )
    event = dict(event)

    # Auto-generate event_id when missing; existing values pass through.
    if "event_id" not in event or event.get("event_id") in (None, ""):
        event["event_id"] = content_hash_event_id(event)'''

WRITER_NEW = '''    # Imported here to keep this module import-cheap for callers that never
    # append (workspace_bootstrap is imported broadly at startup).
    from long_exposure.tools._ledger_schema import (
        content_hash_event_id,
        content_hash_event_id_v2,
        validate_event,
        validate_history,
    )

    # Defensive copy — callers keep their original dict unmodified.
    if not isinstance(event, dict):
        raise LedgerAppendError(
            f"event must be a JSON object, got {type(event).__name__}", None
        )
    event = dict(event)

    # Auto-generate event_id when missing; existing values pass through.
    # c48 sub-fix 2: thread MUSICGEN_LEDGER_SUPERSEDES_IN_HASH through
    # the UUID5 derivation path. Default OFF (exclude supersedes)
    # reproduces the on-disk c46 line-745 event_id.
    if "event_id" not in event or event.get("event_id") in (None, ""):
        event["event_id"] = content_hash_event_id_v2(
            event, include_supersedes=_supersedes_in_hash_active()
        )'''


def apply(target: pathlib.Path) -> None:
    body = target.read_text()
    if MARKER in body:
        print(f"already patched — skipping ({target})")
        return

    # Insert helpers block right BEFORE `def _existing_rows_for_milestone`
    # so it sits between _guard_clone_namespace and the writer machinery.
    anchor = "def _existing_rows_for_milestone(ledger: Path, milestone_id: str)"
    if anchor not in body:
        raise RuntimeError(f"anchor not found: {anchor!r}")
    body = body.replace(anchor, HELPERS_BLOCK.lstrip() + "\n\n" + anchor, 1)

    # Patch _guard_clone_namespace
    if GUARD_OLD not in body:
        raise RuntimeError("guard patch anchor not found")
    body = body.replace(GUARD_OLD, GUARD_NEW, 1)

    # Patch append_ledger_event
    if WRITER_OLD not in body:
        raise RuntimeError("writer patch anchor not found")
    body = body.replace(WRITER_OLD, WRITER_NEW, 1)

    target.write_text(body)
    print(f"patched {target}")
    print(f"  new size: {target.stat().st_size} bytes")


apply(TARGET)

# --- Verification --------------------------------------------------------
import importlib
import inspect
import os
import sys

sys.path.insert(0, '/home/user/human-in-a-loop/long-exposure')
import long_exposure.workspace_bootstrap as wb
importlib.reload(wb)

# API invariants
sig = str(inspect.signature(wb.append_ledger_event))
assert sig == "(workspace: pathlib.Path, event: dict) -> None", sig
print(f"append_ledger_event signature: {sig}")

# MRO invariant
from long_exposure.tools._ledger_schema import LedgerSchemaError
assert wb.LedgerNamespaceViolation.__mro__[0] is wb.LedgerNamespaceViolation
assert issubclass(wb.LedgerNamespaceViolation, LedgerSchemaError)
assert issubclass(wb.LedgerNamespaceViolation, ValueError)
print(f"LedgerNamespaceViolation MRO: "
      f"{[c.__name__ for c in wb.LedgerNamespaceViolation.__mro__]}")

# Helpers exist and are callable
assert callable(wb._substantive_exemption_active)
assert callable(wb._supersedes_in_hash_active)
assert callable(wb._should_suffix)

# Round-trip sub-fix 1
for env_val in (None, "0", "1", "true", "TRUE", "false"):
    if env_val is None:
        os.environ.pop("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", None)
    else:
        os.environ["MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION"] = env_val
    active = wb._substantive_exemption_active()
    should_suffix_m = wb._should_suffix("M-EAR-1/synthetic-test")
    should_suffix_infra = wb._should_suffix("_infra/synthetic-test")
    print(f"  env={env_val!r:8} active={active} should_suffix(M-)={should_suffix_m} "
          f"should_suffix(_infra/)={should_suffix_infra}")

# Round-trip sub-fix 2 semantics via patched writer's derivation
os.environ.pop("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", None)
os.environ.pop("MUSICGEN_LEDGER_SUPERSEDES_IN_HASH", None)
from long_exposure.tools._ledger_schema import content_hash_event_id_v2
import json as _json
lines = pathlib.Path('/home/user/long-exposure-runs/music-gen/promise_ledger.jsonl').read_text().splitlines()
r = _json.loads(lines[744])
assert content_hash_event_id_v2(r, include_supersedes=False) == "658231db-5d86-56e5-8ca9-2a9bed7fdf9f"
assert content_hash_event_id_v2(r, include_supersedes=True) == "6366af60-acb7-5e3f-a2e5-89b47f42c82f"
print("verification PASS")
