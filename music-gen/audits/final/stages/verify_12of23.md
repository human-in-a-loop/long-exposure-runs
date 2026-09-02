# Final audit — verify 12 of 23 (stage 13/48)

Cycle: 12 (final-audit local numbering)
Slices verified this stage: 3 (all closures HOLD)
Findings appended: 4 (3 `closure_verified` severity `none` + 1 `verdict_schema_drift` MODERATE)

## Slice A — M-EAR-1/real-label-training-v2.1 (c47 Branch A)

- Rubric doc: `docs/ear_real_label_training_v2p1_rubric.md`
- Rubric SHA-256: `2920875671ea98b1…cff2abafa`
- 3-way byte-equality chain: PASS
  - doc SHA `2920875671ea98b1…cff2abafa`
  - `data/ear_v2p1/rubric_hash.txt` first field byte-equal
  - `verdict.json.rubric_hash` byte-equal
- Verdict enum ∈ {EAR_v2p1_STABLE_FPR_PASS, EAR_v2p1_BOUNDARY_TIP, EAR_v2p1_FPR_STILL_OVERSHOOT}
- Verdict: **`EAR_v2p1_STABLE_FPR_PASS`**; `byte_determinism_x2=True`; `corpus_caveat=preview_partial_corpus_v2p1`
- SB1/SB2 status: `FAIL_unchanged_from_c45` (expected per c47 brief — v2.1 tests only SB3 stability, does NOT re-verdict SB1/SB2 which remain FAIL under c26 thresholds)
- Byte-determinism × 2:
  - Training (`training_determinism_check.json`): `corn_head_v2p1.pt` run1==run2 sha `43cd7045ac6835ba…`; `training_result_v2p1.json` run1==run2 sha `a030ef1611a1754e…`. Both `byte_det_x2=True`.
  - SB3 (`sb3_determinism_check.json`): `sb3_50ctl_verdict_v2p1.json` run1==run2 sha `c5add489eace0a6d…`. `byte_det_x2=True`.
- Anchor preservation (`anchor_preservation_v2p1.json`): `drift=[]`, `n_anchors=34`, milestone tag `M-EAR-1/real-label-training-v2.1/anchor-preservation-verified`. All 34 upstream anchors byte-identical pre==post.
- Test suite `tests/test_ear_v2p1_real_label_training.py`: 18 cases (`_t01`..`_t18`); plain-assert style; `/usr/bin/python3` invocation guard.
- **Closure holds.**

## Slice B — M-DAW-SPIKE-1/palette-instrument-determinism (c31 Branch A)

- Rubric doc: `docs/palette_instrument_determinism_rubric.md`
- Rubric SHA-256: `75daa068aa804351…4ac7c96`
- 2-way byte-equality chain: PASS
  - doc SHA `75daa068aa804351…4ac7c96`
  - `data/palette_probe/rubric_hash.txt` byte-equal
  - NOTE: this milestone uses `data/palette_probe/instrument_determinism.tsv` as the verdict artifact (per-instrument row-level verdicts), NOT a top-level `verdict.json`. This is faithful to the rubric doc — the milestone's frozen contract calls for per-instrument verdicts in the TSV row `verdict` column.
- Per-instrument verdicts (from `instrument_determinism.tsv`):
  - `surge_xt`: `STILL_GAP` — run1_wav != run2_wav (`fe80fc17…`/`443ca252…`) but state_sha identical after refinement attempt (get_state returned empty; c33 clone-2 later characterized this as VST3-internal nondeterminism, cf. M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization).
  - `dexed`: `STILL_GAP` — same failure mode (run1_wav `05c48e00…` vs run2_wav `3ac46320…`; state_sha identical).
  - `sfizz`: `GREEN` — run1_wav == run2_wav (`4f9735d9459d06df…`); state_sha equal; no refinement needed.
- Sub-artifacts: `per_instrument/{surge_xt,dexed,sfizz}/{pinned_state.json,run{1,2}_wav_sha,run{1,2}_state_sha}` present; refinement.json only for the two STILL_GAP branches.
- Test suite `tests/test_palette_instrument_determinism.py`: 9 cases (rubric brief called for ≥9; matches lower bound).
- **Closure holds.** STILL_GAP verdicts are first-class negative findings honestly reported per the frozen rubric; downstream c35/c36 branches formally accepted the VST3 nondeterminism finding.
- Findings noted below:
  - **MODERATE / verdict_schema_drift** — schema drift from peer-slice convention: no top-level `verdict.json` (verdict is in TSV row `verdict` column). Faithful to this rubric's own contract but breaks cross-slice audit-tool convention (a top-level verdict.json is expected by the standard 3-way rubric-hash chain check). Not fixed — modifying it would break the rubric's own documented artifact set. Logged for pattern-tracking only.

