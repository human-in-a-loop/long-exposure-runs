---
created: 2026-08-28T11:45:00Z
cycle: 14
run_id: run-2026-08-28T040704Z
agent: worker (clone-1, fork 855d4c2e9945)
milestone: M-GEN-1/collision-floor-investigation
---

# M-GEN-1 collision floor structural investigation

**Verdict (headline):** The N=8 collision floor on the frozen 76-row rules
ledger is dominated by **small-K over-selection in the harmonic rule_type**
(K=10, one rule captured by 4/8 salts), against a birthday-paradox baseline
that is otherwise well-tracked by the four other rule_types. This is neither
a pure hash-geometric coincidence nor a structural-cluster mechanism: it is
the **dominant-rule** regime — a statistical fluctuation amplified by the
smallest rule pool in the ledger. **`rule_sub_type` splits are DISQUALIFIED
(schema-out-of-scope) or DEGENERATE (all harmonic rules share F_major).**
The two feasible cycle-15+ interventions are (I3) **corpus expansion** of
the harmonic pool — analytic prediction: adding H=10 rules drops the total
BP-expected floor from 9.64 to 8.24 pairs at N=8 — and (I4) **stratified
rejection sampling** — reduces the within-rule_type floor to 0 pairs at N=8
via a ~10 LOC sampler change, at the cost of the batch-v1 salt=0
byte-identity anchor.

Full attribution and prediction data at
`data/rules/collision_floor_analysis/{attribution.json, fingerprints.tsv,
pairwise_distances_*.tsv, distance_summary.json, cluster_verdict.json,
intervention_proposal.json}`. Figure at
`docs/figures/collision_floor_decomposition.png`.

![Collision floor decomposition — Panel A: per-rule_type observed pairs vs
birthday-paradox expected. Panel B: harmonic (top contributor) 2D MDS with
collision participants highlighted and the dominant rule (4/8 salt picks)
starred.](figures/collision_floor_decomposition.png)

---

## 1. Cycle-13 recap

Cycle-13 clone-0's batch-v2 audit measured **11 pairwise collisions at N=8**
salts on the cycle-12-expanded 76-row rules ledger, breaking down as:

| trend                                       | pairs |
|---------------------------------------------|-------|
| cycle-11 batch-v1, N=5, 28-row ledger       | 5     |
| cycle-12 batch-v1 rerun, N=5, 76-row ledger | 4     |
| cycle-13 batch-v2, N=8, 76-row ledger       | 11    |

The 28 → 76 corpus expansion **did not proportionally reduce** the collision
rate. Under uniform hashing the expected reduction should scale with 1/K per
rule_type; the observed reduction was much smaller. Cycle-13's collision
analysis flagged this as the primary M-GEN-1 batch-capacity ceiling
signal — hence the cycle-14 structural investigation.

## 2. Attribution table

Reproducing the cycle-13 collision matrix from the frozen 76-row ledger + the
frozen `scripts/gen/sample_rules.py` sampler yields **exactly 11
pairwise-collision contributions**, distributed across 10 unique salt pairs
(one pair — salts 1 and 5 — has two contributor rule_types). The regression
contract is satisfied.

| rule_type    | K (pool)  | pairs observed | birthday-paradox expected¹  | ratio obs/exp |
|--------------|-----------|----------------|-----------------------------|---------------|
| harmonic     | 10        | 6              | 2.80                        | 2.14×         |
| rhythmic     | 18        | 2              | 1.56                        | 1.28×         |
| melodic      | 18        | 2              | 1.56                        | 1.28×         |
| form         | 15        | 0              | 1.87                        | 0.00×         |
| arrangement  | 15        | 1              | 1.87                        | 0.53×         |
| **total**    | **76**    | **11**         | **9.64**                    | **1.14×**     |

¹ Birthday-paradox baseline: `C(N,2) / K = 28 / K` at N=8.

**Concentration.** 6 of the 11 pairs (54.5%) come from a single rule_type
(harmonic), and all 6 come from a single rule captured by 4 of the 8 salts.
The other three rule_types (rhythmic, melodic, arrangement) all lie within a
factor of 1.5 of their BP baselines; form is below expectation. The
aggregate observed floor (11) is within 15% of the aggregate BP baseline
(9.64) — an important null result: **at the system level, the sampler is
close to uniform**; the excess is localized entirely to harmonic.

**Per-salt collision partners (from `attribution.json`).**

| salt | any-collision partners |
|------|------------------------|
| 0    | {1, 5, 6}              |
| 1    | {0, 4, 5, 6}           |
| 2    | {4}                    |
| 3    | {4, 7}                 |
| 4    | {1, 2, 3}              |
| 5    | {0, 1, 6}              |
| 6    | {0, 1, 5}              |
| 7    | {3}                    |

