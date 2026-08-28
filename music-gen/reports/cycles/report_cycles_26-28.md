---
title: "Music-Gen — Cycles 26-28"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — Cycles 26-28

## Abstract

Cycles 26-28 covered the fork `dc8cba4b79eb` fanout — two clones testing the two open questions cycle 25 had left on the table — and its post-merge integration. **Clone 0** tested the cycle-14 collision-floor construction proof's distributional-shape prediction at N = 16 by running an unconditioned sampler (cycle-13 `sample_rules.py`, no rejection) on the I3-augmented 86-row ledger through the cycle-13 batch-v2 render pipeline verbatim. The rubric locked pre-run had CONFIRMS_PIGEONHOLE at ≥ 90 % of collisions in the four K = 15 rule_types, PARTIAL 60–90 %, REFUTES_PIGEONHOLE < 60 %; observed **26 collision pairs at N = 16 with {form, arrangement} = 26.9 %, K = 15 family (rhythmic + melodic + form + arrangement) = 76.9 %, and 6 of 26 pairs in the pigeonhole-forbidden harmonic bucket (K = 20)** — verdict **REFUTES_PIGEONHOLE / validated-high** and cycle-14's construction proof survives as a lower bound but fails as a distributional-shape predictor; the actual collision distribution is hash-birthday-shaped, not pigeonhole-concentrated. **Clone 1** ran the last cheap Path A probe on the ear-model chassis (HEUR-only 4-D and PANNs-only 2048-D representations under the cycle-22 harness with the cycle-6 CORN head architecture, only `D_in` changing); both **FAIL C2'** (HEUR-only mean τ = −0.076 with bimodal span [−0.958, +0.951] — the underdetermined-regressor signature at extreme low D, not a Path A rescue; PANNs-only mean τ = +0.006); VGGish-only R3 legitimately deferred. Terminal `invalidated/high` under pre-registered rule 2. Cycle 28's post-merge integration confirmed shadow-ledger auto-concat for the third consecutive fork under the cycle-22 harness-namespacing fix (13/13 shadow event_ids already present in the main ledger); no cross-branch conflicts (disjoint file trees; the only shared file was `tests/test_integration_cross_branch.py`, extended in disjoint sections §35 batch-v6 and §36 feat-rep); 4 rollup ledger events emitted through the SSoT writer (ledger 380 → 384 rows); `promise_check` 40 → 11 pre-existing WARNs, 0 ERRORs; all six test suites green (batch-v6 7/7; feat-rep 7/7; cross-branch §1–§36 0 failures; writer 21/21; concat 17/17; harness namespacing 7/7). Both landings are informative negative findings; Path A on the ear-model chassis at N = 55 synthetic labels is now closed comprehensively across three orthogonal design axes and cycle 26's next move is the pre-registered Path B commit.

## Introduction

By the end of cycle 25 two research questions were queued as concrete cycle-26 work. On the M-GEN-1 side, cycle 23's `NOT_TESTABLE_SAMPLER_EXHAUSTS_AT_N_GT_K` verdict on batch-v5-n16 with the I4 stratified sampler had left the cycle-14 construction proof's *distributional-shape* prediction empirically untested — I4's exclusion-set had converted the pigeonhole bound from *statistical must-collide* into *structural cannot-sample*, so the pigeonhole-concentration claim was structurally unfalsifiable within the I4 mechanism and needed a different sampler to test. Cycle 25's researcher named the two orthogonal paths that keep I4 untouched: Path 1 (`i4_replacement.py` sibling sampler that allows repeats past K), Path 2 (batch-v6 with the cycle-13 unconditioned `sample_rules.py` at N = 16). On the M-EAR-1 side, cycle 23 had exhausted the head-side-fix hypothesis at N = 55 synthetic labels across three orthogonal head-regularization axes, and cycle 25's researcher had staged the last cheap Path A probe on the feature side (two extreme representations at the frozen cache's dimensional ends) before committing to Path B. Cycle 26 was the worker pass running both branches; cycle 27 was the researcher pass framing the integration; cycle 28 was the integration itself.

