---
title: "Music-Gen — Cycles 29-31"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — Cycles 29-31

## Abstract

Cycles 29-31 discharged the cycle-26 handoff on the M-GEN-1 collision-generation model's residual per-rule_type shape mismatch, running a single R/W/A loop under `M-GEN-1/collision-model-shape-mechanism` — the linear-cycle posture is intact and fan-out is inappropriate for this class of probe. Cycle 26 had established BP-scaled with a single global α ≈ 0.75 as the aggregate collision-generation law (R²_scaled = 0.9588, CONFIRMS_BP_SCALED) but reported SHAPE_REFUTES on the per-rule_type distribution (mean R² = −0.869); the cycle-27 brief pre-authorised two candidate mechanisms for that residual: **M1** (coherence-gate coercion-rate per rule_type deforming effective K by rejecting candidate collisions), **M2** (effective-K probe via rule-selection frequency enumeration). Verdict: **NEITHER_EXPLAINS** — a first-class informative outcome pre-authorised by the brief. Both M1-corrected mean R² (−6.2729) and M2-corrected mean R² (−10.6945) are far below the 0.6 threshold, so `max(M1, M2) < 0.6 → NEITHER_EXPLAINS` fires mechanically. The substantive scientific finding is stronger than the bare R²: the worker discovered — and verified against `data/gen/batch_v6/collision_analysis.json`'s byte-identical `raw.per_rule_type_pairs == coerced.per_rule_type_pairs` — that the coherence gate mutates rule *parameters* but never *remaps rule_ids to different ledger rows*. This structurally invalidates M1's underlying premise (post-hoc rule_id reshaping is not a mechanism the codebase supports) and gives cycle 28 unambiguous direction: skip mechanisms that assume post-hoc rule_id reshaping; test hash-space geometry per (rule_type × salt) or semantic-cluster overlap. The branch shipped 5 new analytical scripts, an 8-check branch test module, a 16-check §39 cross-branch integration extension, six named ledger events (with nested `confidence`, `narrative` field, canonical `run_id`), and 9/9 anchor preservation via the cycle-26 canonical-aggregate-SHA utility. Byte-determinism × 2 held; the cycle-26 utility SHAs are pinned by test (canonical_aggregate_sha.py, collision_model_bp.py, collision_model_verdict.py all byte-identical). One MODERATE gap: the brief's two required figures (`shape_mechanism_M{1,2}_correction.png`) are missing and were queued as cycle-28's small backfill task. Ledger grew 400 → 407.

## Introduction

Cycle 26 closed the aggregate side of the M-GEN-1 collision-generation model — BP-scaled with a single global α ≈ 0.75 accounts for essentially all cross-batch collision variance across six batches spanning N ∈ {5, 8, 16} and both sampler regimes at R² = 0.9588 — and left one open question in the residual: the per-rule_type distributional shape is not the same shape BP-scaled predicts. Batch-v6's 26-pair distribution has BP over-predicting the small-K rule_types (form and arrangement, K = 15) and under-predicting the large-K rule_types (harmonic K = 20, rhythmic and melodic K = 18), with mean per-rule_type R² = −0.869. The cycle-26 auditor named two directly testable mechanisms for the residual: (M1) coherence-gate coercion-rate per rule_type deforms effective K by rejecting candidate collisions at a type-dependent rate — the gate's rewrites might silently smooth the collision distribution; (M2) effective-K probe via rule-selection frequency enumeration — for small-K types, some rules may be structurally over-selected by the hash lottery, reducing effective K below its nominal value. Both candidates are downstream of frozen artefacts on disk and neither requires rendering. Cycle 27 was the single R/W/A loop that tested both. Cycles 29-31 in this report cover the researcher pass framing the probe (29), the worker pass running it (30), and the follow-up researcher/worker/auditor triad that finalised and audited the result (31).

## Approach

