---
title: "PhytoGraph — cycles 10-10"
date: "2026-05-18"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph — cycles 10-10

## Abstract

Cycle 10 moved PhytoGraph from Barrier 2 enrichment toward Wave 3 predictive instruments and the Botanical Atlas interface. The cycle was organized as a five-branch fan-out under fork `aaf42b4ab956`, following the cycle 10 researcher directive in session `bca85b8f-fb71-4023-b70f-d61bbbc44d36`.

The branches targeted:

- Track 1: Reticulation Atlas / tree-compatibility index.
- Track 2: Ghost-Partner Candidate Ranker.
- Track 3: Convergence-Pressure Statistic.
- Track 5: Chemodiversity Neighborhood-Completion Predictor.
- Botanical Atlas scaffold.

The result was useful but not yet Barrier 3-ready. Track 2 and Track 5 produced required reports and track-local prediction tables. Track 1 and Track 3 produced usable instrument artifacts, but their required reports are missing because branch reporters failed under API rate limits. The Atlas branch produced a page contract and builder scaffold, but no generated site outputs or readiness report were detected.

No validated biological prediction was produced in cycle 10. The strongest findings are diagnostic: accepted-key gaps block Track 1 and Track 2 canonical recovery; Track 2 collapses under singleton-source removal; Track 5 collapses under Dr. Duke removal; Track 3 has a configured falsifier pass but high confound-model explanatory power; and the Atlas is still a contract plus scaffold rather than a demonstrated researcher interface.

## Introduction

Before cycle 10, PhytoGraph had passed Barrier 2: the six Wave 2 enrichment tracks were integrated under a common schema and conformance validator. The master `prediction_ledger.tsv` was still empty, because no Wave 3 predictive instruments had yet been merged into the campaign-level ledger.

The cycle 10 researcher session (`bca85b8f-fb71-4023-b70f-d61bbbc44d36`) defined the next critical path: build the remaining Wave 3 instruments for Tracks 1, 2, 3, and 5, and build the Botanical Atlas scaffold as a local interface over observed evidence, enrichment rows, predictions, missingness, and data-limited status.

The cycle explicitly held constant the Barrier 1 substrate, Barrier 2 enrichment outputs, schema version, synonym normalization, provenance conventions, Track 6 offline-only constraint, and the rule that no branch should write directly to the master prediction ledger. Each branch was expected to write only to its own namespace and produce track-local candidate outputs.

## Approach

Cycle 10 used a five-branch fan-out recorded in `.long-exposure/fork-aaf42b4ab956/fanout_merge.md` and synthesized in `.long-exposure/fork-aaf42b4ab956/fanout_merge_synthesized.md`.

The fan-out outcomes were:

| Clone | Target | Required report status | Main artifact state |
|---:|---|---|---|
| 0 | Track 1 Reticulation Atlas / TCI | Missing | TCI spec and 60,001-row output exist; canonical recovery data-limited |
| 1 | Track 2 Ghost-Partner Ranker | Present | 31 candidate rows and validation/ablation follow-up |
| 2 | Track 3 Convergence Pressure | Missing | Score, canonical recovery, null, and confound tables exist |
| 3 | Track 5 Chemodiversity Predictor | Present | 1,405 pending prediction rows and source-ablation follow-up |
| 4 | Botanical Atlas scaffold | Missing | Page contract and builder scaffold exist; generated site absent |

The missing Track 1, Track 3, and Atlas reports are recorded as reporter failures with API status 429, not as evidence that the workers did no implementation. The on-disk artifacts show recoverable implementation state for all three.

## Findings

### Track 1: Reticulation Atlas

Track 1 produced a tree-compatibility index, abbreviated TCI, but did not produce the required report `tracks/track1/reports/track1_reticulation_atlas.md`.

The TCI is specified in `tracks/track1/instruments/tci_spec.md` and implemented by `tracks/track1/instruments/build_tci.py`. It scores each taxon in `[0,1]`, where `1` means tree-compatible by available evidence and lower values reflect reticulation evidence or structural proxies. The specification separates direct evidence from structural priors. Direct evidence includes reticulate inheritance, hybridization, polyploidization, and crop-pedigree hyperedges. Structural priors include ploidy-state spread, chromosome-count variation, synonym-cluster size, and taxonomic conflicts.

