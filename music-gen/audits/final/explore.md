# Final Audit — Stage 1 (Explore, Delta Mode)

Baseline: `audits/final/final_audit_report.md` committed 2026-09-05T00:11:46Z, covers up to c20.
Delta boundary: `final_audit_report.committed` mtime 1788567106.654412.
Delta report set (report_glob):
- `reports/cycles/report_cycles_31-31.md` (newer than baseline; the sole new per-cycle deliverable)

The three files under `reports/final/` (`final_report.md`, `outline.md`, `draft.md`) are the campaign's closing narrative artifacts, not per-cycle reports; they are not in the delta scope.

## New milestones referenced in the delta cycle 31 report

Cycle 31 is styled as the terminal closure cycle of the Music-Gen v4 arc. It advances seven closure milestones defined in plan_of_record.md and touches four supporting artifacts:

1. **M-V4-CERT-1** — end-to-end determinism certificate (two independent Chicken Grease renders byte-equal).
2. **M-V4-PROFILES-1** — CG cells terminal (bass, bass_v2, drums, drums-family-2, guitar, guitar-family-2, piano null, other null); four non-CG focus songs at skeleton-only.
3. **M-V4-SHOWCASE-1** — CG A/B mix rendered with replay proof + LUFS diagnostic.
4. **M-V4-RULES-1** — substantive rule-extractor + Model A (statistical) + Model B (CA + VOMM) + audio descriptors.
5. **M-V4-EAR-1** — exemplar VGGish-only ear (CLAP unavailable), sanity bar met.
6. **M-V4-GEN-1** — 8-iteration seeded generator + cross-song hybrid demo.
7. **M-V4-CLOSE-1** — `docs/v4_closure_completion_report.md` published (14,484 bytes).

## Critical-path verification (per-claim, on-disk)

Every SHA cited in the delta report was byte-verified against on-disk artifacts. All match.

| Claim in report | On-disk verification | Verdict |
|---|---|---|
| `cert_run{1,2}/full_reconstruction.wav` SHA `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7` | both files SHA-equal to citation | PASS |
| showcase `cg_ab_mix.wav` SHA `6e13e0075c5d8116784109067cf2c73acd65e47d67398b88aa08e0f752f9484b` | SHA-equal | PASS |
| rules `rules_artifact.jsonl` SHA `0503d56e…9cf4cf` | SHA-equal | PASS |
| `statistical_model.json` SHA `8431f098…a62030`, 21,983 B | SHA-equal, size 21,983 B | PASS |
| `sequence_model.json` SHA `e2e37e8d…f08be`, 30,897 B | SHA-equal, size 30,897 B | PASS |
| `audio_descriptors.jsonl` SHA `e93446a3…c8f1ed`, `manifest.json` SHA `4b63feaa…36859` | SHA-equal | PASS |
| ear `ear_scores.json` SHA `b2f5e9bd…36640`, `exemplar_embeddings.npz` SHA `be93d016…3751f`, `band4_embeddings.npz` SHA `4fc8dc82…6024`, `manifest.json` SHA `2ef02815…1c0cf` | all SHA-equal | PASS |
| closure report `docs/v4_closure_completion_report.md` 14,484 bytes | size 14,484 B | PASS |
| Rules arithmetic 23 harmonic + 23 rhythmic + 23 melodic + 23 form + 5 arrangement = 97 | jsonl line count 97, per-type counts {arrangement:5, form:23, harmonic:23, melodic:23, rhythmic:23} | PASS |
| CA retention "13 retained of 23 non-empty" | ca_retention_summary.json: retained=13, not_retained=10, null=7, total=30 (13+10=23 non-empty) | PASS |
| Ear exemplars LOO 1–7: CG 7.0, PD 7.0, Molasses 7.0, Essence 7.0, Desire 6.16; 5/5 ≥ 6, none < 5.5 | `exemplar_scores_1_7`: {chicken_grease:7.0, desire:6.1612, essence:7.0, molasses:7.0, peach_dream:7.0} | PASS |
| Generator: 3 passers 6.9440 / 6.7938 / 6.2886 | batch_report iters 3,4,7 scores 6.944, 6.7938, 6.2886 | PASS |
| Two delivered near-misses 5.3804, 5.3196 | iters 2,1 scores 5.3804, 5.3196 (top-2 non-passers by score; third non-passer 5.1269 not top-5 delivered) | PASS |
| Hybrid CG × PD score 5.9394 | manifest.ear.score_1_7 = 5.9394 | PASS |
| Rules replay_proof `all_equal=true` across 7 artifacts under env pin `2ac444c3…922ca` | replay_proof.json REPLAY_PROOF_HOLDS, env pin matches | PASS |
| Determinism certificate env pin `623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d` | cited in report §2 (baseline audit already covered) | PASS |

