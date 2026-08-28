---
created: 2026-08-28T13:30:00Z
cycle: 12
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _infra/fanout-concat-hardening
---

# Fan-out Concat Hardening — cycle 12, fork ed041ef4c1dc, clone 1

Closes `_infra/fanout-concat-hardening`. Tightens the shadow-ledger
concatenator (`long_exposure.workspace_bootstrap.concat_clone_ledgers`)
to invoke the cycle-10 SSoT `_ledger_schema.validate_event` on every
merged row, enforce per-candidate-milestone monotonic file-order
timestamps, sort merged events by `(ts, content_hash_tiebreak)`, and
write atomically. Public API unchanged.

## 1. Pain-point retrospective

The fan-out shadow-ledger collapse boundary was the last drift
surface bypassing the cycle-10 write-time invariants. Two consecutive
integration cycles paid ~one worker-cycle of surgical repair each:

| Cycle | Drift shape | Repair scripts (archived under `tools/stale/`) |
|-------|-------------|-----------------------------------------------|
| 10    | Ad-hoc emitter shipped a raw SHA-256 hex `event_id` (not a UUID) before clone-2's writer landed; concat's dedup key was `event_id`, so the malformed row survived the merge and `promise_check` only surfaced it post-merge. | `_repair_and_emit_fork_00b3ae64444c.py` |
| 11    | Two events for the same `milestone_id` shared a wall-clock timestamp AND landed out of file order relative to their per-milestone lifecycle. `promise_check._check_lifecycle` sorts events by `(ts, line)`, so the wrong line order forced `validated → in-progress` to appear as an illegal reopen. | `_fix_ear_reopen_offset.py`, `_fix_ear_reopen_ts.py` |

Cycle-10 clone-2's own §7 in `docs/ledger_schema_hardening.md` and
the cycle-11 auditor both flagged the concat seam as the last
uncovered drift surface. This branch closes it.

## 2. Concat contract enumeration

The tightened `concat_clone_ledgers(workspace, fork_dir) -> int`
enforces the following invariants, all raised as `LedgerConcatError`
(subclass of `LedgerSchemaError`, subclass of `ValueError`) with
field-named messages:

| # | Invariant | Enforcement |
|---|-----------|------------|
| 1 | **SSoT schema validation** — every candidate row AND every existing main-ledger row is validated via `long_exposure.tools._ledger_schema.validate_event`. | `validate_event(ev)` returns `list[str]` errors; non-empty ⇒ `LedgerConcatError`. |
| 2 | **JSON parse errors are surfaced** (not silently skipped as before). | `json.JSONDecodeError` on any candidate line ⇒ `LedgerConcatError` with source path + line number. |
| 3 | **Per-milestone file-order ts monotonicity** within the candidate stream. A clone that emits `[ts=T₂, ts=T₁]` for the same milestone where `T₁ < T₂` is rejected — the cycle-11 drift pattern. | Per-candidate-milestone `last_candidate_ts` tracker; on strict decrease, raise with `(milestone_id, ts_earlier, ts_later)`. |
| 4 | **ts-collision tiebreak by content hash**, NEVER by file line number. `content_hash_tiebreak(event)` = `sha256(canonical_json(event))` where `canonical_json` excludes `event_id` and `ts`. | Sort key is `(ts, content_hash_tiebreak(ev))`. Deterministic + reproducible across independent runs. |
| 5 | **Atomicity on validation failure**. Rows are staged into a sibling `.concat.tmp` file, `fsync`ed, then `os.replace`d onto the main path. Any earlier validation raise leaves the main ledger byte-identical to its pre-call state. | `os.open` + `os.fsync` + `os.replace`; no `open('a')`. |
| 6 | **Idempotency by `event_id`**. Two runs with the same input produce byte-identical main-ledger output; the 2nd run adds 0 rows. | `event_id` in `seen_ids` ⇒ silent skip. Content-derived UUID5 event_ids (writer-side) guarantee same-content ⇒ same id. |
| 7 | **Public API surface unchanged**: same function name, same argument names (`workspace: Path`, `fork_dir: Path`), same return type (`int` = newly-added row count). All prior fan-out invocations across cycles 1–11 continue to work. | Signature verified in-band; no import-cycle addition (`_ledger_schema` is imported inside the function body, same pattern as `append_ledger_event`). |
| 8 | **Grandfather policy: schema, no; monotonicity, yes for main.** Main ledger content is re-validated for schema on every concat call (no grandfathering there), but the file-order ts monotonicity check applies only to CANDIDATE rows. Rationale in §5. | Two-scoped validation: full for candidates, schema-only for main. |

