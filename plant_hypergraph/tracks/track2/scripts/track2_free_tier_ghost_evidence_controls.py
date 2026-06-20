#!/usr/bin/env python3
# created: 2026-05-18T23:55:00+00:00
# cycle: 31
# run_id: fork-2f05eabe3800-clone-0-track2-free-tier-ghost-controls
# agent: worker-clone-0
# milestone: M4.V2
"""Build Track 2 free-tier ghost-hyperedge evidence/control sidecar.

This script is local-only: it checks frozen substrate crosswalks for namespace
repair and preserves the existing M3.T2 ranker score/rank without refitting.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
TRACK = ROOT / "tracks" / "track2"
DATA = TRACK / "data"
REPORTS = TRACK / "reports"

CANDIDATES_PATH = DATA / "ghost_partner_candidate_scores.tsv"
HELDOUTS_PATH = DATA / "track2_wave4_validation_outcomes.tsv"
ACCEPTED_KEY_PATH = DATA / "janzen_martin_accepted_key_recovery.tsv"
MODERN_FAILURE_PATH = DATA / "modern_dispersal_failure_evidence_queue.tsv"
ABLATION_PATH = DATA / "ghost_partner_ablation_results.tsv"
CROSSWALK_PATH = ROOT / "phytograph_dataset" / "taxon_crosswalk.parquet"

MATRIX_PATH = DATA / "track2_free_tier_ghost_evidence_controls.tsv"
REPORT_PATH = REPORTS / "track2_free_tier_ghost_evidence_controls.md"

HELDOUT_CANON = [
    "Persea americana",
    "Maclura pomifera",
    "Gleditsia triacanthos",
    "Annona cherimola",
    "Mauritia flexuosa",
    "Spondias mombin",
    "Sideroxylon foetidissimum",
    "Asimina triloba",
]

MATRIX_COLUMNS = [
    "row_scope",
    "heldout_scientific_name",
    "candidate_id",
    "raw_scientific_name",
    "candidate_class",
    "best_rank",
    "accepted_key_before",
    "accepted_key_after_free_tier_recovery",
    "accepted_key_status",
    "modern_failure_seed_status",
    "modern_failure_independent_free_tier_status",
    "source_groups",
    "source_class_count",
    "non_singleton_source_support",
    "living_megafauna_exclusion_status",
    "passes_validation_contract",
    "final_status",
    "rejection_reason",
    "enters_master_prediction_ledger",
    "inferred_anachronism_claim",
]


def read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t").fillna("")


def normalize_name(value: str) -> str:
    return " ".join(str(value).strip().lower().split())


def load_local_key_map() -> dict[str, str]:
    crosswalk = pd.read_parquet(
        CROSSWALK_PATH,
        columns=[
            "accepted_taxon_key",
            "normalized_name_key",
            "wfo_rank",
            "gbif_rank",
            "confidence",
        ],
    ).fillna("")
    species = crosswalk[
        crosswalk["normalized_name_key"].astype(str).ne("")
        & (
            crosswalk["wfo_rank"].astype(str).str.lower().eq("species")
            | crosswalk["gbif_rank"].astype(str).str.lower().eq("species")
        )
    ]
    key_map: dict[str, str] = {}
    for row in species.itertuples(index=False):
        name = normalize_name(row.normalized_name_key)
        if name and name not in key_map:
            key_map[name] = str(row.accepted_taxon_key)
    return key_map


def local_key_for(raw_name: str, before: str, key_map: dict[str, str]) -> str:
    if str(before).strip():
        return str(before).strip()
    return key_map.get(normalize_name(raw_name), "")


def accepted_status(before: str, after: str, prior_status: str = "") -> str:
    if str(before).strip():
        return "accepted_key_present_existing"
    if str(after).strip():
        return "accepted_key_repaired_local_crosswalk"
    if prior_status == "accepted_key_already_present":
        return "accepted_key_present_existing"
    return "accepted_key_absent_after_free_tier_recovery"


def independent_modern_failure_status(seed_status: str) -> str:
    # Existing local artifacts only contain seed-citation or morphology-only
    # flags. They do not add a direct modern-process source beyond the seed.
    if seed_status == "seed_modern_failure_present":
        return "not_found_beyond_seed_citation_local_only"
    return "not_found_modern_failure_absent_local_only"


def source_groups(row: pd.Series) -> str:
    bits = ["paleobotany_sources"]
    citation = str(row.get("primary_citation_short", "")).strip()
    if citation:
        bits.append(citation)
    return ";".join(bits)


def living_status(row: pd.Series, override: str = "") -> str:
    if str(override).lower() == "true":
        return "blocked_living_megafauna_ambiguity"
    if float(row.get("penalty_living_megafauna_ambiguous", 0) or 0) > 0:
        return "blocked_living_megafauna_ambiguity"
    return "passes_living_megafauna_exclusion"


def build_rejection_reason(row: dict[str, object]) -> str:
    reasons: list[str] = []
    if str(row["accepted_key_status"]).startswith("accepted_key_absent"):
        reasons.append("accepted_key_absent")
    if row["modern_failure_independent_free_tier_status"] != "independent_modern_failure_present":
        reasons.append("modern_failure_independent_evidence_absent")
    if not bool(row["non_singleton_source_support"]):
        reasons.append("singleton_or_source_class_fragile")
    if row["living_megafauna_exclusion_status"] != "passes_living_megafauna_exclusion":
        reasons.append("living_megafauna_ambiguity")
    return "|".join(reasons) if reasons else "passes_all_controls"


def final_status(rejection_reason: str, row_scope: str) -> str:
    if rejection_reason == "passes_all_controls":
        return "validation_contract_supported"
    if "accepted_key_absent" in rejection_reason:
        return "data_limited"
    if "modern_failure_independent_evidence_absent" in rejection_reason:
        return "insufficient_support"
    if "singleton_or_source_class_fragile" in rejection_reason:
        return "source_control_failed"
    return "control_failed"


def candidate_row(candidate: pd.Series, key_map: dict[str, str], heldout_name: str = "") -> dict[str, object]:
    before = str(candidate.get("accepted_taxon_key", "")).strip()
    after = local_key_for(str(candidate["raw_scientific_name"]), before, key_map)
    seed_status = str(candidate.get("modern_failure_evidence_status", "")).strip()
    if not seed_status:
        seed_status = (
            "seed_modern_failure_present"
            if float(candidate.get("modern_failure_support", 0) or 0) > 0
            else "needs_independent_modern_failure_check"
        )
    row = {
        "row_scope": "canonical_heldout" if heldout_name else "local_candidate",
        "heldout_scientific_name": heldout_name,
        "candidate_id": candidate["candidate_id"],
        "raw_scientific_name": candidate["raw_scientific_name"],
        "candidate_class": candidate["candidate_class"],
        "best_rank": int(candidate["rank"]),
        "accepted_key_before": before,
        "accepted_key_after_free_tier_recovery": after,
        "accepted_key_status": accepted_status(before, after),
        "modern_failure_seed_status": seed_status,
        "modern_failure_independent_free_tier_status": independent_modern_failure_status(seed_status),
        "source_groups": source_groups(candidate),
        "source_class_count": 1,
        "non_singleton_source_support": False,
        "living_megafauna_exclusion_status": living_status(candidate),
        "passes_validation_contract": False,
        "final_status": "",
        "rejection_reason": "",
        "enters_master_prediction_ledger": False,
        "inferred_anachronism_claim": False,
    }
    row["rejection_reason"] = build_rejection_reason(row)
    row["passes_validation_contract"] = row["rejection_reason"] == "passes_all_controls"
    row["final_status"] = final_status(str(row["rejection_reason"]), str(row["row_scope"]))
    return row


def heldout_rows(
    candidates: pd.DataFrame,
    heldouts: pd.DataFrame,
    accepted: pd.DataFrame,
    key_map: dict[str, str],
) -> list[dict[str, object]]:
    by_id = candidates.set_index("candidate_id", drop=False)
    accepted_by_name = accepted.set_index("heldout_scientific_name", drop=False)
    rows: list[dict[str, object]] = []
    for name in HELDOUT_CANON:
        prior = heldouts[heldouts["heldout_scientific_name"].eq(name)].iloc[0]
        acc = accepted_by_name.loc[name]
        cid = str(prior["candidate_id"])
        candidate = by_id.loc[cid]
        row = candidate_row(candidate, key_map, heldout_name=name)
        before = str(acc.get("original_accepted_taxon_key", "")).strip()
        recovered = str(acc.get("recovered_accepted_taxon_key", "")).strip()
        after = local_key_for(name, recovered or before, key_map)
        row["accepted_key_before"] = before
        row["accepted_key_after_free_tier_recovery"] = after
        row["accepted_key_status"] = accepted_status(before, after, str(acc["accepted_key_status"]))
        row["modern_failure_seed_status"] = str(prior["modern_failure_evidence_status"])
        row["modern_failure_independent_free_tier_status"] = independent_modern_failure_status(
            str(prior["modern_failure_evidence_status"])
        )
        row["living_megafauna_exclusion_status"] = living_status(
            candidate, str(prior["living_megafauna_ambiguity"])
        )
        row["rejection_reason"] = build_rejection_reason(row)
        row["passes_validation_contract"] = row["rejection_reason"] == "passes_all_controls"
        row["final_status"] = final_status(str(row["rejection_reason"]), "canonical_heldout")
        if str(prior["ablation_outcome"]) == "falsified_by_ablation":
            row["final_status"] = "source_control_failed"
            if "ablation_fragile" not in str(row["rejection_reason"]):
                row["rejection_reason"] = str(row["rejection_reason"]) + "|ablation_fragile"
        rows.append(row)
    return rows


def local_candidate_rows(candidates: pd.DataFrame, key_map: dict[str, str]) -> list[dict[str, object]]:
    return [candidate_row(row, key_map) for _, row in candidates.sort_values("rank").iterrows()]


def count_gate(df: pd.DataFrame, scope: str, column: str, value: object | None = None) -> int:
    sub = df[df["row_scope"].eq(scope)]
    if value is None:
        return int(sub[column].astype(bool).sum())
    return int(sub[column].eq(value).sum())


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in df[columns].itertuples(index=False):
        cells = [str(value).replace("|", "<br>") for value in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_report(matrix: pd.DataFrame, ablations: pd.DataFrame) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    canonical = matrix[matrix["row_scope"].eq("canonical_heldout")]
    local = matrix[matrix["row_scope"].eq("local_candidate")]
    decision = (
        "H2_free_tier_supported_for_n_heldouts"
        if canonical["passes_validation_contract"].any()
        else "H2_remains_not_supported_or_data_limited"
    )
    accepted_c = canonical["accepted_key_after_free_tier_recovery"].astype(str).ne("").sum()
    modern_c = canonical["modern_failure_independent_free_tier_status"].eq(
        "independent_modern_failure_present"
    ).sum()
    nonsingle_c = canonical["non_singleton_source_support"].astype(bool).sum()
    living_c = canonical["living_megafauna_exclusion_status"].eq(
        "passes_living_megafauna_exclusion"
    ).sum()
    accepted_l = local["accepted_key_after_free_tier_recovery"].astype(str).ne("").sum()
    modern_l = local["modern_failure_independent_free_tier_status"].eq(
        "independent_modern_failure_present"
    ).sum()
    nonsingle_l = local["non_singleton_source_support"].astype(bool).sum()
    living_l = local["living_megafauna_exclusion_status"].eq(
        "passes_living_megafauna_exclusion"
    ).sum()

    reason_counts = (
        matrix.assign(reason=matrix["rejection_reason"].str.split("|"))
        .explode("reason")
        .groupby(["row_scope", "reason"])
        .size()
        .reset_index(name="rows")
    )
    status_counts = matrix.groupby(["row_scope", "final_status"]).size().reset_index(name="rows")
    singleton = ablations[ablations["ablation"].eq("remove_singleton_source_rows")].iloc[0]
    normalized = ablations[ablations["ablation"].eq("source_count_candidate_class_normalized")].iloc[0]

    text = f"""---
