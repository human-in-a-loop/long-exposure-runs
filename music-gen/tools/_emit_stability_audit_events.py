"""One-shot emitter for M-EAR-1/synthetic-label-stability-audit ledger events.

Archive to tools/stale/ after use.
"""
# created: 2026-08-28T17:30:00Z  cycle: 22  run_id: run-2026-08-28T040704Z
# agent: worker (clone-2, fork cc548ca0c2e5)  milestone: _archive/stability-audit-scratch
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"
if _LE_PARENT not in sys.path:
    sys.path.insert(0, _LE_PARENT)

from long_exposure.workspace_bootstrap import append_ledger_event  # noqa: E402


def emit(kind: str, extra: str = "") -> None:
    workspace = "."

    if kind == "plan-register":
        ev = {
            "milestone_id": "_plan/register-stability-audit-milestone",
            "ts": "2026-08-28T17:30:00Z",
            "run_id": "run-2026-08-28T040704Z",
            "cycle": 22,
            "agent": "worker",
            "status": "validated",
            "confidence": {
                "level": "high",
                "rationale": "Plan-file edit is mechanical: added 1 row to 5-col Milestones and 1 row to 3-col Sub-milestones tables under parent M-EAR-1.",
                "assessor": "worker",
            },
            "narrative": (
                "Added M-EAR-1/synthetic-label-stability-audit rows to the 5-col Milestones "
                "table (parent M-EAR-1, deps M-EAR-1/preparation + M-EAR-1/training-loop) and "
                "the 3-col Sub-milestones table (parent M-EAR-1). Enables cycle-22 stability-"
                "audit ledger events under this ID to resolve cleanly at promise_check time."
            ),
            "artifacts": ["plan_of_record.md"],
        }
    elif kind == "start":
        ev = {
            "milestone_id": "M-EAR-1/synthetic-label-stability-audit",
            "ts": "2026-08-28T17:31:00Z",
            "run_id": "run-2026-08-28T040704Z",
            "cycle": 22,
            "agent": "worker",
            "status": "in-progress",
            "confidence": {
                "level": "medium",
                "rationale": "Design finalized: 10 SHA-256-salted recipes across 4 families "
                "(hash-noise / linear-projection / nonlinear / cluster-anchor). Chassis "
                "(scripts/ear/model.py train_and_eval) reused verbatim. Three frozen criteria "
                "locked before run.",
                "assessor": "worker",
            },
            "narrative": (
                "10-recipe design frozen: family A hash-noise (salts stab-audit-0,1), family B "
                "linear-projection (2,3), family C nonlinear sigmoid+axis-pick (4,5), family D "
                "cluster-anchor (6,7,8,9). Per recipe: 5-fold stratified CV via existing "
                "train_and_eval; record per-fold MAE + per-clip predicted rank. Cross-recipe: "
                "MAE envelope percentiles, 45 pairwise Kendall τ, per-clip band variance. "
                "Frozen criteria: C1 cycle-6 MAE (0.891) inside [5th,95th] envelope; C2 mean "
                "pairwise τ ≥ 0.7; C3 stability_report.json byte-identical × 2. Frozen invariants: "
                "feature cache untouched; scripts/ear/{features,model,corn,train}.py unchanged; "
                "leak-test artifacts untouched; cycle-6 salt out of stab-audit-* namespace."
            ),
            "artifacts": [],
        }
    elif kind == "mid":
        # extra = json string with observed numbers
        obs = json.loads(extra) if extra else {}
        ev = {
            "milestone_id": "M-EAR-1/synthetic-label-stability-audit",
            "ts": obs.get("ts", "2026-08-28T18:00:00Z"),
            "run_id": "run-2026-08-28T040704Z",
            "cycle": 22,
            "agent": "worker",
            "status": "in-progress",
            "confidence": {
                "level": "medium",
                "rationale": "Run-1 complete; run-2 in progress for C3 byte-determinism check.",
                "assessor": "worker",
            },
            "narrative": obs.get("narrative", "mid checkpoint"),
            "artifacts": obs.get("artifacts", []),
        }
    else:
        raise SystemExit(f"unknown kind: {kind}")

    append_ledger_event(workspace, ev)
    print(f"emitted: {ev['milestone_id']} status={ev['status']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["plan-register", "start", "mid"])
    ap.add_argument("--extra", default="")
    args = ap.parse_args()
    emit(args.kind, args.extra)
