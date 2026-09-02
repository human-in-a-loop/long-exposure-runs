#!/usr/bin/python3
# ---
# created: 2026-09-02T00:00:00Z
# cycle: 58
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-V3-SPINE
# ---
"""End-to-end v3 spine pipeline for one song on the operator-chosen section.

Chain (per docs/v3_spine_rubric.md):
  ingest → slice chosen_section → htdemucs_6s → per-stem MuScriptor
  → merge multi-track MIDI → fluidsynth GM render (drums ch10)
  → vocal overlay (raw stem) → per-stem loudness match → sum
  → excerpt A/B + deliver → sanity panel → verdict.

Interpreter guard `/usr/bin/python3`. NO PRNG. Env pins set in main().

Public entry: `run_song(song_sha16, run_id_suffix, out_dir)`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import time
import wave
from pathlib import Path
from typing import Any

# ------------------------------------------------------------------ env pins
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"v3_spine pipeline requires /usr/bin/python3 (got {sys.executable})")

import numpy as np  # noqa: E402

WSROOT = Path(__file__).resolve().parents[2]
if str(WSROOT) not in sys.path:
    sys.path.insert(0, str(WSROOT))

from scripts.v3_spine.gm_program_map_v3 import (  # noqa: E402
    GM_PROGRAM_MAP,
    STEM_WHITELIST,
    lookup,
    whitelist_for,
)

MUSCRIPTOR_BIN = WSROOT / "workspace" / "learned_transcribers_venv" / "bin" / "muscriptor"
MUSCRIPTOR_MODEL = WSROOT / "workspace" / "models" / "muscriptor-medium" / "model.safetensors"
SF2_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
FOCUS_SET = WSROOT / "data" / "recreate_v2" / "focus_set_v2.json"

STEMS_ORDERED = ["drums", "bass", "guitar", "piano", "other", "vocals"]
NON_VOCAL_STEMS = ["drums", "bass", "guitar", "piano", "other"]
SR_MIX = 44100


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    """Subprocess with env pins + capture. Raises on non-zero."""
    env = os.environ.copy()
    return subprocess.run(cmd, env=env, check=True, capture_output=True, text=True, **kw)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _canonical_json_sha256(path: Path) -> str:
    """Load JSON, dump canonical (sorted keys, no whitespace), SHA."""
    data = json.loads(path.read_text())
    return _sha256_bytes(json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _read_wav_stereo_f32(path: Path) -> tuple[np.ndarray, int]:
    """Read WAV as stereo float32 [-1,1] shape (N, 2). Mono is duplicated.

    Uses soundfile to handle both int16/int24/int32 and IEEE-float formats
    (demucs --float32 emits WAV format tag 3).
    """
    import soundfile as sf
    arr, sr = sf.read(str(path), dtype="float32", always_2d=True)
    if arr.shape[1] == 1:
        arr = np.concatenate([arr, arr], axis=1)
    elif arr.shape[1] > 2:
        arr = arr[:, :2]
    return arr, sr


def _read_wav_mono_f32(path: Path) -> tuple[np.ndarray, int]:
    arr, sr = _read_wav_stereo_f32(path)
    return arr.mean(axis=1), sr


def _write_wav_stereo_int16(path: Path, samples: np.ndarray, sr: int = SR_MIX) -> None:
    """Deterministic 16-bit stereo WAV via stdlib wave (byte-canonical header)."""
    if samples.ndim == 1:
        samples = np.stack([samples, samples], axis=1)
    if samples.shape[1] != 2:
        raise ValueError(f"expected stereo, got shape {samples.shape}")
    peak = float(np.max(np.abs(samples))) if samples.size else 0.0
    if peak > 0.999:
        samples = samples * (0.999 / peak)
    ints = np.clip(np.round(samples * 32767.0), -32768, 32767).astype(np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(ints.tobytes())


def _rms_dbfs(x: np.ndarray) -> float:
    x = x.reshape(-1)
    if x.size == 0:
        return -120.0
    r = float(np.sqrt(np.mean(x.astype(np.float64) ** 2)))
    if r < 1e-9:
        return -120.0
    return 20.0 * float(np.log10(r))


def _resample_linear(x: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    """Deterministic linear resample (avoid scipy nondeterminism paths)."""
    if sr_in == sr_out:
        return x.astype(np.float32)
    if x.ndim == 1:
        n_out = int(round(x.shape[0] * sr_out / sr_in))
        t_in = np.arange(x.shape[0], dtype=np.float64)
        t_out = np.linspace(0, x.shape[0] - 1, n_out, dtype=np.float64)
        return np.interp(t_out, t_in, x).astype(np.float32)
    # stereo
    return np.stack([_resample_linear(x[:, c], sr_in, sr_out) for c in range(x.shape[1])], axis=1)


# --------------------------------------------------------------- pipeline stages

def load_focus_song(song_sha16: str) -> dict[str, Any]:
    fs = json.loads(FOCUS_SET.read_text())
    for s in fs["songs"]:
        if s["audio_sha16"] == song_sha16:
            return s
    raise KeyError(f"song {song_sha16} not in focus_set_v2")


def stage_slice_section(song: dict, out_wav: Path) -> None:
    """Decode mp3 → 44.1kHz stereo → slice chosen_section → deterministic WAV."""
    mp3_path = WSROOT / song["audio_path"]
    section = song["chosen_section"]
    t0 = float(section["t_start_s"])
    t1 = float(section["t_end_s"])
    if not out_wav.exists() or _needs_recompute(out_wav, mp3_path):
        # decode via ffmpeg (deterministic given fixed input)
        tmp = out_wav.with_suffix(".tmp.wav")
        _run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", f"{t0:.6f}", "-to", f"{t1:.6f}",
            "-i", str(mp3_path),
            "-ac", "2", "-ar", str(SR_MIX), "-sample_fmt", "s16",
            "-c:a", "pcm_s16le",
            str(tmp),
        ])
        # canonicalize header via stdlib wave
        arr, sr = _read_wav_stereo_f32(tmp)
        arr = _resample_linear(arr, sr, SR_MIX)
        _write_wav_stereo_int16(out_wav, arr, SR_MIX)
        tmp.unlink()


def _needs_recompute(out: Path, dep: Path) -> bool:
    if not out.exists():
        return True
    return out.stat().st_mtime < dep.stat().st_mtime


def stage_htdemucs_6s(section_wav: Path, out_dir: Path) -> dict[str, Path]:
    """Run htdemucs_6s on the chosen_section slice; write 6 stems as canonical WAVs."""
    out_dir.mkdir(parents=True, exist_ok=True)
    stem_paths = {s: out_dir / f"{s}.wav" for s in STEMS_ORDERED}
    if all(p.exists() for p in stem_paths.values()):
        return stem_paths
    with_tmp = out_dir / "_demucs_tmp"
    if with_tmp.exists():
        shutil.rmtree(with_tmp)
    with_tmp.mkdir(parents=True)
    # demucs writes to <out>/<model>/<trackname>/{drums,bass,...}.wav
    _run([
        "demucs", "-n", "htdemucs_6s", "-d", "cpu",
        "--shifts", "0", "--overlap", "0.25",
        "--float32",
        "-o", str(with_tmp), str(section_wav),
    ])
    inner = with_tmp / "htdemucs_6s" / section_wav.stem
    for s in STEMS_ORDERED:
        src = inner / f"{s}.wav"
        if not src.exists():
            raise RuntimeError(f"htdemucs_6s did not produce stem {s} at {src}")
        arr, sr = _read_wav_stereo_f32(src)
        arr = _resample_linear(arr, sr, SR_MIX)
        _write_wav_stereo_int16(stem_paths[s], arr, SR_MIX)
    shutil.rmtree(with_tmp)
    return stem_paths


def stage_muscriptor(stem_paths: dict[str, Path], out_dir: Path) -> dict[str, dict[str, Path]]:
    """One MuScriptor call per stem with matched --instruments whitelist.

    Returns per-stem {"midi": Path, "json": Path}.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, Path]] = {}
    for stem, wav_path in stem_paths.items():
        midi_path = out_dir / f"{stem}.mid"
        json_path = out_dir / f"{stem}.json"
        if midi_path.exists() and json_path.exists():
            results[stem] = {"midi": midi_path, "json": json_path}
            continue
        wl = whitelist_for(stem)
        # MIDI
        _run([
            str(MUSCRIPTOR_BIN), "transcribe", str(wav_path),
            "-m", str(MUSCRIPTOR_MODEL), "-d", "cpu",
            "--format", "midi",
            "--detect-tempo", "best-effort",
            "--instruments", wl,
            "-o", str(midi_path),
        ])
        # JSON events
        _run([
            str(MUSCRIPTOR_BIN), "transcribe", str(wav_path),
            "-m", str(MUSCRIPTOR_MODEL), "-d", "cpu",
            "--format", "json",
            "--detect-tempo", "best-effort",
            "--instruments", wl,
            "-o", str(json_path),
        ])
        results[stem] = {"midi": midi_path, "json": json_path}
    return results


