---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 31-33"
date: "2026-05-16"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 31-33

## Abstract

Cycles 31-33 continued the local spectral-window branch opened in earlier work on Kim and Tao's random-cover spectral rigidity paper. The previous cycle, M19, had closed the logarithmic-support smoothing route: a compactly supported trace test cannot resolve a polynomially shrinking spectral window unless its geometric support also grows polynomially. These three cycles asked what happens if that long support is allowed.

The answer was a staged narrowing of the remaining compact-support route. M20 quantified the variance saving needed when geometric support grows like a power of the cover degree. M21 converted that budget into a fixed-energy trace-side long-support variance theorem template. M22 then reduced the theorem template to a concrete localized Corollary 3.4 numerator target. No new local spectral statistics theorem was proved. The validated outcome is a precise next bottleneck: build a quotient-family model for the localized numerator
$p_{\Delta,q}$ before attempting a proof of long-support trace variance.

The final decision for this cycle range is therefore not closure of the local-window route, but further narrowing. The active branch is fixed-energy, trace-side, compact Paley-Wiener support with polynomial support parameter $q=n^\eta$. Pre-trace and edge-window branches remain out of scope because prior budgets made them less plausible.

## Introduction

The campaign studies the paper `2603.01127`, "Eigenvalue rigidity of hyperbolic surfaces in the random cover model" by Elena Kim and Zhongkai Tao. The long-term goal is to understand the paper's proof architecture and then search for credible extensions.

Earlier cycles established the following context.

M16 showed that subtracting Kim-Tao global Weyl-law estimates at two endpoints only controls spectral windows above an inherited global-error scale. This gives mesoscopic information, but not genuine shrinking local spectral statistics.

M17 formulated the missing kind of input: a smoothed-window variance estimate. For a window of width $\Delta=n^{-d}$ in the bulk, a centered smoothed statistic has relative control if the variance exponent is small enough; in the notation used there, $v/2<1-d$. To beat endpoint subtraction, the window exponent must also satisfy $d>\alpha_W$.

M18 mapped that target into the Kim-Tao test-function machinery and found a cost: inverse-width localization forces growth in the polynomial degree and geometric support parameter $q$, reintroducing the paper's $q^{2\kappa}$ trace-side and $q^{4\kappa}$ pre-trace losses.

M19 proved the smoothing obstruction that forced the next choice. For a compactly supported transform, resolving a bulk window $\Delta=n^{-d}$ requires support $R=n^\eta$ with $\eta\ge d$. Logarithmic support cannot resolve polynomially shrinking windows.

Cycles 31-33 start from that fork. The branch studied here accepts polynomial support and asks what new trace-side random-cover input would be needed.

## Approach

The work in cycles 31-33 followed a narrowing sequence.

1. M20 treated the missing random-cover saving as an unknown exponent $\beta(\eta)$ and computed when that saving would overcome the long-support losses.

2. M21 converted the M20 budget into a theorem template, named the exact centered trace-side statistic, and identified which Kim-Tao inputs would need uniform long-support strengthening.

3. M22 moved one level closer to the proof object by defining the localized weighted numerator attached to Kim-Tao Lemma 3.3 and Corollary 3.4, then computed which coefficient-variation, direct small-$x$, or stratified weighted bounds would imply the needed $\beta$ saving.

This is a general mathematical report. It records validated work; it does not re-audit the conclusions.

## Source Inventory and Timeline

The following source sessions were gathered and used.

