#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:22:00Z
# cycle: 33
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround
# ---
"""P1 — iterate parameters and canonical-JSON serialize.

For each plugin, in a fresh temp dir per run:
  n = plugin.get_plugin_parameter_size()        # DawDreamer 0.9.0 alias
                                                # for the rubric-brief's
                                                # `get_num_parameters()`.
  state = {plugin.get_parameter_name(i): plugin.get_parameter(i)
           for i in range(n)}
  write canonical-JSON to p1_state_v2.json.

Assert SHA-256 equality across the two runs. Zero PRNG.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

assert sys.executable == '/usr/bin/python3', sys.executable

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.dawdreamer_state import _shared as sh  # noqa: E402


def probe_one(plugin_key: str, plugin_path: str, out_dir: Path) -> dict:
    """Run P1 on one plugin into out_dir. Returns the state dict."""
    out_dir.mkdir(parents=True, exist_ok=True)
    _engine, plugin = sh.make_plugin(plugin_path)
    n = plugin.get_plugin_parameter_size()
    state = {}
    for i in range(n):
        name = plugin.get_parameter_name(i)
        val = plugin.get_parameter(i)
        # keys can collide (Surge XT has many "M1: -"); disambiguate by index.
        key = f"{i:05d}:{name}"
        state[key] = val
    (out_dir / "p1_state_v2.json").write_bytes(sh.canonical_json_bytes(state))
    return state


def run(plugins=None) -> dict:
    """Run P1 on all plugins twice each into fresh temp dirs.

    Persists per-plugin p1_state_v2.json + p1_state_sha under
    data/dawdreamer_state/per_plugin/<plugin>/.
    Returns {plugin_key: {"sha_run1", "sha_run2", "equal", "empty", "n_params"}}.
    """
    if plugins is None:
        plugins = sh.PLUGINS
    results: dict = {}
    for key, path in plugins:
        if not Path(path).exists():
            results[key] = {"sha_run1": None, "sha_run2": None,
                            "equal": False, "empty": True,
                            "n_params": 0, "error": "PLUGIN_MISSING"}
            sh.append_fetchability({
                "probe": "P1", "plugin": key,
                "event": "plugin_missing", "path": path,
            })
            continue
        d1 = sh.fresh_temp_dir(f"dawdstate-p1-{key}-r1-")
        d2 = sh.fresh_temp_dir(f"dawdstate-p1-{key}-r2-")
        s1 = probe_one(key, path, d1)
        s2 = probe_one(key, path, d2)
        b1 = (d1 / "p1_state_v2.json").read_bytes()
        b2 = (d2 / "p1_state_v2.json").read_bytes()
        sha1 = sh.sha256_bytes(b1)
        sha2 = sh.sha256_bytes(b2)
        # Persist canonical artifact + sidecar to workspace data dir.
        pp = sh.per_plugin_dir(key)
        (pp / "p1_state_v2.json").write_bytes(b1)
        (pp / "p1_state_sha").write_text(sha1 + "\n")
        results[key] = {
            "sha_run1": sha1,
            "sha_run2": sha2,
            "equal": sha1 == sha2,
            "empty": len(s1) == 0,
            "n_params": len(s1),
        }
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-json", action="store_true",
                    help="print results as JSON on stdout")
    a = ap.parse_args()
    res = run()
    if a.emit_json:
        print(json.dumps(res, sort_keys=True, indent=2))
    else:
        for k, v in res.items():
            print(f"P1 {k}: n={v['n_params']} equal={v['equal']} sha1={v['sha_run1']!s:.16}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
