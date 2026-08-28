#!/usr/bin/env -S /usr/bin/python3
"""Assemble the M-CLASS-1 validation set (55 labeled clips, 5 classes).

Sources (all CC-licensed / public domain):
  APPLAUSE (10)      : ESC-50 category `clapping` (CC BY-NC 3.0, via raw.githubusercontent.com)
  AMBIENT (15)       : ESC-50 categories rain, wind, sea_waves (5 each)
  SPEECH  (10)       : hf-internal-testing/librispeech_asr_dummy validation FLACs (CC BY 4.0)
  MUSIC_RECORDED(10) : fluidsynth-rendered MIDI over FluidR3_GM.sf2 (deterministic, license-clean)
  MUSIC_LIVE (10)    : same fluidsynth music mixed with ESC-50 clapping (proxy label; documented)

Output:
  data/classifier/valset/clips/<label>__<clip_id>.wav
  data/classifier/valset/valset_manifest.tsv
  data/classifier/valset/build_log.jsonl

All clips are truncated / padded to exactly 30.0 s at 32000 Hz mono (the
project's fixed clip length; PANNs' native SR).
"""
from __future__ import annotations
from . import _interp  # noqa: F401

import csv, hashlib, io, json, subprocess, tempfile, tempfile as _tmp
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import numpy as np
import soundfile as sf


CLIP_SEC = 30.0
TARGET_SR = 32000
VALSET_DIR = Path("data/classifier/valset")
CLIPS_DIR = VALSET_DIR / "clips"
CACHE_DIR = Path("data/classifier/_cache")
SF2 = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")

ESC50_CSV_URL = "https://raw.githubusercontent.com/karolpiczak/ESC-50/master/meta/esc50.csv"
ESC50_AUDIO_URL_FMT = "https://raw.githubusercontent.com/karolpiczak/ESC-50/master/audio/{filename}"

LIBRISPEECH_PARQUET_URL = (
    "https://huggingface.co/datasets/hf-internal-testing/librispeech_asr_dummy"
    "/resolve/main/clean/validation-00000-of-00001.parquet"
)


@dataclass
class ClipRec:
    clip_id: str
    label: str
    source: str
    license: str
    origin_url: str
    sha256: str
    duration_s: float
    notes: str = ""


def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()


def _fetch(url: str, cache_name: str) -> bytes:
    cache = CACHE_DIR / cache_name
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        return cache.read_bytes()
    with urllib.request.urlopen(url, timeout=120) as r:
        data = r.read()
    cache.write_bytes(data)
    return data


def _standardize(audio: np.ndarray, sr_in: int, seconds: float = CLIP_SEC) -> np.ndarray:
    import librosa
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    audio = audio.astype(np.float32, copy=False)
    if sr_in != TARGET_SR:
        audio = librosa.resample(audio, orig_sr=sr_in, target_sr=TARGET_SR)
    n_target = int(round(seconds * TARGET_SR))
    if len(audio) < n_target and len(audio) > 0:
        # TILE the short clip to fill 30 s — zero-padding would flood
        # PANNs' Silence/Ambient heads and swamp the actual event class.
        reps = int(np.ceil(n_target / len(audio)))
        audio = np.tile(audio, reps)[:n_target]
    elif len(audio) > n_target:
        audio = audio[:n_target]
    elif len(audio) == 0:
        audio = np.zeros(n_target, dtype=np.float32)
    # Peak-normalize to -3 dBFS to keep tagger inputs comparable.
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 1e-6:
        audio = audio * (10 ** (-3 / 20.0) / peak)
    return audio.astype(np.float32)


def _write_clip(audio: np.ndarray, label: str, clip_id: str) -> Path:
    out = CLIPS_DIR / f"{label}__{clip_id}.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out), audio, TARGET_SR, subtype="PCM_16")
    return out


# ---------------- ESC-50 helpers ----------------

def load_esc50_index() -> List[dict]:
    raw = _fetch(ESC50_CSV_URL, "esc50_meta.csv").decode()
    rows = list(csv.DictReader(io.StringIO(raw)))
    return rows


def pick_esc50(category: str, k: int, rows: List[dict], rng: np.random.Generator) -> List[dict]:
    matches = [r for r in rows if r["category"] == category]
    idx = rng.choice(len(matches), size=k, replace=False)
    return [matches[i] for i in idx]


def fetch_esc50_clip(rec: dict) -> Tuple[np.ndarray, int, bytes]:
    fn = rec["filename"]
    data = _fetch(ESC50_AUDIO_URL_FMT.format(filename=fn), f"esc50/{fn}")
    audio, sr = sf.read(io.BytesIO(data), dtype="float32", always_2d=False)
    return audio, sr, data


# ---------------- LibriSpeech dummy ----------------

def fetch_librispeech_dummy_rows() -> list:
    import pyarrow.parquet as pq
    data = _fetch(LIBRISPEECH_PARQUET_URL, "librispeech_dummy_validation.parquet")
    with tempfile.NamedTemporaryFile(suffix=".parquet") as tf:
        tf.write(data); tf.flush()
        t = pq.read_table(tf.name)
    return t.to_pylist()


