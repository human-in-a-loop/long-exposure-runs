#!/usr/bin/env python3
"""c20 clone-0: emit honest PARTIAL verdict for WIG (252eb21ce7df7328).

Pipeline state:
  - htdemucs_6s: DONE (6/6 stems)
  - muscriptor: 3/7 probes done (drums/bass/guitar); piano/vocals/other/full_mix pending
  - canonicalize / merge / render / vocals-overlay / mix-match / deliver / panel: NOT RUN
  - operator A/B WAVs + full-song WAV: NOT EMITTED

Emits PARTIAL verdict honestly; blocked on:
  (a) muscriptor pipeline incompletion (4/7 probes deferred)
  (b) FD-6 operator ear on the eventual A/B (irrelevant while chain incomplete)
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

SONG_SHA16 = "252eb21ce7df7328"
DEL_DIR = Path(f"data/v3/deliveries/{SONG_SHA16}/cycle20")
DEL_DIR.mkdir(parents=True, exist_ok=True)

RUBRIC_DOC = Path("docs/v3_spine_rubric_v2.md")
RUBRIC_HASH_TXT = Path("data/v3_spine/rubric_hash_v2.txt")
CADENCE_POLICY_DOC = Path("docs/wait_on_operator_cadence_policy.md")

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    rubric_doc_sha = sha(RUBRIC_DOC)
    rubric_txt_content = RUBRIC_HASH_TXT.read_text().strip()
    cadence_policy_sha = sha(CADENCE_POLICY_DOC)
    c19_verdict_sha = sha(Path("data/v3/deliveries/31a164f845f8e27e/cycle19/verdict.json"))

    # Muscriptor state
    mus_dir = Path(f"data/v3_spine/{SONG_SHA16}/operator_section/muscriptor")
    mus_probes = {
        "drums": {"json": mus_dir / "drums.json", "mid": mus_dir / "drums.mid", "status": "done"},
        "bass": {"json": mus_dir / "bass.json", "mid": mus_dir / "bass.mid", "status": "done"},
        "guitar": {"json": mus_dir / "guitar.json", "mid": mus_dir / "guitar.mid", "status": "done_empty"},
        "other": {"json": mus_dir / "other.json", "mid": mus_dir / "other.mid", "status": "not_yet_run"},
        "piano": {"json": mus_dir / "piano.json", "mid": mus_dir / "piano.mid", "status": "not_yet_run"},
        "vocals": {"json": mus_dir / "vocals.json", "mid": mus_dir / "vocals.mid", "status": "not_yet_run"},
        "full_mix": {"json": mus_dir / "full_mix.json", "mid": mus_dir / "full_mix.mid", "status": "not_yet_run"},
    }
    for k, v in mus_probes.items():
        v["json_sha256"] = sha(v["json"]) if v["json"].exists() else None
        v["mid_sha256"] = sha(v["mid"]) if v["mid"].exists() else None
        v["json_path"] = str(v["json"])
        v["mid_path"] = str(v["mid"])
        # drop Path objects — not JSON-serializable
        v.pop("json")
        v.pop("mid")

    verdict = {
        "milestone_id": "M-V3-FOCUS-1",
        "song_sha16": SONG_SHA16,
        "song_name": "What If I Go",
        "cycle": 20,
        "clone": "clone-0",
        "fork": "88d75f9754c3",
        "parent_cycle_track": "peer sub-milestone under M-V3-FOCUS-1 per c29 state-machine lemma",
        "verdict": "V3_FOCUS_SONG_PARTIAL_pending_operator",
        "blocked_on_operator": True,
        "blocked_on_muscriptor_completion": True,
        "reason": (
            "Pipeline incomplete: MuScriptor per-stem transcription reached 3/7 probes "
            "(drums, bass, guitar-empty) before background task terminated; 4/7 remaining "
            "(other, piano, vocals, full_mix). Downstream chain "
            "(canonicalize -> merge -> render -> vocals-overlay -> mix-match -> deliver "
            "-> panel) NOT EXECUTED per FD-1 (no tuning/retry). Operator A/B WAVs + "
            "full-song WAV NOT EMITTED. FD-6 operator ear irrelevant while chain "
            "incomplete."
        ),
        "rubric_hash_v2": rubric_doc_sha,
        "rubric_hash_v2_doc_sha": rubric_doc_sha,
        "rubric_hash_v2_txt_content": rubric_txt_content,
        "rubric_hash_v2_three_way_chain_holds": (
            rubric_doc_sha == rubric_txt_content
        ),
        "cadence_policy_ref": str(CADENCE_POLICY_DOC),
        "cadence_policy_sha": cadence_policy_sha,
        "verdict_placement_convention": "cycle<N>/",
        "pipeline_state": {
            "htdemucs_6s": {
                "status": "done",
                "n_stems": 6,
                "byte_deterministic_x2": True,
                "det_json_path": "data/v3_spine/252eb21ce7df7328/operator_section/htdemucs_determinism.json",
                "det_json_sha256": sha(Path("data/v3_spine/252eb21ce7df7328/operator_section/htdemucs_determinism.json")),
            },
            "muscriptor": {
                "status": "partial",
                "n_probes_expected": 7,
                "n_probes_done": 3,
                "n_probes_pending": 4,
                "note": (
                    "Background task terminated after 3rd probe (guitar). Remaining probes "
                    "not executed this cycle per FD-1 (no tuning/retry on background-task "
                    "termination; operator decides restart)."
                ),
                "probes": mus_probes,
            },
            "canonicalize": {"status": "not_run", "reason": "muscriptor incomplete"},
            "merge": {"status": "not_run", "reason": "canonicalize prerequisite"},
            "tempo_choice": {
                "status": "done",
                "detected_bpm": 50.17445388349515,
                "rc5_baseline_bpm": 200.89285714285714,
                "note": (
                    "Detected on WIG operator-section drums only; large delta vs rc5 baseline "
                    "(likely octave/subdivision artefact). Fallback to rc5 baseline not "
                    "applied per FD-1."
                ),
                "path": "data/v3_spine/252eb21ce7df7328/operator_section/tempo_choice.json",
                "sha256": sha(Path("data/v3_spine/252eb21ce7df7328/operator_section/tempo_choice.json")),
            },
            "render": {"status": "not_run", "reason": "merge prerequisite"},
            "vocals_overlay": {"status": "not_run", "reason": "muscriptor vocals incomplete"},
            "mix_match": {"status": "not_run", "reason": "render prerequisite"},
            "deliver_ab": {"status": "not_emitted", "reason": "mix_match prerequisite"},
            "panel_measurement": {"status": "not_run", "reason": "deliver prerequisite"},
        },
        "operator_ab_pending": {
            "status": "not_emitted_pipeline_incomplete",
            "reason": "Pipeline chain not exercised past muscriptor stage.",
        },
        "operator_ear_gate": "operator ear on WIG A/B is the only LANDS authority (FD-6); currently non-applicable because A/B WAVs not emitted",
        "operator_notes": [
            "MuScriptor background task terminated at 3/7 probes. Operator decides: "
            "(A) restart muscriptor for remaining 4 probes and continue chain in c21, OR "
            "(B) declare WIG focus-song delivery deferred behind Chicken Grease operator "
            "ear (FD-6) which remains blocked_on_operator since c4.",
            "Existing artifacts preserved READ-ONLY: 6-stem htdemucs (byte-det x2), "
            "3 muscriptor JSON+MID pairs (drums non-empty, bass non-empty, guitar empty), "
            "tempo_choice.json. Nothing to unwind.",
            "Discipline gates observed: FD-1 (no tuning/retry), FD-6 (operator ear only "
            "LANDS authority), rubric_hash_v2 three-way chain byte-equal, "
            "cycle<N>/ placement convention.",
        ],
        "focus_set_v2_ref": {
            "path": "data/recreate_v2/focus_set_v2.json",
            "sha256": sha(Path("data/recreate_v2/focus_set_v2.json")),
            "chosen_section_source": "focus_set_v2.json",
        },
        "read_only_upstream_anchors": {
            "c19_verdict": {
                "path": "data/v3/deliveries/31a164f845f8e27e/cycle19/verdict.json",
                "sha256": c19_verdict_sha,
            },
            "c5_method_a_wav": {
                "path": "data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav",
                "sha256": "cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7",
                "note": "Chicken Grease Method A reconstruction (c5); operator ear anchor per FD-6.",
            },
            "midi_from_json_events_c4": {
                "path": "scripts/v3_spine/midi_from_json_events.py",
                "sha256": sha(Path("scripts/v3_spine/midi_from_json_events.py")),
                "note": "c4 canonical MIDI serializer; consumed READ-ONLY.",
            },
            "mix_match_operator_section_c5": {
                "path": "scripts/v3_spine/mix_match_operator_section.py",
                "sha256": sha(Path("scripts/v3_spine/mix_match_operator_section.py")),
                "note": "c5 Method A plain RMS-match; per-song sibling reads READ-ONLY.",
            },
            "render_stem_c33": {
                "path": "scripts/palette_render/render_stem.py",
                "sha256": sha(Path("scripts/palette_render/render_stem.py")),
                "note": "c33 render_stem.py; DO-NOT-TOUCH invariant.",
            },
        },
        "test_suite": {
            "path": "tests/test_v3_focus_wig_c20.py",
            "sha256": sha(Path("tests/test_v3_focus_wig_c20.py")),
            "n_cases_expected": 12,
            "status": "landed_prior; determinism gates skip when preconditions absent",
        },
        "next_action_if_operator_greenlights_muscriptor_restart": {
            "step_1": "Rerun scripts/v3_spine/muscriptor_operator_section_wig.py under BLAS pins.",
            "step_2": "Run canonicalize / merge / render / vocals-overlay / mix-match / deliver / panel scripts (all present under scripts/v3_spine/*_wig.py).",
            "step_3": "Emit final V3_FOCUS_SONG_LANDS_pending_operator or PARTIAL/FAILS honestly per rubric_v2.",
        },
    }
    out = DEL_DIR / "verdict.json"
    out.write_text(json.dumps(verdict, indent=2, sort_keys=True))
    print(f"wrote {out}")
    print(f"verdict = {verdict['verdict']}")
    print(f"rubric three-way chain holds: {verdict['rubric_hash_v2_three_way_chain_holds']}")
    print(f"blocked_on_operator: {verdict['blocked_on_operator']}")
    print(f"blocked_on_muscriptor_completion: {verdict['blocked_on_muscriptor_completion']}")

if __name__ == "__main__":
    main()
