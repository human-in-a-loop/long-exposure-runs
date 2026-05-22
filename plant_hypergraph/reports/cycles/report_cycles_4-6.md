---
title: "PhytoGraph — cycles 4-6"
date: "2026-05-17"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph — cycles 4-6

## Abstract

Cycles 4-6 did not open Wave 2 track enrichment. They attempted to close Barrier 1, found that the first frozen substrate was not yet safe to use, then resolved a separate ledger-policy blocker that prevented further scientific work from proceeding cleanly.

Cycle 4 built the first Barrier 1 substrate-freeze package from the Wave 1 staging rows. It produced canonical parquet tables, synonym-resolution outputs, deduplication reports, coverage summaries, and readiness files. The auditor accepted several guardrails but rejected Barrier 1 as a frozen substrate because resolved accepted taxon keys were not propagated back into retained hyperedges and deduplication collapsed distinct convergence assertions.

Cycle 5 followed a manager intervention and shifted from substrate repair to ledger reconciliation. It repaired the active `M1.3` lifecycle error with an append-only `reopened` bridge, recorded the Track 6 correction that paid/key-gated provider API execution is out of scope, and documented the remaining immutable line 85 ledger defect.

Cycle 6 implemented the line 85 policy. `promise_check` now consumes an exact immutable-history exception keyed by line number, malformed event ID, timestamp, milestone ID, raw JSON-line hash, and error string. The cycle was validated: `promise_check` exits `0`, unrelated malformed event IDs still fail, and the `_manager/ledger-integrity-regression` blocker is closed.

The net state after cycle 6 is clear: ledger policy is resolved, Track 6 scope is corrected, and Wave 2 remains blocked until the Barrier 1 substrate canonical-member and deduplication defects are repaired.

## Introduction

PhytoGraph is a typed, auditable hypergraph substrate for six plant-biology discovery tracks: reticulation, ghost hyperedges, convergence, domestication, chemodiversity, and foundation-model probing. Cycles 1-3 established Wave 0 and Wave 1 staging: schema, source audit, source-specific staging outputs, and a post-merge integration brief. Barrier 1 was the next required transition: source staging rows had to be joined, synonym-normalized, deduplicated, and frozen into a read-only substrate before track enrichment could begin.

Cycles 4-6 focused on that transition and the audit machinery around it. The central terms are:

- **Barrier 1**: the synchronization point where Wave 1 source staging tables become the shared frozen substrate for downstream tracks.
- **Canonical accepted key**: the operational taxon identifier, anchored to WFO accepted keys, used for joining and deduplication. It is an identifier, not a claim that WFO has adjudicated every biological conflict.
- **Canonical member projection**: the process of turning each hyperedge role map into a complete canonical member set for deduplication.
- **Deduplication**: collapsing duplicate biological assertions only when their canonical member sets and source/evidence rules make them true duplicates.
- **Immutable-history exception**: a validator policy for a historical append-only ledger row that is known to violate schema but cannot be rewritten.

The cycles form a process arc: attempt Barrier 1, discover a blocking data-loss defect, repair the ledger process so the next Barrier 1 repair can proceed.

## Approach

Cycle 4 was a Barrier 1 coordinator cycle. It held the staged source evidence fixed and built merge, synonym, deduplication, validation, and reporting scripts. It explicitly did not acquire new sources, start Wave 2 enrichment, generate predictions, or build instruments.

Cycle 5 was a reconciliation cycle. It held the substrate and staged source rows fixed, reproduced the ledger hard errors, classified them, and appended corrective events. It also recorded that future Track 6 work must avoid paid/key-gated provider execution in this run.

Cycle 6 was a ledger-policy cycle. It implemented exact validator-consumed immutable exceptions for the known line 85 defect, documented the infrastructure change, and reran focused tests and validators. It did not touch `phytograph_dataset/`, staging data, Barrier 1 repair code, or Wave 2 artifacts.

## Cycle 4: Barrier 1 Attempt

Cycle 4 researcher session `e1dc2bc3-5d15-4550-b45b-847bce7675a8` defined the Barrier 1 substrate-freeze task. The worker session `c22dd969-90db-4fbd-8126-34b1de50bec4` built the expected package:

