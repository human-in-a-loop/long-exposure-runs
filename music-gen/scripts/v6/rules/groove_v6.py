#!/usr/bin/python3
"""v6 rules — groove_v6: the joint groove conditional model (groove_v5_v2_full schema) trained on the 29-song stem corpus.

created: 2026-10-04
milestone: M-V6-RULES-1/audio-derived-groove-bass-melody

  /usr/bin/python3 scripts/v6/rules/groove_v6.py [--songs sha16,...] [--workers 2] [--out-v5 data/v5/rules/groove_v5_v2_full.json]
      [--out-v6 data/v6/rules/groove_v6.json] [--variants-out data/v6/rules/groove_v6_variants.json]

Per song the per-onset streams of scripts/v6/rules/stems_common_v6.py (= the microtiming_v6 grid: forced-bpm smoothed beats,
downbeat phase, hypermeter offset, one onset per (bar, slot)) become per-bar bitmasks exactly as scripts/v5/groove_v5_v2.py
bar_patterns does: kick = 8-bit 8th-note mask (bit j iff a kick at 16th 2j or 2j+1), snare / hat / bass = 16-bit masks; corpus
bars = bars with >= 1 kick/snare/hat onset. The downbeat alignment is the microtiming grid's (no separate 16-offset search;
the v5 argmax rule is evaluated on the aligned bars and its agreement recorded). Model: P(kick8), P(snare16 | kick8),
P(hat16 | kick8, snare16), P(bass16 | kick8) via groove_v5_v2.table (alpha 0.5 over the outcome vocabulary); held-out fold =
the 3 songs with the lowest SHA-256 of f"groove_fold_v6|{sha16}" (as groove_v5_full_c84 does with its tag); same 64-bar
SHA-256 sample, statistics, tolerance checks and verdict enum as c84 (the run asserts NOT GROOVE_V2_DEGENERATE). Held-out
log-likelihood per bar (joint vs an independent-marginals baseline; outcomes outside a table's vocabulary take the alpha floor).
Side file: per-band and near-tempo (+/-15 % of 100/120/152 bpm) variant models as counts-only tables. No PRNG.
Size: the composer file is dominated by the DENSE smoothed `probs` rows the v5 schema prescribes and scripts/v6/gen/drums.row_for
reads directly (hat_given_kick_snare: ~2.3 k contexts x ~1.2 k vocabulary outcomes); per-song blocks are ~20 KB. Probabilities
are written rounded to PROB_DECIMALS decimals (bass_pitch_v5's precision); the variants side file carries no probs at all.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.rules import stems_common_v6 as SC  # noqa: E402  (pins + guard at import)
from scripts.v6.v6_data_common import ENV_PIN_SHA256, WS, read_json, sha256_file, write_json_atomic  # noqa: E402
from scripts.v5 import groove_v5_v2 as G  # noqa: E402  READ-ONLY (table / row_for / sample / stats / phase_offset)

FOLD_TAG = "groove_fold_v6"
N_HELDOUT = 3
TOP_N = 10
GM = {"kick": 36, "snare": 38, "hat": 42}
OUT_V5 = WS / "data/v5/rules/groove_v5_v2_full.json"
OUT_V6 = WS / "data/v6/rules/groove_v6.json"
OUT_VARIANTS = WS / "data/v6/rules/groove_v6_variants.json"
PREREG_C84 = WS / "data/v5/rules/groove_prereg_c84.json"
COND = ("snare_given_kick", "hat_given_kick_snare", "bass_given_kick")
PROB_DECIMALS = 9


# ------------------------------------------------------------------------------------------------------ bitmasks ----
def bars_from_streams(streams: dict) -> list[dict]:
    """[{bar, kick(8-bit), snare, hat, bass}] from {stream: [[bar, slot16, ...], ...]} — groove_v5_v2.bar_patterns semantics."""
    bars: dict[int, dict] = {}
    for k in ("kick", "snare", "hat"):
        for row in streams.get(k, []):
            bar, slot = int(row[0]), int(row[1]) % 16
            b = bars.setdefault(bar, {"kick": 0, "snare": 0, "hat": 0, "bass": 0})
            if k == "kick":
                b["kick"] |= 1 << (slot // 2)
            else:
                b[k] |= 1 << slot
    for row in streams.get("bass", []):
        bar, slot = int(row[0]), int(row[1]) % 16
        if bar in bars:
            bars[bar]["bass"] |= 1 << slot
    return [dict(bar=i, **bars[i]) for i in sorted(bars) if (bars[i]["kick"] | bars[i]["snare"] | bars[i]["hat"])]


def pattern_str(mask: int, n: int) -> str:
    return "".join("x" if (int(mask) >> i) & 1 else "." for i in range(n))


def v5_phase_agreement(sha16: str, streams: dict) -> dict:
    """Evaluate groove_v5_v2.phase_offset's argmax rule on the already-aligned grid: agreement <=> offset 0."""
    bars = [r[0] for k in ("kick", "snare", "hat") for r in streams.get(k, [])]
    base = -min(bars) if bars else 0
    drums = [((r[0] + base) * 16 + r[1], GM[k]) for k in ("kick", "snare", "hat") for r in streams.get(k, [])]
    ph = G.phase_offset(sha16, sorted(drums))
    return {"v5_rule_offset_on_aligned_grid": ph["offset"], "agrees": ph["offset"] == 0, "tie": ph["tie"],
            "mass_at_0": ph["mass"].get(0), "mass_at_best": ph["mass"][ph["offset"]]}


