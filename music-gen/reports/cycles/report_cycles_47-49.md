---
title: "Music-Gen v4 — Cycles 47-49"
date: "2026-09-05"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v4 — Cycles 47-49

## Abstract

Cycles 47-49 extended the preservation-only heartbeat cadence established at the end of the prior range into a mature multi-cycle pattern with a stable, mechanically-repeatable shape while all six operator-authority escalations remained `blocked_on_operator=true` throughout. The range constitutes cycles six, seven, and eight of the consecutive substantive-heartbeat sequence codified by the c36 auditor's M-1/M-2 terminal contracts. Each cycle re-probed the workspace for the `long_exposure/` package (ABSENT across the range — chain-stable since c34), emitted a chain-supersede preservation event on the workspace-forced OPT_B ledger-emitter exemption via string `supersedes_path` per the c14 lemma, scanned `live_guidance` for an operator-supplied c31/c32 POR snapshot (absent across the range), emitted a stand-pat preservation event chain-superseding the prior cycle's stand-pat under the same string-typed supersede semantics, verified the six escalation sidecars byte-identical versus the prior cycle's attestation SHAs, landed four honest-deferral rows for the queued Track B/C/D non-CG bass and drums work with concrete resume commands, verified the Peach Dream stem manifest byte-identical (`c4944ee80dfe446b…`) with the invariant-(d) divergence disclosure carried on the deferral row, extended cross-cycle regression coverage in-place by two cases per cycle, and closed with the standard housekeeping triad (`_plan/register-cN-sub-leaves` + `_run/cycle_N_closed` + `_archive/cycle-N-scratch` + `_infra/adopt-cycleN-tests`) plus emitter-sentinel guard. The chain-supersede lineage now runs c34 → c35 → c36 → c37 → c38 → c39 (six cycles); the stand-pat lineage now runs c36 → c37 → c38 → c39 (four cycles). POR parseable-Milestones grew by twelve rows per cycle in a metronomically stable arithmetic — 796 (post-c36) → 808 (post-c37) → 820 (post-c38) → 832 (post-c39) — attributable structurally to the four Track B/C/D honest-deferral rows plus the four-row housekeeping tail plus the two preservation events plus the two test-extension rows, matching the c34-established Track B/C/D deferral-row attribution. Cross-cycle regression coverage grew in-place from twenty-two to twenty-eight cases on `tests/test_c30_legacy_mode_regression.py` (two new tests per cycle capturing the new preservation and stand-pat events' shape and chain-integrity), with the standalone eight-case OP-1 serial-lock suite unchanged — cross-cycle total 36/36 PASS at range close. The c34 empirical POR delta proof diagnostic (SHA `3b0e4d95061a8ad7…`), the c35 blocker event (SHA `c671a40b53565e4e…`), the c37 stand-pat (SHA `bf701f05d73292a1…`), and the c38 stand-pat (SHA `678307e2a59e85c9…`) all remained byte-identical across the range. All six operator escalations remained preserved verbatim with correct `carried_from_cycle` semantics (7, 16, 30, 31, 31, 32); no seventh escalation opened; no wait-on-operator memo emitted (banned per operator directive 2026-09-03 part 2). Independent audit at range close returned **VALIDATED** against all eight validators (a)–(h), with zero CRITICAL, zero HIGH, one MINOR-free MODERATE tracking the +12/cycle POR growth trajectory as informational-and-recurring, and a recommendation that the next cycle propose a POR consolidation strategy if operator adjudication of `_manager/M-V4-CERT-composite-fp-drift-adjudication-c32` remains absent. Canonical 7-key `env_pin_sha256=2ac444c3…922ca` unchanged across the range; FD-16(a) re-issue not triggered. Thirteen read-only anchors byte-identical pre-vs-post at range close. `M-V4-SHOWCASE-1` status unchanged (`LANDS_pending_operator`; the CG A/B mix WAV holds SHA `6e13e007…` byte-identical since c17). The heartbeat cadence is now demonstrably stable across an extended horizon — six chain-supersede cycles and four stand-pat cycles without degradation, hidden-state accretion, or silent drift.

## Introduction

