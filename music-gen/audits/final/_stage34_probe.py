#!/usr/bin/env python3
"""Stage 34 (test 10/23) probes.

Four adversarial probes:
 P1) Housekeeping-event coverage sweep c3..c54 for _archive/cycle-<N>-scratch
     and _infra/adopt-cycle<N>-tests events.
 P2) Anchor manifest v1 SOURCE_DATE_EPOCH entry #19: verify claimed
     value_sha256 and entry_sha256 match canonical-JSON hash.
 P3) Grep for live-network imports in scripts/ear/train_armed_harness.py
     and scripts/egress_ready/*.
 P4) Enumerate unresolved _manager/* rows and assert each is terminal-
     validated or carries an explicit successor.
"""
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

WORKDIR = Path("/home/user/long-exposure-runs/music-gen")
LEDGER = WORKDIR / "promise_ledger.jsonl"


def load_ledger():
    events = []
    with LEDGER.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))
    return events


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def probe_housekeeping_coverage(events):
    """P1: verify c3..c54 has _archive/cycle-<N>-scratch and
    _infra/adopt-cycle<N>-tests events.
    """
    archive_re = re.compile(r"^_archive/cycle-(\d+)-scratch$")
    adopt_re = re.compile(r"^_infra/adopt-cycle(\d+)-tests$")
    archived = defaultdict(list)
    adopted = defaultdict(list)
    for ev in events:
        mid = ev.get("milestone_id", "")
        m = archive_re.match(mid)
        if m:
            archived[int(m.group(1))].append(ev.get("cycle"))
        m = adopt_re.match(mid)
        if m:
            adopted[int(m.group(1))].append(ev.get("cycle"))
    missing = []
    for N in range(3, 55):  # c3..c54 inclusive
        row = {"cycle": N,
               "archive_present": N in archived,
               "adopt_present": N in adopted}
        if not (row["archive_present"] and row["adopt_present"]):
            missing.append(row)
    return {
        "cycles_checked": list(range(3, 55)),
        "archive_covered": sorted(archived.keys()),
        "adopt_covered": sorted(adopted.keys()),
        "missing_or_incomplete": missing,
        "n_missing": len(missing),
    }


def probe_anchor_manifest_sha():
    """P2: verify SOURCE_DATE_EPOCH entry #19 sha values."""
    manifest_path = WORKDIR / "data/anchor_manifest_v1.json"
    if not manifest_path.exists():
        return {"error": "manifest file missing", "path": str(manifest_path)}
    manifest = json.loads(manifest_path.read_text())
    # Locate SOURCE_DATE_EPOCH entry
    entries = manifest.get("entries", manifest.get("anchors", []))
    if not entries and isinstance(manifest, list):
        entries = manifest
    target = None
    for i, e in enumerate(entries):
        key = e.get("key", "")
        if "SOURCE_DATE_EPOCH" in key:
            target = (i, e)
            break
    if target is None:
        return {"error": "SOURCE_DATE_EPOCH entry not found",
                "n_entries": len(entries),
                "keys_sample": [e.get("key") for e in entries[:20]]}
    idx, entry = target
    # Recompute value_sha256: sha256(str(1756463424).encode("utf-8"))
    value = entry.get("value")
    value_str = str(value)
    computed_value_sha = hashlib.sha256(value_str.encode("utf-8")).hexdigest()
    claimed_value_sha = entry.get("value_sha256")
    # Recompute entry_sha256: sha256(canonical_json({"key":..,"value":..,"value_sha256":..}))
    subset = {"key": entry.get("key"),
              "value": entry.get("value"),
              "value_sha256": entry.get("value_sha256")}
    computed_entry_sha = hashlib.sha256(canonical_json(subset).encode("utf-8")).hexdigest()
    claimed_entry_sha = entry.get("entry_sha256")
    return {
        "entry_index_zero_based": idx,
        "entry_index_one_based": idx + 1,
        "key": entry.get("key"),
        "value": value,
        "claimed_value_sha256": claimed_value_sha,
        "computed_value_sha256": computed_value_sha,
        "value_sha_matches": claimed_value_sha == computed_value_sha,
        "claimed_entry_sha256": claimed_entry_sha,
        "computed_entry_sha256": computed_entry_sha,
        "entry_sha_matches": claimed_entry_sha == computed_entry_sha,
        "manifest_anchor_count": manifest.get("anchor_count"),
        "n_entries_actual": len(entries),
    }


