#!/usr/bin/env python3
# c41 harmonic-window-refinement — aggregate + verdict.
#
# NO PRNG. Interpreter-guarded. No sidecar_nonfactor imports.

import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.rules_harmonic_window_v2 import harmonic_wrapper  # noqa: E402

FLOOR_ROWS_PER_SONG = 5
LANDS_MIN_SONGS = 36
PARTIAL_MIN_SONGS = 20


def _cell_stats(out_dir: Path, cell: str, song_ids: List[str]) -> Dict:
    total_rows = 0
    songs_above_floor = 0
    songs_below_floor = 0
    wall_total = 0.0
    per_song: List[Dict] = []
    for sid in song_ids:
        mp = out_dir / "per_song" / sid / cell / "stage_manifest.json"
        m = json.loads(mp.read_text())
        n = m["n_rows"]
        total_rows += n
        wall_total += m["wall_clock_s"]
        if n >= FLOOR_ROWS_PER_SONG:
            songs_above_floor += 1
        else:
            songs_below_floor += 1
        per_song.append({"song_id": sid, "band": m["band"], "n_rows": n,
                         "wall_clock_s": m["wall_clock_s"]})
    n_songs = len(song_ids)
    return {
        "cell": cell,
        "n_songs": n_songs,
        "total_rows": total_rows,
        "mean_rows_per_song": (total_rows / n_songs) if n_songs else 0.0,
        "songs_above_floor": songs_above_floor,
        "songs_below_floor": songs_below_floor,
        "wall_clock_s": round(wall_total, 3),
        "per_song": per_song,
    }


def _pick_winner(stats: List[Dict]) -> Dict:
    # Primary: max mean_rows_per_song; tie-break: max songs_above_floor;
    # then lexicographic cell name.
    return sorted(
        stats,
        key=lambda s: (-s["mean_rows_per_song"], -s["songs_above_floor"], s["cell"]),
    )[0]


def _classify(winner: Dict) -> str:
    if winner["songs_above_floor"] >= LANDS_MIN_SONGS:
        return "HARMONIC_v2_LANDS"
    if winner["songs_above_floor"] >= PARTIAL_MIN_SONGS:
        return "HARMONIC_v2_PARTIAL"
    return "HARMONIC_v2_INSUFFICIENT"


def aggregate(out_dir: Path, song_manifest: Path, rubric_hash_p: Path) -> Dict:
    songs = json.loads(song_manifest.read_text())["songs"]
    song_ids = [s["song_id"] for s in songs]

    stats: List[Dict] = []
    grid_rows: List[str] = []
    grid_rows.append("cell\tn_songs\ttotal_rows\tmean_rows_per_song\tsongs_above_floor\tsongs_below_floor\twall_clock_s")
    for hop, policy in harmonic_wrapper.GRID_CELLS:
        cell = harmonic_wrapper.cell_key(hop, policy)
        s = _cell_stats(out_dir, cell, song_ids)
        stats.append(s)
        grid_rows.append(
            f"{cell}\t{s['n_songs']}\t{s['total_rows']}\t{s['mean_rows_per_song']:.4f}"
            f"\t{s['songs_above_floor']}\t{s['songs_below_floor']}\t{s['wall_clock_s']}"
        )

    winner = _pick_winner(stats)
    verdict = _classify(winner)

    # Write per_cell_summary.tsv
    per_cell_tsv = out_dir / "per_cell_summary.tsv"
    per_cell_tsv.write_text("\n".join(grid_rows) + "\n")

    # Write grid_summary.tsv (per-cell per-song).
    grid_summary_rows = ["cell\tsong_id\tband\tn_rows\twall_clock_s"]
    for s in stats:
        for ps in s["per_song"]:
            grid_summary_rows.append(
                f"{s['cell']}\t{ps['song_id']}\t{ps['band']}\t{ps['n_rows']}\t{ps['wall_clock_s']}"
            )
    (out_dir / "grid_summary.tsv").write_text("\n".join(grid_summary_rows) + "\n")

    rubric_hash = rubric_hash_p.read_text().strip()

    verdict_json = {
        "verdict": verdict,
        "rubric_hash": rubric_hash,
        "winning_cell": winner["cell"],
        "winner_stats": {k: v for k, v in winner.items() if k != "per_song"},
        "per_cell": [{k: v for k, v in s.items() if k != "per_song"} for s in stats],
        "n_songs": len(song_ids),
        "floor_rows_per_song": FLOOR_ROWS_PER_SONG,
        "lands_min_songs": LANDS_MIN_SONGS,
        "partial_min_songs": PARTIAL_MIN_SONGS,
    }
    (out_dir / "verdict.json").write_text(json.dumps(verdict_json, indent=2, sort_keys=True) + "\n")

    # Peer-shard emission on LANDS only.
    peer_shard_path = None
    if verdict == "HARMONIC_v2_LANDS":
        peer_shard_path = REPO / "data" / "rules" / "ledger_rated_corpus_harmonic_v2.jsonl"
        winner_cell = winner["cell"]
        rows: List[str] = []
        for sid in song_ids:
            shard_p = out_dir / "per_song" / sid / winner_cell / "rules_shard.jsonl"
            content = shard_p.read_text()
            if content:
                rows.append(content)
        peer_shard_path.write_text("".join(rows))

    return {
        "verdict": verdict,
        "winning_cell": winner["cell"],
        "peer_shard_path": str(peer_shard_path) if peer_shard_path else None,
        "verdict_json_path": str(out_dir / "verdict.json"),
    }


def main() -> int:
    if len(sys.argv) < 4:
        print("usage: aggregate_and_verdict.py <out_dir> <song_manifest.json> <rubric_hash.txt>",
              file=sys.stderr)
        return 2
    out_dir = Path(sys.argv[1])
    song_manifest = Path(sys.argv[2])
    rubric_hash_p = Path(sys.argv[3])
    result = aggregate(out_dir, song_manifest, rubric_hash_p)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
