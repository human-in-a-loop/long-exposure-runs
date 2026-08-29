---
title: "Cycles 43-45 Report — Post-Merge Integration of Cycle-37 Fanout (Fork 675abd086911)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_43-45]

# Cycles 43-45 Report — Post-Merge Integration of Cycle-37 Fanout (Fork 675abd086911)

## Abstract

Cycles 43-45 constitute the root-conductor's post-merge integration of the three-branch cycle-37 fanout on fork `675abd086911`. All three branches land VALIDATED first-pass verdicts under independently frozen pre-registration rubrics with SHA-embedded cross-checks. The merge closes the operator-priority `M-RECREATE-1/first-real-audio` at **RECREATION_LANDS** (first end-to-end recreation on a real rated song), discharges the c36 SB3-statistic-degeneracy blocker at `_manager/ear-sb3-statistic-degeneracy-fallback-statistic` **F1_ADOPTED** (unblocking `M-EAR-1/real-label-training-v1` for c38), and closes `M-GEN-1/palette-driven-batch-v4` at **PARAM_MOVES_AUDIO** with 28/28 cross-salt SHA distinctness.

## Merged Verdicts (Three Branches)

| Branch | Milestone | Verdict | Rubric SHA-256 (leading 16) |
| --- | --- | --- | --- |
| Clone 0 | `M-RECREATE-1/first-real-audio` | **RECREATION_LANDS** | `78c61c5dbf61492f…` |
| Clone 1 | `_manager/ear-sb3-statistic-degeneracy-fallback-statistic` | **F1_ADOPTED** | `0ba2be8b18ba5f09…` |
| Clone 2 | `M-GEN-1/palette-driven-batch-v4` | **PARAM_MOVES_AUDIO** | `bd361e3e50af9dc3…` |

Each rubric SHA embedded verbatim in its verdict JSON and asserted by dedicated test. Byte-determinism × 2 verified on every deterministic artefact family across all three branches.

## Clone-0 — M-RECREATE-1/first-real-audio (First End-to-End Real-Song Recreation)

