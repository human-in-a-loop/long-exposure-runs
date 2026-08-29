#!/usr/bin/env python3
"""One-shot: write per_band_summary.json from verdict.json per-band counts."""
import json
from collections import Counter

v = json.load(open("data/rules_rated_corpus/verdict.json"))
songs = v["per_song"]
band_ct = Counter(s["band"] for s in songs)
out = {
    "schema": "rule_type_per_band_row_counts",
    "per_band": v["per_band_counts"],
    "per_band_song_count": {str(k): int(v_) for k, v_ in sorted(band_ct.items())},
    "notes": (
        "Row counts summed across all songs in each rating band. "
        "Divide by per_band_song_count[band] for per-song mean. "
        "Bands are the rated-corpus ear-scale buckets (4/5/6/7)."
    ),
}
open("data/rules_rated_corpus/per_band_summary.json", "w").write(
    json.dumps(out, indent=2, sort_keys=True) + "\n"
)
print("wrote data/rules_rated_corpus/per_band_summary.json")
print(json.dumps(out, indent=2, sort_keys=True))
