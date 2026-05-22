---
created: 2026-05-18T10:15:00Z
run_id: fork-0b556d9370a2-clone-1
agent: worker-clone-1
milestone: M4.V4
track: Track 4
status: data-limited closure
---

# Track 4 Barrier 4 Closure

## Scope

This closure determines whether the current Track 4 crop-wild-relative and climate-envelope evidence supports any bounded climate-substitution analysis for H4. It reads the existing Track 4 enrichment and instrument artifacts only. It does not expand ingestion, alter the frozen substrate, change schema, run a new recommender, or promote rows into the master prediction ledger.

## Decision

H4 is closed as data-limited for the current Barrier 4 reconciliation. The current evidence does not support climate-substitution recommendations, CGIAR-class held-out agreement scoring, or a sister-species baseline comparison under climate stress.

The existing Track 4 rows may remain in the Atlas and Track 4 reports only as `pending_data_limited` candidate rankings from pedigree/CWR/selection/Vavilov evidence. They must not be described as climate matches, crop-substitution recommendations, validated predictions, or deployment advice.

## Evidence Read

| Evidence axis | Current observed state | Closure implication |
|---|---:|---|
| Retained Track 4 observed hyperedges | 6 | Enough for a tiny structural domestication layer, not enough for broad Track 4 prediction. |
| Retained crop-pedigree edges | 2 / 43 staged | Only two crops have retained accepted-key pedigree support. |
| Joined crop-wild-relative pairs | 3 / 69 staged | CWR accepted-key coverage is too sparse for a crop matrix or genus-level expert comparison. |
| Held-out validation rows with accepted keys | 2 / 22 | Held-out agreement scoring cannot be interpreted; most held-outs cannot join to substrate keys. |
| Climate-envelope rows with accepted keys | 36 / 375 | Some names join, but joined rows still lack extracted climate values. |
| Observed bioclim vectors | 0 / 375 | Climate matching is undefined, not merely low-confidence. |
| Candidate rows emitted by M3.T4 | 3 | Candidate rows are pedigree/CWR-only and `validation_ready=False`. |
| Climate claims emitted | 0 | The instrument correctly avoided climate suitability claims. |

Primary source artifacts:

- `tracks/track4/docs/ENRICHMENT_AUDIT.md`
- `tracks/track4/track4_domestication_hypergraph.md`
- `tracks/track4/data/crop_cwr_coverage_summary.tsv`
- `tracks/track4/data/climate_envelope_coverage.tsv`
- `tracks/track4/data/crop_wild_relative_pairs.tsv`
- `tracks/track4/data/heldout_validation_seed.tsv`
- `tracks/track4/data/crop_substitution_candidates.tsv`
- `tracks/track4/data/crop_substitution_engine_summary.json`

## Mechanism Statement

Let a climate-substitution score require at least:

`S(c, w, e) = g(P(c, w), CWR(c, w), T(c), V(c), D(x_c, x_w, e))`

where `c` is the crop, `w` is a wild relative, `e` is a target climate envelope, `P` is pedigree evidence, `CWR` is joined crop-wild-relative evidence, `T` is trait evidence, `V` is Vavilov/context evidence, and `D` is a distance or suitability function over observed bioclim vectors `x_c` and `x_w`.

In the current substrate:

- `x_c` is absent for every Track 4 crop row.
- `x_w` is absent for every Track 4 wild-relative row.
- Therefore `D(x_c, x_w, e)` is undefined for every candidate.

The correct boundary behavior is exclusion of the climate term and data-limited closure, not assignment of a zero climate score. A zero score would falsely encode absence of extracted data as evidence of climate mismatch.

## Special-Point Checks

| Special point | Value in current artifacts | Result |
|---|---|---|
| `observed_bioclim_vectors = 0` | True | Climate matching cannot be computed for any crop/CWR pair. |
| `joined_CWR_pairs = 0` | False; value is 3 | Non-climate candidate rankings are possible for two crops. |
| `heldout_accepted_keys = 0` | False; value is 2 | A validation seed exists, but coverage is too sparse for agreement scoring. |
| `candidate_climate_component = 0` | False; blank by design | The engine does not misread missing climate evidence as negative evidence. |
| `validation_ready=True` | False for all 3 candidate rows | No candidate qualifies for Barrier 4 prediction-ledger validation. |

## Falsification Criteria Applied

H4 would be allowed to advance to bounded validation only if the current artifacts contained all of the following:

1. Nonzero observed bioclim vectors for both crops and candidate wild relatives.
2. Sufficient accepted-key CWR coverage to define a crop matrix beyond one or two pedigree examples.
3. Held-out expert rows that join to accepted keys and remain disjoint from training pedigree rows.
4. A score with an explicit climate component and a negative control showing that taxonomy-only or same-genus proximity does not explain the ranking.

The current artifacts fail criteria 1, 2, and 3. Criterion 4 is not runnable because climate and held-out coverage are insufficient.

## Current Candidate Rows

The only scored candidates are:

| Crop | Candidate wild relative | Rank | Non-climate score | Allowed interpretation |
|---|---|---:|---:|---|
| Arachis hypogaea | Arachis duranensis | 1 | 1.000000 | Pedigree/CWR candidate only; no climate suitability claim. |
| Arachis hypogaea | Arachis ipaensis | 2 | 1.000000 | Pedigree/CWR candidate only; no climate suitability claim. |
| Avena sativa | Avena sterilis | 1 | 0.933333 | Pedigree/CWR candidate only; no climate suitability claim. |

These rows should remain out of `prediction_ledger.tsv` unless the master reconciliation process explicitly accepts data-limited pending rows. If represented anywhere globally, they should be described as Track 4 local candidate-prior rows with status `data-limited`, not predictions.

## Barrier 4 Status

Recommended Track 4 status for Barrier 4:

- H4: `data-limited`
- M4.V4 / Track 4 validation: `data-limited closure`
- Master prediction ledger promotion: none
- Master speculation ledger promotion: none required from this closure
- Atlas exposure: allowed only with the existing `pending_data_limited`, `not_computable_no_observed_bioclim_vectors`, and "not a validated recommendation" caveats

## Minimal Future-Data Recipe

Reopen Track 4 climate-substitution validation only after all of the following exist under the existing provenance contract:

1. Accepted-key expansion for crop and wild-relative names, especially the 66 currently unjoined CWR pairs and 20 unjoined held-out validation rows.
2. Occurrence-coordinate extraction for crop and CWR taxa with enough quality filtering to avoid cultivated-occurrence leakage where wild envelopes are required.
3. Per-taxon WorldClim/CHELSA bioclim summary vectors for crops and wild relatives, with rasters not redistributed.
4. A held-out expert-recommendation table that joins to accepted keys and remains disjoint from training pedigree evidence.
5. A sister-species or same-genus baseline and a multi-parent-edge ablation, both run after climate vectors exist.

Until then, the scientific result is a negative closure: Track 4 produced a schema-conformant domestication layer and a tiny non-climate candidate-prior instrument, but the current evidence cannot support H4's climate-substitution validation target.
