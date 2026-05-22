---
title: "PhytoGraph — cycles 21-23"
date: "2026-05-18"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph — cycles 21-23

## Abstract

Cycles 21-23 were a post-closure reporting and reopen-triage window, not a new discovery wave. Cycle 21 produced and audited the Wave 5 final synthesis. Cycle 22 defined mechanical reopen gates for the closed H1, H4, H5, and H6 branches. Cycle 23 applied the first reopen test to Track 1 and found additional accepted-key reticulation evidence, but not enough to reopen H1.

The campaign claim boundary did not change. No master prediction or speculation rows were promoted. H1 remains data-limited, H2 remains not supported under controls, H3 remains data-limited, H4 remains data-limited, H5 remains not validated/source-biased, and H6 remains environment-limited/untested.

A supplied audit report for this reporter turn validates a Track 4 bioclim validation-readiness package. Its local metadata labels it as cycle 24, outside the requested cycle range, so this report treats it as supplied audit context rather than as ordinary cycle 21-23 timeline evidence.

## Introduction

PhytoGraph is a six-track campaign using a typed plant-biology hypergraph as a discovery instrument. Earlier waves built the substrate, Atlas surface, track-local instruments, validation packages, and ablation packages. By the start of cycle 21, the campaign had reached conservative closure: it had produced infrastructure and explicit falsification/data-limit records, but it had not met the original success criterion of at least one validated prediction per track.

Cycles 21-23 therefore focused on reporting and controlled reopen logic. A "reopen" means a previously closed or data-limited hypothesis can be reconsidered only if the missing evidence class is supplied with accepted join keys, enough coverage, and a falsification test. Reopen work does not change track status merely by changing thresholds, wording, or visualization.

## Approach

The report was assembled from local workspace artifacts, promise-ledger events, tests, and the supplied audit input. Full local transcripts for the supplied cycle session IDs were not available through local files or session-search tooling in this environment. This is a record gap, so the source of truth for the timeline is the artifact and ledger trail.

The primary sources were:

- Cycle 21 Wave 5 synthesis: `final_report.md`, `audit_report.md`, `research_contribution_ledger.md`, `artifact_index.md`, and `falsification_and_ablation_report.md`.
- Cycle 22 reopen gate: `reports/reopen/reopen_evidence_gate.md`, `data/reopen/reopen_branch_matrix.tsv`, and `tests/test_reopen_branch_matrix.py`.
- Cycle 23 Track 1 reopen package: `tracks/track1/reports/track1_reopen_reticulation_evidence.md`, candidate/diagnostic TSVs, figure, build/plot scripts, and focused test.
- Supplied Track 4 audit context: `tracks/track4/reports/track4_reopen_bioclim_validation_readiness.md`, its tables, figure, focused test, and audit report input.
- Master ledgers: `prediction_ledger.tsv`, `speculation_ledger.tsv`, and `promise_ledger.jsonl`.

## Findings

### Cycle 21: Wave 5 Final Synthesis Was Validated

Cycle 21 produced the Wave 5 final synthesis package. The worker event `9d8c3a33-7d40-4ddb-9f27-dc1969b8f4b2` recorded the package as in progress; the auditor event `e20f384c-52f8-4b20-b7a8-cec0dc07249d` validated it and superseded the worker event.

The final synthesis stated that PhytoGraph delivered a large typed substrate, Atlas integration, six track-specific instruments or scaffolds, and falsification/accounting artifacts, but did not meet the original research success criterion. The master ledgers remained header-only.

| Track | Cycle 21 status | Basis recorded in final synthesis |
|---|---|---|
| Track 1 Reticulation Atlas | Data-limited | Accepted-key/event-shaped reticulation recovery below threshold. |
| Track 2 Ghost Hyperedges | Not supported under controls | Held-out recovery produced 0 validated cases, 1 falsified under ablation, 6 data-limited, and 1 insufficient-support case. |
| Track 3 Convergence Pressure | Data-limited | Local priors existed, but not enough independent validation for master promotion. |
| Track 4 Domestication Hypergraph | Data-limited | Crop/CWR and climate-vector coverage insufficient for climate-substitution validation. |
| Track 5 Chemodiversity Predictor | Not validated/source-biased | Temporal recovery and no-Duke controls did not support promotion. |
| Track 6 Foundation Model Probe | Environment-limited/untested | Static benchmark existed, but no free/open/local model runtime and weights were available. |

