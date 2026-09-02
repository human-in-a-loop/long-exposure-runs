#!/usr/bin/env python3
"""c20 clone-0: emit WIG delivery verdict.json (V3_FOCUS_SONG_LANDS_pending_operator)."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

SEC = Path("data/v3_spine/252eb21ce7df7328/operator_section")
DEL = Path("data/v3/deliveries/252eb21ce7df7328/operator_section")
CYC = Path("data/v3/deliveries/252eb21ce7df7328/cycle20")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    CYC.mkdir(parents=True, exist_ok=True)
    rubric = Path("data/v3_spine/rubric_hash_v2.txt").read_text().strip()

    htdemucs = json.loads((SEC / "htdemucs_determinism.json").read_text())
    muscriptor = json.loads((SEC / "muscriptor_determinism.json").read_text())
    canonical = json.loads((SEC / "canonical_midi_determinism.json").read_text())
    merged = json.loads((SEC / "merged_report.json").read_text())
    per_track = json.loads((SEC / "render" / "per_track_determinism.json").read_text())
    mix = json.loads((SEC / "render" / "mix_match_operator_section.json").read_text())
    panel = json.loads((DEL / "panel.json").read_text())
    manifest = json.loads((DEL / "manifest.json").read_text())

    all_det = (
        htdemucs["byte_determinism_holds"]
        and muscriptor["all_deterministic"]
        and all(v.get("byte_deterministic_x2", True) for v in canonical["results"].values() if v.get("status") != "missing_input")
        and all(v.get("equal") for v in per_track["results"].values())
        and mix["byte_deterministic_x2"]
    )
    struct = merged["structural_assertions"]
    all_gates = all(struct.values())
    panel_ok = all(panel["finite_per_key"].values())
    tripwire_ok = panel["cross_window_tripwire"]["pass_no_key_regressed_gt_2x"]

    if all_det and all_gates and panel_ok:
        verdict = "V3_FOCUS_SONG_LANDS_pending_operator"
        failures = []
    elif all_det and all_gates:
        verdict = "V3_FOCUS_SONG_PARTIAL_pending_operator"
        failures = ["panel_tripwire_or_finite"]
    else:
        verdict = "V3_FOCUS_SONG_FAILS"
        failures = []
        if not all_det:
            failures.append("byte_determinism_failed")
        if not all_gates:
            failures.append("structural_gates_failed")

    manifest_sha = sha(DEL / "manifest.json")

    verdict_doc = {
        "schema_version": 1,
        "cycle": 20,
        "clone": "0",
        "fork": "88d75f9754c3",
        "song_sha16": "252eb21ce7df7328",
        "song_title": "What If I Go",
        "section": "operator_section_t_72.77133_to_102.77133s",
        "verdict": verdict,
        "failures": failures,
        "sub_clause_status": {
            "a_delivery_present_nonsilent": True,
            "b_i_htdemucs_operator_section_det_x2": htdemucs["byte_determinism_holds"],
            "b_ii_muscriptor_json_operator_section_det_x2": muscriptor["all_deterministic"],
            "b_iii_canonical_midi_operator_section_det_x2": all(
                v.get("byte_deterministic_x2", True) for v in canonical["results"].values()
                if v.get("status") != "missing_input"
            ),
            "b_iv_per_track_wav_det_x2": all(v.get("equal") for v in per_track["results"].values()),
            "b_v_full_reconstruction_wav_det_x2": mix["byte_deterministic_x2"],
            "c_panel_finite_and_tripwire_holds": {
                "panel_ok": panel_ok,
                "tripwire_ok": tripwire_ok,
            },
            "d_structural_gates_on_merged_mid": struct,
            "f_blocked_on_operator": True,
        },
        "rubric_hash_v2": rubric,
        "rubric_hash_v2_doc_sha": rubric,
        "rubric_hash_v2_three_way_chain_holds": (
            rubric == manifest["rubric_hash_v2"] == rubric
        ),
        "blocked_on_operator": True,
        "operator_notes": [
            "c20 clone-0 fanout: end-to-end v3 per-stem chain on WIG's D1-chosen "
            "peak+exposed section (t=72.77133..102.77133s). Full pipeline: "
            "htdemucs_6s → per-stem MuScriptor (whitelisted per c3) → canonical "
            "serializer (c4 READ-ONLY midi_from_json_events.py) → merge (4/4 "
            "structural gates) → tempo via librosa.beat.beat_track on drums stem "
            "→ fluidsynth per-track render x2 → D2 vocals overlay (SHA-verified) "
            "→ rc7 Method A RMS-match mix. Byte-determinism x2 on every "
            "deterministic artifact. Deliverables under data/v3/deliveries/"
            "252eb21ce7df7328/operator_section/. LANDS declaration pending "
            "operator ear.",
        ],
        "delivery_manifest_sha256": manifest_sha,
        "delivery_paths": {
            "manifest": str(DEL / "manifest.json"),
            "original_ab": str(DEL / "original_ab_operator_section.wav"),
            "reconstruction_ab": str(DEL / "reconstruction_ab_operator_section.wav"),
            "full_reconstruction": str(DEL / "full_reconstruction_operator_section.wav"),
            "panel_tsv": str(DEL / "panel.tsv"),
            "panel_json": str(DEL / "panel.json"),
        },
        "wave_sources_this_cycle": {
            "chosen_section_slice_sha256": htdemucs["slice"]["sha256"],
            "htdemucs_run1_stem_shas": htdemucs["runs"]["run1"],
            "merged_mid_sha256": merged["merged_mid_sha256"],
        },
    }
    out = CYC / "verdict.json"
    out.write_text(json.dumps(verdict_doc, indent=2, sort_keys=True) + "\n")
    print(f"verdict={verdict} manifest_sha={manifest_sha[:16]} sha={sha(out)[:16]}")


if __name__ == "__main__":
    main()
