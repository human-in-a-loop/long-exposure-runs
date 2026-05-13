---
created: 2026-05-13T03:36:00Z
cycle: 1
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-PROTO-1
---

# Prototype Safety-Filter Fast Path

## Scope

This prototype tests the narrow M-ARCH-1 boundary: a fixed safety/filter classifier fast path may compute only a deterministic score, decision, and confidence margin. Version checks, health checks, drift alarms, audit availability, host-forced fallback, and fail-safe routing stay in software/control logic. The prototype is not a production accelerator, policy engine, tokenizer, prompt parser, or main-model decision path.

## Fixed Classifier Form

The fixed kernel is an 8-feature signed int8 dot product with signed int8 weights, a signed accumulator, bias, deterministic threshold tie behavior, and margin-derived confidence:

- `weights = [12, -7, 5, 9, -11, 4, 6, -3]`
- `bias = -10`
- `threshold = 64`
- `decision = block` when `score >= threshold`, otherwise `allow`
- `confidence = abs(score - threshold)`
- route confidence threshold: `16`

The all-zero vector scores `-10`, so bias behavior is explicit. The threshold-equality vector scores exactly `64`, which deterministically maps to raw `block` but routes to fallback because confidence is `0`.

## Interface Assumptions

The prototype inherits the M-ARCH-1 register/control assumptions: the host supplies bounded features, required policy version, health/drift state, fallback availability, audit availability, and fail-safe mode. The HDL core implements no update, rollback, versioning, fallback, or audit logic. That separation is intentional; if the fixed block must absorb that policy complexity, the physicalized target should be demoted.

## Relationship to Fallback Policy

`physicalized-weights/scripts/prototype_safety_filter.py` integrates the fixed classifier with the same fallback conditions used by `fallback_policy_sim.py`: classifier unavailable, host forced fallback, failed health, drift alarm, stale version, low confidence, and audit logging failure invalidate the fast path. Invalid output routes to programmable fallback when available, or to fail-safe when both classifier and fallback are unavailable.

![route distribution for the prototype safety-filter classifier, separating physicalized fast path, programmable fallback, and fail-safe outcomes across nominal and edge-case vectors.](../data/prototype_route_distribution.png)

## Results

| Check | Artifact | Result |
|---|---|---|
| Python golden model | `data/prototype_vectors.csv`, `data/prototype_route_results.csv`, `data/prototype_summary.json` | 16 cases generated; 6 fast path, 8 programmable fallback, 2 fail-safe. |
| Edge vectors | `data/prototype_vectors.csv` | all-zero, max/min signed int8, threshold equality, and near-threshold allow/block cases are explicit. |
| Policy routing | `data/prototype_route_results.csv` | low confidence, stale version, failed health, drift, host-forced fallback, and audit failure route away from fast path. |
| HDL core | `hdl/safety_filter_core.sv` | fixed dot product, threshold compare, margin, confidence only; no policy update or fallback logic. |
| HDL evaluation | `data/hdl_sim_results.csv` | 8 HDL/Yosys-eval rows all match expected golden scores, decisions, margins, and confidences. |
| Verilator | `data/verilator_safety_filter.log` | lint completed; compiled Verilator simulation could not run because this container lacks `make` and a C++ compiler. |
| Yosys synthesis | `data/yosys_safety_filter.log` | RTL checks report no problems; post-techmap stats show 2058 simple cells. |
| Netlist diagram | `data/safety_filter_core_netlist.dot`, `data/safety_filter_core_netlist.png` | Yosys RTL-level Graphviz diagram rendered; full techmapped DOT was too large to render usefully. |
| Tests | `tests/test_prototype_safety_filter.py` | stdlib runner passed 6 checks. |

Baseline comparison uses normalized cost units and deliberately retains feature extraction and audit overhead:

| Baseline | Cases | Fast Path | Fallback | Fail-Safe | Modeled Cost Units |
|---|---:|---:|---:|---:|---:|
| software_optimized | 16 | 0 | 16 | 0 | 400.0 |
| programmable_accelerator | 16 | 0 | 16 | 0 | 368.0 |
| hybrid_physicalized | 16 | 6 | 8 | 2 | 162.0 |
| hybrid_request_volume_zero | 0 | 0 | 0 | 0 | 0.0 |

## Interpretation

The fixed computation is deterministic and isolated: Python and HDL/Yosys outputs match on nominal and edge vectors, including max/min signed int8 and threshold equality. The route distribution is intentionally conservative: only 37.5% of the mixed nominal/edge set uses the physicalized fast path, while low-margin and invalid-policy states route away from it. That supports the architecture boundary but does not prove a hardware win, because this toy set overrepresents edge and failure cases and the cost model is normalized.

The most important positive result is not the dot product; it is that the dot product can remain small while control policy stays outside HDL. The most important negative result is that fallback/control/audit behavior dominates the prototype surface: a design that optimizes only the multiply-add block would be measuring the wrong thing.

## Verification Closure

The Verilator gap is closed in `docs/prototype_verification_closure.md` and `data/prototype_verification_closure.json`. Local compiled Verilator simulation remains blocked because `make` and a C++ compiler are absent, so the prototype does not claim compiled simulation passed. `M-PROTO-1` is validated under an amended contract for this pure combinational core: Verilator lint passes, Yosys eval matches the Python golden vectors, Yosys synthesis/check reports no structural problems, the Graphviz netlist artifacts exist, and the closure hashes bind those results to the current HDL and Python artifacts.

## Promotion and Demotion Criteria

Move toward a detailed accelerator model only if a workload trace shows high fast-path fraction, low fallback rate, stable policy versioning, bounded feature extraction cost, and audit overhead that does not erase the fixed-kernel benefit. Demote or narrow the path if near-threshold cases dominate, policy churn is frequent, software or programmable accelerator baselines approach the same normalized cost, or the HDL must absorb mutable policy logic.
