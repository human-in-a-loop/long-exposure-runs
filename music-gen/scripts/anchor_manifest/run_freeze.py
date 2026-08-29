#!/usr/bin/env python3
# scripts/anchor_manifest/run_freeze.py — Cycle 35 clone-2.
# Top-level entry: enumerate, compute, write manifest JSON + rendered index MD.
# created: 2026-08-29
# cycle: 35
# agent: worker
# milestone: _infra/anchor-manifest-v1-clone-2
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

# Ensure workspace root on sys.path so scripts.* imports resolve.
_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))

from scripts.anchor_manifest.enumerate_anchors import enumerate_anchors, LONG_EXPOSURE_PREFIX  # noqa: E402
from scripts.anchor_manifest.compute_sha_manifest import compute_anchor  # noqa: E402


def build_manifest():
    """Build the frozen manifest dict (deterministic, sort_keys-serializable)."""
    anchors = enumerate_anchors()
    computed = [compute_anchor(a) for a in anchors]
    manifest = {
        "schema_version": 1,
        "cycle": 35,
        "milestone": "_infra/anchor-manifest-v1-clone-2",
        "anchor_count": len(computed),
        "long_exposure_prefix": LONG_EXPOSURE_PREFIX,
        "exemptions": {
            "long_exposure_outside_workspace": (
                "Paths under long_exposure_prefix live outside the "
                "workspace and are recorded with an absolute prefix. "
                "The env-var-guarded reachability check ensures the "
                "prefix resolves; missing prefix is a first-class fault."
            ),
        },
        "anchors": computed,
    }
    return manifest


def render_index_md(manifest: dict) -> str:
    lines = []
    lines.append("# Anchor manifest v1 (Cycle 35 Branch C, clone-2)")
    lines.append("")
    lines.append(f"**Schema version:** {manifest['schema_version']}")
    lines.append(f"**Anchor count:** {manifest['anchor_count']}")
    lines.append(f"**Long-exposure prefix (exemption):** `{manifest['long_exposure_prefix']}`")
    lines.append("")
    lines.append("## Anchors")
    lines.append("")
    lines.append("| # | anchor_id | cycle | kind | # paths | # files | is_readonly |")
    lines.append("|---|-----------|-------|------|---------|---------|-------------|")
    for i, a in enumerate(manifest["anchors"], start=1):
        lines.append(
            f"| {i} | `{a['anchor_id']}` | {a['cycle']} | {a['kind']} | "
            f"{len(a['paths'])} | {a['file_count']} | {a['is_readonly']} |"
        )
    lines.append("")
    lines.append("## Per-anchor path SHA summary")
    lines.append("")
    for a in manifest["anchors"]:
        lines.append(f"### `{a['anchor_id']}` (cycle {a['cycle']}, kind: {a['kind']})")
        lines.append("")
        for path_str in a["paths"]:
            e = a["path_entries"][path_str]
            lines.append(f"- **`{path_str}`** — kind={e['kind']}, files={e['entry_count']}"
                         + (f", dir_manifest_sha=`{e['dir_manifest_sha']}`" if e["dir_manifest_sha"] else ""))
            if e["kind"] == "file" and e["sha_per_path"]:
                sha = next(iter(e["sha_per_path"].values()))
                lines.append(f"  - sha256=`{sha}`")
        lines.append("")
    return "\n".join(lines)


def serialize_manifest(manifest: dict) -> bytes:
    return json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def freeze(output_json: Path, output_md: Path) -> dict:
    manifest = build_manifest()
    payload = serialize_manifest(manifest)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_bytes(payload)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_index_md(manifest), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--out-json", default="data/anchor_manifest_v1.json")
    p.add_argument("--out-md", default="docs/anchor_manifest_v1.md")
    args = p.parse_args()
    m = freeze(Path(args.out_json), Path(args.out_md))
    print(f"froze {m['anchor_count']} anchors to {args.out_json}")
