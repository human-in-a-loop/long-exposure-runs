---
created: 2026-05-17T20:00:00Z
cycle: 3
run_id: run-phytograph-cycle3-postmerge-e34b5b2c1c6c
agent: worker
milestone: _plan/wave1-postmerge-integration
---

# Wave 1 Post-Merge Integration Report (fork e34b5b2c1c6c)

**Role.** Single-coordinator post-merge integration after the 8-clone Wave 1 fan-out collapsed. This document is the worker's consolidated audit of what arrived, what passes, what defers to Barrier 1 proper, and the open work-list.

**Scope.** Read-only assessment. No staging table is rewritten in this cycle. The directive explicitly prohibits new research directions in a post-merge cycle; the §6 work-list below is the **handoff to the next-cycle coordinator** that will run Barrier 1's destructive normalization.

## 1. Per-clone disposition (verified on disk)

| Clone | Milestone | Floor | Achieved | Status | INGEST_AUDIT.md | Format |
|---|---|---|---:|---|:-:|---|
| 0 | M1.1 taxonomy backbone | ≥50k taxa | 60,000 | validated | ✅ | parquet + csv |
| 1 | M1.3 reticulation | ≥30k counts / 2k events | 12 / 5 | data-limited (access blocker) | ✅ | TSV |
| 2 | M1.4 paleobotany | ≥200 extinct fauna | 237 | validated | ✅ | JSONL |
| 3 | M1.5 convergence | ≥5 lists × ≥500 taxa | 12 of 13 lists | validated | ✅ | TSV |
| 4 | M1.6 domestication | ≥1000 CWR pairs | 397 (23 multi-parent edges) | data-limited (expansion needed) | ✅ | TSV |
| 5 | M1.7 chemodiversity | 1000 taxa / 8 families / 300 cmpds | 2,315 / 112 / 24,751 | validated | ✅ | TSV |
| 6 | M1.8 FM harness | paid-provider scaffold | 12 pass / 3 skip | out-of-scope for free/open run (stub only; no live spend) | ⚠ | code + JSONL telem |
| 7 | M1.9 wikidata/commons | 30k crosswalk / 10k media | 15,269 / 160 | data-limited (API throttle) | ✅ | TSV |

**Five clones above floor. Three data-limited with documented blockers and disposition recommendations in §5 below.**

## 2. Cross-clone consistency checks

| Check | Result | Notes |
|---|:-:|---|
| INGEST_AUDIT.md present in every staging dir | ✅ | 8 / 8 |
| Substrate-isolation: writes confined to per-source namespace | ✅ | No clone touched another's namespace |
| Provenance/license fields present | ✅ | Every staged row carries source-id + access date + license tag (per per-clone audits) |
| Schema v1.0 conformance (node + edge type names) | ✅ | All clones use frozen schema vocabulary; no clone introduced new types |
| `pending_crosswalk=true` on raw scientific-name keys | ✅ | M1.1 owns the canonical accepted-key; all other clones defer |
| Discipline gate on `convergence_signature` (zero allowed pre-instrument) | ✅ | Clone 3 emitted 0; rejected_records.tsv documents 23 quarantine refusals |
| Discipline gate on inferred `anachronism_candidate_edge` (zero allowed) | ✅ | Clone 2: 31 cited / 0 inferred |
| Sovereignty guard on ethnobotany (Moerman/PROTA/PROSEA) | ✅ | Clone 5: hard-fail probe present; 0 violations |
| Floor-cleared OR explicit data-limited declaration | ✅ | 8 / 8 (5 cleared, 3 declared) |

**Result:** the wave is mergeable. No clone is malformed; no cross-clone collision.

## 3. Divergences requiring coordinator decisions at Barrier 1

| Divergence | Severity | Resolution path |
|---|---|---|
| **Format heterogeneity** — clone 2 = JSONL; clone 6 = code + telemetry JSONL; clones 0/4/5/7 = TSV; clone 0 also has parquet; clone 1/3 = TSV | low | Barrier 1 canonicalization: ingest all formats, emit canonical parquet on the merged substrate. Mechanical, not contested. |
| **Test framework heterogeneity** — `unittest` (clones 0, 1, 2) vs `pytest` (3, 4, 5, 6) | very low | Functional equivalence; no action required this cycle. |
| **Live vs proxy ingestion posture** — clone 2 literature-curated (no network), clone 6 stub-only (no keys), clone 7 partially live (rate-limited); clones 0/3/4/5 ran live or via bulk dumps | medium | Must surface in Phase 6 validation: rows carrying `access_mode: literature-curated` cannot supply primary evidence for paleo-validation predictions; they are seed rows only. |
| **Scale dispersion** — clone 3 staged 420k AusTraits edges; clone 1 staged 12 chromosome rows | high (for Track 1) | Track 1 enrichment (M2.T1) must wait on M1.3 access decision OR proceed at data-limited scale with explicit downstream caveat. |

## 4. Cross-cutting findings (lifted to risk register)

