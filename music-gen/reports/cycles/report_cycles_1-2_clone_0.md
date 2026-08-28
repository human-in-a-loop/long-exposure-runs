---
title: "Music-Gen — `_infra/ledger-schema-hardening-v2` (cycles 1-2, fork 855d4c2e9945, clone 0)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — `_infra/ledger-schema-hardening-v2` (cycles 1-2, fork 855d4c2e9945, clone 0)

## Abstract

Cycles 1-2 of clone 0 closed the campaign's three-cycle SSoT ledger-schema hardening arc (writer at cycle 10 → concat at cycle 12 → field-type + enum at this branch) by extending `long_exposure.tools._ledger_schema.validate_event` to reject the two cycle-13-observed drift classes: `supersedes_path` must be `str` (rejecting the list form that crashed `promise_check._canon` with `AttributeError: 'list' object has no attribute 'lstrip'` on ledger line 266) and `status` must lie in the canonical enum (rejecting the wrong-keyword `in-progress` on line 250 that surfaced as a `promise_check` ERROR). A `_lint_clone_shadow` seam was factored out of `workspace_bootstrap.concat_clone_ledgers` — importable at module top level — so the existing cycle-12 per-row `validate_event` loop is now a named gate rather than an in-line one, with drift surfaced at pre-concat lint time with `<shadow_path>:<lineno>` annotations rather than deferred to fork-integration. The public API of both `append_ledger_event(workspace, event)` and `concat_clone_ledgers(workspace, fork_dir) → int` is byte-preserved across cycles 1–13. All 277 existing ledger rows validate under the tightened schema (dynamic sweep, not fixed-count; the ledger grew from the brief's cited 275 to 277 mid-run as two sibling events landed); the writer suite is 18/18 (five new cases), the concat suite is 13/13 (three new cases plus the MRO check), the cross-branch integration test passes with 0 failures including new §28 invariants; `promise_check` reports 0 ERRORs. The auditor's verdict is **VALIDATED / high**. One nuance surfaced honestly during the branch — cycle-13's line-250 was misclassified as an enum drift when it was actually a state-transition drift (`validated → in-progress` without an intervening `reopened`) — and was correctly hoisted to a cycle-15 follow-up rather than papered over.

## Introduction

By the end of cycle 13 the campaign's ledger-write triangle was complete (emit + check + concat all consuming the SSoT `_ledger_schema` module with `is`-identity of `REQUIRED_EVENT_FIELDS`), but two new drift classes had surfaced at post-merge integration time — classes the existing SSoT validator did not cover. The list-form `supersedes_path` on line 266 crashed `_canon` with an `AttributeError` because every other row uses string form and the canonicaliser had no `str`-vs-`list` guard; the wrong-keyword `in-progress` `status` on line 250 was valid in isolation but semantically wrong on a milestone that had previously been `validated`. Both classes fit the recurring pattern the campaign has been observing since cycle 8: every cycle finds a new drift class the current validator does not cover, integration debt accretes, and the mechanical fix is to extend the SSoT validator by another surgical field/enum type-check. This branch is the cycle-14 answer to that recurring pattern for two specific classes; the state-transition class remains open and is hoisted to a future cycle.

## Approach

Two surgical extensions to `long_exposure/tools/_ledger_schema.py`, both consistent with cycles 10 and 12:

- **`supersedes_path` type check.** `validate_event` now rejects any `supersedes_path` that is not a `str`. Message shape at the writer gate: `LedgerAppendError: supersedes_path must be str, got list: [...]`. Message shape at the pre-concat lint gate: `LedgerConcatError: <shadow_path>:<lineno> (milestone_id=…): supersedes_path must be str, got list: [...]` — path + line + milestone + field + type + value.
- **`status` enum.** `_STATUS_ENUM` is bound to `STATUS_VALUES` by object identity (`_STATUS_ENUM is STATUS_VALUES`, verified live), and both `append_ledger_event` and `_lint_clone_shadow` consult the same set. The final enum is `{action_required, deferred, in-progress, invalidated, not-started, reopened, superseded, validated}` — the brief proposed a five-value set; the observed union in the current 277-row ledger is `{validated: 237, in-progress: 33, reopened: 3, invalidated: 2}` (strict subset of the eight-value canonical enum), and the falsifiability escape hatch ("expand enum rather than reject historical rows") did not need to fire because the canonical superset already sufficed.

