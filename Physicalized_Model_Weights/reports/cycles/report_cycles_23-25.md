---
title: "Physicalized Model Weights - cycles 23-25"
date: "2026-05-13"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Physicalized Model Weights - cycles 23-25

## Abstract

Cycles 23-25 closed the current reopen-path work and then challenged the campaign conclusion on a separate robustness axis. Cycle 23 built `M-LIFECYCLE-1`, a deterministic evidence-package lifecycle state machine that composes acquisition readiness, operator dry-run, intake rehearsal, evidence-pack replay, threshold evaluation, and uncertainty margins into named terminal states. Cycle 24 built `M-PHASE4-SYNTH-1`, a canonical synthesis refresh that folds the validated lifecycle into the campaign claim record. Cycle 25 built `M-ROBUST-1`, a target-class robustness stress test across safety and non-safety physicalization targets.

The campaign conclusion did not change. Full fixed frontier-model physicalization remains rejected. Safety/filter performance superiority remains falsified against stronger programmable baselines. The hybrid safety/filter block remains useful as a bounded architecture, failure-mode, and evidence-scaffold study. No current artifact is actual measured production, shadow, or canary evidence, and no current artifact reopens the Phase 2 downgrade.

The final reopen condition is now canonicalized as a conjunction: a future package must be valid, hash-preserved, schema-compatible, mapped to a known threshold scenario, trace-valid, admissible, measured, production/shadow/canary sourced, provenance-attested, privacy-attested, nonzero in request volume and accepted fast-path volume, measured against the best programmable baseline, threshold-crossing, uncertainty-durable under $UCB_\alpha(H-B)<0$, and terminally classified as `actual_reopen_candidate` by the lifecycle state machine.

## Introduction

The long-exposure directive investigates whether "physicalized model weights" can support a credible hardware or systems claim. Earlier cycles established a taxonomy, built break-even and stronger-baseline models, prototyped a bounded safety/filter path, and then downgraded the performance claim after calibrated stronger-baseline replay. Later cycles built the reopen pathway: production measurement requirements, trace schema validation, quantitative thresholds, ingestion admissibility, end-to-end replay, operator templates, intake rehearsal, and an uncertainty-aware decision rule.

Cycles 23-25 address two questions left after that pathway existed:

1. Can the validated gates be composed into one auditable lifecycle without changing their semantics?
2. Once the reopen path is closed for current artifacts, does the negative result generalize beyond the original safety/filter target class?

The answer to both was reported as validated by the audit sessions. The lifecycle and synthesis cycles made the reopen condition complete and traceable; the robustness cycle found zero calibrated physicalized wins across eight target classes.

## Approach

The work was chronological.

Cycle 23, from researcher session `f445a470-5d93-40bd-8465-452a0f674d07`, worker session `d9d46fd4-3e13-47c6-9f17-752ae9417b21`, and auditor session `ee383376-449c-4250-8f0c-737202114972`, composed the validated gates into an evidence-package lifecycle state machine. A lifecycle state machine is a deterministic classifier: each package scenario receives exactly one terminal state, an owning gate, and a rationale.

Cycle 24, from researcher session `dca6756c-6344-44fa-be64-0480edf54bf6`, worker session `6d1b7541-55da-45fc-ac1d-513c8d929a0a`, and auditor session `e77bd625-5471-4a45-aec9-bad160f72169`, refreshed the canonical campaign synthesis. This cycle did not add a new gate; it consolidated the validated reopen pathway into claim, manifest, summary, and reproducibility artifacts.

Cycle 25, from researcher session `52d5ce28-d56b-47f3-b0d0-a5f52076e030`, worker session `48008c2a-d41f-4e0a-837a-87d7af85b671`, and auditor session `bfffac8e-0f4e-4325-9566-f242e65ed725`, stress-tested target classes against stronger programmable baselines. The stress test separated calibrated assumptions, favorable-plausible assumptions, extreme counterfactuals, and special controls.

The public calibration and stronger-baseline context still relies on the prior references for energy, accelerator, and inference benchmark framing [7]-[10]. No new external references were added during cycles 23-25.

## Findings

### Cycle 23: Evidence-Package Lifecycle State Machine

Cycle 23 built `M-LIFECYCLE-1`, an end-to-end lifecycle classifier for future evidence packages. The created artifacts were:

- `physicalized-weights/scripts/evidence_package_lifecycle.py`
- `physicalized-weights/tests/test_evidence_package_lifecycle.py`
- `physicalized-weights/docs/evidence_package_lifecycle_state_machine.md`
- `physicalized-weights/data/evidence_package_lifecycle_cases.csv`
- `physicalized-weights/data/evidence_package_lifecycle_results.csv`
- `physicalized-weights/data/evidence_package_lifecycle_summary.json`
- `physicalized-weights/data/evidence_package_lifecycle_flow.png`

