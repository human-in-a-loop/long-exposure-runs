---
created: 2026-05-11T12:35:00Z
cycle: 1
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-LIFE-1
---

# State Lifetime and Reuse-Distance Model

This model treats an agentic inference run as a set of memory objects rather than a single request. For object `i`:

`O_i = {class_i, S_i(t), b_i, e_i, R_i(t), P_i(t), C_evict_i}`

where `S_i(t)` is live byte size, `b_i` and `e_i` are birth and death events, `R_i(t)` is the reuse process, `P_i(t)` is a symbolic placement state, and `C_evict_i` is an eviction consequence class. Derived quantity:

`E[L_i(t)] = E[S_i(t) * 1(b_i <= t < e_i)]`

Expected retained value is modeled symbolically as:

`V_i(t) = Pr(reuse_i before eviction) * C_recompute_i + Pr(correctness_sensitive_i) * C_loss_i - C_residency_i`

This cycle leaves `C_residency_i`, hardware tier constants, compression ratios, and placement policies symbolic for `M-COST-1` and `M-SIM-1`.

## Core Equations

Derived linear KV growth with context cap:

`L_KV(T) = s_kv * Min[T, T_max]`

Derived prefix cache expected retained value under Poisson reuse rate `lambda` and eviction horizon `H_e`:

`V_prefix = (1 - Exp[-lambda * H_e]) * C_prefill - C_residency_prefix`

Special cases: if `lambda = 0`, reuse value is zero; if the prefix is pinned or has infinite reuse horizon, reuse probability tends to one and retained value tends to `C_prefill - C_residency_prefix`.

Assumed branch-state process with fanout `f`, branch survival probability `p_s`, verifier delay `d_v`, merge probability `p_m`, and per-branch state bytes `s_b`:

`E[L_branch] = f * p_s * s_b * (d_v + p_m * d_merge)`

The `d_v` term captures state retained until verification; the merge tail represents surviving branch evidence retained for downstream synthesis. If `p_s = 0`, the term collapses to zero; if `f = 1`, it becomes a linear single-candidate verification term, not a branch fanout term.

Assumed durable workspace growth with artifact growth rate `g_d`, retention horizon `H`, and initial bytes `D_0`:

`L_durable(H) = D_0 + g_d * H`

This term is independent of the model context cap unless a later policy explicitly summarizes or deletes durable artifacts.

## Object Mapping

| Object class | Lifetime expression | Reuse process | Eviction consequence |
|---|---|---|---|
| weights | `S_w * 1(model loaded)` | shared popularity process `R_model` | cold start or reroute |
| KV cache | `s_kv * Min[T, T_max]` | exact continuation or branch continuation | prefill recomputation or truncation |
| prefix cache | `S_prefix * 1(valid prefix)` | Poisson/exact template reuse `lambda_prefix` | repeated prefill |
| retrieved context | `S_ret * 1(corpus valid and request/project active)` | query/corpus locality `lambda_ret` | repeated retrieval or stale evidence |
| tool output | `S_tool(t)` over audit/replay horizon | verification and report reuse | lost provenance or rerun |
| intermediate scratch | `S_scratch * 1(substep active)` | retry-local reuse | rerun or transient spike |
| branch state | `f * p_s * s_b * (d_v + p_m * d_merge)` | survival and merge-conditioned reuse | lost alternative or biased merge |
| verifier state | `S_verifier * n_candidates * d_v` | retry/regression reuse | missed counterexample or repeated validation |
| trajectory log | `g_traj * H_audit` | audit, replay, resume | broken reproducibility |
| durable workspace | `D_0 + g_d * H` | project/session reuse | correctness loss or broken dependency |
| semantic cache entry | `S_sem * (1 - invalidation_probability)` | approximate semantic reuse `lambda_sem` | stale or wrong reuse |

## Collapse Conditions

The model collapses to ordinary serving when branch probability and survival are zero, durable growth is zero, semantic/retrieval/tool reuse rates are zero, and the only live state is weights plus capped linear KV and transient scratch. This corresponds to single-turn chat, batch summarization, and many offline inference regimes.

The memory-centric thesis is strengthened when expected retained value or live bytes is dominated by branch state, verifier state, tool output, trajectory log, durable workspace, prefix cache, retrieved context, or semantic cache entries whose lifetimes and correctness risk are not reducible to current token count.

## Derived vs. Assumed Terms

Derived in this cycle: object interval form, expected live bytes, capped KV expression, prefix reuse probability, special-case reductions, and control-regime collapse.

Assumed for modeling probes: branch survival is Bernoulli with parameter `p_s`, branch merge contribution is proportional to `p_m * d_merge`, durable artifacts grow linearly at rate `g_d`, and reuse processes are summarized by scalar rates or horizons. These assumptions are deliberately simple so `M-SIM-1` can replace them with richer workload generators.
