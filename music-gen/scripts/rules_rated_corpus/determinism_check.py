#!/usr/bin/env python3
# M-RULES-1/extraction/rated-corpus — determinism × 2 check.
#
# Author: cyd7bevdr@mozmail.com, cycle 40 (fork c320de981fda / clone-0).
#
# Two fresh tempfile.mkdtemp() output paths. Runs the full pipeline
# (per-song extraction + aggregation into a temp shard) in each.
# Computes SHA-256 on the canonical-sort of ledger_rated_corpus.jsonl
# (rows sorted by rule_id, canonical JSON) and every per-song
# rules_shard.jsonl. Asserts equality across the two runs.
#
# NO PRNG. Interpreter-guarded.

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_file(p: Path) -> str:
    return _sha256_bytes(p.read_bytes())


def canonical_shard_sha(shard_path: Path) -> str:
    """SHA-256 of the canonical-sort of the shard (by rule_id)."""
    rows = []
    for line in shard_path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    rows.sort(key=lambda r: r["rule_id"])
    canon = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows).encode()
    return _sha256_bytes(canon)


def run_one(out_dir: Path, manifest_p: Path) -> None:
    """Run full pipeline into a fresh out_dir."""
    (out_dir / "per_song").mkdir(parents=True, exist_ok=True)
    # Per-song extraction (all 43 songs)
    subprocess.run(
        ["/usr/bin/python3", str(_HERE / "extract_per_song.py"),
         str(manifest_p), str(out_dir)],
        check=True, cwd=str(REPO),
    )
    # Aggregate to temp shard
    shard_p = out_dir / "ledger_rated_corpus.jsonl"
    subprocess.run(
        ["/usr/bin/python3", str(_HERE / "aggregate_and_append.py"),
         str(out_dir), str(shard_p)],
        check=True, cwd=str(REPO),
    )


def main() -> int:
    manifest_p = REPO / "data/rules_rated_corpus/song_manifest.json"
    if not manifest_p.exists():
        print("song_manifest.json not found; run song_manifest.py first", file=sys.stderr)
        return 2

    tmp1 = Path(tempfile.mkdtemp(prefix="c40_det1_"))
    tmp2 = Path(tempfile.mkdtemp(prefix="c40_det2_"))
    try:
        print(f"run 1 → {tmp1}")
        run_one(tmp1, manifest_p)
        print(f"run 2 → {tmp2}")
        run_one(tmp2, manifest_p)

        shard1 = tmp1 / "ledger_rated_corpus.jsonl"
        shard2 = tmp2 / "ledger_rated_corpus.jsonl"
        sha1 = canonical_shard_sha(shard1)
        sha2 = canonical_shard_sha(shard2)
        shards_equal = (sha1 == sha2)

        # Per-song shard equality
        per_song_pairs = []
        song_dirs1 = sorted((tmp1 / "per_song").iterdir())
        song_dirs2_by_id = {p.name: p for p in (tmp2 / "per_song").iterdir()}
        for sd1 in song_dirs1:
            if not sd1.is_dir():
                continue
            sd2 = song_dirs2_by_id[sd1.name]
            s1 = _sha256_file(sd1 / "rules_shard.jsonl")
            s2 = _sha256_file(sd2 / "rules_shard.jsonl")
            per_song_pairs.append({
                "song_id": sd1.name,
                "run1_sha256": s1,
                "run2_sha256": s2,
                "equal": s1 == s2,
            })
        all_per_song_equal = all(p["equal"] for p in per_song_pairs)

        result = {
            "shards_canonical_sha_equal": shards_equal,
            "shard_run1_canonical_sha": sha1,
            "shard_run2_canonical_sha": sha2,
            "per_song_shards_equal": all_per_song_equal,
            "n_per_song_pairs": len(per_song_pairs),
            "n_per_song_mismatches": sum(1 for p in per_song_pairs if not p["equal"]),
            "per_song_pairs": per_song_pairs,
        }
        out_p = REPO / "data/rules_rated_corpus/determinism_check.json"
        out_p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"wrote {out_p}: shard_equal={shards_equal} per_song_equal={all_per_song_equal}")
        return 0 if (shards_equal and all_per_song_equal) else 1
    finally:
        shutil.rmtree(tmp1, ignore_errors=True)
        shutil.rmtree(tmp2, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
