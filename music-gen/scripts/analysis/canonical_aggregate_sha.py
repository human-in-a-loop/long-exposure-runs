#!/usr/bin/env python3
"""Canonical aggregate SHA-256 for a directory tree.

Closes cycle-25 handoff item on aggregation-method drift.
Locked definition (do not change without a new milestone):

  1. Walk the target directory recursively, collecting all REGULAR files
     (skip symlinks, sockets, devices).
  2. For each file, compute sha256_hex = SHA-256(file_bytes).
  3. Convert path to POSIX-relative-to-root, UTF-8.
  4. Sort (relpath, sha256_hex) pairs by relpath (byte-lex).
  5. Serialize each pair as f"{relpath}\\t{sha256_hex}\\n".
  6. Concatenate all pairs -> canonical_aggregation_input (bytes).
  7. aggregate_sha = SHA-256(canonical_aggregation_input), full 64-char hex.

Used by anchor_preservation_bp.py and by any future cycle needing to
prove a directory's byte-invariance.

Interpreter-guarded /usr/bin/python3.  No PRNG.  No sidecar_nonfactor.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"canonical_aggregate_sha requires /usr/bin/python3, got {sys.executable}"
)


def _iter_regular_files(root: pathlib.Path):
    """Yield (relpath_posix, absolute_path) for every regular file under root.

    Skips symlinks, sockets, devices, directories.  Deterministic order does
    not matter here — caller sorts by relpath.
    """
    root = root.resolve()
    for path in root.rglob("*"):
        try:
            if path.is_symlink():
                continue
            if not path.is_file():
                continue
        except OSError:
            continue
        rel = path.relative_to(root).as_posix()
        yield rel, path


def _file_sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_manifest(root: pathlib.Path) -> dict:
    """Return {aggregate_sha, file_count, entries: [(relpath, sha256_hex), ...]}.

    entries is sorted by relpath ascending, byte-lex on the UTF-8 encoding of
    relpath (matches Python's default string ordering for pure-ASCII paths;
    for non-ASCII paths the ordering is on the UTF-8-encoded bytes via
    sort key).
    """
    root = pathlib.Path(root)
    if not root.exists():
        raise FileNotFoundError(f"canonical_aggregate_sha: root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"canonical_aggregate_sha: root is not a directory: {root}")

    pairs: list[tuple[str, str]] = []
    for rel, abs_path in _iter_regular_files(root):
        pairs.append((rel, _file_sha256(abs_path)))
    # Byte-lex on UTF-8 encoded relpath
    pairs.sort(key=lambda p: p[0].encode("utf-8"))

    lines = "".join(f"{rel}\t{sha}\n" for rel, sha in pairs).encode("utf-8")
    aggregate = hashlib.sha256(lines).hexdigest()

    return {
        "aggregate_sha": aggregate,
        "file_count": len(pairs),
        "entries": pairs,
    }


def canonical_aggregate_sha(root: pathlib.Path) -> str:
    """Return the 64-char hex canonical aggregate SHA for a directory tree."""
    return compute_manifest(root)["aggregate_sha"]


def file_sha256(path: pathlib.Path) -> str:
    """Public helper for callers who need per-file SHA-256 with the same
    chunking as compute_manifest (for the two rules ledgers)."""
    return _file_sha256(pathlib.Path(path))


if __name__ == "__main__":  # pragma: no cover
    if len(sys.argv) != 2:
        print("usage: canonical_aggregate_sha.py <path>", file=sys.stderr)
        sys.exit(2)
    target = pathlib.Path(sys.argv[1])
    if target.is_file():
        print(file_sha256(target))
    else:
        manifest = compute_manifest(target)
        print(f"{manifest['aggregate_sha']}  files={manifest['file_count']}  {target}")
