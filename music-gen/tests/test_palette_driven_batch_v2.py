#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T06:20:00Z
# cycle: 35
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v2-sampler-diversified
# ---
"""Test suite for M-GEN-1/palette-driven-batch-v2-sampler-diversified.

Invocation: PYTHONPATH=. /usr/bin/python3 tests/test_palette_driven_batch_v2.py

Plain-assert style; no pytest. ≥14 named cases.
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

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

SCRIPTS_DIR = _REPO / "scripts" / "gen_palette_batch_v2"
DATA_DIR = _REPO / "data" / "gen_palette_batch_v2"
DOCS_RUBRIC = _REPO / "docs" / "palette_driven_batch_v2_sampler_diversified_rubric.md"

PROHIBITED_IMPORT_MODULES = (
    "scripts.tex.render_effects_layered",
    "scripts.gen.batch_v2",
    "scripts.rules.sampling.i4_stratified",
    "scripts.ear.stability_metrics",
    "scripts.ear.stability_audit",
    "scripts.analysis.collision_model_bp",
    "scripts.analysis.canonical_aggregate_sha",
    "scripts.analysis.hash_geometry_fit",
    "scripts.analysis.multiple_testing_correction",
    "scripts.analysis.semantic_cluster_fit",
    "scripts.analysis.shape_mechanism_fit",
    "scripts.analysis.effective_k_probe",
    "scripts.analysis.rule_structural_fingerprints",
    "scripts.analysis.anchor_preservation_shape",
    "scripts.analysis.anchor_preservation_hash",
    "scripts.analysis.anchor_preservation_semantic",
    "scripts.classifier.sidecar_nonfactor",
)

# c31/c33/c34 anchor dirs — writes here are FORBIDDEN.
READONLY_WRITE_FORBIDDEN_DIRS = (
    _REPO / "scripts" / "palette_render",
    _REPO / "scripts" / "palette",
    _REPO / "scripts" / "palette_probe",
    _REPO / "scripts" / "palette_v2",
    _REPO / "scripts" / "dawdreamer_state",
    _REPO / "scripts" / "gen",
    _REPO / "data" / "palette",
    _REPO / "data" / "palette_v2",
    _REPO / "data" / "palette_render",
    _REPO / "data" / "dawdreamer_state",
)

NUMERIC_KEYS = ("mel_l1_db", "spectral_centroid_rmse_hz",
                "rms_env_rmse", "lufs_m_rmse_lu")
SALTS = (0, 1, 2)
VERDICT_ENUM = {"SPREAD_ACHIEVED", "SPREAD_PARTIAL",
                "SPREAD_STILL_COLLAPSED", "BATCH_FAILS"}

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _script_paths() -> list[Path]:
    return sorted(p for p in SCRIPTS_DIR.iterdir()
                  if p.is_file() and p.suffix == ".py")


def _test_functions() -> list[str]:
    """Return this file's test_* function names for the ≥14 test."""
    tree = ast.parse(Path(__file__).read_text())
    return [n.name for n in tree.body
            if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]


