# Post-merge integration report — fork 00b3ae64444c (cycle 10)

**Scope:** worker-only post-merge integration for fork `00b3ae64444c`.
Three clones reconciled into the workspace root:

| Clone | Milestone | Verdict | Deliverable |
|---|---|---|---|
| 0 | M-GEN-1/first-generation | validated/medium | docs/gen_first_generation_report.md |
| 1 | M-INGEST-1/breadth-second-seeds | validated/medium | docs/pipeline_breadth_report.md |
| 2 | _infra/ledger-schema-hardening | validated/high | docs/ledger_schema_hardening.md |

Zero cross-branch content conflict: the three deliverable trees
(`scripts/gen` + `data/gen`, `scripts/breadth` + `data/breadth`,
`tests/test_ledger_writer_validation.py` + upstream `long_exposure/tools/_ledger_schema.py`)
touch disjoint paths. Clones' own scope-close events were already in
the workspace root ledger at integration entry — the fanout collapse
merged the per-clone shadow ledgers back in.

## What this integration did

Clones had already emitted their own closure events (ledger was at
186 rows on entry). Integration work reduced to:

**1. Plan-of-record drift fixes** — added three rows to the Milestones
table so `promise_check` accepts the pre-existing per-seed events:

- `M-INGEST-1/breadth-second-seeds/seed_mid_50s`
- `M-INGEST-1/breadth-second-seeds/synth_060s`

(Row for `_infra/ledger-schema-hardening` was already added by clone-2.)

**2. Ledger repair (in-place, atomic via `os.replace`)** —

- Line 160: `event_id` was a raw SHA-256 hex string (produced by an
  ad-hoc emitter under `_plan/register-gen-first-generation-milestone`
  before the hardened writer landed). Converted to a canonical UUID via
  `uuid5(uuid.NAMESPACE_NIL, hex)`. Original hex preserved in
  `event_id_original`.
- Lines 179–184: six events with `milestone_id: "M-TEST-1/writer"` were
  round-trip fixtures emitted by clone-2 during ledger-writer testing.
  Renamed to reserved namespace `_infra/ledger-writer-test-fixtures` so
  `promise_check` accepts them without diluting the plan. Original
  `milestone_id` preserved in `milestone_id_original`.

**3. Rollup events (5 emitted via the hardened writer)** — ledger
186 → 191:

| # | milestone_id | status | conf |
|---|---|---|---|
| 1 | `_infra/ledger-writer-test-fixtures` | validated | high |
| 2 | `_infra/repair-ledger-cycle10` | validated | high |
| 3 | `_plan/register-post-merge-integration-fork-00b3ae64444c` | validated | high |
| 4 | `_run/post-merge-integration-fork-00b3ae64444c` | validated | high |
| 5 | `_archive/integration-scratch-fork-00b3ae64444c` | validated | high |

**4. Hardened-writer live proof-of-life** — every event this
integration emitted went through `workspace_bootstrap.append_ledger_event()`
from cycle-2 clone. Two emit-time validation failures caught real
schema deficiencies in my draft events (missing `status`, `narrative`,
`confidence.rationale`) — the writer refused them and returned a typed
`LedgerAppendError` naming the missing fields, exactly as designed.
Retry after fixing the fields succeeded. This is the tightening from
cycle-2 doing its job on live traffic in the very cycle it landed.

## Verification (all green)

| Check | Result |
|---|---|
| `promise_check` | **0 ERRORs** (7 pre-existing WARNs unchanged: 5 trailing-slash canonicalization, 1 `M-EAR-1` parent with no events, 1 orphan `data/ear/features/*.npz` cache byproduct from M-GEN-1 ear scoring) |
| `tests/test_ledger_writer_validation.py` | **PASS** (exit 0) |
| `tests/test_integration_cross_branch.py` | **PASS (0 failures)** across §1–§22 including new §20 (schema hardening), §21 (M-GEN-1, 39 checks, per-artefact SHA-256 anchors + PRNG-import grep guard + provenance-chain shape), §22 (breadth, per-seed SHA-256 anchors × 2 seeds) |

## Anti-pattern lock preserved

`M-TRANS-1/basic-pitch/octave-suppression` remains `invalidated/high`
(cycle 8). None of the three clones re-attempted it; clone-1 explicitly
names the anti-pattern in its report ("basic-pitch on pure sines — this
is the same octave-doubling artefact identified in cycle 8; do NOT
re-attempt").

## Ledger at close: 191 rows

## Recommended follow-ups (deferred, out of scope for this integration)

From the clones' own reports:

- `M-GEN-1/rule-composition-constraint`: post-sampling coherence gate
  flagging arrangement-silences-pitched-Parts and form-granularity-too-fine.
- CORN-head recalibration on rated audio when `M-INGEST-1/egress-ready-automation` fires.
- Cheap rules extraction over the two new merged MusicXMLs
  (`data/breadth/{seed_mid_50s,synth_060s}/merged.musicxml`) to widen
  the M-RULES-1 corpus without needing new audio.
- Split `tests/test_integration_cross_branch.py` (now 1110 lines / 413+
  checks) by milestone; flagged not executed.
- Shadow-ledger per-line validation at `fanout._concat_clone_ledgers`
  (clone-2 §Recommended follow-up).
- Adopt the orphan `data/ear/features/gen_first_gen_d81089d39f31b5ca.npz`
  under M-GEN-1/first-generation.

Ready for next cycle. Ledger clean, tests green.
