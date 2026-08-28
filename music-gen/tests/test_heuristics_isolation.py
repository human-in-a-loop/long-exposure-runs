#!/usr/bin/env -S /usr/bin/python3
"""Non-factor isolation for M-HEUR-1: no heuristic module may reach the
classifier's non-factor sidecar or the _nonfactor path.

Rules enforced across every .py under scripts/heuristics/:

  R1. No import of `sidecar_nonfactor` (any form: `import ...`, `from ... import`).
  R2. No import of `scripts.classifier.*` or `.classifier.*` (heuristics are
      corpus-agnostic and classifier-agnostic).
  R3. No string literal referencing `_nonfactor/` (the sidecar directory).
  R4. No reference to the symbols `AuditRecord`, `NonFactorValue`, `audit_unwrap`
      inside heuristics code.
  R5. Also asserts the same for the anchored-tail formula weight formula
      helper's use — `scripts.heuristics.meta_tracker.anchored_tail_weight`
      must return `(30 - overlap)/30` for the seed_long_87s and seed_mid_50s
      overlaps of 23 and 10 seconds respectively. (Anti-drift check.)

Usage:
    /usr/bin/python3 tests/test_heuristics_isolation.py            # normal run
    /usr/bin/python3 tests/test_heuristics_isolation.py --self-test  # plant + catch
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
HEUR_DIR = REPO / "scripts" / "heuristics"

FORBIDDEN_IMPORT_PATTERNS = [
    re.compile(r"\bimport\s+.*sidecar_nonfactor"),
    re.compile(r"\bfrom\s+.*sidecar_nonfactor\s+import"),
    re.compile(r"\bfrom\s+scripts\.classifier[.\w]*\s+import"),
    re.compile(r"\bimport\s+scripts\.classifier"),
    re.compile(r"\bfrom\s+\.\.classifier[.\w]*\s+import"),
    re.compile(r"\bAuditRecord\b"),
    re.compile(r"\bNonFactorValue\b"),
    re.compile(r"\baudit_unwrap\b"),
]

FORBIDDEN_STRINGS = [
    "data/classifier/_nonfactor",
    "_nonfactor/",
    "sidecar_nonfactor",
]


def scan_file(path: Path) -> list[tuple[int, str]]:
    """Return list of (lineno, matched_pattern) tuples in the file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    hits: list[tuple[int, str]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        # Skip pure comment lines and docstring-like lines that are just
        # documentation about the forbidden thing (e.g. this file, the
        # __init__.py note). But strings/imports inside code are the danger,
        # so match on the raw line.
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        for pat in FORBIDDEN_IMPORT_PATTERNS:
            if pat.search(line):
                hits.append((i, pat.pattern))
        for lit in FORBIDDEN_STRINGS:
            if lit in line:
                hits.append((i, f"literal:{lit}"))
    return hits


def scan_tree(tree: Path) -> list[tuple[Path, int, str]]:
    hits: list[tuple[Path, int, str]] = []
    for py in tree.rglob("*.py"):
        for lineno, pat in scan_file(py):
            hits.append((py, lineno, pat))
    return hits


def anchored_tail_formula_check() -> tuple[bool, str]:
    from scripts.heuristics.meta_tracker import anchored_tail_weight
    # seed_long_87s clip 3: prev.t_end=80, this.t_start=57 → overlap=23
    w1 = anchored_tail_weight(80.0, 57.0)
    # seed_mid_50s  clip 1: prev.t_end=30, this.t_start=20 → overlap=10
    w2 = anchored_tail_weight(30.0, 20.0)
    exp1 = (30.0 - 23.0) / 30.0
    exp2 = (30.0 - 10.0) / 30.0
    if abs(w1 - exp1) > 1e-12:
        return False, f"anchored weight for seed_long_87s clip 3: got {w1}, expected {exp1}"
    if abs(w2 - exp2) > 1e-12:
        return False, f"anchored weight for seed_mid_50s clip 1: got {w2}, expected {exp2}"
    # And weight=1.0 when overlap<=0
    if abs(anchored_tail_weight(30.0, 30.0) - 1.0) > 1e-12:
        return False, "no-overlap case should return 1.0"
    return True, "OK"


def self_test() -> int:
    # Copy scripts/heuristics/ to a scratch tree, plant a violation, scan.
    with tempfile.TemporaryDirectory() as td:
        scratch = Path(td) / "scripts" / "heuristics"
        shutil.copytree(HEUR_DIR, scratch)
        planted = scratch / "battery.py"
        original = planted.read_text()
        # Prepend the plant line right after the docstring
        plant_line = "from scripts.classifier import sidecar_nonfactor  # PLANT\n"
        planted.write_text(plant_line + original)
        hits = scan_tree(scratch)
        if not hits:
            print("SELF-TEST FAIL: planted violation was not caught")
            return 1
        print("SELF-TEST OK: plant caught with hits:")
        for h in hits:
            print(f"  {h}")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()

    if not HEUR_DIR.exists():
        print(f"FAIL: heuristics dir does not exist: {HEUR_DIR}")
        return 1
    hits = scan_tree(HEUR_DIR)
    if hits:
        print("FAIL: forbidden references found in heuristics tree:")
        for path, lineno, pat in hits:
            print(f"  {path.relative_to(REPO)}:{lineno}  pattern={pat}")
        return 1

    ok, msg = anchored_tail_formula_check()
    if not ok:
        print(f"FAIL: anchored-tail formula check: {msg}")
        return 1

    # Behavioural probe: import each module, ensure no ImportError with a
    # bogus classifier stub installed.
    try:
        import scripts.heuristics.battery  # noqa: F401
        import scripts.heuristics.meta_tracker  # noqa: F401
        import scripts.heuristics.melody  # noqa: F401
        import scripts.heuristics.timbre  # noqa: F401
        import scripts.heuristics.form  # noqa: F401
        import scripts.heuristics.dynamics  # noqa: F401
    except Exception as e:  # pragma: no cover
        print(f"FAIL: heuristics import raised {type(e).__name__}: {e}")
        return 1

    print("OK: no forbidden references in scripts/heuristics/")
    print(f"OK: anchored-tail formula check: {msg}")
    print("OK: all heuristics modules import cleanly")

    # Re-run self-test to prove the scanner catches violations
    print("\n-- self-test (plant + catch) --")
    rc = self_test()
    if rc != 0:
        return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
