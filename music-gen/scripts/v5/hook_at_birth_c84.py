#!/usr/bin/python3
"""c84 P0.4 — hook-at-birth verification for every song landed AFTER c83 close (baseline = the 9 songs known at c83 close).

created: 2026-09-09T20:52:00Z
cycle: 84
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/hook-at-birth-verification-c84

Sibling of the c83 verifier (READ-ONLY, untouched): the baseline list is a parameter (--baseline-from, default = the c83
hook_at_birth record's baseline + its new landings = the 9 songs with a sidecar at c83 close). Same per-song checks:
sidecar SHAs == disk; MIDI note_on == JSON starts per probe; sidecar written within 5 s of the manifest (hook at birth).
Then reindex_hook.reindex_landed() must be a no-op. Discriminator = 'absent at c83 close' (manifest mtime is NOT a
landing discriminator — the driver re-walks landed songs from stage_cache and rewrites manifests; invariant (d)).
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs; nothing modified except the record.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)
sys.path.insert(0, str(_WS))
from scripts.v5 import reindex_hook as H  # noqa: E402
from scripts.v5.hook_at_birth_c83 import verify, C82_BASELINE  # noqa: E402  READ-ONLY per-song check

CORPUS = Path("data/v5/corpus")
C83_KNOWN = sorted(set(C82_BASELINE) | {"1d9ac896511ebcd4"})  # 9 songs with a sidecar at c83 close


def _iso(t: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline-from", default="data/v5/corpus/hook_at_birth_c83.json",
                    help="c83 record; baseline = its c82 baseline + its new landings")
    ap.add_argument("--out", default="data/v5/corpus/hook_at_birth_c84.json")
    args = ap.parse_args(argv)
    baseline = list(C83_KNOWN)
    bp = Path(args.baseline_from)
    if bp.exists():
        r = json.loads(bp.read_text())
        baseline = sorted(set(r["c82_baseline_songs"]) | set(r["new_landings"]))
    landed = sorted(p.parent.name for p in CORPUS.glob("*/transcription_manifest.json"))
    new = [s for s in landed if s not in baseline]
    songs = {s: verify(s) for s in new}
    catchup = H.reindex_landed()
    non_noop = [x for x in catchup if x[1] != "present"]
    rec = {"schema_version": 1, "agent": "worker", "cycle": 84, "run_id": "run-2026-09-06T000000Z",
           "milestone": "M-V5-CORPUS-1/hook-at-birth-verification-c84",
           "baseline_known_at_c83_close": baseline, "baseline_source": str(bp),
           "invariant_d_disclosure": "landing is discriminated by 'sidecar absent at c83 close'; manifest mtime is NOT a discriminator (stage_cache re-walk rewrites manifests on every driver start)",
           "n_landed_total": len(landed), "new_landings_since_c83": new, "per_song": songs,
           "all_new_hook_at_birth": all(v["hook_at_birth"] for v in songs.values()) if songs else None,
           "reindex_landed_catch_up": [list(x) for x in catchup], "catch_up_is_noop": not non_noop, "n_non_noop": len(non_noop),
           "checked_utc": _iso(time.time())}
    Path(args.out).write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: rec[k] for k in ("n_landed_total", "new_landings_since_c83", "all_new_hook_at_birth", "catch_up_is_noop")}, indent=1))
    for s, v in songs.items():
        print(f"  {s} hook_at_birth={v['hook_at_birth']} dt={v.get('sidecar_minus_manifest_s')}s paired={v.get('paired_total')} unpaired={v.get('unpaired_total')}")
    return 0 if rec["catch_up_is_noop"] else 5


if __name__ == "__main__":
    sys.exit(main())
