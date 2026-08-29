#!/usr/bin/python3
"""v2.1 verdict emitter — reads the two SB3 run outputs and writes data/ear_v2p1/verdict.json."""
# created: 2026-08-29T17:09:00Z  cycle: 47  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: M-EAR-1/real-label-training-v2.1
from __future__ import annotations

import sys

print("[c47:emit_verdict] starting", flush=True)
assert sys.executable == "/usr/bin/python3", sys.executable

import argparse
import hashlib
import json
from pathlib import Path

DATA_DIR = Path("data/ear_v2p1")


def load_run(run_dir: Path) -> dict:
    v = json.loads((run_dir / "sb3_50ctl_verdict_v2p1.json").read_text())
    return v["at_n_controls_50"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run1", required=True)
    ap.add_argument("--run2", required=True)
    args = ap.parse_args()

    r1_dir = Path(args.run1)
    r2_dir = Path(args.run2)
    r1_verdict_path = r1_dir / "sb3_50ctl_verdict_v2p1.json"
    r2_verdict_path = r2_dir / "sb3_50ctl_verdict_v2p1.json"
    r1_sha = hashlib.sha256(r1_verdict_path.read_bytes()).hexdigest()
    r2_sha = hashlib.sha256(r2_verdict_path.read_bytes()).hexdigest()
    byte_det = (r1_sha == r2_sha)

    r1 = load_run(r1_dir)
    r2 = load_run(r2_dir)
    fpr1 = r1["fpr"]
    fpr2 = r2["fpr"]
    det1 = r1["detection_rate"]
    det2 = r2["detection_rate"]
    fpr_max = r1["fpr_max"]
    assert det1 == det2 == 1.000, (det1, det2)

    both_pass_fpr = (fpr1 <= fpr_max and fpr2 <= fpr_max)
    both_fail_fpr = (fpr1 > fpr_max and fpr2 > fpr_max)
    mixed = (fpr1 <= fpr_max) != (fpr2 <= fpr_max)

    if byte_det and both_pass_fpr and not mixed:
        sb3_verdict = "EAR_v2p1_STABLE_FPR_PASS"
        mapping_label = "EAR_v2p1_PARTIAL_WITH_SB3_PASS"
        sb3_fpr_status = "PASS"
    elif both_fail_fpr:
        sb3_verdict = "EAR_v2p1_FPR_STILL_OVERSHOOT"
        mapping_label = "EAR_v2p1_PARTIAL"
        sb3_fpr_status = "FAIL"
    else:
        sb3_verdict = "EAR_v2p1_BOUNDARY_TIP"
        mapping_label = "EAR_v2p1_PARTIAL_WITH_SB3_BOUNDARY_TIP"
        sb3_fpr_status = "BOUNDARY"

    rubric_hash = (DATA_DIR / "rubric_hash.txt").read_text().strip()

    # SHAs pinned in verdict (chassis + probe artifacts).
    def _sha_or_missing(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "MISSING"

    corn_head_sha = _sha_or_missing(DATA_DIR / "corn_head_v2p1.pt")
    train_res_sha = _sha_or_missing(DATA_DIR / "training_result_v2p1.json")
    c46_sb3_sha = _sha_or_missing(
        Path("data/ear_v2/sb3_control_widening_result.json")
    )
    c45_v2_verdict_sha = _sha_or_missing(Path("data/ear_v2/verdict.json"))
    combined_manifest = json.loads(
        Path("data/ear_v2/feature_cache_manifest_v2.json").read_text()
    )
    feature_cache_sha = combined_manifest["combined_manifest_sha256"]

    verdict = {
        "cycle": 47,
        "milestone": "M-EAR-1/real-label-training-v2.1",
        "verdict": sb3_verdict,
        "mapping_label": mapping_label,
        "narrative": (
            f"v2.1 SB3 50-control re-verdict. Detection = 1.000 (unchanged "
            f"from c46, PASS). FPR run 1 = {fpr1:.4f}; FPR run 2 = "
            f"{fpr2:.4f}. Byte-determinism × 2 on "
            f"sb3_50ctl_verdict_v2p1.json = {byte_det}. Verdict "
            f"{sb3_verdict} -> mapping {mapping_label}. c46 methodology "
            f"chain: c37 F1 pooled-variance -> c38 leak-lift -> c46 "
            f"widening 25->50."
        ),
        "rubric_hash": rubric_hash,
        "detection_v2p1": det1,
        "fpr_run_1": fpr1,
        "fpr_run_2": fpr2,
        "fpr_boundary_delta": min(abs(fpr1 - fpr_max), abs(fpr2 - fpr_max)),
        "byte_determinism_x2": byte_det,
        "byte_determinism_shas": [r1_sha, r2_sha],
        "sb1_status": "FAIL_unchanged_from_c45",
        "sb2_status": "FAIL_unchanged_from_c45",
        "sb3_detection_status": "PASS",
        "sb3_fpr_status": sb3_fpr_status,
        "corpus_n": "43_of_80",
        "corpus_caveat": "preview_partial_corpus_v2p1",
        "c46_methodology_chain": [
            "c37_f1_pooled_variance",
            "c38_leak_lift",
            "c46_widening_25_to_50",
        ],
        "c45_verdict_reference": "EAR_v2_PARTIAL_unchanged",
        "c45_v2_verdict_json_sha256": c45_v2_verdict_sha,
        "c46_sb3_widening_result_sha256": c46_sb3_sha,
        "combined_feature_manifest_sha256": feature_cache_sha,
        "training_result_v2p1_sha256": train_res_sha,
        "corn_head_v2p1_sha256": corn_head_sha,
        "sb3_50ctl_run_1_verdict_sha256": r1_sha,
        "sb3_50ctl_run_2_verdict_sha256": r2_sha,
        "run_1_dir": str(r1_dir),
        "run_2_dir": str(r2_dir),
    }
    p = DATA_DIR / "verdict.json"
    p.write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "verdict": sb3_verdict,
        "mapping_label": mapping_label,
        "byte_determinism_x2": byte_det,
        "fpr_run_1": fpr1,
        "fpr_run_2": fpr2,
        "detection_v2p1": det1,
        "path": str(p),
    }, indent=2))


if __name__ == "__main__":
    main()