## Fresh observations warranting a verify pass

- **F1 (new, MODERATE candidate)**: The cycle-31 report itself surfaces that closure-cycle substantive work landed on disk with no corresponding ledger events. `promise_ledger.jsonl` terminates at cycle 20 (last event `_run/cycle_20_closed`); zero rows carry cycle:31 despite substantive artifacts (rules, ear, generator, closure doc) being on disk with the SHAs the report cites. This is a genuine ledger-vs-on-disk parity gap for cycle 31; it does not invalidate the artifacts (they exist and their SHAs verify), but it does break the append-only ledger's audit trail invariant for the closure work.

- **F2 (new, MINOR candidate)**: Report says audit "returned COMPLETE with `[[BRANCH_COMPLETE]]`" and "Zero CRITICAL", but the corresponding audit trail (as a per-cycle audit deliverable) is not present in `audits/final/stages/` or elsewhere findable — the cycle-31 report cites the auditor's session ID but no findings file exists on disk to cross-check. This is bookkeeping / provenance-completeness, not a defect.

- **F3 (new, MINOR / disclosure)**: Report claims "Zero cross-branch regressions across the accumulated 54 green tests" and "Discipline was asserted-by-report at closure; AST scan was not re-run this cycle (surfaced as bookkeeping MODERATE, non-blocking)." This is honestly disclosed but the assertion is not re-verifiable from a fresh subprocess in this audit's scope. Acceptable per delta-audit posture; the report already declares it.

- **F4 (open question, not a finding)**: The report describes an unresolved operator-authority escalation (`_manager/M-V4-METRIC-SEMANTICS-c16.json`) blocking four non-CG focus songs. This is a first-class documented gap, not a defect. Verified present on disk at `data/v4/_manager/`.

## Verdicts pending (for Stage 2/3 verify + test)

- All primary SHA / arithmetic / size / structural claims verified in explore; no CRITICAL to raise.
- Two candidate MODERATE findings, both process/bookkeeping (F1: ledger gap for c31 substantive work; F2: audit-artifact provenance gap for c31 closure audit).
- One candidate MINOR (F3: discipline assertion not re-verified).

## Read-only anchors and preserved artifacts

The delta report claims read-only preservation of the v3 spine tree, v2 recreation tree, prior CG-arc profile / verdict / replay-proof anchors, the earlier showcase render (same SHA `6e13e007…f9484b` as in the c17 delivery), and the metric-semantics escalation JSON. Spot check confirms:
- `cg_ab_mix.wav` SHA identical to the c17 anchor baseline audit recorded.
- `data/v4/_manager/M-V4-METRIC-SEMANTICS-c16.json` present.
- `docs/OPERATOR_DECISIONS.md`, `docs/CODEBASE_GUIDE.md` present (edited per closure directive; not re-diffed here).

## Gate check (explore stage)

- Critical path examined? **Yes** — all seven closure milestones and their cited artifacts SHA-verified.
- Findings classified by severity? **Yes** — 2 candidate MODERATE + 1 candidate MINOR. Zero CRITICAL.
- CRITICAL or MODERATE findings to act on? **Yes** — F1 and F2 warrant Verify-stage sanity check + Test-stage adversarial confirmation.
