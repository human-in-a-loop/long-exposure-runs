---
title: "Final Audit Report — Music-Gen Run (Delta Audit)"
date: "2026-09-05"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Final Audit Report — Music-Gen Run (Delta Audit)

- Run id: `run-2026-08-28T040704Z`
- Mode: delta (baseline committed 2026-09-02; delta scope covers cycles committed after that boundary)
- Scope: only NEW per-cycle deliverables newer than the committed baseline. Prior findings are not re-litigated.
- Wall-cap hit: false
- Focus songs: Chicken Grease (mandatory), What If I Go, Rome, Peach Dream, Disco A
- Report source glob: `reports/cycles/report_cycles_*.md` (plus its enumerated siblings)

---

## 1. Status distribution (delta slice)

Milestones touched or introduced in the delta slice, by unified status:

| status                    | count |
|---------------------------|-------|
| validated (high)          | 47    |
| validated (medium)        | 0     |
| in-progress               | 1     |
| action_required           | 1     |
| deferred                  | 3     |
| superseded (implicit)     | 1     |
| invalidated               | 0     |
| not-started               | 4     |

Note: the "superseded (implicit)" row corresponds to the M-V4-RULES-1 c20 scaffold, whose on-disk state has been replaced by a c21+ substantive implementation with no explicit `_plan/register-*` ledger event — see finding 7 and §5.

## 2. Plan adherence

The delta slice advances four v4 closure milestones and extends v3-spine bookkeeping. Each new milestone was landed with an explicit rubric, three-way `rubric_hash*` byte-equality chain, and byte-determinism × 2 evidence where applicable. Anchor preservation (READ-ONLY predecessor SHAs unchanged pre==post) was verified per cycle.

| Milestone                                              | Terminal status this slice | Confidence |
|--------------------------------------------------------|----------------------------|------------|
| M-V4-CERT-1                                            | validated                  | high       |
| M-V4-PROFILES-1 (parent)                               | in-progress                | high       |
| M-V4-PROFILES-1/cg-bass-* (arc)                        | validated (bass_v2 accepted per c9 fork) | high |
| M-V4-PROFILES-1/cg-drums-* (arc)                       | validated (OPT3 htdemucs substitution accepted at c14) | high |
| M-V4-PROFILES-1/cg-guitar-* (arc)                      | validated (OPT3 htdemucs substitution auto-resolved at c15) | high |
| M-V4-PROFILES-1/cg-piano, cg-other (audibility null)   | validated (audibility-grounded null) | high |
| M-V4-PROFILES-1/{wig,rome,disco-a,peach-dream}-opened  | validated (skeleton only)  | high       |
| M-V4-SHOWCASE-1/cg-ab-full-render                      | validated (LANDS_pending_operator) | high |
| M-V4-RULES-1/scaffold-c20                              | validated in POR narrative but on-disk SUPERSEDED by c21+ substantive implementation without registration | medium (POR view) / high (on-disk view) |
| M-V4-RULES-1/pinned-profile-schema-v1                  | validated                  | high       |
| _manager/M-V4-METRIC-SEMANTICS-c16                     | action_required            | high       |
| M-V4-EAR-1, M-V4-GEN-1, M-V4-CLOSE-1                   | not-started                | n/a        |

Every substantive milestone that landed in this slice did so with a frozen three-way `rubric_hash*` chain and an anchor-preservation snapshot; the delta audit found no case where a "landed" claim was unaccompanied by the artifacts required by its own rubric.

## 3. Confidence calibration

All `validated` events in the delta slice carry `confidence.level = high`. No `low` or `provisional` confidence terminal states appear in the delta window. Two `high` confidence classifications warrant an explicit calibration note:

- **M-V4-RULES-1/scaffold-c20** — the POR row is `validated/high`, but the on-disk state has moved past the scaffold contract (see finding 7). The `validated/high` label is honest for the c20 event as authored; the drift is that no c21+ event has been emitted to close the loop.
- **_manager/M-V4-METRIC-SEMANTICS-c16** — `action_required/high`. The high-confidence classification refers to the strength of the empirical diagnostic (Pair A identity=0.0 rules out similarity semantics decisively), not to a claim that any threshold-gated verdict is safe.

## 4. Residual debt

The delta slice leaves four categories of open work:

1. **Metric-semantics escalation (open, operator-owned).** `_manager/M-V4-METRIC-SEMANTICS-c16` remains `action_required`, `blocked_on_operator=true`. Two named paths: (A) treat `embedding_cos_vggish` as the distance it empirically is, and invert every threshold that was worded as a similarity gate; (B) apply a one-line `1 - distance` correction in the panel or the objective, restoring the intended similarity semantics and re-issuing the determinism certificate per FD-16(a). Neither path is auto-resolvable via the agent-picks invariants; the choice is genuinely operator-authoritative.
2. **M-V4-RULES-1 audit-trail gap (open, c21+ author-owned).** A full substantive c21 extractor is on disk, but no ledger event, no `_plan/register-*` row, and no rubric/verdict trio have been emitted for `M-V4-RULES-1/substantive`. Recommended reconciliation: reopen `M-V4-RULES-1/scaffold-c20` as `superseded`, register `M-V4-RULES-1/substantive` in plan-of-record with c21+ narrative, and pin on-disk SHAs of the six substantive artifacts (`statistical_model.json`, `sequence_model.json`, `audio_descriptors.jsonl`, `rules_artifact.jsonl`, `manifest.json`, `replay_proof.json`) plus the two determinism sibling directories. This reconciliation is NOT proposed as a `reconcile:true` event here because the substantive implementation's own PASS/PARTIAL/FAILS verdict against M-V4-RULES-1 success criteria was never emitted; the correct authority is the c21+ author.
3. **Focus-song v4 profiles beyond Chicken Grease.** WIG, Rome, Disco A, and Peach Dream have `stem_manifest.json` skeletons but no stage-1/stage-2 sweeps, no profiles, no A/B renders. Each is explicitly `blocked_on: _manager/M-V4-METRIC-SEMANTICS-c16` in its manifest to avoid committing to a threshold interpretation.
4. **Downstream v4 closure milestones.** `M-V4-EAR-1`, `M-V4-GEN-1`, and `M-V4-CLOSE-1` are `not-started`. Their prerequisites (M-V4-PROFILES-1, M-V4-RULES-1) are partially satisfied (Chicken Grease profiled; RULES scaffolded then implicitly superseded).

## 5. Findings by severity

**0 CRITICAL. 2 MODERATE. 5 MINOR.** No finding invalidates any operator-blessed or internal-gate-blessed substantive deliverable. Every finding is confined to the audit trail (POR-transcription drift, silent supersession) or to an open operator-owned decision.

### MODERATE — 2

**M-1 (MODERATE). Open embedding-metric semantics escalation confirmed.** _manager/M-V4-METRIC-SEMANTICS-c16.

The c16 diagnostic (`data/v4/diagnostics/embedding_metric_semantics.json`, SHA `2884dd3203f4e561…`) empirically settles that `embedding_cos_vggish` is a distance: Pair A (identity) returns 0.0, which a similarity metric would not do. Every v4 acceptance threshold was worded as a similarity gate (`≥ 0.60` CONFIRMED, `≤ 0.40` RULED_OUT). Under distance semantics those gates fire in the wrong direction: RULED_OUT at `≤ 0.40` fires on near-identical candidates. The five CG-instrument arcs where the frozen composite ranked a non-source-of-truth ahead of a source-of-truth (bass organ-over-bass, drums Orchestra/Power over Standard, guitar Nylon over Rock, plus the two family-2 near-zero readings) are consistent with threshold inversion rather than genuine acoustic anomaly. The c17 CG A/B delivery is threshold-orthogonal (bass_v2 rides the composite-relative WINNER rule that was accepted independently at c9; drums and guitar accepted via OPT3 htdemucs stem substitution; piano and other via audibility-grounded null; vocals via hybrid overlay), so it remains defensible under either Path A or Path B. Everything else in v4 is blocked on this decision.

**M-2 (MODERATE). Silent supersession of M-V4-RULES-1/scaffold-c20 by an unregistered c21+ substantive implementation.** M-V4-RULES-1/scaffold-c20.

