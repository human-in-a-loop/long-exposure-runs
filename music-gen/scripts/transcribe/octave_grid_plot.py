"""Heatmap generator for M-TRANS-1/basic-pitch/octave-suppression grid.

Reads ``data/transcribe/octave_suppression/grid_search.tsv`` and writes
``data/transcribe/octave_suppression/heatmap.png`` — three 3×3 heatmaps
(bass F1 uplift / drums F1 delta / other F1 delta) side by side,
x=overlap_min, y=T_min_ms. Cell text overlays the numeric value.

Aggregate-across-mixes only.  Deterministic (no RNG).

Interpreter: /usr/bin/python3.
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"wrong interpreter: {sys.executable}"

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path("/home/user/long-exposure-runs/music-gen")
IN_TSV = ROOT / "data/transcribe/octave_suppression/grid_search.tsv"
OUT_PNG = ROOT / "data/transcribe/octave_suppression/heatmap.png"

T_MIN_GRID = [50, 100, 200]
OVERLAP_MIN_GRID = [0.3, 0.5, 0.7]


def _load_aggregate() -> dict[tuple[int, float], dict[str, float]]:
    out: dict[tuple[int, float], dict[str, float]] = {}
    with IN_TSV.open() as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            if row["mix_id"] != "aggregate":
                continue
            if row["T_min_ms"] == "baseline":
                continue
            key = (int(row["T_min_ms"]), float(row["overlap_min"]))
            out[key] = {
                "bass_uplift": float(row["bass_F1_uplift"]),
                "drums_delta": float(row["drums_F1_delta"]),
                "other_delta": float(row["other_F1_delta"]),
                "passes": row["passes_harmless"] == "True",
            }
    return out


def _build_matrix(data, field: str) -> np.ndarray:
    m = np.zeros((len(T_MIN_GRID), len(OVERLAP_MIN_GRID)))
    for i, t in enumerate(T_MIN_GRID):
        for j, o in enumerate(OVERLAP_MIN_GRID):
            m[i, j] = data[(t, o)][field]
    return m


def _panel(ax, matrix: np.ndarray, title: str, cmap: str, vmin: float, vmax: float) -> None:
    im = ax.imshow(matrix, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(OVERLAP_MIN_GRID)))
    ax.set_xticklabels([f"{o:.1f}" for o in OVERLAP_MIN_GRID])
    ax.set_yticks(range(len(T_MIN_GRID)))
    ax.set_yticklabels([f"{t}" for t in T_MIN_GRID])
    ax.set_xlabel("overlap_min")
    ax.set_ylabel("T_min_ms")
    ax.set_title(title)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i, j]
            ax.text(j, i, f"{val:+.3f}", ha="center", va="center",
                    color="black" if abs(val) < 0.15 else "white", fontsize=9)
    plt.colorbar(im, ax=ax, shrink=0.7)


def main() -> None:
    data = _load_aggregate()
    m_bass = _build_matrix(data, "bass_uplift")
    m_drums = _build_matrix(data, "drums_delta")
    m_other = _build_matrix(data, "other_delta")

    # Symmetric range for the delta panels; positive-favoring for bass.
    lim = max(0.05, float(np.abs(np.concatenate([m_drums.flat, m_other.flat])).max()))
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    _panel(axes[0], m_bass, "bass F1 uplift", "viridis",
           vmin=min(-0.05, float(m_bass.min())), vmax=max(0.4, float(m_bass.max())))
    _panel(axes[1], m_drums, "drums F1 Δ", "RdBu_r", vmin=-lim, vmax=lim)
    _panel(axes[2], m_other, "other F1 Δ", "RdBu_r", vmin=-lim, vmax=lim)

    fig.suptitle(
        "M-TRANS-1/basic-pitch/octave-suppression — aggregate across 3 mixes"
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    # Fix matplotlib metadata for byte-determinism of the PNG.
    os.environ.setdefault("SOURCE_DATE_EPOCH", "0")
    fig.savefig(OUT_PNG, dpi=110, metadata={"Software": "matplotlib"})
    print(f"wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
