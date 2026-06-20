---
title: "PhytoGraph — cycles 27-29"
date: "2026-05-18"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph — cycles 27-29

## Abstract

Cycles 27-29 tested whether free/open recovery work could reopen closed PhytoGraph validation lanes without changing the frozen schema, substrate, or master ledgers. The result was a narrower but still conservative closure state.

Cycle 27 revisited Track 5, the Chemodiversity Predictor. It found two manual non-Duke, accepted-key historical chemistry candidates, `Artemisia annua`/artemisinin and `Atropa bella-donna`/atropine, but not a structured family/class temporal evidence layer. H5 therefore remained source-biased and not validated.

Cycle 28 revisited Track 4, the Domestication Hypergraph. It recovered nonzero free GBIF/iNaturalist-mediated coordinates for a bounded crop/wild-relative panel, but produced zero numeric BIOCLIM vectors and zero validation-allowed candidate-level comparator rows. H4 therefore remained data-limited.

Cycle 29 reconciled Track 1 branch-local GBIF accepted-key reticulation evidence against the frozen WFO-oriented namespace. The auditor validated the reconciliation package: WFO projection retained only 2 of 22 GBIF accepted-key event taxa, while a labeled GBIF sidecar preserved 22 retained event taxa across 11 source groups with 0/17 matched-control recovery. That sidecar is admissible only as a Track 1 evidence-readiness diagnostic. It does not reopen WFO-based Track 1 closure, does not validate H1, and does not promote any master prediction row.

Across all three cycles, `prediction_ledger.tsv` and `speculation_ledger.tsv` remained header-only.

## Introduction

The PhytoGraph campaign uses a typed plant-biology hypergraph as a discovery substrate. Its success criterion is not data aggregation alone, but falsifiable prediction followed by validation or clean falsification. By cycles 27-29, the campaign had already passed through final synthesis and post-reopen closure for several tracks. The remaining work in this window was not broad discovery. It was targeted recovery: test whether free/open evidence could repair specific blockers without weakening the campaign's evidence rules.

The key constraint was claim discipline. A local branch could refine a blocker, find a useful sidecar signal, or produce future-data recipes, but it could not promote biological novelty, climate-substitution recommendations, phytochemical predictions, or reticulation validation unless the promotion predicate was met.

## Approach

The cycle window used local artifacts, append-only ledger events, and the supplied audit report as source material. Full external session transcripts for the listed session IDs were not fetchable in this environment, so the report treats those transcripts as a record gap and relies on the workspace artifacts and ledger entries that cite them.

The reporting sources were:

- Cycle 27: Track 5 free-tier non-Duke temporal chemistry recovery, worker event `cdb62567-79f1-4c76-a563-6469c531d675`, session ID `504c186b-b730-4ab2-957c-a36d601f7b9b` listed for researcher context.
- Cycle 28: Track 4 free-tier BIOCLIM recovery, worker event `f23f8644-a9dd-42bd-95ee-9f9bd2dc8fc4`, and free-tier recovery integration event `7c3c79db-c2c9-4df0-8b3d-cc407f55a3bc`, session ID `20757142-97dc-424b-b730-1765357d2dcc`.
- Cycle 29: Track 1 namespace reconciliation, worker event `b77f9c32-d0aa-4c02-9f5a-7fa9c7fbba66`, auditor event `d2e8e456-2f64-43ff-86a6-81c8cfe5ea3c`, session IDs `5614c09a-9e3f-450c-83d8-10cd69852fee`, `55fd3b4f-a380-4c48-9707-ad4d8d957bbe`, and `81e05f8b-b8d6-4b05-8fee-22c112a6c33a`.

The field is cross-disciplinary and method-focused, so this report uses the general structure: approach, findings, discussion, open questions, and implementation details.

## Findings

### Cycle 27: Track 5 Found Isolated Non-Duke Chemistry Candidates, Not A Reopenable Evidence Layer

Cycle 27 varied the Track 5 evidence-acquisition axis. Instead of relying only on the frozen local chemistry staging tables, the worker performed a bounded free/open literature-source pass over canonical medicinal taxa and adjacent taxa.

The pass found historical non-Duke chemistry records for several canonical discoveries, including taxol, artemisinin, reserpine/vinca alkaloid context, quinine, morphine, atropine, digoxin-source correction, and willow/salicin history [68]-[77]. Only two candidate rows also had accepted species-level keys visible in the frozen local substrate lookup:

| Accepted key | Accepted name | Compound | Year basis | Status |
|---|---|---|---|---|
| `wfo:wfo-0000083255-2025-12` | `Artemisia annua` | artemisinin/qinghaosu | 1972/1977/1984 | candidate manual recovery |
| `wfo:wfo-0001019409-2025-12` | `Atropa bella-donna` | atropine | 1831 | candidate manual recovery |

The Track 5 mechanism needs a structured non-Duke family/class stratum to estimate the family/class chemistry signature `S_f[k]`. Two manually found rows do not provide that stratum. The result refined the earlier blocker: the literal absence of open non-Duke historical detections was too strong, but the validation predicate still was not met.

No Chemodiversity Predictor rerun occurred. No phytochemical novelty, clinical efficacy, preparation, dosage, safety, bioactivity, prediction-ledger row, or speculation-ledger row was promoted.

### Cycle 28: Track 4 Recovered Coordinates But Still Could Not Compute Climate Validation

Cycle 28 tested whether Track 4 could move from "no usable local climate evidence" to bounded validation readiness using free GBIF occurrence data and iNaturalist-mediated records exposed through GBIF-compatible metadata [6], [8].

The branch produced a clear recovery funnel:

![Free-tier Track 4 recovery funnel showing queried taxa, license-compatible coordinates, post-filter coordinates, numeric BIOCLIM vectors, and validation-allowed comparator rows.](tracks/track4/figures/track4_free_tier_bioclim_recovery.png)

The quantitative result was:

| Metric | Result |
|---|---:|
| Occurrence query-role rows | 30 |
| Returned occurrence records | 8,423 |
| License-compatible coordinate records | 3,408 |
| Post-filter records | 3,358 |
| Deduplicated post-filter coordinates | 2,272 |
| Numeric BIOCLIM vector rows | 0 |
| Validation-allowed comparator rows | 0 |

The occurrence blocker was reduced: the branch showed that free records could provide nonzero coordinates after license, uncertainty, severe-geospatial-issue, duplicate-coordinate, and cultivated/managed filters. The decisive blocker moved downstream. No local WorldClim/CHELSA raster or sampled climate file was present, so every row in `free_tier_bioclim_vectors.tsv` remained `not_computed_no_local_raster_or_runtime`.

Comparator readiness also failed. The open comparator search found candidate-name and stress-adjacent metadata for existing `Arachis` and `Avena` candidates, but those rows overlapped training-derived evidence and were same-genus candidate rows. Existing held-out rows remained crop-program-level rather than disjoint candidate-level expert comparator rows.

The cycle 28 integration record therefore kept H4 data-limited. It also integrated the cycle 27 Track 5 result and a Track 1 branch-local recovery result, but kept all three behind the no-promotion boundary.

### Cycle 29: Track 1 Namespace Reconciliation Preserved A GBIF Sidecar Signal Without Validating H1

Cycle 29 addressed the unresolved Track 1 question from cycle 28: whether branch-local GBIF accepted-key reticulation evidence could be reconciled with the frozen WFO-oriented substrate namespace. The frozen substrate used WFO accepted keys from the WFO Plant List [4]. The branch-local recovery used GBIF accepted keys [6], [7].

The worker built a namespace reconciliation package with a crosswalk, retained evidence table, matched controls, report, figure, build script, plot script, and focused tests. The auditor validated it.

![Track 1 free-tier reticulation evidence retained, rejected, or sidecar-admitted after GBIF-to-WFO reconciliation.](tracks/track1/figures/track1_free_tier_namespace_reconciliation.png)

The central result was:

| Metric | Result |
|---|---:|
| Distinct GBIF accepted-key event taxa accounted for | 22 |
| WFO-projected event taxa | 2 |
| GBIF sidecar-admitted event taxa | 20 |
| Rejected diagnostic rows | 1 |
| Retained event-shaped evidence rows | 23 |
| Retained independent source groups | 11 |
| Matched-control event recovery | 0 / 17 |

Only two GBIF accepted-key event taxa projected cleanly to species-level WFO keys in the frozen local crosswalk: `Arachis hypogaea` and `Arabidopsis suecica`. The remaining GBIF accepted-key evidence was retained only in a labeled sidecar. The sidecar includes canonical and source-supported reticulation/polyploid/hybrid examples such as `Triticum aestivum`, `Brassica napus`, `Tragopogon ×mirus`, `Tragopogon ×miscellus`, `Helianthus` hybrid species, `Rosa canina`, `Quercus robur`, `Musa ×paradisiaca`, and `Camelina sativa` [57]-[67].

One row was explicitly rejected: `Citrus sinensis`, because GBIF collapsed it to the `Citrus ×aurantium` accepted key and the row was diagnostic-only rather than accepted-key event-shaped. The retained Citrus row was the accepted-key `Citrus ×aurantium` sidecar row.

