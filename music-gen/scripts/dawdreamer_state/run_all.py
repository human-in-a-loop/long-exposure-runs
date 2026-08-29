#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:28:00Z
# cycle: 33
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround
# ---
"""Run P1 + P2 + P3 on all plugins and emit data/dawdreamer_state/verdict.json.

Verdict decision (rubric §2):
  WORKAROUND_FOUND     — >=1 path has both_deterministic_nonempty=True
                         on BOTH surge_xt AND dexed.
  PARTIAL_WORKAROUND   — >=1 path yields byte-deterministic non-empty
                         state on exactly one plugin.
  NO_WORKAROUND        — all three paths fail on both plugins.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

assert sys.executable == '/usr/bin/python3', sys.executable

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.dawdreamer_state import _shared as sh  # noqa: E402
from scripts.dawdreamer_state.probe_p1_iterate_parameters import run as run_p1  # noqa: E402
from scripts.dawdreamer_state.probe_p2_save_preset import run as run_p2  # noqa: E402
from scripts.dawdreamer_state.probe_p3_metadata_inspection import run as run_p3  # noqa: E402


PROBES = ("P1", "P2", "P3")
PLUGIN_KEYS = tuple(k for k, _ in sh.PLUGINS)


def _cell(res_for_path: dict, plugin_key: str) -> dict:
    r = res_for_path.get(plugin_key, {})
    return {
        "sha_run1": r.get("sha_run1"),
        "sha_run2": r.get("sha_run2"),
        "equal": bool(r.get("equal")),
        "empty": bool(r.get("empty", True)),
    }


def decide(per_plugin: dict) -> tuple[str, str | None]:
    """Return (verdict, winning_path)."""
    # For each path in canonical order, count plugins where it yielded
    # both_deterministic_nonempty.
    path_scores = {}
    for path in PROBES:
        good = [k for k in PLUGIN_KEYS
                if per_plugin[k][path]["equal"] and not per_plugin[k][path]["empty"]]
        path_scores[path] = good
    # Find a path good on BOTH plugins → WORKAROUND_FOUND.
    for path in PROBES:
        if len(path_scores[path]) == len(PLUGIN_KEYS):
            return "WORKAROUND_FOUND", path
    # Otherwise, find a path good on exactly one → PARTIAL_WORKAROUND.
    for path in PROBES:
        if len(path_scores[path]) >= 1:
            return "PARTIAL_WORKAROUND", path
    return "NO_WORKAROUND", None


def main() -> int:
    p1 = run_p1()
    p2 = run_p2()
    p3 = run_p3()
    per_plugin: dict = {}
    for k in PLUGIN_KEYS:
        per_plugin[k] = {
            "P1": _cell(p1, k),
            "P2": _cell(p2, k),
            "P3": _cell(p3, k),
        }
    per_path = {}
    for path, res in (("P1", p1), ("P2", p2), ("P3", p3)):
        good_all = all(
            per_plugin[k][path]["equal"] and not per_plugin[k][path]["empty"]
            for k in PLUGIN_KEYS
        )
        per_path[path] = {"both_deterministic_nonempty": good_all}
    verdict, winning = decide(per_plugin)
    rubric_hash_path = sh.data_dir() / "rubric_hash.txt"
    rubric_hash = rubric_hash_path.read_text().strip()
    midi_ref_sha = sh.compute_reference_midi_sha()
    obj = {
        "rubric_hash": rubric_hash,
        "verdict": verdict,
        "winning_path": winning,
        "per_plugin": per_plugin,
        "per_path": per_path,
        "midi_input_sha256": midi_ref_sha,
        "committed_at": "2026-08-29T05:30:00Z",
    }
    out = sh.data_dir() / "verdict.json"
    out.write_bytes(sh.canonical_json_bytes(obj) + b"\n")
    print(json.dumps(obj, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
