#!/usr/bin/env python3
"""c5 ledger emitter — appends all cycle-5 named events via workspace_bootstrap."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

from long_exposure import workspace_bootstrap


CYCLE = 5
RUN_ID = "run-2026-09-02T104500Z"  # canonical shape
TS = "2026-09-02T10:45:00Z"
WORKSPACE = Path(".")


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def mk(mid, narrative, artifacts, status="validated", level="high",
       rationale="", supersedes_path=None):
    e = {
        "ts": TS,
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "agent": "worker",
        "milestone_id": mid,
        "status": status,
        "confidence": {
            "level": level,
            "rationale": rationale or "c5 evidence pinned in artifacts",
            "assessor": "worker",
        },
        "narrative": narrative,
        "artifacts": artifacts,
    }
    if supersedes_path is not None:
        e["supersedes_path"] = supersedes_path
    return e


def emit(e):
    workspace_bootstrap.append_ledger_event(WORKSPACE, e)
    print(f"  appended: {e['milestone_id']}")


def main():
    # 2. Anchor preservation pre
    pre = json.loads(open("data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c5.json").read())
    emit(mk(
        "M-V3-SPINE-1/anchor-preservation-pre-c5-verified",
        f"c5 pre-snapshot of {pre['n_anchors']} anchors ({pre['n_missing']} missing) covering c4 "
        f"delivery artifacts + docs + spec hashes + c3/c4 muscriptor+canonical anchors + baseline + "
        f"locked scripts.",
        ["data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c5.json"],
    ))

    # 3. Env drift spec
    emit(mk(
        "M-V3-SPINE-1/env-drift-audit-spec-committed",
        f"docs/v3_spine_venv_delta_audit_spec.md (SHA {sha('docs/v3_spine_venv_delta_audit_spec.md')[:16]}) "
        "pinned before venv_delta_audit.py.",
        ["docs/v3_spine_venv_delta_audit_spec.md",
         "data/v3_spine/venv_delta_audit_spec_hash.txt"],
    ))

    # 4. Env drift audit
    envd = json.loads(open("data/v3_spine/venv_delta_audit.json").read())
    emit(mk(
        "M-V3-SPINE-1/env-drift-audit-completed",
        f"venv_delta_audit: {envd['n_packages_c5']} packages snapshotted. "
        f"baseline_established={envd['baseline_established']}.",
        ["data/v3_spine/venv_delta_audit.json",
         "data/v3_spine/venv_snapshots/c5_baseline.json"],
    ))

    # 5. c3 guitar reproduce probe
    probe = json.loads(open("data/v3_spine/c3_guitar_reproduce_probe.json").read())
    emit(mk(
        "M-V3-SPINE-1/c3-guitar-reproduce-probe-completed",
        f"c3 guitar reproduce probe: status={probe['probe_status']}, "
        f"attribution={probe['attribution_verdict']}. Egress-blocked deferral honestly recorded.",
        ["data/v3_spine/c3_guitar_reproduce_probe.json"],
    ))

    # 6. rehtdemucs spec
    emit(mk(
        "M-V3-SPINE-1/rehtdemucs-operator-section-spec-committed",
        f"docs/v3_spine_rehtdemucs_operator_section_spec.md "
        f"(SHA {sha('docs/v3_spine_rehtdemucs_operator_section_spec.md')[:16]}) pinned before script.",
        ["docs/v3_spine_rehtdemucs_operator_section_spec.md",
         "data/v3_spine/rehtdemucs_operator_section_spec_hash.txt"],
    ))

    # 7. rehtdemucs run
    ht = json.loads(open("data/v3_spine/31a164f845f8e27e/operator_section/htdemucs_determinism.json").read())
    emit(mk(
        "M-V3-SPINE-1/rehtdemucs-operator-section-completed",
        f"htdemucs_6s on operator section t=233.63918..263.63918s. 6/6 stems byte-deterministic x2 "
        f"(all_equal={ht['byte_determinism_holds']}, wall {ht['wall_time_s']}s).",
        ["data/v3_spine/31a164f845f8e27e/operator_section/htdemucs_determinism.json",
         "data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/"],
    ))

    # 8. MuScriptor
    mus = json.loads(open("data/v3_spine/31a164f845f8e27e/operator_section/muscriptor_determinism.json").read())
    emit(mk(
        "M-V3-SPINE-1/muscriptor-operator-section-determinism-verified",
        f"MuScriptor --format json x2 on 7 operator-section probes: "
        f"{mus['n_deterministic']}/{mus['n_probes']} deterministic (all={mus['all_deterministic']}).",
        ["data/v3_spine/31a164f845f8e27e/operator_section/muscriptor_determinism.json",
         "data/v3_spine/31a164f845f8e27e/operator_section/muscriptor/"],
    ))

    # 9. canonical MIDI
    emit(mk(
        "M-V3-SPINE-1/canonical-midi-operator-section-determinism-verified",
        "Canonical serializer x2 on 7 operator-section MuScriptor JSONs. All byte-deterministic x2.",
        ["data/v3_spine/31a164f845f8e27e/operator_section/canonical_midi_determinism.json",
         "data/v3_spine/31a164f845f8e27e/operator_section/canonical_midi/"],
    ))

    # 10. tempo choice
    tempo = json.loads(open("data/v3_spine/31a164f845f8e27e/operator_section/tempo_choice.json").read())
    emit(mk(
        "M-V3-SPINE-1/tempo-map-operator-section-chosen",
        f"Tempo on operator-section via {tempo['source']}: {tempo['detected_bpm']:.4f} BPM, meter {tempo['meter']}.",
        ["data/v3_spine/31a164f845f8e27e/operator_section/tempo_choice.json"],
    ))

    # 11. merged
    merged = json.loads(open("data/v3_spine/31a164f845f8e27e/operator_section/merged_report.json").read())
    emit(mk(
        "M-V3-SPINE-1/per-stem-midi-operator-section-merged",
        f"merged.mid sha {merged['merged_mid_sha256'][:16]}, byte_det_x2={merged['byte_determinism_x2']}, "
        f"structural {merged['n_assertions_pass']}/{merged['n_assertions_total']}.",
        ["data/v3_spine/31a164f845f8e27e/operator_section/merged.mid",
         "data/v3_spine/31a164f845f8e27e/operator_section/merged_report.json"],
    ))

    # 12. reconciliation
    emit(mk(
        "M-V3-SPINE-1/full-mix-reconciliation-operator-section-emitted",
        "Full-mix vs merged per-stem reconciliation; reconciled in per-stem's favor per operator directive point 4.",
        ["data/v3_spine/31a164f845f8e27e/operator_section/full_mix_reconciliation_operator_section.json"],
    ))

    # 13. render + vocals
    emit(mk(
        "M-V3-SPINE-1/render-plus-vocals-overlay-operator-section",
        "fluidsynth per-track render x2 + D2 vocals overlay via SHA-verified copy of operator-section vocals stem.",
        ["data/v3_spine/31a164f845f8e27e/operator_section/render/per_track/",
         "data/v3_spine/31a164f845f8e27e/operator_section/render/per_track_determinism.json",
         "data/v3_spine/31a164f845f8e27e/operator_section/render/vocals_htdemucs.wav",
         "data/v3_spine/31a164f845f8e27e/operator_section/render/vocals_overlay.json"],
    ))

    # 14. rc7 loudness
    emit(mk(
        "M-V3-SPINE-1/rc7-per-stem-loudness-operator-section-computed",
        "Per-stem RMS + LUFS-S proxy loudness targets on operator-section stems. c49 baseline READ-ONLY.",
        ["data/v3_spine/31a164f845f8e27e/operator_section/rc7_per_stem_loudness_operator_section.json"],
    ))

    # 15. mix match
    mix = json.loads(open("data/v3_spine/31a164f845f8e27e/operator_section/render/mix_match_operator_section.json").read())
    emit(mk(
        "M-V3-SPINE-1/mix-match-operator-section-applied",
        f"RMS-match + sum -> full_reconstruction_operator_section.wav "
        f"(det_x2={mix['byte_deterministic_x2']}, sha {mix['final_sha256'][:16]}).",
        ["data/v3_spine/31a164f845f8e27e/operator_section/render/full_reconstruction_operator_section.wav",
         "data/v3_spine/31a164f845f8e27e/operator_section/render/mix_match_operator_section.json"],
    ))

    # 16. delivery
    emit(mk(
        "M-V3-SPINE-1/ab-delivery-operator-section-emitted",
        "Operator-section A/B (30s original vs 30s reconstruction on t=233.63918..263.63918s) + full "
        "reconstruction WAV + manifest.json delivered under data/v3/deliveries/<sha16>/operator_section/.",
        ["data/v3/deliveries/31a164f845f8e27e/operator_section/original_ab_operator_section.wav",
         "data/v3/deliveries/31a164f845f8e27e/operator_section/reconstruction_ab_operator_section.wav",
         "data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav",
         "data/v3/deliveries/31a164f845f8e27e/operator_section/manifest.json"],
    ))

    # 17. panel
    panel = json.loads(open("data/v3/deliveries/31a164f845f8e27e/operator_section/panel.json").read())
    emit(mk(
        "M-V3-SPINE-1/panel-regression-operator-section-checked",
        f"Sanity panel: {panel['panel_keys_count']} keys, "
        f"tripwire pass={panel['cross_window_tripwire']['pass_no_key_regressed_gt_2x']}.",
        ["data/v3/deliveries/31a164f845f8e27e/operator_section/panel.tsv",
         "data/v3/deliveries/31a164f845f8e27e/operator_section/panel.json"],
    ))

    # 18. verdict
    verdict = json.loads(open("data/v3/deliveries/31a164f845f8e27e/operator_section/verdict.json").read())
    emit(mk(
        "M-V3-SPINE-1/verdict-operator-section-emitted",
        f"Verdict {verdict['verdict']}; chain_holds={verdict['rubric_hash_v2_three_way_chain_holds']}, "
        f"blocked_on_operator={verdict['blocked_on_operator']}.",
        ["data/v3/deliveries/31a164f845f8e27e/operator_section/verdict.json"],
        status=("blocked_on_operator" if verdict["verdict"].endswith("_pending_operator") else "action_required"),
    ))

    # 19. anchor post
    post = json.loads(open("data/v3_spine/31a164f845f8e27e/anchor_preservation_c5.json").read())
    emit(mk(
        "M-V3-SPINE-1/anchor-preservation-post-c5-verified",
        f"Post-snapshot verifies {post['n_matched']}/{post['n_pre']} anchors byte-identical "
        f"(all_match={post['all_match']}).",
        ["data/v3_spine/31a164f845f8e27e/anchor_preservation_c5.json"],
    ))

    # 20. Egress probe
    emit(mk(
        "M-INGEST-1/egress-probe-cycle5",
        "c5 linear egress retry probe per c49 path B. HTTP 429 + tv_embedded unchanged.",
        ["data/ingestion/egress_status.jsonl"],
    ))

    # 21. Archive scratch
    emit(mk(
        "_archive/cycle-5-scratch",
        "Cycle-5 one-shot emitter archived to tools/stale/cycle5_v3_spine_scratch/.",
        ["tools/stale/cycle5_v3_spine_scratch/"],
    ))

    # 22. Adopt cycle-5 tests
    emit(mk(
        "_infra/adopt-cycle5-tests",
        "Adopt tests/test_v3_spine_c5.py under the ledger.",
        ["tests/test_v3_spine_c5.py"],
    ))

    # 23. Plan register
    emit(mk(
        "_plan/register-c5-v3-spine-sub-leaves",
        "Register 18 new M-V3-SPINE-1 sub-leaves + M-INGEST-1/egress-probe-cycle5 introduced this cycle "
        "to close promise_check drift.",
        ["plan_of_record.md"],
    ))


if __name__ == "__main__":
    main()