The auditor's decision was `VALIDATED`, but the validation applied to the reconciliation package, not to H1. The audit stated that:

- WFO projection alone does not reopen WFO-based Track 1 closure.
- The GBIF accepted-key sidecar is admissible only as Track 1 evidence-readiness diagnostics.
- The package does not change schema v1.0, the master substrate, the TCI predictor, or the master ledgers.
- The package does not establish a new reticulation claim or validated Track 1 prediction.
- Source-density, family-size, under-studied-clade, and low-publication controls remain blockers for any master-level validation upgrade.

## Discussion

Cycles 27-29 did not reverse the campaign's conservative closure. They narrowed several blockers.

For Track 5, the blocker is no longer "no open historical non-Duke detections can be found." The better statement is: isolated open historical detections exist, but the current workspace lacks a structured, accepted-key, dated, non-Duke taxon-compound layer across enough families/classes to rerun the temporal predictor or validate H5.

For Track 4, the blocker is no longer simply occurrence coordinates. The better statement is: bounded free occurrence recovery works, but climate validation still requires audited local WorldClim/CHELSA raster summaries or an equivalent sampled climate table, plus disjoint candidate-level expert comparator rows.

For Track 1, the branch-local signal is real enough to preserve but not strong enough to promote. The GBIF sidecar carries evidence-readiness value: 22 retained event taxa, 11 source groups, and 0/17 matched-control recovery. It remains outside master validation because the frozen substrate is WFO-oriented, WFO projection retained only 2 taxa, and the unresolved controls are exactly the controls needed to distinguish biological signal from source-density and publication effects.

The master-ledger result is unchanged. `prediction_ledger.tsv` and `speculation_ledger.tsv` remain header-only because no cycle 27-29 branch met its promotion predicate.

## Open Questions

1. Can the Track 1 GBIF sidecar be upgraded through a formally accepted sidecar namespace policy, or must all future Track 1 validation use WFO-projected accepted keys only?

2. What source-density, family-size, low-publication, and under-studied-clade controls are sufficient for Track 1 to convert the sidecar signal into master-level validation evidence?

3. What is the smallest acceptable local/free climate input for Track 4: full WorldClim/CHELSA rasters, a sampled climate table, or a reproducible external summary with source identifiers and access metadata?

4. What minimum structured non-Duke chemistry intake would allow Track 5 to estimate family/class signatures without collapsing into Duke/source-density effects?

5. Should the Track 5 canonical holdout design replace or relabel targets whose historical source taxon is ambiguous, such as `Digitalis purpurea` versus `Digitalis lanata` for digoxin?

## References

[4] The World Flora Online Consortium et al., "World Flora Online Plant List December 2025," Zenodo, 2025. https://doi.org/10.5281/zenodo.18007552 (accessed 2026-05-17).

[6] GBIF Secretariat, "GBIF API Reference," GBIF Technical Documentation, 2026. https://techdocs.gbif.org/en/openapi/ (accessed 2026-05-17).

[7] GBIF Secretariat, "Species API," GBIF Technical Documentation, 2026. https://techdocs.gbif.org/en/openapi/v1/species (accessed 2026-05-17).

[8] GBIF Secretariat, "Occurrence API," GBIF Technical Documentation, 2026. https://techdocs.gbif.org/en/openapi/v1/occurrence (accessed 2026-05-17).

[57] Pamela S. Soltis et al., "The recent and recurrent origin of allopolyploid species in Tragopogon," Proceedings of the National Academy of Sciences, 2004. https://doi.org/10.1073/pnas.0405153101

[58] Marcus A. Koch et al., "Sequencing of the genus Arabidopsis identifies a complex history of nonbifurcating speciation and abundant trans-specific polymorphism," Nature Genetics, 2016. https://doi.org/10.1038/ng.3617

[59] Loren H. Rieseberg et al., "Major ecological transitions in wild sunflowers facilitated by hybridization," Science, 2003. https://doi.org/10.1126/science.1086949

[60] Michael L. Arnold, "Natural hybridization in Louisiana irises: genetic variation and ecological determinants," Evolution, 1990. https://doi.org/10.2307/2445221

[61] Amandine Cornille et al., "New insight into the history of domesticated apple: secondary contribution of the European wild apple to the genome of cultivated varieties," PLOS Genetics, 2012. https://doi.org/10.1371/journal.pgen.1002703

[62] Guohong Albert Wu et al., "Sequencing of diverse mandarin, pummelo and orange genomes reveals complex history of admixture during citrus domestication," Nature Biotechnology, 2014. https://doi.org/10.1038/nbt.2906

