#!/usr/bin/python3
"""v6 Phase 1B — the scorecard entry point: embed candidates, score them against a reference set,
apply the Phase-1A gates, write scorecard.json + SCORECARD.md.

created: 2026-10-04
milestone: M-V6-SCORECARD-1B

    scorecard.py --candidates <dir|files...> --reference corpus|corpus_accomp|musdb|<dir> --name <run_name>
                 [--backbones clap,mert] [--stems] [--gates data/v6/scorecard/gates_v6.json]
    scorecard.py --derive-gates          # (re)write gates_v6.json from the real-vs-real baseline

Pipeline per run:
  1. discover candidate audio (dirs recurse). Files that look like per-instrument stems
     (drums|bass|other|vocals.wav, or *_drums.wav / *-drums.wav ...) are split off from the
     "mix" candidates; with --stems the drums/bass/other ones are scored against the MUSDB18 train
     stems with CLAP ("timbre by instrument"), otherwise they are listed as ignored.
  2. embed candidates (embed_audio.embed_files, sha-cached under data/v6/embeddings/).
  3. resolve the reference: `corpus` = the 29 rated songs (ingest receipts), `corpus_accomp` = their
     vocal-free accompaniment (drums+bass+other, corpus_accompaniment_v6.py; the FAIR reference for an
     instrumental generator, with its own gates under gates_v6.json["references"]["corpus_accomp"]), `musdb` = MUSDB18
     accompaniment wavs from data/v6/public/musdb18/manifest.json (--musdb-split all|train|test),
     or any directory/file list of audio. Reference songs whose sha16 is also a candidate are
     EXCLUDED (so a half-corpus can be scored against the other half) and the exclusion recorded.
  4. per backbone: distribution_metrics.compute_all(candidates, reference) -> distribution_<bb>.json,
     then the gates from gates_v6.json (derived from the split-half noise floor):
        kid_song  primary    FLAG if point > split-half p97.5 AND bootstrap CI95 excludes 0
        c2st      secondary  FLAG if balanced accuracy > threshold (ceil of split-half p97.5 to
                             2 dp -> 0.55 for MERT; CLAP's floor is wide, 0.67)
        coverage  diagnostic FLAG if < split-half p2.5
        density / fad / knn_real_fraction / kid_mean (window-level)   INFO, floor shown
        novelty   per candidate song: FLAG if max cosine to any reference window > threshold, or
                  >= run_length consecutive windows whose nearest reference window is in the same
                  reference song with cosine > the run threshold (split-half ceiling)
  5. audio descriptors per file (integrated LUFS, crest factor, spectral centroid, stereo width,
     peak/RMS), cached by sha16 under data/v6/descriptors/, summarised for candidates vs reference:
     mix-level mismatches (loudness, width) often explain embedding distance.
  6. data/v6/scorecard/runs/<name>/{scorecard.json, SCORECARD.md, distribution_<bb>.json,
     stems_<kind>_clap.json}.
  --match-reference-format (iteration 05, the FAIR mode): candidates are resampled / down-mixed to the reference's modal
     sample rate and channel count before embedding (scorecard_format.py; transformed copies cached by source sha16, the
     transformed file's own sha keys the embedding cache), the run name gets a `_fmt` suffix and scorecard.json carries
     `candidate_format`. Descriptors are then computed on the transformed candidates (width undefined for a mono target).

Determinism: metric seeds explicit (--seed), no PRNG elsewhere; sorted-key atomic JSON.
Discipline: /usr/bin/python3 guard; writes only under data/v6; never writes audio.
"""
from __future__ import annotations

import argparse
import math
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
from scripts.v6.v6_common import (  # noqa: E402
    env_record, iter_audio_files, read_json, sha16_of, sha256_file, write_json_atomic)

SCHEMA_VERSION = "v6.scorecard.1"
GATES_SCHEMA_VERSION = "v6.gates.1"
SCORECARD_DIR = _WS / "data" / "v6" / "scorecard"
DEFAULT_GATES = SCORECARD_DIR / "gates_v6.json"
DEFAULT_RUNS_DIR = SCORECARD_DIR / "runs"
DEFAULT_BASELINE_SUMMARY = SCORECARD_DIR / "baseline_real_vs_real" / "summary.json"
DEFAULT_DESCRIPTOR_CACHE = _WS / "data" / "v6" / "descriptors"
DEFAULT_RECEIPTS = _WS / "corpus" / "ratings" / "ingest_receipts.jsonl"
DEFAULT_MUSDB_MANIFEST = _WS / "data" / "v6" / "public" / "musdb18" / "manifest.json"
DEFAULT_ACCOMP_MANIFEST = _WS / "data" / "v6" / "public" / "corpus_accomp" / "manifest.json"
STEM_KINDS = ("drums", "bass", "other")
STEM_LIKE = STEM_KINDS + ("vocals",)
NOVELTY_MAX_COS = {"clap": 0.985, "mert": 0.995}  # operator-chosen, above the real-vs-real ceiling
NOVELTY_RUN_LENGTH = 3
# metric -> (rule, role); rule semantics in apply_gates()
GATE_RULES = {
    "kid_song": ("point_gt_p97_5_and_ci_excludes_zero", "primary"),
    "c2st_balanced_accuracy": ("gt_threshold", "secondary"),
    "coverage": ("lt_threshold", "diagnostic"),
    "density": ("info", "diagnostic"),
    "fad": ("info", "rank_only"),
    "knn_real_fraction": ("info", "diagnostic"),
    "kid_mean": ("info", "window_level_reference_only"),
    "novelty_max_cos": ("novelty", "hard_flag"),
}
METRIC_ORDER = ["kid_song", "c2st_balanced_accuracy", "coverage", "density", "fad",
                "knn_real_fraction", "kid_mean", "novelty_max_cos"]


