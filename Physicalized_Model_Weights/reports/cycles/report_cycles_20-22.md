---
title: "Physicalized Model Weights - cycles 20-22"
date: "2026-05-13"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Physicalized Model Weights - cycles 20-22

## Abstract

Cycles 20-22 extended the validated Phase 3 reopen pathway from evidence acquisition readiness into an operator-facing package lifecycle and an uncertainty-aware decision rule. The work added three validated milestones:

- `M-DRYRUN-1`: an operator evidence-pack template and dry-run acceptance harness.
- `M-INTAKE-1`: a synthetic-safe intake rehearsal from dry-run templates into evidence-pack replay.
- `M-UNCERTAINTY-1`: a confidence-bound protocol for future measured reopen packages.

The main conclusion did not change. No current artifact reopens the Phase 2 downgrade. Full dense fixed frontier-model physicalization remains rejected, broad analog or in-memory physicalization remains speculative, and safety/filter physicalization remains a bounded architecture and evidence-gating study rather than a current performance or economic winner over strong programmable baselines.

The new contribution is procedural: a future measured shadow or canary evidence package now has a clearer path from pre-collection package preparation, through intake and replay, to statistical margin evaluation. Every stage preserves the distinction between preparation artifacts, synthetic-safe rehearsal artifacts, and real measured evidence.

## Introduction

Earlier cycles built a Phase 3 reopen pathway for the physicalized safety/filter case. In this project, "physicalized weights" means moving some model behavior into fixed or specialized physical structures rather than executing all behavior on programmable software or accelerator paths. The surviving candidate is not a full fixed frontier model. It is a narrow safety/filter fast path that could, in principle, route easy cases cheaply while preserving fallback and audit behavior.

The Phase 2 downgrade rejected the stronger claim that this safety/filter approach currently beats programmable baselines. Phase 3 therefore focused on defining what future evidence would be required to reopen that conclusion. By the start of Cycle 20, validated gates already existed for production measurement requirements, trace schema, quantitative reopen thresholds, ingestion-path admissibility, end-to-end reopen decisions, evidence-pack replay, Phase 3 synthesis, and acquisition readiness.

Cycles 20-22 addressed the next operational gaps:

1. How an operator prepares a future evidence package before collection.
2. How a filled package moves from dry-run preparation into replay.
3. How a future measured threshold crossing is judged under uncertainty.

The work remained intentionally synthetic-safe. It exercised package mechanics and decision rules without introducing real production traces or treating templates as evidence.

## Approach

The cycles followed the existing long-exposure pattern: each cycle selected one bounded sub-topic, built executable artifacts, generated documentation and result files, and underwent audit. The cycle sequence was chronological and cumulative.

Cycle 20 created the operator dry-run layer. It translated acquisition and replay requirements into a package skeleton and checker so future operators can find package-preparation mistakes before data collection.

Cycle 21 created the intake rehearsal layer. It tested whether synthetic-safe filled packages could move from the dry-run layer into the existing evidence-pack replay harness while preserving hashes, manifest fields, threshold mappings, and attestations.

Cycle 22 created the uncertainty layer. It refined the point reopen inequality into a confidence-bound rule over the difference between measured hybrid cost and measured programmable-baseline cost.

The three cycles used the same central invariant: preparation, template, dry-run, synthetic, proxy, and rehearsal artifacts are not current reopen evidence. A future reopen requires a measured production, shadow, or canary package satisfying all prior Phase 3 gates and, after Cycle 22, an uncertainty-aware margin condition.

## Findings

### Cycle 20: Operator Evidence-Pack Dry Run

Cycle 20 implemented `M-DRYRUN-1`, an operator-facing evidence-pack template and dry-run acceptance harness. The researcher session `f8baf60e-1e05-4b81-ae42-8a3307c5b257` identified the gap: `M-ACQUIRE-1` could screen acquisition designs, but there was no concrete artifact an operator would use to assemble a future evidence package without stale hashes, raw-content columns, unknown threshold mappings, or unreplaced attestations.

