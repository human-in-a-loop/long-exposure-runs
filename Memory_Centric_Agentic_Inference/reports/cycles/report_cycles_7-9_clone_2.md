---
title: "Memory-Centric Agentic Inference — cycles 7-9 clone 2"
date: "2026-05-11"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Memory-Centric Agentic Inference — cycles 7-9 clone 2

## Abstract

Cycles 7-9 moved clone 2 from a stable branch-level design into validated parent integration for `M-EXP-1`. The clone-2 artifact, `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md`, remained unchanged at 308 lines because previous cycles had already converged on the semantic-cache and durable-state risk measurement design. The new work was integration and governance: the parent measurement CSV harness now includes the clone-2 `DC-004` semantic-cache rows and `DC-003` durable-state rows, the relevant ledger events register the managed artifacts, and final validation is green.

The main outcome is that clone 2 is now validated at three levels: branch artifact, parent CSV ingestion, and parent/root artifact governance. The parent harness preserves the core mechanism boundary: Option B object reuse depends on safe valid semantic retained value, not raw semantic-cache hit rate; Option C durable replay depends on tail-safe durable replay value, not median durable read latency. The final audit for cycle 9 found one governance issue outside clone-2 design: two newly generated clone-0 report artifacts were unregistered. The auditor registered them in ledger event `523f4e76-04d4-4002-8000-000000000205`, after which `promise_check` and `org_check` passed.

## Introduction

The root project investigates whether future agentic LLM infrastructure should be organized around memory movement, placement, reuse, compression, and lifetime management rather than arithmetic throughput alone. Clone 2 owns one scoped part of that investigation: risk measurement for semantic caches and durable state.

The branch is tied to two deferred constants:

| Deferred constant | Scope | Architecture implication |
|---|---|---|
| `DC-004` | Semantic-cache correctness and invalidation cost | Option B for object reuse is valid only if approximate semantic reuse survives correctness, freshness, provenance, tenant/cache-salt isolation, poisoning, false-positive, and recovery checks. |
| `DC-003` | Durable object-store latency distributions for agent state | Option C for durable replay is valid only if workspace, checkpoint, summary-pointer, and trajectory replay paths avoid p50/p95/p99 tail costs that exceed retained value. |

Cycles 4-6 established that the branch-level design was stable. Cycles 7-9 answered the next integration question: whether that design had been ingested into the parent `M-EXP-1` measurement harness without being flattened into sibling work such as `DC-005` trajectory reuse or `DC-006` provenance overhead.

## Methodology

This report consolidates the supplied cycle records and workspace artifacts. It does not re-audit the results. The primary sources are the researcher, worker, and auditor sessions for cycles 7-9:

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 7 | `9fd22e4a-13f1-4956-9368-8b69db5bcccf` | `0bf02c53-b17d-4965-ab0f-66929ab69be6` | `4298f291-56c4-4289-a0ad-f06969257599` |
| 8 | `af2e8d75-4285-45ce-8aa1-71435cbc7fdf` | `2fd25556-71a0-4e2f-a380-dfd5dc23734c` | `56395283-f193-4aed-91fb-b61c63cef985` |
| 9 | `f2f1153d-6ec0-45d2-adb3-53460fd9d226` | `17fb7767-6b8e-4b2f-9668-995218167f51` | `3b20c8ca-e982-4977-91e5-617c4c00bf10` |

The current workspace was also inspected for the stable artifact, parent measurement CSVs, references, figures, and validation state. No clone-2-specific figures were produced in cycles 7-9, so no figures are embedded in this report.

## Results

### Cycle 7: Parent CSV Ingestion

Cycle 7 converted clone 2 from stable design input into parent measurement-harness content.

The researcher session `9fd22e4a-13f1-4956-9368-8b69db5bcccf` stated that no new branch artifact work was needed. Instead, it identified the active task as parent `M-EXP-1` integration. The sufficiency criteria were concrete: all 11 CDR experiment rows, all 10 CDR thresholds, nonempty instrumentation fields, claim-update links, and downgrade semantics had to appear in the parent CSV harness.

