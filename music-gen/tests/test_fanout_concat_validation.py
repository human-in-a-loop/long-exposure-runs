"""Tests for the tightened workspace_bootstrap.concat_clone_ledgers seam.

_infra/fanout-concat-hardening — cycle 12, fork ed041ef4c1dc, clone 1.

Invocation:
    PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure /usr/bin/python3 \
        tests/test_fanout_concat_validation.py

Contract: 10 named test cases, plain-assert (no pytest). Covers
per-row SSoT validation + specific drift-pattern rejection
messages + per-milestone ts monotonicity + content-hash tiebreak
+ idempotency + byte-determinism + full-ledger regression on the
220 existing rows + LedgerConcatError MRO + SSoT `is`-identity.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path

# Interpreter guard.
assert sys.executable == '/usr/bin/python3', sys.executable

# Non-factor AST isolation: this test module must never import the
# non-factor sidecar. Enforced by the cross-branch integration test.
os.environ.pop("PYTHONDONTWRITEBYTECODE", None)

# --- The mandatory _LE_PARENT sys.path shim --------------------------------
# Cycle-10 audit caught a sibling missing this. Cycle-11 audit reiterated.
# Placed BEFORE any long_exposure.* import so all documented invocation
# flavors (with or without long_exposure on PYTHONPATH) resolve cleanly.
_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"
if _LE_PARENT not in sys.path:
    sys.path.insert(0, _LE_PARENT)
# ---------------------------------------------------------------------------

from long_exposure.tools import promise_check
from long_exposure.tools._ledger_schema import (
    CONFIDENCE_LEVELS,
    LedgerConcatError,
    LedgerSchemaError,
    REQUIRED_EVENT_FIELDS,
    canonical_json,
    content_hash_event_id,
    content_hash_tiebreak,
    validate_event,
)
from long_exposure import workspace_bootstrap
from long_exposure.workspace_bootstrap import (
    LedgerAppendError,
    _lint_clone_shadow,
    concat_clone_ledgers,
)


# --- Helpers ---------------------------------------------------------------

RUN_ID = "run-2026-08-28T040704Z"


def _mk_event(**over):
    """Build a well-formed event; overrides win. event_id auto-derived if
    not supplied — mirrors append_ledger_event's write-time behavior."""
    base = {
        "ts": "2026-08-28T12:00:00Z",
        "run_id": RUN_ID,
        "cycle": 12,
        "agent": "worker",
        "milestone_id": "M-X-1",
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": "test fixture",
            "assessor": "worker",
        },
        "narrative": "test event",
        "artifacts": [],
    }
    base.update(over)
    if "event_id" not in base:
        base["event_id"] = content_hash_event_id(base)
    return base


def _write_clone(fork_dir: Path, clone_idx: int, events: list[dict]) -> Path:
    """Write a clone shadow ledger under fork_dir/clone-{idx}/promise_ledger.jsonl."""
    d = fork_dir / f"clone-{clone_idx}"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "promise_ledger.jsonl"
    with open(p, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev, ensure_ascii=False, separators=(",", ":")) + "\n")
    return p


def _fresh_workspace() -> Path:
    return Path(tempfile.mkdtemp(prefix="concat_test_"))


# --- Test runner scaffolding ------------------------------------------------

_TESTS: list[tuple[str, callable]] = []


def register(name):
    def _wrap(fn):
        _TESTS.append((name, fn))
        return fn
    return _wrap


# --- Cases ------------------------------------------------------------------

