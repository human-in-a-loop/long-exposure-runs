"""Tests for the harness auto-write per-clone milestone_id namespacing fix.

_infra/harness-auto-write-namespacing — cycle 22, fork cc548ca0c2e5, clone 0.

Root cause (cycle-21 handoff #1): the harness's periodic-report artifact-
registration event unconditionally emits `milestone_id` at
`_run/report_cycles_<lo>-<hi>`. In fan-out with 2+ clones every clone lands
that same id in its shadow ledger; `concat_clone_ledgers` then rejects the
merge on per-candidate-milestone file-order ts monotonicity when the sibling
clones' emit-times cross the file-order boundary. Cycle-21 fixed it via
per-clone id normalization at integration time; this cycle pushes the fix
upstream so no future 2+-clone merge needs the workaround.

Fix: `long_exposure.fanout.report_cycles_milestone_id(lo, hi)` returns
`_run/report_cycles_<lo>-<hi>` for a root-cycle invocation and
`_run/report_cycles_<lo>-<hi>_clone-<k>` for a fan-out clone. Also, the
harness write-site (`long_exposure.exploration._append_report_artifact_event`)
drops its manual `uuid.uuid4()` event_id so `append_ledger_event` auto-
derives a UUID5 content-hash event_id — under the namespaced id, siblings
cannot collide on event_id even when they happen to agree on ts and payload.

Invocation:
    PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure /usr/bin/python3 \\
        tests/test_harness_report_namespacing.py

Contract: 6 named test cases, plain-assert (no pytest).
"""
from __future__ import annotations

import ast
import copy
import json
import os
import sys
import tempfile
from pathlib import Path

# Interpreter guard.
assert sys.executable == '/usr/bin/python3', sys.executable

# Non-factor AST isolation: this test module must never import the
# non-factor sidecar. Enforced by the cross-branch integration test.
os.environ.pop("PYTHONDONTWRITEBYTECODE", None)

# --- The mandatory _LE_PARENT sys.path shim --------------------------------
_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"
if _LE_PARENT not in sys.path:
    sys.path.insert(0, _LE_PARENT)
# ---------------------------------------------------------------------------

from long_exposure import fanout
from long_exposure.fanout import (
    _get_clone_k,
    _is_clone,
    report_cycles_milestone_id,
)
from long_exposure.tools._ledger_schema import (
    LedgerConcatError,
    canonical_json,
    content_hash_event_id,
    validate_event,
)
from long_exposure import workspace_bootstrap
from long_exposure.workspace_bootstrap import (
    LedgerAppendError,
    _lint_clone_shadow,
    append_ledger_event,
    concat_clone_ledgers,
)


# --- Helpers ---------------------------------------------------------------

CYCLE21_SHADOW_BASE = Path(
    "/home/user/music-gen-instance/fork-392503ab7d47"
)
MAIN_LEDGER = Path(
    "/home/user/long-exposure-runs/music-gen/promise_ledger.jsonl"
)


class _CloneEnv:
    """Context manager that sets/clears AGENT_FORK_ID / AGENT_FORK_CLONE_K."""
    def __init__(self, fork_id: str | None, k: int | None):
        self.fork_id, self.k = fork_id, k
        self._saved: dict[str, str | None] = {}

    def __enter__(self):
        for name in ("AGENT_FORK_ID", "AGENT_FORK_CLONE_K"):
            self._saved[name] = os.environ.get(name)
        if self.fork_id is None:
            os.environ.pop("AGENT_FORK_ID", None)
        else:
            os.environ["AGENT_FORK_ID"] = self.fork_id
        if self.k is None:
            os.environ.pop("AGENT_FORK_CLONE_K", None)
        else:
            os.environ["AGENT_FORK_CLONE_K"] = str(self.k)
        return self

    def __exit__(self, *a):
        for name, val in self._saved.items():
            if val is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = val


def _fresh_workspace() -> Path:
    return Path(tempfile.mkdtemp(prefix="harness_ns_"))


