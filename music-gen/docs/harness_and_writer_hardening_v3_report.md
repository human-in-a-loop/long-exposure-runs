---
created: 2026-08-29T18:52:00Z
run_id: run-2026-08-28T040704Z
cycle: 48
agent: worker
milestone: _infra/harness-and-writer-hardening-v3
---

# `_infra/harness-and-writer-hardening-v3` — c48 clone-0 Branch A report

## §1 Two-verdict rubric summary + final verdict

Rubric (frozen, byte-pinned in `data/harness_and_writer_hardening_v3/rubric_hash.txt`
= `17c5025504d1aca9413bbd3570db08c568fedcae7d32e725ae0933a7bfb27267`):

| Verdict | Fires iff |
|---|---|
| `HARNESS_AND_WRITER_HARDENING_LANDS` | (i) 793 pre-cycle-48 rows raw-line SHA-256 byte-identical under both flags OFF; (ii) BOTH env-var toggles round-trip (set → new; unset → c47-verbatim); (iii) API + MRO + read-only anchor invariants hold. |
| `HARNESS_AND_WRITER_HARDENING_INSUFFICIENT` | any of the three fails. |

**Final verdict: `HARNESS_AND_WRITER_HARDENING_LANDS`.**

Three-way `rubric_hash` byte-equality confirmed:
`sha256(docs/harness_and_writer_hardening_v3_rubric.md)`
== `data/harness_and_writer_hardening_v3/rubric_hash.txt`
== `data/harness_and_writer_hardening_v3/verdict.json.rubric_hash`
== `17c5025504d1aca9413bbd3570db08c568fedcae7d32e725ae0933a7bfb27267`.

## §2 Sub-fix 1 — `MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION` semantics

