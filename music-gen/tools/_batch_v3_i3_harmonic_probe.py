#!/usr/bin/env -S /usr/bin/python3
"""One-shot probe: show which key each salt's harmonic rule uses."""
import json
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
ledger = [json.loads(ln) for ln in
          open(_REPO / "data/rules/ledger_i3_dminor.jsonl").read().splitlines() if ln]
by_rid = {r.get("rule_id"): r for r in ledger}
print("salt | harmonic rule_id     | key       | chord_progression")
print("-" * 90)
for s in range(8):
    sm = json.load(open(_REPO / f"data/gen/batch_v3_i3/song_{s}/sampling_manifest.json"))
    rid = sm["chosen_rule_ids"]["harmonic"]
    r = by_rid.get(rid, {})
    p = r.get("parameters", {})
    cp = p.get("chord_progression", [])
    cp_str = "-".join(cp[:6]) + ("…" if len(cp) > 6 else "")
    print(f"  {s}  | {rid} | {p.get('key','?'):9s} | {cp_str}")
