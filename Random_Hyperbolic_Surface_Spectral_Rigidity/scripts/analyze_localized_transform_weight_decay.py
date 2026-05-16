# created: 2026-05-16T18:44:00Z
# cycle: 35
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M24-localized-transform-geodesic-weight-decay-obstruction
"""Analyze localized transform/geodesic weight decay in the M22 numerator."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "data/extension_candidates/localized_transform_weight_decay.csv"
SUMMARY_CSV = ROOT / "data/extension_candidates/localized_transform_decay_summary.csv"
ENVELOPE_FIG = ROOT / "reports/figures/m24_transform_envelope_scaling.png"
GROWTH_FIG = ROOT / "reports/figures/m24_geodesic_growth_vs_transform_decay.png"

N_REF = 10.0**12
ALPHA_WEYL = 0.006
SCHWARTZ_ORDER = 8
GEODESIC_NET_RATE = 0.50
REDUCED_WORD_RATE = 0.72
QUOTIENT_RATE = 0.95
NONCOMPACT_TAIL_RATE = 0.18


def num_text(value: float) -> str:
    if math.isinf(value) or math.isnan(value):
        return str(value)
    if abs(value) < 1e-14:
        value = 0.0
    return f"{value:.12g}"


def q_delta_exponent(eta: float, d: float) -> float:
    """Bulk fixed-energy exponent for q * delta_r with q=n^eta and delta_r~n^-d."""
    return eta - d


def support_valid(eta: float, d: float) -> bool:
    return eta + 1e-12 >= d


def endpoint_valid(d: float) -> bool:
    return d > ALPHA_WEYL


def transform_envelope(model: str, u: float, t: float) -> float:
    if model == "compact_support_only":
        return 1.0
    if model == "smooth_schwartz_scaled":
        return (1.0 + max(u, 0.0)) ** (-SCHWARTZ_ORDER)
    if model == "vanishing_moment_scaled":
        return (max(u, 0.0) ** 2) * (1.0 + max(u, 0.0)) ** (-(SCHWARTZ_ORDER + 2))
    if model == "noncompact_gaussian_t_tail":
        return math.exp(-NONCOMPACT_TAIL_RATE * max(t, 0.0))
    raise ValueError(f"unknown transform model: {model}")


def compatibility(model: str) -> str:
    if model in {"compact_support_only", "smooth_schwartz_scaled"}:
        return "compatible"
    if model == "vanishing_moment_scaled":
        return "conditional_zero_mean_not_count_positive"
    if model == "noncompact_gaussian_t_tail":
        return "incompatible_noncompact_geometric_tail"
    raise ValueError(model)


def growth_rate(model: str) -> float:
    if model == "geodesic_after_selberg":
        return GEODESIC_NET_RATE
    if model == "reduced_word_family":
        return REDUCED_WORD_RATE
    if model == "quotient_family_proxy":
        return QUOTIENT_RATE
    raise ValueError(f"unknown growth model: {model}")


def scaled_damping_exponent(model: str, eta: float, d: float) -> float:
    """Exponent a in a support-endpoint damping scale exp(-n^a), when present.

    Compact-support and Schwartz-scaled compatible envelopes have no exponential
    damping in t. The noncompact contrast has a=true eta but is incompatible.
    """
    if model == "noncompact_gaussian_t_tail":
        return eta
    return 0.0


def row_verdict(
    model: str,
    growth_model: str,
    d: float,
    eta: float,
    t_endpoint: float,
    u_endpoint: float,
    envelope: float,
    net_log: float,
) -> tuple[str, str]:
    if not support_valid(eta, d):
        return "fails_support", "eta<d, so the bulk localized window is not resolved"
    if not endpoint_valid(d):
        return "not_endpoint_beating", "d is not above the inherited endpoint-subtraction threshold"
    comp = compatibility(model)
    if comp == "incompatible_noncompact_geometric_tail":
        if net_log < 0.0:
            return "contrast_success_only", "exponential t-tail beats this growth proxy only after changing trace architecture"
        return "contrast_insufficient", "this exponential t-tail is outside compact support and is still weaker than the growth proxy"
    if comp == "conditional_zero_mean_not_count_positive":
        return "conditional_not_count_positive", "moment cancellation gives damping near t=0 but loses positive window-count interpretation"
    return "compact_route_obstructed", "compatible envelope gives at most scaled cutoff/Schwartz decay, not exponential-in-t damping against positive growth"


def build_rows() -> list[dict[str, str]]:
    d_grid = [0.004, 0.006, 0.008, 0.01, 0.02, 0.05, 0.08, 0.12]
    eta_grid = [0.004, 0.006, 0.008, 0.01, 0.02, 0.05, 0.08, 0.12, 0.16, 0.24]
    transform_models = [
        "compact_support_only",
        "smooth_schwartz_scaled",
        "vanishing_moment_scaled",
        "noncompact_gaussian_t_tail",
    ]
    growth_models = ["geodesic_after_selberg", "reduced_word_family", "quotient_family_proxy"]
    rows: list[dict[str, str]] = []
    for d in d_grid:
        for eta in eta_grid:
            q_delta_exp = q_delta_exponent(eta, d)
            t_endpoint = N_REF**eta
            u_endpoint = N_REF**q_delta_exp
            for transform_model in transform_models:
                envelope = transform_envelope(transform_model, u_endpoint, t_endpoint)
                comp = compatibility(transform_model)
                for growth_model in growth_models:
                    rate = growth_rate(growth_model)
                    net_log = math.log(max(envelope, 1e-300)) + rate * t_endpoint
                    net_log10 = net_log / math.log(10.0)
                    verdict, note = row_verdict(
                        transform_model,
                        growth_model,
                        d,
                        eta,
                        t_endpoint,
                        u_endpoint,
                        envelope,
                        net_log,
                    )
                    rows.append(
                        {
                            "d": num_text(d),
                            "eta": num_text(eta),
                            "q_delta_exponent_eta_minus_d": num_text(q_delta_exp),
                            "support_valid_eta_ge_d": str(support_valid(eta, d)).lower(),
                            "endpoint_beating_d_gt_alpha_w": str(endpoint_valid(d)).lower(),
                            "transform_model": transform_model,
                            "compatibility": comp,
                            "growth_model": growth_model,
                            "growth_rate_per_t": num_text(rate),
                            "t_endpoint_n_eta": num_text(t_endpoint),
                            "u_endpoint_t_delta": num_text(u_endpoint),
                            "transform_envelope_endpoint": num_text(envelope),
                            "log10_transform_envelope_endpoint": num_text(math.log10(max(envelope, 1e-300))),
                            "net_log10_endpoint_after_growth": num_text(net_log10),
                            "exponential_damping_exponent_if_any": num_text(scaled_damping_exponent(transform_model, eta, d)),
                            "m22_support_and_endpoint_conditions": str(support_valid(eta, d) and endpoint_valid(d)).lower(),
                            "success_row": str(verdict in {"conditional_decay_row", "contrast_success_only"}).lower(),
                            "verdict": verdict,
                            "note": note,
                        }
                    )
    return rows


def summarize(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["transform_model"], row["compatibility"], row["growth_model"])].append(row)
    summary: list[dict[str, str]] = []
    for (transform_model, comp, growth_model), items in sorted(grouped.items()):
        support_endpoint = [r for r in items if r["m22_support_and_endpoint_conditions"] == "true"]
        verdict_counts = defaultdict(int)
        for row in support_endpoint:
            verdict_counts[row["verdict"]] += 1
        dominant = max(verdict_counts, key=verdict_counts.get) if verdict_counts else "none"
        summary.append(
            {
                "transform_model": transform_model,
                "compatibility": comp,
                "growth_model": growth_model,
                "rows": str(len(items)),
                "m22_support_endpoint_rows": str(len(support_endpoint)),
                "compact_route_obstructed_rows": str(verdict_counts["compact_route_obstructed"]),
                "conditional_decay_rows": str(verdict_counts["conditional_decay_row"]),
                "contrast_success_rows": str(verdict_counts["contrast_success_only"]),
                "contrast_insufficient_rows": str(verdict_counts["contrast_insufficient"]),
                "dominant_verdict_on_m22_rows": dominant,
            }
        )
    return summary


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_envelopes() -> None:
    us = [10 ** (-2 + i * 5 / 260) for i in range(261)]
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.plot(us, [1.0 for _ in us], color="#4c78a8", label="compact support only")
    ax.plot(us, [transform_envelope("smooth_schwartz_scaled", u, u) for u in us], color="#54a24b", label="Schwartz envelope in u=t delta_r")
    ax.plot(us, [transform_envelope("vanishing_moment_scaled", u, u) for u in us], color="#f58518", label="vanishing-moment contrast")
    ax.axvline(1.0, color="black", linestyle=":", linewidth=1.2, label="u=1 transition scale")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(1e-8, 2.0)
    ax.set_xlabel("scaled variable u = t delta_r")
    ax.set_ylabel("relative transform envelope")
    ax.set_title("Compatible localized transform decay is scaled, not exponential in t")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    ENVELOPE_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ENVELOPE_FIG, dpi=180)
    plt.close(fig)


def plot_growth(rows: list[dict[str, str]]) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    subset = [
        r
        for r in rows
        if r["d"] in {"0.01", "0.05"}
        and r["growth_model"] == "quotient_family_proxy"
        and r["m22_support_and_endpoint_conditions"] == "true"
    ]
    colors = {
        "compact_support_only": "#4c78a8",
        "smooth_schwartz_scaled": "#54a24b",
        "noncompact_gaussian_t_tail": "#e45756",
    }
    labels_seen: set[str] = set()
    for model in ["compact_support_only", "smooth_schwartz_scaled", "noncompact_gaussian_t_tail"]:
        for d in ["0.01", "0.05"]:
            items = sorted(
                [r for r in subset if r["transform_model"] == model and r["d"] == d],
                key=lambda r: float(r["eta"]),
            )
            if not items:
                continue
            label = f"{model}, d={d}"
            ax.plot(
                [float(r["eta"]) for r in items],
                [float(r["net_log10_endpoint_after_growth"]) for r in items],
                marker="o",
                linewidth=1.6,
                color=colors[model],
                linestyle="-" if d == "0.01" else "--",
                label=label if label not in labels_seen else None,
            )
            labels_seen.add(label)
    ax.axhline(0.0, color="black", linewidth=1.0)
    ax.set_xlabel("support exponent eta")
    ax.set_ylabel("log10(endpoint envelope x growth proxy)")
    ax.set_title("Compatible envelopes leave endpoint growth positive in M22 rows")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=7)
    fig.tight_layout()
    GROWTH_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(GROWTH_FIG, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    summary = summarize(rows)
    write_csv(OUT_CSV, rows)
    write_csv(SUMMARY_CSV, summary)
    plot_envelopes()
    plot_growth(rows)
    print(f"wrote {len(rows)} rows to {OUT_CSV}")
    print(f"wrote {len(summary)} summary rows to {SUMMARY_CSV}")
    print(f"wrote figures {ENVELOPE_FIG} and {GROWTH_FIG}")


if __name__ == "__main__":
    main()
