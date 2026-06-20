# Random Hyperbolic Surface Spectral Rigidity

This folder contains a completed long-exposure research run centered on
Kim and Tao's paper, *Eigenvalue rigidity of hyperbolic surfaces in the
random cover model*.

The run reconstructed the paper's proof architecture, audited the main
quantitative losses, built finite permutation and Schreier-style toy
benchmarks, and explored extension routes around local spectral windows,
coefficient variation, signed cancellation, and surface-group numerator
control.

## Main Outputs

- Final synthesis: `reports/final/final_report.md`
- Final synthesis PDF: `reports/final/final_report.pdf`
- Final audit: `audits/final/final_audit_report.md`
- Final audit PDF: `audits/final/final_audit_report.pdf`
- Run manifest: `MANIFEST.md`
- Curated artifact map: `CURATION.yaml`
- Cycle reports: `reports/cycles/`
- Extension candidates and theorem-target notes:
  `reports/extension_candidates/`
- Proof ledgers: `docs/proof_ledger/`
- Reproducible scripts: `scripts/`
- Regression and invariant tests: `tests/`
- Generated datasets: `data/`
- Figures: `reports/figures/`

## High-Level Findings

The run did not claim a sharper Kim-Tao exponent, a shrinking-window local
statistics theorem, or a transfer theorem from Schreier graph benchmarks to
random hyperbolic covers.

The strongest output is a structured map of what would be needed for a real
extension. The run localized the most credible remaining target to coefficient
or signed variation for the actual denominator-normalized Corollary 3.4
numerator, evaluated as `p(1/n)/Q_id(1/n)`. It also produced a standalone
two-permutation Schreier benchmark theorem package and a collection of
surface-facing obstruction and conditional-target notes.

## Reproducibility Notes

The scripts are intended to be run from this folder. They primarily use Python
with standard scientific packages, plus optional Wolfram Language, GAP, Lean,
and LaTeX tooling for selected symbolic, group-theoretic, formal, and rendering
checks.

Generated reports and data are included so the run can be inspected without
rerunning every experiment.

## Publication Hygiene

Local run-control files, hidden long-exposure instance state, package zips, and
machine-specific launch logs are omitted. Absolute local paths in text artifacts
were replaced with neutral placeholders before publication.
