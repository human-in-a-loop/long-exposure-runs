# v4 POR Consolidation Strategy — c40 Proposal Doc

---
created: 2026-09-05T21:15:00Z
cycle: 40
run_id: run-2026-09-05T210000Z
agent: worker
milestone: _selection/c40-por-shadow-zone-hold
supersedes_path: null
---

**Status**: proposal-only. NEUTRAL recommendation. Operator/auditor policy call
(parallel to `_manager/M-V4-CERT-composite-fp-drift-adjudication-c32` shape).
Emitting-ledger-event `supersedes_path=null` (new artifact class per FD-1).
**No consolidation action is taken this cycle.** Any actual consolidation is
c41+ contingent on operator/auditor approval.

## §1 Problem statement

POR parseable-milestones grows at a stable **+12/cycle** across c36 → c39
(4 data points confirmed by direct `tools/_c32_por_count.py` measurement):

| Cycle | Parseable-milestones count |
|-------|---------------------------:|
| c36   | 796                        |
| c37   | 808                        |
| c38   | 820                        |
| c39   | 832                        |

Trajectory over 3 heartbeat cycles = **+36 rows** (820 − 784 stepped through
796/808/820/832 with c39-open the latest verified reading). Extrapolating the
same mechanical pattern:

| Cycle | Projected count (if pattern holds) |
|-------|-----------------------------------:|
| c40   | 832 → 845                          |
| c45   | ~905                               |
| c50   | ~952                               |

Per c39 auditor M-1: this growth is *structurally honest* under FD-1 (each row
is a legitimate ledger event with substantive `narrative` and byte-identical
predecessor anchors) and is *not substantive accretion* (no new work landed;
the deltas are Track B/C/D deferral rows + housekeeping tail + heartbeat
preservation events). Reader-cost, however, grows monotonically: at ~950 rows
the POR head section becomes progressively less scannable and slower to load
into agent context.

## §2 Attribution decomposition

Per c34 empirical proof (amended attribution) + c39 auditor M-1: each cycle's
+12 rows break down as:

| Component                                              | Rows/cycle |
|--------------------------------------------------------|-----------:|
| Priority 1 preservation event                          | 1          |
| Priority 2 stand-pat event                             | 1          |
| Priority 5 honest-deferral rows (Track B/C/D)          | 4          |
| Priority 6 POR shadow-zone hold verification           | 1          |
| Priority 7 Track F test-suite extension                | 1          |
| Housekeeping tail (register + closed + scratch + adopt)| 4          |
| **Total**                                              | **12**     |

Under FD-1 every row is defensible. Six rows (preservation + stand-pat +
POR hold + Track F + register + closed) are *structurally required per cycle*
to preserve chain-integrity and clear promise_check drift. Two rows
(scratch + adopt-tests) are housekeeping-tail bookkeeping that could be
folded into the closed-cycle rollup without semantic loss. Four rows
(Track B/C/D deferrals) are per-cycle repetitions of the same
"blocked_on_operator" statement.

## §3 Consolidation option catalog

Three named options are surfaced, following the c31 shadow-zone-hygiene
precedent shape (three named options, per-invariant compliance analysis,
NEUTRAL agent recommendation, operator decides).

### OPT_1 — Rolling-window preservation event

Emit a single **rolling-window preservation event** that supersedes the
prior K per-cycle preservation events in one supersede, fired every N
cycles (e.g., N=5). Between roll-ups, the per-cycle preservation events
continue landing as today; the rolling event lands at the end of each
window and folds them into a single supersede chain.

- **Growth impact**: reduces preservation-event accretion from +2/cycle
  (preservation + stand-pat) to ~+2/N cycles (a single rolling event
  every N cycles that supersedes N prior pairs).
- **Shape**: `_selection/c<N>-preservation-rolling-window.json` with
  `supersedes_path=str` pointing at the most-recent per-cycle preservation
  in the window; `chain_traceability` block enumerates all N predecessors
  and their SHAs (already the shape the per-cycle events use).
- **Ancestors preserved**: byte-identical (supersede is a chain edge, not
  a rewrite, per c14 lemma).

### OPT_2 — Deferral-row rollup

Replace the 4 per-cycle Track B/C/D deferral rows with **two rolling
carry-forward events**:
- `_deferred_bass_stage2_carryforward` supersedes accumulated
  `M-V4-PROFILES-1/{disco-a,rome,peach-dream}-bass-stage2-deferred-c<N>`
  rows once per K cycles.
- `_deferred_drums_stage1_carryforward` supersedes accumulated
  `M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c<N>` rows
  similarly.

- **Growth impact**: reduces deferral-row accretion from +4/cycle to
  ~+2/K cycles.
- **Shape**: identical to OPT_1's rolling-window shape, keyed on the
  specific deferral type. Between roll-ups, per-cycle deferral rows land
  as today (preserving the c40+ carry-forward audit trail).
- **Ancestors preserved**: byte-identical.

### OPT_3 — Do nothing

Accept the +12/cycle growth as first-class honest bookkeeping under FD-1.
Reader-cost is real but does not violate any binding invariant.

- **Growth impact**: unchanged (+12/cycle).
- **Shape**: no change to any pattern.
- **Ancestors preserved**: trivially.

