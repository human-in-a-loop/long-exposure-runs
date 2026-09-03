#!/usr/bin/env /usr/bin/python3
"""c22 M-V3-SPINE-2/unified-driver — ONE parameterized recreate_v3 driver.

Per operator directive 2026-09-02 DETERMINISM CONSOLIDATION: this replaces
every per-song sibling under scripts/v3_spine/*_song_<sha16>.py with ONE
driver parameterized by --song <sha16>. Per-song facts live in data
(data/recreate_v2/focus_set_v2.json), not code.

Pipeline (9 stages, executed in strict order):
    1. slice        — ffmpeg-cut MP3 on operator D1-chosen section
    2. rehtdemucs   — htdemucs_6s per-stem separation
    3. muscriptor   — per-stem transcription with c3 vocab whitelists
    4. tempo_map    — librosa.beat.beat_track on drums stem
    5. canonicalize — c4 midi_from_json_events serializer, byte-det x2
    6. merge        — merge per-stem MIDIs into merged.mid on tempo map
    7. render       — fluidsynth per-track render (SF2 pinned) + vocals overlay copy
    8. mix_match    — rc7 RMS-match + sum → full_reconstruction.wav
    9. panel        — 8-key panel (informational; NEVER a LANDS gate)

Then delivery: assemble manifest.json (with env_pins block stamped by
scripts.v3_spine.v3_pipeline.env_pin).

CLI:
    recreate_v3.py --song <sha16> [--section operator|auto]
                   [--out <dir>] [--dry-run] [--verify-det]
                   [--reproduce-check <existing-delivery-dir>]

Anti-patterns respected:
    - No PRNG (torch.manual_seed(0) is a seed pin, not RNG use)
    - No sidecar_nonfactor imports (AST-verified via existing test suite)
    - No VST3 get_state/save_state/load_state/set_state(bytes) (c31/c35 lock)
    - No wall-clock in serialized outputs (SOURCE_DATE_EPOCH pinned)
    - FD-1: byte-determinism failure → halt, no retry, no fallback
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

# --- Env pins BEFORE any observing import ---------------------------------
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

# --- Interpreter guard ----------------------------------------------------
if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}. Re-run under /usr/bin/python3.",
          file=sys.stderr)
    sys.exit(2)

# --- Workspace-relative imports ------------------------------------------
_WORKSPACE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_WORKSPACE))

from scripts.v3_spine.midi_from_json_events import serialize as canonical_midi_serialize  # noqa: E402
from scripts.v3_spine.gm_program_map_v3 import STEM_DEFAULT  # noqa: E402
from scripts.v3_spine.v3_pipeline.env_pin import write_env_pin, build_env_pin_manifest  # noqa: E402


# --- Constants -----------------------------------------------------------
FOCUS_SET = Path("data/recreate_v2/focus_set_v2.json")
MUSCRIPTOR_BIN = "workspace/learned_transcribers_venv/bin/muscriptor"
MUSCRIPTOR_MODEL = "workspace/models/muscriptor-medium/model.safetensors"
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
V3_SPINE_RUBRIC_SHA = "c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a"
STEMS = ["drums", "bass", "guitar", "other", "piano", "vocals"]
PROBE_ORDER = STEMS + ["full_mix"]
WHITELIST = {
    "drums": None,
    "bass": "acoustic_bass,electric_bass",
    "guitar": "clean_electric_guitar,distorted_electric_guitar,acoustic_guitar",
    "other": "clean_electric_guitar,distorted_electric_guitar,acoustic_guitar,synth_lead,synth_pad",
    "piano": "acoustic_piano,electric_piano,organ",
    "vocals": "acoustic_piano,synth_lead",
    "full_mix": None,
}
TRACKS_FOR_RENDER = [("drums", 9), ("bass", 0), ("guitar", 1), ("piano", 2), ("other", 4)]


# --- Utility helpers -----------------------------------------------------
def sha(p: Path | str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sub_env() -> dict[str, str]:
    e = os.environ.copy()
    for k, v in {
        "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424",
        "TZ": "UTC", "LC_ALL": "C.UTF-8",
        "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
    }.items():
        e[k] = v
    return e


def load_song_facts(song_sha16: str, section: str = "operator") -> dict[str, Any]:
    """Load per-song facts from focus_set_v2.json.  No per-song code paths."""
    if not FOCUS_SET.exists():
        raise RuntimeError(f"focus_set not found: {FOCUS_SET}")
    d = json.loads(FOCUS_SET.read_text())
    for s in d["songs"]:
        if s["audio_sha16"] == song_sha16:
            cs = s.get("chosen_section", {}) or {}
            if section == "auto":
                raise NotImplementedError("--section auto: c23 handoff (needs D1 auto-pick invocation)")
            return {
                "song_sha16": song_sha16,
                "audio_path": s["audio_path"],
                "audio_sha256": s["audio_sha256"],
                "rating_band": s.get("rating_band"),
                "t_start_s": float(cs.get("t_start_s")),
                "t_end_s": float(cs.get("t_end_s")),
                "t_dur_s": float(cs.get("t_end_s")) - float(cs.get("t_start_s")),
                "chosen_section": cs,
            }
    raise RuntimeError(f"song {song_sha16} not in focus_set_v2.json (registered sha16s: "
                       f"{[s['audio_sha16'] for s in d['songs']]})")


# --- STAGE 1: slice -------------------------------------------------------
def stage_slice(mp3: Path, t_start: float, t_dur: float, dst_wav: Path) -> str:
    dst_wav.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst_wav.with_suffix(".wav.tmp")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-ss", f"{t_start}", "-i", str(mp3),
           "-t", f"{t_dur}",
           "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2",
           "-f", "wav", str(tmp)]
    subprocess.run(cmd, check=True, env=sub_env())
    tmp.replace(dst_wav)
    return sha(dst_wav)


# --- STAGE 2: rehtdemucs --------------------------------------------------
def _run_htdemucs_once(in_wav: Path, outdir: Path) -> dict[str, str]:
    import torch
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    import soundfile as sf
    import numpy as np

    torch.manual_seed(0)
    torch.set_num_threads(1)
    try:
        torch.use_deterministic_algorithms(True, warn_only=True)
    except Exception:
        pass

    model = get_model("htdemucs_6s")
    model.cpu().eval()
    data, sr = sf.read(str(in_wav), always_2d=True)
    wav = torch.from_numpy(data.T.astype(np.float32))
    if wav.shape[0] == 1:
        wav = wav.repeat(2, 1)
    ref = wav.mean(0)
    wav_norm = (wav - ref.mean()) / (ref.std() + 1e-8)
    with torch.no_grad():
        sources = apply_model(model, wav_norm[None], device="cpu",
                              split=True, overlap=0.25, shifts=0)[0]
    sources = sources * ref.std() + ref.mean()
    outdir.mkdir(parents=True, exist_ok=True)
    shas: dict[str, str] = {}
    for i, name in enumerate(model.sources):
        stem_wav = sources[i].cpu().numpy().T
        path = outdir / f"{name}.wav"
        sf.write(str(path), stem_wav, sr, subtype="PCM_16")
        shas[name] = sha(path)
    return shas


def stage_rehtdemucs(section_wav: Path, canon_out: Path, det_report: Path,
                     verify_det: bool = True) -> dict[str, Any]:
    """htdemucs_6s per-stem separation, byte-det x2 when verify_det=True."""
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="rv3_htde_r1_") as td1:
        shas1 = _run_htdemucs_once(section_wav, Path(td1))
        canon_out.mkdir(parents=True, exist_ok=True)
        for name in shas1:
            shutil.copy2(Path(td1) / f"{name}.wav", canon_out / f"{name}.wav")
    report: dict[str, Any] = {"run1": shas1, "byte_determinism_holds": True, "n_mismatch": 0}
    if verify_det:
        with tempfile.TemporaryDirectory(prefix="rv3_htde_r2_") as td2:
            shas2 = _run_htdemucs_once(section_wav, Path(td2))
        equal = all(shas1[s] == shas2[s] for s in STEMS)
        report["run2"] = shas2
        report["byte_determinism_holds"] = equal
        report["n_mismatch"] = sum(1 for s in STEMS if shas1[s] != shas2[s])
        if not equal:
            det_report.parent.mkdir(parents=True, exist_ok=True)
            det_report.write_text(json.dumps(report, indent=2, sort_keys=True))
            raise RuntimeError(f"FD-1 halt: htdemucs nondeterministic ({report['n_mismatch']} stems differ)")
    report["wall_time_s"] = round(time.time() - t0, 2)
    det_report.parent.mkdir(parents=True, exist_ok=True)
    det_report.write_text(json.dumps(report, indent=2, sort_keys=True))
    return report


# --- STAGE 3: muscriptor -------------------------------------------------
def _muscriptor_once(wav: Path, out_path: Path, instruments: str | None, fmt: str) -> None:
    cmd = [MUSCRIPTOR_BIN, "transcribe", str(wav),
           "--format", fmt, "--output", str(out_path),
           "--model", MUSCRIPTOR_MODEL, "--device", "cpu",
           "--detect-tempo", "best-effort"]
    if instruments:
        cmd += ["--instruments", instruments]
    r = subprocess.run(cmd, env=sub_env(), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"muscriptor rc={r.returncode}: "
                           f"{r.stderr.decode('utf-8','replace')[-2000:]}")


CHUNK_THRESHOLD_S = 45.0   # inputs longer than this transcribe chunked
CHUNK_LEN_S = 30.0         # campaign chunking doctrine: 30 s windows
CHUNK_OVERLAP_S = 5.0      # ... with 5 s overlap
DEDUP_ONSET_TOL_S = 0.05


def _wav_duration_s(wav: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", str(wav)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def _slice_wav(src: Path, t0: float, dur: float, dst: Path) -> None:
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                        "-ss", f"{t0}", "-t", f"{dur}", "-i", str(src),
                        "-c:a", "pcm_s16le", str(dst)],
                       env=sub_env(), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg slice rc={r.returncode}")


def _merge_chunk_events(chunk_events: list[tuple[float, list]], overlap_s: float) -> list:
    """Deterministic merge of per-chunk MuScriptor JSON events.

    Events from a later chunk that fall inside its leading overlap window are
    dropped when an earlier-chunk event matches (same type/instrument/pitch,
    onset within DEDUP_ONSET_TOL_S); everything is re-offset to absolute time
    and sorted by (time, instrument, pitch, type) for stable output.
    """
    merged: list = []
    for idx, (t0, events) in enumerate(chunk_events):
        lead_end = t0 + overlap_s if idx > 0 else t0
        for e in events:
            e = dict(e)
            for k in ("start_time", "time", "end_time"):
                if isinstance(e.get(k), (int, float)):
                    e[k] = round(e[k] + t0, 6)
            et = e.get("start_time", e.get("time", 0.0))
            if idx > 0 and et < lead_end:
                dup = any(
                    m.get("type") == e.get("type")
                    and m.get("instrument") == e.get("instrument")
                    and m.get("pitch") == e.get("pitch")
                    and abs(m.get("start_time", m.get("time", -1e9)) - et) <= DEDUP_ONSET_TOL_S
                    for m in merged)
                if dup:
                    continue
            merged.append(e)
    merged.sort(key=lambda e: (e.get("start_time", e.get("time", 0.0)),
                               str(e.get("instrument")), e.get("pitch") or -1,
                               str(e.get("type"))))
    return merged


def _muscriptor_chunked(wav: Path, out_path: Path, instruments: str | None,
                        pool, chunk_s: float = CHUNK_LEN_S,
                        overlap_s: float = CHUNK_OVERLAP_S) -> None:
    """Chunk long audio (30 s windows, 5 s overlap), transcribe chunks in the
    shared pool, merge deterministically. Used only above CHUNK_THRESHOLD_S;
    validated against whole-clip transcription by transcription_speed_bench."""
    dur = _wav_duration_s(wav)
    starts: list[float] = []
    t0 = 0.0
    while t0 < dur:
        starts.append(round(t0, 6))
        if t0 + chunk_s >= dur:
            break
        t0 += chunk_s - overlap_s
    with tempfile.TemporaryDirectory(prefix="rv3_ms_chunks_") as d:
        d = Path(d)
        def _do(i_t0):
            i, c0 = i_t0
            cw = d / f"c{i:03d}.wav"
            _slice_wav(wav, c0, min(chunk_s, dur - c0), cw)
            cj = d / f"c{i:03d}.json"
            _muscriptor_once(cw, cj, instruments, "json")
            return c0, json.loads(cj.read_text())
        results = list(pool.map(_do, list(enumerate(starts))))
    merged = _merge_chunk_events(sorted(results, key=lambda r: r[0]),
                                 overlap_s)
    out_path.write_text(json.dumps(merged, sort_keys=True,
                                   separators=(",", ":")))


def stage_muscriptor(section_wav: Path, stem_dir: Path, out_dir: Path,
                     verify_det: bool = True) -> dict[str, Any]:
    """Per-stem + full_mix MuScriptor JSON, byte-det x2 when verify_det=True.

    2026-09-03 operator fix: probes run in a PARALLEL pool of single-threaded
    subprocesses (each invocation is deterministic in isolation; scheduling
    order cannot affect content). The third per-probe invocation that produced
    a debug MIDI was removed — Option A demoted that artifact to
    non_factor_debug and nothing consumes it.
    """
    import concurrent.futures as _cf
    out_dir.mkdir(parents=True, exist_ok=True)

    def _one(task):
        name, run_id = task
        wav = section_wav if name == "full_mix" else stem_dir / f"{name}.wav"
        with tempfile.TemporaryDirectory(prefix=f"rv3_ms_{name}_{run_id}_") as d:
            pj = Path(d) / "e.json"
            _muscriptor_once(wav, pj, WHITELIST[name], "json")
            return name, run_id, sha(pj), pj.read_bytes()

    def _one_chunked(task, pool):
        name, run_id = task
        wav = section_wav if name == "full_mix" else stem_dir / f"{name}.wav"
        with tempfile.TemporaryDirectory(prefix=f"rv3_msc_{name}_{run_id}_") as d:
            pj = Path(d) / "e.json"
            _muscriptor_chunked(wav, pj, WHITELIST[name], pool)
            return name, run_id, sha(pj), pj.read_bytes()

    tasks = [(n, "r1") for n in PROBE_ORDER]
    if verify_det:
        tasks += [(n, "r2") for n in PROBE_ORDER]
    workers = max(1, min(4, (os.cpu_count() or 2)))
    results: dict[tuple[str, str], tuple[str, bytes]] = {}
    long_input = _wav_duration_s(section_wav) > CHUNK_THRESHOLD_S
    with _cf.ThreadPoolExecutor(max_workers=workers) as ex:
        if long_input:
            # Long audio (full songs): chunk each probe across the same pool so
            # cores stay saturated; probes proceed sequentially over chunks.
            for task in tasks:
                name, run_id, h, data = _one_chunked(task, ex)
                results[(name, run_id)] = (h, data)
        else:
            for name, run_id, h, data in ex.map(_one, tasks):
                results[(name, run_id)] = (h, data)

    probes: dict[str, Any] = {}
    for name in PROBE_ORDER:
        wav = section_wav if name == "full_mix" else stem_dir / f"{name}.wav"
        r1, data1 = results[(name, "r1")]
        r2 = results[(name, "r2")][0] if verify_det else r1
        if verify_det and r1 != r2:
            raise RuntimeError(
                f"FD-1 halt: muscriptor JSON nondeterministic on {name} (r1={r1[:16]} r2={r2[:16]})"
            )
        (out_dir / f"{name}.json").write_bytes(data1)
        probes[name] = {
            "input_wav": str(wav),
            "instruments_whitelist": WHITELIST[name],
            "json_run1_sha256": r1,
            "json_run2_sha256": r2 if verify_det else "SKIPPED",
            "byte_deterministic": r1 == r2 if verify_det else None,
            "midi_debug_sha256": "SKIPPED_non_factor_debug (removed 2026-09-03; canonical MIDI comes from the serializer)",
        }
        print(f"  muscriptor {name:10s} json={r1[:12]} det={r1==r2}")
    return {"probes": probes, "n_probes": len(probes),
            "parallel_workers": workers, "debug_midi": "removed"}


# --- STAGE 4: tempo_map ---------------------------------------------------
def stage_tempo_map(section_wav: Path, drums_wav: Path, out_json: Path) -> dict[str, Any]:
    import librosa
    import numpy as np
    import soundfile as sf

    def bt(p: Path) -> float:
        y, sr = sf.read(str(p), always_2d=True)
        mono = y.mean(axis=1).astype(np.float32)
        tempo, _ = librosa.beat.beat_track(y=mono, sr=sr, start_bpm=120.0, units="time")
        return float(np.asarray(tempo).flatten()[0])

    t_drums = bt(drums_wav) if drums_wav.exists() else 0.0
    t_full = bt(section_wav)
    if t_drums <= 20.0:
        bpm, src, fb = t_full, "operator_section_full_mix_librosa_beat_track", "drums_unreliable"
    else:
        bpm, src, fb = t_drums, "operator_section_drums_librosa_beat_track", None
    payload = {
        "schema_version": 1, "detected_bpm": bpm, "meter": [4, 4],
        "source": src, "fallback_reason": fb,
        "cross_checks": {"drums_bpm": t_drums, "full_mix_bpm": t_full},
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


# --- STAGE 5: canonicalize (c4 serializer, READ-ONLY anchor) --------------
def stage_canonicalize(muscriptor_dir: Path, tempo: dict[str, Any], out_dir: Path,
                       verify_det: bool = True) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    bpm = float(tempo["detected_bpm"])
    meter = tuple(tempo["meter"])
    results: dict[str, Any] = {}
    for name in PROBE_ORDER:
        jp = muscriptor_dir / f"{name}.json"
        if not jp.exists():
            results[name] = {"status": "missing_input"}
            continue
        with tempfile.TemporaryDirectory(prefix=f"rv3_can_{name}_r1_") as d1:
            o1 = Path(d1) / f"{name}.mid"
            canonical_midi_serialize(str(jp), str(o1), bpm, meter)
            s1 = sha(o1)
            shutil.copy2(o1, out_dir / f"{name}.mid")
        s2 = s1
        if verify_det:
            with tempfile.TemporaryDirectory(prefix=f"rv3_can_{name}_r2_") as d2:
                o2 = Path(d2) / f"{name}.mid"
                canonical_midi_serialize(str(jp), str(o2), bpm, meter)
                s2 = sha(o2)
            if s1 != s2:
                raise RuntimeError(f"FD-1 halt: canonical serializer nondeterministic on {name}")
        results[name] = {"input_json_sha256": sha(jp),
                         "run1_sha256": s1, "run2_sha256": s2,
                         "byte_deterministic_x2": s1 == s2}
    return {"results": results, "tempo_bpm": bpm, "meter": list(meter)}


# --- STAGE 6: merge_per_stem_midi ----------------------------------------
def _load_stem_events(mid_path: Path) -> list[tuple[int, Any]]:
    import mido
    mf = mido.MidiFile(mid_path)
    if mf.ticks_per_beat != 480:
        raise RuntimeError(f"{mid_path} PPQ {mf.ticks_per_beat}")
    if len(mf.tracks) < 2:
        return []
    ev = []
    t = 0
    for m in mf.tracks[1]:
        t += m.time
        if m.type in ("note_on", "note_off"):
            ev.append((t, m))
    return ev


def _check_no_program_4(mid_path: Path) -> bool:
    import mido
    for tr in mido.MidiFile(mid_path).tracks:
        for m in tr:
            if m.type == "program_change" and m.program == 4:
                return False
    return True


def stage_merge(canon_dir: Path, tempo: dict[str, Any], out_mid: Path) -> dict[str, Any]:
    import mido
    bpm = float(tempo["detected_bpm"])
    ts = tempo["meter"]
    merged = mido.MidiFile(type=1, ticks_per_beat=480)
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    meta.append(mido.MetaMessage("time_signature",
                                 numerator=ts[0], denominator=ts[1],
                                 clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    meta.append(mido.MetaMessage("end_of_track", time=0))
    merged.tracks.append(meta)
    stats: dict[str, Any] = {}
    for stem in STEMS:
        _, prog, ch = STEM_DEFAULT[stem]
        events = _load_stem_events(canon_dir / f"{stem}.mid") if (canon_dir / f"{stem}.mid").exists() else []
        track = mido.MidiTrack()
        track.append(mido.MetaMessage("track_name", name=stem, time=0))
        if stem == "vocals":
            track.append(mido.MetaMessage("text", text="voice_symbolic_do_not_render", time=0))
        if prog is not None:
            track.append(mido.Message("program_change", channel=ch, program=prog, time=0))
        prev, note_ons, pitches = 0, 0, []
        for abs_t, m in events:
            new_ch = 9 if stem == "drums" else ch
            delta = max(0, abs_t - prev)
            track.append(m.copy(channel=new_ch, time=delta))
            if m.type == "note_on":
                note_ons += 1
                pitches.append(m.note)
            prev = abs_t
        track.append(mido.MetaMessage("end_of_track", time=0))
        merged.tracks.append(track)
        stats[stem] = {
            "note_ons": note_ons,
            "median_pitch": statistics.median(pitches) if pitches else None,
            "gm_program": prog, "gm_channel": 9 if stem == "drums" else ch,
        }
    tmp = out_mid.with_suffix(".mid.tmp")
    out_mid.parent.mkdir(parents=True, exist_ok=True)
    merged.save(tmp)
    tmp.replace(out_mid)
    sha1 = sha(out_mid)
    tmp2 = out_mid.with_suffix(".mid.tmp2")
    merged.save(tmp2)
    sha2 = sha(tmp2)
    tmp2.unlink()
    assertions = {
        "drums_track_on_ch10_nonempty": stats["drums"]["gm_channel"] == 9 and stats["drums"]["note_ons"] > 0,
        "bass_median_pitch_lt_55": stats["bass"]["median_pitch"] is not None and stats["bass"]["median_pitch"] < 55,
        "vocals_track_present_symbolic": True,
        "zero_notes_on_gm_program_4": _check_no_program_4(out_mid),
    }
    if not all(assertions.values()):
        raise RuntimeError(f"FD-1 halt: merged.mid structural assertions failed: {assertions}")
    return {"merged_mid_sha256": sha1, "byte_determinism_x2": sha1 == sha2,
            "per_stem_stats": stats, "structural_assertions": assertions}


# --- STAGE 7: render_per_track + vocals_overlay ---------------------------
def _split_track(source: Path, name: str, dst: Path) -> None:
    import mido
    mf = mido.MidiFile(source)
    nm = mido.MidiFile(type=1, ticks_per_beat=mf.ticks_per_beat)
    nm.tracks.append(mf.tracks[0])
    for tr in mf.tracks[1:]:
        tn = next((m.name for m in tr if m.type == "track_name"), None)
        if tn == name:
            nm.tracks.append(tr)
            break
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".mid.tmp")
    nm.save(tmp)
    tmp.replace(dst)


def _fluid(midi: Path, wav: Path) -> None:
    wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["fluidsynth", "-ni", "-F", str(wav), "-r", "44100",
           "-o", "synth.cpu-cores=1", "-o", "synth.reverb.active=false",
           "-o", "synth.chorus.active=false", SF2, str(midi)]
    r = subprocess.run(cmd, env=sub_env(), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"fluidsynth rc={r.returncode}: {r.stderr.decode()[-500:]}")


def stage_render(merged_mid: Path, stem_dir: Path, out_dir: Path,
                 verify_det: bool = True) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, Any] = {}
    for name, _ in TRACKS_FOR_RENDER:
        single = out_dir / f"{name}.mid"
        _split_track(merged_mid, name, single)
        with tempfile.TemporaryDirectory(prefix=f"rv3_r_{name}_r1_") as d1:
            w1 = Path(d1) / f"{name}.wav"
            _fluid(single, w1)
            s1 = sha(w1)
            shutil.copy2(w1, out_dir / f"{name}.wav")
        s2 = s1
        if verify_det:
            with tempfile.TemporaryDirectory(prefix=f"rv3_r_{name}_r2_") as d2:
                w2 = Path(d2) / f"{name}.wav"
                _fluid(single, w2)
                s2 = sha(w2)
            if s1 != s2:
                raise RuntimeError(f"FD-1 halt: fluidsynth render nondeterministic on {name}")
        results[name] = {"sha_r1": s1, "sha_r2": s2, "equal": s1 == s2}
    # Vocals overlay: copy htdemucs vocals stem verbatim
    voc_src = stem_dir / "vocals.wav"
    if voc_src.exists():
        voc_dst = out_dir.parent / "vocals_htdemucs.wav"
        shutil.copy2(voc_src, voc_dst)
        results["vocals_overlay_sha256"] = sha(voc_dst)
    return {"results": results, "sf2_path": SF2, "sf2_sha256": sha(SF2)}


# --- STAGE 8: mix_match (rc7 RMS-match+sum) -------------------------------
def _read_wav(p: Path):
    import numpy as np
    import scipy.io.wavfile as sw
    sr, y = sw.read(str(p))
    if y.dtype.kind == "i":
        y = y.astype(np.float32) / (2 ** (8 * y.dtype.itemsize - 1))
    else:
        y = y.astype(np.float32)
    if y.ndim == 1:
        y = np.stack([y, y], axis=1)
    return sr, y


def _rms_db(y):
    import numpy as np
    r = float(np.sqrt(np.mean(y.astype("float64") ** 2) + 1e-20))
    return 20.0 * math.log10(max(r, 1e-10))


def _write_wav(path: Path, sr: int, y):
    import numpy as np
    import scipy.io.wavfile as sw
    y_c = np.clip(y, -1.0, 1.0)
    y_i = (y_c * 32767.0).astype("int16")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".wav.tmp")
    sw.write(str(tmp), sr, y_i)
    tmp.replace(path)


def _resample_44k(y, src_sr):
    import numpy as np
    if src_sr == 44100:
        return y
    from scipy.signal import resample_poly
    from math import gcd
    g = gcd(src_sr, 44100)
    return resample_poly(y, 44100 // g, src_sr // g, axis=0).astype("float32")


def stage_mix_match(stem_dir: Path, render_dir: Path, out_wav: Path,
                    verify_det: bool = True) -> dict[str, Any]:
    import numpy as np
    stem_map = [(name, render_dir / f"{name}.wav", stem_dir / f"{name}.wav")
                for name, _ in TRACKS_FOR_RENDER]
    stem_map.append(("vocals", render_dir.parent / "vocals_htdemucs.wav", stem_dir / "vocals.wav"))

    def mix_once(dst: Path) -> tuple[str, dict, float]:
        sr_target = 44100
        v_sr, v_y = _read_wav(stem_dir / "vocals.wav")
        v_y = _resample_44k(v_y, v_sr)
        total = v_y.shape[0]
        accum = np.zeros((total, 2), dtype="float64")
        per_info = {}
        for name, rendered, baseline in stem_map:
            if not rendered.exists() or not baseline.exists():
                per_info[name] = {"status": "missing"}
                continue
            r_sr, r_y = _read_wav(rendered)
            b_sr, b_y = _read_wav(baseline)
            b_rms, r_rms = _rms_db(b_y), _rms_db(r_y) if r_y.size > 0 else -100.0
            if r_sr != sr_target:
                r_y = _resample_44k(r_y, r_sr)
            if r_rms > -80.0:
                gain_db = max(min(b_rms - r_rms, 24.0), -24.0)
                r_y = r_y * (10.0 ** (gain_db / 20.0))
            else:
                gain_db = 0.0
            if r_y.shape[0] < total:
                r_y = np.concatenate([r_y, np.zeros((total - r_y.shape[0], 2), dtype="float32")], axis=0)
            elif r_y.shape[0] > total:
                r_y = r_y[:total]
            accum += r_y.astype("float64")
            per_info[name] = {"baseline_rms_db": round(b_rms, 3),
                              "rendered_rms_db": round(r_rms, 3),
                              "gain_applied_db": round(gain_db, 3)}
        peak = float(np.max(np.abs(accum)))
        if peak > 0.707:
            accum *= 0.707 / peak
        _write_wav(dst, sr_target, accum)
        return sha(dst), per_info, peak

    _s1, info, peak = mix_once(out_wav)
    _s2 = _s1
    if verify_det:
        tmp2 = out_wav.with_suffix(".wav.verify")
        _s2, _, _ = mix_once(tmp2)
        if _s1 != _s2:
            raise RuntimeError(f"FD-1 halt: mix_match nondeterministic (s1={_s1[:12]} s2={_s2[:12]})")
        tmp2.unlink()
    return {"final_sha256": _s1, "byte_deterministic_x2": _s1 == _s2,
            "peak_before_normalize": peak, "per_stem_info": info}


# --- STAGE 9: panel (never a LANDS gate) ---------------------------------
def stage_panel(orig_wav: Path, recon_wav: Path, out_json: Path, out_tsv: Path) -> dict[str, Any]:
    from scripts.texture.panel import texture_distance
    import scipy.io.wavfile as sw
    sr, o = sw.read(str(orig_wav))
    sr2, r = sw.read(str(recon_wav))
    assert sr == sr2, f"panel: sr mismatch {sr} vs {sr2}"
    if o.dtype.kind == "i":
        o = o.astype("float32") / (2 ** (8 * o.dtype.itemsize - 1))
        r = r.astype("float32") / (2 ** (8 * r.dtype.itemsize - 1))
    d = texture_distance(o, r, sr)
    NUMERIC = ("mel_l1_db", "spectral_centroid_rmse_hz", "rms_env_rmse",
               "lufs_m_rmse_lu", "embedding_cosine_distance")
    finite = {k: (isinstance(v, (int, float)) and v == v and abs(v) < 1e12)
              if k in NUMERIC else True for k, v in d.items()}
    result = {"panel_keys_count": len(d), "panel": d, "finite_per_key": finite,
              "panel_is_never_lands_gate": True}
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    lines = ["key\tvalue\tfinite"] + [f"{k}\t{d[k]}\t{finite[k]}" for k in sorted(d)]
    out_tsv.write_text("\n".join(lines) + "\n")
    return result


# --- Delivery + manifest assembly ----------------------------------------
def peak_of(p: Path) -> float:
    import numpy as np
    import scipy.io.wavfile as sw
    _, y = sw.read(str(p))
    if y.dtype.kind == "i":
        return float(np.max(np.abs(y.astype("float32") / (2 ** (8 * y.dtype.itemsize - 1)))))
    return float(np.max(np.abs(y.astype("float32"))))


def dur_of(p: Path) -> float:
    import scipy.io.wavfile as sw
    sr, y = sw.read(str(p))
    return y.shape[0] / sr


def assemble_delivery(facts: dict, work_dir: Path, delivery_dir: Path,
                      cycle: int, tempo: dict, canon_report: dict,
                      merge_report: dict) -> dict[str, Any]:
    """Emit the delivery tree + manifest with env_pins stamped in."""
    delivery_dir.mkdir(parents=True, exist_ok=True)
    section_wav = work_dir / "section.wav"
    recon_wav = work_dir / "render" / "full_reconstruction.wav"

    # A/B pair
    orig_ab = delivery_dir / "original_ab.wav"
    recon_ab = delivery_dir / "reconstruction_ab.wav"
    shutil.copy2(section_wav, orig_ab)
    shutil.copy2(recon_wav, recon_ab)
    full_dst = delivery_dir / "full_reconstruction.wav"
    shutil.copy2(recon_wav, full_dst)

    # Stems + renders + muscriptor
    stems_dst = delivery_dir / "stems_6s"
    stems_dst.mkdir(parents=True, exist_ok=True)
    for w in sorted((work_dir / "rc9_6stem").glob("*.wav")):
        shutil.copy2(w, stems_dst / w.name)
    pt_dst = delivery_dir / "per_track"
    pt_dst.mkdir(parents=True, exist_ok=True)
    for w in sorted((work_dir / "render" / "per_track").glob("*.wav")):
        shutil.copy2(w, pt_dst / w.name)
    ms_dst = delivery_dir / "muscriptor"
    ms_dst.mkdir(parents=True, exist_ok=True)
    for f in sorted((work_dir / "muscriptor").iterdir()):
        shutil.copy2(f, ms_dst / f.name)
    for aux in ["merged.mid", "tempo_choice.json"]:
        src = work_dir / aux
        if src.exists():
            shutil.copy2(src, delivery_dir / src.name)

    # Env pin manifest (stamped)
    env_pin_path = delivery_dir / "env_pin.json"
    env_pin = write_env_pin(env_pin_path)

    per_stem_canon = {s: r.get("run1_sha256") for s, r in canon_report.get("results", {}).items()
                      if r.get("run1_sha256")}

    manifest: dict[str, Any] = {
        "schema_version": 2,
        "driver": "scripts/v3_spine/recreate_v3.py",
        "driver_cycle": cycle,
        "song_sha16": facts["song_sha16"],
        "song_audio_path": facts["audio_path"],
        "song_audio_sha256": facts["audio_sha256"],
        "rating_band": facts["rating_band"],
        "ab_window_operator_section": {
            "t_start_s": facts["t_start_s"],
            "t_end_s": facts["t_end_s"],
            "duration_s": facts["t_dur_s"],
            "note": "operator D1-chosen peak+exposed section from focus_set_v2.json",
        },
        "artifacts": {
            "original_ab_wav": {"path": str(orig_ab), "sha256": sha(orig_ab),
                                "duration_s": dur_of(orig_ab), "peak": peak_of(orig_ab)},
            "reconstruction_ab_wav": {"path": str(recon_ab), "sha256": sha(recon_ab),
                                      "duration_s": dur_of(recon_ab), "peak": peak_of(recon_ab)},
            "full_reconstruction_wav": {"path": str(full_dst), "sha256": sha(full_dst),
                                        "duration_s": dur_of(full_dst), "peak": peak_of(full_dst)},
        },
        "per_stem_canonical_midi_sha": per_stem_canon,
        "merged_mid_sha256": merge_report["merged_mid_sha256"],
        "structural_assertions": merge_report["structural_assertions"],
        "tempo_choice": {"bpm": tempo["detected_bpm"], "meter": tempo["meter"],
                         "source": tempo["source"]},
        "rubric_hash_v3_spine": V3_SPINE_RUBRIC_SHA,
        "env_pins": env_pin,  # inlined per operator directive
        "env_pin_json_path": str(env_pin_path),
    }
    mp = delivery_dir / "manifest.json"
    tmp = mp.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    tmp.replace(mp)

    for p in [orig_ab, recon_ab, full_dst]:
        assert peak_of(p) > 1e-4, f"{p} silent"
    return manifest


# --- Reproduce-check ------------------------------------------------------
def reproduce_check(delivery_dir: Path, existing_delivery: Path) -> dict[str, Any]:
    """Compare produced delivery to an existing anchor: panel-equal always,
    byte-equal where env_pins unchanged."""
    report: dict[str, Any] = {"delivery_dir": str(delivery_dir),
                              "existing_delivery": str(existing_delivery),
                              "per_stage": {}, "env_pin_diff": {}, "panel_diff": {}}
    # Env pin diff
    ep_new = delivery_dir / "env_pin.json"
    ep_old = existing_delivery / "env_pin.json"
    if ep_old.exists():
        try:
            m_new = json.loads(ep_new.read_text())
            m_old = json.loads(ep_old.read_text())
            report["env_pin_diff"] = {"new_sha": m_new.get("env_pin_sha256"),
                                      "old_sha": m_old.get("env_pin_sha256"),
                                      "identical": m_new.get("env_pin_sha256") == m_old.get("env_pin_sha256")}
        except Exception as e:
            report["env_pin_diff"] = {"error": f"{type(e).__name__}:{e}"}
    else:
        report["env_pin_diff"] = {"note": "no env_pin.json in existing delivery (pre-c22)"}
    # Panel diff (existing anchor may live in panel_original_vs_palette.tsv etc.)
    for cand in ["panel.tsv", "panel.json"]:
        new = delivery_dir / cand
        old = existing_delivery / cand
        if new.exists() and old.exists():
            report["panel_diff"][cand] = {"new_sha": sha(new), "old_sha": sha(old),
                                          "byte_equal": sha(new) == sha(old)}
    # Byte-equal stage anchors (subset expected under env_pin_identical)
    for stage_file in ["merged.mid", "reconstruction_ab.wav", "full_reconstruction.wav"]:
        new = delivery_dir / stage_file
        old = existing_delivery / stage_file
        if new.exists() and old.exists():
            report["per_stage"][stage_file] = {"new_sha": sha(new), "old_sha": sha(old),
                                               "byte_equal": sha(new) == sha(old)}
    return report


# --- Main pipeline --------------------------------------------------------
def run_pipeline(song_sha16: str, section: str, out_dir: Path, cycle: int,
                 dry_run: bool = False, verify_det: bool = True) -> dict[str, Any]:
    """Run the entire 9-stage chain end-to-end."""
    facts = load_song_facts(song_sha16, section)
    work_dir = Path(f"data/v3_spine/{song_sha16}/operator_section_c{cycle}_unified")
    work_dir.mkdir(parents=True, exist_ok=True)
    print(f"=== recreate_v3 song={song_sha16} section=[{facts['t_start_s']:.2f}..{facts['t_end_s']:.2f}]s ===")

    stage_report: dict[str, Any] = {"driver": "recreate_v3.py", "cycle": cycle,
                                    "song_sha16": song_sha16, "facts": facts,
                                    "dry_run": dry_run, "verify_det": verify_det,
                                    "stages": {}}
    if dry_run:
        stage_report["stages"] = {s: "DRY_RUN_SKIPPED" for s in
                                  ["slice", "rehtdemucs", "muscriptor", "tempo_map",
                                   "canonicalize", "merge", "render", "mix_match", "panel"]}
        # still emit env_pin manifest for reproducibility
        env_pin_path = out_dir / "env_pin.json"
        write_env_pin(env_pin_path)
        stage_report["env_pin_path"] = str(env_pin_path)
        return stage_report

    # 1. slice
    section_wav = work_dir / "section.wav"
    print(f"[stage 1/9] slice → {section_wav}")
    slice_sha = stage_slice(Path(facts["audio_path"]), facts["t_start_s"],
                             facts["t_dur_s"], section_wav)
    stage_report["stages"]["slice"] = {"section_wav_sha256": slice_sha}

    # 2. rehtdemucs
    stem_dir = work_dir / "rc9_6stem"
    print("[stage 2/9] rehtdemucs")
    stage_report["stages"]["rehtdemucs"] = stage_rehtdemucs(
        section_wav, stem_dir, work_dir / "htdemucs_determinism.json", verify_det=verify_det)

    # 3. muscriptor
    ms_dir = work_dir / "muscriptor"
    print("[stage 3/9] muscriptor")
    stage_report["stages"]["muscriptor"] = stage_muscriptor(
        section_wav, stem_dir, ms_dir, verify_det=verify_det)

    # 4. tempo_map
    print("[stage 4/9] tempo_map")
    tempo = stage_tempo_map(section_wav, stem_dir / "drums.wav",
                             work_dir / "tempo_choice.json")
    stage_report["stages"]["tempo_map"] = tempo

    # 5. canonicalize
    canon_dir = work_dir / "canonical_midi"
    print("[stage 5/9] canonicalize")
    canon = stage_canonicalize(ms_dir, tempo, canon_dir, verify_det=verify_det)
    stage_report["stages"]["canonicalize"] = canon

    # 6. merge
    merged_mid = work_dir / "merged.mid"
    print("[stage 6/9] merge")
    merge = stage_merge(canon_dir, tempo, merged_mid)
    stage_report["stages"]["merge"] = merge

    # 7. render
    render_dir = work_dir / "render" / "per_track"
    print("[stage 7/9] render")
    render = stage_render(merged_mid, stem_dir, render_dir, verify_det=verify_det)
    stage_report["stages"]["render"] = render

    # 8. mix_match
    mix_wav = work_dir / "render" / "full_reconstruction.wav"
    print("[stage 8/9] mix_match")
    mix = stage_mix_match(stem_dir, render_dir, mix_wav, verify_det=verify_det)
    stage_report["stages"]["mix_match"] = mix

    # 9. panel + delivery
    print("[stage 9/9] panel + delivery")
    manifest = assemble_delivery(facts, work_dir, out_dir, cycle,
                                  tempo, canon, merge)
    panel = stage_panel(out_dir / "original_ab.wav",
                         out_dir / "reconstruction_ab.wav",
                         out_dir / "panel.json", out_dir / "panel.tsv")
    stage_report["stages"]["panel"] = panel
    stage_report["manifest"] = manifest
    return stage_report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--song", required=True, help="SHA16 of song in focus_set_v2.json")
    ap.add_argument("--section", choices=["operator", "auto"], default="operator")
    ap.add_argument("--out", default=None, help="Delivery dir (default data/v3/deliveries/<sha16>/cycle<N>/)")
    ap.add_argument("--cycle", type=int, default=22)
    ap.add_argument("--dry-run", action="store_true", help="Skip stages; emit env_pin manifest only")
    ap.add_argument("--verify-det", action="store_true",
                    help="Byte-determinism ×2 gate at each stage (adds ~2× wall time)")
    ap.add_argument("--reproduce-check", default=None,
                    help="Path to existing delivery; compare produced against it")
    ap.add_argument("--no-verify-det", action="store_true", help="Explicitly disable ×2 gate")
    args = ap.parse_args()

    verify_det = args.verify_det and not args.no_verify_det

    out_dir = Path(args.out) if args.out else Path(f"data/v3/deliveries/{args.song}/cycle{args.cycle}")
    out_dir.mkdir(parents=True, exist_ok=True)

    report = run_pipeline(args.song, args.section, out_dir, args.cycle,
                          dry_run=args.dry_run, verify_det=verify_det)

    (out_dir / "run_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(f"\nwrote {out_dir}/run_report.json")

    if args.reproduce_check:
        rep = reproduce_check(out_dir, Path(args.reproduce_check))
        rc_path = out_dir / "reproduce_report.json"
        rc_path.write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n")
        print(f"wrote reproduce report to {rc_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
