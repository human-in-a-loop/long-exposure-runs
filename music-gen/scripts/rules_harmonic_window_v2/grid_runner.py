#!/usr/bin/env python3
# c41 harmonic-window-refinement grid runner.
#
# For each of 43 songs × 6 grid cells:
#   1. call harmonic_wrapper.extract(...)
#   2. decorate rows with rule_id/event_id/ts via c9 _finish semantics
#   3. Layer-1+Layer-2 validate each row
#   4. write per_song/<song_id>/<cell>/rules_shard.jsonl + stage_manifest.json
#
# Idempotent per (song, cell): stage_manifest presence → skip.
# NO PRNG. Interpreter-guarded. No sidecar_nonfactor imports.

import json
import sys
import time
from pathlib import Path
from typing import Dict, List

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import music21  # noqa: E402

from scripts.rules.extract._common import (  # noqa: E402
    FIXED_TS, DEFAULT_TEMPO_BPM,
    set_extraction_context, reset_extraction_context, event_id_for,
)
from scripts.rules.extract import harmonic as c9_harmonic  # noqa: E402
from scripts.rules.rule_id import derive_rule_id  # noqa: E402
from scripts.rules.validate import validate_row  # noqa: E402

from scripts.rules_harmonic_window_v2 import harmonic_wrapper  # noqa: E402


def _finish(rule: Dict) -> Dict:
    rule["event_type"] = "rule"
    rule["schema_v"] = 1
    rule["ts"] = FIXED_TS
    rule["extractor"] = c9_harmonic.EXTRACTOR
    rule["extractor_version"] = c9_harmonic.EXTRACTOR_VERSION
    rid = derive_rule_id(rule)
    rule["rule_id"] = rid
    rule["event_id"] = event_id_for(rid)
    return rule


def run_song_cell(song: Dict, hop: float, policy: str, out_dir: Path) -> Dict:
    song_id = song["song_id"]
    cell = harmonic_wrapper.cell_key(hop, policy)
    per_dir = out_dir / "per_song" / song_id / cell
    per_dir.mkdir(parents=True, exist_ok=True)
    manifest_p = per_dir / "stage_manifest.json"
    if manifest_p.exists():
        return json.loads(manifest_p.read_text())

    score_p = Path(song["merged_musicxml"])
    bp_dir = Path(song["bp_dir"])

    wall_start = time.monotonic()
    n_rows = 0
    n_invalid = 0
    error = ""
    valid_rows: List[Dict] = []
    try:
        set_extraction_context(f"harmonic_v2::{song_id}", score_p, bp_dir)
        score = music21.converter.parse(str(score_p))
        candidates = harmonic_wrapper.extract(
            score, window_hop_s=hop, progression_min_unique=policy,
            tempo_bpm=DEFAULT_TEMPO_BPM,
        )
        finished = [_finish(c) for c in candidates]
        for r in finished:
            errs = validate_row(r)
            if errs:
                n_invalid += 1
            else:
                valid_rows.append(r)
        n_rows = len(valid_rows)
    except Exception as exc:
        import traceback
        error = traceback.format_exc()
        _ = exc
    finally:
        reset_extraction_context()

    wall = round(time.monotonic() - wall_start, 3)
    # Sort rows by rule_id for byte-deterministic shard file.
    valid_rows.sort(key=lambda r: r["rule_id"])
    shard_p = per_dir / "rules_shard.jsonl"
    shard_p.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in valid_rows))

    manifest = {
        "song_id": song_id,
        "band": song["band"],
        "source": song["source"],
        "cell": cell,
        "window_hop_s": hop,
        "progression_min_unique": policy,
        "n_rows": n_rows,
        "n_invalid": n_invalid,
        "wall_clock_s": wall,
        "shard_path": str(shard_p.relative_to(out_dir)),
        "error": error,
    }
    manifest_p.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def run_grid(manifest_path: Path, out_dir: Path) -> Dict:
    songs = json.loads(manifest_path.read_text())["songs"]
    out_dir.mkdir(parents=True, exist_ok=True)
    per_cell: Dict[str, List[Dict]] = {}
    for hop, policy in harmonic_wrapper.GRID_CELLS:
        cell = harmonic_wrapper.cell_key(hop, policy)
        per_cell[cell] = []
        for song in songs:
            m = run_song_cell(song, hop, policy, out_dir)
            per_cell[cell].append(m)
    return per_cell


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: grid_runner.py <song_manifest.json> <out_dir>", file=sys.stderr)
        return 2
    manifest_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    per_cell = run_grid(manifest_path, out_dir)
    # brief stdout summary
    for cell, mans in per_cell.items():
        n = len(mans)
        total = sum(m["n_rows"] for m in mans)
        mean = total / n if n else 0.0
        print(f"[{cell}] songs={n} total_rows={total} mean_rows_per_song={mean:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
