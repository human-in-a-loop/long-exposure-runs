#!/usr/bin/python3
"""v6 Phase 0 — thin wrapper around scripts/v5/generate_v5.py (READ-ONLY import) for N = 29 donors.

created: 2026-10-04
milestone: M-V6-DATA-0/generate-v6-wrapper

generate_v5.py renders every donor spec it is given (`--songs N`, :852 default 5) — that part scales. What does not:
the F1 / F2 / F3 roll-up enums at :1051, :1059-1060 and :1070 compare counts against the literal 5 ("5 of 5"), so with
29 donors they can never read *_LANDS. This wrapper runs generate_v5.main(argv) unchanged and then appends a
`v6_enums` block to iteration_rollup.json recomputed for N = the number of regular songs rendered (LANDS iff every
clause holds on all N; PARTIAL iff >= 60 % of N; else FAILS). The v5 fields are left as written (byte-compat).
All flags pass through to generate_v5 (e.g. --iteration 1 --songs 29 --f2 --velocity-mode f2 --f3 --prove-replay
--form-plan data/v5/rules/form_plan_v5.json --tempo-overrides data/v5/corpus/tempo_overrides_c86.json).
Discipline: /usr/bin/python3 guard; env pins (generate_v5 sets them at import); no PRNG.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.v6_data_common import interpreter_guard, pin_env  # noqa: E402

pin_env()
interpreter_guard()

PARTIAL_FRAC = 0.6


def _enum(n_ok: int, n: int, prefix: str) -> str:
    if n and n_ok == n:
        return f"{prefix}_LANDS"
    if n and n_ok >= math.ceil(PARTIAL_FRAC * n):
        return f"{prefix}_PARTIAL"
    return f"{prefix}_FAILS"


def v6_enums(rollup: dict, prove_replay: bool, rms_test: bool) -> dict:
    regular = [s for s in rollup.get("songs", []) if "f5" not in s]
    n = len(regular)
    out = {"n_regular_songs": n, "rule": f"LANDS iff every clause holds on all N; PARTIAL iff >= {int(PARTIAL_FRAC * 100)} % of N; else FAILS "
                                        "(v5 enums at generate_v5.py:1051,1059-1060,1070 compare against the literal 5)"}
    if "f1_enum" in rollup:
        n_ok = sum(1 for s in regular if s.get("all_clauses"))
        out["f1"] = {"n_all_clauses": n_ok, "enum": _enum(n_ok, n, "FORM_PLAN")}
    if "f2" in rollup:
        vel = sum(1 for s in regular if s.get("velocities_present"))
        rms = sum(1 for s in regular if s.get("rms_variance_passes")) if rms_test else None
        rep = sum(1 for s in regular if s.get("replay_proof") == "REPLAY_PROOF_HOLDS") if prove_replay else None
        clauses = {"velocities_present_all": vel == n and n > 0, "rms_variance_all": (rms == n and n > 0) if rms is not None else None,
                   "replay_x2_all": (rep == n and n > 0) if rep is not None else None}
        counts = [vel] + [c for c in (rms, rep) if c is not None]
        n_ok = min(counts) if counts else 0
        out["f2"] = {"n_velocities_present": vel, "n_rms_variance_pass": rms, "n_replay_holds": rep, "clauses": clauses,
                     "enum": "F2_LANDS" if all(v is True for v in clauses.values() if v is not None) and n > 0 else _enum(n_ok, n, "F2").replace("F2_LANDS", "F2_PARTIAL")}
    if "f3" in rollup:
        both = sum(1 for s in regular if s.get("f3", {}).get("per_song_ok") and (not prove_replay or s.get("replay_proof") == "REPLAY_PROOF_HOLDS"))
        out["f3"] = {"n_songs_all_per_song_clauses": both, "enum_per_song": _enum(both, n, "F3")}
    return out


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    from scripts.v5 import generate_v5 as GEN  # noqa: E402  READ-ONLY (imported lazily: heavy audio deps)
    rc = GEN.main(argv)
    if rc:
        return rc
    out_dir = None
    iteration = 1
    for i, a in enumerate(argv):
        if a == "--out" and i + 1 < len(argv):
            out_dir = Path(argv[i + 1])
        if a == "--iteration" and i + 1 < len(argv):
            iteration = int(argv[i + 1])
    out_dir = out_dir or Path(f"data/v5/gen/iteration_{iteration:02d}")
    rp = _WS / out_dir / "iteration_rollup.json" if not out_dir.is_absolute() else out_dir / "iteration_rollup.json"
    rollup = json.loads(rp.read_text())
    rollup["v6_enums"] = v6_enums(rollup, "--prove-replay" in argv, "--rms-variance-test" in argv)
    rollup["v6_wrapper"] = {"script": "scripts/v6/generate_v6.py", "argv": argv}
    rp.write_text(json.dumps(rollup, sort_keys=True, indent=2) + "\n")
    print(f"generate_v6: v6 enums {json.dumps(rollup['v6_enums'], sort_keys=True)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
