#!/usr/bin/env python3
# ------------------------------------------------------------------
# c12 Track 2 spike: verify the family-2 stem-sampled DRUMS approach
# is viable on the CG drums reference stem before authoring the full
# builder.  Sibling to c5 family2_stem_sampled_spike.py (bass; that
# module is READ-ONLY per c11 anchor block).
#
# Drums-specific:
#   * Onset detect on drums.wav via librosa.onset.onset_detect
#     (units='samples', backtrack=True) — drums are percussive, so
#     onset density is high; ~250-500 ms fixed windows per onset
#     (not the ≥6 s bass slices).
#   * NO pitch-shift: drums have kit-slot semantics.  Classify each
#     onset into {kick, snare, hihat} via low/mid/high band-energy
#     argmax, keyed to GM channel-10 pitches (36 kick, 38 snare, 42
#     closed-hh) per drums.mid content.
#
# Writes probe result to
#   data/v4/profiles/31a164f845f8e27e/drums_family2_spike_c12.json
#
# Deterministic, no PRNG.
#
# created: 2026-09-04
# cycle: 12
# run_id: run-2026-09-04T000000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-drums-family2-stem-sampled
# ------------------------------------------------------------------

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

_WORKSPACE = Path(__file__).resolve().parents[2]
_REF_STEM = (
    _WORKSPACE
    / "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/drums.wav"
)
_OUT_JSON = (
    _WORKSPACE
    / "data/v4/profiles/31a164f845f8e27e/drums_family2_spike_c12.json"
)

# Env pins (7-key canonical) applied at import time for determinism.
for _k, _v in {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}.items():
    os.environ.setdefault(_k, _v)


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def classify_slice(x: np.ndarray, sr: int) -> str:
    """Cheap band-energy classifier: {kick, snare, hihat}."""
    # STFT magnitude, hop = 256.
    S = np.abs(librosa.stft(x, n_fft=1024, hop_length=256))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=1024)
    e_low = float(S[freqs < 300].sum())
    e_mid = float(S[(freqs >= 300) & (freqs < 2000)].sum())
    e_hi = float(S[freqs >= 2000].sum())
    tot = e_low + e_mid + e_hi + 1e-9
    frac = {
        "kick": e_low / tot,
        "snare": e_mid / tot,
        "hihat": e_hi / tot,
    }
    return max(frac, key=frac.get)


def main() -> int:
    y, sr = librosa.load(str(_REF_STEM), sr=None, mono=True)
    print(f"REF stem sr={sr}, dur={len(y)/sr:.3f}s, "
          f"sha256={_sha256_file(_REF_STEM)}")

    onset_samples = librosa.onset.onset_detect(
        y=y, sr=sr, units="samples", backtrack=True)
    print(f"n_onsets={len(onset_samples)}")

    win_ms = 400
    win_n = int(sr * win_ms / 1000)
    classes = {"kick": 0, "snare": 0, "hihat": 0}
    per_onset = []
    for i, s in enumerate(onset_samples):
        seg = y[s:s + win_n]
        if seg.size < win_n // 2:
            continue
        c = classify_slice(seg, sr)
        classes[c] += 1
        if i < 8:
            per_onset.append({"idx": int(i), "sample": int(s),
                              "t_s": round(float(s) / sr, 4),
                              "class": c})

    doc = {
        "schema_version": "v1.0",
        "milestone_id": (
            "M-V4-PROFILES-1/cg-drums-family2-stem-sampled/spike"),
        "cycle": 12,
        "ref_stem_path": str(_REF_STEM.relative_to(_WORKSPACE)),
        "ref_stem_sha256": _sha256_file(_REF_STEM),
        "sample_rate": int(sr),
        "duration_s": round(float(len(y)) / sr, 4),
        "n_onsets": int(len(onset_samples)),
        "window_ms": win_ms,
        "class_distribution": classes,
        "per_onset_head_8": per_onset,
        "expected_ratio_kick_snare_hihat_from_midi": {
            "kick_p36": 30, "snare_p38": 33, "hihat_p42_44_46": 118 + 1 + 4,
        },
        "spike_verdict": (
            "VIABLE" if len(onset_samples) >= 100 and classes["hihat"] > 0
            else "SPARSE"
        ),
    }
    _OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(_OUT_JSON, "w") as f:
        json.dump(doc, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"WROTE {_OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
