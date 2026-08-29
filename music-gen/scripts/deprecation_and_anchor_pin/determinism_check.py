#!/usr/bin/env /usr/bin/python3
"""Cycle 47 Branch C: byte-determinism × 2 on the extended anchor manifest.

Reconstructs a pre-append copy of `data/anchor_manifest_v1.json` (by
dropping the c47-pinned `env/SOURCE_DATE_EPOCH` entry, decrementing
`anchor_count`), writes it to a fresh `tempfile.mkdtemp()`, re-runs the
pin, then asserts the resulting file's SHA-256 byte-equals the on-disk
post-append manifest.

Runs under BLAS pins + PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH=1756463424
(dogfoods the pinned anchor) + TZ=UTC + LC_ALL=C.UTF-8.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile

if not sys.executable.startswith("/usr/bin/python"):
    print(f"[det] REFUSE: interpreter {sys.executable!r} is not /usr/bin/python3",
          file=sys.stderr)
    sys.exit(2)

WS = "/home/user/long-exposure-runs/music-gen"
if WS not in sys.path:
    sys.path.insert(0, WS)

from scripts.deprecation_and_anchor_pin.pin_source_date_epoch import (  # noqa: E402
    ANCHOR_ID,
    pin,
)

MANIFEST = os.path.join(WS, "data/anchor_manifest_v1.json")
OUT = os.path.join(WS, "data/deprecation_and_anchor_pin/determinism_check.json")


def sha256_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main() -> int:
    with open(MANIFEST) as f:
        m_current = json.load(f)

    post_sha_on_disk = sha256_file(MANIFEST)

    # Reconstruct pre-append manifest by dropping the c47-pinned entry.
    m_pre = json.loads(json.dumps(m_current))  # deep copy
    m_pre["anchors"] = [a for a in m_pre["anchors"] if a.get("anchor_id") != ANCHOR_ID]
    m_pre["anchor_count"] = len(m_pre["anchors"])

    # Fresh temp dir; write the reconstructed pre-append manifest.
    tmpdir = tempfile.mkdtemp(prefix="c47_det_")
    tmp_manifest = os.path.join(tmpdir, "anchor_manifest_v1.json")
    with open(tmp_manifest, "w") as f:
        json.dump(m_pre, f, indent=2, sort_keys=True)
        f.write("\n")

    # Re-run the pin against the fresh copy.
    _m_post, _pre_sha, tmp_post_sha, _entry = pin(tmp_manifest)

    equal = (tmp_post_sha == post_sha_on_disk)

    result = {
        "cycle": 47,
        "branch": "C",
        "clone": 2,
        "on_disk_post_sha": post_sha_on_disk,
        "tmpdir_post_sha": tmp_post_sha,
        "byte_deterministic_x2": equal,
        "tmpdir": tmpdir,
        "n_anchors_pre_reconstructed": len(m_pre["anchors"]),
        "n_anchors_post": _m_post["anchor_count"],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")

    # Best-effort cleanup.
    try:
        shutil.rmtree(tmpdir)
    except OSError:
        pass

    print(f"[det] on_disk_post_sha={post_sha_on_disk}")
    print(f"[det] tmpdir_post_sha ={tmp_post_sha}")
    print(f"[det] byte_deterministic_x2={equal}")
    print(f"[det] wrote {OUT}")
    return 0 if equal else 1


if __name__ == "__main__":
    raise SystemExit(main())