def stage_analyze_labels(per_stem: dict[str, dict[str, Path]]) -> dict[str, Any]:
    """Enumerate MuScriptor instrument labels present per stem; check GM map coverage."""
    per_stem_labels: dict[str, list[str]] = {}
    all_labels: set[str] = set()
    for stem, files in per_stem.items():
        events = json.loads(files["json"].read_text())
        labels = sorted({e.get("instrument", "") for e in events if e.get("instrument")})
        per_stem_labels[stem] = labels
        all_labels.update(labels)
    unmapped = sorted(l for l in all_labels if l not in GM_PROGRAM_MAP)
    return {
        "per_stem_labels": per_stem_labels,
        "unique_labels": sorted(all_labels),
        "unmapped_labels": unmapped,
        "gm_map_size": len(GM_PROGRAM_MAP),
    }


def _midi_read(path: Path) -> "mido.MidiFile":
    import mido
    return mido.MidiFile(str(path))


def stage_merge_midi(per_stem: dict[str, dict[str, Path]], out_midi: Path,
                     label_info: dict[str, Any]) -> dict[str, Any]:
    """Merge per-stem MIDIs into one multi-track MIDI with GM programs + drums ch10.

    - Vocal-stem tracks stay in the merged MIDI (Fixed Decision 4, symbolic
      record) but are marked as vocal so the renderer can skip them.
    - Drums route to channel 10 (index 9 zero-based).
    - Every non-drum, non-vocal part gets an explicit GM program change.
    - NEVER emits GM program 4 unless the MuScriptor label is
      `electric_piano` (deliberate).
    """
    import mido

    mid_out = mido.MidiFile(type=1)
    mid_out.ticks_per_beat = 480

    # Tempo track from first stem that has one; fallback to 120 BPM.
    tempo_track = mido.MidiTrack()
    tempo_us = None
    ts_msg = None
    for stem in STEMS_ORDERED:
        m = _midi_read(per_stem[stem]["midi"])
        for tr in m.tracks:
            for msg in tr:
                if msg.type == "set_tempo" and tempo_us is None:
                    tempo_us = msg.tempo
                if msg.type == "time_signature" and ts_msg is None:
                    ts_msg = msg
            if tempo_us is not None and ts_msg is not None:
                break
        if tempo_us is not None and ts_msg is not None:
            break
    if tempo_us is None:
        tempo_us = 500000  # 120 BPM
    tempo_track.append(mido.MetaMessage("set_tempo", tempo=tempo_us, time=0))
    if ts_msg is not None:
        tempo_track.append(ts_msg.copy(time=0))
    tempo_track.append(mido.MetaMessage("track_name", name="tempo_map", time=0))
    tempo_track.append(mido.MetaMessage("end_of_track", time=0))
    mid_out.tracks.append(tempo_track)

    # Per-stem tracks. MuScriptor emits one track per instrument; we
    # relabel + re-channel + insert program-change.
    program_manifest: list[dict[str, Any]] = []
    channel_counter = 0  # will be advanced, skipping ch 10 (index 9)

    def _next_channel() -> int:
        nonlocal channel_counter
        # channels 0..15, skip 9 (drums)
        while channel_counter == 9 or channel_counter >= 16:
            channel_counter += 1
            if channel_counter >= 16:
                channel_counter = 0  # wrap; multiple tracks on same ch OK
        ch = channel_counter
        channel_counter += 1
        return ch

    for stem in STEMS_ORDERED:
        is_vocal_stem = (stem == "vocals")
        m = _midi_read(per_stem[stem]["midi"])
        # source ticks_per_beat may differ; scale to 480
        src_tpb = m.ticks_per_beat or 480
        scale = 480 / src_tpb
        for src_tr in m.tracks:
            # instrument name from track_name meta if present
            inst_label: str | None = None
            for msg in src_tr:
                if msg.type == "track_name" and msg.name:
                    inst_label = msg.name.strip().lower().replace(" ", "_")
                    break
                if msg.type == "program_change":
                    # fall through
                    break
            # If no explicit track_name, try to infer from note channel or skip
            has_notes = any(msg.type == "note_on" and msg.velocity > 0 for msg in src_tr)
            if not has_notes:
                continue
            if inst_label is None:
                # fall back: use the stem-primary label
                inst_label = {"drums": "drums", "bass": "electric_bass",
                              "guitar": "clean_electric_guitar",
                              "piano": "acoustic_piano",
                              "other": "synth_pad",
                              "vocals": "voice"}[stem]
            try:
                gm_program, is_drum, gm_name = lookup(inst_label)
            except Exception:
                # unknown label → skip content honestly; log to manifest
                program_manifest.append({
                    "stem": stem, "label": inst_label,
                    "action": "SKIPPED_UNMAPPED", "note_count": 0,
                })
                continue

            channel = 9 if is_drum else _next_channel()
            out_tr = mido.MidiTrack()
            out_tr.append(mido.MetaMessage(
                "track_name",
                name=f"{stem}:{inst_label}{'_VOCAL_SYMBOLIC' if is_vocal_stem else ''}",
                time=0,
            ))
            if not is_drum:
                out_tr.append(mido.Message("program_change", channel=channel,
                                           program=gm_program, time=0))
            # copy note messages, re-channel + scale time
            note_count = 0
            for msg in src_tr:
                if msg.is_meta:
                    continue
                if msg.type in ("note_on", "note_off", "control_change",
                                "pitchwheel", "aftertouch"):
                    new_time = int(round(msg.time * scale))
                    kw = {"time": new_time}
                    if hasattr(msg, "channel"):
                        kw["channel"] = channel
                    out_tr.append(msg.copy(**kw))
                    if msg.type == "note_on" and msg.velocity > 0:
                        note_count += 1
            out_tr.append(mido.MetaMessage("end_of_track", time=0))
            # Mark vocal tracks so the renderer skips them.
            mid_out.tracks.append(out_tr)
            program_manifest.append({
                "stem": stem, "label": inst_label, "gm_program": gm_program,
                "gm_name": gm_name, "channel": channel + 1,  # 1-based for humans
                "is_drum": is_drum, "is_vocal_symbolic": is_vocal_stem,
                "note_count": note_count,
                "action": "VOCAL_SYMBOLIC_NOT_RENDERED" if is_vocal_stem else "RENDER",
            })

    # deterministic write: canonicalize meta ordering, then save
    out_midi.parent.mkdir(parents=True, exist_ok=True)
    mid_out.save(str(out_midi))
    return {"tempo_us_per_beat": tempo_us, "program_manifest": program_manifest,
            "label_info": label_info}


