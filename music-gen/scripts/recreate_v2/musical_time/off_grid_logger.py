#!/usr/bin/python3
"""Off-grid onset honest-log per c11 CLAP fetchability-ladder pattern."""
from __future__ import annotations

import json
import pathlib
from typing import Any, Dict, List


def append_off_grid(
    path: pathlib.Path,
    song_sha16: str,
    stem: str,
    off_grid_rows: List[Dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Deterministic sort by onset_s (or None-safe fallback).
    rows_sorted = sorted(
        off_grid_rows,
        key=lambda r: (r.get("onset_s") if r.get("onset_s") is not None else -1.0),
    )
    with path.open("a", encoding="utf-8") as fh:
        for r in rows_sorted:
            payload = {"song_sha16": song_sha16, "stem": stem, **r}
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
