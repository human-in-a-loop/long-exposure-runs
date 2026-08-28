---
created: 2026-08-29T01:00:00Z
cycle: 30
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/collision-model-semantic-cluster-overlap
---

# Collision-modeling arc close — PARTIAL_BP_UNRESOLVED_SHAPE

**Verdict:** the auditor-named residual-shape mechanism space is
analytically exhausted. The α-pinned BP-scaled model confirms
aggregate collision counts but does not explain per-rule_type
distribution shape. All four candidate mechanisms named across
cycles 26–30 (M1 structural, M2, M3-collapsed, M4) fail to lift
per-batch shape R² above zero. This document records the honest
close of the collision-modeling arc as a first-class negative
finding, not a defeat.

## §1. Campaign directive recap and residual-shape provenance

The Music-Gen long-exposure campaign (`run-2026-08-28T040704Z`)
delivered goal G5 (deterministic generation from the rules ledger)
via seven validated M-GEN-1 batches spanning N ∈ {5, 8, 16} across
two ledgers (76-row baseline and 86-row I3-augmented) and two
samplers (unconditioned SHA-256 tiebreak; I4 stratified rejection).

Cycle 26's retrospective birthday-paradox (BP) model fit against
six observed batches produced:

- **BP-pure** aggregate R² = 0.7558 (no scaling).
- **BP-scaled** aggregate R² = **0.9588** with α̂ = 0.7469387071101908.
- Frozen verdict: `CONFIRMS_BP_SCALED` — birthday-paradox generation
  with a single global scale factor explains total collision counts.

But cycle 26 also surfaced a residual: **per-rule_type shape R²
under BP-scaled is negative on the two largest batches** (batch_v6
scaled shape R² = −0.869; batch_v3_i3 = −0.252; batch_v2 = +0.097;
mean = −0.341). The BP model gets the total right but not the
per-rule_type distribution.

Cycles 27–30 tested each auditor-named candidate mechanism for this
residual under a frozen rubric per cycle, with α pinned at 0.7469.
This document reports the exhaustion.

## §2. α = 0.7469 aggregate BP-scaled anchor

α̂ = **0.7469387071101908** was fit at cycle 26 by weighted
least-squares against six batches' observed totals and PINNED across
all downstream mechanism probes (cycles 27, 28, 29, 30). No probe
was permitted to refit α — this was a pre-registration invariant to
prevent parameter drift from masking mechanism failure.

α ≈ 0.75 is empirically consistent with a mild systematic bias
between the birthday-paradox expected pairs and the observed pairs,
without a mechanistic interpretation grounded in the generation
pipeline itself. Its purpose was as a scale anchor for the shape
analyses; it is not a "generator parameter" in the physical sense.

Aggregate BP-scaled R² = 0.9588 remains the strongest single result
of the collision-modeling arc.

## §3. Four failed mechanism probes

### M1 — coherence-gate coercion-rate (cycle 27)

**Rubric:** M1_EXPLAINS if replacing K with K × (1 − coercion_rate)
yields per-rule_type R² ≥ 0.60 (across at least 2 of 3 batches with
observed_per_rule_type) with |R²_M1 − R²_M2| > 0.15.

**Result:** R²_M1 mean across three batches = **−6.273**. All three
individual R²_M1 values below 0.60. Verdict: M1 does not explain.

**Structural lemma discovered during M1 probe** (cycle 27, load-
bearing for later probes): the coherence gate MUTATES rule
parameters after coercion but NEVER remaps `rule_id` across ledger
rows. This disqualifies any mechanism assuming post-hoc rule_id
substitution — a strong constraint on the mechanism search space.

### M2 — effective-K per rule_type after conditioning (cycle 27)

**Rubric:** M2_EXPLAINS if replacing K with K_eff after conditioning
on other rule_types' sampled rules yields per-rule_type R² ≥ 0.60.

**Result:** R²_M2 mean = **−10.695**. Verdict: M2 does not explain.

Cycle 27 combined verdict: **NEITHER_EXPLAINS** (neither M1 nor M2
crosses the 0.60 threshold).

### M3 — hash-space geometry per (rule_type × salt) (cycle 28)

**Rubric:** M3_EXPLAINS if K → K_eff-hash = K × (1 − chi²/(N(K−1)))
under per-cell chi-squared uniformity produces per-rule_type R² ≥
0.60 without multiple-testing correction.

**Cycle-28 raw result:** M3_WEAK — rank-1 cell `batch_v2 × harmonic`
at raw p = 0.048716; several nominal signals but no multiple-testing
correction applied.

