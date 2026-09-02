#!/usr/bin/env python3
"""c20 clone-0: D2 vocals overlay from WIG operator-section htdemucs vocals stem (sibling of c5)."""
from __future__ import annotations
import hashlib
import json
import shutil
from pathlib import Path

SEC = Path("data/v3_spine/252eb21ce7df7328/operator_section")
SRC = SEC / "rc9_6stem" / "vocals.wav"
DST_DIR = SEC / "render"
DST = DST_DIR / "vocals_htdemucs.wav"


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    DST_DIR.mkdir(parents=True, exist_ok=True)
    s = sha(SRC)
    shutil.copy2(SRC, DST)
    assert sha(DST) == s
    (DST_DIR / "vocals_overlay.json").write_text(json.dumps({
        "cycle": 20, "clone": "0", "song_sha16": "252eb21ce7df7328",
        "src": str(SRC), "sha256": s, "dst": str(DST),
        "note": "operator-section htdemucs_6s vocals stem",
    }, indent=2, sort_keys=True) + "\n")
    print(f"vocals overlay sha={s[:16]}")


if __name__ == "__main__":
    main()
