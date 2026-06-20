---
title: "PhytoGraph — cycles 30-32"
date: "2026-05-18"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph — cycles 30-32

## Abstract

Cycles 30-32 were a Barrier 4 closure-strengthening window, not a new discovery or prediction-promotion window. The work refined three existing blockers:

- Track 1 tested whether the GBIF accepted-key reticulation sidecar from cycle 29 could become control-supported. It could not: the retained event sidecar remained fixed at 22 event taxa and 23 event-shaped rows, but source-density and GBIF/WFO-resolution controls failed.
- Track 2 tested whether free-tier/local repair could recover canonical ghost-hyperedge held-outs under the existing validation contract. It could not: 0 of 8 canonical held-outs passed.
- Track 3 built an accepted-key trait/confound matrix for canonical convergence traits. It found 3,069 accepted-key trait carrier rows across 15 traits, but 0 traits satisfied controlled convergence-readiness.

The post-merge integration for fork `2f05eabe3800` reconciled Track 2 and Track 3 without changing branch science outputs. The master `prediction_ledger.tsv` and `speculation_ledger.tsv` remained header-only. No schema change, substrate mutation, predictor rerun, Atlas change, model execution, biological novelty claim, anachronism claim, convergence validation claim, or reticulation validation claim was promoted.

## Introduction

PhytoGraph is a typed plant-biology hypergraph campaign organized around six prediction tracks. In this report, the relevant tracks are:

- Track 1, Reticulation Atlas: tests whether polyploidy, hybridization, and related reticulate inheritance evidence can support a computable tree-compatibility or reticulation signal.
- Track 2, Ghost Hyperedges: tests whether candidate extinct coevolutionary partnerships can be recovered under explicit evidence gates.
- Track 3, Convergence Pressure: tests whether repeated plant traits can be ranked as controlled convergence candidates rather than artifacts of family size, source coverage, or sampling density.

Cycles 30-32 followed the cycle 29 Track 1 namespace reconciliation, which had preserved a GBIF accepted-key sidecar but did not reopen WFO-based Track 1 validation. The cycle 30-32 work asked whether remaining control gaps could be narrowed enough to change any Barrier 4 status. The answer across the window was no: each package sharpened the blocker diagnosis and preserved the no-promotion boundary.

## Approach

The report was assembled from local workspace artifacts, the supplied post-merge audit report, promise-ledger records, fork merge reports, tests, figures, and data files. Full session-fetch tools for the listed session IDs were not available in this environment, so the report treats the session IDs as traceability handles and relies on the generated artifacts for content.

Key local sources were:

- Cycle 30 Track 1 control strengthening: `tracks/track1/reports/track1_free_tier_control_strengthening.md`
- Cycle 30 Track 3 trait/confound matrix: `tracks/track3/reports/track3_free_tier_trait_confound_matrix.md`
- Cycle 31 Track 2 ghost evidence controls: `tracks/track2/reports/track2_free_tier_ghost_evidence_controls.md`
- Fork integration: `reports/fork_2f05eabe3800_postmerge_integration.md`
- Fork merge records: `.long-exposure/fork-2f05eabe3800/clone-0/merge_report.md`, `.long-exposure/fork-2f05eabe3800/clone-1/merge_report.md`, and `.long-exposure/fork-2f05eabe3800/fanout_merge.md`
- Master ledgers: `prediction_ledger.tsv`, `speculation_ledger.tsv`, and `promise_ledger.jsonl`

## Findings

### Cycle 30: Track 1 Control Strengthening Did Not Upgrade The GBIF Sidecar

Cycle 30 tested whether the Track 1 GBIF sidecar could move from readiness-only evidence toward control-supported readiness. A sidecar is evidence retained outside the frozen WFO-oriented master substrate because it is useful diagnostically but not admissible for master promotion.