The worker session `0bf02c53-b17d-4965-ab0f-66929ab69be6` patched the parent harness files:

- `data/measurement_experiment_specs.csv`
- `data/measurement_required_fields.csv`
- `data/measurement_thresholds.csv`
- `data/measurement_claim_update_matrix.csv`
- `data/measurement_synthetic_probe_results.csv`
- `promise_ledger.jsonl`

The worker did not edit `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md`.

The worker’s coverage probe reported 11 CDR experiment rows, 10 CDR threshold rows, 6 `DC-004` rows, 5 `DC-003` rows, no empty CDR instrumentation rows, and claim links for `CL-002`, `CL-003`, `CL-006`, `CL-008`, `CL-009`, and `CL-010`.

The auditor session `4298f291-56c4-4289-a0ad-f06969257599` validated the integration. It noted that the parent schema uses `required_instrumentation`, while some session language referred to `instrumentation_fields`; the auditor treated this as a naming mismatch only, because the populated column carried the required meaning. The same audit confirmed ledger event `523f4e76-04d4-4002-8000-000000000202` as the registered event for the five measurement CSV artifacts.

### Cycle 8: Root Artifact Governance Cleanup

Cycle 8 moved from clone-2 ingestion to parent/root hygiene.

The researcher session `af2e8d75-4285-45ce-8aa1-71435cbc7fdf` stated that clone 2 was complete at both artifact and parent-ingestion levels. The remaining active issue was not design correctness; it was resolving or ledger-documenting orphan managed-path artifacts outside clone-2 scope.

The worker session `2fd25556-71a0-4e2f-a380-dfd5dc23734c` registered remaining parent/root artifacts in `promise_ledger.jsonl`:

- `523f4e76-04d4-4002-8000-000000000203`: DC-005 merge-readiness verifier and result CSV.
- `523f4e76-04d4-4002-8000-000000000204`: fanout cycle reports for clone 0 and clone 2.

The worker also ran `tests/verify_dc005_merge_ready.py`, compiled that verifier, and reran the repository checks. The reported result was `promise_check` green, `org_check` green, and a passing DC-005 verifier.

The auditor session `56395283-f193-4aed-91fb-b61c63cef985` validated the cleanup. It confirmed that the remaining governance warnings had been resolved, that clone-2 rows were still intact, and that `DC-003`/`DC-004` stayed separate from sibling `DC-005`/`DC-006` scope.

### Cycle 9: Closure Confirmation and Final Governance Fix

Cycle 9 reconfirmed that clone 2 was fully converged.

The researcher session `f2f1153d-6ec0-45d2-adb3-53460fd9d226` stated that clone 2 was validated at branch artifact, parent CSV ingestion, and parent/root artifact-governance levels. It recommended no clone-2 build work, and directed future effort to parent `M-EXP-1` synthesis only.

The worker session `17fb7767-6b8e-4b2f-9668-995218167f51` performed no build work and did not edit the clone artifact. It reran `promise_check`, `org_check`, and a targeted CDR preservation probe. The reported preservation state remained 11 CDR experiment rows, 10 thresholds, 6 `DC-004` rows, 5 `DC-003` rows, and no empty `required_instrumentation` rows.

The auditor session `3b20c8ca-e982-4977-91e5-617c4c00bf10` found one moderate issue, then fixed it. The worker had reported `promise_check` green, but an independent auditor run found two newly generated clone-0 report artifacts that were not ledger-registered:

- `reports/cycles/report_cycles_7-9_clone_0.md`
- `reports/cycles/report_cycles_7-9_clone_0.pdf`

The auditor registered those artifacts in ledger event `523f4e76-04d4-4002-8000-000000000205`. After that, `promise_check` reported 67 events, 14 plan milestones, and green status. `org_check` also passed. The same audit reconfirmed that all CDR rows and thresholds were present, semantic terms were intact, durable terms were intact, and no critical or moderate clone-2 issues remained.

## Integrated Measurement Design

