#!/usr/bin/python3
# created: 2026-08-29T17:31:00Z  cycle: 47  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: _infra/pre-registration-gate-policy-scope-verification-clone-1
"""c47 Branch B — empirical scope verification of c46 harness-constraint amendment.

Modules:
  grep_git_log     — subprocess-drives `git log --all` and writes raw TSV.
  classify_commits — two-signal classifier per commit.
  session_context_matrix — aggregate by (session-context class × count).
  verdict          — apply the rubric to the classified table.

All modules print a startup banner to stdout and are guarded by an
interpreter check (/usr/bin/python3) per c43 CLI-Startup-Silence
interdiction.
"""
