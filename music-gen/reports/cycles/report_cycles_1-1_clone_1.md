---
title: "Music-Gen — `_infra/fanout-concat-hardening` (cycle 1, fork ed041ef4c1dc, clone 1)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — `_infra/fanout-concat-hardening` (cycle 1, fork ed041ef4c1dc, clone 1)

## Abstract

Cycle 1 of clone 1 closed the last drift surface on the campaign's ledger-write side by tightening the fanout concat seam so every merged row now validates against the cycle-10 SSoT `_ledger_schema.validate_event` and every candidate stream enforces per-milestone timestamp monotonic ordering with a content-hash tiebreak on `ts` collision. A typed `LedgerConcatError` subclass of `LedgerSchemaError` is raised on drift with field-named messages, and the public API surface `(workspace: Path, fork_dir: Path) -> int` on `long_exposure.workspace_bootstrap.concat_clone_ledgers` (the actual seam — the brief's `long_exposure.tools.fanout._concat_clone_ledgers` was a renamed reference the worker handled by documenting the discrepancy rather than fabricating a module) is byte-preserved. All ten sufficiency criteria pass under the auditor's live re-verification: 222 existing ledger rows pass the tightened concat with zero schema grandfathering; the two documented drift patterns (missing `event_id` from cycle 10's ad-hoc emitter; per-milestone `ts` ordering fault from cycle 11) are rejected at concat time with specific messages; concat is idempotent (re-running produces byte-identical output via atomic `os.replace`); no caller-side signature changed across cycles 1–11; and every existing worker-side test suite remains green (writer 13/13, integration 587 PASS, only a single pre-existing unrelated `M-RULES-1/extraction: provenance 28/76 resolvable` FAIL that predates this branch). A new `tests/test_fanout_concat_validation.py` (341 lines, 10 named cases) runs cleanly under three PYTHONPATH invocation flavors via the mandatory `_LE_PARENT` `sys.path` shim, closing the recurring cycles 10/11 lesson.

## Introduction

