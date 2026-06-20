---
title: "PhytoGraph — cycles 11-13"
date: "2026-05-18"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph — cycles 11-13

## Abstract

Cycles 11-13 repaired campaign bookkeeping, completed two missing Wave 3 instruments, rebuilt the Botanical Atlas as a six-track integration surface, and then reconciled a post-merge disagreement so Track 1 and Track 3 were no longer stale Atlas placeholders.

The main technical result is that the Atlas now exposes all six track-local Wave 3 outputs across 60,000 searchable taxon pages with evidence-vs-prediction labels. Track 1 contributes 60,000 tree-compatibility index rows. Track 3 contributes pending convergence-prior rows for `drupe` and `capsule`. Tracks 2, 4, 5, and 6 remain exposed through their existing adapters. The master `prediction_ledger.tsv` and `speculation_ledger.tsv` remain header-only.

This cycle range does not close Barrier 3 at audit level and does not validate any biological prediction. It makes the instruments queryable from the Atlas and preserves the campaign boundary that track-local hypotheses are not master-ledger claims.

## Introduction

PhytoGraph is organized around barriers. Barrier 2 had already produced a frozen substrate and track enrichment. Wave 3 then required predictive instruments and an Atlas surface that could query those instruments without blurring observed evidence, enriched evidence, model predictions, and missing data.

At the end of cycle 10, three problems remained. Track 1 had an implemented tree-compatibility instrument but lacked the required report. Track 3 had score tables and diagnostics but lacked the required report. The Atlas scaffold existed as a contract, but the generated site outputs and Track 1/Track 3 queryability were not yet demonstrated. Cycles 11-13 addressed those gaps.

The reporting sources for this cycle range are:

- Cycle 11 worker session `0b9e8647-ca47-48dc-9089-532600e91768`.
- Cycle 12 researcher session `60693f48-7d7a-43e8-9ddc-d9048f53f167`.
- Cycle 13 worker session `0b3756f0-b117-4880-8478-8f96258bfd2a`.
- Fork `eec13528227c` merge reports.
- The post-merge integration audit report provided with this task.
- Workspace artifacts listed in the appendix.

## Approach

The work proceeded in three steps.

First, cycle 11 repaired plan and ledger alignment. A manager intervention had identified hard `promise_check` failures caused by Wave 4 child milestone IDs that existed in the append-only ledger but not in `plan_of_record.md`. The worker added exact plan rows for `M4.V2`, `M4.V5`, and `M4.A-track5-duke-source-ablation`, then reran `promise_check` and `org_check`. This was a bookkeeping repair only. It did not advance Barrier 3 and did not promote predictions.

Second, cycle 12 launched a three-branch Wave 3 fan-out under fork `eec13528227c`:

| Branch | Objective | Required artifact |
|---|---|---|
| Clone 0 | Build Track 1 Reticulation Atlas instrument and report | `tracks/track1/reports/track1_reticulation_atlas.md` |
| Clone 1 | Build Track 3 Convergence Pressure instrument and report | `tracks/track3/reports/track3_convergence_pressure.md` |
| Clone 2 | Build Botanical Atlas scaffold | `botanical_atlas_site/reports/atlas_barrier3_scaffold.md` |

Third, cycle 13 integrated the fork outputs into the main Atlas surface. The post-merge worker changed the Atlas builder and tests, regenerated the site outputs, and confirmed that Track 1 and Track 3 were no longer represented as stale placeholder contracts.

## Findings

### Cycle 11: Plan-Ledger Repair

Cycle 11 repaired a consistency failure, not a biological or instrument gap. The problem was that three Wave 4 ledger rows already existed under milestone IDs that were not declared in the plan of record. This caused `promise_check` to fail.

The worker updated `plan_of_record.md` with the exact child milestone IDs:

- `M4.V2`
- `M4.V5`
- `M4.A-track5-duke-source-ablation`

The repair note states that these are historical track-local outputs and do not authorize additional Wave 4 validation before Barrier 3. After the update, `promise_check` exited 0, and both master ledgers remained header-only.

### Cycle 12: Track 1 Reticulation Atlas

