# _infra/harness-clone-namespace-guard — Frozen 2-verdict rubric

**Cycle:** 33 · **Branch:** clone-2 of fork 4595e91f7574 · **Frozen at:** 2026-08-29T04:30:00Z

This rubric is committed to disk BEFORE any edit lands in `long_exposure/workspace_bootstrap.py`.
Its SHA-256 is echoed verbatim into `tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt`,
and `tests/test_harness_clone_namespace_guard.py::test_11_rubric_sha_fixture_matches_doc` asserts
byte-equality of the fixture value and the on-disk doc SHA on every run.

## Mechanism claim (falsifiable)

Given the cycle-32 `docs/fanout_namespace_convention.md`, writer-boundary enforcement in
`long_exposure.workspace_bootstrap.append_ledger_event` can:

1. In **default mode**, silently auto-suffix any clone-emitted `milestone_id` matching
   `^(_infra|_run|_plan|_archive|_manager)/` (and not already `-clone-<digit>+`-terminated)
   to `<milestone_id>-clone-<k>` (`k` = the clone's `AGENT_FORK_CLONE_K`), parity with the
   c22 `_infra/harness-auto-write-namespacing` upstream fix's silent auto-namespacing;
2. In **strict mode** (opt-in via env var `MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1`),
   raise a typed `LedgerNamespaceViolation` (subclass of
   `long_exposure.tools._ledger_schema.LedgerSchemaError`) with a field-named message
   that includes the offending identifier, the detected clone-`k`, and a pointer to
   `docs/fanout_namespace_convention.md`;

both without changing the public API of `append_ledger_event(workspace, event)` and without
altering the behavior on any of the 468 pre-existing ledger rows in `promise_ledger.jsonl`
(whose clone-touched leading-underscore rows already comply after the cycle-32 retroactive
renames).

## Verdict definitions

### GUARD_LANDS — mechanism confirmed

Requires **ALL** of:

1. **Baseline replay green** — 468/468 pre-existing rows in `promise_ledger.jsonl` pass
   the tightened `append_ledger_event` unchanged, under BOTH default AND strict modes.
   Zero rows reject; zero rows are mutated.
2. **Test suite green** — `tests/test_harness_clone_namespace_guard.py` runs ≥10
   test cases, all PASS. Invocation:
   `PYTHONPATH=. /usr/bin/python3 tests/test_harness_clone_namespace_guard.py`.
3. **Caller-boundary invariant** — zero source-code changes outside `long_exposure/*`
   (the established WARN exemption for the internal writer chain). All existing test
   files and all `scripts/*` and `tools/*` callers of `append_ledger_event` continue
   to work unmodified.
4. **Strict-mode toggle round-trip** — with `MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1`
   set, a manufactured event with `milestone_id=_infra/foo` emitted from a clone
   context raises `LedgerNamespaceViolation`. With the env var unset (or `=0`), the
   same manufactured event is silently mutated to `milestone_id=_infra/foo-clone-<k>`.
   Both modes leave the 468-row baseline unchanged.
5. **Public API preserved** — `inspect.signature(append_ledger_event)` returns exactly
   `(workspace, event)`, unchanged from the c22/c14 chain.

### GUARD_INSUFFICIENT — mechanism refuted or under-specified

Fires on **ANY** of:

- Any of the 468 pre-existing rows rejects under the tightened writer (either mode).
- The guard fails to catch a manufactured `_infra/foo`-from-clone-context violation
  (default mode does not mutate; strict mode does not raise).
- Public API of `append_ledger_event` changes (new required parameter, changed
  signature, changed return contract).
- Test suite fails.
- 468-row baseline replay diverges between default and strict modes.

## Additional invariants (asserted by the test suite)

- `LedgerNamespaceViolation` is a subclass of
  `long_exposure.tools._ledger_schema.LedgerSchemaError` (MRO-verified). A caller that
  already catches `LedgerSchemaError` catches this new type transparently.
- `M-*` identifiers are NEVER touched by the guard.
- Identifiers without a leading `_<family>/` prefix (bare tokens like `foo/bar`) are
  NEVER touched.
- The guard is idempotent: an identifier already ending in `-clone-<digit>+` is never
  double-suffixed (would produce `-clone-2-clone-2`).
- `_lint_clone_shadow(shadow_path)` surfaces the same violation at the concat boundary,
  with `<shadow_path>:<line_number>` annotation.
- The five leading-underscore infra prefixes covered: `_infra/`, `_run/`, `_plan/`,
  `_archive/`, `_manager/`. Parametric test coverage over the full set.
- Rubric-doc SHA equals fixture SHA (git/mtime-ordering enforced by
  `test_12_rubric_committed_before_writer_edits`).

## Explicit non-goals (out of scope for this cycle)

- The upstream `promise_check` parser fragility (c32 side-finding at
  `long_exposure/tools/promise_check.py:159-194` — substring match on `"milestone id"`)
  is NOT addressed here. It lives in `~/human-in-a-loop/long_exposure/tools/` and is
  the responsibility of the deferred `_manager/promise-check-parser-fragility`
  milestone.
- The c22 `_infra/harness-auto-write-namespacing` implementation
  (`long_exposure.exploration._append_report_artifact_event`) is a READ-ONLY reference
  — its `_is_clone` pattern is mirrored, not imported, to keep the writer standalone.
- No changes to caller-side scripts under `scripts/palette/`, `scripts/palette_probe/`,
  `scripts/palette_render/`, `scripts/dawdreamer_state/`, `scripts/tex/`, `scripts/ear/`.
- No modification of the schema module `long_exposure/tools/_ledger_schema.py` itself —
  the writer extends its use of the SSoT symbols, it does not add to the schema.

## Reference

Cycle 32 codified `docs/fanout_namespace_convention.md` (`_infra/fanout-namespace-convention`).
This milestone is the writer-boundary enforcement of that convention. Cycle 33 clone-2's
identifier for events emitted under this milestone is
`_infra/harness-clone-namespace-guard-clone-2` — the identifier IS itself an `_infra/*`
label emitted by a clone, so the `-clone-2` suffix per the c32 convention is REQUIRED
by the very convention this milestone enforces (meta-correct).
