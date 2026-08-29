#!/usr/bin/python3
"""Baseline + shadow-ledger replay for c39 Branch C (convention v3).

Baseline replay: iterate all rows in ``promise_ledger.jsonl``, pass each
through ``long_exposure.tools._ledger_schema.validate_event``, assert
zero rejections.

Shadow-ledger replay: for c37 (fork 675abd086911) and c38 (fork
33a2a8003c84), read each clone's shadow ledger; for every row, extract
``(milestone_id, event_id, canonical_json_excluding_ts)`` and look up
the matching row in main. Assert byte-equal for every row that landed
in main; report any misses.

Byte-determinism: two consecutive invocations produce identical output
JSON (`--out data/fanout_namespace_v3/replay_baseline.json` etc.).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any

from long_exposure.tools._ledger_schema import validate_event

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
MAIN_LEDGER = ROOT / "promise_ledger.jsonl"

FORKS = {
    "c37": {
        "fork_id": "fork-675abd086911",
        "instance_root": pathlib.Path(
            "/home/user/music-gen-instance/fork-675abd086911"
        ),
    },
    "c38": {
        "fork_id": "fork-33a2a8003c84",
        "instance_root": pathlib.Path(
            "/home/user/music-gen-instance/fork-33a2a8003c84"
        ),
    },
}


def canonical_json_excluding_ts(row: dict) -> str:
    """Canonical JSON of a ledger row with the ``ts`` field removed."""
    scrubbed = {k: v for k, v in row.items() if k != "ts"}
    return json.dumps(scrubbed, sort_keys=True, separators=(",", ":"))


def load_main_index() -> dict[tuple[str, str], str]:
    """Index main ledger by (milestone_id, event_id) -> canonical_json-ts."""
    idx: dict[tuple[str, str], str] = {}
    with MAIN_LEDGER.open() as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            row = json.loads(line)
            mid = row.get("milestone_id")
            eid = row.get("event_id")
            if mid and eid:
                idx[(mid, eid)] = canonical_json_excluding_ts(row)
    return idx


def baseline_replay() -> dict[str, Any]:
    """Run validate_event on every main-ledger row."""
    total = 0
    errors: list[dict[str, Any]] = []
    with MAIN_LEDGER.open() as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            total += 1
            row = json.loads(line)
            row_errors = validate_event(row)
            if row_errors:
                errors.append(
                    {
                        "line": lineno,
                        "milestone_id": row.get("milestone_id"),
                        "event_id": row.get("event_id"),
                        "errors": row_errors,
                    }
                )
    return {
        "kind": "baseline_replay",
        "ledger_path": str(MAIN_LEDGER.relative_to(ROOT)),
        "total_rows": total,
        "passed": total - len(errors),
        "failed": len(errors),
        "errors": errors,
    }


def shadow_replay_one_clone(
    fork_id: str, clone_idx: int, shadow_path: pathlib.Path,
    main_idx: dict[tuple[str, str], str],
) -> dict[str, Any]:
    if not shadow_path.exists():
        return {
            "fork_id": fork_id,
            "clone": clone_idx,
            "shadow_path": str(shadow_path),
            "shadow_present": False,
            "rows": 0,
            "byte_identical_in_main": 0,
            "missing_in_main": 0,
            "mismatch_in_main": [],
            "missing_ids": [],
        }
    byte_identical = 0
    missing: list[dict[str, str]] = []
    mismatch: list[dict[str, Any]] = []
    total = 0
    with shadow_path.open() as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            total += 1
            row = json.loads(line)
            mid = row.get("milestone_id")
            eid = row.get("event_id")
            shadow_canon = canonical_json_excluding_ts(row)
            key = (mid, eid)
            if key not in main_idx:
                missing.append(
                    {"line": lineno, "milestone_id": mid, "event_id": eid}
                )
                continue
            if main_idx[key] != shadow_canon:
                mismatch.append(
                    {
                        "line": lineno,
                        "milestone_id": mid,
                        "event_id": eid,
                        "shadow_canon_sha256": hashlib.sha256(
                            shadow_canon.encode()
                        ).hexdigest(),
                        "main_canon_sha256": hashlib.sha256(
                            main_idx[key].encode()
                        ).hexdigest(),
                    }
                )
                continue
            byte_identical += 1
    return {
        "fork_id": fork_id,
        "clone": clone_idx,
        "shadow_path": str(shadow_path),
        "shadow_present": True,
        "rows": total,
        "byte_identical_in_main": byte_identical,
        "missing_in_main": len(missing),
        "mismatch_in_main": mismatch,
        "missing_ids": missing,
    }


def shadow_replay(fork_label: str) -> dict[str, Any]:
    spec = FORKS[fork_label]
    main_idx = load_main_index()
    clones: list[dict[str, Any]] = []
    for k in range(3):
        clone_dir = spec["instance_root"] / f"clone-{k}"
        shadow_path = clone_dir / "promise_ledger.jsonl"
        clones.append(shadow_replay_one_clone(spec["fork_id"], k, shadow_path, main_idx))
    total_rows = sum(c["rows"] for c in clones)
    total_byte_id = sum(c["byte_identical_in_main"] for c in clones)
    total_missing = sum(c["missing_in_main"] for c in clones)
    total_mismatch = sum(len(c["mismatch_in_main"]) for c in clones)
    return {
        "kind": f"shadow_replay_{fork_label}",
        "fork_id": spec["fork_id"],
        "clones": clones,
        "total_rows": total_rows,
        "total_byte_identical_in_main": total_byte_id,
        "total_missing_in_main": total_missing,
        "total_mismatch_in_main": total_mismatch,
        "byte_identical_all_rows": total_byte_id == total_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["baseline", "c37", "c38", "all"])
    parser.add_argument("--out", required=False, default=None)
    args = parser.parse_args()

    if args.kind == "baseline":
        result = baseline_replay()
        default_out = ROOT / "data/fanout_namespace_v3/replay_baseline.json"
    elif args.kind == "c37":
        result = shadow_replay("c37")
        default_out = ROOT / "data/fanout_namespace_v3/replay_c37_clones.json"
    elif args.kind == "c38":
        result = shadow_replay("c38")
        default_out = ROOT / "data/fanout_namespace_v3/replay_c38_clones.json"
    else:
        result = {
            "baseline": baseline_replay(),
            "c37": shadow_replay("c37"),
            "c38": shadow_replay("c38"),
        }
        default_out = ROOT / "data/fanout_namespace_v3/replay_all.json"

    out_path = pathlib.Path(args.out) if args.out else default_out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    out_path.write_text(serialized)
    print(f"wrote {out_path}  bytes={len(serialized)}  sha256={hashlib.sha256(serialized.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
