#!/usr/bin/python3
# ---
# created: 2026-09-02T00:00:00Z
# cycle: 58
# milestone: M-V3-SPINE
# ---
"""Snapshot ≥20 READ-ONLY anchor SHAs pre/post to prove no drift."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"anchor_preservation requires /usr/bin/python3 (got {sys.executable})")

WSROOT = Path(__file__).resolve().parents[2]

ANCHORS: list[str] = [
    "scripts/recreate_v2/rc4_v2_gm_program_map.py",
    "scripts/recreate_v2/rc1_v2_hybrid.py",
    "scripts/recreate_v2/rc7_mix_balance.py",
    "scripts/recreate_v2/rc7_v2_rerun.py",
    "scripts/recreate_v2/rc6_v2_panel_gate.py",
    "scripts/recreate_v2/rc8_section_selection.py",
    "scripts/recreate_v2/rc9_first_class_parts.py",
    "data/recreate_v2/focus_set_v2.json",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/drums.wav",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/bass.wav",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/guitar.wav",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/piano.wav",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/other.wav",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/vocals.wav",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc5_tempo_bpm.json",
    "workspace/models/muscriptor-medium/model.safetensors",
    "scripts/palette_render/render_stem.py",
    "corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3",
    "docs/v3_spine_rubric.md",
    "data/v3_spine/rubric_hash.txt",
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
]


def _sha256(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot() -> dict:
    out: dict[str, str] = {}
    for a in ANCHORS:
        p = Path(a) if a.startswith("/") else WSROOT / a
        out[a] = _sha256(p)
    return out


def check_preservation(song_sha16: str) -> dict:
    root = WSROOT / "data" / "v3_spine" / song_sha16
    pre_path = root / "anchor_preservation_pre.json"
    post_path = root / "anchor_preservation.json"
    now = snapshot()
    if not pre_path.exists():
        # first invocation: baseline
        pre_path.write_text(json.dumps(now, sort_keys=True, indent=2) + "\n")
        result = {"phase": "pre", "n_anchors": len(now), "all_match": True,
                  "snapshot": now}
        post_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        return result
    pre = json.loads(pre_path.read_text())
    mismatches = {k: {"pre": pre.get(k, "MISSING"), "post": now[k]}
                  for k in ANCHORS if pre.get(k) != now[k]}
    result = {
        "phase": "post",
        "n_anchors": len(ANCHORS),
        "n_mismatch": len(mismatches),
        "all_match": len(mismatches) == 0,
        "mismatches": mismatches,
        "snapshot": now,
    }
    post_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--song-sha16", default="31a164f845f8e27e")
    ap.add_argument("--reset", action="store_true", help="delete pre snapshot to re-baseline")
    args = ap.parse_args()
    if args.reset:
        p = WSROOT / "data" / "v3_spine" / args.song_sha16 / "anchor_preservation_pre.json"
        if p.exists():
            p.unlink()
    r = check_preservation(args.song_sha16)
    print(json.dumps({"phase": r.get("phase"), "n_anchors": r["n_anchors"],
                      "all_match": r.get("all_match"),
                      "n_mismatch": r.get("n_mismatch", 0)}, indent=2))


if __name__ == "__main__":
    main()