def inventory(bars: list[dict], top_n: int = TOP_N) -> dict:
    n = len(bars)
    out = {}
    for k, w in (("kick", 8), ("snare", 16), ("hat", 16), ("bass", 16)):
        cnt: dict[int, int] = {}
        for b in bars:
            cnt[b[k]] = cnt.get(b[k], 0) + 1
        top = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]
        out[k] = [{"mask": m, "pattern": pattern_str(m, w), "count": c, "mass": round(c / n, 6) if n else None} for m, c in top]
        out[f"{k}_distinct"] = len(cnt)
    return out


# --------------------------------------------------------------------------------------------------------- model ----
def build_model(bars: list[dict]) -> dict:
    return {"kick_marginal": G.table([("*", b["kick"]) for b in bars]),
            "snare_given_kick": G.table([(str(b["kick"]), b["snare"]) for b in bars]),
            "hat_given_kick_snare": G.table([(f"{b['kick']}|{b['snare']}", b["hat"]) for b in bars]),
            "bass_given_kick": G.table([(str(b["kick"]), b["bass"]) for b in bars])}


def fold(elig: list[str]) -> tuple[list, list, dict]:
    ranked = sorted(elig, key=lambda s: SC.sha_rank(FOLD_TAG, s))
    held = ranked[:N_HELDOUT]
    return [s for s in elig if s not in held], held, {s: SC.sha_rank(FOLD_TAG, s)[:16] for s in ranked}


def _logp(tbl: dict, ctx: str, out: int) -> tuple[float, bool]:
    row = G.row_for(tbl, ctx)
    key = str(out)
    if key in row:
        return math.log(row[key]), False
    n_row = sum(tbl["counts"].get(ctx, {}).values())
    return math.log(tbl["alpha"] / (n_row + tbl["alpha"] * max(1, len(tbl["vocab"])))), True