# ============================================================================= gates
def derive_gates(summary: dict, source_path: str = "") -> dict:
    """Build gates_v6.json content from a baseline_real_vs_real summary (split-half aggregates)."""
    gates = {"schema_version": GATES_SCHEMA_VERSION,
             "derived_from": {"path": source_path, "schema_version": summary.get("schema_version"),
                              "n_songs": summary.get("n_songs"), "bands": summary.get("bands"),
                              "splits": summary.get("params", {}).get("splits"),
                              "seed": summary.get("params", {}).get("seed"), "k": summary.get("params", {}).get("k")},
             "derivation": [
                 "kid_song (PRIMARY): song-level unbiased MMD^2 with the two-level song bootstrap. FLAG when the "
                 "point estimate exceeds the split-half p97.5 AND the bootstrap CI95 excludes 0 (lo > 0). "
                 "Null expectation is 0 by construction; split-half CI coverage of 0 is recorded as calibration.",
                 "c2st_balanced_accuracy (SECONDARY): song-aware kNN two-sample balanced accuracy. FLAG when "
                 "value > threshold, threshold = ceil(split-half p97.5, 2 dp): MERT -> 0.55 (the recommended "
                 "secondary gate); CLAP's split-half floor is wide (p97.5 ~0.666 -> 0.67), so CLAP C2ST is weak.",
                 "coverage (DIAGNOSTIC): fraction of reference k-NN balls hit by a candidate window. FLAG when "
                 "value < split-half p2.5 (candidates collapsed onto part of the real manifold).",
                 "density, knn_real_fraction, kid_mean (window-level): INFO only, split-half range shown. "
                 "kid_mean carries a within-song-clustering bias; knn_real_fraction has a null expectation "
                 "that depends on set sizes and is written next to the value.",
                 "fad: INFO / rank-only. Ledoit-Wolf shrunk covariance at n << 10 d biases it upward; split-to-split "
                 "spread shown. Never gate on it at this sample size.",
                 f"novelty (HARD FLAG, per candidate song): max cosine of any candidate window to any reference "
                 f"window > max_cos_threshold ({NOVELTY_MAX_COS}), operator-chosen above the real-vs-real ceiling "
                 f"(split-half p97.5 of novelty_max_cos); OR >= {NOVELTY_RUN_LENGTH} consecutive candidate windows "
                 f"whose nearest reference window lies in the SAME reference song with cosine > run_cos_threshold "
                 f"(= the split-half ceiling). The run rule catches sustained copying that a single window misses.",
             ],
             "backbones": {}}
    for bb, r in summary["backbones"].items():
        agg = r["split_half"]["aggregate"]

        def floor(m):
            a = agg[m]
            return {k: a.get(k) for k in ("mean", "sd", "p2_5", "p97_5", "min", "max", "n")}

        g = {}
        g["kid_song"] = {"rule": GATE_RULES["kid_song"][0], "role": GATE_RULES["kid_song"][1],
                         "p97_5": agg["kid_song"]["p97_5"], "noise_floor": floor("kid_song"),
                         "ci_covers_zero_fraction_split_half": agg.get("kid_song_ci_covers_zero_fraction")}
        c2 = agg["c2st_balanced_accuracy"]
        g["c2st_balanced_accuracy"] = {"rule": GATE_RULES["c2st_balanced_accuracy"][0],
                                       "role": GATE_RULES["c2st_balanced_accuracy"][1],
                                       "threshold": math.ceil(c2["p97_5"] * 100.0 - 1e-9) / 100.0,
                                       "noise_floor": floor("c2st_balanced_accuracy")}
        g["coverage"] = {"rule": GATE_RULES["coverage"][0], "role": GATE_RULES["coverage"][1],
                         "threshold": agg["coverage"]["p2_5"], "noise_floor": floor("coverage")}
        for m in ("density", "fad", "knn_real_fraction", "kid_mean"):
            g[m] = {"rule": "info", "role": GATE_RULES[m][1], "noise_floor": floor(m)}
        ceiling = agg["novelty_max_cos"]["p97_5"]
        g["novelty_max_cos"] = {"rule": "novelty", "role": "hard_flag",
                                "max_cos_threshold": NOVELTY_MAX_COS.get(bb, min(0.999, round(ceiling + 0.015, 3))),
                                "run_cos_threshold": ceiling, "run_length": NOVELTY_RUN_LENGTH,
                                "split_half_ceiling": ceiling, "noise_floor": floor("novelty_max_cos")}
        gates["backbones"][bb] = g
    return gates


