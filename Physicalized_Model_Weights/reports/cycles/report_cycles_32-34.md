---
title: "Physicalized Model Weights - cycles 32-34"
date: "2026-05-13"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Physicalized Model Weights - cycles 32-34

## Abstract

Cycles 32-34 continued the post-closure public-baseline branch of the physicalized model weights campaign. Cycle 32 completed `M-PUBLICBASE-2`, a conservative mapping from primary MLCommons MLPerf Inference v6.0 public result metadata into the campaign's programmable-baseline prior. Cycle 33 completed `M-PUBLICBASE-SYNTH-1`, which integrated that public-baseline refresh into the canonical final synthesis and reproducibility record. Cycle 34 attempted no new artifact and was audited as `PIVOT`, because the campaign had reached a trigger-gated state and further watch-state restatement would be a null cycle.

The scientific endpoint did not change. Public benchmark evidence can update or strengthen the programmable-baseline prior `B`, meaning the best programmable baseline used for comparison. It does not supply measured hybrid total `H`, meaning measured physicalized-hybrid cost or energy under the same workload accounting. The Phase 2 downgrade remains preserved, the Phase 4 reopen condition remains unchanged, and the current counters remain zero or false: no current physicalized superiority claim, no actual reopen candidate, no new reopen gate, and no current artifact that reopens the claim.

## Introduction

Earlier cycles had already closed the main campaign under current evidence: full fixed frontier-model physicalization remained rejected, and the bounded safety/filter physicalization path remained useful only as an architecture, verification, and evidence-gating study. Cycle 31 then found that official public MLPerf Inference benchmark evidence had advanced to v6.0, published on 2026-04-01, and recommended a future programmable-baseline refresh using primary MLCommons material rather than vendor-only context [10]-[14].

Cycles 32-34 addressed that recommendation. The goal was narrow: determine how official public benchmark data should affect the programmable-baseline side of the comparison without treating public benchmark rows as measured hybrid production, shadow, or canary evidence. This distinction matters because the campaign's reopen rule requires lifecycle-valid measured hybrid evidence under the same accounting frame, not merely stronger public accelerator benchmark results.

## Approach

The work proceeded in three steps.

First, cycle 32 implemented a primary public-data mapping. The worker built `physicalized-weights/scripts/public_baseline_prior_refresh.py`, which ingested MLCommons v6.0 result metadata from the primary `inference_results_v6.0` repository and produced a small auditable subset. The mapping classified each row by campaign relevance: throughput prior, energy prior, software-runtime context, workload comparability, direct energy calibration usability, and safety-filter workload comparability.

Second, cycle 33 integrated the result into the canonical reader-facing record. The worker built `physicalized-weights/scripts/build_public_baseline_synthesis.py`, generated a synthesis addendum, updated `final_synthesis.md` and `reproducibility.md`, and emitted a claim matrix separating supported public recency from unsupported direct energy calibration and unsupported safety-filter workload comparability.

Third, cycle 34 checked whether any new trigger justified further research. No new measured hybrid evidence, changed compiled-HDL capability, materially new public-data mapping requirement, or new handoff artifact class appeared. The auditor therefore marked the cycle `PIVOT`, not `VALIDATED`, because a correct watch-state confirmation still produced no new artifact or analytical result.

## Findings

### Cycle 32: Public Baseline Prior Refresh

Cycle 32's researcher session (`3944693f-7c5e-4450-af44-aa31180d44b7`) scoped `M-PUBLICBASE-2` as a conservative primary MLPerf-to-campaign mapping. The worker session (`1d992063-efdd-4d4f-9c7e-4a232e6df047`) implemented the package, and the auditor session (`13b0ca59-15b6-47af-bfdb-7afc976b50e6`) validated it without source-code fixes.

The key output was `physicalized-weights/data/public_baseline_prior_refresh_summary.json`. It recorded:

| Field | Value |
|---|---:|
| `raw_primary_rows_available` | 520 |
| `primary_mlcommons_rows_ingested` | 12 |
| `throughput_prior_rows` | 12 |
| `direct_energy_calibration_rows` | 0 |
| `safety_filter_direct_workload_rows` | 0 |
| `energy_values_inferred_from_throughput_only` | 0 |
| `refresh_decision` | `strengthen_programmable_null` |
| `programmable_null_effect` | `strengthened_or_preserved` |
| `phase2_downgrade_preserved` | `true` |
| `current_superiority_claim_count` | 0 |
| `actual_reopen_candidate_count` | 0 |
| `new_reopen_gate_count` | 0 |
| `current_artifacts_reopen` | `false` |

The 12-row subset came from primary MLCommons v6.0 result metadata [13]. Rows covered `deepseek-r1` and `gpt-oss-120b` benchmark entries across Server, Offline, and Interactive scenarios, with submitted systems using NVIDIA datacenter accelerator families. The selected rows exposed throughput-like performance fields and units, such as tokens per second, but did not expose comparable power or energy fields usable for campaign energy-per-request calibration.

The campaign mapping therefore separated what could be used from what could not. Throughput rows were accepted only as bounded public programmable-system strength context. Energy priors were not updated, because the selected public rows lacked explicit comparable energy-per-request fields. Safety-filter workload comparability stayed blocked, because MLPerf benchmark workloads are not the campaign's safety/filter production, shadow, or canary workload with feature extraction, audit, fallback, update, utilization, energy, and latency accounting.

![Conservative mapping from public MLPerf v6.0 programmable-baseline evidence to campaign model terms and directional effect on the null hypothesis.](physicalized-weights/data/public_baseline_prior_refresh.png)

The auditor reproduced the script, tests, PNG check, and campaign validators. Direct tests passed, including guards against inferring energy from throughput-only rows, using vendor-secondary rows as primary calibration, and allowing public benchmark rows to create actual reopen candidates. The auditor decision was `VALIDATED`.

### Cycle 33: Public Baseline Synthesis Addendum

Cycle 33's researcher session (`e13f7571-589e-41e2-898b-4c4aed0e1638`) scoped `M-PUBLICBASE-SYNTH-1` as a synthesis integration cycle, not another data acquisition cycle. The worker session (`bd7d124d-1f68-4a7c-9afe-19ba60aa0416`) built the synthesis package, and the auditor session (`4c297790-6069-4e4f-bcaa-2dcf9aeff5c2`) validated it without source-code fixes.

The synthesis integrated `M-PUBLICBASE-1`, `M-PUBLICBASE-2`, and `M-CLOSURE-1`. Its summary file, `physicalized-weights/data/public_baseline_synthesis_summary.json`, recorded:

| Field | Value |
|---|---:|
| `public_baseline_refresh_integrated` | `true` |
| `latest_mlperf_inference_release` | `MLPerf Inference v6.0` |
| `latest_mlperf_inference_publication_date` | `2026-04-01` |
| `primary_mlcommons_rows_ingested` | 12 |
| `raw_primary_rows_available` | 520 |
| `throughput_prior_rows` | 12 |
| `direct_energy_calibration_rows` | 0 |
| `safety_filter_direct_workload_rows` | 0 |
| `programmable_null_effect` | `strengthened_or_preserved` |
| `phase2_downgrade_preserved` | `true` |
| `phase4_reopen_condition_unchanged` | `true` |
| `current_superiority_claim_count` | 0 |
| `actual_reopen_candidate_count` | 0 |
| `new_reopen_gate_count` | 0 |
| `current_artifacts_reopen` | `false` |

The claim matrix in `physicalized-weights/data/public_baseline_synthesis_claim_matrix.csv` separated seven claim dispositions:

| Claim | Disposition |
|---|---|
| Public MLPerf recency | supported |
| Programmable null strength | strengthened or preserved |
| Direct energy calibration from public MLPerf | unsupported |
| Safety-filter workload comparability | unsupported |
| Phase 2 downgrade after public refresh | preserved |
| Physicalized reopen from public benchmark | falsified as public-benchmark-only |
| Future model refresh scope | bounded future work |

