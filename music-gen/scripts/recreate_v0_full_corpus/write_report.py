#!/usr/bin/python3
# ---
# created: 2026-08-29T12:35:00Z
# cycle: 39
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/full-corpus-recreation
# fork: c320de981fda
# clone: 0
# ---
"""Auto-generate docs/recreate_v0_full_corpus_report.md from the on-disk
verdict.json, cross-band tables, and per-song stage manifests. Every
per-song block carries the preview_untrained_ear literal caveat citing
docs/ear_real_label_training_v1_report.md by document-path only."""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "data" / "recreate_v0_full_corpus"
REPORT = REPO_ROOT / "docs" / "recreate_v0_full_corpus_report.md"

PREVIEW_CAVEAT = (
    "preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict "
    "EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; "
    "43/80 corpus coverage) — see "
    "docs/ear_real_label_training_v1_report.md — this pipeline does NOT "
    "compute per-song ear predictions"
)


def _fmt(v, nd=4):
    if v is None:
        return "n/a"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, (int, float)):
        return f"{v:.{nd}f}"
    return str(v)


def main() -> int:
    verdict = json.loads((DATA_ROOT / "verdict.json").read_text())
    chosen = json.loads((DATA_ROOT / "chosen_songs_full.json").read_text())
    corr = json.loads((DATA_ROOT / "cross_band_correlation.json").read_text())
    anchor_pres = json.loads((DATA_ROOT / "anchor_preservation.json").read_text())
    all_results = json.loads((DATA_ROOT / "all_results.json").read_text())

    findings = verdict["per_song_findings"]
    findings_by_sha = {f["sha16"]: f for f in findings}
    results_by_sha = {r["sha16"]: r for r in all_results}

    walls = [f.get("run1_wall_clock_s") for f in findings
             if f.get("run1_wall_clock_s") is not None]
    wall_median = statistics.median(walls) if walls else None
    wall_max = max(walls) if walls else None

    early_exit_songs = [f for f in findings
                        if f.get("run1_failed_stage") == "early_exit:wall_clock_exceeded"]

    lines: list[str] = []
    lines.append("---")
    lines.append("created: 2026-08-29T14:00:00Z")
    lines.append("cycle: 39")
    lines.append("run_id: run-2026-08-28T040704Z")
    lines.append("agent: worker")
    lines.append("milestone: M-RECREATE-1/full-corpus-recreation")
    lines.append("fork: c320de981fda")
    lines.append("clone: 0")
    lines.append("---")
    lines.append("")
    lines.append("# M-RECREATE-1/full-corpus-recreation — Report")
    lines.append("")
    lines.append("First full-G1-spine measurement on real rated audio at "
                 "scale: 37 songs across bands 4/5/6/7, extending "
                 "cycle-37 clone-0's 1-song `RECREATION_LANDS` and "
                 "cycle-38 clone-2's 5-song `BATCH_LANDS`.")
    lines.append("")
    # ---- Verdict
    lines.append("## 1. Verdict")
    lines.append("")
    lines.append(f"**{verdict['verdict']}** — {verdict['reason']}")
    lines.append("")
    lines.append(f"- `rubric_hash`: `{verdict['rubric_hash']}` "
                 f"(byte-equal to `data/recreate_v0_full_corpus/rubric_hash.txt`)")
    lines.append(f"- Rubric verdicts: {verdict['rubric_verdicts']}")
    lines.append(f"- LANDS threshold (positive mel delta): "
                 f">= {verdict['lands_threshold_positive_mel_delta']}/37 "
                 f"(~89%)")
    lines.append("")

    # ---- Song selection
    lines.append("## 2. Song selection")
    lines.append("")
    lines.append(f"- Selection rule: `{chosen['selection_rule']}`")
    lines.append(f"- n_candidates_after_exclusion: {chosen['n_candidates_after_exclusion']}")
    lines.append(f"- n_chosen: {chosen['n_chosen']}")
    lines.append(f"- Per-bucket counts: {chosen['per_bucket_counts']}")
    lines.append("")
    lines.append("### Exclusion set (6 songs)")
    lines.append("")
    for rel in chosen["exclusion_set"]:
        lines.append(f"- `{rel}`")
    lines.append("")
    lines.append("### 37-song canonical order (ascending SHA-256)")
    lines.append("")
    lines.append("| # | band | file_sha256[:16] | mp3 bytes | relpath |")
    lines.append("|---|------|------------------|-----------|---------|")
    for entry in chosen["chosen_songs"]:
        lines.append(f"| {entry['canonical_index']} | {entry['rating_bucket']} | "
                     f"`{entry['file_sha256'][:16]}` | "
                     f"{entry['mp3_bytes']} | `{entry['relpath']}` |")
    lines.append("")

    # ---- Per-band summary
    lines.append("## 3. Per-band summary")
    lines.append("")
    lines.append("| band | n_total | n_pipeline_ok | n_byte_det_ok | "
                 "n_positive_mel_delta |")
    lines.append("|------|---------|---------------|---------------|---------------------|")
    for band, s in verdict["per_band_summary"].items():
        lines.append(f"| {band} | {s['n_total']} | {s['n_pipeline_ok']} | "
                     f"{s['n_byte_det_ok']} | {s['n_positive_mel_delta']} |")
    lines.append("")

    # ---- Per-song blocks
    lines.append("## 4. Per-song results")
    lines.append("")
    for entry in chosen["chosen_songs"]:
        sha16 = entry["file_sha256"][:16]
        f = findings_by_sha.get(sha16, {})
        r = results_by_sha.get(sha16, {})
        p = r.get("panels", {}) or {}
        pb = p.get("original_vs_bare", {}) or {}
        pe = p.get("original_vs_effects", {}) or {}
        det = r.get("determinism", {}) or {}
        per_anchor = det.get("per_anchor", {}) or {}

        def _mel_d():
            b, e = pb.get("mel_l1_db"), pe.get("mel_l1_db")
            if isinstance(b, (int, float)) and isinstance(e, (int, float)):
                return b - e
            return None

        def _sc_d():
            b, e = pb.get("spectral_centroid_rmse_hz"), pe.get("spectral_centroid_rmse_hz")
            if isinstance(b, (int, float)) and isinstance(e, (int, float)):
                return b - e
            return None

        def _rms_d():
            b, e = pb.get("rms_env_rmse"), pe.get("rms_env_rmse")
            if isinstance(b, (int, float)) and isinstance(e, (int, float)):
                return b - e
            return None

        def _lufs_d():
            b, e = pb.get("lufs_m_rmse_lu"), pe.get("lufs_m_rmse_lu")
            if isinstance(b, (int, float)) and isinstance(e, (int, float)):
                return b - e
            return None

        lines.append(f"### Song {entry['canonical_index']}: "
                     f"band {entry['rating_bucket']}, sha `{sha16}`")
        lines.append("")
        lines.append(f"- relpath: `{entry['relpath']}`")
        lines.append(f"- file_sha256: `{entry['file_sha256']}`")
        lines.append(f"- run1 wall_clock_s: {_fmt(f.get('run1_wall_clock_s'), 2)}")
        lines.append(f"- run2 wall_clock_s: {_fmt(f.get('run2_wall_clock_s'), 2)}")
        lines.append(f"- run1_failed_stage: `{f.get('run1_failed_stage')}`")
        lines.append(f"- byte-determinism x 2 (all 4 anchors): "
                     f"**{_fmt(f.get('byte_det_x2'))}**")
        if per_anchor:
            lines.append("")
            lines.append("| anchor | run1 sha[:16] | run2 sha[:16] | equal |")
            lines.append("|--------|---------------|---------------|-------|")
            for anchor, d in per_anchor.items():
                r1 = d.get("run1", "MISSING")
                r2 = d.get("run2", "MISSING")
                lines.append(f"| `{anchor}` | `{r1[:16] if isinstance(r1, str) else r1}` "
                             f"| `{r2[:16] if isinstance(r2, str) else r2}` | "
                             f"{'yes' if d.get('equal') else 'no'} |")
        lines.append("")
        lines.append(f"- M-TEX-1 panel deltas (bare − effects; "
                     f"positive = effects narrows the gap):")
        lines.append(f"  - `mel_l1_db`: bare {_fmt(pb.get('mel_l1_db'))}, "
                     f"effects {_fmt(pe.get('mel_l1_db'))}, "
                     f"delta **{_fmt(_mel_d())}**")
        lines.append(f"  - `spectral_centroid_rmse_hz`: bare {_fmt(pb.get('spectral_centroid_rmse_hz'))}, "
                     f"effects {_fmt(pe.get('spectral_centroid_rmse_hz'))}, "
                     f"delta {_fmt(_sc_d())}")
        lines.append(f"  - `rms_env_rmse`: bare {_fmt(pb.get('rms_env_rmse'))}, "
                     f"effects {_fmt(pe.get('rms_env_rmse'))}, "
                     f"delta {_fmt(_rms_d())}")
        lines.append(f"  - `lufs_m_rmse_lu`: bare {_fmt(pb.get('lufs_m_rmse_lu'))}, "
                     f"effects {_fmt(pe.get('lufs_m_rmse_lu'))}, "
                     f"delta {_fmt(_lufs_d())}")
        lines.append("")
        # Stage manifest: pretty_midi_fallback used?
        sm_path = DATA_ROOT / "per_song" / str(entry["rating_bucket"]) / sha16 / "stage_manifest.json"
        pmi = None
        if sm_path.exists():
            sm = json.loads(sm_path.read_text())
            pmi = sm.get("pretty_midi_fallback_used_run1")
        lines.append(f"- pretty_midi_fallback_used_run1: `{pmi}`")
        lines.append("")
        lines.append(f"- {PREVIEW_CAVEAT}")
        lines.append("")

    # ---- Cross-band tables (summary)
    lines.append("## 5. Cross-band tables (n=37, n=42 pooled, n=43 pooled)")
    lines.append("")
    lines.append("Full tables in `data/recreate_v0_full_corpus/cross_band_"
                 "{n37,pooled_n42,pooled_n43}.tsv`.")
    lines.append("")
    for label, path_tail in (("n=37 (this branch only)", "cross_band_n37.tsv"),
                             ("n=42 (this branch + c38 clone-2's 5)", "cross_band_pooled_n42.tsv"),
                             ("n=43 (this branch + c38 clone-2's 5 + c37 clone-0's 1)",
                              "cross_band_pooled_n43.tsv")):
        p = DATA_ROOT / path_tail
        lines.append(f"### {label}")
        if p.exists():
            rows = p.read_text().strip().split("\n")
            lines.append(f"- rows (excluding header): {len(rows) - 1}")
            lines.append(f"- path: `data/recreate_v0_full_corpus/{path_tail}`")
        lines.append("")

    # ---- Correlations
    lines.append("## 6. Cross-band correlations")
    lines.append("")
    lines.append("Per-metric Pearson r + Spearman ρ of the four family "
                 "metric deltas vs band index, at n=37, n=42, n=43. "
                 "Every row carries the literal `n_too_small` caveat.")
    lines.append("")
    for label in ("n=37", "n=42_pooled", "n=43_pooled"):
        entries = corr.get(label, [])
        lines.append(f"### {label}")
        lines.append("")
        lines.append("| delta_key | n | n_finite | pearson_r | spearman_rho |")
        lines.append("|-----------|---|----------|-----------|--------------|")
        for row in entries:
            lines.append(f"| `{row['delta_key']}` | {row['n']} | {row['n_finite']} "
                         f"| {_fmt(row['pearson_r'])} | {_fmt(row['spearman_rho'])} |")
        lines.append("")
        for row in entries:
            lines.append(f"  - `{row['delta_key']}` caveat: "
                         f"`{row['n_too_small_caveat']}`")
        lines.append("")

    # ---- Byte-determinism summary
    lines.append("## 7. Byte-determinism summary")
    lines.append("")
    lines.append(f"- Total anchors: {verdict.get('n_byte_det_anchors_total')} "
                 f"(37 songs x 4 anchors)")
    lines.append(f"- Anchors equal: {verdict.get('n_byte_det_anchors_ok')}")
    if verdict.get("per_anchor_byte_det_failures"):
        lines.append("- Per-anchor failures:")
        for f in verdict["per_anchor_byte_det_failures"]:
            lines.append(f"  - band {f['band']} sha `{f['song_sha16']}` "
                         f"anchor `{f['anchor']}`")
    lines.append("")

    # ---- Anchor preservation
    lines.append("## 8. Anchor preservation")
    lines.append("")
    lines.append(f"- {anchor_pres['n_anchors']} anchors tracked")
    lines.append(f"- unchanged: {anchor_pres['unchanged']}")
    if anchor_pres.get("changed"):
        lines.append("- Changed:")
        for k in sorted(anchor_pres["changed"].keys()):
            lines.append(f"  - `{k}`")
    lines.append("")
    lines.append("Tracked anchor categories:")
    lines.append("- c37 `scripts/recreate_v0/*.py` + data + report")
    lines.append("- c38 clone-2 `scripts/recreate_v0_batch/*.py` + data + reports")
    lines.append("- c38 clone-0 v1 report (doc-path reference)")
    lines.append("- c38 clone-1 score-bridge + normalizer-v2 reports (doc-path references)")
    lines.append("- c8 `scripts/score/bridge.py`")
    lines.append("- c9 `scripts/tex/render_effects_layered.py`")
    lines.append("")

    # ---- Compute budget
    lines.append("## 9. Compute budget")
    lines.append("")
    lines.append(f"- Per-song run-1 median wall-clock: "
                 f"{_fmt(wall_median, 2)} s")
    lines.append(f"- Per-song run-1 max wall-clock: {_fmt(wall_max, 2)} s")
    lines.append(f"- Early-exit threshold (6x c38 clone-2 median 82.2 s): 493.2 s")
    lines.append(f"- Early-exit count: {len(early_exit_songs)}")
    if early_exit_songs:
        lines.append("- Songs that early-exited:")
        for f in early_exit_songs:
            lines.append(f"  - band {f['band']} sha `{f['sha16']}` "
                         f"observed {_fmt(f.get('run1_wall_clock_s'), 1)} s")
    lines.append("")

    # ---- Interpretation
    lines.append("## 10. Interpretation")
    lines.append("")
    verdict_str = verdict["verdict"]
    n_pos = verdict["n_positive_mel_delta"]
    n_song = verdict["n_songs"]
    if verdict_str == "FULL_CORPUS_LANDS":
        lines.append("The c37 8-stage recreation spine generalizes across "
                     "all four rating bands at n=43 (37 songs new + 6 "
                     "pooled). The effects-layer benefit is consistent: "
                     f"{n_pos}/{n_song} songs show positive `mel_l1_db` "
                     "delta.")
    elif verdict_str == "FULL_CORPUS_PARTIAL":
        lines.append("The recreation spine works for the majority of the "
                     "corpus but has documented failures at the per-song "
                     "level. See §3 for per-band attribution and §4 for "
                     "per-song attribution. First-class negative-finding "
                     "delivery per rubric (silent song drops FORBIDDEN).")
    else:
        lines.append("The recreation spine does NOT generalize across the "
                     "43-song rated corpus at the required LANDS "
                     "thresholds. See §3 + §4 for per-song / per-band "
                     "attribution. c37 anchor drift audit and operator "
                     "conversation about corpus quality are the c40 "
                     "handoff seeds.")
    lines.append("")
    lines.append("### Cross-cycle comparison")
    lines.append("")
    lines.append("- c37 clone-0 (n=1): band 7 `RECREATION_LANDS`, "
                 "mel_l1_db_delta = +5.906 dB")
    lines.append("- c38 clone-2 (n=5): bands 4/5/6/7, `BATCH_LANDS`, "
                 "mel_l1_db deltas +2.879 to +7.983 dB (mean +5.04)")
    lines.append(f"- c39 clone-0 (n={n_song}): full-corpus extension, "
                 f"verdict `{verdict_str}`, "
                 f"{n_pos}/{n_song} positive mel deltas")
    lines.append("")

    # ---- c40 handoff
    lines.append("## 11. c40 handoff seeds")
    lines.append("")
    if verdict_str == "FULL_CORPUS_LANDS":
        lines.append("- Depending on n=43 correlation gradient shape:")
        lines.append("  - If mel_l1_db_delta shows a band-gradient → seed "
                     "`_manager/effects-chain-band-selectivity` as urgent "
                     "for c40.")
        lines.append("  - If flat → G1 recreation spine is band-agnostic; "
                     "seed `M-RULES-1/extraction/rated-corpus` (rule "
                     "extraction on real-audio-derived MusicXML at scale).")
    elif verdict_str == "FULL_CORPUS_PARTIAL":
        lines.append("- Per-band failure attribution and specific c40 "
                     "tickets for named-song reruns (see §3 + §4).")
    else:
        lines.append("- Recreation spine cannot generalize; seed operator "
                     "conversation about corpus quality / c37 anchor "
                     "drift audit.")
    lines.append("")
    lines.append("### Standing c40 references (regardless of verdict)")
    lines.append("")
    lines.append("- `_manager/fanout-namespace-convention-discrepancy` "
                 "still open (c39 Branch C addresses in parallel).")
    lines.append("- c38 clone-1 `QUANTIZATION_REDEFINED_GAP` + "
                 "normalizer-v2 REFUTED — mscore3 quantization root-cause "
                 "narrows to `<time-modification>` tuplets / "
                 "ties-across-measures / `<beat-unit-dot>`; c40 "
                 "opportunistic only.")
    lines.append("- c37 VST3 activation still gated by c36 MIXED verdict.")
    lines.append("- Egress retry per campaign directive: "
                 "`workspace/harvest_playlists.sh` should be retried; "
                 "two consecutive `media_ok=true` unblocks corpus "
                 "expansion to the full 80 rated songs.")
    lines.append("")

    REPORT.write_text("\n".join(lines) + "\n")
    print(f"wrote {REPORT} ({len(lines)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
