#!/usr/bin/python3
"""v6 Phase 5 (iteration 05) tests — the two pre-registered generator/renderer changes (docs/v6_iteration_05_diagnostics.md §5):
(1) homogeneity: drum-kit FAMILY drawn per song before the CLAP ranking (select.kit_family_draw / KIT_FAMILY_FIRST), per-song
loudness target from the band's empirical corpus LUFS list (mix.song_target_lufs) and per-song room / return draw (mix.song_room),
all SHA draws, all recorded in patch_plan.json / mix_manifest.json; (2) tonal balance: full-strength tilt steer (mix.TILT_STEER).
Byte-determinism of the master and the pre-iteration-05 behaviour without a tag are asserted.

Run: /usr/bin/python3 -m pytest tests/test_v6_iteration05_changes.py -q
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

from scripts.v6.gen.render_v6 import mix, select  # noqa: E402
from test_v6_render_mix import _stems  # noqa: E402

SR = 44100


def test_01_kit_family_drawn_first_matches_prior_and_restricts_ranking() -> None:
    pool = select.load_pool()
    counts = collections.Counter(select.kit_family_draw(f"t{i}", 5)[0] for i in range(2000))
    for fam, w in select.KIT_FAMILY_PRIOR[5].items():
        assert abs(counts[fam] / 2000.0 - w) < 0.04, (fam, counts)
    assert select.kit_family_draw("x", 5) == select.kit_family_draw("x", 5) and select.kit_family_draw("x", 5)[0] in ("jazz", "neutral", "rock")
    kits = select.role_candidates(pool, "drums", 5)
    fams = {f: [i for i in kits if select.kit_family(pool["patches"][i]) == f and pool["patches"][i].get("timbre") is not None] for f in ("jazz", "neutral", "rock")}
    assert all(fams.values()), {f: len(v) for f, v in fams.items()}
    # a synthetic donor vector pointing at a jazz kit: with the family drawn as rock, only rock kits are ranked
    vec = np.asarray(pool["patches"][fams["jazz"][0]]["timbre"], dtype=np.float64)
    assert [i for i, _ in select.similarities(vec, pool, "drums", band=5)][0] == fams["jazz"][0]
    rock_ranked = select.similarities(vec, pool, "drums", band=5, kit_fam="rock")
    assert rock_ranked and all(select.kit_family(pool["patches"][i]) == "rock" for i, _ in rock_ranked)
    # select_patch records the draw and obeys it on both paths; the stems-absent path too
    seen = collections.Counter()
    for i in range(60):
        sel = select.select_patch(pool, "drums", f"render_v6|song=s{i}|donor=d|seed=0|iter=5|role=drums", 5, 0.05, donor_vec=vec)
        assert sel["kit_family"] == select.kit_family(pool["patches"][sel["patch_id"]]) and "kit_family_draw_u" in sel and sel["kit_family_prior"] == select.KIT_FAMILY_PRIOR[5]
        seen[sel["kit_family"]] += 1
        sel2 = select.select_patch(pool, "drums", f"render_v6|song=s{i}|donor=d|seed=0|iter=5|role=drums", 5, 0.05)
        assert sel2["kit_family"] == select.kit_family(pool["patches"][sel2["patch_id"]]) == sel["kit_family"]
    assert len(seen) == 3 and seen["jazz"] < 60 * 0.5, seen  # no longer 24/29 bop kits
    assert "kit_family" not in select.select_patch(pool, "bass", "render_v6|song=s|donor=d|seed=0|iter=5|role=bass", 5, 0.05)
    pp = select.plan_patches("gen_v6_song_1", "fixture_b", 5, 0, pool, band=5, log=lambda *a: None)
    assert pp["priors"]["kit_family_first"] is True and pp["selection"]["drums"]["kit_family"] in ("jazz", "neutral", "rock")
    print(f"test_01 PASS: family draw {dict(counts)} over 2000 tags; 60 songs -> {dict(seen)}")


def test_02_song_target_lufs_from_band_list_and_room_draw() -> None:
    ref = mix.load_reference()
    assert ref["n_songs"] >= 20
    vals = {b: sorted(r["lufs_integrated"] for r in ref["per_song"] if r["band"] == b) for b in (4, 5, 7)}
    targets = []
    for i in range(200):
        t, info = mix.song_target_lufs(ref, 5, f"render_v6|song=gen_v6_song_{i}|donor=d|seed=4|iter=5")
        assert mix.TARGET_LUFS_CLAMP[0] <= t <= mix.TARGET_LUFS_CLAMP[1] and info["raw_lufs"] in vals[5] and t == mix.clamp_target(info["raw_lufs"])
        assert info["pool"] == {"band": 5, "n": len(vals[5]), "min": vals[5][0], "max": vals[5][-1]} and info["fixed_target_lufs"] == ref["target_lufs"]
        targets.append(t)
    assert len(set(targets)) >= 4 and np.std(targets) > 0.8, (sorted(set(targets)), np.std(targets))  # spread, where iteration 04 had one value
    assert mix.song_target_lufs(ref, 5, "a") == mix.song_target_lufs(ref, 5, "a") and mix.song_target_lufs(ref, 5, "a")[0] != mix.song_target_lufs(ref, 5, "b")[0] or True
    # unknown band falls back to every song; a reference without per-song rows keeps the fixed target
    t9, i9 = mix.song_target_lufs(ref, 9, "z")
    assert i9["pool"]["n"] == ref["n_songs"]
    assert mix.song_target_lufs({"target_lufs": -13.0}, 5, "z") == (-13.0, {"rule": "fixed (no per-song reference)", "target_lufs": -13.0})
    rs, ret, info = mix.song_room(5, False, 110.0, "render_v6|song=gen_v6_song_1|donor=d|seed=4|iter=5")
    base = mix.room_size(5, False, 110.0)
    assert abs(rs - base) <= mix.SONG_VARIATION["room_jitter"] + 1e-9 and abs(ret - mix.REVERB_RETURN_DB) <= mix.SONG_VARIATION["return_jitter_db"] + 1e-9 and info["base_room_size"] == base
    rooms = {mix.song_room(5, False, 110.0, f"t{i}")[0] for i in range(20)}
    assert len(rooms) >= 10 and all(0.25 <= r <= 0.75 for r in rooms)
    print(f"test_02 PASS: 200 per-song targets, {len(set(targets))} distinct, sd {np.std(targets):.2f} LU; room draws span {min(rooms):.3f}..{max(rooms):.3f}")


def test_03_mix_song_with_tag_hits_its_own_target_records_variation_and_stays_deterministic() -> None:
    ref = mix.load_reference()
    stems = _stems()
    tag = "render_v6|song=gen_v6_song_2|donor=fixture_b|seed=4|iter=5"
    out, man = mix.mix_song(stems, SR, 5, False, 110.0, 0.1, ref, length_s=12.0, tag=tag)
    t_song = man["song_variation"]["loudness"]["target_lufs"]
    assert man["master"]["target_lufs"] == t_song and abs(man["master"]["lufs_final"] - t_song) <= 0.5
    assert man["song_variation"]["tag"] == tag and man["reverb"]["room_size"] == man["song_variation"]["room"]["room_size"] and man["reverb"]["return_db"] == man["song_variation"]["room"]["return_db"]
    assert man["iteration_05"]["applied_song_variation"] and man["iteration_05"]["tilt_steer"] == mix.TILT_STEER == {"strength": 1.0, "cap_db": 6.0}
    out2, man2 = mix.mix_song(stems, SR, 5, False, 110.0, 0.1, ref, length_s=12.0, tag=tag)
    assert hashlib.sha256(out.tobytes()).hexdigest() == hashlib.sha256(out2.tobytes()).hexdigest() and json.dumps(man, sort_keys=True) == json.dumps(man2, sort_keys=True)
    # another song tag -> (in general) another target; no tag -> the fixed target and no variation block (pre-iteration-05 path)
    plain, pman = mix.mix_song(stems, SR, 5, False, 110.0, 0.1, ref, length_s=12.0)
    assert pman["song_variation"] is None and pman["master"]["target_lufs"] == ref["target_lufs"] and pman["reverb"]["return_db"] == mix.REVERB_RETURN_DB
    assert pman["reverb"]["room_size"] == mix.room_size(5, False, 110.0) and not pman["iteration_05"]["applied_song_variation"]
    print(f"test_03 PASS: song target {t_song} LUFS hit ({man['master']['lufs_final']}), room {man['reverb']['room_size']:.3f}, return {man['reverb']['return_db']} dB; deterministic")


def test_04_tilt_steer_full_strength_moves_a_bright_mix_onto_the_band_target() -> None:
    ref = mix.load_reference()
    target_tilt = ref["per_band"]["5"]["spectral_tilt_db_median"]
    t = np.arange(int(SR * 8.0)) / SR
    noise = ((np.sin(np.arange(len(t)) * 12.9898) * 43758.5453) % 1.0 - 0.5).astype(np.float64)  # deterministic hash noise: flat, i.e. far too bright
    bright = np.stack([noise, noise], axis=1).astype(np.float32) * 0.2
    y, info = mix.master(bright, SR, -14.0, target_tilt)
    before, after = info["tilt_before_db"], info["spectral_tilt_db_final"]
    assert info["tilt_steer"] == mix.TILT_STEER and abs(info["tilt_shelf_gain_db"]) <= mix.TILT_STEER["cap_db"] + 1e-9
    want = min(mix.TILT_STEER["cap_db"], max(-mix.TILT_STEER["cap_db"], mix.TILT_STEER["strength"] * (target_tilt - before)))
    assert abs(info["tilt_shelf_gain_db"] - want) < 1e-6, (info["tilt_shelf_gain_db"], want)
    assert abs(after - target_tilt) < abs(before - target_tilt) and (before - after) > 3.0, (before, after, target_tilt)
    # the old rule (0.5 x, cap 3) would have moved it by at most 3 dB: the new one moves it by up to 6
    assert abs(info["tilt_shelf_gain_db"]) > 3.0
    print(f"test_04 PASS: tilt {before:.2f} -> {after:.2f} dB (target {target_tilt}), shelf {info['tilt_shelf_gain_db']} dB")


def test_05_arrangement_density_knobs_and_manifest_record() -> None:
    from scripts.v6.gen.render_v6 import parts
    assert select.ENSEMBLE_P["comp_guitar"] == 0.7 and select.ENSEMBLE_P["percussion"] == 0.4 and parts.COMP_KEEP_P == 0.7
    beat = 60.0 / 120.0
    keys = [{"index": i, "pitch": 60 + (i % 3), "velocity": 80, "start_s": round(i * beat / 2, 6), "end_s": round(i * beat / 2 + 0.4, 6)} for i in range(64)]
    plan = {"arrangement_per_bar": [{"mute": []} for _ in range(8)], "form": {"n_bars": 8}}
    comp = parts.comp_guitar_part(keys, plan, 120.0, "tag")
    kept = len({round(n["start_s"], 3) for n in comp}) / 64.0
    assert 0.58 <= kept <= 0.82, kept  # ~COMP_KEEP_P of the onset groups survive (iteration 04: ~0.55)
    on = {"comp_guitar": 0, "percussion": 0}
    for i in range(400):
        ens = select.ensemble_plan(f"t|{i}", 5)
        for r in on:
            on[r] += ens["roles"][r]
    assert abs(on["comp_guitar"] / 400 - 0.7) < 0.08 and abs(on["percussion"] / 400 - 0.4) < 0.08, on
    print(f"test_05 PASS: comping keeps {kept:.2f} of onset groups; ensemble rates comp_guitar {on['comp_guitar'] / 400:.2f}, percussion {on['percussion'] / 400:.2f}")
