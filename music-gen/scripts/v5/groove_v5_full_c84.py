#!/usr/bin/python3
"""c84 P2 — groove v2 on the full eligible corpus with a SHA-256-chosen held-out fold of 3 (pre-registered).

created: 2026-09-09T21:10:00Z
cycle: 84
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-RULES-1/groove-v2-full-corpus-c84

Sibling of scripts/v5/groove_v5_v2.py (READ-ONLY, imported): same alignment / alphabets / smoothing / sampling /
statistics. Differences (all pre-registered in data/v5/rules/groove_prereg_c84.json):
  * eligible set = landed AND sidecar AND NOT tempo-blocked AND NOT content-blocked (as of run start);
  * held-out fold = the 3 eligible sha16 with the lowest SHA-256 of f"groove_fold_c84|{sha16}" (no PRNG);
  * held-out statistics pooled over the 3 held-out songs' bars; same enum + thresholds as c82.
Byte-det: run x2 into fresh mkdtemp outputs (--out). Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor;
no VST3 state APIs; READ-ONLY inputs; c81/c82 groove artifacts untouched.
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

_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v5 import groove_v5_v2 as G  # noqa: E402  READ-ONLY
from scripts.v5.content_blocked import load_content_blocked, refuse_if_content_blocked  # noqa: E402

FOLD_TAG = "groove_fold_c84"
N_HELDOUT = 3


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def eligible_songs(corpus: Path, manifest: Path) -> tuple[list, dict]:
    man = json.loads(manifest.read_text())
    order = [s["sha16"] for s in sorted(man["songs"], key=lambda s: s["v5_priority_rank"]) if s.get("in_v5_corpus")]
    tempo_blocked = set(json.loads((corpus / "recanonicalization_blocked.json").read_text())["blocked_songs"])
    content_blocked = load_content_blocked(corpus)
    landed = [s for s in order if (corpus / s / "transcription_manifest.json").exists()]
    sidecar = [s for s in landed if (corpus / s / "canonical_v5_reindexed_sha256.json").exists()]
    elig = [s for s in sidecar if s not in tempo_blocked and s not in content_blocked]
    gate = {"n_corpus": len(order), "n_landed": len(landed), "n_sidecar": len(sidecar), "tempo_blocked_skipped": sorted(s for s in sidecar if s in tempo_blocked),
            "content_blocked_skipped": sorted(s for s in sidecar if s in content_blocked), "not_landed": [s for s in order if s not in landed],
            "n_eligible": len(elig), "eligible": elig}
    return elig, gate


def fold(elig: list) -> tuple[list, list, dict]:
    ranked = sorted(elig, key=lambda s: hashlib.sha256(f"{FOLD_TAG}|{s}".encode()).hexdigest())
    held = ranked[:N_HELDOUT]
    train = [s for s in elig if s not in held]
    return train, held, {s: hashlib.sha256(f"{FOLD_TAG}|{s}".encode()).hexdigest()[:16] for s in ranked}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v5 groove v2 full corpus + SHA-256 held-out fold of 3")
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--manifest", default="data/v5/corpus/corpus_manifest.json")
    ap.add_argument("--prereg", default="data/v5/rules/groove_prereg_c84.json")
    ap.add_argument("--out", default="data/v5/rules/groove_v5_v2_full.json")
    ap.add_argument("--eligible-from", default=None, help="byte-det second run: take the eligible list from a prior output (songs may land mid-turn)")
    args = ap.parse_args(argv)
    corpus = Path(args.corpus_dir)
    prereg_p = Path(args.prereg)
    out_p = Path(args.out)
    if out_p.exists() and out_p.stat().st_mtime < prereg_p.stat().st_mtime:
        raise SystemExit("PREREG_AFTER_OUTPUT")
    if args.eligible_from:
        prev = json.loads(Path(args.eligible_from).read_text())
        elig, gate = prev["gate"]["eligible"], prev["gate"]
    else:
        elig, gate = eligible_songs(corpus, Path(args.manifest))
    refuse_if_content_blocked(elig, corpus, who="groove_v5_full_c84")
    train, held, ranks = fold(elig)
    songs = {s: G.load_song(corpus, s) for s in elig}
    train_bars = [b for s in train for b in songs[s]["bars"]]
    held_bars = [b for s in held for b in songs[s]["bars"]]
    model = {
        "kick_marginal": G.table([("*", b["kick"]) for b in train_bars]),
        "snare_given_kick": G.table([(str(b["kick"]), b["snare"]) for b in train_bars]),
        "hat_given_kick_snare": G.table([(f"{b['kick']}|{b['snare']}", b["hat"]) for b in train_bars]),
        "bass_given_kick": G.table([(str(b["kick"]), b["bass"]) for b in train_bars]),
    }
    cond = ("snare_given_kick", "hat_given_kick_snare", "bass_given_kick")
    n_ctx = sum(model[t]["n_contexts"] for t in cond)
    n_single = sum(model[t]["n_singleton_contexts"] for t in cond)
    singleton_fraction = round(n_single / n_ctx, 6) if n_ctx else None
    sampled = G.sample(model, G.N_SAMPLE)
    sample_stats = G.stats(sampled)
    train_stats = G.stats(train_bars)
    held_stats = G.stats(held_bars)
    checks = {}
    for k in ("backbeat_ratio", "bass_kick_lock"):
        c, m = held_stats[k], sample_stats[k]
        ok = (c is not None and m is not None)
        checks[k] = {"heldout_pooled": c, "sampled": m, "abs_diff": round(abs(c - m), 6) if ok else None,
                     "within_tol": (abs(c - m) <= G.TOL) if ok else False, "tol": G.TOL}
    degenerate = sample_stats["distinct_kick_patterns"] < G.MIN_DISTINCT or sample_stats["distinct_bass_patterns"] < G.MIN_DISTINCT
    if degenerate:
        verdict = "GROOVE_V2_DEGENERATE"
    elif all(v["within_tol"] for v in checks.values()) and singleton_fraction is not None and singleton_fraction < G.SINGLETON_MAX:
        verdict = "GROOVE_V2_GENERALIZES"
    else:
        verdict = "GROOVE_V2_OVERFITS"
    per_table = {t: {"n_contexts": model[t]["n_contexts"], "n_singleton_contexts": model[t]["n_singleton_contexts"], "n_pairs": model[t]["n_pairs"],
                     "singleton_fraction": round(model[t]["n_singleton_contexts"] / model[t]["n_contexts"], 6) if model[t]["n_contexts"] else None} for t in cond}
    out = {"schema_version": 1, "cycle": 84, "agent": "worker", "run_id": "run-2026-09-06T000000Z", "env_pin_sha256": G.ENV_PIN_SHA256,
           "milestone": "M-V5-RULES-1/groove-v2-full-corpus-c84", "prereg_path": str(prereg_p), "prereg_sha256": _sha(prereg_p),
           "gate": gate, "fold": {"tag": FOLD_TAG, "n_heldout": N_HELDOUT, "rank_hex16": ranks, "train": train, "heldout": held},
           "n_train_songs": len(train), "n_heldout_songs": len(held), "n_train_bars": len(train_bars), "n_heldout_bars": len(held_bars),
           "pre_declared": {"alpha": G.ALPHA, "tol": G.TOL, "singleton_max": G.SINGLETON_MAX, "min_distinct": G.MIN_DISTINCT, "n_sample": G.N_SAMPLE,
                            "enum": list(G.ENUM), "heldout_pooling": "bars of the 3 held-out songs pooled"},
           "per_song": {s: {k: v for k, v in r.items() if k != "bars"} | {"n_bars": len(r["bars"]), "role": "heldout" if s in held else "train"} for s, r in songs.items()},
           "model": model, "per_table": per_table, "table_context_counts": {t: model[t]["n_contexts"] for t in cond},
           "singleton_context_fraction": singleton_fraction, "n_singleton_contexts": n_single, "n_contexts": n_ctx,
           "sampled_bars": sampled, "sample_stats": sample_stats, "train_stats": train_stats, "heldout_stats_pooled": held_stats,
           "validation": checks, "degenerate": degenerate, "verdict": verdict,
           "growth_reference": {"c81_n2_groove_v5": "data/v5/rules/groove_v5.json", "c82_n2_groove_v5_v2": "data/v5/rules/groove_v5_v2.json"},
           "note": "model artifact for the c84 groove-first generator; c81/c82 groove files untouched"}
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(f"VERDICT {verdict}; eligible {len(elig)} train {len(train)} heldout {held}; train bars {len(train_bars)} heldout bars {len(held_bars)}; "
          f"singleton {singleton_fraction} ({n_single}/{n_ctx}); per_table {per_table}")
    print(f"  heldout pooled {held_stats}")
    print(f"  sampled {sample_stats}")
    for k, v in checks.items():
        print(f"  {k}: heldout={v['heldout_pooled']} sampled={v['sampled']} diff={v['abs_diff']} ok={v['within_tol']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