**Cycle-29 adjudication:** M3 collapses to REFUTES under any of
Bonferroni / Šidák / Benjamini-Hochberg at q = 0.05 across the
35-cell (rule_type × batch) p-vector. Zero survivors. Drop-batch_v2
sensitivity confirms batch_v2 was the ONLY shape-informative batch
(R² = +0.327; removal drives mean R² from −0.240 to −0.524). The
rank-1 cell was dominated by rule_0271c7a9f3b5f606, the cycle-13
four-salt clique on the pre-I3 76-row ledger, a content-property
artifact that dissolves under I3 D-minor augmentation.

Verdict: **M3_COLLAPSES_TO_REFUTES**. Hash-space geometry does not
explain the residual.

### M4 — semantic-cluster overlap (cycle 30, this document)

**Rubric:** M4_EXPLAINS if K → K_eff-semantic (connected components
under pairwise-cosine-distance ≤ per-rule_type 20th-percentile
threshold on typed structural fingerprints) yields mean per-batch
shape R² ≥ 0.60 AND aggregate total-count R² ≥ 0.9088.

**Result (this cycle):**

| batch        |   N | K_eff-sem H | K_eff-sem R | K_eff-sem M | K_eff-sem F | K_eff-sem A | shape R² (M4) | shape R² (baseline) |
|--------------|----:|------------:|------------:|------------:|------------:|------------:|--------------:|--------------------:|
| batch_v2     |   8 |           4 |           5 |           6 |           4 |           3 |       −2.393  |             +0.097  |
| batch_v3_i3  |   8 |           5 |           5 |           6 |           4 |           3 |      −27.607  |             −0.252  |
| batch_v6     |  16 |           5 |           5 |           6 |           4 |           3 |     −128.059  |             −0.869  |

Mean per-batch shape R² M4 = **−52.686** (vs baseline mean = −0.341).

Aggregate total-count R² M4 = **−28.841** (vs baseline 0.9588).

**Verdict: M4_REFUTES.** The semantic-cluster hypothesis
*over-collapses* K, generating dramatic over-predictions. Rhythmic
K crashes from 18 to 5 (many identical 4/4 kick-only patterns share
fingerprints); form K from 15 to 4; arrangement K from 15 to 3;
harmonic K from 10/20 to 4/5; melodic K from 18 to 6. These are
each plausible "semantic identity" collapses in the structural
sense (the fingerprints ARE nearly identical), but the batch
generator does NOT weight rule choice by structural similarity —
each rule_id is drawn independently by SHA-256 tiebreak. So the
observed collision rate reflects the RAW cardinality, not the
semantic-equivalence cardinality.

Result: M4 is not the mechanism.

## §4. Analytical exhaustion argument

The residual-shape mechanism space named by the auditor across
cycles 26–29 is now closed:

