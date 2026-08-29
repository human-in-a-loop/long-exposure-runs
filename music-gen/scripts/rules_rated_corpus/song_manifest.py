#!/usr/bin/env python3
# M-RULES-1/extraction/rated-corpus — song enumeration (43 songs).
#
# Author: cyd7bevdr@mozmail.com, cycle 40 (fork c320de981fda / clone-0).
#
# Unifies c37 (1 song), c38 clone-2 (5 songs), c39 clone-0 (37 songs) into
# a single 43-row manifest ordered by SHA-256 tiebreak (ascending) over the
# source-audio file_sha256 (as recorded in each cycle's chosen_songs manifest).
#
# Read-only reads of manifest files under data/{recreate_v0, recreate_v0_batch,
# recreate_v0_full_corpus}. NO PRNG. Interpreter-guarded.

import json
import sys
from pathlib import Path
from typing import Dict, List

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent  # rules_rated_corpus -> scripts -> repo


def _c37_song() -> Dict:
    """Return the 1 song from c37 clone-0."""
    v = json.loads((REPO / "data/recreate_v0/verdict.json").read_text())
    cs = v["chosen_song"]
    return {
        "song_id": cs["chosen_sha256"],
        "band": cs["chosen_rating_band"],
        "relpath": cs["chosen_relpath"],
        "source": "c37",
        "merged_musicxml": str(REPO / "data/recreate_v0/per_stage/06_score/merged.musicxml"),
        "bp_dir": str(REPO / "data/recreate_v0/per_stage/05_basic_pitch"),
    }


def _c38_songs() -> List[Dict]:
    """Return the 5 songs from c38 clone-2."""
    d = json.loads((REPO / "data/recreate_v0_batch/chosen_songs.json").read_text())
    out = []
    for s in d["chosen_songs"]:
        sha = s["sha256"]
        band = s["band"]
        # c38 per_song dir uses first-16 hex of sha
        sd = REPO / f"data/recreate_v0_batch/per_song/{band}/{sha[:16]}"
        out.append({
            "song_id": sha,
            "band": band,
            "relpath": s["relpath"],
            "source": "c38",
            "merged_musicxml": str(sd / "per_stage/06_score/merged.musicxml"),
            "bp_dir": str(sd / "per_stage/05_basic_pitch"),
        })
    return out


def _c39_songs() -> List[Dict]:
    """Return the 37 songs from c39 clone-0."""
    d = json.loads((REPO / "data/recreate_v0_full_corpus/chosen_songs_full.json").read_text())
    out = []
    for s in d["chosen_songs"]:
        sha = s["file_sha256"]
        band = s["rating_bucket"]
        sd = REPO / f"data/recreate_v0_full_corpus/per_song/{band}/{sha[:16]}"
        out.append({
            "song_id": sha,
            "band": band,
            "relpath": s["relpath"],
            "source": "c39",
            "merged_musicxml": str(sd / "per_stage/06_score/merged.musicxml"),
            "bp_dir": str(sd / "per_stage/05_basic_pitch"),
        })
    return out


def enumerate_43() -> List[Dict]:
    """Return all 43 songs ordered by song_id ascending (SHA-256 tiebreak)."""
    all_songs = [_c37_song()] + _c38_songs() + _c39_songs()
    assert len(all_songs) == 43, f"expected 43, got {len(all_songs)}"
    # SHA-256 tiebreak: sort by song_id ascending.
    all_songs.sort(key=lambda s: s["song_id"])
    # Assign canonical_index in sorted order.
    for i, s in enumerate(all_songs):
        s["canonical_index"] = i
    return all_songs


def verify_exists(songs: List[Dict]) -> List[Dict]:
    """Return the subset whose merged_musicxml + 3 bp jsonls exist."""
    ok = []
    for s in songs:
        mxml = Path(s["merged_musicxml"])
        bp = Path(s["bp_dir"])
        stems_ok = all((bp / f"{x}.jsonl").exists() for x in ("drums", "bass", "other"))
        if mxml.exists() and stems_ok:
            ok.append(s)
        else:
            s["missing"] = True
            ok.append(s)  # keep in manifest, but mark
    return ok


def main() -> int:
    songs = verify_exists(enumerate_43())
    out_dir = REPO / "data/rules_rated_corpus"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "song_manifest.json"
    manifest = {
        "n_songs": len(songs),
        "tiebreak_rule": "sha256_ascending_over_source_audio_file_sha256",
        "sources": {"c37": 1, "c38": 5, "c39": 37},
        "songs": songs,
    }
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    n_missing = sum(1 for s in songs if s.get("missing"))
    print(f"wrote {out}: {len(songs)} songs ({n_missing} missing on disk)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