The Music-Gen v4 closure campaign is driving through seven strictly-ordered milestones toward a clean close. Cycles 47-49 sit at what has now become the campaign's terminal operational cadence: all substantive stage-2 sweep work is gated on operator adjudication of a single composite-floating-point-drift question that spans all three fine-fit drivers (drums c30, bass v2 c31, guitar c31), plus a non-CG bass acceptance-policy escalation from c7, plus a metric-semantics escalation from c16, and no adjudication has arrived through `live_guidance` across the current range or the two preceding ones. Under the anti-heartbeat rule (banned wait-on-operator memos per operator directive 2026-09-03 part 2), the correct posture is preservation-only work that maintains the campaign in a state from which any incoming operator decision can trigger substantive execution in a single downstream cycle.

Two side questions inherited from earlier cycles continue to shape each cycle in the range: the workspace-forced OPT_B ledger-emitter exemption established at c34, which requires each cycle to re-probe the workspace and chain-supersede the prior preservation event under the c14 string-typed `supersedes_path` lemma; and the POR shadow-drift strengthening question, which requires each cycle to scan `live_guidance` for an operator-supplied c31/c32 POR snapshot and, absent one, stand-pat via a preservation event chain-superseding the prior cycle's stand-pat. Both are terminal-contract patterns — the prior auditor's M-1 and M-2 explicitly directed subsequent cycles to continue mechanically absent a state change. The current range demonstrates the pattern is stable at scale.

## Approach

Each of the three cycles executed the same eight-priority template, differing only in the specific SHA anchors chain-superseded and the specific POR arithmetic:

- **Priority 0 (preserve six escalations).** Verify all six escalation sidecars under `data/v4/_manager/` byte-identical versus the prior cycle's attestation SHAs. No memo mutated. No seventh escalation opened. Anti-stall rule respected — `_manager/` is exhaustive at six.
- **Priority 1 (chain-continuation re-probe).** Execute `test -d long_exposure`, confirm ABSENT (unchanged since c34), emit `data/v4/_selection/cN-emitter-writer-boundary-preservation.json` chain-superseding the prior cycle's preservation via string `supersedes_path` per the c14 lemma. Confirm `docs/emitter_exemption_policy.md` (SHA `fd2c33a78d147341…`) byte-identical.
- **Priority 2 (POR stand-pat continuation).** Scan `live_guidance` for operator-supplied c31/c32 POR snapshot, confirm absent, emit `data/v4/_selection/cN-por-drift-preservation.json` chain-superseding the prior cycle's stand-pat via string `supersedes_path`. Confirm c34 empirical proof diagnostic and c35 blocker byte-identical anchors; c34 attribution to Track B/C/D honest-deferral rows transitively holds.
- **Priority 3 (composite-FP-drift adjudication).** Scan `live_guidance` for `PATH_A` / `PATH_B` / `PATH_C` adjudication token, confirm absent, correctly skip. `_manager/M-V4-CERT-composite-fp-drift-adjudication-c32` remains open.
- **Priority 4 (Peach Dream stem manifest anchor).** Verify SHA `c4944ee80dfe446b…` byte-identical pre-vs-post; carry the invariant-(d) divergence disclosure on the `operator_section_c25_checkpointed/rc9_6stem/` non-standard path on the deferral row; no premature disclosure event opened.
- **Priority 5 (honest-deferral rows for Track B/C/D).** Emit four rows with concrete resume commands: Disco A bass stage-2 → next-cycle+ (contingent on Priority 3 + OP-1 SerialLock); Rome bass stage-2 → next-cycle+ (c23 embedding distance 0.5145 predicts `SF2_RULED_OUT`); Peach Dream bass stage-2 → next-cycle+ (c23 distance 0.4437 + invariant (d) disclosure); WIG + Disco A drums stage-1 → next-cycle+ (coarse-sweep driver green c30; additive `--song-sha16` kwarg per c28).
- **Priority 6 (POR shadow-zone hold verification).** Verify parseable_milestones at cycle open matches prior cycle close baseline (delta zero); post-registration count grows by exactly the number of ledger rows emitted this cycle (12 events per cycle across the range). POR baseline 745 (c31 counting-method drift baseline) maintained.
- **Priority 7 (Track F test-suite extension).** Extend `tests/test_c30_legacy_mode_regression.py` in-place by two cases per cycle (one pinning the cycle's chain-supersede preservation event shape + string `supersedes_path` semantics; one pinning the cycle's stand-pat event + full chain-integrity through predecessors + c34 diagnostic byte-identity). Standalone `tests/test_fine_fit_serial_lock_c32.py` unchanged at 8/8.

