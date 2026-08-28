#!/usr/bin/env python3
# ---
# created: 2026-08-28T11:32:00Z
# cycle: 12
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork ed041ef4c1dc)
# milestone: M-RULES-1/extraction/breadth-seeds
# ---
"""M-RULES-1/extraction/breadth-seeds — orchestrator.

Runs the five frozen cycle-9 extractors against the two
M-INGEST-1/breadth-second-seeds merged.musicxml scores and appends the
rule rows to ``data/rules/ledger.jsonl`` via the M-RULES-1/schema/
ledger-writer. Each row inherits the frozen extractor_version and
receives a per-seed provenance_pointers entry (naming the breadth-seed
transcription-event ids), so the resulting rule_ids are content-hash-
distinct from the cycle-9 synth_030s anchors.

Dispatch order (frozen for byte-determinism across runs):

    seeds:      ("seed_mid_50s", "synth_060s")   # alphabetical-then-numeric
    rule_types: ("harmonic", "rhythmic", "melodic", "form", "arrangement")

Non-factor AST isolation: this module MUST NOT import
``scripts.classifier.sidecar_nonfactor``.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

assert sys.executable == "/usr/bin/python3", sys.executable

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent  # extract -> rules -> scripts -> repo
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# Pin single-thread numeric libs BEFORE importing music21 (safe redundant guard).
os.environ.setdefault("PYTHONHASHSEED", "0")
for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(k, "1")

import music21  # noqa: E402

from scripts.rules.extract._common import (  # noqa: E402
    FIXED_TS, DEFAULT_TEMPO_BPM, event_id_for,
    set_extraction_context, reset_extraction_context, active_seed_name,
    NullWithReason,
)
from scripts.rules.extract import (  # noqa: E402
    harmonic, rhythmic, melodic, form, arrangement,
)
from scripts.rules.rule_id import derive_rule_id  # noqa: E402
from scripts.rules.ledger import write_rule, DEFAULT_LEDGER_PATH  # noqa: E402
from scripts.rules.validate import validate_batch, validate_row  # noqa: E402


EXTRACTORS: List[Tuple[str, Any]] = [
    ("harmonic", harmonic),
    ("rhythmic", rhythmic),
    ("melodic", melodic),
    ("form", form),
    ("arrangement", arrangement),
]

DEFAULT_SEEDS: Tuple[str, ...] = ("seed_mid_50s", "synth_060s")


def _seed_paths(seed_name: str) -> Tuple[Path, Path]:
    """Return (merged_musicxml_path, per_stem_transcription_dir)."""
    score = _REPO / "data" / "breadth" / seed_name / "merged.musicxml"
    bp_dir = _REPO / "data" / "breadth" / seed_name / "transcriptions"
    return score, bp_dir


def _finish(rule: Dict[str, Any], ext_mod, seed_name: str) -> Dict[str, Any]:
    """Add event-level fields + content-derived rule_id.

    ``ts`` is a fixed constant per cycle (byte-determinism). The seed name
    does not enter the rule payload directly — it enters through the
    seed-specific ``transcription_event_id`` values in
    ``provenance_pointers`` (guarantees rule_id distinctness across seeds).
    """
    rule["event_type"] = "rule"
    rule["schema_v"] = 1
    rule["ts"] = FIXED_TS
    rule["extractor"] = ext_mod.EXTRACTOR
    rule["extractor_version"] = ext_mod.EXTRACTOR_VERSION
    rid = derive_rule_id(rule)
    rule["rule_id"] = rid
    rule["event_id"] = event_id_for(rid)
    return rule


def _coerce_row_or_skip(rt: str, seed_name: str, score: music21.stream.Score,
                       ext_mod) -> Tuple[List[Dict[str, Any]], List[NullWithReason]]:
    """Run one extractor, catching content-incompatibility patterns.

    Coercion policy (extractor-side, no schema change):

      * harmonic:  music21.analyze("key") or chordify() empty → null:no_pitched_content;
                   ≤1 unique Roman-numeral figure → null:insufficient-progression.
      * rhythmic:  neither drums nor bass onsets available → null:no_onset_events.
      * melodic:   no pitched Part with ≥1 note → null:no_pitched_part.
      * form:      total_measures < 2 → null:too_short_for_sections.
      * arrangement: no Part with any note in the score → null:empty_instrumentation.
    """
    nulls: List[NullWithReason] = []
    rows: List[Dict[str, Any]] = []
    try:
        candidates = ext_mod.extract(score, tempo_bpm=DEFAULT_TEMPO_BPM)
    except Exception as exc:  # pragma: no cover — extractor-side crash
        nulls.append(NullWithReason(rt, "extractor_crashed", f"{type(exc).__name__}: {exc}"))
        return rows, nulls

    if rt == "harmonic":
        # Detect the "insufficient-progression" degeneracy: every candidate
        # row emitted from a corpus with fewer than 2 distinct chord
        # figures. music21 always returns *something* from chordify(), so
        # we filter on the produced payload.
        cleaned: List[Dict[str, Any]] = []
        for cand in candidates:
            prog = cand.get("parameters", {}).get("chord_progression") or []
            uniq = {p for p in prog}
            if len(uniq) < 2:
                nulls.append(NullWithReason(
                    rt, "insufficient-progression",
                    f"scope={cand.get('scope',{}).get('level')} unique_chords={len(uniq)}"))
                continue
            cleaned.append(cand)
        candidates = cleaned

    if rt == "rhythmic":
        for cand in candidates:
            pat = cand.get("parameters", {}).get("pattern") or []
            # Guard against an all-rest pattern that would still validate
            # but carries no rhythm information.
            if pat and all(tok == "rest" for tok in pat):
                nulls.append(NullWithReason(
                    rt, "all-rest-pattern",
                    f"scope={cand.get('scope',{}).get('level')} n_cells={len(pat)}"))
        candidates = [c for c in candidates
                      if not (c.get("parameters", {}).get("pattern")
                              and all(t == "rest" for t in c["parameters"]["pattern"]))]

    if rt == "melodic":
        # Drop windows where extractor emitted only an empty pitch-class
        # spike (single-bin) — those are the "no pitched content" placeholder.
        cleaned = []
        for cand in candidates:
            pch = cand.get("parameters", {}).get("pitch_class_histogram") or []
            nonzero = sum(1 for v in pch if v > 0.0)
            if nonzero == 1 and abs(sum(pch) - 1.0) < 1e-6 and pch[0] == 1.0:
                # exact placeholder — no pitched content
                nulls.append(NullWithReason(
                    rt, "no_pitched_notes",
                    f"scope={cand.get('scope',{}).get('level')}"))
                continue
            cleaned.append(cand)
        candidates = cleaned

    # form + arrangement: cycle-9 extractors always emit valid rows given a
    # score with ≥1 Part; no additional coercion needed for these two seeds.

    if not candidates:
        nulls.append(NullWithReason(rt, "no_rows_after_coercion",
                                    f"seed={seed_name}"))
        return rows, nulls

    for cand in candidates:
        rows.append(_finish(cand, ext_mod, seed_name))
    return rows, nulls


def build_rules_for_seed(seed_name: str) -> Tuple[List[Dict[str, Any]], List[NullWithReason]]:
    score_path, bp_dir = _seed_paths(seed_name)
    if not score_path.is_file():
        raise FileNotFoundError(f"breadth-seed merged.musicxml missing: {score_path}")
    if not bp_dir.is_dir():
        raise FileNotFoundError(f"breadth-seed transcription dir missing: {bp_dir}")

    set_extraction_context(seed_name, score_path, bp_dir)
    try:
        assert active_seed_name() == seed_name
        score = music21.converter.parse(str(score_path))
        all_rows: List[Dict[str, Any]] = []
        all_nulls: List[NullWithReason] = []
        for rt, mod in EXTRACTORS:
            rows, nulls = _coerce_row_or_skip(rt, seed_name, score, mod)
            all_rows.extend(rows)
            all_nulls.extend(nulls)
        return all_rows, all_nulls
    finally:
        reset_extraction_context()


def extract_from_breadth_seeds(
    ledger_path: Optional[Path] = None,
    seeds: Tuple[str, ...] = DEFAULT_SEEDS,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Run extractors on the given seeds; append validated rows to ledger.

    Returns a summary dict shaped for the report + regression harness.
    """
    lp = Path(ledger_path) if ledger_path else DEFAULT_LEDGER_PATH

    summary: Dict[str, Any] = {
        "seeds": list(seeds),
        "per_seed": {},
        "rule_ids_appended": [],
        "ledger_path": str(lp),
    }

    for seed_name in seeds:
        rows, nulls = build_rules_for_seed(seed_name)

        errs = validate_batch(rows)
        if errs:
            print(f"[breadth_seeds] validation failed on {seed_name}:", file=sys.stderr)
            for e in errs[:20]:
                print("  ", e, file=sys.stderr)
            raise SystemExit(2)

        per_type: Dict[str, int] = {}
        for r in rows:
            per_type[r["rule_type"]] = per_type.get(r["rule_type"], 0) + 1
        null_report = [n.to_dict() for n in nulls]
        summary["per_seed"][seed_name] = {
            "n_rows": len(rows),
            "per_rule_type": per_type,
            "null_with_reason": null_report,
            "rule_ids": [r["rule_id"] for r in rows],
        }

        if not dry_run:
            for r in rows:
                write_rule(r, lp)
            summary["rule_ids_appended"].extend(r["rule_id"] for r in rows)

    summary["n_total_appended"] = len(summary["rule_ids_appended"])
    return summary


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ledger", type=Path, default=None,
                    help="Ledger path (default: data/rules/ledger.jsonl)")
    ap.add_argument("--seeds", nargs="+", default=list(DEFAULT_SEEDS))
    ap.add_argument("--dry-run", action="store_true",
                    help="Build+validate rules but do not append.")
    ap.add_argument("--out-summary", type=Path,
                    default=_REPO / "data" / "rules" / "breadth_expansion_summary.json",
                    help="Where to write the per-seed summary JSON.")
    args = ap.parse_args(argv)

    summary = extract_from_breadth_seeds(
        ledger_path=args.ledger,
        seeds=tuple(args.seeds),
        dry_run=args.dry_run,
    )

    args.out_summary.parent.mkdir(parents=True, exist_ok=True)
    args.out_summary.write_text(json.dumps(summary, indent=2, sort_keys=True))

    print(json.dumps({
        "n_total_appended": summary["n_total_appended"],
        "per_seed_n_rows": {s: summary["per_seed"][s]["n_rows"] for s in summary["per_seed"]},
        "per_seed_per_rule_type": {s: summary["per_seed"][s]["per_rule_type"]
                                    for s in summary["per_seed"]},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