- **Rule-ID remapping mechanisms** (any variant of "rules become
  something else after coercion") are structurally disqualified by
  the cycle-27 lemma. This class is EMPTY.
- **Post-hoc rule-cardinality mechanisms** (M2 effective-K, M3
  K_eff-hash, M4 K_eff-semantic) each substitute a different
  cardinality estimator. None survives its rubric.
- **Rule-selection-frequency mechanisms** (M1 coercion-rate as a
  proxy for per-rule_type "effective probability") also fails.

The space of mechanisms *definable at the summary-statistic level*
without extending the generator's dynamics is analytically
exhausted. Further progress on the residual shape would require:

(a) **Instrument the generator**: log per-salt per-batch per-
    rule_type acceptance/rejection traces (not just final rule_ids)
    to expose asymmetries invisible at the collision-count summary
    level.
(b) **Alter the sampler**: introduce a documented importance-
    weighted variant and compare shape R² across sampler families.
(c) **Reformulate the target**: model collision-rate distributions
    (not point estimates) and measure fit quality via distributional
    divergence rather than R².

None of these is in cycle-30's scope. All three are legitimate
cycle-31+ directions if the campaign chooses to reopen this arc.

## §5. What remains legitimately unknown

**A well-defined open problem:** why does BP-scaled explain aggregate
collision counts (R² = 0.9588) while missing per-rule_type
distribution shape (R² ≤ 0 on the two largest batches)?

The four probed mechanisms answer "not because of X" for four
specific X. We do not know what mechanism, if any, would produce a
positive shape R² under a rubric that pins α. The negative result is
robust: it survived multiple-testing correction, sensitivity
analyses, and structural analysis of the generator's dynamics.

This is not a "we couldn't figure it out" close — it is a fully
characterized open question, with the entire summary-statistic
mechanism space analytically closed under the pinned-α constraint.

## §6. Downstream campaign impact

**Unchanged:**

- **M-GEN-1 batch pipeline.** Seven batches produced deterministic,
  byte-identical outputs. The generator itself is not affected by
  this close — only the *explanatory model* for one specific residual
  is closed.
- **M-RULES-1 ledger extraction.** The rules ledgers (76-row and
  86-row I3) are anchored; extraction determinism holds.
- **M-TEX-1 texture panel and M-SEP-1 separation baselines.**
  Unrelated to the collision-modeling arc.
- **M-EAR-1 Path B commitment.** Cycle-26 durable commitment
  stands; real-label training remains the primary path pending
  audio egress.
- **α = 0.7469 aggregate anchor.** Retained as a documented empirical
  fit factor without mechanistic interpretation. Any future
  reopening MUST restart from this anchor.

**Closed:**

- **The four-cycle probe cascade** (M1 → M2 → M3 → M4) is
  documented in cycles 27–30 reports plus this close. The residual
  shape is no longer a "gap to be filled next cycle" — it is a
  characterized negative finding.

## §7. Reopening criteria

The collision-modeling arc may legitimately reopen if any of the
following new information arrives:

1. **A generator dynamics change** that plausibly reshapes per-rule_type
   selection (e.g., a documented sampler variant, a coherence-gate
   redesign, an importance-weighted sampler). Reopening MUST be
   accompanied by a fresh α-refit event (α cannot survive a
   generator change unmodified).
2. **A new mechanism candidate** not in {rule_id remap, effective-K,
   hash geometry, semantic cluster}, with a pre-registered rubric.
   The candidate must not be reducible to any prior probe.
3. **Additional observational batches** (N ≥ 32, or new samplers)
   that materially change the residual-shape empirics. Cycle-25's
   pigeonhole probe already showed N=16 behaves consistently with
   N=8; further extension is unlikely to change the qualitative
   picture without generator changes.
4. **A distributional target reformulation** (per §4 point (c))
   with a matched rubric.

Absent any of the above, the arc remains closed as
`PARTIAL_BP_UNRESOLVED_SHAPE`.

## §8. Handoff to M-EAR-1 Path B

The collision-modeling close does not affect Path B for ear-model
calibration. Real-label training remains the primary path forward
for M-EAR-1, gated on rated-audio egress. The armed harness at
`scripts/ear/train_armed_harness.py` remains armed; the
synthetic-fixture verification (cycle-26) and the frozen three
real-label success bars (SB1 MAE-beats-baselines,
SB2 τ ≥ 0.4 across bootstrap resamples, SB3 leak detection ≥ 0.90
at α=1.0) remain the trigger criteria. `workspace/harvest_playlists.sh`
was retried at the top of cycle 30; egress remains blocked (no
files downloaded across the 6/5/4 rating bands).

The collision-modeling arc's close frees future cycles to focus on
M-EAR-1 (once audio arrives) and on the remaining M-DAW-SPIKE-1 and
M-SEP-1 refinements without accreting cycle-31+ probes on the
now-closed shape residual.

---

## Appendix A: forward-look candidates NOT tested this cycle

Per the investigation contract, cycle 30 does not propose a fifth
mechanism. But candidates that emerge from the M4 residuals and may
be worth noting for future auditors:

- **Salt-conditioned rule-selection bias.** M4 assumed rules are
  drawn independently; if the SHA-256 tiebreak has a subtle per-
  rule_type / per-salt bias, cycle-28's per-(rule_type × salt) chi²
  results would carry residual information the aggregate M3 test
  missed. This overlaps M3 substantially — hard to disentangle at
  the summary-statistic level.
- **Coercion-cascade dependence.** M1 measured coercion-rate as a
  scalar per rule_type; the cycle-11 coherence gate is a 3-rule
  enumerated cascade that may generate rule-type-pair-specific
  cascades. Would require instrumenting the gate (per §4a).
- **Anchor-invariance under distributional targets.** Reformulating
  the target as "match the *distribution* of collision counts per
  rule_type" rather than the point estimate would produce a
  different R²-analog metric; whether α = 0.7469 remains the
  correct anchor under such reformulation is an open question.

These are named for future auditors; none are being pursued in
cycle 30.

## Appendix B: cycle-30 M4 artifact inventory

- `docs/collision_model_semantic_cluster_overlap_rubric.md`
  (rubric hash `efd1baa68d44a73e...`)
- `data/collision_model/rule_structural_fingerprints.tsv`
  (162 rows: 76 + 86)
- `data/collision_model/semantic_cluster_thresholds.json`
  (per-rule_type 20th-percentile, 76-row ledger only)
- `data/collision_model/semantic_equivalence_classes.tsv`
  (10 (source × rule_type) groupings; 45 total components)
- `data/collision_model/effective_k_semantic.tsv`
- `data/collision_model/semantic_cluster_fit.json`
- `data/collision_model/semantic_cluster_verdict.json`
- `data/collision_model/anchor_preservation_semantic.json`
  (cycles 26/27/28/29 all-green)

All scripts under `scripts/analysis/` interpreter-guarded on
`/usr/bin/python3`, no PRNG (AST-verified), no `sidecar_nonfactor`
imports, `i4_stratified.py` NOT imported.
