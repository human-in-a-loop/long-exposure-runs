## 1. Research Question, Definitions, and Null Hypothesis

The research question was whether useful parts of neural-network inference can be moved from ordinary programmable execution into fixed, semi-fixed, or physically encoded hardware. The work did not assume that an entire frontier language model should be permanently burned into a chip. From the first report, the intended question was narrower: which inference components are stable, frequently reused, energy-relevant, and tolerant enough that physicalization could beat optimized programmable execution after update cadence, utilization, yield, repair, and integration costs are counted.

In the cycle reports, "physicalized model weights" means encoding part of an inference workload into hardware structure, storage, topology, data movement, or compute behavior. The initial taxonomy included fixed digital logic, ROM-coded weights, SRAM or eDRAM-resident weights, FPGA and embedded-FPGA overlays, RISC-V-attached accelerators, chiplet or cartridge-style weight modules, analog in-memory arrays, photonic or mixed-signal paths, and hybrid systems that keep some work fixed while leaving control programmable. This definition made physicalization a spectrum rather than one device proposal.

The central discipline was the null hypothesis: optimized software, runtime, compiler, scheduler, memory-management, batching, routing, quantization, caching, and programmable-accelerator improvements may capture much of the available gain without fixing weights in hardware. The first-cycle plan therefore required physicalization to be compared against strong non-physicalized baselines, not against an artificially weak CPU or GPU implementation.

The first analytical mechanism was a break-even inequality:

```text
N * (C_prog - C_phys) > C_fixed + C_update + C_yield + C_integration
```

Here, `N` is the number of served requests or tokens before a material update. `C_prog` is the best programmable per-request cost after software and runtime optimization. `C_phys` is the per-request cost of the physicalized path after conversion, utilization, yield or repair, and fallback penalties. The right-hand side represents fixed substrate cost, update cost, yield or repair cost, and integration cost.

The inequality set the interpretation of the whole run. If request volume is zero, fixed physicalization cannot amortize nonzero fixed cost. If programmable execution is already cheaper than physicalized execution, no finite positive request count produces a win. If update intervals become too short, fixed weights can become stranded before they pay back their substrate cost. If software/runtime optimization cuts memory movement substantially, the request volume required for physicalization rises. If analog conversion, calibration, yield, or fallback penalties are high, analog array-level savings can disappear even when raw array read energy is low.

Cycles 2-4 turned this framing into executable artifacts. The worker built `physicalized-weights/docs/taxonomy_and_null.md`, `physicalized-weights/scripts/breakeven_model.py`, `physicalized-weights/scripts/symbolic_breakeven.wls`, and corresponding tests and outputs. The Python model compared six strategies: unoptimized programmable inference, software-optimized inference, programmable acceleration, fixed digital weights, analog in-memory compute, and a hybrid physicalized submodel. It emitted 3,360 sweep rows. In the reported default sweep, fixed digital weights won 208 rows, programmable acceleration won 192 rows, and software-optimized inference won 160 rows. Analog in-memory and hybrid physicalized submodels did not win under the default or bad-penalty assumptions reported in the cycle summary.

The Wolfram script reduced the break-even threshold to `N_break_even = fixedCost / (cProg - cPhys)` and checked the special cases above. That result was not treated as proof of a hardware win. It was used as a filter: physicalization was only worth pursuing where reuse volume, update stability, and per-request savings could plausibly offset fixed and integration costs.

The first important decision followed from this foundation. The research would not proceed by designing a broad fixed-weight language-model chip. It would first find a bounded target whose stability, reuse, and failure behavior made it a defensible physicalization candidate.

## 2. Target Selection and the Hybrid Safety/Filter Architecture

The target-ranking work rejected full frontier-model permanence and selected a fixed or semi-fixed safety/filter classifier submodel as the strongest physicalization target. This was a narrowing decision, not a proof that the target would ultimately win.

Cycle 3 scored candidate and anti-target components by update stability, reuse volume, approximation tolerance, integration complexity, energy upside against baselines, resistance to software-baseline improvements, and evidence quality. At 35% software/runtime memory-movement savings, the top ranked candidates were fixed safety/filter classifier submodels, small always-on wake-word or router models, repeated retrieval or reranking feature transforms, and mixture-of-experts router or dispatch logic. The lowest-scored anti-targets included full frontier dense weights permanently burned into fixed logic, frequently updated tenant-specific adapters, high-churn vocabulary or logit-head variants, dynamic attention over live context as fixed logic, and training or optimizer state.

