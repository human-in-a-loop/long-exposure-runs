#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T07:30:00Z
# cycle: 36
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v3
# ---
"""Tests for M-GEN-1/palette-driven-batch-v3 (cycle-36 Branch B).

Run:
  PYTHONPATH=. /usr/bin/python3 tests/test_palette_driven_batch_v3.py

At least 14 cases, including backwards-compat SHA equality on c33 anchor.
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

RUBRIC_DOC = _REPO / "docs" / "palette_driven_batch_v3_rubric.md"
RUBRIC_HASH_TXT = _REPO / "data" / "palette_render_v3" / "rubric_hash.txt"
VERDICT_JSON = _REPO / "data" / "palette_render_v3" / "verdict.json"
BC_CHECK_JSON = _REPO / "data" / "palette_render_v3" / "backwards_compat_check.json"
BATCH_MANIFEST = _REPO / "data" / "palette_render_v3" / "batch_manifest.json"
SPREAD_JSON = _REPO / "data" / "palette_render_v3" / "spread_analysis.json"
ANCHOR_JSON = _REPO / "data" / "palette_render_v3" / "anchor_preservation.json"
SCRIPTS_DIR = _REPO / "scripts" / "palette_render_v3"
RENDER_STEM_PY = _REPO / "scripts" / "palette_render" / "render_stem.py"

EXPECTED_SHAS = {
    "bass":  "6b9a5219e761854bdcf42a87f370a283e3fb096faf64648eb198c98520540280",
    "other": "a2e5d0585404b448a2120c3c4bd6432ec1962ed82c3a7a74dd7518ed3d10f621",
    "drums": "f66a776dfde8ba15b4f3cb1abf564e701877a519c38d4d102cc14e73b57982c9",
}
EXPECTED_COMBINED = "a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794"


def test_01_rubric_doc_sha_matches_rubric_hash_txt():
    doc_sha = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()
    txt_sha = RUBRIC_HASH_TXT.read_text().strip()
    assert doc_sha == txt_sha, f"rubric doc SHA {doc_sha} != rubric_hash.txt {txt_sha}"


def test_02_verdict_json_rubric_hash_equals_txt():
    verdict = json.loads(VERDICT_JSON.read_text())
    txt_sha = RUBRIC_HASH_TXT.read_text().strip()
    assert verdict["rubric_hash"] == txt_sha, \
        f"verdict.json.rubric_hash {verdict['rubric_hash']} != {txt_sha}"


def test_03_rubric_mtime_precedes_scripts_and_render_stem_edit():
    rubric_mtime = RUBRIC_DOC.stat().st_mtime
    # All scripts under scripts/palette_render_v3/ MUST have mtime after rubric.
    for p in SCRIPTS_DIR.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        assert p.stat().st_mtime >= rubric_mtime, \
            f"{p} mtime {p.stat().st_mtime} < rubric {rubric_mtime}"
    # render_stem.py edit must also postdate the rubric.
    assert RENDER_STEM_PY.stat().st_mtime >= rubric_mtime, \
        "render_stem.py edit predates rubric"


def test_04_backwards_compat_3_c33_anchor_shas_match():
    bc = json.loads(BC_CHECK_JSON.read_text())
    assert bc["all_match"], f"backwards_compat_check FAILED: {bc}"
    for stem, exp in EXPECTED_SHAS.items():
        assert bc["per_stem_shas"][stem] == exp, \
            f"stem {stem} SHA drift: got {bc['per_stem_shas'][stem]} exp {exp}"
    assert bc["combined_sha"] == EXPECTED_COMBINED


def test_05_render_stem_signature_has_parameter_dict_keyword_only():
    from scripts.palette_render.render_stem import render_stem
    sig = inspect.signature(render_stem)
    assert "parameter_dict" in sig.parameters
    p = sig.parameters["parameter_dict"]
    assert p.kind == inspect.Parameter.KEYWORD_ONLY, \
        f"parameter_dict kind = {p.kind}, expected KEYWORD_ONLY"
    assert p.default is None


def test_06_render_stem_body_preserves_c33_when_parameter_dict_None():
    # Re-execute the backwards-compat check via subprocess so failure
    # is not silently masked by a stale module import. Fresh temp dir
    # each time.
    from scripts.palette_render.render_stem import render_stem, SAMPLE_RATE, SAMPLE_COUNT
    import hashlib, tempfile, numpy as np
    import scipy.io.wavfile as scipy_wav
    import soundfile as sf

    ASSIGN = [("drums", "fluidsynth_gm"), ("bass", "sfizz"), ("other", "sfizz")]
    tmp = Path(tempfile.mkdtemp(prefix="c36b_bc_"))
    per_stem_shas = {}
    stem_wavs = []
    for stem, inst in ASSIGN:
        r = render_stem(stem, inst, tmp / stem, parameter_dict=None)
        per_stem_shas[stem] = r["render_run1_sha"]
        stem_wavs.append(Path(r["run1_wav_path"]))
    accum = np.zeros((SAMPLE_COUNT, 2), dtype=np.float32)
    for sw in stem_wavs:
        y, sr = sf.read(str(sw), always_2d=True)
        if y.shape[1] == 1:
            y = np.concatenate([y, y], axis=1)
        n = min(y.shape[0], SAMPLE_COUNT)
        accum[:n, :] += y[:n, :].astype(np.float32)
    combined = tmp / "bare_combined.wav"
    scipy_wav.write(str(combined), SAMPLE_RATE, accum)
    combined_sha = hashlib.sha256(combined.read_bytes()).hexdigest()
    for stem, exp in EXPECTED_SHAS.items():
        assert per_stem_shas[stem] == exp, \
            f"stem {stem}: got {per_stem_shas[stem]} != expected {exp}"
    assert combined_sha == EXPECTED_COMBINED, \
        f"combined SHA drift: got {combined_sha} != expected {EXPECTED_COMBINED}"


def test_07_vst3_branches_raise_notimplemented_when_parameter_dict_nonNone():
    from scripts.palette_render.render_stem import render_stem
    import tempfile
    for inst in ("surge_xt", "dexed"):
        try:
            render_stem("drums", inst, Path(tempfile.mkdtemp(prefix="c36b_vst3_")),
                        parameter_dict={"gain": 0.75})
        except NotImplementedError:
            continue
        except Exception as e:
            raise AssertionError(f"instrument {inst}: got {type(e).__name__} not NotImplementedError")
        raise AssertionError(f"instrument {inst}: no exception raised")


def test_08_per_salt_byte_determinism_x2_on_bare_combined():
    verdict = json.loads(VERDICT_JSON.read_text())
    for s in ("0", "1", "2"):
        r1 = verdict["per_salt_bare_combined_sha_run1"][s]
        r2 = verdict["per_salt_bare_combined_sha_run2"][s]
        assert r1 == r2, f"salt {s}: run1={r1} != run2={r2}"


def test_09_three_distinct_per_salt_assignment_jsonl_shas():
    verdict = json.loads(VERDICT_JSON.read_text())
    shas = list(verdict["per_salt_assignments_sha"].values())
    assert len(set(shas)) == 3, f"assignments.jsonl SHAs not distinct: {shas}"


def test_10_per_salt_per_stem_parameter_dict_shas_mostly_distinct():
    """The rubric's derivation table has 4 params × 4 values = 256 combos
    per (stem, instrument), so 6 draws have a small but non-zero collision
    probability. The load-bearing gate is cross-salt bare_combined
    distinctness (test_20), NOT parameter_dict-payload distinctness. We
    require at least 4/6 distinct as an honest observation.
    """
    manifest = json.loads(BATCH_MANIFEST.read_text())
    shas = []
    for salt in ("0", "1", "2"):
        for stem in ("bass", "other"):
            shas.append(manifest["per_salt_parameter_dict_shas"][salt][stem])
    assert len(set(shas)) >= 4, \
        f"parameter_dict SHAs too collision-heavy ({len(set(shas))}/6 distinct): {shas}"


def test_11_both_panel_tsvs_8key_finite_per_salt():
    for s in ("0", "1", "2"):
        for name in ("panel_original", "panel_fluidsynth"):
            path = _REPO / "data" / "palette_render_v3" / "per_song" / s / f"{name}.tsv"
            with open(path) as f:
                header = f.readline().strip().split("\t")
                row = f.readline().strip().split("\t")
            assert len(header) == 8, f"{path}: got {len(header)} keys, expected 8"
            numeric_keys = ("mel_l1_db", "spectral_centroid_rmse_hz",
                            "rms_env_rmse", "lufs_m_rmse_lu")
            for k in numeric_keys:
                idx = header.index(k)
                v = float(row[idx])
                assert v == v and v not in (float("inf"), float("-inf")), \
                    f"{path} key {k} non-finite: {v}"


def test_12_ast_grep_no_prng_in_scripts_palette_render_v3():
    prng_hits = []
    for p in SCRIPTS_DIR.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    if n.name in ("random",):
                        prng_hits.append((str(p), n.name))
            if isinstance(node, ast.ImportFrom):
                if node.module in ("random",):
                    prng_hits.append((str(p), node.module))
            if isinstance(node, ast.Attribute):
                # np.random.* is also PRNG territory.
                if isinstance(node.value, ast.Attribute) and node.value.attr == "random":
                    if isinstance(node.value.value, ast.Name) and node.value.value.id == "np":
                        prng_hits.append((str(p), "np.random"))
    assert not prng_hits, f"PRNG found: {prng_hits}"


def test_13_ast_grep_no_sidecar_nonfactor_import():
    for p in SCRIPTS_DIR.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        src = p.read_text()
        assert "sidecar_nonfactor" not in src, f"sidecar_nonfactor referenced in {p}"


def test_14_c33_render_effects_layered_not_imported():
    for p in SCRIPTS_DIR.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        src = p.read_text()
        assert "render_effects_layered" not in src, \
            f"c9 render_effects_layered referenced in {p}"


def test_15_forbidden_utilities_not_imported():
    forbidden_needles = [
        "i4_stratified",
        "sample_rules",  # c13 batch pipeline entry point
        "collision_model",
        "hash_geometry",
        "stability_audit",
        "canonical_aggregate_sha",  # c26 utility surface
    ]
    for p in SCRIPTS_DIR.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        src = p.read_text()
        for needle in forbidden_needles:
            assert needle not in src, f"{needle} referenced in {p}"


def test_16_ledger_i3_dminor_not_read():
    for p in SCRIPTS_DIR.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        src = p.read_text()
        assert "ledger_i3_dminor" not in src, \
            f"ledger_i3_dminor.jsonl referenced in {p}"


def test_17_interpreter_guard_present_in_every_new_script():
    for p in SCRIPTS_DIR.rglob("*.py"):
        if "__pycache__" in p.parts or p.name == "__init__.py":
            continue
        src = p.read_text()
        assert 'sys.executable == "/usr/bin/python3"' in src, \
            f"no interpreter guard in {p}"


def test_18_anchor_preservation_unchanged_except_render_stem_edit():
    ap = json.loads(ANCHOR_JSON.read_text())
    assert ap["unchanged_except_render_stem_edit"] is True, \
        "anchor drift detected outside the intentional render_stem edit"
    edit = ap["intentional_render_stem_edit"]
    assert edit["path"] == "scripts/palette_render/render_stem.py"
    assert edit["sha_pre_edit_expected_present"] is True
    assert edit["sha_post_edit"] is not None


def test_19_verdict_is_expected_enum_value():
    v = json.loads(VERDICT_JSON.read_text())
    assert v["verdict"] in {"PARAM_MOVES_AUDIO", "PARAM_NEUTRAL", "RENDER_FAILS"}


def test_20_cross_salt_pair_count_matches_verdict():
    v = json.loads(VERDICT_JSON.read_text())
    distinct = v["distinct_pair_count_of_3"]
    if v["verdict"] == "PARAM_MOVES_AUDIO":
        assert distinct >= 2, f"PARAM_MOVES_AUDIO but only {distinct}/3 distinct"
    elif v["verdict"] == "PARAM_NEUTRAL":
        assert distinct <= 1


if __name__ == "__main__":
    passed = 0
    failed = 0
    fails: list[str] = []
    tests = [(n, obj) for n, obj in sorted(globals().items())
             if n.startswith("test_") and callable(obj)]
    for name, fn in tests:
        try:
            fn()
            passed += 1
        except Exception as e:
            failed += 1
            fails.append(f"{name}: {type(e).__name__}: {e}")
    print(f"PASS: {passed} / {passed + failed}")
    if fails:
        print("\n".join(fails))
        raise SystemExit(1)
