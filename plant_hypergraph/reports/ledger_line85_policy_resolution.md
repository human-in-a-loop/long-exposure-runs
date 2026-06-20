---
created: 2026-05-17T22:40:00Z
cycle: 6
run_id: run-phytograph-cycle6-ledger-exception-policy
agent: worker
milestone: _manager/ledger-integrity-regression
---

# Line 85 Ledger Policy Resolution

## Defect

`promise_check` reported `ledger:line 85: event_id is not a valid UUID` for historical ledger row 85. The row is the M1.8 auditor closure event:

| Field | Value |
|---|---|
| line | `85` |
| event_id | `auditor-closure-m18-clone6` |
| ts | `2026-05-17T17:25:00+00:00` |
| milestone_id | `M1.8` |
| artifacts | `substrate/staging/fm_probe_harness/INGEST_AUDIT.md`; `substrate/staging/fm_probe_harness/cost_telemetry.jsonl`; `.long-exposure/fork-e34b5b2c1c6c/clone-6/merge_report.md` |

## Rewrite Policy

Historical ledger rewrite remains forbidden. Editing row 85 would hide the defect from the append-only record and make later audits unable to distinguish historical data repair from historical data mutation.

## Adopted Policy

The adopted policy is a validator-consumed immutable historical exception. `promise_check` reads `reports/promise_check_immutable_exceptions.json` and suppresses only an exact match on line number, malformed event ID, timestamp, milestone ID, raw JSON-line SHA-256, and validator error string. The line 85 raw-line SHA-256 is `0f3249698f13496ce2e094eaf8316b8937d042293b7bcf8a022d56bc7f407632`.

This policy preserves strict validation for new malformed rows: an unrelated bad `event_id` still fails. No timestamp-backdated lifecycle repair was added.

## Barrier State

With the exception consumed, the ledger-integrity regression blocker can close if the post-change `promise_check` exits 0. Barrier 1 substrate canonical-member repair remains pending for the next cycle and was not started here.
