---
created: 2026-05-18T06:15:00+00:00
run_id: fork-eec13528227c-clone-0-track1-reticulation-atlas
agent: worker
milestone: M3.T1
schema_version: v1.0
---

# Track 1 Reticulation Atlas Instrument

## Status

This is the M3.T1 Reticulation Atlas instrument over the validated Barrier 2
Track 1 enrichment layer. It computes a reproducible per-taxon
`tree_compatibility_index` (TCI) in `[0,1]`, emits genus-level hotspot
diagnostics, and preserves the accepted-key versus pending-crosswalk split.

It is a data-limited first instrument. The current substrate cannot validate
canonical polyploid recovery because the canonical Track 1 seed cases remain
unresolved against the frozen accepted-key namespace.

## Inputs

| Input | Role |
|---|---|
| `phytograph_dataset/nodes.parquet` | frozen Barrier 1 node table |
| `phytograph_dataset/hyperedges.parquet` | frozen Barrier 1 hyperedge table |
| `tracks/track1/data/reticulation_enrichment_edges.parquet` | 28 Barrier 2 Track 1 enrichment rows |
| `tracks/track1/data/canonical_seed_case_status.tsv` | canonical seed crosswalk status |

The Track 1 enrichment contains 28 rows: 3 accepted-key resolved rows and 25
`pending_crosswalk` rows. The accepted-key resolved rows are two chromosome
count assertions and one ploidy-state assertion; these support structural
context only, not a reticulation event.

## Mechanism

For taxon `t`, the observed component is:

```text
tci_observed(t) = 1 / (1 + n_evidence(t))
```

`n_evidence(t)` counts only event-shaped reticulation evidence on an accepted
key: `hybridization_event`, `polyploidization_event`, event-shaped
`reticulate_inheritance_evidence`, or accepted multi-parent `crop_pedigree`
evidence on the child/cultivar. `chromosome_count_assertion` and
`ploidy_state_assertion` rows are structural context only because their
`allowed_evidence_scope` does not establish event timing or progenitors.

The structural component combines genus-level ploidy spread, chromosome-count
CV, synonym cluster size, and taxonomic-conflict count. Missing structural
evidence defaults to tree-compatible and `data_limited`, so absence of evidence
is not treated as evidence of strict tree inheritance.

Default combine rule:

```text
tci(t) = 1 - max(1 - tci_observed(t), 0.5 * (1 - tci_structural(t)))
```

Observed event evidence dominates when present; structural signal is a soft
prior only.

## Outputs

| Output | Rows | Purpose |
|---|---:|---|
| `tracks/track1/outputs/tci_per_taxon.tsv` | 60,000 | per accepted-key TCI and provenance |
| `tracks/track1/outputs/tci_hotspots_genus.tsv` | 14,292 | genus-level hotspot diagnostics |
| `tracks/track1/outputs/accepted_key_resolved_reticulation_evidence.tsv` | 3 | accepted-key resolved Track 1 enrichment rows |
| `tracks/track1/outputs/pending_crosswalk_reticulation_evidence.tsv` | 25 | pending-crosswalk Track 1 enrichment rows |
| `tracks/track1/outputs/canonical_recovery_report.tsv` | 12 | canonical seed recovery scaffold |
| `tracks/track1/outputs/tci_summary.json` | 1 | machine-readable run summary |

## TCI Summary

| Measure | Value |
|---|---:|
| accepted keys scored | 60,000 |
| evidence-supported taxa | 2 |
| structural-only taxa | 29,294 |
| data-limited unknown taxa | 30,704 |
| minimum TCI | 0.5 |
| mean TCI | 0.986858 |
| maximum TCI | 1.0 |

The 2 evidence-supported taxa are accepted-key rows with retained multi-parent
crop-pedigree evidence. The instrument intentionally does not count the
accepted-key resolved *Arabidopsis thaliana* ploidy-context row as observed
reticulation evidence.

## Hotspot Diagnostics

The hotspot table reports:

```text
hotspot_score(genus) =
  fraction(taxa with event-shaped accepted-key evidence)
  + 0.5 * normalized_entropy(ploidy_states_in_genus)
```

The top rows are currently dominated by accepted multi-parent crop-pedigree
evidence in `Avena` and `Arachis`. Every genus is marked `data_limited` because
no genus has enough accepted-key chromosome-count coverage for a sufficient
chromosome-CV diagnostic. This is a substrate coverage result, not a biological
claim about reticulation density.

## Canonical Polyploid Recovery

The original canonical Track 1 recovery seeds are not validated:

| Canonical seed | Accepted-key status | Recovery status |
|---|---|---|
| *Triticum aestivum* | `pending_crosswalk` | `data_limited` |
| *Brassica napus* | `pending_crosswalk` | `data_limited` |
| *Spartina anglica* | `pending_crosswalk` | `data_limited` |
| *Tragopogon mirus* | `pending_crosswalk` | `data_limited` |
| *Tragopogon miscellus* | `pending_crosswalk` | `data_limited` |
| *Musa acuminata × balbisiana* | `absent` | `data_limited` |
| *Musa acuminata* | `pending_crosswalk` | `data_limited` |
| *Musa balbisiana* | `pending_crosswalk` | `data_limited` |

Additional canonical-like crop polyploid checks were included only as
diagnostics. *Arachis hypogaea* and *Avena sativa* recover through accepted
multi-parent crop-pedigree evidence, but this does not validate the original
M1.3 canonical polyploid seed set.

## Evidence Boundaries

- The instrument does not write `prediction_ledger.tsv` or
  `speculation_ledger.tsv`.
- Predictions are track-local diagnostics only until Barrier 4 reconciliation.
- Pending-crosswalk rows are preserved, not dropped.
- No new taxonomy, hybridization, polyploidization, or evolutionary-history
  claim is established.
- Absence of event evidence is interpreted as missing data unless structural
  diagnostics provide a weak prior.

## Reproduction

```bash
python3 tracks/track1/instruments/build_tci.py
python3 -m pytest -q tracks/track1/tests/test_tci_instrument.py
```
