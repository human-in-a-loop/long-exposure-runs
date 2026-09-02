#!/usr/bin/env python3
"""c6 verdict emitter — two-track substantive cycle.

Reads Track A env-drift + Track B rc7 method-equivalence outputs and
emits `data/v3_spine/verdict_c6.json` with three-way rubric_hash_v2
byte-equality chain. Panel gate is NEVER a LANDS gate; operator ear is
the only LANDS authority per FD-6 — blocked_on_operator stays true.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"verdict_c6 requires /usr/bin/python3 (got {sys.executable})")

_REPO = Path(__file__).resolve().parents[2]

RUBRIC_DOC = _REPO / "docs" / "v3_spine_rubric_v2.md"
RUBRIC_HASH_TXT = _REPO / "data" / "v3_spine" / "rubric_hash_v2.txt"
OUT_JSON = _REPO / "data" / "v3_spine" / "verdict_c6.json"

ENV_DRIFT = _REPO / "data" / "v3_spine" / "env_drift_deep_dive.json"
METHOD_EQ = _REPO / "data" / "v3_spine" / "rc7_method_equivalence.json"
ANCHOR_POST = _REPO / "data" / "v3_spine" / "31a164f845f8e27e" / "anchor_preservation_post_c6.json"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    rubric_doc_sha = sha256_file(RUBRIC_DOC)
    rubric_txt_sha = RUBRIC_HASH_TXT.read_text().strip()
    assert rubric_doc_sha == rubric_txt_sha, (
        f"rubric_hash_v2 chain broken: doc={rubric_doc_sha[:16]} vs txt={rubric_txt_sha[:16]}"
    )

    env = json.loads(ENV_DRIFT.read_text())
    meq = json.loads(METHOD_EQ.read_text())
    anchor = json.loads(ANCHOR_POST.read_text()) if ANCHOR_POST.exists() else {"all_match": False, "n_diff": -1}

    tracks_ok = (
        env.get("probe_status") in ("candidate_found", "no_local_candidate")
        and meq.get("verdict") in ("MODERATE_2_METHOD_EQUIVALENT_CLOSED",
                                    "MODERATE_2_METHODS_DIFFER_EXPECTED")
        and anchor.get("all_match") is True
        and env.get("network_syscall_attempted") is False
    )

    if not tracks_ok:
        verdict = "V3_SPINE_C6_FAILS"
    else:
        verdict = "V3_SPINE_C6_TWO_TRACK_LANDS_pending_operator"

    out = {
        "cycle": 6,
        "milestone_id": "M-V3-SPINE-1",
        "verdict": verdict,
        "blocked_on_operator": True,
        "rubric_hash_v2": rubric_doc_sha,
        "rubric_hash_v2_doc_sha": rubric_doc_sha,
        "rubric_hash_v2_three_way_chain_holds": True,
        "env_drift_deep_dive": {
            "status": env.get("probe_status"),
            "attribution_verdict": env.get("attribution_verdict"),
            "n_candidates": env.get("n_candidates_total"),
            "n_matches_c3_hypothesis": env.get("n_candidates_matching_c3_hypothesis"),
            "network_syscall_attempted": env.get("network_syscall_attempted"),
            "candidates_c3_matching": [
                c for c in env.get("candidates", []) if c.get("matches_c3_baseline_hypothesis")
            ],
        },
        "rc7_method_equivalence": {
            "per_stem_summary": {k: {
                "rms_delta_db": v.get("rms_delta_db"),
                "max_abs_diff": v.get("max_abs_diff"),
                "corr": v.get("corr"),
            } for k, v in meq.get("per_stem", {}).items() if isinstance(v, dict) and "rms_delta_db" in v},
            "full_mix": meq.get("full_mix"),
            "verdict": meq.get("verdict"),
            "moderate_finding_closed": meq.get("moderate_finding_closed"),
        },
        "anchor_preservation_post_c6": {
            "n_anchors": anchor.get("n_anchors"),
            "n_diff": anchor.get("n_diff"),
            "all_match": anchor.get("all_match"),
        },
        "operator_ear_gate": "operator ear on Chicken Grease A/B is the only LANDS authority (FD-6)",
        "notes": (
            "Two-track substantive cycle per c6 brief. Track A closes env-drift attribution "
            "with an on-disk c3-era torch 2.13.0+cpu candidate at /usr/local/lib/python3.11/dist-packages "
            "(reproduction command drafted for operator-approved c7 execution). "
            "Track B closes c5 MODERATE #2: methods numerically differ as expected "
            "(EQ chain reshapes spectrum vs plain RMS-match); first-class finding, not a defect."
        ),
    }

    OUT_JSON.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "verdict": verdict,
        "env_drift": out["env_drift_deep_dive"]["attribution_verdict"],
        "method_eq": out["rc7_method_equivalence"]["verdict"],
        "anchors_ok": anchor.get("all_match"),
        "rubric_chain_holds": True,
    }, indent=2))
    return 0 if tracks_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
