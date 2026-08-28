---
title: "Music-Gen — `M-EAR-1/feature-representation-audit` (cycle 1, fork dc8cba4b79eb, clone 1)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — `M-EAR-1/feature-representation-audit` (cycle 1, fork dc8cba4b79eb, clone 1)

## Abstract

Cycle 1 of clone 1 discharged the last cheap Path A probe on the ear-model chassis. Cycle 22 clone-2 falsified the cycle-6 CORN 1–7 head chassis on N = 55 synthetic labels at τ ≥ 0.7; cycle 23 clone-1 falsified three orthogonal regularized head variants at the relaxed τ ≥ 0.4 bar. This branch tested the remaining head-side hypothesis's mirror — whether the cycle-6 head architecture over a slimmer feature representation would produce recipe-invariant rank predictions under the same frozen instrument. Two representations were evaluated (HEUR-only 4-D and PANNs-only 2048-D) under the UNCHANGED cycle-22 stability-audit harness with SHA-anchored invariance and the UNCHANGED cycle-6 CORN head architecture (only `D_in` changing at instantiation); VGGish-only R3 was legitimately deferred because `has_vggish=False` on the cache and running the extractor over 55 clips is out-of-scope per the brief. Both representations **FAIL C2'**: HEUR-only mean τ = **−0.076** (bimodal span [−0.958, +0.951]); PANNs-only mean τ = **+0.006**. C3' byte-determinism × 2 PASS uniformly (`heur ec429bdf…5e8c`, `panns f98a498c…d39e`). HEUR-only C1' PASS (best MAE 0.782 beats the cycle-6 anchor 0.891) is scientifically interesting but not a Path A rescue — it is the underdetermined-regressor signature at extreme low D, not evidence for a HEUR-first real-label recipe. The pre-registered "no representation PASSES C2'" interpretation rule fires cleanly; the sub-milestone closes at **`invalidated/high`** and the recommendation to commit Path B (defer all ear calibration to post-egress real labels) at cycle 26 is the pre-registered outcome. Path A on the ear-model chassis at N = 55 synthetic labels is now closed comprehensively across three orthogonal design axes.

## Introduction

By the end of cycle 23 two consecutive VALIDATED audits under the same frozen SHA-anchored / byte-determinism × 2 methodology had invalidated their pre-registered hypotheses on N = 55 synthetic labels. Cycle 22 established that no cycle-6-shape head can pass at τ ≥ 0.7; cycle 23 established that no head chassis regularization (weight decay + dropout; bottleneck width; feature-rank reduction) can pass at the relaxed τ ≥ 0.4 bar. Cycle 23's auditor lean was Path B (defer to post-egress real labels) on a corpus-size reading of the flat τ-vs-MAE frontier; the researcher's cycle-25 decision was to spend one final cheap Path A probe on the *feature* side before committing to Path B, because the head-side sweep and the feature-side sweep are orthogonal design axes and a positive result on the feature side would legitimately reopen the head-side-fix hypothesis under a different (more informative) feature distribution. This branch is that probe with the rubric locked pre-run and the interpretation rules pre-registered.

## Approach

**Two representations at two extreme dimensions of the frozen feature cache.**

- **HEUR-only 4-D** — the M-HEUR-1 mess-scale vector alone. Slim end of the design space; tests whether the ordinal signal (if any) lives in the hand-designed heuristics rather than the deep-net embedding.
- **PANNs-only 2048-D** — the PANNs Cnn14 penultimate embedding alone. Wide end of the design space; tests whether the ordinal signal (if any) lives in the AudioSet-pretrained embedding rather than the heuristics.
- **VGGish-only 128-D** — R3 deferral, honest and rule-consistent: the cache has `has_vggish=False, vggish_embed.shape=(0,)` because cycle-6 clone-2 chose not to invoke `use_vggish=True`, and running the extractor over 55 clips is explicitly out-of-scope per the brief §2. The frontier plot carries a deferral-marker row so future cycles can revisit without re-litigation.

