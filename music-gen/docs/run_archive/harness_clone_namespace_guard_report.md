# _infra/harness-clone-namespace-guard — Cycle 33 clone-2 report

**Milestone:** `_infra/harness-clone-namespace-guard` (writer-boundary enforcement
of the cycle-32 fanout-namespace convention).
**Cycle:** 33 · **Fork:** 4595e91f7574 · **Clone:** 2 · **Agent:** worker.
**Rubric:** `docs/harness_clone_namespace_guard_rubric.md`
(SHA-256 `cd020761c919648e797769e3d05721b875be860cc845f16dbd9061ce92e876e3`,
echoed in `tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt`,
committed BEFORE writer edits landed).

## §1. Rubric SHA + verdict

**Verdict: `GUARD_LANDS`.**

All five GUARD_LANDS clauses of the frozen rubric are satisfied:

| # | Clause                                          | Status                            | Evidence                                   |
|---|-------------------------------------------------|-----------------------------------|--------------------------------------------|
| 1 | 468/468 baseline rows unchanged (both modes)    | PASS                              | test_01, test_25, §50c integration checks   |
| 2 | ≥10 test cases pass                             | PASS (14/14)                      | tests/test_harness_clone_namespace_guard.py |
| 3 | Zero caller changes outside `long_exposure/*`   | PASS                              | edits only under long_exposure/workspace_bootstrap.py + tests + docs |
| 4 | Strict-mode env-var toggle round-trip           | PASS                              | test_04, test_05, test_24                   |
| 5 | Public API of `append_ledger_event` unchanged   | PASS (`(workspace, event)`)       | test_13, §50e                               |

**Rubric SHA:** `cd020761c919648e797769e3d05721b875be860cc845f16dbd9061ce92e876e3`
(rubric doc SHA-256 == fixture SHA on every test run; asserted by test_11
and §50b).

## §2. Baseline-replay-green evidence

| Mode      | Rows read | Mutations | Rejects | Result |
|-----------|-----------|-----------|---------|--------|
| default   | 468       | 0         | 0       | PASS   |
| strict    | 468       | 0         | 0       | PASS   |

The 468-row `promise_ledger.jsonl` is the frozen cycle-32 baseline. Replay
uses `long_exposure.workspace_bootstrap._guard_clone_namespace(dict(row),
workspace)` from a root-context process (all clone env vars cleared). Under
BOTH default and strict modes zero rows are mutated and zero rows are
rejected — the guard is a no-op on root writes, and every clone-emitted row
in the historical ledger already carries its `-clone-<k>` suffix (per the
cycle-32 retroactive renames documented in
`docs/fanout_namespace_convention.md`).

Row-count invariant: pre-replay `wc -l promise_ledger.jsonl == 468`;
post-replay `== 468` (no file mutations — the replay path never opens the
ledger for write). Verified in the cycle-33 shadow ledger against
`data/ingestion/egress_status.jsonl` sibling proof-of-liveness.

## §3. Writer-boundary diff summary

Extended `long_exposure/workspace_bootstrap.py` (baseline: 681 lines;
post-edit: 865 lines; delta: **+184 lines** across module-level constants,
imports, `_is_clone_context`, `LedgerNamespaceViolation`,
`_guard_clone_namespace`, and one dispatch hook inside
`append_ledger_event`).

Signature of `append_ledger_event`:

```
def append_ledger_event(workspace: Path, event: dict) -> None:  # UNCHANGED
```

`inspect.signature(append_ledger_event)` returns exactly
`(workspace: 'Path', event: 'dict') -> 'None'` — asserted by `test_13`
(`test_harness_clone_namespace_guard.py`) and `§50e`
(`test_integration_cross_branch.py`).

New public class:
`long_exposure.workspace_bootstrap.LedgerNamespaceViolation` inherits
directly from `long_exposure.tools._ledger_schema.LedgerSchemaError` (see
§6). MRO chain: `LedgerNamespaceViolation → LedgerSchemaError →
ValueError → Exception → BaseException → object`. A caller that already
`except LedgerSchemaError:` transparently catches the new type — nothing
downstream needs an update.

