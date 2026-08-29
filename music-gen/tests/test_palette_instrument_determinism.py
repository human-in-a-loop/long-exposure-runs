#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T02:55:00Z
# cycle: 31
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/palette-instrument-determinism
# ---
"""Tests enforcing the cycle-31 palette-instrument-determinism rubric.

Runs under `/usr/bin/python3` via plain-assert style (no pytest hard
dependency, matches project convention seen in tests/test_rules_schema.py).

Invocation:
    PYTHONPATH=. /usr/bin/python3 tests/test_palette_instrument_determinism.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "scripts" / "palette_probe"
DATA_DIR = ROOT / "data" / "palette_probe"
RUBRIC = ROOT / "docs" / "palette_instrument_determinism_rubric.md"
INSTRUMENTS = ["surge_xt", "dexed", "sfizz"]
VERDICTS = {"GREEN", "REDEFINED_GAP", "STILL_GAP"}


def probe_scripts() -> list[Path]:
    """All executable probe/driver .py files (excludes __init__.py)."""
    return sorted(p for p in PROBE_DIR.glob("*.py") if p.name != "__init__.py")


def test_interpreter_guard_present_in_all_probe_scripts():
    for p in probe_scripts():
        txt = p.read_text()
        assert "sys.executable" in txt and "/usr/bin/python3" in txt, (
            f"missing interpreter guard in {p}"
        )


def test_no_prng_in_probe_code():
    """AST-grep for PRNG entrypoints under scripts/palette_probe/."""
    banned = {
        ("random",),                    # `import random` or `random.*`
        ("secrets",),
        ("numpy", "random"),            # `np.random.*`
        ("numpy.random",),
        ("torch", "randn"),
        ("torch", "rand"),
    }
    for p in probe_scripts():
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError as exc:
            raise AssertionError(f"cannot parse {p}: {exc}")
        for node in ast.walk(tree):
            # import random / import secrets / import numpy.random
            if isinstance(node, ast.Import):
                for a in node.names:
                    n = a.name
                    if n in ("random", "secrets", "numpy.random"):
                        raise AssertionError(
                            f"forbidden PRNG import '{n}' in {p}"
                        )
            if isinstance(node, ast.ImportFrom):
                if node.module in ("random", "secrets", "numpy.random"):
                    raise AssertionError(
                        f"forbidden PRNG from-import '{node.module}' in {p}"
                    )
            # np.random.<x>, torch.randn(...), etc.
            if isinstance(node, ast.Attribute):
                # walk chain of attributes
                parts = []
                cur = node
                while isinstance(cur, ast.Attribute):
                    parts.insert(0, cur.attr)
                    cur = cur.value
                if isinstance(cur, ast.Name):
                    parts.insert(0, cur.id)
                    if parts[0] == "np" and len(parts) > 1 and parts[1] == "random":
                        raise AssertionError(f"forbidden np.random.* in {p}")
                    if parts[0] == "numpy" and len(parts) > 1 and parts[1] == "random":
                        raise AssertionError(f"forbidden numpy.random.* in {p}")
                    if parts[0] == "torch" and len(parts) > 1 and parts[1] in ("randn", "rand", "randint"):
                        raise AssertionError(f"forbidden torch.{parts[1]} in {p}")


def test_pinned_state_json_schema_conformance():
    sys.path.insert(0, str(ROOT))
    from scripts.palette_probe import _shared as sh  # noqa: E402
    for inst in INSTRUMENTS:
        p = DATA_DIR / "per_instrument" / inst / "pinned_state.json"
        assert p.exists(), f"missing {p}"
        obj = json.loads(p.read_text())
        sh.validate_pinned_state(obj)


def test_run1_run2_sha_equal_per_instrument():
    """Per-instrument: verdict GREEN or REDEFINED_GAP must have
    matching final WAV SHAs; STILL_GAP is permitted to differ."""
    rows = list(_read_tsv())
    for row in rows:
        v = row["verdict"]
        assert v in VERDICTS, f"verdict {v!r} not in {VERDICTS}"
        if v == "GREEN":
            assert row["run1_wav_sha"] == row["run2_wav_sha"], row
            assert row["run1_state_sha"] == row["run2_state_sha"], row
        elif v == "REDEFINED_GAP":
            assert row["run1_wav_sha_refined"] == row["run2_wav_sha_refined"], row


def test_verdict_frozen_label():
    rows = list(_read_tsv())
    assert len(rows) == 3, f"expected 3 rows in TSV; got {len(rows)}"
    seen_instruments = {r["instrument"] for r in rows}
    assert seen_instruments == set(INSTRUMENTS), seen_instruments
    for row in rows:
        assert row["verdict"] in VERDICTS, row


def test_cycle9_chain_not_imported():
    """Grep for any reference to the cycle-9 effects chain module under
    scripts/palette_probe/. Must be zero matches."""
    pat = re.compile(r"(from|import)\s+scripts\.tex|render_effects_layered")
    for p in probe_scripts():
        text = p.read_text()
        for line in text.splitlines():
            assert not pat.search(line), (
                f"cycle-9 chain reference found in {p}: {line.strip()!r}"
            )


def test_pinned_state_roundtrip():
    """Load pinned_state.json, re-serialize canonically, byte-identical."""
    sys.path.insert(0, str(ROOT))
    from scripts.palette_probe import _shared as sh  # noqa: E402
    for inst in INSTRUMENTS:
        p = DATA_DIR / "per_instrument" / inst / "pinned_state.json"
        raw = p.read_text()
        obj = json.loads(raw)
        canon = sh.canonical_json(obj) + "\n"
        assert canon == raw, (
            f"canonical re-serialization drift on {inst}: "
            f"lens {len(canon)} vs {len(raw)}"
        )


def test_rubric_hash_matches_committed_doc():
    stored = (DATA_DIR / "rubric_hash.txt").read_text().strip()
    computed = hashlib.sha256(RUBRIC.read_bytes()).hexdigest()
    assert stored == computed, (stored, computed)


def test_rubric_committed_before_probe_scripts():
    """Pre-registration integrity: the rubric file must exist before any
    probe script. Enforced via git log ordering when git commits exist for
    both, otherwise via file-mtime ordering."""
    # Prefer git log ordering when available.
    try:
        git_ok = _git_ordering_ok()
    except Exception:
        git_ok = None
    if git_ok is True:
        return
    # File-mtime fallback (in-workspace ordering the harness enforces).
    r_mtime = RUBRIC.stat().st_mtime
    for p in probe_scripts():
        assert r_mtime <= p.stat().st_mtime + 1e-3, (
            f"rubric mtime {r_mtime} > probe script mtime "
            f"{p.stat().st_mtime} for {p}"
        )


def _git_ordering_ok() -> bool | None:
    """Return True/False if git log carries both; None if either untracked."""
    def _first_commit_ts(rel: str) -> str | None:
        r = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%ct", "--", rel],
            capture_output=True, text=True, cwd=str(ROOT), timeout=15,
        )
        lines = [ln for ln in r.stdout.strip().splitlines() if ln]
        return lines[-1] if lines else None  # oldest add commit

    r_ts = _first_commit_ts("docs/palette_instrument_determinism_rubric.md")
    if r_ts is None:
        return None
    for p in probe_scripts():
        rel = str(p.relative_to(ROOT))
        p_ts = _first_commit_ts(rel)
        if p_ts is None:
            return None
        if int(r_ts) > int(p_ts):
            return False
    return True


def _read_tsv() -> list[dict[str, str]]:
    p = DATA_DIR / "instrument_determinism.tsv"
    lines = p.read_text().strip().splitlines()
    header = lines[0].split("\t")
    out = []
    for ln in lines[1:]:
        parts = ln.split("\t")
        # Handle trailing empty fields
        while len(parts) < len(header):
            parts.append("")
        out.append(dict(zip(header, parts)))
    return out


TESTS = [
    test_interpreter_guard_present_in_all_probe_scripts,
    test_no_prng_in_probe_code,
    test_pinned_state_json_schema_conformance,
    test_run1_run2_sha_equal_per_instrument,
    test_verdict_frozen_label,
    test_cycle9_chain_not_imported,
    test_pinned_state_roundtrip,
    test_rubric_hash_matches_committed_doc,
    test_rubric_committed_before_probe_scripts,
]


def main() -> int:
    passed = failed = 0
    for t in TESTS:
        try:
            t()
            print(f"PASS {t.__name__}")
            passed += 1
        except AssertionError as exc:
            print(f"FAIL {t.__name__}: {exc}")
            failed += 1
        except Exception as exc:
            print(f"ERROR {t.__name__}: {type(exc).__name__}: {exc}")
            failed += 1
    print(f"--- {passed}/{passed+failed} passed ---")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
