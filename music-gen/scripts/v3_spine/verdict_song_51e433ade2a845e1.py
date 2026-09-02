#!/usr/bin/env python3
"""c20 Rome: emit data/v3/deliveries/51e433ade2a845e1/cycle20/verdict.json."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

SHA16 = "51e433ade2a845e1"
SEC = Path(f"data/v3_spine/{SHA16}/operator_section")
FULL = Path(f"data/v3_spine/{SHA16}/full_song")
DEL_ROOT = Path(f"data/v3/deliveries/{SHA16}")
DEL_OP = DEL_ROOT / "operator_section"
CYCLE_DIR = DEL_ROOT / "cycle20"


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    CYCLE_DIR.mkdir(parents=True, exist_ok=True)
    doc = Path("docs/v3_spine_rubric_v2.md")
    rh = Path("data/v3_spine/rubric_hash_v2.txt")
    doc_sha = sha(doc)
    rh_txt = rh.read_text().strip()

    htdemucs = json.loads((SEC / "htdemucs_determinism.json").read_text())
    htdemucs_full = json.loads((FULL / "htdemucs_determinism.json").read_text())
    mus = json.loads((SEC / "muscriptor_determinism.json").read_text())
    canon = json.loads((SEC / "canonical_midi_determinism.json").read_text())
    merged = json.loads((SEC / "merged_report.json").read_text())
    per_track = json.loads((SEC / "render" / "per_track_determinism.json").read_text())
    mix = json.loads((SEC / "render" / "mix_match_operator_section.json").read_text())
    panel = json.loads((DEL_ROOT / "panel.json").read_text())
    panel_op = json.loads((DEL_OP / "panel.json").read_text())
    manifest = json.loads((DEL_ROOT / "manifest.json").read_text())

    c19_ref = Path("data/v3/deliveries/31a164f845f8e27e/cycle19/verdict.json")
    c19_sha = sha(c19_ref) if c19_ref.exists() else None

    canon_all = all(r.get("byte_deterministic_x2", False) for r in canon["results"].values()
                    if r.get("status") != "missing_input")
    per_track_all = all(r["equal"] for r in per_track["results"].values())
    fullrecon_det = mix["byte_deterministic_x2"]
    htdemucs_all = htdemucs["byte_determinism_holds"]
    htdemucs_full_all = htdemucs_full["byte_determinism_holds"]
    mus_all = mus["all_deterministic"]

    delivery_ok = all([
        manifest["artifacts"]["original_ab_wav"]["peak"] > 1e-4,
        manifest["artifacts"]["reconstruction_ab_wav"]["peak"] > 1e-4,
        manifest["artifacts"]["full_reconstruction_wav"]["peak"] > 1e-4,
        manifest["artifacts"]["original_ab_operator_section_wav"]["peak"] > 1e-4,
        manifest["artifacts"]["reconstruction_ab_operator_section_wav"]["peak"] > 1e-4,
        manifest["artifacts"]["full_reconstruction_operator_section_wav"]["peak"] > 1e-4,
    ])
    panel_ok = panel["panel_keys_count"] >= 8 and all(panel["finite_per_key"].values())
    panel_op_ok = panel_op["panel_keys_count"] >= 8 and all(panel_op["finite_per_key"].values())
    struct = merged["structural_assertions"]
    struct_ok = all(struct.values())

    all_pass = (
        canon_all and per_track_all and fullrecon_det
        and htdemucs_all and htdemucs_full_all and mus_all
        and delivery_ok and panel_ok and panel_op_ok and struct_ok
    )
    verdict = ("V3_FOCUS_SONG_LANDS_pending_operator" if all_pass
               else "V3_FOCUS_SONG_PARTIAL")

    failures = []
    if not htdemucs_all:
        failures.append({"kind": "htdemucs_section_nondeterministic", "mismatches": htdemucs["mismatch_stems"]})
    if not htdemucs_full_all:
        failures.append({"kind": "htdemucs_full_song_nondeterministic", "mismatches": htdemucs_full["mismatch_stems"]})
    if not mus_all:
        failures.append({"kind": "muscriptor_nondeterministic", "n_probes": mus["n_probes"], "n_det": mus["n_deterministic"]})
    if not canon_all:
        failures.append({"kind": "canonical_midi_nondeterministic",
                         "per_stem": {s: r.get("byte_deterministic_x2") for s, r in canon["results"].items()}})
    if not per_track_all:
        failures.append({"kind": "per_track_wav_nondeterministic",
                         "per_track": {s: r["equal"] for s, r in per_track["results"].items()}})
    if not fullrecon_det:
        failures.append({"kind": "full_reconstruction_wav_nondeterministic"})
    if not struct_ok:
        failures.append({"kind": "merged_structural_gate_fails",
                         "failed": [k for k, v in struct.items() if not v]})
    if not panel_ok:
        failures.append({"kind": "panel_not_8_finite"})

    payload = {
        "schema_version": 1,
        "cycle": 20,
        "clone": "1",
        "milestone_id": "M-V3-FOCUS-1",
        "song_sha16": SHA16,
        "song_title": "Dojo Cuts - Rome",
        "song_audio_path": "corpus/ratings/5/012__gPp2KBV9zXk__Dojo_Cuts_-_Rome.mp3",
        "chosen_section": {
            "t_start_s": 62.74031746031746,
            "t_end_s": 92.74031746031747,
            "duration_s": 30.0,
            "d1_picker": "focus_set_v2 auto-picker (c50)",
        },
        "verdict": verdict,
        "blocked_on_operator": True,
        "rubric_hash_v2": rh_txt,
        "rubric_hash_v2_doc_sha": doc_sha,
        "rubric_hash_v2_three_way_chain_holds": rh_txt == doc_sha,
        "c19_backref": {
            "path": str(c19_ref),
            "sha256": c19_sha,
            "note": "Chicken Grease c19 heartbeat backref (env-drift track closed c20 per operator directive).",
        },
        "sub_clause_status": {
            "a_delivery_present_nonsilent": delivery_ok,
            "b_i_htdemucs_operator_section_det_x2": htdemucs_all,
            "b_i_htdemucs_full_song_det_x2": htdemucs_full_all,
            "b_ii_muscriptor_json_det_x2": mus_all,
            "b_iii_canonical_midi_det_x2": canon_all,
            "b_iv_per_track_wav_det_x2": per_track_all,
            "b_v_full_reconstruction_wav_det_x2": fullrecon_det,
            "c_panel_finite": {"root_panel_ok": panel_ok, "operator_section_panel_ok": panel_op_ok},
            "d_structural_gates_on_merged_mid": struct,
            "f_blocked_on_operator": True,
        },
        "sub_artifact_shas": {
            "chosen_section_original_ab": {
                "path": str(DEL_ROOT / "original_ab.wav"),
                "sha256": sha(DEL_ROOT / "original_ab.wav"),
            },
            "chosen_section_reconstruction_ab": {
                "path": str(DEL_ROOT / "reconstruction_ab.wav"),
                "sha256": sha(DEL_ROOT / "reconstruction_ab.wav"),
            },
            "full_reconstruction_wav": {
                "path": str(DEL_ROOT / "full_reconstruction.wav"),
                "sha256": sha(DEL_ROOT / "full_reconstruction.wav"),
            },
            "merged_mid": {
                "path": str(DEL_ROOT / "merged.mid"),
                "sha256": sha(DEL_ROOT / "merged.mid"),
            },
            "panel_tsv": {
                "path": str(DEL_ROOT / "panel.tsv"),
                "sha256": sha(DEL_ROOT / "panel.tsv"),
            },
            "manifest_json": {
                "path": str(DEL_ROOT / "manifest.json"),
                "sha256": sha(DEL_ROOT / "manifest.json"),
            },
        },
        "byte_determinism": {
            "htdemucs_section": htdemucs["runs"],
            "htdemucs_full_song": htdemucs_full["runs"],
            "muscriptor_probes": {n: {"run1": r["run1_json_sha256"], "run2": r["run2_json_sha256"]}
                                  for n, r in mus["probes"].items()},
            "canonical_midi": {s: {"run1": r["run1_sha256"], "run2": r["run2_sha256"]}
                               for s, r in canon["results"].items() if r.get("status") != "missing_input"},
            "per_track_wav": {s: {"run1": r["sha_r1"], "run2": r["sha_r2"]}
                              for s, r in per_track["results"].items()},
            "full_reconstruction_wav": {"run1": mix["run1_sha256"], "run2": mix["run2_sha256"], "final": mix["final_sha256"]},
        },
        "failures": failures,
        "operator_notes": [
            "Rome (sha16 51e433ade2a845e1) c20 clone-1: full v3 per-stem chain "
            "end-to-end on operator-D1-chosen section t=62.74..92.74s. Sibling of "
            "Chicken Grease c5 Method A.",
            "M-V3-FOCUS-1 batch build-out per c20 operator BREAK-GLASS directive: "
            "env-drift track closed as non_factor; four focus songs (WIG, Rome, "
            "Peach Dream, Disco A) built in parallel while Chicken Grease LANDS "
            "pending operator ear.",
            "Panel is NEVER a LANDS gate per FD-6; operator ear on chosen-section "
            "A/B WAVs is the only advancing gate.",
        ],
    }
    (CYCLE_DIR / "verdict.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"verdict={verdict} chain_holds={payload['rubric_hash_v2_three_way_chain_holds']} n_failures={len(failures)}")


if __name__ == "__main__":
    main()