def _write_clone(fork_dir: Path, k: int, events: list[dict]) -> Path:
    d = fork_dir / f"clone-{k}"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "promise_ledger.jsonl"
    with open(p, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(
                json.dumps(ev, ensure_ascii=False, separators=(",", ":"))
                + "\n"
            )
    return p


def _harness_event(
    lo: int, hi: int, ts: str, artifacts: list[str]
) -> dict:
    """Build the payload the harness write-site produces UNDER the fix.

    Milestone_id comes from `report_cycles_milestone_id` (namespace-aware).
    event_id is intentionally omitted so append_ledger_event auto-derives.
    """
    return {
        "ts": ts,
        "run_id": "run-unknown",
        "cycle": 1,
        "agent": "harness",
        "milestone_id": report_cycles_milestone_id(lo, hi),
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": "periodic report artifact written by the harness",
            "assessor": "harness",
        },
        "narrative": (
            "Deterministic report artifact registration for audit "
            "and orphan-artifact checks."
        ),
        "artifacts": artifacts,
        "reporter_mode": "periodic",
    }


# --- Test runner scaffolding ------------------------------------------------

_TESTS: list[tuple[str, callable]] = []


def register(name):
    def _wrap(fn):
        _TESTS.append((name, fn))
        return fn
    return _wrap


# --- Cases ------------------------------------------------------------------

@register("1. root invocation → un-suffixed milestone_id")
def test_root_no_suffix():
    with _CloneEnv(fork_id=None, k=None):
        assert not _is_clone()
        assert _get_clone_k() is None
        assert (
            report_cycles_milestone_id(1, 3) == "_run/report_cycles_1-3"
        )
        assert (
            report_cycles_milestone_id(4, 6) == "_run/report_cycles_4-6"
        )
        assert (
            report_cycles_milestone_id(20, 22)
            == "_run/report_cycles_20-22"
        )


@register("2. fanout clone k=0 → _clone-0 suffix")
def test_fanout_clone_zero():
    with _CloneEnv(fork_id="deadbeef", k=0):
        assert _is_clone()
        assert _get_clone_k() == 0
        mid = report_cycles_milestone_id(1, 1)
        assert mid == "_run/report_cycles_1-1_clone-0", mid


@register("3. three parallel clones → three distinct milestone_ids")
def test_three_clones_distinct():
    mids = set()
    for k in (0, 1, 2):
        with _CloneEnv(fork_id="deadbeef", k=k):
            mids.add(report_cycles_milestone_id(1, 1))
    expected = {
        "_run/report_cycles_1-1_clone-0",
        "_run/report_cycles_1-1_clone-1",
        "_run/report_cycles_1-1_clone-2",
    }
    assert mids == expected, mids


