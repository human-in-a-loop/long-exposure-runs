---
title: "PhytoGraph — cycles 24-26"
date: "2026-05-18"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph — cycles 24-26

## Abstract

Cycles 24-26 executed three focused reopen branches after the Wave 5 final synthesis had already closed the PhytoGraph campaign conservatively. Each branch tested whether a specific missing evidence predicate had become true for one track:

- Cycle 24 tested Track 4, the Domestication Hypergraph, for observed crop/crop-wild-relative BIOCLIM vectors and validation-ready expert comparator rows.
- Cycle 25 tested Track 5, the Chemodiversity Predictor, for accepted-key non-Duke dated taxon-compound evidence.
- Cycle 26 tested Track 6, the Botanical Foundation Model Probe, for a runnable free/open/local model runtime plus local model weights and audited benchmark responses.

All three branches ended with the same determination: `no_new_qualifying_evidence`. No predictor was rerun, no model was executed, and no master prediction or speculation row was promoted. The master `prediction_ledger.tsv` and `speculation_ledger.tsv` remained header-only.

The supplied audit report, labeled cycle 27, validated the post-reopen closure addendum that reconciled these three branches with the earlier Track 1 reopen result. That closure context confirms that none of the four tested reopen predicates for Tracks 1, 4, 5, and 6 became true.

## Introduction

PhytoGraph is a six-track research campaign built around a typed, auditable hypergraph of plant biology. Its goal is not to collect known facts into a catalog, but to produce falsifiable predictions and then validate, falsify, or close them cleanly.

By cycles 24-26, the campaign was already in post-closure mode. The Wave 5 final synthesis had recorded conservative outcomes across all six tracks, and the reopen evidence gate from cycle 22 had defined the exact evidence predicates required to reconsider several closed branches. In this context, "reopen" means a branch may change status only if the missing evidence class is actually present in the workspace and passes the relevant join, validation, and claim-boundary checks.

Three terms recur in this report:

- **Accepted key**: the canonical taxon identifier used by the frozen PhytoGraph substrate, based primarily on the World Flora Online naming layer.
- **CWR**: crop wild relative, a wild taxon related to a crop and potentially relevant to crop improvement.
- **BIOCLIM vector**: a numerical climate summary derived from occurrence or range data and climate rasters such as WorldClim or CHELSA.

## Approach

The report was assembled from local workspace artifacts, the supplied audit report, and the append-only `promise_ledger.jsonl`. Direct session-fetch/search tools for the listed session IDs were not available in this environment, so the raw provider-native transcripts for the cycle sessions could not be fetched. This is a record gap. The available trace consists of the cycle reports, data tables, tests, figures, ledger events, and the supplied auditor validation.

The cycle session IDs supplied for traceability were:

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 24 | `ce3702eb-ad17-4e3d-89a6-cabef9b18ded` | `24546f88-788b-4002-8e7a-8da5e75b2498` | `a74fbcc7-24a2-4222-bd42-6aef55c80029` |
| 25 | `a6096ee4-f44a-4b22-813b-61d1289fa619` | `ca7377bb-fe81-4cf5-b409-79e0353610c0` | `29fae4c5-b7e2-429d-89f5-c099b319a9a3` |
| 26 | `f7ed400c-e196-4dcc-86b8-ff81b7854134` | `43ad877f-4bc9-4b43-9aba-e5ddf504ebfa` | `68831f63-3358-429a-8411-f70055c4b161` |

The local promise-ledger events used for the main chronology were the cycle 24 worker/auditor events `2d03bc31-924d-49f8-9a8f-1fd02f36a1e1` and `8b70833f-f79b-4dc0-b211-e8ae1148e594`, the cycle 25 worker/auditor events `9d6e9453-737d-45cf-abea-3f4f5942dd8f` and `2d8c84cb-81ac-45b7-9d3e-18f3b8de98f2`, and the cycle 26 worker/auditor events `b0e8cd52-bdc2-4af8-a85f-efea0da6c6c3` and `d4a3ef34-f9fd-4540-a08b-5683508d394c`.

## Findings

### Cycle 24: Track 4 Did Not Recover Climate-Validation Evidence

