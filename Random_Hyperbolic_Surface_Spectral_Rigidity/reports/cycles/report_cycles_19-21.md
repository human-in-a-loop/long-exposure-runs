---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 19-21"
date: "2026-05-16"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 19-21

## Abstract

Cycles 19-21 moved the campaign from a validated per-template product-ratio lemma to the first explicit aggregate bridge tests. In this report, a **product-ratio template** means a normalized factor of the form
\[
N_L(x)=\frac{\prod_{a\in A_L}(1-a x)}{\prod_{b\in B_L}(1-b x)}
\]
used in earlier cycles to model falling-factorial expectation terms. M7 had shown that individual templates with support and indices growing linearly in \(L\) have fixed-order coefficient and derivative envelopes. The central question for cycles 19-21 was whether that termwise control can connect to the actual quotient-family sums in Kim--Tao's trace and pre-trace arguments.

The answer is now precise and conservative. Cycle 19, M8, produced a bridge taxonomy and then repaired it under audit: M4/M7 exactly cover the independent-permutation labelled-template baseline, but Kim--Tao's surface-group random-cover expectations are only partially covered because they require MPvH/Witten-zeta/Nau/MP23 machinery. Cycle 20, M9, proved the aggregate obstruction: per-template bounds imply only a bound proportional to total weight or family count, so polynomial aggregate control requires additional count, weight, cancellation, or rank-sensitive decay input. Cycle 21, M10, built the first explicit restricted folded two-word aggregate model. It showed that folding reduces raw ordered-pair complexity, but conflict-free canonical profiles and multiplicities still grow quickly through \(L=4\), so measured family-count control remains the active bridge input.

All three milestones were validated. `MANIFEST.md` was updated after this reporter pass to include M8-M10.

## Introduction

The original campaign goal is to understand Kim and Tao's paper, "Eigenvalue rigidity of hyperbolic surfaces in the random cover model," and then search for credible extensions. Earlier work completed the paper map, proof ledger, computational probes, formal labelled-template identity, extension-candidate synthesis, final campaign package, and the M7 product-ratio coefficient lemma.

Cycles 19-21 continue that post-synthesis Phase II. The question was no longer whether individual product-ratio templates can have controlled fixed-order coefficients. M7 already answered that in a toy setting. The new question was whether those individual controls can become a theorem about Kim--Tao's quotient-family sums, where trace statistics are expanded over folded word graphs, cyclic or diagonal terms, rank-two remainders, geometry weights, and surface-group random-cover probability laws.

The report follows the work in order:

1. Cycle 19, M8: classify where the product-ratio framework attaches to Kim--Tao quotient/profile objects.
2. Cycle 20, M9: prove what per-template bounds do and do not imply after summing over a family.
3. Cycle 21, M10: enumerate a restricted folded two-word aggregate model to measure the missing family-count input.

## Approach

The cycles used a staged bridge strategy.

First, M8 compared the existing product-ratio framework with the proof objects in the Theorem 1 variance pipeline and Theorem 2 fourth-moment pipeline. The table `data/extension_candidates/quotient_family_bridge_table.csv` classified objects as `covered`, `partially_covered`, `heuristic_only`, or `not_covered`.

Second, M9 separated termwise control from aggregate control. If each template satisfies
\[
|[x^k]N_T(x)| \le C_k L^{2k},
\]
then for a weighted family
\[
A_L(x)=\sum_T w_T N_T(x)
\]
the only universal conclusion is
\[
|[x^k]A_L(x)|\le C_k L^{2k}\sum_T |w_T|.
\]
The new factor \(\sum_T |w_T|\) is the aggregate total variation. M9 then used deterministic examples to show why this factor cannot be ignored.

Third, M10 tested one restricted aggregate model: ordered pairs of reduced free-group words over `a,A,b,B`, folded and canonicalized as simultaneous fixed-point constraints with a shared basepoint. This model is not Kim--Tao's surface-group law. Its purpose was to measure whether folding and rank filtering visibly control multiplicities in a small auditable family.

## Source Inventory and Timeline

The primary source records for this report are the nine listed cycle sessions plus the supplied M10 audit report.

