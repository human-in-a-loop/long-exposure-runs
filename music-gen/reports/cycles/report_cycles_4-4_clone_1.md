---
title: "Cycle 4 Clone 1 Report — M-EAR-1/real-label-training-v2 (Fork c320de981fda)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_4-4_clone_1]

# Cycle 4 Clone 1 Report — M-EAR-1/real-label-training-v2 (Fork c320de981fda)

## Abstract

Cycle 4 of clone-1 (fork `c320de981fda`) executes the auditor-guided c42 closure sequence for `M-EAR-1/real-label-training-v2` following the cycle-3 (c41) PIVOT to `unfixable-by-audit` under the operating-protocol hard-stop clause. Worker landed the closure `docs/ear_real_label_training_v2_report.md` at **PARTIAL_PROGRESS** state (10 sections; tail `## 10. Branch complete\n\n[[BRANCH_COMPLETE]]`), emitted the `_manager/M-EAR-1-real-label-training-v2-unfixable-by-audit-clone-1` sole substantive event plus 2 housekeeping events, wrote the merge report at both primary and workspace-fallback paths (byte-identical size 3,974 B), and preserved all handoff assets untouched (rubric doc, hash file, resample manifest, 203-file `.npy` feature cache, scripts, tests, c6/c22/c26/c38/c1 anchors). Auditor decision: **COMPLETE** with `[[BRANCH_COMPLETE]]`. Branch retired from fanout scope; downstream work owned by root-conductor sequential-mode pickup.

## Verdict

**PARTIAL_PROGRESS → COMPLETE (auditor)** (branch retired from fanout scope; `[[BRANCH_COMPLETE]]` confirmed at three locations).

## Rubric SHA Anchor (Unchanged; c41-Snapshot Byte-Equal)

| Location | State |
| --- | --- |
| `docs/ear_real_label_training_v2_rubric.md` | SHA `01948b6efe6ca5e9…`, 9,304 B (byte-identical to c41 snapshot) |
| `data/ear_v2/rubric_hash.txt` | 65 B; content `01948b6efe6ca5e9…` byte-equal to rubric doc SHA (dual-gate consistency preserved) |

Zero after-the-fact rubric edits across the 4-cycle arc.

## Cycle Disposition

| Cycle | Researcher Directive | Worker Action | Auditor Decision |
| --- | --- | --- | --- |
| 4 (this) | c42 auditor-guided closure sequence: NO further empirical work; emit closure doc + manager event + housekeeping | Closure report at PARTIAL_PROGRESS; `_manager/*-unfixable-by-audit-clone-1` sole substantive event; 2 housekeeping events; merge reports written; handoff assets preserved | **COMPLETE** with `[[BRANCH_COMPLETE]]` |

## On-Disk Closure Verification (Auditor Grep + Byte-Level Confirmations)

| Check | Result | Evidence |
| --- | --- | --- |
| `docs/ear_real_label_training_v2_report.md` present | ✓ | 13,707 B; 10 `## ` sections; tail `## 10. Branch complete\n\n[[BRANCH_COMPLETE]]` |
| PARTIAL_PROGRESS verdict + `[[BRANCH_COMPLETE]]` sentinel in report | ✓ | grep-count 1 in report |
| Merge report at primary path | ✓ | `/home/user/music-gen-instance/fork-c320de981fda/clone-1/merge_report.md` exists, 3,974 B |
| Merge report at workspace fallback | ✓ | `tools/stale/c41_clone1_merge_report_draft.md` 3,974 B (byte-identical size to primary) + `[[BRANCH_COMPLETE]]` present |
| Rubric doc untouched (pre==post) | ✓ | SHA `01948b6efe6ca5e9…`, 9,304 B |
| `data/ear_v2/rubric_hash.txt` untouched | ✓ | 65 B; byte-equal to rubric doc SHA |
| `data/ear_v2/resample_manifest.json` untouched | ✓ | SHA `c6fa617ccf575c2b…`, 139,988 B |
| 203-file feature cache preserved | ✓ | `data/ear_v2/features_v2/*.npy` count = 203, unchanged from c41 (root-conductor cache-skip resume dependency intact) |
| `[[BRANCH_COMPLETE]]` in report §10 + merge report tail + worker final output | ✓ | all three confirmed |

## Ledger Events (This Cycle: 3; Correctly Under `-clone-1` Suffix)

Per c42 auditor guidance: emit `_manager/*` closure event + housekeeping only; correctly OMIT `_infra/adopt-cycle41-tests-clone-1` (no new tests adopted this cycle):

