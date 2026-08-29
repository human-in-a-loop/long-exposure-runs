#!/usr/bin/python3
"""c46 byte-determinism × 2 check for M-EAR-1/real-label-training-v2.

Correct semantics: run train + evaluate TWICE from a defined initial
state, compare SHA-256 on the three gated artifacts. Records the pair
of run SHAs in data/ear_v2/determinism_check_c46.json.

Startup banner emitted before heavy imports per c43 CLI-Startup-Silence
Pattern interdiction.
"""
# created: 2026-08-29T16:35:00Z  cycle: 46  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: _manager/M-EAR-1-v2-verdict-adjudication-and-gate-closure

from __future__ import annotations

import sys

print("[c46:determinism_check_c46] starting", flush=True)
assert sys.executable == "/usr/bin/python3", sys.executable

import hashlib
import json
from pathlib import Path

DATA_DIR = Path("data/ear_v2")
GATED = ["training_result.json", "corn_head_v2.pt", "sb_v2_verdict.json"]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _run_once() -> dict[str, str]:
    from scripts.ear_v2.train_v2 import train
    from scripts.ear_v2.evaluate_sb_v2 import evaluate

    _ = train()
    _ = evaluate()
    return {name: _sha(DATA_DIR / name) for name in GATED}


def main() -> dict:
    print("[c46:determinism_check_c46] run 1 start", flush=True)
    r1 = _run_once()
    print("[c46:determinism_check_c46] run 1 done", flush=True)
    r2 = _run_once()
    print("[c46:determinism_check_c46] run 2 done", flush=True)

    diffs = [k for k in GATED if r1[k] != r2[k]]
    all_equal = not diffs

    out = {
        "cycle": 46,
        "gated_artifacts": GATED,
        "run_1": r1,
        "run_2": r2,
        "byte_determinism_x2": all_equal,
        "diffs": diffs,
        "verdict": "DETERMINISM_VERIFIED" if all_equal else "DETERMINISM_FAILED",
        "narrative": (
            "Byte-determinism × 2 across all three gated artifacts."
            if all_equal
            else f"Byte-determinism × 2 FAILED on {diffs}. Honest negative "
            f"finding published; c47 first-class ticket."
        ),
    }
    (DATA_DIR / "determinism_check_c46.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n"
    )
    return out


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