The worker session `827bf125-b014-4576-ae38-dd2230925f7d` built:

- `physicalized-weights/scripts/evidence_pack_template_dryrun.py`
- `physicalized-weights/tests/test_evidence_pack_template_dryrun.py`
- `physicalized-weights/docs/operator_evidence_pack_template.md`
- `physicalized-weights/data/operator_evidence_pack_manifest_template.json`
- `physicalized-weights/data/operator_trace_template.csv`
- `physicalized-weights/data/operator_provenance_attestation_template.md`
- `physicalized-weights/data/evidence_pack_dryrun_cases.csv`
- `physicalized-weights/data/evidence_pack_dryrun_results.csv`
- `physicalized-weights/data/evidence_pack_dryrun_summary.json`
- `physicalized-weights/data/evidence_pack_dryrun_status_matrix.png`

The dry-run checker evaluates manifest completeness, trace header privacy, required trace columns, threshold scenario allow-list membership, hash consistency, source/measurement consistency, and attestation replacement. A dry run can become `ready_for_collection_not_evidence`, but it cannot become actual reopen evidence because it has no measured trace rows, measured terms, or threshold crossing.

The final audited summary reports 12 dry-run cases and zero actual reopen candidates:

| Status | Count |
|---|---:|
| `ready_for_collection_not_evidence` | 2 |
| `schema_blocked` | 5 |
| `template_incomplete` | 1 |
| `privacy_blocked` | 1 |
| `provenance_blocked` | 1 |
| `integrity_blocked` | 1 |
| `threshold_mapping_blocked` | 1 |

The two complete templates were `complete_shadow_template` and `complete_canary_template`. Both were classified as ready for measured collection, not evidence. Malformed cases covered missing manifest fields, raw content columns, placeholder attestations, unknown threshold scenarios, hash mismatches, source/measurement contradictions, invalid manifest source values, unknown ingestion paths, missing counterfactual baseline columns, and missing energy columns.

![Dry-run acceptance outcomes for operator evidence-pack templates, showing which package-preparation errors block collection readiness while all placeholder packages remain non-evidence.](physicalized-weights/data/evidence_pack_dryrun_status_matrix.png)

The auditor session `76378fe8-48e7-41a4-9a3b-bf6229b5396c` found one moderate issue: invalid manifest values could pass readiness because the dry-run checker did not yet enforce the `M-EVIDENCEPACK-1` manifest allow-list or the `M-INGEST-1` reopen-candidate ingestion-path allow-list. The auditor tightened the checker, added regression cases for `invalid_manifest_source_value` and `unknown_ingestion_path`, regenerated outputs, and validated the milestone. The validation event recorded `case_count = 12`, `ready_for_collection_not_evidence_count = 2`, `schema_blocked = 5`, and `actual_reopen_candidate_count = 0`.

### Cycle 21: Evidence-Pack Intake Rehearsal

Cycle 21 implemented `M-INTAKE-1`, a measured-package intake rehearsal from operator dry-run templates into evidence-pack replay. The researcher session `28d7c9a5-7b48-4a09-bc75-41bb707916cf` framed the problem as a handoff boundary: a future operator needs to know that a filled package can move from dry-run state into replay state without manual file surgery or silent mutation of hashes, manifests, threshold mappings, and attestations.

The worker session `e8aa1893-5835-431a-b8de-6ffdd95009b6` built:

- `physicalized-weights/scripts/evidence_pack_intake_rehearsal.py`
- `physicalized-weights/tests/test_evidence_pack_intake_rehearsal.py`
- `physicalized-weights/docs/evidence_pack_intake_rehearsal.md`
- `physicalized-weights/data/evidence_pack_intake_cases.csv`
- `physicalized-weights/data/intake_rehearsal_packages/`
- `physicalized-weights/data/evidence_pack_intake_rehearsal_results.csv`
- `physicalized-weights/data/evidence_pack_intake_rehearsal_summary.json`
- `physicalized-weights/data/evidence_pack_intake_rehearsal_flow.png`

