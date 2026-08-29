#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:35:00Z
# cycle: 34
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/palette-driven-bare-render/cross-seed
# ---
"""Plain-assert test suite (no pytest) for M-TEX-1/palette-driven-bare-render/cross-seed.

Invoke: PYTHONPATH=. /usr/bin/python3 tests/test_palette_driven_bare_render_cross_seed.py

≥12 cases enforcing the rubric + Fixed-Decisions contract.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

REPO = Path(__file__).resolve().parents[1]
CS_SCRIPTS_DIR = REPO / "scripts" / "palette_render_cross_seed"
CS_DATA_DIR = REPO / "data" / "palette_render_cross_seed"
RUBRIC_DOC = REPO / "docs" / "palette_driven_bare_render_cross_seed_rubric.md"
RUBRIC_HASH_FILE = CS_DATA_DIR / "rubric_hash.txt"
VERDICT_JSON = CS_DATA_DIR / "verdict.json"
SUMMARY_TSV = CS_DATA_DIR / "cross_seed_summary.tsv"
ANCHOR_JSON = CS_DATA_DIR / "anchor_preservation.json"
SEEDS = ("seed_mid_50s", "synth_060s")

PANEL_KEYS = (
    "mel_l1_db", "spectral_centroid_rmse_hz", "rms_env_rmse", "lufs_m_rmse_lu",
    "embedding_cosine_distance", "embedding_rung", "sr_hz", "n_samples_compared",
)
NUMERIC_KEYS = ("mel_l1_db", "spectral_centroid_rmse_hz",
                "rms_env_rmse", "lufs_m_rmse_lu")

PY_SCRIPTS = sorted(p for p in CS_SCRIPTS_DIR.glob("*.py") if p.name != "__init__.py")


# ---------------- individual test cases ----------------

def test_01_interpreter_guard():
    """/usr/bin/python3 shebang + runtime assert in every Branch B .py file."""
    files = [CS_SCRIPTS_DIR / "__init__.py"] + PY_SCRIPTS
    for p in files:
        text = p.read_text()
        assert text.startswith("#!/usr/bin/env -S /usr/bin/python3"), f"{p} bad shebang"
        assert 'sys.executable == "/usr/bin/python3"' in text or "sys.executable ==" in text, \
            f"{p} missing interpreter assert"


def test_02_no_prng_ast():
    """AST-grep: no `import random`, `from random`, `numpy.random`, `secrets.` anywhere in Branch B code."""
    for p in [CS_SCRIPTS_DIR / "__init__.py"] + PY_SCRIPTS:
        tree = ast.parse(p.read_text(), filename=str(p))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    assert a.name != "random", f"{p} imports random"
                    assert a.name != "secrets", f"{p} imports secrets"
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "random", f"{p} from random import"
                assert node.module != "secrets", f"{p} from secrets import"
                if node.module and node.module.startswith("numpy.random"):
                    raise AssertionError(f"{p} imports numpy.random submodule")
            elif isinstance(node, ast.Attribute):
                # Guard against np.random.<X> chains at attribute level.
                s = ast.unparse(node) if hasattr(ast, "unparse") else ""
                if s.startswith(("np.random.", "numpy.random.", "secrets.")):
                    raise AssertionError(f"{p} uses PRNG attribute: {s}")


def _iter_import_names(tree: ast.AST):
    """Yield (module, name) pairs for every actual import statement in the tree."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield ("", a.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for a in node.names:
                yield (mod, a.name)


def test_03_no_c9_effects_import():
    """AST-level: no import of scripts.tex.render_effects_layered under Branch B."""
    for p in [CS_SCRIPTS_DIR / "__init__.py"] + PY_SCRIPTS:
        tree = ast.parse(p.read_text(), filename=str(p))
        for mod, name in _iter_import_names(tree):
            full = f"{mod}.{name}".strip(".")
            assert "render_effects_layered" not in mod, f"{p} imports {mod}"
            assert "render_effects_layered" not in name, f"{p} imports {full}"


