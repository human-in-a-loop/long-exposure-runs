#!/usr/bin/env python3
"""One-shot: verify provenance-pointer resolvability on sample rows."""
import hashlib
import json
from pathlib import Path

rows = [json.loads(l) for l in open("data/rules/ledger_rated_corpus.jsonl") if l.strip()]
manifest = json.load(open("data/rules_rated_corpus/song_manifest.json"))["songs"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


te_by_song = {}
for s in manifest:
    d = {}
    d["score"] = hashlib.sha256(
        f"transcription::score::{sha(s['merged_musicxml'])}".encode()
    ).hexdigest()[:32]
    for stem in ("drums", "bass", "other"):
        p = Path(s["bp_dir"]) / f"{stem}.jsonl"
        d[stem] = hashlib.sha256(
            f"transcription::{stem}::{sha(p)}".encode()
        ).hexdigest()[:32]
    te_by_song[s["song_id"]] = d

all_te_ids = set()
for d in te_by_song.values():
    all_te_ids.update(d.values())

resolved = 0
unresolved = 0
for r in rows:
    for pp in r["provenance_pointers"]:
        if pp["transcription_event_id"] in all_te_ids:
            resolved += 1
        else:
            unresolved += 1

print(f"total_rows={len(rows)}")
print(f"resolved_pointers={resolved}")
print(f"unresolved_pointers={unresolved}")
print(f"resolvability_rate={resolved/(resolved+unresolved):.4f}")