The synthesis restated the full Phase 4 reopen condition as the only path for future physicalized superiority:

```text
valid_package && hash_match && schema_compatible && known_threshold_scenario && valid_trace && admissible_ingestion_path && measured_terms && production_or_shadow_or_canary_source && provenance_attestation && privacy_attestation && nonzero_request_volume && nonzero_accepted_fast_path_volume && measured_best_programmable_baseline && threshold_crossed && UCB_alpha(H - B) < 0 && lifecycle_terminal_state=actual_reopen_candidate
```

Here `UCB_alpha(H - B) < 0` is the uncertainty-aware condition that the measured hybrid total `H` must beat the measured best programmable baseline `B` with a durable upper-confidence-bound margin. Cycle 33 did not change this rule.

![Public programmable-baseline refresh flow from official MLPerf recency through conservative prior mapping to strengthened programmable null and unchanged hybrid reopen boundary.](physicalized-weights/data/public_baseline_synthesis_flow.png)

The auditor reproduced the synthesis builder, direct tests, PNG check, `promise_check`, and `org_check`. Direct tests passed. The auditor decision was `VALIDATED`.

### Cycle 34: Trigger-Gated Watch State and Pivot

Cycle 34's researcher session (`ee8af970-0595-4541-9217-d96d4ad4bb54`) did not open a new scientific sub-topic. It stated that `M-PUBLICBASE-SYNTH-1` was validated and that future work should begin only if a concrete trigger appeared: lifecycle-valid measured hybrid production/shadow/canary evidence, changed compiled-HDL capability, a genuinely new handoff artifact class, or a materially different primary-data mapping requirement.

The worker session (`6a6ec47c-8fe0-4faf-a3c5-cebf0dc990ee`) built no new artifact. It ran the directive read, checked the ledger tail, and ran `promise_check`. The result confirmed that the latest substantive audited milestone remained `M-PUBLICBASE-SYNTH-1`, with `events: 89` and `plan milestones: 33`.

The auditor session (`b8c8ae98-269f-469d-980c-34a1d7f0be57`) agreed with the substantive state but marked the cycle `PIVOT`. The rationale was procedural: a null-cycle should not be marked `VALIDATED` because it produced no artifact, milestone, evidence class, figure, or new analytical result. The correct next state is to stop repeating conditional-watch confirmation and proceed only when a trigger-backed scope exists.

## Discussion

Cycles 32 and 33 completed the public-baseline refresh path recommended by cycle 31. The public MLPerf v6.0 data are useful because they show current programmable accelerator benchmark strength in a primary public source. The campaign incorporated that evidence as a bounded prior about programmable baselines, not as direct safety/filter workload evidence.

The practical effect is conservative. If public programmable systems are stronger than the campaign's older baseline assumptions, the null hypothesis against physicalization becomes no weaker and may become stronger. If the public data are not directly comparable, the existing energy and workload-specific terms remain unchanged. Neither case improves the physicalized hybrid claim.

Cycle 34 is important because it records a boundary on autonomous continuation. The campaign has enough closure, archive, invariant, toolchain, recency, prior-refresh, and synthesis artifacts for the current evidence state. Additional cycles should not restate the endpoint unless a concrete trigger appears.

## Open Questions

The remaining questions are trigger-dependent rather than open analytical gaps from these cycles.

- Measured hybrid evidence: no lifecycle-valid production, shadow, or canary evidence package has been ingested.
- Direct energy calibration: the selected primary MLCommons rows did not provide comparable energy-per-request fields for the campaign workload.
- Workload comparability: public MLPerf scenarios do not directly measure the campaign's safety/filter workload.
- Compiled HDL simulation: previous toolchain work found Verilator, Yosys, and Graphviz usable, but compiled Verilator simulation remained blocked by missing `make` and C++ compiler support.
- Future model refresh: a full calibrated programmable-baseline model rebuild remains separate work and would need explicit mapping from primary public data into campaign model terms.

## References

[10] MLCommons, "MLPerf Inference: Datacenter benchmark documentation," MLCommons. https://docs.mlcommons.org/inference/

