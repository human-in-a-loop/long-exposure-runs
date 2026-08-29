#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:24:00Z
# cycle: 33
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround
# ---
"""P2 — save preset / save state.

The DawDreamer 0.9.0 API surface exposes `save_state(filepath: str) -> None`
(documented via its docstring "Save the state to a file"). It does NOT
expose `save_preset` verbatim. This probe:

  1. Checks for `save_preset` on the plugin. If absent (the empirical
     case), logs a fetchability_ladder row with the specific
     AttributeError-equivalent and the filtered `dir(plugin)` slice.
  2. Falls through to `save_state`. Writes to a file in a fresh temp
     dir, reads the raw bytes, hex-serializes into p2_preset_hex.
  3. Runs twice into fresh temp dirs and asserts SHA-256 equality
     on the p2_preset_hex bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

assert sys.executable == '/usr/bin/python3', sys.executable

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.dawdreamer_state import _shared as sh  # noqa: E402


def _dump_state_bytes(plugin_path: str, out_dir: Path) -> bytes | None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _engine, plugin = sh.make_plugin(plugin_path)
    # Prefer save_preset if the API ever grows it. Otherwise, fall to save_state.
    if hasattr(plugin, "save_preset"):
        target = out_dir / "state.preset"
        try:
            plugin.save_preset(str(target))
            b = target.read_bytes()
            sh.append_fetchability({
                "probe": "P2", "plugin": Path(plugin_path).stem,
                "event": "save_preset_used",
                "path": str(target), "bytes": len(b),
            })
            return b
        except Exception as exc:
            sh.append_fetchability({
                "probe": "P2", "plugin": Path(plugin_path).stem,
                "event": "save_preset_raised",
                "error_type": type(exc).__name__, "error": str(exc),
                "dir_save_prefix": sorted(
                    a for a in dir(plugin)
                    if a.startswith("save_") or a.startswith("preset")
                ),
            })
    else:
        sh.append_fetchability({
            "probe": "P2", "plugin": Path(plugin_path).stem,
            "event": "save_preset_absent",
            "attribute_error_equivalent": (
                f"AttributeError: 'PluginProcessor' object has no attribute 'save_preset'"
            ),
            "dir_save_prefix": sorted(
                a for a in dir(plugin)
                if a.startswith("save_") or a.startswith("preset")
            ),
        })
    # Fall through: use save_state.
    target = out_dir / "state.bin"
    try:
        plugin.save_state(str(target))
        b = target.read_bytes()
        sh.append_fetchability({
            "probe": "P2", "plugin": Path(plugin_path).stem,
            "event": "save_state_used",
            "path": str(target), "bytes": len(b),
        })
        return b
    except Exception as exc:
        sh.append_fetchability({
            "probe": "P2", "plugin": Path(plugin_path).stem,
            "event": "save_state_raised",
            "error_type": type(exc).__name__, "error": str(exc),
        })
        return None


def run(plugins=None) -> dict:
    if plugins is None:
        plugins = sh.PLUGINS
    results: dict = {}
    for key, path in plugins:
        if not Path(path).exists():
            results[key] = {"sha_run1": None, "sha_run2": None,
                            "equal": False, "empty": True,
                            "size": 0, "error": "PLUGIN_MISSING"}
            continue
        d1 = sh.fresh_temp_dir(f"dawdstate-p2-{key}-r1-")
        d2 = sh.fresh_temp_dir(f"dawdstate-p2-{key}-r2-")
        b1 = _dump_state_bytes(path, d1)
        b2 = _dump_state_bytes(path, d2)
        if b1 is None or b2 is None:
            results[key] = {
                "sha_run1": None, "sha_run2": None,
                "equal": False, "empty": True, "size": 0,
                "error": "SAVE_STATE_FAILED",
            }
            continue
        hex1 = b1.hex()
        hex2 = b2.hex()
        sha1 = hashlib.sha256(hex1.encode()).hexdigest()
        sha2 = hashlib.sha256(hex2.encode()).hexdigest()
        pp = sh.per_plugin_dir(key)
        (pp / "p2_preset_hex").write_text(hex1 + "\n")
        (pp / "p2_state_sha").write_text(sha1 + "\n")
        results[key] = {
            "sha_run1": sha1,
            "sha_run2": sha2,
            "equal": sha1 == sha2,
            "empty": len(b1) == 0,
            "size": len(b1),
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
            print(f"P2 {k}: size={v['size']} equal={v['equal']} sha1={v['sha_run1']!s:.16}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