def probe_live_network_imports():
    """P3: grep for live-network imports in armed-harness + egress_ready."""
    targets = [WORKDIR / "scripts/ear/train_armed_harness.py"]
    egress_dir = WORKDIR / "scripts/egress_ready"
    if egress_dir.exists():
        targets.extend(sorted(egress_dir.rglob("*.py")))
    # Also scan sb_dry_run.py per c31 fixture reinforcement
    sb_path = WORKDIR / "scripts/ear/sb_dry_run.py"
    if sb_path.exists():
        targets.append(sb_path)
    forbidden_modules = ["urllib", "requests", "socket", "httpx",
                         "aiohttp", "http.client", "urllib3"]
    import_re = re.compile(
        r"^\s*(?:import|from)\s+([A-Za-z_][A-Za-z0-9_.]*)")
    findings = []
    scanned = []
    for t in targets:
        if not t.exists():
            continue
        rel = str(t.relative_to(WORKDIR))
        scanned.append(rel)
        for i, line in enumerate(t.read_text().splitlines(), 1):
            m = import_re.match(line)
            if not m:
                continue
            mod_root = m.group(1).split(".")[0]
            if mod_root in [fm.split(".")[0] for fm in forbidden_modules]:
                findings.append({"file": rel, "line": i,
                                 "text": line.strip(),
                                 "module_root": mod_root})
    return {
        "files_scanned": scanned,
        "n_files_scanned": len(scanned),
        "forbidden_modules_checked": forbidden_modules,
        "violations": findings,
        "n_violations": len(findings),
    }


def probe_manager_unresolved(events):
    """P4: enumerate _manager/* rows and check terminal status."""
    manager_events = defaultdict(list)
    for ev in events:
        mid = ev.get("milestone_id", "")
        if mid.startswith("_manager/"):
            manager_events[mid].append(ev)
    terminal_statuses = {"validated", "superseded", "invalidated"}
    unresolved = []
    for mid, evs in manager_events.items():
        # Get latest event
        latest = max(evs, key=lambda e: e.get("ts", ""))
        status = latest.get("status", "")
        if status not in terminal_statuses:
            unresolved.append({
                "milestone_id": mid,
                "latest_status": status,
                "latest_cycle": latest.get("cycle"),
                "latest_ts": latest.get("ts"),
                "n_events": len(evs),
                "narrative_head": (latest.get("narrative") or
                                   latest.get("summary") or "")[:200],
            })
    return {
        "n_manager_milestones": len(manager_events),
        "n_terminal_or_resolved": len(manager_events) - len(unresolved),
        "n_unresolved": len(unresolved),
        "unresolved": unresolved,
    }


def main():
    events = load_ledger()
    print(f"Loaded {len(events)} ledger events", file=sys.stderr)
    results = {
        "P1_housekeeping_coverage": probe_housekeeping_coverage(events),
        "P2_anchor_manifest_sha": probe_anchor_manifest_sha(),
        "P3_live_network_imports": probe_live_network_imports(),
        "P4_manager_unresolved": probe_manager_unresolved(events),
    }
    out = WORKDIR / "audits/final/stages/_stage34_results.json"
    out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"Wrote {out}", file=sys.stderr)
    print(json.dumps({
        "P1_n_missing": results["P1_housekeeping_coverage"]["n_missing"],
        "P2_value_matches": results["P2_anchor_manifest_sha"].get("value_sha_matches"),
        "P2_entry_matches": results["P2_anchor_manifest_sha"].get("entry_sha_matches"),
        "P3_n_violations": results["P3_live_network_imports"]["n_violations"],
        "P4_n_unresolved": results["P4_manager_unresolved"]["n_unresolved"],
    }, indent=2))


if __name__ == "__main__":
    main()
