---
title: "Music-Gen — Cycles 23-25"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — Cycles 23-25

## Abstract

Cycles 23-25 covered the fork `3fbd8c1ab57c` fanout — two clones testing the campaign's two most-open questions of the moment — and its integration. **Clone 0** empirically tested the cycle-14 collision-floor construction proof at N = 16 salts on the batch-v4 I3+I4 compound pipeline (I3-augmented 86-row ledger as source, I4 stratified sampler as sampler, cycle-13 batch-v2 render pipeline verbatim); the pre-run rubric locked CONFIRMS_CONSTRUCTION at ≥ 90 % of pairs attributed to the K = 15 rule_types {form, arrangement}, PARTIAL_CONFIRM at 60–90 %, CONFIRMS_H2_LARGER at < 60 %, and a sampler-pre-flight family for the case where the sampler itself cannot reach the target N. The I4 sampler raises `I4SamplerError` at salt = 15 on `rule_type = form` because K_form = 15 and all 15 form rules are already-picked after salts 0..14 — same by symmetry for rhythmic, melodic, arrangement (all K = 15) at N = 16; form is only first in `RULE_TYPES` iteration order. Salts 0..14 rendered cleanly with **60/60 byte-determinism × 2** and **32/32 anchor regression PASS vs batch-v4** on the salts-0..7 overlap. Verdict: **NOT_TESTABLE_SAMPLER_EXHAUSTS_AT_N_GT_K** (validated/high), a first-class positive empirical finding on the construction proof — at N > K per rule_type, I4's exclusion-set converts the pigeonhole floor from *must-collide* (statistical) into *cannot-sample* (structural), and `N_max_producible_by_I4(ledger) = min_K_across_rule_types(ledger) = 15` on the current augmented ledger. **Clone 1** responded to cycle-22 clone-2's invalidation of the CORN 1–7 head under synthetic-label recipe perturbation by building three regularized head variants (CORN-ridge, CORN-bottleneck, CORN-frozen-projector — spanning three orthogonal regularization axes: weight decay + dropout, bottleneck width, feature-rank reduction) and re-running each through the frozen cycle-22 10-recipe stability-audit harness with SHA-verified anchor invariance. All three variants **FAIL** the relaxed C2' bar (mean τ ≥ 0.4) by roughly 5× (variant τ ≈ 0.06–0.08), C3' PASS × 2 uniformly; sub-milestone closes at `invalidated/high` under pre-registered rule 2 with the first-class finding that the head is not the load-bearing failure surface at N = 55. Cycle 25 was the researcher pass framing the integration and the next-cycle plan-level decision (Path A feature-side redesign vs Path B defer to post-egress real labels).

## Introduction

By the end of cycle 22 two research questions were queued as concrete cycle-23 work. The cycle-14 construction proof — that I4's stratified rejection sampler drives the M-GEN-1 collision floor to zero at N ≤ K by construction — had been empirically confirmed at N = 8 (cycle-15 clone-1 on the source 76-row ledger, 0 pairs) and the I3+I4 composition had been confirmed at N = 8 on the augmented 86-row ledger (cycle-16 clone-1, 0 pairs, CONFIRMS_H0_STRICT with whole-song byte-identity on salt = 4). Both single-lever and compound tests were on the K ≥ N regime; the interesting regime for the *construction* proof is K < N, where the pigeonhole bound predicts a specific concentration of collisions in the rule_types whose K is smaller than N. On the ear-model side, cycle 22 clone-2 had invalidated the cycle-6 CORN head at N = 55 clips under the stricter τ ≥ 0.7 bar (mean τ = 0.059, cycle-6 MAE 0.891 below the observed 5th-percentile envelope minimum), leaving two pre-registered follow-ups: head-side fix via chassis regularization, or a corpus-size / feature-side fundamental limit. Cycle 23 was the worker pass running both fanout branches; cycle 24 was the worker pass finishing the batch-v5-n16 run through the sampler-exhaustion pre-flight discovery; cycle 25 was the researcher pass framing the integration and the next plan-level decision.

## Approach

**Fork `3fbd8c1ab57c` (two clones, disjoint file trees).**

