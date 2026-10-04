#!/usr/bin/python3
"""v6 Phase 1A — distribution-level realism metrics between two SETS of window embeddings.

created: 2026-10-04
milestone: M-V6-SCORECARD-1A

Library + CLI. A = candidate set, B = reference set, each a list of Songs (npz from
embed_audio.py). Nothing is paired; no human labels. Per backbone we report:

  KID      unbiased MMD^2 with polynomial kernel k(x,y) = (x.y/d + 1)^3, mean +- std over random
           equal-size subsets (Binkowski et al. 2018), plus the full-sample MMD^2 and a two-level
           bootstrap 95% CI: songs are resampled with replacement (independently in A and B) and
           ALL windows of a drawn song are used, so the CI reflects song-level sampling noise.
  FAD      Frechet distance between Gaussians fitted to A and B (scipy sqrtm, real-part fix);
           covariances are Ledoit-Wolf shrunk when n < 10*d (always true at n~1500, d=512/1536).
  density / coverage   Naeem et al. 2020, k=5 NN balls around REFERENCE windows:
           density > 1 means candidates sit in dense real regions (realism-ish),
           coverage in [0,1] is the fraction of reference balls hit by any candidate (diversity).
  kNN two-sample       for each candidate window, fraction of its k=5 neighbours in the union that
           are reference ("real fraction", null expectation ~ nB/(nA+nB-1)); and C2ST-kNN balanced
           accuracy of the majority-vote classifier (0.5 = indistinguishable, 1.0 = separable).
  SONG-AWARE: for density/coverage/kNN, windows of the same song (same sha16) are never each
           other's neighbours. Without this, a window's neighbours are its own song's other windows
           (always in the same set), so C2ST -> 1 and coverage -> 0 even for real vs real.
  novelty  per candidate SONG, max cosine of any of its windows to any reference window and the
           reference song hit; flagged above --novelty-threshold (copying / memorisation guard).

Why only KID gets the bootstrap: resampling songs with replacement duplicates windows. For the
song-level KID a duplicate is just a weight (never paired with itself), but for nearest-neighbour
statistics a point's duplicate becomes its own nearest neighbour, so kNN/density/coverage CIs
would be meaningless. Their noise floor is measured by baseline_real_vs_real.py split-halves.

Determinism: every random choice uses numpy.random.default_rng(--seed). No torch here.
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "4", "MKL_NUM_THREADS": "4", "OPENBLAS_NUM_THREADS": "4"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)
if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))

import numpy as np  # noqa: E402
from scipy.linalg import sqrtm  # noqa: E402
from scipy.spatial.distance import cdist  # noqa: E402

from scripts.v6.v6_common import env_record, iter_npz_files, read_json, write_json_atomic  # noqa: E402

SCHEMA_VERSION = "v6.distribution.1"
DEFAULT_OUT_DIR = _WS / "data" / "v6" / "scorecard"


# ----------------------------------------------------------------------------- data
@dataclass
class Song:
    song_id: str
    sha16: str
    emb: np.ndarray  # (n_windows, d) float64
    path: str = ""
    meta: dict | None = None


def load_songs(inputs) -> list[Song]:
    """Load Songs from npz files/dirs produced by embed_audio.py (sidecar JSON optional)."""
    songs = []
    for npz in iter_npz_files(inputs):
        emb = np.asarray(np.load(npz)["emb"], dtype=np.float64)
        side = npz.with_suffix(".json")
        meta = read_json(side) if side.exists() else {}
        songs.append(Song(song_id=meta.get("name", npz.stem), sha16=meta.get("sha16", npz.stem),
                          emb=emb, path=meta.get("path", str(npz)), meta=meta))
    return [s for s in songs if len(s.emb)]


def stack(songs: list[Song]) -> tuple[np.ndarray, np.ndarray]:
    X = np.concatenate([s.emb for s in songs], axis=0)
    idx = np.concatenate([np.full(len(s.emb), i) for i, s in enumerate(songs)])
    return X, idx


# ----------------------------------------------------------------------------- KID
def poly_kernel(X: np.ndarray, Y: np.ndarray, degree: int = 3) -> np.ndarray:
    return (X @ Y.T / X.shape[1] + 1.0) ** degree


def mmd2_unbiased(X: np.ndarray, Y: np.ndarray) -> float:
    m, n = len(X), len(Y)
    if m < 2 or n < 2:
        raise ValueError("need >= 2 samples per set for unbiased MMD^2")
    Kxx, Kyy, Kxy = poly_kernel(X, X), poly_kernel(Y, Y), poly_kernel(X, Y)
    return float((Kxx.sum() - np.trace(Kxx)) / (m * (m - 1))
                 + (Kyy.sum() - np.trace(Kyy)) / (n * (n - 1)) - 2.0 * Kxy.mean())


def kid(X: np.ndarray, Y: np.ndarray, rng: np.random.Generator, subsets: int = 50,
        subset_size: int | None = None) -> dict:
    size = min(500, len(X), len(Y)) if subset_size is None else min(subset_size, len(X), len(Y))
    vals = np.array([mmd2_unbiased(X[rng.choice(len(X), size, replace=False)],
                                   Y[rng.choice(len(Y), size, replace=False)]) for _ in range(subsets)])
    return {"mean": float(vals.mean()), "std": float(vals.std(ddof=1)) if subsets > 1 else 0.0,
            "subsets": int(subsets), "subset_size": int(size)}


def kid_point(X: np.ndarray, Y: np.ndarray, rng: np.random.Generator, cap: int = 2000) -> float:
    """Full-sample unbiased MMD^2 (deterministically subsampled to `cap` per set if larger)."""
    if len(X) > cap:
        X = X[rng.choice(len(X), cap, replace=False)]
    if len(Y) > cap:
        Y = Y[rng.choice(len(Y), cap, replace=False)]
    return mmd2_unbiased(X, Y)


# ----------------------------------------------------------------------------- FAD
def _cov(Z: np.ndarray) -> tuple[np.ndarray, bool]:
    if len(Z) < 10 * Z.shape[1]:
        from sklearn.covariance import ledoit_wolf
        return ledoit_wolf(Z)[0], True
    return np.cov(Z, rowvar=False), False


def fad(X: np.ndarray, Y: np.ndarray) -> dict:
    mu_x, mu_y = X.mean(axis=0), Y.mean(axis=0)
    sx, shrunk_x = _cov(X)
    sy, shrunk_y = _cov(Y)
    covmean = sqrtm(sx @ sy)
    if isinstance(covmean, tuple):  # older scipy returned (sqrtm, errest)
        covmean = covmean[0]
    if np.iscomplexobj(covmean):
        covmean = covmean.real
    diff = mu_x - mu_y
    val = float(diff @ diff + np.trace(sx) + np.trace(sy) - 2.0 * np.trace(covmean))
    return {"value": max(val, 0.0), "raw": val, "mean_shift_sq": float(diff @ diff),
            "shrinkage_used": bool(shrunk_x or shrunk_y)}


# ----------------------------------------------------------------------------- density / coverage
def _mask_same_song(D: np.ndarray, key_r: np.ndarray | None, key_c: np.ndarray | None) -> np.ndarray:
    """Set distances between windows of the same song (same key) to +inf, in place."""
    if key_r is not None and key_c is not None:
        D[np.asarray(key_r)[:, None] == np.asarray(key_c)[None, :]] = np.inf
    return D


def density_coverage(X: np.ndarray, Y: np.ndarray, k: int = 5, key_x=None, key_y=None) -> dict:
    """Naeem et al. 2020 with reference B=Y as the real manifold, X=candidate. Song-aware: windows
    of the same song (same key) are never neighbours, otherwise within-song similarity shrinks the
    reference balls and coverage collapses to ~0 even for real-vs-real. Ball membership is <=."""
    dyy = _mask_same_song(cdist(Y, Y), key_y, key_y)
    if key_y is None:
        np.fill_diagonal(dyy, np.inf)
    radii = np.sort(dyy, axis=1)[:, k - 1]
    if not np.all(np.isfinite(radii)):
        raise ValueError("reference set needs > k windows from other songs for every window")
    dxy = _mask_same_song(cdist(X, Y), key_x, key_y)  # (nA, nB)
    inside = dxy <= radii[None, :]
    return {"density": float(inside.sum() / (k * len(X))),
            "coverage": float(inside.any(axis=0).mean()), "k": int(k)}


# ----------------------------------------------------------------------------- kNN two-sample
def knn_two_sample(X: np.ndarray, Y: np.ndarray, k: int = 5, key_x=None, key_y=None) -> dict:
    """Song-aware kNN two-sample test on the union (same-song pairs excluded, see above)."""
    Z = np.concatenate([X, Y], axis=0)
    is_ref = np.concatenate([np.zeros(len(X), bool), np.ones(len(Y), bool)])
    D = cdist(Z, Z)
    np.fill_diagonal(D, np.inf)
    if key_x is not None and key_y is not None:
        key = np.concatenate([np.asarray(key_x), np.asarray(key_y)])
        _mask_same_song(D, key, key)
        n_same = (key[:len(X), None] == key[None, :]).sum(axis=1)  # own-song windows incl. self
    else:
        n_same = np.ones(len(X), int)
    nn = np.argpartition(D, k, axis=1)[:, :k]
    if not np.all(np.isfinite(np.take_along_axis(D, nn, axis=1))):
        raise ValueError("fewer than k eligible neighbours for some window")
    ref_frac = is_ref[nn].mean(axis=1)
    pred_ref = ref_frac > 0.5
    acc_cand = float((~pred_ref[:len(X)]).mean())
    acc_ref = float(pred_ref[len(X):].mean())
    null = float(np.mean(len(Y) / (len(Z) - n_same)))  # candidate's own-song windows are all in X
    return {"k": int(k), "cand_real_fraction_per_window": ref_frac[:len(X)],
            "cand_real_fraction_mean": float(ref_frac[:len(X)].mean()),
            "null_expectation_real_fraction": null,
            "c2st_balanced_accuracy": 0.5 * (acc_cand + acc_ref),
            "c2st_accuracy": float((pred_ref == is_ref).mean()),
            "acc_candidate": acc_cand, "acc_reference": acc_ref}


# ----------------------------------------------------------------------------- novelty guard
def nearest_reference(songs_a: list[Song], songs_b: list[Song], threshold: float = 0.97) -> list[dict]:
    Y, idx_b = stack(songs_b)
    Yn = Y / np.maximum(np.linalg.norm(Y, axis=1, keepdims=True), 1e-12)
    out = []
    for s in songs_a:
        Xn = s.emb / np.maximum(np.linalg.norm(s.emb, axis=1, keepdims=True), 1e-12)
        S = Xn @ Yn.T
        i, j = np.unravel_index(int(np.argmax(S)), S.shape)
        out.append({"song_id": s.song_id, "sha16": s.sha16, "nearest_ref_cos": float(S[i, j]),
                    "candidate_window": int(i), "nearest_ref_song": songs_b[idx_b[j]].song_id,
                    "nearest_ref_sha16": songs_b[idx_b[j]].sha16, "flagged": bool(S[i, j] > threshold)})
    return out


# ----------------------------------------------------------------------------- song-level KID + bootstrap
def song_block_means(songs_a: list[Song], songs_b: list[Song]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Kernel values averaged over window pairs for every song pair: (Maa, Mbb, Mab)."""
    X, ia = stack(songs_a)
    Y, ib = stack(songs_b)
    Pa = np.zeros((len(songs_a), len(X)))
    Pa[ia, np.arange(len(X))] = 1.0
    Pa /= Pa.sum(axis=1, keepdims=True)
    Pb = np.zeros((len(songs_b), len(Y)))
    Pb[ib, np.arange(len(Y))] = 1.0
    Pb /= Pb.sum(axis=1, keepdims=True)
    return Pa @ poly_kernel(X, X) @ Pa.T, Pb @ poly_kernel(Y, Y) @ Pb.T, Pa @ poly_kernel(X, Y) @ Pb.T