Track 1 now has the required Wave 3 Reticulation Atlas report and regenerated TCI outputs. TCI means tree-compatibility index: a per-taxon score in `[0,1]` where lower values indicate more evidence that a single-parent tree encoding loses information.

The Track 1 worker repaired the evidence boundary in `tracks/track1/instruments/build_tci.py`. Observed reticulation evidence now counts only accepted-key, event-shaped evidence: `hybridization_event`, `polyploidization_event`, event-shaped `reticulate_inheritance_evidence`, or accepted multi-parent `crop_pedigree` evidence. Chromosome-count and ploidy-state rows are structural context only; they no longer count as direct reticulation events.

The instrument produced:

| Output | Count |
|---|---:|
| Accepted keys scored | 60,000 |
| Evidence-supported taxa | 2 |
| Structural-only taxa | 29,294 |
| Data-limited unknown taxa | 30,704 |
| Genus hotspot rows | 14,292 |
| Accepted-key resolved Track 1 enrichment rows | 3 |
| Pending-crosswalk Track 1 enrichment rows | 25 |

The TCI summary reports a minimum TCI of 0.5, mean TCI of 0.986858, and maximum TCI of 1.0. The two evidence-supported taxa are driven by retained multi-parent crop-pedigree evidence. The original canonical polyploid seed cases remain data-limited because they are pending-crosswalk or absent in the frozen accepted-key namespace. *Arachis hypogaea* and *Avena sativa* recover through accepted multi-parent crop-pedigree evidence, but the report explicitly says this does not validate the original M1.3 canonical seed set.

![Track 1 reticulation coverage by edge type. The key point is that direct event evidence remains sparse; structural context dominates current coverage.](tracks/track1/plots/reticulation_coverage_by_edge_type.png)

Track 1 validation run reported 28 passing focused reticulation tests, Barrier 2 conformance PASS, and `promise_check`/`org_check` exit 0 with known warnings only.

### Cycle 12: Track 3 Convergence Pressure

Track 3 now has the required Wave 3 Convergence Pressure report and a track-local prediction TSV for Atlas ingestion. Convergence pressure is a trait-level statistic that asks whether a retained trait is more dispersed across families than expected under two null models. The report uses `CP_min(T) = min(z_N1(T), z_N2(T))`, where `N1` preserves family-size carrier loads and `N2` preserves sampling density through per-taxon Track 3 edge-count weights.

A trait clears the pending convergence-pressure bar when `CP_min >= 2.0`. In the current frozen substrate, two traits clear that bar:

| Trait | Accepted-key carriers | Families | CP_min | Status |
|---|---:|---:|---:|---|
| `drupe` | 187 | 32 | 5.647 | pending convergent-trait hypothesis |
| `capsule` | 544 | 48 | 4.831 | pending convergent-trait hypothesis |

The `convergence_predictions.tsv` row classes are:

| Row class | Count |
|---|---:|
| `pending_convergent_trait_hypothesis` | 2 |
| `observed_trait_evidence_summary` | 10 |
| `data_limited_canonical_trait` | 3 |
| `diagnostic_bucket_excluded` | 1 |

The `_other` bucket remains diagnostic-only. The data-limited canonical traits are `ant_domatia`, `carnivory`, and `parasitism`, each with zero accepted-key carriers in the frozen Track 3 enrichment.

The falsifier summary records strong confounding in raw entropy but not a configured failure of the standardized statistic:

| Measure | Value |
|---|---:|
| `R2_observed_H_family` | 0.835 |
| `R2_CP_min` | 0.852 |
| `spearman_rho_residOBS_vs_CPmin` | 0.406 |
| Falsifier verdict | PASS |

The report interprets this narrowly: Track 3 does not validate H3, but it also does not falsify H3 under the stated `abs(rho) > 0.8` threshold. Wave 4 must still validate the two pending hypotheses against independent trait lists and source/family/sampling ablations. Track 3 uses AusTraits-heavy retained trait coverage from the earlier enrichment layer [31].

![Track 3 convergence-pressure figure. The plot shows the two traits clearing the current pending CP threshold and the diagnostic relationship to family-count structure.](tracks/track3/data/convergence_pressure_figure.png)

Track 3 validation run reported 16 passing focused tests, Barrier 2 conformance PASS, Barrier 1 substrate validation PASS, and header-only master ledgers.

