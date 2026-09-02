#!/usr/bin/env python3
"""c6 Track B: additive-sibling v3-input fork of scripts/recreate_v2/rc7_v2_rerun.py.

Pinned pre-code by docs/v3_spine_method_equivalence_rc7_spec.md
(sha256 in data/v3_spine/method_equivalence_rc7_spec_hash.txt).

Consumes the v3 operator-section per-track WAVs as "bare" (skips
MIDI-split-and-fluidsynth-render because v3 already has per-track WAVs)
and runs the c53 EQ+RMS-match chain against operator-section baseline
6-stem originals.

READ-ONLY imports:
  - scripts.recreate_v2.rc7_mix_balance:
      _fit_eq_curve_from_original, _sha256_file, _read_wav_float, _rms_db
  - scripts.palette_render.render_stem:
      _apply_eq_curve_iirpeak, _apply_loudness_target,
      _canonicalize_wav_deterministic

Milestone: M-V3-SPINE-1/rc7-method-equivalence-completed
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"rc7_v2_rerun_v3_paths requires /usr/bin/python3 (got {sys.executable})")

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import numpy as np  # noqa: E402
import scipy.io.wavfile as scipy_wav  # noqa: E402

from scripts.recreate_v2.rc7_mix_balance import (  # noqa: E402
    _fit_eq_curve_from_original,
    _sha256_file,
    _read_wav_float,
    _rms_db,
)
from scripts.palette_render.render_stem import (  # noqa: E402
    _apply_eq_curve_iirpeak,
    _apply_loudness_target,
    _canonicalize_wav_deterministic,
)

SEC = _REPO / "data" / "v3_spine" / "31a164f845f8e27e" / "operator_section"
RENDER = SEC / "render"
BASELINE_STEMS = SEC / "rc9_6stem"
OUT_ROOT = _REPO / "data" / "v3_spine" / "rc7_v2_v3_paths"

STEM_MAP = [
    ("drums",  RENDER / "per_track" / "drums.wav",  BASELINE_STEMS / "drums.wav"),
    ("bass",   RENDER / "per_track" / "bass.wav",   BASELINE_STEMS / "bass.wav"),
    ("guitar", RENDER / "per_track" / "guitar.wav", BASELINE_STEMS / "guitar.wav"),
    ("piano",  RENDER / "per_track" / "piano.wav",  BASELINE_STEMS / "piano.wav"),
    ("other",  RENDER / "per_track" / "other.wav",  BASELINE_STEMS / "other.wav"),
    ("vocals", RENDER / "vocals_htdemucs.wav",      BASELINE_STEMS / "vocals.wav"),
]


def _apply_chain(bare_wav: Path, eq_curve: dict, target_rms_db: float,
                 max_gain_db: float, out_wav: Path) -> float:
    """Apply 12-band iirpeak EQ + RMS loudness match to bare_wav; write out_wav.
    Returns measured RMS after."""
    _, y = scipy_wav.read(str(bare_wav))
    if y.dtype == np.int16:
        y = y.astype(np.float32) / 32768.0
    elif y.dtype == np.int32:
        y = y.astype(np.float32) / 2147483648.0
    else:
        y = y.astype(np.float32)
    centers = eq_curve["band_center_freqs_hz"]
    gains = eq_curve["band_gains_db"]
    if y.ndim == 1:
        proc = _apply_eq_curve_iirpeak(y, centers, gains)
        y_eq = proc.astype(np.float32)
    else:
        ch_l = _apply_eq_curve_iirpeak(y[:, 0], centers, gains)
        ch_r = _apply_eq_curve_iirpeak(y[:, 1], centers, gains)
        y_eq = np.stack([ch_l, ch_r], axis=1).astype(np.float32)
    y_out, measured_after = _apply_loudness_target(y_eq, target_rms_db, max_gain_db=max_gain_db)
    _canonicalize_wav_deterministic(y_out, out_wav)
    return float(measured_after)


def process(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    per_stem: dict = {}
    matched_wavs: list[Path] = []

    for name, rendered, baseline in STEM_MAP:
        if not rendered.is_file() or not baseline.is_file():
            per_stem[name] = {"error": f"missing rendered={rendered.is_file()} baseline={baseline.is_file()}"}
            continue
        _, y_orig = _read_wav_float(baseline)
        target_rms = _rms_db(y_orig)
        eq_curve = _fit_eq_curve_from_original(baseline, rendered)

        matched = out_dir / f"matched_{name}.wav"
        measured = _apply_chain(
            rendered, eq_curve, float(target_rms),
            max_gain_db=48.0, out_wav=matched,
        )
        per_stem[name] = {
            "rendered_wav": str(rendered.relative_to(_REPO)),
            "baseline_wav": str(baseline.relative_to(_REPO)),
            "target_rms_db": float(target_rms),
            "measured_rms_db_post_match": float(measured),
            "loudness_error_rms_db": float(abs(measured - target_rms)),
            "matched_sha256": _sha256_file(matched),
            "eq_bands_gains_db": eq_curve["band_gains_db"],
        }
        matched_wavs.append(matched)

    # Sum into full-mix reconstruction.
    mix_out = out_dir / "rc7_v2_v3_paths_full_reconstruction.wav"
    if matched_wavs:
        sr, y0 = _read_wav_float(matched_wavs[0])
        mix = np.zeros_like(y0)
        for w in matched_wavs:
            _, y = _read_wav_float(w)
            L = min(len(mix), len(y))
            mix[:L] += y[:L]
        peak = float(np.max(np.abs(mix)))
        if peak > 0.999:
            mix = mix * (0.999 / peak)
        scipy_wav.write(str(mix_out), sr, mix.astype(np.float32))

    return {
        "per_stem": per_stem,
        "full_mix_sha256": _sha256_file(mix_out) if mix_out.exists() else None,
        "full_mix_wav": (str(mix_out.relative_to(_REPO)) if mix_out.exists() and mix_out.is_relative_to(_REPO) else str(mix_out) if mix_out.exists() else None),
        "n_stems_processed": len(matched_wavs),
    }


def main(out_dir: Path | None = None) -> dict:
    if out_dir is None:
        out_dir = OUT_ROOT
    r1 = process(Path(tempfile.mkdtemp(prefix="rc7v3_r1_")))
    r2 = process(Path(tempfile.mkdtemp(prefix="rc7v3_r2_")))
    final = process(out_dir)

    det = {
        "run1_full_mix_sha256": r1["full_mix_sha256"],
        "run2_full_mix_sha256": r2["full_mix_sha256"],
        "final_full_mix_sha256": final["full_mix_sha256"],
        "byte_deterministic_x2": (
            r1["full_mix_sha256"] == r2["full_mix_sha256"] == final["full_mix_sha256"]
        ),
        "per_stem_run1_shas": {k: v.get("matched_sha256") for k, v in r1["per_stem"].items()},
        "per_stem_run2_shas": {k: v.get("matched_sha256") for k, v in r2["per_stem"].items()},
        "per_stem_final_shas": {k: v.get("matched_sha256") for k, v in final["per_stem"].items()},
    }
    (out_dir / "byte_determinism.json").write_text(
        json.dumps(det, sort_keys=True, indent=2) + "\n")
    return {"final": final, "byte_determinism": det}


if __name__ == "__main__":
    r = main()
    print(json.dumps({
        "byte_det_x2": r["byte_determinism"]["byte_deterministic_x2"],
        "full_mix_sha": r["final"]["full_mix_sha256"][:16] if r["final"]["full_mix_sha256"] else None,
    }))
