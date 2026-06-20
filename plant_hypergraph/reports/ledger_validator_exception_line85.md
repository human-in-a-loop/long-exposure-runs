---
created: 2026-05-17T22:10:00Z
cycle: 5
run_id: run-phytograph-cycle6-ledger-exception-policy
agent: worker
milestone: _infra/promise-check-exception-policy
---

# Validator Exception Request: Ledger Line 85

## Exact Finding

`promise_check` reports:

```text
ledger:line 85: event_id is not a valid UUID
```

The row's `event_id` is:

```text
auditor-closure-m18-clone6
```

## Classification

This is a historical immutable data defect. The row violates the current ledger schema because `event_id` is required to be a UUID. It is not a biological-data defect and not a Barrier 1 substrate defect.

## Stable Fingerprint

The validator-consumed exception is recorded in `reports/promise_check_immutable_exceptions.json` and is keyed by the full fingerprint below:

| Field | Value |
|---|---|
| line | `85` |
| malformed event_id | `auditor-closure-m18-clone6` |
| timestamp | `2026-05-17T17:25:00+00:00` |
| milestone_id | `M1.8` |
| raw JSON-line SHA-256 | `0f3249698f13496ce2e094eaf8316b8937d042293b7bcf8a022d56bc7f407632` |
| validator error | `event_id is not a valid UUID` |

## Why It Cannot Be Repaired Append-Only

The ledger is append-only, and editing or deleting historical row 85 is forbidden. A superseding or corrective event can document the bad row, but the current validator still checks every historical row independently and will continue to emit a hard error for the original non-UUID value.

## Requested Validator Behavior

Implemented policy: `promise_check` consumes explicit immutable-history exceptions from `reports/promise_check_immutable_exceptions.json`. The exception must match exact line number, original event identifier, timestamp, milestone ID, raw-line hash, and error string. This makes the known historical defect nonblocking without relaxing validation for future malformed event IDs.
