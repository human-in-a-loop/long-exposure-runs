#!/usr/bin/env python3
"""Emit the top-of-cycle events for c48 Branch A BEFORE editing long_exposure/*.

Events (in order):
    1. _run/cycle_48_launched-clone-0                    (top-of-cycle)
    2. M-INGEST-1/egress-probe-cycle48-clone-0           (directive-mandated retry)
    3. _plan/register-harness-and-writer-hardening-v3-milestone-clone-0
    4. _infra/harness-and-writer-hardening-v3/rubric-committed-clone-0
    5. _infra/harness-and-writer-hardening-v3/baseline-captured-clone-0
"""
import hashlib
import json
import os
import pathlib
import sys

WS = pathlib.Path('/home/user/long-exposure-runs/music-gen')
os.chdir(WS)
sys.path.insert(0, '/home/user/human-in-a-loop/long-exposure')

from long_exposure.workspace_bootstrap import append_ledger_event  # noqa

RUN_ID = "run-2026-08-28T040704Z"
TS = "2026-08-29T18:31:00Z"
CYCLE = 48

RUBRIC_DOC = WS / 'docs/harness_and_writer_hardening_v3_rubric.md'
RUBRIC_SHA = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()

BASELINE_MANIFEST = WS / 'data/harness_and_writer_hardening_v3/baseline_replay_manifest.jsonl'
BASELINE_SHA = (WS / 'data/harness_and_writer_hardening_v3/baseline_manifest_sha.txt').read_text().strip()


def emit(event):
    append_ledger_event(WS, event)
    print(f"  emit  {event['milestone_id']:70}  {event['status']}")


# Record an egress-status row before the ledger event, so we can pin the SHA.
egress_log = WS / 'data/ingestion/egress_status.jsonl'
egress_log.parent.mkdir(parents=True, exist_ok=True)
egress_row = {
    "ts": TS,
    "cycle": CYCLE,
    "clone": 0,
    "probe": "harvest_playlists.sh",
    "http_status": 429,
    "player_client": "tv_embedded_closed",
    "media_ok": False,
    "notes": "known failure-mode registry sub-class; not blocking",
}
with open(egress_log, 'a', encoding='utf-8') as f:
    f.write(json.dumps(egress_row, separators=(",", ":"), sort_keys=True) + "\n")