The branch kept the cycle 29 sidecar fixed: 22 retained GBIF accepted-key event taxa and 23 retained event-shaped rows. It then compared those cases against 17 existing matched controls. The controls were near the cases by genus or family: 16 were genus-near and 1 was family-near.

The result was `sidecar_readiness_uncontrolled`. The case/control split remained visible, but the controls were not comparable enough to support an upgrade. The diagnostic table recorded:

| Diagnostic | Result |
|---|---|
| Retained event taxa | pass |
| Source-density control | fail |
| Publication-proxy control | pass |
| Family-size control | pass, within the local panel |
| GBIF/WFO-resolution control | fail |
| Low-publication control constructibility | fail |

The source-density failure was the central blocker. Cases had event-source exposure by construction, while controls had broad metadata exposure but no curated event-source groups. The GBIF/WFO-resolution diagnostic also failed because the earlier WFO projection had already collapsed the sidecar to only 2 WFO-projectable event taxa. Low-publication control construction produced only 2 usable sparse controls, below the threshold needed to interpret sparse-control non-recovery.

![Track 1 GBIF-sidecar reticulation evidence recovery versus matched controls, stratified by source-group count and family/genus matching basis.](tracks/track1/figures/track1_free_tier_control_recovery.png)

The cycle 30 Track 1 auditor validated the conservative status. The auditor also noted a minor count discrepancy: worker narrative metadata said there was 1 usable low-publication control, while generated artifacts showed 2. The status did not change because 2 still failed the minimum threshold. No tree-compatibility-index rerun, WFO-based H1 reopening, schema change, master substrate change, prediction-ledger row, speculation-ledger row, or validated reticulation claim occurred.

### Cycle 30: Track 3 Built A Trait/Confound Matrix And Kept H3 Confound-Limited

The Track 3 branch built an accepted-key trait-by-taxon matrix for 15 canonical convergence traits. An accepted key is the canonical taxon identifier used for joins after synonym resolution. Controlled convergence-readiness means a trait clears all diagnostic gates needed to treat it as a controlled convergence candidate rather than a source or sampling artifact.

The matrix contained 3,069 accepted-key `(trait, accepted_taxon_key)` carrier rows. No trait satisfied all controlled-readiness gates. The branch therefore kept H3 at `confound_limited`.

The main trait-level results were:

| Trait | Accepted taxa | Families | CP_min | Status | Main blockers |
|---|---:|---:|---:|---|---|
| `drupe` | 186 | 32 | 5.647 | `data_limited_pending_prior` | projection loss; single-source dominance |
| `capsule` | 543 | 48 | 4.831 | `data_limited_pending_prior` | projection loss; family dominance; single-source dominance |
| `c4_photosynthesis` | 157 | 4 | -7.066 | `data_limited_pending_prior` | insufficient independent families; projection loss; confounds |
| `fleshy_fruit` | 716 | 42 | -5.850 | `data_limited_pending_prior` | projection loss; family dominance; confounds |
| `myrmecochory` | 288 | 14 | -10.328 | `confound_limited_pending_prior` | family dominance; family-size and sampling-density confounds |

`CP_min` is the convergence-pressure score carried from the Track 3 instrument, defined as the weaker of two null-model residual scores. The new branch did not treat high `CP_min` alone as sufficient. A trait also had to clear accepted-taxon count, family count, top-family share, family-size baseline, sampling-density baseline, accepted-resolution, and source-dominance gates.

`drupe` and `capsule` remained the strongest priors because they cleared the earlier score screen. They did not become validated convergence claims because retained carriers were still dominated by one frozen source family, `austraits_6_0_0`, and both suffered accepted-key projection loss.

![Canonical Track 3 traits plotted by accepted-family dispersion, top-family dominance, and sampling-density baseline residual; readiness labels distinguish controlled candidates from data/confound-limited priors.](tracks/track3/figures/track3_free_tier_trait_confound_matrix.png)

The branch did not modify the schema, substrate, prediction ledger, or speculation ledger.

