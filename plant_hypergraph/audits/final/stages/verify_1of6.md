# Verify 1/6: M1 Data Feasibility and M2 Schema

Generated: 2026-05-17T15:01:23Z

## Slice
- Milestones verified: M1, M2.
- Source for slice assignment: `audits/final/explore.md`.

## M1 Evidence Check
- Artifact existence: 6/6 present: `REFERENCES.md`, `docs/data_feasibility_map.md`, `scripts/probe_public_sources.py`, `data/source_probe_results.json`, `data/source_feasibility_matrix.csv`, and `data/stale/auditor_probe_results.json`.
- Required source coverage: WFO, GBIF, Open Tree of Life, BIEN/RBIEN, and TRY are all covered in the markdown map and CSV matrix.
- Required feasibility fields are supported. The markdown table includes endpoint/route, auth, license/citation, limits/risks, support/non-support, and prototype recommendation columns; the CSV has explicit `limitations` and `prototype_recommendation` fields.
- Literature/method coverage is present for hypergraph learning, hierarchical classification, biodiversity knowledge graphs, plant taxonomy databases, phylogenetic synthesis, name resolution, and trait feasibility.
- Probe evidence exists as a structured no-auth source probe with top-level keys for access date, examples, probes, script, and summary.
- Support judgment: M1 evidence supports the validated/high terminal state. No unsupported source-feasibility claim was found in this pass.

## M2 Evidence Check
- Artifact existence: 1/1 present: `docs/hypergraph_schema.md`.
- Required schema components are present: typed nodes, required hyperedge families, incidence matrix convention, weight/provenance conventions, label/task space, baselines, leakage controls, and falsification criteria.
- Required hyperedge families are all named: `taxonomic_parentage`, `synonym_cluster`, `trait_syndrome`, `regional_checklist_context`, `occurrence_provenance`, `reticulate_or_hybrid_signal`, and `missing_rank_bridge`.
- Allowed/forbidden evidence claims are represented in the hyperedge-family table via `Allowed inference` and `Forbidden inference`, which is stronger evidence than a loose narrative statement.
- Layer separation is explicit for taxonomy, phylogeny, nomenclature, trait similarity, occurrence evidence, and dataset labels.
- Support judgment: M2 evidence supports the validated/high terminal state. No schema coverage gap was found in this pass.

## Findings Appended
- None. An initial literal keyword pass over-flagged phrasing variants (`Limits and risks`, `Allowed inference`); the false positives were removed before stage close after direct evidence inspection.

## Gate Evidence
- Evidence files exist and support the claims for validated M1/M2 terminal states.
- Low/provisional confidence follow-up: none for M1/M2 terminal states; both terminal events are high-confidence auditor validations.
- Ledger contradictions: none reported for this slice.
