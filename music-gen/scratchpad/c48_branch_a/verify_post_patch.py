#!/usr/bin/env python3
"""Post-patch invariant verification."""
import inspect
import json
import os
import pathlib
import sys

sys.path.insert(0, '/home/user/human-in-a-loop/long-exposure')
import long_exposure.workspace_bootstrap as wb

sig = inspect.signature(wb.append_ledger_event)
params = list(sig.parameters.keys())
print("params:", params)
assert params == ["workspace", "event"], params

from long_exposure.tools._ledger_schema import LedgerSchemaError
assert issubclass(wb.LedgerNamespaceViolation, LedgerSchemaError)
assert issubclass(wb.LedgerNamespaceViolation, ValueError)
mro = [c.__name__ for c in wb.LedgerNamespaceViolation.__mro__]
print("MRO:", mro)

# Verify _should_suffix contract
os.environ.pop("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", None)
assert wb._should_suffix("M-EAR-1/x") is True
assert wb._should_suffix("_infra/x") is True
os.environ["MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION"] = "1"
assert wb._should_suffix("M-EAR-1/x") is False
assert wb._should_suffix("_infra/x") is True
assert wb._should_suffix("_manager/M-EAR-1/x") is True
os.environ.pop("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", None)

# Sub-fix 2 via content_hash_event_id_v2
from long_exposure.tools._ledger_schema import content_hash_event_id_v2
lines = pathlib.Path("/home/user/long-exposure-runs/music-gen/promise_ledger.jsonl").read_text().splitlines()
r = json.loads(lines[744])
assert content_hash_event_id_v2(r, include_supersedes=False) == "658231db-5d86-56e5-8ca9-2a9bed7fdf9f"
assert content_hash_event_id_v2(r, include_supersedes=True) == "6366af60-acb7-5e3f-a2e5-89b47f42c82f"
print("OK — sub-fixes 1+2 land; API/MRO invariants unchanged")
