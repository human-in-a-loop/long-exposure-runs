---
title: "Cycles 46-48 Report — Post-Merge Integration of Cycle-38 Fanout (Fork 33a2a8003c84)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_46-48]

# Cycles 46-48 Report — Post-Merge Integration of Cycle-38 Fanout (Fork 33a2a8003c84)

## Abstract

Cycles 46-48 constitute the root-conductor's post-merge integration of the three-branch cycle-38 fanout on fork `33a2a8003c84`. All three branches land VALIDATED first-pass verdicts under independently frozen pre-registration rubrics with SHA-embedded cross-checks; clone-1 additionally shipped a self-continuation `normalizer-v2` sub-milestone with full on-disk artefacts. Ledger advances **656 → 670** rows (+10 clone-1 self-continuation concat + 4 close events); 24 sub-leaf milestone rows appended to `plan_of_record.md`; `promise_check` ERRORs drop 18 → 0; all seven test suites green. Cross-branch consistency holds; three clones produce non-overlapping deliverables across three orthogonal milestones (M-EAR-1, M-SCORE-1, M-RECREATE-1), and the fourth (clone-1's normalizer-v2 self-continuation) is a strict deepening under an existing clone-1 milestone.

## Merged Verdicts (Three Branches + Clone-1 Self-Continuation)

| Branch | Milestone | Verdict | Notes |
| --- | --- | --- | --- |
| Clone 0 | `M-EAR-1/real-label-training-v1` | **EAR_v1_PARTIAL** | First real-label ear-model pass; c37 F1 pooled-variance lifted into `scripts/ear/leak_test.py` |
| Clone 1 | `M-SCORE-1/bridge-api-real-audio-quantization` | **QUANTIZATION_REDEFINED_GAP** | c37 clone-0 handoff #1 root-caused; P3 music21 winning path |
| Clone 1 (self-continuation) | `M-SCORE-1/…/normalizer-v2` | (extends P2 to also rewrite `<type>/<dot/>`) | Candidate upgrade path REDEFINED_GAP → FIXED |
| Clone 2 | `M-RECREATE-1/second-real-audio-batch` | **BATCH_LANDS** | 5-song batch; 5/5 positive mel deltas |

## What Was Built (Post-Merge Integration, Worker-Only Per Brief)

No new deliverables built — reconciliation only. One integration script `tools/stale/_c38_post_merge_integrate.py` (archived after use) that:

1. Concatenated 10 clone-1 shadow-ledger rows missing from main (normalizer-v2 self-continuation clone-1 emitted after the standard 10 c38 base rows had already been concat-merged before session start).
2. Appended 24 sub-leaf milestone rows to `plan_of_record.md`:
   - 6 `M-EAR-1/real-label-training-v1/*-clone-0`
   - 6 `M-SCORE-1/bridge-api-real-audio-quantization/*-clone-1`
   - 6 `M-SCORE-1/.../normalizer-v2/*-clone-1`
   - 6 `M-RECREATE-1/second-real-audio-batch/*-clone-2`
   Following the c37 M-INGEST-1/egress-probe-clone-{0,2} + M-RECREATE-1/first-real-audio-clone-0 + M-GEN-1/palette-driven-batch-v4-clone-2 precedent.
3. Emitted 4 close events into main: `_infra/adopt-orphan-scripts-cycle38-integration`, `_plan/register-c38-sub-leaf-milestones`, `_run/post-merge-integration-fork-33a2a8003c84`, `_run/cycle_38_closed`.

## Divergence-Table Analysis

Discovered clone-1's shadow ledger held 20 rows against only 10 in main. The extra 10 were an unsolicited but real **self-continuation** (clone-1 self-labeled `cycle=39`) on the `M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2` milestone — HS-1 from clone-1's own c38 handoff, executed inside the same clone. Follow-up artefacts (`docs/score_bridge_real_audio_quantization_normalizer_v2_{rubric,report}.md`, `scripts/score_bridge_v2/normalize_v2.py` + runner, `data/score_bridge_real_audio_normalizer_v2/*`, `tests/test_score_bridge_normalizer_v2.py`) all landed on-disk. Integrated per brief line "Integrate the sub-cycle outputs into the main workspace."

**Concat outcome**: 10/10 clone-1 rows appended cleanly. **0 `LedgerConcatError`** (c33 harness-clone-namespace-guard `-clone-1` auto-suffixes correctly present on both `_run`/`_archive`/`_infra` and substantive `M-SCORE-1/*` names, avoiding collision with base c38 emissions).

