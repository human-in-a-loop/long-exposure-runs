# meta_tracker — intra-song macro descriptors, honors anchored-tail debias
# created: 2026-08-28T05:20:00Z  cycle: 4  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1)  milestone: M-HEUR-1/meta-tracker
"""Intra-song meta-heuristic tracker.

Consumes: ingestion manifest JSONL + per-clip battery TSV output.
Emits four macro descriptors:

- dynamics_trajectory        — weighted-least-squares slope of the
                                clip-level envelope_range_ratio vs. clip midpoint
                                (units: mess_scale / second, sign preserved).
- form_coherence             — chroma-CQT SSM diagonal-band ratio computed on
                                the WHOLE original source audio (not concatenated
                                clips — that would double-count overlap).
- peak_location_fraction     — argmax(clip-weight-adjusted total mess-vector L1)
                                clip midpoint / song duration, in [0, 1].
- heuristic_variance_across_clips — weighted variance of the per-clip 4-vector
                                     L2 norm across clips.

Anchored-tail debias: for a clip with anchored_tail=true, weight is
`(30.0 - actual_overlap_s) / 30.0` where
`actual_overlap_s = prev_clip.t_end_s - this_clip.t_start_s`.
All non-anchored clips get weight 1.0. short_song=true clips also get 1.0.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import librosa
import numpy as np

STANDARD_CLIP_S = 30.0
BLOCK_S = 4.0


def anchored_tail_weight(prev_t_end_s: float, this_t_start_s: float) -> float:
    overlap = prev_t_end_s - this_t_start_s
    if overlap <= 0:
        return 1.0
    w = (STANDARD_CLIP_S - overlap) / STANDARD_CLIP_S
    return max(0.0, min(1.0, w))


def clip_weights(clip_rows: list[dict]) -> list[float]:
    """Assign a weight per clip. clip_rows must be sorted by clip_index."""
    weights: list[float] = []
    for i, r in enumerate(clip_rows):
        short = bool(r.get("short_song", False))
        anchored = bool(r.get("anchored_tail", False))
        if short or not anchored:
            weights.append(1.0)
        else:
            prev = clip_rows[i - 1]
            weights.append(anchored_tail_weight(prev["t_end_s"], r["t_start_s"]))
    return weights


def _weighted_stats(values: np.ndarray, weights: np.ndarray) -> tuple[float, float]:
    w = weights
    s = w.sum()
    if s <= 0:
        return float("nan"), float("nan")
    mean = float((values * w).sum() / s)
    var = float((w * (values - mean) ** 2).sum() / s)
    return mean, var


def _weighted_regression(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> float:
    """Slope of weighted linear regression y ~ a + b*x."""
    s = w.sum()
    if s <= 0 or len(x) < 2:
        return float("nan")
    xw = (x * w).sum() / s
    yw = (y * w).sum() / s
    num = (w * (x - xw) * (y - yw)).sum()
    den = (w * (x - xw) ** 2).sum()
    if den <= 0:
        return float("nan")
    return float(num / den)


def _song_form_coherence(source_path: Path, sr_target: int = 22050) -> float:
    y, sr = librosa.load(str(source_path), sr=sr_target, mono=True)
    if y.size == 0:
        return float("nan")
    hop = 512
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
    frames_per_block = max(1, int(round(BLOCK_S * sr / hop)))
    n_full = chroma.shape[1] // frames_per_block
    if n_full < 3:
        return float("nan")
    trimmed = chroma[:, : n_full * frames_per_block]
    blocks = trimmed.reshape(12, n_full, frames_per_block).mean(axis=2)
    norms = np.linalg.norm(blocks, axis=0, keepdims=True) + 1e-12
    blocks = blocks / norms
    ssm = blocks.T @ blocks
    n = ssm.shape[0]
    idx = np.arange(n)
    ii, jj = np.meshgrid(idx, idx, indexing="ij")
    band_mask = np.abs(ii - jj) <= 1
    diag_mean = float(ssm[band_mask].mean())
    off_mean = float(ssm[~band_mask].mean()) if (~band_mask).any() else float("nan")
    if off_mean <= 0 or math.isnan(off_mean):
        return float("nan")
    return diag_mean / off_mean


def run_meta_tracker(manifest_path: Path, battery_tsv_path: Path) -> dict:
    """Combine manifest + per-clip battery output into 4 macro descriptors."""
    with manifest_path.open() as f:
        rows = [json.loads(line) for line in f if line.strip()]
    source = [r for r in rows if r["kind"] == "source"][0]
    clips = sorted([r for r in rows if r["kind"] == "clip"], key=lambda r: r["clip_index"])

    # Parse battery TSV
    import csv
    with battery_tsv_path.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        battery_rows = list(reader)
    by_idx = {int(b["clip_index"]): b for b in battery_rows}

    weights = clip_weights(clips)
    midpoints = np.array([(c["t_start_s"] + c["t_end_s"]) / 2.0 for c in clips])
    wt = np.array(weights)

    # dynamics_trajectory — regress dynamics envelope_range_ratio (raw) over time
    dyn_range = []
    for c in clips:
        b = by_idx[c["clip_index"]]
        v = b.get("dynamics__raw__envelope_range_ratio", "")
        dyn_range.append(float(v) if v != "" else float("nan"))
    dyn_range_arr = np.array(dyn_range)
    valid = np.isfinite(dyn_range_arr)
    if valid.sum() >= 2:
        slope = _weighted_regression(midpoints[valid], dyn_range_arr[valid], wt[valid])
    else:
        slope = float("nan")

    # form_coherence — song-level SSM on the source audio
    source_path = Path(source["source_ref"])
    form_coh = _song_form_coherence(source_path)

    # peak_location_fraction — weight-adjusted mess-vector total
    per_clip_totals = []
    for c in clips:
        b = by_idx[c["clip_index"]]
        parts = []
        for h in ("melody", "timbre", "form", "dynamics"):
            v = b.get(f"{h}__mess_scale", "")
            if v == "":
                continue
            parts.append(float(v))
        per_clip_totals.append(sum(parts))
    totals_arr = np.array(per_clip_totals) * wt
    if totals_arr.size and np.any(totals_arr > 0):
        peak_idx = int(np.argmax(totals_arr))
        peak_frac = float(midpoints[peak_idx] / source["duration_s"])
    else:
        peak_frac = float("nan")

    # heuristic_variance_across_clips — weighted variance of the L2 norm of
    # the per-clip mess vector.
    l2 = []
    for c in clips:
        b = by_idx[c["clip_index"]]
        acc = 0.0
        for h in ("melody", "timbre", "form", "dynamics"):
            v = b.get(f"{h}__mess_scale", "")
            if v == "":
                continue
            fv = float(v)
            acc += fv * fv
        l2.append(math.sqrt(acc))
    l2_arr = np.array(l2)
    _, l2_var = _weighted_stats(l2_arr, wt)

    return {
        "source_id": source["source_id"],
        "source_ref": source["source_ref"],
        "duration_s": source["duration_s"],
        "n_clips": len(clips),
        "clip_weights": [float(w) for w in weights],
        "clip_midpoints_s": [float(x) for x in midpoints.tolist()],
        "dynamics_trajectory": None if math.isnan(slope) else float(slope),
        "dynamics_trajectory_units": "envelope_range_ratio per second",
        "form_coherence": None if math.isnan(form_coh) else float(form_coh),
        "form_coherence_note": "song-scale chroma-CQT SSM diagonal-band ratio on original source (not concatenated clips)",
        "peak_location_fraction": None if math.isnan(peak_frac) else float(peak_frac),
        "heuristic_variance_across_clips": None if math.isnan(l2_var) else float(l2_var),
        "anchored_tail_formula": "weight = max(0, (30.0 - overlap_s) / 30.0)",
    }
