---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 22-24"
date: "2026-05-16"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 22-24

## Abstract

Cycles 22-24 continued the Phase II extension path that began after the final synthesis of the Kim-Tao paper campaign. The active question was no longer whether individual product-ratio templates have bounded coefficients. That was settled earlier by M7. The question was whether those per-template bounds can control aggregate quotient-family sums of the kind that appear in trace and pre-trace expansions.

The three cycles produced a coherent sequence:

- Cycle 22, M11, replaced the raw two-word quotient model from M10 with a more trace-like toy model based on cyclically reduced conjugacy representatives, primitive/diagonal labels, and explicit length weights.
- Cycle 23, M12, extracted the honest theorem template supported by M7, M9, and M11: aggregate bounds must be stated within fixed `d = C - V` strata, where `C` is the number of label constraints and `V` is the number of vertices.
- Cycle 24, M13, tested whether the M12 total-variation bound could be sharpened by coefficient cancellation. The tested toy family did not support robust algebraic cancellation; length decay remains the plausible external mechanism.

The validated conclusion is conservative. Trace-like quotienting and length weights improve the toy aggregate accounting, but they do not remove the need for an external aggregate input such as weighted total-variation control, rank-sensitive probability-law decay, or a coefficient-variation estimate. No cycle claims a replacement for Kim-Tao's MPvH/Witten-zeta, Nau boundedness, MP23 rank-two estimates, surface-group law, or Selberg trace weights.

## Introduction

The research campaign centers on Kim and Tao's paper `2603.01127`, "Eigenvalue rigidity of hyperbolic surfaces in the random cover model." Earlier cycles reconstructed the proof architecture, built finite random-permutation and Schreier-style probes, certified isolated labelled-template identities, and produced a Phase I final synthesis. Phase II then pursued a possible extension: whether product-ratio coefficient bounds for labelled permutation templates could help explain or sharpen trace-expansion estimates relevant to random hyperbolic covers.

The immediate prehistory matters. M7 established per-template product-ratio coefficient envelopes in an independent-permutation labelled-template model. M8 showed that this framework only partially attaches to Kim-Tao quotient/profile objects: it exactly covers the independent-permutation baseline, but actual random-cover expectations also require surface-group probability-law and imported polynomial-estimate machinery. M9 proved the aggregate obstruction: per-template control does not imply aggregate control unless one also controls total variation, family count, cancellation, or rank-sensitive decay. M10 then built a restricted two-word folded aggregate model and found that measured multiplicity and compatibility control remain active bottlenecks.

Cycles 22-24 asked what the next honest bridge could be. Instead of trying to claim a Kim-Tao theorem, the work narrowed the toy model, stated a conditional theorem template, and tested whether the missing aggregate input could come from cancellation.

## Approach

The cycles followed a chronological research arc.

Cycle 22 refined the aggregate model. The M10 model used ordered reduced-word pairs. M11 replaced those with cyclically reduced conjugacy-class representatives, identified primitive and diagonal/cyclic pairs before folding, retained explicit length weights, and separated the global power `n_power = C - V` from the normalized product-ratio factor.

Cycle 23 converted the empirical model into a theorem template. M12 stated the finite-family aggregate proposition that follows from M7 and M9, but only after grouping templates by the same value of `d = C - V`. This avoided mixing different powers of `n`.

Cycle 24 tested the proposed sharpening route. M13 computed signed coefficient sums, coefficient absolute variation, total-variation proxy bounds, cancellation ratios, grouped cancellation diagnostics, and candidate opposite-sign structural pairings. The goal was to determine whether cancellation exists as a stable mechanism, or whether weighted total variation remains the real control parameter.

All three cycles were validated by audit. The Cycle 22 audit fixed one moderate accounting defect in M11's diagonal-subtracted proxy. Cycles 23 and 24 had no critical or moderate findings. The supplied Cycle 24 audit report validates M13 directly.

## Source Inventory and Timeline

### Cycle 22: M11 Trace-Like Weighted Quotient Class

