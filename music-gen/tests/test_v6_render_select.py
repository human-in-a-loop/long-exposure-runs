#!/usr/bin/python3
"""v6 Phase 4 tests — patch selection: deterministic plans, temperature -> 0 picks the most similar patch, softmax draw
is a proper distribution, band priors cover every role, the donor-stem path (CLAP) finds the patch a stem was made with.

Run: /usr/bin/python3 -m pytest tests/test_v6_render_select.py -q
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

from scripts.v6.gen.render_v6 import select  # noqa: E402

POOL = select.load_pool()


def test_01_plan_is_deterministic_and_always_has_core_roles() -> None:
    a = select.plan_patches("gen_v6_song_1", "fixture_a", 1, 0, POOL, band=5, log=lambda *x: None)
    b = select.plan_patches("gen_v6_song_1", "fixture_a", 1, 0, POOL, band=5, log=lambda *x: None)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert all(a["ensemble"]["roles"][r] for r in ("bass", "drums", "keys", "melody"))
    assert set(a["selection"]) == {r for r, on in a["ensemble"]["roles"].items() if on}
    for role, sel in a["selection"].items():
        assert sel["patch_id"] in POOL["roles"][role] and sel["method"].startswith("band_prior") and sel["patch"]["deterministic"]
    c = select.plan_patches("gen_v6_song_1", "fixture_a", 2, 0, POOL, band=5, log=lambda *x: None)
    assert c["tag"] != a["tag"]  # the iteration is part of the seed tag
    mel = POOL["patches"][a["selection"]["melody"]["patch_id"]]["inventory_role"]
    assert mel == a["ensemble"]["melody_family"]
    # the ensemble probabilities are honoured in aggregate over many songs
    on = {r: 0 for r in select.ENSEMBLE_P}
    n = 400
    for i in range(n):
        ens = select.ensemble_plan(f"t|{i}", 5)
        for r in on:
            on[r] += ens["roles"][r]
    for r, p in select.ENSEMBLE_P.items():
        assert abs(on[r] / n - p) < 0.08, (r, on[r] / n, p)
    print(f"test_01 PASS: deterministic plan; core roles always on; melody family honoured; ensemble rates {dict((r, round(on[r] / n, 2)) for r in on)}")


def test_02_temperature_zero_prefers_most_similar() -> None:
    import numpy as np
    for pid, role in (("finger_bass_yr__Finger_Bass_YR", "bass"), ("fss_steel_string_guitar__FSS_Steel_String_Guitar", "comp_guitar"), ("avl_drumkits_sf2__AVL_Black_Pearl_4pc", "drums")):
        vec = np.asarray(POOL["patches"][pid]["timbre"], dtype=np.float64)
        sel = select.select_patch(POOL, role, "t", 5, temperature=0.0, donor_vec=vec)
        assert sel["patch_id"] == pid and sel["method"] == "clap_similarity_softmax_top5" and sel["similarity"] > 0.99, sel
        assert len(sel["candidates"]) == 5 and sel["candidates"][0]["id"] == pid
        warm = select.select_patch(POOL, role, "t", 5, temperature=0.05, donor_vec=vec)
        assert abs(sum(c["prob"] for c in warm["candidates"]) - 1.0) < 1e-6 and warm["candidates"][0]["prob"] == max(c["prob"] for c in warm["candidates"])
        assert warm["patch_id"] in {c["id"] for c in warm["candidates"]}
    chosen, cands, x = select.softmax_pick([("a", 0.9), ("b", 0.8), ("c", 0.1)], 1e-12, "tag")
    assert chosen == "a" and [c["prob"] for c in cands] == [1.0, 0.0, 0.0]
    # a hotter temperature flattens the distribution
    _, c1, _ = select.softmax_pick([("a", 0.9), ("b", 0.8)], 0.02, "tag")
    _, c2, _ = select.softmax_pick([("a", 0.9), ("b", 0.8)], 1.0, "tag")
    assert c1[0]["prob"] > c2[0]["prob"] > 0.5
    print("test_02 PASS: T->0 is the arg-max of the CLAP similarity; softmax probs sum to 1 and flatten with T")


def test_03_band_priors_cover_roles_and_lean() -> None:
    for band in (4, 5, 7):
        for role in select.ENSEMBLE_P:
            w = select.prior_weights(POOL, role, band)
            assert w and all(v > 0 for v in w.values()) and set(w) <= set(POOL["roles"][role])
    def mass(band, role, inv):
        w = select.prior_weights(POOL, role, band)
        t = sum(w.values())
        return sum(v for i, v in w.items() if POOL["patches"][i]["inventory_role"] == inv) / t
    assert mass(7, "bass", "synth_bass") < mass(4, "bass", "synth_bass")
    assert mass(7, "bass", "acoustic_bass") > mass(4, "bass", "acoustic_bass")
    assert mass(7, "pad", "strings_pad") > mass(4, "pad", "strings_pad")
    assert mass(4, "melody", "lead") > mass(7, "melody", "lead")
    w = select.prior_weights(POOL, "drums", 7)
    jazz = sum(v for i, v in w.items() if select.kit_family(POOL["patches"][i]) == "jazz") / sum(w.values())
    w4 = select.prior_weights(POOL, "drums", 4)
    assert jazz > sum(v for i, v in w4.items() if select.kit_family(POOL["patches"][i]) == "jazz") / sum(w4.values())
    assert select.band_for(6) in (5, 7) and select.donor_band("fixture_a")[0] == select.DEFAULT_BAND
    print("test_03 PASS: band priors defined for every role; 7 acoustic-leaning vs 4 synth-leaning; jazz kits favoured for band 7")


def test_04_donor_stem_path_uses_clap_and_finds_the_source_patch() -> None:
    src = _ROOT / "workspace" / "instruments" / POOL["patches"]["finger_bass_yr__Finger_Bass_YR"]["render_wav"]
    if not src.exists():
        print("test_04 SKIP: smoke render missing")
        return
    with tempfile.TemporaryDirectory() as td:
        stems = Path(td) / "stems"
        (stems / "deadbeefcafef00d").mkdir(parents=True)
        shutil.copyfile(src, stems / "deadbeefcafef00d" / "bass.wav")
        cache = Path(td) / "cache"
        pp = select.plan_patches("s", "deadbeefcafef00d", 1, 0, POOL, band=5, stems_root=stems, temperature=0.0, cache_dir=cache, log=lambda *x: None)
        pp2 = select.plan_patches("s", "deadbeefcafef00d", 1, 0, POOL, band=5, stems_root=stems, temperature=0.0, cache_dir=cache, log=lambda *x: None)
    assert pp["stems_found"] == {"bass": str(stems / "deadbeefcafef00d" / "bass.wav")}
    b = pp["selection"]["bass"]
    assert b["method"] == "clap_similarity_softmax_top5" and b["stem_used"] == "bass" and b["similarity"] > 0.9
    assert b["patch_id"] == "finger_bass_yr__Finger_Bass_YR", b["candidates"]
    assert pp["selection"]["keys"]["method"].startswith("band_prior") and pp["selection"]["keys"]["stem_used"] is None  # no 'other' stem
    assert json.dumps(pp, sort_keys=True) == json.dumps(pp2, sort_keys=True)  # cache hit gives the same plan
    print(f"test_04 PASS: donor bass stem -> CLAP -> {b['patch_id']} (sim {b['similarity']:.3f}); other roles fall back to the band prior; cached run identical")


if __name__ == "__main__":
    test_01_plan_is_deterministic_and_always_has_core_roles()
    test_02_temperature_zero_prefers_most_similar()
    test_03_band_priors_cover_roles_and_lean()
    test_04_donor_stem_path_uses_clap_and_finds_the_source_patch()
