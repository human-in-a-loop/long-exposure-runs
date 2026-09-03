# Merge report — fork f1bae241bde9, clone 0 (M-RULES-1 extraction-half)

**Agent:** worker (cyd7bevdr@mozmail.com)  •  **Cycle:** 9  •  **Date:** 2026-08-28

## Scope delivered

M-RULES-1/extraction — five per-rule_type extractors reading the frozen
M-SCORE-1 merged 30 s MusicXML via music21 9.1.0, emitting typed rule
rows through the existing M-RULES-1/schema ledger writer.

**Aggregate:** 28 rows on `data/rules/ledger.jsonl` (previously empty).
Per type: harmonic 6 / rhythmic 6 / melodic 6 / form 5 / arrangement 5.
Zero validation errors. Byte-identical re-run
(SHA-256 `4fe722adde034c099ff9e65437f0d5c138cb3dd2595089960150af5c2546fc4b`).
28 / 28 provenance pointers re-hash to their declared source files.

No falsifiability escape hatch invoked — every rule_type met the ≥5-row
bar on this seed.

## Files created (all new)

Extractor library:
- `scripts/rules/extract/__init__.py`
- `scripts/rules/extract/_common.py`
- `scripts/rules/extract/from_score.py` (orchestrator)
- `scripts/rules/extract/harmonic.py` (`harmonic-v1`)
- `scripts/rules/extract/rhythmic.py` (`rhythmic-v1`)
- `scripts/rules/extract/melodic.py` (`melodic-v1`)
- `scripts/rules/extract/form.py` (`form-v1`)
- `scripts/rules/extract/arrangement.py` (`arrangement-v1`)
- `scripts/rules/extract/plot_coverage.py`

Deliverables:
- `docs/rules_extraction_report.md` (required output artifact)
- `docs/figures/rules_extraction_coverage.png`
- `data/rules/ledger.jsonl` (28 rows)

Tests + integration:
- `tests/test_rules_extraction.py` (34 assertions, all pass)
- `tests/test_integration_cross_branch.py` — extended with §18
  M-RULES-1/extraction invariants (33 new checks)

Plan-file:
- `plan_of_record.md` — 6 new rows in the 5-col Milestones table for
  `M-RULES-1/extraction` + 5 sub-milestones

Archived to `tools/stale/`:
- `_determinism_check_rules.py`
- `_verify_rules_roundtrip.py`
- `_sample_rules_for_report.py`
- `_emit_rules_extraction_events.py`

## Files modified (existing → touched)

- `tests/test_integration_cross_branch.py` (appended §18 only; nothing
  earlier changed by this clone)
- `plan_of_record.md` (6-row insertion between the M-TEX-1/stage-by-stage
  row and the `## Sub-milestones` header)

## Files NOT touched

- `scripts/rules/{ledger.py, validate.py, rule_id.py}` — schema-half
  contract preserved verbatim (append-only, jsonschema+cross-row
  validator, content-hashed rule_id).
- `scripts/rules/schema/rules_v1.json` — schema is frozen.
- Every M-SCORE-1, M-TRANS-1, M-SEP-1, M-HEUR-1, M-EAR-1, M-TEX-1
  artifact — untouched.
- `M-TRANS-1/basic-pitch/octave-suppression` — campaign anti-pattern;
  intentionally not re-attempted.

## Ledger events (shadow ledger, ready for merge)

Ten events emitted to
`/home/user/music-gen-instance/fork-f1bae241bde9/clone-0/promise_ledger.jsonl`:

| # | milestone_id | status | confidence |
|---|---|---|---|
| 1 | `_plan/register-extraction-submilestones` | validated | high |
| 2 | `M-RULES-1/extraction/harmonic` | validated | high |
| 3 | `M-RULES-1/extraction/rhythmic` | validated | high |
| 4 | `M-RULES-1/extraction/melodic` | validated | high |
| 5 | `M-RULES-1/extraction/form` | validated | high |
| 6 | `M-RULES-1/extraction/arrangement` | validated | high |
| 7 | `M-RULES-1/extraction` | validated | high |
| 8 | `M-RULES-1` (parent rollup, both halves done) | validated | high |
| 9 | `_infra/cross-branch-integration-test-cycle9-rules` | validated | high |
| 10 | `_archive/rules-extraction-scratch` | validated | high |

All events use the healthy schema: `ts` / `narrative` / nested
`confidence: {level, rationale, assessor}` / explicit `event_id` /
`agent: "worker"` / `cycle: 9`. No cycle-8-style schema drift.

## Green matrix (all runs made from `/home/user/long-exposure-runs/music-gen`)

