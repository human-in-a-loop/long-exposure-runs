"""
PhytoGraph Atlas — counter-claim CLI (M3.A).

Header metadata (artifact-tracking):
  created: 2026-05-18T03:10:00+00:00
  cycle: 9
  run_id: run-phytograph-cycle9-wave3-atlas
  agent: worker
  milestone: M3.A

Validates a JSON payload, appends it to
botanical_atlas_site/counter_claims.jsonl (append-only), and emits a
matching `_run/counter-claim-<uuid>` event to the promise ledger.

Usage:
    cat payload.json | python3 tools/file_counter_claim.py
    python3 tools/file_counter_claim.py --payload payload.json
    python3 tools/file_counter_claim.py --inline '{"accepted_taxon_key":...}'

Schema (phytograph.counter_claim.v1):
    accepted_taxon_key : str, required
    target_edge_id     : str, required (rejects empty / missing)
    target_kind        : str, required (observed_row|enriched_row|predicted_row|header_row|evidence_row_or_prediction)
    reviewer_id        : str, required (orcid:... | email:... | any non-empty)
    comment            : str, 1..5000 chars, required
    iso_timestamp      : str, ISO-8601, filled if missing
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
JSONL = REPO / "botanical_atlas_site" / "counter_claims.jsonl"

REQUIRED = ["accepted_taxon_key", "target_edge_id", "target_kind",
            "reviewer_id", "comment"]


class CounterClaimError(ValueError):
    pass


def validate(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise CounterClaimError("payload must be a JSON object")
    for k in REQUIRED:
        v = payload.get(k)
        if v is None or (isinstance(v, str) and not v.strip()):
            raise CounterClaimError(
                f"missing required field: {k!r} (counter-claims MUST target "
                "an explicit row id; free-form notes are rejected)")
    if not isinstance(payload["comment"], str) or len(payload["comment"]) > 5000:
        raise CounterClaimError("comment must be a string of length 1..5000")
    payload.setdefault("schema", "phytograph.counter_claim.v1")
    payload.setdefault("iso_timestamp",
                       datetime.now(timezone.utc).isoformat())
    payload.setdefault("counter_claim_id", str(uuid.uuid4()))
    return payload


def append(payload: dict, jsonl_path: Path = JSONL) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    # Append-only: never edits prior rows.
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def emit_ledger(payload: dict) -> bool:
    """Emit `_run/counter-claim-<uuid>` event via ledger_append helper.
    Returns True if the helper exited 0."""
    cc_id = payload.get("counter_claim_id", str(uuid.uuid4()))
    event = {
        "ts": payload["iso_timestamp"],
        "milestone_id": f"_run/counter-claim-{cc_id}",
        "status": "in-progress",
        "confidence": {"level": "low",
                       "rationale": "Filed counter-claim; awaits curator review."},
        "agent": "atlas-counter-claim-cli",
        "cycle": 9,
        "run_id": os.environ.get("LE_RUN_ID",
                                 "run-phytograph-cycle9-wave3-atlas"),
        "rationale": (
            f"Counter-claim against {payload['target_edge_id']} for taxon "
            f"{payload['accepted_taxon_key']} ({payload['target_kind']}) "
            f"filed by {payload['reviewer_id']}."
        ),
        "artifacts": ["botanical_atlas_site/counter_claims.jsonl"],
        "supersedes": [],
    }
    try:
        r = subprocess.run(
            ["python3", "-m", "long_exposure.tools.ledger_append",
             "--event", json.dumps(event)],
            cwd=str(REPO), capture_output=True, text=True, timeout=30)
        return r.returncode == 0
    except Exception:
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--payload", type=str, help="path to a JSON file")
    g.add_argument("--inline", type=str, help="JSON string")
    ap.add_argument("--no-ledger", action="store_true",
                    help="skip ledger emission (for tests)")
    ap.add_argument("--jsonl", type=str, default=str(JSONL),
                    help="counter-claims jsonl path (for tests)")
    args = ap.parse_args(argv)

    if args.payload:
        raw = Path(args.payload).read_text()
    elif args.inline:
        raw = args.inline
    else:
        raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: payload is not valid JSON: {e}", file=sys.stderr)
        return 2
    try:
        payload = validate(payload)
    except CounterClaimError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3

    append(payload, jsonl_path=Path(args.jsonl))
    if not args.no_ledger:
        ok = emit_ledger(payload)
        if not ok:
            print("WARN: ledger emission failed; counter-claim was still "
                  "appended to JSONL.", file=sys.stderr)
    print(json.dumps({"status": "appended",
                      "counter_claim_id": payload["counter_claim_id"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