@register(
    "4. cycle-21 replay → three main-ledger rows byte-identical at "
    "(milestone_id, event_id, canonical_json-excluding-ts)"
)
def test_cycle21_replay_byte_identical():
    """Reconstruct the three cycle-21 shadow-ledger rows for the harness
    auto-write event, apply the fix's transformation (namespace mid, drop
    event_id, let UUID5 auto-derive), and verify each reproduced row
    matches the corresponding current main-ledger row at
    (milestone_id, event_id, canonical_json-excluding-ts).
    """
    # 1) Locate the three shadow rows.
    shadow_rows: dict[int, dict] = {}
    for k in (0, 1, 2):
        p = CYCLE21_SHADOW_BASE / f"clone-{k}" / "promise_ledger.jsonl"
        found = None
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                ev = json.loads(line)
                if ev.get("milestone_id") == "_run/report_cycles_1-1":
                    found = ev
                    break
        assert found is not None, f"no _run/report_cycles_1-1 in clone-{k}"
        shadow_rows[k] = found

    # 2) Locate the three main-ledger post-integration rows.
    main_rows: dict[int, dict] = {}
    with open(MAIN_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            ev = json.loads(line)
            mid = ev.get("milestone_id", "")
            for k in (0, 1, 2):
                if mid == f"_run/report_cycles_1-1_clone-{k}":
                    main_rows[k] = ev
    assert len(main_rows) == 3, list(main_rows)

    # 3) Apply the fix's transformation to each shadow row and check
    # byte-identity at (milestone_id, event_id, canonical_json-excl-ts).
    for k in (0, 1, 2):
        src = shadow_rows[k]
        transformed = copy.deepcopy(src)
        # a) namespace the mid (what report_cycles_milestone_id emits
        #    for this clone)
        with _CloneEnv(fork_id="392503ab7d47", k=k):
            transformed["milestone_id"] = report_cycles_milestone_id(1, 1)
        # b) drop the shadow event_id so UUID5 auto-derives from content
        #    (matches the cycle-21 driver pop-and-regenerate pattern)
        transformed.pop("event_id", None)
        # c) derive as append_ledger_event would
        derived_eid = content_hash_event_id(transformed)
        transformed["event_id"] = derived_eid

        got_mid = transformed["milestone_id"]
        got_eid = transformed["event_id"]
        want_mid = main_rows[k]["milestone_id"]
        want_eid = main_rows[k]["event_id"]
        assert got_mid == want_mid, f"clone-{k} mid: {got_mid!r} != {want_mid!r}"
        assert got_eid == want_eid, (
            f"clone-{k} event_id: {got_eid!r} != {want_eid!r}"
        )

        # canonical JSON excluding ts (ts is authoritatively the shadow ts,
        # written-through unchanged by cycle-21 driver)
        def _canon_no_ts(ev):
            copy_ = {k2: v for k2, v in ev.items() if k2 != "ts"}
            return canonical_json(copy_)

        got_canon = _canon_no_ts(transformed)
        want_canon = _canon_no_ts(main_rows[k])
        assert got_canon == want_canon, (
            f"clone-{k} canonical drift:\n  got={got_canon}\n want={want_canon}"
        )

        # ts is also equal (cycle-21 pass-through), so full byte-identity
        assert transformed["ts"] == main_rows[k]["ts"], (
            f"clone-{k} ts drift: {transformed['ts']!r} vs "
            f"{main_rows[k]['ts']!r}"
        )


@register("5. concat idempotence — pre-namespaced 3-clone shadows merge cleanly and re-run is a no-op")
def test_concat_idempotence_pre_namespaced():
    ws = _fresh_workspace()
    fork = ws / "fork"
    # Each clone writes a well-formed pre-namespaced harness event, plus a
    # non-report event so the shadow ledger is non-trivial.
    for k in (0, 1, 2):
        with _CloneEnv(fork_id="cafe", k=k):
            ev_report = _harness_event(
                lo=1, hi=1,
                ts=f"2026-08-28T18:0{k}:00Z",
                artifacts=[
                    f"reports/cycles/report_cycles_1-1_clone_{k}.md"
                ],
            )
        ev_report["event_id"] = content_hash_event_id(ev_report)
        # Non-report row for realism.
        ev_other = {
            "ts": f"2026-08-28T18:0{k}:30Z",
            "run_id": "run-unknown",
            "cycle": 1,
            "agent": "worker",
            "milestone_id": f"_infra/scratch-clone-{k}",
            "status": "validated",
            "confidence": {
                "level": "high",
                "rationale": "unit test filler",
                "assessor": "worker",
            },
            "narrative": "filler",
            "artifacts": [],
        }
        ev_other["event_id"] = content_hash_event_id(ev_other)
        _write_clone(fork, k, [ev_report, ev_other])

    # First concat.
    n1 = concat_clone_ledgers(ws, fork)
    body1 = (ws / "promise_ledger.jsonl").read_bytes()
    assert n1 == 6, f"expected 6 rows added, got {n1}"
    # Every namespaced report row present exactly once.
    text = body1.decode()
    for k in (0, 1, 2):
        needle = f'"_run/report_cycles_1-1_clone-{k}"'
        assert text.count(needle) == 1, f"clone-{k} mid missing/duplicated"

    # Re-run concat: idempotent (dedupe by event_id) → no new rows.
    n2 = concat_clone_ledgers(ws, fork)
    body2 = (ws / "promise_ledger.jsonl").read_bytes()
    assert n2 == 0, f"expected 0 new rows on rerun, got {n2}"
    assert body1 == body2, "byte drift on idempotent rerun"


@register("6. validator + shadow-lint accept the namespaced milestone_id unchanged")
def test_validator_acceptance():
    with _CloneEnv(fork_id="cafe", k=1):
        ev = _harness_event(
            lo=13, hi=15,
            ts="2026-08-28T19:00:00Z",
            artifacts=["reports/cycles/report_cycles_13-15_clone_1.md"],
        )
    ev["event_id"] = content_hash_event_id(ev)

    # Schema-level acceptance.
    errs = validate_event(ev)
    assert errs == [], f"validate_event should accept but got {errs}"

    # Writer-level acceptance (real append to a fresh workspace).
    # Force root-mode routing so `resolve_ledger_path` writes to the
    # workspace's own promise_ledger.jsonl, not to any per-clone shadow
    # implied by the ambient AGENT_FORK_ID env var.
    ws = _fresh_workspace()
    with _CloneEnv(fork_id=None, k=None):
        append_ledger_event(ws, dict(ev))
    written = (ws / "promise_ledger.jsonl").read_text().splitlines()
    assert len(written) == 1
    round_trip = json.loads(written[0])
    assert (
        round_trip["milestone_id"]
        == "_run/report_cycles_13-15_clone-1"
    )

    # Pre-concat lint acceptance.
    ws2 = _fresh_workspace()
    shadow = ws2 / "clone-1" / "promise_ledger.jsonl"
    shadow.parent.mkdir(parents=True, exist_ok=True)
    with open(shadow, "w", encoding="utf-8") as f:
        f.write(
            json.dumps(ev, ensure_ascii=False, separators=(",", ":"))
            + "\n"
        )
    _lint_clone_shadow(shadow)  # returns None on clean lint


# --- Bonus assertion: the write-site source itself no longer inlines
# `uuid.uuid4()` or the un-suffixed literal. This is a source-level guard
# against silent regression of the fix (the ast import above is used
# defensively; if either check fails the case fails fast).
@register(
    "7. write-site source drops `uuid.uuid4()` event_id AND routes mid "
    "through report_cycles_milestone_id"
)
def test_write_site_source_shape():
    src_path = Path(
        "/home/user/human-in-a-loop/long-exposure/long_exposure/exploration.py"
    )
    src = src_path.read_text(encoding="utf-8")
    # Find the write-site function.
    tree = ast.parse(src)
    fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and \
                node.name == "_append_report_artifact_event":
            fn = node
            break
    assert fn is not None, "write-site function not found"
    fn_src = ast.get_source_segment(src, fn)
    assert fn_src is not None
    assert "report_cycles_milestone_id(" in fn_src, (
        "write-site does not route through the SSoT helper"
    )
    # Anti-pattern check via AST (not string search — docstring may
    # legitimately mention `uuid.uuid4()`). Walk the function body
    # excluding the docstring node, and verify no Attribute Call to
    # `uuid.uuid4()` appears.
    body_nodes = list(fn.body)
    if (
        body_nodes
        and isinstance(body_nodes[0], ast.Expr)
        and isinstance(body_nodes[0].value, ast.Constant)
        and isinstance(body_nodes[0].value.value, str)
    ):
        body_nodes = body_nodes[1:]  # skip docstring
    for stmt in body_nodes:
        for node in ast.walk(stmt):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "uuid4"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "uuid"
            ):
                raise AssertionError(
                    "write-site still calls uuid.uuid4() — event_id "
                    "would not auto-derive via UUID5"
                )
    # Extra guardrail: the dict-literal that goes to append_ledger_event
    # must NOT hardcode a raw f-string for milestone_id — it must reference
    # a Name bound to the SSoT helper's result (or a Call to the helper
    # directly). This catches a regression where someone re-inlines the
    # f"_run/report_cycles_{lo}-{hi}" literal.
    for call in ast.walk(fn):
        if isinstance(call, ast.Call) and getattr(
            call.func, "id", None
        ) == "append_ledger_event":
            dict_arg = None
            if len(call.args) >= 2 and isinstance(call.args[1], ast.Dict):
                dict_arg = call.args[1]
            if dict_arg is None:
                continue
            for key_node, val_node in zip(dict_arg.keys, dict_arg.values):
                if isinstance(key_node, ast.Constant) and \
                        key_node.value == "milestone_id":
                    # Legal shapes:
                    #   (a) direct Call to report_cycles_milestone_id
                    #   (b) Name referencing a local bound to the helper
                    if isinstance(val_node, ast.Call):
                        assert (
                            getattr(val_node.func, "id", None)
                            == "report_cycles_milestone_id"
                        ), "milestone_id call must be the SSoT helper"
                    elif isinstance(val_node, ast.Name):
                        # Verify the local is assigned from the helper.
                        target = val_node.id
                        found_call = False
                        for stmt in body_nodes:
                            for asg in ast.walk(stmt):
                                if (
                                    isinstance(asg, ast.Assign)
                                    and any(
                                        isinstance(t, ast.Name)
                                        and t.id == target
                                        for t in asg.targets
                                    )
                                    and isinstance(asg.value, ast.Call)
                                    and getattr(
                                        asg.value.func, "id", None
                                    )
                                    == "report_cycles_milestone_id"
                                ):
                                    found_call = True
                        assert found_call, (
                            f"milestone_id name {target!r} must be assigned "
                            "from report_cycles_milestone_id(...)"
                        )
                    else:
                        raise AssertionError(
                            "milestone_id must be a Name or Call node, "
                            f"got {type(val_node).__name__}"
                        )


# --- Runner -----------------------------------------------------------------

def main():
    passed = 0
    failed = []
    for name, fn in _TESTS:
        try:
            fn()
        except Exception as e:  # noqa: BLE001
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
