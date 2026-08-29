#!/usr/bin/env python3
# c41 harmonic-window-refinement — byte-determinism × 2 check.
#
# Two independent full-grid runs in fresh tempfile.mkdtemp() dirs;
# SHA-256 equality across all per-cell shards + aggregate.
#
# NO PRNG. Interpreter-guarded. No sidecar_nonfactor imports.

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _run_grid(manifest_p: Path, out_dir: Path) -> None:
    cmd = ["/usr/bin/python3", "-m", "scripts.rules_harmonic_window_v2.grid_runner",
           str(manifest_p), str(out_dir)]
    subprocess.run(cmd, check=True, cwd=str(REPO))


def _collect_shard_shas(out_dir: Path) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for shard in sorted(out_dir.rglob("rules_shard.jsonl")):
        rel = str(shard.relative_to(out_dir))
        result[rel] = _sha(shard)
    return result


def determinism_check(manifest_p: Path) -> Dict:
    run1_dir = Path(tempfile.mkdtemp(prefix="c41_det_run1_"))
    run2_dir = Path(tempfile.mkdtemp(prefix="c41_det_run2_"))
    _run_grid(manifest_p, run1_dir)
    _run_grid(manifest_p, run2_dir)
    shas1 = _collect_shard_shas(run1_dir)
    shas2 = _collect_shard_shas(run2_dir)
    mismatched: List[str] = []
    all_paths = sorted(set(shas1) | set(shas2))
    for p in all_paths:
        if shas1.get(p) != shas2.get(p):
            mismatched.append(p)
    result = {
        "n_shards_run1": len(shas1),
        "n_shards_run2": len(shas2),
        "n_paths_checked": len(all_paths),
        "n_mismatched": len(mismatched),
        "mismatched_sample": mismatched[:5],
        "pass": len(mismatched) == 0 and shas1 == shas2,
        "run1_dir": str(run1_dir),
        "run2_dir": str(run2_dir),
    }
    return result


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: determinism_check.py <song_manifest.json> <output_json>",
              file=sys.stderr)
        return 2
    manifest_p = Path(sys.argv[1])
    output_p = Path(sys.argv[2])
    result = determinism_check(manifest_p)
    output_p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"determinism_check: pass={result['pass']} n_shards={result['n_shards_run1']}")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