def mmd2_song_level(Maa: np.ndarray, Mbb: np.ndarray, Mab: np.ndarray,
                    wa: np.ndarray | None = None, wb: np.ndarray | None = None) -> float:
    """U-statistic over SONGS: same-song window pairs are excluded from the within-set terms, so
    the null expectation is 0 even though windows cluster by song. Weights = bootstrap counts."""
    wa = np.ones(len(Maa)) if wa is None else np.asarray(wa, float)
    wb = np.ones(len(Mbb)) if wb is None else np.asarray(wb, float)
    Waa, Wbb = np.outer(wa, wa), np.outer(wb, wb)
    np.fill_diagonal(Waa, 0.0)
    np.fill_diagonal(Wbb, 0.0)
    if Waa.sum() == 0 or Wbb.sum() == 0:
        return float("nan")
    return float((Waa * Maa).sum() / Waa.sum() + (Wbb * Mbb).sum() / Wbb.sum()
                 - 2.0 * (np.outer(wa, wb) * Mab).sum() / (wa.sum() * wb.sum()))


def song_level_kid(songs_a: list[Song], songs_b: list[Song], rng: np.random.Generator,
                   n_boot: int = 200) -> dict:
    """Point estimate + two-level bootstrap: songs resampled with replacement (independently in A
    and B), all windows of each drawn song used (as multiplicity weights)."""
    Maa, Mbb, Mab = song_block_means(songs_a, songs_b)
    out = {"point": mmd2_song_level(Maa, Mbb, Mab)}
    if n_boot > 0:
        vals = []
        for _ in range(n_boot):
            wa = np.bincount(rng.integers(0, len(songs_a), len(songs_a)), minlength=len(songs_a))
            wb = np.bincount(rng.integers(0, len(songs_b), len(songs_b)), minlength=len(songs_b))
            vals.append(mmd2_song_level(Maa, Mbb, Mab, wa, wb))
        v = np.asarray([x for x in vals if np.isfinite(x)], dtype=np.float64)
        out["bootstrap"] = {"n_boot": int(len(v)), "mean": float(v.mean()),
                            "std": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                            "ci95": [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]}
    return out


