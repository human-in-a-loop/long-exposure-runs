#!/usr/bin/env python3
# ------------------------------------------------------------------
# c12 Track 2 primary: CG drums family-2 stem-sampled builder.
#
# Sibling to c5/c6 family2_stem_sampled_builder.py (bass; READ-ONLY
# per c11 anchor block).  Drums-specific adaptations per the c12
# research brief:
#
#   * Onset detect on drums stem via librosa.onset.onset_detect
#     (units='samples', backtrack=True) — drums are transient-rich.
#   * Fixed 400 ms slices per onset (NOT ≥6 s slices as bass used).
#   * NO pitch-shift — drums have kit-slot semantics, not pitch
#     semantics.  Sample bank indexed by (band-energy) drum-class.
#   * Render via concatenative synthesis on drums.mid at the source
#     sample rate, splicing per-note samples from bank (deterministic
#     k-th occurrence selection; no PRNG).
#
# Public API:
#     render(ref_stem_path: Path, midi_path: Path, out_wav: Path,
#            *, sample_rate: int|None = None) -> dict
#
# Family-2 IS a distinct RENDER FAMILY from sf2 per FD-16(c) — needs
# its own per-song replay proof (see family2_stem_sampled_drums_replay.py).
#
# created: 2026-09-04
# cycle: 12
# run_id: run-2026-09-04T000000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-drums-family2-stem-sampled
# ------------------------------------------------------------------

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# Env pins (7-key canonical) applied at import time for determinism.
for _k, _v in {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}.items():
    os.environ.setdefault(_k, _v)

import librosa  # noqa: E402
import mido  # noqa: E402
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402

_WORKSPACE = Path(__file__).resolve().parents[2]

# GM channel-10 percussion pitch -> drum class.  Any pitch not listed
# defaults to hihat (a safe non-silent fallback for auxiliary notes).
PITCH_TO_CLASS: Dict[int, str] = {
    35: "kick", 36: "kick",
    37: "snare", 38: "snare", 39: "snare", 40: "snare",
    41: "kick", 43: "kick", 45: "snare", 47: "snare",
    48: "snare", 50: "snare",  # toms — treat as snare timbre
    42: "hihat", 44: "hihat", 46: "hihat",
    49: "hihat", 51: "hihat", 52: "hihat", 53: "hihat",
    55: "hihat", 57: "hihat", 59: "hihat",
}


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def classify_slice(x: np.ndarray, sr: int) -> str:
    """Band-energy argmax classifier: {kick, snare, hihat}."""
    S = np.abs(librosa.stft(x, n_fft=1024, hop_length=256))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=1024)
    e_low = float(S[freqs < 300].sum())
    e_mid = float(S[(freqs >= 300) & (freqs < 2000)].sum())
    e_hi = float(S[freqs >= 2000].sum())
    tot = e_low + e_mid + e_hi + 1e-9
    frac = {"kick": e_low / tot, "snare": e_mid / tot, "hihat": e_hi / tot}
    return max(frac, key=frac.get)


def build_sample_bank(
    ref_stem_path: Path, *, window_ms: int = 400,
) -> Tuple[Dict[str, List[np.ndarray]], int, dict]:
    """Extract per-class sample bank from the reference drums stem."""
    y, sr = librosa.load(str(ref_stem_path), sr=None, mono=True)
    onset_samples = librosa.onset.onset_detect(
        y=y, sr=sr, units="samples", backtrack=True)
    win_n = int(sr * window_ms / 1000)
    bank: Dict[str, List[np.ndarray]] = defaultdict(list)
    for s in onset_samples:
        seg = y[int(s):int(s) + win_n]
        if seg.size < win_n // 2:
            continue
        # Pad short trailing segment with zeros so every sample is same
        # length (simplifies splicing).
        if seg.size < win_n:
            seg = np.concatenate([seg, np.zeros(win_n - seg.size,
                                                dtype=np.float32)])
        c = classify_slice(seg, sr)
        bank[c].append(seg.astype(np.float32))
    # Ensure every class has at least one sample; fallback to hihat.
    for cls in ("kick", "snare", "hihat"):
        if cls not in bank or not bank[cls]:
            # Copy first hihat as fallback so the bank is total.
            if "hihat" in bank and bank["hihat"]:
                bank[cls] = [bank["hihat"][0]]
    diag = {
        "sample_rate": int(sr),
        "duration_s": round(float(len(y)) / sr, 4),
        "n_onsets": int(len(onset_samples)),
        "window_ms": window_ms,
        "class_counts": {k: len(v) for k, v in bank.items()},
    }
    return dict(bank), int(sr), diag


