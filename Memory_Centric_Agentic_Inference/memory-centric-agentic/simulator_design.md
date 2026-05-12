---
created: 2026-05-11T13:21:44Z
cycle: 4
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-SIM-1
---

# Memory Policy Simulator Design

## Scope

This simulator is a compact synthetic bridge from the validated taxonomy, lifetime model, and cost model to policy-level outcomes. It is not a production trace, queueing model, hardware benchmark, or datacenter simulator. Its purpose is to test whether policy decisions change when memory objects carry reuse probability, branch survival, verifier delay, durability horizon, and correctness sensitivity.

## Inputs Consumed

- `memory-centric-agentic/memory_objects.csv`: object classes and qualitative eviction failures.
- `memory-centric-agentic/workload_classes.csv`: workload names, controls, and falsification signals.
- `memory-centric-agentic/lifetime_parameters.csv`: lifetime/reuse concepts used to parameterize synthetic events.
- `memory-centric-agentic/memory_tiers.csv`: tier names and synthetic assumption status.
- `data/cost_model_scenarios.csv`: seed scenario sizes, retained-value scores, energy proxies, dollar proxies, and thesis labels.
- `data/cost_model_sensitivity.csv`: confirms the score surface includes reuse, branch, verifier, durability, correctness, and recomputation axes.

All generated values are synthetic units. No production frequencies, hardware constants, vendor specifications, or measured prices are introduced here.

## Event Schema

Each generated event has:

`run_id, workload_class, time_step, event_type, object_class, object_id, size_units, reuse_probability, branch_fanout, branch_survival, verifier_delay, durability_horizon, correctness_sensitive, recompute_cost, loss_cost`

The generator emits six auditable regimes: single-turn chat control, batch/offline control, RAG, code-agent loop, verification-heavy agent, and multi-agent branch/merge run. Controls contain weights/KV/prefix/scratch-like state only. Agentic regimes introduce retrieved context, tool output, branch state, verifier state, trajectory log, durable workspace, and semantic cache entries.

## Policies

`hbm_first_baseline` prioritizes weights, KV cache, and prefix cache. It treats most non-KV state as spill/recompute and pays correctness or recomputation penalties when those objects are evicted.

`reuse_aware_tiering` scores objects by reuse probability and recomputation avoidance. It can preserve reusable retrieved context and prefix-like state, but it does not directly observe branch survival, verifier delay, durability horizon, or correctness sensitivity.

`branch_verifier_durable_aware` uses reuse plus agentic lifetime fields. It gives additional retention priority to branch state, verifier state, tool output, trajectory log, and durable workspace when survival, delay, horizon, or correctness risk is high.

`cost_proxy_balanced` uses a conservative blended score over retained value, movement, energy proxy, dollar proxy, and risk. It is included as a comparison policy, not as the preferred answer.

## Metrics

For each policy/workload pair the simulator reports:

- total score: retained value minus movement, energy, dollar, recomputation, and correctness-risk penalties.
- retained value score: synthetic value preserved by residency.
- movement score: synthetic transfer and tier movement penalty.
- energy proxy score: synthetic energy-like movement/residency score.
- dollar proxy score: synthetic dollar-like movement/residency score.
- correctness risk score: expected correctness or audit loss from evicted sensitive objects.
- evictions, recomputations, tier transfers, dominant object class, winning policy, and thesis label.

The object breakdown table attributes score contributions by object class so a policy win can be checked for KV-only versus branch/tool/verifier/durable causes.

## Special Cases

The simulator evaluates zero reuse, zero branch survival, zero durable horizon, equal tier costs, zero correctness loss, zero recomputation cost, and context cap saturated with positive durable horizon. These cases are expected to collapse policy differences when the relevant mechanism is removed, except the context-cap case should preserve durable-workspace differences because durable state is not capped by KV context length.

## Limitations

The harness does not model queueing, multi-tenant contention, compression ratios, exact cache-page layout, bandwidth saturation, network topology, or production arrival distributions. It intentionally keeps tier costs as synthetic rankings so downstream scheduling work can inspect policy mechanisms before adding system complexity.
