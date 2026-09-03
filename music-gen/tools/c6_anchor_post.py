#!/usr/bin/env -S /usr/bin/python3
"""Verify anchor preservation post c6."""
import hashlib, json, subprocess
from pathlib import Path

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

WS = Path(".")
pre = json.loads((WS / "data/v4/profiles/31a164f845f8e27e/anchor_preservation_pre_c6.json").read_text())
post_anchors = {}
mismatches = []
for k in pre["anchors"]:
    p = WS / k
    s = sha(p)
    post_anchors[k] = s
    if s != pre["anchors"][k]:
        mismatches.append((k, pre["anchors"][k], s))

spike_post = sha(WS / "scripts/sound_match/family2_stem_sampled_spike.py")
spike_ok = spike_post == pre["family2_spike_pre_sha"]

df = subprocess.check_output(["df", "-h", "."]).decode().splitlines()[1].split()

out = {
    "cycle": 6,
    "anchors_pre": pre["anchors"],
    "anchors_post": post_anchors,
    "all_match": len(mismatches) == 0,
    "n_mismatch": len(mismatches),
    "mismatches": mismatches,
    "family2_spike_pre_sha": pre["family2_spike_pre_sha"],
    "family2_spike_post_sha": spike_post,
    "family2_spike_unchanged": spike_ok,
    "df_pct_pre": pre["df_pct"],
    "df_pct_post": df[4],
}
p = WS / "data/v4/profiles/31a164f845f8e27e/anchor_preservation_post_c6.json"
p.write_text(json.dumps(out, sort_keys=True, indent=2))
print(json.dumps(out, sort_keys=True, indent=2))
if not out["all_match"] or not spike_ok:
    raise SystemExit(1)
