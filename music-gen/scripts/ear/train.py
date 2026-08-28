"""M-EAR-1 training loop (armed-not-fired chassis).

Contract:
    train(features_dir: Path,
          ratings_manifest: Path,
          out_dir: Path,
          seed: int = 0) -> TrainingResult

Semantics:
    1. Load feature vectors from `features_dir/*.npz` (M-EAR-1/preparation
       cache; each file carries `feature_version`, `source_wav_sha256`,
       `panns_embed` (2048,), `heuristic_vec` (4,); vggish optional).
    2. Load ratings from `ratings_manifest` (TSV, columns include `rating`).
       Join by clip identifier.

       Two join modes:
         (a) "audio-sha256" mode — the manifest carries an `audio_sha256`
             column. Rows are joined to cached features whose
             `source_wav_sha256` matches. This is the target mode for
             real rated audio (audio-side sha256 is the ingest chunker's
             chunk-sha256 for rated songs). Used once audio arrives.
         (b) "clip-id fallback" mode — the manifest carries `clip_id` or
             `video_id` (used for the M-CLASS-1 55-clip synth-label
             valset which does not have a per-song sha256 in the ratings
             manifest). Rows are joined to features by filename stem.
       Missing rows on either side are dropped; the resulting `n_clips`
       is recorded.
    3. 5-fold stratified CV split on the (integer 1..7) rating.
    4. Per fold: instantiate a fresh CORN head
       (Linear(2052,128) → ReLU → Dropout(0.3) → Linear(128,6)),
       train with BCE-with-logits loss (via corn_loss), Adam optimizer,
       `torch.manual_seed(seed+fi)`, single-thread BLAS pins.
    5. Evaluate MAE on the held-out fold.
    6. Emit training_result.json with the seven required keys plus
       per-fold detail.
    7. Persist best-fold checkpoint to out_dir/corn_head_v1.pt.

Determinism:
    - `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1` pinned
      before torch import.
    - `torch.set_num_threads(1)`, `torch.manual_seed(seed+fi)` per fold.
    - Adam optimizer instantiated fresh per fold (no state carry-over).
    - Checkpoint saved via `torch.save` with `_use_new_zipfile_serialization=True`;
      keys sorted (state_dict is ordered by module registration).

Zero live network. Zero sidecar_nonfactor imports.
"""
# created: 2026-08-28T11:00:00Z  cycle: 11  run_id: run-2026-08-28T040704Z
# agent: worker (clone-2)  milestone: M-EAR-1/training-loop
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import os
# BLAS thread pins MUST come before numpy/torch import.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

import argparse
import hashlib
import json
import random
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import StratifiedKFold

from scripts.ear.corn import corn_loss, corn_predict
from scripts.ear.features import FEATURE_VERSION

K = 7  # ordinal classes 1..7
EPOCHS = 200
LR = 1e-3
WD = 1e-3
HIDDEN = 128
DROPOUT = 0.3
FEAT_DIM = 2052  # 2048 (PANNs Cnn14 penultimate) + 4 (mess-scale heuristics)


class CornHead(nn.Module):
    """Cycle-6 M-EAR-1/preparation/model architecture, pinned.

    Linear(2052,128) -> ReLU -> Dropout(0.3) -> Linear(128,6).
    """

    def __init__(self, feat_dim: int = FEAT_DIM, hidden: int = HIDDEN,
                 dropout: float = DROPOUT):
        super().__init__()
        self.body = nn.Sequential(
            nn.Linear(feat_dim, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, K - 1),
        )

    def forward(self, x):
        return self.body(x)


