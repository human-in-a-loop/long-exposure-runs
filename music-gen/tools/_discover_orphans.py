"""One-shot: discover orphan artifacts for fork 392503ab7d47 clones."""
from __future__ import annotations
import json, os

with open("promise_ledger.jsonl") as f:
    adopted = set()
    for line in f:
        r = json.loads(line)
        for a in r.get("artifacts", []) or []:
            adopted.add(a)

want = []
bases = ["docs/figures", "scripts/rules/sampling", "scripts/gen",
         "data/gen/batch_v3_i3", "data/gen/batch_v3_i4", "data/rules",
         "tests", "docs"]
keys = ["batch_v3", "v3_i3", "v3_i4", "i3_dminor", "i4_stratified",
        "ledger_schema_hardening_v3", "ledger_i3_dminor",
        "gen_batch_v3", "v3-hardening", "batch-v3"]

for base in bases:
    if not os.path.exists(base):
        continue
    for root, dirs, files in os.walk(base):
        if "__pycache__" in root:
            continue
        for fn in files:
            p = os.path.relpath(os.path.join(root, fn))
            if p in adopted:
                continue
            if any(k in p for k in keys):
                want.append(p)

for p in sorted(want):
    print(p)
