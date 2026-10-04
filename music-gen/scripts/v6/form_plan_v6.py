#!/usr/bin/python3
"""v6 Phase 0 — thin wrapper around scripts/v5/form_plan_v5.py (READ-ONLY import) for the 29-song corpus.

created: 2026-10-04
milestone: M-V6-DATA-0/form-plan-v6-wrapper

form_plan_v5.py:63 FOCUS_ELIGIBLE = (WIG, CG, Rome) and :317 indexes per_song[s] for each -> KeyError for Chicken
Grease (absent from the v6 corpus) or for any focus song that has not landed. This wrapper sets FOCUS_ELIGIBLE to the
v6 focus songs (WIG, Rome, Disco A) that are in the harmony chain's gate.used; if none is, the first three eligible
songs stand in (disclosed on stdout and in the output's R1 block via the module constant). Then form_plan_v5.main runs
unchanged (prereg mtime gate, clustering, Markov model, R1 rule, output path).
Discipline: /usr/bin/python3 guard; env pins (form_plan_v5 sets them at import); no PRNG.
"""
from __future__ import annotations

import sys
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.v6_data_common import FOCUS_ORDER, interpreter_guard, pin_env, read_json  # noqa: E402

pin_env()
interpreter_guard()
from scripts.v5 import form_plan_v5 as F  # noqa: E402  READ-ONLY (module constant patched in-process only)


def choose_focus(used: list[str]) -> tuple[tuple[str, ...], str]:
    present = tuple(s for s in FOCUS_ORDER if s in used)
    if present:
        return present, f"v6 focus songs in the chain: {list(present)} (CG/PD absent from the corpus)"
    return tuple(used[:3]), f"no v6 focus song in the chain; R1 evaluated on the first {min(3, len(used))} eligible songs {used[:3]}"


def main(argv=None) -> int:
    chain_p = _WS / F.CHAIN
    if not chain_p.exists():
        raise SystemExit(f"form_plan_v6: {F.CHAIN} missing — run the harmony stage first")
    used = list(read_json(chain_p)["gate"]["used"])
    focus, why = choose_focus(used)
    F.FOCUS_ELIGIBLE = focus
    print(f"form_plan_v6: FOCUS_ELIGIBLE -> {list(focus)} ({why})")
    return F.main(argv)


if __name__ == "__main__":
    sys.exit(main())
