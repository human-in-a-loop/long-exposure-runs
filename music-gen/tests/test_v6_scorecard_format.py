#!/usr/bin/python3
"""v6 Phase 5 (iteration 05) tests — scorecard fair mode (--match-reference-format, scripts/v6/scorecard_format.py):
reference format probing, the transform (down-mix / up-mix / resample), the sha-keyed cache with pass-through, the
`_fmt` run-name suffix, and an end-to-end scorecard.run with a fake backbone that records `candidate_format`.

Run: /usr/bin/python3 -m pytest tests/test_v6_scorecard_format.py -q
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
from scripts.v6 import embed_audio as ea  # noqa: E402
from scripts.v6 import scorecard as sc  # noqa: E402
from scripts.v6 import scorecard_format as scf  # noqa: E402
from scripts.v6.v6_common import sha16_of, sha256_file, write_json_atomic  # noqa: E402
sys.path.insert(0, str(_ROOT / "tests"))
from test_v6_scorecard_driver import FakeBackbone, _args, _write_song, fake_summary  # noqa: E402


def _tone(sr, secs, f0, stereo=True, amp=0.3):
    t = np.arange(int(secs * sr)) / sr
    x = (amp * np.sin(2 * np.pi * f0 * t)).astype(np.float32)
    return np.stack([x, 0.5 * x], 1) if stereo else x


def test_01_transform_audio_downmix_upmix_resample():
    sr = 44100
    x = _tone(sr, 2.0, 1000.0, stereo=True)
    y = scf.transform_audio(x, sr, 22050, 1)
    assert y.shape == (22050 * 2, 1) and y.dtype == np.float32
    # channel mean: (1 + 0.5) / 2 = 0.75 of the tone amplitude
    assert abs(float(np.abs(y[4000:-4000]).max()) - 0.75 * 0.3) < 0.01
    # the 1 kHz tone survives the resample (spectral peak at 1 kHz)
    spec = np.abs(np.fft.rfft(y[:, 0]))
    assert abs(np.fft.rfftfreq(len(y), 1 / 22050)[int(np.argmax(spec))] - 1000.0) < 2.0
    # mono -> stereo duplicates, same sr is untouched
    m = _tone(sr, 1.0, 440.0, stereo=False)
    z = scf.transform_audio(m, sr, sr, 2)
    assert z.shape == (sr, 2) and np.array_equal(z[:, 0], z[:, 1]) and np.allclose(z[:, 0], m)
    # stereo -> stereo at the same rate is the identity
    assert np.array_equal(scf.transform_audio(x, sr, sr, 2), x)


def test_02_reference_format_modal_and_uniform(tmp_path):
    items = []
    for i, (sr, ch) in enumerate([(22050, 1), (22050, 1), (44100, 2)]):
        p = tmp_path / f"r{i}.wav"
        sf.write(str(p), _tone(sr, 0.5, 220.0, stereo=(ch == 2)), sr, subtype="PCM_16")
        items.append({"path": str(p), "sha16": "0" * 16, "label": f"r{i}"})
    f = scf.reference_format(items)
    assert f["sample_rate"] == 22050 and f["channels"] == 1 and f["n_files"] == 3 and f["n_modal"] == 2 and f["uniform"] is False
    assert f["formats"] == {"22050hz_1ch": 2, "44100hz_2ch": 1}
    assert scf.reference_format(items[:2])["uniform"] is True
    with pytest.raises(ValueError):
        scf.reference_format([])


def test_03_match_items_cache_passthrough_and_sha_keys(tmp_path):
    fmt = {"sample_rate": 22050, "channels": 1}
    cand = tmp_path / "c.wav"
    sf.write(str(cand), _tone(44100, 1.0, 500.0), 44100, subtype="PCM_16")
    already = tmp_path / "a.wav"
    sf.write(str(already), _tone(22050, 1.0, 500.0, stereo=False), 22050, subtype="PCM_16")
    items = [{"path": str(cand), "sha16": sha16_of(sha256_file(cand)), "label": "c"},
             {"path": str(already), "sha16": sha16_of(sha256_file(already)), "label": "a"}]
    logs = []
    matched, block = scf.match_items(items, fmt, tmp_path / "cache", log=logs.append)
    assert block["matched"] and block["n_transformed"] == 1 and block["n_passthrough"] == 1 and len(logs) == 1
    c, a = matched
    assert c["transformed"] and c["cache_hit"] is False and Path(c["path"]).parent == tmp_path / "cache"
    assert Path(c["path"]).name == f"{items[0]['sha16']}_22050hz_1ch.wav"
    assert c["sha16"] == sha16_of(sha256_file(Path(c["path"]))) != c["source_sha16"] == items[0]["sha16"]
    info = sf.info(c["path"])
    assert info.samplerate == 22050 and info.channels == 1 and info.subtype == "PCM_16"
    side = json.loads(Path(c["path"]).with_suffix(".json").read_text())
    assert side["schema_version"] == scf.SCHEMA_VERSION and side["source_sha256"] == sha256_file(cand) and side["target_format"] == fmt
    assert not a["transformed"] and a["path"] == str(already) and a["sha16"] == items[1]["sha16"]
    # second call: cache hit, no rewrite, byte-identical output -> same sha16 (so cached embeddings are reused)
    mtime = Path(c["path"]).stat().st_mtime_ns
    matched2, _ = scf.match_items(items, fmt, tmp_path / "cache", log=lambda m: pytest.fail(f"unexpected transform: {m}"))
    assert matched2[0]["cache_hit"] is True and matched2[0]["sha16"] == c["sha16"] and Path(c["path"]).stat().st_mtime_ns == mtime
    # a changed source invalidates the cache entry
    sf.write(str(cand), _tone(44100, 1.0, 700.0), 44100, subtype="PCM_16")
    items[0]["sha16"] = sha16_of(sha256_file(cand))
    matched3, _ = scf.match_items(items, fmt, tmp_path / "cache", log=lambda *_: None)
    assert matched3[0]["cache_hit"] is False and matched3[0]["sha16"] != c["sha16"]


def test_04_run_name_suffix_idempotent():
    assert scf.run_name("it04_vs_accomp", True) == "it04_vs_accomp_fmt"
    assert scf.run_name("it04_vs_accomp_fmt", True) == "it04_vs_accomp_fmt"
    assert scf.run_name("it04_vs_accomp", False) == "it04_vs_accomp"


def test_05_end_to_end_fair_mode_records_candidate_format(tmp_path, monkeypatch):
    monkeypatch.setattr(ea, "load_backbone", lambda name: FakeBackbone())
    rng = np.random.default_rng(3)
    ref = tmp_path / "ref"
    ref.mkdir()
    for i in range(6):  # reference: mono 8 kHz
        _write_song(ref / f"r{i}.wav", 8000, 40, 200 + 20 * i, rng, stereo=False)
    cd = tmp_path / "cands"
    cd.mkdir()
    for i in range(3):  # candidates: stereo 16 kHz
        _write_song(cd / f"g{i}.wav", 16000, 40, 230 + 25 * i, rng, stereo=True)
    gates_path = tmp_path / "gates.json"
    write_json_atomic(gates_path, sc.derive_gates(fake_summary(), "fake"))
    args = _args(tmp_path, gates_path, candidates=[str(cd)], reference=str(ref), name="fair", stems=False,
                 match_reference_format=True, format_cache=str(tmp_path / "fmt"))
    out = sc.run(args, log=lambda *_: None)
    assert out["name"] == "fair_fmt" and (tmp_path / "runs" / "fair_fmt" / "scorecard.json").exists()
    cf = out["candidate_format"]
    assert cf["matched"] and cf["reference_format"] == {"sample_rate": 8000, "channels": 1, "n_files": 6, "n_modal": 6, "uniform": True, "formats": {"8000hz_1ch": 6}}
    assert cf["n_transformed"] == 3 and len(cf["files"]) == 3 and all(f["transformed"] for f in cf["files"])
    # the embedded candidates are the transformed files (their sha16, their path), descriptors see mono (width undefined)
    assert {c["sha16"] for c in out["candidates"]["files"]} == {f["sha16"] for f in cf["files"]}
    assert all(Path(c["path"]).parent == tmp_path / "fmt" for c in out["candidates"]["files"])
    assert out["descriptors"]["candidates"]["summary"]["stereo_width_db"] == {"n": 0}
    assert all(json.loads(Path(f["path"]).with_suffix(".json").read_text())["target_format"] == {"sample_rate": 8000, "channels": 1} for f in cf["files"])
    md = (tmp_path / "runs" / "fair_fmt" / "SCORECARD.md").read_text()
    assert "FORMAT-MATCHED to the reference: 8000 Hz / 1 ch (3 transformed, 0 already matched)" in md
    # the unmatched run keeps its name and records matched: False
    out2 = sc.run(_args(tmp_path, gates_path, candidates=[str(cd)], reference=str(ref), name="plain", stems=False), log=lambda *_: None)
    assert out2["name"] == "plain" and out2["candidate_format"] == {"matched": False}
    assert out2["backbones"]["clap"]["metrics"]["kid_song"]["value"] != out["backbones"]["clap"]["metrics"]["kid_song"]["value"]
