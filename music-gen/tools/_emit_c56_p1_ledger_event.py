#!/usr/bin/env /usr/bin/python3
# ---
# created: 2026-09-05T17:00:00Z
# cycle: 56
# run_id: run-2026-09-05T170000Z
# agent: worker
# milestone: _infra/fine-fit-drums-song-sha16-verified-c56
# ---
"""One-shot emitter for c56 P1 gate: --song-sha16 kwarg verify + SHA drift.

Case (a) verified: `--song-sha16` is present as canonical required kwarg at
scripts/sound_match/fine_fit_sf2_drums.py:451 in the argparse block.
`fine_fit_sf2_drums.py --help` renders `--song-sha16 SONG_SHA16` as expected.
No additive edit required. P1 becomes a one-line disclosure event unlocking
P2 (WIG drums stage-2) + P3 (Disco A drums stage-2) fine-fit launches.

Invariant (d) SHA drift disclosures included in narrative.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

event = {
    "milestone_id": "_infra/fine-fit-drums-song-sha16-verified-c56",
    "cycle": 56,
    "status": "validated",
    "confidence": {
        "level": "high",
        "rationale": (
            "P1 mandatory pre-work gate verified via direct source inspection. "
            "scripts/sound_match/fine_fit_sf2_drums.py:451 defines "
            "`ap.add_argument(\"--song-sha16\", required=True)` as canonical "
            "required kwarg (case a per brief P1 gate). `--help` invocation "
            "renders `--song-sha16 SONG_SHA16` in the usage line. No additive "
            "edit required; no test extension required. P2 (WIG drums stage-2) "
            "and P3 (Disco A drums stage-2 queued via OP-1) are unblocked."
        ),
        "assessor": "worker",
    },
    "narrative": (
        "c56 Priority 1 (mandatory pre-work gate) landed as case (a) per brief: "
        "scripts/sound_match/fine_fit_sf2_drums.py argparse block at line 451 "
        "already exposes `--song-sha16` as a canonical required kwarg. Verified "
        "by `/usr/bin/python3 scripts/sound_match/fine_fit_sf2_drums.py --help` "
        "which prints `--song-sha16 SONG_SHA16` in the usage line. No edit was "
        "made to any driver script; P1 is a one-line disclosure event. Both "
        "brief expected on-disk kwarg (either canonical `--song-sha16` or "
        "additive `--song, --song-sha16` alias sharing dest) are satisfied by "
        "the canonical form. Invariant (d) SHA drift disclosures: "
        "fine_fit_sf2_drums.py on-disk sha256="
        "bc06892072ed424435fc51e692cf35914702159a74194e8ea04467865d0ffb84 "
        "differs from brief-pinned anchor "
        "a432e1d1... (brief header cited a432e1d1 short form; on-disk full sha "
        "recorded here). fine_fit_sf2_v2.py on-disk sha256="
        "15cbf8b69c2019f3aecdda54d7019efb0a1deda339890e07a6b0387b5547b43a "
        "differs from brief-pinned anchor 6c80c438... . These drivers are "
        "READ-ONLY this cycle per brief; the drift is disclosed for auditor "
        "cross-check and does not affect P1's gate verdict since the required "
        "argparse contract holds at the on-disk revision. _serial_lock_op1.py "
        "on-disk sha256=b8e1b7dda5d1ed19c7a4516597e6b1b446ce0480ab84bbc0f515d0f78034b814 "
        "matches c55 post-fix (also READ-ONLY per c56 brief). "
        "coarse_sweep_sf2_drums.py on-disk sha256="
        "3466fe2e001ae5f27a00cb08d8edd31f2ee080174c040ff21437cbe00cafab90 "
        "matches brief-pinned anchor (also READ-ONLY per c56 brief). P2 and P3 "
        "unblocked for launch in this same cycle."
    ),
    "artifacts": [
        "scripts/sound_match/fine_fit_sf2_drums.py",
    ],
    "supersedes_path": None,
    "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
    "run_id": "run-2026-09-05T170000Z",
    "agent": "worker",
    "ts": "2026-09-05T17:00:00Z",
    "on_disk_sha": {
        "scripts/sound_match/fine_fit_sf2_drums.py": "bc06892072ed424435fc51e692cf35914702159a74194e8ea04467865d0ffb84",
        "scripts/sound_match/fine_fit_sf2_v2.py": "15cbf8b69c2019f3aecdda54d7019efb0a1deda339890e07a6b0387b5547b43a",
        "scripts/sound_match/_serial_lock_op1.py": "b8e1b7dda5d1ed19c7a4516597e6b1b446ce0480ab84bbc0f515d0f78034b814",
        "scripts/sound_match/coarse_sweep_sf2_drums.py": "3466fe2e001ae5f27a00cb08d8edd31f2ee080174c040ff21437cbe00cafab90",
    },
    "kwarg_verification": {
        "file": "scripts/sound_match/fine_fit_sf2_drums.py",
        "line": 451,
        "argparse_call": "ap.add_argument(\"--song-sha16\", required=True)",
        "help_output_contains": "--song-sha16 SONG_SHA16",
        "case": "a",
        "additive_edit_required": False,
    },
    "invariant_d_disclosures": [
        "fine_fit_sf2_drums.py on-disk sha bc06892072ed424435fc51e692cf35914702159a74194e8ea04467865d0ffb84 differs from brief-pinned short-form a432e1d1... ; driver is READ-ONLY this cycle; P1 kwarg contract verified at the on-disk revision.",
        "fine_fit_sf2_v2.py on-disk sha 15cbf8b69c2019f3aecdda54d7019efb0a1deda339890e07a6b0387b5547b43a differs from brief-pinned short-form 6c80c438... ; driver is READ-ONLY this cycle and not exercised by drums stage-2 (drums stage-2 uses fine_fit_sf2_drums.py, not v2).",
        "long_exposure.tools.ledger_append helper absent in workspace per c34+ chain; direct-append to promise_ledger.jsonl at root scope per artifact-tracking policy.",
    ],
}

# UUID5 content-hash event_id (excludes event_id + ts per convention).
content = {k: v for k, v in event.items() if k not in ("event_id", "ts")}
canon = json.dumps(content, sort_keys=True, separators=(",", ":"))
event["event_id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, canon))

line = json.dumps(event, sort_keys=True, separators=(",", ":"))
with open(ROOT / "promise_ledger.jsonl", "a") as f:
    f.write(line + "\n")

print(f"Appended event_id={event['event_id']}")
print(f"Length: {len(line)} chars")
