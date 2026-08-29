"""Cycle-36 post-merge integration for fork 87da4f517029.

Reconciles three clone shadow ledgers into the main promise_ledger.jsonl,
renaming the 2 colliding M-INGEST-1/egress-probe rows to add -clone-<k>
suffix, then sorts per-milestone by (ts, content_hash) and appends.

Runs in root-scope only (no AGENT_FORK_ID env var). Does not use
append_ledger_event's clone guard - writes rows verbatim via direct file
append with pre-validated content.
"""
# created: 2026-08-29T08:15:00Z
# cycle: 36
# run_id: run-2026-08-28T040704Z
# agent: worker (post-merge integration, root scope)
# milestone: _run/post-merge-integration-fork-87da4f517029
import hashlib
import json
import os
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

# Root-scope: clear clone context env vars before importing writer.
for _k in ("AGENT_FORK_ID", "AGENT_INSTANCE_DIR", "AGENT_CLONE_ID",
           "AGENT_FORK_CLONE_K"):
    os.environ.pop(_k, None)

sys.path.insert(0, "/home/user/human-in-a-loop/long-exposure")

from long_exposure.workspace_bootstrap import append_ledger_event
from long_exposure.tools._ledger_schema import validate_event

WORKSPACE = Path("/home/user/long-exposure-runs/music-gen")
LEDGER = WORKSPACE / "promise_ledger.jsonl"
FORK_ROOT = Path("/home/user/music-gen-instance/fork-87da4f517029")


def _canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _content_hash(row):
    # SHA-256 of canonical json excluding event_id + ts (per c15 concat
    # rule)
    scratch = {k: v for k, v in row.items() if k not in ("event_id", "ts")}
    return hashlib.sha256(_canonical_json(scratch).encode()).hexdigest()


# --- Load shadow rows ---
per_clone = {}
for k in (0, 1, 2):
    path = FORK_ROOT / f"clone-{k}" / "promise_ledger.jsonl"
    rows = []
    for i, raw in enumerate(path.read_text().splitlines(), 1):
        if not raw.strip():
            continue
        rows.append(json.loads(raw))
    per_clone[k] = rows

# --- Apply reconciliation ---
# Rule: the only collision this cycle is on M-INGEST-1/egress-probe.
# Rename both occurrences to add -clone-<k> suffix so the concat is
# unambiguous.
COLLIDING = "M-INGEST-1/egress-probe"
renamed_map = []
for k, rows in per_clone.items():
    for r in rows:
        mid = r.get("milestone_id", "")
        if mid == COLLIDING:
            old = mid
            new = f"{old}-clone-{k}"
            r["milestone_id"] = new
            # invalidate any stored event_id - writer will regen on
            # re-emit; here we drop and recompute via UUID5 content-hash
            if "event_id" in r:
                r.pop("event_id")
            renamed_map.append((k, old, new))

print(f"Reconciliation renames: {renamed_map}")

# --- Regenerate event_id (UUID5 content-hash) for renamed rows only ---
import uuid
_NS_LE = uuid.UUID("00000000-0000-5000-8000-000000000000")
for k, rows in per_clone.items():
    for r in rows:
        if "event_id" not in r:
            r["event_id"] = str(uuid.uuid5(_NS_LE, _canonical_json(r)))

# --- Merge: emit all 31 rows, per-milestone sorted by (ts, content_hash)
# BUT preserve overall chronological order across clones ---
# The concat validator wants monotonic per-milestone ts; sorting by ts is
# safe since we renamed the colliding pair.
all_rows = []
for k, rows in per_clone.items():
    all_rows.extend(rows)

# Sort primarily by ts for chronological append, secondary by content-hash
# for tiebreak.
all_rows.sort(key=lambda r: (r.get("ts", ""), _content_hash(r)))

# --- Validate and append to main ---
before_lines = sum(1 for _ in open(LEDGER))
print(f"Main ledger before: {before_lines} lines")

new_appended = 0
with open(LEDGER, "a", encoding="utf-8") as f:
    for r in all_rows:
        # validate_event uses the SSoT contract; catches drift.
        validate_event(r)
        f.write(json.dumps(r) + "\n")
        new_appended += 1

after_lines = sum(1 for _ in open(LEDGER))
print(f"Main ledger after: {after_lines} lines (+{new_appended})")
assert after_lines == before_lines + new_appended
