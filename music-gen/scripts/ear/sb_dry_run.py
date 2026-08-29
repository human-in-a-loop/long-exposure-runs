#!/usr/bin/env python3
# created: 2026-08-29T00:00:00Z  cycle: 31  run_id: run-2026-08-28T040704Z
# agent: worker (clone-2 fork cfc5009aca96)  milestone: _infra/sb-dry-run-script
"""SB dry-run: compute SB1/SB2/SB3 on the M-CLASS-1 55-clip valset using
synthetic labels (c22 protocol).

Verifies the armed harness can produce all three Path B success bars
end-to-end WITHOUT touching rated audio. Emits
`data/ear/armed_harness_reinforcement/sb_dry_run_verdict.json`.

Determinism: SHA-256 tiebreak throughout; NO PRNG; BLAS thread pins
before any numpy/torch import; `torch.manual_seed(0)`; sorted iteration
over cached feature files. Byte-identical outputs across two fresh
temp-dir runs.

Zero live network. Zero `sidecar_nonfactor` imports. Interpreter
`/usr/bin/python3`.

The dry-run asserts each SB metric is COMPUTABLE (all finite) — it does
NOT assert PASS on synthetic labels. The frozen SB thresholds
(SB1 margin > 0.5909, SB2 τ ≥ 0.4, SB3 detection ≥ 0.90) belong to
real-label calibration and are not re-derived here.
"""
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Optional

import numpy as np

# Read-only anchors:
from scripts.ear.synthetic_labels import RECIPES, apply_recipe
from scripts.ear.stability_metrics import kendall_tau_exact
from scripts.ear.features import FEATURE_VERSION
from scripts.ear.model import CornHead, corn_loss, set_determinism, K, EPOCHS, LR, WD
from scripts.ear.corn import corn_predict


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_VALSET = ROOT / "data" / "classifier" / "valset" / "valset_manifest.tsv"
DEFAULT_FEATURES = ROOT / "data" / "ear" / "features"
DEFAULT_OUT = ROOT / "data" / "ear" / "armed_harness_reinforcement"
RUBRIC_PATH = ROOT / "docs" / "ear_armed_harness_fixture_rubric.md"

FEAT_DIM = 2052
N_BOOTSTRAP = 10          # SB2 methodology: 10 stratified bootstrap resamples
BOOTSTRAP_FRACTION = 0.80  # each resample takes 80% of the clips
LEAK_ALPHA = 1.0          # SB3 detection at α=1.0
SB2_SEED_SALT = "sb-dryrun-c31-sb2"
SB3_SEED_SALT = "sb-dryrun-c31-sb3"


def _sha_int(*parts: str) -> int:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\x00")
    return int.from_bytes(h.digest()[:8], "big", signed=False)


def _load_valset(manifest: Path) -> list[dict]:
    rows = []
    with manifest.open() as f:
        header = f.readline().rstrip("\n").split("\t")
        for ln in f:
            if not ln.strip():
                continue
            parts = ln.rstrip("\n").split("\t")
            rows.append(dict(zip(header, parts)))
    return rows


def _load_features(valset_rows: list[dict], features_dir: Path) -> tuple[list[str], list[str], np.ndarray, dict[str, str]]:
    """Load 55 valset feature vectors (PANNs 2048 + heur 4 = 2052-D).

    Returns (clip_ids_sorted, labels, X_matrix, sha_manifest).
    Iterates in sorted(clip_id) order for determinism.
    """
    keep_ids: list[str] = []
    keep_labels: list[str] = []
    vectors: list[np.ndarray] = []
    sha_manifest: dict[str, str] = {}
    # Sort by clip_id for deterministic iteration
    valset_rows = sorted(valset_rows, key=lambda r: r["clip_id"])
    for r in valset_rows:
        cid = r["clip_id"]
        p = features_dir / f"{cid}.npz"
        if not p.is_file():
            continue
        d = np.load(p, allow_pickle=False)
        if str(d.get("feature_version", "")) != FEATURE_VERSION:
            continue
        vec = np.concatenate([d["panns_embed"], d["heuristic_vec"]], axis=0).astype(np.float32)
        if vec.shape[0] != FEAT_DIM:
            continue
        keep_ids.append(cid)
        keep_labels.append(r.get("label", ""))
        vectors.append(vec)
        sha_manifest[cid] = hashlib.sha256(p.read_bytes()).hexdigest()
    if not vectors:
        raise RuntimeError("no valset features loaded")
    X = np.stack(vectors, axis=0)
    return keep_ids, keep_labels, X, sha_manifest


