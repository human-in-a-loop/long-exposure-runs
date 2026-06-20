---
title: "PhytoGraph — cycles 18-20"
date: "2026-05-18"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph — cycles 18-20

## Abstract

Cycles 18-20 moved PhytoGraph from post-merge recovery into conservative campaign closure. The work did not validate the original success criterion of one validated prediction per track. Instead, it reconciled the remaining Barrier 4 track statuses, preserved negative and data-limited outcomes, and kept unsupported predictions out of the master ledgers.

The cycle range has three layers of source material. First, `reports/cycles/report_cycles_17-19.md` records the inherited fork `cc044bf40be3` integration for Track 2, Track 3, and Track 5. Second, cycle 20 artifacts reconcile Track 1, Track 4, and Track 6 closure work from fork `0b556d9370a2`. Third, the supplied audit report validates the Wave 5 synthesis package as a conservative final accounting.

The final status is: H1 data-limited, H2 not supported under controls, H3 data-limited, H4 data-limited, H5 not validated/source-biased, and H6 environment-limited/untested. The master `prediction_ledger.tsv` and `speculation_ledger.tsv` remain header-only.

## Introduction

PhytoGraph is a typed plant-biology hypergraph campaign with six tracks: reticulation, ghost coevolutionary partners, convergence, domestication, chemodiversity, and botanical foundation-model probing. A hypergraph here means a data structure where one relationship can connect more than two typed nodes, such as a crop pedigree connecting multiple wild ancestors, a cultivar, traits, geography, and time.

A “Barrier” is a synchronization point. Barrier 4 is the point where per-track validation, ablation, and falsification results are reconciled into master-level prediction status. A “master ledger” is the campaign-wide file where a row becomes a cross-track prediction or speculation. Track-local rows can be useful evidence, but they do not become campaign predictions until the master ledger admits them.

Cycles 18-20 should be read as a closure window, not a discovery window. The live recovery addendum instructed the run to continue from `reports/cycles/report_cycles_17-19.md` and post-merge artifacts for fork `cc044bf40be3`, to avoid repeating null work, and to close unresolved tracks conservatively.

A record gap remains: the input lists session IDs for Cycle 18, Cycle 19, and Cycle 20, but full local transcripts for those IDs were not available through the tools in this environment. This report therefore relies on workspace artifacts, ledger events, the prior periodic report, and the supplied audit report.

## Approach

The recovery work followed a narrow rule: reconcile what had already been built and validated, without promoting track-local hypotheses beyond their evidence.

The sequence was:

1. The inherited `cc044bf40be3` integration carried Track 2, Track 3, and Track 5 Wave 4 outputs into the root workspace.
2. Cycle 20 integrated Track 1, Track 4, and Track 6 closure/refinement outputs from fork `0b556d9370a2`.
3. Wave 5 synthesis assembled the final root artifacts: `final_report.md`, `audit_report.md`, `research_contribution_ledger.md`, `artifact_index.md`, and `falsification_and_ablation_report.md`.
4. The supplied audit report validated that synthesis and confirmed that no unsupported biological, crop-substitution, phytochemical, or model-performance claim was promoted.

No new source ingestion, biological inference, model run, or master prediction promotion is reported for this cycle range.

## Findings

### Barrier 4 Reconciliation Completed

Cycle 20 produced `reports/barrier4_closure_integration.md`, which reconciles Track 1, Track 4, and Track 6 closure outputs. The integration decision is explicit: all three outputs are closure evidence, not validated master predictions.

| Track | Hypothesis | Cycle 20 status | Evidence basis | Master-ledger action |
|---|---|---|---|---|
| Track 1 Reticulation Atlas | H1 | Data-limited | Sidecar full-WFO recovery improved accepted-key diagnosis, but event-shaped recovery remained below validation threshold. | No promotion. |
| Track 4 Domestication Hypergraph | H4 | Data-limited | Observed bioclim vectors were absent, so climate matching was undefined. | No promotion. |
| Track 6 Foundation Model Probe | H6 | Environment-limited / untested | Static benchmark and deterministic controls existed, but no free/open/local model runtime or local weights were available. | No promotion. |

An “accepted key” is the normalized taxon identifier used by the frozen PhytoGraph substrate. Without accepted-key recovery, a track-local biological row cannot reliably join to the campaign-wide substrate.

### Track 1: Reticulation Closure

Track 1 asked whether the reticulation instrument could recover canonical polyploid or hybrid lineages. The closure script `tracks/track1/scripts/track1_barrier4_key_recovery.py` ran a sidecar recovery probe against the cached full WFO Plant List dump [4]. It did not mutate the frozen substrate or master ledgers.

The result refined the blocker:

