# Merge report — fork 3a908edcb241 clone 2 (M-INGEST-1/egress-ready-automation)

**Cycle:** 8
**Fork:** 3a908edcb241
**Clone:** 2 of 3
**Milestone:** M-INGEST-1/egress-ready-automation
**Status:** validated/high
**Sibling clones (disjoint file trees):**
- clone 0 → `scripts/score/*` (M-SCORE-1)
- clone 1 → `scripts/transcribe/octave_suppression.py` (M-TRANS-1/basic-pitch/octave-suppression)
- clone 2 → `scripts/egress_ready/*` + `tests/fixtures/egress_status/*` (this branch)

## Deliverable

`docs/egress_ready_automation.md` (required output artifact) is on disk with all 10 sections the research brief required: Purpose, Scope, Non-goals, State diagram (mermaid), Trigger rule + falsification criteria, Six-scenario matrix, State persistence, Failure recovery, Human-override API, Isolation, Handoff, Reproduction.

## New files (all under this clone's exclusive subtree)

```
scripts/egress_ready/__init__.py
scripts/egress_ready/trigger.py           # detect_trigger, TriggerDecision, TriggerKind, load_jsonl
scripts/egress_ready/state.py             # EgressReadyMachine, State, TRANSITIONS, override API
scripts/egress_ready/subprocess_hooks.py  # SubprocessHooks + HARVEST_CMD/CHUNKER_CMD/CLASSIFIER_CMD/READY_FLAG_PATH
scripts/egress_ready/cli.py               # --watch/--status/--force-*/--resume/--reset-failure
tests/test_egress_ready_state.py          # 62 checks, all PASS
tests/fixtures/egress_status/all_false.jsonl
tests/fixtures/egress_status/single_true_then_back.jsonl
tests/fixtures/egress_status/two_consecutive_triggers.jsonl
tests/fixtures/egress_status/already_triggered_then_false.jsonl
tests/fixtures/egress_status/interleaved_then_true_true.jsonl
tests/fixtures/egress_status/stale_row_does_not_count.jsonl
docs/egress_ready_automation.md           # REQUIRED OUTPUT ARTIFACT
```

## Shared-state touches

- `plan_of_record.md` — added one row to the 5-col Milestones table for
  `M-INGEST-1/egress-ready-automation` so `promise_check`'s parser resolves
  the researcher's cycle-8 kickoff event. Same drift-fix pattern as
  `_plan/register-ear-preparation-milestones` (cycle 6) and
  `_plan/register-post-merge-integration-milestones` (cycle 7). No other
  rows touched.
- `tests/test_integration_cross_branch.py` — appended §17 (52 checks) at the
  end of the file. Existing sections (§1–§14) untouched. §17 covers:
  isolation AST/regex scan for `sidecar_nonfactor`; module-level command
  constants (`HARVEST_CMD`, `CHUNKER_CMD`, `CLASSIFIER_CMD`, `READY_FLAG_PATH`)
  stability; fixture presence; TRANSITIONS map invariants; docs sections
  present.

## Ledger events (shadow ledger, per-clone)

Written to `/home/user/music-gen-instance/fork-3a908edcb241/clone-2/promise_ledger.jsonl`:

1. `M-INGEST-1/egress-ready-automation` — **validated/high** — 13 artifacts.
2. `_plan/register-egress-ready-milestone` — validated/high — 1 artifact
   (`plan_of_record.md`).
3. `_archive/egress-ready-scratch-fork-3a908edcb241` — validated/high — 3
   artifacts (three one-shot emitters moved to `tools/stale/`).

All events schema-valid per `long_exposure.tools.ledger_append._validate_event`
(required fields: `event_id`, `ts`, `run_id`, `cycle`, `agent`,
`milestone_id`, `status`, `confidence` (nested `.level`/`.rationale`/`.assessor`),
`narrative`). See §Notes below on the fix-up that was required.

## Test results

```
$ PYTHONPATH=. /usr/bin/python3 tests/test_egress_ready_state.py
... 62 checks, result: PASS (0 failures)

$ PYTHONPATH=. /usr/bin/python3 tests/test_integration_cross_branch.py
... section §17 (M-INGEST-1/egress-ready) 52 checks all PASS
```

## promise_check state

At the end of this clone's work, `promise_check` reports:

- **0 errors** attributable to this clone.
  - There is 1 remaining ERROR on ledger line 112 for
    `M-TRANS-1/basic-pitch/octave-suppression` — that's clone-1's scope; my
    plan-file edit only added my own milestone row. Post-merge integrator or
    clone-1 must add its own row.
- **13 orphan-artifact WARNs** for this clone's files. Expected: my ledger
  events live in the shadow ledger; `promise_check` reads only the main
  ledger, so orphans clear only after the harness merges the shadow. Same
  pattern as prior clones (cycle-6 M-EAR-1/preparation, cycle-6
  M-RULES-1/schema, cycle-6 M-TRANS-1).

## Suggested post-merge integrator work

1. Merge this clone's shadow ledger into the main `promise_ledger.jsonl`
   (all three events are schema-valid).
2. Reconcile the plan-file: my clone added row for
   `M-INGEST-1/egress-ready-automation`. Clones 0 and 1 will similarly need
   their milestones added to the 5-col Milestones table (I did not touch
   them).
3. Re-run `promise_check`; the 13 orphan-artifact WARNs from my clone will
   clear once the shadow ledger merges.
4. Re-run `tests/test_integration_cross_branch.py`; §17 (52 checks) should
   remain green.

## Non-goals honored (from research brief)

- No live network exercised.
- No writes to `data/ingestion/egress_status.jsonl` (read-only consumer).
- No imports of `scripts.classifier.sidecar_nonfactor` from any egress_ready
  module (§17 AST scan green).
- No plan-of-record edits outside adding my own milestone row.
- No modifications to `tests/test_integration_cross_branch.py` §1–§14; only
  appended §17.
- No changes to sibling-clone paths (`scripts/score/*`,
  `scripts/transcribe/octave_suppression.py`).

## Notes for the auditor

- **Determinism substitution.** The library uses an injected `Clock`
  (`Clock(now=lambda: FIXED_UTC)` in tests, `Clock.system()` in prod). No
  `datetime.now()` in library code. This is what makes
  `transitions.jsonl` byte-identical across runs.
- **Atomicity primitive.** `tempfile.NamedTemporaryFile` in the state.json's
  parent directory + `os.fsync` + `os.replace`. Test explicitly monkey-
  patches `os.replace` to raise mid-write and asserts previous state.json
  bytes intact.
- **Isolation is guarded at two layers.** (1) The test module patches
  `subprocess.run` at import time with `_SubprocessRunForbidden` — if any
  test unintentionally triggered a real subprocess call, it would raise
  immediately. (2) The integration test's §17 scans
  `scripts/egress_ready/*.py` for `sidecar_nonfactor` at line start.
- **Ledger fix-up.** My first emitter used the wrong field schema
  (`timestamp_utc`/`rationale` flat instead of `ts`/`narrative`/nested
  `confidence`). I detected this by inspecting `REQUIRED_EVENT_FIELDS` in
  `long_exposure.tools.promise_check`. Cleaned up by truncating the
  shadow ledger and re-writing three schema-valid events. Justified per
  cycle-7 precedent (`_fix_missing_event_ids.py`): <5 min old, only I had
  written to this shadow file. The old malformed events never reached the
  main ledger.

## Exit

Cycle loop terminates naturally after this report. Task complete.
