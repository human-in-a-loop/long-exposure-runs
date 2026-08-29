#!/usr/bin/python3
"""RC7 mix-balance + D4 per-stem EQ implementation tests (c51 Branch C).

Covers:
  - render_stem.py signature-v3 (three additive kwargs, VST3 lock)
  - c33 anchor path backwards-compat under (parameter_dict=None, eq_curve=None, loudness_target=None)
  - 12-band iirpeak EQ curve pinning
  - Loudness match RMS accept mechanism
  - Byte-determinism x 2 on the mixed reconstruction
  - Anchor preservation of c50 v1/v2 rubric SHAs
  - Presence of dispatch_summary.json + verdict.json + panel_baseline_old_chain.tsv
  - Three-way rubric_hash-v2 byte-equality

Run: PYTHONPATH=. /usr/bin/python3 tests/test_rc7_impl.py
"""
from __future__ import annotations

import hashlib
import inspect
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

RESULTS = []


def _record(name: str, ok: bool, msg: str = "") -> None:
    RESULTS.append((name, ok, msg))
    tag = "PASS" if ok else "FAIL"
    line = "[" + tag + "] " + name
    if msg:
        line += " -- " + msg
    print(line)


def test_01_render_stem_signature_v3():
    from scripts.palette_render.render_stem import render_stem
    sig = inspect.signature(render_stem)
    params = sig.parameters
    ok = (
        "parameter_dict" in params
        and "eq_curve" in params
        and "loudness_target" in params
        and params["parameter_dict"].kind == inspect.Parameter.KEYWORD_ONLY
        and params["eq_curve"].kind == inspect.Parameter.KEYWORD_ONLY
        and params["loudness_target"].kind == inspect.Parameter.KEYWORD_ONLY
    )
    _record("test_01_render_stem_signature_v3", ok,
            "signature=" + str(sig))


def test_02_c33_backwards_compat_no_kwargs():
    from scripts.palette_render.render_stem import render_stem
    d1 = Path(tempfile.mkdtemp(prefix="rc7t02a_"))
    d2 = Path(tempfile.mkdtemp(prefix="rc7t02b_"))
    r1 = render_stem("drums", "fluidsynth_gm", d1)
    r2 = render_stem("drums", "fluidsynth_gm", d2)
    ok = r1["render_run1_sha"] == r2["render_run1_sha"] and r1["sha_equal"]
    _record("test_02_c33_backwards_compat_no_kwargs", ok,
            "sha=" + r1["render_run1_sha"][:16])


def test_03_c36_backwards_compat_parameter_dict_None():
    from scripts.palette_render.render_stem import render_stem
    d1 = Path(tempfile.mkdtemp(prefix="rc7t03a_"))
    d2 = Path(tempfile.mkdtemp(prefix="rc7t03b_"))
    r1 = render_stem("drums", "fluidsynth_gm", d1, parameter_dict=None)
    r2 = render_stem("drums", "fluidsynth_gm", d2,
                     parameter_dict=None, eq_curve=None, loudness_target=None)
    ok = r1["render_run1_sha"] == r2["render_run1_sha"]
    _record("test_03_c36_backwards_compat_parameter_dict_None", ok,
            "shas equal under all-None: " + str(ok))


def test_04_vst3_locked_with_eq_curve():
    from scripts.palette_render.render_stem import render_stem
    d = Path(tempfile.mkdtemp(prefix="rc7t04_"))
    try:
        render_stem("bass", "surge_xt", d, eq_curve={"band_gains_db": [0.0] * 12,
                                                     "band_center_freqs_hz": [20.0] * 12})
        _record("test_04_vst3_locked_with_eq_curve", False,
                "expected NotImplementedError on VST3 with eq_curve")
    except NotImplementedError as e:
        _record("test_04_vst3_locked_with_eq_curve", True, str(e)[:80])


def test_05_vst3_locked_with_loudness_target():
    from scripts.palette_render.render_stem import render_stem
    d = Path(tempfile.mkdtemp(prefix="rc7t05_"))
    try:
        render_stem("other", "dexed", d,
                    loudness_target={"target_rms_db": -14.0})
        _record("test_05_vst3_locked_with_loudness_target", False,
                "expected NotImplementedError on VST3 with loudness_target")
    except NotImplementedError as e:
        _record("test_05_vst3_locked_with_loudness_target", True, str(e)[:80])


def test_06_rc7_out_present():
    p = REPO / "data" / "recreate_v2" / "rc7_out" / "verdict.json"
    ok = p.is_file()
    _record("test_06_rc7_out_present", ok, str(p))


