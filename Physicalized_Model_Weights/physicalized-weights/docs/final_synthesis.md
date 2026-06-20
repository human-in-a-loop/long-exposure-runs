---
created: 2026-05-13T04:44:00Z
cycle: 1
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-FINAL-1
---

# Final Synthesis: Physicalizing Model Weights Into Hardware

## Executive Conclusion

The defensible answer is conditional and narrow. Full frontier LLM dense weights should not be burned permanently into fixed hardware on the evidence from this first arc: update cadence, yield/repair, integration cost, stranded capital, dynamic context state, and optimized programmable baselines dominate the broad case. The strongest supported result is that physicalization is credible for a stable, bounded safety/filter classifier submodel only when it sits behind programmable fallback, signed update, audit, health, drift, and rollback controls.

Phase 2 supersedes the performance/economic part of that narrow positive result. `M-CAL-1`, `M-WORKLOAD-1`, and especially `M-SWBASE-2` show that, under current calibrated assumptions and equal workload accounting, hybrid physicalized safety/filter wins zero workload scenarios; the programmable accelerator wins nine of ten, and optimized software wins the zero-invocation control. The safety/filter block remains useful as an architecture and failure-mode prototype, but its current superiority over a strong programmable accelerator is falsified until measured production evidence reopens the case.

The central mechanism remains the amortization inequality from `M-TAX-1` and `M-MODEL-1`:

```text
N * (C_prog - C_phys) > C_fixed + C_update + C_yield + C_integration
```

If request volume is zero, there is no fixed-substrate win. If update cadence approaches weekly or daily, fixed weights lose unless they are reprogrammable enough to become a programmable accelerator. If optimized software/runtime work removes 20-50% of memory movement first, the physicalization threshold rises and many apparent wins disappear.

## Taxonomy Recap

`M-TAX-1` defined physicalization as moving a stable part of inference from programmable kernels and general memory into hardware structures whose storage, topology, movement, or compute behavior encodes the workload. The design space includes fixed digital logic, ROM-coded weights, SRAM/eDRAM resident weights, FPGA/eFPGA overlays, RISC-V/custom accelerators, chiplet or cartridge weight modules, analog in-memory arrays, photonic/mixed-signal paths, and hybrid fixed/programmed systems.

The taxonomy also separated static base weights, adapters, MoE experts, embeddings, routers, speculative draft models, attention/KV paths, tokenizers, hot subgraphs, and safety/verifier models. Static, high-volume, slow-update, approximation-tolerant slices remain candidates. Dynamic attention, training state, high-churn tenant fine-tunes, and full frontier dense weights remain anti-targets.

## Where The Null Survived

The null hypothesis survived most of the broad design space: optimized software, runtime, compiler, scheduler, caching, routing, quantization, and programmable-accelerator improvements capture many practical gains before fixed physicalization can amortize. `M-MODEL-1` and `M-BASE-1` modeled unoptimized programmable inference, software-optimized inference, programmable accelerators, fixed digital weights, analog in-memory, and hybrid physicalized submodels. In the sampled grid, software-optimized and programmable-accelerator baselines won 352 of 560 summarized winner cases, while fixed digital won 208 and analog/hybrid won none under default penalties.

Dominant variables were request volume before update, software memory savings, fixed substrate cost, update interval, analog conversion overhead, yield/repair factor, fallback/accuracy penalty, and utilization. Those are exactly the variables that punish broad fixed-weight claims.

## Target And Anti-Target Ranking

`M-TARGET-1` scored 10 candidates and 5 anti-targets. The top target was fixed or semi-fixed safety/filter classifier submodels with score 3.775, just ahead of small always-on wake/router models. The recommended target was selected because it is small, repeatedly invoked, isolated from main-model generation, and compatible with conservative fallback.

The strongest anti-target was the intuitive but weak claim that full frontier LLM dense weights should be fixed permanently. Its score was 1.377 despite apparent per-request energy upside, because update cadence, yield, repair, model churn, and programmable baselines dominate.

## Hybrid Architecture Summary

`M-ARCH-1` proposed a host-controlled or RISC-V-compatible memory-mapped safety/filter classifier accelerator. The fixed block owns only deterministic inference over bounded features and a selected policy slot. The host/runtime owns feature construction, policy selection, fallback dispatch, final action, audit persistence, and update orchestration.

