#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 1
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES
# ---
"""Assemble the operator A/B pair for a sound-matching winner.

Inputs:
    original_stem_wav: the operator-section stem (untouched reference).
    winner_replay_wav: the winner's replayed rendering of the same
                       MIDI excerpt through fluidsynth/sfizz.

The B side is the winner's replay loudness-matched to the stem via a
plain RMS-match (rc7 shape). No EQ chain is applied here — the fine-fit
stage is where EQ lives.

Writes:
    <out_dir>/original_ab.wav
    <out_dir>/reconstruction_ab.wav
    <out_dir>/manifest.json

Manifest carries env_pins block (from build_env_pin_manifest) and the
winner profile SHA.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Mapping

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(
        f"deliver_ab requires /usr/bin/python3 (got {sys.executable})"
    )

import numpy as np
import soundfile as sf


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _rms(y: np.ndarray) -> float:
    return float(np.sqrt(np.mean(y.astype(np.float64) ** 2) + 1e-12))


def _rms_match(target_ref: Path, source: Path, out: Path) -> None:
    y, sr = sf.read(str(source), always_2d=False)
    r, sr_r = sf.read(str(target_ref), always_2d=False)
    if sr != sr_r:
        raise ValueError(f"sr mismatch source={sr} ref={sr_r}")
    ref_rms = _rms(r if r.ndim == 1 else r.mean(axis=1))
    src_rms = _rms(y if y.ndim == 1 else y.mean(axis=1))
    gain = ref_rms / max(src_rms, 1e-9)
    y = np.clip(y * gain, -1.0, 1.0).astype(np.float32)
    sf.write(str(out), y, sr, subtype="PCM_16")


def assemble(
    *,
    out_dir: Path,
    original_stem_wav: Path,
    winner_replay_wav: Path,
    profile: Mapping,
    env_pins: Mapping,
    milestone: str,
) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ab_orig = out_dir / "original_ab.wav"
    ab_recon = out_dir / "reconstruction_ab.wav"
    shutil.copy2(original_stem_wav, ab_orig)
    _rms_match(original_stem_wav, winner_replay_wav, ab_recon)

    manifest = {
        "milestone": milestone,
        "profile_id": profile.get("profile_id"),
        "profile": dict(profile),
        "env_pins": dict(env_pins),
        "artifacts": {
            "original_ab.wav": {
                "sha256": _sha256(ab_orig),
                "source": str(original_stem_wav),
            },
            "reconstruction_ab.wav": {
                "sha256": _sha256(ab_recon),
                "source": str(winner_replay_wav),
                "loudness_match": "rc7_rms_plain",
            },
        },
    }
    with open(out_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, sort_keys=True, indent=2)
    return manifest
