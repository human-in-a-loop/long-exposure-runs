#!/usr/bin/python3
# created: 2026-08-29T18:35:00Z  cycle: 48  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: _infra/pre-existing-test-drift-triage-clone-2
"""Emit per-failure disposition manifest per the c48 Branch C rubric.

For each of the 87 rows in triage_taxonomy.tsv, compose a disposition
entry:

- c47-non-orthogonal (CRITICAL): identifier + line + inferred cause
  + suggested remediation (which c47 branch (A/B/C) likely produced
  the drift).
- infra-brittleness: identifier + line + suggested test rewrite class
  (transient-state class) + ticket for c49+.
- environmental-drift: identifier + line + sub-class + no-action-needed
  note.
- c47-orthogonal: identifier + line + note that no action is required
  at this branch's scope.

Canonical-JSON key ordering; byte-determinism × 2 property.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

print("[test_drift_triage.disposition_report] startup", flush=True)

_ALLOWED = ("/usr/bin/python3",)
if sys.executable not in _ALLOWED and not os.environ.get("TEST_DRIFT_TRIAGE_ALLOW_ANY_PYTHON"):
    print(
        f"[test_drift_triage.disposition_report] interpreter guard: expected one of "
        f"{_ALLOWED}, got {sys.executable!r}",
        file=sys.stderr,
    )
    sys.exit(2)


def infer_c47_branch(identifier: str) -> str:
    """Return the c47 branch (A/B/C) most likely to have produced drift."""
    ident_lc = identifier.lower()
    if "v2p1" in ident_lc or "ear_v2p1" in ident_lc:
        return "Branch A (M-EAR-1/real-label-training-v2.1)"
    if "policy" in ident_lc:
        return "Branch B (_infra/pre-registration-gate-policy-scope-verification)"
    if "deprecation" in ident_lc or "anchor.pin" in ident_lc or "source.date" in ident_lc or "source_date" in ident_lc:
        return "Branch C (_manager/deprecate-c45-and-source-date-epoch-anchor-pin)"
    if "adjudication" in ident_lc:
        return "c46 adjudication chain"
    return "c47 (branch unknown)"


def compose_disposition(row: dict) -> dict:
    ident = row["identifier"]
    line = row["line"]
    label = row["taxonomy_label"]
    sub = row["signal_matched_pattern"]

    entry = {
        "identifier": ident,
        "line": line,
        "taxonomy_label": label,
    }

    if label == "c47-non-orthogonal":
        entry["critical"] = True
        entry["escalation"] = "AUDITOR_CRITICAL"
        entry["inferred_cause"] = (
            f"Identifier substring-matches c47 lock-set token {sub!r}. "
            "This test check was authored against c47 rubric/verdict/anchor "
            "artifacts; if it now fails, the c47 branch that produced those "
            "artifacts may have drifted post-merge."
        )
        entry["suggested_remediation"] = (
            f"Cross-check with {infer_c47_branch(ident)}. Confirm on-disk "
            "verdict.json, rubric_hash.txt, and anchor manifest entries "
            "byte-equal to the c47-close state. Escalate to auditor if "
            "byte-inequality is observed."
        )
        entry["assigned_to"] = "auditor"
    elif label == "infra-brittleness":
        entry["critical"] = False
        entry["escalation"] = "c49+ ticket"
        entry["transient_state_class"] = sub
        entry["suggested_test_rewrite"] = (
            f"Test at line {line} relies on transient state class "
            f"{sub!r}. Replace the transient dependency with a stable "
            "fixture or a well-defined mock. Out of scope for this branch."
        )
        entry["assigned_to"] = "c49+ infra-brittleness sub-cycle"
    elif label == "environmental-drift":
        entry["critical"] = False
        entry["escalation"] = "no-action-needed (documented drift)"
        entry["drift_sub_class"] = sub
        entry["note"] = (
            f"Environmental drift class {sub!r}. Documented drift from "
            "c46 close, unchanged in c47 (see c47 post-merge integration "
            "report §2 for the 87-failure baseline)."
        )
        entry["assigned_to"] = "none (advisory)"
    else:  # c47-orthogonal
        entry["critical"] = False
        entry["escalation"] = "no-action-needed (orthogonal)"
        entry["note"] = (
            "Identifier does not match c47 lock-set. Failure is orthogonal "
            "to c47 branch outcomes. Auditor can independently verify "
            "orthogonality by re-grepping the identifier."
        )
        entry["assigned_to"] = "none (advisory)"

    return entry


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--taxonomy", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    entries = []
    with args.taxonomy.open("r", encoding="utf-8") as f:
        header = f.readline().strip().split("\t")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            row = dict(zip(header, parts))
            row["line"] = int(row["line"])
            entries.append(compose_disposition(row))

    entries.sort(key=lambda e: (e["line"], e["identifier"]))

    counts: dict[str, int] = {}
    critical_identifiers: list[dict] = []
    for e in entries:
        counts[e["taxonomy_label"]] = counts.get(e["taxonomy_label"], 0) + 1
        if e.get("critical"):
            critical_identifiers.append({
                "identifier": e["identifier"],
                "line": e["line"],
            })

    manifest = {
        "total_entries": len(entries),
        "per_taxonomy_counts": dict(sorted(counts.items())),
        "critical_count": len(critical_identifiers),
        "critical_identifiers": critical_identifiers,
        "entries": entries,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"[test_drift_triage.disposition_report] entries={len(entries)} "
        f"critical={len(critical_identifiers)} counts={counts}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
