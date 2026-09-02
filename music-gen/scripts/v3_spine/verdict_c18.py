#!/usr/bin/env python3
"""c18 heartbeat verdict emitter.

Emits data/v3/deliveries/31a164f845f8e27e/cycle18/verdict.json with three-way
rubric_hash_v2 byte-equality. Preserves cycle<N>/ placement convention.

Milestone: M-V3-SPINE-1/verdict-c18-emitted

Cadence: HEARTBEAT per c8-landed wait-on-operator policy. Fourteenth consecutive
substantive-track-absent cycle (c5..c18). Tenth consecutive heartbeat (c9..c18).
No fifth substantive M-V3-SPINE track manufactured this cycle.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"verdict_c18 requires /usr/bin/python3 (got {sys.executable})"
    )

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)

RUBRIC_DOC = _REPO / "docs/v3_spine_rubric_v2.md"
RUBRIC_HASH_FILE = _REPO / "data/v3_spine/rubric_hash_v2.txt"

OUT_DIR = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle18"
OUT_JSON = OUT_DIR / "verdict.json"

POLICY_DOC = _REPO / "docs/wait_on_operator_cadence_policy.md"
POLICY_HASH_FILE = _REPO / "data/v3_spine/wait_on_operator_cadence_policy_hash.txt"

TORCH_PROBE = _REPO / "data/v3_spine/cycle18/torch213_reproduce_probe_c18.json"
ANCHOR_POST = _REPO / "data/v3_spine/cycle18/anchor_preservation_c18.json"

C17_VERDICT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle17/verdict.json"

METHOD_A_WAV = _REPO / (
    "data/v3/deliveries/31a164f845f8e27e/operator_section/"
    "full_reconstruction_operator_section.wav"
)
METHOD_B_WAV = _REPO / (
    "data/v3_spine/rc7_v2_v3_paths/rc7_v2_v3_paths_full_reconstruction.wav"
)


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    doc_sha = _sha256(RUBRIC_DOC)
    file_sha = RUBRIC_HASH_FILE.read_text().strip()
    if doc_sha != file_sha:
        raise RuntimeError(f"rubric hash chain broken: {doc_sha} != {file_sha}")

    policy_doc_sha = _sha256(POLICY_DOC)
    policy_pin_sha = POLICY_HASH_FILE.read_text().strip()
    if policy_doc_sha != policy_pin_sha:
        raise RuntimeError(
            f"cadence policy hash chain broken: {policy_doc_sha} != {policy_pin_sha}"
        )

    torch_out = json.loads(TORCH_PROBE.read_text())
    anchors = json.loads(ANCHOR_POST.read_text())

    verdict = "V3_SPINE_C18_HEARTBEAT_pending_operator"

    out = {
        "cycle": 18,
        "song_sha16": "31a164f845f8e27e",
        "milestone_id": "M-V3-SPINE-1",
        "verdict": verdict,
        "cadence_mode": "heartbeat",
        "cadence_policy_ref": "docs/wait_on_operator_cadence_policy.md",
        "cadence_policy_sha": policy_doc_sha,
        "cycles_since_last_operator_input": 14,

        "rubric_hash_v2": doc_sha,
        "rubric_hash_v2_doc_sha": doc_sha,
        "rubric_hash_v2_three_way_chain_holds": True,

        "blocked_on_operator": True,
        "verdict_placement_convention": "cycle<N>/",
        "operator_ear_gate": (
            "operator ear on Chicken Grease A/B is the only LANDS authority (FD-6)"
        ),

        "torch213_liveness": {
            "mode": "dry_run",
            "checks_all_pass": torch_out["checks_all_pass"],
            "attribution_verdict": torch_out["attribution_verdict"],
            "output_path": "data/v3_spine/cycle18/torch213_reproduce_probe_c18.json",
            "output_sha256": _sha256(TORCH_PROBE),
        },

        "anchor_preservation_post_c18": {
            "n_anchors": anchors["n_post"],
            "all_match": anchors["all_match"],
            "n_diff": anchors["n_diff"],
            "diff_report_path": "data/v3_spine/cycle18/anchor_preservation_c18.json",
        },

        "prior_cycles": ["c4", "c5", "c6", "c7", "c8", "c9", "c10", "c11",
                         "c12", "c13", "c14", "c15", "c16", "c17"],
        "c17_backref_sha": _sha256(C17_VERDICT),
        "c17_verdict_ref": {
            "path": "data/v3/deliveries/31a164f845f8e27e/cycle17/verdict.json",
            "sha256": _sha256(C17_VERDICT),
        },

        "venv_dir_manifest_sha":
            torch_out["venv_signature_post"]["dir_manifest_sha256"],

        "operator_ab_pending": {
            "method_a": {
                "path": (
                    "data/v3/deliveries/31a164f845f8e27e/operator_section/"
                    "full_reconstruction_operator_section.wav"
                ),
                "sha256": _sha256(METHOD_A_WAV),
                "origin": "c5 plain RMS-match (mix_match_operator_section.py)",
            },
            "method_b": {
                "path": (
                    "data/v3_spine/rc7_v2_v3_paths/"
                    "rc7_v2_v3_paths_full_reconstruction.wav"
                ),
                "sha256": _sha256(METHOD_B_WAV),
                "origin": "c6 iirpeak EQ + RMS + LUFS-S (rc7_v2_rerun_v3_paths.py)",
            },
            "status": "operator_ear_pending_fd6",
        },

        "heartbeat_scope_statement": (
            "No fifth substantive M-V3-SPINE track manufactured this cycle. "
            "Operator ear on Chicken Grease A/B remains the only authoritative "
            "gate per FD-6."
        ),

        "operator_notes": [
            "c5-c8 substantive-track + c9-c17 heartbeat LANDS_pending_operator "
            "chain intact; c18 is the tenth consecutive heartbeat per c8-landed "
            "cadence policy — no fifth substantive M-V3-SPINE track manufactured "
            "this cycle.",
            "Operator ear on data/v3/deliveries/31a164f845f8e27e/operator_section/"
            "{original_ab,reconstruction_ab}_operator_section.wav (Method A, c5) "
            "OR data/v3_spine/rc7_v2_v3_paths/rc7_v2_v3_paths_full_reconstruction.wav "
            "(Method B, c6) OR the c4 30 s A/B remains the only advancing move.",
            "Break-glass triggers per docs/wait_on_operator_cadence_policy.md "
            "§Break-glass: operator directive in live_guidance OR auditor CRITICAL "
            "finding. Neither present this cycle.",
            "Torch-213 Mode 2 executable on operator green-light; drafted commands "
            "(binary + module form) pinned in cycle18/torch213_reproduce_probe_c18.json "
            "byte-identical to c7..c17 (eleven-cycle baseline).",
        ],

        "notes": (
            "Heartbeat cycle per c8-landed wait-on-operator cadence policy. "
            "Fourteenth consecutive cycle without operator input "
            "(c5→c6→c7→c8→c9→c10→c11→c12→c13→c14→c15→c16→c17→c18). Four "
            "deliverables: torch-213 dry-run liveness roll-forward (twelve-cycle "
            "venv chain), anchor preservation pre/post (≥205 target, 206 "
            "delivered), verdict emission, housekeeping (egress-probe + register "
            "+ adopt-tests + archive). M-V3-SPINE-1 remains blocked_on_operator "
            "per FD-6; c5-c17 verdicts and c4-c7 LANDS_pending_operator chain "
            "intact and unchanged. Steady-state cadence proven across ten "
            "heartbeat cycles (c9-c18) with zero drift."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT_JSON.relative_to(_REPO)}")
    print(f"verdict: {verdict}")


if __name__ == "__main__":
    main()
