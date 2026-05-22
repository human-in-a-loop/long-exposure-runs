---
created: 2026-05-18T14:45:00+00:00
cycle: 21
run_id: run-phytograph-cycle21-wave5-final-synthesis
agent: worker
milestone: M5.1
---

# Final Report: PhytoGraph

## Executive Result

PhytoGraph produced a large typed plant-biology substrate, six track-specific
instruments or instrument scaffolds, Atlas integration, validation and ablation
packages, and conservative closure records. It did not meet the original
research success criterion of at least one validated prediction per track.

That failure is part of the result. Under frozen schema v1.0, open/local data
constraints, and the no-paid-provider Track 6 correction, the campaign found
that several apparent predictive lanes collapse into accepted-key recovery
limits, missing observed climate vectors, source dominance, or unavailable
local model execution.

The master `prediction_ledger.tsv` and `speculation_ledger.tsv` remain
header-only because no cross-track row currently satisfies the campaign's
promotion contract without over-claiming.

The post-reopen closure and free-tier integrations confirm that the later
branches do not yet license master-ledger promotion. Track 1 now has a
branch-local threshold-met GBIF-keyed recovery result, but it is
reconciliation-pending until the accepted-key namespace is resolved. Track 2 is
`H2_remains_not_supported_or_data_limited` with 0/8 canonical held-outs passing
the validation contract. Track 3 is `confound_limited` with 0 controlled-ready
traits across 3,069 accepted-key trait carrier rows. Track 4
has coordinates but no numeric BIOCLIM vectors or disjoint comparators; Track 5
has two manual non-Duke detection candidates but no structured family/class
stratum; Track 6 added no qualifying execution evidence.

The final free-tier closure synthesis makes that boundary explicit across all
six tracks: Track 1 is `sidecar_readiness_uncontrolled`, Track 2 is
`H2_remains_not_supported_or_data_limited`, Track 3 is `confound_limited`,
Track 4 is `still_data_limited`, Track 5 is `H5_remains_source_biased`, and
Track 6 is `environment_limited_untested`.

## Built Artifacts

The campaign delivered these PhytoGraph-specific components:

- `phytograph_schema.md`: frozen unified hypergraph schema v1.0.
- `data_source_audit.md`: source, license, access, reliability, and track-use audit.
- `coverage_report.md`: Tier 0 through Tier 4 coverage summary.
- `phytograph_dataset/`: typed hypergraph substrate with provenance and caveats.
- `botanical_atlas_site/` and `atlas_runbook.md`: local Atlas surface exposing track outputs with evidence-vs-prediction boundaries.
- `reports/barrier3_atlas_instrument_readiness.md`: Atlas/instrument readiness contract.
- `reports/wave4_postmerge_integration.md`: Track 2/3/5 Wave 4 validation and ablation integration.
- `reports/barrier4_closure_integration.md`: Track 1/4/6 closure integration.
- `reports/reopen/reopen_closure_addendum.md`: post-reopen closure reconciliation for Tracks 1, 4, 5, and 6.
- `reports/reopen/free_tier_recovery_integration.md`: cycle 28 Track 1/4/5 free-tier branch integration.
- `reports/reopen/free_tier_track2_track3_closure_integration.md`: Track 2/3 free-tier closure reconciliation for fork `2f05eabe3800`.
- `reports/reopen/final_free_tier_closure_synthesis.md`: final six-track free-tier closure synthesis.
- `data/reopen/final_free_tier_track_status.tsv`: canonical final free-tier status table.
- This Wave 5 package: `final_report.md`, `audit_report.md`, `research_contribution_ledger.md`, `artifact_index.md`, and `falsification_and_ablation_report.md`.

## Track Outcomes