[63] Guohong Albert Wu et al., "Genomics of the origin and evolution of Citrus," Nature, 2018. https://doi.org/10.1038/nature25447

[64] Christian Ritz et al., "Evolution by reticulation: European dogroses originated by multiple hybridization across the genus Rosa," Molecular Ecology, 2005. https://doi.org/10.1111/j.1365-294X.2005.02730.x

[65] Thibault Leroy et al., "Extensive recent secondary contacts between four European white oak species," New Phytologist, 2019. https://doi.org/10.1111/nph.16069

[66] Xavier Perrier et al., "Multidisciplinary perspectives on banana domestication," Proceedings of the National Academy of Sciences, 2011. https://doi.org/10.1073/pnas.1102001108

[67] Martin A. Lysak et al., "The emerging biofuel crop Camelina sativa retains a highly undifferentiated hexaploid genome structure," Nature Communications, 2014. https://doi.org/10.1038/ncomms4706

[68] Mansukh C. Wani, Harold L. Taylor, Monroe E. Wall, Philip Coggon, and Andrew T. McPhail, "Plant antitumor agents. VI. Isolation and structure of taxol, a novel antileukemic and antitumor agent from Taxus brevifolia," Journal of the American Chemical Society, 1971. https://doi.org/10.1021/ja00738a045 (accessed 2026-05-18).

[69] Richard K. Haynes, "The biosynthesis of artemisinin (Qinghaosu) and the phytochemistry of Artemisia annua L. (Qinghao)," Molecules, 2010. https://pubmed.ncbi.nlm.nih.gov/21030913/ (accessed 2026-05-18).

[70] D. L. Klayman et al., "Isolation of Artemisinin (Qinghaosu) from Artemisia annua Growing in the United States," Journal of Natural Products, 1984. https://doi.org/10.1021/np50034a027 (accessed 2026-05-18).

[71] M. H. M. Sharaf and F. A. K. Al-Yahya, "Isolation of Reserpine from Vinca rosea Linn.," Nature, 1958. https://www.nature.com/articles/181552a0 (accessed 2026-05-18).

[72] JAMA, "Quinin: 1820-1920," Journal of the American Medical Association, 1920. https://jamanetwork.com/journals/jama/fullarticle/223878 (accessed 2026-05-18).

[73] Science Museum Group, "Original preparation of quinine by Pelletier and Caventou," Science Museum Group Collection, 2026. https://collection.sciencemuseumgroup.org.uk/objects/co184085/original-preparation-of-quinine-by-pelletier-and-caveton (accessed 2026-05-18).

[74] Andrea L. Devereaux, Susan L. Mercer, and Christopher W. Cunningham, "DARK Classics in Chemical Neuroscience: Morphine," ACS Chemical Neuroscience, 2018. https://doi.org/10.1021/acschemneuro.8b00150 (accessed 2026-05-18).

[75] M. J. Davies, "Atropa belladonna," Heart, 2002. https://heart.bmj.com/content/88/3/215.2 (accessed 2026-05-18).

[76] D. G. Grahame-Smith, "Digoxin comes from Digitalis lanata," BMJ, 1996. https://www.bmj.com/content/312/7035/912.1 (accessed 2026-05-18).

[77] Royal Society, "An Account of the Success of the Bark of the Willow in the Cure of Agues," Philosophical Transactions of the Royal Society of London, 1763. https://royalsocietypublishing.org/doi/10.1098/rstl.1763.0033 (accessed 2026-05-18).

## Appendix: Implementation Details

### Source Inventory

| Source | Date | Contains | Timeline role |
|---|---|---|---|
| Session `504c186b-b730-4ab2-957c-a36d601f7b9b` | cycle 27 | Listed researcher session | Full transcript unavailable; used as cycle context only. |
| Worker event `cdb62567-79f1-4c76-a563-6469c531d675` | 2026-05-18 | Track 5 free-tier chemistry recovery | Records two manual accepted-key candidates and no predictor rerun. |
| Session `20757142-97dc-424b-b730-1765357d2dcc` | cycle 28 | Listed worker session | Full transcript unavailable; local artifacts and ledger event used. |
| Worker event `f23f8644-a9dd-42bd-95ee-9f9bd2dc8fc4` | 2026-05-18 | Track 4 free-tier BIOCLIM recovery | Records coordinates recovered, but no numeric BIOCLIM or comparator readiness. |
| Worker event `7c3c79db-c2c9-4df0-8b3d-cc407f55a3bc` | 2026-05-18 | Free-tier recovery integration | Integrates Track 1/4/5 branch outcomes and preserves header-only ledgers. |
| Sessions `5614c09a-9e3f-450c-83d8-10cd69852fee`, `55fd3b4f-a380-4c48-9707-ad4d8d957bbe`, `81e05f8b-b8d6-4b05-8fee-22c112a6c33a` | cycle 29 | Listed researcher, worker, auditor sessions | Full transcripts unavailable; local artifacts, ledger events, and supplied audit report used. |
| Worker event `b77f9c32-d0aa-4c02-9f5a-7fa9c7fbba66` | 2026-05-18 | Track 1 namespace reconciliation package | Builds WFO projection and GBIF sidecar diagnostic tables. |
| Auditor event `d2e8e456-2f64-43ff-86a6-81c8cfe5ea3c` | 2026-05-18 | Track 1 reconciliation audit | Validates the package and restricts it to readiness-only sidecar use. |

