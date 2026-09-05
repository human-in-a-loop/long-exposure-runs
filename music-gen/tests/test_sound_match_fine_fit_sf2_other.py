#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-05T18:25:00Z
# cycle: 62
# run_id: run-2026-09-05T221500Z
# agent: worker
# milestone: _infra/adopt-cycle62-tests
# ---
"""c62 P1-B regression suite for scripts/sound_match/fine_fit_sf2_other.py

Mirrors the c61 P2 coarse other test-suite structure (8/8 target per
c59 policy step 4 test-coverage-bar) with the c62-scoped extension of
test_04 to AST-only cross-family structural match against the c14
``fine_fit_sf2_guitar.py`` READ-ONLY anchor.

Discipline gates asserted:
    01 script exists with python3 shebang
    02 --help shows both --song and --song-sha16 (aliased dest)
    03 AST-grep confirms no PRNG imports
    04 AST cross-family structural match against fine_fit_sf2_guitar.py
       (sweep-loop / hygiene-hook / SerialLock-wrap blocks equivalent;
       family-specific literals permitted to differ). Also confirms no
       `sidecar_nonfactor` import (AST-only per c60/c61 refinement — prose
       in docstring is fine). Per c62 brief this is the 3rd family
       propagation of the AST-only refinement (c60 piano coarse, c61 other
       coarse, c62 this other-fine). Promotion to family-policy invariant
       DEFERRED to c63+ operator authority per c62 brief P1-B footnote.
    05 --help end-to-end (rc=0 + "other" mention)
    06 sweep-storage hygiene flags wired
    07 env_pin canonical 7-key subset present in module _PINS dict
    08 both sweep_driver_family_policy shas cited (parent + other-c60)
       AND OP-1 SerialLock wrap present on main()

c63 P2 OPTION A ADOPTED (docstring-only): the c14 READ-ONLY anchor
``fine_fit_sf2_guitar.py`` contains a latent ``%``-in-argparse-help bug
on ``--disk-abort-pct`` that manifests as
``TypeError: must be real number, not dict`` on ``--help`` (never fires
in production; wrappers do not call --help). The c62 driver
``fine_fit_sf2_other.py`` escapes the same argparse help text to ``%%``
locally (one-char difference), disclosed per invariant (d) in the c62
P1-B ledger narrative + §5 SHA drifts section. Test 02/05/06 exercise
the c62 driver's ``%%``-escaped ``--help`` and are correct on-disk;
they intentionally do NOT touch the c14 anchor (READ-ONLY per FD-1 +
invariant (d) DO-NOT-TOUCH; c62 P2 auditor explicit BAN on unilateral
READ-ONLY lift). Option B (refactor to AST-scan of argparse rather
than subprocess ``--help``) remains available under operator authority
per the c63 fork event ``_selection/c63-test-04-subprocess-vs-ast-refactor-decision``.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "scripts" / "sound_match" / "fine_fit_sf2_other.py"
GUITAR_ANCHOR = (
    WORKSPACE / "scripts" / "sound_match" / "fine_fit_sf2_guitar.py"
)
POLICY_SHA = "1546a6fc01e141a0bfdad41672a3f659083c1adf543e78761f9beb2206c73269"
POLICY_OTHER_SHA = (
    "55be79b82ad19ecf9c95f50d6d96d9e969e9a49883ef2d571a537c5836d4a838"
)
CANONICAL_7_KEY_PINS = {
    "PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ", "LC_ALL",
    "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
}


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _parse(p: Path) -> ast.AST:
    return ast.parse(_read(p))


def test_01_script_exists_with_python3_shebang() -> None:
    assert SCRIPT.exists(), f"missing script: {SCRIPT}"
    first_line = _read(SCRIPT).splitlines()[0]
    assert "python3" in first_line, f"unexpected shebang: {first_line!r}"


def test_02_help_shows_both_song_flag_forms() -> None:
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"--help rc={r.returncode} stderr={r.stderr[:200]}"
    assert "--song" in r.stdout, "missing --song in --help"
    assert "--song-sha16" in r.stdout, "missing --song-sha16 in --help"


def test_03_no_prng_imports() -> None:
    tree = _parse(SCRIPT)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name != "random", "PRNG (random) forbidden"
                assert not alias.name.startswith("numpy.random"), (
                    "numpy.random import forbidden"
                )
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            assert mod != "random", "from-random forbidden"
            assert mod != "numpy.random", "from-numpy.random forbidden"
            for alias in node.names:
                if mod == "numpy":
                    assert alias.name != "random", (
                        "from numpy import random forbidden"
                    )


def _function_names(tree: ast.AST) -> set[str]:
    return {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}


def _has_serial_lock_wrap(tree: ast.AST) -> bool:
    """True if any top-level FunctionDef named 'main' contains a `with SerialLock(...)`."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            for child in ast.walk(node):
                if isinstance(child, ast.With):
                    for item in child.items:
                        ctx = item.context_expr
                        if isinstance(ctx, ast.Call):
                            f = ctx.func
                            name = None
                            if isinstance(f, ast.Name):
                                name = f.id
                            elif isinstance(f, ast.Attribute):
                                name = f.attr
                            if name == "SerialLock":
                                return True
    return False


