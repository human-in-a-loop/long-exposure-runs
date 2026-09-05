# Delta Audit — Stage 3 (Test) 1/1

Working dir: `/home/user/long-exposure-runs/music-gen`
Delta scope (single new report): `reports/cycles/report_cycles_31-31.md` (Music-Gen v4 Cycle 31 Closure, 2026-09-05).

## Adversarial pass — targeted regression checks

### T1. Validator runs
- `python3 -m long_exposure.tools.promise_check .` → **0 ERROR / 5034 WARN**. Warnings are the pre-existing baseline drift class (`ledger-tracked artifact missing: …`) covering historical cycles up to and including c20 M-V4 work + earlier campaigns. Zero of the warnings are new-in-c31; the c31 delivery introduces no new missing artifact.
- `python3 -m long_exposure.tools.org_check .` → **0 ERROR / warns only**. Warns are the same organizational baseline (`scratchpad_stage37_*.py`, `merge_report_*.md`, `zip` files at workspace root, `docs/run_archive/figures/*.png`). None new-in-c31.

Neither validator regressed under the c31 addition.

### T2. Silent supersession scan
Delta scope contains ONE closure document (`reports/cycles/report_cycles_31-31.md`). No `_plan/` supersede event fires in the c31 ledger rows (they are v3 palette-schema rows externally labeled cycle-31). No silent supersession pattern detected: the c31 closure report does not modify any prior baseline file — all pre-c31 committed artifacts (final_audit_report.md et al) are untouched (verified by mtime + baseline-boundary).

### T3. Referenced-artifact integrity (c31 report only)
Grep for `data/v4/*` paths in the c31 report → **11 unique paths, 11/11 present on disk**. SHA/arithmetic anchors re-verified in stage 1 (explore) — all PASS. No orphan reference introduced by c31.

### T4. Plan-of-record vs ledger drift (delta scope)
The c31 report describes the v4 CLOSE cycle using v4 internal cycle numbering (c1–c20). The external cycle-31 ledger rows (30 rows with `"cycle": 31`) belong to the older v3 palette-schema campaign (M-DAW-SPIKE-1/palette-instrument-determinism, M-EAR-1/armed-harness-fixture-reinforcement, etc.). This is not a defect — it is the campaign's declared external-vs-internal numbering convention — but it is the mechanical reason F1 (ledger-vs-disk parity gap for v4 substantive milestones M-V4-EAR-1 / M-V4-GEN-1 / M-V4-CLOSE-1 / M-V4-RULES-1) reproduces adversarially: those M-V4-* milestone_ids never receive completion events in `promise_ledger.jsonl` regardless of how many external cycles have elapsed.

### T5. Supersession-pending scan
No milestone in the delta scope carries a `supersedes_path` field this stage. No transitive supersede chain to re-verify at run scope.

### T6. Regression on prior stage-2 findings
- **F1 (MODERATE, ledger-vs-disk parity gap for v4 EAR/GEN/CLOSE/RULES substantive completion)** — reconfirmed by targeted grep this stage: `grep '"milestone_id":"M-V4-EAR-1"' promise_ledger.jsonl` returns 0 hits despite the c31 closure report certifying LANDS on the ear model + generator. Not a defect of the c31 delivery per se; a plan-of-record hygiene gap for the entire v4 closure arc. Retained as CONFIRMED MODERATE; no new reconciliation event proposed here (rubric §7 for the closure report notes the substantive artifacts hold and are byte-verifiable on disk).
- **F2 (MINOR, c31 audit artifact absent)** — reconfirmed: `find audits/final -name '*cycle31*' -o -name '*c31*'` still empty. Retained as CONFIRMED MINOR.

### T7. Cross-report inconsistency scan
- Report claims `rules_artifact.jsonl` = 97 rules (23+23+23+23+5); on-disk `wc -l data/v4/rules/rules_artifact.jsonl` (stage 1) = 97. PASS.
- Report claims ear scores 4/5 exemplars = 7.0, Desire = 6.16; disk JSON PASS (stage 1).
- Report claims full-song `cg_full.wav` sha `cc919559…`; disk PASS. Also equals `cert_run{1,2}/full_reconstruction.wav` from M-V4-CERT-1 (byte-identical, same file series).

## New findings this stage
None. Both stage-2 findings survive re-test.

## Findings appended to `audits/final/findings.jsonl`
0 rows appended (findings.jsonl unchanged from stage 2 state: 2 rows total, both CONFIRMED).

[OUTPUT: final_audit_stage]
Stage 3: Adversarial test pass complete; validators clean (0 ERROR, all WARN pre-existing baseline outside delta scope); F1 MODERATE + F2 MINOR both re-confirmed; no new findings; 0 regressions introduced by c31 delivery.
File: /home/user/long-exposure-runs/music-gen/audits/final/stages/test_1of1.md
Findings appended: 0
[END OUTPUT: final_audit_stage]