The main output, `tracks/track1/outputs/tci_per_taxon.tsv`, contains 60,001 data rows. The visible rows are mostly `data_limited_unknown` or `structural_only`, with zero direct reticulation evidence edges in the displayed sample.

The canonical recovery table, `tracks/track1/outputs/canonical_recovery_report.tsv`, contains eight seed cases:

- *Triticum aestivum*
- *Brassica napus*
- *Spartina anglica*
- *Tragopogon mirus*
- *Tragopogon miscellus*
- *Musa acuminata × balbisiana*
- *Musa acuminata*
- *Musa balbisiana*

All eight are `data_limited`. The reason is not score design; it is accepted-key resolution. Most rows are `pending_crosswalk`, and one is absent. Track 1 therefore has an implemented scoring instrument, but it has not recovered the canonical polyploid/hybrid validation cases under accepted-key resolution.

### Track 2: Ghost Hyperedges

Track 2 produced the required report `tracks/track2/reports/track2_ghost_hyperedges.md`, a candidate ranker, a track-local prediction table, and a Wave 4 validation/ablation update.

The ranker scored 31 candidate rows from the Track 2 seed layer. It uses a transparent prioritization statistic:

```text
S(c) = 0.25 M + 0.25 E + 0.20 F + 0.20 G + 0.10 P - 0.15 L - 0.10 Q
```

Here `M` is morphology support, `E` is extinct-fauna or paleo-context support, `F` is modern dispersal-failure support, `G` is geography/time compatibility, `P` is provenance completeness, `L` is living-megafauna ambiguity, and `Q` is singleton-source thinness. The report states that this score is not a truth probability.

Track 2 emitted 31 rows in `tracks/track2/data/ghost_partner_predictions.tsv`. Status counts in the on-disk report are:

| Status | Count |
|---|---:|
| `candidate_pending_validation` | 1 |
| `data_limited` | 25 |
| `insufficient_support` | 5 |

The top-ranked row is *Asimina triloba*, score `0.800`, status `candidate_pending_validation`, with `source_singleton` ambiguity. Other high-ranked rows include *Diospyros virginiana*, *Gymnocladus dioicus*, *Maclura pomifera*, *Crescentia alata*, *Enterolobium cyclocarpum*, and *Persea americana*, but these are mostly data-limited.

The held-out Janzen-Martin scaffold contains eight canonical taxa. All eight are present in the seed layer. Only *Asimina triloba* is `recovered_validation_ready_seed`; six are recovered but data-limited; *Annona cherimola* is recovered but insufficient-support.

The validation/ablation update in `tracks/track2/reports/track2_validation_and_ablation.md` changes the practical interpretation. Under the baseline, one held-out case is validation-ready. Removing singleton-source rows removes all candidates. Removing modern dispersal-failure support eliminates validation-ready status. Removing paleobotany/extinct-fauna support collapses the score basis. Track 2 is therefore a useful candidate scaffold, but it has no validated ghost-partner claim.

![Score/status movement under Track 2 evidence-removal and confound-control ablations.](tracks/track2/figures/ghost_partner_ablation_sensitivity.png)

### Track 3: Convergence Pressure

Track 3 produced convergence-pressure artifacts but did not produce the required report `tracks/track3/reports/track3_convergence_pressure.md`.

The main script is `tracks/track3/scripts/convergence_pressure.py`. The outputs include:

- `tracks/track3/data/convergence_pressure_scores.tsv`
- `tracks/track3/data/convergence_pressure_canonical_recovery.tsv`
- `tracks/track3/data/convergence_pressure_confound_regression.tsv`
- `tracks/track3/data/convergence_pressure_nulls.tsv`
- `tracks/track3/data/convergence_pressure_run_summary.json`

The run summary names 15 scored traits and excludes `_other` from canonical interpretation. Three traits are data-limited: `ant_domatia`, `carnivory`, and `parasitism`.

Two traits clear the score bar in the available table:

| Trait | Carriers | Families | `CP_min` | Clears bar |
|---|---:|---:|---:|---|
| `drupe` | 187 | 32 | 5.647328 | True |
| `capsule` | 544 | 48 | 4.831440 | True |

Other canonical traits do not clear the score bar in the table, including succulence, CAM photosynthesis, fleshy fruit, samara, C4 photosynthesis, elaiosome, and myrmecochory. The `_other` bucket is explicitly excluded from canonical interpretation.

