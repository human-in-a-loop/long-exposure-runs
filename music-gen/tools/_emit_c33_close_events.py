"""Cycle-33 clone-1 close + housekeeping ledger emitter (scratch → stale/)."""
from __future__ import annotations
from pathlib import Path
import sys

sys.path.insert(0, "/home/user/human-in-a-loop/long-exposure")
from long_exposure.workspace_bootstrap import append_ledger_event  # noqa: E402

WS = Path("/home/user/long-exposure-runs/music-gen")
RUN_ID = "run-2026-08-28T040704Z"
TS = "2026-08-29T05:50:00Z"

EVENTS = [
    {
        "milestone_id": "_run/cycle_33_closed-clone-1",
        "cycle": 33,
        "agent": "worker",
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": (
                "All named milestone events for cycle-33 clone-1 landed: "
                "M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround "
                "verdict=WORKAROUND_FOUND (winning_path=P1). Rubric SHA "
                "chain intact. Tests green (12/12 dawdreamer_state + 8/8 "
                "cross-branch §49). Zero writes under c31 palette anchor "
                "directories. Housekeeping events queued next per c29 "
                "pattern (after this _closed event)."
            ),
            "assessor": "worker",
        },
        "narrative": (
            "Cycle 33 clone-1 branch B closed. Deliverables: rubric doc + "
            "report + 6 probe scripts + verdict.json + 12 per-plugin data "
            "files + fetchability_ladder + 12-case dedicated test suite + "
            "8 §49 cross-branch checks. Verdict WORKAROUND_FOUND with "
            "winning P1 (canonical-JSON iterate-params dict) validated "
            "byte-deterministic × 2 on BOTH Surge XT (2855 params) and "
            "Dexed (2238 params). Report documents c31 STILL_GAP root "
            "cause: probe code called nonexistent get_state() and "
            "swallowed the AttributeError. `pinned_state_v2` proposed as "
            "schema-v2 CANDIDATE for cycle 34; frozen c31 palette_v1.json "
            "NOT edited this cycle."
        ),
        "run_id": RUN_ID,
        "ts": TS,
        "artifacts": [
            "docs/dawdreamer_state_extraction_rubric.md",
            "docs/dawdreamer_state_extraction_workaround_report.md",
            "data/dawdreamer_state/verdict.json",
            "tests/test_dawdreamer_state_extraction.py",
            "tests/test_integration_cross_branch.py",
        ],
    },
    {
        "milestone_id": "_archive/cycle-33-scratch-clone-1",
        "cycle": 33,
        "agent": "worker",
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": (
                "Per c29 housekeeping pattern: one-shot emitters and "
                "exploration probes archived to tools/stale/ after use. "
                "Prevents scratch-file drift; preserves ledger audit "
                "trail of what was written."
            ),
            "assessor": "worker",
        },
        "narrative": (
            "Archived cycle-33 clone-1 scratch to tools/stale/: "
            "_probe_api_c33.py, _probe_api_c33_p1.py, "
            "_emit_c33_events_stage1.py, _emit_c33_verdict_rollup.py, "
            "_emit_c33_close_events.py (this emitter itself). Content "
            "preserved by move (no file deletion)."
        ),
        "run_id": RUN_ID,
        "ts": TS,
        "artifacts": [
            "tools/stale/_probe_api_c33.py",
            "tools/stale/_probe_api_c33_p1.py",
            "tools/stale/_emit_c33_events_stage1.py",
            "tools/stale/_emit_c33_verdict_rollup.py",
            "tools/stale/_emit_c33_close_events.py",
        ],
    },
    {
        "milestone_id": "_infra/adopt-cycle33-tests-clone-1",
        "cycle": 33,
        "agent": "worker",
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": (
                "Per c29 housekeeping pattern: adoption of cycle-33 "
                "test files under the ledger; clears promise_check WARNs "
                "surfaced when tests land outside a milestone-adopted "
                "directory."
            ),
            "assessor": "worker",
        },
        "narrative": (
            "Adopted cycle-33 clone-1 tests: "
            "tests/test_dawdreamer_state_extraction.py (≥12 cases, all "
            "green) and the extension of "
            "tests/test_integration_cross_branch.py §49 (8 additional "
            "state-extraction invariant checks, all green). No content "
            "change; ledger-tracking only."
        ),
        "run_id": RUN_ID,
        "ts": TS,
        "artifacts": [
            "tests/test_dawdreamer_state_extraction.py",
            "tests/test_integration_cross_branch.py",
        ],
    },
]

for ev in EVENTS:
    append_ledger_event(WS, ev)
    print("appended:", ev["milestone_id"])
print("done.")
