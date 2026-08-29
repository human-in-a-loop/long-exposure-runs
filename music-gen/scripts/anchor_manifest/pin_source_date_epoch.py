#!/usr/bin/env /usr/bin/python3
"""Cycle 47 Branch C: pin SOURCE_DATE_EPOCH=1756463424 as anchor #19.

This module is the canonical extension of `scripts/anchor_manifest/` for
env-var anchor pinning. It re-exports and delegates to
`scripts/deprecation_and_anchor_pin/pin_source_date_epoch.py` (the c47
Branch C module) so both locations resolve to the same logic without
duplication.

Interpreter-guarded /usr/bin/python3. No PRNG. Canonical-JSON append.
"""
from __future__ import annotations

import os
import sys

if not sys.executable.startswith("/usr/bin/python"):
    print(f"[pin_sde:anchor_manifest] REFUSE: interpreter {sys.executable!r} "
          "is not /usr/bin/python3", file=sys.stderr)
    sys.exit(2)

# Ensure workspace on sys.path so the sibling package resolves under any CWD.
_WS = "/home/user/long-exposure-runs/music-gen"
if _WS not in sys.path:
    sys.path.insert(0, _WS)

from scripts.deprecation_and_anchor_pin.pin_source_date_epoch import (  # noqa: E402
    ANCHOR_ID,
    SOURCE_DATE_EPOCH_VALUE,
    make_entry,
    pin,
    main,
)

__all__ = ["ANCHOR_ID", "SOURCE_DATE_EPOCH_VALUE", "make_entry", "pin", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