The confound regression table reports high explanatory power from confound-style predictors: `R2_observed_H_family = 0.8353` and `R2_CP_min = 0.8517`. The branch’s configured falsifier still reports `PASS` because the residual Spearman correlation is about `0.4056`, below the branch threshold of absolute rho greater than `0.8`.

This means Track 3 has an implemented diagnostic statistic, but the missing report must define exactly what the statistic supports. The available artifacts should not be promoted as validated convergence biology.

![Track 3 convergence-pressure score output for canonical and diagnostic traits.](tracks/track3/data/convergence_pressure_figure.png)

### Track 5: Chemodiversity Predictor

Track 5 produced the required report `tracks/track5/reports/track5_chemodiversity.md`, a prediction table, and a Wave 4 temporal validation/source-ablation update.

The predictor is a family-level neighborhood-completion prior. For taxon `t`, family `f`, and compound class `k`, the score is:

```text
score(t, k | f) = S_f[k] * w_specificity(k) * w_screening(t)
```

`S_f[k]` is the share of screened taxa in family `f` with at least one retained compound in class `k`; `w_specificity(k)` downweights globally common classes; and `w_screening(t)` prioritizes under-screened taxa.

The baseline output contains:

| Measure | Value |
|---|---:|
| Pending prediction rows | 1,405 |
| Prediction-bearing families | 13 |
| Predicted compound classes | 54 |
| Rows with compound-indirected bioactivity annotation | 735 |
| Data-limited family speculation rows | 37 |
| Predictions after dropping Dr. Duke | 0 |

The evidence firewall is explicit. Rows predict only candidate compound classes for future screening. They do not assert phytochemical detection, taxon-level bioactivity, clinical efficacy, preparation safety, dosage, or therapeutic value. The Dr. Duke database [38] dominates the current Track 5 evidence layer, and every prediction row is Dr. Duke sensitive.

The Wave 4 update in `tracks/track5/reports/track5_temporal_validation.md` records eight canonical holdout rows. All eight are `data-limited`; none reaches top-decile recovery. The current frozen tables do not contain historical assertion dates, so the temporal validation target cannot yet validate H5.

The four required canonical examples have these results:

| Taxon | Target class | Cutoff | Result |
|---|---|---:|---|
| *Taxus brevifolia* | Diterpene | 1970-12-31 | Name absent; family/class signature absent |
| *Catharanthus roseus* | Alkaloid | 1957-12-31 | Name seen only without accepted key; family/class signature absent |
| *Cinchona officinalis* | Alkaloid | 1819-12-31 | Name absent; family/class signature absent |
| *Artemisia annua* | Sesquiterpene | 1971-12-31 | Accepted key resolved, but Asteraceae/Sesquiterpene signature absent |

Source ablations are decisive. The full variant has 1,405 rows. The no-Duke variant has zero. Source-density-matched and screening-count-matched variants also have zero rows. Track 5 is therefore a reproducible screening-prior table with a strong source-dominance caveat, not a validated chemodiversity discovery instrument.

![Track 5 prediction count and top-decile recovery across source-ablation variants.](tracks/track5/figures/source_ablation_prediction_counts.png)

![Track 5 holdout percentile ranks under the current frozen source coverage.](tracks/track5/figures/temporal_holdout_family_percentiles.png)

![Candidate score as a function of Dr. Duke share in source families.](tracks/track5/figures/duke_share_vs_score.png)

### Botanical Atlas

The Atlas branch produced `botanical_atlas_site/page_contract.md` and `botanical_atlas_site/build_atlas.py`, but it did not produce the required readiness report `botanical_atlas_site/reports/atlas_readiness_report.md`.

The page contract defines the Atlas invariant: every rendered claim must be labelled by evidence class and provenance, so a researcher cannot confuse a Wave 3 prediction with a substrate observation. The contract defines four bands:

| Class | Meaning |
|---|---|
| `OBSERVED` | direct ingested source rows |
| `ENRICHED` | Wave 2 source projections or Track 6 ground truth |
| `PREDICTED` | Wave 3 instrument output or inferred rows |
| `DATA-LIMITED` | no substrate or instrument rows for the taxon/track |

