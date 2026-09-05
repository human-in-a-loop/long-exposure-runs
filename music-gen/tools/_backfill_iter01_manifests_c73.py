#!/usr/bin/env /usr/bin/python3
"""c73 P2.c iter-01 manifest back-fill.

Adds c69-shape provenance.<stem>.render_family block + audibility flag per stem to
each of the 5 iter-01 ab_mix.manifest.json files. Preserves original file sha in
_original_ab_mix_manifest_sha256. WAV bytes untouched (asserted via sha256sum).

Discipline:
  - No PRNG, no wall-clock in payload
  - Additive edit only; original fields preserved verbatim
  - render_family: 'vomm_generated_midi_via_sf2' for bass/drums
  - render_family: 'absent_no_generator_output' for guitar/piano/other/vocals
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
from pathlib import Path

_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

ROOT = Path("/home/user/long-exposure-runs/music-gen")
ITER01 = ROOT / "data/v4/gen/iteration_01"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def backfill(mfjson: Path) -> tuple[str, str, str]:
    """Backfill one manifest, return (wav_pre, wav_post, manifest_new_sha)."""
    ab_wav = mfjson.parent / "ab_mix.wav"
    wav_pre = sha256(ab_wav)
    orig_sha = sha256(mfjson)
    with open(mfjson, "r", encoding="utf-8") as f:
        m = json.load(f)
    if "_original_ab_mix_manifest_sha256" in m and "provenance" in m:
        # Already backfilled; skip
        wav_post = sha256(ab_wav)
        new_sha = sha256(mfjson)
        return wav_pre, wav_post, new_sha
    m["_original_ab_mix_manifest_sha256"] = orig_sha
    m["_backfilled_by_cycle"] = 73
    m["_backfill_note"] = (
        "c73 P2.c c69-shape provenance backfill: render_family + per-stem audibility. "
        "WAV bytes byte-identical pre==post (asserted). Manifest sha drifts by design."
    )
    prov = {
        "bass": {
            "render_family": "vomm_generated_midi_via_sf2",
            "audible": True,
            "wav_sha256": m.get("bass_wav_sha256"),
            "midi_sha256": m.get("bass_midi_sha256"),
            "gain_applied": m.get("bass_gain"),
            "profile_relpath": m.get("donor_bass_profile_relpath"),
        },
        "drums": {
            "render_family": "vomm_generated_midi_via_sf2",
            "audible": True,
            "wav_sha256": m.get("drums_wav_sha256"),
            "midi_sha256": m.get("drums_midi_sha256"),
            "gain_applied": m.get("drums_gain"),
            "profile_relpath": m.get("donor_drums_profile_relpath"),
            "note_gm_standard_kit_shim_when_profile_null": (
                m.get("donor_drums_profile_relpath") is None
            ),
        },
        "guitar": {"render_family": "absent_no_generator_output", "audible": False},
        "piano":  {"render_family": "absent_no_generator_output", "audible": False},
        "other":  {"render_family": "absent_no_generator_output", "audible": False},
        "vocals": {"render_family": "absent_no_generator_output", "audible": False,
                   "note": "generated songs are instrumental per campaign L64"},
    }
    m["provenance"] = prov
    with open(mfjson, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2, sort_keys=True)
        f.write("\n")
    wav_post = sha256(ab_wav)
    new_sha = sha256(mfjson)
    assert wav_pre == wav_post, f"WAV MUTATED: {wav_pre} != {wav_post} at {ab_wav}"
    return wav_pre, wav_post, new_sha


def main() -> int:
    songs = sorted(p for p in ITER01.iterdir() if p.is_dir() and p.name.startswith("gen_v4_song_"))
    print(f"backfilling {len(songs)} iter-01 manifests")
    for song_dir in songs:
        mf = song_dir / "ab_mix.manifest.json"
        if not mf.exists():
            print(f"  SKIP missing: {mf}")
            continue
        pre, post, new = backfill(mf)
        status = "IDENTICAL" if pre == post else "MUTATED"
        print(f"  {song_dir.name}: WAV_{status} pre={pre[:16]}... post={post[:16]}... manifest_new_sha={new[:16]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
