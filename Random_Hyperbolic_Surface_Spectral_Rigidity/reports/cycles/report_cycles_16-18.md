---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 16-18"
date: "2026-05-15"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 16-18

## Abstract

Cycles 16-18 completed three linked stages of the research campaign on Kim--Tao's random-cover spectral rigidity paper. Cycle 16 closed `M5-extension-candidates` by turning the validated Cycle 13-15 extension evidence into a precise toy principle: fixed conflict-free labelled-template expectations are analytically stable after normalization, while growing support/profile families can amplify Taylor coefficients and derivatives because product-ratio zeros and poles approach `x=0` at scale `1/L`. Cycle 17 completed `M6-final-synthesis`, producing the campaign's final report, claim ledger, file map, audit packet, and final figures. Cycle 18 opened a post-synthesis Phase II milestone, `M7-product-ratio-bounds`, and proved a deterministic product-ratio coefficient bound that formalizes the M5 mechanism at toy-model scope.

The main outcome is a validated research record plus one post-synthesis toy lemma. The campaign does not claim an improved Kim--Tao rigidity exponent, a reproof of imported MPvH/Nau/MP23 inputs, or a full hyperbolic trace theorem. The open bridge is now sharper: determine whether quotient/profile families in the actual Kim--Tao trace expansion can be compared to the product-ratio framework validated here.

## Introduction

The broader campaign has two goals: reconstruct Kim--Tao's proof architecture for eigenvalue rigidity and eigenfunction delocalization in random hyperbolic surface covers, then build toward credible extensions. Earlier cycles established the paper map, proof ledger, computational toy probes, and a certified finite labelled-template expectation identity. Cycles 13-15 then identified the Markov/interpolation bottleneck as the strongest extension path and showed, inside the finite labelled-template model, that fixed templates are stable but growing profiles amplify coefficients and derivatives.

Cycles 16-18 report on the transition from exploration to consolidation and then to a focused Phase II lemma. The key technical object is a normalized labelled-template expectation. For a conflict-free labelled directed template with `V` vertices and per-label constraint counts `C_a`, the M4 identity gives

```text
N_H(n) = n^{C-V} (n)_V / Product_a (n)_{C_a},
C = Sum_a C_a.
```

With `x=1/n`, this becomes a finite product ratio

```text
N_H(x) = Product_{j in A_H} (1 - jx) / Product_{j in B_H} (1 - jx).
```

The cycles covered here explain what the campaign can responsibly claim from that structure and what remains outside scope.

## Approach

The report follows the cycle order because the work itself was sequential:

1. Cycle 16 closed M5 by synthesizing candidate ranking, fixed-template expansion tests, and growing-template expansion data into one conservative toy principle.
2. Cycle 17 closed M6 by building the final campaign package and repairing one reproducibility wording issue found by audit.
3. Cycle 18 began Phase II by proving deterministic fixed-order coefficient and derivative envelopes for growing product ratios.

Source material came from the nine provided sessions, local artifacts, generated CSV files, figure metadata, `plan_of_record.md`, `promise_ledger.jsonl`, and `MANIFEST.md`. No `REFERENCES.md` exists in the workspace, so the references section lists local sources and session IDs rather than global numbered citations.

## Source Inventory and Timeline

| Cycle | Source ID | Role | What it contributed |
|---:|---|---|---|
| 16 | `2da92e16-78ed-4799-9c85-fb0caa544d95` | researcher | Directed M5 closure as a synthesis/toy-principle cycle. |
| 16 | `80f85bc7-44a8-40d5-9bac-81275cccf6d8` | worker | Built the M5 closure report, synthesis index, log-coefficient CSV, and fixed-versus-growing figure. |
| 16 | `5e808e23-706e-4680-b7dc-71c94ea2f6a4` | auditor | Validated M5 closure with no critical or moderate findings. |
| 17 | `37e022a8-a3e1-468d-9242-4b4c8b697d8f` | researcher | Directed M6 final synthesis after M1-M5 were validated. |
| 17 | `e0d27652-d844-4477-94d2-a04407620d0d` | worker | Built final report, claim ledger, artifact index, file map, audit packet, and final figures. |
| 17 | `c1490ed8-fcc2-42f5-bf85-5eade6eff26a` | auditor | Validated M6 after repairing stale Wolfram reproducibility wording. |
| 18 | `dd418053-e1a7-4691-a19d-27abf7bdc1cb` | researcher | Opened Phase II/M7 product-ratio coefficient bounds. |
| 18 | `6ca428ff-0199-4554-aa43-ced7d08f7005` | worker | Proved the product-ratio bounds and generated M7 script, data, tests, and figure. |
| 18 | `749edacb-777f-4b6e-8899-4f59fdc25f43` | auditor | Validated M7 with one minor scope clarification. |