The selected target was a safety/filter classifier because it had the right shape for a bounded test. It could be small, isolated, repeatedly invoked, conservatively versioned, and routed around when confidence, health, policy version, or audit requirements failed. It also avoided the main anti-target properties: broad model churn, live context dependence, tenant-specific updates, and direct ownership of user-facing generation.

Cycle 4 converted that target into a hybrid architecture. The physicalized classifier sits before the main serving stack and receives bounded request features from the host runtime. It emits a classifier decision and confidence, but it does not own tokenization, prompt parsing, policy authoring, dynamic attention state, or final routing. The host remains responsible for policy versioning, health checks, drift checks, audit logging, rollback, and fallback.

The architecture used a host-controlled, memory-mapped accelerator boundary with a RISC-V-compatible integration path. RISC-V was used as an open control-plane anchor because it is a free and open instruction set architecture with public technical specifications [1], [2]. The reports did not treat RISC-V as automatically optimal; they used it as a credible open substrate for a small, inspectable accelerator interface.

The register map made the boundary explicit. It covered device identity, ABI version, status, control, request ID, feature address and length, policy slot, required and active policy versions, threshold, confidence, decision, fallback reason, audit ring state, and rollback slot. This register map mattered because the fixed classifier was intentionally not trusted as a complete policy system. It was a fast path inside a larger programmable safety and control envelope.

The fallback-policy simulator made the architecture executable. It tested 11 policy cases and produced three route classes:

| Route | Count |
|---|---:|
| `physicalized_fast_path` | 2 |
| `programmable_fallback` | 7 |
| `fail_safe` | 2 |

Only healthy, high-confidence, version-valid cases reached the physicalized fast path. Stale policy, low confidence, zero confidence, failed health, drift alarm, host-forced fallback, and audit logging failure routed away from the physicalized output. Invalid classifier output with unavailable fallback entered fail-safe.

This result defined the first stable architecture claim. The credible system was not a standalone "weight chip." It was a programmable serving path that could optionally route a narrow, stable classifier through fixed or semi-fixed hardware. The physicalized component was deliberately kept subordinate to programmable update, audit, fallback, rollback, and final-routing logic.

## 3. Prototype and First Evidence-Labeled Synthesis

Cycles 5-7 turned the validated architecture into a small prototype and then consolidated the first research arc. The prototype did not establish a production hardware win. It showed that the proposed boundary could be implemented as an inspectable fixed classifier with conservative route and fallback behavior.

The prototype classifier used 8 signed int8 features, fixed signed int8 weights, a bias of `-10`, and a threshold of `64`. Its fixed weights were:

```text
[12, -7, 5, 9, -11, 4, 6, -3]
```

The classifier returned `block` when the score was greater than or equal to the threshold and `allow` otherwise. Confidence was defined as distance from the threshold. The route decision then checked whether the fixed classifier output could be used at all. Low confidence, stale policy version, failed health, drift alarm, host-forced fallback, audit failure, classifier unavailability, or invalid output routed away from the physicalized fast path.

Across 16 prototype cases, the route distribution was:

| Route | Count | Fraction |
|---|---:|---:|
| `physicalized_fast_path` | 6 | 0.375 |
| `programmable_fallback` | 8 | 0.500 |
| `fail_safe` | 2 | 0.125 |

The local baseline comparison used normalized cost units and included feature extraction, register/control, audit, fallback dispatch, and fail-safe handling. It reported 400.0 modeled cost units for optimized software, 368.0 for a programmable accelerator, and 162.0 for the hybrid physicalized path over the 16 diagnostic cases. The reports interpreted this as architecture support only. Because the units were normalized and the cases were diagnostic rather than production traces, the result did not establish measured economic or performance superiority.

The hardware description language work was similarly bounded. The HDL core was pure combinational logic: fixed localparam weights, signed dot product, threshold comparison, and margin/confidence outputs. There was no clock, reset, memory, handshake timing, mutable policy logic, or sequential state. That narrow scope allowed the verification contract to stay modest.

