"""Emit data/ear_v0/anchor_preservation.json.

Enumerates + SHA-256s the c6/c22/c26 anchor set (scripts/ear/*, the
c6 feature-cache dir, the c26 Path B commitment doc) and compares
against the c35 _infra/anchor-manifest-v1 baseline SHA. Emits
{path: {sha, mtime}} per entry + a boolean `unchanged` computed
against the c35 pinned manifest SHA
`6dc917fe365a37ff87c3d72f45b3d433894221f8ebdbb36ed3beb5d44a7a821f`.

Read-only walk. Byte-deterministic on repeated invocation on the same
tree. Runs on the post-training pass (not this cycle).
"""
# created: 2026-08-29T06:00:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: _infra/anchor-preservation-snapshot-script-clone-0
from __future__ import annotations
import sys
assert sys.executable == "/usr/bin/python3", sys.executable
import hashlib, json, os
from pathlib import Path

C35_MANIFEST_SHA = "6dc917fe365a37ff87c3d72f45b3d433894221f8ebdbb36ed3beb5d44a7a821f"

ANCHOR_GROUPS = {
    "scripts_ear": ("scripts/ear", "*.py"),
    "data_ear_features": ("data/ear/features", "*.npy"),
    "docs_path_b": ("docs/ear_path_b_commitment.md", None),
}


def _sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _walk(base: Path, glob: str | None) -> list[Path]:
    if not base.exists():
        return []
    if glob is None:
        return [base] if base.is_file() else []
    if base.is_file():
        return [base]
    return sorted([p for p in base.rglob(glob) if p.is_file()])


def snapshot(root: Path = Path(".")) -> dict:
    out: dict = {"groups": {}, "combined_manifest_sha": "", "c35_baseline": C35_MANIFEST_SHA}
    per_path_shas: list[str] = []
    for gname, (rel, glob) in ANCHOR_GROUPS.items():
        base = root / rel
        entries = []
        for p in _walk(base, glob):
            sha = _sha_file(p)
            entries.append({
                "path": p.relative_to(root).as_posix(),
                "sha": sha,
                "mtime": int(p.stat().st_mtime),
                "size": p.stat().st_size,
            })
            per_path_shas.append(f"{p.relative_to(root).as_posix()}\t{sha}")
        out["groups"][gname] = {"n": len(entries), "entries": entries}
    per_path_shas.sort()
    combined = hashlib.sha256("\n".join(per_path_shas).encode()).hexdigest()
    out["combined_manifest_sha"] = combined
    out["unchanged"] = (combined == C35_MANIFEST_SHA)
    out["changed_paths"] = []  # populated by diff-vs-manifest tool if run
    return out


def main() -> None:
    snap = snapshot(Path("."))
    out_path = Path("data/ear_v0/anchor_preservation.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(snap, f, indent=2, sort_keys=True)
    print(json.dumps({
        "combined_manifest_sha": snap["combined_manifest_sha"],
        "c35_baseline": snap["c35_baseline"],
        "unchanged": snap["unchanged"],
        "n_entries": sum(g["n"] for g in snap["groups"].values()),
    }, indent=2))


if __name__ == "__main__":
    main()
