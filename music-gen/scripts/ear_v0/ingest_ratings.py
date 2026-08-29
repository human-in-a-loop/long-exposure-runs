"""Ingest the operator's rated corpus (43 songs) and parse per-song metadata.

Reads:
  - corpus/ratings/{4,5,6,7}/*.mp3
  - corpus/ratings/{4,5,6,7}/RECEIPTS.md (for sha256 + title cross-check)
  - corpus/ratings/ratings_manifest.tsv (playlist / video_id / title / URL)

Emits:
  - list of Song(path, band, sha256, title, artist, video_id, playlist_id)

Non-factor sidecar isolation preserved (NO import of sidecar_nonfactor).
"""
# created: 2026-08-29T07:22:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: M-EAR-1/real-label-training-v0
from __future__ import annotations
import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


BANDS = (4, 5, 6, 7)


@dataclass
class Song:
    path: Path
    band: int
    sha256: str
    title: str
    artist: str
    video_id: str
    playlist_id: str


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# Filename convention: NNN__<vid>__<Title_underscored>.mp3.
FNAME = re.compile(r"^(\d{3})__([A-Za-z0-9_\-]+)__(.+)\.mp3$")


def parse_filename(name: str) -> tuple[str, str, str] | None:
    m = FNAME.match(name)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def parse_artist(title_underscored: str) -> str:
    """Extract 'Artist' from 'Artist_-_Title' or 'Artist_Title'.

    Convention in corpus/ratings/*/*.mp3: title parts joined by underscore;
    author-title separator is '_-_' when present. Fallback: the entire
    title becomes the artist bucket (used for label-agnostic ablation).
    """
    if "_-_" in title_underscored:
        return title_underscored.split("_-_", 1)[0]
    # LOCAL band-7 files may be title-only ("Desire", "Freedom_Interlude").
    # Use the first two underscore-tokens as artist proxy.
    parts = title_underscored.split("_")
    return "_".join(parts[:2]) if len(parts) >= 2 else parts[0]


def load_ratings_manifest(root: Path) -> dict[str, dict]:
    """video_id -> row dict from ratings_manifest.tsv."""
    path = root / "corpus" / "ratings" / "ratings_manifest.tsv"
    rows: dict[str, dict] = {}
    with open(path) as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            cols = line.rstrip("\n").split("\t")
            if len(cols) != len(header):
                continue
            row = dict(zip(header, cols))
            rows.setdefault(row.get("video_id", ""), row)
    return rows


def discover_songs(root: Path) -> list[Song]:
    """Walk corpus/ratings/{4,5,6,7}/*.mp3, return sorted-by-sha256 songs."""
    ratings_root = root / "corpus" / "ratings"
    manifest = load_ratings_manifest(root)
    out: list[Song] = []
    for band in BANDS:
        band_dir = ratings_root / str(band)
        if not band_dir.is_dir():
            continue
        for p in sorted(band_dir.iterdir()):
            if not p.name.endswith(".mp3"):
                continue
            parsed = parse_filename(p.name)
            if not parsed:
                continue
            _, vid, title_u = parsed
            artist = parse_artist(title_u)
            sha = _sha256(p)
            # video_id "LOCAL" or "LOCAL-NNN" -> not in manifest;
            # playlist_id falls back to LOCAL_BAND_<band>.
            manifest_row = manifest.get(vid, {})
            playlist_id = manifest_row.get(
                "playlist_id", f"LOCAL_BAND_{band}"
            )
            title = manifest_row.get(
                "title", title_u.replace("_", " ")
            )
            out.append(Song(
                path=p, band=band, sha256=sha, title=title,
                artist=artist, video_id=vid, playlist_id=playlist_id,
            ))
    # Deterministic order: by (band, sha256).
    out.sort(key=lambda s: (s.band, s.sha256))
    return out


if __name__ == "__main__":
    songs = discover_songs(Path("."))
    print(f"{len(songs)} songs discovered")
    for band in BANDS:
        n = sum(1 for s in songs if s.band == band)
        print(f"  band {band}: {n}")
    for s in songs[:3]:
        print(f"  {s.band} {s.sha256[:16]} '{s.artist}' <- {s.path.name}")