Cycle 24 tested whether Track 4 could reopen H4 by finding the two evidence classes needed for climate-aware crop substitution validation: observed crop/CWR BIOCLIM vectors and held-out expert comparator rows.

The worker package was `tracks/track4/reports/track4_reopen_bioclim_validation_readiness.md`. It inspected four local artifacts: climate-envelope coverage, crop-wild-relative pairs, a held-out expert crop-source set, and prior Track 4 candidate rows. The result was `no_new_qualifying_evidence`.

The quantitative outcome was:

| Evidence class | Result |
|---|---:|
| Climate-envelope staging rows | 375 |
| Accepted-key climate joins | 36 |
| Crop/CWR pair rows | 69 |
| Fully joined crop/CWR rows | 3 |
| Held-out expert crop rows | 22 |
| Accepted-key held-out crop joins | 2 |
| Numeric BIOCLIM vector rows | 0 |
| Validation-allowed held-out candidate-level pairs | 0 |

The branch produced `tracks/track4/data/crop_cwr_bioclim_vectors.tsv`, which contains 10 accepted-key crop/CWR climate-coverage attempts. Every row has `bioclim_variable=none_available`, an empty value field, and `aggregation_method=not_computed`. These rows document coverage attempts, not usable climate vectors.

The branch also produced `tracks/track4/data/crop_cwr_validation_pairs.tsv`, which contains 22 held-out crop-source rows. All rows avoid training overlap, but all have `validation_allowed=false` because the available held-out sources are crop-level references rather than candidate-level expert CWR comparator rows.

![Accepted-key crop/CWR coverage for observed BIOCLIM vectors and held-out expert-comparison rows.](tracks/track4/figures/track4_reopen_bioclim_coverage.png)

The auditor event `8b70833f-f79b-4dc0-b211-e8ae1148e594` validated this as a non-reopen result. The Crop Substitution Engine was not rerun, and no climate-substitution recommendation, prediction-ledger row, speculation-ledger row, crop-suitability claim, or biological claim was promoted.

### Cycle 25: Track 5 Did Not Recover Non-Duke Temporal Chemistry Evidence

Cycle 25 tested whether Track 5 could reopen H5 by finding source-independent, temporally resolved phytochemical evidence. The specific predicate was accepted-key, non-Duke taxon-compound evidence with usable discovery or isolation dates.

The worker package was `tracks/track5/reports/track5_reopen_temporal_chemistry_evidence.md`. It inspected the frozen local chemistry substrate and source diagnostics. The result was again `no_new_qualifying_evidence`.

The key source diagnostic was:

| Source class | Candidate rows | Accepted-key rows | Dated rows | Non-Duke rows |
|---|---:|---:|---:|---:|
| Dr. Duke phytochemical rows | 103,663 | 13,867 | 0 | 0 |
| ChEBI | 0 | 0 | 0 | 0 |
| KNApSAcK | 0 | 0 | 0 | 0 |
| NPASS | 0 | 0 | 0 | 0 |
| Native American Ethnobotany Database mirror | 0 | 0 | 0 | 0 |
| PROSEA | 0 | 0 | 0 | 0 |
| PROTA | 0 | 0 | 0 | 0 |

The canonical holdout matrix contained eight taxa: *Taxus brevifolia*, *Catharanthus roseus*, *Cinchona officinalis*, *Artemisia annua*, *Digitalis purpurea*, *Papaver somniferum*, *Atropa belladonna*, and *Salix alba*. None had validation-allowed non-Duke pre-target or post-target evidence. Only *Artemisia annua* had an accepted key in the frozen substrate, and it still lacked qualifying non-Duke dated taxon-compound rows.

The branch also carried forward the earlier source-dominance result: `source_ablation_results.tsv` had 1,405 baseline prediction rows, but 0 rows under no-Duke, source-density-matched, and screening-count-matched variants. The cycle 25 branch added no evidence that changed that condition.

![Accepted-key and dated taxon-compound coverage by source for the Track 5 reopen assessment.](tracks/track5/figures/track5_reopen_non_duke_temporal_coverage.png)

