#!/usr/bin/env python3
"""c25 WIG palette-render RC7 mix + delivery emission.

Consumes per-stem palette WAVs at
`data/v3_spine/252eb21ce7df7328/palette_render/per_stem/<stem>/render.wav`
and applies the c6 Method B chain (READ-ONLY import) verbatim:

  12-band iirpeak EQ (Q=1.4, geomspace 20..20000 Hz) fitted vs
  baseline stems + RMS + LUFS-S loudness match per stem + sum matched
  stems into full_reconstruction_palette.wav.

Then emits the delivery tree under
`data/v3/deliveries/252eb21ce7df7328/palette_render_c25/`.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", "0")
os.environ.setdefault("MUSICGEN_LEDGER_SUPERSEDES_IN_HASH", "0")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"requires /usr/bin/python3 (got {sys.executable})")

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import numpy as np  # noqa: E402
import scipy.io.wavfile as scipy_wav  # noqa: E402

# READ-ONLY imports of c53/c6 chain + render_stem helpers
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

# c22 env_pin READ-ONLY import for manifest self-anchor
from scripts.v3_spine.v3_pipeline.env_pin import (  # noqa: E402
    build_env_pin_manifest,
)

SONG_SHA16 = "252eb21ce7df7328"
SEC = _REPO / "data" / "v3_spine" / SONG_SHA16 / "operator_section"
BASELINE_STEMS = SEC / "rc9_6stem"
PAL_ROOT = _REPO / "data" / "v3_spine" / SONG_SHA16 / "palette_render"
DELIV_ROOT = _REPO / "data" / "v3" / "deliveries" / SONG_SHA16 / "palette_render_c25"

STEMS = ["drums", "bass", "guitar", "piano", "other", "vocals"]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def apply_chain(bare_wav: Path, eq_curve: dict, target_rms_db: float,
                max_gain_db: float, out_wav: Path) -> float:
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
    y_out, measured_after = _apply_loudness_target(y_eq, target_rms_db,
                                                    max_gain_db=max_gain_db)
    _canonicalize_wav_deterministic(y_out, out_wav)
    return float(measured_after)


def main() -> int:
    PAL_ROOT.mkdir(parents=True, exist_ok=True)
    DELIV_ROOT.mkdir(parents=True, exist_ok=True)
    (DELIV_ROOT / "per_stem").mkdir(exist_ok=True)

    per_stem: dict = {}
    matched_wavs: list[Path] = []

    for stem in STEMS:
        rendered = PAL_ROOT / "per_stem" / stem / "render.wav"
        baseline = BASELINE_STEMS / f"{stem}.wav"
        if not rendered.is_file() or not baseline.is_file():
            per_stem[stem] = {
                "error": f"missing rendered={rendered.is_file()} "
                         f"baseline={baseline.is_file()}"
            }
            continue
        _, y_orig = _read_wav_float(baseline)
        target_rms = _rms_db(y_orig)
        eq_curve = _fit_eq_curve_from_original(baseline, rendered)
        matched = PAL_ROOT / f"matched_{stem}.wav"
        measured = apply_chain(
            rendered, eq_curve, float(target_rms),
            max_gain_db=48.0, out_wav=matched,
        )
        per_stem[stem] = {
            "rendered_wav": str(rendered.relative_to(_REPO)),
            "baseline_wav": str(baseline.relative_to(_REPO)),
            "target_rms_db": float(target_rms),
            "measured_rms_db_post_match": float(measured),
            "loudness_error_rms_db": float(abs(measured - target_rms)),
            "matched_sha256": _sha256_file(matched),
            "eq_bands_gains_db": eq_curve["band_gains_db"],
        }
        matched_wavs.append(matched)

    mix_out = PAL_ROOT / "full_reconstruction_palette.wav"
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

    mix_sha = _sha256_file(mix_out) if mix_out.exists() else None

    # Delivery emission
    shutil.copy2(str(mix_out), str(DELIV_ROOT / "full_reconstruction_palette.wav"))
    for stem in STEMS:
        rendered = PAL_ROOT / "per_stem" / stem / "render.wav"
        if rendered.is_file():
            dst = DELIV_ROOT / "per_stem" / stem
            dst.mkdir(exist_ok=True)
            shutil.copy2(str(rendered), str(dst / "render.wav"))

    # Env-pin manifest with self-anchor
    env_pins = build_env_pin_manifest()

    manifest = {
        "song_sha16": SONG_SHA16,
        "cycle": 25,
        "milestone": "M-V3-SPINE-1/wig-palette-render-c25",
        "operator_section_s": [72.77133786848073, 102.77133786848073],
        "full_reconstruction_palette_sha256": mix_sha,
        "per_stem": per_stem,
        "read_only_c21_wig_delivery_preserved": True,
        "env_pins": env_pins,
    }
    (DELIV_ROOT / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n")

    for f in ["byte_determinism.json", "fetchability_ladder.jsonl",
              "dispatch_summary.json", "anchor_preservation.json"]:
        src = PAL_ROOT / f
        if src.exists():
            shutil.copy2(str(src), str(DELIV_ROOT / f))

    (PAL_ROOT / "mix_manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n")

    print(json.dumps({
        "n_stems_matched": len(matched_wavs),
        "full_mix_sha16": mix_sha[:16] if mix_sha else None,
        "delivery_root": str(DELIV_ROOT.relative_to(_REPO)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
