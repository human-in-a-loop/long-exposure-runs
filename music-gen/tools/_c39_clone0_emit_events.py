#!/usr/bin/python3
"""Emit c39 clone-0 M-RECREATE-1/full-corpus-recreation ledger events.

6 substantive + 4 housekeeping. Writer auto-suffixes infra families with
`-clone-0` per c33/c36-v2 fanout-namespace-convention guard.

Idempotent: skips events whose (milestone_id, ts) already exists in the
target ledger.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/user/human-in-a-loop/long-exposure")

from long_exposure.workspace_bootstrap import append_ledger_event

ROOT = Path("/home/user/long-exposure-runs/music-gen")
RUN_ID = "run-2026-08-28T040704Z"
TS_BASE = "2026-08-29T14:00:00Z"


def emit(mid: str, narrative: str, artifacts: list, status: str = "validated") -> None:
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
            "rationale": ("Full-corpus 37-song extension of c38 clone-2's "
                          "5-song BATCH_LANDS via SHA-256 tiebreak on the "
                          "43-song rated corpus minus 6-song exclusion; "
                          "8-stage c37 pipeline READ-ONLY; byte-determinism "
                          "x 2 on 148 anchors; per-song and per-band "
                          "attribution; rubric SHA embedded verbatim in "
                          "verdict.json."),
            "assessor": "worker",
        },
        "artifacts": artifacts,
    }
    append_ledger_event(ROOT, ev)
    print(f"  emitted: {mid}")


def main() -> int:
    data = ROOT / "data" / "recreate_v0_full_corpus"
    verdict = json.loads((data / "verdict.json").read_text())
    verdict_str = verdict.get("verdict", "UNKNOWN")

    # 6 substantive under M-RECREATE-1/full-corpus-recreation/*
    emit(
        "M-RECREATE-1/full-corpus-recreation/rubric-committed",
        ("Frozen 3-verdict rubric (FULL_CORPUS_LANDS/PARTIAL/FAILS) SHA "
         "landed before any script under scripts/recreate_v0_full_corpus/. "
         "Rubric SHA-256 pinned in data/recreate_v0_full_corpus/rubric_hash.txt "
         "and embedded verbatim in verdict.json.rubric_hash."),
        artifacts=[
            "docs/recreate_v0_full_corpus_rubric.md",
            "data/recreate_v0_full_corpus/rubric_hash.txt",
        ],
    )
    emit(
        "M-RECREATE-1/full-corpus-recreation/songs-selected",
        ("37-song canonical order via SHA-256 tiebreak over the 43-song "
         "corpus minus the 6-song exclusion set (c37 clone-0 + 5 c38 "
         "clone-2). Per-bucket counts: band 4=9, band 5=9, band 6=11, "
         "band 7=8."),
        artifacts=[
            "scripts/recreate_v0_full_corpus/select_songs.py",
            "data/recreate_v0_full_corpus/chosen_songs_full.json",
        ],
    )
    emit(
        "M-RECREATE-1/full-corpus-recreation/pipeline-run-1",
        ("First deterministic run: 8-stage c37 pipeline (READ-ONLY subprocess "
         "import) on all 37 songs with per-song wall-clock early-exit at "
         "6x c38 clone-2 median (493.2s per run). "
         f"Result: n_pipeline_ok={verdict.get('n_pipeline_ok')}/"
         f"{verdict.get('n_songs')}. Per-band attribution recorded."),
        artifacts=[
            "scripts/recreate_v0_full_corpus/run_full_corpus.py",
            "data/recreate_v0_full_corpus/per_song",
            "data/recreate_v0_full_corpus/all_results.json",
        ],
    )
    emit(
        "M-RECREATE-1/full-corpus-recreation/pipeline-run-2",
        ("Byte-determinism x 2 trial: 8-stage pipeline in fresh temp-dirs "
         "under identical env pins (PYTHONHASHSEED=0, SOURCE_DATE_EPOCH "
         "pinned, single-thread BLAS pins). "
         f"Result: {verdict.get('n_byte_det_anchors_ok')}/"
         f"{verdict.get('n_byte_det_anchors_total')} byte-det anchors equal "
         f"across 37 songs x 4 anchors."),
        artifacts=[
            "data/recreate_v0_full_corpus/per_song",
        ],
    )
    emit(
        "M-RECREATE-1/full-corpus-recreation/cross-band-measured",
        ("Three cross-band tables (n=37, n=42 pooled with c38 clone-2, "
         "n=43 pooled with c37 clone-0 + c38 clone-2) + Pearson/Spearman "
         "correlation JSON. Every correlation row carries the literal "
         "n_too_small caveat per c38 clone-2 convention."),
        artifacts=[
            "scripts/recreate_v0_full_corpus/cross_band_analysis.py",
            "data/recreate_v0_full_corpus/cross_band_n37.tsv",
            "data/recreate_v0_full_corpus/cross_band_pooled_n42.tsv",
            "data/recreate_v0_full_corpus/cross_band_pooled_n43.tsv",
            "data/recreate_v0_full_corpus/cross_band_correlation.json",
        ],
    )
    emit(
        "M-RECREATE-1/full-corpus-recreation/verdict-emitted",
        (f"Verdict {verdict_str}. "
         f"n_pipeline_ok={verdict.get('n_pipeline_ok')}/{verdict.get('n_songs')}, "
         f"byte-det anchors {verdict.get('n_byte_det_anchors_ok')}/"
         f"{verdict.get('n_byte_det_anchors_total')}, "
         f"positive_mel_delta={verdict.get('n_positive_mel_delta')}/"
         f"{verdict.get('n_mel_delta_computable')}. "
         f"Rubric SHA embedded verbatim. Per-band + per-song attribution "
         f"present. Report at docs/recreate_v0_full_corpus_report.md."),
        artifacts=[
            "scripts/recreate_v0_full_corpus/verdict.py",
            "data/recreate_v0_full_corpus/verdict.json",
            "data/recreate_v0_full_corpus/anchor_preservation.json",
            "docs/recreate_v0_full_corpus_report.md",
        ],
    )

    # 4 housekeeping (writer auto-suffixes -clone-0)
    emit(
        "_run/cycle_39_launched",
        ("Cycle 39 fanout clone-0 (fork c320de981fda) launched: "
         "Branch A M-RECREATE-1/full-corpus-recreation. 37-song extension "
         "of c38 clone-2's 5-song BATCH_LANDS."),
        artifacts=["docs/recreate_v0_full_corpus_rubric.md"],
    )
    emit(
        "_archive/cycle-39-scratch",
        ("Cycle 39 clone-0 scratch archived to tools/stale/. One-shot "
         "emitters and probe scripts moved after use."),
        artifacts=["tools/stale/_c39_clone0_emit_events.py"],
    )
    emit(
        "_infra/adopt-cycle39-tests",
        ("Adoption of tests/test_recreate_v0_full_corpus.py under c39 "
         "clone-0. Clears the promise_check WARN that would otherwise "
         "surface for a test file landing outside an adopted directory."),
        artifacts=["tests/test_recreate_v0_full_corpus.py"],
    )
    emit(
        "_infra/anchor-preservation-verified",
        ("Anchor preservation verified: 23+ SHA-256 anchors byte-identical "
         "pre/post the full-corpus run. Includes c37 recreate_v0 scripts + "
         "data + report, c38 clone-2 scripts + data + reports, c38 clone-0 "
         "v1 ear report (doc-path reference), c38 clone-1 score-bridge + "
         "normalizer-v2 reports (doc-path references), c8 scripts/score/"
         "bridge.py, and c9 scripts/tex/render_effects_layered.py."),
        artifacts=["data/recreate_v0_full_corpus/anchor_preservation.json"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
