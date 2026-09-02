#!/usr/bin/env python3
"""c5 Track B: D2 vocals overlay from operator-section htdemucs vocals stem."""
from __future__ import annotations
import hashlib
import json
import shutil
from pathlib import Path

SEC = Path("data/v3_spine/31a164f845f8e27e/operator_section")
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
        "cycle": 5, "src": str(SRC), "sha256": s, "dst": str(DST),
        "note": "operator-section htdemucs_6s vocals stem (NOT c49 baseline)",
    }, indent=2, sort_keys=True) + "\n")
    print(f"vocals overlay sha={s[:16]}")


if __name__ == "__main__":
    main()
