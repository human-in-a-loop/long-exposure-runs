#!/usr/bin/env python3
"""c7 byte-determinism x2 verifier + per-artifact sidecar emitter.

For each c7 script, re-runs it twice into the on-disk output path
(scripts are pure functions of their inputs — no external state) and
records SHA-256 equality. Writes byte-det sidecars per artifact.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"byte_det_c7 requires /usr/bin/python3 (got {sys.executable})"
    )

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)

SCRIPTS = [
    ("scripts/v3_spine/torch213_reproduce_probe.py",
     "data/v3_spine/cycle7/torch213_reproduce_probe.json"),
    ("scripts/v3_spine/empty_stem_duration_sanity.py",
     "data/v3_spine/cycle7/empty_stem_duration_sanity.json"),
    ("scripts/v3_spine/rc7_canonicality_metrics.py",
     "data/v3_spine/cycle7/rc7_canonicality_metrics.json"),
]

SIDECAR = _REPO / "data" / "v3_spine" / "cycle7" / "byte_determinism.json"


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> None:
    det: dict = {"cycle": 7, "per_script": {}}
    all_equal = True
    for script, out in SCRIPTS:
        subprocess.run(["/usr/bin/python3", script], check=True, capture_output=True)
        run1 = Path(out).read_bytes()
        subprocess.run(["/usr/bin/python3", script], check=True, capture_output=True)
        run2 = Path(out).read_bytes()
        eq = run1 == run2
        det["per_script"][script] = {
            "output_path": out,
            "run1_sha256": _sha256_bytes(run1),
            "run2_sha256": _sha256_bytes(run2),
            "equal": eq,
        }
        if not eq:
            all_equal = False

        # Per-artifact byte-det sidecar next to the output.
        side = Path(out).with_suffix(".byte_determinism.json")
        side.parent.mkdir(parents=True, exist_ok=True)
        side.write_text(json.dumps({
            "path": out,
            "run1_sha256": _sha256_bytes(run1),
            "run2_sha256": _sha256_bytes(run2),
            "equal": eq,
        }, indent=2, sort_keys=True) + "\n")

    det["all_equal"] = all_equal
    SIDECAR.write_text(json.dumps(det, indent=2, sort_keys=True) + "\n")
    print(f"wrote {SIDECAR.relative_to(_REPO)}  all_equal={all_equal}")


if __name__ == "__main__":
    main()
