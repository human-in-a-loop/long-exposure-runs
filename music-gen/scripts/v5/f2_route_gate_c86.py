#!/usr/bin/python3
"""c86 F2 Route-1 gate (operator guidance docs/guidance/guidance_2026-09-09_F2_velocity_decision.txt, sha16 8677bb0cd3f240a0).

Gate (research brief Q1): df (driver semantics, _sweep_hygiene_c27._disk_used_pct_user) <= 85 % at entry AND htdemucs
importable under the driver's pinned env (/usr/bin/python3 + recreate_v3.sub_env) AND one full-song separation of the
shortest focus song (WIG, 186 s) completes in <= 5 min into a tempdir. The fresh WIG stems are compared against the
c79 stage-cache SHAs (data/v5/corpus/252eb21ce7df7328/stage_cache/v5_htdemucs_6s/*/stage_manifest.json) — equality is
the cross-cycle x2 determinism proof for the separation step. Stems are deleted after hashing (score-and-delete).
No PRNG. Output: data/v5/gen/f2_route_gate_c86.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_WS = Path(__file__).resolve().parents[2]
os.chdir(_WS)
sys.path.insert(0, str(_WS))
if sys.executable != "/usr/bin/python3":
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

from scripts.v3_spine import recreate_v3 as _v3  # noqa: E402  READ-ONLY
from scripts.sound_match._sweep_hygiene_c27 import _disk_used_pct_user  # noqa: E402  READ-ONLY

WIG = "252eb21ce7df7328"
OUT = Path("data/v5/gen/f2_route_gate_c86.json")


def cached_stem_shas(sha16: str) -> dict:
    ms = sorted(Path(f"data/v5/corpus/{sha16}/stage_cache/v5_htdemucs_6s").glob("*/stage_manifest.json"))
    return json.loads(ms[0].read_text())["result"]["stems"] if ms else {}


def main() -> int:
    for k, v in _v3.sub_env().items():
        os.environ[k] = v
    rec = {"schema_version": 1, "cycle": 86, "agent": "worker", "run_id": "run-2026-09-06T000000Z",
           "guidance": {"path": "docs/guidance/guidance_2026-09-09_F2_velocity_decision.txt", "sha16": "8677bb0cd3f240a0"},
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    df = _disk_used_pct_user(str(_WS))
    rec["df_used_pct_driver_semantics"] = round(df, 2)
    rec["gate_df_le_85"] = df <= 85.0
    try:
        import torch  # noqa: F401
        from demucs.pretrained import get_model  # noqa: F401
        rec["gate_htdemucs_importable"] = True
        rec["torch_version"] = torch.__version__
    except Exception as e:  # noqa: BLE001
        rec["gate_htdemucs_importable"] = False
        rec["htdemucs_import_error"] = repr(e)
    if rec["gate_df_le_85"] and rec["gate_htdemucs_importable"]:
        man = json.loads(Path("data/v5/corpus/corpus_manifest.json").read_text())
        songs = man["songs"] if isinstance(man, dict) else man
        if isinstance(songs, dict):
            songs = list(songs.values())
        song = next(s for s in songs if s["sha16"] == WIG)
        with tempfile.TemporaryDirectory(prefix="f2_gate_c86_") as td:
            td = Path(td)
            t0 = time.time()
            full = td / "full.wav"
            subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", song["audio_path"],
                            "-ac", "2", "-ar", "44100", str(full)], check=True, env=_v3.sub_env())
            rec["decode_wall_s"] = round(time.time() - t0, 1)
            rec["full_wav_sha256"] = _v3.sha(full)
            t1 = time.time()
            shas = _v3._run_htdemucs_once(full, td / "stems")
            rec["separation_wall_s"] = round(time.time() - t1, 1)
            rec["gate_separation_le_300s"] = rec["separation_wall_s"] <= 300.0
            cached = cached_stem_shas(WIG)
            rec["fresh_stem_sha256"] = shas
            rec["c79_cached_stem_sha256"] = cached
            rec["cross_cycle_x2_equal"] = {k: shas.get(k) == cached.get(k) for k in sorted(set(shas) | set(cached))}
            rec["separation_x2_holds"] = all(rec["cross_cycle_x2_equal"].values()) and bool(cached)
            rec["tempdir"] = str(td)
            rec["df_peak_pct_driver_semantics"] = round(_disk_used_pct_user(str(_WS)), 2)
        rec["stems_deleted_after_hash"] = True
    else:
        rec["gate_separation_le_300s"] = None
    gates = [rec["gate_df_le_85"], rec["gate_htdemucs_importable"], bool(rec.get("gate_separation_le_300s"))]
    rec["route"] = "ROUTE_1_STEM_AUDIO" if all(gates) else "ROUTE_2_RULE_BASED"
    OUT.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    print(json.dumps(rec, sort_keys=True, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