| # | Event | Status | Confidence | event_id |
| --- | --- | --- | --- | --- |
| 1 | `_manager/M-EAR-1-real-label-training-v2-unfixable-by-audit-clone-1` | in-progress | high (auditor) | `21ad8f74-…-c001` |
| 2 | `_run/cycle_41_closed-clone-1` | validated | high (auditor) | `8656db64-…-997c` |
| 3 | `_archive/cycle-41-scratch-clone-1` | validated | high (auditor) | `e78a8119-…-8a68` |

The `_manager/*-unfixable-by-audit-clone-1` event is a **first emission on a new identifier**, so the `validated → in_progress` state-machine rule doesn't apply and `in-progress/high` is the correct state per c29 lemma.

`confidence.rationale` on the manager event: "4 consecutive cycles in fanout branch B (c39-initial, c39-resume, c40, c41) landed incremental feature-cache progress (0 → 118 → 124 → 203 / 252) but none completed the >5-stage sequential pipeline (extract → train → eval → determinism × 2 → anchor snapshot → tests → report → 10 events) inside one cycle's wall-time budget. Executional envelope, not science."

## State-Machine Discipline (c29 Lemma Respected)

`M-EAR-1/real-label-training-v2` is a peer sub-milestone under M-EAR-1. NOT a child of terminal-validated `_manager/M-EAR-1-path-B-commit`, `M-EAR-1/{synthetic-label, head-regularization, feature-representation}-audit`, `M-EAR-1/armed-harness-fixture-reinforcement`, c36 v0, or c38 v1. The `_manager/*-unfixable-by-audit-clone-1` event opens a new identifier; `validated → in_progress` rule does not apply.

## Standing Constraints (Unchanged; Preservation Invariants All Hold)