[11] MLCommons, "MLPerf Inference v6.0 Results," MLCommons, 2026. https://mlcommons.org/2026/04/mlperf-inference-v6-0-results/

[12] MLCommons, "MLPerf Inference v5.1 Results," MLCommons, 2025. https://mlcommons.org/2025/09/mlperf-inference-v5-1-results/

[13] MLCommons, "MLPerf Inference Results v6.0," GitHub, 2026. https://github.com/mlcommons/inference_results_v6.0

[14] NVIDIA, "MLPerf AI Benchmarks," NVIDIA. https://www.nvidia.com/en-us/data-center/resources/mlperf-benchmarks/

## Appendix: Implementation Details

### Code Organization

Cycle 32 added the public-baseline prior-refresh package:

| File | Lines | Purpose |
|---|---:|---|
| `physicalized-weights/scripts/public_baseline_prior_refresh.py` | 527 | Ingests primary MLCommons v6.0 metadata and maps public benchmark rows to campaign baseline-prior terms. |
| `physicalized-weights/tests/test_public_baseline_prior_refresh.py` | 133 | Tests no energy inference, endpoint counters, vendor-secondary exclusion, and mapping fields. |
| `physicalized-weights/docs/public_baseline_prior_refresh.md` | 66 | Documents sources, fields, campaign mappings, non-mappings, and reproduction commands. |

Cycle 32 generated:

| File | Rows or status |
|---|---:|
| `physicalized-weights/data/public_baseline_mlperf_v6_subset.csv` | 12 rows |
| `physicalized-weights/data/public_baseline_campaign_mapping.csv` | 72 rows |
| `physicalized-weights/data/public_baseline_prior_refresh.csv` | 5 rows |
| `physicalized-weights/data/public_baseline_prior_refresh_summary.json` | validated summary |
| `physicalized-weights/data/public_baseline_prior_refresh.png` | 960 x 420 RGB PNG |

Cycle 33 added the public-baseline synthesis package:

| File | Lines | Purpose |
|---|---:|---|
| `physicalized-weights/scripts/build_public_baseline_synthesis.py` | 399 | Builds the synthesis addendum, claim matrix, manifest, summary, and flow figure. |
| `physicalized-weights/tests/test_public_baseline_synthesis.py` | 142 | Tests claim rows, endpoint counters, absent direct calibration, and unchanged Phase 4 condition. |
| `physicalized-weights/docs/public_baseline_refresh_synthesis.md` | 36 | Summarizes public-baseline recency, prior refresh, and unchanged reopen boundary. |

Cycle 33 generated or updated:

| File | Rows or status |
|---|---:|
| `physicalized-weights/data/public_baseline_synthesis_claim_matrix.csv` | 7 rows |
| `physicalized-weights/data/public_baseline_synthesis_manifest.csv` | 11 rows |
| `physicalized-weights/data/public_baseline_synthesis_summary.json` | validated summary |
| `physicalized-weights/data/public_baseline_synthesis_flow.png` | 980 x 420 RGB PNG |
| `physicalized-weights/docs/final_synthesis.md` | updated |
| `physicalized-weights/docs/reproducibility.md` | updated |

Cycle 34 generated no new script, data file, report, figure, milestone, or ledger event.

### Test Results

Cycle 32 validation commands reported:

```text
python3 physicalized-weights/scripts/public_baseline_prior_refresh.py
python3 physicalized-weights/tests/test_public_baseline_prior_refresh.py
file physicalized-weights/data/public_baseline_prior_refresh.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

Observed results: 8 direct tests passed; the PNG was valid; `promise_check` exited 0 with known orphan cycle-report warnings; `org_check` exited 0 with known root-file warnings.

Cycle 33 validation commands reported:

```text
python3 physicalized-weights/scripts/build_public_baseline_synthesis.py
python3 physicalized-weights/tests/test_public_baseline_synthesis.py
file physicalized-weights/data/public_baseline_synthesis_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

Observed results: 8 direct tests passed; the PNG was valid; post-auditor `promise_check` reported `events: 89, plan milestones: 33`; `org_check` exited 0 with known root-file warnings.

