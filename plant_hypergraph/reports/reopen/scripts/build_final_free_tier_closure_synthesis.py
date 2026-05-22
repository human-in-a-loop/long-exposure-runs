#!/usr/bin/env python3
# created: 2026-05-18T23:59:59+00:00
# cycle: 33
# run_id: run-phytograph-cycle33-final-free-tier-closure-synthesis
# agent: worker
# milestone: _plan/final-free-tier-closure-synthesis

import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[3]
STATUS_PATH = ROOT / "data/reopen/final_free_tier_track_status.tsv"
REPORT_PATH = ROOT / "reports/reopen/final_free_tier_closure_synthesis.md"
FIGURE_PATH = ROOT / "reports/reopen/figures/final_free_tier_track_status.png"

ROWS = [
    {
        "track": "Track 1",
        "final_free_tier_status": "sidecar_readiness_uncontrolled",
        "validated_branch_basis": "Track 1 free-tier namespace reconciliation and sidecar control-strengthening",
        "key_counts": "22 GBIF event taxa; 11 source groups; 2 WFO-projected taxa; 0/17 matched-control event recovery",
        "blocker": "GBIF sidecar signal is not WFO-projected and source-density controls remain unresolved",
        "future_data_required": "Audited GBIF-to-WFO accepted-key projection or admitted sidecar namespace plus source-density controls preserving event signal",
        "master_ledger_action": "no_master_prediction_or_speculation_row; sidecar_readiness_only",
        "claim_boundary": "No established reticulation hotspot, hybridization, or polyploid recovery claim",
    },
    {
        "track": "Track 2",
        "final_free_tier_status": "H2_remains_not_supported_or_data_limited",
        "validated_branch_basis": "Track 2 free-tier ghost evidence/control closure",
        "key_counts": "8 canonical held-outs; 31 local candidates; 0/8 canonical held-outs pass validation contract",
        "blocker": "Accepted-key modern-failure evidence, source-class support, and living-megafauna controls do not clear the validation contract",
        "future_data_required": "Accepted-key modern-failure evidence, multi-source/source-class support, living-megafauna controls, and source-class-independent held-out recovery",
        "master_ledger_action": "no_master_prediction_or_speculation_row; validated_non_promotion",
        "claim_boundary": "No new anachronism, ghost-partner, or ecological-interaction claim",
    },
    {
        "track": "Track 3",
        "final_free_tier_status": "confound_limited",
        "validated_branch_basis": "Track 3 free-tier trait/confound matrix",
        "key_counts": "3069 accepted-key trait carrier rows; 15 canonical traits; 0 controlled-ready traits",
        "blocker": "No trait separates convergence signal from family-size, sampling-density, projection-loss, and source gates",
        "future_data_required": "Broader trait coverage, phylogenetically separated carrier sets, and family-size/sampling-density controls",
        "master_ledger_action": "no_master_prediction_or_speculation_row; validated_non_promotion",
        "claim_boundary": "No convergence or adaptive-origin claim",
    },
    {
        "track": "Track 4",
        "final_free_tier_status": "still_data_limited",
        "validated_branch_basis": "Track 4 free-tier occurrence/BIOCLIM recovery",
        "key_counts": "3358 post-filter occurrence records; 0 numeric BIOCLIM vectors; 0 validation-allowed comparator rows",
        "blocker": "Coordinate recovery did not yield numeric local/free BIOCLIM vectors or disjoint expert comparator rows",
        "future_data_required": "Audited crop/CWR BIOCLIM summaries and disjoint candidate-level expert comparator rows",
        "master_ledger_action": "no_master_prediction_or_speculation_row; validated_non_promotion",
        "claim_boundary": "No crop-substitution recommendation or climate-adaptation claim",
    },
    {
        "track": "Track 5",
        "final_free_tier_status": "H5_remains_source_biased",
        "validated_branch_basis": "Track 5 non-Duke temporal chemistry recovery and source ablation",
        "key_counts": "Non-Duke temporal evidence insufficient; no validation-ready structured family/class stratum",
        "blocker": "Open non-Duke detections do not support a structured temporal family/class predictor rerun independent of Duke/source density",
        "future_data_required": "Accepted-key, dated, non-Duke taxon-compound rows across enough families/classes to estimate signatures without source collapse",
        "master_ledger_action": "no_master_prediction_or_speculation_row; validated_non_promotion",
        "claim_boundary": "No new phytochemical, bioactivity, or screening-priority claim",
    },
    {
        "track": "Track 6",
        "final_free_tier_status": "environment_limited_untested",
        "validated_branch_basis": "Track 6 free/open/local execution reopen",
        "key_counts": "0 runnable local runtime-weight pairings; 0 executed responses; 0 scored responses",
        "blocker": "No approved local model runtime and weight pairing was available under the free/open/local constraint",
        "future_data_required": "Approved local model weights and runtime producing audited deterministic response rows with scorer diagnostics",
        "master_ledger_action": "no_master_prediction_or_speculation_row; validated_non_promotion",
        "claim_boundary": "No model error-rate, leaderboard, toxicity-look-alike, or vendor-comparison claim",
    },
]