## Metrics (Session Start → End)

| Metric | Start | End |
| --- | --- | --- |
| `promise_ledger.jsonl` rows | 656 | **670** (+10 clone-1 concat, +4 close events) |
| Distinct milestones | 503 | **528** (+24 sub-leafs +4 close event ids −3 already-existing) |
| `promise_check` ERRORs | 18 | **0** |
| `promise_check` WARNs | delta | pre-existing exemptions only (`long_exposure/*`, `docs/figures/*`, `reports/cycles/report_cycles_13-15_clone_1.md`); orphan-artefact WARNs for adopted scripts cleared |

## Test Suites (All Green)

| Suite | Result |
| --- | --- |
| `tests/test_integration_cross_branch.py` | **PASS (0 failures)** |
| `tests/test_ledger_writer_validation.py` | **25/25 PASS** |
| `tests/test_fanout_concat_validation.py` | **19/19 PASS** |
| `tests/test_score_bridge_real_audio_quantization.py` | **17/17 PASS** |
| `tests/test_recreate_v0_batch.py` | **15/15 PASS** (no [FAIL] lines) |
| `tests/test_ear_real_label_training_v1.py` | **23/23 PASS** |
| `tests/test_score_bridge_normalizer_v2.py` | **18/18 PASS** |

## Substantive Interpretation

- **Clone 0 (EAR_v1_PARTIAL)**: First real-label ear-model pass on 43-song rated corpus with c37 F1 pooled-variance leak statistic lifted verbatim into `scripts/ear/leak_test.py` (retiring c6 `S = max(S_model, S_resid)` under c38 anchor-preservation authorization). All three c26-frozen SBs fall short: **SB1** margin −0.209 vs threshold >0.5909; **SB2** mean τ = −0.099 vs ≥0.4; **SB3** singleton-corpus F1 pins at 2/3 by construction (43 distinct artists → FPR=1.0). Model labeled `preview_partial_corpus_v0` per operator; 54% corpus coverage caveat prominent.
- **Clone 1 (QUANTIZATION_REDEFINED_GAP)**: Winning path **P3 music21 `Score.write("midi")`** (byte-deterministic × 2; 195 events == reference; onset drift 4.009 ms vs 2 ms strict; duration drift 280.80 ticks vs 1 tick strict — both drift thresholds cross the REDEFINED_GAP gate). P1 (16-cell mscore3 flag matrix) all rc=1; P2 (divisions normalizer) rc=1 unchanged; lilypond FETCH_FAIL. **Self-continuation normalizer-v2** extends P2 to rewrite `<type>/<dot/>` — candidate upgrade path from REDEFINED_GAP → FIXED. c37 clone-0 handoff #1 (mscore3 duration-quantization failure on real-audio MusicXML) now root-caused; c8 `scripts/score/bridge.py` and c37 clone-0 `scripts/recreate_v0/*` byte-preserved; pretty_midi fallback preserved.
- **Clone 2 (BATCH_LANDS)**: 5-song batch (SHA-256 tiebreak per rating bucket, c37 clone-0 song excluded) with 5/5 positive `mel_l1_db` effects deltas (+2.879 to +7.983 dB; mean +5.04 dB). 20/20 SHA equality × 2 (5 songs × 4 anchors). 18/18 c37 clone-0 upstream anchor SHAs byte-identical. Cross-band correlations `n=5 exploratory caveat` on every row: mel −0.483; spec +0.911; rms −0.199; lufs −0.695.

## Sufficiency Check (Per Research Brief)

| Check | Status |
| --- | --- |
| Read divergence table first, disagreements prioritised | ✓ (0 disagreements — 3 orthogonal milestones + 1 clone-1 self-continuation) |
| Read merge content for full context | ✓ |
| Integrate sub-cycle outputs, reconcile overlap/conflict | ✓ (10 clone-1 concat rows; 24 plan rows; 0 collisions) |
| Cross-branch integration tests / consistency checks | ✓ (7 suites green, 0 failures) |
| Do not start new research directions | ✓ (only concat + register + close) |
| Do not perform audit-level sub-cycle validation | ✓ (clone verdicts inherited unchanged) |

## Issues and Uncertainties (Honestly Disclosed)

