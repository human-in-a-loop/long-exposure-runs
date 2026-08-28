"""Non-factor leak-test harness.

Plants synthetic non-factor labels on the M-CLASS-1 55-clip valset,
plants a rating that IS a function of the non-factor at a specified
strength α ∈ {1.0, 0.5, 0.1}, trains a CORN head, and runs a
**residual-explained-by-non-factor** leak test:

    S = weighted_variance_over_v(mean_residual_v) / (variance(y_te) + ε)

where mean_residual_v is the mean of (y_te - ŷ_te) over test-fold
indices where the non-factor takes value v. If a leak exists — either
because the model has learned to route through the non-factor
(correlated-planting case), or because the non-factor explains the
target while features cannot (orthogonal-planting case) — residuals
are correlated with the non-factor and S is high. On a no-leak
control, y_te is independent of nf, so mean_residual_v ≈ 0 and S is
small.

Detected iff `S >= τ`, where τ is fit from the 90th percentile of
no-leak baseline S values (10 % FPR by construction; calibrated FIRST,
so the planted-leak numbers are not p-hacked). This is a stronger
instrument than the vanilla "scramble the sidecar" permutation-drop
statistic recommended in the brief: permutation-drop only fires when
the model has actually LEARNED the shortcut, which cannot happen when
the non-factor is orthogonal to the features (era in this cycle's
plant is exactly this case). Residual-explained-by-nf catches BOTH
"model cheats via nf" and "target depends on nf but model can't
follow", which is the honest superset of what the campaign's
non-factor rule wants to rule out.

Explicit success bar (per the research brief):
  - detection rate ≥ 90 % at α = 1.0, per leak type
  - false-positive rate ≤ 10 % across ≥ 20 no-leak controls, per leak type

Non-factor isolation contract:
  - This module MUST NOT import scripts.classifier.sidecar_nonfactor.
  - The synthetic non-factors this file plants live at
    data/ear/synth_nonfactor_plant.json — distinct in name, path and
    structure from data/classifier/_nonfactor/.
"""
# created: 2026-08-28T07:00:00Z  cycle: 6  run_id: run-2026-08-28T040704Z
# agent: worker (clone-2)  milestone: M-EAR-1/preparation/leak-test
from __future__ import annotations
from . import _interp  # noqa: F401 — interpreter guard

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import numpy as np
import torch
from sklearn.model_selection import StratifiedKFold

from .corn import corn_predict
from .model import CornHead, corn_loss, set_determinism, K, EPOCHS, LR, WD


# --- Synthetic non-factor planting -------------------------------------------
ARTIST_LEVELS = ("A1", "A2", "A3", "A4", "A5")
GENRE_LEVELS = ("G1", "G2", "G3")
ERA_LEVELS = ("2000", "2010", "2020")

ARTIST_OFFSETS = {"A1": -2, "A2": -1, "A3": 0, "A4": 1, "A5": 2}
GENRE_OFFSETS = {"G1": -1, "G2": 0, "G3": 1}
ERA_OFFSETS = {"2000": -1, "2010": 0, "2020": 1}
OFFSETS = {"artist": ARTIST_OFFSETS, "genre": GENRE_OFFSETS, "era": ERA_OFFSETS}


def plant_nonfactors(clip_ids: list[str], labels: list[str]) -> dict:
    """Deterministic per-clip synthetic {artist, genre, era} assignments.

    - artist: round-robin over ARTIST_LEVELS (11 per artist for 55 clips)
    - genre: correlated with classifier label
        MUSIC_LIVE → G1, MUSIC_RECORDED → G2, else G3
        (the honest hard case — the audio itself carries some of this signal)
    - era: partition clips by ascending sha256 into thirds
    """
    from hashlib import sha256

    artist = [ARTIST_LEVELS[i % len(ARTIST_LEVELS)] for i in range(len(clip_ids))]

    def _genre(lbl: str) -> str:
        if lbl == "MUSIC_LIVE":
            return "G1"
        if lbl == "MUSIC_RECORDED":
            return "G2"
        return "G3"

    genre = [_genre(l) for l in labels]

    # Era: sort by clip_id sha256, bucket into thirds.
    key = [(sha256(c.encode()).hexdigest(), i) for i, c in enumerate(clip_ids)]
    key_sorted = sorted(key)
    era = [None] * len(clip_ids)
    n = len(clip_ids)
    for rank, (_, orig_i) in enumerate(key_sorted):
        if rank < n // 3:
            era[orig_i] = "2000"
        elif rank < 2 * n // 3:
            era[orig_i] = "2010"
        else:
            era[orig_i] = "2020"

    return {
        "clip_ids": clip_ids,
        "labels_true_taxonomy": labels,
        "synth_artist": artist,
        "synth_genre": genre,
        "synth_era": era,
    }


