# form_quality — mess-scale [0,1] via chroma-CQT SSM diagonal-band ratio
# created: 2026-08-28T05:20:00Z  cycle: 4  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1)  milestone: M-HEUR-1/form
"""Form heuristic (clip-level).

Computes a chroma-CQT self-similarity matrix, block-averages to ~4s cells,
and reports the ratio of diagonal-band energy to off-diagonal energy.

Null-with-reason: len(y)/sr < 30.0 → mess_scale=None, reason="too_short_for_ssm".
"""
from __future__ import annotations

import librosa
import numpy as np

from .mess_scale import HeuristicResult, mess_scale


BLIND_SPOTS = (
    "heavily-repeating tracks (loops, minimalism) score falsely high — the SSM diagonal-band ratio just measures block self-similarity, not compositional intent.",
    "through-composed pieces (no repetition by design) score falsely low regardless of whether the form coheres at higher levels.",
    "the ~4s block granularity captures phrase-scale structure and misses both note-level texture (below 4s) and section-level form (repeats separated by >30s inside a single 30s clip are impossible).",
    "key modulation partway through a clip depresses chroma self-similarity even when the arrangement is otherwise repetitive.",
)

# Diagonal-to-off-diagonal ratio anchors (higher ratio = more structure)
DIAG_RATIO_ANCHORS = ((0.5, 0.0), (1.0, 0.3), (1.6, 0.7), (3.0, 1.0))

BLOCK_S = 4.0
MIN_CLIP_S = 30.0


def form_quality(y: np.ndarray, sr: int) -> HeuristicResult:
    np.random.seed(0)
    name = "form_quality"
    raw: dict = {
        "duration_s": None,
        "diag_off_ratio": None,
        "n_blocks": None,
    }
    if y.size == 0:
        return HeuristicResult(name, raw, None, "empty_audio", BLIND_SPOTS)
    dur_s = y.size / float(sr)
    raw["duration_s"] = dur_s
    if dur_s < MIN_CLIP_S:
        return HeuristicResult(name, raw, None, "too_short_for_ssm", BLIND_SPOTS)

    # Chroma-CQT at default hop; then block-average to BLOCK_S columns.
    hop = 512
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
    frames_per_block = max(1, int(round(BLOCK_S * sr / hop)))
    n_full = chroma.shape[1] // frames_per_block
    if n_full < 3:
        return HeuristicResult(name, raw, None, "too_few_ssm_blocks", BLIND_SPOTS)
    trimmed = chroma[:, : n_full * frames_per_block]
    blocks = trimmed.reshape(12, n_full, frames_per_block).mean(axis=2)  # (12, n_full)
    # Normalize columns to unit norm so SSM is cosine-similarity
    norms = np.linalg.norm(blocks, axis=0, keepdims=True) + 1e-12
    blocks = blocks / norms
    ssm = blocks.T @ blocks  # (n_full, n_full)

    n = ssm.shape[0]
    # Diagonal band width = 1 (i.e. immediate neighbours + main diag)
    idx = np.arange(n)
    ii, jj = np.meshgrid(idx, idx, indexing="ij")
    band_mask = np.abs(ii - jj) <= 1
    diag_mean = float(ssm[band_mask].mean())
    off_mean = float(ssm[~band_mask].mean()) if (~band_mask).any() else float("nan")
    if off_mean <= 0 or np.isnan(off_mean):
        return HeuristicResult(name, raw, None, "degenerate_off_diag", BLIND_SPOTS)
    ratio = diag_mean / off_mean
    raw["diag_off_ratio"] = ratio
    raw["n_blocks"] = float(n)
    m = mess_scale(ratio, DIAG_RATIO_ANCHORS)
    return HeuristicResult(name, raw, m, None, BLIND_SPOTS)
