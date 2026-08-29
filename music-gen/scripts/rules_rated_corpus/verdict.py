#!/usr/bin/env python3
# M-RULES-1/extraction/rated-corpus — verdict emitter.
#
# Author: cyd7bevdr@mozmail.com, cycle 40 (fork c320de981fda / clone-0).
#
# Applies the frozen 3-verdict rubric to the aggregate outputs and
# emits data/rules_rated_corpus/verdict.json with rubric_hash embedded
# byte-equal to data/rules_rated_corpus/rubric_hash.txt.

import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent


def main() -> int:
    data_dir = REPO / "data/rules_rated_corpus"
    agg = json.loads((data_dir / "aggregate_summary.json").read_text())
    det = json.loads((data_dir / "determinism_check.json").read_text())
    anch = json.loads((data_dir / "anchor_preservation.json").read_text())
    rubric_hash = (data_dir / "rubric_hash.txt").read_text().strip()

    # Per-song per-rule_type analysis for the ≥5-per-type-per-song floor.
    per_song_dir = data_dir / "per_song"
    songs_meeting_floor = 0
    rule_types = ("harmonic", "rhythmic", "melodic", "form", "arrangement")
    per_rule_type_short_songs = {rt: 0 for rt in rule_types}
    per_band_counts = {}
    per_song_details = []
    n_songs = 0
    for sd in sorted(per_song_dir.iterdir()):
        if not sd.is_dir():
            continue
        n_songs += 1
        m = json.loads((sd / "stage_manifest.json").read_text())
        counts = m["per_type_counts"]
        band = m["band"]
        per_band_counts.setdefault(band, {rt: 0 for rt in rule_types})
        for rt in rule_types:
            per_band_counts[band][rt] += counts.get(rt, 0)
        song_meets = all(counts.get(rt, 0) >= 5 for rt in rule_types)
        if song_meets:
            songs_meeting_floor += 1
        for rt in rule_types:
            if counts.get(rt, 0) < 5:
                per_rule_type_short_songs[rt] += 1
        per_song_details.append({
            "song_id": m["song_id"],
            "band": band,
            "n_rows": m["n_rows"],
            "per_type_counts": counts,
            "meets_floor": song_meets,
        })

    n_rows = agg["n_rows_aggregate"]
    det_ok = (det["shards_canonical_sha_equal"] and det["per_song_shards_equal"])
    anch_ok = anch["all_unchanged"]
    # "Cleanly extracted" per rubric = extraction produced ≥1 valid row
    # without crash. Distinct from meeting the strict ≥5-per-type floor.
    n_cleanly_extracted = sum(1 for s in per_song_details if s["n_rows"] > 0)
    short_rule_types = {k: v for k, v in per_rule_type_short_songs.items() if v > 5}

    # Rubric-driven verdict (see docs/rules_extraction_rated_corpus_rubric.md).
    if not (det_ok and anch_ok):
        verdict = "RATED_CORPUS_FAILS"
        rationale = (f"determinism_ok={det_ok} anchor_preservation_ok={anch_ok}; "
                     "either determinism × 2 failed or a read-only anchor drifted")
    elif n_cleanly_extracted < 20:
        verdict = "RATED_CORPUS_FAILS"
        rationale = f"only {n_cleanly_extracted}/43 songs produced valid rows (< 20 minimum)"
    elif songs_meeting_floor >= 36 and n_rows >= 900 and not short_rule_types:
        verdict = "RATED_CORPUS_LANDS"
        rationale = (f"{songs_meeting_floor}/43 songs meet ≥5-per-type floor across all 5 "
                     f"rule_types; {n_rows} aggregate rows ≥ 900")
    else:
        # PARTIAL — either 20-35 songs meet the strict per-type floor OR
        # one or more rule_types falls short on >5 songs (rubric explicitly
        # OR-clauses these). Honest per-song/per-rule_type gaps disclosed
        # in the report §4/§5.
        verdict = "RATED_CORPUS_PARTIAL"
        rationale = (
            f"{n_cleanly_extracted}/43 songs cleanly extracted with {n_rows} valid rows; "
            f"{songs_meeting_floor}/43 songs meet the strict ≥5-per-type-per-song floor; "
            f"rule_types falling short on >5 songs: {short_rule_types}"
        )

    result = {
        "verdict": verdict,
        "rubric_hash": rubric_hash,
        "rationale": rationale,
        "n_songs": n_songs,
        "n_rows_aggregate": n_rows,
        "n_duplicates_dropped": agg.get("n_duplicates_dropped", 0),
        "per_type_counts_aggregate": agg["per_type_counts"],
        "songs_meeting_per_type_floor": songs_meeting_floor,
        "per_rule_type_short_song_count": per_rule_type_short_songs,
        "per_band_counts": per_band_counts,
        "byte_determinism_x2": {
            "aggregate_shard_canonical_sha_equal": det["shards_canonical_sha_equal"],
            "per_song_shards_all_equal": det["per_song_shards_equal"],
            "aggregate_run1_sha": det["shard_run1_canonical_sha"],
            "aggregate_run2_sha": det["shard_run2_canonical_sha"],
        },
        "anchor_preservation": {
            "n_anchors": anch["n_anchors"],
            "all_unchanged": anch["all_unchanged"],
        },
        "per_song": per_song_details,
        "merge_deferred_on_git_log": True,  # per c38/c39 precedent
    }

    out_p = REPO / "data/rules_rated_corpus/verdict.json"
    out_p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"VERDICT: {verdict}")
    print(f"  rationale: {rationale}")
    print(f"  n_rows: {n_rows}, songs_meeting_floor: {songs_meeting_floor}/43")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
