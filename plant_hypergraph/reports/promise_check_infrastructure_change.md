---
created: 2026-05-17T22:41:00Z
cycle: 6
run_id: run-phytograph-cycle6-ledger-exception-policy
agent: worker
milestone: _infra/promise-check-exception-policy
---

# Promise Check Infrastructure Change

## Prior Supersedes Patch

The previous reconciliation cycle exposed a validator crash on list-valued `supersedes`: `TypeError: unhashable type: 'list'`. `promise_check` now normalizes scalar `supersedes` to a one-element list and iterates list-valued references. This is schema-compatible with append-only correction events that supersede more than one earlier event.

This cycle tightened that behavior with schema validation: `supersedes` must be either a string or a list of strings. Invalid shapes are reported as schema errors, and cross-reference validation skips malformed `supersedes` values after the schema error instead of crashing or emitting misleading follow-on errors.

## Immutable Exception Patch

`promise_check` now computes a SHA-256 fingerprint for each raw JSONL row and reads workspace-local immutable-history exceptions from `reports/promise_check_immutable_exceptions.json`. An exception suppresses only the named error when all fingerprint fields match: line number, event ID string, timestamp, milestone ID, raw-line hash, and error string.

Before this patch, line 85 was an unrecoverable hard error under append-only ledger rules. After this patch, the known line 85 defect is consumed as an exact immutable exception, while unrelated malformed event IDs still fail.

## Infrastructure Namespace

The validator now treats `_infra/` as a reserved ledger namespace alongside `_plan/`, `_run/`, `_archive/`, `_orphan/`, and `_manager/`. This records validator and harness behavior changes without adding artificial campaign milestones to `plan_of_record.md`.

## Tests

Focused tests were added in `<long-exposure-repo>/tests/test_promise_check_exceptions.py` for exact exception matching, unrelated malformed ID failure, hash mismatch failure, and list-valued `supersedes` validation.