def _midi_note_events(midi_path: Path) -> List[Tuple[float, int, int]]:
    """Return sorted (time_s, pitch, channel) for note_on with vel>0."""
    mid = mido.MidiFile(str(midi_path))
    tempo_us = 500000  # default 120 BPM until set_tempo appears.
    ticks_per_beat = mid.ticks_per_beat
    events: List[Tuple[float, int, int]] = []
    # Absolute-time computation per track requires processing each track
    # in isolation, then merging.  For a monolithic drum MIDI (as in
    # this campaign) all note_on live on one track with a shared tempo
    # meta at t=0, so a single-track pass suffices.  If additional
    # tempo events appear we honour them.
    for track in mid.tracks:
        now_ticks = 0
        for msg in track:
            now_ticks += msg.time
            if msg.type == "set_tempo":
                tempo_us = msg.tempo
            elif msg.type == "note_on" and msg.velocity > 0:
                t_s = mido.tick2second(
                    now_ticks, ticks_per_beat, tempo_us)
                events.append((t_s, msg.note, msg.channel))
    events.sort(key=lambda e: (e[0], e[1]))
    return events


def render(
    ref_stem_path: Path,
    midi_path: Path,
    out_wav: Path,
    *,
    sample_rate: int | None = None,
    window_ms: int = 400,
) -> dict:
    """Concatenative render.

    Deterministic sample selection:  for the k-th occurrence of a note
    with class C, use bank[C][k % len(bank[C])].  No PRNG.
    """
    bank, sr, diag = build_sample_bank(ref_stem_path, window_ms=window_ms)
    if sample_rate is not None and sample_rate != sr:
        raise ValueError(
            f"stem sr={sr}, requested sr={sample_rate}, no resample")

    events = _midi_note_events(midi_path)
    # Compute output duration = max(event onset + slice window, stem
    # duration).  Round up to sample boundary.
    win_n = int(sr * window_ms / 1000)
    max_event_end = max(
        (int(t * sr) + win_n for t, _, _ in events), default=0)
    out_n = max(max_event_end, int(diag["duration_s"] * sr))
    out = np.zeros(out_n, dtype=np.float32)

    # Per-class occurrence counter for deterministic bank indexing.
    per_pitch_k = Counter()
    used_pitches = Counter()
    per_class_uses = Counter()
    for t_s, pitch, ch in events:
        cls = PITCH_TO_CLASS.get(pitch, "hihat")
        used_pitches[pitch] += 1
        k = per_pitch_k[(cls, pitch)]
        per_pitch_k[(cls, pitch)] += 1
        per_class_uses[cls] += 1
        samples = bank.get(cls, bank.get("hihat", []))
        if not samples:
            continue
        seg = samples[k % len(samples)]
        pos = int(t_s * sr)
        end = pos + seg.size
        if end > out.size:
            # Extend the buffer (rare with the max-end computation above,
            # but a safety net for MIDI events past stem end).
            new_out = np.zeros(end, dtype=np.float32)
            new_out[: out.size] = out
            out = new_out
        out[pos:end] += seg

    # Soft peak-limit to avoid inter-sample overshoot from concatenative
    # summing.  Deterministic linear rescale iff peak > 0.99.
    peak = float(np.max(np.abs(out))) if out.size else 0.0
    if peak > 0.99:
        out = out * (0.99 / peak)

    out_wav.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_wav), out, sr, subtype="PCM_16")
    render_sha = _sha256_file(out_wav)

    return {
        "render_sha256": render_sha,
        "sample_rate": int(sr),
        "output_samples": int(out.size),
        "peak_abs": peak,
        "n_midi_events": len(events),
        "per_class_uses": dict(per_class_uses),
        "used_pitches": {int(k): v for k, v in used_pitches.items()},
        "bank_diagnostics": diag,
    }


def main() -> int:
    ref_stem = (
        _WORKSPACE
        / "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/drums.wav"
    )
    midi = (
        _WORKSPACE
        / "data/v4/profiles/31a164f845f8e27e/"
        / "drums_sweep_stage1/drums_excerpt.mid"
    )
    out_dir = (
        _WORKSPACE
        / "data/v4/profiles/31a164f845f8e27e/drums_family2_render"
    )
    out_wav = out_dir / "render.wav"
    r = render(ref_stem, midi, out_wav)
    manifest = {
        "schema_version": "v1.0",
        "milestone_id": (
            "M-V4-PROFILES-1/cg-drums-family2-stem-sampled/render"),
        "cycle": 12,
        "ref_stem_path": str(ref_stem.relative_to(_WORKSPACE)),
        "ref_stem_sha256": _sha256_file(ref_stem),
        "midi_path": str(midi.relative_to(_WORKSPACE)),
        "midi_sha256": _sha256_file(midi),
        "out_wav_path": str(out_wav.relative_to(_WORKSPACE)),
        **r,
    }
    (out_dir / "render_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(
        {"render_sha256": r["render_sha256"],
         "peak_abs": r["peak_abs"],
         "n_events": r["n_midi_events"],
         "per_class_uses": r["per_class_uses"],
         "bank_class_counts": r["bank_diagnostics"]["class_counts"]},
        indent=2))
    print(f"WROTE {out_wav}")
    print(f"WROTE {out_dir / 'render_manifest.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