| Measure | Result |
|---|---:|
| Canonical seeds tested | 8 |
| Current accepted-key recoveries | 0 |
| Full-WFO sidecar accepted-key recoveries | 5 |
| Event-shaped recoveries with synonym rescue | 3 |
| Event-shaped exact accepted-taxon recoveries | 2 |
| Validation threshold stated by closure report | at least 5 event-shaped canonical recoveries |

The Track 1 result is therefore data-limited. The sidecar showed that some failure came from frozen-subset truncation and name-status mismatch, but it did not supply enough accepted-key, event-shaped hybridization or polyploidization evidence to validate H1.

### Track 4: Domestication Closure

Track 4 asked whether crop-wild-relative and climate evidence could support bounded crop-substitution analysis. The closure report states that climate substitution was not computable.

| Evidence axis | Current state |
|---|---:|
| Retained Track 4 observed hyperedges | 6 |
| Retained crop-pedigree edges | 2 / 43 staged |
| Joined crop-wild-relative pairs | 3 / 69 staged |
| Held-out validation rows with accepted keys | 2 / 22 |
| Climate-envelope rows with accepted keys | 36 / 375 |
| Observed bioclim vectors | 0 / 375 |
| Candidate rows emitted | 3 |
| Climate claims emitted | 0 |

The three candidate rows are local non-climate priors only: *Arachis hypogaea* with *Arachis duranensis*, *Arachis hypogaea* with *Arachis ipaensis*, and *Avena sativa* with *Avena sterilis*. They remain `pending_data_limited`. The report explicitly forbids describing them as climate matches, crop-substitution recommendations, validated predictions, or deployment advice.

### Track 6: Foundation-Model Probe Closure

Track 6 closed as benchmark-only and environment-limited. The static benchmark contains 210 questions across 7 categories, and the deterministic scorer produced 840 control result rows. These rows test the harness, not a foundation model.

The local availability file records:

| Runtime requirement | Observed value |
|---|---|
| `local_open_model_runnable` | false |
| `transformers` | false |
| `torch` | false |
| `llama_cpp` | false |
| local model files | 0 |

The deterministic controls behaved as infrastructure checks: the scoped positive control passed 210/210, the empty-response and forbidden-overclaim controls passed 0/210, and the verbatim expected-answer diagnostic passed 90/210. That last diagnostic documents a lexical scorer limitation: the scorer can mistake a negated discussion of a forbidden phrase for an overclaim.

No model error rate, leaderboard, toxicity-look-alike policy claim, or vendor/model-family comparison is supported.

### Track 2/3/5 Status Carried Forward

The inherited Track 2, Track 3, and Track 5 package remains part of the cycles 18-20 continuity because the live recovery addendum made `report_cycles_17-19.md` the last substantive state.

| Track | Status carried forward | Evidence basis |
|---|---|---|
| Track 2 Ghost Hyperedges | H2 not supported under controls | 0 validated held-outs, 1 falsified under ablation, 6 data-limited, 1 insufficient-support. |
| Track 3 Convergence Pressure | H3 data-limited | `drupe` and `capsule` remained local pending convergence-prior rows; no master-ledger promotion. |
| Track 5 Chemodiversity Predictor | H5 not validated / source-biased | 0 top-decile temporal recoveries; removing Dr. Duke evidence collapsed prediction rows to 0 [38]. |

Track 2’s result is a null validation result, not evidence that the biological anachronism hypotheses are false. Track 3’s candidate rows are statistical priors, not adaptive-convergence claims. Track 5’s strongest current result is the source-bias ablation: the present instrument measures a Duke-backed screening prior rather than source-independent chemodiversity neighborhood completion.

### Wave 5 Audit Validated Conservative Closure

The supplied audit report records the final decision as `VALIDATED`. It states that Wave 5 synthesis correctly closed the campaign as conservative final synthesis rather than over-promoting track-local priors.

The audit checked:

| Check | Result |
|---|---|
| Wave 4 / Barrier 4 tests | 8 passed |
| Barrier 3 Atlas validator | PASS, 60,000 pages, 6 tracks |
| Barrier 2 enrichment validator | PASS, 6 tracks checked |
| Barrier 1 substrate validator | PASS, 363,237 nodes, 641,183 retained hyperedges |
| `promise_check` | exit 0, inherited warnings only |
| `org_check` | exit 0, inherited warnings only |
| `prediction_ledger.tsv` | header-only |
| `speculation_ledger.tsv` | header-only |

The audit also confirms that the original validated-prediction-per-track criterion was not met.

## Discussion

Cycles 18-20 converted the remaining recovery work into a campaign-level claim boundary. The boundary is simple: PhytoGraph produced a large typed substrate, Atlas integration, track-local instruments or scaffolds, validation/ablation machinery, and explicit closure records, but it did not produce validated predictions across all six tracks.

