---
title: "Cycles 1-3 Clone 0 Report — M-RULES-1/extraction/rated-corpus (Fork c320de981fda)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_1-3_clone_0]

# Cycles 1-3 Clone 0 Report — M-RULES-1/extraction/rated-corpus (Fork c320de981fda)

## Abstract

Cycles 1-3 of clone-0 (fork `c320de981fda`) close **`M-RULES-1/extraction/rated-corpus`** at **RATED_CORPUS_PARTIAL** — a first-class honest verdict under a frozen 3-verdict rubric. **Assignment-vs-audit mismatch note**: the task brief describes `M-RECREATE-1/full-corpus-recreation` (37-song batch extension), but the executed and audited work in this range is the first M-RULES-1 rule extraction at real-audio corpus scale (43 songs → 1030 rows in new peer shard `data/rules/ledger_rated_corpus.jsonl`). This report faithfully documents the executed work per the audit that was actually issued. The recreation-branch scope should be re-fielded in a subsequent cycle if intended; the audit trail on the executed rules-extraction work is complete and validated.

## Verdict

**RATED_CORPUS_PARTIAL** (VALIDATED at cycle 3 auditor decision; harmonic-shortfall PARTIAL OR-clause explicitly fires per pre-registered rubric).

## Rubric SHA Anchor Chain (Three-Way Byte-Equal)

| Location | SHA-256 |
| --- | --- |
| `docs/rules_extraction_rated_corpus_rubric.md` | `ed572704f205a723a9bb6e2f8b7a5d122e9aa186af6a00a05a60a6e59013f1c3` |
| `data/rules_rated_corpus/rubric_hash.txt` | `ed572704…f1c3` |
| `verdict.json.rubric_hash` | `ed572704…f1c3` |

Rubric mtime + git-log dual gate PASS (test_01, test_02). Rubric doc 5,734 B, mtime 12:27; report 16,962 B, mtime 12:44.

## Peer-Shard Placement (Protects c26-c30 Anchor Chain)

| Shard | Rows | State |
| --- | --- | --- |
| `data/rules/ledger.jsonl` (c9 + c12) | **76** | byte-equal pre/post (test_11) |
| `data/rules/ledger_i3_dminor.jsonl` (c15) | **86** | byte-equal pre/post (test_12) |
| `data/rules/ledger_rated_corpus.jsonl` (c40, NEW peer) | **1030** | landed this cycle |
| **Total tracked rules across all three shards** | **1192** | — |

c26-c30 canonical-aggregate-SHA anchors thereby preserved. New shard is a dedicated peer, not an extension.

## Rule-Extraction Volumetric (Honest PARTIAL Attribution)

43/43 songs cleanly extracted; 0 duplicate rule_ids across 43 songs (no cross-song collisions).

| Rule Type | Rows | Per-Song Avg |
| --- | --- | --- |
| arrangement | 215 | 5.0/song ✓ |
| form | 215 | 5.0/song ✓ |
| **harmonic** | **86** | **2.0/song — SHORTFALL** |
| melodic | 256 | ~6.0/song ✓ |
| rhythmic | 258 | ~6.0/song ✓ |

**Harmonic shortfall attribution**: one-dimensional; attributable to c12 `insufficient-progression` coercion (`unique(chord_progression) < 2` → skip) firing on 3-4 of the 6 KS-plus-chordify windows for real-audio 30 s trims. Matches rubric's PARTIAL OR-clause verbatim: "one rule_type falls below the ≥5-rows-per-song floor on >5 songs" (here: 43 songs).

## Byte-Determinism × 2 (43/43 Per-Song + Aggregate)

- Aggregate canonical-sort SHA equal across two independent temp-dir runs (test_13).
- 43/43 per-song shards SHA-equal.

## Anchor Preservation (31/31 SHAs — Contract Required 30+)

`data/rules_rated_corpus/anchor_preservation.json`: `all_unchanged=True`, `n_anchors=31`. Covers c37/c38/c39 recreate trees; 5 c9 extractors; 4 c6 schema+validator+writer; 2 rules ledgers; 8 per-song merged.musicxml spot-checks. c9 extractor SHAs and c6 writer+validator SHAs verified unchanged (test_09, test_10).

## Row-Level Validation

- **1030/1030 rows** Layer-1 + Layer-2 clean (test_14).
- **1030/1030 provenance_pointers** resolve to per-song sidecars (test_15).

## Per-Song Hygiene

- 43 `stage_manifest.json` files present.
- 43 songs enumerated in `song_manifest` (test_17).
- Per-song `wall_clock_s` finite on every manifest (test_16).
- Per-song median ≈ 3.0 s (range 0.36-10.0 s); canonical pass ~110 s wall-clock; determinism × 2 adds ~350 s. Well within cycle envelope.

## Test Surface

| Suite | Result |
| --- | --- |
| `tests/test_rules_extraction_rated_corpus.py` | **20/20 PASS** (contract ≥15) |
| `python3 -m long_exposure.tools.promise_check .` | **0 ERRORs** (no new WARN attributable to this cycle; pre-existing shadow-ledger-not-yet-merged WARNs continue) |

