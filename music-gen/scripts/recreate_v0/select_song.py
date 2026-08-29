#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T08:00:00Z
# cycle: 37
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/first-real-audio
# fork: 675abd086911
# clone: 0
# ---
"""SHA-256 tiebreak song selector for M-RECREATE-1/first-real-audio.

Enumerate every `corpus/ratings/{4,5,6,7}/*.mp3` file in canonical
sort order, compute SHA-256 of each file's bytes, pick the file whose
hash is lexicographically smallest. Deterministic, PRNG-free.

Writes `data/recreate_v0/chosen_song.json`.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

# Do NOT import scripts.classifier.sidecar_nonfactor — non-factor isolation contract.

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_ROOT = REPO_ROOT / "corpus" / "ratings"
BANDS = ("4", "5", "6", "7")


def enumerate_candidates() -> list[tuple[str, Path]]:
    """Return [(relpath_from_repo, absolute_path), ...] sorted by relpath."""
    out: list[tuple[str, Path]] = []
    for band in BANDS:
        band_dir = CORPUS_ROOT / band
        if not band_dir.is_dir():
            continue
        for mp3 in sorted(band_dir.glob("*.mp3")):
            rel = str(mp3.relative_to(REPO_ROOT))
            out.append((rel, mp3))
    out.sort(key=lambda t: t[0])
    return out


def sha256_bytes(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def choose_song() -> dict:
    candidates = enumerate_candidates()
    if not candidates:
        raise RuntimeError("no candidates under corpus/ratings/{4,5,6,7}/*.mp3")
    ranked: list[tuple[str, str, int, str]] = []
    for rel, abspath in candidates:
        band = abspath.parent.name
        h = sha256_bytes(abspath)
        ranked.append((h, rel, abspath.stat().st_size, band))
    ranked.sort(key=lambda t: t[0])
    winner_hash, winner_rel, winner_size, winner_band = ranked[0]
    return {
        "chosen_relpath": winner_rel,
        "chosen_sha256": winner_hash,
        "chosen_bytes": winner_size,
        "chosen_rating_band": int(winner_band),
        "n_candidates": len(candidates),
        "top5_ranked_sha256_ascending": [
            {"sha256": h, "relpath": r, "bytes": s, "band": int(b)}
            for (h, r, s, b) in ranked[:5]
        ],
        "selection_rule": "sha256_tiebreak_over_corpus_ratings_bands_4_5_6_7",
        "rubric_hash": "78c61c5dbf61492ff802d7a0810b4c449b2732b658daffffa84c7b4203c2dab9",
        "trim_seconds": 30.0,
    }


def main() -> int:
    out_path = REPO_ROOT / "data" / "recreate_v0" / "chosen_song.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    choice = choose_song()
    out_path.write_text(json.dumps(choice, indent=2, sort_keys=True) + "\n")
    print(json.dumps(choice, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
