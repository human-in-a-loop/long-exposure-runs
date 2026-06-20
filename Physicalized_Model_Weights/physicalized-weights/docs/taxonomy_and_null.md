---
created: 2026-05-13T02:05:00Z
cycle: 1
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-TAX-1
---

# Physicalized Weights: Taxonomy, Null Hypothesis, and First Model Frame

## Definition

Physicalizing neural-network inference means moving some stable part of a model or inference path from a fully programmable software kernel over general memory into a hardware structure whose topology, storage, data movement, or compute behavior directly encodes that part of the inference workload. The term includes fixed logic, ROM-like weight storage, semi-fixed FPGA/eFPGA fabrics, near-memory accelerators, analog in-memory arrays, photonic or mixed-signal paths, and hybrids that keep control, fallback, adapters, and frequently changing state programmable.

The useful question is not whether an entire frontier model should be permanently burned into silicon. The useful question is whether any static, high-volume, energy-dominant, approximation-tolerant slice can beat strong programmable baselines after fixed cost, update cadence, yield, utilization, calibration, and software integration are charged honestly.

## Physicalization Levels

| Level | Weight/compute binding | Reprogrammability | Likely role | Main risk |
|---|---:|---:|---|---|
| Fixed digital logic | Weights compiled into gates/datapath constants | None after fabrication | Tiny frozen kernels, validators, safety filters | Stranded by updates |
| ROM-coded weights | Weights stored in mask/programmed ROM near compute | None or factory-level | High-volume frozen submodels | SKU fragmentation |
| SRAM/eDRAM resident weights | Weights kept local to a specialized datapath | Runtime loadable | Near-memory accelerator baseline | May just be a programmable accelerator |
| FPGA/eFPGA overlay | Weights and datapath in bitstream/fabric | Field reconfigurable | Frozen small models, model-specific operators | Lower density and clock/energy efficiency |
| RISC-V/custom accelerator | Programmable host with custom matrix/vector extension | Programmable control, fixed/semi-fixed datapath | Open control-plane substrate | Interface and software complexity |
| Chiplet/cartridge weights | Model slice packaged as module on memory/coherence fabric | Replaceable module | Long-lived domain models or experts | Packaging, bandwidth, version churn |
| Analog in-memory | Weights as conductance/cell state, MAC in array physics | Limited, noisy, calibrated updates | Dense linear algebra with tolerant precision | ADC/DAC, drift, yield, repair |
| Photonic/mixed-signal | Weights as optical/electrical transfer functions | Calibrated, often limited | Very high-throughput matrix paths | Integration, conversion, calibration |
| Hybrid fixed/programmed | Stable submodel physicalized; adapters, routing, KV/cache, fallback programmable | Partial | Most credible near-term shape | Runtime must prove use often enough |

## Inference Component Decomposition

| Component | Physicalization fit | Rationale |
|---|---|---|
| Static base weights | Conditional candidate | High reuse, but frontier update cadence and model churn can dominate amortization. |
| Low-rank adapters/fine-tunes | Weak candidate | Usually tenant- or task-specific and updated more often than base weights. |
| MoE expert blocks | Candidate when stable and hot | A small set of high-traffic stable experts may amortize; long-tail experts likely cannot. |
| Embedding tables | Mixed | Large and memory-heavy, but vocabulary/product changes and irregular access make fixed logic unattractive. |
| Routers/gating | Weak candidate | Control-heavy, distribution-sensitive, and easy to update in software. |
| Speculative draft models | Stronger candidate | Small, high-volume, approximation-tolerant, and can fall back to verifier. |
| Attention/KV paths | Anti-target for fixed weights | Dynamic state, sequence dependence, memory management, and scheduling dominate. |
| Recurrent hot subgraphs | Candidate if stable | Repeated projections or small classifiers can be isolated and tested. |
| Tokenizers/pre/post processing | Weak candidate | Control/string-heavy and already cheap relative to model math for large inference. |
| Safety/verifier models | Candidate | Often smaller, high-volume, and can be versioned more conservatively than primary models. |

