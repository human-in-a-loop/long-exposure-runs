# Verify Stage 1 of 5

Generated: 2026-05-13T17:03:42Z
Stage: 2 of 12 (verify 1/5)
Slice: `M-TAX-1`, `M-MODEL-1`, `M-BASE-1`, `M-TARGET-1`, `M-ARCH-1`, `M-PROTO-1`, `M-FINAL-1`

## Verification Method

- Read the explore-stage slice assignment from `audits/final/explore.md`.
- Re-read relevant ledger events in `promise_ledger.jsonl` for the slice, including earlier medium-confidence/in-progress events and later high-confidence validations.
- Inspected milestone documents and generated summaries for taxonomy, target ranking, architecture, prototype closure, and final synthesis.
- Checked generated CSV/JSON artifacts for row counts, schema fields, and claim-supporting summary values.
- Reran focused stdlib tests for the first-arc artifacts.

## Milestone Results

| Milestone | Verification result | Evidence checked |
|---|---|---|
| `M-TAX-1` | Supported. The taxonomy document enumerates physicalization levels, inference components, candidate/non-candidate mapping, non-physicalization baselines, strongest null hypothesis, and falsification criteria. | `physicalized-weights/docs/taxonomy_and_null.md`; ledger event `10cb3163-8c18-42d4-b489-5fa0b8ce6db1`. |
| `M-MODEL-1` | Supported. The break-even model artifacts exist; `breakeven_grid.csv` has 3,360 rows over parameterized request/update/software-savings axes; summary records six strategies and dominant variables. Focused test passed. | `breakeven_model.py`, `symbolic_breakeven.wls`, `breakeven_grid.csv`, `breakeven_summary.json`, `breakeven_update_volume.png`; `python3 physicalized-weights/tests/test_breakeven_model.py`. |
| `M-BASE-1` | Supported. The same model represents programmable unoptimized, software optimized, and programmable accelerator baselines, including software memory-savings sensitivity. | `breakeven_summary.json` strategies and winner counts; `breakeven_grid.csv` fields include `software_memory_savings`. |
| `M-TARGET-1` | Supported. Target scoring contains 10 candidates and 5 anti-targets; the report explicitly rejects full frontier dense weights, tenant fine-tunes, high-churn vocabulary heads, dynamic attention, and training state; focused test passed. | `target_ranking.md`, `target_scores.csv`, `target_scores_summary.json`, `target_score_heatmap.png`; `python3 physicalized-weights/tests/test_target_scoring.py`. |
| `M-ARCH-1` | Supported. Architecture note specifies host/RISC-V-compatible interface, register map, update/rollback paths, failure model, fallback/fail-safe invariants, and baseline demotion criteria; simulator summary covers 11 policy cases; focused test passed. | `hybrid_safety_filter_architecture.md`, `hybrid_arch_summary.json`, `hybrid_arch_policy_cases.csv`, `hybrid_safety_filter_arch.png`; `python3 physicalized-weights/tests/test_fallback_policy_sim.py`. |
| `M-PROTO-1` | Supported under its amended evidence contract. Prototype closure records `closure_status=validated`, Yosys/Python agreement, Verilator lint, Yosys synthesis, Graphviz presence, freshness checks, and compiled Verilator blocked by environment; focused closure test passed. | `prototype_verification_closure.json`, `prototype_equivalence_matrix.csv`, `yosys_safety_filter.log`, `safety_filter_core_netlist.png`; `python3 physicalized-weights/tests/test_prototype_verification_closure.py`. |
| `M-FINAL-1` | Partially supported with a MODERATE integrity defect. Current `final_synthesis.md` still answers the directive and preserves later downgrades, but the M-FINAL-1 manifest no longer has current hashes for files later edited by canonical synthesis/public-baseline updates. | `final_synthesis.md`, `final_synthesis_summary.json`, `evidence_manifest.csv/json`; failing `python3 physicalized-weights/tests/test_final_synthesis.py`. |

## Test Results

| Command | Result | Observed output |
|---|---|---|
| `python3 physicalized-weights/tests/test_breakeven_model.py` | PASS | exit 0, no output |
| `python3 physicalized-weights/tests/test_target_scoring.py` | PASS | exit 0, no output |
| `python3 physicalized-weights/tests/test_fallback_policy_sim.py` | PASS | exit 0, no output |
| `python3 physicalized-weights/tests/test_prototype_verification_closure.py` | PASS | six PASS lines including Yosys/Python agreement and structural evidence checks |
| `python3 physicalized-weights/tests/test_final_synthesis.py` | FAIL | fails in `test_artifact_hashes_are_current` after two earlier PASS lines |

## Findings Appended

- MODERATE `M-FINAL-1`: stale evidence-manifest hashes for `REFERENCES.md`, `physicalized-weights/docs/final_synthesis.md`, and `physicalized-weights/docs/reproducibility.md`. Appended to `audits/final/findings.jsonl`.

## Low/Provisional Confidence Review

- Earlier in-progress/medium events for `M-TAX-1`, `M-MODEL-1`, `M-BASE-1`, and `M-PROTO-1` were followed by high-confidence validated events in the same slice.
- No low or provisional terminal event exists for this slice.

## Residual Risk For Later Stages

- Later public-baseline/canonical synthesis milestones may intentionally supersede older M-FINAL-1 hashes. The document stage should decide whether this remains residual debt or should be reconciled as a supersession/freshness event.
