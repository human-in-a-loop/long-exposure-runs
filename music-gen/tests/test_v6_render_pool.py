#!/usr/bin/python3
"""v6 Phase 4 tests — patch pool builder: GM drum-map check drops kits without kick/snare/hat, sfz/sf2 key scanning,
pool_v6.json integrity (roles only hold deterministic patches, timbre vectors unit-norm, paths exist).

Run: /usr/bin/python3 -m pytest tests/test_v6_render_pool.py -q
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

from scripts.v6.patches import build_pool, sf2_keymap  # noqa: E402

FLUID = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
POOL = _ROOT / "scripts" / "v6" / "patches" / "pool_v6.json"


def _fake_sfz(path: Path, keys: list) -> None:
    body = "\n".join(f"<region> key={k} sample=s{k}.wav" for k in keys)
    path.write_text("<control> hint_ram_based=1\n<group> loop_mode=one_shot lovel=1 hivel=127\n" + body + "\n")


def test_01_gm_drum_check_and_sfz_scan() -> None:
    assert sf2_keymap.gm_drum_check([36, 38, 42, 46, 49, 51, 45, 47, 50])["ok"]
    assert sf2_keymap.gm_drum_check([36, 40, 42]) == {"ok": True, "missing_required": [], "present_optional": [], "missing_optional": ["open_hat", "crash", "ride", "tom_low", "tom_mid", "tom_high"]}
    assert sf2_keymap.gm_drum_check(list(range(48, 67)))["missing_required"] == ["kick", "snare", "closed_hat"]
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "kit.sfz"
        _fake_sfz(p, [35, 36, 38, 42, 46, 49])
        assert build_pool.sfz_keys(p) == [35, 36, 38, 42, 46, 49]
        p2 = Path(td) / "range.sfz"
        p2.write_text("<group> lokey=c2 hikey=e2 sample=a.wav\n<region> pitch_keycenter=d2\n")
        assert build_pool.sfz_keys(p2) == [36, 37, 38, 39, 40]
    keys = sf2_keymap.preset_keys(FLUID, 128, 0)
    assert 36 in keys and 38 in keys and 42 in keys and sf2_keymap.gm_drum_check(keys)["ok"]
    assert sf2_keymap.preset_velocity_layers(FLUID, 128, 0) >= 1
    print("test_01 PASS: GM drum check, sfz key scan (key=, lokey/hikey, note names), FluidR3 bank-128 keys parsed")


def test_02_build_pool_drops_kits_without_kick_snare_hat() -> None:
    with tempfile.TemporaryDirectory() as td:
        good, bad = Path(td) / "good.sfz", Path(td) / "bad.sfz"
        _fake_sfz(good, [36, 38, 42, 46, 49, 51, 45, 47, 50])
        _fake_sfz(bad, list(range(48, 67)))
        inv = {"libraries": [
            {"slug": "fake_kits", "format": "sfz", "license": {"id": "CC0-1.0"}, "instruments": [
                {"name": "Good Kit", "role": "drums", "backend": "sfz", "path": str(good), "sfz_scan": {"velocity_layers": 2, "lokey": 36, "hikey": 51}, "render": {"status": "ok"}},
                {"name": "Bad Kit (DrumGizmo map)", "role": "drums", "backend": "sfz", "path": str(bad), "sfz_scan": {"velocity_layers": 2, "lokey": 48, "hikey": 66}, "render": {"status": "ok"}},
                {"name": "Silent Kit", "role": "drums", "backend": "sfz", "path": str(good), "sfz_scan": {}, "render": {"status": "silent"}}]},
            {"slug": "fluidr3_gm", "format": "sf2", "license": {"id": "MIT"}, "instruments": [
                {"name": "Standard [128:0]", "role": "drums", "backend": "sf2", "path": FLUID, "bank": 128, "program": 0, "render": {"status": "ok"}},
                {"name": "Rhodes EP [0:4]", "role": "electric_piano", "backend": "sf2", "path": FLUID, "bank": 0, "program": 4, "render": {"status": "ok"}}]},
            {"slug": "surge_xt", "format": "dawdreamer", "license": {"id": "GPL-3.0-only"}, "instruments": [
                {"name": "Surge XT: Pad 1", "role": "pad", "backend": "dawdreamer", "plugin": "/x.vst3", "preset": "/p.fxp", "path": "/p.fxp", "deterministic": False, "render": {"status": "ok"}}]}]}
        pool = build_pool.build_pool(inv, timbre=False, log=lambda *a: None)
    dropped = {d["id"]: d["reason"] for d in pool["dropped"]}
    assert "fake_kits__Bad_Kit_DrumGizmo_map" in dropped and "kick" in dropped["fake_kits__Bad_Kit_DrumGizmo_map"]
    assert "fake_kits__Silent_Kit" in dropped
    assert pool["roles"]["drums"] == ["fake_kits__Good_Kit", "fluidr3_gm__Standard_128_0"]
    assert pool["roles"]["keys"] == ["fluidr3_gm__Rhodes_EP_0_4"] and pool["roles"]["melody"] == ["fluidr3_gm__Rhodes_EP_0_4"]
    assert pool["roles"]["pad"] == [] and pool["audition"]["pad"] == ["surge_xt__Surge_XT_Pad_1"]
    e = pool["patches"]["fluidr3_gm__Standard_128_0"]
    assert e["gm_drum_check"]["ok"] and e["bank"] == 128 and e["note_range"][0] <= 36 and e["deterministic"]
    assert pool["patches"]["fake_kits__Good_Kit"]["velocity_layers"] == 2
    print(f"test_02 PASS: pool builder dropped {sorted(dropped)}; kept GM-mapped kits; dawdreamer -> audition only")


def test_03_pool_v6_json_integrity() -> None:
    assert POOL.exists(), "run scripts/v6/patches/build_pool.py"
    pool = json.loads(POOL.read_text())
    P = pool["patches"]
    assert pool["counts"]["patches"] >= 150 and all(pool["counts"]["per_role"][r] >= 1 for r in ("bass", "keys", "comp_guitar", "melody", "pad", "drums", "percussion"))
    assert "muldjord_kit__Muldjord_Kit_rock_stereo" in {d["id"] for d in pool["dropped"]}
    for role, ids in pool["roles"].items():
        for i in ids:
            e = P[i]
            assert e["deterministic"] and e["backend"] in ("sfz", "sf2") and role in e["roles"], i
            assert Path(e["path"]).exists(), e["path"]
            if e["backend"] == "sf2":
                assert isinstance(e["bank"], int) and isinstance(e["program"], int)
            if e["backend"] == "sfz":
                assert e["path"].endswith(".ram.sfz"), e["path"]
    for i in pool["roles"]["drums"]:
        assert P[i]["gm_drum_check"]["ok"], i
    n_t = 0
    for e in P.values():
        if e.get("timbre") is not None:
            assert len(e["timbre"]) == 512
            nrm = sum(x * x for x in e["timbre"]) ** 0.5
            assert abs(nrm - 1.0) < 0.01, (e["id"], nrm)
            n_t += 1
    assert n_t == pool["counts"]["patches"], "every patch has a CLAP timbre vector"
    for aud in pool["audition"].values():
        assert all(P[i]["backend"] == "dawdreamer" and not P[i]["deterministic"] for i in aud)
    print(f"test_03 PASS: pool_v6.json {pool['counts']['patches']} patches, per-role {pool['counts']['per_role']}, {n_t} timbre vectors unit-norm, audition {pool['counts']['per_role_audition']}")


if __name__ == "__main__":
    test_01_gm_drum_check_and_sfz_scan()
    test_02_build_pool_drops_kits_without_kick_snare_hat()
    test_03_pool_v6_json_integrity()
