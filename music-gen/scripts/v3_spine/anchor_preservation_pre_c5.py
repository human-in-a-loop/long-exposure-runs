#!/usr/bin/env python3
"""c5 pre-anchor snapshot: SHA-256 of c4 delivery artifacts + docs + spec hashes."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path


ANCHORS = [
    # c4 delivery artifacts (READ-ONLY for c5)
    "data/v3/deliveries/31a164f845f8e27e/original_ab.wav",
    "data/v3/deliveries/31a164f845f8e27e/reconstruction_ab.wav",
    "data/v3/deliveries/31a164f845f8e27e/full_reconstruction.wav",
    "data/v3/deliveries/31a164f845f8e27e/manifest.json",
    "data/v3/deliveries/31a164f845f8e27e/verdict.json",
    "data/v3/deliveries/31a164f845f8e27e/panel.tsv",
    "data/v3/deliveries/31a164f845f8e27e/panel.json",
    # c4 docs (READ-ONLY)
    "docs/v3_spine_rubric_v2.md",
    "docs/v3_spine_canonical_midi_serializer_spec.md",
    "docs/v3_spine_rubric.md",
    "docs/v3_spine_instrument_whitelist_mapping.md",
    "docs/PIVOT_v3_simplest_robust_pipeline.md",
    "docs/OPERATOR_recreation_root_cause_audit.md",
    "music_gen_v3_prompt.md",
    # c4 canonical serializer + hashes
    "scripts/v3_spine/midi_from_json_events.py",
    "data/v3_spine/canonical_serializer_spec_hash.txt",
    "data/v3_spine/rubric_hash_v2.txt",
    "data/v3_spine/rubric_hash.txt",
    # c3 MuScriptor JSON+MID anchors (READ-ONLY)
    "data/v3_spine/31a164f845f8e27e/muscriptor/drums.json",
    "data/v3_spine/31a164f845f8e27e/muscriptor/drums.mid",
    "data/v3_spine/31a164f845f8e27e/muscriptor/bass.json",
    "data/v3_spine/31a164f845f8e27e/muscriptor/bass.mid",
    "data/v3_spine/31a164f845f8e27e/muscriptor/guitar.json",
    "data/v3_spine/31a164f845f8e27e/muscriptor/guitar.mid",
    "data/v3_spine/31a164f845f8e27e/muscriptor/other.json",
    "data/v3_spine/31a164f845f8e27e/muscriptor/other.mid",
    "data/v3_spine/31a164f845f8e27e/muscriptor/piano.json",
    "data/v3_spine/31a164f845f8e27e/muscriptor/piano.mid",
    "data/v3_spine/31a164f845f8e27e/muscriptor/vocals.json",
    "data/v3_spine/31a164f845f8e27e/muscriptor/vocals.mid",
    "data/v3_spine/31a164f845f8e27e/muscriptor/full_mix.json",
    "data/v3_spine/31a164f845f8e27e/muscriptor/full_mix.mid",
    # c4 canonical MIDI anchors (READ-ONLY)
    "data/v3_spine/31a164f845f8e27e/canonical_midi/drums.mid",
    "data/v3_spine/31a164f845f8e27e/canonical_midi/bass.mid",
    "data/v3_spine/31a164f845f8e27e/canonical_midi/guitar.mid",
    "data/v3_spine/31a164f845f8e27e/canonical_midi/other.mid",
    "data/v3_spine/31a164f845f8e27e/canonical_midi/piano.mid",
    "data/v3_spine/31a164f845f8e27e/canonical_midi/vocals.mid",
    "data/v3_spine/31a164f845f8e27e/canonical_midi/full_mix.mid",
    # c4 merged.mid + tempo choice
    "data/v3_spine/31a164f845f8e27e/merged.mid",
    "data/v3_spine/31a164f845f8e27e/tempo_choice.json",
    # c4 anchor snapshot itself
    "data/v3_spine/31a164f845f8e27e/anchor_preservation_v2.json",
    # baseline (READ-ONLY)
    "data/recreate_v2/baseline/31a164f845f8e27e/rc5_tempo_bpm.json",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc7_per_stem_loudness.json",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/drums.wav",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/bass.wav",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/vocals.wav",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/guitar.wav",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/piano.wav",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/other.wav",
    # Locked scripts (DO-NOT-TOUCH)
    "scripts/palette_render/render_stem.py",
    # c5 spec hashes (just written)
    "data/v3_spine/venv_delta_audit_spec_hash.txt",
    "data/v3_spine/rehtdemucs_operator_section_spec_hash.txt",
    "docs/v3_spine_venv_delta_audit_spec.md",
    "docs/v3_spine_rehtdemucs_operator_section_spec.md",
    # focus_set_v2 with chosen section
    "data/recreate_v2/focus_set_v2.json",
    # SF2
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
]


def sha256_of(p: str) -> tuple[str, int]:
    with open(p, "rb") as f:
        data = f.read()
    return hashlib.sha256(data).hexdigest(), len(data)


def main():
    root = Path.cwd()
    out = {"cycle": 5, "role": "pre", "anchors": {}, "missing": []}
    for rel in ANCHORS:
        p = rel if rel.startswith("/") else str(root / rel)
        if not Path(p).exists():
            out["missing"].append(rel)
            continue
        h, sz = sha256_of(p)
        out["anchors"][rel] = {"sha256": h, "size": sz}
    out["n_anchors"] = len(out["anchors"])
    out["n_missing"] = len(out["missing"])
    dst = root / "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c5.json"
    dst.write_text(json.dumps(out, indent=2, sort_keys=True))
    snap_sha = hashlib.sha256(dst.read_bytes()).hexdigest()
    print(f"n_anchors={out['n_anchors']} n_missing={out['n_missing']} snapshot_sha={snap_sha[:16]}")
    if out["n_missing"] > 0:
        print("MISSING:", out["missing"], file=sys.stderr)


if __name__ == "__main__":
    main()
