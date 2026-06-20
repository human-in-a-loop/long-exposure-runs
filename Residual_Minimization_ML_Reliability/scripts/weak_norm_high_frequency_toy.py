# created: 2026-05-14T14:45:00Z
# cycle: 50
# run_id: run-2026-05-14T030813Z
# agent: worker
# milestone: M-8
"""CAT-06 toy: negative Sobolev objectives suppress high-frequency error."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_PATH = DATA / "weak_norm_scaling.csv"
PNG_PATH = DATA / "weak_norm_scaling.png"


def hminus_norm_sq_for_l2_normalized_mode(k: int, s: float) -> float:
    """Squared H^{-s} norm of an L2-normalized sine mode with frequency k."""
    return (1.0 + k * k) ** (-s)


def direct_weak_residual_values(k: int, s: float = 1.0) -> dict[str, float | int | str]:
    hminus_sq = hminus_norm_sq_for_l2_normalized_mode(k, s)
    return {
        "case": "direct_Hminus_failure",
        "k": k,
        "s": s,
        "objective": hminus_sq,
        "physical_l2_error": 1.0,
        "strong_l2_certificate": 1.0,
        "matched_stability_baseline": 0.0,
        "classification": "failure",
    }


def elliptic_matched_negative_control_values(k: int) -> dict[str, float | int | str]:
    """For L=-d^2+I, ||Lu||_{H^-2}=||u||_{L2} on normalized eigenmodes."""
    return {
        "case": "elliptic_matched_negative_control",
        "k": k,
        "s": 2.0,
        "objective": 1.0,
        "physical_l2_error": 1.0,
        "strong_l2_certificate": 1.0,
        "matched_stability_baseline": 1.0,
        "classification": "stability_baseline",
    }


def build_rows(ks: list[int] | None = None) -> list[dict[str, float | int | str]]:
    if ks is None:
        ks = [1, 2, 4, 8, 16, 32, 64, 128]
    rows: list[dict[str, float | int | str]] = []
    for k in ks:
        rows.append(direct_weak_residual_values(k, s=1.0))
        rows.append(direct_weak_residual_values(k, s=2.0))
        rows.append(elliptic_matched_negative_control_values(k))
    return rows


def write_csv(rows: list[dict[str, float | int | str]], path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "case",
        "k",
        "s",
        "objective",
        "physical_l2_error",
        "strong_l2_certificate",
        "matched_stability_baseline",
        "classification",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def plot_rows(rows: list[dict[str, float | int | str]], path: Path = PNG_PATH) -> None:
    weak_s1 = [row for row in rows if row["case"] == "direct_Hminus_failure" and float(row["s"]) == 1.0]
    weak_s2 = [row for row in rows if row["case"] == "direct_Hminus_failure" and float(row["s"]) == 2.0]
    control = [row for row in rows if row["case"] == "elliptic_matched_negative_control"]
    ks = [float(row["k"]) for row in weak_s1]

    fig, ax = plt.subplots(figsize=(6.8, 4.2), constrained_layout=True)
    ax.loglog(ks, [float(row["objective"]) for row in weak_s1], "o-", label=r"$\|u_k\|_{H^{-1}}^2$")
    ax.loglog(ks, [float(row["objective"]) for row in weak_s2], "s-", label=r"$\|u_k\|_{H^{-2}}^2$")
    ax.loglog(ks, [float(row["physical_l2_error"]) for row in weak_s1], "k--", label=r"$\|u_k\|_{L^2}$")
    ax.loglog(ks, [float(row["objective"]) for row in control], "^-", label=r"matched elliptic baseline")
    ax.set_xlabel("frequency k")
    ax.set_ylabel("value")
    ax.set_title(r"Negative-norm residual decays for high-frequency modes while $L^2$ physical error stays fixed.")
    ax.grid(True, which="both", alpha=0.25)
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
