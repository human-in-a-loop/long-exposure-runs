---
title: "PhytoGraph — cycles 14-16"
date: "2026-05-18"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph — cycles 14-16

## Abstract

Cycles 14-16 moved PhytoGraph from a post-merge Atlas state into the first bounded Wave 4 validation and ablation tranche. The sequence was gate-driven. First, the Barrier 3 instrument-to-Atlas package was built and auditor-validated: all six Wave 3 instruments are now queryable from the Botanical Atlas with provenance, caveats, missing-data indicators, and evidence-vs-prediction labels. Second, two stale Wave 1 source branches, M1.3 and M1.6, were closed as terminal data-limited source-coverage limitations rather than instrument defects. Third, Wave 4 validation/ablation branches were run for Tracks 2, 3, and 5.

The main scientific outcome is conservative. Track 2 did not validate H2: no held-out Janzen-Martin case survived current accepted-key and ablation controls. Track 3 did not validate H3: `drupe` and `capsule` remain pending convergence-prior hypotheses, but the result is data-limited. Track 5 did not validate H5: temporal holdouts were not recovered, and the Duke/source ablation validated a source-bias null result. The master `prediction_ledger.tsv` and `speculation_ledger.tsv` remain header-only.

## Introduction

PhytoGraph is a typed hypergraph campaign for plant discovery across six tracks: reticulation, ghost coevolutionary partners, convergence, domestication, chemodiversity, and foundation-model botanical reasoning. Earlier cycles built the frozen substrate, track-local enrichment, Wave 3 instruments, and a 60,000-page Botanical Atlas. The Atlas is a research window, not the scientific result itself.

Cycles 14-16 focused on lifecycle discipline. Barrier 3 had to be closed before validation work could proceed. Two stale source-ingestion milestones also had to be retired or explicitly carried forward so they would not create ambiguity in later validation. Only after those gates were addressed did the campaign enter bounded Wave 4 work for selected tracks.

The field framing for this report is general computational biology: the work combines data integration, validation, source-bias controls, and auditability rather than a single mathematical or experimental result.

## Approach

The cycle range used a staged sequence.

Cycle 14 began with a researcher brief requesting a Barrier 3 readiness package (`1c9552eb-fdc4-4965-9bb1-3b06a1ae0da5`). The worker then built the package (`86671fae-c3d0-4f38-a0dc-db755413adf5`), and the auditor validated it (`e6517447-afc8-4aa4-a867-5f25398d0f15`).

Cycle 15 addressed manager-identified process drift around stale source milestones. The researcher scoped a source-branch disposition package for M1.3 and M1.6 (`4c21033c-1e55-46c4-ba90-f334e5ce72c3`). The worker produced the package (`479955d6-b87b-4498-b933-980e3a3ee806`), and the auditor validated the terminal dispositions (`95a19c31-c46d-458b-943a-aff5c7af8727`).

Cycle 16 launched the first bounded Wave 4 validation/ablation tranche. The researcher brief (`812bb0b4-a759-400c-b5d8-91148ef4b9ce`) requested three independent branches: Track 2 held-out ghost-partner validation, Track 5 temporal/source validation, and Track 3 convergence/null-model validation. The supplied fork merge report for `cc044bf40be3` records all three branches as completed.

## Findings

### Cycle 14: Barrier 3 Atlas Readiness

Barrier 3 was validated with nonblocking warnings. The readiness package verified that the Atlas exposes all six Wave 3 instruments with provenance, caveats, evidence-vs-prediction boundaries, and missing-data indicators.

![Per-track Atlas projection coverage, showing source rows, projected rows, and taxon pages carrying queryable evidence/prediction sections.](reports/barrier3_atlas_instrument_coverage.png)

The machine-readable contract reported these source/projected/page counts:

| Track | Source rows | Atlas projected rows | Pages with rows | Barrier 3 status |
|---|---:|---:|---:|---|
| Track 1 | 60,000 | 60,000 | 60,000 | ready |
| Track 2 | 31 | 6 | 6 | ready |
| Track 3 | 16 | 50 | 50 | ready with nonblocking warning |
| Track 4 | 3 | 6 | 5 | ready data-limited |
| Track 5 | 1,405 | 1,405 | 65 | ready with source-dominance warning |
| Track 6 | 840 | 244 | 48 | ready with nonblocking warning |

The auditor reran the Atlas build, the Barrier 3 validator, the targeted pytest suite, Barrier 1 and Barrier 2 validators, `promise_check`, and `org_check`. The Atlas rebuild produced 60,000 pages and 60,000 search-index rows. No page rows used unsupported `validated` status, and master ledgers remained header-only.