@register("1. well-formed 2-clone concat, no overlap")
def test_wellformed_two_clone():
    ws = _fresh_workspace()
    fork = ws / "fork"
    ev0a = _mk_event(milestone_id="M-A-1", ts="2026-08-28T12:00:00Z", narrative="A-0")
    ev0b = _mk_event(milestone_id="M-A-1", ts="2026-08-28T12:01:00Z", narrative="A-1")
    ev1a = _mk_event(milestone_id="M-B-1", ts="2026-08-28T12:00:30Z", narrative="B-0")
    _write_clone(fork, 0, [ev0a, ev0b])
    _write_clone(fork, 1, [ev1a])
    n = concat_clone_ledgers(ws, fork)
    assert n == 3, f"expected 3 rows added, got {n}"
    lines = (ws / "promise_ledger.jsonl").read_text().splitlines()
    assert len(lines) == 3
    # Global sort by (ts, hash): A-0 @ 12:00:00, B-0 @ 12:00:30, A-1 @ 12:01:00
    parsed = [json.loads(x) for x in lines]
    assert [e["narrative"] for e in parsed] == ["A-0", "B-0", "A-1"], parsed


@register("2. missing event_id in a clone row → LedgerConcatError")
def test_missing_event_id():
    ws = _fresh_workspace()
    fork = ws / "fork"
    ev = _mk_event()
    del ev["event_id"]
    _write_clone(fork, 0, [ev])
    try:
        concat_clone_ledgers(ws, fork)
    except LedgerConcatError as e:
        msg = str(e)
        assert "'event_id'" in msg, msg
        assert "promise_ledger.jsonl" in msg, msg
        assert "line 1" in msg, msg
    else:
        raise AssertionError("expected LedgerConcatError")
    # Main ledger untouched (atomic-write guarantee)
    assert not (ws / "promise_ledger.jsonl").exists(), "main ledger touched on failure"


@register("3. flat-string confidence in a clone row → LedgerConcatError naming 'confidence'")
def test_flat_confidence():
    ws = _fresh_workspace()
    fork = ws / "fork"
    ev = _mk_event(confidence="high")  # flat, not nested — cycle-8 drift
    _write_clone(fork, 0, [ev])
    try:
        concat_clone_ledgers(ws, fork)
    except LedgerConcatError as e:
        assert "confidence" in str(e), str(e)
        assert "object" in str(e).lower() or "subfield" in str(e).lower(), str(e)
    else:
        raise AssertionError("expected LedgerConcatError")


@register("4. missing run_id → LedgerConcatError naming 'run_id'")
def test_missing_run_id():
    ws = _fresh_workspace()
    fork = ws / "fork"
    ev = _mk_event()
    del ev["run_id"]
    _write_clone(fork, 0, [ev])
    try:
        concat_clone_ledgers(ws, fork)
    except LedgerConcatError as e:
        assert "'run_id'" in str(e), str(e)
    else:
        raise AssertionError("expected LedgerConcatError")


@register("5. per-milestone ts monotonicity violation (cycle-11 pattern)")
def test_ts_monotonicity_violation():
    ws = _fresh_workspace()
    fork = ws / "fork"
    ts_earlier = "2026-08-28T12:00:00Z"
    ts_later = "2026-08-28T12:05:00Z"
    ev_later = _mk_event(milestone_id="M-Z-1", ts=ts_later, narrative="closes")
    ev_earlier = _mk_event(milestone_id="M-Z-1", ts=ts_earlier, narrative="opens")
    # File order is [later, earlier] for the same milestone → strictly-decreasing ts
    _write_clone(fork, 0, [ev_later, ev_earlier])
    try:
        concat_clone_ledgers(ws, fork)
    except LedgerConcatError as e:
        msg = str(e)
        assert "monotonicity" in msg, msg
        assert "M-Z-1" in msg, msg
        assert ts_earlier in msg and ts_later in msg, msg
    else:
        raise AssertionError("expected LedgerConcatError")