created: 2026-05-18T23:55:00+00:00
cycle: 31
run_id: fork-2f05eabe3800-clone-0-track2-free-tier-ghost-controls
agent: worker-clone-0
milestone: M4.V2
---

# Track 2 Free-Tier Ghost Evidence Controls

## Scope

This sidecar tests whether the frozen M3.T2 Ghost-Partner Candidate Ranker gains
validation support under free-tier/local evidence repair. It preserves existing
candidate ranks and scores, does not refit the ranker, performs only local
accepted-key namespace repair against `phytograph_dataset/taxon_crosswalk.parquet`,
and does not write `prediction_ledger.tsv` or `speculation_ledger.tsv`.

## Decision

Decision: `{decision}`.

No canonical held-out passes the full validation conjunction
`accepted_key ∧ independent_modern_failure_evidence ∧ non_singleton_or_multi_source_class_support ∧ living_megafauna_excluded`.
Accepted-key recovery did not improve for absent held-outs from the local frozen
crosswalk. No row gains independent modern dispersal-failure evidence beyond the
existing seed citation, and the source-class/singleton ablations remain binding
controls.

## Gate Counts

| scope | rows | accepted_key_present_or_repaired | independent_modern_failure | non_singleton_source_support | living_megafauna_excluded | passes_validation_contract |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| canonical_heldout | {len(canonical)} | {accepted_c} | {modern_c} | {nonsingle_c} | {living_c} | {int(canonical['passes_validation_contract'].sum())} |
| local_candidate | {len(local)} | {accepted_l} | {modern_l} | {nonsingle_l} | {living_l} | {int(local['passes_validation_contract'].sum())} |

