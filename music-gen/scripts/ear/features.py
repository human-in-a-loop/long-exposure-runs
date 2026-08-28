"""Feature extractor for M-EAR-1/preparation.

Combines:
  - M-CLASS-1: PANNs Cnn14 penultimate 2048-dim embedding
  - M-HEUR-1: mess-scale vectors (melody / timbre / form / dynamics)
  - optional M-TEX-1/panel: VGGish 128-dim embedding

Per-clip result cached under data/ear/features/<clip_id>.npz keyed by
(sha256_of_wav, feature_version). Second run is skip-if-hash-matches.

Song-level aggregation applies the M-INGEST-1 anchored-tail debias
weight: `weight = (clip.t_end - clip.t_start - overlap_with_prev) / 30`,
falling back to 1.0 when no prev clip or anchored_tail is False.

Public API:
    extract_features(clip_id, wav_path, *, use_vggish=False) -> dict
    aggregate_song(rows, weights=None) -> np.ndarray

Non-factor isolation: this module MUST NOT import
`scripts.classifier.sidecar_nonfactor` — enforced by
tests/test_integration_cross_branch.py §11.
"""
# created: 2026-08-28T06:50:00Z  cycle: 6  run_id: run-2026-08-28T040704Z
# agent: worker (clone-2, fork 3168fb0e47a1)  milestone: M-EAR-1/preparation/features
from __future__ import annotations
from . import _interp  # noqa: F401 — interpreter guard

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

# Single-threaded numeric envelope for bit-determinism (matches UMXHQ contract).
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

FEATURE_VERSION = "ear-features-v1"
PANNS_DIM = 2048
HEUR_DIM = 4  # melody, timbre, form, dynamics
VGGISH_DIM = 128


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _feat_hash(*arrays: np.ndarray) -> str:
    h = hashlib.sha256()
    for a in arrays:
        if a is None:
            h.update(b"None")
            continue
        h.update(np.ascontiguousarray(a.astype(np.float32)).tobytes())
    return h.hexdigest()[:16]


# --- lazy singletons ----------------------------------------------------------
_TAGGER = None
_VGG_STATE: dict = {"tried": False, "model": None, "rung": None}


def _get_tagger():
    global _TAGGER
    if _TAGGER is None:
        # Import lazily so --help paths stay fast.
        from scripts.classifier.tagger import Tagger
        _TAGGER = Tagger()
    return _TAGGER


def _get_vggish():
    """Return (callable(y, sr)->np.ndarray[128] | None), rung name."""
    if _VGG_STATE["tried"]:
        return _VGG_STATE["model"], _VGG_STATE["rung"]
    _VGG_STATE["tried"] = True
    try:
        from scripts.texture.embedding_panel import _load_vggish, _embed_vggish  # type: ignore
    except Exception:
        _VGG_STATE["rung"] = "unavailable_import_error"
        return None, _VGG_STATE["rung"]
    try:
        model = _load_vggish()
    except Exception:
        _VGG_STATE["rung"] = "unavailable_load_error"
        return None, _VGG_STATE["rung"]

    def _run(y, sr):
        return _embed_vggish(model, y, sr)

    _VGG_STATE["model"] = _run
    _VGG_STATE["rung"] = "vggish"
    return _run, "vggish"


# --- heuristic vector ---------------------------------------------------------
def _heuristic_vector(y: np.ndarray, sr: int) -> np.ndarray:
    """Return [melody, timbre, form, dynamics] with NaN for null-with-reason."""
    from scripts.heuristics.melody import melody_quality
    from scripts.heuristics.timbre import timbre_quality
    from scripts.heuristics.form import form_quality
    from scripts.heuristics.dynamics import dynamics_quality

    out = np.full(HEUR_DIM, np.nan, dtype=np.float32)
    for i, fn in enumerate([melody_quality, timbre_quality, form_quality, dynamics_quality]):
        try:
            r = fn(y, sr)
            m = getattr(r, "mess_scale", None)
            if m is not None:
                out[i] = float(m)
        except Exception:
            pass  # NaN sentinel already in place
    return out


