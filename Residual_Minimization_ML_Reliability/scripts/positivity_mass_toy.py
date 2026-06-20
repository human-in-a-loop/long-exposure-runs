# created: 2026-05-14T16:05:00Z
# cycle: 52
# run_id: run-2026-05-14T030813Z
# agent: worker
# milestone: M-9
"""M-9 toy: aggregate mass residual misses positivity admissibility."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_PATH = DATA / "positivity_mass_toy.csv"
PNG_PATH = DATA / "positivity_mass_toy.png"


def positivity_certificate(c1: float, c2: float) -> float:
    return max(0.0, -c1) ** 2 + max(0.0, -c2) ** 2


def mass_objective(c1: float, c2: float, mass_derivative: float = 0.0) -> float:
    return mass_derivative**2 + (c1 + c2 - 1.0) ** 2


def classify(c1: float, c2: float) -> str:
    if c1 >= 0.0 and c2 >= 0.0 and abs(c1 + c2 - 1.0) < 1e-12:
        return "admissible_simplex_state"
    if c1 + c2 == 1.0:
        return "mass_correct_but_negative"
    return "mass_or_positivity_violation"


def build_rows() -> list[dict[str, float | str]]:
    states = [
        ("good_equal_split", 0.5, 0.5),
        ("positivity_boundary_c1_zero", 0.0, 1.0),
        ("positivity_boundary_c2_zero", 1.0, 0.0),
        ("bad_negative_c2", 1.5, -0.5),
        ("bad_negative_c1", -0.25, 1.25),
    ]
    rows: list[dict[str, float | str]] = []
    for name, c1, c2 in states:
        certificate = positivity_certificate(c1, c2)
        objective = mass_objective(c1, c2)
        rows.append(
            {
                "case": name,
                "c1": c1,
                "c2": c2,
                "mass": c1 + c2,
                "mass_derivative": 0.0,
                "aggregate_residual": objective,
                "positivity_certificate": certificate,
                "minimum_concentration": min(c1, c2),
                "classification": classify(c1, c2),
            }
        )
    return rows


def write_csv(rows: list[dict[str, float | str]], path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "case",
        "c1",
        "c2",
        "mass",
        "mass_derivative",
        "aggregate_residual",
        "positivity_certificate",
        "minimum_concentration",
        "classification",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def plot_rows(rows: list[dict[str, float | str]], path: Path = PNG_PATH) -> None:
    labels = [str(row["case"]).replace("_", "\n") for row in rows]
    residual = [float(row["aggregate_residual"]) for row in rows]
    certificate = [float(row["positivity_certificate"]) for row in rows]
    minimum = [float(row["minimum_concentration"]) for row in rows]
    x = range(len(rows))

    fig, axes = plt.subplots(2, 1, figsize=(7.4, 5.6), constrained_layout=True, sharex=True)
    axes[0].bar([i - 0.18 for i in x], residual, width=0.36, label="aggregate mass residual")
    axes[0].bar([i + 0.18 for i in x], certificate, width=0.36, label="positivity certificate")
    axes[0].set_ylabel("value")
    axes[0].set_title(
        "Aggregate conservation residual is zero for both admissible and negative-concentration states; "
        "positivity certificate separates them."
    )
    axes[0].legend(fontsize=8)
    axes[0].grid(True, axis="y", alpha=0.25)

    axes[1].bar(x, minimum, color=["#4c78a8" if value >= 0.0 else "#d62728" for value in minimum])
    axes[1].axhline(0.0, color="0.25", linewidth=1.0)
    axes[1].set_ylabel("min concentration")
    axes[1].set_xticks(list(x), labels, rotation=0, fontsize=8)
    axes[1].grid(True, axis="y", alpha=0.25)

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