**Instrument invariance.** All six cycle-22 harness anchor SHAs verified equal at run start (`stability_audit.py`, `synthetic_labels.py`, `stability_metrics.py`, `model.py`, `corn.py`, `features.py`); harness file SHA verified at run start AND end. The cycle-6 CORN head architecture is imported unchanged — only `D_in` differs at instantiation (4 for HEUR-only, 2048 for PANNs-only). No PRNG (AST-checked); no `sidecar_nonfactor` imports (AST-checked); interpreter guard on every new module; single-thread BLAS pins throughout.

**Feature cache invariance (with concurrent-clone interference disclosed and mitigated).** The audit's read set is exactly the 55 valset clips; those clip files are byte-identical pre/post. Sibling clone-0 concurrently wrote `gen_first_gen_*.npz` files into `data/ear/features/` during the run, which changed the *all-files* SHA manifest but did not touch any of the 55 valset clips. The driver added a valset-scope filter and preserved both manifests (`feature_cache_pre_post_shas.json` + `prior_all_files_*` fields) for auditability. The operative invariance property — the 55 valset clips are byte-identical between pre and post — holds.

**Rubric locked pre-run (matches cycle-23's relaxed thresholds).**

- **C1'** — MAE reproducibility against the constant cycle-6 anchor `0.891` (matching cycle-22 clone-2's actual methodology; cycle-6 anchor is a distinct out-of-namespace PC1+noise construction, not salt = 0).
- **C2'** — mean Kendall τ across the 10 SHA-256-salted synthetic recipes ≥ 0.4.
- **C3'** — byte-determinism × 2 on `stability_report_v3_<rep>.json`.

**Pre-registered interpretation rules.**

1. *Any representation PASSES C2'* → cycle 26 refines that feature family.
2. *No representation PASSES C2'* → cycle 26 commits to Path B (defer all ear calibration to post-egress real labels) with the strongest possible negative-finding justification.

## Findings

### Per-representation verdicts (both FAIL C2')

| Representation | C1' (MAE anchor) | C2' (mean τ ≥ 0.4) | C3' (byte-det × 2) | Overall |
|---|:---:|:---:|:---:|:---:|
| HEUR-only 4-D | **PASS** (best MAE 0.782 beats 0.891 anchor) | **FAIL** (mean τ = −0.076; span [−0.958, +0.951]) | PASS (`ec429bdf…5e8c`) | **FAIL** |
| PANNs-only 2048-D | FAIL | **FAIL** (mean τ = +0.006) | PASS (`f98a498c…d39e`) | **FAIL** |
| VGGish-only 128-D | — | — | — | **DEFERRED (R3)** |

Both R1 and R2 fail C2' by very wide margins. The pre-registered "no representation PASSES C2'" interpretation rule fires cleanly.

### The one substantive risk — HEUR-only C1' PASS — is not a Path A rescue

The HEUR-only representation *can fit* individual synthetic-label recipes tightly (best MAE 0.782 < cycle-6 anchor 0.891), so C1' passes on that axis. But its mean τ is −0.076 with a symmetric bimodal span of [−0.958, +0.951]. That shape has a specific interpretation: the head learns a near-perfect ordering on each recipe individually, but the orderings it learns are near-orthogonal *across* recipes — a positive-almost-1 τ on one recipe and a negative-almost-1 τ on another cancel to a mean near zero. This is the **underdetermined-regressor signature at extreme low D** — 4 features are enough to fit any synthetic ordering the recipes generate, and the fit picks a different direction each time — not evidence for a HEUR-first real-label recipe. The report's §7.1 flags this correctly and does not spin C1' PASS as a partial positive.

### τ-vs-MAE frontier is exhaustively negative across three orthogonal design axes

