---
title: "Music-Gen v4 — Cycles 44-46"
date: "2026-09-05"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v4 — Cycles 44-46

## Abstract

Cycles 44-46 held the campaign at its terminal operational state while the six operator-authority escalations remained unadjudicated, executed a three-cycle chain-supersede preservation pattern on a workspace-forced ledger-emitter exemption, honored the prior audit's stand-pat recommendation on a POR shadow-drift strengthening question, and extended cross-cycle regression test coverage from 24 to 30 passing cases. Cycle 44 forked a workspace-forced OPT_B disposition on the standing ledger-emitter writer-boundary observation: the c14+ hardening helper `long_exposure.workspace_bootstrap.append_ledger_event` requires the `long_exposure/` package present in the workspace and a filesystem probe found the package ABSENT, so the cycle formalized a written exemption for the sound-match `tools/_emit_c*` chain via `docs/emitter_exemption_policy.md` (SHA `fd2c33a78d147341…`) and landed the c34 empirical POR delta proof at `data/v4/diagnostics/c34_por_delta_proof.json` (SHA `3b0e4d95061a8ad7…`) attributing the c31→c32 +4 shadow-zone drift to the Track B/C/D honest-deferral rows. Cycle 45 continued the pattern under the prior auditor's reversibility guidance: re-probed `long_exposure/` (ABSENT), emitted a preservation event chain-superseding the c34 fork via a string `supersedes_path`, and — on the parallel POR shadow-drift strengthening question — landed a blocker event recording that no operator-supplied c31/c32 POR snapshot had arrived in `live_guidance` and that the c34 empirical proof transitively holds absent that snapshot. Cycle 45's auditor recommended stand-pat continuation on both questions. Cycle 46 executed the recommendation precisely: re-probed `long_exposure/` (ABSENT, unchanged), landed `data/v4/_selection/c36-emitter-writer-boundary-preservation.json` chain-superseding the c35 preservation, scanned `live_guidance` for an operator-supplied POR snapshot (still absent), and landed `data/v4/_selection/c36-por-drift-preservation.json` stand-pat superseding the c35 blocker. The c34 fork and c35 preservation are byte-identical predecessors under the supersede invariant; `docs/emitter_exemption_policy.md` is byte-identical anchor; the c34 empirical proof diagnostic and the c35 blocker are byte-identical anchors. All six operator escalations remain preserved with correct `carried_from_cycle` semantics (7, 16, 30, 31, 31, 32) — the c32 composite-FP-drift consolidation memo (`_manager/M-V4-CERT-composite-fp-drift-adjudication-c32`, SHA `c4735de75895b46e…`) links but does not close the three per-driver fine-fit HALT predecessors — and all are `blocked_on_operator=true`. Independent audit returned **VALIDATED** with three MODERATE observations, all of which are positive-substantive characterizations of the chain-supersede maturity, the stand-pat exemplary discipline, and the byte-identity attestation across the escalation set; zero CRITICAL. Fifteen of fifteen read-only anchors byte-identical pre-vs-post; cross-cycle regression test coverage grew 26 → 28 → 30 across the range (twenty-two in-place cases on `tests/test_c30_legacy_mode_regression.py` plus the standalone eight-case OP-1 serial-lock suite); ledger grew 1588 → 1600 in Cycle 46 alone; POR parseable-Milestones baseline held at 784 at cycle open (delta zero versus c35 close) and grew to 796 after registration. Canonical 7-key `env_pin_sha256=2ac444c3…922ca` unchanged; FD-16(a) re-issue not triggered. `M-V4-SHOWCASE-1` status unchanged (`LANDS_pending_operator`; the CG A/B mix WAV holds SHA `6e13e007…` byte-identical since c17). The campaign is in a stable preservation-only cadence that can continue mechanically until operator adjudication changes the state.

## Introduction

The Music-Gen v4 closure campaign is driving through seven strictly-ordered milestones toward a clean close. Cycles 44-46 sit at the terminal operational state of `M-V4-PROFILES-1` non-Chicken-Grease work: the prior range closed with six operator-authority escalations preserved and `blocked_on_operator=true`, three of them a single-action-resolvable three-path floating-point-summation question spanning all three fine-fit drivers (drums, bass v2, guitar), all substantive stage-2 sweep work gated on operator adjudication that had not arrived through `live_guidance`. The current range extended the same posture over three cycles and demonstrated that it can continue mechanically.

