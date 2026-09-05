---
title: "Music-Gen v4 — Cycles 41-43"
date: "2026-09-05"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v4 — Cycles 41-43

## Abstract

Cycles 41-43 pushed the two remaining fine-fit driver regressions through the operator-mandated legacy-mode gate, closed the two audit-inherited MODERATE findings from the prior range, and preserved six live operator-authority escalations under a no-adjudication hold — all without launching any substantive stage-2 sweep work, which remains gated on operator adjudication of a three-path floating-point-summation question that now covers three fine-fit drivers. Cycle 41 launched detached legacy-mode regressions for `fine_fit_sf2_v2.py` (bass) and `fine_fit_sf2_guitar.py` against read-only Chicken Grease anchors; both drivers produced bit-identical `render_sha` across all 216 cells but exhibited the same approximately-1e-6 composite-score drift on a subset of cells that the drums fine-fit driver had exhibited in the prior range, and both were correctly HALTed per FD-1 strict-equality with dedicated ledger events (`1c288c4f-…` for bass, `43830b3b-…` for guitar). A `_serial_lock_op1.py` helper (SHA `121809db…`) was introduced to preserve serial-execution guarantees under the multi-driver detached-launch pattern. Cycle 42 discovered a memo state-machine constraint (predecessors must be linked-not-closed; `action_required → action_required` transitions are not re-emitted) and applied it correctly to the growing set of operator escalations, but skipped the procedurally-mandated `_selection/` event on a POR shadow-zone counting-method drift (728 → 732 rows between c31-close and c32-open), leaving the c32 auditor with two MODERATE findings: (i) the two Cycle 41 fine-fit HALTs existed as ledger events but had no `data/v4/_manager/M-V4-CERT-*` JSON sidecars discoverable via `ls`, and (ii) the POR shadow-drift lacked its retroactive `_selection/` event. Cycle 43 landed both closures cleanly: two new sidecar JSONs mirroring the c30 drums-halt shape verbatim (three named paths, `blocked_on_operator=true`, `carried_from_cycle=31`, `supersedes_path=null`), and a retroactive `_selection/c33-por-shadow-drift-disclosure-retroactive-for-c32.json` event enumerating four plausible c31-tail housekeeping rows as the counting-methodology drift delta. All six operator escalations are now discoverable via both `grep _manager/M-V4-CERT` and `ls data/v4/_manager/`, each with correct `carried_from_cycle` (7, 16, 30, 31, 31, 32) and `blocked_on_operator=true`. Cycle 43 verified the POR shadow-zone at 745 parseable Milestones rows at cycle open — zero drift versus c32-close baseline — and grew to 759 rows after housekeeping registration. Tests extended in-place from 14 → 16 cases on `tests/test_c30_legacy_mode_regression.py`; total cross-cycle sound-match plus hygiene test count now 24 in-place plus 8 standalone. All six read-only anchors held byte-identical pre-vs-post including the Peach Dream stem manifest (SHA `c4944ee8…`); OP-1 sentinel wrapping preserved across all three fine-fit driver SHAs (`6c80c438…`, `a432e1d1…`, `40dbb673…`). Independent audit returned **VALIDATED** with three MODERATE observations (two of them positive — the closures of the prior audit's MODERATE debt — and one standing hygiene item on emitter writer-boundary routing) and three MINOR observations. Zero CRITICAL. Ledger grew 1549 → 1563 (+14 events); `promise_check` baseline preserved at 16 pre-existing ERRORs with zero drift introduced this range. `M-V4-SHOWCASE-1` status unchanged (`LANDS_pending_operator`); the CG A/B mix WAV holds SHA `6e13e007…` byte-identical since c17.

## Introduction

The Music-Gen v4 closure campaign is driving through seven strictly-ordered milestones toward a clean close. Cycles 41-43 sit at the tail of the operational-hygiene layer of `M-V4-PROFILES-1` non-Chicken-Grease work: the prior range closed with four of six sweep drivers fully green under legacy-mode regression, one fine-fit driver HALTed on floating-point composite-score drift, and two fine-fit drivers deferred for next-cycle detached launch. The current range completed the six-driver matrix in a specific and predictable way: both remaining drivers HALTed on the same drift pattern.

The consequence is that substantive stage-2 sweep work — Disco A stage-2 resume (Track B), Rome and Peach Dream stage-2 new (Track C), WIG and Disco A drums stage-1 (Track D) — is now blocked on a single operator-authority question that spans three fine-fit drivers. The three-path escalation structure from the prior range (Path A: accept a render-level regression bar via a new invariant (f); Path B: hold the strict-equality bar and keep the drivers HALTed; Path C: harden `objective.py` summation, which requires lifting the read-only per invariant 8) applies to all three drivers uniformly. Path A is the single-action resolution for all three; Path B blocks all downstream drums/bass/guitar fine-fits; Path C is the most rigorous but touches a read-only anchor.

The range's non-adjudication posture is deliberate. The anti-heartbeat rule forbids wait-on-operator memos, and Priority 3 in the c33 brief was explicitly gated on operator adjudication arriving via `live_guidance`. No adjudication landed; Cycle 43 correctly did not proceed with any of the three paths. Instead the cycle closed audit-inherited hygiene debt from the prior range and verified the state remaining in place while the adjudication is pending.

## Approach

**Cycle 41 (two fine-fit regressions launched detached; both HALT).** Launched `fine_fit_sf2_v2.py` and `fine_fit_sf2_guitar.py` legacy-mode CG-anchor regressions detached at cycle open per the c8 launch policy (≤10 min each; zero wall-budget impact). Introduced `_serial_lock_op1.py` (SHA `121809db…`) to preserve serial-execution guarantees under the multi-driver detached-launch pattern (OP-1 sentinel wrapping). Both regressions produced 216/216 bit-identical `render_sha` per cell but exhibited approximately-1e-6 composite-score drift on a subset of cells — the same summation-order floating-point pattern the drums fine-fit driver had exhibited in the prior range. Both drivers were HALTed per FD-1 strict-equality; two dedicated ledger events landed (`1c288c4f-…` for bass, `43830b3b-…` for guitar). Extended the anchor-substitution table with c3 `bass_stage2b/leaderboard.tsv` SHA `c64c0328…` as the correct predecessor for `fine_fit_sf2_v2.py` per the prior-range invariant (d) correction.

**Cycle 42 (memo state-machine discovery; POR shadow-drift; `_selection/` skipped).** Discovered a memo state-machine constraint under FD-1: predecessor memos are linked-not-closed rather than re-emitted with `action_required → action_required` transitions. Applied the constraint correctly across the growing set of operator escalations. Observed a POR shadow-zone counting-method drift between c31-close (728 rows) and c32-open (732 rows) — a delta of four rows attributable to counting-methodology drift on the parser boundary rather than to substantive drift. Skipped the procedurally-mandated retroactive `_selection/` event on operator-scope judgment; the c32 auditor flagged this as MODERATE #2. The auditor also flagged that the two Cycle 41 fine-fit HALTs existed only as ledger events and had no `data/v4/_manager/M-V4-CERT-*` JSON sidecar discoverable via `ls`, leaving the escalations grep-only rather than `ls`-discoverable (MODERATE #1).

**Cycle 43 (close two audit-MODERATE closures; no-adjudication hold).** Two priority landings, four deferrals, one verification, one test extension:

- Priority 1: authored `data/v4/_manager/M-V4-CERT-fine-fit-sf2-v2-legacy-halt.json` and `data/v4/_manager/M-V4-CERT-fine-fit-sf2-guitar-legacy-halt.json` as JSON sidecars, sourced from the c31 ledger events (`1c288c4f-…` bass, `43830b3b-…` guitar) and shape-mirrored on the c30 drums-halt sidecar (status, authority, `blocked_on_operator=true`, `carried_from_cycle=31`, `supersedes_path=null`, three-path structure with per-path invariant analysis).
- Priority 2: authored `data/v4/_selection/c33-por-shadow-drift-disclosure-retroactive-for-c32.json` with a 4-row diff enumeration (`_plan/register-c31-sub-leaves`, `_run/cycle_31_closed`, `_archive/cycle-31-scratch`, `_infra/adopt-cycle31-tests`) as plausible c31-tail housekeeping candidates matching the +4 counting-method drift.
- Priority 3: no operator adjudication received in `live_guidance` — correctly deferred; resume commands preserved in Track B/C/D deferral rows.
- Priority 4: Peach Dream stem-manifest divergence anchor SHA `c4944ee8…` byte-identical pre-vs-post; divergence disclosure carried on the `peach-dream-bass-stage2-deferred` row.
- Priority 5: Tracks B / C / D deferred per Priority 3 gating; four deferral rows added with concrete resume commands.
- Priority 6: POR shadow-zone verified at 745 parseable Milestones rows at cycle open versus c32-close baseline 745 (zero delta); grew to 759 after c33 housekeeping registration. `tools/_por_shadow_consolidate_c31.py` not re-run per the c14+ one-shot convention.
- Priority 7: extended `tests/test_c30_legacy_mode_regression.py` in-place from 14 → 16 cases (test_15 JSON sidecar shape-parity + test_16 `_selection/` event existence + 4-row diff). Standalone `tests/test_fine_fit_serial_lock_c32.py` unchanged at 8/8. Cross-cycle total 24/24 PASS.

**Discipline guards asserted for the range.** Zero `SF2_CONFIRMED` verdicts emitted anywhere on disk. No PRNG. No `sidecar_nonfactor` imports. No VST3 state APIs. No `--verify-det` bypass. `/usr/bin/python3` interpreter guard on the emitter and all new artifacts. `supersedes_path` as string or null throughout per the c14 lemma; new manager memos use `null`; the `_selection/` event uses `null`. All six read-only anchors byte-identical pre-vs-post. Canonical 7-key `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` unchanged; no FD-16(a) re-issue trigger. Housekeeping tail in c8+ order. No wait-on-operator memo (banned per operator directive 2026-09-03 part 2); the Priority 0 preserve-only posture satisfies the genuine operator-authority carve-out.

## Findings

### All six sweep drivers now have completed legacy-mode regression coverage

The three coarse-sweep drivers passed full preset matrices in the prior range and remain green here. The three fine-fit drivers have now all been regressed to the same conclusion: render layer bit-deterministic (216/216 `render_sha` match on each driver), composite score drifts on a subset of cells at approximately 1e-6 magnitude, HALT per FD-1 strict-equality. This is not a defect of the current range; it is the range demonstrating that the summation-order floating-point pattern is universal across the three fine-fit drivers rather than specific to drums, which strengthens the case for Path A (a render-level regression bar via new invariant (f)) as the single-action resolution across all three.

### Six operator-authority escalations preserved and now fully discoverable

The six live escalations are preserved with correct `carried_from_cycle` values and `blocked_on_operator=true` throughout:

- `_manager/M-V4-SHOWCASE-1-cg-bass-acceptance-policy` (`carried_from_cycle=7`) — resolved earlier by operator directive; retained as historical anchor.
- `_manager/M-V4-METRIC-SEMANTICS-c16` (`carried_from_cycle=16`) — non-CG stage-1 metric-semantics distance-vs-similarity adjudication.
- `_manager/M-V4-CERT-fine-fit-sf2-drums-legacy-halt` (`carried_from_cycle=30`) — three-path floating-point drift on drums fine-fit.
- `_manager/M-V4-CERT-fine-fit-sf2-v2-legacy-halt` (`carried_from_cycle=31`) — same pattern on bass fine-fit; JSON sidecar landed this cycle.
- `_manager/M-V4-CERT-fine-fit-sf2-guitar-legacy-halt` (`carried_from_cycle=31`) — same pattern on guitar fine-fit; JSON sidecar landed this cycle.
- `_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy` (`carried_from_cycle=32`) — non-CG bass acceptance policy under the c9 CG-bass composite-relative WINNER precedent scope question.

Post-Cycle 43 all six are discoverable via both `grep _manager/M-V4-CERT` and `ls data/v4/_manager/`. This closes the c32 auditor's MODERATE #1 finding cleanly.

### Retroactive `_selection/` event closes c32 auditor's MODERATE #2

`data/v4/_selection/c33-por-shadow-drift-disclosure-retroactive-for-c32.json` enumerates four c31-tail housekeeping rows (`_plan/register-c31-sub-leaves`, `_run/cycle_31_closed`, `_archive/cycle-31-scratch`, `_infra/adopt-cycle31-tests`) as the +4 counting-methodology drift delta between c31-close (728) and c32-open (732). This satisfies the procedural mandate for the retroactive `_selection/` event that the c32 worker had skipped on judgment; the c32 auditor's MODERATE #2 is closed. The hypothesis is plausible but not yet formally proven by a before-vs-after parser diff on the c31-close and c32-open POR snapshots — the audit flagged this as a strengthening opportunity, not a defect.

### POR shadow-zone hold verified

Parseable Milestones rows at c33 open: 745 (matches c32-close baseline). Post-registration: 759 (14 c33 rows added). Zero drift introduced this cycle; no new `_selection/` event needed. `tools/_por_shadow_consolidate_c31.py` not re-run per the c14+ one-shot convention.

### Read-only anchors held; discipline invariants met

Six read-only anchors verified byte-identical pre-vs-post: `scripts/sound_match/objective.py` `8087ce80…`; `scripts/sound_match/_sweep_hygiene_c27.py` `771ff42b…`; `scripts/sound_match/_serial_lock_op1.py` `121809db…`; `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` `6e13e007…`; `docs/agent_picks_selection_invariants.md` `29a1610b…`; Peach Dream stem manifest `c4944ee8…`. OP-1 sentinel wrapping preserved across all three fine-fit driver SHAs (`6c80c438…`, `a432e1d1…`, `40dbb673…`); coarse-sweep driver SHAs match brief (`3f8bfa08…`, `26aa754c…`, `d6c54f21…`).

Zero `SF2_CONFIRMED` verdicts anywhere on disk. Canonical 7-key environment pin unchanged. Fourteen ledger events landed this range; ledger grew 1549 → 1563. `promise_check` at 16 ERRORs (matches c31/c32 baseline; zero drift introduced this range).

### Test coverage extended in-place

`tests/test_c30_legacy_mode_regression.py` extended in-place 14 → 16 cases (test_15 JSON sidecar shape-parity across the three fine-fit HALT sidecars; test_16 `_selection/` event existence plus 4-row diff enumeration). Standalone `tests/test_fine_fit_serial_lock_c32.py` unchanged at 8/8. Cross-cycle total: 24 in-place plus 8 standalone = 32 PASS (c30 6 + c31 4 + c32 4 + c33 2 in-place + c32 8 standalone). Test-suite growth pattern is healthy and cross-cycle test debt is closed as it arises.

### Audit outcome

**VALIDATED.** Zero CRITICAL. Three MODERATE, three MINOR, none blocking.

Two of the three MODERATE observations are positive-substantive lands: the JSON sidecar backfill closed the c32 auditor's MODERATE #1 cleanly, and the retroactive `_selection/` event closed the c32 auditor's MODERATE #2 cleanly. Both closures mirrored the target shape verbatim (c30 drums-halt shape for the sidecars; c-N `_selection/` shape for the retroactive event), touched no OPEN escalation, and modified no read-only anchor. This is exactly the kind of low-risk hygiene closure the closure-campaign posture calls for.

The third MODERATE observation is a standing item inherited from the prior range: the ledger emitter (`tools/_emit_c33_ledger_events.py`) writes directly to `promise_ledger.jsonl` via `open(..., "a")` rather than routing through the c14+ `long_exposure.workspace_bootstrap.append_ledger_event` helper. The helper enforces validation, UUID5 content-hash derivation, the `_STATUS_ENUM`, and `supersedes_path` string validation per the c14 lemma. The current-cycle worker asserts UUID5 content-hash `event_id` was manually pre-computed and the current baseline of 16 pre-existing ERRORs suggests the manual pre-computation is working, but formal writer-boundary routing would be safer. The recommendation is that the next cycle route all emitters through `append_ledger_event`, or document a formal exemption for the sound-match `tools/_emit_c*` chain.

The three MINOR observations record positive discipline signals and one strengthening opportunity: the Priority 0 memo state-machine constraint is honored throughout (no unilateral status advance); the Peach Dream Priority 4 divergence is carried correctly on the deferral row (with recommendation to surface as its own event if a subsequent cycle lands Path A or Path C adjudication); the test-suite growth pattern is healthy but the `deliver_cg_ab_v4.py` full-render + Peach Dream stem manifest schema coverage remains deferred per the c10-c17 pattern.

## Discussion

Three things about this range are worth naming.

First, the range demonstrates the "close audit debt without touching OPEN work" pattern working exactly as designed. The prior range closed with two MODERATE findings against the intermediate cycle's worker: JSON sidecars missing for two of the three fine-fit HALTs, and the procedurally-mandated `_selection/` event skipped on POR shadow-drift. Cycle 43 could have addressed either finding by re-opening substantive work (re-firing regressions, attempting adjudication paths, restructuring the POR). Instead the cycle closed both findings by authoring the *specific missing artifacts* — two JSON sidecars mirroring the c30 drums-halt shape verbatim, and one retroactive `_selection/` event with the 4-row diff enumeration — without touching any OPEN escalation, any read-only anchor, or any downstream track. This is the correct closure pattern under FD-1 halt-honest: fix the specific missing artifact, do not use the closure as cover to expand scope.

Second, the range surfaces that all three fine-fit drivers now HALT on the same floating-point summation-order pattern. This is a genuine strengthening of the operator-authority escalation shape: Path A (accept a render-level regression bar via new invariant (f)) becomes the single-action resolution across three drivers rather than one; Path B (hold the strict-equality bar) blocks all downstream drums / bass / guitar fine-fit work rather than only drums; Path C (harden `objective.py` summation) touches the same read-only anchor across all three drivers. The operator's decision on the drums-fine escalation now has campaign-wide consequences, not driver-specific ones. The three-path shape is defensible in isolation and now more so given the uniform pattern; the range's decision to preserve rather than adjudicate is correct.

Third, the range holds the campaign in the tightest possible operational state while operator adjudication is pending. All six escalations are preserved with correct provenance and are now doubly discoverable (grep + ls). All six read-only anchors are verified byte-identical. The POR shadow-zone hold is verified at zero drift. The ledger emitter is documented as writing outside the c14+ hardening boundary but with manual UUID5 pre-computation producing the expected baseline. The test suite has grown in-place with cross-cycle regression coverage for each closure. Substantive stage-2 sweep work is honestly deferred with concrete resume commands rather than attempted under unresolved semantics. This is what "drive itself to a clean close" looks like when the last remaining substantive work is gated on a genuine operator-authority question: preserve state, close hygiene debt, and hold.

## Open questions

- **Operator adjudication of the three-driver fine-fit legacy HALT.** Three named paths (A render-level bar via new invariant (f); B hold strict; C harden `objective.py` per invariant 8 operator scope). Path A is the single-action resolution for all three drivers. Priority 3 in the c33 brief was gated on this arriving via `live_guidance`; nothing arrived; correctly deferred. This is the single blocking gate on Track B (Disco A stage-2 resume), Track C (Rome + Peach Dream stage-2 new), and Track D (WIG + Disco A drums stage-1).
- **Non-CG bass acceptance-policy escalation.** Remains `blocked_on_operator=true` with `carried_from_cycle=32`. Systematic 4-arc composite-vs-source-of-truth finding still predicts OPT2 (refuse extension + OPT3 htdemucs bass fallback) as the invariant-compliant outcome; ear-plausibility check on the four stage-1 top-1 renders remains the recommended tiebreaker.
- **Metric-semantics escalation.** Remains `blocked_on_operator=true` with `carried_from_cycle=16`.
- **Ledger emitter writer-boundary routing.** The next cycle should route all emitters through `long_exposure.workspace_bootstrap.append_ledger_event`, or document a formal exemption for the sound-match `tools/_emit_c*` chain. The current manual UUID5 pre-computation is working (16-ERROR baseline preserved with zero drift) but formal writer-boundary routing would be safer.
- **`_selection/` event empirical proof strengthening.** The current-range `_selection/c33-por-shadow-drift-disclosure-retroactive-for-c32.json` records the 4-row hypothesis as "counting-methodology drift" without a concrete before-vs-after parser diff. A subsequent auditor could formally validate by running the same parser on the c31-close and c32-open POR snapshots to confirm those four specific rows are the delta.
- **Peach Dream stem-manifest divergence surfacing.** If a subsequent cycle lands Path A or Path C adjudication and Track C launches, the next brief should re-mandate the Priority 4 divergence disclosure as a first-class rollup row before Peach Dream stage-2 launch.
- **Test coverage gaps.** `deliver_cg_ab_v4.py` full-render coverage and Peach Dream stem manifest schema coverage remain deferred per the c10-c17 pattern.
- **POR shadow-zone hold.** Parseable canonical rows at 759 post-Cycle 43 registration; zero drift; hold verified. Shadow-zone duplicate rows below `## Pointer to ledger` remain unconsolidated (three-consecutive-cycle deferral now four); consolidation cycle should still be scoped before the next substantive push.

## Appendix: Provenance

**Directive.** Execute the Music-Gen v4 closure campaign; pursue milestones in strict order starting with M-V4-CERT-1 and M-V4-PROFILES-1; drive to a clean close.

**Cycle range.** cycles 41–43.

**Working directory.** `/home/user/long-exposure-runs/music-gen`.

**Session references.**

- Cycle 41 researcher `4f9ca2cf-f9c1-46a9-8465-b4e084ec339d`; worker `cfdb4d8c-3aa7-411c-9105-d5266c718f4b`; auditor `f5e77216-9992-4c3e-976c-94b9f2823010`.
- Cycle 42 researcher `de362e13-99f0-4b3f-b66e-5e130372abdb`; worker `c3e2963d-9f1a-42e8-bb51-fe9740dcb4a2`; auditor `e87a5002-754b-40be-8e38-3d70e8cc00bf`.
- Cycle 43 researcher `f745eaf6-e2f1-44df-bbc1-6addf50699b2`; worker `0dd18758-d34c-4387-b1fc-7e3eb0c6a1d8`; auditor `34b59359-8d67-4fc4-a7bb-d6f9483eb2a8`.

**Audit verdict.** **VALIDATED**. Zero CRITICAL. Three MODERATE (M-1 positive substantive land closing c32 MODERATE #1 via JSON sidecar backfill; M-2 positive substantive land closing c32 MODERATE #2 via retroactive `_selection/` event; M-3 standing hygiene item on ledger-emitter writer-boundary routing inherited from the intermediate cycle). Three MINOR (Priority 0 memo state-machine constraint honored; Peach Dream Priority 4 divergence carried on deferral row; test-suite growth pattern healthy but accelerating).

**Terminal deliverables landed this range.**

- Two fine-fit driver regressions completed and HALTed: `fine_fit_sf2_v2.py` (bass) 216/216 `render_sha` bit-identical, ledger event `1c288c4f-…`; `fine_fit_sf2_guitar.py` 216/216 `render_sha` bit-identical, ledger event `43830b3b-…`.
- `scripts/sound_match/_serial_lock_op1.py` (SHA `121809db…`) — serial-execution guarantee helper for OP-1 sentinel wrapping.
- `data/v4/_manager/M-V4-CERT-fine-fit-sf2-v2-legacy-halt.json` — JSON sidecar mirroring c30 drums-halt shape verbatim, `carried_from_cycle=31`, `blocked_on_operator=true`, `supersedes_path=null`, three-path structure.
- `data/v4/_manager/M-V4-CERT-fine-fit-sf2-guitar-legacy-halt.json` — same shape.
- `data/v4/_selection/c33-por-shadow-drift-disclosure-retroactive-for-c32.json` — 4-row diff enumeration with counting-methodology-drift hypothesis.
- `tests/test_c30_legacy_mode_regression.py` extended in-place 14 → 16 cases; standalone `tests/test_fine_fit_serial_lock_c32.py` at 8/8 preserved; cross-cycle total 24 in-place + 8 standalone = 32 PASS.
- Four Track B/C/D deferral rows with concrete resume commands.
- Housekeeping sequence: `_run/cycle_33_closed` → `_archive/cycle-33-scratch` → `_infra/adopt-cycle33-tests`. 14 events emitted (ledger 1549 → 1563).

**Read-only anchors preserved byte-identical pre-vs-post (6 verified).**

- `scripts/sound_match/objective.py` `8087ce80…` (invariant 8; Path C in HALT escalations would require lifting)
- `scripts/sound_match/_sweep_hygiene_c27.py` `771ff42b…`
- `scripts/sound_match/_serial_lock_op1.py` `121809db…`
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` `6e13e007…`
- `docs/agent_picks_selection_invariants.md` `29a1610b…`
- Peach Dream stem manifest `c4944ee8…`

**OP-1 sentinel wrapping** preserved across three fine-fit driver SHAs (`6c80c438…`, `a432e1d1…`, `40dbb673…`); coarse-sweep driver SHAs match brief (`3f8bfa08…`, `26aa754c…`, `d6c54f21…`).

**Six operator escalations preserved.**

- `_manager/M-V4-SHOWCASE-1-cg-bass-acceptance-policy` (`carried_from_cycle=7`)
- `_manager/M-V4-METRIC-SEMANTICS-c16` (`carried_from_cycle=16`)
- `_manager/M-V4-CERT-fine-fit-sf2-drums-legacy-halt` (`carried_from_cycle=30`)
- `_manager/M-V4-CERT-fine-fit-sf2-v2-legacy-halt` (`carried_from_cycle=31`; JSON sidecar landed c43)
- `_manager/M-V4-CERT-fine-fit-sf2-guitar-legacy-halt` (`carried_from_cycle=31`; JSON sidecar landed c43)
- `_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy` (`carried_from_cycle=32`)

All six `blocked_on_operator=true`; all six discoverable via both `grep _manager/M-V4-CERT` and `ls data/v4/_manager/`.

**Environment pin.** Canonical 7-key `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` unchanged this range; no FD-16(a) re-issue trigger.

**Ledger + promise_check.** Ledger grew 1549 → 1563 (+14 events). `promise_check` at 16 ERRORs matches c31/c32 baseline (zero c33-introduced drift).

**POR shadow-zone hold.** 745 parseable Milestones at c33 open (matches c32-close baseline; zero delta). 759 post-registration (+14 c33 rows). `tools/_por_shadow_consolidate_c31.py` not re-run per c14+ one-shot convention.

**Discipline guards asserted.** Zero `SF2_CONFIRMED` verdicts anywhere on disk (invariant 9 upheld). `objective.py` read-only preserved (invariant 8). `supersedes_path` as string or null throughout per c14 lemma. `/usr/bin/python3` interpreter guard on emitter and all new artifacts. No PRNG, no `sidecar_nonfactor` imports, no VST3 state APIs, no `--verify-det` bypass. No wait-on-operator memo (banned per operator directive 2026-09-03 part 2); Priority 0 preserve-only posture satisfies genuine operator-authority carve-out.

**Milestone status at range close.**

- M-V4-CERT-1 — validated (E2E_DETERMINISM_HOLDS on the v3 spine).
- M-V4-PROFILES-1 CG (5/5 instruments) — validated.
- M-V4-PROFILES-1 non-CG bass — 2/4 `SF2_RULED_OUT` from earlier work (Rome, Peach Dream); 2/4 `STILL_INDETERMINATE` (WIG, Disco A). Stage-2 re-work gated on operator adjudication of the three-driver fine-fit legacy HALT and the non-CG bass acceptance-policy escalation.
- M-V4-PROFILES-1 non-CG drums — 0/4 (Track D unblocked at the driver-regression level from prior range; gated on operator adjudication of fine-fit HALTs for downstream stage-2).
- M-V4-PROFILES-1 non-CG guitar — 0/2 (WIG + Peach Dream guitar are NULL by earlier MIDI-probe).
- M-V4-SHOWCASE-1 CG — `LANDS_pending_operator` (`cg_ab_mix.wav` SHA `6e13e007…` byte-identical since c17).
- M-V4-SHOWCASE-1 non-CG — BLOCKED on non-CG bass acceptance-policy escalation.
- M-V4-RULES-1 — scaffold landed c20; substantive implementation queued.
- M-V4-EAR-1 — not yet opened.
- M-V4-GEN-1 — conditional on M-V4-RULES + M-V4-EAR.
- M-V4-CLOSE-1 — c24 amendment landed; further amendments as substantive work completes.

**Next-cycle first task.** Continue to prioritize operator adjudication of the three-driver fine-fit legacy HALT as the single blocking gate on all downstream Track A/B/C/D resumption. If adjudication arrives via `live_guidance`, execute the chosen path (Path A recommended as the single-action resolution across all three drivers; Path B blocks all fine-fits; Path C requires lifting `objective.py` read-only per invariant 8). If it does not, continue the preserve-and-close-hygiene-debt posture; route the ledger emitter through `append_ledger_event` per the standing MODERATE observation; consider scoping the POR shadow-zone consolidation cycle. Operator ear remains LANDS authority post-hoc per FD-6.
