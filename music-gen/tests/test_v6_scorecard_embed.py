#!/usr/bin/python3
"""v6 Phase 1A tests — embed_audio windowing / caching on synthetic WAVs.

Model-dependent tests are skipped when V6_SKIP_MODELS=1 (they need the cached CLAP/MERT weights).
Run: /usr/bin/python3 -m pytest tests/test_v6_scorecard_*.py -q
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

SKIP_MODELS = os.environ.get("V6_SKIP_MODELS") == "1"


def synth(sr=16000, sine_s=20.0, silence_s=15.0, f0=440.0, amp=0.3):
    t = np.arange(int(sine_s * sr)) / sr
    x = np.concatenate([amp * np.sin(2 * np.pi * f0 * t), np.zeros(int(silence_s * sr))]).astype(np.float32)
    return x


def test_cut_windows_count_and_silence_skip():
    sr = 16000
    x = synth(sr)  # 35 s: 20 s sine then 15 s digital silence
    win, starts = ea.cut_windows(x, sr, 10.0, 5.0, silence_dbfs=-60.0)
    # starts 0,5,...,25 -> 6 full windows; 20 and 25 are silent -> skipped; 15 is half-sine -> kept
    assert list(starts) == [0.0, 5.0, 10.0, 15.0]
    assert win.shape == (4, 10 * sr) and win.dtype == np.float32
    win_all, starts_all = ea.cut_windows(x, sr, 10.0, 5.0, silence_dbfs=-300.0)
    assert len(starts_all) == 6 and starts_all[-1] == 25.0
    win_cap, _ = ea.cut_windows(x, sr, 10.0, 5.0, max_windows=2)
    assert win_cap.shape[0] == 2
    # trailing partial window dropped: 12 s -> only one 10 s window at 0
    assert len(ea.cut_windows(x[: 12 * sr], sr, 10.0, 5.0)[1]) == 1
    # nothing usable
    e, es = ea.cut_windows(np.zeros(5 * sr, np.float32), sr, 10.0, 5.0)
    assert e.shape == (0, 10 * sr) and es.shape == (0,)
    assert ea.rms_dbfs(np.zeros(10)) < -200 and abs(ea.rms_dbfs(np.ones(10))) < 1e-9


def test_load_mono_downmix_and_resample(tmp_path):
    sr = 22050
    x = synth(sr, sine_s=3.0, silence_s=0.0)
    stereo = np.stack([x, -x * 0.5], axis=1)
    p = tmp_path / "s.wav"
    sf.write(p, stereo, sr)
    y, dur = ea.load_mono(p, 16000)
    assert abs(dur - 3.0) < 1e-3 and y.dtype == np.float32 and y.ndim == 1
    assert abs(len(y) - 3 * 16000) <= 2
    y2, _ = ea.load_mono(p, sr)
    assert np.allclose(y2, stereo.mean(axis=1), atol=1e-4)  # PCM-16 round trip


class FakeBackbone(ea._Backbone):
    """Deterministic stand-in: 8-d features from window statistics."""
    name, sr, dim = "clap", 16000, 8
    calls = 0

    def embed(self, windows, batch_size):
        FakeBackbone.calls += 1
        rms = np.sqrt((windows ** 2).mean(axis=1))
        feats = np.stack([rms, windows.max(1), windows.min(1), windows.std(1)] + [windows[:, i] for i in range(4)], 1)
        return feats.astype(np.float32)

    def info(self):
        return {"model_id": "fake", "revision": "0", "sample_rate": self.sr, "dim": self.dim}


def test_embed_files_writes_npz_sidecar_and_caches(tmp_path):
    sr = 16000
    p = tmp_path / "song.wav"
    sf.write(p, synth(sr), sr)
    out = tmp_path / "emb"
    fb = FakeBackbone()
    recs = ea.embed_files([p], "clap", out, backbone=fb, log=lambda *_: None)
    assert len(recs) == 1 and recs[0]["cache_hit"] is False
    r = recs[0]
    npz = out / "clap" / f"{r['sha16']}.npz"
    side = out / "clap" / f"{r['sha16']}.json"
    assert npz.exists() and side.exists() and not list((out / "clap").glob("*.tmp*"))
    z = np.load(npz)
    assert z["emb"].shape == (4, 8) and list(z["window_start_s"]) == [0.0, 5.0, 10.0, 15.0]
    meta = json.loads(side.read_text())
    assert meta["n_windows"] == 4 and meta["n_windows_total"] == 6 and abs(meta["duration_s"] - 35.0) < 1e-3
    assert meta["sha256"].startswith(meta["sha16"]) and len(meta["sha256"]) == 64
    assert meta["schema_version"] == ea.SCHEMA_VERSION and "env" in meta and meta["model"]["model_id"] == "fake"
    assert side.read_text() == json.dumps(meta, sort_keys=True, indent=2) + "\n"
    # second call: cache hit, backbone not invoked
    calls = FakeBackbone.calls
    recs2 = ea.embed_files([p], "clap", out, backbone=fb, log=lambda *_: None)
    assert recs2[0]["cache_hit"] is True and FakeBackbone.calls == calls
    # changed settings -> cache miss
    recs3 = ea.embed_files([p], "clap", out, hop_s=2.5, backbone=fb, log=lambda *_: None)
    assert recs3[0]["cache_hit"] is False and recs3[0]["n_windows"] > 4
    # --force -> re-embed
    recs4 = ea.embed_files([p], "clap", out, hop_s=2.5, force=True, backbone=fb, log=lambda *_: None)
    assert recs4[0]["cache_hit"] is False


def test_cli_with_fake_backbone(tmp_path, monkeypatch, capsys):
    sr = 16000
    (tmp_path / "in").mkdir()
    for i in range(2):
        sf.write(tmp_path / "in" / f"s{i}.wav", synth(sr, f0=300.0 + 100 * i), sr)
    monkeypatch.setattr(ea, "load_backbone", lambda name: FakeBackbone())
    rc = ea.main(["--inputs", str(tmp_path / "in"), "--out-dir", str(tmp_path / "emb"), "--backbones", "clap",
                  "--summary-json", str(tmp_path / "summary.json")])
    assert rc == 0
    summ = json.loads((tmp_path / "summary.json").read_text())
    assert summ["backbones"]["clap"]["n_files"] == 2 and summ["backbones"]["clap"]["n_windows"] == 8
    assert len(list((tmp_path / "emb" / "clap").glob("*.npz"))) == 2
    assert "schema_version" in json.loads(capsys.readouterr().out.strip().splitlines()[-1])


@pytest.mark.skipif(SKIP_MODELS, reason="V6_SKIP_MODELS=1: cached CLAP/MERT weights not exercised")
def test_real_backbones_shapes_and_determinism(tmp_path):
    sr = 48000
    p = tmp_path / "tone.wav"
    sf.write(p, synth(sr, sine_s=20.0, silence_s=0.0, f0=220.0), sr)
    out = tmp_path / "emb"
    for name, dim in (("clap", 512), ("mert", 1536)):
        recs = ea.embed_files([p], name, out, log=lambda *_: None)
        z = np.load(out / name / f"{recs[0]['sha16']}.npz")
        assert z["emb"].shape == (3, dim) and np.all(np.isfinite(z["emb"]))
        assert recs[0]["model"]["revision"] is not None
        if name == "clap":
            assert np.allclose(np.linalg.norm(z["emb"], axis=1), 1.0, atol=1e-3)
        z2 = ea.embed_files([p], name, out, force=True, log=lambda *_: None)
        assert np.allclose(np.load(z2[0]["npz"])["emb"], z["emb"], atol=1e-4)
