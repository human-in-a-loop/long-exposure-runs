---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 34-36"
date: "2026-05-16"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 34-36

## Abstract

Cycles 34-36 closed the current fixed-energy local-window investigation as an immediate transform/support-tuning program and preserved it as a precise follow-up problem. The work continued the branch developed in M16-M22: local spectral windows below the endpoint-subtraction scale require a direct trace-side variance saving, and M22 had reduced the needed saving to control of a localized Corollary 3.4 numerator in the Kim--Tao trace expansion.

Cycle 34, milestone M23, built a stratum-preserving proxy model for that localized numerator. It identified the paper-level summation variables, the Selberg/geodesic and localized-transform weights, and the quotient-polynomial numerator terms $Q_{\gamma_1^{k_1},\gamma_2^{k_2}}$. The model generated 4,800 proxy rows and showed that compact support and the basic Paley-Wiener-scaled envelope still leave a large rank-two/unknown quotient-family obstruction. Only an optimistic added decay model changed the scale enough to motivate the next question.

Cycle 35, milestone M24, tested whether that optimistic decay can come from the localized transform and geodesic weights already present in the Kim--Tao compact-support architecture. The answer, after an audit repair, was no. The localized transform scales as
\[
h_\delta^\vee(t)=\delta_r e^{-i r_0t}\widehat{\phi}(\delta_r t),
\]
so compatible decay is in $u=t\delta_r$, not in support length $t$. The repaired numerical model had zero success rows after requiring negative net growth.

Cycle 36, milestone M25, synthesized M16-M24 into a branch decision. The final decision is `preserve_as_followup_problem`: the compact-support local-window route remains mathematically open only through a new coefficient-variation or small-$x$ theorem for the actual surface-group Corollary 3.4 quotient-polynomial numerator, while the noncompact alternative would require a separate trace-tail architecture with geometric error control and a tail rate above actual growth.

## Introduction

The campaign studies Kim and Tao's paper *Eigenvalue rigidity of hyperbolic surfaces in the random cover model* from two angles: first, reconstructing the proof architecture, and second, searching for extensions. The local-window branch began because inherited global rigidity estimates do not directly yield fixed-energy local spectral statistics at polynomially shrinking windows. Earlier milestones established the following chain:

```text
endpoint subtraction
-> variance requirement
-> Paley-Wiener support scaling
-> long-support trace budget
-> localized Corollary 3.4 numerator
```

The central quantity in cycles 34-36 is the localized trace-side numerator that appears after inserting a fixed-energy bulk test into the Kim--Tao Lemma 3.3 / Corollary 3.4 package. In the notation used by the campaign, the target numerator is

```text
p_{Delta,q}(x)
  = sum_{gamma1,gamma2} sum_{k1,k2>=1}
      a(gamma1,k1) a(gamma2,k2)
      h_{Delta,q}^vee(k1 ell_gamma1)
      h_{Delta,q}^vee(k2 ell_gamma2)
      Q_{gamma1^k1,gamma2^k2}(x),
```

where `gamma1,gamma2` range over primitive geodesics, `k1,k2` are primitive-power indices, `a(gamma,k)=ell_gamma/(2 sinh(k ell_gamma/2))` is the Selberg/geodesic weight, and `Q` is the polynomial numerator from the two-trace random-cover expansion.

The M21/M22 beta-saving condition remained the gate throughout these cycles. For bulk window width $\Delta=n^{-d}$ and support $q=n^\eta$, with $d>\alpha_W$ and $\eta\ge d$, the trace-side saving must satisfy

\[
\beta > 2\kappa\eta + 2d - 1.
\]

Cycles 34-36 asked whether this saving can be made plausible from the weighted quotient family and transform/geodesic weights already present in the compact-support trace architecture.

## Approach

The work used a chronological narrowing strategy.

First, M23 modeled the localized numerator as a weighted quotient-family table. The purpose was not to enumerate the actual Kim--Tao surface-group quotient family exactly. It was to preserve the exact paper indices and weights while tagging which parts are proxy annotations: quotient type, rank proxy, cyclic status, and the stratum $d=C-V$.

