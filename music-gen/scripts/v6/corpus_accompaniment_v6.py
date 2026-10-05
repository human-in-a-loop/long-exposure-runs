#!/usr/bin/python3
"""v6 Phase 5 — the FAIR reference for an instrumental generator: the corpus ACCOMPANIMENT.

created: 2026-10-05
milestone: M-V6-ITER-04/fair-reference

Why: all 29 reference songs carry vocals; the generator makes instrumentals. A song-agnostic
scorecard that compares instrumentals against vocal mixes confounds "not real-sounding" with
"no singer". This script builds the vocal-free reference from the Demucs stems and derives its
own split-half noise floor so the gates are calibrated for the comparison actually made.

    corpus_accompaniment_v6.py build        # sum drums+bass+other per song -> data/v6/public/corpus_accomp/<sha16>.wav
    corpus_accompaniment_v6.py embed        # CLAP + MERT window embeddings (sha-cached, embed_audio.embed_files)
    corpus_accompaniment_v6.py baseline     # split-half noise floor (20 splits) -> baseline_corpus_accomp/summary.json
    corpus_accompaniment_v6.py gates        # store the thresholds in gates_v6.json under references.corpus_accomp
    corpus_accompaniment_v6.py all          # the four steps in order

Audio: stems are mono 22.05 kHz 16-bit (data/v6/stems/manifest.json). The sum is written as mono
22.05 kHz 16-bit PCM; when |sum| exceeds full scale the song is scaled to a 0.999 peak and the gain
recorded in the manifest (no clipping, no limiter, no PRNG). The output sha16 is the reference id
used by the embedding cache, so rebuilding bit-identical stems re-uses the cached embeddings.

Noise floor: baseline_real_vs_real.run_case / _agg (same metrics, bootstrap, k) on deterministic
split halves of the accompaniment set. Gates: scorecard.derive_gates() applied to the summary and
stored under gates_v6.json["references"]["corpus_accomp"] (the top-level "backbones" block stays the
full-mix corpus floor), so each --reference reads its own calibrated thresholds.

Discipline: /usr/bin/python3 guard; deterministic; writes only under data/v6; sorted-key atomic JSON.
"""
from __future__ import annotations

import argparse
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
from scripts.v6.v6_common import env_record, read_json, sha16_of, sha256_file, write_json_atomic  # noqa: E402

SCHEMA_VERSION = "v6.corpus_accomp.1"
BASELINE_SCHEMA_VERSION = "v6.baseline.1"  # same shape as baseline_real_vs_real so derive_gates() reads it
REFERENCE_NAME = "corpus_accomp"
ACCOMP_STEMS = ("drums", "bass", "other")
DEFAULT_STEMS_MANIFEST = _WS / "data" / "v6" / "stems" / "manifest.json"
DEFAULT_OUT_DIR = _WS / "data" / "v6" / "public" / REFERENCE_NAME
DEFAULT_BASELINE_DIR = _WS / "data" / "v6" / "scorecard" / f"baseline_{REFERENCE_NAME}"
DEFAULT_GATES = _WS / "data" / "v6" / "scorecard" / "gates_v6.json"
PEAK_CEILING = 0.999


# ----------------------------------------------------------------------------- build
def sum_stems(stems: dict[str, np.ndarray]) -> tuple[np.ndarray, float, float]:
    """Sum the accompaniment stems (float64), scale to PEAK_CEILING only when the sum clips.
    Returns (float32 mono, gain applied, raw peak before gain). Pure; testable."""
    n = min(len(v) for v in stems.values())
    acc = np.zeros(n, dtype=np.float64)
    for k in ACCOMP_STEMS:
        acc += stems[k][:n].astype(np.float64)
    peak = float(np.abs(acc).max()) if n else 0.0
    gain = PEAK_CEILING / peak if peak > PEAK_CEILING else 1.0
    return (acc * gain).astype(np.float32), gain, peak