The open-architecture path is credible as a register-level interface that can be driven by a host, PCIe/CXL/MMIO device, SoC peripheral, or RISC-V management core. RISC-V is attractive because its ISA and specifications are public [1], [2], but the architecture does not depend on proprietary control instructions and does not assume RISC-V is automatically optimal.

## Prototype And HDL Closure

`M-PROTO-1` implemented a tiny 8-feature signed int8 fixed classifier with weights `[12, -7, 5, 9, -11, 4, 6, -3]`, bias `-10`, threshold `64`, and confidence as distance from threshold. The prototype generated 16 route cases: 6 physicalized fast path, 8 programmable fallback, and 2 fail-safe. The mixed case set intentionally overrepresents edge and failure states, so the route fractions are diagnostic rather than workload evidence.

The HDL core implements only fixed dot product, threshold compare, margin, and confidence. It contains no update, fallback, version, health, drift, audit, or policy logic. Yosys eval matched Python golden outputs on all 8 HDL vector cases, Verilator lint passed, Yosys synthesis/check reported no structural problems, and Graphviz netlist artifacts were generated.

Compiled Verilator simulation did not run because the local environment lacks `make` and a C++ compiler. The validated closure is therefore explicitly amended: `prototype_verification_closure.json` records `closure_status: validated` under `amended_lint_yosys_eval_synthesis`, not under compiled Verilator simulation. Reopen `M-PROTO-1` if compiled Verilator later disagrees, Python/Yosys vectors diverge, the HDL hash changes without regenerated evidence, or the HDL gains sequential state, memories, handshake timing, or mutable policy logic.

## Baselines That Remain Stronger

Software/runtime and programmable accelerators remain the dominant null for broad, high-churn, or dynamic inference components. They are stronger when model updates are frequent, when request volume is fragmented across tenants/SKUs, when KV/cache and live context dominate movement, when batching or caching closes memory-movement savings, or when safety policy requires exact programmable behavior.

Programmable accelerators also remain the right comparison for SRAM/eDRAM-resident weights, near-memory execution, and RISC-V-attached vector/matrix engines. A physicalized design that becomes field-reprogrammable, policy-rich, and broadly scheduled may still be useful, but it has become a programmable accelerator rather than a fixed-weight substrate.

## Evidence-Labeled Claim Table

| Claim | Evidence label | Supporting artifacts |
|---|---|---|
| Physicalization is a design spectrum, not one proposal to burn full LLMs into chips. | inferred | `docs/taxonomy_and_null.md` |
| Broad fixed frontier-model physicalization is not supported by this run. | modeled/inferred | `data/target_scores_summary.json`, `docs/target_ranking.md` |
| The break-even mechanism requires repeated per-request savings to exceed fixed, update, yield, integration, fallback, and audit costs. | modeled | `scripts/breakeven_model.py`, `data/breakeven_summary.json`, `scripts/symbolic_breakeven.wls` |
| Software/runtime and programmable-accelerator baselines win large regions of the sampled model space. | modeled | `data/breakeven_summary.json`, `data/breakeven_grid.csv` |
| The narrow safety/filter classifier is the best first target from the scored list. | modeled/inferred | `data/target_scores_summary.json`, `docs/target_ranking.md` |
| A fixed classifier can be wrapped so stale, low-confidence, unhealthy, drifted, unaudited, or forced-fallback states do not silently use the fast path. | simulated | `scripts/fallback_policy_sim.py`, `data/hybrid_arch_summary.json` |
| The prototype fixed computation can remain isolated from mutable policy logic. | simulated/synthesized | `scripts/prototype_safety_filter.py`, `hdl/safety_filter_core.sv`, `data/hdl_sim_results.csv` |
| The HDL closure validates only the pure combinational core under an amended lint/Yosys/Python/synthesis contract. | synthesized/inferred | `data/prototype_verification_closure.json`, `docs/prototype_verification_closure.md` |
| Analog, photonic, and process-specific claims remain speculative without device-level calibration, drift, conversion, yield, and repair data. | speculative | `docs/taxonomy_and_null.md`, `REFERENCES.md` |
| RISC-V is a credible open control-plane path, but not a proof of hardware advantage. | sourced/inferred | `REFERENCES.md`, `docs/hybrid_safety_filter_architecture.md` |

## Phase 2 Addendum

Phase 2 changes the final claim set without deleting the Phase 1 evidence trail. `M-CAL-1` first weakened the safety/filter case: the calibrated hybrid safety/filter won 452 of 6,300 calibrated scenarios, while the programmable accelerator won 4,948 and optimized software won 900. `M-WORKLOAD-1` then showed that effective fast-path volume, not raw request volume, controls viability; only the high-volume stable moderation scenario remained preserved before stronger-baseline replay.

