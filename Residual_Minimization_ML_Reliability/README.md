# Residual Minimization ML Reliability

This folder contains public artifacts from a long-exposure run exploring when
small residual objectives in scientific machine learning are reliable
certificates, and when they can hide failure modes.

The run produced a catalogue of objective-level failure mechanisms, theorem
sketches and obstructions, toy simulations, regression tests, application risk
maps, periodic reports, and final audit/report artifacts. Local runtime state,
virtual environments, caches, session databases, and machine-specific launcher
files were intentionally omitted.

## Start Here

- `reports/final/final_report.md` and `reports/final/final_report.pdf` contain
  the final synthesis.
- `audits/final/final_audit_report.md` and
  `audits/final/final_audit_report.pdf` contain the final closure audit.
- `residual-certificates/` contains the catalogue, proof sketches, application
  map, and simulation summaries.
- `scripts/` contains the toy simulations and validation helpers.
- `tests/` contains the focused regression tests used by the run.
- `MANIFEST.md` maps the important files and how they support the final claims.

## Reproduction Notes

The scripts are research artifacts rather than a packaged library. They were
validated with Python plus NumPy/SciPy/SymPy/Matplotlib/Pytest-style tooling.
Generated reports were sanitized to replace local machine paths with public
placeholders such as `<run-workspace>`.
