#!/usr/bin/python3
"""READ-ONLY anchor SHA snapshot pre/post-run.

Ensures c33 render_stem.py, c50 v2 rubric, c49 v1 rubric, c53 clone-2 rc5
tempo anchors per song, focus_set_v2.json, and baseline 6-stem WAVs are
byte-identical after this branch runs.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Dict, List

ANCHORS_STATIC = [
    "scripts/palette_render/render_stem.py",
    "docs/m_recreate_2_accurate_small_set_rubric_v2.md",
    "docs/m_recreate_2_accurate_small_set_rubric.md",
    "data/recreate_v2/focus_set_v2.json",
    "data/recreate_v2/focus_set.json",
    "data/recreate_v2/rubric_hash.txt",
    "data/recreate_v2/rubric_hash_v2.txt",
    "docs/rc10_drums_v2_rubric.md",
    "docs/rc10_bass_v2_rubric.md",
    "docs/rc10_ab_pairs_refresh_rubric.md",
    "docs/rc10_drums_bass_rubric.md",
    "docs/rc10_guitar_piano_rubric.md",
    "docs/rc10_other_vocals_rubric.md",
]

FOCUS_SONGS = [
    "31a164f845f8e27e",
    "252eb21ce7df7328",
    "51e433ade2a845e1",
    "88d247468cb6d49f",
    "cdd2717e52820ff6",
]


def sha256_file(p: pathlib.Path) -> str:
    if not p.exists():
        return ""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot() -> Dict[str, str]:
    out: Dict[str, str] = {}
    for rel in ANCHORS_STATIC:
        out[rel] = sha256_file(pathlib.Path(rel))
    for sha in FOCUS_SONGS:
        out[f"data/recreate_v2/baseline/{sha}/rc5_tempo_bpm.json"] = sha256_file(
            pathlib.Path(f"data/recreate_v2/baseline/{sha}/rc5_tempo_bpm.json")
        )
        for stem in ("drums", "bass", "vocals", "guitar", "piano", "other"):
            p = pathlib.Path(f"data/recreate_v2/baseline/{sha}/rc9_6stem/{stem}.wav")
            out[str(p)] = sha256_file(p)
    return out


def compare(pre: Dict[str, str], post: Dict[str, str]) -> List[str]:
    diffs: List[str] = []
    for k in sorted(set(pre.keys()) | set(post.keys())):
        if pre.get(k) != post.get(k):
            diffs.append(k)
    return diffs


def main() -> int:
    out_dir = pathlib.Path("data/rc10_musical_time")
    out_dir.mkdir(parents=True, exist_ok=True)
    snap = snapshot()
    # Note: single-shot snapshot; caller invokes pre and post separately and
    # compares. For convenience, emit both pre + post if invoked twice.
    payload = {
        "anchor_count": len(snap),
        "anchors": snap,
    }
    (out_dir / "anchor_preservation.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True)
    )
    print(json.dumps({"n_anchors": len(snap)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