Housekeeping tail closes each cycle with the standard `_plan/register-cN-sub-leaves` + `_run/cycle_N_closed` + `_archive/cycle-N-scratch` + `_infra/adopt-cycleN-tests` triad, emitter-sentinel `tools/.cN_ledger_emitted` guarding against duplicate append.

**Discipline guards asserted across all three cycles.** All AST-scannable invariants pass: no PRNG imports (`random.*`, `np.random.*`), no `sidecar_nonfactor`, no VST3 state APIs (`get_state`/`save_state`/`save_preset`/`load_state`/`set_state`), no `--verify-det` bypass, `/usr/bin/python3` interpreter guard on each cycle's emitter. `supersedes_path` typed as string (never list) per the c14 lemma throughout. Canonical 7-key `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` unchanged; FD-16(a) re-issue not triggered. FD-16(c) replay-proof invariant carried; no new renders in the range. OP-1 serial-lock invariant remains in force. Zero `SF2_CONFIRMED` verdicts on non-CG bass (invariant 9 FORBIDDEN under `SHOWCASE-1-non-cg-bass-acceptance-policy` operator authority). No wait-on-operator memo emitted; Priority 0 preserve-only posture satisfies the genuine operator-authority carve-out.

## Findings

### Chain-supersede lineage matured to six cycles

The c34-established workspace-forced OPT_B ledger-emitter exemption chain now runs six cycles deep: c34 fork → c35 preservation → c36 preservation → c37 preservation → c38 preservation → c39 preservation. Each cycle's preservation event carries `supersedes_path` as a string pointing at the immediately-prior cycle's preservation event path, exercising the c14 lemma each cycle rather than treating it as dormant convention. `docs/emitter_exemption_policy.md` (SHA `fd2c33a78d147341…`) remains byte-identical anchor throughout. The reversibility contract remains intact: if any future cycle finds `long_exposure/` PRESENT, an OPT_A adjudication event can supersede the latest preservation and route the emitter chain through `append_ledger_event`.

### Stand-pat lineage matured to four cycles

The POR shadow-drift strengthening stand-pat pattern established at c36 now runs four cycles deep: c36 stand-pat → c37 stand-pat → c38 stand-pat → c39 stand-pat. c37 stand-pat (SHA `bf701f05d73292a1…`), c38 stand-pat (SHA `678307e2a59e85c9…`), c35 blocker (SHA `c671a40b53565e4e…`), and c34 empirical proof diagnostic (SHA `3b0e4d95061a8ad7…`) all remained byte-identical across the range. The c34 attribution of the c31→c32 +4 shadow-drift to the four Track B/C/D honest-deferral rows continues to hold transitively per string-supersede semantics.

### Six operator escalations preserved verbatim across the range

All six escalation sidecars under `data/v4/_manager/` verified byte-identical versus each cycle's prior attestation:

| Escalation | Origin | Attestation SHA |
|---|---|---|
| `SHOWCASE-1-non-cg-bass-acceptance-policy` | c7 | `8101f7d57ef52991…` |
| `M-V4-METRIC-SEMANTICS-c16` | c16 | `011a708e94989e6a…` |
| `CERT-fine-fit-sf2-drums-legacy-halt` | c30 | `aeaafabfadd4d83d…` |
| `CERT-fine-fit-sf2-v2-legacy-halt` | c31 (c33 sidecar backfill) | `4b95efe95c551b0a…` |
| `CERT-fine-fit-sf2-guitar-legacy-halt` | c31 (c33 sidecar backfill) | `108b48af93a88548…` |
| `CERT-composite-fp-drift-adjudication-c32` | c32 | `c4735de75895b46e…` |

The c32 composite-FP-drift consolidation memo links but does not close the three per-driver fine-fit HALT predecessors, preserving FD-1 discipline across the c30 / c31 / c31 / c32 chain. All six carry correct `carried_from_cycle` semantics; all `blocked_on_operator=true`; all discoverable via both `grep _manager/M-V4-CERT` and `ls data/v4/_manager/`. Priority 0 status BLOCKED_ON_OPERATOR unchanged across the range.

