# created: 2026-05-13T21:45:00Z
# cycle: 2
# run_id: run-2026-05-13T204826Z
# agent: worker
# milestone: M-3
"""Validate bundled task spec examples."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from alignment_test_factory.schemas import TaskSpec  # noqa: E402


def validate_file(path: Path) -> tuple[bool, str]:
    try:
        TaskSpec.model_validate_json(path.read_text(encoding="utf-8"))
    except ValidationError as exc:
        first = exc.errors()[0]
        return False, str(first.get("msg", exc))
    return True, "ok"


def main() -> int:
    failures: list[str] = []
    for path in sorted((ROOT / "examples" / "valid").glob("*.json")):
        ok, message = validate_file(path)
        print(f"valid   {path.name}: {message}")
        if not ok:
            failures.append(f"expected valid spec failed: {path}: {message}")
    for path in sorted((ROOT / "examples" / "invalid").glob("*.json")):
        ok, message = validate_file(path)
        status = "unexpected pass" if ok else f"rejected: {message}"
        print(f"invalid {path.name}: {status}")
        if ok:
            failures.append(f"expected invalid spec passed: {path}")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