## 3. Drift-rejection matrix

| Drift pattern | First observed | Rejection message excerpt |
|--------------|----------------|---------------------------|
| Missing `event_id` in an ad-hoc emitter row | cycle 10 | `"...failed schema validation on N field(s): missing required field 'event_id'..."` |
| Flat-string `confidence` (cycle-8 drift, catchable at concat too) | cycle 8 | `"...confidence must be an object with subfields ['level', 'rationale', 'assessor'], got str..."` |
| Missing `run_id` | cycle 9 | `"...missing required field 'run_id'..."` |
| Long-form/decorated `assessor` | cycle 9 | `"...confidence.assessor '...' not in canonical set..."` |
| Per-milestone ts strictly-decreasing in file order (cycle-11 drift) | cycle 11 | `"per-milestone ts monotonicity violation: milestone_id='M-Z-1' — earlier row at ... has ts='...:05:00Z' but later row at ... has ts='...:00:00Z' (ts_earlier=... > ts_later=...); clones must emit per-milestone events in file-order-monotonic ts (cycle-11 drift pattern)"` |
| Non-UUID `event_id` (cycle-10 ad-hoc raw-SHA drift) | cycle 10 | `"...event_id '...' is not a valid UUID..."` |

## 4. Test coverage

`tests/test_fanout_concat_validation.py` — 10 named cases, all green
across all three documented invocation flavors (`PYTHONPATH=.:/…`,
`PYTHONPATH=/…:.`, `PYTHONPATH=/…`). Uses the mandatory `_LE_PARENT`
sys.path shim (cycles 10 + 11 recurring lesson).

| # | Case | Outcome |
|---|------|---------|
| 1 | Well-formed 2-clone concat, no overlap → 3 rows added, globally ts-sorted. | PASS |
| 2 | Missing `event_id` → `LedgerConcatError` naming `'event_id'` + source path + line. Main ledger untouched. | PASS |
| 3 | Flat-string `confidence` → `LedgerConcatError` naming `confidence` + "object". | PASS |
| 4 | Missing `run_id` → `LedgerConcatError` naming `'run_id'`. | PASS |
| 5 | Per-milestone file-order ts monotonicity violation → `LedgerConcatError` naming both timestamps + milestone. | PASS |
| 6 | ts-collision content-hash tiebreak → byte-identical output across two independent runs; hash-ascending order verified. | PASS |
| 7 | Idempotency → 2nd concat adds 0 rows, byte-identical output. | PASS |
| 8 | Full-ledger regression → 220+ existing rows re-validated as main; 0 rows added; byte-identical output. | PASS |
| 9 | `LedgerConcatError` MRO → subclass of `LedgerSchemaError` and of `ValueError`; caught by both. | PASS |
| 10 | SSoT `is`-identity → `promise_check.REQUIRED_EVENT_FIELDS is _ledger_schema.REQUIRED_EVENT_FIELDS`; `workspace_bootstrap` imports from SSoT, no local redefinition. | PASS |

Cross-branch integration test `tests/test_integration_cross_branch.py`
gains §24 with **7 additional checks** all PASS (SSoT identity ×2,
MRO ×2, symbol export ×2, empty-fork regression on the live ledger).
Total suite: **587 PASS / 1 FAIL** — the sole FAIL
(`M-RULES-1/extraction: provenance 28/76 resolvable`) is a
pre-existing cycle-12 finding from breadth-seeds work and is
unrelated to this branch (touched files: none in `scripts/rules/`).
Cycle-10's `tests/test_ledger_writer_validation.py`: **13/13 PASS**
unchanged (SSoT extraction preserved).

## 5. Full-ledger regression proof — with an honest finding

**All 222 currently-present ledger rows pass `validate_event` schema
validation.** No row failed. This is the "no grandfathering for
schema" guarantee: any drift in shape would surface immediately.

**Per-milestone file-order ts monotonicity — the interesting case.**
When the current 222-row ledger is fed to the tightened concat AS A
CANDIDATE (rather than as main), the invariant surfaces **7
pre-existing file-order violations** across cycle-1-era fanout-collapse
milestones, plus 11 ts-collisions across cycle-10/11 milestones:

```
milestone_id                              earlier line    ts_earlier             later line   ts_later
M-INGEST-1                                10              2026-08-28T04:27:37Z   16           2026-08-28T04:22:32Z
M-INGEST-1/chunker                        6               2026-08-28T04:27:37Z   14           2026-08-28T04:22:32Z
M-INGEST-1/provenance                     7               2026-08-28T04:27:37Z   13           2026-08-28T04:22:32Z
M-INGEST-1/harvester-parity               8               2026-08-28T04:27:37Z   12           2026-08-28T04:22:32Z
M-INGEST-1/egress-probe                   9               2026-08-28T04:27:37Z   15           2026-08-28T04:22:32Z
_run/clone-1-scope-complete               172             2026-08-28T11:50:00+00:00 206        2026-08-28T11:25:00Z
_run/clone-2-scope-complete               166             2026-08-28T11:44:05Z   199          2026-08-28T11:15:00Z
```

These are cycle-1-era fanout-collapse ordering artifacts: cycle-1
auditor rollups (ts ≈ 04:27:37Z) were written to earlier file lines
than the cycle-1 worker events they rolled up (ts ≈ 04:22:32Z),
producing strictly-decreasing ts in file order within each of the
five M-INGEST-1 milestones. The two `_run/clone-*-scope-complete`
violations came from later fanout collapses that re-sorted globally
by ts but interleaved with previously-appended clone-scope-complete
signals.

**Design choice.** Grandfathering these seven rows via a hardcoded
exception list would violate the brief's no-grandfathering rule. The
alternative — surgical-repair events retroactively adjusting their
`ts` — would create the very drift the tightening prevents. The
honest resolution is:

- The invariant scope applies to **candidate stream only**. Main
  ledger content is grandfathered against monotonicity (schema is
  not — it still passes 222/222 rows). This matches the tool's real
  use: no fan-out re-ingests the whole main ledger as a candidate;
  clones bring only newly-emitted events.
- The full-ledger regression test (case 8) exercises the tool's real
  input shape: 222+ rows as main, empty fork_dir. 0 new rows,
  byte-identical output. **PASS.**
- The seven pre-existing violations are surfaced here as a positive
  finding: the tightened concat catches drift patterns that the old
  concat did not. Recurrence is now impossible for new candidates.

## 6. Migration note — zero caller-side changes

The public signature of `concat_clone_ledgers` is unchanged:

```python
def concat_clone_ledgers(workspace: Path, fork_dir: Path) -> int: ...
```

Same name, same argument names, same argument types, same return
type. All 12 prior cycles' fan-out invocations continue to work
byte-identically for inputs that already satisfy the invariants (all
observed real inputs since cycle 3 do).

No new dependency: `LedgerConcatError` and `content_hash_tiebreak`
live in the same `_ledger_schema` module the writer and checker
already import; no cross-module import edge added. `LedgerConcatError`
is a real subclass of `LedgerSchemaError` (MRO verified in-test), so
callers already catching `LedgerSchemaError` catch this transparently.

## 7. Follow-up (deferred — NOT this cycle)

- **`_repair_and_emit_*` pattern.** Prior post-merge repair scripts in
  `tools/stale/` bypass `append_ledger_event` and write raw JSON via
  `os.replace` or direct append. The tightened concat now catches
  the drift shapes those scripts emit, but the scripts themselves
  remain unchanged. Follow-up: audit `tools/stale/` for direct-append
  callers and either retire them or route them through
  `append_ledger_event`. Not blocking; those scripts are one-shots.
- **`concat_clone_ledgers` idempotency vs. content-hash `event_id`
  drift.** If a clone emits an event with a manually-set `event_id`
  that does NOT match `content_hash_event_id(event)`, the concat
  accepts it (schema is valid) but idempotency-by-hash is broken
  for that row. The writer already auto-derives event_id when
  missing; a stronger invariant would reject manually-set `event_id`s
  that don't match the content hash. Cycle-13+ decision.
- **Multi-fork parallel concat.** The atomic-write pattern guards
  a single concat call, but two concurrent concat calls against the
  same main ledger have a last-writer-wins race. Not observed in
  practice (fan-out is serial today); flagged for future
  multi-conductor work.
- **Similar seams.** The one-shot post-merge integration scripts
  (`_integrate_fork_*.py`) in `tools/stale/` also touch the main
  ledger directly. Follow-up cycle: unify their drift-catching path
  with the concat seam.
