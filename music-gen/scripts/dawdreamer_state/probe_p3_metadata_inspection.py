#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:26:00Z
# cycle: 33
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround
# ---
"""P3 — metadata + method-surface inspection.

Calls plugin.get_plugin_parameters_description() (documented available
via `dir(plugin)` scan). Also probes the API for these candidate state
bindings, recording presence and (if callable safely with no args) a
short result summary:

  get_state_information, getStateInformation, save_state,
  get_state_chunk, getChunk, writeStateInformation, get_patch

Writes p3_metadata.json (canonical JSON) and p3_state_sha.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

assert sys.executable == '/usr/bin/python3', sys.executable

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.dawdreamer_state import _shared as sh  # noqa: E402

CANDIDATE_METHODS = (
    "get_state_information",
    "getStateInformation",
    "save_state",
    "get_state_chunk",
    "getChunk",
    "writeStateInformation",
    "get_patch",
)


def _describe_discovered(plugin) -> dict:
    """Presence and cheap descriptor for each candidate binding."""
    out = {}
    for m in CANDIDATE_METHODS:
        present = hasattr(plugin, m)
        info = {"present": present}
        if present:
            fn = getattr(plugin, m)
            doc = getattr(fn, "__doc__", None) or ""
            info["doc_head"] = doc.splitlines()[0] if doc else ""
            # Deliberately DO NOT record repr(fn) — CPython embeds the
            # object memory address, which breaks byte-determinism × 2
            # (each PluginProcessor is a fresh instance at a different
            # address). Documented deviation.
            # get_patch: report length only (values byte-identical
            # under P1 already; adding them here is redundant AND
            # empirically drifts on Dexed at fresh instantiation).
            if m == "get_patch":
                try:
                    patch = plugin.get_patch()
                    info["patch_len"] = len(patch)
                except Exception as exc:
                    info["error"] = f"{type(exc).__name__}: {exc}"
        out[m] = info
    return out


def probe_one(plugin_path: str) -> dict:
    _engine, plugin = sh.make_plugin(plugin_path)
    params_desc = plugin.get_plugin_parameters_description()
    # Normalize per-row keys (they are already dicts).
    params_desc_sorted = [
        {k: v for k, v in sorted(d.items())} for d in params_desc
    ]
    return {
        "plugin_parameters_description": params_desc_sorted,
        "discovered_methods": _describe_discovered(plugin),
        "n_params": len(params_desc_sorted),
    }


def run(plugins=None) -> dict:
    if plugins is None:
        plugins = sh.PLUGINS
    results: dict = {}
    for key, path in plugins:
        if not Path(path).exists():
            results[key] = {"sha_run1": None, "sha_run2": None,
                            "equal": False, "empty": True,
                            "n_params": 0, "error": "PLUGIN_MISSING"}
            continue
        d1 = probe_one(path)
        d2 = probe_one(path)
        b1 = sh.canonical_json_bytes(d1)
        b2 = sh.canonical_json_bytes(d2)
        sha1 = sh.sha256_bytes(b1)
        sha2 = sh.sha256_bytes(b2)
        pp = sh.per_plugin_dir(key)
        (pp / "p3_metadata.json").write_bytes(b1)
        (pp / "p3_state_sha").write_text(sha1 + "\n")
        results[key] = {
            "sha_run1": sha1,
            "sha_run2": sha2,
            "equal": sha1 == sha2,
            "empty": d1["n_params"] == 0,
            "n_params": d1["n_params"],
        }
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-json", action="store_true")
    a = ap.parse_args()
    res = run()
    if a.emit_json:
        print(json.dumps(res, sort_keys=True, indent=2))
    else:
        for k, v in res.items():
            print(f"P3 {k}: n={v['n_params']} equal={v['equal']} sha1={v['sha_run1']!s:.16}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
