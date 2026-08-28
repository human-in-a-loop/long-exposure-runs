#!/usr/bin/env python3
# Coverage-per-rule_type figure for docs/rules_extraction_report.md.

import os
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3"

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from scripts.rules.ledger import read_ledger

OUT = Path(os.environ.get("FIGURE_OUT",
                          str(_REPO / "docs" / "figures" / "rules_extraction_coverage.png")))

TYPES = ["harmonic", "rhythmic", "melodic", "form", "arrangement"]


def main():
    rows = read_ledger()
    counts = {t: 0 for t in TYPES}
    for r in rows:
        rt = r.get("rule_type")
        if rt in counts:
            counts[rt] += 1
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(TYPES, [counts[t] for t in TYPES],
                  color=["#4c72b0","#dd8452","#55a868","#c44e52","#8172b3"])
    for b, t in zip(bars, TYPES):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.1,
                str(counts[t]), ha="center", va="bottom", fontsize=10)
    ax.axhline(5, linestyle="--", color="gray", linewidth=1,
               label="brief threshold (5)")
    ax.set_ylabel("Rows emitted")
    ax.set_title("M-RULES-1/extraction — rows per rule_type (seed: merged_synth030s)")
    ax.set_ylim(0, max(counts.values()) + 2)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=140)
    print(f"wrote {OUT} counts={counts}")


if __name__ == "__main__":
    main()
