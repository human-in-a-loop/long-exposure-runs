#!/usr/bin/env -S /usr/bin/python3
"""Static-analysis enforcement of the M-CLASS-1 non-factor sidecar isolation.

Runs under /usr/bin/python3, zero external deps.

Enforces THREE architectural rules on the whole `scripts/` tree:

  R1. No module OUTSIDE `scripts/classifier/` may `import` or `from ...
      import` the `sidecar_nonfactor` symbol.

  R2. No script anywhere in `scripts/` (except `sidecar_nonfactor.py`
      itself and `write_sidecars.py`) may reference the string
      "_nonfactor/" as a path (open, Path, os.path.join, io functions, ...).

  R3. The `AuditRecord`/`NonFactorValue` symbols must not appear outside
      `scripts/classifier/`. If a downstream author starts consuming
      `AuditRecord.audit_unwrap()`, this test catches it.

Also runs a live behavioral probe: constructs a `NonFactorValue`, tries
common misuse patterns (str, +, ==, dict key, bool, json.dumps), and
asserts each raises `TypeError`.

The test is designed to PASS on the current tree and FAIL the moment a
downstream module imports the sidecar. To verify the enforcement actually
works, this file also contains a `plant_and_verify` helper (invoked when
run with `--self-test`) that writes a synthetic violator into a scratch
dir and confirms the scanner catches it.

Usage:
    /usr/bin/python3 tests/test_sidecar_isolation.py            # normal run
    /usr/bin/python3 tests/test_sidecar_isolation.py --self-test  # plant + catch
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
# Allow `from scripts.classifier...` regardless of cwd.
sys.path.insert(0, str(REPO))
SCRIPTS = REPO / "scripts"
CLASSIFIER = SCRIPTS / "classifier"
SIDECAR_FILE = CLASSIFIER / "sidecar_nonfactor.py"
WRITER_FILE = CLASSIFIER / "write_sidecars.py"


# R1: any of these appearing in an import line outside scripts/classifier/
FORBIDDEN_IMPORT_PATTERNS = [
    re.compile(r"\bimport\s+.*sidecar_nonfactor"),
    re.compile(r"\bfrom\s+.*sidecar_nonfactor\s+import"),
    # even a relative form inside a wandering package
    re.compile(r"\bfrom\s+\.[.\w]*\s+import.*sidecar_nonfactor"),
    # Symbol-level probes (R3):
    re.compile(r"\bAuditRecord\b"),
    re.compile(r"\bNonFactorValue\b"),
    re.compile(r"\baudit_unwrap\b"),
    re.compile(r"\bread_for_audit_only\b"),
]

# R2: forbidden path substring
FORBIDDEN_PATH_LITERAL = "_nonfactor/"


def _iter_py_files(root: Path):
    for p in root.rglob("*.py"):
        # Skip caches and stale dirs.
        if "__pycache__" in p.parts or "stale" in p.parts:
            continue
        yield p


def scan_tree(scripts_root: Path,
              allowed_files: set[Path]) -> list[tuple[Path, int, str, str]]:
    """Return list of (file, line_no, rule_id, offending_line)."""
    violations = []
    for py in _iter_py_files(scripts_root):
        # Skip files in the sidecar-owning subtree (allowed to reference).
        if py in allowed_files:
            continue
        text = py.read_text()
        for i, line in enumerate(text.splitlines(), 1):
            for pat in FORBIDDEN_IMPORT_PATTERNS:
                if pat.search(line):
                    violations.append((py, i, "R1/R3", line.strip()))
            if FORBIDDEN_PATH_LITERAL in line:
                violations.append((py, i, "R2", line.strip()))
    return violations


def behavior_probe() -> list[str]:
    """Live check: NonFactorValue really refuses misuse."""
    from scripts.classifier.sidecar_nonfactor import NonFactorValue
    v = NonFactorValue("rock")
    fails = []

    def _expect_typeerror(name, callable_):
        try:
            callable_()
        except TypeError:
            return
        fails.append(f"{name}: expected TypeError, got no error")

    _expect_typeerror("str(v)", lambda: str(v))
    _expect_typeerror("v + 'x'", lambda: v + "x")
    _expect_typeerror("'x' + v", lambda: "x" + v)
    _expect_typeerror("v == v", lambda: v == v)
    _expect_typeerror("hash(v)", lambda: hash(v))
    _expect_typeerror("bool(v)", lambda: bool(v))

    # audit_unwrap() DOES work (this is intentional, and grep-catchable).
    try:
        assert v.audit_unwrap() == "rock"
    except Exception as e:
        fails.append(f"audit_unwrap misbehaved: {e}")

    # json.dumps(v) fails because default encoder cannot handle it.
    try:
        json.dumps({"g": v})
    except TypeError:
        pass
    else:
        fails.append("json.dumps(v) did not raise TypeError")
    return fails


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    self_test = "--self-test" in argv

    allowed = {
        SIDECAR_FILE,
        WRITER_FILE,
    }

    # ---- Rule scan on real tree
    violations = scan_tree(SCRIPTS, allowed)
    problems = list(violations)

    # ---- Behavior probe on live objects
    beh_fails = behavior_probe()
    if beh_fails:
        for f in beh_fails:
            print(f"[behavior] FAIL: {f}")

    # ---- Optional self-test: plant a violator and confirm scanner catches it
    plant_result = None
    if self_test:
        with tempfile.TemporaryDirectory() as td:
            fake_scripts = Path(td) / "scripts"
            (fake_scripts / "downstream").mkdir(parents=True)
            plant = fake_scripts / "downstream" / "leaky_features.py"
            plant.write_text(
                "from scripts.classifier.sidecar_nonfactor import read_for_audit_only\n"
                "def get_genre(cid):\n"
                "    r = read_for_audit_only(cid, i_understand_this_is_non_factor=True)\n"
                "    return r.genre.audit_unwrap()  # SHOULD BE CAUGHT\n"
                "path = 'data/classifier/_nonfactor/foo.json'  # SHOULD BE CAUGHT\n"
            )
            caught = scan_tree(fake_scripts, allowed_files=set())
            plant_result = len(caught)
            print(f"[self-test] planted violator: caught {plant_result} violations")
            for p, ln, rule, txt in caught:
                print(f"  {p.name}:{ln} {rule} :: {txt}")
            if plant_result == 0:
                print("[self-test] FAIL: planted violator went undetected!")
                problems.append(("<self-test>", 0, "SELF-TEST", "plant not caught"))

    # ---- Report
    if not problems and not beh_fails:
        print("[isolation] PASS "
              f"(scanned {sum(1 for _ in _iter_py_files(SCRIPTS))} .py files "
              f"under scripts/; NonFactorValue behavior probe: OK"
              + (f"; self-test caught {plant_result} planted violations"
                 if self_test else "")
              + ")")
        return 0

    print("[isolation] FAIL")
    for py, i, rule, line in problems:
        print(f"  {py}:{i}  [{rule}]  {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