## Final Status Counts

{markdown_table(status_counts, ["row_scope", "final_status", "rows"])}

## Rejection Reasons

{markdown_table(reason_counts, ["row_scope", "reason", "rows"])}

## Canonical Held-Out Matrix

{markdown_table(canonical, [
    "heldout_scientific_name",
    "candidate_id",
    "best_rank",
    "accepted_key_status",
    "modern_failure_independent_free_tier_status",
    "non_singleton_source_support",
    "living_megafauna_exclusion_status",
    "passes_validation_contract",
    "final_status",
    "rejection_reason",
])}

## Controls

The singleton-source ablation still leaves `{int(singleton.candidate_rows)}` candidate
rows and `{int(singleton.heldout_validation_ready)}` validation-ready held-outs.
The source-count/candidate-class normalized sensitivity leaves
`{int(normalized.heldout_validation_ready)}` validation-ready held-outs. These
controls block promotion even where morphology and extinct-fauna citation support
are present.

![Canonical held-outs and local candidates by accepted-key recovery, modern-failure evidence, source-class support, living-megafauna exclusion, and final validation-contract status.](../figures/track2_free_tier_ghost_control_matrix.png)

## Barrier 4 Interpretation

H2 remains not supported under the existing validation contract. Missing accepted
keys are namespace/data limitations, not biological falsifications; missing
independent modern-failure evidence is insufficient support; singleton/source-class
fragility is a control failure; living-megafauna ambiguity blocks ghost-megafauna
interpretation unless an explicit extant-versus-extinct dispersal contrast is
added in future evidence.

