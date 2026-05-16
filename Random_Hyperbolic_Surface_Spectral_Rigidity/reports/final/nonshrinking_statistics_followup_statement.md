---
created: 2026-05-16T23:44:00Z
cycle: 45
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M34-finite-nonshrinking-spectral-statistics
---

# Non-Shrinking Statistics Follow-Up Statement

Kim--Tao Theorem 1 implies fixed-window spectral count asymptotics: for every fixed \(1/4\le a<b\),
\[
N_{X_n}([a,b])=(2g-2)n(F(b)-F(a))
+O_\epsilon(n^{1-\alpha_W}b^{1/2+\epsilon}).
\]
The same formula gives a centered high-probability error bound of size \(n^{1-\alpha_W}\) up to fixed energy factors.

This is a theorem-level corollary, not a local-statistics theorem.  The edge case \(a=1/4\) has \(F(1/4+\Delta)-F(1/4)\sim(\pi/3)\Delta^{3/2}\), but fixed \(\Delta>0\) still gives an order-\(n\) main term.  Shrinking windows \(\Delta=n^{-d}\), variance asymptotics, limiting distributions, level repulsion, and universality remain outside this result and require new input beyond endpoint subtraction and rigidity.
