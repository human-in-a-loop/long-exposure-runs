---
title: "Physicalized Model Weights - cycles 26-28"
date: "2026-05-13"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Physicalized Model Weights - cycles 26-28

## Abstract

Cycles 26-28 converted the already validated negative research result into a controlled end state. Cycle 26 created a deferral watchlist (`M-DEFER-1`) so future work would not mistake synthetic, proxy, vendor-only, or template artifacts for measured evidence. Cycle 27 created a reader-facing closure package (`M-CLOSURE-1`) that consolidates the full campaign disposition. Cycle 28 created a machine-checkable archive index (`M-ARCHIVE-1`) that records canonical endpoint artifacts with existence, size, SHA-256 hash, milestone owner, artifact class, and regeneration command where available.

The scientific conclusion did not change during these cycles. Current artifacts still support zero current physicalized-weight performance or economic superiority claims, zero actual reopen candidates, zero new reopen gates, and `current_artifacts_reopen = false`. The only valid future performance/economic restart path remains the previously defined Phase 4 measured-evidence condition: an actual production, shadow, or canary package must satisfy package integrity, schema, ingestion, provenance, privacy, measured workload, measured best programmable baseline, threshold crossing, uncertainty durability, and lifecycle terminal-state requirements.

## Introduction

The broader campaign investigated whether useful portions of neural-network inference could be "physicalized" into fixed or semi-fixed hardware structures. Earlier cycles built a taxonomy, break-even models, target rankings, a hybrid safety/filter architecture, a bounded prototype, calibrated comparisons against public energy and accelerator context, stronger programmable baselines, production-trace requirements, and a full measured-evidence reopen pathway. The Phase 2 calibration and stronger-baseline framing remained tied to public energy and accelerator references, including Horowitz energy estimates, NVIDIA H100 specifications, and MLPerf inference documentation [7]-[10].

By the start of cycle 26, the campaign endpoint was already stable:

- Broad fixed frontier-model physicalization was rejected under current evidence.
- Safety/filter performance superiority was falsified against the stronger programmable baseline.
- The hybrid architecture and prototype remained useful as bounded design, failure-mode, and verification work.
- The Phase 4 reopen pathway existed but was inactive because no actual measured production, shadow, or canary package had been ingested.
- The robustness stress test found zero calibrated physicalized wins across target classes.

Cycles 26-28 therefore did not extend the model with another synthetic scenario. They made the endpoint easier to govern, read, and archive.

## Approach

The work proceeded in three reporting and handoff layers.

Cycle 26 (`M-DEFER-1`) built a governance layer. It classified current claims, listed what future evidence would justify action, and blocked insufficient substitutes from triggering new work.

Cycle 27 (`M-CLOSURE-1`) built a reader-facing closure layer. It consolidated the validated campaign into a final disposition report, executive summary, claim table, artifact manifest, and evidence-flow figure.

Cycle 28 (`M-ARCHIVE-1`) built a reproducibility layer. It indexed canonical endpoint artifacts and upstream campaign evidence with hashes and regeneration commands, while documenting known noncanonical warnings.

The provided cycle sessions were used as the source record:

- Cycle 26: researcher `b6e11b5b-307f-4eb6-b563-202ddf3d4382`, worker `f63918c4-478f-403b-8f5e-00dcde62b52b`, auditor `b91a2419-5436-471a-ac3c-14522f463893`.
- Cycle 27: researcher `cfc4885e-e84c-44c8-8e16-89ba903a5793`, worker `30c63335-b9d1-4de4-93f9-5006951e5427`, auditor `1b8a746f-e7fc-4a92-83f8-09e9a04ef1b1`.
- Cycle 28: researcher `b47b1d70-282f-4290-8364-8af30f611307`, worker `6b704e11-bb4d-4d99-aec3-542ee71cfd69`, auditor `d303109e-78da-498e-9023-6462741c457a`.

## Findings

### Cycle 26: Campaign Deferral Watchlist

