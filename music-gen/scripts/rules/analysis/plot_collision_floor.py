#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:30:00Z
# cycle: 14
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 855d4c2e9945)
# milestone: M-GEN-1/collision-floor-investigation
# ---
"""Two-panel figure: attribution bar chart + top-contributor structural MDS.

Panel A (left): per-rule_type observed collision pair count vs. birthday-paradox
                baseline at N=8, K rules-per-type.
Panel B (right): 2D classical MDS of top-contributor rule_type distance matrix,
                 with collision-participating rules highlighted and dominant
                 rule (max_single_rule_picks) circled.

Output: docs/figures/collision_floor_decomposition.png
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

# Deterministic single-thread numeric env (parity with cycle-9/13 discipline).
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from scripts.rules.analysis.collision_attribution import attribute_collisions  # noqa: E402
from scripts.rules.analysis.pairwise_distance import pairwise_distances  # noqa: E402
from scripts.gen.sample_rules import RULE_TYPES  # noqa: E402


def _birthday_expected(N: int, K: int) -> float:
    if K <= 0:
        return 0.0
    return math.comb(N, 2) / K


def _classical_mds(D: np.ndarray, k: int = 2) -> np.ndarray:
    """Deterministic classical MDS (double-centering) to k dims."""
    n = D.shape[0]
    D2 = D ** 2
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ D2 @ J
    # Symmetric eigendecomposition (deterministic given input).
    eigvals, eigvecs = np.linalg.eigh(B)
    # Sort descending; take top-k with positive eigenvalues.
    idx = np.argsort(-eigvals)
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]
    top = eigvecs[:, :k] * np.sqrt(np.maximum(eigvals[:k], 0))
    return top


def _plot(ledger_path: Path, out_path: Path, n_salts: int = 8) -> None:
    attribution = attribute_collisions(ledger_path, n_salts)
    dists = pairwise_distances(ledger_path)

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(13.5, 5.5))

    # --- Panel A: attribution bar chart ---
    types = list(RULE_TYPES)
    obs = [attribution["per_rule_type_pair_count"][rt] for rt in types]
    exp = [_birthday_expected(n_salts, dists[rt]["n_rules"]) for rt in types]
    x = np.arange(len(types))
    w = 0.4
    axA.bar(x - w / 2, obs, w, label="observed", color="#B24C63")
    axA.bar(x + w / 2, exp, w, label="birthday-paradox expected", color="#4C8CB2")
    axA.set_xticks(x)
    axA.set_xticklabels([f"{rt}\n(K={dists[rt]['n_rules']})" for rt in types],
                        fontsize=9)
    axA.set_ylabel("collision pairs at N=8", fontsize=10)
    axA.set_title(f"Panel A — per-rule_type attribution ({sum(obs)} obs vs "
                  f"{sum(exp):.1f} BP-exp)", fontsize=10.5)
    axA.legend(fontsize=9, loc="upper right")
    axA.grid(True, alpha=0.3, axis="y")
    # Value labels
    for i, (o, e) in enumerate(zip(obs, exp)):
        axA.text(i - w / 2, o + 0.15, str(o), ha="center", fontsize=8)
        axA.text(i + w / 2, e + 0.15, f"{e:.2f}", ha="center", fontsize=8)

    # --- Panel B: MDS on top contributor ---
    top_rt = max(types, key=lambda rt: attribution["per_rule_type_pair_count"][rt])
    prs = dists[top_rt]["pair_records"]
    # Build ordered rule id list from pair records.
    seen = []
    for pr in prs:
        for k in ("rule_id_a", "rule_id_b"):
            rid = pr[k]
            if rid not in seen:
                seen.append(rid)
    n = len(seen)
    D = np.zeros((n, n))
    idx_of = {rid: i for i, rid in enumerate(seen)}
    for pr in prs:
        a = idx_of[pr["rule_id_a"]]
        b = idx_of[pr["rule_id_b"]]
        D[a, b] = D[b, a] = pr["distance"]

    coords = _classical_mds(D, k=2) if n >= 2 else np.zeros((n, 2))

    # Identify collision participants + dominant rule.
    contributor_ids = set()
    for pair in attribution["pairs"]:
        if top_rt in pair["contributors"]:
            contributor_ids.add(pair["contributor_rule_ids"][top_rt])

    # dominant = most-picked rule
    picks = {}
    for salt, sp in attribution["per_salt_picks"].items():
        rid = sp.get(top_rt)
        if rid is not None:
            picks[rid] = picks.get(rid, 0) + 1
    dominant = max(picks, key=picks.get) if picks else None

    # Plot non-participants
    for i, rid in enumerate(seen):
        if rid in contributor_ids:
            continue
        axB.scatter(coords[i, 0], coords[i, 1], color="#888888", s=60, alpha=0.55)
    for i, rid in enumerate(seen):
        if rid in contributor_ids and rid != dominant:
            axB.scatter(coords[i, 0], coords[i, 1], color="#B24C63", s=110,
                        edgecolors="black", linewidths=1.2)
    if dominant is not None and dominant in idx_of:
        di = idx_of[dominant]
        axB.scatter(coords[di, 0], coords[di, 1], color="#FFCE3A", s=220,
                    edgecolors="black", linewidths=1.6, marker="*",
                    label=f"dominant ({picks[dominant]}/8 salts)")

    # Short labels: last 4 hex of rule_id
    for i, rid in enumerate(seen):
        axB.annotate(rid[-6:], (coords[i, 0], coords[i, 1]),
                     fontsize=7, xytext=(5, 3), textcoords="offset points",
                     color="#333333")

    axB.set_title(f"Panel B — top contributor '{top_rt}' 2D MDS "
                  f"(K={n}, {attribution['per_rule_type_pair_count'][top_rt]} collision pairs)",
                  fontsize=10.5)
    axB.set_xlabel("MDS axis 1", fontsize=9)
    axB.set_ylabel("MDS axis 2", fontsize=9)
    axB.grid(True, alpha=0.3)
    axB.legend(fontsize=9, loc="best")
    # Manual second-legend for red = collision participant, gray = non-participant.
    from matplotlib.lines import Line2D
    legend_elems = [
        Line2D([0], [0], marker="o", color="w", label="collision participant",
               markerfacecolor="#B24C63", markersize=10,
               markeredgecolor="black"),
        Line2D([0], [0], marker="o", color="w", label="not in any pair",
               markerfacecolor="#888888", markersize=9),
    ]
    if dominant is not None:
        legend_elems.insert(0, Line2D(
            [0], [0], marker="*", color="w",
            label=f"dominant ({picks[dominant]}/8 salts)",
            markerfacecolor="#FFCE3A", markersize=15, markeredgecolor="black"))
    axB.legend(handles=legend_elems, fontsize=8, loc="best")

    fig.suptitle("M-GEN-1 collision floor decomposition (cycle 14, N=8, 76-row ledger)",
                 fontsize=11.5, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140, format="png")
    plt.close(fig)
    print(f"[plot_collision_floor] wrote {out_path}")


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path,
                    default=_REPO / "data" / "rules" / "ledger.jsonl")
    ap.add_argument("--out", type=Path,
                    default=_REPO / "docs" / "figures" /
                    "collision_floor_decomposition.png")
    args = ap.parse_args(argv)
    _plot(args.ledger, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
