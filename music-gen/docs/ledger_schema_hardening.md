---
created: 2026-08-28T12:00:00Z
cycle: 10
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _infra/ledger-schema-hardening
fork: 00b3ae64444c
clone: 2
---

# Ledger schema hardening (`_infra/ledger-schema-hardening`)

## 1. Root-cause narrative

Three consecutive post-merge integration cycles surfaced the same class of
defect: a fan-out clone emitted ledger events that were structurally invalid,
and the invalidity was only discovered *after* the shadow ledger had been
concatenated into `promise_ledger.jsonl` and `promise_check` was re-run at
the integration step. Each cycle spent ~30–60 worker-minutes writing a one-shot
repair script and re-appending fixed events, and each fix expanded the writer's
implicit schema without formalizing it.

| Cycle | Fork              | Drift pattern                                                               | Cost (repair, roughly) |
|-------|-------------------|------------------------------------------------------------------------------|------------------------|
| 7     | `3168fb0e47a1`    | Missing `event_id` on 3 clone-emitted events                                 | ~30 min                |
| 8     | `3a908edcb241`    | Flat-string `confidence` (e.g. `"confidence": "high"`) on 4 clone events    | ~45 min                |
| 9     | `f1bae241bde9`    | Missing `run_id` AND long-form `assessor` on 10 clone-0 events (lines 133–142) | ~60 min             |

