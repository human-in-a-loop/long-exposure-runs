#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T12:00:00Z
# cycle: 11
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork ddd71e9bdb0e)
# milestone: M-GEN-1/rule-composition-constraint
# ---
"""Post-sampling coherence gate for M-GEN-1.

Runs AFTER `sample_ruleset` and BEFORE `assemble_score`. The gate resolves
three named rule-composition contradictions that cycle-10 clone-0 surfaced,
by *coercion* (modifying one rule to accommodate another) rather than
by dropping rules or by moving the choice back into the SHA-256 tiebreak.

Coercion rules (fixed enumeration — do NOT extend without a research
finding, per branch brief):

  1. **arrangement_silence_vs_pitched_melodic**
     Trigger: arrangement.instrumentation excludes both "bass" and "piano"
              AND melodic.pitch_class_histogram has non-zero content.
     Action:  append "piano" to arrangement.instrumentation
              (reduced-density interpretation is documented in
              docs/gen_batch_v1_report.md §2; the assembler currently
              treats presence-in-instrumentation as boolean, so the
              coercion is a set-membership add).

  2. **harmonic_progression_shorter_than_form**
     Trigger: max(section.end_measure for section in form.sections)
              exceeds len(harmonic.chord_progression).
     Action:  expand harmonic.chord_progression deterministically via
              index-modulo cycling to length == form.total_measures.

  3. **drums_pattern_empty_fallback_to_bass**
     Trigger: arrangement.instrumentation includes "drums" AND
              rhythmic.pattern is empty or all-rest.
     Action:  drop "drums" from arrangement.instrumentation and add
              "bass" (matches the extractor's cycle-9 coercion pattern).

Contract:
    enforce_coherence(ruleset) -> (coerced_ruleset, coercions_log)

Idempotence: after any coercion fires, the trigger condition no longer
holds on the coerced ruleset. Therefore
    enforce_coherence(enforce_coherence(r).ruleset).ruleset
    == enforce_coherence(r).ruleset
byte-identically (verified in scripts/gen/batch_v1.py).

Determinism: all coercions are pure functions of the input ruleset.
NO random / numpy.random / secrets / torch — SHA-256 only.

Non-factor AST isolation: this module MUST NOT import
scripts.classifier.sidecar_nonfactor.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Callable, List, Tuple

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.gen.sample_rules import SampledRuleset  # noqa: E402


COERCION_RULES = (
    "arrangement_silence_vs_pitched_melodic",
    "harmonic_progression_shorter_than_form",
    "drums_pattern_empty_fallback_to_bass",
)


def _params(rule_row):
    if not rule_row:
        return {}
    return rule_row.get("parameters") or {}


def _c1_arrangement_silence_vs_pitched(ruleset: SampledRuleset):
    arr = ruleset.rules.get("arrangement")
    mel = ruleset.rules.get("melodic")
    if not arr or not mel:
        return None
    instrumentation = list(_params(arr).get("instrumentation") or [])
    pch = list(_params(mel).get("pitch_class_histogram") or [])
    pitched_present = any(i in ("bass", "piano") for i in instrumentation)
    melodic_needs_pitched = any(float(p) > 0.0 for p in pch)
    if not pitched_present and melodic_needs_pitched:
        new_instr = list(instrumentation)
        if "piano" not in new_instr:
            new_instr.append("piano")
        arr["parameters"]["instrumentation"] = new_instr
        return {
            "rule_pair": "arrangement × melodic",
            "coercion": "arrangement_silence_vs_pitched_melodic",
            "reason": "arrangement excluded bass+piano but melodic PCH has non-zero content",
            "action": "arrangement.instrumentation.append('piano')  # reduced-density interpretation",
            "deterministic_input": {
                "before_instrumentation": instrumentation,
                "pch_nonzero_bins": sum(1 for p in pch if float(p) > 0.0),
                "pch_sum": float(sum(float(p) for p in pch)),
            },
        }
    return None


def _c2_harmonic_progression_shorter_than_form(ruleset: SampledRuleset):
    har = ruleset.rules.get("harmonic")
    frm = ruleset.rules.get("form")
    if not har or not frm:
        return None
    progression = list(_params(har).get("chord_progression") or [])
    sections = list(_params(frm).get("sections") or [])
    if not progression or not sections:
        return None
    max_end = max(int(s.get("end_measure", 0)) for s in sections)
    if max_end <= 0 or len(progression) >= max_end:
        return None
    cycled = [progression[i % len(progression)] for i in range(max_end)]
    if cycled == progression:
        return None
    har["parameters"]["chord_progression"] = cycled
    return {
        "rule_pair": "harmonic × form",
        "coercion": "harmonic_progression_shorter_than_form",
        "reason": f"len(chord_progression)={len(progression)} < form.total_measures={max_end}",
        "action": f"chord_progression cycled deterministically to length {max_end} (index modulo)",
        "deterministic_input": {
            "original_len": len(progression),
            "target_len": max_end,
            "first_cycle": progression,
        },
    }


def _c3_drums_pattern_empty_fallback_to_bass(ruleset: SampledRuleset):
    arr = ruleset.rules.get("arrangement")
    rhy = ruleset.rules.get("rhythmic")
    if not arr or not rhy:
        return None
    instrumentation = list(_params(arr).get("instrumentation") or [])
    pattern = list(_params(rhy).get("pattern") or [])
    if "drums" not in instrumentation:
        return None
    onsets = [t for t in pattern if t != "rest"]
    if onsets:
        return None
    new_instr = [i for i in instrumentation if i != "drums"]
    if "bass" not in new_instr:
        new_instr.append("bass")
    arr["parameters"]["instrumentation"] = new_instr
    return {
        "rule_pair": "arrangement × rhythmic",
        "coercion": "drums_pattern_empty_fallback_to_bass",
        "reason": "arrangement includes drums but rhythmic.pattern is empty or all rests",
        "action": "arrangement.instrumentation.remove('drums'); add 'bass'",
        "deterministic_input": {
            "before_instrumentation": instrumentation,
            "pattern_len": len(pattern),
            "n_onsets": 0,
        },
    }


# Order matters: c3 runs first (may add bass which then satisfies c1);
# c2 is independent; c1 last so it sees any bass added by c3.
_ORDERED_COERCIONS: Tuple[Callable[[SampledRuleset], dict | None], ...] = (
    _c3_drums_pattern_empty_fallback_to_bass,
    _c2_harmonic_progression_shorter_than_form,
    _c1_arrangement_silence_vs_pitched,
)


def enforce_coherence(ruleset: SampledRuleset) -> Tuple[SampledRuleset, List[dict]]:
    """Apply the 3 coercion rules; return (coerced_ruleset_copy, coercions_log).

    The input `ruleset` is NOT mutated. The returned ruleset is a deep copy
    with any coercions applied. `coercions_log` is a list of coercion
    records (empty if the ruleset was already coherent).

    Idempotence: on the coerced output, all three triggers evaluate to
    False, so `enforce_coherence(enforce_coherence(r)[0])[0]` equals
    `enforce_coherence(r)[0]` byte-identically.
    """
    coerced = SampledRuleset(
        rules=copy.deepcopy(ruleset.rules),
        sampling_manifest=copy.deepcopy(ruleset.sampling_manifest),
    )
    log: List[dict] = []
    for fn in _ORDERED_COERCIONS:
        rec = fn(coerced)
        if rec is not None:
            log.append(rec)
    coerced.sampling_manifest["coherence_gate"] = {
        "applied_coercions": [r["coercion"] for r in log],
        "n_coercions": len(log),
        "gate_version": "v1",
        "ordered_rule_set": list(COERCION_RULES),
    }
    return coerced, log


def _main(argv):
    import argparse
    import json
    from scripts.gen.sample_rules import sample_ruleset

    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path,
                    default=_REPO / "data" / "rules" / "ledger.jsonl")
    ap.add_argument("--salt", type=int, default=0)
    args = ap.parse_args(argv)

    rs = sample_ruleset(args.ledger, salt=args.salt)
    coerced, log = enforce_coherence(rs)
    print(json.dumps({
        "salt": args.salt,
        "chosen_rule_ids": rs.rule_ids(),
        "coerced_rule_ids": coerced.rule_ids(),
        "n_coercions": len(log),
        "coercions": log,
    }, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
