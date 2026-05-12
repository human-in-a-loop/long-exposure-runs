---
created: 2026-05-12T13:37:27Z
cycle: 42
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-ARCHPKG-1
---

# Architecture Control-Plane Progression

This package refresh ties the validated memory-centric architecture to the executable control-plane chain introduced by `M-ABI-1` and `M-ABIINT-1`: memory-object ABI validation -> runtime/planner compatibility check -> fail-closed action gating. The point is mechanism traceability. It is not a production-readiness upgrade.

The progression starts with the taxonomy and trace schema, which define what must be visible about weights, KV/prefix state, retrieved context, tool outputs, branch state, verifier state, trajectory logs, semantic cache entries, and durable workspace artifacts. `M-ABI-1` turns those objects into an explicit runtime/compiler/planner contract. `M-ABIINT-1` then feeds accepted, advisory-only, and rejected contracts through the runtime prototype and constrained planner so rejected contracts stop before placement, reuse, compression, migration, or retention actions.

## Option Boundary

- Option A remains opaque conventional request/model/KV execution. It may run without a full memory-object ABI and emits no object-level placement, reuse, compression, migration, or retention action in the ABI integration replay.
- Option B is a memory-object-aware runtime. It requires ABI-admissible object contracts before object-local placement, reuse, compression, and retention actions.
- Option C is a trajectory/DAG memory fabric. It requires branch/dependency-admissible objects before DAG-aware migration, dependency-resolution, reuse, compression, and retention actions.

## Progression Table

| Layer | Artifact | Input contract | Output decision | Fail-closed condition | Evidence label | Production-credit status |
|---|---|---|---|---|---|---|
| Taxonomy and object model | `memory-centric-agentic/taxonomy.md`; `memory-centric-agentic/memory_objects.csv` | Workload and object classes | Object identity and tiering implications | Missing class remains unmodeled | validated_artifact | false |
| Trace schema | `memory-centric-agentic/trace_schema.md` | Trace-v2 memory-object events | Signals available to runtime/planner | Invalid trace rows stop downstream credit | synthetic_trace_contract | false |
| ABI schema | `memory-centric-agentic/memory_object_abi.md` | Runtime object contract fields | Option A opaque or B/C contract-required boundary | Mandatory gaps cannot be planner-ready | synthetic_contract | false |
| ABI validation | `scripts/validate_memory_object_abi.py`; `tests/verify_memory_object_abi.py` | ABI examples and schema constraints | Accepted or rejected contract | Missing mandatory fields, tenant mismatch, unsafe compression, dangling branch, retention-policy gaps, or production labels reject | synthetic_contract | false |
| Runtime compatibility | `scripts/runtime_prototype.py` | Accepted object identity and policy inputs | Runtime placement/reuse/compression/retention candidates | Rejected ABI rows emit zero runtime actions | validated_artifact | false |
| Constrained planner compatibility | `scripts/constrained_memory_planner.py` | Planner constraints and accepted objects | Planner placement/reuse/compression/migration/retention candidates | Infeasible, unsafe, or unauthorized objects emit no planner actions | validated_artifact | false |
| ABI integration replay | `scripts/integrate_memory_object_abi.py`; `tests/verify_memory_object_abi_integration.py` | ABI validation results plus runtime/planner checks | Fail-closed action gating for Options B/C | Rejected contracts produce zero downstream memory actions | synthetic_integration_replay | false |
| Final architecture package | `memory-centric-agentic/final_architecture_package.md` | Validated mechanism stack and readiness boundaries | Mechanism plausibility and production research agenda | Synthetic/internal evidence cannot produce production credit | derived_synthesis | false |
| Production evidence gatechain | `memory-centric-agentic/evidence_gatechain.md`; `memory-centric-agentic/production_target_replay.md` | Future trusted production_target telemetry and artifacts | Future production claim candidacy only after all gates pass | Absent, stale, drifted, non-production, or incomplete evidence blocks claims | future_production_target_prerequisite | false |

## Reproduction Path

Run the ABI path in dependency order:

1. `python3 scripts/build_memory_object_abi.py`
2. `python3 scripts/validate_memory_object_abi.py`
3. `python3 scripts/integrate_memory_object_abi.py`
4. `python3 scripts/plot_memory_object_abi.py`
5. `python3 scripts/plot_memory_object_abi_integration.py`
6. `python3 tests/verify_memory_object_abi.py`
7. `python3 tests/verify_memory_object_abi_integration.py`
8. `python3 scripts/build_architecture_control_plane_progression.py`
9. `python3 scripts/plot_architecture_control_plane_progression.py`
10. `python3 tests/verify_architecture_control_plane_progression.py`

The integration replay outputs are `data/memory_object_abi_integration_results.csv`, `data/memory_object_abi_runtime_actions.csv`, `data/memory_object_abi_planner_actions.csv`, `data/memory_object_abi_integration_failure_modes.csv`, and `data/memory_object_abi_option_boundary.csv`. The rendered views are `data/memory_object_abi_integration_actions.png`, `data/memory_object_abi_option_boundary.png`, and `data/memory_object_abi_integration_failures.png`.

## Failure Modes and Falsification

The control-plane packaging is falsified if the final package implies ABI integration is production evidence, omits Option A opacity, omits rejected-contract zero-action behavior, lacks reproduction paths for ABI integration, or references integration artifacts without tests proving they exist. Mechanism plausibility for Options B/C is strengthened by ABI and integration evidence, but every current row remains synthetic/internal or derived package evidence with `production_credit_allowed=false`.
