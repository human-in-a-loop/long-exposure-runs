---
created: 2026-05-14T16:20:00Z
cycle: 53
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-8
---

# Weak-Norm And Topology-Mismatch Branch

This branch separates two different claims. Measuring the solution itself in a weak norm can be a bad certificate for a stronger physical norm. Measuring a coercive differential residual in its matched dual norm is different: a classical stability estimate may make that residual a valid certificate.

## Candidate Summary

| ID | Objective or residual norm | Bad family or obstruction | Scaling law | Physical-error behavior | Certificate/correction | Status |
|---|---|---|---|---|---|---|
| WT-1 / CAT-06 | Identity task \(u=0\) on \((0,2\pi)\), \(J_s(u)=\|u\|_{H^{-s}}^2\). | \(L^2\)-normalized sine modes \(u_k\). | \(\|u_k\|_{L^2}=1\), \(J_s(u_k)=(1+k^2)^{-s}\sim k^{-2s}\). | \(L^2\) error remains one while weak objective vanishes. | Measure in \(L^2\), add compactness/regularity or bandwidth bounds, or use a matched operator stability estimate. | theorem_quality and toy_demonstrated |
| WT-2 | Direct weak objective \(J_\epsilon=\|u_\epsilon\|_{H^{-1}}^2\) for a localized defect on a periodic unit interval. | Mean-zero interior bump-dipole \(u_\epsilon=\epsilon^{-1/2}[\phi((x-x_0+0.45\epsilon)/\epsilon)-\phi((x-x_0-0.45\epsilon)/\epsilon)]\), normalized to \(\|u_\epsilon\|_{L^2}=1\). | Numerically \(J_\epsilon\) decreases with support scale; fitted log-log slope is \(1.84\) over the tested range after suppressing the mean mode. | \(L^2\) error and local defect certificate remain \(O(1)\); pointwise amplitude grows as the support shrinks. | Strong/local residual check, \(L^2\) certificate, local sampling, or compactness/regularity bound excluding concentration. | toy_demonstrated |
| WT-3 / CAT-04 | Matched elliptic residual \(-u''=f\), exact Dirichlet trace, \(J(u)=\|-u''-f\|_{H^{-1}}^2\). | Attempted high-frequency or localized error \(e=u-u^\star\). | If \(-e''=r\), then \(\|e\|_{H_0^1}\le C\|r\|_{H^{-1}}\). | Physical \(H^1_0\) error is controlled by the residual; no weak-topology failure under matched hypotheses. | Lax-Milgram/energy estimate with exact trace terms. | stability_baseline |

## WT-1 / CAT-06: Oscillatory Weak-Topology Failure

For the identity residual equation \(u=0\), the training objective \(J_s(u)=\|u\|_{H^{-s}}^2\) is weaker than the physical \(L^2\) target. With \(u_k\) chosen as an \(L^2\)-normalized sine mode,
\[
\|u_k\|_{L^2}=1,\qquad \|u_k\|_{H^{-s}}^2=(1+k^2)^{-s}\to0.
\]
This is an objective-function failure, not an optimizer failure. The existing toy artifacts are `scripts/weak_norm_high_frequency_toy.py`, `data/weak_norm_scaling.csv`, `data/weak_norm_scaling.png`, and `tests/test_weak_norm_high_frequency_toy.py`.

## WT-2: Localized Defect In A Weak Topology

The localized family tests concentration rather than oscillation. The implementation uses a mean-zero pair of smooth compact interior bumps so the zero Fourier mode is removed; this avoids overstating a result that would otherwise be limited by nonzero mean content. The defect is normalized to \(\|u_\epsilon\|_{L^2}=1\), while the direct negative norm \(\|u_\epsilon\|_{H^{-1}}^2\) decreases as the support scale \(\epsilon\) shrinks.

The certificate is intentionally simple: the \(L^2\) norm and the local maximum remain nonzero, so a strong norm, local sampling certificate, or regularity/compactness bound detects the defect. This is a topology-mismatch toy, not a claim about a coercive PDE residual.

## WT-3 / CAT-04: Matched Elliptic Residual Baseline

The Poisson/elliptic baseline is a rigorous obstruction to a false weak-norm claim. Let \(e=u-u^\star\in H_0^1(0,1)\) and \(-e''=r\). Testing the weak equation with \(e\) gives
\[
\|e'\|_{L^2}^2=\langle r,e\rangle\le \|r\|_{H^{-1}}\|e\|_{H_0^1},
\]
so \(\|e\|_{H_0^1}\le \|r\|_{H^{-1}}\) up to the chosen norm convention. Thus a residual measured in the correct dual norm of a coercive operator is a certificate, not a residual-minimization failure. This distinction is the main guardrail for M-8.

## M-8 Closure Status

The branch now has three explicit weak/topology candidates: one oscillatory failure, one localized concentration failure, and one matched-operator stability baseline. The failure cases show weak training norms can vanish while \(L^2\) scale remains; the baseline explains why this does not apply to matched elliptic residual minimization with exact traces.