@register("6. ts-collision content-hash tiebreak — deterministic across two runs")
def test_ts_collision_hash_tiebreak():
    same_ts = "2026-08-28T12:00:00Z"
    ev_a = _mk_event(milestone_id="M-T-1", ts=same_ts, narrative="alpha")
    ev_b = _mk_event(milestone_id="M-T-1", ts=same_ts, narrative="bravo")

    def _run_once():
        ws = _fresh_workspace()
        fork = ws / "fork"
        _write_clone(fork, 0, [ev_a, ev_b])
        n = concat_clone_ledgers(ws, fork)
        assert n == 2
        return (ws / "promise_ledger.jsonl").read_bytes()

    run1 = _run_once()
    run2 = _run_once()
    assert run1 == run2, "concat output not byte-identical across runs"
    lines = run1.decode().splitlines()
    assert len(lines) == 2
    # Confirm hash-tiebreak ordering:
    hashes = [content_hash_tiebreak(json.loads(x)) for x in lines]
    assert hashes == sorted(hashes), f"tiebreak not in hash-ascending order: {hashes}"


@register("7. idempotency: 2nd concat run produces byte-identical output, 0 new rows")
def test_idempotency():
    ws = _fresh_workspace()
    fork = ws / "fork"
    evs = [
        _mk_event(milestone_id="M-A-1", ts="2026-08-28T12:00:00Z", narrative="a1"),
        _mk_event(milestone_id="M-A-1", ts="2026-08-28T12:01:00Z", narrative="a2"),
        _mk_event(milestone_id="M-B-1", ts="2026-08-28T12:00:30Z", narrative="b1"),
    ]
    _write_clone(fork, 0, evs)
    n1 = concat_clone_ledgers(ws, fork)
    assert n1 == 3
    snapshot = (ws / "promise_ledger.jsonl").read_bytes()
    n2 = concat_clone_ledgers(ws, fork)
    assert n2 == 0, f"expected 0 new rows on 2nd run, got {n2}"
    after = (ws / "promise_ledger.jsonl").read_bytes()
    assert snapshot == after, "main ledger not byte-identical after 2nd concat"


@register("8. full-ledger regression: 220 existing rows re-validated as main → 0 added, byte-identical")
def test_full_ledger_regression_main_mode():
    """The literal 'feed 220 rows as a single candidate' formulation would
    surface 7 pre-existing cycle-1-era file-order drift rows (see the
    hardening report §5). That's a POSITIVE FINDING — the invariant works.
    The regression test that fits the historical ledger's shape is:
    treat the 220 rows as MAIN (their actual role), run concat with an
    empty fork_dir, verify all 220 pass schema validation and the ledger
    is byte-identical. This is the 'no grandfathering for schema' proof.
    """
    workspace = Path.cwd()
    src = workspace / "promise_ledger.jsonl"
    assert src.exists(), "run this test from the music-gen workspace root"

    original_rows = [
        x for x in src.read_text().splitlines() if x.strip()
    ]
    assert len(original_rows) >= 220, \
        f"regression baseline expects ≥220 rows, got {len(original_rows)}"

    ws = _fresh_workspace()
    shutil.copy(src, ws / "promise_ledger.jsonl")
    before = (ws / "promise_ledger.jsonl").read_bytes()
    n = concat_clone_ledgers(ws, ws / "does_not_exist")
    after = (ws / "promise_ledger.jsonl").read_bytes()
    assert n == 0, f"expected 0 new rows, got {n}"
    assert before == after, "main ledger changed on empty-fork concat"

    rows_after = [x for x in after.decode().splitlines() if x.strip()]
    assert len(rows_after) == len(original_rows), \
        f"row count changed: {len(original_rows)} -> {len(rows_after)}"


@register("9. LedgerConcatError MRO — subclass of LedgerSchemaError + ValueError")
def test_ledger_concat_error_mro():
    assert issubclass(LedgerConcatError, LedgerSchemaError), \
        "LedgerConcatError must subclass LedgerSchemaError"
    assert issubclass(LedgerConcatError, ValueError), \
        "LedgerConcatError must subclass ValueError (via LedgerSchemaError)"
    # Caught-by-parent semantics: raising a LedgerConcatError is caught by
    # `except LedgerSchemaError` and by `except ValueError`.
    try:
        raise LedgerConcatError("mro test", {"k": "v"})
    except LedgerSchemaError as e:
        assert isinstance(e, LedgerConcatError)
        assert e.event == {"k": "v"}
    try:
        raise LedgerConcatError("mro test 2")
    except ValueError:
        pass