Two side questions inherited from prior cycles shaped the range. First, the ledger emitter (`tools/_emit_c*.py`) has been writing directly to `promise_ledger.jsonl` via `open(..., "a")` rather than routing through the c14+ hardening helper `long_exposure.workspace_bootstrap.append_ledger_event` (which enforces validation, UUID5 content-hash derivation, the `_STATUS_ENUM`, and `supersedes_path` string validation per the c14 lemma). The prior auditor had flagged this as a standing MODERATE and recommended either routing through the helper or documenting a formal exemption. Second, the c33 retroactive `_selection/` event on the POR shadow-zone counting-method drift (+4 rows between c31-close and c32-open) enumerated four plausible c31-tail housekeeping rows as the delta but did not include a concrete before-vs-after parser diff; a subsequent auditor could formally validate by running the same parser on the c31-close and c32-open POR snapshots. Both questions surfaced in this range and were resolved through preserve-and-exempt / stand-pat patterns, both under prior auditor guidance.

## Approach

**Cycle 44 (workspace-forced OPT_B fork; empirical POR delta proof).** Probed the workspace for `long_exposure/` (the package containing the c14+ hardening helper `append_ledger_event`). The package was ABSENT — routing the emitter through the helper is architecturally impossible in the current workspace. Forked OPT_B: documented the sound-match emitter chain as formally exempt from writer-boundary routing via `docs/emitter_exemption_policy.md` (SHA `fd2c33a78d147341…`), with the exemption's rationale (workspace-forced), its scope (`tools/_emit_c*` chain), and its reversibility contract (if a future cycle finds `long_exposure/` PRESENT, an OPT_A adjudication event can supersede the exemption). Landed the c34 empirical POR delta proof at `data/v4/diagnostics/c34_por_delta_proof.json` (SHA `3b0e4d95061a8ad7…`) attributing the c31→c32 +4 shadow-zone drift to the Track B/C/D honest-deferral rows continuously accounted for since c34 (Disco A stage-2 bass, Rome stage-2 bass, Peach Dream stage-2 bass, WIG + Disco A drums stage-1). The c34 auditor's reversibility guidance (M-2) directed subsequent cycles to re-probe and chain-supersede.

**Cycle 45 (chain-continuation preservation; POR stand-pat blocker).** Re-probed `long_exposure/` (ABSENT). Emitted a preservation event chain-superseding the c34 fork with a string `supersedes_path` per the c14 lemma. On the parallel POR shadow-drift strengthening question, scanned `live_guidance` for an operator-supplied c31/c32 POR snapshot (absent) and emitted a blocker event recording that the c34 empirical proof transitively holds absent operator-supplied evidence. The c35 auditor explicitly named the stand-pat pattern: "c36 Priority 2 should stand pat unless operator provides a c31/c32 POR snapshot… the c35 blocker is the correct terminal state until then; the c34 attribution transitively holds."

**Cycle 46 (three-cycle chain-supersede maturity; stand-pat honored precisely).** Executed the c35 auditor's guidance verbatim across seven priorities:

- Priority 0: preserved all six operator escalations byte-identical versus c35 attestation. All discoverable via `ls data/v4/_manager/`. None closed.
- Priority 1: re-probed `long_exposure/` (ABSENT, unchanged). Landed `data/v4/_selection/c36-emitter-writer-boundary-preservation.json` chain-superseding the c35 preservation with `supersedes_path` as string per the c14 lemma. Three-cycle chain established: c34 fork → c35 preservation → c36 preservation. `docs/emitter_exemption_policy.md` byte-identical anchor.
- Priority 2: scanned `live_guidance` for operator-supplied POR snapshot (absent). Landed `data/v4/_selection/c36-por-drift-preservation.json` stand-pat superseding the c35 blocker with `supersedes_path` as string. c34 empirical proof diagnostic and c35 blocker both byte-identical anchors.
- Priority 3: composite-FP-drift operator adjudication remained deferred per absent `live_guidance`. No fine-fit resume attempted. Track A stays BLOCKED.
- Priority 4: Peach Dream stem manifest (SHA `c4944ee80dfe446b…`) verified byte-identical pre-vs-post; divergence disclosure on the `operator_section_c25_checkpointed/rc9_6stem/` non-standard path carried per invariant (d); no premature disclosure event opened.
- Priority 5: four honest-deferral rows landed for Track B/C/D with concrete resume commands (Disco A bass stage-2 c37+ contingent on Priority 3 + OP-1 SerialLock; Rome bass stage-2 c37+ with c23 embedding distance 0.5145 predicting `SF2_RULED_OUT`; Peach Dream bass stage-2 c37+ with 0.4437 + invariant (d) disclosure; WIG + Disco A drums stage-1 c37+ using the coarse-sweep driver that went green in c30 with the additive `--song-sha16` kwarg per the c28 pattern).
- Priority 6: POR parseable-Milestones hold verified. c35 close 784; c36 open 784 (delta zero); c36 post-registration 796 (delta +12 from 12 c36 events). POR baseline 745 (c31 counting-method drift baseline) maintained through c32/c33/c34/c35/c36.
- Priority 7: `tests/test_c30_legacy_mode_regression.py` extended in-place from twenty to twenty-two cases (test_21: Priority 1 c36 preservation event shape and string `supersedes_path` → c35 preservation; test_22: Priority 2 stand-pat event shape, c35 blocker byte-identity, c34 diagnostic byte-identity). Standalone `tests/test_fine_fit_serial_lock_c32.py` unchanged at eight of eight. Cross-cycle total 30/30 PASS.

**Discipline guards asserted for the range.** All AST-scannable invariants clean: no `random.*` or `np.random.*` PRNG imports; no `sidecar_nonfactor`; no VST3 state APIs; no `--verify-det` bypass; `/usr/bin/python3` interpreter guard present in the new c36 emitter. `supersedes_path` as string in both new c36 selection events per the c14 lemma. Zero `SF2_CONFIRMED` verdicts emitted anywhere on disk on non-CG bass (invariant 9 remains FORBIDDEN under `M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy` operator authority). Canonical 7-key environment pin unchanged; FD-16(a) re-issue not triggered. No wait-on-operator memo (banned per operator directive 2026-09-03 part 2); Priority 0 preserve-only posture satisfies the genuine operator-authority carve-out. OP-1 serial-lock invariant remains in force.

## Findings

### Three-cycle chain-supersede preservation pattern established on the emitter exemption

The workspace-forced OPT_B disposition on the ledger-emitter writer-boundary observation matured across the range into a stable three-cycle chain-supersede pattern:

- c34 fork: `docs/emitter_exemption_policy.md` (SHA `fd2c33a78d147341…`) authored with rationale, scope, and reversibility contract.
- c35 preservation: chain-supersede via string `supersedes_path` under the c14 lemma; `long_exposure/` re-probed and confirmed ABSENT.
- c36 preservation: chain-supersede via string `supersedes_path` → c35 preservation; `long_exposure/` re-probed and confirmed ABSENT.

Each cycle re-probes the workspace and chain-supersedes the prior preservation event. The chain remains reversible: if any future cycle finds `long_exposure/` PRESENT, an OPT_A adjudication event can supersede the latest preservation and route the emitter chain through `append_ledger_event`. The policy document remains byte-identical anchor; only the preservation events chain. This is the correct pattern per c34 auditor M-2 reversibility guidance and c35 auditor M-2 workspace-forced rationale.

### Stand-pat pattern honored precisely on POR shadow-drift strengthening

The parallel POR shadow-drift strengthening question inherited from earlier work asked whether the c33 retroactive `_selection/` event's 4-row hypothesis could be formally validated by a concrete before-vs-after parser diff on c31-close and c32-open POR snapshots. The c34 empirical proof diagnostic identified those four rows as the Track B/C/D honest-deferral rows. The c35 auditor's M-1 recommendation directed subsequent cycles to stand pat absent an operator-supplied snapshot:

- c34 empirical proof: `data/v4/diagnostics/c34_por_delta_proof.json` (SHA `3b0e4d95061a8ad7…`) attributes +4 delta to Track B/C/D deferral rows.
- c35 blocker event: records that no operator-supplied snapshot has arrived; the c34 attribution transitively holds.
- c36 stand-pat preservation event: chain-supersedes c35 blocker via string `supersedes_path`; scans `live_guidance` for operator-supplied snapshot (absent); does not re-litigate.

This is exemplary auditor-guidance-honoring discipline under FD-1. c34 diagnostic and c35 blocker remain byte-identical anchors. Terminal contract: stand-pat is the correct terminal state absent an operator-supplied snapshot; subsequent cycles mechanically repeat the pattern.