def _set_determinism(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(1)


@dataclass
class TrainingResult:
    mean_mae: float
    per_fold_mae: list
    majority_class_mae: float
    mean_integer_mae: float
    checkpoint_path: str
    training_config: dict
    feature_version: str
    n_clips: int
    calibration: str
    per_fold_detail: list = field(default_factory=list)


# ----------------------------- I/O ------------------------------------


def _iter_ratings(manifest: Path) -> list:
    """Return list of dicts (one per row) with `rating` int and any other
    join columns present."""
    rows = []
    with manifest.open() as f:
        header = f.readline().rstrip("\n").split("\t")
        for ln in f:
            if not ln.strip():
                continue
            parts = ln.rstrip("\n").split("\t")
            row = dict(zip(header, parts))
            try:
                row["rating"] = int(row["rating"])
            except (KeyError, ValueError):
                continue
            rows.append(row)
    return rows


def _load_feature_npz(path: Path) -> Optional[np.ndarray]:
    try:
        d = np.load(path, allow_pickle=False)
    except Exception:
        return None
    if str(d.get("feature_version", "")) != FEATURE_VERSION:
        return None
    panns = d["panns_embed"]
    heur = d["heuristic_vec"]
    vec = np.concatenate([panns, heur], axis=0).astype(np.float32)
    if vec.shape[0] != FEAT_DIM:
        return None
    return vec


def _index_features_by_sha(features_dir: Path) -> dict:
    """Return {source_wav_sha256: (clip_id, vec)}."""
    out = {}
    for p in sorted(features_dir.glob("*.npz")):
        try:
            d = np.load(p, allow_pickle=False)
        except Exception:
            continue
        sha = str(d.get("source_wav_sha256", ""))
        if not sha:
            continue
        vec = _load_feature_npz(p)
        if vec is None:
            continue
        out[sha] = (p.stem, vec)
    return out


def _index_features_by_clip_id(features_dir: Path) -> dict:
    out = {}
    for p in sorted(features_dir.glob("*.npz")):
        vec = _load_feature_npz(p)
        if vec is None:
            continue
        out[p.stem] = vec
    return out


def _join(features_dir: Path, ratings_manifest: Path) -> tuple:
    """Return (X, y, ids, join_mode)."""
    rows = _iter_ratings(ratings_manifest)
    if not rows:
        return np.zeros((0, FEAT_DIM), dtype=np.float32), np.zeros((0,), dtype=np.int64), [], "none"

    header = set(rows[0].keys())
    if "audio_sha256" in header:
        idx = _index_features_by_sha(features_dir)
        X, y, ids = [], [], []
        for r in rows:
            hit = idx.get(r["audio_sha256"])
            if hit is None:
                continue
            cid, vec = hit
            X.append(vec)
            y.append(r["rating"])
            ids.append(cid)
        mode = "audio-sha256"
    else:
        # Fallback: clip_id column (M-CLASS-1 valset).
        # If no clip_id column, use video_id (rated playlists — no local
        # audio, so this join returns 0 rows and TRAINING legitimately
        # fails "audio_missing" upstream).
        key_col = "clip_id" if "clip_id" in header else (
            "video_id" if "video_id" in header else None)
        if key_col is None:
            return np.zeros((0, FEAT_DIM), dtype=np.float32), np.zeros((0,), dtype=np.int64), [], "no-join-key"
        idx = _index_features_by_clip_id(features_dir)
        X, y, ids = [], [], []
        for r in rows:
            vec = idx.get(r[key_col])
            if vec is None:
                continue
            X.append(vec)
            y.append(r["rating"])
            ids.append(r[key_col])
        mode = f"clip-id[{key_col}]"

    if not X:
        return np.zeros((0, FEAT_DIM), dtype=np.float32), np.zeros((0,), dtype=np.int64), [], mode
    return (np.stack(X, axis=0).astype(np.float32),
            np.asarray(y, dtype=np.int64),
            ids, mode)


# ---------------------------- training --------------------------------


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
        # 4 buckets ~ (1-2), (3-4), (5-6), (7)
        return np.clip(np.round((y - 1) / 2), 0, 3).astype(int)
    return y.copy()


def _fit_fold(X_tr, y_tr, X_te, seed: int, epochs: int) -> tuple:
    _set_determinism(seed)
    model = CornHead(X_tr.shape[1])
    opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WD)  # fresh per fold
    Xt = torch.from_numpy(X_tr.astype(np.float32))
    yt = torch.from_numpy(y_tr.astype(np.int64))
    Xe = torch.from_numpy(X_te.astype(np.float32))
    model.train()
    losses = []
    for _ in range(epochs):
        opt.zero_grad()
        logits = model(Xt)
        loss = corn_loss(logits, yt, K)
        loss.backward()
        opt.step()
        losses.append(float(loss.detach().item()))
    model.eval()
    with torch.no_grad():
        logits_te = model(Xe)
        pred = corn_predict(logits_te).numpy()
    final_loss = losses[-1] if losses else float("nan")
    return model, pred, final_loss


