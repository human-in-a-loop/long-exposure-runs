#!/usr/bin/python3
# ------------------------------------------------------------------
# c15 Track 2 spike: CG guitar family-2 stem-sampled sample-bank probe.
#
# Sibling to c5/c6 family2_stem_sampled_builder.py (bass — READ-ONLY)
# and c12 family2_stem_sampled_drums_builder.py (drums — READ-ONLY).
# Guitar-specific adaptations per the c15 research brief:
#
#   * Onset detect on guitar stem via librosa.onset.onset_detect
#     (units='samples', backtrack=True).
#   * Fixed 400 ms slices per onset (matches drums c12 shape).
#   * Guitar IS pitched — sample bank indexed by MIDI pitch derived
#     via librosa.pyin median (matches bass c5/c6 pitch-shift path).
#   * NO PRNG.  Deterministic per-pitch k-th selection at render time.
#
# This spike file is a diagnostic wrapper around the builder's
# build_sample_bank function; it emits per-pitch counts + onset count
# to a JSON manifest for provenance.
#
# created: 2026-09-04
# cycle: 15
# run_id: run-2026-09-04T100000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-guitar-family2-stem-sampled
# ------------------------------------------------------------------
from __future__ import annotations

import json
import sys
from pathlib import Path

from family2_stem_sampled_guitar_builder import (  # type: ignore
    build_sample_bank,
    _WORKSPACE,
    _sha256_file,
)


def main() -> int:
    ref_stem = (
        _WORKSPACE
        / "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/guitar.wav"
    )
    bank, sr, diag = build_sample_bank(ref_stem)
    out = {
        "schema_version": "v1.0",
        "milestone_id": (
            "M-V4-PROFILES-1/cg-guitar-family2-stem-sampled/spike"),
        "cycle": 15,
        "ref_stem_path": str(ref_stem.relative_to(_WORKSPACE)),
        "ref_stem_sha256": _sha256_file(ref_stem),
        "sample_rate": sr,
        "bank_per_pitch_counts": {
            str(p): len(v) for p, v in sorted(bank.items())},
        "n_unique_pitches_extracted": len(bank),
        "diag": diag,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