## Approach

**Fork `dc8cba4b79eb` (two clones, disjoint file trees).**

- **Clone 0 (`M-GEN-1/batch-v6-unconditioned-n16`).** `scripts/gen/batch_v6_*` drives the compound run at N = 16 with the unconditioned sampler. Source: `data/rules/ledger_i3_dminor.jsonl` (86 rows). Sampler: cycle-13 `sample_rules.py` (no rejection, allows repeats). Render pipeline: cycle-13 `run_batch` from `scripts.gen.batch_v2` (imported verbatim). Cycle-9 pinned DawDreamer chain unchanged; SF2 pin `74594e8f…1cb0` inherited; determinism pins applied before any DawDreamer import. Writes to a distinct batch root `data/gen/batch_v6/` so all prior batch anchor trees (v2, v3_i3, v3_i4, v4, v5_n16) are physically untouched. Rubric locked pre-run in three arms: **CONFIRMS_PIGEONHOLE** (≥ 90 % of collisions in {form, arrangement}), **PARTIAL_CONFIRM** (60–90 %), **REFUTES_PIGEONHOLE** (< 60 %). Byte-determinism × 2 required.
- **Clone 1 (`M-EAR-1/feature-representation-audit`).** Two feature representations at extreme dimensions of the frozen cache: HEUR-only 4-D and PANNs-only 2048-D. VGGish-only R3 legitimately deferred because the cache has `has_vggish=False, vggish_embed.shape=(0,)` and running the extractor over 55 clips is out-of-scope per the brief §2. The cycle-22 stability-audit harness is a read-only anchor (6 harness anchor SHAs verified equal at run start; harness file SHA verified at run start AND end; feature cache byte-identical pre/post on the 55 valset clips). Cycle-6 CORN head architecture imported unchanged — only `D_in` differs at instantiation. Rubric matched cycle-23's relaxed thresholds: C1' MAE-in-envelope against the constant cycle-6 anchor 0.891 (cycle-22 methodology precedent); C2' mean τ ≥ 0.4; C3' byte-determinism × 2. Pre-registered rules: (1) any representation PASSES C2' → cycle 26 refines that feature family; (2) no representation PASSES C2' → cycle 26 commits to Path B.

**Cycle 27 (researcher).** Framed the fanout integration and the cycle-28 anti-patterns (no 5th regularized head; no further feature slicing; no cycle-22 harness re-runs with same features + head; no synthetic-label re-audit variants — the two-VALIDATED-audits × two-INVALIDATED-verdicts × orthogonal-design-axes structure is the strongest possible negative-finding structure without real labels).

**Cycle 28 (post-merge integration, worker-only).**

- Shadow-ledger auto-concat verification: enumerated `event_id`s in both `/home/user/music-gen-instance/fork-dc8cba4b79eb/clone-{0,1}/promise_ledger.jsonl` shadows (6 clone-0 + 7 clone-1 = 13 events) and confirmed all 13 already present in the main ledger via the cycle-22 harness-auto-write-namespacing fix. **Third consecutive fork to auto-concat cleanly**; cycle-21's per-clone-id-normalization workaround stays retired.
- Batch-anchor invariance: file counts unchanged since cycle 24 (`v2=62, v3_i3=62, v3_i4=62, v4=74`); new baselines `v5_n16=129, v6=138`; per-file SHAs preserved throughout. New aggregate SHAs recorded under a consistent method (relative-path + SHA + newline + concat, then SHA-256) as fresh baseline: `v2=be5726ab1cc843cf`, `v3_i3=42bdc33d33987f4e`, `v3_i4=b07c231b9373818a`, `v4=9e9444af3af4b5c1`, `v5_n16=2f17ab559c37881f`, `v6=eeff1663d600a21d`. Clone-0's own harness independently verified 5 batch anchors + 2 ledgers pre/post (7/7 PASS).
- Four rollup events emitted through `long_exposure.workspace_bootstrap.append_ledger_event`: `_infra/adopt-fanout-artifacts-fork-dc8cba4b79eb` (29 orphans adopted); `_infra/cross-branch-integration-test-cycle25` (all 6 suites green); `_run/post-merge-integration-fork-dc8cba4b79eb` (post-merge rollup); `_archive/integration-scratch-fork-dc8cba4b79eb` (emitter archived).
- Two ledger-schema drift patterns caught at emit time (self-corrected before final emission): field name `summary` vs canonical `narrative`, and non-canonical `run_id "run-cycle25-post-merge-fork-dc8cba4b79eb"` vs required `run-YYYY-MM-DDTHHMMSSZ` form. The SSoT writer's schema strictness did what it should; both surfaced at the writer gate rather than at post-merge audit.