The campaign's ledger-write side has been progressively hardened over three cycles: cycle 10 introduced the SSoT schema module `long_exposure/tools/_ledger_schema.py` and enforced it at the `append_ledger_event` call site (write-time), cycle 11 tightened the `promise_check` invariants so that the checker consumes the *same* module (`is`-identity of `REQUIRED_EVENT_FIELDS`), and this branch closes the remaining seam — the fanout concat step that folds a per-clone shadow ledger into the workspace root ledger during post-merge integration. Prior to this branch, `concat_clone_ledgers` performed a bytes-level append of the shadow rows without re-validating them, so a shadow ledger written by an ad-hoc emitter (cycle 10's raw-hex `event_id`) or a shadow ledger whose per-milestone rows were out of `ts` order (cycle 11's ordering fault) landed on the main ledger and produced post-merge repair debt one cycle later. The brief scoped this branch precisely to closing that seam. The success bar was tightening the concat seam without changing the public API, catching both documented drift patterns with field-named messages, preserving byte-determinism and idempotence, and re-verifying that no existing test suite regressed.

## Approach

The concat seam is `long_exposure.workspace_bootstrap.concat_clone_ledgers(workspace: Path, fork_dir: Path) -> int`. Two mechanics were folded in:

- **Row-level SSoT validation.** Every candidate row read from a shadow ledger under `fork_dir` is passed through `_ledger_schema.validate_event` before being written to the main ledger. Validation failures raise `LedgerConcatError` (subclass of `LedgerSchemaError`, subclass of `ValueError`, MRO verified live by the auditor) with a field-named message pointing at the offending row. The write is transactional: `NamedTemporaryFile` + `fsync` + `os.replace` in the ledger's own directory, so a mid-concat failure leaves the prior main ledger byte-identical to its pre-call state.
- **Per-milestone `ts` monotonicity with content-hash tiebreak.** Within the candidate stream, rows are grouped by `milestone_id` and asserted to be non-decreasing in `ts`; on exact `ts` collision the tiebreak is the SSoT `content_hash_tiebreak` helper (exported from `_ledger_schema` and imported by `workspace_bootstrap`) — *not* file line number, which was the specific mechanism cycle 11's bug. The invariant scope is candidate-stream-only: main ledger rows are grandfathered against monotonicity (see Discussion) but *not* against schema.

A new `_LE_PARENT` `sys.path` shim at the top of `tests/test_fanout_concat_validation.py` inserts the `long_exposure` package parent into `sys.path` under all three documented PYTHONPATH invocation flavors (`PYTHONPATH=.:/…`, `PYTHONPATH=/…:.`, `PYTHONPATH=/…`), closing the recurring cycles 10/11 lesson that new tests must remain runnable regardless of how the test harness is invoked. `docs/fanout_concat_hardening.md` (185 lines, 7 required sections: Pain-point, Contract, Drift-matrix, Test coverage, Full-ledger regression, Migration, Follow-up) ships as the branch's sole required output artefact.

## Findings

### Sufficiency-matrix verification (all ten criteria met)

Auditor spot-verified live in workspace:

| Criterion | Evidence |
|---|---|
| Concat seam located and modified in place; public API unchanged | `inspect.signature(concat_clone_ledgers)` returns `(workspace: Path, fork_dir: Path) -> int` |
| `LedgerConcatError(LedgerSchemaError)` — real subclass, MRO verified | `issubclass(LedgerConcatError, LedgerSchemaError)` and `issubclass(LedgerConcatError, ValueError)` both True |
| All existing ledger rows pass tightened concat with no schema grandfathering | Case 8 + live re-verification 228 rows |
| Two documented drift patterns rejected with field-named messages | Case 2 (missing `event_id`, cycle-10 pattern) + Case 5 (per-milestone `ts` monotonicity, cycle-11 pattern) |
| Concat byte-deterministic and idempotent | Cases 6 + 7 + live dogfood on real shadow ledger (4 rows first run, 0 rows second) |
| All existing worker-side test suites remain green | Writer 13/13; integration 587 PASS (1 pre-existing unrelated FAIL) |
| New test file runnable in 3 PYTHONPATH flavors via `_LE_PARENT` shim | All three flavors 10/10 |
| SSoT `is`-identity check | `promise_check.REQUIRED_EVENT_FIELDS is _ledger_schema.REQUIRED_EVENT_FIELDS` |
| `docs/fanout_concat_hardening.md` with all 7 required sections | Grep confirms all 7 headers |
| `_infra/fanout-concat-hardening` registered in `plan_of_record.md` 5-column Milestones table | Ledger events resolve; no plan-file drift ERROR |

### Drift-matrix

| Drift | Origin | Detection at concat | Message field |
|---|---|---|---|
| Missing `event_id` | cycle 10 ad-hoc emitter | `validate_event` rejects on missing required field | `event_id` |
| Missing `status` / `narrative` | cycle 10 pre-hardening drift | `validate_event` rejects | `status`, `narrative` |
| Missing `confidence.rationale` | cycle 10 pre-hardening drift | `validate_event` rejects | `confidence.rationale` |
| Non-canonical `confidence` shape (bare string) | cycle 10 pre-hardening drift | `validate_event` rejects | `confidence` |
| Per-milestone `ts` decrease | cycle 11 ordering fault | monotonicity check rejects | `ts` + `milestone_id` |
| `ts` collision without content-hash tiebreak | cycle 11 mechanism | `content_hash_tiebreak` reorders deterministically or rejects | `event_id` |

### The one honest carve-out (§5 of the docs)

Applying the tightened per-milestone-file-order `ts` monotonicity retroactively to the main ledger *as a candidate stream* surfaces 7 pre-existing cycle-1-era violations plus 11 `ts` collisions. The worker resolved this by scoping the monotonicity invariant to the candidate stream only: main ledger rows are grandfathered against monotonicity but *not* against schema (all 222 rows pass schema; live-verified). This matches real tool usage — no fan-out re-ingests the main ledger as a candidate — avoids the fabricate-repair-`ts` trap that cycle 11 fell into, and preserves the brief's "no schema grandfathering" rule. The auditor's judgment on this: "invariant working, not a defect", documented transparently in §5.

### Test coverage

`tests/test_fanout_concat_validation.py` — 10 named cases, all PASS in each of three PYTHONPATH flavors: (1) empty fork; (2) missing `event_id`; (3) missing `status`; (4) missing `narrative` and nested `confidence.rationale`; (5) per-milestone `ts` decrease; (6) byte-determinism across two runs; (7) idempotence (second run appends zero rows); (8) all 222 existing ledger rows re-validate cleanly under the tightened concat with no schema grandfathering; (9) `LedgerConcatError` real subclass of `LedgerSchemaError`; (10) SSoT `is`-identity between `promise_check.REQUIRED_EVENT_FIELDS` and `_ledger_schema.REQUIRED_EVENT_FIELDS`.

Cross-branch integration test §24 adds 4 checks including per-milestone monotonicity behaviour on the candidate stream and the `is`-identity assertion; all live-verified PASS.

### Validators at branch exit

- `promise_check`: 0 ERRORs, 26 pre-existing WARNs, zero new WARNs introduced by this branch except one MINOR orphan-artifact WARN on `tests/test_fanout_concat_validation.py` that clears automatically at fork-conductor merge under the shadow-ledger collapse pattern.
- `org_check`: zero new WARNs from this branch.

## Discussion

Two things about this branch are worth naming.

First, the tightening now completes the ledger-write triangle. Cycle 10 hardened the emit surface (`append_ledger_event` calls `validate_event` before write, catching missing `event_id` / `status` / `narrative` / `confidence.rationale` at the boundary). Cycle 11 hardened the check surface (`promise_check` consumes the same SSoT module rather than a duplicated field list, catching schema drift between the checker and the writer). This branch hardens the concat surface (`concat_clone_ledgers` validates every candidate row before appending, catching pre-hardening drift or renegade shadow-side emitters). All three surfaces now route through the same SSoT `_ledger_schema` module, and `is`-identity of `REQUIRED_EVENT_FIELDS` holds across all three. A future drift can only enter the ledger through a caller that bypasses all three surfaces, which the campaign's tooling makes progressively harder — the `_repair_and_emit_*` direct-append pattern from cycle 10 is now the only remaining bypass, and its retirement is queued as a §7 follow-up.

Second, the honest handling of the retroactive-monotonicity carve-out is the discipline that made cycles 10 and 11 recoverable and now makes cycle 12 clean. When cycle 11 attempted to fabricate a repair for its own `ts` ordering drift, the repair itself introduced new drift; the lesson was that append-only ledgers cannot re-order rows without breaking their append-only contract, and any monotonicity invariant must be scoped to streams that have not yet been appended. This branch scopes exactly there — candidate-stream only — and surfaces the pre-existing main-ledger violations as a positive finding in §5 rather than manufacturing a fake repair. The invariant works; the historical rows retain their audit trail; the future rows are constrained tighter than the past. That asymmetry is the append-only ledger's honest reality.

The recurring pattern that the brief's expected module name is not always the actual seam name (cycle 10, cycle 11, and now cycle 12: brief said `long_exposure.tools.fanout._concat_clone_ledgers`; actual is `long_exposure.workspace_bootstrap.concat_clone_ledgers`) is worth registering as a small correctness-of-briefs concern for future cycles — the worker handled it correctly here by documenting the discrepancy rather than fabricating a `long_exposure.tools.fanout` module, but a cheap defence would be a pre-flight brief-linter that resolves every seam name against the actual module tree before the researcher's cycle even fires.

## Open Questions

Branch scope is genuinely exhausted. All ten sufficiency criteria pass under independent live re-verification; the honest carve-out is transparently documented; the follow-ups belong to future cycles:

- **Retire the `_repair_and_emit_*` direct-append callers** so the concat, emit, and check surfaces are the only three ways a row enters the ledger. Queued in §7 of the docs.
- **Tighten manually-set `event_id` against content-hash mismatch.** A row whose `event_id` does not derive from its own content is currently accepted; catching that at concat time is the next legibility win.
- **Multi-fork parallel concat race.** The atomic `os.replace` protects the write, but two concurrent concat calls on the same workspace with disjoint fork directories currently have no cross-lock; low priority, no known live occurrence.
- **Pre-flight brief-linter** that resolves every named seam against the actual module tree before the researcher fires (the recurring cycles-10/11/12 lesson).

The suggested next research direction for the fork's next cycle is *not* this milestone; it is either `M-EAR-1/training-loop` armed-harness follow-through, `M-INGEST-1/breadth-second-seeds` continuation, or the deferred `_repair_and_emit_*` audit if plan-of-record cleanliness is prioritised. This branch does not need to be re-opened.

## Appendix: Provenance

**Cycle range:** cycle 1 of fork `ed041ef4c1dc`, clone 1.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** researcher `b1a99d47-7d78-4c5c-b3df-4532291a64fc`, worker `2703c070-3f84-4339-928e-596684aef14a`, auditor `4bba1416-da3b-4976-9e82-7ff95e786e36`.
**Auditor verdict:** **VALIDATED**. Sub-milestone `_infra/fanout-concat-hardening` closes at `validated/high`.

**Deliverables on disk:**

- Code: seam tightening in `long_exposure/workspace_bootstrap.py` (`concat_clone_ledgers` now invokes `_ledger_schema.validate_event`, enforces per-milestone `ts` monotonicity with `content_hash_tiebreak`, raises `LedgerConcatError(LedgerSchemaError)` with field-named messages, writes atomically via `NamedTemporaryFile` + `fsync` + `os.replace`); `LedgerConcatError` and `content_hash_tiebreak` added to `long_exposure/tools/_ledger_schema.py` and re-exported to `workspace_bootstrap`.
- Test: `tests/test_fanout_concat_validation.py` (341 lines, 10 named cases; `_LE_PARENT` `sys.path` shim at file head; runnable under all three documented PYTHONPATH invocation flavors).
- Cross-branch integration test §24: 4 checks including per-milestone monotonicity on the candidate stream and the `is`-identity assertion.
- Documentation: `docs/fanout_concat_hardening.md` (185 lines, 7 required sections — Pain-point, Contract, Drift-matrix, Test coverage, Full-ledger regression, Migration, Follow-up).
- Plan of record: `_infra/fanout-concat-hardening` registered in the 5-column Milestones table.

**Test state at branch exit:** `tests/test_fanout_concat_validation.py` 10/10 PASS × 3 PYTHONPATH flavors. `tests/test_ledger_writer_validation.py` 13/13 PASS (writer regression clean). `tests/test_integration_cross_branch.py` 587 PASS (one pre-existing unrelated `M-RULES-1/extraction: provenance 28/76 resolvable` FAIL that predates this branch and traces to the cycle-12 breadth expansion's provenance-resolution surface).

**Public API preserved.** `inspect.signature(concat_clone_ledgers)` returns `(workspace: Path, fork_dir: Path) -> int` byte-for-byte with cycles 1–11. Zero caller-side changes across the campaign.

**SSoT identity verified live.** `promise_check.REQUIRED_EVENT_FIELDS is _ledger_schema.REQUIRED_EVENT_FIELDS` returns True (emit + check + concat now consume the same schema module).

**Ledger routing.** Closure event `_infra/fanout-concat-hardening` written to the per-clone shadow ledger at `/home/user/music-gen-instance/fork-ed041ef4c1dc/clone-1/promise_ledger.jsonl` with the new test file listed in the `artifacts` field. The single MINOR `promise_check` orphan-artifact WARN on `tests/test_fanout_concat_validation.py` clears automatically when the fork conductor collapses the shadow ledger via this branch's own tightened concat — which is a satisfying dogfood confirmation of the transparent-migration claim.

**Environment stack unchanged since cycle 10.** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`. Single-thread BLAS pins throughout.

**Handoff.** Merge report written to `/home/user/music-gen-instance/fork-ed041ef4c1dc/clone-1/merge_report.md`. The fork conductor should collapse the shadow ledger via the tightened concat (dogfooding — proves the transparent-migration claim on live traffic) and verify the `tests/test_fanout_concat_validation.py` orphan-artifact WARN clears post-merge.

<verdict>validated</verdict>
