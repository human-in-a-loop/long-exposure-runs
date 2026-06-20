# Final Report Outline

## Source Inventory

This inventory follows the research record chronologically and names the source reports that will support the final synthesis.

1. `reports/cycles/report_cycles_1-1.md` — 2026-05-13. Establishes the research contract, workspace structure, plan of record, references, and the decision to begin with taxonomy, a strong null hypothesis, and break-even modeling before proposing hardware claims.
2. `reports/cycles/report_cycles_2-4.md` — 2026-05-13. Defines physicalized model weights, builds the normalized break-even model, ranks target classes, rejects full frontier-model permanence as a primary target, and specifies the hybrid safety/filter architecture.
3. `reports/cycles/report_cycles_5-7.md` — 2026-05-13. Builds the prototype safety/filter fast path, closes the initial HDL/prototype verification gap, and produces the first evidence-labeled synthesis.
4. `reports/cycles/report_cycles_8-10.md` — 2026-05-13. Begins Phase 2 calibration, adds workload traces, and shows that a stronger programmable accelerator baseline erases the last modeled hybrid safety/filter win.
5. `reports/cycles/report_cycles_11-13.md` — 2026-05-13. Converts the Phase 2 downgrade into the current claim set, defines production measurement requirements, and creates the production trace schema and validator.
6. `reports/cycles/report_cycles_14-16.md` — 2026-05-13. Quantifies reopen thresholds, ranks admissible trace-ingestion paths, and composes trace validation, ingestion, provenance, and threshold checks into an end-to-end reopen pipeline.
7. `reports/cycles/report_cycles_17-19.md` — 2026-05-13. Adds replayable evidence-pack manifests, Phase 3 reopen-pathway synthesis, and evidence-acquisition readiness screening.
8. `reports/cycles/report_cycles_20-22.md` — 2026-05-13. Adds operator evidence-pack dry-run templates, synthetic-safe intake rehearsal, and an uncertainty-aware measured reopen protocol.
9. `reports/cycles/report_cycles_23-25.md` — 2026-05-13. Builds the evidence-package lifecycle state machine, canonical Phase 4 reopen synthesis, and target robustness stress test. Canonicalizes the future reopen condition as a conjunction over package integrity, measured evidence, threshold crossing, uncertainty durability, and lifecycle terminal state.
10. `reports/cycles/report_cycles_26-28.md` — 2026-05-13. Converts the negative result into a controlled endpoint through the campaign deferral watchlist, reader-facing closure package, and machine-checkable archive index.
11. `reports/cycles/report_cycles_29-31.md` — 2026-05-13. Adds post-closure checks: refreshed local HDL toolchain condition evidence, cross-artifact invariant checking, and public programmable-baseline recency screening. Finds MLPerf Inference v6.0 is newer than the earlier reference set and material for baseline refresh, but not a reopen.
12. `reports/cycles/report_cycles_32-34.md` — 2026-05-13. Maps MLCommons v6.0 public result metadata into the programmable-baseline prior, integrates that public-baseline refresh into canonical synthesis, and records that public benchmark evidence updates baseline context rather than measured hybrid evidence.
13. `reports/cycles/report_cycles_35-37.md` — 2026-05-13. Formalizes the trigger-gated boundary. These reports add no new scientific evidence; they preserve the endpoint counters and reject no-op admission handling as progress.
14. `reports/cycles/report_cycles_38-38.md` — 2026-05-13. Records an admission-blocked state with no admissible trigger. The controlling endpoint remains `M-PUBLICBASE-SYNTH-1`.
15. `MANIFEST.md` — current workspace inventory. Provides script, test, HDL, document, generated-data, figure, cumulative-stat, and cross-reference inventories for implementation details and key-file selection at finalization.
16. `REFERENCES.md` — bibliography with references [1]-[14], including RISC-V, gem5, OpenROAD, CIRCT, IBM analog in-memory computing context, Horowitz energy estimates, NVIDIA H100 context, and MLCommons/MLPerf sources.
17. Final audit summary input — reports `promise_check=unknown`, no residual debt or future-work items, no severity-count findings supplied, no reconciliation events, and complete figure ledger coverage of 33 figures.

Record gaps to carry into the final report:

- The final audit summary does not provide milestone-status distribution, milestone-state confidence tags, residual debt, or future-work anchors. The final report should therefore rely on the cycle reports for the scientific narrative and describe the audit headline conservatively as `promise_check=unknown`.
- Cycles 35-38 are not scientific additions. They should appear only as the endpoint boundary: no admissible trigger, no new evidence, and no changed conclusion.
- The supplied wall-cap flag is `false`, so no wall-cap caveat is needed.

## Narrative Arc

The final report will use a problem-to-endpoint arc rather than a strict cycle log. It will first define the research question and null hypothesis, then explain how the candidate target narrowed to a safety/filter fast path, how calibrated and stronger baselines defeated the performance claim, how the reopen pathway was made executable, and how the campaign closed into a trigger-gated state with public-baseline updates treated as baseline context only.

## Section Plan and Stage Assignments

### Stage 2 Body Sections

#### 1. Research Question, Definitions, and Null Hypothesis

Coverage: Define physicalized model weights, explain why full frontier-model permanence was not the primary question, and state the null hypothesis that optimized software/runtime systems and programmable accelerators may capture practical gains without fixed weights.

