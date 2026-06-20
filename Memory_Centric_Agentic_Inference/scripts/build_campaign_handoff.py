# created: 2026-05-12T01:25:00Z
# cycle: 22
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-HANDOFF-1

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LEDGER = ROOT / "promise_ledger.jsonl"

OUTPUTS = {
    "artifact_index": DATA / "handoff_artifact_index.csv",
    "claim_traceability": DATA / "handoff_claim_traceability.csv",
    "reproduction_manifest": DATA / "handoff_reproduction_manifest.csv",
    "open_questions": DATA / "handoff_open_questions.csv",
}

MILESTONE_ORDER = [
    "M-TAX-1",
    "M-LIFE-1",
    "M-COST-1",
    "M-SIM-1",
    "M-SCHED-1",
    "M-ARCH-1",
    "M-TRACE-1",
    "M-QUEUE-1",
    "M-COMP-1",
    "M-PROTO-1",
    "M-CALIB-1",
    "M-SEC-1",
    "M-SYNTH-1",
    "M-EXP-1",
    "M-ENERGY-1",
    "M-SECOPS-1",
    "M-PLAN-1",
    "M-ABI-1",
    "M-ABIINT-1",
    "M-ARCHPKG-1",
    "M-DC12-1",
    "M-PRODTELEM-1",
    "M-FINALPKG-1",
    "M-HANDOFF-1",
]

DEPENDENCIES = {
    "M-HANDOFF-1": "M-FINALPKG-1; M-PRODTELEM-1; M-DC12-1; M-PLAN-1; M-SECOPS-1; M-ENERGY-1; M-SYNTH-1",
    "M-FINALPKG-1": "M-TAX-1; M-LIFE-1; M-COST-1; M-SIM-1; M-SCHED-1; M-ARCH-1; M-TRACE-1; M-QUEUE-1; M-COMP-1; M-PROTO-1; M-CALIB-1; M-SEC-1; M-SYNTH-1; M-EXP-1; M-ENERGY-1; M-SECOPS-1; M-PLAN-1; M-DC12-1; M-PRODTELEM-1",
    "M-PRODTELEM-1": "M-DC12-1; M-ENERGY-1; M-PLAN-1; M-CALIB-1; M-SECOPS-1",
    "M-DC12-1": "M-ENERGY-1; M-PLAN-1; M-CALIB-1; M-EXP-1; M-SECOPS-1",
}

PRODUCERS = {
    "M-FINALPKG-1": "scripts/build_final_architecture_package.py; scripts/plot_final_architecture_package.py",
    "M-HANDOFF-1": "scripts/build_campaign_handoff.py; scripts/plot_campaign_handoff.py",
    "M-PRODTELEM-1": "scripts/build_production_dc12_fixtures.py; scripts/ingest_production_dc12_telemetry.py; scripts/plot_production_dc12_telemetry.py",
    "M-DC12-1": "scripts/local_dc12_proxy_bench.py; scripts/apply_dc12_proxy_calibration.py; scripts/plot_dc12_proxy_calibration.py",
    "M-PLAN-1": "scripts/constrained_memory_planner.py; scripts/plot_constrained_memory_planner.py",
    "M-SECOPS-1": "scripts/security_enforcement_replay.py; scripts/plot_security_enforcement.py",
    "M-ENERGY-1": "scripts/evaluate_energy_economics.py; scripts/plot_energy_economics.py",
    "M-SYNTH-1": "scripts/synthesize_research_agenda.py; scripts/plot_synthesis.py",
    "M-ABI-1": "scripts/build_memory_object_abi.py; scripts/validate_memory_object_abi.py; scripts/plot_memory_object_abi.py",
    "M-ABIINT-1": "scripts/integrate_memory_object_abi.py; scripts/plot_memory_object_abi_integration.py",
    "M-ARCHPKG-1": "scripts/build_architecture_control_plane_progression.py; scripts/plot_architecture_control_plane_progression.py",
}

