#!/usr/bin/env python3
"""c7 Track B helper: compute per-file characterization metrics for the two
reconstruction WAVs (c5 Method A, c6 Method B). No aggregate score. No
recommendation. Feeds the one-page decision note.

Milestone: M-V3-SPINE-1/rc7-canonicality-note-completed (via note doc)
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
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"rc7_canonicality_metrics requires /usr/bin/python3 (got {sys.executable})"
    )

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)

OUT_JSON = _REPO / "data" / "v3_spine" / "cycle7" / "rc7_canonicality_metrics.json"

METHOD_A = (
    _REPO / "data" / "v3" / "deliveries" / "31a164f845f8e27e"
    / "operator_section" / "full_reconstruction_operator_section.wav"
)
METHOD_A_SHA = "cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7"

METHOD_B = (
    _REPO / "data" / "v3_spine" / "rc7_v2_v3_paths"
    / "rc7_v2_v3_paths_full_reconstruction.wav"
)
METHOD_B_SHA = "f40796be982998b0efbb6536e94fff1ef423f3aacc773f6101e204babc68df54"

ORIGINAL = (
    _REPO / "data" / "v3_spine" / "31a164f845f8e27e" / "operator_section" / "section.wav"
)


def _sha256(p: Path) -> str:
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _characterize(path: Path, original_stereo_first30s) -> dict:
    import librosa
    import numpy as np
    y, sr = librosa.load(str(path), sr=None, mono=False)
    if y.ndim == 1:
        y_mono = y
    else:
        y_mono = np.mean(y, axis=0)

    # LUFS via pyloudnorm.
    try:
        import pyloudnorm as pyln
        meter = pyln.Meter(sr)
        if y.ndim == 1:
            lufs_i = float(meter.integrated_loudness(y))
        else:
            lufs_i = float(meter.integrated_loudness(y.T))
        # LUFS-S (400 ms) via pyloudnorm-block loop.
        # Compute per-block short-term via block windows of 3.0 s per EBU R128.
        # Use a coarser 3s window integrated_loudness on hop-slid sub-mixes.
        hop = int(sr * 0.1)  # 100ms
        win = int(sr * 3.0)  # 3 s short-term window per R128
        vals = []
        n_frames = 1 + max(0, (y_mono.shape[0] - win) // hop)
        for i in range(n_frames):
            s = i * hop
            e = s + win
            if e > y_mono.shape[0]:
                break
            block = y[..., s:e]
            if block.ndim == 1:
                v = meter.integrated_loudness(block)
            else:
                v = meter.integrated_loudness(block.T)
            if v is not None and not (np.isinf(v) or np.isnan(v)):
                vals.append(float(v))
        lufs_s = {
            "mean": float(np.mean(vals)) if vals else None,
            "std": float(np.std(vals)) if vals else None,
            "max": float(np.max(vals)) if vals else None,
            "n_blocks": len(vals),
        }
    except Exception as e:
        lufs_i = None
        lufs_s = {"error": str(e)}

    # True peak (simple max abs sample — not upsampled true-peak, honest name).
    true_peak_amp = float(np.max(np.abs(y)))
    true_peak_dbfs = float(20.0 * np.log10(max(true_peak_amp, 1e-12)))
    max_abs_sample = true_peak_amp

    # Spectral centroid mean+std on mono.
    sc = librosa.feature.spectral_centroid(y=y_mono, sr=sr, n_fft=2048, hop_length=512)[0]
    centroid_mean = float(np.mean(sc))
    centroid_std = float(np.std(sc))

    # Spectral flatness mean.
    sf = librosa.feature.spectral_flatness(y=y_mono, n_fft=2048, hop_length=512)[0]
    flatness_mean = float(np.mean(sf))

    # mel L1 vs original operator-section (mono mixdown, first 30s of D1 slice).
    y_orig_full, sr_o = librosa.load(str(ORIGINAL), sr=None, mono=False)
    assert sr_o == sr, "sr mismatch"
    if y_orig_full.ndim == 2:
        y_orig_mono = np.mean(y_orig_full, axis=0)
    else:
        y_orig_mono = y_orig_full
    # 0..30s window (already 30s at 44.1 kHz).
    win_samples = min(y_orig_mono.shape[0], y_mono.shape[0], sr * 30)
    ref = y_orig_mono[:win_samples]
    tgt = y_mono[:win_samples]
    mel_ref = librosa.feature.melspectrogram(y=ref, sr=sr, n_mels=128, n_fft=2048, hop_length=512)
    mel_tgt = librosa.feature.melspectrogram(y=tgt, sr=sr, n_mels=128, n_fft=2048, hop_length=512)
    log_mel_ref = librosa.power_to_db(mel_ref + 1e-10)
    log_mel_tgt = librosa.power_to_db(mel_tgt + 1e-10)
    mel_l1_db = float(np.mean(np.abs(log_mel_ref - log_mel_tgt)))

    return {
        "path": str(path.relative_to(_REPO)),
        "sha256": _sha256(path),
        "sr": int(sr),
        "n_channels": int(1 if y.ndim == 1 else y.shape[0]),
        "n_samples_mono": int(y_mono.shape[0]),
        "duration_s": float(y_mono.shape[0]) / float(sr),
        "lufs_i": lufs_i,
        "lufs_s": lufs_s,
        "true_peak_dbfs": true_peak_dbfs,
        "max_abs_sample": max_abs_sample,
        "spectral_centroid_hz": {
            "mean": centroid_mean,
            "std": centroid_std,
        },
        "spectral_flatness_mean": flatness_mean,
        "mel_l1_db_vs_original_operator_section_0_30s": mel_l1_db,
    }


def main() -> None:
    a_metrics = _characterize(METHOD_A, None)
    b_metrics = _characterize(METHOD_B, None)

    # Sanity-check SHAs against the c5/c6 anchors.
    assert a_metrics["sha256"] == METHOD_A_SHA, (
        f"Method A SHA drift: {a_metrics['sha256']} != {METHOD_A_SHA}"
    )
    assert b_metrics["sha256"] == METHOD_B_SHA, (
        f"Method B SHA drift: {b_metrics['sha256']} != {METHOD_B_SHA}"
    )

    out = {
        "cycle": 7,
        "milestone": "M-V3-SPINE-1/rc7-canonicality-note-completed",
        "method_a_c5_inline_plain_rms_match": a_metrics,
        "method_b_c6_rc7_v3_paths_iirpeak_plus_rms_lufs": b_metrics,
        "note": (
            "No aggregate score; no method preferred over the other. "
            "Operator ear on the two A/B pairs is the only LANDS "
            "authority per FD-6."
        ),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT_JSON.with_suffix(OUT_JSON.suffix + ".tmp")
    tmp.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, OUT_JSON)
    print(f"wrote {OUT_JSON.relative_to(_REPO)}")


if __name__ == "__main__":
    main()
