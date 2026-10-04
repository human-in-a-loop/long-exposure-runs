#!/usr/bin/python3
"""v6 Phase 3 — microtiming model: the pure-Python schema, pooling, prior and KS helpers shared by scripts/v6/microtiming_v6.py
(learning, numpy/librosa) and scripts/v6/gen/humanize.py / validators.py (generation, no numpy at import).

created: 2026-10-04
milestone: M-V6-GEN-3/humanization

Per-song entries carry SUFFICIENT STATISTICS (n, sum, sum of squares per 16th slot per stream; 41-bin histograms of the
deviation in fractions of a 16th; velocity cell sums) so any subset of songs — a rating band, or the songs within +/-15 %
of a target bpm ("near_tempo") — pools EXACTLY without re-reading audio. `pool(entries)` returns the generation-time model:
per stream the per-slot mean/std (ms and f16), the swing offset (mean deviation at odd-8th slots 2/6/10/14 minus even-8th
slots) and the per-slot RESIDUAL means with that swing removed (so the humanizer applies swing once, explicitly), the
velocity (dB relative to the stream mean) by slot / bar-in-8 / bar-in-4 / beat class, the bass-vs-kick lag, the bass
duration proxy histogram and the fill-density ratios. `PRIOR` is the fixture-mode fallback (no corpus stems).
"""
from __future__ import annotations

import math

STREAMS = ("kick", "snare", "hat", "bass")
DRUM_STREAMS = ("kick", "snare", "hat")
ODD_8TH = (2, 6, 10, 14)
EVEN_8TH = (0, 4, 8, 12)
REJECT_F16 = 0.4
HIST_EDGES = [round(-REJECT_F16 + i * (2 * REJECT_F16 / 41), 6) for i in range(42)]  # 41 bins over [-0.4, 0.4] (f16)
DUR_BINS = 20  # bass duration proxy histogram over [0, 1] (fraction of the inter-onset interval)
BEAT_CLASSES = ("downbeat", "backbeat", "beat3", "offbeat")
NEAR_TEMPO_FRAC = 0.15
MIN_SLOT_N = 5


def beat_class(slot16: int) -> str:
    s = slot16 % 16
    return "downbeat" if s == 0 else ("backbeat" if s in (4, 12) else ("beat3" if s == 8 else "offbeat"))


def empty_cells(n: int) -> list:
    return [{"n": 0, "s": 0.0, "ss": 0.0} for _ in range(n)]


def add_cell(c: dict, x: float) -> None:
    c["n"] += 1
    c["s"] += float(x)
    c["ss"] += float(x) * float(x)


def cell_mean(c: dict):
    return (c["s"] / c["n"]) if c["n"] else None


def cell_std(c: dict):
    if c["n"] < 2:
        return None
    m = c["s"] / c["n"]
    v = max(0.0, c["ss"] / c["n"] - m * m)
    return math.sqrt(v)


def merge_cells(a: list, b: list) -> list:
    return [{"n": x["n"] + y["n"], "s": x["s"] + y["s"], "ss": x["ss"] + y["ss"]} for x, y in zip(a, b)]


def empty_stream() -> dict:
    return {"ms": empty_cells(16), "f16": empty_cells(16), "db": empty_cells(16), "bar_mod4_db": empty_cells(4), "bar_mod8_db": empty_cells(8),
            "beat_class_db": {k: {"n": 0, "s": 0.0, "ss": 0.0} for k in BEAT_CLASSES}, "hist_f16": [0] * 41,
            "n_detected": 0, "n_assigned": 0, "n_rejected": 0, "n_out_of_grid": 0, "n_duplicate": 0, "level_mean_db": None}


def hist_index(f16: float) -> int:
    i = int((f16 + REJECT_F16) / (2 * REJECT_F16) * 41)
    return max(0, min(40, i))