Second, M24 tested the one mechanism that M23 had left open: whether localized transform weights could justify an optimistic support-length decay. This cycle analyzed compact support, Paley-Wiener/Schwartz envelopes, vanishing-moment variants, and a noncompact Gaussian-like contrast.

Third, M25 synthesized the entire local-window branch from M16 through M24. It separated proved consequences of Kim--Tao, conditional theorem templates, toy/proxy evidence, analytic obstructions, and open theorem targets. The output was a branch decision, not another parameter sweep.

## Source Inventory and Timeline

### Cycle 34: M23 Localized Trace Numerator Quotient-Family Model

Sources:

- Researcher session `ffb97519-fc19-472c-a317-596b80290261`
- Worker session `129d8ea5-7a08-4a98-9aa8-81bea15c0fff`
- Auditor session `740c8274-d579-4a42-9d6b-79bff6b4d4b3`
- `docs/proof_ledger/localized_trace_numerator_quotient_family_model.md`
- `reports/extension_candidates/m23_localized_trace_numerator_quotient_family_model.md`
- `scripts/model_localized_trace_numerator_quotients.py`
- `tests/test_localized_trace_numerator_quotients.py`
- `data/extension_candidates/localized_trace_numerator_quotient_terms.csv`
- `data/extension_candidates/localized_trace_numerator_strata_summary.csv`
- `data/extension_candidates/localized_trace_numerator_weight_taxonomy.csv`

The researcher brief set M23's goal: convert the M22 localized numerator target into an inspectable quotient-family and weight model. The worker built the proof note, report, script, tests, three CSV files, and two figures. The auditor validated the package with no critical or moderate findings.

M23's decision was `attempt analytic weight-decay lemma next`.

### Cycle 35: M24 Localized Transform/Geodesic Weight Decay Obstruction

Sources:

- Researcher session `bb9fc699-c5f4-4356-8663-d4e1ff751d05`
- Worker session `0f873bda-b6b9-483c-b180-0a527f25ad5d`
- Auditor session `9f6cd3c5-9852-4cd4-aad9-e133c5ef13e6`
- `docs/proof_ledger/localized_transform_geodesic_weight_decay.md`
- `reports/extension_candidates/m24_localized_transform_geodesic_weight_decay_obstruction.md`
- `scripts/analyze_localized_transform_weight_decay.py`
- `tests/test_localized_transform_weight_decay.py`
- `data/extension_candidates/localized_transform_weight_decay.csv`
- `data/extension_candidates/localized_transform_decay_summary.csv`

The researcher brief asked whether any paper-compatible transform estimate could justify M23's optimistic decay. The worker built the analytic note, report, script, tests, two CSV files, and two figures.

The auditor found one moderate issue: the original script classified every noncompact Gaussian-tail row as a success by model type, even when the tail rate was weaker than the growth proxies. The repair required success to mean negative net balance. After repair, the M24 summary became:

- total rows: 960
- M22 support-and-endpoint rows: 396
- compact-route-obstructed rows: 198
- conditional zero-mean/not-count-positive rows: 99
- contrast-insufficient rows: 99
- success rows: 0

M24's decision was to close the compact-support local-window route as a transform-weight damping mechanism.

### Cycle 36: M25 Local-Window Route Synthesis and Branch Decision

Sources:

- Researcher session `f0e0837f-7596-4111-a86f-2623c0aedd51`
- Worker session `0e02b319-0d1c-4f9a-a082-2506a17bea4f`
- Auditor session `5161c9dd-0579-4423-89c1-8a2a278a2eb7`
- `docs/proof_ledger/local_window_branch_decision_record.md`
- `reports/extension_candidates/m25_local_window_route_synthesis_and_branch_decision.md`
- `reports/final/local_window_followup_problem_statement.md`
- `scripts/build_local_window_route_synthesis.py`
- `tests/test_local_window_route_synthesis.py`
- `data/extension_candidates/local_window_route_evidence_index.csv`
- `data/extension_candidates/local_window_route_decision_table.csv`

The researcher brief asked for a decision-grade synthesis of M16-M24 rather than another transform/support parameter test. The worker built the branch-decision record, final follow-up problem statement, synthesis report, script, tests, two CSV files, and two figures.

The auditor found one moderate usability issue: the M25 report used figure paths that were wrong relative to the report directory. The auditor repaired both links and verified they resolve. The mathematical decision remained unchanged.