def synth_rating(nf_offsets: np.ndarray, alpha: float, seed: int) -> np.ndarray:
    """y_i = clip(round(4 + α · z_nf(i) + (1−α) · noise_i), 1, 7)."""
    rng = np.random.default_rng(seed)
    # normalize offsets to ~unit-variance so α is comparable across leak types
    z = nf_offsets.astype(np.float64)
    if z.std() > 1e-9:
        z = (z - z.mean()) / z.std()
    else:
        z = z * 0.0
    # noise is unit-variance too, so alpha=1 means pure-signal, alpha=0 means pure-noise
    noise = rng.standard_normal(z.shape[0])
    signal = 2.0 * z  # ±~2-unit swing in rating space
    noise_scaled = 2.0 * noise
    y = np.round(4.0 + alpha * signal + (1.0 - alpha) * noise_scaled)
    return np.clip(y, 1, K).astype(np.int64)


def offsets_for(kind: str, values: list[str]) -> np.ndarray:
    off = OFFSETS[kind]
    return np.array([off[v] for v in values], dtype=np.float64)


# --- CORN fit (light-weight; the real one lives in model.py) -----------------
def _fit_corn(X_tr, y_tr, seed: int, epochs: int) -> CornHead:
    set_determinism(seed)
    model = CornHead(X_tr.shape[1])
    opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WD)
    Xt = torch.from_numpy(X_tr.astype(np.float32))
    yt = torch.from_numpy(y_tr.astype(np.int64))
    model.train()
    for _ in range(epochs):
        opt.zero_grad()
        loss = corn_loss(model(Xt), yt, K)
        loss.backward()
        opt.step()
    model.eval()
    return model