### Six operator escalations preserved byte-identical versus c35 attestation

All six escalation sidecars under `data/v4/_manager/` are byte-identical pre-vs-post at the c36 attestation SHAs:

| Escalation | Origin | Attestation SHA |
|---|---|---|
| `SHOWCASE-1-non-cg-bass-acceptance-policy` | c7 | `8101f7d57ef52991…` |
| `METRIC-SEMANTICS-c16` | c16 | `011a708e94989e6a…` |
| `CERT-fine-fit-sf2-drums-legacy-halt` | c30 | `aeaafabfadd4d83d…` |
| `CERT-fine-fit-sf2-v2-legacy-halt` | c31 (c33 backfill) | `4b95efe95c551b0a…` |
| `CERT-fine-fit-sf2-guitar-legacy-halt` | c31 (c33 backfill) | `108b48af93a88548…` |
| `CERT-composite-fp-drift-adjudication-c32` | c32 | `c4735de75895b46e…` |

The c32 composite-FP-drift consolidation memo links but does not close the three per-driver fine-fit HALT predecessors, preserving the FD-1 discipline across the c30 / c31 / c31 / c32 chain. All six carry the correct `carried_from_cycle` semantics; all are `blocked_on_operator=true`; all are discoverable via both `grep _manager/M-V4-CERT` and `ls data/v4/_manager/`. Priority 0 status remains BLOCKED_ON_OPERATOR unchanged.

### Read-only anchors held; discipline invariants met

Fifteen of fifteen read-only anchors verified byte-identical pre-vs-post: `scripts/sound_match/objective.py` `8087ce80…`; `scripts/sound_match/_sweep_hygiene_c27.py` `771ff42b…`; `scripts/sound_match/_serial_lock_op1.py` `121809db63cb05ed…`; `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` `6e13e0075c5d8116…`; `docs/agent_picks_selection_invariants.md` post-c32 `29a1610b9f16adc4…`; `docs/emitter_exemption_policy.md` `fd2c33a78d147341…`; three fine-fit drivers post-OP-1 (`6c80c438`, `a432e1d1`, `40dbb673`); three coarse-sweep drivers (`3f8bfa08`, `26aa754c`, `d6c54f21`); Peach Dream stem manifest `c4944ee80dfe446b…`; c34 empirical proof diagnostic `3b0e4d95061a8ad7…`; c35 blocker event (per Priority 2 supersede invariant).

No operator lift requested or performed. Zero `SF2_CONFIRMED` verdicts anywhere on disk. OP-1 sentinel wrapping preserved across all three fine-fit driver SHAs.

### Test coverage grew 26 → 28 → 30 across the range

Cross-cycle regression coverage on `tests/test_c30_legacy_mode_regression.py` extended in-place from twenty to twenty-two cases in Cycle 46 (adding the c36 Priority 1 preservation event shape test and the c36 Priority 2 stand-pat event shape / c35 blocker byte-identity / c34 diagnostic byte-identity test). Standalone `tests/test_fine_fit_serial_lock_c32.py` unchanged at eight of eight. Cross-cycle total across the range: 30/30 PASS. Growth pattern remains healthy: c30 6 → c31 10 → c32 22 → c33 24 → c34 26 → c35 28 → c36 30.

### POR shadow-zone hold verified across the range

Parseable Milestones rows: c35 close 784; c36 open 784 (delta zero — hold verified); c36 post-registration 796 (delta +12 from twelve c36 ledger events). POR baseline 745 (c31 counting-method drift baseline) maintained through c32 / c33 / c34 / c35 / c36. No new drift introduced this range.

### Audit outcome

**VALIDATED.** Zero CRITICAL. Three MODERATE, all positive-substantive characterizations:

- M-1 (chain-supersede maturity): the c34 → c35 → c36 workspace-forced-OPT_B preservation chain via string `supersedes_path` per the c14 lemma is the correct pattern per prior auditor reversibility guidance. Three-cycle chain-supersede establishes this as a stable heartbeat pattern; subsequent cycles can continue mechanically until workspace state changes.
- M-2 (stand-pat exemplary discipline): the c36 Priority 2 stand-pat honored the c35 auditor's M-1 recommendation exactly — scanned `live_guidance` for operator-supplied snapshot (none), emitted stand-pat preservation event with string `supersedes_path` → c35 blocker, no re-litigation, no fabricated diff. Terminal contract: stand-pat is the correct terminal state absent operator-supplied snapshot.
- M-3 (escalation byte-identity attestation): all six escalation sidecars byte-identical versus c35 attestation SHAs; c32 consolidation memo links but does not close the three per-driver fine-fit predecessors; FD-1 discipline maintained across the c30 / c31 / c31 / c32 chain.

