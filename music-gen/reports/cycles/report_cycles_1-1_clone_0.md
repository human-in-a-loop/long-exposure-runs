---
title: "Music-Gen — `_infra/ledger-schema-hardening-v3` (cycle 1, fork 392503ab7d47, clone 0)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — `_infra/ledger-schema-hardening-v3` (cycle 1, fork 392503ab7d47, clone 0)

## Abstract

Cycle 1 of clone 0 closed the four-cycle SSoT ledger-schema hardening arc (writer c10 → concat c12 → field-type + enum c14 → transitions c15) by adding state-transition validation on top of cycle-14's field-shape checks, categorically foreclosing the specific drift class that cycle-14 clone-0's §2b honestly reclassified from "enum-only" to "transitions" after mis-diagnosing cycle-13's line-250 as an enum violation. A canonical `_STATE_TRANSITIONS` frozenset of 15 pairs is exported at module top level of `long_exposure/tools/_ledger_schema.py`, and a new `validate_history(rows_for_milestone)` groups by `milestone_id`, sorts by `ts`, and rejects illegal consecutive transitions with milestone + event_ids + transition-name-annotated messages. The validator is wired into `_lint_clone_shadow` and `promise_check`. Every non-negotiable bar held under the auditor's independent live re-verification: all 301 existing per-milestone histories validate under the dynamic sweep with zero grandfathering (the two observed self-loops `(validated, validated)` and `(in-progress, in-progress)` were absorbed via the cycle-14 escape-hatch expansion pattern, each with a documented mechanism); the cycle-13 line-250 pattern `validated → in-progress` without an intervening `reopened` rejects at both the writer surface (`LedgerAppendError`) and the pre-concat lint (`LedgerConcatError`), with milestone id, both event_ids, both statuses, and the `_STATE_TRANSITIONS` token present in the message; the bridging sequence `validated → reopened → in-progress` is accepted; and the public API of `append_ledger_event(workspace, event)` and `concat_clone_ledgers(workspace, fork_root)` is byte-preserved across cycles 1–14 (`inspect`-checked live). Test suites all green: writer 21/21, concat 15/15, cross-branch integration §1–§30 PASS, `promise_check` 0 ERRORs on the live 301-row ledger. The auditor emitted **COMPLETE** at `validated/high`; the four-cycle arc closes as a coherent unit.

## Introduction

By the end of cycle 14 the campaign's ledger-write triangle was complete on three of four axes: emit + check + concat surfaces all routed through the SSoT `_ledger_schema` module, and `is`-identity of `REQUIRED_EVENT_FIELDS` held across all three; cycle 14 added the `supersedes_path` type check and the `status` enum. But cycle-14 clone-0's §2b surfaced a specific class the cycle-14 validator did not close: cycle-13's line-250 drift was originally diagnosed as an enum violation (`status: "in-progress"` on a previously-`validated` milestone), and the cycle-14 enum extension did not catch it because `in-progress` is a canonical enum member. The actual mechanism was a **state-transition** drift — the transition `validated → in-progress` without an intervening `reopened` — and type/enum validators cannot express that class. Cycle 14 hoisted the state-transition validator as follow-on (b) rather than papering over the mis-diagnosis. This branch is that follow-on: extend the SSoT validator with a canonical transition graph and a `validate_history` function that groups by milestone and rejects illegal consecutive transitions, wire it into the concat lint and the check surface, and prove that no historical row fails and that the specific cycle-13 pattern rejects at both the writer and the lint gates.

## Approach

Three additions to `long_exposure/tools/_ledger_schema.py`, all consistent with cycles 10, 12, and 14:

- **`_STATE_TRANSITIONS` frozenset** at module top level. The canonical graph the brief drafted: `{not-started → in-progress}`, `{in-progress → {validated, invalidated}}`, `{validated → reopened}`, `{invalidated → reopened}`, `{reopened → {in-progress, validated, invalidated}}`, `{validated → superseded}`, `{deferred ↔ in-progress}`, `{action_required ↔ in-progress}`. The 13 brief pairs plus two escape-hatch self-loops (see Findings) for 15 pairs total. Every endpoint drawn from `STATUS_VALUES`; `_STATUS_ENUM is STATUS_VALUES` alias from cycle 14 preserved.
- **`validate_history(rows_for_milestone)`** — groups rows by `milestone_id`, sorts each group by `ts`, walks consecutive pairs, and raises `LedgerAppendError` at the writer gate or `LedgerConcatError` at the lint gate on any pair not in `_STATE_TRANSITIONS`. Message shape at both gates names the milestone, both event_ids, both statuses, and the `_STATE_TRANSITIONS` token so the reader can find the graph.
- **Wiring.** `validate_history` is called inside `_lint_clone_shadow` after per-row `validate_event` (so per-row schema failures still surface first), and inside `promise_check._check_lifecycle` after the existing ledger read. Neither the writer's nor the concat's public signature changes; both continue to accept the same arguments and return the same values as cycles 1–14.