## Future Data Required

Reopen only with direct, provenance-preserved evidence that supplies all gates at
once: accepted focal taxon keys for the canonical held-outs, modern-process
evidence for dispersal or recruitment failure beyond the seed citation,
non-singleton or multi-source-class support for the same plant-extinct-fauna
pair, and an explicit exclusion or separation of living-megafauna dispersal.
"""
    REPORT_PATH.write_text(text)


def assert_master_ledgers_header_only() -> None:
    for name in ["prediction_ledger.tsv", "speculation_ledger.tsv"]:
        lines = [line for line in (ROOT / name).read_text().splitlines() if line.strip()]
        if len(lines) != 1:
            raise AssertionError(f"{name} must remain header-only, found {len(lines)} lines")


def build() -> dict[str, int]:
    candidates = read_tsv(CANDIDATES_PATH)
    heldouts = read_tsv(HELDOUTS_PATH)
    accepted = read_tsv(ACCEPTED_KEY_PATH)
    modern = read_tsv(MODERN_FAILURE_PATH)
    ablations = read_tsv(ABLATION_PATH)
    key_map = load_local_key_map()

    candidates = candidates.merge(
        modern[["candidate_id", "modern_failure_evidence_status"]],
        on="candidate_id",
        how="left",
    )
    candidates["modern_failure_evidence_status"] = candidates[
        "modern_failure_evidence_status"
    ].fillna("")

    rows = heldout_rows(candidates, heldouts, accepted, key_map) + local_candidate_rows(
        candidates, key_map
    )
    matrix = pd.DataFrame(rows, columns=MATRIX_COLUMNS)
    if len(matrix[matrix["row_scope"].eq("canonical_heldout")]) != 8:
        raise AssertionError("expected all 8 canonical held-outs")
    if len(matrix[matrix["row_scope"].eq("local_candidate")]) != 31:
        raise AssertionError("expected all 31 local candidate rows")
    if matrix["rejection_reason"].astype(str).eq("").any():
        raise AssertionError("failed rows must have machine-readable rejection reasons")
    if matrix["inferred_anachronism_claim"].astype(bool).any():
        raise AssertionError("sidecar must not infer established anachronism claims")
    if matrix["enters_master_prediction_ledger"].astype(bool).any():
        raise AssertionError("sidecar must not promote rows to master prediction ledger")

    MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(MATRIX_PATH, sep="\t", index=False)
    write_report(matrix, ablations)
    assert_master_ledgers_header_only()
    return {
        "rows": int(len(matrix)),
        "canonical": int(matrix["row_scope"].eq("canonical_heldout").sum()),
        "local": int(matrix["row_scope"].eq("local_candidate").sum()),
        "passes": int(matrix["passes_validation_contract"].sum()),
    }


if __name__ == "__main__":
    result = build()
    print(
        "PASS: Track 2 free-tier ghost controls "
        f"({result['canonical']} canonical, {result['local']} local, "
        f"{result['passes']} validation-contract pass)"
    )
    print(f"WROTE: {MATRIX_PATH}")
    print(f"WROTE: {REPORT_PATH}")
