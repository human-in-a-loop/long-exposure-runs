---
title: "Final audit report — Music-Gen campaign"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
audit: "final"
audit_date: "2026-09-02"
cycles_range: "1..54"
promise_check: "green (0 ERROR)"
run_id: "run-2026-08-28T040704Z"
stage: "document (48 of 48)"
wall_cap_exceeded: false
---
# Final audit report — Music-Gen campaign

## §0. Scope

Closing-the-books pass at run scope, per the final-auditor role
contract. Assesses the run's structured commitments (plan-of-record
milestones, ledger events, evidence files, `_manager/*` adjudications,
`_plan/*` amendments, closure documents), **not** the exploration
mechanics. The ratings-audio egress block (HTTP 429 + `tv_embedded`)
is treated as a live external constraint carried forward, not a
defect.

- Cycles executed: 1..54 (max cycle in ledger = 54).
- Ledger events: 920 rows across 762 distinct milestones.
- Substantive `M-*` milestones: 231. Bookkeeping (`_infra` / `_plan` /
  `_manager` / `_run` / `_archive`): 531.
- Reports on disk (`reports/cycles/`): 32 cycle-report `.md` (+PDF).
- `promise_check`: exit 0, 0 ERROR, 3437 WARN (breakdown in §5).
- Findings across 47 prior audit stages: 111 rows in
  `findings.jsonl` (0 CRITICAL / 1 MAJOR / 21 MODERATE / 10 MINOR /
  30 INFO / 45 NONE / 4 PASS). No `reconcile: true` entries — no
  ledger events are committed by this audit.

## §1. Status distribution

Latest event per milestone across all 762 distinct milestone_ids:

| Status       | Count |
|--------------|------:|
| validated    |  731  |
| in-progress  |   22  |
| invalidated  |    6  |
| reopened     |    2  |
| superseded   |    1  |
| **total**    |  762  |

Substantive `M-*` split (231 milestones):

| Root          | validated | in-progress | invalidated | reopened |
|---------------|----------:|------------:|------------:|---------:|
| M-CLASS-1     | 1  | – | – | – |
| M-DAW-SPIKE-1 | 7  | 1 | 1 | – |
| M-EAR-1       | 27 | 3 | 3 | – |
| M-GEN-1       | 24 | 3 | – | – |
| M-HEUR-1      | 6  | – | – | – |
| M-INGEST-1    | 24 | 3 | – | 1 |
| M-RECREATE-1  | 13 | – | – | – |
| M-RECREATE-2  | 44 | 6 | – | – |
| M-RULES-1     | 28 | – | – | – |
| M-SCORE-1     | 16 | – | – | – |
| M-SEP-1       | 4  | – | – | – |
| M-TEX-1       | 9  | 1 | 1 | – |
| M-TRANS-1     | 4  | – | 1 | – |
| **totals**    | **207** | **17** | **6** | **1** |

## §2. Plan adherence

All five goals G1..G5 from the plan of record have substantive
`validated` deliverables. Every plan-of-record row that has a
firing ledger event resolves to one of the eight unified status
values. Two structural adherence gaps survive verification:

