#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 6
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-bass-family2-stem-sampled
# ---
"""c6 family-2 stem-sampled builder for CG bass.

Reads reference bass stem + bass MIDI, measures a stable f0 in the bass
range via pyin, emits a family-2 profile (schema mirrors sf2 bass.json)
with:
    render_family = "stem_sampled_v1"
    identity = {stem_source_*, stem_slice_*, stem_f0_hz, pitch_mapping,
                envelope_mode, gain, post{lufs_target_db}}
    profile_id = UUID5 content-hash

Emits ONE final WAV path (no per-note intermediate WAVs — SWEEP-STORAGE
HYGIENE). Total added audio should stay under 5 MB for CG bass.

NEW sibling to scripts/sound_match/family2_stem_sampled_spike.py which
remains READ-ONLY as a historical anchor.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

_PINS = {
    "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
    "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(f"builder requires /usr/bin/python3 (got {sys.executable})")

import numpy as np  # noqa: E402
import librosa  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.sound_match.replay_family2 import replay_family2  # noqa: E402

REF_STEM = REPO / "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav"
BASS_MIDI = REPO / "data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1/inputs/bass.mid"
BUILDER_RUBRIC_HASH = REPO / "data/v4/profiles/31a164f845f8e27e/family2_builder_c6_rubric_hash.txt"

NAMESPACE = uuid.UUID("00000000-0000-5000-8000-70726f66696c")  # profile


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _estimate_stem_f0(stem: np.ndarray, sr: int) -> tuple[float, str]:
    """Estimate reference stem fundamental in the bass range."""
    try:
        f0, voiced, _ = librosa.pyin(
            stem,
            fmin=float(librosa.note_to_hz("E1")),  # 41.20 Hz
            fmax=float(librosa.note_to_hz("E4")),  # 329.63 Hz
        )
        f0_voiced = f0[np.isfinite(f0) & (voiced > 0.5)]
        if f0_voiced.size >= 5:
            return float(np.median(f0_voiced)), "pyin_bass_range"
    except Exception:
        pass
    try:
        f0 = librosa.yin(stem, fmin=50.0, fmax=400.0)
        f0 = f0[np.isfinite(f0)]
        if f0.size:
            return float(np.median(f0)), "yin_fallback"
    except Exception:
        pass
    return 82.41, "e2_default"


def build_family2_profile(
    *,
    stem_wav_path: Path,
    midi_path: Path,
    out_profile_path: Path,
    out_wav_path: Path,
    strategy: str = "single_slice_pitch_shift",
    envelope: str = "adsr_lite",
    lufs_target_db: float = -18.0,
    slice_start_s: float = 0.0,
    slice_len_s: float = 3.0,
    gain: float = 1.0,
) -> dict:
    """Build a stem_sampled_v1 profile for CG bass and render its output WAV."""
    stem_sha = _sha256(stem_wav_path)
    midi_sha = _sha256(midi_path)
    stem, sr = librosa.load(str(stem_wav_path), sr=None, mono=True)
    stem_f0_hz, f0_method = _estimate_stem_f0(stem, sr)

    identity = {
        "stem_source_path": str(stem_wav_path),
        "stem_source_sha256": stem_sha,
        "stem_slice_start_s": float(slice_start_s),
        "stem_slice_len_s": float(slice_len_s),
        "stem_f0_hz": float(stem_f0_hz),
        "stem_f0_method": f0_method,
        "pitch_mapping": strategy,
        "envelope_mode": envelope,
        "gain": float(gain),
        "post": {"lufs_target_db": float(lufs_target_db)},
    }

    profile_body_for_id = {
        "render_family": "stem_sampled_v1",
        "identity": identity,
        "deps_sha256": {
            "reference_stem": stem_sha,
            "bass_midi_excerpt": midi_sha,
        },
        "schema_v": "v4.0",
        "song_sha16": "31a164f845f8e27e",
        "instrument": "bass",
    }
    canonical_for_id = json.dumps(profile_body_for_id, sort_keys=True,
                                  separators=(",", ":")).encode("utf-8")
    profile_id = str(uuid.uuid5(NAMESPACE, canonical_for_id.hex()))

    # Render to obtain canonical replay SHA (deterministic given identity + midi)
    render_sha = replay_family2(profile_body_for_id, midi_path, out_wav_path)

    profile = dict(profile_body_for_id)
    profile["profile_id"] = profile_id
    profile["render_sha256_canonical_replay"] = render_sha
    profile["rubric_hash"] = BUILDER_RUBRIC_HASH.read_text().strip()
    profile["cycle"] = 6

    out_profile_path.parent.mkdir(parents=True, exist_ok=True)
    out_profile_path.write_text(json.dumps(profile, sort_keys=True, indent=2))
    return profile


def main() -> int:
    out_dir = REPO / "data/v4/profiles/31a164f845f8e27e/bass_family2_v1"
    out_dir.mkdir(parents=True, exist_ok=True)
    profile = build_family2_profile(
        stem_wav_path=REF_STEM,
        midi_path=BASS_MIDI,
        out_profile_path=REPO / "data/v4/profiles/31a164f845f8e27e/bass_family2_v1.json",
        out_wav_path=out_dir / "render.wav",
    )
    print(json.dumps({
        "profile_id": profile["profile_id"],
        "render_sha256_canonical_replay": profile["render_sha256_canonical_replay"],
        "stem_f0_hz": profile["identity"]["stem_f0_hz"],
        "stem_f0_method": profile["identity"]["stem_f0_method"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