def loglik(model: dict, bars: list[dict]) -> dict:
    """Per-bar joint log-likelihood under the 4-table model vs an independent-marginals baseline fitted on the same training bars."""
    tot, oov, per_stream = 0.0, 0, {"kick": 0.0, "snare": 0.0, "hat": 0.0, "bass": 0.0}
    for b in bars:
        for name, tbl, ctx in (("kick", "kick_marginal", "*"), ("snare", "snare_given_kick", str(b["kick"])),
                               ("hat", "hat_given_kick_snare", f"{b['kick']}|{b['snare']}"), ("bass", "bass_given_kick", str(b["kick"]))):
            lp, o = _logp(model[tbl], ctx, b[name])
            tot += lp
            per_stream[name] += lp
            oov += int(o)
    n = len(bars)
    return {"n_bars": n, "loglik_total": round(tot, 4), "loglik_per_bar": round(tot / n, 6) if n else None, "n_oov_outcomes": oov,
            "per_stream_per_bar": {k: round(v / n, 6) if n else None for k, v in per_stream.items()}}


def independent_model(bars: list[dict]) -> dict:
    """Baseline with the same table machinery but every stream conditioned on nothing ('*')."""
    return {"kick_marginal": G.table([("*", b["kick"]) for b in bars]), "snare_given_kick": G.table([("*", b["snare"]) for b in bars]),
            "hat_given_kick_snare": G.table([("*", b["hat"]) for b in bars]), "bass_given_kick": G.table([("*", b["bass"]) for b in bars])}


def loglik_independent(indep: dict, bars: list[dict]) -> dict:
    star = [dict(b, kick=b["kick"]) for b in bars]
    tot, n = 0.0, len(bars)
    for b in star:
        for name, tbl in (("kick", "kick_marginal"), ("snare", "snare_given_kick"), ("hat", "hat_given_kick_snare"), ("bass", "bass_given_kick")):
            tot += _logp(indep[tbl], "*", b[name])[0]
    return {"n_bars": n, "loglik_total": round(tot, 4), "loglik_per_bar": round(tot / n, 6) if n else None}


def evaluate(model: dict, held_bars: list[dict], train_bars: list[dict]) -> dict:
    """c84's sample / statistics / tolerance checks / verdict, unchanged."""
    n_ctx = sum(model[t]["n_contexts"] for t in COND)
    n_single = sum(model[t]["n_singleton_contexts"] for t in COND)
    singleton_fraction = round(n_single / n_ctx, 6) if n_ctx else None
    sampled = G.sample(model, G.N_SAMPLE)
    sample_stats, train_stats, held_stats = G.stats(sampled), G.stats(train_bars), G.stats(held_bars)
    checks = {}
    for k in ("backbeat_ratio", "bass_kick_lock"):
        c, m = held_stats[k], sample_stats[k]
        ok = c is not None and m is not None
        checks[k] = {"heldout_pooled": c, "sampled": m, "abs_diff": round(abs(c - m), 6) if ok else None, "within_tol": (abs(c - m) <= G.TOL) if ok else False, "tol": G.TOL}
    degenerate = sample_stats["distinct_kick_patterns"] < G.MIN_DISTINCT or sample_stats["distinct_bass_patterns"] < G.MIN_DISTINCT
    if degenerate:
        verdict = "GROOVE_V2_DEGENERATE"
    elif all(v["within_tol"] for v in checks.values()) and singleton_fraction is not None and singleton_fraction < G.SINGLETON_MAX:
        verdict = "GROOVE_V2_GENERALIZES"
    else:
        verdict = "GROOVE_V2_OVERFITS"
    per_table = {t: {"n_contexts": model[t]["n_contexts"], "n_singleton_contexts": model[t]["n_singleton_contexts"], "n_pairs": model[t]["n_pairs"],
                     "singleton_fraction": round(model[t]["n_singleton_contexts"] / model[t]["n_contexts"], 6) if model[t]["n_contexts"] else None} for t in COND}
    return {"sampled_bars": sampled, "sample_stats": sample_stats, "train_stats": train_stats, "heldout_stats_pooled": held_stats, "validation": checks,
            "degenerate": degenerate, "verdict": verdict, "per_table": per_table, "table_context_counts": {t: model[t]["n_contexts"] for t in COND},
            "singleton_context_fraction": singleton_fraction, "n_singleton_contexts": n_single, "n_contexts": n_ctx}


