#!/usr/bin/python3
"""v6 Phase 5 (iteration 05) — gap localisation IN EMBEDDING SPACE: spread / homogeneity and discriminant descriptors.

created: 2026-10-05
milestone: M-V6-ITER-05/localize

  diag_embed_v6.py spread --scorecard data/v6/scorecard/runs/<run>/scorecard.json [--backbones clap,mert]
      Candidate vs reference song-mean embeddings (unit-norm mean of unit-normed windows, diag_common.song_means): the pairwise
      cosine distribution among candidate songs vs among reference songs (mean / sd / p5 / p50 / p95), spread = 1 - mean pairwise
      cosine, and the between-song / within-song variance ratio (trace of the song-mean covariance over the mean within-song window
      covariance trace). PRE-REGISTERED RULE: homogeneity is a confirmed gap when candidate between-song spread < 0.60 x the
      reference's (per backbone).
  diag_embed_v6.py descriptors --scorecard <run>/scorecard.json [--backbones clap,mert]
      Per-WINDOW audio descriptors on the very windows the embeddings were cut from (window_start_s in the npz sidecars; the
      format-matched candidate files and the reference files): spectral centroid / bandwidth / flatness / rolloff (0.85), onset rate,
      dynamic range (p95 - p5 of frame RMS dB), harmonic/percussive energy ratio (librosa HPSS), low (< 250 Hz) / mid / high (> 4 kHz)
      band energy ratios, RMS, crest, zero-crossing rate, stereo width (undefined -> dropped for a mono reference). Discriminant:
      Fisher/LDA direction w = Sigma_pooled^-1 (mu_cand - mu_ref) with a Ledoit-Wolf shrunk pooled covariance; per-window score x.w,
      reported with its AUC (candidate-vs-reference separability along w). For every descriptor: Spearman rho with the score over
      all windows, candidate-minus-reference mean gap, Cohen's d and the Mann-Whitney AUC. Ranked by |rho|: this names what the
      classifier hears. Descriptors are cached per file under the diagnostics dir.

Discipline: /usr/bin/python3 guard (through the imported modules); no PRNG; sorted-key atomic JSON; writes under data/v6 only.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))

import numpy as np  # noqa: E402

from scripts.v6 import diag_common as dc  # noqa: E402
from scripts.v6 import distribution_metrics as dm  # noqa: E402
from scripts.v6 import embed_audio as ea  # noqa: E402
from scripts.v6.v6_common import env_record, read_json, write_json_atomic  # noqa: E402

HOMOGENEITY_RULE = 0.60  # candidate between-song spread < this x the reference's -> homogeneity confirmed
DESCRIPTORS = ("spectral_centroid_hz", "spectral_bandwidth_hz", "spectral_flatness", "spectral_rolloff_hz", "onset_rate_hz", "dynamic_range_db",
               "hp_ratio_db", "low_ratio_db", "mid_ratio_db", "high_ratio_db", "rms_db", "crest_db", "zcr", "stereo_width_db")
DESC_SCHEMA = "v6.window_descriptors.1"


def _log(msg):
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)


# ============================================================================= loading
def songs_from_scorecard(scd: dict, backbone: str, emb_dir: Path) -> tuple[list, list]:
    """(candidate Songs, reference Songs) of a scorecard run: npz by sha16 under <emb_dir>/<backbone>/ (format-matched candidates
    when the run was a fair-mode run: their transformed sha16 is what scorecard.json lists)."""
    bdir = ea.embeddings_dir(emb_dir, backbone)
    cands = dm.load_songs([bdir / f"{c['sha16']}.npz" for c in scd["candidates"]["files"] if (bdir / f"{c['sha16']}.npz").exists()])
    refs = dm.load_songs([bdir / f"{r['sha16']}.npz" for r in scd["reference"]["files"] if (bdir / f"{r['sha16']}.npz").exists()])
    labels = {r["sha16"]: r["label"] for r in scd["reference"]["files"]}
    for s in refs:
        s.song_id = labels.get(s.sha16, s.song_id)
    return cands, refs


# ============================================================================= spread
def pairwise_cos_stats(M: np.ndarray) -> dict:
    C = M @ M.T
    iu = np.triu_indices(len(M), 1)
    v = C[iu]
    return {"n_pairs": int(len(v)), "mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0, "p5": float(np.percentile(v, 5)),
            "p50": float(np.percentile(v, 50)), "p95": float(np.percentile(v, 95)), "min": float(v.min()), "max": float(v.max())}


def variance_ratio(songs: list) -> dict:
    """between = trace cov(song means); within = mean over songs of trace cov(unit-normed windows); ratio between/within."""
    means = dc.song_means(songs)
    between = float(np.trace(np.cov(means, rowvar=False))) if len(means) > 1 else 0.0
    within = []
    for s in songs:
        X = np.asarray(s.emb, dtype=np.float64)
        Xn = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
        if len(Xn) > 1:
            within.append(float(np.trace(np.cov(Xn, rowvar=False))))
    w = float(np.mean(within)) if within else float("nan")
    return {"between_song_var": between, "within_song_var": w, "ratio": between / w if w > 0 else None}


def spread(scd: dict, backbones: list, emb_dir: Path, out: Path, log=_log) -> dict:
    rep = {"schema_version": dc.SCHEMA_VERSION, "scorecard": scd["name"], "rule": f"homogeneity confirmed when candidate between-song spread (1 - mean pairwise cosine of song means) "
           f"< {HOMOGENEITY_RULE} x the reference's (pre-registered, iteration 05)", "backbones": {}, "env": env_record()}
    for bb in backbones:
        cands, refs = songs_from_scorecard(scd, bb, emb_dir)
        if not cands or not refs:
            rep["backbones"][bb] = {"error": f"missing embeddings ({len(cands)} cand / {len(refs)} ref)"}
            continue
        pc, pr = pairwise_cos_stats(dc.song_means(cands)), pairwise_cos_stats(dc.song_means(refs))
        vc, vr = variance_ratio(cands), variance_ratio(refs)
        sc_, sr_ = 1.0 - pc["mean"], 1.0 - pr["mean"]
        # cross set: how close candidate song means come to reference song means vs reference-to-reference
        Mc, Mr = dc.song_means(cands), dc.song_means(refs)
        cross = Mc @ Mr.T
        b = {"n_candidates": len(cands), "n_reference": len(refs), "pairwise_cos_candidates": pc, "pairwise_cos_reference": pr,
             "spread_candidates": sc_, "spread_reference": sr_, "spread_ratio": sc_ / sr_ if sr_ > 0 else None,
             "variance_candidates": vc, "variance_reference": vr, "between_within_ratio_cand_over_ref": (vc["ratio"] / vr["ratio"]) if (vc["ratio"] and vr["ratio"]) else None,
             "cross_cos_mean": float(cross.mean()), "cross_nearest_ref_cos_mean": float(cross.max(axis=1).mean()),
             "homogeneity_confirmed": bool(sr_ > 0 and sc_ / sr_ < HOMOGENEITY_RULE)}
        rep["backbones"][bb] = b
        log(f"[spread:{bb}] cand pairwise cos {pc['mean']:.4f} (spread {sc_:.4f}) vs ref {pr['mean']:.4f} (spread {sr_:.4f}) ratio {b['spread_ratio']:.3f}; between/within "
            f"cand {vc['ratio']:.3f} ref {vr['ratio']:.3f} -> homogeneity {'CONFIRMED' if b['homogeneity_confirmed'] else 'not confirmed'}")
    out.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out / "spread_diagnostic.json", rep)
    (out / "SPREAD.md").write_text(spread_markdown(rep), encoding="utf-8")
    return rep


def spread_markdown(rep: dict) -> str:
    rows = []
    for bb, b in rep["backbones"].items():
        if "error" in b:
            rows.append([bb] + ["-"] * 10 + [b["error"]])
            continue
        rows.append([bb, b["pairwise_cos_candidates"]["mean"], b["pairwise_cos_candidates"]["p5"], b["pairwise_cos_candidates"]["p95"], b["pairwise_cos_reference"]["mean"],
                     b["pairwise_cos_reference"]["p5"], b["pairwise_cos_reference"]["p95"], b["spread_ratio"], b["variance_candidates"]["ratio"], b["variance_reference"]["ratio"],
                     b["cross_nearest_ref_cos_mean"], "CONFIRMED" if b["homogeneity_confirmed"] else "not confirmed"])
    return (f"# Spread / homogeneity of song-mean embeddings ({rep['scorecard']})\n\n{rep['rule']}\n\n"
            + dc.md_table(["backbone", "cand cos mean", "cand p5", "cand p95", "ref cos mean", "ref p5", "ref p95", "spread ratio (cand/ref)", "between/within cand",
                           "between/within ref", "cand->nearest ref cos", "homogeneity"], rows))


# ============================================================================= window descriptors
def window_descriptors(y: np.ndarray, sr: int, stereo: np.ndarray | None = None) -> dict:
    import librosa
    y = np.asarray(y, dtype=np.float32)
    n_fft, hop = 2048, 512
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop)) ** 2
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    cent = librosa.feature.spectral_centroid(S=np.sqrt(S), sr=sr)[0]
    bw = librosa.feature.spectral_bandwidth(S=np.sqrt(S), sr=sr)[0]
    flat = librosa.feature.spectral_flatness(S=np.sqrt(S))[0]
    roll = librosa.feature.spectral_rolloff(S=np.sqrt(S), sr=sr, roll_percent=0.85)[0]
    rms = librosa.feature.rms(S=np.sqrt(S))[0]
    rms_db = 20.0 * np.log10(np.maximum(rms, 1e-9))
    onsets = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop, units="frames")
    H, P = librosa.decompose.hpss(librosa.stft(y, n_fft=n_fft, hop_length=hop))
    eh, ep = float((np.abs(H) ** 2).sum()), float((np.abs(P) ** 2).sum())
    tot = float(S.sum()) + 1e-18
    low, mid, high = float(S[freqs < 250.0].sum()), float(S[(freqs >= 250.0) & (freqs < 4000.0)].sum()), float(S[freqs >= 4000.0].sum())
    peak = float(np.abs(y).max()) if y.size else 0.0
    r = float(np.sqrt(np.mean(y.astype(np.float64) ** 2))) if y.size else 0.0
    d = {"spectral_centroid_hz": float(cent.mean()), "spectral_bandwidth_hz": float(bw.mean()), "spectral_flatness": float(flat.mean()), "spectral_rolloff_hz": float(roll.mean()),
         "onset_rate_hz": float(len(onsets) / (len(y) / sr)), "dynamic_range_db": float(np.percentile(rms_db, 95) - np.percentile(rms_db, 5)),
         "hp_ratio_db": 10.0 * np.log10(max(eh, 1e-18) / max(ep, 1e-18)), "low_ratio_db": 10.0 * np.log10(max(low, 1e-18) / tot),
         "mid_ratio_db": 10.0 * np.log10(max(mid, 1e-18) / tot), "high_ratio_db": 10.0 * np.log10(max(high, 1e-18) / tot),
         "rms_db": 20.0 * np.log10(max(r, 1e-9)), "crest_db": 20.0 * np.log10(max(peak, 1e-9) / max(r, 1e-9)),
         "zcr": float(librosa.feature.zero_crossing_rate(y, frame_length=n_fft, hop_length=hop)[0].mean()), "stereo_width_db": None}
    if stereo is not None and stereo.shape[1] >= 2:
        L, R = stereo[:, 0].astype(np.float64), stereo[:, 1].astype(np.float64)
        mid_, side_ = 0.5 * (L + R), 0.5 * (L - R)
        em, es = float(np.dot(mid_, mid_)), float(np.dot(side_, side_))
        d["stereo_width_db"] = 10.0 * np.log10(max(es, 1e-20) / max(em, 1e-20)) if em > 0 else None
    return {k: (float(v) if v is not None else None) for k, v in d.items()}


def file_window_descriptors(path: Path, starts: np.ndarray, window_s: float, cache: Path, log=_log) -> list:
    """Descriptors of the windows [t, t + window_s) at the file's native rate; cached by (sha16 of the npz identity) in `cache`."""
    import soundfile as sf
    if cache.exists():
        rec = read_json(cache)
        if rec.get("schema_version") == DESC_SCHEMA and rec.get("n_windows") == len(starts):
            return rec["windows"]
    t0 = time.time()
    x, sr = sf.read(str(path), dtype="float32", always_2d=True)
    mono = x.mean(axis=1)
    L = int(round(window_s * sr))
    rows = []
    for t in starts:
        a = int(round(float(t) * sr))
        rows.append(window_descriptors(mono[a:a + L], sr, x[a:a + L] if x.shape[1] >= 2 else None))
    write_json_atomic(cache, {"schema_version": DESC_SCHEMA, "path": str(path), "sr": int(sr), "window_s": window_s, "n_windows": len(rows), "windows": rows, "wall_s": round(time.time() - t0, 2)})
    log(f"[desc] {path.name}: {len(rows)} windows in {time.time() - t0:.1f}s")
    return rows