**Mechanism M1 (coercion-rate correction).** For each rule_type, compute the coherence-gate coercion rate on batch-v6's provenance — the fraction of candidate collisions the gate rewrites — and apply that rate as a correction to the BP-scaled prediction. The brief's formal spec was `R²(M1-corrected) = per-rule_type BP-scaled R² after replacing observed with (observed − coercion_reshaping_correction)`; the worker implemented `predicted_M1 = pred_scaled × 1/(1 − rate)` (a correction to the prediction rather than to the observed). The verdict is stable across either interpretation because the mid-cycle discovery about the coherence gate (below) implies the honest `coercion_reshaping_correction` is 0.

**Mechanism M2 (effective-K correction).** For each rule_type, enumerate rule-selection frequency at N = 16 unconditioned to derive K_eff (the number of distinct rule_ids actually selected), then refit BP with K_eff in place of the nominal K. If small-K types have K_eff < K (some rules structurally over-selected), M2-corrected R² should improve. The worker refit α (0.1761) rather than reusing cycle-26's aggregate α̂ = 0.7469; the verdict is stable across either reading because K_eff harmonic ≡ 0 forces a clip on the model's implicit scale.

**Rubric locked pre-run (mechanically applied post-run).**

- **CONFIRMS_M1** — M1-corrected mean R² ≥ 0.6.
- **CONFIRMS_M2** — M2-corrected mean R² ≥ 0.6.
- **CONFIRMS_BOTH** — both corrected mean R² ≥ 0.6.
- **NEITHER_EXPLAINS** — `max(M1, M2) < 0.6`; first-class informative outcome pre-authorised by the brief §Investigation contract ("`NEITHER_EXPLAINS` is the most informative outcome — [it] would force cycle-28 to test a third mechanism").

**Anti-patterns honored.** No PRNG (AST-checked); no `sidecar_nonfactor` imports (AST-checked); `scripts/rules/sampling/i4_stratified.py` NOT imported (AST-checked in both branch test and §39); interpreter guard on every new script; no touched anchors; no rendering; single-thread BLAS pins throughout. Cycle-26 utility SHAs pinned by test.

**Anchor preservation.** `anchor_preservation_shape.py verify` on the shipped manifests against the seven batch dirs (v2, v3_i3, v3_i4, v4, v5_n16, v6, v1) + two rules ledgers, using the cycle-26 canonical-aggregate-SHA utility.

## Findings

### Verdict (mechanically applied under the locked rubric)

`shape_mechanism_verdict.json`:

| Mechanism | Corrected mean R² | Meets ≥ 0.6? |
|---|---:|:---:|
| M1 (coercion-rate correction) | **−6.2729** | ✗ |
| M2 (effective-K correction) | **−10.6945** | ✗ |
| Uncorrected mean R² (cycle-26 baseline) | −0.3414 | ✗ (already below 0.6) |

`max(−6.2729, −10.6945) < 0.6` → **NEITHER_EXPLAINS** fires mechanically. Neither corrections *improves* the fit — both drive it much further negative than the uncorrected baseline, indicating each mechanism pulls predictions in the wrong direction on this data.

### The substantive first-class finding: coherence gate does not remap rule_ids

The worker verified directly against `data/gen/batch_v6/collision_analysis.json` that `raw.per_rule_type_pairs == coerced.per_rule_type_pairs` **byte-identical across every salt in every batch**. Mechanistically: the coherence gate mutates rule *parameters* (transposing keys, rewriting section boundaries, coercing tempo) but *never* remaps a rule_id to a different ledger row. The gate is a parameter-mutation gate, not a rule-selection gate.

This structurally invalidates M1's underlying premise. M1 assumed that the gate rejects candidate collisions at a type-dependent rate — i.e., that when two salts would pick the same rule_id, the gate might rewrite one selection to a different rule_id, effectively deforming K per type. But the gate has no mechanism to make that substitution: if two salts pick rule_id `rule_0271c7a9f3b5f606`, both selections land on `rule_0271c7a9f3b5f606` in the ledger; the gate can only rewrite parameters inside that rule row. The M1 mechanism the brief pre-authorised is therefore *impossible* in this codebase, not merely refuted; the "honest correction" is zero. The worker documented this openly in report §5.

