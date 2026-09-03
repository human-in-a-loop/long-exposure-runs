#!/usr/bin/env python3
"""One-shot: dump event_type column from clone-2 shadow ledger."""
import json
for ln in open("data/v3/rules/ledger_c23_clone_2.jsonl"):
    ev = json.loads(ln)
    print(ev.get("event_type"))
