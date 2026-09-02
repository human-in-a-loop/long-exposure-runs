# Final Audit — Stage 28 of 48 (Test 4 of 23)

**Stage:** test (4/23) — periodic-invariants + report-coverage probes
**Working dir:** `/home/user/long-exposure-runs/music-gen`
**Preceding stage:** test_3of23 (orphan-milestone scan; F10–F15 CONFIRMED — clone-suffix bookkeeping gaps + three-way rubric_hash byte-equality PASS 4/4)

## Probes run this stage

1. **Egress-probe cadence audit** — schema + per-cycle coverage of `data/ingestion/egress_status.jsonl` against `_plan/egress-retry-cadence-policy-formalized` (path A / path B).
2. **Anchor-preservation contract audit** — 5-file sample from the 44 `anchor_preservation*.json` artifacts; verify claims + schema uniformity.
3. **Rubric-doc mtime discipline** — targeted 6-rubric check against per-milestone impl subdirs (per c46 path (ii) amendment: mtime hard, git-log advisory).
4. **Report-glob coverage** — gap scan of `reports/cycles/report_cycles_*.md` vs ledger-executed cycle range.

## Findings

| #    | Severity | Verdict    | Summary |
|------|----------|------------|---------|
| F16  | MODERATE | CONFIRMED  | Egress-probe schema drift + pre-c34 cadence silence |
| F17  | MODERATE | CONFIRMED  | `anchor_preservation*.json` schema drift (5+ variants; no unified contract) |
| F18  | INFO     | CONFIRMED  | Rubric-mtime discipline HELD on all 5 resolvable targeted samples |
| F19  | MODERATE | CONFIRMED  | Report-coverage gaps at cycles 19, 41, 42; `report_cycles_56-58.md` exists 4 cycles ahead of ledger |

## F16 — Egress-probe cadence + schema (MODERATE, CONFIRMED)

**Evidence:**
- `data/ingestion/egress_status.jsonl` has **34 total rows**.
- **15 rows carry no `cycle` key** (the c1-era bootstrap schema had only `{ts, video_id, http_code, media_ok, metadata_ok, stream_url_present, note}`); the 2 pre-c34 `media_ok=true` rows (bootstrap smoke-test — see F8 in test_2of23) are among these 15.
- Explicit `cycle` field first appears at c35; per-cycle rows exist only for cycles **{35, 46, 47, 48, 49, 50, 51, 53, 54}** — **c36-c45 (10 cycles) have no per-cycle egress probe rows on disk** despite the directive's periodic-retry mandate.
- Per-clone rows for c48 (×3), c51 (×4), c53 (×4) confirm path-A cadence enforced under fanout post-c49 policy formalization; c47 also has a per-clone row (clone-0) — clones 1-2 for c47 were only recorded as _plan/POR entries per test_3of23 F11.
- **Bootstrap-smoke rows** semantically indistinguishable from production probes at row-schema level (no `probe_kind` field; see F9 in test_2of23 for the schema-level defect).
- Last row (c53, clone-2): `path: 'A'`, `http_status: 429`, `note: 'tv_embedded client-no-longer-supported unchanged (17+ cycles); not blocking'` — consistent path-A cadence post-c49.

**Impact:** pre-c34 audit trail for periodic-retry compliance is impaired (cannot map an on-disk row to a specific cycle without external context). Ledger `M-INGEST-1/egress-probe-cycle<N>*` events partially compensate (c46+ have named milestones per cycle), but the JSONL sidecar is the primary compliance artifact per directive.

**Not a fix:** on-disk history is append-only; retroactively backfilling `cycle` on legacy rows would violate append-only invariant. Document as narrative caveat only.

## F17 — Anchor-preservation schema drift (MODERATE, CONFIRMED)

**Evidence:** 44 `anchor_preservation*.json` files across `data/`. Sampled 5 spread across cycle range; found **5 distinct top-level schemas**:

| Schema variant | Top-level keys | Sample |
|---|---|---|
| A | `count_pass, count_total, overall_pass, results` | `data/collision_model/anchor_preservation_hash.json` (c28) |
| B | `all_unchanged, anchors, n_anchors, pre, post, changed_paths, authorized_mutation_tracked_separately` | `data/ear_v1/anchor_preservation.json` (c38) |
| C | `captured_at, post, pre, unchanged` | `data/gen_palette_batch_v2/anchor_preservation.json` (c35) |
| D | `anchors, captured_at, count` | `data/pre_existing_test_drift/anchor_preservation.json` (c48) |
| E | `anchors_post, anchors_pre, changed, n_anchors, unchanged` | `data/recreate_v0/anchor_preservation.json` (c37) |

**All 5 samples report their preservation claims as PASS** (`overall_pass=True`, `all_unchanged=True`, `unchanged=True`, or `changed={}` respectively). Claims themselves are honest and internally consistent within each file.

**Impact:** no unified reader can consume the corpus. Any future rollup or cross-cycle drift analysis must handle all 5 schemas or accept partial coverage. This is a bookkeeping-consistency gap, not a data-integrity defect — the preservation guarantees hold within each file's own schema.

**No fix at audit stage:** normalizing the corpus would require rewriting historical artifacts (breaks byte-anchor chains). Recommend the anchor-manifest-v2 candidate document a canonical schema for future cycles.

