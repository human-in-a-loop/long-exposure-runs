---
created: 2026-05-14T03:45:00Z
cycle: 1
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-3
---

# Publishability Note: Fixed-Collocation Blind Spot

## What The Result Proves

The result proves a clean objective-function failure for fixed finite collocation. For the ODE \(u'=0\) with zero endpoint data, a smooth oscillatory sequence can make every sampled derivative residual and endpoint penalty exactly zero while its \(L^2\) distance from the true solution remains \(\sqrt{3/8}\). This separates the failure of the residual objective from optimizer failure: the bad functions are explicit global minimizers of the sampled loss.

## What It Does Not Prove

It does not prove that PINNs, neural operators, or residual minimization fail in general. It also does not prove failure of the continuous residual \(\|u'\|_{L^2}\), which controls the physical error by the fundamental theorem of calculus. The theorem is about fixed finite sampling over a trial class large enough to oscillate between nodes.

## Why It Is Relevant

PINN and collocation training objectives often replace global residual control by sampled residual penalties. This example shows, in the smallest possible differential equation, that sampled residual agreement is not automatically a certificate of physical correctness. The failure mechanism is not neural-network-specific, which is a strength: it isolates the mathematical risk in the objective before optimization or architecture enters.

## Classical Numerical Analysis Framing

In classical language, the sampled residual plus endpoint penalties are a noncoercive seminorm on unrestricted smooth functions. The collocation set is not a norming set for the trial class, and the missing ingredient is control of between-node behavior. A fill-distance plus regularity estimate restores coercivity by bounding how far \(u'\) can move away from its sampled values on each cell; equivalent repairs could use quadrature control, inverse estimates on a finite-dimensional trial space, or direct continuous residual measurement.

## Likely Novelty

The mathematical ingredients are classical: Poincare-type estimates, fill-distance reasoning, and regularity bounds. The likely contribution is the compact scientific-ML reliability framing: an explicit residual objective with zero training loss and nonzero physical error, paired with an equally explicit sampled certificate that repairs exactly the missing mechanism.
