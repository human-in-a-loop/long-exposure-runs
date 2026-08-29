#!/usr/bin/env python3
# M-RULES-1/extraction/rated-corpus — anchor preservation on 30+ SHAs.
#
# Author: cyd7bevdr@mozmail.com, cycle 40 (fork c320de981fda / clone-0).
#
# Snapshots SHA-256 of 30+ files pre and post the extraction run.
# Coverage: c37 recreate_v0 anchors, c38 recreate_v0_batch anchors,
# c39 recreate_v0_full_corpus anchors, c9 extractors (5 files), c6
# schema+validator+writer (4 files), two frozen rules ledgers.
#
# NO PRNG. Interpreter-guarded.

import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def anchor_paths() -> List[Path]:
    paths = [
        # c37 recreate_v0 (4)
        REPO / "data/recreate_v0/verdict.json",
        REPO / "data/recreate_v0/rubric_hash.txt",
        REPO / "data/recreate_v0/chosen_song.json",
        REPO / "data/recreate_v0/per_stage/06_score/merged.musicxml",
        # c38 recreate_v0_batch (4)
        REPO / "data/recreate_v0_batch/verdict.json",
        REPO / "data/recreate_v0_batch/rubric_hash.txt",
        REPO / "data/recreate_v0_batch/chosen_songs.json",
        REPO / "data/recreate_v0_batch/cross_band_table.tsv",
        # c39 recreate_v0_full_corpus (4)
        REPO / "data/recreate_v0_full_corpus/verdict.json",
        REPO / "data/recreate_v0_full_corpus/rubric_hash.txt",
        REPO / "data/recreate_v0_full_corpus/chosen_songs_full.json",
        REPO / "data/recreate_v0_full_corpus/cross_band_correlation.json",
        # c9 extractors (5)
        REPO / "scripts/rules/extract/harmonic.py",
        REPO / "scripts/rules/extract/rhythmic.py",
        REPO / "scripts/rules/extract/melodic.py",
        REPO / "scripts/rules/extract/form.py",
        REPO / "scripts/rules/extract/arrangement.py",
        # c6 schema+validator+writer (4)
        REPO / "scripts/rules/validate.py",
        REPO / "scripts/rules/ledger.py",
        REPO / "scripts/rules/rule_id.py",
        REPO / "scripts/rules/schema/rules_v1.json",
        # Two frozen rules ledgers (2)
        REPO / "data/rules/ledger.jsonl",
        REPO / "data/rules/ledger_i3_dminor.jsonl",
    ]
    # Add per-song spot-checks: 3 c39 + 2 c38 + 1 c37 already-included
    # → drop c37 (already in list above) → +5 spot merged.musicxml
    per_song_spots = sorted(
        (REPO / "data/recreate_v0_full_corpus/per_song").glob("*/*/per_stage/06_score/merged.musicxml")
    )[:5]
    per_song_spots += sorted(
        (REPO / "data/recreate_v0_batch/per_song").glob("*/*/per_stage/06_score/merged.musicxml")
    )[:3]
    paths.extend(per_song_spots)
    return paths


def snapshot() -> Dict[str, str]:
    out = {}
    for p in anchor_paths():
        out[str(p.relative_to(REPO))] = _sha(p) if p.exists() else "MISSING"
    return out


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "compare"
    pre_p = REPO / "data/rules_rated_corpus/_anchor_pre.json"

    if mode == "pre":
        pre = snapshot()
        pre_p.write_text(json.dumps(pre, indent=2, sort_keys=True) + "\n")
        print(f"pre: {len(pre)} anchors → {pre_p}")
        return 0

    if not pre_p.exists():
        print("pre snapshot missing; run with 'pre' first", file=sys.stderr)
        return 2

    pre = json.loads(pre_p.read_text())
    post = snapshot()

    per_file = []
    all_ok = True
    for rel, pre_sha in sorted(pre.items()):
        post_sha = post.get(rel, "MISSING")
        eq = (pre_sha == post_sha)
        if not eq:
            all_ok = False
        per_file.append({"path": rel, "pre_sha256": pre_sha,
                         "post_sha256": post_sha, "unchanged": eq})

    result = {
        "n_anchors": len(per_file),
        "all_unchanged": all_ok,
        "per_file": per_file,
    }
    out_p = REPO / "data/rules_rated_corpus/anchor_preservation.json"
    out_p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out_p}: n={len(per_file)} all_unchanged={all_ok}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
