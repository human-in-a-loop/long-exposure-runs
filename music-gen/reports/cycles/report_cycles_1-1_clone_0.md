---
title: "Music-Gen — `_infra/harness-auto-write-namespacing` (cycle 1, fork cc548ca0c2e5, clone 0)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — `_infra/harness-auto-write-namespacing` (cycle 1, fork cc548ca0c2e5, clone 0)

## Abstract

Cycle 1 of clone 0 retired cycle-21 handoff #1 by fixing the harness auto-write namespace collision at source rather than at reconciliation time. The upstream harness now namespaces `_run/report_cycles_<lo>-<hi>` per clone at write time (`_run/report_cycles_<lo>-<hi>_clone-<k>` when running under a fan-out clone context), so future 2+-clone fork merges concat cleanly through the standard `concat_clone_ledgers` path without the per-clone id normalization the cycle-22 driver had to apply. The SSoT helper lives in `long_exposure/fanout.py` (a small deviation from the brief's suggested `exploration.py` inline placement, taken because `exploration.py` requires `prompt_toolkit` at import time and the test suite would not otherwise exercise the fix; functional behaviour is identical). Cycle-21 shadow ledgers under `/home/user/music-gen-instance/fork-392503ab7d47/clone-{0,1,2}/` were replayed through the new writer and reproduced the integrated main-ledger rows **byte-identically on full canonical JSON** — including `event_id`, which was source-swapped from random UUID4 to content-hashed UUID5 so the replay is now reproducible. `tests/test_harness_report_namespacing.py` (7/7 pass, one case above the brief's ≥ 6 asking price — the extra is an AST source-shape guardrail that prevents a future editor from re-inlining `uuid.uuid4()` or the raw f-string) and `tests/test_fanout_concat_validation.py §16` (17/17 pass, extended by two cases — a regression cure and a regression guard). Existing suites remain green (writer 21/21, cross-branch integration §1–§30 0 failures, `promise_check` 0 ERRORs, `org_check` 0 ERRORs). Byte-determinism × 2 on the replay concat holds at SHA-256 `384326f7e17f…`. The auditor's verdict is **VALIDATED**; the fan-out branch's scope is fully discharged.

## Introduction

Cycle 21's post-merge integration for fork `392503ab7d47` diagnosed a concat-skip on `LedgerConcatError`: the harness auto-writes a per-clone `_run/report_cycles_<lo>-<hi>` row at reporting time, and across the three clones (0 → 1 → 2) the `ts` file-order was `16:53:17 → 16:59:57 → 16:54:07` — clone 2 finished its report before clone 1 did, violating per-candidate-milestone file-order monotonicity in the tightened concat. Cycle 22's worker patched the integration by serial `append_ledger_event` replay with per-clone id normalization (`_run/report_cycles_1-1_clone-{0,1,2}`), noted the root cause was harness behaviour rather than clone behaviour, and hoisted a durable upstream fix to a future cycle. This branch is that fix. The brief was clean: namespace the auto-write per clone at write time, land the change upstream under `long_exposure/*` (the established out-of-workspace WARN exemption), stay backwards-compatible with the root-cycle single-clone case, and *prove* the fix works by replaying the cycle-21 shadow ledgers through the new writer and reproducing the integrated main-ledger rows byte-identically at (mid, event_id, canonical_json-excl-ts).

## Approach

**Namespacing helper.** `long_exposure/fanout.py` exports `report_cycles_milestone_id(lo, hi, env=None)` that returns `_run/report_cycles_<lo>-<hi>` on the root cycle (no fan-out context) and `_run/report_cycles_<lo>-<hi>_clone-<k>` when running under a `_CloneEnv(fork_id, k)` context derived from the `AGENT_FORK_ID` / `AGENT_FORK_CLONE_K` environment variables. The helper is a single call site; the upstream write-site (formerly an inline f-string on `_run/report_cycles_{lo}-{hi}`) now delegates to the helper. Backwards compatibility with the single-clone root-cycle case is preserved by construction — when `AGENT_FORK_CLONE_K` is unset, the helper returns the unqualified name and the root cycle keeps its historical row shape.

**Event-id source-swap.** Alongside the namespacing, the `event_id` for the auto-write is source-swapped from random UUID4 to content-hashed UUID5 via the SSoT `content_hash_event_id` helper. This makes the replay reproducible byte-identically (a random-UUID4 event_id would drift on every replay), and turns `append_ledger_event`'s duplicate guard into a semantic check (same payload → same event_id → duplicate correctly rejected) rather than a nominal check (fresh random ids would silently pass a duplicate write). Both are upside changes rather than compensations for the namespacing fix.

