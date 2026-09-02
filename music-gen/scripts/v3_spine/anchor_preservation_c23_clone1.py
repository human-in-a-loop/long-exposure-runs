#!/usr/bin/env /usr/bin/python3
"""c23 clone-1 Peach Dream anchor-preservation snapshot emitter.

Emits data/v3/deliveries/88d247468cb6d49f/cycle23/anchor_preservation_{pre,post}.json
with >=40 anchor SHAs covering read-only files that MUST survive byte-identical
pre==post across the c23 unified-driver delivery run.
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
import glob
from pathlib import Path


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def collect_anchors() -> dict[str, str]:
    anchors: dict[str, str] = {}
    # c22 driver + env_pin (MANDATORY: byte-identical pre==post per operator directive)
    anchors["c22_recreate_v3_py"] = "scripts/v3_spine/recreate_v3.py"
    anchors["c22_env_pin_module"] = "scripts/v3_spine/v3_pipeline/env_pin.py"
    # c4 serializer + palette renderer (canonical read-only anchors)
    anchors["c4_midi_from_json_events_py"] = "scripts/v3_spine/midi_from_json_events.py"
    anchors["c4_render_stem_py"] = "scripts/palette_render/render_stem.py"
    anchors["c4_gm_program_map_v3_py"] = "scripts/v3_spine/gm_program_map_v3.py"
    # Rubric anchors (three-way chain foundation)
    anchors["v3_spine_rubric_v2_txt"] = "data/v3_spine/rubric_hash_v2.txt"
    anchors["v3_recreate_rubric_v3_txt"] = "data/v3/recreate_v3/rubric_hash.txt"
    # Data anchors
    anchors["focus_set_v2_json"] = "data/recreate_v2/focus_set_v2.json"
    anchors["peach_dream_mp3"] = "corpus/ratings/6/015__wXvX1vOe0rQ__Peach_Dream.mp3"
    # c20 PARTIAL predecessor (must survive; c23 sibling under cycle23/)
    anchors["c20_peach_dream_partial_verdict"] = "data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json"
    # c22 dry-run predecessor
    anchors["c22_peach_dream_dryrun_report"] = "data/v3/deliveries/88d247468cb6d49f/cycle22/run_report.json"
    anchors["c22_peach_dream_env_pin_dryrun"] = "data/v3/deliveries/88d247468cb6d49f/cycle22/env_pin.json"
    # SF2 + MuScriptor artifacts (module SHAs must not change)
    anchors["sf2_fluidr3_gm"] = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    anchors["muscriptor_model_safetensors"] = "workspace/models/muscriptor-medium/model.safetensors"
    anchors["muscriptor_binary"] = "workspace/learned_transcribers_venv/bin/muscriptor"

    # Auto-collect scripts/v3_spine/*.py and v3_pipeline/*.py (all read-only)
    for pattern, key_prefix in [
        ("scripts/v3_spine/*.py", "v3spine_"),
        ("scripts/v3_spine/v3_pipeline/*.py", "v3pipeline_"),
    ]:
        for f in sorted(glob.glob(pattern)):
            key = key_prefix + os.path.basename(f).replace(".", "_").replace("-", "_")
            if f not in anchors.values():
                anchors[key] = f

    # c5 CG operator-blessed reconstruction anchor (must survive)
    for i, p in enumerate(sorted(glob.glob("data/v3/deliveries/*/operator_section/full_reconstruction*.wav"))):
        anchors[f"c5_operator_recon_{i}"] = p

    # Cross-song verdicts (must not be touched)
    for f in sorted(glob.glob("data/v3/deliveries/*/cycle*/verdict.json")):
        if "88d247468cb6d49f/cycle23" in f:
            continue
        key = "v3_delivery_" + f.replace("/", "_").replace(".", "_")
        anchors[key] = f
    return anchors


def build_snapshot(purpose: str) -> dict:
    anchors = collect_anchors()
    snapshot = {
        "schema_version": 1,
        "purpose": purpose,
        "expectation": "every anchor byte-identical pre==post; c23 delivery does NOT overwrite predecessors",
        "anchors": {},
    }
    for key, path in sorted(anchors.items()):
        p = Path(path)
        if p.exists() and p.is_file():
            snapshot["anchors"][key] = {
                "path": str(p),
                "sha256": sha(p),
                "size": p.stat().st_size,
            }
        else:
            snapshot["anchors"][key] = {"path": str(p), "status": "MISSING_OR_DIR"}
    snapshot["anchor_count"] = sum(1 for a in snapshot["anchors"].values() if "sha256" in a)
    return snapshot


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else "pre"
    if phase not in ("pre", "post"):
        print(f"usage: {sys.argv[0]} pre|post", file=sys.stderr)
        return 2
    out = Path(f"data/v3/deliveries/88d247468cb6d49f/cycle23/anchor_preservation_{phase}.json")
    snap = build_snapshot(f"c23 clone-1 Peach Dream unified-driver delivery — {phase}-run anchor snapshot")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snap, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out}")
    print(f"anchor_count={snap['anchor_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