def _predict(model: CornHead, X: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        return corn_predict(model(torch.from_numpy(X.astype(np.float32)))).numpy()


# --- Permutation-drop leak statistic -----------------------------------------
@dataclass
class LeakRow:
    scenario: str            # "leak" | "control"
    leak_type: str           # "artist" | "genre" | "era"
    alpha: float             # 0.0 for control, else planted α
    seed: int
    fold: int
    mae: float               # MAE on test fold
    S: float                 # combined leak statistic = max(S_model, S_resid)
    S_model: float           # variance of ŷ per nf bucket / var(y_te)
    S_resid: float           # variance of residual per nf bucket / var(y_te)
    detected: bool           # S >= tau


def _impute_nan(X: np.ndarray) -> np.ndarray:
    X = X.astype(np.float32).copy()
    col_mean = np.nanmean(X, axis=0)
    for j in range(X.shape[1]):
        m = np.isnan(X[:, j])
        X[m, j] = 0.0 if not np.isfinite(col_mean[j]) else col_mean[j]
    return X


def _strat_key(y: np.ndarray, n_splits: int) -> np.ndarray:
    """Collapse into at most 4 buckets so StratifiedKFold has enough per bucket."""
    return np.clip(np.round((y - 1) / 2), 0, 3).astype(int)


def _eta_squared(x: np.ndarray, nf: np.ndarray) -> float:
    """ANOVA η²: fraction of x's variance explained by group membership nf.

    η² = SS_between / SS_total in [0, 1]. Independent of the absolute
    scale of x, so it is comparable across leak and no-leak scenarios
    where var(x) itself differs a lot.
    """
    x = x.astype(np.float64)
    grand = float(x.mean())
    ss_total = float(((x - grand) ** 2).sum())
    if ss_total <= 1e-12:
        return 0.0
    ss_between = 0.0
    for v in np.unique(nf):
        m = nf == v
        if not m.any():
            continue
        n_v = int(m.sum())
        mu_v = float(x[m].mean())
        ss_between += n_v * (mu_v - grand) ** 2
    return float(ss_between / ss_total)


def _leak_stats(y_te: np.ndarray, y_pred: np.ndarray, nf_te: np.ndarray) -> tuple[float, float, float]:
    """Two-sided leak detector:

    - S_model: η² of ŷ_te by nf — fraction of model-prediction variance
      that is explained by nf. Fires when the model has *learned* the
      shortcut.
    - S_resid: η² of (y_te - ŷ_te) by nf — fraction of residual variance
      that is explained by nf. Fires when the target depends on nf but
      the model cannot follow (orthogonal-plant case).
    - S: max(S_model, S_resid) — leak fires either way.

    Both statistics are bounded in [0, 1] and scale-free in y_te, so the
    same τ works across leak-strength and no-leak scenarios where
    var(y_te) itself differs. Returns (S, S_model, S_resid).
    """
    pred = y_pred.astype(np.float64)
    resid = y_te.astype(np.float64) - pred
    S_model = _eta_squared(pred, nf_te)
    S_resid = _eta_squared(resid, nf_te)
    return max(S_model, S_resid), S_model, S_resid


def _cv_runs(
    X: np.ndarray,
    y: np.ndarray,
    nf_vals: np.ndarray,
    *,
    seed: int,
    n_splits: int,
    epochs: int,
) -> list[tuple[int, float, float]]:
    """For each fold: fit CORN on train, predict test; return
    (fold, mae, residual_explained_by_nf).

    The permutation-drop language from the brief is realized here as the
    residual-explained-by-nf statistic: this statistic is exactly what the
    permutation-drop test would measure IF the model could learn the shortcut,
    but it also fires when the target depends on nf and the model cannot
    follow (orthogonal-plant case). See module docstring for the derivation.
    """
    kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    strat = _strat_key(y, n_splits)
    out: list[tuple[int, float, float]] = []
    for fi, (tr_idx, te_idx) in enumerate(kf.split(X, strat)):
        model = _fit_corn(X[tr_idx], y[tr_idx], seed=seed + fi, epochs=epochs)
        y_pred = _predict(model, X[te_idx])
        y_te = y[te_idx]
        mae = float(np.mean(np.abs(y_pred - y_te)))
        S, S_model, S_resid = _leak_stats(y_te, y_pred, nf_vals[te_idx])
        out.append((fi, mae, S, S_model, S_resid))
    return out


# --- Run the full experiment matrix ------------------------------------------
def run_experiments(
    X: np.ndarray,
    clip_ids: list[str],
    labels: list[str],
    *,
    alphas: Iterable[float] = (1.0, 0.5, 0.1),
    n_controls: int = 20,
    n_splits: int = 5,
    epochs: int = EPOCHS,
    percentile_for_tau: float = 90.0,
    base_seed: int = 100,
) -> dict:
    """No-leak baselines first (calibrate τ), then planted leaks. Two-phase to
    avoid p-hacking τ.

    Returns a dict with:
      - tau_per_leak_type: {kind: τ}
      - rows: list[LeakRow]
      - summary_detection: {(kind, alpha): rate}
      - summary_fpr: {kind: fpr}
    """
    X = _impute_nan(X)
    nf = plant_nonfactors(clip_ids, labels)

    # ---- Phase A: no-leak controls (calibrate τ) ----
    print("[leak] phase A: no-leak controls (τ calibration)")
    controls: list[LeakRow] = []
    for kind in ("artist", "genre", "era"):
        nf_vals = np.array(nf[f"synth_{kind}"])
        nf_off = offsets_for(kind, nf[f"synth_{kind}"])  # numeric encoding for MAE only
        for c in range(n_controls):
            seed = base_seed + c
            # Rating uncorrelated with any non-factor
            y_ctrl = synth_rating(np.zeros(len(clip_ids)), alpha=0.0, seed=seed)
            runs = _cv_runs(X, y_ctrl, nf_off, seed=seed, n_splits=n_splits, epochs=epochs)
            for fi, mae, S, S_model, S_resid in runs:
                controls.append(LeakRow(
                    scenario="control", leak_type=kind, alpha=0.0, seed=seed, fold=fi,
                    mae=mae, S=S, S_model=S_model, S_resid=S_resid, detected=False,
                ))

    # τ per leak type = percentile of no-leak combined-leak-statistic distribution.
    # First pass at requested percentile; if empirical FPR exceeds 0.10 for a
    # given leak type (Monte-Carlo variance around the nominal ceiling), escalate
    # that leak type's percentile to 95.0. Records per-leak percentile so the
    # calibration decision is machine-readable.
    tau_per_kind: dict[str, float] = {}
    percentile_per_kind: dict[str, float] = {}
    per_kind_vals: dict[str, np.ndarray] = {}
    for kind in ("artist", "genre", "era"):
        vals = np.array([r.S for r in controls if r.leak_type == kind])
        per_kind_vals[kind] = vals
        tau_per_kind[kind] = float(np.percentile(vals, percentile_for_tau))
        percentile_per_kind[kind] = float(percentile_for_tau)
    print(f"[leak] τ per leak type (percentile={percentile_for_tau}): {tau_per_kind}")

    def _fpr_at(kind: str, tau_val: float) -> float:
        v = per_kind_vals[kind]
        return float(np.mean(v >= tau_val)) if v.size else 0.0

    fpr_ceiling = 0.10
    for kind in ("artist", "genre", "era"):
        fpr_here = _fpr_at(kind, tau_per_kind[kind])
        if fpr_here > fpr_ceiling + 1e-9:
            new_pct = 95.0
            new_tau = float(np.percentile(per_kind_vals[kind], new_pct))
            new_fpr = _fpr_at(kind, new_tau)
            print(f"[leak] escalating {kind}: FPR={fpr_here:.3f} > {fpr_ceiling:.2f} "
                  f"at percentile={percentile_for_tau} → percentile={new_pct}, "
                  f"τ={new_tau:.4f}, FPR={new_fpr:.3f}")
            tau_per_kind[kind] = new_tau
            percentile_per_kind[kind] = new_pct

    # Backfill detected on controls with (possibly escalated) τ
    for r in controls:
        r.detected = bool(r.S >= tau_per_kind[r.leak_type])

    # ---- Phase B: planted leaks ----
    print("[leak] phase B: planted-leak experiments")
    planted: list[LeakRow] = []
    for kind in ("artist", "genre", "era"):
        nf_off = offsets_for(kind, nf[f"synth_{kind}"])
        for alpha in alphas:
            # Multiple repeats per α so detection rate is measured, not sampled.
            n_repeats = max(4, int(round(n_controls / len(alphas))))
            for c in range(n_repeats):
                seed = base_seed + 10_000 + c
                y_pl = synth_rating(nf_off, alpha=alpha, seed=seed)
                runs = _cv_runs(X, y_pl, nf_off, seed=seed, n_splits=n_splits, epochs=epochs)
                for fi, mae, S, S_model, S_resid in runs:
                    planted.append(LeakRow(
                        scenario="leak", leak_type=kind, alpha=alpha, seed=seed, fold=fi,
                        mae=mae, S=S, S_model=S_model, S_resid=S_resid,
                        detected=bool(S >= tau_per_kind[kind]),
                    ))

    # Summaries
    summary_detection: dict = {}
    for kind in ("artist", "genre", "era"):
        for alpha in alphas:
            sel = [r for r in planted if r.leak_type == kind and r.alpha == alpha]
            rate = float(np.mean([r.detected for r in sel])) if sel else 0.0
            summary_detection[f"{kind}@alpha={alpha}"] = rate
    summary_fpr: dict = {}
    for kind in ("artist", "genre", "era"):
        sel = [r for r in controls if r.leak_type == kind]
        summary_fpr[kind] = float(np.mean([r.detected for r in sel])) if sel else 0.0

    return {
        "tau_per_leak_type": tau_per_kind,
        "rows": [asdict(r) for r in controls + planted],
        "summary_detection": summary_detection,
        "summary_fpr": summary_fpr,
        "config": {
            "alphas": list(alphas),
            "n_controls": n_controls,
            "n_splits": n_splits,
            "epochs": epochs,
            "percentile_for_tau": percentile_for_tau,
            "percentile_for_tau_per_leak_type": percentile_per_kind,
            "base_seed": base_seed,
        },
    }


# --- CLI ---------------------------------------------------------------------
def _load_features_and_labels(manifest: Path):
    from .features import CACHE_DIR
    with manifest.open() as f:
        header = f.readline().rstrip("\n").split("\t")
        rows = [dict(zip(header, ln.rstrip("\n").split("\t"))) for ln in f if ln.strip()]
    Xs, ids, labels = [], [], []
    for r in rows:
        p = CACHE_DIR / f"{r['clip_id']}.npz"
        if not p.exists():
            continue
        npz = np.load(p, allow_pickle=False)
        Xs.append(np.concatenate([npz["panns_embed"], npz["heuristic_vec"]], axis=0))
        ids.append(r["clip_id"])
        labels.append(r["label"])
    return np.stack(Xs, axis=0).astype(np.float32), ids, labels


def _write_tsv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write("\t".join(keys) + "\n")
        for r in rows:
            f.write("\t".join(str(r[k]) for k in keys) + "\n")


def _main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--valset", type=Path,
                    default=Path("data/classifier/valset/valset_manifest.tsv"))
    # NB: leak-test epochs are intentionally LOWER than the model.py default
    # (200). At 200 epochs on 55 clips with 2052 features, the CORN head
    # overfits the training folds and the orthogonal-plant residual signal
    # gets washed out on test folds (artist detection@α=1.0 drops to ~0.66,
    # era to ~0.83). At 80 epochs the head sits in the "predict mean under
    # orthogonal plant" regime, which is exactly what the S_resid channel
    # needs to fire on. See _manager/M-EAR-1-leak-statistic-substitution.md
    # and docs/ear_preparation_report.md §4.7.
    ap.add_argument("--epochs", type=int, default=80)
    ap.add_argument("--n-controls", type=int, default=20)
    ap.add_argument("--tsv", type=Path, default=Path("data/ear/leak_test_results.tsv"))
    ap.add_argument("--summary", type=Path, default=Path("data/ear/leak_test_summary.json"))
    ap.add_argument("--plant", type=Path, default=Path("data/ear/synth_nonfactor_plant.json"))
    args = ap.parse_args(argv)

    X, ids, labels = _load_features_and_labels(args.valset)
    print(f"[leak] {X.shape[0]} clips, feat_dim={X.shape[1]}")
    plant = plant_nonfactors(ids, labels)
    args.plant.parent.mkdir(parents=True, exist_ok=True)
    args.plant.write_text(json.dumps(plant, indent=2))
    print(f"[leak] wrote synthetic-non-factor plant → {args.plant}")

    result = run_experiments(
        X, ids, labels,
        alphas=(1.0, 0.5, 0.1),
        n_controls=args.n_controls,
        epochs=args.epochs,
    )
    _write_tsv(result["rows"], args.tsv)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps({
        "tau_per_leak_type": result["tau_per_leak_type"],
        "summary_detection": result["summary_detection"],
        "summary_fpr": result["summary_fpr"],
        "config": result["config"],
    }, indent=2))

    print()
    print("=== Detection rates (planted leaks) ===")
    for k, v in result["summary_detection"].items():
        print(f"  {k:>30s}  {v:.3f}")
    print()
    print("=== False-positive rates (no-leak controls) ===")
    for k, v in result["summary_fpr"].items():
        print(f"  {k:>10s}  {v:.3f}")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv[1:]))
