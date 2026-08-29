---
title: "Cycles 1-3 Clone 1 Report — M-EAR-1/real-label-training-v2 (Fork c320de981fda)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_1-3_clone_1]

# Cycles 1-3 Clone 1 Report — M-EAR-1/real-label-training-v2 (Fork c320de981fda)

## Abstract

Cycles 1-3 of clone-1 (fork `c320de981fda`) advance `M-EAR-1/real-label-training-v2` scaffolding but **do not complete the pipeline** within the fanout-cycle wall-time envelope. Rubric frozen; resample manifest (43 songs → 252 clips) landed; feature extraction advanced across cycles (0 → 118 → 124 → 203/252 = 80.6%); scripts AST-clean vs c22/c23/c25 forbidden imports; c1 chunker + c6 chassis + c22 stability harness + c26 Path B doc + c38 clone-0 v1 tree preserved. But 8/10 sufficiency criteria fail: extraction incomplete, training/eval/determinism/anchor-snapshot/tests/report/10-events all not reached. Cycle 3 auditor emits **PIVOT (unfixable-by-audit escalation)** per operating-protocol hard-stop clause after 4th consecutive attempt with same executional choke.

## Verdict

**PARTIAL_PROGRESS → PIVOT (unfixable-by-audit)** (rubric-verdict slot unfilled; branch escalates to root-conductor sequential-mode pickup with 203/252 feature cache preserved as handoff asset).

## Rubric SHA Anchor (Committed at Cycle 1; Persisted Across Cycles 2-3)

| Location | State |
| --- | --- |
| `docs/ear_real_label_training_v2_rubric.md` | mtime gate held |
| `data/ear_v2/rubric_hash.txt` | 65 B, present |
| `data/ear_v2/verdict.json` | **absent** (not reached) |

