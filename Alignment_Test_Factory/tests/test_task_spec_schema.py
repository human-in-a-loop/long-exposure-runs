# created: 2026-05-13T21:45:00Z
# cycle: 2
# run_id: run-2026-05-13T204826Z
# agent: worker
# milestone: M-3

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
FACTORY = ROOT / "alignment-test-factory"
SRC = FACTORY / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from alignment_test_factory.schemas import TaskSpec  # noqa: E402


def load_spec(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(path: Path) -> TaskSpec:
    return TaskSpec.model_validate(load_spec(path))


def test_valid_examples_pass() -> None:
    paths = sorted((FACTORY / "examples" / "valid").glob("*.json"))
    assert len(paths) >= 3
    for path in paths:
        spec = validate(path)
        assert spec.metadata.executable is True
        assert spec.rubric.safety == 2


@pytest.mark.parametrize(
    "name, message",
    [
        ("missing_required_trace_event.json", "missing required trace events"),
        ("rejected_rubric_or_unsafe_flag.json", "rubric.safety == 2"),
        ("composite_without_primitive.json", "composite label"),
    ],
)
def test_invalid_examples_fail(name: str, message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        validate(FACTORY / "examples" / "invalid" / name)


def test_unknown_label_fails() -> None:
    spec = load_spec(FACTORY / "examples" / "valid" / "uncertainty_escalation.json")
    spec["failure_labels"][0]["label"] = "unknown_label"
    with pytest.raises(ValidationError, match="failure_labels"):
        TaskSpec.model_validate(spec)


def test_composite_label_without_primitive_cause_fails() -> None:
    spec = load_spec(FACTORY / "examples" / "valid" / "provenance_trace_mismatch.json")
    spec["failure_labels"] = [
        {
            "label": "trace_final_answer_mismatch",
            "role": "secondary",
            "primary_failure_label": None,
            "rationale": "Composite label with no primitive cause should be rejected.",
        }
    ]
    with pytest.raises(ValidationError, match="composite label"):
        TaskSpec.model_validate(spec)


def test_final_answer_only_agentic_task_fails() -> None:
    spec = load_spec(FACTORY / "examples" / "valid" / "uncertainty_escalation.json")
    spec["expected_trace"] = [
        {
            "event_type": "final_answer",
            "required_fields": ["uncertainty_status", "conflict_ids", "escalation_action"],
            "min_count": 1,
            "description": "Only final answer evidence should be rejected.",
        }
    ]
    with pytest.raises(ValidationError, match="missing required trace events|final-answer-only"):
        TaskSpec.model_validate(spec)


def test_provider_specific_core_field_fails_but_adapter_metadata_passes() -> None:
    spec = load_spec(FACTORY / "examples" / "valid" / "uncertainty_escalation.json")
    spec["metadata"]["adapter_metadata"]["model"] = "mockllm/model"
    TaskSpec.model_validate(spec)
    spec["structured_final_answer"]["claim_schema"]["model"] = "mockllm/model"
    with pytest.raises(ValidationError, match="provider-specific core fields"):
        TaskSpec.model_validate(spec)


def test_json_schema_export_exists_and_contains_core_definition() -> None:
    schema_path = FACTORY / "schemas" / "task_spec.schema.json"
    assert schema_path.exists()
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["title"] == "TaskSpec"
    assert "metadata" in schema["properties"]
    assert "failure_labels" in schema["properties"]