def build(stems_manifest: Path, out_dir: Path, log) -> dict:
    import soundfile as sf
    man = read_json(stems_manifest)
    out_dir.mkdir(parents=True, exist_ok=True)
    stems_root = stems_manifest.parent
    songs = {}
    for src16 in sorted(man["songs"]):
        meta = man["songs"][src16]
        out_wav = out_dir / f"{src16}.wav"
        t0 = time.time()
        if not out_wav.exists():
            data, sr = {}, None
            for k in ACCOMP_STEMS:
                x, sr_k = sf.read(str(stems_root / src16 / f"{k}.wav"), dtype="float32", always_2d=True)
                if sr is not None and sr_k != sr:
                    raise ValueError(f"{src16}: stem {k} sr {sr_k} != {sr}")
                sr = sr_k
                data[k] = x.mean(axis=1)
            y, gain, peak = sum_stems(data)
            tmp = out_wav.with_name(out_wav.name + ".tmp.wav")
            sf.write(str(tmp), y, sr, subtype="PCM_16")
            os.replace(tmp, out_wav)
            built = {"gain": gain, "raw_peak": peak, "n_samples": int(len(y)), "sr": int(sr)}
        else:
            info = sf.info(str(out_wav))
            built = {"gain": None, "raw_peak": None, "n_samples": int(info.frames), "sr": int(info.samplerate),
                     "note": "existing file kept (delete to rebuild)"}
        sha = sha256_file(out_wav)
        songs[src16] = {"source_sha16": src16, "source_audio_path": meta["audio_path"], "band": meta.get("band"),
                        "title": meta.get("title"), "path": os.path.relpath(out_wav, _WS), "sha256": sha,
                        "sha16": sha16_of(sha), "stems": list(ACCOMP_STEMS), "wall_s": round(time.time() - t0, 2),
                        **built}
        log(f"[build] {src16} -> {songs[src16]['sha16']} gain={built['gain']} peak={built['raw_peak']} {meta.get('title')}")
    out = {"schema_version": SCHEMA_VERSION, "generator": "scripts/v6/corpus_accompaniment_v6.py",
           "reference": REFERENCE_NAME, "format": "mono 22050 Hz 16-bit PCM WAV = drums + bass + other (Demucs htdemucs)",
           "peak_ceiling": PEAK_CEILING, "stems_manifest": os.path.relpath(stems_manifest, _WS),
           "stems_manifest_sha16": sha16_of(sha256_file(stems_manifest)),
           "n_songs": len(songs), "songs": songs, "env": env_record()}
    write_json_atomic(out_dir / "manifest.json", out)
    log(f"[build] {len(songs)} songs -> {out_dir / 'manifest.json'}")
    return out


def reference_items(manifest_path: Path = DEFAULT_OUT_DIR / "manifest.json") -> list[dict]:
    """[{path, sha16, label, band, source_sha16}] for scorecard.resolve_reference('corpus_accomp')."""
    man = read_json(manifest_path)
    items = []
    for src16 in sorted(man["songs"]):
        s = man["songs"][src16]
        p = Path(s["path"])
        if not p.is_absolute():
            p = _WS / p
        items.append({"path": str(p), "sha16": s["sha16"], "label": s.get("title") or p.name,
                      "band": s.get("band"), "source_sha16": src16})
    if not items:
        raise ValueError(f"no songs in {manifest_path}")
    return items


# ----------------------------------------------------------------------------- embed / baseline
def embed(items: list[dict], backbones: list[str], emb_dir: Path, log) -> dict:
    out = {}
    for bb in backbones:
        t0 = time.time()
        recs = ea.embed_files([Path(it["path"]) for it in items], bb, emb_dir, log=log)
        out[bb] = {"n_files": len(recs), "cache_hits": int(sum(1 for r in recs if r.get("cache_hit"))),
                   "n_windows": int(sum(r["n_windows"] for r in recs)), "wall_s": round(time.time() - t0, 1)}
        log(f"[embed:{bb}] {out[bb]}")
    return out


