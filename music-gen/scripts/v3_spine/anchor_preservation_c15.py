#!/usr/bin/env python3
"""c15 anchor preservation: snapshot ≥175 SHAs pre-run, verify byte-identical post-run.

Extends the c14 166-anchor list with the c14-landed additions:
    - c14 cycle14/ delivery (verdict.json)
    - c14 torch probe JSON (data/v3_spine/cycle14/torch213_reproduce_probe_c14.json)
    - c14 anchor pre/post/diff snapshots
    - c14 scripts (anchor_preservation_c14.py, verdict_c14.py) —
      torch213_reproduce_probe_c14.py already in locked-scripts block
    - c14 test file (tests/test_v3_spine_c14.py)
    - c14 report doc (docs/v3_spine_report_cycle14.md)

Target ≥175 anchors (166 + 10 = 176 delivered). Verify pre==post byte-identical.

Usage:
    /usr/bin/python3 scripts/v3_spine/anchor_preservation_c15.py pre
    /usr/bin/python3 scripts/v3_spine/anchor_preservation_c15.py post
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"anchor_preservation_c15 requires /usr/bin/python3 (got {sys.executable})"
    )

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)

ANCHORS = [
    # c5 operator-section delivery (READ-ONLY)
    "data/v3/deliveries/31a164f845f8e27e/operator_section/original_ab_operator_section.wav",
    "data/v3/deliveries/31a164f845f8e27e/operator_section/reconstruction_ab_operator_section.wav",
    "data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav",
    "data/v3/deliveries/31a164f845f8e27e/operator_section/manifest.json",
    "data/v3/deliveries/31a164f845f8e27e/operator_section/verdict.json",
    "data/v3/deliveries/31a164f845f8e27e/operator_section/panel.tsv",
    "data/v3/deliveries/31a164f845f8e27e/operator_section/panel.json",
    # c4 delivery preserved as READ-ONLY
    "data/v3/deliveries/31a164f845f8e27e/original_ab.wav",
    "data/v3/deliveries/31a164f845f8e27e/reconstruction_ab.wav",
    "data/v3/deliveries/31a164f845f8e27e/full_reconstruction.wav",
    "data/v3/deliveries/31a164f845f8e27e/manifest.json",
    "data/v3/deliveries/31a164f845f8e27e/verdict.json",
    "data/v3/deliveries/31a164f845f8e27e/panel.tsv",
    "data/v3/deliveries/31a164f845f8e27e/panel.json",
    # c5 operator-section raw stems + rendered per-track
    "data/v3_spine/31a164f845f8e27e/operator_section/section.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/drums.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/bass.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/guitar.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/piano.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/other.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/vocals.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/render/per_track/drums.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/render/per_track/bass.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/render/per_track/guitar.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/render/per_track/piano.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/render/per_track/other.wav",
    "data/v3_spine/31a164f845f8e27e/operator_section/render/vocals_htdemucs.wav",
    # Docs (READ-ONLY)
    "docs/v3_spine_rubric_v2.md",
    "docs/v3_spine_canonical_midi_serializer_spec.md",
    "docs/v3_spine_rubric.md",
    "docs/v3_spine_instrument_whitelist_mapping.md",
    "docs/v3_spine_venv_delta_audit_spec.md",
    "docs/v3_spine_rehtdemucs_operator_section_spec.md",
    "docs/v3_spine_env_drift_deep_dive_spec.md",
    "docs/v3_spine_method_equivalence_rc7_spec.md",
    "docs/PIVOT_v3_simplest_robust_pipeline.md",
    "docs/OPERATOR_recreation_root_cause_audit.md",
    "music_gen_v3_prompt.md",
    "docs/v3_spine_torch213_reproduce_spec.md",
    # c4 canonical serializer + hashes
    "scripts/v3_spine/midi_from_json_events.py",
    "data/v3_spine/canonical_serializer_spec_hash.txt",
    "data/v3_spine/rubric_hash_v2.txt",
    "data/v3_spine/rubric_hash.txt",
    "data/v3_spine/venv_delta_audit_spec_hash.txt",
    "data/v3_spine/rehtdemucs_operator_section_spec_hash.txt",
    "data/v3_spine/env_drift_deep_dive_spec_hash.txt",
    "data/v3_spine/method_equivalence_rc7_spec_hash.txt",
    "data/v3_spine/torch213_reproduce_spec_hash.txt",
    # c3 MuScriptor JSON+MID anchors (READ-ONLY)
    "data/v3_spine/31a164f845f8e27e/muscriptor/drums.json",
    "data/v3_spine/31a164f845f8e27e/muscriptor/drums.mid",
    "data/v3_spine/31a164f845f8e27e/muscriptor/bass.json",
    "data/v3_spine/31a164f845f8e27e/muscriptor/bass.mid",
    "data/v3_spine/31a164f845f8e27e/muscriptor/full_mix.json",
    "data/v3_spine/31a164f845f8e27e/muscriptor/full_mix.mid",
    "data/v3_spine/31a164f845f8e27e/muscriptor/guitar.json",
    # c4 canonical MIDI anchors (READ-ONLY)
    "data/v3_spine/31a164f845f8e27e/canonical_midi/drums.mid",
    "data/v3_spine/31a164f845f8e27e/canonical_midi/bass.mid",
    "data/v3_spine/31a164f845f8e27e/canonical_midi/guitar.mid",
    "data/v3_spine/31a164f845f8e27e/canonical_midi/other.mid",
    "data/v3_spine/31a164f845f8e27e/canonical_midi/piano.mid",
    "data/v3_spine/31a164f845f8e27e/canonical_midi/vocals.mid",
    "data/v3_spine/31a164f845f8e27e/canonical_midi/full_mix.mid",
    # c4 merged.mid + tempo
    "data/v3_spine/31a164f845f8e27e/merged.mid",
    "data/v3_spine/31a164f845f8e27e/tempo_choice.json",
    # c4 anchor snapshots + c5/c6/c7/c8 pre/post
    "data/v3_spine/31a164f845f8e27e/anchor_preservation_v2.json",
    "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c5.json",
    "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c6.json",
    "data/v3_spine/31a164f845f8e27e/anchor_preservation_post_c6.json",
    "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c7.json",
    "data/v3_spine/31a164f845f8e27e/anchor_preservation_post_c7.json",
    "data/v3_spine/31a164f845f8e27e/anchor_preservation_c7.json",
    "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_c8.json",
    "data/v3_spine/31a164f845f8e27e/anchor_preservation_post_c8.json",
    "data/v3_spine/31a164f845f8e27e/anchor_preservation_c8.json",
    # baseline (READ-ONLY)
    "data/recreate_v2/baseline/31a164f845f8e27e/rc5_tempo_bpm.json",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc7_per_stem_loudness.json",
    # Locked scripts (DO-NOT-TOUCH)
    "scripts/palette_render/render_stem.py",
    "scripts/recreate_v2/rc7_v2_rerun.py",
    "scripts/recreate_v2/rc7_mix_balance.py",
    "scripts/v3_spine/mix_match_operator_section.py",
    "scripts/v3_spine/rc7_v2_rerun_v3_paths.py",
    "scripts/v3_spine/torch213_reproduce_probe.py",
    "scripts/v3_spine/torch213_reproduce_probe_c8.py",
    "scripts/v3_spine/torch213_reproduce_probe_c9.py",
    "scripts/v3_spine/torch213_reproduce_probe_c10.py",
    "scripts/v3_spine/torch213_reproduce_probe_c11.py",
    "scripts/v3_spine/torch213_reproduce_probe_c12.py",
    "scripts/v3_spine/torch213_reproduce_probe_c13.py",
    "scripts/v3_spine/torch213_reproduce_probe_c14.py",
    # focus_set_v2
    "data/recreate_v2/focus_set_v2.json",
    # SF2 (system path per c6 anchor list)
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
    # c6 outputs (READ-ONLY for c7+)
    "data/v3_spine/verdict_c6.json",
    "data/v3_spine/env_drift_deep_dive.json",
    "data/v3_spine/env_drift_deep_dive_byte_det.json",
    "data/v3_spine/rc7_method_equivalence.json",
    "data/v3_spine/rc7_v2_v3_paths/rc7_v2_v3_paths_full_reconstruction.wav",
    "data/v3_spine/rc7_v2_v3_paths/byte_determinism.json",
    "docs/v3_spine_report_cycle3.md",
    "docs/v3_spine_report_cycle4.md",
    "docs/v3_spine_report_cycle5.md",
    "docs/v3_spine_report_cycle6.md",
    "docs/v3_spine_report_cycle7.md",
    "docs/v3_spine_report_cycle8.md",
    "docs/v3_spine_report_cycle9.md",
    # c7 delivery (READ-ONLY) — cycle7/ path
    "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.json",
    "data/v3/deliveries/31a164f845f8e27e/cycle7/torch213_reproduce_probe.json",
    "data/v3/deliveries/31a164f845f8e27e/cycle7/empty_stem_duration_sanity.json",
    "data/v3/deliveries/31a164f845f8e27e/cycle7/rc7_canonicality_metrics.json",
    # c7 cycle7 data
    "data/v3_spine/cycle7/torch213_reproduce_probe.json",
    "data/v3_spine/cycle7/empty_stem_duration_sanity.json",
    "data/v3_spine/cycle7/rc7_canonicality_metrics.json",
    "data/v3_spine/cycle7/byte_determinism.json",
    # rc7 canonicality decision note — POST-drift SHA
    "docs/v3_spine_rc7_canonicality_decision_note.md",
    # c8-landed cadence policy doc + hash
    "docs/wait_on_operator_cadence_policy.md",
    "data/v3_spine/wait_on_operator_cadence_policy_hash.txt",
    # c8 artifacts (READ-ONLY)
    "data/v3/deliveries/31a164f845f8e27e/cycle8/verdict.json",
    "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.c8_amendment.json",
    "data/v3_spine/cycle8/torch213_reproduce_probe_c8.json",
    "scripts/v3_spine/verdict_c8_amendment.py",
    "scripts/v3_spine/anchor_preservation_c8.py",
    "scripts/v3_spine/verdict_c8.py",
    "tests/test_verdict_sha_fields_resolve_on_disk.py",
    "tests/test_v3_spine_c8.py",
    # c9 artifacts (READ-ONLY)
    "data/v3/deliveries/31a164f845f8e27e/cycle9/verdict.json",
    "data/v3_spine/cycle9/torch213_reproduce_probe_c9.json",
    "data/v3_spine/cycle9/anchor_preservation_pre_c9.json",
    "data/v3_spine/cycle9/anchor_preservation_post_c9.json",
    "data/v3_spine/cycle9/anchor_preservation_c9.json",
    "scripts/v3_spine/anchor_preservation_c9.py",
    "scripts/v3_spine/verdict_c9.py",
    "tests/test_v3_spine_c9.py",
    "docs/v3_spine_report_cycle9.md",
    # c10 artifacts (READ-ONLY)
    "data/v3/deliveries/31a164f845f8e27e/cycle10/verdict.json",
    "data/v3_spine/cycle10/torch213_reproduce_probe_c10.json",
    "data/v3_spine/cycle10/anchor_preservation_pre_c10.json",
    "data/v3_spine/cycle10/anchor_preservation_post_c10.json",
    "data/v3_spine/cycle10/anchor_preservation_c10.json",
    "scripts/v3_spine/anchor_preservation_c10.py",
    "scripts/v3_spine/verdict_c10.py",
    "tests/test_v3_spine_c10.py",
    "docs/v3_spine_report_cycle10.md",
    # c11 artifacts (READ-ONLY)
    "data/v3/deliveries/31a164f845f8e27e/cycle11/verdict.json",
    "data/v3_spine/cycle11/torch213_reproduce_probe_c11.json",
    "data/v3_spine/cycle11/anchor_preservation_pre_c11.json",
    "data/v3_spine/cycle11/anchor_preservation_post_c11.json",
    "data/v3_spine/cycle11/anchor_preservation_c11.json",
    "scripts/v3_spine/anchor_preservation_c11.py",
    "scripts/v3_spine/verdict_c11.py",
    "tests/test_v3_spine_c11.py",
    "docs/v3_spine_report_cycle11.md",
    # c12 artifacts (READ-ONLY)
    "data/v3/deliveries/31a164f845f8e27e/cycle12/verdict.json",
    "data/v3_spine/cycle12/torch213_reproduce_probe_c12.json",
    "data/v3_spine/cycle12/anchor_preservation_pre_c12.json",
    "data/v3_spine/cycle12/anchor_preservation_post_c12.json",
    "data/v3_spine/cycle12/anchor_preservation_c12.json",
    "scripts/v3_spine/anchor_preservation_c12.py",
    "scripts/v3_spine/verdict_c12.py",
    "tests/test_v3_spine_c12.py",
    "docs/v3_spine_report_cycle12.md",
    # c13 artifacts (READ-ONLY)
    "data/v3/deliveries/31a164f845f8e27e/cycle13/verdict.json",
    "data/v3_spine/cycle13/torch213_reproduce_probe_c13.json",
    "data/v3_spine/cycle13/anchor_preservation_pre_c13.json",
    "data/v3_spine/cycle13/anchor_preservation_post_c13.json",
    "data/v3_spine/cycle13/anchor_preservation_c13.json",
    "scripts/v3_spine/anchor_preservation_c13.py",
    "scripts/v3_spine/verdict_c13.py",
    "tests/test_v3_spine_c13.py",
    "docs/v3_spine_report_cycle13.md",
    # c14 artifacts (READ-ONLY for c15) — 10 new entries → 166 + 10 = 176 (target ≥175)
    "data/v3/deliveries/31a164f845f8e27e/cycle14/verdict.json",
    "data/v3_spine/cycle14/torch213_reproduce_probe_c14.json",
    "data/v3_spine/cycle14/anchor_preservation_pre_c14.json",
    "data/v3_spine/cycle14/anchor_preservation_post_c14.json",
    "data/v3_spine/cycle14/anchor_preservation_c14.json",
    "scripts/v3_spine/anchor_preservation_c14.py",
    "scripts/v3_spine/verdict_c14.py",
    "tests/test_v3_spine_c14.py",
    "docs/v3_spine_report_cycle14.md",
    # (torch213_reproduce_probe_c14.py already listed in locked-scripts block above)
]


def sha256_of(p: str) -> tuple[str, int]:
    with open(p, "rb") as f:
        data = f.read()
    return hashlib.sha256(data).hexdigest(), len(data)


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in ("pre", "post"):
        print("usage: anchor_preservation_c15.py {pre|post}", file=sys.stderr)
        sys.exit(2)
    role = sys.argv[1]

    root = Path.cwd()
    out: dict = {"cycle": 15, "role": role, "anchors": {}, "missing": []}
    for rel in ANCHORS:
        p = rel if rel.startswith("/") else str(root / rel)
        if not Path(p).exists():
            out["missing"].append(rel)
            continue
        h, sz = sha256_of(p)
        out["anchors"][rel] = {"sha256": h, "size": sz}
    out["n_anchors"] = len(out["anchors"])
    out["n_missing"] = len(out["missing"])

    dst_name = f"anchor_preservation_{role}_c15.json"
    dst_dir = root / "data/v3_spine/cycle15"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / dst_name
    dst.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")

    if role == "post":
        pre_path = dst_dir / "anchor_preservation_pre_c15.json"
        pre = json.loads(pre_path.read_text())
        diffs = []
        for rel, meta in pre["anchors"].items():
            if rel not in out["anchors"]:
                diffs.append({"path": rel, "reason": "missing_post"})
                continue
            if meta["sha256"] != out["anchors"][rel]["sha256"]:
                diffs.append({
                    "path": rel,
                    "pre_sha": meta["sha256"],
                    "post_sha": out["anchors"][rel]["sha256"],
                })
        report = {
            "cycle": 15,
            "n_pre": len(pre["anchors"]),
            "n_post": len(out["anchors"]),
            "n_diff": len(diffs),
            "all_match": len(diffs) == 0 and len(pre["anchors"]) == len(out["anchors"]),
            "diffs": diffs,
        }
        report_path = dst_dir / "anchor_preservation_c15.json"
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(f"post: n_pre={report['n_pre']} n_post={report['n_post']} "
              f"n_diff={report['n_diff']} all_match={report['all_match']}")
    else:
        print(f"pre: n_anchors={out['n_anchors']} n_missing={out['n_missing']}")
    if out["n_missing"] > 0:
        print("MISSING:", out["missing"], file=sys.stderr)


if __name__ == "__main__":
    main()