The harmonic 4-clique on {0, 1, 5, 6} accounts for 6 of the 11 pairs; the
remaining 5 pairs are split across rhythmic (2), melodic (2), arrangement (1).

## 3. Structural fingerprint methodology

Every fingerprint field is derived deterministically from the rule row's
`parameters` block. No metadata (`rule_id`, `provenance_pointers`,
`confidence`, `ts`) is included, and no PRNG is used. Per-rule_type fields
are defined in
`scripts/rules/analysis/structural_fingerprints.py::FIELDS_BY_TYPE`:

- **harmonic:** `key`, `cadence`, `progression_length`, `progression_sig`
  (12-hex SHA-256 of chord-sequence), `unique_chords`.
- **rhythmic:** `meter`, `tempo_bpm`, `swing_ratio`, `pattern_length`,
  `onset_density` (fraction non-rest), `pattern_sig` (12-hex of pattern).
- **melodic:** `contour`, `range_semitones`, `dominant_pc`
  (argmax pitch class), `pch_entropy` (base-2 Shannon entropy of PCH),
  `pch_nonzero_bins`.
- **form:** `section_pattern` (classified as `monolithic`, `uniform_2m`,
  `uniform_4m`, `ABAB`, `ABA`, or `other`), `n_sections`, `total_measures`.
- **arrangement:** `has_drums`, `has_bass`, `has_other`, `instr_count`,
  `density_mean`, `density_std`, `peak_location_fraction`, `active_frac`,
  `n_layer_events`.

Categorical fields use Hamming distance (0 or 1); numeric fields use the
normalized-difference metric `|a−b| / (|a| + |b| + ε)` with `ε=1e-9`. The
rule-pair distance is the sum of per-field distances.
`data/rules/collision_floor_analysis/fingerprints.tsv` contains all 76 rows.

## 4. Pairwise distance analysis

Per-rule_type pairwise distance distributions
(`data/rules/collision_floor_analysis/distance_summary.json`):

| rule_type    | K   | n_pairs | mean   | median | stdev |
|--------------|-----|---------|--------|--------|-------|
| harmonic     | 10  | 45      | 1.681  | 2.048  | 0.793 |
| rhythmic     | 18  | 153     | 0.947  | 1.143  | 0.455 |
| melodic      | 18  | 153     | 1.327  | 1.378  | 0.471 |
| form         | 15  | 105     | 1.598  | 1.891  | 0.675 |
| arrangement  | 15  | 105     | 3.571  | 3.523  | 1.771 |

**Tight-cluster analysis on the top contributor (harmonic).**

The tight-cluster threshold is defined as `max(0, median − 1σ)`. For
harmonic this is `1.255` (from median 2.048 − stdev 0.793). Under that
threshold, harmonic has **13 tight-cluster edges** (out of 45 pairs).

However, an important structural feature of the harmonic pool renders the
usual "collision ⇔ close-together rules" reading invalid: **the four salts
that collide on harmonic all pick the SAME rule (`rule_0271c7a9f3b5f606`)**,
not four different-but-similar rules. The cluster-verdict script
(`scripts/rules/analysis/cluster_analysis.py`) therefore classifies the
harmonic case as a `dominant_rule` regime, not `structural_cluster`, on the
`max_single_rule_picks ≥ 3` criterion.

**Cluster threshold sensitivity.** At the tighter `median − 2σ = 0` threshold
harmonic has 0 tight edges; at the median threshold (2.048) it has 25. The
verdict does not depend on the threshold, however, because the mechanism is
"one rule captures 4/8 salts", not "different rules that are structurally
close collide". No amount of structural-neighbor analysis on the dominant
rule changes that.

## 5. Cluster verdict

Per-rule_type verdicts (`cluster_verdict.json`):

| rule_type    | obs | BP-exp | max_single_rule_picks | verdict            |
|--------------|-----|--------|-----------------------|--------------------|
| harmonic     | 6   | 2.80   | 4                     | **dominant_rule**  |
| rhythmic     | 2   | 1.56   | 2                     | hash_geometric     |
| melodic      | 2   | 1.56   | 2                     | hash_geometric     |
| form         | 0   | 1.87   | 1                     | no_collision       |
| arrangement  | 1   | 1.87   | 2                     | hash_geometric     |

**System-level verdict: `dominant_rule` on the top contributor (harmonic).**

The four other rule_types are consistent with the pure birthday-paradox
mechanism (M2 in the research brief). Only harmonic diverges — and its
divergence is a **small-K statistical fluctuation** in which one specific
rule sorted first under a plurality of salt envelopes. Enumerating the 10
harmonic rules reveals why the pool is small and the diversity is thin:

| rule_id                | key      | scope    | prog_len | unique |
|------------------------|----------|----------|----------|--------|
| rule_0271c7a9f3b5f606¹ | F_major  | song     | 8        | 7      |
| rule_821a916f5a58a283  | F_major  | measure  | 6        | 5      |
| rule_e97a8ce34a67651d  | F_major  | measure  | 1        | 1      |
| rule_ff1fa8c4bf0f228f  | F_major  | measure  | 1        | 1      |
| rule_f0d4393926766453  | F_major  | measure  | 1        | 1      |
| rule_900193a92a8810e5  | F_major  | measure  | 1        | 1      |
| rule_a5f50a9707200179  | F_major  | song     | 8        | 2      |
| rule_ca6007d98315c046  | F_major  | measure  | 6        | 2      |
| rule_d8ab0bcf0694e01d  | F_major  | song     | 8        | 5      |
| rule_2549a4193dead599  | F_major  | measure  | 6        | 3      |

¹ Dominant rule — sampled at salts {0, 1, 5, 6}.

Every harmonic rule in the pool is F_major (all three seed corpora produced
F_major songs). The dominant rule is not an outlier in its parameter space;
it is simply the one whose canonical-JSON representation happens to sort
first under 4 of the 8 salt envelopes.

## 6. Intervention proposal

Five candidates were evaluated
(`data/rules/collision_floor_analysis/intervention_proposal.json`):

| id | intervention                                                  | schema change? | predicted total floor (N=8) | verdict                       |
|----|---------------------------------------------------------------|----------------|-----------------------------|-------------------------------|
| I1 | `rule_sub_type` split on harmonic by `scope.level`            | yes            | 20.18                       | DISQUALIFIED (worse; frozen)  |
| I2 | `rule_sub_type` split on harmonic by `key`                    | yes            | 9.64                        | DISQUALIFIED (degenerate)     |
| I3 | corpus expansion of harmonic (add H new rules)                | no             | 8.24 (H=10) / 7.78 (H=20)   | **RECOMMENDED (structural)**  |
| I4 | stratified rejection sampling (per rule_type)                 | no             | 0.00                        | **RECOMMENDED (sampling)**    |
| I5 | content-aware tiebreak (structural-spread bipartite matching) | no             | not scored this cycle       | DEFERRED (concept only)       |

**I1 (scope-level split) analytics.** The scope buckets are `{song: 3,
measure: 7}`. Expected pairs after split = `C(8,2)/3 + C(8,2)/7 = 9.33 +
4.00 = 13.33` for harmonic alone — worse than the flat pool's 2.80 because
smaller sub-buckets have higher BP. Total floor becomes `9.64 − 2.80 + 13.33
= 20.18`. Disqualified on two counts (schema change out of scope AND worse).

**I2 (key split) analytics.** Distinct keys in the harmonic pool = 1
(F_major). Degenerate.

**I3 (corpus expansion) analytics.** Adding H new harmonic rules of any key
drops the per-type BP from 2.80 to `28 / (10 + H)`. The full sweep:

| H  | new K | new harmonic BP-exp | predicted total floor |
|----|-------|---------------------|-----------------------|
| 5  | 15    | 1.87                | 8.71                  |
| 10 | 20    | 1.40                | 8.24¹                 |
| 20 | 30    | 0.93                | 7.78                  |

¹ Recommended cycle-15+ target: extract harmonic rules from ≥2 non-F_major
seed songs (target keys: D_minor to break the 4-clique per cycle-13
handoff pointer 1; A_minor for a second contrast). At H=10 the total floor
drops by ~1.9 pairs from BP, and — importantly — the diversity within
harmonic increases so the small-K variance shrinks.

**I4 (stratified rejection sampling) analytics.** With N=8 and every
rule_type having K ≥ 10 ≥ N, a rejection-sampling policy that discards any
candidate already picked at a lower salt within the same rule_type
eliminates every within-rule_type collision by construction. Predicted total
floor = 0 pairs at N=8. Concrete implementation in
`scripts/gen/sample_rules.py::sample_ruleset` is a ~10 LOC change:

```python
# Pseudocode:
already_picked = set()  # optional carry across salts
scored.sort(key=lambda t: t[0])
for h, r in scored:
    if r["rule_id"] not in already_picked:
        winner_hash, winner = h, r
        already_picked.add(r["rule_id"])
        break
```

**Trade-off.** I4 breaks the cycle-11 batch-v1 salt=0 byte-identity anchor
whenever the anchor path would have been the picked-again rule for a later
salt (harmless for salt=0 itself; must be verified for salts 1..N−1 that
inherit the anchor semantics via the envelope-hash contract). A cycle-15
regression check is required: rerun batch-v1 under the new sampler and
diff `data/gen/batch_v1/*.json` against the frozen anchor.

**Combined I3+I4.** Both interventions are compatible: I3 raises K, I4
reduces within-type collisions to 0. The residual N=8 floor after both is 0
pairs from within-rule_type sources — leaving only cross-rule_type
interactions and coherence-gate coercions as the batch-capacity ceiling
signals. Recommended cycle-15 order: land I4 first (small, mechanical), then
plan I3 as a corpus intervention behind egress unblock.

