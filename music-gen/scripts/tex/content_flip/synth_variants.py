#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T14:10:00Z
# cycle: 14
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel/embedding/content-flip-analysis
# ---
"""Deterministic 10-s synthetic content variants for the M-TEX-1/panel/
embedding content-flip sweep.

Two axes, four variants each (8 total):

  Polyphony (P1..P4)
    P1  monophonic bass          — GM 33 (Acoustic Bass), quarter notes in C2-C3
    P2  bass + piano             — P1 + GM 1 (Piano) harmonizing a 5th above
    P3  P2 + drums               — GM standard drum kit (channel 10), kick+snare
    P4  P3 + other (piano triad) — extra piano voice in C5-C6

  Envelope (E1..E4)
    E1  sustained sine chords    — GM 79 (Whistle) whole-note stacked chords
    E2  decaying triad           — GM 1 (Piano) single C-E-G triad, quick decay
    E3  percussion-heavy         — drum kit only, dense kick+snare+hihat
    E4  harmonic-sustained-only  — GM 49 (String Ensemble) sustained chords

Duration: 10 s @ 44.1 kHz stereo (matches cycle-13 panel scale conventions
where possible; cycle-13 stage-by-stage measured 30 s / 50 s / 60 s but the
panel operates on any length).

SF2 sha 74594e8f...1cb0 is asserted before rendering (M-SEP-1 pin).
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Iterable

assert sys.executable == "/usr/bin/python3", sys.executable

import numpy as np
import soundfile as sf
import scipy.io.wavfile as scipy_wav
from music21 import stream, note, chord, tempo, meter, instrument, midi as m21midi

SF2_EXPECTED_SHA = (
    "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
)
SF2_DEFAULT = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
DURATION_S = 10.0
SR = 44100

VARIANTS = ("P1", "P2", "P3", "P4", "E1", "E2", "E3", "E4")
AXIS_OF = {
    "P1": "polyphony", "P2": "polyphony", "P3": "polyphony", "P4": "polyphony",
    "E1": "envelope",  "E2": "envelope",  "E3": "envelope",  "E4": "envelope",
}
# 1..4 rank within its axis (for sweep ordering).
RANK_OF = {
    "P1": 1, "P2": 2, "P3": 3, "P4": 4,
    "E1": 1, "E2": 2, "E3": 3, "E4": 4,
}


def _assert_sf2(sf2_path: Path) -> None:
    h = hashlib.sha256(sf2_path.read_bytes()).hexdigest()
    if h != SF2_EXPECTED_SHA:
        raise RuntimeError(
            f"SF2 sha mismatch on {sf2_path}: got {h}, expected "
            f"{SF2_EXPECTED_SHA}. Refusing to render (M-SEP-1 pin).")


# ----- MIDI construction (music21) ------------------------------------

def _bass_part(dur_beats: int) -> stream.Part:
    """P1 monophonic bass: quarter notes stepping in C2-C3, GM 33."""
    p = stream.Part()
    p.insert(0, instrument.AcousticBass())  # -> GM prog ~33
    pitches = ["C2", "E2", "G2", "C3", "G2", "E2"]
    for i in range(dur_beats):
        n = note.Note(pitches[i % len(pitches)])
        n.quarterLength = 1.0
        p.append(n)
    return p


def _piano_part(dur_beats: int, register: str = "mid") -> stream.Part:
    """Piano harmonizing 5ths above the bass root, quarter notes."""
    p = stream.Part()
    p.insert(0, instrument.Piano())  # -> GM prog 0/1
    if register == "mid":
        pitches = ["G4", "B4", "D5", "G5", "D5", "B4"]
    else:  # "high"
        pitches = ["C5", "E5", "G5", "C6", "G5", "E5"]
    for i in range(dur_beats):
        n = note.Note(pitches[i % len(pitches)])
        n.quarterLength = 1.0
        p.append(n)
    return p


def _drums_part(dur_beats: int, mode: str = "kick_snare") -> stream.Part:
    """Drum backbeat on channel 10 (GM percussion).

    music21 emits drums by placing UnpitchedPercussion on a part with an
    instrument.Percussion(). For clarity + broadest FluidSynth compatibility
    we use pitched notes on midi channel 10 explicitly via the raw pitch
    numbers (kick=35, snare=38, closed hat=42, open hat=46).
    """
    p = stream.Part()
    perc = instrument.Percussion()
    perc.midiChannel = 9  # channel 10 in 1-indexed MIDI
    p.insert(0, perc)
    for i in range(dur_beats):
        if mode == "kick_snare":
            # kick on 1&3, snare on 2&4
            pitch_num = 35 if (i % 2 == 0) else 38
            n = note.Note()
            n.pitch.midi = pitch_num
            n.volume.velocity = 100
            n.quarterLength = 1.0
            p.append(n)
        elif mode == "dense":
            # 8th-note kick+snare+hihat pattern
            for eighth in range(2):
                if eighth == 0:
                    pitch_num = 35 if (i % 2 == 0) else 38
                else:
                    pitch_num = 42  # closed hat
                n = note.Note()
                n.pitch.midi = pitch_num
                n.volume.velocity = 100
                n.quarterLength = 0.5
                p.append(n)
        else:
            raise ValueError(f"unknown drum mode {mode!r}")
    return p


def _other_piano_part(dur_beats: int) -> stream.Part:
    """Extra piano voice — high triads."""
    p = stream.Part()
    p.insert(0, instrument.Piano())
    for i in range(dur_beats):
        c = chord.Chord(["C5", "E5", "G5"])
        c.quarterLength = 1.0
        p.append(c)
    return p


def _sustained_sine_part(n_whole_notes: int) -> stream.Part:
    """E1 sustained sine-like chords via GM 79 (Whistle) — sinusoidal patch."""
    p = stream.Part()
    inst = instrument.Whistle()  # GM 79
    p.insert(0, inst)
    for i in range(n_whole_notes):
        c = chord.Chord(["C4", "E4", "G4", "B4", "D5"])
        c.quarterLength = 4.0  # whole notes
        p.append(c)
    return p


def _decaying_triad_part(n_beats: int) -> stream.Part:
    """E2 decaying C-E-G triad via piano — short attacks + rapid decay.

    Piano's natural envelope decays; short quarterLength on each hit.
    """
    p = stream.Part()
    p.insert(0, instrument.Piano())
    for i in range(n_beats):
        c = chord.Chord(["C4", "E4", "G4"])
        c.quarterLength = 1.0  # each triad rings ~1 beat before next
        p.append(c)
    return p


def _sustained_strings_part(n_whole_notes: int) -> stream.Part:
    """E4 harmonic sustained: GM 49 String Ensemble whole-note chords."""
    p = stream.Part()
    p.insert(0, instrument.StringInstrument())  # music21 maps to strings
    for i in range(n_whole_notes):
        c = chord.Chord(["C4", "E4", "G4", "C5"])
        c.quarterLength = 4.0
        p.append(c)
    return p


def build_variant_score(variant_id: str) -> stream.Score:
    """Return a music21 Score for `variant_id`."""
    if variant_id not in VARIANTS:
        raise ValueError(f"unknown variant {variant_id!r}")

    # 10 s @ 120 BPM => 20 beats
    beats = 20
    whole_notes = 5  # 5 x 4-beat wholes = 20 beats
    s = stream.Score()
    s.insert(0, tempo.MetronomeMark(number=120))
    s.insert(0, meter.TimeSignature("4/4"))

    if variant_id == "P1":
        s.insert(0, _bass_part(beats))
    elif variant_id == "P2":
        s.insert(0, _bass_part(beats))
        s.insert(0, _piano_part(beats))
    elif variant_id == "P3":
        s.insert(0, _bass_part(beats))
        s.insert(0, _piano_part(beats))
        s.insert(0, _drums_part(beats, mode="kick_snare"))
    elif variant_id == "P4":
        s.insert(0, _bass_part(beats))
        s.insert(0, _piano_part(beats))
        s.insert(0, _drums_part(beats, mode="kick_snare"))
        s.insert(0, _other_piano_part(beats))
    elif variant_id == "E1":
        s.insert(0, _sustained_sine_part(whole_notes))
    elif variant_id == "E2":
        s.insert(0, _decaying_triad_part(beats))
    elif variant_id == "E3":
        s.insert(0, _drums_part(beats, mode="dense"))
    elif variant_id == "E4":
        s.insert(0, _sustained_strings_part(whole_notes))
    return s


# ----- Deterministic MIDI serialization -------------------------------

def _score_to_midi_bytes(score: stream.Score) -> bytes:
    """Convert a music21 score to a byte-deterministic MIDI blob."""
    mf = m21midi.translate.streamToMidiFile(score)
    return mf.writestr()


def write_midi(variant_id: str, out_midi_path: Path) -> None:
    s = build_variant_score(variant_id)
    blob = _score_to_midi_bytes(s)
    out_midi_path.parent.mkdir(parents=True, exist_ok=True)
    out_midi_path.write_bytes(blob)


# ----- Fluidsynth invocation ------------------------------------------

def _fluidsynth_render(midi_path: Path, out_wav_path: Path,
                      sf2_path: Path, sr: int = SR,
                      duration_s: float = DURATION_S) -> None:
    """Deterministic fluidsynth render; matches M-SEP-1 ground-truth flags."""
    _assert_sf2(sf2_path)
    tmp = out_wav_path.with_suffix(".raw.wav")
    if tmp.exists():
        tmp.unlink()
    if out_wav_path.exists():
        out_wav_path.unlink()
    cmd = [
        "fluidsynth", "-a", "null", "-T", "wav",
        "-F", str(tmp),
        "-r", str(sr),
        "-g", "1.0",
        "-i",
        str(sf2_path), str(midi_path),
    ]
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    y, got_sr = sf.read(str(tmp), always_2d=True)
    if got_sr != sr:
        raise RuntimeError(f"expected sr={sr}, got {got_sr}")
    if y.shape[1] == 1:
        y = np.concatenate([y, y], axis=1)
    n_target = int(round(duration_s * sr))
    if y.shape[0] < n_target:
        pad = np.zeros((n_target - y.shape[0], y.shape[1]), dtype=y.dtype)
        y = np.concatenate([y, pad], axis=0)
    else:
        y = y[:n_target]
    scipy_wav.write(str(out_wav_path), sr, y.astype(np.float32))
    tmp.unlink()


def render_variant(variant_id: str, out_dir: Path,
                   sf2_path: Path = SF2_DEFAULT,
                   duration_s: float = DURATION_S) -> Path:
    """Build MIDI + render bare WAV for `variant_id` into `out_dir`.

    Returns the path to the rendered bare_midi.wav.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    midi_path = out_dir / "variant.mid"
    wav_path = out_dir / "bare_midi.wav"
    write_midi(variant_id, midi_path)
    _fluidsynth_render(midi_path, wav_path, sf2_path,
                       sr=SR, duration_s=duration_s)
    return wav_path


def render_all(out_root: Path, sf2_path: Path = SF2_DEFAULT) -> dict:
    """Render all 8 variants; return a dict of {variant_id: bare_wav_path}."""
    out = {}
    for v in VARIANTS:
        out[v] = render_variant(v, out_root / v, sf2_path=sf2_path)
    return out