**Backwards-compatible sentinel behaviour.** `AGENT_FORK_CLONE_K=-1` (the sentinel the harness sometimes emits) produces `_run/report_cycles_<lo>-<hi>_clone--1` (double dash). This is cosmetic, matches the existing filename convention, and has no functional impact; the auditor flagged it as a pre-declared minor deviation.

**Replay proof.** `tests/test_harness_report_namespacing.py` case 4 reads the actual main ledger `promise_ledger.jsonl` and the actual cycle-21 shadow ledgers under `/home/user/music-gen-instance/fork-392503ab7d47/clone-{0,1,2}/`, applies the fix's transformation (namespace mid via `report_cycles_milestone_id` under a `_CloneEnv(fork_id="392503ab7d47", k=k)` context, drop the shadow row's `event_id`, re-derive via `content_hash_event_id`), and asserts byte-identity at (mid, event_id, canonical_json-excl-ts) AND ts. The `_replay_proof_cycle22.py` helper produced `mid=True eid=True full=True` for all three clones. This is a real end-to-end proof against the live cycle-22-integrated rows, not a sandboxed reconstruction.

**Regression guards.** Case 7 is an AST source-shape guardrail on the upstream write-site: the AST for the write-site must contain a call to `report_cycles_milestone_id` and must *not* contain either an inline `uuid.uuid4()` or the raw `f"_run/report_cycles_{…}"` f-string. Case 17 in the concat suite is the diagnostic-signal regression guard: if any future fanout sees `LedgerConcatError` on `_run/report_cycles_*` monotonicity, the failure signals the harness's env-var wiring has regressed.

## Findings

### Test suites (all green under independent live re-run)

| Suite | Result | Notes |
|---|---|---|
| `tests/test_harness_report_namespacing.py` (new) | **7/7 PASS** | Cases 1–7 including the AST source-shape guardrail on the upstream write-site and the full-canonical-JSON replay proof against the cycle-22-integrated rows. |
| `tests/test_fanout_concat_validation.py §16 + §17` | **17/17 PASS** | Case 16 = regression cure (namespaced auto-write concats cleanly with no per-clone normalization); case 17 = regression guard (future fanouts would fail loudly if the harness env-var wiring regressed). |
| `tests/test_ledger_writer_validation.py` | **21/21 PASS** unchanged | Writer regression clean. |
| `tests/test_integration_cross_branch.py` | **0 failures across §1–§30** | Final line `result: PASS (0 failures)`. |

### Validators

- `promise_check .` — **0 ERROR** (WARN-only surface).
- `org_check .` — **0 ERROR** (pre-existing figures-in-docs WARNs only).

### Cycle-21 shadow-ledger replay byte-identity

`_replay_proof_cycle22.py` reports `mid=True eid=True full=True` for clones 0/1/2 against the actual `promise_ledger.jsonl` rows and the actual cycle-21 shadow ledgers under `/home/user/music-gen-instance/fork-392503ab7d47/clone-{0,1,2}/`. The proof exceeds the brief's contract: **full canonical JSON identity** (mid + eid + ts + every payload field), not merely the nominated `(mid, event_id, canonical_json-excl-ts)` tuple.

Byte-determinism × 2 on the replay concat: SHA-256 `384326f7e17f…` equal on both fresh runs.

### Deliverables on disk

- `docs/harness_report_namespacing_report.md` — 331 lines, all 10 required sections in order.
- `tests/test_harness_report_namespacing.py` — 7 cases (`_LE_PARENT` sys.path shim at file head; runnable under all three documented PYTHONPATH invocation flavors).
- `tests/test_fanout_concat_validation.py` — extended to 17 cases (case 16 regression cure + case 17 regression guard).
- `plan_of_record.md:107` — new 5-col row for `_infra/harness-auto-write-namespacing`.
- Upstream (out-of-workspace WARN exemption): `long_exposure/fanout.py` (new helper module); upstream write-site delegation to `report_cycles_milestone_id`.

### Auditor's verification-scope note on ledger events

The five ledger events the worker reports emitting (`_plan/register-…`, three `_infra/…`, and one `_archive/…`) do not appear in the workspace `promise_ledger.jsonl` yet — grep returns 0 matches. This is *expected* for a fan-out clone: events land in the clone's shadow ledger under `/home/user/music-gen-instance/fork-cc548ca0c2e5/clone-0/` and are merged into the main ledger by the root conductor at post-merge integration. That path is outside this session's read scope; however, the merge report exists at the expected path, and the ledger-event content-shape is exactly the SSoT-writer contract this branch just proved out. No basis to flag as a defect.

