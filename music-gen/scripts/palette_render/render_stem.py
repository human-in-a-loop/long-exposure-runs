#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T04:34:00Z
# cycle: 33
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/palette-driven-bare-render
# ---
"""Per-stem renderer dispatched on assignment.instrument.

Instrument dispatch:
  * fluidsynth_gm — direct subprocess call to `fluidsynth` (c9 anchored
    invocation pattern, copied via documented comment from
    scripts/tex/render_bare_midi.py — that module is NOT imported).
  * sfizz — subprocess call to `sfizz_render` (c31 palette_probe/sfizz.py
    invocation pattern, copied via documented comment — that module is
    NOT imported at runtime).

Output: a 44.1 kHz stereo WAV at `out_dir/render.wav`, canonicalized
through the stdlib `wave` module so header bytes are byte-deterministic
across runs.

NO PRNG. /usr/bin/python3 guarded. No sidecar_nonfactor imports.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
import soundfile as sf
import scipy.io.wavfile as scipy_wav

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
SAMPLE_RATE = 44100
DURATION_S = 30.0
SAMPLE_COUNT = int(SAMPLE_RATE * DURATION_S)  # 1_323_000

SF2_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
SF2_EXPECTED_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
SFZ_PATH = _REPO / "data" / "texture" / "test.sfz"
SFIZZ_RENDER = "/usr/bin/sfizz_render"
FLUIDSYNTH = "/usr/bin/fluidsynth"

# Per-stem MIDIs (c6/c9 anchor): basic-pitch transcriptions of the
# synth_030s M-SEP-1 ground-truth stems. These are the "cycle-9 30 s
# synth seed" per-stem inputs. Read-only reads.
PER_STEM_MIDI = {
    "drums": _REPO / "data" / "transcribe" / "basic_pitch" / "synth_030s" / "drums.mid",
    "bass":  _REPO / "data" / "transcribe" / "basic_pitch" / "synth_030s" / "bass.mid",
    "other": _REPO / "data" / "transcribe" / "basic_pitch" / "synth_030s" / "other.mid",
}


def _assert_sf2() -> None:
    """SF2 SHA pin — copied from scripts/tex/render_bare_midi.py verbatim.

    (That module is NOT imported here to satisfy the anti-anchor-import
    contract; the check is duplicated to keep the M-SEP-1 pin
    respected.)
    """
    if not SF2_PATH.is_file():
        raise RuntimeError(f"SF2 missing: {SF2_PATH}")
    h = hashlib.sha256(SF2_PATH.read_bytes()).hexdigest()
    if h != SF2_EXPECTED_SHA:
        raise RuntimeError(f"SF2 SHA mismatch: got {h}, expected {SF2_EXPECTED_SHA}")


def _canonicalize_wav_deterministic(y: np.ndarray, out_wav: Path) -> None:
    """Write a byte-deterministic PCM WAV via scipy.io.wavfile.

    scipy.io.wavfile writes no BEXT/timestamp chunks, so the file-level
    SHA is byte-identical across runs (libsndfile would drift).
    Copied invocation-style from scripts/tex/render_bare_midi.py:83.
    """
    if y.ndim == 1:
        y = np.stack([y, y], axis=1)
    if y.shape[1] == 1:
        y = np.concatenate([y, y], axis=1)
    # trim/pad to exactly SAMPLE_COUNT
    if y.shape[0] > SAMPLE_COUNT:
        y = y[:SAMPLE_COUNT, :]
    elif y.shape[0] < SAMPLE_COUNT:
        pad = np.zeros((SAMPLE_COUNT - y.shape[0], y.shape[1]), dtype=y.dtype)
        y = np.concatenate([y, pad], axis=0)
    scipy_wav.write(str(out_wav), SAMPLE_RATE, y.astype(np.float32))


def render_fluidsynth(midi_path: Path, out_wav: Path,
                      parameter_dict: dict | None = None) -> None:
    """Fluidsynth CLI dispatch. Command line copied verbatim from
    scripts/tex/render_bare_midi.py:70 — that module is NOT imported.

    When ``parameter_dict is None`` this function is byte-identical to
    the c33 anchor path (fixed gain=1.0, no chorus/reverb args).

    When non-None (c36 Branch B extension) the fluidsynth CLI is threaded
    with ``gain`` and optional chorus/reverb settings via ``-o`` synth
    options. Recognized keys (all optional): ``gain``, ``chorus_level``,
    ``reverb_level``, ``reverb_room_size``. Additional/unknown keys are
    IGNORED (forward-compatible with a wider table in c37+).
    """
    _assert_sf2()
    if not midi_path.is_file():
        raise RuntimeError(f"MIDI missing: {midi_path}")
    tmp = out_wav.with_suffix(".raw.wav")
    if tmp.exists():
        tmp.unlink()
    # c33 anchor path — byte-identical when parameter_dict is None.
    if parameter_dict is None:
        cmd = [
            FLUIDSYNTH, "-a", "null", "-T", "wav",
            "-F", str(tmp),
            "-r", str(SAMPLE_RATE),
            "-g", "1.0",
            "-i",
            str(SF2_PATH), str(midi_path),
        ]
    else:
        gain = float(parameter_dict.get("gain", 1.0))
        cmd = [
            FLUIDSYNTH, "-a", "null", "-T", "wav",
            "-F", str(tmp),
            "-r", str(SAMPLE_RATE),
            "-g", f"{gain:.6f}",
            "-i",
        ]
        # Chorus (on when chorus_level provided).
        if "chorus_level" in parameter_dict:
            cl = float(parameter_dict["chorus_level"])
            cmd += ["-o", "synth.chorus.active=1",
                    "-o", f"synth.chorus.level={cl:.6f}"]
        # Reverb (on when either reverb_level or reverb_room_size provided).
        if "reverb_level" in parameter_dict or "reverb_room_size" in parameter_dict:
            cmd += ["-o", "synth.reverb.active=1"]
            if "reverb_level" in parameter_dict:
                rl = float(parameter_dict["reverb_level"])
                cmd += ["-o", f"synth.reverb.level={rl:.6f}"]
            if "reverb_room_size" in parameter_dict:
                rs = float(parameter_dict["reverb_room_size"])
                cmd += ["-o", f"synth.reverb.room-size={rs:.6f}"]
        cmd += [str(SF2_PATH), str(midi_path)]
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    y, got_sr = sf.read(str(tmp), always_2d=True)
    if got_sr != SAMPLE_RATE:
        raise RuntimeError(f"fluidsynth sr={got_sr}, expected {SAMPLE_RATE}")
    _canonicalize_wav_deterministic(y, out_wav)
    tmp.unlink()


def render_sfizz(midi_path: Path, out_wav: Path,
                 block_size: int = 512,
                 parameter_dict: dict | None = None) -> None:
    """sfizz_render CLI dispatch. Command line copied via documented
    comment from scripts/palette_probe/sfizz.py:82 — that module is
    NOT imported.

    Note: sfizz_render doesn't have a --duration flag; it renders MIDI
    to completion. If the MIDI is shorter than 30s we pad; longer we
    trim. Both happen inside _canonicalize_wav_deterministic.

    c37 v4 opcode-rewrite fallback: when parameter_dict contains
    'cutoff' (Hz) and/or 'resonance' (dB) the SFZ is rewritten to a
    temp file with `fil_cutoff=<Hz>` and/or `fil_resonance=<dB>`
    injected into each `<region>` block, sfizz_render is invoked with
    that temp path, and the temp is unlinked. The on-disk anchor SFZ
    is never modified. Lazy import of the rewriter keeps v3 dispatch
    independent of v4.
    """
    if not SFZ_PATH.is_file():
        raise RuntimeError(f"SFZ missing: {SFZ_PATH}")
    if not midi_path.is_file():
        raise RuntimeError(f"MIDI missing: {midi_path}")
    if not Path(SFIZZ_RENDER).is_file():
        raise RuntimeError(f"sfizz_render binary missing: {SFIZZ_RENDER}")
    raw = out_wav.with_suffix(".raw.wav")
    if raw.exists():
        raw.unlink()
    # c37 v4 opcode-rewrite fallback (sfizz dispatch branch growth).
    sfz_path_to_use = SFZ_PATH
    rewritten_sfz: Path | None = None
    if parameter_dict is not None and (
        "cutoff" in parameter_dict or "resonance" in parameter_dict
    ):
        # Lazy import: keep v3 sfizz path free of v4 dependency.
        from scripts.palette_render_v4.extend_sfizz_opcode_rewrite import (
            rewrite_sfz_to_temp,
        )
        rewritten_sfz = rewrite_sfz_to_temp(
            SFZ_PATH,
            cutoff=parameter_dict.get("cutoff"),
            resonance=parameter_dict.get("resonance"),
        )
        sfz_path_to_use = rewritten_sfz
    cmd = [
        SFIZZ_RENDER,
        "--sfz", str(sfz_path_to_use),
        "--midi", str(midi_path),
        "--wav", str(raw),
        "-b", str(block_size),
        "-s", str(SAMPLE_RATE),
        "-q", "1",
        "-p", "64",
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    if rewritten_sfz is not None:
        try:
            rewritten_sfz.unlink()
        except FileNotFoundError:
            pass
    # sfizz_render writes int16 mono/stereo — read via soundfile as float.
    data, sr = sf.read(str(raw), always_2d=True)
    if sr != SAMPLE_RATE:
        raise RuntimeError(f"sfizz sr={sr}, expected {SAMPLE_RATE}")
    # c33 anchor path — when parameter_dict is None output is byte-identical.
    # When non-None (c36 Branch B extension), thread post-render gain/pitch
    # adjustments deterministically (sfizz_render CLI on this workspace does
    # not expose --set opcode overrides; the fallback is documented in
    # dispatch_summary.json). Recognized keys: `master_volume` (dB scalar
    # multiplier applied to samples), `master_pitch_offset` (cents; ignored
    # this cycle as re-pitching post-render is not byte-safe against the
    # canonicalizer and c37 will address via opcode-file rewrite),
    # `envelope_attack_mult`, `envelope_release_mult` (ignored this cycle
    # per rubric fallback). All unrecognized keys IGNORED.
    y = data.astype(np.float32)
    if parameter_dict is not None:
        if "master_volume" in parameter_dict:
            db = float(parameter_dict["master_volume"])
            scale = float(10.0 ** (db / 20.0))
            y = y * np.float32(scale)
    _canonicalize_wav_deterministic(y, out_wav)
    raw.unlink()


def _apply_eq_curve_iirpeak(mono: np.ndarray, centers: list, gains_db: list,
                             fs: int = 44100) -> np.ndarray:
    """c51 signature-v3: apply 12-band iirpeak EQ chain per rc7_eq_curve_fit_method.md."""
    from scipy.signal import iirpeak, lfilter
    out = mono.astype(np.float64, copy=True)
    for f_c, gdb in zip(centers, gains_db):
        b, a = iirpeak(float(f_c), Q=1.4, fs=fs)
        gain_lin = float(10.0 ** (float(gdb) / 20.0))
        band = lfilter(b, a, out)
        out = out + (gain_lin - 1.0) * band
    return out


def _apply_loudness_target(stereo: np.ndarray, target_rms_db: float,
                            max_gain_db: float = 24.0) -> tuple:
    """c51 signature-v3: RMS-match scalar gain, return (out, measured_after_db)."""
    mono = stereo.mean(axis=1) if stereo.ndim > 1 else stereo
    rms = float(np.sqrt(np.mean(mono.astype(np.float64) ** 2)))
    measured_db = 20.0 * np.log10(max(rms, 1e-10))
    delta_db = target_rms_db - measured_db
    delta_db_clip = max(-max_gain_db, min(max_gain_db, delta_db))
    scalar = float(10.0 ** (delta_db_clip / 20.0))
    out = stereo.astype(np.float32) * np.float32(scalar)
    mono2 = out.mean(axis=1) if out.ndim > 1 else out
    rms2 = float(np.sqrt(np.mean(mono2.astype(np.float64) ** 2)))
    measured_after_db = 20.0 * np.log10(max(rms2, 1e-10))
    return out, measured_after_db


def render_stem(stem: str, instrument: str, out_dir: Path,
                *,
                parameter_dict: dict | None = None,
                eq_curve: dict | None = None,
                loudness_target: dict | None = None) -> dict:
    """Render one stem twice, verify byte-determinism, save SHAs.

    ``parameter_dict`` is keyword-only and defaults to None (c33 anchor
    path — byte-identical output). When non-None, threads params via
    the extended fluidsynth/sfizz CLI dispatch per the c36 Branch B
    rubric. Surge XT / Dexed remain unsupported (c31 STILL_GAP + c35
    Branch A RENDER_FAILS). Any non-None ``parameter_dict`` passed
    with instrument ∈ {surge_xt, dexed} raises NotImplementedError.

    c51 signature-v3 additive kwargs (Branch C, RC7 mix-balance):

    - ``eq_curve``: dict describing 12-band iirpeak EQ (Q=1.4, log-spaced
      20 Hz–20 kHz per docs/rc7_eq_curve_fit_method.md). Applied
      post-render, pre-loudness-match. Same VST3 lock as parameter_dict.
    - ``loudness_target``: dict with target_rms_db + optional
      target_lufs_s_db + max_gain_db. Applied AFTER eq_curve. Same VST3 lock.

    When both eq_curve AND loudness_target are None, dispatch is
    byte-identical to c33/c36 (backwards-compat contract).

    Returns dict:
      {"stem": stem, "instrument": instrument,
       "midi_path": str, "midi_sha": str,
       "render_run1_sha": str, "render_run2_sha": str,
       "sha_equal": bool, "run1_wav_path": str,
       # only when eq_curve non-None:
       "eq_applied": bool, "eq_bands_gains_db": list,
       # only when loudness_target non-None:
       "loudness_error_rms_db": float}
    """
    if stem not in PER_STEM_MIDI:
        raise RuntimeError(f"unknown stem {stem}")
    midi_path = PER_STEM_MIDI[stem]
    if not midi_path.is_file():
        raise RuntimeError(f"per-stem MIDI missing: {midi_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    out1 = out_dir / "render_run1.wav"
    out2 = out_dir / "render_run2.wav"

    if instrument in ("surge_xt", "dexed"):
        # c51 lock: eq_curve and loudness_target both trigger NotImplementedError on VST3
        if parameter_dict is not None or eq_curve is not None or loudness_target is not None:
            raise NotImplementedError(
                "VST3 param/EQ/loudness threading not attempted per c35 STILL_GAP "
                "anti-pattern lock (Surge XT / Dexed excluded)"
            )
        raise RuntimeError(f"unsupported instrument {instrument} for palette-render "
                           f"(Surge XT / Dexed excluded per c31 STILL_GAP)")
    elif instrument == "fluidsynth" or instrument == "fluidsynth_gm":
        render_fluidsynth(midi_path, out1, parameter_dict=parameter_dict)
        render_fluidsynth(midi_path, out2, parameter_dict=parameter_dict)
    elif instrument == "sfizz":
        render_sfizz(midi_path, out1, parameter_dict=parameter_dict)
        render_sfizz(midi_path, out2, parameter_dict=parameter_dict)
    else:
        raise RuntimeError(f"unsupported instrument {instrument} for palette-render "
                           f"(Surge XT / Dexed excluded per c31 STILL_GAP)")

    # c51 signature-v3 post-processing chain: EQ → loudness match.
    # When both are None, this section is inert and c33/c36 output is preserved.
    extra_ret: dict = {}
    if eq_curve is not None or loudness_target is not None:
        for out_wav in (out1, out2):
            _, y = scipy_wav.read(str(out_wav))
            y = y.astype(np.float32)
            if eq_curve is not None:
                centers = eq_curve.get("band_center_freqs_hz")
                gains = eq_curve.get("band_gains_db")
                if centers is None or gains is None or len(centers) != 12:
                    raise RuntimeError("eq_curve must carry band_center_freqs_hz + band_gains_db (12 each)")
                # Apply chain independently on each channel (parallel L/R).
                if y.ndim == 1:
                    proc = _apply_eq_curve_iirpeak(y, centers, gains)
                    y_eq = proc.astype(np.float32)
                else:
                    ch_l = _apply_eq_curve_iirpeak(y[:, 0], centers, gains)
                    ch_r = _apply_eq_curve_iirpeak(y[:, 1], centers, gains)
                    y_eq = np.stack([ch_l, ch_r], axis=1).astype(np.float32)
                y = y_eq
                if "eq_bands_gains_db" not in extra_ret:
                    extra_ret["eq_applied"] = True
                    extra_ret["eq_bands_gains_db"] = list(gains)
            if loudness_target is not None:
                tgt = float(loudness_target["target_rms_db"])
                max_g = float(loudness_target.get("max_gain_db", 24.0))
                y, measured_after = _apply_loudness_target(y, tgt, max_gain_db=max_g)
                if "loudness_error_rms_db" not in extra_ret:
                    extra_ret["loudness_error_rms_db"] = float(abs(measured_after - tgt))
            # Re-canonicalize.
            _canonicalize_wav_deterministic(y, out_wav)

    sha1 = hashlib.sha256(out1.read_bytes()).hexdigest()
    sha2 = hashlib.sha256(out2.read_bytes()).hexdigest()
    (out_dir / "render_run1.wav.sha").write_text(sha1 + "\n")
    (out_dir / "render_run2.wav.sha").write_text(sha2 + "\n")

    midi_sha = hashlib.sha256(midi_path.read_bytes()).hexdigest()
    pinned = {
        "stem": stem,
        "instrument": instrument,
        "midi_input_sha256": midi_sha,
        "sample_rate": SAMPLE_RATE,
        "sample_count": SAMPLE_COUNT,
        "sha_equal": sha1 == sha2,
    }
    (out_dir / "pinned_state.json").write_text(
        json.dumps(pinned, sort_keys=True, indent=2) + "\n")

    ret = {
        "stem": stem, "instrument": instrument,
        "midi_path": str(midi_path), "midi_sha": midi_sha,
        "render_run1_sha": sha1, "render_run2_sha": sha2,
        "sha_equal": sha1 == sha2,
        "run1_wav_path": str(out1), "run2_wav_path": str(out2),
    }
    ret.update(extra_ret)
    return ret


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", required=True, choices=["drums", "bass", "other"])
    ap.add_argument("--instrument", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    result = render_stem(a.stem, a.instrument, Path(a.out_dir))
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