def load_gates(path: Path) -> dict:
    gates = read_json(path)
    if gates.get("schema_version") != GATES_SCHEMA_VERSION:
        raise ValueError(f"gates schema {gates.get('schema_version')!r} != {GATES_SCHEMA_VERSION}")
    return gates


def gates_for_reference(gates: dict, reference: str) -> tuple[dict, str]:
    """Per-backbone gate blocks for `reference`: gates["references"][<name>]["backbones"] when that
    reference has its own split-half floor (corpus_accomp), else the top-level full-mix corpus floor.
    Returns (backbones_dict, key_used)."""
    ref = (gates.get("references") or {}).get(reference)
    if ref and ref.get("backbones"):
        return ref["backbones"], f"references.{reference}"
    return gates["backbones"], "backbones"


def apply_gates(flat: dict, gates_bb: dict, novelty_flagged: int = 0) -> dict:
    """Metric -> {value, ci95, rule, threshold, noise_floor, verdict}. Pure; testable.
    `flat` is distribution_metrics.flat_scalars(); verdicts: PASS / FLAG / INFO / N/A."""
    out = {}
    for m in METRIC_ORDER:
        g = gates_bb.get(m)
        if g is None:
            continue
        val = flat.get(m)
        rec = {"value": val, "rule": g["rule"], "role": g.get("role"),
               "noise_floor": g.get("noise_floor"), "threshold": None, "ci95": None}
        finite = val is not None and isinstance(val, (int, float)) and math.isfinite(val)
        if g["rule"] == "point_gt_p97_5_and_ci_excludes_zero":
            lo, hi = flat.get("kid_song_ci95_lo"), flat.get("kid_song_ci95_hi")
            rec["threshold"] = g["p97_5"]
            if lo is not None and hi is not None and math.isfinite(lo) and math.isfinite(hi):
                rec["ci95"] = [lo, hi]
            if not finite or rec["ci95"] is None:
                rec["verdict"] = "N/A"
            else:
                rec["verdict"] = "FLAG" if (val > g["p97_5"] and lo > 0.0) else "PASS"
        elif g["rule"] == "gt_threshold":
            rec["threshold"] = g["threshold"]
            rec["verdict"] = "N/A" if not finite else ("FLAG" if val > g["threshold"] else "PASS")
        elif g["rule"] == "lt_threshold":
            rec["threshold"] = g["threshold"]
            rec["verdict"] = "N/A" if not finite else ("FLAG" if val < g["threshold"] else "PASS")
        elif g["rule"] == "novelty":
            rec["threshold"] = g["max_cos_threshold"]
            rec["run_cos_threshold"], rec["run_length"] = g["run_cos_threshold"], g["run_length"]
            rec["verdict"] = "FLAG" if novelty_flagged > 0 else ("N/A" if not finite else "PASS")
            rec["n_flagged_songs"] = int(novelty_flagged)
        else:
            rec["verdict"] = "INFO"
            if m == "knn_real_fraction":
                rec["null_expectation"] = flat.get("knn_real_fraction_null")
        out[m] = rec
    return out


# ============================================================================= novelty runs
def novelty_runs(songs_a: list[dm.Song], songs_b: list[dm.Song], run_cos_threshold: float,
                 run_length: int = NOVELTY_RUN_LENGTH) -> list[dict]:
    """Per candidate song: longest run of consecutive windows whose nearest reference window belongs
    to the same reference song with cosine > run_cos_threshold. Window order = npz order (time)."""
    Y, idx_b = dm.stack(songs_b)
    Yn = Y / np.maximum(np.linalg.norm(Y, axis=1, keepdims=True), 1e-12)
    out = []
    for s in songs_a:
        Xn = s.emb / np.maximum(np.linalg.norm(s.emb, axis=1, keepdims=True), 1e-12)
        S = Xn @ Yn.T
        j = np.argmax(S, axis=1)
        cos = S[np.arange(len(j)), j]
        ref_song = idx_b[j]
        best_len, best_ref, best_start, cur_len = 0, None, None, 0
        for i in range(len(j)):
            if cos[i] > run_cos_threshold and i > 0 and cos[i - 1] > run_cos_threshold and ref_song[i] == ref_song[i - 1]:
                cur_len += 1
            else:
                cur_len = 1 if cos[i] > run_cos_threshold else 0
            if cur_len > best_len:
                best_len, best_ref, best_start = cur_len, int(ref_song[i]), i - cur_len + 1
        out.append({"song_id": s.song_id, "sha16": s.sha16, "longest_run": int(best_len),
                    "run_ref_song": songs_b[best_ref].song_id if best_ref is not None else None,
                    "run_ref_sha16": songs_b[best_ref].sha16 if best_ref is not None else None,
                    "run_start_window": best_start, "run_flagged": bool(best_len >= run_length)})
    return out