def _impute_nan(X: np.ndarray) -> np.ndarray:
    X = X.astype(np.float32).copy()
    col_mean = np.nanmean(X, axis=0)
    for j in range(X.shape[1]):
        m = np.isnan(X[:, j])
        X[m, j] = 0.0 if not np.isfinite(col_mean[j]) else col_mean[j]
    return X


def _strat_key(y: np.ndarray, n_splits: int) -> np.ndarray:
    from collections import Counter
    cnt = Counter(y.tolist())
    if any(v < n_splits for v in cnt.values()):
        return np.clip(np.round((y - 1) / 2), 0, 3).astype(int)
    return y.copy()


def _fit_predict_cv(X: np.ndarray, y: np.ndarray, seed: int, epochs: int, n_splits: int = 5) -> np.ndarray:
    """5-fold stratified CV; return per-clip out-of-fold predictions."""
    import torch
    from sklearn.model_selection import StratifiedKFold
    kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    strat = _strat_key(y, n_splits)
    oof = np.zeros(X.shape[0], dtype=np.int64)
    for fi, (tr_idx, te_idx) in enumerate(kf.split(X, strat)):
        set_determinism(seed + fi)
        model = CornHead(X.shape[1])
        opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WD)
        Xt = torch.from_numpy(X[tr_idx].astype(np.float32))
        yt = torch.from_numpy(y[tr_idx].astype(np.int64))
        Xe = torch.from_numpy(X[te_idx].astype(np.float32))
        model.train()
        for _ in range(epochs):
            opt.zero_grad()
            loss = corn_loss(model(Xt), yt, K)
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            pred = corn_predict(model(Xe)).numpy()
        oof[te_idx] = pred
    return oof


def _baselines_mae(y: np.ndarray) -> tuple[float, float]:
    """Return (majority_class_mae, mean_integer_mae) for the labels."""
    y_arr = np.asarray(y, dtype=np.int64)
    maj = int(np.bincount(y_arr, minlength=K + 1).argmax())
    majority_mae = float(np.mean(np.abs(maj - y_arr)))
    mn_int = int(round(float(np.mean(y_arr))))
    mean_integer_mae = float(np.mean(np.abs(mn_int - y_arr)))
    return majority_mae, mean_integer_mae


def _compute_sb1(X: np.ndarray, ids: list[str], epochs: int) -> dict:
    """SB1 methodology: MAE margin vs min(majority, mean-integer) baselines.

    Uses the SHA-256-salted synthetic-label recipe RECIPES[0] (hash-noise
    family salt 0). Any recipe works — dry-run asserts computability, not
    real-label PASS.
    """
    features_by_id = {cid: X[i] for i, cid in enumerate(ids)}
    label_map = apply_recipe(RECIPES[0], features_by_id)  # {cid: 1..7}
    y = np.array([label_map[c] for c in ids], dtype=np.int64)
    pred = _fit_predict_cv(_impute_nan(X), y, seed=0, epochs=epochs)
    mae_corn = float(np.mean(np.abs(pred - y)))
    maj_mae, mn_mae = _baselines_mae(y)
    baseline_hard = min(maj_mae, mn_mae)
    margin = baseline_hard - mae_corn
    return {
        "sb1_mae_corn": mae_corn,
        "majority_class_baseline_mae": maj_mae,
        "mean_integer_baseline_mae": mn_mae,
        "sb1_baseline_hard": baseline_hard,
        "sb1_margin": margin,
        "sb1_recipe_idx": 0,
        "sb1_recipe_salt": RECIPES[0]["salt"],
    }


def _stratified_bootstrap_indices(y: np.ndarray, resample_id: int, keep_frac: float) -> np.ndarray:
    """Deterministic SHA-256-salted stratified bootstrap.

    Within each rating class, sort clip-indices by (sha256(salt||resample_id||orig_idx))
    and keep the first ceil(n_class * keep_frac).
    """
    salt = SB2_SEED_SALT
    kept: list[int] = []
    for v in sorted(np.unique(y).tolist()):
        idxs = np.where(y == v)[0].tolist()
        ordered = sorted(idxs, key=lambda i: _sha_int(salt, str(resample_id), str(i)))
        n_keep = max(1, math.ceil(len(ordered) * keep_frac))
        kept.extend(ordered[:n_keep])
    return np.array(sorted(kept), dtype=np.int64)


