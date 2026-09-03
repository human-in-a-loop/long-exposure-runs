#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 1
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES
# ---
"""Profile writer tests: schema keys + profile_id determinism."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.sound_match import profile_writer as pw  # noqa: E402


def _make_row(family: str) -> dict:
    identity = {"sf2_path": "/usr/share/sounds/sf2/FluidR3_GM.sf2",
                "bank": 0, "program": 33}
    if family == "sfz":
        identity = {"sfz_path": "workspace/palette/sfz/bass_finger.sfz"}
    if family == "stem_sampled":
        identity = {"sfz_path": "data/v4/stem_sampled/31a164f/bass.sfz"}
    if family == "surge":
        identity = {"vst3_path": "/usr/lib/vst3/SurgeXT.vst3",
                    "patch_name": "Bass/Finger"}
    return pw.build_profile(
        song_sha16="31a164f845f8e27e",
        instrument="bass",
        family=family,
        identity=identity,
        params={"sample_rate": 44100, "gain": 0.8},
        deps_sha256={"soundfont_sha256": "74594e8f4250680a"},
        objective_scores={"composite": 1.23, "mel_l1_db": 2.0},
        search_metadata={"seed": 0, "n_candidates": 15, "date": "2026-09-03"},
        render_replayable=(family != "surge"),
    )


def test_schema_validates_three_families():
    for fam in ("sf2", "sfz", "stem_sampled"):
        row = _make_row(fam)
        for k in pw._REQUIRED_KEYS:
            assert k in row, f"family={fam} missing {k}"
        assert row["schema_v"] == pw.SCHEMA_V
        assert row["family"] == fam
        assert isinstance(row["profile_id"], str)
        assert len(row["profile_id"]) == 36  # UUID canonical
    print("PASS test_schema_validates_three_families")


def test_profile_id_reproducible_from_fresh_dict():
    r1 = _make_row("sf2")
    r2 = _make_row("sf2")
    assert r1["profile_id"] == r2["profile_id"], (r1["profile_id"], r2["profile_id"])
    # Also: adding render_sha256 must not change the id.
    r3 = dict(r1)
    r3["render_sha256"] = "abc" * 20
    assert pw.compute_profile_id(r3) == r1["profile_id"]
    print("PASS test_profile_id_reproducible_from_fresh_dict")


def test_bad_family_rejected():
    try:
        pw.build_profile(
            song_sha16="deadbeef",
            instrument="bass",
            family="banjo",  # invalid
            identity={}, params={}, deps_sha256={},
            objective_scores={}, search_metadata={},
        )
    except ValueError:
        print("PASS test_bad_family_rejected")
        return
    raise AssertionError("expected ValueError on family=banjo")


def test_write_profile_round_trip():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "cg" / "bass.json"
        row = _make_row("sf2")
        pw.write_profile(row, p)
        assert p.exists()
        parsed = json.loads(p.read_bytes())
        assert parsed["profile_id"] == row["profile_id"]
    print("PASS test_write_profile_round_trip")


if __name__ == "__main__":
    test_schema_validates_three_families()
    test_profile_id_reproducible_from_fresh_dict()
    test_bad_family_rejected()
    test_write_profile_round_trip()
    print("OK")
