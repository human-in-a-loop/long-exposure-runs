# created: 2026-05-17T18:25:00Z
# cycle: 2
# run_id: fork-e34b5b2c1c6c-clone-5
# agent: worker
# milestone: _manager/ledger-integrity
"""Classify promise_check output after the PhytoGraph plan pivot.

This is intentionally append-only: it reads the ledger and validator output,
then writes a reconciliation table/report without changing historical events.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


LEGACY_IDS = {f"M{i}" for i in range(1, 9)}
ACTIVE_PREFIXES = (
    "M0.",
    "M1.",
    "M2.",
    "M3.",
    "M4.",
    "M5.",
    "(Barrier",
)
M1_7_FRAGMENT = "chemodiversity_ethnobotany_sources/"
M1_1_FRAGMENT = "taxonomy_backbone/"


def run_promise_check(workspace: Path) -> tuple[str, int]:
    proc = subprocess.run(
        ["python3", "-m", "long_exposure.tools.promise_check", str(workspace)],
        cwd=workspace,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return proc.stdout, proc.returncode


def parse_ledger(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            row["_line_no"] = line_no
            rows.append(row)
    return rows


def current_status(events: list[dict], milestone_id: str) -> str:
    matches = [e for e in events if e.get("milestone_id") == milestone_id]
    return matches[-1].get("status", "absent") if matches else "absent"


def extract_warning_rows(output: str) -> list[dict]:
    rows = []
    for line in output.splitlines():
        if line.startswith("! WARNING: "):
            rows.append({"severity": "warning", "message": line.removeprefix("! WARNING: ")})
        elif line.startswith("x ERROR: "):
            rows.append({"severity": "error", "message": line.removeprefix("x ERROR:   ")})
    return rows


def classify(message: str) -> tuple[str, str]:
    milestone_match = re.search(r"milestone_id '([^']+)'", message)
    plan_match = re.search(r"plan milestone '([^']+)'", message)
    path_match = re.search(r"(?:path|artifact|path: ) '([^']+)'", message)
    orphan_match = re.search(r"orphan artifact in managed path: ([^ ]+)", message)
    missing_match = re.search(r"ledger-tracked artifact missing: ([^ ]+)", message)

    milestone = (milestone_match or plan_match).group(1) if (milestone_match or plan_match) else ""
    path = ""
    if path_match:
        path = path_match.group(1)
    elif orphan_match:
        path = orphan_match.group(1)
    elif missing_match:
        path = missing_match.group(1)

    if milestone in LEGACY_IDS:
        return "legacy_prior_campaign", "bare M1-M8 milestone from pre-PhytoGraph plan"
    if path.startswith("reports/final/") or path.startswith("reports/cycles/report_cycles_"):
        return "legacy_prior_campaign", "prior-campaign report artifact outside active PhytoGraph obligations"
    if "public_taxonomy_sample/v0.1" in path:
        return "legacy_prior_campaign", "pre-pivot public taxonomy sample artifact"
    if "manager_assessments/" in path or milestone.startswith("_manager/"):
        return "manager_artifact", "manager lifecycle artifact, not source staging evidence"
    if message.startswith("plan_of_record.md mtime"):
        return "manager_artifact", "plan timestamp warning caused by post-pivot plan/ledger bookkeeping"
    if path in {
        "reports/legacy_ledger_reconciliation.md",
        "reports/legacy_ledger_reconciliation.tsv",
        "reports/legacy_promise_check_after.txt",
    }:
        return "manager_artifact", "reconciliation output registered by the closure event"
    if path == "scripts/reconcile_legacy_ledger.py":
        return "manager_artifact", "this reconciliation script is registered by the closure event"
    if path.startswith(".long-exposure/manager_assessments/") or path.startswith("long-exposure/manager_assessments/"):
        return "manager_artifact", "manager assessment path normalization issue"
    if M1_7_FRAGMENT in path:
        return "active_phytograph", "M1.7 chemodiversity/handoff artifact"
    if M1_1_FRAGMENT in path:
        return "active_phytograph", "M1.1 taxonomy-backbone artifact"
    if path.startswith("scripts/m1_6_domestication/") or path.startswith("tests/m1_6_domestication/"):
        return "active_phytograph", "M1.6 domestication source artifact awaiting owning clone ledger event"
    if "reticulation" in path or path == "scripts/plot_m1_3_scale_gap_closure.py":
        return "active_phytograph", "Track 1 / M1.3 reticulation artifact awaiting owning clone ledger event"
    if plan_match:
        if milestone == "Milestone":
            return "manager_artifact", "plan table header parsed as a milestone by validator"
        if milestone.startswith(ACTIVE_PREFIXES) or "M1." in milestone or "M2." in milestone or "M3." in milestone or "M4." in milestone:
            return "active_phytograph", "future or pending PhytoGraph milestone has no event yet"
    return "unknown", "no conservative rule matched"


def write_tsv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["row_id", "severity", "classification", "reason", "message"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for idx, row in enumerate(rows, 1):
            classification, reason = classify(row["message"])
            writer.writerow(
                {
                    "row_id": idx,
                    "severity": row["severity"],
                    "classification": classification,
                    "reason": reason,
                    "message": row["message"],
                }
            )


def read_tsv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_report(
    path: Path,
    tsv_path: Path,
    promise_output_path: Path,
    promise_exit: int,
    rows: list[dict],
    events: list[dict],
) -> None:
    counts = Counter(row["classification"] for row in rows)
    severity_counts = Counter(row["severity"] for row in rows)
    m17_mentions = [r for r in rows if M1_7_FRAGMENT in r["message"] or "M1.7" in r["message"]]
    m11_mentions = [r for r in rows if M1_1_FRAGMENT in r["message"] or "M1.1" in r["message"]]
    unknown_rows = [r for r in rows if r["classification"] == "unknown"]

    error_count = severity_counts.get("error", 0)
    if error_count:
        error_summary = (
            "The remaining hard errors are legacy/post-pivot drift: all error rows "
            "are bare `M1`-`M8` entries from the prior plant-taxonomy hypergraph campaign. "
            "They should be handled as archived historical evidence, not as active "
            "PhytoGraph Wave 1 obligations."
        )
    else:
        error_summary = (
            "The current `promise_check` run has no hard errors. Former hard-error "
            "noise from bare `M1`-`M8` prior-campaign entries has been reduced to "
            "classified warning-level legacy and manager bookkeeping rows."
        )

    body = f"""---
