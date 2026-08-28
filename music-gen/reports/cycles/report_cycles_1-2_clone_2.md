---
title: "Music-Gen — M-INGEST-1/egress-ready-automation (cycles 1-2, fork 3a908edcb241, clone 2)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — M-INGEST-1/egress-ready-automation (cycles 1-2, fork 3a908edcb241, clone 2)

## Abstract

Clone 2 built the crash-resumable state machine that closes the "egress opens mid-run and nobody catches it" hole in the campaign's rated-audio pipeline. Cycle 1 delivered the module (`scripts/egress_ready/{__init__, trigger, state, subprocess_hooks, cli}.py` — 776 lines), six named fixtures under `tests/fixtures/egress_status/`, a 62-check test suite (`tests/test_egress_ready_state.py`, 434 lines), a §17 extension to the cross-branch integration test (52 additional checks), a 305-line documentation page (`docs/egress_ready_automation.md`, all 13 required sections present), a five-column plan-of-record row, three shadow-ledger events, and merge reports at both the workspace root and the shadow-ledger clone path. The cycle-1 auditor emitted `VALIDATED/high`, independently reproducing every falsification criterion — the six-scenario matrix (all-false, single-true-then-back, two-consecutive-triggers, already-triggered-then-false, interleaved-then-true-true, stale-row-does-not-count); byte-deterministic `transitions.jsonl` across independent runs; atomic `state.json` survival of a monkey-patched `os.replace` crash; zero real `subprocess.run` calls in tests; zero `sidecar_nonfactor` imports; and all 13 required documentation sections. Cycle 2 was a termination cycle: the researcher acknowledged scope exhaustion, the worker performed a presence check with no ledger events / code edits / doc changes, and the auditor emitted `COMPLETE` with `[[BRANCH_COMPLETE]]`. No live harvest was attempted by contract — proving the machine will notice when egress unblocks is a distinct question from proving egress will unblock, and only the former is this branch's scope.

## Introduction

`M-INGEST-1/egress-probe` already writes one row per `workspace/harvest_playlists.sh` retry into `data/ingestion/egress_status.jsonl` with `{ts, media_ok, http_code, …}`. Until this branch landed, no code watched those rows: when egress relaxes and the probe starts recording `media_ok=true`, the rated-audio pipeline (harvester → chunker → classifier → M-EAR-1 training-set assembly) does not fire until a human notices. The campaign's fixed decision that acquisition never blocks downstream work implies a companion decision — that acquisition also never *silently* unblocks work. The state machine codifies that companion decision as an on-disk trigger detector.

The specific mechanism is: two consecutive fresh `media_ok=true` rows in the probe log constitute the unblock signal. A single true row is a coincidence — the CDN sometimes returns a 302 once before reverting — while two in a row means egress has actually opened. Freshness is enforced by a 24-hour staleness rejection: a row whose timestamp lies at or before `now_utc − 24 h` is treated as if absent, so an old good day cannot masquerade as a current unblock.

## Approach

The module is partitioned so the pure logic is easy to test and the impure edges are the single injection point for the whole system:

- **`trigger.py`** — the pure-function `detect_trigger(rows, now_utc, staleness_hours=24)`. Filters `rows` by strict `<` freshness, returns `NONE` if no fresh rows remain or if the last fresh row is false, returns `TRIGGERED((i0, i1))` if the last two fresh rows are both true, and returns `ARMED((i,))` if exactly one trailing fresh true exists. Only the last streak matters: `[T, F, T, T]` → `TRIGGERED(2, 3)`; `[T, T, F]` → `NONE`.
- **`state.py`** — the finite-state machine over `IDLE → ARMED → TRIGGERED → HARVESTING → CHUNKING → CLASSIFYING → READY` with a `FAILED` sink, an authoritative transition map (`state.TRANSITIONS`), and atomic persistence.
- **`subprocess_hooks.py`** — the single injection point for the four downstream commands (`workspace/harvest_playlists.sh`, the chunker CLI, the classifier CLI, and the ready-flag writer). Tests inject an `OkHooks` or `FailAtHooks` subclass; the test module additionally monkey-patches `subprocess.run` itself at import time with a `_SubprocessRunForbidden` guard, so any accidental live invocation raises immediately.
- **`cli.py`** — the human-override interface: `--status`, `--watch` (`--loop N` stub), `--force-idle`, `--force-trigger`, `--resume`, `--reset-failure`.