## Findings

### Clone 0 — `M-GEN-1/batch-v6-unconditioned-n16` (validated/high, REFUTES_PIGEONHOLE)

**26 collision pairs at N = 16.** Per-rule-type breakdown:

| rule_type | K | pairs | share of 26 | pigeonhole-forbidden? |
|---|:---:|---:|---:|:---:|
| form | 15 | 4 | 15.4 % | no (K < N) |
| arrangement | 15 | 3 | 11.5 % | no (K < N) |
| rhythmic | 18 | 6 | 23.1 % | no (K < N) |
| melodic | 18 | 7 | 26.9 % | no (K < N) |
| harmonic | 20 | 6 | 23.1 % | **yes** (K ≥ N) |
| **total** | — | **26** | 100 % | — |

Rubric thresholds vs observed:

- {form, arrangement}: 26.9 % (below 60 % PARTIAL floor).
- K = 15 family (form + arrangement + the two K = 18 rule_types rhythmic + melodic): 76.9 % (below 90 % CONFIRMS bar and inside the PARTIAL 60–90 % band).
- **6 of 26 pairs in the harmonic bucket** where K = 20 ≥ N = 16 → pigeonhole *forbids* collisions there under a strict distributional-shape reading.

**Verdict: REFUTES_PIGEONHOLE.** The {form, arrangement} share is below the 60 % PARTIAL floor, and the 6 pigeonhole-forbidden harmonic pairs are the strongest single piece of evidence: if the pigeonhole bound predicted the distributional shape, no harmonic collisions would appear at N = 16 (K_harmonic = 20 > N), but they do. The construction proof from cycle 14 survives as a *lower bound* (I4 stratified rejection at K ≥ N provably eliminates within-rule_type collisions — confirmed empirically at cycle-15 clone-1 and cycle-16 clone-1) but fails as a *distributional-shape predictor* at N > K under unconditioned sampling: the actual collision distribution is **hash-birthday-shaped**, concentrated more or less uniformly across rule_types weighted by 1/K, rather than pigeonhole-concentrated in the K < N buckets. Byte-determinism × 2 held; prior batch anchors byte-identical pre/post (v2, v3_i3, v3_i4, v4, v5_n16 all unchanged); tests 7/7.

### Clone 1 — `M-EAR-1/feature-representation-audit` (invalidated/high, pre-registered rule 2)

| Representation | C1' (MAE anchor) | C2' (mean τ ≥ 0.4) | C3' (byte-det × 2) | Overall |
|---|:---:|:---:|:---:|:---:|
| HEUR-only 4-D | **PASS** (best MAE 0.782 beats 0.891 anchor) | **FAIL** (mean τ = −0.076; span [−0.958, +0.951]) | PASS (`ec429bdf…5e8c`) | **FAIL** |
| PANNs-only 2048-D | FAIL | **FAIL** (mean τ = +0.006) | PASS (`f98a498c…d39e`) | **FAIL** |
| VGGish-only 128-D | — | — | — | **DEFERRED (R3)** |