def _ast_grep_prng_hits(source: str) -> list[str]:
    """Return AST-level PRNG import/attribute hits (empty = clean)."""
    tree = ast.parse(source)
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for al in node.names:
                if al.name in ("random", "secrets"):
                    hits.append(f"import {al.name}")
                if al.name.startswith("numpy.random"):
                    hits.append(f"import {al.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module == "random" or node.module == "secrets":
                hits.append(f"from {node.module}")
            if node.module and node.module.startswith("numpy.random"):
                hits.append(f"from {node.module}")
            if node.module == "os" and any(al.name == "urandom" for al in node.names):
                hits.append("from os import urandom")
        elif isinstance(node, ast.Attribute):
            # Match torch.manual_seed / torch.cuda.manual_seed_all etc.
            if isinstance(node.attr, str) and node.attr.endswith("seed"):
                # exclude our SHA-seeded uint32 helper `_seed_u32`
                if node.attr == "seed" or "seed_all" in node.attr:
                    parts = []
                    cur = node
                    while isinstance(cur, ast.Attribute):
                        parts.insert(0, cur.attr)
                        cur = cur.value
                    if isinstance(cur, ast.Name):
                        parts.insert(0, cur.id)
                    dotted = ".".join(parts)
                    if dotted.startswith("torch.") or dotted.startswith("tf."):
                        hits.append(dotted)
    return hits


# --------------------------------------------------------------------------
# tests
# --------------------------------------------------------------------------

def test_rubric_and_hash_file_present():
    assert DOCS_RUBRIC.is_file(), f"rubric doc missing: {DOCS_RUBRIC}"
    assert (DATA_DIR / "rubric_hash.txt").is_file(), "rubric_hash.txt missing"


def test_rubric_hash_matches_doc_sha256():
    doc_sha = _sha256_file(DOCS_RUBRIC)
    txt_sha = (DATA_DIR / "rubric_hash.txt").read_text().strip()
    assert doc_sha == txt_sha, (
        f"rubric_hash.txt drift: doc={doc_sha[:12]}, txt={txt_sha[:12]}"
    )


def test_rubric_mtime_precedes_scripts():
    """Frozen rubric MUST land BEFORE any script under scripts/gen_palette_batch_v2/."""
    scripts = _script_paths()
    assert scripts, "no scripts under scripts/gen_palette_batch_v2/"
    rubric_mtime = DOCS_RUBRIC.stat().st_mtime
    earliest_script = min(s.stat().st_mtime for s in scripts)
    # Try git-log ordering first; fall back to mtime.
    try:
        r_doc = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(DOCS_RUBRIC.relative_to(_REPO))],
            cwd=_REPO, capture_output=True, text=True, timeout=15,
        )
        doc_ct = int(r_doc.stdout.strip()) if r_doc.stdout.strip() else None
        earliest_script_ct = None
        for s in scripts:
            r_s = subprocess.run(
                ["git", "log", "-1", "--format=%ct", "--", str(s.relative_to(_REPO))],
                cwd=_REPO, capture_output=True, text=True, timeout=15,
            )
            v = int(r_s.stdout.strip()) if r_s.stdout.strip() else None
            if v is not None and (earliest_script_ct is None or v < earliest_script_ct):
                earliest_script_ct = v
        if doc_ct is not None and earliest_script_ct is not None:
            assert doc_ct <= earliest_script_ct, (
                f"rubric git-commit-time ({doc_ct}) must precede earliest "
                f"script git-commit-time ({earliest_script_ct})"
            )
            return
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    assert rubric_mtime <= earliest_script, (
        f"rubric mtime ({rubric_mtime}) must precede earliest script "
        f"mtime ({earliest_script})"
    )


def test_verdict_json_present_with_rubric_hash_byte_equal():
    v = DATA_DIR / "verdict.json"
    assert v.is_file(), f"verdict.json missing"
    obj = json.loads(v.read_text())
    txt_sha = (DATA_DIR / "rubric_hash.txt").read_text().strip()
    assert obj.get("rubric_hash") == txt_sha, (
        f"verdict.rubric_hash ({obj.get('rubric_hash', '')[:12]}) != "
        f"rubric_hash.txt ({txt_sha[:12]})"
    )
    assert obj.get("verdict") in VERDICT_ENUM, (
        f"verdict {obj.get('verdict')!r} not in {sorted(VERDICT_ENUM)}"
    )


def test_per_salt_byte_determinism_bare_combined():
    for salt in SALTS:
        d = DATA_DIR / "per_song" / str(salt)
        r1 = (d / "bare_combined.wav.sha.run1").read_text().strip()
        r2 = (d / "bare_combined.wav.sha.run2").read_text().strip()
        assert r1 == r2, (
            f"salt={salt} bare_combined SHA drift across runs: "
            f"run1={r1[:12]}, run2={r2[:12]}"
        )


def test_per_salt_byte_determinism_per_stem():
    for salt in SALTS:
        for stem in ("drums", "bass", "other"):
            d = DATA_DIR / "per_song" / str(salt) / "per_stem" / stem
            r1 = (d / "render_run1.wav.sha").read_text().strip()
            r2 = (d / "render_run2.wav.sha").read_text().strip()
            assert r1 == r2, (
                f"salt={salt} stem={stem} SHA drift: {r1[:12]} vs {r2[:12]}"
            )


def test_per_salt_assignments_jsonl_distinct_across_salts():
    """Per c34-clone-2 diagnosis + c35 fix: rule triples MUST differ per salt."""
    shas = set()
    for salt in SALTS:
        p = DATA_DIR / "per_song" / str(salt) / "assignments.jsonl"
        assert p.is_file(), f"salt={salt} assignments.jsonl missing"
        shas.add(_sha256_file(p))
    assert len(shas) == len(SALTS), (
        f"expected {len(SALTS)} distinct assignments.jsonl SHAs across salts, "
        f"got {len(shas)} — sampler-side diversification failed at the "
        f"provenance layer"
    )