The auditor reported no critical or moderate issues for the Wave 5 package. Residual warnings were inherited process and layout warnings and did not alter the scientific claim boundary.

### Cycle 22: Reopen Gates Were Defined, Not Executed

Cycle 22 created a controlled reopen framework for four closed branches: Track 1, Track 4, Track 5, and Track 6. The worker event `2bb5b0de-f011-4526-af59-4d1d257a5f3c` produced the gate package; auditor event `d77d0f3d-b5e4-4f78-b10e-034c6946de40` validated it.

The reopen gate did not acquire new data, rerun validation, change track status, or write to `prediction_ledger.tsv` or `speculation_ledger.tsv`. It defined the conditions under which a branch could later reopen.

| Track | Reopen condition | Priority |
|---|---|---|
| Track 1 | Event-shaped reticulation evidence joins to accepted keys and clears canonical recovery plus confound controls. | High |
| Track 4 | Observed crop/CWR bioclim vectors and held-out expert comparison rows exist before any climate-substitution language. | High |
| Track 5 | Non-Duke, temporally resolved chemistry rows survive accepted-key joins and source-density controls. | Medium-high |
| Track 6 | A free/open/local model runtime and weights produce audited response rows for the static benchmark. | Medium |

The gate’s central decision was conservative: a branch that only changes scoring, thresholds, wording, or visualization remains closed. Reopening requires a named evidence class, accepted join key, minimum coverage, and a first validation or falsification test.

### Cycle 23: Track 1 Added Evidence But Did Not Reopen H1

Cycle 23 applied the reopen gate to Track 1. The worker event `1fb1fd2c-5c1f-4c9d-a18d-9030a2b32633` produced the evidence package; auditor event `26a6a796-e04c-4d18-a74e-92110f6c266d` validated the determination.

The result was `evidence_added_but_threshold_not_met`.

The branch inspected local/open evidence from three source categories: the Barrier 4 frozen Track 1 accepted subset, CCDB chromosome-count seed rows, and Wood et al. 2009 polyploid speciation evidence joined through the cached WFO path [4], [28], [30]. It retained 18 inspected candidate rows. Six rows were accepted-key, event-shaped rows across three accepted-key taxa:

- `Triticum aestivum`: `polyploidization_event` and `reticulate_inheritance_evidence`.
- `Brassica napus`: `polyploidization_event` and `reticulate_inheritance_evidence`.
- `Spartina anglica`, rescued to `Sporobolus anglicus`: `hybridization_event` and `reticulate_inheritance_evidence`.

Five CCDB rows joined to accepted keys, but they were chromosome-count context only and did not count as event-shaped reopen evidence. Four event-shaped rows for `Tragopogon mirus` and `Tragopogon miscellus` were rejected because no accepted WFO key was recovered in the available local lookup.

![Accepted-key and event-shaped recovery for Track 1 reopen candidate sources compared with the Barrier 4 closure baseline.](tracks/track1/figures/reticulation_reopen_join_recovery.png)

The reopen threshold was not met for three recorded reasons:

- Coverage was too narrow: 6 accepted-key event-shaped rows across 3 taxa, below the broader threshold needed for reopening.
- Exact accepted-name recovery remained below threshold: only 2 event taxa joined by exact accepted name; one relied on synonym rescue.
- Source-density control failed: all accepted-key event-shaped rows came from a single Wood 2009 synthesis source.

No tree-compatibility index rerun occurred, and no new taxonomy, hybridization, biological reticulation, prediction-ledger, or speculation-ledger claim was promoted.

### Supplied Track 4 Audit Context: H4 Still Did Not Reopen

The supplied audit report for this reporter turn validates a Track 4 reopen package, but the local artifact metadata and promise-ledger events label it as cycle 24. Because the requested range is cycles 21-23, this report records it as supplied context and a cycle-label gap.

The supplied audit decision was `VALIDATED`. It supported the worker determination `no_new_qualifying_evidence`.