M25's decision was `preserve_as_followup_problem`.

## Findings

### Finding 1: M23 Made the Localized Numerator Inspectable

M23's main result was a schema for the localized Corollary 3.4 numerator. The exact paper-level indices are:

- primitive geodesics `gamma1,gamma2 in P(X)`,
- primitive powers `k1,k2 >= 1`,
- Selberg/geodesic weights `ell_gamma/(2 sinh(k ell_gamma/2))`,
- localized transform weights `h_{Delta,q}^vee(k ell_gamma)`,
- polynomial numerator objects `Q_{gamma1^k1,gamma2^k2}`.

The generated proxy table deliberately separated exact objects from annotations. The quotient identifier, rank proxy, cyclic flag, surface-group uncertainty tag, and $d=C-V$ stratum are modeling annotations, not exact Kim--Tao quotient data.

The script generated 4,800 bounded proxy rows and 27 support-valid summary rows. The weighted total-variation proxy by transform model was:

| Transform model | Total weighted-TV proxy |
|---|---:|
| compact support | 619646.329313 |
| Paley-Wiener scaled | 244563.796952 |
| optimistic decay | 16199.197116 |

The interpretation was that compact support and the basic scaled Paley-Wiener envelope do not remove the aggregate obstruction. The optimistic decay model changes the scale, but M23 did not claim that such decay is available in the Kim--Tao architecture.

![Total-variation proxy by localized numerator stratum and transform-weight model. The plot records that compact and Paley-Wiener-scaled weights still leave large rank-two and unknown surface-group proxy contributions.](reports/figures/m23_localized_quotient_strata_tv.png)

![Localized transform damping compared with quotient-family growth proxies across support bins. The optimistic model motivates the M24 question but is not a proved estimate.](reports/figures/m23_transform_weight_vs_family_growth.png)

The M23 auditor validated the model as a proxy, not a proof. The auditor specifically checked that unknown surface-group rows were not counted as M4-certified independent-permutation rows.

### Finding 2: M24 Ruled Out Transform Damping Inside the Compact-Support Architecture

M24 answered the question left by M23: can the optimistic decay come from the localized transform and geodesic weights already present in the compact-support trace formula?

The central scaling identity was

\[
h_\delta^\vee(t)=\delta_r e^{-ir_0t}\widehat{\phi}(\delta_r t),
\]

where

\[
\delta_r=\frac{\Delta}{2r_0}+O(\Delta^2).
\]

For support $q=n^\eta$ and width $\Delta=n^{-d}$, the endpoint scaled variable is

\[
u_{\mathrm{endpoint}}=q\delta_r \asymp n^{\eta-d}.
\]

This means decay is controlled by $u=t\delta_r$, not by $t$ alone. At the minimal support scale $\eta=d$, the endpoint is constant scale. When $\eta>d$, smooth tails can decay in $n^{\eta-d}$, but this is still not an exponential-in-support factor such as $\exp(-ct)$.

M24 classified the candidate mechanisms as follows:

| Mechanism | Compatibility | M24 verdict |
|---|---|---|
| compact support only | compatible | obstructed |
| smooth Paley-Wiener/Schwartz envelope | compatible | obstructed against growth proxies |
| vanishing moments | conditional | not count-positive for the target statistic |
| noncompact Gaussian-like tail | incompatible with compact support | contrast only; repaired rate insufficient |

The audit repair was important. The worker initially reported 99 noncompact contrast successes, but the auditor found that success had been assigned by model type rather than by net balance. After repair, success required `net_log < 0`, and the repaired dataset had zero success rows.

![Scaled localized transform envelopes versus `t delta_r`. The figure illustrates that the compact-support-compatible envelope changes in the scaled variable, not directly in support length.](reports/figures/m24_transform_envelope_scaling.png)

![Net transform damping versus geodesic/family growth proxies. After audit repair, the noncompact contrast at rate 0.18 is classified as insufficient against the tested growth proxies.](reports/figures/m24_geodesic_growth_vs_transform_decay.png)

M24 therefore closed only one mechanism: transform/geodesic weights do not supply the needed optimistic damping inside the compact-support Paley-Wiener architecture. It did not prove that coefficient variation is impossible.

