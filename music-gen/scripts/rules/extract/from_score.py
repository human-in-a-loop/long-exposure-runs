#!/usr/bin/env python3
# M-RULES-1/extraction — orchestrator.
#
# Author: cyd7bevdr@mozmail.com, cycle 9 (fork f1bae241bde9 / clone-0).
#
# Reads the frozen M-SCORE-1 merged 30-s MusicXML, dispatches to the five
# per-rule_type extractors, decorates each candidate rule with a
# content-derived rule_id + event_id + fixed ts + extractor metadata,
# validates against the schema, and appends via write_rule.
#
# Byte-identical re-run: every field is deterministic given the frozen
# inputs. ts is constant across runs.
#
# Non-factor AST isolation: this module MUST NOT import
# scripts.classifier.sidecar_nonfactor.

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent  # extract -> rules -> scripts -> repo
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import music21

from scripts.rules.extract._common import (
    SCORE_PATH, FIXED_TS, DEFAULT_TEMPO_BPM, event_id_for,
)
from scripts.rules.extract import harmonic, rhythmic, melodic, form, arrangement
from scripts.rules.rule_id import derive_rule_id
from scripts.rules.ledger import write_rule, DEFAULT_LEDGER_PATH
from scripts.rules.validate import validate_batch

EXTRACTORS = [
    ("harmonic", harmonic),
    ("rhythmic", rhythmic),
    ("melodic", melodic),
    ("form", form),
    ("arrangement", arrangement),
]


def _finish(rule: Dict[str, Any], ext_mod) -> Dict[str, Any]:
    """Add event_type/schema_v/ts/extractor/extractor_version/rule_id/event_id."""
    rule["event_type"] = "rule"
    rule["schema_v"] = 1
    rule["ts"] = FIXED_TS
    rule["extractor"] = ext_mod.EXTRACTOR
    rule["extractor_version"] = ext_mod.EXTRACTOR_VERSION
    rule_id = derive_rule_id(rule)
    rule["rule_id"] = rule_id
    rule["event_id"] = event_id_for(rule_id)
    return rule


def build_rules(score: music21.stream.Score,
                tempo_bpm: float = DEFAULT_TEMPO_BPM) -> List[Dict[str, Any]]:
    """Run every extractor and return the finished rule dicts."""
    out: List[Dict[str, Any]] = []
    for _, mod in EXTRACTORS:
        for candidate in mod.extract(score, tempo_bpm=tempo_bpm):
            out.append(_finish(candidate, mod))
    return out


def run(ledger_path: Optional[Path] = None,
        score_path: Optional[Path] = None) -> Dict[str, Any]:
    sp = Path(score_path) if score_path else SCORE_PATH
    lp = Path(ledger_path) if ledger_path else DEFAULT_LEDGER_PATH

    score = music21.converter.parse(str(sp))
    rules = build_rules(score)
    errors = validate_batch(rules)
    if errors:
        print("VALIDATION FAILED", file=sys.stderr)
        for e in errors[:40]:
            print("  ", e, file=sys.stderr)
        raise SystemExit(2)

    # Fresh append; caller is responsible for using a fresh path if they
    # want a clean run.
    for r in rules:
        write_rule(r, lp)

    summary = {
        "n_rules": len(rules),
        "per_type": {},
        "ledger_path": str(lp),
        "rule_ids": [r["rule_id"] for r in rules],
    }
    for r in rules:
        summary["per_type"].setdefault(r["rule_type"], 0)
        summary["per_type"][r["rule_type"]] += 1
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description="M-RULES-1 extraction from merged score.")
    ap.add_argument("--ledger", default=None, help="Ledger path (default: data/rules/ledger.jsonl)")
    ap.add_argument("--score", default=None, help="MusicXML path (default: merged_synth030s)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Build+validate rules but do not append to any ledger.")
    args = ap.parse_args(argv)

    if args.dry_run:
        score = music21.converter.parse(str(SCORE_PATH if args.score is None else args.score))
        rules = build_rules(score)
        errors = validate_batch(rules)
        summary = {
            "n_rules": len(rules),
            "per_type": {},
            "errors": errors,
            "rule_ids": [r["rule_id"] for r in rules],
        }
        for r in rules:
            summary["per_type"].setdefault(r["rule_type"], 0)
            summary["per_type"][r["rule_type"]] += 1
        import json as _json
        print(_json.dumps(summary, indent=2))
        return 0 if not errors else 2

    summary = run(ledger_path=args.ledger, score_path=args.score)
    import json as _json
    print(_json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