def _lda_direction(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    from sklearn.covariance import ledoit_wolf
    Z = np.concatenate([X - X.mean(axis=0), Y - Y.mean(axis=0)], axis=0)
    cov = ledoit_wolf(Z)[0]
    w = np.linalg.solve(cov + 1e-9 * np.eye(cov.shape[0]), X.mean(axis=0) - Y.mean(axis=0))
    return w / max(float(np.linalg.norm(w)), 1e-12)


def _auc(a: np.ndarray, b: np.ndarray) -> float:
    """P(a > b) by ranks (Mann-Whitney AUC)."""
    from scipy.stats import rankdata
    r = rankdata(np.concatenate([a, b]))
    return float((r[: len(a)].sum() - len(a) * (len(a) + 1) / 2.0) / (len(a) * len(b)))


def discriminant_table(score_c: np.ndarray, score_r: np.ndarray, Dc: dict, Dr: dict) -> list:
    from scipy.stats import spearmanr
    s_all = np.concatenate([score_c, score_r])
    rows = []
    for k in DESCRIPTORS:
        a, b = np.asarray(Dc[k], dtype=np.float64), np.asarray(Dr[k], dtype=np.float64)
        if np.isnan(a).all() or np.isnan(b).all():
            continue
        v = np.concatenate([a, b])
        ok = np.isfinite(v)
        rho = float(spearmanr(v[ok], s_all[ok]).statistic) if ok.sum() > 3 else None
        ma, mb = float(np.nanmean(a)), float(np.nanmean(b))
        sp = float(np.sqrt((np.nanvar(a, ddof=1) + np.nanvar(b, ddof=1)) / 2.0))
        rows.append({"descriptor": k, "spearman_rho": rho, "cand_mean": ma, "ref_mean": mb, "gap": ma - mb, "cohen_d": (ma - mb) / sp if sp > 0 else None,
                     "auc_cand_gt_ref": _auc(a[np.isfinite(a)], b[np.isfinite(b)]), "cand_sd": float(np.nanstd(a, ddof=1)), "ref_sd": float(np.nanstd(b, ddof=1))})
    return sorted(rows, key=lambda r: -(abs(r["spearman_rho"]) if r["spearman_rho"] is not None else -1))


def descriptors(scd: dict, backbones: list, emb_dir: Path, out: Path, log=_log) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    cache_dir = out / "window_descriptors"
    cache_dir.mkdir(exist_ok=True)
    rep = {"schema_version": dc.SCHEMA_VERSION, "scorecard": scd["name"], "descriptors": list(DESCRIPTORS), "backbones": {}, "env": env_record(),
           "method": "LDA direction w = LW-shrunk pooled cov^-1 (mu_cand - mu_ref) in embedding space; per-window score x.w; Spearman rho(descriptor, score) over all windows"}
    for bb in backbones:
        cands, refs = songs_from_scorecard(scd, bb, emb_dir)
        bdir = ea.embeddings_dir(emb_dir, bb)
        Dc, Dr = {k: [] for k in DESCRIPTORS}, {k: [] for k in DESCRIPTORS}
        for songs, D in ((cands, Dc), (refs, Dr)):
            for s in songs:
                side = read_json(bdir / f"{s.sha16}.json")
                starts = np.load(bdir / f"{s.sha16}.npz")["window_start_s"]
                rows = file_window_descriptors(Path(side["path"]), starts, float(side["settings"]["window_s"]), cache_dir / f"{s.sha16}.json", log)
                for k in DESCRIPTORS:
                    D[k] += [np.nan if r.get(k) is None else r[k] for r in rows]
        X, _ = dm.stack(cands)
        Y, _ = dm.stack(refs)
        w = _lda_direction(X, Y)
        sc_, sr_ = X @ w, Y @ w
        table = discriminant_table(sc_, sr_, Dc, Dr)
        rep["backbones"][bb] = {"n_windows_cand": int(len(X)), "n_windows_ref": int(len(Y)), "dim": int(X.shape[1]), "score_auc": _auc(sc_, sr_),
                                "score_cand_mean": float(sc_.mean()), "score_ref_mean": float(sr_.mean()), "table": table}
        log(f"[discriminant:{bb}] AUC {rep['backbones'][bb]['score_auc']:.3f}; top: " + ", ".join(f"{r['descriptor']} rho={r['spearman_rho']:+.2f} gap={r['gap']:+.3g}" for r in table[:5]))
    write_json_atomic(out / "discriminant_diagnostic.json", rep)
    (out / "DISCRIMINANT.md").write_text(descriptors_markdown(rep), encoding="utf-8")
    return rep


def descriptors_markdown(rep: dict) -> str:
    L = [f"# Discriminant descriptors ({rep['scorecard']})", "", rep["method"], ""]
    for bb, b in rep["backbones"].items():
        L += [f"## {bb} (score AUC {dc.fmt(b['score_auc'], 3)}; {b['n_windows_cand']} candidate / {b['n_windows_ref']} reference windows)", "",
              dc.md_table(["descriptor", "Spearman rho", "cand mean", "ref mean", "gap (cand - ref)", "Cohen d", "AUC cand>ref"],
                          [[r["descriptor"], r["spearman_rho"], r["cand_mean"], r["ref_mean"], r["gap"], r["cohen_d"], r["auc_cand_gt_ref"]] for r in b["table"]])]
    return "\n".join(L)


# ============================================================================= CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("cmd", choices=["spread", "descriptors"])
    ap.add_argument("--scorecard", required=True, help="scorecard.json of the run whose candidate / reference sets to analyse")
    ap.add_argument("--backbones", default="clap,mert")
    ap.add_argument("--emb-dir", default=str(ea.DEFAULT_OUT_DIR))
    ap.add_argument("--out", default=None, help="default data/v6/scorecard/diagnostics/iteration_05/<cmd>")
    a = ap.parse_args(argv)
    scd = read_json(a.scorecard)
    out = Path(a.out) if a.out else dc.DIAG_DIR / "iteration_05" / a.cmd
    bbs = [b.strip() for b in a.backbones.split(",") if b.strip()]
    (spread if a.cmd == "spread" else descriptors)(scd, bbs, Path(a.emb_dir), out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
