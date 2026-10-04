#!/usr/bin/python3
"""v6 rules — form_v6: audio self-similarity form segmentation (chroma + MFCC + drums + stem levels) on the shared beat grid.

created: 2026-10-04
milestone: M-V6-RULES-1/audio-form

  /usr/bin/python3 scripts/v6/rules/form_v6.py [--chords-dir data/v6/rules/chords] [--chain data/v5/rules/harmony_markov_v5_full.json]
                                               [--v5-out data/v5/rules/form_plan_v5.json] [--v6-out data/v6/rules/form_v6.json] [--workers 2]

Per song (eligible = the harmony chain's gate.used, i.e. the songs whose chords_v6 / key passed harmony_rules_v6's gate):
  bars      stream bars of data/v6/rules/chords/<sha16>/chords_v6.json (bar 0 = first downbeat of the microtiming_v6 grid);
            the FORM grid starts at the hypermeter offset (form bar k = stream bar hypermeter_offset + k), so every 4- and
            8-bar multiple below is a hypermetric multiple; lead-in bars before it are disclosed (n_lead_bars).
  features  per bar, four L2-normalised groups weighted 1/2 each (cosine of the concatenation = mean of the group cosines):
            12-D mean beat chroma (chords_v6 beat_chroma), 20-D mean beat MFCC of the stem mix (z-scored per coefficient
            over the song's beats), 48-D kick16|snare16|hat16 onset bits (chords_v6 drum_masks), 4-D per-stem beat RMS
            (drums / bass / other / vocals, each / its song max).
  blocks    8-bar blocks from the form grid, block feature = concat of the four group means; cosine self-similarity;
            deterministic single linkage at form_plan_v5.SIM_THRESHOLD (0.85, data/v5/gen/form_prereg_c85.json);
            labels in first-appearance order -> form_blocks ("AABA..."). This is the form_plan_v5 model's input.
  segments  v6 segmentation: bar-level cosine self-similarity -> Foote checkerboard novelty (half-width 4 bars) at the
            4-bar hypermetric candidates -> local maxima >= NOVELTY_MIN, >= 4 bars apart -> segments (lengths multiples
            of 4 bars, snapped to downbeats by construction); segment labels by the same single-linkage rule on the
            segment-mean features -> form_segments ("A:8 B:8 A:8 C:4 ...").
  model     form_plan_v5.json key set (length distribution round(bars/8) clipped [4, 8]; label Markov over songs with >= 4
            blocks; per-label drum-density terciles + harmony region (most common tonic-relative root of the chords_v6
            stream); intro density quantile; boundary fill pool = snare|hat masks of the last bar before a label change,
            top-quartile snare popcount; R1 = every v6 focus song present recovers >= 3 labels AND a literal repeat, else
            the fallback template A A B A B C A A is recorded).
Outputs: data/v5/rules/form_plan_v5.json (read by scripts/v6/gen/fixtures.load_models / planner.plan_form) and
data/v6/rules/form_v6.json (per-song form strings, segments, novelty, block similarity). No PRNG; sorted-key atomic JSON.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.v6_data_common import ENV_PIN_SHA256, FOCUS_ORDER, WS, interpreter_guard, pin_env, read_json, sha256_file, write_json_atomic  # noqa: E402

pin_env()
interpreter_guard()
import numpy as np  # noqa: E402
from scripts.v5.form_plan_v5 import BARS_PER_BLOCK, FALLBACK_TEMPLATE, LEN_MAX, LEN_MIN, SIM_THRESHOLD, cosine_matrix, first_appearance_labels, popcount, single_linkage  # noqa: E402  READ-ONLY
from scripts.v6 import microtiming_v6 as MT  # noqa: E402  READ-ONLY (load_mono)

SR, HOP, N_MFCC = 22050, 512, 20
NOVELTY_HALF_BARS, NOVELTY_MIN, MIN_SEGMENT_BARS = 4, 0.15, 4
STEMS = ("drums", "bass", "other", "vocals")
GROUPS = {"chroma": 12, "mfcc": N_MFCC, "drums": 48, "levels": 4}
STEMS_DIR = WS / "data/v6/stems"
CHORDS_DIR = WS / "data/v6/rules/chords"
CHAIN = WS / "data/v5/rules/harmony_markov_v5_full.json"
PREREG = WS / "data/v5/gen/form_prereg_c85.json"
V5_OUT = WS / "data/v5/rules/form_plan_v5.json"
V6_OUT = WS / "data/v6/rules/form_v6.json"
LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _norm(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 0 else v


def group_concat(rows: np.ndarray) -> np.ndarray:
    """Mean of per-bar rows -> each group L2-normalised and weighted 1/2 (so the cosine = mean of group cosines)."""
    m = rows.mean(axis=0)
    out, i = np.zeros_like(m), 0
    for _g, d in GROUPS.items():
        out[i:i + d] = 0.5 * _norm(m[i:i + d])
        i += d
    return out


# ------------------------------------------------------------------------------------------------------- features ----
def beat_mfcc_levels(stems: dict, beats: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(z-scored beat MFCC (n_beats, 20) of the stem mix, per-stem beat RMS / song max (n_beats, 4)) on the grid beats."""
    import librosa
    n = min(y.size for y in stems.values())
    mix = sum(stems[k][:n] for k in STEMS).astype(np.float32)
    frames = np.clip(librosa.time_to_frames(beats, sr=SR, hop_length=HOP), 0, None)
    M = librosa.feature.mfcc(y=mix, sr=SR, n_mfcc=N_MFCC, hop_length=HOP)
    frames = np.clip(frames, 0, M.shape[1] - 1)
    bm = librosa.util.sync(M, frames, aggregate=np.mean)[:, 1:].T
    bm = (bm - bm.mean(axis=0)) / (bm.std(axis=0) + 1e-9)
    lv = []
    for k in STEMS:
        r = librosa.feature.rms(y=stems[k][:n], frame_length=2048, hop_length=HOP)[0]
        br = librosa.util.sync(r[None, :], np.clip(frames, 0, r.size - 1), aggregate=np.mean)[0, 1:]
        lv.append(br / (br.max() + 1e-9))
    return bm, np.stack(lv, axis=1)