# ============================================================================= candidates / reference
def classify_stem(path: Path) -> str | None:
    """'drums'|'bass'|'other'|'vocals' when the file name says so, else None."""
    stem = path.stem.lower()
    for kind in STEM_LIKE:
        if stem == kind or stem.endswith("_" + kind) or stem.endswith("-" + kind) or stem.endswith("." + kind):
            return kind
    return None


def discover_candidates(inputs) -> dict:
    files = iter_audio_files(inputs)
    out = {"mix": [], "stems": {k: [] for k in STEM_KINDS}, "ignored": []}
    for f in files:
        kind = classify_stem(f)
        if kind is None:
            out["mix"].append(f)
        elif kind in STEM_KINDS:
            out["stems"][kind].append(f)
        else:
            out["ignored"].append({"path": str(f), "reason": f"{kind} stem has no reference set"})
    return out


class RefItem(dict):
    """{"path", "sha16", "label"} for one reference audio file."""


def _items(paths, labels=None, shas=None) -> list[RefItem]:
    paths = [Path(p) for p in paths]
    shas = shas or [sha16_of(sha256_file(p)) for p in paths]
    labels = labels or [p.name for p in paths]
    return [RefItem(path=str(p), sha16=s, label=l) for p, s, l in zip(paths, shas, labels)]


def resolve_corpus(receipts: Path, bands=(4, 5, 7)) -> list[RefItem]:
    from scripts.v6.baseline_real_vs_real import read_receipts
    rows = read_receipts(receipts, set(bands))
    return _items([r["path"] for r in rows], [r.get("title") or Path(r["path"]).name for r in rows],
                  [r["sha16"] for r in rows])


def resolve_musdb(manifest_path: Path, split: str = "all", stem: str = "accompaniment") -> list[RefItem]:
    man = read_json(manifest_path)
    items = []
    for s in man["songs"]:
        if split != "all" and s["split"] != split:
            continue
        f = s["files"].get(stem)
        if not f:
            continue
        p = Path(f["path"])
        if not p.is_absolute():
            p = _WS / p
        items.append(RefItem(path=str(p), sha16=f["sha16"], label=f"{s['split']}/{s['slug']}"))
    if not items:
        raise ValueError(f"no {stem!r} files for split {split!r} in {manifest_path}")
    return items


def resolve_corpus_accomp(manifest_path: Path) -> list[RefItem]:
    from scripts.v6.corpus_accompaniment_v6 import reference_items
    return [RefItem(path=it["path"], sha16=it["sha16"], label=it["label"]) for it in reference_items(manifest_path)]


def resolve_reference(spec: str, args) -> tuple[list[RefItem], dict]:
    if spec == "corpus":
        items = resolve_corpus(Path(args.receipts), tuple(int(b) for b in args.bands.split(",")))
        info = {"spec": spec, "receipts": str(args.receipts), "bands": args.bands}
    elif spec == "corpus_accomp":
        items = resolve_corpus_accomp(Path(args.accomp_manifest))
        info = {"spec": spec, "manifest": str(args.accomp_manifest), "stems": "drums+bass+other (no vocals)"}
    elif spec == "musdb":
        items = resolve_musdb(Path(args.musdb_manifest), args.musdb_split)
        info = {"spec": spec, "manifest": str(args.musdb_manifest), "split": args.musdb_split, "stem": "accompaniment"}
    else:
        paths = iter_audio_files([p for p in spec.split(",")])
        items = _items(paths)
        info = {"spec": spec}
    return items, info


def exclude_overlap(ref: list[RefItem], cand_sha16s: set[str]) -> tuple[list[RefItem], list[dict]]:
    kept, dropped = [], []
    for r in ref:
        (dropped if r["sha16"] in cand_sha16s else kept).append(r)
    return kept, [{"sha16": r["sha16"], "label": r["label"]} for r in dropped]


def embed_and_load(paths: list[Path], backbone: str, emb_dir: Path, log, tag: str | None = None,
                   labels: dict[str, str] | None = None) -> tuple[list[dm.Song], list[dict]]:
    """Embed (cache-aware) and load Songs in `paths` order; returns (songs, dropped_no_windows)."""
    recs = ea.embed_files(paths, backbone, emb_dir, log=log, tag=tag)
    bdir = ea.embeddings_dir(emb_dir, backbone, tag)
    songs = dm.load_songs([bdir / f"{r['sha16']}.npz" for r in recs])
    have = {s.sha16 for s in songs}
    dropped = [{"sha16": r["sha16"], "name": r["name"], "reason": "no usable windows"} for r in recs if r["sha16"] not in have]
    if labels:
        for s in songs:
            s.song_id = labels.get(s.sha16, s.song_id)
    return songs, dropped


# ============================================================================= descriptors
# (moved to scorecard_descriptors.py in iteration 05; re-exported so callers and tests keep `scorecard.audio_descriptors` etc.)
from scripts.v6.scorecard_descriptors import (  # noqa: E402,F401
    DESCRIPTOR_KEYS, DESCRIPTORS_SCHEMA_VERSION, audio_descriptors, descriptors_for, summarise_descriptors)
