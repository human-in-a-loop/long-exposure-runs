#!/usr/bin/python3
"""Emit c39 clone-1 M-EAR-1/real-label-training-v2 ledger events.

6 substantive + 4 housekeeping. Writer auto-suffixes infra families
with `-clone-1` per the c33/c36-v2 fanout-namespace-convention guard;
substantive `M-EAR-1/*` events are also passed with `-clone-1` suffix
explicitly per the c33 convention.

Idempotent: skips events whose (milestone_id, ts) already exists.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/user/human-in-a-loop/long-exposure")

from long_exposure.workspace_bootstrap import append_ledger_event

ROOT = Path("/home/user/long-exposure-runs/music-gen")
RUN_ID = "run-2026-08-28T040704Z"
TS_BASE = "2026-08-29T13:30:00Z"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def emit(mid: str, narrative: str, artifacts: list, status: str = "validated"
         ) -> None:
    ev = {
        "milestone_id": mid,
        "status": status,
        "cycle": 39,
        "run_id": RUN_ID,
        "ts": TS_BASE,
        "agent": "worker",
        "narrative": narrative,
        "confidence": {
            "level": "high",
            "rationale": (
                "M-EAR-1/real-label-training-v2 anchored-tail per-song "
                "resample intervention on 43-song rated corpus (252 clips); "
                "READ-ONLY imports of c6 chassis + c22 harness + c26 Path B "
                "+ c38 v1 tree + c1 chunker; c22/c23/c25 anti-pattern axes "
                "not touched; GroupKFold per-song grouping; byte-determinism "
                "x2 gated; anchor preservation asserted."
            ),
            "assessor": "worker",
        },
        "artifacts": [str(a) for a in artifacts],
    }
    append_ledger_event(ROOT, ev)


def emit_all() -> dict:
    verdict = json.loads((ROOT / "data/ear_v2/verdict.json").read_text())
    rubric_sha = (ROOT / "data/ear_v2/rubric_hash.txt").read_text().strip()
    resample = json.loads((ROOT / "data/ear_v2/resample_manifest.json").read_text())
    features_m = json.loads((ROOT / "data/ear_v2/feature_cache_manifest_v2.json").read_text())
    train = json.loads((ROOT / "data/ear_v2/training_result.json").read_text())
    sb = json.loads((ROOT / "data/ear_v2/sb_v2_verdict.json").read_text())
    leak = json.loads((ROOT / "data/ear_v2/leak_test_v2_summary.json").read_text())
    det = json.loads((ROOT / "data/ear_v2/determinism_check.json").read_text())
    anchor = json.loads((ROOT / "data/ear_v2/anchor_preservation.json").read_text())

    # 6 substantive
    emit(
        "M-EAR-1/real-label-training-v2/rubric-committed-clone-1",
        (
            f"Rubric SHA-256={rubric_sha}. Frozen 3-verdict rubric "
            "(EAR_v2_LANDS/PARTIAL/INSUFFICIENT) committed to disk on a "
            "clean tree BEFORE any script under scripts/ear_v2/ per the "
            "mtime gate; git-commit ordering MERGE_DEFERRED per c38 "
            "precedent (documented in verdict.json.git_log_gate_note)."
        ),
        ["docs/ear_real_label_training_v2_rubric.md", "data/ear_v2/rubric_hash.txt"],
    )
    emit(
        "M-EAR-1/real-label-training-v2/resample-manifest-locked-clone-1",
        (
            f"Anchored-tail per-song resample: {resample['n_songs_kept']} "
            f"songs kept ({resample['n_songs_skipped']} skipped), "
            f"{resample['n_clips_total']} total clips in target band "
            f"[172, 258]. Per-song clip count in [1,6]; final clip "
            "tail-anchored per c1 chunker convention."
        ),
        ["data/ear_v2/resample_manifest.json"],
    )
    emit(
        "M-EAR-1/real-label-training-v2/features-extracted-clone-1",
        (
            f"Per-clip PANNs Cnn14 (2048-D) + M-HEUR-1 (4-D) = 2052-D "
            f"feature vectors cached for {features_m['n_clips']} clips "
            f"under data/ear_v2/features_v2/. Combined manifest SHA-256 "
            f"prefix={features_m['combined_manifest_sha256'][:16]}. "
            "Content-addressed cache; skip-if-hash-matches on re-run."
        ),
        ["data/ear_v2/feature_cache_manifest_v2.json"],
    )
    emit(
        "M-EAR-1/real-label-training-v2/head-trained-clone-1",
        (
            f"c6 CORN 1-7 head trained under 5-fold GroupKFold "
            f"(groups=song_sha256, stratify=band) on "
            f"{train['corpus_size_clips']} clips across "
            f"{train['corpus_size_songs']} songs. "
            f"Clip-level MAE={train['clip_level']['aggregate_mae']:.4f} "
            f"vs baseline_min={min(train['clip_level']['baseline_majority_mae'], train['clip_level']['baseline_mean_int_mae']):.4f}. "
            f"corn_head_v2.pt SHA={_sha(ROOT/'data/ear_v2/corn_head_v2.pt')[:16]}; "
            f"training_result.json SHA={_sha(ROOT/'data/ear_v2/training_result.json')[:16]}."
        ),
        ["data/ear_v2/training_result.json", "data/ear_v2/corn_head_v2.pt",
         "data/ear_v2/held_out_predictions.tsv", "data/ear_v2/held_out_folds.json"],
    )
    a = leak["leak_types"]["artist"]
    emit(
        "M-EAR-1/real-label-training-v2/sb-evaluated-clone-1",
        (
            f"SB1 clip-level margin={sb['sb1']['margin']:.4f} "
            f"vs threshold>{sb['sb1']['threshold']} pass={sb['sb1']['pass']}. "
            f"SB2 mean tau={sb['sb2']['mean_tau']:.4f} vs threshold>="
            f"{sb['sb2']['threshold']} pass={sb['sb2']['pass']}. "
            f"SB3 artist detection={a['detection_rate']:.3f} fpr={a['fpr']:.3f} "
            f"denominator_pairs={a['denominator_pairs']} (>43={a['denominator_gt_43']}) "
            f"pass={sb['sb3']['pass']}. Frozen c26 thresholds unchanged."
        ),
        ["data/ear_v2/sb_v2_verdict.json", "data/ear_v2/sb_v2_results.json",
         "data/ear_v2/leak_test_v2_summary.json"],
    )
    emit(
        "M-EAR-1/real-label-training-v2/verdict-emitted-clone-1",
        (
            f"Verdict={verdict['verdict']}. rubric_hash={rubric_sha[:16]} "
            f"byte-equal to data/ear_v2/rubric_hash.txt. Named SB "
            f"attribution: {len(verdict.get('named_sb_attribution', []))} "
            f"entries. Delta vs v1: SB1 margin "
            f"{verdict['delta_vs_v1']['sb1_margin_v1']:.4f} -> "
            f"{verdict['delta_vs_v1']['sb1_margin_v2']:.4f}; "
            f"SB2 tau {verdict['delta_vs_v1']['sb2_tau_v1']:.4f} -> "
            f"{verdict['delta_vs_v1']['sb2_tau_v2']:.4f}; "
            f"SB3 denominator {verdict['delta_vs_v1']['sb3_denominator_v1']} "
            f"-> {verdict['delta_vs_v1']['sb3_denominator_v2']}. "
            f"Byte-determinism x2 gate: {det['byte_determinism_x2']}."
        ),
        ["data/ear_v2/verdict.json", "docs/ear_real_label_training_v2_report.md"],
    )

    # 4 housekeeping (all -clone-1)
    emit(
        "_run/cycle_39_launched-clone-1",
        "c39 clone-1 M-EAR-1/real-label-training-v2 launched.",
        ["docs/ear_real_label_training_v2_rubric.md"],
    )
    emit(
        "_infra/adopt-cycle39-tests-clone-1",
        "Adopt tests/test_ear_real_label_training_v2.py under c39 ledger.",
        ["tests/test_ear_real_label_training_v2.py"],
    )
    emit(
        "_infra/anchor-preservation-verified-clone-1",
        (
            f"c6/c22/c26/c38-v1/c1 chunker anchor SHAs byte-identical "
            f"pre/post: {anchor['all_unchanged']} across {anchor['n_anchors']} "
            f"files + c6 feature cache manifest SHA unchanged: "
            f"{anchor['c6_feature_cache_unchanged']}."
        ),
        ["data/ear_v2/anchor_preservation.json"],
    )
    emit(
        "_archive/cycle-39-scratch-clone-1",
        "Archive c39 clone-1 one-shot ledger emitter to tools/stale/.",
        ["tools/stale/_c39_clone1_emit_events.py"],
    )
    return {"emitted": 10}


if __name__ == "__main__":
    r = emit_all()
    print(json.dumps(r, indent=2))
