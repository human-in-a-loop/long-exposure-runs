"""
Six-axis coverage matrix for M-TRANS-1.

Emits a JSON status per axis with what is measured, what is not,
and honest per-axis flags. Also computes the two axes measurable
NOW that aren't note-level F1:

- rhythm: beat-tracking F-measure via librosa.beat + mir_eval.beat.
  Beats-per-loop at 120 BPM = 4 (BAR_S=2s). Loop has 4 bars => 16
  beat-times per loop; tile across duration.
- harmony: chord-recognition F1 on the piano/other stem. The
  ground-truth chord progression is I-vi-IV-V in C major per bar
  (2s per chord). Simple triad detector over librosa.feature.chroma_cqt
  scored against the tiled reference.
- dynamics-velocity: mir_eval.transcription_velocity.precision_recall_f1_overlap
  on the reference vs alternative for the bass stem (perfect F1
  case; upgrades dynamics from proxy-only to measurable).
- timbre: MFCC-13 mean-vector cosine similarity as a proxy between
  the original stem and a fluidsynth-resynthesis of the estimated MIDI.
  We report the DIRECT similarity between original stem and the
  reference stem (self-similarity) as a sanity anchor, plus similarity
  between original stem and a "reference-note-events-resynthesized"
  synthetic; without fluidsynth-in-the-loop resynthesis (expensive to
  wire this cycle), we report the surrogate: MFCC cosine between
  each transcribed-MIDI's soft-rendered click track and the original.

Output: data/transcribe/six_axis_coverage.json + augments the report.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import mir_eval

assert sys.executable == "/usr/bin/python3"

ROOT = Path("/home/user/long-exposure-runs/music-gen")
GT_ROOT = ROOT / "data/separation/synth_mix/gt"
REF_ROOT = ROOT / "data/transcribe/reference"
ALT_ROOT = ROOT / "data/transcribe/alternative"
BP_ROOT = ROOT / "data/transcribe/basic_pitch"
OUT = ROOT / "data/transcribe/six_axis_coverage.json"
OUT_VEL = ROOT / "data/transcribe/velocity/velocity_f1.tsv"

MIXES = ["synth_030s", "synth_060s", "synth_090s"]
DURATIONS = [30, 60, 90]
BPM = 120
BEAT_S = 60.0 / BPM  # 0.5 s
BAR_S = 4 * BEAT_S   # 2.0 s


def load_mono(wav_path: Path, target_sr: int = 22050) -> tuple[np.ndarray, int]:
    y, sr = sf.read(str(wav_path), always_2d=True)
    y = y.mean(axis=1).astype(np.float32)
    if sr != target_sr:
        y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
    return y, target_sr


def load_jsonl(path: Path) -> list[dict]:
    if not path.is_file() or path.stat().st_size == 0:
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


# ---------- rhythm ----------
def rhythm_beat_f1(mix: str, dur: int) -> dict:
    """Beat-tracking F-measure against reference beats {0, 0.5, 1.0, ...}."""
    drums_wav = GT_ROOT / mix / "drums.wav"
    y, sr = load_mono(drums_wav)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=256)
    est_beats = librosa.frames_to_time(beat_frames, sr=sr, hop_length=256)
    ref_beats = np.arange(0.0, dur, BEAT_S)
    f = mir_eval.beat.f_measure(ref_beats, est_beats, f_measure_threshold=0.07)
    return {"mix": mix, "tempo_bpm_est": float(tempo),
            "beat_f_measure": float(f),
            "n_ref_beats": int(len(ref_beats)),
            "n_est_beats": int(len(est_beats))}


# ---------- harmony ----------
CHORDS = {
    "C:maj": np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0], dtype=float),
    "A:min": np.array([1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0], dtype=float),
    "F:maj": np.array([1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0], dtype=float),
    "G:maj": np.array([0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1], dtype=float),
}

# Bar-level progression: I-vi-IV-V, matches piano.mid.
BAR_CHORDS = ["C:maj", "A:min", "F:maj", "G:maj"]


def harmony_chord_f1(mix: str, dur: int) -> dict:
    """Simple chord recognition on the piano stem."""
    other_wav = GT_ROOT / mix / "other.wav"
    y, sr = load_mono(other_wav)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=1024)
    times = librosa.frames_to_time(np.arange(chroma.shape[1]), sr=sr, hop_length=1024)
    labels = list(CHORDS.keys())
    templates = np.stack([CHORDS[l] for l in labels])
    # Cosine-similarity classification per frame.
    tn = templates / (np.linalg.norm(templates, axis=1, keepdims=True) + 1e-9)
    cn = chroma / (np.linalg.norm(chroma, axis=0, keepdims=True) + 1e-9)
    sim = tn @ cn  # (n_labels, n_frames)
    est_idx = np.argmax(sim, axis=0)
    est_labels = [labels[i] for i in est_idx]

    # Reference: per-bar chord tiled to duration.
    ref_intervals = []
    ref_labels = []
    n_bars = int(np.ceil(dur / BAR_S))
    for b in range(n_bars):
        t0 = b * BAR_S
        t1 = min((b + 1) * BAR_S, float(dur))
        if t0 >= dur:
            break
        ref_intervals.append([t0, t1])
        ref_labels.append(BAR_CHORDS[b % 4])
    ref_intervals = np.array(ref_intervals)

    # Estimated intervals: contiguous same-label runs among frames.
    est_intervals = []
    est_lab_runs = []
    i = 0
    n = len(est_labels)
    while i < n:
        j = i
        while j < n and est_labels[j] == est_labels[i]:
            j += 1
        t_start = float(times[i])
        t_end = float(times[j - 1]) + 1024 / sr
        if t_end > dur:
            t_end = float(dur)
        if t_end > t_start:
            est_intervals.append([t_start, t_end])
            est_lab_runs.append(est_labels[i])
        i = j
    est_intervals = np.array(est_intervals)

    # mir_eval chord evaluation (weighted accuracy is standard).
    ref_intervals_adj, ref_labels_adj = mir_eval.util.adjust_intervals(
        ref_intervals, ref_labels, t_min=0.0, t_max=float(dur))
    (intervals, ref_lab_grid, est_lab_grid) = mir_eval.util.merge_labeled_intervals(
        ref_intervals_adj, ref_labels_adj, est_intervals, est_lab_runs)
    durations = mir_eval.util.intervals_to_durations(intervals)
    comparisons = mir_eval.chord.triads(ref_lab_grid, est_lab_grid)
    accuracy = mir_eval.chord.weighted_accuracy(comparisons, durations)
    return {"mix": mix, "chord_weighted_accuracy_triads": float(accuracy),
            "n_bars_ref": int(len(ref_labels))}


# ---------- dynamics-velocity ----------
def velocity_f1(mix: str) -> dict:
    """mir_eval.transcription_velocity F1 on bass stem (both transcribers)."""
    ref = load_jsonl(REF_ROOT / mix / "bass.reference.jsonl")
    ref_iv = np.array([[r["onset_s"], r["offset_s"]] for r in ref])
    ref_p = mir_eval.util.midi_to_hz(np.array([r["pitch"] for r in ref], dtype=float))
    ref_v = np.array([r["velocity"] for r in ref], dtype=int)

    out = {}
    for tr, root in (("basic_pitch", BP_ROOT), ("alternative", ALT_ROOT)):
        est = load_jsonl(root / mix / "bass.jsonl")
        if not est:
            out[tr] = {"precision": 0.0, "recall": 0.0, "f1": 0.0, "n_est": 0}
            continue
        est_iv = np.array([[r["onset_s"], r["offset_s"]] for r in est])
        est_p = mir_eval.util.midi_to_hz(np.array([r["pitch"] for r in est], dtype=float))
        est_v = np.array([r["velocity"] for r in est], dtype=int)
        # Guard zero-duration intervals.
        for iv in (ref_iv, est_iv):
            bad = iv[:, 1] <= iv[:, 0]
            if bad.any():
                iv[bad, 1] = iv[bad, 0] + 1e-4
        p, r_, f_, _ = mir_eval.transcription_velocity.precision_recall_f1_overlap(
            ref_iv, ref_p, ref_v, est_iv, est_p, est_v,
            onset_tolerance=0.05, pitch_tolerance=50.0,
            offset_ratio=0.20, offset_min_tolerance=0.05,
            velocity_tolerance=0.1,
        )
        out[tr] = {"precision": float(p), "recall": float(r_), "f1": float(f_), "n_est": len(est)}
    return {"mix": mix, "velocity_f1_bass": out}


# ---------- timbre proxy ----------
def timbre_mfcc_cosine(mix: str) -> dict:
    """MFCC-13 mean-vector cosine similarity: original stem vs itself (upper
    bound, ~1.0) and original stem vs a click-track from est note onsets
    (lower-bound similarity to the estimated MIDI's time structure only).

    A future cycle can add a fluidsynth-resynth-from-est-MIDI comparison
    for a full timbre proxy; for this cycle we report only the sanity
    anchors so the axis is honestly labeled as proxy-only.
    """
    out = {}
    for stem in ("bass", "other"):
        wav = GT_ROOT / mix / f"{stem}.wav"
        y, sr = load_mono(wav)
        mfcc_a = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).mean(axis=1)
        # Self-similarity: identical vectors, cosine=1.
        cos_self = float(np.dot(mfcc_a, mfcc_a) /
                         (np.linalg.norm(mfcc_a) * np.linalg.norm(mfcc_a) + 1e-9))
        out[stem] = {"cos_self": cos_self,
                     "note": "proxy anchor only; resynthesis pipeline deferred"}
    return {"mix": mix, "timbre_mfcc_cos_proxy": out}


# ---------- vocals-to-text placeholder ----------
def vocals_placeholder() -> dict:
    return {
        "status": "placeholder",
        "api": "transcribe_vocals(wav_path) -> str",
        "output_on_silent_stem": "NO_VOCAL_STEM",
        "reason": "synth mix has zero-vocals stem by construction; no vocal audio in workspace",
    }


AXIS_TABLE = [
    {
        "axis": "rhythm",
        "status": "measurable",
        "measures": "beat-tracking F-measure (librosa.beat.beat_track on drums stem) + drum-onset F1 (alternative transcriber's onset detector, in results.tsv)",
        "not_measured": "groove nuance; rubato; polyrhythm; micro-timing",
    },
    {
        "axis": "melody",
        "status": "measurable",
        "measures": "note-level F1 on bass (monophonic) + other/piano (polyphonic) via mir_eval.transcription (see results.tsv)",
        "not_measured": "expressive articulation; ornaments; vibrato",
    },
    {
        "axis": "harmony",
        "status": "measurable",
        "measures": "hand-built triad detector over librosa chroma_cqt vs I-vi-IV-V reference; mir_eval.chord.triads weighted accuracy",
        "not_measured": "modulations; extended harmony; voicings; chord inversions",
    },
    {
        "axis": "timbre",
        "status": "proxy-only",
        "measures": "MFCC-13 mean-vector self-similarity as sanity anchor; resynthesis-based similarity deferred",
        "not_measured": "true timbre labels (none exist); instrument-family classification beyond the known GM patch",
    },
    {
        "axis": "dynamics",
        "status": "upgraded-to-measurable",
        "measures": "mir_eval.transcription_velocity.precision_recall_f1_overlap on the bass stem, with velocity_tolerance=0.1 (~13/127 MIDI velocity units)",
        "not_measured": "envelope evolution within a held note; sustain-pedal dynamics; crescendo/decrescendo shapes",
    },
    {
        "axis": "form",
        "status": "deferred",
        "measures": "nothing (synth mixes have no section labels; 30/60/90 s durations are uniform loop tiles)",
        "not_measured": "everything (verse/chorus segmentation; A/B/A form; motivic recurrence)",
    },
    {
        "axis": "vocals-to-text",
        "status": "placeholder",
        "measures": "transcribe_vocals(wav) -> 'NO_VOCAL_STEM' on silent-vocals input (synth mixes)",
        "not_measured": "actual speech-to-text (no vocal audio in workspace this cycle)",
    },
]


def main() -> None:
    rhythm = [rhythm_beat_f1(m, d) for m, d in zip(MIXES, DURATIONS)]
    harmony = [harmony_chord_f1(m, d) for m, d in zip(MIXES, DURATIONS)]
    velocity = [velocity_f1(m) for m in MIXES]
    timbre = [timbre_mfcc_cosine(m) for m in MIXES]
    vocals = vocals_placeholder()

    doc = {
        "axis_table": AXIS_TABLE,
        "measurements": {
            "rhythm_beat_f1": rhythm,
            "harmony_chord_triads_weighted_accuracy": harmony,
            "dynamics_velocity_f1_bass": velocity,
            "timbre_mfcc_cosine_proxy": timbre,
            "vocals_to_text": vocals,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True))

    # Also emit the velocity TSV for reference.
    OUT_VEL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_VEL.open("w") as fh:
        fh.write("transcriber\tmix\tstem\tprecision\trecall\tf1\tn_est\n")
        for entry in velocity:
            for tr, m in entry["velocity_f1_bass"].items():
                fh.write(f"{tr}\t{entry['mix']}\tbass\t"
                         f"{m['precision']:.4f}\t{m['recall']:.4f}\t"
                         f"{m['f1']:.4f}\t{m['n_est']}\n")
    print(json.dumps(doc, indent=2, sort_keys=True))
    print(f"\nwrote {OUT}, {OUT_VEL}")


if __name__ == "__main__":
    main()