| Cycle | Session ID | Date | Role | Contents |
|---|---|---|---|---|
| 31 | `169954ce-48cf-472a-a28b-a2db5ff61bbd` | 2026-05-16 | researcher | Opened M20. Framed the long-support variance budget after M19 and specified required artifacts. |
| 31 | `25259870-a419-447a-a2ff-67239e24ee31` | 2026-05-16 | worker | Built M20 proof note, report, analyzer, tests, CSVs, and figures. |
| 31 | `26b77f9e-e136-492b-9b7d-171698b029c6` | 2026-05-16 | auditor | Validated M20 after one moderate repair to median computation in generated summaries. |
| 32 | `69efb200-e06c-4da7-935b-393262fdf225` | 2026-05-16 | researcher | Opened M21. Asked for the exact trace-side long-support theorem template. |
| 32 | `7978fb53-3b20-4f6d-ab22-dd74fe347a34` | 2026-05-16 | worker | Built M21 theorem-template proof note, report, analyzer, tests, CSVs, and figures. |
| 32 | `97e2b0bd-de7c-4716-a0a7-5c4e9b562f15` | 2026-05-16 | auditor | Validated M21 with no critical or moderate findings. |
| 33 | `36c56594-f3e6-4cae-9d5e-430065bb65bc` | 2026-05-16 | researcher | Opened M22. Narrowed the theorem target to the localized Corollary 3.4 numerator. |
| 33 | `ffacb468-1319-42d2-9539-d95f7c9cee99` | 2026-05-16 | worker | Built M22 numerator target proof note, report, analyzer, tests, CSVs, and figures. |
| 33 | `369b8204-7b26-4734-8b3a-e4afcb973eca` | 2026-05-16 | auditor | Validated M22 with no critical or moderate findings. |

The main artifacts used were:

- `docs/proof_ledger/long_support_trace_variance_requirement.md`
- `reports/extension_candidates/m20_long_support_trace_variance_requirement.md`
- `docs/proof_ledger/trace_side_long_support_variance_template.md`
- `reports/extension_candidates/m21_trace_side_long_support_variance_template.md`
- `docs/proof_ledger/trace_corollary34_localized_numerator_target.md`
- `reports/extension_candidates/m22_trace_corollary34_uniform_coefficient_variation_target.md`
- the six generated CSV datasets under `data/extension_candidates/`
- the six generated figures under `reports/figures/`

No `REFERENCES.md` file exists in the workspace, so this report cites internal source sessions and local artifacts rather than continuing a global numbered bibliography.

## Findings

### Finding 1: M20 Quantified the Long-Support Variance Budget

M20 asked what variance theorem would be required if the local-window trace route accepts polynomial geometric support.

The model starts with a future long-support variance estimate

$$
\operatorname{Var} Z_n \le n^{1+L(\eta)-\beta(\eta)}.
$$

Here $L(\eta)$ records the support, degree, and interpolation loss, while $\beta(\eta)$ is the new random-cover saving that is not available from existing Kim-Tao inputs.

For a bulk window $\Delta=n^{-d}$, the M17 smoothed-window Chebyshev condition becomes

$$
\beta(\eta) > L(\eta)+2d-1.
$$

At the edge, where the mean exponent is different, M20 recorded

$$
\beta(\eta) > L(\eta)+3d-1.
$$

M20 used the Kim-Tao support map from M18,

$$
\operatorname{supp}((h\circ f_{\Lambda_0})^\vee)
  \lesssim \Lambda_0^{-1/2}q,
$$

so at fixed $\Lambda_0$, support $R=n^\eta$ corresponds to $q=n^\eta$. The existing loss proxies are:

$$
L_{\mathrm{trace}}(\eta)=2\kappa\eta,
\qquad
L_{\mathrm{pretrace}}(\eta)=4\kappa\eta.
$$

At minimal support and $\kappa=5$, this gives the representative thresholds:

| Regime | Architecture | Required saving |
|---|---|---|
| bulk | trace | $\beta>12d-1$ |
| bulk | pre-trace | $\beta>22d-1$ |
| edge | trace | $\beta>8d-1$ |
| edge | pre-trace | $\beta>13d-1$ |

The generated M20 budget table has 4,356 data rows. Its classes were:

| Class | Rows |
|---|---:|
| `impossible_by_support` | 1,872 |
| `outside_current_architecture` | 1,284 |
| `requires_no_extra_saving` | 510 |
| `requires_moderate_new_saving` | 192 |
| `requires_large_new_saving` | 498 |

The M20 auditor found one moderate issue: the summary script computed medians for even-cardinality lists using the upper-middle element rather than the true median. The auditor repaired the script, added a regression test, regenerated the data and figures, and confirmed that the formulas and strategic conclusion were unchanged.

For $\kappa=5$, fixed $\Lambda_0=4$, and endpoint-beating rows satisfying the M19 support condition, the corrected medians were:

| Regime | Architecture | Rows | Minimum beta | Median beta |
|---|---|---:|---:|---:|
| bulk | trace | 28 | -0.904 | 0.15 |
| bulk | pre-trace | 28 | -0.824 | 1.15 |
| edge | trace | 44 | -0.942 | -0.091 |
| edge | pre-trace | 44 | -0.902 | 0.659 |
| high energy | trace | 28 | -0.904 | 0.15 |
| high energy | pre-trace | 28 | -0.824 | 1.15 |

The decision was to continue with a concrete long-support trace theorem template. The trace side remained conditionally plausible in a narrow exponent band; the pre-trace side was deprioritized because of the larger $4\kappa\eta$ loss.

![Required random-cover variance saving beta as a function of window exponent under trace and pre-trace long-support losses.](reports/figures/m20_required_variance_saving.png)

![Feasible, conditional, and obstructed regions for long-support local-window variance estimates.](reports/figures/m20_long_support_feasibility_map.png)

### Finding 2: M21 Turned the Budget into a Trace-Side Theorem Template

M21 named the exact fixed-energy trace-side statistic that the missing theorem should control.

Fix

$$
\Lambda_0>1/4,\qquad r_0=\sqrt{\Lambda_0-1/4},
\qquad \Delta=n^{-d},\qquad q=n^\eta,\qquad \eta\ge d.
$$

The localized spectral statistic is

$$
Z_n(h_{\Lambda_0,\Delta,q})
=
\sum_j h_{\Lambda_0,\Delta,q}(r_j(X_n))
-
\frac{n\operatorname{Vol}(X)}{2\pi}
\int_0^\infty h_{\Lambda_0,\Delta,q}(r)r\tanh(\pi r)\,dr.
$$

Here $\lambda_j(X_n)=r_j(X_n)^2+1/4$, and the $r$-window width is

$$
\delta_r=\frac{\Delta}{2r_0}+O(\Delta^2).
$$

By Kim-Tao Lemma 2.1, M21 identified the same statistic with the non-identity geometric trace sum

$$
\sum_{\gamma\in P(X)}\sum_{k\ge 1}
\frac{\ell_\gamma(X)}{2\sinh(k\ell_\gamma(X)/2)}
h_{\Lambda_0,\Delta,q}^{\vee}(k\ell_\gamma(X))
\operatorname{tr}\rho(\gamma^k).
$$

This was the exact attachment point to the trace formula.

M21 then stated the conditional theorem template `LSTV_trace(eta,beta)`:

$$
\operatorname{Var} Z_n(h_{\Lambda_0,\Delta,q})
\le
C n^{1+2\kappa\eta-\beta+\epsilon}.
$$

The term $2\kappa\eta$ is the trace-side Markov/interpolation loss after substituting $q=n^\eta$. The new exponent $\beta$ is the missing saving.

Since the bulk expected mass is $\mu_n\asymp n\Delta=n^{1-d}$, Chebyshev gives relative smoothed-window control when

$$
1+2\kappa\eta-\beta < 2-2d,
$$

or equivalently

$$
\beta > 2\kappa\eta+2d-1.
$$

To beat M16 endpoint subtraction, this must hold with $d>\alpha_W$.

The M21 analyzer produced 11,664 data rows and 81 summary rows. The generated classes were:

| Class | Rows |
|---|---:|
| `support_invalid` | 5,346 |
| `not_endpoint_beating` | 3,564 |
| `conditional_success` | 1,927 |
| `needs_large_saving` | 531 |
| `needs_moderate_saving` | 296 |

For $\kappa=5$ and $\alpha_W=0.006$, each beta model had 36 endpoint-beating, support-valid pairs $(d,\eta)$. The required beta range was

$$
-0.904 \le \beta_{\mathrm{required}}\le 2.0,
$$

with median $0.07$.

M21 did not claim the theorem is proved. Its dependency checklist separated existing inputs from missing ones:

| Dependency | M21 status |
|---|---|
| Lemma 2.1 trace formula | existing |
| M19 support condition | existing |
| Markov interpolation framework | existing but costly |
| localized §2.4-style test construction | new construction needed |
| Proposition 3.1 long-support variance form | needs uniform extension |
| Lemma 3.3 two-trace polynomial expansion | needs uniform extension |
| Corollary 3.4 polynomial numerator | new theorem-level input |
| MPvH/Witten-zeta normalization | needs uniform extension |
| Nau boundedness | needs uniform extension |
| de-smoothing | out of scope |

The M21 decision was: `needs external uniform input before proof attempt`.

![Required trace-side long-support variance saving as a function of window exponent and support exponent.](reports/figures/m21_trace_template_beta_thresholds.png)

![Conditional success regions for candidate beta models in the fixed-energy trace-side theorem template.](reports/figures/m21_trace_template_plausibility_regions.png)

### Finding 3: M22 Reduced the Theorem to the Localized Corollary 3.4 Numerator

M22 moved from the global theorem template to the upstream polynomial numerator target.

For a localized trace test $h_{\Delta,q}$ with $\Delta=n^{-d}$, $q=n^\eta$, and $\eta\ge d$, M22 defined

$$
p_{\Delta,q}(x)
=
\sum_{\gamma_1,\gamma_2}
\sum_{k_1,k_2\ge 1}
a(\gamma_1,k_1)a(\gamma_2,k_2)
h_{\Delta,q}^{\vee}(k_1\ell_{\gamma_1})
h_{\Delta,q}^{\vee}(k_2\ell_{\gamma_2})
Q_{\gamma_1^{k_1},\gamma_2^{k_2}}(x).
$$

This is literally Kim-Tao's Corollary 3.4 numerator only if the localized window can be realized inside the paper-compatible $h\circ f_{\Lambda_0}$ polynomial/support architecture. Otherwise it is the nearest localized analogue and requires a new uniform Lemma 3.3 / Corollary 3.4 package.

The M22 beta algebra was:

$$
\mathbb{E}G_n(h_{\Delta,q})^2
\le
n q^A n^{-\sigma+o(1)}
\quad\Longrightarrow\quad
\beta=(2\kappa-A)\eta+\sigma.
$$

This is measured relative to the M21 baseline $nq^{2\kappa}=n^{1+2\kappa\eta}$.

The fixed-bulk local-window condition stayed the same:

$$
d>\alpha_W,\qquad \eta\ge d,\qquad
\beta>2\kappa\eta+2d-1.
$$

M22 separated three sufficient target types:

| Target | Meaning | Main risk |
|---|---|---|
| coefficient variation | absolute coefficient/tail control of $p_{\Delta,q}$ at $x=1/n$ | may discard cancellation |
| direct small-$x$ | signed control of $p_{\Delta,q}(1/n)$ near $1/n$ | cancellation only at $x=0$ is not enough |
| stratified weighted | fixed $C-V$ or quotient-power strata with Selberg/localized weights | needs the actual quotient-family decomposition |

The pure Markov/interpolation baseline has $A=2\kappa$ and $\sigma=0$, so $\beta=0$. M22 found that this baseline succeeds only in rows where the required beta is already negative; it fails every endpoint-beating, support-valid row with positive required beta.