The auditor event `2d8c84cb-81ac-45b7-9d3e-18f3b8de98f2` validated the package. The chemodiversity predictor was not rerun. No phytochemical novelty, clinical efficacy, preparation, dosage, safety, bioactivity, master prediction, or speculation claim was promoted.

### Cycle 26: Track 6 Did Not Find A Runnable Local Model

Cycle 26 tested whether Track 6 could reopen H6 under the free/open/local constraint. The required predicate was at least one local model runtime plus compatible local model weights, producing audited deterministic responses for the static botanical probe.

The worker package was `tracks/track6/reports/track6_reopen_local_model_execution.md`. It inspected local Python packages, local binaries, and workspace model-weight files. The result was `no_new_qualifying_evidence`.

The availability table contained 12 rows. Every inspected runtime or asset was unavailable or non-runnable:

| Runtime or asset class | Result |
|---|---|
| Python packages `llama_cpp`, `transformers`, `torch`, `ctransformers`, `gpt4all`, `onnxruntime`, `sentencepiece` | Missing |
| Binaries `ollama`, `llama-cli`, `llamafile`, `gpt4all` | Missing from PATH |
| Workspace model files matching `*.gguf`, `*.safetensors`, `pytorch_model*.bin`, or `model*.onnx` | Missing |

The static benchmark remained intact: 210 question rows across seven categories. The reopen package wrote explicit `not_run_no_local_model` rows instead of fabricating responses.

| Probe category | Static questions | Runnable responses | Scored responses |
|---|---:|---:|---:|
| convergence_detection | 30 | 0 | 0 |
| ghost_partner_reasoning | 30 | 0 | 0 |
| hybrid_pedigree | 30 | 0 | 0 |
| phytochemistry_safety | 30 | 0 | 0 |
| region_conditional | 30 | 0 | 0 |
| synonym_confusion | 30 | 0 | 0 |
| toxicity_lookalike_media_scope | 30 | 0 | 0 |

![Track 6 reopen coverage by probe category, separating static benchmark size from executed and scored responses.](tracks/track6/figures/track6_reopen_execution_coverage.png)

The auditor event `d4a3ef34-f9fd-4540-a08b-5683508d394c` validated this as a non-reopen result. No remote, paid, key-gated, or hosted provider execution was configured. No model-performance, leaderboard, vendor-comparison, toxicity-safety, failure-rate, prediction-ledger, or speculation-ledger claim was promoted.

### Supplied Closure Context: The Four Reopen Branches Remained Below Promotion Threshold

The supplied audit report validates a post-reopen closure package labeled cycle 27. Because the requested range is cycles 24-26, this closure package is context rather than part of the main chronology. It matters because it reconciles the cycle 24-26 branches with the earlier Track 1 reopen branch from cycle 23.

The closure addendum is `reports/reopen/reopen_closure_addendum.md`, and the machine-readable status table is `data/reopen/reopen_closure_status.tsv`.

The consolidated status table is:

| Track | Reopen result | Quantitative blocker | Master-ledger action |
|---|---|---|---|
| Track 1 | `evidence_added_but_threshold_not_met` | 6 accepted-key event-shaped rows across 3 accepted-key taxa, dominated by one source; no additional 30 accepted-key rows for source-density or family-size controls | No master prediction or speculation row |
| Track 4 | `no_new_qualifying_evidence` | 0 observed numeric BIOCLIM vectors and 0 validation-allowed held-out candidate-level crop/CWR comparison pairs | No master prediction or speculation row |
| Track 5 | `no_new_qualifying_evidence` | 0 accepted-key non-Duke taxon-compound rows with usable `discovery_or_isolation_year`; no-Duke/source-matched variants remain at 0 prediction rows | No master prediction or speculation row |
| Track 6 | `no_new_qualifying_evidence` | 0 runnable runtime-weight pairings, 0 executed model responses, and 0 scored responses | No master prediction or speculation row |

![Validated reopen branch outcomes by track.](reports/reopen/figures/reopen_branch_outcomes.png)

The supplied auditor event `83116d67-3a6c-43d1-aa5f-c06743fcd2ef` validated the closure package. The audit reported 13 focused tests passing, `promise_check` exiting 0 with inherited warnings only, and `org_check` exiting 0 with inherited root-layout warnings only. The audit also recorded `promise_ledger.jsonl` at 205 lines after the auditor append.