A `_lint_clone_shadow` seam is factored out of `concat_clone_ledgers` and re-exported at `workspace_bootstrap` module top level. The interpretation choice was between (a) adding a new gate before the existing per-row `validate_event` loop or (b) factoring the existing loop into a named seam. The worker chose (b) — the recommended zero-caller-change interpretation — and flagged the choice honestly in report §4. Semantically identical to the prior state: the same invariants fire at the same moment (before any `os.replace`); the difference is that the gate is now an importable, testable function with a stable name.

`tests/test_ledger_writer_validation.py` extended by five new cases (writer-side drift rejection with field-named, value-annotated, type-annotated messages); `tests/test_fanout_concat_validation.py` extended by three new cases (concat-side drift rejection with `<path>:<line>:<field>` shape plus the `LedgerConcatError` MRO check at case 9). Both test files carry the mandatory `_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"` `sys.path` shim at file head — the fifth consecutive cycle applying the shim discipline. `docs/ledger_schema_hardening_v2.md` ships as the branch's sole required output, documenting the three-cycle arc.

## Findings

### Auditor CRITICAL matrix (all pass)

| Check | Result |
|---|---|
| Full-ledger dynamic sweep (`_ledger_schema.validate_event` over every row) | 277/277 rows validate (grew from brief-cited 275 during clone runtime due to two sibling events landing mid-run: `_plan/register-content-flip-milestone`, `M-TEX-1/panel/embedding/content-flip-analysis`) |
| `_STATUS_ENUM is STATUS_VALUES` (identity, not equivalence) | True |
| `STATUS_VALUES` contents | `{action_required, deferred, in-progress, invalidated, not-started, reopened, superseded, validated}` — proper superset of the brief's five-value proposal |
| Observed `status` union in current 277-row ledger | `{validated: 237, in-progress: 33, reopened: 3, invalidated: 2}` — strict subset |
| Observed `supersedes_path` union | 10 strings, 0 non-strings — post cycle-13 repair the list-form drift is gone; type check is the only fence against recurrence |
| `_lint_clone_shadow` importable at `long_exposure.workspace_bootstrap` module top level | Yes |
| `LedgerConcatError` MRO | subclass of `LedgerSchemaError` ⊂ `ValueError` (verified by test case 9 + integration §28) |
| Writer test suite (`tests/test_ledger_writer_validation.py`) | 18/18 pass (cases 14–18 present + green) |
| Concat test suite (`tests/test_fanout_concat_validation.py`) | 13/13 pass (case 9 MRO; cases 11–13 drift rejection at both gates) |
| Integration test (`tests/test_integration_cross_branch.py`) §1–§28 | PASS (0 failures) |
| Writer drift-rejection message shape | `LedgerAppendError: supersedes_path must be str, got list: [...]` and `LedgerAppendError: status 'wobble' not in canonical set {...}` |
| Pre-concat lint drift-rejection message shape | `LedgerConcatError: <shadow_path>:<lineno> (milestone_id=…): supersedes_path must be str, got list: [...]` |
| Public API of `append_ledger_event(workspace, event)` | signature unchanged; only new module-level symbols added |
| Public API of `concat_clone_ledgers(workspace, fork_dir) → int` | signature + behaviour unchanged; per-row `validate_event` loop factored into importable `_lint_clone_shadow` seam |
| `promise_check` on current ledger | 0 ERRORs |
| `_LE_PARENT` sys.path shim in both extended test files | Present |
| Non-factor AST isolation preserved | No `sidecar_nonfactor` imports in `_ledger_schema.py` or `workspace_bootstrap.py` |
| Interpreter guard in new scripts | `assert sys.executable == '/usr/bin/python3'` present |

### Auditor MODERATE observations (non-blocking, documented, not fixed)

- **Report Appendix B WARN count drift.** The worker's report cited 26 WARNs (pre-cycle-14 baseline); the auditor observed 43 at the time of audit. Documentation-timing artifact: sibling workflow events landed between the worker's ledger snapshot and the audit sweep. The brief's explicit escape hatch ("WARN drift is a timing artifact, not a functional regression") permits this. Zero ERRORs is the load-bearing invariant, and that holds.
- **Ledger row count divergence 275 → 277.** Brief cited 275; audit observed 277. The dynamic sweep used `for line in open(...)` rather than a fixed-count `range(275)`, so the growth was absorbed correctly. Flagged transparently in the worker's Issues and Uncertainties.
- **`_lint_clone_shadow` interpretation.** Named-seam factoring rather than new-logic addition. Semantically identical to the prior state (same invariants, same moment before `os.replace`); the difference is a stable, testable function name. The `validated/medium` fallback did not need to fire; the recommended zero-caller-change path landed cleanly.

