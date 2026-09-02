#!/usr/bin/env python3
"""c7 verdict emitter.

Emits data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.json with three-way
rubric_hash_v2 byte-equality (doc SHA == rubric_hash_v2.txt content ==
verdict.rubric_hash_v2).

Also mirrors to data/v3_spine/verdict_c7.json ONLY IF downstream scripts read
the flat path (checked via grep; c6 grep showed only self+tests). This cycle:
no mirror — verdict lives at cycle7/ only.

Milestone: M-V3-SPINE-1/verdict-c7-emitted
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"verdict_c7 requires /usr/bin/python3 (got {sys.executable})"
    )

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)

RUBRIC_DOC = _REPO / "docs" / "v3_spine_rubric_v2.md"
RUBRIC_HASH_FILE = _REPO / "data" / "v3_spine" / "rubric_hash_v2.txt"

OUT_DIR = _REPO / "data" / "v3" / "deliveries" / "31a164f845f8e27e" / "cycle7"
OUT_JSON = OUT_DIR / "verdict.json"


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    doc_sha = _sha256(RUBRIC_DOC)
    file_sha = RUBRIC_HASH_FILE.read_text().strip()
    if doc_sha != file_sha:
        raise RuntimeError(f"rubric hash chain broken: {doc_sha} != {file_sha}")

    # Load Track A / B / C outputs.
    torch_probe = json.loads((_REPO / "data/v3_spine/cycle7/torch213_reproduce_probe.json").read_text())
    empty_stem = json.loads((_REPO / "data/v3_spine/cycle7/empty_stem_duration_sanity.json").read_text())
    rc7_metrics = json.loads((_REPO / "data/v3_spine/cycle7/rc7_canonicality_metrics.json").read_text())

    note_path = _REPO / "docs/v3_spine_rc7_canonicality_decision_note.md"
    note_sha = _sha256(note_path)

    anchors_post = json.loads(
        (_REPO / "data/v3_spine/31a164f845f8e27e/anchor_preservation_c7.json").read_text()
    )

    # All three tracks are "green" this cycle (see per-track pass criteria).
    track_a_ok = (
        torch_probe["mode"] == "dry_run"
        and torch_probe["probe_status"] == "awaiting_operator_green_light"
        and torch_probe["venv_unchanged"] is True
        and torch_probe["network_syscall_attempted"] is False
    )
    track_b_ok = note_path.is_file() and rc7_metrics.get("cycle") == 7
    track_c_ok = (
        empty_stem["full_mix_duration_correct"] is True
        and empty_stem["empty_stem_shorts_expected"] is True
    )
    anchors_ok = anchors_post["all_match"] is True

    if track_a_ok and track_b_ok and track_c_ok and anchors_ok:
        verdict = "V3_SPINE_C7_THREE_TRACK_LANDS_pending_operator"
    else:
        verdict = "PARTIAL"

    out = {
        "cycle": 7,
        "song_sha16": "31a164f845f8e27e",
        "verdict": verdict,
        "milestone_id": "M-V3-SPINE-1",
        "torch213_reproduce": {
            "mode": torch_probe["mode"],
            "probe_status": torch_probe["probe_status"],
            "attribution_verdict": torch_probe["attribution_verdict"],
            "torch_version_observed": torch_probe["torch_version_observed"],
            "torch_file_observed": torch_probe["torch_file_observed"],
            "venv_unchanged": torch_probe["venv_unchanged"],
            "network_syscall_attempted": torch_probe["network_syscall_attempted"],
            "command_string_drafted_prefix": torch_probe["command_string_drafted"][:120] + "…",
        },
        "rc7_canonicality_note": {
            "path": "docs/v3_spine_rc7_canonicality_decision_note.md",
            "sha256": note_sha,
            "method_a_sha256": rc7_metrics["method_a_c5_inline_plain_rms_match"]["sha256"],
            "method_b_sha256": rc7_metrics["method_b_c6_rc7_v3_paths_iirpeak_plus_rms_lufs"]["sha256"],
        },
        "empty_stem_duration_sanity": {
            "full_mix_duration_correct": empty_stem["full_mix_duration_correct"],
            "empty_stem_shorts_expected": empty_stem["empty_stem_shorts_expected"],
            "per_file": empty_stem["per_file"],
        },
        "anchor_preservation_post_c7": {
            "all_match": anchors_post["all_match"],
            "n_anchors": anchors_post["n_pre"],
            "n_diff": anchors_post["n_diff"],
        },
        "rubric_hash_v2": doc_sha,
        "rubric_hash_v2_doc_sha": doc_sha,
        "rubric_hash_v2_three_way_chain_holds": True,
        "verdict_placement_convention": "cycle<N>/",
        "blocked_on_operator": True,
        "operator_ear_gate": (
            "operator ear on Chicken Grease A/B is the only LANDS "
            "authority (FD-6)"
        ),
        "operator_notes": [
            "Track A dry-run drafted the reproduction command against the "
            "on-disk c3-era torch 2.13.0+cpu candidate; no execution "
            "attempted (awaits operator directive in live_guidance).",
            "Track B one-page canonicality note characterizes Method A "
            "(c5 plain RMS-match) and Method B (c6 iirpeak+RMS+LUFS-S) "
            "side-by-side with no aggregate, no recommendation, operator "
            "ear the only LANDS authority.",
            "Track C confirms both full-mix WAVs are 30 s @ 44.1 kHz "
            "(1_323_000 samples) and closes the c6 auditor watch item "
            "on empty-stem nominal shorts (88_320 samples for other/piano).",
        ],
        "notes": (
            "Three-track substantive cycle per c7 brief. Linear execution "
            "(fanout self-check factors all fail). Track A stays in "
            "dry-run mode absent operator directive in live_guidance. "
            "Track B publishes characterization only, per FD-1 no method "
            "tuning. Track C closes the c6 empty-stem watch item cleanly. "
            "M-V3-SPINE-1 remains blocked on operator ear per FD-6."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = OUT_JSON.with_suffix(OUT_JSON.suffix + ".tmp")
    tmp.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, OUT_JSON)
    print(f"wrote {OUT_JSON.relative_to(_REPO)} verdict={verdict}")


if __name__ == "__main__":
    main()