New module-level constants:

- `_FANOUT_INFRA_PREFIXES = ("_infra/", "_run/", "_plan/", "_archive/", "_manager/")`
- `_CLONE_SUFFIX_RE = re.compile(r"-clone-\d+$")`

New helpers:

- `_is_clone_context(workspace: Path) -> tuple[bool, int | None]` — mirrors
  the c22 `long_exposure.fanout._is_clone` + `_get_clone_k` pattern. Reads
  `AGENT_FORK_ID` and `AGENT_FORK_CLONE_K` from process env; returns
  `(True, k)` when both are present and `k` parses as a non-negative int;
  else `(False, None)`. The `workspace` param is accepted for future-
  proofing (workspace-manifest override) but unused today. **Deliberately
  standalone** — the writer does not import from `long_exposure.exploration`
  or `long_exposure.fanout`, which keeps the writer's dependency footprint
  minimal and prevents circular import risk.
- `_guard_clone_namespace(event: dict, workspace: Path) -> dict` — the
  actual guard. Runs AFTER `validate_event` (so schema violations are
  caught first) and BEFORE the mutated `milestone_id` is used for
  duplicate-id + transition checks.

`append_ledger_event` dispatch hook (only new line inside the writer's
existing control flow):

```python
    errors = validate_event(event)
    if errors:
        raise LedgerAppendError(...)

    # Cycle-33 _infra/harness-clone-namespace-guard: c32 convention enforcement.
    event = _guard_clone_namespace(event, workspace)

    ledger = resolve_ledger_path(workspace)
```

No other line inside `append_ledger_event` changed. The duplicate-event_id
scan and per-milestone transition history both use `event["milestone_id"]`
AFTER the guard has run — so a silently-suffixed event's history is looked
up under its canonical (`-clone-<k>`-appended) identifier, not the bare
form.

## §4. Concat-boundary `_lint_clone_shadow` diff summary

Extended `_lint_clone_shadow(shadow_path)` with a symmetric per-row guard.
For each row that (a) has a `milestone_id` starting with one of
`_FANOUT_INFRA_PREFIXES`, (b) does not already end `-clone-<digit>+`, the
lint raises `LedgerNamespaceViolation` with a `<shadow_path>:<line_no>`
annotation.

Clone-`k` recovery precedence:

1. Parse from the shadow path itself — the last `clone-<N>` path segment
   (typical when a fan-out collector runs `_lint_clone_shadow` against a
   sibling clone's shadow at merge).
2. Fall back to `AGENT_FORK_CLONE_K` in the current process env.
3. If neither succeeds, the diagnostic renders `-clone-<k>` literal so
   the operator sees the shape.

Round-trip evidence:

- `test_10` (`test_harness_clone_namespace_guard.py`) — manufactured
  two-row shadow with `M-TEST-1/foo` + bare `_infra/violator` fails on
  line 2 with the correct annotation.
- `test_fanout_concat_validation.py §18` — the same violation surfaces at
  the concat boundary with a shadow-file-relative annotation
  (`fork/clone-2/promise_ledger.jsonl:2`).
- `test_fanout_concat_validation.py §19` — the negative control: a shadow
  with only `M-*` rows and properly suffixed `_infra/*` / `_run/*` rows
  lints cleanly. Confirms the guard is precise (no over-rejection).

The writer and the concat-lint share the same `_FANOUT_INFRA_PREFIXES`
tuple and `_CLONE_SUFFIX_RE` compiled regex — no drift risk between the
two enforcement surfaces.

## §5. 14-case test results table

Invocation: `PYTHONPATH=. /usr/bin/python3 tests/test_harness_clone_namespace_guard.py`

| # | Test                                                                            | Result |
|---|---------------------------------------------------------------------------------|--------|
| 01 | `test_01_baseline_468_rows_replay_green`                                        | PASS   |
| 02 | `test_02_infra_from_clone_autosuffixes`                                         | PASS   |
| 03 | `test_03_infra_from_root_stays_canonical`                                       | PASS   |
| 04 | `test_04_strict_mode_rejects_with_typed_error`                                  | PASS   |
| 05 | `test_05_strict_mode_disabled_autosuffixes`                                     | PASS   |
| 06 | `test_06_all_five_families_covered`                                             | PASS   |
| 07 | `test_07_M_star_never_touched`                                                  | PASS   |
| 08 | `test_08_unprefixed_never_touched`                                              | PASS   |
| 09 | `test_09_idempotent_on_already_suffixed`                                        | PASS   |
| 10 | `test_10_lint_clone_shadow_symmetric`                                           | PASS   |
| 11 | `test_11_rubric_sha_fixture_matches_doc`                                        | PASS   |
| 12 | `test_12_rubric_committed_before_writer_edits`                                  | PASS   |
| 13 | `test_13_public_api_unchanged`                                                  | PASS   |
| 14 | `test_14_MRO_LedgerNamespaceViolation_subclass_of_LedgerSchemaError`            | PASS   |

`result: PASS (14/14)`

Related suites:

- `tests/test_ledger_writer_validation.py` extended from 22 → 25 tests
  (new: `test_23`, `test_24`, `test_25`). All 25/25 pass; no regression on
  existing cases.
- `tests/test_fanout_concat_validation.py` extended from 17 → 19 tests
  (new: §18 + §19). All 19/19 pass.
- `tests/test_integration_cross_branch.py` §50 added (8 checks). All 8/8
  pass; the file's overall result is PASS with 0 failures.

## §6. MRO verification block

```
>>> import long_exposure.workspace_bootstrap as wb
>>> from long_exposure.tools._ledger_schema import LedgerSchemaError
>>> [c.__name__ for c in wb.LedgerNamespaceViolation.__mro__]
['LedgerNamespaceViolation', 'LedgerSchemaError', 'ValueError', 'Exception', 'BaseException', 'object']
>>> issubclass(wb.LedgerNamespaceViolation, LedgerSchemaError)
True
```

The subclass relationship is a real single-inheritance chain
(`LedgerSchemaError → ValueError` is inherited from `_ledger_schema`).
Not a runtime rebind, not a `__class__` reassignment — the class is
declared with `LedgerSchemaError` as its base at module load, using a
lazy import from `long_exposure.tools._ledger_schema` (which has no
back-dependency on `workspace_bootstrap`, verified by the c14
`test_13_no_import_cycles`).

`test_14` also asserts, empirically, that an exception raised from the
guard is caught by `except LedgerSchemaError:` — confirming call-site
transparency.

## §7. Strict-mode env-var toggle round-trip evidence

Manufactured event under clone-2 context (`AGENT_FORK_ID=test-fork-abcdef`,
`AGENT_FORK_CLONE_K=2`, `AGENT_INSTANCE_DIR=…`), `milestone_id=_infra/foo`:

| `MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE` | Behavior                                                     | Post-guard `milestone_id`     |
|------------------------------------------|--------------------------------------------------------------|-------------------------------|
| unset                                    | silent auto-suffix                                           | `_infra/foo-clone-2`          |
| `"0"`                                    | silent auto-suffix (same as unset)                           | `_infra/foo-clone-2`          |
| `"1"`                                    | raises `LedgerNamespaceViolation` (subclass of `LedgerSchemaError`) | n/a (write refused) |

Round-trip evidence:

- `test_24` (`test_ledger_writer_validation.py`) — full round-trip
  through the writer's public `append_ledger_event(...)` API: strict raise
  then default auto-suffix; ledger file contains the suffixed identifier
  in the second call; the first call's failed write never touches disk
  (atomicity preserved by the existing pre-write validation flow).
- `test_04` + `test_05` (`test_harness_clone_namespace_guard.py`) — pure
  guard-function toggle (no writer touched).

Baseline invariance: under BOTH modes the 468 pre-existing rows replay
unchanged (see §2 — `test_25` explicitly checks this through the writer's
public code path with `MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1` set).

## §8. Forward-look + Cycle-34 handoff

### Deferred hardening

- **`_manager/promise-check-parser-fragility`** — the c32 side-finding at
  `long_exposure/tools/promise_check.py:159-194` (substring match on
  `"milestone id"` silently hides matching plan-of-record rows) is
  unaddressed. `promise_check` lives under `~/human-in-a-loop/long_exposure/`
  and is upstream scope; this milestone waits on a cross-repo escalation.
  Workaround remains: descriptions avoid the literal `"milestone id"`
  substring in favor of `"identifier"` / `"row"` / `"label"`.

- **`_infra/harness-parser-fragility-workaround`** (candidate for a future
  cycle) — a defensive downstream shim that pre-processes plan-of-record
  input for `promise_check`, escaping the parser trigger substring or
  passing an explicit row list. Only worth landing if the upstream fix
  stays deferred past cycle 35.

### Anti-drift observations

- The writer's guard is silent by design (parity with c22
  `_infra/harness-auto-write-namespacing`). A future cycle that wants
  audit visibility on auto-suffixed writes could add a per-write log
  entry to a workspace-local `data/harness/namespace_guard_log.jsonl`
  without changing the writer's public API.

