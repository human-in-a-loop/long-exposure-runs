#!/usr/bin/python3
"""One-shot: find shadow-ledger rows for fork 33a2a8003c84 not yet in main."""
import json
from pathlib import Path

ROOT = Path("/home/user/long-exposure-runs/music-gen")
with open(ROOT / "promise_ledger.jsonl") as f:
    main_eids = {json.loads(l).get("event_id") for l in f}

for k in range(3):
    p = Path(f"/home/user/music-gen-instance/fork-33a2a8003c84/clone-{k}/promise_ledger.jsonl")
    missing = []
    with open(p) as f:
        for line in f:
            ev = json.loads(line)
            if ev.get("event_id") not in main_eids:
                missing.append(ev)
    print(f"clone-{k}: {len(missing)} rows missing")
    for m in missing:
        arts = m.get("artifacts") or []
        n_arts = len(arts) if isinstance(arts, list) else "?"
        print(f"  {m.get('milestone_id')} cycle={m.get('cycle')} ts={m.get('ts')} n_arts={n_arts}")