## Discussion

Cycles 24-26 did not change the scientific status of the campaign. They made the closure record more precise.

Track 4 moved from a general data-limited condition to a specific blocker: climate-aware validation cannot run because there are zero observed numeric BIOCLIM vectors and zero validation-allowed candidate-level expert comparator pairs. The branch documents accepted-key coverage attempts, but those attempts do not become climate evidence.

Track 5 confirmed that the source-bias problem remained unresolved. The local chemistry substrate contains many Duke-derived rows, including accepted-key retained rows, but it contains zero accepted-key non-Duke dated taxon-compound rows. Since the target validation protocol depends on temporally frozen, source-independent recovery of known phytochemical discoveries, the predictor could not be rerun.

Track 6 confirmed that the free/open/local execution constraint remained binding. The static benchmark and deterministic scoring infrastructure exist, but without a runnable local model and local weights, model error rates are undefined. The branch correctly recorded skipped rows rather than treating the benchmark itself as a model evaluation.

The common decision across all three cycles was non-promotion. This means the track-local diagnostic tables remain useful as audit artifacts, but the master ledgers remain reserved for claims satisfying the campaign’s validation and ablation contracts.

## Open Questions

The future reopen predicates are now explicit.

Track 4 can reopen only if occurrence-backed crop and CWR coordinates yield accepted-key BIOCLIM summaries, and disjoint candidate-level expert comparator rows exist before climate-substitution scoring.

Track 5 can reopen only if non-Duke taxon-compound detections have accepted taxon joins, compound identifiers, usable dates, family spread, and controls that preserve signal without Duke source dominance.

Track 6 can reopen only if approved local model weights and a free/open/local runtime produce audited deterministic responses with scorer diagnostics and nonzero scored-response coverage.

Track 1 remains outside the main cycle 24-26 chronology, but the supplied closure context records its future predicate: independent local/open event-shaped reticulation evidence must join to accepted keys, clear canonical recovery thresholds, and provide enough additional accepted-key rows for source-density and family-size controls.

## References

[4] The World Flora Online Consortium et al., "World Flora Online Plant List December 2025," Zenodo, 2025. https://doi.org/10.5281/zenodo.18007552 (accessed 2026-05-17).

[38] James A. Duke, "Dr. Duke's Phytochemical and Ethnobotanical Databases," Ag Data Commons, 2023. https://agdatacommons.nal.usda.gov/articles/dataset/Dr_Duke_s_Phytochemical_and_Ethnobotanical_Databases/24660351 (accessed 2026-05-17).

[40] KNApSAcK Family, "KNApSAcK Core System," KNApSAcK Family Databases, 2026. http://www.knapsackfamily.com/KNApSAcK/ (accessed 2026-05-17).

[41] Zeng et al., "NPASS: Natural Product Activity and Species Source Database," NPASS, 2026. https://bidd.group/NPASS/ (accessed 2026-05-17).

[42] EMBL-EBI, "ChEBI: Chemical Entities of Biological Interest," EMBL-EBI, 2026. https://www.ebi.ac.uk/chebi/ (accessed 2026-05-17).

[43] PROTA Foundation, "Plant Resources of Tropical Africa," PROTA4U, 2026. https://prota.prota4u.org/ (accessed 2026-05-17).

[44] PlantUse, "Plant Resources of South-East Asia (PROSEA)," PlantUse, 2026. https://uses.plantnet-project.org/en/PROSEA (accessed 2026-05-17).

## Appendix: Implementation Details

### Source Inventory

