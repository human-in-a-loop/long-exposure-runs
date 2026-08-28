---
created: 2026-08-28T17:57:00Z
cycle: 22
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _infra/harness-auto-write-namespacing
fork: cc548ca0c2e5
clone: 0
---

# Harness Report Namespacing — Upstream Fix (cycle-21 handoff #1)

## 1. Root-cause recap (cycle-21 handoff #1, verbatim)

> **Harness auto-write per-clone namespacing** — root cause is harness
> behaviour, not clone behaviour; namespace `_run/report_cycles_*` per
> clone at write time so future fork merges don't need this reconciliation.

Cycle-21 diagnosed that the harness's periodic-report artifact-registration
event unconditionally emits `milestone_id` at
`_run/report_cycles_<lo>-<hi>`. In a fan-out with 2+ clones, every clone
writes that same `milestone_id` into its shadow ledger. Cycle-21's
tightened `concat_clone_ledgers` (from `_infra/fanout-concat-hardening`)
enforces per-candidate-milestone file-order timestamp monotonicity, and
that check fires:

    LedgerConcatError: per-milestone ts monotonicity violation on
    milestone_id '_run/report_cycles_1-1' between clone-1 (ts
    2026-08-28T16:59:57Z, promise_ledger.jsonl line 7) and
    clone-2 (ts 2026-08-28T16:54:07Z, line 4)

Cycle-21 patched this at integration time in
`tools/stale/_integrate_fork_392503ab7d47.py::replay_shadow`, which
mutated the mid to `_run/report_cycles_1-1_clone-<k>` for each clone
before appending, and popped `event_id` so the writer regenerated it via
UUID5. This cycle pushes the fix upstream so no future 2+-clone fork
merge needs the workaround.

## 2. Write-site identification

- **File.** `long_exposure/exploration.py` (upstream, at
  `/home/user/human-in-a-loop/long-exposure/long_exposure/exploration.py`).
- **Function.** `_append_report_artifact_event(config, score_inputs, *,
  cycle, cycle_range_start, cycle_range_end, reporter_mode, artifacts)`
  at line 2620 (pre-fix).
- **Caller.** `_run_reporter` at line 3008.
- **Pre-fix behavior.** The function unconditionally builds
  `f"_run/report_cycles_{cycle_range_start}-{cycle_range_end}"` and
  assigns a fresh random `event_id: str(uuid.uuid4())` in the dict passed
  to `append_ledger_event`. Both were structurally guaranteed to collide
  on the mid across sibling clones — see cycle-21 handoff #1 and rows 304,
  311, 315 of the current main ledger.

## 3. Design

### 3.1 Milestone-id format

| Runtime state | milestone_id |
|---|---|
| Root cycle (single-clone; `AGENT_FORK_ID` unset) | `_run/report_cycles_<lo>-<hi>` |
| Fan-out clone `k` (`AGENT_FORK_ID` set, `AGENT_FORK_CLONE_K=k`) | `_run/report_cycles_<lo>-<hi>_clone-<k>` |

### 3.2 Clone-index source

The clone identity is knowable to the harness at report-write time via
two environment variables set by the fan-out driver:

- `AGENT_FORK_ID` — non-empty when this process is a fan-out clone.
- `AGENT_FORK_CLONE_K` — zero-based clone index within the fork.

These are the same two variables `_get_clone_k()` and `_is_clone()` (in
`long_exposure/fanout.py`) already consult; the existing filename
basename branch at `long_exposure/exploration.py:2803` already routes on
them. The fix reuses these unchanged.

### 3.3 Root-vs-fanout decision rule

Both must hold to apply the `_clone-<k>` suffix: `_is_clone()` returns
True AND `_get_clone_k()` returns a non-None int. If either fails,
the un-suffixed root form is emitted. This preserves the root-cycle
path exactly (see §5).

### 3.4 Event-id derivation

The manual `event_id: str(uuid.uuid4())` is dropped. `append_ledger_event`
auto-derives a UUID5 content-hash `event_id` via
`long_exposure.tools._ledger_schema.content_hash_event_id`. Under the
new namespaced mids, the three clone-`<k>` payloads are structurally
distinct, so UUID5 event_ids for different clones cannot collide even
when other fields happen to match.

### 3.5 SSoT helper