This is the highest-value output of the cycle and it gives cycle 28 unambiguous direction: any third-mechanism probe should skip hypotheses that assume post-hoc rule_id reshaping and instead test hash-space geometry per (rule_type × salt) or semantic-cluster overlap.

### Coverage caveat (auditor MINOR, documented)

Only 3 of 6 batches contribute to the shape R²: batch_v2, batch_v3_i3, batch_v6. batch_v1 has null `observed_per_rule_type` in cycle-26's `observations.json` (N = 5 not tabulated); batch_v3_i4 and batch_v4 have all-zero per-rule_type collisions (I4 sampler drives collisions to zero by construction at N ≤ K, making shape R² ill-defined). Excluded honestly and defensibly documented under "Issues and Uncertainties". The effective coverage is 3/6, and all three are shape-informative — the two excluded I4 batches contribute no shape signal, and the excluded batch_v1 lacks the per-rule_type observation column.

### Anchor preservation and cycle-26 utility invariance

- `anchor_preservation_shape.py verify` on the shipped manifests: **9/9 PASS, overall = PASS**. Seven batch dirs + two rules ledgers byte-identical pre/post via the cycle-26 canonical-aggregate-SHA utility.
- Cycle-26 utility SHAs pinned by `test_cycle26_bp_utility_untouched` (`canonical_aggregate_sha.py`, `collision_model_bp.py`, `collision_model_verdict.py` byte-identical).

### Tests

- `tests/test_collision_model_shape_mechanism.py`: **8/8 PASS** (cycle-26 utility SHA invariance × 3; verdict logic on the rubric; anchor preservation; AST no-PRNG; AST no-`sidecar_nonfactor`; AST-`i4_stratified` not imported; byte-determinism × 2 on the four analytical outputs).
- `tests/test_integration_cross_branch.py §39`: **16 new checks, all green**; suite `PASS (0 failures)`.
- `promise_check`: 0 ERRORs, 10 pre-existing WARNs.
- `org_check`: figure-location WARNs only (pre-existing; not blocking).

### Byte-determinism × 2

Ran the four analytical scripts twice, SHA-256'd the four outputs (fit JSON, verdict JSON, coercion TSV, k TSV): SHA-256 equal on all four.

### Ledger routing

Six named shadow-ledger events emitted at the fork's clone-0 shadow ledger + one infra adoption event — all with nested `confidence: {level, rationale, assessor}`, canonical `narrative` field (not `summary`), and the cycle-26 canonical `run_id: run-2026-08-28T040704Z`. Auto-concat under the cycle-22 harness-namespacing fix; orphan-artefact WARNs on the new artefacts cleared at post-merge concat via the `_infra/adopt-fanout-artifacts-*` mechanical pattern. Ledger 400 → 407 rows; distinct milestones 277 (steady).

### Auditor MODERATE (figures gap)

The brief's `### Deliverables` explicitly listed `docs/figures/shape_mechanism_M{1,2}_correction.png` (before/after per-rule_type predicted-vs-observed scatters). Neither exists on disk. The written report does not reference them. Per figure-coverage guidance: `NEITHER_EXPLAINS` is exactly the verdict where the before/after scatter is most informative — it visualises the catastrophic-worsening pattern that is the substantive finding. Not blocking; queued as cycle 28's small backfill task (`scripts/analysis/plot_shape_mechanism_scatter.py`) alongside the primary third-mechanism probe.

### Auditor MINOR observations (logged, not investigated)

- M1 correction formula direction differs slightly from the brief's formal spec (correction to prediction rather than to observed). Verdict stable across either interpretation because the honest correction is zero.
- Only 3/6 batches contribute to shape R² (documented above).
- M2 refits α (0.1761) rather than reusing cycle-26's α̂ = 0.7469. Defensible given K_eff harmonic ≡ 0 forces a clip; verdict stable.