`M-SWBASE-2` is the decisive downgrade. Replaying the exact workload rows against optimized software/runtime, programmable accelerator, and hybrid physicalized safety/filter produced zero hybrid wins. The formerly preserved high-volume stable moderation case flips to `programmable_accelerator`, with a daily hybrid margin of `-1471448845.624272` pJ-equivalent/day versus the best programmable baseline. This falsifies the current safety/filter performance/economic superiority claim under the validated Phase 2 assumptions.

The revised answer to the directive is therefore: useful portions of inference can be studied as physicalized hardware only as narrow bounded architectural experiments today. Current evidence does not support the tested safety/filter classifier as a performance or economic winner against a strong programmable accelerator. The broad rejection of full frontier-model fixed-weight physicalization remains unchanged, and analog/in-memory broad claims remain speculative.

The machine-checkable Phase 2 claim matrix is `physicalized-weights/data/phase2_claim_matrix.csv`; the compact summary is `physicalized-weights/data/phase2_synthesis_summary.json`; and the human-readable downgrade note is `physicalized-weights/docs/phase2_synthesis_downgrade.md`. Reopen the safety/filter performance claim only with production traces showing a durable positive hybrid margin under identical feature extraction, audit logging, fallback, update, utilization, latency, and accelerator-energy accounting.

## Falsification Roadmap

Future cycles should try to falsify the narrow positive result before broadening it:

1. Collect or synthesize workload traces for safety/filter invocation volume, fallback rate, policy update cadence, audit cost, and feature extraction cost.
2. Replace normalized cost units with sourced memory-access, accelerator dispatch, audit write, package, utilization, and update costs.
3. Compare the same classifier against optimized software batching/caching/quantization and a programmable accelerator under identical feature inputs.
4. Add a compiled Verilator simulation when `make` and a C++ compiler are available; treat disagreement as a reopening event.
5. Reopen the architecture if the HDL must absorb mutable policy state, sequential control, memories, or timing handshakes.
6. Demote the target if policy updates are weekly, if near-threshold cases dominate, if fallback/audit overhead erases savings, or if 50% software/runtime savings closes the modeled gap.
7. Promote only if measured workload data shows high reuse, slow updates, low fallback rate, bounded feature extraction, and lower per-request movement than optimized programmable baselines.

## Reproducibility And Artifact Paths

The evidence manifest is generated at `physicalized-weights/data/evidence_manifest.csv` and `physicalized-weights/data/evidence_manifest.json`. The final summary is `physicalized-weights/data/final_synthesis_summary.json`, and the evidence map is `physicalized-weights/data/final_evidence_map.png`.

Regeneration commands are listed in `physicalized-weights/docs/reproducibility.md`. The current environment does not provide `pytest`, so tests are stdlib scripts such as `python3 physicalized-weights/tests/test_final_synthesis.py`. The final package is auditable from workspace artifacts and the hashes in the manifest.

## Phase 3 Reopen-Pathway Addendum

Phase 3 integrates the production measurement contract, production trace schema, quantitative reopen thresholds, ingestion-path admissibility, end-to-end reopen gate, and replayable evidence-pack manifest into one canonical pathway. The result preserves the Phase 2 conclusion: current evidence remains downgraded, and physicalized safety/filter is not a current performance/economic winner.

The current committed Phase 3 artifacts report `actual_reopen_candidate_count = 0`. Synthetic threshold crossings, proxy/local measurements, vendor-only benchmark paths, privacy-risk traces, stale hashes, unknown threshold scenarios, and non-crossing measured packages are represented as blocked evidence classes in `physicalized-weights/data/phase3_reopen_claim_matrix.csv`.

Future reopening requires exactly this conjunction:

```text
valid_package ∧ hash_match ∧ schema_compatible ∧ known_threshold_scenario ∧ valid_trace ∧ admissible_ingestion_path ∧ measured_terms ∧ production_or_shadow_or_canary_source ∧ provenance_attestation ∧ privacy_attestation ∧ threshold_crossed
```

The generated Phase 3 report is `physicalized-weights/docs/phase3_reopen_pathway_summary.md`, the manifest is `physicalized-weights/data/phase3_reopen_manifest.csv`, and the compact summary is `physicalized-weights/data/phase3_reopen_summary.json`.