### Finding 3: M25 Preserved the Local-Window Route as a Follow-Up Problem

M25 converted M16-M24 into a decision record. The evidence chain was:

| Milestone | Evidence label | Implication |
|---|---|---|
| M16 | proved from Kim--Tao | Inherited global estimates only control windows above endpoint-subtraction scales. |
| M17 | conditional theorem template | Endpoint-beating local windows require direct smoothed-window variance saving. |
| M18 | analytic obstruction | Retuning Kim--Tao test functions is insufficient; trace-side localization is the plausible route. |
| M19 | analytic obstruction | Bulk $\Delta=n^{-d}$ forces polynomial support $q=n^\eta$ with $\eta\ge d$. |
| M20 | conditional theorem template | Polynomial support creates a long-support variance-saving budget. |
| M21 | conditional theorem template | `LSTV_trace(eta,beta)` suffices if $\beta>2\kappa\eta+2d-1$. |
| M22 | open theorem | The trace variance target reduces upstream to localized Corollary 3.4 numerator control. |
| M23 | toy/proxy evidence | Quotient-family growth dominates absent extra damping; surface-group uncertainty remains. |
| M24 | analytic obstruction | Compact-support transform/geodesic weights decay in $t\delta_r$, not $t$. |

![Dependency and obstruction chain from M16 endpoint subtraction to M24 transform-damping obstruction.](reports/figures/m25_local_window_obstruction_chain.png)

![Decision matrix comparing compact coefficient variation, noncompact trace-tail architecture, and branch closure/follow-up preservation.](reports/figures/m25_branch_decision_matrix.png)

M25 separated the surviving paths into two theorem targets.

The compact-support target is a localized coefficient-variation or small-$x$ theorem for the actual Kim--Tao quotient-polynomial numerator. A sufficient estimate would have the form

```text
p_{Delta,q}(1/n) / Q_id(1/n)
  <= n q^A n^{-sigma+o(1)}
```

after exact identity/diagonal treatment, with

\[
(2\kappa-A)\eta+\sigma > 2\kappa\eta+2d-1.
\]

This theorem must concern the actual folded surface-group quotient family. Independent-permutation templates, M23 proxy strata, and transform-envelope damping do not suffice.

The noncompact target is a different trace architecture. It would need:

1. a noncompact spectral localizer that still approximates the desired fixed-energy window,
2. geometric-side convergence and truncation control for the noncompact trace formula,
3. a tail rate stronger than the actual geodesic and quotient-family growth rate.

M25's final branch decision was:

```text
preserve_as_followup_problem
```

The local-window branch is not declared false. It is no longer the best immediate same-axis empirical direction because every surviving route requires a new theorem.

## Discussion

Cycles 34-36 changed the status of the local-window branch from an active parameter-search route to a precise obstruction-and-follow-up package.

Before these cycles, M22 had identified the localized Corollary 3.4 numerator as the target but had not separated the possible mechanisms. M23 supplied the missing schema: it showed where the summation variables, transform weights, Selberg weights, quotient tags, cyclic/diagonal status, and $d=C-V$ strata enter. That made the proof target inspectable.

M24 then tested the most accessible mechanism, transform damping. The result was negative inside the compact-support architecture. The key point is not only numerical. It is structural: Fourier scaling gives decay in $t\delta_r$, while the optimistic M23 model required decay in the support variable $t$ itself. This prevents the compact-support transform from carrying the beta saving by itself.

M25 then made the branch decision explicit. The compact route is now a named theorem target, not a broad instruction to "prove the missing variance theorem." The noncompact route is also named, but it would require changing the trace architecture rather than retuning the existing compact-support construction.

The campaign should therefore pivot away from same-axis local-window cycles unless it deliberately chooses one of those theorem-development branches. The local-window work remains valuable because it records exactly what a future contribution would need to prove.

## Open Questions

1. **Localized coefficient variation.** Does the actual Kim--Tao Lemma 3.3 / Corollary 3.4 quotient-polynomial family satisfy a localized small-$x$ or coefficient-variation estimate strong enough to meet
   \[
   (2\kappa-A)\eta+\sigma > 2\kappa\eta+2d-1?
   \]