The M22 analyzer generated 10,368 data rows and 72 summary rows. The classes were:

| Class | Rows |
|---|---:|
| `support_invalid` | 4,752 |
| `not_endpoint_beating` | 3,168 |
| `conditional_success` | 1,498 |
| `needs_more_numerator_saving` | 950 |

For the representative $\kappa=5$, $\alpha_W=0.006$ endpoint-beating, support-valid band, selected target outcomes were:

| Target | Successes / 36 | Reading |
|---|---:|---|
| `baseline A=2k` | 15 | passes only negative-threshold rows |
| `direct sigma=0.75` | 27 | fixed small-$x$ saving handles most small-window rows |
| `CV A=2k-4` | 24 | coefficient-variation improvement helps |
| `stratified A=2k-4 W=q^-1` | 27 | stratified decay matches the tested direct-saving count |

The M22 decision was: `needs quotient-family model before proof attempt`.

This means the next cycle should model the actual weighted quotient-family strata appearing in $p_{\Delta,q}$, including Selberg weights, localized transform weights, and the $Q_{\gamma_1^{k_1},\gamma_2^{k_2}}$ numerator contribution.

![Conditional success regions for candidate localized numerator bounds in the fixed-energy trace-side bulk band.](reports/figures/m22_corollary34_target_success_regions.png)

![Required numerator-level saving beyond the trace-side $q^{2\kappa}$ loss as a function of $d$ and $\eta$.](reports/figures/m22_required_numerator_saving.png)

### Finding 4: The Local-Window Route Has Been Narrowed to a Quotient-Family Numerator Model

The cumulative logic through cycles 31-33 is:

1. M19 forced polynomial support for polynomially shrinking compact-support windows.

2. M20 showed that accepting polynomial support leaves a narrow trace-side exponent band, but requires a new variance saving $\beta$.

3. M21 stated the exact fixed-energy trace-side theorem template and found that the missing input is not simply Proposition 3.1 as a black box. It is uniform localized control around Lemma 3.3 and Corollary 3.4.

4. M22 defined the localized numerator target and showed which coefficient-variation, direct small-$x$, or stratified weighted controls would produce useful beta saving.

The live branch is therefore precise. It asks whether the localized numerator $p_{\Delta,q}$ has enough quotient-family structure, cancellation, or weighted decay to produce positive $\beta$ in the endpoint-beating, support-valid band.

The branch is still conditional. Existing Kim-Tao inputs do not prove this numerator saving, and the prior independent-permutation toy models do not automatically transfer to the surface-group trace numerator.

## Discussion

Cycles 31-33 did not produce a new rigidity theorem, but they made the local-window extension problem more inspectable.

Before M20, the phrase "long-support trace variance theorem" was a global slogan. After M21, it became a theorem template with a named statistic and a concrete inequality,

$$
\operatorname{Var} Z_n
\le
n^{1+2\kappa\eta-\beta+o(1)}.
$$

After M22, the theorem template became a numerator-level question about $p_{\Delta,q}(x)$ at $x=1/n$.

This matters because it separates three different problems that should not be conflated:

- constructing a localized test function compatible with Kim-Tao's trace architecture;
- making Lemma 3.3 / Corollary 3.4 uniform when $q=n^\eta$;
- proving actual numerator saving by coefficient variation, signed small-$x$ cancellation, or stratified weighted decay.

The validated guidance from the M22 audit is to build the quotient-family model next. A proof attempt before that model would lack the exact weighted strata it needs to control.

## Open Questions

1. Can the localized test $h_{\Delta,q}$ be realized inside the $h\circ f_{\Lambda_0}$ polynomial/support architecture without changing the proof object?

2. What are the actual quotient-family strata in the localized numerator $p_{\Delta,q}$ once Selberg weights and localized transform weights are included?