Cycle 5 confirmed Python prototype generation, Yosys evaluation, Verilator lint, Yosys synthesis, Graphviz rendering, and stdlib tests. Compiled Verilator simulation did not run because the environment lacked `make`. Cycle 6 closed this gap by recording an amended evidence contract rather than pretending compiled simulation had passed. The closure accepted Verilator lint, Yosys evaluation, Yosys synthesis, Graphviz artifacts, Python golden-vector agreement, and artifact hash freshness as sufficient for this specific combinational core. The closure JSON recorded `closure_status = validated`, `compiled_simulation_status = blocked_make_unavailable`, `yosys_eval_matches_python = true`, `verilator_lint_passed = true`, `yosys_synthesis_passed = true`, `graphviz_artifacts_present = true`, and `structural_artifacts_fresh = true`.

Cycle 6 also defined reopen conditions for the prototype milestone. `M-PROTO-1` should reopen if compiled Verilator later runs and disagrees, Python and Yosys rows diverge, the HDL hash changes without regenerated evidence, or the HDL grows to include sequential state, memories, handshake timing, or mutable policy logic. This preserved the scope of the validation: the accepted evidence applies to the tiny combinational classifier, not to a larger accelerator.

Cycle 7 produced the first final synthesis for the initial arc. It created `physicalized-weights/docs/final_synthesis.md`, `physicalized-weights/docs/reproducibility.md`, `physicalized-weights/scripts/build_final_synthesis.py`, `physicalized-weights/data/evidence_manifest.csv`, `physicalized-weights/data/evidence_manifest.json`, `physicalized-weights/data/final_synthesis_summary.json`, and `physicalized-weights/data/final_evidence_map.png`. After an auditor fix, the evidence manifest contained 25 artifacts across six evidence labels: `sourced`, `modeled`, `simulated`, `synthesized`, `inferred`, and `speculative`.

The first-arc conclusion was narrow and conditional. The completed work did not support permanently fixing full frontier large-language-model weights in hardware. It supported continued study of a stable, bounded, high-reuse safety/filter submodel only when placed behind programmable fallback, signed update, audit, health, drift, and rollback controls. The prototype showed that such a boundary could be made small and inspectable. It also reinforced the null hypothesis: most practical system complexity remained in feature extraction, runtime control, policy management, audit, fallback, and programmable serving infrastructure.

## 4. Calibration, Workload Replay, and Phase 2 Downgrade

The Phase 2 result was a downgrade of the remaining safety/filter physicalization claim. Calibration first weakened the claim, workload replay then narrowed it to one preserved synthetic workload, and a stronger programmable accelerator baseline erased that last modeled win. After this point, the research no longer supported the statement that the hybrid physicalized safety/filter path was a performance or economic winner over strong programmable baselines.

The calibration step replaced the earlier normalized model with explicit-unit companion modeling. The reports used public energy-scale and accelerator framing sources as context: Horowitz operation and memory-access energy material [7], [8], NVIDIA H100 public accelerator information [9], and MLPerf Inference documentation for system-level benchmark framing [10]. The cycle also added local host/Python proxy measurements for small int8 dot products, dispatch, combined dot-plus-dispatch, and audit logging. Those measurements were treated as local overhead proxies, not silicon energy evidence.

The calibrated model evaluated 6,300 scenarios. The reported winners were:

| Winner | Scenario count |
|---|---:|
| programmable accelerator | 4,948 |
| optimized software | 900 |
| hybrid physicalized safety/filter | 452 |

The hybrid safety/filter winner share fell to 0.0717, with the result classified as `preserved_but_weakened`. The top uncertainty drivers were fallback frequency, utilization, requests per day, audit/control scale, and update interval. This shifted attention away from the fixed dot-product core and toward the surrounding serving system.

The workload replay made that shift concrete. Ten deterministic synthetic workload regimes distinguished raw request volume from effective fast-path volume. Effective fast-path volume is the request share that can actually use the fixed classifier after fallback, near-threshold uncertainty, stale policy windows, drift, audit failures, fallback outages, and utilization penalties are counted. Only one regime, `high_volume_stable_moderation`, preserved the physicalized safety/filter claim. Three were weakened, two were speculative, and four were falsified. The preserved case had high traffic, low fallback pressure, monthly-or-slower update cadence, and bounded audit/control overhead.

