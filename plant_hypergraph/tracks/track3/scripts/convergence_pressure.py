"""
Track 3 Convergence-Pressure statistic (Wave 3 / M3.T3).

created:    2026-05-18T02:00:00+00:00
cycle:      8
fork:       e08673192f98
clone:      2
run_id:     run-phytograph-cycle8-track3-convergence-pressure
agent:      worker
milestone:  M3.T3 (_plan/wave3-track3-convergence-pressure)

Purpose
-------
Compute CP_min(T) = min(CP_N1, CP_N2) for the frozen Track 3 canonical trait
set. Family-share Shannon entropy H_family(T) is standardized against two
permutation nulls:

  N1  Family-size-preserving (trait x family contingency table with fixed
      row and column marginals, swap Markov chain).
  N2  Sampling-density-preserving (carriers drawn from the substrate weighted
      by per-taxon total_track3_edge_count to mimic the AusTraits-heavy
      coding-intensity confound).

Falsifier
---------
OLS of observed H_family on (log n_families, log n_carriers, log mean
sampling density) over the 12 canonical traits. If R^2(observed) >= 0.7 and
CP_min ranking matches confound-residual ranking on Spearman rho > 0.8, the
statistic is collinear with confounds and H3 is falsified against this
substrate. Verdict is emitted to convergence_pressure_confound_regression.tsv.

Discipline
----------
- Reads only tracks/track3/data/convergence_trait_edges.parquet and the
  frozen substrate parquets under phytograph_dataset/.
- Writes only under tracks/track3/data/.
- No paid-provider SDKs imported.
- Deterministic: np.random.default_rng(20260517).
- `_other` excluded from canonical scoring via hard assert; reported as a
  companion sanity-check row with excluded_from_canonical=True.

Usage
-----
    python3 tracks/track3/scripts/convergence_pressure.py

CLI has no flags; all parameters frozen for reproducibility.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# Make sibling import work whether invoked as module or script.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from trait_dictionary import (  # noqa: E402
    CANONICAL_TRAITS,
    TRAITS_WITHOUT_SUBSTRATE_LABEL,
)

# ----- Frozen constants -------------------------------------------------------

SEED = 20260517
B_REPLICATES = 1000
SWAP_MULTIPLIER = 10            # swaps per replicate = SWAP_MULTIPLIER * n_pairs
CP_THRESHOLD = 2.0              # z-score >= 2.0 clears the convergence bar
EXCLUDED_FROM_SCORING: Tuple[str, ...] = ("_other",)
STAT_VERSION = "track3-cp-v1.0"
DATE_FILED = "2026-05-18"

REPO = Path(__file__).resolve().parents[3]
ENRICHMENT_TABLE = REPO / "tracks" / "track3" / "data" / "convergence_trait_edges.parquet"
OUT_DIR = REPO / "tracks" / "track3" / "data"

PREDICTION_COLUMNS = [
    "track",
    "prediction_id",
    "trait",
    "rank",
    "row_class",
    "prediction_statement",
    "supporting_hyperedges",
    "supporting_node_set",
    "score",
    "CP_N1",
    "CP_N2",
    "CP_min",
    "n_carriers",
    "n_families",
    "observed_trait_evidence_count",
    "observed_evidence_scope",
    "expected_validation_source",
    "status",
    "validation_ready",
    "hypothesis_caveat",
    "ablation_sensitivity",
    "excluded_from_canonical",
    "enters_master_prediction_ledger",
    "date_filed",
    "date_resolved",
]

# Canonical "textbook expected" band for high-priority convergent cases.
# HIGH = strong textbook convergence (C4 ~60 origins, fleshy fruit >100 origins).
# MEDIUM = recurrent dispersal syndrome / fruit syndrome.
# LOW (single-family / Aus-confounded) = aril (Sapindaceae-dominated),
#                                         follicle (Proteaceae-dominated),
#                                         samara (3 families in substrate).
TEXTBOOK_BAND: Dict[str, str] = {
    "c4_photosynthesis": "high",
    "fleshy_fruit": "high",
    "drupe": "high",
    "myrmecochory": "medium",
    "elaiosome": "medium",
    "samara": "medium",
}


# ----- Core statistic ---------------------------------------------------------


def shannon_entropy(counts: np.ndarray) -> float:
    """Natural-log Shannon entropy of a non-negative count vector."""
    counts = counts[counts > 0].astype(float)
    if counts.size == 0:
        return float("nan")
    p = counts / counts.sum()
    return float(-np.sum(p * np.log(p)))


def load_carriers() -> pd.DataFrame:
    """Dedup (trait, accepted_taxon_key, family_key, family_label) carriers.

    Returns columns: trait, accepted_taxon_key, family_key, family_label,
    source_edge_id, source_id.
    """
    df = pd.read_parquet(ENRICHMENT_TABLE)
    keep = [
        "trait", "accepted_taxon_key", "family_key", "family_label",
        "source_edge_id", "source_id",
    ]
    carriers = (
        df[keep]
        .drop_duplicates(subset=["trait", "accepted_taxon_key"])
        .reset_index(drop=True)
    )
    return carriers


def observed_signal(carriers: pd.DataFrame) -> pd.DataFrame:
    """One row per trait with n_carriers, n_families, H_family."""
    rows = []
    for trait, sub in carriers.groupby("trait", sort=True):
        fam_counts = sub["family_key"].value_counts().to_numpy()
        rows.append({
            "trait": trait,
            "n_carriers": int(len(sub)),
            "n_families": int(len(fam_counts)),
            "H_family": shannon_entropy(fam_counts),
        })
    return pd.DataFrame(rows).sort_values("trait").reset_index(drop=True)


# ----- N1 null: family-size-preserving via swap Markov chain ------------------


def n1_swap_null(
    canonical_carriers: pd.DataFrame,
    rng: np.random.Generator,
    b: int,
    swap_mult: int,
) -> Dict[str, np.ndarray]:
    """Swap Markov chain on (trait, family) carrier tokens.

    Preserves per-trait carrier counts and per-family carrier loads. Each
    replicate copies the observed list, performs K = swap_mult * n_pairs
    independent (trait, family) swaps, then recomputes H_family per trait.
    Returns dict trait -> array of B null H_family values.
    """
    sub = canonical_carriers[canonical_carriers["trait"] != "_other"].copy()
    traits = sub["trait"].to_numpy()
    families = sub["family_key"].to_numpy()
    n_pairs = len(sub)
    if n_pairs == 0:
        return {t: np.full(b, np.nan) for t in canonical_carriers["trait"].unique()}

    distinct_traits = sorted(set(traits))
    n_swaps = swap_mult * n_pairs
    out: Dict[str, List[float]] = {t: [] for t in distinct_traits}

    for _ in range(b):
        perm_fam = families.copy()
        # vectorize swaps by pre-sampling index pairs
        idx_a = rng.integers(0, n_pairs, size=n_swaps)
        idx_b = rng.integers(0, n_pairs, size=n_swaps)
        for k in range(n_swaps):
            i, j = idx_a[k], idx_b[k]
            tmp = perm_fam[i]
            perm_fam[i] = perm_fam[j]
            perm_fam[j] = tmp
        # H_family per trait
        for t in distinct_traits:
            mask = traits == t
            fams = perm_fam[mask]
            uniq, cnt = np.unique(fams, return_counts=True)
            out[t].append(shannon_entropy(cnt))

    return {t: np.asarray(v, dtype=float) for t, v in out.items()}


# ----- N2 null: sampling-density-preserving weighted draw ---------------------


def per_taxon_edge_count() -> pd.DataFrame:
    """total_track3_edge_count per accepted_taxon_key, including _other rows.

    The screening-intensity confound is over ALL track-3 edges a taxon has,
    not just canonical ones; we want to model AusTraits coding intensity.
    Columns: accepted_taxon_key, family_key, total_track3_edge_count.
    """
    df = pd.read_parquet(ENRICHMENT_TABLE)
    grp = (
        df.groupby(["accepted_taxon_key", "family_key", "family_label"])
        .size()
        .reset_index(name="total_track3_edge_count")
    )
    return grp


def n2_weighted_null(
    observed: pd.DataFrame,
    weighted_pool: pd.DataFrame,
    rng: np.random.Generator,
    b: int,
) -> Dict[str, np.ndarray]:
    """For each canonical trait, draw n_carriers(T) taxa from substrate pool
    weighted by total_track3_edge_count. Compute H_family of drawn taxa's
    families. B replicates per trait.
    """
    pool_keys = weighted_pool["accepted_taxon_key"].to_numpy()
    pool_fams = weighted_pool["family_key"].to_numpy()
    weights = weighted_pool["total_track3_edge_count"].to_numpy().astype(float)
    probs = weights / weights.sum()

    out: Dict[str, np.ndarray] = {}
    n_pool = len(pool_keys)
    for _, row in observed.iterrows():
        t = row["trait"]
        n_t = int(row["n_carriers"])
        if t == "_other":
            # skip computing the null for excluded; it gets a separate companion
            # path below
            out[t] = np.full(b, np.nan)
            continue
        if n_t == 0 or n_t > n_pool:
            out[t] = np.full(b, np.nan)
            continue
        h_arr = np.empty(b, dtype=float)
        for k in range(b):
            idx = rng.choice(n_pool, size=n_t, replace=False, p=probs)
            fams = pool_fams[idx]
            uniq, cnt = np.unique(fams, return_counts=True)
            h_arr[k] = shannon_entropy(cnt)
        out[t] = h_arr
    return out


# ----- OLS for confound regression -------------------------------------------


def ols_fit(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, float, np.ndarray]:
    """OLS with intercept. Returns (coeffs, R2, residuals).

    X is (n, k) without intercept; intercept prepended.
    """
    n = X.shape[0]
    X1 = np.column_stack([np.ones(n), X])
    beta, *_ = np.linalg.lstsq(X1, y, rcond=None)
    yhat = X1 @ beta
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return beta, r2, y - yhat


def spearman_rho(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman rank correlation (no scipy)."""
    ra = pd.Series(a).rank().to_numpy().astype(float).copy()
    rb = pd.Series(b).rank().to_numpy().astype(float).copy()
    ra = ra - ra.mean(); rb = rb - rb.mean()
    denom = math.sqrt(float(np.sum(ra ** 2) * np.sum(rb ** 2)))
    if denom == 0:
        return float("nan")
    return float(np.sum(ra * rb) / denom)


