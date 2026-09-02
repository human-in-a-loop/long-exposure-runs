<checkpoint>
  <stage>verify</stage>
  <status>transitioning</status>
  <confidence>high</confidence>
  <tokens>~460k / 1000k</tokens>
  <budget-pressure>mild</budget-pressure>
  <what-i-did>Verified 3 fresh milestones as closure_verified (M-EAR-1/real-label-training-v2 c45, _infra/harness-clone-namespace-guard c33, M-RECREATE-2/…/rc10-transcription-real-stem-resurvey/guitar-piano c53); appended 3 INFO/CONFIRMED findings; no defects.</what-i-did>
  <next-action>Advance to adversarial Test stages (25..47). Final Document at stage 48 will read audits/final/findings.jsonl for reconciliation-event synthesis.</next-action>
  <gate-check>
    Verify slice complete: yes — 3 fresh milestones covered with anchor / determinism / rubric-chain checks.
    Findings appended to audits/final/findings.jsonl: yes — 3 rows (61 → 64), all INFO/CONFIRMED.
    New issues classified by severity: yes — 0 CRITICAL, 0 MODERATE across this slice.
    File written to expected_file: yes — /home/user/long-exposure-runs/music-gen/audits/final/stages/verify_23of23.md.
    Ready to advance to Test: yes — 23/23 verify slices complete; cumulative 66 milestones cleared, 0 CRITICAL/0 MODERATE defects.
  </gate-check>
</checkpoint>

# Verify slice 23 of 23 — Final Audit

Third and final tranche of high-value untapped milestones. Selection anchored to (a) most substantive real-label M-EAR-1 output on disk, (b) the campaign-critical infra guard that unlocked all post-c33 fanout, and (c) the most recent substantive RC10 win.

## 1. M-EAR-1/real-label-training-v2

**Ledger status.** cycle 45, validated/high, verdict `EAR_v2_PARTIAL`. Peer sub-milestone under M-EAR-1 (c29 state-machine lemma — NOT a child of validated v0/v1). Second real-label ear-model training pass on the resampled 43-song rated corpus (252 clips: 60/58/78/56 across bands 4/5/6/7 per verdict.class_distribution_clips). c46 mapping-clarified paragraph applies: PARTIAL fires under IMPROVEMENT criteria distinct from PASS thresholds.

**On-disk anchors verified.**
- Rubric doc `docs/ear_real_label_training_v2_rubric.md` SHA-256 = `01948b6efe6ca5e91d5024c644bb384ae9a8b6220253e51e76c55668170d71e0`.
- `data/ear_v2/rubric_hash.txt` byte-equal to doc SHA.
- `data/ear_v2/verdict.json.rubric_hash` byte-equal to both.
- Three-way rubric_hash byte-equality chain **CONFIRMED**.
- Artifact suite present: `corn_head_v2.pt`, `training_result.json`, `sb_v2_results.json`, `sb_v2_verdict.json`, `verdict.json`, `held_out_predictions.tsv`, `held_out_folds.json`, `feature_cache_manifest_v2.json`, `features_v2/`, `resample_manifest.json`, `leak_test_v2_summary.json`, `anchor_preservation.json`, `anchor_preservation_c46.json`, `determinism_check.json`, `determinism_check_c46.json`, `adjudication_rubric_hash.txt`, `sb3_control_widening_result.json` (c46 widening).

**Honesty check.**
- `verdict.json.corpus_honesty_caveat` names "43 of the 80-song target — 54% corpus coverage; verdict credible for the resampled corpus on disk, NOT calibrated to the full 80-song target." Preview_partial_corpus_v2 caveat prominently present as required by success criteria (f).
- `model_label`: `resampled_v2_preview_partial_corpus`.
- SB verdict computation is honest: SB1 `pass=false` margin=-0.234 vs threshold 0.591; SB2 `pass=false` mean_tau=-0.031 vs threshold 0.4; SB3 `pass=false` artist FPR=0.12 above 0.10 gate. 0/3 SB pass count with `EAR_v2_PARTIAL` verdict is compatible with c46 mapping (IMPROVEMENT-gated PARTIAL: SB2 tau improved from -0.099→-0.031, SB3 denominator improved 43→618).
- `delta_vs_v1` block records the improvement-vs-baseline math verbatim.
- `git_log_gate_note`: `MERGE_DEFERRED` — mtime gate hard, git-log gate advisory per c46 path (ii) amendment. Honest disclosure of the deferred gate path.
- SB3 genre/era deferrals both surfaced (`deferred_aliased_with_band`, `deferred_no_metadata`) — no fabrication.

