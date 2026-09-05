---
title: "Music-Gen v4 — Cycles 35-37"
date: "2026-09-05"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v4 — Cycles 35-37

## Abstract

Cycles 35-37 carried the campaign from the discipline-reset state established in the prior range into the operational-hygiene layer required to reopen substantive non-Chicken-Grease bass work under an operator-mandated procedure. The range delivered one canonical infrastructure landing, one substantive negative finding, and honest deferral of three recommended tracks. Cycle 35 opened stage-2 fine-fit sweeps for the two below-floor non-CG bass candidates (Wonderful It Is at embedding distance 0.3055 and Disco A at 0.2443) under the legacy per-sweep-render-batch pattern; Cycle 36 attempted to land the emitter that turns stage-2 leaderboards into pinned profiles + verdicts + replay proofs but the emitter (`_emit_c26_bass_profiles.py`) was authored and never fired to completion — WIG produced a 216-row stage-2 leaderboard plus an operator-pruned tombstone but no `bass.json` / `bass_family_verdict.json` / `bass.replay_proof.json`, and Disco A's stage-2 sweep was interrupted before completion; Cycle 37 responded on two tracks under the operator-mandated procedure fix. Track A landed the canonical sweep-hygiene module `scripts/sound_match/_sweep_hygiene_c27.py` (SHA `771ff42b768d9c44…`, 10,657 bytes) carrying a `RunningTopK` per-candidate render→score→delete pattern, a disk-fullness guard (prune at 85%, abort at 90% per FD-1), and a stale-audio pruner; test suite landed 10/10 PASS (against a ≥6 gate) with the operator-mandated prune/abort thresholds asserted explicitly. Track B landed a substantive negative-finding verification at `data/v4/c27_track_b_c26_landing_verification.json` (SHA `f2eb5cc4582a2666…`) with verdict `C26_TRACK_A_LANDING_INCOMPLETE`, no `supersedes_path`, honoring FD-1 minimal intervention. Tracks C (Rome + Peach Dream stage-2), D (WIG + Disco A drums stage-1), and E (completion-report second pass) were deferred within brief allowance. Independent audit returned **VALIDATED** with zero CRITICAL findings, two MODERATE observations (driver integration deferred to the next cycle as an operational gate; c26 emitter did not fire, retroactively confirming the prior audit's CONTINUE verdict), and two MINOR observations (test coverage exceeded gate; worker's independent-audit-surface disclosure was exemplary). All sixteen spot-checked read-only anchors held byte-identical pre-vs-post, the operator-authority escalation `_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy` remained unchanged with `blocked_on_operator=true`, and no `SF2_CONFIRMED` verdicts landed anywhere on disk. `M-V4-SHOWCASE-1` status is unchanged (`LANDS_pending_operator`; the CG A/B mix WAV holds SHA `6e13e0075c5d8116…` byte-identical). The campaign moved from "verdict-declaration discipline restored" to "verdict-declaration discipline restored + operational-hygiene canonicalized + c28 gated on six-driver integration before any next sweep launches."

## Introduction

The Music-Gen v4 closure campaign is driving itself through seven strictly-ordered milestones toward a clean close. Cycles 35-37 sit inside `M-V4-PROFILES-1` — pinned instrument profiles for the five focus songs — and specifically inside its non-Chicken-Grease continuation. The Chicken Grease cells have been terminal since earlier work; the non-CG portion consists of four songs (Wonderful It Is, Rome, Disco A, Peach Dream) whose stage-1 sweeps had been landed and reclassified under corrected distance semantics in the prior range: Rome and Peach Dream `SF2_RULED_OUT` (embedding distances 0.5145 and 0.4437, above the retained 0.40 upper-bound floor), WIG and Disco A `STILL_INDETERMINATE` (0.3055 and 0.2443, below the floor and therefore eligible for `CONFIRMED` only under operator authority). An operator-authority escalation was open on the non-CG bass acceptance policy with three named options and per-option invariant-compliance analysis; that escalation remains `blocked_on_operator=true` throughout this range.

An additional cross-cutting concern shaped Cycle 37: an operator directive tightening sweep-storage hygiene ("effective immediately") required per-candidate render→score→delete with an explicit disk-fullness guard. The prior batch-render pattern had contributed to the Cycle 36 interruption of Disco A's stage-2 sweep — approximately 166 unscored render subdirectories were left behind, which the Cycle 37 df-guard's first invocation will prune by age gate.

## Approach

**Cycle 35 (stage-2 sweep launch, below-floor bass).** Under the extended `fine_fit_sf2_v2.py` driver with additive `--song-sha16`, `--merged-mid-path`, and `--reference-stem-path` keyword arguments, launched stage-2 fine fits for WIG bass (0.3055, below-floor, `STILL_INDETERMINATE`) and Disco A bass (0.2443, below-floor, `STILL_INDETERMINATE`) over a stage-1-top-5 × gain × reverb × post grid. Sweep-storage hygiene was applied under the legacy per-run policy (`--score-and-delete --keep-top 3 --max-audio-mb 500 --disk-abort-pct 90.0`); detached launch (`nohup+setsid+logfile`) per policy. Rome and Peach Dream were not run — they land `SF2_RULED_OUT` under corrected distance semantics from the prior range.

**Cycle 36 (emitter attempt; interruption).** Attempted to land the emitter `_emit_c26_bass_profiles.py` that turns per-song stage-2 leaderboards into the standard triple of `bass.json` (pinned profile), `bass_family_verdict.json` (verdict enum with proper supersession semantics), and `bass.replay_proof.json` (per-song sf2 replay proof per FD-16(c)). The emitter was authored but never fired to completion. WIG produced its 216-row stage-2 leaderboard plus an operator-pruned tombstone but none of the three emitted artifacts; Disco A's stage-2 sweep was interrupted before completion, leaving no leaderboard and approximately 166 unscored render subdirectories. Cycle 36's rollup event (`_run/cycle_26_closed`) contained ambitious language describing intended state rather than actually-delivered artifacts — a factual drift caught in the next cycle.

**Cycle 37 (canonical hygiene + honest verification).** Two mandatory tracks and three recommended tracks. Track A landed the canonical hygiene module and its POR one-liner verbatim. Track B verified that the Cycle 36 emitter had not fired to completion and published an honest `C26_TRACK_A_LANDING_INCOMPLETE` verification row as a *peer* action-required event rather than superseding the Cycle 36 rollup — honoring FD-1 minimal intervention and preserving Cycle 36's rollup as historical record of intent that predated delivery. Tracks C (Rome + PD stage-2), D (WIG + Disco A drums stage-1), and E (completion report second pass) were deferred within the brief's wall-time allowance because no new sweeps could launch until the canonical hygiene module was integrated into the six sweep-driver anchors.

**Discipline guards asserted for the range.** No `SF2_CONFIRMED` verdicts anywhere on disk (absolute prohibition until operator resolves the acceptance-policy escalation). No unilateral scope-extension of the c9 CG-bass composite-relative WINNER precedent. All read-only anchors preserved byte-identical. Canonical 7-key `env_pin_sha256=2ac444c3…922ca` on every new artifact. `/usr/bin/python3` interpreter guard on all new scripts. No PRNG, no `sidecar_nonfactor` imports, no `--verify-det` bypass, no VST3 state APIs. No wait-on-operator memo (banned per operator directive 2026-09-03 part 2).

## Findings

### Canonical sweep-hygiene module landed (Track A)

`scripts/sound_match/_sweep_hygiene_c27.py` (SHA `771ff42b768d9c44…`, 10,657 bytes) is the canonical module carrying the operator-mandated procedure fix. It provides a `RunningTopK` container that maintains the top-k candidates by score under a deterministic SHA-256 tiebreak, holding on to only their audio while every non-top-k candidate's audio is deleted immediately after scoring. A disk-fullness guard prunes at 85% full and aborts at 90% full per FD-1. A stale-audio pruner sweeps age-gated (older than 60 seconds) unscored render subdirectories and will, on its first invocation in the next cycle's sweep, clean up the approximately 166 subdirectories left behind by the Cycle 36 Disco A interruption.

The POR one-liner landed verbatim matching the brief instruction exactly. The adoption plan `docs/sweep_hygiene_c27_driver_adoption_plan.md` (SHA `37203b8d60594fd0…`) codifies the six-step integration shape (additive `--score-and-delete-per-candidate` flag on-by-default, `--legacy-batch-render` opt-out for regression), a regression-test gate per driver (backward-compat SHA match on CG), and SHA-drift disclosure per driver under invariant (d).

Test suite: 10/10 PASS against the ≥6 gate, with the operator-mandated prune-at-85% / abort-at-90% thresholds asserted explicitly in tests 04 and 05.

### Substantive negative finding on Cycle 36 landing (Track B)

`data/v4/c27_track_b_c26_landing_verification.json` (SHA `f2eb5cc4582a2666…`) carries verdict `C26_TRACK_A_LANDING_INCOMPLETE`. WIG holds a 216-row stage-2 leaderboard and an operator-pruned tombstone but no `bass.json`, no `bass_family_verdict.json`, and no `bass.replay_proof.json`. Disco A's stage-2 leaderboard is absent — the sweep was interrupted. `SF2_CONFIRMED` is absent by absence — the discipline invariant against emitting it holds vacuously across the range. This finding retroactively confirms the prior audit's CONTINUE verdict on Cycle 36, which specifically named four checkpoints (216 distinct render SHAs, verdict enums, replay proofs `env_pin`, `stem_manifest` `blocked_on` advancement) as pending emitter fire. The emitter simply never fired.

Cycle 37 correctly did not supersede the Cycle 36 rollup: `supersedes_path: null` on the verification row honors FD-1 minimal intervention and preserves the Cycle 36 event as historical record of intent. The on-disk state (WIG 216-row leaderboard + tombstone) is preserved as a partial anchor for the next cycle to build on.

### Read-only anchors held; discipline invariants met

Sixteen spot-checked read-only anchors verified byte-identical pre-vs-post, including all six sweep-driver anchors preserved read-only (`coarse_sweep_sf2.py` `c74c35bc…`; `coarse_sweep_sf2_drums.py` `b894f2b3…`; `coarse_sweep_sf2_guitar.py` `9ddf692f…`; `fine_fit_sf2_v2.py` `dc030073…`; `fine_fit_sf2_drums.py` `54fb4d48…`; `fine_fit_sf2_guitar.py` `96368445…`); the prior-range handoff SHAs for `objective.py` `8087ce80…`, `replay.py` `1f43027039c45f5e`, `deliver_cg_ab_v4.py` `3c454652…`, `pinned_profile_schema_v1.json` `8f61d939…`, `cg_ab_mix.wav` `6e13e007…`, and `cg_bass_pinned_profile.json` `aa9b36be…`; the CG drums and guitar pinned profiles at `720f1424…` and `14d0707898b557df…`; and both non-CG bass verdict predecessors at WIG `7d1d6cad…` and Disco A `c8d4fd3d…`.

The operator-authority escalation `_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy` is unchanged with `blocked_on_operator=true`. No `SF2_CONFIRMED` verdicts landed anywhere on disk. Canonical 7-key environment pin on every new artifact. Eight ledger events landed with proper nested `confidence`, canonical `narrative` field, and `assessor="worker"` per the prior-range validator lesson (identity carried in `narrative` and `cycle` fields). Housekeeping tail landed in the correct c8+ order.

### Audit outcome

**VALIDATED.** Zero CRITICAL. Two MODERATE and two MINOR observations, none blocking.

The first MODERATE is an operational-risk gate for the next cycle: the brief listed six driver anchors under Track A with a specific patch shape, and the worker landed the canonical module + adoption plan but did not modify the drivers. Rationale — no sweep launched this cycle, so no operator-directive violation occurred in practice — is defensible under FD-1 (halt honest, no untested integration). But the next cycle *must* integrate the hygiene module into all six drivers under invariant (d) SHA-drift disclosure *before* any Rome / Peach Dream stage-2 sweep launches, or the operator directive is violated. The adoption plan specifies the mechanical path fully; the residual risk is procedural adherence.

The second MODERATE is the retroactive confirmation of the prior audit's CONTINUE verdict on Cycle 36. Cycle 36's rollup event contained ambitious language describing intent rather than delivered artifact; Cycle 37 correctly did not supersede it, emitting instead a peer action-required verification row. The next cycle's researcher should draft a targeted brief to re-fire the emitter (or run the stage-2 sweeps under integrated hygiene) and land the four missing checkpoints.

The MINOR observations record positive discipline signals: cross-cycle sound-match plus hygiene test total now sits at 85 across the campaign (28 + 6 + 12 + 7 + 1 + 21 + 10 across the relevant cycles); Cycle 37's worker enumerated four items for the auditor to scrutinize (driver-integration-satisfaction interpretation, `RunningTopK` SHA-tiebreak literal, test 04 mock strategy, Cycle 36 event historical treatment) as an exemplary independent-audit-surface disclosure.

## Discussion

Three things about this range are worth naming.

First, the range demonstrates the halt-honest pattern working on an *operational* rather than *substantive* axis. Cycle 36 attempted a substantive delivery (four checkpoints per non-CG bass song via the emitter); it did not complete. Cycle 37 could have re-attempted the same delivery pattern and possibly produced the same interruption. Instead the cycle correctly identified that the underlying gap was an *operational-hygiene* gap — sweeps were exhausting disk mid-run, batch-render patterns were leaving unscored subdirectories behind, and the operator's fresh procedure directive tightened the requirement to per-candidate render→score→delete. Cycle 37 landed the canonical hygiene module, its tests, and the adoption plan — the load-bearing infrastructure — without attempting the substantive delivery until the infrastructure is integrated into the drivers. This is the correct sequencing under FD-1: land the infrastructure that makes the substantive delivery reproducible, then do the substantive delivery under that infrastructure. Rushing substantive delivery under legacy infrastructure repeats the Cycle 36 pattern.

Second, the Cycle 37 verification-as-peer-event pattern is worth preserving as a discipline example. When Cycle 36 rolled up under ambitious language that did not match delivered artifacts, the tempting move for Cycle 37 would have been to supersede the Cycle 36 rollup — cleaner ledger, no residual ambiguity. Instead the cycle emitted a peer `action_required` verification row with `supersedes_path: null`, preserving Cycle 36 as historical record of intent that predated delivery. This preserves ledger auditability across the drift (a reader can see both the intent and the honest correction), respects FD-1 minimal intervention (no revised verdict where a peer verification suffices), and leaves the on-disk partial anchor (WIG 216-row leaderboard + tombstone) available for the next cycle to build on. The alternative — supersession — would have erased the drift from the ledger and made the next cycle's re-fire look like it was starting from scratch when in fact it can pick up the 216-row leaderboard as-is.

Third, the operator-directive integration gate is the next range's central risk. The mechanical path is fully specified — six drivers, additive flag on-by-default with regression opt-out, per-driver regression-test SHA match, invariant (d) SHA-drift disclosure — but the gate is procedural: any sweep launched against a non-integrated driver violates the operator directive. The next cycle's brief should explicitly BLOCK Rome + Peach Dream stage-2 sweep launches on completion of the six-driver integration, and should route the WIG + Disco A stage-2 re-work through the integrated drivers rather than picking up the interrupted sweeps under legacy hygiene.

## Open questions

- **Six-driver integration is the next-cycle blocking gate.** All six sweep drivers must be patched to import `_sweep_hygiene_c27.RunningTopK` under the additive `--score-and-delete-per-candidate` flag (on by default) with `--legacy-batch-render` opt-out for regression, per the adoption plan. Regression test per driver on CG (backward-compat SHA match). SHA-drift disclosed per driver under invariant (d). This must land *before* any Track C sweep launches.
- **Re-fire (or re-do) the Cycle 36 landing.** Run WIG stage-2 emission from the existing 216-row leaderboard (or re-run the sweep under integrated hygiene) and re-run Disco A stage-2 from scratch under integrated hygiene. Emit the standard triple per song (`bass.json` / `bass_family_verdict.json` / `bass.replay_proof.json`). Both verdicts land `STILL_INDETERMINATE` under corrected distance semantics until the operator adjudicates the acceptance-policy escalation — the SF2_CONFIRMED-forbidden clause is inherited.
- **Rome + Peach Dream stage-2 fine fits.** Both predicted `SF2_RULED_OUT` under distance semantics from the prior-range stage-1 embedding distances (Rome 0.5145; Peach Dream 0.4437 — both above the 0.40 floor). Should run under integrated hygiene once the driver integration lands.
- **WIG + Disco A drums stage-1 coarse sweeps.** Aspirational under integrated hygiene; extends the systematic composite-vs-source-of-truth finding from 4-arc bass toward the full 15-arc set if the pattern holds.
- **Completion report second pass.** Consolidate the c22-c27 amendments plus the 15-arc composite-vs-source-of-truth systematic finding into a coherent second-pass completion document.
- **Non-CG bass acceptance-policy escalation.** Remains `blocked_on_operator=true`. The systematic 4-arc finding still predicts OPT2 (refuse extension + OPT3 htdemucs bass fallback) as the invariant-compliant outcome; the ear-plausibility check on the four stage-1 top-1 renders remains the recommended tiebreaker before the operator authorizes OPT1.
- **Approximately 166 unscored render subdirectories from the Cycle 36 Disco A interruption.** Will be pruned by the df-guard's first invocation in the next cycle's sweep under the age-gate (>60s) policy per the worker's honest note.

## Appendix: Provenance

**Directive.** Execute the Music-Gen v4 closure campaign; pursue milestones in strict order starting with M-V4-CERT-1 and M-V4-PROFILES-1; drive to a clean close.

**Cycle range.** cycles 35–37.

**Working directory.** `/home/user/long-exposure-runs/music-gen`.

**Session references.**

- Cycle 35 researcher `f4216562-7a24-42d5-99ac-a4d7fb74f975`; worker `1e877c27-bbc3-4144-9ee4-f6b8d74ef7ee`; auditor `db4c2124-afd6-475d-a1ed-4704fa2afb00`.
- Cycle 36 researcher `235384ad-d12f-4f8d-9753-8c9acc27e0f7`; worker `5b3fa0f2-b9ab-4b89-9a5d-afda922de680`; auditor `4e187fd0-b9b9-4887-85d5-f18e809cd77d`.
- Cycle 37 researcher `02f228e4-3039-467c-ab4b-233e147ba383`; worker `6db52a28-a9aa-4a6e-936c-1e083bcffcfc`; auditor `8fea4b3c-cb2d-4e34-872c-a095a3ca4352`.

**Audit verdict.** **VALIDATED**. Zero CRITICAL. Two MODERATE (driver integration deferred as operational gate for next cycle; Cycle 36 emitter did not fire, retroactively confirming prior CONTINUE verdict). Two MINOR (test coverage exceeded gate at 10/10 against ≥6; worker's independent-audit-surface disclosure was exemplary).

**Terminal deliverables landed this range.**

- `scripts/sound_match/_sweep_hygiene_c27.py` (SHA `771ff42b768d9c44…`, 10,657 bytes) — canonical hygiene module: `RunningTopK` per-candidate render→score→delete with deterministic SHA-256 tiebreak; df guard prune-at-85% / abort-at-90% per FD-1; stale-audio pruner age-gated >60s.
- 10/10 PASS test suite for the hygiene module with operator-mandated prune/abort thresholds asserted in tests 04 and 05.
- `docs/sweep_hygiene_c27_driver_adoption_plan.md` (SHA `37203b8d60594fd0…`) — six-step integration shape, regression-test gate per driver on CG backward-compat SHA match, per-driver invariant-(d) SHA-drift disclosure.
- `data/v4/c27_track_b_c26_landing_verification.json` (SHA `f2eb5cc4582a2666…`) — verdict `C26_TRACK_A_LANDING_INCOMPLETE`, `supersedes_path: null` (peer verification, not supersession).
- Cycle 35 stage-2 sweep artifacts (WIG 216-row leaderboard + operator-pruned tombstone) preserved on disk as partial anchor for next-cycle emission.
- POR one-liner landed verbatim per brief.
- Eight ledger events landed with proper nested `confidence`, canonical `narrative` field, `assessor="worker"` (c27 identity carried in `narrative` and `cycle` fields).
- Housekeeping tail in correct c8+ order.

**Read-only anchors preserved byte-identical pre-vs-post (16 spot-checked).**

- Six sweep-driver anchors: `coarse_sweep_sf2.py` `c74c35bc…`; `coarse_sweep_sf2_drums.py` `b894f2b3…`; `coarse_sweep_sf2_guitar.py` `9ddf692f…`; `fine_fit_sf2_v2.py` `dc030073…`; `fine_fit_sf2_drums.py` `54fb4d48…`; `fine_fit_sf2_guitar.py` `96368445…`.
- `objective.py` `8087ce80…`; `replay.py` `1f43027039c45f5e`; `deliver_cg_ab_v4.py` `3c454652…`; `pinned_profile_schema_v1.json` `8f61d939…`; `cg_ab_mix.wav` `6e13e007…`; `cg_bass_pinned_profile.json` `aa9b36be…`.
- `cg_drums_pinned_profile.json` `720f1424…`; `cg_guitar_pinned_profile.json` `14d0707898b557df…`.
- WIG bass verdict predecessor `7d1d6cad…`; Disco A bass verdict predecessor `c8d4fd3d…`.

**Environment pin.** Canonical 7-key `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` on every new artifact.

**Discipline guards asserted.** No `SF2_CONFIRMED` verdicts anywhere on disk (absolute prohibition). No unilateral scope-extension of the c9 CG-bass precedent. Operator-authority escalation `_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy` unchanged, `blocked_on_operator=true`. `/usr/bin/python3` interpreter guard on all new scripts. No PRNG, no `sidecar_nonfactor` imports, no `--verify-det` bypass, no VST3 state APIs. No wait-on-operator memo (banned per operator directive 2026-09-03 part 2).

**Standing test-count anchor.** Cross-cycle sound-match plus hygiene tests total 85 (28 + 6 + 12 + 7 + 1 + 21 + 10 across the relevant cycles).

**Milestone status at range close.**

- M-V4-CERT-1 — validated (E2E_DETERMINISM_HOLDS on the v3 spine).
- M-V4-PROFILES-1 CG (5/5 instruments) — validated (bass_v2 accepted per operator authority; drums OPT3; guitar OPT3; piano/other NULL grounded).
- M-V4-PROFILES-1 non-CG bass — 2/4 `SF2_RULED_OUT` from prior range (Rome, Peach Dream); 2/4 `STILL_INDETERMINATE` (WIG, Disco A) with WIG stage-2 leaderboard (216 rows) landed but emitter incomplete, Disco A stage-2 sweep interrupted (approximately 166 unscored subdirs left for next-cycle df-guard prune).
- M-V4-PROFILES-1 non-CG drums — 0/4 (aspirational, deferred).
- M-V4-PROFILES-1 non-CG guitar — 0/2 (aspirational, deferred; WIG + Peach Dream guitar are NULL by MIDI-probe).
- M-V4-SHOWCASE-1 CG — `LANDS_pending_operator` (`cg_ab_mix.wav` SHA `6e13e007…` byte-identical since c17).
- M-V4-SHOWCASE-1 non-CG — BLOCKED on `_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy` (`blocked_on_operator=true`).
- M-V4-RULES-1 — scaffold landed c20; substantive implementation queued.
- M-V4-EAR-1 — not yet opened.
- M-V4-GEN-1 — conditional on M-V4-RULES + M-V4-EAR.
- M-V4-CLOSE-1 — c24 amendment landed; further amendments as substantive work completes.

**Next-cycle blocking gate.** Integrate `_sweep_hygiene_c27` into all six driver anchors per `docs/sweep_hygiene_c27_driver_adoption_plan.md` under invariant (d) SHA-drift disclosure *before* any Rome / Peach Dream stage-2 sweep launches. Operator ear remains LANDS authority post-hoc per FD-6.