The lifecycle defined terminal states including `collection_ready_not_evidence`, `dryrun_ready_not_evidence`, `intake_rehearsed_not_evidence`, `replay_blocked`, `threshold_crossed_nonactual`, `uncertainty_inconclusive`, `statistically_durable_nonactual`, and `actual_reopen_candidate`.

![State-machine flow from acquisition design through dry-run, intake, replay, threshold, and uncertainty gates, with terminal non-reopen states and the single hypothetical actual-measured candidate path highlighted.](physicalized-weights/data/evidence_package_lifecycle_flow.png)

The final lifecycle summary reported:

| Metric | Value |
|---|---:|
| Cases | 15 |
| Current actual reopen candidates | 0 |
| Current artifacts reopen | false |
| Hypothetical actual candidate controls | 1 |
| Status mismatches | 0 |

The single `actual_reopen_candidate` terminal state was reached only by `hypothetical_actual_measured_durable_candidate_control`. That row is a positive control showing that the state machine can represent future valid evidence; it is not counted as current evidence.

The auditor found one critical accounting defect: a current row reaching `actual_reopen_candidate` could have been masked because the candidate flag was forced false for `current_artifact=True`. The fix changed the summary count to derive from `terminal_state == actual_reopen_candidate`, suppressed the candidate flag only for hypothetical controls, and added `test_current_candidate_branch_is_not_masked_by_accounting`. After the fix, the auditor validated `M-LIFECYCLE-1` with event `6ab3748e-c2ce-4ad4-8b85-a3262e9473b9`.

### Cycle 24: Phase 4 Reopen Lifecycle Synthesis

Cycle 24 built `M-PHASE4-SYNTH-1`, a synthesis refresh after lifecycle closure. The created or updated artifacts were:

- `physicalized-weights/scripts/build_phase4_reopen_synthesis.py`
- `physicalized-weights/tests/test_phase4_reopen_synthesis.py`
- `physicalized-weights/docs/phase4_reopen_lifecycle_synthesis.md`
- `physicalized-weights/docs/final_synthesis.md`
- `physicalized-weights/docs/reproducibility.md`
- `physicalized-weights/data/phase4_reopen_claim_matrix.csv`
- `physicalized-weights/data/phase4_reopen_manifest.csv`
- `physicalized-weights/data/phase4_reopen_summary.json`
- `physicalized-weights/data/phase4_reopen_lifecycle_flow.png`

The Phase 4 summary reported:

| Metric | Value |
|---|---:|
| Claim rows | 10 |
| Current actual reopen candidates | 0 |
| Current artifacts reopen | false |
| Hypothetical actual candidate controls | 1 |

![Campaign-level evidence flow from Phase 2 downgrade through production measurement, trace/replay gates, operator preparation, uncertainty margins, lifecycle closure, and the still-empty current reopen branch.](physicalized-weights/data/phase4_reopen_lifecycle_flow.png)

The cycle canonicalized the future reopen condition:

```text
valid_package && hash_match && schema_compatible && known_threshold_scenario &&
valid_trace && admissible_ingestion_path && measured_terms &&
production_or_shadow_or_canary_source && provenance_attestation &&
privacy_attestation && nonzero_request_volume &&
nonzero_accepted_fast_path_volume && measured_best_programmable_baseline &&
threshold_crossed && UCB_alpha(H - B) < 0 &&
lifecycle_terminal_state=actual_reopen_candidate
```

Here, $H$ is the measured hybrid total and $B$ is the measured best programmable baseline total under the same workload accounting. The uncertainty rule requires the upper confidence bound on $H-B$ to be below zero.

The auditor found one critical auditability defect: five artifacts cited by claim rows were missing from `phase4_reopen_manifest.csv`. The fix added those claim-support artifacts to the generated manifest inputs and added `test_manifest_covers_every_claim_support`. After the fix, `missing_claim_supports` was empty, and the auditor validated `M-PHASE4-SYNTH-1` with event `9cd4dd0b-69da-410e-bd88-9b78af3629b8`.

### Cycle 25: Target Robustness Stress Test

Cycle 25 built `M-ROBUST-1`, a robustness stress test over target classes. The created artifacts were:

- `physicalized-weights/scripts/target_robustness_stress.py`
- `physicalized-weights/tests/test_target_robustness_stress.py`
- `physicalized-weights/docs/target_robustness_stress_test.md`
- `physicalized-weights/data/target_robustness_cases.csv`
- `physicalized-weights/data/target_robustness_results.csv`
- `physicalized-weights/data/target_robustness_summary.json`
- `physicalized-weights/data/target_robustness_frontier.png`

The eight target classes were:

| Target class |
|---|
| `safety_filter` |
| `embedding_lookup_or_static_table` |
| `fixed_feature_extractor` |
| `small_keyword_or_policy_classifier` |
| `decoder_dense_weights` |
| `attention_kv_or_dynamic_context` |
| `tenant_adapter_or_lora` |
| `training_optimizer_state` |

The stress test evaluated calibrated, favorable-plausible, extreme-counterfactual, and special-control regimes. It reported frontier quantities: minimum physicalized savings needed to tie, maximum allowable update frequency, and minimum utilization needed.

![Target-class robustness frontier showing the required physicalized per-request advantage or utilization/update-cadence shift needed to beat the best programmable baseline.](physicalized-weights/data/target_robustness_frontier.png)

The final robustness summary reported:

| Metric | Value |
|---|---:|
| Target classes | 8 |
| Cases | 28 |
| Calibrated physicalized wins | 0 |
| Favorable-plausible physicalized wins | 4 |
| Plausible anti-target wins | 0 |
| Extreme counterfactual wins | 8 |
| Current superiority claims | 0 |
| Status mismatches | 0 |

The favorable-plausible wins were limited to candidate-like stable targets under simultaneous favorable movement in request volume, utilization, update cadence, overhead, and physicalized per-request savings. Prior anti-targets remained blocked under plausible assumptions. Extreme wins were labeled `counterfactual_not_current_evidence`.

The auditor found one critical consistency defect: favorable-plausible anti-target rows were labeled as programmable-baseline wins while their computed `margin_vs_best_programmable` was negative. The fix kept plausible anti-target physicalized savings below candidate-like savings and added a regression asserting that favorable-plausible anti-target rows must not select `physicalized_target` and must have positive margins. After the fix, the auditor validated `M-ROBUST-1` with event `33828561-7fa4-4049-8af3-6bd07343da7e`.

## Discussion

Cycles 23-25 shifted the work from adding individual gates to closing and challenging the campaign record.

The lifecycle state machine made the gate ordering explicit. Readiness and dry-run artifacts stop before evidence credit. Intake rehearsal stops as rehearsal. Stale hashes and unknown threshold mappings stop before threshold evaluation. Zero-volume and all-fallback cases stop before margin credit. Noisy point crossings stop at the uncertainty gate. Nonactual favorable arithmetic remains nonactual.

The Phase 4 synthesis then made that lifecycle canonical. Its claim matrix states which claims are falsified, preserved, non-evidence, or future-reopen conditions. Its manifest maps claim-support artifacts to generated outputs. The auditor fix strengthened that auditability contract by ensuring every claim support is listed in the manifest.

The robustness stress test challenged the negative result outside the reopen gate. It did not create a new evidence path. Under calibrated stronger-baseline assumptions, no tested physicalization target won. Favorable-plausible wins showed where future measured evidence might focus, but they did not alter current claims. Extreme counterfactual wins remained explicitly non-evidence.

The cumulative conclusion is stable: physicalization survives as bounded architecture and evidence-gating research, not as a current performance superiority claim.

## Open Questions

No actual measured production, shadow, or canary evidence has been ingested. The reopen pathway is ready to classify such evidence, but current artifacts remain synthetic, modeled, proxy, template, rehearsal, or hypothetical-control artifacts.

Production accelerator energy, latency, utilization, batching behavior, workload mix, and measured programmable-baseline terms remain unmeasured for a real candidate deployment.

The uncertainty protocol uses a normal-approximation upper confidence bound. Future measured evidence may require stronger distributional treatment if workloads are heavy-tailed, request classes are imbalanced, or instrumentation errors are non-normal.

Compiled Verilator simulation remains a future superseding check for the HDL prototype if local build tooling becomes available. Existing cycle 23-25 work did not depend on that compiled simulation path.

## References

[7] Mark Horowitz, "1.1 Computing's Energy Problem (and What We Can Do about It)," 2014 IEEE International Solid-State Circuits Conference Digest of Technical Papers (ISSCC), 2014. https://doi.org/10.1109/ISSCC.2014.6757323

[8] Mark Horowitz, "Computing's Energy Problem (and What We Can Do about It)," slide transcript/mirror of ISSCC 2014 energy table. https://doczz.net/doc/9135487/computing-s-energy-problem--and-what-we-can-do-about-it-