The durable contribution in this window is procedural and diagnostic:

- Track 1’s accepted-key recovery blocker is now more precise.
- Track 4’s climate-substitution claim is blocked for a concrete reason: no observed bioclim vectors.
- Track 6’s model-probe execution is blocked by local runtime and weight absence, not by question-set absence.
- Track 2 and Track 5 preserve negative/source-biased validation outcomes.
- Track 3 preserves pending priors without turning them into biological claims.
- The master ledgers remain empty by design.

This is consistent with the campaign guardrail that predictions are predictions, not facts, and unsupported claims must not be promoted.

## Open Questions

1. Full session transcripts for the supplied cycle session IDs were not available locally. The report therefore cannot narrate researcher/worker/auditor conversations beyond what their artifacts and ledger events record.

2. Track 1 can only reopen with a substrate revision or approved sidecar that supplies accepted-key, event-shaped reticulation evidence at validation scale.

3. Track 4 can only reopen after crop and wild-relative occurrence coordinates, WorldClim/CHELSA bioclim vectors, joined held-out expert rows, and climate-aware baselines exist.

4. Track 5 can only reopen with temporally resolved non-Duke phytochemical or ethnobotanical evidence and screening-intensity controls that preserve a signal.

5. Track 6 can only execute H6 with free/open/local model runtime and weights plus audited response rows. The current benchmark is ready, but untested against real models.

## References

[4] The World Flora Online Consortium et al., "World Flora Online Plant List December 2025," Zenodo, 2025. https://doi.org/10.5281/zenodo.18007552 (accessed 2026-05-17).

[38] James A. Duke, "Dr. Duke's Phytochemical and Ethnobotanical Databases," Ag Data Commons, 2023. https://agdatacommons.nal.usda.gov/articles/dataset/Dr_Duke_s_Phytochemical_and_Ethnobotanical_Databases/24660351 (accessed 2026-05-17).

## Appendix: Implementation Details

### Source Inventory

| Source ID | Date | Contents | Role in timeline |
|---|---|---|---|
| `037ab180-dc31-4e6c-b69f-d09fcb02d36c` | Cycle 18, supplied input | Researcher session ID listed in `cycle_sessions`; full transcript not available locally. | Record gap for cycle 18. |
| `e2b0e844-320e-4964-ac1b-df40d81efd24` | Cycle 19, supplied input | Worker session ID listed in `cycle_sessions`; full transcript not available locally. | Record gap for cycle 19. |
| `e634e204-bb3c-4f65-92b8-032008e59406` | Cycle 20, supplied input | Researcher session ID listed in `cycle_sessions`; full transcript not available locally. | Record gap for cycle 20 planning context. |
| `75fdfeb6-e134-4264-aed9-aa99a4848f33` | Cycle 20, supplied input | Worker session ID listed in `cycle_sessions`; represented by Barrier 4 closure artifacts in workspace. | Cycle 20 implementation context. |
| `906f451d-916b-4ff8-ac57-f7c2c73fb1a7` | Cycle 20, supplied input | Auditor session ID listed in `cycle_sessions`; supplied audit report validates final synthesis. | Audit trail for closure. |
| `reports/cycles/report_cycles_17-19.md` | 2026-05-18 | Prior periodic report for fork `cc044bf40be3` Track 2/3/5 integration. | Last substantive state named by live recovery addendum. |
| `reports/wave4_postmerge_integration.md` | 2026-05-18T11:00:00+00:00 | Root integration of Track 2/3/5 Wave 4 outputs. | Carries H2, H3, and H5 status forward. |
| `tracks/track1/reports/track1_barrier4_closure.md` | 2026-05-18T12:05:00+00:00 | Track 1 accepted-key sidecar recovery and H1 closure. | Refines Track 1 blocker. |
| `tracks/track4/reports/track4_barrier4_closure.md` | 2026-05-18T10:15:00Z | Track 4 data-limited climate-substitution closure. | Closes H4 without recommendation claims. |
| `tracks/track6/reports/track6_barrier4_closure.md` | 2026-05-18T13:29:31+00:00 | Track 6 benchmark-only/environment-limited closure. | Closes H6 execution as environment-limited. |
| `reports/barrier4_closure_integration.md` | 2026-05-18T14:05:00+00:00 | Master-level Track 1/4/6 Barrier 4 integration. | Consolidates remaining closure statuses. |
| `final_report.md` | 2026-05-18T14:45:00+00:00 | Wave 5 final synthesis. | Campaign-level closure narrative. |
| `audit_report` input / event `e20f384c-52f8-4b20-b7a8-cec0dc07249d` | 2026-05-18T15:05:00+00:00 | Auditor validation of Wave 5 synthesis. | Final validation source for this report. |

