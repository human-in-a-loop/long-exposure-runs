#!/usr/bin/python3
"""v6 Phase 0 — corpus manifest for the 29-song bands-4/5/7 corpus (v5-consumer compatible).

created: 2026-10-04
milestone: M-V6-DATA-0/corpus-manifest-v6

Replaces scripts/v5/corpus_manifest.py (which keeps only bands 6/7 + five hard-coded focus shas, three of which are
absent after the container wipe). Enumerates every song in corpus/ratings/ingest_receipts.jsonl (29 rows: 9 band-4,
16 band-5, 4 band-7), re-hashes the mp3 bytes (receipt sha256 is verified, not trusted), probes duration with ffprobe
(as v5 did), and emits the SAME per-song keys the v5 consumers read unchanged:

    sha16, audio_sha256, audio_path, duration_s, band, title, video_id, manifest_duration_s, is_focus_song,
    focus_name, is_v4_ear_exemplar, asset_inventory, in_v5_corpus (true for all), v5_tier, v5_priority_rank

v5_tier in {focus, band7, band5, band4}; priority = focus songs (WIG, Rome, Disco A) first, then band 7, 5, 4 by
playlist position (deterministic, no PRNG, no SHA tiebreak needed: (band, position) is unique per receipt).
Writes data/v5/corpus/corpus_manifest.json (the path every v5 script reads) AND a byte-identical copy at
data/v6/corpus/corpus_manifest_v6.json. A "summary" block carries band / tier counts and total duration.

Discipline: /usr/bin/python3 guard (suppressible); env pins; sorted-key atomic JSON; no PRNG; corpus READ-ONLY.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.v6_data_common import (  # noqa: E402
    BAND_ORDER, ENV_PIN_SHA256, EXEMPLARS, FOCUS, FOCUS_ABSENT, FOCUS_ORDER, MANIFEST_V5, MANIFEST_V6, RATINGS_TSV,
    RECEIPTS, WS, canonical_json, interpreter_guard, pin_env, read_ratings_tsv, read_receipts, sha256_file,
    write_text_atomic)

pin_env()
interpreter_guard()

SCHEMA_VERSION = 2  # v5 manifest was 1; same per-song keys, new top-level summary / provenance blocks
EXPECTED_BANDS = {4: 9, 5: 16, 7: 4}


def duration_s(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return round(float(r.stdout.strip()), 3)


def tier_of(sha16: str, band: int) -> str:
    return "focus" if sha16 in FOCUS else f"band{band}"


def sort_key(song: dict):
    if song["is_focus_song"]:
        return (0, FOCUS_ORDER.index(song["sha16"]), 0)
    return (1 + BAND_ORDER.index(song["band"]), song["position"], 0)


def build_manifest(ws: Path = WS, receipts_path: Path = RECEIPTS, ratings_path: Path = RATINGS_TSV,
                   verify_sha: bool = True, probe_duration: bool = True) -> dict:
    receipts = read_receipts(receipts_path)
    by_vid = read_ratings_tsv(ratings_path) if ratings_path.exists() else {}
    songs: dict[str, dict] = {}
    sha_mismatch = []
    for r in receipts:
        rel = r["path"]
        mp3 = ws / rel
        if not mp3.exists():
            raise FileNotFoundError(f"receipt path missing on disk: {rel}")
        full = sha256_file(mp3) if verify_sha else r["sha256"]
        if full != r["sha256"]:
            sha_mismatch.append({"path": rel, "receipt_sha256": r["sha256"], "disk_sha256": full})
        sha16 = full[:16]
        vid = r.get("video_id")
        mrow = by_vid.get(vid) if vid and not str(vid).startswith("LOCAL") else None
        dur = duration_s(mp3) if probe_duration else float(r["duration_s"])
        songs[sha16] = {
            "sha16": sha16, "audio_sha256": full, "audio_path": rel, "duration_s": dur,
            "band": int(r["band"]), "position": int(r["position"]), "title": r.get("title"),
            "video_id": vid, "manifest_duration_s": float(mrow["duration_s"]) if mrow else float(r.get("manifest_duration_s") or 0) or None,
            "receipt_duration_s": float(r["duration_s"]), "receipt_sha256": r["sha256"],
            "is_focus_song": sha16 in FOCUS, "focus_name": FOCUS[sha16]["name"] if sha16 in FOCUS else None,
            "is_v4_ear_exemplar": sha16 in EXEMPLARS,
            "asset_inventory": {"full_length_stems_present": False, "full_length_stem_dirs": [],
                                "operator_section_stem_dirs": [], "existing_muscriptor_json": [],
                                "existing_muscriptor_json_full_length": [], "tempo_anchors": {},
                                "note": "container wipe of data/: no prior assets exist; everything is recomputed in v6"},
        }
    if sha_mismatch:
        raise RuntimeError(f"receipt sha256 mismatch on disk: {sha_mismatch}")
    ordered = sorted(songs.values(), key=sort_key)
    for rank, s in enumerate(ordered, 1):
        s["in_v5_corpus"] = True
        s["v5_tier"] = tier_of(s["sha16"], s["band"])
        s["v6_tier"] = s["v5_tier"]
        s["v5_priority_rank"] = rank
    band_counts = {str(b): sum(1 for s in ordered if s["band"] == b) for b in sorted({s["band"] for s in ordered})}
    tier_counts = {t: sum(1 for s in ordered if s["v5_tier"] == t) for t in sorted({s["v5_tier"] for s in ordered})}
    total = round(sum(s["duration_s"] for s in ordered), 3)
    focus_present = {k: v["name"] for k, v in FOCUS.items() if k in songs}
    out = {
        "schema_version": SCHEMA_VERSION,
        "generator": "scripts/v6/corpus_manifest_v6.py",
        "milestone": "M-V6-DATA-0/corpus-manifest-v6",
        "env_pin_sha256": ENV_PIN_SHA256,
        "sources": {"receipts": str(receipts_path.relative_to(ws)) if receipts_path.is_relative_to(ws) else str(receipts_path),
                    "receipts_sha256": sha256_file(receipts_path),
                    "ratings_manifest": str(ratings_path.relative_to(ws)) if ratings_path.exists() and ratings_path.is_relative_to(ws) else None,
                    "ratings_manifest_sha256": sha256_file(ratings_path) if ratings_path.exists() else None},
        "policy": {"included_bands": sorted(EXPECTED_BANDS), "in_v5_corpus": "all songs",
                   "priority": "focus (WIG, Rome, Disco A) -> band 7 -> band 5 -> band 4; within a band by playlist position",
                   "tiers": ["focus", "band7", "band5", "band4"], "prng": "none"},
        "summary": {"n_songs": len(ordered), "band_counts": band_counts, "tier_counts": tier_counts,
                    "total_duration_s": total, "total_duration_hms": _hms(total),
                    "mean_duration_s": round(total / len(ordered), 3) if ordered else None,
                    "focus_present": focus_present, "focus_absent": dict(FOCUS_ABSENT),
                    "expected_band_counts": {str(k): v for k, v in EXPECTED_BANDS.items()},
                    "band_counts_match_expected": band_counts == {str(k): v for k, v in EXPECTED_BANDS.items()}},
        "v5_compat_note": ("per-song keys mirror scripts/v5/corpus_manifest.py so transcribe_full_length.py, harmony_v5.py, "
                           "groove_v5_full_c84.py, velocity_v5.py, generate_v5.py read this file unchanged; v5_tier values "
                           "differ (focus/band7/band5/band4 instead of focus/exemplar/band7_extra/band6_extra) — no v5 "
                           "consumer branches on v5_tier"),
        "songs": ordered,
    }
    return out


def _hms(sec: float) -> str:
    s = int(round(sec))
    return f"{s // 3600:d}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 corpus manifest (29 songs, bands 4/5/7, v5-compatible keys)")
    ap.add_argument("--out-v5", default=str(MANIFEST_V5))
    ap.add_argument("--out-v6", default=str(MANIFEST_V6))
    ap.add_argument("--receipts", default=str(RECEIPTS))
    ap.add_argument("--ratings", default=str(RATINGS_TSV))
    ap.add_argument("--no-verify-sha", action="store_true", help="trust receipt sha256 (tests only)")
    args = ap.parse_args(argv)
    man = build_manifest(WS, Path(args.receipts), Path(args.ratings), verify_sha=not args.no_verify_sha)
    txt = canonical_json(man)
    changed = [write_text_atomic(Path(args.out_v5), txt), write_text_atomic(Path(args.out_v6), txt)]
    sm = man["summary"]
    print(f"manifest: {sm['n_songs']} songs bands={sm['band_counts']} tiers={sm['tier_counts']} total={sm['total_duration_hms']} "
          f"focus_present={sorted(sm['focus_present'].values())} sha256={__import__('hashlib').sha256(txt.encode()).hexdigest()[:16]}")
    print(f"wrote {args.out_v5} ({'changed' if changed[0] else 'unchanged'}); {args.out_v6} ({'changed' if changed[1] else 'unchanged'})")
    for s in man["songs"]:
        print(f"  {s['v5_priority_rank']:2d} {s['sha16']} band={s['band']} pos={s['position']:2d} {s['v5_tier']:6s} {s['duration_s']:7.2f}s {str(s['title'])[:48]}")
    if not sm["band_counts_match_expected"]:
        print(f"WARNING: band counts {sm['band_counts']} != expected {sm['expected_band_counts']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
