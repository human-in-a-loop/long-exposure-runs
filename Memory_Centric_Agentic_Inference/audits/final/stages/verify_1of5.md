# Final Audit Verify 1/5

Stage: 2 of 12, verify pass 1/5
Slice: M-TAX-1, M-LIFE-1, M-COST-1, M-SIM-1
Run id: run-2026-05-11T121649Z
Wall cap hit: false

## Method

This pass verified the first milestone slice assigned in `audits/final/explore.md`.
For each milestone, I checked the full ledger history, latest validated event,
evidence-file existence, artifact content against the plan success criteria,
and executable or generated-output evidence where applicable.

Commands and checks run from `<workspace>`:

- Searched plan, ledger, and cycle reports for the four milestone histories.
- Confirmed all ledger-listed artifacts for the slice exist on disk.
- Read primary narrative artifacts:
  - `memory-centric-agentic/taxonomy.md`
  - `memory-centric-agentic/lifetime_model.md`
  - `memory-centric-agentic/cost_model.md`
  - `memory-centric-agentic/simulator_design.md`
- Re-ran executable artifacts:
  - `wolfram-batch -script scripts/lifetime_model.wls`
  - `wolfram-batch -script scripts/cost_model.wls`
  - `python3 scripts/simulate_memory_policies.py`
  - `python3 scripts/plot_sim_policy_results.py`
  - `python3 scripts/plot_lifetime_regimes.py`
  - `python3 scripts/plot_cost_sensitivity.py`
- Ran a targeted CSV/PNG validation script for category counts, required fields,
  special cases, policy winners, proxy columns, and nonblank figure outputs.

`git status` could not be used because `<workspace>` is not a
Git repository. This is not a milestone defect; the audit uses on-disk artifacts
and the promise ledger as the source of record.

## Milestone Results

### M-TAX-1

Latest ledger state: `validated/high`, cycle 1, event
`96af6af9-bf1e-4daf-865e-aeed8fe592ae`.

Evidence checked:

- `memory-centric-agentic/taxonomy.md`
- `memory-centric-agentic/memory_objects.csv`
- `memory-centric-agentic/workload_classes.csv`
- `memory-centric-agentic/assumptions.md`
- `memory-centric-agentic/data/taxonomy_coverage.csv`
- `memory-centric-agentic/data/plot_taxonomy_coverage.py`
- `memory-centric-agentic/data/taxonomy_coverage.png`

Verification:

- The taxonomy defines 9 workload classes, exceeding the required minimum of 6.
- The object schema defines 11 memory object classes, exceeding the required
  minimum of 7.
- Object rows include size driver, mutability, reuse mode, placement candidates,
  and eviction failure mode fields.
- Workload rows include memory-centric hypotheses and falsification signals.
- The coverage table has 9 workload rows and 11 object columns, matching the
  workload/object artifacts, and no object column is unused.
- The coverage figure is present and nonblank (`1980 x 990` PNG).

Verdict-pending flag from explore: resolved for this pass.
Finding: none.

### M-LIFE-1

Latest ledger state: `validated/high`, cycle 2, event
`adbbe56c-7813-4e36-b1c0-e233e8873a2c`.

Evidence checked:

- `memory-centric-agentic/lifetime_model.md`
- `memory-centric-agentic/lifetime_parameters.csv`
- `scripts/lifetime_model.wls`
- `scripts/plot_lifetime_regimes.py`
- `data/lifetime_model_special_cases.csv`
- `data/lifetime_regime_grid.csv`
- `data/lifetime_regime_plot.png`

Verification:

- The narrative artifact defines equations for expected live bytes, retained
  value, capped KV growth, prefix reuse, branch state, and durable workspace
  growth.
- The parameter table covers the required object classes: weights, KV cache,
  prefix cache, retrieved context, tool output, branch state, verifier state,
  and durable workspace.
- The Wolfram script regenerated 9 special-case rows and a 144-row regime grid.
- Required special cases are present: context cap saturation, zero reuse
  (`lambda_equals_0`), infinite/pinned reuse, zero branch survival
  (`p_s_equals_0`), and zero durable growth (`g_d_equals_0`).
