# Final Audit Explore Stage

Generated: 2026-05-13T17:01:33Z
Run id: run-2026-05-13T015136Z
Stage: 1 of 12 (explore)

## Inputs Read

- `plan_of_record.md`: read from workspace root; 33 plan milestones parsed.
- `promise_ledger.jsonl`: read in full; 89 JSONL events parsed.
- Cycle reports: 14 report files matched under `reports/cycles/`.
- Closure/supersession filename scan: 0 files found.
- `REFERENCES.md`: read for citation numbering; references [1]-[14] are present.
- `sessions.db`: queried directly at `<long-exposure>/long_exposure/data/sessions.db`; `audit_reports_index.md` was generated from matching session rows and report files.

No file whose name contains `CLOSURE` or `SUPERSEDES` was present in the workspace. Closure claims therefore remain represented by the named closure/archive/synthesis milestones and their artifacts, not by filename-matched closure documents.

## Status Distribution

- `validated`: 33

## Verify Slice Assignment

- Stage 2: `M-TAX-1`, `M-MODEL-1`, `M-BASE-1`, `M-TARGET-1`, `M-ARCH-1`, `M-PROTO-1`, `M-FINAL-1`
- Stage 3: `M-CAL-1`, `M-WORKLOAD-1`, `M-SWBASE-2`, `M-SYNTH-2`, `M-MEASURE-1`, `M-TRACE-1`, `M-REOPEN-1`
- Stage 4: `M-INGEST-1`, `M-PIPELINE-1`, `M-EVIDENCEPACK-1`, `M-PHASE3-SYNTH-1`, `M-ACQUIRE-1`, `M-DRYRUN-1`, `M-INTAKE-1`
- Stage 5: `M-UNCERTAINTY-1`, `M-LIFECYCLE-1`, `M-PHASE4-SYNTH-1`, `M-ROBUST-1`, `M-DEFER-1`, `M-CLOSURE-1`
- Stage 6: `M-ARCHIVE-1`, `M-TOOLCHAIN-1`, `M-INVARIANT-1`, `M-PUBLICBASE-1`, `M-PUBLICBASE-2`, `M-PUBLICBASE-SYNTH-1`

## Milestone Index

