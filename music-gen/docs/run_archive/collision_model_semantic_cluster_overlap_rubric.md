---
created: 2026-08-29T00:30:00Z
cycle: 30
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/collision-model-semantic-cluster-overlap
---

# Frozen rubric — M4 semantic-cluster overlap probe (cycle 30)

**Status: FROZEN — committed BEFORE any verdict/fit script runs.**
The verdict JSON's `rubric_hash` field records this document's
SHA-256 verbatim. Test
`test_rubric_hash_matches_committed_doc` re-computes the SHA and
asserts equality.

## 1. Scope

The M4 probe tests whether **semantic-cluster overlap** — rules that
are structurally near-identical even when their content-hashed
`rule_id` differs — explains the residual per-rule_type shape
R² observed under the α-pinned BP-scaled collision model.

The residual under test:

- cycle-26 aggregate BP-scaled R² = 0.9588 (CONFIRMS_BP_SCALED)
- cycle-26 per-batch shape R²_scaled: batch_v2 = +0.097, batch_v3_i3
  = −0.252, batch_v6 = −0.869 (mean = −0.341)
- The batch_v6 shape R²_scaled = −0.869 is the primary residual the
  probe is aimed at.

α is pinned at **0.7469387071101908** (cycle-26 anchor) throughout.
No refit.

## 2. Structural fingerprint construction (locked)

Vocabularies (locked before threshold computation):

- roman-numeral bag: {I, i, II, ii, III, iii, IV, iv, V, v, VI, vi,
  VII, vii} (14 dims).
- cadence: {none, PAC, IAC, HC, DC, PC, other} (7 dims).
- rhythmic pattern: {kick, snare, hihat, cymbal, tom, rest} (6 dims).
- contour class: {arch, ascending, descending, static, undulating}
  (5 dims).
- instrumentation: {drums, bass, other} (3 dims).

Per-rule_type fingerprint vector:

- **harmonic**: tonic_pc one-hot (12) + mode one-hot (2) + roman
  bag-of-tokens (14) + cadence one-hot (7) = 35 dims.
- **rhythmic**: (meter_num, meter_den, tempo_bpm rounded) (3) +
  pattern bag (6) = 9 dims.
- **melodic**: contour one-hot (5) + range_semitones (1) + PCH
  (12, L1-normalized) = 18 dims.
- **form**: (n_sections, total_span, mean_section_length,
  n_distinct_labels) (4) + canonical-label histogram (8 slots) = 12
  dims.
- **arrangement**: instrumentation multi-hot (3) + density resampled
  to 8-point L∞-normalized (8) + (n_events, n_add, n_remove) (3) =
  14 dims.

Pairwise structural distance within a rule_type: **1 − cosine
similarity** of L2-normalized fingerprint vectors.

## 3. Semantic-equivalence threshold — per rule_type (LOCKED)

The 20th percentile of the pairwise cosine-distance distribution on
the **76-row `data/rules/ledger.jsonl`** (cycle-12 breadth-expanded
baseline) is the pre-registered per-rule_type semantic-equivalence
threshold. Computed by
`scripts/analysis/semantic_cluster_thresholds.py`; that script MUST
NOT read `ledger_i3_dminor.jsonl` (test-asserted for pre-registration
integrity).

Per-rule_type thresholds (from
`data/collision_model/semantic_cluster_thresholds.json`, run
2026-08-29T00:20:00Z):

| rule_type   | n rules (76-row) | n pairs | p20 threshold |
|-------------|-----------------:|--------:|--------------:|
| harmonic    |               10 |      45 |  0.184393     |
| rhythmic    |               18 |     153 |  0.000000     |
| melodic     |               18 |     153 |  0.000175     |
| form        |               15 |     105 |  0.011135     |
| arrangement |               15 |     105 |  0.001788     |

Rationale for 20th percentile: principled sparsity choice; any tighter
threshold would produce degenerate singleton clusters, any looser
would collapse everything. Rhythmic p20 = 0 is a substantive finding
in its own right — many rhythmic rules share identical fingerprints
(same 4/4 120-bpm kick-only pattern in different provenance) — and
represents the natural collapse the M4 hypothesis is designed to
detect.

## 4. K_eff-semantic construction

For each ledger (76-row and 86-row), for each rule_type:

1. Build the pairwise adjacency graph: edge(i, j) iff
   dist(i, j) ≤ p20_threshold for that rule_type. The ≤ is
   intentional: it makes identical-fingerprint pairs (distance = 0)
   collapse into the same component even when the frozen p20
   threshold itself is 0 (this is the case for rhythmic, where many
   rules share identical fingerprints — kick-only 4/4 120-bpm
   pattern in different provenance). Semantic-identity is the
   floor of the equivalence relation.
2. Extract connected components (union-find; deterministic; no PRNG).
3. **K_eff-semantic** = number of connected components.

By construction, K_eff-semantic ≤ K (raw rule count).

## 5. Refit under M4 correction

BP-scaled prediction per rule_type per batch, α pinned:

    E_shape[rule_type] = α × N(N-1) / (2 × K_eff-semantic[rule_type])

where N is the batch size and K_eff-semantic comes from the batch's
source ledger (batch_v2 → 76-row; batch_v3_i3 / v6 → 86-row).

Per-batch shape R² = 1 - SS_residual / SS_total, computed over the
five per-rule_type observed vs predicted pairs (H, R, M, F, A).
Aggregate R² = mean of per-batch shape R² across the three batches
with observed_per_rule_type (batch_v2, batch_v3_i3, batch_v6).

## 6. Frozen verdicts

**M4_EXPLAINS**: mean per-batch shape R² ≥ 0.60 across the three
batches AND aggregate total-collision-count R² (per canonical
BP-scaled from cycle 26) does not degrade below 0.9588 − 0.05 =
**0.9088**. Semantic-cluster overlap is a genuine mechanism for the
residual per-rule_type shape.

**M4_WEAK**: mean per-batch shape R² in [0, 0.60). Semantic-cluster
overlap partially explains the residual (moves it out of negative
territory but doesn't reach the PARTIAL_BP floor). Recommend
cycle-31 refinement OR trigger `PARTIAL_BP_UNRESOLVED_SHAPE` close
depending on the per-rule_type breakdown.

**M4_REFUTES**: mean per-batch shape R² ≤ 0. Semantic-cluster overlap
does not explain the residual. Trigger the campaign close
`PARTIAL_BP_UNRESOLVED_SHAPE` — a first-class negative finding
recording (i) the α = 0.7469 aggregate BP-scaled anchor, (ii) the
four failed mechanism probes (M1 structural, M2, M3-collapsed, M4),
and (iii) analytical exhaustion of the auditor-named residual-shape
mechanism space.

## 7. Escape-hatch integrity

M4_WEAK and M4_REFUTES are legitimate research outcomes. The frozen
20th-percentile threshold, the pinned α, and the fingerprint
construction are not adjustable after seeing results. Any change
after publication must land as a cycle-31+ event (`_manager/*`
milestone) with explicit before/after diff.

## 8. Constraints inherited from prior cycles

- **α pinned** at 0.7469387071101908 (cycle 26).
- **No PRNG** anywhere (SHA-256 tiebreak).
- **Structural rule_id non-remapping lemma** (cycle 27): semantic-
  equivalence classes group *rule_ids that are semantically similar*;
  they do not *replace* rule_ids in ledger rows.
- **No cycle-26/27/28/29 utility modification** — read-only anchors
  under the extended §41 SHA guard.
- **Threshold script does not read `ledger_i3_dminor.jsonl`** —
  pre-registration integrity.
