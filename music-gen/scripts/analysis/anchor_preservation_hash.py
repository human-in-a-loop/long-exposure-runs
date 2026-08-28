#!/usr/bin/env python3
# ---
# created: 2026-08-28T23:00:00Z
# cycle: 28
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-hash-space-geometry
# ---
"""Pre/post canonical-aggregate-SHA anchor preservation for cycle-28.

Anchors (9):
  data/gen/batch_v1/          (dir)
  data/gen/batch_v2/          (dir)
  data/gen/batch_v3_i3/       (dir)
  data/gen/batch_v3_i4/       (dir)
  data/gen/batch_v4/          (dir)
  data/gen/batch_v5_n16/      (dir)
  data/gen/batch_v6/          (dir)
  data/rules/ledger.jsonl     (file)
  data/rules/ledger_i3_dminor.jsonl (file)

Uses cycle-26's canonical_aggregate_sha.py verbatim (do not modify).

Interpreter-guarded /usr/bin/python3.  No PRNG.  No sidecar_nonfactor.
Does not import i4_stratified.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"anchor_preservation_hash requires /usr/bin/python3, got {sys.executable}"
)

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from canonical_aggregate_sha import canonical_aggregate_sha, file_sha256  # noqa: E402


ANCHOR_DIRS = [
    "data/gen/batch_v1",
    "data/gen/batch_v2",
    "data/gen/batch_v3_i3",
    "data/gen/batch_v3_i4",
    "data/gen/batch_v4",
    "data/gen/batch_v5_n16",
    "data/gen/batch_v6",
]
ANCHOR_FILES = [
    "data/rules/ledger.jsonl",
    "data/rules/ledger_i3_dminor.jsonl",
]


def capture(workspace: pathlib.Path) -> dict:
    workspace = workspace.resolve()
    out = {"schema_v": 1, "method": "canonical_aggregate_sha_v1", "anchors": {}}
    for rel in ANCHOR_DIRS:
        p = workspace / rel
        if p.exists():
            out["anchors"][rel] = {"kind": "dir", "sha": canonical_aggregate_sha(p)}
        else:
            out["anchors"][rel] = {"kind": "dir", "sha": None, "note": "missing"}
    for rel in ANCHOR_FILES:
        p = workspace / rel
        if p.exists():
            out["anchors"][rel] = {"kind": "file", "sha": file_sha256(p)}
        else:
            out["anchors"][rel] = {"kind": "file", "sha": None, "note": "missing"}
    return out


def verify(pre: dict, post: dict) -> dict:
    results = []
    ok = True
    for rel in ANCHOR_DIRS + ANCHOR_FILES:
        p_sha = pre["anchors"].get(rel, {}).get("sha")
        q_sha = post["anchors"].get(rel, {}).get("sha")
        match = (p_sha is not None) and (p_sha == q_sha)
        if not match:
            ok = False
        results.append(
            {
                "anchor": rel,
                "kind": pre["anchors"].get(rel, {}).get("kind"),
                "pre_sha": p_sha,
                "post_sha": q_sha,
                "status": "PASS" if match else "FAIL",
            }
        )
    return {
        "overall_pass": ok,
        "results": results,
        "count_pass": sum(1 for r in results if r["status"] == "PASS"),
        "count_total": len(results),
    }


def _write_json(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
        fh.write("\n")


def _load_json(path: pathlib.Path) -> dict:
    with path.open("r") as fh:
        return json.load(fh)


if __name__ == "__main__":  # pragma: no cover
    workspace = pathlib.Path.cwd()
    if len(sys.argv) < 2:
        print(
            "usage:\n"
            "  anchor_preservation_hash.py capture <out_manifest.json>\n"
            "  anchor_preservation_hash.py verify <pre_manifest.json> <out_post_manifest.json>",
            file=sys.stderr,
        )
        sys.exit(2)
    mode = sys.argv[1]
    if mode == "capture":
        m = capture(workspace)
        _write_json(pathlib.Path(sys.argv[2]), m)
        print(
            f"captured {sum(1 for a in m['anchors'].values() if a.get('sha'))} / {len(m['anchors'])} anchors"
        )
    elif mode == "verify":
        if len(sys.argv) != 4:
            print("verify: needs pre and post out paths", file=sys.stderr)
            sys.exit(2)
        pre = _load_json(pathlib.Path(sys.argv[2]))
        post = capture(workspace)
        report = verify(pre, post)
        _write_json(pathlib.Path(sys.argv[3]), post)
        outp = pathlib.Path("data/collision_model/anchor_preservation_hash.json")
        _write_json(outp, report)
        print(
            f"anchor preservation: {report['count_pass']} / {report['count_total']} PASS  "
            f"overall={'PASS' if report['overall_pass'] else 'FAIL'}"
        )
        if not report["overall_pass"]:
            sys.exit(1)
    else:
        print(f"unknown mode: {mode}", file=sys.stderr)
        sys.exit(2)