# ----------------------------------------------------------------------------- scorecard
def compute_all(songs_a: list[Song], songs_b: list[Song], seed: int = 0, subsets: int = 50,
                subset_size: int | None = None, n_boot: int = 200, k: int = 5,
                novelty_threshold: float = 0.97, backbone: str = "", with_fad: bool = True) -> dict:
    rng = np.random.default_rng(seed)
    X, idx_a = stack(songs_a)
    Y, _ = stack(songs_b)
    if X.shape[1] != Y.shape[1]:
        raise ValueError(f"dim mismatch {X.shape[1]} vs {Y.shape[1]}")
    res = {"schema_version": SCHEMA_VERSION, "backbone": backbone, "dim": int(X.shape[1]),
           "n_songs_a": len(songs_a), "n_windows_a": int(len(X)),
           "n_songs_b": len(songs_b), "n_windows_b": int(len(Y)),
           "params": {"seed": seed, "subsets": subsets, "subset_size": subset_size, "bootstrap": n_boot,
                      "k": k, "novelty_threshold": novelty_threshold},
           "inputs": {"a": [s.sha16 for s in songs_a], "b": [s.sha16 for s in songs_b]}}
    res["kid"] = kid(X, Y, rng, subsets, subset_size)
    res["kid"]["full"] = kid_point(X, Y, rng)
    res["kid"]["song_level"] = song_level_kid(songs_a, songs_b, rng, n_boot)
    if with_fad:
        res["fad"] = fad(X, Y)
    key_a = np.array([songs_a[i].sha16 for i in idx_a])
    key_b = np.array([s.sha16 for s in songs_b for _ in range(len(s.emb))])
    res["density_coverage"] = density_coverage(X, Y, k, key_a, key_b)
    knn = knn_two_sample(X, Y, k, key_a, key_b)
    per_window = knn.pop("cand_real_fraction_per_window")
    res["knn"] = knn
    nov = nearest_reference(songs_a, songs_b, novelty_threshold)
    res["novelty"] = {"threshold": novelty_threshold, "n_flagged": int(sum(n["flagged"] for n in nov)),
                      "flagged": [n["song_id"] for n in nov if n["flagged"]]}
    per_song = []
    for i, s in enumerate(songs_a):
        rec = dict(nov[i])
        rec.update({"n_windows": int(len(s.emb)),
                    "knn_real_fraction_mean": float(per_window[idx_a == i].mean())})
        per_song.append(rec)
    res["per_song_candidate"] = sorted(per_song, key=lambda r: r["knn_real_fraction_mean"])
    res["env"] = env_record()
    return res