def merge_stream(a: dict, b: dict) -> dict:
    out = {"ms": merge_cells(a["ms"], b["ms"]), "f16": merge_cells(a["f16"], b["f16"]), "db": merge_cells(a["db"], b["db"]),
           "bar_mod4_db": merge_cells(a["bar_mod4_db"], b["bar_mod4_db"]), "bar_mod8_db": merge_cells(a["bar_mod8_db"], b["bar_mod8_db"]),
           "beat_class_db": {k: {"n": a["beat_class_db"][k]["n"] + b["beat_class_db"][k]["n"], "s": a["beat_class_db"][k]["s"] + b["beat_class_db"][k]["s"],
                                 "ss": a["beat_class_db"][k]["ss"] + b["beat_class_db"][k]["ss"]} for k in BEAT_CLASSES},
           "hist_f16": [x + y for x, y in zip(a["hist_f16"], b["hist_f16"])]}
    for k in ("n_detected", "n_assigned", "n_rejected", "n_out_of_grid", "n_duplicate"):
        out[k] = a.get(k, 0) + b.get(k, 0)
    out["level_mean_db"] = None
    return out


def swing_of(cells_ms: list, cells_f16: list) -> dict:
    """Swing offset = mean deviation at odd-8th slots minus mean at even-8th slots; ratio = (2 + d) / (2 - d) with d in 16ths."""
    odd = {"n": sum(cells_ms[i]["n"] for i in ODD_8TH), "s": sum(cells_ms[i]["s"] for i in ODD_8TH)}
    even = {"n": sum(cells_ms[i]["n"] for i in EVEN_8TH), "s": sum(cells_ms[i]["s"] for i in EVEN_8TH)}
    odd_f = sum(cells_f16[i]["s"] for i in ODD_8TH)
    even_f = sum(cells_f16[i]["s"] for i in EVEN_8TH)
    if odd["n"] < MIN_SLOT_N or even["n"] < MIN_SLOT_N:
        return {"offset_ms": None, "offset_f16": None, "ratio": None, "n_odd": odd["n"], "n_even": even["n"]}
    d_ms = odd["s"] / odd["n"] - even["s"] / even["n"]
    d_f = odd_f / odd["n"] - even_f / even["n"]
    d_f = max(-1.5, min(1.5, d_f))
    return {"offset_ms": round(d_ms, 3), "offset_f16": round(d_f, 5), "ratio": round((2 + d_f) / (2 - d_f), 4), "n_odd": odd["n"], "n_even": even["n"]}


def quantiles(values: list, qs=(0.0, 0.25, 0.5, 0.75, 1.0)) -> dict:
    v = sorted(values)
    out = {}
    for q in qs:
        if not v:
            out[str(q)] = None
            continue
        pos = q * (len(v) - 1)
        lo, hi = int(math.floor(pos)), int(math.ceil(pos))
        out[str(q)] = round(v[lo] + (v[hi] - v[lo]) * (pos - lo), 5)
    return out


def hist_quantile(hist: list, lo: float, hi: float, q: float):
    tot = sum(hist)
    if tot <= 0:
        return None
    acc, target, w = 0.0, q * tot, (hi - lo) / len(hist)
    for i, c in enumerate(hist):
        if acc + c >= target:
            frac = (target - acc) / c if c else 0.0
            return lo + (i + frac) * w
        acc += c
    return hi


def stream_summary(st: dict, pooled_db_center: bool = True) -> dict:
    """Generation-time view of a (merged) stream: means/stds per slot, swing, swing-removed residual means, velocity tables."""
    mean_ms = [cell_mean(c) for c in st["ms"]]
    std_ms = [cell_std(c) for c in st["ms"]]
    mean_f = [cell_mean(c) for c in st["f16"]]
    std_f = [cell_std(c) for c in st["f16"]]
    sw = swing_of(st["ms"], st["f16"])
    d_ms, d_f = sw["offset_ms"] or 0.0, sw["offset_f16"] or 0.0
    resid_ms = [None if m is None else round(m - (d_ms if i in ODD_8TH else 0.0), 3) for i, m in enumerate(mean_ms)]
    resid_f = [None if m is None else round(m - (d_f if i in ODD_8TH else 0.0), 5) for i, m in enumerate(mean_f)]
    vel = [cell_mean(c) for c in st["db"]]
    vel_n = sum(c["n"] for c in st["db"])
    vel_mean = (sum(c["s"] for c in st["db"]) / vel_n) if vel_n else 0.0
    center = (lambda x: None if x is None else round(x - vel_mean, 3)) if pooled_db_center else (lambda x: None if x is None else round(x, 3))
    return {"slot_mean_ms": [None if m is None else round(m, 3) for m in mean_ms], "slot_std_ms": [None if s is None else round(s, 3) for s in std_ms],
            "slot_mean_f16": [None if m is None else round(m, 5) for m in mean_f], "slot_std_f16": [None if s is None else round(s, 5) for s in std_f],
            "slot_n": [c["n"] for c in st["ms"]], "slot_resid_mean_ms": resid_ms, "slot_resid_mean_f16": resid_f, "swing": sw,
            "vel_by_slot_db": [center(v) for v in vel], "vel_by_bar_mod4_db": [center(cell_mean(c)) for c in st["bar_mod4_db"]],
            "vel_by_bar_mod8_db": [center(cell_mean(c)) for c in st["bar_mod8_db"]],
            "vel_by_beat_class_db": {k: center(cell_mean(st["beat_class_db"][k])) for k in BEAT_CLASSES},
            "hist_f16": list(st["hist_f16"]), "n_detected": st["n_detected"], "n_assigned": st["n_assigned"], "n_rejected": st["n_rejected"],
            "n_out_of_grid": st["n_out_of_grid"], "n_duplicate": st.get("n_duplicate", 0), "reject_rate": round(st["n_rejected"] / st["n_detected"], 4) if st["n_detected"] else None}