## Candidate and Non-Candidate Table

| Target | Candidate? | Why | What would falsify it |
|---|---:|---|---|
| Small frozen draft model | Yes | High request volume, acceptable approximation, verifier fallback exists | Software speculative decoding plus quantization removes most memory savings |
| Safety or policy classifier | Yes | Small, repeated, conservative update cadence possible | Policy updates arrive faster than amortization interval |
| Stable MoE hot expert | Conditional | Reuse concentration may be high | Expert routing distribution shifts or long-tail utilization dominates |
| Domain-specific verifier/reranker | Conditional | Enterprise workloads may be stable and high volume | Per-tenant variants fragment volume |
| Full frontier LLM base | Mostly no | Huge fixed cost, frequent refresh, accuracy sensitivity, supply-chain lag | Only plausible if update cadence is far slower and request volume far higher than assumed |
| KV-cache movement | No for fixed weights | Dynamic per sequence and better handled by memory/runtime systems | N/A: not a fixed-weight structure |
| Routing/control plane | No | Branchy, software-defined, and update-sensitive | N/A unless a tiny stable router dominates energy, which is unlikely |
| Tokenization | No | Irregular string/control workload and low energy share | N/A under this model |

## Strong Non-Physicalization Baselines

1. Optimized programmable serving: quantization, sparsity, batching, prefix caching, KV-cache management, speculative decoding, and model routing reduce memory movement and improve utilization without fixed-weight substrate risk.
2. AI-aware OS/runtime/control plane: schedulers, memory managers, compiler passes, placement policies, and data-center orchestration can reduce waste across existing GPUs/CPUs/accelerators.
3. Programmable accelerators: NPUs, TPUs, vector engines, near-memory engines, and RISC-V-attached accelerators reduce energy while preserving weight updates and software-defined model evolution.
4. Semi-fixed reconfigurable fabrics: FPGA/eFPGA overlays can test whether specialization wins before irreversible fabrication, though with area/energy penalties.

## Strongest Null Hypothesis

Optimized software, runtime, compiler, and programmable-accelerator improvements capture most practical inference gains before physicalized weights can amortize their fixed substrate, integration, yield, and update costs. Under this null, physicalization is not broadly wrong; it is narrow. It only survives for slices with unusually high reuse, slow update cadence, stable interfaces, meaningful memory-movement energy share, tolerable approximation, and cheap fallback.

The null becomes stronger as software memory-movement savings approach 20-50%, as update cadence moves from yearly to weekly/daily, as utilization falls, as yield/repair costs rise, or as analog conversion/fallback penalties erase array-level gains.

## First Break-Even Mechanism

The model for this cycle is:

```text
N * (C_prog - C_phys) > C_fixed + C_update + C_yield + C_integration
```

where `N` is requests served before the next material weight update, `C_prog` is the best programmable per-request cost after software savings, and `C_phys` is the physicalized per-request cost including conversion, utilization, yield/repair, and fallback penalties. If `C_prog <= C_phys`, no finite positive volume amortizes fixed cost. If updates arrive before amortization, fixed weights strand value.

## Falsification Criteria

Early enthusiasm for physicalized weights should be rejected or narrowed if:

- Fixed physicalization wins at `N = 0` while fixed substrate cost is nonzero.
- Frequent updates do not penalize fixed or mask-programmed strategies.
- A 50% software memory-movement saving does not raise the break-even request volume for physicalized strategies.
- Analog in-memory wins even when ADC/DAC conversion, yield/repair, and fallback penalties dominate its array savings.
- The winning region disappears after utilization and update cadence are charged.
- Candidate targets cannot be separated from dynamic control, KV/cache state, tenant-specific adapters, or frequently updated policy logic.

## Placeholder Assumptions

This first cycle uses normalized cost/energy units rather than process-specific joules, dollars, or area. The variables are intentionally parameterized: later cycles should replace defaults with sourced estimates for memory-access energy, package/NRE cost, utilization, yield, and analog conversion overhead. The output is therefore a boundary-finding model, not a device claim.
