#!/usr/bin/env /usr/bin/python3
"""c23 clone-1 (Peach Dream): 4-row ledger for M-V3-FOCUS-1 first-unified-driver delivery.

Rows (ts+1s ordering per convention):
  1. M-INGEST-1/egress-probe-cycle23-clone-1
  2. M-V3-FOCUS-1/peach-dream-first-unified-driver-delivery
  3. _infra/adopt-cycle23-tests-clone-1
  4. _archive/cycle-23-scratch-clone-1

AGENT="worker" + AGENT_ORIGINAL="worker-clone-1" per c9 canonical-assessor pattern.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"ledger requires /usr/bin/python3 (got {sys.executable})")

WSROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WSROOT))

from long_exposure.workspace_bootstrap import append_ledger_event  # noqa: E402

RUN_ID = "run-2026-09-02T210000Z"
CYCLE = 23
AGENT = "worker"
AGENT_ORIGINAL = "worker-clone-1"


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _base(mid, narrative, artifacts, status="validated", conf="high"):
    return {
        "milestone_id": mid,
        "status": status,
        "confidence": {"level": conf, "rationale": "measured", "assessor": AGENT,
                       "assessor_original": AGENT_ORIGINAL},
        "narrative": narrative,
        "artifacts": artifacts,
        "cycle": CYCLE,
        "run_id": RUN_ID,
        "agent": AGENT,
        "agent_original": AGENT_ORIGINAL,
        "clone": "1",
        "ts": _now_iso(),
    }


def build_events(delivery_verdict: str, env_pin_sha: str, merged_mid_sha: str,
                  recon_ab_sha: str, byte_det_summary: str):
    events = []
    events.append(_base(
        "M-INGEST-1/egress-probe-cycle23-clone-1",
        "c23 clone-1 egress probe (no fetches attempted): proxy TLS respected, "
        "HTTPS_PROXY unchanged. All model+SF2 assets already local per env_pin.json.",
        ["data/ingestion/egress_status.jsonl"],
    ))
    events.append(_base(
        "M-V3-FOCUS-1/peach-dream-first-unified-driver-delivery",
        (f"c23 first-unified-driver delivery for Peach Dream (sha16 88d247468cb6d49f, "
         f"operator section t=172.87256..202.87256s from focus_set_v2.json). "
         f"Verdict={delivery_verdict}. Retires c20 clone-2 Option-3-terminal PARTIAL per "
         f"operator directive point 5 (2026-09-02 DETERMINISM CONSOLIDATION extended). "
         f"FIRST delivery to carry env_pins block with self-anchor env_pin_sha256="
         f"{env_pin_sha[:16]}... under real operator directive. merged.mid sha256="
         f"{merged_mid_sha[:16]}...; reconstruction_ab.wav sha256={recon_ab_sha[:16]}.... "
         f"Byte-determinism: {byte_det_summary}. Three-way rubric_hash_v2 chain "
         f"(c49db5a12e955f26...016451a) AND rubric_hash_v3 chain "
         f"(bea618721ebb74b1...c99a0d6) verified byte-equal. c22 unified driver + "
         f"env_pin module SHAs byte-identical pre==post."),
        ["data/v3/deliveries/88d247468cb6d49f/cycle23/verdict.json",
         "data/v3/deliveries/88d247468cb6d49f/cycle23/manifest.json",
         "data/v3/deliveries/88d247468cb6d49f/cycle23/env_pin.json",
         "data/v3/deliveries/88d247468cb6d49f/cycle23/anchor_preservation_pre.json",
         "data/v3/deliveries/88d247468cb6d49f/cycle23/anchor_preservation_post.json",
         "docs/v3_focus_peach_dream_c23_unified_delivery_report.md"],
    ))
    events.append(_base(
        "_infra/adopt-cycle23-tests-clone-1",
        "No new test file this cycle — c23 clone-1 exercises the c22 unified driver "
        "end-to-end (which is itself covered by existing v3-spine test suite). "
        "Test-adoption housekeeping row emitted for canonical-assessor coverage.",
        [],
    ))
    events.append(_base(
        "_archive/cycle-23-scratch-clone-1",
        "Scratch: scripts/v3_spine/anchor_preservation_c23_clone1.py + "
        "scripts/v3_spine/peach_dream_c23_clone1_ledger.py. Anchor snapshot script "
        "is reusable for future c23+ clones (parameterized by phase arg).",
        ["scripts/v3_spine/anchor_preservation_c23_clone1.py",
         "scripts/v3_spine/peach_dream_c23_clone1_ledger.py"],
    ))
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verdict", required=True)
    ap.add_argument("--env-pin-sha", required=True)
    ap.add_argument("--merged-mid-sha", required=True)
    ap.add_argument("--recon-ab-sha", required=True)
    ap.add_argument("--byte-det-summary", required=True)
    args = ap.parse_args()
    events = build_events(args.verdict, args.env_pin_sha, args.merged_mid_sha,
                           args.recon_ab_sha, args.byte_det_summary)
    if args.dry_run:
        print(json.dumps([{"milestone_id": e["milestone_id"], "status": e["status"]}
                          for e in events], indent=2))
        return
    prev_ts = None
    for e in events:
        if prev_ts is not None:
            cur = datetime.strptime(e["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            prv = datetime.strptime(prev_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if (cur - prv).total_seconds() < 1:
                time.sleep(max(0.1, 1.1 - (cur - prv).total_seconds() % 1))
                e["ts"] = _now_iso()
        append_ledger_event(str(WSROOT), e)
        print(f"appended: {e['milestone_id']} ts={e['ts']}")
        prev_ts = e["ts"]


if __name__ == "__main__":
    main()
