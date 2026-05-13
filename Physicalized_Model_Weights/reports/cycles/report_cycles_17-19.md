---
title: "Physicalized Model Weights - cycles 17-19"
date: "2026-05-13"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Physicalized Model Weights - cycles 17-19

## Abstract

Cycles 17-19 completed the Phase 3 evidence-handling layer for the physicalized-model-weights study. The work did not reopen the Phase 2 downgrade. Instead, it made the future reopen path more operational: candidate evidence can now be packaged, replayed, synthesized across the full gate chain, and screened before collection.

The central conclusion remains unchanged: physicalized safety/filter hardware is not currently a demonstrated performance or economic winner over the stronger programmable accelerator baseline. A future challenge to that conclusion requires a measured, privacy-safe, provenance-attested production, shadow, or canary package that crosses the quantitative threshold under identical workload accounting.

## Introduction

Earlier cycles downgraded the safety/filter physicalization claim after stronger programmable baselines erased the modeled advantage. Cycles 14-16 then built the reopen gate: quantitative thresholds, trace-ingestion admissibility, and an end-to-end pipeline that blocks synthetic, proxy, privacy-risk, and non-crossing evidence.

Cycles 17-19 built the next layer above that gate. The question shifted from "what would reopen the claim?" to "how would future evidence be packaged, synthesized, and screened before collection?" The answer is a three-part chain:

1. Cycle 17, `M-EVIDENCEPACK-1`: replayable evidence-package manifests.
2. Cycle 18, `M-PHASE3-SYNTH-1`: campaign-level Phase 3 reopen-pathway synthesis.
3. Cycle 19, `M-ACQUIRE-1`: pre-collection readiness screening for proposed shadow or canary evidence designs.

The public calibration context from earlier Phase 2 work still depends on references [7]-[10]. No new external references were added during cycles 17-19.

## Approach

The work followed the validated Phase 3 gate contract. A future reopen candidate must satisfy the full conjunction:

```text
valid_package AND hash_match AND schema_compatible AND known_threshold_scenario
AND valid_trace AND admissible_ingestion_path AND measured_terms
AND production_or_shadow_or_canary_source AND provenance_attestation
AND privacy_attestation AND threshold_crossed
```

The key rule is that readiness, packaging, replay, and synthesis are not themselves evidence. They are controls around evidence. Current artifacts remain synthetic, proxy, fixture-based, or pre-collection plans, so the generated summaries continue to report `actual_reopen_candidate_count = 0`.

## Findings

### Cycle 17: Replayable Evidence Packs

Cycle 17 created `M-EVIDENCEPACK-1`, a manifest and replay harness for future evidence packages. The researcher session `66239872-6d3d-4751-be97-429cf1e3ec64` defined the need: future trace evidence should be replayable from a manifest rather than manually assembled from files and declarations.

The worker artifacts created the package contract:

- `physicalized-weights/scripts/evidence_pack_replay.py`
- `physicalized-weights/data/evidence_pack_manifest_schema.json`
- five privacy-safe manifest fixtures
- `physicalized-weights/data/evidence_pack_replay_results.csv`
- `physicalized-weights/data/evidence_pack_replay_summary.json`
- `physicalized-weights/docs/evidence_pack_replay_harness.md`

The replay harness checks manifest completeness, trace file hash, schema compatibility, privacy attestation, provenance attestation, ingestion path, evidence source type, measurement status, threshold scenario mapping, and downstream `M-PIPELINE-1` status.

![Evidence-pack replay outcomes showing that package integrity, provenance, measured-source eligibility, ingestion admissibility, and threshold crossing are conjunctive gates before any actual reopen candidate can exist.](physicalized-weights/data/evidence_pack_replay_flow.png)

The generated summary reports:

| Measure | Value |
|---|---:|
| Evidence packs | 5 |
| Valid packages | 3 |
| Invalid packages | 2 |
| Threshold-not-evaluated packages | 2 |
| Actual reopen candidates | 0 |

