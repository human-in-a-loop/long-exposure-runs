#!/usr/bin/python3
# ---
# created: 2026-08-29T12:15:00Z
# cycle: 39
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/full-corpus-recreation
# fork: c320de981fda
# clone: 0
# ---
"""SHA-256 tiebreak selector for the 37-song full-corpus batch.

Algorithm (deterministic, PRNG-free, no mtime/size):
  1. Enumerate `corpus/ratings/{4,5,6,7}/*.mp3` (43 files).
  2. Subtract the 6-song exclusion set (c37 clone-0's 1 + c38 clone-2's 5).
  3. Compute sha256 per remaining file.
  4. Sort ascending by SHA -> canonical processing order (37 entries).
  5. Write `data/recreate_v0_full_corpus/chosen_songs_full.json`.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_ROOT = REPO_ROOT / "corpus" / "ratings"
BANDS = ("4", "5", "6", "7")

# 6-song exclusion set: c37 clone-0 (1) + c38 clone-2 (5).
# Enumerated verbatim from rubric.
EXCLUSION_SET = frozenset({
    # c37 clone-0
    "corpus/ratings/7/016__LOCAL__05_02.mp3",
    # c38 clone-2 (5 songs; SHA-256-tiebreak per bucket plus band-6 second-lowest)
    "corpus/ratings/4/013__jZVdDl_asYY__Mariah_Carey_-_Shake_It_Off.mp3",
    "corpus/ratings/5/002__EvyTWRB4l4w__La_Rumba_Me_Llamo_Yo_-_Dayme_Arocena.mp3",
    "corpus/ratings/6/027__riDSMdAH5hk__Tom_Misch_-_Red_Moon.mp3",
    "corpus/ratings/6/001__iLF0ZNdhNM0__Justin_Bieber_-_YUKON_Live_Grammys_2026.mp3",
    "corpus/ratings/7/008__LOCAL__Oba_La_-_Vem_Ela.mp3",
})


def sha256_bytes(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def enumerate_remaining() -> list[dict]:
    """Return [{relpath, rating_bucket, file_sha256, mp3_bytes}, ...] over all
    non-excluded mp3s across bands 4/5/6/7."""
    out: list[dict] = []
    for band in BANDS:
        band_dir = CORPUS_ROOT / band
        if not band_dir.is_dir():
            continue
        for mp3 in sorted(band_dir.glob("*.mp3")):
            rel = str(mp3.relative_to(REPO_ROOT))
            if rel in EXCLUSION_SET:
                continue
            out.append({
                "relpath": rel,
                "rating_bucket": int(band),
                "file_sha256": sha256_bytes(mp3),
                "mp3_bytes": mp3.stat().st_size,
            })
    return out


def choose_37() -> dict:
    remaining = enumerate_remaining()
    # Canonical order: ascending sha256
    remaining.sort(key=lambda r: r["file_sha256"])
    for i, r in enumerate(remaining):
        r["canonical_index"] = i
    per_bucket_counts: dict = {}
    for r in remaining:
        per_bucket_counts[str(r["rating_bucket"])] = \
            per_bucket_counts.get(str(r["rating_bucket"]), 0) + 1
    rubric_hash = (REPO_ROOT / "data" / "recreate_v0_full_corpus"
                   / "rubric_hash.txt").read_text().strip()
    return {
        "selection_rule": "sha256_tiebreak_over_43_song_corpus_minus_6_song_exclusion",
        "exclusion_set": sorted(EXCLUSION_SET),
        "n_excluded": len(EXCLUSION_SET),
        "n_candidates_after_exclusion": len(remaining),
        "n_chosen": len(remaining),
        "per_bucket_counts": per_bucket_counts,
        "chosen_songs": remaining,
        "rubric_hash": rubric_hash,
        "trim_seconds": 30.0,
    }


def main() -> int:
    out_path = REPO_ROOT / "data" / "recreate_v0_full_corpus" / "chosen_songs_full.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    choice = choose_37()
    out_path.write_text(json.dumps(choice, indent=2, sort_keys=True) + "\n")
    print(f"selected n={choice['n_chosen']} songs across "
          f"bands={choice['per_bucket_counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