### Code Organization

| File | Lines | Purpose |
|---|---:|---|
| `tracks/track1/scripts/track1_barrier4_key_recovery.py` | 303 | Sidecar WFO accepted-key recovery probe for Track 1 canonical seeds. |
| `tests/test_barrier4_closure_integration.py` | 85 | Verifies Track 1/4/6 closure counts and header-only master ledgers. |
| `tracks/track6/scripts/run_offline_probe.py` | 379 | Refreshes Track 6 benchmark/control outputs without model inference. |
| `tracks/track6/scripts/score_offline_probe.py` | 71 | Deterministic lexical scorer for Track 6 controls. |
| `tests/test_wave4_postmerge_integration.py` | 74 | Verifies Track 2/3/5 post-merge integration boundaries. |
| `tracks/track2/scripts/track2_wave4_validation_closure.py` | 321 | Produces Track 2 held-out validation closure. |
| `tracks/track3/scripts/validate_wave4_convergence.py` | 378 | Produces Track 3 convergence/confound interpretation. |
| `tracks/track5/scripts/build_wave4_temporal_source_closure.py` | 208 | Produces Track 5 temporal/source-ablation closure. |

### Data And Report Artifacts

| Artifact | Rows / Lines | Role |
|---|---:|---|
| `tracks/track1/data/barrier4_canonical_key_recovery.tsv` | 8 data rows | Canonical seed recovery matrix for H1. |
| `tracks/track1/data/barrier4_rescued_reticulation_edges.tsv` | 14 data rows | Sidecar rescued reticulation edges. |
| `tracks/track4/data/crop_substitution_candidates.tsv` | 3 data rows | Local Track 4 candidate priors, all data-limited. |
| `tracks/track6/data/probe_results.tsv` | 840 data rows | Deterministic Track 6 control results. |
| `tracks/track6/data/local_model_availability.json` | 13 lines | Records absent local model runtime and weights. |
| `tracks/track2/data/track2_wave4_validation_outcomes.tsv` | 8 data rows | Track 2 held-out outcomes. |
| `tracks/track3/data/track3_wave4_validation_outcomes.tsv` | 16 data rows | Track 3 trait outcomes. |
| `tracks/track5/data/track5_wave4_validation_outcomes.tsv` | 13 data rows | Track 5 temporal/source outcomes. |
| `prediction_ledger.tsv` | 0 data rows | Master prediction ledger remains header-only. |
| `speculation_ledger.tsv` | 0 data rows | Master speculation ledger remains header-only. |

### Test Results

The supplied audit report records:

```text
Wave 4 / Barrier 4 tests: 8 passed
Barrier 3 Atlas validator: PASS, 60000 pages, 6 tracks
Barrier 2 enrichment validator: PASS, 6 tracks checked
Barrier 1 substrate validator: PASS, 363237 nodes, 641183 retained hyperedges
promise_check: exit 0, inherited warnings only
org_check: exit 0, inherited warnings only
```

### Cross-Reference Map

| Origin | Consuming artifact | Flow |
|---|---|---|
| Fork `cc044bf40be3` Track 2/3/5 outputs | `reports/wave4_postmerge_integration.md` | Carries H2, H3, and H5 local validation/ablation results into root workspace. |
| Fork `0b556d9370a2` Track 1 output | `reports/barrier4_closure_integration.md` | Converts accepted-key sidecar probe into H1 data-limited closure. |
| Fork `0b556d9370a2` Track 4 output | `reports/barrier4_closure_integration.md` | Converts absent observed bioclim vectors into H4 data-limited closure. |
| Fork `0b556d9370a2` Track 6 output | `reports/barrier4_closure_integration.md` | Converts benchmark-only state into H6 environment-limited closure. |
| Wave 5 worker event `9d8c3a33-7d40-4ddb-9f27-dc1969b8f4b2` | Auditor event `e20f384c-52f8-4b20-b7a8-cec0dc07249d` | Auditor supersedes worker in-progress synthesis with validated final synthesis. |
| Track-local ledgers and outcome tables | `prediction_ledger.tsv`, `speculation_ledger.tsv` | No rows promoted; master ledgers remain header-only. |

### Manifest Update

`MANIFEST.md` was updated for `report_cycles_18-20`. The existing `## Key Files` section was preserved verbatim, and the surrounding snapshot now records the cycle 18-20 source inventory, script inventory, file counts, cross-references, and master-ledger status.

### Coherence Review

The report passed one coherence review pass. Terms needed by a fresh reader are defined in the introduction, gaps in the session record are stated explicitly, and every track conclusion is tied to a source artifact or supplied audit statement.
