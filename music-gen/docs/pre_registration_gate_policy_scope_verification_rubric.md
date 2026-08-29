<!--
created: 2026-08-29T17:30:00Z
cycle: 47
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _infra/pre-registration-gate-policy-scope-verification-clone-1
-->

# Pre-registration gate policy — scope verification rubric (c47 Branch B)

## Purpose

The c46 amendment to `docs/pre_registration_gate_policy.md` claims:

> Under the current session's harness, `git add` and `git commit` are
> gated behind an approval prompt that cannot be satisfied inside a
> single worker turn. Git commits happen at a HIGHER harness level
> via periodic sweep.

This rubric governs the empirical verification of that claim across
the git-log commit history reachable via `git log --all` in this
workspace. The verdict fires **strictly per the three clauses below**;
no reconciliation clauses may be added retroactively.

## Frozen verdict set

The verdict is one of exactly three labels:

- **HARNESS_CONSTRAINT_CONFIRMED** — every commit classified as
  worker-authored in the git-log history occurred at periodic-sweep
  boundaries (author-email match with periodic-sweep bot OR
  commit-message marker match with `(periodic sweep)` /
  `(post-merge cycle N)` / `(cycle N merge...)`). Zero commits are
  classified as worker-inside-turn.

- **HARNESS_CONSTRAINT_LIFTED** — at least one commit is classified
  as worker-authored **and** carries evidence of landing inside a
  single worker turn (commit-message marker names a specific
  substantive milestone with no periodic-sweep envelope and no
  post-merge envelope), and that class is not empty across the
  entire history.

- **MIXED** — evidence supports both patterns partitioned by session
  context class. Some session contexts produce only periodic-sweep
  commits; other contexts produce worker-inside-turn commits.

Decision precedence: if the worker-inside-turn count is 0, verdict is
CONFIRMED. Otherwise, if the periodic-sweep count is also > 0 the
verdict is MIXED. Otherwise (all commits worker-inside-turn) the
verdict is LIFTED.

## Session-context classes

Every commit is bucketed into exactly one of these classes:

| class | signals |
|---|---|
| `periodic-sweep` | marker match: `(periodic sweep)` or the trailing envelope `Add music-gen run artifacts (periodic sweep)`. |
| `merge-integration` | marker match: `(post-merge cycle N)`, `(cycle N merge ...)`, or `Add music-gen run artifacts (... merge ...)`. |
| `worker-turn` | marker begins with a substantive milestone id (`M-*:`, `_infra/*:`, `_plan/*:`, `_manager/*:`, `_archive/*:`) OR is a hand-authored lowercase phrase like `commit ear v1 rubric`. Not enveloped by periodic-sweep or merge markers. |
| `auditor-turn` | marker begins with an `audit:` / `AUDIT:` prefix or names an `_manager/audit-*` milestone. |
| `researcher-turn` | marker begins with a `researcher:` / `plan:` prefix or names an `_plan/*` milestone from the researcher role. |
| `harness-auto-write` | marker match: `Add music-gen run artifacts` without `periodic sweep` or `merge` envelope, and no worker milestone prefix. |
| `unknown` | none of the above match, or the two signals (email_class, marker_class) disagree with `confidence=medium`. |

Two-signal classifier:

1. **email_class**: derived from `%ae`. In this session's history all
   commits carry `noreply@anthropic.com`; that resolves to `bot` as
   `email_class`. Alternative emails (human contributors) would
   resolve to `human`, but there are none in this workspace.

2. **marker_class**: derived from `%s` (first 60 chars) via the
   ordered regex list above. First match wins.

3. **session_context**: `marker_class` (email_class alone cannot
   distinguish worker-turn from periodic-sweep when both are the bot).
   `confidence=high` when both signals agree in identifying a
   bot-authored event; `confidence=medium` when only `marker_class`
   fires; `confidence=low` reserved for future human-authored rows.

## Pre-registration gate ordering (this cycle)

- The rubric doc mtime must be strictly less than every script under
  `scripts/pre_reg_policy_verify/` (test 01, HARD gate per c46 path
  (ii) amendment).
- The rubric doc git-log commit ordering is ADVISORY (test 02, SOFT
  gate per the same amendment). MERGE_DEFERRED acceptable — this
  cycle's commits land at the harness periodic-sweep boundary.

## Determinism envelope

All classifier / matrix / verdict scripts run under:

```
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8
```

Byte-determinism × 2 asserted on `commit_classification.tsv`,
`session_context_matrix.tsv`, `verdict.json` (SHA-256 equal across
two fresh `tempfile.mkdtemp()` invocations).

## Rubric hash

The SHA-256 of this file (canonical bytes as committed) is pinned to
`data/pre_reg_policy_verify/rubric_hash.txt` and embedded in
`verdict.json.rubric_hash`. Three-way byte-equality is asserted by
test 03.

## Reconciliation actions (post-verdict)

Exactly one of the following fires:

- **CONFIRMED** → append one paragraph + one evidence-count table to
  `docs/pre_registration_gate_policy.md` §2 (prior text preserved
  verbatim; append-only). Ledger event
  `_infra/…/amendment-empirically-confirmed-clone-1`.
- **LIFTED** → do not touch §2. Emit
  `_plan/pre-registration-gate-policy-sunset-proposal-clone-1` naming
  the session-context class that can commit inside a turn (path (i)
  becomes mandatory for that class).
- **MIXED** → add a new §3 to `docs/pre_registration_gate_policy.md`
  listing which session contexts land in the periodic-sweep bucket
  vs. which can commit inside a turn (§1 + §2 preserved verbatim).

## Falsifiability

The rubric is falsified by a single row in
`data/pre_reg_policy_verify/commit_classification.tsv` whose
`session_context` is `worker-turn` and whose commit lands OUTSIDE the
`(periodic sweep)` / `(post-merge ...)` envelopes yet within a single
worker turn attributable via `Claude-Session:` trailer or similar
session-bounded marker. Such rows drive the verdict to LIFTED or
MIXED.
