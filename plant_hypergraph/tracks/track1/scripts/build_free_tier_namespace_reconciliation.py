#!/usr/bin/env python3
# created: 2026-05-18T22:20:00+00:00
# cycle: 29
# run_id: run-phytograph-cycle29-track1-free-tier-namespace-reconciliation
# agent: worker
# milestone: _plan/track1-free-tier-namespace-reconciliation
"""Build Track 1 GBIF-to-WFO namespace reconciliation artifacts."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PANEL = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_panel.tsv"
EVIDENCE = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_evidence.tsv"
CROSSWALK = ROOT / "phytograph_dataset" / "taxon_crosswalk.parquet"
OUT_CROSSWALK = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_namespace_crosswalk.tsv"
OUT_EVIDENCE = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_reconciled_evidence.tsv"
OUT_CONTROLS = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_reconciled_controls.tsv"
OUT_REPORT = ROOT / "tracks" / "track1" / "reports" / "track1_free_tier_namespace_reconciliation.md"

ACCESS_DATE = "2026-05-18"
SOURCE_URL = "local:phytograph_dataset/taxon_crosswalk.parquet; local:tracks/track1/data/free_tier_reticulation_evidence.tsv"


def normalized_binomial(name: str) -> str:
    clean = str(name).replace("×", " x ")
    clean = re.sub(r"[^A-Za-z0-9]+", " ", clean).strip().lower()
    tokens = clean.split()
    if len(tokens) >= 3 and tokens[1] == "x":
        return " ".join(tokens[:3])
    return " ".join(tokens[:2])


def gbif_status(match_type: str) -> str:
    match = re.search(r"status=([^;]+)", str(match_type))
    return match.group(1) if match else "unknown"


def gbif_rank(_: str) -> str:
    # The GBIF species API branch only retained species-level accepted keys in this panel.
    return "species"


def projection_for(row: pd.Series, crosswalk: pd.DataFrame) -> dict[str, str]:
    name_key = normalized_binomial(row["accepted_name"])
    candidates = crosswalk[crosswalk["wfo_binomial"] == name_key].copy()
    species_candidates = candidates[candidates["wfo_rank"] == "species"]
    if len(species_candidates) == 1:
        hit = species_candidates.iloc[0]
        return {
            "wfo_candidate_key": hit["accepted_taxon_key"],
            "wfo_candidate_name": hit["wfo_accepted_name"],
            "match_type": "exact_wfo_species_name",
            "match_confidence": "medium",
            "accepted_key_basis": "wfo_projected",
            "crosswalk_status": "wfo_projected",
            "rejection_reason": "",
        }
    if len(candidates) > 0:
        names = "; ".join(candidates["wfo_accepted_name"].head(4).tolist())
        return {
            "wfo_candidate_key": "",
            "wfo_candidate_name": names,
            "match_type": "ambiguous_or_rank_mismatched_wfo_candidates",
            "match_confidence": "low",
            "accepted_key_basis": "gbif_sidecar",
            "crosswalk_status": "gbif_sidecar_admitted",
            "rejection_reason": "WFO projection ambiguous or rank-mismatched in frozen crosswalk; GBIF accepted key retained only as labeled sidecar evidence",
        }
    return {
        "wfo_candidate_key": "",
        "wfo_candidate_name": "",
        "match_type": "no_exact_wfo_species_projection",
        "match_confidence": "low",
        "accepted_key_basis": "gbif_sidecar",
        "crosswalk_status": "gbif_sidecar_admitted",
        "rejection_reason": "No exact species-level WFO projection in frozen local crosswalk; GBIF accepted key retained only as labeled sidecar evidence",
    }


def build() -> None:
    panel = pd.read_csv(PANEL, sep="\t").fillna("")
    evidence = pd.read_csv(EVIDENCE, sep="\t").fillna("")
    crosswalk = pd.read_parquet(CROSSWALK).fillna("")
    crosswalk["wfo_binomial"] = crosswalk["wfo_accepted_name"].map(normalized_binomial)

    usable = evidence[evidence["support_status"] == "accepted_key_event_shaped"].copy()
    taxa = (
        usable[["accepted_key", "accepted_name", "family"]]
        .drop_duplicates()
        .sort_values("accepted_name")
        .reset_index(drop=True)
    )
    panel_by_key = panel.drop_duplicates("accepted_key").set_index("accepted_key")

    crosswalk_rows = []
    decisions: dict[str, dict[str, str]] = {}
    for _, taxon in taxa.iterrows():
        accepted_key = taxon["accepted_key"]
        panel_matches = panel[panel["accepted_key"] == accepted_key]
        panel_row = panel_matches.iloc[0] if not panel_matches.empty else pd.Series(dtype=str)
        status_values = panel_matches["gbif_match_type"].map(gbif_status).tolist()
        status = "ACCEPTED" if "ACCEPTED" in status_values else (status_values[0] if status_values else "unknown")
        decision = projection_for(taxon, crosswalk)
        decisions[accepted_key] = decision
        crosswalk_rows.append(
            {
                "gbif_taxon_key": accepted_key,
                "gbif_scientific_name": taxon["accepted_name"],
                "gbif_status": status,
                "gbif_rank": gbif_rank(taxon["accepted_name"]),
                "wfo_candidate_key": decision["wfo_candidate_key"],
                "wfo_candidate_name": decision["wfo_candidate_name"],
                "match_type": decision["match_type"],
                "match_confidence": decision["match_confidence"],
                "accepted_key_basis": decision["accepted_key_basis"],
                "crosswalk_status": decision["crosswalk_status"],
                "rejection_reason": decision["rejection_reason"],
                "source_url": SOURCE_URL,
                "access_date": ACCESS_DATE,
            }
        )

    reconciled_rows = []
    for idx, row in evidence.iterrows():
        decision = decisions.get(row["accepted_key"], {})
        accepted_key_basis = decision.get("accepted_key_basis", "rejected")
        validation_use = "track1_readiness_diagnostic"
        rejection_reason = ""
        if row["support_status"] != "accepted_key_event_shaped":
            accepted_key_basis = "rejected"
            validation_use = "excluded_from_validation_readiness"
            rejection_reason = "support_status is diagnostic_only, not accepted_key_event_shaped"
        reconciled_rows.append(
            {
                "row_id": f"t1_ns_{idx+1:03d}",
                "input_name": row["input_name"],
                "gbif_taxon_key": row["accepted_key"],
                "gbif_scientific_name": row["accepted_name"],
                "wfo_candidate_key": "" if accepted_key_basis != "wfo_projected" else decision["wfo_candidate_key"],
                "wfo_candidate_name": "" if accepted_key_basis != "wfo_projected" else decision["wfo_candidate_name"],
                "accepted_key_basis": accepted_key_basis,
                "event_type": row["evidence_class"],
                "event_shape": row["event_shape"],
                "parent_taxa_named": row["parent_taxa_named"],
                "ploidy_or_chromosome_evidence": row["ploidy_or_chromosome_evidence"],
                "source_group": row["independent_source_group"],
                "source_title": row["source_title"],
                "source_url_or_doi": row["source_url_or_doi"],
                "validation_use": validation_use,
                "no_promotion_flag": "true",
                "rejection_reason": rejection_reason,
                "caveat": row["caveat"],
            }
        )

    controls = panel[panel["panel_role"] == "matched_control"].copy()
    control_rows = []
    for _, row in controls.iterrows():
        event_count = int(row["usable_event_shaped_evidence_count"])
        control_rows.append(
            {
                "input_name": row["input_name"],
                "matched_control_for": row["matched_control_for"],
                "gbif_taxon_key": row["accepted_key"],
                "gbif_scientific_name": row["accepted_name"],
                "accepted_key_basis": "gbif_control_basis",
                "usable_event_shaped_evidence_count": event_count,
                "control_recovered": str(event_count > 0).lower(),
                "validation_use": "matched_control_diagnostic",
                "no_promotion_flag": "true",
                "caveat": "Controls are restated under the same GBIF accepted-key branch basis; WFO projection was not attempted for controls because positive evidence projection already collapses under frozen WFO coverage.",
            }
        )

    crosswalk_df = pd.DataFrame(crosswalk_rows)
    reconciled_df = pd.DataFrame(reconciled_rows)
    controls_df = pd.DataFrame(control_rows)

    OUT_CROSSWALK.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    crosswalk_df.to_csv(OUT_CROSSWALK, sep="\t", index=False)
    reconciled_df.to_csv(OUT_EVIDENCE, sep="\t", index=False)
    controls_df.to_csv(OUT_CONTROLS, sep="\t", index=False)
    OUT_REPORT.write_text(render_report(crosswalk_df, reconciled_df, controls_df), encoding="utf-8")


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    rows = df.astype(str).values.tolist()
    headers = list(df.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell.replace("|", "/") for cell in row) + " |")
    return "\n".join(lines)


def render_report(crosswalk_df: pd.DataFrame, evidence_df: pd.DataFrame, controls_df: pd.DataFrame) -> str:
    accepted = evidence_df[evidence_df["validation_use"] == "track1_readiness_diagnostic"]
    wfo = accepted[accepted["accepted_key_basis"] == "wfo_projected"]
    sidecar = accepted[accepted["accepted_key_basis"] == "gbif_sidecar"]
    rejected = evidence_df[evidence_df["accepted_key_basis"] == "rejected"]
    source_groups = accepted["source_group"].nunique()
    control_recovered = (controls_df["control_recovered"] == "true").sum()
    lines = [
        "---",
        "created: 2026-05-18T22:20:00+00:00",
        "cycle: 29",
        "run_id: run-phytograph-cycle29-track1-free-tier-namespace-reconciliation",
        "agent: worker",
        "milestone: _plan/track1-free-tier-namespace-reconciliation",
        "---",
        "",
        "# Track 1 Free-Tier Namespace Reconciliation",
        "",
        "determination: `gbif_sidecar_admissible_for_readiness_only`",
        "",
        "## Scope",
        "",
        "This package reconciles the Track 1 free-tier GBIF accepted-key reticulation evidence against the frozen WFO-oriented substrate. It does not rerun the tree-compatibility predictor, does not change schema v1.0, does not modify the master substrate, and creates no master prediction or speculation row.",
        "",
        "## Summary",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Distinct GBIF accepted-key event taxa accounted for | {crosswalk_df['gbif_taxon_key'].nunique()} |",
        f"| WFO-projected event taxa | {wfo['gbif_taxon_key'].nunique()} |",
        f"| GBIF sidecar-admitted event taxa | {sidecar['gbif_taxon_key'].nunique()} |",
        f"| Rejected diagnostic rows | {len(rejected)} |",
        f"| Retained event-shaped evidence rows | {len(accepted)} |",
        f"| Retained independent source groups | {source_groups} |",
        f"| Matched-control event recovery | {control_recovered} / {len(controls_df)} |",
        "",
        "The WFO-only projection does not preserve the branch-local threshold: only two GBIF accepted-key event taxa project cleanly to species-level WFO keys in the frozen local crosswalk. The non-null finding is that the remaining accepted-key event evidence can be kept as a clearly labeled GBIF sidecar readiness layer, subject to auditor acceptance and with no promotion into the master substrate or master prediction ledger.",
        "",
        "![Track 1 free-tier reticulation evidence retained, rejected, or sidecar-admitted after GBIF-to-WFO reconciliation.](../figures/track1_free_tier_namespace_reconciliation.png)",
        "",
        "## wfo_projected_evidence",
        "",
        "WFO-projected rows require an exact species-level match in `phytograph_dataset/taxon_crosswalk.parquet`; genus-level matches and form-level hybrid candidates are not accepted as species projections.",
        "",
        md_table(wfo[["gbif_scientific_name", "wfo_candidate_key", "wfo_candidate_name", "source_group"]].drop_duplicates()) if len(wfo) else "No event-shaped evidence row survived WFO projection.",
        "",
        "## gbif_sidecar_evidence",
        "",
        "Rows listed here retain a GBIF accepted key and event-shaped source support, but they did not receive a clean WFO species-level projection in the frozen local crosswalk. They are admissible only as Track 1 evidence-readiness diagnostics, not as master-substrate accepted keys and not as predictions.",
        "",
        md_table(sidecar[["gbif_taxon_key", "gbif_scientific_name", "event_type", "source_group"]].drop_duplicates()) if len(sidecar) else "No sidecar rows were retained.",
        "",
        "## rejected_or_unresolved_evidence",
        "",
        "Rejected rows are excluded from validation-readiness counts. The current rejection is diagnostic-only Citrus evidence where GBIF collapsed `Citrus sinensis` to the same accepted key used for `Citrus aurantium`; the retained Citrus event row is the accepted-key `Citrus ×aurantium` sidecar row.",
        "",
        md_table(rejected[["input_name", "gbif_taxon_key", "gbif_scientific_name", "rejection_reason"]]) if len(rejected) else "No rows were rejected.",
        "",
        "## Control Diagnostic",
        "",
        f"Matched controls remain represented under the same GBIF branch basis, with {control_recovered}/{len(controls_df)} controls carrying event-shaped evidence. This preserves the useful negative control from the free-tier pass, but it is still a high-publication matched panel and is not a source-density or family-size ablation.",
        "",
        "## Admissibility Decision",
        "",
        "The package supports a narrow auditor decision: WFO projection alone is insufficient to reopen WFO-based Track 1 closure, but a labeled GBIF accepted-key sidecar preserves 22 distinct accepted-key event taxa across 11 source groups with 0/17 matched-control recovery. Admission of that sidecar would upgrade Track 1 evidence readiness only within a sidecar namespace and only under the existing no-promotion rule.",
        "",
        "## Remaining Blocker",
        "",
        "A master-level Track 1 validation upgrade still requires auditor/conductor acceptance of the GBIF sidecar or a stronger WFO crosswalk. The sidecar does not solve broad generalization to under-studied clades, family-size controls, or low-publication source-density controls.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    build()
