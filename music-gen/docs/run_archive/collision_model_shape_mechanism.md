---
created: 2026-08-28T15:00:00Z
cycle: 27
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/collision-model-shape-mechanism
---

# Collision-model shape mechanism probe

**Verdict:** `NEITHER_EXPLAINS`.
**R²(M1-corrected, mean)** = -6.2729.
**R²(M2-corrected, mean)** = -10.6945.
**R²(uncorrected, mean)** = -0.3414 (baseline: cycle-26 BP-scaled shape residual).

Frozen 4-verdict rubric (locked BEFORE analysis):

| Verdict | Condition |
|---|---|
| **M1_EXPLAINS** | R²(M1) ≥ 0.6 AND R²(M2) < R²(M1) − 0.15 |
| **M2_EXPLAINS** | R²(M2) ≥ 0.6 AND R²(M1) < R²(M2) − 0.15 |
| **BOTH_EXPLAIN** | R²(M1) ≥ 0.6 AND R²(M2) ≥ 0.6 AND \|R²(M1)−R²(M2)\| ≤ 0.15 |
| **NEITHER_EXPLAINS** | max(R²(M1), R²(M2)) < 0.6 |

## §1 Setup

Cycle 26 established that BP-scaled explains **aggregate** collision counts across N∈{5,8,16} at R² = 0.9588 with α̂ = 0.7469, but the *per-rule_type* shape refuted (R² = −0.869 on batch_v6). This branch tests the two candidate mechanisms named in the cycle-26 auditor handoff:

- **M1 (coercion-rate reshaping)** — coerced rule-picks might not count toward the naive BP per-rule_type distribution; uneven coercion rates across rule_types would reshape observed vs predicted.
- **M2 (effective-K)** — the per-rule_type admissible set after conditioning on other rule_types' actual picks could be smaller than raw K; using K_eff in the BP formula would rotate the shape prediction.

The 0.6 threshold matches cycle-26's PARTIAL_BP band — lower bar than the aggregate rubric's CONFIRMS threshold because we are explaining a residual, not fitting a primary model.

## §2 M1 methodology + per-rule_type coercion rates

`scripts/analysis/coercion_rate_per_rule_type.py` reads each batch's `provenance.jsonl` `coherence_gate` events and each `batch_manifest.json`'s per-song `applied_coercions` block. Per-rule_type coercion rate = fraction of salts on which a c1/c2/c3 coercion mutated that rule_type's parameters:

- c1 (`arrangement_silence_vs_pitched_melodic`) mutates **arrangement**
- c2 (`harmonic_progression_shorter_than_form`) mutates **harmonic**
- c3 (`drums_pattern_empty_fallback_to_bass`) mutates **arrangement**

Consequently form/melodic/rhythmic coercion rates are structurally 0 across every batch — the coherence gate never mutates their parameters.

M1 correction: `predicted_M1(r) = alpha_hat * pred_pure(r) * 1/(1 − rate(r))`.

Per-rule_type coercion rates (from `data/collision_model/coercion_rate_per_rule_type.tsv`):

| batch | A | F | H | M | R |
|---|---|---|---|---|---|
| batch_v1 | 0.800 | 0.000 | 0.800 | 0.000 | 0.000 |
| batch_v2 | 0.5625 | 0.000 | 0.5625 | 0.000 | 0.000 |
| batch_v3_i3 | 0.5625 | 0.000 | 0.5625 | 0.000 | 0.000 |
| batch_v3_i4 | 0.625 | 0.000 | 0.625 | 0.000 | 0.000 |
| batch_v4 | 0.625 | 0.000 | 0.625 | 0.000 | 0.000 |
| batch_v6 | 0.625 | 0.000 | 0.625 | 0.000 | 0.000 |

**Empirical observation, first-class:** across all 6 batches, `raw_rule_ids == coerced_rule_ids` for every salt (verified in the `per_rule_type_rule_id_change_count` column: all zeros). Coercions mutate rule *parameters* (e.g. append 'piano' to arrangement.instrumentation) but never remap a rule to a different ledger row. Rule-id-level per-rule_type collision counts are therefore identical between raw and coerced sides (verified: `data/gen/batch_v6/collision_analysis.json` — `raw.per_rule_type_pairs == coerced.per_rule_type_pairs`).

**The M1 correction inflates the model's per-rule_type predictions on the two rule_types (arrangement, harmonic) that actually get their parameters mutated — but the *observed* collision counts already reflect those mutations, and per-rule_type observed counts were not reshaped by coercions because rule_ids never changed. So the correction pushes exactly the wrong pair of predictions upward, and R² collapses.**

## §3 M2 methodology + K vs K_eff

`scripts/analysis/effective_k_probe.py` computes K_eff per rule_type per salt as the count of rules of that rule_type that would NOT trigger any coherence-gate coercion given the other rule_types' actual sampled picks:

- arrangement K_eff = # arrangement rules that pass BOTH c1 (against melodic pick) and c3 (against rhythmic pick)
- harmonic K_eff = # harmonic rules that pass c2 (against form pick)
- form/melodic/rhythmic: never mutated → K_eff = K_raw

Mean K_eff per batch (from `data/collision_model/effective_k_per_batch.tsv`):

| batch | A_raw | A_eff | H_raw | H_eff |
|---|---|---|---|---|
| batch_v1..v6 | 15 | 9.0 | 10 or 20 | **0.0** |

