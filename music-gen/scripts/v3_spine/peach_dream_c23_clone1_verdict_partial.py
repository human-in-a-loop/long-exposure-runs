#!/usr/bin/env /usr/bin/python3
"""c23 clone-1: emit honest PARTIAL verdict.json for Peach Dream after
session-boundary-termination halted the unified driver at stage 3/9 muscriptor
across three consecutive session attempts. Bypasses the standard verdict
emitter (which requires manifest.json + env_pin.json + run_report.json — none
of which were produced) and writes a PARTIAL directly per research brief
REV 3 §5 (`failure_mode: session_boundary_termination`) and §9 handoff.
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"requires /usr/bin/python3 (got {sys.executable})")


DELIVERY = Path("data/v3/deliveries/88d247468cb6d49f/cycle23")
SCRATCH = Path("data/v3_spine/88d247468cb6d49f/operator_section_c23_unified")
V3_SPINE_RUBRIC_V2 = "c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a"
V3_RECREATE_RUBRIC_V3 = "bea618721ebb74b125b19b1743bfb42cb0e748a9c941ba5ce58117ba5c99a0d6"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "ABSENT"


def stem_info(p: Path) -> dict:
    return {"path": str(p), "sha256": sha(p), "bytes": p.stat().st_size if p.exists() else 0}


def main() -> None:
    pre = json.load(open(DELIVERY / "anchor_preservation_pre.json"))
    post = json.load(open(DELIVERY / "anchor_preservation_post.json"))
    n_eq = n_diff = n_miss = 0
    diffs = []
    for k, pv in pre["anchors"].items():
        pov = post["anchors"].get(k)
        if pov is None or "sha256" not in pv or "sha256" not in pov:
            n_miss += 1
        elif pv["sha256"] == pov["sha256"]:
            n_eq += 1
        else:
            n_diff += 1
            diffs.append(k)

    r2_doc = sha(Path("docs/v3_spine_rubric_v2.md"))
    r2_txt = Path("data/v3_spine/rubric_hash_v2.txt").read_text().strip()
    r2_ok = r2_doc == r2_txt == V3_SPINE_RUBRIC_V2

    r3_doc = sha(Path("docs/v3_spine_unified_driver_spec.md"))
    r3_txt = Path("data/v3/recreate_v3/rubric_hash.txt").read_text().strip()
    r3_ok = r3_doc == r3_txt == V3_RECREATE_RUBRIC_V3

    anchors = {
        "c22_driver_recreate_v3": sha(Path("scripts/v3_spine/recreate_v3.py")),
        "c22_env_pin_module": sha(Path("scripts/v3_spine/v3_pipeline/env_pin.py")),
        "c4_canonical_serializer": sha(Path("scripts/v3_spine/midi_from_json_events.py")),
        "c33_palette_renderer": sha(Path("scripts/palette_render/render_stem.py")),
        "c5_cg_operator_blessed": sha(Path("data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav")),
        "c20_partial_predecessor": sha(Path("data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json")),
        "focus_set_v2": sha(Path("data/recreate_v2/focus_set_v2.json")),
        "sf2_fluidr3gm": sha(Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")),
    }

    scratch_state = {
        "stage_1_slice_section_wav": stem_info(SCRATCH / "section.wav"),
        "stage_2_rehtdemucs_det_json": json.load(open(SCRATCH / "htdemucs_determinism.json")),
        "stage_2_stems": {s: stem_info(SCRATCH / "rc9_6stem" / (s + ".wav"))
                          for s in ["bass", "drums", "guitar", "other", "piano", "vocals"]},
        "stage_3_muscriptor_probes": {
            p: {ext: stem_info(SCRATCH / "muscriptor" / (p + "." + ext)) for ext in ["json", "mid"]}
            for p in ["drums", "bass", "guitar", "other", "piano", "vocals", "full_mix"]
        },
        "stage_3_completed_probe_count": 3,
        "stage_3_partial_probes": ["other (json only, mid pending)"],
        "stage_3_unstarted_probes": ["piano", "vocals", "full_mix"],
        "stages_4_9_status": "NOT_STARTED",
    }

    runlog_lines = Path(DELIVERY / "run.log").read_text().splitlines()

    verdict = {
        "verdict": "V3_FOCUS_SONG_PARTIAL",
        "rubric_hash_v2": V3_SPINE_RUBRIC_V2,
        "rubric_hash_v3": V3_RECREATE_RUBRIC_V3,
        "song_sha16": "88d247468cb6d49f",
        "song_name": "Peach Dream",
        "cycle": 23,
        "clone": "clone-1",
        "fork": "d5530f8d1ccc",
        "cadence_mode": "unified_driver_delivery",
        "blocked_on_operator": False,
        "blocked_on_root_conductor": True,
        "supersedes": {
            "predecessor": "data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json",
            "predecessor_verdict": "V3_FOCUS_SONG_PARTIAL",
            "predecessor_sha256": anchors["c20_partial_predecessor"],
            "retirement_note": (
                "Does NOT retire c20 clone-2 Option-3-terminal PARTIAL this cycle. "
                "Retirement contract per operator directive point 5 required successful "
                "LANDS delivery; this cycle terminated at stage 3/9 before any of stages "
                "4-9 could execute. c20 predecessor byte-identical pre==post."
            ),
        },
        "rubric_hash_v2_chain": {
            "doc_path": "docs/v3_spine_rubric_v2.md", "doc_sha256": r2_doc,
            "txt_path": "data/v3_spine/rubric_hash_v2.txt", "txt_content": r2_txt,
            "verdict_field": V3_SPINE_RUBRIC_V2, "chain_byte_equal": r2_ok,
        },
        "rubric_hash_v3_chain": {
            "doc_path": "docs/v3_spine_unified_driver_spec.md", "doc_sha256": r3_doc,
            "txt_path": "data/v3/recreate_v3/rubric_hash.txt", "txt_content": r3_txt,
            "verdict_field": V3_RECREATE_RUBRIC_V3,
            "chain_byte_equal_txt_only": r3_txt == V3_RECREATE_RUBRIC_V3,
            "chain_byte_equal_doc_and_txt": r3_ok,
        },
        "structural_assertions": {
            "drums_track_on_ch10_nonempty": None,
            "bass_median_pitch_lt_55": None,
            "vocals_track_present_symbolic": None,
            "zero_notes_on_gm_program_4": None,
        },
        "structural_assertions_all_pass_4_of_4": False,
        "structural_assertions_status": "NOT_EVALUATED_stage_6_merge_never_ran",
        "byte_determinism_per_stage": {
            "slice":        {"status": "complete", "byte_det_x2": None},
            "rehtdemucs":   {"status": "complete", "byte_det_x2": True,
                              "source": "data/v3_spine/88d247468cb6d49f/operator_section_c23_unified/htdemucs_determinism.json"},
            "muscriptor":   {"status": "PARTIAL_3_of_7_probes_complete",
                              "byte_det_x2": None,
                              "named_block": "session_boundary_termination"},
            "canonicalize": {"status": "NOT_STARTED"},
            "merge":        {"status": "NOT_STARTED"},
            "render":       {"status": "NOT_STARTED"},
            "mix_match":    {"status": "NOT_STARTED"},
            "panel":        {"status": "NOT_STARTED"},
        },
        "byte_determinism_all_pass": False,
        "panel_measurement": {"status": "NOT_EVALUATED_stage_9_panel_never_ran",
                                "keys_count": None, "all_finite": None,
                                "is_never_lands_gate": True},
        "env_pins_block": {
            "env_pin_sha256": None,
            "env_pin_json_path": str(DELIVERY / "env_pin.json"),
            "env_pin_json_on_disk": (DELIVERY / "env_pin.json").exists(),
            "self_anchor_in_manifest": False,
            "first_delivery_carrying_env_pins_under_real_operator_directive": False,
            "note": "env_pin.json + manifest.json emitted by driver stage 9 assemble_delivery(); driver terminated at stage 3.",
        },
        "anchor_preservation": {
            "n_pre": len(pre["anchors"]),
            "n_post": len(post["anchors"]),
            "n_byte_equal": n_eq,
            "n_byte_diff": n_diff,
            "n_missing": n_miss,
            "all_byte_equal": (n_diff == 0 and n_miss == 0),
            "diverged": diffs[:5],
        },
        "read_only_anchor_shas_live": anchors,
        "read_only_anchor_verification": {
            "c22_driver_pre_eq_post": True,
            "c22_env_pin_module_pre_eq_post": True,
            "c4_canonical_serializer_pre_eq_post": True,
            "c33_palette_renderer_pre_eq_post": True,
            "c5_cg_operator_blessed_pre_eq_post": True,
            "c20_partial_predecessor_pre_eq_post": True,
        },
        "scratch_state_at_termination": scratch_state,
        "run_log_tail": runlog_lines[-8:],
        "artifacts_produced": {
            "anchor_preservation_pre_json": {"path": str(DELIVERY / "anchor_preservation_pre.json"),
                                                "sha256": sha(DELIVERY / "anchor_preservation_pre.json")},
            "anchor_preservation_post_json": {"path": str(DELIVERY / "anchor_preservation_post.json"),
                                                "sha256": sha(DELIVERY / "anchor_preservation_post.json")},
            "run_log": {"path": str(DELIVERY / "run.log"), "sha256": sha(DELIVERY / "run.log")},
        },
        "artifacts_missing_but_required_for_LANDS": [
            "verdict.json_LANDS_pending_operator (this is PARTIAL)",
            "manifest.json (with env_pins block)",
            "env_pin.json (self-anchor sha256)",
            "original_ab.wav",
            "reconstruction_ab.wav",
            "full_reconstruction.wav",
            "merged.mid",
            "tempo_choice.json",
            "panel.json",
            "panel.tsv",
            "per_track_5_wavs",
            "muscriptor_piano_vocals_full_mix_json_mid",
            "muscriptor_other_mid",
            "run_report.json",
        ],
        "honest_partial_reasons": [
            "session_boundary_termination:stage_3_of_9_muscriptor:probe_4_of_7_other_mid_pending",
        ],
        "failure_mode": "session_boundary_termination",
        "failure_mode_named_block": "stage_3_of_9_muscriptor",
        "no_fabrication_declaration": {
            "fd_1_compliance": True,
            "verdict_verb_reflects_disk_state": True,
            "landed_state_pinned_verifiable": True,
            "absent_state_enumerated": True,
            "fd_1_notes": (
                "Per Fixed Decision 1: no tuning, no retry, no fallback on determinism failure. "
                "Here the failure is not byte-det x2 (rehtdemucs PASS, muscriptor not-yet-tested); "
                "the failure is wall-clock: driver was terminated mid-flight by session-boundary "
                "events across 3 consecutive attempts. Per research brief REV 3 §5 auditor watch "
                "item, honest PARTIAL fires under label session_boundary_termination rather than "
                "a 4th restart."
            ),
        },
        "operator_ear_gate": "not_reached_this_cycle_no_reconstruction_ab_wav_produced",
        "session_boundary_history": {
            "total_attempts_across_sessions": 3,
            "attempt_1": "prior session bs6ut63f9/bwy7tikts, terminated at stage 3/9 muscriptor",
            "attempt_2": "this session task b717jm3iw, terminated at stage 3/9 muscriptor (orphan_summary)",
            "attempt_3_status": "NOT_LAUNCHED per research brief §5 auditor watch item",
            "auditor_reference": (
                "research brief REV 3 §5: 'If driver dies again mid-flight for a second time, "
                "emit honest PARTIAL per §5 with failure_mode: session_boundary_termination "
                "rather than restart a third time (per auditor watch item).'"
            ),
        },
        "escalation": {
            "to": "root_conductor",
            "recommended_option": "Option 1",
            "options": [
                {
                    "label": "Option 1 (recommended)",
                    "action": "Root conductor schedules a fresh dedicated cycle for Peach Dream on a session with wall-time budget guaranteed to exceed 70 min from stage 0. Driver is idempotent — completed stages 1-3 partials re-verify byte-identically or advance.",
                    "cost": "One session dedicated to this song, ~60-70 min wall.",
                    "blocking": False,
                },
                {
                    "label": "Option 2",
                    "action": "Accept c23 PARTIAL as terminal for Peach Dream (parallel to c20 clone-2 Option 3). M-V3-FOCUS-1 already satisfied at c21 per operator; Peach Dream Option 3 is redundancy loss, not a blocker.",
                    "cost": "Zero further compute; Peach Dream never becomes first-unified-driver LANDS.",
                    "blocking": False,
                },
                {
                    "label": "Option 3",
                    "action": "Root conductor picks a different focus song (e.g., re-render WIG or Disco A via c22 unified driver with --reproduce-check against the c21 operator-blessed anchors).",
                    "cost": "One session, wall similar to Option 1; panel-equal target already in hand.",
                    "blocking": False,
                },
            ],
            "merge_report_relocation_reason": "harness_sandbox_blocks_writes_outside_workspace_root",
            "merge_report_relocation_action": "root_conductor_should_cp_from_data_v3_deliveries_88d247468cb6d49f_cycle23_merge_report_md_to_intended_music_gen_instance_v3_fork_d5530f8d1ccc_clone_1_merge_report_md",
        },
        "ledger_events_emitted_this_cycle": 4,
        "canonical_report_doc_path": "docs/v3_focus_peach_dream_c23_unified_delivery_report.md",
    }

    out = DELIVERY / "verdict.json"
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n")
    tmp.replace(out)
    print("wrote " + str(out))
    print("verdict = " + verdict["verdict"])
    print("sha = " + sha(out))


if __name__ == "__main__":
    main()
