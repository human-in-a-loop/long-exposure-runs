#!/usr/bin/env python3
# M-RULES-1/extraction/rated-corpus — foreground driver.
#
# Author: cyd7bevdr@mozmail.com, cycle 40 (fork c320de981fda / clone-0).
#
# Orchestrates the full c40 pipeline in one foreground process:
#   1) song_manifest.py  (enumerate 43 songs)
#   2) anchor_preservation.py pre
#   3) extract_per_song.py  (all 43 songs into data/rules_rated_corpus/)
#   4) aggregate_and_append.py (peer shard data/rules/ledger_rated_corpus.jsonl)
#   5) determinism_check.py  (two fresh temp runs → SHA equality)
#   6) anchor_preservation.py compare
#   7) verdict.py
#
# Per-song idempotence: stage_manifest.json presence skips re-extraction.

import subprocess
import sys
import time
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent


def run(cmd, label):
    print(f"\n=== {label} ===")
    t0 = time.monotonic()
    r = subprocess.run(cmd, cwd=str(REPO))
    dt = time.monotonic() - t0
    print(f"  {label} rc={r.returncode} wall={dt:.1f}s")
    if r.returncode != 0:
        raise SystemExit(f"{label} failed rc={r.returncode}")


def main() -> int:
    out_dir = REPO / "data/rules_rated_corpus"
    manifest = out_dir / "song_manifest.json"
    shard = REPO / "data/rules/ledger_rated_corpus.jsonl"

    run(["/usr/bin/python3", str(_HERE / "song_manifest.py")], "song_manifest")
    run(["/usr/bin/python3", str(_HERE / "anchor_preservation.py"), "pre"],
        "anchor_pre")
    run(["/usr/bin/python3", str(_HERE / "extract_per_song.py"),
         str(manifest), str(out_dir)], "extract_per_song (43 songs)")
    run(["/usr/bin/python3", str(_HERE / "aggregate_and_append.py"),
         str(out_dir), str(shard)], "aggregate → peer shard")
    run(["/usr/bin/python3", str(_HERE / "determinism_check.py")],
        "determinism × 2")
    run(["/usr/bin/python3", str(_HERE / "anchor_preservation.py"), "compare"],
        "anchor_post_compare")
    run(["/usr/bin/python3", str(_HERE / "verdict.py")], "verdict")

    print("\n=== c40 pipeline complete ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