Sources: `report_cycles_1-1.md`; `report_cycles_2-4.md`; references [1]-[6] where needed for systems context.

#### 2. Target Selection and the Hybrid Safety/Filter Architecture

Coverage: Summarize the break-even mechanism, target-ranking result, rejected anti-targets, and the selected fixed or semi-fixed safety/filter classifier behind programmable fallback, update, rollback, audit, health, and drift controls.

Sources: `report_cycles_2-4.md`; `report_cycles_5-7.md`; `MANIFEST.md` script/data inventory for `breakeven_model.py`, `target_scoring.py`, `fallback_policy_sim.py`, and prototype artifacts.

#### 3. Prototype and First Evidence-Labeled Synthesis

Coverage: Explain the prototype safety/filter fast path, HDL/prototype verification closure, and the first narrow claim: the architecture was credible as a bounded safety/filter study, not as evidence for full-model physicalization.

Sources: `report_cycles_5-7.md`; `MANIFEST.md` HDL inventory; final audit summary figure-coverage count only if needed for artifact completeness.

### Stage 3 Body Sections

#### 4. Calibration, Workload Replay, and Phase 2 Downgrade

Coverage: Present the key result first: calibrated modeling weakened the safety/filter claim, workload traces left one preserved case, and stronger programmable accelerator replay erased the last hybrid win. Define `H` as hybrid physicalized cost/energy and `B` as best programmable baseline when those symbols first appear.

Sources: `report_cycles_8-10.md`; `report_cycles_11-13.md`; references [7]-[10] for public calibration and programmable-baseline context.

#### 5. Production Measurement Contract and Trace Validation

Coverage: Explain why local proxy timings did not count as production evidence and summarize the production trace schema/validator blockers: incomplete telemetry, proxy-only energy, privacy-risk columns, missing baselines, inconsistent policy windows, zero-volume/all-fallback controls, and failed fast-path guardrails.

Sources: `report_cycles_11-13.md`; `MANIFEST.md` cross-references for `local_overhead_benchmark.py`, `production_trace_validator.py`, and generated trace-schema artifacts.

#### 6. Reopen Pathway: Thresholds, Ingestion, Evidence Packs, and Uncertainty

Coverage: Synthesize the future evidence path from quantitative thresholds through admissible ingestion, pipeline decisioning, evidence-pack replay, acquisition readiness, operator dry-run, intake rehearsal, and uncertainty-aware margins. Emphasize that these mechanisms did not reopen the claim.

Sources: `report_cycles_14-16.md`; `report_cycles_17-19.md`; `report_cycles_20-22.md`; references from `REFERENCES.md` only where cited by those reports.

### Stage 4 Body Sections

#### 7. Lifecycle State Machine and Canonical Phase 4 Reopen Condition

Coverage: State the canonical future reopen conjunction, including package validity, hash preservation, schema compatibility, threshold scenario mapping, trace validity, admissibility, measured production/shadow/canary source, provenance and privacy attestations, nonzero volume and fast-path volume, measured best programmable baseline, threshold crossing, uncertainty durability, and terminal `actual_reopen_candidate` lifecycle state.

Sources: `report_cycles_23-25.md`; `MANIFEST.md` data/figure inventory for lifecycle, Phase 4 synthesis, and target robustness artifacts.

#### 8. Robustness, Closure, and Archive

Coverage: Summarize the target robustness stress test, closure package, deferral watchlist, and archive index. Report the stable endpoint counters: zero current superiority claims, zero actual reopen candidates, zero new reopen gates, and `current_artifacts_reopen = false`.

Sources: `report_cycles_23-25.md`; `report_cycles_26-28.md`; `MANIFEST.md` generated data and cumulative stats.

#### 9. Post-Closure Checks and Public-Baseline Refresh

Coverage: Explain the post-closure toolchain condition probe, invariant checker, public-baseline recency probe, MLCommons v6.0 prior refresh, and synthesis addendum. State that public benchmark evidence updates programmable-baseline prior `B` but does not provide measured hybrid total `H`, so it cannot satisfy the Phase 4 reopen rule.

Sources: `report_cycles_29-31.md`; `report_cycles_32-34.md`; references [10]-[14]; `MANIFEST.md` public-baseline and toolchain inventories.

#### 10. Trigger-Gated Endpoint and Residual Work

Coverage: Describe the final endpoint as trigger-gated at `M-PUBLICBASE-SYNTH-1`. Note that cycles 35-38 add no new scientific evidence and that the final audit summary provides no residual-debt or future-work anchors. Future work should therefore be limited to the already defined trigger condition rather than newly invented directions.

Sources: `report_cycles_35-37.md`; `report_cycles_38-38.md`; final audit summary input.

## Finalize Stage Assembly Plan

Stage 5 will assemble:

1. YAML front matter with title and date.
2. Abstract summarizing the negative scientific endpoint and the bounded value of the architecture/evidence scaffold.
3. Introduction defining the research question and report scope.
4. The full body from `reports/final/draft.md`.
5. Conclusions stating the endpoint, future trigger condition, audit headline (`promise_check=unknown`), figure coverage from the audit summary, and the absence of wall-cap caveat.
6. References copied from `REFERENCES.md` using bracket numbering [1]-[14].
7. A MANIFEST.md `## Key Files` update based only on files explicitly cited or used as direct evidence in the completed final report.
