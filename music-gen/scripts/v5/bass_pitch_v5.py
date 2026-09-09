#!/usr/bin/python3
"""c86 F2 P2b — corpus BASS PITCH MODEL (interval class vs chord root, conditioned on 16th slot x chord-change flag).

created: 2026-09-09T23:30:00Z
cycle: 86
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F2-bass-melody-dynamics

Pre-registered in data/v5/gen/f2_prereg_c86.json block `bass_pitch_model`.
Corpus: n=21 eligible songs (data/v5/rules/eligible_c84.json gate.used; NOT PD / Disco A).
Inputs (READ-ONLY): data/v5/corpus/<sha16>/canonical_v5_reindexed/bass.mid (PPQ 480, tempo = bpm_v5, beat = tick/480),
  data/v5/rules/per_song_c84/<sha16>/harmony_v5.json chord_stream (per-beat root/quality/state),
  data/v5/rules/groove_v5_v2_full.json per_song[sha16].phase.offset (16th slots; downbeat alignment only).

Per bass onset: b = tick // 480, slot s = (tick % 480) // 120 in 0..3, chord = chord_stream[b] (onsets whose chord root is
null or state 'N' are skipped), next = chord_stream[b+1]; chord_change_flag = next exists, next.root not null and
next.root != root (a null/'N' next beat counts as no change - disclosed).
Interval classes (mutually exclusive, precedence approach > root > fifth > third > octave > other where `root` is the
NON-octave root-pc case: approach = pc within +/-1 or +/-2 semitones of the NEXT chord root, only when chord_change_flag;
then pc == root -> octave iff pitch >= (lowest root-pc bass note of the chord segment, a maximal run of beats sharing the
root) + 12 else root; fifth = pc - root == 7; third = pc - root in {3, 4}; other = the rest.
Conditionals: "<slot>|<chg>" -> class counts and alpha = 0.5 additive-smoothed probabilities over the 6 classes in the
fixed order root/fifth/octave/third/approach/other; a global marginal; per-song counts and register (median, p25, p75).
Downbeat = aligned 16th slot (tick//120 - phase_offset) % 16 == 0 (aligned grid, per pre-reg); the raw-grid variant
(beat % 4 == 0 and slot 0, offset 0) is reported alongside.
Sampling check: 2000 draws, u = hash_uniform(f"bass_check|{i}") at slot 0 with chg drawn from its empirical downbeat rate
(u = hash_uniform(f"bass_check|{i}|chg")); PASS iff |sampled root-pc fraction - corpus downbeat root-pc fraction| <= 0.15.
FD-1: the check is recorded, never tuned. No PRNG (SHA-256 inverse-CDF only). No sidecar_nonfactor. No VST3 state APIs.
Exports (pure, side-effect free): analyze_song, build_model, run_sampling_check, sample_interval_class, interval_to_pitch.
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
CLASS_ORDER = ("root", "fifth", "octave", "third", "approach", "other")
PRECEDENCE = "approach > root > fifth > third > octave > other (root = non-octave root-pc case; see definitions)"
ALPHA = 0.5
N_CHECK = 2000
TOL = 0.15
GM_BASS_LO, GM_BASS_HI = 28, 60
DEFAULT_OUT = "data/v5/rules/bass_pitch_v5.json"
DEFAULT_ELIGIBLE = "data/v5/rules/eligible_c84.json"
DEFAULT_CORPUS = "data/v5/corpus"
DEFAULT_PER_SONG = "data/v5/rules/per_song_c84"
DEFAULT_GROOVE = "data/v5/rules/groove_v5_v2_full.json"
PREREG = "data/v5/gen/f2_prereg_c86.json"


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def hash_uniform(tag: str) -> float:
    """SHA-256 inverse-CDF driver (identical to scripts.v5.groove_v5_v2.hash_uniform, READ-ONLY there)."""
    return int(hashlib.sha256(tag.encode()).hexdigest()[:16], 16) / float(1 << 64)


def percentile(xs: list[int], q: float) -> float:
    s = sorted(xs)
    if not s:
        return 0.0
    pos = (len(s) - 1) * q
    lo, hi = int(pos // 1), min(int(pos // 1) + 1, len(s) - 1)
    return round(s[lo] + (s[hi] - s[lo]) * (pos - lo), 6)


# ----------------------------------------------------------------------------------------------------------------------
# pure analysis
# ----------------------------------------------------------------------------------------------------------------------
def _segments(chords: dict[int, dict]) -> dict[int, int]:
    """beat -> segment id (maximal run of consecutive beats with the same non-null root)."""
    seg, sid, prev = {}, -1, None
    for b in sorted(chords):
        r = chords[b].get("root")
        if r is None or chords[b].get("state") == "N":
            prev = None
            continue
        if prev is None or prev[0] != b - 1 or prev[1] != r:
            sid += 1
        seg[b] = sid
        prev = (b, r)
    return seg


def classify(pitch: int, root: int, next_root: int | None, chg: bool, seg_low_root: int | None) -> str:
    pc = pitch % 12
    if chg and next_root is not None and (pc - next_root) % 12 in (1, 2, 10, 11):
        return "approach"
    iv = (pc - root) % 12
    if iv == 0:
        return "octave" if seg_low_root is not None and pitch >= seg_low_root + 12 else "root"
    if iv == 7:
        return "fifth"
    if iv in (3, 4):
        return "third"
    return "other"


def analyze_song(onsets: list[tuple[int, int]], chord_stream: list[dict], phase_offset: int = 0) -> dict:
    """onsets = [(tick, pitch)], chord_stream = [{beat, root, quality, state}], phase_offset in 16th slots.
    Returns event records + register; no I/O."""
    chords = {int(c["beat"]): c for c in chord_stream}
    seg = _segments(chords)
    seg_low: dict[int, int] = {}
    for tick, pitch in onsets:
        b = tick // PPQ
        if b in seg and pitch % 12 == chords[b]["root"] % 12:
            seg_low[seg[b]] = min(seg_low.get(seg[b], 10 ** 9), pitch)
    events, skipped = [], 0
    for tick, pitch in sorted(onsets):
        b = tick // PPQ
        c = chords.get(b)
        if c is None or c.get("root") is None or c.get("state") == "N":
            skipped += 1
            continue
        root = int(c["root"]) % 12
        nxt = chords.get(b + 1)
        next_root = None if nxt is None or nxt.get("root") is None or nxt.get("state") == "N" else int(nxt["root"]) % 12
        chg = next_root is not None and next_root != root
        slot = (tick % PPQ) // TICKS_16TH
        cls = classify(pitch, root, next_root, chg, seg_low.get(seg.get(b, -1)))
        events.append({
            "slot": slot, "chg": int(chg), "cls": cls, "pitch": pitch, "root_pc": int(pitch % 12 == root),
            "downbeat_aligned": int((tick // TICKS_16TH - phase_offset) % 16 == 0),
            "downbeat_raw": int(b % 4 == 0 and slot == 0),
        })
    pitches = [p for _, p in onsets]
    register = {
        "n": len(pitches), "median": percentile(pitches, 0.5), "p25": percentile(pitches, 0.25),
        "p75": percentile(pitches, 0.75), "min": min(pitches) if pitches else None, "max": max(pitches) if pitches else None,
    }
    register["iqr_lo"], register["iqr_hi"] = register["p25"], register["p75"]
    return {"events": events, "n_onsets": len(onsets), "n_used": len(events), "n_skipped_null_chord": skipped,
            "register": register, "phase_offset": phase_offset}


def _row(counts: dict[str, int]) -> dict:
    n = sum(counts.values())
    return {"n": n, "counts": {c: counts.get(c, 0) for c in CLASS_ORDER},
            "probs": {c: round((counts.get(c, 0) + ALPHA) / (n + ALPHA * len(CLASS_ORDER)), 9) for c in CLASS_ORDER}}


def _frac(num: int, den: int) -> float | None:
    return round(num / den, 9) if den else None


def build_model(per_song: dict[str, dict]) -> dict:
    cond: dict[str, dict[str, int]] = {f"{s}|{c}": {} for s in range(4) for c in (0, 1)}
    marg: dict[str, int] = {}
    db_a = {"n": 0, "root_pc": 0, "root_cls": 0, "chg": 0}
    db_r = {"n": 0, "root_pc": 0, "root_cls": 0, "chg": 0}
    n_chg = 0
    ps_out, all_pitches = {}, []
    for sha, a in sorted(per_song.items()):
        cnt: dict[str, int] = {}
        s_db = {"n": 0, "root_pc": 0}
        for e in a["events"]:
            k = f"{e['slot']}|{e['chg']}"
            cond[k][e["cls"]] = cond[k].get(e["cls"], 0) + 1
            marg[e["cls"]] = marg.get(e["cls"], 0) + 1
            cnt[e["cls"]] = cnt.get(e["cls"], 0) + 1
            n_chg += e["chg"]
            for flag, db in (("downbeat_aligned", db_a), ("downbeat_raw", db_r)):
                if e[flag]:
                    db["n"] += 1
                    db["root_pc"] += e["root_pc"]
                    db["root_cls"] += int(e["cls"] == "root")
                    db["chg"] += e["chg"]
            if e["downbeat_aligned"]:
                s_db["n"] += 1
                s_db["root_pc"] += e["root_pc"]
        all_pitches.extend(e["pitch"] for e in a["events"])
        ps_out[sha] = {
            "n_onsets": a["n_onsets"], "n_used": a["n_used"], "n_skipped_null_chord": a["n_skipped_null_chord"],
            "counts": {c: cnt.get(c, 0) for c in CLASS_ORDER}, "register": a["register"],
            "phase_offset": a["phase_offset"], "n_downbeat_onsets": s_db["n"],
            "downbeat_root_pc_fraction": _frac(s_db["root_pc"], s_db["n"]),
        }
    n_all = sum(marg.values())

    def db_block(db: dict) -> dict:
        return {"n_onsets": db["n"], "root_pc_fraction": _frac(db["root_pc"], db["n"]),
                "root_class_only_fraction": _frac(db["root_cls"], db["n"]), "chord_change_rate": _frac(db["chg"], db["n"])}

    medians = [ps_out[s]["register"]["median"] for s in ps_out if ps_out[s]["register"]["n"]]
    return {
        "class_order": list(CLASS_ORDER), "precedence": PRECEDENCE, "alpha": ALPHA,
        "conditional": {k: _row(v) for k, v in sorted(cond.items())},
        "marginal": _row(marg),
        "chord_change_rate": {"all": _frac(n_chg, n_all)},
        "downbeat": {
            "definition": "aligned: (tick//120 - groove phase_offset) % 16 == 0; raw: beat index % 4 == 0 and slot == 0 (offset 0)",
            "aligned": db_block(db_a), "raw": db_block(db_r),
        },
        "register": {
            "corpus": {"n": len(all_pitches), "median": percentile(all_pitches, 0.5), "iqr_lo": percentile(all_pitches, 0.25),
                       "iqr_hi": percentile(all_pitches, 0.75)},
            "median_of_song_medians": percentile([int(round(m)) for m in medians], 0.5) if medians else None,
        },
        "per_song": ps_out,
        "n_events": n_all,
        "n_onsets_total": sum(a["n_onsets"] for a in per_song.values()),
        "n_skipped_null_chord_total": sum(a["n_skipped_null_chord"] for a in per_song.values()),
    }


# ----------------------------------------------------------------------------------------------------------------------
# exported samplers (pure)
# ----------------------------------------------------------------------------------------------------------------------
def sample_interval_class(model: dict, slot: int, chord_change: bool, u: float) -> str:
    """Inverse-CDF over the smoothed row "<slot>|<chg>" in fixed class order; falls back to the marginal row."""
    row = model.get("conditional", {}).get(f"{int(slot) % 4}|{int(bool(chord_change))}") or model["marginal"]
    probs = row["probs"]
    order = model.get("class_order", list(CLASS_ORDER))
    acc = 0.0
    for c in order:
        acc += probs[c]
        if u < acc:
            return c
    return order[-1]


def _place(pc: int, register: dict, anchor: float | None = None) -> int:
    lo, hi = int(round(register["iqr_lo"])), int(round(register["iqr_hi"]))
    lo, hi = max(GM_BASS_LO, min(lo, hi)), min(GM_BASS_HI, max(lo, hi))
    a = register["median"] if anchor is None else anchor
    cands = [p for p in range(lo, hi + 1) if p % 12 == pc % 12]
    if not cands:
        cands = [p for p in range(GM_BASS_LO, GM_BASS_HI + 1) if p % 12 == pc % 12]
    return min(cands, key=lambda p: (abs(p - a), p))


def interval_to_pitch(cls: str, root_pc: int, next_root_pc: int | None, register: dict, u: float) -> int:
    """register = {median, iqr_lo, iqr_hi}. root/fifth/third/octave relative to root_pc placed in [iqr_lo, iqr_hi] nearest the
    median (octave = root placement + 12 when <= 60, else the root placement); approach = next_root_pc placement - {1, 2}
    by u (below the target root; None next root -> root); third = major (4) if u < 0.5 else minor (3);
    other = pc root+2 if u < 0.5 else root+9. Always clipped to GM bass 28..60."""
    root_pc %= 12
    if cls == "approach" and next_root_pc is not None:
        p = _place(next_root_pc, register) - (1 if u < 0.5 else 2)
    elif cls == "fifth":
        p = _place(root_pc + 7, register)
    elif cls == "third":
        p = _place(root_pc + (4 if u < 0.5 else 3), register)
    elif cls == "octave":
        r = _place(root_pc, register)
        p = r + 12 if r + 12 <= GM_BASS_HI else r
    elif cls == "other":
        p = _place(root_pc + (2 if u < 0.5 else 9), register)
    else:  # root, or approach without a next root
        p = _place(root_pc, register)
    return max(GM_BASS_LO, min(GM_BASS_HI, int(p)))


def run_sampling_check(model: dict, n: int = N_CHECK) -> dict:
    db = model["downbeat"]["aligned"]
    chg_rate = db["chord_change_rate"] if db["chord_change_rate"] is not None else 0.0
    cnt = {c: 0 for c in CLASS_ORDER}
    for i in range(n):
        chg = hash_uniform(f"bass_check|{i}|chg") < chg_rate
        cnt[sample_interval_class(model, 0, chg, hash_uniform(f"bass_check|{i}"))] += 1
    root_pc = (cnt["root"] + cnt["octave"]) / n
    corpus = db["root_pc_fraction"]
    diff = None if corpus is None else round(abs(root_pc - corpus), 9)
    raw = model["downbeat"]["raw"]["root_pc_fraction"]
    return {
        "n": n, "tag_format": "bass_check|{i} (class) and bass_check|{i}|chg (chord-change flag)", "context": "slot 0",
        "chg_rate_used": chg_rate, "sampled_class_counts": cnt, "sampled_root_pc_fraction": round(root_pc, 9),
        "sampled_root_class_only_fraction": round(cnt["root"] / n, 9),
        "corpus_downbeat_root_pc_fraction": corpus, "abs_diff": diff, "tol": TOL,
        "pass": bool(diff is not None and diff <= TOL),
        "raw_grid_informational": {"corpus_downbeat_root_pc_fraction": raw,
                                   "abs_diff": None if raw is None else round(abs(root_pc - raw), 9),
                                   "within_tol": bool(raw is not None and abs(root_pc - raw) <= TOL)},
    }


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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--eligible-from", default=DEFAULT_ELIGIBLE)
    ap.add_argument("--corpus-dir", default=DEFAULT_CORPUS)
    ap.add_argument("--per-song-dir", default=DEFAULT_PER_SONG)
    ap.add_argument("--groove", default=DEFAULT_GROOVE)
    a = ap.parse_args()
    elig_p = _WS / a.eligible_from
    songs = json.loads(elig_p.read_text())["gate"]["used"]
    groove_p = _WS / a.groove
    groove = json.loads(groove_p.read_text()).get("per_song", {}) if groove_p.exists() else {}
    per_song, disclosures, inputs = {}, [], {}
    for sha in songs:
        bass_p = _WS / a.corpus_dir / sha / "canonical_v5_reindexed" / "bass.mid"
        harm_p = _WS / a.per_song_dir / sha / "harmony_v5.json"
        harm = json.loads(harm_p.read_text())
        off = groove.get(sha, {}).get("phase", {}).get("offset")
        if off is None:
            disclosures.append(f"{sha}: no groove phase offset in {a.groove}; downbeat alignment offset 0 used")
            off = 0
        per_song[sha] = analyze_song(midi_onsets(bass_p), harm["chord_stream"], int(off))
        inputs[sha] = {"bass_mid_sha256": sha_file(bass_p), "harmony_v5_sha256": sha_file(harm_p), "bpm_v5": harm.get("bpm_v5")}
    model = build_model(per_song)
    check = run_sampling_check(model)
    disclosures += [
        "octave = pc == chord root AND pitch >= lowest root-pc bass note of the chord segment + 12 (measurable from the "
        "corpus, so the median+6 fallback was not needed); the literal precedence root > octave would leave octave empty, "
        "so root is defined as the non-octave root-pc case",
        "chord_change_flag is 0 when the next beat is null/'N' or past the end of chord_stream",
        "approach receives alpha smoothing mass in chg=0 rows (alpha over all 6 classes per pre-reg); interval_to_pitch "
        "maps approach with next_root_pc=None to the root placement",
        "downbeat for the sampling check = groove-aligned grid (phase_offset from groove_v5_v2_full.json); the conditional "
        "slot is the raw tick grid, so the raw-grid downbeat fraction is reported informationally too",
        "sampled root fraction counts root + octave (root pitch class) against the corpus root-pc fraction; root-class-only "
        "figures are reported alongside",
        "third at sampling = major (4) if u < 0.5 else minor (3): chord quality is not part of the export signature",
    ]
    out = {
        "schema_version": 1, "cycle": 86, "agent": "worker", "run_id": "run-2026-09-06T000000Z",
        "milestone": "M-V5-GEN-1/F2-bass-melody-dynamics", "kind": "bass_pitch_model_v5",
        "env_pin_sha256": ENV_PIN_SHA256, "prereg_path": PREREG, "prereg_sha256": sha_file(_WS / PREREG),
        "script_sha256": sha_file(Path(__file__).resolve()),
        "eligible_from": a.eligible_from, "eligible_sha256": sha_file(elig_p), "n_songs": len(songs), "songs": list(songs),
        "inputs": inputs, "groove_path": a.groove, "groove_sha256": sha_file(groove_p) if groove_p.exists() else None,
        "definitions": {
            "beat": "tick // 480", "slot": "(tick % 480) // 120 in 0..3", "chord": "chord_stream[beat]; null root / state 'N' skipped",
            "chord_change_flag": "next beat exists with non-null root != current root",
            "approach": "pc within +/-1 or +/-2 semitones of the NEXT chord root, only when chord_change_flag",
            "root": "pc == root and not octave", "fifth": "(pc - root) % 12 == 7", "third": "(pc - root) % 12 in {3, 4}",
            "octave": "pc == root and pitch >= lowest root-pc bass note of the chord segment + 12",
            "other": "remaining onsets", "conditional_key": "<slot>|<chg>",
            "smoothing": "probs = (count + 0.5) / (n + 0.5 * 6) over class_order",
            "register": "per song median / p25 (iqr_lo) / p75 (iqr_hi) of bass MIDI pitches (linear-interpolated percentiles)",
            "gm_bass_range": [GM_BASS_LO, GM_BASS_HI],
        },
        **model,
        "sampling_check": check,
        "fd1": "recorded, not tuned",
        "disclosures": disclosures,
    }
    out_p = Path(a.out) if Path(a.out).is_absolute() else _WS / a.out
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out_p} sha256={sha_file(out_p)} n_events={model['n_events']} "
          f"downbeat_root_pc={model['downbeat']['aligned']['root_pc_fraction']} sampled={check['sampled_root_pc_fraction']} "
          f"pass={check['pass']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