## Ledger Events (10; 6 Substantive + 4 Housekeeping; Post-Artefact Per c39 Issue #6)

- 6 substantive `M-RULES-1/extraction/rated-corpus/*` (unsuffixed per c32 for substantive M-*)
- 4 housekeeping under `-clone-0` suffix per c33 harness guard (c39 v3 codified)
- Second-run idempotence verified: 10/10 SKIP via writer-side `LedgerAppendError: duplicate event_id` defense (pre-scan pattern anticipated by brief remains a c41+ carry-forward; writer refusal is behaviourally equivalent for this cycle).

## Cycle Disposition

| Cycle | Researcher Directive | Worker Action | Auditor Decision |
| --- | --- | --- | --- |
| 1 | Rubric-first commit + song manifest + scaffold | Rubric + hash + song_manifest + scripts landed | in-progress |
| 2 | Foreground extraction on 43 songs | Full extraction; 1030 rows; harmonic shortfall surfaced | in-progress with verdict-logic recalibration disclosed (Issue #3) |
| 3 | Verdict + report + tests + ledger + close | RATED_CORPUS_PARTIAL emitted; 20/20 tests; 10 post-artefact events; determinism × 2 confirmed | **VALIDATED** |

## Worker-Surfaced Trade-Offs (All Honestly Disclosed)

1. **Merge-report path**: canonical `/home/user/music-gen-instance/fork-c320de981fda/clone-0/merge_report.md` outside writable scope; fallback `tools/stale/c40_clone0_merge_report_draft.md` per rubric §10 + c39 clone-0 precedent.
2. **Emitter idempotence**: pre-scan-based idempotence failed because shadow ledger lives outside workspace scope; idempotence rides on writer's `LedgerAppendError` duplicate-catch (defensive-in-depth). Pre-scan pattern remains genuine c41 carry-forward.
3. **Verdict-logic recalibration**: first-pass verdict logic used an overly-strict FAILS branch; rubric's PARTIAL OR-clause explicitly covers the observed harmonic shortfall. Corrected inline; verdict re-emitted; 20/20 tests re-run. Reviewed: no post-hoc rubric editing; `rubric_hash` stable.

## State-Machine Discipline (c29 Lemma Respected)

`M-RULES-1/extraction/rated-corpus` is a peer sub-milestone under M-RULES-1. Follows the c9 (n=1 synth) → c12 (n=3 breadth) → c40 (n=43 real-audio) progression. NOT a child of any terminal-validated ancestor.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908`.
- SHA-256 tiebreak; no PRNG (test_06); no `sidecar_nonfactor` (test_08); no `i4_stratified` import.
- Interpreter guard `/usr/bin/python3` on every script (test_07).
- Read-only anchors preserved: 31/31 including c37 recreate_v0; c38 clone-2 recreate_v0_batch; c38 clone-0 ear_v1; c38 clone-1 score_bridge_v2; c9 effects chain + rule extractors; c6 schema/validator/writer.
- c12 `insufficient-progression` coercion policy is a frozen anchor; this cycle did NOT touch it (c41 refinement candidate).
- Rated audio egress-blocked at `*.googlevideo.com` (unchanged 403; retry cadence at conductor level; not required — 43 songs on-disk).
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`.

## Anti-Patterns Locked (5-Count Stable)

c8 octave-suppression; c11 CLAP/VGGish embedding; c22 stability; c23 head-reg; c25 feature-representation — not re-attempted. c31 STILL_GAP / c35 A anti-pattern surface intact. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged.

**c39 "The Assumption" pattern locked out**: foreground execution honoured; per-song idempotence via `stage_manifest.json` skip; ledger emission after artefacts land (post-artefact per Issue #6). Zero recurrence.

**SILENT_SONG_DROPS_FORBIDDEN honoured**: 0 songs dropped; harmonic shortfall named per-song, not silent.

## Assignment-vs-Audit Mismatch (Disclosed)

The task brief for this fanout clone assignment describes **M-RECREATE-1/full-corpus-recreation** (37-song batch extension of c38 clone-2's 5-song batch), whereas the executed and audited work in this range is **M-RULES-1/extraction/rated-corpus** (first rule-extraction pass at real-audio corpus scale on 43 songs). The audit trail on the executed rules-extraction work is complete, VALIDATED, and internally coherent. If the recreation-branch scope was intended, it should be re-fielded in a subsequent cycle with a fresh assignment brief; the preserved handoff assets from c37 (single-song) and c38 clone-2 (5-song) remain intact for that future work.

This report faithfully documents the audit that was issued for cycles 1-3.

## Merge Disposition

Merge report at workspace fallback `tools/stale/c40_clone0_merge_report_draft.md` per §10 precedent (canonical path outside writable scope). 10 shadow-ledger rows queued for `concat_clone_ledgers`; c33 harness guard applied to housekeeping only per c32-v2 substantive-unsuffixed convention.

## Cycle-41 Handoff (Priority Order, Per Cycle-3 Auditor Guidance)

**Primary (recommended)**:

1. **`M-RULES-1/extraction/rated-corpus/harmonic-window-refinement`** — test whether adjusting chord-window hop (5 s → 2 s) or relaxing `unique(chord_progression) ≥ 2` to include repeated Roman numerals lifts harmonic on real-audio 30 s trims without perturbing c9's synth_030s harmonic anchor rule_ids. c12 coercion policy is a frozen anchor; c41 peer sub-milestone with its own frozen rubric can commit to a specific relaxation and test against the exact set of 43 songs with a clean re-verdict path.

**Alternative primary (if operator prefers G5 advance)**:

2. **`M-GEN-1/palette-driven-batch-rated-corpus`** — sample from the new 1030-row peer shard through c33 palette-render machinery. K-per-rule_type is now much larger (H=86, R=258, M=256, F=215, A=215), changing the birthday-paradox collision landscape. Comparing per-salt panel deltas against c34/c36 synth-derived palette batches is a well-scoped one-cycle deliverable.

**Deferred M-RECREATE-1/full-corpus-recreation scope** (per assignment-vs-audit mismatch above): re-field with fresh brief if intended. Handoff assets from c37 + c38 clone-2 remain preserved.

**Standing tickets (opportunistic)**:

- **Band-6 `f1cfe4855364ea9b`** (Tom Misch / Yussef Dayes — *Last 100*) focused-rerun from c39 auditor — would flip 36/37 → 37/37 if benign.
- **`_infra/emitter-idempotence-guard-clone-*`** — inherits c39 future risk; generic emitter helper that either does pre-scan (when shadow is in-workspace) OR degrades cleanly to writer-side (when shadow is out-of-workspace) would close this once for the campaign.
- **`_manager/effects-chain-band-selectivity`** — remains opportunistic per c39 pre-registered logic.
- **c38 clone-1 REDEFINED_GAP + normalizer-v2 REFUTED** — mscore3 quantization root-cause narrowing remains opportunistic.
- **c37 VST3 activation** still gated by c36 MIXED verdict.
- **Egress retry** per campaign directive.
- **`_manager/fanout-pipeline-cost-audit`** (carried forward from c42 clone-1 closure) — enumerate which M-* milestones exceed fanout-cycle capacity and must be scheduled sequentially.

## Cumulative Progress

**M-RULES-1 arc**:

| Cycle | Milestone | Songs | Rows | Verdict |
| --- | --- | --- | --- | --- |
| c9 | first extraction (synth seed) | n=1 | 76 (in c9+c12 shard) | validated |
| c12 | breadth extension | n=3 | +86 (c15 i3_dminor shard) | validated |
| **c40 (this)** | **first real-audio corpus extraction** | **n=43** | **1030 (new peer shard)** | **RATED_CORPUS_PARTIAL** (harmonic OR-clause) |

**First M-RULES-1 extraction at real-audio corpus scale**. Progression: c9 n=1 synth → c12 n=3 (synth + 2 breadth) → **c40 n=43 real-audio-derived**. Peer-shard convention (dedicated `ledger_rated_corpus.jsonl`) protects the c26-c30 canonical-aggregate-SHA anchor chain and gives future M-GEN-1 batches explicit opt-in.

**Seven consecutive cycles of rubric-first discipline** (c26-c30, c37/c38/c39 clone-0, c40 clone-0). The mtime + git-log dual gate with MERGE_DEFERRED-tolerant git leg is now boilerplate; cost trivial (a 3 s sleep before scripts land) and payoff unbroken across every cycle it's been applied.

**c39 lessons transferred cleanly**: foreground-only execution honoured; per-song idempotence via `stage_manifest.json` skip; ledger emission after artefacts land. c39 "Assumption" pattern did not recur.

**First-class PARTIAL verdict, cleanly attributed**: one-dimensional harmonic shortfall characterised by mechanism (c12 coercion sensitivity on real-audio 30 s trims), not by fault. Rubric's OR-clause is doing the work it was designed to do — disciplined verdict-design in the campaign's post-c37 era.

**Emitter-idempotence future risk partially addressed via writer-side defense**: pre-scan pattern remains genuine c41 carry-forward; writer-side `LedgerAppendError: duplicate event_id` is a real safety net; 10/10 SKIP on second run confirms end-to-end for this cycle.

**Cross-cycle count**: main ledger stays at 670 rows; 10 c40 clone-0 events await concat-merge at cycle close per c33/c36 fanout-namespace convention. Peer shard adds 1030 rows to `data/rules/ledger_rated_corpus.jsonl`; c9 (76) + c15 (86) unchanged; total tracked rules across all three shards now **1192**.

**c29 state-machine lemma** respected: peer sub-milestone; ledger topology stays a DAG.

**c32 → c33 → c36 v2 → c39 v3** fanout-namespace convention held: 4 housekeeping events under `-clone-0` suffix; 6 substantive `M-*` events unsuffixed per c32-v2 codification.

**Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

[END OUTPUT]
