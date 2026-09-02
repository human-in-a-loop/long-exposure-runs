#!/usr/bin/env python3
"""c21 clone-1: anchor preservation snapshot for WIG restart. Verify c20 anchors byte-identical pre==post."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

SEC = Path("data/v3_spine/252eb21ce7df7328/operator_section")
OUT = SEC / "anchor_preservation_c21.json"


def sha(p):
    p = Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "MISSING"


ANCHORS = {
    # 12 c20 htdemucs stem SHAs (6 rc9_6stem + 6 _run1_stems if present)
    "htdemucs/rc9_6stem/bass.wav":   "4878f22d5187de370a91723c097c62cfa5f830b0f7e56daabcd626fa62a5e047",
    "htdemucs/rc9_6stem/drums.wav":  "4ea5bfb2d442e3f74b460ba4a15d9b799a9053d9b7488d217e9b18406db97e83",
    "htdemucs/rc9_6stem/guitar.wav": "ea6dbc4d7f4a6e03b591490b9d4b514c22ffe95a174b7f1dae08b863ed96c77a",
    "htdemucs/rc9_6stem/other.wav":  "c51b0872087573e36f16973f1cc313a37745b23f67aa2aa08f1e0fac514d4fb4",
    "htdemucs/rc9_6stem/piano.wav":  "5ed59e93204b4b3b48a05e4353d3d1a5cf7a68b16472e080290fa80c4c682156",
    "htdemucs/rc9_6stem/vocals.wav": "7ddf6e655ea46e3bdbd4f7e6b61f34090994654fb536d89cf709d601cd83108c",
    # 3 c20 MuScriptor JSON SHAs (drums/bass/guitar frozen)
    "muscriptor/drums.json":  "a8c28773a4d7a4571a5927b80306ac296211cb9cae722fc62f97ffc3d2b51c68",
    "muscriptor/bass.json":   "8060faaa728092546b38b83ced62f6738bf1a5cdac9fa64aa0a1373ad4af6904",
    "muscriptor/guitar.json": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    # 3 c20 MuScriptor MID SHAs
    "muscriptor/drums.mid":  "33de0cbc2ae02844c96391e02198b77692db939106067c09f724af78cde5db28",
    "muscriptor/bass.mid":   "543f1ab705b7b2fe845689ca4ef5274e2dd885a2d70121e7a1e175ceadf40cbe",
}


PATH_MAP = {
    "htdemucs/rc9_6stem/bass.wav":   SEC / "rc9_6stem/bass.wav",
    "htdemucs/rc9_6stem/drums.wav":  SEC / "rc9_6stem/drums.wav",
    "htdemucs/rc9_6stem/guitar.wav": SEC / "rc9_6stem/guitar.wav",
    "htdemucs/rc9_6stem/other.wav":  SEC / "rc9_6stem/other.wav",
    "htdemucs/rc9_6stem/piano.wav":  SEC / "rc9_6stem/piano.wav",
    "htdemucs/rc9_6stem/vocals.wav": SEC / "rc9_6stem/vocals.wav",
    "muscriptor/drums.json":  SEC / "muscriptor/drums.json",
    "muscriptor/bass.json":   SEC / "muscriptor/bass.json",
    "muscriptor/guitar.json": SEC / "muscriptor/guitar.json",
    "muscriptor/drums.mid":   SEC / "muscriptor/drums.mid",
    "muscriptor/bass.mid":    SEC / "muscriptor/bass.mid",
}


def main():
    result = {"schema_version": 1, "cycle": 21, "clone": "1", "anchors": {}, "n_total": 0, "n_match": 0, "n_mismatch": 0}
    for key, expected in ANCHORS.items():
        actual = sha(PATH_MAP[key])
        match = actual == expected
        result["anchors"][key] = {"expected": expected, "actual": actual, "match": match}
        result["n_total"] += 1
        if match:
            result["n_match"] += 1
        else:
            result["n_mismatch"] += 1
    result["all_match"] = result["n_mismatch"] == 0
    # section.wav, tempo_choice.json, rubric doc
    result["additional_context"] = {
        "section_wav_sha": sha(SEC / "section.wav"),
        "tempo_choice_json_sha": sha(SEC / "tempo_choice.json"),
        "rubric_hash_v2": Path("data/v3_spine/rubric_hash_v2.txt").read_text().strip(),
        "render_stem_py_sha": sha(Path("scripts/palette_render/render_stem.py")),
        "midi_from_json_events_py_sha": sha(Path("scripts/v3_spine/midi_from_json_events.py")),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"anchor_preservation_c21: n_total={result['n_total']} n_match={result['n_match']} n_mismatch={result['n_mismatch']} all_match={result['all_match']}")


if __name__ == "__main__":
    main()
