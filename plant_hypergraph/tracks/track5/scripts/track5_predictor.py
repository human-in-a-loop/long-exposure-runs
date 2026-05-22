"""
track5_predictor.py — PhytoGraph Track 5 chemodiversity neighborhood-completion predictor.

created: 2026-05-18T03:00:00+00:00
cycle: 9
run_id: run-phytograph-cycle9-track5-instrument
agent: worker
milestone: M3.T5

Algorithm (per brief):
  score(t, k | f) = S_f[k] * w_specificity(k) * w_screening(t)
    S_f[k]              = (# taxa in f with >=1 retained compound in class k) / (# screened taxa in f)
    w_specificity(k)    = -log p(k | global), where p is the within-Track-5 compound_class prevalence
    w_screening(t)      = 1 / (1 + n_compounds_detected_in_t)   [unscreened: w=1]

Firewall (mandatory):
  Bioactivity predictions are derived ONLY by the literal chain
      (taxon -> compound) o (compound -> bioactivity_class).
  No direct (taxon, bioactivity_class) join may appear in the output.

Reads (read-only):
  tracks/track5/data/track5_enrichment_edges.parquet
  tracks/track5/data/track5_compound_class_membership.parquet
  tracks/track5/data/track5_bioactivity_assertions.parquet
  tracks/track5/data/track5_taxon_to_family.parquet
  tracks/track5/data/per_taxon_screening_intensity.tsv

Writes:
  tracks/track5/data/phytochemistry_predictions.tsv
  tracks/track5/data/phytochemistry_speculation.tsv
  tracks/track5/data/chemodiversity_signatures.parquet
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

# ---- Firewall scope strings (canonical, used by validator Test B) ---------------
SCOPE_DETECTION  = "predicted phytochemical screening candidate: does not support observed detection, typical concentration, bioactivity, clinical efficacy, or safety"
SCOPE_ETHNO      = "ethnobotanical use: human-cultural record; does not imply bioactivity, clinical efficacy, or safety"
SCOPE_BIOACT     = "predicted neighborhood-completion bioactivity-class via compound indirection; does not support detection, clinical efficacy, or ethnobotanical safety"
SCOPE_CLINICAL   = "clinical efficacy: requires regulatory-grade trial evidence; NOT inferable from any Track 5 layer"

DUKE_SOURCE_ID   = "Dr. Duke Phytochemical and Ethnobotanical Databases"


# ---- Loader ---------------------------------------------------------------------

def load_phytochem(enrichment_path: Path,
                   loso_drop_source_class: str | None = None,
                   exclude_assertions_for_taxa: set[str] | None = None) -> pd.DataFrame:
    """Load retained phytochemical_assertion rows; optionally apply LOSO and held-out masks.

    Family is restored by combining the enrichment edge's `family` column with a
    fallback lookup from `track5_taxon_to_family.parquet` (substrate gap recovery).
    """
    e = pd.read_parquet(enrichment_path)
    phyto = e[(e["edge_type"] == "phytochemical_assertion") & (e["retained"])].copy()
    if loso_drop_source_class:
        phyto = phyto[phyto["source_class"] != loso_drop_source_class]
    if exclude_assertions_for_taxa:
        phyto = phyto[~phyto["accepted_taxon_key"].isin(exclude_assertions_for_taxa)]

    tf = pd.read_parquet(enrichment_path.parent / "track5_taxon_to_family.parquet")
    tf_map = (
        tf.dropna(subset=["family"])
        .drop_duplicates(subset=["accepted_taxon_key"])
        .set_index("accepted_taxon_key")["family"]
        .to_dict()
    )
    fam_from_tf = phyto["accepted_taxon_key"].map(tf_map)
    phyto["family_final"] = phyto["family"].fillna(fam_from_tf)
    return phyto


def family_signature(phyto: pd.DataFrame, min_taxa: int = 3, min_cc: int = 2):
    """Compute S_f[k] = n_taxa_with_compound_in_class_k / n_screened_taxa_in_family.

    Returns (signature_df, qualifying_families, n_screened_per_family,
             family_status_df), where family_status_df labels every family as
     'qualified' | 'data-limited:few_taxa' | 'data-limited:few_classes' | 'data-limited:zero_assertions'.
    """
    fam = phyto.dropna(subset=["family_final"])
    empty_status_cols = ["family", "n_screened_taxa", "n_compound_classes", "family_status"]
    if fam.empty:
        return (
            pd.DataFrame(columns=["family", "compound_class", "n_in_class", "n_screened", "signature"]),
            set(),
            pd.Series(dtype="int64"),
            pd.DataFrame(columns=empty_status_cols),
        )
    valid = fam.dropna(subset=["compound_class"])
    n_screened = fam.groupby("family_final")["accepted_taxon_key"].nunique()
    fc = (
        valid.groupby(["family_final", "compound_class"])["accepted_taxon_key"]
        .nunique()
        .reset_index(name="n_in_class")
    )
    fc["n_screened"] = fc["family_final"].map(n_screened)
    fc["signature"] = fc["n_in_class"] / fc["n_screened"]
    n_cc = valid.groupby("family_final")["compound_class"].nunique()

    qualifying = set(n_screened[n_screened >= min_taxa].index) & set(n_cc[n_cc >= min_cc].index)

    status_rows = []
    for f in sorted(set(n_screened.index)):
        s = "qualified" if f in qualifying else (
            "data-limited:few_taxa" if n_screened.get(f, 0) < min_taxa else "data-limited:few_classes"
        )
        status_rows.append({
            "family": f, "n_screened_taxa": int(n_screened.get(f, 0)),
            "n_compound_classes": int(n_cc.get(f, 0)), "family_status": s,
        })
    fam_status = pd.DataFrame(status_rows, columns=empty_status_cols).sort_values("family")
    return fc.rename(columns={"family_final": "family"}), qualifying, n_screened, fam_status


def specificity_weights(phyto: pd.DataFrame) -> dict[str, float]:
    """w_specificity(k) = -log p(k | global). Classes never observed get 0."""
    cc = phyto["compound_class"].dropna()
    if len(cc) == 0:
        return {}
    p = cc.value_counts() / len(cc)
    return {k: float(-np.log(v)) for k, v in p.items()}


def compound_to_bioactivity(bioactivity_path: Path) -> dict[str, set[str]]:
    """Build compound_id -> set(bioactivity_class) from the compound-keyed firewall table."""
    ba = pd.read_parquet(bioactivity_path)
    ba = ba[ba["retained"]].dropna(subset=["compound_id", "bioactivity_class"])
    out: dict[str, set[str]] = {}
    for c, b in zip(ba["compound_id"], ba["bioactivity_class"]):
        out.setdefault(c, set()).add(b)
    return out


def class_to_compounds(compound_class_path: Path) -> dict[str, set[str]]:
    """Build compound_class -> set(compound_id) from the Duke CHEMCLASS view."""
    cc = pd.read_parquet(compound_class_path)
    cc = cc.dropna(subset=["compound_class", "compound_id"])
    out: dict[str, set[str]] = {}
    for k, c in zip(cc["compound_class"], cc["compound_id"]):
        out.setdefault(k, set()).add(c)
    return out


def predict_bioactivity_chain(compound_class: str,
                              cls_to_cmpd: dict[str, set[str]],
                              cmpd_to_bio: dict[str, set[str]],
                              max_compounds_per_class: int = 50) -> tuple[list[str], list[str]]:
    """Strict (taxon->compound)o(compound->bioactivity) chain.

    Returns (sorted_unique_bioactivity_classes, sorted_supporting_compound_ids).
    The chain is documented per row so Test C can re-derive it from inputs.
    """
    cmpds = sorted(cls_to_cmpd.get(compound_class, set()))[:max_compounds_per_class]
    bio = set()
    supporting = []
    for c in cmpds:
        if c in cmpd_to_bio:
            bio.update(cmpd_to_bio[c])
            supporting.append(c)
    return sorted(bio), sorted(supporting)


# ---- Main predictor -------------------------------------------------------------

def run_predictor(enrichment_path: Path,
                  screening_path: Path,
                  compound_class_path: Path,
                  bioactivity_path: Path,
                  taxon_family_path: Path,
                  out_predictions: Path,
                  out_signatures: Path,
                  out_speculation: Path,
                  loso_drop_source_class: str | None = None,
                  exclude_assertions_for_taxa: set[str] | None = None,
                  min_taxa: int = 3, min_cc: int = 2,
                  top_n_per_cell: int = 5,
                  rng_seed: int = 20260518) -> dict:
    """Build the predictor end-to-end and write the ledger.

    Returns a small summary dict suitable for logging and the harness.
    """
    np.random.seed(rng_seed)
    phyto = load_phytochem(enrichment_path,
                           loso_drop_source_class=loso_drop_source_class,
                           exclude_assertions_for_taxa=exclude_assertions_for_taxa)
    sig_df, qualifying, n_screened, fam_status = family_signature(
        phyto, min_taxa=min_taxa, min_cc=min_cc
    )
    spec = specificity_weights(phyto)
    cls_to_cmpd = class_to_compounds(compound_class_path)
    cmpd_to_bio = compound_to_bioactivity(bioactivity_path)

    si = pd.read_csv(screening_path, sep="\t")
    nc_map = si.set_index("accepted_taxon_key")["n_compounds"].to_dict()
    ds_map = si.set_index("accepted_taxon_key")["dominant_source"].to_dict()

    tf = pd.read_parquet(taxon_family_path)
    fam_to_all_taxa = (
        tf.dropna(subset=["family"]).groupby("family")["accepted_taxon_key"]
        .apply(lambda s: sorted(set(s))).to_dict()
    )

    # Duke share per family (from non-LOSO baseline phytochem)
    base_phyto = load_phytochem(enrichment_path)
    fam_duke_share = {}
    for f, grp in base_phyto.dropna(subset=["family_final"]).groupby("family_final"):
        n_total = len(grp)
        n_duke = int((grp["source_class"] == "Dr. Duke").sum())
        fam_duke_share[f] = float(n_duke / n_total) if n_total else 0.0

    rows = []
    speculation = []
    for fam in sorted(qualifying):
        sig_for_fam = sig_df[sig_df["family"] == fam].set_index("compound_class")
        n_scr = int(n_screened.get(fam, 0))
        duke_share = fam_duke_share.get(fam, 0.0)
        screened_taxa = set(phyto[phyto["family_final"] == fam]["accepted_taxon_key"].unique())
        all_taxa = set(fam_to_all_taxa.get(fam, []))
        target_taxa = sorted(all_taxa - screened_taxa)
        if not target_taxa:
            # Fall back to lightly-screened taxa in the family (n_compounds <= 3)
            target_taxa = sorted([t for t in screened_taxa if nc_map.get(t, 0) <= 3])
        for k in sorted(sig_for_fam.index):
            S_fk = float(sig_for_fam.at[k, "signature"])
            if S_fk <= 0:
                continue
            n_supp = int(sig_for_fam.at[k, "n_in_class"])
            w_k = spec.get(k, 0.0)
            bio_pred, supporting = predict_bioactivity_chain(k, cls_to_cmpd, cmpd_to_bio)
            for t in target_taxa:
                nc = int(nc_map.get(t, 0))
                w_t = 1.0 / (1.0 + nc)
                score = S_fk * w_k * w_t
                ablation = [DUKE_SOURCE_ID] if duke_share >= 0.50 else []
                exp_val = (
                    "Targeted phytochemical screen of taxon; KNApSAcK/NPASS/ChEBI side-wave ingest "
                    "for cross-source confirmation; ethnobotanical-use cross-check (NAEB expansion)."
                )
                rows.append({
                    "track": "track5",
                    "prediction_statement": (
                        f"Under-screened taxon {t} (family {fam}) is predicted to express compound class "
                        f"'{k}' by within-family neighborhood-completion (S_f={S_fk:.3f}, "
                        f"n_supporting_congeners={n_supp}, screening_weight={w_t:.3f})."
                    ),
                    "taxon_accepted_key": t,
                    "family": fam,
                    "predicted_compound_class": k,
                    "predicted_bioactivity_via_compound_indirection": "|".join(bio_pred),
                    "bioactivity_chain_supporting_compound_ids": "|".join(supporting),
                    "supporting_hyperedges": "phytochemical_assertion+compound_class_membership",
                    "n_supporting_congeners": n_supp,
                    "score": round(score, 6),
                    "S_f_k": round(S_fk, 6),
                    "w_specificity_k": round(w_k, 6),
                    "w_screening_t": round(w_t, 6),
                    "n_compounds_taxon": nc,
                    "family_quantile": None,  # filled by validation phase
                    "evidence_scope": SCOPE_BIOACT if bio_pred else SCOPE_DETECTION,
                    "dominant_source": ds_map.get(t, "Dr. Duke" if duke_share >= 0.5 else "unscreened"),
                    "duke_share_in_family": round(duke_share, 6),
                    "expected_validation_source": exp_val,
                    "status": "pending",
                    "ablation_sensitivity": "|".join(ablation),
                    "date_filed": "2026-05-18",
                })

    pred_columns = [
        "track", "prediction_statement", "taxon_accepted_key", "family",
        "predicted_compound_class", "predicted_bioactivity_via_compound_indirection",
        "bioactivity_chain_supporting_compound_ids", "supporting_hyperedges",
        "n_supporting_congeners", "score", "S_f_k", "w_specificity_k",
        "w_screening_t", "n_compounds_taxon", "family_quantile", "evidence_scope",
        "dominant_source", "duke_share_in_family", "expected_validation_source",
        "status", "ablation_sensitivity", "date_filed",
    ]
    pred_df = pd.DataFrame(rows, columns=pred_columns)
    if not pred_df.empty:
        pred_df = pred_df.sort_values(
            ["family", "predicted_compound_class", "score", "taxon_accepted_key"],
            ascending=[True, True, False, True],
        )
        pred_df = pred_df.groupby(
            ["family", "predicted_compound_class"], group_keys=False
        ).head(top_n_per_cell).reset_index(drop=True)
        pred_df["family_quantile"] = pred_df.groupby("family")["score"].rank(
            method="average", ascending=False, pct=True
        ).round(6)

    # Speculation ledger: family-level signature rows with no expected validation source named
    for f in sorted(set(fam_status[fam_status["family_status"].str.startswith("data-limited")]["family"])):
        speculation.append({
            "track": "track5",
            "speculation_statement": f"Family {f} signature is data-limited (status={fam_status[fam_status['family']==f]['family_status'].iloc[0]}); no predictor output emitted.",
            "family": f,
            "expected_validation_source": None,
            "status": "data-limited",
            "date_filed": "2026-05-18",
        })

    out_predictions.parent.mkdir(parents=True, exist_ok=True)
    pred_df.to_csv(out_predictions, sep="\t", index=False)
    speculation_columns = [
        "track", "speculation_statement", "family", "expected_validation_source",
        "status", "date_filed",
    ]
    pd.DataFrame(speculation, columns=speculation_columns).to_csv(
        out_speculation, sep="\t", index=False
    )

    sig_out = sig_df.copy()
    sig_out["w_specificity"] = sig_out["compound_class"].map(spec).fillna(0.0)
    sig_out["family_status"] = sig_out["family"].map(
        fam_status.set_index("family")["family_status"]
    )
    sig_out["duke_share_in_family"] = sig_out["family"].map(fam_duke_share).fillna(0.0)
    sig_out.to_parquet(out_signatures, index=False)

    # Append a status row per data-limited family to the signatures table (Test D)
    extra = []
    for _, r in fam_status[fam_status["family_status"].str.startswith("data-limited")].iterrows():
        extra.append({
            "family": r["family"], "compound_class": "__family_status__",
            "n_in_class": 0, "n_screened": int(r["n_screened_taxa"]),
            "signature": 0.0, "w_specificity": 0.0,
            "family_status": r["family_status"],
            "duke_share_in_family": float(fam_duke_share.get(r["family"], 0.0)),
        })
    if extra:
        sig_out2 = pd.concat([sig_out, pd.DataFrame(extra)], ignore_index=True)
        sig_out2.to_parquet(out_signatures, index=False)

    summary = {
        "n_qualifying_families": len(qualifying),
        "n_data_limited_families": int((fam_status["family_status"].str.startswith("data-limited")).sum()),
        "n_predictions": int(len(pred_df)),
        "n_speculation_rows": len(speculation),
        "loso_drop_source_class": loso_drop_source_class,
        "rng_seed": rng_seed,
    }
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--track5-dir", default="tracks/track5")
    ap.add_argument("--loso-drop-source-class", default=None,
                    help="Drop all retained rows whose source_class equals this string (LOSO).")
    ap.add_argument("--out-prefix", default="phytochemistry")
    args = ap.parse_args()
    d = Path(args.track5_dir) / "data"
    summary = run_predictor(
        enrichment_path=d / "track5_enrichment_edges.parquet",
        screening_path=d / "per_taxon_screening_intensity.tsv",
        compound_class_path=d / "track5_compound_class_membership.parquet",
        bioactivity_path=d / "track5_bioactivity_assertions.parquet",
        taxon_family_path=d / "track5_taxon_to_family.parquet",
        out_predictions=d / f"{args.out_prefix}_predictions.tsv",
        out_signatures=d / f"{args.out_prefix}_signatures.parquet",
        out_speculation=d / f"{args.out_prefix}_speculation.tsv",
        loso_drop_source_class=args.loso_drop_source_class,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
