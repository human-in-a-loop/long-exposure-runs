#!/usr/bin/python3
"""v6 Phase 4 — render one MIDI stem through one pool patch: sfizz_render (sfz), fluidsynth CLI (sf2), DawDreamer (frozen).

created: 2026-10-04
milestone: M-V6-RENDER-4/realistic-renderer

render_stem(midi_path, patch, out_wav, sample_rate=44100) -> manifest dict (backend, command, sha256, wall_s, frozen?).
  sfz  : `sfizz_render --sfz <.ram.sfz wrapper> --midi <mid> --wav <out> --samplerate <sr>` — the wrapper (hint_ram_based=1,
         recorded in INVENTORY) is what makes sfizz byte-deterministic (INVENTORY determinism_checks).
  sf2  : `fluidsynth -ni -F <out> -r <sr> -g 0.8 -o synth.cpu-cores=1 -o synth.reverb.active=false -o synth.chorus.active=false
         <sf2> <mid>` — bank/program are forced INSIDE the MIDI by midi_io.write_midi (CC0/CC32 + program_change, drums on
         channel 9 so the GS-mode synth takes bank 128), the same contract scripts/sound_match/replay.py enforces by rewriting.
  dawdreamer (optional, Surge XT / Dexed): NOT bit-deterministic. The render is FROZEN under
         data/v6/render_v6/frozen/<sha256(midi bytes | canonical patch)>.wav on first use and copied byte-identically after,
         so a song is reproducible once frozen (same escape hatch as replay.py's surge bounce). Needs dawdreamer importable.
Both CLI backends run with LC_ALL=C and a single core; stderr is kept in the manifest head on failure.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

WS = Path(__file__).resolve().parents[4]
FROZEN_DIR = WS / "data" / "v6" / "render_v6" / "frozen"
FLUID_GAIN = "0.8"


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _run(cmd: list, timeout: int = 1800) -> subprocess.CompletedProcess:
    env = dict(os.environ, LC_ALL="C", OMP_NUM_THREADS="1")
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)


def midi_channel_for(patch: dict, role: str = "") -> int:
    """Channel 9 ONLY for sf2 bank-128 kits (fluidsynth GS mode looks drum channels up in bank 128). AVL kits are plain
    bank-0 presets and sfizz ignores the channel, so both stay on channel 0 — a bank-0 kit on channel 9 renders silence."""
    return 9 if (patch.get("backend") == "sf2" and int(patch.get("bank") or 0) == 128) else 0


def _midi_length_s(midi_path: Path) -> float:
    import mido
    return float(mido.MidiFile(str(midi_path)).length)


def _strip_cc(midi_path: Path, out_path: Path, controls: set) -> None:
    import mido
    f = mido.MidiFile(str(midi_path))
    g = mido.MidiFile(ticks_per_beat=f.ticks_per_beat, type=f.type)
    for tr in f.tracks:
        nt, acc = mido.MidiTrack(), 0
        for m in tr:
            acc += m.time
            if m.type == "control_change" and m.control in controls:
                continue
            nt.append(m.copy(time=acc)); acc = 0
        g.tracks.append(nt)
    g.save(str(out_path))


def _run_guarded(cmd: list, out_wav: Path, max_bytes: int, max_wall_s: float) -> tuple:
    """Run a renderer, killing it if the output file outgrows the MIDI-implied size or the wall budget (runaway guard)."""
    env = dict(os.environ, LC_ALL="C", OMP_NUM_THREADS="1")
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    while True:
        try:
            out, err = proc.communicate(timeout=0.5)
            return proc.returncode, out, err, False
        except subprocess.TimeoutExpired:
            size = out_wav.stat().st_size if out_wav.exists() else 0
            if size > max_bytes or (time.time() - t0) > max_wall_s:
                proc.kill(); proc.communicate()
                return -9, "", f"runaway: size={size} max_bytes={max_bytes} wall={time.time() - t0:.0f}s max_wall={max_wall_s:.0f}s", True


def render_sfz(sfz: str, midi_path: Path, out_wav: Path, sample_rate: int) -> list:
    if shutil.which("sfizz_render") is None:
        raise RuntimeError("sfizz_render not on PATH")
    length = _midi_length_s(midi_path)
    max_bytes = int((length + 60.0) * sample_rate * 2 * 4 * 1.5)  # float32 stereo worst case + 60 s tail, 1.5x slack
    max_wall = max(300.0, 8.0 * length)
    cmd = ["sfizz_render", "--sfz", str(sfz), "--midi", str(midi_path), "--wav", str(out_wav), "--samplerate", str(sample_rate)]
    rc, so, se, runaway = _run_guarded(cmd, out_wav, max_bytes, max_wall)
    if runaway:
        # retry once with the sustain pedal stripped (known sfizz/Salamander non-termination with CC64)
        stripped = midi_path.with_name(midi_path.stem + ".nocc64.mid")
        _strip_cc(midi_path, stripped, {64})
        out_wav.unlink(missing_ok=True)
        cmd = ["sfizz_render", "--sfz", str(sfz), "--midi", str(stripped), "--wav", str(out_wav), "--samplerate", str(sample_rate)]
        rc, so, se, runaway = _run_guarded(cmd, out_wav, max_bytes, max_wall)
        cmd = cmd + ["#retry_without_cc64"]
    if rc != 0 or runaway or not out_wav.exists():
        out_wav.unlink(missing_ok=True)
        raise RuntimeError(f"sfizz_render rc={rc} runaway={runaway}: {(se or so)[-600:]}")
    return cmd


def render_sf2(sf2: str, midi_path: Path, out_wav: Path, sample_rate: int) -> list:
    if shutil.which("fluidsynth") is None:
        raise RuntimeError("fluidsynth not on PATH")
    cmd = ["fluidsynth", "-ni", "-F", str(out_wav), "-r", str(sample_rate), "-g", FLUID_GAIN, "-o", "synth.cpu-cores=1",
           "-o", "synth.reverb.active=false", "-o", "synth.chorus.active=false", "-o", f"synth.sample-rate={sample_rate}", str(sf2), str(midi_path)]
    r = _run(cmd)
    if r.returncode != 0 or not out_wav.exists():
        raise RuntimeError(f"fluidsynth rc={r.returncode}: {(r.stderr or r.stdout)[-600:]}")
    return cmd


def frozen_key(midi_path: Path, patch: dict) -> str:
    ident = {k: patch.get(k) for k in ("id", "backend", "plugin", "preset", "program", "path")}
    h = hashlib.sha256(Path(midi_path).read_bytes())
    h.update(json.dumps(ident, sort_keys=True, separators=(",", ":")).encode())
    return h.hexdigest()


def render_dawdreamer(patch: dict, midi_path: Path, out_wav: Path, frozen_dir: Path) -> dict:
    key = frozen_key(midi_path, patch)
    frozen = Path(frozen_dir) / f"{key}.wav"
    if frozen.exists():
        shutil.copyfile(frozen, out_wav)
        return {"frozen": True, "frozen_key": key, "frozen_path": str(frozen), "rendered_now": False}
    v6_dir = WS / "scripts" / "v6"
    if str(v6_dir) not in sys.path:
        sys.path.insert(0, str(v6_dir))
    from render_vst_test import render_vst_entry  # noqa: E402  (dawdreamer imported lazily inside)
    inst = {"plugin": patch["plugin"]}
    if patch.get("preset"):
        inst["preset"] = patch["preset"]
    if patch.get("program") is not None and not patch.get("preset"):
        inst["program"] = patch["program"]
    render_vst_entry(inst, Path(midi_path), out_wav)
    frozen.parent.mkdir(parents=True, exist_ok=True)
    tmp = frozen.with_name(frozen.name + ".tmp")
    shutil.copyfile(out_wav, tmp)
    os.replace(tmp, frozen)
    return {"frozen": True, "frozen_key": key, "frozen_path": str(frozen), "rendered_now": True}


def render_stem(midi_path, patch: dict, out_wav, sample_rate: int = 44100, frozen_dir=FROZEN_DIR) -> dict:
    """Render `midi_path` with pool `patch` to `out_wav` (stereo WAV at sample_rate). Returns the manifest block."""
    midi_path, out_wav = Path(midi_path), Path(out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    backend = patch["backend"]
    man = {"backend": backend, "patch_id": patch.get("id"), "deterministic": bool(patch.get("deterministic", backend in ("sfz", "sf2"))),
           "midi_sha256": sha_file(midi_path), "sample_rate": sample_rate}
    if backend == "sfz":
        man["command"] = render_sfz(patch["path"], midi_path, out_wav, sample_rate)
    elif backend == "sf2":
        man["command"] = render_sf2(patch["path"], midi_path, out_wav, sample_rate)
        man["bank_program_forced_in_midi"] = [patch.get("bank"), patch.get("program")]
    elif backend == "dawdreamer":
        man.update(render_dawdreamer(patch, midi_path, out_wav, Path(frozen_dir)))
    else:
        raise ValueError(f"unknown backend {backend!r}")
    man["wav_sha256"] = sha_file(out_wav)
    man["wall_s"] = round(time.time() - t0, 3)
    return man