The final package decisions were:

| Decision | Count |
|---|---:|
| `package_invalid` | 2 |
| `valid_but_insufficient` | 1 |
| `threshold_evaluable_not_crossed` | 1 |
| `synthetic_counterfactual_crossed` | 1 |

The auditor session `d5a1782b-531f-4640-8654-aa15e977b8b5` found and fixed one moderate issue: an unknown but internally consistent `threshold_scenario_id` could initially reach downstream evaluation. The fix made unknown threshold scenarios hard package blockers before the pipeline runs. The auditor appended validation event `4d96c2f7-2980-4c4b-9df9-3a63ee0c4d9f`.

A record gap remains: the provided cycle-session list did not include a Cycle 17 worker session ID. The workspace artifacts and ledger contain the worker-built `M-EVIDENCEPACK-1` outputs, and the auditor validated them.

### Cycle 18: Phase 3 Reopen Synthesis

Cycle 18 created `M-PHASE3-SYNTH-1`, a campaign-level synthesis of the Phase 3 reopen path. The researcher session `46216529-e25f-40e9-ba98-e212710f2de1` specified that the project needed one consolidated record across six validated milestones:

- `M-MEASURE-1`
- `M-TRACE-1`
- `M-REOPEN-1`
- `M-INGEST-1`
- `M-PIPELINE-1`
- `M-EVIDENCEPACK-1`

The worker session `35bcf591-c78b-4e62-b557-a774b51f29a8` built:

- `physicalized-weights/scripts/build_phase3_reopen_synthesis.py`
- `physicalized-weights/tests/test_phase3_reopen_synthesis.py`
- `physicalized-weights/docs/phase3_reopen_pathway_summary.md`
- `physicalized-weights/data/phase3_reopen_claim_matrix.csv`
- `physicalized-weights/data/phase3_reopen_manifest.csv`
- `physicalized-weights/data/phase3_reopen_summary.json`
- `physicalized-weights/data/phase3_reopen_evidence_flow.png`

It also updated `physicalized-weights/docs/final_synthesis.md` and `physicalized-weights/docs/reproducibility.md`.

![Phase 3 evidence chain from measurement requirements through evidence-pack replay, showing that all current committed artifacts preserve the Phase 2 downgrade and only a measured eligible threshold-crossing package can reopen.](physicalized-weights/data/phase3_reopen_evidence_flow.png)

The synthesis reports:

| Measure | Value |
|---|---:|
| Phase 3 claims | 14 |
| Current artifacts reopen | `false` |
| Actual reopen candidates | 0 |
| Ingestion actual reopened count | 0 |

It identifies the blocked evidence classes as synthetic, proxy/local, vendor-only, privacy-risk, stale-hash, unknown-threshold, and non-crossing measured packages.

The auditor session `a84097a7-f85e-4ffd-b083-a270722e31ff` validated the synthesis with no moderate or critical findings. The validation event was `682459e5-9bfe-49c6-a484-90f44a6d2045`.

### Cycle 19: Evidence-Acquisition Readiness

Cycle 19 created `M-ACQUIRE-1`, a pre-collection readiness screen for proposed production, shadow, or canary evidence designs. The researcher session `12520363-b3af-4d1a-ad15-d2c6d6afe691` framed the problem: before data collection begins, a proposed design should be rejected if it would inevitably fail the evidence-pack or reopen gates.

The worker session `e9def7a0-22bf-4e53-8126-23aa177997be` built:

- `physicalized-weights/docs/evidence_acquisition_readiness.md`
- `physicalized-weights/data/evidence_acquisition_readiness_criteria.csv`
- `physicalized-weights/data/evidence_acquisition_designs.csv`
- `physicalized-weights/scripts/evidence_acquisition_readiness.py`
- `physicalized-weights/tests/test_evidence_acquisition_readiness.py`
- `physicalized-weights/data/evidence_acquisition_readiness_results.csv`
- `physicalized-weights/data/evidence_acquisition_readiness_summary.json`
- `physicalized-weights/data/evidence_acquisition_readiness_matrix.png`