| Track | Hypothesis | Final status | Evidence basis | Reopen condition |
|---|---|---|---|---|
| Track 1 Reticulation Atlas | H1 | `sidecar_readiness_uncontrolled` | Free-tier sidecar retained 22 event taxa across 11 source groups, but WFO projection retained only 2 taxa and source-density controls remain unresolved. | Map GBIF accepted-key evidence to frozen WFO accepted keys or admit an audited sidecar namespace with source-density controls before any master prediction. |
| Track 2 Ghost Hyperedges | H2 | `H2_remains_not_supported_or_data_limited` | Free-tier branch retained 8 canonical held-outs and 31 local candidates, with 0/8 canonical held-outs passing the validation contract. | Accepted-key modern-failure evidence, multi-source/source-class support, living-megafauna controls, and source-class-independent held-out recovery. |
| Track 3 Convergence Pressure | H3 | `confound_limited` | Free-tier branch retained 3,069 accepted-key trait carrier rows across 15 canonical traits, with 0 controlled-ready traits; `drupe` and `capsule` remain local pending priors. | Broader trait coverage, phylogenetically separated carrier sets, and family-size/sampling-density controls sufficient to distinguish convergence from homology or sampling. |
| Track 4 Domestication Hypergraph | H4 | `still_data_limited` | 3,358 post-filter occurrence records, 0 numeric BIOCLIM vectors, and 0 validation-allowed comparator rows. | Audited crop/CWR BIOCLIM summaries and disjoint candidate-level expert comparator rows. |
| Track 5 Chemodiversity Predictor | H5 | `H5_remains_source_biased` | Non-Duke temporal evidence is insufficient and no validation-ready structured family/class stratum exists. | Temporally resolved non-Duke phytochemical/ethnobotanical evidence and screening-intensity controls that preserve signal. |
| Track 6 Foundation Model Probe | H6 | `environment_limited_untested` | Static benchmark and deterministic scorer exist, but there are 0 runnable local runtime-weight pairings, 0 executed responses, and 0 scored responses. | Free/open/local model runtime and weights available in workspace, with audited response rows and no paid or key-gated API calls. |

## What Is New

PhytoGraph's durable contributions are not validated biological predictions.
They are the substrate, claim boundary, and falsification infrastructure:

- A unified typed schema that keeps taxonomy, phylogeny, reticulation,
  convergence, domestication, phytochemistry, ethnobotany, media, and model
  probes in one provenance-preserving hypergraph.
- A large accepted-key substrate with 60,000 Tier 0 accepted taxonomy rows,
  113,582 synonym nodes, 363,237 nodes, and 641,183 retained hyperedges after
  Barrier 1 repair.
- Barrier validators for substrate, track enrichment, and Atlas integration.
- Six track-local instruments or benchmark scaffolds that expose missing-data
  and source-bias boundaries instead of promoting weak predictions.
- A conservative final claim policy that treats null, falsified, data-limited,
  source-biased, and environment-limited results as first-class findings.

## What Failed

The original success criterion was not met. There is no validated prediction
per track, and no row was promoted to the master prediction ledger. Track 2 and
Track 5 explicitly failed their headline validation thresholds under controls.
Track 1, Track 3, and Track 4 could not clear data coverage requirements. Track
6 could not execute model scoring because the allowed local/open environment did
not contain a runnable model stack or weights.

These failures are traceable to local artifacts rather than conjecture. They are
summarized in `falsification_and_ablation_report.md` and in the track closure
reports under `tracks/`.

## Ledger Position

`prediction_ledger.tsv` and `speculation_ledger.tsv` intentionally remain
header-only. Track-local candidate rows are retained in their own namespaces,
but the master ledgers are not a place for insufficiently validated priors. The
post-reopen closure status table records this as validated non-promotion rather
than missing work.

## Reproduction

The Wave 5 closure was checked with:

```bash
python3 -m pytest -q tests/test_wave4_postmerge_integration.py tests/test_barrier4_closure_integration.py
python3 -m pytest -q tests/test_reopen_closure_addendum.py tests/test_free_tier_recovery_integration.py
python3 tools/validate_barrier3_atlas_integration.py
python3 tools/validate_barrier2_track_enrichment.py
python3 tools/validate_barrier1_substrate.py
python3 -m long_exposure.tools.promise_check <run-root>
python3 -m long_exposure.tools.org_check <run-root>
```

Known residual warnings are inherited process and layout warnings, documented
in `audit_report.md`; they do not change the scientific claim boundary.