The c20 rubric describes `scripts/v4_rules/{__init__,extract_v4}.py` as stubs raising `NotImplementedError('c21+ substantive implementation')`. On disk, `extract_v4.py` is a full substantive c21 module (docstring: "M-V4-RULES-1 substantive extractor"; header cycle=21) that emits `statistical_model.json`, `sequence_model.json`, `audio_descriptors.jsonl`, `rules_artifact.jsonl`, `manifest.json`, `replay_proof.json`, plus `run1/` and `run2/` determinism siblings under `data/v4/rules/`. `grep` on the promise ledger returns zero events for `M-V4-RULES-1/substantive` and zero `_plan/register-c21-v4-rules-*` rows. The scaffold's own smoke-test anchor `data/v4/rules/scaffold_smoke_test.json` (SHA `8250774547d0c55d…`) still matches its POR pin — orthogonal evidence that the scaffold was legitimately built at c20 before being superseded on disk. This is an audit-trail gap, not a code defect; the substantive implementation looks disciplined (deterministic outputs, `env_pin` sidecar, `/usr/bin/python3` guard, no PRNG, no `sidecar_nonfactor`). But the ledger and plan-of-record no longer describe the true state of M-V4-RULES-1, which is exactly the "Cover-Up" anti-pattern the plan warns against.

### MINOR — 5

**m-1. POR path drift — M-V3-RULES-1/first-activation/rubric-committed.** POR narrates the v3 rules spec doc at `docs/v3_rules_deterministic_extractor_spec_c23.md`; on-disk canonical path is `docs/specs/v3_rules_deterministic_extractor_spec_c23.md`. SHA `e81ff589200f6d6b…` byte-exact under the on-disk path; three-way `rubric_hash_v3_rules` chain preserved. Cosmetic.

**m-2. POR anchor drift — M-V4-PROFILES-1/cg-bass-sf2-replay-proof-v2.** POR c4 row pins `bass_v2.replay_proof.json` at SHA `86948709746b966a…`; on-disk full SHA is `4b9eea98052d6b2f…` (full divergence, no first-16-hex collision). Substantive REPLAY_PROOF claim intact: internal `run1_sha256 == run2_sha256 == 832868d0ea8a81ca…`, verdict `REPLAY_PROOF_HOLDS`, canonical 7-key `env_pin_sha256`. Only the file-level POR anchor is stale.

**m-3. POR SHA drift — M-V4-RULES-1/scaffold-c20 (narrative view).** POR narrative pins `scripts/v4_rules/__init__.py` at SHA `c8603851d54c56c4…` and `extract_v4.py` at `1e0ad1131f090003…`; on-disk 24-hex prefixes are `3189da3df7cfb49f…` and `2b1764e3fa9b4c75…`. This finding treats the divergence as narrative-transcription drift; finding M-2 above reclassifies the same divergence as silent supersession under the on-disk-authoritative reading (FD-1). The scaffold smoke-test anchor is unchanged, which is why the two findings coexist: c20's scaffold work was real, and something newer landed after it without a ledger event.

**m-4. POR anchor drift — M-V4-PROFILES-1/cg-bass-sf2-replay-proof.** POR c2 row narrates `run1_sha256 == run2_sha256 == 832868d0ea8a81ca…`; on-disk `data/v4/profiles/31a164f845f8e27e/bass.replay_proof.json` holds `run1_sha256 == run2_sha256 == c69775040c325b86…` (full SHA divergence). The `REPLAY_PROOF_HOLDS` claim is intact (both runs SHA-equal to each other). File mtime postdates `bass.json` and is consistent with regeneration after the c11 `_infra/replay-channel-aware-fix-c11` (which changed sf2 dispatch semantics). No substantive invalidation; only the POR-pinned internal-run SHA is stale.

**m-5. POR anchor drift + malformed SHA — M-V4-PROFILES-1/cg-drums-profile-v1-emitted.** POR c11 narrates `drums.json` SHA `f48b7d7fb1bf28d3ff6b9c9e17e64f1eef8586fa1e56d4cdbf7d0d7d1a2432ba` and `drums.replay_proof.json` SHA `a7877f2ec1dd67b4a4d1cf9bde8fe12c2b32d95a63a6f2e1ed01f7d67bf2c8a0`; on-disk full SHAs are `f48b7d7fb1bf28d3fb65c5827c47a917…` and `a7877f2ec1dd67b4d0e2160717afa4f2…` — first-16-hex collision on both, tail divergence. Additionally the POR narrative includes a 62-hex-character drums-MIDI SHA `0fd71ce70a26365c8fb0f9f87531178f9f9c18cc419d042a3869989c990ef2` (malformed — 64-char correct value on disk: `0fd71ce70a26365c2acf08b9f87531178f9f9c18cc419d042a3869989c990ef2`). Substantive facts intact: profile_id `83728154-6f48-5c5d-a558-b4d82523ac1b`, program 16 Power Kit, verdict `REPLAY_PROOF_HOLDS`, `run1==run2==dadafcfc0153f002651c23975c3845dd3f8ca7896d263faf1c52eb54d64b8d7c`.

