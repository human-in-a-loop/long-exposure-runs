#!/usr/bin/env python3
# c41 harmonic-window-refinement — one-shot orchestrator.
#
# Steps:
#   1. anchor snapshot (pre)
#   2. grid_runner canonical pass into data/rules_harmonic_window_v2/
#   3. aggregate + verdict (writes verdict.json, per_cell_summary.tsv, grid_summary.tsv,
#      and peer shard on LANDS)
#   4. determinism_check.py (two independent fresh-dir runs, SHA equality)
#   5. anchor snapshot (post) + compare
#
# NO PRNG. Interpreter-guarded. No sidecar_nonfactor imports.

import subprocess
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent


def _run(cmd):
    print(f">>> {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, cwd=str(REPO))


def main() -> int:
    manifest_p = REPO / "data" / "rules_rated_corpus" / "song_manifest.json"
    out_dir = REPO / "data" / "rules_harmonic_window_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    rubric_hash_p = out_dir / "rubric_hash.txt"

    pre_p = out_dir / "_anchor_pre.json"
    post_p = out_dir / "_anchor_post.json"
    ap_report_p = out_dir / "anchor_preservation.json"
    det_p = out_dir / "determinism_check.json"

    py = "/usr/bin/python3"
    _run([py, "-m", "scripts.rules_harmonic_window_v2.anchor_preservation",
          "snapshot", str(pre_p)])
    _run([py, "-m", "scripts.rules_harmonic_window_v2.grid_runner",
          str(manifest_p), str(out_dir)])
    _run([py, "-m", "scripts.rules_harmonic_window_v2.aggregate_and_verdict",
          str(out_dir), str(manifest_p), str(rubric_hash_p)])
    _run([py, "-m", "scripts.rules_harmonic_window_v2.determinism_check",
          str(manifest_p), str(det_p)])
    _run([py, "-m", "scripts.rules_harmonic_window_v2.anchor_preservation",
          "snapshot", str(post_p)])
    _run([py, "-m", "scripts.rules_harmonic_window_v2.anchor_preservation",
          "compare", str(pre_p), str(post_p), str(ap_report_p)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