| Milestone | Status | Confidence | Cycle | Latest evidence pointer | Artifact existence | Verdict pending | Notes |
|---|---|---|---:|---|---:|---|---|
| `M-TAX-1` | `validated` | `high` | 1 | `physicalized-weights/docs/taxonomy_and_null.md` | 1/1 | yes - verify evidence support in assigned slice | Created taxonomy/null-hypothesis document defining physicalization levels, inference-component candidates and anti-targets, strong programmable baselines, and falsification criteria. |
| `M-MODEL-1` | `validated` | `high` | 1 | `physicalized-weights/scripts/breakeven_model.py` | 6/6 | yes - verify evidence support in assigned slice | Built and ran first-order break-even model over request volume, update cadence, software savings, fixed substrate cost, analog conversion overhead, yield/repair factor, utilization, and fallback penalty. |
| `M-BASE-1` | `validated` | `high` | 1 | `physicalized-weights/scripts/breakeven_model.py` | 2/2 | yes - verify evidence support in assigned slice | Represented the baseline stack in the executable model before crediting physicalized strategies with any win. |
| `M-TARGET-1` | `validated` | `high` | 1 | `physicalized-weights/scripts/target_scoring.py` | 6/6 | yes - verify evidence support in assigned slice | Built and validated the ranked target and anti-target selection for physicalized inference components, preserving software/runtime and programmable-accelerator baselines before recommending a safety/filter clas |
| `M-ARCH-1` | `validated` | `high` | 1 | `physicalized-weights/docs/hybrid_safety_filter_architecture.md` | 7/7 | yes - verify evidence support in assigned slice | Built and validated a concrete hybrid open-architecture proposal for the safety/filter classifier target, including RISC-V-compatible memory-mapped control, update and rollback paths, fallback/fail-safe invaria |
| `M-PROTO-1` | `validated` | `high` | 1 | `physicalized-weights/scripts/verify_prototype_closure.py` | 9/9 | yes - verify evidence support in assigned slice | Tightened the M-PROTO-1 amended evidence contract so stale structural artifacts fail closure, then revalidated the pure combinational safety-filter prototype under the lint plus Yosys eval/synthesis evidence co |
| `M-FINAL-1` | `validated` | `high` | 1 | `physicalized-weights/scripts/build_final_synthesis.py` | 6/6 | yes - verify evidence support in assigned slice | Tightened the M-FINAL-1 evidence manifest so every evidence category used in the final synthesis is represented in the generated manifest and summary. Revalidated the final package without changing the central  |
| `M-CAL-1` | `validated` | `high` | 2 | `REFERENCES.md` | 19/19 | yes - verify evidence support in assigned slice | Validated Phase 2 M-CAL-1 after tightening the generated evidence trail. The calibrated companion preserves but weakens the safety/filter conclusion: hybrid wins 452 of 6300 calibrated scenarios, programmable a |
| `M-WORKLOAD-1` | `validated` | `high` | 2 | `physicalized-weights/docs/workload_trace_assumptions.md` | 8/8 | yes - verify evidence support in assigned slice | Validated Phase 2 M-WORKLOAD-1 after tightening the all-fallback control. The workload overlay preserves the safety/filter claim only for high-volume stable low-overhead traffic; weakens bursty, low-volume, and |
| `M-SWBASE-2` | `validated` | `high` | 2 | `physicalized-weights/scripts/stronger_baseline_model.py` | 7/7 | yes - verify evidence support in assigned slice | Validated Phase 2 M-SWBASE-2 after tightening the threshold mechanism reporting. The stronger programmable accelerator wins nine of ten workload scenarios, optimized software wins the zero-invocation control, a |
| `M-SYNTH-2` | `validated` | `high` | 2 | `plan_of_record.md` | 12/12 | yes - verify evidence support in assigned slice | Validated M-SYNTH-2 without additional code fixes. The Phase 2 synthesis consistently incorporates M-CAL-1, M-WORKLOAD-1, and M-SWBASE-2: programmable accelerator wins nine of ten workload scenarios, optimized  |
| `M-MEASURE-1` | `validated` | `high` | 3 | `plan_of_record.md` | 8/8 | yes - verify evidence support in assigned slice | Validated M-MEASURE-1 without code fixes. The cycle creates an auditable reopen evidence contract and deterministic local proxy harness while preserving the Phase 2 downgrade: local timing decomposes feature ex |
| `M-TRACE-1` | `validated` | `high` | 3 | `plan_of_record.md` | 10/10 | yes - verify evidence support in assigned slice | Validated M-TRACE-1 after tightening fast-path credit validation. The production trace contract now prevents incomplete telemetry, proxy-only energy, privacy-risk columns, missing baseline metrics, mixed policy |
| `M-REOPEN-1` | `validated` | `high` | 3 | `plan_of_record.md` | 9/9 | yes - verify evidence support in assigned slice | Validated M-REOPEN-1 without code fixes. The quantitative threshold model provides a stable measured-trace reopen contract for the Phase 2 downgrade: eight scenarios have finite positive threshold distances to  |
| `M-INGEST-1` | `validated` | `high` | 3 | `plan_of_record.md` | 8/8 | yes - verify evidence support in assigned slice | Validated M-INGEST-1 without code fixes. The trace-ingestion admissibility matrix preserves the M-TRACE-1 and M-REOPEN-1 measured-evidence contract: convenient proxy or synthetic sources cannot reopen the downg |
| `M-PIPELINE-1` | `validated` | `high` | 3 | `plan_of_record.md` | 11/11 | yes - verify evidence support in assigned slice | Validated M-PIPELINE-1 without source fixes. The composed reopen gate preserves the Phase 2 downgrade: privacy-risk traces are invalid, proxy/synthetic and insufficient ingestion paths are blocked, non-crossing |
| `M-EVIDENCEPACK-1` | `validated` | `high` | 3 | `plan_of_record.md` | 13/13 | yes - verify evidence support in assigned slice | Validated M-EVIDENCEPACK-1 after tightening threshold-scenario integrity. The replayable evidence-pack layer preserves the Phase 2 downgrade by rejecting stale hashes, missing attestations, schema mismatches, a |
| `M-PHASE3-SYNTH-1` | `validated` | `high` | 3 | `plan_of_record.md` | 10/10 | yes - verify evidence support in assigned slice | Validated the campaign-level Phase 3 reopen-pathway synthesis. No current artifact reopens the Phase 2 downgrade; synthetic, proxy/local, vendor-only, privacy-risk, stale-hash, unknown-threshold, and non-crossi |
| `M-ACQUIRE-1` | `validated` | `high` | 4 | `plan_of_record.md` | 9/9 | yes - verify evidence support in assigned slice | Validated M-ACQUIRE-1 after a targeted fixture/test correction. The readiness layer screens future shadow/canary acquisition designs before collection, keeps plans distinct from evidence, rejects or downgrades  |
| `M-DRYRUN-1` | `validated` | `high` | 4 | `plan_of_record.md` | 11/11 | yes - verify evidence support in assigned slice | Validated M-DRYRUN-1 after a targeted dry-run gate correction. The operator package layer now generates placeholder-safe manifest, trace, and attestation templates; blocks missing fields, raw content columns, u |
| `M-INTAKE-1` | `validated` | `high` | 4 | `plan_of_record.md` | 9/9 | yes - verify evidence support in assigned slice | Validated M-INTAKE-1 after a targeted handoff identity correction. The intake rehearsal now preserves trace_file as well as hash, source, ingestion path, measurement status, threshold mapping, provenance, priva |
| `M-UNCERTAINTY-1` | `validated` | `high` | 5 | `plan_of_record.md` | 8/8 | yes - verify evidence support in assigned slice | Validated M-UNCERTAINTY-1 after tightening high-correlation handling. The uncertainty layer now requires UCB_alpha(hybrid_total - best_programmable_total) < 0 in addition to existing Phase 3 evidence-package ga |
| `M-LIFECYCLE-1` | `validated` | `high` | 5 | `plan_of_record.md` | 8/8 | yes - verify evidence support in assigned slice | Validated M-LIFECYCLE-1 after tightening candidate accounting. The lifecycle composes acquisition readiness, dry-run, intake, evidence-pack replay, threshold, and uncertainty gates into deterministic terminal s |
| `M-PHASE4-SYNTH-1` | `validated` | `high` | 6 | `plan_of_record.md` | 10/10 | yes - verify evidence support in assigned slice | Validated M-PHASE4-SYNTH-1 after tightening manifest coverage. The final reopen-path synthesis refresh now folds acquisition readiness, operator dry-run, intake rehearsal, evidence-pack replay, uncertainty marg |
| `M-ROBUST-1` | `validated` | `high` | 7 | `plan_of_record.md` | 8/8 | yes - verify evidence support in assigned slice | Validated M-ROBUST-1 after tightening anti-target plausible-case consistency. The stress test covers eight target classes, preserves zero calibrated physicalized wins, keeps current_superiority_claim_count=0 an |
| `M-DEFER-1` | `validated` | `high` | 8 | `plan_of_record.md` | 8/8 | yes - verify evidence support in assigned slice | Completed the campaign deferral and future-evidence watchlist package. The package closes current claims under available evidence, keeps the Phase 4 reopen conjunction unchanged and inactive absent actual measu |
| `M-CLOSURE-1` | `validated` | `high` | 9 | `plan_of_record.md` | 11/11 | yes - verify evidence support in assigned slice | Completed the campaign-level closure and reader-facing final disposition report. The package consolidates the validated campaign endpoint without changing the Phase 4 condition, adding a reopen gate, or creatin |
| `M-ARCHIVE-1` | `validated` | `high` | 10 | `plan_of_record.md` | 8/8 | yes - verify evidence support in assigned slice | Completed the closure artifact archive and reproducibility index. The package maps curated canonical endpoint artifacts to milestone owner, artifact class, file size, SHA-256 hash, and regeneration command whil |
| `M-TOOLCHAIN-1` | `validated` | `high` | 11 | `plan_of_record.md` | 11/11 | yes - verify evidence support in assigned slice | Completed the toolchain condition probe and conditional prototype verification refresh. Local Verilator, Yosys, and Graphviz remain usable and refreshed checks pass; compiled Verilator simulation remains enviro |
| `M-INVARIANT-1` | `validated` | `high` | 12 | `physicalized-weights/scripts/campaign_invariant_checker.py` | 6/6 | yes - verify evidence support in assigned slice | Validated M-INVARIANT-1 after a targeted milestone-ownership correction. The checker now preserves canonical summary ownership while reporting contradiction_count=0, warning-level ambiguous prose only, zero cur |
| `M-PUBLICBASE-1` | `validated` | `high` | 13 | `physicalized-weights/scripts/public_baseline_recency_probe.py` | 7/7 | yes - verify evidence support in assigned slice | Validated M-PUBLICBASE-1 after a targeted source-table completeness correction. The public baseline recency probe now records structured source materiality fields, recommends only a future programmable-baseline |
| `M-PUBLICBASE-2` | `validated` | `high` | 14 | `plan_of_record.md` | 9/9 | yes - verify evidence support in assigned slice | Validated M-PUBLICBASE-2 without source-code fixes. The conservative MLPerf-to-campaign mapping ingests 12 primary MLCommons v6.0 rows from 520 available summary records, records 12 throughput-prior rows, recor |
| `M-PUBLICBASE-SYNTH-1` | `validated` | `high` | 15 | `plan_of_record.md` | 10/10 | yes - verify evidence support in assigned slice | Validated M-PUBLICBASE-SYNTH-1 without source-code fixes. The public programmable-baseline synthesis addendum correctly records MLPerf Inference v6.0 recency and the M-PUBLICBASE-2 primary MLCommons mapping as  |

