"""_ledger_schema — single source of truth for ledger event schema.

Extracted from promise_check.py and ledger_append.py in _infra/ledger-schema-hardening
(cycle 10, fork 00b3ae64444c clone 2, 2026-08-28) as the write-time and check-time
validation surface for promise_ledger.jsonl events.

Design contract:
    * Pure module. No imports from long_exposure.tools.promise_check,
      long_exposure.tools.ledger_append, or long_exposure.workspace_bootstrap.
    * validate_event(event) is a pure function returning list[str]; every field
      access is .get()-guarded. Never partial-crashes on malformed input.
    * content_hash_event_id(event) returns a deterministic UUID5 derived from
      canonical-JSON of the event with ``event_id`` and ``ts`` removed. This
      preserves the pre-existing invariant that event_ids validate as UUIDs
      (see promise_check._check_uuid).
    * Extension fields (fields not in REQUIRED_EVENT_FIELDS) are tolerated by
      default; validate_event only checks presence + shape of required fields
      plus the well-known optional fields (confidence, artifacts, supersedes,
      supersedes_path, reporter_mode).
    * Cycle-15 (_infra/ledger-schema-hardening-v3): adds the canonical
      per-milestone state-transition graph ``_STATE_TRANSITIONS`` and a pure
      ``validate_history(rows)`` function. Both are additive; existing callers
      never see behavior changes.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from typing import Iterable

# --- Constants (canonical, imported by promise_check + ledger_append) --------

REQUIRED_EVENT_FIELDS: tuple[str, ...] = (
    "event_id",
    "ts",
    "run_id",
    "cycle",
    "agent",
    "milestone_id",
    "status",
    "confidence",
    "narrative",
)

CONFIDENCE_LEVELS: frozenset[str] = frozenset({"provisional", "low", "medium", "high"})

CONFIDENCE_REQUIRED_SUBFIELDS: tuple[str, ...] = ("level", "rationale", "assessor")

STATUS_VALUES: frozenset[str] = frozenset({
    "not-started",
    "in-progress",
    "validated",
    "invalidated",
    "reopened",
    "deferred",
    "action_required",
    "superseded",
})

# Alias for pre-concat lint + external reference (cycle-14 hardening).
# This is the enum the brief calls out; kept as-is because 275/275 rows use
# a strict subset {validated, in-progress, reopened, invalidated}.
_STATUS_ENUM = STATUS_VALUES

# --- Cycle-15 state-transition graph (_infra/ledger-schema-hardening-v3) ----
#
# Canonical per-milestone consecutive-status transition graph. Each tuple is
# an allowed (prev_status, next_status) pair; every other pair is illegal and
# rejected by ``validate_history``.
#
# Derived from the brief:
#   not-started -> in-progress
#   in-progress -> {validated, invalidated}
#   validated -> reopened
#   invalidated -> reopened
#   reopened -> {in-progress, validated, invalidated}
#   validated -> superseded
#   deferred <-> in-progress
#   action_required <-> in-progress
#
# Expanded with the two self-loops observed in the 301-row historical sweep
# (`tools/_v3_sweep.py`, cycle 15 clone 0), both semantically legitimate:
#   * validated -> validated (54x): parent milestone re-validated after a
#     new sub-milestone rolls up. Common for M-* parent capstones.
#   * in-progress -> in-progress (3x): mid-cycle progress-note update
#     without a status change (e.g. researcher amending the goal narrative).
#
# The `expand-when-legitimate` escape hatch mirrors cycle-14's approach for
# the enum (STATUS_VALUES): when a legitimate historical pattern surfaces,
# expand the graph rather than grandfather rows.
_STATE_TRANSITIONS: frozenset[tuple[str, str]] = frozenset({
    # brief-specified transitions
    ("not-started", "in-progress"),
    ("in-progress", "validated"),
    ("in-progress", "invalidated"),
    ("validated", "reopened"),
    ("invalidated", "reopened"),
    ("reopened", "in-progress"),
    ("reopened", "validated"),
    ("reopened", "invalidated"),
    ("validated", "superseded"),
    ("deferred", "in-progress"),
    ("in-progress", "deferred"),
    ("action_required", "in-progress"),
    ("in-progress", "action_required"),
    # historical self-loops (observed in the 301-row sweep, legitimate)
    ("validated", "validated"),
    ("in-progress", "in-progress"),
})

# Canonical short-form assessor tokens. Long-form / decorated assessors
# (e.g. "cyd7bevdr@mozmail.com (worker, cycle 9, fork ..., clone 2)")
# are the drift pattern the cycle-9 audit surfaced; those are rejected.
ASSESSORS: frozenset[str] = frozenset({
    "worker",
    "researcher",
    "auditor",
    "harness",
    "human",
    "manager",
    "final_auditor",
})

# --- Regexes for shape checks -----------------------------------------------

# Accept two ts shapes:
#   * "2026-08-28T04:07:04Z"                  (canonical, used by workspace_bootstrap._now_iso)
#   * "2026-08-28T04:07:04+00:00"             (Python datetime.isoformat() default)
# Both are UTC ISO-8601. Fractional seconds allowed.
TS_REGEX: re.Pattern[str] = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)

# run_id shapes seen in the ledger:
#   * "run-2026-08-28T040704Z"                (canonical plan-of-record run_id)
#   * "run-unknown"                            (bootstrap fallback)
#   * "fork-<hex>-clone-<n>"                   (per-clone shadow-ledger run_id)
RUN_ID_REGEX: re.Pattern[str] = re.compile(
    r"^(?:run-(?:unknown|\d{4}-\d{2}-\d{2}T\d{6}Z))$"
    r"|^fork-[0-9a-f]{6,32}-clone-\d+$"
)

# milestone_id shapes:
#   * "M-<UPPER>-<n>[/subpath]"                (canonical milestone IDs)
#   * "_run/...", "_plan/...", "_infra/...", "_manager/...", "_archive/...", "_audit/..."
MILESTONE_ID_REGEX: re.Pattern[str] = re.compile(
    r"^(?:M-[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?-\d+(?:/[A-Za-z0-9_.\-/]+)?"
    r"|_(?:run|plan|infra|manager|archive|audit|report|handoff|proto)/[A-Za-z0-9_.\-/]+)$"
)

# Namespace for content-derived UUID5 event_ids. Fixed; changing it would
# break re-derivation of any historical id.
_EVENT_ID_NAMESPACE = uuid.UUID("00000000-0000-5000-8000-6c6564676572")  # ns hex for "ledger"


# --- Error type --------------------------------------------------------------

class LedgerSchemaError(ValueError):
    """Base for ledger schema validation failures.

    Callers of append_ledger_event that catch LedgerAppendError also catch
    this transparently — LedgerAppendError is a thin re-brand of this class
    at the writer boundary (see workspace_bootstrap.append_ledger_event).
    """

    def __init__(self, message: str, event: dict | None = None) -> None:
        super().__init__(message)
        self.event = event or {}


class LedgerConcatError(LedgerSchemaError):
    """Raised by ``workspace_bootstrap.concat_clone_ledgers`` when a merged
    row fails schema validation, when a JSON parse fails on a candidate
    clone-ledger line, or when per-milestone file-order timestamp
    monotonicity is violated within the candidate stream.

    Real subclass of ``LedgerSchemaError`` (not a re-brand): callers that
    already ``except LedgerSchemaError`` catch this transparently.
    Established in _infra/fanout-concat-hardening (cycle 12, fork
    ed041ef4c1dc clone 1) to close the last drift surface — the fan-out
    collapse boundary — through which shadow-ledger rows bypassed the
    write-time invariants that cycle 10 SSoT extraction enforces
    everywhere else.
    """


def content_hash_tiebreak(event: dict) -> str:
    """SHA-256 hex digest of the event canonical JSON, with ``event_id``
    and ``ts`` excluded from the hash input (same exclusion set as
    ``content_hash_event_id``).

    Used by ``workspace_bootstrap.concat_clone_ledgers`` as the deterministic
    tiebreak when two events for the same milestone share a wall-clock ``ts``.
    Deliberately NOT the file line number (cycle 11 bug) and NOT the
    ``event_id`` itself (event_ids for content-identical events are equal by
    construction of ``content_hash_event_id``, so an event_id tiebreak
    collapses to hash-of-content anyway; using hash-of-content directly is
    the clearer contract).
    """
    payload = canonical_json(event)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# --- Pure helpers ------------------------------------------------------------

def canonical_json(event: dict) -> str:
    """Deterministic JSON serialization of an event with the fields excluded
    from content hashing (event_id, ts) removed. Sorted keys, tightest separators.

    Used for content_hash_event_id() and, secondarily, for byte-level round-trip
    determinism checks in the test suite.
    """
    core = {k: v for k, v in (event or {}).items() if k not in ("event_id", "ts")}
    return json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_hash_event_id(event: dict) -> str:
    """Return a UUID5-format event_id derived deterministically from the event's
    canonical content (excludes event_id + ts from the hash input).

    Chosen UUID5 (not raw SHA-256 hex prefix) because promise_check._check_uuid
    already requires event_ids to be valid UUID strings; a hex prefix would
    fail that invariant. UUID5 preserves the invariant while giving determinism.
    """
    payload = canonical_json(event)
    return str(uuid.uuid5(_EVENT_ID_NAMESPACE, payload))


def _is_uuid(value: object) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except (TypeError, ValueError, AttributeError):
        return False


# --- The validator -----------------------------------------------------------

_OPTIONAL_WELL_KNOWN = ("artifacts", "supersedes", "supersedes_path", "reporter_mode")


def validate_event(event: object) -> list[str]:
    """Return a list of specific error strings; empty list => event is valid.

    Never raises on malformed input. Every access is .get()-guarded so a
    non-dict, empty dict, or dict with unexpected value types produces
    error strings, not a partial crash.
    """
    errors: list[str] = []
    if not isinstance(event, dict):
        errors.append(f"event must be a JSON object, got {type(event).__name__}")
        return errors

    # Required-field presence.
    for field in REQUIRED_EVENT_FIELDS:
        if field not in event:
            errors.append(f"missing required field {field!r}")

    # event_id must be a valid UUID if present. Uniqueness is enforced by the
    # writer/checker at ledger scope (see workspace_bootstrap.append_ledger_event
    # duplicate-id check), not here.
    eid = event.get("event_id")
    if eid is not None and not _is_uuid(eid):
        errors.append(f"event_id {eid!r} is not a valid UUID")

    # ts shape.
    ts = event.get("ts")
    if ts is not None and (not isinstance(ts, str) or not TS_REGEX.match(ts)):
        errors.append(f"ts {ts!r} does not match ISO-8601 UTC (expected e.g. 2026-08-28T04:07:04Z)")

    # run_id shape.
    rid = event.get("run_id")
    if rid is not None and (not isinstance(rid, str) or not RUN_ID_REGEX.match(rid)):
        errors.append(
            f"run_id {rid!r} does not match canonical shape "
            f"(run-YYYY-MM-DDTHHMMSSZ, run-unknown, or fork-<hex>-clone-<n>)"
        )

    # cycle must be a positive int.
    cyc = event.get("cycle")
    if cyc is not None and (not isinstance(cyc, int) or isinstance(cyc, bool) or cyc < 1):
        errors.append(f"cycle {cyc!r} must be a positive integer")

    # agent must be one of the canonical assessors (same vocabulary).
    agent = event.get("agent")
    if agent is not None and (not isinstance(agent, str) or agent not in ASSESSORS):
        errors.append(f"agent {agent!r} not in canonical assessor set {sorted(ASSESSORS)}")

    # milestone_id shape.
    mid = event.get("milestone_id")
    if mid is not None and (not isinstance(mid, str) or not MILESTONE_ID_REGEX.match(mid)):
        errors.append(f"milestone_id {mid!r} does not match canonical shape")

    # status vocabulary.
    status = event.get("status")
    if status is not None and status not in STATUS_VALUES:
        errors.append(
            f"status {status!r} not in unified vocabulary {sorted(STATUS_VALUES)}"
        )

    # confidence: must be a nested object with the three required subfields
    # and canonical assessor. The cycle-8 drift ("confidence": "high") and
    # cycle-9 drift (long-form assessor) both fail here.
    conf = event.get("confidence")
    if conf is not None:
        if not isinstance(conf, dict):
            errors.append(
                f"confidence must be an object with subfields {list(CONFIDENCE_REQUIRED_SUBFIELDS)}, "
                f"got {type(conf).__name__} ({conf!r})"
            )
        else:
            for sub in CONFIDENCE_REQUIRED_SUBFIELDS:
                if sub not in conf:
                    errors.append(f"confidence.{sub} missing")
            level = conf.get("level")
            if level is not None and level not in CONFIDENCE_LEVELS:
                errors.append(
                    f"confidence.level {level!r} not in {sorted(CONFIDENCE_LEVELS)}"
                )
            rationale = conf.get("rationale")
            if rationale is not None and (
                not isinstance(rationale, str) or not rationale.strip()
            ):
                errors.append("confidence.rationale must be a non-empty string")
            assessor = conf.get("assessor")
            if assessor is not None and (
                not isinstance(assessor, str) or assessor not in ASSESSORS
            ):
                errors.append(
                    f"confidence.assessor {assessor!r} not in canonical set "
                    f"{sorted(ASSESSORS)} (long-form/decorated assessors are the "
                    f"drift pattern from cycle 9; use short-form and put the "
                    f"decorated identity in an optional assessor_original field)"
                )

    # narrative: if present, must be a non-empty string.
    narrative = event.get("narrative")
    if narrative is not None and (
        not isinstance(narrative, str) or not narrative.strip()
    ):
        errors.append("narrative must be a non-empty string")

    # artifacts (optional): if present, list[str].
    artifacts = event.get("artifacts")
    if artifacts is not None and (
        not isinstance(artifacts, list)
        or not all(isinstance(a, str) for a in artifacts)
    ):
        errors.append("artifacts must be a list of strings")

    # supersedes (optional): str or list[str].
    supersedes = event.get("supersedes")
    if supersedes is not None:
        ok = isinstance(supersedes, str) or (
            isinstance(supersedes, list)
            and all(isinstance(r, str) for r in supersedes)
        )
        if not ok:
            errors.append("supersedes must be a string or list of strings")

    # supersedes_path (optional, cycle-14 hardening): must be a string.
    # Cycle-13 drift: line 266 emitted a list-form supersedes_path which
    # crashed promise_check._canon (AttributeError: list has no lstrip).
    supersedes_path = event.get("supersedes_path")
    if supersedes_path is not None and not isinstance(supersedes_path, str):
        errors.append(
            f"supersedes_path must be a string, got "
            f"{type(supersedes_path).__name__} ({supersedes_path!r}) "
            f"— cycle-13 drift: list-form crashed promise_check._canon"
        )

    return errors


# --- Cycle-15 per-milestone transition validator ---------------------------

def validate_history(rows: Iterable[dict]) -> list[str]:
    """Group ``rows`` by ``milestone_id``, sort each group by ``ts``, and
    return specific error strings for every illegal consecutive
    (prev_status, next_status) transition, using ``_STATE_TRANSITIONS`` as
    the ground-truth graph.

    Never raises on malformed input. Rows lacking a ``milestone_id`` are
    grouped under the sentinel ``""`` bucket; rows lacking ``status`` are
    skipped (validate_event catches missing-status separately). Rows whose
    ``status`` is not in STATUS_VALUES are also skipped here (again,
    validate_event catches unknown-status separately).

    Error message shape matches the brief:
        "<milestone_id>: illegal transition <prev> -> <next> between event
        <eid_prev> (ts=<ts_prev>) and event <eid_next> (ts=<ts_next>) —
        not in _STATE_TRANSITIONS"

    Cycle-13 line-250 pattern (validated -> in-progress without an
    intervening reopened event) is the flagship rejection this function
    catches at every writer + pre-concat lint call site.
    """
    errors: list[str] = []

    by_mid: dict[str, list[dict]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        mid = row.get("milestone_id") or ""
        by_mid.setdefault(mid, []).append(row)

    for mid, evs in by_mid.items():
        # Sort by ts (lexicographic ISO-8601 sort is chronologically correct
        # for both canonical shapes accepted by TS_REGEX). Rows without a ts
        # sort to the front (empty string) — validate_event catches those
        # separately as a ts-shape error.
        evs.sort(key=lambda e: e.get("ts", ""))
        prev = None
        for ev in evs:
            status = ev.get("status")
            if not isinstance(status, str) or status not in STATUS_VALUES:
                # validate_event catches unknown/missing status; skip here so
                # a single row does not blow up the whole history walk.
                continue
            if prev is not None:
                prev_status = prev.get("status")
                if (prev_status, status) not in _STATE_TRANSITIONS:
                    errors.append(
                        f"{mid}: illegal transition {prev_status!r} -> "
                        f"{status!r} between event {prev.get('event_id')!r} "
                        f"(ts={prev.get('ts')!r}) and event "
                        f"{ev.get('event_id')!r} (ts={ev.get('ts')!r}) — "
                        f"not in _STATE_TRANSITIONS"
                    )
            prev = ev

    return errors
