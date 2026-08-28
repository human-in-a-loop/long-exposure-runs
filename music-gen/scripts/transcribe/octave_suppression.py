"""M-TRANS-1/basic-pitch/octave-suppression — post-processing filter.

Removes octave-doubled note events from basic-pitch outputs. On monophonic
bass lines, basic-pitch's CQT frontend often fires simultaneously at the
fundamental ``p`` and its first overtone ``p+12`` because the +12 partial
has significant CQT energy relative to the neural onset threshold. This
filter identifies such pairs by their co-onset + co-sustain signature and
keeps only the more-confident (higher-velocity) partner.

The cycle-6 JSONL schema is:
    {is_drum: bool, onset_s: float, offset_s: float, pitch: int, velocity: int}

There is no ``confidence`` field; ``velocity`` is the confidence proxy
(basic-pitch's ``model_output_to_notes`` maps note-amplitude to MIDI
velocity, so velocity is monotone in note confidence).

Public API
----------
suppress_octaves(notes, t_min_ms, overlap_min) -> (kept, suppressed)

CLI (optional)
--------------
    /usr/bin/python3 scripts/transcribe/octave_suppression.py \\
        --in data/transcribe/basic_pitch/synth_030s/bass.jsonl \\
        --out /tmp/bass_filtered.jsonl \\
        --t-min-ms 100 --overlap-min 0.5

Isolation contract: does NOT import scripts.classifier.sidecar_nonfactor.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

assert sys.executable == "/usr/bin/python3", f"wrong interpreter: {sys.executable}"

# Co-onset window (seconds). Tighter than mir_eval's 50 ms onset tolerance
# on purpose — otherwise we would collapse notes the evaluator treats as
# distinct. Not a grid axis this cycle; documented as a future refinement.
CO_ONSET_S = 0.025


class OctaveSuppressionError(ValueError):
    """Raised on schema violations or degenerate note geometry."""


def _validate(note: dict) -> None:
    for key in ("onset_s", "offset_s", "pitch"):
        if key not in note:
            raise OctaveSuppressionError(f"missing field {key!r} in {note!r}")
    if float(note["offset_s"]) <= float(note["onset_s"]):
        raise OctaveSuppressionError(
            f"degenerate interval offset<=onset: {note!r}"
        )


def _confidence(note: dict) -> float:
    """Confidence proxy: velocity (int 0..127) → float. Missing → 0.0."""
    return float(note.get("velocity", 0))


def suppress_octaves(
    notes: Iterable[dict],
    t_min_ms: int,
    overlap_min: float,
) -> tuple[list[dict], list[dict]]:
    """Split ``notes`` into (kept, suppressed) by the octave-doubling rule.

    Algorithm
    ---------
    1. Sort notes by ``onset_s``.
    2. Group into co-onset buckets: two notes share a bucket if
       ``|onset(a) - onset(b)| <= CO_ONSET_S``.  Buckets are formed
       greedily on the sorted list, so a bucket may span slightly more
       than ``CO_ONSET_S`` when notes chain — this is intentional and
       matches how basic-pitch groups overlapping onsets.
    3. Within each bucket, enumerate all ordered pairs ``(a, b)`` where
       ``pitch(b) == pitch(a) + 12`` (b is the octave-up partner).
    4. For each pair, compute ``dur_min = min(dur_a, dur_b)`` and
       ``overlap_frac = overlap_s / dur_min``.
    5. The pair QUALIFIES for suppression IFF:
           ``dur_min * 1000 >= t_min_ms`` AND ``overlap_frac >= overlap_min``.
    6. Iterate qualified pairs in confidence-descending order (by the
       maximum-confidence member).  For each, decide the loser:
           - lower velocity loses,
           - tie → shorter duration loses,
           - tie → higher pitch loses (bass fundamental preference).
       Skip pairs where either member is already suppressed (never
       double-suppress).
    """
    notes_list = list(notes)
    for n in notes_list:
        _validate(n)

    if not notes_list:
        return [], []

    # Stable sort: primary onset, secondary pitch.
    indexed = sorted(
        enumerate(notes_list),
        key=lambda kv: (kv[1]["onset_s"], kv[1]["pitch"]),
    )

    # Build co-onset buckets on the sorted stream.
    buckets: list[list[int]] = []
    current: list[int] = []
    last_onset: float | None = None
    for original_idx, note in indexed:
        onset = float(note["onset_s"])
        if last_onset is None or onset - last_onset <= CO_ONSET_S:
            current.append(original_idx)
        else:
            buckets.append(current)
            current = [original_idx]
        last_onset = onset
    if current:
        buckets.append(current)

    # Enumerate candidate pairs.
    candidate_pairs: list[tuple[int, int, float]] = []
    for bucket in buckets:
        for i in bucket:
            ni = notes_list[i]
            for j in bucket:
                if i == j:
                    continue
                nj = notes_list[j]
                if int(nj["pitch"]) != int(ni["pitch"]) + 12:
                    continue
                dur_i = float(ni["offset_s"]) - float(ni["onset_s"])
                dur_j = float(nj["offset_s"]) - float(nj["onset_s"])
                dur_min = min(dur_i, dur_j)
                overlap = max(
                    0.0,
                    min(float(ni["offset_s"]), float(nj["offset_s"]))
                    - max(float(ni["onset_s"]), float(nj["onset_s"])),
                )
                if dur_min <= 0.0:
                    continue
                overlap_frac = overlap / dur_min
                if dur_min * 1000.0 < t_min_ms:
                    continue
                if overlap_frac < overlap_min:
                    continue
                priority = max(_confidence(ni), _confidence(nj))
                # Order canonicalized (low_pitch, high_pitch).
                candidate_pairs.append((i, j, priority))

    # Highest-confidence pair first; stable secondary keys for determinism.
    candidate_pairs.sort(
        key=lambda p: (
            -p[2],
            notes_list[p[0]]["onset_s"],
            notes_list[p[0]]["pitch"],
            notes_list[p[1]]["pitch"],
        )
    )

    suppressed_idx: set[int] = set()
    for i, j, _ in candidate_pairs:
        if i in suppressed_idx or j in suppressed_idx:
            continue
        ni, nj = notes_list[i], notes_list[j]
        ci, cj = _confidence(ni), _confidence(nj)
        di = float(ni["offset_s"]) - float(ni["onset_s"])
        dj = float(nj["offset_s"]) - float(nj["onset_s"])
        # Decide the loser.
        if ci != cj:
            loser = i if ci < cj else j
        elif di != dj:
            loser = i if di < dj else j
        else:
            # Duration tie: keep lower pitch (bass fundamental preference).
            loser = i if int(ni["pitch"]) > int(nj["pitch"]) else j
        suppressed_idx.add(loser)

    kept = [n for k, n in enumerate(notes_list) if k not in suppressed_idx]
    suppressed = [n for k, n in enumerate(notes_list) if k in suppressed_idx]
    return kept, suppressed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file() or path.stat().st_size == 0:
        return []
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")


def _main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", required=True)
    ap.add_argument("--out", dest="out_path", required=True)
    ap.add_argument("--t-min-ms", type=int, required=True)
    ap.add_argument("--overlap-min", type=float, required=True)
    args = ap.parse_args(argv)
    notes = _read_jsonl(Path(args.in_path))
    kept, suppressed = suppress_octaves(notes, args.t_min_ms, args.overlap_min)
    _write_jsonl(Path(args.out_path), kept)
    print(f"kept={len(kept)} suppressed={len(suppressed)} total={len(notes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