| Command | Result |
|---|---|
| `PYTHONPATH=. /usr/bin/python3 scripts/rules/extract/from_score.py --dry-run` | 28 rows, 0 errors |
| `/usr/bin/python3 scripts/rules/extract/from_score.py` | 28 rows appended |
| `PYTHONPATH=. /usr/bin/python3 tests/test_rules_extraction.py` | 34 pass, 0 fail |
| `PYTHONPATH=. /usr/bin/python3 tests/test_integration_cross_branch.py` (M-RULES-1 §18 alone) | PASS on §18's 33 checks |
| `PYTHONPATH=. /usr/bin/python3 tests/test_rules_schema.py` (regression) | 25 pass, 0 fail |
| Determinism re-run into two fresh temp ledgers | rule_id sequences equal; ledger SHA-256 equal (`4fe722ad…`) |

Note: the sibling clone-1 (M-TEX-1/stage-by-stage) appended §19+
concurrently. A merged run of `test_integration_cross_branch.py` will
exercise both branches' § blocks; there is one sentinel line at file
end (`sys.exit(1 if fail else 0)`) which must appear exactly once —
verify the conductor's merge preserves that.

## Expected orphan WARNINGs at pre-merge promise_check

`promise_check` against the root workspace ledger surfaces expected
transient WARNINGs BEFORE the shadow-ledger merge:

- "plan milestone `M-RULES-1/extraction/…` has no ledger events yet"
- "orphan artifact in managed path: `scripts/rules/extract/*`, `docs/rules_extraction_report.md`, `docs/figures/rules_extraction_coverage.png`, `tests/test_rules_extraction.py`"

These clear the moment the conductor merges the shadow ledger — every
new artifact is listed in the `artifacts` field of one of the ten
events above. Same pattern as cycle-8 fork 3a908edcb241's clone-0
integration.

## Cross-branch conflict surface

Zero file-tree overlap with the sibling clone-1 (M-TEX-1/stage-by-stage).

- clone-0 writes: `scripts/rules/extract/*`, `docs/rules_extraction_report.md`,
  `docs/figures/rules_extraction_coverage.png`, `tests/test_rules_extraction.py`,
  new rows in `plan_of_record.md`, appended §18 in
  `tests/test_integration_cross_branch.py`, appended lines in
  `data/rules/ledger.jsonl`.
- clone-1 writes: `scripts/tex/*`, `docs/tex_stage_by_stage_report.md`
  (or similar), `docs/figures/tex_stage_by_stage_families.png`,
  `data/tex/renders/synth_030s/*`, and appears to have appended §19+
  in the integration test.

Both clones added rows to `plan_of_record.md`. The conductor should
concatenate them in the order they arrive; row order within the 5-col
table is not load-bearing for `promise_check`.

## Sufficiency vs. brief

| Brief criterion | Result |
|---|---|
| ≥25 rows appended to `data/rules/ledger.jsonl` (≥5 per rule_type × 5 types) | 28 rows (6/6/6/5/5) |
| 25/25 rows pass `validate_batch()` | 28/28, 0 errors |
| Two independent runs produce the same rule_id set | equal; ledger byte-identical |
| `read_ledger()` returns rows in insertion order | verified |
| `effective_rules()` returns the full set (no supersedes this cycle) | 28 == 28 |
| Every row's `provenance_pointers` resolves via re-hash | 28/28 |
| `docs/rules_extraction_report.md` present with coverage figure | shipped |
| `PYTHONPATH=. /usr/bin/python3 tests/test_rules_extraction.py` green | 34 pass, 0 fail |
| Zero `sidecar_nonfactor` imports across `scripts/rules/extract/` | AST-verified |

## Honest limitations (documented in report §6)

1. **Rhythmic extractor falls back to bass onsets** because the frozen
   basic-pitch drums stem is empty (0 events). Every hit is labeled
   `"kick"`; the label carries no real drum-class information. Report
   §6 tells downstream consumers to treat these labels as onset-grid
   placeholders, not percussion selectors. A future `rhythmic-v2`
   can supersede once a real drums transcription lands.
2. **Merged score reports 131 nominal measures for a 30 s clip** —
   music21 sees trailing empty measures across the 10 sub-parts.
   Extractors honor the nominal count; the arrangement density curves
   correctly show the actual active region as measures 0-15. Not a
   bug in this cycle; a hint for a future M-SCORE-1 refinement.

## Handoff

No further clone work. Ready for the fork conductor's merge pass. The
merge should:

1. Fold this shadow ledger into the root `promise_ledger.jsonl`.
2. Optionally re-run `promise_check` to confirm the 5 new
   `M-RULES-1/extraction/*` sub-milestones + parent + rollup now
   resolve to events, and the orphan artifacts clear.
3. Optionally re-run the integration test suite to confirm both
   clones' § blocks coexist.
