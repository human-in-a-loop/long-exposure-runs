#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T23:30:00Z
# cycle: 25
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork dc8cba4b79eb)
# milestone: M-GEN-1/batch-v6-unconditioned-n16
# ---
"""Anchor-preservation gate for batch-v6.

Computes per-file SHA-256 for every file under each frozen batch directory
plus the two ledger files, produces an aggregate SHA per anchor (SHA-256
of the JSON-serialized sorted (relpath, sha256) list, first 16 hex), and
compares to a saved pre-run manifest. Any drift is a hard-stop.

Also verifies that no in-branch script imports
``scripts.rules.sampling.i4_stratified`` via a simple text scan.

Reads:
    data/gen/batch_v6/pre_run_anchor_manifest.json   (required)
Writes:
    data/gen/batch_v6/post_run_anchor_manifest.json
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

os.environ.setdefault("PYTHONHASHSEED", "0")
assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent

ANCHOR_DIRS = ("batch_v2", "batch_v3_i3", "batch_v3_i4", "batch_v4", "batch_v5_n16")
ANCHOR_LEDGERS = ("data/rules/ledger.jsonl", "data/rules/ledger_i3_dminor.jsonl")

BATCH_V6_SCRIPTS = (
    "scripts/gen/batch_v6_unconditioned_n16.py",
    "scripts/gen/collision_count_batch_v6.py",
    "scripts/gen/batch_v6_hypothesis_verdict.py",
    "scripts/gen/batch_v6_anchor_check.py",
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _list_dir(root: Path) -> List[Tuple[str, str]]:
    if not root.exists():
        return []
    lst = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            lst.append((str(p.relative_to(root)), _sha256(p)))
    return lst


def _agg(files: List[Tuple[str, str]]) -> str:
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:16]


def compute_anchor_manifest() -> Dict:
    out = {"per_batch": {}, "per_ledger": {}, "aggregation_method":
           "sha256_hex_first16(json.dumps(sorted[[relpath, sha256]]))"}
    for name in ANCHOR_DIRS:
        files = _list_dir(_REPO / "data" / "gen" / name)
        out["per_batch"][name] = {
            "agg16": _agg(files),
            "n_files": len(files),
            "per_file_sha": {rp: s for rp, s in files},
        }
    for rel in ANCHOR_LEDGERS:
        p = _REPO / rel
        out["per_ledger"][rel] = _sha256(p) if p.exists() else None
    return out


def _grep_i4_imports() -> Dict[str, List[str]]:
    """Detect actual `^\\s*(import|from) ... i4_stratified` lines.

    Docstring / comment mentions of the name are permitted (they document
    the exclusion).
    """
    hits: Dict[str, List[str]] = {}
    pat = re.compile(r"^\s*(import|from)\s+.*\bi4_stratified\b")
    for rel in BATCH_V6_SCRIPTS:
        p = _REPO / rel
        if not p.exists():
            continue
        found = []
        for i, line in enumerate(p.read_text().splitlines(), 1):
            if pat.match(line):
                found.append(f"{i}:{line.strip()}")
        if found:
            hits[rel] = found
    return hits


def verify(pre_run_manifest_path: Path,
           post_run_out_path: Path) -> Dict:
    pre = json.loads(pre_run_manifest_path.read_text())
    post = compute_anchor_manifest()
    per_anchor: Dict[str, Dict] = {}
    all_pass = True

    for name in ANCHOR_DIRS:
        pre_e = pre["per_batch"].get(name, {})
        post_e = post["per_batch"][name]
        drifted_files = []
        for rp, sha in post_e["per_file_sha"].items():
            if pre_e.get("per_file_sha", {}).get(rp) != sha:
                drifted_files.append(rp)
        for rp in pre_e.get("per_file_sha", {}):
            if rp not in post_e["per_file_sha"]:
                drifted_files.append(rp + " [MISSING]")
        agg_match = pre_e.get("agg16") == post_e["agg16"]
        n_match = pre_e.get("n_files") == post_e["n_files"]
        anchor_pass = agg_match and n_match and not drifted_files
        per_anchor[name] = {
            "pass": anchor_pass,
            "pre_agg16": pre_e.get("agg16"),
            "post_agg16": post_e["agg16"],
            "pre_n_files": pre_e.get("n_files"),
            "post_n_files": post_e["n_files"],
            "drifted_files": drifted_files,
        }
        if not anchor_pass:
            all_pass = False

    for rel in ANCHOR_LEDGERS:
        pre_sha = pre["per_ledger"].get(rel)
        post_sha = post["per_ledger"][rel]
        ok = pre_sha == post_sha and pre_sha is not None
        per_anchor[rel] = {
            "pass": ok,
            "pre_sha256": pre_sha,
            "post_sha256": post_sha,
        }
        if not ok:
            all_pass = False

    i4_hits = _grep_i4_imports()
    per_anchor["i4_stratified_not_imported"] = {
        "pass": len(i4_hits) == 0,
        "hits": i4_hits,
    }
    if i4_hits:
        all_pass = False

    report = {
        "all_pass": all_pass,
        "per_anchor": per_anchor,
        "aggregation_method": post["aggregation_method"],
    }
    post_run_out_path.write_text(json.dumps(report, indent=2, sort_keys=True))
    return report


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path,
                    default=_REPO / "data" / "gen" / "batch_v6")
    ap.add_argument("--mode", choices=("compute", "verify"), default="verify")
    args = ap.parse_args(argv)

    if args.mode == "compute":
        m = compute_anchor_manifest()
        args.batch_root.mkdir(parents=True, exist_ok=True)
        (args.batch_root / "pre_run_anchor_manifest.json").write_text(
            json.dumps(m, indent=2, sort_keys=True))
        print(f"[batch_v6_anchor_check] wrote pre_run_anchor_manifest.json")
        for name in ANCHOR_DIRS:
            print(f"  {name}: agg={m['per_batch'][name]['agg16']} "
                  f"files={m['per_batch'][name]['n_files']}")
        for rel in ANCHOR_LEDGERS:
            print(f"  {rel}: {m['per_ledger'][rel]}")
        return 0

    pre_path = args.batch_root / "pre_run_anchor_manifest.json"
    if not pre_path.exists():
        print(f"[batch_v6_anchor_check] ERROR: {pre_path} missing", file=sys.stderr)
        return 2
    report = verify(pre_path, args.batch_root / "post_run_anchor_manifest.json")
    for name, info in report["per_anchor"].items():
        status = "PASS" if info["pass"] else "FAIL"
        print(f"[batch_v6_anchor_check] {status:4s}  {name}")
    print(f"[batch_v6_anchor_check] all_pass={report['all_pass']}")
    return 0 if report["all_pass"] else 3


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