def pool(entries: dict, variant: str, target_bpm=None) -> dict:
    """entries = {sha16: per_song entry}. Returns the generation-time model for that subset."""
    shas = sorted(entries)
    streams = {s: empty_stream() for s in STREAMS}
    lag = {"n": 0, "s": 0.0, "ss": 0.0}
    dur_hist = [0] * DUR_BINS
    dur_cls = {"on_beat": {"n": 0, "s": 0.0, "ss": 0.0}, "syncopated": {"n": 0, "s": 0.0, "ss": 0.0}}
    fill = {"mod4": {"boundary_onsets": 0, "boundary_bars": 0, "other_onsets": 0, "other_bars": 0}, "mod8": {"boundary_onsets": 0, "boundary_bars": 0, "other_onsets": 0, "other_bars": 0}}
    swing_vals, swing_hat, confs = [], [], {}
    for sha in shas:
        e = entries[sha]
        for s in STREAMS:
            streams[s] = merge_stream(streams[s], e["streams"][s])
        for k in ("n", "s", "ss"):
            lag[k] += e["bass_kick_lag"][k]
        dur_hist = [x + y for x, y in zip(dur_hist, e["bass_duration"]["hist"])]
        for c in dur_cls:
            for k in ("n", "s", "ss"):
                dur_cls[c][k] += e["bass_duration"]["by_class"][c][k]
        for m in ("mod4", "mod8"):
            for k in fill[m]:
                fill[m][k] += e["fill_density"][m][k]
        if e["swing"]["drums"]["ratio"] is not None:
            swing_vals.append(e["swing"]["drums"]["ratio"])
        if e["swing"]["hat"]["ratio"] is not None:
            swing_hat.append(e["swing"]["hat"]["ratio"])
        confs[e["grid"]["confidence"]] = confs.get(e["grid"]["confidence"], 0) + 1
    out = {"variant": variant, "target_bpm": target_bpm, "songs": shas, "n_songs": len(shas), "grid_confidence_tally": confs,
           "streams": {s: stream_summary(streams[s]) for s in STREAMS},
           "swing_ratios_drums": dict(quantiles(swing_vals), values=[round(v, 4) for v in sorted(swing_vals)], n=len(swing_vals),
                                     iqr=(round(quantiles(swing_vals)["0.75"] - quantiles(swing_vals)["0.25"], 4) if swing_vals else None)),
           "swing_ratios_hat": dict(quantiles(swing_hat), n=len(swing_hat)),
           "bass_kick_lag_ms": {"n": lag["n"], "mean": round(cell_mean(lag), 3) if lag["n"] else None, "std": round(cell_std(lag), 3) if lag["n"] > 1 else None},
           "bass_duration": {"hist": dur_hist, "n": sum(dur_hist), "mean_frac": round(sum((i + 0.5) / DUR_BINS * c for i, c in enumerate(dur_hist)) / sum(dur_hist), 4) if sum(dur_hist) else None,
                             "quantiles": {q: (None if hist_quantile(dur_hist, 0.0, 1.0, float(q)) is None else round(hist_quantile(dur_hist, 0.0, 1.0, float(q)), 4)) for q in ("0.1", "0.25", "0.5", "0.75", "0.9")},
                             "by_class": {c: {"n": v["n"], "mean": round(cell_mean(v), 4) if v["n"] else None} for c, v in dur_cls.items()}},
           "fill_density": {m: dict(v, ratio=(round((v["boundary_onsets"] / v["boundary_bars"]) / max(1e-9, v["other_onsets"] / v["other_bars"]), 4)
                                               if v["boundary_bars"] and v["other_bars"] and v["other_onsets"] else None)) for m, v in fill.items()}}
    return out