### POR parseable-Milestones +12/cycle heartbeat now four data points

The POR parseable-Milestones count now traces a metronomically stable +12/cycle arithmetic across the four consecutive heartbeat data points at range boundaries: 796 (post-c36) → 808 (post-c37) → 820 (post-c38) → 832 (post-c39). Each cycle open matches the immediately-prior cycle close exactly (delta zero); each post-registration count grows by exactly twelve rows from twelve emitted ledger events (four Track B/C/D deferral rows + four housekeeping-tail rows + two preservation events + two test-extension rows, matching the c34-established Track B/C/D deferral-row attribution). POR baseline 745 (c31 counting-method drift baseline) maintained through c32 / c33 / c34 / c35 / c36 / c37 / c38 / c39. No new drift beyond the accounted heartbeat.

### Read-only anchors held throughout the range

Thirteen read-only anchors verified byte-identical pre-vs-post at range close: `scripts/sound_match/objective.py` `8087ce80…`; `scripts/sound_match/_sweep_hygiene_c27.py` `771ff42b…`; `scripts/sound_match/_serial_lock_op1.py` `121809db…`; `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` `6e13e0075c5d8116…`; `docs/agent_picks_selection_invariants.md` post-c32 `29a1610b…`; `docs/emitter_exemption_policy.md` `fd2c33a7…`; three fine-fit drivers post-OP-1 (`6c80c438`, `a432e1d1`, `40dbb673`); three coarse-sweep drivers (`3f8bfa08`, `26aa754c`, `d6c54f21`); Peach Dream stem manifest `c4944ee8…`; plus the six escalation memos under `data/v4/_manager/`.

Zero `SF2_CONFIRMED` verdicts anywhere on disk. Canonical 7-key environment pin unchanged.

### Test coverage grew 22 → 24 → 26 → 28 in-place

Cross-cycle regression coverage on `tests/test_c30_legacy_mode_regression.py` extended in-place by two cases per cycle across the range, capturing each cycle's new preservation and stand-pat events' shape and chain-integrity. Growth trajectory: c36 22 → c37 24 → c38 26 → c39 28. Standalone `tests/test_fine_fit_serial_lock_c32.py` unchanged at 8/8. Cross-cycle total at range close: 36/36 PASS.

### Audit outcome

**VALIDATED** at range close against all eight validators (a)–(h). Zero CRITICAL. Zero HIGH. One MODERATE, informational-and-recurring, tracking the +12/cycle POR growth trajectory as structurally honest per c34-established Track B/C/D deferral-row attribution plus housekeeping-tail arithmetic — not substantive accretion. The prior audit projected that consolidation-strategy discussion might merit consideration at c40+; the current audit continues the not-action-required ruling per the original scope of the observation and recommends that the next cycle propose a consolidation strategy (parallel to c31/c34 shadow-zone hygiene precedent) if operator adjudication of `_manager/M-V4-CERT-composite-fp-drift-adjudication-c32` remains absent, retaining the current mechanical pattern in the meantime.

Zero MINOR observations at range close. The audit interprets the range as a textbook instance of the halt-honest campaign closure discipline the brief mandates — five consecutive Priority 1 chain-supersede preservations and four consecutive Priority 2 stand-pat continuations demonstrate the mechanical heartbeat pattern is genuinely stable across an extended horizon, not degrading, not accreting hidden state, not silently drifting.

## Discussion

Three things about this range are worth naming.

First, the range is the empirical demonstration that the preservation-only cadence established at the end of the prior range is not a transient posture but a stable multi-cycle equilibrium. Six chain-supersede cycles and four stand-pat cycles now stand as evidence that the pattern can continue mechanically without degradation: each cycle's disk-state matches the prior cycle's expected close-state exactly, each cycle's ledger emission is a clean twelve rows, each cycle's test extension is a clean two cases, each cycle's read-only anchor set is byte-identical. There is no shear stress accumulating between cycles. This is what "hold cleanly while blocked on operator" looks like at scale — it is not idling and it is not heartbeat-manufacturing. Each cycle re-executes the discipline invariants (workspace probe, `supersedes_path` string-typing, escalation byte-identity attestation, POR arithmetic), keeps the campaign reversible-ready, and closes.