## §4 Per-option invariant compliance

Each option is checked against the five agent-picks invariants (a)-(e)
per `docs/agent_picks_selection_invariants.md`.

### OPT_1 (rolling-window preservation)

| Invariant | Status | Rationale |
|-----------|:------:|-----------|
| (a) no operator-scope extension | PASS  | No policy change; only bookkeeping cadence changes. |
| (b) prefer above-line             | PASS  | Reduces cost without unresolving any chain edge. |
| (c) reflects definition           | PASS  | Rolling-window supersede is exactly how c14 lemma is meant to be used. |
| (d) discloses on-disk vs brief    | PASS  | Every rolled-up event is enumerated in `chain_traceability`. |
| (e) preserves canonical shape     | PASS  | Rolling event has the same shape as per-cycle preservation events. |

### OPT_2 (deferral rollup)

| Invariant | Status | Rationale |
|-----------|:------:|-----------|
| (a) | PASS | No policy change; the deferral remains blocked_on_operator. |
| (b) | PASS | Same cost reduction, applied to a different row class. |
| (c) | PASS | c14 supersede lemma applies to any row class. |
| (d) | PASS | Rolling event enumerates the per-cycle deferrals it supersedes. |
| (e) | PASS | Rolling event mirrors the deferral-row shape. |

### OPT_3 (do nothing)

| Invariant | Status | Rationale |
|-----------|:------:|-----------|
| (a) | PASS  | No change of any kind. |
| (b) | PASS  | Trivially. |
| (c) | PASS  | Trivially. |
| (d) | PASS  | Trivially. |
| (e) | PASS  | Trivially. |

## §5 Chain-integrity concern

All three options must preserve the following as byte-identical anchors
per FD-1:

- c34 empirical proof + diagnostic (`data/v4/diagnostics/c34_por_delta_proof.json`
  sha `3b0e4d95061a8ad767ce524ae9ffbe1f71fc25a9f8101cd7ed843d5599a78561`).
- c35 blocker (`data/v4/_selection/c35-por-drift-proof-strengthening-blocker.json`
  sha `c671a40b53565e4ec9ee44513474226aff8085894878e36ba4f68af544d1caad`).
- c36 → c39 stand-pat lineage (four events, all byte-identical to their
  landing SHAs).
- c34 fork → c35 → c36 → c37 → c38 → c39 preservation lineage (five events).

OPT_1 and OPT_2 rollups **supersede via `supersedes_path` as str** (never as
list) per c14 lemma, but do **NOT rewrite predecessor events**. The chain
edge is directional: the rolling event points at the most-recent per-cycle
event; every prior event remains byte-identical on disk and grep-searchable.

OPT_3 is trivially compliant (no chain edges added or removed).

## §6 Recommendation

**NEUTRAL.** This proposal doc surfaces the option catalog with honest per-
option invariant compliance analysis. The choice among OPT_1 / OPT_2 / OPT_3
is an operator/auditor policy call, NOT an agent-picks-invariants-resolvable
case (parallels the c32 composite-FP-drift consolidation memo shape).

Rationale for withholding an agent-side pick:

- Invariants (a)-(e) do not disambiguate among the three options (all PASS).
- The trade-off is between (i) reader-cost as chain length grows and
  (ii) bookkeeping-cadence complexity and audit-trail granularity. Neither
  axis has a binding-invariant answer. The trade-off weight is an operator
  preference.
- Under the anti-stall rule, agent MUST pick when invariants uniquely
  resolve. They do not. Escalating for an operator preference is
  permitted (parallel to c32 composite-FP-drift memo).

## §7 Contingent trigger — proposal scope

If operator adjudication of `_manager/M-V4-CERT-composite-fp-drift-adjudication-c32`
lands in any future cycle:

- **PATH_A landed**: fine-fit legacy-mode HALTs close terminally; Track A
  work resumes; the 4 Track B/C/D deferral rows retire as their gating
  condition dissolves. Most of the +12/cycle bookkeeping load evaporates
  organically. Consolidation becomes moot for the deferral-row axis (OPT_2
  is subsumed); preservation-event roll-up (OPT_1) still has some standing
  but with substantially reduced urgency.
- **PATH_B landed**: fine-fit arc closes as HALTED; deferral rows retire
  by absorption; same organic dissolution as PATH_A for the deferral axis.
- **PATH_C landed**: campaign HALTED per c32 escalation semantics; POR
  frozen at whatever cycle observes PATH_C; consolidation becomes an
  archival-only concern.

**Proposal scope**: this doc is scoped strictly to the *sustained-blocked*
branch (operator adjudication remains absent through c40+; heartbeat
cycles continue mechanically as at c36→c39). If adjudication lands within
1–2 cycles of c40, the operator may reasonably retire this proposal
without action.

## §8 Meta

- `docs/v4_por_consolidation_strategy_proposal_c40.md` becomes a READ-ONLY
  anchor at c41+ if operator/auditor concurs.
- The emitting ledger event carries `supersedes_path=null` (new artifact
  class; no predecessor to supersede).
- Any actual consolidation is c41+ contingent; this cycle takes no
  consolidation action per operator/auditor policy-call boundary.