The stable branch artifact remains `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md`. It is a 308-line measurement design for deciding when semantic reuse or durable replay is safe enough to support memory-centric architecture options.

### DC-004: Semantic-Cache Risk

The semantic-cache side measures whether approximate reuse is safe after correctness and security checks. The central quantity is safe semantic retained value:

$$
V_{\text{semantic safe}} =
P_{\text{hit}} \cdot P_{\text{valid}\mid\text{hit}} \cdot C_{\text{recompute avoided}}
- C_{\text{lookup}}
- C_{\text{validation}}
- C_{\text{invalidation}}
- C_{\text{recovery}}
- E[C_{\text{wrong reuse}}]
$$

The parent harness now includes six `DC-004` experiment rows:

| ID | Measurement purpose |
|---|---|
| `CDR-SEM-001` | Raw semantic hit rate versus valid-hit rate. |
| `CDR-SEM-002` | Semantic false-positive rate by match-score bucket. |
| `CDR-SEM-003` | Stale-hit rate after source-version and invalidation changes. |
| `CDR-SEM-004` | Safe hit rate after tenant-scope and cache-salt enforcement. |
| `CDR-SEM-005` | Recovery latency and action after invalid cache hit. |
| `CDR-SEM-006` | Poisoning or untrusted-provenance rejection rate. |

The corresponding thresholds are `T-SEM-VALID-001`, `T-SEM-STALE-002`, `T-SEM-ISOLATION-003`, `T-SEM-POISON-004`, and `T-SEM-RECOVERY-005`.

The interpretation preserved through cycles 7-9 is that Option B is not justified by raw hit rate. It requires positive safe value after correctness labels, freshness checks, provenance, tenant/cache-salt isolation, poisoning rejection, validation cost, invalidation cost, recovery cost, and wrong-reuse severity.

### DC-003: Durable-State Replay Risk

The durable-state side measures whether remote or persistent replay is fast and valid enough to support Option C. The branch artifact defines durable replay value as:

$$
V_{\text{durable replay}} =
P_{\text{replay}} \cdot C_{\text{recompute avoided}}
- L_{\text{store read}}(p)
- L_{\text{consistency}}(p)
- C_{\text{pointer validation}}
- C_{\text{reconstruction}}
- E[C_{\text{replay failure}}]
$$

The percentile variable $p$ must include p50, p95, and p99 because long agentic runs can be blocked by the slowest required replay object. Durable replay is therefore not a median-latency claim.

The parent harness now includes five `DC-003` experiment rows:

| ID | Measurement purpose |
|---|---|
| `CDR-DUR-001` | Durable workspace read/write p50, p95, and p99 by size and consistency mode. |
| `CDR-DUR-002` | Dependency-path maximum replay latency under fan-in. |
| `CDR-DUR-003` | Summary-pointer recovery latency and validity. |
| `CDR-DUR-004` | Retention-horizon and hold-state violations. |
| `CDR-DUR-005` | Replay success rate under object-store tail injection. |

The corresponding thresholds are `T-DUR-TAIL-001`, `T-DUR-P99-002`, `T-DUR-FANIN-003`, `T-DUR-RECOVERY-004`, and `T-DUR-RETENTION-005`.

The interpretation preserved through cycles 7-9 is that Option C is not justified by median durable read latency. It requires replay value to survive p95/p99 tails, dependency fan-in, consistency wait, pointer validity, reconstruction latency, retention state, authorization, and replay-failure risk.

## Validation and Governance Status

By the end of cycle 9, clone 2 had passed the relevant validation checks at all required levels.

| Layer | Status | Evidence |
|---|---|---|
| Branch artifact | Validated | `cache_durable_risk_measurement_plan.md` remained stable at 308 lines. |
| Parent CSV ingestion | Validated | All 11 CDR experiments, all 10 thresholds, required fields, claim links, and synthetic probes were present. |
| Root artifact governance | Validated | Ledger events `...000000000202`, `...203`, `...204`, and `...205` registered the relevant managed artifacts. |
| Repository checks | Validated | Final `promise_check` reported 67 events, 14 plan milestones, and green status; `org_check` was green. |