def backbeat_block(bars: list[dict]) -> dict:
    n = len(bars)
    both = sum(1 for b in bars if (b["snare"] >> 4 & 1) and (b["snare"] >> 12 & 1))
    kick1 = sum(1 for b in bars if b["kick"] & 1)
    snare_off = sum(1 for b in bars for p in G.bits(b["snare"]) if p % 4 != 0)
    snare_tot = sum(len(G.bits(b["snare"])) for b in bars)
    hats = [len(G.bits(b["hat"])) for b in bars]
    return {"n_bars": n, "snare_on_both_backbeats_frac": round(both / n, 6) if n else None, "kick_on_downbeat_frac": round(kick1 / n, 6) if n else None,
            "snare_off_beat_16th_frac": round(snare_off / snare_tot, 6) if snare_tot else None, "hat_onsets_per_bar_mean": round(sum(hats) / n, 4) if n else None,
            "four_on_the_floor_frac": round(sum(1 for b in bars if b["kick"] & 0x55 == 0x55) / n, 6) if n else None, **G.stats(bars)}


# ------------------------------------------------------------------------------------------------------ assembly ----
def song_record(sha16: str, onsets: dict) -> dict:
    bars = bars_from_streams(onsets["streams"])
    g = onsets["grid"]
    return {"title": onsets.get("title"), "band": onsets.get("band"), "bpm_v5": g["bpm"], "bars": bars, "stats": G.stats(bars),
            "phase": {"offset": g["downbeat_phase_offset_16th"], "beat_phase": g["phase"], "hypermeter_offset": g["hypermeter_offset"], "mass": None, "tie": False,
                      "source": "microtiming_v6 grid (scripts/v6/microtiming_v6.py choose_phase / hyper_offset)", **v5_phase_agreement(sha16, onsets["streams"])},
            "grid_confidence": g.get("confidence"), "stats_unaligned_offset0": None, "inventory": inventory(bars)}


