#!/usr/bin/python3
"""c83 S3 — zero-catch-up verification for songs landed by the restarted driver (PID 10247, hook live at birth).

created: 2026-09-06T21:10:00Z
cycle: 83
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/hook-at-birth-verification-c83

For every song whose transcription_manifest.json did NOT exist at c82 close (the 8 c82 songs are listed as the baseline;
their manifests were re-written 19:59:2xZ when the restarted driver re-walked them from stage_cache, so manifest mtime alone
is NOT a landing discriminator — invariant (d) disclosure vs the brief's "mtime > 19:59:26Z" rule): verify
canonical_v5_reindexed/ + sidecar exist, sidecar SHAs == disk, MIDI note_on == JSON starts per probe, and
sidecar_mtime - manifest_mtime <= 5 s (hook_at_birth). Then run reindex_hook.reindex_landed() and assert it is a
no-op ("present" for every song). Output: data/v5/corpus/hook_at_birth_c83.json.
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs; nothing modified.
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

_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)
sys.path.insert(0, str(_WS))
import mido  # noqa: E402
from scripts.v5 import reindex_hook as H  # noqa: E402

CORPUS = Path("data/v5/corpus")
OUT = CORPUS / "hook_at_birth_c83.json"
C82_BASELINE = ["252eb21ce7df7328", "31a164f845f8e27e", "88d247468cb6d49f", "51e433ade2a845e1", "cdd2717e52820ff6",
                "467fbeb2e3b019a0", "2b0370d9d0162c98", "a9587ccde1b333f5"]
RESTART_UTC = "2026-09-06T19:59:26Z"
PROBES = ["bass", "drums", "guitar", "other", "piano", "vocals", "full_mix"]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _iso(t: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def verify(sha16: str) -> dict:
    d = CORPUS / sha16
    tm = d / "transcription_manifest.json"
    sc = d / H.SIDECAR_NAME
    rd = d / "canonical_v5_reindexed"
    rec = {"sha16": sha16, "manifest_mtime": _iso(tm.stat().st_mtime), "sidecar_exists": sc.exists(), "reindexed_dir_exists": rd.exists()}
    if not sc.exists():
        rec["hook_at_birth"] = False
        rec["defect"] = "NO_SIDECAR_AT_LANDING"
        return rec
    side = json.loads(sc.read_text())
    rec["sidecar_mtime"] = _iso(sc.stat().st_mtime)
    rec["sidecar_minus_manifest_s"] = round(sc.stat().st_mtime - tm.stat().st_mtime, 3)
    rec["sidecar_sha_match"] = {p: side["midi_sha256"].get(p) == _sha(rd / f"{p}.mid") for p in PROBES if (rd / f"{p}.mid").exists()}
    rec["sidecar_sha_match"]["reindex_manifest"] = side["reindex_manifest_sha256"] == _sha(rd / "reindex_manifest.json")
    rm = json.loads((rd / "reindex_manifest.json").read_text())
    per = {}
    for p in PROBES:
        if not (rd / f"{p}.mid").exists():
            continue
        starts = sum(1 for e in json.loads((rd / f"{p}.reindexed.json").read_text()) if e["type"] == "start")
        n_on = sum(1 for tr in mido.MidiFile(rd / f"{p}.mid").tracks for m in tr if m.type == "note_on" and m.velocity > 0)
        st = rm["probes"][p]
        per[p] = {"json_starts": starts, "midi_note_on": n_on, "equal": starts == n_on, "n_paired": st["n_paired"], "n_unpaired": st["n_unpaired_starts"]}
    rec["per_probe"] = per
    rec["note_on_equals_starts_all"] = all(v["equal"] for v in per.values())
    rec["paired_total"] = sum(v["n_paired"] for v in per.values())
    rec["unpaired_total"] = sum(v["n_unpaired"] for v in per.values())
    rec["hook_at_birth"] = bool(all(rec["sidecar_sha_match"].values()) and rec["note_on_equals_starts_all"] and 0 <= rec["sidecar_minus_manifest_s"] <= 5.0)
    rec["hook_version"] = side.get("hook_version")
    return rec


def main() -> int:
    landed = sorted(p.parent.name for p in CORPUS.glob("*/transcription_manifest.json"))
    new = [s for s in landed if s not in C82_BASELINE]
    songs = {s: verify(s) for s in new}
    catchup = H.reindex_landed()
    non_noop = [x for x in catchup if x[1] != "present"]
    rec = {"schema_version": 1, "agent": "worker", "cycle": 83, "run_id": "run-2026-09-06T000000Z",
           "milestone": "M-V5-CORPUS-1/hook-at-birth-verification-c83", "restart_utc": RESTART_UTC, "new_driver_pid": 10247,
           "c82_baseline_songs": C82_BASELINE,
           "invariant_d_disclosure": "the 8 c82 baseline manifests carry mtime 19:59:23-19:59:32Z (re-written by the restarted driver's stage_cache re-walk); landing is discriminated by 'manifest absent at c82 close', not by manifest mtime",
           "n_landed_total": len(landed), "new_landings": new, "per_song": songs,
           "all_new_hook_at_birth": all(v["hook_at_birth"] for v in songs.values()) if songs else None,
           "reindex_landed_catch_up": [list(x) for x in catchup], "catch_up_is_noop": not non_noop, "n_non_noop": len(non_noop),
           "checked_utc": _iso(time.time())}
    OUT.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: rec[k] for k in ("n_landed_total", "new_landings", "all_new_hook_at_birth", "catch_up_is_noop")}, indent=1))
    for s, v in songs.items():
        print(f"  {s} hook_at_birth={v['hook_at_birth']} dt={v.get('sidecar_minus_manifest_s')}s paired={v.get('paired_total')} unpaired={v.get('unpaired_total')}")
    return 0 if rec["catch_up_is_noop"] else 5


if __name__ == "__main__":
    sys.exit(main())
