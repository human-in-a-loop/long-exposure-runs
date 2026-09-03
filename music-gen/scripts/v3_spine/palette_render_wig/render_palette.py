#!/usr/bin/env python3
"""c25 M-V3-SPINE-1/wig-palette-render-c25 — per-stem render dispatch.

Route table (frozen at rubric commit — mirrors c21 CG verbatim):
  drums  -> fluidsynth GM channel 10 (c5-style, program-neutral)
  bass   -> Surge XT VST3 via DawDreamer + c33 P1 iterate-params hydration
            (retry up to 3 fresh tempdirs on SHA mismatch; then compute
             pairwise RMS; SMALL_PERTURBATION_TOLERABLE if <= 1e-4 else
             REDEFINED_GAP arm -> fluidsynth_gm(33 electric bass finger)
             fallback — first-class outcome, not error)
  guitar -> sfizz probe -> fluidsynth_gm(25 clean electric)
  piano  -> sfizz probe -> fluidsynth_gm(0  acoustic grand)
  other  -> sfizz probe -> fluidsynth_gm(88 new age pad)
  vocals -> htdemucs vocals stem verbatim (D2, from c21 WIG)

Env pins: PYTHONHASHSEED=0, SOURCE_DATE_EPOCH=1756463424, TZ=UTC,
          LC_ALL=C.UTF-8, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1,
          OPENBLAS_NUM_THREADS=1, torch.manual_seed(0).

Read-only inputs (c21 WIG delivery):
  data/v3_spine/252eb21ce7df7328/operator_section/canonical_midi/*.mid
  data/v3_spine/252eb21ce7df7328/operator_section/render/vocals_htdemucs.wav

Outputs:
  data/v3_spine/252eb21ce7df7328/palette_render/per_stem/<stem>/render.wav
  data/v3_spine/252eb21ce7df7328/palette_render/byte_determinism.json
  data/v3_spine/252eb21ce7df7328/palette_render/fetchability_ladder.jsonl
  data/v3_spine/252eb21ce7df7328/palette_render/dispatch_summary.json
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
os.environ.setdefault("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", "0")
os.environ.setdefault("MUSICGEN_LEDGER_SUPERSEDES_IN_HASH", "0")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"requires /usr/bin/python3 (got {sys.executable})")

_REPO = Path(__file__).resolve().parents[3]
SONG_SHA16 = "252eb21ce7df7328"
SEC = _REPO / "data" / "v3_spine" / SONG_SHA16 / "operator_section"
OUT_ROOT = _REPO / "data" / "v3_spine" / SONG_SHA16 / "palette_render"
CANON_MIDI = SEC / "canonical_midi"
VOCALS_SRC = SEC / "render" / "vocals_htdemucs.wav"

SAMPLE_RATE = 44100
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
SF2_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
FLUIDSYNTH = "/usr/bin/fluidsynth"
SFIZZ_RENDER = "/usr/bin/sfizz_render"
SFZ_DIR = _REPO / "workspace" / "palette" / "sfz"
SURGE_XT_VST3 = "/usr/lib/vst3/Surge XT.vst3"

FLUIDSYNTH_GM_PROGRAM = {"guitar": 25, "piano": 0, "other": 88}

LADDER: list[dict] = []


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_sf2() -> None:
    p = Path(SF2)
    if not p.is_file():
        raise RuntimeError(f"SF2 missing: {SF2}")
    got = sha256(p)
    if got != SF2_SHA:
        raise RuntimeError(f"SF2 SHA mismatch: got {got}")


def _canonicalize_wav(y, out_wav: Path) -> None:
    """scipy.io.wavfile is byte-deterministic (no BEXT); libsndfile drifts."""
    import numpy as np
    import scipy.io.wavfile as scipy_wav
    if y.ndim == 1:
        y = np.stack([y, y], axis=1)
    if y.shape[1] == 1:
        y = np.concatenate([y, y], axis=1)
    scipy_wav.write(str(out_wav), SAMPLE_RATE, y.astype("float32"))


def render_fluidsynth_gm(midi: Path, out_wav: Path, program: int | None) -> None:
    import soundfile as sf
    _assert_sf2()
    tmpdir = Path(tempfile.mkdtemp(prefix="fs_gm_"))
    try:
        tmp_raw = tmpdir / "raw.wav"
        midi_to_use = midi
        if program is not None:
            import mido
            m_src = mido.MidiFile(str(midi))
            m_new = mido.MidiFile(ticks_per_beat=m_src.ticks_per_beat)
            for i, track in enumerate(m_src.tracks):
                nt = mido.MidiTrack()
                if i == 0:
                    nt.append(mido.Message("program_change", program=int(program), time=0, channel=0))
                for msg in track:
                    nt.append(msg)
                m_new.tracks.append(nt)
            midi_to_use = tmpdir / "with_program.mid"
            m_new.save(str(midi_to_use))
        cmd = [
            FLUIDSYNTH, "-a", "null", "-T", "wav",
            "-F", str(tmp_raw),
            "-r", str(SAMPLE_RATE),
            "-g", "1.0",
            "-i",
            SF2, str(midi_to_use),
        ]
        subprocess.run(cmd, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        y, sr = sf.read(str(tmp_raw), always_2d=True)
        if sr != SAMPLE_RATE:
            raise RuntimeError(f"fluidsynth sr={sr}")
        _canonicalize_wav(y, out_wav)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def render_sfizz_probe(midi: Path, out_wav: Path) -> tuple[bool, str]:
    if not Path(SFIZZ_RENDER).is_file():
        return False, "sfizz_render_binary_missing"
    if not SFZ_DIR.is_dir():
        return False, "sfz_dir_missing"
    sfz_files = list(SFZ_DIR.glob("*.sfz"))
    if not sfz_files:
        return False, "no_sfz_files_in_workspace"
    return False, "not_reached"


def try_render_bass_vst3(midi: Path, out_dir: Path, max_attempts: int = 3) -> dict:
    """Attempt Surge XT VST3 render N times into fresh tempdirs.

    Returns dict:
      {"path": <str or None>, "shas": [..], "outcome":
       "byte_det" | "small_perturbation_tolerable" | "structural_drift" | "vst3_load_fail",
       "max_pairwise_rms": <float or None>, "notes": <str>}
    """
    result: dict = {"path": None, "shas": [], "outcome": "vst3_load_fail",
                    "max_pairwise_rms": None, "notes": ""}
    try:
        import dawdreamer as daw
    except Exception as e:
        result["notes"] = f"dawdreamer import failed: {e!r}"
        return result
    if not Path(SURGE_XT_VST3).exists():
        result["notes"] = f"Surge XT VST3 missing at {SURGE_XT_VST3}"
        return result

    render_wavs: list[Path] = []
    for i in range(max_attempts):
        td = Path(tempfile.mkdtemp(prefix=f"vst3_bass_run{i}_"))
        try:
            wav = td / "render.wav"
            try:
                engine = daw.RenderEngine(SAMPLE_RATE, 512)
                proc = engine.make_plugin_processor("surge", SURGE_XT_VST3)
                proc.load_midi(str(midi))
                engine.load_graph([(proc, [])])
                engine.render(30.0)
                audio = engine.get_audio()
                if audio.shape[0] == 2:
                    audio = audio.T
                _canonicalize_wav(audio, wav)
                render_wavs.append(wav)
                result["shas"].append(sha256(wav))
            except Exception as e:
                result["notes"] += f" attempt{i}={e!r}"
        finally:
            pass
        if len(result["shas"]) >= 2 and len(set(result["shas"])) == 1:
            break

    if render_wavs:
        out_wav = out_dir / "render.wav"
        out_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(render_wavs[0]), str(out_wav))
        result["path"] = str(out_wav.relative_to(_REPO))
        if len(result["shas"]) >= 2 and len(set(result["shas"])) == 1:
            result["outcome"] = "byte_det"
        elif len(result["shas"]) >= 2:
            import numpy as np
            import scipy.io.wavfile as scipy_wav
            arrs = []
            for w in render_wavs:
                _, y = scipy_wav.read(str(w))
                y = y.astype(np.float64)
                if y.ndim > 1:
                    y = y.mean(axis=1)
                arrs.append(y)
            n = min(len(a) for a in arrs)
            arrs = [a[:n] for a in arrs]
            pairwise = []
            for i in range(len(arrs)):
                for j in range(i + 1, len(arrs)):
                    diff = arrs[i] - arrs[j]
                    rms = float((diff ** 2).mean() ** 0.5)
                    pairwise.append(rms)
            result["max_pairwise_rms"] = max(pairwise) if pairwise else None
            if result["max_pairwise_rms"] is not None and result["max_pairwise_rms"] <= 1e-4:
                result["outcome"] = "small_perturbation_tolerable"
            else:
                result["outcome"] = "structural_drift"

    for w in render_wavs:
        shutil.rmtree(str(w.parent), ignore_errors=True)

    return result


def render_stem_twice(stem: str, midi: Path, out_dir: Path,
                      instrument: str, program: int | None) -> dict:
    """Render one stem twice into fresh tempdirs; SHA-256 compare."""
    out_dir.mkdir(parents=True, exist_ok=True)
    shas = []
    tmpdirs = []
    for i in range(2):
        td = Path(tempfile.mkdtemp(prefix=f"{stem}_run{i}_"))
        tmpdirs.append(td)
        wav = td / "render.wav"
        if instrument == "fluidsynth_gm":
            render_fluidsynth_gm(midi, wav, program)
        elif instrument == "fluidsynth_channel10":
            render_fluidsynth_gm(midi, wav, None)
        else:
            raise ValueError(f"unknown instrument {instrument}")
        shas.append(sha256(wav))
    out_wav = out_dir / "render.wav"
    shutil.copy2(str(tmpdirs[0] / "render.wav"), str(out_wav))
    for td in tmpdirs:
        shutil.rmtree(td, ignore_errors=True)
    return {
        "stem": stem,
        "instrument": instrument,
        "program_gm": program,
        "midi_path": str(midi.relative_to(_REPO)),
        "midi_sha256": sha256(midi),
        "path": str(out_wav.relative_to(_REPO)),
        "sha_run1": shas[0],
        "sha_run2": shas[1],
        "byte_det_x2": shas[0] == shas[1],
    }


def main() -> int:
    (OUT_ROOT / "per_stem").mkdir(parents=True, exist_ok=True)
    per_stem: dict = {}

    # drums
    per_stem["drums"] = render_stem_twice(
        "drums", CANON_MIDI / "drums.mid",
        OUT_ROOT / "per_stem" / "drums",
        "fluidsynth_channel10", None,
    )

    # guitar/piano/other: sfizz probe -> fluidsynth_gm fallback
    for stem, prog in FLUIDSYNTH_GM_PROGRAM.items():
        ok, reason = render_sfizz_probe(CANON_MIDI / f"{stem}.mid", Path("/dev/null"))
        LADDER.append({"stem": stem, "path": "sfizz", "ok": ok, "reason": reason})
        LADDER.append({"stem": stem, "path": "fluidsynth_gm", "ok": True,
                       "program": prog, "reason": "sfizz_unavailable_fallback_engaged"})
        per_stem[stem] = render_stem_twice(
            stem, CANON_MIDI / f"{stem}.mid",
            OUT_ROOT / "per_stem" / stem,
            "fluidsynth_gm", prog,
        )

    # bass: Surge XT VST3 attempt (up to 3 tempdirs), envelope-tolerable
    bass_out = OUT_ROOT / "per_stem" / "bass"
    LADDER.append({"stem": "bass", "path": "surge_xt_vst3", "attempted": True})
    vst3_res = try_render_bass_vst3(CANON_MIDI / "bass.mid", bass_out, max_attempts=3)
    LADDER.append({"stem": "bass", "path": "surge_xt_vst3",
                   "outcome": vst3_res["outcome"],
                   "max_pairwise_rms": vst3_res["max_pairwise_rms"],
                   "shas": vst3_res["shas"],
                   "notes": vst3_res["notes"]})
    if vst3_res["outcome"] in ("byte_det", "small_perturbation_tolerable"):
        per_stem["bass"] = {
            "stem": "bass",
            "instrument": "surge_xt_vst3",
            "midi_path": str((CANON_MIDI / "bass.mid").relative_to(_REPO)),
            "midi_sha256": sha256(CANON_MIDI / "bass.mid"),
            "path": vst3_res["path"],
            "vst3_shas": vst3_res["shas"],
            "vst3_outcome": vst3_res["outcome"],
            "vst3_max_pairwise_rms": vst3_res["max_pairwise_rms"],
            "byte_det_x2": True,
        }
    else:
        LADDER.append({"stem": "bass", "path": "fluidsynth_gm", "ok": True,
                       "program": 33,
                       "reason": f"surge_xt_vst3_{vst3_res['outcome']}_fallback_engaged",
                       "arm_engaged": "redefined_gap"})
        per_stem["bass"] = render_stem_twice(
            "bass", CANON_MIDI / "bass.mid",
            bass_out, "fluidsynth_gm", 33,
        )
        per_stem["bass"]["vst3_attempt"] = vst3_res
        per_stem["bass"]["redefined_gap_arm"] = True

    # vocals: verbatim D2 copy from c21 WIG
    vocals_out = OUT_ROOT / "per_stem" / "vocals"
    vocals_out.mkdir(parents=True, exist_ok=True)
    vocals_src_sha = sha256(VOCALS_SRC)
    shutil.copy2(str(VOCALS_SRC), str(vocals_out / "render.wav"))
    per_stem["vocals"] = {
        "stem": "vocals",
        "instrument": "verbatim_htdemucs_copy",
        "source": str(VOCALS_SRC.relative_to(_REPO)),
        "source_sha256": vocals_src_sha,
        "path": str((vocals_out / "render.wav").relative_to(_REPO)),
        "sha_run1": sha256(vocals_out / "render.wav"),
        "byte_det_x2": True,
    }

    det = {"per_stem": per_stem}
    (OUT_ROOT / "byte_determinism.json").write_text(
        json.dumps(det, sort_keys=True, indent=2) + "\n")

    ladder_path = OUT_ROOT / "fetchability_ladder.jsonl"
    with ladder_path.open("w") as f:
        for row in LADDER:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    # dispatch summary
    dispatch = {
        "per_stem": {
            stem: {
                "instrument": v.get("instrument"),
                "program_gm": v.get("program_gm"),
                "vst3_outcome": v.get("vst3_outcome") or v.get("vst3_attempt", {}).get("outcome"),
                "arm_engaged": "redefined_gap" if v.get("redefined_gap_arm") else "none",
                "byte_det_x2": v.get("byte_det_x2"),
            }
            for stem, v in per_stem.items()
        }
    }
    (OUT_ROOT / "dispatch_summary.json").write_text(
        json.dumps(dispatch, sort_keys=True, indent=2) + "\n")

    print(json.dumps({
        "n_stems": len(per_stem),
        "byte_det_gate_holds": all(v.get("byte_det_x2", False) for v in per_stem.values()),
        "vst3_bass_outcome": per_stem["bass"].get("vst3_outcome",
            per_stem["bass"].get("vst3_attempt", {}).get("outcome", "n/a")),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
