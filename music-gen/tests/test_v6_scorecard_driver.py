#!/usr/bin/python3
"""v6 Phase 1B tests — scorecard.py driver: gates derivation/application, candidate/reference overlap
exclusion, stem file discovery, audio descriptors on synthetic WAVs, novelty runs, SCORECARD.md rendering,
and an end-to-end run with a fake backbone (no models, no network).

Run: /usr/bin/python3 -m pytest tests/test_v6_scorecard_*.py -q
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
from scripts.v6 import distribution_metrics as dm  # noqa: E402
from scripts.v6 import embed_audio as ea  # noqa: E402
from scripts.v6 import musdb_export as mx  # noqa: E402
from scripts.v6 import scorecard as sc  # noqa: E402


# ----------------------------------------------------------------------------- fixtures
def _agg(mean, sd, lo, hi):
    return {"n": 20, "mean": mean, "sd": sd, "min": lo, "max": hi, "p2_5": lo, "p97_5": hi}


def fake_summary():
    """Minimal baseline_real_vs_real summary with two backbones."""
    def bb(kid_hi, c2_hi, cov_lo, nov_hi):
        agg = {"kid_song": _agg(0.0, 1e-4, -1e-4, kid_hi), "kid_mean": _agg(2e-4, 1e-4, 1e-4, 4e-4),
               "fad": _agg(0.15, 0.02, 0.12, 0.2), "c2st_balanced_accuracy": _agg(0.49, 0.09, 0.33, c2_hi),
               "knn_real_fraction": _agg(0.52, 0.1, 0.37, 0.72), "density": _agg(2.4, 0.7, 1.4, 3.8),
               "coverage": _agg(0.7, 0.12, cov_lo, 0.9), "novelty_max_cos": _agg(0.966, 0.003, 0.959, nov_hi),
               "kid_song_ci_covers_zero_fraction": 1.0}
        return {"split_half": {"aggregate": agg}}
    return {"schema_version": "v6.baseline.1", "n_songs": 29, "bands": {"4": 9, "5": 16, "7": 4},
            "params": {"splits": 20, "seed": 0, "k": 5},
            "backbones": {"clap": bb(2e-4, 0.666, 0.4671, 0.9686), "mert": bb(8.5e-4, 0.5485, 0.5551, 0.9874)}}


@pytest.fixture
def gates():
    return sc.derive_gates(fake_summary(), "fake/summary.json")


# ----------------------------------------------------------------------------- gates
def test_derive_gates_records_thresholds_and_derivation(gates, tmp_path):
    assert gates["schema_version"] == sc.GATES_SCHEMA_VERSION
    assert gates["derived_from"]["path"] == "fake/summary.json" and len(gates["derivation"]) >= 5
    m = gates["backbones"]["mert"]
    assert m["c2st_balanced_accuracy"]["threshold"] == 0.55   # ceil(0.5485, 2dp)
    assert gates["backbones"]["clap"]["c2st_balanced_accuracy"]["threshold"] == 0.67
    assert m["kid_song"]["p97_5"] == 8.5e-4 and m["coverage"]["threshold"] == 0.5551
    assert m["novelty_max_cos"]["max_cos_threshold"] == 0.995 and m["novelty_max_cos"]["run_cos_threshold"] == 0.9874
    assert gates["backbones"]["clap"]["novelty_max_cos"]["max_cos_threshold"] == 0.985
    p = tmp_path / "gates.json"
    from scripts.v6.v6_common import write_json_atomic
    write_json_atomic(p, gates)
    loaded = sc.load_gates(p)
    assert loaded == json.loads(json.dumps(gates))
    bad = dict(gates, schema_version="nope")
    write_json_atomic(p, bad)
    with pytest.raises(ValueError):
        sc.load_gates(p)


def _flat(**kw):
    base = {"kid_song": 0.0, "kid_song_ci95_lo": -1e-4, "kid_song_ci95_hi": 1e-4, "kid_mean": 2e-4, "fad": 0.15,
            "c2st_balanced_accuracy": 0.5, "coverage": 0.7, "density": 2.0, "knn_real_fraction": 0.5,
            "knn_real_fraction_null": 0.5, "novelty_max_cos": 0.96}
    base.update(kw)
    return base


def test_apply_gates_pass_flag_info(gates):
    g = gates["backbones"]["mert"]
    r = sc.apply_gates(_flat(), g)
    assert r["kid_song"]["verdict"] == "PASS" and r["kid_song"]["ci95"] == [-1e-4, 1e-4]
    assert r["c2st_balanced_accuracy"]["verdict"] == "PASS" and r["coverage"]["verdict"] == "PASS"
    assert r["novelty_max_cos"]["verdict"] == "PASS"
    assert {r[m]["verdict"] for m in ("density", "fad", "knn_real_fraction", "kid_mean")} == {"INFO"}
    assert r["knn_real_fraction"]["null_expectation"] == 0.5
    # primary: point above p97.5 AND CI excluding 0 -> FLAG
    r = sc.apply_gates(_flat(kid_song=2e-3, kid_song_ci95_lo=5e-4, kid_song_ci95_hi=4e-3), g)
    assert r["kid_song"]["verdict"] == "FLAG"
    # point above p97.5 but CI covers 0 -> PASS (not distinguishable)
    r = sc.apply_gates(_flat(kid_song=2e-3, kid_song_ci95_lo=-5e-4, kid_song_ci95_hi=4e-3), g)
    assert r["kid_song"]["verdict"] == "PASS"
    # CI excludes 0 but point below p97.5 -> PASS
    r = sc.apply_gates(_flat(kid_song=5e-4, kid_song_ci95_lo=1e-5, kid_song_ci95_hi=9e-4), g)
    assert r["kid_song"]["verdict"] == "PASS"
    # secondary + diagnostic
    r = sc.apply_gates(_flat(c2st_balanced_accuracy=0.56, coverage=0.3), g)
    assert r["c2st_balanced_accuracy"]["verdict"] == "FLAG" and r["coverage"]["verdict"] == "FLAG"
    assert sc.apply_gates(_flat(c2st_balanced_accuracy=0.55), g)["c2st_balanced_accuracy"]["verdict"] == "PASS"
    # novelty flagged songs -> FLAG regardless of max value
    assert sc.apply_gates(_flat(), g, novelty_flagged=1)["novelty_max_cos"]["verdict"] == "FLAG"
    # NaN / missing -> N/A
    r = sc.apply_gates(_flat(kid_song=float("nan"), kid_song_ci95_lo=float("nan"), kid_song_ci95_hi=float("nan"),
                             c2st_balanced_accuracy=None), g)
    assert r["kid_song"]["verdict"] == "N/A" and r["c2st_balanced_accuracy"]["verdict"] == "N/A"


def test_overall_verdict_reasons(gates):
    g = gates["backbones"]["clap"]
    flagged = sc.apply_gates(_flat(coverage=0.1), g)
    block = {"metrics": flagged, "flags": [m for m, r in flagged.items() if r["verdict"] == "FLAG"]}
    v = sc.overall_verdict({"clap": block}, {"drums": {"flags": ["c2st_balanced_accuracy"]}})
    assert v["overall"] == "FLAG" and v["reasons"] == ["clap:coverage (diagnostic)", "stem=drums:c2st_balanced_accuracy (indicative)"]
    ok = sc.apply_gates(_flat(), g)
    assert sc.overall_verdict({"clap": {"metrics": ok, "flags": []}}, None) == {"overall": "PASS", "reasons": []}


# ----------------------------------------------------------------------------- overlap / discovery
def test_exclude_overlap_by_sha16():
    ref = [sc.RefItem(path=f"/r/{i}.wav", sha16=f"{i:016x}", label=f"r{i}") for i in range(5)]
    kept, dropped = sc.exclude_overlap(ref, {"0000000000000001", "0000000000000003", "ffffffffffffffff"})
    assert [r["label"] for r in kept] == ["r0", "r2", "r4"]
    assert dropped == [{"sha16": "0000000000000001", "label": "r1"}, {"sha16": "0000000000000003", "label": "r3"}]
    assert sc.exclude_overlap(ref, set())[0] == ref


def test_discover_candidates_splits_stems(tmp_path):
    sr = 8000
    names = ["mix.wav", "drums.wav", "bass.wav", "other.wav", "vocals.wav", "take2_drums.wav", "take2-bass.wav",
             "take2.other.wav", "brother.wav", "song_final.wav", "mother_of_pearl.wav"]
    for n in names:
        sf.write(tmp_path / n, np.zeros(sr, np.float32), sr)
    (tmp_path / "notes.txt").write_text("x")
    d = sc.discover_candidates([tmp_path])
    assert sorted(p.name for p in d["mix"]) == ["brother.wav", "mix.wav", "mother_of_pearl.wav", "song_final.wav"]
    assert sorted(p.name for p in d["stems"]["drums"]) == ["drums.wav", "take2_drums.wav"]
    assert sorted(p.name for p in d["stems"]["bass"]) == ["bass.wav", "take2-bass.wav"]
    assert sorted(p.name for p in d["stems"]["other"]) == ["other.wav", "take2.other.wav"]
    assert len(d["ignored"]) == 1 and d["ignored"][0]["path"].endswith("vocals.wav")
    assert sc.classify_stem(Path("x/Drums.WAV")) == "drums" and sc.classify_stem(Path("x/drumsolo.wav")) is None


def test_resolve_musdb_from_manifest(tmp_path):
    man = {"schema_version": "v6.musdb_export.1", "songs": [
        {"split": "train", "slug": "a", "files": {"accompaniment": {"path": "data/x/a/accompaniment.wav", "sha16": "a" * 16},
                                                  "drums": {"path": str(tmp_path / "a_drums.wav"), "sha16": "d" * 16}}},
        {"split": "test", "slug": "b", "files": {"accompaniment": {"path": "data/x/b/accompaniment.wav", "sha16": "b" * 16}}}]}
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps(man))
    items = sc.resolve_musdb(p, "all")
    assert [i["sha16"] for i in items] == ["a" * 16, "b" * 16] and items[0]["label"] == "train/a"
    assert Path(items[0]["path"]).is_absolute()
    assert [i["label"] for i in sc.resolve_musdb(p, "test")] == ["test/b"]
    assert sc.resolve_musdb(p, "train", "drums")[0]["path"] == str(tmp_path / "a_drums.wav")
    with pytest.raises(ValueError):
        sc.resolve_musdb(p, "test", "drums")


# ----------------------------------------------------------------------------- descriptors
def test_audio_descriptors_synthetic(tmp_path):
    sr = 44100
    t = np.arange(10 * sr) / sr
    tone = (0.5 * np.sin(2 * np.pi * 1000 * t)).astype(np.float32)
    # stereo, L = R -> zero width, correlation 1
    p_mono_ish = tmp_path / "same.wav"
    sf.write(p_mono_ish, np.stack([tone, tone], 1), sr)
    d = sc.audio_descriptors(p_mono_ish)
    assert d["channels"] == 2 and abs(d["duration_s"] - 10.0) < 1e-3
    assert abs(d["peak_dbfs"] - 20 * math.log10(0.5)) < 0.05
    assert abs(d["crest_factor_db"] - 20 * math.log10(math.sqrt(2))) < 0.05  # sine: 3.01 dB
    assert abs(d["spectral_centroid_hz"] - 1000) < 30
    assert d["stereo_width_db"] < -60 and abs(d["lr_correlation"] - 1.0) < 1e-6
    assert d["lufs_integrated"] is not None and -12 < d["lufs_integrated"] < -2
    # L = -R -> all side, no mid
    p_wide = tmp_path / "wide.wav"
    sf.write(p_wide, np.stack([tone, -tone], 1), sr)
    w = sc.audio_descriptors(p_wide)
    assert w["stereo_width_db"] > 60 and abs(w["lr_correlation"] + 1.0) < 1e-6
    # mono file: width undefined, centroid still computed
    p_mono = tmp_path / "mono.wav"
    sf.write(p_mono, tone[::2], 22050)  # decimate so the tone stays 1 kHz at 22.05 kHz
    m = sc.audio_descriptors(p_mono)
    assert m["channels"] == 1 and m["stereo_width_db"] is None and m["lr_correlation"] is None
    assert abs(m["spectral_centroid_hz"] - 1000) < 60
    # digital silence: LUFS undefined (-inf -> None), no crash
    p_sil = tmp_path / "sil.wav"
    sf.write(p_sil, np.zeros((sr, 2), np.float32), sr)
    s = sc.audio_descriptors(p_sil)
    assert s["lufs_integrated"] is None and s["peak_dbfs"] < -200
    # cache + summary
    items = [sc.RefItem(path=str(p_mono_ish), sha16="1" * 16, label="same"), sc.RefItem(path=str(p_wide), sha16="2" * 16, label="wide")]
    recs = sc.descriptors_for(items, tmp_path / "cache", log=lambda *_: None)
    assert (tmp_path / "cache" / ("1" * 16 + ".json")).exists() and recs[1]["label"] == "wide"
    recs2 = sc.descriptors_for(items, tmp_path / "cache", log=lambda *_: pytest.fail("cache miss"))
    assert recs2[0]["lufs_integrated"] == recs[0]["lufs_integrated"]
    summ = sc.summarise_descriptors(recs)
    assert summ["n"] == 2 and summ["lr_correlation"]["n"] == 2 and abs(summ["lr_correlation"]["mean"]) < 1e-6
    assert summ["stereo_width_db"]["min"] < -60 < 60 < summ["stereo_width_db"]["max"]


# ----------------------------------------------------------------------------- novelty runs
def test_novelty_runs_detects_consecutive_same_song_hits():
    rng = np.random.default_rng(1)
    ref = [dm.Song(f"r{i}", f"r{i:015d}", rng.standard_normal((6, 16))) for i in range(3)]
    # candidate: 7 windows; windows 2,3,4 copy ref song 1 windows (cos ~1), rest random
    emb = rng.standard_normal((7, 16))
    emb[2:5] = ref[1].emb[1:4] * 1.01
    cand = [dm.Song("c0", "c" * 16, emb), dm.Song("c1", "d" * 16, rng.standard_normal((4, 16)))]
    runs = sc.novelty_runs(cand, ref, run_cos_threshold=0.97, run_length=3)
    assert runs[0]["longest_run"] == 3 and runs[0]["run_flagged"] and runs[0]["run_ref_song"] == "r1"
    assert runs[0]["run_start_window"] == 2
    assert runs[1]["longest_run"] == 0 and not runs[1]["run_flagged"] and runs[1]["run_ref_song"] is None
    # two consecutive hits on the same song, third on a different song -> run of 2, not flagged
    emb2 = rng.standard_normal((5, 16))
    emb2[0:2] = ref[0].emb[0:2]
    emb2[2] = ref[2].emb[0]
    r = sc.novelty_runs([dm.Song("c2", "e" * 16, emb2)], ref, 0.97, 3)[0]
    assert r["longest_run"] == 2 and not r["run_flagged"]


# ----------------------------------------------------------------------------- rendering + end to end
class FakeBackbone(ea._Backbone):
    """Deterministic 8-d features from window statistics (fast, no model)."""
    name, sr, dim = "clap", 8000, 8

    def embed(self, windows, batch_size):
        f = np.fft.rfft(windows, axis=1)
        mag = np.abs(f)
        bands = np.stack([mag[:, i * (mag.shape[1] // 8):(i + 1) * (mag.shape[1] // 8)].mean(1) for i in range(8)], 1)
        return (bands / np.maximum(bands.sum(1, keepdims=True), 1e-9)).astype(np.float32)

    def info(self):
        return {"model_id": "fake", "revision": "0", "sample_rate": self.sr, "dim": self.dim}


def _write_song(path, sr, seconds, f0, rng, noise=0.05, stereo=True):
    t = np.arange(int(seconds * sr)) / sr
    x = 0.3 * np.sin(2 * np.pi * f0 * t) + 0.1 * np.sin(2 * np.pi * 2.5 * f0 * t) + noise * rng.standard_normal(len(t))
    x = x.astype(np.float32)
    sf.write(path, np.stack([x, 0.8 * x], 1) if stereo else x, sr)


def _args(tmp_path, gates_path, **kw):
    import argparse
    d = dict(candidates=None, reference=None, name="run", backbones="clap", stems=False, gates=str(gates_path),
             emb_dir=str(tmp_path / "emb"), runs_dir=str(tmp_path / "runs"), descriptor_cache=str(tmp_path / "desc"),
             no_descriptors=False, receipts="", bands="4,5,7", musdb_manifest=str(tmp_path / "musdb" / "manifest.json"),
             musdb_split="all", seed=0, subsets=5, bootstrap=20, k=3)
    d.update(kw)
    return argparse.Namespace(**d)


def test_end_to_end_run_with_fake_backbone_and_stems(tmp_path, monkeypatch):
    from scripts.v6.v6_common import write_json_atomic
    monkeypatch.setattr(ea, "load_backbone", lambda name: FakeBackbone())
    rng = np.random.default_rng(0)
    sr = 8000
    # reference "musdb": 8 songs with accompaniment + 3 stems each, manifest like musdb_export writes
    man = {"schema_version": "v6.musdb_export.1", "songs": []}
    for i in range(8):
        sd = tmp_path / "musdb" / "train" / f"song{i}"
        sd.mkdir(parents=True)
        files = {}
        for kind, f0 in (("accompaniment", 200 + 20 * i), ("drums", 90 + 5 * i), ("bass", 60 + 3 * i), ("other", 400 + 30 * i)):
            p = sd / f"{kind}.wav"
            _write_song(p, sr, 40, f0, rng)
            from scripts.v6.v6_common import sha16_of, sha256_file
            files[kind] = {"path": str(p), "sha16": sha16_of(sha256_file(p)), "bytes": p.stat().st_size}
        man["songs"].append({"split": "train", "slug": f"song{i}", "files": files, "duration_s": 40.0})
    write_json_atomic(tmp_path / "musdb" / "manifest.json", man)
    # candidates: 3 songs in-distribution + stems; one candidate is byte-identical to a reference song (overlap)
    cd = tmp_path / "cands"
    cd.mkdir()
    for i in range(2):
        _write_song(cd / f"gen{i}.wav", sr, 40, 230 + 25 * i, rng)
        _write_song(cd / f"gen{i}_drums.wav", sr, 40, 95 + 7 * i, rng)
    import shutil
    shutil.copy(tmp_path / "musdb" / "train" / "song3" / "accompaniment.wav", cd / "copy_of_song3.wav")
    (cd / "vocals.wav").write_bytes((tmp_path / "musdb" / "train" / "song0" / "drums.wav").read_bytes())
    gates = sc.derive_gates(fake_summary(), "fake")
    gates_path = tmp_path / "gates.json"
    write_json_atomic(gates_path, gates)
    args = _args(tmp_path, gates_path, candidates=[str(cd)], reference="musdb", name="e2e", stems=True)
    out = sc.run(args, log=lambda *_: None)
    assert out["candidates"]["n_files"] == 3 and out["reference"]["n_files_total"] == 8
    assert out["reference"]["n_files"] == 7 and out["reference"]["excluded_overlap"][0]["label"] == "train/song3"
    assert len(out["candidates"]["ignored"]) == 1
    b = out["backbones"]["clap"]
    assert b["n_songs_a"] == 3 and b["n_songs_b"] == 7 and set(b["metrics"]) == set(sc.METRIC_ORDER)
    assert b["metrics"]["kid_song"]["ci95"] is not None and b["verdict"] in ("PASS", "FLAG")
    # the exact copy of song3 was excluded from the reference, so it must not be a novelty hit on itself
    assert all(r["nearest_ref_song"] != "train/song3" or r["song_id"] != "copy_of_song3.wav" for r in b["least_real_like"])
    assert set(out["stems"]) == {"drums"} and out["stems"]["drums"]["n_songs_a"] == 2 and out["stems"]["drums"]["n_songs_b"] == 8
    assert (tmp_path / "emb" / "clap" / "stem=drums").is_dir()
    assert out["descriptors"]["candidates"]["summary"]["n"] == 3 and out["descriptors"]["reference"]["summary"]["n"] == 7
    assert out["verdict"]["overall"] in ("PASS", "FLAG") and out["gates"]["sha16"]
    run_dir = tmp_path / "runs" / "e2e"
    assert (run_dir / "scorecard.json").exists() and (run_dir / "distribution_clap.json").exists()
    assert (run_dir / "distribution_clap_stem=drums.json").exists()
    md = (run_dir / "SCORECARD.md").read_text()
    assert md.startswith("# v6 scorecard — e2e") and "## clap" in md and "| kid_song |" in md
    assert "## Timbre by instrument" in md and "| drums |" in md
    assert "## Audio descriptors" in md and "| lufs_integrated |" in md
    assert "1 excluded as candidate overlap" in md and "ignored" in md
    assert f"Overall verdict: **{out['verdict']['overall']}**" in md
    # JSON is sorted-key and re-loadable
    txt = (run_dir / "scorecard.json").read_text()
    assert txt == json.dumps(json.loads(txt), sort_keys=True, indent=2) + "\n"
    # a second run is a pure cache hit for embeddings and descriptors and gives identical metrics
    out2 = sc.run(_args(tmp_path, gates_path, candidates=[str(cd)], reference="musdb", name="e2e2", stems=True), log=lambda *_: None)
    assert out2["backbones"]["clap"]["metrics"]["kid_song"]["value"] == b["metrics"]["kid_song"]["value"]


def test_render_markdown_minimal_pass():
    gates = sc.derive_gates(fake_summary(), "fake")
    metrics = sc.apply_gates(_flat(), gates["backbones"]["mert"])
    block = {"backbone": "mert", "tag": None, "dim": 1536, "n_songs_a": 14, "n_windows_a": 700, "n_songs_b": 15, "n_windows_b": 750,
             "metrics": metrics, "flags": [], "verdict": "PASS", "novelty_flagged_songs": [],
             "least_real_like": [{"song_id": "s", "knn_real_fraction_mean": 0.4, "nearest_ref_cos": 0.9, "nearest_ref_song": "r"}],
             "distribution_json": "x"}
    scd = {"name": "t", "verdict": {"overall": "PASS", "reasons": []},
           "candidates": {"n_files": 14, "n_songs_scored": 14, "ignored": [], "dropped": {}},
           "reference": {"info": {"spec": "corpus"}, "n_files": 15, "excluded_overlap": [{"sha16": "a" * 16, "label": "x"}] * 14},
           "gates": {"path": "g.json", "sha16": "0" * 16}, "params": {"seed": 0, "k": 5, "bootstrap": 200},
           "backbones": {"mert": block}, "stems": None, "descriptors": None, "wall_s": 1.0}
    md = sc.render_markdown(scd)
    assert "Overall verdict: **PASS**" in md and "14 excluded as candidate overlap" in md
    assert "| c2st_balanced_accuracy | 0.5 | - | [0.33, 0.5485] | FLAG if > 0.55 | PASS |" in md
    assert "Novelty: no candidate song flagged." in md and "Least real-like" in md


# ----------------------------------------------------------------------------- musdb_export (pure parts)
def test_musdb_export_layout_decision_and_slug():
    assert mx.slugify("A Classic Education - NightOwl") == "a_classic_education_nightowl"
    assert mx.slugify("Actions - Devil's Words") == "actions_devil_s_words"
    durs = {"train": [240.0] * 100, "test": [240.0] * 50}
    a, b = mx.estimate_footprint(durs, "A"), mx.estimate_footprint(durs, "B")
    assert a > b and abs(a - (100 * 5 + 50) * 240 * 176400) / a < 0.01
    assert abs(b - (100 * 240 * (176400 + 4 * 44100) + 50 * 240 * 176400)) / b < 0.01
    lay, dec = mx.choose_layout(durs, int(9e9))
    assert lay == "B" and "WARNING" in dec["note"]
    assert mx.choose_layout(durs, int(30e9))[0] == "A"
    assert mx.files_for_split("test") == ["accompaniment"] and "vocals" not in mx.files_for_split("train")
    assert mx.layout_formats("B")["accompaniment"] == "stereo44k" and mx.layout_formats("B")["drums"] == "mono22k"


def test_musdb_export_to_format_and_write_wav(tmp_path):
    sr = 44100
    t = np.arange(sr) / sr
    x = np.stack([0.5 * np.sin(2 * np.pi * 440 * t), 1.5 * np.sin(2 * np.pi * 440 * t)], 1)
    y = mx.to_format(x, "mono22k")
    assert y.ndim == 1 and abs(len(y) - 22050) <= 2 and y.dtype == np.float32
    z = mx.to_format(x, "stereo44k")
    assert z.shape == (sr, 2)
    rec = mx.write_wav(tmp_path / "a.wav", z, sr)
    assert rec["clipped_samples"] > 0 and rec["channels"] == 2 and rec["sr"] == sr and len(rec["sha16"]) == 16
    info = sf.info(str(tmp_path / "a.wav"))
    assert info.subtype == "PCM_16" and info.channels == 2 and not list(tmp_path.glob("*.tmp*"))
    assert abs(mx.rms_dbfs(np.full(100, 0.5)) - 20 * math.log10(0.5)) < 1e-9
