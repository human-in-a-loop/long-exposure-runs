"""Measure feature-extraction throughput and ETA."""
# created: 2026-08-29T06:00:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: _infra/extraction-liveness-tsv-clone-0
import sys
assert sys.executable == "/usr/bin/python3", sys.executable
import os, time, datetime
from pathlib import Path

CACHE = Path("data/ear_v0/per_song_features")
TSV = Path("data/ear_v0/extraction_liveness.tsv")
TOTAL = 43

files = sorted(CACHE.glob("*.npy"), key=lambda p: p.stat().st_mtime)
n = len(files)
if n == 0:
    sec_per_song = 0.0
    eta_iso = "N/A"
else:
    t_first = files[0].stat().st_mtime
    t_last = files[-1].stat().st_mtime
    span = t_last - t_first if n > 1 else 0.0
    sec_per_song = (span / max(1, n - 1)) if n > 1 else 0.0
    remaining = max(0, TOTAL - n)
    eta_epoch = time.time() + remaining * (sec_per_song if sec_per_song > 0 else 120.0)
    eta_iso = datetime.datetime.fromtimestamp(eta_epoch, datetime.UTC).isoformat(timespec="seconds")

now_iso = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
newest_iso = datetime.datetime.fromtimestamp(files[-1].stat().st_mtime, datetime.UTC).isoformat(timespec="seconds") if files else "N/A"

TSV.parent.mkdir(parents=True, exist_ok=True)
header = "ts\tfiles_seen\tsec_per_song\teta_to_43_iso\tnewest_mtime_iso\tnote\n"
row = f"{now_iso}\t{n}\t{sec_per_song:.2f}\t{eta_iso}\t{newest_iso}\tc36-clone0-liveness\n"
if not TSV.exists():
    TSV.write_text(header + row)
else:
    with open(TSV, "a") as f:
        f.write(row)

print(f"n={n}/43 sec/song={sec_per_song:.2f} eta={eta_iso}")