The only gap in the record is bibliographic: no `REFERENCES.md` was present. The work in these cycles used local paper files and internal artifacts rather than new external sources.

## Findings

### Finding 1: Cycle 16 Closed M5 as a Toy Principle

Cycle 16 converted the validated M5 evidence into a single conservative statement:

```text
Fixed conflict-free labelled-template expectations are analytically stable
after normalization; growing support/profile size can force coefficient and
derivative amplification because product-ratio singularities drift toward
x=0 at scale 1/L.
```

The closure report `reports/extension_candidates/m5_extension_synthesis_and_toy_principle.md` states the M4 falling-factorial identity, explains the product-ratio form, and records the logarithmic identity

```text
log N_L(x)
  = Sum_{r>=1} ((Sum_{j in B_L} j^r - Sum_{j in A_L} j^r) / r) x^r.
```

This identity explains the Cycle 15 growth curves without relying on noisy fitted polynomials: if factors have indices up to `O(L)`, the sums of powers can grow polynomially in `L`.

![Fixed-template Taylor stability versus growing-template coefficient/derivative amplification and shrinking radius proxy.](reports/figures/m5_fixed_vs_growing_template_mechanism.png)

Cycle 16 generated:

- `reports/extension_candidates/m5_extension_synthesis_and_toy_principle.md`
- `scripts/plot_m5_extension_synthesis.py`
- `data/extension_candidates/m5_extension_synthesis_index.csv`
- `data/extension_candidates/m5_log_coefficient_summary.csv`
- `reports/figures/m5_fixed_vs_growing_template_mechanism.png`

The artifact index has 26 rows and zero missing dependencies. The log-coefficient summary has 792 rows. The figure is readable and nonblank at `2430 x 756` RGBA. The auditor independently spot-checked the log-coefficient formula for selected profiles and validated M5 closure.

### Finding 2: Cycle 17 Produced the Final Campaign Package

Cycle 17 moved from extension work to final synthesis. The final report `reports/final/final_report.md` records the whole campaign: Kim--Tao theorem map, Theorem 1 rigidity reconstruction, Theorem 2 delocalization reconstruction, computational probe ladder, M4 formal certification, M5 extension principle, failed routes, non-claims, and follow-up problems.

The final claim ledger classifies 17 claims into the required categories:

- `reconstructed`
- `certified`
- `proved_toy`
- `numerical_evidence`
- `conjectural`
- `negative_result`
- `non_claim`

The final artifact index has 61 rows, covers milestones M1-M6, and reports zero missing artifacts. The final file map tells future readers to start with `reports/final/final_report.md`, `data/final/final_claim_ledger.csv`, `data/final/final_artifact_index.csv`, and `audits/final/final_audit_packet.md`.

![Validated campaign ladder from paper reconstruction through proof ledgers, probes, certification, and extension benchmark.](reports/figures/final_campaign_evidence_ladder.png)

![Proof-side loss sources and evidence-side mechanism analogues, highlighting polynomial/interpolation derivative amplification.](reports/figures/final_bottleneck_map.png)

The Cycle 17 audit found one moderate issue: the worker package said Wolfram execution was blocked by license expiry, but the auditor successfully reran `wolfram-batch -script scripts/derive_labelled_embedding_expansions.wls`. The auditor repaired this wording in the final report, file map, audit packet, and final index builder. The final package now states that Wolfram is optional and environment-dependent, while Python validation paths are canonical for the final checks.

### Finding 3: Cycle 18 Formalized the Product-Ratio Mechanism

Cycle 18 opened Phase II with `M7-product-ratio-bounds`. This was the first post-synthesis follow-up recommended by the M6 audit: prove explicit coefficient and derivative bounds for the growing product ratios that had explained M5's toy mechanism.

The M7 report considers

```text
N_L(x) = Product_{a in A_L} (1 - ax) / Product_{b in B_L} (1 - bx),
```

where the support size and maximum index are both linear in `L`:

```text
max(A_L union B_L) <= C_0 L,
|A_L| + |B_L| <= C_1 L.
```

It proves three toy-model lemmas:

```text
[x^r] log N_L(x) = (Sum_{b in B_L} b^r - Sum_{a in A_L} a^r) / r,
```

```text
|[x^r] log N_L(x)| <= (C_1 C_0^r / r) L^{r+1},
```

and, for fixed `k`,

```text
|[x^k] N_L(x)| <= D_k L^{2k},
|N_L^{(k)}(0)| <= k! D_k L^{2k}.
```

The ordinary coefficient bound follows by writing `N_L(x)=exp(log N_L(x))` and expanding with the finite partition formula. A partition term for order `k` contributes at most `L^{k+m}`, where `m` is the number of parts and `m <= k`, giving the crude envelope `L^{2k}`.