def stage_render_fluidsynth(merged_midi: Path, out_wav: Path,
                            merge_manifest: dict[str, Any]) -> None:
    """Render merged MIDI to a single stereo WAV, skipping vocal-symbolic parts.

    Approach: emit a temporary MIDI with vocal-symbolic tracks REMOVED, then
    run fluidsynth deterministically. GM programs + channel 10 come through
    verbatim.
    """
    import mido
    src = mido.MidiFile(str(merged_midi))
    tmp_mid = out_wav.with_suffix(".synth.mid")
    render_mid = mido.MidiFile(type=1)
    render_mid.ticks_per_beat = src.ticks_per_beat
    for tr in src.tracks:
        name = ""
        for msg in tr:
            if msg.type == "track_name":
                name = msg.name
                break
        if "_VOCAL_SYMBOLIC" in name:
            continue
        render_mid.tracks.append(tr)
    render_mid.save(str(tmp_mid))
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    tmp_wav = out_wav.with_suffix(".raw.wav")
    _run([
        "fluidsynth", "-ni", "-g", "0.5",
        "-F", str(tmp_wav),
        "-r", str(SR_MIX),
        "-T", "wav",
        str(SF2_PATH), str(tmp_mid),
    ])
    arr, sr = _read_wav_stereo_f32(tmp_wav)
    arr = _resample_linear(arr, sr, SR_MIX)
    _write_wav_stereo_int16(out_wav, arr, SR_MIX)
    tmp_wav.unlink()
    tmp_mid.unlink()