- The regime grid includes control collapse, branch-dominated, and
  durable-workspace-dominated regimes.
- The lifetime figure is present and nonblank (`1890 x 1530` PNG).

Verdict-pending flag from explore: resolved for this pass.
Finding: none.

### M-COST-1

Latest ledger state: `validated/high`, cycle 3, event
`8c78c632-cfbf-4b93-ad6d-f5ca3b9d476a`.

Evidence checked:

- `memory-centric-agentic/cost_model.md`
- `memory-centric-agentic/memory_tiers.csv`
- `memory-centric-agentic/cost_assumptions.md`
- `scripts/cost_model.wls`
- `scripts/plot_cost_sensitivity.py`
- `data/cost_model_special_cases.csv`
- `data/cost_model_scenarios.csv`
- `data/cost_model_sensitivity.csv`
- `data/cost_model_sensitivity.png`

Verification:

- The model defines total cost terms for residency, transfer, bandwidth delay,
  recompute, eviction loss, and staleness/correctness risk.
- The tier table includes 7 tiers: HBM/GPU memory, CPU DRAM, CXL/pooled memory,
  NVMe local, remote object store, durable workspace store, and semantic cache.
- The cost model explicitly labels tier constants as symbolic/synthetic and
  does not treat proxy values as measured hardware facts.
- The Wolfram script regenerated 10 special cases, 6 scenario rows, and 648
  sensitivity rows.
- Scenario rows include populated `energy_proxy_score`, `dollar_proxy_score`,
  `retained_value_score`, `dominant_cost_term`, `best_symbolic_tier_choice`,
  and `assumption_status` fields.
- The sensitivity figure is present and nonblank (`1440 x 936` PNG).

Verdict-pending flag from explore: resolved for this pass.
Finding: none.

### M-SIM-1

Latest ledger state: `validated/high`, cycle 4, event
`d591360d-c591-4ea0-a714-0a19eb828d59`, superseding the earlier cycle 4 worker
validation by documenting the auditor patch for cost proxy consumption.

Evidence checked:

- `memory-centric-agentic/simulator_design.md`
- `scripts/simulate_memory_policies.py`
- `scripts/plot_sim_policy_results.py`
- `data/sim_workload_events.csv`
- `data/sim_policy_results.csv`
- `data/sim_policy_object_breakdown.csv`
- `data/sim_special_cases.csv`
- `data/sim_policy_results.png`
- `data/sim_object_breakdown.png`

Verification:

- The simulator regenerated 215 workload events, 24 policy-result rows, 112
  object-breakdown rows, and 7 special-case rows.
- It compares 4 policies across 6 workload regimes, exceeding the required
  minimum of 3 policies and 3 regimes.
- Control winners are baseline as required:
  - `single-turn chat control`: `hbm_first_baseline`
  - `batch summarization/offline inference control`: `hbm_first_baseline`
- Agentic regimes select memory-centric policies where expected:
  - `RAG with retrieved-context reuse`: `reuse_aware_tiering`
  - code-agent, verification-heavy, and multi-agent branch/merge workloads:
    `branch_verifier_durable_aware`
- Policy result rows include populated energy and dollar proxy fields, matching
  the auditor repair described in the ledger and cycle 4 report.
- Both simulator figures are present and nonblank (`1920 x 1040` PNGs).

Verdict-pending flag from explore: resolved for this pass.
Finding: none.

## Low Or Provisional Confidence Review

No low-confidence or provisional events were found for this slice. The only
non-terminal events in the slice are ordinary `in-progress/medium` starts, each
followed by a later `validated/high` event. M-SIM-1 has two validated events in
cycle 4; the later auditor event is the controlling evidence because it records
the proxy-score consumption repair and revalidation.

## Findings Appended

None. No CRITICAL, MODERATE, or MINOR findings were identified in this verify
slice, so `audits/final/findings.jsonl` was left unchanged.

## Residual Items For Later Stages

- The global process markers noted in explore (`_run/start` and
  `_manager/validator-warnings`) are outside this milestone slice and remain for
  later test/document stages.
- This pass did not run the global `promise_check` or `org_check` validators;
  those are required by the test stages.