### Cycle 31: Track 2 Ghost Controls Found Zero Validation-Contract Passes

The Track 2 free-tier ghost-hyperedge branch tested whether local evidence repair could rescue canonical Janzen-Martin-style held-outs or local candidates. The validation contract required all of the following at once:

1. accepted-key recovery,
2. independent modern dispersal-failure evidence,
3. non-singleton or multi-source-class support,
4. exclusion of living-megafauna ambiguity.

No canonical held-out passed the conjunction. The gate counts were:

| Scope | Rows | Accepted key present or repaired | Independent modern-failure evidence | Non-singleton/source support | Living-megafauna exclusion | Full validation pass |
|---|---:|---:|---:|---:|---:|---:|
| canonical held-out | 8 | 2 | 0 | 0 | 7 | 0 |
| local candidate | 31 | 6 | 0 | 0 | 30 | 0 |

The canonical held-outs were `Persea americana`, `Maclura pomifera`, `Gleditsia triacanthos`, `Annona cherimola`, `Mauritia flexuosa`, `Spondias mombin`, `Sideroxylon foetidissimum`, and `Asimina triloba`. Only `Annona cherimola` and `Asimina triloba` had accepted keys already present. All eight lacked independent modern-failure evidence beyond seed/local evidence, and all eight failed non-singleton/source-class support. `Gleditsia triacanthos` also had living-megafauna ambiguity.

![Canonical held-outs and local candidates by accepted-key recovery, modern-failure evidence, source-class support, living-megafauna exclusion, and final validation-contract status.](tracks/track2/figures/track2_free_tier_ghost_control_matrix.png)

The decision was `H2_remains_not_supported_or_data_limited`. Missing accepted keys were treated as namespace/data limitations, not biological falsifications. Missing modern-failure evidence was insufficient support. Singleton/source-class fragility was a control failure. No anachronism claim entered the master prediction ledger.

### Cycle 31: Fork Integration Reconciled Track 2 And Track 3 Without Promotion

The post-merge integration reconciled fork `2f05eabe3800`, which had two completed clone outputs:

| Clone | Track | Outcome | Deliverable |
|---|---|---|---|
| clone-0 | Track 2 | done | `tracks/track2/reports/track2_free_tier_ghost_evidence_controls.md` |
| clone-1 | Track 3 | done | `tracks/track3/reports/track3_free_tier_trait_confound_matrix.md` |

The integration did not start new research, fetch external data, refit instruments, run audit-level validation, or promote any master-ledger row. It recorded the shared Barrier 4 boundary:

- Track 2 remained `H2_remains_not_supported_or_data_limited`.
- Track 3 remained `confound_limited`.
- The master ledgers stayed header-only.

The supplied audit report for this user request validated that integration as complete at worker scope. It reported 13 focused tests passing, both branch figure checks passing, `promise_check` and `org_check` exiting 0 with inherited warnings, and `prediction_ledger.tsv` plus `speculation_ledger.tsv` each remaining one line.

### Cycle 32: No Substantive Local Work Artifact Was Found

The supplied cycle-session list includes a cycle 32 worker session ID, `84a10aee-f522-4e64-9cb5-e942b0e15ed2`. Full session-fetch tools were not available, and local search found only manager/watch ledger entries for cycle 32, not a substantive cycle 32 report, branch output, validation artifact, or integration record.

This is recorded as a gap rather than filled by inference. Within the local artifact record available for this report, cycles 30-31 contain the substantive work, while cycle 32 does not add a documented scientific result.

## Discussion

Cycles 30-32 strengthened closure by making prior blockers more explicit.

Track 1 did not lose the GBIF sidecar signal; it constrained its interpretation. The sidecar still records event-shaped evidence for 22 GBIF accepted-key event taxa, but the cycle 30 controls show that source-density and WFO-resolution comparability remain unresolved. This keeps the sidecar useful for readiness diagnostics only.