**State persistence.** `state.json` is written on every transition via a same-directory `NamedTemporaryFile` plus `os.fsync` plus `os.replace`; POSIX `rename(2)` is atomic across a same-filesystem replace, so no reader ever observes a torn file. `transitions.jsonl` is append-only: every transition writes a `{timestamp_utc, from_state, to_state, reason, evidence_ref}` line. A fresh `EgressReadyMachine(...)` constructed against the same `state.json` loads the exact recorded snapshot and picks up where a crashed predecessor left off — the constructor re-runs the current stage's hook and no earlier one, relying on each downstream milestone's own idempotence guarantee (the chunker is deterministic; the classifier writes content-hashed sidecars; the harvester skips already-fetched ids).

**Failure semantics.** Any hook returning `HookResult(ok=False)` triggers `_fail(from_stage, hook_name, result)`, which writes a `diagnostic_YYYYMMDD_HHMMSS.json` under `data/egress_ready/` with `{failed_at_stage, hook, returncode, stderr_tail (4 KiB), duration_s, timestamp_utc}` and transitions to `FAILED` with `failed_stage` and `diagnostic_path` recorded in `state.json`. The chain halts until a human invokes `--resume` (which is legal only from `FAILED`, requires `failed_stage ∈ {HARVESTING, CHUNKING, CLASSIFYING}`, and re-runs *only that stage and its successors*) or `--reset-failure` combined with `--force-idle` (a deliberate two-flag acknowledgement that the failure is being abandoned; the library raises `InvalidTransition` without the acknowledgement, and the CLI exits 2).

## Findings

### The six-scenario matrix

All six scenarios pass end-to-end against synthetic fixtures at `tests/fixtures/egress_status/`, with the reference clock frozen to `2026-08-28T10:00:00Z`:

| # | Scenario | Expected detect_trigger | Expected terminal state |
|---|---|---|---|
| 1 | all-false | `NONE` | `IDLE` |
| 2 | single-true-then-back | `NONE` | `IDLE` |
| 3 | two-consecutive-triggers | `TRIGGERED(1, 2)` | `READY` |
| 4 | already-triggered-then-false | first call `TRIGGERED`; re-scan does not retract | `READY` |
| 5 | interleaved-then-true-true | `TRIGGERED(2, 3)` | `READY` |
| 6 | stale-row-does-not-count | `ARMED((1,))` (stale row invisible) | `ARMED` |

Every drive-through additionally asserts that `state.json` on disk matches the terminal in-memory state (or is absent when the machine never left `IDLE`), that `transitions.jsonl` records the correct sequence and is append-only, and that a second `EgressReadyMachine(...)` against the same disk state returns the same terminal state without re-firing any hook (idempotence).

### Verified invariants

- **Byte-deterministic `transitions.jsonl`** across two independent `--watch` invocations against the same fixture — SHA-256 equal.
- **Atomic `state.json` under crash.** The test suite monkey-patches `os.replace` to raise mid-transition and asserts that the previous `state.json` bytes remain readable.
- **Zero live subprocess calls.** `subprocess.run` is replaced with `_SubprocessRunForbidden` at import time; the test never exercises the real network or the real harvester.
- **Zero `sidecar_nonfactor` imports.** Every module under `scripts/egress_ready/` guards the interpreter with `assert sys.executable == "/usr/bin/python3"` at import time, and both the local test suite and the AST/regex scan in `tests/test_integration_cross_branch.py §17` (module-level constant `_er_pat`) enforce the isolation contract.
- **Command argv stability.** `HARVEST_CMD`, `CHUNKER_CMD`, `CLASSIFIER_CMD`, and `READY_FLAG_PATH` are pinned as module-level constants and asserted verbatim by the integration test; a silent refactor of any of them fails CI.

### Test counts at branch exit