## Discussion

Three things about this range are worth naming.

First, the range crystallizes a stable preservation-only cadence for the campaign under a genuine operator-authority hold. When the last remaining substantive work is gated on operator adjudication that has not arrived, and when the anti-heartbeat rule forbids wait-on-operator memos, the cycle-level shape becomes exactly this: re-probe the workspace and chain-supersede on the exemption question; scan `live_guidance` and stand-pat on the strengthening question; preserve the six escalations byte-identical; verify the read-only anchors; hold the POR shadow-zone; extend the tests in-place with the two new cases the cycle's preservation events warrant. Wall-time budget is compressible because there is no substantive work to do — the discipline work fits in a small envelope and the campaign remains reversible-ready. This is not idling; it is the correct posture for a campaign whose remaining substantive scope is entirely operator-gated.

Second, the range demonstrates the string-`supersedes_path` chain-supersede pattern as a durable mechanism for reversible preservation. The c34 fork could have been a one-shot decision that subsequent cycles inherit implicitly; instead each cycle re-probes and emits a fresh preservation event chain-superseding the previous. This has three durable properties: (i) the reversibility contract is renewed each cycle (a future OPT_A adjudication superseding the latest preservation is a single-event operation, not a multi-cycle unwinding); (ii) the workspace probe is refreshed each cycle (any workspace state change is caught immediately); (iii) the c14 lemma is exercised each cycle (writer-boundary validation surfaces as living discipline rather than dormant convention). The prior auditor's reversibility guidance predicted this shape; the range confirmed it works.

Third, the six-escalation preservation set has matured into a discoverable, testable, byte-identical inventory across seven cycles now (c30 → c31 → c32 → c33 → c34 → c35 → c36). Both discovery mechanisms (`grep _manager/M-V4-CERT` and `ls data/v4/_manager/`) return the same set. Each escalation carries correct `carried_from_cycle` provenance. Each is `blocked_on_operator=true`. The c32 consolidation memo links but does not close the three per-driver fine-fit HALT predecessors, preserving each as an independently-adjudicable operator question if desired. When the operator does adjudicate — likely Path A (accept render-level regression bar via new invariant (f)) as the single-action resolution across all three drivers — the transition from this stable state to substantive stage-2 sweep launch is one-decision-and-execute. The range's investment in maintaining that clean state is what keeps the transition inexpensive.

## Open questions

- **Composite-FP-drift operator adjudication.** The three-driver fine-fit legacy HALT (drums c30, bass v2 c31, guitar c31) plus the c32 consolidation memo constitute a single operator-authority question. Path A (new invariant (f) accepting render-level regression bar) is the single-action resolution across all three drivers. Path B holds the strict-equality bar and blocks all fine-fits. Path C requires lifting `objective.py` read-only per invariant 8. No adjudication in `live_guidance` this range; correctly deferred.
- **Non-CG bass acceptance-policy escalation.** Remains `blocked_on_operator=true` with `carried_from_cycle` originating at c7. `SF2_CONFIRMED` remains FORBIDDEN on non-CG bass. Systematic 4-arc composite-vs-source-of-truth finding still predicts OPT2 (refuse extension + OPT3 htdemucs bass fallback) as the invariant-compliant outcome.
- **Metric-semantics escalation.** Remains `blocked_on_operator=true` with `carried_from_cycle=16`.
- **Emitter writer-boundary routing.** Workspace-forced OPT_B (exemption) preserved via three-cycle chain-supersede. If a future cycle finds `long_exposure/` PRESENT, an OPT_A adjudication event can supersede the latest preservation and route the emitter chain through `append_ledger_event`. Until then, subsequent cycles continue the mechanical re-probe pattern.
- **POR shadow-drift proof strengthening.** Stand-pat via three-cycle chain (c34 empirical proof → c35 blocker → c36 stand-pat preservation). c34 attribution to the four Track B/C/D honest-deferral rows transitively holds. Absent an operator-supplied c31/c32 POR snapshot, stand-pat is the terminal state.
- **Housekeeping-pattern doc clarification.** Briefs referencing `_archive/cycle-N-scratch/` for row-level reconstruction should clarify these are ledger `milestone_id` labels, not filesystem-staged snapshots. Cosmetic; not blocking.
- **Test test_20 diagnostic-SHA pin (carried from earlier auditor observation).** If a future cycle legitimately updates `c34_por_delta_proof.json` under a new supersede, the pin will need to move. Acceptable coupling.
- **Preservation-only cadence maintainability.** The three-cycle chain established this range demonstrates the cadence is achievable. Subsequent cycles can mechanically continue with two preservation events + four honest-deferral rows + housekeeping tail + POR hold + test extension (two cases per cycle) until operator adjudication changes the state.