Researcher session `596d2a52-925b-42fd-899d-53b7331457dc` opened `M11-trace-like-weighted-quotient-class`. The brief asked whether replacing ordered reduced-word pairs by cyclically reduced conjugacy-class representatives would materially reduce folded profile multiplicity and weighted total variation. It also required primitive/diagonal classification before folding, explicit length weights, and explicit `n_power = C - V` accounting.

Worker session `9c780e18-66ab-43eb-8b75-e6d9cb5f1d65` built:

- `reports/extension_candidates/m11_trace_like_weighted_quotient_class.md`
- `scripts/enumerate_trace_like_weighted_quotients.py`
- `tests/test_trace_like_weighted_quotients.py`
- `data/extension_candidates/trace_like_weighted_quotient_profiles.csv`
- `data/extension_candidates/trace_like_weighted_quotient_summary.csv`
- `data/extension_candidates/trace_like_weighted_diagonal_decomposition.csv`
- `reports/figures/m11_trace_like_family_growth.png`
- `reports/figures/m11_diagonal_subtraction_effect.png`
- `reports/figures/m11_weighted_total_variation.png`

Auditor session `41ff385b-2a69-484e-95df-8fa99ef4ca6c` validated M11 after a repair. The original diagonal-subtracted proxy assigned diagonal/cyclic records negative sign. The research brief required "all minus diagonal/cyclic contribution," so the auditor repaired the script to remove those records, added a regression test, regenerated CSVs and figures, and updated the M11 report. The repair changed total variation and pair/profile accounting, but not the main order-one coefficient conclusion because diagonal/cyclic coefficients vanish in this toy model.

### Cycle 23: M12 Restricted Aggregate Theorem Template

Researcher session `4eea1162-7d12-4042-9260-494a69c49c9c` opened `M12-restricted-aggregate-theorem-template`. The brief asked for the strongest honest theorem statement implied by M7 plus an aggregate total-variation hypothesis, with mandatory stratification by `n_power = C - V`.

Worker session `2c24878e-f2d9-4c1e-8652-39ba7d0a8956` built:

- `reports/extension_candidates/m12_restricted_aggregate_theorem_template.md`
- `scripts/analyze_restricted_aggregate_theorem_template.py`
- `tests/test_restricted_aggregate_theorem_template.py`
- `data/extension_candidates/restricted_aggregate_theorem_strata.csv`
- `data/extension_candidates/restricted_aggregate_theorem_bound_checks.csv`
- `reports/figures/m12_stratified_total_variation.png`
- `reports/figures/m12_coefficient_bound_ratios.png`

Auditor session `6323e0a2-a88e-4e78-a738-96e1d5ceb462` validated M12 with no critical or moderate findings. The audit specifically confirmed that coefficient sums and total variation were computed by `d=C-V` stratum rather than by global sums that mix powers of `n`.

### Cycle 24: M13 Cancellation Mechanism Diagnostics

Researcher session `3e1653eb-0614-4baa-88a8-06ba71a66c0a` opened `M13-cancellation-mechanism-diagnostics`. The brief asked whether the M12 total-variation theorem could be sharpened by coefficient-level cancellation, structural grouping, length decay, or rank-sensitive decay in the M11 toy family.

Worker session `a0320462-1e19-4fd5-8468-51733ddc41ef` built:

- `reports/extension_candidates/m13_cancellation_mechanism_diagnostics.md`
- `scripts/analyze_cancellation_mechanisms.py`
- `tests/test_cancellation_mechanisms.py`
- `data/extension_candidates/cancellation_coefficient_summary.csv`
- `data/extension_candidates/cancellation_group_summary.csv`
- `data/extension_candidates/cancellation_candidate_pairings.csv`
- `reports/figures/m13_cancellation_ratios.png`
- `reports/figures/m13_grouped_cancellation_heatmap.png`
- `reports/figures/m13_bound_mode_comparison.png`

