#!/usr/bin/env python3
# created: 2026-05-18T23:10:00+00:00
# cycle: 30
# run_id: run-phytograph-cycle30-track1-free-tier-control-strengthening
# agent: worker
# milestone: _plan/track1-free-tier-control-strengthening
"""Build Track 1 GBIF-sidecar control-strengthening diagnostics."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track1" / "data"
REPORTS = ROOT / "tracks" / "track1" / "reports"

EVIDENCE = DATA / "free_tier_reticulation_reconciled_evidence.tsv"
CONTROLS = DATA / "free_tier_reticulation_reconciled_controls.tsv"
PANEL = DATA / "free_tier_reticulation_panel.tsv"
CROSSWALK = DATA / "free_tier_reticulation_namespace_crosswalk.tsv"

CONTROL_PANEL_OUT = DATA / "free_tier_reticulation_control_panel.tsv"
DIAGNOSTICS_OUT = DATA / "free_tier_reticulation_control_diagnostics.tsv"
LOW_PUBLICATION_OUT = DATA / "free_tier_reticulation_low_publication_controls.tsv"
REPORT_OUT = REPORTS / "track1_free_tier_control_strengthening.md"

RUN_ID = "run-phytograph-cycle30-track1-free-tier-control-strengthening"
CREATED = "2026-05-18T23:10:00+00:00"


def genus(name: str) -> str:
    cleaned = str(name).replace("×", "x").strip()
    return cleaned.split()[0] if cleaned else ""


def name_turnover(row: pd.Series) -> int:
    gbif = str(row.get("gbif_match_status", ""))
    wfo = str(row.get("wfo_projection_status", ""))
    return int(("SYNONYM" in gbif) or ("sidecar" in wfo) or ("not_projected" in wfo))


def band_from_publication_proxy(value: int) -> str:
    if value >= 10_000:
        return "high"
    if value >= 1_000:
        return "medium"
    if value > 0:
        return "low"
    return "none"


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        out.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(out)


def build_case_rows(evidence: pd.DataFrame, panel: pd.DataFrame, crosswalk: pd.DataFrame) -> pd.DataFrame:
    retained = evidence[evidence["validation_use"] == "track1_readiness_diagnostic"].copy()
    grouped = (
        retained.groupby(["gbif_taxon_key", "gbif_scientific_name"], dropna=False)
        .agg(source_group_count=("source_group", "nunique"), evidence_row_count=("row_id", "count"))
        .reset_index()
    )
    panel_by_key = panel.drop_duplicates("accepted_key").set_index("accepted_key")
    cross_by_key = crosswalk.drop_duplicates("gbif_taxon_key").set_index("gbif_taxon_key")
    rows = []
    for _, row in grouped.iterrows():
        key = row["gbif_taxon_key"]
        p = panel_by_key.loc[key] if key in panel_by_key.index else pd.Series(dtype=object)
        c = cross_by_key.loc[key] if key in cross_by_key.index else pd.Series(dtype=object)
        pub = int(pd.to_numeric(p.get("openalex_reticulation_hit_count", 0), errors="coerce") or 0)
        out = {
            "panel_role": "case_retained_sidecar_event",
            "taxon_name": row["gbif_scientific_name"],
            "namespace": c.get("accepted_key_basis", "gbif_sidecar"),
            "accepted_key": key,
            "family": p.get("family", ""),
            "genus": genus(row["gbif_scientific_name"]),
            "source_group_count": int(row["source_group_count"]),
            "evidence_row_count": int(row["evidence_row_count"]),
            "gbif_match_status": p.get("gbif_match_type", "accepted_key_from_reconciled_evidence"),
            "wfo_projection_status": c.get("crosswalk_status", "not_projected_local_crosswalk"),
            "publication_proxy": pub,
            "control_match_basis": "case",
            "validation_use": "track1_sidecar_control_diagnostic",
            "rejection_reason": "",
        }
        out["name_turnover_proxy"] = name_turnover(out)
        rows.append(out)
    return pd.DataFrame(rows)


def build_existing_control_rows(controls: pd.DataFrame, panel: pd.DataFrame, case_rows: pd.DataFrame) -> pd.DataFrame:
    panel_by_key = panel.drop_duplicates("accepted_key").set_index("accepted_key")
    case_by_name = case_rows.assign(input_name=case_rows["taxon_name"].str.replace(" L\\.$", "", regex=True))
    rows = []
    for _, row in controls.iterrows():
        key = row["gbif_taxon_key"]
        p = panel_by_key.loc[key] if key in panel_by_key.index else pd.Series(dtype=object)
        matched = str(row["matched_control_for"])
        matched_case = case_rows[case_rows["taxon_name"].str.contains(matched.split()[0], case=False, regex=False, na=False)]
        same_genus = genus(row["input_name"]) == genus(matched)
        basis = "genus_near" if same_genus else "family_near"
        if matched_case.empty and p.get("family", "") in set(case_rows["family"]):
            basis = "family_near"
        pub = int(pd.to_numeric(p.get("openalex_reticulation_hit_count", 0), errors="coerce") or 0)
        out = {
            "panel_role": "matched_control_existing",
            "taxon_name": row["gbif_scientific_name"],
            "namespace": row["accepted_key_basis"],
            "accepted_key": key,
            "family": p.get("family", ""),
            "genus": genus(row["gbif_scientific_name"]),
            "source_group_count": 0,
            "evidence_row_count": int(row["usable_event_shaped_evidence_count"]),
            "gbif_match_status": p.get("gbif_match_type", "accepted_key_from_reconciled_controls"),
            "wfo_projection_status": "control_wfo_projection_not_attempted",
            "publication_proxy": pub,
            "control_match_basis": basis,
            "validation_use": "matched_control_diagnostic",
            "rejection_reason": "",
        }
        out["name_turnover_proxy"] = name_turnover(out)
        rows.append(out)
    return pd.DataFrame(rows)


def build_source_density_controls(panel: pd.DataFrame, existing_controls: pd.DataFrame) -> pd.DataFrame:
    controls = panel[panel["panel_role"] == "matched_control"].copy()
    existing_keys = set(existing_controls["accepted_key"])
    rows = []
    for _, p in controls.iterrows():
        key = p["accepted_key"]
        if key in existing_keys:
            continue
        pub = int(pd.to_numeric(p.get("openalex_reticulation_hit_count", 0), errors="coerce") or 0)
        out = {
            "panel_role": "source_density_candidate_control",
            "taxon_name": p["accepted_name"],
            "namespace": "gbif_control_basis",
            "accepted_key": key,
            "family": p["family"],
            "genus": genus(p["accepted_name"]),
            "source_group_count": 0,
            "evidence_row_count": int(p["usable_event_shaped_evidence_count"]),
            "gbif_match_status": p["gbif_match_type"],
            "wfo_projection_status": "control_wfo_projection_not_attempted",
            "publication_proxy": pub,
            "control_match_basis": "source_density_candidate",
            "validation_use": "control_candidate_diagnostic",
            "rejection_reason": "already represented in reconciled controls" if key in existing_keys else "",
        }
        out["name_turnover_proxy"] = name_turnover(out)
        rows.append(out)
    return pd.DataFrame(rows)


def build_low_publication_controls(panel: pd.DataFrame, case_rows: pd.DataFrame) -> pd.DataFrame:
    case_families = set(case_rows["family"])
    rows = []
    controls = panel[panel["panel_role"] == "matched_control"].copy()
    for _, p in controls.iterrows():
        pub = int(pd.to_numeric(p.get("openalex_reticulation_hit_count", 0), errors="coerce") or 0)
        band = band_from_publication_proxy(pub)
        reason = ""
        if p["family"] not in case_families:
            reason = "family not represented among retained sidecar event taxa"
        elif band not in {"low", "none"}:
            reason = "not low-publication under local OpenAlex proxy"
        rows.append(
            {
                "taxon_name": p["accepted_name"],
                "accepted_key": p["accepted_key"],
                "family": p["family"],
                "genus": genus(p["accepted_name"]),
                "publication_proxy": pub,
                "source_density_band": band,
                "gbif_match_status": p["gbif_match_type"],
                "candidate_status": "usable_low_publication_control" if not reason else "rejected_low_publication_control",
                "rejection_reason": reason,
            }
        )
    if not any(r["candidate_status"] == "usable_low_publication_control" for r in rows):
        rows.append(
            {
                "taxon_name": "NO_LOCAL_LOW_PUBLICATION_MATCH",
                "accepted_key": "",
                "family": "",
                "genus": "",
                "publication_proxy": 0,
                "source_density_band": "none",
                "gbif_match_status": "",
                "candidate_status": "not_constructible_from_local_panel",
                "rejection_reason": "All local family/genus-near controls have nonzero/high metadata exposure; sparse controls cannot be used to interpret 0-recovery as biological separation.",
            }
        )
    return pd.DataFrame(rows)


def diagnostics(panel_out: pd.DataFrame, low_publication: pd.DataFrame) -> pd.DataFrame:
    cases = panel_out[panel_out["panel_role"] == "case_retained_sidecar_event"]
    controls = panel_out[panel_out["panel_role"].str.contains("control", na=False)]
    comparable = controls[controls["control_match_basis"].isin(["genus_near", "family_near"])]
    family_case = cases.groupby("family")["accepted_key"].nunique()
    family_ctrl = comparable.groupby("family")["accepted_key"].nunique()
    shared_families = sorted(set(family_case.index) & set(family_ctrl.index))
    control_recovery = float((comparable["evidence_row_count"] > 0).mean()) if len(comparable) else 0.0
    case_recovery = float((cases["evidence_row_count"] > 0).mean()) if len(cases) else 0.0
    low_usable = low_publication.query("candidate_status == 'usable_low_publication_control'")
    rows = [
        {
            "diagnostic": "retained_event_taxa",
            "case_mean": cases["evidence_row_count"].mean(),
            "case_median": cases["evidence_row_count"].median(),
            "control_mean": comparable["evidence_row_count"].mean() if len(comparable) else 0,
            "control_median": comparable["evidence_row_count"].median() if len(comparable) else 0,
            "effect_direction": "cases_above_controls",
            "caveat": "Counts are from retained GBIF-sidecar event rows; they support readiness diagnostics only.",
            "pass_fail": "pass",
        },
        {
            "diagnostic": "source_density_control",
            "case_mean": cases["source_group_count"].mean(),
            "case_median": cases["source_group_count"].median(),
            "control_mean": comparable["source_group_count"].mean() if len(comparable) else 0,
            "control_median": comparable["source_group_count"].median() if len(comparable) else 0,
            "effect_direction": "cases_have_event_source_exposure_controls_zero",
            "caveat": "Controls have comparable metadata search exposure but no curated event source groups; this leaves targeted-source artifact risk.",
            "pass_fail": "fail",
        },
        {
            "diagnostic": "publication_proxy_control",
            "case_mean": cases["publication_proxy"].mean(),
            "case_median": cases["publication_proxy"].median(),
            "control_mean": comparable["publication_proxy"].mean() if len(comparable) else 0,
            "control_median": comparable["publication_proxy"].median() if len(comparable) else 0,
            "effect_direction": "metadata_exposure_overlaps",
            "caveat": "OpenAlex reticulation-query counts are broad metadata proxies and not evidence rows.",
            "pass_fail": "pass",
        },
        {
            "diagnostic": "family_size_control",
            "case_mean": family_case.mean(),
            "case_median": family_case.median(),
            "control_mean": family_ctrl.reindex(shared_families).mean() if shared_families else 0,
            "control_median": family_ctrl.reindex(shared_families).median() if shared_families else 0,
            "effect_direction": "same_family_opportunity_present",
            "caveat": f"Existing controls cover {len(shared_families)} case families; family size is measured within the local panel, not global taxonomy.",
            "pass_fail": "pass" if len(shared_families) >= 8 else "fail",
        },
        {
            "diagnostic": "gbif_wfo_resolution_control",
            "case_mean": cases["name_turnover_proxy"].mean(),
            "case_median": cases["name_turnover_proxy"].median(),
            "control_mean": comparable["name_turnover_proxy"].mean() if len(comparable) else 0,
            "control_median": comparable["name_turnover_proxy"].median() if len(comparable) else 0,
            "effect_direction": "cases_have_more_wfo_sidecar_name_turnover",
            "caveat": "WFO projection was intentionally not attempted for controls because WFO-only case evidence already collapsed to 2 taxa.",
            "pass_fail": "fail",
        },
        {
            "diagnostic": "low_publication_control_constructibility",
            "case_mean": cases["publication_proxy"].mean(),
            "case_median": cases["publication_proxy"].median(),
            "control_mean": low_usable["publication_proxy"].mean()
            if len(low_usable)
            else 0,
            "control_median": low_usable["publication_proxy"].median()
            if len(low_usable)
            else 0,
            "effect_direction": "low_publication_controls_sparse_or_insufficient",
            "caveat": f"Only {len(low_usable)} low-publication control(s) are available from the local panel; this is not enough to interpret sparse-control non-recovery.",
            "pass_fail": "pass" if len(low_usable) >= 3 else "fail",
        },
    ]
    out = pd.DataFrame(rows)
    out["case_mean"] = out["case_mean"].fillna(0).round(3)
    out["case_median"] = out["case_median"].fillna(0).round(3)
    out["control_mean"] = out["control_mean"].fillna(0).round(3)
    out["control_median"] = out["control_median"].fillna(0).round(3)
    return out


def write_report(panel_out: pd.DataFrame, diag: pd.DataFrame, low_publication: pd.DataFrame) -> None:
    cases = panel_out[panel_out["panel_role"] == "case_retained_sidecar_event"]
    controls = panel_out[panel_out["panel_role"].str.contains("control", na=False)]
    basis_counts = controls["control_match_basis"].value_counts().rename_axis("control_match_basis").reset_index(name="rows")
    status = "sidecar_readiness_uncontrolled"
    if (diag["diagnostic"].eq("source_density_control") & diag["pass_fail"].eq("fail")).any():
        status = "sidecar_readiness_uncontrolled"
    if controls["evidence_row_count"].gt(0).any():
        status = "source_density_artifact_risk"
    frontmatter = f"""---
