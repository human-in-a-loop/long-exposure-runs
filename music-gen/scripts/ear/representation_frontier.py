"""τ-vs-MAE frontier plotter for M-EAR-1/feature-representation-audit (cycle 25).

Reads:
  data/ear/feature_representation_audit/stability_report_v3_<representation>.json
  data/ear/feature_representation_audit/representation_verdicts.json
  data/ear/head_regularization_audit/frontier_summary.json   (cycle-23 refs)
  data/ear/stability_audit/stability_report.json             (cycle-22 anchor)

Writes:
  data/ear/feature_representation_audit/frontier_summary.json
  docs/figures/ear_representation_frontier.png
  docs/figures/ear_representation_tau_per_variant.png

Non-factor isolation: NO import of scripts.classifier.sidecar_nonfactor.
Interpreter guard: /usr/bin/python3.
"""
# created: 2026-08-28T21:20:00Z  cycle: 25  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork dc8cba4b79eb)  milestone: M-EAR-1/feature-representation-audit
from __future__ import annotations
from . import _interp  # noqa: F401

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

DATA_DIR = Path("data/ear/feature_representation_audit")
HEAD_REG_DIR = Path("data/ear/head_regularization_audit")
FIG_DIR = Path("docs/figures")

CYCLE6_BASELINE = {"variant": "cycle6_baseline",
                   "mean_tau": 0.059,
                   "median_mae": 0.891,
                   "source_cycle": 6,
                   "d_in": 2052}
C2_TAU_THRESHOLD = 0.4
REPRESENTATIONS = ("heur_only", "panns_only", "vggish_only")


def _load_v3(name: str) -> dict | None:
    p = DATA_DIR / f"stability_report_v3_{name}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def _load_verdicts() -> dict:
    return json.loads((DATA_DIR / "representation_verdicts.json").read_text())


def _load_cycle23_rows() -> list[dict]:
    """Return the three cycle-23 head-regularization data points as frontier rows."""
    p = HEAD_REG_DIR / "frontier_summary.json"
    if not p.exists():
        return []
    hr = json.loads(p.read_text())
    out: list[dict] = []
    for row in hr["rows"]:
        if row["variant"] == "cycle6_baseline":
            continue  # avoid duplicate baseline
        out.append({
            "variant": f"cycle23_{row['variant']}",
            "mean_tau": row["mean_tau"],
            "median_mae": row["median_mae"],
            "envelope_p05": row.get("envelope_p05"),
            "envelope_p95": row.get("envelope_p95"),
            "c1_prime_verdict": row.get("c1_prime_verdict"),
            "c2_prime_verdict": row.get("c2_prime_verdict"),
            "c3_prime_verdict": row.get("c3_prime_verdict"),
            "overall": row.get("overall"),
            "source_cycle": 23,
            "d_in": 2052,
        })
    return out


def build_frontier_summary() -> dict:
    verdicts = _load_verdicts()
    rows: list[dict] = []

    # 1. Cycle-6 baseline
    rows.append(dict(CYCLE6_BASELINE, verdict="reference",
                     note="cycle-6 recipe (PC1+noise); C1/C2/C3=FAIL/FAIL/PASS at cycle-22 anchor"))

    # 2. Cycle-23 head-regularization variants (3)
    rows.extend(_load_cycle23_rows())

    # 3. Cycle-25 representations (2 or 3)
    for name in REPRESENTATIONS:
        r = _load_v3(name)
        if r is None:
            # deferred
            if "_deferrals" in verdicts and name in verdicts["_deferrals"]:
                rows.append({
                    "variant": f"cycle25_{name}",
                    "deferred": True,
                    "reason": verdicts["_deferrals"][name]["reason"],
                    "source_cycle": 25,
                })
            continue
        v = verdicts[name]
        rows.append({
            "variant": f"cycle25_{name}",
            "d_in": int(r["feat_dim"]),
            "mean_tau": r["tau_summary"]["mean"],
            "median_mae": r["mae_envelope"]["p50"],
            "envelope_p05": r["mae_envelope"]["p05"],
            "envelope_p95": r["mae_envelope"]["p95"],
            "c1_prime_verdict": v["C1_prime"]["verdict"],
            "c2_prime_verdict": v["C2_prime"]["verdict"],
            "c3_prime_verdict": v["C3_prime"]["verdict"],
            "overall": v["overall"],
            "source_cycle": 25,
        })

    summary = {
        "milestone_id": "M-EAR-1/feature-representation-audit",
        "cycle": 25,
        "run_id": "run-2026-08-28T040704Z",
        "c2_prime_threshold": C2_TAU_THRESHOLD,
        "cycle6_reference_mae": CYCLE6_BASELINE["median_mae"],
        "cycle6_reference_tau": CYCLE6_BASELINE["mean_tau"],
        "rows": rows,
    }
    return summary