def build_outputs(songs: dict[str, dict], prereg: Path | None = None) -> tuple[dict, dict, dict]:
    """(groove_v5_v2_full.json, groove_v6.json, groove_v6_variants.json) from {sha16: song_record}."""
    elig = sorted(songs)
    train, held, ranks = fold(elig)
    train_bars = [b for s in train for b in songs[s]["bars"]]
    held_bars = [b for s in held for b in songs[s]["bars"]]
    model = build_model(train_bars)
    ev = evaluate(model, held_bars, train_bars)
    indep = independent_model(train_bars)
    ll = {"heldout_joint": loglik(model, held_bars), "heldout_independent_baseline": loglik_independent(indep, held_bars),
          "train_joint": loglik(model, train_bars), "train_independent_baseline": loglik_independent(indep, train_bars),
          "oov_rule": "an outcome absent from a table's vocabulary takes alpha / (n_row + alpha * |vocab|); unseen contexts are uniform over the vocabulary (groove_v5_v2.row_for)"}
    ll["heldout_conditional_gain_per_bar"] = round(ll["heldout_joint"]["loglik_per_bar"] - ll["heldout_independent_baseline"]["loglik_per_bar"], 6) if held_bars else None
    per_song_v5 = {s: {k: v for k, v in r.items() if k not in ("bars", "inventory")} | {"n_bars": len(r["bars"]), "role": "heldout" if s in held else "train"} for s, r in songs.items()}
    gate = {"n_corpus": len(elig), "n_landed": len(elig), "n_sidecar": len(elig), "tempo_blocked_skipped": [], "content_blocked_skipped": [], "not_landed": [],
            "n_eligible": len(elig), "eligible": elig, "source": "data/v6/stems/manifest.json (every separated song)"}
    v5 = {"schema_version": 1, "cycle": "v6", "agent": "worker", "run_id": "v6-rules-2026-10-04", "env_pin_sha256": ENV_PIN_SHA256,
          "milestone": "M-V6-RULES-1/audio-derived-groove-bass-melody", "prereg_path": str(prereg.relative_to(WS)) if prereg and prereg.exists() else None,
          "prereg_sha256": sha256_file(prereg) if prereg and prereg.exists() else None,
          "gate": gate, "fold": {"tag": FOLD_TAG, "n_heldout": N_HELDOUT, "rank_hex16": ranks, "train": train, "heldout": held},
          "n_train_songs": len(train), "n_heldout_songs": len(held), "n_train_bars": len(train_bars), "n_heldout_bars": len(held_bars),
          "pre_declared": {"alpha": G.ALPHA, "tol": G.TOL, "singleton_max": G.SINGLETON_MAX, "min_distinct": G.MIN_DISTINCT, "n_sample": G.N_SAMPLE, "enum": list(G.ENUM),
                           "heldout_pooling": "bars of the 3 held-out songs pooled"},
          "per_song": per_song_v5, "model": round_probs(model), "probs_rounded_decimals": PROB_DECIMALS, **ev,
          "growth_reference": {"c81_n2_groove_v5": "data/v5/rules/groove_v5.json", "c82_n2_groove_v5_v2": "data/v5/rules/groove_v5_v2.json", "v6_full": "data/v6/rules/groove_v6.json"},
          "note": "v6: trained from separated stems (data/v6/stems) on the microtiming_v6 grid by scripts/v6/rules/groove_v6.py; schema of groove_v5_full_c84",
          "generator": "scripts/v6/rules/groove_v6.py", "source": "audio stems (no symbolic transcription)", "heldout_loglik": ll}
    all_bars = [b for s in elig for b in songs[s]["bars"]]
    v6 = {"schema_version": 1, "generator": "scripts/v6/rules/groove_v6.py", "milestone": v5["milestone"], "env_pin_sha256": ENV_PIN_SHA256,
          "n_songs": len(elig), "songs": elig, "fold": v5["fold"], "verdict": ev["verdict"], "degenerate": ev["degenerate"], "validation": ev["validation"],
          "singleton_context_fraction": ev["singleton_context_fraction"], "per_table": ev["per_table"], "heldout_loglik": ll,
          "pooled_train": {"inventory": inventory(train_bars), "backbeat": backbeat_block(train_bars)}, "pooled_all": {"inventory": inventory(all_bars), "backbeat": backbeat_block(all_bars)},
          "heldout_pooled": {"inventory": inventory(held_bars), "backbeat": backbeat_block(held_bars)}, "sample_stats": ev["sample_stats"],
          "per_song": {s: {"title": r["title"], "band": r["band"], "bpm": r["bpm_v5"], "role": "heldout" if s in held else "train", "n_bars": len(r["bars"]),
                           "grid_confidence": r["grid_confidence"], "phase": r["phase"], "stats": r["stats"], "inventory": r["inventory"]} for s, r in songs.items()},
          "pattern_notation": "kick: 8 chars = 8th notes of the bar; snare/hat/bass: 16 chars = 16ths; 'x' = onset",
          "v5_file": str(OUT_V5.relative_to(WS)), "variants_file": str(OUT_VARIANTS.relative_to(WS))}
    variants = {"schema_version": 1, "generator": "scripts/v6/rules/groove_v6.py", "env_pin_sha256": ENV_PIN_SHA256, "note": "full-corpus variant models (no held-out fold)",
                "band": {}, "near_tempo": {}}
    for band in sorted({str(r["band"]) for r in songs.values()}):
        sub = [s for s in elig if str(songs[s]["band"]) == band]
        variants["band"][band] = _variant(sub, songs)
    for t in SC.NEAR_TEMPO_TARGETS:
        sub = [s for s in elig if SC.near_tempo(songs[s]["bpm_v5"], t)]
        variants["near_tempo"][str(int(t))] = _variant(sub, songs, t)
    return v5, v6, variants