The decisive test was the stronger-baseline replay. The same workload rows were compared across optimized software/runtime, programmable accelerator, and hybrid physicalized safety/filter alternatives under identical traffic, feature extraction, fallback, audit, update, and utilization accounting. The result was:

| Winner | Scenario count |
|---|---:|
| programmable accelerator | 9 |
| optimized software/runtime | 1 |
| hybrid physicalized safety/filter | 0 |

For the previously preserved `high_volume_stable_moderation` case, the programmable accelerator cost proxy was `8,178,811,874.414918` pJ-equivalent/day, while the hybrid physicalized safety/filter cost proxy was `9,650,260,720.03919` pJ-equivalent/day. The hybrid margin against the best programmable baseline was therefore `-1,471,448,845.624272` pJ-equivalent/day. A negative margin means the best programmable baseline was already cheaper under the model.

The reports later use $H$ for the measured or modeled hybrid physicalized total and $B$ for the measured or modeled best programmable baseline total. Phase 2 established that, for the current modeled workload set, $H - B$ was not below zero for any scenario. The safety/filter hardware remained useful as an architecture and failure-mode study, but not as a demonstrated winner.

Cycle 11 converted this downgrade into the current claim set. The Phase 2 claim matrix marked the physicalized safety/filter performance/economic winner claim as `falsified`. It preserved the architecture and failure-mode study as useful, and it marked earlier target-ranking superiority language as `superseded` because target suitability alone no longer justified performance-superiority language after stronger-baseline replay.

## 5. Production Measurement Contract and Trace Validation

The next decision was that local timings and synthetic traces could not reopen the downgraded claim. Cycles 11-13 defined a production measurement contract and then encoded it in a trace validator. The result was a hard separation between tooling evidence and production evidence.

The local proxy benchmark measured six components over the ten validated workload scenarios:

| Component | Median proxy latency |
|---|---:|
| append-only audit write | `20538.441 ns/request` |
| audit serialization | `17367.176 ns/request` |
| feature extraction | `10437.758 ns/request` |
| optimized software classifier | `8763.939 ns/request` |
| route/fallback decision | `5667.545 ns/request` |
| fixed classifier | `5160.697 ns/request` |

The summary reported that control overhead dominated the fixed classifier. This result supported the system-level interpretation of Phase 2: the fixed arithmetic block was not the main unresolved cost. Feature extraction, audit serialization, audit writes, fallback routing, baseline execution, and accelerator integration had to be measured under the same workload before any hardware-superiority claim could be reconsidered.

The measurement gap matrix then separated what had been locally proxied from what remained production-required. Local proxies covered feature extraction latency, audit serialization/logging latency, fallback dispatch timing, and optimized software classifier timing. Production-required or unmeasured quantities included feature extraction energy, audit storage cost, optimized software energy, programmable accelerator latency, programmable accelerator energy, accelerator utilization and batching, and durable hybrid margin.

The production trace schema made those requirements machine-checkable. A trace could only become a `valid_reopen_candidate` if it had nonzero request volume, nonzero accepted physicalized fast-path requests, measured accelerator energy, measured hybrid energy, required software and accelerator baseline latency fields, audit fields, passing health and drift gates for accepted fast-path rows, and a consistent policy window.

The validator also closed several loopholes. It rejected incomplete telemetry, proxy-only energy, privacy-risk columns, missing baselines, inconsistent policy windows, zero-volume controls, all-fallback controls, and failed fast-path guardrails. After an auditor fix, accepted fast-path credit also required `fallback_taken=false`, `audit_logged=true`, `health_gate_passed=true`, and `drift_gate_passed=true`.

The synthetic valid fixture remained intentionally non-reopening. It had nonzero request volume and accepted fast-path rows, but it was blocked because its hybrid energy was proxy evidence and its environment was synthetic. The invalid fixture was rejected for privacy-risk content, missing accelerator baseline latency, negative feature-extraction latency, and inconsistent policy versions.

This measurement contract changed the meaning of future work. The open question was no longer whether another local benchmark or synthetic workload could make the hybrid path look favorable. The required evidence became measured feature extraction, audit cost, fallback behavior, update cadence, utilization, software baseline latency and energy, programmable accelerator latency and energy, and hybrid total cost over the same requests and policy window.

## 6. Reopen Pathway: Thresholds, Ingestion, Evidence Packs, and Uncertainty