def _compute_sb2(X: np.ndarray, ids: list[str], epochs: int) -> dict:
    """SB2 methodology: mean pairwise Kendall τ across 10 stratified
    bootstrap resamples. Uses RECIPES[2] (linear-projection, salt 2).
    Each resample fits a CORN head on the SHA-256-sampled subset and
    predicts on the full set; τ measured pairwise across the 10
    per-clip rank vectors.
    """
    features_by_id = {cid: X[i] for i, cid in enumerate(ids)}
    label_map = apply_recipe(RECIPES[2], features_by_id)
    y = np.array([label_map[c] for c in ids], dtype=np.int64)
    X_imp = _impute_nan(X)

    per_resample_predictions: list[np.ndarray] = []
    for r in range(N_BOOTSTRAP):
        keep = _stratified_bootstrap_indices(y, r, BOOTSTRAP_FRACTION)
        # Fit on the resampled subset via 5-fold CV; predict full set by
        # concatenating OOF on the subset and training a full-data head
        # for the held-out clips (simpler: fit on subset, predict on ALL
        # clips via a single model — the dry-run is about computability).
        import torch
        set_determinism(r)
        model = CornHead(X_imp.shape[1])
        opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WD)
        Xt = torch.from_numpy(X_imp[keep].astype(np.float32))
        yt = torch.from_numpy(y[keep].astype(np.int64))
        model.train()
        for _ in range(epochs):
            opt.zero_grad()
            loss = corn_loss(model(Xt), yt, K)
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            pred_all = corn_predict(model(torch.from_numpy(X_imp.astype(np.float32)))).numpy()
        per_resample_predictions.append(pred_all)

    # Pairwise τ across the 10 rank vectors — 45 pairs.
    pair_taus: list[float] = []
    for i in range(N_BOOTSTRAP):
        for j in range(i + 1, N_BOOTSTRAP):
            d = kendall_tau_exact(per_resample_predictions[i], per_resample_predictions[j])
            pair_taus.append(d["tau_b"])
    mean_tau = float(np.mean(pair_taus)) if pair_taus else float("nan")
    per_resample_tau_mean = [float(np.mean(
        [kendall_tau_exact(per_resample_predictions[i], per_resample_predictions[j])["tau_b"]
         for j in range(N_BOOTSTRAP) if j != i])) for i in range(N_BOOTSTRAP)]
    return {
        "sb2_mean_tau": mean_tau,
        "sb2_per_resample_tau": per_resample_tau_mean,  # length 10 (mean τ vs the other 9)
        "sb2_pairwise_tau_count": len(pair_taus),
        "sb2_bootstrap_fraction": BOOTSTRAP_FRACTION,
        "sb2_recipe_idx": 2,
        "sb2_recipe_salt": RECIPES[2]["salt"],
    }


def _compute_sb3(X: np.ndarray, ids: list[str], labels: list[str]) -> dict:
    """SB3 methodology: leak-test detection rate at α=1.0 for artist,
    genre, era. Reuses c6 leak_test.run_experiments with reduced controls
    (n_controls=4) to bound wall time; the dry-run only asserts detection
    rate is computable and finite in [0,1].
    """
    from scripts.ear.leak_test import run_experiments
    X_imp = _impute_nan(X)
    # SHA-salted base_seed for determinism across two dry-runs (numpy default_rng
    # inside run_experiments is used only for label synthesis; base_seed is fixed).
    base_seed = _sha_int(SB3_SEED_SALT, "base") % (2**31)
    result = run_experiments(
        X_imp, list(ids), list(labels),
        alphas=(LEAK_ALPHA,),
        n_controls=4,           # bounded wall-time; smaller than c6's 20
        n_splits=3,             # bounded wall-time; smaller than c6's 5
        epochs=20,              # bounded wall-time; smaller than c6's 60
        base_seed=base_seed,
    )
    per_leak = {}
    for k in ("artist", "genre", "era"):
        rate = result["summary_detection"].get(f"{k}@alpha={float(LEAK_ALPHA)}", float("nan"))
        per_leak[k] = float(rate)
    return {
        "sb3_detection_rate_per_leak_type": per_leak,
        "sb3_alpha": LEAK_ALPHA,
        "sb3_tau_per_leak_type": {k: float(v) for k, v in result["tau_per_leak_type"].items()},
        "sb3_config": {
            "n_controls": 4,
            "n_splits": 3,
            "epochs": 20,
            "base_seed": base_seed,
        },
    }