# --- PANNs embedding ---------------------------------------------------------
def _panns_embedding(y: np.ndarray, sr: int) -> np.ndarray:
    tagger = _get_tagger()
    emb = tagger.embed(y, sr)
    return np.asarray(emb, dtype=np.float32)


# --- Public API ---------------------------------------------------------------
@dataclass
class FeatureRow:
    clip_id: str
    panns_embed: np.ndarray  # (2048,)
    heuristic_vec: np.ndarray  # (4,)
    vggish_embed: Optional[np.ndarray]  # (128,) or None
    feat_hash: str
    source_wav_sha256: str


CACHE_DIR = Path(__file__).resolve().parents[2] / "data" / "ear" / "features"


def _cache_path(clip_id: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{clip_id}.npz"


def _load_wav_for_panns(wav_path: Path) -> tuple[np.ndarray, int]:
    import librosa
    from scripts.classifier.tagger import MODEL_SR
    y, sr = librosa.load(str(wav_path), sr=MODEL_SR, mono=True)
    return y.astype(np.float32), sr


def _load_wav_for_heur(wav_path: Path) -> tuple[np.ndarray, int]:
    import librosa
    y, sr = librosa.load(str(wav_path), sr=22050, mono=True)
    return y.astype(np.float32), sr


def extract_features(
    clip_id: str,
    wav_path: Path,
    *,
    use_vggish: bool = False,
    force: bool = False,
) -> FeatureRow:
    """Extract PANNs + heuristic + (optional) VGGish features for one clip.

    Caches by (sha256_of_wav, feature_version, use_vggish) under
    data/ear/features/<clip_id>.npz. Re-run with matching hash is O(load).
    """
    wav_path = Path(wav_path)
    src_sha = sha256_of(wav_path)
    cache = _cache_path(clip_id)
    if cache.exists() and not force:
        try:
            npz = np.load(cache, allow_pickle=False)
            if (
                str(npz["source_wav_sha256"]) == src_sha
                and str(npz["feature_version"]) == FEATURE_VERSION
                and bool(npz["has_vggish"]) == bool(use_vggish and npz["vggish_embed"].size > 0)
            ):
                vgg = npz["vggish_embed"] if bool(npz["has_vggish"]) else None
                return FeatureRow(
                    clip_id=clip_id,
                    panns_embed=npz["panns_embed"],
                    heuristic_vec=npz["heuristic_vec"],
                    vggish_embed=vgg,
                    feat_hash=str(npz["feat_hash"]),
                    source_wav_sha256=src_sha,
                )
        except Exception:
            pass  # fall through to recompute

    # PANNs at 32 kHz mono
    y_panns, sr_panns = _load_wav_for_panns(wav_path)
    panns = _panns_embedding(y_panns, sr_panns)

    # Heuristics at 22.05 kHz mono (matches battery.load_clip)
    y_heur, sr_heur = _load_wav_for_heur(wav_path)
    heur = _heuristic_vector(y_heur, sr_heur)

    vgg = None
    if use_vggish:
        model, rung = _get_vggish()
        if model is not None:
            try:
                vgg = np.asarray(model(y_heur, sr_heur), dtype=np.float32)
                if vgg.ndim > 1:
                    vgg = vgg.mean(axis=0).astype(np.float32)
            except Exception:
                vgg = None

    fhash = _feat_hash(panns, heur, vgg)
    row = FeatureRow(
        clip_id=clip_id,
        panns_embed=panns,
        heuristic_vec=heur,
        vggish_embed=vgg,
        feat_hash=fhash,
        source_wav_sha256=src_sha,
    )

    np.savez(
        cache,
        clip_id=np.array(clip_id),
        panns_embed=panns,
        heuristic_vec=heur,
        vggish_embed=vgg if vgg is not None else np.zeros(0, dtype=np.float32),
        has_vggish=np.array(vgg is not None),
        feat_hash=np.array(fhash),
        source_wav_sha256=np.array(src_sha),
        feature_version=np.array(FEATURE_VERSION),
    )
    return row


def stack_matrix(rows: list[FeatureRow], *, include_vggish: bool = False) -> np.ndarray:
    """Stack per-clip features into an (N, D) matrix. NaN heuristics stay NaN."""
    mats = []
    for r in rows:
        parts = [r.panns_embed.astype(np.float32), r.heuristic_vec.astype(np.float32)]
        if include_vggish:
            v = r.vggish_embed if r.vggish_embed is not None else np.zeros(VGGISH_DIM, dtype=np.float32)
            parts.append(v.astype(np.float32))
        mats.append(np.concatenate(parts, axis=0))
    return np.stack(mats, axis=0)


# --- Song-level aggregation with anchored-tail debias -------------------------
def anchored_tail_weight(
    t_start: float, t_end: float, overlap_with_prev: float, anchored_tail: bool
) -> float:
    """M-INGEST-1 anchored-tail debias weight.

    Formula per plan of record: weight = (t_end - t_start - overlap_with_prev) / 30.
    First clip in a song, or when anchored_tail is False, gets weight = 1.0.
    """
    if not anchored_tail:
        return 1.0
    dur = float(t_end - t_start)
    return max(0.0, (dur - float(overlap_with_prev)) / 30.0)


def aggregate_song(feature_rows: list[FeatureRow], weights: Optional[list[float]] = None) -> np.ndarray:
    """Weighted mean of clip features + weighted std, concatenated.

    Doubled dimensionality: [weighted_mean || weighted_std]. Weights default
    to uniform. For single-clip "songs" (the leak test), weighted_std is a
    zero vector by construction (identity aggregation).
    """
    if not feature_rows:
        raise ValueError("no feature rows to aggregate")
    if weights is None:
        weights = [1.0] * len(feature_rows)
    if len(weights) != len(feature_rows):
        raise ValueError("weights length mismatch")

    X = stack_matrix(feature_rows, include_vggish=any(r.vggish_embed is not None for r in feature_rows))
    w = np.asarray(weights, dtype=np.float64)
    w = w / (w.sum() + 1e-12)
    # Replace NaN heuristics with column mean (weighted) before aggregating.
    for j in range(X.shape[1]):
        col = X[:, j]
        nan_mask = np.isnan(col)
        if nan_mask.any():
            good = ~nan_mask
            if good.any():
                mu = float(np.average(col[good], weights=w[good]))
            else:
                mu = 0.0
            X[nan_mask, j] = mu
    mean = np.average(X, axis=0, weights=w)
    var = np.average((X - mean) ** 2, axis=0, weights=w)
    std = np.sqrt(np.clip(var, 0.0, None))
    return np.concatenate([mean, std], axis=0).astype(np.float32)


# --- CLI: run over the classifier valset --------------------------------------
def _main(argv: list[str]) -> int:
    import argparse
    import time

    ap = argparse.ArgumentParser(description="Extract ear features over the classifier valset.")
    ap.add_argument("--valset", type=Path,
                    default=Path("data/classifier/valset/valset_manifest.tsv"))
    ap.add_argument("--clips-dir", type=Path,
                    default=Path("data/classifier/valset/clips"))
    ap.add_argument("--vggish", action="store_true", help="Include VGGish 128-dim embedding.")
    ap.add_argument("--force", action="store_true", help="Ignore cache and re-extract.")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args(argv)

    with args.valset.open() as f:
        header = f.readline().rstrip("\n").split("\t")
        rows = [dict(zip(header, ln.rstrip("\n").split("\t"))) for ln in f if ln.strip()]
    if args.limit:
        rows = rows[: args.limit]

    print(f"[features] extracting over {len(rows)} clips (use_vggish={args.vggish})")
    t0 = time.time()
    out = []
    for i, r in enumerate(rows):
        wav = args.clips_dir / f"{r['clip_id']}.wav"
        fr = extract_features(r["clip_id"], wav, use_vggish=args.vggish, force=args.force)
        out.append(fr)
        if (i + 1) % 10 == 0 or (i + 1) == len(rows):
            dt = time.time() - t0
            print(f"[features] {i + 1}/{len(rows)} clip_id={r['clip_id']} "
                  f"feat_hash={fr.feat_hash} (elapsed {dt:.1f}s)")
    print(f"[features] done; cached under {CACHE_DIR}")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv[1:]))
