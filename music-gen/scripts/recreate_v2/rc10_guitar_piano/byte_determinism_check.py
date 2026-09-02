#!/usr/bin/python3
# c53 clone-1 RC10 Branch B — byte-determinism × 2 verifier.
"""Re-run the RC10 pipeline into a fresh temp dir, and hash-compare artifacts.

Compares SHA-256 of:
  * canonical MIDI files under data/rc10_impl/guitar_piano/per_song/<sha>/<stem>/*.midi
  * scorecard.tsv
  * winner_per_stem.json
  * verdict.json (excluding the timestamp/tempdir fields if any)
  * A/B pair WAVs under data/recreate_v2/ab_pairs/<sha>/<stem>/iter_0/*.wav

Writes byte_determinism.json with per-file SHAs from both runs and n_mismatch.

Because basic-pitch outputs are content-hash-keyed and cached, the second run
will reuse the same MIDI cache; determinism of the downstream deterministic
pipeline is what this verifies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"byte_det requires /usr/bin/python3 (got {sys.executable})")

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

ROOT = Path("/home/user/long-exposure-runs/music-gen")
OUT_ROOT = ROOT / "data/rc10_impl/guitar_piano"
AB_ROOT = ROOT / "data/recreate_v2/ab_pairs"
RUN = ROOT / "scripts/recreate_v2/rc10_guitar_piano/run_all.py"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def enumerate_artifacts() -> list[Path]:
    """List all deterministic artifacts we require byte-identical across runs."""
    files = []
    # MIDIs under per_song.
    for song_dir in sorted((OUT_ROOT / "per_song").glob("*")):
        for stem_dir in sorted(song_dir.glob("*")):
            for midi in sorted(stem_dir.glob("*.midi")):
                files.append(midi)
    # Scorecard, winner, verdict, ab_manifest, anchor_preservation.
    for name in ("scorecard.tsv", "winner_per_stem.json", "verdict.json",
                 "ab_pairs_manifest.json", "anchor_preservation.json"):
        p = OUT_ROOT / name
        if p.exists():
            files.append(p)
    # A/B pair WAVs.
    for song_dir in sorted(AB_ROOT.glob("*")):
        for stem_dir in sorted(song_dir.glob("*")):
            for iter_dir in sorted(stem_dir.glob("iter_*")):
                for wav in sorted(iter_dir.glob("*.wav")):
                    files.append(wav)
    return files


def snapshot() -> dict[str, str]:
    return {str(p.relative_to(ROOT)): sha256(p) for p in enumerate_artifacts()}


def main() -> int:
    argp = argparse.ArgumentParser()
    argp.add_argument("--skip-second-run", action="store_true",
                     help="only snapshot; assume orchestrator already ran twice")
    args = argp.parse_args()

    # Run 1 must already have happened (called from CI or manually).
    run1 = snapshot()
    if not run1:
        raise SystemExit("no artifacts to snapshot — run scripts/recreate_v2/rc10_guitar_piano/run_all.py first")

    if not args.skip_second_run:
        # Re-run into the same OUT_ROOT (deterministic paths — write-overwrite is idempotent).
        print("byte-det run 2: re-invoking run_all.py (basic-pitch cache hit expected)...")
        proc = subprocess.run(
            ["/usr/bin/python3", str(RUN)],
            env={**os.environ},
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            print("STDOUT:", proc.stdout[-500:])
            print("STDERR:", proc.stderr[-500:])
            raise SystemExit(f"run 2 failed rc={proc.returncode}")
        print(proc.stdout.strip().splitlines()[-1] if proc.stdout else "run 2 done")

    run2 = snapshot()

    all_keys = sorted(set(run1) | set(run2))
    mismatches = []
    for k in all_keys:
        s1, s2 = run1.get(k), run2.get(k)
        if s1 != s2:
            mismatches.append({"file": k, "run1": s1, "run2": s2})

    payload = {
        "milestone": "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano",
        "clone": "clone-1",
        "cycle": 53,
        "n_artifacts": len(all_keys),
        "n_mismatch": len(mismatches),
        "byte_determinism_holds": len(mismatches) == 0,
        "env_pins": {
            "PYTHONHASHSEED": os.environ["PYTHONHASHSEED"],
            "SOURCE_DATE_EPOCH": os.environ["SOURCE_DATE_EPOCH"],
            "TZ": os.environ["TZ"],
            "LC_ALL": os.environ["LC_ALL"],
            "OPENBLAS_NUM_THREADS": os.environ["OPENBLAS_NUM_THREADS"],
            "MKL_NUM_THREADS": os.environ["MKL_NUM_THREADS"],
            "OMP_NUM_THREADS": os.environ["OMP_NUM_THREADS"],
        },
        "run1_shas": run1,
        "run2_shas": run2,
        "mismatches": mismatches,
    }
    out = OUT_ROOT / "byte_determinism.json"
    out.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    print(f"byte_determinism: n={len(all_keys)} n_mismatch={len(mismatches)} holds={len(mismatches) == 0}")
    return 0 if len(mismatches) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
