#!/usr/bin/python3
"""c79 P1 — v5 corpus manifest.

created: 2026-09-06T00:00:00Z
cycle: 79
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/corpus-manifest-emitted-c79

Enumerates every band-6/7 song from the corpus receipts
(`corpus/ratings/{6,7}/*.mp3` + `corpus/ratings/ratings_manifest.tsv`) plus
the five operator-approved focus songs (three of which — WIG, Rome, Disco A —
live in band 5, not band 6/7; disclosed per invariant (d)). Marks the v5
corpus, assigns a deterministic priority order (SHA-256 tiebreak, no PRNG),
and inventories existing full-length assets per song.

Output: data/v5/corpus/corpus_manifest.json (canonical JSON, sort_keys,
byte-deterministic x2).

Discipline: /usr/bin/python3 interpreter guard; no PRNG; no sidecar_nonfactor;
no VST3 state APIs; reads corpus + prior artifacts READ-ONLY.
"""
from __future__ import annotations

import csv
import glob
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)

FOCUS = {  # operator-approved five focus songs (v3 M-V3-FOCUS-1 + v4 M-V4-PROFILES-1)
    "31a164f845f8e27e": "Chicken Grease",
    "252eb21ce7df7328": "What If I Go",
    "51e433ade2a845e1": "Rome",
    "88d247468cb6d49f": "Peach Dream",
    "cdd2717e52820ff6": "Disco A",
}
EXEMPLARS = {  # v4 M-V4-EAR-1 exemplar set (band 7)
    "a9587ccde1b333f5": "Molasses",
    "467fbeb2e3b019a0": "Essence",
    "2b0370d9d0162c98": "Desire",
}
FOCUS_ORDER = ["252eb21ce7df7328", "31a164f845f8e27e", "88d247468cb6d49f",
               "51e433ade2a845e1", "cdd2717e52820ff6"]  # brief §P3 item 4: WIG first
