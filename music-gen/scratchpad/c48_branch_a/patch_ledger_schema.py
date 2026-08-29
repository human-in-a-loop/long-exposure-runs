#!/usr/bin/env python3
"""Apply c48 _infra/harness-and-writer-hardening-v3 sub-fix 2 edits to
long_exposure/tools/_ledger_schema.py.

Adds `canonical_json_bytes(event, include_supersedes)` and
`content_hash_event_id_v2(event, include_supersedes)` as first-class helpers,
plus a comment upgrade around the existing supersedes optional-field surface
to note the c48 first-class status.

Idempotent — re-running the patch on an already-patched file is a no-op.
"""
import pathlib

TARGET = pathlib.Path('/home/user/human-in-a-loop/long-exposure/long_exposure/tools/_ledger_schema.py')

MARKER = "# --- Cycle-48 _infra/harness-and-writer-hardening-v3 sub-fix 2"

APPEND_BLOCK = '''

# --- Cycle-48 _infra/harness-and-writer-hardening-v3 sub-fix 2 --------------
#
# First-class canonical-JSON helper with an explicit `include_supersedes`
# toggle. Called by ``workspace_bootstrap.append_ledger_event`` when the
# ``MUSICGEN_LEDGER_SUPERSEDES_IN_HASH`` env var is set (flag semantics
# defined in ``docs/harness_and_writer_hardening_v3_rubric.md``).
#
# Rationale (c47 audit issue #3): the c46 line-745 event was written before
# the ``supersedes`` field was added; a future write-path replay from the
# row's current content would re-derive ``event_id`` and diverge from the
# on-disk id ``658231db-5d86-56e5-8ca9-2a9bed7fdf9f``. Default
# ``include_supersedes=False`` reproduces the on-disk id byte-identically;
# ``include_supersedes=True`` produces the alternate UUID5
# ``6366af60-acb7-5e3f-a2e5-89b47f42c82f`` as the material
# behavior-change evidence.
#
# The existing ``canonical_json`` helper is preserved verbatim to avoid
# perturbing ``content_hash_tiebreak`` semantics inside
# ``concat_clone_ledgers`` (canonical_json includes ``supersedes`` today;
# c48 fix scope is limited to the UUID5 event_id derivation path).
#
# ``supersedes`` was already recognized as a first-class optional field by
# ``validate_event`` (see ``_OPTIONAL_WELL_KNOWN``); this comment upgrade
# formalizes its first-class status in the content-hash contract.

def canonical_json_bytes(event: "dict", include_supersedes: bool = False) -> bytes:
    """Canonical-JSON bytes for UUID5 content-hash derivation, with an
    explicit ``supersedes`` inclusion toggle.

    When ``include_supersedes`` is False (default), the returned bytes
    exclude ``event_id``, ``ts``, AND ``supersedes``. This reproduces the
    on-disk c46 line-745 ``event_id``.
    When ``include_supersedes`` is True, only ``event_id`` and ``ts`` are
    excluded; the ``supersedes`` field participates in the content hash.
    """
    if include_supersedes:
        exclude = ("event_id", "ts")
    else:
        exclude = ("event_id", "ts", "supersedes")
    core = {k: v for k, v in (event or {}).items() if k not in exclude}
    return json.dumps(
        core, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def content_hash_event_id_v2(event: "dict", include_supersedes: bool = False) -> str:
    """UUID5 ``event_id`` derivation with explicit ``supersedes`` toggle.

    Preserves the ``_EVENT_ID_NAMESPACE`` and UUID5 format of
    ``content_hash_event_id`` so all downstream promise_check UUID
    invariants continue to hold.
    """
    payload = canonical_json_bytes(event, include_supersedes=include_supersedes).decode("utf-8")
    return str(uuid.uuid5(_EVENT_ID_NAMESPACE, payload))
'''

body = TARGET.read_text()
if MARKER in body:
    print(f"already patched — skipping ({TARGET})")
else:
    TARGET.write_text(body.rstrip() + "\n" + APPEND_BLOCK)
    print(f"patched {TARGET}")
    print(f"  new size: {TARGET.stat().st_size} bytes")

# Verify import
import sys
sys.path.insert(0, '/home/user/human-in-a-loop/long-exposure')
# Force fresh import
import importlib, long_exposure.tools._ledger_schema
importlib.reload(long_exposure.tools._ledger_schema)
from long_exposure.tools._ledger_schema import (
    canonical_json_bytes, content_hash_event_id_v2, content_hash_event_id, validate_event,
)
# Sanity-check on line 745
import json
lines = pathlib.Path('/home/user/long-exposure-runs/music-gen/promise_ledger.jsonl').read_text().splitlines()
r = json.loads(lines[744])
print(f"line-745 OFF (supersedes NOT in hash): {content_hash_event_id_v2(r, include_supersedes=False)}")
print(f"line-745  ON (supersedes  IN  hash): {content_hash_event_id_v2(r, include_supersedes=True)}")
assert content_hash_event_id_v2(r, include_supersedes=False) == "658231db-5d86-56e5-8ca9-2a9bed7fdf9f"
assert content_hash_event_id_v2(r, include_supersedes=True)  == "6366af60-acb7-5e3f-a2e5-89b47f42c82f"
# validate_event still accepts supersedes
errs = validate_event(r)
assert errs == [], errs
print("post-patch sanity checks PASS")