def prediction_row_class(row: pd.Series) -> Tuple[str, str, bool]:
    """Return (row_class, status, validation_ready) for one score row."""
    if bool(row["excluded_from_canonical"]):
        return "diagnostic_bucket_excluded", "diagnostic_not_prediction", False
    if row["data_limited"] == "yes":
        return "data_limited_canonical_trait", "data_limited_not_prediction", False
    if bool(row["clears_bar"]):
        return "pending_convergent_trait_hypothesis", "pending", True
    return "observed_trait_evidence_summary", "observed_evidence_not_prediction", False


def build_prediction_rows(scores_df: pd.DataFrame, carriers: pd.DataFrame) -> pd.DataFrame:
    """Track-local prediction/evidence TSV for Barrier 3 Atlas ingestion.

    The file deliberately mixes pending hypotheses with non-prediction evidence
    summaries so downstream readers can see why only threshold-clearing
    canonical traits are predictions. No row is written to the master ledger in
    M3.T3.
    """
    rows = []
    ranked = scores_df.copy()
    ranked["_rank_score"] = ranked["CP_min"].fillna(-1e9)
    ranked = ranked.sort_values(
        ["excluded_from_canonical", "_rank_score", "trait"],
        ascending=[True, False, True],
    ).drop(columns=["_rank_score"])

    rank = 0
    for _, r in ranked.iterrows():
        trait = r["trait"]
        row_class, status, validation_ready = prediction_row_class(r)
        if not bool(r["excluded_from_canonical"]):
            rank += 1
            rank_value = rank
        else:
            rank_value = ""

        trait_edges = carriers[carriers["trait"] == trait]
        evidence_count = int(len(trait_edges))
        source_edges = sorted(set(trait_edges["source_edge_id"].dropna().astype(str)))
        supporting_hyperedges = ";".join(source_edges[:25])
        if len(source_edges) > 25:
            supporting_hyperedges += f";...(+{len(source_edges) - 25} more)"

        top_families = (
            trait_edges["family_label"].replace("", np.nan).dropna().value_counts()
            .head(5)
        )
        supporting_node_set = json.dumps({
            "trait": trait,
            "top_observed_families": top_families.to_dict(),
            "n_carriers": int(r["n_carriers"]),
            "n_families": int(r["n_families"]),
        }, sort_keys=True)

        if row_class == "pending_convergent_trait_hypothesis":
            statement = (
                "Hypothesis for validation: Track 3 convergence pressure ranks "
                f"`{trait}` as unusually dispersed across families relative to "
                "both family-size-preserving and sampling-density-preserving "
                f"nulls (CP_min={float(r['CP_min']):.3f}). This is a pending "
                "convergent-trait hypothesis, not an adaptive-origin or new "
                "trait-occurrence claim."
            )
            expected_validation = (
                "Wave 4 held-out convergence validation against independently "
                "curated trait lists and source-density/family-size ablations."
            )
        elif row_class == "observed_trait_evidence_summary":
            statement = (
                f"Observed evidence summary only: `{trait}` has retained Track 3 "
                f"trait-membership evidence for {int(r['n_carriers'])} accepted "
                "taxa, but it does not clear the convergence-pressure threshold "
                "under the current frozen substrate."
            )
            expected_validation = "not applicable: retained observed evidence summary, not a prediction"
        elif row_class == "data_limited_canonical_trait":
            statement = (
                f"Data-limited non-prediction: `{trait}` is on the canonical "
                "Track 3 axis but has no retained accepted-key carrier in the "
                "current frozen substrate."
            )
            expected_validation = "source recovery side-wave required before predictive validation"
        else:
            statement = (
                "`_other` diagnostic bucket: out-of-axis AusTraits labels are "
                "retained for coverage auditing and excluded from canonical "
                "convergence-pressure scoring."
            )
            expected_validation = "not applicable: diagnostic bucket excluded from canonical scoring"

        rows.append({
            "track": "track3",
            "prediction_id": f"T3-CONV-{len(rows) + 1:04d}",
            "trait": trait,
            "rank": rank_value,
            "row_class": row_class,
            "prediction_statement": statement,
            "supporting_hyperedges": supporting_hyperedges,
            "supporting_node_set": supporting_node_set,
            "score": float(r["CP_min"]) if not math.isnan(float(r["CP_min"])) else "",
            "CP_N1": float(r["CP_N1"]) if not math.isnan(float(r["CP_N1"])) else "",
            "CP_N2": float(r["CP_N2"]) if not math.isnan(float(r["CP_N2"])) else "",
            "CP_min": float(r["CP_min"]) if not math.isnan(float(r["CP_min"])) else "",
            "n_carriers": int(r["n_carriers"]),
            "n_families": int(r["n_families"]),
            "observed_trait_evidence_count": evidence_count,
            "observed_evidence_scope": (
                "retained Track 3 trait_membership evidence only; supports "
                "source-coded trait occurrence, not independent convergence, "
                "adaptive mechanism, or undocumented taxon-level trait claims"
            ),
            "expected_validation_source": expected_validation,
            "status": status,
            "validation_ready": validation_ready,
            "hypothesis_caveat": (
                "candidate convergence-pressure prior only; validate against "
                "independent trait lists and ablations before master-ledger "
                "promotion"
            ),
            "ablation_sensitivity": (
                "family-size null N1; sampling-density null N2; source-density "
                "control; removal of AusTraits-derived trait_membership rows; "
                "family-size/sampling-density confound regression"
            ),
            "excluded_from_canonical": bool(r["excluded_from_canonical"]),
            "enters_master_prediction_ledger": False,
            "date_filed": DATE_FILED,
            "date_resolved": "",
        })

    return pd.DataFrame(rows, columns=PREDICTION_COLUMNS)