from scripts.v6 import scorecard_format as scf  # noqa: E402


# ============================================================================= scoring
def score_backbone(cands: list[dm.Song], ref: list[dm.Song], backbone: str, gates_bb: dict, out_dir: Path,
                   args, tag: str = "") -> tuple[dict, dict]:
    """compute_all + gates for one backbone; writes distribution_<bb>[_<tag>].json. Returns (block, res)."""
    n_boot = args.bootstrap if min(len(cands), len(ref)) >= 2 else 0
    res = dm.compute_all(cands, ref, seed=args.seed, subsets=args.subsets, n_boot=n_boot, k=args.k,
                         novelty_threshold=gates_bb["novelty_max_cos"]["max_cos_threshold"], backbone=backbone)
    runs = novelty_runs(cands, ref, gates_bb["novelty_max_cos"]["run_cos_threshold"],
                        gates_bb["novelty_max_cos"]["run_length"])
    run_by_sha = {r["sha16"]: r for r in runs}
    per_song = []
    for p in res["per_song_candidate"]:
        r = dict(p)
        r.update({k: v for k, v in run_by_sha[p["sha16"]].items() if k not in ("song_id", "sha16")})
        r["flagged_max_cos"] = bool(p["flagged"])
        r["flagged"] = bool(p["flagged"] or r["run_flagged"])
        per_song.append(r)
    res["novelty"]["runs"] = runs
    res["per_song_candidate"] = per_song
    fname = f"distribution_{backbone}{('_' + tag) if tag else ''}.json"
    write_json_atomic(out_dir / fname, res)
    flat = dm.flat_scalars(res)
    n_nov = sum(1 for r in per_song if r["flagged"])
    metrics = apply_gates(flat, gates_bb, n_nov)
    flags = [m for m, r in metrics.items() if r["verdict"] == "FLAG"]
    block = {"backbone": backbone, "tag": tag or None, "dim": res["dim"],
             "n_songs_a": res["n_songs_a"], "n_windows_a": res["n_windows_a"],
             "n_songs_b": res["n_songs_b"], "n_windows_b": res["n_windows_b"],
             "metrics": metrics, "flags": flags, "verdict": "FLAG" if flags else "PASS",
             "novelty_flagged_songs": [r for r in per_song if r["flagged"]],
             "least_real_like": per_song[: min(3, len(per_song))],
             "distribution_json": str(out_dir / fname)}
    return block, res


# ============================================================================= rendering
def scf_cache_default() -> Path:
    return SCORECARD_DIR / "format_cache"


def _f(x, nd=4):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "-"
    return f"{x:.{nd}g}" if isinstance(x, (int, float)) else str(x)


def _floor(nf):
    return f"[{_f(nf.get('p2_5'))}, {_f(nf.get('p97_5'))}]" if nf else "-"


def _rule_text(m, r):
    if r["rule"] == "point_gt_p97_5_and_ci_excludes_zero":
        return f"FLAG if > {_f(r['threshold'])} and CI95 excludes 0"
    if r["rule"] == "gt_threshold":
        return f"FLAG if > {_f(r['threshold'])}"
    if r["rule"] == "lt_threshold":
        return f"FLAG if < {_f(r['threshold'])}"
    if r["rule"] == "novelty":
        return f"FLAG song if max cos > {_f(r['threshold'])} or >= {r['run_length']} consecutive windows > {_f(r['run_cos_threshold'])} on one ref song"
    if m == "knn_real_fraction":
        return f"info (null expectation {_f(r.get('null_expectation'))})"
    return "info" if r["role"] != "rank_only" else "info (rank only)"


def render_backbone_table(block: dict) -> list[str]:
    lines = ["| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |", "|---|---|---|---|---|---|"]
    for m in METRIC_ORDER:
        r = block["metrics"].get(m)
        if r is None:
            continue
        ci = f"[{_f(r['ci95'][0])}, {_f(r['ci95'][1])}]" if r.get("ci95") else "-"
        lines.append(f"| {m} | {_f(r['value'])} | {ci} | {_floor(r.get('noise_floor'))} | {_rule_text(m, r)} | {r['verdict']} |")
    return lines


