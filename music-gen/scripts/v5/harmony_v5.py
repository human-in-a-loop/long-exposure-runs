#!/usr/bin/python3
"""c80 P3 — harmony root+quality template matching + functional Markov chain (OPERATOR #2, first data).

created: 2026-09-06T16:30:00Z
cycle: 80
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-RULES-1/harmony_v5-first-data-c80

Per song (landed = transcription_manifest.json present; NOT listed in
data/v5/corpus/recanonicalization_blocked.json):
  1. Read canonical MIDI (canonical_v5c_reindexed/ if a SUPPORTED tempo revision
     exists, else canonical_v5_reindexed/ — the c80 lossless re-index) for
     bass + guitar + piano + other. PPQ=480 and tempo=bpm_v5 make beat = tick/480.
     c81: the LOSSY c79 canonical_midi_full/ is NEVER read; an unblocked song
     without a reindexed dir raises MISSING_REINDEX (no silent fallback).
  2. Beat-weighted pitch-class profile: for every note, its overlap (in beats) with
     each beat x velocity is added to pcp[beat][pitch % 12]. DISCLOSURE: the c4
     canonical serializer writes a uniform velocity (100) because MuScriptor events
     carry no velocity, so the weighting is duration-only in practice.
  3. Template matching: 7 qualities x 12 roots = 84 binary templates, cosine
     similarity against each beat's PCP; beats with zero energy -> "N". Ties ->
     lowest SHA-256 of f"{sha16}|{beat}|{root}|{quality}".
  4. Key: Krumhansl-Kessler major/minor profiles correlated with the song-summed
     PCP over 12 rotations (no key metadata exists in the profile manifests);
     argmax, ties -> (mode order major<minor, lowest tonic). Common-key transposition:
     functional state = f"{(root - tonic) % 12}:{quality}" so every song is
     expressed relative to its own tonic.
  5. Corpus chain: beat-level transition counts over functional states
     (self-transitions INCLUDED — a per-beat sampler's chain), row-normalized;
     stationary distribution by power iteration. Segment-level (change-only)
     matrix emitted as a secondary table.
Pre-declared degeneracy check (NOT tuned): non-degenerate iff max stationary
mass < 0.60 AND >= 4 distinct qualities appear with segment count >= 8 across the
corpus. Requires >= 3 unblocked landed songs; otherwise writes harmony_v5_gated.json.
Nothing here feeds a generator this cycle.

Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs;
READ-ONLY inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
         "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
         "OPENBLAS_NUM_THREADS": "1"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

import numpy as np  # noqa: E402
import mido  # noqa: E402

_WS = Path(__file__).resolve().parent.parent.parent
ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
PPQ = 480
HARMONY_STEMS = ("bass", "guitar", "piano", "other")
QUALITIES = {"maj": (0, 4, 7), "min": (0, 3, 7), "7": (0, 4, 7, 10), "min7": (0, 3, 7, 10),
             "maj7": (0, 4, 7, 11), "9": (0, 2, 4, 7, 10), "sus": (0, 5, 7)}
QUALITY_ORDER = tuple(QUALITIES)
PC_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
# Krumhansl & Kessler (1982) key profiles
KK_MAJOR = (6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88)
KK_MINOR = (6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17)
DEGENERACY = {"max_stationary_mass_lt": 0.60, "min_distinct_qualities": 4, "min_quality_segment_count": 8}
MIN_SONGS = 3
CYCLE = 82  # c82 P3: input-artifact exclusion (pre-declared) on top of the c81 lossless-only patch
# c82 P3.1 PRE-DECLARED input-artifact exclusion: a beat is EXCLUDED from the chord stream (never enters a PCP,
# a state, or a transition) when a single stem contributes >= EXCLUDE_MAX_SIMULTANEOUS_STARTS note starts on
# that beat (the Rome bass 215.08 s tail chord: 122 starts in one chunk-tail event). Excluded-beat counts are
# disclosed per song and per stem. No other behaviour change.
EXCLUDE_MAX_SIMULTANEOUS_STARTS = 12
# c81 P0.4: lossless dirs only; "canonical_midi_full" (c79, lossy) removed from the preference tuple.
MIDI_DIR_PREFERENCE = ("canonical_v5c_reindexed", "canonical_v5_reindexed")


class MissingReindexError(RuntimeError):
    """Raised when an unblocked landed song has no lossless re-indexed canonical MIDI (c81 P0.4)."""


def sha_str(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def templates() -> list[tuple[int, str, np.ndarray]]:
    out = []
    for root in range(12):
        for q in QUALITY_ORDER:
            v = np.zeros(12)
            for iv in QUALITIES[q]:
                v[(root + iv) % 12] = 1.0
            out.append((root, q, v / np.linalg.norm(v)))
    return out


TEMPLATES = templates()


def read_notes(mid_path: Path) -> list[tuple[float, float, int, int]]:
    """(start_beat, end_beat, pitch, velocity) from a canonical MIDI (PPQ=480, tick/480 = beat)."""
    m = mido.MidiFile(str(mid_path))
    assert m.ticks_per_beat == PPQ, f"{mid_path}: PPQ {m.ticks_per_beat} != {PPQ}"
    notes = []
    for tr in m.tracks:
        t = 0
        open_: dict[tuple[int, int], list[tuple[int, int]]] = {}  # FIFO per (channel, pitch): overlapping same-pitch notes kept
        for msg in tr:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                open_.setdefault((msg.channel, msg.note), []).append((t, msg.velocity))
            elif msg.type in ("note_off", "note_on"):
                k = (msg.channel, msg.note)
                if open_.get(k):
                    t0, vel = open_[k].pop(0)
                    if t > t0:
                        notes.append((t0 / PPQ, t / PPQ, msg.note, vel))
    notes.sort()
    return notes


def beat_pcps(notes: list[tuple[float, float, int, int]]) -> np.ndarray:
    if not notes:
        return np.zeros((0, 12))
    n_beats = int(np.ceil(max(e for _s, e, _p, _v in notes)))
    pcp = np.zeros((n_beats, 12))
    for s, e, p, v in notes:
        b0, b1 = int(np.floor(s)), int(np.ceil(e))
        for b in range(b0, min(b1, n_beats)):
            ov = min(e, b + 1) - max(s, b)
            if ov > 0:
                pcp[b, p % 12] += ov * v
    return pcp


def match_beat(sha16: str, beat: int, v: np.ndarray) -> dict:
    n = float(np.linalg.norm(v))
    if n <= 0:
        return {"root": None, "quality": "N", "sim": 0.0}
    u = v / n
    best = None
    for root, q, tv in TEMPLATES:
        sim = round(float(np.dot(u, tv)), 9)
        key = (-sim, sha_str(f"{sha16}|{beat}|{root}|{q}"))
        if best is None or key < best[0]:
            best = (key, root, q, sim)
    return {"root": best[1], "quality": best[2], "sim": best[3]}


def estimate_key(pcp_sum: np.ndarray) -> dict:
    best = None
    for mode, prof in (("major", KK_MAJOR), ("minor", KK_MINOR)):
        for tonic in range(12):
            rot = np.roll(np.asarray(prof), tonic)
            r = float(np.corrcoef(pcp_sum, rot)[0, 1]) if pcp_sum.std() > 0 else 0.0
            r = round(r, 9)
            key = (-r, 0 if mode == "major" else 1, tonic)
            if best is None or key < best[0]:
                best = (key, tonic, mode, r)
    return {"tonic": best[1], "tonic_name": PC_NAMES[best[1]], "mode": best[2], "corr": best[3], "method": "krumhansl_kessler_argmax"}


def analyse_song(sha16: str, corpus: Path) -> dict:
    d = corpus / sha16
    # c81: preference tuple contains ONLY lossless re-indexed dirs. canonical_v5c_reindexed/ exists only if a
    # SUPPORTED tempo criterion re-canonicalized the song; canonical_v5_reindexed/ is the c80 fix. The c79
    # canonical_midi_full/ (LOSSY, see reindex_canonical_v5.py) is deliberately NOT a fallback.
    mid_dir = None
    for sub in MIDI_DIR_PREFERENCE:
        if (d / sub / "reindex_manifest.json").exists():  # a lossless dir always carries its reindex manifest
            mid_dir = d / sub
            break
    if mid_dir is None:
        raise MissingReindexError(f"MISSING_REINDEX: {sha16} has no {'/'.join(MIDI_DIR_PREFERENCE)} directory; "
                                  f"run scripts/v5/reindex_canonical_v5.py --songs {sha16} (the c79 canonical_midi_full/ is lossy and is never read)")
    tm = json.loads((d / "transcription_manifest.json").read_text())
    per_stem = {}
    all_notes = []
    excluded: dict[int, dict[str, int]] = {}  # c82 P3.1: beat -> {stem: n_starts} for beats hit by the exclusion rule
    for stem in HARMONY_STEMS:
        p = mid_dir / f"{stem}.mid"
        notes = read_notes(p) if p.exists() else []
        starts_per_beat: dict[int, int] = {}
        for s, _e, _p, _v in notes:
            starts_per_beat[int(np.floor(s))] = starts_per_beat.get(int(np.floor(s)), 0) + 1
        stem_excl = {b: n for b, n in starts_per_beat.items() if n >= EXCLUDE_MAX_SIMULTANEOUS_STARTS}
        for b, n in stem_excl.items():
            excluded.setdefault(b, {})[stem] = n
        per_stem[stem] = {"n_notes_midi": len(notes),
                          "n_note_on_muscriptor_json": tm["note_counts"].get(stem, {}).get("n_note_on"),
                          "excluded_beats": sorted(stem_excl), "n_excluded_beats": len(stem_excl)}
        all_notes.extend(notes)
    pcp = beat_pcps(all_notes)
    excluded_beats = sorted(b for b in excluded if b < len(pcp))
    if excluded_beats:
        pcp[excluded_beats, :] = 0.0  # excluded beats never enter the key estimate either
    vels = sorted({v for _s, _e, _p, v in all_notes})
    key = estimate_key(pcp.sum(axis=0)) if len(pcp) else {"tonic": 0, "tonic_name": "C", "mode": "major", "corr": 0.0, "method": "empty"}
    stream = []
    for b in range(len(pcp)):
        if b in excluded:
            continue  # c82 P3.1: dropped from the stream -> no state, no transition
        m = match_beat(sha16, b, pcp[b])
        state = "N" if m["root"] is None else f"{(m['root'] - key['tonic']) % 12}:{m['quality']}"
        stream.append({"beat": b, "root": m["root"], "quality": m["quality"], "sim": m["sim"], "state": state,
                       "energy": round(float(pcp[b].sum()), 6)})
    segments = []
    for e in stream:
        if segments and segments[-1]["state"] == e["state"]:
            segments[-1]["n_beats"] += 1
        else:
            segments.append({"state": e["state"], "start_beat": e["beat"], "n_beats": 1})
    return {"schema_version": 1, "cycle": CYCLE, "sha16": sha16, "title": tm.get("title"), "bpm_v5": tm["bpm_v5"],
            "midi_dir": str(mid_dir), "env_pin_sha256": ENV_PIN_SHA256, "stems": HARMONY_STEMS, "per_stem": per_stem,
            "velocity_values_seen": vels, "velocity_uniform": len(vels) <= 1,
            "weighting": "note overlap (beats) x velocity; velocity is uniform in canonical MIDI so effectively duration-only",
            "key": key, "n_beats": len(pcp), "n_segments": len(segments),
            "exclusion_rule": {"max_simultaneous_starts_per_stem": EXCLUDE_MAX_SIMULTANEOUS_STARTS,
                               "excluded_beats": {str(b): excluded[b] for b in excluded_beats}, "n_excluded_beats": len(excluded_beats),
                               "n_beats_in_stream": len(stream)},
            "chord_stream": stream, "segments": segments}


def markov(streams: dict[str, list[str]], segs: dict[str, list[str]]) -> dict:
    states = sorted({s for seq in streams.values() for s in seq} | {s for seq in segs.values() for s in seq})
    idx = {s: i for i, s in enumerate(states)}
    C = np.zeros((len(states), len(states)))
    for seq in streams.values():
        for a, b in zip(seq, seq[1:]):
            C[idx[a], idx[b]] += 1
    Cs = np.zeros_like(C)
    for seq in segs.values():
        for a, b in zip(seq, seq[1:]):
            Cs[idx[a], idx[b]] += 1
    rows = C.sum(axis=1, keepdims=True)
    P = np.divide(C, rows, out=np.zeros_like(C), where=rows > 0)
    for i in range(len(states)):  # absorbing/unseen rows -> uniform (documented)
        if rows[i, 0] == 0:
            P[i, :] = 1.0 / len(states)
    pi = np.full(len(states), 1.0 / len(states))
    for _ in range(2000):
        pi = pi @ P
        pi = pi / pi.sum()
    seg_counts_by_quality: dict[str, int] = {}
    for seq in segs.values():
        for s in seq:
            q = s.split(":")[1] if ":" in s else "N"
            seg_counts_by_quality[q] = seg_counts_by_quality.get(q, 0) + 1
    quals_ok = [q for q, c in sorted(seg_counts_by_quality.items()) if q != "N" and c >= DEGENERACY["min_quality_segment_count"]]
    max_mass = float(pi.max())
    non_degenerate = (max_mass < DEGENERACY["max_stationary_mass_lt"] and len(quals_ok) >= DEGENERACY["min_distinct_qualities"])
    return {"states": states, "beat_level_counts": C.astype(int).tolist(), "beat_level_row_normalized": np.round(P, 6).tolist(),
            "segment_level_counts": Cs.astype(int).tolist(),
            "stationary_distribution": {s: round(float(pi[idx[s]]), 6) for s in states},
            "max_stationary_state": states[int(pi.argmax())], "max_stationary_mass": round(max_mass, 6),
            "segment_counts_by_quality": dict(sorted(seg_counts_by_quality.items())),
            "qualities_with_count_ge_threshold": quals_ok,
            "degeneracy_thresholds": DEGENERACY,
            "degeneracy_verdict": "NON_DEGENERATE" if non_degenerate else "DEGENERATE",
            "chain_definition": "beat-level functional states (self-transitions included); unseen rows uniform; stationary by power iteration (2000 steps)"}


def main() -> int:
    global EXCLUDE_MAX_SIMULTANEOUS_STARTS
    ap = argparse.ArgumentParser(description="v5 harmony root+quality template matching + functional Markov chain")
    ap.add_argument("--manifest", default="data/v5/corpus/corpus_manifest.json")
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--out-dir", default="data/v5/rules")
    ap.add_argument("--min-songs", type=int, default=MIN_SONGS)
    ap.add_argument("--exclude-max-starts", type=int, default=EXCLUDE_MAX_SIMULTANEOUS_STARTS,
                    help="c82 P3.1 exclusion threshold; the official run uses the pre-declared default (12). Any other value is a LABELLED "
                         "sensitivity diagnostic and must be written to a non-default --out-dir.")
    args = ap.parse_args()
    os.chdir(_WS)
    if args.exclude_max_starts != EXCLUDE_MAX_SIMULTANEOUS_STARTS:
        if args.out_dir == "data/v5/rules":
            raise SystemExit("sensitivity runs must not overwrite the official artifacts: pass --out-dir <diagnostic dir>")
        EXCLUDE_MAX_SIMULTANEOUS_STARTS = args.exclude_max_starts
    corpus = Path(args.corpus_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    man = json.loads(Path(args.manifest).read_text())
    order = [s["sha16"] for s in sorted(man["songs"], key=lambda s: s["v5_priority_rank"]) if s.get("in_v5_corpus")]
    blocked_p = corpus / "recanonicalization_blocked.json"
    blocked = set(json.loads(blocked_p.read_text())["blocked_songs"]) if blocked_p.exists() else set()
    landed = [s for s in order if (corpus / s / "transcription_manifest.json").exists()]
    used = [s for s in landed if s not in blocked]
    skipped_blocked = [s for s in landed if s in blocked]
    gate = {"cycle": CYCLE, "n_landed": len(landed), "landed": landed, "n_blocked_skipped": len(skipped_blocked),
            "blocked_skipped": skipped_blocked, "n_used": len(used), "used": used, "min_songs": args.min_songs}
    if len(used) < args.min_songs:
        gate["verdict"] = "GATED_INSUFFICIENT_UNBLOCKED_SONGS"
        (out_dir / "harmony_v5_gated.json").write_text(json.dumps(gate, sort_keys=True, indent=2) + "\n")
        print(f"GATED: {len(used)} unblocked landed songs < {args.min_songs}: {gate}")
        return 0
    streams, segs, per_song_summary = {}, {}, {}
    for s in used:
        r = analyse_song(s, corpus)
        (out_dir / s).mkdir(parents=True, exist_ok=True)
        (out_dir / s / "harmony_v5.json").write_text(json.dumps(r, sort_keys=True, indent=2) + "\n")
        streams[s] = [e["state"] for e in r["chord_stream"]]
        segs[s] = [g["state"] for g in r["segments"]]
        per_song_summary[s] = {"title": r["title"], "key": r["key"], "n_beats": r["n_beats"], "n_segments": r["n_segments"],
                               "per_stem": r["per_stem"], "top_states": sorted(
                                   ((streams[s].count(st), st) for st in set(streams[s])), reverse=True)[:5]}
        print(f"{s} {str(r['title'])[:26]:26s} key={r['key']['tonic_name']} {r['key']['mode']} beats={r['n_beats']} "
              f"segs={r['n_segments']} top={per_song_summary[s]['top_states'][:3]}")
    mk = markov(streams, segs)
    mk.update({"schema_version": 1, "cycle": CYCLE, "env_pin_sha256": ENV_PIN_SHA256, "gate": gate,
               "per_song": per_song_summary, "qualities": list(QUALITY_ORDER),
               "notes": ["first data only; NOT fed to any generator this cycle",
                         "velocity uniform in canonical MIDI -> duration-only weighting (disclosed)"]})
    (out_dir / "harmony_markov_v5.json").write_text(json.dumps(mk, sort_keys=True, indent=2) + "\n")
    print(f"corpus chain: {len(mk['states'])} states; max stationary {mk['max_stationary_state']}={mk['max_stationary_mass']}; "
          f"qualities>=8 segs {mk['qualities_with_count_ge_threshold']}; verdict {mk['degeneracy_verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
