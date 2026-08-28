---
title: "Music-Gen — Ear-Model Preparation (M-EAR-1, cycles 4-6, clone 2)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — Ear-Model Preparation (M-EAR-1, cycles 4-6, clone 2)

## Abstract

No new work was performed in cycles 4-6. The scoped objective for this clone — the training-agnostic chassis for M-EAR-1 (feature extractor, CORN ordinal head, non-factor leak-test harness) — was fully discharged and validated in cycles 1-3, with every success bar met on the synthetic-label evaluation and the non-factor isolation contract intact. These three cycles are a closure-acknowledgment posture: the researcher, worker, and auditor each confirmed no falsifiable hypothesis remains inside clone-2's assigned scope, refused to open sibling scopes, and refused to gold-plate already-validated criteria. The auditor's verdict for the cycle range is a one-line VALIDATED with the note "Scope discharged; no work this cycle. State unchanged."

## Introduction

Clone-2's assignment is bounded: everything M-EAR-1 needs that does not require the real rated audio. That work landed in cycles 1-3 with per-leak-type calibration of the leak-detection threshold τ recorded as a management decision (`_manager/M-EAR-1-leak-statistic-substitution.md`), determinism confirmed by byte-identity of a replay summary, and cross-branch isolation enforced by an integration test.

The one remaining M-EAR-1 task — training the CORN head against the 80 real ratings — is blocked on the workspace egress policy denying `*.googlevideo.com`, and by the campaign's fixed decision that acquisition never blocks downstream work but also does not become another branch's job. That task belongs to the root conductor's post-egress cycle, not to this clone.

Given that, the correct behavior for cycles 4-6 is to hold. The three cycles do exactly that.

## Approach

The clone's cycle loop drives itself by low-output detection: when no cycle produces new artifacts or ledger events, the loop terminates naturally at the end of the assigned range. Cycles 4-6 exercised the researcher/worker/auditor triad three times against unchanged scope. Each triad correctly identified that:

1. The success bars from cycles 1-3 already meet the assignment with margin — pushing further would be optimization theater on already-VALIDATED criteria.
2. The two siblings in the fork (clone-0 on M-TRANS-1 and clone-1 on M-RULES-1/schema) had already written their merge reports on 2026-08-28 and were out of this clone's lane by construction.
3. The one open frame — whether the α = 0.5 / 0.1 detection profile holds on the real 80-song corpus once egress unblocks — is a parent-M-EAR-1 concern owned by the root conductor, not a preparation-chassis concern.

The auditor for each cycle recorded VALIDATED. The final auditor entry for the cycle range collapsed to a single-line decision because there was nothing new to weigh.

## Findings

### Regression spot-check against the cycle 1-3 baseline

| Check | Cycle 1-3 baseline | Cycle 4-6 state |
|---|---|---|
| `__PLACEHOLDER__` tokens in `docs/ear_preparation_report.md` | 0 | 0 (unchanged) |
| Byte-identity `leak_test_summary.det_run1.json ↔ leak_test_summary.json` | zero diff | zero diff (unchanged) |
| Load-bearing artifacts present | all present | all present (unchanged) |
| Cross-branch integration test §13 M-EAR-1 invariants | pass | pass (unchanged) |

No files under `scripts/ear/`, `data/ear/`, `_manager/`, or `docs/` were touched in cycles 4-6. No new shadow-ledger events were emitted from this clone. The plan-of-record was not edited.

### Success bars from cycle 1-3 (restated for the record, unchanged)

- Detection at α = 1.0: artist 91.4%, genre 100.0%, era 91.4% — all clear the ≥ 90% floor.
- False-positive rate on 20 no-leak Monte Carlo controls: 10.0% for all three leak types — meets the ≤ 10% ceiling exactly by 90th-percentile-of-controls calibration.
- CORN sanity training on synthetic labels: MAE 0.89 ± 0.11 vs 2.16 majority baseline and 1.55 mean-integer baseline; Kendall τ 0.74 ± 0.10.

### Non-factor isolation

No import of `scripts.classifier.sidecar_nonfactor` exists anywhere under `scripts/ear/`. The integration-test §13 scan continues to enforce this at merge time. Nothing changed this cycle range.

## Discussion

The value of a hold cycle is that it makes closure legible. A clone that stops producing artifacts because it hit a wall looks the same in the tree as a clone that stops producing artifacts because the scope is genuinely done. Cycles 4-6 make the second case explicit: the researcher's brief, worker's output, and auditor's verdict each name the closure and refuse to manufacture work that would obscure it.

Three anti-patterns were correctly refused:

- **Gold-plating.** Sweeping τ percentiles or extending epoch counts on already-VALIDATED metrics would inflate numbers without changing the validated conclusion.
- **Sibling-pivot.** Wandering into M-TRANS-1 or M-RULES-1/schema territory would violate cross-clone isolation and duplicate work already merged.
- **Fabricated advancement.** Re-emitting a fresh "deliverable" that only restates cycle 1-3's results would pollute the ledger without adding evidence.

None of the three were taken.

## Open Questions

Same as at cycle 3 exit, unchanged. All three belong to the parent M-EAR-1 training cycle owned by the root conductor once egress unblocks:

- Does the α = 1.0 / α = 0.1 detection profile hold on the smaller and imbalanced 80-song real corpus?
- Is the 2048-dim classifier embedding alone sufficient once real audio is available, or does VGGish materially reduce MAE?
- What is the right way to summarize the six CORN heads' confidence into a single rating decision for the downstream rules layer?

## Appendix: Provenance

**Cycle range:** cycles 4-6, clone 2 of fork 3168fb0e47a1.

**Session references:**

- Cycle 4: researcher `a5e2ee87-54ed-4652-ac0e-25df7891ebcc`, worker `ba205e1e-9940-4f39-8adb-0f76691de391`, auditor `0b494a2f-d969-4c6c-b0e2-98a32bbab429`.
- Cycle 5: researcher `18436659-5e41-48d2-ad5f-3cdda2dd759d`, worker `14141938-4b06-49ba-8e5b-2584a3990900`, auditor `625abe90-0bfd-4b94-94b2-aa504e415c45`.
- Cycle 6: researcher `83eae1cd-450a-4025-bc6c-ba0107265c13`, worker `7fc655f4-6e10-4e30-9450-0d8e2453c0a0`, auditor `26b28499-684a-45d9-8884-fb9626676c25`.

**Auditor verdict for the range:** VALIDATED. Rationale (verbatim): "Scope discharged; no work this cycle. State unchanged."

**Sibling status at exit** (unchanged from cycle 3 exit):

- Clone-0 (M-TRANS-1): merge report written 2026-08-28T07:18:06.
- Clone-1 (M-RULES-1/schema): merge report written 2026-08-28T07:29:27.
- Clone-2 (M-EAR-1/preparation): this report.

**Files touched this cycle range:** none under `scripts/ear/`, `data/ear/`, `_manager/`, `docs/`, or the plan-of-record. This report itself is the only new artifact and is a reader-facing summary of the hold, not new campaign state.

**Handoff to root conductor:** the six shadow-ledger events written at cycle 3 exit remain the load-bearing ledger surface for M-EAR-1/preparation. The chassis (features cache, CORN 6-head, leak-test harness with per-leak-type τ escalation) is ready for direct reuse the moment `M-INGEST-1/egress-probe` returns two consecutive `media_ok=true` rows.

<verdict>validated</verdict>
