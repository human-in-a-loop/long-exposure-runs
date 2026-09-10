#!/usr/bin/python3
"""Shared repo-root helper for scripts that live below data/ (e.g. data/v5/gen/iteration_NN/plot_*.py).

created: 2026-09-10T03:15:00Z
cycle: 89
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F5-interpolation-demo

c87 + c88 both slipped on a hard-coded `Path(__file__).resolve().parents[N]` (one parent short) in the per-iteration plot
scripts (c88 auditor MINOR (b)). `repo_root(start)` walks up from `start` until it finds the workspace markers
(`promise_ledger.jsonl` AND `scripts/v5/`) and returns that directory; it raises instead of guessing. Pure stdlib, no I/O
beyond `Path.exists`, no PRNG.

Bootstrap from a script under data/ (the module itself has to be found first; this is the ONLY walk a caller writes):

    from pathlib import Path
    import sys
    _p = Path(__file__).resolve()
    _ws = next(p for p in _p.parents if (p / "scripts" / "v5" / "repo_root.py").exists())
    sys.path.insert(0, str(_ws))
    from scripts.v5.repo_root import repo_root
    os.chdir(repo_root(__file__))
"""
from __future__ import annotations

from pathlib import Path

MARKERS = ("promise_ledger.jsonl", "scripts/v5")


def repo_root(start: str | Path | None = None) -> Path:
    """Return the workspace root that contains every MARKERS entry, walking up from `start` (a file or directory)."""
    p = Path(start).resolve() if start is not None else Path(__file__).resolve()
    for cand in (p, *p.parents):
        if all((cand / m).exists() for m in MARKERS):
            return cand
    raise FileNotFoundError(f"repo_root: no ancestor of {p} contains {MARKERS}")


if __name__ == "__main__":
    print(repo_root(__file__))
