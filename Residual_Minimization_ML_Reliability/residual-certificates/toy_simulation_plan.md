---
created: 2026-05-14T14:12:00Z
cycle: 48
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-7
---

# Toy Simulation Triage Plan

The M-7 objective is triage, not full execution of five new simulations. CAT-01 is already executed and validated from prior work; the remaining plans are selected for low cost and distinct mechanisms.

## Selected Initial Five

| Priority | Catalogue ID | Simulation name | Physical task | Residual objective tested | Misleading low-loss construction | Physical error/observable | Certificate/correction to show | Expected artifacts | Status |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | CAT-01 | fixed-node derivative residual aliasing | solve \(u'=0\), \(u(0)=u(1)=0\) | fixed-node derivative residual plus endpoint penalty | \(u_n=\sin^2(\pi mnx)\) | \(L^2\) error fixed at \(\sqrt{3/8}\) | continuous derivative and fill-distance/\(u''\) certificate grow | existing `data/collocation_certificate_scaling.csv`, `data/collocation_certificate_scaling.png`, `scripts/collocation_certificate_scaling.py` | completed/validated |
| 2 | CAT-02 | trace leakage scaling | solve \(u'=0\), \(u(0)=0\) | \(\|u'\|_{L^2}^2+n^{-2}|u(0)|^2\) | \(u_n\equiv1\) | \(L^2\) error \(=1\) | fixed trace penalty gives nonzero certificate | `data/trace_leakage_scaling.csv`, `data/trace_leakage_scaling.png`, `scripts/trace_leakage_scaling.py`, `tests/test_trace_leakage_scaling.py` | next |
| 3 | CAT-06 | weak-norm topology mismatch | certify \(u=0\) while measuring in \(H^{-s}\) | \(\|u\|_{H^{-s}}^2\), \(s=1\) or \(2\) | \(u_n=\sin(nx)\) | \(L^2\) norm constant | \(L^2\) residual or bandwidth/regularity bound detects it | `data/weak_norm_scaling.csv`, `data/weak_norm_scaling.png`, `scripts/weak_norm_scaling.py`, `tests/test_weak_norm_scaling.py` | next |
| 4 | CAT-09/CAT-10 | entropy selection toy | scalar conservation-law Riemann problem | weak residual/admissibility check | entropy vs non-entropy weak candidate satisfying Rankine-Hugoniot | mismatch against entropy solution or entropy inequality violation | entropy residual/Kruzhkov-style inequality | `data/burgers_entropy_selection.csv`, `data/burgers_entropy_selection.png`, `scripts/burgers_entropy_selection.py`, `tests/test_burgers_entropy_selection.py` | planned; may downgrade to obstruction note |
| 5 | CAT-11 | stiff observability failure | two-component stiff ODE with hidden fast state | observed slow-state residual/data loss only | correct \(y_1=e^{-t}\), wrong hidden \(y_2=1\) | hidden-state \(L^2\) or terminal error | full-state residual or observability/rank certificate | `data/stiff_observability_failure.csv`, `data/stiff_observability_failure.png`, `scripts/stiff_observability_failure.py`, `tests/test_stiff_observability_failure.py` | next |

## Backup Simulations

| Catalogue ID | Backup reason | Proposed artifact |
|---|---|---|
| CAT-07 | If entropy selection takes too long, quadrature aliasing is cheap and distinct from trace leakage. | `data/quadrature_aliasing.csv/png` |
| CAT-15 | Eigenmode normalization failure is theorem-quality and easy to test with a Sturm-Liouville residual. | `data/eigenmode_normalization.csv/png` |
| CAT-17 | Inverse non-identifiability is a rigorous obstruction and can be shown with a small parameter sweep. | `data/inverse_nonidentifiability.csv/png` |

## Reproducibility Expectations

Each new simulation should produce one CSV with columns for the scale parameter, residual loss, physical error, and certificate value. Each figure should plot residual loss against the physically relevant error or certificate so the failure/correction contrast is visible. Each test should check one happy path asymptotic and one failure/negative-control condition, for example that trace leakage loss decays while \(L^2\) error stays one, or that a matched \(L^2\) residual does not decay for the weak-norm high-frequency family.

## Deferred Cases And Rationale

CAT-08 and CAT-13 are deferred because they are visually useful but mostly variants of fixed sampling missing between-node behavior. CAT-14 and CAT-20 are deferred because they need a chosen vector-field or rollout surrogate class before the residual objective is precise. CAT-18 is deferred because a meaningful source-identification toy should be designed around a specific sensor matrix or PDE Green's function rather than sketched generically.
