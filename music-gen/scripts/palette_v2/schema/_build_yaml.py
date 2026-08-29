#!/usr/bin/env python3
"""Build palette_v2.yaml from palette_v2.json (safe_dump). Interpreter-guarded."""
import sys
assert sys.executable == "/usr/bin/python3"
import json
from pathlib import Path
import yaml

_HERE = Path(__file__).resolve().parent
src = _HERE / "palette_v2.json"
dst = _HERE / "palette_v2.yaml"

d = json.loads(src.read_text())
with open(dst, "w") as f:
    yaml.safe_dump(d, f, sort_keys=True, default_flow_style=False)

y = yaml.safe_load(dst.read_text())
assert y == d, "YAML load != JSON load"
print(f"wrote {dst} ({dst.stat().st_size} bytes); YAML == JSON verified")
