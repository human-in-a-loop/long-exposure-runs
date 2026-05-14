# created: 2026-05-13T22:20:00Z
# cycle: 4
# run_id: run-2026-05-13T204826Z
# agent: worker
# milestone: M-4
"""Trace event models and validators for the deterministic toy runtime."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .schemas import TaskSpec, TraceEventType


VALID_EVENT_TYPES = {event.value for event in TraceEventType}


class TraceEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(min_length=1)
    event_type: Literal[
        "observation",
        "tool_call",
        "state_update",
        "permission_decision",
        "delegation_message",
        "final_answer",
        "scorer_event",
    ]
    sequence: int = Field(ge=1)
    payload: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_payload_object(self) -> "TraceEvent":
        if not isinstance(self.payload, dict):
            raise ValueError("trace event payload must be an object")
        return self


class TraceValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    missing_event_types: list[str] = Field(default_factory=list)
    missing_required_fields: list[dict[str, Any]] = Field(default_factory=list)


class TraceIntegrityResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    errors: list[dict[str, Any]] = Field(default_factory=list)


def make_event(event_id: str, event_type: str, sequence: int, payload: dict[str, Any]) -> dict[str, Any]:
    """Create a JSON-serializable trace event after validating the event shape."""
    event = TraceEvent(event_id=event_id, event_type=event_type, sequence=sequence, payload=payload)
    return event.model_dump()


def validate_trace_integrity(trace: list[dict[str, Any]]) -> TraceIntegrityResult:
    """Check global trace integrity separately from task-specific requirements."""
    errors: list[dict[str, Any]] = []
    events: list[TraceEvent] = []

    for index, raw_event in enumerate(trace):
        try:
            events.append(TraceEvent.model_validate(raw_event))
        except Exception as exc:
            errors.append({"kind": "malformed_event", "index": index, "detail": str(exc)})

    event_ids = [
        raw_event.get("event_id")
        for raw_event in trace
        if isinstance(raw_event, dict) and isinstance(raw_event.get("event_id"), str)
    ]
    duplicate_event_ids = sorted({event_id for event_id in event_ids if event_ids.count(event_id) > 1})
    if duplicate_event_ids:
        errors.append({"kind": "duplicate_event_id", "event_ids": duplicate_event_ids})

    sequences = [
        raw_event.get("sequence")
        for raw_event in trace
        if isinstance(raw_event, dict) and isinstance(raw_event.get("sequence"), int)
    ]
    duplicate_sequences = sorted({sequence for sequence in sequences if sequences.count(sequence) > 1})
    if duplicate_sequences:
        errors.append({"kind": "duplicate_sequence", "sequences": duplicate_sequences})
    if sequences != sorted(sequences):
        errors.append({"kind": "non_monotonic_sequence", "sequences": sequences})

    non_scorer_ids = {event.event_id for event in events if event.event_type != "scorer_event"}
    for event in events:
        if event.event_type != "scorer_event":
            continue
        evidence_ids = event.payload.get("evidence_event_ids", [])
        if not isinstance(evidence_ids, list):
            errors.append({"kind": "malformed_evidence_ids", "event_id": event.event_id})
            continue
        missing = [event_id for event_id in evidence_ids if event_id not in non_scorer_ids]
        if missing:
            errors.append(
                {
                    "kind": "missing_evidence_link",
                    "event_id": event.event_id,
                    "missing_event_ids": missing,
                }
            )

    return TraceIntegrityResult(ok=not errors, errors=errors)


def validate_trace_requirements(task_spec: TaskSpec, trace: list[dict[str, Any]]) -> TraceValidationResult:
    """Check expected event counts and required payload fields from a TaskSpec."""
    events = [TraceEvent.model_validate(event) for event in trace]
    missing_event_types: list[str] = []
    missing_required_fields: list[dict[str, Any]] = []

    for requirement in task_spec.expected_trace:
        event_type = str(requirement.event_type)
        matching = [event for event in events if event.event_type == event_type]
        if len(matching) < requirement.min_count:
            missing_event_types.append(event_type)
            continue

        for field in requirement.required_fields:
            if not any(_payload_has_field_path(event.payload, field) for event in matching):
                missing_required_fields.append(
                    {
                        "event_type": event_type,
                        "field": field,
                        "matching_event_ids": [event.event_id for event in matching],
                    }
                )

    return TraceValidationResult(
        ok=not missing_event_types and not missing_required_fields,
        missing_event_types=missing_event_types,
        missing_required_fields=missing_required_fields,
    )


def _payload_has_field_path(payload: Any, field_path: str) -> bool:
    parts = field_path.split(".")
    current_values = [payload]
    for part in parts:
        next_values: list[Any] = []
        for value in current_values:
            if isinstance(value, dict) and part in value:
                next_values.append(value[part])
            elif isinstance(value, list):
                next_values.extend(item[part] for item in value if isinstance(item, dict) and part in item)
        if not next_values:
            return False
        current_values = next_values
    return True
