#!/usr/bin/env python3
"""Pre/post canonical-aggregate-SHA anchor preservation check.

Anchors (8):
  data/gen/batch_v2/          (dir)
  data/gen/batch_v3_i3/       (dir)
  data/gen/batch_v3_i4/       (dir)
  data/gen/batch_v4/          (dir)
  data/gen/batch_v5_n16/      (dir)
  data/gen/batch_v6/          (dir)
  data/rules/ledger.jsonl     (file)
  data/rules/ledger_i3_dminor.jsonl (file)

Usage:
  # Pre-run baseline (freezes truth):
  python3 scripts/analysis/anchor_preservation_bp.py capture data/collision_model/pre_run_anchor_manifest.json

  # Post-run check:
  python3 scripts/analysis/anchor_preservation_bp.py verify data/collision_model/pre_run_anchor_manifest.json data/collision_model/post_run_anchor_manifest.json

Interpreter-guarded /usr/bin/python3.  No PRNG.  No sidecar_nonfactor.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"anchor_preservation_bp requires /usr/bin/python3, got {sys.executable}"
)

# Add scripts/analysis to path for direct-script invocation
_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from canonical_aggregate_sha import canonical_aggregate_sha, file_sha256  # noqa: E402


ANCHOR_DIRS = [
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
    """Return a manifest dict of aggregate SHAs for all 8 anchors."""
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
    """Diff pre vs post; return {overall_pass, per_anchor: [{rel, status, ...}]}."""
    results = []
    ok = True
    for rel in ANCHOR_DIRS + ANCHOR_FILES:
        p = pre["anchors"].get(rel, {})
        q = post["anchors"].get(rel, {})
        p_sha = p.get("sha")
        q_sha = q.get("sha")
        match = (p_sha is not None) and (p_sha == q_sha)
        if not match:
            ok = False
        results.append(
            {
                "anchor": rel,
                "kind": p.get("kind"),
                "pre_sha": p_sha,
                "post_sha": q_sha,
                "status": "PASS" if match else "FAIL",
            }
        )
    return {"overall_pass": ok, "results": results, "count_pass": sum(1 for r in results if r["status"] == "PASS"), "count_total": len(results)}


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
            "  anchor_preservation_bp.py capture <out_manifest.json>\n"
            "  anchor_preservation_bp.py verify <pre_manifest.json> <out_post_manifest.json>",
            file=sys.stderr,
        )
        sys.exit(2)
    mode = sys.argv[1]
    if mode == "capture":
        if len(sys.argv) != 3:
            print("capture: needs out path", file=sys.stderr)
            sys.exit(2)
        m = capture(workspace)
        _write_json(pathlib.Path(sys.argv[2]), m)
        print(f"captured {sum(1 for a in m['anchors'].values() if a.get('sha'))} / {len(m['anchors'])} anchors")
    elif mode == "verify":
        if len(sys.argv) != 4:
            print("verify: needs pre and post out paths", file=sys.stderr)
            sys.exit(2)
        pre = _load_json(pathlib.Path(sys.argv[2]))
        post = capture(workspace)
        _write_json(pathlib.Path(sys.argv[3]), post)
        report = verify(pre, post)
        print(
            f"anchor preservation: {report['count_pass']} / {report['count_total']} PASS  overall={'PASS' if report['overall_pass'] else 'FAIL'}"
        )
        if not report["overall_pass"]:
            sys.exit(1)
    else:
        print(f"unknown mode: {mode}", file=sys.stderr)
        sys.exit(2)
