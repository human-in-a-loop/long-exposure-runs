#!/usr/bin/env python3
"""GAP-2 fallback measurement.

Reads data/daw_spike/gap_closure_lv2_render.wav and checks whether the
RMS profile shows time-varying wet-mix as expected from the LV2 wet
automation ramp (Blend 0.05 -> 0.90 over 8 s). Compares to the cycle-1
Ardour render (Surge XT Effects reverb slot, VST3 automation
not delivered) as a control.

Tolerance (locked at investigation-phase before running the render):

  GREEN if the second-half RMS is at least 1.20 x the first-half RMS
  (analogous to the 2x ramp achieved via track-Amp automation in
  cycle 1). This is a boolean automation-delivery test: the ratio
  must reflect the wet-mix rise, not merely track-gain shape (which
  is held STATIC in this run so RMS variation comes from wet-mix only).

  still-GAP if the ratio is <= 1.05 (essentially flat — the LV2
  automation did not drive the plugin), matching the cycle-1
  VST3 outcome.

  redefined-GAP (implausible here) reserved for the case where the
  automation drove the parameter but by a different mechanism than
  originally documented.
"""
import json
import sys
import pathlib
import numpy as np
import soundfile as sf

assert sys.executable == '/usr/bin/python3', sys.executable

ROOT = pathlib.Path("/home/user/long-exposure-runs/music-gen")
OUT_JSON = ROOT / "data/daw_spike/gap2_lv2_measurement.json"


def rms_env(x: np.ndarray, sr: int, win_s: float = 0.100, hop_s: float = 0.050) -> np.ndarray:
    if x.ndim > 1:
        x = x.mean(axis=1)
    win = int(sr * win_s)
    hop = int(sr * hop_s)
    n = max(1, (len(x) - win) // hop + 1)
    env = np.empty(n, dtype=np.float64)
    for i in range(n):
        seg = x[i * hop : i * hop + win]
        env[i] = float(np.sqrt(np.mean(seg * seg)) + 1e-12)
    return env


def summarize(path: pathlib.Path) -> dict:
    x, sr = sf.read(str(path))
    env = rms_env(x, sr)
    half = len(env) // 2
    first_half = float(env[:half].mean())
    second_half = float(env[half:].mean())
    peak = float(np.max(np.abs(x)))
    return {
        "path": str(path.relative_to(ROOT)),
        "sr": sr,
        "shape": list(x.shape),
        "peak": peak,
        "rms_first_half": first_half,
        "rms_second_half": second_half,
        "second_over_first": second_half / max(first_half, 1e-12),
    }


def main():
    lv2 = summarize(ROOT / "data/daw_spike/gap_closure_lv2_render.wav")
    baseline_ardour = summarize(ROOT / "data/daw_spike/ardour_render.wav")
    # A DawDreamer render with VST3 automation delivering successfully
    # is the ground-truth reference for what "automation delivered"
    # looks like end-to-end.
    dd_matched = summarize(ROOT / "data/daw_spike/dawdreamer_render_matched.wav")

    ratio = lv2["second_over_first"]
    if ratio >= 1.20:
        verdict = "GREEN"
    elif ratio <= 1.05:
        verdict = "still-GAP"
    else:
        verdict = "PARTIAL"

    result = {
        "milestone": "M-DAW-SPIKE-1/gap-closure",
        "gap": "GAP-2",
        "gap_description": "Ardour VST3 plugin-parameter automation delivery to Surge XT Effects",
        "fallback_used": "fallback #2 — replace with LV2 reverb (a-reverb.lv2 == ACE Reverb)",
        "tolerance_metric": "second-half RMS / first-half RMS >= 1.20 (locked at investigation-phase)",
        "measurement": {
            "gap_closure_lv2": lv2,
            "cycle1_ardour_baseline_vst3": baseline_ardour,
            "cycle1_dawdreamer_matched_reference": dd_matched,
        },
        "second_over_first_ratio_lv2": ratio,
        "second_over_first_ratio_ardour_vst3_baseline": baseline_ardour["second_over_first"],
        "second_over_first_ratio_dawdreamer_reference": dd_matched["second_over_first"],
        "verdict": verdict,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