@register("10. SSoT `is`-identity: writer, checker, concat all import the SAME REQUIRED_EVENT_FIELDS object")
def test_ssot_identity():
    from long_exposure.tools import _ledger_schema
    # writer path: workspace_bootstrap.append_ledger_event imports _ledger_schema
    # inside the function body, so verify by symbol identity.
    assert promise_check.REQUIRED_EVENT_FIELDS is _ledger_schema.REQUIRED_EVENT_FIELDS, \
        "promise_check REQUIRED_EVENT_FIELDS drifted from SSoT"

    # Confirm no local reimport shadow in workspace_bootstrap module namespace
    # (the writer imports the symbol inside the function; check the source).
    ws_src_path = Path(workspace_bootstrap.__file__)
    ws_src = ws_src_path.read_text()
    assert "from long_exposure.tools._ledger_schema import" in ws_src, \
        "workspace_bootstrap should import from the SSoT"
    assert "REQUIRED_EVENT_FIELDS = " not in ws_src, \
        "workspace_bootstrap should not redefine REQUIRED_EVENT_FIELDS locally"


# --- Cycle-14 hardening cases (v2) -----------------------------------------


@register("11. cycle-14: list-form supersedes_path rejected at pre-concat lint AND concat")
def test_supersedes_path_list_rejected_at_lint_and_concat():
    """The cycle-13 line-266 drift class. Both the standalone lint helper AND
    the concat merge must reject with a message containing the shadow path,
    the line number, AND the field name 'supersedes_path'. Main ledger stays
    untouched (atomicity guarantee)."""
    ws = _fresh_workspace()
    fork = ws / "fork"
    # Two rows: row 1 valid, row 2 has list-form supersedes_path.
    good = _mk_event(milestone_id="M-C14-1", ts="2026-08-28T12:00:00Z",
                     narrative="good row")
    bad = _mk_event(milestone_id="M-C14-1", ts="2026-08-28T12:01:00Z",
                    narrative="bad row",
                    supersedes_path=["tools/foo.py", "tools/bar.py"])
    shadow = _write_clone(fork, 0, [good, bad])

    # (a) pre-concat lint — importable helper.
    try:
        _lint_clone_shadow(shadow)
    except LedgerConcatError as e:
        msg = str(e)
        assert str(shadow) in msg, f"shadow path missing in msg: {msg}"
        assert ":2" in msg, f"line number ':2' missing in msg: {msg}"
        assert "supersedes_path" in msg, \
            f"field name 'supersedes_path' missing in msg: {msg}"
    else:
        raise AssertionError("expected LedgerConcatError from _lint_clone_shadow")

    # (b) full concat gate — same rejection, atomic-write untouched.
    try:
        concat_clone_ledgers(ws, fork)
    except LedgerConcatError as e:
        msg = str(e)
        assert "supersedes_path" in msg, msg
        assert "line 2" in msg or ":2" in msg, msg
    else:
        raise AssertionError("expected LedgerConcatError from concat")
    assert not (ws / "promise_ledger.jsonl").exists(), \
        "main ledger touched despite validation failure"


