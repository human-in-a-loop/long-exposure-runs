#!/usr/bin/python3
"""v6 Phase 1A tests — distribution_metrics on synthetic embeddings (no audio, no models).

Run: /usr/bin/python3 -m pytest tests/test_v6_scorecard_*.py -q
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
from scripts.v6 import distribution_metrics as dm  # noqa: E402

D = 32


def make_songs(rng, n_songs, n_win=40, d=D, shift=0.0, song_sd=0.3, tag="a"):
    """Song-clustered Gaussian windows: each song has its own centre (song_sd) + window noise."""
    out = []
    for i in range(n_songs):
        centre = rng.standard_normal(d) * song_sd + shift
        out.append(dm.Song(f"{tag}{i}", f"{tag}{i:015d}", rng.standard_normal((n_win, d)) + centre))
    return out


@pytest.fixture
def sets():
    rng = np.random.default_rng(123)
    return (make_songs(rng, 12, tag="a"), make_songs(rng, 12, tag="b"),
            make_songs(rng, 12, shift=1.5, tag="c"))


def test_poly_kernel_matches_formula():
    rng = np.random.default_rng(0)
    X, Y = rng.standard_normal((3, D)), rng.standard_normal((4, D))
    K = dm.poly_kernel(X, Y)
    assert K.shape == (3, 4)
    assert np.isclose(K[1, 2], (X[1] @ Y[2] / D + 1.0) ** 3)
    assert np.isclose(dm.mmd2_unbiased(X, Y), dm.mmd2_unbiased(Y, X))


def test_kid_near_zero_same_distribution_and_positive_when_shifted(sets):
    A, B, C = sets
    rng = np.random.default_rng(0)
    same = dm.kid(dm.stack(A)[0], dm.stack(B)[0], rng, subsets=20)
    shifted = dm.kid(dm.stack(A)[0], dm.stack(C)[0], rng, subsets=20)
    song_same = dm.song_level_kid(A, B, rng, n_boot=0)["point"]
    song_shift = dm.song_level_kid(A, C, rng, n_boot=0)["point"]
    assert abs(song_same) < 0.1 * song_shift
    assert shifted["mean"] > 5 * abs(same["mean"])
    assert shifted["mean"] > 0 and song_shift > 0
    assert same["subset_size"] == min(500, 480, 480)


def test_fad_monotone_in_mean_shift():
    rng = np.random.default_rng(1)
    X = rng.standard_normal((400, D))
    vals = [dm.fad(X, rng.standard_normal((400, D)) + s)["value"] for s in (0.0, 0.5, 1.0, 2.0)]
    assert vals == sorted(vals) and vals[-1] > vals[0] + 1.0
    f = dm.fad(X, X)
    assert f["value"] == 0.0 and f["shrinkage_used"] is False  # n=400 >= 10*32
    assert dm.fad(X[:100], X[:100])["shrinkage_used"] is True


def test_density_coverage_identical_sets(sets):
    A, _, _ = sets
    X, ia = dm.stack(A)
    key = np.array([A[i].sha16 for i in ia])
    dc = dm.density_coverage(X, X, k=5, key_x=key, key_y=key)
    assert dc["coverage"] == 1.0
    assert abs(dc["density"] - 1.0) < 1e-9
    # no-key fallback: the zero-distance twin of each reference window also counts -> (k+1)/k
    dc2 = dm.density_coverage(X, X, k=5)
    assert dc2["coverage"] == 1.0 and abs(dc2["density"] - 1.2) < 1e-9


def test_density_coverage_drop_for_shifted(sets):
    A, B, C = sets
    r_same = dm.compute_all(A, B, n_boot=0, subsets=5)["density_coverage"]
    r_shift = dm.compute_all(A, C, n_boot=0, subsets=5)["density_coverage"]
    assert r_same["coverage"] > 0.8 and 0.7 < r_same["density"] < 1.3
    assert r_shift["coverage"] < r_same["coverage"] and r_shift["density"] < r_same["density"]


def test_c2st_half_for_same_distribution_and_one_for_separated(sets):
    A, B, _ = sets
    rng = np.random.default_rng(7)
    far = make_songs(rng, 12, shift=8.0, tag="f")
    same = dm.compute_all(A, B, n_boot=0, subsets=5)["knn"]
    sep = dm.compute_all(A, far, n_boot=0, subsets=5)["knn"]
    assert abs(same["c2st_balanced_accuracy"] - 0.5) < 0.08
    assert abs(same["cand_real_fraction_mean"] - same["null_expectation_real_fraction"]) < 0.08
    assert sep["c2st_balanced_accuracy"] > 0.97
    assert sep["cand_real_fraction_mean"] < 0.05


def test_identical_sets_are_indistinguishable(sets):
    A, _, _ = sets
    r = dm.compute_all(A, A, n_boot=0, subsets=5)
    assert r["knn"]["c2st_balanced_accuracy"] == 0.5
    assert r["fad"]["value"] == 0.0
    assert r["density_coverage"] == {"density": 1.0, "coverage": 1.0, "k": 5}


def test_bootstrap_ci_contains_point_and_is_deterministic(sets):
    A, B, C = sets
    r1 = dm.song_level_kid(A, B, np.random.default_rng(0), n_boot=100)
    r2 = dm.song_level_kid(A, B, np.random.default_rng(0), n_boot=100)
    assert r1 == r2
    lo, hi = r1["bootstrap"]["ci95"]
    assert lo <= r1["point"] <= hi and lo <= 0.0 <= hi  # null: CI covers 0
    assert r1["bootstrap"]["n_boot"] == 100
    rs = dm.song_level_kid(A, C, np.random.default_rng(0), n_boot=100)
    assert rs["bootstrap"]["ci95"][0] > 0.0  # shifted: CI excludes 0


def test_novelty_guard_flags_exact_duplicate(sets):
    A, B, _ = sets
    dup = dm.Song("copy_of_b3", "deadbeefdeadbeef", B[3].emb.copy())
    r = dm.compute_all(A + [dup], B, n_boot=0, subsets=5)
    assert r["novelty"]["n_flagged"] == 1 and r["novelty"]["flagged"] == ["copy_of_b3"]
    rec = [p for p in r["per_song_candidate"] if p["song_id"] == "copy_of_b3"][0]
    assert rec["flagged"] and rec["nearest_ref_song"] == "b3" and rec["nearest_ref_cos"] > 0.999
    assert all(not p["flagged"] for p in r["per_song_candidate"] if p["song_id"] != "copy_of_b3")
    assert len(r["per_song_candidate"]) == len(A) + 1
    assert all("knn_real_fraction_mean" in p for p in r["per_song_candidate"])


def test_compute_all_deterministic_and_schema(sets):
    A, B, _ = sets
    r1 = dm.compute_all(A, B, seed=3, n_boot=20, subsets=5, backbone="synthetic")
    r2 = dm.compute_all(A, B, seed=3, n_boot=20, subsets=5, backbone="synthetic")
    s1 = json.dumps(r1, sort_keys=True, default=str)
    assert s1 == json.dumps(r2, sort_keys=True, default=str)
    for key in ("schema_version", "env", "inputs", "kid", "fad", "density_coverage", "knn", "novelty",
                "per_song_candidate", "n_songs_a", "n_windows_b"):
        assert key in r1
    assert r1["inputs"]["a"] == [s.sha16 for s in A]
    flat = dm.flat_scalars(r1)
    assert {"kid_song", "kid_song_ci95_lo", "fad", "c2st_balanced_accuracy", "coverage"} <= set(flat)


def test_cli_writes_sorted_json(tmp_path, sets):
    A, B, _ = sets
    for name, songs in (("cand", A), ("ref", B)):
        d = tmp_path / name
        d.mkdir()
        for s in songs:
            np.savez(d / f"{s.sha16}.npz", emb=s.emb.astype(np.float32), window_start_s=np.arange(len(s.emb)) * 5.0)
            (d / f"{s.sha16}.json").write_text(json.dumps({"name": s.song_id, "sha16": s.sha16, "path": s.song_id}))
    rc = dm.main(["--candidate", str(tmp_path / "cand"), "--reference", str(tmp_path / "ref"), "--backbone", "syn",
                  "--run-name", "t", "--out-dir", str(tmp_path / "out"), "--bootstrap", "10", "--subsets", "3"])
    assert rc == 0
    out = tmp_path / "out" / "t" / "distribution_syn.json"
    txt = out.read_text()
    obj = json.loads(txt)
    assert txt == json.dumps(obj, sort_keys=True, indent=2) + "\n"
    assert obj["schema_version"] == dm.SCHEMA_VERSION and obj["n_songs_a"] == len(A)
    assert obj["per_song_candidate"][0]["song_id"] in {s.song_id for s in A}
    assert not list((tmp_path / "out" / "t").glob("*.tmp"))
