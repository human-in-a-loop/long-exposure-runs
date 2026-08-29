#!/usr/bin/env python3
# scripts/anchor_manifest/compute_sha_manifest.py — Cycle 35 clone-2.
# Per-file SHA-256 + per-directory sorted-relpath concat manifest SHA.
# Read-only. Symlinks not followed. __pycache__/ and *.pyc excluded.
# created: 2026-08-29
# cycle: 35
# agent: worker
# milestone: _infra/anchor-manifest-v1-clone-2
import hashlib
import os
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_dir(root: Path):
    """Yield (posix_relpath, absolute_path) for files under root, filtered
    and sorted stably. Excludes __pycache__/ dirs and *.pyc files.
    Does not follow symlinks."""
    root = Path(root)
    files = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        # in-place prune of pycache
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            if fn.endswith(".pyc"):
                continue
            abs_p = Path(dirpath) / fn
            if abs_p.is_symlink():
                continue
            rel = abs_p.relative_to(root).as_posix()
            files.append((rel, abs_p))
    files.sort(key=lambda t: t[0])
    return files


def compute_path_sha(path_str: str) -> dict:
    """Return {'kind': 'file'|'dir'|'missing', 'sha_per_path': {...},
    'dir_manifest_sha': str|None, 'entry_count': int}."""
    p = Path(path_str)
    out = {"kind": "missing", "sha_per_path": {}, "dir_manifest_sha": None, "entry_count": 0}
    if not p.exists():
        return out
    if p.is_file():
        out["kind"] = "file"
        out["sha_per_path"] = {path_str: _sha256_file(p)}
        out["entry_count"] = 1
        return out
    if p.is_dir():
        out["kind"] = "dir"
        entries = _iter_dir(p)
        sha_map = {}
        parts = []
        for rel, abs_p in entries:
            sha = _sha256_file(abs_p)
            sha_map[f"{path_str}/{rel}"] = sha
            parts.append(f"{rel}\t{sha}\n")
        dir_manifest = hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()
        out["sha_per_path"] = sha_map
        out["dir_manifest_sha"] = dir_manifest
        out["entry_count"] = len(entries)
        return out
    return out


def compute_anchor(anchor: dict) -> dict:
    """Extend an enumerate_anchors row with SHA fields."""
    entries = {}
    dir_shas = {}
    total_files = 0
    for path_str in anchor["paths"]:
        r = compute_path_sha(path_str)
        entries[path_str] = {
            "kind": r["kind"],
            "sha_per_path": r["sha_per_path"],
            "dir_manifest_sha": r["dir_manifest_sha"],
            "entry_count": r["entry_count"],
        }
        if r["dir_manifest_sha"]:
            dir_shas[path_str] = r["dir_manifest_sha"]
        total_files += r["entry_count"]
    out = dict(anchor)
    out["path_entries"] = entries
    # Aggregate sha_per_path across all listed paths (path -> sha).
    agg = {}
    for path_str, r in entries.items():
        agg.update(r["sha_per_path"])
    out["sha_per_path"] = agg
    out["dir_manifest_sha_per_dir"] = dir_shas
    out["file_count"] = total_files
    out["is_readonly"] = True
    return out


if __name__ == "__main__":
    import json
    from scripts.anchor_manifest.enumerate_anchors import enumerate_anchors
    for a in enumerate_anchors():
        r = compute_anchor(a)
        print(json.dumps({
            "anchor_id": r["anchor_id"],
            "file_count": r["file_count"],
            "dir_manifest_sha_per_dir": r["dir_manifest_sha_per_dir"],
        }, indent=2))
