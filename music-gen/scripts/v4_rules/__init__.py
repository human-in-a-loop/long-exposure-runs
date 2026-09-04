#!/usr/bin/python3
# ---
# cycle: 21
# milestone: M-V4-RULES-1/substantive
# purpose: Package init. Re-exports the substantive extractor entry
#          points. See extract_v4.py.
# ---
"""M-V4-RULES-1 substantive package (c21+)."""
from .extract_v4 import (  # noqa: F401
    extract,
    extract_rules_v4,
    compute_rule_id,
    list_corpus_songs,
    RULE_TYPES,
    STEM_ORDER,
    CANONICAL_ENV_PIN_SHA,
    EXTRACTOR_VERSION,
)

__all__ = (
    "extract",
    "extract_rules_v4",
    "compute_rule_id",
    "list_corpus_songs",
    "RULE_TYPES",
    "STEM_ORDER",
    "CANONICAL_ENV_PIN_SHA",
    "EXTRACTOR_VERSION",
)