The intake rehearsal regenerates the dry-run templates, fills synthetic-safe package-local traces, computes trace SHA-256 values, writes replay-compatible manifests, checks preservation across handoff, and then delegates preserved packages to the existing `M-EVIDENCEPACK-1` replay evaluator.

The final audited summary reports nine cases:

| Intake result | Count |
|---|---:|
| `intake_passed` | 3 |
| `intake_manifest_blocked` | 2 |
| `intake_hash_blocked` | 1 |
| `intake_threshold_blocked` | 1 |
| `intake_attestation_blocked` | 1 |
| `intake_privacy_blocked` | 1 |

Three synthetic-safe packages passed intake:

- `shadow_synthetic_filled_non_crossing`
- `canary_synthetic_filled_non_crossing`
- `synthetic_counterfactual_crossing_non_actual`

The shadow and canary cases replayed as `threshold_evaluable_not_crossed`. The synthetic counterfactual reached the arithmetic crossing branch but remained non-actual because the source and ingestion gates still failed. Six mutation cases were blocked before replay: stale hash, trace-file aliasing, manifest/source mismatch, threshold remapping, attestation mutation, and post-dry-run raw content.

![Intake rehearsal from operator dry-run templates to evidence-pack replay, showing preserved hashes/manifests for valid synthetic-safe packages and blocked handoff mutations before any current artifact can reopen.](physicalized-weights/data/evidence_pack_intake_rehearsal_flow.png)

The auditor session `09ed2efc-37e8-4297-b968-d84c02b9383c` found one moderate issue: `trace_file` identity was not preserved. A manifest could be changed after dry run to point at an identical copied trace file, and intake would still pass because `trace_file` was not part of the preserved manifest fields. The auditor added `trace_file` preservation, added the `trace_file_alias_after_handoff` mutation case, added a regression test, regenerated artifacts, and validated the milestone. The final summary reports `successful_intake_count = 3`, `blocked_before_replay_count = 6`, `all_successful_intakes_preserved = true`, and `actual_reopen_candidate_count = 0`.

### Cycle 22: Measured Reopen Uncertainty Protocol

Cycle 22 implemented `M-UNCERTAINTY-1`, an uncertainty-aware decision-margin protocol for future measured reopen packages. The researcher session `dfa04e65-1796-47f2-95db-9c0799ee4edc` identified the next gap: the existing reopen rule used a point inequality, but any real shadow or canary package will contain sampling variance, meter calibration error, workload-mix uncertainty, correlated measurement error, and finite sample effects.

The worker session `7b77bc20-7667-4f1c-ae8e-340384d29ea7` built:

- `physicalized-weights/scripts/reopen_uncertainty_protocol.py`
- `physicalized-weights/tests/test_reopen_uncertainty_protocol.py`
- `physicalized-weights/docs/measured_reopen_uncertainty_protocol.md`
- `physicalized-weights/data/reopen_uncertainty_cases.csv`
- `physicalized-weights/data/reopen_uncertainty_results.csv`
- `physicalized-weights/data/reopen_uncertainty_summary.json`
- `physicalized-weights/data/reopen_uncertainty_margin_plot.png`

The protocol defines the operative difference:

$$D = H - B$$

where $H$ is the measured hybrid total and $B$ is the measured best programmable baseline total under the same workload, fallback, audit, update, utilization, latency, and energy accounting.

The uncertainty-aware rule is:

$$UCB_\alpha(D) = \Delta_{\text{mean}} + z_\alpha \sigma_\Delta < 0$$

with:

$$\Delta_{\text{mean}} = H_{\text{mean}} - B_{\text{mean}}$$

and:

$$\sigma_\Delta = \sqrt{\sigma_H^2 + \sigma_B^2 - 2\rho\sigma_H\sigma_B + \sigma_{\text{workload mix}}^2 + \sigma_{\text{meter}}^2}$$