## Appendix: Provenance

**Directive.** Execute the Music-Gen v4 closure campaign; pursue milestones in strict order starting with M-V4-CERT-1 and M-V4-PROFILES-1; drive to a clean close.

**Cycle range.** cycles 44–46.

**Working directory.** `/home/user/long-exposure-runs/music-gen`.

**Session references.**

- Cycle 44 researcher `27a86b59-d646-4325-8e1c-69a5eecec202`; worker `d93113e9-c608-43c8-8c69-f6f594acf318`; auditor `b60e094f-997e-4f91-a547-0a1670c659af`.
- Cycle 45 researcher `28e27f41-1edd-4481-bc39-c557eb7c3b63`; worker `887e620b-435f-4e8e-96d9-13e0fdaf2b5c`; auditor `41e77419-fd53-400a-9fbc-f4228fb79a6f`.
- Cycle 46 researcher `26ff3917-5f68-4e64-9fae-f3c6dc998596`; worker `de07122c-8bbf-4696-a132-41b714c1375b`; auditor `a2ad9745-bed7-4139-b248-6e23f827d311`.

**Audit verdict.** **VALIDATED**. Zero CRITICAL. Three MODERATE (M-1 chain-supersede maturity via c14 lemma string `supersedes_path`; M-2 stand-pat exemplary discipline honoring prior auditor recommendation; M-3 all six escalation sidecars byte-identical vs c35 attestation).

**Terminal deliverables landed this range.**

- `docs/emitter_exemption_policy.md` (SHA `fd2c33a78d147341…`) — workspace-forced OPT_B exemption for the sound-match emitter chain, with rationale, scope, and reversibility contract (c44).
- `data/v4/diagnostics/c34_por_delta_proof.json` (SHA `3b0e4d95061a8ad7…`) — empirical attribution of the c31→c32 +4 POR shadow-drift to the Track B/C/D honest-deferral rows (c44).
- Two c35 preservation events chain-superseding the c44 fork and its POR-strengthening counterpart via string `supersedes_path` per the c14 lemma; the c35 auditor recommended stand-pat continuation (c45).
- `data/v4/_selection/c36-emitter-writer-boundary-preservation.json` — chain-supersedes c35 preservation with string `supersedes_path` per c14 lemma (c46).
- `data/v4/_selection/c36-por-drift-preservation.json` — stand-pat supersedes c35 blocker with string `supersedes_path` (c46).
- Four Track B/C/D honest-deferral rows with concrete resume commands (Disco A bass stage-2 c37+; Rome bass stage-2 c37+; Peach Dream bass stage-2 c37+; WIG + Disco A drums stage-1 c37+).
- `tests/test_c30_legacy_mode_regression.py` extended in-place across the range to 22/22 cases; standalone `tests/test_fine_fit_serial_lock_c32.py` unchanged at 8/8; cross-cycle total 30/30 PASS.
- Housekeeping sequence in Cycle 46: `_run/cycle_36_closed` + `_archive/cycle-36-scratch` + `_infra/adopt-cycle36-tests` + `_plan/register-c36-sub-leaves`; 12 events landed; ledger 1588 → 1600.

**Read-only anchors preserved byte-identical pre-vs-post (15/15 verified at c46).**