| Source | Date or cycle | Contents | Timeline role |
|---|---|---|---|
| Cycle 24 worker event `2d03bc31-924d-49f8-9a8f-1fd02f36a1e1` | 2026-05-18, cycle 24 | Track 4 bioclim validation-readiness package | Produced cycle 24 non-reopen evidence package |
| Cycle 24 auditor event `8b70833f-f79b-4dc0-b211-e8ae1148e594` | 2026-05-18, cycle 24 | Validated Track 4 package | Superseded worker event and confirmed `no_new_qualifying_evidence` |
| Cycle 25 worker event `9d6e9453-737d-45cf-abea-3f4f5942dd8f` | 2026-05-18, cycle 25 | Track 5 non-Duke temporal chemistry package | Produced cycle 25 non-reopen evidence package |
| Cycle 25 auditor event `2d8c84cb-81ac-45b7-9d3e-18f3b8de98f2` | 2026-05-18, cycle 25 | Validated Track 5 package | Superseded worker event and confirmed `no_new_qualifying_evidence` |
| Cycle 26 worker event `b0e8cd52-bdc2-4af8-a85f-efea0da6c6c3` | 2026-05-18, cycle 26 | Track 6 local model execution package | Produced cycle 26 non-reopen evidence package |
| Cycle 26 auditor event `d4a3ef34-f9fd-4540-a08b-5683508d394c` | 2026-05-18, cycle 26 | Validated Track 6 package | Superseded worker event and confirmed `no_new_qualifying_evidence` |
| Supplied audit event `83116d67-3a6c-43d1-aa5f-c06743fcd2ef` | 2026-05-18, cycle 27 | Post-reopen closure validation | Context for reconciling Tracks 1, 4, 5, and 6 |

### Code Organization

| Area | Files | Role |
|---|---|---|
| Track 4 reopen | `tracks/track4/scripts/build_reopen_bioclim_validation.py`, `tracks/track4/scripts/plot_reopen_bioclim_coverage.py`, `tests/test_track4_reopen_bioclim_validation.py` | Build and verify bioclim validation-readiness artifacts |
| Track 5 reopen | `tracks/track5/scripts/build_reopen_temporal_chemistry_evidence.py`, `tracks/track5/scripts/plot_reopen_temporal_chemistry_coverage.py`, `tests/test_track5_reopen_temporal_chemistry.py` | Build and verify non-Duke temporal chemistry evidence artifacts |
| Track 6 reopen | `tracks/track6/scripts/build_reopen_local_model_execution.py`, `tracks/track6/scripts/plot_reopen_execution_coverage.py`, `tests/test_track6_reopen_local_model_execution.py` | Build and verify local model availability, not-run response rows, and scoring diagnostics |
| Closure context | `reports/reopen/scripts/plot_reopen_branch_outcomes.py`, `tests/test_reopen_closure_addendum.py` | Build and verify the post-reopen closure outcome figure and table |

### File Counts

| Path | Rows or lines |
|---|---:|
| `tracks/track4/reports/track4_reopen_bioclim_validation_readiness.md` | 55 lines |
| `tracks/track4/data/crop_cwr_bioclim_vectors.tsv` | 11 lines, 10 data rows |
| `tracks/track4/data/crop_cwr_validation_pairs.tsv` | 23 lines, 22 data rows |
| `tracks/track4/data/track4_reopen_join_diagnostics.tsv` | 5 lines, 4 data rows |
| `tracks/track4/scripts/build_reopen_bioclim_validation.py` | 255 lines |
| `tracks/track4/scripts/plot_reopen_bioclim_coverage.py` | 67 lines |
| `tests/test_track4_reopen_bioclim_validation.py` | 125 lines |
| `tracks/track5/reports/track5_reopen_temporal_chemistry_evidence.md` | 54 lines |
| `tracks/track5/data/non_duke_temporal_taxon_compound_evidence.tsv` | 1 line, 0 data rows |
| `tracks/track5/data/track5_reopen_temporal_holdout_matrix.tsv` | 9 lines, 8 data rows |
| `tracks/track5/data/track5_reopen_source_diagnostics.tsv` | 8 lines, 7 data rows |
| `tracks/track5/scripts/build_reopen_temporal_chemistry_evidence.py` | 268 lines |
| `tracks/track5/scripts/plot_reopen_temporal_chemistry_coverage.py` | 51 lines |
| `tests/test_track5_reopen_temporal_chemistry.py` | 135 lines |
| `tracks/track6/reports/track6_reopen_local_model_execution.md` | 58 lines |
| `tracks/track6/data/local_model_availability_reopen.tsv` | 13 lines, 12 data rows |
| `tracks/track6/data/local_model_probe_responses.tsv` | 211 lines, 210 data rows |
| `tracks/track6/data/local_model_probe_scoring_diagnostics.tsv` | 8 lines, 7 data rows |
| `tracks/track6/scripts/build_reopen_local_model_execution.py` | 304 lines |
| `tracks/track6/scripts/plot_reopen_execution_coverage.py` | 49 lines |
| `tests/test_track6_reopen_local_model_execution.py` | 81 lines |
| `reports/reopen/reopen_closure_addendum.md` | 81 lines |
| `data/reopen/reopen_closure_status.tsv` | 5 lines, 4 data rows |
| `prediction_ledger.tsv` | 1 line, header only |
| `speculation_ledger.tsv` | 1 line, header only |
| `promise_ledger.jsonl` | 205 lines at scan time |

