# created: 2026-05-14T15:20:00Z
# cycle: 51
# run_id: run-2026-05-14T030813Z
# agent: worker
# milestone: M-11
"""CAT-15 toy: homogeneous eigen-residual does not select amplitude."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_PATH = DATA / "eigenmode_normalization.csv"
PNG_PATH = DATA / "eigenmode_normalization.png"
NORMALIZED_AMPLITUDE = math.sqrt(2.0 / math.pi)


def eigenmode_values(amplitude: float) -> dict[str, float | str]:
    l2_norm_sq = amplitude**2 * math.pi / 2.0
    physical_l2_error = abs(amplitude - NORMALIZED_AMPLITUDE) * math.sqrt(math.pi / 2.0)
    return {
        "case": "amplitude_null_family",
        "amplitude": amplitude,
        "target_amplitude": NORMALIZED_AMPLITUDE,
        "eigen_residual_l2_sq": 0.0,
        "boundary_penalty": 0.0,
        "objective_without_normalization": 0.0,
        "physical_l2_error": physical_l2_error,
        "l2_norm_sq": l2_norm_sq,
        "normalization_certificate": (l2_norm_sq - 1.0) ** 2,
        "classification": "normalization_failure",
    }


def build_rows(amplitudes: list[float] | None = None) -> list[dict[str, float | str]]:
    if amplitudes is None:
        amplitudes = [0.0, 0.1, 0.25, 0.5, NORMALIZED_AMPLITUDE, 0.9, 1.0, 1.25]
    return [eigenmode_values(amplitude) for amplitude in amplitudes]


def write_csv(rows: list[dict[str, float | str]], path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "case",
        "amplitude",
        "target_amplitude",
        "eigen_residual_l2_sq",
        "boundary_penalty",
        "objective_without_normalization",
        "physical_l2_error",
        "l2_norm_sq",
        "normalization_certificate",
        "classification",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def plot_rows(rows: list[dict[str, float | str]], path: Path = PNG_PATH) -> None:
    amplitudes = [float(row["amplitude"]) for row in rows]
    residual = [float(row["objective_without_normalization"]) for row in rows]
    error = [float(row["physical_l2_error"]) for row in rows]
    certificate = [float(row["normalization_certificate"]) for row in rows]

    fig, ax = plt.subplots(figsize=(6.8, 4.2), constrained_layout=True)
    ax.plot(amplitudes, residual, "o-", label="eigen-residual objective")
    ax.plot(amplitudes, error, "s--", label=r"physical error to normalized $\sin x$")
    ax.plot(amplitudes, certificate, "^-", label="normalization certificate")
    ax.axvline(NORMALIZED_AMPLITUDE, color="0.35", linestyle=":", label="target amplitude")
    ax.set_xlabel("amplitude a in u_a(x)=a sin(x)")
    ax.set_ylabel("value")
    ax.set_title("Eigen-residual is zero for all amplitudes, while normalization detects the physically wrong zero mode.")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    write_csv(rows)
    plot_rows(rows)
    print(f"wrote {CSV_PATH}")
    print(f"wrote {PNG_PATH}")


if __name__ == "__main__":
    main()