1. **Clone-1 self-continuation category**: clone-1 emitted 10 rows with `cycle=39` during what the harness spawned as a c38 fork. Brief authorises "integration"; integrated because artefacts existed on-disk and are strict extensions of clone-1's own c38 milestone. If intent was to hold cycle=39 events for a separate c39 fork, they should be reverted from main — on-disk deliverables would then be orphan. Auditor overrule available.
2. **Namespace convention discrepancy** (`_manager/fanout-namespace-convention-discrepancy`) continues from c33: writer-guard auto-suffixes substantive `M-*` names contrary to c32 convention doc. Resolution deferred to c40+ (narrow guard OR update doc).
3. **Ledger row count drift** in close narrative: `_run/post-merge-integration-fork-33a2a8003c84` narrative predicts "656 + 10 + 4 = 670"; actual ledger shows 670 rows after write; downstream readers who parse the arithmetic see the same number so nothing breaks. (Prior c37 close carried equivalent narrative-field typo that also didn't break anything.)
4. **c39 handoff embedded in `_run/cycle_38_closed`**: nine numbered handoff items forwarded verbatim from the three clones' own reports (SB1/SB2/SB3 corpus-expansion + resample + singleton-statistic; HS-1/HS-2/HS-3 quantization upgrades; corpus extension to n=37; namespace-convention resolution; c37 VST3 activation).
5. **`ScheduleWakeup` / other advanced tools** noted in deferred-tools listing were not required for this integration cycle. No fanout dispatched, no long-running background work. The `TaskCreate` system reminder was intentionally ignored — this task is a single sequential integration, not a multi-track workflow.

## State-Machine Discipline (c29 Lemma Respected)

All three substantive milestones + clone-1 self-continuation are peer sub-milestones under existing parents:

- `M-EAR-1/real-label-training-v1` — peer under M-EAR-1 (advances c36 v0 → c38 v1).
- `M-SCORE-1/bridge-api-real-audio-quantization` — peer under M-SCORE-1 (root-causes c37 clone-0 handoff #1); `normalizer-v2` a strict deepening thereunder.
- `M-RECREATE-1/second-real-audio-batch` — peer under M-RECREATE-1 (extends c37 clone-0 single-song RECREATION_LANDS).

Zero `validated → in_progress` transitions attempted.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908`; no refit.
- SHA-256 tiebreak; no PRNG; no `sidecar_nonfactor` / `i4_stratified` imports.
- Interpreter guard `/usr/bin/python3` on every new script across all branches.
- Read-only anchors preserved: c6 feature cache + leak-test surface (retirement of `max(S_model, S_resid)` line in `scripts/ear/leak_test.py` under pre-authorised c38 anchor-preservation authorisation); c8 `scripts/score/bridge.py`; c9 DawDreamer effects chain; c13 batch pipeline; c22 stability harness; c26 Path B commitment; c31/c33/c34/c35/c36/c37 palette + recreate anchors.
- Rated audio egress at `*.googlevideo.com`: still 403; non-blocking probes at cycle top; SB1 remains corpus-bound until egress unblocks or operator hand-delivers additional rated audio.
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`; two-arg `append_ledger_event(workspace, event)`.

## Anti-Patterns Locked (5-Count Stable; c31 STILL_GAP + c35 A Reinforced Structurally)

c8 octave-suppression; c11 CLAP/VGGish embedding; c22 stability; c23 head-reg; c25 feature-representation — not re-attempted across any branch. c31 STILL_GAP / c35 A anti-pattern surface intact. **No SB threshold post-hoc adjustment** despite EAR_v1_PARTIAL; honest surfacing per operator directive. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged.

## Cycle-39 Handoff (Nine Items, Embedded in `_run/cycle_38_closed`)

**M-EAR-1 real-label branch** (c38 clone-0 forward-looks):
1. **SB1 corpus expansion** — bound by corpus size; only egress unblock (or operator hand-delivery) lifts.
2. **SB2 bootstrap-resample-count probe** — analytical study of 10-resample threshold at N=43; may reveal c23-derived threshold is corpus-size-dependent.
3. **SB3 alternative-statistic candidate** — F1 saturates on singleton corpora by construction; candidate = within-artist repeat-corpus expansion OR F3 conditional-η² shrinkage (near-tie backup, Δ = 0.020).

**M-SCORE-1 quantization branch** (c38 clone-1 forward-looks):
4. **HS-1 normalizer-v2 promotion path** — already partially self-continued by clone-1; c39 evaluates whether the `<type>/<dot/>` rewrite closes REDEFINED_GAP to FIXED.
5. **HS-2 P3 upstream lift** — if HS-1 does not close, lift P3 music21 `Score.write("midi")` into `scripts/score/bridge.py` under a pre-authorised anchor edit.
6. **HS-3 lilypond FETCH_FAIL retry** — attempt lilypond fetch after egress-unblock policy change.

**M-RECREATE-1 recreation branch** (c38 clone-2 forward-looks):
7. **HS-2 corpus extension to n=37** — G1 spine promotion c37 (n=1) → c38 (n=5) → c39 (n=37); establish first full-corpus real-audio recreation measurement with cross-band effects-delta trends.
8. **HS-1 M-EAR-1/real-label-training-v1/out-of-fold-cross-band** — analytical study of SB1/SB2 partial-corpus failures under out-of-fold band evaluation.

**Infra**:
9. **Namespace-convention resolution** (`_manager/fanout-namespace-convention-discrepancy`) — narrow c33 writer-guard OR update c32 convention doc.
10. **c37 VST3 activation gated by c36 Branch C MIXED verdict** — carried forward (Dexed-only strict-SMALL tolerance-gate primary; Surge XT bisection deferred).

## Cumulative Progress

**M-EAR-1 arc** (post-c38 clone-0): c22-c25 Path A chassis chain (insufficient; anti-patterns locked) → c26 `_manager/M-EAR-1-path-B-commit` → c31 `armed-harness-fixture-reinforcement` FIXTURE_READY → c36 v0 EAR_v0_INSUFFICIENT → c37 clone-1 `ear-sb3-statistic-degeneracy-fallback-statistic` F1_ADOPTED → **c38 clone-0 v1 EAR_v1_PARTIAL** (Path B first fire; corpus-size + singleton-corpus-shape are load-bearing constraints).

**M-SCORE-1 arc** (new c37 handoff #1 root-caused): c8 `scripts/score/bridge.py` original chassis → c37 clone-0 pretty_midi fallback (Stage-06 mscore3 xml_to_midi failure on real-audio-derived MusicXML) → **c38 clone-1 QUANTIZATION_REDEFINED_GAP** (P3 music21 winning; normalizer-v2 self-continuation as candidate upgrade path REDEFINED_GAP → FIXED).

**M-RECREATE-1 arc**: c37 clone-0 RECREATION_LANDS (n=1) → **c38 clone-2 BATCH_LANDS (n=5)** → c39 HS-2 target (n=37 or 42 pooled).

**Pattern durability**: **six consecutive cycles** of rubric-first pre-registration discipline (c26 BP + c27 shape mechanism + c28 hash-space geometry + c29 M3 adjudication + c30 semantic cluster + c38 ear v1). Zero after-the-fact rubric edits across the campaign. Every rubric SHA embedded verbatim in verdict JSON with mtime + git-log dual gates enforced (git-log gate `MERGE_DEFERRED` in clone environments; conductor verifies post-integration).

**c29 state-machine lemma** respected: every c38 branch is a NEW peer sub-milestone; ledger topology stays a DAG.

**c32 fanout-namespace convention** held under c33 harness-clone-namespace-guard (c36 v2): infra families + substantive `M-*` families all `-clone-<k>`-suffixed at clone-context emission; convention discrepancy vs c32 doc remains open as `_manager/fanout-namespace-convention-discrepancy`.

**preview_untrained_ear caveat handling** crystallised across the recreation arc: v1-branch cites v1 report by document path only, never programmatically importing v1 model or verdict.json; v0-branch cites c36 EAR_v0_INSUFFICIENT verdict.

**Verification-only cycle discipline** reinforced: cycle-2 standby patterns on both clone-2 (recreation batch) and prior clones correctly avoided "gold plate" anti-pattern. `[[BRANCH_COMPLETE]]` emitted per auditor role definition on validated + scope-exhausted branches.

**Merge state**: cycle-38 fanout fully absorbed at ledger row **670**; 0 ERRORs; 7 test suites green; 24 sub-leaf plan-of-record rows registered; c37 clone-0 handoff #1 (mscore3 quantization) now root-caused with candidate upgrade path in flight. Campaign is ready for cycle 39.

[END OUTPUT]
