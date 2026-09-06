#!/usr/bin/python3
"""c81 P4 — joint groove conditional model, first data (OPERATOR #3), pre-declared validation.

created: 2026-09-06T17:05:00Z
cycle: 81
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-RULES-1/groove_v5-first-data-c81

Inputs: canonical_v5_reindexed/{drums,bass}.mid (lossless c80 re-index; PPQ 480, tempo = bpm_v5) of the UNBLOCKED
landed songs listed on the command line (default WIG + CG). Songs in recanonicalization_blocked.json are refused.
Grid: 16th = 120 ticks; slot = round(tick / 120); bar = slot // 16; pos = slot % 16 (4/4 assumed, as serialized).
Drum classes (GM, same as the transcription driver): kick {35,36}, snare {37,38,39,40}, hat {42,44,46}.
Corpus bars = bars with >= 1 drum onset of any class (empty bars excluded, pre-declared); the bass onset pattern is
taken for the same bars. Patterns are 16-bit masks (bit = pos).
Model (counts + row-normalized): P(kick), P(snare | kick), P(hat | kick, snare), P(bass | kick).
Sampling 64 bars: per bar i and stage k, u = int(sha256(f"groove_v5|{i}|{stage}|{context}")[:16], 16) / 2**64,
inverse-CDF over keys sorted ascending (no PRNG). Every sampled context is observed by construction.
Pre-declared validation (corpus vs 64 sampled bars):
  backbeat ratio = snare onsets at pos {4, 12} / all snare onsets — reproduced within +/-0.10;
  bass-kick lock = fraction of bass onsets with a kick within one 16th (|dpos| <= 1, same bar) — within +/-0.10.
Pre-declared degeneracy: reject iff sampled distinct kick patterns < 3 OR distinct bass patterns < 3 OR any
conditional table has < 8 observed contexts.
Verdict: GROOVE_NONDEGENERATE_STATS_MATCH | GROOVE_NONDEGENERATE_STATS_MISS | GROOVE_DEGENERATE.
Data-existence only; nothing is fed to a generator this cycle.
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs; READ-ONLY inputs.
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
TOL = 0.10
MIN_CONTEXTS = 8
MIN_DISTINCT = 3
DEFAULT_SONGS = ("252eb21ce7df7328", "31a164f845f8e27e")


def onsets_ticks(path: Path) -> list[tuple[int, int]]:
    m = mido.MidiFile(str(path))
    assert m.ticks_per_beat == PPQ, f"{path}: PPQ {m.ticks_per_beat}"
    out = []
    for tr in m.tracks:
        t = 0
        for msg in tr:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                out.append((t, msg.note))
    out.sort()
    return out


def bar_patterns(drums: list[tuple[int, int]], bass: list[tuple[int, int]]) -> list[dict]:
    bars: dict[int, dict] = {}
    for t, p in drums:
        cls = next((c for c, ps in CLASSES.items() if p in ps), None)
        if cls is None:
            continue
        slot = int(round(t / TICKS_16TH))
        b = bars.setdefault(slot // SLOTS, {"kick": 0, "snare": 0, "hat": 0, "bass": 0})
        b[cls] |= 1 << (slot % SLOTS)
    for t, p in bass:
        slot = int(round(t / TICKS_16TH))
        if slot // SLOTS in bars:
            bars[slot // SLOTS]["bass"] |= 1 << (slot % SLOTS)
    return [dict(bar=i, **bars[i]) for i in sorted(bars) if (bars[i]["kick"] | bars[i]["snare"] | bars[i]["hat"])]


def popcount(x: int) -> int:
    return bin(x).count("1")


def bits(x: int) -> list[int]:
    return [i for i in range(SLOTS) if x >> i & 1]


def stats(bars: list[dict]) -> dict:
    snare_total = sum(popcount(b["snare"]) for b in bars)
    snare_bb = sum(1 for b in bars for pos in bits(b["snare"]) if pos in BACKBEAT_POS)
    bass_total = sum(popcount(b["bass"]) for b in bars)
    locked = 0
    for b in bars:
        kp = set(bits(b["kick"]))
        for pos in bits(b["bass"]):
            if any(abs(pos - k) <= 1 for k in kp):
                locked += 1
    return {"n_bars": len(bars), "snare_onsets": snare_total, "snare_on_backbeat": snare_bb,
            "backbeat_ratio": round(snare_bb / snare_total, 6) if snare_total else None,
            "bass_onsets": bass_total, "bass_locked_to_kick": locked,
            "bass_kick_lock": round(locked / bass_total, 6) if bass_total else None,
            "distinct_kick_patterns": len({b["kick"] for b in bars}), "distinct_bass_patterns": len({b["bass"] for b in bars})}


def table(pairs: list[tuple[str, int]]) -> dict:
    """counts[context][outcome] + row-normalized."""
    counts: dict[str, dict[str, int]] = {}
    for ctx, out in pairs:
        counts.setdefault(ctx, {})
        counts[ctx][str(out)] = counts[ctx].get(str(out), 0) + 1
    probs = {ctx: {o: c / sum(row.values()) for o, c in sorted(row.items())} for ctx, row in counts.items()}
    return {"counts": {k: dict(sorted(v.items())) for k, v in sorted(counts.items())}, "probs": {k: probs[k] for k in sorted(probs)},
            "n_contexts": len(counts)}


def hash_uniform(tag: str) -> float:
    return int(hashlib.sha256(tag.encode()).hexdigest()[:16], 16) / float(1 << 64)


def draw(row: dict[str, float], u: float) -> int:
    acc = 0.0
    keys = sorted(row, key=lambda k: int(k))
    for k in keys:
        acc += row[k]
        if u < acc:
            return int(k)
    return int(keys[-1])


def sample(model: dict, n: int) -> list[dict]:
    out = []
    kick_row = model["kick_marginal"]["probs"]["*"]
    for i in range(n):
        k = draw(kick_row, hash_uniform(f"groove_v5|{i}|kick|*"))
        s = draw(model["snare_given_kick"]["probs"][str(k)], hash_uniform(f"groove_v5|{i}|snare|{k}"))
        h = draw(model["hat_given_kick_snare"]["probs"][f"{k}|{s}"], hash_uniform(f"groove_v5|{i}|hat|{k}|{s}"))
        b = draw(model["bass_given_kick"]["probs"][str(k)], hash_uniform(f"groove_v5|{i}|bass|{k}"))
        out.append({"bar": i, "kick": k, "snare": s, "hat": h, "bass": b})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="v5 joint groove conditional model (first data)")
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--songs", nargs="*", default=list(DEFAULT_SONGS))
    ap.add_argument("--out", default="data/v5/rules/groove_v5.json")
    args = ap.parse_args()
    os.chdir(_WS)
    corpus = Path(args.corpus_dir)
    blocked = set(json.loads((corpus / "recanonicalization_blocked.json").read_text())["blocked_songs"])
    refused = [s for s in args.songs if s in blocked]
    if refused:
        raise SystemExit(f"REFUSED: blocked songs must not be consumed by the groove model: {refused}")
    per_song, all_bars = {}, []
    for s in args.songs:
        d = corpus / s / "canonical_v5_reindexed"
        if not (d / "reindex_manifest.json").exists():
            raise SystemExit(f"MISSING_REINDEX: {s}")
        tm = json.loads((corpus / s / "transcription_manifest.json").read_text())
        bars = bar_patterns(onsets_ticks(d / "drums.mid"), onsets_ticks(d / "bass.mid"))
        per_song[s] = {"title": tm.get("title"), "bpm_v5": tm["bpm_v5"], "stats": stats(bars),
                       "top_kick_patterns": sorted(((sum(1 for b in bars if b["kick"] == k), format(k, "016b")[::-1]) for k in {b["kick"] for b in bars}), reverse=True)[:5]}
        all_bars.extend(bars)
    model = {
        "kick_marginal": table([("*", b["kick"]) for b in all_bars]),
        "snare_given_kick": table([(str(b["kick"]), b["snare"]) for b in all_bars]),
        "hat_given_kick_snare": table([(f"{b['kick']}|{b['snare']}", b["hat"]) for b in all_bars]),
        "bass_given_kick": table([(str(b["kick"]), b["bass"]) for b in all_bars]),
    }
    sampled = sample(model, N_SAMPLE)
    corpus_stats, sample_stats = stats(all_bars), stats(sampled)
    ctx_counts = {k: v["n_contexts"] for k, v in model.items() if k != "kick_marginal"}
    degenerate = (sample_stats["distinct_kick_patterns"] < MIN_DISTINCT or sample_stats["distinct_bass_patterns"] < MIN_DISTINCT
                  or any(n < MIN_CONTEXTS for n in ctx_counts.values()))
    checks = {}
    for k in ("backbeat_ratio", "bass_kick_lock"):
        c, m = corpus_stats[k], sample_stats[k]
        checks[k] = {"corpus": c, "sampled": m, "abs_diff": round(abs(c - m), 6) if (c is not None and m is not None) else None,
                     "within_tol": (abs(c - m) <= TOL) if (c is not None and m is not None) else False}
    if degenerate:
        verdict = "GROOVE_DEGENERATE"
    elif all(v["within_tol"] for v in checks.values()):
        verdict = "GROOVE_NONDEGENERATE_STATS_MATCH"
    else:
        verdict = "GROOVE_NONDEGENERATE_STATS_MISS"
    out = {"schema_version": 1, "cycle": 81, "env_pin_sha256": ENV_PIN_SHA256, "songs": list(args.songs), "blocked_refused": blocked and sorted(blocked),
           "grid": {"ppq": PPQ, "ticks_per_16th": TICKS_16TH, "slots_per_bar": SLOTS, "classes": {k: list(v) for k, v in CLASSES.items()},
                    "corpus_bars": "bars with >= 1 kick/snare/hat onset", "pattern_encoding": "16-bit mask, bit i = 16th position i"},
           "pre_declared": {"backbeat_positions": list(BACKBEAT_POS), "lock_tolerance_16ths": 1, "stat_tolerance": TOL, "n_sample_bars": N_SAMPLE,
                            "degeneracy": {"min_distinct_kick_patterns": MIN_DISTINCT, "min_distinct_bass_patterns": MIN_DISTINCT, "min_contexts_per_table": MIN_CONTEXTS},
                            "sampling": "SHA-256 inverse-CDF (no PRNG)", "enum": ["GROOVE_NONDEGENERATE_STATS_MATCH", "GROOVE_NONDEGENERATE_STATS_MISS", "GROOVE_DEGENERATE"]},
           "per_song": per_song, "corpus_stats": corpus_stats, "model": model, "table_context_counts": ctx_counts,
           "sampled_bars": sampled, "sample_stats": sample_stats, "validation": checks, "degenerate": degenerate, "verdict": verdict,
           "note": "first data only; NOT fed to any generator this cycle"}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(f"VERDICT {verdict}; corpus {corpus_stats}; sampled {sample_stats}; contexts {ctx_counts}")
    for k, v in checks.items():
        print(f"  {k}: corpus={v['corpus']} sampled={v['sampled']} diff={v['abs_diff']} ok={v['within_tol']}")
    for s, r in per_song.items():
        print(f"  {s} {str(r['title'])[:24]:24s} bars={r['stats']['n_bars']} backbeat={r['stats']['backbeat_ratio']} lock={r['stats']['bass_kick_lock']} top kick {r['top_kick_patterns'][:3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
