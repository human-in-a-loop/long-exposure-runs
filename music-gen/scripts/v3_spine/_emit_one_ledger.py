"""Quick emitter for the namespace-registration ledger event (pre-Track-B)."""
import sys
from pathlib import Path
from long_exposure import workspace_bootstrap

event = {
    "ts": "2026-09-02T10:45:00Z",
    "run_id": "run-2026-09-02T104500Z",
    "cycle": 5,
    "agent": "worker",
    "milestone_id": "_plan/register-c5-operator-section-namespace",
    "status": "validated",
    "confidence": {
        "level": "high",
        "rationale": "namespace pre-declared before Track B execution",
        "assessor": "worker",
    },
    "narrative": (
        "c5 declares operator-section artifact naming convention: sibling "
        "operator_section/ subdirs under data/v3/deliveries/<sha16>/ and "
        "data/v3_spine/<sha16>/. c4 delivery artifacts READ-ONLY anchors."
    ),
    "artifacts": [
        "data/v3/deliveries/31a164f845f8e27e/operator_section/",
        "data/v3_spine/31a164f845f8e27e/operator_section/",
    ],
}
workspace_bootstrap.append_ledger_event(Path("."), event)
print("OK")