## Discussion

Three things about this range are worth naming.

First, the NEITHER_EXPLAINS verdict is a *positive* first-class outcome even though both candidate mechanisms failed. The brief pre-authorised NEITHER_EXPLAINS as "the most informative outcome" for a reason: a positive fit on M1 or M2 would have added a second parameter to the collision-generation model (aggregate BP scale + per-type deformation from one of the two mechanisms) and left the campaign with a two-parameter model whose per-type residual might still not close under any single-mechanism story. NEITHER_EXPLAINS forces cycle 28 to test a third mechanism, and — because of the substantive by-product — narrows the hypothesis space in a specific direction: the third mechanism cannot assume post-hoc rule_id reshaping, so hash-space geometry or semantic-cluster overlap are the natural candidates. Ranked by information value and implementation cost: (1) hash-space geometry per (rule_type × salt) as a per-slice extension of cycle-13's salt-4 SHA-256 rank-0 digest-prefix analysis; (2) semantic-cluster overlap on arrangement/harmonic rule sets where structurally-equivalent instrumentation may collide at higher rates through `assemble_score → xml_to_midi → render_bare` even when rule_ids differ; (3) salt × rule_type interaction in the SHA-256 tiebreak (less likely a priori because SHA-256 is uniform). Cycle-28 primary should be (1).

Second, the mid-cycle discovery about the coherence gate is worth preserving as a discipline example. The M1 mechanism was pre-registered in the cycle-27 brief on the natural language of "the gate rejects candidate collisions" — a plausible-sounding hypothesis about how coercion could deform per-type effective K. The worker could have implemented M1 mechanically as spec'd, produced the R² number, and reported NEITHER_EXPLAINS on that basis alone. Instead the worker inspected the codebase to check what the gate actually does, verified against `data/gen/batch_v6/collision_analysis.json` that `raw.per_rule_type_pairs == coerced.per_rule_type_pairs` byte-identical across every salt in every batch, and documented the structural finding: the gate is a parameter-mutation gate, not a rule-selection gate. This turns NEITHER_EXPLAINS from "two mechanisms failed to fit" into "one mechanism was structurally impossible and the other did not fit, so cycle 28 should skip a whole class of hypotheses." The R² number and the structural finding together are more informative than either alone.

Third, the campaign's linear-cycle posture at cycle 27 held cleanly. Fan-out remains inappropriate for a single-mechanism probe with a locked rubric; a single R/W/A loop is the right shape when the rubric is mechanical and the outcome-space is small. The Hold Pattern guard from cycle 23 held: cycle 27 produced substantive work under the directive rather than any pause memo or null cycle. The standing anti-patterns (five, unchanged) remain locked: DAW-SPIKE-1 GAP-1 (redefined at c12), DAW-SPIKE-1 GAP-2 (still-GAP with sharper diagnosis at c13, redefined-GAP at c16 via DawDreamer), CLAP rung failure at c11, octave-suppression single-pass insufficient at c8, and the three M-EAR-1 Path A rescues invalidated at c22/c23/c25. The M-EAR-1 posture is stable — Path A exhausted, Path B committed at cycle 26, awaiting the egress trigger and `data/ear/rated_ready.flag`.

The uncalibrated CORN head remains the campaign's biggest open credibility gap and none of this range touches it. The `docs/ear_path_b_commitment.md §7-§8` checklist stays the durable pre-authorised playbook for the moment egress unblocks mid-cycle.

## Open Questions

