"""Shared license allow-list — single source of truth.

Any script that inspects image `license` fields imports ALLOWED_LICENSES from
here rather than duplicating the set. This prevents the allow-list from
drifting between the fetcher and the coverage checker.

Rules for what may live in this set:
  - Public-domain equivalents: CC0, PD, USGov-PD.
  - Creative Commons Attribution (CC-BY) at any generic/international
    version — CC-BY-2.0, CC-BY-2.5, CC-BY-3.0, CC-BY-4.0.
  - Creative Commons Attribution-ShareAlike (CC-BY-SA) — 3.0, 4.0.
Explicitly rejected: any -NC (non-commercial), -ND (no-derivatives), or
all-rights-reserved license. See tests/test_validators.py for the negative
fixture that pins the boundary.

Cycle 3, Branch C added CC-BY-2.0 and CC-BY-2.5. Ledger event:
  _infra/license-allowlist-cc-by-2 (validated, high).
"""
from __future__ import annotations

ALLOWED_LICENSES = frozenset({
    # public-domain equivalents
    "CC0",
    "PD",
    "USGov-PD",
    # CC-BY family — attribution only, any version
    "CC-BY-2.0",
    "CC-BY-2.5",
    "CC-BY-3.0",
    "CC-BY-4.0",
    # CC-BY-SA family — attribution + share-alike
    "CC-BY-SA-3.0",
    "CC-BY-SA-4.0",
})