Cycles 14-22 made the future reopen pathway executable without changing the scientific conclusion. No current artifact reopened the Phase 2 downgrade. The contribution was a complete gate chain for future evidence: quantitative threshold, admissible ingestion path, end-to-end pipeline status, evidence package replay, acquisition readiness, operator dry run, intake rehearsal, and uncertainty-aware margin.

The quantitative threshold model stated the core reopen inequality:

```text
measured_hybrid_total < measured_best_programmable_baseline
```

The comparison must use identical accepted-volume, fallback, audit, update, utilization, latency, and energy accounting. For the `high_volume_stable_moderation` scenario, the current gap was the same Phase 2 margin: the hybrid path would need a `1,471,448,845.624272` pJ-equivalent/day reduction, or the programmable baseline would need an equivalent degradation, just to tie. The threshold summary reported `current_hybrid_wins = 0`, eight finite-threshold scenarios, one unreopenable zero-volume scenario, and one unreopenable all-fallback scenario.

The ingestion-path evaluator then ranked possible evidence sources. It classified `shadow_production_dual_run` and `canary_ab_dual_instrumented` as `reopen_candidate_path` designs. `offline_replay_redacted_features` was only `threshold_evaluable_if_measured`. Synthetic fixtures, sampled production logs without baselines, vendor-only benchmarks, and simulated scaled workloads were valid or diagnostic in limited ways but insufficient to reopen the claim. Privacy-risk raw logs were inadmissible.

The end-to-end pipeline combined trace validation, ingestion admissibility, provenance checks, measured-status checks, and threshold comparison. Its final statuses were `invalid_trace`, `valid_but_insufficient`, `threshold_evaluable_not_crossed`, `synthetic_counterfactual_crossed`, and `actual_reopen_candidate`. The generated fixtures covered the non-reopening branches, and the summary reported `actual_reopen_candidate_count = 0`.

The evidence-pack layer bound the required inputs into replayable manifests. A package had to preserve the trace file hash, schema compatibility, privacy attestation, provenance attestation, ingestion path, evidence source type, measurement status, threshold scenario mapping, and downstream pipeline result. The replay summary covered five privacy-safe manifest fixtures: three valid packages, two invalid packages, and zero actual reopen candidates. An auditor fix made unknown threshold scenarios hard package blockers before downstream evaluation.

The Phase 3 synthesis consolidated the gate chain across measurement requirements, trace validation, thresholds, ingestion admissibility, pipeline status, and evidence-pack replay. It reported 14 Phase 3 claims, `current_artifacts_reopen = false`, `actual_reopen_candidates = 0`, and `ingestion_actual_reopened_count = 0`. It also named the blocked evidence classes: synthetic, proxy/local, vendor-only, privacy-risk, stale-hash, unknown-threshold, and non-crossing measured packages.

The acquisition-readiness layer screened proposed collection designs before data collection. It evaluated 20 criteria across ten proposed designs. Two designs, `shadow_dual_run_full_instrumentation` and `canary_ab_full_instrumentation`, were `ready_to_collect_candidate`; one was repairable before collection; five were inadmissible; and two were diagnostic-only. The ready designs were not evidence. They were admissible plans for collecting future evidence.

The operator dry-run and intake rehearsal layers then made that future path usable. The dry-run checker evaluated package templates for manifest completeness, trace header privacy, required columns, threshold scenario allow-list membership, hash consistency, source/measurement consistency, and attestation replacement. Two complete templates were `ready_for_collection_not_evidence`, and ten cases were blocked for schema, template, privacy, provenance, integrity, or threshold-mapping problems. The intake rehearsal filled synthetic-safe package-local traces, computed SHA-256 hashes, wrote replay-compatible manifests, checked handoff preservation, and delegated preserved packages to the replay evaluator. Three synthetic-safe packages passed intake, six mutation cases were blocked before replay, and zero packages became actual reopen candidates.

The final Stage 3 addition was uncertainty. A future measured package must not merely show a favorable point estimate. It must show a statistically durable margin. The protocol defined:

$$D = H - B$$

where $H$ is the measured hybrid total and $B$ is the measured best programmable baseline total under the same workload and accounting. The uncertainty-aware rule is:

$$UCB_\alpha(D) = \Delta_{\text{mean}} + z_\alpha \sigma_\Delta < 0$$

