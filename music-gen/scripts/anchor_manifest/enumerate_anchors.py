#!/usr/bin/env python3
# scripts/anchor_manifest/enumerate_anchors.py — Cycle 35 clone-2.
# Returns the canonical 18-entry anchor list (path-only; no I/O).
# created: 2026-08-29
# cycle: 35
# agent: worker
# milestone: _infra/anchor-manifest-v1-clone-2
import sys
assert sys.executable == "/usr/bin/python3", sys.executable

# Long-exposure harness lives outside the workspace; an env-var-guarded
# absolute-path prefix is used for its files (established WARN exemption).
LONG_EXPOSURE_PREFIX = "/home/user/human-in-a-loop/long-exposure"

ANCHORS = [
    {
        "anchor_id": "c06_feature_cache",
        "cycle": 6, "kind": "feature_cache",
        "paths": ["data/ear/features"],
    },
    {
        "anchor_id": "c08_basic_pitch_venv",
        "cycle": 8, "kind": "venv",
        "paths": ["workspace/basic_pitch_venv"],
    },
    {
        "anchor_id": "c09_pinned_dawdreamer_chain",
        "cycle": 9, "kind": "dawdreamer_chain",
        "paths": ["scripts/tex/render_effects_layered.py"],
    },
    {
        "anchor_id": "c13_batch_v2_pipeline",
        "cycle": 13, "kind": "batch_pipeline",
        # Brief said scripts/gen/batch_v2/* but on-disk it's a single .py file;
        # sample_rules.py is the sibling per-brief.
        "paths": ["scripts/gen/batch_v2.py", "scripts/gen/sample_rules.py"],
    },
    {
        "anchor_id": "c15_i4_stratified",
        "cycle": 15, "kind": "sampling_utility",
        "paths": ["scripts/rules/sampling/i4_stratified.py"],
    },
    {
        "anchor_id": "c22_stability_harness",
        "cycle": 22, "kind": "stability_harness",
        "paths": [
            "scripts/ear/synthetic_labels.py",
            "scripts/ear/stability_metrics.py",
            "scripts/ear/stability_audit.py",
        ],
    },
    {
        "anchor_id": "c22_antipattern_flag",
        "cycle": 22, "kind": "anti_pattern_flag",
        "paths": ["docs/ear_stability_audit_report.md"],
    },
    {
        "anchor_id": "c23_antipattern_flag",
        "cycle": 23, "kind": "anti_pattern_flag",
        "paths": ["docs/ear_head_regularization_audit_report.md"],
    },
    {
        "anchor_id": "c25_antipattern_flag",
        "cycle": 25, "kind": "anti_pattern_flag",
        "paths": ["docs/ear_feature_representation_audit_report.md"],
    },
    {
        "anchor_id": "c26_c27_c28_c29_c30_analytical",
        "cycle": 30, "kind": "analytical_utility",
        "paths": ["scripts/analysis"],
    },
    {
        "anchor_id": "c31_palette_v1",
        "cycle": 31, "kind": "schema",
        "paths": [
            "scripts/palette",
            "docs/palette_assignment_schema_rubric.md",
            "docs/palette_assignment_schema_report.md",
            "data/palette/schema",
        ],
    },
    {
        "anchor_id": "c31_palette_probe",
        "cycle": 31, "kind": "probe",
        "paths": [
            "scripts/palette_probe",
            "docs/palette_instrument_determinism_rubric.md",
            "docs/palette_instrument_determinism_report.md",
            "data/palette_probe",
        ],
    },
    {
        "anchor_id": "c33_palette_render",
        "cycle": 33, "kind": "palette_render",
        "paths": [
            "scripts/palette_render",
            "docs/palette_driven_bare_render_rubric.md",
            "docs/palette_driven_bare_render_report.md",
            "data/palette_render",
        ],
    },
    {
        "anchor_id": "c33_dawdreamer_state",
        "cycle": 33, "kind": "workaround",
        "paths": [
            "scripts/dawdreamer_state",
            "docs/dawdreamer_state_extraction_rubric.md",
            "docs/dawdreamer_state_extraction_workaround_report.md",
            "data/dawdreamer_state",
        ],
    },
    {
        "anchor_id": "c33_harness_clone_namespace_guard",
        "cycle": 33, "kind": "guard",
        # long_exposure/* lives outside workspace — WARN exemption documented.
        "paths": [
            f"{LONG_EXPOSURE_PREFIX}/long_exposure/workspace_bootstrap.py",
            "tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt",
            "docs/harness_clone_namespace_guard_rubric.md",
        ],
        "exemption": "long_exposure_outside_workspace",
    },
    {
        "anchor_id": "c34_palette_v2",
        "cycle": 34, "kind": "schema",
        "paths": [
            "scripts/palette_v2",
            "docs/palette_schema_v2_rubric.md",
            "docs/palette_schema_v2_report.md",
            "data/palette_v2",
        ],
    },
    {
        "anchor_id": "c34_palette_render_cross_seed",
        "cycle": 34, "kind": "cross_seed",
        "paths": [
            "scripts/palette_render_cross_seed",
            "docs/palette_driven_bare_render_cross_seed_rubric.md",
            "docs/palette_driven_bare_render_cross_seed_report.md",
            "data/palette_render_cross_seed",
        ],
    },
    {
        "anchor_id": "c34_gen_palette_batch_v1",
        "cycle": 34, "kind": "batch",
        "paths": [
            "scripts/gen_palette_batch_v1",
            "docs/palette_driven_batch_v1_rubric.md",
            "docs/palette_driven_batch_v1_report.md",
            "data/gen_palette_batch_v1",
        ],
    },
]

def enumerate_anchors():
    """Return a deep-copy of the canonical 18-entry anchor list."""
    import copy
    return copy.deepcopy(ANCHORS)


if __name__ == "__main__":
    import json
    print(json.dumps(enumerate_anchors(), indent=2))
