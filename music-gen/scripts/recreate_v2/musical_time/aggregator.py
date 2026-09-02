#!/usr/bin/python3
"""D4 Per-repeat consensus aggregator + per-repeat deviations table.

For a detected loop of N bars over K repeats within chosen_section, fold all
onset events into loop grid; per (grid_position_mod_loop, stem) vote presence
and record median deviation. Emit both consensus loop and per-repeat
deviations, plus a round-trip self-consistency check.
"""
from __future__ import annotations

import csv
import json
import math
import pathlib
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np


def build_per_stem_notes(
    quantized_by_stem: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, List[Tuple[int, float]]]:
    """Return {stem: [(grid_position, grid_deviation_ms), ...]} — sorted."""
    out: Dict[str, List[Tuple[int, float]]] = {}
    for stem, notes in quantized_by_stem.items():
        rows = [(int(n["grid_position"]), float(n["grid_deviation_ms"])) for n in notes]
        rows.sort(key=lambda x: (x[0], x[1]))
        out[stem] = rows
    return out


def aggregate_consensus(
    per_stem_notes: Dict[str, List[Tuple[int, float]]],
    loop_length_bars: int,
    n_repeats: int,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Return (consensus_dict, per_repeat_rows)."""
    if loop_length_bars <= 0 or n_repeats <= 0:
        return (
            {
                "loop_length_bars": int(loop_length_bars),
                "n_repeats": int(n_repeats),
                "positions": [],
                "reason": "no_loop_detected_or_no_repeats",
            },
            [],
        )

    positions_per_loop = loop_length_bars * 16
    quorum = math.ceil(n_repeats / 2)

    # Bucket by (repeat_index, position_mod_loop, stem): last-wins on dupes,
    # but we keep all deviations to compute median across present repeats.
    # dev_bucket[(mod, stem)][repeat_idx] = deviation
    dev_bucket: Dict[Tuple[int, str], Dict[int, float]] = {}
    for stem, notes in per_stem_notes.items():
        for pos, dev in notes:
            repeat_idx = pos // positions_per_loop
            if repeat_idx < 0 or repeat_idx >= n_repeats:
                continue
            mod = pos % positions_per_loop
            key = (mod, stem)
            dev_bucket.setdefault(key, {})[repeat_idx] = float(dev)

    # Consensus positions.
    positions: List[Dict[str, Any]] = []
    keys_sorted = sorted(dev_bucket.keys(), key=lambda k: (k[0], k[1]))
    for (mod, stem) in keys_sorted:
        per_rep = dev_bucket[(mod, stem)]
        k_present = len(per_rep)
        presence = bool(k_present >= quorum)
        median_dev = float(np.median(list(per_rep.values()))) if k_present else 0.0
        positions.append({
            "grid_pos_mod": int(mod),
            "stem": stem,
            "presence": presence,
            "median_deviation_ms": median_dev,
            "k_present": int(k_present),
        })

    # Per-repeat deviations rows.
    all_stems_mods = sorted({(m, s) for (m, s) in dev_bucket.keys()},
                            key=lambda x: (x[0], x[1]))
    consensus_lookup = {(p["grid_pos_mod"], p["stem"]): p for p in positions}

    per_repeat_rows: List[Dict[str, Any]] = []
    for repeat_index in range(n_repeats):
        for (mod, stem) in all_stems_mods:
            per_rep = dev_bucket.get((mod, stem), {})
            present_here = repeat_index in per_rep
            dev_here = float(per_rep.get(repeat_index, 0.0)) if present_here else 0.0
            consensus_row = consensus_lookup.get((mod, stem))
            present_in_consensus = bool(consensus_row["presence"]) if consensus_row else False
            disagreement = bool(present_here != present_in_consensus)
            per_repeat_rows.append({
                "repeat_index": int(repeat_index),
                "grid_position_mod_loop": int(mod),
                "stem": stem,
                "present_here": present_here,
                "deviation_ms_here": dev_here,
                "present_in_consensus": present_in_consensus,
                "disagreement": disagreement,
            })

    return (
        {
            "loop_length_bars": int(loop_length_bars),
            "n_repeats": int(n_repeats),
            "positions": positions,
        },
        per_repeat_rows,
    )


def consensus_from_per_repeat(rows: List[Dict[str, Any]], loop_length_bars: int) -> Dict[str, Any]:
    """Round-trip: reconstruct consensus from per-repeat rows.

    Uses the same quorum rule. Median deviation over repeats where
    ``present_here=True``.
    """
    if not rows:
        return {"loop_length_bars": int(loop_length_bars), "n_repeats": 0, "positions": []}

    n_repeats = max(r["repeat_index"] for r in rows) + 1
    quorum = math.ceil(n_repeats / 2)

    bucket: Dict[Tuple[int, str], List[float]] = {}
    for r in rows:
        if r["present_here"]:
            key = (int(r["grid_position_mod_loop"]), r["stem"])
            bucket.setdefault(key, []).append(float(r["deviation_ms_here"]))

    positions: List[Dict[str, Any]] = []
    for key in sorted(bucket.keys(), key=lambda x: (x[0], x[1])):
        devs = bucket[key]
        k_present = len(devs)
        positions.append({
            "grid_pos_mod": int(key[0]),
            "stem": key[1],
            "presence": bool(k_present >= quorum),
            "median_deviation_ms": float(np.median(devs)),
            "k_present": int(k_present),
        })
    return {
        "loop_length_bars": int(loop_length_bars),
        "n_repeats": int(n_repeats),
        "positions": positions,
    }


def emit_consensus(out_dir: pathlib.Path, consensus: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "consensus_loop.json").write_text(
        json.dumps(consensus, indent=2, sort_keys=True)
    )


def emit_per_repeat_tsv(out_dir: pathlib.Path, rows: List[Dict[str, Any]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "per_repeat_deviations.tsv"
    cols = [
        "repeat_index", "grid_position_mod_loop", "stem",
        "present_here", "deviation_ms_here",
        "present_in_consensus", "disagreement",
    ]
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(cols)
        for r in sorted(
            rows,
            key=lambda x: (x["repeat_index"], x["grid_position_mod_loop"], x["stem"]),
        ):
            w.writerow([r[c] for c in cols])


def round_trip_ok(consensus: Dict[str, Any], reconstructed: Dict[str, Any]) -> bool:
    """Byte-compatible check: positions match on (grid_pos_mod, stem, presence)."""
    def key(p: Dict[str, Any]) -> Tuple:
        return (int(p["grid_pos_mod"]), p["stem"], bool(p["presence"]))
    a = {key(p) for p in consensus.get("positions", [])}
    b = {key(p) for p in reconstructed.get("positions", [])}
    return a == b