- `tests/test_egress_ready_state.py` — 62/62 passing.
- `tests/test_integration_cross_branch.py §17` — 52/52 passing (new checks added by this branch, coexisting with the sibling clones' §14 additions).
- Byte-determinism SHA-256 reproduced live by the auditor.
- Atomic-write crash-test reproduced live by the auditor.

### Documentation and handoff

`docs/egress_ready_automation.md` — 305 lines, 15,036 bytes, 13 top-level sections: Purpose, Scope, Non-goals, State diagram (mermaid), Trigger rule (with an explicit falsification-criteria block), Six-scenario matrix, State persistence (with a worked crash-between-CHUNKING-and-CLASSIFYING example), Failure recovery, Human-override API, Isolation, Handoff, Reproduction, Pointers.

### Cycle 2: null cycle, correct exit

Cycle 2 was a termination cycle by design. The researcher's brief acknowledged that scope was genuinely exhausted after cycle 1's `VALIDATED/high` and instructed the worker to verify presence only and not to emit ledger events, edit code, or extend the documentation. The worker complied: an `ls -la docs/egress_ready_automation.md merge_report.md` verification of both files at their cycle-1 sizes and timestamps (15,036 bytes and 6,860 bytes respectively), no other state change. The auditor emitted `COMPLETE` under the guidance that when a null cycle occurs on a milestone whose scope is genuinely exhausted, the correct verdict is `COMPLETE`, not `PIVOT`, and issued `[[BRANCH_COMPLETE]]` so the orchestrator does not rely on the low-output detector to converge across another empty pass.

## Discussion

Three properties of this branch are worth naming. First, the two-consecutive-fresh-true rule is a conservative choice motivated by CDN behaviour, and it is not tunable through the CLI. Making it tunable would be tempting — a `--min-consecutive N` or a `--staleness-hours H` flag looks harmless — and is deliberately refused. A human-tunable trigger rule invites drift under pressure ("just this once, one true is enough"); the pipeline that fires when the rule fires produces artefacts (harvest cache, chunk manifests, classifier sidecars, `rated_ready.flag`) that will be reasoned about later, and their provenance is legible only if the trigger rule that produced them is fixed. If the rule turns out to be wrong, the correct response is to change it in code, in one place, with a diff and a review, rather than to make it configurable per invocation.

Second, the `--resume` semantics were delivered as "resume from failing stage forward" rather than "restart the failing stage from a clean state". The two look identical when the failing hook is idempotent — which is contractually true for all four downstream hooks in this pipeline — and different only if a hook were to accidentally accumulate state on repeated calls. The chosen semantics keep the state machine simple (`_drive_chain()` is the same code path for the initial run and the resume) and rely on the downstream milestones' own idempotence guarantees, which is where the responsibility already lives.

Third, the `--reset-failure` + `--force-idle` two-flag acknowledgement is the branch's one deliberate ergonomic friction. `--reset-failure` alone would be easy to type and easy to run inadvertently against a failure that still needed diagnosis; requiring `--force-idle` in the same invocation makes the human write down "I am abandoning this failure and returning the machine to IDLE" as a positive action, and the diagnostic JSON on disk survives to be read later regardless. The CLI's exit-code plan (`0` success, `1` no-op / help, `2` reset-without-force-idle, `3` `InvalidTransition`) makes each failure legible to an outer orchestrator.

Downstream, the state machine's handoff surface is intentionally narrow. When it writes `data/ear/rated_ready.flag`, its sidecar `data/ear/rated_ready.flag.json` records the UTC timestamp and the argv of the three commands that produced the rated-audio artefacts. M-EAR-1 (parent, training) treats the flag as the single signal that rated audio, chunks, and classifier sidecars are all on disk. There is no coupling in the other direction: this module does not read anything M-EAR-1 produces, and swapping the training path later requires no change here.

## Open Questions

None within the branch's scope; all cycle-1 falsification criteria came back green under independent reproduction, and cycle 2 confirmed no scope-internal work remained. Items explicitly deferred to future cycles are recorded on the documentation page as non-goals — they are the right pieces of work at the right time, but they are not this branch's:

- **Live-network integration.** Actually exercising the machine against a real relaxed egress; a distinct question from proving the machine will notice when egress unblocks, which is what this cycle answered.
- **Continuous-poll daemon.** The `--loop N` flag is a stub; production use is per-orchestrator-tick `--watch` invocation. A daemon is a supervisor concern, not a state-machine concern.
- **Retry loop.** By contract this state machine is a trigger detector, not a retry loop. Repeated harvest attempts belong at the orchestrator level with the failure-diagnostic JSON as its input.

For the root conductor, the natural next research step for this fork is the post-merge integration cycle for fork `3a908edcb241`, which will reconcile all three clones' shadow ledgers into the root ledger (mirroring the pattern established in cycles 3, 5, and 7), extend the cross-branch integration test's section numbering as needed (this branch's §17 coexists with the sibling clones' §14 and their score-bridge additions; renumber during integration if any collision), and confirm file-tree disjointness (`scripts/score/*`, `scripts/transcribe/octave_suppression.py`, and `scripts/egress_ready/*` share no path). This is out of scope for a fanout clone.

## Appendix: Provenance

**Cycle range:** cycles 1-2 of fork `3a908edcb241`, clone 2 of 3.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:**

- Cycle 1: researcher `8c17d07b-5cb3-40d7-b0d7-bd44e5cb72fb`, worker `fd0c6c9e-34bc-4b0d-b3ea-04c775716b71`, auditor `fffd9a03-d17b-48e9-a350-9ab90c4cdd95`.
- Cycle 2: researcher `6853eb97-6044-4369-b334-52767b466268`, worker `925bafba-2111-49cd-80f8-d05134482317`, auditor `2b66a842-d318-415f-bb9a-389508e1bb54`.

**Auditor verdicts.** Cycle 1: `VALIDATED/high` on independent reproduction of every falsification criterion. Cycle 2: `COMPLETE` with `[[BRANCH_COMPLETE]]` under the null-cycle-on-exhausted-scope rule.

**Deliverables on disk:**

- Code: `scripts/egress_ready/{__init__.py, trigger.py, state.py, subprocess_hooks.py, cli.py}` — 776 lines total; each module guards the interpreter with `assert sys.executable == "/usr/bin/python3"` at import time.
- Fixtures: `tests/fixtures/egress_status/{all_false, single_true_then_back, two_consecutive_triggers, already_triggered_then_false, interleaved_then_true_true, stale_row_does_not_count}.jsonl`.
- Tests: `tests/test_egress_ready_state.py` (434 lines, 62 checks); `tests/test_integration_cross_branch.py §17` (52 new checks).
- Documentation: `docs/egress_ready_automation.md` (305 lines / 15,036 bytes / 13 top-level sections).
- Runtime state: `data/egress_ready/state.json` and `data/egress_ready/transitions.jsonl` are not on disk yet; they are created on the first live trigger. Diagnostics are written under `data/egress_ready/diagnostic_*.json` on failure.
- Plan of record: five-column Milestones row for `M-INGEST-1/egress-ready-automation` at plan_of_record line 71.

**Ledger routing:** three shadow-ledger events landed at `/home/user/music-gen-instance/fork-3a908edcb241/clone-2/promise_ledger.jsonl` — `M-INGEST-1/egress-ready-automation` completion, `_plan/register-egress-ready-milestone` (plan-file edit), and `_archive/egress-ready-scratch-fork-3a908edcb241` (scratch archival). The 54 `orphan artifact` WARNs on the workspace-root `promise_check` are the routine consequence of shadow-ledger routing across fanout clones; they clear at fork-merge under the root conductor's `_infra/adopt-fanout-artifacts-*` pattern established in cycles 3, 5, and 7.

**Environment discipline.** No pip installs, no `numpy` / `torch` / `tensorflow` changes on this branch. Contrast with the cycle-4 M-TEX-1/panel/embedding branch which introduced the `numpy 2.4.6 → 1.26.4` downgrade; this branch is environment-neutral.

**Merge reports:** written at `/home/user/long-exposure-runs/music-gen/merge_report.md` (workspace root, 6,860 bytes) and `/home/user/music-gen-instance/fork-3a908edcb241/clone-2/merge_report.md` (shadow-ledger clone path).

**Handoff to root conductor.** When `workspace/harvest_playlists.sh` begins writing `media_ok=true` rows post-egress-relaxation, this state machine fires the rated-audio pipeline unattended, writes `data/ear/rated_ready.flag`, and unblocks the M-EAR-1 (parent, training) milestone. This branch is the trigger that closes the "nobody catches the egress opening" hole. The root conductor's post-merge integration cycle should adopt the artefact list above under `M-INGEST-1/egress-ready-automation`, fold the three shadow-ledger events into the root ledger, and reconcile §17 numbering against sibling clones' cross-branch additions.

<verdict>validated</verdict>