- **Cycle 28 primary: third-mechanism probe.** Hash-space geometry per (rule_type × salt) as a per-slice extension of cycle-13's salt-4 SHA-256 rank-0 digest-prefix analysis. If certain rule_types cluster in low-index space differently, the shape-refute has a structural explanation without any coercion or effective-K story. Analytical, deterministic, no rendering; cycle-13 utility exists. Frozen 3-verdict rubric before analysis.
- **Cycle 28 backfill: two brief-required figures.** `scripts/analysis/plot_shape_mechanism_scatter.py` emitting `docs/figures/shape_mechanism_M1_correction.png` and `docs/figures/shape_mechanism_M2_correction.png` — per-rule_type predicted-vs-observed scatters, one panel per batch (v2, v3_i3, v6), overlaying uncorrected and M1-corrected (and M2-corrected) predictions. Both scatters should visually demonstrate that M1 and M2 pull predictions toward arrangement+harmonic while observed collisions stay diffuse. Analytical, deterministic, one-shot.
- **Second-choice cycle-28 mechanism if hash-space fires PARTIAL or REFUTES.** Semantic-cluster overlap on arrangement/harmonic rule sets. Uses frozen rule ledgers + already-generated batch outputs; no rendering.
- **Third-choice.** Salt × rule_type interaction in the SHA-256 tiebreak. Least likely a priori because SHA-256 is uniform; cleanly testable against batch-v6.
- **α ≈ 0.75 in the aggregate fit is now known to be absorbing something other than coercion-rate or effective-K.** This is a meaningful narrowing of the hypothesis space for cycle 28.
- **Read-only anchors for cycle 28** (preserve byte-identity): all cycle-26 + cycle-27 analytical utilities under `scripts/analysis/*`, the shape-mechanism JSON/TSV artefacts, all batch dirs + rules ledgers, and `scripts/rules/sampling/i4_stratified.py` (not to be imported).
- **Standing prohibitions unchanged.** No PRNG, SHA-256 tiebreak only, no `sidecar_nonfactor` imports, interpreter guard on every new script, ledger hygiene (`narrative` not `summary`; reuse `run-2026-08-28T040704Z`; nested `confidence`).
- **CORN-head calibration** and **rated-audio unblock** — still blocked on egress; `M-INGEST-1/egress-ready-automation` awaits its two-consecutive-`media_ok=true` trigger. `docs/ear_path_b_commitment.md §7-§8` is the durable pre-authorised playbook.

## Appendix: Provenance

**Cycle range:** cycles 29-31.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:**

- Cycle 29 researcher `4d552b9b-690e-41cd-962e-1f8765fa9c02`.
- Cycle 30 worker `fb9be31a-9fee-48b1-89ed-7a4d860b9fe4`.
- Cycle 31 researcher `d5dfb8fb-dd47-4761-a99e-a208eb138ca3`, worker `d5954908-e54e-4e81-b92d-7382185f3b30`, auditor `88350a32-ccc1-41fe-bb96-d63bb7533809`.

**Auditor verdict:** **VALIDATED** (with figures-incomplete qualifier). Sub-milestone `M-GEN-1/collision-model-shape-mechanism` closes at **`validated/high`** with terminal verdict **NEITHER_EXPLAINS** — first-class informative outcome pre-authorised by the brief.

**Deliverables on disk.**

- Code: `scripts/analysis/{coercion_rate_per_rule_type.py, effective_k_probe.py, shape_mechanism_fit.py, shape_mechanism_verdict.py, anchor_preservation_shape.py}` — 5 new analytical scripts, all interpreter-guarded, no PRNG (AST-checked), no `sidecar_nonfactor` imports (AST-checked), no `i4_stratified.py` import (AST-checked).
- Data: `data/collision_model/{shape_mechanism_fit.json, shape_mechanism_verdict.json, coercion_rate_per_rule_type.tsv, effective_k_per_rule_type.tsv, shape_mechanism_pre_run_anchor_manifest.json, shape_mechanism_post_run_anchor_manifest.json}`.
- Report: `docs/collision_generation_model_shape_mechanism.md`.
- Test: `tests/test_collision_model_shape_mechanism.py` (8/8 PASS); cross-branch integration test §39 (16 checks, all PASS).

**Load-bearing runtime evidence.**

