#!/usr/bin/python3
# ---
# cycle: 21
# milestone: M-V4-EAR-1
# purpose: Lightweight exemplar ear (NOT a trained regressor). Backbone
#          CLAP+VGGish per docs/specs/v4_rules_and_ear_spec.md. CLAP
#          fails to install in this environment (torchvision::nms
#          missing per data/texture/embedding_rung.log); this script
#          therefore lands on the VGGish-only fallback and records the
#          substitution in the manifest per spec §backbone.
#          10s windows, hop 5s, top-k window similarity, mean of the
#          best 50% windows. Calibration: leave-one-out mean E and
#          fixed noise-floor F, score = 1 + 6 * (s - F) / (E - F),
#          clipped to [1,7]. Fully deterministic given pinned VGGish
#          weights + 7-key env pin + TF_ENABLE_ONEDNN_OPTS=0.
# ---
"""M-V4-EAR-1 substantive ear.

Contracts:
    * No PRNG. `/usr/bin/python3` guard.
    * TF_ENABLE_ONEDNN_OPTS=0 forced for byte-determinism.
    * VGGish 128-D frame embeddings (1 frame ~ 0.96s @ 16kHz mono).
    * Output artifacts under `data/v4/ear/`:
        - ear_scores.json (per candidate + per exemplar leave-one-out
          + band-4 spot-check + calibration params)
        - exemplar_embeddings.npz (window embeddings per exemplar)
        - candidate_embeddings.npz (window embeddings per candidate)
        - manifest.json (env-pin + shas + fallback substitution notice)
        - env_pin.json (canonical 7-key)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

# force deterministic TF numerics BEFORE tensorflow is imported anywhere
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

CANONICAL_ENV_PIN_SHA = (
    "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
)

# Exemplar set (5 songs) per campaign prompt + v4 rules/ear spec.
EXEMPLARS = (
    # (short_id, human_name, rating_band, mp3_path)
    ("chicken_grease", "Chicken Grease", 6,
     "corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3"),
    ("peach_dream", "Peach Dream", 6,
     "corpus/ratings/6/015__wXvX1vOe0rQ__Peach_Dream.mp3"),
    ("molasses", "Hiatus Kaiyote - Molasses", 7,
     "corpus/ratings/7/019__LOCAL__Hiatus_Kaiyote_-_Molasses.mp3"),
    ("essence", "Wizkid - Essence ft. Tems", 7,
     "corpus/ratings/7/005__LOCAL__Wizkid_-_Essence_ft._Tems.mp3"),
    ("desire", "Desire", 7,
     "corpus/ratings/7/001__LOCAL__Desire.mp3"),
)

# Band-4 spot check (3 songs, small).
BAND_4_SPOT_CHECK = (
    ("aguanile", "Hector Lavoe - Aguanile",
     "corpus/ratings/4/001__pz650EkJFKc__Hector_Lavoe_-_Aguanile.mp3"),
    ("stay_live", "Stay (Live)",
     "corpus/ratings/4/002__Bc4AezWceUc__Stay_Live.mp3"),
    ("wagon_wheel", "OCMS - Wagon Wheel",
     "corpus/ratings/4/007__1gX1EP6mG-E__Old_Crow_Medicine_Show_-_Wagon_Wheel.mp3"),
)

WINDOW_S = 10.0
HOP_S = 5.0
SR = 16000
NOISE_FLOOR_SEC = 30.0  # length of the synthetic silence used for floor F


# ----- discipline -----

def _assert_env() -> None:
    if sys.executable != "/usr/bin/python3":
        raise RuntimeError(
            f"interpreter guard: expected /usr/bin/python3, got {sys.executable}"
        )
    for k, v in (("PYTHONHASHSEED", "0"), ("TZ", "UTC"), ("LC_ALL", "C.UTF-8")):
        if os.environ.get(k) != v:
            raise RuntimeError(f"env-pin: {k}={os.environ.get(k)!r} not {v!r}")
    if os.environ.get("TF_ENABLE_ONEDNN_OPTS") != "0":
        raise RuntimeError("TF_ENABLE_ONEDNN_OPTS must be 0 for byte-det VGGish")


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ----- audio -----

def _load_mono_16k(mp3_path: Path):
    import librosa
    import numpy as np
    y, _ = librosa.load(str(mp3_path), sr=SR, mono=True)
    return np.ascontiguousarray(y, dtype=np.float32)


def _window_indices(n_samples: int):
    """Return list of (start, end) sample indices for 10s windows @ 5s hop."""
    win = int(round(WINDOW_S * SR))
    hop = int(round(HOP_S * SR))
    idx = []
    s = 0
    while s + win <= n_samples:
        idx.append((s, s + win))
        s += hop
    return idx


# ----- VGGish backbone -----

_VGGISH_MODEL = None


def _load_vggish():
    global _VGGISH_MODEL
    if _VGGISH_MODEL is not None:
        return _VGGISH_MODEL
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import tensorflow_hub as hub
        _VGGISH_MODEL = hub.load("https://tfhub.dev/google/vggish/1")
    return _VGGISH_MODEL


def _embed_window(y):
    import numpy as np
    m = _load_vggish()
    frames = m(y).numpy()  # (n_frames, 128); frame stride ~0.96s @ 16kHz
    if frames.ndim == 1:
        return frames.astype(np.float64)
    return frames.mean(axis=0).astype(np.float64)


def _embed_song(y):
    """Return per-window mean-pooled VGGish embeddings for one song."""
    import numpy as np
    idx = _window_indices(len(y))
    if not idx:
        return np.zeros((0, 128), dtype=np.float64)
    embs = []
    for (s, e) in idx:
        embs.append(_embed_window(y[s:e]))
    return np.vstack(embs)


def _normalize_rows(m):
    import numpy as np
    norm = np.linalg.norm(m, axis=1, keepdims=True) + 1e-12
    return m / norm


def _song_stat(cand_emb, exemplar_emb):
    """Similarity = for each candidate window, max cosine over EXEMPLAR windows.

    Song statistic = mean of the best 50% windows (rewards strong stretches,
    tolerates intros/outros).
    """
    import numpy as np
    if cand_emb.shape[0] == 0 or exemplar_emb.shape[0] == 0:
        return 0.0
    a = _normalize_rows(cand_emb)
    b = _normalize_rows(exemplar_emb)
    sims = a @ b.T  # (n_cand, n_exem)
    per_win = sims.max(axis=1)  # (n_cand,)
    order = np.argsort(per_win)[::-1]
    k = max(1, len(per_win) // 2)
    top = per_win[order[:k]]
    return float(top.mean())


def _linear_calibration(exemplar_stats_loo, floor_stat):
    """score = 1 + 6*(s - F)/(E - F), clipped [1,7]."""
    import numpy as np
    E = float(np.mean(list(exemplar_stats_loo.values())))
    F = float(floor_stat)
    def _map(s):
        if E <= F:
            return 1.0
        v = 1.0 + 6.0 * (float(s) - F) / (E - F)
        return round(max(1.0, min(7.0, v)), 4)
    return _map, E, F


# ----- driver -----

def run_ear(repo_root: Path, out_dir: Path) -> dict:
    _assert_env()
    import numpy as np
    out_dir.mkdir(parents=True, exist_ok=True)

    # exemplar audio SHAs + embeddings
    ex_meta = []
    ex_embs = {}
    for short_id, name, band, rel in EXEMPLARS:
        p = repo_root / rel
        sha = _sha256_file(p)
        y = _load_mono_16k(p)
        emb = _embed_song(y)
        ex_embs[short_id] = emb
        ex_meta.append({"short_id": short_id, "name": name, "band": band,
                        "path": rel, "audio_sha256": sha,
                        "n_windows": int(emb.shape[0]),
                        "duration_s": round(len(y) / SR, 3)})

    # leave-one-out per exemplar: statistic vs pool of the other 4
    exemplar_stats_loo = {}
    for short_id, _, _, _ in EXEMPLARS:
        pool = np.vstack([ex_embs[k] for k in ex_embs if k != short_id])
        exemplar_stats_loo[short_id] = _song_stat(ex_embs[short_id], pool)

    # noise-floor F: 30s of digital silence
    silence = np.zeros(int(NOISE_FLOOR_SEC * SR), dtype=np.float32)
    silence_emb = _embed_song(silence)
    all_ex = np.vstack([ex_embs[k] for k in ex_embs])
    floor_stat = _song_stat(silence_emb, all_ex)

    # calibration
    mapper, E, F = _linear_calibration(exemplar_stats_loo, floor_stat)
    exemplar_scores = {k: mapper(s) for k, s in exemplar_stats_loo.items()}

    # band-4 spot check (3 songs)
    b4_meta = []
    b4_scores = []
    b4_stats = []
    for short_id, name, rel in BAND_4_SPOT_CHECK:
        p = repo_root / rel
        sha = _sha256_file(p)
        y = _load_mono_16k(p)
        emb = _embed_song(y)
        s = _song_stat(emb, all_ex)
        b4_stats.append({"short_id": short_id, "name": name,
                         "path": rel, "audio_sha256": sha,
                         "statistic": round(float(s), 6),
                         "n_windows": int(emb.shape[0]),
                         "score_1_7": mapper(s)})
        b4_scores.append(mapper(s))
        b4_meta.append({"short_id": short_id, "name": name,
                        "audio_sha256": sha})

    # sanity: >=4 of 5 exemplars >= 6 leave-one-out; none below 5.5
    ex_score_vals = list(exemplar_scores.values())
    sanity = {
        "n_ex_at_or_above_6": sum(1 for v in ex_score_vals if v >= 6.0),
        "n_ex_below_5p5": sum(1 for v in ex_score_vals if v < 5.5),
        "operator_sanity_bar_passes": (
            sum(1 for v in ex_score_vals if v >= 6.0) >= 4
            and all(v >= 5.5 for v in ex_score_vals)
        ),
        "band_4_max_score": max(b4_scores) if b4_scores else None,
        "band_4_min_score": min(b4_scores) if b4_scores else None,
        "band_4_below_exemplar_min": (
            (max(b4_scores) if b4_scores else 7.0)
            < min(ex_score_vals)
        ),
    }

    # save embeddings (npz) for reproducibility auditing
    ex_np_path = out_dir / "exemplar_embeddings.npz"
    np.savez(str(ex_np_path), **{k: v for k, v in ex_embs.items()})
    ex_np_sha = _sha256_file(ex_np_path)

    cand_np_path = out_dir / "band4_embeddings.npz"
    # we recompute; store b4 embeddings
    b4_embs = {}
    for short_id, name, rel in BAND_4_SPOT_CHECK:
        y = _load_mono_16k(repo_root / rel)
        b4_embs[short_id] = _embed_song(y)
    np.savez(str(cand_np_path), **{k: v for k, v in b4_embs.items()})
    b4_np_sha = _sha256_file(cand_np_path)

    # scores JSON
    scores = {
        "schema_v": 1,
        "milestone_id": "M-V4-EAR-1",
        "backbone_selected": "vggish",
        "backbone_ensemble_planned": "clap+vggish (CLAP unavailable via egress)",
        "backbone_fallback_note": (
            "CLAP install fails on this system (torchvision::nms missing per "
            "data/texture/embedding_rung.log). Per spec §backbone, "
            "fallback to VGGish-only recorded here."
        ),
        "vggish_source": "https://tfhub.dev/google/vggish/1",
        "vggish_frame_s": 0.96,
        "vggish_dim": 128,
        "window_s": WINDOW_S,
        "hop_s": HOP_S,
        "sample_rate": SR,
        "top_k_policy": "mean of best 50% of candidate windows",
        "calibration_E_mean_loo": round(E, 6),
        "calibration_F_noise_floor_stat": round(F, 6),
        "calibration_formula": "score = 1 + 6*(s - F)/(E - F), clipped [1,7]",
        "exemplars": ex_meta,
        "exemplar_stats_loo": {k: round(v, 6) for k, v in exemplar_stats_loo.items()},
        "exemplar_scores_1_7": exemplar_scores,
        "band_4_spot_check": b4_stats,
        "sanity": sanity,
        "env_pin_sha256": CANONICAL_ENV_PIN_SHA,
        "TF_ENABLE_ONEDNN_OPTS": os.environ.get("TF_ENABLE_ONEDNN_OPTS"),
        "ts": "2026-09-04T07:30:00Z",
    }
    scores_path = out_dir / "ear_scores.json"
    scores_path.write_text(_canonical_json(scores), encoding="ascii")

    # env_pin
    env_pin = {
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "SOURCE_DATE_EPOCH": os.environ.get("SOURCE_DATE_EPOCH"),
        "TZ": os.environ.get("TZ"),
        "LC_ALL": os.environ.get("LC_ALL"),
        "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS", "1"),
        "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS", "1"),
        "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS", "1"),
    }
    env_json = _canonical_json(env_pin)
    env_sha = hashlib.sha256(env_json.encode("ascii")).hexdigest()
    (out_dir / "env_pin.json").write_text(env_json, encoding="ascii")

    manifest = {
        "schema_v": 1,
        "milestone_id": "M-V4-EAR-1",
        "backbone_selected": "vggish",
        "clap_available": False,
        "clap_error": "torchvision::nms missing (documented in data/texture/embedding_rung.log)",
        "env_pin_sha256_from_extractor": env_sha,
        "env_pin_matches_canonical": env_sha == CANONICAL_ENV_PIN_SHA,
        "artifacts": {
            "ear_scores.json": {"sha256": _sha256_file(scores_path)},
            "exemplar_embeddings.npz": {"sha256": ex_np_sha},
            "band4_embeddings.npz": {"sha256": b4_np_sha},
            "env_pin.json": {"sha256": env_sha},
        },
        "ts": "2026-09-04T07:30:00Z",
    }
    manifest_json = _canonical_json(manifest)
    (out_dir / "manifest.json").write_text(manifest_json, encoding="ascii")

    return {
        "ear_scores_sha256": _sha256_file(scores_path),
        "manifest_sha256": hashlib.sha256(manifest_json.encode("ascii")).hexdigest(),
        "env_pin_sha256": env_sha,
        "env_pin_matches_canonical": env_sha == CANONICAL_ENV_PIN_SHA,
        "sanity": sanity,
        "exemplar_scores_1_7": exemplar_scores,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    args = ap.parse_args()
    result = run_ear(args.repo_root.resolve(), args.out_dir.resolve())
    sys.stdout.write(_canonical_json(result) + "\n")


if __name__ == "__main__":
    _assert_env()
    main()