The builder scaffold is substantial. It reads `phytograph_dataset/` and track outputs, writes static JSON pages, emits a search index, writes a provenance registry, and includes a counter-claim template. It also defines a visible `instrument_pending` state when a Wave 3 instrument output is absent.

However, the file scan found no generated Atlas outputs beyond source files and Python bytecode. Missing generated artifacts include pages, `search_index.json`, `coverage_summary.json`, `provenance_registry.json`, `index.html`, `app.js`, `style.css`, and a readiness report. The Atlas therefore remains pre-Barrier-3.

## Discussion

Cycle 10 advanced PhytoGraph’s Wave 3 instrument layer, but it did not cross the line from candidate/scaffold to validated prediction.

The first shared constraint is accepted-key resolution. Track 1 and Track 2 both contain biologically recognizable canonical examples, but accepted-key gaps prevent those examples from functioning as validation targets. The next work is not mainly score refinement; it is crosswalk repair for canonical polyploid/hybrid taxa and Janzen-Martin seed taxa.

The second shared constraint is source dominance. Track 2 is singleton-source dominated. Track 5 is Dr. Duke dominated. These are not minor caveats. They determine whether candidate rows survive ablation. Until independent support is added, these outputs should remain track-local and should not be promoted to validated campaign-level ledger rows.

The third constraint is report and interface incompleteness. Track 1 and Track 3 have artifacts but missing reports. The Atlas has a contract and code but no demonstrated build. Barrier 3 requires instruments to be queryable from the Atlas with prediction-vs-evidence distinctions visible. Cycle 10 did not meet that condition.

The useful outcome of cycle 10 is therefore a disciplined map of what is ready, what is blocked, and why. Track 2 and Track 5 have reproducible local instruments. Track 1 and Track 3 have recoverable instrument state. The Atlas has a clear evidence-class invariant. None yet provides a validated biological prediction.

## Open Questions

1. Can accepted-key repair recover the Track 1 canonical polyploid/hybrid cases and the Track 2 Janzen-Martin cases without changing schema or re-normalizing independently inside tracks?

2. Can Track 2 add non-singleton modern dispersal-failure evidence so that at least one held-out candidate remains validation-ready after source ablation?

3. Can Track 3’s convergence-pressure report define a defensible claim scope given the high confound-model R2 values?

4. Can Track 5 recover non-Duke compound-class support from KNApSAcK, NPASS, ChEBI, or other sources before rerunning temporal holdouts?

5. Can the Atlas builder be run or repaired to produce pages, search index, provenance registry, coverage summary, counter-claim template, and readiness report?

6. After those repairs, which track-local rows, if any, are mature enough for conservative master-ledger reconciliation?

## References

[38] James A. Duke, "Dr. Duke's Phytochemical and Ethnobotanical Databases," Ag Data Commons, 2023. https://agdatacommons.nal.usda.gov/articles/dataset/Dr_Duke_s_Phytochemical_and_Ethnobotanical_Databases/24660351 (accessed 2026-05-17).

## Appendix: Implementation Details

### Source Sessions And Reports

| Source | Date | Role in cycle 10 report |
|---|---|---|
| `bca85b8f-fb71-4023-b70f-d61bbbc44d36` | 2026-05-18 | Researcher session defining Wave 3 fan-out objectives and sufficiency criteria |
| `.long-exposure/fork-aaf42b4ab956/fanout_merge.md` | 2026-05-18 | Raw five-branch merge report |
| `.long-exposure/fork-aaf42b4ab956/fanout_merge_synthesized.md` | 2026-05-18 | Cross-branch synthesis used for branch status and next-cycle interpretation |
| `tracks/track2/reports/track2_ghost_hyperedges.md` | 2026-05-18 | Required Track 2 M3 report |
| `tracks/track2/reports/track2_validation_and_ablation.md` | 2026-05-18 | Track 2 Wave 4 validation/ablation update |
| `tracks/track5/reports/track5_chemodiversity.md` | 2026-05-18 | Required Track 5 M3 report |
| `tracks/track5/reports/track5_temporal_validation.md` | 2026-05-18 | Track 5 Wave 4 temporal/source-ablation update |

### Code Organization