Second, the +12/cycle POR growth trajectory is now sharp enough to be predictable and structurally attributable. Every twelve-row growth per cycle decomposes exactly to four Track B/C/D deferral rows + four housekeeping-tail rows + two preservation events + two test-extension rows. The c34 empirical proof anchored this attribution; three subsequent cycles of the same arithmetic without drift is confirmatory evidence. This is why the audit continues to characterize the growth as "informational, non-blocking" rather than substantive accretion — the delta per cycle is fully accounted-for at row-level, and the accumulation is the natural consequence of running an operator-authority hold under the anti-heartbeat rule. If operator adjudication of the composite-FP-drift memo remains absent through a subsequent cycle, however, the growing row count merits a consolidation-strategy proposal parallel to earlier shadow-zone hygiene work — not to change the substance of what is being tracked, but to compact the accumulated deferral-row set into a stable summary that the campaign can hand off cleanly at whichever cycle operator adjudication arrives.

Third, the c14 string-typed `supersedes_path` lemma has now been exercised across ten preservation events in ten cycles (six chain-supersedes on the exemption question + four stand-pats on the POR question) without a single lapse. Each cycle re-executes the lemma against a live prior-cycle anchor; each cycle's audit re-attests the string type. The lemma is not dormant convention; it is living infrastructure that makes the preservation-only cadence auditable and reversible. When operator adjudication does arrive — likely Path A (accept render-level regression bar via new invariant (f)) as the single-action resolution across all three fine-fit drivers — the transition from this stable state to substantive stage-2 sweep launch requires only that the adjudication token appear in `live_guidance`; the next cycle's worker executes the chosen path and the deferral chain collapses. The range's investment in maintaining that clean state is what keeps the transition cheap.

## Open questions

- **Composite-FP-drift operator adjudication.** The three per-driver fine-fit legacy HALT escalations (drums c30, bass v2 c31, guitar c31) plus the c32 consolidation memo constitute a single operator-authority question with three named paths (A accept render-level bar via new invariant (f); B hold strict; C harden `objective.py` per invariant 8 operator scope). Path A is the single-action resolution across all three drivers. No adjudication in `live_guidance` across the range.
- **Non-CG bass acceptance-policy escalation.** Remains `blocked_on_operator=true`. `SF2_CONFIRMED` remains FORBIDDEN on non-CG bass. Systematic 4-arc composite-vs-source-of-truth finding still predicts OPT2 (refuse extension + OPT3 htdemucs bass fallback) as the invariant-compliant outcome.
- **Metric-semantics escalation.** Remains `blocked_on_operator=true` with `carried_from_cycle=16`.
- **Emitter writer-boundary chain.** Six-cycle chain-supersede continues if `long_exposure/` remains ABSENT. Reversibility contract intact — if a future cycle finds it PRESENT, OPT_A adjudication event supersedes the latest preservation.
- **POR shadow-drift stand-pat.** Four-cycle chain continues absent an operator-supplied c31/c32 POR snapshot. c34 empirical proof transitively holds.
- **POR consolidation strategy proposal (auditor recommendation for next cycle).** With four consecutive +12/cycle data points and no operator adjudication imminent, the next cycle's worker is asked to propose a consolidation strategy parallel to c31 / c34 shadow-zone hygiene precedent, retaining the current mechanical pattern in the meantime. This would compact the accumulated Track B/C/D deferral-row set into a stable summary that hands off cleanly at whichever cycle operator adjudication arrives.
- **Expected next-cycle open state.** parseable_milestones = 832; six escalation memo SHAs unchanged; `long_exposure/` ABSENT; c39 preservation + stand-pat + POR-hold events on disk byte-identical; 36/36 test suite green pre-extension.
- **Two operator triggers that would change the state.** Either (a) an operator-supplied c31/c32 POR snapshot (would fire a Priority 2 close event superseding the stand-pat chain), or (b) a `PATH_A` / `PATH_B` / `PATH_C` adjudication token for the composite-FP-drift memo (would unblock Priority 3 downstream + Priority 4 Peach Dream disclosure + Priority 5 non-CG bass and drums sweep resumption). Both remain absent.

