#!/usr/bin/env python3
"""c20 clone-0 WIG: compute SHAs of existing state artifacts for honest verdict."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

PATHS = {
  "section_wav": Path("data/v3_spine/252eb21ce7df7328/operator_section/section.wav"),
  "htdemucs_determinism": Path("data/v3_spine/252eb21ce7df7328/operator_section/htdemucs_determinism.json"),
  "tempo_choice": Path("data/v3_spine/252eb21ce7df7328/operator_section/tempo_choice.json"),
  "muscriptor_drums_json": Path("data/v3_spine/252eb21ce7df7328/operator_section/muscriptor/drums.json"),
  "muscriptor_drums_mid": Path("data/v3_spine/252eb21ce7df7328/operator_section/muscriptor/drums.mid"),
  "muscriptor_bass_json": Path("data/v3_spine/252eb21ce7df7328/operator_section/muscriptor/bass.json"),
  "muscriptor_bass_mid": Path("data/v3_spine/252eb21ce7df7328/operator_section/muscriptor/bass.mid"),
  "muscriptor_guitar_json": Path("data/v3_spine/252eb21ce7df7328/operator_section/muscriptor/guitar.json"),
  "muscriptor_guitar_mid": Path("data/v3_spine/252eb21ce7df7328/operator_section/muscriptor/guitar.mid"),
  "muscriptor_script": Path("scripts/v3_spine/muscriptor_operator_section_wig.py"),
  "canonicalize_script": Path("scripts/v3_spine/canonicalize_operator_section_probes_wig.py"),
  "merge_script": Path("scripts/v3_spine/merge_per_stem_midi_operator_section_wig.py"),
  "render_script": Path("scripts/v3_spine/render_per_track_operator_section_wig.py"),
  "vocals_overlay_script": Path("scripts/v3_spine/vocals_overlay_operator_section_wig.py"),
  "mix_match_script": Path("scripts/v3_spine/mix_match_operator_section_wig.py"),
  "deliver_script": Path("scripts/v3_spine/deliver_operator_section_wig.py"),
  "sanity_panel_script": Path("scripts/v3_spine/sanity_panel_operator_section_wig.py"),
  "verdict_c20_wig_script": Path("scripts/v3_spine/verdict_c20_wig.py"),
  "v3_rubric_v2_doc": Path("docs/v3_spine_rubric_v2.md"),
  "rubric_hash_v2_txt": Path("data/v3_spine/rubric_hash_v2.txt"),
  "cadence_policy_doc": Path("docs/wait_on_operator_cadence_policy.md"),
  "cadence_policy_hash_txt": Path("data/v3_spine/wait_on_operator_cadence_policy_hash.txt"),
  "c5_method_a_wav": Path("data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav"),
  "c19_verdict": Path("data/v3/deliveries/31a164f845f8e27e/cycle19/verdict.json"),
  "test_wig_c20": Path("tests/test_v3_focus_wig_c20.py"),
  "focus_set_v2": Path("data/recreate_v2/focus_set_v2.json"),
  "midi_from_json_events": Path("scripts/v3_spine/midi_from_json_events.py"),
  "mix_match_c5": Path("scripts/v3_spine/mix_match_operator_section.py"),
  "render_stem_c33": Path("scripts/palette_render/render_stem.py"),
}

def main():
    out = {}
    for k, p in PATHS.items():
        if p.exists():
            out[k] = {"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
        else:
            out[k] = {"path": str(p), "exists": False}
    outp = Path("data/v3_spine/252eb21ce7df7328/cycle20/state_snapshot.json")
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"wrote {outp}")

if __name__ == "__main__":
    main()
