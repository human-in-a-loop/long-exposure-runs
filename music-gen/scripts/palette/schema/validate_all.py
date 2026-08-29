#!/usr/bin/env python3
"""Sweep all valid + planted-invalid palette instances through the two-layer
validator; emit data/palette/schema/validation_report.tsv.

Columns:
  relpath | layer_1_errors_count | layer_2_errors_count | first_error_msg | expected_verdict | observed_verdict

expected_verdict is "PASS" for files under examples/<stem>/*.json and "FAIL"
for files under examples/planted_invalid/*.json.
Batch-only failure classes (duplicate_assignment_id) are checked separately.
"""

import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.palette.validate import validate_row, validate_batch  # noqa: E402
from scripts.palette.provenance import known_rule_ids  # noqa: E402


def sweep():
    known_ids = known_rule_ids()
    valid_dirs = ["drums", "bass", "other"]
    planted_dir = _HERE / "examples" / "planted_invalid"

    rows = []
    # Valid corpus.
    for stem in valid_dirs:
        stem_dir = _HERE / "examples" / stem
        if not stem_dir.is_dir():
            continue
        for p in sorted(stem_dir.glob("*.json")):
            row = json.loads(p.read_text())
            l1 = 0
            l2 = 0
            first_msg = ""
            errs = validate_row(row, known_ids=known_ids)
            for e in errs:
                if e.startswith("schema:"):
                    l1 += 1
                else:
                    l2 += 1
                if not first_msg:
                    first_msg = e
            observed = "PASS" if not errs else "FAIL"
            rows.append((
                str(p.relative_to(_REPO)),
                l1, l2, first_msg, "PASS", observed,
            ))

    # Planted-invalid corpus (single-row failures).
    # NOTE: 10a/10b are batch-only failures (duplicate assignment_id detected
    # only under validate_batch); individually they must PASS. All other
    # planted classes must FAIL individually.
    per_class_rows = []
    for p in sorted(planted_dir.glob("*.json")):
        obj = json.loads(p.read_text())
        row = obj.get("row")
        klass = obj.get("_planted_class")
        offending = obj.get("_offending_field")
        errs = validate_row(row, known_ids=known_ids)
        l1 = sum(1 for e in errs if e.startswith("schema:"))
        l2 = len(errs) - l1
        first_msg = errs[0] if errs else ""
        observed = "PASS" if not errs else "FAIL"
        expected = "PASS" if klass == "duplicate_assignment_id" else "FAIL"
        rows.append((
            str(p.relative_to(_REPO)),
            l1, l2, first_msg, expected, observed,
        ))
        per_class_rows.append((klass, offending, observed, first_msg))

    # Batch-level: duplicate_assignment_id — feed the two 10a/10b rows to validate_batch.
    dup_rows = []
    for name in ("10a_duplicate_assignment_id.json", "10b_duplicate_assignment_id.json"):
        obj = json.loads((planted_dir / name).read_text())
        dup_rows.append(obj["row"])
    batch_errs = validate_batch(dup_rows)
    dup_hits = [e for e in batch_errs if "duplicate_assignment_id" in e]
    dup_first = dup_hits[0] if dup_hits else ""
    rows.append((
        "scripts/palette/schema/examples/planted_invalid/_batch_duplicate_check",
        0, len(dup_hits), dup_first, "FAIL", ("FAIL" if dup_hits else "PASS"),
    ))

    # Write TSV.
    data_dir = _REPO / "data" / "palette" / "schema"
    data_dir.mkdir(parents=True, exist_ok=True)
    out = data_dir / "validation_report.tsv"
    with open(out, "w") as f:
        f.write("relpath\tlayer_1_errors_count\tlayer_2_errors_count\tfirst_error_msg\texpected_verdict\tobserved_verdict\n")
        for rpath, l1, l2, msg, exp, obs in rows:
            # First error message is one line only; escape newlines.
            msg = msg.replace("\t", " ").replace("\n", " ")
            f.write(f"{rpath}\t{l1}\t{l2}\t{msg}\t{exp}\t{obs}\n")

    # Report agreement.
    agree = sum(1 for r in rows if r[4] == r[5])
    print(f"Wrote {out}")
    print(f"  {len(rows)} rows; {agree} verdict-matches; {len(rows) - agree} mismatches")
    if agree != len(rows):
        for r in rows:
            if r[4] != r[5]:
                print("  MISMATCH:", r)
        sys.exit(1)


if __name__ == "__main__":
    sweep()