- Sun-of-fanout invariant: after a fanout collapse, every emitted
  `_infra/*` / `_run/*` / `_plan/*` / `_archive/*` / `_manager/*` row in
  the merged main ledger either (a) came from root and lacks the suffix,
  or (b) came from a clone and has the suffix. That's now enforceable
  from either boundary — the writer at emit time OR `_lint_clone_shadow`
  at merge time. Both share the same regex + prefix set.

### Cycle-34 handoff subsection

Nothing blocks cycle 34. This branch closes the c32 auditor-deferred
`_infra/harness-clone-namespace-guard` handoff cleanly with `GUARD_LANDS`.
The three-clone fanout of fork 4595e91f7574 has this as branch-C; the
merge conductor sees six named + two housekeeping events under
`-clone-2`-suffixed identifiers and no cross-clone collisions by
construction.

Suggested cycle-34 candidates (surfaced during this cycle):

- Palette-driven bare-render implementation consuming the cycle-31 Branch
  A determinism verdicts + Branch B schema (sfizz-first per c31 finding
  that Surge XT + Dexed remain STILL_GAP under DawDreamer 0.9.0).
- DawDreamer upgrade probe for Surge XT / Dexed determinism closure.
- Opportunistic egress retry via `workspace/harvest_playlists.sh`
  (media_ok=false as of cycle 33 top; HTTP 403 persists).
- If the c32 parser fragility is escalated upstream and lands, close
  `_manager/promise-check-parser-fragility` in the following cycle.

## Appendix — event trail (clone-2 shadow ledger)

Six named + two housekeeping events land in
`/home/user/music-gen-instance/fork-4595e91f7574/clone-2/promise_ledger.jsonl`,
all under `-clone-2`-suffixed identifiers per the cycle-32 convention:

1. `_run/cycle_33_launched-clone-2` (validated/high)
2. `_plan/register-harness-clone-namespace-guard-milestone-clone-2` (validated/high)
3. `_plan/harness_clone_namespace_guard_rubric_frozen-clone-2` (validated/high)
4. `_infra/harness-clone-namespace-guard-clone-2` (in-progress/medium → validated/high `GUARD_LANDS`)
5. `_infra/egress-probe-cycle-33-clone-2` (validated/high, media_ok=false)
6. `_run/cycle_33_closed-clone-2` (validated/high)
7. `_archive/cycle-33-scratch-clone-2` (validated/high — housekeeping)
8. `_infra/adopt-cycle33-tests-clone-2` (validated/high — housekeeping)

At merge time, c27 canonical-hash concat dedup handles collision-free
merge with clone-0 and clone-1 events; the `-clone-2` suffix guarantees
no cross-clone name collision by construction (the very invariant this
milestone codifies at the writer boundary going forward).
