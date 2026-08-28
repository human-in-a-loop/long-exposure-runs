"""Append-only provenance ledger for the ingestion chassis.

One JSONL file per source. First line is a `kind:"source"` row; subsequent
lines are `kind:"clip"` rows. See docs/provenance_schema.md.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from scripts.ingest.chunker import (
    CHUNKER_VERSION,
    CLIP_S,
    OVERLAP_S,
    ChunkResult,
)

MANIFESTS_DIR = Path("data/ingestion/manifests")

_SOURCE_REQUIRED = {
    "kind": str, "schema_v": int, "source_id": str, "source_type": str,
    "source_ref": str, "sr_hz": int, "n_samples": int, "duration_s": (int, float),
    "bytes_sha256": str, "chunker_version": str, "tail_rule": str,
    "ingest_ts": str,
}
_CLIP_REQUIRED = {
    "kind": str, "schema_v": int, "source_id": str, "clip_index": int,
    "clip_id": str, "t_start_s": (int, float), "t_end_s": (int, float),
    "n_samples": int, "sr_hz": int, "clip_path": str,
    "clip_bytes_sha256": str, "short_song": bool, "anchored_tail": bool,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_manifest(result: ChunkResult, source_type: str, source_ref: str,
                   manifest_path: Path) -> Path:
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    src_row = dict(
        kind="source",
        schema_v=1,
        source_id=result.source_id,
        source_type=source_type,
        source_ref=source_ref,
        sr_hz=result.sr_hz,
        n_samples=result.n_samples,
        duration_s=result.n_samples / result.sr_hz,
        bytes_sha256=result.source_bytes_sha256,
        chunker_version=CHUNKER_VERSION,
        tail_rule="anchored",
        ingest_ts=_now_iso(),
    )
    with manifest_path.open("w") as f:
        f.write(json.dumps(src_row, sort_keys=True) + "\n")
        for row in result.clips:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    return manifest_path


def read_manifest(manifest_path: Path) -> tuple[dict, list[dict]]:
    src: dict | None = None
    clips: list[dict] = []
    with Path(manifest_path).open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("kind") == "source":
                if src is not None:
                    raise ValueError("multiple source rows")
                src = row
            elif row.get("kind") == "clip":
                clips.append(row)
            else:
                raise ValueError(f"unknown row kind: {row.get('kind')!r}")
    if src is None:
        raise ValueError("no source row")
    return src, clips


def _type_ok(value: Any, expected: Any) -> bool:
    return isinstance(value, expected)


def validate_manifest(manifest_path: Path, *, check_clip_files: bool = True
                      ) -> list[str]:
    """Return a list of failure strings. Empty list => manifest is valid."""
    errors: list[str] = []
    try:
        src, clips = read_manifest(manifest_path)
    except Exception as exc:
        return [f"parse error: {exc}"]

    for k, t in _SOURCE_REQUIRED.items():
        if k not in src:
            errors.append(f"source missing field: {k}")
        elif not _type_ok(src[k], t):
            errors.append(f"source field {k!r} wrong type: {type(src[k]).__name__}")

    seen: set[tuple[str, int]] = set()
    prev_end: float | None = None
    prev_row: dict | None = None
    sr_hz = src.get("sr_hz")
    for row in clips:
        for k, t in _CLIP_REQUIRED.items():
            if k not in row:
                errors.append(f"clip missing field: {k}")
            elif not _type_ok(row[k], t):
                errors.append(f"clip field {k!r} wrong type in idx={row.get('clip_index')}")
        # FK to source
        if row.get("source_id") != src.get("source_id"):
            errors.append(f"clip idx={row.get('clip_index')} source_id mismatch")
        # unique (source_id, clip_index)
        key = (row.get("source_id"), row.get("clip_index"))
        if key in seen:
            errors.append(f"duplicate (source_id, clip_index) {key}")
        seen.add(key)
        # monotonic starts
        if prev_row is not None and row["t_start_s"] < prev_row["t_start_s"]:
            errors.append(f"non-monotonic t_start_s at idx={row['clip_index']}")
        # overlap invariant: adjacent clips overlap by >= OVERLAP_S - eps
        if prev_row is not None and not prev_row.get("short_song", False):
            eps = 1.0 / (sr_hz or 22050)
            overlap = prev_row["t_end_s"] - row["t_start_s"]
            if overlap + eps < OVERLAP_S:
                errors.append(
                    f"overlap invariant broken between idx={prev_row['clip_index']} and "
                    f"idx={row['clip_index']}: {overlap:.6f}s < {OVERLAP_S}s"
                )
        prev_row = row

    if check_clip_files:
        for row in clips:
            cp = Path(row.get("clip_path", ""))
            if not cp.exists():
                errors.append(f"missing clip file: {cp}")
                continue
            # Verify the *decoded pcm bytes* of the on-disk clip match the
            # recorded hash — this is the replay proof.
            from scripts.ingest.wavio import (
                encode_pcm16_bytes,
                read_pcm16_mono,
            )
            samp, _ = read_pcm16_mono(cp)
            got = hashlib.sha256(encode_pcm16_bytes(samp)).hexdigest()
            if got != row.get("clip_bytes_sha256"):
                errors.append(
                    f"clip sha mismatch at {cp}: recorded={row['clip_bytes_sha256'][:12]} "
                    f"observed={got[:12]}"
                )
    return errors


def replay(manifest_path: Path, source_wav: Path, out_dir: Path) -> list[str]:
    """Regenerate clip files from the source WAV and check byte identity
    against the manifest. Returns list of mismatches; empty = success."""
    from scripts.ingest.chunker import chunk
    src, clips_recorded = read_manifest(manifest_path)
    res = chunk(source_wav, out_dir, source_type=src["source_type"],
                source_ref=src["source_ref"])
    mismatches: list[str] = []
    if res.source_id != src["source_id"]:
        mismatches.append(f"source_id changed: {src['source_id']} -> {res.source_id}")
    by_idx = {c["clip_index"]: c for c in clips_recorded}
    for new in res.clips:
        old = by_idx.get(new["clip_index"])
        if not old:
            mismatches.append(f"new clip idx={new['clip_index']} not in manifest")
            continue
        if new["clip_bytes_sha256"] != old["clip_bytes_sha256"]:
            mismatches.append(
                f"clip idx={new['clip_index']} sha mismatch"
            )
    if len(res.clips) != len(clips_recorded):
        mismatches.append(
            f"clip count differs: manifest={len(clips_recorded)} replay={len(res.clips)}"
        )
    return mismatches