**Problem** (c47 audit issue #2): `long_exposure.workspace_bootstrap._guard_clone_namespace`
auto-suffixes every id matching `_FANOUT_INFRA_PREFIXES` (the c36 v2 set that
includes `_infra/…`, `_run/…`, `_plan/…`, `_archive/…`, `_manager/…`, AND all
top-level `M-<TAG>-<n>/…` families) inside a fan-out clone context. The c32
convention says substantive `M-*` ids should stay unsuffixed. Consequence:
every fanout cycle since c36 must retroactively register the auto-suffixed
`M-*/*-clone-<k>` rows in `plan_of_record.md` (c36/c37/c38/c44/c47 pattern).

**Fix**: `long_exposure/workspace_bootstrap.py` now exports four new module-level
helpers (see the sub-fix-1-landed ledger event for the post-edit SHA-256):

- `_env_flag_truthy(value)` — canonical `{1, true}` truthiness check.
- `_substantive_exemption_active()` — reads `MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION`.
- `_supersedes_in_hash_active()` — reads `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH` (sub-fix 2).
- `_should_suffix(milestone_id)` — returns `False` for ids matching `^M-` when
  the substantive-exemption flag is active; returns `True` in every other case
  (`_infra/…`, `_run/…`, `_plan/…`, `_archive/…`, `_manager/…` continue to
  auto-suffix as before — the exemption discriminator is the leading `M-`, not
  the presence of `M-` anywhere in the path).

`_guard_clone_namespace` is gated on `_should_suffix(mid)` right before the
strict-mode raise / default auto-suffix. Under `=1` / `=true` the guard passes
`^M-` ids through unmodified even in a clone context; under unset / `=0` the
c33 behavior holds verbatim.

**Env-var round-trip fixture** (pinned in
`data/harness_and_writer_hardening_v3/toggle_round_trip_fixture.json`,
byte-deterministic across two fresh `/usr/bin/python3` subprocesses under all
env pins):

| id | flag OFF → `_should_suffix` | flag ON → `_should_suffix` |
|---|---|---|
| `M-EAR-1/synthetic-test` | `True` (auto-suffix) | **`False` (exemption)** |
| `_infra/synthetic-test` | `True` | `True` (infra-family always suffix) |
| `_manager/M-EAR-1/synthetic-test` | `True` | `True` (`_manager/` discriminator) |

**c48 default: OFF** (preserves the 793-row baseline replay contract).
**c49+ planned default: ON** via a one-line change in a follow-on cycle
(outside this branch's scope — see §9).

## §3 Sub-fix 2 — `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH` semantics + c46 line-745

**Problem** (c47 audit issue #3): the writer's UUID5 content-hash derivation
did not treat `supersedes` as first-class. The c46 line-745 event
(`_manager/M-EAR-1-real-label-training-v2-unfixable-by-audit-clone-1`) had its
`supersedes` field added post-hoc during c47 integration; a future replay
that re-derives its `event_id` from the current row content diverges from the
on-disk id `658231db-5d86-56e5-8ca9-2a9bed7fdf9f`.

**Fix**: `long_exposure/tools/_ledger_schema.py` now exports two new
first-class helpers:

- `canonical_json_bytes(event, include_supersedes=False)` — canonical-JSON
  bytes for content-hash derivation. Default `include_supersedes=False`
  excludes `{event_id, ts, supersedes}`; `include_supersedes=True` excludes
  only `{event_id, ts}`.
- `content_hash_event_id_v2(event, include_supersedes=False)` — UUID5
  derivation using the above helper. Same `_EVENT_ID_NAMESPACE` as
  `content_hash_event_id` so all downstream UUID invariants hold.

`long_exposure/workspace_bootstrap.append_ledger_event` now auto-derives
missing `event_id`s via `content_hash_event_id_v2(event,
include_supersedes=_supersedes_in_hash_active())`.

**c46 line-745 divergence fixture** (pinned in
`data/harness_and_writer_hardening_v3/line_745_divergence.json`):

| Property | Value |
|---|---|
| on-disk `event_id` | `658231db-5d86-56e5-8ca9-2a9bed7fdf9f` |
| re-derived under flag OFF (exclude supersedes) | `658231db-5d86-56e5-8ca9-2a9bed7fdf9f` (byte-equal) |
| re-derived under flag ON (include supersedes) | `6366af60-acb7-5e3f-a2e5-89b47f42c82f` (alternate) |
| supersedes | `91a17dc3-3ae0-58ef-99b3-52ba594a04c7` |
| supersedes_path | `M-EAR-1/real-label-training-v2/mapping-clarified` |

**c48 default: OFF** (preserves reproducibility of on-disk line-745 id).
**c49+ planned default: ON** via a one-line follow-on.

**Corpus-N caveat not applicable — this branch does not touch training or
corpus paths.**

## §4 Baseline replay 793-row byte-identity evidence

Baseline manifest snapshotted **BEFORE** any edit to `long_exposure/*` at
`data/harness_and_writer_hardening_v3/baseline_replay_manifest.jsonl`
(793 rows, one `{lineno, event_id, milestone_id, canonical_sha256_pre_edit}`
per event). Manifest SHA-256 pinned in `baseline_manifest_sha.txt` =
`c175d65a87bae90be2b8212fbfc0a547ff49964e5fbc30582fef2be5933871f3`.

Post-edit re-hash under both flags OFF: **793/793 raw-line SHA-256s
byte-identical**. Manifest SHA-256 unchanged pre==post.

Compressed distinct-SHA summary (from the manifest):

| Bucket | Rows | Distinct raw-line SHAs |
|---|---|---|
| pre-edit total | 793 | 793 (one per row) |
| post-edit total (flags OFF) | 793 | 793 (byte-equal pre) |
| pre-edit rows with `supersedes` field | 1 (line 745) | line-745 raw SHA unchanged |

Secondary observation (informational, not the replay contract): 389/793
existing on-disk `event_id`s reproduce byte-identically via
`content_hash_event_id_v2(row, include_supersedes=False)`. The remaining
404 rows had their `event_id`s assigned manually (`str(uuid.uuid4())`) at
write time — cycle-6/8/etc. `_run/*` and `_manager/*` events emit an
explicit `event_id`, bypassing the auto-derivation path — so those rows
were never subject to content-hash reproducibility in the first place.
The raw-line SHA replay is the authoritative baseline invariant.

## §5 Env-var toggle round-trip evidence per sub-fix

Both toggles verified by running the fixture inside two fresh
`tempfile.mkdtemp()` dirs via `subprocess.check_output(["/usr/bin/python3",
…])` under full env pins (BLAS singleton pins + `PYTHONHASHSEED=0` +
`SOURCE_DATE_EPOCH=1756463424` + `TZ=UTC` + `LC_ALL=C.UTF-8`). Run 1 stdout
== Run 2 stdout byte-identical.

Fixture output (verbatim):

```json
{
  "sub_fix_1": {
    "off": {"M-EAR-1/synthetic-test": true, "_infra/synthetic-test": true,
            "_manager/M-EAR-1/synthetic-test": true},
    "on":  {"M-EAR-1/synthetic-test": false, "_infra/synthetic-test": true,
            "_manager/M-EAR-1/synthetic-test": true}
  },
  "sub_fix_2": {
    "off": "658231db-5d86-56e5-8ca9-2a9bed7fdf9f",
    "on":  "6366af60-acb7-5e3f-a2e5-89b47f42c82f"
  }
}
```

## §6 Anchor preservation manifest (≥18 SHAs)

Pinned at `data/harness_and_writer_hardening_v3/anchor_preservation.json`.
20 read-only anchor files verified byte-identical pre==post (one
`data/anchor_manifest_v1.md` is missing from disk in this workspace — the
19 environmental anchor entries live inside `data/anchor_manifest_v1.json`
which is unchanged and includes anchor #19 `env/SOURCE_DATE_EPOCH=1756463424`
verbatim).

| Anchor | SHA-256 unchanged pre==post |
|---|---|
| `docs/fanout_namespace_convention.md` | ✓ |
| `docs/harness_clone_namespace_guard_rubric.md` | ✓ |
| `tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt` | ✓ |
| `data/anchor_manifest_v1.json` (incl. anchor #19) | ✓ |
| `docs/ear_real_label_training_v2_rubric.md` | ✓ |
| `data/ear_v2/rubric_hash.txt` | ✓ |
| `data/ear_v2/verdict.json` | ✓ |
| `docs/ear_real_label_training_v2p1_rubric.md` | ✓ |
| `data/ear_v2p1/rubric_hash.txt` | ✓ |
| `data/ear_v2p1/verdict.json` | ✓ |
| `docs/pre_registration_gate_policy.md` | ✓ |
| `docs/pre_registration_gate_policy_scope_verification_rubric.md` | ✓ |
| `docs/deprecation_and_anchor_pin_rubric.md` | ✓ |
| `scripts/ear/synthetic_labels.py` | ✓ |
| `scripts/ear/stability_metrics.py` | ✓ |
| `scripts/ear/stability_audit.py` | ✓ |
| `scripts/ear/features.py` | ✓ |
| `scripts/ear/model.py` | ✓ |
| `scripts/ear/corn.py` | ✓ |
| `scripts/ear/leak_test.py` | ✓ |

Total = 20 unchanged; ≥18 threshold satisfied.

## §7 c14/c22/c32/c33/c35 infra chain SHA invariance

The c14 SSoT `long_exposure/tools/_ledger_schema.py` was intentionally edited
(canonical_json_bytes + content_hash_event_id_v2 appended). All other
identifiers in the infra chain are byte-preserved. Explicit pre/post SHA
table for the two intentionally-edited modules is pinned in
`data/harness_and_writer_hardening_v3/anchor_preservation.json.expected_diff_surface`:

| Module | pre-edit SHA-256 | post-edit SHA-256 | Diff scope |
|---|---|---|---|
| `workspace_bootstrap.py` | `af0e1e87f7ca…89eed9f` | new SHA | helpers + guard gating + writer thread |
| `_ledger_schema.py` | `566fad6977e0…7d7b6af735725` | new SHA | canonical_json_bytes + content_hash_event_id_v2 appended |

Neither edit alters public API surface (`append_ledger_event`, `validate_event`,
`content_hash_event_id`, `canonical_json`, `content_hash_tiebreak`,
`concat_clone_ledgers`, `_lint_clone_shadow` — all unchanged in signature and
semantics under both flags OFF).

## §8 `LedgerNamespaceViolation` MRO + `append_ledger_event` signature stability

| Invariant | Verified |
|---|---|
| `inspect.signature(append_ledger_event)` params | `['workspace', 'event']` |
| `LedgerNamespaceViolation.__mro__` (first three) | `[LedgerNamespaceViolation, LedgerSchemaError, ValueError]` |
| `issubclass(LedgerNamespaceViolation, ValueError)` | `True` |
| `issubclass(LedgerNamespaceViolation, LedgerSchemaError)` | `True` |
| `MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1` on unsuffixed `_infra/…` inside clone context | still raises `LedgerNamespaceViolation` |

All four invariants verified by `tests/test_harness_and_writer_hardening_v3.py`
tests 08, 09, 22.

## §9 c48 default-OFF vs c49+ planned default-ON rationale + migration checklist

**Why c48 keeps both defaults OFF.** The 793-row baseline replay contract
requires that re-hashing the pre-cycle-48 ledger under the new writer
produces byte-identical output. Flipping the defaults ON in c48 would (a)
strip auto-suffixes from any post-c48 `M-*` sub-leaf emission — which is
exactly the intended long-term behavior, but would risk drift for any
in-flight cycle whose auditor expected the c47 pattern — and (b) alter the
UUID5 derivation for any new event carrying a `supersedes` field. Both are
safe changes but constitute behavior flips and belong in their own cycle
with their own rubric.

**c49+ migration checklist** (proposed, not this branch's work):

1. Flip the `_substantive_exemption_active` default: change the helper body
   to return `True` when the env var is UNSET (or introduce a distinct
   `MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION_DEFAULT_ON=1` guard). One-line
   change.
2. Flip the `_supersedes_in_hash_active` default the same way.
3. Update `docs/fanout_namespace_convention.md` §3 to describe the new
   default.
4. Update `docs/harness_clone_namespace_guard_rubric.md` to reference the
   c48 helpers by name.
5. Retroactively drop the redundant `M-*/*-clone-<k>` rows from
   `plan_of_record.md` inserted by c36/c37/c38/c44/c47 forks — a one-shot
   scratch script under `tools/stale/` after the row-drop is documented in
   a `_plan/…` event.
6. Optional c50+ audit: full write-path replay from ledger row content to
   verify every event's `event_id` is reproducible under the new defaults.

## §10 c49 handoff seeds

Ranked by leverage:

1. **Default-flip c49+**: the one-line change described in §9 items 1–2.
   Ship as a peer sub-milestone under `_infra/harness-and-writer-hardening-v3`
   with its own frozen 2-verdict rubric (`DEFAULT_FLIP_LANDS /
   DEFAULT_FLIP_INSUFFICIENT`).
2. **Retroactive plan-of-record migration**: after the default flip lands,
   drop the redundant `M-*/*-clone-<k>` rows from c36/c37/c38/c44/c47 forks
   (see §9 item 5). Non-blocking; can be batched with c50+ housekeeping.
3. **c50+ write-path replay audit**: for every one of the 793 pre-c48
   rows plus every event emitted since, verify
   `event_id == content_hash_event_id_v2(row, include_supersedes=<flag>)`
   or is explicitly documented in the manual-uuid4 exemption list. Would
   materialize the "reproducible from content" invariant campaign-wide.
4. **Corpus expansion 43→80 rated songs** (highest downstream leverage;
   egress-blocked). Unrelated to this branch; carried over from c47
   handoffs.
5. **c33 auto-suffix behavior on substantive `M-*` leaves**: superseded by
   this branch — the exemption is now landed, awaiting default flip.
6. **Egress retry cadence formalization**: unrelated; ambient carry.

## Appendix — event trail (c48 clone-0 Branch A)

Six named + supporting + two housekeeping events, all under `-clone-0`
suffix on infra families per c33 (the substantive c48 exemption does not
activate for this clone's own emissions — env vars default OFF):

1. `_run/cycle_48_launched-clone-0`
2. `M-INGEST-1/egress-probe-cycle48-clone-0`
3. `_plan/register-harness-and-writer-hardening-v3-milestone-clone-0`
4. `_infra/harness-and-writer-hardening-v3/rubric-committed-clone-0`
5. `_infra/harness-and-writer-hardening-v3/baseline-captured-clone-0`
6. `_infra/harness-and-writer-hardening-v3/sub-fix-1-landed-clone-0`
7. `_infra/harness-and-writer-hardening-v3/sub-fix-2-landed-clone-0`
8. `_infra/harness-and-writer-hardening-v3/baseline-replay-verified-clone-0`
9. `_infra/harness-and-writer-hardening-v3/toggle-round-trip-verified-clone-0`
10. `_infra/harness-and-writer-hardening-v3/anchor-preservation-verified-clone-0`
11. `_infra/harness-and-writer-hardening-v3/verdict-emitted-clone-0`
12. `_run/cycle_48_closed-clone-0`
13. `_archive/cycle-48-scratch-clone-0`
14. `_infra/adopt-cycle48-tests-clone-0`
