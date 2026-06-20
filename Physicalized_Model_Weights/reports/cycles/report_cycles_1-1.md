---
title: "Physicalized Model Weights - cycles 1-1"
date: "2026-05-13"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Physicalized Model Weights - cycles 1-1

## Abstract

Cycle 1 established the research contract for a long-exposure investigation into "physicalized model weights": hardware structures where useful parts of neural-network inference are fixed, semi-fixed, or physically encoded rather than repeatedly fetched and executed through ordinary programmable CPU/GPU memory hierarchies.

The cycle did not produce worker-built simulations, figures, HDL, or audit results. Its completed output was foundational: it converted the directive into a plan of record, created the workspace structure, registered initial references, opened the first milestones, and produced a researcher brief for the next worker step. The central decision was to begin with taxonomy, a strong null hypothesis, and a break-even model before proposing RISC-V interfaces, analog arrays, chiplets, or HDL artifacts. The rationale was that later architecture work only matters if physicalization can beat strong software/runtime and programmable-accelerator baselines after update cadence, utilization, yield, repair, and amortization are included.

Sources: directive file `physicalized_model_weights_long_exposure_prompt.md`; researcher session `767b4ba0-735b-48f8-811a-32cafefc3c0e`; related compaction record `cb62f65f-3ac2-4687-b349-e34a629ecf79`; `plan_of_record.md`; `STRUCTURE.md`; `promise_ledger.jsonl`; `REFERENCES.md`; telemetry under `.long-exposure-physicalized/telemetry/`.

## Introduction

The directive asks whether useful portions of neural-network inference can be moved from programmable execution toward fixed, semi-fixed, or physically encoded hardware. It explicitly rejects the naive question of whether an entire frontier large language model should be permanently burned into one chip. Instead, it asks which parts of inference are static, frequently reused, energy-dominant, and tolerant enough to justify physicalization.

The directive also defines the strongest objection: software, operating systems, runtimes, compilers, schedulers, quantization, batching, caching, and heterogeneous routing may capture much of the practical efficiency gain without changing hardware. Cycle 1 therefore framed physicalization as a design-space question that must be compared against strong non-physicalization baselines.

The initial references registered for this work cover the open architecture and tooling baseline: RISC-V as an open instruction set architecture [1], RISC-V technical specifications [2], gem5 as an open architecture simulator [3], OpenROAD for open RTL-to-GDSII flows [4], CIRCT for MLIR/LLVM-based hardware tooling [5], and IBM Research's analog in-memory compute framing [6].

## Approach

Cycle 1 began at `2026-05-13T01:51:36Z` with run ID `run-2026-05-13T015136Z`. The initial researcher work created or updated the following root artifacts:

- `STRUCTURE.md`, which established the standard workspace layout and added `physicalized-weights/` as the domain-specific folder for taxonomy, models, data, tests, HDL sketches, and stale artifacts.
- `plan_of_record.md`, which converted the directive into goals, milestones, success criteria, dependencies, and explicit out-of-scope boundaries.
- `REFERENCES.md`, which registered six starting references.
- `promise_ledger.jsonl`, which recorded run start, plan validation, and the first active milestones.

The plan of record defines five goals:

- `G1`: define the physicalized-weight design space and strongest null hypothesis against software/runtime and programmable-accelerator baselines.
- `G2`: build auditable analytical and executable models for energy, amortization, update cadence, utilization, and uncertainty.
- `G3`: identify credible targets and anti-targets for physicalization with ranked evidence and falsification criteria.
- `G4`: develop at least one concrete open-architecture hybrid proposal with interfaces, failure modes, and prototype roadmap.
- `G5`: produce a final research-grade synthesis with evidence labels.

The plan also defines seven milestones. Cycle 1 opened three of them: `M-TAX-1`, `M-MODEL-1`, and `M-BASE-1`. The remaining milestones, `M-TARGET-1`, `M-ARCH-1`, `M-PROTO-1`, and `M-FINAL-1`, remained pending.

## Findings

### Foundational Decision

Cycle 1 chose the foundational sub-topic: define the taxonomy, the null hypothesis, and the first break-even model scaffold before building any hardware artifact.

The researcher brief states that this is first because every later RTL, RISC-V, analog, chiplet, or OS/runtime claim depends on whether fixed or semi-fixed weights can beat strong programmable baselines after update cadence, utilization, yield, and amortization are included. This decision appears in session `767b4ba0-735b-48f8-811a-32cafefc3c0e` and is repeated in compaction record `cb62f65f-3ac2-4687-b349-e34a629ecf79`.

### Null Hypothesis

The working null hypothesis is that optimized software, runtime, and control-plane improvements on programmable hardware may capture most practical gains without physically encoding model weights. The brief names quantization, batching, routing, prefix caching, key-value cache management, speculative decoding, schedulers, memory managers, compiler/runtime placement, and heterogeneous model routing as the baselines that physicalization must beat or complement.