def near_tempo_entries(per_song: dict, bpm: float, frac: float = NEAR_TEMPO_FRAC) -> dict:
    return {sha: e for sha, e in per_song.items() if abs(e["grid"]["bpm"] - bpm) <= frac * bpm}


def model_for_bpm(mt: dict, bpm: float, min_songs: int = 3) -> dict:
    """near_tempo pool for `bpm` (songs within +/-15 %) when it has >= min_songs songs, else the pooled-all model."""
    sub = near_tempo_entries(mt["per_song"], bpm)
    if len(sub) >= min_songs:
        return pool(sub, "near_tempo", round(float(bpm), 3))
    return dict(mt["pooled"]["all"], variant="all_(near_tempo_too_small)", target_bpm=round(float(bpm), 3))


def gaussian_hist(mean_f16: float, std_f16: float, n: int = 1000) -> list:
    """Discretised normal over HIST_EDGES (the PRIOR's deviation distribution)."""
    out = []
    for i in range(41):
        lo, hi = HIST_EDGES[i], HIST_EDGES[i + 1]
        p = 0.5 * (math.erf((hi - mean_f16) / (std_f16 * math.sqrt(2))) - math.erf((lo - mean_f16) / (std_f16 * math.sqrt(2))))
        out.append(int(round(p * n)))
    return out


def swing_ms_from_ratio(ratio: float, s16_ms: float) -> float:
    """Swing ratio r (odd 8th late) -> odd-8th offset in ms at this tempo: d_f16 = 2 (r - 1) / (r + 1) (= humanize.swing_ms_of)."""
    return 2.0 * (float(ratio) - 1.0) / (float(ratio) + 1.0) * s16_ms


def _prior_stream(mean_ms: float, std_ms: float, swing_ms: float, vel_slot: list, bpm: float = 110.0, std_scale: float = 1.0) -> dict:
    """hist_f16 = 0.65 N(mean, std_scale x std) + 0.35 N(mean + swing, std_scale x std): the odd-8th slots carry ~1/3 of the onsets of an
    8th-note pattern. std_scale = the factor the humanizer applies to slot_std_ms (humanize.STD_SCALE), so in prior mode the reference
    histogram IS the distribution the humanizer draws from (validators.timing_ks holds by construction up to the song's odd/even slot mix)."""
    s16_ms = 60000.0 / bpm / 4
    sd = max(1e-6, std_ms * std_scale) / s16_ms
    hist = [int(round(0.65 * a + 0.35 * b)) for a, b in zip(gaussian_hist(mean_ms / s16_ms, sd), gaussian_hist((mean_ms + swing_ms) / s16_ms, sd))]
    return {"slot_mean_ms": [round(mean_ms + (swing_ms if i in ODD_8TH else 0.0), 3) for i in range(16)], "slot_std_ms": [std_ms] * 16,
            "slot_mean_f16": [round((mean_ms + (swing_ms if i in ODD_8TH else 0.0)) / s16_ms, 5) for i in range(16)], "slot_std_f16": [round(std_ms / s16_ms, 5)] * 16,
            "slot_n": [0] * 16, "slot_resid_mean_ms": [mean_ms] * 16, "slot_resid_mean_f16": [round(mean_ms / s16_ms, 5)] * 16,
            "swing": {"offset_ms": swing_ms, "offset_f16": round(swing_ms / s16_ms, 5), "ratio": round((2 + swing_ms / s16_ms) / (2 - swing_ms / s16_ms), 4), "n_odd": 0, "n_even": 0},
            "vel_by_slot_db": vel_slot, "vel_by_bar_mod4_db": [0.3, -0.2, 0.0, 0.6], "vel_by_bar_mod8_db": [0.5, -0.3, 0.0, 0.4, 0.2, -0.3, 0.1, 1.0],
            "vel_by_beat_class_db": {"downbeat": 1.5, "backbeat": 1.0, "beat3": 0.3, "offbeat": -2.5},
            "hist_f16": hist, "n_detected": 0, "n_assigned": 0, "n_rejected": 0, "n_out_of_grid": 0, "reject_rate": None}