![Observed fixed-order coefficient/log-coefficient growth for Cycle 15 families compared with deterministic L-power envelopes.](reports/figures/m7_product_ratio_bounds.png)

The M7 script generated 55 summary rows in `data/extension_candidates/product_ratio_bound_summary.csv`. Tests covered hand profiles, rank-two small cases, exact cancellation, parsing, and envelope-ratio sanity. The M7 figure is readable and nonblank at `2160 x 1440` RGBA.

The auditor validated the proof and implementation. The one minor note was interpretive: saying Cycle 15 families “fit inside this deterministic framework” means an existence-of-constant envelope, not that the unit envelope `L^{2k}` bounds every plotted value. This is consistent with the M7 report, which labels the bound crude and treats finite-window slopes as descriptive rather than asymptotic claims.

### Finding 4: The Scope Boundary Is Now Cleaner

The cycles sharpened the distinction between three levels of evidence.

First, M6 records the Kim--Tao proof reconstruction as a local proof-architecture and loss-ledger result. It does not reprove imported estimates such as MPvH embedding expansion, Nau boundedness, or MP23 rank-two fixed-point estimates.

Second, M5/M7 provide proved or certified toy-model results. The finite labelled-template identity is certified, the fixed-versus-growing product-ratio mechanism is exact in the toy model, and M7 proves deterministic coefficient envelopes for product ratios with linear support.

Third, the bridge to the actual Kim--Tao trace expansion remains conjectural. The main open question is whether quotient/profile families arising in the true random-cover trace expansion can be put into, or compared sharply with, the product-ratio framework.

## Discussion

Cycles 16-18 changed the state of the campaign from “validated exploration” to “audit-ready record plus Phase II lemma.” M5 is no longer an open extension search; it is a closed benchmark principle. M6 is no longer pending; it is a validated final synthesis package. M7 then extends the strongest follow-up into a standalone deterministic lemma.

The strongest technical narrative is now:

1. Kim--Tao's rigidity and delocalization proofs depend on polynomialized random-cover trace statistics and interpolation-type derivative control.
2. Fixed finite labelled templates do not explain derivative blowup after normalization; their product ratios are analytic at `x=0` with bounded fixed-order coefficients.
3. Growing support/profile families do explain amplification: zeros and poles move toward `x=0`, log coefficients become sums of powers over indices up to `O(L)`, and ordinary coefficients inherit growth through the exponential partition formula.
4. This is a toy benchmark, not a hyperbolic trace theorem.

This gives future work a concrete target. The next research step should not reopen M5, M6, or M7. It should test whether actual quotient families from Kim--Tao-relevant trace expansions satisfy hypotheses comparable to the M7 product-ratio setup, or identify where the comparison fails.

## Open Questions

1. Which quotient/profile families in the Kim--Tao trace expansion actually realize growing product-ratio structures?
2. Can the crude M7 envelope `O_k(L^{2k})` be sharpened for structured conflict-free families?
3. Are the cancellation cases seen in cycle and path profiles common in trace-relevant quotient families, or exceptional?
4. Can Markov/interpolation losses be improved under structural restrictions suggested by the labelled-template model?
5. What additional imported black-box reconstruction is needed before any theorem-level exponent improvement can be responsibly proposed?

## References

No `REFERENCES.md` file exists in the workspace. The report therefore cites local campaign sources and session IDs:

- Local paper files: `2603.01127.pdf`, `2603.01127.txt`.
- Cycle 16 sessions: `2da92e16-78ed-4799-9c85-fb0caa544d95`, `80f85bc7-44a8-40d5-9bac-81275cccf6d8`, `5e808e23-706e-4680-b7dc-71c94ea2f6a4`.
- Cycle 17 sessions: `37e022a8-a3e1-468d-9242-4b4c8b697d8f`, `e0d27652-d844-4477-94d2-a04407620d0d`, `c1490ed8-fcc2-42f5-bf85-5eade6eff26a`.
- Cycle 18 sessions: `dd418053-e1a7-4691-a19d-27abf7bdc1cb`, `6ca428ff-0199-4554-aa43-ced7d08f7005`, `749edacb-777f-4b6e-8899-4f59fdc25f43`.
- M5 synthesis: `reports/extension_candidates/m5_extension_synthesis_and_toy_principle.md`.
- M6 final package: `reports/final/final_report.md`, `reports/final/final_file_map.md`, `audits/final/final_audit_packet.md`, `data/final/final_artifact_index.csv`, `data/final/final_claim_ledger.csv`.
- M7 product-ratio bounds: `reports/extension_candidates/m7_product_ratio_coefficient_bounds.md`, `data/extension_candidates/product_ratio_bound_summary.csv`.

## Appendix: Implementation Details

