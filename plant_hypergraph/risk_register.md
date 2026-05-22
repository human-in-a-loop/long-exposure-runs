<!--
created: 2026-05-17T15:50:00Z
cycle: 1
run_id: run-phytograph-cycle1
agent: worker
milestone: M0.1
-->

# Risk Register — PhytoGraph Campaign

| # | Risk | Severity | Affected tracks | Mitigation | Detection signal |
|---|---|---|---|---|---|
| R1 | **Accidental paid-provider use** — Track 6 may drift into pay-as-you-go or key-gated model APIs despite the free/open-source run constraint. | high | T6 | Paid provider APIs are out of scope. Do not export API keys, do not run live paid-provider smoke tests, and do not build milestones around USD caps. Use free/open-source or already-local models; if unavailable, publish benchmark/scoring artifacts and mark execution `data-limited`. | Audit search for Anthropic/OpenAI/Gemini/Pl@ntNet/iNaturalist live-call instructions, API-key requirements, pricing tables, USD caps, or non-stub telemetry. |
| R2 | **Indigenous-data sovereignty mishandled** — ethnobotanical attribution stripped during cleaning or merge. | high | T5 (especially), Atlas | All `ethnobotanical_use_assertion` edges retain people-group + source attribution. No anonymization step. Sovereignty-flag column in `data_source_audit.md` for sources 27 (Moerman), 28 (PROTA), 29 (PROSEA). | Barrier 1 conformance check fails any edge missing attribution. Atlas displays attribution prominently. |
| R3 | **Paleobotany over-interpretation** — anachronism candidates promoted to "established anachronism" in downstream narrative. | high | T2 | Schema § 3.3 hard-restricts `anachronism_candidate_edge` evidence scope. Atlas distinguishes prediction from evidence visually. All Track 2 outputs flagged "model-derived hypothesis." | Barrier 4 ledger reconciliation: any T2 row with status=`validated` must cite an external authoritative paleobotany source. |
| R4 | **Speculative bioactivity claims** — Track 5 predictions read as medical advice. | high | T5, T6 (probe wording), Atlas | All `phytochemical_assertion` edges constrained to "compound detected, by this source"; predictions explicitly framed as "candidate for screening." No clinical-efficacy claims anywhere. Atlas surface includes explicit disclaimer. | Audit: search for clinical-claim phrases in any deliverable; reject before Barrier 5. |
| R5 | **Schema drift across source clones (Barrier 1)** — clones invent new edge types or modify allowed-evidence-scope. | medium | substrate, all tracks | Schema v1.0 frozen in `phytograph_schema.md`. Source-clone outputs validated against the canonical-key + edge-type inventory at Barrier 1. Any non-conformant row blocks the merge. | Barrier 1 conformance script lists rejected rows. Worker prompt for source clones explicitly cites `phytograph_schema.md` and forbids extension. |
| R6 | **Cross-track contamination at Barrier 2** — Track 5 reads in-progress Track 4 predictions, or Track 6 builds probe questions whose answers leak through. | medium | T4, T5, T6 | Read-only mounts where possible. Track 6 ground-truth construction must build from frozen substrate, not from other tracks' Phase 4 instrument outputs. Conformance check at Barrier 2. | Barrier 2 conformance script: trace which track-namespace each edge was read from; flag cross-namespace reads. |
| R7 | **Image-licensing breach** — Wikimedia / GBIF media re-displayed in Atlas without attribution. | medium | Atlas, T6 (visual probe) | Every `image_evidence` edge carries license + attribution in `P(e)`. Atlas rendering layer refuses to display any image lacking those fields. | Atlas QA: count images with empty license/attribution; must be zero before Barrier 3. |
| R8 | **Source-density confound dominates predictions** — TCI, CPS, chemodiversity scores reflect literature volume rather than biological signal. | medium | T1, T3, T5 (H7) | Cross-cutting ablation suite (Phase 8) explicitly controls for publication density, screening intensity, image availability. Residualized variants of each statistic computed. Falsification protocols in each track scope-doc flag this collapse. | Per-track ablation report: ρ(score, publication_density) reported; > 0.7 triggers a residualization rerun. |
| R9 | **Synonym-normalization gaps** — un-normalized synonyms inflate apparent diversity (H8). | medium | substrate, T1, T3, T5, T6 | WFO is the canonical synonym backbone. Cross-source crosswalk at Barrier 1. Per-track `_synonym_normalized` variants computed. | Coverage report: % of taxa resolved to a WFO accepted-name node. Aim ≥ 90%; below 75% triggers a re-ingest. |
| R10 | **Single coordinator bottleneck at barriers** — Barriers 1, 2, 4 stall waves. | low | all | `barrier_preempt_timeout_seconds` documented per directive. Stuck clones produce `data-limited` rather than blocking. Late-arrival merge documented as a gap. | Wave-elapsed-time monitor: barrier > 2× expected wave time → preempt. |
| R11 | **Atlas reflex** — team gravitates to building a polished wiki. | low | Atlas | Directive explicitly deprecates "wiki as flagship." Atlas content gated on Phase 4 predictions existing. M3.A success criteria require per-track prediction surfacing, not data browsing alone. | Auditor at Barrier 3 rejects Atlas pages without per-track prediction columns. |
| R12 | **TRY / Tropicos access blocked** — registration delays stall trait/taxonomy ingestion. | low | T3 (trait), substrate | Directive marks both optional. Track 3 uses curated trait lists from M1.5 (Sage C4 lists, succulence lists, myrmecochory lists) which do not require TRY. | M1.5 ingestion proceeds without TRY; if Track 3 minimum scale is at risk, file `data-limited`. |
| R13 | **Held-out validation leakage** — canonical Janzen-Martin / polyploid / discovery-date cases leak into training data via Wikipedia / Wikidata. | medium | T1, T2, T5 | Explicit hold-out sets per track scope-doc. For Track 5 historical validation, the substrate is temporally frozen with audit trail. For T1/T2, supervised-style labels are excluded from input. | Per-track leakage audit at validation: any held-out target appearing in training-edge node set is logged and counted as a leak. |
| R14 | **Prompt-template effects in Track 6** — error rates dominated by phrasing rather than knowledge gaps. | medium | T6 | ≥ 3 prompt-template variants per question (paraphrasing). Cross-template variance reported as a primary finding, not hidden. | Variance > 30% across templates triggers a template-confound flag in the per-question row. |
| R15 | **Polyploid / hybrid record gaps for held-out validation** — fewer than 20 well-documented canonical cases. | low | T1 | CCDB + Wood-et-al-style supplements should cover ≥ 30 canonical polyploids. Cultivar pedigree literature adds crops. If still < 20, T1 validation falls back to a stratified survey across angiosperm orders. | M1.3 coverage report counts unique `polyploidization_event` and `hybridization_event` edges. |

**Total risks recorded: 15** (well above the ≥ 8 floor).

## Severity legend

- **high**: campaign-publishable result blocked or guardrail-violation possible
- **medium**: track-level result blocked or confounded
- **low**: known constraint with mitigation in place

## Per-track risk profile summary

| Track | Top risk | Why |
|---|---|---|
| substrate | R5 (schema drift) | Barrier 1 is the choke point. |
| T1 | R8 (source density) | TCI vs publication-density confound. |
| T2 | R3 (paleo over-interpretation) | Janzen-Martin candidates can be read as established. |
| T3 | R8 (source density) | CPS family-size confound. |
| T4 | R4 (overconfidence) + sister-species-baseline collapse. | Substitution recommendations carry real downstream weight. |
| T5 | R2 (sovereignty) + R4 (bioactivity claims) | Highest-stakes track for guardrails. |
| T6 | R1 (API cost) + R14 (prompt-template effect) | Both are operational, not scientific. |