## Slice C — M-GEN-1/palette-driven-batch-v4 (c37 clone-2)

- Rubric doc: `docs/palette_driven_batch_v4_rubric.md`
- Rubric SHA-256: `bd361e3e50af9dc3…8d9be38cf`
- 3-way byte-equality chain: PASS
  - doc SHA `bd361e3e50af9dc3…8d9be38cf`
  - `data/palette_render_v4/rubric_hash.txt` byte-equal
  - `verdict.json.rubric_hash` byte-equal
- Verdict enum ∈ {PARAM_MOVES_AUDIO, PARAM_NEUTRAL, RENDER_FAILS}
- Verdict: **`PARAM_MOVES_AUDIO`**
  - `cross_salt_distinct_count = 28` / `cross_salt_pair_count = 28` — every one of C(8,2)=28 cross-salt bare_combined SHA pairs distinct
  - `backwards_compat_pass = True` (3/3 c33 anchor SHAs match under `parameter_dict=None`: bass `6b9a5219…0540280`, other `a2e5d058…d10f621`, combined `a8c1557c…c212ba794`)
  - `per_salt_determinism`: 8 salts × per-salt byte-det × 2 = 8 True
  - `anchor_unchanged_except_render_stem_edit = True`
- Anchor preservation (`anchor_preservation.json`): 45 pre / 45 post entries; only intentional target is `scripts/palette_render/render_stem.py` (documented v4 growth of sfizz opcode-rewrite fallback); pre/post SHA both `3955bff8e6966f42…3fc0ade2b0` — meaning the render_stem.py edit itself was already merged before this run's snapshot window, and the pre-run snapshot captured the post-edit state. The additive-kwargs contract remains preserved via the passing backwards_compat_check.
- Test suite `tests/test_palette_driven_batch_v4.py`: 21 cases.
- **Closure holds.**

## Summary table

| Slice | Rubric-hash chain | Verdict           | Byte-det × 2 | Anchors | Tests | Verdict holds |
|-------|-------------------|-------------------|--------------|---------|-------|---------------|
| A: ear v2.1 | 3-way PASS   | EAR_v2p1_STABLE_FPR_PASS | PASS (train + SB3) | 34/34 unchanged | 18 | ✅ |
| B: palette-instrument-det | 2-way PASS (per rubric contract) | 3× per-inst: 2 STILL_GAP + 1 GREEN | Split: sfizz PASS; surge_xt/dexed WAV nondeterministic (verdict is STILL_GAP, honestly) | n/a | 9 | ✅ (negative findings first-class) |
| C: palette v4 | 3-way PASS | PARAM_MOVES_AUDIO | PASS (8/8 salts) + backwards-compat 3/3 | 45/45 (1 intentional target self-documented) | 21 | ✅ |

## Findings appended this stage (4)

1. **closure_verified / none** — Slice A `M-EAR-1/real-label-training-v2.1` verified: EAR_v2p1_STABLE_FPR_PASS with 3-way rubric chain PASS, byte-det × 2 across training + SB3, 34 anchors unchanged, 18-case suite.
2. **closure_verified / none** — Slice B `M-DAW-SPIKE-1/palette-instrument-determinism` verified: per-instrument TSV row verdicts hold (sfizz GREEN, surge_xt/dexed STILL_GAP as honest negative findings); rubric-hash chain PASS to the artifact set the rubric names.
3. **verdict_schema_drift / MODERATE** — Slice B uses TSV per-row `verdict` instead of the peer `verdict.json` convention; faithful to the rubric doc but breaks cross-slice audit-tool convention; not fixable without breaking the milestone's own frozen artifact contract.
4. **closure_verified / none** — Slice C `M-GEN-1/palette-driven-batch-v4` verified: PARAM_MOVES_AUDIO with 3-way rubric chain PASS, 28/28 cross-salt distinct, 3/3 c33 backwards-compat SHAs match, per-salt byte-det × 2 PASS on all 8 salts, anchor preservation clean (1 documented intentional target), 21-case suite.

Cumulative findings after this stage: 38 + 4 = **42** rows in `audits/final/findings.jsonl`.