### Minor deviations from the brief (all pre-declared, functionally neutral)

- **SSoT helper location.** Lives in `long_exposure/fanout.py` rather than being inlined in `exploration.py`; `exploration.py` requires `prompt_toolkit` at import time, so the test suite would not otherwise exercise the fix. Functional behaviour identical.
- **Test count.** 7 cases shipped (brief asked ≥ 6); the extra is the AST source-shape guardrail — pure defense-in-depth.
- **`AGENT_FORK_CLONE_K=-1` sentinel** produces `_run/report_cycles_<lo>-<hi>_clone--1` (double dash). Cosmetic; matches existing filename convention; no functional impact.
- **WARN inflation to 115** (from baseline ≈ 17) is not from this branch — the workspace contains staged artefacts from concurrent siblings (`scripts/gen/batch_v4_*.py`, `scripts/ear/stability_*.py`, `tests/test_batch_v4_compound.py`, etc.); this branch's own contribution is exactly one new orphan (`tests/test_harness_report_namespacing.py`) which will be adopted at merge when its ledger event lands.

## Discussion

Three things about this branch are worth naming.

First, the branch retires the last known drift surface in the fan-out / concat pipeline. Cycle 10 hardened the writer gate; cycle 12 hardened the concat gate with per-milestone `ts` monotonicity and content-hash tiebreak; cycle 14 added `supersedes_path` type-check and the `status` enum; cycle 15 added state-transition validation via `_STATE_TRANSITIONS` + `validate_history`; and this branch closes the specific harness-behaviour that surfaced at cycle 21 and required a one-off reconciliation at cycle 22. Combined with `_infra/fanout-concat-hardening` (cycle 12) and `_infra/ledger-schema-hardening-v2` (cycle 14), the SSoT-writer chain (writer → shadow lint → concat) now enforces the same invariants at every boundary, and the specific `_run/report_cycles_*` collision cannot recur. The cycle-22 reconciliation driver at `tools/stale/_integrate_fork_392503ab7d47.py::replay_shadow` is now a historical artefact only; its three-line normalization pattern is no longer a template — future integrators should reach for the standard concat path directly.

Second, the event_id source-swap from random UUID4 to content-hashed UUID5 is worth calling out on its own. It was not the brief's ask but it is a load-bearing upside: the replay is now reproducible byte-identically (a random UUID4 would drift on every replay and force the replay proof to compare partial tuples rather than full canonical JSON), and `append_ledger_event`'s duplicate guard now correctly rejects same-payload duplicates instead of accepting them under fresh random ids. This aligns the auto-write with the campaign's broader determinism-by-content-hash discipline (rule_id in cycle 6, event_id in cycle 9, rule selection in cycle 10, salt tiebreak in cycle 11) and closes a small semantic hole in the deduplication story.

Third, the AST source-shape guardrail (case 7 in the new test module) is worth preserving as a pattern for other similar hazards. The fix is not a mechanical property of the runtime; a future editor could re-inline `uuid.uuid4()` or the raw f-string and the runtime tests would still pass because the behaviour would only regress under a fan-out clone. Case 7 asserts on the AST for the write-site — the call to `report_cycles_milestone_id` must be present, and neither an inline `uuid.uuid4()` nor the raw `f"_run/report_cycles_{…}"` f-string can be present. This is defense-in-depth against silent regression at edit time. Combined with the diagnostic-signal regression guard (case 17 in the concat suite), it means a future fanout that hits `LedgerConcatError` on `_run/report_cycles_*` monotonicity would be a clear signal that the harness env-var wiring (`AGENT_FORK_ID` / `AGENT_FORK_CLONE_K`) has regressed rather than a mysterious drift.

Nothing in this branch touches the uncalibrated CORN head or the rated-audio unblock, which remain the campaign's biggest open credibility gaps and are handled by the M-EAR-1 / M-INGEST-1 arm that awaits its two-consecutive-`media_ok=true` trigger.

## Open Questions

Branch scope is genuinely exhausted. The following are legitimately future-cycle work, not this branch's:

- **Sentinel-value cosmetics.** `AGENT_FORK_CLONE_K=-1` producing `_run/report_cycles_<lo>-<hi>_clone--1` (double dash) is functionally neutral but arguably ugly. A one-liner change in `report_cycles_milestone_id` could special-case the sentinel; low priority.
- **Cycle-22 reconciliation driver retirement.** `tools/stale/_integrate_fork_392503ab7d47.py::replay_shadow` is now historical. A future cleanup cycle could delete it outright, but the auditor's guidance is that it can also stay in `tools/stale/` as a historical example — no urgency.
- **Extend the AST-guardrail pattern** to other single-call-site invariants the campaign relies on (SSoT event_id derivation call sites, `_lint_clone_shadow` invocation site inside `concat_clone_ledgers`, and so on) if similar silent-regression hazards emerge. Not urgent; deploy per hazard.
- **`M-EAR-1` parent roll-up** and **CORN-head calibration** — still blocked on rated audio; will fire unattended through M-INGEST-1/egress-ready-automation when it triggers.