def render_markdown(sc: dict) -> str:
    L = [f"# v6 scorecard — {sc['name']}", "",
         f"Overall verdict: **{sc['verdict']['overall']}**" + (f" — {'; '.join(sc['verdict']['reasons'])}" if sc["verdict"]["reasons"] else ""), "",
         f"Candidates: {sc['candidates']['n_files']} mix files ({sc['candidates']['n_songs_scored']} with windows); "
         f"reference `{sc['reference']['info']['spec']}`: {sc['reference']['n_files']} files"
         + (f", {len(sc['reference']['excluded_overlap'])} excluded as candidate overlap" if sc["reference"]["excluded_overlap"] else "")
         + f". Gates: `{sc['gates']['path']}` (sha16 {sc['gates']['sha16']}, key `{sc['gates'].get('key', 'backbones')}`). Seed {sc['params']['seed']}, k={sc['params']['k']}, bootstrap {sc['params']['bootstrap']}."
         + (f" Candidates FORMAT-MATCHED to the reference: {sc['candidate_format']['reference_format']['sample_rate']} Hz / {sc['candidate_format']['reference_format']['channels']} ch "
            f"({sc['candidate_format']['n_transformed']} transformed, {sc['candidate_format']['n_passthrough']} already matched)." if (sc.get("candidate_format") or {}).get("matched") else ""), ""]
    for bb, block in sc["backbones"].items():
        L += [f"## {bb} (d={block['dim']}; candidates {block['n_songs_a']} songs / {block['n_windows_a']} windows; "
              f"reference {block['n_songs_b']} songs / {block['n_windows_b']} windows) — **{block['verdict']}**", ""]
        L += render_backbone_table(block)
        L.append("")
        if block["novelty_flagged_songs"]:
            L.append("Novelty-flagged candidate songs:")
            for r in block["novelty_flagged_songs"]:
                L.append(f"- `{r['song_id']}` ({r['sha16']}): max cos {_f(r['nearest_ref_cos'])} to `{r['nearest_ref_song']}` "
                         f"(window {r['candidate_window']}); longest same-song run {r['longest_run']} windows"
                         + (f" on `{r['run_ref_song']}`" if r.get("run_ref_song") else "") + f"; kNN-real fraction {_f(r['knn_real_fraction_mean'], 3)}")
        else:
            L.append("Novelty: no candidate song flagged.")
        L.append("")
        if block["least_real_like"]:
            L.append("Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):")
            for r in block["least_real_like"]:
                L.append(f"- `{r['song_id']}`: kNN-real {_f(r['knn_real_fraction_mean'], 3)}, max cos {_f(r['nearest_ref_cos'])} to `{r['nearest_ref_song']}`")
            L.append("")
    if sc.get("stems"):
        L += ["## Timbre by instrument (CLAP vs MUSDB18 train stems)", "",
              "Gates reuse the full-mix CLAP noise floor (no stem-level baseline yet), so verdicts here are indicative.", "",
              "| stem | n cand songs / windows | n ref songs / windows | kid_song | CI95 | c2st | coverage | density | fad | novelty flags | verdict |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for kind, b in sc["stems"].items():
            if "error" in b:
                L.append(f"| {kind} | - | - | - | - | - | - | - | - | - | {b['error']} |")
                continue
            m = b["metrics"]
            ci = f"[{_f(m['kid_song']['ci95'][0])}, {_f(m['kid_song']['ci95'][1])}]" if m["kid_song"].get("ci95") else "-"
            L.append(f"| {kind} | {b['n_songs_a']} / {b['n_windows_a']} | {b['n_songs_b']} / {b['n_windows_b']} | "
                     f"{_f(m['kid_song']['value'])} ({m['kid_song']['verdict']}) | {ci} | {_f(m['c2st_balanced_accuracy']['value'], 3)} ({m['c2st_balanced_accuracy']['verdict']}) | "
                     f"{_f(m['coverage']['value'], 3)} ({m['coverage']['verdict']}) | {_f(m['density']['value'], 3)} | {_f(m['fad']['value'])} | "
                     f"{m['novelty_max_cos'].get('n_flagged_songs', 0)} | {b['verdict']} |")
        L.append("")
    if sc.get("descriptors"):
        d = sc["descriptors"]
        L += ["## Audio descriptors (mix level)", "",
              f"Candidates n={d['candidates']['summary']['n']}, reference n={d['reference']['summary']['n']}. "
              "Loudness/width/crest mismatches often explain embedding distance before timbre does.", "",
              "| descriptor | candidates mean ± sd | reference mean ± sd | Δ (cand − ref) |", "|---|---|---|---|"]
        for k in DESCRIPTOR_KEYS:
            a, b = d["candidates"]["summary"].get(k, {}), d["reference"]["summary"].get(k, {})
            if a.get("n") and b.get("n"):
                L.append(f"| {k} | {_f(a['mean'])} ± {_f(a['sd'], 3)} | {_f(b['mean'])} ± {_f(b['sd'], 3)} | {_f(a['mean'] - b['mean'], 3)} |")
            else:
                L.append(f"| {k} | {_f(a.get('mean'))} | {_f(b.get('mean'))} | - |")
        L.append("")
    if sc["candidates"].get("ignored") or any(sc["candidates"].get("dropped", {}).values()):
        L.append("Notes:")
        for ig in sc["candidates"].get("ignored", []):
            L.append(f"- ignored `{ig['path']}`: {ig['reason']}")
        for bb, lst in sc["candidates"].get("dropped", {}).items():
            for dr in lst:
                L.append(f"- [{bb}] dropped `{dr['name']}`: {dr['reason']}")
        L.append("")
    L.append(f"Wall {sc['wall_s']} s. Full numbers: `scorecard.json`, per-backbone `distribution_<backbone>.json`.")
    return "\n".join(L) + "\n"


# ============================================================================= driver
def overall_verdict(backbones: dict, stems: dict | None) -> dict:
    reasons = []
    for bb, b in backbones.items():
        for m in b["flags"]:
            role = b["metrics"][m]["role"]
            reasons.append(f"{bb}:{m} ({role})")
    for kind, b in (stems or {}).items():
        for m in b.get("flags", []):
            reasons.append(f"stem={kind}:{m} (indicative)")
    return {"overall": "FLAG" if reasons else "PASS", "reasons": reasons}


def run(args, log=print) -> dict:
    t0 = time.time()
    emb_dir = Path(args.emb_dir)
    args.name = scf.run_name(args.name, bool(getattr(args, "match_reference_format", False)))
    out_dir = Path(args.runs_dir) / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    gates_path = Path(args.gates)
    gates = load_gates(gates_path)
    gates_bbs, gates_key = gates_for_reference(gates, args.reference)
    backbones = [b.strip() for b in args.backbones.split(",") if b.strip()]
    for bb in backbones:
        if bb not in gates_bbs:
            raise KeyError(f"gates file has no backbone {bb!r} under {gates_key}")

    disc = discover_candidates(args.candidates)
    cand_paths = disc["mix"]
    if not cand_paths:
        raise ValueError("no candidate mix files found")
    cand_items = _items(cand_paths)
    cand_shas = {c["sha16"] for c in cand_items}
    log(f"candidates: {len(cand_paths)} mix files" + (f", stems {{{', '.join(f'{k}:{len(v)}' for k, v in disc['stems'].items())}}}" if args.stems else ""))

    ref_items_all, ref_info = resolve_reference(args.reference, args)
    match_fmt = bool(getattr(args, "match_reference_format", False))
    fmt_block = {"matched": False}
    if match_fmt:  # fair mode: candidates take the reference's format before embedding (scorecard_format.py)
        fmt = scf.reference_format(ref_items_all)
        cand_items, fmt_block = scf.match_items(cand_items, fmt, Path(getattr(args, "format_cache", scf_cache_default())), log)
        cand_paths = [Path(c["path"]) for c in cand_items]
        cand_shas |= {c["sha16"] for c in cand_items}
        log(f"format-matched {fmt_block['n_transformed']} candidates to {fmt['sample_rate']} Hz / {fmt['channels']} ch ({fmt_block['n_passthrough']} already matched)")
    ref_items, excluded = exclude_overlap(ref_items_all, cand_shas)
    if not ref_items:
        raise ValueError("reference set is empty after excluding candidate overlap")
    log(f"reference {args.reference}: {len(ref_items_all)} files, {len(excluded)} excluded as overlap -> {len(ref_items)}")

    sc = {"schema_version": SCHEMA_VERSION, "name": args.name, "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
          "params": {"seed": args.seed, "k": args.k, "bootstrap": args.bootstrap, "subsets": args.subsets,
                     "backbones": backbones, "stems": bool(args.stems)},
          "gates": {"path": str(gates_path), "sha16": sha16_of(sha256_file(gates_path)), "schema_version": gates["schema_version"],
                    "key": gates_key},
          "candidates": {"inputs": [str(p) for p in args.candidates], "n_files": len(cand_paths),
                         "files": [dict(c) for c in cand_items], "ignored": disc["ignored"], "dropped": {}},
          "candidate_format": fmt_block,
          "reference": {"info": ref_info, "n_files_total": len(ref_items_all), "n_files": len(ref_items),
                        "excluded_overlap": excluded, "files": [dict(r) for r in ref_items]},
          "backbones": {}, "stems": None, "descriptors": None}
    ref_labels = {r["sha16"]: r["label"] for r in ref_items}
    n_scored = None
    for bb in backbones:
        cands, dropped_c = embed_and_load(cand_paths, bb, emb_dir, log)
        refs, dropped_r = embed_and_load([Path(r["path"]) for r in ref_items], bb, emb_dir, log, labels=ref_labels)
        sc["candidates"]["dropped"][bb] = dropped_c
        if not cands or not refs:
            raise ValueError(f"[{bb}] empty candidate ({len(cands)}) or reference ({len(refs)}) set after embedding")
        n_scored = len(cands)
        block, _ = score_backbone(cands, refs, bb, gates_bbs[bb], out_dir, args)
        block["dropped_reference"] = dropped_r
        sc["backbones"][bb] = block
        log(f"[{bb}] {block['verdict']} " + " ".join(f"{m}={_f(r['value'])}:{r['verdict']}" for m, r in block["metrics"].items()))
    sc["candidates"]["n_songs_scored"] = n_scored

    if args.stems:
        sc["stems"] = {}
        for kind in STEM_KINDS:
            files = disc["stems"][kind]
            if not files:
                continue
            tag = f"stem={kind}"
            try:
                cand_stem_items = _items(files)
                ref_stem_items, excluded_stem = exclude_overlap(resolve_musdb(Path(args.musdb_manifest), "train", kind),
                                                                {c["sha16"] for c in cand_stem_items})
                cands, dropped_c = embed_and_load(files, "clap", emb_dir, log, tag=tag)
                refs, _ = embed_and_load([Path(r["path"]) for r in ref_stem_items], "clap", emb_dir, log, tag=tag,
                                         labels={r["sha16"]: r["label"] for r in ref_stem_items})
                if not cands or not refs:
                    raise ValueError(f"empty set (cands {len(cands)}, refs {len(refs)})")
                block, _ = score_backbone(cands, refs, "clap", gates["backbones"]["clap"], out_dir, args, tag=tag)
                block["files"] = [str(f) for f in files]
                block["dropped"] = dropped_c
                block["excluded_overlap"] = excluded_stem
                sc["stems"][kind] = block
                log(f"[stem={kind}] {block['verdict']} kid_song={_f(block['metrics']['kid_song']['value'])} c2st={_f(block['metrics']['c2st_balanced_accuracy']['value'], 3)}")
            except Exception as exc:
                sc["stems"][kind] = {"error": f"{type(exc).__name__}: {exc}", "files": [str(f) for f in files]}
                log(f"[stem={kind}] error: {exc}")

    if not args.no_descriptors:
        cache = Path(args.descriptor_cache)
        cache.mkdir(parents=True, exist_ok=True)
        dc = descriptors_for(cand_items, cache, log)
        dr = descriptors_for(ref_items, cache, log)
        sc["descriptors"] = {"candidates": {"per_file": dc, "summary": summarise_descriptors(dc)},
                             "reference": {"per_file": dr, "summary": summarise_descriptors(dr)}}

    sc["verdict"] = overall_verdict(sc["backbones"], sc["stems"])
    sc["env"] = env_record()
    sc["wall_s"] = round(time.time() - t0, 1)
    write_json_atomic(out_dir / "scorecard.json", sc)
    (out_dir / "SCORECARD.md").write_text(render_markdown(sc), encoding="utf-8")
    log(f"{sc['verdict']['overall']} -> {out_dir / 'SCORECARD.md'} ({sc['wall_s']} s)")
    return sc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--candidates", nargs="+", help="audio files and/or directories (dirs recurse)")
    ap.add_argument("--reference", help="corpus | corpus_accomp | musdb | <dir or comma-separated files>")
    ap.add_argument("--name", help="run name -> data/v6/scorecard/runs/<name>/")
    ap.add_argument("--backbones", default="clap,mert")
    ap.add_argument("--stems", action="store_true", help="score drums/bass/other stems vs MUSDB18 train stems (CLAP)")
    ap.add_argument("--gates", default=str(DEFAULT_GATES))
    ap.add_argument("--derive-gates", action="store_true", help="write --gates from --baseline-summary and exit")
    ap.add_argument("--baseline-summary", default=str(DEFAULT_BASELINE_SUMMARY))
    ap.add_argument("--emb-dir", default=str(ea.DEFAULT_OUT_DIR))
    ap.add_argument("--runs-dir", default=str(DEFAULT_RUNS_DIR))
    ap.add_argument("--descriptor-cache", default=str(DEFAULT_DESCRIPTOR_CACHE))
    ap.add_argument("--no-descriptors", action="store_true")
    ap.add_argument("--match-reference-format", action="store_true", help="fair mode: resample/down-mix candidates to the reference's format before embedding (run name + '_fmt')")
    ap.add_argument("--format-cache", default=str(SCORECARD_DIR / "format_cache"), help="where the transformed candidate copies live (keyed by source sha16)")
    ap.add_argument("--receipts", default=str(DEFAULT_RECEIPTS))
    ap.add_argument("--bands", default="4,5,7")
    ap.add_argument("--musdb-manifest", default=str(DEFAULT_MUSDB_MANIFEST))
    ap.add_argument("--accomp-manifest", default=str(DEFAULT_ACCOMP_MANIFEST))
    ap.add_argument("--musdb-split", default="all", choices=["all", "train", "test"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--subsets", type=int, default=50)
    ap.add_argument("--bootstrap", type=int, default=200)
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args(argv)

    def log(msg):
        print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)

    if args.derive_gates:
        summary = read_json(args.baseline_summary)
        gates = derive_gates(summary, os.path.relpath(args.baseline_summary, _WS))
        write_json_atomic(args.gates, gates)
        log(f"wrote {args.gates} from {args.baseline_summary}")
        for bb, g in gates["backbones"].items():
            log(f"  {bb}: kid_song p97.5={_f(g['kid_song']['p97_5'])} c2st>{g['c2st_balanced_accuracy']['threshold']} "
                f"coverage<{_f(g['coverage']['threshold'])} novelty>{g['novelty_max_cos']['max_cos_threshold']} "
                f"(run>{_f(g['novelty_max_cos']['run_cos_threshold'])} x{g['novelty_max_cos']['run_length']})")
        return 0
    if not (args.candidates and args.reference and args.name):
        ap.error("--candidates, --reference and --name are required (or use --derive-gates)")
    run(args, log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
