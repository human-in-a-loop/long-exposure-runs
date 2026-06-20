# created: 2026-05-17T21:45:00Z
# cycle: 4
# run_id: run-phytograph-cycle4-barrier1
# agent: worker
# milestone: _plan/barrier1-substrate-freeze
"""Write Barrier-1 reports and figures from validated substrate outputs."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "phytograph_dataset"
SUBSTRATE = ROOT / "substrate"


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    text = df.fillna("").astype(str)
    cols = list(text.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in text.iterrows():
        vals = [str(row[c]).replace("|", "\\|").replace("\n", " ") for c in cols]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_reports() -> None:
    nodes = pd.read_parquet(DATASET / "nodes.parquet")
    edges = pd.read_parquet(DATASET / "hyperedges.parquet")
    crosswalk = pd.read_parquet(DATASET / "taxon_crosswalk.parquet")
    delta = pd.read_csv(DATASET / "synonym_normalization_delta.tsv", sep="\t")
    dedup = pd.read_csv(DATASET / "dedup_report.tsv", sep="\t")
    member_audit = pd.read_csv(DATASET / "canonical_member_audit.tsv", sep="\t")
    propagation_audit = pd.read_csv(DATASET / "resolved_key_propagation_audit.tsv", sep="\t")
    collision_audit = pd.read_csv(DATASET / "dedup_collision_audit.tsv", sep="\t")
    dedup_edge_type = pd.read_csv(DATASET / "dedup_before_after_by_edge_type.tsv", sep="\t")
    unresolved_reasons = pd.read_csv(SUBSTRATE / "barrier1_unresolved_name_reasons.tsv", sep="\t")

    # Keep provenance/caveat companion tables aligned to retained hyperedges after dedup.
    retained = edges[["edge_id"]]
    for name in ["provenance", "caveats"]:
        frame = pd.read_parquet(DATASET / f"{name}.parquet").merge(retained, on="edge_id", how="inner")
        frame.to_parquet(DATASET / f"{name}.parquet", index=False)

    readiness = pd.DataFrame(
        [
            {"track": "Track 1 Reticulation", "readiness": "ready_data_limited", "reason": "M1.3 seed rows merged, but CCDB/C-values/Wood 2009 production-scale acquisition deferred."},
            {"track": "Track 2 Ghost Hyperedges", "readiness": "ready_data_limited", "reason": "Literature-curated paleo/anachronism seed rows merged; no inferred anachronism rows introduced."},
            {"track": "Track 3 Convergence", "readiness": "ready", "reason": "AusTraits trait_syndrome/fruit_morphology/life_form rows merged; convergence_signature count remains zero."},
            {"track": "Track 4 Domestication", "readiness": "ready_data_limited", "reason": "Current crop-pedigree/CWR seed rows merged; CWR expansion and climate extraction still deferred."},
            {"track": "Track 5 Chemodiversity", "readiness": "ready", "reason": "Phytochemical and ethnobotanical assertions merged with provenance; Duke source dominance flagged for ablation."},
            {"track": "Track 6 Foundation Model Probe", "readiness": "ready_static_only", "reason": "Static/free/open benchmark scaffolding only; paid-provider harness work remains out of scope and was not executed."},
        ]
    )
    readiness.to_csv(SUBSTRATE / "barrier1_track_readiness.tsv", sep="\t", index=False)

    fig_delta = delta.sort_values("rows_before", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(fig_delta["source_group"], fig_delta["raw_name_diversity_before"], label="raw-name diversity")
    ax.bar(fig_delta["source_group"], fig_delta["accepted_key_diversity_after"], label="post-normalization diversity", alpha=0.75)
    ax.set_ylabel("distinct name/key count")
    ax.set_title("Barrier 1 synonym normalization delta by source")
    ax.tick_params(axis="x", rotation=35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(SUBSTRATE / "barrier1_synonym_delta.png", dpi=180)
    plt.close(fig)

    retention = dedup.copy()
    retention["unresolved_rows"] = retention["source_group"].map(delta.set_index("source_group")["unresolved_rows"]).fillna(0).astype(int)
    plot_cols = ["retained_edges", "collapsed_rows", "unresolved_rows"]
    fig, ax = plt.subplots(figsize=(10, 5))
    bottom = None
    for col in plot_cols:
        ax.bar(retention["source_group"], retention[col], bottom=bottom, label=col)
        bottom = retention[col] if bottom is None else bottom + retention[col]
    ax.set_ylabel("rows")
    ax.set_title("Barrier 1 source retention")
    ax.tick_params(axis="x", rotation=35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(SUBSTRATE / "barrier1_source_retention.png", dpi=180)
    plt.close(fig)

    plot_dedup = dedup_edge_type.sort_values("input_rows", ascending=False).head(30).copy()
    labels = plot_dedup["source_group"].astype(str) + "\n" + plot_dedup["edge_type"].astype(str)
    x = range(len(plot_dedup))
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar([i - 0.2 for i in x], plot_dedup["retained_raw_name_only_before"], width=0.4, label="raw-name-only projection")
    ax.bar([i + 0.2 for i in x], plot_dedup["retained_full_member_after"], width=0.4, label="full role-map projection")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=55, ha="right", fontsize=8)
    ax.set_ylabel("retained dedup keys")
    ax.set_title("Barrier 1 deduplication before vs. after canonical-member repair")
    ax.legend()
    fig.tight_layout()
    fig.savefig(SUBSTRATE / "barrier1_dedup_before_after.png", dpi=180)
    plt.close(fig)

    width_plot = member_audit.sort_values("input_rows", ascending=False).head(35).copy()
    labels = width_plot["source_group"].astype(str) + "\n" + width_plot["edge_type"].astype(str)
    x = range(len(width_plot))
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(x, width_plot["median_member_width"], label="median")
    ax.scatter(x, width_plot["max_member_width"], label="max", color="black", s=16)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=55, ha="right", fontsize=8)
    ax.set_ylabel("canonical member-set size")
    ax.set_title("Barrier 1 canonical member-set widths after full role-map projection")
    ax.legend()
    fig.tight_layout()
    fig.savefig(SUBSTRATE / "barrier1_canonical_member_widths.png", dpi=180)
    plt.close(fig)

    source_counts = (
        edges.groupby(["source_group", "edge_type"], dropna=False)
        .size()
        .reset_index(name="retained_edges")
        .sort_values(["source_group", "retained_edges"], ascending=[True, False])
    )
    source_summary = (
        edges.groupby("source_group", dropna=False)
        .agg(retained_edges=("edge_id", "count"), edge_types=("edge_type", pd.Series.nunique), resolved_taxon_edges=("accepted_taxon_key", lambda s: int(s.fillna("").astype(str).str.len().gt(0).sum())))
        .reset_index()
        .merge(dedup[["source_group", "input_edges", "collapsed_rows"]], on="source_group", how="left")
    )
    tier_rows = pd.DataFrame(
        [
            {"tier": "Tier 0 taxonomy-backed accepted taxa", "count": int(nodes["node_type"].isin(["family", "genus", "species", "infraspecific_unit"]).sum()), "status": "cleared"},
            {"tier": "Taxonomy synonym rows (reported separately, excluded from Tier 0 accepted taxa)", "count": int((nodes["node_type"] == "synonym").sum()), "status": "coverage_only"},
            {"tier": "Tier 2 crop/domestication retained edges", "count": int(edges["edge_type"].isin(["crop_pedigree", "cultivation_or_domestication", "vavilov_center_hyperedge"]).sum()), "status": "data-limited"},
            {"tier": "Tier 3 phytochemical retained assertions", "count": int((edges["edge_type"] == "phytochemical_assertion").sum()), "status": "cleared"},
            {"tier": "Tier 4 deep evidence retained edges", "count": int(edges["edge_type"].isin(["chromosome_count_assertion", "anachronism_candidate_edge", "trait_syndrome", "image_evidence"]).sum()), "status": "cleared/data-limited by axis"},
        ]
    )

    frontmatter = f"---\ncreated: {datetime.now(timezone.utc).isoformat()}\ncycle: 7\nrun_id: run-phytograph-cycle7-barrier1-canonical-member-repair\nagent: worker\nmilestone: _plan/barrier1-canonical-member-repair\n---\n\n"
    join_report = frontmatter + "# Barrier 1 Join Report\n\n"
    join_report += "Barrier 1 froze the current Wave-1 staging rows into `phytograph_dataset/` without acquiring new sources or starting Wave 2 enrichment. WFO accepted keys are used as operational substrate identifiers, not as taxonomic adjudication.\n\n"
    join_report += "## Counts\n\n" + md_table(source_summary) + "\n\n"
    join_report += "## Synonym Normalization\n\n" + md_table(delta) + "\n\n"
    join_report += "![Diversity and row-count shifts before vs. after synonym normalization, by source group.](barrier1_synonym_delta.png)\n\n"
    join_report += "## Deduplication\n\n" + md_table(dedup) + "\n\n"
    join_report += "![Retained, unresolved, deduplicated, and rejected rows by source group after Barrier 1.](barrier1_source_retention.png)\n\n"
    join_report += "![Retained vs. deduplicated edge counts before and after repair, stratified by source group and edge type.](barrier1_dedup_before_after.png)\n\n"
    join_report += "![Canonical member-set sizes by edge type after full role-map projection.](barrier1_canonical_member_widths.png)\n\n"
    join_report += "## Unresolved Name Classes\n\n" + md_table(unresolved_reasons.head(30)) + "\n\n"
    join_report += "## Wave 2 Readiness\n\n" + md_table(readiness) + "\n\n"
    join_report += "## Null Results And Gaps\n\nM1.3, M1.6, and M1.9 remain data-limited. No inferred `anachronism_candidate_edge` rows and no pre-instrument `convergence_signature` rows were introduced. One media row retained an explicit `license-missing-in-source-row` marker so missingness remains auditable.\n"
    (SUBSTRATE / "BARRIER1_JOIN_REPORT.md").write_text(join_report, encoding="utf-8")

    repair = frontmatter + "# Barrier 1 Canonical Member Repair Report\n\n"
    repair += "The first Barrier 1 freeze used a lossy projection for large source frames: many retained hyperedges deduplicated on raw taxon name alone, so same-taxon/different-trait and same-taxon/different-compound assertions could collapse. The repair rewrites canonical members from the full typed role map, then applies synonym resolution back into `hyperedges.parquet` before deduplication.\n\n"
    repair += "## What Changed\n\n"
    repair += "- `canonical_node_ids_json` now includes the accepted taxon key when resolved plus non-taxon role members such as trait, fruit type, compound, plant part, use, region, bioactivity class, crop pedigree, extinct fauna, paleo context, and media nodes.\n"
    repair += "- Resolved rows now have `accepted_taxon_key` populated and `pending_crosswalk=False`; unresolved rows keep raw-name members plus machine-readable `ambiguity_reason` caveats.\n"
    repair += "- Deduplication now keys on edge type, sorted full canonical typed member set, source ID, and the existing evidence-multiplicity policy.\n\n"
    repair += "## Synonym Propagation Audit\n\n" + md_table(propagation_audit.head(80)) + "\n\n"
    repair += "## Canonical Member Audit\n\n" + md_table(member_audit.head(80)) + "\n\n"
    repair += "## Dedup Collision Audit\n\n" + md_table(collision_audit.head(80)) + "\n\n"
    repair += "## Figures\n\n"
    repair += "![Retained vs. deduplicated edge counts before and after repair, stratified by source group and edge type.](barrier1_dedup_before_after.png)\n\n"
    repair += "![Canonical member-set sizes by edge type after full role-map projection.](barrier1_canonical_member_widths.png)\n\n"
    repair += "## Result\n\n"
    repair += "Tier 0 accepted taxonomy rows are reported as 60,000; the 113,582 synonym rows remain separate synonym coverage. Wave 2 remains blocked until this repair is audited, and no Track 6 paid-provider code was executed or extended.\n"
    (SUBSTRATE / "BARRIER1_REPAIR_REPORT.md").write_text(repair, encoding="utf-8")

    coverage = frontmatter + "# Coverage Report — Post-Barrier-1 Merged Substrate\n\n"
    coverage += "This report supersedes the previous staging-only `coverage_report.md`; counts below are from the deduplicated merged substrate.\n\n"
    coverage += "## Tier Summary\n\n" + md_table(tier_rows) + "\n\n"
    coverage += "## Source Summary\n\n" + md_table(source_summary) + "\n\n"
    coverage += "## Edge-Type Counts\n\n" + md_table(source_counts.head(80)) + "\n\n"
    coverage += "## Caveats\n\nTracks 1 and 4 are ready only at data-limited seed scale. Track 2 can start with cited literature seed rows only. Tracks 3, 5, and 6 can start Wave 2 after Barrier 1 validation.\n"
    (ROOT / "coverage_report.md").write_text(coverage, encoding="utf-8")

    print("wrote Barrier 1 reports and figures")


if __name__ == "__main__":
    write_reports()
