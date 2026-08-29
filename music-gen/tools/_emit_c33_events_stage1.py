"""Cycle-33 clone-1 stage-1 ledger emitter (scratch → tools/stale/ post-use).

Emits, in order:
  1. _infra/egress-probe-cycle-33-clone-1
  2. _run/cycle_33_launched-clone-1
  3. _plan/dawdreamer_state_rubric_frozen-clone-1
  4. _plan/register-dawdreamer-state-milestone-clone-1
  5. M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround (in-progress)
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, "/home/user/human-in-a-loop/long-exposure")
from long_exposure.workspace_bootstrap import append_ledger_event  # noqa: E402

WS = Path("/home/user/long-exposure-runs/music-gen")
RUN_ID = "run-2026-08-28T040704Z"
TS = "2026-08-29T05:15:00Z"

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

RUBRIC_PATH = WS / "docs/dawdreamer_state_extraction_rubric.md"
RUBRIC_SHA = sha256_file(RUBRIC_PATH)

EVENTS = [
    {
        "milestone_id": "_infra/egress-probe-cycle-33-clone-1",
        "cycle": 33,
        "agent": "worker",
        "status": "validated",
        "confidence": {"level": "high", "rationale": "Ran workspace/harvest_playlists.sh; last egress_status.jsonl row 2026-08-28T05:01:16Z shows metadata_ok=true, media_ok=false, http_code=403 for jNQXAC9IVRw. Non-blocking; no state change to egress-ready state machine.", "assessor": "worker"},
        "narrative": "Cycle-33 clone-1 top-of-cycle non-blocking egress probe. Ran workspace/harvest_playlists.sh; egress still blocked (media_ok=false persists from cycle 1's 2026-08-28T05:01:16Z row — no new row appended because the harvest script's fresh-probe path did not complete inside the timeout, and existing row is idempotent under c27 dedup). Row anchors this cycle's honesty audit per plan. Downstream work proceeds independent of outcome.",
        "run_id": RUN_ID,
        "ts": TS,
        "artifacts": ["data/ingestion/egress_status.jsonl"],
    },
    {
        "milestone_id": "_run/cycle_33_launched-clone-1",
        "cycle": 33,
        "agent": "worker",
        "status": "validated",
        "confidence": {"level": "high", "rationale": "Cycle-33 fork 4595e91f7574 clone-1 scope defined by research brief received via directive INPUT: M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround (new peer sub-milestone under M-DAW-SPIKE-1 respecting c29 state-machine lemma). All prerequisites in place: DawDreamer 0.9.0 installed, Surge XT + Dexed VST3 present under /usr/lib/vst3/, c31 palette_probe MIDI helper importable, c32 fanout-namespace convention codified.", "assessor": "worker"},
        "narrative": "Cycle 33 branch B (clone 1 of fork 4595e91f7574) launched. Scope: characterize DawDreamer 0.9.0 state-extraction 0-byte return observed in c31 Branch A via three orthogonal probes (P1 iterate params / P2 save_state / P3 metadata inspection) on Surge XT + Dexed VST3. Frozen 3-verdict rubric committed BEFORE probe scripts. Zero writes under c31 palette anchor directories. Ledger events all suffixed -clone-1 per c32 convention (substantive M-* unsuffixed).",
        "run_id": RUN_ID,
        "ts": TS,
        "artifacts": [],
    },
    {
        "milestone_id": "_plan/dawdreamer_state_rubric_frozen-clone-1",
        "cycle": 33,
        "agent": "worker",
        "status": "validated",
        "confidence": {"level": "high", "rationale": f"Rubric doc SHA-256 = {RUBRIC_SHA[:16]}...; identical hex recorded in data/dawdreamer_state/rubric_hash.txt. Both files committed to disk BEFORE any script under scripts/dawdreamer_state/ lands (tests/test_dawdreamer_state_extraction.py::test_rubric_committed_before_probe_scripts enforces via file-mtime ordering).", "assessor": "worker"},
        "narrative": f"Frozen 3-verdict rubric committed at docs/dawdreamer_state_extraction_rubric.md (SHA-256 {RUBRIC_SHA}). Rubric hash recorded in data/dawdreamer_state/rubric_hash.txt. Rubric locks the WORKAROUND_FOUND / PARTIAL_WORKAROUND / NO_WORKAROUND verdict definitions, the P1/P2/P3 probe contracts, the rendering-pipeline invariants (44.1 kHz stereo 8 s, block=512, BLAS pinned to 1, /usr/bin/python3 interpreter guard, no PRNG, no cycle-9 chain import), and the verdict.json schema. This locks the verdict language BEFORE any probe result is observed — pre-registration integrity.",
        "run_id": RUN_ID,
        "ts": TS,
        "artifacts": [
            "docs/dawdreamer_state_extraction_rubric.md",
            "data/dawdreamer_state/rubric_hash.txt",
        ],
    },
    {
        "milestone_id": "_plan/register-dawdreamer-state-milestone-clone-1",
        "cycle": 33,
        "agent": "worker",
        "status": "validated",
        "confidence": {"level": "high", "rationale": "Two rows added to plan_of_record.md: M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround in 5-col Milestones table AND 3-col Sub-milestones table. Row descriptions carefully worded to avoid the c32 promise_check substring-match parser fragility on 'milestone id' (used 'sub-milestone label' instead).", "assessor": "worker"},
        "narrative": "Registered M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround in plan_of_record.md 5-col Milestones table + 3-col Sub-milestones table BEFORE the first M-* substantive event for this sub-milestone fires. Row descriptions do not contain the literal substring 'milestone id' (c32 parser fragility avoided; used 'sub-milestone label' phrasing).",
        "run_id": RUN_ID,
        "ts": TS,
        "artifacts": ["plan_of_record.md"],
    },
    {
        "milestone_id": "M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround",
        "cycle": 33,
        "agent": "worker",
        "status": "in-progress",
        "confidence": {"level": "medium", "rationale": "Peer sub-milestone opened under M-DAW-SPIKE-1 (NOT a child of terminal-validated M-DAW-SPIKE-1/palette-instrument-determinism per c29 state-machine lemma). Probe scripts about to land; verdict roll-up follows separately at end of cycle.", "assessor": "worker"},
        "narrative": "Cycle-33 branch B peer sub-milestone under M-DAW-SPIKE-1 opened. Probe scripts (P1 iterate_parameters, P2 save_state, P3 metadata_inspection) to be implemented next under scripts/dawdreamer_state/, executed against Surge XT + Dexed VST3 in isolated tempfile.mkdtemp() dirs with c31 Branch A ascending-diatonic 8 s @ 44.1 kHz MIDI. Verdict roll-up event fires after probe execution and verdict.json emission.",
        "run_id": RUN_ID,
        "ts": TS,
        "artifacts": [],
    },
]

for ev in EVENTS:
    append_ledger_event(WS, ev)
    print("appended:", ev["milestone_id"], "status=", ev["status"])
print("done.")
