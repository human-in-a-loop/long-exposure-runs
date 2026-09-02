#!/usr/bin/env python3
"""c21 anchor preservation snapshot for palette-render branch.

Snapshots >= 60 read-only anchors pre-run into anchor_preservation.json,
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

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"requires /usr/bin/python3 (got {sys.executable})")

_REPO = Path(__file__).resolve().parents[3]
OUT = _REPO / "data" / "v3_spine" / "31a164f845f8e27e" / "palette_render" / "anchor_preservation.json"

C5_DELIV = _REPO / "data" / "v3" / "deliveries" / "31a164f845f8e27e"
SEC = _REPO / "data" / "v3_spine" / "31a164f845f8e27e" / "operator_section"

ANCHORS: list[str] = []

# c5 delivery root + operator_section
for p in [
    C5_DELIV / "verdict.json",
    C5_DELIV / "manifest.json",
    C5_DELIV / "cycle7" / "verdict.json",
    C5_DELIV / "cycle8" / "verdict.json",
    C5_DELIV / "cycle9" / "verdict.json",
    C5_DELIV / "cycle10" / "verdict.json",
    C5_DELIV / "operator_section" / "full_reconstruction_operator_section.wav",
    C5_DELIV / "operator_section" / "original_ab_operator_section.wav",
    C5_DELIV / "operator_section" / "reconstruction_ab_operator_section.wav",
    C5_DELIV / "operator_section" / "manifest.json",
    C5_DELIV / "operator_section" / "verdict.json",
    C5_DELIV / "operator_section" / "panel.json",
    C5_DELIV / "operator_section" / "panel.tsv",
]:
    ANCHORS.append(str(p.relative_to(_REPO)))

# c5 canonical per-stem MIDIs (read-only render inputs)
for stem in ("bass", "drums", "guitar", "piano", "other", "vocals", "full_mix"):
    ANCHORS.append(str((SEC / "canonical_midi" / f"{stem}.mid").relative_to(_REPO)))

# c5 htdemucs vocals stem + baseline 6-stems
ANCHORS.append(str((SEC / "render" / "vocals_htdemucs.wav").relative_to(_REPO)))
for stem in ("bass", "drums", "guitar", "piano", "other", "vocals"):
    ANCHORS.append(str((SEC / "rc9_6stem" / f"{stem}.wav").relative_to(_REPO)))
for stem in ("bass", "drums", "guitar", "piano", "other"):  # vocals verbatim, no per_track
    ANCHORS.append(str((SEC / "render" / "per_track" / f"{stem}.wav").relative_to(_REPO)))

# c5 metadata JSONs
for p in [
    SEC / "canonical_midi_determinism.json",
    SEC / "muscriptor_determinism.json",
    SEC / "htdemucs_determinism.json",
    SEC / "tempo_choice.json",
    SEC / "merged.mid",
    SEC / "merged_midi_sha.txt",
    SEC / "merged_report.json",
    SEC / "rc7_per_stem_loudness_operator_section.json",
    SEC / "render" / "mix_match_operator_section.json",
    SEC / "render" / "vocals_overlay.json",
    SEC / "render" / "per_track_determinism.json",
]:
    ANCHORS.append(str(p.relative_to(_REPO)))

# c6 Method B v3-paths anchors
V3P = _REPO / "data" / "v3_spine" / "rc7_v2_v3_paths"
for p in [
    V3P / "rc7_v2_v3_paths_full_reconstruction.wav",
    V3P / "byte_determinism.json",
]:
    if p.exists():
        ANCHORS.append(str(p.relative_to(_REPO)))

# Locked scripts (do-not-touch)
for p in [
    "scripts/palette_render/render_stem.py",
    "scripts/v3_spine/rc7_v2_rerun_v3_paths.py",
    "scripts/recreate_v2/rc7_mix_balance.py",
    "scripts/v3_spine/midi_from_json_events.py",
    "scripts/v3_spine/mix_match_operator_section.py",
    "scripts/v3_spine/muscriptor_operator_section.py",
]:
    ANCHORS.append(p)

# Rubric chains
for p in [
    "docs/v3_spine_rubric.md",
    "docs/v3_spine_rubric_v2.md",
    "data/v3_spine/rubric_hash.txt",
    "data/v3_spine/rubric_hash_v2.txt",
    "docs/v3_spine_chicken_grease_palette_render_c21_rubric.md",
    "data/v3_spine/31a164f845f8e27e/palette_render/rubric_hash_v2.txt",
]:
    ANCHORS.append(p)

# Focus set + cadence policy
for p in [
    "data/recreate_v2/focus_set_v2.json",
    "docs/wait_on_operator_cadence_policy.md",
    "data/v3_spine/wait_on_operator_cadence_policy_hash.txt",
    "plan_of_record.md",
]:
    ANCHORS.append(p)


def sha256(path: Path) -> str:
    if not path.is_file():
        return "MISSING"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot() -> dict:
    entries = []
    for rel in ANCHORS:
        p = _REPO / rel
        entries.append({"path": rel, "sha256": sha256(p)})
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

    # post: compare vs pre
    if not OUT.is_file():
        print("ERROR: pre snapshot missing", file=sys.stderr)
        return 2
    pre = json.loads(OUT.read_text())
    pre_map = {e["path"]: e["sha256"] for e in pre["entries"]}
    post_entries = []
    mismatches = []
    for rel in ANCHORS:
        p = _REPO / rel
        s = sha256(p)
        post_entries.append({"path": rel, "sha256": s})
        if pre_map.get(rel) != s:
            mismatches.append({"path": rel, "pre": pre_map.get(rel), "post": s})
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