The nonblocking warnings are part of the result. Track 3 page projection is support-list-limited because long support lists in `convergence_predictions.tsv` are truncated. Track 4 remains data-limited because observed bioclim vectors are absent. Track 5 remains source-dominated. Track 6 is benchmark-only/data-limited because no free/open local model runtime is available.

### Cycle 15: M1.3 And M1.6 Source Disposition

Cycle 15 closed two stale Wave 1 source branches as terminal data-limited source-coverage limitations.

M1.3, the reticulation specialty-source branch, was not treated as a Track 1 instrument failure. Its local source branch contains 28 staged reticulation rows: 12 chromosome-count assertions, 6 ploidy-state assertions, 1 hybridization event, 4 polyploidization events, and 5 reticulate-inheritance evidence rows. Only 3 rows resolved to accepted keys; 25 remained `pending_crosswalk`. The canonical polyploid seed set remains pending-crosswalk or absent in the frozen accepted-key namespace. The disposition records this as `deferred_terminal_data_limited`, encoded in the ledger as `deferred`.

M1.6, the domestication/CWR-climate source branch, was also closed as terminal data-limited. Track 4 retained 6 observed domestication edges, joined 3 of 69 crop-wild-relative pairs, and joined 36 of 375 climate-envelope rows, but observed bioclim vector count is 0. Climate matching is therefore undefined, not negative evidence. Track 4 candidate rows remain `pending_data_limited` rankings, not deployment recommendations.

The auditor validated both dispositions. The stale mechanism warning disappeared from `promise_check`, and Barrier 1, Barrier 2, and Barrier 3 validators still passed. No substrate, instrument, Atlas, prediction-ledger, or speculation-ledger content was promoted or rewritten.

### Cycle 16: Track 2 Wave 4 Validation Closure

Track 2 tested whether the Ghost-Partner Candidate Ranker recovered canonical Janzen-Martin held-out cases under accepted-key, modern-failure, singleton-source, source-class, and living-megafauna controls. No held-out case was validated.

| Outcome | Count |
|---|---:|
| validated | 0 |
| pending | 0 |
| falsified under ablation | 1 |
| data-limited | 6 |
| insufficient-support | 1 |

`Asimina triloba` was the only pre-ablation validation-ready held-out case, but it was falsified as validation-ready under singleton/source-class controls. Six cases were data-limited, mostly because accepted focal taxon keys were absent. `Annona cherimola` was insufficiently supported because modern dispersal-failure evidence was missing and support was singleton-source.

![Held-out status counts and ablation survival under singleton-source, source-class, accepted-key, and modern-failure controls.](tracks/track2/figures/track2_wave4_validation_ablation.png)

The branch does not claim any biological anachronism is absent. Its falsification is narrower: under the current frozen evidence package, H2 is not supported at the requested 30% canonical recovery threshold.

### Cycle 16: Track 3 Wave 4 Validation And Confound Ablation

Track 3 reinterpreted frozen convergence-pressure outputs under Wave 4 validation and null-model controls. The statistic remains:

`CP_min(T) = min(z_N1(T), z_N2(T))`

Here, N1 preserves family-size carrier structure, and N2 preserves sampling-density carrier structure. A trait remains a pending convergence prior only when both null comparisons are finite, `_other` is excluded, and confound checks do not fail.

The H3 decision is `data_limited`. `drupe` and `capsule` remain the only pending convergence-prior hypotheses. `drupe` has 187 carriers, 32 families, and `CP_min = 5.647`. `capsule` has 544 carriers, 48 families, and `CP_min = 4.831`. Neither enters the master prediction ledger because independent validation and Barrier 4 reconciliation remain pending.

![Observed CP_min against N1/N2 null context for scored Track 3 traits; vertical dashed line marks the CP_min >= 2 pending-prior threshold.](tracks/track3/figures/track3_wave4_null_model_comparison.png)

The result does not validate adaptive convergence, independent origins, evolutionary inevitability, new trait occurrences, new taxonomy, or new distribution facts. Canonical traits such as C4 photosynthesis, fleshy fruit, myrmecochory, elaiosome, and samara did not clear the current frozen-substrate threshold and were classified as data-limited rather than biological negatives. `_other` remains diagnostic-only.

### Cycle 16: Track 5 Temporal And Source Closure

Track 5 did not validate H5 under frozen inputs. The temporal holdout branch evaluated eight canonical phytochemical-source taxa: *Taxus brevifolia*, *Catharanthus roseus*, *Cinchona officinalis*, *Artemisia annua*, *Digitalis purpurea*, *Papaver somniferum*, *Atropa belladonna*, and *Salix alba*. None was recovered in the top decile. The cutoff status for all eight was `no_assertion_dates_available`, and several targets failed accepted-key or family/class signature requirements.