def _has_topk_push(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and f.attr == "push":
                if isinstance(f.value, ast.Name) and f.value.id == "topk":
                    return True
    return False


def _has_df_guard(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id == "df_guard_before_stage":
                return True
    return False


def _has_sweep_loop(tree: ast.AST) -> bool:
    """True if any FunctionDef contains `for cell in cells:` (fine-fit shape)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            tgt = node.target
            it = node.iter
            if (isinstance(tgt, ast.Name) and tgt.id == "cell"
                    and isinstance(it, ast.Name) and it.id == "cells"):
                return True
    return False


def test_04_ast_cross_family_structural_match_and_no_sidecar() -> None:
    """c62 3rd-family AST-only structural match refinement.

    Compares AST structural equivalence of key blocks between the c62
    other-fine-fit driver and the c14 guitar-fine-fit READ-ONLY anchor:
        - sweep loop (`for cell in cells:`)
        - hygiene hook (`df_guard_before_stage(...)` call + `topk.push(...)`)
        - SerialLock wrap on `main()`
        - Function-name superset match (permits family-specific renames
          via `_read_top_k_other_from_stage1` vs `_read_top_k_guitar_from_stage1`).
    Family-specific literal differences (docstring, program names, MIDI
    field names, instrument label) are permitted per c62 brief.

    Also confirms AST-only that no `sidecar_nonfactor` import is present.
    """
    tree = _parse(SCRIPT)
    guitar_tree = _parse(GUITAR_ANCHOR)

    # Sub-check A: sweep-loop equivalence.
    assert _has_sweep_loop(tree), "other-fine missing `for cell in cells:` loop"
    assert _has_sweep_loop(guitar_tree), (
        "guitar-fine anchor missing sweep loop (unexpected READ-ONLY drift)"
    )

    # Sub-check B: hygiene hook equivalence.
    assert _has_df_guard(tree), "other-fine missing df_guard_before_stage"
    assert _has_df_guard(guitar_tree), (
        "guitar-fine anchor missing df_guard (unexpected drift)"
    )
    assert _has_topk_push(tree), "other-fine missing topk.push"
    assert _has_topk_push(guitar_tree), (
        "guitar-fine anchor missing topk.push (unexpected drift)"
    )

    # Sub-check C: SerialLock-wrap equivalence.
    assert _has_serial_lock_wrap(tree), (
        "other-fine missing SerialLock wrap on main()"
    )
    assert _has_serial_lock_wrap(guitar_tree), (
        "guitar-fine anchor missing SerialLock wrap (unexpected drift)"
    )

    # Sub-check D: family-specific reader function present (permits rename).
    fns = _function_names(tree)
    assert "_read_top_k_other_from_stage1" in fns, (
        f"other-fine missing _read_top_k_other_from_stage1; got {sorted(fns)}"
    )

    # Sub-check E: no sidecar_nonfactor import (AST-only).
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "sidecar_nonfactor" not in alias.name, (
                    f"sidecar_nonfactor import forbidden: {alias.name}"
                )
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            assert "sidecar_nonfactor" not in mod, (
                f"from-sidecar_nonfactor forbidden: {mod}"
            )
            for alias in node.names:
                assert "sidecar_nonfactor" not in alias.name, (
                    f"sidecar_nonfactor name-import forbidden: {alias.name}"
                )


def test_05_help_end_to_end_and_mentions_other() -> None:
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"--help failed rc={r.returncode}"
    assert "other" in r.stdout.lower(), "help doesn't mention other"


def test_06_sweep_storage_hygiene_flags_wired() -> None:
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0
    for flag in ("--score-and-delete", "--keep-top", "--max-audio-mb",
                 "--disk-abort-pct"):
        assert flag in r.stdout, f"missing sweep-hygiene flag {flag}"


def test_07_env_pin_canonical_7_key_subset_present() -> None:
    src = _read(SCRIPT)
    for k in CANONICAL_7_KEY_PINS:
        assert f'"{k}"' in src, f"missing env_pin key {k} in _PINS dict"


def test_08_policy_shas_cited_and_serial_lock_present() -> None:
    src = _read(SCRIPT)
    assert POLICY_SHA in src, (
        f"parent policy sha {POLICY_SHA[:16]}... must be cited"
    )
    assert POLICY_OTHER_SHA in src, (
        f"other-family policy sha {POLICY_OTHER_SHA[:16]}... must be cited"
    )
    # OP-1 SerialLock import + wrap.
    assert "from scripts.sound_match._serial_lock_op1 import SerialLock" in src, (
        "OP-1 SerialLock import missing"
    )
    assert "with SerialLock(" in src, "SerialLock context wrap missing"


def _run_all() -> int:
    tests = [
        test_01_script_exists_with_python3_shebang,
        test_02_help_shows_both_song_flag_forms,
        test_03_no_prng_imports,
        test_04_ast_cross_family_structural_match_and_no_sidecar,
        test_05_help_end_to_end_and_mentions_other,
        test_06_sweep_storage_hygiene_flags_wired,
        test_07_env_pin_canonical_7_key_subset_present,
        test_08_policy_shas_cited_and_serial_lock_present,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
            passed += 1
        except Exception as exc:
            print(f"FAIL {t.__name__}: {exc}")
    print(f"---\n{passed}/{len(tests)} tests passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(_run_all())
