#!/usr/bin/python3
"""Byte-determinism × 2 harness: run twice into fresh temp dirs, SHA-compare.

Usage:
    /usr/bin/python3 -m scripts.recreate_v2.musical_time.byte_determinism
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
from typing import Dict, List

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _sha_tree(root: pathlib.Path) -> Dict[str, str]:
    if not root.exists():
        return {}
    out: Dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root))] = _sha(p)
    return out


def run_once(out_dir: pathlib.Path) -> None:
    env = os.environ.copy()
    env.update({
        "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
        "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424",
        "TZ": "UTC", "LC_ALL": "C.UTF-8",
    })
    subprocess.run(
        ["/usr/bin/python3", "-m", "scripts.recreate_v2.musical_time.run_all",
         "--out-dir", str(out_dir)],
        cwd=str(REPO_ROOT), env=env, check=True,
        capture_output=True,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
        d1 = pathlib.Path(t1) / "run1"
        d2 = pathlib.Path(t2) / "run2"
        d1.mkdir(); d2.mkdir()
        # Seed rubric_hash.txt so run_all can consume it.
        rubric = REPO_ROOT / "docs/rc10_musical_time_rubric.md"
        rubric_hash = hashlib.sha256(rubric.read_bytes()).hexdigest()
        (d1 / "rubric_hash.txt").write_text(rubric_hash)
        (d2 / "rubric_hash.txt").write_text(rubric_hash)
        run_once(d1)
        run_once(d2)
        sha1 = _sha_tree(d1)
        sha2 = _sha_tree(d2)
        all_keys = sorted(set(sha1.keys()) | set(sha2.keys()))
        mismatches: List[str] = [k for k in all_keys if sha1.get(k) != sha2.get(k)]
        report = {
            "n_files_run1": len(sha1),
            "n_files_run2": len(sha2),
            "byte_determinism_holds": (not mismatches) and (sha1 == sha2),
            "n_mismatch": len(mismatches),
            "mismatch_files": mismatches,
            "env_pins": {
                "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0",
                "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
            },
        }
        out = REPO_ROOT / "data/rc10_musical_time/byte_determinism.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True))
        print(json.dumps({"holds": report["byte_determinism_holds"],
                          "n_mismatch": report["n_mismatch"]}))
        return 0 if report["byte_determinism_holds"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
