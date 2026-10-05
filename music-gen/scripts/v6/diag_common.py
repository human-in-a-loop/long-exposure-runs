#!/usr/bin/python3
"""v6 Phase 5 (iteration 05) — shared helpers for the gap-localisation diagnostics (diag_stems_v6.py, diag_embed_v6.py).

created: 2026-10-05
milestone: M-V6-ITER-05/localize

  score()             distribution_metrics.compute_all + flat_scalars between two Song lists (seeded, small bootstrap)
  deterministic_halves() / split_half_floor()   the real-vs-real noise floor of ANY song set (numpy default_rng(seed) permutations,
                      as baseline_real_vs_real does): mean / sd / p2.5 / p97.5 per metric over n_splits
  song_means()        unit-norm mean of unit-normed windows per song (the song-level embedding used by the spread diagnostics)
  embed_set()         sha-cached embeddings for a list of audio files (scorecard.embed_and_load) with optional labels
  md_table()          a Markdown table from headers + rows (numbers formatted with 4 significant digits)

Discipline: /usr/bin/python3 guard (via the scorecard modules); seeds explicit; sorted-key atomic JSON; writes under data/v6 only.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))

import numpy as np  # noqa: E402

from scripts.v6 import distribution_metrics as dm  # noqa: E402
from scripts.v6 import scorecard as sc  # noqa: E402

SCHEMA_VERSION = "v6.diagnostics.1"
DIAG_DIR = _WS / "data" / "v6" / "scorecard" / "diagnostics"
FLOOR_METRICS = ("kid_song", "c2st_balanced_accuracy", "coverage", "knn_real_fraction", "density", "fad")


def agg(values) -> dict:
    v = np.asarray([x for x in values if x is not None and np.isfinite(x)], dtype=np.float64)
    if not len(v):
        return {"n": 0}
    return {"n": int(len(v)), "mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
            "min": float(v.min()), "max": float(v.max()), "p2_5": float(np.percentile(v, 2.5)), "p97_5": float(np.percentile(v, 97.5))}


def score(songs_a: list, songs_b: list, seed: int = 0, k: int = 5, n_boot: int = 200, subsets: int = 50, backbone: str = "") -> dict:
    """Flat headline metrics of A (candidate) vs B (reference), plus sizes."""
    res = dm.compute_all(songs_a, songs_b, seed=seed, subsets=subsets, n_boot=n_boot, k=k, backbone=backbone)
    flat = dm.flat_scalars(res)
    flat.update({"n_songs_a": res["n_songs_a"], "n_songs_b": res["n_songs_b"], "n_windows_a": res["n_windows_a"], "n_windows_b": res["n_windows_b"]})
    return flat


def deterministic_halves(n: int, n_splits: int, seed: int) -> list:
    """[(idx_a, idx_b)] disjoint halves of range(n) per split; numpy default_rng(seed), the same convention as the baseline."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_splits):
        perm = rng.permutation(n)
        out.append((sorted(int(i) for i in perm[: n // 2]), sorted(int(i) for i in perm[n // 2:])))
    return out


def split_half_floor(songs: list, n_splits: int = 10, seed: int = 0, k: int = 5, backbone: str = "") -> dict:
    """Real-vs-real noise floor of `songs`: score(half A, half B) per split, aggregated per metric."""
    per_split = []
    for i, (ia, ib) in enumerate(deterministic_halves(len(songs), n_splits, seed)):
        flat = score([songs[j] for j in ia], [songs[j] for j in ib], seed=seed + i, k=k, n_boot=0, subsets=20, backbone=backbone)
        flat["split"] = i
        per_split.append(flat)
    return {"n_splits": n_splits, "seed": seed, "k": k, "n_songs": len(songs), "per_split": per_split,
            "aggregate": {m: agg([p.get(m) for p in per_split]) for m in FLOOR_METRICS}}


def ratio_to_floor(value, floor: dict, key: str = "p97_5"):
    """value / floor[key] (None when either is missing or the floor is ~0 / negative, e.g. a kid floor below 0)."""
    f = (floor or {}).get(key)
    if value is None or f is None or not np.isfinite(value) or not np.isfinite(f) or f <= 1e-12:
        return None
    return float(value / f)


def song_means(songs: list) -> np.ndarray:
    """(n_songs, d): unit-norm mean of the unit-normed windows of every song."""
    out = []
    for s in songs:
        X = np.asarray(s.emb, dtype=np.float64)
        Xn = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
        m = Xn.mean(axis=0)
        out.append(m / max(float(np.linalg.norm(m)), 1e-12))
    return np.stack(out)


def embed_set(paths: list, backbone: str, emb_dir: Path, log, tag: str | None = None, labels: dict | None = None) -> list:
    """Songs for `paths` (sha-cached npz; files without usable windows are dropped and logged)."""
    songs, dropped = sc.embed_and_load([Path(p) for p in paths], backbone, Path(emb_dir), log, tag=tag, labels=labels)
    for d in dropped:
        log(f"[{backbone}] dropped {d['name']}: {d['reason']}")
    return songs


def fmt(x, nd: int = 4) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "-"
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, (int, float)):
        return f"{x:.{nd}g}"
    return str(x)


def md_table(headers: list, rows: list) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in rows:
        lines.append("| " + " | ".join(fmt(c) for c in r) + " |")
    return "\n".join(lines) + "\n"