## F18 — Rubric-mtime discipline (INFO, CONFIRMED)

**Evidence:** targeted 6-rubric probe against `docs/*_rubric.md` mtime vs `min(mtime)` of per-milestone impl subdir:

| Rubric | Impl subdir | n_scripts | Δ (rubric − script) | Verdict |
|---|---|---|---|---|
| `rc10_drums_bass_rubric.md` | `scripts/recreate_v2/rc10_drums_bass/` | 9 | −13.3 s | HELD |
| `rc10_guitar_piano_rubric.md` | `scripts/recreate_v2/rc10_guitar_piano/` | 6 | −11.8 s | HELD |
| `rc10_other_vocals_rubric.md` | `scripts/recreate_v2/rc10_other_vocals/` | 2 | −30.0 s | HELD |
| `palette_v2_hydration_render_rubric.md` | `scripts/palette_v2_render/` | 4 | −21.1 s | HELD |
| `rc7_v2_rerun_rubric.md` | `scripts/recreate_v2/rc7_v2_*.py` (per-file glob) | matched in stage-27 sweep | negative | HELD |
| `harness_and_writer_hardening_v3_rubric.md` | `long_exposure/*` (edits, not new dir) | — | — | N/A (no dedicated impl dir; validated via test suite `tests/test_harness_and_writer_hardening_v3.py`) |

**Note:** a coarse `docs/*rubric*.md` → `scripts/<hint>*/*.py` heuristic returned 39/45 NO_MATCH cases; those are naming-mismatch false alarms, not violations (e.g., `ear_v2_verdict_adjudication_rubric.md` → `scripts/ear_v2/adjudication/` — different tree). Targeted spot-checks confirm the c46 path (ii) amendment's mtime-hard invariant is respected on the substantive branches.

## F19 — Report-coverage gaps (MODERATE, CONFIRMED)

**Evidence:** 21 `report_cycles_N-M.md` files present under `reports/cycles/`, covering cycles 1–58 with gaps:

| Cycle | Reported? | Ledger events | Notes |
|---|---|---|---|
| 19 | **NO** | **0** | Genuine ledger gap (no c19 events); likely renumbered or unpublished |
| 41 | **NO** | 3 | Small event count — likely a triage/holding cycle |
| 42 | **NO** | 10 | Modest event count — probably substantive but no report published |
| 55 | **NO** | 0 | No ledger events either; ledger ends at c54 |
| 56–58 | **YES** (report present) | 0 each | `report_cycles_56-58.md` describes "c50 Close Correction + M-RECREATE-2 Rubric-v2 Peer-Supersede (Root Sequential)" — a report published ahead of ledger commitments |

**Ledger latest cycle:** 54. **Reports latest cycle:** 58. **4-cycle lead** of reports over ledger.

**Impact:**
- Cycles 41 and 42 have on-ledger events but no reader-facing report — moderate reporting-completeness gap.
- The 56-58 report exists as a plan-of-work document but no substantive ledger events back it up — orphaned narrative (the report claims c56-c58 actions that never landed on the ledger). Consumers taking the report at face value would think work is done that isn't.
- Cycle-19 gap is complete (no report AND no ledger events) — likely a skipped/renumbered cycle, not a defect.

**Recommendation for final report §Residual debt:** flag the 56-58 report as "written but never executed" so downstream readers don't over-count landed work.

## Gate check (test stage)

- **Is every fix verified against its original finding?** N/A — audit-only, no fixes attempted.
- **Have I checked for regressions in adjacent behavior?** YES — c9-formalized policy (c49) confirmed enforced c49+; pre-c49 rows expected schema-different, not regressed.
- **Are any new issues introduced?** NO — read-only probes.
- **All findings classified?** YES — F16 MODERATE, F17 MODERATE, F18 INFO, F19 MODERATE.

## What's next (stage 29 = test 5/23)

Planned probes:
1. **Ledger-writer invariants** — verify `_infra/harness-and-writer-hardening-v3` c48 fixes (substantive-exemption + supersedes-in-hash toggles) round-trip on a sample of post-c48 events.
2. **Rated-corpus manifest ↔ on-disk audio provenance** — re-hash 5 of the 43 rated MP3s and cross-check against `corpus/ratings/ratings_manifest.tsv`.
3. **Test-suite invocation surface** — sample 3 `tests/test_*.py` files from the c48-c54 window and verify they collect + import successfully (no execution).
4. **`_run/post-merge-integration-*` completeness** — check that each fanout fork (c31/c33/c34/c35/c36/c38/c47/c48/c51/c53) has a corresponding integration ledger event.

<checkpoint>
  <stage>test (4/23) — stage 28 of 48</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~200k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Ran 4 periodic-invariants probes; surfaced 4 findings (F16-F19: 3 MODERATE + 1 INFO). Egress-schema drift + anchor-preservation schema drift + report-coverage gap at c19/c41/c42 + c56-58 report ahead of ledger.</what-i-did>
  <next-action>Advance to test 5/23 (stage 29); probe ledger-writer invariants, rated-corpus provenance, test-suite collection, post-merge integration completeness.</next-action>
  <gate-check>Continuing in test stage; stage 28 file written to expected path; findings sidecar appended (see below).</gate-check>
</checkpoint>
