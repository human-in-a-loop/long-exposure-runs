#!/usr/bin/python3
"""c81 P3 — reindex fidelity cross-check (M-3), pre-declared.

created: 2026-09-06T17:05:00Z
cycle: 81
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/reindex-fidelity-c81

Inputs (both READ-ONLY):
  A. WIG full-length lossless canonical MIDI data/v5/corpus/252eb21ce7df7328/canonical_v5_reindexed/<stem>.mid
     (c80 re-index; serialized at bpm_v5 99.384) restricted to t in [72.77133, 102.77133] s and re-based to 0.
  B. c21 single-chunk operator-section canonical MIDI
     data/v3_spine/252eb21ce7df7328/operator_section/canonical_midi/<stem>.mid (serialized at 50.174 BPM —
     collision-free by construction because a 30 s section is one chunk).
Both are converted to SECONDS through their own tempo meta (mido), so the different serialization tempi cancel.

Two pre-declared statistics per stem (separated because starts are lossless but the section was transcribed from
a different audio slice):
  (a) onset F1 at +/-50 ms with pitch equality (primary; pitch-agnostic F1 reported as a diagnostic) — measures
      transcription agreement between the full-length chunked run and the single-chunk section run;
  (b) on matched onsets only, |duration_A - duration_B| — measures the greedy start/end pairing fidelity.
Verdict (pre-declared in the c81 brief):
  REINDEX_FIDELITY_HOLDS     iff median |dDuration| <= 75 ms (1/8 beat at 99.384) on EVERY stem with >= 20 matched onsets
  REINDEX_FIDELITY_DEGRADED  if any such stem exceeds 75 ms
  TRANSCRIPTION_MISMATCH_INCONCLUSIVE if onset F1 < 0.60 on ALL pitched stems (then (b) has no support)
Matching: greedy nearest-onset among same-pitch unmatched candidates, reference = section (B), deterministic.
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs; nothing written under READ-ONLY dirs.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

import mido  # noqa: E402

_WS = Path(__file__).resolve().parent.parent.parent
ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
WIG = "252eb21ce7df7328"
T0, T1 = 72.77133, 102.77133
TOL_ONSET_S = 0.050
TOL_DUR_S = 0.075
MIN_MATCHED = 20
F1_INCONCLUSIVE = 0.60
STEMS = ("drums", "bass", "guitar", "other", "piano", "vocals", "full_mix")
PITCHED = ("bass", "guitar", "other", "piano", "vocals", "full_mix")


def notes_seconds(path: Path) -> list[tuple[float, float, int]]:
    """(onset_s, duration_s, pitch) via the file's own tempo meta (mido merged iteration yields seconds)."""
    m = mido.MidiFile(str(path))
    t = 0.0
    open_: dict[tuple[int, int], list[float]] = {}
    notes = []
    for msg in m:  # merged tracks, delta times in seconds
        t += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            open_.setdefault((msg.channel, msg.note), []).append(t)
        elif msg.type in ("note_off", "note_on"):
            k = (msg.channel, msg.note)
            if open_.get(k):
                t0 = open_[k].pop(0)
                if t > t0:
                    notes.append((t0, t - t0, msg.note))
    notes.sort()
    return notes


def match(ref: list, cand: list, pitch_equal: bool) -> list[tuple[int, int]]:
    """Greedy nearest-onset matching: for each ref note (sorted), the closest unmatched cand note within TOL (same pitch if required)."""
    used = set()
    pairs = []
    by_pitch: dict[int | None, list[int]] = {}
    for j, (o, d, p) in enumerate(cand):
        by_pitch.setdefault(p if pitch_equal else None, []).append(j)
    for i, (o, d, p) in enumerate(ref):
        best = None
        for j in by_pitch.get(p if pitch_equal else None, []):
            if j in used:
                continue
            dt = abs(cand[j][0] - o)
            if dt <= TOL_ONSET_S and (best is None or dt < best[0] or (dt == best[0] and j < best[1])):
                best = (dt, j)
        if best is not None:
            used.add(best[1])
            pairs.append((i, best[1]))
    return pairs


def f1(n_ref: int, n_cand: int, n_match: int) -> float | None:
    if n_ref == 0 or n_cand == 0:
        return None
    p, r = n_match / n_cand, n_match / n_ref
    return round(2 * p * r / (p + r), 6) if (p + r) > 0 else 0.0


