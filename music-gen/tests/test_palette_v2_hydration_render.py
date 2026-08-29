#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T06:30:00Z
# cycle: 35
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/palette-schema-v2-hydration-render
# ---
"""Test suite for c35 Branch A palette-v2 hydration render.

Run:
    PYTHONPATH=. /usr/bin/python3 tests/test_palette_v2_hydration_render.py

Fourteen mandatory cases per rubric §Contract:
  1. rubric doc landed BEFORE any script under scripts/palette_v2_render/
     (mtime + git-log fallback ordering).
  2. rubric_hash.txt byte-equal to sha256(docs/palette_v2_hydration_render_rubric.md).
  3. rubric_hash in verdict.json byte-equal to rubric_hash.txt.
  4. anchor_preservation snapshot equal pre/post (unchanged=True).
  5. per-stem determinism gate is reachable and honestly resolved
     (either sha_equal=True on every VST3 stem OR RENDER_FAILS with
      an honest reason under justification.per_stem_determinism_failure).
  6. combined determinism reachable + honestly resolved.
  7. panel_original_vs_v2.tsv has 8 canonical keys.
  8. panel_v1_vs_v2.tsv has 8 canonical keys.
  9. panel key finiteness on both TSVs for numeric family.
 10. no-PRNG AST scan under scripts/palette_v2_render/.
 11. c9 render_effects_layered NOT imported (grep-verified).
 12. c13 batch pipeline NOT imported (grep-verified).
 13. No M-EAR-1/* ledger events emitted in this cycle.
 14. Interpreter guard present in every script under scripts/palette_v2_render/.
 15. set_parameter loop is used for hydration; get_state/save_state/save_preset/
     set_state(bytes) do NOT appear in render_stem_v2.py (AST + string scan).
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

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

RUBRIC = REPO / "docs" / "palette_v2_hydration_render_rubric.md"
RUBRIC_HASH_FILE = REPO / "data" / "palette_v2_render" / "rubric_hash.txt"
VERDICT_JSON = REPO / "data" / "palette_v2_render" / "verdict.json"
ANCHOR_JSON = REPO / "data" / "palette_v2_render" / "anchor_preservation.json"
SCRIPTS_DIR = REPO / "scripts" / "palette_v2_render"
PANEL_ORIG_V2 = REPO / "data" / "palette_v2_render" / "panel_original_vs_v2.tsv"
PANEL_V1_V2 = REPO / "data" / "palette_v2_render" / "panel_v1_vs_v2.tsv"

FAILS = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}  {detail}")
        FAILS.append((name, detail))


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _mtime(p: Path) -> int:
    return int(p.stat().st_mtime) if p.exists() else -1


def _git_first_seen(rel_path: str) -> int:
    """Unix timestamp of the earliest git-log commit touching a path.
    Returns 0 if git-log knows nothing (unstaged file); the caller
    then falls back to mtime.
    """
    try:
        r = subprocess.run(
            ["git", "-C", str(REPO), "log", "--diff-filter=A",
             "--format=%at", "--", rel_path],
            capture_output=True, text=True, check=False, timeout=15,
        )
        s = (r.stdout or "").strip()
        if s:
            return int(s.splitlines()[-1])
    except Exception:
        pass
    return 0


def test_01_rubric_landed_before_scripts():
    """Rubric doc's mtime OR earliest-git must precede every script under
    scripts/palette_v2_render/ (except __pycache__)."""
    rubric_ts = _git_first_seen(str(RUBRIC.relative_to(REPO))) or _mtime(RUBRIC)
    check("test_01_rubric_exists", RUBRIC.exists(), f"missing {RUBRIC}")
    for p in sorted(SCRIPTS_DIR.glob("*.py")):
        if p.name == "__init__.py":
            continue
        p_ts = _git_first_seen(str(p.relative_to(REPO))) or _mtime(p)
        check(f"test_01_rubric_precedes:{p.name}",
              rubric_ts <= p_ts + 1,
              f"rubric_ts={rubric_ts}, {p.name}_ts={p_ts}")


def test_02_rubric_hash_bytes_equal_file():
    got = RUBRIC_HASH_FILE.read_text().strip()
    expected = _sha256_file(RUBRIC)
    check("test_02_rubric_hash_bytes_equal", got == expected,
          f"file has {got}, sha of rubric is {expected}")


def test_03_verdict_rubric_hash_matches():
    if not VERDICT_JSON.exists():
        check("test_03_verdict_rubric_hash_matches", False,
              f"missing {VERDICT_JSON}")
        return
    v = json.loads(VERDICT_JSON.read_text())
    got = v.get("rubric_hash")
    expected = RUBRIC_HASH_FILE.read_text().strip()
    check("test_03_verdict_rubric_hash_matches", got == expected,
          f"verdict rubric_hash={got}, rubric_hash.txt={expected}")


def test_04_anchor_preservation_unchanged():
    if not ANCHOR_JSON.exists():
        check("test_04_anchor_preservation_unchanged", False, "missing")
        return
    a = json.loads(ANCHOR_JSON.read_text())
    check("test_04_anchor_preservation_unchanged",
          a.get("unchanged") is True and len(a.get("pre", {})) >= 1,
          f"unchanged={a.get('unchanged')}, n_files={len(a.get('pre',{}))}")


def test_05_per_stem_determinism_honestly_resolved():
    if not VERDICT_JSON.exists():
        check("test_05_per_stem_determinism_honestly_resolved", False, "missing verdict")
        return
    v = json.loads(VERDICT_JSON.read_text())
    verdict = v.get("verdict")
    per_stem = v.get("per_stem", [])
    if verdict in ("V2_MOVES_PANEL", "V2_NEUTRAL"):
        # Must be all-equal on VST3 stems.
        for p in per_stem:
            if p["instrument"] in ("surge_xt", "dexed"):
                check(f"test_05_vst3_sha_equal:{p['stem']}",
                      p["run1_sha"] == p["run2_sha"],
                      f"run1={p['run1_sha']} run2={p['run2_sha']}")
    elif verdict == "RENDER_FAILS":
        j = v.get("justification", {})
        honestly = (
            "per_stem_determinism_failure" in j
            or "combined_determinism_failure" in j
            or "vst3_hydration_silent" in j
            or "per_stem_render_error" in j
            or "combined_render_error" in j
            or "anchor_preservation_drift" in j
            or "non_finite_numeric_key" in j
            or "panel_key_contract" in j
        )
        check("test_05_render_fails_has_honest_reason", honestly,
              f"justification keys: {list(j.keys())}")
    else:
        check("test_05_verdict_in_enum", False,
              f"unknown verdict: {verdict}")


def test_06_combined_determinism_honestly_resolved():
    v = json.loads(VERDICT_JSON.read_text())
    got1 = v.get("bare_combined_sha_run1")
    got2 = v.get("bare_combined_sha_run2")
    verdict = v.get("verdict")
    if verdict in ("V2_MOVES_PANEL", "V2_NEUTRAL"):
        check("test_06_combined_sha_equal", got1 == got2 and got1 is not None,
              f"run1={got1}, run2={got2}")
    else:
        # RENDER_FAILS is honest as long as SHAs are populated (may be equal or
        # unequal — the justification names the failing gate).
        check("test_06_combined_sha_present", got1 is not None and got2 is not None,
              f"run1={got1}, run2={got2}")


def test_07_panel_original_vs_v2_8_keys():
    if not PANEL_ORIG_V2.exists():
        check("test_07_panel_original_vs_v2_8_keys", False, f"missing {PANEL_ORIG_V2}")
        return
    lines = PANEL_ORIG_V2.read_text().splitlines()
    header = lines[0].split("\t")
    check("test_07_panel_original_vs_v2_8_keys", len(header) == 8,
          f"header has {len(header)} keys: {header}")


def test_08_panel_v1_vs_v2_8_keys():
    if not PANEL_V1_V2.exists():
        check("test_08_panel_v1_vs_v2_8_keys", False, f"missing {PANEL_V1_V2}")
        return
    lines = PANEL_V1_V2.read_text().splitlines()
    header = lines[0].split("\t")
    check("test_08_panel_v1_vs_v2_8_keys", len(header) == 8,
          f"header has {len(header)} keys: {header}")


def _panel_numeric_finite(tsv: Path) -> bool:
    lines = tsv.read_text().splitlines()
    if len(lines) < 2:
        return False
    header = lines[0].split("\t")
    values = lines[1].split("\t")
    d = dict(zip(header, values))
    for k in ("mel_l1_db", "spectral_centroid_rmse_hz",
              "rms_env_rmse", "lufs_m_rmse_lu"):
        v = d.get(k, "")
        if not v:
            return False
        try:
            f = float(v)
            if not (f == f) or f in (float("inf"), float("-inf")):
                return False
        except ValueError:
            return False
    return True


def test_09_panel_numeric_finiteness():
    check("test_09_panel_orig_v2_numeric_finite",
          _panel_numeric_finite(PANEL_ORIG_V2), str(PANEL_ORIG_V2))
    check("test_09_panel_v1_v2_numeric_finite",
          _panel_numeric_finite(PANEL_V1_V2), str(PANEL_V1_V2))


def test_10_no_prng_ast():
    banned = {"random", "numpy.random", "torch.random"}
    for p in sorted(SCRIPTS_DIR.glob("*.py")):
        src = p.read_text()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            check(f"test_10_ast_parses:{p.name}", False, "syntax error")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    check(f"test_10_no_prng_import:{p.name}:{n.name}",
                          n.name not in banned, f"banned import {n.name}")
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                check(f"test_10_no_prng_from:{p.name}:{mod}",
                      mod not in banned, f"banned from-import {mod}")


def test_11_no_c9_effects_import():
    for p in sorted(SCRIPTS_DIR.glob("*.py")):
        src = p.read_text()
        # Grep for the c9 module path; comments are stripped from the check
        # by requiring a whole-word `import` or `from` line context.
        for lineno, line in enumerate(src.splitlines(), 1):
            s = line.strip()
            if s.startswith("#"):
                continue
            if "render_effects_layered" in s and (
                    "import" in s or "from" in s):
                check(f"test_11_no_c9_import:{p.name}:{lineno}", False,
                      f"line {lineno}: {s[:100]}")


def test_12_no_c13_batch_import():
    """No cycle-13 batch-v2 pipeline import (scripts.gen.batch_v2 or
    scripts.rules.sampling.i4_stratified)."""
    banned_paths = ("scripts.gen.batch_v2", "scripts.rules.sampling.i4_stratified")
    for p in sorted(SCRIPTS_DIR.glob("*.py")):
        src = p.read_text()
        for lineno, line in enumerate(src.splitlines(), 1):
            s = line.strip()
            if s.startswith("#"):
                continue
            for banned in banned_paths:
                if banned in s and ("import" in s or "from" in s):
                    check(f"test_12_no_c13_import:{p.name}:{lineno}", False,
                          f"line {lineno}: {s[:100]}")


def test_13_no_m_ear_1_emission_in_scripts():
    """Best-effort AST scan: no 'M-EAR-1' string literal in scripts (would
    indicate an emitter targeting the wrong milestone)."""
    for p in sorted(SCRIPTS_DIR.glob("*.py")):
        src = p.read_text()
        for lineno, line in enumerate(src.splitlines(), 1):
            if "M-EAR-1" in line and "#" not in line.split("M-EAR-1")[0]:
                check(f"test_13_no_m_ear_1:{p.name}:{lineno}", False,
                      f"line {lineno}: {line.strip()[:120]}")


def test_14_interpreter_guard_present():
    for p in sorted(SCRIPTS_DIR.glob("*.py")):
        src = p.read_text()
        has_shebang = src.startswith("#!/usr/bin/env -S /usr/bin/python3") or \
                      src.startswith("#!/usr/bin/python3")
        has_assert = 'sys.executable == "/usr/bin/python3"' in src or \
                     "sys.executable == '/usr/bin/python3'" in src
        check(f"test_14_interpreter_guard:{p.name}",
              has_shebang or has_assert,
              "missing shebang or interpreter assert")


def test_15_set_parameter_only_no_get_state_paths():
    """render_stem_v2.py MUST use set_parameter loop; MUST NOT call
    get_state / save_state / save_preset / set_state (the c31 STILL_GAP anti-pattern
    surface). AST-level check on Attribute/Call nodes plus string sweep."""
    render_stem = SCRIPTS_DIR / "render_stem_v2.py"
    src = render_stem.read_text()
    tree = ast.parse(src)

    seen_set_parameter = False
    banned_calls = {"get_state", "save_state", "save_preset", "load_state"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "set_parameter":
                seen_set_parameter = True
            if node.func.attr in banned_calls:
                check(f"test_15_banned_call:{node.func.attr}", False,
                      f"line {node.lineno}: {ast.unparse(node)[:120]}")
            # set_state accepted with bytes is the specific c31 anti-pattern.
            if node.func.attr == "set_state":
                # any positional arg treated as bytes = banned surface
                if node.args:
                    check("test_15_banned_set_state_bytes", False,
                          f"line {node.lineno}: set_state(bytes) is c31 anti-pattern")

    check("test_15_uses_set_parameter_loop", seen_set_parameter,
          "no plugin.set_parameter(...) call found in render_stem_v2.py")

    # String sweep: no bare occurrence in-code (comments allowed).
    for lineno, line in enumerate(src.splitlines(), 1):
        s = line.strip()
        if s.startswith("#"):
            continue
        for term in ("get_state(", "save_state(", "save_preset(", "load_state("):
            if term in s:
                check(f"test_15_no_string:{term}", False,
                      f"line {lineno}: {s[:120]}")


def run_all():
    tests = [
        test_01_rubric_landed_before_scripts,
        test_02_rubric_hash_bytes_equal_file,
        test_03_verdict_rubric_hash_matches,
        test_04_anchor_preservation_unchanged,
        test_05_per_stem_determinism_honestly_resolved,
        test_06_combined_determinism_honestly_resolved,
        test_07_panel_original_vs_v2_8_keys,
        test_08_panel_v1_vs_v2_8_keys,
        test_09_panel_numeric_finiteness,
        test_10_no_prng_ast,
        test_11_no_c9_effects_import,
        test_12_no_c13_batch_import,
        test_13_no_m_ear_1_emission_in_scripts,
        test_14_interpreter_guard_present,
        test_15_set_parameter_only_no_get_state_paths,
    ]
    for t in tests:
        print(t.__name__)
        t()
    print()
    if FAILS:
        print(f"FAILED: {len(FAILS)} check(s)")
        for name, detail in FAILS:
            print(f"  - {name}: {detail}")
        return 1
    print(f"OK ({len(tests)} test-functions, all checks pass)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_all())
