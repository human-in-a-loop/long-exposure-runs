#!/usr/bin/env python3
# c41 harmonic-window-refinement — anchor preservation snapshot.
#
# Records SHA-256 of ≥32 anchor files; used pre/post to assert unchanged.
#
# NO PRNG. Interpreter-guarded. No sidecar_nonfactor imports.

import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


ANCHOR_FILES: List[str] = [
    # c9 extractors
    "scripts/rules/extract/harmonic.py",
    "scripts/rules/extract/rhythmic.py",
    "scripts/rules/extract/melodic.py",
    "scripts/rules/extract/form.py",
    "scripts/rules/extract/arrangement.py",
    # c6 writer/validator/schema/id
    "scripts/rules/validate.py",
    "scripts/rules/ledger.py",
    "scripts/rules/rule_id.py",
    "scripts/rules/schema/rules_v1.json",
    # rules ledgers
    "data/rules/ledger.jsonl",
    "data/rules/ledger_i3_dminor.jsonl",
    "data/rules/ledger_rated_corpus.jsonl",
    # c37 recreate_v0
    "data/recreate_v0/verdict.json",
    "data/recreate_v0/rubric_hash.txt",
    # c38 recreate_v0_batch
    "data/recreate_v0_batch/verdict.json",
    "data/recreate_v0_batch/rubric_hash.txt",
    # c39 recreate_v0_full_corpus
    "data/recreate_v0_full_corpus/verdict.json",
    "data/recreate_v0_full_corpus/rubric_hash.txt",
    # c40 rated_corpus (READ-ONLY)
    "data/rules_rated_corpus/verdict.json",
    "data/rules_rated_corpus/rubric_hash.txt",
    "data/rules_rated_corpus/aggregate_summary.json",
    "data/rules_rated_corpus/aggregate_summary.tsv",
    # c40 report + rubric
    "docs/rules_extraction_rated_corpus_rubric.md",
    "docs/rules_extraction_rated_corpus_report.md",
]

# 8 per-song merged.musicxml spot-checks (chosen deterministically from c40 manifest).
SPOT_CHECK_SONG_INDICES = [0, 5, 10, 15, 20, 25, 30, 35]


def _spot_check_paths() -> List[str]:
    manifest_p = REPO / "data" / "rules_rated_corpus" / "song_manifest.json"
    songs = json.loads(manifest_p.read_text())["songs"]
    paths: List[str] = []
    for idx in SPOT_CHECK_SONG_INDICES:
        song = songs[idx]
        p = Path(song["merged_musicxml"])
        try:
            rel = str(p.relative_to(REPO))
        except ValueError:
            rel = str(p)
        paths.append(rel)
    return paths


def snapshot(out_p: Path) -> Dict:
    entries: Dict[str, str] = {}
    missing: List[str] = []
    for rel in ANCHOR_FILES + _spot_check_paths():
        p = REPO / rel
        if not p.exists():
            missing.append(rel)
            continue
        entries[rel] = _sha(p)
    result = {
        "n_anchors": len(entries),
        "missing": missing,
        "shas": entries,
    }
    out_p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def compare(pre_p: Path, post_p: Path, out_p: Path) -> Dict:
    pre = json.loads(pre_p.read_text())
    post = json.loads(post_p.read_text())
    drifted: List[str] = []
    for rel, sha in pre["shas"].items():
        if post["shas"].get(rel) != sha:
            drifted.append(rel)
    result = {
        "n_anchors_pre": pre["n_anchors"],
        "n_anchors_post": post["n_anchors"],
        "n_drifted": len(drifted),
        "drifted": drifted,
        "unchanged": len(drifted) == 0 and pre["n_anchors"] == post["n_anchors"],
    }
    out_p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: anchor_preservation.py {snapshot <out.json>|compare <pre.json> <post.json> <out.json>}",
              file=sys.stderr)
        return 2
    mode = sys.argv[1]
    if mode == "snapshot":
        snapshot(Path(sys.argv[2]))
        return 0
    if mode == "compare":
        r = compare(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
        print(f"anchor_preservation: unchanged={r['unchanged']} n_drifted={r['n_drifted']}")
        return 0 if r["unchanged"] else 1
    print(f"unknown mode: {mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
