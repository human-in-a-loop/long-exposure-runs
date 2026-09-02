#!/usr/bin/env python3
"""c6 pre-anchor snapshot: c5 delivery + operator_section artifacts + docs + spec hashes."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path


ANCHORS = [
    # c5 operator-section delivery (READ-ONLY for c6)
    "data/v3/deliveries/31a164f845f8e27e/operator_section/original_ab_operator_section.wav",
    "data/v3/deliveries/31a164f845f8e27e/operator_section/reconstruction_ab_operator_section.wav",
    "data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav",
    "data/v3/deliveries/31a164f845f8e27e/operator_section/manifest.json",
    "data/v3/deliveries/31a164f845f8e27e/operator_section/verdict.json",
    "data/v3/deliveries/31a164f845f8e27e/operator_section/panel.tsv",
    "data/v3/deliveries/31a164f845f8e27e/operator_section/panel.json",
    # c4 delivery preserved as READ-ONLY anchor
    "data/v3/deliveries/31a164f845f8e27e/original_ab.wav",
    "data/v3/deliveries/31a164f845f8e27e/reconstruction_ab.wav",
    "data/v3/deliveries/31a164f845f8e27e/full_reconstruction.wav",
    "data/v3/deliveries/31a164f845f8e27e/manifest.json",
    "data/v3/deliveries/31a164f845f8e27e/verdict.json",
    "data/v3/deliveries/31a164f845f8e27e/panel.tsv",
    "data/v3/deliveries/31a164f845f8e27e/panel.json",
    # c5 operator-section raw stems + rendered per-track
    "data/v3_spine/31a164f845f8e27e/operator_section/section.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/drums.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/bass.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/guitar.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/piano.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/other.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/vocals.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/render/per_track/drums.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/render/per_track/bass.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/render/per_track/guitar.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/render/per_track/piano.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/render/per_track/other.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/render/vocals_htdemucs.wav",
    # Docs (READ-ONLY)
    "docs/v3_spine_rubric_v2.md",
    "docs/v3_spine_canonical_midi_serializer_spec.md",
    "docs/v3_spine_rubric.md",
    "docs/v3_spine_instrument_whitelist_mapping.md",
    "docs/v3_spine_venv_delta_audit_spec.md",
    "docs/v3_spine_rehtdemucs_operator_section_spec.md",
    "docs/PIVOT_v3_simplest_robust_pipeline.md",
    "docs/OPERATOR_recreation_root_cause_audit.md",
    "music_gen_v3_prompt.md",
    # c4 canonical serializer + hashes
    "scripts/v3_spine/midi_from_json_events.py",
    "data/v3_spine/canonical_serializer_spec_hash.txt",
    "data/v3_spine/rubric_hash_v2.txt",
    "data/v3_spine/rubric_hash.txt",
    "data/v3_spine/venv_delta_audit_spec_hash.txt",
    "data/v3_spine/rehtdemucs_operator_section_spec_hash.txt",
    # c3 MuScriptor JSON+MID anchors (READ-ONLY)
    "data/v3_spine/31a164f845f8e27e/muscriptor/drums.json",
    "data/v3_spine/31a164f845f8e27e/muscriptor/drums.mid",
    "data/v3_spine/31a164f845f8e27e/muscriptor/bass.json",
    "data/v3_spine/31a164f845f8e27e/muscriptor/bass.mid",
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
    # c4 merged.mid + tempo
    "data/v3_spine/31a164f845f8e27e/merged.mid",
    "data/v3_spine/31a164f845f8e27e/tempo_choice.json",
    # c4 anchor snapshot + c5 pre/post
    "data/v3_spine/31a164f845f8e27e/anchor_preservation_v2.json",
    "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c5.json",
    # baseline (READ-ONLY)
    "data/recreate_v2/baseline/31a164f845f8e27e/rc5_tempo_bpm.json",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc7_per_stem_loudness.json",
    # Locked scripts (DO-NOT-TOUCH)
    "scripts/palette_render/render_stem.py",
    "scripts/recreate_v2/rc7_v2_rerun.py",
    "scripts/recreate_v2/rc7_mix_balance.py",
    "scripts/v3_spine/mix_match_operator_section.py",
    # focus_set_v2
    "data/recreate_v2/focus_set_v2.json",
    # SF2
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
    # c6 new spec hashes (just written)
    "docs/v3_spine_env_drift_deep_dive_spec.md",
    "docs/v3_spine_method_equivalence_rc7_spec.md",
    "data/v3_spine/env_drift_deep_dive_spec_hash.txt",
    "data/v3_spine/method_equivalence_rc7_spec_hash.txt",
]


def sha256_of(p: str) -> tuple[str, int]:
    with open(p, "rb") as f:
        data = f.read()
    return hashlib.sha256(data).hexdigest(), len(data)


def main():
    root = Path.cwd()
    out = {"cycle": 6, "role": "pre", "anchors": {}, "missing": []}
    for rel in ANCHORS:
        p = rel if rel.startswith("/") else str(root / rel)
        if not Path(p).exists():
            out["missing"].append(rel)
            continue
        h, sz = sha256_of(p)
        out["anchors"][rel] = {"sha256": h, "size": sz}
    out["n_anchors"] = len(out["anchors"])
    out["n_missing"] = len(out["missing"])
    dst = root / "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c6.json"
    dst.write_text(json.dumps(out, indent=2, sort_keys=True))
    snap_sha = hashlib.sha256(dst.read_bytes()).hexdigest()
    print(f"n_anchors={out['n_anchors']} n_missing={out['n_missing']} snapshot_sha={snap_sha[:16]}")
    if out["n_missing"] > 0:
        print("MISSING:", out["missing"], file=sys.stderr)


if __name__ == "__main__":
    main()
