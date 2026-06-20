# Final Audit Stage 7 - Verify 6/6

Stage: 7 of 14  
Slice: M7 and M8  
Expected file: `<run-root>/audits/final/stages/verify_6of6.md`  
Findings appended: 0

## Scope

This verify pass checked the final planned milestone slice from `audits/final/explore.md`:

- M7: Formal diagnostic, counterexample, or theorem template.
- M8: Final synthesis, audit, artifact index, and contribution ledger.

The check was limited to structured commitments and evidence: `promise_ledger.jsonl`, claimed artifacts, final deliverables, generated data/figure outputs, and runnable validation commands.

## M7 Verification

### Ledger Status

M7 has a complete in-progress to validated chain:

- `6968cd94-9eb7-4d4b-88d6-e442a1d0434f`: M7 opened as formal clique-expansion warning theorem/finite diagnostic.
- `f13162b0-2583-471c-8d4d-b6c073499961`: worker validated M7 with finite verifier, generated diagnostic outputs, formal report, and unittest validation.
- `ee864375-cda4-4aa3-9cf6-9d3b00ec3123`: auditor validated M7 after checking the proposition, finite pair-count examples, M6 family summary, generated CSV/JSON/PNG artifacts, ledger traceability, py_compile, unittest validation, deterministic verifier output, and best-effort validators.

Latest status: `validated`  
Latest confidence: `high`

### Artifact Existence

All ledger-listed M7 artifacts are present:

- `docs/formal_diagnostic.md`
- `scripts/verify_formal_diagnostic.py`
- `tests/test_formal_diagnostic.py`
- `data/formal_diagnostic/finite_examples.csv`
- `data/formal_diagnostic/m6_clique_diagnostic_summary.csv`
- `data/formal_diagnostic/formal_diagnostic_summary.json`
- `data/formal_diagnostic/clique_warning_diagnostic.png`

### Evidence Support

`docs/formal_diagnostic.md` contains the claimed formal diagnostic:

- Proposition: clique expansion of a role-labeled hyperedge with `k` taxon members creates `k(k - 1) / 2` unordered pairwise adjacencies.
- Safety condition: clique expansion is semantically safe only when every introduced pairwise adjacency is licensed by the hyperedge family's declared semantics.
- Proof sketch: native hyperedges can assert shared context without asserting mutual pairwise taxon similarity; role labels make reticulate cases sharper because child-source lineage credit does not license source-source similarity.
- M6 linkage: native hypergraph hierarchy distance `1.772727`, clique expansion `2.090909`, collapse-to-clique penalty `+0.318182`.
- Limitations: reticulate evidence is synthetic; the diagnostic is a semantic warning and finite counterexample template, not a broad biological or predictive superiority claim.

Frozen diagnostic output supports the document:

- `finite_examples.csv`: 8 finite examples:
  - `arity_0_empty_context`
  - `arity_1_singleton_context`
  - `arity_2_pairwise_trait_safe`
  - `arity_3_context_only`
  - `arity_5_context_only`
  - `regional_context_example`
  - `reticulate_role_example`
  - `trait_convergence_trap`
- `m6_clique_diagnostic_summary.csv`: 3 M6 family rows:
  - `regional_checklist_context`
  - `reticulate_or_hybrid_signal`
  - `trait_syndrome`
- `formal_diagnostic_summary.json` records:
  - `milestone`: `M7`
  - `finite_example_rows`: 8
  - `m6_family_rows`: 3
  - `m6_numeric_anchors`:
    - native hypergraph mean hierarchy distance: `1.772727`
    - clique expansion mean hierarchy distance: `2.090909`
    - collapsed native mean hierarchy distance: `2.090909`
    - collapse-to-clique distance delta: `0.318182`

### Tests Run

Commands run:

```bash
python3 -m py_compile scripts/verify_formal_diagnostic.py tests/test_formal_diagnostic.py scripts/generate_synthetic_benchmark.py scripts/build_public_taxonomy_sample.py scripts/run_synthetic_experiments.py tools/hierarchy_metrics.py tools/baselines.py tools/source_sample_checks.py
python3 -m unittest tests.test_formal_diagnostic -v
python3 -m unittest tests.test_synthetic_benchmark tests.test_hierarchy_metrics tests.test_public_taxonomy_sample tests.test_baselines tests.test_formal_diagnostic -v
python3 scripts/verify_formal_diagnostic.py --m6-diagnostic data/experiments/synthetic_v0.1/clique_false_similarity.csv --out-dir /tmp/m7_verify_stage7.<pid>
```

Observed results:

- `py_compile` passed for M7/M8-relevant scripts and tests.
- `tests.test_formal_diagnostic` passed 6 tests in 1.975s.
- Full M8-listed unittest suite passed 31 tests in 44.847s.
- Deterministic M7 verifier rerun wrote expected outputs:
  - `finite_examples.csv`
  - `m6_clique_diagnostic_summary.csv`
  - `formal_diagnostic_summary.json`
  - `clique_warning_diagnostic.png`

