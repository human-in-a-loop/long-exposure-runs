---
created: 2026-05-11T19:40:00Z
cycle: 15
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-EXP-1
deferred_constant: DC-005
artifact_type: merge_verification
---

# DC-005 Merge Verification

## Purpose

This note defines the conductor-facing verification path for the validated `DC-005` trajectory-reuse branch. It does not reinterpret the trajectory-reuse design or change any `TRJ-*` measurement rows. Its job is to distinguish expected pre-merge fanout ledger isolation from real merge defects such as missing CSVs, lost trajectory experiment rows, missing collapse thresholds, missing production security fields, or accidental absorption of `DC-006` provenance-overhead measurement into `DC-005`.

## Verification Command

Run from the workspace root:

```bash
python3 tests/verify_dc005_merge_ready.py
```

The script reads:

- `data/measurement_experiment_specs.csv`
- `data/measurement_required_fields.csv`
- `data/measurement_thresholds.csv`
- `data/measurement_claim_update_matrix.csv`
- `data/measurement_synthetic_probe_results.csv`

It writes `data/dc005_merge_verification_results.csv` with one row per check. A nonzero exit means the conductor should reopen the merge package or the `DC-005` integration rows, depending on the named failure.

## Checks

The verifier fails if any required CSV is missing, headerless, or empty. It also asserts that `TRJ-001` through `TRJ-007` are present, that `C_to_B_trajectory_reuse`, `C_to_A_trajectory_reuse`, `p_survive_min`, and `p_verifier_reuse_min` remain in the thresholds table, and that `trajectory_node_id`, `replay_authorization_scope`, `verifier_evidence_hash`, and `retention_hold_state` remain represented in the required-fields table.

The scope-boundary check is intentionally narrow: `DC-006` may be mentioned in explanatory notes as the owner of provenance-validation overhead magnitude, and sibling deferred constants may share the parent harness CSVs. The merge verifier rejects `DC-006` only if it reuses `DC-005` trajectory experiment IDs or collapse threshold IDs. Authorization and provenance fields are accepted here only as replay-validity gates for `DC-005`, not as measured overhead constants.

## Ledger and Organization Commands

The conductor can also run:

```bash
python3 -m long_exposure.tools.org_check <workspace>
python3 -m long_exposure.tools.promise_check <workspace>
```

Before conductor reconciliation, root `promise_check` may report the five DC-005 CSVs or this verification package as orphan artifacts because fanout clones write ledger events to clone shadow ledgers. That warning is tolerated only when `python3 tests/verify_dc005_merge_ready.py` passes. After merge, continuing orphan warnings require conductor investigation, not a change to the validated trajectory-reuse semantics.

## Reopen Conditions

Reopen `DC-005` only if merge verification reports a missing artifact, missing `TRJ-*` row, missing threshold, missing required trajectory/security field, empty CSV, corrupt CSV, or `DC-006` row that reuses a `DC-005` trajectory experiment ID or collapse threshold ID. Do not reopen `DC-005` for the known pre-merge fanout ledger warning alone.
