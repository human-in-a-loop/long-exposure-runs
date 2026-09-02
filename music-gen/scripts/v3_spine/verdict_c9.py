#!/usr/bin/env python3
"""c9 heartbeat verdict emitter.

Emits data/v3/deliveries/31a164f845f8e27e/cycle9/verdict.json with three-way
rubric_hash_v2 byte-equality (doc SHA == rubric_hash_v2.txt content ==
verdict.rubric_hash_v2). Preserves cycle<N>/ placement convention (no flat mirror).

Milestone: M-V3-SPINE-1/verdict-c9-emitted

Cadence: HEARTBEAT per c8-landed wait-on-operator policy
(docs/wait_on_operator_cadence_policy.md, pinned SHA in
data/v3_spine/wait_on_operator_cadence_policy_hash.txt). Fifth consecutive
substantive-track-absent cycle (c5..c9). No fourth substantive M-V3-SPINE
track manufactured this cycle.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"verdict_c9 requires /usr/bin/python3 (got {sys.executable})"
    )

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)

RUBRIC_DOC = _REPO / "docs/v3_spine_rubric_v2.md"
RUBRIC_HASH_FILE = _REPO / "data/v3_spine/rubric_hash_v2.txt"

OUT_DIR = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle9"
OUT_JSON = OUT_DIR / "verdict.json"

POLICY_DOC = _REPO / "docs/wait_on_operator_cadence_policy.md"
POLICY_HASH_FILE = _REPO / "data/v3_spine/wait_on_operator_cadence_policy_hash.txt"

TORCH_PROBE = _REPO / "data/v3_spine/cycle9/torch213_reproduce_probe_c9.json"
ANCHOR_POST = _REPO / "data/v3_spine/cycle9/anchor_preservation_c9.json"

C8_VERDICT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle8/verdict.json"


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

    verdict = "V3_SPINE_C9_HEARTBEAT_pending_operator"

    out = {
        "cycle": 9,
        "song_sha16": "31a164f845f8e27e",
        "milestone_id": "M-V3-SPINE-1",
        "verdict": verdict,
        "cadence_mode": "heartbeat",
        "cadence_policy_ref": "docs/wait_on_operator_cadence_policy.md",
        "cadence_policy_sha": policy_doc_sha,
        "cycles_since_last_operator_input": 5,

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
            "output_path": "data/v3_spine/cycle9/torch213_reproduce_probe_c9.json",
            "output_sha256": _sha256(TORCH_PROBE),
        },

        "anchor_preservation_post_c9": {
            "n_anchors": anchors["n_post"],
            "all_match": anchors["all_match"],
            "n_diff": anchors["n_diff"],
        },

        "c8_verdict_ref": {
            "path": "data/v3/deliveries/31a164f845f8e27e/cycle8/verdict.json",
            "sha256": _sha256(C8_VERDICT),
        },

        "operator_notes": [
            "c5-c8 substantive-track LANDS_pending_operator chain intact; "
            "c9 is heartbeat per c8-landed cadence policy — no fourth "
            "substantive M-V3-SPINE track manufactured this cycle.",
            "Operator ear on data/v3/deliveries/31a164f845f8e27e/operator_section/"
            "{original_ab,reconstruction_ab}_operator_section.wav (Method A, c5) "
            "OR data/v3_spine/rc7_v2_v3_paths/rc7_v2_v3_paths_full_reconstruction.wav "
            "(Method B, c6) OR the c4 30 s A/B remains the only advancing move.",
            "Break-glass triggers per docs/wait_on_operator_cadence_policy.md "
            "§Break-glass: operator directive in live_guidance OR auditor CRITICAL "
            "finding. Neither present this cycle.",
            "Torch-213 Mode 2 executable on operator green-light; drafted commands "
            "(binary + module form) pinned in cycle9/torch213_reproduce_probe_c9.json "
            "byte-identical to c7/c8.",
        ],

        "notes": (
            "Heartbeat cycle per c8-landed wait-on-operator cadence policy. "
            "Fifth consecutive cycle without operator input (c5→c6→c7→c8→c9). "
            "Four deliverables: torch-213 dry-run liveness roll-forward, "
            "anchor preservation pre/post (≥110 target, 116 delivered), verdict "
            "emission, housekeeping (egress-probe + archive + adopt-tests + "
            "register-sub-leaves). M-V3-SPINE-1 remains blocked_on_operator "
            "per FD-6; c5-c8 verdicts and c4-c7 LANDS_pending_operator chain "
            "intact and unchanged."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT_JSON.relative_to(_REPO)}")
    print(f"verdict: {verdict}")


if __name__ == "__main__":
    main()