def train(features_dir: Path,
          ratings_manifest: Path,
          out_dir: Path,
          seed: int = 0,
          epochs: int = EPOCHS,
          calibration: str = "synthetic_labels_only",
          synthesize_labels: bool = False) -> TrainingResult:
    """Main training entry.

    Args:
        features_dir: Directory containing cached feature .npz files.
        ratings_manifest: TSV file with a `rating` column plus a join key.
        out_dir: Output directory. Written: training_result.json, corn_head_v1.pt.
        seed: Base seed. Per-fold seed = seed + fold_index.
        epochs: Number of Adam epochs per fold.
        calibration: "synthetic_labels_only" or "user_ratings" — passed
            through to training_result.json.
        synthesize_labels: If True, ignore the `rating` column and
            synthesize labels from the feature-space 1-PC (used to
            proof-of-life the loop on the M-CLASS-1 55-clip valset which
            has no ratings).

    Returns:
        TrainingResult dataclass; also written to out_dir/training_result.json.

    Raises:
        ValueError: on NaN loss or empty join.
    """
    _set_determinism(seed)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    X, y, ids, join_mode = _join(Path(features_dir), Path(ratings_manifest))
    if X.shape[0] == 0:
        raise ValueError(
            f"train: no clips joined between features_dir={features_dir} "
            f"and ratings_manifest={ratings_manifest} (join_mode={join_mode})"
        )
    if synthesize_labels:
        y = _synth_labels_from_features(X, seed=seed)

    X = _impute_nan(X)

    n_splits = 5
    kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    strat_key = _strat_key(y, n_splits)

    per_fold_mae = []
    per_fold_detail = []
    best_mae = float("inf")
    best_model = None
    best_fold = -1

    for fi, (tr_idx, te_idx) in enumerate(kf.split(X, strat_key)):
        X_tr, y_tr = X[tr_idx], y[tr_idx]
        X_te, y_te = X[te_idx], y[te_idx]
        model, pred, final_loss = _fit_fold(X_tr, y_tr, X_te, seed=seed + fi, epochs=epochs)
        if not np.isfinite(final_loss):
            raise ValueError(f"train: NaN loss in fold {fi}")
        mae = float(np.mean(np.abs(pred - y_te)))
        per_fold_mae.append(mae)
        per_fold_detail.append({
            "fold": fi,
            "mae": mae,
            "n_train": int(X_tr.shape[0]),
            "n_test": int(X_te.shape[0]),
            "final_loss": final_loss,
            "seed": int(seed + fi),
        })
        if mae < best_mae:
            best_mae = mae
            best_model = model
            best_fold = fi

    # Baselines: single-integer prediction across the whole set.
    y_arr = np.asarray(y, dtype=np.int64)
    maj = int(np.bincount(y_arr, minlength=K + 1).argmax())
    majority_mae = float(np.mean(np.abs(maj - y_arr)))
    mn_int = int(round(float(np.mean(y_arr))))
    mean_integer_mae = float(np.mean(np.abs(mn_int - y_arr)))

    # Persist best-fold checkpoint deterministically.
    ckpt_path = out_dir / "corn_head_v1.pt"
    _save_checkpoint_deterministic(best_model, ckpt_path, best_fold, seed)

    # `checkpoint_path` in training_result.json is stored as the basename
    # so the JSON is byte-deterministic across runs whose out_dir differs
    # by tmpdir. Callers resolve to a full path via `out_dir / basename`.
    result = TrainingResult(
        mean_mae=float(np.mean(per_fold_mae)),
        per_fold_mae=[float(x) for x in per_fold_mae],
        majority_class_mae=majority_mae,
        mean_integer_mae=mean_integer_mae,
        checkpoint_path=ckpt_path.name,
        training_config={
            "arch": "Linear(2052,128)->ReLU->Dropout(0.3)->Linear(128,6)",
            "loss": "BCEWithLogitsLoss (corn_loss)",
            "optimizer": "Adam",
            "lr": LR,
            "weight_decay": WD,
            "epochs": epochs,
            "n_splits": n_splits,
            "K": K,
            "seed": seed,
            "join_mode": join_mode,
            "blas_threads": 1,
        },
        feature_version=FEATURE_VERSION,
        n_clips=int(X.shape[0]),
        calibration=calibration,
        per_fold_detail=per_fold_detail,
    )
    (out_dir / "training_result.json").write_text(
        json.dumps(asdict(result), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def _save_checkpoint_deterministic(model: nn.Module, path: Path,
                                   best_fold: int, seed: int) -> None:
    """Serialize state_dict + fixed metadata to a byte-deterministic file.

    Rather than rely on torch.save (whose zipfile embeds mtimes),
    write a plain JSON+npz sidecar: keys sorted, tensors written as
    a single flat npz. Re-loadable via load_checkpoint below.
    """
    sd = model.state_dict()
    arrays = {k: v.detach().cpu().numpy() for k, v in sd.items()}
    meta = {
        "arch": "CornHead(2052,128,6)",
        "K": K,
        "hidden": HIDDEN,
        "dropout": DROPOUT,
        "feat_dim": FEAT_DIM,
        "best_fold": int(best_fold),
        "seed": int(seed),
        "feature_version": FEATURE_VERSION,
    }
    # Write meta + arrays into a single npz whose contents are sorted-key.
    payload = {
        "__meta__": np.array(json.dumps(meta, sort_keys=True), dtype="U"),
    }
    for k in sorted(arrays.keys()):
        payload[k] = arrays[k].astype(np.float32)
    # np.savez writes zip entries in insertion order; sorted keys → deterministic order.
    # ZIP central-directory carries mtime; we bypass by writing raw bytes then
    # patching mtime → 0 via np.savez internal path is not exposed. Simpler:
    # write to a BytesIO with np.savez, then normalize the zip.
    import io
    import zipfile as _zip
    buf = io.BytesIO()
    np.savez(buf, **payload)
    src = _zip.ZipFile(io.BytesIO(buf.getvalue()), "r")
    with open(path, "wb") as fh:
        with _zip.ZipFile(fh, "w", compression=_zip.ZIP_STORED) as dst:
            for name in sorted(src.namelist()):
                info = _zip.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = _zip.ZIP_STORED
                dst.writestr(info, src.read(name))
        src.close()


def load_checkpoint(path: Path) -> tuple:
    """Return (model, meta_dict)."""
    d = np.load(path, allow_pickle=False)
    meta = json.loads(str(d["__meta__"]))
    model = CornHead(meta["feat_dim"], meta["hidden"], meta["dropout"])
    sd = {}
    for k in model.state_dict().keys():
        sd[k] = torch.from_numpy(d[k].astype(np.float32))
    model.load_state_dict(sd)
    model.eval()
    return model, meta


def _synth_labels_from_features(X: np.ndarray, seed: int = 0) -> np.ndarray:
    """Deterministic synthetic labels for proof-of-life.

    Same recipe as scripts/ear/model.py:synthesize_ratings — deterministic
    1-PC via power iteration, add Gaussian noise, round + clip to 1..K.
    """
    rng = np.random.default_rng(seed)
    Xc = X.astype(np.float64)
    col_mean = np.nanmean(Xc, axis=0)
    for j in range(Xc.shape[1]):
        m = np.isnan(Xc[:, j])
        Xc[m, j] = 0.0 if not np.isfinite(col_mean[j]) else col_mean[j]
    Xc = Xc - Xc.mean(axis=0, keepdims=True)
    v = rng.standard_normal(Xc.shape[1])
    for _ in range(30):
        v = Xc.T @ (Xc @ v)
        v /= (np.linalg.norm(v) + 1e-12)
    z = Xc @ v
    z = (z - z.mean()) / (z.std() + 1e-12)
    noise = rng.standard_normal(z.shape[0])
    y = np.clip(np.round(4 + 1.5 * z + 1.0 * noise), 1, K).astype(np.int64)
    return y


def content_hash_manifest(manifest: Path) -> str:
    """SHA-256 of the ratings-manifest file bytes. Used by the harness to
    gate retraining on manifest change."""
    h = hashlib.sha256()
    h.update(manifest.read_bytes())
    return h.hexdigest()


# ------------------------------ CLI -----------------------------------


def _synth_manifest_for_valset(valset_manifest: Path, out_manifest: Path,
                                features_dir: Path, seed: int = 0) -> Path:
    """Build a synthetic ratings manifest from the M-CLASS-1 55-clip valset.

    Column: rating\tclip_id — deterministic PC1-based labels, matching
    scripts/ear/model.py's `synthesize_ratings`.
    """
    with valset_manifest.open() as f:
        header = f.readline().rstrip("\n").split("\t")
        rows = [dict(zip(header, ln.rstrip("\n").split("\t"))) for ln in f if ln.strip()]

    clip_ids, X = [], []
    for r in rows:
        p = features_dir / f"{r['clip_id']}.npz"
        if not p.is_file():
            continue
        vec = _load_feature_npz(p)
        if vec is None:
            continue
        clip_ids.append(r["clip_id"])
        X.append(vec)
    if not X:
        raise ValueError("synth manifest: no features cached")
    X = _impute_nan(np.stack(X, axis=0))
    y = _synth_labels_from_features(X, seed=seed)
    out_manifest.parent.mkdir(parents=True, exist_ok=True)
    with out_manifest.open("w", encoding="utf-8") as fh:
        fh.write("rating\tclip_id\n")
        for r, cid in zip(y.tolist(), clip_ids):
            fh.write(f"{int(r)}\t{cid}\n")
    return out_manifest


def _main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--features-dir", type=Path,
                    default=Path("data/ear/features"))
    ap.add_argument("--ratings-manifest", type=Path,
                    default=Path("corpus/ratings/ratings_manifest.tsv"))
    ap.add_argument("--out-dir", type=Path,
                    default=Path("data/ear/training_v1"))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    ap.add_argument("--calibration", choices=["synthetic_labels_only", "user_ratings"],
                    default="user_ratings")
    ap.add_argument("--synthesize-labels", action="store_true",
                    help="Ignore the ratings column; synthesize labels from feature 1-PC.")
    ap.add_argument("--synth-valset", action="store_true",
                    help="Build a synthetic ratings manifest from the M-CLASS-1 55-clip valset "
                         "and train against that (proof-of-life mode).")
    ap.add_argument("--valset-manifest", type=Path,
                    default=Path("data/classifier/valset/valset_manifest.tsv"))
    args = ap.parse_args(argv)

    manifest = args.ratings_manifest
    calibration = args.calibration
    if args.synth_valset:
        manifest = args.out_dir / "synth_ratings_manifest.tsv"
        _synth_manifest_for_valset(args.valset_manifest, manifest,
                                   args.features_dir, seed=args.seed)
        calibration = "synthetic_labels_only"

    result = train(
        features_dir=args.features_dir,
        ratings_manifest=manifest,
        out_dir=args.out_dir,
        seed=args.seed,
        epochs=args.epochs,
        calibration=calibration,
        synthesize_labels=args.synthesize_labels,
    )
    print(f"[train] n_clips={result.n_clips} feature_version={result.feature_version}")
    print(f"[train] mean MAE = {result.mean_mae:.4f}")
    print(f"[train] majority-class MAE = {result.majority_class_mae:.4f}")
    print(f"[train] mean-integer  MAE = {result.mean_integer_mae:.4f}")
    print(f"[train] per-fold MAE = {['%.4f' % x for x in result.per_fold_mae]}")
    print(f"[train] checkpoint = {result.checkpoint_path}")
    beats = (result.mean_mae < result.majority_class_mae
             and result.mean_mae < result.mean_integer_mae)
    print(f"[train] beats naive baselines: {beats}")
    return 0 if beats else 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
