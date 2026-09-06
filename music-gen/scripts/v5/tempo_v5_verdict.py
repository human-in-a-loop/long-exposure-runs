#!/usr/bin/python3
"""c79 P2 — evaluate the FROZEN falsification targets for tempo_v5 (no retune).

created: 2026-09-06T00:00:00Z
cycle: 79
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/tempo-v5-halt-honest-c79

Reads data/v5/corpus/<sha16>/tempo_v5.json for the five anchored focus songs and
the WIG mechanism probe; applies the pre-registered RULES-IN / RULES-OUT clauses
verbatim from the c79 brief; writes data/v5/corpus/tempo_v5_falsification.json
with the failing lag tables. The criterion is NEVER adjusted here (FD-1).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)
_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)

ROOT = Path("data/v5/corpus")
WIG, CG, PD, ROME, DISCO = ("252eb21ce7df7328", "31a164f845f8e27e", "88d247468cb6d49f",
                            "51e433ade2a845e1", "cdd2717e52820ff6")


def load(s: str) -> dict:
    return json.loads((ROOT / s / "tempo_v5.json").read_text())


def lag_table(t: dict, lo_bpm: float = 60.0, hi_bpm: float = 200.0) -> list[dict]:
    lt = t["autocorr_lag_table"]
    rows = []
    for i, (b, a) in enumerate(zip(lt["bpm_per_lag"], lt["autocorr_norm"]), start=lt["lag_frames_start"]):
        if lo_bpm <= b <= hi_bpm:
            rows.append({"lag_frames": i, "bpm": b, "autocorr_norm": a})
    return rows


def main() -> int:
    T = {s: load(s) for s in (WIG, CG, PD, ROME, DISCO)}
    probe = json.loads((ROOT / WIG / "tempo_v5_wig_mechanism_probe.json").read_text())
    drums = probe["probes"]["drums_operator_section_c20"]

    # --- frozen per-song targets ------------------------------------------------
    wig_full_ok = not (45.0 <= T[WIG]["bpm_v5"] <= 56.0) and abs(T[WIG]["bpm_v5"] - 100.35) <= 3.0
    wig_rules_in_strict = bool(95.0 <= T[WIG]["bpm_v5"] <= 106.0 and T[WIG]["ratio_2T_over_T"] >= 1.10)
    wig_drums_resolved = not (45.0 <= drums["bpm_v5"] <= 56.0) and abs(drums["bpm_v5"] - 100.35) <= 3.0
    wig_drums_ac_dominant = drums["ratio_2T_over_T"] is not None and drums["ratio_2T_over_T"] >= 1.10

    per_song = {}
    for s in (CG, PD, ROME, DISCO):
        t = T[s]
        a = t["anchors"]["anchor_bpm"]
        d = t["bpm_v5"] - a
        ratio = t["bpm_v5"] / a
        octave = any(abs(ratio - r) / r <= 0.03 for r in (0.5, 1.0, 2.0))
        per_song[s] = {"name": t["anchors"]["name"], "bpm_librosa": t["bpm_librosa"], "bpm_v5": t["bpm_v5"],
                       "anchor_bpm": a, "delta_bpm": round(d, 4), "ratio_v5_over_anchor": round(ratio, 4),
                       "within_2bpm": abs(d) <= 2.0, "octave_relation_to_anchor": octave,
                       "non_octave_regression_gt_2bpm": (abs(d) > 2.0 and not octave),
                       "winner_candidate": t["winner_candidate"],
                       "librosa_matched_anchor_within_2bpm": abs(t["bpm_librosa"] - a) <= 2.0}
    per_song[WIG] = {"name": "What If I Go", "bpm_librosa_full_length": T[WIG]["bpm_librosa"],
                     "bpm_v5_full_length": T[WIG]["bpm_v5"], "c20_anchor_drums_section": 50.17445388349515,
                     "full_length_out_of_half_time_band_and_near_100": wig_full_ok,
                     "rules_in_strict_clause_full_length": wig_rules_in_strict,
                     "ratio_2T_over_T_full_length": T[WIG]["ratio_2T_over_T"],
                     "drums_section_probe": {"bpm_librosa": drums["bpm_librosa"], "bpm_v5": drums["bpm_v5"],
                                             "winner": drums["winner_candidate"],
                                             "ratio_2T_over_T": drums["ratio_2T_over_T"],
                                             "resolved_out_of_half_time": wig_drums_resolved,
                                             "autocorr_2T_dominant_ge_1p10": wig_drums_ac_dominant}}

    failing = [s for s in (CG, PD, ROME, DISCO) if per_song[s]["non_octave_regression_gt_2bpm"]]
    rules_out = len(failing) > 0
    verdict = "RULES_OUT_CRITERION_TOO_PERMISSIVE" if rules_out else ("RULES_IN" if wig_full_ok else "RULES_OUT_WIG_STILL_HALF_TIME")

    out = {
        "schema_version": 1, "cycle": 79,
        "verdict": verdict,
        "verdict_rationale": (
            "Pre-registered RULES-OUT clause fired: anchored song(s) regress by a NON-octave factor > 2 BPM under the "
            "flat-band autocorrelation criterion. The raw onset autocorrelation is a decaying function without metrical "
            "hierarchy; a 3:2-related lag (e.g. lag 32 = 80.75 BPM vs lag 21 = 123.05 BPM) can carry a higher normalized "
            "value than the true beat lag. Criterion NOT adjusted post hoc (FD-1). librosa's prior-driven estimate matched "
            "every anchored song's anchor on the FULL-LENGTH mix, including WIG (99.38, not 50.17)."
            if rules_out else "All frozen targets met."),
        "wig_finding": (
            "The c20 WIG 50.17 half-time value came from librosa.beat.beat_track on the 30 s DRUMS STEM of the operator "
            "section (v3 tempo_map prefers the drums stem when its estimate > 20 BPM). On the full-length MIX librosa "
            "returns 99.38 directly (the same value c20 recorded for the full-mix section). The v5 octave-candidate + "
            "plausibility band resolves the drums-stem probe 49.69 -> 99.38 via the [55,220] band (49.69 has weight 0), "
            "NOT via autocorrelation dominance: autocorr at 2T is 0.32x autocorr at T on that stem, so the strict "
            "'2T exceeds T by >= 10 %' clause FAILS. Mechanism verdict: the half-time was a stem-choice + band artifact, "
            "not a prior octave-bias on the mix."),
        "failing_songs": failing,
        "per_song": per_song,
        "lag_tables_failing": {s: lag_table(T[s]) for s in failing},
        "lag_quantization_note": T[PD]["lag_quantization_note"],
        "downstream_policy": (
            "Per brief §diagnostic_ladder Rung 3, transcription launches regardless using bpm_v5 (MuScriptor JSON is "
            "tempo-independent; canonical MIDI re-serializes from cached JSON at a revised BPM in seconds). Songs whose "
            "bpm_v5 disagrees with a librosa-matched anchor are flagged in transcription manifests for c80 re-canonicalization "
            "once a metrically-aware criterion (e.g. comb-filter / tempogram with harmonic weighting) is pre-registered."),
        "anchor_dir_disclosure": "data/recreate_v2/baseline/<sha16>/rc5_tempo_bpm.json (brief §P1) is ABSENT on this instance; anchors taken from on-disk tempo_choice.json files (invariant (d)).",
    }
    p = ROOT / "tempo_v5_falsification.json"
    p.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("verdict", "failing_songs")}, indent=1))
    for s, r in per_song.items():
        print(s, {k: v for k, v in r.items() if k not in ("drums_section_probe",)})
    print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