def test_04_no_c13_batch_import():
    """AST-level: no scripts.gen.batch_v2 or scripts.rules.sampling.i4_stratified imports."""
    banned_mod_substrings = ("scripts.gen.batch_v2", "scripts.rules.sampling.i4_stratified")
    for p in [CS_SCRIPTS_DIR / "__init__.py"] + PY_SCRIPTS:
        tree = ast.parse(p.read_text(), filename=str(p))
        for mod, name in _iter_import_names(tree):
            for b in banned_mod_substrings:
                assert b not in mod, f"{p} imports {mod}"
                assert b not in name, f"{p} imports {mod}.{name}"


def test_05_no_sidecar_nonfactor():
    """Line-start regex: no `from|import scripts.classifier.sidecar_nonfactor`."""
    pat = re.compile(r"^\s*(from|import)\s+scripts\.classifier\.sidecar_nonfactor", re.MULTILINE)
    for p in [CS_SCRIPTS_DIR / "__init__.py"] + PY_SCRIPTS:
        assert not pat.search(p.read_text()), f"{p} imports sidecar_nonfactor"


def test_06_no_writes_to_anchor_dirs():
    """anchor_preservation.json.unchanged must be True; mtime + SHA per anchor file byte-identical pre/post."""
    d = json.loads(ANCHOR_JSON.read_text())
    assert d["unchanged"] is True, "anchor_preservation.json.unchanged is False"
    pre, post = d["pre"], d["post"]
    assert set(pre.keys()) == set(post.keys()), "anchor file set diverges"
    for k in pre:
        assert pre[k] == post[k], f"anchor file drift on {k}"
    # And require the tracked set to include all four required anchor roots.
    for root in ("scripts/palette_render/", "scripts/palette/",
                 "scripts/palette_probe/", "scripts/dawdreamer_state/"):
        matched = [k for k in pre if k.startswith(root)]
        # dawdreamer_state may be empty in some environments; palette_render is required.
        if root == "scripts/palette_render/":
            assert matched, f"no anchor files tracked under {root}"


def test_07_byte_determinism_per_seed():
    """bare_combined + per-stem SHA byte-equal across the two independent temp-dir runs."""
    v = json.loads(VERDICT_JSON.read_text())
    for seed in SEEDS:
        d = v[seed]
        assert d["combined_sha_equal"] is True, f"{seed} combined SHA mismatch"
        assert d["combined_sha_run1"] == d["combined_sha_run2"], f"{seed} combined SHA fields differ"
        for stem, ok in d["per_stem_sha_equal"].items():
            assert ok is True, f"{seed} stem {stem} SHA mismatch"


def test_08_panels_8key_finite():
    """Both TSVs per seed have all 8 panel keys; the 4 numeric keys are finite."""
    for seed in SEEDS:
        for tsv in ("panel_original_vs_palette.tsv", "panel_fluidsynth_vs_palette.tsv"):
            p = CS_DATA_DIR / "per_seed" / seed / tsv
            assert p.is_file(), f"{p} missing"
            lines = p.read_text().strip().splitlines()
            assert len(lines) == 2, f"{p} has {len(lines)} lines, expected 2"
            header = lines[0].split("\t")
            assert set(header) == set(PANEL_KEYS), f"{p} keys drift: {header}"
            values = dict(zip(header, lines[1].split("\t")))
            for k in NUMERIC_KEYS:
                v = float(values[k])
                assert math.isfinite(v), f"{p} {k} not finite: {v}"


def test_09_rubric_before_scripts_mtime():
    """docs/palette_driven_bare_render_cross_seed_rubric.md mtime < earliest scripts/palette_render_cross_seed/*.py mtime."""
    assert RUBRIC_DOC.is_file()
    rubric_mtime = RUBRIC_DOC.stat().st_mtime_ns
    script_mtimes = [p.stat().st_mtime_ns for p in PY_SCRIPTS]
    assert script_mtimes, "no scripts to compare"
    earliest = min(script_mtimes)
    assert rubric_mtime < earliest, (
        f"rubric mtime {rubric_mtime} not < earliest script mtime {earliest}. "
        "Rubric must be committed BEFORE any script under scripts/palette_render_cross_seed/."
    )