## 7. Blind spots

This analysis is analytic and does not include an empirical batch-v3 run
that would confirm the intervention predictions. Specifically:

1. **No batch-v3 rerun with proposed sampler.** I4's predicted floor of 0
   at N=8 is a construction proof, not a measurement. A cycle-15 batch-v3
   rerun under a modified sampler would be a legitimate falsification.
2. **No cross-rule_type interaction floor.** The current sampler picks one
   rule per rule_type independently; there is no cross-type collision. Under
   I4, cross-type residuals are impossible by construction, but if the
   coherence gate rewrites picks, new interaction patterns may emerge.
3. **No absolute-content diversity metric.** Two harmonic rules can have
   very different `progression_sig` values yet play identically (e.g., both
   in F_major with V-I dominant motion). The `pairwise_distance` metric
   here treats `progression_sig` as categorical, so it cannot detect
   audition-similar-but-hash-different rules.
4. **No time-varying salt policy.** All 8 salts are drawn from a uniform
   integer range. If salt distribution biases exist (e.g., preferring
   power-of-two salts) this analysis would not surface them.
5. **The 76-row ledger is frozen at cycle 13.** New rule extractions
   scheduled for cycle 15 (breadth seeds beyond `seed_mid_50s` and
   `synth_060s`) will re-shape the harmonic pool and require rerunning this
   pipeline.

## 8. Cycle-15+ recommendations

Ranked by expected impact-per-effort:

1. **Land I4 (stratified rejection sampling)** as a mechanical sampler
   change. Modify `sample_ruleset` in `scripts/gen/sample_rules.py` to
   reject already-picked rules within a rule_type across salts 0..N−1. Add
   a regression test on the cycle-11 batch-v1 salt=0 anchor. Predicted new
   floor at N=8: 0 within-rule_type pairs.
2. **Plan I3 (harmonic corpus expansion)** as the structural intervention
   whose value scales with the number of non-F_major seed songs we can
   ingest. Requires unblocking rated-audio egress (per
   `corpus/CORPUS_STATUS.md`) or extending the synthetic seed catalog with
   a D_minor / A_minor breadth pair (fold into the cycle-13 handoff
   pointer 1 already in `merge_report.md`).
3. **Defer I5 (content-aware tiebreak)** to a research spike that specifies
   the bipartite-matching algorithm and its determinism contract. Not a
   good candidate for immediate cycle-15 work.
4. **Retain the analytic pipeline in `scripts/rules/analysis/`** as a
   permanent cycle audit tool: after any future ledger expansion or
   sampler modification, re-run the six-script pipeline and cross-check
   the resulting predicted floor against the empirical N=X batch result.
5. **Extend cycle-14 auditor scope.** The auditor should verify that
   subsequent cycles' M-GEN-1 collision reports cite this analysis and use
   the BP-baseline column as the null hypothesis rather than "reduction
   from previous cycle" (which the corpus-size-invariance result shows is
   the wrong reference).

---

### Reproduction contract

- Byte-deterministic × 2 verified via `tools/_determinism_check.sh` (all
  11 output artifacts SHA-256-equal across two independent runs).
- Rules schema untouched: `scripts/rules/schema/rules_v1.json` SHA-256
  `b9bec6733c0be7e4…`.
- Rules ledger untouched: `data/rules/ledger.jsonl` SHA-256
  `a6fd53e9bf9a10f6…` (76 rows).
- Non-factor AST isolation preserved: no imports of
  `scripts.classifier.sidecar_nonfactor` in the new analysis package.
- Interpreter guard on every new script (`assert sys.executable ==
  '/usr/bin/python3'`).

### Regression contract

- Total pair-contributions = **11** across the 5 rule_types (matches
  cycle-13 clone-0's `data/gen/batch_v2/collision_analysis.json`).
- Unique any-collision pair count = **10** (pair (1, 5) is dual-contributed
  by harmonic and melodic — accounted for as one pair, two contributions).
- Per-rule_type pair counts: harmonic=6, rhythmic=2, melodic=2, form=0,
  arrangement=1.

### Artifact inventory

- `docs/collision_floor_investigation_report.md` — this document.
- `docs/figures/collision_floor_decomposition.png` — two-panel figure.
- `data/rules/collision_floor_analysis/attribution.json`
- `data/rules/collision_floor_analysis/fingerprints.tsv`
- `data/rules/collision_floor_analysis/pairwise_distances_{harmonic, rhythmic, melodic, form, arrangement}.tsv`
- `data/rules/collision_floor_analysis/distance_summary.json`
- `data/rules/collision_floor_analysis/cluster_verdict.json`
- `data/rules/collision_floor_analysis/intervention_proposal.json`
