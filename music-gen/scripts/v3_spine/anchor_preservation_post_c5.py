#!/usr/bin/env python3
"""c5 post-anchor snapshot: verify all pre-snapshot anchors byte-identical."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

PRE = Path("data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c5.json")
POST = Path("data/v3_spine/31a164f845f8e27e/anchor_preservation_c5.json")


def sha_of(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    pre = json.loads(PRE.read_text())
    diffs = []
    matches = 0
    now = {}
    for rel, meta in pre["anchors"].items():
        p = rel if rel.startswith("/") else str(Path.cwd() / rel)
        if not Path(p).exists():
            diffs.append({"path": rel, "kind": "missing_now"})
            continue
        h = sha_of(p)
        now[rel] = {"sha256": h, "size": Path(p).stat().st_size}
        if h != meta["sha256"]:
            diffs.append({
                "path": rel, "kind": "sha_changed",
                "pre_sha": meta["sha256"], "post_sha": h,
            })
        else:
            matches += 1

    out = {
        "cycle": 5,
        "role": "post",
        "n_pre": len(pre["anchors"]),
        "n_matched": matches,
        "n_diffs": len(diffs),
        "diffs": diffs,
        "all_match": len(diffs) == 0,
        "post_anchors": now,
    }
    POST.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"n_pre={len(pre['anchors'])} n_matched={matches} n_diffs={len(diffs)} all_match={out['all_match']}")
    if diffs:
        for d in diffs[:10]:
            print("  DIFF:", d)


if __name__ == "__main__":
    main()