VERIFIERS = {
    "M-HANDOFF-1": "tests/verify_campaign_handoff.py",
    "M-FINALPKG-1": "tests/verify_final_architecture_package.py",
    "M-PRODTELEM-1": "tests/verify_production_dc12_telemetry.py",
    "M-DC12-1": "tests/verify_dc12_proxy_calibration.py",
    "M-PLAN-1": "tests/verify_constrained_memory_planner.py",
    "M-SECOPS-1": "tests/verify_security_enforcement_replay.py",
    "M-EXP-1": "tests/verify_mexp1_integration.py",
    "M-ABI-1": "tests/verify_memory_object_abi.py",
    "M-ABIINT-1": "tests/verify_memory_object_abi_integration.py",
    "M-ARCHPKG-1": "tests/verify_architecture_control_plane_progression.py",
}

REPRODUCTION_COMMANDS = [
    ("foundation", "python3 scripts/simulate_memory_policies.py", "scripts/simulate_memory_policies.py"),
    ("foundation", "python3 scripts/plot_sim_policy_results.py", "scripts/plot_sim_policy_results.py"),
    ("scheduling", "python3 scripts/evaluate_scheduling_abstractions.py", "scripts/evaluate_scheduling_abstractions.py"),
    ("scheduling", "python3 scripts/plot_scheduling_abstractions.py", "scripts/plot_scheduling_abstractions.py"),
    ("architecture", "python3 scripts/synthesize_architecture_package.py", "scripts/synthesize_architecture_package.py"),
    ("architecture", "python3 scripts/plot_architecture_synthesis.py", "scripts/plot_architecture_synthesis.py"),
    ("trace", "python3 scripts/generate_agentic_trace_v2.py", "scripts/generate_agentic_trace_v2.py"),
    ("trace", "python3 scripts/validate_agentic_trace_v2.py", "scripts/validate_agentic_trace_v2.py"),
    ("trace", "python3 scripts/plot_agentic_trace_v2.py", "scripts/plot_agentic_trace_v2.py"),
    ("queueing", "python3 scripts/simulate_queueing_overheads.py", "scripts/simulate_queueing_overheads.py"),
    ("queueing", "python3 scripts/plot_queueing_overheads.py", "scripts/plot_queueing_overheads.py"),
    ("compression", "python3 scripts/evaluate_compression_strategies.py", "scripts/evaluate_compression_strategies.py"),
    ("compression", "python3 scripts/plot_compression_strategies.py", "scripts/plot_compression_strategies.py"),
    ("runtime", "python3 scripts/runtime_prototype.py", "scripts/runtime_prototype.py"),
    ("runtime", "python3 scripts/plot_runtime_prototype.py", "scripts/plot_runtime_prototype.py"),
    ("calibration", "python3 scripts/build_calibration_map.py", "scripts/build_calibration_map.py"),
    ("calibration", "python3 scripts/plot_calibration_map.py", "scripts/plot_calibration_map.py"),
    ("security", "python3 scripts/evaluate_security_provenance.py", "scripts/evaluate_security_provenance.py"),
    ("security", "python3 scripts/plot_security_provenance.py", "scripts/plot_security_provenance.py"),
    ("energy", "python3 scripts/evaluate_energy_economics.py", "scripts/evaluate_energy_economics.py"),
    ("energy", "python3 scripts/plot_energy_economics.py", "scripts/plot_energy_economics.py"),
    ("security-enforcement", "python3 scripts/security_enforcement_replay.py", "scripts/security_enforcement_replay.py"),
    ("security-enforcement", "python3 scripts/plot_security_enforcement.py", "scripts/plot_security_enforcement.py"),
    ("planner", "python3 scripts/constrained_memory_planner.py", "scripts/constrained_memory_planner.py"),
    ("planner", "python3 scripts/plot_constrained_memory_planner.py", "scripts/plot_constrained_memory_planner.py"),
    ("abi", "python3 scripts/build_memory_object_abi.py", "scripts/build_memory_object_abi.py"),
    ("abi", "python3 scripts/validate_memory_object_abi.py", "scripts/validate_memory_object_abi.py"),
    ("abi", "python3 scripts/plot_memory_object_abi.py", "scripts/plot_memory_object_abi.py"),
    ("abi-integration", "python3 scripts/integrate_memory_object_abi.py", "scripts/integrate_memory_object_abi.py"),
    ("abi-integration", "python3 scripts/plot_memory_object_abi_integration.py", "scripts/plot_memory_object_abi_integration.py"),
    ("control-plane-package", "python3 scripts/build_architecture_control_plane_progression.py", "scripts/build_architecture_control_plane_progression.py"),
    ("control-plane-package", "python3 scripts/plot_architecture_control_plane_progression.py", "scripts/plot_architecture_control_plane_progression.py"),
    ("dc12-proxy", "python3 scripts/local_dc12_proxy_bench.py", "scripts/local_dc12_proxy_bench.py"),
    ("dc12-proxy", "python3 scripts/apply_dc12_proxy_calibration.py", "scripts/apply_dc12_proxy_calibration.py"),
    ("dc12-proxy", "python3 scripts/plot_dc12_proxy_calibration.py", "scripts/plot_dc12_proxy_calibration.py"),
    ("production-telemetry", "python3 scripts/build_production_dc12_fixtures.py", "scripts/build_production_dc12_fixtures.py"),
    ("production-telemetry", "python3 scripts/ingest_production_dc12_telemetry.py", "scripts/ingest_production_dc12_telemetry.py"),
    ("production-telemetry", "python3 scripts/plot_production_dc12_telemetry.py", "scripts/plot_production_dc12_telemetry.py"),
    ("final-package", "python3 scripts/build_final_architecture_package.py", "scripts/build_final_architecture_package.py"),
    ("final-package", "python3 scripts/plot_final_architecture_package.py", "scripts/plot_final_architecture_package.py"),
    ("handoff", "python3 scripts/build_campaign_handoff.py", "scripts/build_campaign_handoff.py"),
    ("handoff", "python3 scripts/plot_campaign_handoff.py", "scripts/plot_campaign_handoff.py"),
    ("validation", "python3 tests/verify_final_architecture_package.py", "tests/verify_final_architecture_package.py"),
    ("validation", "python3 tests/verify_campaign_handoff.py", "tests/verify_campaign_handoff.py"),
    ("validation", "python3 tests/verify_memory_object_abi.py", "tests/verify_memory_object_abi.py"),
    ("validation", "python3 tests/verify_memory_object_abi_integration.py", "tests/verify_memory_object_abi_integration.py"),
    ("validation", "python3 tests/verify_architecture_control_plane_progression.py", "tests/verify_architecture_control_plane_progression.py"),
    ("governance", "python3 -m long_exposure.tools.promise_check .", "promise_ledger.jsonl"),
    ("governance", "python3 -m long_exposure.tools.org_check .", "plan_of_record.md"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def artifact_type(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".py":
        return "script_or_test"
    if suffix == ".md":
        return "narrative"
    if suffix == ".csv":
        return "data"
    if suffix == ".png":
        return "figure"
    if suffix == ".json":
        return "metadata"
    return "artifact"


def evidence_class(milestone: str, path: str) -> str:
    if "production_dc12" in path:
        return "synthetic_fixture_or_contract_ready"
    if "dc12_" in path:
        return "host_local_proxy"
    if milestone in {"M-CALIB-1"}:
        return "sourced"
    if milestone in {"M-LIFE-1", "M-COST-1", "M-QUEUE-1"}:
        return "derived"
    if milestone in {"M-SIM-1", "M-SCHED-1", "M-TRACE-1", "M-COMP-1", "M-ENERGY-1"}:
        return "simulated"
    if milestone in {"M-FINALPKG-1", "M-HANDOFF-1", "M-SYNTH-1"}:
        return "derived_synthesis"
    if milestone in {"M-ABI-1", "M-ABIINT-1", "M-ARCHPKG-1"}:
        return "synthetic_internal_control_plane"
    return "validated_artifact"


def limitation_for(row: dict[str, str]) -> str:
    path = row["artifact_path"]
    if "production_dc12" in path:
        return "Synthetic production-shaped fixtures validate ingestion semantics only; real production_target telemetry is still required."
    if "dc12_" in path:
        return "Host-local proxy result; not GPU/HBM/CXL/datacenter production calibration."
    if row["evidence_class"] in {"simulated", "derived"}:
        return "Model-backed evidence; production calibration remains external unless stated otherwise."
    if row["artifact_type"] == "figure":
        return "Figure is a rendered view of co-located CSV outputs, not independent evidence."
    return "No independent production endorsement implied by this artifact."


def latest_validated_events() -> dict[str, dict[str, object]]:
    events: dict[str, dict[str, object]] = {}
    for line in LEDGER.read_text().splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        milestone = event.get("milestone_id", "")
        if not milestone.startswith("M-") or event.get("status") != "validated":
            continue
        events[milestone] = event
    return events


def build_artifact_index() -> list[dict[str, object]]:
    events = latest_validated_events()
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for milestone in MILESTONE_ORDER:
        event = events.get(milestone)
        artifacts = list(event.get("artifacts", [])) if event else []
        if milestone == "M-HANDOFF-1":
            artifacts = [
                "scripts/build_campaign_handoff.py",
                "scripts/plot_campaign_handoff.py",
                "tests/verify_campaign_handoff.py",
                "final_report.md",
                "data/handoff_artifact_index.csv",
                "data/handoff_claim_traceability.csv",
                "data/handoff_reproduction_manifest.csv",
                "data/handoff_open_questions.csv",
                "data/handoff_artifact_dependency_graph.png",
                "data/handoff_claim_traceability_coverage.png",
                "data/handoff_experiment_upgrade_path.png",
            ]
        if milestone == "M-ARCHPKG-1" and not artifacts:
            artifacts = [
                "scripts/build_architecture_control_plane_progression.py",
                "scripts/plot_architecture_control_plane_progression.py",
                "tests/verify_architecture_control_plane_progression.py",
                "memory-centric-agentic/architecture_control_plane_progression.md",
                "memory-centric-agentic/final_architecture_package.md",
                "final_report.md",
                "data/architecture_control_plane_progression.csv",
                "data/architecture_control_plane_progression.png",
            ]
        for artifact in artifacts:
            if artifact.startswith("/"):
                continue
            key = f"{milestone}:{artifact}"
            if key in seen:
                continue
            seen.add(key)
            atype = artifact_type(artifact)
            eclass = evidence_class(milestone, artifact)
            exists = (ROOT / artifact).exists() or milestone == "M-HANDOFF-1"
            rows.append(
                {
                    "artifact_path": artifact,
                    "artifact_type": atype,
                    "producing_script": PRODUCERS.get(milestone, "see milestone ledger event"),
                    "verifier": VERIFIERS.get(milestone, "ledger validation and downstream handoff verifier"),
                    "milestone": milestone,
                    "evidence_class": eclass,
                    "upstream_dependencies": DEPENDENCIES.get(milestone, ""),
                    "production_readiness_impact": "never sufficient for production_ready without final production_target gates" if eclass != "production_target" else "can support production_ready if all gates pass",
                    "known_limitation": "",
                    "exists": str(exists).lower(),
                }
            )
    for row in rows:
        row["known_limitation"] = limitation_for(row)  # type: ignore[arg-type]
    return rows


def build_claim_traceability() -> list[dict[str, object]]:
    claims = read_csv(DATA / "final_claim_readiness_matrix.csv")
    rows: list[dict[str, object]] = []
    for claim in claims:
        support = [p.strip() for p in claim.get("supporting_artifacts", "").split(";") if p.strip()]
        data_artifacts = [p for p in support if p.endswith(".csv")]
        if not data_artifacts:
            data_artifacts = ["data/final_claim_readiness_matrix.csv"]
        narrative = [p for p in support if p.endswith(".md")]
        narrative.append("memory-centric-agentic/final_architecture_package.md")
        figures = [
            "data/final_claim_readiness_heatmap.png",
            "data/final_architecture_option_readiness.png",
            "data/final_production_experiment_priority.png",
        ]
        rows.append(
            {
                "claim_id": claim["claim_id"],
                "claim": claim["claim"],
                "readiness_label": claim["readiness_label"],
                "evidence_classes": claim["evidence_classes"],
                "production_ready": claim["production_ready"],
                "production_endorsed": "true" if claim["production_ready"] == "true" else "false",
                "data_artifacts": "; ".join(dict.fromkeys(data_artifacts)),
                "narrative_artifacts": "; ".join(dict.fromkeys(narrative)),
                "validation_sources": "tests/verify_final_architecture_package.py; tests/verify_campaign_handoff.py",
                "figures": "; ".join(figures),
                "reproduction_steps": "final-package; handoff; validation",
                "limitation_named": claim.get("basis", "") or "Production endorsement remains blocked without production_target telemetry.",
                "falsification_condition": claim.get("falsification_condition", ""),
            }
        )
    return rows


def build_reproduction_manifest() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for idx, (stage, command, primary) in enumerate(REPRODUCTION_COMMANDS, start=1):
        rows.append(
            {
                "step": idx,
                "stage": stage,
                "command": command,
                "primary_artifact": primary,
                "exists": str((ROOT / primary).exists()).lower(),
                "expected_result": "regenerates or verifies campaign artifact state",
                "production_boundary": "No command can promote synthetic/proxy evidence to production_ready; production_target evidence must pass M-PRODTELEM-1 and M-FINALPKG-1 gates.",
            }
        )
    return rows


def build_open_questions() -> list[dict[str, object]]:
    backlog = read_csv(DATA / "final_production_experiment_backlog.csv")
    rows: list[dict[str, object]] = []
    for row in backlog:
        expected = row["expected_evidence_type"]
        rows.append(
            {
                "rank": row["rank"],
                "open_question": row["experiment"],
                "required_telemetry": row["required_telemetry"],
                "expected_signal": row["risk_retired"],
                "claim_upgrade_path": (
                    f"Can update research readiness for {row['unblocks_claims']} with evidence_class={expected} "
                    "only after the named experiment verifier passes; production_ready requires "
                    "evidence_label=production_target plus ingestion and final readiness gates."
                ),
                "falsification_criteria": row["production_boundary"],
                "current_status": "open_production_calibration_required",
            }
        )
    return rows


def main() -> None:
    write_csv(
        OUTPUTS["artifact_index"],
        build_artifact_index(),
        ["artifact_path", "artifact_type", "producing_script", "verifier", "milestone", "evidence_class", "upstream_dependencies", "production_readiness_impact", "known_limitation", "exists"],
    )
    write_csv(
        OUTPUTS["claim_traceability"],
        build_claim_traceability(),
        ["claim_id", "claim", "readiness_label", "evidence_classes", "production_ready", "production_endorsed", "data_artifacts", "narrative_artifacts", "validation_sources", "figures", "reproduction_steps", "limitation_named", "falsification_condition"],
    )
    write_csv(
        OUTPUTS["reproduction_manifest"],
        build_reproduction_manifest(),
        ["step", "stage", "command", "primary_artifact", "exists", "expected_result", "production_boundary"],
    )
    write_csv(
        OUTPUTS["open_questions"],
        build_open_questions(),
        ["rank", "open_question", "required_telemetry", "expected_signal", "claim_upgrade_path", "falsification_criteria", "current_status"],
    )
    for path in OUTPUTS.values():
        print(rel(path))


if __name__ == "__main__":
    main()
