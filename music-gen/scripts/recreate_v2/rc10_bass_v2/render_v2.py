#!/usr/bin/env /usr/bin/python3
# RC10 bass v2 A/B pair rendering: v2 notes → MIDI (GM 34, per-note velocity,
# articulation-driven envelope shaping) → fluidsynth → LUFS-I -23 normalization.
# created: 2026-09-02, cycle 55, run-2026-08-28T040704Z, worker, fork 7cc01d726807 clone-1
import subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
import pretty_midi

from ._common import SF2


# Articulation-driven envelope shaping: modulate note-off timing (duration
# scaling) so the fluidsynth-rendered envelope reflects articulation.
# slap → sharper attack: shorten note-off (release ~40% of duration).
# ghost → soft, brief; keep short duration as-is.
# sustained → default full duration.
DUR_SCALE = {
    "slap": 0.40,
    "ghost": 1.00,
    "sustained": 1.00,
}


def notes_to_midi_v2(notes, path):
    """Write MIDI with GM 34 (Electric Bass Finger, program=33 in 0-indexed).
    Articulation is encoded via velocity + note-off timing."""
    pm = pretty_midi.PrettyMIDI()
    inst = pretty_midi.Instrument(program=33, is_drum=False, name="Bass_v2")
    for n in notes:
        start = float(n["onset_s"])
        dur = max(0.02, float(n["duration_s"]))
        scale = DUR_SCALE.get(n.get("articulation", "sustained"), 1.0)
        end = start + max(0.020, dur * scale)
        inst.notes.append(pretty_midi.Note(
            velocity=int(n["velocity"]),
            pitch=int(n["midi"]),
            start=start,
            end=end,
        ))
    pm.instruments.append(inst)
    pm.write(str(path))


def fluidsynth_render(midi_path, wav_out, sr=44100):
    """Render MIDI to WAV via fluidsynth CLI. Deterministic given identical env."""
    cmd = [
        "/usr/bin/fluidsynth", "-a", "file", "-F", str(wav_out),
        "-r", str(sr), "-g", "0.5", "-q", "-i",
        str(SF2), str(midi_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=300)


def loudness_normalize(y, sr, target_lufs=-23.0):
    """LUFS-I normalize a mono/stereo array via pyloudnorm.

    System pyloudnorm is verified available. If import fails for any reason,
    honest fallback to RMS-dBFS proxy is used (disclosed in report §Issues)."""
    try:
        import pyloudnorm as pln
        if y.ndim == 1:
            yy = y.astype(np.float32).reshape(-1, 1)
        else:
            yy = y.astype(np.float32)
        meter = pln.Meter(sr)
        loudness = meter.integrated_loudness(yy)
        if not np.isfinite(loudness):
            return y.astype(np.float32), None, "invalid_lufs"
        gain_db = target_lufs - loudness
        gain = 10 ** (gain_db / 20.0)
        out = (y.astype(np.float32) * gain).astype(np.float32)
        peak = float(np.max(np.abs(out)) or 1.0)
        if peak > 0.99:
            out = out * (0.99 / peak)
        return out, float(loudness), "pyloudnorm"
    except Exception as e:
        # RMS-dBFS proxy fallback
        rms = float(np.sqrt(np.mean(y.astype(np.float32) ** 2) + 1e-12))
        if rms <= 0:
            return y.astype(np.float32), None, f"rms_fallback:{e}"
        target_rms = 10 ** (target_lufs / 20.0)
        gain = target_rms / rms
        out = (y.astype(np.float32) * gain).astype(np.float32)
        peak = float(np.max(np.abs(out)) or 1.0)
        if peak > 0.99:
            out = out * (0.99 / peak)
        return out, float(20 * np.log10(rms + 1e-12)), f"rms_fallback:{e}"


def write_ab_pair_v2(y_original, sr, notes, out_dir):
    """Write LUFS-normalized original.wav + rendered.wav (from v2 notes MIDI)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    y_orig_norm, lo, meth_o = loudness_normalize(y_original, sr)
    sf.write(str(out_dir / "original.wav"), y_orig_norm, sr, subtype="PCM_16")
    midi_p = out_dir / "candidate.mid"
    wav_p = out_dir / "_render_raw.wav"
    notes_to_midi_v2(notes, midi_p)
    try:
        fluidsynth_render(midi_p, wav_p, sr=sr)
        yr, srr = sf.read(str(wav_p))
        if yr.ndim == 2:
            yr = yr.mean(axis=1)
        yr_norm, lr, meth_r = loudness_normalize(yr, srr)
        sf.write(str(out_dir / "rendered.wav"), yr_norm, srr, subtype="PCM_16")
        wav_p.unlink()
        return {"orig_lufs": lo, "rendered_lufs": lr, "method_orig": meth_o,
                "method_rendered": meth_r, "ok": True}
    except Exception as e:
        return {"orig_lufs": lo, "rendered_lufs": None, "method_orig": meth_o,
                "method_rendered": None, "ok": False, "error": str(e)}