This rule is necessary but not sufficient. It is conjoined with the existing Phase 3 gates: valid package, hash match, schema compatibility, known threshold scenario, valid trace, admissible ingestion path, measured terms, production/shadow/canary source, provenance attestation, privacy attestation, threshold crossing, nonzero request volume, and nonzero accepted fast-path volume.

The final audited summary evaluates 11 synthetic-safe scenarios and reports zero actual reopen candidates:

| Classification | Count |
|---|---:|
| `statistically_durable_nonactual_control` | 2 |
| `blocked_missing_uncertainty_terms` | 3 |
| `baseline_favored` | 1 |
| `blocked_all_fallback` | 1 |
| `blocked_non_actual_source` | 1 |
| `blocked_zero_volume` | 1 |
| `inconclusive_overlap` | 1 |
| `point_crossing_not_statistically_durable` | 1 |

The key discriminating examples are:

| Case | Result |
|---|---|
| `point_crossing_wide_uncertainty` | $\Delta_{\text{mean}} = -20$, but $UCB_\alpha = 66.186070$, so the point crossing is not statistically durable. |
| `synthetic_large_margin_low_uncertainty` | $UCB_\alpha = -215.711866$, but the case is synthetic and remains non-actual. |
| `zero_volume_control` | Blocked despite any favorable arithmetic because there is no request volume. |
| `all_fallback_control` | Blocked because there is no accepted fast-path volume. |
| `high_correlation_without_shared_instrumentation` | Blocked after audit because high correlation cannot cancel uncertainty without shared-instrumentation attestation. |

![Uncertainty intervals for synthetic-safe measured-package scenarios, showing which point crossings fail or pass the statistical margin rule and why none are current actual reopen evidence.](physicalized-weights/data/reopen_uncertainty_margin_plot.png)

The auditor session `93487eb1-f2b3-4317-be7e-e2c8d07e8f95` found one moderate issue: `rho = 1.0` without explicit shared-instrumentation evidence could collapse $\sigma_\Delta$ to zero and classify an otherwise actual measured candidate as statistically durable. The auditor added a high-correlation attestation blocker, a regression scenario, and a test. After regeneration, the milestone was validated with 11 scenarios and `actual_reopen_candidate_count = 0`.

## Discussion

Cycles 20-22 converted the Phase 3 reopen pathway from a set of validated gates into an operator-oriented lifecycle.

The dry-run layer answers: "Can a future operator assemble the right package structure before collection?" The answer is yes for two complete shadow/canary templates, but the outputs remain non-evidence.

The intake layer answers: "Can a filled package move into evidence-pack replay without silent mutation?" The answer is yes for preserved synthetic-safe packages, while stale hashes, trace-file aliasing, manifest changes, threshold remapping, attestation changes, and raw-content additions are blocked before replay.

The uncertainty layer answers: "If a future measured package crosses the point threshold, when is that crossing durable enough to matter?" The answer is: only when the upper confidence bound on $H - B$ is below zero, and only after all existing package and source gates pass.

Together, these cycles make the future reopen condition stricter and more explicit:

```text
valid_package
AND hash_match
AND schema_compatible
AND known_threshold_scenario
AND valid_trace
AND admissible_ingestion_path
AND measured_terms
AND production_or_shadow_or_canary_source
AND provenance_attestation
AND privacy_attestation
AND threshold_crossed
AND nonzero_request_volume
AND nonzero_accepted_fast_path_volume
AND UCB_alpha(hybrid_total - best_programmable_total) < 0
```

The evidence standard remains calibrated against the earlier stronger-baseline work. Public calibration context from Horowitz, NVIDIA H100 specifications, and MLPerf Inference documentation remains relevant to the Phase 2 and Phase 3 baseline framing [7]-[10]. No new external references were added in cycles 20-22.

The work does not claim production superiority. It builds the machinery that a future production/shadow/canary package would need to pass before such a claim could be reopened.

## Open Questions

No real production trace has been ingested. The current artifacts are templates, synthetic-safe rehearsals, and decision protocols.

Production accelerator energy, latency, utilization, batching effects, fallback behavior, audit cost, update cadence, and workload mix remain unmeasured in real deployments.

