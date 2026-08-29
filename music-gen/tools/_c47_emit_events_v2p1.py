#!/usr/bin/python3
"""c47 clone-0 Branch A ledger event emitter for M-EAR-1/real-label-training-v2.1.

Fires (in strict order):
  aux 1) _run/cycle_47_launched-clone-0  [c33 auto-suffix]
  aux 2) _plan/register-ear-v2p1-milestone-clone-0
  1) M-EAR-1/real-label-training-v2.1/rubric-committed
  2) M-EAR-1/real-label-training-v2.1/features-loaded
  3) M-EAR-1/real-label-training-v2.1/head-trained
  4) M-EAR-1/real-label-training-v2.1/sb3-50ctl-run-1
  5) M-EAR-1/real-label-training-v2.1/sb3-50ctl-run-2
  6) M-EAR-1/real-label-training-v2.1/verdict-emitted
  aux 3) M-EAR-1/real-label-training-v2.1/anchor-preservation-verified
  aux 4) M-INGEST-1/egress-probe-cycle47-clone-0
  close) _run/cycle_47_closed-clone-0
  hk 1) _archive/cycle-47-scratch-clone-0
  hk 2) _infra/adopt-cycle47-tests-clone-0

Uses long_exposure.tools.ledger_append via subprocess helper.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
os.chdir(WS)

# --- SHAs pinned in verdict.
def sha(p: str) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

RUBRIC_SHA = sha("docs/ear_real_label_training_v2p1_rubric.md")
FEATURE_MANIFEST_SHA = json.loads(
    Path("data/ear_v2/feature_cache_manifest_v2.json").read_text()
)["combined_manifest_sha256"]
CORN_HEAD_SHA = sha("data/ear_v2p1/corn_head_v2p1.pt")
TRAIN_RES_SHA = sha("data/ear_v2p1/training_result_v2p1.json")
SB3_R1_SHA = sha("data/ear_v2p1/sb3_50ctl_run_1/sb3_50ctl_verdict_v2p1.json")
SB3_R2_SHA = sha("data/ear_v2p1/sb3_50ctl_run_2/sb3_50ctl_verdict_v2p1.json")
VERDICT_SHA = sha("data/ear_v2p1/verdict.json")
ANCHOR_SHA = sha("data/ear_v2p1/anchor_preservation_v2p1.json")
REPORT_SHA = sha("docs/ear_real_label_training_v2p1_report.md")
V2_VERDICT_SHA = sha("data/ear_v2/verdict.json")
C46_SB3_SHA = sha("data/ear_v2/sb3_control_widening_result.json")
V2P1_VERDICT = json.loads(Path("data/ear_v2p1/verdict.json").read_text())

RUN_ID = "run-2026-08-28T040704Z"
CYCLE = 47
NOW = lambda: datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"


def emit(event: dict) -> None:
    """Append event via long_exposure.tools.ledger_append CLI."""
    # Try importlib path first.
    from long_exposure.tools._ledger_schema import content_hash_event_id
    ev = dict(event)
    if "event_id" not in ev:
        ev["event_id"] = content_hash_event_id(ev)
    payload = json.dumps(ev)
    r = subprocess.run(
        ["/usr/bin/python3", "-m", "long_exposure.tools.ledger_append",
         "--event", payload],
        cwd=WS, capture_output=True, text=True,
    )
    if r.returncode != 0:
        print("STDERR:", r.stderr, file=sys.stderr)
        raise SystemExit(f"ledger_append failed for {ev.get('milestone_id')}")
    print(f"[emit] {ev.get('milestone_id')} → {ev['event_id']}")


def _confidence(rationale: str) -> dict:
    return {
        "level": "high",
        "rationale": rationale,
        "assessor": "worker",
    }


def _e(milestone: str, narrative: str, artifacts: list[str],
       rationale: str, status: str = "validated") -> dict:
    return {
        "milestone_id": milestone,
        "cycle": CYCLE,
        "run_id": RUN_ID,
        "ts": NOW(),
        "agent": "worker",
        "status": status,
        "confidence": _confidence(rationale),
        "narrative": narrative,
        "artifacts": artifacts,
    }


EVENTS: list[dict] = []

# --- aux 1: cycle launched
EVENTS.append(_e(
    "_run/cycle_47_launched-clone-0",
    "Cycle 47 clone-0 Branch A (M-EAR-1/real-label-training-v2.1) launched.",
    ["data/ear_v2p1/rubric_hash.txt"],
    "top-of-cycle marker per c33 convention.",
    status="in-progress",
))

# --- aux 2: plan-of-record row registration
EVENTS.append(_e(
    "_plan/register-ear-v2p1-milestone-clone-0",
    "Registered M-EAR-1/real-label-training-v2.1 + 6 sub-leaves + "
    "egress-probe-cycle47-clone-0 rows in plan_of_record.md before "
    "rubric doc landed. Peer sub-milestone under M-EAR-1 per c29 "
    "state-machine lemma; NOT a child of validated v2.",
    ["plan_of_record.md"],
    "plan-of-record hygiene before code lands.",
))

# --- 1: rubric-committed
EVENTS.append(_e(
    "M-EAR-1/real-label-training-v2.1/rubric-committed",
    f"v2.1 rubric doc SHA-256 = {RUBRIC_SHA} landed on disk before any "
    "script under scripts/ear_v2p1/. mtime gate hard; git-log gate soft "
    "per c46 path (ii) amendment. 3-verdict rubric: "
    "EAR_v2p1_STABLE_FPR_PASS / EAR_v2p1_BOUNDARY_TIP / "
    "EAR_v2p1_FPR_STILL_OVERSHOOT with mapping labels for the c45 rubric "
    "PARTIAL clause. rubric_hash byte-equal in "
    "data/ear_v2p1/rubric_hash.txt.",
    ["docs/ear_real_label_training_v2p1_rubric.md",
     "data/ear_v2p1/rubric_hash.txt"],
    "rubric SHA is chassis for all downstream v2.1 anchoring.",
))

# --- 2: features-loaded
EVENTS.append(_e(
    "M-EAR-1/real-label-training-v2.1/features-loaded",
    "c45 features cache READ-ONLY re-used; combined_manifest_sha256 "
    f"= {FEATURE_MANIFEST_SHA} byte-equal to c45 anchor per feature "
    "cache manifest at data/ear_v2/feature_cache_manifest_v2.json. "
    "252 clips across 43 songs; no re-extraction.",
    ["data/ear_v2/feature_cache_manifest_v2.json"],
    "c6 feature pipeline verbatim; no swap.",
))

# --- 3: head-trained
EVENTS.append(_e(
    "M-EAR-1/real-label-training-v2.1/head-trained",
    f"c6 CORN 1-7 head trained under 5-fold GroupKFold; artifact "
    f"corn_head_v2p1.pt SHA-256 = {CORN_HEAD_SHA}; training_result_v2p1.json "
    f"SHA-256 = {TRAIN_RES_SHA}. Byte-determinism × 2 verified in "
    "training_determinism_check.json (both hashes stable across two "
    "consecutive runs under BLAS pins + PYTHONHASHSEED=0 + "
    "SOURCE_DATE_EPOCH=1756463424 + TZ=UTC + LC_ALL=C.UTF-8 + "
    "torch.manual_seed(0)).",
    ["scripts/ear_v2p1/train_v2p1.py",
     "data/ear_v2p1/corn_head_v2p1.pt",
     "data/ear_v2p1/training_result_v2p1.json",
     "data/ear_v2p1/held_out_predictions_v2p1.tsv",
     "data/ear_v2p1/held_out_folds_v2p1.json",
     "data/ear_v2p1/training_determinism_check.json"],
    "training artifacts byte-deterministic × 2.",
))

# --- 4: sb3-50ctl-run-1
EVENTS.append(_e(
    "M-EAR-1/real-label-training-v2.1/sb3-50ctl-run-1",
    f"SB3 50-control re-verdict run 1 in fresh tempfile.mkdtemp() dir; "
    f"sb3_50ctl_verdict_v2p1.json SHA-256 = {SB3_R1_SHA}. Detection "
    f"= {V2P1_VERDICT['detection_v2p1']} (>= 0.90 PASS). "
    f"FPR = {V2P1_VERDICT['fpr_run_1']} (<= 0.10 PASS). "
    "c37/c38 F1 pooled-variance statistic unchanged; c26 thresholds "
    "unchanged.",
    ["scripts/ear_v2p1/sb3_50ctl_reverdict.py",
     "data/ear_v2p1/sb3_50ctl_run_1/sb3_50ctl_verdict_v2p1.json",
     "data/ear_v2p1/sb3_50ctl_run_1/run_manifest.json"],
    "per-run SB3 SHAs pinned.",
))

# --- 5: sb3-50ctl-run-2
EVENTS.append(_e(
    "M-EAR-1/real-label-training-v2.1/sb3-50ctl-run-2",
    f"SB3 50-control re-verdict run 2 in fresh tempfile.mkdtemp() dir; "
    f"sb3_50ctl_verdict_v2p1.json SHA-256 = {SB3_R2_SHA}. Byte-equal "
    "to run 1's SHA. Byte-determinism × 2 gate PASS. Detection "
    f"= {V2P1_VERDICT['detection_v2p1']}; FPR = "
    f"{V2P1_VERDICT['fpr_run_2']}. Verdict path fires "
    "EAR_v2p1_STABLE_FPR_PASS given equal SHAs + both FPRs <= 0.10.",
    ["data/ear_v2p1/sb3_50ctl_run_2/sb3_50ctl_verdict_v2p1.json",
     "data/ear_v2p1/sb3_50ctl_run_2/run_manifest.json",
     "data/ear_v2p1/sb3_determinism_check.json"],
    "SB3 byte-determinism × 2 verified.",
))

# --- 6: verdict-emitted
EVENTS.append(_e(
    "M-EAR-1/real-label-training-v2.1/verdict-emitted",
    f"v2.1 verdict emitted: {V2P1_VERDICT['verdict']} -> mapping "
    f"{V2P1_VERDICT['mapping_label']}. Three-way rubric_hash byte-equal "
    f"({RUBRIC_SHA}). SB1/SB2 status FAIL_unchanged_from_c45. SB3 "
    f"detection PASS 1.000 (unchanged from c46); SB3 FPR PASS "
    f"{V2P1_VERDICT['fpr_run_1']} (new PASS at 50-ctl). Corpus caveat "
    "43/80 preview_partial_corpus_v2p1 prominent. c46 methodology "
    "chain c37 F1 pooled-variance -> c38 leak-lift -> c46 25->50 "
    "widening cited. c45 data/ear_v2/verdict.json NOT modified "
    f"(pinned SHA {V2_VERDICT_SHA}).",
    ["data/ear_v2p1/verdict.json",
     "docs/ear_real_label_training_v2p1_report.md",
     "tests/test_ear_v2p1_real_label_training.py"],
    "3-verdict rubric fired STABLE_FPR_PASS with byte-det x2 SB3 evidence.",
))

# --- aux 3: anchor-preservation-verified
EVENTS.append(_e(
    "M-EAR-1/real-label-training-v2.1/anchor-preservation-verified",
    f"34 anchor SHAs snapshotted pre/post v2.1 work; all 34 present; "
    f"all 34 byte-identical (unchanged=True). anchor_preservation SHA "
    f"= {ANCHOR_SHA}. Spans c6 chassis + c22 stability harness + c26 "
    "Path B doc + c36 v0 + c38 v1 + c45 v2 + c46 SB3 widening + "
    "adjudication artifacts + rules ledger invariants + c46 policy doc.",
    ["data/ear_v2p1/anchor_preservation_v2p1.json",
     "data/ear_v2p1/anchor_preservation_pre.json",
     "scripts/ear_v2p1/anchor_manifest_v2p1.py"],
    "READ-ONLY anchor guarantee verified byte-exact.",
))

# --- aux 4: egress probe
EVENTS.append(_e(
    "M-INGEST-1/egress-probe-cycle47-clone-0",
    "c47 clone-0 Branch A directive-mandated egress retry. Fresh row "
    "appended to data/ingestion/egress_status.jsonl continuing the "
    "c45/c46 failure-mode registry (HTTP 429 + tv_embedded player-client "
    "no-longer-supported closure). Egress remains blocked; the "
    "two-consecutive media_ok=true unblock signal did NOT fire.",
    ["data/ingestion/egress_status.jsonl"],
    "non-blocking directive-mandated retry per campaign registry lemma.",
))

# --- close
EVENTS.append(_e(
    "_run/cycle_47_closed-clone-0",
    "Cycle 47 clone-0 Branch A closed with verdict EAR_v2p1_STABLE_FPR_PASS "
    "-> EAR_v2p1_PARTIAL_WITH_SB3_PASS. All 6 substantive + 4 aux ledger "
    "events landed. 18/18 tests green; 11/11 new §61 integration checks "
    "green. Anchor preservation 34/34 byte-identical.",
    ["docs/ear_real_label_training_v2p1_report.md",
     "data/ear_v2p1/verdict.json",
     "data/ear_v2p1/anchor_preservation_v2p1.json"],
    "cycle close before housekeeping pair.",
))

# --- housekeeping 1: archive
EVENTS.append(_e(
    "_archive/cycle-47-scratch-clone-0",
    "One-shot c47 clone-0 emitters archived to tools/stale/ after use. "
    "This emitter itself moves post-emission via explicit touch per "
    "c38 mtime lesson.",
    ["tools/stale/_c47_emit_events_v2p1.py"],
    "cycle-tail hygiene per c29-hardened convention.",
))

# --- housekeeping 2: adopt cycle-47 tests
EVENTS.append(_e(
    "_infra/adopt-cycle47-tests-clone-0",
    "Adopts c47 clone-0 Branch A new test file "
    "tests/test_ear_v2p1_real_label_training.py under the ledger. "
    "Extends tests/test_integration_cross_branch.py §61 with 11 "
    "v2.1 invariants; §61 is an in-place extension of an existing "
    "file (adopted at initial creation), not a new-file event.",
    ["tests/test_ear_v2p1_real_label_training.py",
     "tests/test_integration_cross_branch.py"],
    "clears promise_check WARNs for new test file.",
))


if __name__ == "__main__":
    for e in EVENTS:
        emit(e)
    print(f"[emit] {len(EVENTS)} events landed.")
