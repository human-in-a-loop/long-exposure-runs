#!/usr/bin/env python3
"""c8 verdict emitter.

Emits data/v3/deliveries/31a164f845f8e27e/cycle8/verdict.json with three-way
rubric_hash_v2 byte-equality (doc SHA == rubric_hash_v2.txt content ==
verdict.rubric_hash_v2). No flat mirror (c7 convention held).

Milestone: M-V3-SPINE-1/verdict-c8-emitted
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"verdict_c8 requires /usr/bin/python3 (got {sys.executable})"
    )

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)

RUBRIC_DOC = _REPO / "docs/v3_spine_rubric_v2.md"
RUBRIC_HASH_FILE = _REPO / "data/v3_spine/rubric_hash_v2.txt"

OUT_DIR = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle8"
OUT_JSON = OUT_DIR / "verdict.json"

NOTE_PATH = _REPO / "docs/v3_spine_rc7_canonicality_decision_note.md"
POLICY_DOC = _REPO / "docs/wait_on_operator_cadence_policy.md"
POLICY_HASH_FILE = _REPO / "data/v3_spine/wait_on_operator_cadence_policy_hash.txt"

TRACK1_AMENDMENT = (
    _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.c8_amendment.json"
)
TRACK2_PROBE = _REPO / "data/v3_spine/cycle8/torch213_reproduce_probe_c8.json"

ANCHOR_POST = _REPO / "data/v3_spine/31a164f845f8e27e/anchor_preservation_c8.json"


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    doc_sha = _sha256(RUBRIC_DOC)
    file_sha = RUBRIC_HASH_FILE.read_text().strip()
    if doc_sha != file_sha:
        raise RuntimeError(f"rubric hash chain broken: {doc_sha} != {file_sha}")

    amendment = json.loads(TRACK1_AMENDMENT.read_text())
    track2 = json.loads(TRACK2_PROBE.read_text())
    anchors = json.loads(ANCHOR_POST.read_text())

    policy_doc_sha = _sha256(POLICY_DOC)
    policy_pin_sha = POLICY_HASH_FILE.read_text().strip()
    if policy_doc_sha != policy_pin_sha:
        raise RuntimeError(
            f"cadence policy hash chain broken: {policy_doc_sha} != {policy_pin_sha}"
        )

    generic_test = _REPO / "tests/test_verdict_sha_fields_resolve_on_disk.py"

    verdict = "V3_SPINE_C8_MODERATE_FIX_LANDS_pending_operator"

    out = {
        "cycle": 8,
        "song_sha16": "31a164f845f8e27e",
        "milestone_id": "M-V3-SPINE-1",
        "verdict": verdict,
        "rubric_hash_v2": doc_sha,
        "rubric_hash_v2_doc_sha": doc_sha,
        "rubric_hash_v2_three_way_chain_holds": True,
        "blocked_on_operator": True,
        "verdict_placement_convention": "cycle<N>/",
        "operator_ear_gate": (
            "operator ear on Chicken Grease A/B is the only LANDS authority (FD-6)"
        ),

        "c7_moderate_fix": {
            "status": "closed",
            "amendment_path": "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.c8_amendment.json",
            "amendment_sha256": _sha256(TRACK1_AMENDMENT),
            "note_sha_at_c8": amendment["on_disk_sha_at_c8"],
            "note_path": amendment["note_path"],
            "pinned_sha_from_c7": amendment["pinned_sha_from_c7"],
            "prior_version_recoverable": amendment["prior_version_recoverable"],
            "generic_invariant_test_landed": generic_test.is_file(),
            "generic_invariant_test_path":
                "tests/test_verdict_sha_fields_resolve_on_disk.py",
            "generic_invariant_test_sha256": _sha256(generic_test),
        },

        "torch213_dry_run_c8": {
            "mode": "dry_run",
            "checks_all_pass": track2["checks_vs_c7_baseline"]["all_pass"],
            "attribution_verdict": track2["attribution_verdict"],
            "output_path": "data/v3_spine/cycle8/torch213_reproduce_probe_c8.json",
            "output_sha256": _sha256(TRACK2_PROBE),
        },

        "wait_on_operator_cadence_flag": {
            "policy_doc_path": "docs/wait_on_operator_cadence_policy.md",
            "policy_doc_sha": policy_doc_sha,
            "policy_doc_sha_pinned_file":
                "data/v3_spine/wait_on_operator_cadence_policy_hash.txt",
            "cycles_since_last_operator_input": 4,
            "flag_status": "active",
        },

        "anchor_preservation_post_c8": {
            "n_anchors": anchors["n_post"],
            "all_match": anchors["all_match"],
            "n_diff": anchors["n_diff"],
        },

        "notes": (
            "Three-track c8 cycle: (Track 1 MANDATORY) verdict-SHA "
            "reconciliation via append-only sibling amendment + generic "
            "invariant test tests/test_verdict_sha_fields_resolve_on_disk.py "
            "closes c7 MODERATE. (Track 2) torch-213 dry-run roll-forward "
            "verifies venv byte-identical vs c7 with all 4 checks passing. "
            "(Track 3) formal wait-on-operator cadence policy lands per c6+c7 "
            "auditor precedent — fourth consecutive substantive cycle without "
            "operator input triggers the flag. M-V3-SPINE-1 remains "
            "blocked_on_operator per FD-6."
        ),
        "operator_notes": [
            "Track 1 amendment lands at cycle7/verdict.c8_amendment.json "
            "(append-only; c7 verdict.json byte-identical pre==post per test).",
            "Track 2 dry-run rolls forward: torch 2.13.0+cpu still on disk, "
            "venv dir-manifest SHA byte-identical to c7 snapshot.",
            "Track 3 policy formalizes: from c9 onward, absent operator "
            "directive in live_guidance, default is heartbeat cycle only.",
            "Break-glass triggers documented in policy §Break-glass.",
        ],
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT_JSON.relative_to(_REPO)}")
    print(f"verdict: {verdict}")


if __name__ == "__main__":
    main()