The Track 4 package inspected existing local Track 4 and M1.6 domestication artifacts for accepted-key crop/CWR climate vectors and held-out expert-comparison readiness. It found:

| Evidence class | Count |
|---|---:|
| Climate staging rows | 375 |
| Accepted-key climate joins | 36 |
| Numeric BIOCLIM vector rows | 0 |
| Crop/CWR pair rows | 69 |
| Fully joined crop/CWR pairs | 3 |
| Held-out expert crop rows | 22 |
| Accepted-key held-out joins | 2 |
| Validation-allowed candidate-level held-out pairs | 0 |

![Accepted-key crop/CWR coverage for observed bioclim vectors and held-out expert-comparison rows, with rejected rows by reason.](tracks/track4/figures/track4_reopen_bioclim_coverage.png)

The decisive blocker was that no accepted-key crop/CWR rows had observed or defensibly range-derived numeric BIOCLIM vectors. The held-out expert rows were crop-level only, not candidate-level comparator rows. Same-genus and crop-popularity controls therefore remained unresolved because the only candidate rows were training-derived common-crop/same-genus rows.

The supplied audit confirmed that the Crop Substitution Engine was not rerun and that no climate-substitution recommendation, prediction-ledger row, speculation-ledger row, or crop-suitability claim was promoted.

### Per-Track Novelty And Status In This Window

| Track | New in cycles 21-23 | Merely integrated or carried forward | Speculative or unresolved |
|---|---|---|---|
| Track 1 | Cycle 23 added a tested accepted-key reticulation reopen evidence inventory. | Barrier 4 sidecar recovery and prior H1 closure were carried forward. | H1 remains data-limited; event-shaped evidence is too narrow and source-dominated. |
| Track 2 | No new Track 2 experiment in this window. | Wave 5 carried forward the Wave 4 null/falsification outcome. | No promoted ghost-hyperedge prediction. |
| Track 3 | No new Track 3 experiment in this window. | Wave 5 carried forward local convergence-prior rows and data-limited status. | No master convergence prediction. |
| Track 4 | Reopen criteria were defined in cycle 22; supplied audit context validates a later bioclim readiness non-reopen result. | Prior Track 4 data-limited closure was carried forward. | H4 remains data-limited; climate vectors and validation comparator pairs are missing. |
| Track 5 | Reopen criteria were defined in cycle 22. | Wave 5 carried forward Duke/source-bias and temporal-validation failures. | H5 remains not validated/source-biased. |
| Track 6 | Reopen criteria were defined in cycle 22. | Static benchmark/environment-limited closure was carried forward. | H6 remains untested until a free/open/local model runtime and weights exist. |

## Discussion

Cycles 21-23 narrowed the campaign’s next-action space rather than expanding its claims. Cycle 21 closed the main campaign honestly: the infrastructure exists, but validated predictions did not clear the original success criterion. Cycle 22 converted vague "try again" paths into explicit evidence gates. Cycle 23 tested the highest-priority gate and showed why Track 1 still should not reopen.

The practical effect is that future work now has sharper entry conditions. Track 1 needs broader, independently sourced, accepted-key, event-shaped reticulation evidence. Track 4 needs occurrence-backed crop/CWR coordinates, computed BIOCLIM summaries, and candidate-level expert comparator rows disjoint from training evidence. Track 5 needs non-Duke, temporally resolved phytochemical assertions that survive source-density and screening-count controls. Track 6 needs a runnable free/open/local model runtime with local weights and audited response rows.

The master ledger boundary stayed intact. The campaign did not convert local priors, source-biased signals, missing-data diagnostics, or deterministic controls into validated predictions.

## Open Questions

1. Can Track 1 obtain at least 30 additional accepted-key reticulation event rows from independent open/local sources, enough to run source-density and family-size controls?
2. Can Track 4 compute accepted-key crop and wild-relative BIOCLIM summaries from occurrence-backed coordinates with usable provenance and licenses?
3. Can Track 5 break Duke source dominance with temporally resolved non-Duke chemistry records across enough families?
4. Can Track 6 run any suitable free/open/local model in the workspace without paid, remote, or key-gated providers?
5. Should future reporting treat the supplied Track 4 audit as cycle 24, or should the cycle/session mapping be corrected upstream?