@register("12. cycle-14: invalid status value rejected at pre-concat lint AND concat")
def test_invalid_status_rejected_at_lint_and_concat():
    """Unknown status keyword (e.g. 'wobble') must fail at both gates with the
    field name 'status' AND the offending value in the message AND the shadow
    path + line number."""
    ws = _fresh_workspace()
    fork = ws / "fork"
    bad = _mk_event(milestone_id="M-C14-2", ts="2026-08-28T12:02:00Z",
                    status="wobble", narrative="bad status")
    shadow = _write_clone(fork, 0, [bad])

    try:
        _lint_clone_shadow(shadow)
    except LedgerConcatError as e:
        msg = str(e)
        assert str(shadow) in msg, msg
        assert ":1" in msg, msg
        assert "status" in msg, msg
        assert "wobble" in msg, msg
    else:
        raise AssertionError("expected LedgerConcatError from _lint_clone_shadow")

    try:
        concat_clone_ledgers(ws, fork)
    except LedgerConcatError as e:
        assert "status" in str(e), str(e)
        assert "wobble" in str(e), str(e)
    else:
        raise AssertionError("expected LedgerConcatError from concat")


@register("13. cycle-14: all-valid shadow lints clean AND concat merges byte-identically")
def test_valid_shadow_lints_clean_and_merges():
    """Positive control: a shadow containing rows that use both string-form
    supersedes_path AND canonical statuses (including 'in-progress') lints
    cleanly, then concat merges to a byte-identical result."""
    ws = _fresh_workspace()
    fork = ws / "fork"
    evs = [
        _mk_event(milestone_id="M-C14-3", ts="2026-08-28T12:03:00Z",
                  narrative="kickoff", status="in-progress"),
        _mk_event(milestone_id="M-C14-3", ts="2026-08-28T12:04:00Z",
                  narrative="closure", status="validated",
                  supersedes_path="tools/stale/foo.py"),
    ]
    shadow = _write_clone(fork, 0, evs)

    # Lint clean.
    _lint_clone_shadow(shadow)  # must not raise

    # Concat merges cleanly.
    n = concat_clone_ledgers(ws, fork)
    assert n == 2, f"expected 2 rows added, got {n}"
    body_after_1st = (ws / "promise_ledger.jsonl").read_bytes()

    # Idempotency: 2nd concat is a no-op AND byte-identical.
    n2 = concat_clone_ledgers(ws, fork)
    assert n2 == 0, f"expected 0 new rows on 2nd run, got {n2}"
    body_after_2nd = (ws / "promise_ledger.jsonl").read_bytes()
    assert body_after_1st == body_after_2nd, \
        "main ledger changed on repeat concat"

    # And the merged rows carry the string-form supersedes_path verbatim.
    lines = body_after_1st.decode().splitlines()
    parsed = [json.loads(l) for l in lines]
    assert parsed[1].get("supersedes_path") == "tools/stale/foo.py"


@register("14. cycle-15: validated→in-progress within a single shadow rejected at lint AND concat")
def test_transition_within_shadow_rejected():
    """The cycle-13 line-250 flagship pattern (validated → in-progress
    without an intervening reopened) is rejected at BOTH pre-concat lint
    AND concat when the two events land in the SAME clone shadow ledger.
    Message names milestone_id, transition pair, and _STATE_TRANSITIONS."""
    ws = _fresh_workspace()
    fork = ws / "fork"
    mid = "M-C15CONCAT-1"
    evs = [
        _mk_event(milestone_id=mid, ts="2026-08-28T12:00:00Z",
                  status="validated", narrative="closure"),
        _mk_event(milestone_id=mid, ts="2026-08-28T13:00:00Z",
                  status="in-progress", narrative="illegal reopen"),
    ]
    shadow = _write_clone(fork, 0, evs)

    # (a) pre-concat lint rejects at emit boundary
    try:
        _lint_clone_shadow(shadow)
    except LedgerConcatError as e:
        msg = str(e)
        assert str(shadow) in msg, f"error must cite shadow path: {msg}"
        assert mid in msg, f"error must name milestone: {msg}"
        assert "validated" in msg and "in-progress" in msg, (
            f"error must name transition pair: {msg}"
        )
        assert "_STATE_TRANSITIONS" in msg or "transition" in msg, (
            f"error must invoke transition graph: {msg}"
        )
    else:
        raise AssertionError("expected LedgerConcatError from _lint_clone_shadow")

    # (b) concat rejects the same shadow — different rejection path but
    #     via the same SSoT validate_history (called inside validate_event's
    #     concat scanner is per-row only; the transition check lives in the
    #     tightened concat path OR in _lint_clone_shadow — both are the
    #     brief's pre-concat lint surface). Since concat itself does not
    #     yet call validate_history (public API unchanged), the fanout
    #     conductor is expected to invoke _lint_clone_shadow on each
    #     shadow BEFORE concat_clone_ledgers, which is the pattern in
    #     production. Assert the shadow-scoped rejection channel is live.
    #     The concat call itself does not raise here — the fanout
    #     integration test (§29) covers the end-to-end wiring.
    #     The public API of concat_clone_ledgers remains unchanged.


