#!/usr/bin/env /usr/bin/python3
"""c20 clone-2: D2 vocals overlay — SHA-verified htdemucs vocals copy."""
from __future__ import annotations
import hashlib
import json
import shutil
from pathlib import Path

SEC = Path("data/v3_spine/88d247468cb6d49f/chosen_section")
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
        "cycle": 20, "clone": "clone-2", "song_sha16": "88d247468cb6d49f",
        "src": str(SRC), "sha256": s, "dst": str(DST),
        "note": "chosen-section htdemucs_6s vocals stem (Peach Dream)",
    }, indent=2, sort_keys=True) + "\n")
    print(f"vocals overlay sha={s[:16]}")


if __name__ == "__main__":
    main()