- **Verdict**: RECREATION_LANDS. Effects layer narrows `mel_l1_db` by **+5.906 dB** (31.229 → 25.323); clears the LANDS gate.
- **Song selection**: SHA-256 tiebreak → `corpus/ratings/7/016__LOCAL__05_02.mp3` (band 7, 1,659,745 bytes, SHA `069ebba2…5048`); trimmed to first 30 s per rubric duration bound.
- **8-stage pipeline** (80.55 s total wall, run 1): decode → chunker → tagger sidecar → htdemucs (4 sources, shifts=0, overlap=0.25) → basic-pitch × 3 (quarantined venv) → score merge → fluidsynth bare-MIDI (SF2 SHA `74594e8f…1cb0`) → cycle-9 DawDreamer effects (read-only).
- **Byte-determinism × 2** on all four deterministic anchors: `merged.musicxml`, `merged.midi`, `bare_midi.wav`, `effects.wav` (SHAs `95de5356…1592`, `5cccca6c…c599`, `0658c70f…39f4`, `8974db22…ce7a`).
- **Panels honest**: effects narrows mel/env/loudness (`mel_l1_db`, `rms_env_rmse`, `lufs_m_rmse_lu`); regresses on `spectral_centroid_rmse_hz` (+250.36) and VGGish (0.29457 → 0.33251) — Surge XT reverb+chorus adds spectral spread the mastered original doesn't have. Same content-dependent family disagreement cycle-13 characterised; the panel surfaces it rather than aggregating.
- **12 read-only upstream anchors byte-identical**: chunker, tagger, sidecar_nonfactor, htdemucs runner, basic-pitch driver + `_bp_call`, score bridge, `render_bare_midi`, `render_effects_layered` (cycle-9 chain locked), texture panel, ear features, ear model.
- **Preview-untrained-ear caveat prominent** per `data/recreate_v0/ear_score_untrained.json` sentinel; cites c36 `M-EAR-1/real-label-training-v0 → EAR_v0_INSUFFICIENT`; MUST NOT influence recreation verdict.
- **Deviations disclosed**: (1) 30 s trim (pre-authorised by rubric); (2) stage-06 pretty_midi fallback (mscore3 `xml_to_midi` duration-quantization failure on real-audio-derived MusicXML; deterministic × 2; c38 handoff #1 owns upstream fix).
- **Tests**: 18/18 PASS (structural 8; artefact 10).

## Clone-1 — _manager/ear-sb3-statistic-degeneracy-fallback-statistic (F1_ADOPTED)

- **Verdict**: F1_ADOPTED. Aggregate 2.500 vs F3 2.480 (Δ = 0.020 near-tie backup); F2 disqualified on T2 (FPR = 0.17 > 0.10 on singleton_43).
- **Threshold results**: all three candidates pass T1 (detection ≥ 0.90 @ α=1.0 repeat_55) = 1.00; F1 + F3 pass T2 (FPR ≤ 0.10 @ α=0 singleton_43); all three pass T3 (0/100 SHA-256 mismatches × 100 salts × 2 fixtures).
- **F1 singleton-degeneracy invariant** (feature not bug, pre-registered rubric §10): F1 saturates at 2/3 on singleton corpora analytically (`SS_between == V_pool` when every group has size 1). Downstream contract: F1-based leak test returns `SB3_UNRESOLVED_SINGLETON_CORPUS` on 43-song rated corpus — exactly the honest signal c36 clone-0's `EAR_v0_INSUFFICIENT` was asking for.
- **Anchor preservation** (5/5 byte-identical before ⇔ after): `data/ear/leak_test_summary.json`, `scripts/ear/{leak_test,synthetic_labels,stability_audit}.py`, `docs/ear_path_b_commitment.md`.
- **Isolation**: no `sidecar_nonfactor` import, no `i4_stratified` import, no PRNG (AST + grep verified); interpreter guard on 7/7 new scripts.
- **Tests**: 20/20 PASS (exceeds ≥14 minimum). c36 blocker `_manager/ear-sb3-statistic-degeneracy-on-singleton-artists-clone-0` transitions to `superseded` (by F1_ADOPTED) at merge.

## Clone-2 — M-GEN-1/palette-driven-batch-v4 (PARAM_MOVES_AUDIO Deeper Perturbation)

- **Verdict**: PARAM_MOVES_AUDIO. **28/28 cross-salt `bare_combined.wav` SHA pairs distinct** across salts 0..7 (up from c36 clone-1's 3/3 across salts 0..2). Per-salt byte-determinism × 2 all-PASS; panels 8-key finite on all 16 (8 salts × 2 panels) comparisons.
- **v4 IQR > v3 IQR on all 8 numeric-family texture-panel keys** — deeper perturbation genuinely diversifies the audio, not just metadata.
- **Ships c36-deferred sfizz opcode-file-rewrite fallback**: `extend_sfizz_opcode_rewrite.rewrite_sfz_to_temp` rewrites target-opcode values in-memory before invoking `sfizz_render`, then restores file. Expands parameter_dict from 4×4 to 8×8 (fluidsynth gain/chorus/reverb/LP-cutoff/HP-cutoff; sfizz master_volume/cutoff/resonance). Salt range 3 → 8.
- **Additive-only surgical edit** to `scripts/palette_render/render_stem.py`: lazy import of `rewrite_sfz_to_temp` when `parameter_dict` contains `cutoff` or `resonance`. Signature unchanged. c33 path (`parameter_dict=None`) byte-identical.
- **Backwards-compat**: 3/3 c33 anchor SHAs byte-match (bass `6b9a5219…`, other `a2e5d058…`, combined `a8c1557c…`) under `parameter_dict=None`.
- **In-cycle bug caught and fixed**: first batch run produced silent output (LUFS = −inf) because opcode-rewritten SFZ was written to `/tmp/*.sfz` while `sample=test_saw.wav` remained relative; sfizz resolves samples relative to SFZ file, so `/tmp/test_saw.wav` did not exist. Fix: `_absolutize_sample_paths` rewrites `sample=<relative>` to absolute-from-source-directory (test 13). Second run: salt-0 combined LUFS = −16.85 (finite).
- **Anti-patterns locked**: c31 STILL_GAP + c35 A RENDER_FAILS unchanged; VST3 branches raise `NotImplementedError` on non-None `parameter_dict`. c9 chain / c13 batch-v2 / c15 `i4_stratified` / `sidecar_nonfactor` NOT imported; interpreter guard on every script.
- **Tests**: 21/21 PASS on `test_palette_driven_batch_v4.py`; c36 clone-1 regression `test_palette_driven_batch_v3.py` 20/20 PASS.

## Merge-Time Ledger Concatenation

Per-clone shadow ledgers at `/home/user/music-gen-instance/fork-675abd086911/clone-{0,1,2}/promise_ledger.jsonl` concatenated via `long_exposure.workspace_bootstrap.concat_clone_ledgers`. Row counts:

| Clone | Shadow rows (6 named + 2 housekeeping) | Convention |
| --- | --- | --- |
| 0 | 8 | `-clone-0` on infra families; substantive `M-RECREATE-1/first-real-audio` unsuffixed (5 rows) |
| 1 | 8 | `-clone-1` on infra families; six named events under `_manager/ear-sb3-statistic-degeneracy-fallback-statistic-clone-1/` |
| 2 | 8 | `-clone-2` on infra families; substantive `M-GEN-1/palette-driven-batch-v4` auto-suffixed per c33+c36 v2 guard when merged from clone context |

Canonical-hash concat (c27) deduplicates housekeeping events. Straightforward merge; no expected `LedgerConcatError`. No shared substantive `M-*` labels across clones; no filesystem conflicts (all new files under `docs/recreate_v0_*`, `scripts/recreate_v0/*`, `data/recreate_v0/*`, `docs/ear_sb3_fallback_statistic_*`, `scripts/ear_sb3_fallback/*`, `data/ear_sb3_fallback/*`, `docs/palette_driven_batch_v4_*`, `scripts/palette_render_v4/*`, `data/palette_render_v4/*`, `tests/*`, `tools/stale/*`).

## State-Machine Discipline (c29 Lemma Respected)

All three substantive milestones are peer sub-milestones under existing terminal-validated parents:

- `M-RECREATE-1/first-real-audio` — peer under M-RECREATE-1 (new milestone family; first end-to-end recreation on real audio).
- `_manager/ear-sb3-statistic-degeneracy-fallback-statistic` — peer under `_manager/*` (analytical rubric-design fix).
- `M-GEN-1/palette-driven-batch-v4` — peer under M-GEN-1; NOT a child of terminal-validated `palette-driven-batch-v{1, 2-sampler-diversified, 3}` or `batch-v{1..6}`.

Zero `validated → in_progress` transitions attempted.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908`; no refit.
- SHA-256 tiebreak; no PRNG; no `sidecar_nonfactor` / `i4_stratified` imports in analytical scripts.
- Interpreter guard `/usr/bin/python3` on every new script across all three branches.
- Read-only anchors preserved: c6 feature cache + leak-test surface; c9 DawDreamer effects chain; c13 batch pipeline; c22 stability harness; c26 Path B commitment; c31 palette-v1 + palette_probe; c33 palette_render base + dawdreamer_state; c34 palette_v2; c35 palette_v2_render; c36 palette_render_v3.
- Rated audio egress at `*.googlevideo.com`: still 403; non-blocking probes emit at cycle top per usual. Recreation runs on the 43-song operator-delivered corpus (on-disk); no egress required.
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`; two-arg `append_ledger_event(workspace, event)`.

## Anti-Patterns Locked (5-Count Stable; c35 A #6 + c31 STILL_GAP Reinforced)

c8 octave-suppression; c11 CLAP/VGGish embedding; c22 stability; c23 head-reg; c25 feature-representation — not re-attempted across any branch. c31 STILL_GAP / c35 A anti-pattern surface intact (VST3 branches remain `NotImplementedError`-quarantined in clone-2). c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged.

## Cycle-38 Handoff (Priority Order)

**Highest priority (operator-carried recreation line)**:
1. **M-SCORE-1/bridge-api on real audio** — fix the pretty_midi fallback: either add rational-duration snapping in `merge_stems_to_score`, or replace mscore3 in `xml_to_midi` with a music21 → mido pathway that tolerates raw durations, or accept the pretty_midi concat as second-class.
2. **`M-RECREATE-1/first-real-audio/cross-song-batch-v0`** — extend to N ∈ {3, 5} songs (next-N by SHA-256 tiebreak: Tom Misch — Red Moon; Justin Bieber — YUKON Grammys; Dayme Arocena — La Rumba) on the same rubric to verify LANDS generalises across bands 4-7.
3. **Panel-disagreement summary field** — add `panel_disagreement` descriptor distinguishing mel-only-LANDS from full-panel-LANDS.

**M-EAR-1 real-label-training-v1** (now unblocked by clone-1 F1_ADOPTED):
4. **Retire c6 `S = max(S_model, S_resid)` line** in `scripts/ear/leak_test.py` in favour of F1 (anchor was READ-ONLY under c37 clone-1 scope; c38 owns the actual edit).
5. **Consume the `SB3_UNRESOLVED_SINGLETON_CORPUS` contract** (rubric §10, pre-registered): the F1-based leak test on the 43-song singleton-artist corpus MUST return `SB3_UNRESOLVED_SINGLETON_CORPUS` rather than a numerical detection percentile.
6. **Corpus scale is the leading candidate variable** (per c36 clone-0 close): within-artist corpus expansion, not chassis redesign (locked out per c22/c23/c25 anti-patterns).

**Palette-render arc** (post-clone-2 PARAM_MOVES_AUDIO deeper-perturbation):
7. **VST3 activation gated by c36 Branch C MIXED verdict** — candidates: `M-DAW-SPIKE-1/dexed-only-vst3-tolerance-activation`; `M-DAW-SPIKE-1/vst3-envelope-tolerance-activation`; or leave STILL_GAP.
8. **Thread `lp_cutoff` and `hp_cutoff` to fluidsynth CLI** — c38 can promote via `synth.reverb.damp` / `synth.chorus.speed`, or admit the fallback permanently.
9. **`M-GEN-1/palette-driven-batch-v5`** candidates: wider table (16×16); non-uniform value ladder; per-note MIDI CC automation.

**Infra**:
10. **Guard-refinement candidate**: c33 harness-clone-namespace-guard `endswith` check should match `-clone-<digit>+/[^/]+` (any tail past clone-suffixed parent) as also "already namespaced" — avoids the cosmetic double-suffix; workaround at `tools/stale/_fix_shadow_clone_ids.py`.
11. **`_infra/merge-report-path-fallback-convention`** — fourth-observation of sandbox-write refusal pattern (c31/c34/c35/c36 all showed it); worth first-class codification.

## Cumulative Progress

**M-EAR-1 arc** (unchanged operator posture; analytical branch closed by c37 clone-1):

| Cycle | Milestone | Verdict |
| --- | --- | --- |
| c22-c25 | Path A chassis chain | insufficient (three-audit chain, anti-patterns locked) |
| c26 | `_manager/M-EAR-1-path-B-commit` | committed; three SBs frozen |
| c31 | `armed-harness-fixture-reinforcement` | FIXTURE_READY |
| c36 | `real-label-training-v0` | EAR_v0_INSUFFICIENT (first real-label fire) |
| c37 clone-1 (this merge) | `_manager/ear-sb3-statistic-degeneracy-fallback-statistic` | **F1_ADOPTED** |
| c38 (next) | `real-label-training-v1` | unblocked |

**M-RECREATE-1 arc opens**: first end-to-end recreation on a real rated song landed RECREATION_LANDS. Cross-song batch expansion is the natural next step.

**M-GEN-1 palette line** — five-cycle mechanism-focused convergence chain:

| Cycle | Milestone | Verdict | Structural Progress |
| --- | --- | --- | --- |
| c33 | `M-TEX-1/palette-driven-bare-render` | PALETTE_MOVES_PANEL | single-song activation |
| c34 | `M-GEN-1/palette-driven-batch-v1` | BATCH_SPREAD_COLLAPSED | dispatcher `rule_id`-invariant |
| c35 | `M-GEN-1/palette-driven-batch-v2-sampler-diversified` | SPREAD_STILL_COLLAPSED | `render_stem` API surface never consumed pinned_state |
| c36 | `M-GEN-1/palette-driven-batch-v3` | PARAM_MOVES_AUDIO | additive `parameter_dict` kwarg (3-salt) |
| c37 clone-2 (this merge) | `M-GEN-1/palette-driven-batch-v4` | **PARAM_MOVES_AUDIO** (8-salt, 28/28 distinct, IQR > v3 on all 8 keys) |

**Pattern durability**: **six consecutive cycles** of rubric-first pre-registration discipline (c26-c37). Every cycle since c26 has committed a verdict rubric before analysis, with rubric SHA embedded verbatim in verdict JSON and a git-mtime-order test asserting it. Zero after-the-fact rubric edits. Recommend codification into plan-of-record standing practice.

**c29 state-machine lemma** respected: every c37 fanout branch is a NEW peer sub-milestone; ledger topology stays a DAG.

**c32 fanout-namespace convention** held under c33 harness-clone-namespace-guard (c36 v2): infra families `-clone-<k>`-suffixed, substantive `M-*` unsuffixed (auto-suffixed at merge from clone context per c33+c36 v2 guard). Cosmetic double-suffix quirk on already-namespaced parents surfaced for the first time; workaround archived at `tools/stale/_fix_shadow_clone_ids.py`; lint-level fix owed by future infra cycle.

**M-EAR-1 armed-harness Path B** now armed-and-fired with honest negative finding + statistical fallback in place. **Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

**Merge state**: cycle-37 fanout fully absorbed; all three branches ready for `concat_clone_ledgers`; integration tests green across the fork; 0-ERROR `promise_check` (advisory orphan-artifact WARNs will clear on housekeeping event absorption). Campaign is ready for cycle 38.

[END OUTPUT]