## Initial Finding Classification

- CRITICAL: 0 identified in explore. No plan milestone is missing a terminal latest ledger event, and all latest ledger artifact paths for plan milestones exist on disk.
- MODERATE: 0 identified in explore. Verification still needs to check whether evidence contents support each terminal claim, especially post-closure public-baseline and invariant claims.
- MINOR: 1 logged. No filename-matched `CLOSURE`/`SUPERSEDES` documents exist despite closure milestones; this is a naming/organization gap only because closure artifacts are represented under lower-case milestone-specific docs and ledger events.

## Evidence Pointers By Report

- `reports/cycles/report_cycles_1-1.md`
- `reports/cycles/report_cycles_11-13.md`
- `reports/cycles/report_cycles_14-16.md`
- `reports/cycles/report_cycles_17-19.md`
- `reports/cycles/report_cycles_2-4.md`
- `reports/cycles/report_cycles_20-22.md`
- `reports/cycles/report_cycles_23-25.md`
- `reports/cycles/report_cycles_26-28.md`
- `reports/cycles/report_cycles_29-31.md`
- `reports/cycles/report_cycles_32-34.md`
- `reports/cycles/report_cycles_35-37.md`
- `reports/cycles/report_cycles_38-38.md`
- `reports/cycles/report_cycles_5-7.md`
- `reports/cycles/report_cycles_8-10.md`