M7 verdict: `validated` / `high` is supported.

## M8 Verification

### Ledger Status

M8 has a complete in-progress to validated chain:

- `bbd51124-5d76-4a4f-9b5b-8338ec6bc436`: M8 opened for final synthesis, audit, artifact index, and contribution ledger.
- `5f5dbbfb-6052-4c5d-a5f9-2eab1e7fb9fd`: worker validated the four required M8 deliverables with traceable claims and explicit limitations.
- `4aa2726d-839d-4e82-b4cb-30d99c0f1a13`: worker validated py_compile, 31-test unittest suite, and promise_check with only documented nonblocking warnings.
- `05456048-f7cb-4426-922f-ef437b94a75a`: auditor validated the four root deliverables, claim classification, H1-H5 assessment, M6/M7 numeric anchors, figure references, reproduction commands, py_compile, 31-test unittest suite, promise_check, and org_check.

Latest status: `validated`  
Latest confidence: `high`

### Artifact Existence

All required M8 deliverables are present:

- `final_report.md`
- `artifact_index.md`
- `research_contribution_ledger.md`
- `audit_report.md`

### Evidence Support

`final_report.md` satisfies the required final-report contract:

- States the research question and gives a scoped final answer.
- Describes the evidence base for M1-M7.
- Describes methods and reproduction commands.
- Reports M6 results with numeric anchors:
  - test split `n=22`
  - structure-aware methods tied at `0.409091` flat and synonym-normalized exact match
  - native hypergraph best hierarchy distance `1.772727`
  - clique expansion hierarchy distance `2.090909`
  - tree/DAG and ordinary graph hierarchy distance `2.181818`
  - collapse-to-clique penalty `+0.318182`
- Separates claim categories:
  - validated claims
  - weakened or falsified claims
  - synthetic-only claims
  - public-data-limited claims
  - unsupported biological claims explicitly avoided
- Keeps biological claims scoped: no new plant taxonomy, corrected accepted names, species relationships, hybrid origins, trait syndromes, range claims, occurrence-quality conclusions, or phylogenetic novelty.

`artifact_index.md` satisfies the index contract:

- Lists datasets, scripts, figures, tests, reports, and reproduction commands for M1-M8.
- A strict inline-path check found 57 path-like entries. The only apparent missing entry was bare `predictions.csv` in a known nonblocking warning note; the actual indexed artifact exists at `data/experiments/synthetic_v0.1/predictions.csv`.
- The false positive was from audit parsing of prose, not a broken artifact reference.

`research_contribution_ledger.md` satisfies the contribution-ledger contract:

- Gives a terse M1-M8 ledger of artifacts and what each contributes.
- Distinguishes new/useful outputs from claims not proved.
- Correctly frames M6 as deterministic baseline/ablation evidence, not broad native-hypergraph predictive superiority.
- Correctly frames M7 as a clique-expansion warning diagnostic, not proof that clique expansion is always worse.

`audit_report.md` satisfies the audit-report contract:

- Lists missing or limited evidence:
  - no public reticulation evidence
  - no public trait evidence
  - no public occurrence provenance in the transformed sample
  - deterministic scoring baselines rather than optimized classifiers
  - small M6 test split
  - sparse missing-rank held-out coverage
- Lists failed/null results:
  - no flat exact accuracy gain for native hypergraph
  - remove-reticulate aggregate effect flat for native hypergraph
  - trait-edge ablations flat in M6
  - synonym-edge ablation flat while accepted-name randomization mattered
  - strict negative control did not disadvantage tree/DAG
- Lists unsupported biological claims avoided.
- Lists concrete next experiments.

### Tests Run

The M8 validation commands were exercised as part of this stage:

```bash
python3 -m py_compile scripts/generate_synthetic_benchmark.py scripts/build_public_taxonomy_sample.py scripts/run_synthetic_experiments.py scripts/verify_formal_diagnostic.py
python3 -m unittest tests.test_synthetic_benchmark tests.test_hierarchy_metrics tests.test_public_taxonomy_sample tests.test_baselines tests.test_formal_diagnostic -v
```

Observed results:

- Compilation passed.
- Full listed unittest suite passed 31 tests in 44.847s.

M8 verdict: `validated` / `high` is supported.

## Non-Findings And Audit-Script Corrections

Two audit-side checks produced non-findings:

- The first artifact-index parser treated a multiline fenced/prose block as a file path and failed with `OSError: [Errno 36] File name too long`. This was an audit-script error and was corrected with strict inline-token parsing.
- The corrected parser reported bare `predictions.csv` as missing, but that token appears only in a known warning note. The actual artifact is present at `data/experiments/synthetic_v0.1/predictions.csv` and is correctly referenced in the artifact index and ledger.

No CRITICAL, MODERATE, or actionable MINOR milestone finding was found in this slice.

## Findings Appended

0 findings appended to `<run-root>/audits/final/findings.jsonl`.

## Stage Result

M7 and M8 remain supported as `validated` / `high`.