with:

$$\Delta_{\text{mean}} = H_{\text{mean}} - B_{\text{mean}}$$

and:

$$\sigma_\Delta = \sqrt{\sigma_H^2 + \sigma_B^2 - 2\rho\sigma_H\sigma_B + \sigma_{\text{workload mix}}^2 + \sigma_{\text{meter}}^2}$$

This rule is necessary but not sufficient. It is conjoined with all previous gates: valid package, hash match, schema compatibility, known threshold scenario, valid trace, admissible ingestion path, measured terms, production/shadow/canary source, provenance attestation, privacy attestation, threshold crossing, nonzero request volume, and nonzero accepted fast-path volume. The uncertainty summary evaluated 11 synthetic-safe cases and reported zero actual reopen candidates.

The resulting reopen condition is precise. A future challenge to the Phase 2 downgrade must be a measured, privacy-safe, provenance-attested production, shadow-production, or canary package; it must preserve hashes and schema compatibility; it must map to a known threshold scenario; it must pass trace validation and ingestion admissibility; it must include nonzero request and accepted fast-path volume; it must cross the quantitative threshold against the best programmable baseline under identical accounting; and its upper confidence bound on $H - B$ must be below zero. Current artifacts are templates, proxies, synthetic fixtures, rehearsals, and decision protocols. They do not satisfy that condition.

## 7. Lifecycle State Machine and Canonical Phase 4 Reopen Condition

The Phase 4 work converted the accumulated reopen gates into one lifecycle state machine and one canonical reopen rule. The conclusion did not change: no current artifact was actual measured production, shadow, or canary evidence, and no current artifact reopened the Phase 2 downgrade.

The lifecycle state machine classified candidate evidence packages through the existing gates: acquisition readiness, operator dry run, intake rehearsal, evidence-pack replay, threshold evaluation, and uncertainty margin. A lifecycle state machine is a deterministic classifier. Each package scenario receives a terminal state, an owning gate, and a rationale. Terminal states included `collection_ready_not_evidence`, `dryrun_ready_not_evidence`, `intake_rehearsed_not_evidence`, `replay_blocked`, `threshold_crossed_nonactual`, `uncertainty_inconclusive`, `statistically_durable_nonactual`, and `actual_reopen_candidate`.

The lifecycle summary reported 15 cases, zero current actual reopen candidates, `current_artifacts_reopen = false`, one hypothetical actual-candidate control, and zero status mismatches. The single `actual_reopen_candidate` terminal state belonged only to a hypothetical measured durable positive-control row. It showed that the state machine could represent future valid evidence; it was not counted as current evidence.

The Phase 4 synthesis then canonicalized the future reopen condition:

```text
valid_package && hash_match && schema_compatible && known_threshold_scenario &&
valid_trace && admissible_ingestion_path && measured_terms &&
production_or_shadow_or_canary_source && provenance_attestation &&
privacy_attestation && nonzero_request_volume &&
nonzero_accepted_fast_path_volume && measured_best_programmable_baseline &&
threshold_crossed && UCB_alpha(H - B) < 0 &&
lifecycle_terminal_state=actual_reopen_candidate
```

Here, $H$ is the measured hybrid total and $B$ is the measured best programmable baseline total under the same workload accounting. The expression $UCB_\alpha(H - B) < 0$ means the upper confidence bound on the hybrid-minus-baseline margin must remain below zero. A favorable point estimate is not enough.

The Phase 4 summary reported 10 claim rows, zero current actual reopen candidates, `current_artifacts_reopen = false`, and one hypothetical actual-candidate control. An auditability fix ensured every claim-support artifact appeared in the Phase 4 manifest. After that fix, the Phase 4 synthesis made the reopen condition complete and traceable without adding a new route around the earlier evidence gates.

## 8. Robustness, Closure, and Archive

The robustness, closure, and archive work converted the negative result into a governed endpoint. It did not soften the conclusion. Across these stages, the reported endpoint counters stayed fixed: zero current physicalized superiority claims, zero actual reopen candidates, zero new reopen gates, and `current_artifacts_reopen = false`.

The target robustness stress test evaluated eight target classes:

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

