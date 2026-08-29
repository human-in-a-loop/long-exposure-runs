#!/usr/bin/python3
# created: 2026-08-29T18:34:00Z  cycle: 48  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: _infra/pre-existing-test-drift-triage-clone-2
"""Independent c47-overlap soundness check.

Reads captured_failures.jsonl and independently greps each identifier for
the c47 lock-set (case-insensitive substring match). Cross-checks against
the classification in triage_taxonomy.tsv. Any mismatch is a soundness
bug: the branch verdict flips to DRIFT_TRIAGE_INSUFFICIENT.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

print("[test_drift_triage.detect_c47_overlap] startup", flush=True)

_ALLOWED = ("/usr/bin/python3",)
if sys.executable not in _ALLOWED and not os.environ.get("TEST_DRIFT_TRIAGE_ALLOW_ANY_PYTHON"):
    print(
        f"[test_drift_triage.detect_c47_overlap] interpreter guard: expected one of "
        f"{_ALLOWED}, got {sys.executable!r}",
        file=sys.stderr,
    )
    sys.exit(2)

LOCK_SET = (
    "c47", "v2p1", "policy", "deprecation", "anchor.pin",
    "source.date", "source_date", "ear_v2p1", "adjudication",
)


def scan_identifier(identifier: str) -> list[str]:
    """Return the list of lock-set tokens found as substrings (case-insensitive)."""
    ident_lc = identifier.lower()
    return [t for t in LOCK_SET if t in ident_lc]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures", type=Path, required=True)
    ap.add_argument("--taxonomy", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    # Independent re-scan
    per_row_scan = []
    scanned_c47 = set()
    with args.captures.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            hits = scan_identifier(row["identifier"])
            per_row_scan.append({
                "identifier": row["identifier"],
                "line": row["line"],
                "matched_tokens": hits,
                "is_c47": bool(hits),
            })
            if hits:
                scanned_c47.add((row["identifier"], row["line"]))

    # Read classification
    classified_c47 = set()
    with args.taxonomy.open("r", encoding="utf-8") as f:
        header = f.readline().strip().split("\t")
        idx_id = header.index("identifier")
        idx_line = header.index("line")
        idx_label = header.index("taxonomy_label")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if parts[idx_label] == "c47-non-orthogonal":
                classified_c47.add((parts[idx_id], int(parts[idx_line])))

    mismatches = []
    for row in sorted(scanned_c47 - classified_c47):
        mismatches.append({"identifier": row[0], "line": row[1],
                           "kind": "scan_flags_class_missed"})
    for row in sorted(classified_c47 - scanned_c47):
        mismatches.append({"identifier": row[0], "line": row[1],
                           "kind": "class_flags_scan_missed"})

    agreement = (len(mismatches) == 0)
    result = {
        "lock_set": list(LOCK_SET),
        "per_row_scan": per_row_scan,
        "classification_agreement": agreement,
        "mismatches": mismatches,
        "soundness_status": "PASS" if agreement else "FAIL",
        "soundness_bug": (not agreement),
        "scan_c47_count": len(scanned_c47),
        "classification_c47_count": len(classified_c47),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(
        f"[test_drift_triage.detect_c47_overlap] scan_c47={len(scanned_c47)} "
        f"class_c47={len(classified_c47)} agreement={agreement}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
