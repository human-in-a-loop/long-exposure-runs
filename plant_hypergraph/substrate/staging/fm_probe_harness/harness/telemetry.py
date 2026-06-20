# PhytoGraph M1.8 — append-only JSONL telemetry + replay aggregator. cycle 2, worker.
"""Telemetry log.

Format: one JSON object per line. Writes are flushed per line so a crash
mid-cycle preserves prior calls. The cycle USD total is computed by replaying
the file at process start, which makes the $500/cycle cap durable across
process restarts within the same cycle_id.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


REQUIRED_FIELDS = (
    "ts_iso", "cycle_id", "provider", "model_id", "prompt_template_id",
    "tokens_in", "tokens_out", "cost_usd", "latency_s", "status", "mode",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class TelemetryLog:
    def __init__(self, path: os.PathLike | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            # Drop a header comment line. The reader ignores lines starting with '#'.
            with open(self.path, "a") as f:
                f.write(
                    "# PhytoGraph M1.8 fm_probe_harness cost_telemetry.jsonl — "
                    "append-only; one JSON object per line; lines starting with # are comments.\n"
                )

    def append(self, record: Dict[str, Any]) -> None:
        missing = [k for k in REQUIRED_FIELDS if k not in record]
        if missing:
            raise ValueError(f"telemetry record missing required fields: {missing}")
        line = json.dumps(record, separators=(",", ":"), sort_keys=True)
        with open(self.path, "a") as f:
            f.write(line + "\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                pass

    def iter_records(self, cycle_id: Optional[str] = None) -> Iterable[Dict[str, Any]]:
        if not self.path.exists():
            return
        with open(self.path) as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                try:
                    rec = json.loads(s)
                except json.JSONDecodeError:
                    # Skip malformed lines (e.g. partial write after a crash).
                    continue
                if cycle_id is None or rec.get("cycle_id") == cycle_id:
                    yield rec

    def cycle_total_usd(self, cycle_id: str) -> float:
        total = 0.0
        for rec in self.iter_records(cycle_id):
            try:
                total += float(rec.get("cost_usd", 0.0))
            except (TypeError, ValueError):
                continue
        return total

    def count(self, cycle_id: Optional[str] = None) -> int:
        return sum(1 for _ in self.iter_records(cycle_id))