### Cycle 12: Botanical Atlas Scaffold

The Atlas branch built a static site scaffold under `botanical_atlas_site/`. Its purpose is to make track outputs visible and queryable, not to generate new predictions.

The scaffold produced:

| Artifact | Role |
|---|---|
| `index.html`, `app.js`, `style.css` | Local static Atlas shell |
| `search_index.json` | 60,000-row search index |
| `pages/*.json` | 60,000 per-taxon page payloads |
| `coverage_summary.json` | Per-track coverage and adapter status |
| `provenance_registry.json` | Source-group provenance summary |
| `counter_claim_template.json` | Counter-claim schema |
| `build_log.json` | Reproducible build metadata |
| `tools/file_counter_claim.py` | Targeted counter-claim validator |
| `tests/test_atlas_build.py` | Atlas contract tests |

The scaffold enforced four page states:

| State | Meaning |
|---|---|
| `observed` | Source-ingested substrate rows |
| `enriched` | Wave 2 track-local source projections |
| `predicted` | Wave 3 instrument or result rows |
| `data-limited` | No accepted-key substrate or instrument row for that taxon/track section |

In the initial clone-2 branch, Track 2, Track 4, Track 5, and Track 6 outputs were exposed, while Track 1 and Track 3 were contract placeholders. The branch therefore did not close Barrier 3 by itself.

### Cycle 13: Post-Merge Atlas Integration

Cycle 13 reconciled the post-merge disagreement: the Atlas no longer leaves Track 1 and Track 3 as stale placeholders. The worker integrated Track 1 TCI outputs and Track 3 convergence-prior outputs into the Atlas adapters, rebuilt the site, and reran the checks.

The final Atlas build reported:

| Metric | Value |
|---|---:|
| Substrate nodes read | 363,237 |
| Substrate hyperedges read | 641,183 |
| Taxon crosswalk rows read | 75,269 |
| Per-taxon pages written | 60,000 |
| Search-index rows written | 60,000 |
| Build elapsed time | 61.43 seconds |

Final per-track page state:

| Track | Observed pages | Enriched pages | Predicted pages | Data-limited pages |
|---|---:|---:|---:|---:|
| Track 1 | 0 | 0 | 60,000 | 0 |
| Track 2 | 0 | 0 | 6 | 59,994 |
| Track 3 | 4 | 3,198 | 50 | 56,748 |
| Track 4 | 0 | 0 | 5 | 59,995 |
| Track 5 | 0 | 1,255 | 65 | 58,680 |
| Track 6 | 0 | 0 | 48 | 59,952 |

Final Atlas instrument rows detected by adapter:

| Track | Instrument rows | Taxa |
|---|---:|---:|
| Track 1 | 60,000 | 60,000 |
| Track 2 | 6 | 6 |
| Track 3 | 50 | 50 |
| Track 4 | 6 | 5 |
| Track 5 | 1,405 | 65 |
| Track 6 | 244 | 48 |

The post-merge tests reported 20 passing tests across Atlas, Track 1, and Track 3. Barrier 2 conformance passed. Barrier 1 substrate validation passed with 363,237 nodes and 641,183 retained hyperedges. `promise_check` and `org_check` exited 0 with warnings only.

One nonblocking warning remains: `promise_check` warns that ledger line 146 tracks `botanical_atlas_site/pages/` as a directory artifact rather than a canonicalized file artifact. The check still exits 0.

## Discussion

Cycles 11-13 changed the campaign state from “Wave 3 outputs exist but are not fully surfaced” to “all six track-local outputs are queryable from the Atlas.” This matters because Barrier 3 requires instrument-to-Atlas integration, not just standalone instrument files.

The work remains conservative in three ways.

First, the master ledgers are still empty. `prediction_ledger.tsv` and `speculation_ledger.tsv` each contain only a header row. Track-local rows are visible in the Atlas, but they have not been reconciled into Barrier 4 master prediction statuses.

Second, the Atlas labels Track 1 and Track 3 rows as predictions or instrument outputs with caveats. Track 1 TCI rows are data-limited instrument results, not established reticulation claims. Track 3 `drupe` and `capsule` rows are pending convergence-prior hypotheses, not validated convergence findings.

