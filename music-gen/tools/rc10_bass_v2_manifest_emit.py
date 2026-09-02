#!/usr/bin/env /usr/bin/python3
# One-shot: emit A/B pairs manifest + per-pair v2 info.json. Archives to stale/ post-run per c29+.
# created: 2026-09-02, cycle 55, run-2026-08-28T040704Z, worker, fork 7cc01d726807 clone-1
import json
import hashlib
from pathlib import Path

impl = Path("data/rc10_bass_v2_impl")
ab_root = Path("data/recreate_v2/ab_pairs")
verdict = json.loads((impl / "verdict.json").read_text())

manifest = {
    "iter": 1,
    "stem": "bass",
    "rendered_via": "fluidsynth GM 34 (program=33) with articulation-driven envelope shaping",
    "target_lufs_i": -23.0,
    "pairs": [],
}
for song in verdict["songs"]:
    sha = song["song_id"]
    pair_dir = ab_root / sha / "bass" / "iter_1"
    orig = pair_dir / "original.wav"
    rend = pair_dir / "rendered.wav"
    entry = {
        "song_id": sha,
        "original_wav": str(orig),
        "rendered_wav": str(rend),
        "original_sha256": hashlib.sha256(orig.read_bytes()).hexdigest() if orig.exists() else None,
        "rendered_sha256": hashlib.sha256(rend.read_bytes()).hexdigest() if rend.exists() else None,
        "n_notes": song["articulation"]["slap"] + song["articulation"]["ghost"] + song["articulation"]["sustained"],
        "articulation": song["articulation"],
        "gate": song["gate"],
    }
    manifest["pairs"].append(entry)
    info = {
        "iter": 1,
        "song_id": sha,
        "winner": "bass_v2_onset_segmented_pyin",
        "n_notes": entry["n_notes"],
        "articulation": entry["articulation"],
        "gate": song["gate"],
    }
    (pair_dir / "info.json").write_text(json.dumps(info, sort_keys=True, indent=2) + "\n")

(impl / "ab_pairs_manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
print(f"manifest with {len(manifest['pairs'])} pairs written")
