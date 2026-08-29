"""Walk data/ear_v0/per_song_features/*.npy and emit a manifest row per song.

Row: {npy_path, npy_sha256, source_song_sha256 (parsed from stem),
      cache_key_derivation, n_bytes}.

Byte-deterministic (sorted output, no PRNG). Runs against the current
cache count — smoke test on the 8 files present now; final pass runs
against 43. Distinct from `extract_features_v0.build_manifest` which
emits the c6-anchored per-song entries; this utility is a raw
filesystem-view for c37 audits and orphan-check hygiene.
"""
# created: 2026-08-29T06:00:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: _infra/feature-cache-manifest-emitter-clone-0
from __future__ import annotations
import sys
assert sys.executable == "/usr/bin/python3", sys.executable
import hashlib, json
from pathlib import Path

CACHE_DIR = Path("data/ear_v0/per_song_features")
OUT = Path("data/ear_v0/feature_cache_manifest_raw.json")


def _sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def build(cache_dir: Path = CACHE_DIR) -> dict:
    files = sorted(cache_dir.glob("*.npy"))
    entries = []
    for p in files:
        entries.append({
            "npy_path": p.as_posix(),
            "npy_sha256": _sha_file(p),
            "source_song_sha256": p.stem,
            "cache_key_derivation": "hashlib.sha256(mp3 file bytes).hexdigest()",
            "n_bytes": p.stat().st_size,
        })
    entries.sort(key=lambda e: e["source_song_sha256"])
    return {
        "n_songs": len(entries),
        "cache_dir": cache_dir.as_posix(),
        "entries": entries,
    }


def main() -> None:
    m = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(m, f, indent=2, sort_keys=True)
    print(json.dumps({"n_songs": m["n_songs"], "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