![Readiness classification for proposed evidence-acquisition designs, separating admissible future collection plans from inadmissible, repair-required, and diagnostic-only designs before any data can affect the Phase 2 downgrade.](physicalized-weights/data/evidence_acquisition_readiness_matrix.png)

The readiness evaluator covers 20 criteria and 10 proposed designs. The final classification is:

| Readiness Class | Count |
|---|---:|
| `ready_to_collect_candidate` | 2 |
| `repair_required_before_collection` | 1 |
| `inadmissible_design` | 5 |
| `diagnostic_only` | 2 |
| `actual_reopen_candidate` | 0 |

The two collection-ready designs are `shadow_dual_run_full_instrumentation` and `canary_ab_full_instrumentation`. They are ready to collect candidate evidence, not evidence themselves. `shadow_dual_run_missing_energy` is repairable before collection because measured energy can still be added. Missing counterfactuals, privacy-risk raw content, single-path logs, unknown threshold mapping, missing provenance, vendor/proxy-only data, and synthetic scaled replay are blocked or diagnostic-only.

The auditor session `fa58983c-dd22-4f8c-a936-285cadbca2ec` found and fixed one moderate issue. The `vendor_benchmark_plus_local_proxy` fixture had been modeled as scaled synthetic rather than vendor/proxy-only, so it did not exercise the intended admissible-ingestion-path gate. The auditor corrected the fixture, added a regression assertion, regenerated outputs, and appended validation event `708fa42e-186a-43d3-80ac-62214fd99241`.

## Discussion

Cycles 17-19 did not add new hardware evidence. They added controls around future evidence. That distinction is the main result.

The evidence-pack replay layer makes future claims reproducible by binding a trace file, hash, schema version, source type, ingestion path, threshold scenario, and attestations into one package. The Phase 3 synthesis layer makes the full reopen chain readable from one place. The acquisition-readiness layer lets operators reject bad collection designs before collecting unusable data.

The conclusion remains conservative. Current committed artifacts contain no measured production/shadow/canary package that is privacy-safe, provenance-attested, admissible, fully measured, and threshold-crossing. Therefore, the Phase 2 downgrade remains in force.

## Open Questions

The main open question is operational: whether a real production, shadow, or canary collection can be run under the required controls without violating privacy, provenance, or identical-workload accounting.

The technical gate is now explicit. What remains missing is measured evidence: hybrid and programmable accelerator latency, energy, utilization, fallback, audit, update, rollback, health, and drift accounting over the same requests and policy window.

Compiled Verilator simulation remains a future superseding check for the small HDL prototype if `make` and a C++ compiler become available locally. That issue is separate from the Phase 3 evidence gate.

## References

[7] Mark Horowitz, "1.1 Computing's Energy Problem (and What We Can Do about It)," 2014 IEEE International Solid-State Circuits Conference Digest of Technical Papers (ISSCC), 2014. https://doi.org/10.1109/ISSCC.2014.6757323

[8] Mark Horowitz, "Computing's Energy Problem (and What We Can Do about It)," slide transcript/mirror of ISSCC 2014 energy table. https://doczz.net/doc/9135487/computing-s-energy-problem--and-what-we-can-do-about-it-

[9] NVIDIA, "NVIDIA H100 Tensor Core GPU," product specification page. https://www.nvidia.com/en-us/data-center/h100/

[10] MLCommons, "MLPerf Inference: Datacenter benchmark documentation," MLCommons. https://docs.mlcommons.org/inference/

## Appendix: Implementation Details

### Code Organization

Cycle 17 added `evidence_pack_replay.py` with 482 lines, `test_evidence_pack_replay.py` with 234 lines, and `evidence_pack_replay_harness.md` with 27 lines.

Cycle 18 added `build_phase3_reopen_synthesis.py` with 630 lines, `test_phase3_reopen_synthesis.py` with 138 lines, and `phase3_reopen_pathway_summary.md` with 75 lines.

