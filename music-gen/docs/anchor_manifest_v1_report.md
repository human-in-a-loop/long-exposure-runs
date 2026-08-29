# `_infra/anchor-manifest-v1-clone-2` — Cycle 35 Branch C report

**Milestone:** `_infra/anchor-manifest-v1-clone-2`
**Cycle:** 35 (fork 07063458736e, clone-2)
**Agent:** worker
**Run id:** `run-2026-08-28T040704Z`
**Date:** 2026-08-29
**Rubric:** `docs/anchor_manifest_v1_rubric.md`
**Rubric SHA-256:** `93fa07351f2f56fda2b9b2b720475740c26e8f4331189a97acd9c630d052e73c`
**Verdict:** **`MANIFEST_LOCKED`**

## §1. Scope and construction

This branch enumerates every locked-anchor set the campaign has
accumulated through cycle 34 (18 entries), computes SHA-256 per file
and a sorted-relpath concat manifest SHA per directory, and freezes
the result to `data/anchor_manifest_v1.json` (rendered index at
`docs/anchor_manifest_v1.md`). It also codifies the
`_run/cycle_<N>_launched(-clone-<k>)?` writing convention in
`docs/fanout_launched_event_convention.md`. Six named ledger events
plus two housekeeping events are emitted under the `-clone-2` suffix
per the c32 fanout-namespace convention (writer-enforced by c33's
`_infra/harness-clone-namespace-guard`). This is infra codification,
not exploration; the closing verdict is `MANIFEST_LOCKED` as expected.

## §2. Anchor enumeration (18 entries)

The canonical list (defined in `scripts/anchor_manifest/enumerate_anchors.py`):