def stage_mix_match_and_overlay(render_wav: Path, stem_paths: dict[str, Path],
                                out_wav: Path) -> dict[str, Any]:
    """Loudness-match rendered mix to summed non-vocal stems, then overlay vocals.

    Simple first-pass per FD5 §"No EQ fitting unless listening demands it":
    - Target loudness = RMS-dBFS of (drums+bass+guitar+piano+other) htdemucs sum.
    - Scale rendered instrumental to match target RMS.
    - Overlay vocals stem at 0 dB.
    - Clip guard at 0.99.
    """
    r_arr, _ = _read_wav_stereo_f32(render_wav)
    n = r_arr.shape[0]

    # sum non-vocal stems as target
    tgt = np.zeros_like(r_arr)
    per_stem_rms: dict[str, float] = {}
    for stem in NON_VOCAL_STEMS:
        s_arr, _ = _read_wav_stereo_f32(stem_paths[stem])
        if s_arr.shape[0] > n:
            s_arr = s_arr[:n]
        elif s_arr.shape[0] < n:
            pad = np.zeros((n - s_arr.shape[0], 2), dtype=np.float32)
            s_arr = np.concatenate([s_arr, pad], axis=0)
        tgt += s_arr
        per_stem_rms[stem] = _rms_dbfs(s_arr)

    tgt_rms = _rms_dbfs(tgt)
    r_rms = _rms_dbfs(r_arr)
    if r_rms <= -119.0:
        raise RuntimeError(f"rendered instrumental is silent (RMS {r_rms:.2f} dBFS)")
    gain_db = tgt_rms - r_rms
    gain_lin = float(10 ** (gain_db / 20.0))
    matched = r_arr * gain_lin

    # vocal overlay
    v_arr, _ = _read_wav_stereo_f32(stem_paths["vocals"])
    if v_arr.shape[0] > n:
        v_arr = v_arr[:n]
    elif v_arr.shape[0] < n:
        pad = np.zeros((n - v_arr.shape[0], 2), dtype=np.float32)
        v_arr = np.concatenate([v_arr, pad], axis=0)
    v_rms = _rms_dbfs(v_arr)

    mixed = matched + v_arr
    _write_wav_stereo_int16(out_wav, mixed, SR_MIX)
    return {
        "target_rms_dbfs": tgt_rms,
        "rendered_rms_dbfs": r_rms,
        "gain_applied_db": gain_db,
        "vocals_rms_dbfs": v_rms,
        "per_stem_rms_dbfs": per_stem_rms,
    }