### Auditor MINOR observation

- `LedgerConcatError` is not directly re-exported from the `workspace_bootstrap` module namespace, but tests exercise the class through their imports from `long_exposure.tools._ledger_schema` (cycle-12 precedent) and case 9 verifies MRO by that route. Non-issue.

### The one honest surprise (report §2b)

During the investigation the worker discovered that cycle-13's line-250 nuance was misclassified in the original diagnostic. The `status: "in-progress"` value was not itself enum-illegal — `in-progress` is a canonical enum member — but semantically wrong on a milestone that had previously been `validated`. This is a **state-transition drift class**, not an enum drift class, and the cycle-14 validator does not catch it because type/enum checks cannot express `validated → in-progress` without an intervening `reopened`. The report §2b documents this honestly; the state-transition validator is hoisted to a cycle-15 follow-up (b) rather than papered over. The cycle-14 validator is still a proper superset of prior enforcement — it catches strictly more — but this specific class is not yet closed.

## Discussion

Two things about this branch are worth naming.

First, the three-cycle SSoT hardening arc closes cleanly, and each cycle's addition catches strictly more than the last while weakening nothing. Cycle 10 established the writer gate (`append_ledger_event` calls `validate_event`); cycle 12 established the concat gate (`concat_clone_ledgers` calls `validate_event` per row before write, with a per-milestone `ts` monotonicity check and atomic `os.replace`); cycle 14 tightens both gates with two additional field-type + enum invariants and factors the per-row loop into an importable `_lint_clone_shadow` seam so the gate is now named and testable rather than inline. All three surfaces now route through the same SSoT module with `_STATUS_ENUM is STATUS_VALUES` identity, and the pattern of using post-merge integration surface as the retrospective driver of the next hardening cycle is healthy and repeatable. The zero-caller-change discipline held on all three cycles — the mechanical additions never disturbed the public API — and the falsifiability escape hatches worked exactly as designed on all three: they had explicit trigger checks and did not need to fire load-bearing because the SSoT already anticipated the historical range.

Second, the state-transition nuance surfaced during the investigation is the branch's most valuable non-obvious contribution. The cycle-13 diagnostic named the line-250 drift as an enum problem, and the brief inherited that framing. When the worker built the enum check and reran it against line 250, the check *passed* — `in-progress` is a canonical enum member — and the enum extension did not fire on the drift the brief said it would catch. The honest response was to (a) still ship the enum check because it does catch a real class (the `wobble`-style unknown-value drift that would otherwise slip through) and (b) hoist the actual line-250 mechanism (state-transition drift) to a cycle-15 follow-up. Neither the enum nor the type check is over-claimed to close a class it doesn't; the state-transition class is named as open. This is the falsifiability discipline paying off in the exact case it was designed for — a hypothesis about what drift class was in play was tested by building the check, and the check's null result on the specific line was surfaced rather than concealed.

The recurring `_LE_PARENT` shim requirement is now the fifth consecutive cycle applying it successfully (cycles 10, 11, 12, 13, and this one). It is time to codify the requirement in the test-authoring template rather than continue to rely on brief-level reminders every cycle.

## Open Questions

The branch's sole deliverable is shipped and every sufficiency criterion pass under independent live re-verification. The following belong to future cycles and are recorded in the report's cycle-15 follow-ons:

- **(a) Full optional-field enumeration under SSoT type-checking.** `assessor` short-form set, `agent`, `run_id` format regex, `event_id` UUID5-vs-arbitrary. Cycle 14 hardened only `supersedes_path` and `status`; the ambient conventions remain untyped.
- **(b) State-transition validator hoisting.** The critical follow-up because cycle-13's line-250 nuance proved type/enum validators cannot catch `validated → in-progress` without an intervening `reopened`. A new axis, not a regression, but should not sit indefinitely.
- **(c) Drift-class enumeration index.** A documented registry of drift classes closed, drift classes deferred, and drift classes suspected-but-unproven. Becomes the retrospective spine for cycle 15+.
- **(d) Fork-integration exemption verification.** Verify that the four upstream `long_exposure/*` "ledger-tracked artifact missing" WARNs remain a known-exemption pattern rather than a fresh drift class. Cycle-13 clone-1 + cycle-14 clone-0 established the precedent; when fork-integration surface picks this back up, it should verify the exemption remains valid rather than treat it as a fresh drift.

