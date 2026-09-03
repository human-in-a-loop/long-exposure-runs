#!/usr/bin/env /usr/bin/python3
"""Transcription speed/quality bench (operator directive 2026-09-03).

Compares, on one real stem (default: Peach Dream drums, operator section):
  A. whole-clip transcription (baseline; current quality reference)
  B. chunked 30s/5s-overlap parallel transcription (_muscriptor_chunked)
  C. muscriptor --batch-size N (internal batching; conditioning may change)

Reports wall time and NOTE-LEVEL AGREEMENT vs baseline A: onset F1 at 50 ms
tolerance with pitch+instrument match, plus note-count ratio. A speed lever
is adoptable only if F1 >= 0.98 and count ratio in [0.98, 1.02] — i.e. the
output is functionally identical; otherwise it is rejected as quality
degradation, per the operator's no-degradation constraint.

Usage: /usr/bin/python3 scripts/v3_spine/transcription_speed_bench.py \
         [--wav PATH] [--instruments LIST] [--batch-sizes 2,4]
Run from the music-gen root.
"""
import argparse
import json
import subprocess
import sys
import tempfile
import time
from concurrent import futures
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import recreate_v3 as rv3  # noqa: E402


def notes(events):
    out = []
    for e in events:
        if e.get("type") in ("start", "note", None) and e.get("pitch") is not None:
            out.append((round(e.get("start_time", e.get("time", 0.0)), 6),
                        e.get("instrument"), e.get("pitch")))
    return sorted(out)


def f1_vs(a, b, tol=0.05):
    if not a and not b:
        return 1.0, 1.0
    used = set()
    tp = 0
    for t, ins, p in b:
        for j, (t2, ins2, p2) in enumerate(a):
            if j in used or ins2 != ins or p2 != p or abs(t2 - t) > tol:
                continue
            used.add(j)
            tp += 1
            break
    prec = tp / len(b) if b else 0.0
    rec = tp / len(a) if a else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return f1, (len(b) / len(a) if a else float("inf"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", default="data/v3_spine/88d247468cb6d49f/"
                    "operator_section_c27_checkpointed/rc9_6stem/drums.wav")
    ap.add_argument("--instruments", default="drums")
    ap.add_argument("--batch-sizes", default="2,4")
    args = ap.parse_args()
    wav = Path(args.wav)
    rows = []

    with tempfile.TemporaryDirectory(prefix="ts_bench_") as d:
        d = Path(d)
        # A. whole-clip baseline
        t0 = time.time()
        rv3._muscriptor_once(wav, d / "a.json", args.instruments, "json")
        ta = time.time() - t0
        base = notes(json.loads((d / "a.json").read_text()))
        rows.append(("whole_clip_baseline", ta, 1.0, 1.0, "REFERENCE"))

        # B. chunked parallel
        t0 = time.time()
        with futures.ThreadPoolExecutor(max_workers=4) as pool:
            rv3._muscriptor_chunked(wav, d / "b.json", args.instruments, pool)
        tb = time.time() - t0
        f1, ratio = f1_vs(base, notes(json.loads((d / "b.json").read_text())))
        rows.append(("chunked_30s_5s_parallel", tb, f1, ratio,
                     "ADOPTABLE" if f1 >= 0.98 and 0.98 <= ratio <= 1.02 else "REJECT"))

        # C. batch sizes
        for bs in [int(x) for x in args.batch_sizes.split(",") if x]:
            out = d / f"c{bs}.json"
            cmd = [rv3.MUSCRIPTOR_BIN, "transcribe", str(wav), "--format", "json",
                   "--output", str(out), "--model", rv3.MUSCRIPTOR_MODEL,
                   "--device", "cpu", "--detect-tempo", "best-effort",
                   "--instruments", args.instruments, "--batch-size", str(bs)]
            t0 = time.time()
            r = subprocess.run(cmd, env=rv3.sub_env(), capture_output=True)
            tc = time.time() - t0
            if r.returncode != 0:
                rows.append((f"batch_size_{bs}", tc, 0.0, 0.0,
                             f"ERROR rc={r.returncode}"))
                continue
            f1, ratio = f1_vs(base, notes(json.loads(out.read_text())))
            rows.append((f"batch_size_{bs}", tc, f1, ratio,
                         "ADOPTABLE" if f1 >= 0.98 and 0.98 <= ratio <= 1.02 else "REJECT"))

    print(f"{'variant':28s} {'wall_s':>8s} {'F1_vs_base':>10s} {'n_ratio':>8s}  verdict")
    for name, w, f1, ratio, v in rows:
        print(f"{name:28s} {w:8.1f} {f1:10.3f} {ratio:8.3f}  {v}")
    Path("data/v3_spine/transcription_speed_bench.json").write_text(
        json.dumps([{"variant": n, "wall_s": round(w, 2), "f1": round(f1, 4),
                     "note_ratio": round(r, 4), "verdict": v}
                    for n, w, f1, r, v in rows], indent=1))
    print("wrote data/v3_spine/transcription_speed_bench.json")


if __name__ == "__main__":
    main()
