#!/usr/bin/env python3
"""Append 3 findings from verify slice 23 of 23 to audits/final/findings.jsonl."""
import json, pathlib

findings_path = pathlib.Path("/home/user/long-exposure-runs/music-gen/audits/final/findings.jsonl")

rows = [
    {
        "ts": "2026-09-02T00:00:00Z",
        "milestone_id": "M-EAR-1/real-label-training-v2",
        "finding_kind": "closure_note",
        "severity": "INFO",
        "verdict": "CONFIRMED",
        "narrative": (
            "c45 M-EAR-1/real-label-training-v2 closure verified. Three-way rubric_hash "
            "byte-equality chain holds: docs/ear_real_label_training_v2_rubric.md SHA "
            "01948b6e…d71e0 == data/ear_v2/rubric_hash.txt == data/ear_v2/verdict.json.rubric_hash. "
            "Verdict EAR_v2_PARTIAL emitted honestly under c46 mapping-clarified rubric: "
            "0/3 SB pass count is compatible with PARTIAL when IMPROVEMENT criteria fire "
            "(SB2 tau v1=-0.099 → v2=-0.031; SB3 denominator v1=43 → v2=618 per verdict.delta_vs_v1). "
            "SB1 margin=-0.234 vs threshold 0.591 pass=false; SB2 mean_tau=-0.031 vs threshold 0.4 "
            "pass=false; SB3 artist FPR=0.12 vs 0.10 gate pass=false. Genre deferred_aliased_with_band, "
            "era deferred_no_metadata surfaced explicitly. Full artifact suite present: corn_head_v2.pt, "
            "training_result.json, sb_v2_{results,verdict}.json, held_out_{predictions.tsv,folds.json}, "
            "feature_cache_manifest_v2.json, resample_manifest.json, leak_test_v2_summary.json, "
            "anchor_preservation{,_c46}.json, determinism_check{,_c46}.json, sb3_control_widening_result.json. "
            "Preview_partial_corpus_v2 caveat prominent (model_label='resampled_v2_preview_partial_corpus'; "
            "corpus_honesty_caveat names 43/80 = 54% coverage). git_log_gate_note = MERGE_DEFERRED per c46 "
            "path (ii) amendment. No PRNG, no sidecar_nonfactor, c6 chassis anchors READ-ONLY. Downstream "
            "chain c46 mapping-clarified + sb3-control-widening + c47 v2.1 boundary-tip re-verdict all lands "
            "cleanly. No defect."
        ),
        "stage": "verify_23of23",
    },
    {
        "ts": "2026-09-02T00:00:00Z",
        "milestone_id": "_infra/harness-clone-namespace-guard",
        "finding_kind": "closure_note",
        "severity": "INFO",
        "verdict": "CONFIRMED",
        "narrative": (
            "c33 _infra/harness-clone-namespace-guard closure verified. Rubric doc "
            "docs/harness_clone_namespace_guard_rubric.md SHA cd020761…e876e3 byte-equal to "
            "tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt. All 5 guard symbols "
            "present on long_exposure.workspace_bootstrap module (verified via hasattr): "
            "_guard_clone_namespace, _is_clone_context, _should_suffix, LedgerNamespaceViolation, "
            "_substantive_exemption_active (c48 additive extension). LedgerNamespaceViolation.__mro__ "
            "confirms subclass of LedgerSchemaError → ValueError → Exception. append_ledger_event.__signature__ "
            "= (workspace: Path, event: dict) → None — public API unchanged as required. Test file "
            "tests/test_harness_clone_namespace_guard.py = 409 LOC with 14 def test_ functions (spec ≥10; "
            "surplus 4). Downstream evidence: 21 cycles (c34-c54) of heavy fanout exercised the guard with "
            "zero LedgerConcatError incidents observed in the ledger — e.g., c47 fork 420a6b028dfb clone-0 "
            "wrote 7 -clone-0-suffixed sub-leaves alongside clone-1/clone-2 egress-probe emissions without "
            "collision; c48 clone-0 wrote 6 -clone-0-suffixed sub-fix sub-leaves for harness-and-writer-hardening-v3 "
            "without collision. Chain extension c14 → c14 v2 → c22 → c32 → c33 preserved. No defect."
        ),
        "stage": "verify_23of23",
    },
    {
        "ts": "2026-09-02T00:00:00Z",
        "milestone_id": "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano",
        "finding_kind": "closure_note",
        "severity": "INFO",
        "verdict": "CONFIRMED",
        "narrative": (
            "c53 M-RECREATE-2/…/rc10-transcription-real-stem-resurvey/guitar-piano closure verified. "
            "Three-way rubric_hash byte-equality: docs/rc10_guitar_piano_rubric.md SHA c7fe33a7…03d7a8 == "
            "data/rc10_impl/guitar_piano/rubric_hash.txt == verdict.json.rubric_hash. Verdict "
            "RC10_GUITAR_PIANO_LANDS in frozen enum. Scorecard rows = 60 (3 candidates × 2 stems × 5 songs × "
            "2 D4-flavors) per plan spec (c). Byte-determinism × 2: n_artifacts=133, n_mismatch=0, "
            "byte_determinism_holds=true, mismatches=[]. Anchor preservation n_entries=28, n_mismatch=0 (spec "
            "≥25). candidate_win_counts: guitar C2_tuned 3/5 + C1_default 2/5; piano C2_tuned 3/5 + C1_default "
            "2/5 → winner_per_stem_type = C2_tuned for both via D5 SHA-256 tiebreak. 5 per-song subdirs. "
            "env_pins block records all 7 pins verbatim (BLAS single-thread, PYTHONHASHSEED=0, SOURCE_DATE_EPOCH="
            "1756463424, TZ=UTC, LC_ALL=C.UTF-8). Test suite tests/test_rc10_guitar_piano.py = 385 LOC. "
            "Operator UPDATE #4 (correct chord track > wrong note soup) honored via C3_chord_track candidate. "
            "LUFS ±0.5 LU target relaxed honestly for peak-limited signals — surfaced in report §Issues, not "
            "suppressed. scripts/palette_render/render_stem.py SHA 214372d9…5b2b byte-identical pre==post "
            "(c33/c36/c51 anchor). No PRNG, no sidecar_nonfactor, /usr/bin/python3 guard on top-level scripts, "
            "venv guard on _bp_inner.py. c48 env-var flags default OFF via os.environ.setdefault. Downstream: "
            "c54 emitted the drums+bass RC10 peer branch validated/high — RC10 arc converging cleanly. No defect."
        ),
        "stage": "verify_23of23",
    },
]

with findings_path.open("a") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")

print(f"Appended {len(rows)} rows. Total: {sum(1 for _ in findings_path.open())}")