| Cycle | Session ID | Role | Date | Contents |
|---:|---|---|---|---|
| 19 | `6cd30b3c-9101-450d-b436-e3dd68fa5a02` | researcher | 2026-05-15 | Directed M8: classify the product-ratio bridge to Kim--Tao quotient/profile trace-expansion objects. |
| 19 | `f90d3574-c185-47a6-b8a5-2838180c2a4a` | worker | 2026-05-15 | Built M8 report, taxonomy table, script, test, figure, and ledger updates. |
| 19 | `ce53f519-2bfd-4914-ba46-19319a54cc36` | auditor | 2026-05-15 | Found and repaired an M8 overclaim; validated the corrected bridge taxonomy. |
| 20 | `05c0df1b-8b1c-4f86-858c-6949719faf81` | researcher | 2026-05-15 | Directed M9: formalize the aggregate obstruction left by M8. |
| 20 | `7f497bcb-54f7-4c43-aca6-0afd27c230bf` | worker | 2026-05-15 | Built M9 theorem report, generator, data tables, test, figure, and ledger updates. |
| 20 | `c394d1de-bc4c-46da-ab2b-cf1e8c9e0072` | auditor | 2026-05-15 | Validated M9 with no critical or moderate findings. |
| 21 | `048aad7d-9415-4f29-ac97-3c7aa87499ff` | researcher | 2026-05-15 | Directed M10: enumerate a restricted two-word folded quotient aggregate model. |
| 21 | `a5d07325-c571-4e6a-87fc-78b81c6b7c4c` | worker | 2026-05-15 | Built M10 enumerator, profiles, summaries, figures, report, test, and ledger updates. |
| 21 | `0dd6b24a-d5e6-43a6-8985-731a55a4f82b` | auditor | 2026-05-15 | Validated M10 and recorded two minor scope notes. |

The reporter pass also read the main artifacts:

- `reports/extension_candidates/m8_quotient_family_bridge.md`
- `reports/extension_candidates/m9_aggregate_obstruction_and_enumeration.md`
- `reports/extension_candidates/m10_restricted_quotient_aggregate.md`
- `data/extension_candidates/quotient_family_bridge_table.csv`
- `data/extension_candidates/aggregate_product_ratio_obstruction.csv`
- `data/extension_candidates/aggregate_bridge_requirements.csv`
- `data/extension_candidates/restricted_quotient_family_profiles.csv`
- `data/extension_candidates/restricted_quotient_aggregate_summary.csv`
- `plan_of_record.md`
- `promise_ledger.jsonl`
- `MANIFEST.md`

There is no `REFERENCES.md` in the workspace, so this report's References section lists local sources and session IDs rather than global numbered citations.

## Findings

### Finding 1: Cycle 19 Narrowed the Bridge to a Partial Bridge

M8 asked where the M4/M7 labelled-template product-ratio framework attaches to Kim--Tao's trace-expansion objects. The original worker output treated some single Kim--Tao folded quotient expectations as exactly covered by M4. The Cycle 19 auditor found that this was too strong. M4 certifies independent uniform-permutation templates, while Kim--Tao's random-cover model averages over \(\mathrm{Hom}(\Gamma,S_n)\), requiring MPvH/Witten-zeta/Nau/MP23 inputs even before aggregate summation.

The audit repair changed the M8 conclusion. Exact coverage is now reserved for the independent-permutation baseline. Kim--Tao quotient objects are only partially covered: they may share the same labelled constraint skeleton or exposed falling-factorial profile, but the surface-group law, denominator normalization, boundedness, rank-sensitive decay, geometry weights, centering, and summation are external.

The repaired bridge table has 11 rows:

| Bridge status | Rows | Meaning |
|---|---:|---|
| `covered` | 1 | Exact independent-permutation M4/M7 baseline. |
| `partially_covered` | 7 | Same skeleton or product-ratio profile appears, but Kim--Tao-level inputs remain outside M7. |
| `heuristic_only` | 2 | Product-ratio language matches the shape, but the decisive bound is imported aggregate machinery. |
| `not_covered` | 1 | Full MPvH/MP23 polynomial-method estimates are not derived from product-ratio envelopes. |

