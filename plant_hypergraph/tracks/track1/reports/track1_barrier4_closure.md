---
created: 2026-05-18T12:05:00+00:00
cycle: 20
run_id: fork-0b556d9370a2-clone-0-track1-barrier4-closure
agent: worker
milestone: _plan/track1-barrier4-closure
---

# Track 1 Barrier 4 Closure

## Current State

Track 1 enters Barrier 4 as a data-limited Reticulation Atlas instrument. The
frozen Track 1 enrichment layer has 28 seed rows: 3 rows currently resolve to
the Barrier-1 accepted-key namespace, and 25 remain `pending_crosswalk`. None
of the original eight canonical Track 1 recovery seeds has a current
accepted key in `canonical_seed_case_status.tsv`.

The accepted-key resolved Track 1 rows are not canonical event recovery:
the resolved rows are chromosome/ploidy context, and the M3.T1 instrument
correctly excludes chromosome-count and ploidy-context rows from observed
reticulation evidence.

## Recovery Probe

I ran `tracks/track1/scripts/track1_barrier4_key_recovery.py` against:

- `tracks/track1/data/canonical_seed_case_status.tsv`
- `tracks/track1/data/reticulation_enrichment_edges.parquet`
- `substrate/staging/taxonomy_backbone/accepted_taxa.parquet`
- `substrate/staging/taxonomy_backbone/synonym_clusters.parquet`
- `substrate/staging/taxonomy_backbone/raw/wfo/wfo_plantlist_2025-12.zip`

The script writes a sidecar recovery matrix only:

- `tracks/track1/data/barrier4_canonical_key_recovery.tsv`
- `tracks/track1/data/barrier4_rescued_reticulation_edges.tsv`

It does not mutate `phytograph_dataset/`, the frozen accepted-key subset, or
the master prediction/speculation ledgers.

## Recovered Seed Matrix

| Seed | Current status | Full-WFO sidecar status | Rescued key | Event-shaped rows attached | Blocker class |
|---|---|---|---|---:|---|
| *Triticum aestivum* | `pending_crosswalk` | `rescued_exact_full_wfo_taxon` | `wfo:wfo-0000905667-2025-12` | 2 | `frozen_subset_truncation` |
| *Brassica napus* | `pending_crosswalk` | `rescued_exact_full_wfo_taxon` | `wfo:wfo-0000571271-2025-12` | 2 | `frozen_subset_truncation` |
| *Spartina anglica* | `pending_crosswalk` | `rescued_synonym_to_full_wfo_taxon` | `wfo:wfo-0001341446-2025-12` | 2 | `name_status_mismatch` |
| *Tragopogon mirus* | `pending_crosswalk` | `not_recovered_absent_from_full_wfo` |  | 2 | `absent_from_full_wfo_exact_lookup` |
| *Tragopogon miscellus* | `pending_crosswalk` | `not_recovered_absent_from_full_wfo` |  | 2 | `absent_from_full_wfo_exact_lookup` |
| *Musa acuminata × balbisiana* | `missing_from_staging` | `not_recovered_absent_from_full_wfo` |  | 0 | `absent_raw_name` |
| *Musa acuminata* | `pending_crosswalk` | `rescued_exact_full_wfo_taxon` | `wfo:wfo-0000473834-2025-12` | 0 | `frozen_subset_truncation_non_event_only` |
| *Musa balbisiana* | `pending_crosswalk` | `rescued_exact_full_wfo_taxon` | `wfo:wfo-0000473990-2025-12` | 0 | `frozen_subset_truncation_non_event_only` |

Accepted-key recovery improved from 0/8 current canonical seeds to 5/8 in the
full-WFO sidecar. Event-shaped canonical recovery improved from 0/8 to 3/8 if
the synonym-to-accepted *Spartina anglica* mapping is accepted as a sidecar
join. Exact accepted-taxon recovery with event-shaped rows is 2/8.

## TCI Implication

The sidecar probe refines the diagnosis but does not validate H1. Full-WFO
coverage shows that part of the failure is frozen-subset truncation:
*Triticum aestivum*, *Brassica napus*, *Musa acuminata*, and *Musa balbisiana*
have exact taxon rows in the cached full WFO dump, but were absent from the
60k accepted-key subset used by the frozen substrate.

That taxonomic rescue does not by itself supply validation-scale biological
evidence. *Musa acuminata* and *Musa balbisiana* attach only to
chromosome-count rows, so they remain non-event context. *Spartina anglica*
has event-shaped evidence but is a WFO name/synonym mapping rather than an
exact accepted-taxon row. *Tragopogon mirus* and *Tragopogon miscellus* remain
blocked under the exact full-WFO probe despite event-shaped local seed rows.

Validation threshold for closure refinement: at least 5 canonical seeds with
accepted keys and event-shaped reticulation evidence, including explicit
hybridization/polyploidization or parent-bearing reticulate-inheritance rows.
The sidecar reaches 3 if synonym rescue is allowed, or 2 under exact accepted
taxon rows only.

## H1 Closure Status

H1 closure status: `data-limited`.

The refined blocker is mixed:

- Frozen-subset truncation is ruled in for *Triticum aestivum*,
  *Brassica napus*, *Musa acuminata*, and *Musa balbisiana*.
- Source/evidence scarcity remains ruled in because only two exact full-WFO
  rescued taxa attach to event-shaped canonical rows.
- Name-status mismatch is ruled in for *Spartina anglica*, which appears as a
  WFO name/synonym leading to an accepted taxon, not as an exact accepted
  taxon row.
- Exact-name absence remains ruled in for *Tragopogon mirus* and
  *Tragopogon miscellus* under this cached WFO dump.
- Raw-name absence remains ruled in for *Musa acuminata × balbisiana*, which
  is not present in the M1.3 seed rows.

This is not a falsification of biological reticulation in these lineages. It
is a validation-scale failure of the current accepted-key and event-source
coverage.

## Minimal Future-Data Recipe

To make H1 testable, Track 1 needs all of the following:

1. Promote a full taxonomy-backbone accepted-key expansion or late-arrival WFO
   sidecar into an audited substrate revision, including synonym/status
   treatment for nothospecies and reclassified names.
2. Acquire an approved CCDB export with row-level source identifiers,
   chromosome-count fields, taxon names, access date, and license/provenance.
3. Acquire an approved Plant DNA C-values export with accepted-key recoverable
   names, genome-size/ploidy fields, source identifiers, and license metadata.
4. Add a curated hybrid/polyploid event table with child taxon, parent taxa,
   event type, source citation, allowed evidence scope, and explicit status for
   nothospecies/cultivar hybrids.
5. Re-run TCI only after event-shaped canonical accepted-key recovery reaches
   validation scale; chromosome/ploidy rows must remain structural context
   unless a source explicitly asserts a hybridization or polyploidization event.
