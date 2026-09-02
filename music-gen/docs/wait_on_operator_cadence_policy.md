---
created: 2026-09-02T13:00:00Z
run_id: run-2026-09-02T130000Z
cycle: 8
agent: worker
milestone: _plan/wait-on-operator-cadence-flag
---

# Wait-on-Operator Cadence Policy

## Statement

`M-V3-SPINE-1` is `V3_SPINE_C{4,5,6,7}_..._LANDS_pending_operator` across four
consecutive cycles. Each landing is complete under the frozen three-way
`rubric_hash_v2` chain and 87-anchor byte-preservation contract, but only the
operator's ear on Chicken Grease A/B pairs flips
`blocked_on_operator: true → false` (FD-6). The only advancing move is the
operator listening to one or both of:

- **Method A** (c5 plain RMS-match):
  `data/v3/deliveries/31a164f845f8e27e/operator_section/original_ab_operator_section.wav`
  vs `.../reconstruction_ab_operator_section.wav`
  (c5 window `t = 233.639..263.639 s`).
- **Method B** (c6 iirpeak + RMS + LUFS-S):
  paired A/B slicing on
  `data/v3_spine/rc7_v2_v3_paths/rc7_v2_v3_paths_full_reconstruction.wav`.

Older delivery: c4 t = 0..30 s window at
`data/v3/deliveries/31a164f845f8e27e/{original_ab.wav, reconstruction_ab.wav}`.

## Cadence rule

From cycle 9 onward, if `[INPUT: live_guidance]` still carries no operator ear
verdict AND no operator directive naming a specific substantive follow-up, the
researcher's default cycle is a **short heartbeat cycle** — housekeeping only
plus a liveness probe:

- `M-INGEST-1/egress-probe-cycle<N>` (linear path B per c49
  `_plan/egress-retry-cadence-policy-formalized`)
- `_archive/cycle-<N>-scratch` (single emission after physical `mv`)
- `_infra/adopt-cycle<N>-tests` (bookkeeping if new tests land, else
  `artifacts=[]`)
- Re-run of the c7-landed torch-2.13 dry-run probe (path B c8 style — no
  execute, no venv touch) as a liveness signal.

No new substantive M-V3-SPINE tracks are manufactured until an operator or
auditor directive supplies one.

## Break-glass

The heartbeat cadence pauses immediately when either of the following arrives
in a cycle's inputs:

1. **Operator directive** — any operator ear verdict, follow-up ask, or
   explicit substantive-track brief in `[INPUT: live_guidance]`.
2. **Auditor CRITICAL finding** — a c8+ auditor CRITICAL that reopens a
   frozen anchor, invalidates a landed verdict, or exposes a discipline gate
   failure.

The break-glass trigger is documented in the reopening cycle's brief; the
heartbeat resumes only after the reopened work lands.

## Non-blocking

This flag does **not**:

- close `M-V3-SPINE-1` (only operator ear does that);
- invalidate `V3_SPINE_C{4,5,6,7}_..._LANDS_pending_operator` verdicts;
- halt egress-probe cadence (`M-INGEST-1/egress-probe-cycle<N>` still fires);
- freeze the anchor set (the heartbeat cycle still snapshots pre/post);
- alter FD-1 or FD-6.

## Cross-reference

- c6 auditor `Cumulative Progress Notes`: flagged three-cycle operator-absence
  pattern; asked for a formal flag if c7 also arrived without operator input.
- c7 auditor `Cumulative Progress Notes`: c7 was that flagged cycle; brief
  instructed c8 to formalize the policy if the pattern continued (it did).
- c8 brief Track 3: instructs this document.

## Cycles-since-last-operator-input

At time of writing: **4** (c5, c6, c7, c8 all substantive-track cycles without
operator ear input).