![Taxonomy of where the product-ratio framework attaches to Kim--Tao quotient/profile objects and where additional trace-expansion structure enters.](reports/figures/m8_bridge_taxonomy.png)

The validated M8 report states the strongest bridge as conditional. If a Kim--Tao trace or pre-trace polynomial can be decomposed into geometry-weighted conflict-free folded quotient templates with exposed falling-factorial profiles, then M7 gives fixed-order coefficient envelopes termwise after the product-ratio form has been isolated. To reach Proposition 3.1 or Proposition 4.2 level estimates, additional aggregate control is still required.

### Finding 2: Cycle 20 Proved the Aggregate Obstruction

M9 formalized the missing step identified by M8. The result is a simple but decisive lemma: if each template is controlled by M7 and the aggregate has weights \(w_T\), then the coefficient of the sum is bounded by the per-template envelope multiplied by total variation:
\[
|[x^k]\sum_T w_T N_T(x)| \le C_k L^{2k}\sum_T |w_T|.
\]

This proves that per-template control alone is not an aggregate theorem. Polynomial aggregate control requires at least one extra input:

- polynomial family-count control;
- polynomial total variation of weights;
- coefficient-level cancellation;
- rank-sensitive or probability-law decay;
- denominator and boundedness control.

The deterministic examples in M9 used the path profile \(N_L(x)=1-Lx\). At \(L=40\), the generated examples recorded:

| Family | Aggregate coefficient | Total variation | Interpretation |
|---|---:|---:|---|
| `single_template_path` | `-40` | `1` | Termwise M7 control. |
| `polynomial_count_path` | `-64000` | `1600` | Polynomially many copies remain polynomial. |
| `exponential_count_path` | `-43980465111040` | `1099511627776` | Positive exponential proliferation defeats per-template control. |
| `signed_cancelled_pair` | `0` | `2` | Cancellation is additional information. |
| `rank_decay_toy` | `-40` | `1` | Decay can offset family growth. |

![Aggregate coefficient growth under polynomial family count, exponential family count, exact cancellation, and rank-decay toy weighting.](reports/figures/m9_aggregate_obstruction.png)

The Cycle 20 audit validated this with no critical or moderate findings. The report explicitly does not claim that Kim--Tao's actual quotient families grow exponentially or lack cancellation. It says only that M7 cannot decide those questions by itself.

### Finding 3: Cycle 21 Built the First Explicit Restricted Aggregate Enumeration

M10 moved from the abstract M9 obstruction to a concrete restricted model. The model enumerates reduced words over the free-group alphabet `a,A,b,B`, forms ordered pairs \((u,v)\), and interprets them as simultaneous fixed-point constraints \(u(i)=i\), \(v(i)=i\) with a shared basepoint. Inverse labels are normalized by reversing orientation. The resulting labelled skeletons are folded and canonicalized, with partial-injection conflicts flagged.

The direct enumerator was originally targeted at \(L_{\max}=6\) or \(7\), but the validated run used \(L_{\max}=4\) because larger values were too slow for the cycle budget. This runtime limit is part of the finding.

The M10 audit reported ordered-pair totals and conflict-free multiplicities:

| \(L\) | Total ordered pairs | Conflict-free multiplicity | Conflict multiplicity |
|---:|---:|---:|---:|
| 1 | 16 | 16 | 0 |
| 2 | 256 | 40 | 216 |
| 3 | 2704 | 320 | 2384 |
| 4 | 25600 | 2656 | 22944 |

The M10 report also summarized profile growth:

| \(L\) | Profiles | Conflict profiles | Conflict multiplicity | Conflict-free multiplicity |
|---:|---:|---:|---:|---:|
| 1 | 3 | 0 | 0 | 16 |
| 2 | 18 | 13 | 216 | 40 |
| 3 | 211 | 171 | 2384 | 320 |
| 4 | 2208 | 1876 | 22944 | 2656 |

For the order-one all-conflict-free aggregate coefficient, the auditor checked:

| \(L\) | Coefficient | M7/M9 proxy bound |
|---:|---:|---:|
| 1 | 0 | 16 |
| 2 | -24 | 160 |
| 3 | -760 | 2880 |
| 4 | -16392 | 42496 |

![Canonical skeleton counts and multiplicities by length and rank-filter variant.](reports/figures/m10_restricted_quotient_family_growth.png)

![Aggregate coefficient magnitudes for all, cyclic/rank-one, rank-two/noncyclic, and diagonal-subtracted proxy variants.](reports/figures/m10_restricted_quotient_aggregate_coefficients.png)

The finding is mixed but useful. Folding collapses many ordered pairs, yet conflict-compatible canonical profiles still grow quickly. Conflict rows dominate by multiplicity for \(L\ge2\). The cyclic/rank-one proxy is visible only at \(L=1\) after conflict exclusion; for \(L\ge2\), the tested conflict-free rows are rank-two/noncyclic under this proxy. The M7/M9 aggregate proxy holds once multiplicity is measured, but the multiplicity measurement is exactly the hard input.

### Finding 4: The Scope Boundary Became Sharper

The cycles did not produce a Kim--Tao exponent improvement, a replacement for MPvH/MP23, or a surface-group quotient-family theorem. They produced a sharper map of what such a theorem would need.

The current boundary is:

- M7 controls individual normalized product-ratio templates.
- M8 shows that Kim--Tao objects only partially expose such templates; exact coverage is limited to the independent-permutation baseline.
- M9 proves that per-template envelopes do not imply aggregate control without family-count, weight, cancellation, or decay information.
- M10 supplies first restricted aggregate data and reinforces that measured multiplicity and compatibility control are decisive.

This is progress because it turns the vague question "Can M7 explain Kim--Tao?" into a narrower bridge target: prove or falsify aggregate control for a specified quotient family after separating cyclic/diagonal contributions and rank-two remnants.

## Discussion

The main outcome of cycles 19-21 is negative in the useful mathematical sense. The product-ratio mechanism remains valuable, but it cannot be used as a standalone bridge to Kim--Tao's full trace estimates. M8 showed why: Kim--Tao's polynomialized quantities live in the surface-group random-cover law, not merely the independent-permutation template model. M9 showed the logical obstruction after summation. M10 then demonstrated the obstruction in the first restricted aggregate enumeration: even a small folded two-word model requires explicit multiplicity and compatibility control.

The next theorem target stated across the cycle records is an aggregate quotient-family statement. In one form:

\[
\text{For folded quotients generated by two-cycle or eight-loop word graphs with total word length }\le q,
\]
prove that the weighted sum of normalized product-ratio coefficients up to fixed order \(k\) is bounded by an explicit power of \(q\), after separating cyclic diagonal families and rank-two remnants.

M10 suggests two concrete next paths. One is engineering-driven: optimize the restricted enumerator to reach \(L=5\) or \(L=6\). The other is model-driven: define a narrower, more Kim--Tao-like weighted quotient class where cyclic diagonal families and rank-two remnants are separated before folding.

## Open Questions

1. Can the M10 restricted enumerator be optimized enough to reach \(L=5\) or \(L=6\) while preserving deterministic canonicalization and auditability?

2. Is there a narrower quotient family closer to Kim--Tao's two-trace or eight-loop expansions where cyclic diagonal terms and rank-two remnants can be separated structurally before folding?

3. For a restricted family, can one prove polynomial total variation of weights, or does the family require cancellation or rank-sensitive decay?

4. Can the normalized product-ratio factor be combined with the separated \(n\)-power in a future theorem statement, addressing the M10 audit note that the current summaries use the M7-style normalized factor rather than the full falling-factorial expectation when vertex and constraint counts differ?

5. Can the conservative conflict flag used in M10 be replaced by a compatibility criterion closer to the actual Kim--Tao quotient setting?

## References

No `REFERENCES.md` file exists in the workspace, so no global numbered bibliography was available. The report cites local source records and artifacts instead:

- Kim--Tao source paper files: `2603.01127.pdf`, `2603.01127.txt`.
- Cycle 19 sessions: researcher `6cd30b3c-9101-450d-b436-e3dd68fa5a02`, worker `f90d3574-c185-47a6-b8a5-2838180c2a4a`, auditor `ce53f519-2bfd-4914-ba46-19319a54cc36`.
- Cycle 20 sessions: researcher `05c0df1b-8b1c-4f86-858c-6949719faf81`, worker `7f497bcb-54f7-4c43-aca6-0afd27c230bf`, auditor `c394d1de-bc4c-46da-ab2b-cf1e8c9e0072`.
- Cycle 21 sessions: researcher `048aad7d-9415-4f29-ac97-3c7aa87499ff`, worker `a5d07325-c571-4e6a-87fc-78b81c6b7c4c`, auditor `0dd6b24a-d5e6-43a6-8985-731a55a4f82b`.
- M8 artifacts: `reports/extension_candidates/m8_quotient_family_bridge.md`, `data/extension_candidates/quotient_family_bridge_table.csv`.
- M9 artifacts: `reports/extension_candidates/m9_aggregate_obstruction_and_enumeration.md`, `data/extension_candidates/aggregate_product_ratio_obstruction.csv`, `data/extension_candidates/aggregate_bridge_requirements.csv`.
- M10 artifacts: `reports/extension_candidates/m10_restricted_quotient_aggregate.md`, `data/extension_candidates/restricted_quotient_family_profiles.csv`, `data/extension_candidates/restricted_quotient_aggregate_summary.csv`.

## Appendix: Implementation Details

### Code Organization

Cycles 19-21 added or used these new Phase II files:

| Milestone | Script | Lines | Test | Lines |
|---|---|---:|---|---:|
| M8 | `scripts/build_quotient_family_bridge_table.py` | 243 | `tests/test_quotient_family_bridge_table.py` | 73 |
| M9 | `scripts/analyze_aggregate_product_ratio_obstruction.py` | 231 | `tests/test_aggregate_product_ratio_obstruction.py` | 67 |
| M10 | `scripts/enumerate_restricted_quotient_aggregates.py` | 404 | `tests/test_restricted_quotient_aggregates.py` | 68 |

New or central data outputs:

| File | Rows excluding header |
|---|---:|
| `data/extension_candidates/quotient_family_bridge_table.csv` | 11 |
| `data/extension_candidates/aggregate_product_ratio_obstruction.csv` | 234 |
| `data/extension_candidates/aggregate_bridge_requirements.csv` | 6 |
| `data/extension_candidates/restricted_quotient_family_profiles.csv` | 2440 |
| `data/extension_candidates/restricted_quotient_aggregate_summary.csv` | 64 |

Figures checked during this reporter pass:

| Figure | Size |
|---|---|
| `reports/figures/m8_bridge_taxonomy.png` | 1680 x 896 RGBA |
| `reports/figures/m9_aggregate_obstruction.png` | 1600 x 960 RGBA |
| `reports/figures/m10_restricted_quotient_family_growth.png` | 1600 x 960 RGBA |
| `reports/figures/m10_restricted_quotient_aggregate_coefficients.png` | 1600 x 960 RGBA |

### Validation Results

Cycle validations reported these commands as passed:

- M8:
  - `python3 -m py_compile scripts/build_quotient_family_bridge_table.py tests/test_quotient_family_bridge_table.py`
  - `python3 scripts/build_quotient_family_bridge_table.py`
  - `python3 tests/test_quotient_family_bridge_table.py`
  - figure check for `reports/figures/m8_bridge_taxonomy.png`
  - `python3 -m long_exposure.tools.promise_check .`
  - `python3 -m long_exposure.tools.org_check .`

- M9:
  - `python3 -m py_compile scripts/analyze_aggregate_product_ratio_obstruction.py tests/test_aggregate_product_ratio_obstruction.py`
  - `python3 scripts/analyze_aggregate_product_ratio_obstruction.py`
  - `python3 tests/test_aggregate_product_ratio_obstruction.py`
  - figure check for `reports/figures/m9_aggregate_obstruction.png`
  - `python3 -m long_exposure.tools.promise_check .`
  - `python3 -m long_exposure.tools.org_check .`