### Code Organization

Cycle 27 was documentation-centered. Its primary artifact is `tracks/track5/reports/track5_free_tier_non_duke_temporal_chemistry.md`.

Cycle 28 Track 4 used four scripts: `fetch_free_tier_occurrences.py`, `build_free_tier_bioclim_vectors.py`, `search_open_cwr_comparators.py`, and `plot_free_tier_bioclim_recovery.py`. The focused test was `tests/test_track4_free_tier_bioclim_recovery.py`.

Cycle 29 Track 1 used `build_free_tier_namespace_reconciliation.py` and `plot_free_tier_namespace_reconciliation.py`. The focused test was `tests/test_track1_free_tier_namespace_reconciliation.py`.

### File Counts

| File | Lines |
|---|---:|
| `tracks/track5/reports/track5_free_tier_non_duke_temporal_chemistry.md` | 81 |
| `tracks/track4/reports/track4_free_tier_bioclim_recovery.md` | 55 |
| `tracks/track4/scripts/fetch_free_tier_occurrences.py` | 226 |
| `tracks/track4/scripts/build_free_tier_bioclim_vectors.py` | 157 |
| `tracks/track4/scripts/search_open_cwr_comparators.py` | 145 |
| `tracks/track4/scripts/plot_free_tier_bioclim_recovery.py` | 52 |
| `tests/test_track4_free_tier_bioclim_recovery.py` | 68 |
| `reports/reopen/free_tier_recovery_integration.md` | 55 |
| `tracks/track1/reports/track1_free_tier_namespace_reconciliation.md` | 88 |
| `tracks/track1/scripts/build_free_tier_namespace_reconciliation.py` | 280 |
| `tracks/track1/scripts/plot_free_tier_namespace_reconciliation.py` | 59 |
| `tests/test_track1_free_tier_namespace_reconciliation.py` | 89 |
| `prediction_ledger.tsv` | 1 |
| `speculation_ledger.tsv` | 1 |
| `promise_ledger.jsonl` | 212 |

### Test Results

The supplied cycle 29 audit reports:

```text
python3 -m pytest -q tests/test_track1_free_tier_namespace_reconciliation.py tests/test_track1_free_tier_reticulation_recovery.py tests/test_free_tier_recovery_integration.py
13 passed in 0.66s
```

It also reports:

```text
python3 -m long_exposure.tools.promise_check <run-root>
exit 0, 212 events, inherited warnings only

python3 -m long_exposure.tools.org_check <run-root>
exit 0, inherited root-layout warnings only
```

The reporter did not re-audit these results. They are reported as supplied audit findings.

### Cross-Reference Map

| Origin | Consuming artifact | Meaning |
|---|---|---|
| Track 5 free-tier report | Cycle 28 integration | Two accepted-key manual candidates refine H5 but do not validate it. |
| Track 4 occurrence and comparator tables | Cycle 28 integration | Coordinates are available, but climate and comparator validation remain blocked. |
| Track 1 branch-local recovery | Track 1 namespace reconciliation | GBIF accepted-key signal required WFO projection or sidecar labeling. |
| Track 1 namespace reconciliation audit | Master ledgers | Sidecar is readiness-only; no master prediction/speculation row is added. |
| `MANIFEST.md` | This report appendix | Updated to the cycles 27-29 snapshot while preserving the existing `## Key Files` section verbatim. |

### Record Gaps

The environment did not provide session-search or session-fetch tools. The direct session IDs supplied for cycles 27-29 were therefore not fetched as full transcripts. This report uses the local workspace artifacts, append-only ledger events, and supplied audit report instead.

### Coherence Review

The report was reviewed once for flow, term definition, claim boundaries, and traceability. The main boundary to preserve is that the Track 1 audit validated the reconciliation package, not H1 as a biological prediction.
