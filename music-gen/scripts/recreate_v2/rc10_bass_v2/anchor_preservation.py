#!/usr/bin/env /usr/bin/python3
# Anchor preservation snapshot: pins ≥25 read-only SHAs before + after runs.
# created: 2026-09-02, cycle 55, run-2026-08-28T040704Z, worker, fork 7cc01d726807 clone-1
import json
import hashlib
from pathlib import Path

from ._common import WS, write_json_canonical


ANCHOR_PATHS = [
    "scripts/palette_render/render_stem.py",                            # c33 do-not-touch
    "docs/m_recreate_2_accurate_small_set_rubric_v2.md",                # c50 v2 rubric
    "docs/m_recreate_2_accurate_small_set_rubric.md",                   # c49 v1 rubric
    "docs/rc10_drums_bass_rubric.md",                                    # c54 v1 bass rubric
    "data/rc10_drums_bass_impl/rubric_hash.txt",                         # c54 v1 chain
    "data/rc10_drums_bass_impl/verdict.json",
    "data/rc10_drums_bass_impl/scorecard.tsv",
    "data/rc10_drums_bass_impl/winner_per_stem.json",
    "data/rc10_drums_bass_impl/anchor_preservation.json",
    "data/rc10_drums_bass_impl/byte_determinism.json",
    "data/recreate_v2/focus_set_v2.json",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/bass.wav",
    "data/recreate_v2/baseline/cdd2717e52820ff6/rc9_6stem/bass.wav",
    "data/recreate_v2/baseline/51e433ade2a845e1/rc9_6stem/bass.wav",
    "data/recreate_v2/baseline/252eb21ce7df7328/rc9_6stem/bass.wav",
    "data/recreate_v2/baseline/88d247468cb6d49f/rc9_6stem/bass.wav",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc3_bass_low_band_energy.json",
    "data/recreate_v2/baseline/31a164f845f8e27e/rc3_bass_pyin_voiced_segments.json",
    "data/recreate_v2/baseline/cdd2717e52820ff6/rc3_bass_low_band_energy.json",
    "data/recreate_v2/baseline/51e433ade2a845e1/rc3_bass_low_band_energy.json",
    "data/recreate_v2/baseline/252eb21ce7df7328/rc3_bass_low_band_energy.json",
    "data/recreate_v2/baseline/88d247468cb6d49f/rc3_bass_low_band_energy.json",
    "data/rc10_drums_bass_impl/31a164f845f8e27e/bass/pyin_mono/notes.json",
    "data/rc10_drums_bass_impl/cdd2717e52820ff6/bass/pyin_mono/notes.json",
    "data/rc10_drums_bass_impl/51e433ade2a845e1/bass/pyin_mono/notes.json",
    "data/rc10_drums_bass_impl/252eb21ce7df7328/bass/pyin_mono/notes.json",
    "data/rc10_drums_bass_impl/88d247468cb6d49f/bass/pyin_mono/notes.json",
]


def snapshot():
    out = {}
    for rel in ANCHOR_PATHS:
        p = WS / rel
        if p.exists():
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
        else:
            out[rel] = None
    return out


def write_snapshot(pre, post, path):
    entries = []
    all_ok = True
    for rel in ANCHOR_PATHS:
        p = pre.get(rel); q = post.get(rel)
        ok = (p is not None and p == q)
        if not ok:
            all_ok = False
        entries.append({"path": rel, "pre_sha256": p, "post_sha256": q, "unchanged": ok})
    write_json_canonical(path, {
        "n_anchors": len(ANCHOR_PATHS),
        "all_unchanged": bool(all_ok),
        "entries": entries,
    })
    return all_ok


if __name__ == "__main__":
    s = snapshot()
    print(json.dumps({"n": len(s), "present": sum(1 for v in s.values() if v)}))