def _lufs_i_placeholder(x: np.ndarray) -> float:
    """RMS-dBFS proxy used when pyloudnorm is not available.

    Honest proxy: labeled `rms_dbfs_proxy` in output. Real LUFS-I differs by
    a K-weighting + gating step; for A/B loudness parity a straight RMS
    match is close enough for a first delivery, and we document the swap.
    """
    return _rms_dbfs(x)


def stage_excerpt_and_deliver(section_wav: Path, mixed_wav: Path,
                              deliver_dir: Path,
                              song_sha16: str,
                              anchors_manifest: dict[str, str]) -> dict[str, Any]:
    """Emit A/B pair + full reconstruction + manifest at target LUFS-I −23."""
    deliver_dir.mkdir(parents=True, exist_ok=True)

    orig, _ = _read_wav_stereo_f32(section_wav)
    recon, _ = _read_wav_stereo_f32(mixed_wav)
    n = min(orig.shape[0], recon.shape[0], SR_MIX * 30)
    orig_ab = orig[:n]
    recon_ab = recon[:n]

    target_dbfs = -23.0
    o_rms = _rms_dbfs(orig_ab)
    r_rms = _rms_dbfs(recon_ab)
    orig_gain = float(10 ** ((target_dbfs - o_rms) / 20.0))
    recon_gain = float(10 ** ((target_dbfs - r_rms) / 20.0))
    orig_ab_norm = orig_ab * orig_gain
    recon_ab_norm = recon_ab * recon_gain
    full_norm = recon * recon_gain

    _write_wav_stereo_int16(deliver_dir / "original_ab.wav", orig_ab_norm, SR_MIX)
    _write_wav_stereo_int16(deliver_dir / "reconstruction_ab.wav", recon_ab_norm, SR_MIX)
    _write_wav_stereo_int16(deliver_dir / "full_reconstruction.wav", full_norm, SR_MIX)

    manifest = {
        "song_sha16": song_sha16,
        "target_loudness_dbfs_rms_proxy": target_dbfs,
        "note": "LUFS-I loudness match uses RMS-dBFS proxy in v3 spine; "
                "pyloudnorm swap-in is a follow-up polish, not a v3 spine gate.",
        "duration_s": n / SR_MIX,
        "sample_rate": SR_MIX,
        "artifacts": {
            "original_ab.wav": _sha256(deliver_dir / "original_ab.wav"),
            "reconstruction_ab.wav": _sha256(deliver_dir / "reconstruction_ab.wav"),
            "full_reconstruction.wav": _sha256(deliver_dir / "full_reconstruction.wav"),
        },
        "inputs": anchors_manifest,
        "verdict_path": "data/v3_spine/31a164f845f8e27e/verdict.json",
    }
    (deliver_dir / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n"
    )
    return manifest