Auditor session `e2e4bb5f-f225-4076-8fa0-5f868b1f2e4a` validated M13 with no critical or moderate findings. The audit confirmed that M13 used M11 record-level pair data, preserved M12's `d=C-V` stratification, and computed cancellation metrics in the correct strata.

### Reference Gap

No `REFERENCES.md` file exists in the workspace. Therefore this report uses local source references: session IDs, reports, scripts, data files, and figures. No global numbered bibliography is available for these cycles.

## Findings

### Finding 1: Trace-Like Quotienting Reduced Aggregate Mass, But Did Not Supply Cancellation

Cycle 22 showed that trace-like quotienting materially reduced the toy aggregate size relative to M10. M11 replaced raw ordered reduced-word pairs with cyclically reduced conjugacy-class representatives, canonicalized by cyclic rotation and inversion. It then folded pair classes into labelled partial-permutation skeletons and tracked three weights:

| Weight scheme | Definition |
|---|---|
| `weight_unweighted` | orbit-size product |
| `weight_exp_decay_theta_0_5` | orbit-size product times `exp(-0.5(|u|+|v|))` |
| `weight_length_inverse` | orbit-size product divided by `max(1, |u||v|)` |

At the shared cutoff `L=4`, M10 had 332 conflict-free folded profiles and conflict-free multiplicity 2656. M11 had 18 conflict-free folded profiles and unweighted conflict-free total variation 136. This comparison supports the first M11 hypothesis: trace-like cyclic conjugacy and inversion quotienting reduce the family-count and total-variation burden in the tested toy model.

The post-repair M11 counts are:

| L | M10-style raw ordered pairs | M11 folded profiles | M11 conflict-free profiles | M11 conflict-free unweighted TV |
|---:|---:|---:|---:|---:|
| 1 | 16 | 3 | 3 | 16 |
| 2 | 256 | 16 | 6 | 40 |
| 3 | 2704 | 49 | 11 | 80 |
| 4 | 25600 | 227 | 18 | 136 |
| 5 | 234256 | 1039 | 27 | 208 |

![M11 family growth: raw ordered word-pair counts, cyclic conjugacy representative pairs, folded profiles, and conflict-free folded profiles by length cutoff.](reports/figures/m11_trace_like_family_growth.png)

The same cycle also showed that diagonal/cyclic subtraction is not the main mechanism in this toy model. At `L=5`, all conflict-free classes had order-one coefficient `-800` and total variation 208. The diagonal/cyclic class had coefficient 0 and total variation 8. After subtracting diagonal/cyclic records, the signed diagonal-subtracted proxy had coefficient `-800` and total variation 200, matching the rank-two/noncyclic remainder.

| L | Variant | Order-one coefficient | Unweighted TV | Profiles | Pair classes |
|---:|---|---:|---:|---:|---:|
| 1 | all conflict-free | 0 | 16 | 3 | 4 |
| 1 | signed diagonal-subtracted | 0 | 8 | 1 | 2 |
| 2 | all conflict-free | -8 | 40 | 6 | 10 |
| 2 | signed diagonal-subtracted | -8 | 32 | 4 | 8 |
| 3 | all conflict-free | -72 | 80 | 11 | 20 |
| 3 | signed diagonal-subtracted | -72 | 72 | 9 | 18 |
| 4 | all conflict-free | -288 | 136 | 18 | 34 |
| 4 | signed diagonal-subtracted | -288 | 128 | 16 | 32 |
| 5 | all conflict-free | -800 | 208 | 27 | 52 |
| 5 | signed diagonal-subtracted | -800 | 200 | 25 | 50 |

![M11 diagonal subtraction effect: unweighted order-one aggregate coefficient magnitudes before, within, and after signed diagonal/cyclic subtraction.](reports/figures/m11_diagonal_subtraction_effect.png)

Length weights did reduce effective total variation. At `L=5`, the all-conflict-free unweighted TV was 208, the exponential-decay weighted TV was about 18.96, and the inverse-length weighted TV was about 49.71. This supports length weighting as a plausible aggregate input, but still as total-variation control, not as cancellation.

