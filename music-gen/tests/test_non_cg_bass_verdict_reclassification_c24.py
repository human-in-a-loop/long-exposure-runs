#!/usr/bin/env -S /usr/bin/python3
"""c26 Track C: regression for the 4 non-CG bass_family_verdict_c23.json
c24-reclassified verdicts. Under distance semantics per c22 operator
resolution, top-1 emb_cos_dist > 0.40 = SF2_RULED_OUT (Rome, Peach Dream);
top-1 emb_cos_dist <= 0.40 = STILL_INDETERMINATE (WIG, Disco A). Also
asserts supersedes_path is `str` per c14 lemma, and the c23 pre-
reclassification sibling exists under stale/ per invariant (d).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

SONGS = {
    "252eb21ce7df7328": ("STILL_INDETERMINATE", "what_if_i_go"),
    "51e433ade2a845e1": ("SF2_RULED_OUT",       "rome"),
    "cdd2717e52820ff6": ("STILL_INDETERMINATE", "disco_a"),
    "88d247468cb6d49f": ("SF2_RULED_OUT",       "peach_dream"),
}


def _load(sha16: str) -> dict:
    return json.loads((ROOT / f"data/v4/profiles/{sha16}/bass_family_verdict_c23.json").read_text())


def test_01_wig_verdict_reclassified_indeterminate():
    d = _load("252eb21ce7df7328")
    assert d["verdict"] == "STILL_INDETERMINATE", d["verdict"]


def test_02_rome_verdict_reclassified_ruled_out():
    d = _load("51e433ade2a845e1")
    assert d["verdict"] == "SF2_RULED_OUT", d["verdict"]


def test_03_disco_a_verdict_reclassified_indeterminate():
    d = _load("cdd2717e52820ff6")
    assert d["verdict"] == "STILL_INDETERMINATE", d["verdict"]


def test_04_peach_dream_verdict_reclassified_ruled_out():
    d = _load("88d247468cb6d49f")
    assert d["verdict"] == "SF2_RULED_OUT", d["verdict"]


def test_05_all_supersedes_path_is_str_per_c14_lemma():
    for sha16 in SONGS:
        d = _load(sha16)
        sp = d.get("supersedes_path")
        assert isinstance(sp, (str, type(None))), \
            f"{sha16}: supersedes_path must be str|None per c14 lemma, got {type(sp)}"
        assert not isinstance(sp, list), f"{sha16}: supersedes_path must NEVER be list per c14"


def test_06_all_stale_c23_scope_extension_siblings_exist():
    for sha16, (_, slug) in SONGS.items():
        expected = ROOT / f"stale/{slug}_bass_family_verdict.c23_scope_extension_disclosed.json"
        assert expected.exists(), f"missing stale sibling: {expected}"


def test_07_all_verdicts_in_frozen_enum():
    ENUM = {"SF2_CONFIRMED", "SF2_RULED_OUT", "STILL_INDETERMINATE"}
    for sha16 in SONGS:
        v = _load(sha16)["verdict"]
        assert v in ENUM, f"{sha16}: {v} not in frozen enum {ENUM}"


def test_08_no_non_cg_sf2_confirmed_this_cycle():
    """c26 absolute discipline: NO SF2_CONFIRMED on non-CG bass. Escalation
    `_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy` remains
    blocked_on_operator=true per c24.
    """
    for sha16 in SONGS:
        assert _load(sha16)["verdict"] != "SF2_CONFIRMED", \
            f"{sha16}: SF2_CONFIRMED forbidden this cycle (operator scope not extended)"


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
