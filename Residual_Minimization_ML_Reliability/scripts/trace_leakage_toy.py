# created: 2026-05-14T14:45:00Z
# cycle: 50
# run_id: run-2026-05-14T030813Z
# agent: worker
# milestone: M-11
"""CAT-02 toy: vanishing trace penalty leaves the wrong constant uncontrolled."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_PATH = DATA / "trace_leakage_scaling.csv"
PNG_PATH = DATA / "trace_leakage_scaling.png"


def bad_family_values(n: int, fixed_lambda: float = 1.0) -> dict[str, float | int | str]:
    """Values for u_n(x)=1 in u'=0 with intended trace u(0)=0."""
    vanishing_lambda = n**-2
    trace_value = 1.0
    derivative_residual_l2_sq = 0.0
    physical_l2_error_sq = 1.0
    return {
        "case": "bad_constant",
        "n": n,
        "vanishing_lambda": vanishing_lambda,
        "derivative_residual_l2_sq": derivative_residual_l2_sq,
        "objective": derivative_residual_l2_sq + vanishing_lambda * trace_value**2,
        "physical_l2_error": physical_l2_error_sq**0.5,
        "trace_value": trace_value,
        "fixed_trace_certificate": fixed_lambda * trace_value**2,
    }


def shrinking_control_values(n: int, fixed_lambda: float = 1.0) -> dict[str, float | int | str]:
    """A harmless control family u_n(x)=1/n where both objective and error vanish."""
    vanishing_lambda = n**-2
    trace_value = 1.0 / n
    derivative_residual_l2_sq = 0.0
    physical_l2_error_sq = trace_value**2
    return {
        "case": "shrinking_constant_control",
        "n": n,
        "vanishing_lambda": vanishing_lambda,
        "derivative_residual_l2_sq": derivative_residual_l2_sq,
        "objective": derivative_residual_l2_sq + vanishing_lambda * trace_value**2,
        "physical_l2_error": physical_l2_error_sq**0.5,
        "trace_value": trace_value,
        "fixed_trace_certificate": fixed_lambda * trace_value**2,
    }


def build_rows(ns: list[int] | None = None) -> list[dict[str, float | int | str]]:
    if ns is None:
        ns = [1, 2, 4, 8, 16, 32, 64, 128]
    rows: list[dict[str, float | int | str]] = []
    for n in ns:
        rows.append(bad_family_values(n))
        rows.append(shrinking_control_values(n))
    return rows


def write_csv(rows: list[dict[str, float | int | str]], path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "case",
        "n",
        "vanishing_lambda",
        "derivative_residual_l2_sq",
        "objective",
        "physical_l2_error",
        "trace_value",
        "fixed_trace_certificate",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def plot_rows(rows: list[dict[str, float | int | str]], path: Path = PNG_PATH) -> None:
    bad = [row for row in rows if row["case"] == "bad_constant"]
    ns = [float(row["n"]) for row in bad]
    objective = [float(row["objective"]) for row in bad]
    error = [float(row["physical_l2_error"]) for row in bad]
    certificate = [float(row["fixed_trace_certificate"]) for row in bad]

    fig, ax = plt.subplots(figsize=(6.5, 4.2), constrained_layout=True)
    ax.loglog(ns, objective, "o-", label=r"vanishing objective $n^{-2}|u(0)|^2$")
    ax.loglog(ns, error, "s--", label=r"physical error $\|u\|_{L^2}$")
    ax.loglog(ns, certificate, "^-", label="fixed trace certificate")
    ax.set_xlabel("penalty scale index n")
    ax.set_ylabel("value")
    ax.set_title("Boundary penalty tends to zero while the wrong constant solution keeps unit physical error.")
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