The source-ablation result was stronger. The full baseline emitted 1,405 prediction rows. Removing Dr. Duke produced 0 rows. Source-density-matched and screening-count-matched variants also produced 0 rows. Duke-downweighted rows persisted only because Duke still supplied the family/class support term.

![Temporal holdout family-percentile outcomes compared with prediction-count survival under no-Duke, source-matched, screening-matched, and Duke-downweighted ablations.](tracks/track5/figures/track5_wave4_temporal_source_summary.png)

The branch therefore records `M4.V5` as deferred/data-limited and validates `M4.A-track5-duke-source-ablation` as a source-bias null result. The evidence firewall remains in force: the result is about prediction mechanics and source coverage, not taxon-level compound detection, bioactivity, clinical effect, dose, preparation, or safety.

## Discussion

Cycles 14-16 advanced the campaign by closing gates and turning weak claims into classified outcomes. Barrier 3 is now auditor-validated: the Atlas is sufficient as a query surface for all six Wave 3 instruments. That does not mean any biological prediction has been validated. It means the interface preserves status, caveats, provenance, and missingness well enough for validation work to proceed.

The source-branch dispositions are also substantive. M1.3 and M1.6 no longer hang over the campaign as ambiguous process debt. M1.3 explains why Track 1’s TCI remains data-limited: unresolved reticulation rows cannot increase accepted-key evidence, and chromosome/ploidy rows are structural context rather than reticulation events. M1.6 explains why Track 4 cannot yet make climate-suitability recommendations: observed bioclim vectors are absent.

The Wave 4 tranche produced mostly null and data-limited results. Track 2 did not validate H2. Track 3 did not validate H3. Track 5 did not validate H5 and instead produced a validated source-bias finding. These are negative results, but they are organized outcomes rather than failures hidden in the artifact trail.

## Open Questions

Barrier 4 remains open. The master `prediction_ledger.tsv` and `speculation_ledger.tsv` still have no data rows, so track-local pending hypotheses and null results have not yet been reconciled into a cross-track ledger.

Track 1 still needs accepted-key recovery for canonical polyploid and hybrid cases before H1 can be tested as originally framed. Track 4 still needs observed bioclim vectors and broader accepted-key CWR coverage before climate substitution claims can be evaluated. Track 6 remains benchmark-only/data-limited until a free/open local model runtime or approved model-evaluation path exists.

For Track 2, reopening validation requires accepted-key repair, independent modern dispersal-failure evidence, non-singleton source support, or explicit living-megafauna contrast evidence. For Track 3, reopening H3 validation requires independent trait-list validation and stronger source/family/sampling controls. For Track 5, reopening H5 requires historical assertion dates and non-Duke phytochemical support sufficient for a matched comparison.

## References

[4] The World Flora Online Consortium et al., "World Flora Online Plant List December 2025," Zenodo, 2025. https://doi.org/10.5281/zenodo.18007552

[27] CCDB, "Chromosome Counts Database (CCDB)," Tel Aviv University, version 1.66.6, 2026. https://ccdb.tau.ac.il/

[28] Anna Rice, Lior Glick, Shiran Abadi, et al., "The Chromosome Counts Database (CCDB) — a community resource of plant chromosome numbers," New Phytologist, 2015. https://doi.org/10.1111/nph.13191

[29] Ilia J. Leitch, Emma Johnston, Jaume Pellicer, Oriane Hidalgo, and Michael D. Bennett, "Plant DNA C-values Database," Royal Botanic Gardens, Kew, 2026. https://cvalues.science.kew.org/

[31] Daniel Falster, Rachael Gallagher, Elizabeth Wenk, Herve Sauquet, et al., "AusTraits: a curated plant trait database for the Australian flora," Zenodo, version 6.0.0, 2024. https://doi.org/10.5281/zenodo.11188867

[38] James A. Duke, "Dr. Duke's Phytochemical and Ethnobotanical Databases," Ag Data Commons, 2023. https://agdatacommons.nal.usda.gov/articles/dataset/Dr_Duke_s_Phytochemical_and_Ethnobotanical_Databases/24660351

[40] KNApSAcK Family, "KNApSAcK Core System," KNApSAcK Family Databases, 2026. http://www.knapsackfamily.com/KNApSAcK/

[41] Zeng et al., "NPASS: Natural Product Activity and Species Source Database," NPASS, 2026. https://bidd.group/NPASS/

[42] EMBL-EBI, "ChEBI: Chemical Entities of Biological Interest," EMBL-EBI, 2026. https://www.ebi.ac.uk/chebi/

## Appendix: Implementation Details

### Code Organization