The mid-construction logic lives in `long_exposure/fanout.py` as a new
public-ish helper:

    def report_cycles_milestone_id(cycle_range_start, cycle_range_end):
        base = f"_run/report_cycles_{cycle_range_start}-{cycle_range_end}"
        if _is_clone():
            k = _get_clone_k()
            if k is not None:
                return f"{base}_clone-{k}"
        return base

`exploration.py` imports it alongside the existing `_is_clone` /
`_get_clone_k` imports and calls it inside `_append_report_artifact_event`.
Placing the helper in `fanout.py` (which has zero heavy deps) means
the cycle-22 test suite can exercise the fix without pulling in
`exploration.py`'s full import chain (which requires `prompt_toolkit`
and other harness-side modules).

## 4. Change diff (minimal snippet)

**`long_exposure/fanout.py`** — new helper appended immediately after
`_is_clone`:

    def report_cycles_milestone_id(cycle_range_start, cycle_range_end):
        """Build the harness auto-write milestone_id for the periodic-
        report artifact-registration event. Namespace-aware."""
        base = f"_run/report_cycles_{cycle_range_start}-{cycle_range_end}"
        if _is_clone():
            k = _get_clone_k()
            if k is not None:
                return f"{base}_clone-{k}"
        return base

**`long_exposure/exploration.py`** — write-site rewritten from:

    append_ledger_event(workspace, {
        "event_id": str(uuid.uuid4()),
        "ts": ...,
        ...
        "milestone_id": (
            f"_run/report_cycles_{cycle_range_start}-{cycle_range_end}"
        ),
        ...
    })

to (the manual `event_id` is gone; the mid comes from the helper):

    _mid = report_cycles_milestone_id(
        cycle_range_start, cycle_range_end
    )
    append_ledger_event(workspace, {
        "ts": ...,
        ...
        "milestone_id": _mid,
        ...
    })

And the fan-out import list at the bottom of the file gains one line:

    from long_exposure.fanout import (
        ...
        _get_clone_k,
        _get_fork_id,
        _is_clone,
        report_cycles_milestone_id,   # ← added
        ...
    )

Both edits land upstream under `long_exposure/*`, within the established
out-of-workspace WARN exemption cycles 6, 10, 12, 14 relied on.

## 5. Backward-compatibility argument

1. **Existing rows unaffected.** No historical row is rewritten. The
   validator (`_ledger_schema.validate_event`) does not re-canonicalize
   historical event_ids or mids; it only shapes new emits.
2. **Root-cycle single-clone path unchanged.** When `AGENT_FORK_ID` is
   unset, `_is_clone()` returns False, the helper returns the
   un-suffixed base form, and the payload matches what root cycles
   have been writing since day one (e.g. `_run/report_cycles_1-3`,
   `_run/report_cycles_4-6`, `_run/report_cycles_7-9`,
   `_run/report_cycles_10-12`, `_run/report_cycles_13-15`,
   `_run/report_cycles_16-18`, `_run/report_cycles_20-22`). Only the
   `event_id` field's derivation source changes from random UUID4 to
   content-hashed UUID5 — the schema accepts both (both are valid RFC
   4122 UUIDs), and the `_ledger_schema.validate_event` regex does not
   distinguish them.
3. **UUID5 duplicate guard.** `append_ledger_event`'s duplicate-event_id
   guard would fire only if two runs produced the exact same
   canonical-JSON payload (mid, ts, run_id, cycle, artifacts,
   narrative, confidence subfields all equal). That is a legitimate
   duplicate-write to be rejected — it fires nowhere in existing history
   because ts differs run-to-run.
4. **milestone_id regex acceptance.** The SSoT regex
   `MILESTONE_ID_REGEX` (`_ledger_schema.py:148`) matches
   `_(run|plan|infra|manager|archive|audit|report|handoff|proto)/[A-Za-z0-9_.\-/]+`;
   `_clone-<k>` in the tail is `[A-Za-z0-9_.\-]+` — accepted.
5. **Fanout-concat contract unchanged.** Cycle-15's per-milestone ts
   monotonicity rule is preserved verbatim; the fix simply ensures
   each clone's harness auto-write lives under its own milestone_id,
   so the monotonicity check is per-clone-vacuous.

## 6. Replay proof

Reconstruct the three cycle-21 shadow-ledger rows for
`_run/report_cycles_1-1` at
`/home/user/music-gen-instance/fork-392503ab7d47/clone-{0,1,2}/promise_ledger.jsonl`;
transform each per the fix (namespace mid via
`report_cycles_milestone_id(1, 1)` with `AGENT_FORK_ID` set and
`AGENT_FORK_CLONE_K=k`; drop `event_id`; UUID5-derive via
`content_hash_event_id`). Compare each transformed row to the
corresponding current main-ledger row.