PRIOR_SWING_RATIOS = {"0.0": 1.0, "0.25": 1.03, "0.5": 1.08, "0.75": 1.15, "1.0": 1.3}


def prior_model(bpm: float = 110.0, std_scale: float = 1.0) -> dict:
    """Fixture-mode fallback (no corpus stems): modest, lightly swung pop/soul feel at `bpm`; documented as 'prior' in every manifest.
    Every stream's swing is the prior's median drums swing ratio (PRIOR_SWING_RATIOS["0.5"]) converted to ms at `bpm` — exactly the
    offset humanize.swing_ms_of applies — so the per-stream deviation histograms match the generated offsets; std_scale: see _prior_stream."""
    swing = swing_ms_from_ratio(PRIOR_SWING_RATIOS["0.5"], 60000.0 / bpm / 4)
    hat_vel = [2.0, -3.0, -1.0, -3.5, 1.0, -3.0, -1.0, -3.5, 1.5, -3.0, -1.0, -3.5, 1.0, -3.0, -1.0, -3.0]
    kick_vel = [2.0, -2.0, -1.0, -2.0, 0.0, -2.0, -1.0, -2.0, 1.0, -2.0, -1.0, -2.0, 0.0, -2.0, -0.5, -2.0]
    snare_vel = [0.0, -6.0, -4.0, -6.0, 2.0, -6.0, -4.0, -6.0, 0.0, -6.0, -4.0, -6.0, 2.0, -6.0, -3.0, -6.0]
    bass_vel = [1.5, -2.0, -1.0, -2.0, 0.5, -2.0, -0.5, -2.0, 1.0, -2.0, -1.0, -2.0, 0.5, -2.0, -0.5, -2.0]
    streams = {"kick": _prior_stream(0.0, 6.0, swing, kick_vel, bpm, std_scale), "snare": _prior_stream(2.0, 8.0, swing, snare_vel, bpm, std_scale),
               "hat": _prior_stream(-1.0, 7.0, swing, hat_vel, bpm, std_scale), "bass": _prior_stream(6.0, 10.0, swing, bass_vel, bpm, std_scale)}
    dur_hist = [0, 0, 0, 0, 0, 0, 1, 2, 3, 5, 8, 10, 12, 14, 14, 12, 9, 6, 3, 1]
    return {"variant": "prior", "target_bpm": round(float(bpm), 3), "songs": [], "n_songs": 0, "grid_confidence_tally": {}, "streams": streams,
            "swing_ratios_drums": dict(PRIOR_SWING_RATIOS, values=[], n=0, iqr=0.12), "swing_ratios_hat": dict(PRIOR_SWING_RATIOS, n=0),
            "bass_kick_lag_ms": {"n": 0, "mean": 6.0, "std": 8.0},
            "bass_duration": {"hist": dur_hist, "n": sum(dur_hist), "mean_frac": 0.7, "quantiles": {"0.1": 0.5, "0.25": 0.6, "0.5": 0.7, "0.75": 0.78, "0.9": 0.85},
                              "by_class": {"on_beat": {"n": 0, "mean": 0.75}, "syncopated": {"n": 0, "mean": 0.55}}},
            "fill_density": {"mod4": {"boundary_onsets": 0, "boundary_bars": 0, "other_onsets": 0, "other_bars": 0, "ratio": 1.3},
                             "mod8": {"boundary_onsets": 0, "boundary_bars": 0, "other_onsets": 0, "other_bars": 0, "ratio": 1.5}}}


def hist_cdf(hist: list) -> list:
    tot = float(sum(hist)) or 1.0
    acc, out = 0.0, [0.0]
    for c in hist:
        acc += c
        out.append(acc / tot)
    return out


def ks_vs_hist(sample_f16: list, hist: list) -> dict:
    """Two-sample KS statistic between a sample of deviations (f16) and a 41-bin reference histogram, evaluated at the bin edges."""
    if not sample_f16 or sum(hist) <= 0:
        return {"D": None, "n": len(sample_f16)}
    ref = hist_cdf(hist)
    s = sorted(sample_f16)
    n = len(s)
    D, j = 0.0, 0
    for i, edge in enumerate(HIST_EDGES):
        while j < n and s[j] <= edge:
            j += 1
        D = max(D, abs(j / n - ref[i]))
    return {"D": round(D, 4), "n": n}
