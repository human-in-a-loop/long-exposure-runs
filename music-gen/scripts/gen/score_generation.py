#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:20:00Z
# cycle: 10
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 00b3ae64444c)
# milestone: M-GEN-1/first-generation
# ---
"""Score a generated clip: heuristics battery + meta-tracker + M-TEX-1/panel + ear prediction.

    score(effects_wav, bare_wav, out_json) -> None

Writes a scoring_v1.json with:
  * heuristics: 4-key dict of {mess_scale, raw_features, reason, blind_spots}
  * meta_tracker: descriptors for a single anchored 30 s clip (weight=1.0)
  * texture_panel: 8-key M-TEX-1/panel result between (bare, effects)
  * ear:
      - feature_shape, panns_sha, heur_sha, feat_hash
      - prediction: int 1..7 (predicted rating from the CORN head)
      - calibration: "synthetic_labels_only" sentinel
      - baselines: majority-class and mean-integer references

The CORN head is trained fresh each run on the M-CLASS-1 valset synthetic
labels (deterministic seed=0) and used to predict on our generated clip's
feature vector. This is a PIPELINE-signal, NOT a musical judgment — the
calibration sentinel is included and the report surfaces this loudly.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

# Pins before any heavy import
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

assert sys.executable == "/usr/bin/python3", sys.executable

import numpy as np


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _serialize_heuristic(hr) -> dict:
    return {
        "name": hr.name,
        "mess_scale": (None if hr.mess_scale is None else float(hr.mess_scale)),
        "raw_features": {k: (None if v is None or (isinstance(v, float) and not np.isfinite(v)) else float(v))
                         for k, v in dict(hr.raw_features).items()},
        "reason": hr.reason,
        "blind_spots": list(hr.blind_spots),
    }


def _run_heuristics(wav_path: Path) -> dict:
    from scripts.heuristics.battery import run_battery, load_clip
    y, sr = load_clip(Path(wav_path), target_sr=22050)
    results = run_battery(y, sr)
    return {k: _serialize_heuristic(v) for k, v in results.items()}


def _run_meta_tracker_single_clip(heuristic_dict: dict, wav_path: Path) -> dict:
    """Single-clip anchored-tail reduction (weight=1.0).

    The M-HEUR-1 meta-tracker was designed for multi-clip anchored-tail
    inputs. On a single 30 s generated clip the anchored-tail weight
    trivially collapses to 1.0 and heuristic_variance_across_clips is
    exactly 0 by construction. Rather than fabricating variance from a
    single sample, we compute:
      * anchored_tail_weight: 1.0 (single clip, no prev)
      * heuristic_variance_across_clips: 0.0 (single sample)
      * peak_location_fraction: t of max-|amplitude| divided by duration
      * form_coherence: chroma-CQT SSM ratio on the source WAV (via
        _song_form_coherence).
      * dynamics_trajectory: single-clip RMS envelope range in dB.
    """
    import librosa
    from scripts.heuristics.meta_tracker import _song_form_coherence  # type: ignore
    y, sr = librosa.load(str(wav_path), sr=22050, mono=True)
    peak_idx = int(np.argmax(np.abs(y)))
    duration = max(1e-9, len(y) / sr)
    peak_fraction = float(peak_idx / max(1, len(y)))
    # dynamics trajectory: single-window RMS envelope range in dB.
    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    rms = rms[rms > 0]
    if len(rms) >= 2:
        env_db = 20.0 * np.log10(rms)
        dyn_range_db = float(np.percentile(env_db, 95) - np.percentile(env_db, 5))
    else:
        dyn_range_db = float("nan")
    try:
        form_coh = _song_form_coherence(Path(wav_path), sr_target=22050)
    except Exception as exc:
        form_coh = None

    return {
        "anchored_tail_weight": 1.0,
        "heuristic_variance_across_clips": 0.0,
        "peak_location_fraction": peak_fraction,
        "dynamics_trajectory_db": dyn_range_db,
        "form_coherence": (None if form_coh is None or not np.isfinite(form_coh) else float(form_coh)),
        "n_clips_input": 1,
        "single_clip_reduction_note": (
            "single 30 s generated clip → anchored-tail weight=1.0 and "
            "variance-across-clips=0 by construction; descriptors reduce "
            "to per-clip measurements."
        ),
    }


def _run_texture_panel(bare_wav: Path, fx_wav: Path) -> dict:
    import soundfile as sf
    from scripts.texture.panel import texture_distance
    a, sr_a = sf.read(str(bare_wav), always_2d=True)
    b, sr_b = sf.read(str(fx_wav), always_2d=True)
    if sr_a != sr_b:
        raise RuntimeError(f"SR mismatch bare={sr_a} fx={sr_b}")
    return texture_distance(a, b, sr_a)


def _ear_predict(effects_wav: Path) -> dict:
    """Extract features on our clip; train CORN head on valset synthetic labels; predict."""
    from scripts.ear.features import extract_features, sha256_of
    from scripts.ear.model import (
        _load_valset_features, synthesize_ratings, set_determinism, _fit
    )
    # 1. Extract features on our generated clip (no VGGish → 2052-D feature vector)
    clip_id = f"gen_first_gen_{sha256_of(Path(effects_wav))[:16]}"
    row = extract_features(clip_id, Path(effects_wav), use_vggish=False, force=True)
    x = np.concatenate([row.panns_embed, row.heuristic_vec], axis=0).astype(np.float32)

    # 2. Train CORN on valset with synthetic labels (deterministic, seed=0).
    valset_manifest = Path("data/classifier/valset/valset_manifest.tsv")
    clips_dir = Path("data/classifier/valset/clips")
    X, ids, labels = _load_valset_features(clips_dir, valset_manifest)
    y = synthesize_ratings(X, seed=0)
    set_determinism(0)
    # Fit on full set (single-fold prediction on our OOD generated clip).
    x_ = x.reshape(1, -1)
    # NaN-guard on features (heuristic nulls → column-mean impute).
    Xt = X.astype(np.float32).copy()
    col_mean = np.nanmean(Xt, axis=0)
    for j in range(Xt.shape[1]):
        m = np.isnan(Xt[:, j])
        Xt[m, j] = 0.0 if not np.isfinite(col_mean[j]) else col_mean[j]
    xg = x_.copy()
    for j in range(xg.shape[1]):
        if np.isnan(xg[0, j]):
            xg[0, j] = 0.0 if not np.isfinite(col_mean[j]) else col_mean[j]
    pred = _fit(Xt, y, xg, np.array([0], dtype=np.int64), seed=0, epochs=200)
    pred_int = int(pred[0])

    # 3. Baselines (for context in the report; NOT calibrated).
    from collections import Counter
    cnt = Counter(y.tolist())
    majority = int(sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[0][0])
    mean_int = int(round(float(np.mean(y))))

    return {
        "prediction": pred_int,
        "calibration": "synthetic_labels_only",
        "calibration_note": (
            "CORN head trained on M-EAR-1/preparation synthetic labels "
            "(deterministic PC-1 driven, seed=0) from the M-CLASS-1 55-clip "
            "valset. The 1-7 output is a functional-pipeline signal, NOT a "
            "musical quality judgment. Real calibration is gated on rated "
            "audio arrival (M-INGEST-1/egress-ready-automation triggers)."
        ),
        "feature_dim": int(x.shape[0]),
        "feature_version": "ear-features-v1",
        "n_valset_train": int(X.shape[0]),
        "majority_class": majority,
        "mean_int_baseline": mean_int,
        "clip_id": clip_id,
        "clip_feat_hash": row.feat_hash,
        "clip_source_wav_sha256": row.source_wav_sha256,
    }


def score(bare_wav: Path, effects_wav: Path, out_json: Path) -> None:
    bare_wav = Path(bare_wav); effects_wav = Path(effects_wav); out_json = Path(out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)

    result = {
        "milestone": "M-GEN-1/first-generation",
        "inputs": {
            # Only basenames stored — full paths would break byte-determinism
            # across runs invoked from different working directories.
            "bare_wav_basename": bare_wav.name,
            "effects_wav_basename": effects_wav.name,
            "bare_wav_sha256": _sha256(bare_wav),
            "effects_wav_sha256": _sha256(effects_wav),
        },
        "heuristics": _run_heuristics(effects_wav),
        "texture_panel_bare_vs_effects": _run_texture_panel(bare_wav, effects_wav),
        "ear": _ear_predict(effects_wav),
    }
    # meta-tracker after heuristics (uses same wav)
    result["meta_tracker_single_clip"] = _run_meta_tracker_single_clip(
        result["heuristics"], effects_wav)

    # Canonical JSON for byte-determinism.
    text = json.dumps(result, indent=2, sort_keys=True, allow_nan=False,
                      default=lambda o: None if (isinstance(o, float) and not np.isfinite(o)) else str(o))
    out_json.write_text(text)


def _main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--bare-wav", type=Path, default=Path("data/gen/renders/bare_midi.wav"))
    ap.add_argument("--effects-wav", type=Path, default=Path("data/gen/renders/effects_layered.wav"))
    ap.add_argument("--out", type=Path, default=Path("data/gen/scoring_v1.json"))
    args = ap.parse_args(argv)
    score(args.bare_wav, args.effects_wav, args.out)
    print(f"[score_generation] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