Pre-registered rule 2 fires: no representation PASSES C2'. The HEUR-only C1' PASS is the underdetermined-regressor signature at extreme low D (bimodal τ span [−0.958, +0.951] with mean near zero — per-recipe overfit, cross-recipe orthogonal), not a Path A rescue. The report §7.1 flags this correctly and does not spin C1' PASS as a partial-positive.

**τ-vs-MAE frontier is exhaustively negative across three orthogonal design axes.** `frontier_summary.json` has 7 rows: cycle-6 baseline + cycle-23 three head-regularization variants + cycle-25 two representations + one R3 deferral marker. All 6 tested design points cluster near τ ≈ 0; no design point clears C2' = 0.4. This is the load-bearing empirical finding: at N = 55, no reasonable head over any reasonable feature slice of the frozen cache produces cross-recipe-stable rankings under the C2' threshold.

### Cycle-28 post-merge integration

**Shadow-ledger auto-concat.** 13/13 shadow event_ids already present in the main ledger via the cycle-22 harness-auto-write-namespacing fix. Third consecutive fork to auto-concat cleanly.

**Test suites.**

| Suite | Result |
|---|:---:|
| `tests/test_batch_v6_unconditioned.py` | 7/7 PASS |
| `tests/test_ear_feature_representation_audit.py` | 7/7 PASS |
| `tests/test_integration_cross_branch.py` (§1–§36) | 0 failures |
| `tests/test_ledger_writer_validation.py` | 21/21 PASS |
| `tests/test_fanout_concat_validation.py` | 17/17 PASS |
| `tests/test_harness_report_namespacing.py` | 7/7 PASS |

**Cross-branch conflicts.** Zero. Disjoint file trees; the only shared file (`tests/test_integration_cross_branch.py`) was extended in disjoint sections (§35 batch-v6 vs §36 feat-rep).

**Batch-anchor invariance.** File counts unchanged since cycle 24 (v2 = 62, v3_i3 = 62, v3_i4 = 62, v4 = 74); new baselines v5_n16 = 129, v6 = 138; per-file SHAs preserved. New aggregate SHAs recorded under a consistent method for cycle 25 as a fresh baseline (per-file SHAs are byte-identical throughout; only the aggregate SHA differs across method changes).

**Rollup events + validators.** 4 events via SSoT writer (380 → 384 rows). `promise_check` 40 → 11 WARNs, 0 ERRORs — remaining 11 are all pre-existing carry-over (6 trailing-slash canonicalization on old rows; 1 `M-EAR-1` parent no-ledger-events roll-up pending post-egress; 4 upstream `long_exposure/*` + `report_cycles_13-15_clone_1.md` exempted/handoff).

**Ledger-schema strictness caught two drift patterns at emit time** (self-corrected before final emission): the field name `summary` was rejected in favour of the canonical `narrative`, and the non-canonical `run_id "run-cycle25-post-merge-fork-dc8cba4b79eb"` was rejected in favour of the required `run-YYYY-MM-DDTHHMMSSZ` form. The SSoT writer's schema strictness did what it should; both were caught at the writer gate rather than at post-merge audit.

### Cross-branch pattern (three consecutive successful stability-audit-instrument uses)

Cycles 22, 23, and 25 each fired the stability instrument on a distinct hypothesis (cycle-6 chassis alone; three regularized head variants; two feature representations), each pre-registered a threshold before running, and each honored the falsifiability contract by publishing the FAIL outcome as a first-class finding rather than tuning to force a PASS. Cycle 26 clone 0's REFUTES_PIGEONHOLE verdict is the analogous discipline on the M-GEN-1 side. Three consecutive M-EAR-1 audits + one M-GEN-1 audit = four consecutive rubric-locked-pre-run experiments that produced honest first-class outcomes without tuning to force PASS.

## Discussion

Three things about this range are worth naming.