def baseline(items: list[dict], backbones: list[str], emb_dir: Path, out: Path, args, log) -> dict:
    from scripts.v6.baseline_real_vs_real import METRICS, _agg, run_case
    summary = {"schema_version": BASELINE_SCHEMA_VERSION, "reference": REFERENCE_NAME, "params": vars(args),
               "n_songs": len(items),
               "bands": {str(b): sum(1 for it in items if it.get("band") == b) for b in sorted({it.get("band") for it in items})},
               "inputs": [{"sha16": it["sha16"], "source_sha16": it["source_sha16"], "band": it.get("band"),
                           "path": os.path.relpath(it["path"], _WS)} for it in items],
               "backbones": {}, "env": env_record()}
    t_all = time.time()
    for bb in backbones:
        songs = dm.load_songs([ea.embeddings_dir(emb_dir, bb) / f"{it['sha16']}.npz" for it in items])
        n = len(songs)
        rng = np.random.default_rng(args.seed)
        rows = []
        for i in range(args.splits):
            perm = rng.permutation(n)
            a, b = [songs[j] for j in perm[: n // 2]], [songs[j] for j in perm[n // 2:]]
            flat = run_case(a, b, bb, out / "split_half" / f"split_{i:02d}", args.seed + i, args)
            flat["split"] = i
            rows.append(flat)
            log(f"[{bb}] split {i:02d}: " + " ".join(f"{m}={flat.get(m, float('nan')):.4g}" for m in METRICS))
        agg = {m: _agg([r.get(m) for r in rows]) for m in METRICS + ["kid_song_ci95_lo", "kid_song_ci95_hi"]}
        agg["kid_song_ci_covers_zero_fraction"] = float(np.mean([r["kid_song_ci95_lo"] <= 0.0 <= r["kid_song_ci95_hi"] for r in rows]))
        summary["backbones"][bb] = {"n_songs": n, "n_windows": int(sum(len(s.emb) for s in songs)),
                                    "dim": int(songs[0].emb.shape[1]), "split_half": {"splits": rows, "aggregate": agg}}
        write_json_atomic(out / "summary.json", summary)
    summary["wall_total_s"] = round(time.time() - t_all, 1)
    write_json_atomic(out / "summary.json", summary)
    (out / "REPORT.md").write_text(baseline_report(summary), encoding="utf-8")
    log(f"[baseline] -> {out / 'summary.json'} ({summary['wall_total_s']} s)")
    return summary


def _fmt(x, nd=4):
    return "-" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{nd}g}"


def baseline_report(summary: dict) -> str:
    from scripts.v6.baseline_real_vs_real import METRICS
    L = [f"# v6 — split-half noise floor of the `{REFERENCE_NAME}` reference (drums+bass+other, no vocals)", "",
         f"{summary['n_songs']} songs, bands {summary['bands']}; splits={summary['params']['splits']}, seed={summary['params']['seed']}, "
         f"k={summary['params']['k']}, bootstrap={summary['params']['bootstrap']}.", ""]
    for bb, r in summary["backbones"].items():
        agg = r["split_half"]["aggregate"]
        L += [f"## {bb} (d={r['dim']}, {r['n_windows']} windows)", "",
              "| metric | split-half mean | sd | 95% range [p2.5, p97.5] |", "|---|---|---|---|"]
        for m in METRICS:
            a = agg[m]
            L.append(f"| {m} | {_fmt(a.get('mean'))} | {_fmt(a.get('sd'))} | [{_fmt(a.get('p2_5'))}, {_fmt(a.get('p97_5'))}] |")
        L += ["", f"Song-level KID bootstrap CI covered 0 in {agg['kid_song_ci_covers_zero_fraction']:.0%} of split-halves.", ""]
    return "\n".join(L) + "\n"


def store_gates(summary: dict, gates_path: Path, summary_path: Path, log) -> dict:
    from scripts.v6.scorecard import derive_gates
    gates = read_json(gates_path)
    derived = derive_gates(summary, os.path.relpath(summary_path, _WS))
    derived["reference"] = REFERENCE_NAME
    derived["note"] = ("thresholds for --reference corpus_accomp (vocal-free corpus accompaniment); the top-level "
                       "'backbones' block is the full-mix corpus floor and stays the default for other references")
    refs = gates.setdefault("references", {})
    refs[REFERENCE_NAME] = {k: v for k, v in derived.items() if k != "schema_version"}
    write_json_atomic(gates_path, gates)
    for bb, g in derived["backbones"].items():
        log(f"[gates:{REFERENCE_NAME}] {bb}: kid_song p97.5={_fmt(g['kid_song']['p97_5'])} c2st>{g['c2st_balanced_accuracy']['threshold']} "
            f"coverage<{_fmt(g['coverage']['threshold'])} novelty run>{_fmt(g['novelty_max_cos']['run_cos_threshold'])}")
    return gates


# ----------------------------------------------------------------------------- driver
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("step", choices=["build", "embed", "baseline", "gates", "all"])
    ap.add_argument("--stems-manifest", default=str(DEFAULT_STEMS_MANIFEST))
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--baseline-dir", default=str(DEFAULT_BASELINE_DIR))
    ap.add_argument("--gates", default=str(DEFAULT_GATES))
    ap.add_argument("--emb-dir", default=str(ea.DEFAULT_OUT_DIR))
    ap.add_argument("--backbones", default="clap,mert")
    ap.add_argument("--splits", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--subsets", type=int, default=50)
    ap.add_argument("--bootstrap", type=int, default=200)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--novelty-threshold", type=float, default=0.97)
    args = ap.parse_args(argv)

    def log(msg):
        print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)

    out_dir, bdir, emb_dir = Path(args.out_dir), Path(args.baseline_dir), Path(args.emb_dir)
    backbones = [b.strip() for b in args.backbones.split(",") if b.strip()]
    steps = ["build", "embed", "baseline", "gates"] if args.step == "all" else [args.step]
    if "build" in steps:
        build(Path(args.stems_manifest), out_dir, log)
    items = reference_items(out_dir / "manifest.json")
    if "embed" in steps:
        embed(items, backbones, emb_dir, log)
    if "baseline" in steps:
        bdir.mkdir(parents=True, exist_ok=True)
        baseline(items, backbones, emb_dir, bdir, args, log)
    if "gates" in steps:
        store_gates(read_json(bdir / "summary.json"), Path(args.gates), bdir / "summary.json", log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
