"""Venv-side worker: render + LUFS-normalize A/B pairs via fluidsynth CLI.

Invoked via subprocess by run_all.py. Reads a JSON job list on stdin,
writes result JSON on stdout. Each job:
  {sha16, stem, winner_midi_path, original_wav_path, gm_program, is_drum, out_dir}
Output: {ok, pairs: [{sha16, stem, ..., lufs_i_original, lufs_i_rendered,
  rendered_sha256, original_sha256, midi_program_baked_sha256}]}
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

WS = Path("/home/user/long-exposure-runs/music-gen")
SF2 = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
FLUIDSYNTH = "/usr/bin/fluidsynth"
LUFS_TARGET = -23.0
TRUE_PEAK_LIMIT = 0.99


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _bake_gm_program(src_midi: Path, dst_midi: Path, gm_program: int, is_drum: bool) -> None:
    """Load MIDI, set instrument program/is_drum on all instruments, write back."""
    import pretty_midi

    pm = pretty_midi.PrettyMIDI(str(src_midi))
    if not pm.instruments:
        # Empty MIDI — add an empty instrument so fluidsynth has something to load
        pm.instruments.append(pretty_midi.Instrument(program=gm_program, is_drum=is_drum))
    for inst in pm.instruments:
        inst.program = int(gm_program)
        inst.is_drum = bool(is_drum)
    pm.write(str(dst_midi))


def _render_fluidsynth(midi_path: Path, out_wav: Path, sample_rate: int = 44100) -> None:
    """Invoke fluidsynth CLI with fixed params for deterministic render."""
    cmd = [
        FLUIDSYNTH,
        "-a", "null",
        "-T", "wav",
        "-F", str(out_wav),
        "-r", str(sample_rate),
        "-R", "1", "-C", "0",  # reverb + chorus enabled (default) — deterministic
        "-g", "1.0",
        "-i", "-n",
        str(SF2),
        str(midi_path),
    ]
    env = os.environ.copy()
    proc = subprocess.run(cmd, capture_output=True, env=env)
    if proc.returncode != 0:
        raise RuntimeError(f"fluidsynth failed rc={proc.returncode}: {proc.stderr[:400]}")


def _read_wav_stereo(p: Path):
    import numpy as np
    import soundfile as sf

    y, sr = sf.read(str(p), always_2d=False)
    if y.ndim == 1:
        y = np.stack([y, y], axis=1)
    return y.astype(np.float32), int(sr)


def _write_stereo_wav(p: Path, y, sr: int) -> None:
    import numpy as np
    import soundfile as sf

    y = np.clip(y, -TRUE_PEAK_LIMIT, TRUE_PEAK_LIMIT).astype(np.float32)
    sf.write(str(p), y, int(sr), subtype="PCM_16")


def _lufs_normalize(y, sr: int, target: float = LUFS_TARGET):
    """Return (y_normalized, lufs_pre, lufs_post, fallback_used).

    If pyloudnorm's integrated_loudness returns non-finite (input entirely below
    the ITU-R BS.1770 -70 LUFS gate), we fall back to RMS-dBFS scaling so the
    A/B pair still carries audible audio the operator can listen to; the
    fallback is recorded honestly in the manifest.
    """
    import math

    import numpy as np
    import pyloudnorm as pyln

    m = pyln.Meter(sr)
    lufs_pre = float(m.integrated_loudness(y))
    fallback_used = False
    if math.isfinite(lufs_pre):
        gain_db = target - lufs_pre
    else:
        # RMS-dBFS fallback (matches c53 protocol before pyloudnorm arrived)
        fallback_used = True
        rms = float(np.sqrt(np.mean(y.astype(np.float64) ** 2)) + 1e-12)
        cur_dbfs = 20.0 * np.log10(rms + 1e-12)
        gain_db = target - cur_dbfs
        # Clamp fallback gain to +/-60 dB to avoid pathological amplification
        gain_db = float(np.clip(gain_db, -60.0, 60.0))
    gain = 10.0 ** (gain_db / 20.0)
    y2 = y * gain
    peak = float(np.max(np.abs(y2))) if y2.size else 0.0
    if peak > TRUE_PEAK_LIMIT:
        y2 = y2 * (TRUE_PEAK_LIMIT / peak)
    y2 = np.clip(y2, -TRUE_PEAK_LIMIT, TRUE_PEAK_LIMIT).astype(np.float32)
    lufs_post = float(m.integrated_loudness(y2))
    if not math.isfinite(lufs_post):
        lufs_post = float("nan")
    if not math.isfinite(lufs_pre):
        lufs_pre = float("nan")
    return y2, lufs_pre, lufs_post, fallback_used


def _process_pair(job: dict) -> dict:
    sha16 = job["sha16"]
    stem = job["stem"]
    winner_midi = Path(job["winner_midi_path"])
    original_wav = Path(job["original_wav_path"])
    gm_program = int(job["gm_program"])
    is_drum = bool(job["is_drum"])
    out_dir = Path(job["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    tmp = Path(tempfile.mkdtemp(prefix=f"rc10_render_{sha16}_{stem}_",
                                dir=str(WS / "tmp/rc10_ab_refresh")))
    try:
        # 1. Bake GM program into MIDI (deterministic canonical form)
        baked_midi = tmp / f"{stem}_baked.mid"
        _bake_gm_program(winner_midi, baked_midi, gm_program, is_drum)
        midi_baked_sha = _sha256_file(baked_midi)

        # 2. Copy original → tmp → LUFS-normalize → write final
        y_orig, sr_orig = _read_wav_stereo(original_wav)
        y_orig_n, lufs_orig_pre, lufs_orig_post, fallback_orig = _lufs_normalize(y_orig, sr_orig)
        orig_out = out_dir / "original.wav"
        _write_stereo_wav(orig_out, y_orig_n, sr_orig)

        # 3. Render via fluidsynth into tmp
        rendered_tmp = tmp / f"{stem}_rendered.wav"
        _render_fluidsynth(baked_midi, rendered_tmp, sample_rate=sr_orig)

        # 4. LUFS-normalize rendered → write final
        y_ren, sr_ren = _read_wav_stereo(rendered_tmp)
        # Match rendered length to original if slightly different
        n_orig = y_orig_n.shape[0]
        if y_ren.shape[0] < n_orig:
            import numpy as np

            pad = np.zeros((n_orig - y_ren.shape[0], 2), dtype=np.float32)
            y_ren = np.concatenate([y_ren, pad], axis=0)
        elif y_ren.shape[0] > n_orig:
            y_ren = y_ren[:n_orig]
        y_ren_n, lufs_ren_pre, lufs_ren_post, fallback_ren = _lufs_normalize(y_ren, sr_ren)
        rendered_out = out_dir / "rendered.wav"
        _write_stereo_wav(rendered_out, y_ren_n, sr_ren)

        return {
            "sha16": sha16,
            "stem": stem,
            "gm_program": gm_program,
            "is_drum": is_drum,
            "original_wav_path": str(orig_out.relative_to(WS)),
            "rendered_wav_path": str(rendered_out.relative_to(WS)),
            "winner_midi_path": str(winner_midi.relative_to(WS)),
            "winner_midi_sha256": _sha256_file(winner_midi),
            "midi_program_baked_sha256": midi_baked_sha,
            "lufs_i_original_pre": lufs_orig_pre,
            "lufs_i_original_post": lufs_orig_post,
            "lufs_i_original_fallback_rms_dbfs": fallback_orig,
            "lufs_i_rendered_pre": lufs_ren_pre,
            "lufs_i_rendered_post": lufs_ren_post,
            "lufs_i_rendered_fallback_rms_dbfs": fallback_ren,
            "original_wav_sha256": _sha256_file(orig_out),
            "rendered_wav_sha256": _sha256_file(rendered_out),
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    (WS / "tmp/rc10_ab_refresh").mkdir(parents=True, exist_ok=True)
    jobs = json.loads(sys.stdin.read())
    results = []
    for j in jobs:
        r = _process_pair(j)
        def _f(v):
            try:
                return f"{v:.3f}" if v is not None else "None"
            except (TypeError, ValueError):
                return str(v)
        print(f"[render] {r['sha16']}/{r['stem']} "
              f"lufs_ren_post={_f(r['lufs_i_rendered_post'])} "
              f"lufs_orig_post={_f(r['lufs_i_original_post'])} "
              f"fb_o={int(r['lufs_i_original_fallback_rms_dbfs'])} "
              f"fb_r={int(r['lufs_i_rendered_fallback_rms_dbfs'])}",
              file=sys.stderr, flush=True)
        results.append(r)
    sys.stdout.write(json.dumps({"ok": True, "pairs": results}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