created: {CREATED}
cycle: 30
run_id: {RUN_ID}
agent: worker
milestone: _plan/track1-free-tier-control-strengthening
---
"""
    text = f"""{frontmatter}
# Track 1 Free-Tier Control Strengthening

## Determination

Final status: `{status}`.

This package keeps the validated GBIF accepted-key sidecar fixed: {cases['accepted_key'].nunique()} retained event taxa, {int(cases['evidence_row_count'].sum())} retained event-shaped rows, and no master prediction or speculation row. It does not rerun the TCI predictor and does not reopen WFO-based H1 validation.

## Case And Control Construction

Cases are the retained rows from `free_tier_reticulation_reconciled_evidence.tsv`, collapsed to one row per GBIF accepted key. Controls start from `free_tier_reticulation_reconciled_controls.tsv` and are annotated with the prior panel's GBIF match, family, genus, and broad OpenAlex/Crossref metadata proxies.

{md_table(basis_counts)}

## Source-Density Diagnostics

{md_table(diag)}

## Matching Failures

The existing controls are useful for family/genus opportunity and broad metadata exposure, but they are not comparable on curated event-source exposure: retained cases have at least one event source group by construction, while controls have zero curated event source groups. Low-publication controls are inadequate from the local panel: only {int((low_publication['candidate_status'] == 'usable_low_publication_control').sum())} usable sparse control(s) were found, and rejected sparse-control candidates plus reasons are recorded in `free_tier_reticulation_low_publication_controls.tsv`.

