#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T22:00:00Z
# cycle: 23
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 3fbd8c1ab57c)
# milestone: M-GEN-1/batch-v5-n16
# ---
"""Anchor regression: batch-v5 salts 0..7 must reproduce batch-v4's 32 SHAs.

batch-v5 is a pure salt-range extension of batch-v4 (identical source
ledger, identical I4 sampler, identical render pipeline). Because the
I4 sampler's already_picked state is deterministic and monotonic in
salt order, driving 0..15 must reproduce the 0..7 picks exactly. This
harness proves the byte-level extension at the render layer for all
32 (salt, file_kind) cells.

Emits:
    data/gen/batch_v5_n16/anchor_regression.json
Exits non-zero on ANY cell mismatch (branch cannot ship a verdict
without a clean anchor regression).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict

os.environ.setdefault("PYTHONHASHSEED", "0")
assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
V5_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v5_n16"
V4_MANIFEST = _REPO / "data" / "gen" / "batch_v4" / "batch_manifest.json"

FILE_KINDS = ("musicxml", "midi", "bare_wav", "effects_wav")
ANCHOR_SALTS = tuple(range(8))


def _load_v4_shas() -> Dict[int, Dict[str, str]]:
    m = json.loads(V4_MANIFEST.read_text())
    out: Dict[int, Dict[str, str]] = {}
    for row in m["per_song"]:
        s = int(row["salt"])
        out[s] = {fk: row["sha"][fk] for fk in FILE_KINDS}
    return out


def _load_v5_shas(batch_root: Path) -> Dict[int, Dict[str, str]]:
    m = json.loads((batch_root / "batch_manifest.json").read_text())
    out: Dict[int, Dict[str, str]] = {}
    for row in m["per_song"]:
        s = int(row["salt"])
        if s in ANCHOR_SALTS:
            out[s] = {fk: row["sha"][fk] for fk in FILE_KINDS}
    return out


def check(batch_root: Path = V5_BATCH_ROOT) -> Dict:
    v4 = _load_v4_shas()
    v5 = _load_v5_shas(batch_root)

    rows = []
    n_pass = 0
    n_fail = 0
    for s in ANCHOR_SALTS:
        for fk in FILE_KINDS:
            a = v4[s][fk]
            b = v5[s][fk]
            ok = (a == b)
            n_pass += ok
            n_fail += (not ok)
            rows.append({
                "salt": s,
                "file_kind": fk,
                "batch_v4_sha256": a,
                "batch_v5_sha256": b,
                "verdict": "PASS" if ok else "FAIL",
            })

    result = {
        "n_cells": len(rows),
        "n_pass": n_pass,
        "n_fail": n_fail,
        "all_pass": n_fail == 0,
        "rows": rows,
    }
    (batch_root / "anchor_regression.json").write_text(
        json.dumps(result, indent=2, sort_keys=True))
    return result


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path, default=V5_BATCH_ROOT)
    args = ap.parse_args(argv)
    r = check(args.batch_root)
    print(f"[batch_v5_anchor_regression] {r['n_pass']}/{r['n_cells']} PASS "
          f"({r['n_fail']} FAIL)")
    if not r["all_pass"]:
        for row in r["rows"]:
            if row["verdict"] == "FAIL":
                print(f"  FAIL salt={row['salt']} kind={row['file_kind']}")
                print(f"      v4={row['batch_v4_sha256'][:16]}")
                print(f"      v5={row['batch_v5_sha256'][:16]}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