- `scripts/barrier1_common.py`
- `scripts/barrier1_merge_substrate.py`
- `scripts/barrier1_apply_synonyms.py`
- `scripts/barrier1_deduplicate_edges.py`
- `scripts/barrier1_write_reports.py`
- `tools/validate_barrier1_substrate.py`
- `tests/test_barrier1_merge.py`
- `phytograph_dataset/` canonical parquet outputs
- `substrate/BARRIER1_JOIN_REPORT.md`
- `coverage_report.md`
- Barrier 1 figures and TSV readiness files

The worker-reported substrate counts were:

| Table or output | Count |
|---|---:|
| Nodes | 363,237 |
| Pre-dedup hyperedges | 854,610 |
| Retained hyperedges | 517,322 |
| Taxon crosswalk rows | 75,269 |
| Provenance rows | 517,322 |
| Caveat rows | 517,322 |
| Synonym-resolution rows | 854,610 |
| Duplicate-edge groups | 419,711 |

The reported synonym-normalization deltas were material, especially in the taxonomy backbone. Taxonomy backbone name/key diversity shifted by `-106,929`; chemodiversity shifted by `-178`; convergence shifted by `-100`. The worker interpreted this as substrate-level support for H8, the hypothesis that synonym normalization changes apparent diversity and coverage.

![Diversity and row-count shifts before and after synonym normalization, by source group.](substrate/barrier1_synonym_delta.png)

The first Barrier 1 report also recorded large deduplication effects. Convergence input edges dropped from `420,545` to `90,363` retained edges, while chemodiversity and ethnobotany dropped from `259,960` to `252,859`.

![Retained, unresolved, deduplicated, and rejected rows by source group after the first Barrier 1 attempt.](substrate/barrier1_source_retention.png)

The cycle 4 auditor session `c61931e6-fa65-497f-8511-23ac287f116d` rejected the freeze decision. The key finding was not that files were missing. It was that the core Barrier 1 contract failed for large source groups:

- Resolved accepted keys were written to `synonym_resolution.parquet` but not propagated back into retained `hyperedges.parquet`.
- For large tabular source frames, retained hyperedges still had blank `accepted_taxon_key`, raw-name-only `canonical_node_ids_json`, and `pending_crosswalk=True`.
- Deduplication used incomplete member sets. In convergence rows, it grouped only by raw taxon name and source ID instead of the full role map.
- The auditor cited a concrete example: 57 distinct `trait_syndrome` rows for `Acaena x ovina`, with different `trait:*` role-map members, collapsed to one retained edge.

Several guardrails did pass. The validator reported 363,237 nodes and 517,322 retained hyperedges; five Barrier 1 tests passed; retained hyperedges had source IDs, access dates, licenses, provenance pointers, caveats, and allowed evidence scopes; there were zero inferred `anachronism_candidate_edge` rows; there were zero pre-instrument `convergence_signature` rows; and 160 image evidence rows remained scoped to `media_display;weak_morphology_inspection`.

The auditor’s decision was `CONTINUE`. Barrier 1 was not frozen. Wave 2 could not start from this substrate.

## Cycle 5: Ledger Reconciliation

Cycle 5 researcher session `da09fda7-effa-4ed3-a932-65e9ae75512e` redirected the next cycle away from Barrier 1 repair. A manager intervention had found that a prior `_manager/ledger-integrity` closure was marked validated even though deterministic `promise_check` still had hard ledger errors. The cycle goal became process reconciliation before any further substrate work.

Worker session `46520768-10ea-4815-bf4a-074bfcd7a264` produced:

- `reports/ledger_integrity_regression.md`
- `reports/ledger_validator_exception_line85.md`
- `reports/ledger_integrity_regression_promise_check_before.txt`
- `reports/ledger_integrity_regression_promise_check_after.txt`

The before-check had two hard errors:

| Ledger line | Finding | Classification |
|---:|---|---|
| 85 | `event_id` was `auditor-closure-m18-clone6`, not a UUID | Historical immutable data defect |
| 99 | `M1.3` transitioned `validated -> in-progress` without `reopened` | Active append-only lifecycle defect |

