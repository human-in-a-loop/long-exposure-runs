"""Workspace bootstrap + plan/ledger helpers.

Stdlib-only. Called once per fresh run from exploration.py to lay down the
standard folder skeleton, render plan_of_record.md and STRUCTURE.md from
templates, and append a `_run/start` bootstrap event to promise_ledger.jsonl.
On resume of an existing run, this is a no-op (graceful by design — see
docs/workspace-conventions.md).

Also provides the cycle-input summarizer used to inject a token-bounded
view of the ledger into each cycle's agent prompts.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

STANDARD_FOLDERS = ("reports", "audits", "scripts", "tests", "data", "docs", "tools", "stale")

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug_from_directive(directive: str, max_len: int = 60) -> str:
    """Cheap slug for a Plan-of-Record title."""
    text = (directive or "exploration").strip().splitlines()[0] if directive else "exploration"
    text = text[:max_len].strip()
    return text or "exploration"


def is_fresh_start(workspace: Path, current_cycle: int) -> bool:
    """A run qualifies for bootstrap iff cycle == 1 AND no prior plan exists.

    Per docs/workspace-conventions.md, mid-run resumes never bootstrap.
    """
    if current_cycle > 1:
        return False
    if (workspace / "plan_of_record.md").exists():
        return False
    return True


def ensure_skeleton(workspace: Path) -> list[str]:
    """Create the standard folder skeleton if missing. Returns folders created.

    Idempotent — calling on an already-bootstrapped workspace is a no-op.
    """
    created = []
    for folder in STANDARD_FOLDERS:
        d = workspace / folder
        if not d.exists():
            try:
                d.mkdir(parents=True, exist_ok=True)
                created.append(folder)
            except OSError:
                pass
    try:
        from long_exposure.paths import ensure_layout
        ensure_layout(workspace)
    except OSError:
        pass
    return created


def render_template(name: str, **subs: str) -> str:
    """Read a template file and substitute {placeholders}. Returns the body."""
    path = _TEMPLATE_DIR / name
    text = path.read_text()
    return text.format(**subs)


def write_plan_of_record(workspace: Path, directive: str, run_id: str) -> Path:
    """Render and write plan_of_record.md if missing. Returns the path."""
    plan = workspace / "plan_of_record.md"
    if plan.exists():
        return plan
    body = render_template(
        "plan_of_record_template.md",
        created=_now_iso(),
        run_id=run_id,
        title=_slug_from_directive(directive),
        directive=directive.strip(),
    )
    plan.write_text(body)
    return plan


def write_structure_md(workspace: Path, run_id: str) -> Path:
    """Render and write STRUCTURE.md if missing. Returns the path."""
    s = workspace / "STRUCTURE.md"
    if s.exists():
        return s
    body = render_template(
        "structure_template.md",
        created=_now_iso(),
        run_id=run_id,
    )
    s.write_text(body)
    return s


def resolve_ledger_path(workspace: Path) -> Path:
    """Pick the right ledger file for the calling process (Plan 1 §6).

    Clones — detected via the AGENT_FORK_ID env var that the fan-out conductor
    sets when spawning each clone subprocess — write to their per-clone
    shadow ledger at ``<instance_dir>/promise_ledger.jsonl``. The fan-out
    conductor concatenates these into the workspace's main ledger after the
    barrier collapses (see ``fanout._concat_clone_ledgers``).

    Root processes (and any caller without ``AGENT_FORK_ID``) write directly
    to the workspace main ledger.
    """
    if os.environ.get("AGENT_FORK_ID"):
        instance_dir = os.environ.get("AGENT_INSTANCE_DIR")
        if instance_dir:
            d = Path(instance_dir)
            d.mkdir(parents=True, exist_ok=True)
            return d / "promise_ledger.jsonl"
    return workspace / "promise_ledger.jsonl"


class LedgerAppendError(ValueError):
    """Raised by ``append_ledger_event`` when the event fails schema
    validation before write. The full event dict is available on ``.event``
    for debug. Callers get validation failures in their own process rather
    than as mystery ERROR rows surfaced by a downstream ``promise_check``
    integration cycle (see _infra/ledger-schema-hardening, cycle 10).
    """

    def __init__(self, message: str, event: dict | None = None) -> None:
        super().__init__(message)
        self.event = event or {}


# ---------------------------------------------------------------------------
# _infra/harness-clone-namespace-guard (cycle 33, fork 4595e91f7574 / clone 2)
#
# Writer-boundary enforcement of the c32 fanout-namespace convention
# (docs/fanout_namespace_convention_v3.md). When the process detects it is
# running as a fan-out clone AND the emitting milestone_id matches one of
# the five leading-underscore infra families AND the id is not already
# ``-clone-<digit>+``-suffixed:
#
#   default mode (MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE unset or "0"):
#     the writer silently rewrites the emitting ``milestone_id`` to
#     ``<mid>-clone-<k>``. Parity with c22's silent auto-namespacing in
#     exploration._append_report_artifact_event.
#
#   strict mode  (MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1):
#     the writer raises ``LedgerNamespaceViolation`` (typed subclass of
#     _ledger_schema.LedgerSchemaError) with a field-named message
#     identifying the offending id, the detected clone-k, and a pointer
#     to the convention doc.
#
# Substantive ``M-*`` identifiers are never touched. Identifiers without a
# leading ``_<family>/`` prefix (bare tokens like ``foo/bar``) are never
# touched. Already-suffixed identifiers are never double-suffixed.
#
# The same detection is applied at the concat boundary by
# ``_lint_clone_shadow``. The public API of ``append_ledger_event(workspace,
# event)`` is UNCHANGED - the new behavior is entirely internal to the writer.
# ---------------------------------------------------------------------------

# c36 _infra/fanout-namespace-convention-v2: extended from the v1
# leading-underscore infra families to include substantive M-* families.
# Rationale: third LedgerConcatError observed on M-INGEST-1/egress-probe
# between fork 87da4f517029 clone-0 and clone-2. See docs/fanout_namespace_convention_v2.md.
_FANOUT_INFRA_PREFIXES = (
    # v1 infra families
    "_infra/", "_run/", "_plan/", "_archive/", "_manager/",
    # v2 substantive milestone families (c36)
    "M-INGEST-1/", "M-SEP-1/", "M-CLASS-1/", "M-DAW-SPIKE-1/",
    "M-TRANS-1/", "M-SCORE-1/", "M-HEUR-1/", "M-EAR-1/",
    "M-RULES-1/", "M-TEX-1/", "M-GEN-1/", "M-RECREATE-1/",
)
_CLONE_SUFFIX_RE = re.compile(r"-clone-\d+$")

# Import LedgerSchemaError at module load so LedgerNamespaceViolation can
# inherit from it directly (avoiding a fragile late-rebind that would break
# super() calls in a caller-visible way). _ledger_schema has no dependency
# on workspace_bootstrap (see tests/test_ledger_writer_validation.py
# test_13_no_import_cycles), so this is safe.
from long_exposure.tools._ledger_schema import (  # noqa: E402
    LedgerSchemaError as _LedgerSchemaError,
)


class LedgerNamespaceViolation(_LedgerSchemaError):
    """Raised by ``append_ledger_event`` (strict mode) or
    ``_lint_clone_shadow`` when a fan-out clone emits a leading-underscore
    infra-family identifier without the ``-clone-<k>`` suffix that the c32
    convention requires.

    Real subclass of
    ``long_exposure.tools._ledger_schema.LedgerSchemaError`` — a caller
    that already catches ``LedgerSchemaError`` catches this transparently.
    The MRO is verified by
    ``tests/test_harness_clone_namespace_guard.py::test_14_MRO_LedgerNamespaceViolation_subclass_of_LedgerSchemaError``.
    """

    def __init__(self, message: str, event: dict | None = None,
                 shadow_path: "Path | None" = None,
                 line_no: int | None = None) -> None:
        super().__init__(message)
        self.event = event or {}
        self.shadow_path = shadow_path
        self.line_no = line_no


def _is_clone_context(workspace: Path) -> tuple[bool, int | None]:
    """Detect whether this process is running as a fan-out clone.

    Mirrors the pattern used by ``long_exposure.exploration._is_clone`` +
    ``_get_clone_k`` (see cycle-22 ``_infra/harness-auto-write-namespacing``).
    Reads process env vars - ``AGENT_FORK_ID`` marks a clone process, and
    ``AGENT_FORK_CLONE_K`` carries the zero-based clone index within its
    fork. The ``workspace`` argument is accepted for future-proofing (a
    workspace-side manifest could override the env-var contract) but is
    unused at present - matches the signature style other writer helpers
    in this module follow.

    Returns:
        (True, k) when running under a clone with a parseable non-negative
        K; else (False, None).
    """
    fid = os.environ.get("AGENT_FORK_ID", "").strip()
    if not fid:
        return (False, None)
    raw_k = os.environ.get("AGENT_FORK_CLONE_K", "").strip()
    if not raw_k:
        return (False, None)
    try:
        k = int(raw_k)
    except ValueError:
        return (False, None)
    if k < 0:
        return (False, None)
    _ = workspace  # signature parity; unused today
    return (True, k)


def _guard_clone_namespace(event: dict, workspace: Path) -> dict:
    """Enforce the c32 fanout-namespace convention at the writer boundary.

    Called by ``append_ledger_event`` after schema validation. Returns the
    event dict (possibly with ``milestone_id`` mutated to append the
    ``-clone-<k>`` suffix). Raises ``LedgerNamespaceViolation`` when strict
    mode is enabled and a violation is detected.

    The event is mutated in place AND returned - matches c22's silent
    auto-namespacing behavior (no log line, no warning). Callers that need
    to detect the mutation can compare pre/post ``milestone_id``.
    """
    mid = event.get("milestone_id")
    if not isinstance(mid, str):
        return event
    # Must be one of the five leading-underscore infra families.
    if not any(mid.startswith(p) for p in _FANOUT_INFRA_PREFIXES):
        return event
    # Idempotence: if already ``-clone-<digit>+`` suffixed, leave alone.
    if _CLONE_SUFFIX_RE.search(mid):
        return event
    # Detect clone context.
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
    return event




def _existing_rows_for_milestone(ledger: Path, milestone_id: str) -> list[dict]:
    """Return every row in ``ledger`` whose ``milestone_id`` matches. Skips
    malformed lines silently (validate_event catches those separately).
    Empty list if the ledger does not exist.
    """
    if not ledger.exists():
        return []
    rows: list[dict] = []
    try:
        with open(ledger, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(ev, dict) and ev.get("milestone_id") == milestone_id:
                    rows.append(ev)
    except OSError:
        return []
    return rows


def append_ledger_event(workspace: Path, event: dict) -> None:
    """Append a single event to the appropriate ledger file atomically.

    Routes clone-side writes to a per-clone shadow ledger (Plan 1 §6) so
    concurrent clones never interleave bytes into the workspace main file.
    JSONL appends are mostly atomic at the OS level for small lines (POSIX
    O_APPEND + a single write() under PIPE_BUF); shadow ledgers eliminate
    the small-line contention boundary entirely.

    Schema hardening (cycle 10, _infra/ledger-schema-hardening): before
    writing, the event is validated against
    ``long_exposure.tools._ledger_schema.validate_event``. If ``event_id``
    is missing, a deterministic UUID5 is derived from the canonical-JSON
    content hash. If validation fails, ``LedgerAppendError`` is raised
    BEFORE the file is opened, so a rejected event never touches disk
    (atomicity on validation failure).

    Transition hardening (cycle 15, _infra/ledger-schema-hardening-v3):
    after the per-event pass, the resolved ledger is scanned for existing
    rows sharing the candidate's ``milestone_id``. The candidate is spliced
    onto that history (sorted by ``ts``), and ``validate_history`` is run
    against the resulting per-milestone sequence. On a transition failure —
    e.g. the cycle-13 line-250 pattern ``validated -> in-progress`` without
    an intervening ``reopened`` — ``LedgerAppendError`` is raised BEFORE
    the file is opened. Atomicity preserved.
    """
    # Imported here to keep this module import-cheap for callers that never
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
        event["event_id"] = content_hash_event_id(event)

    errors = validate_event(event)
    if errors:
        raise LedgerAppendError(
            f"ledger event schema validation failed on {len(errors)} field(s): "
            + "; ".join(errors),
            event,
        )

    # Cycle-33 _infra/harness-clone-namespace-guard: c32 convention enforcement.
    # Guard runs AFTER schema validation and BEFORE the mutated milestone_id
    # is used to resolve prior rows for the duplicate-id + transition checks.
    event = _guard_clone_namespace(event, workspace)

    ledger = resolve_ledger_path(workspace)

    # Duplicate-event_id guard (cycle 10, _infra/ledger-schema-hardening):
    # scan existing rows for an event_id collision. This hardens the invariant
    # that promise_check previously surfaced only at post-merge time. Cheap
    # scan even at O(N) — ledger files are line-oriented JSONL well under
    # 10^5 rows in practice.
    if ledger.exists():
        target_id = event["event_id"]
        needle = f'"event_id":"{target_id}"'
        try:
            with open(ledger, "r", encoding="utf-8") as f:
                for existing_line in f:
                    if needle in existing_line:
                        raise LedgerAppendError(
                            f"duplicate event_id {target_id!r}: already present in "
                            f"{ledger}",
                            event,
                        )
        except OSError:
            # If we cannot read the file (permissions), fall through — the write
            # will surface the OS error naturally.
            pass

    # Transition validation (cycle 15): scan same-milestone prior rows,
    # splice in the candidate, run validate_history. Duplicate event_id
    # is already blocked above, so no double-count risk here.
    mid = event.get("milestone_id")
    if isinstance(mid, str):
        prior = _existing_rows_for_milestone(ledger, mid)
        history_errors = validate_history(prior + [event])
        if history_errors:
            raise LedgerAppendError(
                f"ledger event history validation failed on "
                f"{len(history_errors)} transition(s): "
                + "; ".join(history_errors),
                event,
            )

    line = json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"
    # O_APPEND ensures the kernel performs the seek+write atomically per call.
    fd = os.open(ledger, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)


def _lint_clone_shadow(shadow_path: "Path") -> None:
    """Run cycle-10 SSoT validate_event on every row of a clone shadow ledger,
    then run cycle-15 validate_history on the whole shadow grouped by
    ``milestone_id``. Raises LedgerConcatError on the first failure.

    Cycle-14 hardening seam (_infra/ledger-schema-hardening-v2): lets a clone
    lint its OWN shadow at emit boundary — surfacing drift where the operator
    can attribute it, instead of at fork-integration inside concat_clone_ledgers.

    Cycle-15 hardening seam (_infra/ledger-schema-hardening-v3): after the
    per-row pass, runs ``validate_history`` on the collected rows. This
    catches the cycle-13 line-250 pattern (``validated -> in-progress``
    without an intervening ``reopened``) WITHIN a single clone shadow before
    the fanout concat ever sees it.

    On failure the message includes the shadow path AND (for per-row errors)
    the line number AND the underlying error string (which names the offending
    field or transition). For transition errors, the message names the
    milestone_id and the (prev_status, next_status) pair. On empty files
    (no lines or all blank), returns cleanly.

    concat_clone_ledgers ALREADY runs the same per-line validation on merge —
    this helper is the exposed, importable form of that check. No public API
    of concat_clone_ledgers changes.
    """
    from long_exposure.tools._ledger_schema import (
        LedgerConcatError,
        validate_event,
        validate_history,
    )
    rows: list[dict] = []
    with open(shadow_path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                raise LedgerConcatError(
                    f"{shadow_path}:{lineno}: invalid JSON: {e}"
                ) from e
            errors = validate_event(row)
            if errors:
                raise LedgerConcatError(
                    f"{shadow_path}:{lineno} "
                    f"(milestone_id={row.get('milestone_id')!r}): "
                    + "; ".join(errors),
                    row,
                )
            # Cycle-33 _infra/harness-clone-namespace-guard: same detection at
            # concat boundary. A shadow-ledger row emitted with a bare
            # leading-underscore infra id (no -clone-<k>) surfaces as a
            # LedgerNamespaceViolation with <shadow_path>:<line_no> annotation.
            _ns_mid = row.get("milestone_id")
            if isinstance(_ns_mid, str) and any(
                _ns_mid.startswith(p) for p in _FANOUT_INFRA_PREFIXES
            ) and not _CLONE_SUFFIX_RE.search(_ns_mid):
                # Recover clone-k: prefer the shadow_path's clone-<N>
                # segment; fall back to the current process env.
                _sk: int | None = None
                for _part in reversed(Path(shadow_path).parts):
                    _m = re.match(r"^clone-(\d+)$", _part)
                    if _m:
                        try:
                            _sk = int(_m.group(1))
                        except ValueError:
                            _sk = None
                        break
                if _sk is None:
                    _raw_env_k = os.environ.get("AGENT_FORK_CLONE_K", "").strip()
                    if _raw_env_k:
                        try:
                            _sk = int(_raw_env_k)
                        except ValueError:
                            _sk = None
                _canon_suffix = (
                    f"-clone-{_sk}" if _sk is not None else "-clone-<k>"
                )
                raise LedgerNamespaceViolation(
                    f"{shadow_path}:{lineno}: milestone_id={_ns_mid!r} in "
                    f"clone shadow ledger is missing the required "
                    f"-clone-<k> suffix per the c32 fanout namespace "
                    f"convention (docs/fanout_namespace_convention_v3.md); "
                    f"clone_k={_sk!r}, canonical identifier would be "
                    f"{_ns_mid + _canon_suffix!r}",
                    row,
                    Path(shadow_path),
                    lineno,
                )
            rows.append(row)

    # Cycle-15: per-milestone transition sweep across the whole shadow.
    if rows:
        history_errors = validate_history(rows)
        if history_errors:
            raise LedgerConcatError(
                f"{shadow_path}: per-milestone transition validation failed "
                f"on {len(history_errors)} transition(s): "
                + "; ".join(history_errors)
            )


def concat_clone_ledgers(workspace: Path, fork_dir: Path) -> int:
    """Merge clone shadow ledgers into the workspace main ledger.

    Called by the fan-out conductor after the barrier collapses. Walks
    ``fork_dir/clone-*/promise_ledger.jsonl`` files, reads all events,
    deduplicates by ``event_id`` (idempotent — re-running concat after
    a partial run never produces duplicate lines), then appends the
    new events to the workspace main ledger sorted per-milestone by
    ``(ts, content_hash_tiebreak)``.

    Returns the count of newly-appended events.

    Hardened in _infra/fanout-concat-hardening (cycle 12, fork
    ed041ef4c1dc/1) — closes the last drift surface (cycles 10 + 11
    post-merge repair sink). New invariants, all enforced at concat
    time and raised as ``LedgerConcatError`` (subclass of
    ``LedgerSchemaError``):

      (i)   every candidate row is validated against the cycle-10 SSoT
            ``_ledger_schema.validate_event`` — same object identity as
            the writer and checker use;
      (ii)  json.JSONDecodeError on a candidate line is surfaced (not
            silently skipped) with source clone path + line number;
      (iii) per-milestone file-order ts monotonicity is enforced WITHIN
            the candidate stream — a clone that emits [ts=T2, ts=T1]
            for the same milestone with T1 < T2 is rejected (this is
            the cycle-11 drift pattern);
      (iv)  ts-collision tiebreak inside a milestone group uses the
            SHA-256 content hash (``content_hash_tiebreak``), NEVER
            file line number (which was cycle-11's bug);
      (v)   the write is atomic: rows are staged into a sibling temp
            file, fsynced, then ``os.replace``d onto the main path —
            on any validation failure, the main ledger is untouched.

    The main ledger's pre-existing content is grandfathered against
    the file-order monotonicity check (seven cycle-1-era violations
    exist from fan-out collapses that pre-date this contract) but
    IS re-validated for schema conformance — no grandfathering for
    schema.

    Zero caller-side changes: same name, same argument names, same
    return type. All prior fan-out invocations continue to work.
    """
    # Import here to avoid pulling _ledger_schema into every startup path
    # (workspace_bootstrap is imported broadly at boot).
    from long_exposure.tools._ledger_schema import (
        LedgerConcatError,
        content_hash_tiebreak,
        validate_event,
    )

    main_ledger = workspace / "promise_ledger.jsonl"

    seen_ids: set[str] = set()
    if main_ledger.exists():
        for lineno, raw in enumerate(main_ledger.read_text().splitlines(), 1):
            line = raw.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError as e:
                raise LedgerConcatError(
                    f"main ledger {main_ledger} line {lineno}: "
                    f"json parse failed: {e}"
                )
            if not isinstance(ev, dict):
                raise LedgerConcatError(
                    f"main ledger {main_ledger} line {lineno}: "
                    f"expected JSON object, got {type(ev).__name__}"
                )
            errors = validate_event(ev)
            if errors:
                raise LedgerConcatError(
                    f"main ledger {main_ledger} line {lineno} (milestone_id="
                    f"{ev.get('milestone_id')!r}) failed schema validation on "
                    f"{len(errors)} field(s): " + "; ".join(errors),
                    ev,
                )
            eid = ev.get("event_id")
            if eid:
                seen_ids.add(eid)

    new_events: list[dict] = []
    if not fork_dir.exists():
        return 0

    # Per-milestone last-seen ts within the CANDIDATE stream (main is
    # grandfathered against monotonicity). Tracks the ts of the last
    # non-skipped candidate row per milestone across all clones in
    # path-sorted order.
    last_candidate_ts: dict[str, tuple[str, Path, int]] = {}

    for clone_ledger in sorted(fork_dir.glob("clone-*/promise_ledger.jsonl")):
        for lineno, raw in enumerate(clone_ledger.read_text().splitlines(), 1):
            line = raw.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError as e:
                raise LedgerConcatError(
                    f"clone ledger {clone_ledger} line {lineno}: "
                    f"json parse failed: {e}"
                )
            if not isinstance(ev, dict):
                raise LedgerConcatError(
                    f"clone ledger {clone_ledger} line {lineno}: "
                    f"expected JSON object, got {type(ev).__name__}"
                )
            errors = validate_event(ev)
            if errors:
                raise LedgerConcatError(
                    f"clone ledger {clone_ledger} line {lineno} (milestone_id="
                    f"{ev.get('milestone_id')!r}) failed schema validation on "
                    f"{len(errors)} field(s): " + "; ".join(errors),
                    ev,
                )
            eid = ev["event_id"]  # validate_event guaranteed present
            if eid in seen_ids:
                # Idempotency — dedupe silently by event_id. This is the
                # two-key equality mentioned in the contract.
                continue

            mid = ev.get("milestone_id")
            ts = ev.get("ts", "")
            prev = last_candidate_ts.get(mid)
            if prev is not None:
                prev_ts, prev_path, prev_line = prev
                if ts < prev_ts:
                    raise LedgerConcatError(
                        f"per-milestone ts monotonicity violation: "
                        f"milestone_id={mid!r} — earlier row at "
                        f"{prev_path} line {prev_line} has ts={prev_ts!r} "
                        f"but later row at {clone_ledger} line {lineno} has "
                        f"ts={ts!r} (ts_earlier={prev_ts!r} > ts_later={ts!r}); "
                        f"clones must emit per-milestone events in "
                        f"file-order-monotonic ts (cycle-11 drift pattern)",
                        ev,
                    )
            last_candidate_ts[mid] = (ts, clone_ledger, lineno)

            seen_ids.add(eid)
            new_events.append(ev)

    if not new_events:
        return 0

    # Global sort: primary key ts, tiebreak content_hash. Milestone grouping
    # is preserved implicitly — within any milestone, the sort still yields
    # (ts, hash) order. Global ts-then-milestone order matches the previous
    # public behavior on non-colliding ts.
    new_events.sort(key=lambda e: (e.get("ts", ""), content_hash_tiebreak(e)))

    # Atomic write: read existing main, splice new lines, write to temp,
    # os.replace onto main. Guarantees that a validation failure above
    # leaves the main ledger byte-identical to its pre-call state.
    existing = ""
    if main_ledger.exists():
        existing = main_ledger.read_text()
        if existing and not existing.endswith("\n"):
            existing += "\n"
    body = existing + "".join(
        json.dumps(ev, ensure_ascii=False, separators=(",", ":")) + "\n"
        for ev in new_events
    )
    tmp = main_ledger.with_suffix(main_ledger.suffix + ".concat.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        os.write(fd, body.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, main_ledger)
    return len(new_events)


def emit_run_start_event(workspace: Path, run_id: str, directive: str) -> str:
    """Append the canonical bootstrap event. Returns the event_id."""
    eid = str(uuid.uuid4())
    event = {
        "event_id": eid,
        "ts": _now_iso(),
        "run_id": run_id,
        "cycle": 1,
        "agent": "researcher",
        "milestone_id": "_run/start",
        "status": "in-progress",
        "confidence": {
            "level": "high",
            "rationale": "run boot — directive recorded, plan-of-record drafted",
            "assessor": "researcher",
        },
        "narrative": (directive or "").strip().splitlines()[0][:240] or "run started",
        "artifacts": ["plan_of_record.md", "STRUCTURE.md"],
    }
    append_ledger_event(workspace, event)
    return eid


def bootstrap_workspace(
    workspace: Path,
    directive: str,
    run_id: str,
    cycle: int,
) -> dict:
    """Run cycle-1 bootstrap if applicable. Returns a small status dict.

    No-op on resume (cycle > 1 or plan_of_record.md already exists).
    """
    status = {
        "ran": False,
        "folders_created": [],
        "wrote_plan": False,
        "wrote_structure": False,
        "ledger_event_id": None,
    }
    if not is_fresh_start(workspace, cycle):
        return status

    status["folders_created"] = ensure_skeleton(workspace)

    plan_path = workspace / "plan_of_record.md"
    if not plan_path.exists():
        write_plan_of_record(workspace, directive, run_id)
        status["wrote_plan"] = True

    struct_path = workspace / "STRUCTURE.md"
    if not struct_path.exists():
        write_structure_md(workspace, run_id)
        status["wrote_structure"] = True

    if not (workspace / "promise_ledger.jsonl").exists():
        status["ledger_event_id"] = emit_run_start_event(workspace, run_id, directive)

    status["ran"] = True
    return status


# ---------------------------------------------------------------------------
# Ledger summary for cycle-input injection
# ---------------------------------------------------------------------------


def _read_ledger(ledger_path: Path) -> list[dict]:
    """Tolerant JSONL reader. Skips malformed lines silently — promise_check
    is responsible for surfacing parse errors; this reader must not crash
    the cycle loop."""
    if not ledger_path.exists():
        return []
    events: list[dict] = []
    for raw in ledger_path.read_text().splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
            if isinstance(ev, dict):
                events.append(ev)
        except json.JSONDecodeError:
            continue
    return events


def summarize_ledger(workspace: Path, max_chars: int = 32_000) -> str:
    """Produce a token-bounded summary of the ledger for cycle-input injection.

    Strategy (per plan §5):
      - For each unique milestone_id, emit the most recent event.
      - Always include any in-progress events, regardless of recency.
      - Always include validated/superseded events with low or provisional
        confidence (these are the items that need re-verification).
      - Truncate at max_chars (~8K tokens at ~4 chars/token).

    Returns a single string ready to inject as `promise_ledger_summary`.
    """
    ledger_path = workspace / "promise_ledger.jsonl"
    events = _read_ledger(ledger_path)
    if not events:
        return "[promise_ledger.jsonl is empty or absent]"

    # Group by milestone, sort each group by ts.
    by_mid: dict[str, list[dict]] = {}
    for ev in events:
        by_mid.setdefault(ev.get("milestone_id") or "_unknown", []).append(ev)
    for evs in by_mid.values():
        evs.sort(key=lambda e: e.get("ts", ""))

    selected: list[dict] = []
    seen_event_ids: set[str] = set()

    for mid, evs in by_mid.items():
        latest = evs[-1]
        if latest.get("event_id") and latest["event_id"] not in seen_event_ids:
            selected.append(latest)
            seen_event_ids.add(latest["event_id"])

    # In-progress backfill + low-confidence validated/superseded backfill.
    for ev in events:
        eid = ev.get("event_id")
        if not eid or eid in seen_event_ids:
            continue
        status = ev.get("status")
        level = (ev.get("confidence") or {}).get("level")
        if status == "in-progress":
            selected.append(ev)
            seen_event_ids.add(eid)
        elif status in ("validated", "superseded") and level in ("low", "provisional"):
            selected.append(ev)
            seen_event_ids.add(eid)

    # Sort the final set chronologically.
    selected.sort(key=lambda e: (e.get("ts", ""), e.get("milestone_id", "")))

    lines: list[str] = []
    lines.append("# Promise Ledger Summary")
    lines.append(
        f"Total events: {len(events)}, distinct milestones: {len(by_mid)}, "
        f"shown: {len(selected)} (latest-per-milestone + in-progress + low-confidence)"
    )
    lines.append("")
    for ev in selected:
        mid = ev.get("milestone_id", "?")
        status = ev.get("status", "?")
        conf = ev.get("confidence") or {}
        if not isinstance(conf, dict):
            conf = {}
        level = conf.get("level", "?")
        cycle = ev.get("cycle", "?")
        agent = ev.get("agent", "?")
        ts = ev.get("ts", "")
        narrative = (ev.get("narrative") or "").strip().replace("\n", " ")
        if len(narrative) > 200:
            narrative = narrative[:197] + "..."
        artifacts = ev.get("artifacts") or []
        art_str = f" artifacts={len(artifacts)}" if artifacts else ""
        lines.append(
            f"- [{mid}] {status}/{level} (cycle {cycle}, {agent}, {ts}){art_str}"
        )
        if narrative:
            lines.append(f"    {narrative}")

    text = "\n".join(lines)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n... [truncated; full ledger at promise_ledger.jsonl]"
    return text


def derive_run_id(state_dir: Path | None = None) -> str:
    """A simple run_id: ISO timestamp of the run's first cycle."""
    return f"run-{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H%M%SZ')}"