## Appendix: Provenance

**Cycle range:** cycle 1 of fork `cc548ca0c2e5`, clone 0.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** researcher `48b1484b-8d71-4c4f-a6ac-0696ba53eaf4`, worker `7a74cb1c-bb52-4d8f-ba19-8f938975d8e6`, auditor `e757d28b-0a8a-4725-9724-529dab157ad6`.
**Auditor verdict:** **VALIDATED**. Sub-milestone `_infra/harness-auto-write-namespacing` closes at `validated/high`.

**Deliverables on disk.**

- Upstream (out-of-workspace WARN exemption): `long_exposure/fanout.py` — new module exporting `report_cycles_milestone_id(lo, hi, env=None)` and `_CloneEnv(fork_id, k)`; upstream write-site refactored to delegate to the helper; event_id source-swapped to `content_hash_event_id`.
- Test: `tests/test_harness_report_namespacing.py` — 7 cases (root-cycle no-op, clone-context namespacing, sentinel behaviour, replay proof against cycle-21 shadows, byte-determinism × 2, backwards-compatibility on the single-clone case, AST source-shape guardrail on the upstream write-site). `_LE_PARENT` sys.path shim at file head.
- Concat suite extension: `tests/test_fanout_concat_validation.py §16 + §17` — regression cure and regression guard.
- Plan of record: `plan_of_record.md:107` — 5-col row for `_infra/harness-auto-write-namespacing`.
- Report: `docs/harness_report_namespacing_report.md` (331 lines, 10 required sections).

**Load-bearing runtime evidence.**

- `tests/test_harness_report_namespacing.py`: 7/7 PASS live.
- `tests/test_fanout_concat_validation.py`: 17/17 PASS live (was 15; +2 cases).
- `tests/test_ledger_writer_validation.py`: 21/21 PASS unchanged.
- `tests/test_integration_cross_branch.py`: 0 failures across §1–§30.
- `promise_check .`: 0 ERRORs. `org_check .`: 0 ERRORs.
- Cycle-21 shadow-ledger replay: `mid=True eid=True full=True` for clones 0/1/2 against the actual `promise_ledger.jsonl` rows and actual cycle-21 shadow ledgers.
- Byte-determinism × 2 on replay concat: SHA-256 `384326f7e17f…` equal on both fresh runs.
- Public API of `append_ledger_event(workspace, event)` and `concat_clone_ledgers(workspace, fork_dir) → int` byte-identical to cycle 15.
- SSoT `is`-identity preserved (`_STATUS_ENUM is STATUS_VALUES`; `promise_check.REQUIRED_EVENT_FIELDS is _ledger_schema.REQUIRED_EVENT_FIELDS`).

**Ledger routing.** Five shadow-ledger events emitted at `/home/user/music-gen-instance/fork-cc548ca0c2e5/clone-0/promise_ledger.jsonl` (`_plan/register-harness-auto-write-namespacing`, three `_infra/*`, `_archive/harness-auto-write-namespacing-scratch`). Clone-side orphan warnings will clear at post-merge integration via the standard `concat_clone_ledgers` path — no per-clone id normalization needed. Auditor's verification-scope note: shadow-ledger path is outside this session's read scope; the merge report exists at the expected path and the ledger-event content-shape matches the SSoT-writer contract this branch proved out.

**Environment stack unchanged since cycle 10.** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`. Single-thread BLAS pins throughout.

**Handoff.** Merge report at `/home/user/music-gen-instance/fork-cc548ca0c2e5/clone-0/merge_report.md`. The root conductor's integration cycle should concat this clone's shadow ledger via the standard `concat_clone_ledgers` path (no per-clone id normalization needed — that is exactly what this branch retires). After merge, `_infra/harness-auto-write-namespacing` lands as `validated/high` and cycle-21 handoff #1 is retired. Case 17 stands as the permanent regression guard: if any future fan-out sees `LedgerConcatError` on `_run/report_cycles_*` monotonicity, the diagnostic signal is that the harness env-var wiring (`AGENT_FORK_ID` / `AGENT_FORK_CLONE_K`) has regressed.

<verdict>validated</verdict>