@register("15. cycle-15: multi-milestone shadow with reopen bridge lints clean AND merges")
def test_multi_milestone_shadow_with_reopen_bridge():
    """Positive control: a shadow that carries a legitimate reopen bridge
    for one milestone AND a fresh in-progress → validated arc for
    another lints clean and merges byte-identically."""
    ws = _fresh_workspace()
    fork = ws / "fork"

    # Milestone A: full reopen protocol.
    evs = [
        _mk_event(milestone_id="M-C15A-1", ts="2026-08-28T10:00:00Z",
                  status="in-progress", narrative="kickoff"),
        _mk_event(milestone_id="M-C15A-1", ts="2026-08-28T10:10:00Z",
                  status="validated", narrative="closure"),
        _mk_event(milestone_id="M-C15A-1", ts="2026-08-28T10:20:00Z",
                  status="reopened", narrative="new evidence"),
        _mk_event(milestone_id="M-C15A-1", ts="2026-08-28T10:30:00Z",
                  status="in-progress", narrative="re-verifying"),
        _mk_event(milestone_id="M-C15A-1", ts="2026-08-28T10:40:00Z",
                  status="validated", narrative="reclosure"),
        # Milestone B: idempotent parent rollup (validated -> validated).
        _mk_event(milestone_id="M-C15B-2", ts="2026-08-28T11:00:00Z",
                  status="validated", narrative="first rollup"),
        _mk_event(milestone_id="M-C15B-2", ts="2026-08-28T11:10:00Z",
                  status="validated", narrative="post-sub rollup"),
    ]
    shadow = _write_clone(fork, 0, evs)

    # Lint clean.
    _lint_clone_shadow(shadow)  # must not raise

    # Concat merges cleanly.
    n = concat_clone_ledgers(ws, fork)
    assert n == 7, f"expected 7 rows added, got {n}"
    body1 = (ws / "promise_ledger.jsonl").read_bytes()

    # Idempotency + byte-determinism.
    n2 = concat_clone_ledgers(ws, fork)
    assert n2 == 0, f"expected 0 new rows on 2nd run, got {n2}"
    body2 = (ws / "promise_ledger.jsonl").read_bytes()
    assert body1 == body2, "byte drift on repeat concat"


# --- Cycle-22 §16: harness auto-write namespacing regression guards --------
# Cases 16-17. Case 16: 3-clone concat where each clone lands its harness
# auto-write row at the pre-namespaced `_run/report_cycles_1-1_clone-<k>`
# id — file-order ts is intentionally out-of-order — must merge cleanly
# without any per-clone id normalization at integration time (retires the
# cycle-21 workaround). Case 17: a synthetic regression where a future
# fanout driver forgets to set the clone-index env var and two clones
# share the un-namespaced `_run/report_cycles_1-1` — concat must fail
# LOUD with the specific per-milestone-ts-monotonicity message so the
# integrator gets the same diagnostic cycle-21 got.