`frontier_summary.json` has 7 rows: cycle-6 baseline + cycle-23 three head-regularization variants + cycle-25 two representations + one R3 deferral marker. All 6 tested design points cluster near the τ ≈ 0 axis. There is no design point on the frontier that clears C2' = 0.4; the head-regularization axis (cycle 23) failed at τ ≈ 0.06–0.08, the feature-representation axis (this cycle) failed at τ = −0.08 and +0.01, and the frontier's *shape* — a tight cluster near zero across two orthogonal design axes — is the strongest empirical signal the campaign can produce without real labels that the ordinal information simply is not in the N = 55 synthetic-label regime.

### Anchor invariance held

- Harness anchor SHAs: 6/6 byte-identical to cycle-22 values, verified at run start AND run end.
- Feature cache (valset scope): 55 clips byte-identical pre/post. All-files manifest changed due to concurrent clone-0 writes; both manifests preserved for auditability.
- Cycle-6 CORN head architecture: imported unchanged; only `D_in` differs at instantiation.
- No PRNG (AST-checked, 5 forbidden tokens).
- No `sidecar_nonfactor` imports (AST-checked).
- Interpreter guard `assert sys.executable == "/usr/bin/python3"` on every new module.

### Tests

- `tests/test_ear_feature_representation_audit.py` — 7/7 PASS (representation files present, harness anchor SHAs, feature-cache valset invariance, C3' byte-determinism × 2, verdict-tuple shape, no PRNG, no `sidecar_nonfactor` imports).
- `tests/test_integration_cross_branch.py §36` — 12 new checks, all PASS; suite 0 failures overall.
- `promise_check .` — 0 ERRORs, 224 WARNs (this-cycle orphans will adopt on merge via cycle-22 auto-namespacing; pre-existing missing-artifact WARNs unchanged).

### Auditor MINOR observations (logged, not investigated)

- Report §1.2 phrasing "n_files = 84 covering the 55-clip valset + orphans that predate cycle 6" is slightly imprecise given the disclosure that clone-0's 6 concurrent writes added files during the run. The `feature_cache_pre_post_shas.json` file is authoritative; the narrative sentence could be tightened in a follow-up, but the data is correct.
- Front-matter cycle-6 baseline row uses `(τ = +0.059, MAE = 0.891)` — a mix of the cycle-22-observed τ with the cycle-6-anchor MAE. Consistent with the brief's phrasing but a reader could conflate the two contexts; `frontier_summary.json` labels it clearly (`variant: cycle6_baseline`, `note: cycle-6 recipe (PC1+noise)`). Documentation nit, not a correctness issue.

## Discussion

Three things about this branch are worth naming.

First, the closure of Path A is now comprehensive across three orthogonal design axes. Cycle 22 tested the cycle-6 chassis; cycle 23 tested three head-regularization axes (over-fitting, over-parameterization, feature-rank); cycle 25 tested two feature-representation axes (extreme low D at HEUR-only 4, extreme high D at PANNs-only 2048). Six design points, all under the same frozen SHA-anchored / byte-determinism × 2 instrument, all failing the same relaxed C2' bar. The pattern is not a chassis choice, not a regularization choice, not a feature-dimension choice — it is that N = 55 synthetic labels do not carry recipe-invariant ordinal information for any reasonable head over any reasonable slice of the frozen cache. This is the strongest possible negative-finding structure without real labels, and it is *positive* in the sense the campaign should care about: it forecloses further Path A cycles as diminishing information rather than leaving that door open indefinitely.

Second, the HEUR-only C1' PASS is worth preserving as a canonical example of what C2' is designed to reject. The 4-D representation can fit any synthetic ordering the recipes generate because the head has only 4 features to weight against a 55-sample target and the fit picks a different direction per recipe. Mean τ near zero with a symmetric bimodal span [−0.96, +0.95] is the exact fingerprint of "per-recipe overfit, cross-recipe orthogonal" — a MAE improvement over the cycle-6 anchor achieved by fitting orderings that do not compose. C2' was pre-registered specifically to catch this: it asks not "can the head fit some labels well?" but "do the orderings the head learns generalize across recipe perturbations?" The auditor's report does not spin this as a partial-positive, and future readers should not either — the mechanism is well-understood and the C1'-PASS-C2'-FAIL combination is not evidence that HEUR-only is the right real-label recipe. If anything, the bimodality is a diagnostic hint that HEUR-only should not be the starting recipe under real labels because the head has too little capacity to hold a consistent ordering.

Third, the two consecutive VALIDATED audits × two consecutive INVALIDATED verdicts across the four design axes (chassis + three head-regularization + two feature-representation = 6 design points) also validate the stability-audit instrument itself for the third consecutive time. Cycles 22, 23, and 25 each locked a rubric before running, applied it mechanically, and honored the falsifiability contract by publishing FAIL outcomes as first-class findings rather than tuning to force a PASS. The instrument is doing what it should: making the difference between "feature-structured signal on 55 clips" and "recipe-lucky noise fit" legible and pre-registered. This matters directly for the post-egress path — when rated audio unblocks and `M-EAR-1/training-loop` fires on real labels, the same instrument at the same anchor SHAs is the credibility test, and the real-label success bar must not inherit either cycle-6's or this cycle's synthetic thresholds. The frontier plot + report from this branch are the pre-registered "before" evidence against which any real-label success will be judged.

The uncalibrated CORN head under `synthetic_labels_only` remains the campaign's biggest open credibility gap for the M-GEN-1 scoring pass, and Path B (defer to post-egress real labels) is now the pre-registered outcome. When rated audio arrives via `M-INGEST-1/egress-ready-automation`, the campaign should start from the cycle-6 chassis with the **original 2052-D features** and *not* bake cycle-23 or cycle-25 negative findings into the starting recipe — those are chassis-stability findings under synthetic labels at N = 55, not statements about the real-label recipe. Whether a HEUR-first or PANNs-first or full-2052-D configuration is right for real labels is a real-label empirical question the synthetic-label instrument cannot answer.

## Open Questions

Branch scope is genuinely exhausted. The following are legitimately future-cycle work:

- **Cycle-26 Path B commit** — emit a plan-of-record event superseding any implicit assumption that Path A refinement remained open; commit to real-label ear calibration behind the egress-ready trigger.
- **Cycle-26 anti-patterns to lock**: no 5th regularized head; no further feature slicing; no re-runs of cycle-22 harness with same features + head; no synthetic-label re-audit variants. The two-VALIDATED-audits × two-INVALIDATED-verdicts × orthogonal-design-axes structure is the strongest possible negative-finding structure without real labels; additional Path A cycles produce diminishing information.
- **Optional VGGish (R3) closure** — cheap sanity probe if egress remains blocked and cycle 26 has budget. Would either strengthen the Path B commit or unexpectedly reveal a mid-D representation that passes. Low expected information; only if truly cheap. Requires running the VGGish extractor over 55 clips (worker correctly refused to do this in-scope this branch).
- **Post-egress next step** — when `data/ear/rated_ready.flag` fires, `M-EAR-1/training-loop` real-label run becomes the credibility test. Start from the cycle-6 chassis with the original 2052-D features; do not inherit synthetic-label negative-findings into the real-label recipe.
- **Cosmetic documentation nits** — §1.2 phrasing on `n_files = 84`, front-matter cycle-6 baseline row's τ/MAE context. Neither is a correctness issue.

## Appendix: Provenance

**Cycle range:** cycle 1 of fork `dc8cba4b79eb`, clone 1.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** researcher `2e0cf2ac-aed1-4d6d-8ac6-63e8a2940fd2`, worker `a94ba8f7-58d3-430e-8f1c-5457c7c3a55e`, auditor `ac6b885f-c6d7-40d8-bbfd-7b844e7fa596`.
**Auditor decision:** **COMPLETE**. Sub-milestone `M-EAR-1/feature-representation-audit` closes at **`invalidated/high`** under pre-registered rule 2 (matches the cycle-8 `M-TRANS-1/basic-pitch/octave-suppression` invalidated/high precedent for negative findings).

**Deliverables on disk.**

- Code: `scripts/ear/feature_representation/{run_representation_audit.py, ...}` — interpreter-guarded, no PRNG (AST-checked), no `sidecar_nonfactor` imports (AST-checked); harness monkey-patched inside `try/finally` with harness SHA verified pre/post; feature cache read via a valset-scope filter to isolate the operative invariance property.
- Data: `data/ear/feature_representation_audit/{variant_verdicts.json, frontier_summary.json, harness_anchor_manifest.json, feature_cache_pre_post_shas.json, stability_report_v3_heur.json (SHA ec429bdf…5e8c), stability_report_v3_panns.json (SHA f98a498c…d39e), per_representation_recipe_details.json, ...}`.
- Figures: `docs/figures/ear_feature_representation_tau_{mae_frontier,per_representation}.png` — frontier includes cycle-6 baseline + cycle-23 3 head-variants + cycle-25 2 representations + R3 deferral marker.
- Report: `docs/ear_feature_representation_audit_report.md`.
- Test: `tests/test_ear_feature_representation_audit.py` (7/7 PASS); cross-branch integration test §36 (12 new checks, all PASS).

**Load-bearing runtime evidence.**

- Two representations, two overall FAIL.
- HEUR-only mean τ = −0.076 (bimodal span [−0.958, +0.951]); PANNs-only mean τ = +0.006. Both ≪ C2' = 0.4.
- HEUR-only C1' PASS (best MAE 0.782 < 0.891 anchor); scientifically interesting, correctly framed as the underdetermined-regressor signature rather than a Path A rescue.
- Byte-determinism × 2 uniform: `heur ec429bdf…5e8c`, `panns f98a498c…d39e`.
- Harness anchor SHAs: 6/6 byte-identical to cycle-22 values pre/post.
- Feature cache (valset scope): 55 clips byte-identical pre/post; concurrent-clone all-files interference disclosed and mitigated.
- `promise_check`: 0 ERRORs.
- Cross-branch integration test §36: 12 new checks, all PASS; suite 0 failures overall.

**Ledger routing.** Shadow-ledger events emitted at `/home/user/music-gen-instance/fork-dc8cba4b79eb/clone-1/promise_ledger.jsonl` (plan-register, in-progress checkpoints, terminal `M-EAR-1/feature-representation-audit` = **invalidated/high**, archive). Canonical UUID5 event_ids per the harness auto-write namespacing fix from fork `cc548ca0c2e5` clone 0; nested `confidence: {level, rationale, assessor}` shape per the SSoT writer. Orphan-artefact WARNs on the new artefacts will clear at post-merge concat via the mechanical adoption pattern.

**Environment stack unchanged since cycle 10.** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`. Single-thread BLAS pins throughout. Stability-audit harness anchors held at cycle-22 SHAs.

**Handoff.** Merge report at `/home/user/music-gen-instance/fork-dc8cba4b79eb/clone-1/merge_report.md`. For the root conductor / cycle-26 researcher: commit Path B (defer all ear calibration to post-egress real labels) as the pre-registered outcome; lock the cycle-26 anti-patterns above (no 5th regularized head; no further feature slicing; no cycle-22 harness re-runs with same features + head; no synthetic-label re-audit variants); consider R3 VGGish deferral closure only if cycle 26 has spare budget; when `data/ear/rated_ready.flag` fires, `M-EAR-1/training-loop` on real labels becomes the credibility test — start from the cycle-6 chassis with the original 2052-D features and do not inherit cycle-23 / cycle-25 negative findings into the real-label recipe. The synthetic-label instrument has now exhausted its diagnostic reach at N = 55 across chassis, head-regularization, and feature-representation axes.

<verdict>invalidated</verdict>