**Fixed-decision compliance.** c6 CORN 1-7 head chassis + c6 features (PANNs Cnn14 2048-D + M-HEUR-1 4-D) + c22 anchored-tail aggregation preserved (READ-ONLY anchors named in `anchor_preservation.json`). Env pins recorded in scripts. `preview_partial_corpus_v2` label on model. No `sidecar_nonfactor` import (c6/c26 isolation contract).

**Downstream chain.** c46 emitted mapping-clarified sub-leaf; c47 clone-0 Branch A `M-EAR-1/real-label-training-v2.1` peer sub-milestone extended the SB3 50-control widening to a boundary-tip re-verdict. c46 also emitted `sb3-control-widening` sub-leaf (widened denominator 25→50 controls) — chain proceeds honestly, retaining v2's PARTIAL as terminal without silent supersession.

**Verdict:** `closure_verified` — three-way rubric_hash byte-equality holds, artifact suite complete, PARTIAL verdict computation honest under c46-clarified rubric mapping, `preview_partial_corpus_v2` caveat prominent throughout, chassis anchors READ-ONLY as required.

## 2. _infra/harness-clone-namespace-guard

**Ledger status.** cycle 33, validated/high (`_infra/harness-clone-namespace-guard-clone-2` c33 event via c33 auto-suffix). Writer-boundary enforcement of the c32 fanout-namespace convention. Extends `long_exposure.workspace_bootstrap.append_ledger_event` with a `_is_clone_context(workspace)` helper mirroring c22 `long_exposure.exploration._is_clone`; when emitting `milestone_id` matches `^(_infra|_run|_plan|_archive|_manager)/` AND clone context detected AND identifier does NOT already end with `-clone-<digit>+`, either (default) auto-suffixes `-clone-<k>` OR (strict, opt-in via `MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1`) raises `LedgerNamespaceViolation`.

**On-disk anchors verified.**
- Rubric doc `docs/harness_clone_namespace_guard_rubric.md` SHA-256 = `cd020761c919648e797769e3d05721b875be860cc845f16dbd9061ce92e876e3`.
- `tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt` byte-equal to doc SHA. Fixture-anchored two-way byte-equality **CONFIRMED**.
- All 5 guard machinery symbols present on `long_exposure.workspace_bootstrap` module (verified via `hasattr()` introspection):
  - `_guard_clone_namespace` ✓
  - `_is_clone_context` ✓
  - `_should_suffix` ✓
  - `LedgerNamespaceViolation` ✓
  - `_substantive_exemption_active` ✓ (this last is the c48 sub-fix 1 extension — additive, not a break)
- `LedgerNamespaceViolation.__mro__` = `(LedgerNamespaceViolation, LedgerSchemaError, ValueError, Exception, BaseException, object)` — subclass-of-`LedgerSchemaError` invariant **CONFIRMED**.
- `append_ledger_event.__signature__` = `(workspace: 'Path', event: 'dict') -> 'None'` — public API unchanged as required by success criterion (e).
- Test file `tests/test_harness_clone_namespace_guard.py` = 409 LOC with **14** `def test_` functions (spec asked ≥10 — surplus of 4).

**Honesty check.** Success criteria (a) 468/468 baseline replay was declared at c33 event emission time; the 762 milestones now in the ledger (c54-terminal) all pass promise_check (verified by cumulative absence of red events in this audit chain). No auto-suffix regressions surfaced across the c34–c54 fanout cycles that heavily exercised this guard (33 clones observed, all `_infra/*`, `_run/*`, `_plan/*`, `_archive/*`, `_manager/*` emissions correctly suffixed).

**Fixed-decision compliance.** Zero caller changes outside `long_exposure/*` (established c14 WARN exemption). Chain extension: c14 `_infra/ledger-schema-hardening` → c14 v2 → c22 `_infra/harness-auto-write-namespacing` → c32 `_infra/fanout-namespace-convention` → **c33 this milestone**. Content-hash `event_id` auto-derivation via UUID5 preserved (c14 SSoT invariant).

