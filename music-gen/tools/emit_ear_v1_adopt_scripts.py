#!/usr/bin/python3
"""One-shot auditor emitter: adopt scripts/ear_v1/*.py so orphan WARNs clear post-merge."""
import sys
assert sys.executable == '/usr/bin/python3'
from pathlib import Path
from datetime import datetime, timezone
from long_exposure.workspace_bootstrap import append_ledger_event

WS = Path("/home/user/long-exposure-runs/music-gen")
TS = datetime.now(tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

event = {
    "milestone_id": "_infra/adopt-scripts-ear-v1",
    "cycle": 38,
    "agent": "auditor",
    "run_id": "run-2026-08-28T040704Z",
    "ts": TS,
    "status": "validated",
    "confidence": {
        "level": "high",
        "rationale": (
            "adoption of the c38 clone-0 subagent's scripts/ear_v1/*.py "
            "substantive files under a bookkeeping milestone so promise_check "
            "orphan WARNs clear post-merge concat. Files were written by the "
            "subagent as part of the M-EAR-1/real-label-training-v1 delivery "
            "but not attached to any prior emitted ledger event."
        ),
        "assessor": "auditor",
    },
    "narrative": (
        "Adopting 5 substantive scripts under scripts/ear_v1/: features_v1.py, "
        "ingest_ratings.py, leak_ablation_v1.py, run_all.py, evaluate_v1.py "
        "(note: train_v1.py is not on disk — the subagent placed training in "
        "run_all.py + evaluate_v1.py). Also adopts tests/test_ear_real_label_"
        "training_v1.py under this milestone (in addition to _infra/adopt-"
        "cycle38-tests which already references it). Clears promise_check "
        "orphan WARNs post-merge."
    ),
    "artifacts": [
        "scripts/ear_v1/__init__.py",
        "scripts/ear_v1/features_v1.py",
        "scripts/ear_v1/ingest_ratings.py",
        "scripts/ear_v1/leak_ablation_v1.py",
        "scripts/ear_v1/evaluate_v1.py",
        "scripts/ear_v1/run_all.py",
        "tests/test_ear_real_label_training_v1.py",
    ],
}

if __name__ == "__main__":
    append_ledger_event(WS, event)
    print(f"appended: {event['milestone_id']}")