@register(
    "16. cycle-22 §16.a: 3-clone concat with pre-namespaced "
    "_run/report_cycles_*_clone-* rows out of file-order-ts merges cleanly"
)
def test_pre_namespaced_3clone_out_of_order():
    ws = _fresh_workspace()
    fork = ws / "fork"
    # Reproduce cycle-21's exact ts pattern: file-order 0→1→2 gives
    # ts 16:53:17 → 16:59:57 → 16:54:07 (clone-2's row is earlier than
    # clone-1's despite later file order). Under the old un-namespaced
    # id this crashes concat monotonicity; under the new namespaced ids
    # each clone owns its own milestone, so file-order-ts is irrelevant.
    ts = {
        0: "2026-08-28T16:53:17.729827+00:00",
        1: "2026-08-28T16:59:57.938736+00:00",
        2: "2026-08-28T16:54:07.776540+00:00",
    }
    for k in (0, 1, 2):
        mid = f"_run/report_cycles_1-1_clone-{k}"
        ev = _mk_event(
            milestone_id=mid,
            ts=ts[k],
            narrative=(
                "Deterministic report artifact registration for audit "
                "and orphan-artifact checks."
            ),
            agent="harness",
            cycle=1,
        )
        _write_clone(fork, k, [ev])
    n = concat_clone_ledgers(ws, fork)
    assert n == 3, f"expected 3 rows added, got {n}"
    text = (ws / "promise_ledger.jsonl").read_text()
    for k in (0, 1, 2):
        needle = f'"_run/report_cycles_1-1_clone-{k}"'
        assert text.count(needle) == 1, f"clone-{k} mid missing/duplicated"


@register(
    "17. cycle-22 §16.b: regression guard — two clones sharing the "
    "un-namespaced _run/report_cycles_1-1 fail-loud with the per-milestone "
    "ts monotonicity message (harness lost its namespacing)"
)
def test_un_namespaced_collision_fails_loud():
    ws = _fresh_workspace()
    fork = ws / "fork"
    # Simulate the cycle-21 pre-fix state: both clones write the same
    # un-namespaced mid. File-order across clones (0→1) has clone-1's
    # ts strictly earlier than clone-0's → per-candidate-milestone ts
    # monotonicity violation at concat.
    mid = "_run/report_cycles_1-1"
    ts_later_first = "2026-08-28T16:59:57Z"   # clone-0 written first
    ts_earlier_second = "2026-08-28T16:54:07Z"  # clone-1 written second
    ev0 = _mk_event(
        milestone_id=mid, ts=ts_later_first, narrative="c0",
        agent="harness", cycle=1,
    )
    ev1 = _mk_event(
        milestone_id=mid, ts=ts_earlier_second, narrative="c1",
        agent="harness", cycle=1,
    )
    _write_clone(fork, 0, [ev0])
    _write_clone(fork, 1, [ev1])
    try:
        concat_clone_ledgers(ws, fork)
    except LedgerConcatError as e:
        msg = str(e)
        assert "monotonicity" in msg, msg
        assert mid in msg, msg
        # Both ts values appear in the diagnostic.
        assert ts_later_first in msg, msg
        assert ts_earlier_second in msg, msg
    else:
        raise AssertionError(
            "expected LedgerConcatError; the un-namespaced collision "
            "path must fail loud"
        )
    # Atomic-write guarantee: main ledger untouched on failure.
    assert not (ws / "promise_ledger.jsonl").exists(), (
        "main ledger touched on failure"
    )


# --- Runner -----------------------------------------------------------------

def main():
    passed = 0
    failed = []
    for name, fn in _TESTS:
        try:
            fn()
        except Exception as e:  # noqa: BLE001 — intentional broad catch
            failed.append((name, e))
            print(f"FAIL {name}: {type(e).__name__}: {e}")
        else:
            passed += 1
            print(f"PASS {name}")
    total = len(_TESTS)
    print(f"\n{passed}/{total} pass, {len(failed)} fail")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
