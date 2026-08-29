"""§1 regeneration-determinism close (auditor MODERATE #1, c36 clone-0).

Forces re-extraction of one already-cached song into an isolated temp
CACHE_DIR, then compares SHA-256 of the fresh .npy against the on-disk
cached copy. Does NOT touch the main cache or interfere with the running
extractor.
"""
# created: 2026-08-29T06:20:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: M-EAR-1/real-label-training-v0
from __future__ import annotations
import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import hashlib
import tempfile
from pathlib import Path

import numpy as np

from scripts.ear_v0 import extract_features_v0 as ef
from scripts.ear_v0.ingest_ratings import discover_songs

TARGET_SHA = "069ebba269efccc273ce9651912b0f0aaf91564a34d677e49efb860166585048"


def main() -> int:
    songs = discover_songs(Path("."))
    target = next((s for s in songs if s.sha256 == TARGET_SHA), None)
    if target is None:
        print(f"ERROR: target sha {TARGET_SHA[:16]} not in discover_songs")
        return 1

    orig_cache = Path("data/ear_v0/per_song_features") / f"{TARGET_SHA}.npy"
    if not orig_cache.exists():
        print(f"ERROR: original cache missing at {orig_cache}")
        return 1

    v_orig = np.load(orig_cache).astype(np.float32).reshape(-1)
    sha_a = hashlib.sha256(v_orig.tobytes()).hexdigest()
    file_sha_a = hashlib.sha256(orig_cache.read_bytes()).hexdigest()
    print(f"target: {target.artist} band={target.band} path={target.path}")
    print(f"vector SHA_A (raw float32 bytes): {sha_a}")
    print(f"file   SHA_A (.npy bytes)      : {file_sha_a}")

    # Isolated temp cache dir; monkey-patch CACHE_DIR to force fresh write.
    tmp = tempfile.mkdtemp(prefix="regen_det_")
    ef.CACHE_DIR = Path(tmp)
    print(f"regen tempdir: {tmp}")

    v_new = ef.extract_song(target)
    fresh = Path(tmp) / f"{TARGET_SHA}.npy"
    sha_b = hashlib.sha256(v_new.tobytes()).hexdigest()
    file_sha_b = hashlib.sha256(fresh.read_bytes()).hexdigest()
    print(f"vector SHA_B (raw float32 bytes): {sha_b}")
    print(f"file   SHA_B (.npy bytes)      : {file_sha_b}")

    equal_vec = (sha_a == sha_b)
    equal_file = (file_sha_a == file_sha_b)
    print(f"VECTOR EQUAL: {equal_vec}")
    print(f"FILE EQUAL  : {equal_file}")

    if not equal_vec:
        # Diagnose diff
        diff = np.where(v_orig != v_new)[0]
        print(f"first differing indices: {diff[:20].tolist()}")
        if len(diff) > 0:
            i = int(diff[0])
            print(f"  index {i}: orig={v_orig[i]!r} new={v_new[i]!r} "
                  f"delta={float(v_new[i] - v_orig[i])!r}")
        max_abs = float(np.abs(v_orig - v_new).max())
        print(f"max abs delta: {max_abs}")
    return 0 if equal_vec else 2


if __name__ == "__main__":
    sys.exit(main())