Track 2’s result is a sharper null result under the stated contract. The work did not show that ghost hyperedges are biologically absent. It showed that the current local/free-tier evidence does not meet the accepted-key, modern-process, source-support, and living-megafauna gates needed to validate H2.

Track 3’s matrix created a more concrete failure mode for H3. The problem is not merely that convergence traits are missing. Some traits have many accepted-key carriers and high prior scores. The blocker is that controlled-readiness requires those carriers to survive projection-loss, source-dominance, family-size, and sampling-density checks. No trait did.

Across all three tracks, the shared decision was conservative: branch-local diagnostics may refine future work, but none creates a master-level prediction row.

## Open Questions

1. Track 1: Can a future WFO-compatible crosswalk recover canonical hybrid and polyploid taxa while also constructing comparable non-event controls under the same source-extraction protocol?
2. Track 2: Can independent modern dispersal-failure or recruitment-failure evidence be attached to the same accepted taxa and extinct-fauna candidate pairs, rather than remaining seed-citation-only?
3. Track 3: Can convergence trait carriers be rebuilt from more than one source family so that `drupe`, `capsule`, and other traits can be tested without single-source dominance?
4. Cycle 32 record gap: Was the listed cycle 32 worker session a no-work continuity event, an unmaterialized worker attempt, or a session whose artifacts were not written into the local workspace?

## References

[4] The World Flora Online Consortium et al., "World Flora Online Plant List December 2025," Zenodo, 2025. https://doi.org/10.5281/zenodo.18007552

[6] GBIF Secretariat, "GBIF API Reference," GBIF Technical Documentation, 2026. https://techdocs.gbif.org/en/openapi/

[7] GBIF Secretariat, "Species API," GBIF Technical Documentation, 2026. https://techdocs.gbif.org/en/openapi/v1/species

[8] GBIF Secretariat, "Occurrence API," GBIF Technical Documentation, 2026. https://techdocs.gbif.org/en/openapi/v1/occurrence

[31] Daniel Falster, Rachael Gallagher, Elizabeth Wenk, Herve Sauquet, et al., "AusTraits: a curated plant trait database for the Australian flora," Zenodo, version 6.0.0, 2024. https://doi.org/10.5281/zenodo.11188867

## Appendix: Implementation Details

### Source Inventory

| Source ID | Date | Content | Timeline role |
|---|---|---|---|
| `c3387235-45e2-4435-9e10-5991aaa3a5e2` | cycle 30 | Listed worker session | Full transcript unavailable; local artifacts show cycle 30 Track 1 and Track 3 worker outputs. |
| `7f0e3fd4-e3fb-4e36-9577-c23b032b0b4b` | cycle 30 | Listed auditor session | Full transcript unavailable; promise ledger records Track 1 control-strengthening audit validation. |
| `df8a1f19-13ae-4353-a707-35f681fa3dae` | cycle 31 | Listed researcher session | Full transcript unavailable; no separate local research brief found for this report window. |
| `.long-exposure/fork-2f05eabe3800/clone-0/merge_report.md` | 2026-05-18 | Track 2 clone merge report | Records Track 2 outputs, validation commands, 13 passed tests, and no-promotion guidance. |
| `.long-exposure/fork-2f05eabe3800/clone-1/merge_report.md` | 2026-05-18 | Track 3 clone merge report | Records Track 3 outputs, 27 passed tests, and no-promotion guidance. |
| `reports/fork_2f05eabe3800_postmerge_integration.md` | 2026-05-18 | Post-merge integration | Reconciles Track 2 and Track 3 fork outputs without changing branch science outputs. |
| `84a10aee-f522-4e64-9cb5-e942b0e15ed2` | cycle 32 | Listed worker session | Full transcript unavailable; no substantive local cycle 32 artifact found. |

### Code Organization

Track 1 cycle 30 files:

- `tracks/track1/scripts/build_free_tier_control_strengthening.py` — 387 lines
- `tracks/track1/scripts/plot_free_tier_control_strengthening.py` — 60 lines
- `tests/test_track1_free_tier_control_strengthening.py` — 94 lines
- `tracks/track1/reports/track1_free_tier_control_strengthening.md` — 49 lines

Track 2 cycle 31 files:

- `tracks/track2/scripts/track2_free_tier_ghost_evidence_controls.py` — 451 lines
- `tracks/track2/scripts/plot_track2_free_tier_ghost_evidence_controls.py` — 71 lines
- `tracks/track2/tests/test_track2_free_tier_ghost_evidence_controls.py` — 95 lines
- `tracks/track2/reports/track2_free_tier_ghost_evidence_controls.md` — 100 lines

Track 3 cycle 30 files:

- `tracks/track3/scripts/build_free_tier_trait_confound_matrix.py` — 476 lines
- `tracks/track3/tests/test_track3_free_tier_trait_confound_matrix.py` — 134 lines
- `tracks/track3/reports/track3_free_tier_trait_confound_matrix.md` — 50 lines

Integration file:

- `tests/test_fork_2f05eabe3800_postmerge_integration.py` — 84 lines
- `reports/fork_2f05eabe3800_postmerge_integration.md` — 60 lines

### Test Results

Reported validation results from source artifacts and supplied audit input:

- Track 1 control-strengthening audit: focused tests, compile checks, figure nonblank check, promise check, and org check passed with inherited warnings only.
- Track 2 clone merge: 13 tests passed; figure check OK at 73 KB; master ledgers remained header-only.
- Track 3 clone merge: 27 tests passed in 70.24 seconds; figure check OK at 137 KB; master ledgers remained header-only.
- Post-merge integration audit input: 13 focused tests passed in 44.50 seconds; Track 2 and Track 3 figure checks passed; `promise_check` and `org_check` exited 0 with inherited warnings.
- `prediction_ledger.tsv`: 1 line, header-only.
- `speculation_ledger.tsv`: 1 line, header-only.

The reporter did not rerun tests; these results are reported from the worker, merge, and supplied audit records.

### Cross-Reference Map

| Origin | Consuming artifact | Flow |
|---|---|---|
| Cycle 29 Track 1 namespace reconciliation | Cycle 30 Track 1 control strengthening | The fixed GBIF sidecar became the case set for comparability diagnostics. |
| Track 1 control diagnostics | Barrier 4 handoff | Failed source-density and GBIF/WFO-resolution controls prevented H1 reopening. |
| Frozen Track 3 convergence-pressure outputs | Cycle 30 Track 3 matrix | Prior scores were reinterpreted under accepted-key, family-size, sampling-density, projection-loss, and source-dominance gates. |
| Track 2 clone output | Cycle 31 integration | H2 was reconciled as not supported/data-limited under the validation contract. |
| Track 3 clone output | Cycle 31 integration | H3 was reconciled as confound-limited with 0 controlled-ready traits. |
| Master ledgers | All cycle 30-32 outputs | Header-only state preserved because no branch met promotion criteria. |

### Record Gaps

Full session transcripts for the supplied session IDs were not accessible through tools available in this environment. The report therefore uses local artifacts, merge records, ledgers, and the supplied audit report as source material.

Cycle 32 has no substantive local artifact in the searched workspace record. Local evidence contains manager/watch entries, but not a cycle 32 branch report or scientific output.

### Manifest Update

`MANIFEST.md` was updated for `report_cycles_30-32`. The existing `## Key Files` section was preserved verbatim, and the mutable sections were replaced with the current script inventory, data/documentation inventory, cumulative stats, and cross-reference map.

### Coherence Review

One coherence pass was completed. The report states null, data-limited, and uncontrolled outcomes without converting them into biological conclusions. It defines sidecar and accepted-key usage before relying on them, and it records missing session access as a gap rather than inferring undocumented work.