The stress test covered calibrated, favorable-plausible, extreme-counterfactual, and special-control regimes. Its final summary reported 28 cases, zero calibrated physicalized wins, four favorable-plausible physicalized wins, zero plausible anti-target wins, eight extreme counterfactual wins, zero current superiority claims, and zero status mismatches. The favorable-plausible wins were limited to candidate-like stable targets under simultaneous favorable movement in volume, utilization, update cadence, overhead, and physicalized per-request savings. Extreme wins were labeled counterfactual, not current evidence.

The deferral watchlist then separated claims, future triggers, and insufficient substitutes. It recorded five current claim dispositions: broad fixed frontier-model physicalization rejected under current evidence; safety/filter performance or economic superiority falsified under the stronger programmable baseline; hybrid architecture and prototype retained as architecture, failure-mode, and evidence-scaffold work; the Phase 4 reopen pathway complete but inactive; and no calibrated current superiority claim for non-safety target classes.

The watchlist also made future triggers explicit. Measured shadow/canary packages, measured production packages, and new stable high-volume target evidence remained inactive unless they satisfied the existing Phase 4 lifecycle path. Vendor-only benchmarks, synthetic counterfactuals, local proxies, and templates or dry runs were insufficient. Compiled Verilator availability and HDL design-scope changes affected prototype verification only. Public programmable-baseline updates could refresh assumptions but could not, by themselves, imply a physicalized win.

The closure report projected the campaign into seven claim rows:

| Claim | Disposition |
|---|---|
| `full_frontier_fixed_weight_physicalization` | rejected under current evidence |
| `safety_filter_performance_superiority` | falsified under stronger programmable baseline |
| `hybrid_architecture_failure_mode_value` | retained as architecture and failure-mode study |
| `prototype_hdl_evidence` | retained as bounded prototype evidence |
| `future_measured_reopen_path` | complete but inactive absent actual measured evidence |
| `non_safety_target_robustness` | no calibrated current superiority claim |
| `campaign_deferral_state` | closed under current evidence, deferred until a valid measured package |

The closure summary preserved the same endpoint values: `current_superiority_claim_count = 0`, `actual_reopen_candidate_count = 0`, `new_reopen_gate_count = 0`, `current_artifacts_reopen = false`, `phase2_hybrid_workload_wins = 0`, and `robust_calibrated_physicalized_win_count = 0`.

The archive index made that endpoint machine-checkable. It indexed 54 canonical artifacts with existence, byte size, SHA-256 hash, milestone owner, artifact class, and regeneration command where available. The archive summary reported zero missing canonical artifacts and zero zero-size canonical artifacts. It also preserved the same endpoint counters and documented two known noncanonical warnings: generated cycle reports under `reports/cycles/` and root prompt/log files.

## 9. Post-Closure Checks and Public-Baseline Refresh

Post-closure checks addressed three bounded maintenance questions: whether local HDL tooling had changed, whether canonical artifacts contradicted the endpoint, and whether newer public programmable-baseline evidence should refresh the baseline prior. None reopened physicalized performance superiority.

The toolchain condition probe found Verilator, Yosys, and Graphviz available. Verilator lint, Yosys eval, Yosys synthesis, and Graphviz artifact checks passed. Compiled Verilator simulation remained blocked by the environment because `make` and a C++ compiler were unavailable. The probe therefore refreshed prototype evidence but did not change the prototype status. It recorded `compiled_verilator_available = false`, `compiled_verilator_status = blocked_environment`, `prototype_claim_reopened = false`, `performance_claim_reopened = false`, and the endpoint counters at zero or false.

The campaign invariant checker reviewed 17 artifacts: eight JSON summaries and nine Markdown reports. It checked fields such as `current_superiority_claim_count`, `actual_reopen_candidate_count`, `new_reopen_gate_count`, `current_artifacts_reopen`, and `performance_claim_reopened`. The result was zero machine-readable contradictions. Warning-level ambiguous text rows were preserved as reader-risk flags, but they did not assert a current physicalized-weight win or actual reopen.

The public programmable-baseline recency probe identified MLPerf Inference v6.0, published by MLCommons on 2026-04-01, as newer than the earlier public MLPerf reference set [10]-[13]. The official v6.0 results repository was treated as the primary machine-readable source for future baseline refresh [13]. NVIDIA's MLPerf page was retained as secondary vendor context only [14]. The probe recommended a model refresh and reported that public sources did not reopen the physicalized claim.