First, clone 0's REFUTES_PIGEONHOLE verdict is a valuable clarification of the cycle-14 construction proof rather than a rebuttal of it. The proof's zero-collision claim at N ≤ K under I4 stratified rejection holds and has been empirically confirmed at cycle-15 clone 1, cycle-16 clone 1, and (in the partial N = 15 slice) at cycle-23 clone 0. What this branch falsifies is a *distributional-shape prediction* — the intuition that at N > K, collisions would concentrate in the K < N buckets by pigeonhole logic. On the actual unconditioned data at N = 16, the collision distribution is much closer to a hash-birthday shape (concentration by 1/K across all rule_types, including the K = 20 harmonic bucket where the pigeonhole *forbids* collisions but 6 still appear). This is worth preserving because the two claims are commonly conflated in informal talk about "the pigeonhole bound"; separating them lets future cycles reason about I4's construction proof and the unconditioned sampler's collision distribution as distinct properties. The I4 mechanism converts the birthday-shape collisions to zero at N ≤ K, and refuses to run at N > K; the unconditioned mechanism runs at any N and produces birthday-shape collisions; the pigeonhole bound gives a *lower bound* on the unconditioned collision count at N > K but does not predict the shape.

Second, clone 1's negative result closes Path A on the ear-model chassis exhaustively enough that continuing to sweep design axes at N = 55 would produce diminishing information. Cycle 22 tested the cycle-6 chassis; cycle 23 tested three head-regularization axes (over-fitting, over-parameterization, feature-rank reduction); cycle 25 tested two feature-representation axes (extreme low D at 4, extreme high D at 2048). Six design points, all under the same frozen SHA-anchored / byte-determinism × 2 instrument, all failing the same relaxed C2' bar. The pattern is not any specific chassis, regularization, or dimension — it is that N = 55 synthetic labels do not carry recipe-invariant ordinal information for any reasonable head over any reasonable slice of the frozen cache. Cycle 26 committing Path B (defer to post-egress real labels) is the pre-registered outcome; the anti-patterns cycle 27 locked (no 5th regularized head; no further feature slicing; no cycle-22 harness re-runs with same features + head; no synthetic-label re-audit variants) are the right guardrails against Path-A-scope-creep in the meantime.

Third, the cycle-28 integration was mechanical because the cycle-22 harness-auto-write-namespacing fix has now auto-concat'd three consecutive forks (cc548ca0c2e5 was the first proof; the two subsequent forks confirm the fix generalises). Combined with the SSoT writer catching two drift patterns at emit time this cycle (canonical `narrative` field name; canonical `run-YYYY-MM-DDTHHMMSSZ` `run_id` form), the ledger surface's move-to-catching-drift-at-the-writer-gate rather than at post-merge audit has now paid off across three cycles' worth of forks. The concrete win is that post-merge integration debt on the ledger side has approached zero as designed; the concrete cycle-29 action item worth naming is picking a canonical batch-anchor aggregation method and recording it in a locked utility so future cycles do not spin three different aggregate SHAs from three formatter choices while per-file SHAs stay byte-identical.

The uncalibrated CORN head under `synthetic_labels_only` remains the campaign's biggest open credibility gap. Path B is now the pre-registered outcome; when rated audio arrives via `M-INGEST-1/egress-ready-automation`, `M-EAR-1/training-loop` on real labels becomes the credibility test. The frontier plot from cycle 25 + this branch's report are the pre-registered "before" evidence against which any real-label success will be judged; the real-label success bar must not inherit either cycle-6's or the cycles-22/23/25 synthetic thresholds.

## Open Questions