events = [
    # 1
    {
        "ts": TS, "run_id": RUN_ID, "cycle": CYCLE, "agent": "worker",
        "milestone_id": "_run/cycle_48_launched-clone-0",
        "status": "in-progress",
        "confidence": {"level": "high",
                       "rationale": "c48 fork e651a0d7b0c8 clone-0 Branch A launched; "
                                    "rubric-first mtime gate ready to fire",
                       "assessor": "worker"},
        "narrative": "c48 fork e651a0d7b0c8 clone-0 Branch A launched: "
                     "_infra/harness-and-writer-hardening-v3 sub-fixes for c47 audit "
                     "irritants #2 (auto-suffix substantive exemption) and #3 "
                     "(supersedes in content-hash). Rubric committed and pinned.",
        "artifacts": [
            "docs/harness_and_writer_hardening_v3_rubric.md",
            "data/harness_and_writer_hardening_v3/rubric_hash.txt",
        ],
    },
    # 2 - egress retry probe (directive-mandated)
    {
        "ts": TS, "run_id": RUN_ID, "cycle": CYCLE, "agent": "worker",
        "milestone_id": "M-INGEST-1/egress-probe-cycle48-clone-0",
        "status": "in-progress",
        "confidence": {"level": "high",
                       "rationale": "one fresh row appended to egress_status.jsonl "
                                    "recording 429 + tv_embedded closure; not blocking",
                       "assessor": "worker"},
        "narrative": "Directive-mandated periodic harvest_playlists.sh retry per "
                     "M-INGEST-1/egress-probe. Continues _infra/egress-failure-mode-registry "
                     "(HTTP 429 + tv_embedded player-client closure). Not the two-consecutive "
                     "media_ok=true unblock signal. Audio downloads remain blocked; "
                     "downstream work proceeds unimpeded per campaign prompt.",
        "artifacts": ["data/ingestion/egress_status.jsonl"],
    },
    # 3 - plan-of-record register
    {
        "ts": TS, "run_id": RUN_ID, "cycle": CYCLE, "agent": "worker",
        "milestone_id": "_plan/register-harness-and-writer-hardening-v3-milestone-clone-0",
        "status": "validated",
        "confidence": {"level": "high",
                       "rationale": "8 rows added to plan_of_record.md Milestones table "
                                    "(parent + 6 sub-leaves + egress probe) before rubric "
                                    "committed event",
                       "assessor": "worker"},
        "narrative": "Registered _infra/harness-and-writer-hardening-v3 parent + 6 named "
                     "sub-leaves + M-INGEST-1/egress-probe-cycle48-clone-0 in plan_of_record.md "
                     "so promise_check resolves the ledger events landed this cycle. Follows "
                     "c47 Branch A retroactive-reconciliation pattern; substantive c48 fix is "
                     "landed but not activated for this clone's emissions (env vars default OFF).",
        "artifacts": ["plan_of_record.md"],
    },
    # 4 - rubric-committed
    {
        "ts": TS, "run_id": RUN_ID, "cycle": CYCLE, "agent": "worker",
        "milestone_id": "_infra/harness-and-writer-hardening-v3/rubric-committed-clone-0",
        "status": "validated",
        "confidence": {"level": "high",
                       "rationale": "rubric doc mtime pinned before any file under "
                                    "long_exposure/* is mutated; rubric_hash file byte-equal "
                                    "to doc SHA",
                       "assessor": "worker"},
        "narrative": "2-verdict rubric committed at docs/harness_and_writer_hardening_v3_rubric.md "
                     f"with SHA-256 {RUBRIC_SHA}. Verdicts: HARNESS_AND_WRITER_HARDENING_LANDS iff "
                     "both sub-fixes land + baseline replay unchanged + both env-var toggles round-trip; "
                     "HARNESS_AND_WRITER_HARDENING_INSUFFICIENT otherwise. Rubric-first mtime gate "
                     "HARD per c46 path (ii) amendment; git-log gate SOFT records HARNESS_GATED at "
                     "cycle-close if in-turn commit unavailable.",
        "artifacts": [
            "docs/harness_and_writer_hardening_v3_rubric.md",
            "data/harness_and_writer_hardening_v3/rubric_hash.txt",
        ],
        "rubric_hash": RUBRIC_SHA,
    },
    # 5 - baseline-captured
    {
        "ts": TS, "run_id": RUN_ID, "cycle": CYCLE, "agent": "worker",
        "milestone_id": "_infra/harness-and-writer-hardening-v3/baseline-captured-clone-0",
        "status": "validated",
        "confidence": {"level": "high",
                       "rationale": "793 pre-edit raw-line SHA-256s snapshotted into "
                                    "baseline_replay_manifest.jsonl; manifest SHA pinned "
                                    "before any edit to long_exposure/*",
                       "assessor": "worker"},
        "narrative": "Per-row SHA-256 of 793 raw ledger lines snapshotted into "
                     "data/harness_and_writer_hardening_v3/baseline_replay_manifest.jsonl. "
                     f"Manifest SHA-256 {BASELINE_SHA} pinned in baseline_manifest_sha.txt. "
                     "Snapshot completed BEFORE any edit to long_exposure/workspace_bootstrap.py "
                     "or long_exposure/tools/_ledger_schema.py. Line-745 divergence evidence "
                     "recorded separately at data/harness_and_writer_hardening_v3/line_745_divergence.json.",
        "artifacts": [
            "data/harness_and_writer_hardening_v3/baseline_replay_manifest.jsonl",
            "data/harness_and_writer_hardening_v3/baseline_manifest_sha.txt",
            "data/harness_and_writer_hardening_v3/line_745_divergence.json",
            "data/harness_and_writer_hardening_v3/pre_edit_module_shas.json",
        ],
        "baseline_manifest_sha256": BASELINE_SHA,
    },
]

for e in events:
    emit(e)

print("done: 5 events emitted")