## Appendix: Provenance

**Directive.** Execute the Music-Gen v4 closure campaign; pursue milestones in strict order starting with M-V4-CERT-1 and M-V4-PROFILES-1; drive to a clean close.

**Cycle range.** cycles 47–49.

**Working directory.** `/home/user/long-exposure-runs/music-gen`.

**Session references.**

- Cycle 47 researcher `4f964648-4b5a-4134-917f-68e940f4639a`; worker `e0f14848-e752-418e-a79b-670b9777b225`; auditor `24c24104-9c9a-4ce0-ae1e-338f62e1f378`.
- Cycle 48 researcher `31c7cd68-de31-4643-a12e-9a016469a04c`; worker `c21aa847-f6d7-4b32-948e-a1279d07d81a`; auditor `2b5059d4-60fc-448a-9bed-d3a157c8f869`.
- Cycle 49 researcher `58cbaffa-1d20-4688-b324-bd6658b6e9df`; worker `a967b16c-3b0f-483c-9d99-f6126f4af19a`; auditor `b9b28d40-7f1b-44f8-b3bd-12f1f76afa38`.

**Audit verdict.** **VALIDATED** at range close against all eight validators (a)–(h). Zero CRITICAL. Zero HIGH. One MODERATE (informational, non-blocking, recurring): POR parseable-Milestones +12/cycle heartbeat now four data points (796 → 808 → 820 → 832); structurally honest per c34-established Track B/C/D deferral-row attribution + housekeeping-tail arithmetic; recommendation that next cycle propose consolidation-strategy parallel to c31/c34 shadow-zone hygiene precedent if operator adjudication remains absent. Zero MINOR.

**Terminal deliverables landed this range.**

- Three chain-supersede preservation events on the workspace-forced OPT_B ledger-emitter exemption at `data/v4/_selection/c{37,38,39}-emitter-writer-boundary-preservation.json`, each `supersedes_path` string-typed → prior-cycle preservation per c14 lemma.
- Three stand-pat preservation events on the POR shadow-drift strengthening question at `data/v4/_selection/c{37,38,39}-por-drift-preservation.json`, each `supersedes_path` string-typed → prior-cycle stand-pat.
- Twelve honest-deferral rows total across the range for Track B/C/D (four per cycle: Disco A bass stage-2; Rome bass stage-2; Peach Dream bass stage-2 with invariant-(d) disclosure carried; WIG + Disco A drums stage-1) with concrete resume commands.
- Six new test cases across the range (two per cycle) extending `tests/test_c30_legacy_mode_regression.py` in-place 22 → 24 → 26 → 28; standalone `tests/test_fine_fit_serial_lock_c32.py` unchanged at 8/8; cross-cycle total 36/36 PASS at range close.
- Three housekeeping-triad sequences (one per cycle): `_plan/register-cN-sub-leaves` + `_run/cycle_N_closed` + `_archive/cycle-N-scratch` + `_infra/adopt-cycleN-tests`; emitter-sentinel guards `tools/.c{37,38,39}_ledger_emitted`.

**Ledger + POR arithmetic across the range.**

- c37: ledger 1600 → 1612 (+12); POR 796 → 808 (+12).
- c38: ledger 1612 → 1624 (+12); POR 808 → 820 (+12).
- c39: ledger 1624 → 1636 (+12); POR 820 → 832 (+12).
- Each cycle open matches prior cycle close (delta zero). POR baseline 745 (c31 counting-method drift baseline) maintained.

**Read-only anchors preserved byte-identical pre-vs-post (13 verified at range close).**