2. **Surface-group quotient structure.** Which features of the folded surface-group quotient family are lost in independent-permutation or free-group proxy models, and can any part of M23's stratum schema be upgraded to an exact enumeration?

3. **Noncompact trace tails.** Is there a noncompact spectral localizer with a trace-formula error theorem strong enough to control the geometric side at a tail rate exceeding actual quotient/geodesic growth?

4. **Alternative high-value targets.** Since M25 recommends preserving the local-window route rather than continuing same-axis sweeps, the next campaign direction should avoid immediate dependence on the full localized Corollary 3.4 coefficient-variation theorem.

## References

No `REFERENCES.md` file was present in the workspace during this reporter pass. The sources used for this report are therefore local campaign records:

- Kim--Tao paper files: `2603.01127.pdf`, `2603.01127.txt`.
- Cycle 34 sessions: researcher `ffb97519-fc19-472c-a317-596b80290261`, worker `129d8ea5-7a08-4a98-9aa8-81bea15c0fff`, auditor `740c8274-d579-4a42-9d6b-79bff6b4d4b3`.
- Cycle 35 sessions: researcher `bb9fc699-c5f4-4356-8663-d4e1ff751d05`, worker `0f873bda-b6b9-483c-b180-0a527f25ad5d`, auditor `9f6cd3c5-9852-4cd4-aad9-e133c5ef13e6`.
- Cycle 36 sessions: researcher `f0e0837f-7596-4111-a86f-2623c0aedd51`, worker `0e02b319-0d1c-4f9a-a082-2506a17bea4f`, auditor `5161c9dd-0579-4423-89c1-8a2a278a2eb7`.
- M23 artifacts: `docs/proof_ledger/localized_trace_numerator_quotient_family_model.md`, `reports/extension_candidates/m23_localized_trace_numerator_quotient_family_model.md`, `data/extension_candidates/localized_trace_numerator_quotient_terms.csv`, `data/extension_candidates/localized_trace_numerator_strata_summary.csv`, `data/extension_candidates/localized_trace_numerator_weight_taxonomy.csv`.
- M24 artifacts: `docs/proof_ledger/localized_transform_geodesic_weight_decay.md`, `reports/extension_candidates/m24_localized_transform_geodesic_weight_decay_obstruction.md`, `data/extension_candidates/localized_transform_weight_decay.csv`, `data/extension_candidates/localized_transform_decay_summary.csv`.
- M25 artifacts: `docs/proof_ledger/local_window_branch_decision_record.md`, `reports/extension_candidates/m25_local_window_route_synthesis_and_branch_decision.md`, `reports/final/local_window_followup_problem_statement.md`, `data/extension_candidates/local_window_route_evidence_index.csv`, `data/extension_candidates/local_window_route_decision_table.csv`.

## Appendix: Implementation Details

### Code Organization

Cycle 34 added:

- `scripts/model_localized_trace_numerator_quotients.py` — 288 lines.
- `tests/test_localized_trace_numerator_quotients.py` — 88 lines.
- `docs/proof_ledger/localized_trace_numerator_quotient_family_model.md` — 144 lines.
- `reports/extension_candidates/m23_localized_trace_numerator_quotient_family_model.md` — 68 lines.

Cycle 35 added:

- `scripts/analyze_localized_transform_weight_decay.py` — 296 lines.
- `tests/test_localized_transform_weight_decay.py` — 91 lines.
- `docs/proof_ledger/localized_transform_geodesic_weight_decay.md` — 122 lines.
- `reports/extension_candidates/m24_localized_transform_geodesic_weight_decay_obstruction.md` — 76 lines.

Cycle 36 added:

- `scripts/build_local_window_route_synthesis.py` — 279 lines.
- `tests/test_local_window_route_synthesis.py` — 78 lines.
- `docs/proof_ledger/local_window_branch_decision_record.md` — 98 lines.
- `reports/extension_candidates/m25_local_window_route_synthesis_and_branch_decision.md` — 107 lines.
- `reports/final/local_window_followup_problem_statement.md` — 59 lines.

### Generated Data

Cycle 34 generated:

- `data/extension_candidates/localized_trace_numerator_quotient_terms.csv` — 4,800 data rows.
- `data/extension_candidates/localized_trace_numerator_strata_summary.csv` — 27 data rows.
- `data/extension_candidates/localized_trace_numerator_weight_taxonomy.csv` — 7 data rows.