Cycle 26 created `M-DEFER-1`, a campaign deferral and future-evidence watchlist. Its purpose was to prevent future cycles from reopening the performance/economic question based on inputs that prior milestones had already classified as insufficient.

The worker created:

- `physicalized-weights/scripts/build_campaign_deferral_watchlist.py`
- `physicalized-weights/tests/test_campaign_deferral_watchlist.py`
- `physicalized-weights/docs/campaign_deferral_watchlist.md`
- `physicalized-weights/data/campaign_deferral_watchlist.csv`
- `physicalized-weights/data/campaign_deferral_watchlist_results.csv`
- `physicalized-weights/data/campaign_deferral_watchlist_summary.json`
- `physicalized-weights/data/campaign_deferral_watchlist.png`

The watchlist classified five current claim dispositions:

| Claim | Disposition |
|---|---|
| `broad_fixed_frontier_model_physicalization` | rejected under current evidence |
| `safety_filter_performance_or_economic_winner` | falsified under stronger programmable baseline |
| `hybrid_architecture_and_prototype` | retained as architecture, failure-mode, and evidence-scaffold work |
| `phase4_reopen_pathway` | complete but inactive absent actual measured evidence |
| `non_safety_target_classes_current_superiority` | no calibrated current superiority claim |

It also classified ten future trigger rows. Three measured-evidence triggers remained inactive until they satisfy the existing Phase 4 path: `measured_shadow_or_canary_package`, `measured_production_package`, and `new_stable_high-volume_target_evidence`. Four substitutes were explicitly insufficient: `vendor_benchmark_only`, `synthetic_counterfactual_only`, `local_proxy_only`, and `template_or_dryrun_only`. Two triggers affected prototype verification only: `compiled_verilator_available` and `hdl_design_scope_change`. One trigger, `programmable_baseline_public_update`, could refresh model assumptions but could not itself imply a physicalized win.

The summary values were:

| Field | Value |
|---|---:|
| `trigger_count` | 10 |
| `new_reopen_gate_count` | 0 |
| `current_superiority_claim_count` | 0 |
| `current_artifacts_reopen` | false |
| `phase4_future_reopen_condition_unchanged` | true |
| `measured_triggers_require_lifecycle_and_uncertainty` | true |
| `prototype_triggers_reopen_performance_claim` | false |

![Deferral map separating closed claims, inactive reopen triggers, insufficient substitutes, and prototype-only verification triggers.](physicalized-weights/data/campaign_deferral_watchlist.png)

The auditor validated `M-DEFER-1` with no critical or moderate issues. The only warnings were pre-existing validator warnings about orphan cycle reports and root prompt/log files.

### Cycle 27: Campaign Closure Report

Cycle 27 created `M-CLOSURE-1`, a reader-facing final disposition package. This was not a new model or gate. It projected the validated campaign state into a closure report, executive summary, claim disposition table, manifest, summary JSON, and evidence-flow figure.

The worker created or updated:

- `physicalized-weights/scripts/build_campaign_closure_report.py`
- `physicalized-weights/tests/test_campaign_closure_report.py`
- `physicalized-weights/docs/campaign_closure_report.md`
- `physicalized-weights/docs/campaign_executive_summary.md`
- `physicalized-weights/docs/final_synthesis.md`
- `physicalized-weights/docs/reproducibility.md`
- `physicalized-weights/data/campaign_closure_claim_disposition.csv`
- `physicalized-weights/data/campaign_closure_manifest.csv`
- `physicalized-weights/data/campaign_closure_summary.json`
- `physicalized-weights/data/campaign_closure_evidence_flow.png`

The closure report reduced the campaign to seven claim rows:

| Claim | Disposition |
|---|---|
| `full_frontier_fixed_weight_physicalization` | rejected under current evidence |
| `safety_filter_performance_superiority` | falsified under stronger programmable baseline |
| `hybrid_architecture_failure_mode_value` | retained as architecture and failure-mode study |
| `prototype_hdl_evidence` | retained as bounded prototype evidence |
| `future_measured_reopen_path` | complete but inactive absent actual measured evidence |
| `non_safety_target_robustness` | no calibrated current superiority claim |
| `campaign_deferral_state` | closed under current evidence, deferred until a valid measured package |

The closure summary recorded the campaign endpoint:

| Field | Value |
|---|---:|
| `claim_count` | 7 |
| `current_superiority_claim_count` | 0 |
| `actual_reopen_candidate_count` | 0 |
| `new_reopen_gate_count` | 0 |
| `current_artifacts_reopen` | false |
| `phase2_hybrid_workload_wins` | 0 |
| `robust_calibrated_physicalized_win_count` | 0 |

The closure report also preserved the future reopen condition exactly:

```text
valid_package && hash_match && schema_compatible && known_threshold_scenario && valid_trace && admissible_ingestion_path && measured_terms && production_or_shadow_or_canary_source && provenance_attestation && privacy_attestation && nonzero_request_volume && nonzero_accepted_fast_path_volume && measured_best_programmable_baseline && threshold_crossed && UCB_alpha(H - B) < 0 && lifecycle_terminal_state=actual_reopen_candidate
```

Here, `H` means measured hybrid total under the same workload accounting, and `B` means measured best programmable baseline total. `UCB_alpha(H - B) < 0` means the uncertainty-aware upper confidence bound for the hybrid-minus-baseline margin must remain below zero.

![Campaign evidence flow from taxonomy and modeling through Phase 2 downgrade, Phase 3/4 reopen pathway, robustness stress test, deferral watchlist, and final current-evidence closure.](physicalized-weights/data/campaign_closure_evidence_flow.png)

The auditor validated `M-CLOSURE-1`. The only minor issue was that the closure row for prototype HDL evidence used a terse evidence label, `python_yosys_verilator_lint_graphviz`; the auditor accepted it because the report explicitly states that compiled Verilator remains blocked. Known validator warnings remained nonblocking.

### Cycle 28: Closure Archive Index

Cycle 28 created `M-ARCHIVE-1`, a machine-checkable archive index for handoff and reproducibility. Its purpose was to reduce future rediscovery cost by mapping canonical endpoint artifacts to milestone owner, artifact class, file existence, byte size, SHA-256 hash, and regeneration command where known.

The worker created:

- `physicalized-weights/scripts/build_closure_archive_index.py`
- `physicalized-weights/tests/test_closure_archive_index.py`
- `physicalized-weights/docs/closure_archive_index.md`
- `physicalized-weights/data/closure_archive_manifest.csv`
- `physicalized-weights/data/closure_archive_manifest.json`
- `physicalized-weights/data/closure_archive_summary.json`
- `physicalized-weights/data/closure_archive_coverage.png`

The archive summary recorded:

| Field | Value |
|---|---:|
| `canonical_artifact_count` | 54 |
| `missing_canonical_artifact_count` | 0 |
| `zero_size_canonical_artifact_count` | 0 |
| `closure_claim_support_count` | 16 |
| `current_superiority_claim_count` | 0 |
| `actual_reopen_candidate_count` | 0 |
| `new_reopen_gate_count` | 0 |
| `current_artifacts_reopen` | false |
| `known_warning_count` | 2 |

The 54 canonical artifacts covered the endpoint chain from taxonomy and modeling through Phase 4, robustness, deferral, closure, and archive artifacts. The archive included reports, summary data, evidence data, figures, schemas, manifests, and one HDL source file. Its artifact-class counts were:

| Artifact class | Count |
|---|---:|
| `summary_data` | 21 |
| `report` | 16 |
| `figure` | 7 |
| `evidence_data` | 5 |
| `schema` | 2 |
| `manifest` | 2 |
| `hdl_source` | 1 |