def bar_features(rec: dict, mfcc: np.ndarray, levels: np.ndarray) -> dict:
    """Per FORM bar (from the hypermeter offset): 84-D raw feature rows + drum density + relative chord roots."""
    g = rec["grid"]
    phase, hoff = int(g["phase"]), int(g["hypermeter_offset"])
    n_bars = int(g["n_bars_from_first_downbeat"])
    chroma = np.asarray(rec["beat_chroma"], dtype=float)
    masks = rec["drum_masks"]
    tonic = int(rec["key"]["tonic"])
    rel_root = {}
    for e in rec["chords"]["chord_stream"]:
        if e["root"] is not None:
            rel_root.setdefault(e["bar"], []).append((int(e["root"]) - tonic) % 12)
    rows, dens, roots = [], [], []
    for b in range(hoff, n_bars):
        gb = slice(phase + 4 * b, phase + 4 * b + 4)
        bits = np.zeros(48)
        for j, k in enumerate(("kick", "snare", "hat")):
            m = int(masks[k][b])
            for pos in range(16):
                if m >> pos & 1:
                    bits[16 * j + pos] = 1.0
        rows.append(np.concatenate([chroma[gb].mean(axis=0), mfcc[gb].mean(axis=0), bits, levels[gb].mean(axis=0)]))
        dens.append(float(sum(popcount(masks[k][b]) for k in ("kick", "snare", "hat"))))
        roots.append(rel_root.get(b, []))
    return {"rows": np.asarray(rows), "density": np.asarray(dens), "roots": roots, "n_lead_bars": hoff, "n_form_bars": n_bars - hoff, "n_bars": n_bars}


# --------------------------------------------------------------------------------------------------- segmentation ----
def novelty_curve(S: np.ndarray, half: int = NOVELTY_HALF_BARS) -> list:
    """Foote checkerboard novelty at every 4-bar candidate boundary b (between bars b-1 and b): [(b, novelty)]."""
    n = S.shape[0]
    out = []
    for b in range(MIN_SEGMENT_BARS, n - MIN_SEGMENT_BARS + 1, MIN_SEGMENT_BARS):
        lo, hi = max(0, b - half), min(n, b + half)
        a, c, x = S[lo:b, lo:b], S[b:hi, b:hi], S[lo:b, b:hi]
        out.append((b, round(float(a.mean() + c.mean() - 2.0 * x.mean()), 6)))
    return out