These were surfaced by individual clones but are now cross-cutting and belong in `risk_register.md` (already covered by R8 source-density and a new R-bias-NH-temperate row that the next-cycle owner should append):

- **Source-density confound, Track 5.** Dr. Duke alone clears the chemodiversity floor. The ablation "remove Dr. Duke" is now a Wave-4 M4.Ax requirement, not optional.
- **Northern-Hemisphere temperate bias.** Confirmed in clones 0 (WFO anchor), 1 (CCDB sampling), and 5 (Moerman geographic scope). Tracks 1, 3, and 5 must stratify Phase-6 validation by latitude band.
- **Anachronism canon clean.** Clone 2's 31 anachronism candidates are all literature-cited; zero inferred. Track 2 M3.T2 instrument can use this as a clean seed.
- **CWR-pair shortfall, Track 4.** 397 / 1000 staged; 131 `CWR_pool_for_<crop>` placeholders need per-species expansion from Vincent et al. 2013 Table S1.
- **Track 6 paid-provider scaffold is out of scope.** Clone 6 built a paid-provider API harness from the original prompt wording, but this run is constrained to free/open-source/public materials only. No live provider calls were made; future Track 6 work must use local/open models, public datasets, static benchmark generation, and deterministic offline scoring rather than USD caps or provider-key smoke tests.
- **Wikidata/Commons fragility.** SPARQL pagination is unstable; dump-based ingestion is the recommended Barrier 1 recovery path.

## 5. Gap-item triage (handoff to Barrier 1 coordinator)

In priority order. **These are recommendations; the coordinator owns the actual decisions and the writes.**

1. **Storage canonicalization** — convert clone 2 JSONL to parquet on the merged substrate; verify clones 0/4/5/7 TSV/parquet schemas line up with `phytograph_schema.md` v1.0. Mechanical.
2. **Taxonomic crosswalk union** — merge clone 0's `accepted_taxa.parquet` (60k) ⊕ clone 7's Wikidata QID crosswalk (15k) ⊕ raw-name fields from clones 1–5 ⇒ canonical `wfo_id ↔ ott_id ↔ powo_id ↔ gbif_taxon_key ↔ qid` map. Clone 0's 62 taxonomic_conflicts are *inputs*, not pre-resolved.
3. **Synonym normalization pass** — apply clone 0's `synonym_clusters.parquet` (113,582 rows) to all per-source raw names. Record diversity-before vs diversity-after for the H8 ablation.
4. **Canonical-key dedup** — union-by `(τ_E, sorted(node_ids), source_id)` per schema §6. Intentional intra-source duplication preserved (per clone 2 note).
5. **Gap decisions (require ledger event for each):**
   - **M1.3 (reticulation):** authorize CCDB bulk download + Wood 2009 supplement parse, OR accept Wave 2 Track 1 start at data-limited scale.
   - **M1.6 (domestication):** authorize Vincent 2013 Table S1 expansion + Genesys per-accession bioclim extraction (raster cache outside staging).
   - **M1.9 (wikidata/commons):** authorize dump-based ingestion path; abandon SPARQL pagination as primary.
6. **Coverage report** — emit `coverage_report.md` at workspace root (this post-merge cycle produces a first cut; see `coverage_report.md`).

## 6. Validator state and known minor errors

`python3 -m long_exposure.tools.promise_check <run-root>` returns:

- **2 hard errors**, both pre-existing from cycle-2 events and append-only ledger semantics:
  - line 85: event_id `auditor-closure-m18-clone6` is not a valid UUID (M1.8 auditor closure event). Append-only; no rewrite. Inherited.
  - line 99: M1.3 transitioned `validated → in-progress` without an intervening `reopened` event (clone-1 side-wave at 18:20Z added a bulk-intake path while M1.3 was already validated). Append-only; the validator's expected `reopened` interstitial cannot be retro-inserted.
- ~50 warnings: orphan reports/* from prior-campaign legacy run + missing `merge_report.md` files in `long-exposure/fork-e34b5b2c1c6c/clone-{1,3,4,5,6,7}` (already triaged by `_archive/legacy-taxonomy-run-artifacts` and the `_manager/ledger-integrity` close at 18:35Z).
- Two new orphan artifacts under managed paths (cycle-2 reticulation enrichment preflight files created without ledger reference): `scripts/build_reticulation_enrichment_preflight.py` and `tests/test_reticulation_enrichment_preflight.py`. Recommend a `_plan/orphan-cleanup-reticulation-preflight` ledger event in the next worker cycle.

**Verdict:** validator-state is stable. The 2 hard errors are inherited audit backlog and do not block Barrier 1. They should be resolved by either (a) the next manager intervention proposing a validator allowlist extension, or (b) tolerated as historical-evidence rows.

## 7. Single-line recommendation to next-cycle coordinator

Proceed to Barrier 1 with the §5 work-list; treat the M1.3 and M1.9 gap items as binding constraints for Wave-2 Track-1 start, M1.6 as binding for Track-4 specifically, and accept the remainder of the substrate as ready for read-only consumption by Wave-2 enrichment clones.
