#!/usr/bin/python3
"""v6 Phase 4 tests — render_song end to end through compose_v6 --renderer both on one fixture song (< 90 s): v6 mix +
GM A/B mix side by side, patch_plan / mix_manifest / render_manifest written, LUFS on target, replay proof holds, and the
default (--renderer gm) manifest layout is unchanged.

Run: /usr/bin/python3 -m pytest tests/test_v6_render_song.py -q
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

PY = "/usr/bin/python3"
CLI = [PY, "scripts/v6/gen/compose_v6.py", "--iteration", "1", "--seed", "3", "--fixtures", "--bars", "16", "--donors", "fixture_b", "--bpm", "112"]


def test_01_compose_renderer_both_end_to_end_under_90s() -> None:
    import soundfile as sf
    from scripts.v6.gen.render_v6 import mix
    with tempfile.TemporaryDirectory(prefix="v6render_e2e_") as td:
        t0 = time.time()
        r = subprocess.run(CLI + ["--renderer", "both", "--out", td], capture_output=True, text=True, cwd=str(_ROOT))
        wall = time.time() - t0
        assert r.returncode == 0, r.stdout + r.stderr
        assert wall < 90.0, f"render took {wall:.1f}s"
        sd = Path(td) / "gen_v6_song_1_donor_fixture_b"
        for f in ("ab_mix.wav", "ab_mix_gm.wav", "patch_plan.json", "mix_manifest.json", "render_manifest.json", "ab_mix.manifest.json", "render_midi/bass.mid", "render_midi/drums.mid"):
            assert (sd / f).exists(), f
        assert not (sd / "per_track").exists() or not list((sd / "per_track").glob("*.wav"))
        man = json.loads((sd / "ab_mix.manifest.json").read_text())
        assert man["renderer"] == "both" and man["render"]["renderer"] == "v6" and man["ab_mix_gm_sha256"] == man["render_gm"]["ab_mix_sha256"]
        assert man["ab_mix_sha256"] == hashlib.sha256((sd / "ab_mix.wav").read_bytes()).hexdigest() != man["ab_mix_gm_sha256"]
        pp = json.loads((sd / "patch_plan.json").read_text())
        assert pp["donor"] == "fixture_b" and pp["seed"] == 3 and pp["iteration"] == 1 and set(pp["selection"]) >= {"bass", "drums", "keys", "melody"}
        assert pp["stems_found"] == {} and all(s["method"].startswith("band_prior") for s in pp["selection"].values())
        mm = json.loads((sd / "mix_manifest.json").read_text())
        ref = mix.load_reference()
        assert abs(mm["master"]["lufs_final"] - ref["target_lufs"]) <= 0.5 and mm["master"]["true_peak_dbtp_final"] <= mix.TRUE_PEAK_DBTP + 0.05 and mm["master"]["clipped_samples"] == 0
        x, sr = sf.read(str(sd / "ab_mix.wav"), dtype="float32", always_2d=True)
        g, _ = sf.read(str(sd / "ab_mix_gm.wav"), dtype="float32", always_2d=True)
        assert sr == 44100 and x.shape[1] == 2 and abs(x.shape[0] / sr - 16 * 4 * 60.0 / 112.0) < 6.0 and float(abs(x).max()) < 1.0
        assert abs(len(x) - len(g)) / sr < 6.0  # same song (tails differ by sampler release)
        rm = json.loads((sd / "render_manifest.json").read_text())
        assert rm["deterministic_backends_only"] and set(rm["roles"]) == set(pp["selection"])
        for role, info in rm["roles"].items():
            if info.get("n_notes") == 0:
                continue
            assert info["expression"]["velocity"]["realized_span"] >= 60, (role, info["expression"]["velocity"])
            assert (sd / info["midi"]).exists()
        print(f"test_01 PASS: compose --renderer both in {wall:.1f}s; roles {sorted(rm['roles'])}; LUFS {mm['master']['lufs_final']} (target {ref['target_lufs']}); gm A/B written")


def test_02_render_song_replay_proof_and_gm_default_unchanged() -> None:
    from scripts.v6.gen.render_v6 import render_song, select
    with tempfile.TemporaryDirectory(prefix="v6render_gm_") as td:
        r = subprocess.run(CLI + ["--out", td, "--no-render"], capture_output=True, text=True, cwd=str(_ROOT))
        assert r.returncode == 0, r.stdout + r.stderr
        sd = Path(td) / "gen_v6_song_1_donor_fixture_b"
        man = json.loads((sd / "ab_mix.manifest.json").read_text())
        assert "renderer" not in man and "render" not in man  # default gm path: Phase-2 manifest keys only
        pool = select.load_pool()
        out = Path(td) / "v6"
        m1 = render_song.render_song(sd, "fixture_b", iteration=1, seed=3, out_dir=out, band=7, pool=pool, log=lambda *a: None)
        proof = render_song.prove_replay(sd, "fixture_b", m1, out, iteration=1, seed=3, band=7, pool=pool)
        assert proof["verdict"] == "REPLAY_PROOF_HOLDS", proof
        assert (out / "ab_mix.replay_proof.json").exists() and (out / "patch_plan.json").exists()
        assert m1["band"] == 7 and json.loads((out / "patch_plan.json").read_text())["band_source"] == "argument"
        pt = out / "per_track"
        assert not pt.exists() or not list(pt.glob("*.wav"))
        m2 = render_song.render_song(sd, "fixture_b", iteration=1, seed=3, out_dir=Path(td) / "keep", band=7, pool=pool, keep_per_track=True, log=lambda *a: None)
        kept = sorted(p.name for p in (Path(td) / "keep" / "per_track").glob("*.wav"))
        assert kept == sorted(f"{r}.wav" for r in m2["roles"] if m2["roles"][r].get("n_notes") != 0) and m2["ab_mix_sha256"] == m1["ab_mix_sha256"]
        # --keep-stems (iteration 05): the Demucs-style groups land in stems/, the mix stays byte-identical, manifests record them
        m3 = render_song.render_song(sd, "fixture_b", iteration=1, seed=3, out_dir=Path(td) / "grp", band=7, pool=pool, keep_stems=True, log=lambda *a: None)
        assert m3["ab_mix_sha256"] == m1["ab_mix_sha256"] and m1["stems_kept"] == {}
        grp = sorted(p.name for p in (Path(td) / "grp" / "stems").glob("*.wav"))
        assert grp == sorted(f"{g}.wav" for g in m3["stems_kept"]) and {"drums", "bass"} <= set(m3["stems_kept"]) and "other" in m3["stems_kept"]
        import soundfile as sf
        gx, gsr = sf.read(str(Path(td) / "grp" / "stems" / "drums.wav"), dtype="float32", always_2d=True)
        mx, _ = sf.read(str(Path(td) / "grp" / "ab_mix.wav"), dtype="float32", always_2d=True)
        assert gsr == 44100 and gx.shape == mx.shape and float(np.abs(gx).max()) > 0.01
        assert set(sum((v["roles"] for v in m3["stems_kept"].values()), [])) == {r for r in m3["roles"] if m3["roles"][r].get("n_notes") != 0}
        mm = json.loads((Path(td) / "grp" / "mix_manifest.json").read_text())
        assert mm["stems_kept"] == m3["stems_kept"] and all(hashlib.sha256((Path(td) / "grp" / v["path"]).read_bytes()).hexdigest() == v["sha256"] for v in mm["stems_kept"].values())
        print(f"test_02 PASS: gm default manifest unchanged; v6 replay proof holds ({m1['wall_s']}s); --keep-per-track keeps {kept}; --keep-stems writes {grp}")


if __name__ == "__main__":
    test_01_compose_renderer_both_end_to_end_under_90s()
    test_02_render_song_replay_proof_and_gm_default_unchanged()