3. Does $p_{\Delta,q}$ exhibit coefficient variation, direct small-$x$ cancellation, or stratified weighted decay strong enough to give positive $\beta$?

4. Can the MPvH/Witten-zeta, Nau boundedness, and MP23 rank-two decay inputs be made uniform for $q=n^\eta$ in the endpoint-beating band?

5. If the quotient-family model fails to produce numerator saving, should the compact-support local-window route be closed in favor of noncompact geometric-tail trace methods?

## References

No `REFERENCES.md` file exists in the workspace. This report therefore cites the local source materials used for cycles 31-33:

- Kim and Tao paper files: `2603.01127.pdf`, `2603.01127.txt`.
- Cycle 31 sessions: `169954ce-48cf-472a-a28b-a2db5ff61bbd`, `25259870-a419-447a-a2ff-67239e24ee31`, `26b77f9e-e136-492b-9b7d-171698b029c6`.
- Cycle 32 sessions: `69efb200-e06c-4da7-935b-393262fdf225`, `7978fb53-3b20-4f6d-ab22-dd74fe347a34`, `97e2b0bd-de7c-4716-a0a7-5c4e9b562f15`.
- Cycle 33 sessions: `36c56594-f3e6-4cae-9d5e-430065bb65bc`, `ffacb468-1319-42d2-9539-d95f7c9cee99`, `369b8204-7b26-4734-8b3a-e4afcb973eca`.
- M20 artifacts: `docs/proof_ledger/long_support_trace_variance_requirement.md`, `reports/extension_candidates/m20_long_support_trace_variance_requirement.md`, `data/extension_candidates/long_support_variance_budget.csv`, `data/extension_candidates/long_support_variance_summary.csv`.
- M21 artifacts: `docs/proof_ledger/trace_side_long_support_variance_template.md`, `reports/extension_candidates/m21_trace_side_long_support_variance_template.md`, `data/extension_candidates/trace_variance_template_budget.csv`, `data/extension_candidates/trace_variance_template_summary.csv`.
- M22 artifacts: `docs/proof_ledger/trace_corollary34_localized_numerator_target.md`, `reports/extension_candidates/m22_trace_corollary34_uniform_coefficient_variation_target.md`, `data/extension_candidates/corollary34_target_budget.csv`, `data/extension_candidates/corollary34_target_summary.csv`.

## Appendix: Implementation Details

### Code Organization

Cycle 31 added:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/analyze_long_support_variance_budget.py` | 278 | Computes M20 long-support variance-saving budgets for trace and pre-trace local-window routes. |
| `tests/test_long_support_variance_budget.py` | 99 | Tests M20 support thresholds, loss ratios, Chebyshev inequalities, endpoint logic, and true median computation. |
| `docs/proof_ledger/long_support_trace_variance_requirement.md` | 180 | Records the M20 exponent-budget theorem template. |
| `reports/extension_candidates/m20_long_support_trace_variance_requirement.md` | 113 | Summarizes the M20 decision and generated diagnostics. |

Cycle 32 added:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/analyze_trace_variance_template_budget.py` | 268 | Computes M21 beta-model budgets for the fixed-energy trace-side theorem template. |
| `tests/test_trace_variance_template_budget.py` | 94 | Tests M21 required beta, support validity, endpoint-beating logic, and no-saving baseline behavior. |
| `docs/proof_ledger/trace_side_long_support_variance_template.md` | 191 | States the trace-side long-support theorem template and dependency map. |
| `reports/extension_candidates/m21_trace_side_long_support_variance_template.md` | 160 | Summarizes the M21 theorem target and decision. |

