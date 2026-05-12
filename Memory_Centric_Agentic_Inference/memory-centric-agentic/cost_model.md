---
created: 2026-05-11T13:02:00Z
cycle: 3
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-COST-1
---

# Heterogeneous Memory Cost Model

## Core Expression

Claim label: derived.

For memory object `i`, tier `k`, and placement policy `p`:

`C_total(i,k,p) = C_residency + C_transfer + C_bandwidth_delay + C_recompute + C_eviction_loss + C_staleness_or_correctness_risk`.

For downstream reporting, the model also emits non-calibrated proxy projections:

`C_energy_proxy(i,k) = X_i E_k + E[L_i(t)] H_i E_idle_k`

`C_dollar_proxy(i,k) = E[L_i(t)] H_i D_k`

These proxy terms are synthetic/symbolic and are not added to `C_total` unless a later calibrated model assigns commensurate units.

The useful retention inequality is:

`P_reuse_i C_recompute_i + P_correct_i C_loss_i > C_residency(i,k) + C_transfer(i,k) + C_bandwidth_delay(i,k)`.

Interpretation: keep or place an object in a more useful tier when avoided recomputation plus avoided correctness/audit loss exceeds the cost of residency and movement. This is a symbolic decision rule, not a measured hardware claim.

## Term Definitions

Claim label: derived.

- `C_residency(i,k) = E[L_i(t)] R_k H_i`, where `R_k` is synthetic per-byte tier pressure and `H_i` is the relevant lifetime horizon.
- `C_transfer(i,k) = X_i M_k`, where `X_i` is transferred bytes and `M_k` is synthetic movement penalty for tier `k`.
- `C_bandwidth_delay(i,k) = X_i / B_k + A_k N_access_i`, left symbolic in the document and approximated by a dimensionless `bandwidth_delay_ratio` in the synthetic sweep.
- `C_recompute(i) = (1 - I_resident_i) P_reuse_i C_recompute_i`, the expected cost paid after eviction when reuse occurs.
- `C_eviction_loss(i) = P_correct_i C_loss_i`, used when eviction can break auditability, provenance, verification, or durable dependencies.
- `C_staleness_or_correctness_risk(i) = P_stale_i C_stale_i`, most relevant to retrieved context and semantic cache entries.
- `C_energy_proxy(i,k)` and `C_dollar_proxy(i,k)` are dimensionless reporting fields generated from symbolic `E_k`, `E_idle_k`, and `D_k` placeholders so later simulators can compare energy/cost sensitivity without treating the numbers as sourced facts.

`M-LIFE-1` supplies `E[L_i(t)]`, `P_reuse_i`, branch-conditioned survival, verifier delay, durability horizon, and context-cap behavior. This layer adds tier and consequence costs.

## Tier Abstraction

Claim label: assumed/synthetic.

The downstream simulator can start with seven tiers: `HBM/GPU memory`, `CPU DRAM`, `CXL_or_pooled_memory`, `NVMe_local`, `remote_object_store`, `durable_workspace_store`, and `semantic_cache`. Constants are symbols in `memory_tiers.csv`; synthetic rankings in `scripts/cost_model.wls` are only for regime classification.

## Object-Specific Interpretations

Claim labels below are derived from the taxonomy unless noted.

| Object | Dominant cost terms | Memory-centric distinction |
|---|---|---|
| weights | residency, capacity pressure, cold-start transfer | Mostly ordinary serving; shared popularity and routing dominate. |
| KV cache | residency, bandwidth-delay, prefill recomputation | Ordinary serving explains much of the cost unless branch survival makes KV state uncertain and reusable. |
| prefix cache | reuse-weighted recomputation avoidance | Memory-centric value rises with exact prefix reuse or pinned system/tool prefixes. |
| retrieved context | transfer, staleness, repeated retrieval | Agentic value appears when project locality and provenance matter beyond one prompt. |
| tool output | recomputation, durable transfer, correctness loss | Not a normal cache miss when eviction loses evidence, replay, or expensive tool results. |
| intermediate scratch | peak residency, retry recomputation | Usually transient; memory-centric value weak unless retry probability or peak pressure is high. |
| branch state | branch-conditioned residency, recomputation, biased-merge loss | Cost depends on fanout, survival, verifier delay, and merge probability rather than token count alone. |
| verifier state | correctness-sensitive loss, repeated validation | Eviction can cause missed counterexamples or repeated tests, not just latency. |
| trajectory log | durable residency, audit/replay loss | Persistent across context windows; cost is tied to audit horizon and resume needs. |
| durable workspace | durable residency, transfer, broken-dependency loss | Context cap does not remove it; placement matters over project horizon. |
| semantic cache entry | staleness, approximate reuse, index residency | Benefit is semantic locality minus wrong-reuse risk; not reducible to exact KV reuse. |

## Boundary Cases

Claim label: derived.

The formulas intentionally collapse under controls:

- zero transfer cost removes movement advantage;
- infinite bandwidth removes bandwidth-delay advantage;
- zero reuse removes recomputation-avoidance value;
- perfect reuse or pinned prefix maximizes reuse value;
- zero durable state removes workspace and trajectory pressure;
- equal tier costs remove placement preference;
- context cap unsaturated yields linear KV pressure, while saturation caps KV bytes;
- zero correctness loss turns tool/verifier/trajectory objects into ordinary recompute caches;
- zero recomputation cost leaves only correctness and residency terms.

## Falsification Conditions

Claim label: derived/speculative.

The memory-centric thesis is weakened if controls and agentic scenarios remain dominated by weights plus capped KV after nonzero branch survival, verifier delay, tool-output reuse, and durable horizon are introduced. It is narrowed if benefit appears only from arbitrary correctness-loss multipliers. It is supported in this model when controls collapse but branch/tool/verifier/durable scenarios show distinct dominant terms under transparent synthetic ratios.
