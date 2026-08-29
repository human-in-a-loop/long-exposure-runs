#!/usr/bin/env /usr/bin/python3
"""Cycle 47 Branch C: anchor preservation post-work snapshot.

Asserts the 18 pre-existing anchor entries in `data/anchor_manifest_v1.json`
are byte-identical to their pre-work snapshot
(`data/deprecation_and_anchor_pin/anchor_preservation_pre.json`) — the
manifest only grew by one entry (SOURCE_DATE_EPOCH). Also re-verifies:

- c46 canonical `scripts/ear_v2/adjudication/determinism_check_c46.py`
  SHA + mtime unchanged.
- c22 stability_harness anchor entries (from the manifest) byte-identical.

Writes `data/deprecation_and_anchor_pin/anchor_preservation.json`.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

if not sys.executable.startswith("/usr/bin/python"):
    print(f"[preserve] REFUSE: interpreter {sys.executable!r} is not /usr/bin/python3",
          file=sys.stderr)
    sys.exit(2)

WS = "/home/user/long-exposure-runs/music-gen"
MANIFEST = os.path.join(WS, "data/anchor_manifest_v1.json")
C46 = os.path.join(WS, "scripts/ear_v2/adjudication/determinism_check_c46.py")
PRE = os.path.join(WS, "data/deprecation_and_anchor_pin/anchor_preservation_pre.json")
OUT = os.path.join(WS, "data/deprecation_and_anchor_pin/anchor_preservation.json")


def sha256_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _summarize_anchor(a: dict) -> dict:
    return {
        "anchor_id": a["anchor_id"],
        "kind": a["kind"],
        "cycle": a.get("cycle"),
        "file_count": a.get("file_count"),
        "dir_manifest_sha_per_dir": a.get("dir_manifest_sha_per_dir", {}),
    }


def main() -> int:
    pre = json.load(open(PRE))
    m = json.load(open(MANIFEST))

    # 18 pre-existing entries preserved: match by anchor_id.
    pre_by_id = {a["anchor_id"]: a for a in pre["anchors_pre"]}
    post_by_id = {a["anchor_id"]: _summarize_anchor(a) for a in m["anchors"]}

    preserved = []
    drift = []
    for aid, pre_a in pre_by_id.items():
        post_a = post_by_id.get(aid)
        if post_a is None:
            drift.append({"anchor_id": aid, "reason": "missing post-work"})
            continue
        # Compare identity + sha maps.
        if pre_a == post_a:
            preserved.append(aid)
        else:
            drift.append({"anchor_id": aid, "reason": "content differs",
                          "pre": pre_a, "post": post_a})

    new_entry = None
    for aid, post_a in post_by_id.items():
        if aid not in pre_by_id:
            new_entry = m["anchors"][[a["anchor_id"] for a in m["anchors"]].index(aid)]

    c46_post_sha = sha256_file(C46)
    c46_post_mtime = os.path.getmtime(C46)
    c46_preserved = (
        c46_post_sha == pre["c46_canonical"]["sha256"]
        and c46_post_mtime == pre["c46_canonical"]["mtime"]
    )

    # c22 stability harness anchor (`c22_stability_harness`) present in both.
    c22_pre = pre_by_id.get("c22_stability_harness")
    c22_post = post_by_id.get("c22_stability_harness")
    c22_preserved = (c22_pre == c22_post)

    result = {
        "cycle": 47,
        "branch": "C",
        "clone": 2,
        "n_pre_entries": len(pre_by_id),
        "n_post_entries": len(post_by_id),
        "n_preserved": len(preserved),
        "preserved_anchor_ids": sorted(preserved),
        "drift": drift,
        "new_entry": new_entry,
        "c46_canonical_preserved": c46_preserved,
        "c46_pre_sha": pre["c46_canonical"]["sha256"],
        "c46_post_sha": c46_post_sha,
        "c22_stability_harness_preserved": c22_preserved,
        "intentional_writes": [
            "data/anchor_manifest_v1.json (append-only: 18 -> 19 entries)",
            "docs/anchor_manifest_v1.md (append-only: row #19 + section)",
        ],
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")

    print(f"[preserve] n_preserved={len(preserved)}/{len(pre_by_id)} "
          f"c46_preserved={c46_preserved} c22_preserved={c22_preserved}")
    print(f"[preserve] wrote {OUT}")
    return 0 if not drift and c46_preserved and c22_preserved else 1


if __name__ == "__main__":
    raise SystemExit(main())