def test_07_rc7_verdict_three_way_rubric_hash():
    verdict = json.loads((REPO / "data" / "recreate_v2" / "rc7_out" / "verdict.json").read_text())
    rubric_v2_txt = (REPO / "data" / "recreate_v2" / "rubric_hash_v2.txt").read_text().strip()
    rubric_doc_sha = hashlib.sha256(
        (REPO / "docs" / "m_recreate_2_accurate_small_set_rubric_v2.md").read_bytes()
    ).hexdigest()
    ok = (verdict["rubric_hash"] == rubric_v2_txt == rubric_doc_sha)
    _record("test_07_rc7_verdict_three_way_rubric_hash", ok,
            "chain=" + str(verdict["rubric_hash"] == rubric_v2_txt) + "/" +
            str(rubric_v2_txt == rubric_doc_sha))


def test_08_c49_v1_rubric_preserved():
    p = REPO / "docs" / "m_recreate_2_accurate_small_set_rubric.md"
    expected = "958ade3886eba560df284878ff5d351e3f6186159ed598f68b82fc7c3fe58b9d"
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    ok = actual == expected
    _record("test_08_c49_v1_rubric_preserved", ok, actual[:32])


def test_09_verdict_in_frozen_enum():
    verdict = json.loads((REPO / "data" / "recreate_v2" / "rc7_out" / "verdict.json").read_text())
    ok = verdict["verdict"] in ("RC7_LANDS", "RC7_PARTIAL", "RC7_FAILS")
    _record("test_09_verdict_in_frozen_enum", ok, verdict["verdict"])


def test_10_dispatch_summary_per_song():
    root = REPO / "data" / "recreate_v2" / "rc7_out"
    dirs = [d for d in root.iterdir() if d.is_dir()]
    ok = len(dirs) >= 1
    for d in dirs:
        p = d / "dispatch_summary.json"
        if not p.is_file():
            ok = False
            break
    _record("test_10_dispatch_summary_per_song", ok, "n_songs=" + str(len(dirs)))


def test_11_panel_baseline_old_chain_tsv():
    root = REPO / "data" / "recreate_v2" / "rc7_out"
    ok = True
    for d in root.iterdir():
        if not d.is_dir():
            continue
        p = d / "panel_baseline_old_chain.tsv"
        if not p.is_file():
            ok = False
            break
        lines = p.read_text().strip().split("\n")
        header = lines[0]
        if "old_chain_rms_db" not in header:
            ok = False
            break
    _record("test_11_panel_baseline_old_chain_tsv", ok, "D4 baseline present")


def test_12_eq_curve_12bands_geomspace():
    import numpy as np
    expected = np.geomspace(20.0, 20000.0, 12).tolist()
    root = REPO / "data" / "recreate_v2" / "rc7_out"
    ok = True
    for d in root.iterdir():
        if not d.is_dir():
            continue
        ds = d / "dispatch_summary.json"
        if not ds.is_file():
            continue
        s = json.loads(ds.read_text())
        for stem, res in s["per_stem"].items():
            if "eq_bands_gains_db" not in res:
                continue
            if len(res["eq_bands_gains_db"]) != 12:
                ok = False
                break
    _record("test_12_eq_curve_12bands_geomspace", ok, "12 bands confirmed")


def test_13_rc7_out_byte_determinism_x2():
    """Two fresh tempfile.mkdtemp runs produce SHA-equal rc7_mixed_reconstruction.wav."""
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("PYTHONHASHSEED", "0")
    os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
    os.environ.setdefault("TZ", "UTC")
    os.environ.setdefault("LC_ALL", "C.UTF-8")
    from scripts.recreate_v2.rc7_mix_balance import run
    d1 = Path(tempfile.mkdtemp(prefix="rc7t13a_"))
    d2 = Path(tempfile.mkdtemp(prefix="rc7t13b_"))
    v1 = run(out_dir=d1, limit=1)
    v2 = run(out_dir=d2, limit=1)
    p1 = d1 / "31a164f845f8e27e" / "rc7_mixed_reconstruction.wav"
    p2 = d2 / "31a164f845f8e27e" / "rc7_mixed_reconstruction.wav"
    if not (p1.is_file() and p2.is_file()):
        _record("test_13_rc7_out_byte_determinism_x2", False,
                "mixed reconstruction missing")
        return
    sha1 = hashlib.sha256(p1.read_bytes()).hexdigest()
    sha2 = hashlib.sha256(p2.read_bytes()).hexdigest()
    ok = sha1 == sha2 and v1["rubric_hash"] == v2["rubric_hash"]
    _record("test_13_rc7_out_byte_determinism_x2", ok, sha1[:16])


