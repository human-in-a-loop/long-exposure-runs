"""One-shot ledger-emit helper for M-EAR-1/head-regularization-audit.

Usage: /usr/bin/python3 tools/_emit_ledger.py <event-key>
Archived to tools/stale/ on cycle completion.
"""
# created: 2026-08-28T20:00:00Z  cycle: 23  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 3fbd8c1ab57c)  milestone: M-EAR-1/head-regularization-audit
from __future__ import annotations
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "/home/user/human-in-a-loop/long-exposure")
from long_exposure.workspace_bootstrap import append_ledger_event  # noqa: E402

WS = Path("/home/user/long-exposure-runs/music-gen")

EVENTS = {
    "plan-register": {
        "milestone_id": "_plan/register-head-regularization-audit-milestone",
        "status": "validated",
        "confidence": {"level": "high",
                       "rationale": "Added Milestones + Sub-milestones rows for M-EAR-1/head-regularization-audit before any in-progress event under this ID.",
                       "assessor": "worker"},
        "narrative": ("Registered new milestone M-EAR-1/head-regularization-audit in plan_of_record.md "
                      "(5-col Milestones table row + 3-col Sub-milestones table row with parent M-EAR-1). "
                      "Chassis-redesign response to cycle-22 clone-2 invalidation. Three regularized head variants "
                      "(CORN-ridge, CORN-bottleneck, CORN-frozen-projector) audited under UNCHANGED cycle-22 harness "
                      "with relaxed rubric (C1' MAE-in-envelope, C2' mean tau >= 0.4, C3' byte-determinism x 2)."),
        "assessment": "plan-of-record updated; ledger events under M-EAR-1/head-regularization-audit can now resolve.",
        "run_id": "run-2026-08-28T040704Z",
        "cycle": 23,
        "agent": "worker",
        "artifacts": ["plan_of_record.md"],
    },
    "start": {
        "milestone_id": "M-EAR-1/head-regularization-audit",
        "status": "in-progress",
        "confidence": {"level": "medium",
                       "rationale": "Frozen rubric + variant list + harness anchors captured before any training run.",
                       "assessor": "worker"},
        "narrative": ("Starting the chassis-redesign audit. Variant list frozen (CORN-ridge, CORN-bottleneck, "
                      "CORN-frozen-projector). Rubric frozen: C1' cycle-6-recipe MAE inside variant's own 10-recipe "
                      "[5th,95th] envelope; C2' mean pairwise Kendall tau across 45 recipe pairs >= 0.4; "
                      "C3' SHA-256(stability_report_v2_<variant>.json) equal across two independent runs. "
                      "Harness anchor SHAs captured: stability_audit.py=b1ce5137..., synthetic_labels.py=b71f194e..., "
                      "stability_metrics.py=6a5cb518..., model.py=d4322a95..., corn.py=5028c58c..., "
                      "features.py=5e7cbf33... Feature cache (data/ear/features/, 55 clips) is read-only anchor."),
        "assessment": "audit setup locked; ready to build variant heads.",
        "run_id": "run-2026-08-28T040704Z",
        "cycle": 23,
        "agent": "worker",
        "artifacts": ["plan_of_record.md"],
    },
}


def main(key: str) -> int:
    event = dict(EVENTS[key])
    event.setdefault("ts", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z")
    append_ledger_event(WS, event)
    print(f"appended {key}: {event['milestone_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "plan-register"))