def pick_boundaries(nov: list, thr: float = NOVELTY_MIN) -> list:
    """Local maxima (ties -> the earlier candidate) with novelty >= thr; neighbours are the adjacent 4-bar candidates."""
    vals = {b: v for b, v in nov}
    out = []
    for b, v in nov:
        left, right = vals.get(b - MIN_SEGMENT_BARS, -np.inf), vals.get(b + MIN_SEGMENT_BARS, -np.inf)
        if v >= thr and v > left and v >= right:
            out.append(b)
    return out


def segment_labels(rows: np.ndarray, bounds: list, n: int) -> tuple[list, str]:
    """Segments between the boundaries, labelled by single linkage (SIM_THRESHOLD) on the segment-mean features."""
    edges = [0] + list(bounds) + [n]
    segs = [(a, b) for a, b in zip(edges, edges[1:]) if b > a]
    F = np.asarray([group_concat(rows[a:b]) for a, b in segs]) if segs else np.zeros((0, rows.shape[1]))
    labels = first_appearance_labels(single_linkage(cosine_matrix(F), SIM_THRESHOLD)) if segs else ""
    out = [{"start_bar": a, "n_bars": b - a, "label": labels[i]} for i, (a, b) in enumerate(segs)]
    return out, " ".join(f"{s['label']}:{s['n_bars']}" for s in out)


def block_form(rows: np.ndarray) -> tuple[str, np.ndarray, int]:
    n_blocks = rows.shape[0] // BARS_PER_BLOCK
    if n_blocks == 0:
        return "", np.zeros((0, 0)), 0
    F = np.asarray([group_concat(rows[BARS_PER_BLOCK * j: BARS_PER_BLOCK * (j + 1)]) for j in range(n_blocks)])
    S = cosine_matrix(F)
    return first_appearance_labels(single_linkage(S, SIM_THRESHOLD)), S, n_blocks


def analyse_song(sha16: str, chords_dir: Path = CHORDS_DIR) -> dict:
    t0 = time.time()
    rec = read_json(chords_dir / sha16 / "chords_v6.json")
    beats = np.asarray(rec["grid"]["beat_times"], dtype=float)
    stems = {k: MT.load_mono(STEMS_DIR / sha16 / f"{k}.wav") for k in STEMS}
    mfcc, levels = beat_mfcc_levels(stems, beats)
    out = analyse_record(sha16, rec, mfcc, levels)
    out.update({"chords_sha256": sha256_file(chords_dir / sha16 / "chords_v6.json"), "wall_s": round(time.time() - t0, 1)})
    return out


def analyse_record(sha16: str, rec: dict, mfcc: np.ndarray, levels: np.ndarray) -> dict:
    """Pure per-song analysis from a chords_v6 record + beat MFCC / levels (no I/O; synthetic tests call this directly)."""
    bf = bar_features(rec, mfcc, levels)
    rows = bf["rows"]
    n = rows.shape[0]
    S_bar = cosine_matrix(np.asarray([group_concat(rows[i:i + 1]) for i in range(n)])) if n else np.zeros((0, 0))
    nov = novelty_curve(S_bar) if n >= 2 * MIN_SEGMENT_BARS else []
    bounds = pick_boundaries(nov)
    segs, form_segments = segment_labels(rows, bounds, n)
    form_blocks, S_blk, n_blocks = block_form(rows)
    dens = [round(float(bf["density"][BARS_PER_BLOCK * j: BARS_PER_BLOCK * (j + 1)].mean()), 6) for j in range(n_blocks)]
    roots = []
    for j in range(n_blocks):
        cnt: dict = {}
        for k in range(BARS_PER_BLOCK * j, BARS_PER_BLOCK * (j + 1)):
            for r in bf["roots"][k]:
                cnt[r] = cnt.get(r, 0) + 1
        roots.append(min(cnt, key=lambda x: (-cnt[x], x)) if cnt else None)
    masks = rec["drum_masks"]
    bars_abs = lambda k: k + bf["n_lead_bars"]  # noqa: E731  form bar -> stream bar (drum_masks index)
    return {"sha16": sha16, "title": rec.get("title"), "band": rec.get("band"), "bpm_v5": float(rec["bpm"]), "bar_count_at_bpm_v5": float(bf["n_bars"]),
            "n_bars": bf["n_bars"], "n_lead_bars": bf["n_lead_bars"], "n_form_bars": bf["n_form_bars"], "n_blocks": n_blocks,
            "n_sections_for_length": max(LEN_MIN, min(LEN_MAX, int(round(bf["n_bars"] / 8.0)))), "phase_offset": int(rec["grid"]["phase"]),
            "form": form_blocks, "n_labels": len(set(form_blocks)), "has_literal_repeat": any(form_blocks.count(c) >= 2 for c in set(form_blocks)),
            "in_transition_corpus": n_blocks >= LEN_MIN, "block_density": dens, "block_root": roots, "has_harmony_stream": True,
            "similarity": S_blk.tolist(), "segments": segs, "form_segments": form_segments, "n_segments": len(segs), "boundaries_form_bars": bounds,
            "novelty": [{"bar": b, "novelty": v} for b, v in nov], "bar_similarity_mean": round(float(S_bar.mean()), 6) if n else None,
            "boundaries_on_8bar_multiple": sum(1 for b in bounds if b % 8 == 0),
            "last_bar_masks": [{"block": j, "snare": int(masks["snare"][bars_abs(BARS_PER_BLOCK * j + 7)]), "hat": int(masks["hat"][bars_abs(BARS_PER_BLOCK * j + 7)])} for j in range(n_blocks)],
            "all_bar_masks": [{"bar": k, "snare": int(masks["snare"][bars_abs(k)]), "hat": int(masks["hat"][bars_abs(k)])} for k in range(bf["n_form_bars"])]}


