#!/usr/bin/env python3
# M-RULES-1/schema — deterministic YAML equivalent generator.
#
# Author: cyd7bevdr@mozmail.com, cycle 6 (fork 3168fb0e47a1 / clone-1).
#
# Contract: yaml.safe_load(rules_v1.yaml) == json.load(rules_v1.json)
# exactly, at every level. YAML is a strict mechanical translation of JSON;
# JSON remains authoritative.

import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

import yaml  # noqa: E402

_HERE = Path(__file__).resolve().parent
JSON_PATH = _HERE / "rules_v1.json"
YAML_PATH = _HERE / "rules_v1.yaml"


def build():
    with open(JSON_PATH, "r") as f:
        schema = json.load(f)
    with open(YAML_PATH, "w") as f:
        f.write(
            "# M-RULES-1/schema rules_v1.yaml\n"
            "# AUTO-GENERATED from rules_v1.json by scripts/rules/schema/build_yaml.py.\n"
            "# JSON is authoritative; this YAML is a mechanical safe_load-equivalent view.\n"
            "# Regenerate: /usr/bin/python3 scripts/rules/schema/build_yaml.py\n"
        )
        yaml.safe_dump(schema, f, sort_keys=True, default_flow_style=False)
    # Verify round-trip.
    with open(YAML_PATH, "r") as f:
        loaded = yaml.safe_load(f)
    with open(JSON_PATH, "r") as f:
        original = json.load(f)
    assert loaded == original, "YAML round-trip failed: loaded YAML does not equal JSON parse"
    print(f"wrote {YAML_PATH}; round-trip equality verified.")


if __name__ == "__main__":
    build()
