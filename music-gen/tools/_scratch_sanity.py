#!/usr/bin/env -S /usr/bin/python3
"""One-shot sanity probe for the batch-v2 sampler + perturbation."""
import sys, json
sys.path.insert(0, "/home/user/long-exposure-runs/music-gen")
from pathlib import Path
from scripts.gen_palette_batch_v2.sample_rule_triple_v2 import sample_triples

triples = sample_triples([0, 1, 2])
print("triples:", json.dumps(triples, sort_keys=True, indent=2))
for rt in ("harmonic", "rhythmic", "arrangement"):
    picks = [triples[s][rt] for s in sorted(triples)]
    print(f"  {rt}: distinct={len(set(picks))==len(picks)} picks={picks}")

# List dawdreamer_state per_plugin dirs
d = Path("/home/user/long-exposure-runs/music-gen/data/dawdreamer_state/per_plugin")
print("plugins:", sorted(p.name for p in d.iterdir()) if d.is_dir() else "MISSING")
for pdir in sorted(d.iterdir()):
    p1 = pdir / "p1_state_v2.json"
    if not p1.exists():
        print(f"  {pdir.name}: MISSING p1_state_v2.json")
        continue
    obj = json.loads(p1.read_text())
    ip = obj.get("iterated_params") or {}
    print(f"  {pdir.name}: iterated_params size = {len(ip) if isinstance(ip, dict) else type(ip).__name__}, keys={sorted(obj.keys())}")
    if isinstance(ip, dict) and ip:
        for k in list(ip.keys())[:3]:
            print(f"    sample: {k!r} = {ip[k]!r}")
