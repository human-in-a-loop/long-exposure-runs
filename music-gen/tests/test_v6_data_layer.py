#!/usr/bin/python3
"""v6 Phase 0 data-layer tests — manifest (29 songs, bands, tiers), tempo_v6 on synthetic clicks (97 BPM +/- 1; half-
and double-time clicks resolve to 97), bootstrap creates every required v5 input, donor map validates against
generate_v5's spec keys (AST-scanned, no audio import), profiles' sf2 sha matches the on-disk soundfont.

Run: /usr/bin/python3 tests/test_v6_data_layer.py        (plain script: every test_* function runs, PASS/FAIL per test)
     /usr/bin/python3 -m pytest tests/test_v6_data_layer.py -q   (also pytest-compatible)
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from scripts.v6 import v6_data_common as C  # noqa: E402
from scripts.v6 import corpus_manifest_v6 as M  # noqa: E402
from scripts.v6 import bootstrap_v5_inputs as B  # noqa: E402

PY = "/usr/bin/python3"
SR = 22050
EXPECTED_BANDS = {"4": 9, "5": 16, "7": 4}
V5_KEYS = ("sha16", "audio_sha256", "audio_path", "duration_s", "band", "title", "video_id", "is_focus_song",
           "in_v5_corpus", "v5_tier", "v5_priority_rank", "asset_inventory")

_MANIFEST_CACHE: dict = {}


def _manifest() -> dict:
    """Build once per test session (29 sha256s + ffprobe); prefer the on-disk manifest when it is current."""
    if "m" not in _MANIFEST_CACHE:
        p = C.MANIFEST_V5
        if p.exists():
            m = json.loads(p.read_text())
            if m.get("sources", {}).get("receipts_sha256") == C.sha256_file(C.RECEIPTS) and m["summary"]["n_songs"] == 29:
                _MANIFEST_CACHE["m"] = m
        if "m" not in _MANIFEST_CACHE:
            _MANIFEST_CACHE["m"] = M.build_manifest(C.WS, C.RECEIPTS, C.RATINGS_TSV, verify_sha=True, probe_duration=True)
    return _MANIFEST_CACHE["m"]


# ------------------------------------------------------------------------------------------------------ manifest
def test_01_manifest_29_songs_bands_tiers_order() -> None:
    m = _manifest()
    songs = m["songs"]
    assert len(songs) == 29, len(songs)
    assert m["summary"]["band_counts"] == EXPECTED_BANDS, m["summary"]["band_counts"]
    assert m["summary"]["tier_counts"] == {"band4": 9, "band5": 13, "band7": 4, "focus": 3}, m["summary"]["tier_counts"]
    for s in songs:
        for k in V5_KEYS:
            assert k in s, (s["sha16"], k)
        assert s["in_v5_corpus"] is True
        assert s["v5_tier"] in ("focus", "band7", "band5", "band4")
        assert s["v5_tier"] == ("focus" if s["sha16"] in C.FOCUS else f"band{s['band']}")
        assert s["sha16"] == s["audio_sha256"][:16]
        assert s["band"] in (4, 5, 7)
    ranks = [s["v5_priority_rank"] for s in songs]
    assert ranks == list(range(1, 30)), ranks
    assert [s["sha16"] for s in songs[:3]] == list(C.FOCUS_ORDER), "focus songs (WIG, Rome, Disco A) must come first"
    tiers = [s["v5_tier"] for s in songs]
    assert tiers == ["focus"] * 3 + ["band7"] * 4 + ["band5"] * 13 + ["band4"] * 9, tiers
    for band in (7, 5, 4):  # by playlist position within a band
        pos = [s["position"] for s in songs if s["v5_tier"] == f"band{band}"]
        assert pos == sorted(pos), (band, pos)
    assert "31a164f845f8e27e" not in {s["sha16"] for s in songs} and "88d247468cb6d49f" not in {s["sha16"] for s in songs}, "CG / PD must be absent"
    assert abs(m["summary"]["total_duration_s"] - sum(s["duration_s"] for s in songs)) < 1e-6
    assert m["env_pin_sha256"] == C.ENV_PIN_SHA256 and m["schema_version"] == 2
    print(f"test_01 PASS: 29 songs, bands {m['summary']['band_counts']}, tiers {m['summary']['tier_counts']}, total {m['summary']['total_duration_hms']}")


def test_02_manifest_on_disk_byte_identical_copies() -> None:
    assert C.MANIFEST_V5.exists() and C.MANIFEST_V6.exists(), "run scripts/v6/corpus_manifest_v6.py first"
    assert C.MANIFEST_V5.read_bytes() == C.MANIFEST_V6.read_bytes(), "v5 and v6 manifest copies differ"
    m = json.loads(C.MANIFEST_V5.read_text())
    txt = C.canonical_json(m)
    assert txt == C.MANIFEST_V5.read_text(), "manifest is not canonical (sorted keys, indent 2, trailing newline)"
    print(f"test_02 PASS: data/v5 and data/v6 manifest copies byte-identical ({hashlib.sha256(txt.encode()).hexdigest()[:16]})")


# --------------------------------------------------------------------------------------------------------- tempo
def _click_track(bpm: float, dur: float = 60.0, accent=None, sr: int = SR):
    import numpy as np
    y = np.zeros(int(dur * sr), dtype=np.float32)
    period = 60.0 / bpm
    n = int(0.02 * sr)
    tone = (np.sin(2 * np.pi * 1000 * np.arange(n) / sr) * np.exp(-np.arange(n) / (0.004 * sr))).astype(np.float32)
    t, i = 0.0, 0
    while t < dur - 0.05:
        amp = 1.0 if accent is None else accent[i % len(accent)]
        n0 = int(t * sr)
        y[n0:n0 + n] += amp * tone
        t += period
        i += 1
    return y


def test_03_tempo_click_97_and_octave_resolution() -> None:
    from scripts.v6 import tempo_v6 as T
    r = T.estimate_from_signal(_click_track(97.0), SR, "click97")
    assert abs(r["bpm_v5"] - 97.0) <= 1.0, r["bpm_v5"]
    assert r["confidence"] in ("high", "medium"), r["confidence"]
    assert r["estimator_agreement"]["n_agree"] >= 2
    assert r["override"]["applied"] is False
    # accented (strong/weak) 97 BPM click: must not drop to 48.5
    r2 = T.estimate_from_signal(_click_track(97.0, accent=[1.0, 0.35]), SR, "click97_accent")
    assert abs(r2["bpm_v5"] - 97.0) <= 1.0, r2["bpm_v5"]
    # half-time click (48.5 BPM, below the band): the raw beat_track / prior say ~48.5; served value must be the double, 97
    r3 = T.estimate_from_signal(_click_track(48.5), SR, "click48.5")
    raw3 = r3["estimators_raw"]
    assert any(abs(v - 48.5) / 48.5 <= 0.04 for v in raw3.values()), f"probe not half-time: {raw3}"
    assert abs(r3["bpm_v5"] - 97.0) <= 1.5, (r3["bpm_v5"], raw3, r3["confidence"])
    # double-time click (194 BPM, above the band): served value must be the half, 97
    r4 = T.estimate_from_signal(_click_track(194.0), SR, "click194")
    assert abs(r4["bpm_v5"] - 97.0) <= 1.5, (r4["bpm_v5"], r4["estimators_raw"])
    assert T.fold_to_band(48.5) == 97.0 and T.fold_to_band(194.0) == 97.0 and T.fold_to_band(100.0) == 100.0
    assert T.octave_within(161.5, 79.75) and T.octave_within(99.38, 100.1) and not T.octave_within(120.0, 80.0)
    print(f"test_03 PASS: click 97 -> {r['bpm_v5']:.3f} ({r['confidence']}); accented -> {r2['bpm_v5']:.3f}; "
          f"48.5 click -> {r3['bpm_v5']:.3f} ({r3['confidence']}, raw {raw3}); 194 click -> {r4['bpm_v5']:.3f}")


def test_04_tempo_outputs_and_validation() -> None:
    summ = C.V6_CORPUS / "tempo_v6_summary.json"
    assert summ.exists(), "run scripts/v6/tempo_v6.py first"
    s = json.loads(summ.read_text())
    assert s["n_songs"] == 29
    val = s["validation"]
    assert val["all_pass"] is True, val
    wig, rome, disco = val["252eb21ce7df7328"], val["51e433ade2a845e1"], val["cdd2717e52820ff6"]
    assert abs(wig["bpm_v5"] - 99.38) / 99.38 <= 0.02 and abs(rome["bpm_v5"] - 152.0) / 152.0 <= 0.02
    assert disco["bpm_v5"] == 120.272335
    for song in _manifest()["songs"]:
        p5 = C.V5_CORPUS / song["sha16"] / "tempo_v5.json"
        p6 = C.V6_CORPUS / song["sha16"] / "tempo_v6.json"
        assert p5.exists() and p6.exists(), song["sha16"]
        v5 = json.loads(p5.read_text())
        v6 = json.loads(p6.read_text())
        assert isinstance(v5["bpm_v5"], float) and 70.0 <= v5["bpm_v5"] <= 180.0, (song["sha16"], v5["bpm_v5"])
        assert v5["bpm_v5"] == v6["bpm_v5"] and v5["env_pin_sha256"] == C.ENV_PIN_SHA256
        assert v6["confidence"] in ("high", "medium", "low", "ambiguous", "override"), v6["confidence"]
        assert v6["audio_sha256"] == song["audio_sha256"]
    disco6 = json.loads((C.V6_CORPUS / "cdd2717e52820ff6" / "tempo_v6.json").read_text())
    assert disco6["override"]["applied"] is True and disco6["confidence"] == "override"
    assert C.load_tempo_overrides()["cdd2717e52820ff6"] == 120.272335
    tsv = (C.V6_CORPUS / "tempo_v6_summary.tsv").read_text().splitlines()
    assert len(tsv) == 30 and tsv[0].split("\t")[:5] == ["rank", "sha16", "title", "band", "bpm_v5"]
    assert (C.V5_CORPUS / "tempo_v5_summary.tsv").read_text() == "\n".join(tsv) + "\n"
    print(f"test_04 PASS: 29 tempo_v5.json + tempo_v6.json; validation {{WIG {wig['bpm_v5']}, Rome {rome['bpm_v5']}, Disco A {disco['bpm_v5']}}}; "
          f"confidence tally {s['confidence_tally']}; flags {s.get('flag_tally')}")


# ------------------------------------------------------------------------------------------------------ bootstrap
def _spec_keys_read_by_generate_v5() -> set[str]:
    """AST scan of scripts/v5/generate_v5.py for spec["k"] / spec.get("k") (the donor-map spec keys it reads)."""
    tree = ast.parse(Path("scripts/v5/generate_v5.py").read_text())
    keys: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == "spec" \
                and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
            keys.add(node.slice.value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get" \
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "spec" and node.args \
                and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            keys.add(node.args[0].value)
    return keys


def test_05_bootstrap_creates_every_required_input_in_tmp_ws() -> None:
    with tempfile.TemporaryDirectory(prefix="v6_bootstrap_") as td:
        ws = Path(td)
        (ws / "data/v5/corpus").mkdir(parents=True)
        shutil.copy(C.MANIFEST_V5, ws / "data/v5/corpus/corpus_manifest.json")
        r = subprocess.run([PY, "scripts/v6/bootstrap_v5_inputs.py", "--ws", str(ws)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        sha16s = [s["sha16"] for s in _manifest()["songs"]]
        req = B.required_paths(ws, sha16s)
        missing = [str(p.relative_to(ws)) for p in req if not p.exists()]
        assert not missing, missing
        assert len(req) == 15 + 1 + 2 * 29, len(req)
        # exact consumer keys
        blocked = json.loads((ws / "data/v5/corpus/recanonicalization_blocked.json").read_text())
        assert blocked["blocked_songs"] == {} and blocked["unblocked_c86"] == {}
        prereg = json.loads((ws / "data/v5/corpus/content_gate_prereg_c84.json").read_text())
        assert "rules" in prereg and prereg["expected"]["blocked"] == []
        res = json.loads((ws / "data/v5/corpus/tempo_f4_operator_resolution_c86.json").read_text())
        assert res["adopted_bpm"] == {"cdd2717e52820ff6": 120.272335} and res["authority"] == "OPERATOR"
        assert set(res["guidance"]) >= {"path", "sha256"} and set(res["supersedes"]) >= {"path", "sha256"}
        ov = json.loads((ws / "data/v5/corpus/tempo_overrides_c86.json").read_text())
        assert ov == {"cdd2717e52820ff6": 120.272335} and all(isinstance(float(v), float) for v in ov.values())
        for name in ("eligible_c84", "eligible_c86"):
            e = json.loads((ws / f"data/v5/rules/{name}.json").read_text())
            assert e["gate"]["used"] == sha16s and e["gate"]["late_landed_deferred"] == []
        comp = json.loads((ws / "data/v5/rules/comping_prereg_c87.json").read_text())
        assert comp["thresholds"] == {"min_songs": 8, "min_bars_with_onsets_per_song": 16, "pooled_max_slot_mass_lt": 0.5, "chord_window_ms": 30}
        assert sorted(comp["enum"]) == sorted(["COMPING_NON_DEGENERATE", "COMPING_DEGENERATE"])
        sc = json.loads((ws / "data/v5/gen/stall_counter.json").read_text())
        assert sc["iterations"] == 0 and sc["budget"] == 12 and sc["history"] == []
        assert (ws / "data/v5/logs").is_dir()
        for p in ("harmony_prereg_c84", "groove_prereg_c84"):
            assert json.loads((ws / f"data/v5/rules/{p}.json").read_text())["written_before_any_output"] is True
        for p in ("form_prereg_c85", "f2_prereg_c86", "f3_prereg_c88", "f5_prereg_c89"):
            assert json.loads((ws / f"data/v5/gen/{p}.json").read_text())["env_pin_sha256"] == C.ENV_PIN_SHA256
        # idempotent: second run changes nothing (byte compare every created file), preregs kept
        before = {p: p.read_bytes() for p in req if p.is_file()}
        r2 = subprocess.run([PY, "scripts/v6/bootstrap_v5_inputs.py", "--ws", str(ws)], capture_output=True, text=True)
        assert r2.returncode == 0 and "kept" in r2.stdout and "created" not in r2.stdout.split("bootstrap:")[-1], r2.stdout
        after = {p: p.read_bytes() for p in req if p.is_file()}
        assert before == after, "second bootstrap run changed bytes"
        r3 = subprocess.run([PY, "scripts/v6/bootstrap_v5_inputs.py", "--ws", str(ws), "--check"], capture_output=True, text=True)
        assert r3.returncode == 0 and "74/74" in r3.stdout, r3.stdout
    print(f"test_05 PASS: bootstrap created {len(req)} required inputs in a tmp workspace, idempotent on re-run")


def test_06_donor_map_matches_generate_v5_expectations() -> None:
    dm_p = Path("data/v4/gen/donor_profile_map.json")
    assert dm_p.exists(), "run scripts/v6/bootstrap_v5_inputs.py first"
    dm = json.loads(dm_p.read_text())
    assert "songs" in dm and "interpolation_demo" in dm
    specs = dm["songs"]
    assert len(specs) == 29 and dm["n_donors"] == 29
    keys_read = _spec_keys_read_by_generate_v5()
    assert {"donor_song_sha16", "generated_song_id", "donor_bass_profile_relpath", "donor_drums_profile_relpath", "donor_song_name"} <= keys_read, keys_read
    man_order = [s["sha16"] for s in _manifest()["songs"]]
    assert [s["donor_song_sha16"] for s in specs] == man_order, "donor order must be manifest priority (focus first)"
    assert [s["generated_song_id"] for s in specs] == [f"gen_v6_song_{i:02d}" for i in range(1, 30)]
    assert specs[0]["donor_song_name"] == "What If I Go"
    for s in specs:
        for k in keys_read:
            assert k in s, (s["generated_song_id"], k)
        for rel_key in ("donor_bass_profile_relpath", "donor_drums_profile_relpath"):
            p = Path(s[rel_key])
            assert p.exists(), p
            prof = json.loads(p.read_text())
            assert prof["family"] == "sf2"
            ident = prof["identity"]
            for k in ("sf2_path", "sf2_sha256", "bank", "program"):  # generate_v5.py:639-642 + replay.py:52-56
                assert k in ident, (p, k)
            assert prof["params"]["sample_rate"] == 44100 and prof["params"]["gain"] == 0.8
            assert ident["sf2_path"] == C.SF2_PATH
        bass = json.loads(Path(s["donor_bass_profile_relpath"]).read_text())
        drums = json.loads(Path(s["donor_drums_profile_relpath"]).read_text())
        assert bass["identity"]["program"] == 33 and bass["identity"]["bank"] == 0
        assert drums["identity"]["program"] == 0 and drums["identity"]["bank"] == 128
        assert bass["song_sha16"] == drums["song_sha16"] == s["donor_song_sha16"]
    # generate_v5 reads gen_id via .replace("gen_v4_", "gen_v5_"): gen_v6 ids pass through unchanged
    assert specs[0]["generated_song_id"].replace("gen_v4_", "gen_v5_") == "gen_v6_song_01"
    print(f"test_06 PASS: 29 donor specs carry every spec key generate_v5.py reads {sorted(keys_read)}; profiles present with identity/params")


def test_07_profiles_sf2_sha_matches_disk() -> None:
    sf2 = Path(C.SF2_PATH)
    assert sf2.exists(), f"{C.SF2_PATH} missing"
    on_disk = C.sha256_file(sf2)
    assert on_disk == C.SF2_SHA256_PINNED, (on_disk, C.SF2_SHA256_PINNED)
    n = 0
    for p in sorted(Path("data/v4/profiles").glob("*/*.json")):
        prof = json.loads(p.read_text())
        assert prof["identity"]["sf2_sha256"] == on_disk, p
        assert prof["deps_sha256"]["sf2_sha256"] == on_disk, p
        n += 1
    assert n == 58, n
    dm = json.loads(Path("data/v4/gen/donor_profile_map.json").read_text())
    assert dm["profile_policy"]["sf2_sha256"] == on_disk
    print(f"test_07 PASS: {n} profiles pin sf2 sha {on_disk[:16]}... == on-disk FluidR3_GM.sf2")


def test_08_env_pin_and_discipline() -> None:
    pins = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
            "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
    assert C.PINS == pins
    assert hashlib.sha256(json.dumps(pins, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == C.ENV_PIN_SHA256
    for script in ("corpus_manifest_v6.py", "tempo_v6.py", "bootstrap_v5_inputs.py", "velocity_v6.py", "form_plan_v6.py", "generate_v6.py", "v6_data_common.py"):
        src = Path("scripts/v6") / script
        txt = src.read_text()
        assert txt.startswith("#!/usr/bin/python3"), script
        assert "random." not in txt and "np.random" not in txt, f"{script}: PRNG use"
        if script != "v6_data_common.py":
            assert "interpreter_guard()" in txt and "pin_env()" in txt, script
    # scripts/v5 untouched by this phase (no v6 import, no edits): every v6 wrapper imports v5 read-only
    for w in ("velocity_v6.py", "form_plan_v6.py", "generate_v6.py"):
        assert "from scripts.v5 import" in (Path("scripts/v6") / w).read_text()
    assert Path("scripts/v6/run_pipeline_v6.sh").read_text().startswith("#!/usr/bin/env bash")
    print(f"test_08 PASS: env pin sha {C.ENV_PIN_SHA256[:16]} reproduced; guards/pins present; no PRNG in scripts/v6 data layer")


def _run_all() -> int:
    fails = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        try:
            fn()
        except AssertionError as exc:
            fails += 1
            print(f"{name} FAIL: {exc}")
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"{name} ERROR: {type(exc).__name__}: {exc}")
    print(f"{'ALL PASS' if not fails else f'{fails} FAILED'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(_run_all())
