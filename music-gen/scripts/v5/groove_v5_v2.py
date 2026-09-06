#!/usr/bin/python3
"""c82 P4 — joint groove conditional model v2: bar-phase alignment, 8th-note kick alphabet, additive smoothing,
HELD-OUT evaluation (pre-declared). Sibling of the c81 groove_v5.py (READ-ONLY, untouched).

created: 2026-09-06T18:00:00Z
cycle: 82
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-RULES-1/groove_v5-v2-heldout-c82

Inputs (READ-ONLY): canonical_v5_reindexed/{drums,bass}.mid of unblocked landed songs (PPQ 480, tempo = bpm_v5).
Grid: 16th = 120 ticks; slot = round(tick/120); bar = slot//16; pos = slot%16 (4/4 as serialized).
Drum classes (GM): kick {35,36}, snare {37..40}, hat {42,44,46} (c81).

Bar-phase alignment (pre-declared): per song choose the 16th-grid offset o in 0..15 that maximizes
  mass(o) = #kick onsets with (pos - o) % 16 == 0 + #snare onsets with (pos - o) % 16 in {4, 12};
ties -> lowest SHA-256 of f"{sha16}|phase|{o}". Every drum + bass slot is shifted by -o before barring.
Pattern alphabet: kick = 8-bit 8th-note mask (bit j set iff any kick onset at 16th pos 2j or 2j+1);
snare / hat / bass = 16-bit masks (c81). Corpus bars = bars with >= 1 drum onset (c81).
Model: P(kick8), P(snare16 | kick8), P(hat16 | kick8, snare16), P(bass16 | kick8) as counts + additive smoothing
alpha = 0.5 over each table's OUTCOME VOCABULARY (the outcomes observed for that table in training); an unseen
context therefore samples uniformly over the vocabulary.
Sampling 64 bars: SHA-256 inverse-CDF (u = int(sha256(f"groove_v5_v2|{i}|{stage}|{context}")[:16],16)/2**64), no PRNG.
Statistics (aligned grid): backbeat ratio = snare onsets at pos {4,12} / all snare onsets; bass-kick lock = fraction
of bass onsets with a kick within one 16th (kick8 bit j covers 16th positions 2j, 2j+1; |bass_pos - kick_pos| <= 1).
Pre-declared held-out verdict (train WIG + CG, evaluate ROME held out):
  GROOVE_V2_GENERALIZES iff |backbeat(Rome corpus) - backbeat(64 sampled)| <= 0.15 AND |lock(Rome) - lock(sampled)| <= 0.15
                       AND singleton-context fraction < 0.5 (fraction of (table, context) training entries with count == 1
                       over the three conditional tables);
  GROOVE_V2_DEGENERATE iff < 3 distinct kick8 or < 3 distinct bass16 patterns in the 64 sampled bars;
  GROOVE_V2_OVERFITS otherwise.
Also reports the c81 in-sample (WIG + CG) statistics under the new alignment for comparison.
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs; READ-ONLY inputs; c81 untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

import mido  # noqa: E402

_WS = Path(__file__).resolve().parent.parent.parent
ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
PPQ = 480
TICKS_16TH = PPQ // 4
SLOTS = 16
CLASSES = {"kick": (35, 36), "snare": (37, 38, 39, 40), "hat": (42, 44, 46)}
BACKBEAT_POS = (4, 12)
N_SAMPLE = 64
TOL = 0.15
ALPHA = 0.5
MIN_DISTINCT = 3
SINGLETON_MAX = 0.5
TRAIN_DEFAULT = ("252eb21ce7df7328", "31a164f845f8e27e")
HELDOUT_DEFAULT = "51e433ade2a845e1"
ENUM = ("GROOVE_V2_GENERALIZES", "GROOVE_V2_OVERFITS", "GROOVE_V2_DEGENERATE")


def sha_str(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def onsets_slots(path: Path) -> list[tuple[int, int]]:
    """(slot, pitch) note_on onsets on the 16th grid."""
    m = mido.MidiFile(str(path))
    assert m.ticks_per_beat == PPQ, f"{path}: PPQ {m.ticks_per_beat}"
    out = []
    for tr in m.tracks:
        t = 0
        for msg in tr:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                out.append((int(round(t / TICKS_16TH)), msg.note))
    out.sort()
    return out


def cls_of(p: int) -> str | None:
    return next((c for c, ps in CLASSES.items() if p in ps), None)


def phase_offset(sha16: str, drums: list[tuple[int, int]]) -> dict:
    mass = {}
    for o in range(SLOTS):
        m = 0
        for slot, p in drums:
            c = cls_of(p)
            pos = (slot - o) % SLOTS
            if c == "kick" and pos == 0:
                m += 1
            elif c == "snare" and pos in BACKBEAT_POS:
                m += 1
        mass[o] = m
    best = min(range(SLOTS), key=lambda o: (-mass[o], sha_str(f"{sha16}|phase|{o}")))
    return {"offset": best, "mass": mass, "tie": sum(1 for o in mass if mass[o] == mass[best]) > 1}


def bar_patterns(drums: list[tuple[int, int]], bass: list[tuple[int, int]], offset: int) -> list[dict]:
    bars: dict[int, dict] = {}
    for slot, p in drums:
        c = cls_of(p)
        if c is None:
            continue
        s = slot - offset
        if s < 0:
            continue
        b = bars.setdefault(s // SLOTS, {"kick": 0, "snare": 0, "hat": 0, "bass": 0})
        pos = s % SLOTS
        if c == "kick":
            b["kick"] |= 1 << (pos // 2)  # 8th-note alphabet
        else:
            b[c] |= 1 << pos
    for slot, _p in bass:
        s = slot - offset
        if s >= 0 and s // SLOTS in bars:
            bars[s // SLOTS]["bass"] |= 1 << (s % SLOTS)
    return [dict(bar=i, **bars[i]) for i in sorted(bars) if (bars[i]["kick"] | bars[i]["snare"] | bars[i]["hat"])]


def bits(x: int, n: int = SLOTS) -> list[int]:
    return [i for i in range(n) if x >> i & 1]


def stats(bars: list[dict]) -> dict:
    snare_total = sum(len(bits(b["snare"])) for b in bars)
    snare_bb = sum(1 for b in bars for pos in bits(b["snare"]) if pos in BACKBEAT_POS)
    bass_total = sum(len(bits(b["bass"])) for b in bars)
    locked = 0
    for b in bars:
        kick16 = {2 * j for j in bits(b["kick"], 8)} | {2 * j + 1 for j in bits(b["kick"], 8)}
        for pos in bits(b["bass"]):
            if any(abs(pos - k) <= 1 for k in kick16):
                locked += 1
    return {"n_bars": len(bars), "snare_onsets": snare_total, "snare_on_backbeat": snare_bb,
            "backbeat_ratio": round(snare_bb / snare_total, 6) if snare_total else None,
            "bass_onsets": bass_total, "bass_locked_to_kick": locked,
            "bass_kick_lock": round(locked / bass_total, 6) if bass_total else None,
            "distinct_kick_patterns": len({b["kick"] for b in bars}), "distinct_bass_patterns": len({b["bass"] for b in bars})}


def table(pairs: list[tuple[str, int]]) -> dict:
    counts: dict[str, dict[str, int]] = {}
    for ctx, out in pairs:
        counts.setdefault(ctx, {})
        counts[ctx][str(out)] = counts[ctx].get(str(out), 0) + 1
    vocab = sorted({o for row in counts.values() for o in row}, key=int)
    probs = {}
    for ctx, row in counts.items():
        n = sum(row.values())
        probs[ctx] = {o: (row.get(o, 0) + ALPHA) / (n + ALPHA * len(vocab)) for o in vocab}
    n_ctx_total = sum(sum(r.values()) for r in counts.values())
    return {"counts": {k: dict(sorted(v.items())) for k, v in sorted(counts.items())}, "probs": {k: probs[k] for k in sorted(probs)},
            "vocab": vocab, "alpha": ALPHA, "n_contexts": len(counts), "n_singleton_contexts": sum(1 for r in counts.values() if sum(r.values()) == 1),
            "n_pairs": n_ctx_total}


def row_for(tbl: dict, ctx: str) -> dict[str, float]:
    if ctx in tbl["probs"]:
        return tbl["probs"][ctx]
    v = tbl["vocab"]
    return {o: 1.0 / len(v) for o in v}  # unseen context: uniform over the outcome vocabulary (alpha-smoothing limit)


def hash_uniform(tag: str) -> float:
    return int(hashlib.sha256(tag.encode()).hexdigest()[:16], 16) / float(1 << 64)


def draw(row: dict[str, float], u: float) -> int:
    acc = 0.0
    keys = sorted(row, key=int)
    for k in keys:
        acc += row[k]
        if u < acc:
            return int(k)
    return int(keys[-1])


def sample(model: dict, n: int) -> list[dict]:
    out = []
    for i in range(n):
        k = draw(row_for(model["kick_marginal"], "*"), hash_uniform(f"groove_v5_v2|{i}|kick|*"))
        s = draw(row_for(model["snare_given_kick"], str(k)), hash_uniform(f"groove_v5_v2|{i}|snare|{k}"))
        h = draw(row_for(model["hat_given_kick_snare"], f"{k}|{s}"), hash_uniform(f"groove_v5_v2|{i}|hat|{k}|{s}"))
        b = draw(row_for(model["bass_given_kick"], str(k)), hash_uniform(f"groove_v5_v2|{i}|bass|{k}"))
        out.append({"bar": i, "kick": k, "snare": s, "hat": h, "bass": b})
    return out


def load_song(corpus: Path, s: str) -> dict:
    d = corpus / s / "canonical_v5_reindexed"
    if not (d / "reindex_manifest.json").exists():
        raise SystemExit(f"MISSING_REINDEX: {s}")
    tm = json.loads((corpus / s / "transcription_manifest.json").read_text())
    drums = onsets_slots(d / "drums.mid")
    bass = onsets_slots(d / "bass.mid")
    ph = phase_offset(s, drums)
    bars = bar_patterns(drums, bass, ph["offset"])
    bars_unaligned = bar_patterns(drums, bass, 0)
    return {"title": tm.get("title"), "bpm_v5": tm["bpm_v5"], "phase": ph, "bars": bars,
            "stats": stats(bars), "stats_unaligned_offset0": stats(bars_unaligned)}


def main() -> int:
    ap = argparse.ArgumentParser(description="v5 joint groove model v2 (phase-aligned, 8th-note kick, smoothed, held-out)")
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--train", nargs="*", default=list(TRAIN_DEFAULT))
    ap.add_argument("--heldout", default=HELDOUT_DEFAULT)
    ap.add_argument("--out", default="data/v5/rules/groove_v5_v2.json")
    args = ap.parse_args()
    os.chdir(_WS)
    corpus = Path(args.corpus_dir)
    blocked = set(json.loads((corpus / "recanonicalization_blocked.json").read_text())["blocked_songs"])
    refused = [s for s in list(args.train) + [args.heldout] if s in blocked]
    if refused:
        raise SystemExit(f"REFUSED: blocked songs must not be consumed: {refused}")
    songs = {s: load_song(corpus, s) for s in list(args.train) + [args.heldout]}
    train_bars = [b for s in args.train for b in songs[s]["bars"]]
    model = {
        "kick_marginal": table([("*", b["kick"]) for b in train_bars]),
        "snare_given_kick": table([(str(b["kick"]), b["snare"]) for b in train_bars]),
        "hat_given_kick_snare": table([(f"{b['kick']}|{b['snare']}", b["hat"]) for b in train_bars]),
        "bass_given_kick": table([(str(b["kick"]), b["bass"]) for b in train_bars]),
    }
    cond = ("snare_given_kick", "hat_given_kick_snare", "bass_given_kick")
    n_ctx = sum(model[t]["n_contexts"] for t in cond)
    n_single = sum(model[t]["n_singleton_contexts"] for t in cond)
    singleton_fraction = round(n_single / n_ctx, 6) if n_ctx else None
    sampled = sample(model, N_SAMPLE)
    sample_stats = stats(sampled)
    train_stats = stats(train_bars)
    held = songs[args.heldout]["stats"]
    checks = {}
    for k in ("backbeat_ratio", "bass_kick_lock"):
        c, m = held[k], sample_stats[k]
        checks[k] = {"heldout_corpus": c, "sampled": m, "abs_diff": round(abs(c - m), 6) if (c is not None and m is not None) else None,
                     "within_tol": (abs(c - m) <= TOL) if (c is not None and m is not None) else False, "tol": TOL}
    degenerate = sample_stats["distinct_kick_patterns"] < MIN_DISTINCT or sample_stats["distinct_bass_patterns"] < MIN_DISTINCT
    if degenerate:
        verdict = "GROOVE_V2_DEGENERATE"
    elif all(v["within_tol"] for v in checks.values()) and singleton_fraction is not None and singleton_fraction < SINGLETON_MAX:
        verdict = "GROOVE_V2_GENERALIZES"
    else:
        verdict = "GROOVE_V2_OVERFITS"
    out = {"schema_version": 1, "cycle": 82, "agent": "worker", "env_pin_sha256": ENV_PIN_SHA256,
           "train_songs": list(args.train), "heldout_song": args.heldout, "blocked_refused": sorted(blocked),
           "grid": {"ppq": PPQ, "ticks_per_16th": TICKS_16TH, "slots_per_bar": SLOTS, "classes": {k: list(v) for k, v in CLASSES.items()},
                    "kick_alphabet": "8-bit 8th-note mask", "other_alphabets": "16-bit 16th-note masks", "corpus_bars": "bars with >= 1 kick/snare/hat onset"},
           "pre_declared": {"phase_alignment": "argmax over o in 0..15 of kick@pos0 + snare@{4,12} after shift -o; SHA-256 tiebreak",
                            "smoothing_alpha": ALPHA, "stat_tolerance": TOL, "singleton_context_fraction_max": SINGLETON_MAX,
                            "degeneracy_min_distinct": MIN_DISTINCT, "n_sample_bars": N_SAMPLE, "sampling": "SHA-256 inverse-CDF (no PRNG)", "enum": list(ENUM)},
           "per_song": {s: {k: v for k, v in r.items() if k != "bars"} for s, r in songs.items()},
           "train_stats_aligned": train_stats, "c81_in_sample_comparison": {
               "note": "c81 groove_v5.json (offset 0, 16-bit kick, no smoothing) corpus backbeat 0.1404 / lock 0.6033 on WIG+CG; below: the same two songs under c82 alignment",
               "aligned": train_stats, "unaligned_offset0_per_song": {s: songs[s]["stats_unaligned_offset0"] for s in args.train}},
           "model": model, "table_context_counts": {t: model[t]["n_contexts"] for t in cond},
           "singleton_context_fraction": singleton_fraction, "n_singleton_contexts": n_single, "n_contexts": n_ctx,
           "sampled_bars": sampled, "sample_stats": sample_stats, "heldout_stats": held, "validation": checks,
           "degenerate": degenerate, "verdict": verdict,
           "note": "data-existence only; NOT fed to any generator this cycle; c81 groove_v5.py untouched"}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(f"VERDICT {verdict}; heldout {args.heldout} {held}; sampled {sample_stats}; singleton_fraction {singleton_fraction}; contexts {out['table_context_counts']}")
    for s, r in songs.items():
        print(f"  {s} {str(r['title'])[:24]:24s} phase={r['phase']['offset']} (tie={r['phase']['tie']}) bars={r['stats']['n_bars']} "
              f"backbeat={r['stats']['backbeat_ratio']} (offset0 {r['stats_unaligned_offset0']['backbeat_ratio']}) lock={r['stats']['bass_kick_lock']}")
    for k, v in checks.items():
        print(f"  {k}: heldout={v['heldout_corpus']} sampled={v['sampled']} diff={v['abs_diff']} ok={v['within_tol']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