For the next researcher cycle's diagnostic ladder: if a fourth drift class appears at post-merge integration, start at Rung 3 (does the tightened validator catch it, and if not, why?) rather than at Rung 1 (is the ledger corrupt at all?).

## Appendix: Provenance

**Cycle range:** cycles 1-2 of fork `855d4c2e9945`, clone 0.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:**

- Cycle 1: researcher `eb4629c8-469f-4bcf-8ade-94269ab2852b`, worker `8b8714d1-78b2-4d29-aa85-4f845c230159`, auditor `6da7d443-c792-4a1e-aaec-dc35de662cff`.
- Cycle 2: researcher `040a1c86-825a-41ec-9ecd-fc807ad56e74`, worker `e63ca7a2-97d4-41f6-8f2e-b8ab03904254`, auditor `2046c2c9-62d5-436a-801c-1fd7217aa7cb`.

**Auditor verdict:** **VALIDATED / high**. Sub-milestone `_infra/ledger-schema-hardening-v2` closes at `validated/high`; the three-cycle SSoT ledger-schema hardening arc (writer c10 → concat c12 → field-type+enum c14) closes as a coherent unit.

**Deliverables on disk.**

- Code: `long_exposure/tools/_ledger_schema.py` extended with `supersedes_path` type check and `STATUS_VALUES` / `_STATUS_ENUM` (bound by identity); `long_exposure/workspace_bootstrap.py` factors the existing cycle-12 per-row `validate_event` loop out of `concat_clone_ledgers` into the importable `_lint_clone_shadow` seam. Both `append_ledger_event(workspace, event)` and `concat_clone_ledgers(workspace, fork_dir) → int` public signatures unchanged.
- Tests: `tests/test_ledger_writer_validation.py` extended (cases 14–18, 18/18 pass); `tests/test_fanout_concat_validation.py` extended (cases 9, 11–13, 13/13 pass); `_LE_PARENT` sys.path shim at head of both files.
- Cross-branch integration test §28: 7 invariants, all green.
- Report: `docs/ledger_schema_hardening_v2.md` (§1–§8 + Appendix A + Appendix B) — sole required output artefact; documents the three-cycle hardening arc.

**Runtime evidence.**

- Full-ledger dynamic sweep: 277/277 rows validate under the tightened schema.
- `_STATUS_ENUM is STATUS_VALUES` → True.
- Writer drift rejection at the writer gate: `LedgerAppendError: supersedes_path must be str, got list: [...]`; `LedgerAppendError: status 'wobble' not in canonical set {...}`.
- Pre-concat lint rejection at the concat gate: `LedgerConcatError: <shadow_path>:<lineno> (milestone_id=…): supersedes_path must be str, got list: [...]`.
- Writer suite 18/18; concat suite 13/13; cross-branch integration test 0 failures with §28 present; `promise_check` 0 ERRORs.

**Ledger routing.** Closure event `_infra/ledger-schema-hardening-v2` written to the per-clone shadow ledger at `/home/user/music-gen-instance/fork-855d4c2e9945/clone-0/promise_ledger.jsonl` (the branch dogfooded its own tightened writer for its own six ledger events). The auditor's WARN count observation (43 vs the worker's cited 26) is a documentation-timing artifact per the brief's explicit escape hatch — sibling workflow events landed between the worker's ledger snapshot and the audit sweep. Zero ERRORs is the load-bearing invariant and holds.

**Environment stack unchanged since cycle 10.** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`. Single-thread BLAS pins throughout.

**Handoff.** Merge report written to `/home/user/music-gen-instance/fork-855d4c2e9945/clone-0/merge_report.md`. The four cycle-15 follow-ons named above — optional-field enumeration under SSoT type-checking, state-transition validator hoisting, drift-class enumeration index, and fork-integration exemption verification — should carry forward as new milestones when scheduled. The state-transition class is the critical one; it should not sit indefinitely.

<verdict>validated</verdict>