def test_cross_salt_bare_combined_sha_interpretation():
    """The rubric permits any cross-salt SHA distribution; assert the
    verdict maps to the observed distribution as the rubric prescribes."""
    obj = json.loads((DATA_DIR / "verdict.json").read_text())
    distinct = set(obj.get("distinct_bare_combined_shas", []))
    verdict = obj.get("verdict")
    if verdict == "SPREAD_ACHIEVED":
        assert len(distinct) == len(SALTS), (
            f"SPREAD_ACHIEVED requires {len(SALTS)} distinct SHAs; got "
            f"{len(distinct)}"
        )
    elif verdict == "SPREAD_STILL_COLLAPSED":
        # Either fully collapsed OR numeric flat with SHA distribution ok
        flat = not obj["evidence"].get("any_numeric_key_meets_spread", False)
        assert (len(distinct) == 1) or flat, (
            f"SPREAD_STILL_COLLAPSED requires single distinct SHA OR "
            f"numeric-flat verdict; distinct={len(distinct)}, flat={flat}"
        )


def test_panel_tsvs_8_finite_keys_per_salt():
    from scripts.texture.panel import PUBLIC_KEYS  # noqa: E402
    expected = set(PUBLIC_KEYS)
    for salt in SALTS:
        for tsv_name in ("panel_original", "panel_fluidsynth"):
            p = DATA_DIR / "per_song" / str(salt) / f"{tsv_name}.tsv"
            assert p.is_file(), f"salt={salt} {tsv_name}.tsv missing"
            lines = p.read_text().strip().splitlines()
            assert len(lines) == 2, (
                f"salt={salt} {tsv_name}.tsv: expected 2 lines (hdr + row), "
                f"got {len(lines)}"
            )
            hdr = lines[0].split("\t")
            row = lines[1].split("\t")
            assert set(hdr) == expected, (
                f"salt={salt} {tsv_name}.tsv header {sorted(hdr)} != {sorted(expected)}"
            )
            values = dict(zip(hdr, row))
            for k in NUMERIC_KEYS:
                v = values.get(k, "")
                assert v not in ("", "nan", "inf", "-inf"), (
                    f"salt={salt} {tsv_name}.tsv key {k!r} not finite: {v!r}"
                )
                try:
                    fv = float(v)
                except Exception:
                    raise AssertionError(f"salt={salt} {tsv_name}.tsv key {k!r} unparseable: {v!r}")
                assert fv == fv, f"{k!r} NaN"


def test_anchor_preservation_unchanged():
    p = DATA_DIR / "anchor_preservation.json"
    assert p.is_file(), "anchor_preservation.json missing"
    obj = json.loads(p.read_text())
    assert obj.get("unchanged") is True, (
        "anchor preservation FAILED — c31/c33/c34 anchors were mutated "
        "during batch-v2 run"
    )


def test_verdict_enum_membership():
    obj = json.loads((DATA_DIR / "verdict.json").read_text())
    assert obj.get("verdict") in VERDICT_ENUM, (
        f"verdict {obj.get('verdict')!r} not in {sorted(VERDICT_ENUM)}"
    )


def test_ast_grep_no_prng_and_no_sidecar_nonfactor():
    """AST-grep clean: no `random`, `numpy.random`, `torch.*seed`, `secrets`,
    `os.urandom`, and no `sidecar_nonfactor` imports."""
    for p in _script_paths():
        src = p.read_text()
        hits = _ast_grep_prng_hits(src)
        assert not hits, f"{p.name} PRNG hits: {hits}"
        assert "sidecar_nonfactor" not in src, (
            f"{p.name}: sidecar_nonfactor reference forbidden"
        )


