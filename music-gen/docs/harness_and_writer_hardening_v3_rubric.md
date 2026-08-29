---
created: 2026-08-29T18:30:00Z
run_id: run-2026-08-28T040704Z
cycle: 48
agent: worker
milestone: _infra/harness-and-writer-hardening-v3
---

# `_infra/harness-and-writer-hardening-v3` — frozen 2-verdict adjudication rubric

Rubric-first, committed BEFORE any Python edit under `long_exposure/*`
(mtime gate hard; git-log gate advisory per c46 path (ii) amendment —
this session's harness cannot commit in-turn, so the git-log check is
soft and records `HARNESS_GATED` when it does not fire).

Two-verdict rubric with no third state (per c47 fanout convention):

| Verdict | Fires iff |
|---|---|
| `HARNESS_AND_WRITER_HARDENING_LANDS` | (i) baseline replay of the 793 pre-cycle-48 ledger rows byte-identical under both flags OFF; (ii) BOTH env-var toggles round-trip (set → new behavior; unset → c47-verbatim behavior); (iii) all invariants below unchanged. |
| `HARNESS_AND_WRITER_HARDENING_INSUFFICIENT` | any of (i), (ii), (iii) fails. |

## Sub-fix 1 — c33 auto-suffix substantive exemption

**Env var**: `MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION`

| Value | Semantics |
|---|---|
| unset / `0` / any string other than the truthy values | INACTIVE — c33 behavior verbatim: every `_infra/*`, `_run/*`, `_plan/*`, `_archive/*`, `_manager/*`, and top-level `M-*/*` id emitted inside a fan-out clone context is auto-suffixed `-clone-<k>`. |
| `1` or `true` (case-insensitive) | ACTIVE — substantive-milestone exemption: ids matching `^M-` are NOT auto-suffixed even inside a clone context. Ids matching `^(_infra|_run|_plan|_archive|_manager)/` continue to auto-suffix as before. `_manager/M-...` continues to auto-suffix (`_manager/` prefix is the discriminator — not `M-`). |

Default for c48: **OFF** (preserves the 793-row baseline replay contract).
Default for c49+: planned **ON** via a one-line change in a follow-on
cycle. This branch does NOT flip the default.

## Sub-fix 2 — `supersedes` field in content-hash

**Env var**: `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH`

| Value | Semantics |
|---|---|
| unset / `0` / any string other than the truthy values | INACTIVE — the writer's canonical-JSON path used to derive UUID5 `event_id` EXCLUDES the `supersedes` field. This reproduces the on-disk c46 line-745 `event_id` `658231db-5d86-56e5-8ca9-2a9bed7fdf9f`, which was originally computed before `supersedes` was added post-hoc during c47 integration. |
| `1` or `true` (case-insensitive) | ACTIVE — canonical-JSON path INCLUDES `supersedes`. For the c46 line-745 event this re-derives the alternate UUID5 `6366af60-acb7-5e3f-a2e5-89b47f42c82f`, which differs from the on-disk id and proves the toggle is doing something material. |

Default for c48: **OFF** (preserves reproducibility of the on-disk
line-745 `event_id`). Default for c49+: planned **ON** via a one-line
change in a follow-on cycle. This branch does NOT flip the default.

## Falsifiable c46 line-745 divergence marker

| Property | Value |
|---|---|
| on-disk `event_id` | `658231db-5d86-56e5-8ca9-2a9bed7fdf9f` |
| re-derived `event_id` under `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH=0` | `658231db-5d86-56e5-8ca9-2a9bed7fdf9f` (byte-equal) |
| re-derived `event_id` under `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH=1` | `6366af60-acb7-5e3f-a2e5-89b47f42c82f` (differs) |

The pair (on-disk, alternate) is pinned into
`tests/test_harness_and_writer_hardening_v3.py::test_07_line_745_divergence`
and into `verdict.json.c46_line_745_alternate_event_id_under_flag`
as the material behavior-change evidence.

## Invariants (must all remain byte-equal pre==post)

| Anchor | Path |
|---|---|
| c14 SSoT schema | `long_exposure/tools/_ledger_schema.py` (WILL be edited; assert only the expected canonical-JSON+validator diff surface) |
| c22 harness auto-namespacing | `long_exposure/exploration.py` |
| c32 convention doc | `docs/fanout_namespace_convention.md` |
| c33 guard rubric | `docs/harness_clone_namespace_guard_rubric.md`, `tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt` |
| c35 anchor manifest | `data/anchor_manifest_v1.json`, `docs/anchor_manifest_v1.md` |
| c45 v2 rubric + artifacts | `docs/ear_real_label_training_v2_rubric.md`, `data/ear_v2/rubric_hash.txt`, `data/ear_v2/verdict.json` |
| c47 v2.1 rubric + artifacts | `docs/ear_real_label_training_v2p1_rubric.md`, `data/ear_v2p1/rubric_hash.txt`, `data/ear_v2p1/verdict.json` |
| c47 policy doc | `docs/pre_registration_gate_policy.md`, `docs/pre_registration_gate_policy_scope_verification_rubric.md`, `docs/deprecation_and_anchor_pin_rubric.md` |
| c47 anchor manifest #19 | `SOURCE_DATE_EPOCH=1756463424` entry in `data/anchor_manifest_v1.json` |
| c22 stability harness | `scripts/ear/synthetic_labels.py`, `scripts/ear/stability_metrics.py`, `scripts/ear/stability_audit.py` |
| c6 chassis | `scripts/ear/features.py`, `scripts/ear/model.py`, `scripts/ear/corn.py`, `scripts/ear/leak_test.py` |

Additional API invariants:

- `long_exposure.workspace_bootstrap.append_ledger_event.__signature__ == (workspace, event)` unchanged.
- `LedgerNamespaceViolation` MRO chain unchanged (subclass of `LedgerSchemaError` which is subclass of `ValueError`).
- `MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1` toggle interaction preserved.

## Baseline replay contract

Byte-identity of the 793 pre-cycle-48 ledger rows is measured as
`sha256(raw_line_bytes)` per row against
`data/harness_and_writer_hardening_v3/baseline_replay_manifest.jsonl`.
The manifest itself is fingerprinted into
`data/harness_and_writer_hardening_v3/baseline_manifest_sha.txt`.
Under both env-var flags OFF the writer never touches
`promise_ledger.jsonl` for its own emissions in a way that mutates
prior rows, and re-derivation from row content for line 745 reproduces
`658231db-5d86-56e5-8ca9-2a9bed7fdf9f` byte-identically.

## Env pins (determinism-gated verification)

- BLAS: `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`
- `PYTHONHASHSEED=0`
- `SOURCE_DATE_EPOCH=1756463424` (c47 anchor #19)
- `TZ=UTC`
- `LC_ALL=C.UTF-8`

## Discipline (binding for this branch)

- Rubric doc mtime < any file mutated under `long_exposure/*`.
- No PRNG introduced; `uuid.uuid5`/`uuid.uuid4` counts unchanged in the diff.
- No `sidecar_nonfactor` import introduced.
- No writes to Branch B (`_manager/corpus-expansion-plan`) or Branch C
  (`_infra/pre-existing-test-drift-triage`) paths.
- Corpus-N caveat N/A — this branch does not touch training or corpus paths.
- Foreground execution only (c41 interdiction).
- Substantive c48 fix does NOT activate for this clone's own emissions;
  env vars default OFF preserves the 793-row baseline replay contract.
