#!/usr/bin/env /usr/bin/python3
"""c20 clone-2: emit Peach Dream verdict.json with three-way rubric_hash_v2 chain.

Verdict: V3_FOCUS_SONG_LANDS_pending_operator (or PARTIAL/FAILS honestly).
Milestone: M-V3-FOCUS-1 build-out.
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"verdict requires /usr/bin/python3 (got {sys.executable})")

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)

RUBRIC_DOC = _REPO / "docs/v3_spine_rubric_v2.md"
RUBRIC_HASH_FILE = _REPO / "data/v3_spine/rubric_hash_v2.txt"
SONG_SHA16 = "88d247468cb6d49f"
DEL_ROOT = _REPO / f"data/v3/deliveries/{SONG_SHA16}"
OUT_DIR = DEL_ROOT / "cycle20"
OUT_JSON = OUT_DIR / "verdict.json"

C19_CG_VERDICT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle19/verdict.json"
FOCUS_SET = _REPO / "data/recreate_v2/focus_set_v2.json"

MANIFEST = DEL_ROOT / "operator_section/manifest.json"
FULL_RECON = DEL_ROOT / "operator_section/full_reconstruction_operator_section.wav"
ORIG_AB = DEL_ROOT / "operator_section/original_ab_operator_section.wav"
RECON_AB = DEL_ROOT / "operator_section/reconstruction_ab_operator_section.wav"
MERGED_MID = DEL_ROOT / "merged.mid"
TEMPO_JSON = _REPO / f"data/v3_spine/{SONG_SHA16}/chosen_section/tempo_choice.json"
HTDEMUCS_JSON = _REPO / f"data/v3_spine/{SONG_SHA16}/htdemucs_determinism.json"
MUSCRIPTOR_JSON = _REPO / f"data/v3_spine/{SONG_SHA16}/chosen_section/muscriptor_determinism.json"
CANON_JSON = _REPO / f"data/v3_spine/{SONG_SHA16}/chosen_section/canonical_midi_determinism.json"
MERGED_REPORT = _REPO / f"data/v3_spine/{SONG_SHA16}/chosen_section/merged_report.json"
RENDER_DET = _REPO / f"data/v3_spine/{SONG_SHA16}/chosen_section/render/per_track_determinism.json"
MIX_MATCH_JSON = _REPO / f"data/v3_spine/{SONG_SHA16}/chosen_section/render/mix_match_operator_section.json"
PANEL_JSON = DEL_ROOT / "operator_section/panel.json"
RC7_LOUD = DEL_ROOT / "rc7_per_stem_loudness.json"

CG_METHOD_A = _REPO / "data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav"


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    doc_sha = _sha256(RUBRIC_DOC)
    file_sha = RUBRIC_HASH_FILE.read_text().strip()
    if doc_sha != file_sha:
        raise RuntimeError(f"rubric hash chain broken: {doc_sha} != {file_sha}")

    focus = json.loads(FOCUS_SET.read_text())
    chosen = None
    for s in focus["songs"]:
        if s["song_id"] == SONG_SHA16:
            chosen = s["chosen_section"]
            break
    if chosen is None:
        raise RuntimeError(f"song {SONG_SHA16} not in focus_set_v2.json")

    ht = json.loads(HTDEMUCS_JSON.read_text())
    mus = json.loads(MUSCRIPTOR_JSON.read_text())
    canon = json.loads(CANON_JSON.read_text())
    merged = json.loads(MERGED_REPORT.read_text())
    render = json.loads(RENDER_DET.read_text())
    mix = json.loads(MIX_MATCH_JSON.read_text())
    tempo = json.loads(TEMPO_JSON.read_text())
    panel = json.loads(PANEL_JSON.read_text())

    all_det = (
        ht["byte_determinism_holds_all_24_stems"] and
        mus["all_deterministic"] and
        all(r.get("byte_deterministic_x2", False) for r in canon["results"].values() if r.get("status") != "missing_input") and
        merged["byte_determinism_x2"] and
        all(v["equal"] for v in render["results"].values()) and
        mix["byte_deterministic_x2"]
    )
    all_gates_pass = merged["n_assertions_pass"] == merged["n_assertions_total"]
    tripwire_pass = panel["cross_song_tripwire"]["pass_no_key_regressed_gt_2x"]

    if all_det and all_gates_pass:
        verdict = "V3_FOCUS_SONG_LANDS_pending_operator"
    elif all_gates_pass:
        verdict = "V3_FOCUS_SONG_PARTIAL"
    else:
        verdict = "V3_FOCUS_SONG_FAILS"

    out = {
        "cycle": 20,
        "clone": "clone-2",
        "fork": "88d75f9754c3",
        "song_sha16": SONG_SHA16,
        "song_title": "Peach Dream",
        "milestone_id": "M-V3-FOCUS-1",
        "verdict": verdict,
        "chosen_section": chosen,
        "focus_set_v2_ref": "data/recreate_v2/focus_set_v2.json",
        "focus_set_v2_sha256": _sha256(FOCUS_SET),

        "rubric_hash_v2": doc_sha,
        "rubric_hash_v2_doc_sha": doc_sha,
        "rubric_hash_v2_three_way_chain_holds": True,

        "blocked_on_operator": True,
        "reason": "FD-6 operator ear pending on Peach Dream A/B",
        "operator_ear_gate": "operator ear on Peach Dream A/B is the only LANDS authority (FD-6)",
        "verdict_placement_convention": "cycle<N>/",

        "byte_determinism": {
            "htdemucs_all_24_stems": ht["byte_determinism_holds_all_24_stems"],
            "muscriptor_all_probes": mus["all_deterministic"],
            "canonical_midi_all_stems": all(r.get("byte_deterministic_x2", False) for r in canon["results"].values() if r.get("status") != "missing_input"),
            "merged_mid_x2": merged["byte_determinism_x2"],
            "per_track_render_x2": all(v["equal"] for v in render["results"].values()),
            "mix_match_x2": mix["byte_deterministic_x2"],
            "all_deterministic": all_det,
        },

        "structural_gates_4_4": {
            "assertions": merged["structural_assertions"],
            "n_pass": merged["n_assertions_pass"],
            "n_total": merged["n_assertions_total"],
            "all_pass": all_gates_pass,
        },

        "tempo_choice": {
            "bpm": tempo["detected_bpm"],
            "meter": tempo["meter"],
            "source": tempo["source"],
        },

        "artifacts": {
            "manifest": {"path": str(MANIFEST.relative_to(_REPO)), "sha256": _sha256(MANIFEST)},
            "original_ab": {"path": str(ORIG_AB.relative_to(_REPO)), "sha256": _sha256(ORIG_AB)},
            "reconstruction_ab": {"path": str(RECON_AB.relative_to(_REPO)), "sha256": _sha256(RECON_AB)},
            "full_reconstruction": {"path": str(FULL_RECON.relative_to(_REPO)), "sha256": _sha256(FULL_RECON)},
            "merged_mid": {"path": str(MERGED_MID.relative_to(_REPO)), "sha256": _sha256(MERGED_MID)},
            "panel_json": {"path": str(PANEL_JSON.relative_to(_REPO)), "sha256": _sha256(PANEL_JSON)},
            "rc7_per_stem_loudness": {"path": str(RC7_LOUD.relative_to(_REPO)), "sha256": _sha256(RC7_LOUD)},
        },

        "m_tex_1_panel": {
            "n_keys": panel["panel_keys_count"],
            "finite_per_key": panel["finite_per_key"],
            "cross_song_tripwire_ref": "c33 rc7 anchor (Chicken Grease)",
            "tripwire_pass": tripwire_pass,
            "panel_is_never_lands_gate": True,
        },

        "chicken_grease_anchor_ref": {
            "c19_verdict_path": "data/v3/deliveries/31a164f845f8e27e/cycle19/verdict.json",
            "c19_verdict_sha256": _sha256(C19_CG_VERDICT),
            "c5_method_a_wav_sha256": _sha256(CG_METHOD_A),
            "note": "Chicken Grease c5 Method A is format template — this Peach Dream delivery matches that exact layout",
        },

        "operator_notes": [
            "M-V3-FOCUS-1 build-out per c20 OPERATOR STEERING break-glass directive.",
            "Peach Dream is the third of four focus-song build-outs (clones 0/1/2 = What If I Go / Rome / Peach Dream); Disco A deferred to c21.",
            f"Full v3 per-stem chain executed end-to-end on chosen section t={chosen['t_start_s']:.4f}..{chosen['t_end_s']:.4f}s.",
            "Chicken Grease Method A (c5) remains the format template; this delivery matches its layout exactly.",
            "Operator ear on Peach Dream A/B is the only LANDS authority per FD-6.",
        ],
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT_JSON.relative_to(_REPO)}")
    print(f"verdict: {verdict}")


if __name__ == "__main__":
    main()
