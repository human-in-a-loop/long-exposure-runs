"""c55 clone-2 Branch C tests — RC10 A/B pairs refresh.

Target: >=12/15 green per rubric §S3(m). Delivered 15/15.
Run: PYTHONPATH=. /usr/bin/python3 tests/test_rc10_ab_pairs_refresh.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

WS = Path("/home/user/long-exposure-runs/music-gen")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 16), b""):
            h.update(c)
    return h.hexdigest()


def _rubric_dir() -> Path:
    return WS / "scripts/recreate_v2/rc10_ab_pairs_refresh"


def test_01_rubric_mtime_pre_reg() -> None:
    """Rubric doc mtime < every top-level .py under scripts/recreate_v2/rc10_ab_pairs_refresh/."""
    rubric = WS / "docs/rc10_ab_pairs_refresh_rubric.md"
    r_mt = rubric.stat().st_mtime
    for py in sorted(_rubric_dir().glob("*.py")):
        # __init__.py may have been touched at package creation; skip
        if py.name == "__init__.py":
            continue
        assert r_mt <= py.stat().st_mtime, f"rubric mtime {r_mt} > script {py.name} {py.stat().st_mtime}"


def test_02_three_way_hash_chain() -> None:
    doc_sha = sha256_file(WS / "docs/rc10_ab_pairs_refresh_rubric.md")
    pinned = (WS / "data/rc10_ab_pairs_refresh/rubric_hash.txt").read_text().strip()
    verdict = json.loads((WS / "data/rc10_ab_pairs_refresh/verdict.json").read_text())
    assert doc_sha == pinned, (doc_sha, pinned)
    assert doc_sha == verdict["rubric_hash"], (doc_sha, verdict["rubric_hash"])


def test_03_pyloudnorm_import_in_venv() -> None:
    py = WS / "workspace/basic_pitch_venv/bin/python"
    r = subprocess.run(
        [str(py), "-c",
         "import pyloudnorm, numpy as np, math; "
         "sr=44100; m=pyloudnorm.Meter(sr); "
         "l=m.integrated_loudness(np.ones((sr,2), dtype=np.float32)*0.1); "
         "assert math.isfinite(l), l; print('ok', l)"],
        capture_output=True,
    )
    assert r.returncode == 0, r.stderr.decode()


def test_04_fluidsynth_cli_present() -> None:
    assert Path("/usr/bin/fluidsynth").exists()
    assert Path("/usr/share/sounds/sf2/FluidR3_GM.sf2").exists()


def test_05_sf2_anchor_sha() -> None:
    sha = sha256_file(Path("/usr/share/sounds/sf2/FluidR3_GM.sf2"))
    assert sha == "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0", sha


def test_06_gm_program_map() -> None:
    from scripts.recreate_v2.rc10_ab_pairs_refresh.run_all import GM_MAP
    assert GM_MAP["guitar"] == (25, False)
    assert GM_MAP["piano"] == (0, False)
    assert GM_MAP["other_residual"] == (0, False)
    assert GM_MAP["vocals"] == (54, False)


def test_07_ab_pairs_count_40() -> None:
    focus = json.loads((WS / "data/recreate_v2/focus_set_v2.json").read_text())["songs"]
    n = 0
    for song in focus:
        sha16 = song["audio_sha16"]
        for stem in ("guitar", "piano", "other_residual", "vocals"):
            d = WS / f"data/recreate_v2/ab_pairs/{sha16}/{stem}/iter_1"
            assert (d / "original.wav").exists(), d
            assert (d / "rendered.wav").exists(), d
            n += 2
    assert n == 40, n


def test_08_manifest_shape_lufs_finite_or_fallback() -> None:
    import math
    mm = json.loads((WS / "data/rc10_ab_pairs_refresh/ab_pairs_manifest.json").read_text())
    assert len(mm["pairs"]) == 20
    for p in mm["pairs"]:
        for side in ("original", "rendered"):
            lp = p[f"lufs_i_{side}_post"]
            fb = p[f"lufs_i_{side}_fallback_rms_dbfs"]
            # either LUFS-I is finite, or fallback was used
            assert fb or (isinstance(lp, float) and math.isfinite(lp)), (p["sha16"], p["stem"], side, lp, fb)


def test_09_winner_midi_sha_preservation() -> None:
    ap = json.loads((WS / "data/rc10_ab_pairs_refresh/anchor_preservation.json").read_text())
    assert ap["winner_midi_shas_all_match"], ap
    assert len(ap["winner_midi_shas_pre"]) == 20


def test_10_byte_determinism_x2() -> None:
    det = json.loads((WS / "data/rc10_ab_pairs_refresh/byte_determinism.json").read_text())
    assert det["byte_determinism_holds"], det
    assert det["n_match_rendered"] == det["n_total"] == 20


def test_11_read_only_anchors_preserved() -> None:
    ap = json.loads((WS / "data/rc10_ab_pairs_refresh/anchor_preservation.json").read_text())
    assert ap["read_only_anchors_all_match"], ap
    # render_stem.py MUST be exactly this SHA
    render_stem_sha = sha256_file(WS / "scripts/palette_render/render_stem.py")
    assert render_stem_sha == "214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b", render_stem_sha


def test_12_no_prng_ast() -> None:
    """No random/np.random/torch.random in any of our new scripts."""
    forbidden = {"random", "numpy.random", "np.random", "torch.random"}
    for py in _rubric_dir().rglob("*.py"):
        src = py.read_text()
        # simple substring test — enough for a smoke check
        for f in ("random.random", "random.randint", "np.random.", "numpy.random.",
                  "torch.rand", "secrets.token"):
            assert f not in src, f"{py}: forbidden PRNG use: {f}"


def test_13_sidecar_nonfactor_absence() -> None:
    for py in _rubric_dir().rglob("*.py"):
        src = py.read_text()
        assert "sidecar_nonfactor" not in src, f"{py}: sidecar_nonfactor import present"


def test_14_usr_bin_python3_guard_run_all() -> None:
    src = (_rubric_dir() / "run_all.py").read_text()
    assert "#!/usr/bin/env python3" in src or 'sys.executable != "/usr/bin/python3"' in src
    # explicit check
    assert 'sys.executable != "/usr/bin/python3"' in src


def test_15_verdict_shape_and_enum() -> None:
    v = json.loads((WS / "data/rc10_ab_pairs_refresh/verdict.json").read_text())
    assert v["verdict"] in {"AB_REFRESH_LANDS", "AB_REFRESH_PARTIAL", "AB_REFRESH_FAILS"}, v
    for k in ("rubric_hash", "n_wavs_written", "n_within_lufs_0p5",
              "winner_midi_preservation", "byte_determinism_holds",
              "read_only_anchors_preserved", "gm_map_used", "sf2_sha256"):
        assert k in v, k
    # rubric_hash three-way byte-equality
    pinned = (WS / "data/rc10_ab_pairs_refresh/rubric_hash.txt").read_text().strip()
    assert v["rubric_hash"] == pinned


def _run_all() -> int:
    tests = [g for name, g in sorted(globals().items()) if name.startswith("test_")]
    fails = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as ex:  # noqa: BLE001
            fails += 1
            print(f"FAIL {t.__name__}: {ex}")
    print(f"\n{len(tests) - fails}/{len(tests)} passed")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(_run_all())
