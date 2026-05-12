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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def require_text(path: Path, needles: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    assert not missing, f"{path} missing {missing}"


def test_architecture_control_plane_progression() -> None:
    doc = ROOT / "memory-centric-agentic" / "architecture_control_plane_progression.md"
    final_pkg = ROOT / "memory-centric-agentic" / "final_architecture_package.md"
    final_report = ROOT / "final_report.md"
    progress_csv = DATA / "architecture_control_plane_progression.csv"
    progress_png = DATA / "architecture_control_plane_progression.png"

    for path in [doc, final_pkg, final_report, progress_csv, progress_png]:
        assert path.exists(), path

    require_text(
        doc,
        [
            "memory-object ABI validation -> runtime/planner compatibility check -> fail-closed action gating",
            "ABI validation",
            "integration replay",
            "runtime prototype",
            "constrained planner",
            "Option A remains opaque",
            "Option B is a memory-object-aware runtime",
            "Option C is a trajectory/DAG memory fabric",
            "production_credit_allowed=false",
        ],
    )
    require_text(
        final_pkg,
        [
            "## ABI and Action-Gating Control Plane",
            "data/memory_object_abi_integration_results.csv",
            "data/memory_object_abi_runtime_actions.csv",
            "data/memory_object_abi_planner_actions.csv",
            "data/memory_object_abi_integration_failure_modes.csv",
            "data/memory_object_abi_option_boundary.csv",
            "data/memory_object_abi_integration_actions.png",
            "data/memory_object_abi_option_boundary.png",
            "data/memory_object_abi_integration_failures.png",
            "do not grant production calibration",
        ],
    )
    require_text(
        final_report,
        [
            "## ABI Control Plane",
            "data/architecture_control_plane_progression.csv",
            "data/architecture_control_plane_progression.png",
            "python3 tests/verify_memory_object_abi.py",
            "python3 tests/verify_memory_object_abi_integration.py",
            "python3 tests/verify_architecture_control_plane_progression.py",
        ],
    )

    rows = read_csv(progress_csv)
    required_rows = {
        "taxonomy",
        "trace_schema",
        "abi_schema",
        "abi_validation",
        "runtime_prototype_compatibility",
        "constrained_planner_compatibility",
        "abi_integration_replay",
        "final_architecture_package",
        "production_evidence_gatechain",
    }
    required_cols = {
        "stage_id",
        "validated_input",
        "decision_boundary",
        "downstream_action",
        "fail_closed_condition",
        "evidence_label",
        "production_credit_allowed",
    }
    assert required_cols <= set(rows[0]), rows[0]
    assert required_rows <= {row["stage_id"] for row in rows}
    for row in rows:
        assert row["production_credit_allowed"] == "false", row
        assert row["fail_closed_condition"].strip(), row
    gatechain = next(row for row in rows if row["stage_id"] == "production_evidence_gatechain")
    assert "future prerequisite" in gatechain["decision_boundary"]
    assert "production_target" in gatechain["validated_input"]

    integration_artifacts = [
        DATA / "memory_object_abi_integration_results.csv",
        DATA / "memory_object_abi_runtime_actions.csv",
        DATA / "memory_object_abi_planner_actions.csv",
        DATA / "memory_object_abi_integration_failure_modes.csv",
        DATA / "memory_object_abi_option_boundary.csv",
        DATA / "memory_object_abi_integration_actions.png",
        DATA / "memory_object_abi_option_boundary.png",
        DATA / "memory_object_abi_integration_failures.png",
    ]
    for path in integration_artifacts:
        assert path.exists(), path
        if path.suffix == ".png":
            assert path.stat().st_size > 10_000, f"{path} looks blank or trivial"

    assert progress_png.stat().st_size > 10_000, f"{progress_png} looks blank or trivial"

    manifest = read_csv(DATA / "handoff_reproduction_manifest.csv")
    commands = [row["command"] for row in manifest]
    for command in [
        "python3 scripts/build_memory_object_abi.py",
        "python3 scripts/validate_memory_object_abi.py",
        "python3 scripts/integrate_memory_object_abi.py",
        "python3 scripts/plot_memory_object_abi.py",
        "python3 scripts/plot_memory_object_abi_integration.py",
        "python3 tests/verify_memory_object_abi.py",
        "python3 tests/verify_memory_object_abi_integration.py",
        "python3 tests/verify_architecture_control_plane_progression.py",
    ]:
        assert command in commands, command
    assert commands.index("python3 scripts/validate_memory_object_abi.py") < commands.index("python3 scripts/integrate_memory_object_abi.py")
    assert commands.index("python3 scripts/integrate_memory_object_abi.py") < commands.index("python3 scripts/build_final_architecture_package.py")

    artifact_index = read_csv(DATA / "handoff_artifact_index.csv")
    indexed = {row["artifact_path"] for row in artifact_index}
    for path in [
        "scripts/build_memory_object_abi.py",
        "scripts/validate_memory_object_abi.py",
        "scripts/integrate_memory_object_abi.py",
        "tests/verify_memory_object_abi.py",
        "tests/verify_memory_object_abi_integration.py",
        "memory-centric-agentic/architecture_control_plane_progression.md",
        "data/architecture_control_plane_progression.csv",
        "data/architecture_control_plane_progression.png",
    ]:
        assert path in indexed, path

    integration = read_csv(DATA / "memory_object_abi_integration_results.csv")
    assert any(row["case_id"] == "option_a_opaque_baseline" and row["option_boundary"] == "opaque_baseline" for row in integration)
    rejected = [row for row in integration if row["abi_status"] == "rejected"]
    assert rejected, "expected rejected ABI integration rows"
    for row in rejected:
        assert row["runtime_action_count"] == "0", row
        assert row["planner_action_count"] == "0", row
        assert row["downstream_memory_action_count"] == "0", row
        assert row["production_calibrated"] == "false", row
        assert row["production_ready"] == "false", row
        assert row["threshold_success"] == "false", row
        assert row["causal_validity_granted"] == "false", row
        assert row["claim_credit_allowed"] == "false", row


if __name__ == "__main__":
    test_architecture_control_plane_progression()
    print("OK: architecture control-plane progression verified.")
