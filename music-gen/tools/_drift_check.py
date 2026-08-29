#!/usr/bin/env python3
"""Cross-check freshly frozen SHAs vs any prior SHA recorded in the ledger."""
import sys, json, re, hashlib
from pathlib import Path
assert sys.executable == "/usr/bin/python3"
WS = Path("/home/user/long-exposure-runs/music-gen")

manifest = json.loads((WS / "data/anchor_manifest_v1.json").read_bytes())
# path -> current sha
current = {}
for a in manifest["anchors"]:
    current.update(a["sha_per_path"])

SHA_RE = re.compile(r"\b([0-9a-f]{64})\b")

# Scan ledger for prior SHA claims:
#  - artifacts field: {"path": "...", "sha256": "..."} or free-form
#  - narratives / artifacts strings containing "sha ...abc" or "sha256:..."
drift = []
matched = 0
scanned_rows = 0
per_path_prior = {}  # path -> set of prior shas seen

def _record(path, sha):
    if not path:
        return
    if path not in current:
        return
    per_path_prior.setdefault(path, set()).add(sha)

with (WS / "promise_ledger.jsonl").open() as f:
    for line in f:
        scanned_rows += 1
        try:
            e = json.loads(line)
        except Exception:
            continue
        arts = e.get("artifacts") or []
        for a in arts:
            if isinstance(a, dict):
                p = a.get("path") or a.get("relpath") or a.get("file")
                s = a.get("sha256") or a.get("sha") or a.get("hash")
                if p and s and isinstance(s, str) and SHA_RE.fullmatch(s):
                    _record(p, s)

# Now check each recorded prior against current.
for path, prior_set in per_path_prior.items():
    cur = current.get(path)
    if not cur:
        continue
    for pr in prior_set:
        if pr == cur:
            matched += 1
        else:
            drift.append({"path": path, "prior_sha": pr, "current_sha": cur})

result = {
    "scanned_rows": scanned_rows,
    "paths_with_prior_sha": len(per_path_prior),
    "matched_prior_shas": matched,
    "drift_count": len(drift),
    "drift": drift,
}
print(json.dumps(result, indent=2))

# Write drift result to data/anchor_manifest_v1/
out = WS / "data/anchor_manifest_v1/drift_check.json"
out.write_text(json.dumps(result, indent=2, sort_keys=True))
