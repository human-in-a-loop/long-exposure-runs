---
created: 2026-05-16T17:50:00Z
cycle: 33
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M22-trace-corollary34-uniform-coefficient-variation-target
---

# M22 Trace Corollary 3.4 Uniform Coefficient-Variation Target

## Target

M22 localizes the Corollary 3.4 numerator in the M21 fixed-bulk trace statistic. For a localized trace test `h_{Delta,q}` with `Delta=n^(-d)`, `q=n^eta`, and `eta>=d`, define

```text
p_{Delta,q}(x)
 = sum_{gamma1,gamma2} sum_{k1,k2>=1}
     a(gamma1,k1) a(gamma2,k2)
     h_{Delta,q}^vee(k1 ell_gamma1)
     h_{Delta,q}^vee(k2 ell_gamma2)
     Q_{gamma1^k1,gamma2^k2}(x).
```

This is literally Kim--Tao's Corollary 3.4 numerator only if the localized window can be realized inside the paper-compatible `h o f_Lambda0` polynomial/support architecture. Otherwise it is a local analogue and the missing structural theorem is exactly the uniform Lemma 3.3/Corollary 3.4 package for that analogue.

## Exponent Algebra

The M21 baseline is

```text
Var Z_n <= n q^(2 kappa) = n^(1+2 kappa eta).
```

A candidate numerator control

```text
E G_n(h_{Delta,q})^2 <= n q^A n^(-sigma+o(1))
```

implies

```text
candidate_beta = (2 kappa - A) eta + sigma.
```

The fixed-bulk endpoint-beating local-window condition remains

```text
d > alpha_W,       eta >= d,       candidate_beta > 2 kappa eta + 2d - 1.
```

Equivalently, the numerator target itself must force `1+A eta-sigma < 2-2d`.

## Candidate Bounds

| target | sufficient bound | implied beta | main risk |
|---|---|---:|---|
| coefficient variation | absolute coefficient/tail control of `p_{Delta,q}` at `x=1/n` | `(2 kappa-A)eta+sigma` | may be too strong because it discards cancellation |
| direct small-`x` | signed control of `p_{Delta,q}(1/n)/Q_id(1/n)` | `(2 kappa-A)eta+sigma` | must hold near `1/n`, not only at `x=0` |
| stratified weighted | fixed `C-V` or quotient-power strata with Selberg/localized weights | `(2 kappa-A-omega)eta+sigma` for `W(q)=q^omega` | needs actual Kim--Tao quotient-family decomposition |

Pure Markov/interpolation baseline has `A=2 kappa`, `sigma=0`, so `candidate_beta=0`. It only succeeds in rows where the required beta is negative, which are bookkeeping rows rather than the useful obstruction range.

## Generated Budget

The analyzer `scripts/analyze_corollary34_target_budget.py` evaluates candidate numerator target types over fixed-bulk grids. It writes:

- `data/extension_candidates/corollary34_target_budget.csv`
- `data/extension_candidates/corollary34_target_summary.csv`
- `reports/figures/m22_corollary34_target_success_regions.png`
- `reports/figures/m22_required_numerator_saving.png`

The budget columns include `support_valid`, `endpoint_beating`, `required_beta`, `candidate_beta`, `local_window_success`, `target_type`, and `failure_reason`.

The generated grid has 10,368 rows. The failure/success classes are:

| class | rows |
|---|---:|
| support_invalid | 4752 |
| not_endpoint_beating | 3168 |
| conditional_success | 1498 |
| needs_more_numerator_saving | 950 |

For the representative `kappa=5`, `alpha_W=0.006` endpoint-beating support-valid band, each selected target has 36 `(d,eta)` pairs and required beta ranges from `-0.904` to `2.0`. Selected outcomes:

| target | successes / 36 | reading |
|---|---:|---|
| `baseline A=2k` | 15 | passes only the negative-threshold rows |
| `direct sigma=0.75` | 27 | fixed small-`x` saving handles most small-window rows |
| `CV A=2k-4` | 24 | coefficient-variation improvement helps but less than a constant direct saving on this grid |
| `stratified A=2k-4 W=q^-1` | 27 | stratified decay has the same tested success count as `sigma=0.75` |

Thus the grid shows nonempty conditional success regions for direct small-`x` and stratified weighted targets with positive `sigma`, reduced `A`, or decaying `W(q)`, but not for the no-saving Markov baseline wherever `required_beta>0`. M22 identifies a falsifiable numerator-level target rather than proving the M21 variance theorem.

![conditional success regions for candidate localized numerator bounds in the fixed-energy trace-side bulk band](reports/figures/m22_corollary34_target_success_regions.png)

![required numerator-level saving beyond the trace-side q^{2 kappa} loss as a function of d and eta](reports/figures/m22_required_numerator_saving.png)

## Feasibility Decision

Decision:

```text
needs quotient-family model before proof attempt
```

The localized numerator is now explicit enough to attack. But a proof attempt would be premature until the localized test family is shown to be paper-compatible and the weighted quotient-family decomposition of `p_{Delta,q}` is made concrete enough to test coefficient variation versus direct small-`x` cancellation. Existing Kim--Tao inputs supply Lemma 3.3 and Corollary 3.4 for the endpoint architecture; they do not already supply the localized numerator saving.

## Non-Claims

M22 does not prove beta saving, local spectral statistics, or an improved Kim--Tao exponent. It also does not treat pre-trace or edge windows. It isolates the trace-side fixed-bulk Corollary 3.4 numerator condition that would imply the M21 theorem if the needed uniform inputs were proved.
