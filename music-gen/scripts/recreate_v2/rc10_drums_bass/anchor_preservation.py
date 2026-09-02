#!/usr/bin/env /usr/bin/python3
# RC10 anchor preservation snapshot (≥25 SHAs pre==post byte-exact).
# created: 2026-09-02, cycle 54, run-2026-08-28T040704Z, worker, fork bdd7bb47f1b5 clone-0
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def collect():
    ap = {}
    # rubric anchors
    ap["docs/m_recreate_2_accurate_small_set_rubric_v2.md"] = sha(ROOT / "docs/m_recreate_2_accurate_small_set_rubric_v2.md")
    ap["data/recreate_v2/rubric_hash.txt"] = sha(ROOT / "data/recreate_v2/rubric_hash.txt")
    ap["data/recreate_v2/rubric_hash_v2.txt"] = sha(ROOT / "data/recreate_v2/rubric_hash_v2.txt")
    ap["data/recreate_v2/focus_set_v2.json"] = sha(ROOT / "data/recreate_v2/focus_set_v2.json")
    # c49 v1 rubric doc
    for rel in [
        "docs/m_recreate_2_accurate_small_set_rubric.md",
        "data/rc2_rc3_impl/verdict.json",
        "data/rc1_rc9_impl/verdict.json",
        "data/recreate_v2/rc7_out/verdict.json",
    ]:
        p = ROOT / rel
        if p.exists():
            ap[rel] = sha(p)
    # c49 baseline anchors: RC2 drum onset count + RC3 bass counts per song
    for sha16 in ["31a164f845f8e27e", "cdd2717e52820ff6", "51e433ade2a845e1",
                  "252eb21ce7df7328", "88d247468cb6d49f"]:
        for rel in [
            f"data/recreate_v2/baseline/{sha16}/rc2_drum_onset_count.json",
            f"data/recreate_v2/baseline/{sha16}/rc3_bass_voiced_segments.json",
        ]:
            p = ROOT / rel
            if p.exists():
                ap[rel] = sha(p)
    # c53 clone-2 rc5 tempo estimates
    for sha16 in ["31a164f845f8e27e", "cdd2717e52820ff6", "51e433ade2a845e1",
                  "252eb21ce7df7328", "88d247468cb6d49f"]:
        p = ROOT / f"data/rc5_impl/{sha16}/rc5_tempo_estimate.json"
        if p.exists():
            ap[f"data/rc5_impl/{sha16}/rc5_tempo_estimate.json"] = sha(p)
    # c53 clone-0 render_stem.py invariant
    p = ROOT / "scripts/palette_render/render_stem.py"
    if p.exists():
        ap["scripts/palette_render/render_stem.py"] = sha(p)
    # baseline drums+bass WAVs (10)
    for sha16 in ["31a164f845f8e27e", "cdd2717e52820ff6", "51e433ade2a845e1",
                  "252eb21ce7df7328", "88d247468cb6d49f"]:
        for stem in ("drums", "bass"):
            p = ROOT / f"data/recreate_v2/baseline/{sha16}/rc9_6stem/{stem}.wav"
            if p.exists():
                ap[f"data/recreate_v2/baseline/{sha16}/rc9_6stem/{stem}.wav"] = sha(p)
    return ap


if __name__ == "__main__":
    ap = collect()
    out = ROOT / "data/rc10_drums_bass_impl/anchor_preservation.json"
    out.write_text(json.dumps({"n_entries": len(ap), "anchors": ap}, sort_keys=True, indent=2) + "\n")
    print(f"anchors={len(ap)} written {out}")