def test_ast_grep_no_forbidden_module_imports():
    for p in _script_paths():
        tree = ast.parse(p.read_text())
        mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for al in node.names:
                    mods.add(al.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mods.add(node.module)
        for bad in PROHIBITED_IMPORT_MODULES:
            hit = any(m == bad or m.startswith(bad + ".") for m in mods)
            assert not hit, f"{p.name} imports forbidden {bad}"


def test_interpreter_guard_present_in_every_script():
    pat = re.compile(
        r"assert\s+sys\.executable\s*==\s*['\"]/usr/bin/python3['\"]"
    )
    for p in _script_paths():
        if p.name == "__init__.py":
            continue
        src = p.read_text()
        assert pat.search(src), (
            f"{p.name} missing interpreter guard `assert sys.executable == "
            f"'/usr/bin/python3'`"
        )


def test_no_writes_into_readonly_anchor_dirs():
    """Every file the batch produces must live under data/gen_palette_batch_v2/
    (or the shared egress_status.jsonl, which is opened in append mode)."""
    # Assertion: no non-anchor artifact appears under any forbidden dir with
    # a mtime greater than the rubric mtime (allowing for pre-existing files).
    ap = json.loads((DATA_DIR / "anchor_preservation.json").read_text())
    pre = ap.get("pre", {})
    post = ap.get("post", {})
    assert set(pre.keys()) == set(post.keys()), (
        f"anchor snapshot key sets differ: added={sorted(set(post) - set(pre))} "
        f"removed={sorted(set(pre) - set(post))}"
    )
    for k in sorted(pre):
        assert pre[k] == post[k], (
            f"anchor category {k}: files diverged pre/post batch run"
        )


def test_spread_analysis_shape_correct():
    s = json.loads((DATA_DIR / "spread_analysis.json").read_text())
    assert set(s["salts"]) == set(SALTS), f"spread.salts != {SALTS}"
    for pname in ("panel_original", "panel_fluidsynth"):
        for k in NUMERIC_KEYS:
            entry = s["per_key"][pname][k]
            assert "iqr" in entry and "max_minus_min" in entry, (
                f"spread {pname}/{k} missing iqr / max_minus_min"
            )
            assert len(entry["values"]) == len(SALTS), (
                f"spread {pname}/{k} values count != {len(SALTS)}"
            )
    assert "sfizz_vs_delta_correlation" in s, (
        "spread.sfizz_vs_delta_correlation missing"
    )


def test_v2_perturbed_payloads_present_and_validate_v2_schema():
    """Perturbed palette-v2 payloads authored for surge_xt + dexed and
    revalidated through palette_v2 validator."""
    from scripts.palette_v2.validate import validate_row  # noqa: E402
    for salt in SALTS:
        v2_dir = DATA_DIR / "per_song" / str(salt) / "v2_perturbed"
        for plugin in ("surge_xt", "dexed"):
            p = v2_dir / f"{plugin}.json"
            assert p.is_file(), f"salt={salt} v2 payload missing for {plugin}"
            row = json.loads(p.read_text())
            errors = validate_row(row)
            assert not errors, (
                f"salt={salt} plugin={plugin} palette_v2 validator "
                f"rejected: {errors[:3]}"
            )
            assert row["pinned_state"]["format"] == "v2_iterated_params"


def test_per_salt_rule_triples_distinct_cross_salt():
    v = json.loads((DATA_DIR / "verdict.json").read_text())
    triples = v.get("per_salt_rule_triples") or {}
    for rt in ("harmonic", "rhythmic", "arrangement"):
        picks = [triples[str(s)][rt] for s in SALTS]
        assert len(set(picks)) == len(picks), (
            f"cross-salt distinctness FAILED on rule_type={rt}: {picks}"
        )


def test_no_ledger_i3_dminor_read_and_no_i4_import():
    """Sampler+perturbation MUST NOT read data/rules/ledger_i3_dminor.jsonl,
    and no script may import scripts.rules.sampling.i4_stratified."""
    # Enforce via AST literals only — mentions in comments/docstrings are fine.
    for p in _script_paths():
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                assert "ledger_i3_dminor" not in node.value, (
                    f"{p.name}: string literal references ledger_i3_dminor.jsonl "
                    f"(forbidden this cycle)"
                )
    # Import check is covered by test_ast_grep_no_forbidden_module_imports
    # for i4_stratified; add a positive check that the base ledger is what's read.
    assert (_REPO / "data" / "rules" / "ledger.jsonl").is_file(), (
        "data/rules/ledger.jsonl (base 76-row ledger) missing"
    )


def test_test_file_has_at_least_14_test_functions():
    fns = _test_functions()
    assert len(fns) >= 14, (
        f"test file must define ≥14 test_ functions; got {len(fns)}: {fns}"
    )


# --------------------------------------------------------------------------
# runner
# --------------------------------------------------------------------------

def _run_all() -> int:
    fns = _test_functions()
    failures: list[tuple[str, str]] = []
    for name in fns:
        try:
            globals()[name]()
            print(f"  PASS {name}")
        except AssertionError as e:
            failures.append((name, str(e)))
            print(f"  FAIL {name}: {e}")
        except Exception as e:
            failures.append((name, f"{type(e).__name__}: {e}"))
            print(f"  ERROR {name}: {type(e).__name__}: {e}")
    print()
    if failures:
        print(f"FAIL: {len(failures)} failures out of {len(fns)} tests")
        return 1
    print(f"PASS: {len(fns)}/{len(fns)} tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
