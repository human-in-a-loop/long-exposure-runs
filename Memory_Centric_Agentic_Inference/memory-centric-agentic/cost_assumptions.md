---
created: 2026-05-11T13:02:00Z
cycle: 3
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-COST-1
---

# Cost Model Assumptions

## Sourced Facts

No external hardware, datacenter, or production-trace constants are used in this cycle. The model is symbolic plus synthetic, so no entries were added to `REFERENCES.md`.

## Derived Variables

The cost layer consumes the `M-LIFE-1` variables: live bytes `L_i(t)`, reuse probability `P_reuse_i`, branch survival `p_s`, branch fanout `f`, verifier delay `d_v`, merge probability `p_m`, durability horizon `H`, and context cap `T_max`.

For object `i` in tier `k`, the retained-value condition is derived as:

`P_reuse_i C_recompute_i + P_correct_i C_loss_i > C_residency_i,k + C_transfer_i,k + C_bandwidth_delay_i,k`.

The left side is value preserved by keeping state available. The right side is the tiering cost of preserving it.

## Synthetic Tier Ratios

Synthetic ratios are used only for scenario ranking and sensitivity sweeps. They are dimensionless placeholders, not measured constants:

- `HBM_GPU_memory`: high residency pressure, low transfer/bandwidth penalty for active decode.
- `CPU_DRAM`: lower residency pressure, moderate movement penalty.
- `CXL_or_pooled_memory`: medium residency pressure, higher movement penalty, shared scope.
- `NVMe_local`: low residency pressure, high movement penalty, persistent local scope.
- `remote_object_store`: low residency pressure, very high movement penalty, durable shared scope.
- `durable_workspace_store`: low residency pressure, high access penalty, correctness-oriented persistence.
- `semantic_cache`: index and staleness cost dominate byte residency.

## Symbolic Variables

Tier variables remain symbolic in `memory_tiers.csv`: capacity `K_k`, bandwidth `B_k`, latency `A_k`, energy per byte `E_k`, dollar cost `D_k`, and per-byte residency price `R_k`.

Object variables remain symbolic in formulas: object bytes `S_i`, expected live bytes `L_i`, transfer bytes `X_i`, reuse probability `P_reuse_i`, correctness probability `P_correct_i`, recomputation cost `C_recompute_i`, and loss cost `C_loss_i`.

The generated scenario table reports synthetic `energy_proxy_score` and `dollar_proxy_score` from tier rankings. These are dimensionless placeholders for sensitivity analysis, not measured joules, watts, dollars, or service costs.

## Deferred Assumptions

The following are intentionally deferred to later cycles:

- production trace frequencies for agent branches, tool calls, verifier loops, and durable artifact reuse;
- hardware vendor constants for bandwidth, latency, capacity, energy, and cost;
- compression ratios and tier-specific encoding overheads;
- placement and scheduling policies beyond simple scenario best-tier labels;
- queueing effects, interference, preemption, and multi-tenant contention.