The uncertainty protocol defines a normal-approximation confidence-bound rule. Future real evidence may require more detailed treatment if measurement distributions are heavy-tailed, request classes are highly imbalanced, or instrumentation errors are not well approximated by the current terms.

Compiled Verilator simulation remains a future superseding check for the earlier `M-PROTO-1` HDL path if local build tools become available. This does not affect the cycle 20-22 evidence-package lifecycle.

## References

[7] Mark Horowitz, "1.1 Computing's Energy Problem (and What We Can Do about It)," 2014 IEEE International Solid-State Circuits Conference Digest of Technical Papers (ISSCC), 2014. https://doi.org/10.1109/ISSCC.2014.6757323

[8] Mark Horowitz, "Computing's Energy Problem (and What We Can Do about It)," slide transcript/mirror of ISSCC 2014 energy table. https://doczz.net/doc/9135487/computing-s-energy-problem--and-what-we-can-do-about-it-

[9] NVIDIA, "NVIDIA H100 Tensor Core GPU," product specification page. https://www.nvidia.com/en-us/data-center/h100/

[10] MLCommons, "MLPerf Inference: Datacenter benchmark documentation," MLCommons. https://docs.mlcommons.org/inference/

## Appendix: Implementation Details

### Code Organization

Cycle 20 added the operator dry-run package:

- `physicalized-weights/scripts/evidence_pack_template_dryrun.py` - 704 lines
- `physicalized-weights/tests/test_evidence_pack_template_dryrun.py` - 161 lines
- `physicalized-weights/docs/operator_evidence_pack_template.md` - 38 lines
- `physicalized-weights/data/operator_evidence_pack_manifest_template.json`
- `physicalized-weights/data/operator_trace_template.csv`
- `physicalized-weights/data/operator_provenance_attestation_template.md`
- `physicalized-weights/data/evidence_pack_dryrun_cases.csv`
- `physicalized-weights/data/evidence_pack_dryrun_results.csv`
- `physicalized-weights/data/evidence_pack_dryrun_summary.json`
- `physicalized-weights/data/evidence_pack_dryrun_status_matrix.png`

Cycle 21 added the intake rehearsal package:

- `physicalized-weights/scripts/evidence_pack_intake_rehearsal.py` - 599 lines
- `physicalized-weights/tests/test_evidence_pack_intake_rehearsal.py` - 124 lines
- `physicalized-weights/docs/evidence_pack_intake_rehearsal.md` - 33 lines
- `physicalized-weights/data/evidence_pack_intake_cases.csv`
- `physicalized-weights/data/intake_rehearsal_packages/`
- `physicalized-weights/data/evidence_pack_intake_rehearsal_results.csv`
- `physicalized-weights/data/evidence_pack_intake_rehearsal_summary.json`
- `physicalized-weights/data/evidence_pack_intake_rehearsal_flow.png`

Cycle 22 added the uncertainty protocol package:

- `physicalized-weights/scripts/reopen_uncertainty_protocol.py` - 669 lines
- `physicalized-weights/tests/test_reopen_uncertainty_protocol.py` - 130 lines
- `physicalized-weights/docs/measured_reopen_uncertainty_protocol.md` - 42 lines
- `physicalized-weights/data/reopen_uncertainty_cases.csv`
- `physicalized-weights/data/reopen_uncertainty_results.csv`
- `physicalized-weights/data/reopen_uncertainty_summary.json`
- `physicalized-weights/data/reopen_uncertainty_margin_plot.png`

`MANIFEST.md` was updated as the current workspace snapshot. It now reports 24 authored research scripts with 9,892 total script lines, 21 stdlib test files with 2,928 total test lines, 23 authored docs and diagram sources with 1,487 total lines, 60 ledger events, and 22 plan milestones.

### Generated Figures

The following cycle 20-22 figures exist and were checked as valid PNG files:

| Figure | Dimensions |
|---|---:|
| `physicalized-weights/data/evidence_pack_dryrun_status_matrix.png` | 980 x 430 |
| `physicalized-weights/data/evidence_pack_intake_rehearsal_flow.png` | 980 x 430 |
| `physicalized-weights/data/reopen_uncertainty_margin_plot.png` | 980 x 430 |

### Test Results

The cycle records and audit report report the following validation commands as passed:

```bash
python3 physicalized-weights/scripts/evidence_pack_template_dryrun.py
python3 physicalized-weights/tests/test_evidence_pack_template_dryrun.py
file physicalized-weights/data/evidence_pack_dryrun_status_matrix.png
python3 physicalized-weights/scripts/evidence_pack_intake_rehearsal.py
python3 physicalized-weights/tests/test_evidence_pack_intake_rehearsal.py
file physicalized-weights/data/evidence_pack_intake_rehearsal_flow.png
python3 physicalized-weights/scripts/reopen_uncertainty_protocol.py
python3 physicalized-weights/tests/test_reopen_uncertainty_protocol.py
file physicalized-weights/data/reopen_uncertainty_margin_plot.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

The reporter reran the repository checks after updating `MANIFEST.md`:

- `promise_check`: exit 0, `events: 60`, `plan milestones: 22`.
- `org_check`: exit 0.

Remaining warnings are pre-existing: orphan report artifacts under `reports/cycles/` and root prompt/log files `physicalized_model_weights_long_exposure_prompt.md` and `physicalized_weights_long_exposure_live.log`.

### Session References

| Cycle | Role | Session ID | Contribution |
|---:|---|---|---|
| 20 | researcher | `f8baf60e-1e05-4b81-ae42-8a3307c5b257` | Defined `M-DRYRUN-1` scope and sufficiency criteria. |
| 20 | worker | `827bf125-b014-4576-ae38-dd2230925f7d` | Built dry-run templates, checker, tests, data, and figure. |
| 20 | auditor | `76378fe8-48e7-41a4-9a3b-bf6229b5396c` | Validated `M-DRYRUN-1` after fixing manifest and ingestion allow-list enforcement. |
| 21 | researcher | `28d7c9a5-7b48-4a09-bc75-41bb707916cf` | Defined `M-INTAKE-1` handoff-rehearsal scope. |
| 21 | worker | `e8aa1893-5835-431a-b8de-6ffdd95009b6` | Built intake rehearsal script, packages, tests, data, and figure. |
| 21 | auditor | `09ed2efc-37e8-4297-b968-d84c02b9383c` | Validated `M-INTAKE-1` after adding `trace_file` preservation. |
| 22 | researcher | `dfa04e65-1796-47f2-95db-9c0799ee4edc` | Defined `M-UNCERTAINTY-1` decision-margin protocol. |
| 22 | worker | `7b77bc20-7667-4f1c-ae8e-340384d29ea7` | Built uncertainty classifier, tests, data, document, and figure. |
| 22 | auditor | `93487eb1-f2b3-4317-be7e-e2c8d07e8f95` | Validated `M-UNCERTAINTY-1` after adding high-correlation attestation blocking. |

### Cross-Reference Map

The cycle 20-22 dependency chain is:

```text
M-ACQUIRE-1 + M-EVIDENCEPACK-1
  -> evidence_pack_template_dryrun.py
  -> operator_evidence_pack_template.md
  -> evidence_pack_dryrun_summary.json

evidence_pack_template_dryrun.py + M-EVIDENCEPACK-1
  -> evidence_pack_intake_rehearsal.py
  -> evidence_pack_intake_rehearsal_summary.json
  -> evidence_pack_replay.py

M-REOPEN-1 + M-EVIDENCEPACK-1 + M-INTAKE-1
  -> reopen_uncertainty_protocol.py
  -> reopen_uncertainty_summary.json
```

The cumulative result is an end-to-end future evidence-package lifecycle: acquisition readiness, operator dry run, intake rehearsal, evidence-pack replay, and uncertainty-aware margin evaluation. Every current cycle 20-22 artifact remains non-reopening.