Cycle 33 added:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/analyze_corollary34_target_budget.py` | 245 | Computes M22 localized numerator target budgets and success regions. |
| `tests/test_corollary34_target_budget.py` | 90 | Tests M22 beta algebra, support validity, endpoint logic, monotonic savings, and baseline failures. |
| `docs/proof_ledger/trace_corollary34_localized_numerator_target.md` | 228 | Defines the localized numerator and sufficient target classes. |
| `reports/extension_candidates/m22_trace_corollary34_uniform_coefficient_variation_target.md` | 111 | Summarizes the M22 numerator target and proof-facing decision. |

### Generated Data

| Dataset | Data rows |
|---|---:|
| `data/extension_candidates/long_support_variance_budget.csv` | 4,356 |
| `data/extension_candidates/long_support_variance_summary.csv` | 12 |
| `data/extension_candidates/trace_variance_template_budget.csv` | 11,664 |
| `data/extension_candidates/trace_variance_template_summary.csv` | 81 |
| `data/extension_candidates/corollary34_target_budget.csv` | 10,368 |
| `data/extension_candidates/corollary34_target_summary.csv` | 72 |

### Figure Inventory

| Figure | Size |
|---|---|
| `reports/figures/m20_required_variance_saving.png` | 1530 x 936 |
| `reports/figures/m20_long_support_feasibility_map.png` | 1475 x 1007 |
| `reports/figures/m21_trace_template_beta_thresholds.png` | 1494 x 936 |
| `reports/figures/m21_trace_template_plausibility_regions.png` | 1512 x 972 |
| `reports/figures/m22_corollary34_target_success_regions.png` | 1440 x 1120 |
| `reports/figures/m22_required_numerator_saving.png` | 1152 x 800 |

### Validation Results

Cycle validators reported the following:

- M20: validated after one audit repair to true median computation. Python compile, analyzer, tests, figure checks, `promise_check`, and `org_check` passed.
- M21: validated with no critical or moderate findings. Python compile, analyzer, tests, independent formula checks, figure checks, `promise_check`, and `org_check` passed.
- M22: validated with no critical or moderate findings. Python compile, analyzer, tests, independent CSV formula checks, figure checks, `promise_check`, and `org_check` passed.

After the reporter manifest update, the following checks were rerun:

```text
python3 -m long_exposure.tools.promise_check .
events: 88, plan milestones: 22
exit code: 0, historical warnings only

python3 -m long_exposure.tools.org_check .
exit code: 0, historical warnings only
```

The historical `promise_check` warnings concern one noncanonical old `docs/paper_map/` artifact path and orphaned prior periodic reports. The historical `org_check` warnings concern root paper/live-run files and older figures under `docs/`. These warnings predate cycles 31-33.

### Manifest Snapshot

`MANIFEST.md` was replaced with a current snapshot after M22. It contains:

| Metric | Value |
|---|---:|
| Manifest lines | 154 |
| Campaign scripts | 35 |
| Campaign script lines | 9,000 |
| Campaign test files | 23 |
| Campaign test lines | 1,892 |
| Markdown/DOT/PNG documentation artifacts under `docs/`, `reports/`, and `audits/` | 129 |
| PNG figures under `reports/figures/` | 55 |
| Canonical CSV datasets under `data/` | 60 |
| Promise ledger events | 88 |

There was no `## Key Files` section in the prior manifest, so no final-reporter-owned section needed preservation.

### Cross-Reference Map

| Origin | Consuming artifact | Role |
|---|---|---|
| M17 variance criterion | M20 budget | Supplies the Chebyshev variance-to-window-count inequality. |
| M18 support map | M20 budget | Converts long support into $q$ growth and trace/pre-trace losses. |
| M19 Fourier obstruction | M20 budget | Forces $\eta\ge d$ in the bulk and $\eta\ge d/2$ at the edge. |
| M20 long-support budget | M21 theorem template | Selects fixed-energy trace-side variance as the plausible compact-support continuation. |
| M21 theorem template | M22 numerator target | Narrows the missing variance theorem to localized Lemma 3.3 / Corollary 3.4 numerator control. |
| M22 numerator target | next milestone | Recommends `M23-localized-trace-numerator-quotient-family-model`. |
