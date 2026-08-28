"""
M-SEP-1 ground-truth constructor.

Authors three GM MIDIs (drums / bass / piano) that repeat to cover
{30, 60, 90}s exactly, renders each with `fluidsynth` at 44.1 kHz stereo
through FluidR3_GM.sf2, and writes a peak-normalized (-3 dBFS) sum WAV
per duration bucket. All output paths, SHA-256s of MIDIs, SF2 SHA, and
sample counts are printed to stdout so the auditor can rerun and verify.

Determinism contract: same MIDI + same SF2 + same fluidsynth version =
bit-identical WAV. First-run SHA-256s are printed so a second run can
diff against them.

Interpreter: /usr/bin/python3 (asserted).
Invocation:
    /usr/bin/python3 scripts/separation/synth_gt.py

Outputs:
    data/separation/synth_mix/midi/{drums,bass,piano}.mid
    data/separation/synth_mix/gt/{mix_id}/{drums,bass,other,vocals}.wav
    data/separation/synth_mix/gt/{mix_id}/mix.wav
    data/separation/synth_mix/manifest.json
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pretty_midi
import soundfile as sf

assert sys.executable == "/usr/bin/python3", f"interpreter guard: {sys.executable}"

SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
SR = 44100
BPM = 120
BAR_S = 60.0 / BPM * 4.0  # 4/4 bar in seconds = 2.0 s
BARS_PER_LOOP = 4  # 4-bar phrase, 8.0 s
LOOP_S = BARS_PER_LOOP * BAR_S  # 8.0 s
DURATIONS = [30, 60, 90]

ROOT = Path("/home/user/long-exposure-runs/music-gen")
MIDI_DIR = ROOT / "data/separation/synth_mix/midi"
GT_ROOT = ROOT / "data/separation/synth_mix/gt"
MANIFEST = ROOT / "data/separation/synth_mix/manifest.json"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_midis() -> dict[str, Path]:
    """Author 4-bar (8 s @ 120 BPM) loops that concatenate cleanly to any duration."""
    MIDI_DIR.mkdir(parents=True, exist_ok=True)

    # DRUMS: kick on 1&3, snare on 2&4, hihat on every eighth. Channel 10.
    pm_drums = pretty_midi.PrettyMIDI(initial_tempo=BPM)
    drum_inst = pretty_midi.Instrument(program=0, is_drum=True, name="drums")
    for bar in range(BARS_PER_LOOP):
        t0 = bar * BAR_S
        # kick (36) on beats 1 & 3
        for beat in (0, 2):
            drum_inst.notes.append(pretty_midi.Note(
                velocity=110, pitch=36,
                start=t0 + beat * (BAR_S / 4), end=t0 + beat * (BAR_S / 4) + 0.10))
        # snare (38) on beats 2 & 4
        for beat in (1, 3):
            drum_inst.notes.append(pretty_midi.Note(
                velocity=100, pitch=38,
                start=t0 + beat * (BAR_S / 4), end=t0 + beat * (BAR_S / 4) + 0.10))
        # hihat (42) every eighth
        for eighth in range(8):
            drum_inst.notes.append(pretty_midi.Note(
                velocity=70, pitch=42,
                start=t0 + eighth * (BAR_S / 8), end=t0 + eighth * (BAR_S / 8) + 0.05))
    pm_drums.instruments.append(drum_inst)

    # BASS: root notes I-vi-IV-V in C major (C2 A1 F2 G2), one note per bar
    pm_bass = pretty_midi.PrettyMIDI(initial_tempo=BPM)
    bass_inst = pretty_midi.Instrument(program=33, name="bass")  # Electric Bass (finger)
    bass_roots = [36, 33, 41, 43]  # C2, A1, F2, G2
    for bar, pitch in enumerate(bass_roots):
        t0 = bar * BAR_S
        bass_inst.notes.append(pretty_midi.Note(
            velocity=100, pitch=pitch, start=t0, end=t0 + BAR_S * 0.95))
    pm_bass.instruments.append(bass_inst)

    # PIANO: block triads I-vi-IV-V in root position, one chord per bar
    pm_piano = pretty_midi.PrettyMIDI(initial_tempo=BPM)
    piano_inst = pretty_midi.Instrument(program=0, name="piano")  # Acoustic Grand
    chords = [(60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62)]
    for bar, chord in enumerate(chords):
        t0 = bar * BAR_S
        for pitch in chord:
            piano_inst.notes.append(pretty_midi.Note(
                velocity=85, pitch=pitch, start=t0, end=t0 + BAR_S * 0.95))
    pm_piano.instruments.append(piano_inst)

    paths = {}
    for name, pm in (("drums", pm_drums), ("bass", pm_bass), ("piano", pm_piano)):
        p = MIDI_DIR / f"{name}.mid"
        pm.write(str(p))
        paths[name] = p
    return paths


def render_stem(midi_path: Path, out_wav: Path, duration_s: int) -> None:
    """Render midi_path with fluidsynth to out_wav; then trim/pad to duration_s."""
    tmp = out_wav.with_suffix(".raw.wav")
    if tmp.exists():
        tmp.unlink()
    if out_wav.exists():
        out_wav.unlink()
    cmd = [
        "fluidsynth", "-a", "null", "-T", "wav",
        "-F", str(tmp),
        "-r", str(SR),
        "-g", "1.0",
        "-i",           # no interactive
        SF2, str(midi_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    y, sr = sf.read(str(tmp), always_2d=True)
    if sr != SR:
        raise RuntimeError(f"expected sr={SR}, got {sr}")
    if y.shape[1] == 1:
        y = np.concatenate([y, y], axis=1)  # promote mono to stereo
    # Tile the rendered loop until we cover >= duration_s + release tail (0.5 s).
    n_target = duration_s * SR
    n_loop = int(round(LOOP_S * SR))
    if y.shape[0] < n_loop:
        # pad with silence to loop length so tiling is stable
        pad = np.zeros((n_loop - y.shape[0], y.shape[1]), dtype=y.dtype)
        y = np.concatenate([y, pad], axis=0)
    else:
        y = y[:n_loop]
    reps = int(np.ceil(duration_s / LOOP_S))
    tiled = np.tile(y, (reps, 1))
    trimmed = tiled[:n_target]
    sf.write(str(out_wav), trimmed, SR, subtype="FLOAT")
    tmp.unlink()


def peak_normalize(y: np.ndarray, target_dbfs: float = -3.0) -> np.ndarray:
    peak = np.max(np.abs(y))
    if peak <= 0:
        return y
    target = 10 ** (target_dbfs / 20.0)
    return y * (target / peak)


def build_mix(duration_s: int, midi_paths: dict[str, Path]) -> dict:
    mix_id = f"synth_{duration_s:03d}s"
    out_dir = GT_ROOT / mix_id
    out_dir.mkdir(parents=True, exist_ok=True)

    stem_names = ("drums", "bass", "piano")
    stem_files = {}
    for name in stem_names:
        wav = out_dir / (f"{name}.wav" if name != "piano" else "other.wav")
        render_stem(midi_paths[name], wav, duration_s)
        stem_files[name] = wav

    # Zero vocals stem so ground-truth has 4 stems paralleling htdemucs output.
    n = duration_s * SR
    zeros = np.zeros((n, 2), dtype=np.float32)
    vocals_wav = out_dir / "vocals.wav"
    sf.write(str(vocals_wav), zeros, SR, subtype="FLOAT")

    # Sum-mix.
    total = None
    for name in stem_names:
        wav_path = stem_files[name]
        y, sr = sf.read(str(wav_path), always_2d=True)
        assert sr == SR and y.shape[0] == n
        total = y if total is None else total + y
    total = peak_normalize(total, target_dbfs=-3.0)
    mix_wav = out_dir / "mix.wav"
    sf.write(str(mix_wav), total.astype(np.float32), SR, subtype="FLOAT")

    return {
        "mix_id": mix_id,
        "duration_s": duration_s,
        "n_samples": n,
        "sr_hz": SR,
        "channels": 2,
        "peak_dbfs_target": -3.0,
        "stems": {
            "drums": {"path": str(stem_files["drums"].relative_to(ROOT)),
                      "sha256": sha256(stem_files["drums"])},
            "bass":  {"path": str(stem_files["bass"].relative_to(ROOT)),
                      "sha256": sha256(stem_files["bass"])},
            "other": {"path": str(stem_files["piano"].relative_to(ROOT)),
                      "sha256": sha256(stem_files["piano"]),
                      "instrument": "piano (GM program 0)"},
            "vocals": {"path": str(vocals_wav.relative_to(ROOT)),
                       "sha256": sha256(vocals_wav),
                       "kind": "zero (no-vocals ground truth)"},
        },
        "mix": {"path": str(mix_wav.relative_to(ROOT)),
                "sha256": sha256(mix_wav)},
    }


def main() -> None:
    if shutil.which("fluidsynth") is None:
        raise SystemExit("fluidsynth not found on PATH")
    if not Path(SF2).is_file():
        raise SystemExit(f"SF2 missing at {SF2}")
    sf2_sha = hashlib.sha256(Path(SF2).read_bytes()).hexdigest()

    midi_paths = build_midis()
    midi_shas = {k: sha256(p) for k, p in midi_paths.items()}

    mixes = [build_mix(d, midi_paths) for d in DURATIONS]

    manifest = {
        "created": "2026-08-28T05:35:00Z",
        "cycle": 4,
        "run_id": "run-2026-08-28T040704Z",
        "agent": "worker",
        "milestone": "M-SEP-1/ground-truth",
        "sr_hz": SR,
        "bpm": BPM,
        "bars_per_loop": BARS_PER_LOOP,
        "loop_s": LOOP_S,
        "durations_s": DURATIONS,
        "sf2_path": SF2,
        "sf2_sha256": sf2_sha,
        "fluidsynth_cmd": "fluidsynth -a null -T wav -F <out.wav> -r 44100 -g 1.0 -i <sf2> <mid>",
        "midi_shas256": midi_shas,
        "mixes": mixes,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