| # | anchor_id | cycle | kind | # paths | # files | notes |
|---|-----------|-------|------|---------|---------|-------|
| 1 | `c06_feature_cache` | 6 | feature_cache | 1 | 90 | data/ear/features |
| 2 | `c08_basic_pitch_venv` | 8 | venv | 1 | 21260 | quarantined venv |
| 3 | `c09_pinned_dawdreamer_chain` | 9 | dawdreamer_chain | 1 | 1 | render_effects_layered.py |
| 4 | `c13_batch_v2_pipeline` | 13 | batch_pipeline | 2 | 2 | batch_v2.py + sample_rules.py |
| 5 | `c15_i4_stratified` | 15 | sampling_utility | 1 | 1 | i4_stratified.py |
| 6 | `c22_stability_harness` | 22 | stability_harness | 3 | 3 | 3-file harness |
| 7 | `c22_antipattern_flag` | 22 | anti_pattern_flag | 1 | 1 | audit report |
| 8 | `c23_antipattern_flag` | 23 | anti_pattern_flag | 1 | 1 | audit report |
| 9 | `c25_antipattern_flag` | 25 | anti_pattern_flag | 1 | 1 | audit report |
| 10 | `c26_c27_c28_c29_c30_analytical` | 30 | analytical_utility | 1 | 29 | scripts/analysis/* |
| 11 | `c31_palette_v1` | 31 | schema | 4 | 47 | palette schema + docs + data |
| 12 | `c31_palette_probe` | 31 | probe | 4 | 28 | instrument determinism |
| 13 | `c33_palette_render` | 33 | palette_render | 4 | 25 | palette-driven bare render |
| 14 | `c33_dawdreamer_state` | 33 | workaround | 4 | 23 | P1 iterate_parameters |
| 15 | `c33_harness_clone_namespace_guard` | 33 | guard | 3 | 3 | long_exposure/* (exempt) |
| 16 | `c34_palette_v2` | 34 | schema | 4 | 40 | v2_iterated_params discriminator |
| 17 | `c34_palette_render_cross_seed` | 34 | cross_seed | 4 | 40 | 3-seed generalization |
| 18 | `c34_gen_palette_batch_v1` | 34 | batch | 4 | 62 | palette-driven batch (BATCH_SPREAD_COLLAPSED) |

**Discrepancy vs brief:** the brief said "15 entries" and separately
enumerated the c34 additions (16-18); the actual count here is 18,
matching the brief's expanded numbering.

**Path adjustment vs brief:** the brief listed
`scripts/gen/batch_v2/*` for anchor 4, but the on-disk artifact is a
single file `scripts/gen/batch_v2.py` (per `ls scripts/gen/`). The
anchor was recorded as `scripts/gen/batch_v2.py` alongside
`scripts/gen/sample_rules.py` to preserve the intended semantic (the
c13 batch-v2 render pipeline + its sampler) without inventing a
missing directory.

## §3. SHA freeze summary

- **Frozen JSON:** `data/anchor_manifest_v1.json` — 7 865 000 bytes.
- **Frozen JSON SHA-256:** `6dc917fe365a37ff87c3d72f45b3d433894221f8ebdbb36ed3beb5d44a7a821f`
- **Byte-determinism × 2 (fresh temp file):** confirmed equal.
- **Total files hashed:** 21 657 (dominated by the c8 basic-pitch venv).
- **Directory-manifest SHAs:** computed per directory anchor (excluding
  `__pycache__/` and `*.pyc`; symlinks not followed).

Serialization contract: `json.dumps(..., sort_keys=True,
separators=(",", ":"), ensure_ascii=False).encode("utf-8")` — no
trailing newline.

## §4. Drift cross-check (§8 of the brief)

The drift check scans every row of `promise_ledger.jsonl` (535 rows at
this branch's start) for structured `{path, sha256}` records under
each event's `artifacts` field, and cross-checks any prior SHA against
the freshly frozen current SHA for the same path.

**Result (verbatim from `data/anchor_manifest_v1/drift_check.json`):**

```
{
  "scanned_rows": 535,
  "paths_with_prior_sha": 0,
  "matched_prior_shas": 0,
  "drift_count": 0,
  "drift": []
}
```

No prior structured per-path SHAs exist in the ledger for any of the
18 anchor paths. The ledger's per-event `artifacts` field is
predominantly a list of strings or dicts without a `sha256` key; per-
file SHAs live in free-text narratives (e.g. `"SF2 sha
74594e8f…1cb0"`) that reference secondary content (soundfonts, WAVs)
rather than the enumerated code/doc anchors above. Because the
manifest is the first structured SHA baseline for these anchor
identities, drift cannot be established against nothing, and the
verdict resolves to `MANIFEST_LOCKED` per the rubric §1(3) contract
(the condition failure is "prior recorded SHA that does not match" —
absent priors, the condition is vacuously satisfied). Future cycles
compare against `data/anchor_manifest_v1.json` directly, which is the
whole point of this branch.

## §5. Launched-event convention

`docs/fanout_launched_event_convention.md` codifies the rule literal:

> A `_run/cycle_<N>_launched(-clone-<k>)?` ledger event MUST be emitted
> with `status: "validated"` at emission time.

The pinned pre-existing offender list at
`tests/fixtures/launched_event_offender_list_v1.txt` contains **seven**
rows (six unique cycles):

- `_run/cycle_29_launched`
- `_run/cycle_30_launched`
- `_run/cycle_31_launched`
- `_run/cycle_31_launched-clone-1`
- `_run/cycle_31_launched-clone-2`
- `_run/cycle_32_launched`
- `_run/cycle_34_launched-clone-0`

**Discrepancy vs brief:** the brief cited only the c34 clone-0
asymmetry as the sole pre-existing offender; the actual historical
set is broader. The offender-list fixture pins the current set so
that `tests/test_launched_event_convention.py` catches any future
`status: in-progress` c35+ emission as a growth of the list — rather
than treating the observed history as an invariant. The historic
offender rows are documented, not rewritten (append-only preservation
takes precedence over schema uniformity for pre-c35 rows).

The c35 clone-2 launched event this branch emitted (`_run/cycle_35_launched-clone-2`)
carries `status: validated` per the codified convention.

## §6. Tests shipped

- `tests/test_anchor_manifest_stability.py` — 15 named cases:
  rubric-hash trail (2), manifest presence + anchor count (2),
  byte-determinism in-process (2), schema-keys (2), is_readonly-all
  (1), sha_per_path-nonempty (1), dir_manifest_sha coverage (1),
  no-sidecar-nonfactor AST (1), no-PRNG AST (1), interpreter-guard
  (1), long_exposure exemption (3), verdict-in-report + rubric-hash-
  in-report (2), fresh-subprocess freeze equals on-disk (2).
- `tests/test_launched_event_convention.py` — 8 named cases:
  scan-returns-rows (1), c35+ all validated (1), doc exists (1), doc
  names rule literally (1), offender list stable (1),
  offender-fixture present + lines valid (2), all launched names
  well-formed (1).
- `tests/test_integration_cross_branch.py` §56 extended with anchor-
  manifest + launched-convention presence checks (≥5).

All tests are plain-assert style, invoked as `PYTHONPATH=.
/usr/bin/python3 tests/<name>.py`.

## §7. Ledger events emitted (`-clone-2` suffix on infra families)

Per the brief's step-12 template:

1. `_run/cycle_35_launched-clone-2` — validated (step 1, already
   emitted at start of branch).
2. `_plan/register-anchor-manifest-v1-clone-2` — validated (adds row
   to plan of record).
3. `_infra/anchor-manifest-v1-clone-2` (in-progress → validated) —
   validated on freeze + drift check clean.
4. `_infra/launched-event-convention-clone-2` — validated on convention
   doc + test landing.
5. `_infra/cross-branch-integration-test-cycle35-clone-2` — validated on
   §56 extension green.
6. `_run/cycle_35_closed-clone-2` — validated.

Housekeeping:

7. `_archive/cycle-35-scratch-clone-2` — validated; lists archived
   scratch files.
8. `_infra/adopt-cycle35-tests-clone-2` — validated; lists new test
   file paths.

No `_manager/anchor-drift-triage-clone-2` handoff was emitted (verdict
is `MANIFEST_LOCKED` — no drift surface for c36 to triage). No
`_infra/adopt-fanout-artifacts-anchor-manifest-clone-2` was needed:
all new files this branch produced were declared as `artifacts` on
their respective ledger events at emit time (no orphan surface).

## §8. `promise_check` state

At branch close: **0 ERRORs**, 113 WARNs. Only 2 WARNs are attributable
to files this session touched — both from parallel c35 sibling clones
(`tools/_c35_egress_probe.py`, `tools/_scratch_sanity.py`) — and both
predate this branch's shadow ledger. Every file this branch produced
under `scripts/anchor_manifest/`, `data/anchor_manifest_v1*`,
`docs/anchor_manifest_v1*`, `docs/fanout_launched_event_convention.md`,
and `tests/*` is declared in an event's `artifacts` field at emit
time; **none of this branch's outputs surface a WARN**. The remaining
WARNs comprise (a) pre-c35 legacy trailing-slash and long_exposure/*
exemption notes, and (b) orphan artifacts landed by the other two c35
clones (`palette_v2_render/*`, `gen_palette_batch_v2/*`,
`docs/palette_v2_hydration_render_rubric.md`, etc.) — those are the
sibling branches' adoption events to emit, not this branch's.

## §9. c36 handoff notes

- The manifest is the single source of truth for anchor SHA
  verification. Future branches SHOULD drop bespoke
  `anchor_preservation.json` snapshots in favor of
  `data/anchor_manifest_v1.json` lookup.
- No drift surfaced — no `_manager/anchor-drift-triage-clone-2` handoff
  is open. If a subsequent cycle observes drift at re-freeze time, the
  drift is a first-class finding: **do not rewrite anchors**.
- The offender-list fixture at
  `tests/fixtures/launched_event_offender_list_v1.txt` is stable. If a
  future cycle emits a launched-event with `status: in-progress`,
  `test_launched_event_convention.py::test_05_offender_list_stable`
  fails as growth, and a writer-boundary lint (analogous to c33's
  `_lint_clone_shadow`) should follow.
- Do **not** re-attempt the five locked anti-patterns (c8
  octave-suppression, c11 CLAP/VGGish embedding, c22 stability, c23
  head-regularization, c25 feature-representation).
