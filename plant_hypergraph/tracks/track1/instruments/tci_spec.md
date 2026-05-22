<!--
created: 2026-05-18T03:00:00+00:00
cycle: 9
run_id: run-phytograph-cycle9-m3t1-tci
agent: worker
milestone: _plan/track1-m3t1-instrument
-->

# Track 1 — Tree Compatibility Index (TCI) Specification

## Scope

The TCI is a per-taxon score in [0, 1] derived from the **frozen Barrier-1 substrate** (363,237 nodes, 641,183 retained hyperedges) and **Track 1 enrichment** (28 staged seed rows, 3 resolved to accepted keys, 25 `pending_crosswalk`). It is a transparent, hand-specified statistic — **not** a learned model — built to make the evidence-versus-structural-prior distinction visible at the level of the output rows.

## Definitions

Let `t` be a taxon with accepted key `k(t)`. Define five basic counts:

- `E(t)` = number of event-shaped substrate hyperedges of type ∈ { `reticulate_inheritance_evidence`, `hybridization_event`, `polyploidization_event` } that are incident to `k(t)` (either as `accepted_taxon_key` of the edge, or with `k(t)` listed in the edge's canonical members under a `taxon`, `child_taxon`, or `parent_taxa` role). For `reticulate_inheritance_evidence`, the preserved role map must contain an event role such as `child_taxon` or `parent_taxa`; pre-repair ploidy-context rows with only `ploidy_state` are not observed reticulation evidence.
- `Cp(t)` = number of `crop_pedigree` hyperedges where `k(t)` appears in role `cultivar` (multi-parent crop pedigree counts as observed reticulation evidence on the child).
- `P(g)` = number of distinct ploidy states observed among accepted-key-resolved members of the smallest enclosing genus `g` of `t`. Computed from `ploidy_state_assertion` rows in Track 1 enrichment with resolved keys.
- `χ(g)` = chromosome-count coefficient of variation across the **midpoints of parsed numeric counts** (from `chromosome_count_assertion.parsed_min..parsed_max`) within `g`, computed only when `g` has ≥ 3 distinct numeric counts.
- `S(t)` = synonym cluster size of `t`, defined as the number of distinct nodes (synonym + accepted) in the unique `synonym_cluster` hyperedge whose `accepted_taxon_key = k(t)`. If `t` has no `synonym_cluster` row, `S(t) = 1`.
- `X(t)` = number of `taxonomic_conflict` hyperedges with `accepted_taxon_key = k(t)`.

Reticulation evidence count for `t`:
```
n_evidence(t) = E(t) + Cp(t)
```

`chromosome_count_assertion` and `ploidy_state_assertion` rows are structural
context only. Their preserved `allowed_evidence_scope` explicitly forbids
promotion to a polyploidization or hybridization event.

## TCI components

### Observed component

```
tci_observed(t) = 1 / (1 + n_evidence(t))
```

Invariance: `tci_observed = 1` iff `n_evidence = 0`; strictly monotone decreasing in `n_evidence`. A single edge drops the score to 0.5; three edges drop it to 0.25. The function is bounded in (0, 1] without parameters.

### Structural component

Four bounded sub-terms in [0, 1], each `1.0` meaning "tree-compatible by default":

1. **Ploidy-state spread** of the smallest enclosing genus `g`:
   ```
   s_ploidy(t) = 1 - H_norm(ploidy_states(g))
   ```
   where `H_norm` is Shannon entropy of the ploidy-state distribution, normalized by `log(P(g))` (natural log). `s_ploidy = 1.0` if `P(g) ≤ 1` (no spread observable). The honest data-limited default is `1.0`.

2. **Chromosome-count CV**:
   ```
   s_chrom(t) = 1 - min(1, χ(g))
   ```
   `s_chrom = 1.0` if `g` has < 3 numeric chromosome-count records (undefined CV → tree-compatible by default; flagged `data_sufficiency=insufficient` downstream).

3. **Synonym turnover** (large clusters indicate name turnover, a soft proxy for taxonomic instability that often co-occurs with reticulation):
   ```
   s_synonym(t) = 1 / (1 + max(0, S(t) - 1) / 4)
   ```
   `s_synonym = 1.0` for singleton clusters; halves at `S = 5`.

4. **Taxonomic conflict** density:
   ```
   s_conflict(t) = 1 / (1 + X(t))
   ```

Combined structural component (default weights equal, exposed via `--weights w_p,w_c,w_s,w_x` on the CLI; weights need not sum to 1, they are averaged):
```
tci_structural(t) = (w_p · s_ploidy + w_c · s_chrom + w_s · s_synonym + w_x · s_conflict)
                    / (w_p + w_c + w_s + w_x)
```

Default: `w_p = w_c = w_s = w_x = 1` → straight mean.

### Combine rule

```
tci(t) = 1 - max( 1 - tci_observed(t),  λ · (1 - tci_structural(t)) )
```

with default `λ = 0.5`.

This rule has three critical properties:

- When `tci_observed < 1` (i.e. evidence present), observed signal **dominates**: `tci ≤ tci_observed`, and `tci → tci_observed` as λ → 0.
- When `tci_observed = 1` (no evidence), `tci = 1 - λ · (1 - tci_structural)`. Structural signal can only act as a **soft prior**, bounded above by `1 - λ · (1 - tci_structural) ≥ 1 - λ`. With default λ = 0.5, no structural-only signal can pull TCI below 0.5.
- λ → 0 disables the structural prior entirely (`tci ≡ tci_observed`). This is the ablation `--ablation no_structural`.

### Provenance

`tci_provenance(t)` ∈ { `evidence_supported`, `structural_only`, `data_limited_unknown` }:

- `evidence_supported` if `n_evidence(t) ≥ 1`
- `structural_only` if `n_evidence(t) = 0` and at least one of `s_ploidy < 1`, `s_chrom < 1`, `s_synonym < 1`, `s_conflict < 1`
- `data_limited_unknown` otherwise (zero evidence, all structural sub-terms = 1.0). This is the honest "we don't know" point.

### Confidence

`confidence(t)` ∈ { `high`, `medium`, `low`, `data_limited` }:

- `high`: `n_evidence(t) ≥ 2`
- `medium`: `n_evidence(t) = 1`
- `low`: `n_evidence(t) = 0` AND any structural sub-term < 1 AND `g` has ≥ 3 chromosome-count records OR ≥ 2 ploidy records
- `data_limited`: all other cases (default for the vast majority of the 60,000 Tier-0 species nodes).

## Honest multi-way claim

A `polyploidization_event` hyperedge of arity 4 (e.g. *Triticum aestivum* with 3 parent lineages + 1 child + 1 source node) contributes to `n_evidence` of the child taxon as **one** edge, not as `C(4,2) = 6` pairwise edges. This preserves the multi-way semantics that the M7 clique-warning diagnostic from the prior campaign established as load-bearing.

## Invariance properties (empirically tested)

| Property | Test |
|---|---|
| Default tree-compatibility | A taxon with `n_evidence = 0` and a genus with no ploidy variance, no chromosome CV, no synonym turnover, no taxonomic conflict returns `tci = 1.0`, provenance `structural_only` (or `data_limited_unknown` if every structural term is exactly 1.0 too), confidence `data_limited`. |
| Evidence monotone | Injecting one synthetic `polyploidization_event` on a focal taxon strictly lowers `tci`. |
| Ablation isolation | `--ablation no_structural` forces `tci ≡ tci_observed`. |
| Synonym invariance smoke | Re-running with one swapped synonym → accepted-key choice leaves TCI rank order unchanged for unrelated taxa. |

## Hotspot statistic (genus / family)

For a clade `C` with member set `M(C)`:

```
hotspot_score(C) = fraction( m ∈ M(C) : tci_observed(m) < 1 )
                 + α · H_norm( ploidy_states(C) )
```

with default `α = 0.5`. The first term is **evidence-driven**; the second is the structural diagnostic. Both are reported separately so the auditor can see which is doing the work.

`data_sufficiency(C)` = `sufficient` iff `|M(C)| ≥ 2` AND clade has ≥ 3 numeric chromosome-count records; else `data_limited`.

## CLI ablations

`--ablation` accepts `{none, no_evidence, no_structural, no_ploidy, no_chrom_cv, no_synonym, shuffle_provenance}`:

- `no_evidence`: zero out `tci_observed`'s contribution (sets evidence count to 0). TCI becomes a pure structural prior.
- `no_structural`: λ = 0. TCI ≡ tci_observed.
- `no_ploidy`, `no_chrom_cv`, `no_synonym`: zero the weight on that single structural sub-term.
- `shuffle_provenance`: randomly permute `source_id` strings within the substrate before scoring; used to test whether any apparent signal collapses to source-density signal.

## Output tables

Default execution writes:

- `tracks/track1/outputs/tci_per_taxon.tsv` — one row per non-empty accepted key scored.
- `tracks/track1/outputs/tci_hotspots_genus.tsv` — genus-level hotspot diagnostics with `hotspot_score`, evidence fraction, ploidy entropy, and data-sufficiency flag.
- `tracks/track1/outputs/accepted_key_resolved_reticulation_evidence.tsv` — the 3 Track 1 enrichment rows that resolve to accepted keys.
- `tracks/track1/outputs/pending_crosswalk_reticulation_evidence.tsv` — the 25 Track 1 enrichment rows preserved as raw-name pending-crosswalk evidence.
- `tracks/track1/outputs/canonical_recovery_report.tsv` — canonical seed recovery status; original M1.3 canonical polyploid seeds are data-limited at current accepted-key coverage.
- `tracks/track1/outputs/tci_summary.json` — count summary and evidence-boundary declaration.