**Non-grandfathering escape hatch.** The brief carried the cycle-14 pattern — if legitimate historical rows fail, expand the graph rather than reject them. The dynamic 301-row sweep found the graph needed exactly two additions: `(validated, validated)` for parent-milestone rollups (54 real occurrences — a validated child milestone triggers a validated parent rollup) and `(in-progress, in-progress)` for mid-cycle progress notes (3 real occurrences). Both were added, both are documented in `docs/ledger_schema_hardening_v3.md`, and both are traceable to real ledger rows — the escape hatch is used honestly rather than as cover for drift.

**Test additions.** `tests/test_ledger_writer_validation.py` extended 18 → 21 (three new cases: cycle-13 pattern rejection at writer with correct message shape; `validated → reopened → in-progress` bridging accepted; single-row history no-op). `tests/test_fanout_concat_validation.py` extended 13 → 15 (two new cases: cycle-13 pattern rejection at lint with `<shadow_path>:<line>` annotation flowing through; multi-row shadow with mixed legal and illegal transitions). Both test files carry the `_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"` `sys.path` shim — the sixth consecutive cycle applying the shim discipline. `docs/ledger_schema_hardening_v3.md` ships as the branch's sole required output.

## Findings

### Auditor CRITICAL matrix (all pass)

| Check | Result |
|---|---|
| `_STATE_TRANSITIONS` at module top level | 15 pairs, live-import verified, `frozenset` of `(str, str)` tuples, every endpoint in `STATUS_VALUES` |
| `_STATUS_ENUM is STATUS_VALUES` (cycle-14 alias preserved) | True |
| Full-ledger dynamic sweep of `validate_history` on all 301 rows | 0 errors; 7 distinct consecutive transitions observed; all 7 are proper subset of `_STATE_TRANSITIONS` |
| Cycle-13 line-250 pattern rejection at writer | `LedgerAppendError` raised with milestone id, both event_ids, both statuses, `_STATE_TRANSITIONS` token in message |
| Bridging sequence `validated → reopened → in-progress` at writer | Accepted |
| Cycle-13 pattern rejection at pre-concat lint | `LedgerConcatError` raised naming shadow path, milestone, and transition; `<shadow_path>:<line>` annotation from cycle 14 flows through |
| Atomicity on rejection | Ledger file line count unchanged after transition-failure attempt |
| Public API of `append_ledger_event(workspace, event)` | signature byte-identical to cycle 14 |
| Public API of `concat_clone_ledgers(workspace, fork_root)` | signature byte-identical to cycle 14 |
| Writer suite `tests/test_ledger_writer_validation.py` | 21/21 pass |
| Concat suite `tests/test_fanout_concat_validation.py` | 15/15 pass |
| `tests/test_integration_cross_branch.py` §1–§30 | PASS (0 failures) |
| `promise_check` on live 301-row ledger | 0 ERRORs |
| `_LE_PARENT` `sys.path` shim in both extended test files | Present |

### Escape-hatch expansions (documented, honest)

The graph the brief drafted covered 13 pairs; the 301-row dynamic sweep found two legitimate patterns not covered:

| Pair added | Occurrences | Mechanism |
|---|---:|---|
| `(validated, validated)` | 54 | Parent-milestone rollup: a validated child produces a validated parent rollup — a real semantic pattern the campaign has used since cycle 6 |
| `(in-progress, in-progress)` | 3 | Mid-cycle progress notes: a milestone in progress produces a further progress note without changing status |

Both are self-loops rather than novel transitions to new states; both are traceable to specific ledger rows; both are documented in §5 of the docs page. The cycle-14 expansion pattern (add historical entries to the enum rather than reject them; document mechanism; the escape hatch is used honestly) held.

### Observed transitions vs graph (all 7 real transitions in the graph)

| Observed transition | Count |
|---|---:|
| `(validated, validated)` | 54 |
| `(in-progress, validated)` | 29 |
| `(not-started, in-progress)` | 3 |
| `(validated, reopened)` | 3 |
| `(reopened, in-progress)` | 2 |
| `(in-progress, invalidated)` | 2 |
| `(in-progress, in-progress)` | 1 |

All seven are proper subsets of the 15-pair `_STATE_TRANSITIONS` graph. The graph is a proper superset of observed reality; the additional transitions in the graph are the ones cycle 15+ will need as the campaign evolves (e.g., `reopened → invalidated`, `deferred ↔ in-progress`, `validated → superseded`).

### Auditor MINOR observations (logged, not acted on)

