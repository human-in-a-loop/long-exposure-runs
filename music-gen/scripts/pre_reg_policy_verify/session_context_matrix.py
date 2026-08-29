#!/usr/bin/python3
# created: 2026-08-29T17:31:00Z  cycle: 47  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: _infra/pre-registration-gate-policy-scope-verification-clone-1
"""Aggregate commit_classification.tsv into (session-context class × count) matrix.

Output columns: session_context\tcommit_count\tconfidence_high\tconfidence_medium\tconfidence_low
Includes a `TOTAL` row whose counts sum the classified rows.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_ALLOWED = ("/usr/bin/python3",)
if sys.executable not in _ALLOWED and not os.environ.get("PRE_REG_POLICY_VERIFY_ALLOW_ANY_PYTHON"):
    print(f"[pre_reg_policy_verify.session_context_matrix] interpreter guard failed",
          file=sys.stderr)
    sys.exit(2)

BANNER = "[pre_reg_policy_verify.session_context_matrix] c47 Branch B — starting"
print(BANNER)

ROOT = Path(__file__).resolve().parent.parent.parent

# Canonical order of session-context classes; TOTAL always last.
_CLASSES = (
    "periodic-sweep",
    "merge-integration",
    "worker-turn",
    "auditor-turn",
    "researcher-turn",
    "harness-auto-write",
    "unknown",
)


def build(class_tsv: Path, out_tsv: Path) -> dict[str, int]:
    counts: dict[str, dict[str, int]] = {c: {"total": 0, "high": 0, "medium": 0, "low": 0}
                                          for c in _CLASSES}
    lines = class_tsv.read_text().splitlines()
    header = lines[0].split("\t") if lines else []
    idx_sc = header.index("session_context")
    idx_cf = header.index("confidence")
    total_rows = 0
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        sc = parts[idx_sc]
        cf = parts[idx_cf]
        if sc not in counts:
            counts[sc] = {"total": 0, "high": 0, "medium": 0, "low": 0}
        counts[sc]["total"] += 1
        counts[sc][cf] = counts[sc].get(cf, 0) + 1
        total_rows += 1

    header_out = "session_context\tcommit_count\tconfidence_high\tconfidence_medium\tconfidence_low\n"
    body = [header_out]
    for c in _CLASSES:
        d = counts[c]
        body.append(f"{c}\t{d['total']}\t{d['high']}\t{d['medium']}\t{d['low']}\n")
    # TOTAL row
    t_high = sum(counts[c]["high"] for c in _CLASSES)
    t_med = sum(counts[c]["medium"] for c in _CLASSES)
    t_low = sum(counts[c]["low"] for c in _CLASSES)
    body.append(f"TOTAL\t{total_rows}\t{t_high}\t{t_med}\t{t_low}\n")
    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    out_tsv.write_text("".join(body))
    print(f"[pre_reg_policy_verify.session_context_matrix] wrote {len(_CLASSES)+1} rows -> {out_tsv}")
    return {c: counts[c]["total"] for c in counts}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--classified", type=Path,
                    default=ROOT / "data" / "pre_reg_policy_verify" / "commit_classification.tsv")
    ap.add_argument("--out", type=Path,
                    default=ROOT / "data" / "pre_reg_policy_verify" / "session_context_matrix.tsv")
    args = ap.parse_args()
    build(args.classified, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