COLORS = {
    "cycle6_baseline": "#ff8800",
    "cycle23_ridge": "#1f77b4",
    "cycle23_bottleneck": "#2ca02c",
    "cycle23_frozen_projector": "#d62728",
    "cycle25_heur_only": "#9467bd",
    "cycle25_panns_only": "#8c564b",
    "cycle25_vggish_only": "#e377c2",
}


def _plot_frontier(summary: dict, out_path: Path) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.0, 5.5))
    for row in summary["rows"]:
        if row.get("deferred"):
            continue
        name = row["variant"]
        tau = row["mean_tau"]
        mae = row["median_mae"]
        marker = "*" if name == "cycle6_baseline" else ("D" if name.startswith("cycle25_") else "o")
        size = 340 if name == "cycle6_baseline" else (220 if name.startswith("cycle25_") else 160)
        ax.scatter([tau], [mae], marker=marker, s=size,
                   color=COLORS.get(name, "gray"),
                   edgecolor="black", linewidth=1.0,
                   label=name, zorder=3)
        label = name.replace("cycle23_", "c23:").replace("cycle25_", "c25:")
        if name == "cycle6_baseline":
            label = "cycle-6 baseline"
        ax.annotate(label, xy=(tau, mae), xytext=(tau + 0.015, mae + 0.03),
                    fontsize=8.5, color="black")
    ax.axvline(C2_TAU_THRESHOLD, ls="--", color="gray", lw=1,
               label=f"C2' threshold τ = {C2_TAU_THRESHOLD}")
    # Shade PASS region (τ ≥ C2_TAU_THRESHOLD and mae in cycle-6-anchor band)
    y_lo, y_hi = ax.get_ylim()
    ax.axvspan(C2_TAU_THRESHOLD, 1.05, alpha=0.08, color="green",
               label="C2' PASS region")
    ax.set_xlim(-0.1, 1.05)
    ax.set_xlabel("mean pairwise Kendall τ-b (across 45 recipe pairs)")
    ax.set_ylabel("median mean-5-fold MAE (across 10 recipes)")
    ax.set_title("M-EAR-1 feature-representation audit — τ-vs-MAE frontier\n"
                 "cycle-6 baseline + cycle-23 head-reg variants + cycle-25 representations")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", fontsize=7.5, framealpha=0.85)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_tau_panels(out_path: Path) -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    reps_with_data = [n for n in REPRESENTATIONS if _load_v3(n) is not None]
    if not reps_with_data:
        return
    n = len(reps_with_data)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4), sharey=True)
    if n == 1:
        axes = [axes]
    for ax, name in zip(axes, reps_with_data):
        r = _load_v3(name)
        taus = np.array([p["kendall_tau"] for p in r["tau_pairs"]], dtype=float)
        ax.hist(taus, bins=15, color="#1f77b4", edgecolor="black")
        ax.axvline(taus.mean(), color="orange", lw=2,
                   label=f"mean = {taus.mean():+.3f}")
        ax.axvline(C2_TAU_THRESHOLD, ls="--", color="gray", lw=1,
                   label=f"C2' = {C2_TAU_THRESHOLD}")
        ax.set_title(f"{name} (D_in={r['feat_dim']})\n"
                     f"mean τ = {taus.mean():+.3f}, min = {taus.min():+.3f}",
                     fontsize=10)
        ax.set_xlabel("pairwise Kendall τ-b")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)
    axes[0].set_ylabel("count of the 45 recipe pairs")
    fig.suptitle("Cycle-25 τ distributions per representation")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main() -> int:
    summary = build_frontier_summary()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "frontier_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    _plot_frontier(summary, FIG_DIR / "ear_representation_frontier.png")
    _plot_tau_panels(FIG_DIR / "ear_representation_tau_per_variant.png")
    print("[rep-frontier] wrote", DATA_DIR / "frontier_summary.json")
    print("[rep-frontier] wrote", FIG_DIR / "ear_representation_frontier.png")
    print("[rep-frontier] wrote", FIG_DIR / "ear_representation_tau_per_variant.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
