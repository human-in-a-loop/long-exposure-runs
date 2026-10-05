#!/usr/bin/python3
"""v6 Phase 5 (iteration 05) tests — gap-localisation diagnostics (scripts/v6/diag_common.py, diag_embed_v6.py, diag_stems_v6.py):
deterministic split halves and the split-half floor, song means / spread statistics and the pre-registered homogeneity rule,
per-window descriptors on synthetic audio, the discriminant table (direction separates the classes, descriptor ranking), the
Markdown renderers, and the oracle role mapping / stem grouping. No models, no network, < 30 s.

Run: /usr/bin/python3 -m pytest tests/test_v6_diagnostics.py -q
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
from scripts.v6 import diag_common as dc  # noqa: E402
from scripts.v6 import diag_embed_v6 as de  # noqa: E402
from scripts.v6 import diag_stems_v6 as ds  # noqa: E402
from scripts.v6 import distribution_metrics as dm  # noqa: E402


def _songs(rng, n_songs, n_windows, d, centre_scale=1.0, within=0.3, prefix="s", common=None):
    """Synthetic Songs: per-song centre (scale centre_scale) + optional shared `common` vector + within-song noise."""
    out = []
    for i in range(n_songs):
        c = rng.standard_normal(d) * centre_scale + (common if common is not None else 0.0)
        out.append(dm.Song(f"{prefix}{i}", f"{prefix}{i:015d}"[:16], c[None, :] + within * rng.standard_normal((n_windows, d))))
    return out


def test_01_deterministic_halves_and_split_half_floor():
    h1, h2 = dc.deterministic_halves(9, 4, 0), dc.deterministic_halves(9, 4, 0)
    assert h1 == h2 and len(h1) == 4
    for a, b in h1:
        assert len(a) == 4 and len(b) == 5 and not set(a) & set(b) and set(a) | set(b) == set(range(9))
    assert dc.deterministic_halves(9, 4, 1) != h1
    rng = np.random.default_rng(0)
    songs = _songs(rng, 12, 8, 16)
    floor = dc.split_half_floor(songs, n_splits=3, seed=0, k=3)
    assert floor["n_splits"] == 3 and len(floor["per_split"]) == 3 and set(floor["aggregate"]) == set(dc.FLOOR_METRICS)
    a = floor["aggregate"]["kid_song"]
    assert a["n"] == 3 and a["p2_5"] <= a["mean"] <= a["p97_5"]
    # real-vs-real from one distribution: c2st near 0.5, coverage high; the same call is reproducible
    assert floor["aggregate"]["c2st_balanced_accuracy"]["mean"] < 0.8 and floor["aggregate"]["coverage"]["mean"] > 0.5
    assert dc.split_half_floor(songs, n_splits=3, seed=0, k=3)["aggregate"] == floor["aggregate"]
    assert dc.ratio_to_floor(2.0, {"p97_5": 0.5}) == 4.0 and dc.ratio_to_floor(2.0, {"p97_5": -1e-4}) is None and dc.ratio_to_floor(None, {"p97_5": 1.0}) is None


def test_02_song_means_spread_and_homogeneity_rule(tmp_path):
    rng = np.random.default_rng(1)
    refs = _songs(rng, 10, 6, 32, centre_scale=1.0, within=0.3, prefix="r")
    homog = _songs(rng, 10, 6, 32, centre_scale=0.15, within=0.3, prefix="c", common=rng.standard_normal(32))  # one shared centre -> homogeneous
    M = dc.song_means(refs)
    assert M.shape == (10, 32) and np.allclose(np.linalg.norm(M, axis=1), 1.0)
    pc, pr = de.pairwise_cos_stats(dc.song_means(homog)), de.pairwise_cos_stats(M)
    assert pc["n_pairs"] == 45 and pc["mean"] > pr["mean"] and pc["p5"] <= pc["p50"] <= pc["p95"]
    vr, vc = de.variance_ratio(refs), de.variance_ratio(homog)
    assert vr["ratio"] > vc["ratio"] > 0
    # spread() end to end through a fake scorecard.json + npz layout
    emb = tmp_path / "emb" / "clap"
    emb.mkdir(parents=True)
    files = {"candidates": [], "reference": []}
    for key, songs in (("candidates", homog), ("reference", refs)):
        for s in songs:
            np.savez(emb / f"{s.sha16}.npz", emb=s.emb.astype(np.float32), window_start_s=np.arange(len(s.emb)) * 5.0)
            files[key].append({"sha16": s.sha16, "label": s.song_id, "path": f"/x/{s.song_id}.wav"})
    scd = {"name": "fake_fmt", "candidates": {"files": files["candidates"]}, "reference": {"files": files["reference"]}}
    rep = de.spread(scd, ["clap"], tmp_path / "emb", tmp_path / "out", log=lambda *_: None)
    b = rep["backbones"]["clap"]
    assert b["n_candidates"] == 10 and b["n_reference"] == 10 and b["spread_ratio"] < de.HOMOGENEITY_RULE and b["homogeneity_confirmed"] is True
    assert (tmp_path / "out" / "spread_diagnostic.json").exists() and "CONFIRMED" in (tmp_path / "out" / "SPREAD.md").read_text()
    # the same distribution as the reference is NOT flagged
    same = _songs(rng, 10, 6, 32, centre_scale=1.0, within=0.3, prefix="d")
    for s in same:
        np.savez(emb / f"{s.sha16}.npz", emb=s.emb.astype(np.float32), window_start_s=np.arange(len(s.emb)) * 5.0)
    scd2 = {"name": "fake2", "candidates": {"files": [{"sha16": s.sha16, "label": s.song_id} for s in same]}, "reference": {"files": files["reference"]}}
    rep2 = de.spread(scd2, ["clap"], tmp_path / "emb", tmp_path / "out2", log=lambda *_: None)
    assert rep2["backbones"]["clap"]["homogeneity_confirmed"] is False and 0.7 < rep2["backbones"]["clap"]["spread_ratio"] < 1.4


def test_03_window_descriptors_on_synthetic_audio():
    sr = 22050
    t = np.arange(10 * sr) / sr
    tone = (0.3 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)
    d = de.window_descriptors(tone, sr)
    assert set(d) == set(de.DESCRIPTORS) and abs(d["spectral_centroid_hz"] - 440.0) < 40 and d["spectral_flatness"] < 0.05
    assert d["mid_ratio_db"] > -1.0 and d["low_ratio_db"] < -20 and d["high_ratio_db"] < -20 and d["hp_ratio_db"] > 10  # pure tone: harmonic, mid band
    assert abs(d["crest_db"] - 3.01) < 0.1 and d["onset_rate_hz"] < 0.5 and d["stereo_width_db"] is None
    clicks = np.zeros(10 * sr, np.float32)
    clicks[:: sr // 4] = 1.0  # 4 Hz impulses
    c = de.window_descriptors(clicks, sr)
    assert c["onset_rate_hz"] > 2.0 and c["hp_ratio_db"] < d["hp_ratio_db"] and c["spectral_flatness"] > d["spectral_flatness"] and c["crest_db"] > 20
    assert c["dynamic_range_db"] > d["dynamic_range_db"]
    st = np.stack([tone, -0.5 * tone], 1)  # mid 0.25, side 0.75 -> +9.5 dB side/mid
    w = de.window_descriptors(tone, sr, stereo=st)
    assert abs(w["stereo_width_db"] - 10 * np.log10(9.0)) < 0.1
    assert de.window_descriptors(tone, sr, stereo=np.stack([tone, tone], 1))["stereo_width_db"] < -60
    bright = (0.3 * np.sin(2 * np.pi * 6000.0 * t)).astype(np.float32)
    assert de.window_descriptors(bright, sr)["high_ratio_db"] > -1.0


def test_04_discriminant_table_names_the_separating_descriptor(tmp_path):
    rng = np.random.default_rng(2)
    n, d = 120, 16
    X = rng.standard_normal((n, d))
    Y = rng.standard_normal((n, d))
    X[:, 0] += 2.0  # candidates differ along axis 0
    w = de._lda_direction(X, Y)
    assert abs(w[0]) > 0.7 and de._auc(X @ w, Y @ w) > 0.9 and de._auc(Y @ w, X @ w) < 0.1
    base = {k: list(rng.standard_normal(n)) for k in de.DESCRIPTORS}
    Dc = {k: list(v) for k, v in base.items()}
    Dr = {k: list(rng.standard_normal(n)) for k in de.DESCRIPTORS}
    Dc["spectral_centroid_hz"] = list(X @ w + 0.1 * rng.standard_normal(n))  # tracks the score
    Dr["spectral_centroid_hz"] = list(Y @ w + 0.1 * rng.standard_normal(n))
    Dc["stereo_width_db"], Dr["stereo_width_db"] = [np.nan] * n, [np.nan] * n  # undefined (mono) -> dropped
    table = de.discriminant_table(X @ w, Y @ w, Dc, Dr)
    assert table[0]["descriptor"] == "spectral_centroid_hz" and table[0]["spearman_rho"] > 0.9 and table[0]["gap"] > 1.0 and table[0]["auc_cand_gt_ref"] > 0.9
    assert "stereo_width_db" not in {r["descriptor"] for r in table} and len(table) == len(de.DESCRIPTORS) - 1
    rep = {"scorecard": "x", "method": "m", "backbones": {"clap": {"score_auc": 0.95, "n_windows_cand": n, "n_windows_ref": n, "table": table}}}
    md = de.descriptors_markdown(rep)
    assert md.startswith("# Discriminant descriptors (x)") and "| spectral_centroid_hz |" in md


def test_05_oracle_mapping_stem_groups_and_markdown(tmp_path):
    from scripts.v6.gen.render_v6 import mix
    assert ds.ORACLE_ROLE == {"drums": "drums", "bass": "bass", "other": "keys"} and ds.KINDS == ("drums", "bass", "other")
    assert {mix.STEM_GROUP[r] for r in ("keys", "comp_guitar", "melody", "pad")} == {"other"} and mix.STEM_GROUP["percussion"] == "drums"
    # real_stem_items reads the stems manifest layout and skips missing kinds
    root = tmp_path / "stems"
    for sha in ("a" * 16, "b" * 16):
        (root / sha).mkdir(parents=True)
        for k in ("drums", "bass"):
            sf.write(str(root / sha / f"{k}.wav"), np.zeros(2205, np.float32), 22050, subtype="PCM_16")
    (root / "manifest.json").write_text('{"songs": {"%s": {"title": "A"}, "%s": {"title": "B"}}}' % ("a" * 16, "b" * 16))
    items = ds.real_stem_items(root, "drums")
    assert [i["source_sha16"] for i in items] == ["a" * 16, "b" * 16] and items[0]["label"] == "A|drums" and ds.real_stem_items(root, "other") == []
    rep = {"backbones": ["clap"], "splits": 3, "rule": "r", "ranking": {"clap": [("drums", 30.0), ("bass", 2.0)]},
           "kinds": {k: {"backbones": {"clap": {"candidate_vs_real": {"kid_song": v, "c2st_balanced_accuracy": 0.9, "coverage": 0.1, "knn_real_fraction": 0.01, "knn_real_fraction_null": 0.5,
                                                                        "n_windows_a": 10, "n_windows_b": 12},
                                                  "floor": {"aggregate": {"kid_song": {"p97_5": v / r}, "c2st_balanced_accuracy": {"mean": 0.5}, "coverage": {"mean": 0.7}, "knn_real_fraction": {"mean": 0.5}}},
                                                  "gap_ratio_kid": r}}} for k, v, r in (("drums", 3e-3, 30.0), ("bass", 2e-4, 2.0))}}
    md = ds.stems_markdown(rep)
    assert md.index("| drums |") < md.index("| bass |") and "| 30 |" in md
    orep = {"n_songs": 2, "splits": 3, "rule": "r", "backbones": {"clap": {"oracle": {m: {"mean": 0.1, "p97_5": 0.2} for m in dc.FLOOR_METRICS},
                                                                           "real_vs_real": {m: {"mean": 0.1, "p97_5": 0.2} for m in dc.FLOOR_METRICS}, "kid_ratio_to_floor_p97_5": 0.5,
                                                                           "c2st_gate": 0.61, "verdict": "PASS"}}}
    assert "| clap |" in ds.oracle_markdown(orep) and "PASS" in ds.oracle_markdown(orep)
