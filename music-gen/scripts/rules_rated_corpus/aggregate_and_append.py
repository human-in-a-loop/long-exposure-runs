#!/usr/bin/env python3
# M-RULES-1/extraction/rated-corpus — aggregator + peer-shard writer.
#
# Author: cyd7bevdr@mozmail.com, cycle 40 (fork c320de981fda / clone-0).
#
# Reads all per-song rules_shard.jsonl files, validates each row via
# Layer-1 + Layer-2, deduplicates any inter-song rule_id collisions
# (keeping the row from the earliest canonical_index, i.e. earliest
# SHA-256 tiebreak position), and appends the resulting rows to the
# DEDICATED peer shard data/rules/ledger_rated_corpus.jsonl (or a
# caller-specified alternate path for determinism-check runs).
#
# The c9 synth ledger data/rules/ledger.jsonl is NEVER modified —
# preserving c26/c27/c28/c29/c30 canonical-aggregate-SHA anchor stability.

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.rules.ledger import write_rule  # noqa: E402
from scripts.rules.validate import validate_batch  # noqa: E402


def collect(out_dir: Path) -> Tuple[List[Dict], List[Dict], Dict]:
    """Return (unique_rows, duplicates_dropped, per_song_summary).

    Rows are ordered by rule_id ascending (canonical order for the shard).
    Duplicates: same rule_id emitted by 2+ songs → keep the one from the
    song with the lowest canonical_index (== lowest SHA-256 tiebreak
    position); drop the rest, recording the drop.
    """
    per_song_dir = out_dir / "per_song"
    per_song_summary: Dict[str, Dict] = {}
    by_rid: Dict[str, Tuple[int, Dict]] = {}
    duplicates: List[Dict] = []

    song_dirs = sorted(per_song_dir.iterdir())
    for sd in song_dirs:
        if not sd.is_dir():
            continue
        m = json.loads((sd / "stage_manifest.json").read_text())
        per_song_summary[m["song_id"]] = m
        shard = sd / "rules_shard.jsonl"
        if not shard.exists():
            continue
        idx = m["canonical_index"]
        for line in shard.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            rid = row["rule_id"]
            if rid in by_rid:
                prev_idx, prev_row = by_rid[rid]
                if idx < prev_idx:
                    # replace, previous becomes duplicate
                    duplicates.append({"rule_id": rid, "dropped_song_index": prev_idx,
                                       "kept_song_index": idx})
                    by_rid[rid] = (idx, row)
                else:
                    duplicates.append({"rule_id": rid, "dropped_song_index": idx,
                                       "kept_song_index": prev_idx})
            else:
                by_rid[rid] = (idx, row)

    unique_rows = [row for _, row in sorted(by_rid.values(), key=lambda t: t[1]["rule_id"])]
    return unique_rows, duplicates, per_song_summary


def write_shard(rows: List[Dict], shard_path: Path) -> None:
    """Append rows to the peer-shard ledger (create if missing).

    Uses c6 write_rule for Layer-1+Layer-2 validation at write time.
    """
    shard_path.parent.mkdir(parents=True, exist_ok=True)
    # Fresh shard on each aggregate run (this is a build-from-source
    # operation, not an incremental append).
    if shard_path.exists():
        shard_path.unlink()
    for r in rows:
        write_rule(r, shard_path)


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: aggregate_and_append.py <out_dir> <shard_path>", file=sys.stderr)
        return 2
    out_dir = Path(sys.argv[1])
    shard_path = Path(sys.argv[2])

    rows, dups, per_song = collect(out_dir)

    # Whole-batch Layer-1+Layer-2 revalidation (catches any inter-row
    # issues the per-song validate_row missed).
    errs = validate_batch(rows)
    if errs:
        print("AGGREGATE VALIDATION FAILED:", file=sys.stderr)
        for e in errs[:20]:
            print("  ", e, file=sys.stderr)
        return 3

    write_shard(rows, shard_path)

    per_type: Dict[str, int] = {}
    for r in rows:
        per_type[r["rule_type"]] = per_type.get(r["rule_type"], 0) + 1

    summary = {
        "shard_path": str(shard_path),
        "n_songs": len(per_song),
        "n_rows_aggregate": len(rows),
        "n_duplicates_dropped": len(dups),
        "per_type_counts": per_type,
        "per_song_counts": {sid: m["n_rows"] for sid, m in per_song.items()},
    }
    summary_p = out_dir / "aggregate_summary.json"
    summary_p.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    # Also write flat TSV: song_id, rule_type, n
    tsv_p = out_dir / "aggregate_summary.tsv"
    lines = ["song_id\trule_type\tn"]
    for sid, m in sorted(per_song.items()):
        for rt, n in sorted(m["per_type_counts"].items()):
            lines.append(f"{sid}\t{rt}\t{n}")
    tsv_p.write_text("\n".join(lines) + "\n")

    print(json.dumps({k: v for k, v in summary.items() if k not in ("per_song_counts",)},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