### 6.1 SHA-256 pairs (canonical_json of the full row)

| Clone | Shadow (pre-fix) canonical SHA-256 | Main-ledger (post-integration) canonical SHA-256 | Fix-transformed canonical SHA-256 | Match |
|---|---|---|---|---|
| 0 | `0d17efd79c0058f19422c51a5b909fab11460946cbdc03f4f9f466d3f80eb31c` | `9459723e6f8cf2f1d9e60b07692030202beb21e853d9fb19001aa47a8c236152` | `9459723e6f8cf2f1d9e60b07692030202beb21e853d9fb19001aa47a8c236152` | **byte-identical** |
| 1 | `232a95b83b1b4a3d20f9c6b0ee2c5fb0e674db7507a100fd9fdd006505849d29` | `6831d2e68fe1de013af89e821f271526d7dfc003c7111bd87ba561844cdd4d6c` | `6831d2e68fe1de013af89e821f271526d7dfc003c7111bd87ba561844cdd4d6c` | **byte-identical** |
| 2 | `324c78d3086ce1169535beb72b41365ed0eab9c38021ab7505b20b50d1fba4bd` | `915744fe248276054f143547727ecad0d469d613f11eab520bba1a4e13237b35` | `915744fe248276054f143547727ecad0d469d613f11eab520bba1a4e13237b35` | **byte-identical** |

Byte-identity holds at the strongest possible level: **full canonical
JSON** — not merely at the tuple `(milestone_id, event_id,
canonical_json-excluding-ts)` the brief nominates. All three
`event_id` values (`83fc83c1-5d35-52f6-a050-91a1898c3be9`,
`b94f44d8-7e6c-55ac-a1fa-a9caace78fd0`,
`64c47584-f956-5cf4-b529-d9f31fb26424`) match; all three timestamps
match (cycle-21 driver was pure pass-through on ts); all three mids
match; all payload fields match.

### 6.2 Byte-determinism × 2

Running `concat_clone_ledgers` twice on the reconstructed shadows
(fresh temp workspace per run) produces the same merged output:

    run 1 SHA-256: 384326f7e17fdf6ae8b9f48d7483aca9bee4d8e597a1918f07ed322dbfd6a074
    run 2 SHA-256: 384326f7e17fdf6ae8b9f48d7483aca9bee4d8e597a1918f07ed322dbfd6a074
    IDENTICAL: True

Emitted by `tools/_replay_proof_cycle22.py` (archived to
`tools/stale/` at cycle end; regeneratable at any time).

## 7. Test suite summary

| Suite | Before | After | Status |
|---|---|---|---|
| `tests/test_harness_report_namespacing.py` (**new**) | — | **7/7 pass** | GREEN (brief asks ≥6; shipped 7 — the extra one is a source-shape AST guardrail against silent regression) |
| `tests/test_fanout_concat_validation.py` | 15/15 pass | **17/17 pass** (§16 cases 16, 17 added) | GREEN |
| `tests/test_ledger_writer_validation.py` | 21/21 pass | **21/21 pass** (unchanged) | GREEN |
| `tests/test_integration_cross_branch.py` | 0 failures across §1–§30 | **0 failures across §1–§30** | GREEN |
| `promise_check .` | 0 ERROR | **0 ERROR** | GREEN |

### 7.1 New test module cases

1. Root invocation → un-suffixed milestone_id.
2. Fanout clone k=0 → `_clone-0` suffix.
3. Three parallel clones → three distinct milestone_ids.
4. **Cycle-21 replay**: three main-ledger rows byte-identical at
   `(milestone_id, event_id, canonical_json-excluding-ts)`.
5. Concat idempotence — pre-namespaced 3-clone shadows merge cleanly
   and re-run is a no-op.
6. Validator + shadow-lint accept the namespaced milestone_id unchanged.
7. Write-site source drops `uuid.uuid4()` event_id AND routes mid
   through `report_cycles_milestone_id` (AST-level guard).

### 7.2 Concat test module extensions (§16, cases 16-17)