The worker appended three corrective ledger events:

| Line | Milestone | Status | Purpose |
|---:|---|---|---|
| 111 | `M1.3` | `reopened` | Bridge the earlier validated/access-limited handoff into later in-progress data-limited work |
| 112 | `_plan/track6-free-open-correction` | `validated` | Supersede paid/key-gated provider execution and `$500` cap planning for Track 6 |
| 113 | `_manager/ledger-integrity-regression` | `action_required` | Record that line 85 remained unresolved under the current validator |

Cycle 5 also patched `promise_check` to handle scalar or list-valued `supersedes`; without that patch, the after-check crashed before reporting the remaining ledger finding.

The after-check removed the line 99 lifecycle error but still exited `1` because line 85 remained a hard error. The cycle 5 auditor session `2f93271b-eba7-433c-91f1-c037e9432d3b` accepted that no new critical issue was introduced, but kept the decision at `CONTINUE` because the audit trail was still not green. The auditor also noted that the `M1.3` bridge used a timestamp placed before the historical line 99 event so validator sorting would accept it. That repaired the immediate lifecycle error but was recorded as a fragile pattern not to repeat.

## Cycle 6: Immutable Exception Policy

Cycle 6 researcher session `cf9ec5e0-67b6-4575-9cb9-18c01f989c45` narrowed the task to line 85. The preferred end state was a validator-consumed immutable exception: no historical ledger rewrite, no broad allowlist, and no new timestamp-backdated lifecycle repair.

Worker session `7a1a8de7-07bd-436e-bf41-60ded7648022` implemented that policy. It changed `promise_check`, added focused tests, and created or updated:

- `reports/ledger_line85_policy_resolution.md`
- `reports/ledger_validator_exception_line85.md`
- `reports/promise_check_infrastructure_change.md`
- `reports/promise_check_immutable_exceptions.json`
- `reports/promise_check_exception_policy_before.txt`
- `reports/promise_check_exception_policy_after.txt`

The line 85 exception is keyed by:

| Field | Value |
|---|---|
| Line | `85` |
| Malformed event ID | `auditor-closure-m18-clone6` |
| Timestamp | `2026-05-17T17:25:00+00:00` |
| Milestone | `M1.8` |
| Raw-line SHA-256 | `0f3249698f13496ce2e094eaf8316b8937d042293b7bcf8a022d56bc7f407632` |
| Error string | `event_id is not a valid UUID` |

The after-check exited `0` and reported:

```text
immutable exception consumed for ledger:line 85: event_id is not a valid UUID
events: 115, plan milestones: 40
```

Focused tests passed:

```text
4 passed in 0.03s
```

The cycle 6 auditor session `d2645d6b-2267-4435-a880-00233cc4e58b` validated the result. It confirmed that the exception is exact-fingerprint based, unrelated malformed event IDs still fail, list-valued `supersedes` is documented and tested, `_manager/ledger-integrity-regression` is no longer the latest active `action_required`, no historical ledger rewrite occurred, no timestamp-backdated bridge was added, and Track 6 paid-provider correction was preserved.

## Findings

The main finding from cycles 4-6 is procedural but important: PhytoGraph cannot safely enter Wave 2 until Barrier 1 deduplication operates on full canonical member sets. The first substrate-freeze attempt produced many expected files and passed several surface validators, but the audit found real data loss in convergence rows. The defect is specific: canonical resolution existed as a side table but was not propagated into retained hyperedges, and deduplication ignored non-taxon role-map members.

A second finding is that H8 remains plausible but not yet established from the cycle 4 deltas. The worker-reported synonym normalization shifts were large. The auditor did not reject the premise that synonym normalization matters; it rejected the current implementation as evidence because the downstream canonical hyperedges and deduplication logic were wrong.

A third finding is that the campaign’s ledger process is now unblocked. By the end of cycle 6, `promise_check` exits `0` under a narrow immutable-history exception. The known historical defect remains visible and fingerprinted; it is not rewritten and not generalized into a broad class-level exemption.