# -------------------------------------------------------------------------------------------------------- model ----
def corpus_model(per_song: dict, eligible: list, focus: tuple) -> dict:
    """form_plan_v5 model block from the per-song block forms (same rules as scripts/v5/form_plan_v5.main)."""
    forms = [per_song[s]["form"] for s in eligible if per_song[s]["in_transition_corpus"]]
    lengths: dict = {}
    for s in eligible:
        k = per_song[s]["n_sections_for_length"]
        lengths[k] = lengths.get(k, 0) + 1
    labels_seen = sorted({c for f in forms for c in f})
    start, trans = {}, {}
    for f in forms:
        start[f[0]] = start.get(f[0], 0) + 1
        for a, b in zip(f, f[1:]):
            trans.setdefault(a, {})[b] = trans.setdefault(a, {}).get(b, 0) + 1
    trans_probs = {}
    for a in labels_seen:
        row, tot = trans.get(a, {}), sum(trans.get(a, {}).values())
        trans_probs[a] = {b: (row.get(b, 0) / tot if tot else 1.0 / len(labels_seen)) for b in labels_seen}
    dens_all = np.asarray([d for s in eligible for d in per_song[s]["block_density"]])
    t1, t2 = (float(np.percentile(dens_all, 33.333)), float(np.percentile(dens_all, 66.667))) if len(dens_all) else (0.0, 0.0)
    per_label: dict = {}
    for s in eligible:
        p = per_song[s]
        for j, lab in enumerate(p["form"]):
            e = per_label.setdefault(lab, {"n_blocks": 0, "density_tercile_counts": [0, 0, 0], "root_counts": {}})
            e["n_blocks"] += 1
            d = p["block_density"][j]
            e["density_tercile_counts"][0 if d < t1 else (1 if d < t2 else 2)] += 1
            if p["block_root"][j] is not None:
                e["root_counts"][str(p["block_root"][j])] = e["root_counts"].get(str(p["block_root"][j]), 0) + 1
    for lab, e in per_label.items():
        n = sum(e["density_tercile_counts"])
        e["density_tercile_probs"] = [round(c / n, 6) if n else 1 / 3 for c in e["density_tercile_counts"]]
        e["harmony_region"] = int(min(e["root_counts"], key=lambda r: (-e["root_counts"][r], int(r)))) if e["root_counts"] else None
    intro = [float((dens_all < per_song[s]["block_density"][0]).mean()) for s in eligible if per_song[s]["block_density"]]
    boundary = []
    for si, s in enumerate(eligible):
        p = per_song[s]
        for j in range(p["n_blocks"] - 1):
            if p["form"][j] != p["form"][j + 1]:
                m = p["last_bar_masks"][j]
                boundary.append((m["snare"], m["hat"], si, BARS_PER_BLOCK * j + 7))
    fill_pool, fallback = [], False
    if boundary and max(popcount(b[0]) for b in boundary) > 0:
        q75 = float(np.percentile([popcount(b[0]) for b in boundary], 75))
        cnt: dict = {}
        for snare, hat, _si, _k in boundary:
            if popcount(snare) >= q75:
                cnt[(snare, hat)] = cnt.get((snare, hat), 0) + 1
        fill_pool = [{"snare": k[0], "hat": k[1], "count": v} for k, v in sorted(cnt.items())]
    if not fill_pool:
        fallback = True
        allbars = [(popcount(m["snare"]), si, m["bar"], m["snare"], m["hat"]) for si, s in enumerate(eligible) for m in per_song[s]["all_bar_masks"]]
        best = max(allbars, key=lambda x: (x[0], -x[1], -x[2])) if allbars else (0, 0, 0, 0xF000, 0x5555)
        fill_pool = [{"snare": best[3], "hat": best[4], "count": 1}]
    r1 = {s: {"n_labels": per_song[s]["n_labels"], "has_literal_repeat": per_song[s]["has_literal_repeat"], "form": per_song[s]["form"]} for s in focus}
    r1_pass = bool(focus) and all(v["n_labels"] >= 3 and v["has_literal_repeat"] for v in r1.values())
    rep_a = trans_probs.get("A", {}).get("A")
    return {"length_distribution": {str(k): v for k, v in sorted(lengths.items())}, "n_songs_in_transition_corpus": len(forms), "labels": labels_seen,
            "start_counts": dict(sorted(start.items())), "start_distribution": {k: round(v / sum(start.values()), 6) for k, v in sorted(start.items())} if start else {},
            "transition_counts": {a: dict(sorted(trans.get(a, {}).items())) for a in labels_seen},
            "transition_probs": {a: {b: round(p, 6) for b, p in trans_probs[a].items()} for a in labels_seen},
            "repeat_A_probability": round(rep_a, 6) if rep_a is not None else None, "density_tercile_bounds": [round(t1, 6), round(t2, 6)],
            "n_blocks_total": int(len(dens_all)), "per_label": per_label, "intro_density_quantile": round(float(np.median(intro)), 6) if intro else None,
            "boundary_fill_pool": fill_pool, "n_boundary_bars": len(boundary), "fill_pool_fallback_used": fallback,
            "R1": {"focus_songs": r1, "pass": r1_pass, "fallback_template": list(FALLBACK_TEMPLATE) if not r1_pass else None, "focus_eligible": list(focus)}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 audio self-similarity form model (form_plan_v5 schema + v6 segments)")
    ap.add_argument("--chords-dir", default=str(CHORDS_DIR))
    ap.add_argument("--chain", default=str(CHAIN))
    ap.add_argument("--v5-out", default=str(V5_OUT))
    ap.add_argument("--v6-out", default=str(V6_OUT))
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args(argv)
    cd, chain_p, v5p, v6p = (Path(p) if Path(p).is_absolute() else WS / p for p in (args.chords_dir, args.chain, args.v5_out, args.v6_out))
    if chain_p.exists():
        eligible, elig_src = list(read_json(chain_p)["gate"]["used"]), str(chain_p.relative_to(WS)) + " gate.used"
    else:
        eligible, elig_src = sorted(p.parent.name for p in cd.glob("*/chords_v6.json")), "chain absent: every song with a chords_v6.json"
    eligible = [s for s in eligible if (cd / s / "chords_v6.json").exists()]
    focus = tuple(s for s in FOCUS_ORDER if s in eligible)
    if args.workers > 1 and len(eligible) > 1:
        import functools
        import multiprocessing as mp
        with mp.get_context("fork").Pool(args.workers) as pool:
            per_song = dict(zip(eligible, pool.map(functools.partial(analyse_song, chords_dir=cd), eligible, chunksize=1)))
    else:
        per_song = {s: analyse_song(s, cd) for s in eligible}
    for s in eligible:
        p = per_song[s]
        print(f"{s} {str(p['title'])[:26]:26s} bars={p['n_bars']:3d} lead={p['n_lead_bars']} blocks={p['n_blocks']:2d} form={p['form']:12s} segs={p['form_segments']} wall={p['wall_s']}s", flush=True)
    model = corpus_model(per_song, eligible, focus)
    common = {"schema_version": 1, "cycle": 600, "agent": "worker", "run_id": "v6-rules-2026-10-04", "milestone": "M-V6-RULES-1/audio-form", "env_pin_sha256": ENV_PIN_SHA256,
              "generator": "scripts/v6/rules/form_v6.py", "prereg_path": str(PREREG.relative_to(WS)), "prereg_sha256": sha256_file(PREREG) if PREREG.exists() else None,
              "chain_path": str(chain_p.relative_to(WS)) if str(chain_p).startswith(str(WS)) else str(chain_p), "chain_sha256": sha256_file(chain_p) if chain_p.exists() else None,
              "eligible": eligible, "n_eligible": len(eligible), "eligible_source": elig_src,
              "excluded_disclosed": {"tempo_blocked": [], "not_in_chain": sorted(p.parent.name for p in cd.glob("*/chords_v6.json") if p.parent.name not in eligible)},
              "params": {"bars_per_block": BARS_PER_BLOCK, "similarity_threshold": SIM_THRESHOLD, "length_clip": [LEN_MIN, LEN_MAX], "feature_dims": dict(GROUPS), "group_weight": "1/2 (four groups)",
                         "linkage": "single, deterministic (form_plan_v5.single_linkage)", "novelty": {"kernel_half_bars": NOVELTY_HALF_BARS, "min": NOVELTY_MIN, "candidate_step_bars": MIN_SEGMENT_BARS},
                         "mfcc": {"n_mfcc": N_MFCC, "hop": HOP, "source": "sum of the four stems, z-scored per coefficient over the song's grid beats"},
                         "source": "audio (data/v6/stems) on the microtiming_v6 grid via chords_v6.json; form grid starts at the hypermeter offset"}, **model}
    v5_keys = ("title", "bpm_v5", "bar_count_at_bpm_v5", "n_bars", "n_blocks", "n_sections_for_length", "phase_offset", "form", "n_labels", "has_literal_repeat",
               "in_transition_corpus", "block_density", "block_root", "has_harmony_stream", "similarity", "n_lead_bars", "form_segments")
    write_json_atomic(v5p, dict(common, per_song={s: {k: per_song[s][k] for k in v5_keys} for s in eligible}))
    v6_songs = {s: {k: v for k, v in per_song[s].items() if k != "all_bar_masks"} for s in eligible}
    seg_lens: dict = {}
    for s in eligible:
        for g in per_song[s]["segments"]:
            seg_lens[str(g["n_bars"])] = seg_lens.get(str(g["n_bars"]), 0) + 1
    n_b = sum(len(per_song[s]["boundaries_form_bars"]) for s in eligible)
    summary = {"form_strings": {s: {"blocks": per_song[s]["form"], "segments": per_song[s]["form_segments"], "title": per_song[s]["title"]} for s in eligible},
               "n_labels_histogram": {str(k): sum(1 for s in eligible if per_song[s]["n_labels"] == k) for k in sorted({per_song[s]["n_labels"] for s in eligible})},
               "segment_length_histogram": {k: seg_lens[k] for k in sorted(seg_lens, key=int)}, "n_boundaries": n_b,
               "fraction_boundaries_on_8bar_multiple": round(sum(per_song[s]["boundaries_on_8bar_multiple"] for s in eligible) / n_b, 6) if n_b else None,
               "n_songs_literal_repeat": sum(1 for s in eligible if per_song[s]["has_literal_repeat"])}
    write_json_atomic(v6p, dict(common, per_song=v6_songs, summary=summary))
    if PREREG.exists():
        assert PREREG.stat().st_mtime < v5p.stat().st_mtime, "PREREG_GATE: output mtime does not exceed the prereg mtime"
    print(f"lengths {model['length_distribution']}; labels {model['labels']}; start {model['start_distribution']}; repeat_A {model['repeat_A_probability']}; "
          f"terciles {model['density_tercile_bounds']}; intro_q {model['intro_density_quantile']}; fill pool {len(model['boundary_fill_pool'])} (fallback {model['fill_pool_fallback_used']}); "
          f"R1 pass {model['R1']['pass']} {model['R1']['focus_songs']}")
    print(f"n_labels histogram {summary['n_labels_histogram']}; segment lengths {summary['segment_length_histogram']}; 8-bar boundaries {summary['fraction_boundaries_on_8bar_multiple']}")
    print(f"wrote {v5p} and {v6p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
