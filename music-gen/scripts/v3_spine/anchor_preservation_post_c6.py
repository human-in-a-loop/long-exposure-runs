#!/usr/bin/env python3
"""c6 post-anchor verification: re-hash the c6 pre-anchor set and
assert every entry byte-identical to pre-snapshot."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path


PRE_PATH = Path("data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c6.json")
POST_PATH = Path("data/v3_spine/31a164f845f8e27e/anchor_preservation_post_c6.json")


def main() -> int:
    pre = json.loads(PRE_PATH.read_text())
    n_diff = 0
    diffs: list[dict] = []
    for rel, entry in pre["anchors"].items():
        p = rel if rel.startswith("/") else rel
        if not Path(p).exists():
            n_diff += 1
            diffs.append({"path": rel, "reason": "missing_post"})
            continue
        h = hashlib.sha256(Path(p).read_bytes()).hexdigest()
        if h != entry["sha256"]:
            n_diff += 1
            diffs.append({"path": rel, "reason": "sha_mismatch",
                          "pre_sha256": entry["sha256"], "post_sha256": h})
    out = {
        "cycle": 6,
        "role": "post",
        "pre_snapshot_sha256": hashlib.sha256(PRE_PATH.read_bytes()).hexdigest(),
        "n_anchors": pre["n_anchors"],
        "n_diff": n_diff,
        "all_match": n_diff == 0,
        "diffs": diffs,
    }
    POST_PATH.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"n_anchors={out['n_anchors']} n_diff={n_diff} all_match={out['all_match']}")
    return 0 if n_diff == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