Code organization after cycles 16-18 is recorded in `MANIFEST.md`, which was updated during this reporter pass. The current snapshot contains 18 campaign scripts with 4,254 total script lines, 9 test files with 646 total test lines, 27 canonical CSV datasets under `data/`, 24 PNG figures under `reports/figures/`, and 38 promise ledger events.

New or central cycle 16-18 files include:

| File | Lines / rows | Purpose |
|---|---:|---|
| `scripts/plot_m5_extension_synthesis.py` | 230 lines | Builds M5 synthesis index, log-coefficient data, and mechanism figure. |
| `reports/extension_candidates/m5_extension_synthesis_and_toy_principle.md` | 101 lines | M5 closure report and toy principle. |
| `data/extension_candidates/m5_extension_synthesis_index.csv` | 27 lines | M5 dependency index; 26 data rows. |
| `data/extension_candidates/m5_log_coefficient_summary.csv` | 793 lines | M5 log-coefficient data; 792 data rows. |
| `scripts/build_final_synthesis_index.py` | 207 lines | Builds final artifact and claim ledgers. |
| `scripts/plot_final_campaign_summary.py` | 186 lines | Builds final evidence and bottleneck figures. |
| `reports/final/final_report.md` | 246 lines | Standalone final campaign report. |
| `reports/final/final_file_map.md` | 52 lines | Final workspace guide. |
| `audits/final/final_audit_packet.md` | 60 lines | Final validation checklist and residual risks. |
| `data/final/final_artifact_index.csv` | 62 lines | Final artifact index; 61 data rows. |
| `data/final/final_claim_ledger.csv` | 18 lines | Final claim ledger; 17 data rows. |
| `scripts/analyze_product_ratio_bounds.py` | 237 lines | M7 product-ratio bound analysis. |
| `tests/test_product_ratio_bounds.py` | 70 lines | M7 regression tests. |
| `reports/extension_candidates/m7_product_ratio_coefficient_bounds.md` | 161 lines | M7 proof report. |
| `data/extension_candidates/product_ratio_bound_summary.csv` | 56 lines | M7 summary; 55 data rows. |

Figure metadata checked during this pass:

| Figure | Dimensions |
|---|---:|
| `reports/figures/m5_fixed_vs_growing_template_mechanism.png` | `2430 x 756` RGBA |
| `reports/figures/final_campaign_evidence_ladder.png` | `2160 x 1224` RGBA |
| `reports/figures/final_bottleneck_map.png` | `2160 x 1296` RGBA |
| `reports/figures/m7_product_ratio_bounds.png` | `2160 x 1440` RGBA |

Validation commands reported by cycle audits:

```bash
python3 -m py_compile scripts/plot_m5_extension_synthesis.py
python3 scripts/plot_m5_extension_synthesis.py
python3 -m py_compile scripts/build_final_synthesis_index.py scripts/plot_final_campaign_summary.py
python3 scripts/build_final_synthesis_index.py
python3 scripts/plot_final_campaign_summary.py
wolfram-batch -script scripts/derive_labelled_embedding_expansions.wls
python3 -m py_compile scripts/analyze_product_ratio_bounds.py tests/test_product_ratio_bounds.py
python3 scripts/analyze_product_ratio_bounds.py
python3 tests/test_product_ratio_bounds.py
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

Validation after the reporter manifest update:

```text
promise_check: exit 0; events: 38, plan milestones: 7; historical warnings only.
org_check: exit 0; historical root-file and docs-figure warnings only.
MANIFEST.md: 110 lines.
```

Known historical warnings remain: the root paper and prompt files are intentionally at workspace root, live-run root files remain from orchestration, one early ledger path references `docs/paper_map/` as a directory, historical cycle reports are not ledgered as primary artifacts, and older figures under `docs/` predate the later figure organization rule.

Cross-reference map for cycles 16-18:

| Origin | Consuming artifact | Role |
|---|---|---|
| Cycle 14 fixed-template expansions | Cycle 16 M5 synthesis | Supplies fixed-template stability evidence. |
| Cycle 15 growing-template expansions | Cycle 16 M5 synthesis | Supplies amplification and shrinking-radius evidence. |
| Cycle 16 M5 synthesis | Cycle 17 final report | Supplies the campaign's strongest new contribution. |
| Cycle 17 final report | Cycle 18 M7 brief | Identifies product-ratio coefficient bounds as the next follow-up. |
| `scripts/analyze_product_ratio_bounds.py` | `product_ratio_bound_summary.csv`, `m7_product_ratio_bounds.png` | Checks Cycle 15 families against M7 deterministic envelopes. |
| M7 audit | Future Phase II | Sets the next bridge problem: compare actual Kim--Tao quotient/profile families to the product-ratio framework. |
