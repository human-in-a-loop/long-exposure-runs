#!/usr/bin/env /usr/bin/python3
"""Cycle 47 Branch C: pin SOURCE_DATE_EPOCH=1756463424 as anchor #19.

Extends `_infra/anchor-manifest-v1` (c35 chain). Append-only per the c35
anchor-manifest contract: read entire JSON, append to `anchors` list,
increment `anchor_count`, write back atomically via temp + os.replace.

Canonical-JSON via `json.dumps(sort_keys=True, separators=(",", ":"))`.
No PRNG. SHA-256 for content hashing. Interpreter-guarded /usr/bin/python3.

CLI:
    pin_source_date_epoch.py [--manifest PATH] [--out PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile

WS = "/home/user/long-exposure-runs/music-gen"
DEFAULT_MANIFEST = os.path.join(WS, "data/anchor_manifest_v1.json")
DEFAULT_OUT = os.path.join(WS, "data/deprecation_and_anchor_pin/source_date_epoch_pin.json")
SOURCE_DATE_EPOCH_VALUE = 1756463424
ANCHOR_ID = "env/SOURCE_DATE_EPOCH"

if not sys.executable.startswith("/usr/bin/python"):
    print(f"[pin_sde] REFUSE: interpreter {sys.executable!r} is not /usr/bin/python3",
          file=sys.stderr)
    sys.exit(2)


def _canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def make_entry(value: int) -> dict:
    """Build the canonical anchor entry for SOURCE_DATE_EPOCH."""
    value_sha256 = sha256_str(str(value))
    core = {"key": ANCHOR_ID, "value": value, "value_sha256": value_sha256}
    entry_sha256 = sha256_str(_canonical_json(core))
    return {
        "anchor_id": ANCHOR_ID,
        "kind": "env_pin",
        "cycle": 47,
        "key": ANCHOR_ID,
        "value": value,
        "value_sha256": value_sha256,
        "entry_sha256": entry_sha256,
        "pinned_cycle": 47,
        "pinned_by": "clone-2",
    }


def atomic_write_json(path: str, obj) -> None:
    """Atomic write via temp file + os.replace. Preserves parent dir."""
    parent = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix=".pin_sde_", dir=parent)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(obj, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def pin(manifest_path: str) -> tuple[dict, str, str, dict]:
    """Append SOURCE_DATE_EPOCH entry to the manifest.

    Returns (manifest_dict_post, pre_sha, post_sha, entry).
    """
    with open(manifest_path) as f:
        m = json.load(f)

    pre_sha = sha256_file(manifest_path)
    pre_count = m["anchor_count"]
    pre_len = len(m["anchors"])
    assert pre_count == pre_len, (
        f"invariant: anchor_count={pre_count} != len(anchors)={pre_len}"
    )

    # Guard: refuse duplicate append.
    for a in m["anchors"]:
        if a.get("anchor_id") == ANCHOR_ID:
            print(f"[pin_sde] already pinned; anchor_id={ANCHOR_ID}; no-op",
                  file=sys.stderr)
            return m, pre_sha, pre_sha, a

    entry = make_entry(SOURCE_DATE_EPOCH_VALUE)
    m["anchors"].append(entry)
    m["anchor_count"] = pre_count + 1

    atomic_write_json(manifest_path, m)
    post_sha = sha256_file(manifest_path)

    return m, pre_sha, post_sha, entry


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=DEFAULT_MANIFEST)
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    print(f"[pin_sde] c47 Branch C — pinning {ANCHOR_ID}={SOURCE_DATE_EPOCH_VALUE}")
    print(f"[pin_sde] manifest={args.manifest}")

    m_post, pre_sha, post_sha, entry = pin(args.manifest)

    result = {
        "cycle": 47,
        "branch": "C",
        "clone": 2,
        "manifest_path": os.path.relpath(args.manifest, WS)
        if args.manifest.startswith(WS) else args.manifest,
        "manifest_pre_sha256": pre_sha,
        "manifest_post_sha256": post_sha,
        "anchor_count_pre": m_post["anchor_count"] - 1,
        "anchor_count_post": m_post["anchor_count"],
        "entry": entry,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    atomic_write_json(args.out, result)

    print(f"[pin_sde] pre_sha ={pre_sha}")
    print(f"[pin_sde] post_sha={post_sha}")
    print(f"[pin_sde] value_sha256={entry['value_sha256']}")
    print(f"[pin_sde] entry_sha256={entry['entry_sha256']}")
    print(f"[pin_sde] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
