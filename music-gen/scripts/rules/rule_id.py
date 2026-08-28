#!/usr/bin/env python3
# M-RULES-1/schema — content-addressed rule_id derivation.
#
# Author: cyd7bevdr@mozmail.com, cycle 6 (fork 3168fb0e47a1 / clone-1).
# rule_id = "rule_" + sha256(canonical_json(payload))[:16]
# where payload = {rule_type, scope, sorted_provenance_pointers, parameters}.
# Deterministic: same content -> same id. Bit-difference -> different id.

import hashlib
import json
import sys

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"


def canonical_json(obj) -> str:
    """Deterministic serialization: sorted keys, no whitespace."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _canonicalize_provenance(pointers):
    """Sort provenance pointers by (transcription_event_id, measure_range[0], measure_range[1], clip_id)."""
    def key(p):
        return (
            p.get("transcription_event_id", ""),
            (p.get("measure_range") or [0, 0])[0],
            (p.get("measure_range") or [0, 0])[1],
            p.get("clip_id", ""),
        )
    return sorted(pointers, key=key)


def derive_rule_id(rule: dict) -> str:
    """Compute the content-addressed rule_id for a rule dict.

    Only fields that identify the *rule's content* participate:
    rule_type, scope, sorted provenance_pointers, parameters.
    Event-level fields (event_id, ts, extractor*) do NOT.
    """
    rule_type = rule.get("rule_type")
    scope = rule.get("scope")
    provenance = rule.get("provenance_pointers") or []
    parameters = rule.get("parameters")
    payload = {
        "rule_type": rule_type,
        "scope": scope,
        "provenance_pointers": _canonicalize_provenance(provenance),
        "parameters": parameters,
    }
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return f"rule_{digest[:16]}"


if __name__ == "__main__":
    # smoke: derive twice, expect equal
    example = {
        "rule_type": "harmonic",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 180.0},
        "provenance_pointers": [{"transcription_event_id": "a" * 32, "measure_range": [0, 16]}],
        "parameters": {"key": "C_major", "chord_progression": ["I", "vi", "IV", "V"], "cadence": "authentic"},
    }
    a = derive_rule_id(example)
    b = derive_rule_id(example)
    assert a == b, f"non-deterministic: {a} vs {b}"
    print(a)