The cycle 9 audit explicitly fixed the only newly surfaced moderate issue: unregistered clone-0 cycle 7-9 report artifacts. That issue was outside clone-2 design and outside CDR ingestion, but it affected root governance. After event `523f4e76-04d4-4002-8000-000000000205`, no critical or moderate clone-2 issues remained.

## Discussion

Cycles 7-9 changed the status of clone 2 from “validated design input” to “validated parent-ingested measurement branch.”

The most important technical preservation is the mechanism boundary. The branch remains about risk-gated reuse:

- Semantic-cache reuse is credited only when valid-hit retained value remains positive after safety and recovery costs.
- Durable-state replay is credited only when replay retained value remains positive after tail latency, fan-in, pointer, consistency, reconstruction, retention, and failure penalties.

This boundary matters because raw reuse signals can overstate memory-centric value. A semantic cache with high hit rate can still be unsafe if hits are stale, poisoned, cross-tenant, or expensive to validate. A durable object store with good median reads can still be unsuitable for Option C if p99 replay tails miss verifier or merge deadlines. The cycles 7-9 integration preserved those distinctions in machine-readable parent CSV rows rather than leaving them only in prose.

The work also clarified ownership. Clone 2 does not own DC-005 trajectory reuse, DC-006 provenance overhead, or full parent synthesis. It supplies stable `DC-003` and `DC-004` evidence for parent `M-EXP-1`.

## Conclusions and Recommendations

Clone 2 should be treated as closed unless a future parent audit finds a concrete regression in CDR rows, thresholds, fields, or downgrade semantics.

The parent/root synthesis should use registered CDR integration event `523f4e76-04d4-4002-8000-000000000202`. It should not cite the earlier absent event `523f4e76-04d4-4002-8000-000000000002`.

Future parent synthesis should preserve these rules:

- Option B requires safe valid semantic retained value, not raw semantic hit rate.
- Option C requires tail-safe durable replay value, not median durable read latency.
- `DC-003` and `DC-004` must remain separate from sibling `DC-005` and `DC-006` scope.
- Unsafe reuse should downgrade or forbid the architecture option rather than count as a degraded success case.

## References

[6] NVM Express, "Specifications," NVM Express, accessed 2026-05-11. https://nvmexpress.org/specifications/

[12] vLLM Project, "Automatic Prefix Caching," vLLM Documentation, accessed 2026-05-11. https://docs.vllm.ai/en/latest/design/prefix_caching/

[13] Sajal Regmi and Chetan Phakami Pun, "GPT Semantic Cache: Reducing LLM Costs and Latency via Semantic Embedding Caching," arXiv, 2024. https://arxiv.org/abs/2411.05276

## Appendix: Implementation Details

### Code and Artifact Organization

The required clone-2 artifact is:

| File | Lines | Purpose |
|---|---:|---|
| `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md` | 308 | Validated measurement design for `DC-004` semantic-cache correctness/invalidation risk and `DC-003` durable replay-tail risk. |

The parent measurement CSVs after cycles 7-9 are:

| File | Lines | Cycle 7-9 role |
|---|---:|---|
| `data/measurement_experiment_specs.csv` | 19 | Contains DC-005 rows plus 6 `CDR-SEM-*` and 5 `CDR-DUR-*` rows. |
| `data/measurement_required_fields.csv` | 23 | Contains DC-005 required fields plus clone-2 semantic-cache and durable-state gates. |
| `data/measurement_thresholds.csv` | 15 | Contains DC-005 thresholds plus 5 `T-SEM-*` and 5 `T-DUR-*` thresholds. |
| `data/measurement_claim_update_matrix.csv` | 23 | Maps clone-2 evidence to `CL-002`, `CL-003`, `CL-006`, `CL-008`, `CL-009`, and `CL-010`. |
| `data/measurement_synthetic_probe_results.csv` | 13 | Contains semantic-cache failure probes and durable replay-tail probes. |

The workspace contains 25 Python scripts, 4 Wolfram scripts, and 7,376 total script lines. The broader project contains 29 figures, but none were generated specifically for clone-2 cycles 7-9.

