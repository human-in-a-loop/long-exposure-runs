#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T10:36:00Z
# cycle: 38
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/second-real-audio-batch
# fork: 33a2a8003c84
# clone: 2
# ---
"""SHA-256 tiebreak per-bucket song selector for the 5-song batch.

Algorithm (deterministic, PRNG-free, no mtime/size):
  1. Enumerate `corpus/ratings/{4,5,6,7}/*.mp3`.
  2. Exclude `corpus/ratings/7/016__LOCAL__05_02.mp3` (c37 clone-0's).
  3. Compute sha256 per file.
  4. Group by band; per-bucket ascending sort by SHA.
  5. Pick lowest-SHA entry from each of bands 4, 5, 6, 7 (4 songs).
  6. 5th slot: band-6 SECOND-lowest SHA.

Writes `data/recreate_v0_batch/chosen_songs.json`.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_ROOT = REPO_ROOT / "corpus" / "ratings"
EXCLUDE_RELPATH = "corpus/ratings/7/016__LOCAL__05_02.mp3"
BANDS = ("4", "5", "6", "7")


def sha256_bytes(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def enumerate_by_band() -> dict:
    """Return {band_str: [(sha, relpath, bytes), ...] sorted by sha ascending}."""
    out: dict = {b: [] for b in BANDS}
    for band in BANDS:
        band_dir = CORPUS_ROOT / band
        if not band_dir.is_dir():
            continue
        for mp3 in sorted(band_dir.glob("*.mp3")):
            rel = str(mp3.relative_to(REPO_ROOT))
            if rel == EXCLUDE_RELPATH:
                continue
            h = sha256_bytes(mp3)
            out[band].append((h, rel, mp3.stat().st_size))
    for band in BANDS:
        out[band].sort(key=lambda t: t[0])
    return out


def choose_five() -> dict:
    grouped = enumerate_by_band()
    picks = []
    # 4 slots: per-band lowest sha
    for band in BANDS:
        if not grouped[band]:
            raise RuntimeError(f"band {band}: no candidates after exclusion")
        h, rel, sz = grouped[band][0]
        picks.append({
            "band": int(band),
            "slot_kind": "band_lowest_sha",
            "relpath": rel,
            "sha256": h,
            "bytes": sz,
        })
    # 5th slot: band-6 second-lowest sha
    if len(grouped["6"]) < 2:
        raise RuntimeError("band 6 has fewer than 2 candidates; cannot pick second-lowest")
    h, rel, sz = grouped["6"][1]
    picks.append({
        "band": 6,
        "slot_kind": "band_6_second_lowest_sha",
        "relpath": rel,
        "sha256": h,
        "bytes": sz,
    })
    rubric_hash = (REPO_ROOT / "data" / "recreate_v0_batch" / "rubric_hash.txt").read_text().strip()
    return {
        "selection_rule": "sha256_tiebreak_per_bucket_plus_band6_second_lowest",
        "excluded_relpath": EXCLUDE_RELPATH,
        "n_candidates_after_exclusion": sum(len(v) for v in grouped.values()),
        "n_chosen": len(picks),
        "chosen_songs": picks,
        "rubric_hash": rubric_hash,
        "trim_seconds": 30.0,
    }


def main() -> int:
    out_path = REPO_ROOT / "data" / "recreate_v0_batch" / "chosen_songs.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    choice = choose_five()
    out_path.write_text(json.dumps(choice, indent=2, sort_keys=True) + "\n")
    print(json.dumps(choice, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
