"""
Note-level F1 evaluation for M-TRANS-1.

For every (transcriber ∈ {basic_pitch, alternative}) × (mix) × (stem):
- load reference JSONL from data/transcribe/reference/<mix>/<stem>.reference.jsonl
- load estimate JSONL from data/transcribe/<transcriber>/<mix>/<stem>.jsonl
- compute mir_eval.transcription.precision_recall_f1_overlap with
    onset_tolerance = 0.05 s
    offset_ratio    = 0.20
    offset_min_tolerance = 0.05 s
    pitch_tolerance = 50 cents (0.5 semitones)
- for drums, use the same call but pitch equality on GM drum notes.

Writes:
  data/transcribe/results.tsv
  data/transcribe/results_bar_chart.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import mir_eval

assert sys.executable == "/usr/bin/python3", f"interpreter guard: {sys.executable}"

ROOT = Path("/home/user/long-exposure-runs/music-gen")
REF_ROOT = ROOT / "data/transcribe/reference"
BP_ROOT = ROOT / "data/transcribe/basic_pitch"
ALT_ROOT = ROOT / "data/transcribe/alternative"
OUT_TSV = ROOT / "data/transcribe/results.tsv"
OUT_PNG = ROOT / "data/transcribe/results_bar_chart.png"

MIXES = ["synth_030s", "synth_060s", "synth_090s"]
STEMS = ["drums", "bass", "other"]

ONSET_TOL_S = 0.05
OFFSET_RATIO = 0.20
OFFSET_MIN_TOL_S = 0.05


def load_jsonl(path: Path) -> list[dict]:
    if not path.is_file() or path.stat().st_size == 0:
        return []
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def to_arrays(rows: list[dict]):
    if not rows:
        return np.zeros((0, 2)), np.array([])
    intervals = np.array([[r["onset_s"], r["offset_s"]] for r in rows], dtype=float)
    pitches = np.array([r["pitch"] for r in rows], dtype=float)
    return intervals, pitches


def eval_pair(ref: list[dict], est: list[dict], is_drum: bool):
    ref_iv, ref_p = to_arrays(ref)
    est_iv, est_p = to_arrays(est)

    if len(ref) == 0 and len(est) == 0:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "overlap": 1.0}
    if len(ref) == 0:
        return {"precision": 0.0, "recall": 1.0, "f1": 0.0, "overlap": 0.0}
    if len(est) == 0:
        return {"precision": 1.0, "recall": 0.0, "f1": 0.0, "overlap": 0.0}

    # mir_eval uses Hz. Convert MIDI pitch to Hz. For drums, treat drum
    # note numbers as-is (unique integer identity) by leaving them in
    # MIDI space and using a very tight pitch_tolerance in Hz-space:
    # instead compute F1 with a large offset_ratio (drums are ~0.1s hits).
    if is_drum:
        # Convert drum MIDI numbers to fake Hz for identity: 100 Hz per unit.
        # mir_eval requires positive frequencies; identity match iff same pitch.
        ref_hz = 100.0 + ref_p  # e.g. 136 for kick=36
        est_hz = 100.0 + est_p
        # pitch_tolerance small enough that only exact GM-drum match passes.
        # 0.5 in Hz over a 100-Hz base is looser than a semitone, but the
        # candidate hits are integer-spaced, so it's fine.
        pitch_tol = 0.5
    else:
        ref_hz = mir_eval.util.midi_to_hz(ref_p)
        est_hz = mir_eval.util.midi_to_hz(est_p)
        pitch_tol = 50.0  # cents

    # Guard against zero-duration intervals which mir_eval rejects; add
    # a tiny epsilon to offset if offset <= onset.
    eps = 1e-4
    for iv in (ref_iv, est_iv):
        bad = iv[:, 1] <= iv[:, 0]
        if bad.any():
            iv[bad, 1] = iv[bad, 0] + eps

    p, r, f, o = mir_eval.transcription.precision_recall_f1_overlap(
        ref_iv, ref_hz, est_iv, est_hz,
        onset_tolerance=ONSET_TOL_S,
        pitch_tolerance=pitch_tol,
        offset_ratio=OFFSET_RATIO,
        offset_min_tolerance=OFFSET_MIN_TOL_S,
    )
    return {"precision": float(p), "recall": float(r), "f1": float(f), "overlap": float(o)}


def main() -> None:
    rows = []
    header = ["transcriber", "mix", "stem", "precision", "recall", "f1",
              "avg_overlap_ratio", "notes_ref", "notes_est", "disclaimer"]
    for tr, tr_root in (("basic_pitch", BP_ROOT), ("alternative", ALT_ROOT)):
        for mix in MIXES:
            for stem in STEMS:
                ref = load_jsonl(REF_ROOT / mix / f"{stem}.reference.jsonl")
                est = load_jsonl(tr_root / mix / f"{stem}.jsonl")
                is_drum = (stem == "drums")
                m = eval_pair(ref, est, is_drum)
                disclaimer = ""
                if tr == "basic_pitch" and stem == "drums":
                    disclaimer = "basic-pitch is polyphonic-pitch-oriented; F1 on drums is a LOWER BOUND."
                rows.append({
                    "transcriber": tr, "mix": mix, "stem": stem,
                    "precision": m["precision"], "recall": m["recall"],
                    "f1": m["f1"], "avg_overlap_ratio": m["overlap"],
                    "notes_ref": len(ref), "notes_est": len(est),
                    "disclaimer": disclaimer,
                })

    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TSV.open("w") as fh:
        fh.write("\t".join(header) + "\n")
        for r in rows:
            fh.write("\t".join([
                r["transcriber"], r["mix"], r["stem"],
                f"{r['precision']:.4f}", f"{r['recall']:.4f}", f"{r['f1']:.4f}",
                f"{r['avg_overlap_ratio']:.4f}",
                str(r["notes_ref"]), str(r["notes_est"]),
                r["disclaimer"],
            ]) + "\n")
    print(f"wrote {OUT_TSV}")

    # Bar chart: F1 per (transcriber, stem), averaged across the three mixes.
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        transcribers = ["basic_pitch", "alternative"]
        stems = STEMS
        means = {t: [] for t in transcribers}
        for t in transcribers:
            for s in stems:
                vals = [r["f1"] for r in rows if r["transcriber"] == t and r["stem"] == s]
                means[t].append(sum(vals) / len(vals) if vals else 0.0)
        x = np.arange(len(stems))
        w = 0.35
        fig, ax = plt.subplots(figsize=(6.5, 4.0))
        ax.bar(x - w / 2, means["basic_pitch"], w, label="basic_pitch 0.4.0")
        ax.bar(x + w / 2, means["alternative"], w, label="alternative (librosa)")
        ax.set_xticks(x)
        ax.set_xticklabels(stems)
        ax.set_ylabel("F1 (mean over 30/60/90 s)")
        ax.set_title("M-TRANS-1: note-level F1 per (transcriber, stem)")
        ax.set_ylim(0, 1)
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUT_PNG, dpi=120)
        print(f"wrote {OUT_PNG}")
    except Exception as e:
        print(f"bar chart skipped: {e}")


if __name__ == "__main__":
    main()
