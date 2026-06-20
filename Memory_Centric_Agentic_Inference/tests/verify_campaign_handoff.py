# created: 2026-05-12T01:25:00Z
# cycle: 22
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-HANDOFF-1

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def split_paths(value: str) -> list[str]:
    return [p.strip() for p in value.split(";") if p.strip()]


def assert_columns(rows: list[dict[str, str]], required: set[str], path: Path) -> None:
    assert rows, f"{path} is empty"
    missing = required - set(rows[0])
    assert not missing, f"{path} missing columns {missing}"


def command_target(command: str, primary_artifact: str) -> Path:
    if primary_artifact.endswith(".py") or primary_artifact.endswith(".jsonl") or primary_artifact.endswith(".md"):
        return ROOT / primary_artifact
    match = re.search(r"(scripts|tests)/[A-Za-z0-9_./-]+\.py", command)
    if match:
        return ROOT / match.group(0)
    return ROOT / primary_artifact


def test_campaign_handoff() -> None:
    artifact_index = read_csv(DATA / "handoff_artifact_index.csv")
    claims = read_csv(DATA / "handoff_claim_traceability.csv")
    manifest = read_csv(DATA / "handoff_reproduction_manifest.csv")
    questions = read_csv(DATA / "handoff_open_questions.csv")
    final_claims = read_csv(DATA / "final_claim_readiness_matrix.csv")

    assert_columns(artifact_index, {"artifact_path", "artifact_type", "producing_script", "verifier", "milestone", "evidence_class", "upstream_dependencies", "production_readiness_impact", "known_limitation", "exists"}, DATA / "handoff_artifact_index.csv")
    assert_columns(claims, {"claim_id", "readiness_label", "evidence_classes", "production_ready", "production_endorsed", "data_artifacts", "narrative_artifacts", "validation_sources", "figures", "limitation_named"}, DATA / "handoff_claim_traceability.csv")
    assert_columns(manifest, {"step", "stage", "command", "primary_artifact", "exists", "production_boundary"}, DATA / "handoff_reproduction_manifest.csv")
    assert_columns(questions, {"rank", "open_question", "required_telemetry", "expected_signal", "claim_upgrade_path", "falsification_criteria"}, DATA / "handoff_open_questions.csv")

    missing = [row["artifact_path"] for row in artifact_index if row["exists"] != "true" or not (ROOT / row["artifact_path"]).exists()]
    assert not missing, f"artifact index lists missing files: {missing[:10]}"

    final_claim_keys = {(r["claim_id"], r["claim"]) for r in final_claims}
    handoff_claim_keys = {(r["claim_id"], r["claim"]) for r in claims}
    assert final_claim_keys <= handoff_claim_keys, "not every final claim appears in handoff traceability"

    for row in claims:
        assert split_paths(row["data_artifacts"]), row
        assert split_paths(row["narrative_artifacts"]), row
        assert split_paths(row["validation_sources"]), row
        assert row["limitation_named"].strip(), row
        for field in ["data_artifacts", "narrative_artifacts", "validation_sources", "figures"]:
            for path in split_paths(row[field]):
                assert (ROOT / path).exists(), f"{row['claim_id']} references missing {path}"
        if any(label in row["evidence_classes"] for label in ["synthetic_production_fixture", "host_local_proxy"]):
            assert row["production_ready"] == "false"
            assert row["production_endorsed"] == "false"

    steps = [int(r["step"]) for r in manifest]
    assert steps == sorted(steps) and steps == list(range(1, len(steps) + 1))
    stages = [r["stage"] for r in manifest]
    assert stages.index("final-package") < stages.index("handoff") < stages.index("validation")
    for row in manifest:
        assert row["exists"] == "true", row
        assert command_target(row["command"], row["primary_artifact"]).exists(), row
        assert "production_target" in row["production_boundary"], row

    for row in questions:
        assert "production_ready requires evidence_label=production_target" in row["claim_upgrade_path"], row

    report = (ROOT / "final_report.md").read_text()
    for required in [
        "data/handoff_artifact_index.csv",
        "data/handoff_claim_traceability.csv",
        "data/handoff_reproduction_manifest.csv",
        "Option B/C are not production recommendations",
        "zero final claims are production-ready",
        "production_target",
    ]:
        assert required in report, required

    for row in final_claims:
        if any(label in row["evidence_classes"] for label in ["synthetic_production_fixture", "host_local_proxy"]):
            assert row["production_ready"] == "false", row

    for path in [
        DATA / "handoff_artifact_dependency_graph.png",
        DATA / "handoff_claim_traceability_coverage.png",
        DATA / "handoff_experiment_upgrade_path.png",
    ]:
        assert path.exists(), path
        assert path.stat().st_size > 10_000, f"{path} looks blank or trivial"


if __name__ == "__main__":
    test_campaign_handoff()
    print("OK: campaign handoff package verified.")
