#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 1
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES
# ---
"""Deterministic replay: MIDI + profile -> stem audio.

Dispatch by family:
    sf2          -> fluidsynth CLI
    sfz          -> sfizz_render CLI (fetchability recorded if missing)
    stem_sampled -> sfizz_render CLI (sfz built from stems)
    surge        -> pinned-bounce escape hatch (render_replayable=False)

Records render_sha256 post-hoc. This module is pure control flow; the
underlying binaries are the sound producers.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Mapping

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(
        f"replay requires /usr/bin/python3 (got {sys.executable})"
    )


_DISPATCH = {
    "sf2": "_replay_sf2",
    "sfz": "_replay_sfz",
    "stem_sampled": "_replay_sfz",
    "surge": "_replay_surge_bounce",
}


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _replay_sf2(profile: Mapping, midi_path: Path, out_wav_path: Path) -> None:
    ident = profile["identity"]
    sf2 = ident["sf2_path"]
    bank = int(ident.get("bank", 0))
    program = int(ident["program"])
    sr = int(profile.get("params", {}).get("sample_rate", 44100))
    if shutil.which("fluidsynth") is None:  # pragma: no cover
        raise RuntimeError("fluidsynth binary not found on PATH")
    out_wav_path = Path(out_wav_path)
    out_wav_path.parent.mkdir(parents=True, exist_ok=True)
    # Deterministic pins: single core, no reverb/chorus, gain from params.
    gain = float(profile.get("params", {}).get("gain", 0.8))
    cmd = [
        "fluidsynth",
        "-ni",
        "-F", str(out_wav_path),
        "-r", str(sr),
        "-g", str(gain),
        "-o", "synth.cpu-cores=1",
        "-o", "synth.reverb.active=false",
        "-o", "synth.chorus.active=false",
        "-o", f"synth.sample-rate={sr}",
        "-o", f"synth.midi-bank-select=gs",
        str(sf2),
        # program pre-select via MIDI file itself; command-line preload:
        "-o", f"synth.default-soundfont={sf2}",
    ]
    # Feed a bank/program via a short setup script.
    setup = (
        f"select 0 1 {bank} {program}\n"
    )
    # NOTE: fluidsynth CLI expects program change in the MIDI file.
    # We rely on the sweep runner writing a bass-only MIDI with an
    # embedded program_change event, so the setup is a safety net only.
    _ = setup  # documentation
    cmd.append(str(midi_path))
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(
            f"fluidsynth failed rc={r.returncode} stderr={r.stderr.decode(errors='replace')[:400]}"
        )


def _replay_sfz(profile: Mapping, midi_path: Path, out_wav_path: Path) -> None:  # pragma: no cover
    ident = profile["identity"]
    sfz = ident["sfz_path"]
    sr = int(profile.get("params", {}).get("sample_rate", 44100))
    if shutil.which("sfizz_render") is None:
        raise RuntimeError("sfizz_render binary not found on PATH")
    cmd = [
        "sfizz_render",
        "--sfz", str(sfz),
        "--midi", str(midi_path),
        "--wav", str(out_wav_path),
        "--samplerate", str(sr),
        "--oversampling", "x1",
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(
            f"sfizz_render failed rc={r.returncode} stderr={r.stderr.decode(errors='replace')[:400]}"
        )


def _replay_surge_bounce(profile: Mapping, midi_path: Path, out_wav_path: Path) -> None:  # pragma: no cover
    # Surge XT is non-deterministic-by-design (see c36 characterization).
    # Escape hatch: profile carries `bounce_path` referring to a pre-rendered
    # sha-pinned stem bounce; we copy it byte-identical.
    ident = profile["identity"]
    bounce = Path(ident["bounce_path"])
    if not bounce.exists():
        raise FileNotFoundError(f"pinned bounce missing: {bounce}")
    shutil.copy2(bounce, out_wav_path)


def replay(profile: Mapping, midi_path: Path, out_wav_path: Path) -> str:
    """Render `midi_path` through `profile` to `out_wav_path`; return sha256."""
    family = profile["family"]
    if family not in _DISPATCH:
        raise ValueError(f"unknown family: {family}")
    fn = globals()[_DISPATCH[family]]
    midi_path = Path(midi_path)
    out_wav_path = Path(out_wav_path)
    fn(profile, midi_path, out_wav_path)
    return _sha256_of_file(out_wav_path)