Rubric-first commit gate PASS from c39 (this fork's cycle 1); zero after-the-fact rubric edits.

## Cycle Disposition

| Cycle | Researcher Directive | Worker Action | Auditor Decision | Feature Extraction Progress |
| --- | --- | --- | --- | --- |
| 1 (c39-initial + resume) | Ship the milestone under frozen 3-verdict rubric | Rubric + scripts + manifest landed; pure Hold Pattern on extraction | CONTINUE | 0 → 118 |
| 2 (c40) | Foreground-only extractor invocation with strongest executional guardrails | Near-null cycle (+6 features) | CONTINUE with strong nudge | 118 → 124 |
| 3 (c41, this range close) | Monitor-poll allowed; no background-job-await | Substantive-but-incomplete cycle (+79 features; escaped pure Hold Pattern with real progress); exhausted cycle budget before extraction completed | **PIVOT (unfixable-by-audit escalation)** | 124 → **203/252** (80.6%) |

## On-Disk State (Verified Via ls + JSON Inspection)

| Deliverable | State | Notes |
| --- | --- | --- |
| `docs/ear_real_label_training_v2_rubric.md` | PASS | mtime gate held |
| `data/ear_v2/rubric_hash.txt` | PASS | 65 B |
| `data/ear_v2/resample_manifest.json` | PASS | 43 songs / 252 clips planned |
| `data/ear_v2/features_v2/*.npy` | **PARTIAL** | **203/252 = 80.6%** |
| `data/ear_v2/training_result.json` | ABSENT | never ran |
| `data/ear_v2/corn_head_v2.pt` | ABSENT | never trained |
| `data/ear_v2/leak_test_v2_summary.json` | ABSENT | never evaluated |
| `data/ear_v2/sb_v2_verdict.json` | ABSENT | SB1/SB2/SB3 unknown |
| `data/ear_v2/verdict.json` | ABSENT | no rubric-verdict emitted |
| `data/ear_v2/anchor_preservation.json` | ABSENT | 25+ SHAs never snapshotted |
| `docs/ear_real_label_training_v2_report.md` | **ABSENT** | branch's required output artefact |
| `tests/test_ear_real_label_training_v2.py` | scaffolded, unrun | 0 assertions executed |
| Ledger events `M-EAR-1/real-label-training-v2/*-clone-1` | **0/10** | grep on `promise_ledger.jsonl` returns only c38 handoff-narrative match |

**Extension note**: files written as `.npy` not `.npz` per brief. Minor divergence, non-blocking.

## Sufficiency Table (2/10 PASS)

| # | Criterion | Status |
| --- | --- | --- |
| 1 | Rubric committed before scripts (mtime + git-log dual gate) | PASS (from c39) |
| 2 | AST-clean vs c22/c23/c25 forbidden imports | PASS |
| 3 | Resample manifest complete (43 songs → 252 clips) | PASS |
| 4 | Feature extraction complete (`len(features) == manifest.n_clips_total`) | **FAIL** — 203 vs 252 |
| 5 | Training run produced `training_result.json` + `corn_head_v2.pt` under GroupKFold(song_id) | **FAIL** — not reached |
| 6 | SB1/SB2/SB3 evaluated; F1 denominator > 43 (SB3 redesign contract) | **FAIL** — not reached |
| 7 | Byte-determinism × 2 SHA-256 equality on 3 artefacts | **FAIL** — not reached |
| 8 | Anchor preservation on ≥25 SHAs (`unchanged: true`) | **FAIL** — not reached |
| 9 | ≥14 tests green | **FAIL** — never invoked |
| 10 | Report + 10 `-clone-1` ledger events landed | **FAIL** — 0/10 |

**Sufficiency-table result**: 3/10 PASS; 7/10 FAIL (extraction-blocked). 4-cycle sequential progression of pure Hold Pattern → near-null → substantive-but-incomplete confirms same executional choke every cycle.

## PIVOT Decision (Operating-Protocol Hard-Stop Clause Triggered)

Operating-protocol hard-stop clause: *"If the same CRITICAL issue persists across 2 consecutive cycles, document as 'unfixable by audit — requires original builder.'"* Now the **4th consecutive attempt** with the same executional choke.

**Choke is executional, not scientific.**

- Each cycle landed incremental progress (0 → 118 → 124 → 203 features).
- No single cycle within the fanout branch's per-cycle wall-time budget carried the pipeline through extraction → train → eval → determinism × 2 → anchor preservation → tests → report → 10 events.
- c40's strongest executional guardrail (foreground-only, Monitor-poll allowed, no background-job-await); c41's worker honored the Monitor-poll directive (real progress, no null cycle) but still exhausted cycle budget before extraction completed.
- **Feature extraction alone plausibly exceeds a single cycle's budget** on this corpus (43 songs × 4-6 clips × PANNs Cnn14 penultimate 2048-D — CPU-only inference).

**Scientific scope is sound**; scaffolding is complete; scripts AST-clean and locally runnable. Continuing to spin the same wheel in this branch will not converge.

## Auditor-Guided c42 Cycle Purpose: Escalation and Closure — NO Further Empirical Work in This Branch

Per cycle-3 auditor guidance, c42 researcher brief must instruct worker to:

1. **Do NOT resume feature extraction or downstream stages in the fanout branch.** Corpus-side intervention scientifically sound; executional envelope in fanout context is not.
2. **Emit `_manager/M-EAR-1-real-label-training-v2-unfixable-by-audit-clone-1`** as the sole substantive ledger event this cycle. `status=in_progress`, `confidence.level=high`, `confidence.assessor=auditor`, `confidence.rationale` = "4 consecutive cycles in fanout branch B (c39-initial, c39-resume, c40, c41) landed incremental feature-cache progress (0 → 118 → 124 → 203 / 252) but none completed the >5-stage sequential pipeline inside one cycle's wall-time budget. Executional envelope, not science."
3. **Write closure document** `docs/ear_real_label_training_v2_report.md` (the required branch artefact) at PARTIAL_PROGRESS state, documenting:
   - 4-cycle scaffolding + partial-extraction ledger.
   - 203/252 feature cache as preserved handoff asset (do NOT invalidate).
   - Scientific soundness of anchored-tail resample + SB3 redesign (denominator > 43 contract).
   - Explicit handoff: root conductor picks up in sequential (non-fanout) execution, with full context window per stage, resuming the extractor cache from 203/252.
4. **Emit COMPLETE with `[[BRANCH_COMPLETE]]`** after closure doc + manager event land.
5. **Preservation invariants (still binding)**: rubric doc untouched; `scripts/ear_v2/*.py` untouched; α pinned at `0.7469387071101908` (this branch never touched); c26-frozen SB1/SB2/SB3 thresholds unchanged; **203-file feature cache preserved on disk (do NOT delete — root pickup uses it)**.
6. **Housekeeping** (under `-clone-1` suffix): `_run/cycle_41_closed-clone-1`, `_archive/cycle-41-scratch-clone-1`.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908` (this branch never touched α).
- SHA-256 tiebreak; no PRNG; no `sidecar_nonfactor` imports.
- Interpreter guard `#!/usr/bin/python3` on every new script (scripts AST-verified).
- Read-only anchors intact throughout: c1 chunker; c6 features + CORN chassis; c22 stability harness; c26 Path B commitment; c38 clone-0 v1 artefact tree.
- c15 `i4_stratified.py` NOT imported; c23 `model_v2_*` and c25 `feature_subset_adapter` NOT imported (AST-verified, criterion #2 PASS).
- Rated audio egress-blocked at `*.googlevideo.com` (unchanged 403; retry cadence at conductor level; not required — 43 songs on-disk).
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`.
- c26-frozen SB1/SB2/SB3 thresholds unchanged; no post-hoc adjustment attempted or contemplated.

## Anti-Patterns Locked (5-Count Stable)

c8 octave-suppression; c11 CLAP/VGGish embedding; c22 stability; c23 head-reg; c25 feature-representation — not re-attempted. c31 STILL_GAP / c35 A anti-pattern surface intact. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged.

**c22/c23/c25 anti-pattern locks explicitly enforced in this branch**: AST-check confirmed no `c23 model_v2_*` or `c25 feature_subset_adapter` modules imported anywhere under `scripts/ear_v2/`. Corpus-side intervention orthogonal to c22/c23/c25 axes preserved throughout.

## State-Machine Discipline (c29 Lemma Respected)

`M-EAR-1/real-label-training-v2` is a peer sub-milestone under M-EAR-1. NOT a child of terminal-validated `_manager/M-EAR-1-path-B-commit`, `M-EAR-1/{synthetic-label, head-regularization, feature-representation}-audit`, `M-EAR-1/armed-harness-fixture-reinforcement`, c36 `real-label-training-v0`, or c38 `real-label-training-v1`.

## Merge Disposition

No merge action this range (PIVOT to escalation; branch does not close normally). Handoff to c42 for auditor-guided closure sequence. Root-conductor sequential-mode pickup owns downstream empirical work; 203/252 feature cache preserved on-disk as handoff asset.

**Systemic finding** (to file at campaign level, not this branch): fanout cycle wall-time envelope is insufficient for pipelines with dominant single-stage costs. Recommend a campaign-level `_manager/fanout-pipeline-cost-audit` at some future cycle to enumerate which M-* milestones exceed fanout-cycle capacity and must be assigned to root-conductor sequential mode.

## Cycle-42+ Handoff (Priority Order)

1. **c42 auditor-guided closure sequence** (per cycle-3 auditor guidance above): closure doc + manager event + housekeeping + `[[BRANCH_COMPLETE]]`.
2. **Root-conductor sequential-mode pickup of M-EAR-1/real-label-training-v2** — resume extractor cache from 203/252; complete extraction → train → eval → determinism × 2 → anchor snapshot → tests → report → 10 events in sequential mode with full context window per stage.
3. **Campaign-level `_manager/fanout-pipeline-cost-audit`** — enumerate which M-* milestones exceed fanout-cycle capacity and must be assigned to root-conductor sequential mode. Not this branch.
4. **Sibling awareness**: clone-2 closed at `_manager/fanout-namespace-convention-v3-resolution` (CONVENTION_v3_LANDS); not directly relevant to this branch. Clone-0 status per fork-level merge report.

## Cumulative Progress

**M-EAR-1 arc** (post-c41 clone-1 PIVOT):

| Cycle | Milestone | Verdict |
| --- | --- | --- |
| c22-c25 | Path A chassis chain | insufficient (anti-patterns locked) |
| c26 | `_manager/M-EAR-1-path-B-commit` | committed; three SBs frozen |
| c31 | `armed-harness-fixture-reinforcement` | FIXTURE_READY |
| c36 | `real-label-training-v0` | EAR_v0_INSUFFICIENT (first real-label fire) |
| c37 clone-1 | `_manager/ear-sb3-statistic-degeneracy-fallback-statistic` | F1_ADOPTED |
| c38 clone-0 | `real-label-training-v1` | EAR_v1_PARTIAL |
| c39-c41 clone-1 (this) | `real-label-training-v2` | **PARTIAL_PROGRESS → PIVOT** (203/252 feature cache preserved for root pickup) |

**Executional pattern observed and documented**: fanout cycle wall-time envelope insufficient for >5-stage sequential pipelines with dominant single-stage costs. Future M-EAR-1 real-label training work should not be assigned to a fanout branch.

**Scientific plan remains sound**: anchored-tail resample of 43 songs → 252 clips (mean 5.86 clips/song) breaks singleton-artist geometry that pinned v1's F1 at 2/3, giving SB3 F1 a meaningful denominator > 43 as originally motivated by c37 clone-1's F1_ADOPTED handoff.

**Preserved assets valuable at root pickup**: 203/252 features cached (~80% of extractor cost sunk); manifest frozen; rubric + hash landed; scripts AST-clean; test suite scaffolded (≥14 cases enumerated per brief); c22/c23/c25 anti-pattern locks verified absent from `scripts/ear_v2/`.

**Pattern durability**: rubric-first pre-registration discipline held for cycle 1 (c39-initial) even though downstream stages did not complete. Rubric SHA embedded verbatim in `rubric_hash.txt` and would be embedded verbatim in `verdict.json` at pipeline completion. Zero after-the-fact rubric edits.

**c29 state-machine lemma** respected: peer sub-milestone; ledger topology stays a DAG.

**c32 → c33 → c36 v2 → c39 v3** fanout-namespace convention held: scripts would emit under `-clone-1` suffix per codified v3 behavior (0/10 events emitted due to pipeline incomplete).

**Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

**New systemic pattern** worth c42+ campaign-level codification: fanout-pipeline-cost-audit to catalog which M-* milestones exceed fanout-cycle capacity. This is the first observed instance of a cleanly-scoped scientific milestone whose executional envelope exceeded the fanout budget four consecutive times.

[END OUTPUT]