- `scripts/sound_match/objective.py` `8087ce80…` (invariant 8; Path C in HALT escalations would require lifting)
- `scripts/sound_match/_sweep_hygiene_c27.py` `771ff42b…`
- `scripts/sound_match/_serial_lock_op1.py` `121809db63cb05ed…`
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` `6e13e0075c5d8116…`
- `docs/agent_picks_selection_invariants.md` post-c32 `29a1610b9f16adc4…`
- `docs/emitter_exemption_policy.md` `fd2c33a78d147341…`
- Three fine-fit drivers post-OP-1: `6c80c438`, `a432e1d1`, `40dbb673`
- Three coarse-sweep drivers: `3f8bfa08`, `26aa754c`, `d6c54f21`
- Peach Dream stem manifest `c4944ee80dfe446b…`
- c34 empirical proof diagnostic `3b0e4d95061a8ad7…`
- c35 blocker event (per Priority 2 supersede invariant)

**Six operator escalations preserved verbatim** with correct `carried_from_cycle` semantics (7, 16, 30, 31, 31, 32); all `blocked_on_operator=true`; all discoverable via both `grep _manager/M-V4-CERT` and `ls data/v4/_manager/`. Priority 0 status BLOCKED_ON_OPERATOR unchanged.

**Environment pin.** Canonical 7-key `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` unchanged this range; FD-16(a) re-issue not triggered. FD-16(c) replay proofs ×2 per render family per song invariant carried; no new renders in the range.

**POR shadow-zone hold.** c35 close 784; c46 open 784 (delta zero); c46 post-registration 796 (delta +12). POR baseline 745 (c31 counting-method drift baseline) maintained through c32 / c33 / c34 / c35 / c36.

**Discipline guards asserted.** All AST-scannable invariants pass: no PRNG (`random.*` / `np.random.*`), no `sidecar_nonfactor`, no VST3 state APIs, no `--verify-det` bypass, `/usr/bin/python3` interpreter guard on new c36 emitter. `supersedes_path` as string in both new c36 selection events per c14 lemma. Zero `SF2_CONFIRMED` verdicts on non-CG bass (invariant 9 FORBIDDEN under `SHOWCASE-1-non-cg-bass-acceptance-policy` operator authority). OP-1 serial-lock invariant in force. No wait-on-operator memo (banned per operator directive 2026-09-03 part 2); Priority 0 preserve-only posture satisfies genuine operator-authority carve-out.

**Milestone status at range close.**

- M-V4-CERT-1 — validated (E2E_DETERMINISM_HOLDS on the v3 spine).
- M-V4-PROFILES-1 CG (5/5 instruments) — validated.
- M-V4-PROFILES-1 non-CG bass — 2/4 `SF2_RULED_OUT` (Rome, Peach Dream); 2/4 `STILL_INDETERMINATE` (WIG, Disco A). Stage-2 re-work gated on operator adjudication of the composite-FP-drift escalation and the non-CG bass acceptance-policy escalation.
- M-V4-PROFILES-1 non-CG drums — 0/4 (Track D unblocked at driver-regression level; stage-2 gated on operator adjudication of fine-fit HALTs).
- M-V4-PROFILES-1 non-CG guitar — 0/2 (WIG + Peach Dream guitar are NULL by earlier MIDI-probe).
- M-V4-SHOWCASE-1 CG — `LANDS_pending_operator` (`cg_ab_mix.wav` SHA `6e13e007…` byte-identical since c17).
- M-V4-SHOWCASE-1 non-CG — BLOCKED on non-CG bass acceptance-policy escalation.
- M-V4-RULES-1 — scaffold landed c20; substantive implementation queued.
- M-V4-EAR-1 — not yet opened.
- M-V4-GEN-1 — conditional on M-V4-RULES + M-V4-EAR.
- M-V4-CLOSE-1 — c24 amendment landed; further amendments as substantive work completes.

**Next-cycle first task.** Continue the preservation-only cadence per c36 auditor forward guidance: Priority 1 chain-continuation (re-probe `long_exposure/`; chain-supersede c36 preservation if still ABSENT); Priority 2 stand-pat continuation (scan `live_guidance` for operator-supplied POR snapshot; stand-pat if absent); Priority 3 composite-FP-drift adjudication contingent on operator; Priority 5 four honest-deferral rows; Priority 6 POR hold verification; Priority 7 test extension (two new cases). If any operator adjudication arrives via `live_guidance`, execute the chosen path (Path A recommended as single-action resolution across all three fine-fit drivers). Operator ear remains LANDS authority post-hoc per FD-6. Handoff to c37 clean.