- **Plan-ledger drift, RECREATE-2 v2 supersede.** Plan-of-record row
  `M-RECREATE-2/accurate-small-set-v2` is registered as the supersede
  parent of the v1 tree (`_plan/m-recreate-2-rubric-v2-supersede`
  fired at c50), but every c50+ leaf (rc7/rc8/rc9/rc10/*) still fires
  under `M-RECREATE-2/accurate-small-set/…`. Terminal work is
  correctly located and validated; only the parent-identifier
  attribution drifts.
- **Plan-ledger drift, c46/c47 clone-suffixed rows.** Four registered
  milestones never fire on the ledger:
  `_archive/deprecate-c45-determinism-check-clone-2`,
  `_infra/pin-source-date-epoch-anchor-clone-2`,
  `_infra/pre-registration-gate-policy-scope-verification-clone-1`
  variants, and a small number of egress-probe rows. No substantive
  work is missing; these are planning stubs superseded by the same
  cycle's rollup emissions.

## §3. Confidence calibration

Distribution across all 762 terminal events:

| Confidence level | Count |
|------------------|------:|
| high             |  742  |
| medium           |   20  |
| low              |    0  |
| provisional      |    0  |

No `validated` milestone terminates at `low` or `provisional`
confidence. The 20 `medium`-confidence rows are legitimate — early
c1..c4 fanout events (M-INGEST-1, M-CLASS-1, M-DAW-SPIKE-1,
M-HEUR-1, M-TEX-1/panel, M-SEP-1 base) that were subsequently
promoted to `high` by follow-on sub-milestone rollups. No calibration
inversions detected.

## §4. Residual debt (17 substantive `in-progress` at run close)

Each row below is carried into future work; none is a silent defect.

### 4.1 Design-locked in-progress (2)

- **`M-EAR-1` (parent).** Held in-progress by design under c26 Path B
  commit doc pending real-label calibration on full 80-song corpus;
  v2 delivered `EAR_v2_PARTIAL` (c45) with c46 mapping-clarified
  adjudication; v2.1 sub-leaves validated at c47.
- **`M-EAR-1/armed-harness` (c11).** Waits on two-consecutive
  `media_ok=true` egress probes; fixture-verified at c26 and c31.

### 4.2 RECREATE-2 arc leaves (7)

- `M-RECREATE-2/accurate-small-set` and RC1/RC4/RC5/RC6/RC9 leaves
  (c49–c50). Explicit `NotImplementedError('c50+ branch')` stubs
  landed under mtime-pinned rubric chains; c51–c54 delivered
  substantive RC1/RC2/RC3/RC7/RC9/RC10 implementations under peer
  sub-milestone labels. Plan-of-record parent-attribution drift is
  captured in §2.

### 4.3 Bookkeeping / harness in-progress (13)

- Nine `_run/cycle_<N>_launched(-clone-<k>)?` rows never re-close at
  integration time. This is a harness-level pattern — the launch
  event is a stub; the close event lives under
  `_run/cycle_<N>_closed` and, for fan-outs, under
  `_run/post-merge-integration-fork-<hash>`. No substantive work is
  missing.
- `M-INGEST-1/egress-probe-cycle{47,51}-clone-*` (2). Two probe rows
  reopened by the c33 harness auto-suffix without a later close.
- `_manager/M-INGEST-1-corpus-expansion-plan-c48-queued-clone-1` (1).
  Bookkeeping-only row acknowledged c48 Branch B produced no
  substantive artifacts; c49 registered this explicitly.
- `_manager/background-job-supervision-clone-0` (1). c36 in-progress
  row that never receives a closing event; two observed silent
  background-job-death events at c31 (fixture) and c36 (feature
  extraction) have no adjudication row. **See finding F-13.**
- `_run/start` (1). Root run-open event; expected in-progress.

### 4.4 Superseded / reopened

- `_infra/shadow-ledger-probe` (c6) — `superseded` by design.
- `M-INGEST-1/egress-probe*` — one `reopened` cluster tied to the
  c33 auto-suffix; verified honest.

## §5. Findings

Aggregate (111 findings across stages 2..47; verify + test):
`CRITICAL 0, MAJOR 1, MODERATE 21, MINOR 10, INFO 30, PASS 4,
NONE 45`.

### 5.1 Major (1)

- **F-01 · Missing SSoT source files (`_infra/harness-and-writer-hardening-v3`).**
  `long_exposure/workspace_bootstrap.py` and
  `long_exposure/tools/_ledger_schema.py` — the source files the
  c14/c22/c33/c48 hardening chain claims to have edited — are **not
  present on disk** under `long_exposure/`. Package layout: only
  `long_exposure/tools/promise_check.py`, `org_check.py`, and
  `_ledger_schema.py` exist; `workspace_bootstrap.py` is absent. All
  invariants the writer enforced (rubric mtime gates, byte-determinism
  ×2, three-way rubric-hash chains, clone-namespace auto-suffix)
  remain **enforced downstream** because the on-disk verdict artifacts
  encode them, and `promise_check`/`org_check` still run green from
  the surviving package files. But the source-of-truth code the audit
  chain claims to have hardened is not verifiable from disk.
  *Failure scenario:* a c55+ cycle asked to re-derive or extend the
  writer contract would find nothing to extend. Recommendation: the
  original builder to either restore the source files from a prior
  session, or file a `_plan/*-supersede` event that renames the
  hardening chain to what actually lives in the package.

### 5.2 Moderate (21)

Grouped by category; each item survives verification against on-disk
evidence.

- **F-02 · Artifact loss (M-GEN-1 batch cluster).** 684 distinct
  artifact references in the ledger are absent on disk. Buckets:
  `data/gen/*` (565 — batch-v1..v6, palette-driven-batch-v1..v4,
  rated-corpus), plus scattered `tools/stale/*` (98) and
  `docs/figures/*` (21). All are downstream generation renders and
  ephemeral probe outputs; their verdict JSONs and provenance rows
  survive. No verdict claim is unverifiable, but the renders
  themselves cannot be re-listened to.
- **F-03 · Silent supersession of `_infra/fanout-namespace-convention`.**
  The c32 event pins `docs/fanout_namespace_convention.md`; that
  exact path is absent. Versioned successors (`_v1.md`, `_v2.md`,
  `_v3.md`, `_v3_rubric.md`) are present but no `_plan/*-supersede`
  event narrates the rename.
- **F-04 · Egress-probe schema drift.** 15/34 rows in
  `data/ingestion/egress_status.jsonl` predate the `cycle` field
  (c1 bootstrap). Cycles c36..c45 have no on-disk probe rows despite
  the c49 policy `_plan/egress-retry-cadence-policy-formalized`
  requiring ≥1 per cycle.
- **F-05 · Egress capability gap.** Two consecutive `media_ok=true`
  rows exist at c1 bootstrap (both against YouTube canonical
  smoke-test video `jNQXAC9IVRw`), but the c8
  `M-INGEST-1/egress-ready-automation` state machine never fired
  because those rows target a *smoke-test target*, not the rated
  playlists. The `two-consecutive` unblock signal does not
  distinguish smoke-test from production targets.
- **F-06 · Anchor manifest read-only drift.** Full scan of
  `data/anchor_manifest_v1.json` (21657 file SHAs across 19 anchors)
  finds **2 drifted anchors**:
  `scripts/palette_render/render_stem.py` was intentionally extended
  at c36 (additive kwargs), so the c33-frozen SHA no longer matches
  the on-disk file. The drift is *known and honest* (c36
  backwards-compat regression asserts `parameter_dict=None` still
  reproduces the c33 anchor), but the anchor-manifest itself was
  never republished to reflect the extension.
- **F-07 · Verdict-schema drift (rubric_hash top-level convention).**
  `data/recreate_v0_full_corpus/verdict.json` and the c31 palette
  instrument-determinism per-row verdict do not expose `rubric_hash`
  as a top-level key, breaking the three-way byte-equality convention
  otherwise used consistently.
- **F-08 · Content-flip analysis evidence drift.**
  `M-TEX-1/panel/embedding/content-flip-analysis` (c14) pins 13
  artifacts and a follow-up `_infra/adopt-content-flip-artifacts`
  event registers the full `variants/` directory; the directory
  itself is only partially present on disk (subset survived, no
  supersede event).
- **F-09 · Reporting gap.** `reports/cycles/` has 21
  `report_cycles_N-M.md` files. c19 was a genuine skip (0 ledger
  events); c41 (3 events) and c42 (10 events) have no report;
  c55–c58 has a report (`report_cycles_56-58.md`) but no ledger
  events past c54 — the report is empty of substantive content.
- **F-10 · Fanout post-merge bookkeeping gap.** 23 fanout
  post-merge-integration events landed; the c31 fork
  `cfc5009aca96` fanout is missing a dedicated
  `_run/post-merge-integration-fork-<hash>` event (rollup captured
  under `_infra/fanout-namespace-convention` reconciliation).
- **F-11 · Housekeeping-pattern coverage gap.** The c29-codified
  `_archive/cycle-N-scratch` + `_infra/adopt-cycleN-tests` pair
  is missing at least one of the two at cycles 40, 41, 42, 43.
- **F-12 · Ratings manifest / on-disk drift.**
  `corpus/ratings/ratings_manifest.tsv` holds 80 rows for bands
  4/5/6 only (20+30+30). The 10 on-disk band-7 songs
  (`corpus/ratings/7/*.mp3`, all `LOCAL`) are not in the manifest
  despite being the rated-audio source that unblocked the c37
  `M-RECREATE-1/first-real-audio` chain. `corpus/ratings/7/RECEIPTS.md`
  states the manifest was updated; it wasn't.
- **F-13 · Unresolved manager row (background-job supervision).**
  `_manager/background-job-supervision-clone-0` emitted c36 with
  `status: in-progress` after two silent background-job-death events
  (c31 fixture, c36 feature extraction). Zero successor closure event.
- **F-14 · v2 supersede plan-ledger drift.** See §2.
- **F-15 · c46/c47 clone-suffixed rows never fire.** See §2.
- **F-16 · Anchor-preservation schema polymorphism.** 44
  `anchor_preservation*.json` artifacts under `data/` use 5 distinct
  top-level schemas. Each cycle's own tests are consistent, but no
  SSoT schema.
- **F-17 · Egress policy-compliance gap at c52.** c52 emitted no
  `M-INGEST-1/egress-probe*` row despite c49 policy requiring one.
- **F-18 · RECREATE-2 v2 vs v1 plan tree divergence** — narrated
  §2.
- **F-19..F-21** — additional plan-ledger drift and schema-drift
  items narrated inline above; each has an on-disk successor that
  covers the substance.

### 5.3 Minor (10 — logged, not acted on)

- Stale `C3` verdict field on `M-EAR-1/synthetic-label-stability-audit`
  (byte-determinism was actually verified; field never updated).
- Silent stem under fallback (`M-DAW-SPIKE-1/palette-schema-v2-hydration-render`
  drums, fluidsynth_gm fallback below 1e-4 threshold — flagged with
  `run1_silent=true`, first-class negative finding).
- Deferred VGGish representation
  (`M-EAR-1/feature-representation-audit`) honestly deferred.
- Legibility notes on collision-model / DawDreamer / rules-extraction
  verdicts (pre-c33 convention, no separate rubric-hash file).
- 6 unarchived `merge_report_*.md` files at repo root.
- Cross-band `long_exposure/*` package-path registration gap.
- Documentation-code drift on band-7 ratings (see F-12; kept both).
- `promise_check` validator run summary: 0 ERROR, 3437 WARN. Of
  the 3437 WARN, 2713 are orphan artifacts, 684 are missing-on-disk,
  21 are non-canonical paths, 20 are plan-milestone-no-events. All
  categorized; none block.

### 5.4 Info / pass / none (79 combined)

All are neutral verification observations (closure_verified,
invalidation_verified, validation_verified, rubric-chain byte-equality
confirmations). Not summarized further here.

## §6. Future work

Each item is anchored to a specific residual-debt or finding row so a
downstream reader can act on it directly.

1. **Restore or supersede the missing `long_exposure/*` writer
   sources.** Anchored to F-01. Either recover
   `long_exposure/workspace_bootstrap.py` and
   `long_exposure/tools/_ledger_schema.py` from a prior session, or
   emit a `_plan/*-supersede` event that names what actually
   implements the c14/c22/c33/c48 hardening contract today.
2. **Close the RECREATE-2 v2 plan-tree attribution.** Anchored to §2
   / F-14 / F-18. Emit one supersede event that either (a) renames
   the c51+ RC7/RC10 leaves to the v2 parent, or (b) explicitly
   folds v2 back into v1 with a note that the rubric-v2 was carried
   inline under the v1 leaf identifiers.
3. **Republish `data/anchor_manifest_v1.json` as `_v2`.** Anchored
   to F-06. The c36 additive-kwargs edit to `render_stem.py` is
   material; republish the manifest with anchor #20 =
   post-c36-edit SHA + backwards-compat contract explicitly named.
4. **Close the `_manager/background-job-supervision-clone-0` row.**
   Anchored to F-13. Either emit a closure event that adjudicates
   the two observed silent-death cases, or record them as `_archive`
   with lessons learned.
5. **Reconcile the ratings manifest with band-7 on-disk audio.**
   Anchored to F-12. Append 10 band-7 rows to
   `corpus/ratings/ratings_manifest.tsv` so provenance matches
   what M-RECREATE-1 already consumed.
6. **Fill the c41/c42/c52/c55–c58 reporting/probe gaps.** Anchored
   to F-04, F-09, F-17. c19 was a genuine skip; the others were
   substantive cycles.
7. **Rebuild the missing generation-batch renders on demand.**
   Anchored to F-02. All 565 missing `data/gen/*` artifacts are
   deterministically regenerable from the seeded ledger; a single
   sweep can re-materialize them.
8. **Unify anchor-preservation schema and verdict-file rubric-hash
   convention.** Anchored to F-07, F-16. Publish one SSoT schema
   (`data/anchor_preservation_v1.json` + `data/verdict_v1.json`)
   and have subsequent cycles conform.
9. **Distinguish smoke-test from production targets in
   `egress_status.jsonl`.** Anchored to F-05. Add a `probe_kind ∈
   {smoke, production}` field so the two-consecutive-`media_ok`
   unblock signal cannot be spuriously satisfied by smoke rows.
10. **Real-label M-EAR-1 calibration.** Anchored to §4.1. Awaits
    egress unblock; c26 Path B commit doc pre-registers the SB1/SB2/SB3
    success bars. First-class future work.

## §7. Figure coverage

Figures on disk under `docs/figures/`: many present (batch grids,
collision heatmaps, tex-embedding flip, DAW spike coverage v2/v3,
etc.). Figures referenced by ledger `artifacts` but absent from disk:
21 (subset of F-02's artifact loss). Milestones that warrant a figure
and have one: all M-GEN-1 batch-vN rollups, M-DAW-SPIKE-1 gap-closure
v2/v3, M-TEX-1 content-flip. Milestones that warrant a figure and
lack it: M-RECREATE-2 RC0..RC10 (only tabular scorecards; no
before/after mel or centroid plots). See summary JSON.

## §8. Reconciliation log

**No reconciliation events emitted.** The findings file contains zero
`reconcile: true` entries — the audit surfaces defects for the
original builder to address rather than mutating the ledger itself.
This is consistent with the audit-role file-writing contract (audit
observes and reports; only the harness batch-commits reconciliations,
and none were queued).

## §9. Audit trail

- Total audit stages: 48 (explore 1 + verify 23 + test 23 + document 1).
- Per-stage files: `audits/final/stages/{verify,test}_Nof23.md` +
  `audits/final/explore.md` + this file (48/48).
- Findings JSONL: `audits/final/findings.jsonl` (111 rows,
  append-only across stages 2..47).
- Lesson candidates JSONL: `audits/final/lessons.jsonl` (empty —
  no lesson candidates emitted; nothing this audit observed rose
  to the confidence + evidence-count bar the role contract requires
  for a durable lesson).
- Wall-cap: not hit.
- `promise_check`: exit 0, 0 ERROR.
- No source files under `long_exposure/*`, `scripts/*`, `data/*`,
  `docs/*`, `tests/*`, `corpus/*`, `reports/*`, or
  `promise_ledger.jsonl` were modified by this audit.

## §10. Verdict

The Music-Gen campaign closes with **207/231 substantive `M-*`
milestones validated, 6 honest invalidations (first-class negative
findings), 17 in-progress by design or awaiting external unblock,
1 superseded, 1 reopened**. All invalidations are honestly narrated
and load-bearing to the record — they document what does not work
under the pre-registered criteria, not silent failures.

The audit surfaces **0 CRITICAL and 1 MAJOR** finding (F-01, missing
`long_exposure/*` source files). The MAJOR finding does not overturn
any validated verdict — every downstream artifact the missing sources
would have written is present on disk with the appropriate rubric-hash
chain — but it is a real gap in the source-of-truth for the
harness-hardening chain and requires the original builder's attention.

The 21 MODERATE findings are all schema / bookkeeping / evidence-drift
items that survive verification and have on-disk successors; they are
listed for future-cycle cleanup, not audit-cycle repair.