def pairing_ambiguity(stem: str) -> dict:
    """Diagnostic (not part of the verdict): for the full-length starts inside the window, how many had MORE than one
    candidate end (same chunk-local start_event_index, end > start, span <= 30 s) in the raw MuScriptor JSON — i.e.
    where the c80 greedy pairing could have mis-assigned a duration — versus exactly one (unambiguous)."""
    raw = json.loads(Path(f"data/v5/corpus/{WIG}/muscriptor_full/{stem}.json").read_text())
    ends: dict[int, list[float]] = {}
    for e in raw:
        if e.get("type") == "end":
            ends.setdefault(int(e["start_event_index"]), []).append(float(e["end_time"]))
    n_amb = n_one = n_zero = 0
    for e in raw:
        if e.get("type") != "start" or not (T0 <= float(e["start_time"]) < T1):
            continue
        st = float(e["start_time"])
        c = sum(1 for et in ends.get(int(e["index"]), []) if st < et <= st + 30.0)
        if c == 0:
            n_zero += 1
        elif c == 1:
            n_one += 1
        else:
            n_amb += 1
    n = n_amb + n_one + n_zero
    return {"n_starts_in_window": n, "n_unambiguous_one_end": n_one, "n_ambiguous_multi_end": n_amb, "n_no_end": n_zero,
            "ambiguous_fraction": round(n_amb / n, 6) if n else None}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/v5/corpus/252eb21ce7df7328/reindex_fidelity_c81.json")
    args = ap.parse_args()
    os.chdir(_WS)
    full_dir = Path(f"data/v5/corpus/{WIG}/canonical_v5_reindexed")
    sec_dir = Path(f"data/v3_spine/{WIG}/operator_section/canonical_midi")
    tm = json.loads(Path(f"data/v5/corpus/{WIG}/transcription_manifest.json").read_text())
    per_stem = {}
    for stem in STEMS:
        A = [(o - T0, d, p) for (o, d, p) in notes_seconds(full_dir / f"{stem}.mid") if T0 <= o < T1]
        B = notes_seconds(sec_dir / f"{stem}.mid")
        pairs = match(B, A, pitch_equal=True)
        pairs_any = match(B, A, pitch_equal=False)
        ddur = sorted(abs(A[j][1] - B[i][1]) for i, j in pairs)
        rec = {"n_full_in_window": len(A), "n_section": len(B), "n_matched_pitch": len(pairs), "n_matched_any_pitch": len(pairs_any),
               "onset_f1_pitch": f1(len(B), len(A), len(pairs)), "onset_f1_any_pitch": f1(len(B), len(A), len(pairs_any)),
               "dduration_median_s": round(statistics.median(ddur), 6) if ddur else None,
               "dduration_p90_s": round(ddur[int(0.9 * (len(ddur) - 1))], 6) if ddur else None,
               "dduration_mean_s": round(sum(ddur) / len(ddur), 6) if ddur else None,
               "eligible_for_duration_bound": len(pairs) >= MIN_MATCHED,
               "median_dduration_within_75ms": (statistics.median(ddur) <= TOL_DUR_S) if len(pairs) >= MIN_MATCHED else None,
               "duration_median_full_s": round(statistics.median(d for _o, d, _p in A), 6) if A else None,
               "duration_median_section_s": round(statistics.median(d for _o, d, _p in B), 6) if B else None,
               "pairing_ambiguity_diagnostic": pairing_ambiguity(stem)}
        per_stem[stem] = rec
    pitched_f1 = [per_stem[s]["onset_f1_pitch"] for s in PITCHED if per_stem[s]["onset_f1_pitch"] is not None]
    eligible = [s for s in STEMS if per_stem[s]["eligible_for_duration_bound"]]
    if pitched_f1 and all(v < F1_INCONCLUSIVE for v in pitched_f1):
        verdict = "TRANSCRIPTION_MISMATCH_INCONCLUSIVE"
    elif eligible and all(per_stem[s]["median_dduration_within_75ms"] for s in eligible):
        verdict = "REINDEX_FIDELITY_HOLDS"
    elif eligible:
        verdict = "REINDEX_FIDELITY_DEGRADED"
    else:
        verdict = "TRANSCRIPTION_MISMATCH_INCONCLUSIVE"
    out = {"schema_version": 1, "cycle": 81, "sha16": WIG, "env_pin_sha256": ENV_PIN_SHA256,
           "inputs": {"full_length_reindexed_dir": str(full_dir), "full_length_bpm_v5": tm["bpm_v5"],
                      "section_canonical_dir": str(sec_dir), "section_window_s": [T0, T1],
                      "note": "both converted to seconds via their own tempo meta; section MIDI serialized at 50.174 BPM (c20 drums-stem anchor), full-length at bpm_v5"},
           "pre_declared": {"onset_tolerance_s": TOL_ONSET_S, "duration_tolerance_s": TOL_DUR_S, "min_matched_onsets": MIN_MATCHED,
                            "f1_inconclusive_below": F1_INCONCLUSIVE, "primary_f1": "pitch-equal greedy nearest-onset", "pitched_stems": list(PITCHED),
                            "enum": ["REINDEX_FIDELITY_HOLDS", "REINDEX_FIDELITY_DEGRADED", "TRANSCRIPTION_MISMATCH_INCONCLUSIVE"]},
           "per_stem": per_stem, "stems_eligible_for_duration_bound": eligible, "verdict": verdict}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(f"VERDICT {verdict}; eligible stems {eligible}")
    for s in STEMS:
        r = per_stem[s]
        print(f"  {s:8s} full_in_win={r['n_full_in_window']:4d} section={r['n_section']:4d} matched(pitch)={r['n_matched_pitch']:4d} "
              f"F1(pitch)={r['onset_f1_pitch']} F1(any)={r['onset_f1_any_pitch']} med|dDur|={r['dduration_median_s']} p90={r['dduration_p90_s']} "
              f"medDur full/sec={r['duration_median_full_s']}/{r['duration_median_section_s']} amb={r['pairing_ambiguity_diagnostic']['ambiguous_fraction']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