### Test Results

The supplied audit reported:

```text
python3 -m pytest -q tests/test_reopen_closure_addendum.py tests/test_wave4_postmerge_integration.py tests/test_barrier4_closure_integration.py
13 passed in 0.67s
```

It also reported:

```text
python3 -m long_exposure.tools.promise_check <run-root>
exit 0, 205 events, inherited warnings only

python3 -m long_exposure.tools.org_check <run-root>
exit 0, inherited root-layout warnings only
```

The branch-level auditor events additionally report focused pytest validation for the Track 4, Track 5, and Track 6 reopen packages.

### Cross-Reference Map

| From | To | Meaning |
|---|---|---|
| `data/reopen/reopen_branch_matrix.tsv` | Cycle 24 Track 4 package | Defines the H4 predicate tested in cycle 24 |
| `tracks/track4/data/crop_cwr_bioclim_vectors.tsv` | `tracks/track4/reports/track4_reopen_bioclim_validation_readiness.md` | Provides the zero-numeric-BIOCLIM basis for non-reopen |
| `tracks/track4/data/crop_cwr_validation_pairs.tsv` | `tracks/track4/reports/track4_reopen_bioclim_validation_readiness.md` | Provides the zero-validation-allowed-comparator basis for non-reopen |
| `data/reopen/reopen_branch_matrix.tsv` | Cycle 25 Track 5 package | Defines the H5 predicate tested in cycle 25 |
| `tracks/track5/data/non_duke_temporal_taxon_compound_evidence.tsv` | `tracks/track5/reports/track5_reopen_temporal_chemistry_evidence.md` | Provides the zero-row non-Duke temporal evidence basis for non-reopen |
| `tracks/track5/data/track5_reopen_temporal_holdout_matrix.tsv` | `tracks/track5/reports/track5_reopen_temporal_chemistry_evidence.md` | Documents eight canonical holdouts, all validation-disallowed |
| `data/reopen/reopen_branch_matrix.tsv` | Cycle 26 Track 6 package | Defines the H6 predicate tested in cycle 26 |
| `tracks/track6/data/local_model_availability_reopen.tsv` | `tracks/track6/reports/track6_reopen_local_model_execution.md` | Documents zero runnable runtime-weight pairings |
| `tracks/track6/data/local_model_probe_responses.tsv` | `tracks/track6/reports/track6_reopen_local_model_execution.md` | Preserves 210 not-run benchmark rows without fabricating responses |
| Cycles 23-26 branch packages | `reports/reopen/reopen_closure_addendum.md` | Reconciles Tracks 1, 4, 5, and 6 into validated non-promotion |
| `prediction_ledger.tsv` and `speculation_ledger.tsv` | All reopen reports | Remain header-only because no predicate became true |

### Manifest Update

`MANIFEST.md` was updated for `report_cycles_24-26`. The existing `## Key Files` section was preserved verbatim. The mutable sections now list the cycle 24-26 scripts, data artifacts, cumulative counts, and cross-references.

### Record Gaps

The named cycle session IDs were supplied, but no session-search or session-fetch tool was available in this environment. The report therefore relies on local workspace artifacts, promise-ledger events, tests, figures, and the supplied audit report. This gap does not change the reported branch outcomes because each branch is represented by local artifacts and auditor-validated ledger events.

### Coherence Review

The report was reviewed as a self-contained narrative. The main correction during review was to keep the supplied cycle-27 closure audit separate from the cycle 24-26 chronology while still using it as validated context for the final non-promotion decision.