### Validation Commands

The reporter pass reran the repository checks after updating `MANIFEST.md`:

```bash
python3 -m long_exposure.tools.promise_check <workspace>
python3 -m long_exposure.tools.org_check <workspace>
```

Results:

```text
events: 67, plan milestones: 14
OK: promise_check green.
```

```text
root files: 5, root dirs: 10; standard folders present: ['audits', 'data', 'docs', 'reports', 'scripts', 'stale', 'tests', 'tools']
OK: org_check green.
```

A `git diff` command was attempted for manifest review, but `<workspace>` is not a Git repository. This did not affect validation; both project checks passed after the manifest update.

### Manifest Update

`MANIFEST.md` was updated as a workspace snapshot. The update changed the snapshot description from the prior DC-005 terminal handoff state to the clone-2 cycles 7-9 DC-003/DC-004 parent-ingestion and validation state. It also updated the line counts and purposes for the five parent measurement CSVs, and added cross-references from `cache_durable_risk_measurement_plan.md` into the parent experiment, threshold, required-field, and claim-update CSVs.

No `## Key Files` preservation section was present in the manifest, so no protected section needed to be preserved.

### Session Reference Map

| Session | Role in report |
|---|---|
| `9fd22e4a-13f1-4956-9368-8b69db5bcccf` | Cycle 7 researcher brief defining parent CDR integration sufficiency criteria. |
| `0bf02c53-b17d-4965-ab0f-66929ab69be6` | Cycle 7 worker output for parent CSV ingestion and CDR coverage probe. |
| `4298f291-56c4-4289-a0ad-f06969257599` | Cycle 7 audit validating parent CSV ingestion and noting remaining non-clone orphan warnings. |
| `af2e8d75-4285-45ce-8aa1-71435cbc7fdf` | Cycle 8 researcher brief shifting active work to root artifact governance. |
| `2fd25556-71a0-4e2f-a380-dfd5dc23734c` | Cycle 8 worker output registering DC-005 verifier artifacts and fanout report artifacts. |
| `56395283-f193-4aed-91fb-b61c63cef985` | Cycle 8 audit validating root governance cleanup and clone-2 preservation. |
| `f2f1153d-6ec0-45d2-adb3-53460fd9d226` | Cycle 9 researcher brief declaring clone-2 fully converged. |
| `17fb7767-6b8e-4b2f-9668-995218167f51` | Cycle 9 worker output rerunning green checks and CDR preservation probe. |
| `3b20c8ca-e982-4977-91e5-617c4c00bf10` | Cycle 9 audit fixing clone-0 report artifact registration and issuing final validation. |

### Cross-Reference Map

| Origin | Consuming artifact | Flow |
|---|---|---|
| `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md` | `data/measurement_experiment_specs.csv` | `CDR-SEM-*` and `CDR-DUR-*` measurement designs become parent `M-EXP-1` experiment rows. |
| `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md` | `data/measurement_required_fields.csv` | Semantic-cache and durable-state instrumentation gates become required parent fields. |
| `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md` | `data/measurement_thresholds.csv` | `T-SEM-*` and `T-DUR-*` downgrade/forbid rules become parent thresholds. |
| `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md` | `data/measurement_claim_update_matrix.csv` | Clone-2 evidence updates claims `CL-002`, `CL-003`, `CL-006`, `CL-008`, `CL-009`, and `CL-010`. |
| `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md` | `data/measurement_synthetic_probe_results.csv` | Semantic-cache false-positive/stale/recovery probes and durable tail/pointer/retention probes become synthetic mechanism checks. |
| `promise_ledger.jsonl` event `523f4e76-04d4-4002-8000-000000000202` | Parent `M-EXP-1` governance | Registers the five CDR measurement CSV artifacts. |
| `promise_ledger.jsonl` event `523f4e76-04d4-4002-8000-000000000205` | Final cycle 9 validation | Registers newly surfaced clone-0 cycle 7-9 report artifacts, restoring green `promise_check`. |