K_eff for harmonic collapses to 0 in every batch: no harmonic rule in either rules ledger has `len(chord_progression) ≥ max(form.section end_measure)` (harmonic prog lengths ∈ {1, 6, 8}; form max_end_measure ∈ {131, 208, 299}). This is a documented degeneracy — the M2 correction script clips K_eff to `max(K_eff, 1.0)` to keep the BP formula bounded and refits alpha (α̂_M2 = 0.1761).

M2 correction: `predicted_M2(r) = alpha_hat_M2 * N*(N-1) / (2 * max(K_eff(r), 1))`.

## §4 Corrected R² fit numbers

Per-batch shape R²:

| batch | R²(uncorrected) | R²(M1-corrected) | R²(M2-corrected) |
|---|---|---|---|
| batch_v2 | 0.0971 | 0.5376 | 0.6434 |
| batch_v3_i3 | -0.2523 | -2.5944 | -6.7543 |
| batch_v6 | -0.8690 | -16.7619 | -25.9727 |
| **mean** | **-0.3414** | **-6.2729** | **-10.6945** |

Interpretation: both corrections happen to move batch_v2 closer to fit (M2 crosses the 0.6 threshold on batch_v2 alone). But both catastrophically worsen batch_v3_i3 and batch_v6, because the corrections concentrate predicted collisions on arrangement and harmonic (the two mutation-eligible rule_types), while the *observed* distribution does not concentrate there — observed counts stay diffuse across all five rule_types.

## §5 Verdict + interpretation

**Verdict: `NEITHER_EXPLAINS`.** Both mechanisms fall well below the 0.6 rubric threshold on aggregate (mean across the three shape-observable batches).

Substantive interpretation:

1. **Coercion doesn't remap rule_ids.** The coherence gate mutates rule parameters in place; rule_id-level collision counts per rule_type are therefore invariant to coercion by construction. M1's "reshaping" hypothesis presupposes a mechanism that does not exist in this codebase.
2. **K_eff under strict "would-not-trigger" reading is degenerate for harmonic.** Every harmonic rule would trigger c2 against every form rule in either ledger. That degeneracy is itself an informative structural finding — but the corrected BP formula predicts collisions concentrated on harmonic and (to a lesser degree) arrangement, while observed collisions are diffuse.
3. **The α ≈ 0.75 in cycle-26's BP-scaled aggregate fit is not absorbing coercion-rate or effective-K structure.** It appears to be absorbing something else — a candidate the brief names as cycle-28's third-mechanism probe.

## §6 Byte-determinism proof

Two independent runs of the pipeline (`coercion_rate_per_rule_type.py`, `effective_k_probe.py`, `shape_mechanism_fit.py`, `shape_mechanism_verdict.py`) produce SHA-256-equal outputs on all six emitted JSONs and TSVs. See `tools/_run_determinism_check.sh`.

## §7 Anchor preservation proof

`scripts/analysis/anchor_preservation_shape.py verify` reports 9/9 PASS across:

- 7 batch dirs (batch_v1, batch_v2, batch_v3_i3, batch_v3_i4, batch_v4, batch_v5_n16, batch_v6)
- 2 rules ledgers (`data/rules/ledger.jsonl`, `data/rules/ledger_i3_dminor.jsonl`)

Cycle-26 utility SHAs (`canonical_aggregate_sha.py`, `collision_model_bp.py`, `collision_model_verdict.py`) also asserted unchanged (test cases 2–3 in `tests/test_collision_model_shape_mechanism.py`).

## §8 Cycle-28 recommendation

Because neither M1 nor M2 explains the SHAPE_REFUTES, cycle 28 should test a third mechanism as pre-authorized by the cycle-27 brief and cycle-13's salt-4 diagnostic. Concrete candidates:

- **Hash-space geometry** — SHA-256-rank-0 digest-prefix clustering per rule_type × salt. Cycle-13 clone-0 already surfaced this for salt=4; extending to per-rule_type slice across N=16 salts (batch_v6) may reveal that certain rule_types cluster in low-index space differently.
- **Salt × rule_type interaction** — a rule_type-conditional bias in the SHA-256 tiebreak may prefer particular rules of certain types.
- **Semantic-cluster overlap** — arrangement rules with "drums + bass + piano" instrumentation may collide with each other at higher effective rates because they share structural equivalents that survive assemble_score → xml_to_midi → render_bare pipeline stages.

All three are analytical and testable against the frozen batch outputs without touching any anchors.

---

**Files shipped:**

- `docs/collision_model_shape_mechanism.md` (this report)
- `scripts/analysis/coercion_rate_per_rule_type.py`
- `scripts/analysis/effective_k_probe.py`
- `scripts/analysis/shape_mechanism_fit.py`
- `scripts/analysis/shape_mechanism_verdict.py`
- `scripts/analysis/anchor_preservation_shape.py`
- `tests/test_collision_model_shape_mechanism.py`
- `data/collision_model/coercion_rate_per_rule_type.tsv`
- `data/collision_model/coercion_rate_summary.json`
- `data/collision_model/effective_k_per_batch.tsv`
- `data/collision_model/effective_k_summary.json`
- `data/collision_model/shape_mechanism_fit.json`
- `data/collision_model/shape_mechanism_verdict.json`
- `data/collision_model/anchor_preservation_shape.json`
- `data/collision_model/shape_mechanism_pre_run_anchor_manifest.json`
- `data/collision_model/shape_mechanism_post_run_anchor_manifest.json`

Cross-branch integration test extended with §39 (≥6 checks). All 8 test cases in `tests/test_collision_model_shape_mechanism.py` pass.
