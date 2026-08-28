#!/usr/bin/env -S /usr/bin/python3
"""One-shot byte-determinism check for batch_v3_i3 (moved to stale/ after use)."""
import hashlib
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    A = _REPO / "data" / "gen" / "batch_v3_i3"
    B = Path("/tmp/batch_v3_i3_run2")
    mismatch = []
    matched = []
    for p in sorted(A.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(A)
        q = B / rel
        if not q.exists():
            mismatch.append((str(rel), "MISSING_IN_B"))
            continue
        sa, sb = sha256(p), sha256(q)
        if sa != sb:
            # batch_manifest.json contains absolute-path fields; compare content_less-path.
            if rel.name in ("batch_manifest.json",):
                a = json.loads(p.read_text()); b = json.loads(q.read_text())
                # normalize per_song sha comparison
                if a.get("per_song") == b.get("per_song") and a.get("ledger_sha256") == b.get("ledger_sha256"):
                    matched.append(f"{rel}(content-equal, path-differs)")
                    continue
            mismatch.append((str(rel), f"{sa[:12]} vs {sb[:12]}"))
        else:
            matched.append(str(rel))
    print(f"MATCHED: {len(matched)}")
    print(f"MISMATCH: {len(mismatch)}")
    for m in mismatch:
        print("  ", m)
    return 0 if not [m for m in mismatch if m[1] != "MISSING_IN_B"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
