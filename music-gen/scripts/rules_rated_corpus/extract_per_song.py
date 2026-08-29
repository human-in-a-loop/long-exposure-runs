#!/usr/bin/env python3
# M-RULES-1/extraction/rated-corpus — per-song extractor.
#
# Author: cyd7bevdr@mozmail.com, cycle 40 (fork c320de981fda / clone-0).
#
# For one song: reads that song's merged.musicxml + basic-pitch sidecars,
# invokes each of the 5 c9 extractors via READ-ONLY import through
# set_extraction_context (identical pattern to scripts/rules/extract/
# breadth_seeds.py), writes a per-song per_song/<song_id>/rules_shard.jsonl
# of candidate rows (unappended), and writes a stage_manifest.json marking
# completion (idempotent skip on re-run).
#
# NO PRNG. Interpreter-guarded. No sidecar_nonfactor imports.

import json
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List, Tuple

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent  # rules_rated_corpus -> scripts -> repo
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import music21  # noqa: E402

# Read-only imports of c9 extractors + c6 schema/validator.
from scripts.rules.extract import harmonic, rhythmic, melodic, form, arrangement  # noqa: E402
from scripts.rules.extract._common import (  # noqa: E402
    FIXED_TS, DEFAULT_TEMPO_BPM,
    set_extraction_context, reset_extraction_context,
    event_id_for, NullWithReason,
)
from scripts.rules.rule_id import derive_rule_id  # noqa: E402
from scripts.rules.validate import validate_row  # noqa: E402

EXTRACTORS = [
    ("harmonic", harmonic),
    ("rhythmic", rhythmic),
    ("melodic", melodic),
    ("form", form),
    ("arrangement", arrangement),
]


def _finish(rule: Dict, ext_mod) -> Dict:
    rule["event_type"] = "rule"
    rule["schema_v"] = 1
    rule["ts"] = FIXED_TS
    rule["extractor"] = ext_mod.EXTRACTOR
    rule["extractor_version"] = ext_mod.EXTRACTOR_VERSION
    rid = derive_rule_id(rule)
    rule["rule_id"] = rid
    rule["event_id"] = event_id_for(rid)
    return rule


def _apply_coercions(rt: str, candidates: List[Dict]) -> Tuple[List[Dict], List[NullWithReason]]:
    """Mirror scripts/rules/extract/breadth_seeds.py's _coerce_row_or_skip
    coercion policy exactly, so real-audio-derived scores that produce
    degenerate rows are skipped with a null-with-reason rather than
    validated-and-emitted.
    """
    nulls: List[NullWithReason] = []
    if rt == "harmonic":
        cleaned = []
        for c in candidates:
            prog = c.get("parameters", {}).get("chord_progression") or []
            uniq = {p for p in prog}
            if len(uniq) < 2:
                nulls.append(NullWithReason(rt, "insufficient-progression",
                    f"scope={c.get('scope',{}).get('level')} unique_chords={len(uniq)}"))
                continue
            cleaned.append(c)
        candidates = cleaned
    elif rt == "rhythmic":
        cleaned = []
        for c in candidates:
            pat = c.get("parameters", {}).get("pattern") or []
            if pat and all(t == "rest" for t in pat):
                nulls.append(NullWithReason(rt, "all-rest-pattern",
                    f"scope={c.get('scope',{}).get('level')} n_cells={len(pat)}"))
                continue
            cleaned.append(c)
        candidates = cleaned
    elif rt == "melodic":
        cleaned = []
        for c in candidates:
            pch = c.get("parameters", {}).get("pitch_class_histogram") or []
            nonzero = sum(1 for v in pch if v > 0.0)
            if nonzero == 1 and abs(sum(pch) - 1.0) < 1e-6 and pch[0] == 1.0:
                nulls.append(NullWithReason(rt, "no_pitched_notes",
                    f"scope={c.get('scope',{}).get('level')}"))
                continue
            cleaned.append(c)
        candidates = cleaned
    if not candidates:
        nulls.append(NullWithReason(rt, "no_rows_after_coercion", ""))
    return candidates, nulls


def extract_one(song: Dict, out_dir: Path) -> Dict:
    """Run 5 extractors on one song → write rules_shard.jsonl + stage_manifest.json.

    Idempotent: if stage_manifest.json already exists in out_dir, returns
    the parsed manifest without redoing work.
    """
    song_id = song["song_id"]
    per_song_dir = out_dir / "per_song" / song_id
    per_song_dir.mkdir(parents=True, exist_ok=True)
    manifest_p = per_song_dir / "stage_manifest.json"

    if manifest_p.exists():
        return json.loads(manifest_p.read_text())

    score_p = Path(song["merged_musicxml"])
    bp_dir = Path(song["bp_dir"])

    wall_start = time.monotonic()
    rows: List[Dict] = []
    per_type_counts: Dict[str, int] = {}
    per_type_nulls: Dict[str, List[Dict]] = {}
    error: str = ""

    try:
        set_extraction_context(f"rated_corpus::{song_id}", score_p, bp_dir)
        score = music21.converter.parse(str(score_p))
        for rt, mod in EXTRACTORS:
            per_type_nulls.setdefault(rt, [])
            try:
                candidates = list(mod.extract(score, tempo_bpm=DEFAULT_TEMPO_BPM))
            except Exception as exc:
                per_type_nulls[rt].append({
                    "reason": "extractor_crashed",
                    "detail": f"{type(exc).__name__}: {exc}",
                })
                per_type_counts[rt] = 0
                continue
            candidates, nulls = _apply_coercions(rt, candidates)
            for n in nulls:
                per_type_nulls[rt].append({"reason": n.reason, "detail": n.detail})
            finished = [_finish(c, mod) for c in candidates]
            # Validate each row; drop invalid rows (recorded as nulls).
            valid = []
            for r in finished:
                errs = validate_row(r)
                if errs:
                    per_type_nulls[rt].append({
                        "reason": "validation_failed",
                        "detail": "; ".join(errs[:3]),
                    })
                else:
                    valid.append(r)
            rows.extend(valid)
            per_type_counts[rt] = len(valid)
    except Exception:
        error = traceback.format_exc()
    finally:
        reset_extraction_context()

    wall = round(time.monotonic() - wall_start, 3)
    shard_p = per_song_dir / "rules_shard.jsonl"
    # Sort rows by rule_id for byte-deterministic shard file.
    rows.sort(key=lambda r: r["rule_id"])
    shard_p.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))

    manifest = {
        "song_id": song_id,
        "band": song["band"],
        "relpath": song["relpath"],
        "source": song["source"],
        "canonical_index": song["canonical_index"],
        "merged_musicxml": song["merged_musicxml"],
        "bp_dir": song["bp_dir"],
        "n_rows": len(rows),
        "per_type_counts": per_type_counts,
        "per_type_nulls": per_type_nulls,
        "wall_clock_s": wall,
        "shard_path": str(shard_p.relative_to(out_dir)),
        "error": error,
    }
    manifest_p.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: extract_per_song.py <song_manifest.json> <out_dir> [song_idx]", file=sys.stderr)
        return 2
    songs = json.loads(Path(sys.argv[1]).read_text())["songs"]
    out_dir = Path(sys.argv[2])
    idxs = [int(sys.argv[3])] if len(sys.argv) > 3 else list(range(len(songs)))
    for i in idxs:
        m = extract_one(songs[i], out_dir)
        print(f"[{i}] {m['song_id'][:16]} band={m['band']} n_rows={m['n_rows']} wall={m['wall_clock_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
