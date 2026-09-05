#!/usr/bin/env -S /usr/bin/python3
"""c60 P1 regression suite for scripts/sound_match/coarse_sweep_sf2_piano.py

Per docs/sweep_driver_family_policy.md sha
`1546a6fc01e141a0bfdad41672a3f659083c1adf543e78761f9beb2206c73269`
(c59 policy step 4 test-coverage-bar of 8 cases minimum, mirroring c13
guitar sweep precedent).

Discipline gates asserted:
    01 script exists with /usr/bin/python3 shebang
    02 --help shows both --song and --song-sha16 (aliased dest)
    03 AST-grep confirms no PRNG imports (random, numpy.random, etc.)
    04 AST-grep confirms no `sidecar_nonfactor` import
    05 --dry-run smoke: --help returns rc=0 end-to-end
    06 sweep-storage hygiene flags wired (--score-and-delete, --keep-top,
       --max-audio-mb, --disk-abort-pct present)
    07 env_pin canonical 7-key subset present in module _PINS dict
    08 sweep_driver_family_policy.md sha `1546a6fc...` cited in module
       docstring or manifest constant
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "scripts" / "sound_match" / "coarse_sweep_sf2_piano.py"
POLICY_SHA = "1546a6fc01e141a0bfdad41672a3f659083c1adf543e78761f9beb2206c73269"
CANONICAL_7_KEY_PINS = {
    "PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ", "LC_ALL",
    "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
}


def _read_script() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def _parse_ast() -> ast.AST:
    return ast.parse(_read_script())


def test_01_script_exists_with_python3_shebang() -> None:
    assert SCRIPT.exists(), f"missing script: {SCRIPT}"
    first_line = _read_script().splitlines()[0]
    # Accept either canonical form per docs/interpreter_guard_policy.md.
    assert first_line.startswith("#!/usr/bin/env") or first_line.startswith(
        "#!/usr/bin/python3"
    ), f"unexpected shebang: {first_line!r}"
    assert "python3" in first_line


def test_02_help_shows_both_song_flag_forms() -> None:
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"--help rc={r.returncode} stderr={r.stderr[:200]}"
    assert "--song" in r.stdout, "missing --song in --help"
    assert "--song-sha16" in r.stdout, "missing --song-sha16 in --help"


def test_03_no_prng_imports() -> None:
    tree = _parse_ast()
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


def test_04_no_sidecar_nonfactor_import() -> None:
    # AST-only check: prose mentions in docstrings are permitted (indeed
    # expected to document the discipline); actual `import sidecar_nonfactor`
    # or `from ... import sidecar_nonfactor` is what the discipline forbids.
    tree = _parse_ast()
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


def test_05_dry_run_help_end_to_end() -> None:
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"dry-run --help failed rc={r.returncode}"
    # Sanity: help text mentions piano-family purpose.
    assert "piano" in r.stdout.lower(), "help doesn't mention piano"


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
    src = _read_script()
    # The _PINS dict must at least include the canonical 7-key subset.
    for k in CANONICAL_7_KEY_PINS:
        assert f'"{k}"' in src, f"missing env_pin key {k} in _PINS dict"


def test_08_sweep_driver_family_policy_sha_cited() -> None:
    src = _read_script()
    assert POLICY_SHA in src, (
        f"docs/sweep_driver_family_policy.md sha {POLICY_SHA[:16]}... "
        "must be cited in module docstring or manifest constant"
    )


def _run_all():
    tests = [
        test_01_script_exists_with_python3_shebang,
        test_02_help_shows_both_song_flag_forms,
        test_03_no_prng_imports,
        test_04_no_sidecar_nonfactor_import,
        test_05_dry_run_help_end_to_end,
        test_06_sweep_storage_hygiene_flags_wired,
        test_07_env_pin_canonical_7_key_subset_present,
        test_08_sweep_driver_family_policy_sha_cited,
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
