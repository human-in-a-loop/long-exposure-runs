#!/usr/bin/env python3
"""Build palette_v1.yaml as a deterministic mirror of palette_v1.json.

Verifies yaml.safe_load(yaml) deep-equal json.load(json) before writing.
Idempotent: rerun produces byte-identical output.
"""
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

import yaml  # noqa: E402

_HERE = Path(__file__).resolve().parent
JSON_PATH = _HERE / "palette_v1.json"
YAML_PATH = _HERE / "palette_v1.yaml"


def build_and_write() -> bool:
    with open(JSON_PATH) as f:
        data = json.load(f)
    with open(YAML_PATH, "w") as f:
        yaml.safe_dump(data, f, sort_keys=True, default_flow_style=False, allow_unicode=False)
    with open(YAML_PATH) as f:
        y = yaml.safe_load(f)
    if y != data:
        print("[FAIL] YAML does not round-trip to JSON", file=sys.stderr)
        return False
    print(f"Wrote {YAML_PATH} (load-identical to {JSON_PATH})")
    return True


if __name__ == "__main__":
    sys.exit(0 if build_and_write() else 1)