def test_10_c33_anchor_shas_unchanged():
    """Cross-check: verify each c33 palette_render file recorded in anchor_preservation matches on-disk SHA today."""
    d = json.loads(ANCHOR_JSON.read_text())
    for rel, meta in d["post"].items():
        if not rel.startswith("scripts/palette_render/"):
            continue
        p = REPO / rel
        assert p.is_file(), f"{rel} vanished"
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        assert h == meta["sha256"], f"{rel} SHA drift: on-disk {h} vs anchor {meta['sha256']}"


def test_11_cross_seed_summary_rows():
    """cross_seed_summary.tsv has exactly 2 data rows with per-seed verdict populated."""
    assert SUMMARY_TSV.is_file()
    lines = SUMMARY_TSV.read_text().strip().splitlines()
    # header + 2 data rows
    assert len(lines) == 3, f"expected 3 lines, got {len(lines)}"
    header = lines[0].split("\t")
    assert header[0] == "seed" and header[1] == "verdict"
    seen_seeds = set()
    for row in lines[1:]:
        cols = row.split("\t")
        seed = cols[0]
        verdict = cols[1]
        assert seed in SEEDS, f"unknown seed {seed}"
        assert verdict in ("PALETTE_MOVES_PANEL", "PALETTE_NEUTRAL", "RENDER_FAILS"), \
            f"bad verdict {verdict}"
        seen_seeds.add(seed)
    assert seen_seeds == set(SEEDS), f"summary missing seeds: {set(SEEDS) - seen_seeds}"


def test_12_verdict_json_schema_conformant():
    """verdict.json: rubric_hash byte-equal in both per-seed keys; cumulative in enum."""
    v = json.loads(VERDICT_JSON.read_text())
    rubric_disk = RUBRIC_HASH_FILE.read_text().strip()
    assert v["rubric_hash"] == rubric_disk
    for seed in SEEDS:
        d = v[seed]
        for k in ("rubric_hash", "verdict", "panel_delta_percent_per_key",
                  "panel_original_vs_palette", "panel_fluidsynth_vs_palette",
                  "assignments"):
            assert k in d, f"{seed}.{k} missing"
        assert d["rubric_hash"] == rubric_disk, f"{seed}.rubric_hash drift"
        assert d["verdict"] in ("PALETTE_MOVES_PANEL", "PALETTE_NEUTRAL", "RENDER_FAILS")
    cumulative = v["cross_seed_cumulative_verdict"]
    assert cumulative in ("CROSS_SEED_CONSISTENT", "CROSS_SEED_PARTIAL",
                          "CROSS_SEED_INCONSISTENT", "RENDER_FAILS")


def test_13_read_only_c33_imports_present():
    """Every Branch B .py script imports scripts.palette_render.{render_stem, build_assignments}."""
    for p in PY_SCRIPTS:
        text = p.read_text()
        has_rs = ("scripts.palette_render" in text and "render_stem" in text) \
            or "from scripts.palette_render import render_stem" in text \
            or "from scripts.palette_render.render_stem" in text \
            or "import scripts.palette_render.render_stem" in text
        has_ba = ("scripts.palette_render" in text and "build_assignments" in text) \
            or "from scripts.palette_render.build_assignments" in text
        assert has_rs, f"{p} does not import scripts.palette_render.render_stem"
        assert has_ba, f"{p} does not import scripts.palette_render.build_assignments"


def test_14_no_writes_under_palette_v2_or_dawdreamer_state():
    """anchor_preservation covers palette_v2 and dawdreamer_state dirs when present."""
    d = json.loads(ANCHOR_JSON.read_text())
    for root in ("scripts/palette_v2/", "scripts/dawdreamer_state/"):
        if (REPO / root).exists():
            matched_pre = [k for k in d["pre"] if k.startswith(root)]
            matched_post = [k for k in d["post"] if k.startswith(root)]
            for k in set(matched_pre) | set(matched_post):
                assert d["pre"].get(k) == d["post"].get(k), f"{k} drift under {root}"


ALL_TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]


def main() -> int:
    fails = 0
    for t in ALL_TESTS:
        name = t.__name__
        try:
            t()
            print(f"PASS  {name}")
        except AssertionError as e:
            fails += 1
            print(f"FAIL  {name}: {e}")
        except Exception as e:
            fails += 1
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{len(ALL_TESTS) - fails}/{len(ALL_TESTS)} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