Third, Barrier 3 is ready for assessment but not closed by the worker reports. The post-merge integration made the missing outputs queryable, but the audit report explicitly says no audit-level validation was performed.

## Open Questions

The immediate open question is whether an auditor should close Barrier 3 after inspecting the updated Atlas. The worker evidence supports queryability and evidence-vs-prediction labeling, but audit-level closure remains unperformed.

Track 1 still needs accepted-key repair for the original canonical polyploid/hybrid seeds before recovery rates can be interpreted. Current recovery is data-limited for the original seed set.

Track 3 still needs Wave 4 validation and ablations for `drupe` and `capsule`. The statistic generated pending hypotheses, not validated convergence biology.

The Atlas still has a known limitation in Track 3 page projection: it uses explicitly listed supporting hyperedges from `convergence_predictions.tsv`, and long support lists are truncated there. The pages are queryable, but not exhaustive carrier enumerations.

Track 4 and Track 6 remain data-limited in their own ways. Track 4 lacks observed bioclim vectors. Track 6 executed deterministic offline controls only and did not evaluate hosted or local foundation models.

## References

[4] The World Flora Online Consortium et al., "World Flora Online Plant List December 2025," Zenodo, 2025. https://doi.org/10.5281/zenodo.18007552 (accessed 2026-05-17).

[27] CCDB, "Chromosome Counts Database (CCDB)," Tel Aviv University, version 1.66.6, 2026. https://ccdb.tau.ac.il/ (accessed 2026-05-17).

[28] Anna Rice, Lior Glick, Shiran Abadi, et al., "The Chromosome Counts Database (CCDB) — a community resource of plant chromosome numbers," New Phytologist, 2015. https://doi.org/10.1111/nph.13191 (accessed 2026-05-17).

[29] Ilia J. Leitch, Emma Johnston, Jaume Pellicer, Oriane Hidalgo, and Michael D. Bennett, "Plant DNA C-values Database," Royal Botanic Gardens, Kew, 2026. https://cvalues.science.kew.org/ (accessed 2026-05-17).

[30] Troy E. Wood, Naoki Takebayashi, Michael S. Barker, et al., "The frequency of polyploid speciation in vascular plants," Proceedings of the National Academy of Sciences, 2009. https://doi.org/10.1073/pnas.0811575106 (accessed 2026-05-17).

[31] Daniel Falster, Rachael Gallagher, Elizabeth Wenk, Herve Sauquet, et al., "AusTraits: a curated plant trait database for the Australian flora," Zenodo, version 6.0.0, 2024. https://doi.org/10.5281/zenodo.11188867 (accessed 2026-05-17).

## Appendix: Implementation Details

### Source Inventory

| Source ID | Date | Contents | Timeline role |
|---|---|---|---|
| `0b9e8647-ca47-48dc-9089-532600e91768` | 2026-05-18T03:31:33Z | Cycle 11 worker summary for plan-ledger namespace repair | Repaired `promise_check` failures before further Wave 3 work |
| `60693f48-7d7a-43e8-9ddc-d9048f53f167` | 2026-05-18T03:41:41Z | Cycle 12 researcher brief | Directed three-branch fan-out for Track 1, Track 3, and Atlas |
| `.long-exposure/fork-eec13528227c/clone-0/merge_report.md` | 2026-05-18 | Track 1 clone merge report | Documents M3.T1 instrument, outputs, and tests |
| `.long-exposure/fork-eec13528227c/clone-1/merge_report.md` | 2026-05-18 | Track 3 clone merge report | Documents M3.T3 statistic, outputs, and tests |
| `.long-exposure/fork-eec13528227c/clone-2/merge_report.md` | 2026-05-18 | Atlas clone merge report | Documents M3.A scaffold before post-merge Track 1/3 integration |
| `.long-exposure/fork-eec13528227c/fanout_merge.md` | 2026-05-18 | Three-branch merge summary | Confirms all required branch deliverables existed |
| `0b3756f0-b117-4880-8478-8f96258bfd2a` | 2026-05-18T04:09:07Z | Cycle 13 worker summary | Documents post-merge Atlas integration and checks |
| Provided audit report | 2026-05-18 | Post-merge integration audit summary | Confirms tests and validators after integration |

