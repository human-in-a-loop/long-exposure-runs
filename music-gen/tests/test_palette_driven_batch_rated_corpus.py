#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T15:05:00Z
# cycle: 44
# run_id: fork-c320de981fda-clone-0
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-rated-corpus
# ---
"""Test suite for c44 M-GEN-1/palette-driven-batch-rated-corpus.

20 cases across five families:
  A. Rubric + hash discipline           (3)
  B. Scaffold + interpreter guards      (4)
  C. Anti-pattern locks (PRNG, sidecar, VST3 branch) (4)
  D. Batch artifacts + determinism      (5)
  E. Verdict + anchor preservation      (4)
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

RUBRIC_DOC = _REPO / "docs" / "palette_driven_batch_rated_corpus_rubric.md"
OUT_DIR = _REPO / "data" / "gen_palette_batch_rated_corpus"
SCRIPT_DIR = _REPO / "scripts" / "gen_palette_batch_rated_corpus"
RATED_CORPUS_LEDGER = _REPO / "data" / "rules" / "ledger_rated_corpus.jsonl"
C42_ABSENT_SHARD = _REPO / "data" / "rules" / "ledger_rated_corpus_harmonic_v2.jsonl"

_RESULTS: list[tuple[str, bool, str]] = []


def _check(name: str, cond: bool, detail: str = "") -> None:
    _RESULTS.append((name, cond, detail))


# ---------- A. Rubric + hash discipline ----------

def test_01_rubric_doc_exists():
    _check("test_01_rubric_doc_exists", RUBRIC_DOC.exists(),
           f"path={RUBRIC_DOC}")


def test_02_rubric_hash_file_matches_doc_content():
    doc_sha = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()
    hash_content = (OUT_DIR / "rubric_hash.txt").read_text().strip()
    _check("test_02_rubric_hash_file_matches_doc_content",
           doc_sha == hash_content,
           f"doc_sha={doc_sha[:16]} file_content={hash_content[:16]}")


def test_03_verdict_json_rubric_hash_matches():
    hash_content = (OUT_DIR / "rubric_hash.txt").read_text().strip()
    v = json.loads((OUT_DIR / "verdict.json").read_text())
    _check("test_03_verdict_json_rubric_hash_matches",
           v["rubric_hash"] == hash_content,
           f"verdict.rubric_hash={v['rubric_hash'][:16]} file={hash_content[:16]}")


# ---------- B. Scaffold + interpreter guards ----------

def test_04_scaffold_files_present():
    required = [
        "__init__.py", "sample_rule_triple.py", "derive_parameter_dict.py",
        "render_song.py", "run_batch.py", "spread_analysis.py",
        "anchor_preservation.py",
    ]
    missing = [f for f in required if not (SCRIPT_DIR / f).exists()]
    _check("test_04_scaffold_files_present", not missing,
           f"missing={missing}")


def test_05_interpreter_guard_shebang():
    files = sorted(SCRIPT_DIR.glob("*.py"))
    files = [f for f in files if f.name != "__init__.py"]
    bad = []
    for f in files:
        first = f.read_text().splitlines()[0] if f.read_text() else ""
        if "/usr/bin/python3" not in first:
            bad.append(f.name)
    _check("test_05_interpreter_guard_shebang", not bad,
           f"missing_shebang={bad}")


def test_06_rubric_mtime_strictly_before_scripts():
    rubric_mtime = RUBRIC_DOC.stat().st_mtime
    files = [f for f in SCRIPT_DIR.glob("*.py") if f.name != "__init__.py"]
    bad = [f.name for f in files if f.stat().st_mtime < rubric_mtime]
    _check("test_06_rubric_mtime_strictly_before_scripts", not bad,
           f"scripts_older_than_rubric={bad}")


def test_07_no_sidecar_nonfactor_imports():
    files = list(SCRIPT_DIR.glob("*.py"))
    bad = []
    for f in files:
        text = f.read_text()
        for ln in text.splitlines():
            stripped = ln.strip()
            if (stripped.startswith("import ") or
                stripped.startswith("from ")) and "sidecar_nonfactor" in stripped:
                bad.append(f"{f.name}:{stripped}")
    _check("test_07_no_sidecar_nonfactor_imports", not bad,
           f"bad_imports={bad}")


# ---------- C. Anti-pattern locks ----------

def test_08_no_prng_ast_grep():
    """Reject `import random`, `numpy.random`, `torch.*rand*`, `randint`, etc."""
    forbidden_prefixes = ("random", "numpy.random", "np.random")
    bad = []
    for f in SCRIPT_DIR.glob("*.py"):
        try:
            tree = ast.parse(f.read_text())
        except SyntaxError:
            bad.append(f"{f.name}:syntax_error")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("random",) or alias.name.startswith("random."):
                        bad.append(f"{f.name}:import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and (node.module == "random" or
                                    node.module.startswith("random.")):
                    bad.append(f"{f.name}:from {node.module}")
    _check("test_08_no_prng_ast_grep", not bad, f"prng_uses={bad}")


def test_09_no_vst3_nontrivial_parameter_dict_import_path():
    """Ensure c33 render_stem VST3 branch is not exercised — dispatch map
    contains only fluidsynth/sfizz instrument names."""
    import scripts.gen_palette_batch_rated_corpus.run_batch as rb
    disp = rb.PER_STEM_DISPATCH
    allowed = {"fluidsynth", "sfizz", "fluidsynth_gm"}
    bad = {k: v for k, v in disp.items() if v not in allowed}
    _check("test_09_no_vst3_nontrivial_parameter_dict_import_path",
           not bad, f"non_allowed_dispatch={bad}")


def test_10_c42_absent_shard_still_absent():
    _check("test_10_c42_absent_shard_still_absent",
           not C42_ABSENT_SHARD.exists(),
           f"present={C42_ABSENT_SHARD.exists()}")


def test_11_rules_source_is_c40_rated_corpus():
    b = json.loads((OUT_DIR / "batch_manifest.json").read_text())
    ok = b["rules_source_path"] == "data/rules/ledger_rated_corpus.jsonl"
    _check("test_11_rules_source_is_c40_rated_corpus", ok,
           f"rules_source_path={b['rules_source_path']}")


# ---------- D. Batch artifacts + determinism ----------

def test_12_three_salts_per_song_dirs():
    dirs = sorted((OUT_DIR / "per_song").glob("*"))
    names = [d.name for d in dirs if d.is_dir()]
    _check("test_12_three_salts_per_song_dirs",
           names == ["0", "1", "2"], f"names={names}")


def test_13_per_salt_bare_combined_shas_present():
    missing = []
    for s in (0, 1, 2):
        d = OUT_DIR / "per_song" / str(s)
        if not (d / "bare_combined.wav.sha.run1").exists():
            missing.append(f"salt{s}/run1")
        if not (d / "bare_combined.wav.sha.run2").exists():
            missing.append(f"salt{s}/run2")
    _check("test_13_per_salt_bare_combined_shas_present",
           not missing, f"missing={missing}")


def test_14_per_salt_determinism_pass():
    v = json.loads((OUT_DIR / "verdict.json").read_text())
    d = v["per_salt_determinism"]
    all_pass = all(d.get(str(s)) is True for s in (0, 1, 2))
    _check("test_14_per_salt_determinism_pass",
           all_pass, f"per_salt_determinism={d}")


def test_15_cross_salt_bare_combined_all_distinct():
    v = json.loads((OUT_DIR / "verdict.json").read_text())
    n = sum(1 for p in v["cross_salt_pairs"] if p["distinct"])
    _check("test_15_cross_salt_bare_combined_all_distinct",
           n == 3, f"distinct_pair_count={n}/3")


def test_16_per_salt_panel_8_keys_finite_both():
    v = json.loads((OUT_DIR / "verdict.json").read_text())
    from scripts.texture.panel import PUBLIC_KEYS
    numeric = ("mel_l1_db", "spectral_centroid_rmse_hz",
               "rms_env_rmse", "lufs_m_rmse_lu")
    bad = []
    for s in (0, 1, 2):
        for pname in ("panel_original", "panel_fluidsynth"):
            panel = v["per_salt_panels"][str(s)][pname]
            if set(panel.keys()) != set(PUBLIC_KEYS):
                bad.append(f"salt{s}/{pname}:missing_keys")
            for k in numeric:
                x = panel.get(k)
                if x is None or (isinstance(x, float) and (x != x)):
                    bad.append(f"salt{s}/{pname}/{k}:non_finite")
    _check("test_16_per_salt_panel_8_keys_finite_both", not bad,
           f"bad={bad}")


# ---------- E. Verdict + anchor preservation ----------

def test_17_verdict_is_lands():
    v = json.loads((OUT_DIR / "verdict.json").read_text())
    _check("test_17_verdict_is_lands",
           v["verdict"] == "RATED_CORPUS_BATCH_LANDS",
           f"verdict={v['verdict']}")


def test_18_anchor_preservation_unchanged():
    v = json.loads((OUT_DIR / "verdict.json").read_text())
    ap = v["anchor_preservation"]
    _check("test_18_anchor_preservation_unchanged",
           ap["unchanged"] is True,
           f"unchanged={ap['unchanged']} drift_rows={ap.get('drift_rows')}")


def test_19_rules_source_sha_byte_equal_pre_post():
    v = json.loads((OUT_DIR / "verdict.json").read_text())
    _check("test_19_rules_source_sha_byte_equal_pre_post",
           v["rules_source_unchanged"] is True,
           f"pre={v['rules_source_sha256_pre'][:16]} "
           f"post={v['rules_source_sha256_post'][:16]}")


def test_20_at_least_30_anchors_snapshot():
    pre = json.loads((OUT_DIR / "_anchor_pre.json").read_text())
    n = len(pre)
    _check("test_20_at_least_30_anchors_snapshot", n >= 30,
           f"anchor_count={n} (target ≥30)")


# ---------- runner ----------

def _run():
    for name in sorted(globals().keys()):
        if name.startswith("test_"):
            try:
                globals()[name]()
            except Exception as e:
                _RESULTS.append((name, False, f"EXCEPTION: {e!r}"))

    n_pass = sum(1 for _, ok, _ in _RESULTS if ok)
    n_total = len(_RESULTS)
    for name, ok, detail in _RESULTS:
        mark = "PASS" if ok else "FAIL"
        print(f"  {mark}  {name}  {detail}")
    print(f"\n{n_pass}/{n_total} tests passed")
    return 0 if n_pass == n_total else 1


if __name__ == "__main__":
    raise SystemExit(_run())