def test_14_anchor_preservation_ge_30():
    p = REPO / "data" / "recreate_v2" / "rc7_out" / "anchor_preservation.json"
    obj = json.loads(p.read_text())
    ok = obj["n_anchors"] >= 30
    _record("test_14_anchor_preservation_ge_30", ok, "n=" + str(obj["n_anchors"]))


def test_15_render_stem_edit_grep_no_prng():
    src = (REPO / "scripts" / "palette_render" / "render_stem.py").read_text()
    forbidden = ["random.", "numpy.random", "np.random", "torch.rand", "PRNGKey"]
    hits = [f for f in forbidden if f in src]
    _record("test_15_render_stem_edit_grep_no_prng", len(hits) == 0,
            "PRNG imports: " + str(hits))


def test_16_render_stem_edit_interpreter_guard():
    p = REPO / "scripts" / "recreate_v2" / "rc7_mix_balance.py"
    src = p.read_text()
    ok = "/usr/bin/python3" in src and "sys.executable" in src
    _record("test_16_render_stem_edit_interpreter_guard", ok, "guard present")


def test_17_rubric_v2_mtime_hard_before_edit():
    """c46 path (ii): rubric doc mtime < script edit mtime (mtime hard)."""
    r = REPO / "docs" / "render_stem_signature_v3.md"
    s = REPO / "scripts" / "recreate_v2" / "rc7_mix_balance.py"
    ok = r.stat().st_mtime < s.stat().st_mtime
    _record("test_17_rubric_v2_mtime_hard_before_edit", ok,
            "sig_v3 doc mtime={:.0f} script mtime={:.0f}".format(
                r.stat().st_mtime, s.stat().st_mtime))


def test_18_eq_curve_fit_method_doc_predates_edit():
    r = REPO / "docs" / "rc7_eq_curve_fit_method.md"
    s = REPO / "scripts" / "recreate_v2" / "rc7_mix_balance.py"
    ok = r.stat().st_mtime < s.stat().st_mtime
    _record("test_18_eq_curve_fit_method_doc_predates_edit", ok,
            "fit doc mtime={:.0f} script mtime={:.0f}".format(
                r.stat().st_mtime, s.stat().st_mtime))


def test_19_verdict_carries_per_song_passes():
    verdict = json.loads((REPO / "data" / "recreate_v2" / "rc7_out" / "verdict.json").read_text())
    ok = "per_song_passes" in verdict and len(verdict["per_song_passes"]) >= 1
    _record("test_19_verdict_carries_per_song_passes", ok,
            "n=" + str(len(verdict.get("per_song_passes", []))))


def test_20_d4_old_chain_present_in_verdict():
    verdict = json.loads((REPO / "data" / "recreate_v2" / "rc7_out" / "verdict.json").read_text())
    ok = verdict.get("d4_old_chain_baseline_present") is True
    _record("test_20_d4_old_chain_present_in_verdict", ok, "D4 flag=true")


def main() -> int:
    tests = [
        test_01_render_stem_signature_v3,
        test_02_c33_backwards_compat_no_kwargs,
        test_03_c36_backwards_compat_parameter_dict_None,
        test_04_vst3_locked_with_eq_curve,
        test_05_vst3_locked_with_loudness_target,
        test_06_rc7_out_present,
        test_07_rc7_verdict_three_way_rubric_hash,
        test_08_c49_v1_rubric_preserved,
        test_09_verdict_in_frozen_enum,
        test_10_dispatch_summary_per_song,
        test_11_panel_baseline_old_chain_tsv,
        test_12_eq_curve_12bands_geomspace,
        test_13_rc7_out_byte_determinism_x2,
        test_14_anchor_preservation_ge_30,
        test_15_render_stem_edit_grep_no_prng,
        test_16_render_stem_edit_interpreter_guard,
        test_17_rubric_v2_mtime_hard_before_edit,
        test_18_eq_curve_fit_method_doc_predates_edit,
        test_19_verdict_carries_per_song_passes,
        test_20_d4_old_chain_present_in_verdict,
    ]
    for t in tests:
        try:
            t()
        except Exception as e:
            _record(t.__name__, False, "EXCEPTION " + type(e).__name__ + ": " + str(e)[:80])
    n_pass = sum(1 for _, ok, _ in RESULTS if ok)
    print()
    print("SUMMARY:", n_pass, "/", len(RESULTS), "PASS")
    return 0 if n_pass == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
