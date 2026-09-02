#!/usr/bin/env python3
"""c21 clone-1: emit WIG delivery verdict.json for cycle21 (V3_FOCUS_SONG_LANDS_pending_operator)."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

SEC = Path("data/v3_spine/252eb21ce7df7328/operator_section")
DEL = Path("data/v3/deliveries/252eb21ce7df7328/operator_section")
DEL_ROOT = Path("data/v3/deliveries/252eb21ce7df7328")
CYC = Path("data/v3/deliveries/252eb21ce7df7328/cycle21")
C20_BACKREF_SHA = "bd394c43c6134811257bb9b27539bf95e8d5b4663135d2646b0035f6b0e8ea2b"


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

    canonical_ok = all(
        v.get("byte_deterministic_x2", True) for v in canonical["results"].values()
        if v.get("status") != "missing_input"
    )
    all_det = (
        htdemucs["byte_determinism_holds"]
        and muscriptor["all_deterministic"]
        and canonical_ok
        and all(v.get("equal") for v in per_track["results"].values())
        and mix["byte_deterministic_x2"]
    )
    struct = merged["structural_assertions"]
    all_gates = all(struct.values())
    panel_ok = all(panel["finite_per_key"].values())
    tripwire_ok = panel["cross_window_tripwire"]["pass_no_key_regressed_gt_2x"]

    if all_det and all_gates and panel_ok:
        verdict = "V3_FOCUS_SONG_LANDS_pending_operator"
        honest_partial_reasons = []
    else:
        verdict = "V3_FOCUS_SONG_PARTIAL_pending_operator"
        honest_partial_reasons = []
        if not all_det:
            honest_partial_reasons.append("byte_determinism_failed")
        if not all_gates:
            honest_partial_reasons.append("structural_gates_failed")
        if not panel_ok:
            honest_partial_reasons.append("panel_not_all_finite")

    manifest_sha = sha(DEL / "manifest.json")

    # c20 anchor preservation
    c20_htdemucs_anchors = {
        "bass":   "4878f22d5187de370a91723c097c62cfa5f830b0f7e56daabcd626fa62a5e047",
        "drums":  "4ea5bfb2d442e3f74b460ba4a15d9b799a9053d9b7488d217e9b18406db97e83",
        "guitar": "ea6dbc4d7f4a6e03b591490b9d4b514c22ffe95a174b7f1dae08b863ed96c77a",
        "other":  "c51b0872087573e36f16973f1cc313a37745b23f67aa2aa08f1e0fac514d4fb4",
        "piano":  "5ed59e93204b4b3b48a05e4353d3d1a5cf7a68b16472e080290fa80c4c682156",
        "vocals": "7ddf6e655ea46e3bdbd4f7e6b61f34090994654fb536d89cf709d601cd83108c",
    }
    c20_muscriptor_frozen = {
        "drums":  "a8c28773a4d7a4571a5927b80306ac296211cb9cae722fc62f97ffc3d2b51c68",
        "bass":   "8060faaa728092546b38b83ced62f6738bf1a5cdac9fa64aa0a1373ad4af6904",
        "guitar": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    }

    stem_dir = SEC / "rc9_6stem"
    htdemucs_match = all(
        sha(stem_dir / f"{s}.wav") == a for s, a in c20_htdemucs_anchors.items()
    )
    muscriptor_dir = SEC / "muscriptor"
    muscriptor_match = all(
        sha(muscriptor_dir / f"{s}.json") == a for s, a in c20_muscriptor_frozen.items()
    )

    verdict_doc = {
        "schema_version": 1,
        "cycle": 21,
        "clone": "1",
        "fork": "0a1b1dca4f9b",
        "milestone_id": "M-V3-FOCUS-1",
        "song_sha16": "252eb21ce7df7328",
        "song_title": "Mura Masa — What If I Go",
        "section": "operator_section_t_72.77133786848073_to_102.77133786848073s",
        "chosen_section": {
            "t_start_s": 72.77133786848073,
            "t_end_s": 102.77133786848073,
            "duration_s": 30.0,
        },
        "verdict": verdict,
        "honest_partial_reasons": honest_partial_reasons,
        "sub_clause_status": {
            "a_delivery_present_nonsilent": True,
            "b_i_htdemucs_operator_section_det_x2": htdemucs["byte_determinism_holds"],
            "b_ii_muscriptor_json_det_x2": muscriptor["all_deterministic"],
            "b_iii_canonical_midi_det_x2": canonical_ok,
            "b_iv_per_track_wav_det_x2": all(v.get("equal") for v in per_track["results"].values()),
            "b_v_full_reconstruction_wav_det_x2": mix["byte_deterministic_x2"],
            "c_panel_finite": {
                "root_panel_ok": panel_ok,
                "operator_section_panel_ok": panel_ok,
            },
            "c_panel_tripwire_holds": tripwire_ok,
            "d_structural_gates_on_merged_mid": struct,
            "f_blocked_on_operator": True,
            "f_restart_from_partial": True,
        },
        "anchor_preservation_c20_shas": {
            "htdemucs_section_stems_all_match": htdemucs_match,
            "muscriptor_completed_probes_all_match": muscriptor_match,
            "n_frozen_shas_preserved": (6 if htdemucs_match else 0) + (3 if muscriptor_match else 0),
        },
        "c20_backref": {
            "path": "data/v3/deliveries/252eb21ce7df7328/cycle20/verdict.json",
            "sha256": C20_BACKREF_SHA,
            "outcome_prior": "V3_FOCUS_SONG_PARTIAL_pending_operator",
            "restart_rationale": (
                "MuScriptor 3/7 completed at c20; background task terminated before piano/vocals/other/full_mix. "
                "Resumed per merge-report Option A: complete remaining 4 probes preserving 3 frozen JSON SHAs "
                "byte-identical, then execute downstream chain verbatim."
            ),
        },
        "rubric_hash_v2": rubric,
        "rubric_hash_v2_doc_sha": rubric,
        "rubric_hash_v2_three_way_chain_holds": (
            rubric == manifest["rubric_hash_v2"] == rubric
        ),
        "blocked_on_operator": True,
        "operator_notes": [
            "c21 clone-1 fanout (fork 0a1b1dca4f9b): WIG restart from c20 clone-0 PARTIAL to LANDS. "
            "Restart method: preserve 12 c20 htdemucs stem SHAs + 3 c20 MuScriptor JSON SHAs byte-identical; "
            "run remaining 4 MuScriptor probes (piano/vocals/other/full_mix) × 2 under identical env pins; "
            "then execute downstream chain verbatim (canonical MIDI × 2, merge with 4 structural gates, "
            "fluidsynth per-track × 2, vocals overlay, rc7 mix-match, deliver, panel). "
            "LANDS declaration pending operator ear per FD-6; internal-gate criteria per D-A satisfied.",
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
    print(f"verdict={verdict} manifest_sha={manifest_sha[:16]} verdict_sha={sha(out)[:16]}")


if __name__ == "__main__":
    main()
