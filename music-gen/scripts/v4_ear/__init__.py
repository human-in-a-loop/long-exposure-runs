#!/usr/bin/python3
"""M-V4-EAR-1 lightweight exemplar-ear package (c21+)."""
from .ear import (  # noqa: F401
    EXEMPLARS,
    BAND_4_SPOT_CHECK,
    CANONICAL_ENV_PIN_SHA,
    run_ear,
)

__all__ = ("EXEMPLARS", "BAND_4_SPOT_CHECK", "CANONICAL_ENV_PIN_SHA", "run_ear")