![M11 weighted total variation: total-variation proxies under unweighted, exponential-decay, and inverse-length weights.](reports/figures/m11_weighted_total_variation.png)

The M11 audit decision was `VALIDATED`. The repaired conclusion is: trace-like quotienting helps, diagonal subtraction is small in this model, and the remaining rank-two mass is still controlled by weighted total variation.

### Finding 2: The Honest Aggregate Theorem Requires `d=C-V` Stratification

Cycle 23 turned the M11 model into a theorem template. The main technical point is that templates can have different global powers of `n`. For a template `T`, M12 writes

\[
E_T(n) = n^{d_T} R_T(1/n),
\qquad d_T = C_T - V_T,
\]

where `C_T` is the number of normalized label constraints, `V_T` is the vertex count, and `R_T(x)` is the normalized product-ratio factor controlled by M7.

Because the powers `n^{d_T}` differ, one cannot honestly aggregate all templates into a single coefficient sum. M12 defines the stratum

\[
F_{L,d}=\{T\in F_L : d_T=d\}
\]

and the stratum total variation

\[
TV_{L,d}=\sum_{T\in F_{L,d}} |w_T|.
\]

The validated proposition states that for a fixed coefficient order `k`, under the M7 support/index hypotheses,

\[
\left|[n^{d-k}]\sum_{T\in F_{L,d}} w_T E_T(n)\right|
\le C_k L^{2k} TV_{L,d}.
\]

The proof is the triangle inequality applied after factoring out the common `n^d` within one stratum. This is the M9 aggregate obstruction in its correct stratified form.

The M11 empirical check used record-level data because folded profile rows can aggregate diagonal and non-diagonal pre-fold records into the same folded key. At `L=5`, unweighted all-conflict-free data split as:

| Variant | `d` | TV | Profiles | Pair classes | coeff `k=1` | coeff `k=2` | coeff `k=3` | coeff `k=4` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all conflict-free | 0 | 8 | 2 | 2 | 0 | 0 | 0 | 0 |
| all conflict-free | 1 | 200 | 25 | 50 | -800 | 800 | 2800 | 3392 |
| signed diagonal-subtracted | 1 | 200 | 25 | 50 | -800 | 800 | 2800 | 3392 |
| rank-two remainder | 1 | 200 | 25 | 50 | -800 | 800 | 2800 | 3392 |

The largest empirical ratio

\[
|\text{actual coefficient}| / \max(1, L^{2k} TV_{L,d})
\]

over generated M12 rows was 0.16, attained at `L=5`, unweighted, `d=1`, `k=1`. This is not a sharp constant claim. It confirms that the theorem proxy is being applied to the correct stratum.

![M12 stratified total variation: unweighted total variation split by `n_power` stratum for all conflict-free, diagonal-subtracted, and rank-two remainder variants.](reports/figures/m12_stratified_total_variation.png)

![M12 coefficient bound ratios: empirical ratios `|coefficient| / max(1, L^(2k) TV_{L,d})` by coefficient order, taking the maximum over `n_power` strata.](reports/figures/m12_coefficient_bound_ratios.png)

The M12 audit decision was `VALIDATED`. The accepted theorem is explicitly a restricted independent-permutation labelled-template theorem template. It is not a Kim-Tao trace theorem.

### Finding 3: Robust Coefficient Cancellation Was Not Found

Cycle 24 tested whether M12's total-variation bound could be sharpened by coefficient-level cancellation in the M11 toy family. M13 computed, for each fixed length cutoff, variant, weight scheme, `d=C-V` stratum, and coefficient order `k`:

\[
S_{d,k}=\sum_T w_T c_{T,k},
\qquad
AV_{d,k}=\sum_T |w_T c_{T,k}|,
\qquad
B_{d,k}=L^{2k}\sum_T |w_T|.
\]

Here `S` is the signed coefficient sum, `AV` is coefficient absolute variation, and `B` is the M12 total-variation proxy. The cancellation ratio is

\[
\rho_{d,k}=|S_{d,k}|/AV_{d,k}
\]