This null hypothesis is not a rejection of physicalization. It is the benchmark against which physicalization must show value.

### Physicalization Scope

Cycle 1 framed physicalization as a spectrum rather than a single architecture. The researcher brief directed the next worker to cover:

- ROM-coded or fixed digital weights.
- SRAM/eDRAM-resident weights.
- FPGA or eFPGA overlays.
- RISC-V-attached accelerators.
- Chiplet or cartridge-style model modules.
- Analog in-memory arrays.
- Photonic or mixed-signal paths.
- Hybrid programmable/fixed systems.

The same brief also directed the worker to decompose inference into candidate components such as static base weights, low-rank adapters, mixture-of-experts blocks, embedding tables, routers, speculative draft models, attention and key-value cache paths, recurrent hot subgraphs, tokenizers, and verifier or safety models.

### Break-Even Mechanism

The cycle-1 mechanism statement is:

$$N(C_{prog} - C_{phys}) > C_{fixed} + C_{update} + C_{yield} + C_{integration}$$

Here, `N` is the number of served requests or tokens per update interval. `C_prog` is the per-request cost of programmable execution. `C_phys` is the per-request cost of physicalized execution. The right-hand side represents fixed substrate cost, update cost, yield or repair cost, and integration cost.

The brief identifies several special cases:

- If `N = 0`, fixed physicalization cannot win.
- If `C_fixed = 0`, physicalization still depends on per-request costs and penalties.
- If `C_prog <= C_phys`, no finite positive `N` amortizes fixed hardware.
- If the update interval approaches zero, fixed weights become stranded before amortization unless the substrate is reprogrammable.
- If software/runtime optimization saves 20-50% of memory movement, the required volume for physicalization rises.
- If analog conversion, yield, or fallback penalties are high, analog in-memory compute can lose even when array read energy is low.

This is a modeled framing, not a completed simulation result.

### Requested Worker Artifacts

The researcher brief specifies four concrete worker outputs for the next phase.

First, `physicalized-weights/docs/taxonomy_and_null.md` should define the taxonomy, component decomposition, candidate versus non-candidate table, non-physicalization baselines, and a falsification matrix with evidence labels.

Second, `physicalized-weights/scripts/breakeven_model.py` should implement named strategy classes:

- `programmable_unoptimized`
- `software_optimized`
- `programmable_accelerator`
- `fixed_digital_weights`
- `analog_in_memory`
- `hybrid_physicalized_submodel`

The script should sweep assumptions such as model size, tokens per request, requests per day, update cadence, off-chip and local energy per byte, compute energy, software memory-movement savings, utilization, fixed substrate cost, analog conversion overhead, yield and repair factor, and accuracy or fallback penalty.

Third, the script should emit:

- `physicalized-weights/data/breakeven_grid.csv`
- `physicalized-weights/data/breakeven_summary.json`
- `physicalized-weights/data/breakeven_update_volume.png`

Fourth, `physicalized-weights/tests/test_breakeven_model.py` should check edge cases including zero request volume, very frequent updates, 50% software memory savings, zero fixed substrate cost with analog penalties, and stable output schemas.

A Wolfram script, `physicalized-weights/scripts/symbolic_breakeven.wls`, was listed as optional if it clarifies the algebra.

### Tooling Decision

Cycle 1 explicitly deferred Verilator, Yosys, Graphviz, gem5, OpenROAD, CIRCT, MLIR, and Calyx until after the first break-even map identifies a small kernel worth representing. The researcher brief recommends Wolfram for symbolic threshold derivation and Python for the sweep and plot.

This was a sequencing decision: use the smallest inspectable artifact that can produce evidence before introducing heavier architecture or HDL tooling.

## Discussion

Cycle 1 produced a research foundation, not a technical result about whether physicalized weights win. The important contribution was to make the future work falsifiable. The cycle established that physicalization must be evaluated against optimized programmable systems, not against an artificially weak GPU/CPU baseline.

The immediate next cycle should implement the requested taxonomy document and break-even model. Those artifacts will determine whether later work should focus on fixed digital weights, analog in-memory assumptions, hybrid physicalized submodels, or an AI-aware runtime/control plane that routes work across programmable and optional physicalized modules.

No audit report existed for cycle 1. The provided audit input stated: "No prior audit - this is the first cycle. Choose the most foundational sub-topic to start." No worker output existed in the workspace at report time, and no figures were present under the working directory outside the preloaded `wolfram-bridge` examples.

## Open Questions

The record leaves these questions open for later cycles:

- Which physicalization targets survive the first taxonomy screen?
- How high must request volume be for fixed or semi-fixed weights to amortize substrate and update costs?
- How much do 20-50% software/runtime memory savings shift the boundary?
- Does analog in-memory compute remain attractive after conversion, calibration, yield, repair, and fallback penalties?
- Is RISC-V the strongest open control-plane substrate for the first prototype, or only one candidate among several?
- Should the likely product be a physicalized "weight chip," a programmable accelerator, or an AI-aware runtime that can optionally use physicalized modules?

## References

[1] RISC-V International, "RISC-V FAQ," RISC-V International. https://riscv.org/about/faq/

[2] RISC-V International, "RISC-V Technical Specifications," RISC-V International. https://docs.riscv.org/reference/home/index.html

[3] The gem5 Project, "About gem5," gem5. https://www.gem5.org/about/

[4] OpenROAD Project, "OpenROAD," OpenROAD. https://openroad.ergodex.ai/

[5] LLVM CIRCT Project, "CIRCT," GitHub. https://github.com/llvm/circt

[6] IBM Research, "How can analog in-memory computing power transformer models?," IBM Research. https://research.ibm.com/blog/how-can-analog-in-memory-computing-power-transformer-models

## Appendix: Implementation Details

### Code Organization

Cycle 1 established this domain layout:

- `physicalized-weights/docs/`: planned location for taxonomy and design notes.
- `physicalized-weights/scripts/`: planned location for analytical models and generators.
- `physicalized-weights/data/`: planned location for generated CSV, JSON, and plots.
- `physicalized-weights/tests/`: planned location for tests.
- `physicalized-weights/hdl/`: planned location for HDL sketches if later justified.
- `physicalized-weights/stale/`: planned location for archived obsolete artifacts.

No authored physicalized-weights scripts, tests, HDL files, data products, or figures existed at the end of cycle 1.

### Test Results

No worker tests were run in cycle 1 because no worker artifact had been produced yet.

A plan validation command was recorded in the session summary: `python3 -m long_exposure.tools.promise_check .`. It reported 5 events and 7 plan milestones, with expected warnings that later milestones had no ledger events yet.

### File Counts

Root files directly relevant to cycle 1:

| File | Lines | Role |
|---|---:|---|
| `physicalized_model_weights_long_exposure_prompt.md` | 224 | Long-exposure directive |
| `STRUCTURE.md` | 46 | Workspace organization |
| `plan_of_record.md` | 55 | Goals, milestones, success criteria |
| `promise_ledger.jsonl` | 5 | Milestone and run ledger |
| `REFERENCES.md` | 13 | Initial references |
| `physicalized_weights_long_exposure_live.log` | 0 | Empty live log |
| `MANIFEST.md` | 37 | Current workspace snapshot |

The manifest was updated during report preparation as required. It records zero authored research scripts and lists the preloaded `wolfram-bridge` helper modules separately from the physicalized-weights research artifacts.

### Session References

| Source ID | Date | Type | What it contains | Timeline role |
|---|---|---|---|---|
| `767b4ba0-735b-48f8-811a-32cafefc3c0e` | 2026-05-13T01:54:14Z | Researcher session | Full cycle-1 research brief, including sub-topic choice, key questions, worker deliverables, sufficiency criteria, and investigation contract | Primary cycle-1 source |
| `cb62f65f-3ac2-4687-b349-e34a629ecf79` | 2026-05-13T01:55:20Z | Compaction record | Preserved summary of the same researcher work, file changes, validation command, and next steps | Supporting trace and recovery source |
| `.long-exposure-physicalized/telemetry/events.jsonl` | 2026-05-13T01:51:36Z to 01:54:14Z | Telemetry | Run start, cycle start, researcher call completion, model and token metadata | Confirms cycle timing and successful researcher output |
| `promise_ledger.jsonl` | 2026-05-13T01:51:36Z to 01:52:47Z | Ledger | Run start, plan validation, active milestone openings | Confirms milestone state |
| `plan_of_record.md` | 2026-05-13T01:51:36Z | Plan | Goals, milestones, dependencies, out-of-scope constraints | Defines research contract |
| `STRUCTURE.md` | 2026-05-13T01:51:36Z | Workspace structure | Standard folders and `physicalized-weights/` domain folder | Defines artifact organization |

### Cross-Reference Map

- Directive -> `plan_of_record.md`: the directive became goals `G1` through `G5` and milestones `M-TAX-1` through `M-FINAL-1`.
- `plan_of_record.md` -> `promise_ledger.jsonl`: the plan's first active milestones were recorded as ledger events.
- `REFERENCES.md` -> researcher brief: references [1]-[6] were assigned to the taxonomy, open architecture, simulator, flow, compiler, and analog in-memory framing.
- Researcher brief -> future worker artifacts: the brief specifies `taxonomy_and_null.md`, `breakeven_model.py`, generated data files, plot output, tests, and optional Wolfram algebra.
- `STRUCTURE.md` -> `physicalized-weights/`: the domain folder is the target location for future research artifacts.