## 6. Future work (anchored to residual debt)

- **Anchored to M-1.** Operator adjudication of the metric-semantics escalation. Whichever path the operator selects, the follow-up work is scoped and deterministic: Path A rewrites threshold interpretations in the rubric and the profile-writer discipline docs and re-issues verdicts against the inverted floors; Path B applies `1 - distance` in exactly one location (either `objective.py` or `embedding_panel.py`), re-runs the certificate under FD-16(a), and re-evaluates all five CG arcs on the intended similarity scale. Either path is one focused cycle of work.
- **Anchored to M-2.** c21+ authors should emit (i) an `M-V4-RULES-1/substantive` milestone row with the c21 rubric and success criteria, (ii) a `_plan/register-*` row for the six substantive artifacts, (iii) an event that supersedes the c20 scaffold (`supersedes_path` as `str` per c14 lemma), (iv) an anchor-preservation snapshot confirming the c20 smoke-test SHA is unchanged, and (v) an explicit verdict (LANDS/PARTIAL/FAILS) against M-V4-RULES-1's stated success criteria.
- **Anchored to residual debt item 3.** WIG/Rome/Disco A/Peach Dream stage-1 sweeps remain queued behind M-1. Once thresholds are settled, the sweep-storage hygiene protocol (score-and-delete; `≤ 500 MB` working audio per instrument; `df` check before each stage; disk `≤ 90%`) already proved out on Chicken Grease can be reused verbatim.
- **Anchored to residual debt item 4.** M-V4-EAR-1 (lightweight exemplar ear on CG + Molasses + Essence + Desire + Peach Dream) is compute-bounded (~1 h target) and does not depend on M-1. M-V4-GEN-1 depends on both M-V4-RULES-1 (waiting on M-2) and M-V4-EAR-1. M-V4-CLOSE-1 rolls all of the above.
- **Anchored to m-1..m-5.** POR-transcription drift is corrigible cheaply in the next housekeeping cycle: canonicalize the v3 rules spec path in the POR narrative; refresh five POR-pinned SHAs against on-disk artifacts using the on-disk-authoritative FD-1 rule; correct the one malformed 62-hex drums-MIDI SHA to its 64-hex on-disk value. None of these is on the critical path.

## 7. Reconciliation log

No `reconcile: true` events were proposed in this delta audit. All seven findings are `reconcile: false`:

- The five MINOR POR-transcription drifts are within the on-disk-authoritative FD-1 rule and do not warrant a formal supersession event — they would be corrected in a housekeeping pass rather than reconciled through a ledger event.
- The MODERATE metric-semantics escalation is `action_required` and `blocked_on_operator`; reconciliation is not the auditor's authority.
- The MODERATE M-V4-RULES-1 silent supersession requires the c21+ author to emit the missing milestone rows, plan-of-record registration, and verdict event — again outside the final auditor's authority. The auditor documents the gap; the c21+ author closes it.

The harness will therefore commit zero reconciliation events with `agent: "final_auditor"` after this stage.

## 8. Delta-audit summary

Baseline final audit report was committed 2026-09-02. The delta window covers the cycles that produced M-V4-CERT-1, the full CG M-V4-PROFILES-1 arc, M-V4-SHOWCASE-1/cg-ab-full-render, the WIG/Rome/Disco A/Peach Dream skeletons, M-V4-RULES-1/scaffold-c20 (plus its silent on-disk supersession), M-V4-RULES-1/pinned-profile-schema-v1, and the two M-V3-RULES-1 first-activation sub-leaves.

Result of the delta pass: **0 CRITICAL, 2 MODERATE, 5 MINOR**. The two MODERATE findings are the headline (open operator escalation on metric semantics; unregistered c21+ M-V4-RULES-1 substantive supersession). The five MINOR findings are the audit-trail POR-transcription-drift class that was already emerging in the baseline window; the on-disk artifacts remain authoritative and no substantive claim is broken.

The delta audit does not reopen any baseline finding, does not propose a reconciliation event, and does not overwrite operator authority on any open decision.