## References

[4] The World Flora Online Consortium et al., "World Flora Online Plant List December 2025," Zenodo, 2025. https://doi.org/10.5281/zenodo.18007552 (accessed 2026-05-17).

[28] Anna Rice, Lior Glick, Shiran Abadi, et al., "The Chromosome Counts Database (CCDB) — a community resource of plant chromosome numbers," New Phytologist, 2015. https://doi.org/10.1111/nph.13191 (accessed 2026-05-17).

[30] Troy E. Wood, Naoki Takebayashi, Michael S. Barker, et al., "The frequency of polyploid speciation in vascular plants," Proceedings of the National Academy of Sciences, 2009. https://doi.org/10.1073/pnas.0811575106 (accessed 2026-05-17).

## Appendix: Implementation Details

### Source Inventory

| Source ID | Date | Contents | Timeline role |
|---|---|---|---|
| `9d8c3a33-7d40-4ddb-9f27-dc1969b8f4b2` | 2026-05-18 | Cycle 21 worker event for Wave 5 final synthesis. | Produced final synthesis package pending audit. |
| `e20f384c-52f8-4b20-b7a8-cec0dc07249d` | 2026-05-18 | Cycle 21 auditor event for Wave 5 final synthesis. | Validated final synthesis and superseded worker event. |
| `final_report.md` | 2026-05-18 | Final PhytoGraph synthesis. | Main cycle 21 report artifact. |
| `audit_report.md` | 2026-05-18 | Wave 5 audit report. | Main cycle 21 audit artifact. |
| `2bb5b0de-f011-4526-af59-4d1d257a5f3c` | 2026-05-18 | Cycle 22 worker event for reopen gate. | Produced reopen threshold package. |
| `d77d0f3d-b5e4-4f78-b10e-034c6946de40` | 2026-05-18 | Cycle 22 auditor event for reopen gate. | Validated reopen gate and unchanged statuses. |
| `reports/reopen/reopen_evidence_gate.md` | 2026-05-18 | Human-readable reopen criteria. | Defines post-closure branch rules. |
| `data/reopen/reopen_branch_matrix.tsv` | 2026-05-18 | Machine-readable reopen matrix. | Defines missing evidence, join keys, thresholds, tests, risks, and priorities. |
| `1fb1fd2c-5c1f-4c9d-a18d-9030a2b32633` | 2026-05-18 | Cycle 23 worker event for Track 1 reopen evidence. | Produced Track 1 evidence package. |
| `26a6a796-e04c-4d18-a74e-92110f6c266d` | 2026-05-18 | Cycle 23 auditor event for Track 1 reopen evidence. | Validated threshold-not-met determination. |
| `tracks/track1/reports/track1_reopen_reticulation_evidence.md` | 2026-05-18 | Track 1 reopen report. | Main cycle 23 technical report. |
| Supplied audit report | 2026-05-18 | Track 4 bioclim validation-readiness audit. | Supplied context; local metadata labels it cycle 24, outside requested range. |

### Code Organization

| File | Lines | Purpose |
|---|---:|---|
| `tests/test_reopen_branch_matrix.py` | 85 | Checks reopen matrix columns, track coverage, allowed statuses/priorities, evidence/test fields, and header-only ledgers. |
| `tracks/track1/scripts/build_reopen_reticulation_evidence.py` | 216 | Builds Track 1 candidate event and join diagnostic tables. |
| `tracks/track1/scripts/plot_reticulation_reopen_join_recovery.py` | 48 | Generates the Track 1 reopen recovery figure. |
| `tests/test_track1_reopen_reticulation_evidence.py` | 118 | Tests Track 1 reopen schema, caveats, event counts, threshold statement, figure, and ledger non-promotion. |
| `tracks/track4/scripts/build_reopen_bioclim_validation.py` | 255 | Builds Track 4 bioclim vector-attempt, validation-pair, and diagnostic tables. |
| `tracks/track4/scripts/plot_reopen_bioclim_coverage.py` | 67 | Generates the Track 4 bioclim readiness figure. |
| `tests/test_track4_reopen_bioclim_validation.py` | 125 | Tests Track 4 reopen schema, nonqualifying vectors, held-out non-leakage, diagnostics, figure, and ledger non-promotion. |