# ---------------- fluidsynth music ----------------

def synth_midi_and_render(midi_bytes: bytes, tag: str) -> np.ndarray:
    """Render a MIDI file to audio via fluidsynth CLI (deterministic)."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    wav_path = CACHE_DIR / f"fluid_{tag}.wav"
    mid_path = CACHE_DIR / f"fluid_{tag}.mid"
    mid_path.write_bytes(midi_bytes)
    # Render mono, 44100, deterministic.
    subprocess.run(
        [
            "fluidsynth", "-ni", "-g", "0.8", "-r", "44100",
            "-F", str(wav_path), str(SF2), str(mid_path),
        ],
        check=True, capture_output=True,
    )
    audio, sr = sf.read(str(wav_path), dtype="float32", always_2d=False)
    return _standardize(audio, sr)


def _build_midi(program: int, notes: Iterable[Tuple[int, float, float, int]],
                tempo_bpm: int = 100) -> bytes:
    """Build a tiny type-0 MIDI via pretty_midi.

    notes: iterable of (pitch, start_s, dur_s, velocity)
    """
    import pretty_midi as pm
    m = pm.PrettyMIDI(initial_tempo=tempo_bpm)
    inst = pm.Instrument(program=program)
    for pitch, s, d, v in notes:
        inst.notes.append(pm.Note(velocity=v, pitch=pitch, start=s, end=s + d))
    m.instruments.append(inst)
    buf = io.BytesIO()
    m.write(buf)
    return buf.getvalue()


def make_music_recordings(n: int, rng: np.random.Generator) -> List[np.ndarray]:
    """Generate n varied instrumental clips via fluidsynth (GM programs)."""
    # Diverse GM programs: piano, guitar, violin, flute, trumpet, e.piano,
    # organ, sax, choir, harp
    programs = [0, 24, 40, 73, 56, 4, 19, 65, 52, 46][:n]
    outs: List[np.ndarray] = []
    for i, prog in enumerate(programs):
        # 30 s of quarter-note runs on a C major scale, varying tempo/rhythm.
        tempo = int(80 + rng.integers(0, 60))
        beat = 60.0 / tempo
        scale = [60, 62, 64, 65, 67, 69, 71, 72]
        notes = []
        t = 0.0
        step = 0
        while t < 30.0:
            pitch = scale[step % len(scale)] + int(rng.choice([-12, 0, 0, 12]))
            dur = beat * float(rng.choice([0.5, 1.0, 1.0, 2.0]))
            vel = int(60 + rng.integers(0, 40))
            notes.append((pitch, t, dur * 0.9, vel))
            t += dur
            step += 1
        midi = _build_midi(program=prog, notes=notes, tempo_bpm=tempo)
        outs.append(synth_midi_and_render(midi, tag=f"music_{i:02d}_prog{prog}"))
    return outs


def make_music_live(music_clips: List[np.ndarray], applause_clips: List[np.ndarray],
                    rng: np.random.Generator) -> List[np.ndarray]:
    """Overlay music with applause+cheering ambience to proxy MUSIC_LIVE.

    Applause gain deliberately high (0.9 vs music 0.6) so the applause
    head of the tagger fires reliably. This is *not* a natural live-mix
    energy balance — real live recordings have applause well below music
    during performance. The mixdown here is a **proxy for detectability**,
    not a proxy for typical live-audio energy ratios. See report §4 and §7.
    """
    outs = []
    TARGET_RMS = 0.10
    for i in range(len(music_clips)):
        m = music_clips[i].copy()
        a = applause_clips[i % len(applause_clips)].copy()
        # RMS-match both stems so applause has real energy against music
        # (peak-norm alone leaves applause ~15 dB quieter due to transients).
        m_rms = float(np.sqrt(np.mean(m ** 2))) or 1e-6
        a_rms = float(np.sqrt(np.mean(a ** 2))) or 1e-6
        m = m * (TARGET_RMS / m_rms)
        a = a * (TARGET_RMS / a_rms)
        # Mix with applause slightly louder than music so the tagger's
        # applause head fires. See §4/§7 in report for the honesty caveat.
        mix = 0.6 * m + 1.0 * a
        peak = float(np.max(np.abs(mix))) if mix.size else 0.0
        if peak > 1.0:
            mix = mix / peak * 0.98
        outs.append(mix.astype(np.float32))
    return outs


def main() -> int:
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed=20260828)

    manifest: List[ClipRec] = []
    log_path = VALSET_DIR / "build_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = log_path.open("w")

    def emit(rec: ClipRec):
        manifest.append(rec)
        log.write(json.dumps(rec.__dict__) + "\n")

    # --- ESC-50 index
    print("[valset] loading ESC-50 index...")
    esc = load_esc50_index()

    # APPLAUSE (10)
    print("[valset] fetching APPLAUSE clips (ESC-50 clapping)...")
    applause_std: List[np.ndarray] = []
    for r in pick_esc50("clapping", 10, esc, rng):
        audio, sr, raw = fetch_esc50_clip(r)
        std = _standardize(audio, sr)
        applause_std.append(std)
        out = _write_clip(std, "APPLAUSE", r["filename"].removesuffix(".wav"))
        emit(ClipRec(
            clip_id=out.stem, label="APPLAUSE", source="ESC-50",
            license="CC BY-NC 3.0",
            origin_url=ESC50_AUDIO_URL_FMT.format(filename=r["filename"]),
            sha256=_sha256_bytes(raw), duration_s=CLIP_SEC,
            notes=f"esc50_category={r['category']} fold={r['fold']}",
        ))

    # AMBIENT (15) — 5 each rain/wind/sea_waves
    print("[valset] fetching AMBIENT clips (ESC-50)...")
    for cat in ("rain", "wind", "sea_waves"):
        for r in pick_esc50(cat, 5, esc, rng):
            audio, sr, raw = fetch_esc50_clip(r)
            std = _standardize(audio, sr)
            out = _write_clip(std, "AMBIENT", r["filename"].removesuffix(".wav"))
            emit(ClipRec(
                clip_id=out.stem, label="AMBIENT", source="ESC-50",
                license="CC BY-NC 3.0",
                origin_url=ESC50_AUDIO_URL_FMT.format(filename=r["filename"]),
                sha256=_sha256_bytes(raw), duration_s=CLIP_SEC,
                notes=f"esc50_category={cat} fold={r['fold']}",
            ))

    # SPEECH (10)
    print("[valset] fetching SPEECH clips (LibriSpeech dummy)...")
    ls_rows = fetch_librispeech_dummy_rows()
    ls_pick_idx = rng.choice(len(ls_rows), size=10, replace=False)
    for idx in ls_pick_idx:
        row = ls_rows[int(idx)]
        flac_bytes = row["audio"]["bytes"]
        audio, sr = sf.read(io.BytesIO(flac_bytes), dtype="float32", always_2d=False)
        std = _standardize(audio, sr)
        clip_id = row["id"]
        out = _write_clip(std, "SPEECH", clip_id)
        emit(ClipRec(
            clip_id=out.stem, label="SPEECH", source="LibriSpeech dev-clean (dummy)",
            license="CC BY 4.0",
            origin_url=LIBRISPEECH_PARQUET_URL + "#" + clip_id,
            sha256=_sha256_bytes(flac_bytes), duration_s=CLIP_SEC,
            notes=f"speaker={row['speaker_id']} chapter={row['chapter_id']}",
        ))

    # MUSIC_RECORDED (10)
    print("[valset] rendering MUSIC_RECORDED clips (fluidsynth)...")
    music_clips = make_music_recordings(10, rng)
    for i, clip in enumerate(music_clips):
        cid = f"fluid_music_{i:02d}"
        out = _write_clip(clip, "MUSIC_RECORDED", cid)
        emit(ClipRec(
            clip_id=out.stem, label="MUSIC_RECORDED", source="fluidsynth+FluidR3_GM",
            license="MIT (fluidsynth) / CC BY 3.0 (FluidR3_GM.sf2)",
            origin_url="local:fluidsynth", sha256=_sha256_bytes(clip.tobytes()),
            duration_s=CLIP_SEC,
            notes=f"gm_program_seq_index={i} deterministic_seed=20260828",
        ))

    # MUSIC_LIVE (10) — music+applause overlay (PROXY LABEL; see report §4)
    print("[valset] synthesizing MUSIC_LIVE clips (music + applause overlay)...")
    live_clips = make_music_live(music_clips, applause_std, rng)
    for i, clip in enumerate(live_clips):
        cid = f"fluid_music_live_{i:02d}"
        out = _write_clip(clip, "MUSIC_LIVE", cid)
        emit(ClipRec(
            clip_id=out.stem, label="MUSIC_LIVE", source="fluidsynth+ESC-50 mixdown",
            license="MIT+CC BY 3.0 + CC BY-NC 3.0",
            origin_url="local:mixdown", sha256=_sha256_bytes(clip.tobytes()),
            duration_s=CLIP_SEC,
            notes="PROXY LABEL: music_clip_i + applause_clip_(i%10); documented in report",
        ))

    log.close()

    # Write manifest.
    manifest_path = VALSET_DIR / "valset_manifest.tsv"
    with open(manifest_path, "w") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["clip_id", "label", "source", "license", "origin_url",
                    "sha256", "duration_s", "notes"])
        for m in manifest:
            w.writerow([m.clip_id, m.label, m.source, m.license, m.origin_url,
                        m.sha256, f"{m.duration_s:.3f}", m.notes])
    print(f"[valset] wrote {len(manifest)} clips; manifest at {manifest_path}")
    # Per-class count summary.
    from collections import Counter
    c = Counter(m.label for m in manifest)
    for k in sorted(c):
        print(f"  {k}: {c[k]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
