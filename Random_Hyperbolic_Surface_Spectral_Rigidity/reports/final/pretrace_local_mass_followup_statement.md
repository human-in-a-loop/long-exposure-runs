---
created: 2026-05-16T20:39:00Z
cycle: 40
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M29-pretrace-local-mass-intermediate-from-theorem2-proof
---

# Pre-Trace Local-Mass Follow-Up Statement

Kim--Tao's proof of Theorem 2 contains a standalone fixed-cutoff local mass estimate before the final Sobolev/elliptic conversion. With probability at least `1 - n^(-1/10)`, the proof gives

```text
int_H a(z)|u_j^rho(z,i)|^2 dVol(z) <= C Lambda0 n^(-alpha0)
```

for the smooth nonnegative base cutoff `a`, every fiber `i`, and all normalized eigenfunctions below the relevant energy. The final `L^\infty` theorem then multiplies this local mass by `Lambda0^2` before taking square roots, which changes the squared mass envelope from `Lambda0` to `Lambda0^3`. The statement is therefore a useful pre-Sobolev local-mass corollary, but not a quantum-ergodicity result or a uniform theorem for arbitrary balls.