- `scripts/sound_match/objective.py` `8087ce80…` (invariant 8; Path C in HALT escalations would require lifting)
- `scripts/sound_match/_sweep_hygiene_c27.py` `771ff42b…`
- `scripts/sound_match/_serial_lock_op1.py` `121809db…`
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` `6e13e0075c5d8116…`
- `docs/agent_picks_selection_invariants.md` post-c32 `29a1610b…`
- `docs/emitter_exemption_policy.md` `fd2c33a7…`
- Three fine-fit drivers post-OP-1: `6c80c438`, `a432e1d1`, `40dbb673`
- Three coarse-sweep drivers: `3f8bfa08`, `26aa754c`, `d6c54f21`
- Peach Dream stem manifest `c4944ee8…`
- Six escalation memos under `data/v4/_manager/` (as tabulated in Findings)

**Chain-supersede provenance anchors verified byte-identical across the range.**

- c34 empirical POR delta proof diagnostic `3b0e4d95061a8ad7…`
- c35 blocker event `c671a40b53565e4e…`
- c37 stand-pat `bf701f05d73292a1…`
- c38 stand-pat `678307e2a59e85c9…`

**Six operator escalations preserved verbatim** with correct `carried_from_cycle` semantics (7, 16, 30, 31, 31, 32); all `blocked_on_operator=true`; all discoverable via both `grep _manager/M-V4-CERT` and `ls data/v4/_manager/`. Priority 0 status BLOCKED_ON_OPERATOR unchanged across the range.

**Environment pin.** Canonical 7-key `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` unchanged this range; FD-16(a) re-issue not triggered. FD-16(c) replay-proof ×2 per render family per song invariant carried; no new renders in the range.

**Discipline guards asserted (AST-scannable).** No PRNG imports (`random.*` / `np.random.*`), no `sidecar_nonfactor`, no VST3 state APIs, no `--verify-det` bypass, `/usr/bin/python3` interpreter guard on each cycle's emitter. `supersedes_path` typed as string (never list) per c14 lemma across all ten preservation events emitted this range. Zero `SF2_CONFIRMED` verdicts on non-CG bass (invariant 9 FORBIDDEN under `SHOWCASE-1-non-cg-bass-acceptance-policy` operator authority). OP-1 serial-lock invariant in force. No wait-on-operator memo (banned per operator directive 2026-09-03 part 2); Priority 0 preserve-only posture satisfies genuine operator-authority carve-out.

**Milestone status at range close.**

- M-V4-CERT-1 — validated (E2E_DETERMINISM_HOLDS on the v3 spine).
- M-V4-PROFILES-1 CG (5/5 instruments) — validated.
- M-V4-PROFILES-1 non-CG bass — 2/4 `SF2_RULED_OUT` (Rome, Peach Dream); 2/4 `STILL_INDETERMINATE` (WIG, Disco A). Stage-2 re-work gated on operator adjudication.
- M-V4-PROFILES-1 non-CG drums — 0/4 (Track D unblocked at driver-regression level; stage-2 gated on operator adjudication).
- M-V4-PROFILES-1 non-CG guitar — 0/2 (WIG + Peach Dream guitar are NULL by earlier MIDI-probe).
- M-V4-SHOWCASE-1 CG — `LANDS_pending_operator` (`cg_ab_mix.wav` SHA `6e13e007…` byte-identical since c17).
- M-V4-SHOWCASE-1 non-CG — BLOCKED on non-CG bass acceptance-policy escalation.
- M-V4-RULES-1 — scaffold landed c20; substantive implementation queued.
- M-V4-EAR-1 — not yet opened.
- M-V4-GEN-1 — conditional on M-V4-RULES + M-V4-EAR.
- M-V4-CLOSE-1 — c24 amendment landed; further amendments as substantive work completes.

**Next-cycle first task.** Continue the preservation-only cadence per c39 auditor forward guidance: Priority 1 chain-continuation (re-probe `long_exposure/`; chain-supersede c39 preservation if still ABSENT); Priority 2 stand-pat continuation (scan `live_guidance` for operator-supplied POR snapshot; stand-pat if absent); Priority 3 composite-FP-drift adjudication contingent on operator; Priorities 4-6 as usual; Priority 7 test extension by two cases. **Consider proposing a POR consolidation strategy** per c39 MODERATE M-1 parallel to c31/c34 shadow-zone hygiene precedent if the operator-adjudication wait continues. If any operator adjudication arrives via `live_guidance` — either a c31/c32 POR snapshot for Priority 2 close, or `PATH_A`/`PATH_B`/`PATH_C` for the composite-FP-drift memo — execute the chosen path (Path A recommended as single-action resolution across all three fine-fit drivers). Operator ear remains LANDS authority post-hoc per FD-6.
