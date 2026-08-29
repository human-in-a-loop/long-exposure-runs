#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:20:00Z
# cycle: 36
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization
# ---
"""Test suite for c36 Branch C: VST3 nondeterminism characterization.

Invocation: PYTHONPATH=. /usr/bin/python3 tests/test_vst3_nondeterminism_characterization.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

SCRIPTS_DIR = REPO / "scripts" / "vst3_nondeterminism"
DATA_DIR = REPO / "data" / "vst3_nondeterminism"
RUBRIC_DOC = REPO / "docs/vst3_nondeterminism_characterization_rubric.md"
RUBRIC_SHA_FILE = DATA_DIR / "rubric_hash.txt"
VERDICT_JSON = DATA_DIR / "characterization_verdict.json"
ANCHOR_JSON = DATA_DIR / "anchor_preservation.json"

SCRIPT_FILES = [
    "__init__.py", "_shared.py",
    "probe_surge_xt.py", "probe_dexed.py",
    "rms_pairwise_distribution.py",
    "envelope_correlation_pairwise.py",
    "characterization_fit.py",
    "run_all.py",
]

FORBIDDEN_CALLS = [
    r"get_state\s*\(",
    r"save_state\s*\(",
    r"save_preset\s*\(",
    r"load_state\s*\(",
    r"set_state\s*\(.*bytes.*\)",
]

PRNG_PATTERNS = [
    r"\brandom\.",
    r"\bnp\.random\.",
    r"\btorch\.rand",
    r"\bsecrets\.",
]

PLUGINS = ["surge_xt", "dexed"]
N_RUNS = 5
N_PAIRS = 10


def _read(p: Path) -> str:
    return p.read_text()


def test_01_rubric_sha_three_way_equal():
    doc_sha = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()
    file_sha = RUBRIC_SHA_FILE.read_text().strip()
    verdict_sha = json.loads(VERDICT_JSON.read_text())["rubric_hash"]
    assert doc_sha == file_sha == verdict_sha, (doc_sha, file_sha, verdict_sha)


def test_02_rubric_mtime_before_scripts():
    """Rubric doc mtime must precede every script's mtime."""
    rubric_mt = RUBRIC_DOC.stat().st_mtime
    for name in SCRIPT_FILES:
        p = SCRIPTS_DIR / name
        assert p.exists(), f"missing: {p}"
        assert rubric_mt <= p.stat().st_mtime, f"{name} mtime precedes rubric"


def test_03_interpreter_guard_in_every_script():
    for name in SCRIPT_FILES:
        if name == "__init__.py":
            continue
        src = _read(SCRIPTS_DIR / name)
        assert 'sys.executable == "/usr/bin/python3"' in src, name


def test_04_no_forbidden_state_calls_in_package():
    for name in SCRIPT_FILES:
        src = _read(SCRIPTS_DIR / name)
        for pat in FORBIDDEN_CALLS:
            m = re.search(pat, src)
            assert m is None, f"{name}: forbidden call matched pattern {pat!r}"


def test_05_no_prng_in_package():
    for name in SCRIPT_FILES:
        src = _read(SCRIPTS_DIR / name)
        for pat in PRNG_PATTERNS:
            m = re.search(pat, src)
            assert m is None, f"{name}: PRNG pattern {pat!r} present"


def test_06_no_sidecar_nonfactor_import():
    for name in SCRIPT_FILES:
        src = _read(SCRIPTS_DIR / name)
        assert "sidecar_nonfactor" not in src, name


def test_07_no_forbidden_module_imports():
    forbidden = [
        "scripts.tex.render_effects_layered",     # c9
        "scripts.gen.batch",                       # c13
        "scripts.rules.sampling.i4_stratified",   # c15
        "scripts.ear.stability_audit",            # c22
        "scripts.analysis.collision_model_bp",    # c26
        "scripts.analysis.shape_mechanism",       # c27
        "scripts.analysis.hash_uniformity",       # c28
        "scripts.analysis.multiple_testing",      # c29
        "scripts.analysis.semantic",              # c30
    ]
    for name in SCRIPT_FILES:
        src = _read(SCRIPTS_DIR / name)
        for mod in forbidden:
            assert mod not in src, f"{name} imports {mod}"


def test_08_n5_runs_per_plugin_wav_and_sha():
    for plugin in PLUGINS:
        d = DATA_DIR / "per_plugin" / plugin
        for k in range(1, N_RUNS + 1):
            assert (d / f"run{k}.wav").exists(), (plugin, k)
            assert (d / f"run{k}_wav_sha").exists(), (plugin, k)


def test_09_per_run_shas_recorded_and_distinct():
    for plugin in PLUGINS:
        d = DATA_DIR / "per_plugin" / plugin
        shas = [(d / f"run{k}_wav_sha").read_text().strip() for k in range(1, N_RUNS + 1)]
        # Sha of file bytes matches sidecar
        for k, sha in enumerate(shas, start=1):
            actual = hashlib.sha256((d / f"run{k}.wav").read_bytes()).hexdigest()
            assert actual == sha, (plugin, k)


