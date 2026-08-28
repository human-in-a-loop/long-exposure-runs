"""Driver for M-EAR-1/synthetic-label-stability-audit.

Loads the frozen 55-clip feature cache; loops over the 10 SHA-256-salted
recipes from ``synthetic_labels.RECIPES``; per recipe runs 5-fold stratified
CV via the existing ``scripts.ear.model.train_and_eval`` chassis; captures
per-fold MAE and per-clip predicted rank.

Aggregates:
  - MAE envelope (mean, 5th/50th/95th) across the 10 recipes.
  - 45 pairwise Kendall τ-b across recipe-level 55-vector predicted ranks.
  - Per-clip band variance across the 10 recipes.

Emits (under ``data/ear/stability_audit/``):
  stability_report.json         # machine-readable summary
  per_recipe_mae.tsv            # 10 rows
  rank_matrix.tsv               # 55 x 10 predicted ranks
  tau_pairs.tsv                 # 45 rows
  per_clip_band_variance.tsv    # 55 rows

Byte-deterministic: identical outputs on repeated invocations under the
single-thread BLAS pins (verified via C3).

Non-factor isolation: NO import of scripts.classifier.sidecar_nonfactor.
Interpreter guard: /usr/bin/python3.
"""
# created: 2026-08-28T17:34:00Z  cycle: 22  run_id: run-2026-08-28T040704Z
# agent: worker (clone-2, fork cc548ca0c2e5)  milestone: M-EAR-1/synthetic-label-stability-audit
from __future__ import annotations
from . import _interp  # noqa: F401 -- interpreter guard

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

# Single-thread BLAS envelope pinned before numpy / torch import.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

import numpy as np

from .synthetic_labels import RECIPES, apply_recipe
from .stability_metrics import kendall_tau_exact, mae_envelope, per_clip_band_variance
from .model import train_and_eval, K


OUT_DIR = Path("data/ear/stability_audit")
DEFAULT_VALSET = Path("data/classifier/valset/valset_manifest.tsv")


# ---------------------------------------------------------------------------
# Feature-cache load (deterministic clip order = sorted-by-clip_id)
# ---------------------------------------------------------------------------
def load_features(valset: Path) -> tuple[list[str], dict[str, np.ndarray], np.ndarray]:
    """Load per-clip features from the frozen data/ear/features/ cache.

    Returns:
      clip_ids sorted lexicographically (deterministic order),
      dict clip_id -> concatenated feature vector (panns_embed + heuristic_vec),
      X ndarray (N, feat_dim) in that order.
    """
    from .features import CACHE_DIR
    with valset.open() as f:
        header = f.readline().rstrip("\n").split("\t")
        rows = [dict(zip(header, ln.rstrip("\n").split("\t"))) for ln in f if ln.strip()]
    clip_ids = sorted(r["clip_id"] for r in rows)
    features: dict[str, np.ndarray] = {}
    for cid in clip_ids:
        p = CACHE_DIR / f"{cid}.npz"
        if not p.exists():
            raise SystemExit(f"[FAIL] missing feature cache for {cid} at {p}")
        npz = np.load(p, allow_pickle=False)
        vec = np.concatenate(
            [npz["panns_embed"], npz["heuristic_vec"]], axis=0
        ).astype(np.float32)
        features[cid] = vec
    X = np.stack([features[c] for c in clip_ids], axis=0)
    return clip_ids, features, X


# ---------------------------------------------------------------------------
# Per-recipe 5-fold CV: MAE + per-clip predicted rank (out-of-fold assembly)
# ---------------------------------------------------------------------------
def _run_one_recipe(
    recipe: dict, features: dict[str, np.ndarray], clip_ids: list[str], X: np.ndarray, *, epochs: int
) -> dict:
    """Return per-recipe summary.

    Uses model.train_and_eval to get per-fold metrics (MAE etc.), then a
    parallel out-of-fold pass with the SAME splitter to record per-clip
    predicted rank in the deterministic clip_ids order.
    """
    labels_map = apply_recipe(recipe, features)
    y = np.asarray([labels_map[c] for c in clip_ids], dtype=np.int64)

    # Per-fold metrics via existing chassis (unmodified).
    fold_metrics = train_and_eval(X, y, seed=0, n_splits=5, epochs=epochs)

    # Out-of-fold predicted ranks. Reproduce train_and_eval's splitter exactly.
    from .model import _fit, set_determinism
    from sklearn.model_selection import StratifiedKFold
    from collections import Counter

    set_determinism(0)
    # NaN-safe X copy (train_and_eval already does this internally too).
    Xc = X.astype(np.float32).copy()
    col_mean = np.nanmean(Xc, axis=0)
    for j in range(Xc.shape[1]):
        m = np.isnan(Xc[:, j])
        Xc[m, j] = 0.0 if not np.isfinite(col_mean[j]) else col_mean[j]

    strat_key = y.copy()
    cnt = Counter(strat_key.tolist())
    if any(v < 5 for v in cnt.values()):
        strat_key = np.clip(np.round((y - 1) / 2), 0, 3).astype(int)
    kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)

    oof_pred = np.full(y.shape, -1, dtype=np.int64)
    for fi, (tr_idx, te_idx) in enumerate(kf.split(Xc, strat_key)):
        pred = _fit(Xc[tr_idx], y[tr_idx], Xc[te_idx], y[te_idx], seed=0 + fi, epochs=epochs)
        oof_pred[te_idx] = pred
    assert (oof_pred >= 1).all(), "oof coverage broken"

    per_fold_maes = [m.mae for m in fold_metrics]
    return {
        "idx": recipe["idx"],
        "family": recipe["family"],
        "salt": recipe["salt"],
        "labels_by_clip": {c: int(labels_map[c]) for c in clip_ids},
        "labels_histogram": {str(k): int(v) for k, v in sorted(Counter(labels_map.values()).items())},
        "per_fold_mae": [float(x) for x in per_fold_maes],
        "mean_mae": float(np.mean(per_fold_maes)),
        "std_mae": float(np.std(per_fold_maes, ddof=0)),
        "predicted_ranks": [int(x) for x in oof_pred],
        "oof_mae": float(np.mean(np.abs(oof_pred - y))),
    }