## Phase 4 Reopen Lifecycle Synthesis

Phase 4 folds `M-ACQUIRE-1`, `M-DRYRUN-1`, `M-INTAKE-1`, `M-UNCERTAINTY-1`, and `M-LIFECYCLE-1` into the canonical campaign record. The current claim state is unchanged but now unambiguous: broad/full fixed frontier physicalization remains rejected; safety/filter performance superiority remains falsified against stronger programmable baselines; and the hybrid architecture remains useful as a failure-mode and evidence-scaffold study.

No current artifact is actual measured reopen evidence. The refreshed synthesis reports `actual_reopen_candidate_count = 0` and `current_artifacts_reopen = false`. The lifecycle branch that reaches `actual_reopen_candidate` is counted separately as `hypothetical_actual_candidate_control_count = 1` and is not current measured evidence.

Future reopening requires the full lifecycle and uncertainty-aware conjunction:

```text
valid_package && hash_match && schema_compatible && known_threshold_scenario && valid_trace && admissible_ingestion_path && measured_terms && production_or_shadow_or_canary_source && provenance_attestation && privacy_attestation && nonzero_request_volume && nonzero_accepted_fast_path_volume && measured_best_programmable_baseline && threshold_crossed && UCB_alpha(H - B) < 0 && lifecycle_terminal_state=actual_reopen_candidate
```

The lifecycle states are defined by `M-LIFECYCLE-1` in `physicalized-weights/docs/evidence_package_lifecycle_state_machine.md`. The generated Phase 4 report is `physicalized-weights/docs/phase4_reopen_lifecycle_synthesis.md`, the claim matrix is `physicalized-weights/data/phase4_reopen_claim_matrix.csv`, the manifest is `physicalized-weights/data/phase4_reopen_manifest.csv`, and the compact summary is `physicalized-weights/data/phase4_reopen_summary.json`.

## Campaign Closure Disposition

M-CLOSURE-1 is the reader-facing final disposition layer for the current evidence package. It consolidates the taxonomy, models, target ranking, architecture/prototype, Phase 2 stronger-baseline downgrade, Phase 3/4 reopen pathway, M-ROBUST-1 target-class stress test, and M-DEFER-1 deferral watchlist.

The closure state is: no current physicalized-weight performance/economic superiority claim, no current reopen candidate, retained architecture/prototype value, and explicit deferral until genuinely new measured evidence appears. The generated closure report is `physicalized-weights/docs/campaign_closure_report.md`; the executive summary is `physicalized-weights/docs/campaign_executive_summary.md`; the claim table is `physicalized-weights/data/campaign_closure_claim_disposition.csv`; the manifest is `physicalized-weights/data/campaign_closure_manifest.csv`.

Counters preserved by the closure package: `current_superiority_claim_count = 0`, `actual_reopen_candidate_count = 0`, and `new_reopen_gate_count = 0`. Deferral state: `closed_under_current_evidence_deferred_until_valid_measured_package`.

## Post-Closure Public Baseline Refresh

This post-closure addendum integrates `M-PUBLICBASE-1` and `M-PUBLICBASE-2` into the canonical campaign record. It exists because official public programmable-baseline evidence moved after closure: `MLPerf Inference v6.0` was recorded as the latest MLPerf Inference release, and primary MLCommons v6.0 rows were mapped into campaign terms.

The public-baseline refresh affects the programmable baseline term `B`, not measured hybrid evidence `H`. `M-PUBLICBASE-2` ingested `12` primary MLCommons rows from `520` available rows and found `12` throughput-prior rows, `0` direct energy-calibration rows, and `0` direct safety-filter workload rows. The result is `programmable_null_effect = strengthened_or_preserved`.

The Phase 2 downgrade is preserved, no public benchmark source reopens physicalized superiority, and endpoint counters remain `current_superiority_claim_count = 0`, `actual_reopen_candidate_count = 0`, `new_reopen_gate_count = 0`, and `current_artifacts_reopen = false`. The Phase 4 reopen condition remains unchanged; public benchmark-only evidence is not production, shadow, or canary measured hybrid evidence.

The generated addendum is `physicalized-weights/docs/public_baseline_refresh_synthesis.md`; the claim matrix is `physicalized-weights/data/public_baseline_synthesis_claim_matrix.csv`; the manifest is `physicalized-weights/data/public_baseline_synthesis_manifest.csv`; and the compact summary is `physicalized-weights/data/public_baseline_synthesis_summary.json`.
