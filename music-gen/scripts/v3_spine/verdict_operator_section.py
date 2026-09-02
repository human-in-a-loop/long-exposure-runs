#!/usr/bin/env python3
"""c5 Track B: operator-section verdict under rubric-v2."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

SEC = Path("data/v3_spine/31a164f845f8e27e/operator_section")
DEL = Path("data/v3/deliveries/31a164f845f8e27e/operator_section")


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    doc = Path("docs/v3_spine_rubric_v2.md")
    rh = Path("data/v3_spine/rubric_hash_v2.txt")
    doc_sha = sha(doc)
    rh_txt = rh.read_text().strip()

    htdemucs = json.loads((SEC / "htdemucs_determinism.json").read_text())
    mus = json.loads((SEC / "muscriptor_determinism.json").read_text())
    canon = json.loads((SEC / "canonical_midi_determinism.json").read_text())
    merged = json.loads((SEC / "merged_report.json").read_text())
    per_track = json.loads((SEC / "render" / "per_track_determinism.json").read_text())
    mix = json.loads((SEC / "render" / "mix_match_operator_section.json").read_text())
    panel = json.loads((DEL / "panel.json").read_text())
    manifest = json.loads((DEL / "manifest.json").read_text())
    envaudit = json.loads(Path("data/v3_spine/venv_delta_audit.json").read_text())
    probe = json.loads(Path("data/v3_spine/c3_guitar_reproduce_probe.json").read_text())

    canon_all = all(r.get("byte_deterministic_x2", False) for r in canon["results"].values())
    per_track_all = all(r["equal"] for r in per_track["results"].values())
    fullrecon_det = mix["byte_deterministic_x2"]
    htdemucs_all = htdemucs["byte_determinism_holds"]
    mus_all = mus["all_deterministic"]

    delivery_ok = all([
        manifest["artifacts"]["original_ab_operator_section_wav"]["peak"] > 1e-4,
        manifest["artifacts"]["reconstruction_ab_operator_section_wav"]["peak"] > 1e-4,
        manifest["artifacts"]["full_reconstruction_operator_section_wav"]["peak"] > 1e-4,
    ])
    panel_ok = panel["panel_keys_count"] >= 8 and all(panel["finite_per_key"].values())
    tripwire_ok = panel["cross_window_tripwire"]["pass_no_key_regressed_gt_2x"]
    struct = merged["structural_assertions"]
    struct_ok = all(struct.values())

    all_pass = (
        canon_all and per_track_all and fullrecon_det and htdemucs_all and mus_all
        and delivery_ok and panel_ok and tripwire_ok and struct_ok
    )
    verdict = ("V3_SPINE_OPERATOR_SECTION_LANDS_pending_operator" if all_pass
               else "V3_SPINE_OPERATOR_SECTION_PARTIAL")

    failures = []
    if not htdemucs_all:
        failures.append({"kind": "htdemucs_operator_section_nondeterministic",
                         "mismatches": htdemucs["mismatch_stems"]})
    if not mus_all:
        failures.append({"kind": "muscriptor_operator_section_nondeterministic",
                         "n_probes": mus["n_probes"], "n_det": mus["n_deterministic"]})
    if not canon_all:
        failures.append({"kind": "canonical_midi_operator_section_nondeterministic",
                         "per_stem": {s: r.get("byte_deterministic_x2") for s, r in canon["results"].items()}})
    if not per_track_all:
        failures.append({"kind": "per_track_wav_operator_section_nondeterministic",
                         "per_track": {s: r["equal"] for s, r in per_track["results"].items()}})
    if not fullrecon_det:
        failures.append({"kind": "full_reconstruction_operator_section_wav_nondeterministic"})
    if not struct_ok:
        failures.append({"kind": "merged_structural_gate_fails",
                         "failed": [k for k, v in struct.items() if not v]})
    if not panel_ok:
        failures.append({"kind": "panel_not_8_finite"})
    if not tripwire_ok:
        failures.append({"kind": "cross_window_tripwire_regressed",
                         "per_key": panel["cross_window_tripwire"]["per_key"]})

    env_attr = probe["attribution_verdict"]

    payload = {
        "schema_version": 1,
        "cycle": 5,
        "song_sha16": "31a164f845f8e27e",
        "song_title": "Chicken Grease",
        "section": "operator_section_t_233.63918_to_263.63918s",
        "verdict": verdict,
        "blocked_on_operator": True,
        "rubric_hash_v2": rh_txt,
        "rubric_hash_v2_doc_sha": doc_sha,
        "rubric_hash_v2_three_way_chain_holds": rh_txt == doc_sha,
        "sub_clause_status": {
            "a_delivery_present_nonsilent": delivery_ok,
            "b_i_htdemucs_operator_section_det_x2": htdemucs_all,
            "b_ii_muscriptor_json_operator_section_det_x2": mus_all,
            "b_iii_canonical_midi_operator_section_det_x2": canon_all,
            "b_iv_per_track_wav_det_x2": per_track_all,
            "b_v_full_reconstruction_wav_det_x2": fullrecon_det,
            "c_panel_finite_and_tripwire_holds": {"panel_ok": panel_ok, "tripwire_ok": tripwire_ok},
            "d_structural_gates_on_merged_mid": struct,
            "f_blocked_on_operator": True,
        },
        "env_drift_track": {
            "audit_ref": "data/v3_spine/venv_delta_audit.json",
            "audit_baseline_established": envaudit["baseline_established"],
            "probe_ref": "data/v3_spine/c3_guitar_reproduce_probe.json",
            "probe_status": probe["probe_status"],
            "attribution_verdict": env_attr,
        },
        "failures": failures,
        "operator_notes": [
            "Cycle 5 runs the full pipeline on the operator's D1-chosen "
            "section t=233.63918..263.63918s. c4 A/B (t=0..30s) preserved "
            "READ-ONLY at data/v3/deliveries/31a164f845f8e27e/{original,reconstruction}_ab.wav.",
            f"Env-drift audit: baseline_established={envaudit['baseline_established']}; "
            f"c3-guitar-reproduce probe: {probe['probe_status']} (attribution={env_attr}).",
            "Two A/B pairs available to operator: c4's 0..30s A/B (compat window) and "
            "c5's operator-section A/B (D1-chosen peak+exposed section).",
        ],
    }
    (DEL / "verdict.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"verdict={verdict} chain_holds={payload['rubric_hash_v2_three_way_chain_holds']} "
          f"n_failures={len(failures)}")


if __name__ == "__main__":
    main()