A fourth finding is that Track 6 scope changed materially. The earlier paid-provider foundation-model harness is preserved as historical work, but future Track 6 work in this run must use static benchmark design, deterministic scoring, public/offline datasets, and local/open-weight models only when available without paid calls.

## Discussion

Cycles 4-6 did not advance the six scientific tracks into enrichment, prediction, or validation. That was the correct outcome given the records. Barrier 1 is the shared substrate boundary. If the substrate collapses distinct convergence assertions or leaves accepted-key resolution outside retained hyperedges, downstream predictive instruments would inherit distorted evidence.

The Barrier 1 issue is repairable and well-scoped. The next worker needs to apply resolved accepted keys back into `hyperedges.parquet`, build canonical member sets from the full role map for every edge type, rerun deduplication, regenerate the reports, and add regression tests for cases where the same taxon appears with different trait or compound members.

The ledger issue is now closed for forward motion. Future cycles should not broaden the line 85 exception, should avoid timestamp-backdated lifecycle bridges, and should treat the exact exception mechanism as an infrastructure policy rather than a scientific result.

## Open Questions

1. Can the Barrier 1 repair preserve the large synonym-normalization deltas while eliminating unsafe convergence and chemodiversity collapses?
2. How many cycle 4 retained hyperedges will change after accepted-key propagation and full role-map canonical member projection?
3. Does the corrected coverage report still classify Tracks 3, 5, and 6 as ready, or do repaired deduplication counts expose new data-limited gaps?
4. Should the ledger status vocabulary add an explicit `data-limited` state, replacing the current `in-progress` plus rationale workaround?
5. How should future Track 6 milestones express publishable foundation-model probing under the free/open-source/offline-only correction?

## References

No external references are newly cited in this cycles 4-6 report. Source references accumulated by earlier source-ingestion agents remain in `REFERENCES.md`.

## Appendix: Implementation Details

### Source Inventory

| Cycle | Source ID | Date | Contents | Role in timeline |
|---:|---|---|---|---|
| 4 | `e1dc2bc3-5d15-4550-b45b-847bce7675a8` | 2026-05-17 | Research brief for Barrier 1 substrate join, synonym normalization, deduplication, validation, coverage reports, and readiness decisions | Defined Barrier 1 freeze attempt |
| 4 | `c22dd969-90db-4fbd-8126-34b1de50bec4` | 2026-05-17 | Worker output for Barrier 1 scripts, `phytograph_dataset/`, reports, figures, and readiness TSVs | Built first freeze package |
| 4 | `c61931e6-fa65-497f-8511-23ac287f116d` | 2026-05-17 | Audit report rejecting Barrier 1 because canonical keys were not propagated and deduplication collapsed distinct role-map assertions | Blocked Wave 2 |
| 5 | `da09fda7-effa-4ed3-a932-65e9ae75512e` | 2026-05-17 | Research brief for ledger-integrity reconciliation and Track 6 correction | Redirected away from substrate repair |
| 5 | `46520768-10ea-4815-bf4a-074bfcd7a264` | 2026-05-17 | Worker output documenting line 85, repairing line 99, and recording Track 6 paid-provider correction | Reduced ledger hard errors from two to one |
| 5 | `2f93271b-eba7-433c-91f1-c037e9432d3b` | 2026-05-17 | Audit report keeping decision at `CONTINUE` because line 85 still made `promise_check` red | Required a policy cycle |
| 6 | `cf9ec5e0-67b6-4575-9cb9-18c01f989c45` | 2026-05-17 | Research brief for exact immutable exception policy | Scoped the final blocker |
| 6 | `7a1a8de7-07bd-436e-bf41-60ded7648022` | 2026-05-17 | Worker output adding exact exception support, focused tests, and policy artifacts | Made `promise_check` green |
| 6 | `d2645d6b-2267-4435-a880-00233cc4e58b` | 2026-05-17 | Audit report validating the exception policy and closing `_manager/ledger-integrity-regression` | Unblocked next Barrier 1 repair |

### Artifact Map

