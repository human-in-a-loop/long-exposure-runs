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
    # c6 CRITICAL fix: rewrite the source MIDI in-memory to force fluidsynth
    # to honor profile.identity.program, regardless of what program_change
    # the source MIDI embeds. Strip existing program_change events on all
    # tracks/channels; inject a fresh program_change(channel=0, program=N)
    # at tick 0 of the first note-carrying track. Deterministic pure function
    # of (midi_path, program). Pre-fix behavior was `_ = setup  # documentation`
    # which discarded the program-select payload.
    import mido  # local import: only needed on sf2 dispatch
    _mid = mido.MidiFile(str(midi_path))
    for _tr in _mid.tracks:
        _to_del = [i for i, m in enumerate(_tr) if m.type == "program_change"]
        for i in reversed(_to_del):
            del _tr[i]
    # c11 EXTENSION: channel-aware program_change routing. c6 fix inserted
    # program_change on channel 0, which is correct for pitched-instrument
    # MIDIs (all bass anchors -- notes exclusively on ch 0). For GM
    # percussion (ch 10 == idx 9) the ch 0 insertion silently defaults the
    # drum kit to Standard, ignoring the profile's declared program.
    # New behavior: insert one program_change per unique channel carrying
    # note_on events, on the FIRST track that carries note_on for that
    # channel, at tick 0. For pure-ch0 MIDIs this is byte-identical to c6.
    _channels_seen: list[int] = []
    for _tr in _mid.tracks:
        for _m in _tr:
            if _m.type == "note_on":
                _ch = int(_m.channel)
                if _ch not in _channels_seen:
                    _channels_seen.append(_ch)
    _channels_seen.sort()  # deterministic ordering
    for _ch in _channels_seen:
        for _tr in _mid.tracks:
            if any(m.type == "note_on" and int(m.channel) == _ch for m in _tr):
                _tr.insert(0, mido.Message(
                    "program_change", channel=_ch, program=program, time=0,
                ))
                break
    _rewritten = out_wav_path.with_suffix(".prog_forced.mid")
    _mid.save(str(_rewritten))
    cmd.append(str(_rewritten))
    _ = bank  # bank currently unused; program-select forces default bank 0
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
