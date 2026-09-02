import json, pathlib
p = pathlib.Path("/home/user/long-exposure-runs/music-gen/audits/final/findings.jsonl")
rows = [
    {"ts": "2026-09-02T00:00:00Z", "milestone_id": "M-CLASS-1", "finding_kind": "closure_note", "severity": "none", "narrative": "Slice 20/23 verify: M-CLASS-1 (c1) closure_verified. valset_manifest.tsv 55 clips + predictions.jsonl 55 rows + confusion_matrix.tsv + per_class_metrics.tsv on disk. Non-factor sidecar isolation enforced by tests/test_sidecar_isolation.py (189 lines, static-analysis). Numpy 2.4.6 to 1.26.4 downgrade accepted at c6; downstream regression never surfaced. 0 defects."},
    {"ts": "2026-09-02T00:00:00Z", "milestone_id": "M-EAR-1/preparation", "finding_kind": "closure_note", "severity": "none", "narrative": "Slice 20/23 verify: M-EAR-1/preparation (c6) closure_verified. Roll-up of features (2052-D = PANNs 2048 + HEUR 4), model (CORN 1-7 head), leak-test (tau artist 0.7047 genre 0.6289 era 0.4929; detection at alpha=1.0 all >=0.914; FPR exactly 0.10 per leak type). 90 npz files on disk. Chassis used verbatim by 6 later M-EAR-1 milestones (c22/c23/c25 audits + c36/c38/c45/c47 real-label training). 0 defects."},
    {"ts": "2026-09-02T00:00:00Z", "milestone_id": "M-GEN-1/collision-model-semantic-cluster-overlap", "finding_kind": "closure_note", "severity": "none", "narrative": "Slice 20/23 verify: M-GEN-1/collision-model-semantic-cluster-overlap (c30) closure_verified as M4_REFUTES; arc_close_triggered=true. First-class negative finding closes the collision-modeling arc as PARTIAL_BP_UNRESOLVED_SHAPE after four sequential mechanism probes (M1-M4). aggregate_r2_before=0.9588, aggregate_r2_after=-28.84, alpha_pinned=0.7469387071101908 (c26 alpha-hat, not refit). 12/12 tests in test_semantic_cluster_overlap.py. c26-c29 utility anchors READ-ONLY per anchor_preservation_semantic.json. No PRNG, no sidecar_nonfactor, i4_stratified.py not imported. 0 defects."},
]
with p.open("a") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print("appended", len(rows), "rows; total now", sum(1 for _ in p.open()))