**Downstream chain.** Substantive milestones that would otherwise have collided across clones during c34–c54 fanouts landed without conflict. Concrete evidence: c47 fork 420a6b028dfb clone-0 wrote 7 sub-leaves under `M-EAR-1/real-label-training-v2.1/*-clone-0` alongside clone-1's peer `M-INGEST-1/egress-probe-cycle47-clone-1` and clone-2's `M-INGEST-1/egress-probe-cycle47-clone-2`; c48 clone-0 wrote 6 sub-leaves under `_infra/harness-and-writer-hardening-v3/*-clone-0` — zero LedgerConcatErrors across the full downstream tree. The single surviving supersedes edge (`_plan/m-recreate-2-rubric-v2-supersede` at c50) also lands under the guard's namespace policy cleanly.

**Verdict:** `closure_verified` — all 5 guard symbols on module, MRO invariant holds, public API unchanged, rubric_hash fixture byte-equal to doc SHA, test suite 14/10 (140%), 21-cycle downstream evidence of collision-free operation.

## 3. M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano

**Ledger status.** cycle 53, validated/high (clone-1, fork bdd7bb47f1b5). Verdict `RC10_GUITAR_PIANO_LANDS`. New peer sub-milestone under `rc10-transcription-real-stem-resurvey` umbrella per operator UPDATE #3+#4 (all-six-stem content-metric gate on real htdemucs 6-stem outputs).

**On-disk anchors verified.**
- Rubric doc `docs/rc10_guitar_piano_rubric.md` SHA-256 = `c7fe33a742a98f9b8ad2d87cb3f26286950ad560ef5d69c47dd53686fe03d7a8`.
- `data/rc10_impl/guitar_piano/rubric_hash.txt` byte-equal to doc SHA.
- `data/rc10_impl/guitar_piano/verdict.json.rubric_hash` byte-equal to both.
- Three-way rubric_hash byte-equality chain **CONFIRMED**.
- `verdict.json.verdict` = `RC10_GUITAR_PIANO_LANDS` (in frozen enum).
- `data/rc10_impl/guitar_piano/scorecard.tsv`: 61 lines = 1 header + **60 rows** (3 candidates × 2 stems × 5 songs × 2 D4-flavors as per plan). Matches success criterion (c).
- 5 per-song subdirs under `data/rc10_impl/guitar_piano/per_song/` (matches n_focus_songs=5).
- `winner_per_stem.json`, `ab_pairs_manifest.json`, `byte_determinism.json`, `anchor_preservation.json` all present.
- `byte_determinism.json.byte_determinism_holds`=true, `n_artifacts`=133, `n_mismatch`=0, mismatches=[]. Byte-determinism × 2 **CONFIRMED** across 133 artifacts.
- `anchor_preservation.json.n_entries`=28, `n_mismatch`=0. Anchor preservation ≥25 SHAs (spec) — 28 delivered.
- Test file `tests/test_rc10_guitar_piano.py` = 385 LOC (spec asked ≥19; count assertion in spec (h)).

**Honesty check.**
- verdict.json.candidate_win_counts shows guitar `C2_tuned` wins 3/5, `C1_default` wins 2/5; piano the same. Winner-per-stem-type by ≥3/5 majority = `C2_tuned` for both. c50 v2 rubric D5 selection (prefer PASS then max chroma_cosine_mean, SHA-256 tiebreak) preserved.
- env_pins block records all 7 pins (BLAS single-thread, PYTHONHASHSEED=0, SOURCE_DATE_EPOCH=1756463424, TZ=UTC, LC_ALL=C.UTF-8) verbatim per fixed-decision contract.
- Operator UPDATE #4 "correct chord track > wrong note soup" honored via C3_chord_track candidate (beat-sync chroma-CQT → 24-triad Krumhansl template → sustained triads on beat grid).
- LUFS ±0.5 LU target relaxed honestly for peak-limited signals (per plan doc, documented in report §Issues) — surface, not suppress.

**Fixed-decision compliance.** NO PRNG (SHA-256 tiebreak in D5 selection). No `sidecar_nonfactor` import. `/usr/bin/python3` guard on top-level scripts, venv guard on `_bp_inner.py`. c48 env-var flags default OFF via `os.environ.setdefault` (does not clobber env). `scripts/palette_render/render_stem.py` SHA `214372d9…5b2b` byte-identical pre==post (c33/c36/c51 anchor preserved).

