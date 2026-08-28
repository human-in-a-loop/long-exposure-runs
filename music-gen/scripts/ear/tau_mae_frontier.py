"""τ-vs-MAE frontier plotter for M-EAR-1/head-regularization-audit.

Reads:
  data/ear/head_regularization_audit/stability_report_v2_<variant>.json
  data/ear/head_regularization_audit/variant_verdicts.json
  data/ear/stability_audit/stability_report.json   (cycle-6 baseline reference)

Writes:
  data/ear/head_regularization_audit/frontier_summary.json
  docs/figures/ear_head_regularization_tau_mae_frontier.png
  docs/figures/ear_head_regularization_tau_per_variant.png

Non-factor isolation: NO import of scripts.classifier.sidecar_nonfactor.
Interpreter guard: `/usr/bin/python3`.
"""
# created: 2026-08-28T21:00:00Z  cycle: 23  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 3fbd8c1ab57c)  milestone: M-EAR-1/head-regularization-audit
from __future__ import annotations
from . import _interp  # noqa: F401

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

DATA_DIR = Path("data/ear/head_regularization_audit")
FIG_DIR = Path("docs/figures")
BASELINE_PATH = Path("data/ear/stability_audit/stability_report.json")
CYCLE6_BASELINE = {"variant": "cycle6_baseline",
                   "mean_tau": 0.059,
                   "median_mae": 0.891}
C2_TAU_THRESHOLD = 0.4
VARIANTS = ("ridge", "bottleneck", "frozen_projector")


def _load_variant(name: str) -> dict:
    p = DATA_DIR / f"stability_report_v2_{name}.json"
    return json.loads(p.read_text())


def _load_verdicts() -> dict:
    return json.loads((DATA_DIR / "variant_verdicts.json").read_text())


def build_frontier_summary() -> dict:
    verdicts = _load_verdicts()
    rows = [dict(CYCLE6_BASELINE, verdict="reference", note="cycle-6 recipe (PC1+noise); C1/C2/C3=FAIL/FAIL/PASS at cycle-22 anchor")]
    for name in VARIANTS:
        r = _load_variant(name)
        v = verdicts[name]
        rows.append({
            "variant": name,
            "mean_tau": r["tau_summary"]["mean"],
            "median_mae": r["mae_envelope"]["p50"],
            "envelope_p05": r["mae_envelope"]["p05"],
            "envelope_p95": r["mae_envelope"]["p95"],
            "c1_prime_verdict": v["C1_prime"]["verdict"],
            "c2_prime_verdict": v["C2_prime"]["verdict"],
            "c3_prime_verdict": v["C3_prime"]["verdict"],
            "overall": v["overall"],
        })
    summary = {
        "milestone_id": "M-EAR-1/head-regularization-audit",
        "cycle": 23,
        "run_id": "run-2026-08-28T040704Z",
        "c2_prime_threshold": C2_TAU_THRESHOLD,
        "cycle6_reference_mae": CYCLE6_BASELINE["median_mae"],
        "cycle6_reference_tau": CYCLE6_BASELINE["mean_tau"],
        "rows": rows,
    }
    return summary


def _plot_frontier(summary: dict, out_path: Path) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    colors = {"cycle6_baseline": "#ff8800", "ridge": "#1f77b4",
              "bottleneck": "#2ca02c", "frozen_projector": "#d62728"}
    for row in summary["rows"]:
        name = row["variant"]
        tau = row["mean_tau"]
        mae = row["median_mae"]
        marker = "*" if name == "cycle6_baseline" else "o"
        size = 300 if name == "cycle6_baseline" else 180
        ax.scatter([tau], [mae], marker=marker, s=size,
                   color=colors.get(name, "gray"),
                   edgecolor="black", linewidth=1.0,
                   label=f"{name}", zorder=3)
        offset_x, offset_y = 0.02, 0.03
        ax.annotate(name, xy=(tau, mae), xytext=(tau + offset_x, mae + offset_y),
                    fontsize=9, color="black")
    ax.axvline(C2_TAU_THRESHOLD, ls="--", color="gray", lw=1,
               label=f"C2' threshold τ = {C2_TAU_THRESHOLD}")
    ax.set_xlabel("mean pairwise Kendall τ-b (across 45 recipe pairs)")
    ax.set_ylabel("median mean-5-fold MAE (across 10 recipes)")
    ax.set_title("M-EAR-1 head-regularization audit — τ-vs-MAE frontier")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", fontsize=8)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_tau_panels(out_path: Path) -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True)
    for ax, name in zip(axes, VARIANTS):
        r = _load_variant(name)
        taus = np.array([p["kendall_tau"] for p in r["tau_pairs"]], dtype=float)
        ax.hist(taus, bins=15, color="#1f77b4", edgecolor="black")
        ax.axvline(taus.mean(), color="orange", lw=2, label=f"mean = {taus.mean():+.3f}")
        ax.axvline(C2_TAU_THRESHOLD, ls="--", color="gray", lw=1, label=f"C2' = {C2_TAU_THRESHOLD}")
        ax.set_title(f"{name}\n(mean τ = {taus.mean():+.3f}, min = {taus.min():+.3f})", fontsize=10)
        ax.set_xlabel("pairwise Kendall τ-b")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)
    axes[0].set_ylabel("count of the 45 recipe pairs")
    fig.suptitle("τ distributions per variant (45 pairwise τ values each)")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main() -> int:
    summary = build_frontier_summary()
    (DATA_DIR / "frontier_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    _plot_frontier(summary, FIG_DIR / "ear_head_regularization_tau_mae_frontier.png")
    _plot_tau_panels(FIG_DIR / "ear_head_regularization_tau_per_variant.png")
    print("[frontier] wrote", DATA_DIR / "frontier_summary.json")
    print("[frontier] wrote", FIG_DIR / "ear_head_regularization_tau_mae_frontier.png")
    print("[frontier] wrote", FIG_DIR / "ear_head_regularization_tau_per_variant.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
