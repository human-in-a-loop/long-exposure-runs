---
created: 2026-05-18T15:20:00+00:00
cycle: 22
run_id: run-phytograph-cycle22-reopen-evidence-gate
agent: worker
milestone: _plan/reopen-evidence-gate
---

# Reopen Evidence Gate

## Scope

This package defines when a closed PhytoGraph hypothesis may be reopened without
weakening the Wave 5 conservative closure. It does not acquire new data, rerun
validation, change track status, or write to `prediction_ledger.tsv` or
`speculation_ledger.tsv`.

The rule is mechanical: a branch is a reopen candidate only when it names the
previously missing evidence class, an accepted join key, minimum coverage, and a
falsification test. A branch that only changes scoring, thresholds, wording, or
visualization remains closed.

## Branch Matrix

The machine-readable gate matrix is
`data/reopen/reopen_branch_matrix.tsv`.

| Track | Current closed status | Reopen condition | Priority |
|---|---|---|---|
| Track 1 | H1 data-limited | Event-shaped reticulation evidence joins to accepted keys and clears canonical recovery plus confound controls. | high |
| Track 4 | H4 data-limited | Observed crop/CWR bioclim vectors and held-out expert comparison rows exist before any climate-substitution language. | high |
| Track 5 | H5 not validated/source-biased | Non-Duke, temporally resolved chemistry rows survive accepted-key joins and source-density controls. | medium-high |
| Track 6 | H6 environment-limited/untested | A free/open/local model runtime and weights produce audited response rows for the static benchmark. | medium |

## Per-Track Gates

### Track 1: Accepted-Key Reticulation Recovery

H1 can reopen only if new local/open evidence supplies event-shaped accepted-key
reticulation rows. Name-only recovery is insufficient. The minimum gate is at
least 5 of 8 canonical seed cases recovered as event-shaped accepted-key rows,
plus at least 30 additional accepted-key reticulation evidence rows to permit
source-density and family-size controls.

No-reopen conditions: repeating the existing WFO sidecar probe, recovering only
accepted names without event evidence, or changing the tree-compatibility score
without new joinable reticulation records.

### Track 4: Observed Crop/CWR Bioclim Vectors

H4 can reopen only if both crop and wild-relative sides have observed
coordinate-derived bioclim vectors and enough accepted-key held-out expert rows
for validation. The minimum gate is at least 30 accepted-key crop-wild-relative
pairs, at least 10 held-out crops with expert comparison rows, and nonzero
observed bioclim vectors for both sides.

No-reopen conditions: pedigree-only scoring, same-genus candidate lists without
climate vectors, or climate-substitution wording before sister-species and
same-genus dominance controls pass.

### Track 5: Non-Duke Temporal Chemistry

H5 can reopen only if non-Duke chemistry evidence has dates, accepted taxon
joins, compound identifiers, and enough family spread to test whether the Duke
source dominance has been broken. The minimum gate is at least 8 canonical
temporal holdouts with assertion dates, at least 5 chemically distinct families,
and at least 100 non-Duke taxon-compound rows after accepted-key join.

No-reopen conditions: Duke-only rows, undated chemistry assertions, family-level
signals without taxon-compound dates, or phrasing screening priors as
undocumented bioactivity.

### Track 6: Local/Open Model Execution

H6 can reopen only if a free/open/local model runtime and local model weights are
actually runnable in the workspace or approved local filesystem. The minimum
gate is at least one runnable local model, at least 210 static probe responses,
deterministic scorer outputs, preserved prompt/response provenance, and a
prompt-template sensitivity check.

No-reopen conditions: paid or key-gated providers, live remote API calls,
benchmark-only scorer controls, or any model error-rate claim without audited
response rows.

## Priority Decision

Track 1 is the highest-value branch because its blocker is narrow and
joinability-focused: event-shaped accepted-key reticulation records would
directly test the failed predicate. Track 4 is also high value, but its
promotion risk is higher because climate-substitution language can read as a
recommendation before validation. Track 5 is medium-high because it directly
tests source dominance. Track 6 is medium unless a compatible local runtime and
weights are already present.

## Falsification Tests

Every branch must distinguish new signal from coverage artifacts before any
status change is considered:

- Track 1: canonical recovery, source-density control, family-size control.
- Track 4: climate-vector presence, held-out expert agreement, sister-species
  baseline, same-genus dominance control.
- Track 5: temporal top-decile recovery, no-Duke baseline, source-density
  matched control, screening-count matched control.
- Track 6: local runtime availability, deterministic scorer controls, response
  audit, category error rates, prompt-template sensitivity.

## Ledger Boundary

The master prediction and speculation ledgers remain header-only. This package
defines reopen gates only; it does not change H1, H4, H5, or H6 status and does
not promote biological, climate-substitution, chemistry, or model-performance
claims.
