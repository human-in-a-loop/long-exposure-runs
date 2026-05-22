---
created: 2026-05-18T21:40:00+00:00
cycle: 28
run_id: run-phytograph-cycle28-free-tier-recovery-integration
agent: worker
milestone: _plan/free-tier-recovery-integration
---

# Free-Tier Recovery Integration

## Scope

This integration reconciles fork `5fe97ebd91d9` branch outputs for Track 1,
Track 4, and Track 5 into the main closure record, and now cross-references the
fork `2f05eabe3800` Track 2/3 closure integration. It does not start new
research, change schema v1.0, rerun predictors, execute models, or write rows to
the master `prediction_ledger.tsv` or `speculation_ledger.tsv`.

## Divergence Resolution

| Track | Branch result | Integration disposition |
|---|---|---|
| Track 1 | `threshold_met` branch-locally: 40/40 GBIF accepted-key joins, 22 distinct accepted-key taxa with event-shaped evidence, 11 independent source groups, and 0/17 matched-control event recovery. | Reopen status changes to `branch_local_threshold_met_reconciliation_pending`; master promotion remains blocked until GBIF accepted keys are reconciled against the frozen WFO-oriented accepted-key namespace or admitted as an audited sidecar namespace. |
| Track 2 | `H2_remains_not_supported_or_data_limited`: 8 canonical held-outs and 31 local candidates; 0/8 canonical held-outs pass the full validation contract. | H2 remains not supported/data-limited. The blocker is accepted-key modern-failure evidence, multi-source/source-class support, living-megafauna controls, and source-class-independent held-out recovery. |
| Track 3 | `confound_limited`: 3,069 accepted-key trait carrier rows across 15 canonical traits; 0 controlled-ready traits. | H3 remains confound-limited. `drupe` and `capsule` remain data-limited pending priors, not master convergence claims. |
| Track 4 | `still_data_limited`: 8,423 GBIF occurrence records, 3,408 license-compatible coordinate records, 3,358 post-filter records, 0 numeric BIOCLIM vectors, and 0 validation-allowed comparator rows. | H4 remains data-limited. The blocker is narrowed from no coordinates to no local/free BIOCLIM raster/runtime plus no disjoint candidate-level comparator rows. |
| Track 5 | `insufficient_non_duke_temporal_evidence_h5_remains_source_biased`: two accepted-key manual non-Duke candidates, but no structured family/class stratum. | H5 remains not validated and source-biased. The literal absence claim is refined: isolated open detections exist, but they do not support a non-Duke temporal family/class predictor rerun. |

## Master-Ledger Boundary

The Track 1 branch is the only disagreement with the prior post-reopen closure
matrix. It is useful and non-null, but it is still branch-local because its
accepted-key basis is GBIF, while the frozen substrate closure path is
WFO-oriented. Until that namespace question is resolved by auditor or conductor
review, the correct master-level status is reconciliation-pending, not a
promoted master claim.

The Track 4 and Track 5 branches refine the blockers without changing the
scientific conclusion. Track 4 now has bounded coordinate recovery but still has
zero numeric BIOCLIM vectors and zero validation-allowed comparator rows. Track
5 now has two manual accepted-key historical detection candidates, but no
structured non-Duke temporal evidence layer capable of estimating family/class
signatures under the existing scoring mechanism.

The Track 2 and Track 3 free-tier branch outcomes are master-level closure
records, not new evidence claims. Track 2 has 0/8 canonical held-outs passing
the validation contract, so no anachronism or ecological-interaction claim is
established. Track 3 has 0 controlled-ready traits across 3,069 accepted-key
trait carrier rows, so no convergence or adaptive-origin claim is established.

## Updated Closure Predicate

Track 1 can advance beyond reconciliation-pending only if the recovered GBIF
accepted-key event rows are mapped to the frozen WFO-oriented namespace or
explicitly admitted as an audited sidecar accepted-key namespace, while
preserving the branch evidence counts, source-group spread, matched-control
separation, and claim firewall.

Track 2 can reopen only with accepted-key modern-failure evidence,
multi-source/source-class support, living-megafauna controls, and
source-class-independent held-out recovery.

Track 3 can reopen only with broader trait coverage, phylogenetically separated
carrier sets, and family-size/sampling-density controls strong enough to
distinguish convergence from homology or sampling.

Track 4 can reopen only with audited local/free BIOCLIM summaries for paired
crop/CWR coordinates plus disjoint candidate-level comparator rows.

Track 5 can reopen only with a reproducible structured non-Duke intake that adds
accepted-key, dated taxon-compound rows across enough families/classes to
estimate `S_f[k]` without Duke/source-density collapse.

## Final Free-Tier Synthesis

The final six-track synthesis is
`reports/reopen/final_free_tier_closure_synthesis.md`, with canonical machine
rows in `data/reopen/final_free_tier_track_status.tsv` and summary figure
`reports/reopen/figures/final_free_tier_track_status.png`.

The final free-tier statuses are:

| Track | Final free-tier status | Boundary |
|---|---|---|
| Track 1 | `sidecar_readiness_uncontrolled` | 22 GBIF sidecar event taxa across 11 source groups are retained, but WFO projection is 2 taxa and source-density controls remain unresolved. |
| Track 2 | `H2_remains_not_supported_or_data_limited` | 0/8 canonical held-outs pass the validation contract. |
| Track 3 | `confound_limited` | 0 controlled-ready traits across 3,069 accepted-key trait carrier rows. |
| Track 4 | `still_data_limited` | 3,358 post-filter occurrence records exist, but numeric BIOCLIM vectors and validation-allowed comparator rows are both 0. |
| Track 5 | `H5_remains_source_biased` | Non-Duke temporal evidence is insufficient and no validation-ready structured family/class stratum exists. |
| Track 6 | `environment_limited_untested` | 0 runnable local runtime-weight pairings, 0 executed responses, and 0 scored responses. |

These statuses preserve the master-ledger boundary: no master prediction or
speculation row is promoted.
