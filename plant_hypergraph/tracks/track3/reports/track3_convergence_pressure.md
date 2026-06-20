---
created: 2026-05-18T06:00:00Z
run_id: fork-eec13528227c-clone-1-track3-convergence-pressure
agent: worker-clone-1
milestone: M3.T3
---

# Track 3 Convergence Pressure Instrument

## Scope

This branch builds the Wave 3 / M3.T3 convergence-pressure instrument from
the frozen Track 3 enrichment table:

- input: `tracks/track3/data/convergence_trait_edges.parquet`
- script: `tracks/track3/scripts/convergence_pressure.py`
- report: `tracks/track3/reports/track3_convergence_pressure.md`

The instrument reads only frozen Barrier 2 Track 3 enrichment plus the
frozen substrate-derived family labels already projected into that enrichment.
It does not mutate `phytograph_dataset/`, does not change the schema, does
not re-normalize synonyms, does not read sibling-track predictions, and does
not write to the cross-track `prediction_ledger.tsv` or
`speculation_ledger.tsv`.

## Mechanism

For each canonical trait `T`, the instrument computes family-share Shannon
entropy:

```text
H_family(T) = - sum_f p(f | T) log p(f | T)
```

It then standardizes the observed entropy against two deterministic nulls:

```text
CP_N1(T) = (H_family(T) - mean_N1(T)) / sd_N1(T)
CP_N2(T) = (H_family(T) - mean_N2(T)) / sd_N2(T)
CP_min(T) = min(CP_N1(T), CP_N2(T))
```

Null `N1` is a family-size-preserving swap null over `(trait, family)`
carrier tokens. Null `N2` is a sampling-density-preserving weighted draw
from taxa, where weights are per-taxon Track 3 edge counts. A trait clears
the pending convergence-pressure bar when `CP_min >= 2.0`.

Mechanism hypothesis: a canonical trait that is more family-dispersed than
both nulls is a candidate convergence-pressure signal. This is not proof of
independent origins, adaptive mechanism, or undocumented trait occurrence.
Those claims require Wave 4 held-out validation against independent trait
lists and ablations.

## Special-Point Checks

| Special point | Instrument behavior |
|---|---|
| `_other` bucket | excluded from canonical scoring; retained as one diagnostic row |
| zero-carrier canonical traits | marked `data_limited_not_prediction`; no CP score |
| CP below threshold | retained as observed evidence summary, not a prediction |
| high family-size/sampling-density confounding | recorded in confound regression; H3 is falsified only if residual rank agreement with CP is also high |
| master ledgers | remain header-only in this branch |

## Outputs

| Artifact | Purpose |
|---|---|
| `tracks/track3/data/convergence_pressure_scores.tsv` | per-trait CP scores and data-limited/exclusion flags |
| `tracks/track3/data/convergence_pressure_nulls.tsv` | N1/N2 null summaries with seed and replicate counts |
| `tracks/track3/data/convergence_pressure_confound_regression.tsv` | family-size and sampling-density falsifier regression |
| `tracks/track3/data/convergence_pressure_canonical_recovery.tsv` | canonical-case ranking diagnostic |
| `tracks/track3/data/convergence_predictions.tsv` | track-local prediction/evidence TSV for Atlas ingestion |
| `tracks/track3/data/convergence_pressure_figure.png` | CP score plot and CP-vs-family-count diagnostic |
| `tracks/track3/data/convergence_pressure_run_summary.json` | machine-readable run metadata |

`convergence_predictions.tsv` deliberately distinguishes four row classes:

| Row class | Meaning | Count |
|---|---|---:|
| `pending_convergent_trait_hypothesis` | canonical trait clears CP threshold; pending validation | 2 |
| `observed_trait_evidence_summary` | retained trait evidence but no predictive CP claim | 10 |
| `data_limited_canonical_trait` | canonical trait with zero retained accepted-key carriers | 3 |
| `diagnostic_bucket_excluded` | `_other` coverage diagnostic, not canonical scoring | 1 |

All rows have `enters_master_prediction_ledger=False`.

## Results

Two traits clear the current pending convergence-pressure threshold:

| trait | accepted-key carriers | families | CP_N1 | CP_N2 | CP_min |
|---|---:|---:|---:|---:|---:|
| `drupe` | 187 | 32 | 5.647 | 6.640 | 5.647 |
| `capsule` | 544 | 48 | 4.831 | 6.523 | 4.831 |

These are pending trait-level hypotheses only. They say that, in the frozen
Track 3 substrate, the observed family dispersion for these trait codings is
higher than expected under both nulls. They do not say any particular taxon
has an undocumented drupe or capsule trait, and they do not establish
adaptive convergence.

The confound falsifier records:

- `R2_observed_H_family = 0.835`
- `R2_CP_min = 0.852`
- `spearman_rho_residOBS_vs_CPmin = 0.406`
- verdict: `PASS`

Interpretation: raw observed entropy is strongly explainable by family-size
and sampling-density covariates, so the unstandardized signal is confounded.
However, the residual ranking is not strongly collinear with `CP_min` under
the stated falsifier threshold (`abs(rho) > 0.8`), so this branch does not
falsify H3. It also does not validate H3; Wave 4 must test the two pending
trait hypotheses against independent trait lists and ablations.

## Data-Limited Findings

The frozen Track 3 enrichment remains AusTraits-heavy and uneven:

- 12 of 15 canonical traits have non-zero retained edges.
- `ant_domatia`, `carnivory`, and `parasitism` have zero accepted-key carriers.
- `_other` contains 184,218 retained rows and is treated as a diagnostic
  bucket, not as a convergence trait.
- Canonical recovery is weak for some expected textbook cases because current
  substrate coverage is regional/source-biased. For example, `c4_photosynthesis`
  is present but does not clear the CP threshold in this frozen substrate.

## Evidence Boundary

Observed Track 3 trait-membership rows support only source-coded trait
occurrence within the retained enrichment. The M3.T3 prediction rows support
only prioritization for future convergence validation. They do not support:

- new trait occurrence in a taxon;
- new taxonomy, native range, ecological interaction, or adaptive history;
- a claim that a trait's family dispersion is biologically real after all
  future source-density, family-size, or sampling ablations;
- a validated prediction in the master ledger.

## Reproducibility

```bash
python3 tracks/track3/scripts/convergence_pressure.py
python3 -m pytest -q tracks/track3/tests/test_track3_enrichment.py tracks/track3/tests/test_convergence_pressure.py
python3 tools/validate_barrier2_track_enrichment.py
python3 tools/validate_barrier1_substrate.py
```

Current focused Track 3 tests pass: 16/16.

## Open Work

Wave 4 should validate or falsify the two pending hypotheses (`drupe`,
`capsule`) against independent trait lists, then run source-density,
family-size, and sampling-intensity ablations. Side-wave source recovery is
needed before `ant_domatia`, `carnivory`, and `parasitism` can become
predictive targets.
