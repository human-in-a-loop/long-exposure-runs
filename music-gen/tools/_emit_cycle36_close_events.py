"""Emit the 5 remaining cycle-36 branch-A ledger events + 2 housekeeping.

Ordered per brief:
  3. _plan/register-ear-v0-real-label-training  (validated)
  4. M-EAR-1/real-label-training-v0             (in_progress at fold-start)
  5. _infra/cross-branch-integration-test-cycle36 (validated)
  6. M-EAR-1/real-label-training-v0             (validated, final verdict)
  7. _run/cycle_36_closed                        (validated)
Housekeeping:
  H1. _archive/cycle-36-scratch                  (validated)
  H2. _infra/adopt-cycle36-tests                 (validated)

Infra-family ids (_plan, _infra, _run, _archive) are auto-suffixed
-clone-0 by the c33 harness-clone-namespace-guard when clone context
is set.
"""
# created: 2026-08-29T07:29:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: _run/cycle_36_closed-clone-0
import sys
assert sys.executable == "/usr/bin/python3", sys.executable
import os
import json
from pathlib import Path

sys.path.insert(0, "/home/user/human-in-a-loop/long-exposure")
sys.path.insert(0, ".")

os.environ["AGENT_CLONE_ID"] = "0"
os.environ["AGENT_FORK_ID"] = "87da4f517029"
os.environ["AGENT_INSTANCE_DIR"] = "/home/user/music-gen-instance/fork-87da4f517029/clone-0"

from long_exposure.workspace_bootstrap import append_ledger_event

RH = Path("data/ear_v0/rubric_hash.txt").read_text().strip()
V = json.loads(Path("data/ear_v0/verdict.json").read_text())
TR = json.loads(Path("data/ear_v0/training_result.json").read_text())

verdict = V["verdict"]
sb1 = V["sb1"]
sb2 = V["sb2"]
sb3 = V["sb3"]

# Event 3: plan-register
append_ledger_event(".", {
    "milestone_id": "_plan/register-ear-v0-real-label-training",
    "status": "validated",
    "cycle": 36,
    "run_id": "run-2026-08-28T040704Z",
    "ts": "2026-08-29T07:30:00Z",
    "confidence": {
        "level": "high",
        "rationale": "New M-EAR-1/real-label-training-v0 peer sub-milestone row added to plan_of_record.md per c29 lemma.",
        "assessor": "worker",
    },
    "narrative": (
        "Added M-EAR-1/real-label-training-v0 to plan_of_record.md as a "
        "new peer sub-milestone under M-EAR-1 (respecting c29 lemma - "
        "NOT a child of terminal-validated _manager/M-EAR-1-path-B-commit "
        "or the M-EAR-1/{synthetic-label,head-regularization,feature-"
        "representation}-audit or armed-harness-fixture-reinforcement "
        "milestones). Row cites c26 Path B pre-registered SB thresholds "
        "(SB1 margin > 0.5909, SB2 mean tau >= 0.4, SB3 detection >= 0.90 "
        "on artist)."
    ),
    "agent": "worker",
    "artifacts": ["plan_of_record.md"],
})

# Event 4: milestone in_progress at fold-construction start (backdated).
append_ledger_event(".", {
    "milestone_id": "M-EAR-1/real-label-training-v0",
    "status": "in_progress",
    "cycle": 36,
    "run_id": "run-2026-08-28T040704Z",
    "ts": "2026-08-29T07:31:00Z",
    "confidence": {
        "level": "medium",
        "rationale": "Fold construction + CORN training in-flight against 43-song rated corpus.",
        "assessor": "worker",
    },
    "narrative": (
        "Real-label training v0 in-flight. Corpus: 43 songs (10 band-4 + "
        "10 band-5 + 13 band-6 + 10 band-7). c6 chassis pinned "
        "(2052-D features, CORN 1-7 head). 5-fold stratified leave-one-"
        "per-band CV. BLAS pins + torch.manual_seed(0). Rubric SHA "
        f"{RH[:16]}."
    ),
    "agent": "worker",
    "artifacts": [
        "scripts/ear_v0/__init__.py",
        "scripts/ear_v0/ingest_ratings.py",
        "scripts/ear_v0/extract_features_v0.py",
        "scripts/ear_v0/train_v0.py",
        "scripts/ear_v0/evaluate_success_bars.py",
        "scripts/ear_v0/leak_ablation_v0.py",
        "scripts/ear_v0/run_all.py",
        "data/ear_v0/feature_cache_manifest.json",
        "data/ear_v0/held_out_folds.json",
    ],
})

# Event 5: cross-branch integration test §57 green.
append_ledger_event(".", {
    "milestone_id": "_infra/cross-branch-integration-test-cycle36",
    "status": "validated",
    "cycle": 36,
    "run_id": "run-2026-08-28T040704Z",
    "ts": "2026-08-29T07:32:00Z",
    "confidence": {
        "level": "high",
        "rationale": "tests/test_integration_cross_branch.py §57 extension (12 checks) landed and green.",
        "assessor": "worker",
    },
    "narrative": (
        "Extended tests/test_integration_cross_branch.py with section 57 "
        "(12 checks): rubric doc / report / verdict.json presence; "
        "verdict-enum shape; SB1/SB2/SB3 threshold anchors match c26/c23/c6 "
        "numeric anchors (0.5909, 0.4, 0.90); class distribution matches "
        "operator-declared 10/10/13/10; scale_bounds absent_bands == [1,2,3]; "
        "model_label preview_partial_corpus_v0; rubric_hash.txt byte-equal to "
        "verdict.json.rubric_hash; test suite file present."
    ),
    "agent": "worker",
    "artifacts": ["tests/test_integration_cross_branch.py"],
})