OUT = Path("data/v5/corpus/corpus_manifest.json")
ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def duration_s(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return round(float(r.stdout.strip()), 3)


def _stem_dir_inventory(d: Path) -> dict | None:
    if not d.is_dir():
        return None
    wavs = sorted(d.glob("*.wav"))
    if not wavs:
        return None
    return {"path": str(d), "n_wav": len(wavs),
            "total_bytes": sum(w.stat().st_size for w in wavs),
            "stems": {w.stem: sha256_file(w) for w in wavs}}


def inventory(sha16: str) -> dict:
    """Existing assets per song. Full-length = stems whose byte size implies
    > 60 s at 44.1 kHz int16 stereo (30 s section stems are ~5.29 MB each)."""
    full_len, section = [], []
    for root in (Path(f"data/v3_spine/{sha16}"), Path(f"data/v3/deliveries/{sha16}")):
        if not root.is_dir():
            continue
        for d in sorted(p for p in root.rglob("*") if p.is_dir()):
            if d.name not in ("rc9_6stem", "stems_6s", "_run1_stems"):
                continue
            inv = _stem_dir_inventory(d)
            if not inv:
                continue
            per_stem = inv["total_bytes"] / max(1, inv["n_wav"])
            (full_len if per_stem > 44100 * 4 * 60 else section).append(inv)
    ms = sorted(str(p) for p in glob.glob(f"data/v3_spine/{sha16}/**/muscriptor/*.json", recursive=True))
    ms += sorted(str(p) for p in glob.glob(f"data/v3/deliveries/{sha16}/**/muscriptor*/*.json", recursive=True))
    rc5 = Path(f"data/recreate_v2/baseline/{sha16}/rc5_tempo_bpm.json")
    anchors: dict = {"rc5_tempo_bpm": json.loads(rc5.read_text()) if rc5.exists() else None,
                     "tempo_choice": {}}
    for p in sorted(glob.glob(f"data/v3_spine/{sha16}/**/tempo_choice.json", recursive=True)
                    + glob.glob(f"data/v3/deliveries/{sha16}/**/tempo_choice.json", recursive=True)):
        if "stage_cache" in p:
            continue
        try:
            anchors["tempo_choice"][p] = json.loads(Path(p).read_text()).get("detected_bpm")
        except Exception:
            anchors["tempo_choice"][p] = None
    return {
        "full_length_stems_present": bool(full_len),
        "full_length_stem_dirs": full_len,
        "operator_section_stem_dirs": [d["path"] for d in section],
        "existing_muscriptor_json": ms,
        "existing_muscriptor_json_full_length": [],  # none exist on disk at c79 (all are 30 s sections)
        "tempo_anchors": anchors,
    }


def main() -> int:
    rows: dict[str, dict] = {}
    with open("corpus/ratings/ratings_manifest.tsv", newline="") as f:
        manifest_rows = list(csv.DictReader(f, delimiter="\t"))
    by_vid = {r["video_id"]: r for r in manifest_rows}

    for band in (4, 5, 6, 7):
        for mp3 in sorted(Path(f"corpus/ratings/{band}").glob("*.mp3")):
            full = sha256_file(mp3)
            sha16 = full[:16]
            is_focus = sha16 in FOCUS
            if band not in (6, 7) and not is_focus:
                continue  # band-4/5 non-focus songs are out of scope (operator decision #1)
            parts = mp3.stem.split("__", 2)
            vid = parts[1] if len(parts) >= 2 else None
            mrow = by_vid.get(vid) if vid and not vid.startswith("LOCAL") else None
            title = (mrow or {}).get("title") or (parts[2].replace("_", " ") if len(parts) == 3 else mp3.stem)
            rows[sha16] = {
                "sha16": sha16, "audio_sha256": full, "audio_path": str(mp3),
                "duration_s": duration_s(mp3), "band": band, "title": title,
                "video_id": vid, "manifest_duration_s": float(mrow["duration_s"]) if mrow else None,
                "is_focus_song": is_focus, "focus_name": FOCUS.get(sha16),
                "is_v4_ear_exemplar": sha16 in EXEMPLARS,
                "asset_inventory": inventory(sha16),
            }

    # v5 corpus membership + deterministic priority (no PRNG; SHA tiebreak).
    def tier(r: dict) -> tuple[int, str]:
        if r["is_focus_song"]:
            return (0, "focus")
        if r["is_v4_ear_exemplar"]:
            return (1, "exemplar")
        return (2, "band7_extra") if r["band"] == 7 else (3, "band6_extra")

    def sort_key(r: dict):
        t, _ = tier(r)
        if t == 0:
            return (0, FOCUS_ORDER.index(r["sha16"]), "")
        return (t, 0, hashlib.sha256(f"v5corpus|{r['sha16']}".encode()).hexdigest())

    ordered = sorted(rows.values(), key=sort_key)
    for rank, r in enumerate(ordered, 1):
        t, name = tier(r)
        r["in_v5_corpus"] = True
        r["v5_tier"] = name
        r["v5_priority_rank"] = rank

    n_b6 = sum(1 for r in rows.values() if r["band"] == 6)
    n_b7 = sum(1 for r in rows.values() if r["band"] == 7)
    n_b5 = sum(1 for r in rows.values() if r["band"] == 5)
    out = {
        "schema_version": 1,
        "cycle": 79,
        "run_id": "run-2026-09-06T000000Z",
        "env_pin_sha256": ENV_PIN_SHA256,
        "operator_decision": "2026-09-06 #1: five focus songs full-length + remaining band-6/7 corpus songs full-length",
        "count_disclosure": {
            "operator_expected_total": "~7",
            "band6_on_disk": n_b6, "band7_on_disk": n_b7,
            "focus_songs_in_band5": n_b5,
            "total_enumerated": len(rows),
            "note": ("Corpus receipts enumerate 13 band-6 + 10 band-7 songs (23), of which CG + PD are focus; "
                     "the other three focus songs (WIG, Rome, Disco A) are BAND 5 per corpus/ratings/5/RECEIPTS.md. "
                     "The operator's '~7 total' undercounts the receipts by ~19. Per brief §P1 all are included with "
                     "in_v5_corpus=true and a deterministic priority order (focus -> v4 ear exemplars -> band-7 extras "
                     "-> band-6 extras, SHA-256 tiebreak within tier); transcription processes in v5_priority_rank order "
                     "and lands whatever completes. Nothing is silently truncated."),
        },
        "full_length_asset_disclosure": (
            "No full-song htdemucs_6s stems exist on disk for any song at c79 open: every rc9_6stem / stems_6s / "
            "_run1_stems directory holds 30 s operator-section stems (~5.29 MB per stem). The brief's premise that "
            "Rome (c20) and Disco A (c21) full-song stems were cached is NOT borne out by the filesystem (invariant (d)); "
            "the c20/c21 full-song runs recorded SHAs in ledger narratives but their WAVs were not retained. "
            "Full-length separation must be recomputed for all songs."),
        "songs": ordered,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    txt = json.dumps(out, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"
    OUT.write_text(txt)
    print(f"wrote {OUT} songs={len(ordered)} sha256={hashlib.sha256(txt.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