Cycle 35 generated:

- `data/extension_candidates/localized_transform_weight_decay.csv` — 960 data rows.
- `data/extension_candidates/localized_transform_decay_summary.csv` — 12 data rows.

Cycle 36 generated:

- `data/extension_candidates/local_window_route_evidence_index.csv` — 9 data rows.
- `data/extension_candidates/local_window_route_decision_table.csv` — 3 data rows.

### Figure Inventory

- `reports/figures/m23_localized_quotient_strata_tv.png` — 2240x768.
- `reports/figures/m23_transform_weight_vs_family_growth.png` — 1440x880.
- `reports/figures/m24_transform_envelope_scaling.png` — 1475x900.
- `reports/figures/m24_geodesic_growth_vs_transform_decay.png` — 1475x900.
- `reports/figures/m25_local_window_obstruction_chain.png` — 1980x576.
- `reports/figures/m25_branch_decision_matrix.png` — 1332x756.

### Validation Results

Cycle 34 validation:

- `python3 -m py_compile scripts/model_localized_trace_numerator_quotients.py tests/test_localized_trace_numerator_quotients.py`: passed.
- `python3 scripts/model_localized_trace_numerator_quotients.py`: regenerated 4,800 term rows, 27 summary rows, taxonomy, and two figures.
- `python3 tests/test_localized_trace_numerator_quotients.py`: passed.
- Auditor CSV consistency check: zero summary mismatches.
- `promise_check`: passed with historical warnings; 91 events and 23 plan milestones.
- `org_check`: passed with historical warnings.

Cycle 35 validation after audit repair:

- `python3 -m py_compile scripts/analyze_localized_transform_weight_decay.py tests/test_localized_transform_weight_decay.py`: passed.
- `python3 scripts/analyze_localized_transform_weight_decay.py`: regenerated 960 rows and 12 summary rows.
- `python3 tests/test_localized_transform_weight_decay.py`: passed.
- Figure checks: both M24 figures readable and nonblank.
- `promise_check`: passed with historical warnings.
- `org_check`: passed with historical warnings.
- Repaired classification: zero success rows after requiring negative net growth.

Cycle 36 validation after audit repair:

- Direct relative-link check for the M25 report figures: passed.
- `python3 -m py_compile scripts/build_local_window_route_synthesis.py tests/test_local_window_route_synthesis.py`: passed.
- `python3 scripts/build_local_window_route_synthesis.py`: regenerated 9 evidence rows, 3 decision rows, and two figures.
- `python3 tests/test_local_window_route_synthesis.py`: passed.
- Figure checks: both M25 figures readable and nonblank.
- `promise_check`: passed with historical warnings; 99 events and 25 plan milestones.
- `org_check`: passed with historical warnings.

Reporter validation after updating `MANIFEST.md`:

- `python3 -m long_exposure.tools.promise_check .`: passed with historical warnings; 99 events and 25 plan milestones.
- `python3 -m long_exposure.tools.org_check .`: passed with historical warnings.
- `MANIFEST.md`: updated to 142 lines.

Historical warnings included old noncanonical `docs/paper_map/` references, orphan prior cycle reports under `reports/cycles/`, root paper/prompt/live-run files, and older figures under `docs/`. These were already present and were not treated as cycle 34-36 blockers.

### Manifest Snapshot

The refreshed `MANIFEST.md` records:

- 34 Python scripts, 9,491 total script lines.
- 26 Python tests, 2,149 total test lines.
- 67 CSV datasets under `data/`.
- 61 PNG figures under `reports/figures/`.
- 143 documentation/report artifacts under `docs/`, `reports/`, and `audits/`.
- 99 promise ledger events.
- 25 plan milestones.

### Cross-Reference Map

- M22 localized numerator target -> M23 quotient-family model.
- M23 quotient-family proxy rows -> M24 transform/geodesic damping test.
- M24 repaired obstruction -> M25 branch synthesis.
- M25 branch synthesis -> `reports/final/local_window_followup_problem_statement.md`.
- M25 decision -> next research direction should pivot away from same-axis local-window empirical cycles unless starting a deliberate theorem-development branch.