For this reporter pass, `MANIFEST.md` was updated to include cycle 32-33 artifacts. Reporter validation then observed:

```text
promise_check: exit 0, events: 89, plan milestones: 33
org_check: exit 0
MANIFEST.md: 193 lines, no "## Key Files" section to preserve
```

Known warnings remained limited to orphan historical cycle reports under `reports/cycles/` and root run-management files.

### Manifest Snapshot

The updated manifest records:

| Category | Count |
|---|---:|
| Authored research scripts | 35 |
| Authored research script lines | 15,311 |
| Authored tests | 32 |
| Authored test lines | 4,439 |
| Authored HDL/support files | 4 |
| Authored HDL/support lines | 241 |
| Authored research docs and diagram sources | 34 |
| Authored doc/source lines | 2,150 |
| Ledger events | 89 |
| Plan milestones | 33 |

Public-baseline-specific manifest values now include:

| Value | Count |
|---|---:|
| Public baseline source rows | 5 |
| Public baseline delta rows | 6 |
| MLCommons v6.0 subset rows | 12 |
| Raw primary rows available | 520 |
| Prior-refresh mapping rows | 72 |
| Direct energy calibration rows | 0 |
| Direct safety-filter workload rows | 0 |
| Synthesis claim rows | 7 |
| Synthesis manifest rows | 11 |

### Session References

| Cycle | Role | Session ID | Reported content |
|---|---|---|---|
| 32 | researcher | `3944693f-7c5e-4450-af44-aa31180d44b7` | Scoped `M-PUBLICBASE-2` as primary MLPerf-to-campaign prior refresh. |
| 32 | worker | `1d992063-efdd-4d4f-9c7e-4a232e6df047` | Built prior-refresh script, tests, docs, CSV/JSON/PNG artifacts. |
| 32 | auditor | `13b0ca59-15b6-47af-bfdb-7afc976b50e6` | Validated `M-PUBLICBASE-2` with no source-code fixes. |
| 33 | researcher | `e13f7571-589e-41e2-898b-4c4aed0e1638` | Scoped `M-PUBLICBASE-SYNTH-1` as synthesis integration. |
| 33 | worker | `bd7d124d-1f68-4a7c-9afe-19ba60aa0416` | Built synthesis addendum, claim matrix, manifest, summary, figure, and canonical doc updates. |
| 33 | auditor | `4c297790-6069-4e4f-bcaa-2dcf9aeff5c2` | Validated `M-PUBLICBASE-SYNTH-1` with no source-code fixes. |
| 34 | researcher | `ee8af970-0595-4541-9217-d96d4ad4bb54` | Marked state as trigger-gated with no new scientific sub-topic. |
| 34 | worker | `6a6ec47c-8fe0-4faf-a3c5-cebf0dc990ee` | Confirmed watch state without creating artifacts. |
| 34 | auditor | `b8c8ae98-269f-469d-980c-34a1d7f0be57` | Marked the null-cycle `PIVOT` and advised against further restatement cycles. |

### Cross-Reference Map

- `REFERENCES.md`, `public_baseline_sources.csv`, and MLCommons v6.0 `summary_results.json` feed `public_baseline_prior_refresh.py`.
- `public_baseline_prior_refresh.py` emits the MLPerf subset, campaign mapping, conservative refresh table, summary JSON, and prior-refresh figure.
- `public_baseline_prior_refresh_summary.json` feeds `build_public_baseline_synthesis.py` alongside `public_baseline_recency_summary.json`, `public_baseline_campaign_mapping.csv`, and `phase2_synthesis_summary.json`.
- `build_public_baseline_synthesis.py` emits the synthesis claim matrix, synthesis manifest, synthesis summary, and flow figure, and updates the canonical final synthesis and reproducibility records.
- The final campaign state routes future work through existing trigger classes only: lifecycle-valid measured hybrid evidence, changed compiled-HDL capability, materially different public primary-data mapping, or a genuinely new handoff artifact class.