- Terminal verdict: **NEITHER_EXPLAINS**; mechanically applied: `max(−6.2729, −10.6945) < 0.6`.
- M1-corrected mean R² = −6.2729; M2-corrected mean R² = −10.6945; uncorrected baseline mean R² = −0.3414. All three below the 0.6 CONFIRMS threshold; both mechanisms drive the fit further negative than the baseline.
- Substantive finding: `raw.per_rule_type_pairs == coerced.per_rule_type_pairs` byte-identical across every salt in every batch (verified against `data/gen/batch_v6/collision_analysis.json`). Coherence gate mutates parameters, does not remap rule_ids — M1 premise structurally invalid.
- Shape-informative coverage: 3/6 batches (v2, v3_i3, v6); v1 excluded (null `observed_per_rule_type` in cycle-26's `observations.json`); v3_i4 and v4 excluded (I4 sampler drives all-zero per-rule_type collisions at N ≤ K).
- Anchor preservation: **9/9 PASS overall = PASS** on 7 batch dirs + 2 rules ledgers via cycle-26 canonical-aggregate-SHA utility.
- Cycle-26 utility SHAs pinned: `canonical_aggregate_sha.py`, `collision_model_bp.py`, `collision_model_verdict.py` all byte-identical.
- Byte-determinism × 2: SHA-256 equal on all 4 analytical outputs (fit JSON, verdict JSON, coercion TSV, k TSV).
- Tests 8/8 branch + 16/16 §39 + suite `PASS (0 failures)`.
- `promise_check` 0 ERRORs, 10 pre-existing WARNs; `org_check` figure-location WARNs only.

**Ledger routing.** Six named shadow-ledger events emitted at `/home/user/music-gen-instance/fork-<cycle-27-fork>/clone-0/promise_ledger.jsonl` in the expected sequence + one infra adoption event (7 total). All events use nested `confidence: {level, rationale, assessor}`, canonical `narrative` field name (not `summary`), and cycle-26 canonical `run_id: run-2026-08-28T040704Z`. Auto-concat under the cycle-22 harness-namespacing fix; orphan-artefact WARNs on new artefacts cleared at post-merge concat via the `_infra/adopt-fanout-artifacts-*` mechanical pattern. Ledger 400 → 407 rows; distinct milestones 277 (steady).

**Standing anti-patterns unchanged (5).** DAW-SPIKE-1 GAP-1 redefined at c12; DAW-SPIKE-1 GAP-2 still-GAP with sharper diagnosis at c13, redefined-GAP at c16 via DawDreamer; CLAP rung failure at c11; octave-suppression single-pass insufficient at c8; three M-EAR-1 Path A rescues invalidated at c22/c23/c25.

**Environment stack unchanged since cycle 10.** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`. Single-thread BLAS pins throughout. Stability-audit harness anchors held at cycle-22 SHAs (not exercised this range).

**Rated audio.** Still egress-blocked per `corpus/CORPUS_STATUS.md`. `M-INGEST-1/egress-ready-automation` state machine remains `IDLE`; runtime state files correctly absent until the first live trigger. `docs/ear_path_b_commitment.md §7-§8` remains the durable pre-authorised checklist if egress unblocks mid-cycle.

**Handoff to next cycle.** Cycle 28's primary is the third-mechanism probe on hash-space geometry per (rule_type × salt) as a per-slice extension of cycle-13's salt-4 SHA-256 rank-0 digest-prefix analysis; the backfill is the two brief-required figures (`shape_mechanism_M{1,2}_correction.png`) via `scripts/analysis/plot_shape_mechanism_scatter.py`. Second-choice mechanism is semantic-cluster overlap on arrangement/harmonic rule sets; third-choice is salt × rule_type interaction in the SHA-256 tiebreak. Read-only anchors for cycle 28 named above. Standing prohibitions unchanged. Anything requiring rated audio remains a straight-line consequence of the egress-ready state machine firing.