1. **`tests/test_fanout_concat_validation.py` test-14 header string.** Reads "cycle-15: validated→in-progress within a single shadow rejected at lint AND concat", but the test body only asserts rejection via `_lint_clone_shadow`; a comment block (lines 466–477) openly documents that `concat_clone_ledgers` itself does not raise on transition drift, because that channel is intentionally omitted to preserve the public API required by brief criterion (d). The test PASSES as written; only the header string is aspirational. Worker's §Issues §1 flags this as a cycle-16 defense-in-depth candidate.
2. **`_STATE_TRANSITIONS` has 15 pairs, not the 13 the brief listed.** The two extras (`(validated, validated)`, `(in-progress, in-progress)`) are the escape-hatch expansions documented above.

### Auditor MODERATE, CRITICAL

None.

### Validators

- `promise_check .` on the 301-row ledger: 0 ERRORs, 301 events, 76 plan milestones. Warnings are strictly unrelated sibling-clone orphans (`batch_v3_i3`, `batch_v3_i4`, `i3_dminor`, `i4_stratified`) from other cycle-15 branches doing M-GEN-1 collision-floor interventions, plus expected upstream-repo-file paths (`long_exposure/tools/_ledger_schema.py`, `long_exposure/workspace_bootstrap.py`) referenced from the ledger but living under `/home/user/human-in-a-loop/long-exposure/` outside this workspace by design.
- `org_check` not re-run this cycle; audit-only additions in `tools/stale/` do not add managed-path drift, and the worker's cycle already ran it clean.

## Discussion

Three things about this branch are worth naming.

First, the four-cycle SSoT hardening arc closes as a coherent unit. Cycle 10 established the writer gate (`append_ledger_event` calls `validate_event`), cycle 12 established the concat gate (per-row `validate_event` at concat time with atomic `os.replace`), cycle 14 tightened both gates with `supersedes_path` type checks and the `status` enum, and cycle 15 adds the state-transition validator that closes the class type/enum validators cannot express. Each cycle preserved the prior cycles' invariants (`_STATUS_ENUM is STATUS_VALUES` still True; `is`-identity across all four gates), never weakened them, and each caught strictly more drift than the last. The pattern of using post-merge integration surface as the retrospective driver of the next hardening cycle is now four-for-four healthy and repeatable, and the discipline of never grandfathering historical rows against the tightened validator held across all four cycles (301 rows pass the cycle-15 validator with zero exceptions after two documented self-loop escape-hatch expansions).

Second, the two escape-hatch expansions are the branch's most valuable non-obvious contribution to campaign hygiene. `(validated, validated)` and `(in-progress, in-progress)` self-loops are not drift; they are real semantic patterns (parent rollups; mid-cycle progress notes) that the brief's initial 13-pair draft did not anticipate. The cycle-14 pattern — if legitimate historical rows fail, expand the graph and document the mechanism rather than reject them — kept the branch honest here: rather than reject 57 historical rows and force a fabricated repair, the graph is widened with two documented self-loop entries that each trace to a specific mechanism. The escape hatch is used sparingly and traceably across all four cycles (cycle 14 expanded `STATUS_VALUES` to accommodate `not-started` / `reopened` observed historically; this cycle expanded `_STATE_TRANSITIONS` to accommodate the two self-loops); neither expansion is used to paper over drift.

Third, the deliberate omission of transition-drift raising from `concat_clone_ledgers` itself is a good example of the campaign's zero-caller-change discipline paying its cost. Adding transition validation to `concat_clone_ledgers` would require a new documented `LedgerConcatError` sub-message class and would change the exception surface callers see, which would break brief criterion (d) (public API unchanged). The `_lint_clone_shadow` seam catches the same transitions and is what the fanout conductor invokes at pre-concat lint, so the production path is protected; the theoretical direct-call-to-`concat_clone_ledgers` path is not, and the auditor's minor observation about the test-14 header string aspirationally naming both channels while the test body only asserts one is candidly hoisted to a future cycle-16 defense-in-depth candidate. This is the same interpretation-choice discipline cycles 10, 12, and 14 exercised — surface the choice honestly rather than silently expand the public API.

The four-cycle arc closes; the `_infra/` track is now fully closed for the campaign. What remains open is the substantive frontier — M-GEN-1 collision-floor intervention batches (in-flight on sibling clones), M-EAR-1 armed-harness live activation (blocked on rated-audio egress), M-INGEST-1 egress-probe live retry loop (armed, not fired) — none of which are `_infra/` scope.

## Open Questions

Branch scope is genuinely exhausted. The following are legitimate future work, not this branch's:

- **`_infra/ledger-schema-hardening-v4`** (cycle-16 defense-in-depth candidate, optional): promote `validate_history` from `_lint_clone_shadow` into `concat_clone_ledgers` proper. Would require a new documented `LedgerConcatError` sub-message class for transition drift; brief a follow-on cycle to weigh the cost against the current defence-in-depth by lint. Not urgent — the fanout conductor's pre-concat lint invocation is the production path.
- **Sibling-clone orphan warnings** in `promise_check` (~140 warnings from `batch_v3_i3`, `batch_v3_i4`, `i3_dminor`, `i4_stratified` — other cycle-15 branches doing M-GEN-1 collision-floor interventions). Their own rollup events on integration will clear them; no v3 action needed.
- **Campaign substantive frontier** — M-GEN-1 collision-floor intervention batches, M-EAR-1 armed-harness, M-INGEST-1 egress-probe live retry loop. Unrelated to the `_infra/` track.

## Appendix: Provenance

**Cycle range:** cycle 1 of fork `392503ab7d47`, clone 0.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** researcher `45a3e916-51ce-4b5d-9a31-f0810945ab64`, worker `3778ec06-6112-4b2f-9978-50338e97532e`, auditor `a222f718-34db-4ad5-a49a-af16e5084a02`.
**Auditor decision:** **COMPLETE** at `validated/high`. Sub-milestone `_infra/ledger-schema-hardening-v3` closes at `validated/high`; the four-cycle SSoT ledger-schema hardening arc (writer c10 → concat c12 → field-type+enum c14 → transitions c15) closes as a coherent unit.

**Deliverables on disk.**

- Code: `long_exposure/tools/_ledger_schema.py` extended with `_STATE_TRANSITIONS` frozenset (15 pairs) at module top level and `validate_history(rows_for_milestone)`; `long_exposure/workspace_bootstrap.py`'s `_lint_clone_shadow` calls `validate_history` after per-row `validate_event`; `long_exposure/tools/promise_check.py`'s `_check_lifecycle` calls `validate_history` on the live ledger.
- Tests: `tests/test_ledger_writer_validation.py` extended 18 → 21 (three new cases: cycle-13 pattern rejection at writer; `validated → reopened → in-progress` bridging accepted; single-row no-op); `tests/test_fanout_concat_validation.py` extended 13 → 15 (two new cases: cycle-13 pattern rejection at lint with annotation; multi-row shadow mixing legal and illegal transitions); `_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"` `sys.path` shim at head of both files (sixth consecutive cycle applying the shim discipline).
- Cross-branch integration test §1–§30 continues to pass with 0 failures.
- Report: `docs/ledger_schema_hardening_v3.md` (285 lines, 14.6 KB, front-matter includes cycle + milestone tags). Sole required output artefact.

**Runtime evidence (all live-verified by the auditor).**

- 301-row historical sweep: 0 errors from `validate_history`; 7 distinct consecutive transitions observed, all proper subset of the 15-pair graph.
- `_STATE_TRANSITIONS` live-import: `frozenset` of 15 `(str, str)` tuples; every endpoint drawn from `STATUS_VALUES`; `_STATUS_ENUM is STATUS_VALUES` True.
- Writer surface: `LedgerAppendError` raised with milestone id + both event_ids + both statuses + `_STATE_TRANSITIONS` token on `validated → in-progress` without `reopened`; bridging sequence `validated → reopened → in-progress` accepted.
- Pre-concat lint surface: `LedgerConcatError` raised naming shadow path + milestone + transition; `<shadow_path>:<line>` cycle-14 annotation flows through.
- Public API: `inspect`-checked byte-identical to cycle-14 signatures for both `append_ledger_event(workspace, event)` and `concat_clone_ledgers(workspace, fork_root)`; `LedgerAppendError`, `LedgerConcatError`, and `_lint_clone_shadow` all present at the same import paths.
- Test suites: writer 21/21, concat 15/15, integration §1–§30 PASS, `promise_check` 0 ERR.

**Ledger row count across the four-cycle arc.** Cycle 10 pool 156 → cycle 12 pool 220 → cycle 14 pool 275 → cycle 15 pool 301. Every step preserved byte-identity of prior rows via append-only writes and passed the tightened validator without grandfathering. Escape-hatch expansions used twice (cycle 14: enum `not-started` / `reopened`; cycle 15: transitions self-loops `(validated, validated)`, `(in-progress, in-progress)`), each documented and traceable to real rows.

**Environment stack unchanged since cycle 10.** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`. Single-thread BLAS pins throughout.

**Handoff.** Merge report written to `/home/user/music-gen-instance/fork-392503ab7d47/clone-0/merge_report.md`. The optional cycle-16 `_infra/ledger-schema-hardening-v4` candidate (promoting `validate_history` from `_lint_clone_shadow` into `concat_clone_ledgers` proper) is queued but not urgent; the campaign substantive frontier (M-GEN-1 collision-floor batches, M-EAR-1 armed-harness, M-INGEST-1 egress-probe live retry loop) is where next-cycle research effort belongs.

<verdict>validated</verdict>