Cycle 19 added `evidence_acquisition_readiness.py` with 298 lines, `test_evidence_acquisition_readiness.py` with 116 lines, and `evidence_acquisition_readiness.md` with 42 lines.

`MANIFEST.md` was updated as the current workspace snapshot. It now reports 21 authored research scripts, 18 test files, 20 research docs and diagram sources, 51 ledger events, and 19 plan milestones.

### Generated Data and Figures

Cycle 17 generated the evidence-pack manifest schema, five manifest fixtures, replay results CSV, replay summary JSON, and `evidence_pack_replay_flow.png` at 900 x 460.

Cycle 18 generated the Phase 3 claim matrix, manifest, summary JSON, and `phase3_reopen_evidence_flow.png` at 980 x 500.

Cycle 19 generated readiness criteria, acquisition design fixtures, readiness results CSV, summary JSON, and `evidence_acquisition_readiness_matrix.png` at 960 x 440.

### Test Results

Validated commands recorded for Cycle 17:

```bash
python3 physicalized-weights/scripts/evidence_pack_replay.py
python3 physicalized-weights/tests/test_evidence_pack_replay.py
file physicalized-weights/data/evidence_pack_replay_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

Validated commands recorded for Cycle 18:

```bash
python3 physicalized-weights/scripts/build_phase3_reopen_synthesis.py
python3 physicalized-weights/tests/test_phase3_reopen_synthesis.py
python3 physicalized-weights/tests/test_final_synthesis.py
file physicalized-weights/data/phase3_reopen_evidence_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

Validated commands recorded for Cycle 19:

```bash
python3 physicalized-weights/scripts/evidence_acquisition_readiness.py
python3 physicalized-weights/tests/test_evidence_acquisition_readiness.py
file physicalized-weights/data/evidence_acquisition_readiness_matrix.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

Reporter sanity checks after updating `MANIFEST.md`:

```bash
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

Both exited successfully. Remaining warnings are pre-existing: orphan report artifacts under `reports/cycles/` and root-file warnings for `physicalized_model_weights_long_exposure_prompt.md` and `physicalized_weights_long_exposure_live.log`.

### Session References

Cycle 17 sources:

- Researcher: `66239872-6d3d-4751-be97-429cf1e3ec64`
- Auditor: `d5a1782b-531f-4640-8654-aa15e977b8b5`
- Worker session ID: not provided in the cycle-session input; artifacts and ledger entries were present and auditor-validated.

Cycle 18 sources:

- Researcher: `46216529-e25f-40e9-ba98-e212710f2de1`
- Worker: `35bcf591-c78b-4e62-b557-a774b51f29a8`
- Auditor: `a84097a7-f85e-4ffd-b083-a270722e31ff`

Cycle 19 sources:

- Researcher: `12520363-b3af-4d1a-ad15-d2c6d6afe691`
- Worker: `e9def7a0-22bf-4e53-8126-23aa177997be`
- Auditor: `fa58983c-dd22-4f8c-a936-285cadbca2ec`

### Cross-Reference Map

`M-PIPELINE-1` feeds `M-EVIDENCEPACK-1`: the evidence-pack replay harness packages traces, hashes, attestations, source declarations, ingestion paths, and threshold scenarios before invoking the downstream gate.

`M-EVIDENCEPACK-1` feeds `M-PHASE3-SYNTH-1`: the synthesis builder integrates evidence-pack replay with measurement, trace validation, thresholds, ingestion admissibility, and pipeline results.

`M-PHASE3-SYNTH-1` feeds `M-ACQUIRE-1`: validated Phase 3 gates become readiness criteria for proposed future acquisition designs.

`M-ACQUIRE-1` preserves the final active rule: a collection plan may be ready, repairable, inadmissible, or diagnostic-only, but no plan is evidence until measured trace data is packaged and passes the full Phase 3 conjunction.
