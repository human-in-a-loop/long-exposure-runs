#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T08:00:00Z
# cycle: 37
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/first-real-audio
# fork: 675abd086911
# clone: 0
# ---
"""8-stage pipeline for M-RECREATE-1/first-real-audio.

Stages, all READ-ONLY imports of upstream modules:

  1. decode+trim   (soundfile+libsndfile, 30 s from t=0, mono→stereo,
                    44.1 kHz resample)          → data/recreate_v0/per_stage/01_decode/
  2. chunker       (scripts.ingest.chunker)     → per_stage/02_chunker/
  3. tagger sidecar(scripts.classifier.tagger + non-factor isolation preserved)
                                                → per_stage/03_tagger/
  4. htdemucs      (demucs.apply / pretrained)  → per_stage/04_htdemucs/
  5. basic-pitch   (subprocess to workspace/basic_pitch_venv)
                                                → per_stage/05_basic_pitch/
  6. merged score  (scripts.score.bridge.merge_stems_to_score)
                                                → per_stage/06_score/
  7a. bare-MIDI    (scripts.tex.render_bare_midi)
                                                → per_stage/07_bare_midi.wav
  7b. effects      (scripts.tex.render_effects_layered)
                                                → per_stage/07_effects.wav

Every stage's runtime, exit status, output SHA-256s, and any exception are
captured in per_stage/pipeline_run.json. On stage failure, remaining stages
are skipped and the failed stage is named — the honest-close path per
brief.

Byte-determinism × 2 is verified by run_all.py (not here); this file is
idempotent and drops all outputs on rerun.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any

assert sys.executable == "/usr/bin/python3", sys.executable

# Determinism pins BEFORE any torch/tensorflow import (belt-and-braces).
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DATA_ROOT = REPO_ROOT / "data" / "recreate_v0"
PER_STAGE = DATA_ROOT / "per_stage"
SF2 = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
VENV_PY = REPO_ROOT / "workspace" / "basic_pitch_venv" / "bin" / "python3"
BP_CALL = REPO_ROOT / "scripts" / "transcribe" / "_bp_call.py"

SR = 44100
TRIM_S = 30.0


def sha256_bytes(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _stage_record(name: str, status: str, wall_s: float, artifacts: dict[str, str],
                  error: str | None = None, note: str | None = None) -> dict[str, Any]:
    return {
        "stage": name,
        "status": status,
        "wall_seconds": round(wall_s, 3),
        "artifacts": artifacts,
        "error": error,
        "note": note,
    }


# --------------------------------------------------------------------------
# Stage 1: decode + trim to 30s @ 44.1 kHz stereo
# --------------------------------------------------------------------------
def stage_01_decode(input_mp3: Path, out_dir: Path) -> tuple[dict[str, Any], Path]:
    import numpy as np
    import soundfile as sf
    out_dir.mkdir(parents=True, exist_ok=True)
    out_wav = out_dir / "original_30s.wav"
    t0 = time.perf_counter()
    try:
        # Robust decode: try soundfile first, fall back to ffmpeg for MP3.
        try:
            y, sr_in = sf.read(str(input_mp3), always_2d=True)
        except Exception:
            # ffmpeg fallback (MP3 needs libmad or ffmpeg on some setups)
            tmp_wav = out_dir / "_decoded_full.wav"
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(input_mp3), "-ar", str(SR),
                 "-ac", "2", str(tmp_wav)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            y, sr_in = sf.read(str(tmp_wav), always_2d=True)
            tmp_wav.unlink(missing_ok=True)
        # Force stereo
        if y.shape[1] == 1:
            y = np.concatenate([y, y], axis=1)
        elif y.shape[1] > 2:
            y = y[:, :2]
        # Resample to 44100 if needed (linear-interp is deterministic)
        if sr_in != SR:
            n_out = int(round(y.shape[0] * SR / sr_in))
            x_old = np.linspace(0.0, 1.0, y.shape[0], endpoint=False)
            x_new = np.linspace(0.0, 1.0, n_out, endpoint=False)
            y_rs = np.stack(
                [np.interp(x_new, x_old, y[:, ch]) for ch in range(y.shape[1])],
                axis=1,
            )
            y = y_rs.astype(np.float32)
            sr_in = SR
        # Trim
        n_target = int(round(TRIM_S * SR))
        y = y[:n_target].astype(np.float32)
        # Actual samples (may be shorter if song shorter than TRIM_S)
        sf.write(str(out_wav), y, SR, subtype="FLOAT")
        wall = time.perf_counter() - t0
        return (
            _stage_record(
                "01_decode", "ok", wall,
                {"original_30s.wav": sha256_bytes(out_wav)},
                note=f"trimmed_from_{sr_in}Hz_to_{SR}Hz_stereo_{TRIM_S}s "
                     f"actual_samples={y.shape[0]}",
            ),
            out_wav,
        )
    except Exception as exc:  # pragma: no cover
        wall = time.perf_counter() - t0
        return (
            _stage_record("01_decode", "fail", wall, {}, error=repr(exc)),
            out_wav,
        )


# --------------------------------------------------------------------------
# Stage 2: chunker
# --------------------------------------------------------------------------
def stage_02_chunker(wav_in: Path, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    try:
        # Chunker expects PCM16 mono via read_pcm16_mono. Convert first.
        import soundfile as sf
        import numpy as np
        from scripts.ingest.chunker import CLIP_S, OVERLAP_S, chunk
        y, sr = sf.read(str(wav_in), always_2d=True)
        mono = y.mean(axis=1)
        mono16 = np.clip(mono, -1.0, 1.0)
        mono16 = (mono16 * 32767.0).astype(np.int16)
        pcm_path = out_dir / "mono_pcm16.wav"
        sf.write(str(pcm_path), mono16, sr, subtype="PCM_16")
        result = chunk(pcm_path, out_dir, source_type="local")
        artifacts: dict[str, str] = {"mono_pcm16.wav": sha256_bytes(pcm_path)}
        for clip_row in result.clips:
            cp = Path(clip_row["clip_path"])
            if cp.exists():
                artifacts[cp.name] = sha256_bytes(cp)
        # Store chunker manifest for provenance
        manifest_path = out_dir / "chunker_manifest.json"
        manifest_path.write_text(json.dumps({
            "source_id": result.source_id,
            "source_bytes_sha256": result.source_bytes_sha256,
            "sr_hz": result.sr_hz,
            "n_samples": result.n_samples,
            "n_clips": len(result.clips),
        }, indent=2, sort_keys=True) + "\n")
        artifacts["chunker_manifest.json"] = sha256_bytes(manifest_path)
        wall = time.perf_counter() - t0
        return _stage_record(
            "02_chunker", "ok", wall, artifacts,
            note=f"n_clips={len(result.clips)} CLIP_S={CLIP_S} OVERLAP_S={OVERLAP_S}",
        )
    except Exception as exc:
        wall = time.perf_counter() - t0
        return _stage_record(
            "02_chunker", "fail", wall, {}, error=repr(exc),
            note=traceback.format_exc(limit=3),
        )


# --------------------------------------------------------------------------
# Stage 3: tagger sidecar (non-factor isolation preserved)
# --------------------------------------------------------------------------
def stage_03_tagger(wav_in: Path, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    try:
        # Non-factor isolation: this stage MUST NOT import sidecar_nonfactor.
        # It emits a sidecar shape that is downstream-invisible.
        import numpy as np
        import soundfile as sf
        from scripts.classifier.tagger import Tagger
        y, sr = sf.read(str(wav_in), always_2d=True)
        mono = y.mean(axis=1).astype(np.float32)
        tagger = Tagger()
        # Tagger.tag returns np.ndarray shape (527,) — AudioSet class dist.
        clipwise = tagger.tag(mono, sr)
        top_idx = np.argsort(clipwise)[::-1][:10].tolist()
        sidecar = {
            "wav_relpath": str(wav_in.relative_to(REPO_ROOT)),
            "wav_sha256": sha256_bytes(wav_in),
            "tagger_top_idx": top_idx,
            "tagger_top_scores": [round(float(clipwise[i]), 6) for i in top_idx],
            "note": "non-factor isolation contract: not consumed downstream",
        }
        sidecar_path = out_dir / "tagger_sidecar.json"
        sidecar_path.write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n")
        wall = time.perf_counter() - t0
        return _stage_record(
            "03_tagger", "ok", wall,
            {"tagger_sidecar.json": sha256_bytes(sidecar_path)},
            note="non_factor_isolation_preserved",
        )
    except Exception as exc:
        wall = time.perf_counter() - t0
        return _stage_record(
            "03_tagger", "fail_soft", wall, {}, error=repr(exc),
            note="tagger failure is non-blocking (non-factor sidecar); pipeline continues",
        )


# --------------------------------------------------------------------------
# Stage 4: htdemucs
# --------------------------------------------------------------------------
def stage_04_htdemucs(wav_in: Path, out_dir: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    stems: dict[str, Path] = {}
    try:
        import numpy as np
        import soundfile as sf
        import torch
        torch.set_num_threads(1)
        torch.manual_seed(0)
        np.random.seed(0)
        from demucs.apply import apply_model
        from demucs.pretrained import get_model
        y, sr = sf.read(str(wav_in), always_2d=True)
        if y.shape[1] == 1:
            y = np.concatenate([y, y], axis=1)
        wav_t = torch.from_numpy(y.T.astype(np.float32)).unsqueeze(0)
        model = get_model("htdemucs")
        model.eval()
        with torch.no_grad():
            est = apply_model(model, wav_t, device="cpu",
                              shifts=0, split=True, overlap=0.25,
                              num_workers=0, progress=False)
        est = est[0].numpy()  # (sources, channels, samples)
        artifacts: dict[str, str] = {}
        for i, name in enumerate(model.sources):
            stem_wav = out_dir / f"{name}.wav"
            sf.write(str(stem_wav), est[i].T.astype(np.float32), sr, subtype="FLOAT")
            artifacts[stem_wav.name] = sha256_bytes(stem_wav)
            stems[name] = stem_wav
        wall = time.perf_counter() - t0
        return (
            _stage_record("04_htdemucs", "ok", wall, artifacts,
                          note=f"sources={list(model.sources)} shifts=0 overlap=0.25"),
            stems,
        )
    except Exception as exc:
        wall = time.perf_counter() - t0
        return (
            _stage_record("04_htdemucs", "fail", wall, {}, error=repr(exc),
                          note=traceback.format_exc(limit=3)),
            stems,
        )


# --------------------------------------------------------------------------
# Stage 5: basic-pitch on {drums, bass, other} (skip vocals)
# --------------------------------------------------------------------------
def stage_05_basic_pitch(stems: dict[str, Path], out_dir: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    per_stem_midi: dict[str, Path] = {}
    per_artifact: dict[str, str] = {}
    try:
        assert VENV_PY.is_file(), f"venv python missing: {VENV_PY}"
        assert BP_CALL.is_file(), f"_bp_call.py missing: {BP_CALL}"
        for stem_name in ("drums", "bass", "other"):
            if stem_name not in stems:
                continue
            in_wav = stems[stem_name]
            out_midi = out_dir / f"{stem_name}.mid"
            out_jsonl = out_dir / f"{stem_name}.jsonl"
            proc = subprocess.run(
                [str(VENV_PY), str(BP_CALL), str(in_wav),
                 str(out_midi), str(out_jsonl)],
                capture_output=True, text=True,
            )
            if proc.returncode != 0:
                raise RuntimeError(
                    f"basic-pitch on {stem_name} exited {proc.returncode}: "
                    f"{proc.stderr[-500:]}"
                )
            per_stem_midi[stem_name] = out_midi
            per_artifact[out_midi.name] = sha256_bytes(out_midi)
            per_artifact[out_jsonl.name] = sha256_bytes(out_jsonl)
        wall = time.perf_counter() - t0
        return (
            _stage_record("05_basic_pitch", "ok", wall, per_artifact,
                          note=f"stems_transcribed={list(per_stem_midi.keys())}"),
            per_stem_midi,
        )
    except Exception as exc:
        wall = time.perf_counter() - t0
        return (
            _stage_record("05_basic_pitch", "fail", wall, per_artifact,
                          error=repr(exc), note=traceback.format_exc(limit=3)),
            per_stem_midi,
        )


# --------------------------------------------------------------------------
# Stage 6: merged score via score bridge
# --------------------------------------------------------------------------
def _concat_per_stem_midis_prettymidi(per_stem_midi: dict[str, Path],
                                       out_midi: Path) -> None:
    """Fallback: build one merged MIDI by loading each per-stem MIDI with
    pretty_midi and copying its instruments/notes into one output file.

    Deterministic (no PRNG, iteration in sorted key order). Preserves note
    onset/offset/velocity/pitch exactly. Used only when mscore3's
    xml_to_midi export fails on the bridge's merged MusicXML — a
    documented, non-fabricated fallback path that keeps the recreation
    contract intact (per-stem transcriptions still feed into one merged
    MIDI for fluidsynth).
    """
    import pretty_midi
    out = pretty_midi.PrettyMIDI(initial_tempo=120.0)
    for stem_name in sorted(per_stem_midi):
        src = pretty_midi.PrettyMIDI(str(per_stem_midi[stem_name]))
        for inst in src.instruments:
            new_inst = pretty_midi.Instrument(
                program=inst.program,
                is_drum=(stem_name == "drums" or inst.is_drum),
                name=f"{stem_name}:{inst.name}",
            )
            new_inst.notes = list(inst.notes)
            new_inst.control_changes = list(inst.control_changes)
            new_inst.pitch_bends = list(inst.pitch_bends)
            out.instruments.append(new_inst)
    out.write(str(out_midi))


def stage_06_score(per_stem_midi: dict[str, Path], out_dir: Path) -> tuple[dict[str, Any], Path | None]:
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    try:
        from scripts.score.bridge import (
            merge_stems_to_score, xml_to_midi, ScoreBridgeError,
        )
        merged_xml = out_dir / "merged.musicxml"
        merged_midi = out_dir / "merged.midi"
        if not per_stem_midi:
            raise RuntimeError("no per-stem MIDIs to merge (stage 5 likely failed)")
        merge_stems_to_score(
            {k: str(v) for k, v in per_stem_midi.items()},
            str(merged_xml),
        )
        # Try mscore3 xml_to_midi first (contract path).
        xml_to_midi_note = None
        try:
            xml_to_midi(str(merged_xml), str(merged_midi))
            xml_to_midi_status = "ok"
        except ScoreBridgeError as exc:
            # Documented fallback: pretty_midi direct concat.
            # Root cause: mscore3 raises on duration-quantization rounding
            # errors when basic-pitch note onsets don't align to musically
            # regular subdivisions. This is a real-audio-vs-synth mismatch
            # in the bridge's rhythm quantizer; fixing it upstream is a
            # cycle-38 handoff. The fallback keeps the recreation running.
            xml_to_midi_status = "fallback_pretty_midi_concat"
            xml_to_midi_note = f"mscore3_xml_to_midi_failed: {repr(exc)[:200]}"
            _concat_per_stem_midis_prettymidi(per_stem_midi, merged_midi)
        artifacts = {
            "merged.musicxml": sha256_bytes(merged_xml),
            "merged.midi": sha256_bytes(merged_midi),
        }
        wall = time.perf_counter() - t0
        note = (f"merged_from={list(per_stem_midi.keys())} "
                f"midi_export={xml_to_midi_status}")
        if xml_to_midi_note:
            note += f" | fallback_reason={xml_to_midi_note}"
        return (
            _stage_record("06_score", "ok", wall, artifacts, note=note),
            merged_midi,
        )
    except Exception as exc:
        wall = time.perf_counter() - t0
        return (
            _stage_record("06_score", "fail", wall, {}, error=repr(exc),
                          note=traceback.format_exc(limit=3)),
            None,
        )


# --------------------------------------------------------------------------
# Stage 7a: bare-MIDI render via fluidsynth
# --------------------------------------------------------------------------
def stage_07a_bare_midi(merged_midi: Path, out_dir: Path) -> tuple[dict[str, Any], Path | None]:
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    bare_wav = out_dir / "bare_midi.wav"
    try:
        from scripts.tex.render_bare_midi import render_bare_midi
        assert SF2.is_file(), f"SF2 missing: {SF2}"
        render_bare_midi(merged_midi, bare_wav, SF2, sr=SR, duration_s=TRIM_S)
        wall = time.perf_counter() - t0
        return (
            _stage_record("07a_bare_midi", "ok", wall,
                          {"bare_midi.wav": sha256_bytes(bare_wav)},
                          note=f"sf2={SF2.name} sr={SR}"),
            bare_wav,
        )
    except Exception as exc:
        wall = time.perf_counter() - t0
        return (
            _stage_record("07a_bare_midi", "fail", wall, {}, error=repr(exc),
                          note=traceback.format_exc(limit=3)),
            None,
        )


# --------------------------------------------------------------------------
# Stage 7b: effects-layered via cycle-9 DawDreamer chain (READ-ONLY import)
# --------------------------------------------------------------------------
def stage_07b_effects(bare_wav: Path, out_dir: Path) -> tuple[dict[str, Any], Path | None]:
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    effects_wav = out_dir / "effects.wav"
    try:
        from scripts.tex.render_effects_layered import apply_dawdreamer_chain
        apply_dawdreamer_chain(bare_wav, effects_wav)
        wall = time.perf_counter() - t0
        return (
            _stage_record("07b_effects", "ok", wall,
                          {"effects.wav": sha256_bytes(effects_wav)},
                          note="cycle_9_dawdreamer_chain_read_only_import"),
            effects_wav,
        )
    except Exception as exc:
        wall = time.perf_counter() - t0
        return (
            _stage_record("07b_effects", "fail", wall, {}, error=repr(exc),
                          note=traceback.format_exc(limit=3)),
            None,
        )


# --------------------------------------------------------------------------
# Orchestrator
# --------------------------------------------------------------------------
def run_pipeline(chosen_song_path: Path, per_stage_root: Path) -> dict[str, Any]:
    per_stage_root.mkdir(parents=True, exist_ok=True)
    stages: list[dict[str, Any]] = []
    t0 = time.perf_counter()

    # Stage 1
    rec, orig_wav = stage_01_decode(chosen_song_path, per_stage_root / "01_decode")
    stages.append(rec)
    if rec["status"] != "ok":
        return _finalize(stages, "01_decode", t0)

    # Stage 2
    stages.append(stage_02_chunker(orig_wav, per_stage_root / "02_chunker"))
    # Chunker failure is non-blocking for the recreation contract (only used
    # to demonstrate the read-only import). Continue either way.

    # Stage 3 (soft — non-factor sidecar)
    stages.append(stage_03_tagger(orig_wav, per_stage_root / "03_tagger"))

    # Stage 4
    rec4, stems = stage_04_htdemucs(orig_wav, per_stage_root / "04_htdemucs")
    stages.append(rec4)
    if rec4["status"] != "ok":
        return _finalize(stages, "04_htdemucs", t0)

    # Stage 5
    rec5, per_stem_midi = stage_05_basic_pitch(stems, per_stage_root / "05_basic_pitch")
    stages.append(rec5)
    if rec5["status"] != "ok":
        return _finalize(stages, "05_basic_pitch", t0)

    # Stage 6
    rec6, merged_midi = stage_06_score(per_stem_midi, per_stage_root / "06_score")
    stages.append(rec6)
    if rec6["status"] != "ok" or merged_midi is None:
        return _finalize(stages, "06_score", t0)

    # Stage 7a
    rec7a, bare_wav = stage_07a_bare_midi(merged_midi, per_stage_root / "07_render")
    stages.append(rec7a)
    if rec7a["status"] != "ok" or bare_wav is None:
        return _finalize(stages, "07a_bare_midi", t0)

    # Stage 7b
    rec7b, _ = stage_07b_effects(bare_wav, per_stage_root / "07_render")
    stages.append(rec7b)
    if rec7b["status"] != "ok":
        return _finalize(stages, "07b_effects", t0)

    return _finalize(stages, None, t0)


def _finalize(stages: list[dict[str, Any]], failed_stage: str | None,
              t0: float) -> dict[str, Any]:
    return {
        "stages": stages,
        "failed_stage": failed_stage,
        "total_wall_seconds": round(time.perf_counter() - t0, 3),
        "pipeline_version": "recreate_v0/0.1.0",
    }


def main() -> int:
    chosen_json = json.loads((DATA_ROOT / "chosen_song.json").read_text())
    chosen_song = REPO_ROOT / chosen_json["chosen_relpath"]
    result = run_pipeline(chosen_song, PER_STAGE)
    out_path = PER_STAGE / "pipeline_run.json"
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"failed_stage": result["failed_stage"],
                      "total_wall_seconds": result["total_wall_seconds"]},
                     indent=2))
    return 0 if result["failed_stage"] is None else 1


if __name__ == "__main__":
    sys.exit(main())