- **Cycle-26 Path B commit** — emit a plan-of-record event superseding any implicit assumption that Path A refinement remained open; commit to real-label ear calibration behind the egress-ready trigger. (Pre-registered; researcher's task at cycle 26.)
- **Cycle-26 anti-patterns to lock**: no 5th regularized head; no further feature slicing; no cycle-22 harness re-runs with same features + head; no synthetic-label re-audit variants. Path A produces diminishing information.
- **Optional VGGish (R3) closure** — cheap sanity probe if egress remains blocked and cycle 26 has budget. Would strengthen the Path B commit or unexpectedly reveal a mid-D representation that passes. Low expected information; only if truly cheap. Requires running the VGGish extractor over 55 clips (worker correctly refused to do this in-scope this branch).
- **Canonical batch-anchor aggregation method** — cycle 29 should pick one and record it in a locked utility so future cycles do not spin three different aggregate SHAs from three formatter choices while per-file SHAs stay byte-identical.
- **Doc drift in clone-1 report** — figure paths reference `docs/figures/ear_feature_representation_tau_{mae_frontier,per_representation}.png` but on-disk figures are `docs/figures/ear_representation_{frontier,tau_per_variant}.png` (matches PoR). Figures exist; only the report text is wrong. Cycle-26 cosmetic fix.
- **Cycle-25 doc-drift on figure paths (feat-rep report §7)** — see cosmetic fix note.
- **`M-EAR-1` parent no-ledger-events WARN** — once cycle 26 emits the Path B commit event, this may or may not clear depending on whether the commit is under the parent or a new sub-milestone. Not blocking.
- **Post-egress next step** — when `data/ear/rated_ready.flag` fires, `M-EAR-1/training-loop` on real labels becomes the credibility test. Start from the cycle-6 chassis with the original 2052-D features; do not inherit cycle-23 / cycle-25 negative findings into the real-label recipe.
- **Distinction between construction-proof lower-bound and distributional-shape predictor** should be preserved in campaign-level documentation so future readers do not conflate them.
- **CORN-head calibration** and **rated-audio unblock** — still blocked on egress; will fire unattended through M-INGEST-1/egress-ready-automation when it triggers.

## Appendix: Provenance

**Cycle range:** cycles 26-28.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** cycle 26 worker `d4e57c51-8040-49f2-8c88-f8a17dc6f9df`; cycle 27 researcher `1788ecb0-536b-4050-a8d6-45ba23c3e4c9`; cycle 28 worker `d228d3e4-b176-479f-ab80-81367d124f11`.

**Clone verdicts.**

| Clone | Milestone | Verdict |
|---|---|---|
| 0 | `M-GEN-1/batch-v6-unconditioned-n16` | **validated/high** — REFUTES_PIGEONHOLE |
| 1 | `M-EAR-1/feature-representation-audit` | **invalidated/high** — pre-registered rule 2 fires (both representations FAIL C2'; VGGish R3 deferred) |

Clone 1 sub-agent transcripts: researcher `2e0cf2ac-aed1-4d6d-8ac6-63e8a2940fd2`, worker `a94ba8f7-58d3-430e-8f1c-5457c7c3a55e`, auditor `ac6b885f-c6d7-40d8-bbfd-7b844e7fa596`.

**Deliverables on disk at cycle-28 exit.**

- Clone 0: `scripts/gen/batch_v6_*`; `data/gen/batch_v6/` (138 files); `tests/test_batch_v6_unconditioned.py` (7/7 PASS); cross-branch integration test §35 (green).
- Clone 1: `scripts/ear/{feature_subset_adapter,representation_frontier,stability_audit_v3_representations}.py`; `data/ear/feature_representation_audit/*`; `docs/figures/ear_representation_{frontier,tau_per_variant}.png`; `docs/ear_feature_representation_audit_report.md`; `tests/test_ear_feature_representation_audit.py` (7/7 PASS); cross-branch integration test §36 (12 checks, green).
- Cycle-28 integration: workspace-root `merge_report.md` (cycle-25 fork capstone); `tools/stale/_emit_cycle25_integration_events.py`; 4 rollup events (`_infra/adopt-fanout-artifacts-fork-dc8cba4b79eb`, `_infra/cross-branch-integration-test-cycle25`, `_run/post-merge-integration-fork-dc8cba4b79eb`, `_archive/integration-scratch-fork-dc8cba4b79eb`).

**Load-bearing runtime evidence.**

- Clone 0: 26 collision pairs at N = 16; {form, arrangement} = 26.9 % (below PARTIAL 60 % floor); K = 15 family = 76.9 % (below CONFIRMS 90 % bar); 6/26 in pigeonhole-forbidden harmonic bucket (K = 20); byte-determinism × 2 held; prior batch anchors byte-identical pre/post.
- Clone 1: HEUR-only mean τ = −0.076 (span [−0.958, +0.951]); PANNs-only mean τ = +0.006; C3' byte-det × 2 uniform (`ec429bdf…5e8c`, `f98a498c…d39e`); harness anchor SHAs 6/6 byte-identical to cycle-22 values pre/post; feature cache (valset scope) byte-identical pre/post.
- Cycle 28: 13/13 shadow event_ids already in main ledger via cycle-22 auto-namespacing; ledger 380 → 384 rows; `promise_check` 40 → 11 WARNs, 0 ERRORs; all six test suites green.

**Ledger routing.** Clone 0 emitted 6 shadow events; clone 1 emitted 7 shadow events; both under the harness-namespacing fix so auto-concat cleanly at cycle 28. Cycle 28 emitted 4 rollup capstones through the SSoT writer with canonical UUID5 event_ids, nested `confidence: {level, rationale, assessor}`, `narrative` field name (self-corrected from `summary`), and canonical `run-YYYY-MM-DDTHHMMSSZ` `run_id` form (self-corrected). 29 orphan artefacts adopted (22 `data/ear/features/gen_first_gen_*.npz` = 16 pre-existing + 6 new from clone-0 batch-v6 side-writes; 5 `data/ear/stability_audit_c3check/*` carry-over; `tools/_audit_inspect.py` new; `tools/_audit_probe.py` carry-over).

**Batch-anchor state at cycle-28 exit.**

| Anchor | Files | Aggregate SHA (this cycle's method) |
|---|---:|---|
| batch_v2 | 62 | `be5726ab1cc843cf` |
| batch_v3_i3 | 62 | `42bdc33d33987f4e` |
| batch_v3_i4 | 62 | `b07c231b9373818a` |
| batch_v4 | 74 | `9e9444af3af4b5c1` |
| batch_v5_n16 | 129 | `2f17ab559c37881f` |
| batch_v6 | 138 | `eeff1663d600a21d` |

Per-file SHAs preserved throughout; aggregate SHAs differ from cycle-24's because the aggregation method differs — canonical method + locked utility hoisted to cycle 29 as a documentation cleanup.

**Environment stack unchanged since cycle 10.** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`; VGGish rung on the texture panel; CORN head under the `synthetic_labels_only` sentinel. Single-thread BLAS pins throughout. Stability-audit harness anchors held at cycle-22 SHAs.

**Rated audio.** Still egress-blocked per `corpus/CORPUS_STATUS.md`. `M-INGEST-1/egress-ready-automation` state machine remains `IDLE`; runtime state files correctly absent until the first live trigger. Not this range's problem; the machine is pre-wired.

**Handoff to next cycle.** The concrete downstream steps queued by this range are (a) cycle-26 Path B commit event for `M-EAR-1`; (b) locking the cycle-26 anti-patterns (no 5th regularized head, no further feature slicing, no cycle-22 harness re-runs, no synthetic-label re-audit variants); (c) optional VGGish (R3) closure only if cheap; (d) a canonical batch-anchor aggregation method and locked utility in cycle 29; (e) cycle-26 cosmetic fix to clone-1 report figure paths; (f) preserving the distinction between construction-proof lower-bound and distributional-shape predictor in campaign-level documentation. Anything requiring rated audio remains a straight-line consequence of the egress-ready state machine firing.
