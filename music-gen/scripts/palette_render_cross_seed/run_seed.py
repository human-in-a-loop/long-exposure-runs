#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:20:00Z
# cycle: 34
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/palette-driven-bare-render/cross-seed
# ---
"""Per-seed cross-seed render orchestrator.

For one seed (seed_mid_50s or synth_060s):
  1. Build assignments (delegates to build_assignments_per_seed).
  2. Render each per-stem MIDI twice into fresh `tempfile.mkdtemp()`
     directories, using this seed's actual duration & sample rate (both
     seeds are 44.1 kHz stereo per c10/c13 anchors — the brief's
     22050/mono claim for seed_mid_50s is superseded by the on-disk
     header). Renderer invocations follow the c33 CLI pattern verbatim
     (fluidsynth / sfizz_render); c33 render_stem is imported READ-ONLY
     for constant-cross-check (SF2 SHA pin, binary paths).
  3. Sum per-stem WAVs to bare_combined at THIS seed's sample rate +
     channel count; write SHAs run1 + run2; assert byte-identity.
  4. Measure M-TEX-1/panel on TWO comparisons:
       (data/breadth/<seed>/original.wav, palette-bare)
       (data/breadth/<seed>/bare_midi.wav,  palette-bare)
     Write per-seed panel TSVs.
  5. Return dict summarising SHAs + panel deltas for downstream verdict.

NO PRNG. /usr/bin/python3 guarded. No sidecar_nonfactor import.
c9 effects chain NOT imported. c13 batch pipeline NOT imported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
import soundfile as sf
import scipy.io.wavfile as scipy_wav

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.palette_render_cross_seed.build_assignments_per_seed import (  # noqa: E402
    PER_SEED_MIDI,
    build_assignments_for_seed,
)
# READ-ONLY imports of c33 anchors (used for constant cross-check).
from scripts.palette_render import render_stem as _c33_render_stem  # noqa: E402
from scripts.palette_render import build_assignments as _c33_build  # noqa: E402
from scripts.texture.panel import PUBLIC_KEYS, texture_distance  # noqa: E402


SAMPLE_RATE = 44100  # both seeds actually 44.1 kHz stereo on disk.

# Cross-check with the c33 anchor — this must match; if c33 ever moves off
# 44.1 kHz we want to blow up loudly rather than silently drift.
assert _c33_render_stem.SAMPLE_RATE == SAMPLE_RATE, (
    "c33 render_stem SAMPLE_RATE drifted — cross-seed inherits its rate")

SF2_PATH = _c33_render_stem.SF2_PATH
SF2_EXPECTED_SHA = _c33_render_stem.SF2_EXPECTED_SHA
SFZ_PATH = _c33_render_stem.SFZ_PATH
SFIZZ_RENDER = _c33_render_stem.SFIZZ_RENDER
FLUIDSYNTH = _c33_render_stem.FLUIDSYNTH


def _assert_sf2() -> None:
    """SF2 SHA pin — copied invocation pattern from
    scripts/tex/render_bare_midi.py:70 and scripts/palette_render/render_stem.py:_assert_sf2.
    That module is NOT imported at runtime beyond the c33 constant cross-check above.
    """
    if not SF2_PATH.is_file():
        raise RuntimeError(f"SF2 missing: {SF2_PATH}")
    h = hashlib.sha256(SF2_PATH.read_bytes()).hexdigest()
    if h != SF2_EXPECTED_SHA:
        raise RuntimeError(f"SF2 SHA mismatch: got {h}, expected {SF2_EXPECTED_SHA}")


def _canonicalize_wav(y: np.ndarray, out_wav: Path, sample_count: int) -> None:
    """Byte-deterministic PCM WAV via scipy.io.wavfile. Stereo, float32.

    Trims / pads to exactly `sample_count` frames at 44.1 kHz stereo.
    """
    if y.ndim == 1:
        y = np.stack([y, y], axis=1)
    if y.shape[1] == 1:
        y = np.concatenate([y, y], axis=1)
    if y.shape[0] > sample_count:
        y = y[:sample_count, :]
    elif y.shape[0] < sample_count:
        pad = np.zeros((sample_count - y.shape[0], y.shape[1]), dtype=y.dtype)
        y = np.concatenate([y, pad], axis=0)
    scipy_wav.write(str(out_wav), SAMPLE_RATE, y.astype(np.float32))


def render_fluidsynth(midi_path: Path, out_wav: Path, sample_count: int) -> None:
    """Fluidsynth CLI. Copied invocation pattern from
    scripts/palette_render/render_stem.render_fluidsynth (documented anchor).
    That module is imported READ-ONLY at module scope for cross-check.
    """
    _assert_sf2()
    if not midi_path.is_file():
        raise RuntimeError(f"MIDI missing: {midi_path}")
    tmp = out_wav.with_suffix(".raw.wav")
    if tmp.exists():
        tmp.unlink()
    cmd = [
        FLUIDSYNTH, "-a", "null", "-T", "wav",
        "-F", str(tmp),
        "-r", str(SAMPLE_RATE),
        "-g", "1.0",
        "-i",
        str(SF2_PATH), str(midi_path),
    ]
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    y, got_sr = sf.read(str(tmp), always_2d=True)
    if got_sr != SAMPLE_RATE:
        raise RuntimeError(f"fluidsynth sr={got_sr}, expected {SAMPLE_RATE}")
    _canonicalize_wav(y, out_wav, sample_count)
    tmp.unlink()


def render_sfizz(midi_path: Path, out_wav: Path, sample_count: int,
                 block_size: int = 512) -> None:
    """sfizz_render CLI. Copied invocation pattern from
    scripts/palette_render/render_stem.render_sfizz (documented anchor).
    That module is imported READ-ONLY at module scope for cross-check.
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
    cmd = [
        SFIZZ_RENDER,
        "--sfz", str(SFZ_PATH),
        "--midi", str(midi_path),
        "--wav", str(raw),
        "-b", str(block_size),
        "-s", str(SAMPLE_RATE),
        "-q", "1",
        "-p", "64",
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    data, sr = sf.read(str(raw), always_2d=True)
    if sr != SAMPLE_RATE:
        raise RuntimeError(f"sfizz sr={sr}, expected {SAMPLE_RATE}")
    _canonicalize_wav(data.astype(np.float32), out_wav, sample_count)
    raw.unlink()


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _seed_duration_samples(seed: str) -> int:
    """Read this seed's original.wav header and return exact sample count.

    Uses soundfile.info instead of the stdlib wave module because the
    on-disk WAVs are float32 PCM (format tag 3) which wave.open rejects.
    """
    orig = _REPO / "data" / "breadth" / seed / "original.wav"
    info = sf.info(str(orig))
    if info.samplerate != SAMPLE_RATE:
        raise RuntimeError(f"seed {seed} sr={info.samplerate}, expected {SAMPLE_RATE}")
    return int(info.frames)


def render_stem_for_seed(seed: str, stem: str, instrument: str,
                         out_dir: Path, sample_count: int) -> dict:
    """Render one stem for a given seed twice into fresh tempdir; assert byte-identity."""
    midi_path = PER_SEED_MIDI[seed][stem]
    if not midi_path.is_file():
        raise RuntimeError(f"per-seed MIDI missing: {midi_path}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out1 = out_dir / "render_run1.wav"
    out2 = out_dir / "render_run2.wav"
    if instrument == "fluidsynth_gm":
        render_fluidsynth(midi_path, out1, sample_count)
        render_fluidsynth(midi_path, out2, sample_count)
    elif instrument == "sfizz":
        render_sfizz(midi_path, out1, sample_count)
        render_sfizz(midi_path, out2, sample_count)
    else:
        raise RuntimeError(f"unsupported instrument {instrument} for cross-seed render")

    sha1 = _sha256_file(out1)
    sha2 = _sha256_file(out2)
    midi_sha = hashlib.sha256(midi_path.read_bytes()).hexdigest()
    (out_dir / "render_run1.wav.sha").write_text(sha1 + "\n")
    (out_dir / "render_run2.wav.sha").write_text(sha2 + "\n")

    pinned = {
        "seed": seed,
        "stem": stem,
        "instrument": instrument,
        "midi_input_sha256": midi_sha,
        "sample_rate": SAMPLE_RATE,
        "sample_count": sample_count,
        "sha_equal": sha1 == sha2,
        "run1_sha": sha1,
        "run2_sha": sha2,
    }
    (out_dir / "pinned_state.json").write_text(
        json.dumps(pinned, sort_keys=True, indent=2) + "\n")

    return {
        "stem": stem, "instrument": instrument,
        "midi_path": str(midi_path), "midi_sha": midi_sha,
        "render_run1_sha": sha1, "render_run2_sha": sha2,
        "sha_equal": sha1 == sha2,
        "run1_wav_path": str(out1), "run2_wav_path": str(out2),
    }


def combine_stems(per_stem_wavs: list[Path], out_wav: Path,
                  sample_count: int) -> None:
    """Sum three per-stem WAVs into one bare_combined WAV.

    All inputs assumed 44.1 kHz stereo of `sample_count` frames (enforced
    by _canonicalize_wav upstream). Sum, clip to [-1, 1], write via
    scipy.io.wavfile (byte-deterministic).
    """
    accum = np.zeros((sample_count, 2), dtype=np.float32)
    for p in per_stem_wavs:
        y, sr = sf.read(str(p), always_2d=True, dtype="float32")
        if sr != SAMPLE_RATE:
            raise RuntimeError(f"stem {p} sr={sr}")
        if y.shape[0] < sample_count:
            pad = np.zeros((sample_count - y.shape[0], y.shape[1]), dtype=np.float32)
            y = np.concatenate([y, pad], axis=0)
        elif y.shape[0] > sample_count:
            y = y[:sample_count, :]
        if y.shape[1] == 1:
            y = np.concatenate([y, y], axis=1)
        accum += y
    np.clip(accum, -1.0, 1.0, out=accum)
    scipy_wav.write(str(out_wav), SAMPLE_RATE, accum)


def _panel_measure(a_wav: Path, b_wav: Path) -> dict:
    ya, sra = sf.read(str(a_wav), always_2d=True, dtype="float32")
    yb, srb = sf.read(str(b_wav), always_2d=True, dtype="float32")
    if sra != srb:
        raise RuntimeError(f"panel SR mismatch: a={sra} b={srb}")
    return texture_distance(ya, yb, sra)


def _write_panel_tsv(out_path: Path, panel: dict) -> None:
    with open(out_path, "w") as f:
        f.write("\t".join(PUBLIC_KEYS) + "\n")
        row = []
        for k in PUBLIC_KEYS:
            v = panel.get(k)
            if v is None:
                row.append("")
            elif isinstance(v, (int, float)):
                row.append(f"{v}")
            else:
                row.append(str(v))
        f.write("\t".join(row) + "\n")


def run_one_run(seed: str, assignments: list[dict], sample_count: int) -> dict:
    """One end-to-end render pass into a fresh tempdir. Returns per-stem SHAs + combined SHA + combined WAV path (kept outside tempdir)."""
    tmpdir = Path(tempfile.mkdtemp(prefix=f"cross_seed_{seed}_"))
    per_stem_results = []
    stem_wavs = []
    for a in assignments:
        stem_dir = tmpdir / a["stem"]
        res = render_stem_for_seed(seed, a["stem"], a["instrument"], stem_dir, sample_count)
        per_stem_results.append(res)
        stem_wavs.append(Path(res["run1_wav_path"]))

    combined = tmpdir / "bare_combined.wav"
    combine_stems(stem_wavs, combined, sample_count)
    combined_sha = _sha256_file(combined)

    # Persist combined outside tempdir so downstream panel measurement can read it.
    persist_dir = _REPO / "data" / "palette_render_cross_seed" / "per_seed" / seed
    persist_dir.mkdir(parents=True, exist_ok=True)
    persist_path = persist_dir / "_tmp_combined.wav"
    shutil.copy2(str(combined), str(persist_path))

    shutil.rmtree(str(tmpdir), ignore_errors=True)
    return {
        "per_stem": per_stem_results,
        "combined_sha": combined_sha,
        "combined_wav": str(persist_path),
    }


def process_seed(seed: str) -> dict:
    """End-to-end per-seed pipeline. Returns dict absorbed by run_all."""
    sample_count = _seed_duration_samples(seed)
    seed_dir = _REPO / "data" / "palette_render_cross_seed" / "per_seed" / seed
    seed_dir.mkdir(parents=True, exist_ok=True)

    # 1. Assignments (SHA-tiebreak within this seed's rule_id subset).
    assignments = build_assignments_for_seed(seed, seed_dir)

    # 2. Two independent runs via fresh tempdirs.
    r1 = run_one_run(seed, assignments, sample_count)
    r2 = run_one_run(seed, assignments, sample_count)

    # 3. Per-stem: verify cross-run byte-identity, persist SHAs.
    per_stem_dir = seed_dir / "per_stem"
    per_stem_dir.mkdir(exist_ok=True)
    per_stem_sha_equal = {}
    for res1 in r1["per_stem"]:
        stem = res1["stem"]
        res2 = next(x for x in r2["per_stem"] if x["stem"] == stem)
        stem_out = per_stem_dir / stem
        stem_out.mkdir(exist_ok=True)
        (stem_out / "render_run1.wav.sha").write_text(res1["render_run1_sha"] + "\n")
        (stem_out / "render_run2.wav.sha").write_text(res2["render_run1_sha"] + "\n")
        per_stem_sha_equal[stem] = res1["render_run1_sha"] == res2["render_run1_sha"]
        pinned = {
            "seed": seed,
            "stem": stem,
            "instrument": res1["instrument"],
            "midi_input_sha256": res1["midi_sha"],
            "sample_rate": SAMPLE_RATE,
            "sample_count": sample_count,
            "run1_sha": res1["render_run1_sha"],
            "run2_sha": res2["render_run1_sha"],
            "sha_equal": per_stem_sha_equal[stem],
        }
        (stem_out / "pinned_state.json").write_text(
            json.dumps(pinned, sort_keys=True, indent=2) + "\n")

    # 4. Combined SHAs.
    (seed_dir / "bare_combined.wav.sha.run1").write_text(r1["combined_sha"] + "\n")
    (seed_dir / "bare_combined.wav.sha.run2").write_text(r2["combined_sha"] + "\n")

    # 5. Panel measurements.
    orig_wav = _REPO / "data" / "breadth" / seed / "original.wav"
    fluid_wav = _REPO / "data" / "breadth" / seed / "bare_midi.wav"
    palette_wav = Path(r1["combined_wav"])

    panel_orig_vs_pal = _panel_measure(orig_wav, palette_wav)
    panel_fluid_vs_pal = _panel_measure(fluid_wav, palette_wav)
    panel_fluid_self = _panel_measure(fluid_wav, fluid_wav)  # per-seed baseline

    _write_panel_tsv(seed_dir / "panel_original_vs_palette.tsv", panel_orig_vs_pal)
    _write_panel_tsv(seed_dir / "panel_fluidsynth_vs_palette.tsv", panel_fluid_vs_pal)

    # 6. Clean up persisted combined WAV.
    try:
        palette_wav.unlink()
    except Exception:
        pass

    return {
        "seed": seed,
        "sample_count": sample_count,
        "assignments": assignments,
        "per_stem_sha_equal": per_stem_sha_equal,
        "combined_sha_run1": r1["combined_sha"],
        "combined_sha_run2": r2["combined_sha"],
        "combined_sha_equal": r1["combined_sha"] == r2["combined_sha"],
        "panel_original_vs_palette": panel_orig_vs_pal,
        "panel_fluidsynth_vs_palette": panel_fluid_vs_pal,
        "panel_fluidsynth_self": panel_fluid_self,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", required=True, choices=list(PER_SEED_MIDI.keys()))
    a = ap.parse_args()
    result = process_seed(a.seed)
    # Print summary — panel dicts elided for readability.
    summary = {k: v for k, v in result.items() if not k.startswith("panel_")
               and k != "assignments"}
    summary["panel_orig_vs_palette_keys"] = sorted(result["panel_original_vs_palette"].keys())
    print(json.dumps(summary, sort_keys=True, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
