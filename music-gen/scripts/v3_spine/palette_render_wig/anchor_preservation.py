#!/usr/bin/env python3
"""c25 anchor preservation snapshot for WIG palette-render branch.

Snapshots >=30 read-only anchors pre-run into anchor_preservation.json,
re-hashes post-run, and asserts every entry byte-identical pre==post.

Usage:
    anchor_preservation.py --phase pre
    anchor_preservation.py --phase post
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"requires /usr/bin/python3 (got {sys.executable})")

_REPO = Path(__file__).resolve().parents[3]
SONG_SHA16 = "252eb21ce7df7328"
OUT = _REPO / "data" / "v3_spine" / SONG_SHA16 / "palette_render" / "anchor_preservation.json"

WIG_DELIV = _REPO / "data" / "v3" / "deliveries" / SONG_SHA16
WIG_SEC = _REPO / "data" / "v3_spine" / SONG_SHA16 / "operator_section"
CG_DELIV = _REPO / "data" / "v3" / "deliveries" / "31a164f845f8e27e"
CG_SPINE_PAL = _REPO / "data" / "v3_spine" / "31a164f845f8e27e" / "palette_render"

ANCHORS: list[str] = []

# --- c21 WIG operator-blessed delivery
for p in [
    WIG_DELIV / "operator_section" / "manifest.json",
    WIG_DELIV / "operator_section" / "full_reconstruction_operator_section.wav",
    WIG_DELIV / "operator_section" / "original_ab_operator_section.wav",
    WIG_DELIV / "operator_section" / "reconstruction_ab_operator_section.wav",
    WIG_DELIV / "operator_section" / "panel.json",
    WIG_DELIV / "operator_section" / "panel.tsv",
]:
    ANCHORS.append(str(p.relative_to(_REPO)))

# --- c21 WIG operator_section (spine dir)
for p in [
    WIG_SEC / "section.wav",
    WIG_SEC / "merged.mid",
    WIG_SEC / "merged_report.json",
    WIG_SEC / "tempo_choice.json",
    WIG_SEC / "muscriptor_determinism.json",
    WIG_SEC / "htdemucs_determinism.json",
    WIG_SEC / "canonical_midi_determinism.json",
    WIG_SEC / "anchor_preservation_c21.json",
    WIG_SEC / "render" / "vocals_htdemucs.wav",
    WIG_SEC / "render" / "vocals_overlay.json",
    WIG_SEC / "render" / "per_track_determinism.json",
]:
    ANCHORS.append(str(p.relative_to(_REPO)))

for stem in ("bass", "drums", "guitar", "piano", "other", "vocals"):
    ANCHORS.append(str((WIG_SEC / "rc9_6stem" / f"{stem}.wav").relative_to(_REPO)))

for m in ("bass", "drums", "guitar", "piano", "other", "vocals", "full_mix"):
    ANCHORS.append(str((WIG_SEC / "canonical_midi" / f"{m}.mid").relative_to(_REPO)))

# --- c21 Chicken Grease palette delivery (anchor: proof exists byte-identical)
for p in [
    CG_DELIV / "cycle21" / "verdict_palette.json",
    CG_DELIV / "palette_render" / "manifest.json",
    CG_DELIV / "palette_render" / "full_reconstruction_palette.wav",
    CG_SPINE_PAL / "rubric_hash_v2.txt",
    CG_SPINE_PAL / "full_reconstruction_palette.wav",
    CG_SPINE_PAL / "anchor_preservation.json",
]:
    if p.exists():
        ANCHORS.append(str(p.relative_to(_REPO)))

# --- Locked scripts (do-not-touch)
for p in [
    "scripts/palette_render/render_stem.py",
    "scripts/v3_spine/recreate_v3.py",
    "scripts/v3_spine/v3_pipeline/env_pin.py",
    "scripts/v3_spine/midi_from_json_events.py",
    "scripts/v3_spine/rc7_v2_rerun_v3_paths.py",
    "scripts/v3_spine/mix_match_operator_section.py",
    "scripts/recreate_v2/rc7_mix_balance.py",
]:
    ANCHORS.append(p)

# --- Rubric chains
for p in [
    "docs/v3_spine_rubric.md",
    "docs/v3_spine_rubric_v2.md",
    "data/v3_spine/rubric_hash.txt",
    "data/v3_spine/rubric_hash_v2.txt",
    "docs/v3_spine_chicken_grease_palette_render_c21_rubric.md",
    "docs/v3_spine_wig_palette_render_c25_rubric.md",
    "data/v3_spine/252eb21ce7df7328/palette_render/rubric_hash_v2.txt",
]:
    ANCHORS.append(p)

# --- Focus set + cadence policy + POR
for p in [
    "data/recreate_v2/focus_set_v2.json",
    "data/recreate_v2/rubric_hash_v2.txt",
    "docs/wait_on_operator_cadence_policy.md",
    "data/v3_spine/wait_on_operator_cadence_policy_hash.txt",
    "plan_of_record.md",
]:
    ANCHORS.append(p)

# --- SF2 sha (external file, only path anchor)
for p in ["/usr/share/sounds/sf2/FluidR3_GM.sf2"]:
    ANCHORS.append(p)


def sha256(path) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = _REPO / p
    if not p.is_file():
        return "MISSING"
    return hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot() -> dict:
    entries = []
    for rel in ANCHORS:
        entries.append({"path": str(rel), "sha256": sha256(rel)})
    return {"n_entries": len(entries), "entries": entries}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("pre", "post"), required=True)
    args = ap.parse_args()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if args.phase == "pre":
        snap = snapshot()
        snap["phase"] = "pre"
        OUT.write_text(json.dumps(snap, sort_keys=True, indent=2) + "\n")
        print(f"pre-snapshot: {snap['n_entries']} anchors -> {OUT.relative_to(_REPO)}")
        return 0

    if not OUT.is_file():
        print("ERROR: pre snapshot missing", file=sys.stderr)
        return 2
    pre = json.loads(OUT.read_text())
    pre_map = {e["path"]: e["sha256"] for e in pre["entries"]}
    post_entries = []
    mismatches = []
    for rel in ANCHORS:
        s = sha256(rel)
        post_entries.append({"path": str(rel), "sha256": s})
        if pre_map.get(str(rel)) != s:
            mismatches.append({"path": str(rel),
                               "pre": pre_map.get(str(rel)), "post": s})
    result = {
        "phase": "post",
        "n_entries": len(post_entries),
        "n_mismatch": len(mismatches),
        "all_match": len(mismatches) == 0,
        "mismatches": mismatches,
        "pre_entries": pre["entries"],
        "post_entries": post_entries,
    }
    OUT.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(f"post-snapshot: {len(post_entries)} anchors, n_mismatch={len(mismatches)}")
    return 0 if result["all_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