The subsequent public-baseline prior refresh ingested 12 rows from 520 available primary MLCommons v6.0 result rows. The selected rows covered public throughput-like benchmark metadata for datacenter accelerator submissions, including model/scenario combinations such as `deepseek-r1` and `gpt-oss-120b`. The mapping accepted these rows only as bounded programmable-system strength context. It found zero direct energy calibration rows and zero safety-filter direct workload rows. The refresh decision was `strengthen_programmable_null`, with the Phase 2 downgrade preserved.

The public-baseline synthesis integrated this refresh into the canonical record. It reported `public_baseline_refresh_integrated = true`, `latest_mlperf_inference_release = MLPerf Inference v6.0`, `primary_mlcommons_rows_ingested = 12`, `direct_energy_calibration_rows = 0`, `safety_filter_direct_workload_rows = 0`, `programmable_null_effect = strengthened_or_preserved`, `phase2_downgrade_preserved = true`, and `phase4_reopen_condition_unchanged = true`.

The important distinction is between $B$ and $H$. Public benchmark evidence can update or strengthen $B$, the best programmable-baseline side of the comparison. It does not supply $H$, the measured hybrid physicalized total under the same safety/filter workload accounting. Because the Phase 4 reopen condition requires both measured hybrid evidence and measured best programmable-baseline evidence in the same lifecycle-valid package, public MLPerf evidence alone cannot satisfy the reopen rule.

## 10. Trigger-Gated Endpoint and Residual Work

The final endpoint is trigger-gated at `M-PUBLICBASE-SYNTH-1`. Later admission-control records did not add scientific evidence, executable validation, milestone state, or research artifacts. They formalized that no further research cycle should be opened unless a validated trigger appears.

The endpoint state is:

| Endpoint field | Current value |
|---|---:|
| `current_superiority_claim_count` | 0 |
| `actual_reopen_candidate_count` | 0 |
| `new_reopen_gate_count` | 0 |
| `current_artifacts_reopen` | false |

Cycles 35-37 checked the admissible trigger classes and found all absent: no lifecycle-valid measured production, shadow, or canary hybrid evidence; no relevant compiled-HDL capability change for `M-PROTO-1`; no materially new primary public-data mapping scope beyond the public-baseline milestones; and no nonduplicative handoff artifact class. The controlling decision was `PIVOT`, meaning the work should not treat no-op admission handling or watch-state reconfirmation as campaign progress.

Cycle 38 recorded the same state as `ADMISSION_BLOCKED_NO_CYCLE`. No files, milestones, ledger events, validation runs, or artifacts were created. The audit again issued `PIVOT`, preserving the trigger-gated endpoint and preventing duplicate endpoint validation from being counted as a new research result.

The final audit summary supplied to this final-report stage has `promise_check = unknown`, no milestone-status distribution, no confidence-tagged milestone state, no residual-debt items, no future-work items, no severity-count findings, and no reconciliation events. It does report complete figure ledger coverage: 33 figures present and 33 figures in the ledger, with no missing or orphan figures. Because the audit summary provides no residual-debt or future-work anchors, this report does not invent new research directions beyond the already defined trigger condition.

The remaining actionable work is therefore conditional:

| Trigger | Effect |
|---|---|
| lifecycle-valid measured production/shadow/canary hybrid evidence | evaluate through the Phase 4 reopen condition |
| `make` and a C++ compiler become available for compiled Verilator simulation | rerun prototype verification for `M-PROTO-1`; this affects prototype correctness, not performance superiority by itself |
| materially new primary public-data mapping scope appears | refresh programmable-baseline prior `B`; this does not reopen without measured hybrid `H` |
| nonduplicative handoff artifact requirement appears | produce that handoff artifact without changing scientific claims unless new evidence supports it |

Absent one of those triggers, the campaign remains closed under current evidence. Full fixed frontier-model physicalization is rejected under the present record. Safety/filter physicalization remains a bounded architecture, verification, failure-mode, and evidence-gating study. It is not a current performance or economic winner over strong programmable baselines.


Stage 4: Appended body sections 7-10 covering lifecycle closure, robustness/archive, public-baseline refresh, and the trigger-gated endpoint.
File: <workspace>/reports/final/draft.md
Size: 293 lines / 39836 bytes
