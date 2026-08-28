"""
Alternative transcriber (librosa-family fallback) for M-TRANS-1.

Rationale: crepe pip install fails at metadata generation (HTTP 403
during setup.py's weight-fetch); magenta wheel fetches but its
onsets-frames checkpoint follows the same GCS path Crepe fails on
and its ~300 MB dep tree is disproportionate to this survey.
The librosa-family fallback is the honest alternative rung.

Distinct-from-basic-pitch pipeline choices:

- drums:  librosa.onset.onset_detect + spectral-centroid bins into
          GM drum note numbers {36 kick, 38 snare, 42 hihat} by
          low/mid/high sub-band energy. Onset time is the note event;
          duration fixed at 0.10 s (matches synth_gt.py drum notes).

- bass:   librosa.pyin monophonic pitch (C1-C4), quantized to nearest
          MIDI, then contiguous same-pitch runs become notes.

- other (piano/polyphonic): CQT peak-picking across time frames -
          for each frame, keep local maxima above a threshold in the
          chroma-aggregated CQT, group adjacent frames of the same
          pitch into notes.

Output canonical JSONL matches the reference schema:
  {pitch, onset_s, offset_s, velocity, is_drum}
sorted by (onset_s, pitch).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

assert sys.executable == "/usr/bin/python3", f"interpreter guard: {sys.executable}"

ROOT = Path("/home/user/long-exposure-runs/music-gen")
GT_ROOT = ROOT / "data/separation/synth_mix/gt"
OUT_ROOT = ROOT / "data/transcribe/alternative"
SR = 22050  # downsample from 44100 stereo to 22050 mono
MIXES = ["synth_030s", "synth_060s", "synth_090s"]

DRUM_HIT_DUR_S = 0.10


def load_mono(wav_path: Path) -> tuple[np.ndarray, int]:
    y, sr_native = sf.read(str(wav_path), always_2d=True)
    y = y.mean(axis=1)  # stereo -> mono
    if sr_native != SR:
        y = librosa.resample(y, orig_sr=sr_native, target_sr=SR)
    return y.astype(np.float32), SR


def transcribe_drums(y: np.ndarray, sr: int) -> list[dict]:
    """Onset detection + sub-band energy classification to GM drum notes."""
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=256,
                                              backtrack=False, units="frames")
    if len(onset_frames) == 0:
        return []
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=256)
    # Compute STFT once and classify each onset by sub-band energy in a
    # short window around it.
    n_fft = 1024
    hop = 256
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    # Bands: low <120 Hz kick; mid 200-1500 Hz snare; high >4000 Hz hihat.
    low_mask = freqs < 120
    mid_mask = (freqs >= 200) & (freqs <= 1500)
    high_mask = freqs > 4000

    notes = []
    for t, f in zip(onset_times, onset_frames):
        f0 = max(0, f - 1)
        f1 = min(S.shape[1], f + 4)
        seg = S[:, f0:f1].mean(axis=1)
        e_low = float(seg[low_mask].sum())
        e_mid = float(seg[mid_mask].sum())
        e_high = float(seg[high_mask].sum())
        # Argmax of the three bands = drum class.
        idx = int(np.argmax([e_low, e_mid, e_high]))
        pitch = {0: 36, 1: 38, 2: 42}[idx]  # kick / snare / hihat
        vel = 100 if pitch != 42 else 70
        notes.append({
            "pitch": pitch,
            "onset_s": round(float(t), 6),
            "offset_s": round(float(t) + DRUM_HIT_DUR_S, 6),
            "velocity": vel,
            "is_drum": True,
        })
    notes.sort(key=lambda r: (r["onset_s"], r["pitch"]))
    return notes


def transcribe_bass(y: np.ndarray, sr: int) -> list[dict]:
    """pyin monophonic pitch, quantize to MIDI, group same-pitch runs."""
    f0, voiced_flag, _ = librosa.pyin(
        y, sr=sr,
        fmin=librosa.note_to_hz("C1"),
        fmax=librosa.note_to_hz("C4"),
        frame_length=2048, hop_length=256,
    )
    if f0 is None:
        return []
    times = librosa.times_like(f0, sr=sr, hop_length=256)
    midi = np.where(np.isfinite(f0) & voiced_flag,
                    librosa.hz_to_midi(f0), np.nan)
    midi_int = np.where(np.isfinite(midi), np.round(midi), -1).astype(int)

    notes = []
    i = 0
    n = len(midi_int)
    MIN_FRAMES = 4  # ~46 ms
    while i < n:
        p = midi_int[i]
        if p < 0:
            i += 1
            continue
        j = i
        while j < n and midi_int[j] == p:
            j += 1
        if (j - i) >= MIN_FRAMES:
            onset = float(times[i])
            offset = float(times[j - 1] + 256 / sr)
            notes.append({
                "pitch": int(p),
                "onset_s": round(onset, 6),
                "offset_s": round(offset, 6),
                "velocity": 100,
                "is_drum": False,
            })
        i = j
    notes.sort(key=lambda r: (r["onset_s"], r["pitch"]))
    return notes


def transcribe_polyphonic(y: np.ndarray, sr: int) -> list[dict]:
    """CQT peak-picking per frame, then per-pitch contiguous runs -> notes."""
    hop = 512
    n_bins = 84  # 7 octaves
    fmin = librosa.note_to_hz("C1")
    C = np.abs(librosa.cqt(y, sr=sr, hop_length=hop, n_bins=n_bins, fmin=fmin))
    # Normalize per frame.
    C_db = librosa.amplitude_to_db(C, ref=np.max)
    # Peak-pick: keep bins > -30 dB relative and higher than neighbors.
    active = np.zeros_like(C, dtype=bool)
    thresh_db = -25.0
    for f in range(C_db.shape[1]):
        col = C_db[:, f]
        for b in range(1, len(col) - 1):
            if col[b] > thresh_db and col[b] > col[b - 1] and col[b] > col[b + 1]:
                active[b, f] = True
    # Group per-pitch contiguous runs -> notes; require >= 4 frames.
    times = librosa.frames_to_time(np.arange(C.shape[1]), sr=sr, hop_length=hop)
    notes = []
    midi_of_bin = np.arange(n_bins) + int(round(librosa.hz_to_midi(fmin)))
    MIN_FRAMES = 4
    for b in range(n_bins):
        active_frames = active[b]
        f = 0
        n = len(active_frames)
        while f < n:
            if not active_frames[f]:
                f += 1
                continue
            f_end = f
            while f_end < n and active_frames[f_end]:
                f_end += 1
            if (f_end - f) >= MIN_FRAMES:
                onset = float(times[f])
                offset = float(times[f_end - 1] + hop / sr)
                notes.append({
                    "pitch": int(midi_of_bin[b]),
                    "onset_s": round(onset, 6),
                    "offset_s": round(offset, 6),
                    "velocity": 85,
                    "is_drum": False,
                })
            f = f_end
    notes.sort(key=lambda r: (r["onset_s"], r["pitch"]))
    return notes


HANDLERS = {"drums": transcribe_drums, "bass": transcribe_bass, "other": transcribe_polyphonic}


def main() -> None:
    for mix in MIXES:
        for stem, handler in HANDLERS.items():
            wav = GT_ROOT / mix / f"{stem}.wav"
            y, sr = load_mono(wav)
            notes = handler(y, sr)
            out_dir = OUT_ROOT / mix
            out_dir.mkdir(parents=True, exist_ok=True)
            out_jsonl = out_dir / f"{stem}.jsonl"
            payload = "\n".join(
                json.dumps(r, sort_keys=True, separators=(",", ":")) for r in notes
            ) + "\n"
            out_jsonl.write_text(payload)
            print(f"[alt] {mix}/{stem}: {len(notes)} notes -> {out_jsonl}", flush=True)


if __name__ == "__main__":
    main()