16. **Regression cure**: 3-clone concat with pre-namespaced
    `_run/report_cycles_*_clone-*` rows out of file-order-ts merges
    cleanly (reproduces cycle-21's exact ts pattern
    16:53:17→16:59:57→16:54:07; under the fix the monotonicity check
    is per-clone-vacuous).
17. **Regression guard**: two clones sharing the un-namespaced
    `_run/report_cycles_1-1` fail-loud with the specific per-milestone
    ts monotonicity message. Catches a future harness that loses its
    namespacing.

## 8. Failure-mode enumeration

| Scenario | Behavior | Diagnostic |
|---|---|---|
| Root cycle (no `AGENT_FORK_ID`) | Un-suffixed mid emitted | (silent — normal) |
| Clone `k` with `AGENT_FORK_ID` set and `AGENT_FORK_CLONE_K=k` (int-parseable) | `_clone-<k>` suffix emitted | (silent — normal) |
| Clone with `AGENT_FORK_ID` set but `AGENT_FORK_CLONE_K` unset or non-int (e.g. `"bogus"`) | Fallback to un-suffixed mid (safe) | (silent — matches pre-fix root behavior) |
| Clone with sentinel `AGENT_FORK_CLONE_K=-1` | `_clone--1` emitted (distinct from any real k≥0) | (silent — same sentinel used by filename branch) |
| Future fanout driver forgets to set `AGENT_FORK_CLONE_K` on 2+ clones | Both clones fall back to un-suffixed mid → shadow-concat fails-loud at cycle-15 monotonicity check | `LedgerConcatError: ... monotonicity violation on milestone_id '_run/report_cycles_<lo>-<hi>' between clone-<a> ... and clone-<b> ...` (guarded by case 17) |
| Two runs coincidentally emit identical canonical payloads | `append_ledger_event`'s duplicate-event_id guard rejects | `LedgerAppendError: duplicate event_id ...` |

## 9. Downstream implications

- Future 2+-clone fork merges **need no per-clone id normalization**.
  The cycle-21 workaround (per-clone id renaming inside a bespoke
  integration driver) is retired for all new forks.
- Cycle-21's driver at `tools/stale/_integrate_fork_392503ab7d47.py`
  and its 3 lines of normalization
  (`if r.get("milestone_id") == COLLIDING_MID: r["milestone_id"] =
  f"{COLLIDING_MID}_clone-{k}"; r.pop("event_id", None)`) become a
  historical artifact only — not a template to reuse.
- Integration cycles after cycle-22 should exercise the standard
  `concat_clone_ledgers` path directly. If a 2+-clone merge still
  errors on `_run/report_cycles_*` monotonicity, that is now a
  legitimate SIGNAL that the harness lost its namespacing (probably
  a fanout-driver env-var regression) — case 17 exists to catch it
  before it hits production.
- The SSoT helper `report_cycles_milestone_id` is now the sole source
  of truth for the report artifact's mid. Any future evolution
  (e.g. cross-cycle-range clones, nested fan-outs) extends the helper
  once, and both the emitter and the tests pick it up.

## 10. Investigation-contract outcome

**Outcome: SUCCESS.** The harness code path is fully accessible; the
upstream edit landed and is exercisable end-to-end from the test suite
without a live fan-out. The falsifiability escape hatch (publishing a
FAIL with a minimal upstream patch proposal + reusable
`tools/_normalize_clone_report_ids.py` helper) is **NOT** exercised;
the honest positive result stands on its own.

Evidence:
- Byte-identical replay for all three clones (§6.1) — the strongest
  possible byte-identity claim (full canonical JSON, not just the
  brief's nominated tuple).
- Byte-determinism × 2 on the concat itself (§6.2).
- All five validation gates GREEN (§7).

## References

- `promise_ledger.jsonl` rows 304, 311, 315 (post-cycle-21-integration
  targets)
- `tools/stale/_integrate_fork_392503ab7d47.py::replay_shadow`
  (cycle-21 per-clone id normalization pattern this cycle retires)
- `long_exposure/tools/_ledger_schema.py::MILESTONE_ID_REGEX`,
  `content_hash_event_id`, `_EVENT_ID_NAMESPACE`
- `long_exposure/workspace_bootstrap.py::append_ledger_event`,
  `concat_clone_ledgers`, `_lint_clone_shadow`
- Cycle-15 clone-0 `_STATE_TRANSITIONS` (permits `validated →
  validated` self-loop used by parent rollups)
- Cycle-21 report at `merge_report.md` (fork 392503ab7d47 capstone)
