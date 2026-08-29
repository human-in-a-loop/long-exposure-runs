#!/usr/bin/env python3
"""Walk all palette_v2 example dirs; write assignment_ids_v2_expected.tsv,
validation_report.tsv, skip_manifest.json into data/palette_v2/schema/ (or
into --out-dir if specified). Deterministic; interpreter-guarded."""

import argparse
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3"

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent
sys.path.insert(0, str(_REPO))

from scripts.palette_v2.validate import validate_row, validate_batch  # noqa: E402
from scripts.palette_v2.provenance import known_rule_ids  # noqa: E402

EX_ROOT = _HERE / "examples"
STEMS = ("drums", "bass", "other", "mono")
DEFAULT_OUT = _REPO / "data" / "palette_v2" / "schema"


def _load_valid_rows():
    rows = []
    for stem in STEMS:
        for p in sorted((EX_ROOT / stem).glob("*.json")):
            with open(p, "r") as f:
                row = json.load(f)
            rows.append((str(p.relative_to(_REPO)), row))
    return rows


def _load_invalid_rows():
    rows = []
    for p in sorted((EX_ROOT / "planted_invalid").glob("*.json")):
        with open(p, "r") as f:
            row = json.load(f)
        rows.append((str(p.relative_to(_REPO)), row))
    return rows


def main(out_dir=None):
    out_dir = Path(out_dir) if out_dir else DEFAULT_OUT
    out_dir.mkdir(parents=True, exist_ok=True)

    kids = known_rule_ids()
    valid = _load_valid_rows()
    invalid = _load_invalid_rows()

    # assignment_ids_v2_expected.tsv — sorted-by-path, canonical
    aids_path = out_dir / "assignment_ids_v2_expected.tsv"
    lines = ["path\tassignment_id_v2\tstem\tinstrument\tformat"]
    for path, row in sorted(valid):
        aid = row.get("assignment_id_v2", "")
        stem = row.get("stem", "")
        inst = row.get("instrument", "")
        fmt = (row.get("pinned_state") or {}).get("format", "")
        lines.append(f"{path}\t{aid}\t{stem}\t{inst}\t{fmt}")
    aids_path.write_text("\n".join(lines) + "\n")

    # validation_report.tsv — per-file layer1+layer2 status
    rep_path = out_dir / "validation_report.tsv"
    rlines = ["path\tkind\tn_errors\tfirst_error"]
    # valid should have 0 errors each
    batch_errs = validate_batch([r for _, r in valid])
    per_file_errs = {p: [] for p, _ in valid}
    # (batch also checks duplicates; use validate_row per-file to attribute)
    for path, row in valid:
        errs = validate_row(row, known_ids=kids)
        per_file_errs[path] = errs
        first = errs[0] if errs else ""
        rlines.append(f"{path}\tvalid\t{len(errs)}\t{first}")
    # invalid should have >=1 error each
    for path, row in invalid:
        errs = validate_row(row, known_ids=kids)
        first = errs[0] if errs else ""
        rlines.append(f"{path}\tplanted_invalid\t{len(errs)}\t{first}")
    rep_path.write_text("\n".join(rlines) + "\n")

    # skip_manifest.json — documented skip reasons for non-VST3 rows in v2
    skip = {
        "format_v1_flat_only": {
            "reason": "sfizz + fluidsynth_gm rows MUST use format=v1_flat "
                      "(v2_iterated_params is enforced VST3-only by Layer 2 §8)",
            "affected_instruments": ["sfizz", "fluidsynth_gm"],
        }
    }
    (out_dir / "skip_manifest.json").write_text(json.dumps(skip, indent=2, sort_keys=True) + "\n")

    # summary
    n_valid_bad = sum(1 for p, _ in valid if len(per_file_errs[p]) > 0)
    n_invalid_good = sum(1 for path, row in invalid if len(validate_row(row, known_ids=kids)) == 0)
    print(f"valid: {len(valid)} (unexpected-errors: {n_valid_bad}, batch_errs: {len(batch_errs)})")
    print(f"invalid: {len(invalid)} (unexpected-passes: {n_invalid_good})")
    print(f"out_dir: {out_dir}")
    return 0 if (n_valid_bad == 0 and n_invalid_good == 0) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()
    sys.exit(main(out_dir=args.out_dir))
