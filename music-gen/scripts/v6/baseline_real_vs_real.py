#!/usr/bin/python3
"""v6 Phase 1A — "real vs real" noise floor for the distribution scorecard at our sample size.

created: 2026-10-04
milestone: M-V6-SCORECARD-1A

Why: a KID of 0.003 or a C2ST of 0.6 means nothing until we know what two disjoint halves of
REAL songs score against each other at n~29 songs / ~1500 windows. This script measures that.

Inputs: the rated corpus (corpus/ratings/{4,5,7}/*.mp3, receipts in ingest_receipts.jsonl give
band + sha256). Steps, per backbone (clap, mert):
  0. embed every song with embed_audio.embed_files (cached npz under data/v6/embeddings);
  a. split-half: --splits deterministic random halves of the songs, all metrics A=half1 vs
     B=half2; mean / sd / [p2.5, p97.5] per metric = the noise floor;
  b. band-vs-band: 4 vs 5, 4 vs 7, 5 vs 7 (are the user's rating bands separable at all?);
  c. leave-one-band-out: band b vs the rest (a stand-in for "a novel set of real songs");
  d. corpus vs MUSDB18 if --musdb-dir holds decodable audio (absence is recorded). Phase 1B: the
     default is the musdb_export.py output (data/v6/public/musdb18) and only the instrumental
     accompaniment.wav files are used (our generator makes instrumentals), all 150 songs.

Outputs (data/v6/scorecard/baseline_real_vs_real/):
  <config>/<case>/distribution_<backbone>.json   full scorecards (distribution_metrics schema)
  summary.json                                   aggregates + embed timing + env + input sha16s
  REPORT.md                                      table metric -> noise-floor range + usability notes

Determinism: splits come from numpy default_rng(--seed); metric seeds derive from it.
Discipline: /usr/bin/python3 guard; writes only under data/v6; never writes audio.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "4", "MKL_NUM_THREADS": "4", "OPENBLAS_NUM_THREADS": "4"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)
if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))

import numpy as np  # noqa: E402

from scripts.v6 import distribution_metrics as dm  # noqa: E402
from scripts.v6 import embed_audio as ea  # noqa: E402
from scripts.v6.v6_common import env_record, iter_audio_files, write_json_atomic  # noqa: E402

SCHEMA_VERSION = "v6.baseline.1"
DEFAULT_OUT = _WS / "data" / "v6" / "scorecard" / "baseline_real_vs_real"
METRICS = ["kid_song", "kid_mean", "fad", "c2st_balanced_accuracy", "knn_real_fraction",
           "density", "coverage", "novelty_max_cos"]


def read_receipts(path: Path, bands: set[int]) -> list[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if int(r["band"]) in bands:
                rows.append({"path": str(_WS / r["path"]), "band": int(r["band"]),
                             "sha256": r["sha256"], "sha16": r["sha16"], "title": r.get("title")})
    missing = [r["path"] for r in rows if not Path(r["path"]).is_file()]
    if missing:
        raise FileNotFoundError(f"{len(missing)} corpus files missing, e.g. {missing[0]}")
    return sorted(rows, key=lambda r: (r["band"], r["path"]))


def load_corpus_songs(rows: list[dict], backbone: str, emb_dir: Path) -> list[dm.Song]:
    songs = dm.load_songs([emb_dir / backbone / f"{r['sha16']}.npz" for r in rows])
    band = {r["sha16"]: r["band"] for r in rows}
    for s in songs:
        s.meta = dict(s.meta or {}, band=band.get(s.sha16))
    return songs


def _agg(values: list[float]) -> dict:
    v = np.asarray([x for x in values if x is not None and np.isfinite(x)], dtype=np.float64)
    if not len(v):
        return {"n": 0}
    return {"n": int(len(v)), "mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
            "min": float(v.min()), "max": float(v.max()),
            "p2_5": float(np.percentile(v, 2.5)), "p97_5": float(np.percentile(v, 97.5))}


def run_case(songs_a, songs_b, backbone, out_dir: Path, seed: int, args) -> dict:
    res = dm.compute_all(songs_a, songs_b, seed=seed, subsets=args.subsets, n_boot=args.bootstrap,
                         k=args.k, novelty_threshold=args.novelty_threshold, backbone=backbone)
    write_json_atomic(out_dir / f"distribution_{backbone}.json", res)
    flat = dm.flat_scalars(res)
    flat["n_songs_a"], flat["n_songs_b"] = res["n_songs_a"], res["n_songs_b"]
    flat["n_windows_a"], flat["n_windows_b"] = res["n_windows_a"], res["n_windows_b"]
    return flat


def embed_corpus(rows: list[dict], backbone: str, emb_dir: Path, log) -> dict:
    t0 = time.time()
    recs = ea.embed_files([Path(r["path"]) for r in rows], backbone, emb_dir, log=log)
    fresh = [r for r in recs if not r.get("cache_hit")]
    return {"n_files": len(recs), "cache_hits": len(recs) - len(fresh), "wall_total_s": round(time.time() - t0, 1),
            "wall_per_song_s": _agg([r["wall_s"] for r in fresh]) if fresh else {"n": 0, "note": "all cache hits"},
            "n_windows_total": int(sum(r["n_windows"] for r in recs)),
            "sec_audio_per_sec_wall": (round(sum(r["duration_s"] for r in fresh) / max(1e-9, sum(r["wall_s"] for r in fresh)), 2)
                                       if fresh else None)}


def baseline_backbone(rows, backbone, args, out: Path, log) -> dict:
    emb_dir = Path(args.emb_dir)
    result = {"embedding": embed_corpus(rows, backbone, emb_dir, log)}
    songs = load_corpus_songs(rows, backbone, emb_dir)
    n = len(songs)
    result["n_songs"], result["n_windows"], result["dim"] = n, int(sum(len(s.emb) for s in songs)), int(songs[0].emb.shape[1])
    rng = np.random.default_rng(args.seed)
    # (a) split-half
    rows_sh = []
    for i in range(args.splits):
        perm = rng.permutation(n)
        a, b = [songs[j] for j in perm[: n // 2]], [songs[j] for j in perm[n // 2:]]
        flat = run_case(a, b, backbone, out / "split_half" / f"split_{i:02d}", args.seed + i, args)
        flat["split"] = i
        rows_sh.append(flat)
        log(f"[{backbone}] split {i:02d}: " + " ".join(f"{m}={flat.get(m, float('nan')):.4g}" for m in METRICS))
    agg = {m: _agg([r.get(m) for r in rows_sh]) for m in METRICS + ["kid_song_ci95_lo", "kid_song_ci95_hi"]}
    agg["kid_song_ci_covers_zero_fraction"] = float(np.mean([r["kid_song_ci95_lo"] <= 0.0 <= r["kid_song_ci95_hi"]
                                                             for r in rows_sh]))
    result["split_half"] = {"splits": rows_sh, "aggregate": agg}
    # (b) band vs band, (c) leave-one-band-out
    by_band = {}
    for s in songs:
        by_band.setdefault(s.meta["band"], []).append(s)
    bands = sorted(by_band)
    result["bands"] = {str(b): len(v) for b, v in by_band.items()}
    result["band_vs_band"], result["leave_one_band_out"] = {}, {}
    for i, b1 in enumerate(bands):
        for b2 in bands[i + 1:]:
            key = f"band{b1}_vs_band{b2}"
            result["band_vs_band"][key] = run_case(by_band[b1], by_band[b2], backbone,
                                                   out / "band_vs_band" / key, args.seed, args)
            log(f"[{backbone}] {key}: kid_song={result['band_vs_band'][key]['kid_song']:.4g} "
                f"c2st={result['band_vs_band'][key]['c2st_balanced_accuracy']:.3f}")
    for b in bands:
        rest = [s for bb in bands if bb != b for s in by_band[bb]]
        key = f"band{b}_vs_rest"
        result["leave_one_band_out"][key] = run_case(by_band[b], rest, backbone,
                                                     out / "leave_one_band_out" / key, args.seed, args)
        log(f"[{backbone}] {key}: kid_song={result['leave_one_band_out'][key]['kid_song']:.4g} "
            f"c2st={result['leave_one_band_out'][key]['c2st_balanced_accuracy']:.3f}")
    # (d) corpus vs MUSDB18 (optional)
    musdb = Path(args.musdb_dir)
    musdb_files = iter_audio_files([musdb]) if musdb.is_dir() else []
    acc = [f for f in musdb_files if f.name == "accompaniment.wav"]
    musdb_files = acc or musdb_files  # Phase 1B export layout: compare against accompaniment (no vocals) only
    if musdb_files:
        if args.musdb_max_files:
            musdb_files = musdb_files[: args.musdb_max_files]
        ea.embed_files(musdb_files, backbone, emb_dir, log=log)
        from scripts.v6.v6_common import sha16_of, sha256_file
        msongs = dm.load_songs([emb_dir / backbone / f"{sha16_of(sha256_file(f))}.npz" for f in musdb_files])
        result["corpus_vs_musdb18"] = run_case(songs, msongs, backbone, out / "corpus_vs_musdb18", args.seed, args)
        result["corpus_vs_musdb18"]["musdb_n_files"] = len(msongs)
        result["corpus_vs_musdb18"]["musdb_file_kind"] = "accompaniment.wav" if acc else "any audio"
    else:
        result["corpus_vs_musdb18"] = {"status": "absent", "looked_in": str(musdb),
                                       "note": "no decodable audio files found (zip-only or missing); skipped"}
    return result


def _fmt(x, nd=4):
    return "-" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{nd}g}"


def write_report(summary: dict, path: Path) -> None:
    lines = ["# v6 Phase 1A — real-vs-real baseline (noise floor)", "",
             f"Corpus: {summary['n_songs']} songs, bands {summary['bands']}; splits={summary['params']['splits']}, "
             f"seed={summary['params']['seed']}, window/hop from embed sidecars; k={summary['params']['k']}.", ""]
    for bb, r in summary["backbones"].items():
        agg = r["split_half"]["aggregate"]
        bvb = r["band_vs_band"]
        lobo = r["leave_one_band_out"]
        lines += [f"## {bb} (d={r['dim']}, {r['n_windows']} windows)", "",
                  "| metric | split-half mean | sd | 95% range [p2.5, p97.5] | band-vs-band (min..max) | leave-one-band-out (min..max) |",
                  "|---|---|---|---|---|---|"]
        for m in METRICS:
            a = agg[m]
            bv = [v[m] for v in bvb.values() if m in v]
            lo = [v[m] for v in lobo.values() if m in v]
            lines.append(f"| {m} | {_fmt(a.get('mean'))} | {_fmt(a.get('sd'))} | [{_fmt(a.get('p2_5'))}, {_fmt(a.get('p97_5'))}] | "
                         f"{_fmt(min(bv)) if bv else '-'}..{_fmt(max(bv)) if bv else '-'} | "
                         f"{_fmt(min(lo)) if lo else '-'}..{_fmt(max(lo)) if lo else '-'} |")
        cov = agg["kid_song_ci_covers_zero_fraction"]
        fad_cv = agg["fad"]["sd"] / agg["fad"]["mean"] if agg["fad"].get("mean") else float("nan")
        c2 = agg["c2st_balanced_accuracy"]
        bvb_c2 = [v["c2st_balanced_accuracy"] for v in bvb.values()]
        sep = [k for k, v in bvb.items() if v["c2st_balanced_accuracy"] > c2["p97_5"]]
        kid_sep = [k for k, v in bvb.items() if v.get("kid_song_ci95_lo", -1) > 0]
        lines += ["", f"Song-level KID bootstrap CI covered 0 in {cov:.0%} of split-halves (target ~95%). "
                  f"Window-level KID has a positive floor of {_fmt(agg['kid_mean']['mean'])} (within-song clustering) and is "
                  f"reported for reference only. FAD across splits: mean {_fmt(agg['fad']['mean'])}, CV {fad_cv:.2f}; "
                  f"FAD is never near 0 at this n (covariance estimation in d={r['dim']} from ~{r['n_windows'] // 2} windows per half), "
                  f"so it can rank candidate sets but has no absolute meaning here. "
                  f"C2ST noise floor [{_fmt(c2['p2_5'], 3)}, {_fmt(c2['p97_5'], 3)}]; band-vs-band C2ST "
                  f"{_fmt(min(bvb_c2), 3)}..{_fmt(max(bvb_c2), 3)} — bands above the floor: {sep or 'none'}; "
                  f"bands with KID CI excluding 0: {kid_sep or 'none'}.",
                  "", f"MUSDB18: {r['corpus_vs_musdb18'].get('status', 'ran')} "
                  + ((lambda m: f"({m.get('musdb_n_files')} {m.get('musdb_file_kind', 'files')}): kid_song={_fmt(m.get('kid_song'))} "
                              f"CI95=[{_fmt(m.get('kid_song_ci95_lo'))}, {_fmt(m.get('kid_song_ci95_hi'))}] "
                              f"c2st={_fmt(m.get('c2st_balanced_accuracy'), 3)} coverage={_fmt(m.get('coverage'), 3)} "
                              f"density={_fmt(m.get('density'), 3)} fad={_fmt(m.get('fad'))} novelty_max_cos={_fmt(m.get('novelty_max_cos'))}"
                      )(r["corpus_vs_musdb18"]) if "kid_song" in r["corpus_vs_musdb18"] else ""), ""]
    lines += ["## Which metrics are usable at n=29", "",
              "- **Song-level KID with the two-level bootstrap** is the primary gate: its null expectation is 0 by "
              "construction, the CI coverage above says whether the bootstrap is calibrated, and a candidate set whose "
              "CI excludes 0 *and* whose point estimate exceeds the split-half p97.5 is distinguishable from real.",
              "- **C2ST-kNN (song-aware)** is the secondary gate: compare a candidate's value with the split-half 95% range; "
              "it is scale-free and the same across backbones, which makes it the easiest number to read.",
              "- **Coverage / density** are diagnostics (diversity vs realism); gate only on coverage falling below the "
              "split-half p2.5.",
              "- **FAD** is reported but not recommended as a gate at this sample size: the Ledoit-Wolf covariance is "
              "shrunk heavily (n << 10 d), the estimate is biased upward and its split-to-split spread is shown above.",
              "- **Window-level KID (subsets)** carries a within-song-clustering bias; prefer the song-level estimate.",
              "- **Novelty guard** (max cosine to any reference window) is a hard flag, not a distribution statistic; the "
              "split-half column shows the real-vs-real ceiling, so a threshold must sit clearly above it.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--receipts", default=str(_WS / "corpus" / "ratings" / "ingest_receipts.jsonl"))
    ap.add_argument("--bands", default="4,5,7")
    ap.add_argument("--backbones", default="clap,mert")
    ap.add_argument("--emb-dir", default=str(ea.DEFAULT_OUT_DIR))
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT))
    ap.add_argument("--musdb-dir", default=str(_WS / "data" / "v6" / "public" / "musdb18"),
                    help="musdb_export.py output; only accompaniment.wav files are used when present")
    ap.add_argument("--musdb-max-files", type=int, default=0)
    ap.add_argument("--splits", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--subsets", type=int, default=50)
    ap.add_argument("--bootstrap", type=int, default=200)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--novelty-threshold", type=float, default=0.97)
    args = ap.parse_args(argv)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    def log(msg):
        print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)

    rows = read_receipts(Path(args.receipts), {int(b) for b in args.bands.split(",")})
    log(f"corpus: {len(rows)} songs")
    summary = {"schema_version": SCHEMA_VERSION, "params": vars(args), "n_songs": len(rows),
               "bands": {str(b): sum(1 for r in rows if r["band"] == b) for b in sorted({r['band'] for r in rows})},
               "inputs": [{"sha16": r["sha16"], "band": r["band"], "path": os.path.relpath(r["path"], _WS)} for r in rows],
               "backbones": {}, "env": env_record()}
    t0 = time.time()
    for bb in [b.strip() for b in args.backbones.split(",") if b.strip()]:
        summary["backbones"][bb] = baseline_backbone(rows, bb, args, out, log)
        write_json_atomic(out / "summary.json", summary)  # checkpoint after each backbone
    summary["wall_total_s"] = round(time.time() - t0, 1)
    write_json_atomic(out / "summary.json", summary)
    write_report(summary, out / "REPORT.md")
    log(f"done in {summary['wall_total_s']} s -> {out / 'summary.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
