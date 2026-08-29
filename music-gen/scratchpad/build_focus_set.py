"""Build data/recreate_v2/focus_set.json (deterministic SHA-256 tiebreak).
Runs before any script under scripts/recreate_v2/ lands (mtime discipline).
This file is scratchpad-only; not adopted into the ledger."""
import hashlib
import json
import os
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = Path("/home/user/long-exposure-runs/music-gen")
os.chdir(ROOT)

POOL = [
    ("Chicken Grease",        "It2s36sL4aM", "PLoxlz_x73gZO1UKfmdIRRvnJBiJkQd53l", 6,
        "corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3"),
    ("Mura Masa What If I Go", "pLuQ0MGLBXU", "PLoxlz_x73gZO1UKfmdIRRvnJBjWQd53l", 5,
        "corpus/ratings/5/021__pLuQ0MGLBXU__Mura_Masa_-_What_If_I_Go.mp3"),
    ("Disco A",               "hcwKJOsUUIk", "PLoxlz_x73gZO1UKfmdIRRvnJBjWQd53l", 5,
        "corpus/ratings/5/011__hcwKJOsUUIk__Disco_A.mp3"),
    ("Peach Dream",           "wXvX1vOe0rQ", "PLoxlz_x73gZO1UKfmdIRRvnJBiJkQd53l", 6,
        "corpus/ratings/6/015__wXvX1vOe0rQ__Peach_Dream.mp3"),
    ("Lost",                  "89RgkWOsn18", "PLoxlz_x73gZO1UKfmdIRRvnJBiJkQd53l", 6,
        "corpus/ratings/6/007__89RgkWOsn18__Lost.mp3"),
    ("Dojo Cuts Rome",        "gPp2KBV9zXk", "PLoxlz_x73gZO1UKfmdIRRvnJBjWQd53l", 5,
        "corpus/ratings/5/012__gPp2KBV9zXk__Dojo_Cuts_-_Rome.mp3"),
]

def sha256_bytes(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def tiebreak(title, vid, pl):
    return hashlib.sha256(f"{title}|{vid}|{pl}".encode("utf-8")).hexdigest()

entries = []
for title, vid, pl, band, path in POOL:
    tb = tiebreak(title, vid, pl)
    exists = os.path.exists(path)
    entry = {
        "title": title, "video_id": vid, "playlist_id": pl,
        "rating_band": band, "path": path,
        "tiebreak_sha256": tb, "exists": exists,
        "audio_sha256": sha256_bytes(path) if exists else None,
    }
    if exists:
        entry["audio_sha16"] = entry["audio_sha256"][:16]
    entries.append(entry)

mandatory = [e for e in entries if e["title"] == "Chicken Grease"]
candidates = [e for e in entries if e["title"] != "Chicken Grease"]
ranked = sorted(candidates, key=lambda e: e["tiebreak_sha256"])
selected = mandatory + [e for e in ranked[:4] if e["exists"]]

focus_set = {
    "cycle": 49,
    "run_id": "run-2026-08-28T040704Z",
    "milestone": "M-RECREATE-2/accurate-small-set",
    "selection_method": "SHA-256 tiebreak over (title|video_id|playlist_id) UTF-8; Chicken Grease mandatory; top 4 filler",
    "n_songs": len(selected),
    "songs": selected,
    "excluded_by_rank": [e["title"] for e in ranked[4:]],
    "rubric_sha256": Path("data/recreate_v2/rubric_hash.txt").read_text().strip(),
}

out = Path("data/recreate_v2/focus_set.json")
out.write_text(json.dumps(focus_set, indent=2, sort_keys=True) + "\n")
print(f"selected {len(selected)} songs: {[s['title'] for s in selected]}")
print(f"excluded by rank: {focus_set['excluded_by_rank']}")
print(f"file sha: {hashlib.sha256(out.read_bytes()).hexdigest()[:16]}")
