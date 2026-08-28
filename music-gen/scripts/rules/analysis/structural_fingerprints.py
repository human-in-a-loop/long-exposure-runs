#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:30:00Z
# cycle: 14
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 855d4c2e9945)
# milestone: M-GEN-1/collision-floor-investigation
# ---
"""Per-rule_type structural fingerprint extractor.

Every fingerprint field is derived from the rule row's `parameters`
block via deterministic extraction. No PRNG. No metadata fields
(rule_id, provenance_pointers, ts, confidence) leak in.

Emits fingerprints.tsv, one row per rule.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Dict, List

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.rules.ledger import effective_rules  # noqa: E402
from scripts.gen.sample_rules import RULE_TYPES  # noqa: E402


def _prog_sig(prog: List[str]) -> str:
    """Content-hashed short signature of a chord progression."""
    canonical = json.dumps(prog, separators=(",", ":"), sort_keys=False)
    return hashlib.sha256(canonical.encode()).hexdigest()[:12]


def _pattern_sig(pattern: List[str]) -> str:
    canonical = json.dumps(pattern, separators=(",", ":"), sort_keys=False)
    return hashlib.sha256(canonical.encode()).hexdigest()[:12]


def _pch_entropy(pch: List[float]) -> float:
    e = 0.0
    for p in pch:
        if p > 0:
            e -= p * math.log2(p)
    return e


def _dominant_pc(pch: List[float]) -> int:
    if not pch:
        return -1
    m = max(pch)
    for i, p in enumerate(pch):
        if p == m:
            return i
    return -1


def _classify_form(sections: List[dict]) -> str:
    """Return one of: monolithic / uniform_4m / uniform_2m / ABAB / ABA / other."""
    if not sections:
        return "empty"
    labels = [s.get("label", "?") for s in sections]
    lens = [s.get("end_measure", 0) - s.get("start_measure", 0) for s in sections]
    if len(sections) == 1:
        return "monolithic"
    unique_lens = set(lens)
    if len(unique_lens) == 1:
        L = lens[0]
        if L == 4:
            return "uniform_4m"
        if L == 2:
            return "uniform_2m"
        return f"uniform_{L}m"
    if labels == ["A", "B", "A", "B"] or labels == ["A", "B", "A", "B", "A", "B"]:
        return "ABAB"
    if labels == ["A", "B", "A"]:
        return "ABA"
    return "other"


def fingerprint_harmonic(params: dict) -> Dict:
    key = params.get("key", "?")
    prog = params.get("chord_progression", []) or []
    cadence = params.get("cadence", "none")
    return {
        "key": key,
        "cadence": cadence,
        "progression_length": len(prog),
        "progression_sig": _prog_sig(prog),
        "unique_chords": len(set(prog)),
    }


def fingerprint_rhythmic(params: dict) -> Dict:
    pattern = params.get("pattern", []) or []
    tempo = float(params.get("tempo_bpm", 0.0))
    meter = params.get("meter", "?")
    swing = float(params.get("swing_ratio", 0.5))
    n_rest = sum(1 for t in pattern if t == "rest")
    n_total = len(pattern) if pattern else 1
    return {
        "meter": meter,
        "tempo_bpm": tempo,
        "swing_ratio": swing,
        "pattern_length": len(pattern),
        "onset_density": (n_total - n_rest) / n_total,
        "pattern_sig": _pattern_sig(pattern),
    }


def fingerprint_melodic(params: dict) -> Dict:
    pch = params.get("pitch_class_histogram", []) or []
    contour = params.get("contour", "?")
    range_st = int(params.get("range_semitones", 0))
    return {
        "contour": contour,
        "range_semitones": range_st,
        "dominant_pc": _dominant_pc(pch),
        "pch_entropy": _pch_entropy(pch),
        "pch_nonzero_bins": sum(1 for p in pch if p > 0),
    }


def fingerprint_form(params: dict) -> Dict:
    sections = params.get("sections", []) or []
    total = 0
    if sections:
        total = max(s.get("end_measure", 0) for s in sections)
    return {
        "section_pattern": _classify_form(sections),
        "n_sections": len(sections),
        "total_measures": total,
    }


def fingerprint_arrangement(params: dict) -> Dict:
    inst = params.get("instrumentation", []) or []
    dot = params.get("density_over_time", []) or []
    events = params.get("layer_events", []) or []
    active = [x for x in dot if x > 0]
    if dot:
        mean = sum(dot) / len(dot)
        variance = sum((x - mean) ** 2 for x in dot) / len(dot)
        std = math.sqrt(variance)
        peak_idx = max(range(len(dot)), key=lambda i: dot[i])
        peak_frac = peak_idx / max(len(dot) - 1, 1)
    else:
        mean = std = peak_frac = 0.0
    return {
        "has_drums": int("drums" in inst),
        "has_bass": int("bass" in inst),
        "has_other": int("other" in inst),
        "instr_count": len(inst),
        "density_mean": mean,
        "density_std": std,
        "peak_location_fraction": peak_frac,
        "active_frac": len(active) / max(len(dot), 1),
        "n_layer_events": len(events),
    }


_FP_BY_TYPE = {
    "harmonic": fingerprint_harmonic,
    "rhythmic": fingerprint_rhythmic,
    "melodic": fingerprint_melodic,
    "form": fingerprint_form,
    "arrangement": fingerprint_arrangement,
}


# Deterministic column ordering per rule_type (used by pairwise_distance)
FIELDS_BY_TYPE = {
    "harmonic": ["key", "cadence", "progression_length", "progression_sig", "unique_chords"],
    "rhythmic": ["meter", "tempo_bpm", "swing_ratio", "pattern_length", "onset_density", "pattern_sig"],
    "melodic": ["contour", "range_semitones", "dominant_pc", "pch_entropy", "pch_nonzero_bins"],
    "form": ["section_pattern", "n_sections", "total_measures"],
    "arrangement": ["has_drums", "has_bass", "has_other", "instr_count",
                    "density_mean", "density_std", "peak_location_fraction",
                    "active_frac", "n_layer_events"],
}

# Which fields are categorical (Hamming) vs numeric (normalized-difference).
CATEGORICAL_FIELDS = {
    "harmonic": {"key", "cadence", "progression_sig"},
    "rhythmic": {"meter", "pattern_sig"},
    "melodic": {"contour", "dominant_pc"},
    "form": {"section_pattern"},
    "arrangement": {"has_drums", "has_bass", "has_other"},
}


def extract_all(ledger_path: Path) -> List[dict]:
    """Return one fingerprint row per effective rule."""
    rows: List[dict] = []
    rules = effective_rules(Path(ledger_path))
    for r in rules:
        rt = r.get("rule_type")
        if rt not in _FP_BY_TYPE:
            continue
        fp = _FP_BY_TYPE[rt](r.get("parameters", {}) or {})
        rows.append({
            "rule_id": r.get("rule_id"),
            "rule_type": rt,
            **{f"fp_{k}": v for k, v in fp.items()},
        })
    return rows


def write_tsv(rows: List[dict], out_path: Path) -> None:
    """Write fingerprints TSV with a stable union of columns."""
    # Collect all columns in a deterministic order: rule_id, rule_type,
    # then per-type fp_* keys in FIELDS_BY_TYPE order.
    header = ["rule_id", "rule_type"]
    for rt in RULE_TYPES:
        for f in FIELDS_BY_TYPE[rt]:
            col = f"fp_{f}"
            if col not in header:
                header.append(col)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(header)]
    for row in rows:
        line = []
        for col in header:
            v = row.get(col, "")
            if isinstance(v, float):
                # Fixed 6-decimal float formatting for byte-determinism.
                line.append(f"{v:.6f}")
            else:
                line.append(str(v))
        lines.append("\t".join(line))
    out_path.write_text("\n".join(lines) + "\n")


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path,
                    default=_REPO / "data" / "rules" / "ledger.jsonl")
    ap.add_argument("--out", type=Path,
                    default=_REPO / "data" / "rules" /
                    "collision_floor_analysis" / "fingerprints.tsv")
    args = ap.parse_args(argv)
    rows = extract_all(args.ledger)
    write_tsv(rows, args.out)
    print(f"[structural_fingerprints] wrote {args.out} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