- **Clone 0 (`M-GEN-1/batch-v5-n16`).** `scripts/gen/batch_v5_n16.py` drives the compound run at N = 16: `data/rules/ledger_i3_dminor.jsonl` (86 rows = 76 source + 10 D_minor variants) as SOURCE; `scripts/rules/sampling/i4_stratified.py` as SAMPLER (imported verbatim, grep-verified untouched); cycle-13 `run_batch` from `scripts.gen.batch_v2` as render pipeline (imported verbatim); cycle-9 pinned DawDreamer chain applies unchanged; SF2 SHA `74594e8f…1cb0` inherited; determinism pins applied before any DawDreamer import. Writes to a distinct batch root `data/gen/batch_v5_n16/` so all prior batch anchor trees are physically untouched. Rubric locked pre-run in five arms: **CONFIRMS_CONSTRUCTION** (≥ 90 % of pairs in {form, arrangement}), **PARTIAL_CONFIRM** (60–90 %), **CONFIRMS_H2_LARGER** (< 60 % — construction proof falsified), plus the sampler-pre-flight family for the case where the sampler cannot produce N samples at all. Salts-0..7 anchor regression against batch-v4 must be 32/32 byte-identical.
- **Clone 1 (`M-EAR-1/head-regularization-audit`).** Three regularized head variants covering three orthogonal regularization axes: **CORN-ridge** (L2 weight decay + higher dropout — targets over-fitting on the training-loss tail); **CORN-bottleneck** (32-D bottleneck, 4× narrower than cycle-6's 128-D — targets over-parameterization relative to N); **CORN-frozen-projector** (content-pinned PCA-64 projection of the PANNs component concatenated with the M-HEUR-1 4-D vector, feeding the same downstream ordinal head — targets feature-rank rather than head-shape; PCA basis SHA pinned at `9381ad73…`). The stability-audit harness from cycle 22 is a read-only anchor (six harness anchor SHAs verified equal to cycle-22 values at run start; `_fit` + `train_and_eval` monkey-patched inside a `try/finally` block with the harness file's SHA verified at run start AND end; feature cache byte-identical pre/post). Rubric locked pre-run: **C1'** MAE reproducibility against the constant cycle-6 anchor `0.891` (matching cycle-22 clone-2's actual methodology per its report §55; the brief's parenthetical about salt = 0 was factually wrong and the worker correctly ignored it); **C2'** mean τ ≥ 0.4 (relaxed from cycle-22's 0.7); **C3'** byte-determinism × 2. Pre-registered rules: (1) if any variant PASSES C2', the head-side-fix hypothesis is reopened; (2) if none does, the finding is first-class.

**Cycle 25 (researcher).** Framed the fanout integration and the next-cycle plan-level decision (Path A vs Path B on the ear track; Path 1 vs Path 2 on the batch-v6 side).

## Findings

### Clone 0 — `M-GEN-1/batch-v5-n16` (`validated/high`, `NOT_TESTABLE_SAMPLER_EXHAUSTS_AT_N_GT_K`)

The I4 stratified rejection sampler raises `I4SamplerError` at **salt = 15** on **rule_type = form** because K_form = 15 and all 15 form rules are already picked after salts 0..14. Same by symmetry for rhythmic, melodic, arrangement (also K = 15) at N = 16; form is only the first to exhaust in `RULE_TYPES` iteration order. Both run 1 (default output dir) and run 2 (temp dir) failed identically at salt = 15 with byte-identical prior-salt SHAs.

Salts 0..14 (N = 15) rendered successfully with:

- **60/60 byte-determinism × 2** on the 15-song partial batch across the tracked artefact set.
- **32/32 anchor regression PASS** against batch-v4 on the salts-0..7 overlap (all four file kinds byte-identical: musicxml / midi / bare / effects).
- **0 collision pairs** on the partial N = 15 batch (as expected: K = 15 ≥ N = 15 for every rule_type, so I4's construction proof still holds at N = 15).

The mechanism reading is precise: at N > K for any rule_type, I4's `already_picked` exclusion-set converts the birthday-paradox pigeonhole floor from a *must-collide statistical* prediction (which the un-conditioned sampler would exhibit) into a *cannot-sample structural* refusal. The construction proof's zero-collision claim at N ≤ K is preserved (the N = 15 partial batch is 0 pairs), but the pigeonhole bound at N > K is *unfalsifiable within the I4 mechanism* — the mechanism itself refuses to enter the regime where the bound would fire. The formal statement is:

    N_max_producible_by_I4(ledger) = min_K_across_rule_types(ledger)

For the current I3-augmented 86-row ledger, `N_max = 15`.

**Two cycle-24 orthogonal paths to test the construction proof at N > K without modifying I4:**

1. **New sibling sampler** `scripts/rules/sampling/i4_replacement.py` — accepts N > K by allowing repeats past K with an explicit collision-recording branch. Direct test of the pigeonhole prediction on the compound (I3+I4) source.
2. **Batch-v6 with un-conditioned sampler** — reuse cycle-13's `sample_rules.py` (no rejection) at N = 16 on the augmented ledger. Prediction: the pigeonhole floor manifests as observed collisions concentrated in the four K = 15 rule_types (rhythmic, melodic, form, arrangement).

Path 2 is closer to batch-v2's baseline and easier to reason about. Both keep I4 untouched. A `min_K < N` pre-flight guard on any future batch-vN driver at N > 8 is a small ledger-side follow-up.

**Test suite:** `tests/test_batch_v5_n16.py` 7/7 PASS; cross-branch integration test §33 0 failures. `_infra/adopt-batch-v5-artifacts` adopts all 250 files under `data/gen/batch_v5_n16/` + `tools/tmp_batch_v5_run2/` for post-merge `promise_check` cleanliness.

### Clone 1 — `M-EAR-1/head-regularization-audit` (`invalidated/high`, first-class rule-2 finding)

`variant_verdicts.json`:

| Variant | C1' (MAE anchor) | C2' (mean τ ≥ 0.4) | C3' (byte-det × 2) | Overall |
|---|:---:|:---:|:---:|:---:|
| CORN-ridge | FAIL (constant 0.891 vs env min 0.989) | FAIL (τ ≈ 0.06–0.08) | PASS (`be9a750e…`) | **FAIL** |
| CORN-bottleneck | FAIL | FAIL (τ ≈ 0.06–0.08) | PASS (`f224157c…`) | **FAIL** |
| CORN-frozen-projector | FAIL | FAIL (τ ≈ 0.06–0.08) | PASS (`5dd1c9da…`) | **FAIL** |

Three orthogonal head-side regularizations (weight decay + dropout; bottleneck width; feature-rank reduction) all land τ approximately 5× below the C2' bar. **Pre-registered rule 2 fires cleanly:** no variant passes C2', so the finding is first-class — the head is not the load-bearing failure surface at N = 55 clips.

**Anchor invariance held.** Harness anchor SHAs match cycle-22 values on all 6 harness files at both run start and run end (harness file SHA verified pre/post the monkey-patch); PCA basis SHA `9381ad73…` regenerates byte-identically in a fresh temp dir; feature cache SHA manifest byte-identical pre/post.

**τ-vs-MAE trade-off frontier is not really a frontier in this regime.** The three variants cluster tightly in τ (0.06–0.08) with modestly different MAE, and the baseline sits at the recipe-lucky point outside every variant's own envelope minimum. If the head chassis were near capacity, a genuine frontier would appear; a tight cluster near τ ≈ 0 is a corpus-size signal.

**Two auditor MODERATE observations, neither changes any verdict:** (1) report §7 line 241 says "no variant lands its cycle-6-recipe (nonlinear salt-4) MAE inside its own 10-recipe envelope" — false for `frozen_projector` (salt-4 MAE 1.1273 IS inside its envelope [1.0127, 1.9282]); but the C1' verdicts in the JSON are computed against the constant cycle-6 anchor `0.891` per cycle-22 precedent and all three still FAIL under that methodology; sentence conflates two interpretations, cosmetic. (2) The brief's parenthetical said "salt = 0 matches clone-2's cycle-6-anchor recipe" — factually wrong per cycle-22 clone-2's report §55 (cycle-6 anchor is distinct out-of-namespace PC1+noise); worker correctly used the constant-0.891 check.

**Test suite:** `tests/test_ear_head_regularization.py` 6/6 PASS; `tests/test_integration_cross_branch.py §34` all PASS; `promise_check` 0 ERRORs.

### Cycle-25 researcher pass

Framed the fanout integration and the cycle-26+ plan-level decision on both tracks. Named the M-GEN-1 next step as one of the two orthogonal paths that keep I4 untouched (Path 1 replacement-sampler sibling, or Path 2 batch-v6 un-conditioned sampler on the augmented ledger). Named the M-EAR-1 next step as the Path A / Path B decision with auditor's lean toward Path B (defer to post-egress real labels) on the corpus-size reading of the head-regularization audit's flat frontier.

### Validators at cycle-25 exit

- Adopted branch artefacts under `_infra/adopt-batch-v5-artifacts` (250 files) + the mechanical orphan-adoption pattern for the head-regularization audit (2 orphan-artefact WARNs on `variant_verdicts.json` / `frontier_summary.json` cleared at post-merge concat).
- `promise_check` 0 ERRORs across the fanout integration.
- Cross-branch integration test §33 (batch-v5) + §34 (head-regularization) 0 failures.

### Two-cycle instrument validation

Two consecutive VALIDATED audits under the same frozen-harness / SHA-anchored / byte-determinism × 2 methodology (cycle 22 on the cycle-6 chassis at τ ≥ 0.7; cycle 23 on three regularized variants at τ ≥ 0.4) both invalidated their pre-registered hypotheses on N = 55 synthetic labels. This is a validation of the stability-audit instrument itself: it is making the difference between "feature-structured signal on 55 clips" and "recipe-lucky noise fit" legible and pre-registered, and honoring the falsifiability contract by publishing FAIL outcomes as first-class findings rather than tuning to force a PASS. Future ear-model calibration under real ratings must reuse this instrument at the same harness anchor SHAs.

## Discussion

Three things about this range are worth naming.

First, the batch-v5-n16 verdict is a rare kind of result — a *mechanism-level* first-class finding rather than a metric-level one. The pre-run rubric anticipated three outcomes at N = 16 (construction proof confirmed, partially confirmed, or falsified) plus the sampler-pre-flight family; what actually happened was the sampler-pre-flight family firing *post-hoc* rather than pre-flight, because the exhaustion is data-dependent and only manifests at the exact salt where `already_picked` covers the smallest pool. The verdict `NOT_TESTABLE_SAMPLER_EXHAUSTS_AT_N_GT_K` names a specific structural property of I4 rather than a numerical outcome: the sampler's exclusion-set converts the pigeonhole bound from *statistical must-collide* into *structural cannot-sample*. This is *stronger* than any of the three anticipated numerical outcomes for the specific question "does I4 preserve its construction proof at N > K?" — the answer is that I4 preserves its zero-collision claim at N ≤ K and *refuses* to enter the N > K regime, so the construction proof is not just unfalsified but structurally unfalsifiable within the mechanism. The pigeonhole prediction remains testable *outside* the I4 mechanism, and both cycle-24 paths (replacement-sampler sibling, or batch-v6 un-conditioned sampler) do exactly that without modifying I4.

Second, the head-regularization audit produces its most useful evidence in the *shape* of the τ-vs-MAE frontier rather than in the individual variant τ values. Three orthogonal regularization axes producing coincident τ ≈ 0.06–0.08 is not just "the head is bad" — it is "the axes that would separate the variants at a larger N produce coincident results here, so the head has effectively no ordinal information to trade against MAE on N = 55 clips." That is a corpus-size signal read out of the frontier's geometry, not out of any single metric. Combined with the cycle-22 finding that the cycle-6 MAE 0.891 is recipe-lucky under its specific PC1+noise construction rather than a stable property, the two cycles now converge on the same reading: N = 55 is where the synthetic-label instrument runs out of diagnostic reach in both stricter (τ ≥ 0.7) and relaxed (τ ≥ 0.4) modes. Path B (defer to post-egress real labels) is the honest default under this reading; Path A (feature-side redesign) is worth one cycle if a specific concrete probe is at hand (class-supervised projection on M-CLASS-1's 5-class label, or a VGGish concat rung reproducibility retry), and if Path A also lands FAIL then Path B is forced.

Third, this range strengthens the campaign-level pattern that the diagnostic instruments' *own* falsifiability discipline is the load-bearing invariant. Cycles 22 and 23 both invalidated pre-registered hypotheses; cycles 15 and 16 both empirically confirmed pre-registered mechanistic predictions; cycle 23's batch-v5 discovered a pre-flight family firing post-hoc as a first-class outcome. In every case the rubric was locked before the run, the verdict was applied mechanically, and the honest outcome (positive, null, or mechanism-structural) was published rather than tuned. This is why the campaign now has a coherent multi-cycle story on both tracks: on M-GEN-1, I4 is empirically zero at K ≥ N with I3 as complementary safety margin, and I4 is structurally undefined at N > K; on M-EAR-1, three orthogonal head chassis fail at N = 55 under both stricter and relaxed τ bars, so head-side chassis-tuning is not the mechanism for closing the credibility gap synthetically. Real labels via M-INGEST-1/egress-ready-automation remain the mechanism that closes the credibility gap substantively; nothing in this range changes that, and nothing needs to.

## Open Questions

- **Cycle-26 batch-v6 path** — either Path 1 (`i4_replacement.py` sibling sampler) or Path 2 (un-conditioned `sample_rules.py` at N = 16 on the augmented ledger). Path 2 is closer to batch-v2's baseline and easier to reason about. Both keep I4 untouched.
- **`min_K < N` pre-flight guard** on any future batch-vN driver at N > 8. Small ledger-side follow-up that would surface the sampler-exhaustion condition before the run rather than at salt = min_K.
- **Path A vs Path B decision** for the M-EAR-1 track. Auditor's lean is Path B (defer to post-egress real labels); Path A is one cycle if a specific concrete probe (class-supervised projection on M-CLASS-1's 5-class label, or a VGGish concat rung reproducibility retry) is queued.
- **Cosmetic fix to `docs/ear_head_regularization_audit_report.md` §7 line 241** to reflect the actual C1' definition (constant cycle-6 anchor 0.891 vs variant envelope) rather than the incorrect "salt-4 inside envelope" phrasing. Verdicts are correct; only the sentence is wrong.
- **When ratings audio unblocks**, fire `M-EAR-1/armed-harness` on real labels *without* inheriting either cycle-6's or this cycle's synthetic success bar; re-run this range's three regularized variants under real labels alongside the armed-harness training.
- **No further head-shape variants** on the N = 55 valset. Three orthogonal axes have been exhausted; a fourth would be scope-creep.
- **Future briefs should not repeat the "salt = 0 = cycle-6 anchor" mis-statement.** The cycle-6 anchor is distinct-out-of-namespace PC1+noise per cycle-22 clone-2's report §55; C1' methodology is the constant-0.891 check.
- **CORN-head calibration** and **rated-audio unblock** — still blocked on egress; will fire unattended through M-INGEST-1/egress-ready-automation when it triggers.

