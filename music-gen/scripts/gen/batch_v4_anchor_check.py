#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T17:15:00Z
# cycle: 16
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork cc548ca0c2e5)
# milestone: M-GEN-1/batch-v4-compound
# ---
"""Standalone re-materializer for the anchor cross-reference table.

Reads batch-v4's ``batch_manifest.json`` and the two reference batch
manifests (batch_v3_i4 and batch_v3_i3), then re-derives
``anchor_cross_reference.json`` and prints a summary. Useful for
auditors: verdict CONFIRMS_H0_STRICT relies on this file's contents.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.gen.batch_v4_compound import _anchor_cross_reference  # noqa: E402


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path,
                    default=_REPO / "data" / "gen" / "batch_v4")
    args = ap.parse_args(argv)
    xref = _anchor_cross_reference(args.batch_root)
    (args.batch_root / "anchor_cross_reference.json").write_text(
        json.dumps(xref, indent=2, sort_keys=True))
    print(f"[batch_v4_anchor_check] counts = {json.dumps(xref['counts'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