| Area | Key files | Purpose |
|---|---|---|
| Track 1 | `tracks/track1/instruments/tci_spec.md`, `tracks/track1/instruments/build_tci.py` | TCI specification and builder |
| Track 2 | `scripts/track2_ghost_partner_ranker.py`, `tracks/track2/scripts/track2_validation_recovery.py`, `tracks/track2/scripts/track2_ablation_checks.py` | Ghost-partner scoring, recovery, and ablation |
| Track 3 | `tracks/track3/scripts/convergence_pressure.py`, `tracks/track3/scripts/trait_dictionary.py` | Convergence-pressure scoring and trait dictionary |
| Track 5 | `tracks/track5/scripts/track5_predictor.py`, `tracks/track5/scripts/build_temporal_holdout_validation.py`, `tracks/track5/scripts/run_source_ablation_matrix.py` | Chemodiversity prediction, temporal holdouts, and source ablations |
| Atlas | `botanical_atlas_site/page_contract.md`, `botanical_atlas_site/build_atlas.py`, `tests/test_atlas_build.py` | Evidence-class contract and static-site scaffold |

### File Counts And Outputs

| Artifact | Count |
|---|---:|
| Track 1 TCI rows | 60,001 |
| Track 1 canonical recovery rows | 8 |
| Track 2 prediction rows | 31 |
| Track 2 ablation variants | 6 |
| Track 3 scored table rows | 16 |
| Track 5 prediction rows | 1,405 |
| Track 5 temporal holdout rows | 8 |
| Track 5 source-ablation variants | 5 |
| Master `prediction_ledger.tsv` data rows | 0 |
| Master `speculation_ledger.tsv` data rows | 0 |

### Test And Validation Record

The branch records report the following validation commands and results:

| Branch | Reported validation |
|---|---|
| Track 2 | `python3 scripts/track2_ghost_partner_ranker.py`; `python3 -m pytest -q tracks/track2/tests/test_ghost_partner_ranker.py` |
| Track 5 M3 | `python3 tracks/track5/scripts/track5_predictor.py`; Dr. Duke drop run; Track 5 enrichment validator; focused tests reported as 14 passed |
| Track 5 M4 | `python3 tracks/track5/scripts/build_temporal_holdout_validation.py`; `python3 tracks/track5/scripts/run_source_ablation_matrix.py`; `python3 tracks/track5/scripts/harmonize_non_duke_compound_classes.py`; Track 5 Wave 4 tests |
| Barrier checks | Track 5 report records Barrier 2 validation, Barrier 1 substrate validation, promise check, and organization check commands |

This reporter did not rerun those tests. The report records the branch validation claims and the on-disk artifacts.

### Cross-Reference Map

| Finding | Primary source |
|---|---|
| Five-branch cycle 10 fan-out and branch statuses | `.long-exposure/fork-aaf42b4ab956/fanout_merge_synthesized.md` |
| Track 1 TCI definition and data-limited canonical recovery | `tracks/track1/instruments/tci_spec.md`; `tracks/track1/outputs/canonical_recovery_report.tsv` |
| Track 2 candidate counts and held-out scaffold | `tracks/track2/reports/track2_ghost_hyperedges.md` |
| Track 2 singleton-source collapse | `tracks/track2/reports/track2_validation_and_ablation.md`; `tracks/track2/data/ghost_partner_ablation_results.tsv` |
| Track 3 score and confound tension | `tracks/track3/data/convergence_pressure_scores.tsv`; `tracks/track3/data/convergence_pressure_confound_regression.tsv`; `tracks/track3/data/convergence_pressure_run_summary.json` |
| Track 5 Dr. Duke sensitivity and prediction counts | `tracks/track5/reports/track5_chemodiversity.md`; `tracks/track5/data/source_ablation_results.tsv` |
| Track 5 temporal holdout data-limited result | `tracks/track5/reports/track5_temporal_validation.md`; `tracks/track5/data/temporal_holdout_recovery.tsv` |
| Atlas evidence-class invariant and missing generated outputs | `botanical_atlas_site/page_contract.md`; `botanical_atlas_site/build_atlas.py`; file scan of `botanical_atlas_site/` |
| Manifest snapshot | `MANIFEST.md` updated for `report_cycles_10-10` |

### Barrier Status

Cycle 10 remains pre-Barrier-3. The cycle produced track-local instruments and scaffolds, but did not demonstrate Atlas-queryable instrument integration. The master prediction and speculation ledgers contain only headers. No cycle 10 row should be treated as a validated campaign-level biological prediction.
