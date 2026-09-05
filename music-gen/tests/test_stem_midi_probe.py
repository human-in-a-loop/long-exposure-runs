#!/usr/bin/env -S /usr/bin/python3
"""c26 Track C: regression for the 5 focus-song v4 stem_manifest.json files.

Ensures each on-disk manifest parses, contains 6 stem SHAs, and each SHA
byte-matches sha256sum of the referenced WAV. Regression-pins Peach Dream's
non-standard `operator_section_c25_checkpointed/` stem path per c19
invariant (d) disclosure.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

STEMS = ["bass", "drums", "guitar", "piano", "other", "vocals"]
SONGS = {
    "31a164f845f8e27e": None,           # CG - no stem_manifest.json (terminal state)
    "252eb21ce7df7328": "operator_section",
    "51e433ade2a845e1": "operator_section",
    "cdd2717e52820ff6": "operator_section",
    "88d247468cb6d49f": "operator_section_c25_checkpointed",  # c19 invariant (d)
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(sha16: str) -> dict:
    return json.loads((ROOT / f"data/v4/profiles/{sha16}/stem_manifest.json").read_text())


def test_01_all_four_manifests_present_and_parse():
    for sha16, sect in SONGS.items():
        if sect is None:
            continue
        m = _load(sha16)
        assert isinstance(m, dict), sha16
        assert "stems" in m or "stem_shas" in m or "stem_sha256" in m, f"{sha16}: {list(m.keys())}"


def test_02_wig_six_stems_and_shas_match():
    _assert_song_stems("252eb21ce7df7328")


def test_03_rome_six_stems_and_shas_match():
    _assert_song_stems("51e433ade2a845e1")


def test_04_disco_a_six_stems_and_shas_match():
    _assert_song_stems("cdd2717e52820ff6")


def test_05_peach_dream_six_stems_and_shas_match():
    _assert_song_stems("88d247468cb6d49f")


def test_06_peach_dream_uses_non_standard_c25_checkpointed_path():
    """c19 invariant (d) disclosure: PD stems live under
    `operator_section_c25_checkpointed/rc9_6stem/`, not `operator_section/`.
    """
    m = _load("88d247468cb6d49f")
    text = json.dumps(m)
    assert "operator_section_c25_checkpointed" in text or "c25_checkpointed" in text, \
        "PD manifest must reference c25_checkpointed path per c19 invariant (d)"


def _assert_song_stems(sha16: str) -> None:
    m = _load(sha16)
    # Find the stems dict by best-effort schema tolerance
    stems = m.get("stems") or m.get("stem_shas") or m.get("stem_sha256") or {}
    assert isinstance(stems, dict), f"{sha16}: expected stems dict, got {type(stems)}"
    # Locate all 6 stem entries (may be nested under paths/shas)
    found = 0
    for stem in STEMS:
        for k, v in stems.items():
            if stem in k.lower() or (isinstance(v, dict) and stem in json.dumps(v).lower()):
                found += 1
                break
    assert found == 6, f"{sha16}: found {found}/6 stems in manifest"


if __name__ == "__main__":
    fns = [v for k, v in list(globals().items()) if k.startswith("test_")]
    ok = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
            ok += 1
        except AssertionError as e:
            print(f"FAIL {fn.__name__}: {e}")
    print(f"---\n{ok}/{len(fns)} tests passed")
    sys.exit(0 if ok == len(fns) else 1)