def flat_scalars(res: dict) -> dict:
    """The headline numbers of a compute_all() result, flattened for tables/aggregation."""
    out = {"kid_mean": res["kid"]["mean"], "kid_std": res["kid"]["std"], "kid_full": res["kid"]["full"],
           "density": res["density_coverage"]["density"], "coverage": res["density_coverage"]["coverage"],
           "knn_real_fraction": res["knn"]["cand_real_fraction_mean"],
           "knn_real_fraction_null": res["knn"]["null_expectation_real_fraction"],
           "c2st_balanced_accuracy": res["knn"]["c2st_balanced_accuracy"],
           "novelty_max_cos": max((r["nearest_ref_cos"] for r in res["per_song_candidate"]), default=0.0)}
    if "fad" in res:
        out["fad"] = res["fad"]["value"]
    out["kid_song"] = res["kid"]["song_level"]["point"]
    if "bootstrap" in res["kid"]["song_level"]:
        out["kid_song_ci95_lo"], out["kid_song_ci95_hi"] = res["kid"]["song_level"]["bootstrap"]["ci95"]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--candidate", nargs="+", required=True, help="npz files/dirs for set A")
    ap.add_argument("--reference", nargs="+", required=True, help="npz files/dirs for set B")
    ap.add_argument("--backbone", required=True, help="label, e.g. clap or mert (also in output name)")
    ap.add_argument("--run-name", required=True)
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--subsets", type=int, default=50)
    ap.add_argument("--subset-size", type=int, default=None, help="default min(500, nA, nB)")
    ap.add_argument("--bootstrap", type=int, default=200)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--novelty-threshold", type=float, default=0.97)
    ap.add_argument("--no-fad", action="store_true")
    args = ap.parse_args(argv)
    songs_a, songs_b = load_songs(args.candidate), load_songs(args.reference)
    if not songs_a or not songs_b:
        print("empty candidate or reference set", file=sys.stderr)
        return 1
    res = compute_all(songs_a, songs_b, args.seed, args.subsets, args.subset_size, args.bootstrap,
                      args.k, args.novelty_threshold, args.backbone, with_fad=not args.no_fad)
    out = Path(args.out_dir) / args.run_name / f"distribution_{args.backbone}.json"
    write_json_atomic(out, res)
    print(f"wrote {out}")
    for key, val in sorted(flat_scalars(res).items()):
        print(f"  {key:>24s} = {val:.6g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