# ---------------------------------------------------------------------------
# Deterministic JSON canonicalization
# ---------------------------------------------------------------------------
def _canonical_json(obj) -> str:
    """sort_keys + ensure_ascii + compact separators + float repr = deterministic."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _sha256_of_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# TSV writers (deterministic newline, no trailing whitespace)
# ---------------------------------------------------------------------------
def _write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="\n") as f:
        f.write("\t".join(header) + "\n")
        for row in rows:
            f.write("\t".join(row) + "\n")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def run_audit(
    *,
    valset: Path = DEFAULT_VALSET,
    out_dir: Path = OUT_DIR,
    epochs: int = 200,
    cycle6_mae: float = 0.890909090909091,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)

    clip_ids, features, X = load_features(valset)
    assert len(clip_ids) == 55, f"expected 55 clips, got {len(clip_ids)}"

    per_recipe = [
        _run_one_recipe(r, features, clip_ids, X, epochs=epochs) for r in RECIPES
    ]

    # ------------------------------------------------------------------ MAE envelope
    per_recipe_mean_mae = [r["mean_mae"] for r in per_recipe]
    envelope = mae_envelope(per_recipe_mean_mae)

    # ------------------------------------------------------------------ Pairwise τ
    rank_matrix = np.array(
        [r["predicted_ranks"] for r in per_recipe], dtype=np.int64
    ).T  # (n_clips, n_recipes)
    tau_pairs = []
    for i in range(len(per_recipe)):
        for j in range(i + 1, len(per_recipe)):
            res = kendall_tau_exact(rank_matrix[:, i], rank_matrix[:, j])
            tau_pairs.append({
                "recipe_i": per_recipe[i]["idx"],
                "recipe_j": per_recipe[j]["idx"],
                "kendall_tau": res["tau_b"],
                "n_concordant": res["n_concordant"],
                "n_discordant": res["n_discordant"],
                "n_tied_a": res["n_tied_a"],
                "n_tied_b": res["n_tied_b"],
                "n_tied_both": res["n_tied_both"],
            })
    taus = np.array([p["kendall_tau"] for p in tau_pairs], dtype=np.float64)
    tau_summary = {
        "mean": float(taus.mean()),
        "p05": float(np.percentile(taus, 5.0, method="linear")),
        "p50": float(np.percentile(taus, 50.0, method="linear")),
        "p95": float(np.percentile(taus, 95.0, method="linear")),
        "min": float(taus.min()),
        "max": float(taus.max()),
        "n_pairs": int(taus.size),
    }

    # ------------------------------------------------------------------ Per-clip variance
    per_clip = per_clip_band_variance(rank_matrix)
    per_clip_rows = []
    for i, cid in enumerate(clip_ids):
        per_clip_rows.append({
            "clip_id": cid,
            "mean_rank": float(per_clip["mean_rank"][i]),
            "band_variance": float(per_clip["band_variance"][i]),
        })

    # ------------------------------------------------------------------ Verdicts
    c1_pass = envelope["p05"] <= cycle6_mae <= envelope["p95"]
    p01 = float(np.percentile(per_recipe_mean_mae, 1.0, method="linear"))
    p99 = float(np.percentile(per_recipe_mean_mae, 99.0, method="linear"))
    if c1_pass:
        c1_verdict = "PASS"
    elif p01 <= cycle6_mae <= p99:
        c1_verdict = "PARTIAL"
    else:
        c1_verdict = "FAIL"

    c2_verdict = "PASS" if tau_summary["mean"] >= 0.7 else (
        "PARTIAL" if tau_summary["mean"] >= 0.55 else "FAIL"
    )
    # C3 is byte-determinism × 2 — decided post-hoc by comparing two full runs.

    # ------------------------------------------------------------------ Report skeleton
    report = {
        "milestone_id": "M-EAR-1/synthetic-label-stability-audit",
        "cycle": 22,
        "run_id": "run-2026-08-28T040704Z",
        "n_clips": len(clip_ids),
        "feat_dim": int(X.shape[1]),
        "n_recipes": len(per_recipe),
        "K": K,
        "epochs": epochs,
        "clip_ids": clip_ids,
        "cycle6_reference": {
            "mae_mean": cycle6_mae,
            "source": "data/ear/model_sanity.json (cycle 6)",
        },
        "per_recipe": per_recipe,
        "mae_envelope": {
            "values": per_recipe_mean_mae,
            **envelope,
            "cycle6_inside_5th_95th": bool(c1_pass),
            "cycle6_inside_1st_99th": bool(p01 <= cycle6_mae <= p99),
            "p01": p01,
            "p99": p99,
        },
        "tau_pairs": tau_pairs,
        "tau_summary": tau_summary,
        "per_clip_band_variance": per_clip_rows,
        "criteria": {
            "C1": {
                "name": "MAE reproducibility",
                "threshold": "cycle-6 MAE inside [5th, 95th] percentile envelope",
                "cycle6_mae": cycle6_mae,
                "envelope_p05": envelope["p05"],
                "envelope_p95": envelope["p95"],
                "verdict": c1_verdict,
            },
            "C2": {
                "name": "Rank stability",
                "threshold": "mean pairwise Kendall τ-b ≥ 0.7",
                "observed_mean_tau": tau_summary["mean"],
                "verdict": c2_verdict,
            },
            "C3": {
                "name": "Byte-determinism × 2",
                "threshold": "SHA-256(stability_report.json) equal across two runs",
                "verdict": "PENDING",
            },
        },
    }

    # ------------------------------------------------------------------ Emit files
    tsv_recipe = out_dir / "per_recipe_mae.tsv"
    _write_tsv(
        tsv_recipe,
        header=["recipe_idx", "family", "salt", "mean_mae", "std_mae", "folds_mae_json"],
        rows=[
            [
                str(r["idx"]), r["family"], r["salt"],
                f"{r['mean_mae']:.10f}", f"{r['std_mae']:.10f}",
                _canonical_json(r["per_fold_mae"]),
            ]
            for r in per_recipe
        ],
    )
    tsv_rank = out_dir / "rank_matrix.tsv"
    _write_tsv(
        tsv_rank,
        header=["clip_id"] + [f"recipe_{r['idx']}" for r in per_recipe],
        rows=[
            [clip_ids[i]] + [str(int(rank_matrix[i, j])) for j in range(len(per_recipe))]
            for i in range(len(clip_ids))
        ],
    )
    tsv_tau = out_dir / "tau_pairs.tsv"
    _write_tsv(
        tsv_tau,
        header=["recipe_i", "recipe_j", "kendall_tau", "n_concordant", "n_discordant", "n_tied_a", "n_tied_b"],
        rows=[
            [
                str(p["recipe_i"]), str(p["recipe_j"]),
                f"{p['kendall_tau']:.10f}",
                str(p["n_concordant"]), str(p["n_discordant"]),
                str(p["n_tied_a"]), str(p["n_tied_b"]),
            ]
            for p in tau_pairs
        ],
    )
    tsv_var = out_dir / "per_clip_band_variance.tsv"
    _write_tsv(
        tsv_var,
        header=["clip_id", "mean_rank", "band_variance"],
        rows=[
            [row["clip_id"], f"{row['mean_rank']:.10f}", f"{row['band_variance']:.10f}"]
            for row in per_clip_rows
        ],
    )

    # Canonical JSON write — this file is what C3 hashes.
    report_path = out_dir / "stability_report.json"
    report_path.write_text(_canonical_json(report) + "\n")
    report_sha = _sha256_of_str(_canonical_json(report) + "\n")

    print(f"[stability_audit] n_recipes={len(per_recipe)} n_clips={len(clip_ids)}")
    print(f"[stability_audit] MAE envelope: p05={envelope['p05']:.4f} p50={envelope['p50']:.4f} p95={envelope['p95']:.4f} mean={envelope['mean']:.4f}")
    print(f"[stability_audit] mean pairwise τ = {tau_summary['mean']:.4f} (p05={tau_summary['p05']:.4f}, min={tau_summary['min']:.4f})")
    print(f"[stability_audit] C1={c1_verdict} C2={c2_verdict} C3=PENDING (byte-determinism × 2 decided offline)")
    print(f"[stability_audit] wrote {report_path}  sha256={report_sha[:16]}...")

    return {"report_path": str(report_path), "sha256": report_sha, "report": report}


def _main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--valset", type=Path, default=DEFAULT_VALSET)
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--epochs", type=int, default=200)
    args = ap.parse_args(argv)
    run_audit(valset=args.valset, out_dir=args.out_dir, epochs=args.epochs)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
