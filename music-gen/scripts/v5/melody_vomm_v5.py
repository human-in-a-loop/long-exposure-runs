#!/usr/bin/python3
"""c86 F2 P2b — corpus MELODY VOMM (variable-order Markov over "<deg>|<ioi>" tokens, order <= 3, escape to shorter context).

created: 2026-09-09T23:30:00Z
cycle: 86
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F2-bass-melody-dynamics

Pre-registered in data/v5/gen/f2_prereg_c86.json block `melody_vomm`.
Corpus: n=21 eligible songs (data/v5/rules/eligible_c84.json gate.used; NOT PD / Disco A).
Inputs (READ-ONLY): canonical_v5_reindexed/vocals.mid onsets + canonical_v5_reindexed/other.mid onsets whose
  other.reindexed.json start has instrument == 'synth_lead' (paired by (round(start_time * bpm_v5 / 60 * 480), pitch);
  both other instruments sit on DEFAULT_CHANNEL 4 so the JSON label is the only discriminator), key {tonic, mode} from
  data/v5/rules/per_song_c84/<sha16>/harmony_v5.json, bpm_v5 from transcription_manifest.json.
Events per song sorted by tick; simultaneous onsets (same tick) folded to the highest pitch.
Token = "<deg>|<ioi>": deg = scale degree 0..6 of (pitch_class - tonic) % 12 in the mode scale (major [0,2,4,5,7,9,11],
minor [0,2,3,5,7,8,10]; any other mode label -> major, disclosed) or 'c' if chromatic; ioi = round(gap_to_next / 120)
snapped to the nearest bucket in {1,2,3,4,6,8,12} (>= 12 -> 12, 0 -> 1; the last onset of a song has no next onset and gets 12).
Model: counts[order][context_key] = {token: count} for order 0..3 (context = the previous `order` tokens, key = tokens
joined by ' ', '' for order 0); sequences never cross song boundaries.
Escape rule: sampling uses the longest matching context of length <= 3 with >= 1 count; on an unseen context fall back to
the next shorter context (down to order 0); if even order 0 is empty return '0|4'. No smoothing (counts as observed).
Generalization check (pre-declared): singleton-context fraction at order 3 < 0.5 -> GENERALIZES else MEMORIZES (recorded).
scripts/gen/vomm_generator.py (c72) is READ-ONLY and NOT reused: its VommModel requires rule dicts keyed by
'rule_type' / 'rule_id', samples by seed-string modulo reduction rather than a u-driven inverse-CDF, and exposes no JSON
model dict - the sibling below trains on plain token sequences (same escape rule).
Sampling check: 500 tokens from the empty context, u = hash_uniform(f"melody_check|{i}"), L1 distance of the sampled token
frequency to the corpus unigram (informational). phrase_structure: phrase = run of onsets with gaps < 2 beats (960 ticks).
FD-1: recorded, never tuned. No PRNG (SHA-256 inverse-CDF only). No sidecar_nonfactor. No VST3 state APIs.
Exports (pure, side-effect free): tokenize, train_counts, order_stats, sample_next, generate_sequence, token_pitch,
phrase_structure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

for _k, _v in (("PYTHONHASHSEED", "0"), ("SOURCE_DATE_EPOCH", "1756463424"), ("TZ", "UTC"), ("LC_ALL", "C.UTF-8"),
               ("OMP_NUM_THREADS", "1"), ("MKL_NUM_THREADS", "1"), ("OPENBLAS_NUM_THREADS", "1")):
    os.environ.setdefault(_k, _v)

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
PPQ = 480
TICKS_16TH = PPQ // 4
MAX_ORDER = 3
IOI_BUCKETS = (1, 2, 3, 4, 6, 8, 12)
SCALES = {"major": (0, 2, 4, 5, 7, 9, 11), "minor": (0, 2, 3, 5, 7, 8, 10)}
PHRASE_GAP_TICKS = 2 * PPQ
N_CHECK = 500
SINGLETON_MAX = 0.5
DEFAULT_TOKEN = "0|4"
DEFAULT_OUT = "data/v5/rules/melody_vomm_v5.json"
DEFAULT_ELIGIBLE = "data/v5/rules/eligible_c84.json"
DEFAULT_CORPUS = "data/v5/corpus"
DEFAULT_PER_SONG = "data/v5/rules/per_song_c84"
PREREG = "data/v5/gen/f2_prereg_c86.json"
ENUM = ("GENERALIZES", "MEMORIZES")


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def hash_uniform(tag: str) -> float:
    """SHA-256 inverse-CDF driver (identical to scripts.v5.groove_v5_v2.hash_uniform, READ-ONLY there)."""
    return int(hashlib.sha256(tag.encode()).hexdigest()[:16], 16) / float(1 << 64)


# ----------------------------------------------------------------------------------------------------------------------
# pure tokenization / training
# ----------------------------------------------------------------------------------------------------------------------
def scale_for(mode: str) -> tuple[int, ...]:
    return SCALES.get(str(mode).lower(), SCALES["major"])


def degree_of(pitch: int, tonic: int, mode: str) -> str:
    sc = scale_for(mode)
    rel = (pitch - tonic) % 12
    return str(sc.index(rel)) if rel in sc else "c"


def ioi_bucket(gap_ticks: int | None) -> int:
    if gap_ticks is None:
        return IOI_BUCKETS[-1]
    n = int(round(gap_ticks / TICKS_16TH))
    if n <= 0:
        return 1
    if n >= IOI_BUCKETS[-1]:
        return IOI_BUCKETS[-1]
    return min(IOI_BUCKETS, key=lambda b: (abs(b - n), b))


def fold_simultaneous(onsets: list[tuple[int, int]]) -> list[tuple[int, int]]:
    top: dict[int, int] = {}
    for t, p in onsets:
        top[t] = max(top.get(t, -1), p)
    return sorted(top.items())


def tokenize(onsets: list[tuple[int, int]], tonic: int, mode: str) -> list[str]:
    ev = fold_simultaneous(onsets)
    toks = []
    for i, (t, p) in enumerate(ev):
        gap = ev[i + 1][0] - t if i + 1 < len(ev) else None
        toks.append(f"{degree_of(p, tonic, mode)}|{ioi_bucket(gap)}")
    return toks


def ctx_key(ctx: tuple[str, ...]) -> str:
    return " ".join(ctx)


def train_counts(sequences: list[list[str]], max_order: int = MAX_ORDER) -> dict[str, dict[str, dict[str, int]]]:
    counts: dict[str, dict[str, dict[str, int]]] = {str(o): {} for o in range(max_order + 1)}
    for seq in sequences:
        for i, tok in enumerate(seq):
            for o in range(0, max_order + 1):
                if i - o < 0:
                    break
                k = ctx_key(tuple(seq[i - o:i]))
                row = counts[str(o)].setdefault(k, {})
                row[tok] = row.get(tok, 0) + 1
    return counts


def order_stats(counts: dict[str, dict[str, dict[str, int]]]) -> dict[str, dict]:
    out = {}
    for o, table in sorted(counts.items(), key=lambda kv: int(kv[0])):
        n = len(table)
        s = sum(1 for row in table.values() if sum(row.values()) == 1)
        out[o] = {"n_contexts": n, "n_singleton_contexts": s,
                  "singleton_context_fraction": round(s / n, 9) if n else None,
                  "n_events": sum(sum(r.values()) for r in table.values())}
    return out


def phrase_structure(per_song_onsets: dict[str, list[tuple[int, int]]], gap_ticks: int = PHRASE_GAP_TICKS) -> dict:
    hist: dict[str, int] = {}
    lengths, per_song = [], {}
    for sha, ons in sorted(per_song_onsets.items()):
        ev = fold_simultaneous(ons)
        n_phr, run = 0, 0
        for i, (t, _p) in enumerate(ev):
            run += 1
            if i + 1 == len(ev) or ev[i + 1][0] - t >= gap_ticks:
                lengths.append(run)
                hist[str(run)] = hist.get(str(run), 0) + 1
                n_phr += 1
                run = 0
        per_song[sha] = {"n_events": len(ev), "n_phrases": n_phr}
    s = sorted(lengths)
    return {"definition": f"phrase = run of (folded) onsets with gaps < {gap_ticks} ticks (2 beats); length = onsets per phrase",
            "n_phrases": len(s), "length_histogram": hist,
            "mean_length": round(sum(s) / len(s), 6) if s else None, "median_length": s[len(s) // 2] if s else None,
            "max_length": s[-1] if s else None, "per_song": per_song}


# ----------------------------------------------------------------------------------------------------------------------
# exported samplers (pure)
# ----------------------------------------------------------------------------------------------------------------------
def sample_next(model: dict, context: tuple, u: float) -> str:
    """Longest matching context (<= order 3) with >= 1 count; inverse-CDF over sorted tokens; '0|4' if order 0 is empty."""
    counts = model["counts"]
    max_order = int(model.get("max_order", MAX_ORDER))
    ctx = tuple(context)[-max_order:] if max_order else ()
    for o in range(min(max_order, len(ctx)), -1, -1):
        row = counts.get(str(o), {}).get(ctx_key(ctx[len(ctx) - o:]) if o else "")
        if not row:
            continue
        total = sum(row.values())
        acc = 0.0
        toks = sorted(row)
        for t in toks:
            acc += row[t] / total
            if u < acc:
                return t
        return toks[-1]
    return DEFAULT_TOKEN


def generate_sequence(model: dict, n: int, seed_str: str) -> list[str]:
    seq: list[str] = []
    for i in range(n):
        seq.append(sample_next(model, tuple(seq[-MAX_ORDER:]), hash_uniform(f"{seed_str}|{i}")))
    return seq


def token_pitch(token: str, tonic: int, mode: str, register_lo: int, register_hi: int, prev_pitch: int | None) -> int:
    """Nearest pitch with the token's scale degree to prev_pitch within [register_lo, register_hi]; chromatic 'c' ->
    prev_pitch + 1 clipped; prev_pitch None -> the register midpoint is the anchor."""
    lo, hi = int(min(register_lo, register_hi)), int(max(register_lo, register_hi))
    anchor = (lo + hi) // 2 if prev_pitch is None else int(prev_pitch)
    deg = token.split("|")[0]
    if deg == "c":
        return max(lo, min(hi, anchor + 1))
    pc = (int(tonic) + scale_for(mode)[int(deg) % 7]) % 12
    cands = [p for p in range(lo, hi + 1) if p % 12 == pc]
    if not cands:
        return max(lo, min(hi, anchor))
    return min(cands, key=lambda p: (abs(p - anchor), p))


def run_sampling_check(model: dict, n: int = N_CHECK) -> dict:
    seq = generate_sequence(model, n, "melody_check")
    freq: dict[str, int] = {}
    for t in seq:
        freq[t] = freq.get(t, 0) + 1
    uni = model["counts"]["0"].get("", {})
    tot = sum(uni.values())
    vocab = sorted(set(uni) | set(freq))
    l1 = sum(abs(freq.get(t, 0) / n - (uni.get(t, 0) / tot if tot else 0.0)) for t in vocab)
    return {"n": n, "tag_format": "melody_check|{i}", "start_context": [], "l1_to_corpus_unigram": round(l1, 9),
            "n_distinct_sampled": len(freq), "n_vocab": len(uni), "informational": True,
            "sampled_first_16": seq[:16]}


# ----------------------------------------------------------------------------------------------------------------------
# I/O
# ----------------------------------------------------------------------------------------------------------------------
def midi_onsets(path: Path) -> list[tuple[int, int]]:
    import mido  # local import keeps the pure exports importable without mido
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


def lead_onsets(other_mid: Path, other_json: Path, bpm: float) -> tuple[list[tuple[int, int]], dict]:
    """other.mid onsets whose (tick, pitch) matches a synth_lead start in other.reindexed.json."""
    if not other_mid.exists() or not other_json.exists():
        return [], {"n_json_lead_starts": 0, "n_matched": 0, "n_unmatched_json_lead": 0, "present": False}
    js = json.loads(other_json.read_text())
    lead = {(int(round(e["start_time"] * bpm / 60.0 * PPQ)), int(e["pitch"])) for e in js
            if e.get("type") == "start" and e.get("instrument") == "synth_lead"}
    ons = midi_onsets(other_mid)
    have = set(ons)
    kept = [o for o in ons if o in lead]
    return kept, {"n_json_lead_starts": len(lead), "n_matched": len(kept), "n_midi_other_onsets": len(ons),
                  "n_unmatched_json_lead": len([k for k in lead if k not in have]), "present": True}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--eligible-from", default=DEFAULT_ELIGIBLE)
    ap.add_argument("--corpus-dir", default=DEFAULT_CORPUS)
    ap.add_argument("--per-song-dir", default=DEFAULT_PER_SONG)
    a = ap.parse_args()
    elig_p = _WS / a.eligible_from
    songs = json.loads(elig_p.read_text())["gate"]["used"]
    sequences, per_song, per_song_onsets, disclosures, inputs = [], {}, {}, [], {}
    unigram_by_song = {}
    for sha in songs:
        cdir = _WS / a.corpus_dir / sha / "canonical_v5_reindexed"
        harm_p = _WS / a.per_song_dir / sha / "harmony_v5.json"
        man_p = _WS / a.corpus_dir / sha / "transcription_manifest.json"
        harm = json.loads(harm_p.read_text())
        bpm = float(json.loads(man_p.read_text())["bpm_v5"])
        key = harm["key"]
        if str(key["mode"]).lower() not in SCALES:
            disclosures.append(f"{sha}: mode '{key['mode']}' not in {{major, minor}}; major scale used")
        voc = midi_onsets(cdir / "vocals.mid") if (cdir / "vocals.mid").exists() else []
        lead, pairing = lead_onsets(cdir / "other.mid", cdir / "other.reindexed.json", bpm)
        ons = sorted(voc + lead)
        toks = tokenize(ons, int(key["tonic"]), str(key["mode"]))
        if toks:
            sequences.append(toks)
        per_song_onsets[sha] = ons
        per_song[sha] = {"n_vocal_onsets": len(voc), "n_lead_onsets": len(lead), "n_events_folded": len(toks),
                         "n_chromatic": sum(1 for t in toks if t.startswith("c|")), "key": {"tonic": key["tonic"], "mode": key["mode"]},
                         "bpm_v5": bpm, "lead_pairing": pairing}
        inputs[sha] = {"vocals_mid_sha256": sha_file(cdir / "vocals.mid") if (cdir / "vocals.mid").exists() else None,
                       "other_mid_sha256": sha_file(cdir / "other.mid") if (cdir / "other.mid").exists() else None,
                       "other_reindexed_json_sha256": sha_file(cdir / "other.reindexed.json") if (cdir / "other.reindexed.json").exists() else None,
                       "harmony_v5_sha256": sha_file(harm_p)}
        if pairing.get("n_unmatched_json_lead"):
            disclosures.append(f"{sha}: {pairing['n_unmatched_json_lead']} synth_lead JSON starts had no exact (tick, pitch) match in other.mid")
    counts = train_counts(sequences)
    stats = order_stats(counts)
    o3 = stats[str(MAX_ORDER)]["singleton_context_fraction"]
    verdict = "GENERALIZES" if o3 is not None and o3 < SINGLETON_MAX else "MEMORIZES"
    model = {"max_order": MAX_ORDER, "counts": counts}
    check = run_sampling_check(model)
    uni = counts["0"].get("", {})
    tot = sum(uni.values())
    disclosures += [
        "the last onset of each song has no next onset; its ioi bucket is 12 (phrase end)",
        "sequences are trained per song; contexts never cross song boundaries",
        "synth_lead onsets are paired from other.reindexed.json by exact (round(start_time*bpm_v5/60*480), pitch); "
        "synth_pad / synth_strings / orchestra_hit starts are excluded; every other.mid onset sharing an exact (tick, pitch) "
        "with a synth_lead start is kept (a pad note coincident with a lead note at the same pitch is indistinguishable in "
        "the MIDI, so n_matched can exceed n_json_lead_starts; folding to the highest pitch per tick absorbs this)",
        "no smoothing in the VOMM: the escape rule (longest context with >= 1 count) is the only backoff",
        "vomm_generator.py (c72) not reused: constructor requires rule dicts with rule_type/rule_id, sampler is seed-string "
        "modulo (not u inverse-CDF), no JSON model export",
    ]
    out = {
        "schema_version": 1, "cycle": 86, "agent": "worker", "run_id": "run-2026-09-06T000000Z",
        "milestone": "M-V5-GEN-1/F2-bass-melody-dynamics", "kind": "melody_vomm_v5",
        "env_pin_sha256": ENV_PIN_SHA256, "prereg_path": PREREG, "prereg_sha256": sha_file(_WS / PREREG),
        "script_sha256": sha_file(Path(__file__).resolve()),
        "eligible_from": a.eligible_from, "eligible_sha256": sha_file(elig_p), "n_songs": len(songs), "songs": list(songs),
        "n_songs_with_events": len(sequences), "inputs": inputs,
        "vomm_generator_reused": False,
        "vomm_generator_reuse_reason": "scripts/gen/vomm_generator.py VommModel takes List[dict] rules keyed by 'rule_type' "
                                       "and 'rule_id' and samples via sha256(seed_str|ctx) modulo total, not a plain token "
                                       "sequence with a u-driven inverse-CDF or a JSON model dict; sibling VOMM implemented "
                                       "here with the same escape rule (backoff to the next shorter context)",
        "token": {"format": "<deg>|<ioi>", "deg": "scale degree 0..6 of (pc - tonic) % 12 in the mode scale, 'c' if chromatic",
                  "scales": {k: list(v) for k, v in SCALES.items()}, "ioi": "round(gap_ticks / 120) snapped to nearest bucket",
                  "ioi_buckets": list(IOI_BUCKETS), "fold": "simultaneous onsets (same tick) -> highest pitch"},
        "model": {"max_order": MAX_ORDER, "context_key": "previous tokens joined by ' ' ('' for order 0)",
                  "escape_rule": "longest matching context of length <= 3 with >= 1 count; unseen -> next shorter context; "
                                 "empty order 0 -> '0|4'", "smoothing": "none",
                  "counts": counts},
        "max_order": MAX_ORDER, "counts": counts,
        "order_stats": stats, "singleton_threshold_order3": SINGLETON_MAX, "verdict_enum": list(ENUM), "verdict": verdict,
        "unigram": {"n": tot, "probs": {t: round(c / tot, 9) for t, c in sorted(uni.items())} if tot else {}},
        "vocab": sorted(uni),
        "phrase_structure": phrase_structure(per_song_onsets),
        "per_song": per_song,
        "sampling_check": check,
        "fd1": "recorded, not tuned",
        "disclosures": disclosures,
    }
    out_p = Path(a.out) if Path(a.out).is_absolute() else _WS / a.out
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out_p} sha256={sha_file(out_p)} n_events={tot} verdict={verdict} "
          f"order3_singleton={o3} l1={check['l1_to_corpus_unigram']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
