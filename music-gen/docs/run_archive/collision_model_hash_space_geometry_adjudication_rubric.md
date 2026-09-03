---
created: 2026-08-28T23:35:00Z
cycle: 29
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/collision-model-hash-space-geometry
---

# Cycle 29 — Frozen adjudication rubric for cycle-28 M3_WEAK verdict

**This document is committed BEFORE the adjudication scripts run.
It defines the three verdict outcomes; the outcome is a mechanical
function of the three input JSON files listed at the end. No
modification after the p-vector is examined.**

Cycle-28 verdict: `M3_WEAK`, based on one (rule_type × batch) cell at
raw p = 0.0487 (`batch_v2` × `harmonic`) and mean per-batch shape R²
of −0.240 across the three shape-informative batches. Cycle-28's
auditor flagged fragility under multiple-testing correction. This
cycle adjudicates.

## Verdict 1: M3_STANDS

The hash-space-geometry mechanism is a genuine partial explanation of
the residual collision structure.

Requires **all three** of the following:

1. **BH survival**: At least one (rule_type × batch) cell with p-value
   surviving Benjamini-Hochberg correction at q < 0.05 across all
   m = 35 cells.
2. **Drop-batch_v2 sensitivity**: When batch_v2 is excluded from the
   ledger row set (SHA prefix `be5726ab…`), at least one cell
   surviving BH q < 0.05 remains.
3. **Leave-one-cell-out contribution**: The surviving signal is not
   concentrated in a single cell — holding out any one cell
   individually still leaves at least one BH survivor.

## Verdict 2: M3_COLLAPSES_TO_REFUTES

The cycle-28 raw p = 0.0487 was a multiple-testing artifact. The
hash-space-geometry mechanism does not explain the residual collision
structure.

Requires:

- **No BH survivor**: Zero cells with p-value below the BH q = 0.05
  threshold across m = 35 cells.

Consequence: advances Path B candidate list. The semantic-cluster
overlap probe becomes the cycle-30 primary mechanism candidate.

## Verdict 3: MIXED

Requires either of:

- Exactly one cell surviving BH q < 0.05 AND drop-batch_v2 removes
  that cell entirely (surviving-count drops from 1 to 0), OR
- Leave-one-cell-out shows total dependence on a single legacy
  content cluster — every BH survivor disappears when that one cell
  is held out.

Consequence: verdict reported as MIXED with the specific dependency
named. No further hash-geometry cycles pursued.

## Multiple-testing methods (fixed)

Three corrections applied at α = 0.05 to the 35-cell p-vector:

- **Bonferroni**: reject if p_i ≤ α / m = 0.05 / 35 ≈ 1.428571 × 10⁻³.
- **Šidák**: reject if p_i ≤ 1 − (1 − α)^(1/m).
- **Benjamini-Hochberg (BH-FDR)**: sort p in ascending order; find the
  largest rank i such that p_(i) ≤ i × q / m; reject all p_(j) for j ≤ i.
  Uses q = 0.05.

No softening. No additional methods. If none of the three yield a
clean verdict, MIXED is reported with the ambiguity named.

## Alpha pin (unchanged)

Every recomputation of the fit under drop-batch_v2 or leave-one-cell-out
uses α = **0.7469387071101908**, the cycle-26 anchor. Alpha is NOT refit
in this cycle.

## Inputs (frozen)

The rubric fires on the three JSON files produced this cycle:

- `data/collision_model/multiple_testing_correction.json`
- `data/collision_model/drop_batch_v2_sensitivity.json`
- `data/collision_model/leave_one_cell_out.json`

All three consume `data/collision_model/hash_uniformity_summary.json`
(cycle-28 output, read-only anchor) and the per-batch canonical SHAs
via `scripts/analysis/canonical_aggregate_sha.py` (cycle-26 anchor).

## Output

The verdict lands at
`data/collision_model/hash_geometry_adjudication_verdict.json`
with a `rubric_hash` field equal to the SHA-256 of THIS file's
bytes at the time of computation. Any post-hoc edit to this doc
after the verdict is recorded will show as a `rubric_hash` mismatch
against the committed rubric.