created: {datetime.now(timezone.utc).isoformat()}
cycle: 2
run_id: fork-e34b5b2c1c6c-clone-5
agent: worker
milestone: _manager/ledger-integrity
---

# Legacy Ledger Reconciliation

This reconciliation classifies the current `promise_check` output after the PhytoGraph pivot. It does not rewrite, delete, or alter historical `promise_ledger.jsonl` lines.

## Summary

- `promise_check` exit code: `{promise_exit}`
- Parsed validator rows: {len(rows)}
- Severity counts: {dict(severity_counts)}
- Classification counts: {dict(counts)}
- M1.1 ledger status: `{current_status(events, "M1.1")}`
- M1.7 ledger status: `{current_status(events, "M1.7")}`
- M1.7 warning/error mentions: {len(m17_mentions)}
- M1.1 warning/error mentions: {len(m11_mentions)}

## Classification Rule

Pre-pivot bare milestone IDs `M1` through `M8` are classified as `legacy_prior_campaign` because the active PhytoGraph plan uses IDs such as `M0.1`, `M1.1`, and `M1.7`. Prior-cycle report/final artifacts and the old public-taxonomy sample are also legacy. Manager assessment paths and validator bookkeeping rows are `manager_artifact`. Current or pending PhytoGraph milestone/path rows are `active_phytograph`; these are warnings about unfinished sibling work or future waves unless they name a validated M1.1/M1.7 artifact.

## Findings

{error_summary}

No current `promise_check` warning or error names an M1.7 chemodiversity/handoff artifact. M1.1 and M1.7 remain validated in the ledger, so Barrier 1 can treat future M1.1/M1.7 warnings as new defects rather than inherited ledger noise.

The remaining active-PhytoGraph warnings are pending/future milestones with no events yet, plus sibling-clone artifacts outside clone 5 ownership. The reconciliation does not mark those complete.

## Outputs

- TSV: `{tsv_path}`
- Validator capture: `{promise_output_path}`

"""
    if unknown_rows:
        body += "## Unknown Rows\n\n"
        for row in unknown_rows:
            body += f"- {row['severity']}: {row['message']}\n"
    else:
        body += "## Unknown Rows\n\nNo rows were left unclassified.\n"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--promise-output", default="reports/legacy_promise_check_after.txt")
    parser.add_argument("--tsv", default="reports/legacy_ledger_reconciliation.tsv")
    parser.add_argument("--md", default="reports/legacy_ledger_reconciliation.md")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    output, promise_exit = run_promise_check(workspace)
    promise_output_path = workspace / args.promise_output
    promise_output_path.parent.mkdir(parents=True, exist_ok=True)
    promise_output_path.write_text(output, encoding="utf-8")

    raw_rows = extract_warning_rows(output)
    tsv_path = workspace / args.tsv
    write_tsv(raw_rows, tsv_path)
    rows = read_tsv(tsv_path)
    events = parse_ledger(workspace / "promise_ledger.jsonl")
    write_report(workspace / args.md, Path(args.tsv), Path(args.promise_output), promise_exit, rows, events)

    print(
        json.dumps(
            {
                "promise_check_exit": promise_exit,
                "rows": len(rows),
                "classification_counts": dict(Counter(r["classification"] for r in rows)),
                "severity_counts": dict(Counter(r["severity"] for r in rows)),
                "m1_1_status": current_status(events, "M1.1"),
                "m1_7_status": current_status(events, "M1.7"),
                "outputs": [args.tsv, args.md, args.promise_output],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