[9] NVIDIA, "NVIDIA H100 Tensor Core GPU," product specification page. https://www.nvidia.com/en-us/data-center/h100/

[10] MLCommons, "MLPerf Inference: Datacenter benchmark documentation," MLCommons. https://docs.mlcommons.org/inference/

## Appendix: Implementation Details

### Code Organization

Cycle 23 added `physicalized-weights/scripts/evidence_package_lifecycle.py` with 830 lines, `physicalized-weights/tests/test_evidence_package_lifecycle.py` with 155 lines, and `physicalized-weights/docs/evidence_package_lifecycle_state_machine.md` with 41 lines.

Cycle 24 added `physicalized-weights/scripts/build_phase4_reopen_synthesis.py` with 566 lines, `physicalized-weights/tests/test_phase4_reopen_synthesis.py` with 162 lines, and `physicalized-weights/docs/phase4_reopen_lifecycle_synthesis.md` with 71 lines.

Cycle 25 added `physicalized-weights/scripts/target_robustness_stress.py` with 485 lines, `physicalized-weights/tests/test_target_robustness_stress.py` with 119 lines, and `physicalized-weights/docs/target_robustness_stress_test.md` with 35 lines.

The workspace manifest was updated as a snapshot. It now reports 27 authored research scripts with 11,773 lines, 24 stdlib test files with 3,364 lines, 4 HDL/support files with 241 lines, and 26 authored research docs or diagram sources with 1,634 lines.

### Generated Figures

Cycle 23 generated `physicalized-weights/data/evidence_package_lifecycle_flow.png`, a valid 980 x 430 RGB PNG.

Cycle 24 generated `physicalized-weights/data/phase4_reopen_lifecycle_flow.png`, a valid 980 x 430 RGB PNG.

Cycle 25 generated `physicalized-weights/data/target_robustness_frontier.png`, a valid 980 x 430 RGB PNG.

### Test Results

The Cycle 23 worker and auditor ran:

```bash
python3 physicalized-weights/scripts/evidence_package_lifecycle.py
python3 physicalized-weights/tests/test_evidence_package_lifecycle.py
file physicalized-weights/data/evidence_package_lifecycle_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

The Cycle 24 worker and auditor ran:

```bash
python3 physicalized-weights/scripts/build_phase4_reopen_synthesis.py
python3 physicalized-weights/tests/test_phase4_reopen_synthesis.py
file physicalized-weights/data/phase4_reopen_lifecycle_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

The Cycle 25 worker and auditor ran:

```bash
python3 physicalized-weights/scripts/target_robustness_stress.py
python3 physicalized-weights/tests/test_target_robustness_stress.py
file physicalized-weights/data/target_robustness_frontier.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

During this report pass, `promise_check` exited 0 with `events: 69, plan milestones: 25`. It continued to warn about pre-existing orphan cycle report artifacts. `org_check` exited 0 and continued to warn about the root prompt and live log files.

### Session References

| Cycle | Role | Session ID |
|---:|---|---|
| 23 | Researcher | `f445a470-5d93-40bd-8465-452a0f674d07` |
| 23 | Worker | `d9d46fd4-3e13-47c6-9f17-752ae9417b21` |
| 23 | Auditor | `ee383376-449c-4250-8f0c-737202114972` |
| 24 | Researcher | `dca6756c-6344-44fa-be64-0480edf54bf6` |
| 24 | Worker | `6d1b7541-55da-45fc-ac1d-513c8d929a0a` |
| 24 | Auditor | `e77bd625-5471-4a45-aec9-bad160f72169` |
| 25 | Researcher | `52d5ce28-d56b-47f3-b0d0-a5f52076e030` |
| 25 | Worker | `48008c2a-d41f-4e0a-837a-87d7af85b671` |
| 25 | Auditor | `bfffac8e-0f4e-4325-9566-f242e65ed725` |

### Cross-Reference Map

`evidence_acquisition_readiness.py`, `evidence_pack_template_dryrun.py`, `evidence_pack_intake_rehearsal.py`, `evidence_pack_replay.py`, `reopen_thresholds.py`, and `reopen_uncertainty_protocol.py` feed `evidence_package_lifecycle.py`.

`evidence_package_lifecycle.py` feeds `build_phase4_reopen_synthesis.py`, which updates the canonical claim matrix, manifest, Phase 4 summary, final synthesis, and reproducibility record.

`target_scoring.py`, `stronger_baseline_model.py`, and `build_phase4_reopen_synthesis.py` feed `target_robustness_stress.py`, which stress-tests calibrated, favorable-plausible, extreme-counterfactual, and special-control target cases without creating a new reopen gate.
