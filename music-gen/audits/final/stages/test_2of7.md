# Test stage 2 of 7 — delta scope

## Scope
Focus areas per prior handoff:
1. Verify FD-16(c) replay proof coverage for c78 interpolation demo
2. Verify c85-c87 auditor-flagged issues
3. Verify c77-c78 SHA anchor claims on-disk
4. Rescan delta-scope ledger events for missing `agent` field (extend beyond c77-c78)

## Adversarial checks

### C1. FD-16(c) replay proof for c78 new code path — PASS
- `scripts/gen/interpolate_v4.py` present, sha16 `2359f35d2355647d` matches c87 report.
- `scripts/gen/iterate_v4.py` READ-ONLY anchor byte-identical, sha16 `8f1f0b8835bdda1d`.
- Replay proof `data/v4/gen/interpolation_demo/interpolation_demo_donor_a_31a164f845f8e27e_donor_b_88d247468cb6d49f_t_0.5/ab_mix.replay_proof.json`:
  - `verdict = REPLAY_PROOF_HOLDS`
  - `run1_sha256 == run2_sha256 == b129c6d1bac8be90fa32249a012a47e5c9e7b369b0707ca6b2f652de478e690a`
  - `env_pin_sha256 = 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` (canonical 7-key)
- Per FD-16(c) per-family-per-song scope: 1 song (interpolation demo), 1 proof — coverage satisfied.
- Per operator 2026-09-03 ceremony relaxation: single proof per new code path suffices.

### C2. c85-c87 auditor findings — PASS (zero CRITICAL/MODERATE)
- report_cycles_84-86.md: VALIDATED, zero CRITICAL, zero MODERATE, 3 INFO (all non-blocking).
- report_cycles_87-87.md: VALIDATED, zero CRITICAL, zero MODERATE, `[[BRANCH_COMPLETE]]`.
- Verdict matrix reflected accurately in `docs/v4_completion_report_v3.md`.

### C3. c78 completion-report v3.1 amendment on-disk SHA — PASS
- On-disk `docs/v4_completion_report_v3.md` sha256 = `b900b0eeadc00095f7a0c8e3d5660e505d545b19941ca3cf695690eec7e04d09`.
- c87 report claim: post-append SHA `b900b0ee…` ✓ prefix matches.
- Additive amendment (line 244 append) preserves v3 verdict matrix intact per c14 str-supersede lemma at ledger event level.
- POR narrative row `_plan/completion-report-v2-emitted-c29` also cites `341d5bbaf859c8ca…` (c71 append) — confirming multi-append history is consistent with rc7 method-equivalence work.

### C4. Delta-scope missing-`agent` field rescan — CONFIRMS finding from test 1/7
- Full re-scan `cycle >= 77`: 10 total events missing `agent` field.
- Breakdown: c77=4, c78=6. Confirms test 1/7 finding `M-V4-CLOSE-ledger-agent-field-drift-c77-c78`.
- No additional delta-scope cycles affected (c85, c86, c87 events all carry `agent` field).

### C5. c78 interpolation demo ledger event content — PASS
- Ledger event `M-V4-GEN-1/interpolation-demo-delivered-c78` present.
- Artifacts list matches on-disk (ab_mix.wav, ab_mix.manifest.json, ab_mix.replay_proof.json).
- Causal chain intact via `M-V4-GEN-1` parent.

### C6. Silent supersession scan — CLEAN
- v3 completion report has c78 amendment properly disclosed with expected drift `d920c93…` → `b900b0ee…`.
- v2 completion report c71 append `341d5bbaf859c8ca…` matches POR narrative.
- No orphaned SHA references detected in delta scope.

## New findings this stage
None. All checks pass except confirmation of the MODERATE finding already recorded in test 1/7.

## File written
`audits/final/stages/test_2of7.md`

## Findings appended
0 (already recorded in test 1/7)