when `AV` is nonzero. A value near 1 means little or no cancellation. A value near 0 would indicate strong cancellation.

For the dominant `L=5`, unweighted, `d=1`, rank-two/noncyclic remainder, M13 found:

| k | Signed sum | Coefficient AV | `rho` | M12 ratio |
|---:|---:|---:|---:|---:|
| 1 | -800 | 800 | 1.000 | 0.160 |
| 2 | 800 | 1136 | 0.704225352113 | 0.0064 |
| 3 | 2800 | 3104 | 0.90206185567 | 0.000896 |
| 4 | 3392 | 4720 | 0.718644067797 | 0.0000434 |

Order one has no cancellation in the dominant tested stratum: every contributing term has the same sign. Higher orders show partial cancellation, but not a stable small-ratio pattern.

![M13 cancellation ratios: `rho = |signed coefficient sum| / coefficient absolute variation` in the unweighted `d=1` stratum.](reports/figures/m13_cancellation_ratios.png)

The length-weighted results confirmed the distinction between decay and cancellation. At `L=5`, `d=1`, `k=1`, the rank-two remainder has `rho=1` for all three tested weights:

| Weight scheme | Signed sum | Coefficient AV | Weighted TV |
|---|---:|---:|---:|
| unweighted | -800 | 800 | 200 |
| exp decay `theta=0.5` | -19.1824613678 | 19.1824613678 | 16.0169067036 |
| inverse length | -59.0422222222 | 59.0422222222 | 41.7088888889 |

The improvement from length weights is therefore a weighted-variation effect, not sign cancellation.

M13 then grouped the data by length pair, rank/cyclic proxy, primitive/diagonal status, folded profile key, and coefficient sign vector. For `L=5`, unweighted `d=1`, rank-two remainder, the absolute-variation-weighted mean group cancellation ratios were:

| Grouping rule | `k=1` | `k=2` | `k=3` | `k=4` |
|---|---:|---:|---:|---:|
| length pair | 1.000 | 1.000 | 1.000 | 1.000 |
| rank/cyclic proxy | 1.000 | 0.704 | 0.902 | 0.719 |
| primitive/diagonal status | 1.000 | 0.704 | 0.902 | 0.719 |
| folded profile key | 1.000 | 1.000 | 1.000 | 1.000 |
| coefficient sign vector | 1.000 | 1.000 | 1.000 | 1.000 |

The finer groupings destroyed the apparent higher-order cancellation: each refined cell was one-sided in coefficient sign. The candidate-pairing CSV recorded a null result: no opposite-sign structural cells were found under the tested structural keys.

![M13 grouped cancellation heatmap: absolute-variation-weighted cancellation ratios by grouping rule in the `L=5` unweighted `d=1` rank-two remainder.](reports/figures/m13_grouped_cancellation_heatmap.png)

M13 compared four bound modes: the M12 total-variation proxy, coefficient absolute variation, signed coefficient magnitude, and length/rank weighted versions. Coefficient absolute variation is sharper than the M12 proxy because it uses actual coefficients rather than the uniform `L^{2k}` envelope. The report treats this as diagnostic only: replacing total variation by coefficient absolute variation in a theorem would require a new a priori estimate.

![M13 bound mode comparison: TV-controlled M12 proxy, coefficient absolute variation, signed magnitude, and weighted-decay modes in the dominant stratum.](reports/figures/m13_bound_mode_comparison.png)

The M13 audit decision was `VALIDATED`. The accepted conclusion is negative for algebraic cancellation: total variation remains the only robust algebraic control mechanism in the tested toy family, while length decay remains a plausible external weighted-variation hypothesis.

### Finding 4: The Phase II Bottleneck Is Now an External Aggregate Estimate

M7-M13 now form a clear chain:

1. M7 gives per-template normalized product-ratio coefficient control.
2. M8 shows that this framework only partially touches Kim-Tao quotient objects.
3. M9 proves that aggregate control needs total variation, cancellation, family count, or decay.
4. M10 shows raw folded two-word aggregates still require measured multiplicity and compatibility control.
5. M11 shows trace-like quotienting and length weights reduce the toy total variation.
6. M12 packages the valid theorem template, but only inside fixed `d=C-V` strata.
7. M13 rules out robust coefficient cancellation in the tested M11 toy family.

This sequence shifts the active bottleneck. The unresolved issue is not per-template coefficient growth. It is an external aggregate estimate: a bound on weighted total variation, coefficient absolute variation, family count, or rank/length probability-law decay in quotient families close enough to the actual Kim-Tao trace/pre-trace expansion.

## Discussion

Cycles 22-24 refined the research direction rather than closing it. M11 provided evidence that quotienting by cyclic conjugacy and inversion is not cosmetic. It changes the measured toy aggregate mass substantially at shared cutoffs. That is a useful positive result because trace formula sums are naturally organized by conjugacy classes rather than raw ordered words.

M12 then prevented a common overclaim. Once templates have different `C-V`, aggregating coefficients without stratification mixes distinct powers of `n`. The theorem template is simple, but its simplicity is the point: it states exactly what follows from M7 and M9, and exactly what remains unproved.

M13 tested the most tempting improvement route: maybe signs cancel. The tested answer was mostly no. Order-one cancellation is absent in the dominant rank-two stratum, and higher-order cancellation is unstable under natural refinements. This negative result is useful because it directs future work away from unstructured algebraic cancellation and toward external decay axes.

The next recommended sub-topic from the M13 audit is an M14 rank/length weighted coefficient-variation model. That would introduce explicit hypothetical decay weights by rank proxy, word length, or primitive-power complexity, then quantify what exponent would be sufficient for the M12 theorem template to be useful at the trace/pre-trace interpolation scale.

## Open Questions

1. Can one prove a weighted total-variation or coefficient-variation bound for a quotient family that is closer to the actual Kim-Tao trace expansion?

2. What length-decay exponent would be sufficient for the M12 theorem template to survive the trace/pre-trace interpolation scale?

3. Can a rank-sensitive probability-law input, analogous in role to MP23 rank-two common-fixed-point decay, be modeled in the restricted quotient family?

4. Can the M11 enumerator be optimized beyond `L=5` without changing the model, or is a narrower Kim-Tao-like quotient class more valuable than larger toy cutoffs?

5. How should Witten-zeta normalization, Nau boundedness, and surface-group law effects be represented in the next restricted aggregate model without overclaiming equivalence to Kim-Tao?

## References

No `REFERENCES.md` file exists in the workspace, so no global numbered citations are available for this report. The report is based on the following local sources.

- Kim and Tao paper files: `2603.01127.pdf`, `2603.01127.txt`.
- Cycle 22 sessions: researcher `596d2a52-925b-42fd-899d-53b7331457dc`, worker `9c780e18-66ab-43eb-8b75-e6d9cb5f1d65`, auditor `41ff385b-2a69-484e-95df-8fa99ef4ca6c`.
- Cycle 23 sessions: researcher `4eea1162-7d12-4042-9260-494a69c49c9c`, worker `2c24878e-f2d9-4c1e-8652-39ba7d0a8956`, auditor `6323e0a2-a88e-4e78-a738-96e1d5ceb462`.
- Cycle 24 sessions: researcher `3e1653eb-0614-4baa-88a8-06ba71a66c0a`, worker `a0320462-1e19-4fd5-8468-51733ddc41ef`, auditor `e2e4bb5f-f225-4076-8fa0-5f868b1f2e4a`.
- M11 artifacts: `reports/extension_candidates/m11_trace_like_weighted_quotient_class.md`, `scripts/enumerate_trace_like_weighted_quotients.py`, M11 CSVs under `data/extension_candidates/`, and three M11 figures under `reports/figures/`.
- M12 artifacts: `reports/extension_candidates/m12_restricted_aggregate_theorem_template.md`, `scripts/analyze_restricted_aggregate_theorem_template.py`, M12 CSVs under `data/extension_candidates/`, and two M12 figures under `reports/figures/`.
- M13 artifacts: `reports/extension_candidates/m13_cancellation_mechanism_diagnostics.md`, `scripts/analyze_cancellation_mechanisms.py`, M13 CSVs under `data/extension_candidates/`, and three M13 figures under `reports/figures/`.
- Campaign state files: `plan_of_record.md`, `promise_ledger.jsonl`, `MANIFEST.md`.