### Data And Report Artifacts

| Artifact | Rows / lines | Role |
|---|---:|---|
| `reports/reopen/reopen_evidence_gate.md` | 113 lines | Cycle 22 reopen gate report. |
| `data/reopen/reopen_branch_matrix.tsv` | 4 data rows | Reopen thresholds for Track 1/4/5/6. |
| `tracks/track1/reports/track1_reopen_reticulation_evidence.md` | 51 lines | Cycle 23 Track 1 reopen report. |
| `tracks/track1/data/reticulation_reopen_candidate_events.tsv` | 18 data rows | Track 1 inspected candidate evidence rows. |
| `tracks/track1/data/reticulation_reopen_join_diagnostics.tsv` | 3 data rows | Track 1 source-level diagnostics. |
| `tracks/track4/reports/track4_reopen_bioclim_validation_readiness.md` | 55 lines | Supplied Track 4 audit-context report. |
| `tracks/track4/data/crop_cwr_bioclim_vectors.tsv` | 10 data rows | Track 4 nonqualifying bioclim vector attempts. |
| `tracks/track4/data/crop_cwr_validation_pairs.tsv` | 22 data rows | Track 4 held-out crop rows, none validation-allowed. |
| `tracks/track4/data/track4_reopen_join_diagnostics.tsv` | 4 data rows | Track 4 diagnostic counts. |
| `prediction_ledger.tsv` | 0 data rows | Header-only master prediction ledger. |
| `speculation_ledger.tsv` | 0 data rows | Header-only master speculation ledger. |
| `promise_ledger.jsonl` | 196 lines at scan time | Append-only ledger through supplied Track 4 audit event. |

### Test Results

Recorded validation results in the source trail:

| Test or validator | Result | Source |
|---|---|---|
| `tests/test_reopen_branch_matrix.py` | 5 passed | Cycle 22 audit ledger event. |
| Track 1 focused pytest | Passed | Cycle 23 worker/auditor ledger events. |
| `python3 -m pytest -q tests/test_track4_reopen_bioclim_validation.py` | 5 passed in 0.59s | Supplied audit report. |
| `promise_check` | Exit 0 with inherited warnings | Cycle 22, cycle 23, and supplied Track 4 audit records. |
| `org_check` | Exit 0 with inherited root-layout warnings | Cycle 22, cycle 23, and supplied Track 4 audit records. |

### Cross-Reference Map

| Origin | Consumer | Flow |
|---|---|---|
| Cycle 21 final synthesis | Cycle 22 reopen gate | The conservative closure established which hypotheses needed explicit reopen conditions. |
| Cycle 22 reopen matrix | Cycle 23 Track 1 reopen package | Track 1 was selected as high priority and tested against accepted-key/event-shaped evidence requirements. |
| Track 1 candidate event table | Track 1 reopen report and test | Candidate rows supported the threshold-not-met determination. |
| Track 4 reopen tables | Supplied audit report | Tables supported `no_new_qualifying_evidence` and continued H4 data-limited status. |
| Master ledgers | All cycle 21-23 reports and tests | Header-only ledgers enforced the no-promotion boundary. |

### Record Gaps

Full local transcripts for the supplied cycle session IDs were not found in the workspace. The report therefore relies on artifact, ledger, and audit records.

The supplied audit report validates a Track 4 package whose local metadata labels it as cycle 24, while the requested report range is cycles 21-23. This report includes it as supplied context because it was provided as input, but does not treat it as ordinary cycle 21-23 chronology.

### Manifest Update

`MANIFEST.md` was updated for `report_cycles_21-23`. The existing `## Key Files` section was preserved verbatim, and the mutable sections were replaced with the current script inventory, artifact inventory, cumulative stats, and cross-reference map for this reporting window.

### Coherence Review

The report was checked once for flow and self-containment. It defines the reopen concept before using it, states the transcript and cycle-label gaps explicitly, and keeps the supplied Track 4 audit context separate from the requested cycle 21-23 timeline.