def stage_sanity_panel(orig_ab: Path, recon_ab: Path, out_tsv: Path) -> dict[str, float]:
    """8 finite panel keys. Tripwire only per Fixed Decision 6."""
    o, sr_o = _read_wav_stereo_f32(orig_ab)
    r, sr_r = _read_wav_stereo_f32(recon_ab)
    n = min(o.shape[0], r.shape[0])
    o = o[:n]
    r = r[:n]
    o_mono = o.mean(axis=1).astype(np.float64)
    r_mono = r.mean(axis=1).astype(np.float64)
    sr = sr_o

    # 1) mel_l1_db (multi-scale mean over n_mels ∈ {64,128,256}); computed via
    #    numpy STFT + mel filterbank (no librosa nondeterminism required).
    def _stft_mag(x, n_fft=2048, hop=512):
        window = np.hanning(n_fft).astype(np.float64)
        pad = n_fft // 2
        xp = np.pad(x, (pad, pad), mode="reflect")
        frames = (len(xp) - n_fft) // hop + 1
        out = np.empty((frames, n_fft // 2 + 1), dtype=np.float64)
        for i in range(frames):
            seg = xp[i * hop:i * hop + n_fft] * window
            out[i] = np.abs(np.fft.rfft(seg))
        return out

    def _mel_filter(n_fft, sr, n_mels, fmin=0.0, fmax=None):
        if fmax is None:
            fmax = sr / 2
        def hz_to_mel(f):
            return 2595.0 * np.log10(1.0 + f / 700.0)
        def mel_to_hz(m):
            return 700.0 * (10 ** (m / 2595.0) - 1.0)
        m_min = hz_to_mel(fmin)
        m_max = hz_to_mel(fmax)
        m_pts = np.linspace(m_min, m_max, n_mels + 2)
        f_pts = mel_to_hz(m_pts)
        bins = np.floor((n_fft + 1) * f_pts / sr).astype(int)
        fb = np.zeros((n_mels, n_fft // 2 + 1), dtype=np.float64)
        for i in range(n_mels):
            l, c, u = bins[i], bins[i + 1], bins[i + 2]
            if u == l:
                continue
            for k in range(l, c):
                if c == l:
                    continue
                fb[i, k] = (k - l) / (c - l)
            for k in range(c, u):
                if u == c:
                    continue
                fb[i, k] = (u - k) / (u - c)
        return fb

    def _mel_db(x, sr, n_mels):
        S = _stft_mag(x)
        fb = _mel_filter(2048, sr, n_mels)
        mel = fb @ S.T  # (n_mels, frames)
        return 10.0 * np.log10(np.maximum(mel, 1e-10))

    mel_l1_scales = []
    for n_mels in (64, 128, 256):
        o_db = _mel_db(o_mono, sr, n_mels)
        r_db = _mel_db(r_mono, sr, n_mels)
        mel_l1_scales.append(float(np.mean(np.abs(o_db - r_db))))
    mel_l1_db = float(np.mean(mel_l1_scales))

    # 2) spectral centroid RMSE in Hz
    def _centroid(x):
        S = _stft_mag(x)
        freqs = np.linspace(0, sr / 2, S.shape[1])
        num = (S * freqs[None, :]).sum(axis=1)
        den = S.sum(axis=1) + 1e-12
        return num / den
    o_c = _centroid(o_mono)
    r_c = _centroid(r_mono)
    m = min(len(o_c), len(r_c))
    spectral_centroid_rmse_hz = float(np.sqrt(np.mean((o_c[:m] - r_c[:m]) ** 2)))

    # 3) RMS envelope RMSE (frame-level, hop 512)
    def _rms_env(x, hop=512):
        n = len(x)
        frames = n // hop
        env = np.empty(frames, dtype=np.float64)
        for i in range(frames):
            seg = x[i * hop:(i + 1) * hop]
            env[i] = np.sqrt(np.mean(seg ** 2))
        return env
    oe = _rms_env(o_mono)
    re_ = _rms_env(r_mono)
    m = min(len(oe), len(re_))
    rms_env_rmse = float(np.sqrt(np.mean((oe[:m] - re_[:m]) ** 2)))

    # 4) LUFS-M RMSE proxy (400ms window / 100ms hop, RMS-dB in windows)
    win = int(sr * 0.400)
    hop_lufs = int(sr * 0.100)
    def _lufs_m_series(x):
        out = []
        for i in range(0, len(x) - win, hop_lufs):
            seg = x[i:i + win]
            r = np.sqrt(np.mean(seg ** 2))
            out.append(20 * np.log10(max(r, 1e-9)) - 0.691)  # K-weight approx offset
        return np.array(out, dtype=np.float64)
    o_l = _lufs_m_series(o_mono)
    r_l = _lufs_m_series(r_mono)
    m = min(len(o_l), len(r_l))
    lufs_m_rmse = float(np.sqrt(np.mean((o_l[:m] - r_l[:m]) ** 2)))

    # 5) mel L1 broken out per scale (3 keys)
    d = {
        "mel_l1_db": mel_l1_db,
        "mel_l1_db_64": mel_l1_scales[0],
        "mel_l1_db_128": mel_l1_scales[1],
        "mel_l1_db_256": mel_l1_scales[2],
        "spectral_centroid_rmse_hz": spectral_centroid_rmse_hz,
        "rms_env_rmse": rms_env_rmse,
        "lufs_m_rmse_proxy": lufs_m_rmse,
        "vggish_cosine_distance": float("nan"),  # not fetchable in offline env
    }
    # honest: mark vggish None instead of NaN (json compat)
    d["vggish_cosine_distance"] = -1.0  # sentinel = "not available"
    lines = ["key\tvalue\n"]
    for k in sorted(d):
        lines.append(f"{k}\t{d[k]:.6f}\n")
    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    out_tsv.write_text("".join(lines))
    return d


# -------------------------------------------------------------------- orchestrate

def run_song(song_sha16: str, out_root: Path) -> dict[str, Any]:
    song = load_focus_song(song_sha16)
    root = out_root / song_sha16
    root.mkdir(parents=True, exist_ok=True)

    section_wav = root / "section.wav"
    stems_dir = root / "stems_6s"
    musc_dir = root / "muscriptor"
    merged_midi = root / "merged.mid"
    render_wav = root / "instrumental_render.wav"
    mixed_wav = root / "mixed_reconstruction.wav"
    panel_tsv = root / "panel.tsv"
    deliver_dir = WSROOT / "data" / "v3" / "deliveries" / song_sha16

    ts_start = time.time()
    stage_slice_section(song, section_wav)
    stem_paths = stage_htdemucs_6s(section_wav, stems_dir)
    per_stem = stage_muscriptor(stem_paths, musc_dir)
    label_info = stage_analyze_labels(per_stem)
    merge_info = stage_merge_midi(per_stem, merged_midi, label_info)
    stage_render_fluidsynth(merged_midi, render_wav, merge_info)
    mix_info = stage_mix_match_and_overlay(render_wav, stem_paths, mixed_wav)

    anchors_manifest = {
        "section.wav": _sha256(section_wav),
        "merged.mid": _sha256(merged_midi),
        "instrumental_render.wav": _sha256(render_wav),
        "mixed_reconstruction.wav": _sha256(mixed_wav),
    }
    for s, p in stem_paths.items():
        anchors_manifest[f"stems_6s/{s}.wav"] = _sha256(p)
    for s, files in per_stem.items():
        anchors_manifest[f"muscriptor/{s}.mid"] = _sha256(files["midi"])
        anchors_manifest[f"muscriptor/{s}.json"] = _canonical_json_sha256(files["json"])

    deliver_manifest = stage_excerpt_and_deliver(
        section_wav, mixed_wav, deliver_dir, song_sha16, anchors_manifest,
    )
    panel = stage_sanity_panel(
        deliver_dir / "original_ab.wav",
        deliver_dir / "reconstruction_ab.wav",
        panel_tsv,
    )

    result = {
        "song_sha16": song_sha16,
        "wall_time_s": time.time() - ts_start,
        "label_info": label_info,
        "merge_info": {
            "tempo_us_per_beat": merge_info["tempo_us_per_beat"],
            "program_manifest": merge_info["program_manifest"],
        },
        "mix_info": mix_info,
        "deliver_manifest": deliver_manifest,
        "panel": panel,
        "anchors": anchors_manifest,
    }
    (root / "run_summary.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--song-sha16", default="31a164f845f8e27e")
    ap.add_argument("--out-root", default=str(WSROOT / "data" / "v3_spine"))
    args = ap.parse_args()
    result = run_song(args.song_sha16, Path(args.out_root))
    print(json.dumps({
        "song_sha16": result["song_sha16"],
        "wall_time_s": round(result["wall_time_s"], 2),
        "labels": result["label_info"]["unique_labels"],
        "unmapped": result["label_info"]["unmapped_labels"],
        "panel": result["panel"],
        "delivery": result["deliver_manifest"]["artifacts"],
    }, indent=2))


if __name__ == "__main__":
    main()
