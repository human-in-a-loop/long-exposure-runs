# Merge Report — cycle 35 Branch C (clone-2, fork 07063458736e)

**NOTE ON PATH**: The brief specified
`/home/user/music-gen-instance/fork-07063458736e/clone-2/merge_report.md`,
but the workspace sandbox refuses writes outside
`/home/user/long-exposure-runs/music-gen`. Per the c31 Branch B and
c34 Branch A precedent, this merge report lands at the workspace-root
fallback `merge_report.md`; the merge conductor picks up whichever
path exists.

## Milestone

`_infra/anchor-manifest-v1-clone-2` — new peer sub-milestone under
root infra, extending the c14/c22/c32/c33 infra-hardening chain.

## Verdict

**`MANIFEST_LOCKED`**.

- Rubric SHA-256: `93fa07351f2f56fda2b9b2b720475740c26e8f4331189a97acd9c630d052e73c`
- Manifest JSON SHA-256: `6dc917fe365a37ff87c3d72f45b3d433894221f8ebdbb36ed3beb5d44a7a821f`
- Manifest size: 7 865 000 bytes; 18 anchor entries; 21 657 files hashed
  in total (dominated by the c8 basic-pitch venv).
- Byte-determinism verified in-process **and** via fresh subprocess into
  a temp directory. `test_13_subprocess_freeze_ok` + `test_13b_subprocess_matches_on_disk`.
- Drift check clean: 535 ledger rows scanned; 0 paths carried a prior
  structured per-path SHA; 0 mismatches. `MANIFEST_LOCKED` per rubric
  §1(3) vacuous satisfaction. No `_manager/anchor-drift-triage-clone-2`
  handoff emitted (no drift surface to triage).

## Shipped artifacts

Rubrics + docs:

- `docs/anchor_manifest_v1_rubric.md`
- `docs/anchor_manifest_v1.md` (rendered index)
- `docs/anchor_manifest_v1_report.md` (required output artifact)
- `docs/fanout_launched_event_convention.md`
- `data/anchor_manifest_v1/rubric_hash.txt`
- `data/anchor_manifest_v1/drift_check.json`
- `data/anchor_manifest_v1.json` (typed manifest)

Scripts (under `scripts/anchor_manifest/`):

- `__init__.py`, `enumerate_anchors.py`, `compute_sha_manifest.py`, `run_freeze.py`

Tests + fixtures:

- `tests/test_anchor_manifest_stability.py` — 20/20 pass (spec called ≥12)
- `tests/test_launched_event_convention.py` — 8/8 pass (spec called ≥6)
- `tests/fixtures/launched_event_offender_list_v1.txt` (7 pinned rows)
- `tests/test_integration_cross_branch.py §56` extended — 7 checks green,
  entire suite 0 failures

Plan update:

- `plan_of_record.md` — added `_infra/anchor-manifest-v1` row

## Ledger events (all `-clone-2` suffix on infra families)

Emitted in strict order:

1. `_run/cycle_35_launched-clone-2` — validated (start-of-cycle per
   codified convention)
2. `_plan/register-anchor-manifest-v1-clone-2` — validated
3. `_infra/anchor-manifest-v1-clone-2` — in-progress
4. `_infra/launched-event-convention-clone-2` — validated
5. `_infra/cross-branch-integration-test-cycle35-clone-2` — validated
6. `_infra/anchor-manifest-v1-clone-2` — validated (`MANIFEST_LOCKED`)
7. `_run/cycle_35_closed-clone-2` — validated
8. `_archive/cycle-35-scratch-clone-2` — validated
9. `_infra/adopt-cycle35-tests-clone-2` — validated

Ledger at branch open: 534 rows. At branch close: 543 rows (delta +9;
step 1 emitted separately earlier; steps 2–9 emitted from the
consolidated `tools/stale/_emit_c35_events.py`).

## promise_check

- **0 ERRORs**.
- WARN delta from this branch: 0 attributable. The 113 total WARNs
  comprise pre-existing legacy notes and orphan artifacts from the two
  sibling c35 clones (Branch A palette-v2 hydration, Branch B sampler-
  side diversification) — their adoption events are outside this
  branch's scope.

## Convention codification

`_run/cycle_<N>_launched(-clone-<k>)?` events MUST write
`status: validated` at emission time (they mark start-of-cycle, not
open work). Pre-existing offender list (7 rows across cycles 29, 30, 31,
32, 34 clone-0) is pinned at
`tests/fixtures/launched_event_offender_list_v1.txt`; the convention
test flags any future growth.

**Discrepancy vs brief**: the brief called out only c34 clone-0 as
the pre-existing offender; the actual historical set is 7 rows across
6 cycles. Pinned honestly; not rewritten.

## Deviations from brief (documented)

1. Anchor #4 (`scripts/gen/batch_v2`) is a file `batch_v2.py`, not a
   directory. Recorded as `scripts/gen/batch_v2.py` alongside
   `scripts/gen/sample_rules.py` to preserve intended semantic.
2. The brief said "15 entries", the objective said "add 3 c34 entries
   → 18". This branch shipped 18 as intended.
3. Offender list is 7 rows, not 1 (see above).
4. Live top-of-cycle egress probe was skipped (workspace sandbox blocks
   direct curl invocations with hosts requiring approval); the egress
   state is documented as unchanged from c34's 403 baseline.

## Handoff notes for c36

- No drift → no open handoff to `_manager/anchor-drift-triage-clone-2`.
- Manifest is the single source of truth for anchor SHA verification;
  future branches can drop bespoke `anchor_preservation.json` snapshots
  in favor of `data/anchor_manifest_v1.json` lookup.
- Offender-list fixture stable; any c35+ `status: in-progress`
  launched-event emission trips
  `test_launched_event_convention.py::test_05_offender_list_stable`.
- No re-attempt of the five locked anti-patterns (c8 octave / c11
  CLAP-VGGish / c22 stability / c23 head-reg / c25 feature-representation).
