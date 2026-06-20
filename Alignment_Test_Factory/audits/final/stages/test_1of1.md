# Final Audit Stage 3 - Test (1/1)

## Scope

This adversarial pass tested the closure verdict from Stage 2 against the required failure modes:

- silent supersessions or closure/supersession document drift
- orphan or missing plan milestones
- plan/ledger status inconsistencies
- supersession-pending states
- validator behavior via `promise_check` and `org_check`
- adjacent executable regression behavior for the prototype test stack

## Validator Results

### `promise_check`

Command:

```bash
python3 -m long_exposure.tools.promise_check <RUN_WORKSPACE>
```

Observed result: exit code 0.

Output summary:

- `events: 30, plan milestones: 8`
- warnings for orphan managed report artifacts under `reports/cycles/`
- warnings for ledger-tracked manager assessment artifacts under `<RUN_INSTANCE_DIR>/manager_assessments/...`

Adversarial follow-up found that the manager assessment files do exist on disk at the ledger paths:

- `<RUN_INSTANCE_DIR>/manager_assessments/manager_assessment_20260513T214826Z.md`
- `<RUN_INSTANCE_DIR>/manager_assessments/manager_assessment_20260513T224826Z.md`
- `<RUN_INSTANCE_DIR>/manager_assessments/manager_assessment_20260513T234827Z.md`

The warning text omits the leading dot and therefore reads as if ledger-tracked manager assessment artifacts are absent when the ledger paths are present. This is a validator bookkeeping/message issue, not evidence that M-1 through M-8 are unsupported.

### `org_check`

Command:

```bash
python3 -m long_exposure.tools.org_check <RUN_WORKSPACE>
```

Observed result: exit code 0.

Output summary:

- root files: 5
- root dirs: 10
- standard folders present: `audits`, `data`, `docs`, `reports`, `scripts`, `stale`, `tests`, `tools`
- `OK: org_check green.`

## Adversarial Consistency Checks

### Closure and supersession scan

Command scanned the workspace for filenames containing `CLOSURE` or `SUPERSEDES`.

Observed result: no matching files. No closure document mtime drift or silent supersession document was found.

### Plan/ledger consistency

The adversarial parser normalized structured status/confidence fields and checked all ledger events.

Observed result:

- total events: 30
- plan milestones: `M-1` through `M-8`
- ledger milestone set: `M-1` through `M-8`
- missing plan milestones in ledger: none
- extra deliverable milestones in ledger: none
- invalid status values: none
- invalid confidence values: none
- terminal plan milestones: `M-1` through `M-8`
- non-terminal plan milestones: none
- latest non-plan statuses:
  - `_run/start`: `in-progress` / `high`
  - `_plan/initial-campaign-milestones`: `validated` / `medium`
  - `_plan/domain-folder-convention`: `validated` / `medium`
  - `_manager/validator-warnings`: `in-progress` / `medium`
- latest superseded milestones: none
- supersession mentions: none
- missing ledger artifact paths under exact ledger spelling: none

Conclusion: no silent supersession, orphan deliverable milestone, status taxonomy violation, confidence taxonomy violation, or plan/ledger mismatch was found.

## Adjacent Regression Check

An optional full prototype test stack was run to check whether the runnable evidence still behaves as reported.

First attempt:

```bash
<RUN_WORKSPACE>/.alignment-eval-venv/bin/python -m pytest tests/test_task_spec_schema.py tests/test_toy_environment.py tests/test_inspect_smoke.py tests/test_task_families.py tests/test_multi_family_inspect.py tests/test_benchmark_stress.py
```

Observed result: 29 passed, 2 failed. Both failures were environment invocation failures: the venv Python was used directly without putting the venv `bin` directory on `PATH`, and the runner code locates the `inspect` executable with `shutil.which("inspect")`.

Second attempt, using the documented reproduction path:

```bash
source <RUN_WORKSPACE>/.alignment-eval-venv/bin/activate && python -m pytest tests/test_task_spec_schema.py tests/test_toy_environment.py tests/test_inspect_smoke.py tests/test_task_families.py tests/test_multi_family_inspect.py tests/test_benchmark_stress.py
```

Observed result: 31 passed in 11.75s.

Conclusion: the prototype regression stack passes when invoked with the documented environment activation. The first failure is not a milestone defect; it confirms that the Inspect runners depend on `inspect` being discoverable on `PATH`, as the run documentation states.

## Findings Appended

One structured finding was appended to `audits/final/findings.jsonl`:

- MODERATE: `_manager/validator-warnings` remains a bookkeeping residual because `promise_check` emits warnings that can mislead a reader about manager assessment artifact presence by reporting paths without the ledger's leading dot.

No CRITICAL findings were found.

## Remaining Issues for Document Stage

- `_manager/validator-warnings` remains `in-progress` / `medium` and should be listed as residual bookkeeping debt.
- `promise_check` exits 0, so `promise_check_status` should be `green` in the final summary, with the warning caveat documented.
- `org_check` is green.
- `_run/start` remains `in-progress` / `high`; this is run bookkeeping rather than an unvalidated deliverable milestone.
- No plan milestone remains non-terminal.

## Gate Check

- Required validators run: yes, both `promise_check` and `org_check` were run and observed.
- Adversarial checks performed: yes, closure/supersession scan, plan/ledger consistency, status/confidence validation, missing artifact validation, and adjacent regression tests were performed.
- New issues introduced: none. The optional first pytest invocation failed due to environment activation, and the documented invocation passed.
- Expected file exists: yes, this file is the required Stage 3 output path.