The archive also documented two known warnings as noncanonical: orphan generated cycle reports under `reports/cycles/report_cycles_*`, and root prompt/log files. The archive did not move, delete, or reclassify those files.

![Archive coverage by milestone and artifact class, showing canonical closure/campaign artifacts present versus missing.](physicalized-weights/data/closure_archive_coverage.png)

The auditor validated `M-ARCHIVE-1` with no critical or moderate issues. One minor note was that `closure_archive_coverage.png` is a minimal generated coverage chart with bars and legend marks but no text axis labels inside the PNG itself. The auditor accepted this because the report caption and machine-readable archive summary carry the required meaning.

## Discussion

Cycles 26-28 changed the campaign's operational state, not its scientific conclusion. Before these cycles, the project had already concluded that current evidence does not support physicalized-weight performance or economic superiority. These cycles made that endpoint durable in three ways.

First, the deferral watchlist made future control flow explicit. A measured production, shadow, or canary package can activate only the existing Phase 4 pathway. Synthetic traces, local proxies, vendor-only claims, templates, dry-runs, intake rehearsals, and unverifiable summaries do not activate a reopen.

Second, the closure report made the conclusion readable without requiring a reader to reconstruct every prior cycle. It separated rejected claims, falsified claims, retained architecture/prototype value, inactive future reopen conditions, and deferred campaign state.

Third, the archive index made the endpoint auditable at the file level. It tied canonical artifacts to hashes and owners, while preserving the same zero-current-superiority and zero-current-reopen counters.

No new external references were added in these cycles. The cited public references remain those used by the earlier calibration and stronger-baseline context [7]-[10].

## Open Questions

No open question from cycles 26-28 changes the validated endpoint. Remaining gaps are operational:

- No actual measured production, shadow, or canary evidence package has been ingested.
- Compiled Verilator simulation remains a future superseding prototype check if local build tooling becomes available.
- The known orphan report and root prompt/log warnings remain documented as noncanonical validator warnings.
- Future performance/economic work should wait for actual Phase 4 lifecycle-valid measured evidence or a materially changed public baseline/toolchain condition.

## References

[7] Mark Horowitz, "1.1 Computing's Energy Problem (and What We Can Do about It)," 2014 IEEE International Solid-State Circuits Conference Digest of Technical Papers (ISSCC), 2014. https://doi.org/10.1109/ISSCC.2014.6757323

[8] Mark Horowitz, "Computing's Energy Problem (and What We Can Do about It)," slide transcript/mirror of ISSCC 2014 energy table. https://doczz.net/doc/9135487/computing-s-energy-problem--and-what-we-can-do-about-it-

[9] NVIDIA, "NVIDIA H100 Tensor Core GPU," product specification page. https://www.nvidia.com/en-us/data-center/h100/

[10] MLCommons, "MLPerf Inference: Datacenter benchmark documentation," MLCommons. https://docs.mlcommons.org/inference/

## Appendix: Implementation Details

### Code Organization

Cycle 26 added `build_campaign_deferral_watchlist.py` with 444 lines, `test_campaign_deferral_watchlist.py` with 116 lines, and `campaign_deferral_watchlist.md` with 58 lines.

Cycle 27 added `build_campaign_closure_report.py` with 518 lines, `test_campaign_closure_report.py` with 142 lines, `campaign_closure_report.md` with 71 lines, and `campaign_executive_summary.md` with 29 lines.

Cycle 28 added `build_closure_archive_index.py` with 442 lines, `test_closure_archive_index.py` with 133 lines, and `closure_archive_index.md` with 109 lines.

`MANIFEST.md` was updated for this report cycle. The current snapshot records 30 authored research scripts with 13,177 lines, 27 authored stdlib tests with 3,755 lines, 4 HDL/support files with 241 lines, and 30 authored research docs/diagram sources with 1,901 lines. There was no protected `## Key Files` section to preserve.

### Generated Figures

The cycle figures are valid PNG files:

| Figure | Dimensions |
|---|---|
| `physicalized-weights/data/campaign_deferral_watchlist.png` | 980 x 430 RGB |
| `physicalized-weights/data/campaign_closure_evidence_flow.png` | 1100 x 450 RGB |
| `physicalized-weights/data/closure_archive_coverage.png` | 1100 x 520 RGB |

### Test Results

Cycle 26 validation passed:

```bash
python3 physicalized-weights/scripts/build_campaign_deferral_watchlist.py
python3 physicalized-weights/tests/test_campaign_deferral_watchlist.py
file physicalized-weights/data/campaign_deferral_watchlist.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

Cycle 27 validation passed:

```bash
python3 physicalized-weights/scripts/build_campaign_closure_report.py
python3 physicalized-weights/tests/test_campaign_closure_report.py
file physicalized-weights/data/campaign_closure_evidence_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

Cycle 28 validation passed:

```bash
python3 physicalized-weights/scripts/build_closure_archive_index.py
python3 physicalized-weights/tests/test_closure_archive_index.py
file physicalized-weights/data/closure_archive_coverage.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

During this reporting pass, `promise_check` also exited 0 with `events: 75` and `plan milestones: 28`. It reported only known orphan-report warnings, including generated cycle reports through `report_cycles_23-25` and `report_cycles_8-10`. `org_check` exited 0 with only the known root prompt/log warnings.

### Session References

| Cycle | Role | Session ID | Main content |
|---|---|---|---|
| 26 | researcher | `b6e11b5b-307f-4eb6-b563-202ddf3d4382` | Defined `M-DEFER-1`, its trigger taxonomy, insufficient substitutes, and no-new-gate contract. |
| 26 | worker | `f63918c4-478f-403b-8f5e-00dcde62b52b` | Built the deferral watchlist package and fixed missing ledger event IDs before validation. |
| 26 | auditor | `b91a2419-5436-471a-ac3c-14522f463893` | Validated `M-DEFER-1` with no critical or moderate issues. |
| 27 | researcher | `cfc4885e-e84c-44c8-8e16-89ba903a5793` | Defined `M-CLOSURE-1` as reader-facing closure rather than a new model or gate. |
| 27 | worker | `30c63335-b9d1-4de4-93f9-5006951e5427` | Built the closure report, executive summary, claim table, manifest, summary, and evidence-flow figure. |
| 27 | auditor | `1b8a746f-e7fc-4a92-83f8-09e9a04ef1b1` | Validated `M-CLOSURE-1`; noted only minor wording and known validator warnings. |
| 28 | researcher | `b47b1d70-282f-4290-8364-8af30f611307` | Defined `M-ARCHIVE-1` as archive and handoff infrastructure. |
| 28 | worker | `6b704e11-bb4d-4d99-aec3-542ee71cfd69` | Built the archive index, manifest CSV/JSON, summary, tests, and coverage figure. |
| 28 | auditor | `d303109e-78da-498e-9023-6462741c457a` | Validated `M-ARCHIVE-1` with no critical or moderate issues. |

### Cross-Reference Map

`build_phase4_reopen_synthesis.py` and `target_robustness_stress.py` flow into `build_campaign_deferral_watchlist.py`: validated no-current-superiority and no-current-reopen outcomes become trigger governance for measured evidence, baseline refreshes, prototype-only checks, and insufficient substitutes.

`build_campaign_deferral_watchlist.py`, `build_phase4_reopen_synthesis.py`, and `target_robustness_stress.py` flow into `build_campaign_closure_report.py`: deferral state, Phase 4 reopen conditions, and robustness results are consolidated into the reader-facing campaign closure package.

`build_campaign_closure_report.py`, `build_campaign_deferral_watchlist.py`, and upstream canonical summaries flow into `build_closure_archive_index.py`: closure claim supports and endpoint artifacts are indexed by milestone, artifact class, file size, SHA-256 hash, and regeneration command while preserving zero current superiority claims and zero actual reopen candidates.