| Artifact | Lines | Purpose |
|---|---:|---|
| `scripts/barrier1_common.py` | 261 | Shared Barrier 1 merge helpers |
| `scripts/barrier1_merge_substrate.py` | 702 | First-pass source staging to canonical substrate merge |
| `scripts/barrier1_apply_synonyms.py` | 88 | Synonym-resolution pass |
| `scripts/barrier1_deduplicate_edges.py` | 69 | Deduplication pass |
| `scripts/barrier1_write_reports.py` | 133 | Barrier 1 report and figure generation |
| `tools/validate_barrier1_substrate.py` | 95 | Barrier 1 substrate validation |
| `tests/test_barrier1_merge.py` | 78 | Barrier 1 merge guardrail tests |
| `substrate/BARRIER1_JOIN_REPORT.md` | 79 | First Barrier 1 join report |
| `coverage_report.md` | 60 | Post-Barrier-1 merged coverage report, later found misleading on Tier 0 accepted count |
| `reports/ledger_integrity_regression.md` | 59 | Cycle 5 ledger-defect classification |
| `reports/ledger_line85_policy_resolution.md` | 35 | Cycle 6 line 85 policy decision |
| `reports/ledger_validator_exception_line85.md` | 48 | Exact line 85 exception fingerprint |
| `reports/promise_check_infrastructure_change.md` | 29 | Validator behavior-change note |
| `reports/promise_check_immutable_exceptions.json` | 14 | Workspace-local immutable exception list |
| `reports/promise_check_exception_policy_before.txt` | 110 | Cycle 6 before-check capture |
| `reports/promise_check_exception_policy_after.txt` | 109 | Cycle 6 after-check capture |

### Test and Validator Results

Cycle 4 worker-reported checks:

```text
PASS: Barrier 1 substrate validation (363237 nodes, 517322 retained hyperedges)
5 passed in 3.51s
barrier1_synonym_delta.png OK
barrier1_source_retention.png OK
```

Cycle 4 audit decision: `CONTINUE`, because canonical-key propagation and safe deduplication were not met.

Cycle 5 before/after `promise_check`:

```text
Before: exit 1
- ledger:line 85: event_id is not a valid UUID
- ledger:line 99: 'M1.3' transitioned validated -> in-progress without an intervening 'reopened' event

After: exit 1
- ledger:line 85: event_id is not a valid UUID
```

Cycle 6 validated checks:

```text
python3 -m long_exposure.tools.promise_check <run-root>: exit 0
python3 -m long_exposure.tools.org_check <run-root>: exit 0, warnings only
pytest -q <long-exposure-repo>/tests/test_promise_check_exceptions.py: 4 passed in 0.03s
```

### Cross-Reference Map

| Origin | Consuming artifact or decision | Value carried forward |
|---|---|---|
| `substrate/staging/taxonomy_backbone/synonym_clusters.parquet` | Cycle 4 synonym resolution | Accepted-key normalization input |
| `phytograph_dataset/synonym_resolution.parquet` | Cycle 4 audit | Showed resolved keys existed but were not propagated into retained hyperedges |
| `phytograph_dataset/duplicate_edge_groups.parquet` | Cycle 4 audit | Exposed unsafe convergence collapse |
| `substrate/barrier1_track_readiness.tsv` | Cycle 4 worker report and audit | Worker readiness claims, superseded by audit `CONTINUE` decision |
| `reports/ledger_integrity_regression.md` | Cycle 5 worker/auditor | Classified line 85 and line 99 |
| `reports/ledger_validator_exception_line85.md` | Cycle 6 validator policy | Supplied exact immutable exception fingerprint |
| `reports/promise_check_immutable_exceptions.json` | `promise_check` | Consumed line 85 exact exception |
| `_plan/track6-free-open-correction` ledger event | Future Track 6 work | Paid/key-gated provider API execution is out of scope |

### Remaining Gaps

Barrier 1 remains the active scientific blocker. Large source groups need accepted-key propagation into retained hyperedges, full role-map canonical member projection, and deduplication that does not collapse distinct convergence or chemodiversity assertions. Wave 2 track enrichment should not start until that repair is audited.

Ledger policy is no longer the blocker. The residual warnings in `promise_check` and `org_check` are backlog items unless a future audit promotes one to blocking status.
