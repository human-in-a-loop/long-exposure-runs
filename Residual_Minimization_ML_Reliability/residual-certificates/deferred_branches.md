---
created: 2026-05-14T04:20:00Z
cycle: 3
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-6
---

# Deferred Branches

## M-2: Continuous Norm-Mismatch Counterexample

M-2 is deferred because a valid continuous residual failure requires a genuinely noncoercive pairing between the residual training norm and the target physical error norm. The simple ODE and elliptic baselines inspected so far are stability examples when the residual and trace norms are matched: the continuous derivative residual for \(u'=0\) controls \(L^2\) error by the fundamental theorem of calculus, and analogous elliptic residual norms often control error through standard energy estimates. Treating those stable baselines as failures would blur the central distinction between continuous residual control and finite sampled collocation.

Future work should search for a precise weak-norm or topology mismatch, such as residual convergence in a norm too weak to control the desired observable, rather than weakening the current theorem statement.

## M-4: Conservation-Law Entropy Selection Failure

M-4 is deferred because entropy nonselection is promising but requires its own construction. A conservation-law result should state the weak formulation, identify a non-entropy weak solution or wrong admissibility class, verify residual satisfaction, and prove which entropy condition selects the physical solution. That is a different mechanism from fixed-sampling noncoercivity and should not be presented as validated by the collocation theorem.

Future work can target a scalar Burgers or scalar conservation-law example where residual minimization admits weak non-entropy solutions and an entropy inequality or vanishing-viscosity certificate restores uniqueness.