# ----- Build pipeline ---------------------------------------------------------


def build(out_dir: Path = OUT_DIR) -> Dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    carriers = load_carriers()
    observed = observed_signal(carriers)
    # `_other` is handled once below as a diagnostic companion row. Keeping it
    # in observed would create a duplicate excluded row and blur the canonical
    # score table.
    observed = observed[~observed["trait"].isin(EXCLUDED_FROM_SCORING)].copy()

    # Append data-limited canonical traits with zero carriers.
    present = set(observed["trait"].tolist())
    for t in TRAITS_WITHOUT_SUBSTRATE_LABEL:
        if t not in present:
            observed = pd.concat(
                [observed,
                 pd.DataFrame([{"trait": t, "n_carriers": 0,
                                "n_families": 0, "H_family": float("nan")}])],
                ignore_index=True,
            )
    observed = observed.sort_values("trait").reset_index(drop=True)

    # Hard guard: no _other in the canonical scoring path.
    scored_traits = [t for t in observed["trait"]
                     if t not in EXCLUDED_FROM_SCORING and t in CANONICAL_TRAITS]
    assert "_other" not in scored_traits, "_other leaked into scored traits"
    assert set(scored_traits).issubset(set(CANONICAL_TRAITS))

    # ---- N1 null (canonical-only carriers) -------------------------------
    n1_h = n1_swap_null(
        carriers[carriers["trait"].isin(scored_traits)].copy(),
        rng, B_REPLICATES, SWAP_MULTIPLIER,
    )

    # ---- N2 null (weighted draw from full substrate) ---------------------
    pool = per_taxon_edge_count()
    n2_h = n2_weighted_null(observed, pool, rng, B_REPLICATES)

    # ---- Companion _other row: compute its own n_carriers, H_family,
    #      and run N2 for sanity check (no N1 because _other is not in
    #      the canonical scored set).
    other_carriers = carriers[carriers["trait"] == "_other"]
    n_other = other_carriers["accepted_taxon_key"].nunique()
    n_other_fam = other_carriers["family_key"].nunique()
    h_other = shannon_entropy(
        other_carriers["family_key"].value_counts().to_numpy()
    )
    other_n2 = n2_weighted_null(
        pd.DataFrame([{"trait": "_other", "n_carriers": n_other,
                       "n_families": n_other_fam, "H_family": h_other}]),
        pool, np.random.default_rng(SEED + 1), B_REPLICATES,
    )
    # _other in n2 dict above will be NaN due to skip; override:
    rng_o = np.random.default_rng(SEED + 1)
    pool_keys = pool["accepted_taxon_key"].to_numpy()
    pool_fams = pool["family_key"].to_numpy()
    pool_w = pool["total_track3_edge_count"].to_numpy().astype(float)
    pool_p = pool_w / pool_w.sum()
    n_pool = len(pool_keys)
    other_h_n2 = np.empty(B_REPLICATES, dtype=float)
    n_draw = min(n_other, n_pool)
    for k in range(B_REPLICATES):
        idx = rng_o.choice(n_pool, size=n_draw, replace=False, p=pool_p)
        fams = pool_fams[idx]
        uniq, cnt = np.unique(fams, return_counts=True)
        other_h_n2[k] = shannon_entropy(cnt)

    # ---- Compose scores TSV ---------------------------------------------
    rows = []
    for _, r in observed.iterrows():
        t = r["trait"]
        excluded = t in EXCLUDED_FROM_SCORING
        data_limited = (r["n_carriers"] == 0)
        if data_limited or excluded:
            cp_n1 = float("nan")
            cp_n2 = float("nan")
        else:
            n1arr = n1_h.get(t, np.full(B_REPLICATES, np.nan))
            n2arr = n2_h.get(t, np.full(B_REPLICATES, np.nan))
            cp_n1 = float((r["H_family"] - np.nanmean(n1arr)) /
                          np.nanstd(n1arr)) if np.nanstd(n1arr) > 0 else float("nan")
            cp_n2 = float((r["H_family"] - np.nanmean(n2arr)) /
                          np.nanstd(n2arr)) if np.nanstd(n2arr) > 0 else float("nan")
        cp_min = float("nan") if math.isnan(cp_n1) or math.isnan(cp_n2) \
                              else min(cp_n1, cp_n2)
        clears_bar = (not math.isnan(cp_min)) and (cp_min > CP_THRESHOLD) and (not excluded)
        rows.append({
            "trait": t,
            "n_carriers": int(r["n_carriers"]),
            "n_families": int(r["n_families"]),
            "H_family": float(r["H_family"]) if r["n_carriers"] > 0 else float("nan"),
            "CP_N1": cp_n1,
            "CP_N2": cp_n2,
            "CP_min": cp_min,
            "clears_bar": bool(clears_bar),
            "data_limited": "yes" if data_limited else "no",
            "excluded_from_canonical": bool(excluded),
        })

    # _other companion: compute CP_N2 only (CP_N1 not defined for excluded).
    cp_n2_other = float((h_other - np.nanmean(other_h_n2)) /
                        np.nanstd(other_h_n2)) if np.nanstd(other_h_n2) > 0 \
                                                else float("nan")
    rows.append({
        "trait": "_other",
        "n_carriers": int(n_other),
        "n_families": int(n_other_fam),
        "H_family": float(h_other),
        "CP_N1": float("nan"),    # excluded from N1 swap pool by construction
        "CP_N2": cp_n2_other,
        "CP_min": float("nan"),
        "clears_bar": False,
        "data_limited": "no",
        "excluded_from_canonical": True,
    })

    scores_df = pd.DataFrame(rows)
    # Order: canonical (by CP_min desc, NaNs last), then _other.
    canon_mask = ~scores_df["excluded_from_canonical"]
    canon = scores_df[canon_mask].copy()
    canon["_sort"] = canon["CP_min"].fillna(-1e9)
    canon = canon.sort_values("_sort", ascending=False).drop(columns="_sort")
    other = scores_df[~canon_mask]
    scores_df = pd.concat([canon, other], ignore_index=True)

    scores_path = out_dir / "convergence_pressure_scores.tsv"
    scores_df.to_csv(scores_path, sep="\t", index=False, float_format="%.6f")

    predictions_path = out_dir / "convergence_predictions.tsv"
    prediction_df = build_prediction_rows(scores_df, carriers)
    prediction_df.to_csv(predictions_path, sep="\t", index=False, float_format="%.6f")

    # ---- Nulls summary TSV ----------------------------------------------
    null_rows = []
    for t in scored_traits:
        for name, arr in (("N1", n1_h.get(t)), ("N2", n2_h.get(t))):
            if arr is None or np.all(np.isnan(arr)):
                continue
            null_rows.append({
                "trait": t,
                "null": name,
                "mean": float(np.nanmean(arr)),
                "std": float(np.nanstd(arr)),
                "p5": float(np.nanpercentile(arr, 5)),
                "p95": float(np.nanpercentile(arr, 95)),
                "n_replicates": int(np.sum(~np.isnan(arr))),
                "seed": SEED,
            })
    null_rows.append({
        "trait": "_other", "null": "N2",
        "mean": float(np.nanmean(other_h_n2)),
        "std": float(np.nanstd(other_h_n2)),
        "p5": float(np.nanpercentile(other_h_n2, 5)),
        "p95": float(np.nanpercentile(other_h_n2, 95)),
        "n_replicates": int(np.sum(~np.isnan(other_h_n2))),
        "seed": SEED + 1,
    })
    nulls_path = out_dir / "convergence_pressure_nulls.tsv"
    pd.DataFrame(null_rows).to_csv(
        nulls_path, sep="\t", index=False, float_format="%.6f")

    # ---- Confound regression --------------------------------------------
    # Use only canonical traits with n_carriers >= 1.
    fit_df = scores_df[(~scores_df["excluded_from_canonical"]) &
                       (scores_df["n_carriers"] > 0)].copy()
    # Mean sampling density per trait: mean total_track3_edge_count over the
    # trait's carriers.
    pool_lookup = pool.set_index("accepted_taxon_key")["total_track3_edge_count"]
    mean_density = []
    for t in fit_df["trait"]:
        sub = carriers[carriers["trait"] == t]
        d = pool_lookup.reindex(sub["accepted_taxon_key"]).fillna(1.0)
        mean_density.append(float(d.mean()))
    fit_df["mean_sampling_density"] = mean_density

    X = np.column_stack([
        np.log1p(fit_df["n_families"].to_numpy()),
        np.log1p(fit_df["n_carriers"].to_numpy()),
        np.log1p(fit_df["mean_sampling_density"].to_numpy()),
    ])
    y_obs = fit_df["H_family"].to_numpy()
    beta_obs, r2_obs, resid_obs = ols_fit(X, y_obs)

    y_cp = fit_df["CP_min"].to_numpy()
    beta_cp, r2_cp, resid_cp = ols_fit(X, y_cp)

    rho_resid_vs_cp = spearman_rho(resid_obs, y_cp)

    # Falsifier: H3 falsified iff r2_obs >= 0.7 AND rho_resid_vs_cp > 0.8.
    falsifier_trigger = (r2_obs >= 0.7) and (abs(rho_resid_vs_cp) > 0.8)
    verdict = "FALSIFIED (H3)" if falsifier_trigger else "PASS"

    reg_rows = [
        {"name": "intercept_obs",    "coef": float(beta_obs[0])},
        {"name": "log_n_families_obs",   "coef": float(beta_obs[1])},
        {"name": "log_n_carriers_obs",   "coef": float(beta_obs[2])},
        {"name": "log_mean_density_obs", "coef": float(beta_obs[3])},
        {"name": "R2_observed_H_family", "coef": float(r2_obs)},
        {"name": "intercept_cp",     "coef": float(beta_cp[0])},
        {"name": "log_n_families_cp",    "coef": float(beta_cp[1])},
        {"name": "log_n_carriers_cp",    "coef": float(beta_cp[2])},
        {"name": "log_mean_density_cp",  "coef": float(beta_cp[3])},
        {"name": "R2_CP_min",            "coef": float(r2_cp)},
        {"name": "spearman_rho_residOBS_vs_CPmin", "coef": float(rho_resid_vs_cp)},
        {"name": "falsifier_threshold_R2_obs_geq", "coef": 0.7},
        {"name": "falsifier_threshold_abs_rho_gt", "coef": 0.8},
        {"name": "verdict", "coef": verdict},
    ]
    reg_path = out_dir / "convergence_pressure_confound_regression.tsv"
    pd.DataFrame(reg_rows).to_csv(reg_path, sep="\t", index=False)

    # ---- Canonical-case recovery ----------------------------------------
    canon_rank = canon["trait"].tolist()  # already sorted by CP_min desc
    rec_rows = []
    for t, band in TEXTBOOK_BAND.items():
        if t in canon_rank:
            rank = canon_rank.index(t) + 1
        else:
            rank = -1
        row = scores_df[scores_df["trait"] == t]
        cpmin = float(row["CP_min"].iloc[0]) if len(row) else float("nan")
        n_canon = len(canon_rank)
        upper_half = (rank > 0) and (rank <= n_canon // 2 + n_canon % 2)
        rec_rows.append({
            "trait": t,
            "CP_min": cpmin,
            "rank_among_canonical_traits": int(rank),
            "n_canonical_with_score": int(sum(~canon["CP_min"].isna())),
            "expected_band": band,
            "in_upper_half": bool(upper_half),
            "agreement": "yes" if (band == "high" and upper_half) or
                                  (band == "medium" and rank > 0) else "weak",
        })
    rec_path = out_dir / "convergence_pressure_canonical_recovery.tsv"
    pd.DataFrame(rec_rows).to_csv(rec_path, sep="\t", index=False,
                                  float_format="%.6f")

    # ---- Figure (2-panel) -----------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig_path = out_dir / "convergence_pressure_figure.png"
    plot_df = canon.dropna(subset=["CP_min"]).copy()
    plot_df = plot_df.sort_values("CP_min", ascending=True)

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    ax = axes[0]
    ypos = np.arange(len(plot_df))
    ax.barh(ypos, plot_df["CP_min"], color="#3b6ea8")
    # N1/N2 error markers as separate dots
    ax.scatter(plot_df["CP_N1"], ypos + 0.18, marker="o",
               s=24, color="#d97a00", label="CP_N1", zorder=5)
    ax.scatter(plot_df["CP_N2"], ypos - 0.18, marker="s",
               s=24, color="#5fa860", label="CP_N2", zorder=5)
    ax.axvline(CP_THRESHOLD, color="red", linestyle="--",
               label=f"clears_bar threshold = {CP_THRESHOLD}")
    ax.set_yticks(ypos)
    ax.set_yticklabels(plot_df["trait"])
    ax.set_xlabel("CP score (sigma above null)")
    ax.set_title("(a) CP_min by trait, with CP_N1 and CP_N2")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="x", alpha=0.3)

    ax = axes[1]
    sc = ax.scatter(plot_df["n_families"], plot_df["CP_min"],
                    c=plot_df["n_carriers"], cmap="viridis",
                    s=80, edgecolor="black", linewidth=0.5)
    for _, r in plot_df.iterrows():
        ax.annotate(r["trait"], (r["n_families"], r["CP_min"]),
                    fontsize=7, xytext=(4, 3), textcoords="offset points")
    ax.axhline(CP_THRESHOLD, color="red", linestyle="--", alpha=0.6)
    ax.set_xlabel("n_families (carriers/trait)")
    ax.set_ylabel("CP_min")
    ax.set_title("(b) CP_min vs n_families (color = n_carriers)")
    plt.colorbar(sc, ax=ax, label="n_carriers")
    ax.grid(alpha=0.3)

    fig.suptitle(
        f"Track 3 Convergence Pressure ({STAT_VERSION}); seed={SEED}; B={B_REPLICATES}",
        fontsize=10,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(fig_path, dpi=140)
    plt.close(fig)

    # ---- Run summary JSON for audit -------------------------------------
    summary = {
        "version": STAT_VERSION,
        "seed": SEED,
        "b_replicates": B_REPLICATES,
        "swap_multiplier": SWAP_MULTIPLIER,
        "scored_traits": scored_traits,
        "excluded_traits": list(EXCLUDED_FROM_SCORING),
        "data_limited_traits": [t for t in observed["trait"]
                                if int(observed.loc[observed["trait"] == t,
                                                     "n_carriers"].iloc[0]) == 0],
        "falsifier_verdict": verdict,
        "R2_observed": float(r2_obs),
        "R2_CP_min": float(r2_cp),
        "spearman_rho_residOBS_vs_CPmin": float(rho_resid_vs_cp),
    }
    (out_dir / "convergence_pressure_run_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n")

    return {
        "scores": scores_path,
        "nulls": nulls_path,
        "regression": reg_path,
        "recovery": rec_path,
        "figure": fig_path,
        "summary": out_dir / "convergence_pressure_run_summary.json",
        "predictions": predictions_path,
    }


if __name__ == "__main__":
    out = build()
    for k, v in out.items():
        print(f"{k}: {v}")
