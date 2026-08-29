#!/usr/bin/python3
# created: 2026-08-29T17:31:00Z  cycle: 47  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: _infra/pre-registration-gate-policy-scope-verification-clone-1
"""Grep git-log history reachable via `git log --all` into a TSV.

Columns: commit_sha\tauthor_email\tiso_ts\tsubject
Output : data/pre_reg_policy_verify/git_log_raw.tsv
Idempotent + deterministic (git log ordering is stable).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Interpreter guard (c43 CLI-Startup-Silence interdiction — must print banner).
_ALLOWED = ("/usr/bin/python3",)
if sys.executable not in _ALLOWED and not os.environ.get("PRE_REG_POLICY_VERIFY_ALLOW_ANY_PYTHON"):
    print(f"[pre_reg_policy_verify.grep_git_log] interpreter guard: expected one of "
          f"{_ALLOWED}, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

BANNER = "[pre_reg_policy_verify.grep_git_log] c47 Branch B — starting"
print(BANNER)

ROOT = Path(__file__).resolve().parent.parent.parent


def run(out_path: Path) -> int:
    cmd = ["git", "log", "--all", "--format=%H%x09%ae%x09%aI%x09%s"]
    proc = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Trailing newline explicit; git log emits a trailing newline naturally.
    body = proc.stdout
    if not body.endswith("\n"):
        body += "\n"
    out_path.write_text(body)
    n = body.count("\n")
    print(f"[pre_reg_policy_verify.grep_git_log] wrote {n} rows -> {out_path}")
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=ROOT / "data" / "pre_reg_policy_verify" / "git_log_raw.tsv")
    args = ap.parse_args()
    run(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
