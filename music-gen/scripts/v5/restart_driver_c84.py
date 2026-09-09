#!/usr/bin/python3
"""c84 P0.1 + P0.3 — liveness record for the dead driver and checkpointed relaunch from its resume point.

created: 2026-09-09T20:55:00Z
cycle: 84
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/driver-restart-c84

P0.1: os.kill(10247, 0) result, df in driver semantics (used/(used+avail)), landed/sidecar counts ->
      data/v5/logs/c84_p0_liveness.txt.
P0.3: verify transcribe_full_length.py sha c1c6b2df… and reindex_hook.py sha a63434a6… unchanged; verify the stage-cache
      env-pin key (d9241686…) is reproduced by build_env_pin_manifest() under the driver's pinned env (cache hits expected);
      relaunch the PINNED c79 command via READ-ONLY scripts/v3_spine/launch_detached.launch_detached (no --songs: the
      driver re-walks landed songs from stage_cache and resumes 0e1e8f20592db366 at muscriptor:full_mix, then lands
      cc0693b4a24f64b2). _transient/ is NOT touched by hand (the driver consumes/deletes it).
      -> data/v5/logs/transcribe_full_c84.launch.json.
Discipline: no kill -9 (nothing to kill); no install; df at open recorded; escalation iff avail < 4.5 GB.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)
_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)
_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)
sys.path.insert(0, str(_WS))
from scripts.v3_spine.launch_detached import launch_detached  # noqa: E402  READ-ONLY

OLD_PID = 10247
CMD = ["/usr/bin/python3", "scripts/v5/transcribe_full_length.py", "--manifest", "data/v5/corpus/corpus_manifest.json",
       "--tempo-dir", "data/v5/corpus"]
LOG = Path("data/v5/logs/transcribe_full_c79.log")
EXPECT = {"scripts/v5/transcribe_full_length.py": "c1c6b2df923db13c", "scripts/v5/reindex_hook.py": "a63434a60cc12b83",
          "scripts/v3_spine/launch_detached.py": "999045f373f9d476"}
CACHE_KEY = "d924168629978d1fedab52a3a10c615b21b8ae4ece443d506e779d5dcea6439d"
RESUME_SONG = "0e1e8f20592db366"


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def df() -> dict:
    st = os.statvfs(".")
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    avail = st.f_bavail * st.f_frsize
    return {"used_pct": round(100 * used / (used + avail), 2), "avail_gb": round(avail / 1e9, 3), "ts": now()}


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def main() -> int:
    C = Path("data/v5/corpus")
    landed = sorted(p.parent.name for p in C.glob("*/transcription_manifest.json"))
    side = sorted(p.parent.name for p in C.glob("*/canonical_v5_reindexed_sha256.json"))
    d0 = df()
    was_alive = alive(OLD_PID)
    partial = {s: sorted(os.listdir(C / s)) for s in ("0e1e8f20592db366", "cc0693b4a24f64b2") if (C / s).exists()}
    live = (f"c84 P0 liveness {now()} | pid={OLD_PID} alive={was_alive} (os.kill(pid,0); died with the container 2026-09-07 03:4xZ per operator) | "
            f"log={LOG} mtime={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(LOG.stat().st_mtime))} | "
            f"df_driver_semantics used_pct={d0['used_pct']} avail_gb={d0['avail_gb']} (abort ceiling 90; escalation threshold avail<4.5GB -> "
            f"{'TRIGGERED' if d0['avail_gb'] < 4.5 else 'not triggered'}) | landed={len(landed)}/26 sidecar={len(side)}/26 | "
            f"partial dirs={partial} | c100-c127 lost to outage (ONE POR line)\n")
    Path("data/v5/logs/c84_p0_liveness.txt").write_text(live)
    print(live)
    shas = {k: hashlib.sha256(Path(k).read_bytes()).hexdigest() for k in EXPECT}
    sha_ok = {k: shas[k].startswith(v) for k, v in EXPECT.items()}
    if not all(sha_ok.values()):
        raise SystemExit(f"FROZEN driver/hook sha mismatch: {sha_ok} — FD-1 halt, no launch")
    from scripts.v3_spine.v3_pipeline.env_pin import build_env_pin_manifest  # noqa: E402
    pin_now = build_env_pin_manifest()["env_pin_sha256"]
    if pin_now != CACHE_KEY:
        raise SystemExit(f"stage-cache env-pin key drift: now {pin_now[:16]} != {CACHE_KEY[:16]} — a relaunch would cache-miss every song; FD-1 halt")
    if was_alive:
        raise SystemExit("old PID still alive — not relaunching")
    d1 = df()
    if d1["used_pct"] >= 90.0:
        raise SystemExit(f"df {d1['used_pct']} >= 90 abort ceiling — no launch")
    pid = launch_detached(CMD, LOG, workdir=_WS)
    time.sleep(8)
    rec = {"schema_version": 1, "cycle": 84, "agent": "worker", "run_id": "run-2026-09-06T000000Z",
           "milestone": "M-V5-CORPUS-1/driver-restart-c84", "old_pid": OLD_PID, "old_pid_alive_before": was_alive,
           "old_death": "container restart 2026-09-07 03:32Z (operator guidance 2026-09-09); last log line 03:42:26Z at 0e1e8f20592db366 muscriptor:full_mix",
           "cmd": CMD, "launcher": "scripts/v3_spine/launch_detached.launch_detached (READ-ONLY; start_new_session=True)",
           "log": str(LOG), "new_pid": pid, "launched_utc": now(), "running_after_8s": alive(pid),
           "driver_sha256_at_launch": shas["scripts/v5/transcribe_full_length.py"], "reindex_hook_sha256_at_launch": shas["scripts/v5/reindex_hook.py"],
           "frozen_sha_prefix_ok": sha_ok, "stage_cache_env_pin_key": CACHE_KEY, "env_pin_key_reproduced_under_pinned_env": pin_now == CACHE_KEY,
           "resume_song": RESUME_SONG, "resume_stage": "muscriptor:full_mix (6 probes cached in stage_cache; _transient/full.wav + stems_full present, consumed by the driver — not deleted by hand)",
           "then": "cc0693b4a24f64b2 (last in v5_priority_rank order) from decode_full",
           "df_trajectory": [d0, d1, df()], "landed_at_launch": len(landed), "sidecar_at_launch": len(side),
           "cache_hits": "filled at close by tools/_emit_c84_ledger_events.py from the log (per-stage cache_hit flags for the resume song)",
           "hook_live_at_birth": True, "no_install_this_cycle": True,
           "resume_command": "PYTHONPATH=. /usr/bin/python3 scripts/v5/transcribe_full_length.py --manifest data/v5/corpus/corpus_manifest.json --tempo-dir data/v5/corpus (stage_cache resumes; wrap with launch_detached)"}
    Path("data/v5/logs/transcribe_full_c84.launch.json").write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: rec[k] for k in ("new_pid", "running_after_8s", "launched_utc", "env_pin_key_reproduced_under_pinned_env")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