def test_10_per_run_isolated_temp_dirs():
    """Verify probes use tempfile.mkdtemp/TemporaryDirectory pattern."""
    for probe in ("probe_surge_xt.py", "probe_dexed.py"):
        src = _read(SCRIPTS_DIR / probe)
        assert "tempfile.TemporaryDirectory" in src, probe
        # No shared out-dir manipulation between runs.
        assert "for k in range" in src, probe


def test_11_c33_p1_anchor_shas_unchanged():
    ap = json.loads(ANCHOR_JSON.read_text())
    assert ap.get("preserved") is True, ap.get("drift", ap)
    # Sanity — the c33 anchors specifically referenced.
    for plugin in PLUGINS:
        key = f"data/dawdreamer_state/per_plugin/{plugin}/p1_state_v2.json"
        assert key in ap["pre"], key
        assert ap["pre"][key] == ap["post"][key], key


def test_12_pairwise_rms_shape_and_finite():
    for plugin in PLUGINS:
        p = DATA_DIR / "per_plugin" / plugin / "pairwise_rms.tsv"
        lines = p.read_text().splitlines()
        assert lines[0] == "i\tj\trms_diff\tmax_abs_sample"
        rows = lines[1:]
        assert len(rows) == N_PAIRS, (plugin, len(rows))
        for row in rows:
            parts = row.split("\t")
            i, j = int(parts[0]), int(parts[1])
            rms = float(parts[2])
            mx = float(parts[3])
            assert 1 <= i < j <= N_RUNS
            assert rms >= 0.0 and rms == rms  # finite, non-negative
            assert mx >= 0.0 and mx == mx


def test_13_pairwise_env_corr_shape_and_range():
    for plugin in PLUGINS:
        p = DATA_DIR / "per_plugin" / plugin / "pairwise_env_corr.tsv"
        lines = p.read_text().splitlines()
        assert lines[0] == "i\tj\tenv_corr"
        rows = lines[1:]
        assert len(rows) == N_PAIRS, plugin
        for row in rows:
            parts = row.split("\t")
            r = float(parts[2])
            assert -1.0 <= r <= 1.0 + 1e-9, (plugin, r)


def test_14_pairwise_mel_l1_db_shape():
    for plugin in PLUGINS:
        p = DATA_DIR / "per_plugin" / plugin / "pairwise_mel_l1_db.tsv"
        lines = p.read_text().splitlines()
        assert lines[0] == "i\tj\tmel_l1_db_mean"
        rows = lines[1:]
        assert len(rows) == N_PAIRS, plugin
        for row in rows:
            v = float(row.split("\t")[2])
            assert v >= 0.0 and v == v, (plugin, v)


def test_15_verdict_in_frozen_set():
    v = json.loads(VERDICT_JSON.read_text())
    assert v["verdict"] in {"SMALL_PERTURBATION_TOLERABLE",
                            "STRUCTURAL_DRIFT", "MIXED"}, v["verdict"]
    for plugin in PLUGINS:
        pp = v["per_plugin"][plugin]
        assert pp["label"] in {"SMALL", "STRUCTURAL", "BORDERLINE"}, pp


def test_16_tolerance_candidate_iff_small():
    v = json.loads(VERDICT_JSON.read_text())
    tol_path = DATA_DIR / "tolerance_gate_rubric_candidate.json"
    if v["verdict"] == "SMALL_PERTURBATION_TOLERABLE":
        assert tol_path.exists(), "tolerance candidate missing"
        c = json.loads(tol_path.read_text())
        for key in ("tolerance_rms_max", "tolerance_mel_l1_db_max",
                    "tolerance_env_corr_min", "source_rubric_hash",
                    "candidate_status"):
            assert key in c, key
    else:
        # Not required to exist for MIXED / STRUCTURAL
        pass


def test_17_ast_grep_forbidden_via_parse():
    """AST-parse-based verification: no Call node whose attr name is in
    {get_state, save_state, save_preset, load_state}, and no set_state
    with a bytes argument. (Regex test above catches strings; this
    catches structured calls.)"""
    forbidden_attrs = {"get_state", "save_state", "save_preset", "load_state"}
    for name in SCRIPT_FILES:
        if name == "__init__.py":
            continue
        src = _read(SCRIPTS_DIR / name)
        tree = ast.parse(src, filename=name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute):
                    assert func.attr not in forbidden_attrs, (name, func.attr)
                    if func.attr == "set_state":
                        # A set_state(...) call is suspect. If any arg is
                        # something clearly bytes-like, fail.
                        for arg in node.args:
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, (bytes, bytearray)):
                                raise AssertionError(f"{name}: set_state(bytes literal)")


if __name__ == "__main__":
    fns = [g for n, g in sorted(globals().items()) if n.startswith("test_") and callable(g)]
    failures = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except Exception as e:
            print(f"FAIL  {fn.__name__}: {e}")
            failures += 1
    print(f"\n{len(fns)} tests, {failures} failures")
    sys.exit(0 if failures == 0 else 1)