- M10:
  - `python3 -m py_compile scripts/enumerate_restricted_quotient_aggregates.py tests/test_restricted_quotient_aggregates.py`
  - `python3 scripts/enumerate_restricted_quotient_aggregates.py`
  - `python3 tests/test_restricted_quotient_aggregates.py`
  - figure checks for both M10 figures
  - `python3 -m long_exposure.tools.promise_check .`
  - `python3 -m long_exposure.tools.org_check .`

After updating `MANIFEST.md`, the reporter reran:

- `python3 -m long_exposure.tools.promise_check .`
  - exit 0
  - `events: 48, plan milestones: 10`
  - warnings only: historical noncanonical `docs/paper_map/` ledger path and orphan prior cycle reports.
- `python3 -m long_exposure.tools.org_check .`
  - exit 0
  - warnings only: historical root paper/live/prompt files and old figures under `docs/`.

### Manifest Snapshot

`MANIFEST.md` was replaced with the current snapshot. There was no `## Key Files` section to preserve.

Current manifest totals:

| Metric | Value |
|---|---:|
| Campaign scripts | 21 |
| Campaign script lines | 5,132 |
| Campaign test files | 12 |
| Campaign test lines | 854 |
| Documentation artifacts under `docs/`, `reports/`, and `audits/` | 78 |
| PNG figures under `reports/figures/` | 28 |
| Canonical CSV datasets under `data/` | 32 |
| Promise ledger events | 48 |

Current validated milestones:

- `M1-paper-map`
- `M2-proof-ledger`
- `M3-computational-probes`
- `M4-formal-certification`
- `M5-extension-candidates`
- `M6-final-synthesis`
- `M7-product-ratio-bounds`
- `M8-quotient-family-bridge`
- `M9-aggregate-product-ratio-obstruction`
- `M10-restricted-quotient-aggregate`

### Cross-Reference Map

| Origin | Consuming Artifact | Role |
|---|---|---|
| `reports/extension_candidates/m7_product_ratio_coefficient_bounds.md` | `reports/extension_candidates/m8_quotient_family_bridge.md` | Supplies the per-template product-ratio lemma tested against Kim--Tao quotient/profile objects. |
| `scripts/build_quotient_family_bridge_table.py` | `data/extension_candidates/quotient_family_bridge_table.csv` | Builds the repaired M8 taxonomy. |
| `scripts/build_quotient_family_bridge_table.py` | `reports/figures/m8_bridge_taxonomy.png` | Builds the M8 bridge figure. |
| `reports/extension_candidates/m8_quotient_family_bridge.md` | `reports/extension_candidates/m9_aggregate_obstruction_and_enumeration.md` | Identifies aggregate family count, total weight, cancellation, and rank decay as the missing bridge inputs. |
| `scripts/analyze_aggregate_product_ratio_obstruction.py` | `data/extension_candidates/aggregate_product_ratio_obstruction.csv` | Generates deterministic aggregate examples. |
| `scripts/analyze_aggregate_product_ratio_obstruction.py` | `data/extension_candidates/aggregate_bridge_requirements.csv` | Records aggregate requirements not present in M7. |
| `scripts/analyze_aggregate_product_ratio_obstruction.py` | `reports/figures/m9_aggregate_obstruction.png` | Builds the M9 aggregate obstruction figure. |
| `reports/extension_candidates/m9_aggregate_obstruction_and_enumeration.md` | `reports/extension_candidates/m10_restricted_quotient_aggregate.md` | Supplies the aggregate obstruction that M10 tests in a restricted folded model. |
| `scripts/enumerate_restricted_quotient_aggregates.py` | `data/extension_candidates/restricted_quotient_family_profiles.csv` | Enumerates M10 folded profiles through `L_max=4`. |
| `scripts/enumerate_restricted_quotient_aggregates.py` | `data/extension_candidates/restricted_quotient_aggregate_summary.csv` | Builds M10 aggregate summaries and proxy bounds. |
| `scripts/enumerate_restricted_quotient_aggregates.py` | M10 figures | Builds the family-growth and aggregate-coefficient figures. |
