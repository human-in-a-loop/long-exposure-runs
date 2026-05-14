# created: 2026-05-13T21:45:00Z
# cycle: 2
# run_id: run-2026-05-13T204826Z
# agent: worker
# milestone: M-3
"""Export the task spec JSON Schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from alignment_test_factory.schemas import TaskSpec  # noqa: E402


def main() -> None:
    out = ROOT / "schemas" / "task_spec.schema.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    schema = TaskSpec.model_json_schema()
    out.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
