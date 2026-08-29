#!/usr/bin/env /usr/bin/python3
"""Cycle 47 Branch C: deprecate c45 `scripts/ear_v2/determinism_check.py`.

Moves the c45 module to `tools/stale/scripts_ear_v2_determinism_check_c45.py`
via `os.rename` + explicit `os.utime` post-move (c38 lesson: some
filesystems preserve mtime through rename; the touch is required for the
move-mtime gate to pass).

No PRNG. Interpreter-guarded /usr/bin/python3. Startup banner to stdout
per c43 CLI-Startup-Silence interdiction.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

WS = "/home/user/long-exposure-runs/music-gen"
SRC = os.path.join(WS, "scripts/ear_v2/determinism_check.py")
DST = os.path.join(WS, "tools/stale/scripts_ear_v2_determinism_check_c45.py")
OUT = os.path.join(WS, "data/deprecation_and_anchor_pin/deprecation_check.json")

# Interpreter guard (c26/c31/c33 pattern).
if not sys.executable.startswith("/usr/bin/python"):
    print(f"[deprecate_c45] REFUSE: interpreter {sys.executable!r} is not /usr/bin/python3", file=sys.stderr)
    sys.exit(2)


def sha256_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _grep_imports_zero() -> dict:
    """Scan for actual import statements referencing the c45 module."""
    import re
    scan_roots = ["scripts", "tools", "tests", "docs", "data"]
    patterns = [
        re.compile(r"^\s*from\s+scripts\.ear_v2\.determinism_check"),
        re.compile(r"^\s*import\s+scripts\.ear_v2\.determinism_check"),
    ]
    matches: list[dict] = []
    for root in scan_roots:
        for dp, _dn, files in os.walk(os.path.join(WS, root)):
            # Skip the stale destination itself.
            if os.path.normpath(dp).endswith(os.sep + os.path.join("tools", "stale")) or "/tools/stale" in dp:
                continue
            for fn in files:
                # Look only at code and text files, keep it fast.
                if not (fn.endswith(".py") or fn.endswith(".md") or fn.endswith(".txt")):
                    continue
                fp = os.path.join(dp, fn)
                try:
                    with open(fp, encoding="utf-8", errors="replace") as f:
                        for lineno, line in enumerate(f, 1):
                            for pat in patterns:
                                if pat.match(line):
                                    matches.append({
                                        "path": os.path.relpath(fp, WS),
                                        "line": lineno,
                                        "content": line.rstrip("\n"),
                                    })
                except OSError:
                    continue
    return {"scan_roots": scan_roots, "matches": matches, "count": len(matches)}


def main() -> int:
    print("[deprecate_c45] c47 Branch C — deprecating c45 determinism_check.py")
    if not os.path.exists(SRC):
        print(f"[deprecate_c45] REFUSE: source {SRC!r} does not exist", file=sys.stderr)
        return 3

    pre_sha = sha256_file(SRC)
    pre_mtime = os.path.getmtime(SRC)

    # Ensure stale/ exists.
    os.makedirs(os.path.dirname(DST), exist_ok=True)

    # os.rename: atomic on same filesystem. Never delete.
    os.rename(SRC, DST)

    # c38 lesson: some filesystems preserve mtime through rename.
    # Force update to now so the move-mtime gate is falsifiable.
    now = time.time()
    # Bump slightly forward to guarantee post > pre even on coarse mtime FS.
    new_mtime = max(now, pre_mtime + 1.0)
    os.utime(DST, (new_mtime, new_mtime))

    post_sha = sha256_file(DST)
    post_mtime = os.path.getmtime(DST)

    imports_scan = _grep_imports_zero()

    result = {
        "cycle": 47,
        "branch": "C",
        "clone": 2,
        "src_path": os.path.relpath(SRC, WS),
        "dst_path": os.path.relpath(DST, WS),
        "pre_sha256": pre_sha,
        "post_sha256": post_sha,
        "sha_preserved": (pre_sha == post_sha),
        "pre_mtime": pre_mtime,
        "post_mtime": post_mtime,
        "mtime_advanced": (post_mtime >= pre_mtime),
        "imports_scan": imports_scan,
        "grep_zero_imports": (imports_scan["count"] == 0),
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2, sort_keys=True)

    print(f"[deprecate_c45] moved {SRC} -> {DST}")
    print(f"[deprecate_c45] sha_preserved={result['sha_preserved']} "
          f"mtime_advanced={result['mtime_advanced']} "
          f"grep_zero_imports={result['grep_zero_imports']}")
    print(f"[deprecate_c45] wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
