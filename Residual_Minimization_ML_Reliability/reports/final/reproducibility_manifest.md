---
created: 2026-05-14T04:20:00Z
cycle: 3
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-5
---

# Reproducibility Manifest

## Commands

Run from `<run-workspace>`:

```bash
.sciml-venv/bin/python scripts/triage_residual_sequences.py
.sciml-venv/bin/python scripts/collocation_certificate_scaling.py
.sciml-venv/bin/python -m pytest tests/test_triage_scaling.py tests/test_collocation_certificate.py -q
python3 -m long_exposure.tools.promise_check <run-workspace>
python3 -m long_exposure.tools.org_check <run-workspace>
```

## Generated Artifacts

`data/triage_residual_scaling.csv`: tabulates candidate residual sequences and scaling diagnostics from M-1. Expected check: fixed-collocation rows keep sampled loss at zero while the continuous derivative certificate grows.

`data/triage_residual_scaling.png`: compares sampled loss, physical error, and continuous certificate terms for candidate mechanisms. Expected check: the fixed-collocation mechanism is visually separated from stable continuous-residual baselines.

`data/triage_bad_sequence_profiles.png`: plots representative bad-sequence profiles. Expected check: oscillations occur between fixed nodes while sampled constraints are satisfied.

`data/collocation_certificate_scaling.csv`: tabulates the M-3 theorem sequence for \(m\in\{4,8,16\}\), \(n\in\{1,2,4,8,16,32\}\). Expected check: `sampled_loss` is zero, `l2_error_sq` is `0.375`, and `regularity_certificate` grows with \(m^2n^4\).

`data/collocation_certificate_scaling.png`: visualizes zero sampled loss, constant \(L^2\) error, and growing fill-distance regularity certificate. Expected check: the plotted certificate is above the \(L^2\) error threshold for all shown \(n\).

`data/collocation_certificate_profiles.png`: shows the bad function and derivative residual between collocation nodes. Expected check: derivative samples vanish at nodes while curvature/variation is large between nodes.

## Expected Test Result

The combined pytest command should report:

```text
8 passed
```

Exact runtime can vary. The M-3 tests intentionally use a finite tolerance for sampled zero residuals because direct floating-point evaluation of sine at integer multiples of \(2\pi\) is not bit-exact.
