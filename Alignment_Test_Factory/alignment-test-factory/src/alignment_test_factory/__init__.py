# created: 2026-05-13T21:45:00Z
# cycle: 2
# run_id: run-2026-05-13T204826Z
# agent: worker
# milestone: M-3
"""Core package for the open alignment test factory prototype."""

from .schemas import TaskSpec
from .runtime import ToyEnvironment
from .scorers import (
    score_delegation_drift,
    score_permission_tool_overreach,
    score_provenance_trace_mismatch,
    score_task_family,
    score_uncertainty_escalation,
)
from .trace import TraceEvent, validate_trace_integrity, validate_trace_requirements

__all__ = [
    "TaskSpec",
    "ToyEnvironment",
    "TraceEvent",
    "score_delegation_drift",
    "score_permission_tool_overreach",
    "score_provenance_trace_mismatch",
    "score_task_family",
    "score_uncertainty_escalation",
    "validate_trace_integrity",
    "validate_trace_requirements",
]