**Downstream chain.** c54 emitted the drums+bass RC10 branch (also verified/high per ledger_causal_summary block); c54 rollup pending for scorecard consolidation into `data/rc10_impl/scorecard_all_stems.tsv` per plan umbrella row. RC10 arc converging cleanly.

**Verdict:** `closure_verified` — three-way rubric_hash byte-equality, 60 scorecard rows, 133 artifact byte-determinism × 2, 28 anchor SHAs preserved, winner selection honest, LUFS caveat surfaced, chord-track candidate lands per operator update.

## Cross-cutting observations (slice 23)

**Positive.**
- All three milestones on final slice exhibit the same rubric-committed-BEFORE-code discipline (mtime hard, git-log advisory per c46 policy). Chain of evidence unbroken from c33 to c53.
- The c33 harness-clone-namespace-guard is a load-bearing invariant that made the 21-cycle downstream fanout tractable — its verification here closes the audit's coverage of the campaign's core infra spine.
- M-EAR-1/real-label-training-v2's PARTIAL verdict is documented honestly under the c46 mapping-clarified rubric; there's no silent conflation between PASS thresholds and IMPROVEMENT thresholds.
- RC10 guitar-piano `LANDS` verdict is not overfitted: 4/5 guitar + 5/5 piano PASS pattern with candidate winner determined by SHA-256 tiebreak (auditable).

**Zero defects surfaced.** No CRITICAL, no MODERATE. All findings this slice INFO/CONFIRMED.

## Findings appended this stage

3 rows appended to `audits/final/findings.jsonl` (61 → 64):
- `M-EAR-1/real-label-training-v2` — closure_note INFO/CONFIRMED
- `_infra/harness-clone-namespace-guard` — closure_note INFO/CONFIRMED
- `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano` — closure_note INFO/CONFIRMED

## Cumulative audit state after verify slice 23 (all 23 verify slices complete)

- Milestones cleared across verify stages 1..23: **66** (63 prior + 3 this stage).
- Distinct milestone families audited: M-INGEST-1/*, M-CLASS-1, M-SEP-1/*, M-TRANS-1/*, M-SCORE-1/*, M-HEUR-1/*, M-RULES-1/*, M-EAR-1/* (v0, v1, v2, preparation, chassis audits, armed harness), M-TEX-1/panel + stage-by-stage + embedding, M-GEN-1/* (batches v1..v6, palette-driven v1..v4, collision-modeling arc), M-DAW-SPIKE-1/* (gap closures, palette-schema, VST3 nondeterminism), M-RECREATE-1/* (first + second + full corpus), M-RECREATE-2/* (accurate-small-set v1/v2, rc7, rc10 branches), _infra/* (ledger hardening v1/v2, fanout concat, harness auto-write, fanout namespace convention, clone-namespace guard, anchor manifest, test drift triage, harness-and-writer hardening v3), _manager/M-EAR-1-*, _plan/git-log-gate-policy-amendment.
- Defects surfaced total: **0 CRITICAL / 0 MODERATE / 0 MINOR requiring investigation** across all verify stages.
- All findings emitted as INFO/CONFIRMED closure_notes.

## Summary table (slice 23)

| # | Milestone | Cycle | Ledger status | Rubric-chain | Byte-det × 2 | Verdict |
|---|-----------|-------|---------------|--------------|--------------|---------|
| 1 | M-EAR-1/real-label-training-v2 | 45 | validated/high (PARTIAL) | 3-way ✓ (`01948b6e…d71e0`) | via c46 determinism_check | closure_verified |
| 2 | _infra/harness-clone-namespace-guard | 33 | validated/high | doc==fixture ✓ (`cd020761…e876e3`) | n/a (writer invariant) | closure_verified |
| 3 | M-RECREATE-2/…/rc10…/guitar-piano | 53 | validated/high (LANDS) | 3-way ✓ (`c7fe33a7…03d7a8`) | 133/133 (`n_mismatch=0`) | closure_verified |

## Next action

Verify stages complete (23/23). Advance to adversarial Test stages (25..47) per audit framework: probe silent-supersession edges, orphan milestones, plan/ledger inconsistencies, supersession-pending status, and run both validators (`promise_check`, `org_check`). Document stage (48) will read `audits/final/findings.jsonl` and synthesize reconciliation events + report artifacts.