- α pinned at `0.7469387071101908` (this branch never touched α).
- SHA-256 tiebreak; no PRNG; no `sidecar_nonfactor` imports.
- Interpreter guard `#!/usr/bin/python3` on every new script (scripts unchanged from c41; still AST-verified).
- Read-only anchors intact throughout: c1 chunker; c6 features + CORN chassis; c22 stability harness; c26 Path B commitment; c38 clone-0 v1 artefact tree.
- c15 `i4_stratified.py` NOT imported; c23 `model_v2_*` and c25 `feature_subset_adapter` NOT imported (AST-verified from c41).
- c26-frozen SB1/SB2/SB3 thresholds unchanged; no post-hoc adjustment attempted.
- Rated audio egress-blocked at `*.googlevideo.com` (unchanged 403; retry cadence at conductor level; not required — 43 songs on-disk).
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`.

Validators (promise_check / org_check) not run this cycle — closure work touches no code and no schema; on-disk anchors verified byte-for-byte against c41 snapshot per role guidance ("best-effort per role guidance; no findings a validator could have surfaced would change the verdict").

## Anti-Patterns Locked (5-Count Stable)

c8 octave-suppression; c11 CLAP/VGGish embedding; c22 stability; c23 head-reg; c25 feature-representation — not re-attempted. c31 STILL_GAP / c35 A anti-pattern surface intact. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged.

**Null-cycle anti-pattern explicitly avoided**: this closure cycle produced substantive closure with a durable report, a durable ledger event, a durable merge report, and preserved handoff assets — not a null-cycle pause memo.

## MINOR Findings (Logged, Not Acted On)

1. **Cycle-numbering nomenclature drift** between brief §0 ("c42 worker") and §3 event names (`cycle_41_*`) is real but harmless — the closure ledger is unambiguous, the auditor's c41 PIVOT report and worker's c42 closure form a coherent two-cycle sequence, and every event_id is content-hash derivable and grep-locatable.

## Systemic Finding (Filed in Report §6 Only, Not as Standalone Ledger Event)

Fanout cycle wall-time envelope is insufficient for pipelines with dominant single-stage costs. Two independent clones this campaign have now hit it (this branch + earlier signals in other M-EAR-1 branches). Recommendation: campaign-level `_manager/fanout-pipeline-cost-audit` to enumerate which M-* milestones exceed fanout-cycle capacity and must be assigned to root-conductor sequential mode. Root conductor decides where and when to formalise as a standalone ledger event.

## Merge Disposition

Merge report at both primary path (`/home/user/music-gen-instance/fork-c320de981fda/clone-1/merge_report.md`, 3,974 B) and workspace fallback (`tools/stale/c41_clone1_merge_report_draft.md`, byte-identical 3,974 B). `[[BRANCH_COMPLETE]]` sentinel present at three locations (report §10, merge report tail, worker final output). Branch retired from fanout scope; no further cycle should be scheduled on this clone-1 branch. Any further M-EAR-1/real-label-training-v2 work is owned by root-conductor sequential-mode pickup using preserved handoff assets.

## Root-Conductor Sequential-Mode Handoff (Per Cycle-4 Auditor Guidance)

Estimated pipeline cost (sequential-mode): ~49 PANNs Cnn14 penultimate CPU inferences + 5-fold GroupKFold training + SB1/SB2/SB3 evaluation + × 2 determinism check. Order of hours, not order of a fanout cycle.

1. Resume `scripts/ear_v2/extract_features_v2.py` in sequential (non-fanout) mode with cache-skip semantics against the preserved 203/252 `.npy` cache; complete the remaining ~49 clips.
2. Run `scripts/ear_v2/train_v2.py` (5-fold GroupKFold, per-song grouping preserves no-clip-leakage contract).
3. Run `scripts/ear_v2/evaluate_sb_v2.py` against c26-frozen thresholds (SB1 margin > 0.5909; SB2 mean τ ≥ 0.4; SB3 detection F1 ≥ 0.90 — resample now gives SB3 F1 denominator meaningful cardinality > 43).
4. Run `scripts/ear_v2/determinism_check.py` × 2 on `training_result.json` + `corn_head_v2.pt`.
5. Run `tests/test_ear_real_label_training_v2.py` (≥14 tests).
6. Emit 6 substantive + 4 housekeeping ledger events originally scoped under `M-EAR-1/real-label-training-v2/*` (no `-clone-*` suffix in sequential mode — the c33 harness guard applies only in clone context, per c39 v3 doc codification).
7. Rewrite `docs/ear_real_label_training_v2_report.md` at final verdict state (EAR_v2_LANDS / PARTIAL / INSUFFICIENT per frozen rubric) OR leave the PARTIAL_PROGRESS report as historical closure and produce a new report under a distinct name.

**Candidate future ticket** (root-conductor discretion): `_manager/fanout-pipeline-cost-audit`.

## Cumulative Progress

**M-EAR-1 arc** (post-c41 PIVOT + c42 closure):

| Cycle | Milestone | Verdict |
| --- | --- | --- |
| c22-c25 | Path A chassis chain | insufficient (anti-patterns locked) |
| c26 | `_manager/M-EAR-1-path-B-commit` | committed; three SBs frozen |
| c31 | `armed-harness-fixture-reinforcement` | FIXTURE_READY |
| c36 | `real-label-training-v0` | EAR_v0_INSUFFICIENT |
| c37 clone-1 | `_manager/ear-sb3-statistic-degeneracy-fallback-statistic` | F1_ADOPTED |
| c38 clone-0 | `real-label-training-v1` | EAR_v1_PARTIAL |
| c39-c41 clone-1 | `real-label-training-v2` (attempts 1-4) | PARTIAL_PROGRESS → PIVOT (unfixable-by-audit) |
| **c42 clone-1 (this)** | closure sequence for `real-label-training-v2` | **COMPLETE** with `[[BRANCH_COMPLETE]]`; branch retired from fanout scope; 203-file cache + scaffolding preserved for root-conductor sequential-mode pickup |

**Operating-protocol hard-stop clause executed as designed**: c41 audit fired it; c42 closure cycle honoured it without attempting a 5th extraction. Anti-recursion behaviour the clause exists to enforce.

**Fanout-envelope pattern now a first-class systemic observation**: two independent clones this campaign have hit it; root conductor has concrete recommendation on file (report §6) to codify a campaign-level cost audit before spawning further pipeline-heavy fanout clones.

**The `unfixable-by-audit` verdict has proven to be a useful protocol primitive**: creates a legible exit from a productive-but-unbounded loop without invalidating the underlying science, and produces the specific artefact set (preserved cache + PARTIAL_PROGRESS report + `_manager/*` closure event) that a subsequent sequential-mode pickup can consume with zero re-audit.

**Preserved assets valuable at root pickup** (unchanged from c41): 203/252 features cached (~80% of extractor cost sunk); manifest frozen; rubric + hash landed; scripts AST-clean; test suite scaffolded (≥14 cases enumerated per brief); c22/c23/c25 anti-pattern locks verified absent from `scripts/ear_v2/`.

**Pattern durability**: rubric-first pre-registration discipline held for all 4 cycles even though downstream stages did not complete. Rubric SHA anchored to `rubric_hash.txt`; would embed verbatim in `verdict.json` at pipeline completion in sequential mode. Zero after-the-fact rubric edits.

**c29 state-machine lemma** respected: peer sub-milestone; new `_manager/*-unfixable-by-audit-clone-1` identifier opens `in-progress` (first emission); ledger topology stays a DAG.

**c32 → c33 → c36 v2 → c39 v3** fanout-namespace convention held: 3 closure events correctly emitted under `-clone-1` suffix per codified v3 behaviour.

**Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

**Session terminal for clone-1's role in fork c320de981fda.** `[[BRANCH_COMPLETE]]` sentinel present at three locations; no further cycle should be scheduled on this clone-1 branch.

[END OUTPUT]