def write_status() -> None:
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATUS_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ROWS[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(ROWS)


def write_report() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "created: 2026-05-18T23:59:59+00:00",
        "cycle: 33",
        "run_id: run-phytograph-cycle33-final-free-tier-closure-synthesis",
        "agent: worker",
        "milestone: _plan/final-free-tier-closure-synthesis",
        "---",
        "",
        "# Final Free-Tier Closure Synthesis",
        "",
        "## Scope",
        "",
        "This synthesis reconciles the strongest auditor-validated free-tier branch outcome for each PhytoGraph track. It does not perform new evidence search, change schema v1.0, alter branch science outputs, or write rows to the master `prediction_ledger.tsv` or `speculation_ledger.tsv`.",
        "",
        "The global result is conservative: PhytoGraph remains successful as infrastructure, instrumentation, Atlas, formal-diagnostic, and falsification/closure science, but the original criterion of at least one validated prediction per track remains unmet.",
        "",
        "## Canonical Status Table",
        "",
        "| Track | Final free-tier status | Validated evidence counts | Blocker | Future-data requirement | Claim boundary |",
        "|---|---|---|---|---|---|",
    ]
    for row in ROWS:
        lines.append(
            f"| {row['track']} | `{row['final_free_tier_status']}` | {row['key_counts']} | {row['blocker']} | {row['future_data_required']} | {row['claim_boundary']} |"
        )
    lines.extend(
        [
            "",
            "![Final free-tier closure status for all six PhytoGraph tracks, distinguishing sidecar-readiness, not-supported, confound-limited, data-limited, source-biased, and environment-limited outcomes.](figures/final_free_tier_track_status.png)",
            "",
            "## Master-Ledger Boundary",
            "",
            "The master `prediction_ledger.tsv` and `speculation_ledger.tsv` remain header-only. This is a validated non-promotion decision, not an omission: every free-tier track has at least one failed validation predicate, unresolved control, source-bias collapse, or execution blocker.",
            "",
            "No final synthesis artifact promotes new taxonomy, reticulation, anachronism, convergence, climate-substitution, phytochemical, bioactivity, or model-performance claims. Track-local artifacts remain useful diagnostics and candidate-prior records, but they do not satisfy the cross-track promotion contract.",
            "",
            "## Future-Data Recipes",
            "",
        ]
    )
    for row in ROWS:
        lines.append(f"- {row['track']}: {row['future_data_required']}.")
    lines.extend(
        [
            "",
            "These predicates are intentionally specific enough to prevent another same-axis free-tier retry. A future reopen should vary the missing data axis rather than rerunning the same branch inputs.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_figure(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    colors = {
        "sidecar_readiness_uncontrolled": "#4c78a8",
        "H2_remains_not_supported_or_data_limited": "#e45756",
        "confound_limited": "#f58518",
        "still_data_limited": "#72b7b2",
        "H5_remains_source_biased": "#b279a2",
        "environment_limited_untested": "#54a24b",
    }
    fig, ax = plt.subplots(figsize=(11, 5.5))
    labels = [row["track"].replace(" ", "\n") for row in ROWS]
    values = [1] * len(ROWS)
    bar_colors = [colors[row["final_free_tier_status"]] for row in ROWS]
    bars = ax.bar(labels, values, color=bar_colors, edgecolor="#222222", linewidth=0.8)
    ax.set_ylim(0, 1.35)
    ax.set_yticks([])
    ax.set_title("Final Free-Tier Closure Status by Track")
    ax.set_xlabel("PhytoGraph track")
    ax.spines[["left", "right", "top"]].set_visible(False)
    ax.spines["bottom"].set_color("#444444")
    for bar, row in zip(bars, ROWS):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            1.04,
            row["final_free_tier_status"].replace("_", "\n"),
            ha="center",
            va="bottom",
            fontsize=8,
        )
    fig.text(
        0.02,
        0.02,
        "Final free-tier closure status for all six PhytoGraph tracks, distinguishing sidecar-readiness, not-supported, confound-limited, data-limited, source-biased, and environment-limited outcomes.",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.07, 1, 1])
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def main() -> None:
    figure_out = os.environ.get("FIGURE_OUT")
    if figure_out:
        write_figure(Path(figure_out))
        return
    write_status()
    write_report()


if __name__ == "__main__":
    main()