## Appendix: Implementation Details

### Code Organization

Cycles 22-24 added three campaign scripts:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/enumerate_trace_like_weighted_quotients.py` | 568 | Enumerates M11 cyclic conjugacy quotient classes with diagonal separation, weights, summaries, and figures. |
| `scripts/analyze_restricted_aggregate_theorem_template.py` | 224 | Computes M12 `n_power = C - V` strata, coefficient sums, total-variation bounds, CSVs, and figures. |
| `scripts/analyze_cancellation_mechanisms.py` | 425 | Computes M13 signed sums, absolute variation, grouped cancellation diagnostics, candidate pairings, and bound-mode figures. |

Cycles 22-24 added three test files:

| File | Lines | Purpose |
|---|---:|---|
| `tests/test_trace_like_weighted_quotients.py` | 108 | Tests M11 canonicalization, inversion, primitive powers, inverse-label normalization, `n_power`, and weighted summaries. |
| `tests/test_restricted_aggregate_theorem_template.py` | 94 | Tests M12 stratum aggregation, diagonal-subtracted TV accounting, cancellation examples, finite ratios, and CSV columns. |
| `tests/test_cancellation_mechanisms.py` | 127 | Tests M13 cancellation ratios, zero-variation handling, grouped refinements, and M11/M12 reference values. |

Generated M11-M13 datasets:

| File | Lines including header |
|---|---:|
| `data/extension_candidates/trace_like_weighted_quotient_profiles.csv` | 1335 |
| `data/extension_candidates/trace_like_weighted_quotient_summary.csv` | 301 |
| `data/extension_candidates/trace_like_weighted_diagonal_decomposition.csv` | 21 |
| `data/extension_candidates/restricted_aggregate_theorem_strata.csv` | 76 |
| `data/extension_candidates/restricted_aggregate_theorem_bound_checks.csv` | 301 |
| `data/extension_candidates/cancellation_coefficient_summary.csv` | 361 |
| `data/extension_candidates/cancellation_group_summary.csv` | 6385 |
| `data/extension_candidates/cancellation_candidate_pairings.csv` | 2 |

Generated or updated figures:

| Figure | Metadata |
|---|---|
| `reports/figures/m11_trace_like_family_growth.png` | PNG, 1600 x 960 |
| `reports/figures/m11_diagonal_subtraction_effect.png` | PNG, 1600 x 960 |
| `reports/figures/m11_weighted_total_variation.png` | PNG, 1600 x 960 |
| `reports/figures/m12_stratified_total_variation.png` | PNG, 2080 x 768 |
| `reports/figures/m12_coefficient_bound_ratios.png` | PNG, 1760 x 1280 |
| `reports/figures/m13_cancellation_ratios.png` | PNG, 1760 x 1280 |
| `reports/figures/m13_grouped_cancellation_heatmap.png` | PNG, 1360 x 768 |
| `reports/figures/m13_bound_mode_comparison.png` | PNG, 1520 x 880 |

### Validation Results

The supplied M13 audit reports the following validation commands as passed:

```bash
python3 -m py_compile scripts/analyze_cancellation_mechanisms.py tests/test_cancellation_mechanisms.py
python3 scripts/analyze_cancellation_mechanisms.py
python3 tests/test_cancellation_mechanisms.py
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

It also reports that all three M13 PNGs are readable and nonblank. The audit lists only known historical warnings from `promise_check` and `org_check`.

For this report pass, `MANIFEST.md` was updated and the workspace validators were rerun:

```text
python3 -m long_exposure.tools.promise_check .
events: 58, plan milestones: 13
exit 0, warnings only

python3 -m long_exposure.tools.org_check .
exit 0, warnings only
```

The warnings are historical: noncanonical early `docs/paper_map/` ledger path, orphan prior cycle reports under `reports/cycles/`, root paper/live files, and older figures under `docs/`.

### Manifest Snapshot

`MANIFEST.md` was replaced as a current snapshot. There was no `## Key Files` section to preserve. The updated manifest has 159 lines and records:

| Metric | Value |
|---|---:|
| Campaign scripts | 24 |
| Campaign script lines | 6349 |
| Campaign test files | 15 |
| Campaign test lines | 1183 |
| Documentation artifacts under `docs/`, `reports/`, and `audits/` | 90 |
| PNG figures under `reports/figures/` | 36 |
| Canonical CSV datasets under `data/` | 40 |
| Promise ledger events | 58 |

### Session Reference Map

| Cycle | Role | Session ID | Role in timeline |
|---:|---|---|---|
| 22 | researcher | `596d2a52-925b-42fd-899d-53b7331457dc` | Defined M11 trace-like weighted quotient-class task. |
| 22 | worker | `9c780e18-66ab-43eb-8b75-e6d9cb5f1d65` | Built M11 script, tests, CSVs, figures, and report. |
| 22 | auditor | `41ff385b-2a69-484e-95df-8fa99ef4ca6c` | Repaired and validated M11 diagonal-subtracted accounting. |
| 23 | researcher | `4eea1162-7d12-4042-9260-494a69c49c9c` | Defined M12 theorem-template task. |
| 23 | worker | `2c24878e-f2d9-4c1e-8652-39ba7d0a8956` | Built M12 theorem report, analyzer, tests, CSVs, and figures. |
| 23 | auditor | `6323e0a2-a88e-4e78-a738-96e1d5ceb462` | Validated M12 stratum-wise theorem template. |
| 24 | researcher | `3e1653eb-0614-4baa-88a8-06ba71a66c0a` | Defined M13 cancellation diagnostics task. |
| 24 | worker | `a0320462-1e19-4fd5-8468-51733ddc41ef` | Built M13 analyzer, tests, CSVs, figures, and report. |
| 24 | auditor | `e2e4bb5f-f225-4076-8fa0-5f868b1f2e4a` | Validated M13 and recommended the M14 external decay axis. |

### Cross-Reference Map

| Origin | Consuming artifact | Value / role |
|---|---|---|
| `reports/extension_candidates/m10_restricted_quotient_aggregate.md` | `reports/extension_candidates/m11_trace_like_weighted_quotient_class.md` | Motivated trace-like cyclic conjugacy quotienting and pre-fold diagonal separation. |
| `scripts/enumerate_trace_like_weighted_quotients.py` | M11 CSVs and figures | Produced trace-like profile, summary, diagonal decomposition, family-growth, diagonal-effect, and weighted-TV artifacts. |
| `reports/extension_candidates/m11_trace_like_weighted_quotient_class.md` | `reports/extension_candidates/m12_restricted_aggregate_theorem_template.md` | Supplied M11 data and explicit `n_power = C - V` fields for theorem packaging. |
| `scripts/analyze_restricted_aggregate_theorem_template.py` | M12 CSVs and figures | Computed stratum-wise coefficient sums, total variation, empirical ratios, and figures. |
| `reports/extension_candidates/m12_restricted_aggregate_theorem_template.md` | `reports/extension_candidates/m13_cancellation_mechanism_diagnostics.md` | Defined the stratified total-variation theorem that M13 attempted to sharpen. |
| `scripts/analyze_cancellation_mechanisms.py` | M13 CSVs and figures | Computed signed sums, coefficient absolute variation, grouping diagnostics, pairing null result, and bound-mode comparison. |
| M13 audit `e2e4bb5f-f225-4076-8fa0-5f868b1f2e4a` | Next research direction | Recommended moving to an external rank/length weighted coefficient-variation model rather than further algebraic cancellation searches. |