The shared underlying cause was a **validation-timing bug**: the CLI
`ledger_append --event ...` path validated its input, but the Python-callable
`long_exposure.workspace_bootstrap.append_ledger_event(workspace, event)` —
which the great majority of emitters (fanout, manager, exploration,
`ledger_append`'s own module surface) actually use — had no validation at
all. It opened the file with `O_APPEND` and wrote whatever bytes it was
handed. Malformed emits therefore succeeded silently until `promise_check`
was next run, at which point a bare `ERROR: line N: missing required field
'run_id'` row appeared with no attribution to the emitter that produced it.

The fix moves validation *forward in time*, from post-merge check to
per-emit. A future malformed emit fails in its own process, in its own
stack, with a specific field-named `LedgerAppendError` message and the
offending event dict attached — the emitter can log the context, retry, or
crash loudly. The class of drift eliminated at write time cannot recur.

## 2. Required-field set (canonical)

Extracted to `long_exposure/tools/_ledger_schema.py`. `promise_check.py`
and `ledger_append.py` both import from this module; there is no other
place where the field set is enumerated.

| Field           | Type            | Purpose                                                                                             | Optional? |
|-----------------|-----------------|-----------------------------------------------------------------------------------------------------|-----------|
| `event_id`      | UUID string     | Unique per event; auto-generated as UUID5 of canonical content if not supplied.                     | required (auto) |
| `ts`            | ISO-8601 UTC    | Emission timestamp. Accepts trailing `Z` or `+00:00`; optional fractional seconds.                  | required  |
| `run_id`        | string          | `run-YYYY-MM-DDTHHMMSSZ`, `run-unknown`, or `fork-<hex>-clone-<n>`.                                 | required  |
| `cycle`         | positive int    | Cycle number (integer ≥1).                                                                          | required  |
| `agent`         | canonical token | One of `{worker, researcher, auditor, harness, human, manager, final_auditor}`.                     | required  |
| `milestone_id`  | canonical shape | `M-<TAG>[-<TAG>...]-<n>[/subpath]` or `_(run\|plan\|infra\|manager\|archive\|audit\|report\|handoff\|proto)/…`. | required |
| `status`        | canonical token | One of `{not-started, in-progress, validated, invalidated, reopened, deferred, action_required, superseded}`. | required |
| `confidence`    | nested object   | Must contain `level`, `rationale`, `assessor` (see below).                                          | required  |
| `narrative`     | non-empty str   | Human-readable description.                                                                         | required  |
| `artifacts`     | list[str]       | Files this event registers. Optional.                                                               | optional  |
| `supersedes`    | str \| list[str]| References to prior event_ids that this event replaces.                                             | optional  |
| `supersedes_path` | str            | Filesystem path that this event replaces (used by `_archive/*`).                                    | optional  |
| `reporter_mode` | str             | Reserved for the harness's report events (e.g. `cycles_1-3`).                                       | optional  |

**`confidence` sub-object:**

| Sub-field   | Type                | Purpose                                                                                        |
|-------------|---------------------|------------------------------------------------------------------------------------------------|
| `level`     | one of `{provisional, low, medium, high}` | Calibration.                                                            |
| `rationale` | non-empty string    | Why this level. Explanation for `invalidated` events must appear here.                         |
| `assessor`  | canonical token     | Same set as `agent` above. Long-form / decorated forms (e.g. `"user@example (worker, cycle 9, fork …, clone …)"`) are the cycle-9 drift pattern and are rejected; extended provenance may live in an optional `assessor_original` sibling field. |

The validator tolerates any additional keys not enumerated above (e.g.
future fields, per-event debug metadata). Extension-tolerance is
tested explicitly (case 8).

## 3. Backward-compatibility protocol

- **All 156 pre-existing events in `promise_ledger.jsonl` pass the tightened
  validator without modification.** This is asserted at import time by test
  case 9 (`test_all_existing_ledger_events_pass`) and again by §20 of
  `tests/test_integration_cross_branch.py`. No event was rewritten; no
  grandfather list was needed.
- **Extension fields observed in the live ledger are permitted**:
  `reporter_mode`, `supersedes`, `supersedes_path`, and the optional
  `assessor_original` sibling under `confidence` (added by the cycle-9
  repair script). Case 8 asserts round-trip preservation.
- **`ts` format tolerance**: both the canonical `Z`-suffixed form
  (`workspace_bootstrap._now_iso()` produces this) and the
  `datetime.isoformat()` default `+00:00` form are accepted. Both are
  present in the historical ledger.
- **`run_id` shape tolerance**: the canonical
  `run-YYYY-MM-DDTHHMMSSZ` form, the bootstrap `run-unknown` fallback,
  and per-clone `fork-<hex>-clone-<n>` shadow-ledger run_ids are all
  accepted.
- **`milestone_id` shape**: matches either the M-prefixed milestone syntax
  with any depth of subpath OR the reserved `_*/` prefixes.

## 4. Auto-generated `event_id`

When an event is appended without an `event_id` (or with `event_id` set to
`None` / empty string), the writer derives one deterministically:

```
event_id = UUID5(namespace=_EVENT_ID_NAMESPACE,
                 name=canonical_json(event_without_event_id_and_ts))
```

where `canonical_json` is `json.dumps(sorted_keys=True, separators=(",", ":"))`
of the event with `event_id` and `ts` stripped. The namespace UUID is
fixed at module load; changing it would prevent re-derivation of any
historical id.

**Why UUID5, not raw SHA-256 hex prefix?** `promise_check._check_uuid`
already requires event_ids to be *valid UUID strings*. A raw hex prefix
would break that invariant. UUID5 is deterministic-from-content AND
UUID-formatted, so both invariants hold simultaneously.

The `ts` field is excluded from the hash input because it is
runtime-generated: including it would make re-hashing an already-written
event unstable, and the same event emitted twice at different moments
would (correctly) collide-detect on `event_id` rather than accidentally
producing two distinct ids for the same logical content.

Case 2 (`test_auto_event_id_generated`) proves determinism: an event
appended without `event_id` receives an id that
`content_hash_event_id(original_event)` reproduces exactly.

## 5. Test coverage

`tests/test_ledger_writer_validation.py` — 13 named cases, all
green under `PYTHONPATH=. /usr/bin/python3 tests/test_ledger_writer_validation.py`:

| # | Case                                              | Defends                                                                    |
|---|---------------------------------------------------|----------------------------------------------------------------------------|
| 1 | `test_well_formed_event_accepted`                 | Happy-path round-trip: append → readback → same event                      |
| 2 | `test_auto_event_id_generated`                    | Auto-id is a valid UUID AND deterministic from content                     |
| 3 | `test_missing_run_id_rejected`                    | Cycle-9 drift pattern (missing `run_id`) rejected with `"run_id"` in msg   |
| 4 | `test_missing_ts_rejected`                        | Missing `ts` rejected with `"ts"` in msg                                   |
| 5 | `test_flat_string_confidence_rejected`            | Cycle-8 drift pattern (`confidence="high"`) rejected with `"confidence"` in msg |
| 6 | `test_confidence_missing_subfield_rejected`       | Nested confidence lacking `assessor` rejected with `"assessor"` in msg     |
| 7 | `test_long_form_assessor_rejected`                | Cycle-9 drift pattern (long-form assessor) rejected; `assessor_original` extension tolerated |
| 8 | `test_unknown_extension_field_tolerated`          | `reporter_mode` and `supersedes_path` extension fields pass through cleanly |
| 9 | `test_all_existing_ledger_events_pass`            | Regression harness: all 156 rows in `promise_ledger.jsonl` still validate  |
| 10| `test_duplicate_event_id_rejected_at_writer`      | Duplicate id caught at emit, not at post-merge check                       |
| 11| `test_write_atomicity_on_validation_failure`      | A failed append leaves the ledger byte-identical                           |
| 12| `test_ssot_constants_are_shared_object`           | `promise_check` and `ledger_append` share the same constants object as `_ledger_schema` |
| 13| `test_no_import_cycles`                           | AST scan proves `_ledger_schema` never imports the modules that import IT  |

Cases 3, 5, 7 are the three documented drift patterns from cycles 7/8/9;
each is rejected at emit with a specific field-named message.

Additionally, §20 of `tests/test_integration_cross_branch.py` re-asserts
the SSoT and no-import-cycles invariants at cross-branch integration
time, and re-verifies all 156 events pass.

Regression check on the rest of the worker-side suite (all green after
the change):

| Suite                                                | Result           |
|------------------------------------------------------|------------------|
| `tests/test_integration_cross_branch.py`             | PASS (0 failures, §1–§20) |
| `tests/test_rules_schema.py`                         | 25 pass / 0 fail |
| `tests/test_rules_extraction.py`                     | 34 pass / 0 fail |
| `tests/test_score_bridge.py`                         | 23 pass / 0 fail |
| `tests/test_egress_ready_state.py`                   | 0 failures       |
| `long_exposure.tools.promise_check .`                | exit 0, 0 ERRORs, WARNs unchanged for pre-existing rows |

## 6. Migration note — zero caller change

The writer's public signature is unchanged:

```python
append_ledger_event(workspace: Path, event: dict) -> None
```

Existing emitters — `long_exposure.exploration`, `long_exposure.manager`,
`long_exposure.fanout`, `long_exposure.tools.ledger_append.main`, plus
every worker-side helper in `tools/_emit_*.py` — continue to call it
exactly as before. The only observable change is that a call passing a
malformed event now raises `LedgerAppendError` instead of silently
writing an invalid row.

Callers wanting to opt into auto-generation of `event_id` simply omit the
field (or pass `None`); the writer fills in a content-derived UUID5.
Callers wanting duplicate-id detection get it for free — the writer now
scans the target ledger for an id collision before opening it for append.

## 7. Future infra work

- **Shadow-ledger validation at merge time.** The clone shadow ledgers
  concatenated by `fanout._concat_clone_ledgers` are not currently
  re-validated at merge time. In principle a corrupt shadow file could
  land bytes into the main ledger without going through the tightened
  writer path (e.g. someone `cat >> shadow.jsonl` from a shell). A
  merge-time re-validation is a natural follow-up; it would use exactly
  the same `_ledger_schema.validate_event` function.
- **Structural equivalence to `promise_check._check_event_schema`.** The
  writer's validator and the checker's lifecycle validator have been
  aligned at the required-field / shape level, but `promise_check` still
  carries deeper lifecycle checks (state-transition rules,
  supersede-target existence, dependency resolution) that intentionally
  do not fire at emit time. These belong at the checker layer and should
  stay there.
- **Fuzz surface**: the validator currently accepts a broad set of
  extension keys. If a future audit finds that extension keys are being
  used to smuggle in un-validated payloads, tightening `additionalProperties`
  (or emitting a WARN on unknown top-level keys) is the natural next
  step. Not done here on the zero-caller-change principle.
- **Contract test for the writer surface.** The current tests exercise
  `long_exposure.workspace_bootstrap.append_ledger_event` directly. A
  parallel contract test that goes through the CLI `python3 -m
  long_exposure.tools.ledger_append --event '{...}'` path would be
  cheap and would catch any regression in CLI-specific plumbing.

---

*Deliverable status:* `validated/high`. All eight sufficiency criteria
in the research brief are met. No falsifiability escape hatch was
invoked.
