# Rogers-Ramanujan Derivation

This folder contains public artifacts from a long-exposure mathematics run
focused on deriving the Rogers-Ramanujan identities from first principles.

The run explored formal power series identities, finite polynomial
approximants, q-difference and product-side checks, partition-inspired
experiments, Bailey-transform structure, and validation artifacts. The goal was
not to look up a proof, but to build a reproducible reasoning trail with
symbolic experiments separated from proof claims.

## Start Here

- `reports/final/final_report.md` and `reports/final/final_report.pdf` contain
  the final synthesis.
- `audits/final/final_audit_report.md` and
  `audits/final/final_audit_report.pdf` contain the final closure audit.
- `docs/proof/` contains proof-route notes and the main proof draft.
- `docs/lemmas/lemma_catalogue.md` tracks lemmas and proof status.
- `docs/validation.md` separates symbolic checks from mathematical proof steps.
- `scripts/rr/` contains Wolfram and Python probes used during exploration.
- `data/finite_experiments/` contains generated tables and figures.
- `MANIFEST.md` maps the important files and their roles.

## Reproduction Notes

The scripts are research artifacts rather than a packaged library. They were
validated with local Python tooling and Wolfram Language via `wolfram-batch`.
Local runtime state, session databases, process logs, and machine-specific
paths are omitted or sanitized in the public copy.
