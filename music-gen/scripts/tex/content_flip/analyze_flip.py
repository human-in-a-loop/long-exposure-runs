#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T14:30:00Z
# cycle: 14
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel/embedding/content-flip-analysis
# ---
"""Post-sweep analysis of the VGGish content-flip signal.

Signal definition (documented in the report §2):

  For every variant v in the sweep (P1..P4 on polyphony, E1..E4 on
  envelope), the M-TEX-1/panel is called on the (bare_midi, effects_layered)
  pair to yield mel_l1_db(v) and vggish(v) (embedding_cosine_distance).

  Family-disagreement sign relative to a baseline B:
      dmel(v)  = mel_l1_db(v)  - mel_l1_db(B)
      dvgg(v)  = vggish(v)     - vggish(B)
      s_mel(v) = sign(dmel(v))
      s_vgg(v) = sign(dvgg(v))
      agree(v) = s_mel(v) * s_vgg(v)    # +1 agree, -1 disagree, 0 tie

  A "flip" along an axis is a variant transition where agree(v) changes
  sign. Baselines: P4 (max polyphony) for polyphony axis; E4 (harmonic-
  sustained) for envelope axis.

Cycle-13 anchors provide three reference signs computed the same way but
across stages of one seed (bare_midi -> effects_layered) rather than across
variants of one axis. They are reported side-by-side for interpretation but
do NOT enter the axis-threshold characterization directly (the semantics
differ — same-variant across-stages vs across-variants same-pair).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

assert sys.executable == "/usr/bin/python3", sys.executable

WS = Path(__file__).resolve().parents[3]


def _read_sweep(tsv: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with tsv.open("r", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            rows.append(row)
    return rows


def _f(row: Dict[str, str], key: str) -> float:
    return float(row[key])


def _sign(x: float) -> int:
    if x > 0:
        return +1
    if x < 0:
        return -1
    return 0


def analyze_axis(rows: List[Dict[str, str]], axis: str,
                 baseline_variant: str) -> Dict[str, object]:
    """Return per-axis disagreement signs relative to baseline_variant."""
    axis_rows = [r for r in rows if r["axis"] == axis]
    axis_rows.sort(key=lambda r: int(r["rank"]))
    baseline = next(r for r in axis_rows if r["variant_id"] == baseline_variant)
    b_mel = _f(baseline, "mel_l1_db")
    b_vgg = _f(baseline, "embedding_cosine_distance")

    entries = []
    signs_agree = []
    for r in axis_rows:
        v = r["variant_id"]
        mel = _f(r, "mel_l1_db")
        vgg = _f(r, "embedding_cosine_distance")
        dmel = mel - b_mel
        dvgg = vgg - b_vgg
        s_mel = _sign(dmel)
        s_vgg = _sign(dvgg)
        agree = s_mel * s_vgg
        signs_agree.append((int(r["rank"]), agree))
        entries.append({
            "variant_id": v,
            "rank": int(r["rank"]),
            "mel_l1_db": mel,
            "vggish_cosine": vgg,
            "dmel_vs_baseline": dmel,
            "dvgg_vs_baseline": dvgg,
            "s_mel": s_mel,
            "s_vgg": s_vgg,
            "agree": agree,
        })

    # Locate a flip (transition of the `agree` sign) along the rank axis
    # (skipping the baseline itself whose agree is 0).
    trans: List[Tuple[int, int, int]] = []
    prev_a = None
    for rank, a in sorted(signs_agree):
        if a == 0:  # baseline — no comparison
            continue
        if prev_a is not None and prev_a != a:
            trans.append((rank - 1, rank, a))
        prev_a = a

    return {
        "axis": axis,
        "baseline_variant": baseline_variant,
        "entries": entries,
        "flip_transitions": [
            {"from_rank": a, "to_rank": b, "new_agree": s} for (a, b, s) in trans
        ],
        "n_disagree": sum(1 for _, a in signs_agree if a == -1),
        "n_agree":    sum(1 for _, a in signs_agree if a == +1),
        "n_tie":      sum(1 for _, a in signs_agree if a == 0),
    }


def analyze_full(sweep_tsv: Path, anchor_tsvs: Dict[str, Path]) -> Dict[str, object]:
    rows = _read_sweep(sweep_tsv)

    poly = analyze_axis(rows, "polyphony", "P4")
    env  = analyze_axis(rows, "envelope",  "E4")

    # Cycle-13 anchor across-stage signs (side-panel — informational).
    anchors: Dict[str, dict] = {}
    for seed, tsv in anchor_tsvs.items():
        seed_rows = list(csv.DictReader(tsv.open("r"), delimiter="\t"))
        # find (original, bare_midi) and (original, effects_layered).
        row_ob = next(r for r in seed_rows
                      if r["a_stage"] == "original" and r["b_stage"] == "bare_midi")
        row_oe = next(r for r in seed_rows
                      if r["a_stage"] == "original" and r["b_stage"] == "effects_layered")
        dmel = _f(row_oe, "mel_l1_db") - _f(row_ob, "mel_l1_db")
        dvgg = _f(row_oe, "embedding_cosine_distance") - _f(row_ob, "embedding_cosine_distance")
        anchors[seed] = {
            "d_mel_l1_db_orig_eff_vs_orig_bare": dmel,
            "d_vggish_orig_eff_vs_orig_bare":    dvgg,
            "s_mel": _sign(dmel),
            "s_vgg": _sign(dvgg),
            "agree": _sign(dmel) * _sign(dvgg),
        }

    # Threshold characterization heuristic.
    # We call it "polyphony-localized" if the polyphony axis has ≥1 flip
    # transition AND the envelope axis has 0. Vice-versa for envelope.
    # "both" if both axes have ≥1 flip. "neither" if neither.
    poly_has_flip = len(poly["flip_transitions"]) >= 1
    env_has_flip  = len(env["flip_transitions"])  >= 1
    if poly_has_flip and not env_has_flip:
        flip_dim = "polyphony"
    elif env_has_flip and not poly_has_flip:
        flip_dim = "envelope"
    elif poly_has_flip and env_has_flip:
        flip_dim = "both"
    else:
        flip_dim = "neither"

    # Additional check: was the sign truly consistent within each axis
    # (excluding baseline)? If both non-baseline signs are identical the
    # axis is "flat" — no informative flip.
    def _axis_consistency(a: dict) -> str:
        non_base = [e["agree"] for e in a["entries"]
                    if e["variant_id"] != a["baseline_variant"]]
        if not non_base:
            return "no_data"
        if all(x == non_base[0] for x in non_base):
            return "consistent"
        return "mixed"

    poly_consistency = _axis_consistency(poly)
    env_consistency  = _axis_consistency(env)

    # Confidence heuristic: if the axis has a clean single flip AND the
    # dmel/dvgg magnitudes are comfortably above noise (say > 5% of the
    # baseline value), call it "medium/high" — otherwise "low".
    def _magnitude_confidence(a: dict) -> str:
        base_mel = next(e["mel_l1_db"] for e in a["entries"]
                        if e["variant_id"] == a["baseline_variant"])
        base_vgg = next(e["vggish_cosine"] for e in a["entries"]
                        if e["variant_id"] == a["baseline_variant"])
        for e in a["entries"]:
            if e["variant_id"] == a["baseline_variant"]:
                continue
            if abs(e["dmel_vs_baseline"]) < 0.05 * max(abs(base_mel), 1e-9):
                return "low"
            if abs(e["dvgg_vs_baseline"]) < 0.05 * max(abs(base_vgg), 1e-9):
                return "low"
        return "medium"

    poly_conf = _magnitude_confidence(poly)
    env_conf  = _magnitude_confidence(env)

    # Final verdict per Rung 6 (single-line summary).
    if flip_dim == "neither":
        verdict = "no_flip_reproduced"
    elif flip_dim == "both":
        verdict = "flip_polydimensional"
    elif flip_dim in ("polyphony", "envelope"):
        # localizes to a single axis.
        if (poly_conf == "low" and env_conf == "low"):
            verdict = "noisy"
        else:
            verdict = f"localized_to_{flip_dim}"
    else:
        verdict = "unknown"

    result = {
        "verdict": verdict,
        "flip_dimension": flip_dim,
        "polyphony_axis": poly,
        "envelope_axis":  env,
        "polyphony_axis_consistency": poly_consistency,
        "envelope_axis_consistency":  env_consistency,
        "polyphony_magnitude_confidence": poly_conf,
        "envelope_magnitude_confidence":  env_conf,
        "cycle13_anchors_across_stage": anchors,
        "notes": (
            "Baseline for polyphony sweep: P4 (max polyphony, closest to "
            "the cycle-13 polyphonic seeds synth_030s / synth_060s). "
            "Baseline for envelope sweep: E4 (harmonic-sustained, most "
            "spectrally busy long-lived content). Flip = transition in the "
            "sign of dmel*dvgg along the axis. Cycle-13 anchors capture "
            "across-stage signs (bare_midi->effects_layered relative to "
            "original) — orthogonal comparison, reported side-by-side for "
            "interpretation only."
        ),
    }
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep-tsv",
                    default="data/tex/embedding_flip_analysis/sweep_results.tsv")
    ap.add_argument("--out-json",
                    default="data/tex/embedding_flip_analysis/threshold_characterization.json")
    args = ap.parse_args()

    sweep = (WS / args.sweep_tsv).resolve()
    anchors = {
        "synth_030s":   WS / "data/tex/stage_by_stage_synth_030s.tsv",
        "seed_mid_50s": WS / "data/tex/stage_by_stage_seed_mid_50s.tsv",
        "synth_060s":   WS / "data/tex/stage_by_stage_synth_060s.tsv",
    }
    result = analyze_full(sweep, anchors)
    out = (WS / args.out_json).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"[analyze_flip] verdict={result['verdict']!r} flip_dim={result['flip_dimension']!r}")
    print(f"[analyze_flip] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