## Appendix: Provenance

**Cycle range:** cycles 23-25.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** cycle 23 researcher `c78e1df6-7be0-45ed-bd3b-bf1b960a84f5`; cycle 24 worker `297f74bf-dcf1-4cc3-bb11-55762d9b872b`; cycle 25 researcher `9e8cdc04-cedc-4fe5-942f-a461ba11ef6d`.

**Sub-agent transcripts (fork `3fbd8c1ab57c` clones).**

- Clone 0 (`M-GEN-1/batch-v5-n16`): worker delivered `NOT_TESTABLE_SAMPLER_EXHAUSTS_AT_N_GT_K` at `validated/high` as a first-class empirical finding on the cycle-14 construction proof.
- Clone 1 (`M-EAR-1/head-regularization-audit`): researcher `12064f4e-8b06-4d71-b114-b1652d717cd7`, worker `70e33e5b-e8ed-4a67-bc67-fff51e102c19`, auditor `e4296994-05aa-4137-920d-465c4cbfcadf`. Auditor decision COMPLETE; sub-milestone closes at `invalidated/high` under pre-registered rule 2.

**Deliverables on disk at cycle-25 exit.**

- Clone 0: `scripts/gen/{batch_v5_n16.py, collision_count_batch_v5.py, batch_v5_anchor_regression.py, batch_v5_hypothesis_verdict.py, batch_v5_finalize_partial.py}`; `data/gen/batch_v5_n16/{15 song folders, batch_manifest_partial.json, batch_v4_anchor_reference.json, anchor_regression.json (32/32 PASS), determinism_run1_vs_run2.json (60/60 PASS), collision_analysis.json (0 pairs), collision_analysis_partial_N15.json, hypothesis_verdict.json, collision_matrix.tsv, summary.tsv}`; `docs/figures/batch_v5_n16_{grid, collision_heatmap, attribution}.png`; `docs/gen_batch_v5_n16_report.md`; `tests/test_batch_v5_n16.py` (7/7 PASS); cross-branch integration test §33 (0 failures); `tools/tmp_batch_v5_run2/` (second-run scratch, adopted); `tools/logs/batch_v5_run{1,2}.log`.
- Clone 1: `scripts/ear/head_regularization/{corn_ridge.py, corn_bottleneck.py, corn_frozen_projector.py, run_variant_audit.py, ...}`; `data/ear/head_regularization_audit/{variant_verdicts.json, frontier_summary.json, harness_anchor_manifest.json, feature_cache_pre_post_shas.json, stability_report_v2_<v>.json × 3, per_variant_recipe_details.json, pca_basis_9381ad73.npy}`; `docs/figures/ear_head_regularization_tau_{mae_frontier, per_variant}.png`; `docs/ear_head_regularization_audit_report.md`; `tests/test_ear_head_regularization.py` (6/6 PASS); cross-branch integration test §34 (all PASS).