def run_dry_run(valset_manifest: Path, features_dir: Path, out_dir: Path,
                epochs: int = 40) -> dict:
    valset_rows = _load_valset(valset_manifest)
    ids, labels, X, sha_manifest = _load_features(valset_rows, features_dir)
    print(f"[sb-dry-run] loaded {len(ids)} clips, feat_dim={X.shape[1]}")

    sb1 = _compute_sb1(X, ids, epochs=epochs)
    print(f"[sb-dry-run] SB1 margin = {sb1['sb1_margin']:.6f}")

    sb2 = _compute_sb2(X, ids, epochs=epochs)
    print(f"[sb-dry-run] SB2 mean τ = {sb2['sb2_mean_tau']:.6f}")

    sb3 = _compute_sb3(X, ids, labels)
    print(f"[sb-dry-run] SB3 detection = {sb3['sb3_detection_rate_per_leak_type']}")

    # Rubric hash embed.
    rubric_hash = hashlib.sha256(RUBRIC_PATH.read_bytes()).hexdigest() \
        if RUBRIC_PATH.is_file() else ""

    # Verdict per rubric §FIXTURE_READY item 4.
    def _finite(v):
        return isinstance(v, (int, float)) and math.isfinite(float(v))

    sb1_ok = _finite(sb1["sb1_margin"]) and _finite(sb1["majority_class_baseline_mae"]) \
        and _finite(sb1["mean_integer_baseline_mae"])
    sb2_ok = _finite(sb2["sb2_mean_tau"]) and isinstance(sb2["sb2_per_resample_tau"], list) \
        and len(sb2["sb2_per_resample_tau"]) == 10 \
        and all(_finite(x) for x in sb2["sb2_per_resample_tau"])
    sb3_ok = all(k in sb3["sb3_detection_rate_per_leak_type"]
                 for k in ("artist", "genre", "era")) \
        and all(_finite(sb3["sb3_detection_rate_per_leak_type"][k]) and
                0.0 <= sb3["sb3_detection_rate_per_leak_type"][k] <= 1.0
                for k in ("artist", "genre", "era"))

    dry_run_computable = sb1_ok and sb2_ok and sb3_ok
    verdict = "FIXTURE_READY" if dry_run_computable else "FIXTURE_INSUFFICIENT"

    # Aggregate manifest SHA (SHA-256 of concat of sorted (cid,sha) pairs).
    manifest_agg = hashlib.sha256(
        json.dumps(sha_manifest, sort_keys=True).encode("utf-8")
    ).hexdigest()

    out = {
        "cycle": 31,
        "run_id": "run-2026-08-28T040704Z",
        "milestone": "M-EAR-1/armed-harness-fixture-reinforcement",
        "rubric_hash": rubric_hash,
        "verdict": verdict,
        "dry_run_computable": dry_run_computable,
        "sb1_ok": sb1_ok,
        "sb2_ok": sb2_ok,
        "sb3_ok": sb3_ok,
        "n_clips": int(X.shape[0]),
        "feature_version": FEATURE_VERSION,
        "feature_cache_agg_sha256": manifest_agg,
        "feature_cache_sha_manifest": sha_manifest,
        "alpha_pinned_c26": 0.7469387071101908,
        "epochs": epochs,
        **sb1,
        **sb2,
        **sb3,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "sb_dry_run_verdict.json"
    # Deterministic JSON: sort_keys, indent=2, trailing newline.
    dst.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"[sb-dry-run] wrote {dst}")
    print(f"[sb-dry-run] verdict = {verdict}")
    return out


def _main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--valset-manifest", type=Path, default=DEFAULT_VALSET)
    ap.add_argument("--features-dir", type=Path, default=DEFAULT_FEATURES)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--epochs", type=int, default=40)
    args = ap.parse_args(argv)
    run_dry_run(args.valset_manifest, args.features_dir, args.out_dir, args.epochs)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