### Code Organization

| Area | Key files | Purpose |
|---|---|---|
| Plan/ledger repair | `plan_of_record.md`, `promise_ledger.jsonl` | Aligns milestone IDs and append-only events |
| Track 1 | `tracks/track1/instruments/build_tci.py`, `tracks/track1/reports/track1_reticulation_atlas.md`, `tracks/track1/outputs/*.tsv` | Builds and reports TCI instrument |
| Track 3 | `tracks/track3/scripts/convergence_pressure.py`, `tracks/track3/reports/track3_convergence_pressure.md`, `tracks/track3/data/convergence_*` | Builds and reports convergence-pressure statistic |
| Atlas | `botanical_atlas_site/build_atlas.py`, `index.html`, `app.js`, `style.css`, `coverage_summary.json`, `pages/*.json` | Static site generation and per-track adapters |
| Counter-claims | `tools/file_counter_claim.py`, `counter_claim_template.json` | Targeted correction payload validation |
| Tests | `tests/test_atlas_build.py`, `tracks/track1/tests/test_tci_instrument.py`, `tracks/track3/tests/test_convergence_pressure.py` | Contract and instrument checks |

### Test Results

| Check | Result |
|---|---|
| Cycle 11 `promise_check` after plan repair | exit 0 |
| Cycle 11 `org_check` | exit 0 with known warnings |
| Track 1 focused reticulation pytest set | 28 passed |
| Track 3 focused tests | 16 passed |
| Atlas scaffold tests in clone 2 | 10 passed |
| Post-merge Atlas + Track 1 + Track 3 tests | 20 passed |
| Barrier 2 conformance after post-merge integration | PASS |
| Barrier 1 substrate validation after post-merge integration | PASS: 363,237 nodes; 641,183 retained hyperedges |
| Post-merge `promise_check` | exit 0; warnings only |
| Post-merge `org_check` | exit 0; known root-layout warnings only |

### File Counts And Rows

| Artifact | Count |
|---|---:|
| `tracks/track1/outputs/tci_per_taxon.tsv` | 60,000 data rows |
| `tracks/track1/outputs/tci_hotspots_genus.tsv` | 14,292 data rows |
| `tracks/track1/outputs/canonical_recovery_report.tsv` | 12 data rows |
| `tracks/track3/data/convergence_predictions.tsv` | 16 data rows |
| `tracks/track3/data/convergence_pressure_scores.tsv` | 16 data rows |
| `tracks/track4/data/crop_substitution_candidates.tsv` | 3 data rows |
| `tracks/track6/data/probe_results.tsv` | 840 data rows |
| `botanical_atlas_site/pages/*.json` | 60,000 files |
| `prediction_ledger.tsv` | 0 data rows |
| `speculation_ledger.tsv` | 0 data rows |

### Cross-Reference Map

| Origin | Consuming artifact | Flow |
|---|---|---|
| `tracks/track1/instruments/build_tci.py` | `tracks/track1/outputs/tci_per_taxon.tsv` | Computes TCI rows from frozen substrate and Track 1 enrichment |
| `tracks/track1/outputs/tci_per_taxon.tsv` | `botanical_atlas_site/pages/*.json` | Exposed by the Atlas as Track 1 predicted/instrument rows |
| `tracks/track3/scripts/convergence_pressure.py` | `tracks/track3/data/convergence_predictions.tsv` | Emits Track 3 row classes for pending hypotheses and evidence summaries |
| `tracks/track3/data/convergence_predictions.tsv` | `botanical_atlas_site/pages/*.json` | Exposed by the Atlas as Track 3 predicted/enriched/observed/data-limited states |
| `tracks/track2`, `tracks/track4`, `tracks/track5`, `tracks/track6` track-local outputs | `botanical_atlas_site/coverage_summary.json` | Preserved by adapters during post-merge Track 1/3 integration |
| `tests/test_atlas_build.py` | `botanical_atlas_site/reports/atlas_barrier3_scaffold.md` | Tests the six fixed track sections, provenance, inferred flags, search rows, and counter-claim validation |
| `MANIFEST.md` | This report | Updated as the concise cycle 11-13 workspace snapshot while preserving the existing `## Key Files` section |