def _variant(sub: list, songs: dict, target=None) -> dict:
    """Variant model WITHOUT the dense smoothed `probs` rows (counts + vocab + alpha suffice: probs = (count + alpha) / (n + alpha * |vocab|))."""
    bars = [b for s in sub for b in songs[s]["bars"]]
    if not bars:
        return {"songs": sub, "n_songs": len(sub), "n_bars": 0, "model": None, "target_bpm": target}
    m = build_model(bars)
    lean = {t: {k: v for k, v in tbl.items() if k != "probs"} for t, tbl in m.items()}
    return {"songs": sub, "n_songs": len(sub), "n_bars": len(bars), "target_bpm": target, "model": lean, "stats": G.stats(bars), "inventory": inventory(bars),
            "sample_stats": G.stats(G.sample(m, G.N_SAMPLE)), "model_note": "counts-only tables; rebuild probs with scripts/v5/groove_v5_v2.table semantics"}


def round_probs(model: dict, ndigits: int = PROB_DECIMALS) -> dict:
    """The composer copy of the model with every smoothed probability rounded to `ndigits` decimals (same keys / rows / vocab).
    Rows keep >= 5 significant digits for the smallest hat probability (alpha / (n + alpha * |vocab|) >= 1e-4); a row's sum
    deviates from 1 by < |vocab| * 5e-10, which common.draw_row absorbs on the last vocabulary key."""
    out = {}
    for t, tbl in model.items():
        out[t] = dict(tbl, probs={ctx: {o: round(p, ndigits) for o, p in row.items()} for ctx, row in tbl["probs"].items()})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--songs", default=None)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out-v5", default=str(OUT_V5))
    ap.add_argument("--out-v6", default=str(OUT_V6))
    ap.add_argument("--variants-out", default=str(OUT_VARIANTS))
    args = ap.parse_args(argv)
    shas = [s.strip() for s in args.songs.split(",")] if args.songs else SC.corpus_songs()
    missing = [s for s in shas if not (SC.ONSETS_DIR / f"{s}.json").exists()]
    if missing:
        SC.run_parallel(SC.build_onsets, missing, args.workers)
    songs = {s: song_record(s, SC.load_onsets(s, compute=False)) for s in shas}
    v5, v6, variants = build_outputs(songs, PREREG_C84)
    assert v5["verdict"] != "GROOVE_V2_DEGENERATE", f"groove_v6: {v5['verdict']} {v5['sample_stats']}"
    write_json_atomic(args.out_v5, v5)
    write_json_atomic(args.out_v6, v6)
    write_json_atomic(args.variants_out, variants)
    print(f"VERDICT {v5['verdict']}; songs {len(shas)} train {v5['n_train_songs']} heldout {v5['fold']['heldout']}; bars train {v5['n_train_bars']} heldout {v5['n_heldout_bars']}; "
          f"singleton {v5['singleton_context_fraction']}; contexts {v5['table_context_counts']}")
    print(f"  heldout LL/bar joint {v5['heldout_loglik']['heldout_joint']['loglik_per_bar']} vs independent {v5['heldout_loglik']['heldout_independent_baseline']['loglik_per_bar']} "
          f"(gain {v5['heldout_loglik']['heldout_conditional_gain_per_bar']}); oov {v5['heldout_loglik']['heldout_joint']['n_oov_outcomes']}")
    for k, v in v5["validation"].items():
        print(f"  {k}: heldout={v['heldout_pooled']} sampled={v['sampled']} diff={v['abs_diff']} ok={v['within_tol']}")
    for k in ("kick", "snare"):
        print(f"  top {k}: " + ", ".join(f"{e['pattern']} {e['mass']:.3f}" for e in v6["pooled_train"]["inventory"][k][:6]))
    print(f"  backbeat (all): {v6['pooled_all']['backbeat']}")
    agree = sum(1 for r in songs.values() if r["phase"]["agrees"])
    print(f"  v5 phase rule agrees with the microtiming grid on {agree}/{len(songs)} songs; wrote {args.out_v5}, {args.out_v6}, {args.variants_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