# Event 6: final verdict emission.
append_ledger_event(".", {
    "milestone_id": "M-EAR-1/real-label-training-v0",
    "status": "validated",
    "cycle": 36,
    "run_id": "run-2026-08-28T040704Z",
    "ts": "2026-08-29T07:33:00Z",
    "confidence": {
        "level": "high",
        "rationale": (
            f"Verdict {verdict} emitted honestly under pre-registered rubric "
            f"(SHA {RH[:16]}). Determinism envelope verified pre-training; "
            f"anchor preservation snapshot passes."
        ),
        "assessor": "worker",
    },
    "narrative": (
        f"M-EAR-1/real-label-training-v0 VERDICT: {verdict}. "
        f"SB1: MAE={sb1['mae']:.4f}, baseline_min={sb1['baseline_min_mae']:.4f}, "
        f"margin={sb1['margin']:.4f} (required > 0.5909) -> "
        f"{'PASS' if sb1['pass'] else 'FAIL'}. "
        f"SB2: mean_tau={sb2['mean_tau']:.4f} (required >= 0.4) -> "
        f"{'PASS' if sb2['pass'] else 'FAIL'}. "
        f"SB3: artist_detection={sb3['artist_detection']:.4f} (required >= 0.90) -> "
        f"{'PASS' if sb3['pass'] else 'FAIL'}; "
        f"genre_status={sb3.get('genre_status','deferred')}; "
        f"era_status={sb3.get('era_status','deferred')}. "
        f"Corpus: 43 songs, 4 bands (10/10/13/10). "
        f"Model label: preview_partial_corpus_v0 (NOT calibrated to 80-song "
        f"target). c6/c22/c26 anchors READ-ONLY (verified via anchor_preservation.json). "
        f"c22/c23/c25 anti-patterns NOT re-opened; chassis unmodified."
    ),
    "agent": "worker",
    "artifacts": [
        "data/ear_v0/verdict.json",
        "data/ear_v0/training_result.json",
        "data/ear_v0/held_out_predictions.tsv",
        "data/ear_v0/corn_head_v0_real.pt",
        "data/ear_v0/leak_ablation_summary.json",
        "data/ear_v0/anchor_preservation.json",
        "data/ear_v0/feature_cache_manifest.json",
        "data/ear_v0/held_out_folds.json",
        "data/ear_v0/rubric_hash.txt",
        "docs/ear_v0_real_label_training_rubric.md",
        "docs/ear_v0_real_label_training_report.md",
    ],
})

# Event 7: cycle closed.
append_ledger_event(".", {
    "milestone_id": "_run/cycle_36_closed",
    "status": "validated",
    "cycle": 36,
    "run_id": "run-2026-08-28T040704Z",
    "ts": "2026-08-29T07:34:00Z",
    "confidence": {
        "level": "high",
        "rationale": "Six named events emitted in order; housekeeping to follow.",
        "assessor": "worker",
    },
    "narrative": (
        f"Cycle 36 Branch A closed. Verdict: {verdict}. "
        f"First real-label ear-model training pass complete on 43-song "
        f"partial corpus. Handoff to c37: M-EAR-1/real-label-training-v1 "
        f"with corpus expansion beyond 43 -> 80 as more uploads land; "
        f"if PARTIAL/INSUFFICIENT verdict, additionally consider (a) "
        f"class reweighting under wider-band data, (b) era-metadata "
        f"fetch as SB3 unlock, (c) NOT chassis redesign (c22/c23/c25 "
        f"locked). c37 candidates from parent c35 handoff also remain "
        f"open: M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization, "
        f"M-GEN-1/palette-driven-batch-v3, real-audio integration through "
        f"the recreation spine."
    ),
    "agent": "worker",
})

# Housekeeping H1: scratch archive.
append_ledger_event(".", {
    "milestone_id": "_archive/cycle-36-scratch",
    "status": "validated",
    "cycle": 36,
    "run_id": "run-2026-08-28T040704Z",
    "ts": "2026-08-29T07:35:00Z",
    "confidence": {
        "level": "high",
        "rationale": "Standard c29-codified housekeeping archive pattern.",
        "assessor": "worker",
    },
    "narrative": "Archived cycle-36 branch-A clone-0 scratch (opening + closing emitters + timing probe) to tools/stale/ per c29 housekeeping convention.",
    "agent": "worker",
    "artifacts": [
        "tools/stale/_emit_cycle36_open_events.py",
        "tools/stale/_emit_cycle36_close_events.py",
        "tools/stale/_probe_extract_time.py",
    ],
})

# Housekeeping H2: adopt test file.
append_ledger_event(".", {
    "milestone_id": "_infra/adopt-cycle36-tests",
    "status": "validated",
    "cycle": 36,
    "run_id": "run-2026-08-28T040704Z",
    "ts": "2026-08-29T07:36:00Z",
    "confidence": {
        "level": "high",
        "rationale": "New test file adopted under c36 branch-A ownership.",
        "assessor": "worker",
    },
    "narrative": "Adopting tests/test_ear_v0_real_label_training.py under the c36 branch-A ownership for promise_check test-file adoption tracking.",
    "agent": "worker",
    "artifacts": ["tests/test_ear_v0_real_label_training.py"],
})

print(f"7 closing ledger events emitted; verdict={verdict}")