Cycle 14-16 added or used four main Python scripts: `tools/validate_barrier3_atlas_integration.py` for the Barrier 3 contract, `tracks/track2/scripts/track2_wave4_validation_closure.py` for Track 2 held-out classification, `tracks/track3/scripts/validate_wave4_convergence.py` for Track 3 null-model interpretation, and `tracks/track5/scripts/build_wave4_temporal_source_closure.py` for Track 5 temporal/source closure.

Focused tests were added or used for each package: `tests/test_barrier3_atlas_integration.py`, `tests/test_source_branch_disposition.py`, `tracks/track2/tests/test_track2_wave4_validation_closure.py`, `tracks/track3/tests/test_track3_wave4_validation_ablation.py`, and `tracks/track5/tests/test_track5_wave4_closure.py`.

### Test Results

Cycle 14 worker checks reported Barrier 3 validator PASS, 31 targeted pytest tests passed, Barrier 2 validator PASS, Barrier 1 validator PASS, `promise_check` exit 0, and `org_check` exit 0. The cycle 14 auditor reran the same gate and validated Barrier 3.

Cycle 15 worker checks reported 5 focused tests passed, Barrier 3 validator PASS, Barrier 2 validator PASS, Barrier 1 validator PASS, and `promise_check` exit 0. The cycle 15 auditor appended closure events for M1.3 and M1.6 and confirmed no stale mechanism warning remained.

Cycle 16 branch checks reported Track 2 closure tests passed, Track 5 closure/predictor/validation tests passed with 14 tests, and Track 3 enrichment/convergence/Wave 4 tests passed with 22 tests. The shared Barrier 1, Barrier 2, and Barrier 3 validators continued to pass. Known inherited warnings remain in `promise_check` and `org_check`, but they were not defects in these packages.

### File Counts

`MANIFEST.md` was updated for `report_cycles_14-16` and now inventories 4 cycle-range Python scripts, 5 test files, and 1,678 script/test lines. It records 60,000 Barrier 3 Atlas pages, 60,000 search-index rows, 6 validated track adapters, 2 terminal source-branch dispositions, 8 Track 2 held-out cases, 16 Track 3 Wave 4 trait rows, and 13 Track 5 Wave 4 outcome rows.

### Session References

Direct session sources:

| Cycle | Role | Session ID | Contents |
|---|---|---|---|
| 14 | researcher | `1c9552eb-fdc4-4965-9bb1-3b06a1ae0da5` | Barrier 3 readiness brief |
| 14 | worker | `86671fae-c3d0-4f38-a0dc-db755413adf5` | Barrier 3 readiness package |
| 14 | auditor | `e6517447-afc8-4aa4-a867-5f25398d0f15` | Barrier 3 validation |
| 15 | researcher | `4c21033c-1e55-46c4-ba90-f334e5ce72c3` | M1.3/M1.6 source disposition brief |
| 15 | worker | `479955d6-b87b-4498-b933-980e3a3ee806` | Source disposition package |
| 15 | auditor | `95a19c31-c46d-458b-943a-aff5c7af8727` | Source disposition validation |
| 16 | researcher | `812bb0b4-a759-400c-b5d8-91148ef4b9ce` | Wave 4 validation/ablation fan-out brief |

Cycle 16 worker results are represented by the supplied fork merge report for `cc044bf40be3`, with clone outputs for Track 2, Track 5, and Track 3. No separate cycle 16 worker or auditor session ID was supplied in the input list.

### Cross-Reference Map

`botanical_atlas_site/build_atlas.py` feeds `data/barrier3_atlas_instrument_contract.tsv` and `reports/barrier3_atlas_instrument_readiness.md`.

`tracks/track1/outputs/pending_crosswalk_reticulation_evidence.tsv` supports the M1.3 terminal data-limited mechanism in `reports/source_branch_disposition_m1_3_m1_6.md`.

`tracks/track4/data/crop_substitution_engine_summary.json` supports the M1.6 terminal data-limited mechanism through the zero observed bioclim vector result.

`tracks/track2/data/ghost_partner_ablation_results.tsv` feeds `tracks/track2/data/track2_wave4_validation_outcomes.tsv`, where the only pre-ablation validation-ready held-out case becomes falsified under controls.

`tracks/track3/data/convergence_pressure_scores.tsv` feeds `tracks/track3/data/track3_wave4_validation_outcomes.tsv`, where rows are classified as pending, data-limited, observed-only, or diagnostic.

`tracks/track5/data/source_ablation_results.tsv` feeds `tracks/track5/data/track5_wave4_validation_outcomes.tsv`, establishing the Duke/source-dominance null result.

`prediction_ledger.tsv` and `speculation_ledger.tsv` remain header-only throughout the cycle range.