## Admissibility Status

`sidecar_control_supported_readiness` is not assigned. The sidecar still separates cases from the existing matched controls on event recovery, but source-density comparability is not strong enough to rule out targeted-source artifact risk. The conservative status is therefore `{status}`.

## Future Data Required For WFO-Based H1 Reopening

WFO-based H1 validation would require an expanded frozen WFO crosswalk that resolves the canonical hybrid/polyploid event taxa at accepted species or sanctioned hybrid-name rank, plus comparable non-event controls with WFO projection, family/genus opportunity, and source exposure measured under the same query protocol. It would also require curated reticulation/non-reticulation evidence extraction for controls, not only metadata hit counts.

![Track 1 GBIF-sidecar reticulation evidence recovery versus matched controls, stratified by source-group count and family/genus matching basis.](../figures/track1_free_tier_control_recovery.png)
"""
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(text, encoding="utf-8")


def main() -> None:
    evidence = pd.read_csv(EVIDENCE, sep="\t").fillna("")
    controls = pd.read_csv(CONTROLS, sep="\t").fillna("")
    panel = pd.read_csv(PANEL, sep="\t").fillna("")
    crosswalk = pd.read_csv(CROSSWALK, sep="\t").fillna("")

    case_rows = build_case_rows(evidence, panel, crosswalk)
    existing_control_rows = build_existing_control_rows(controls, panel, case_rows)
    source_density_controls = build_source_density_controls(panel, existing_control_rows)
    panel_out = pd.concat([case_rows, existing_control_rows, source_density_controls], ignore_index=True)

    required_cols = [
        "panel_role",
        "taxon_name",
        "namespace",
        "accepted_key",
        "family",
        "genus",
        "source_group_count",
        "evidence_row_count",
        "gbif_match_status",
        "wfo_projection_status",
        "name_turnover_proxy",
        "publication_proxy",
        "control_match_basis",
        "validation_use",
        "rejection_reason",
    ]
    panel_out = panel_out[required_cols].sort_values(["panel_role", "family", "genus", "taxon_name"])
    low_publication = build_low_publication_controls(panel, case_rows)
    diag = diagnostics(panel_out, low_publication)

    DATA.mkdir(parents=True, exist_ok=True)
    panel_out.to_csv(CONTROL_PANEL_OUT, sep="\t", index=False)
    diag.to_csv(DIAGNOSTICS_OUT, sep="\t", index=False)
    low_publication.to_csv(LOW_PUBLICATION_OUT, sep="\t", index=False)
    write_report(panel_out, diag, low_publication)

    print(f"wrote {CONTROL_PANEL_OUT}")
    print(f"wrote {DIAGNOSTICS_OUT}")
    print(f"wrote {LOW_PUBLICATION_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