**Load-bearing runtime evidence.**

- Batch-v5-n16 verdict: NOT_TESTABLE_SAMPLER_EXHAUSTS_AT_N_GT_K. Sampler exhausts at salt = 15 on form (K_form = 15); by symmetry rhythmic, melodic, arrangement (all K = 15) at N = 16. Salts 0..14 rendered with 60/60 byte-determinism × 2; salts-0..7 anchor regression 32/32 PASS vs batch-v4; 0 collision pairs on the partial N = 15 batch.
- N_max_producible_by_I4(augmented ledger) = min_K_across_rule_types = 15.
- Head-regularization: three variants, three overall FAIL; τ ≈ 0.06–0.08 across all three (~5× below C2' = 0.4); C3' PASS × 2 uniformly (ridge `be9a750e…`, bottleneck `f224157c…`, frozen_projector `5dd1c9da…`).
- Harness anchor SHAs: `match: true` on 6 harness files pre-run; re-verified at audit time.
- Feature cache pre/post: `byte_identical: true`.
- PCA basis pinned at `9381ad73…`; regenerates byte-identically in fresh temp dir.
- `promise_check`: 0 ERRORs.
- Cross-branch integration test suite: 0 failures with §33 (batch-v5) and §34 (head-regularization) added.

**Ledger routing.** Clone 0 emitted 7 shadow-ledger events (2 from prior session + 5 from this session, including `_infra/adopt-batch-v5-artifacts` adopting 250 files under `data/gen/batch_v5_n16/` and `tools/tmp_batch_v5_run2/`). Clone 1 emitted 7 shadow-ledger events (plan-register, 4 in-progress checkpoints, terminal invalidated/high with 20 artefacts listed, archive). Canonical UUID5 event_ids per the harness-namespacing fix from fork `cc548ca0c2e5` clone 0; nested `confidence: {level, rationale, assessor}` shape per the SSoT writer. Two pre-integration orphan WARNs on `data/ear/head_regularization_audit/{variant_verdicts, frontier_summary}.json` cleared at post-merge concat via the standard adoption pattern.

**Environment stack unchanged since cycle 10.** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`; VGGish rung on the texture panel; CORN head under the `synthetic_labels_only` sentinel. Single-thread BLAS pins throughout. Stability-audit harness anchors held at cycle-22 SHAs.

**Rated audio.** Still egress-blocked per `corpus/CORPUS_STATUS.md`. `M-INGEST-1/egress-ready-automation` state machine remains `IDLE`; runtime state files correctly absent until the first live trigger. Not this range's problem; the machine is pre-wired.

**Handoff to next cycle.** The concrete downstream steps queued by this range are (a) cycle-26 batch-v6 path selection — Path 1 (`i4_replacement.py` sibling sampler) or Path 2 (un-conditioned `sample_rules.py` on the augmented ledger at N = 16) — both keeping I4 untouched; (b) the `min_K < N` pre-flight guard for any future batch-vN driver at N > 8; (c) Path A vs Path B decision on the M-EAR-1 track (auditor's lean is Path B, defer to post-egress real labels); (d) the cosmetic §7 line 241 fix on the head-regularization audit report. Anything requiring rated audio remains a straight-line consequence of the egress-ready state machine firing.
