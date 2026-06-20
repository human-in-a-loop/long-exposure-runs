# created: 2026-05-12T13:37:27Z
# cycle: 42
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ARCHPKG-1

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOC = ROOT / "memory-centric-agentic" / "architecture_control_plane_progression.md"
CSV_OUT = DATA / "architecture_control_plane_progression.csv"

ROWS = [
    {
        "stage_id": "taxonomy",
        "layer": "Workload and memory-object taxonomy",
        "artifact": "memory-centric-agentic/taxonomy.md; memory-centric-agentic/memory_objects.csv",
        "validated_input": "agentic workload classes and memory-object classes",
        "decision_boundary": "which state deserves object identity, lifetime, reuse, and tiering metadata",
        "downstream_action": "feeds trace schema, lifetime model, architecture options, and ABI object classes",
        "fail_closed_condition": "missing workload/object class is treated as an unmodeled regime rather than an endorsed architecture path",
        "evidence_label": "validated_artifact",
        "production_credit_allowed": "false",
    },
    {
        "stage_id": "trace_schema",
        "layer": "Trace and instrumentation contract",
        "artifact": "memory-centric-agentic/trace_schema.md; scripts/generate_agentic_trace_v2.py; scripts/validate_agentic_trace_v2.py",
        "validated_input": "trace-v2 events with object, lifetime, reuse, branch, verifier, and durable fields",
        "decision_boundary": "whether traces expose the memory signals needed by object and trajectory planning",
        "downstream_action": "feeds runtime prototype, security enforcement, constrained planner, and ABI examples",
        "fail_closed_condition": "missing or inconsistent trace fields become invalid trace rows, not placement credit",
        "evidence_label": "synthetic_trace_contract",
        "production_credit_allowed": "false",
    },
    {
        "stage_id": "abi_schema",
        "layer": "Memory-object ABI schema",
        "artifact": "memory-centric-agentic/memory_object_abi.md; scripts/build_memory_object_abi.py; data/memory_object_abi_schema.csv",
        "validated_input": "memory-object contract fields for identity, lineage, tenant, lifetime, compression, tiers, and evidence label",
        "decision_boundary": "Option A may stay opaque; Options B/C require planner-admissible memory-object contracts",
        "downstream_action": "emits ABI examples and field constraints for validation",
        "fail_closed_condition": "mandatory field gaps or illegal production evidence labels cannot be represented as planner-ready contracts",
        "evidence_label": "synthetic_contract",
        "production_credit_allowed": "false",
    },
    {
        "stage_id": "abi_validation",
        "layer": "ABI validation",
        "artifact": "scripts/validate_memory_object_abi.py; tests/verify_memory_object_abi.py; data/memory_object_abi_validation_results.csv",
        "validated_input": "ABI examples and schema constraints",
        "decision_boundary": "accepted contract, rejected contract, or Option A opaque path",
        "downstream_action": "accepted B/C objects may be tested by runtime/planner integration; rejected objects stop here",
        "fail_closed_condition": "missing mandatory field, tenant mismatch, unsafe lossy compression, dangling branch parent, durable retention without policy, or production evidence label in runtime ABI",
        "evidence_label": "synthetic_contract",
        "production_credit_allowed": "false",
    },
    {
        "stage_id": "runtime_prototype_compatibility",
        "layer": "Runtime prototype compatibility",
        "artifact": "memory-centric-agentic/runtime_prototype.md; scripts/runtime_prototype.py; data/runtime_policy_decisions.csv",
        "validated_input": "object registry and policy-loop decisions over synthetic traces",
        "decision_boundary": "whether an admitted object can drive registry placement, reuse, compression, and retention actions",
        "downstream_action": "runtime action candidates for ABI integration replay",
        "fail_closed_condition": "opaque Option A emits no object-level memory action; rejected ABI objects emit no runtime action",
        "evidence_label": "validated_artifact",
        "production_credit_allowed": "false",
    },
    {
        "stage_id": "constrained_planner_compatibility",
        "layer": "Constrained memory planner compatibility",
        "artifact": "memory-centric-agentic/constrained_memory_planning.md; scripts/constrained_memory_planner.py; data/memory_plan_actions.csv",
        "validated_input": "security, compression, queueing, tier, and planner constraints",
        "decision_boundary": "whether placement, reuse, compression, migration, and retention are admissible under constraints",
        "downstream_action": "planner action candidates for ABI integration replay",
        "fail_closed_condition": "infeasible constraints, unsafe compression, security denial, or missing contract stop planner actions",
        "evidence_label": "validated_artifact",
        "production_credit_allowed": "false",
    },
    {
        "stage_id": "abi_integration_replay",
        "layer": "ABI-to-action integration replay",
        "artifact": "memory-centric-agentic/memory_object_abi_integration.md; scripts/integrate_memory_object_abi.py; tests/verify_memory_object_abi_integration.py",
        "validated_input": "ABI validation results plus runtime and constrained-planner compatibility checks",
        "decision_boundary": "ABI validation -> runtime/planner compatibility check -> fail-closed action gating",
        "downstream_action": "accepted Option B/C contracts emit object-aware memory actions; Option C may emit DAG dependency/migration actions",
        "fail_closed_condition": "rejected ABI rows produce zero placement, reuse, compression, migration, and retention actions",
        "evidence_label": "synthetic_integration_replay",
        "production_credit_allowed": "false",
    },
    {
        "stage_id": "final_architecture_package",
        "layer": "Final architecture package",
        "artifact": "memory-centric-agentic/final_architecture_package.md; data/final_claim_readiness_matrix.csv",
        "validated_input": "validated mechanism stack, production-readiness gates, ABI control-plane boundary",
        "decision_boundary": "mechanism plausibility versus production architecture endorsement",
        "downstream_action": "documents Option A/B/C readiness and open production experiments",
        "fail_closed_condition": "any synthetic, proxy, ABI, or integration evidence attempting production credit remains blocked",
        "evidence_label": "derived_synthesis",
        "production_credit_allowed": "false",
    },
    {
        "stage_id": "production_evidence_gatechain",
        "layer": "Production evidence gatechain",
        "artifact": "memory-centric-agentic/evidence_gatechain.md; memory-centric-agentic/production_target_replay.md; memory-centric-agentic/claim_expiry_revalidation.md",
        "validated_input": "future real production_target telemetry with root enrollment, attestation, intake, timing, redaction, uncertainty, causal, artifact, replay, and lifecycle gates",
        "decision_boundary": "future prerequisite for production calibration and claim support",
        "downstream_action": "may evaluate production claim candidacy only if real trusted production material exists and every gate passes",
        "fail_closed_condition": "no real production bundle, non-production label, missing evidence artifact, failed gate, stale TTL, or deployment drift blocks claim support",
        "evidence_label": "future_production_target_prerequisite",
        "production_credit_allowed": "false",
    },
]


def write_csv() -> None:
    fields = [
        "stage_id",
        "layer",
        "artifact",
        "validated_input",
        "decision_boundary",
        "downstream_action",
        "fail_closed_condition",
        "evidence_label",
        "production_credit_allowed",
    ]
    DATA.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ROWS)


def write_doc() -> None:
    DOC.write_text(
        """---
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
""",
        encoding="utf-8",
    )


def main() -> None:
    write_csv()
    write_doc()
    print(CSV_OUT.relative_to(ROOT))
    print(DOC.relative_to(ROOT))


if __name__ == "__main__":
    main()
