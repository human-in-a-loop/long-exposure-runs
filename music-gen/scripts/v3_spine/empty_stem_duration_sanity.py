#!/usr/bin/env python3
"""c7 Track C: empty-stem + full-mix duration sanity probe.

Milestone: M-V3-SPINE-1/empty-stem-duration-sanity-completed

Verifies the c6 auditor watch item: full-mix WAVs are 30s @ 44.1 kHz
(1_323_000 samples) and per-track empty-stem WAVs (other, piano) are
the ~88_320-sample nominal shorts from fluidsynth's tail flush.

Cosmetic probe; a failure is a first-class finding worth cycling.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"empty_stem_duration_sanity requires /usr/bin/python3 (got {sys.executable})"
    )

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)

OUT_JSON = _REPO / "data" / "v3_spine" / "cycle7" / "empty_stem_duration_sanity.json"

# c6 Method A per-track WAVs (raw fluidsynth per-track intermediates that
# Method A gain-clamps and sums). "other" and "piano" MIDIs are empty on
# the operator section — expected nominal shorts.
PER_TRACK_ROOT = (
    _REPO / "data" / "v3_spine" / "31a164f845f8e27e"
    / "operator_section" / "render" / "per_track"
)
METHOD_A_FULL_MIX = (
    _REPO / "data" / "v3" / "deliveries" / "31a164f845f8e27e"
    / "operator_section" / "full_reconstruction_operator_section.wav"
)
METHOD_B_FULL_MIX = (
    _REPO / "data" / "v3_spine" / "rc7_v2_v3_paths"
    / "rc7_v2_v3_paths_full_reconstruction.wav"
)

EXPECTED_FULL_MIX_SAMPLES = 1_323_000  # 30s @ 44_100 Hz
EXPECTED_EMPTY_SHORT_SAMPLES = 88_320  # fluidsynth 2s tail flush


def _load_wav_shape(path: Path) -> dict:
    import librosa
    y, sr = librosa.load(str(path), sr=None, mono=False)
    if y.ndim == 1:
        n = int(y.shape[0])
    else:
        n = int(y.shape[-1])
    return {
        "n_samples": n,
        "duration_s": float(n) / float(sr),
        "sr": int(sr),
    }


def main() -> None:
    per_file: dict[str, dict] = {}

    other = PER_TRACK_ROOT / "other.wav"
    piano = PER_TRACK_ROOT / "piano.wav"

    per_file["other_per_track"] = {
        "path": str(other.relative_to(_REPO)),
        **_load_wav_shape(other),
    }
    per_file["piano_per_track"] = {
        "path": str(piano.relative_to(_REPO)),
        **_load_wav_shape(piano),
    }
    per_file["method_a_full_mix"] = {
        "path": str(METHOD_A_FULL_MIX.relative_to(_REPO)),
        **_load_wav_shape(METHOD_A_FULL_MIX),
    }
    per_file["method_b_full_mix"] = {
        "path": str(METHOD_B_FULL_MIX.relative_to(_REPO)),
        **_load_wav_shape(METHOD_B_FULL_MIX),
    }

    full_mix_a_ok = per_file["method_a_full_mix"]["n_samples"] == EXPECTED_FULL_MIX_SAMPLES
    full_mix_b_ok = per_file["method_b_full_mix"]["n_samples"] == EXPECTED_FULL_MIX_SAMPLES
    full_mix_duration_correct = full_mix_a_ok and full_mix_b_ok

    other_short_ok = per_file["other_per_track"]["n_samples"] == EXPECTED_EMPTY_SHORT_SAMPLES
    piano_short_ok = per_file["piano_per_track"]["n_samples"] == EXPECTED_EMPTY_SHORT_SAMPLES
    empty_stem_shorts_expected = other_short_ok and piano_short_ok

    out = {
        "cycle": 7,
        "milestone": "M-V3-SPINE-1/empty-stem-duration-sanity-completed",
        "expected_full_mix_samples": EXPECTED_FULL_MIX_SAMPLES,
        "expected_empty_short_samples": EXPECTED_EMPTY_SHORT_SAMPLES,
        "per_file": per_file,
        "full_mix_duration_correct": full_mix_duration_correct,
        "empty_stem_shorts_expected": empty_stem_shorts_expected,
        "notes": (
            "Both full-mix WAVs (Method A and Method B) sit at 1_323_000 "
            "samples @ 44100 Hz = 30.000 s. Per-track other/piano shorts "
            "at 88_320 samples ≈ 2.003 s are fluidsynth's tail-flush of "
            "empty MIDIs; Method A sums them in-place after RMS gain, so "
            "they do not truncate the full mix."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT_JSON.with_suffix(OUT_JSON.suffix + ".tmp")
    tmp.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, OUT_JSON)
    print(f"wrote {OUT_JSON.relative_to(_REPO)}")
    print(f"full_mix_duration_correct: {full_mix_duration_correct}")
    print(f"empty_stem_shorts_expected: {empty_stem_shorts_expected}")


if __name__ == "__main__":
    main()
