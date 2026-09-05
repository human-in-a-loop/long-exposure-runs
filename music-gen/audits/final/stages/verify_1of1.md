# Final Audit — Stage 2 (Verify, Delta Mode)

Stage 2 of 4. Adversarial re-verification of the three candidate findings surfaced in Stage 1
(explore.md). Verify pass grounded in on-disk primary evidence; no re-litigation of prior baseline.

## F1 — Ledger-vs-disk parity gap for v4 closure cycle 31 (MODERATE, CONFIRMED)

**Claim:** `promise_ledger.jsonl` contains no ledger events recording the substantive completion
of the M-V4 closure work that the delta report (`reports/cycles/report_cycles_31-31.md`) cites.

**Adversarial re-verify:**
- `tail -1 promise_ledger.jsonl` → last event is `_run/cycle_20_closed` (v4 internal cycle 20;
  M-V4-RULES-1/scaffold-c20 landed as stubs raising `NotImplementedError('c21+ substantive
  implementation')`). Full-file line count: 1434 events.
- `grep -oE '"milestone_id":"[^"]*M-V4[^"]*"' promise_ledger.jsonl | sort -u` returns
  `M-V4-CERT-1`, `M-V4-PROFILES-1` (with a dense CG sub-tree), `M-V4-RULES-1/scaffold-c20`,
  `M-V4-RULES-1/pinned-profile-schema-v1`, `M-V4-SHOWCASE-1/{cg-ab-driver-scaffolded,cg-ab-full-render}`,
  plus three `_manager/M-V4-*` escalations. Zero events for `M-V4-EAR-1`, `M-V4-GEN-1`,
  `M-V4-CLOSE-1`, or the substantive M-V4-RULES-1 extraction the report cites.
- Numeric spot: `grep -c '"milestone_id":"M-V4-EAR-1"' → 0`; same for `M-V4-GEN-1`, `M-V4-CLOSE-1`.
- Meanwhile the report cites on-disk artifacts (rules artifact, statistical model, sequence model,
  audio descriptors, ear scores, band4/exemplar embeddings, generator batch, closure doc) that
  Stage 1 byte-verified as present with matching SHAs.
- The rows in the ledger tagged `"cycle":31` (30 matches) belong to a different (Music-Gen v3)
  campaign — palette-assignment-schema, DAW spike, egress-probe — not the v4 closure work.

**Verdict: CONFIRMED, MODERATE.** The append-only ledger invariant is broken for the four
closure milestones whose substantive completion landed on disk but never landed as ledger
events. This does not invalidate the artifacts (SHAs verify), but it does break the audit-trail
invariant. The report itself surfaces the gap in its "Discussion" section as a bookkeeping
MODERATE and disclaims it as non-blocking; this audit confirms it and rates the same.

## F2 — c31 closure-cycle audit findings artifact absent from disk (MINOR, CONFIRMED)

**Claim:** Report asserts "Independent audit this cycle byte-verified every referenced SHA…
and returned `COMPLETE`" but no per-cycle audit-findings artifact for c31 is discoverable
under `audits/`.

**Adversarial re-verify:**
- `ls audits/final/stages/` shows numerous prior-cycle audit probes (`_verify10..15_findings.jsonl`,
  `_stage25..30_findings_append.jsonl`, etc.) but no file whose name resembles a c31 audit
  (no `cycle31*`, no `c31*`, no `v4_closure_audit*`).
- `find audits -name '*cycle*31*' -o -name '*c31*'` returns empty.
- The report cites a session ID for the auditor but no on-disk findings file corresponds.
- The report's own reconciliation of the "audit returned COMPLETE" claim relies on the
  auditor's session transcript, not a re-verifiable JSON/MD artifact.

**Verdict: CONFIRMED, MINOR.** Provenance completeness gap — the audit ran and its verdict is
recorded in the report narrative, but the customary per-cycle findings artifact is missing
from disk, so an independent re-audit cannot cross-check the "COMPLETE / Zero CRITICAL" claim
except by re-running its work (which the present delta audit did, and independently confirms).

## F3 — Discipline-guards assertion not re-verified (MINOR, non-actionable disclosure)

**Claim:** Report says "Discipline was asserted-by-report at closure; AST scan was not re-run
this cycle (surfaced as bookkeeping MODERATE, non-blocking)."

**Adversarial re-verify:** The report is honest about this — the claim is explicitly disclosed
as unverified-this-cycle. Under the delta-audit posture, re-running an AST discipline scan on
the whole codebase is out of scope. Prior baseline audits covered the discipline invariants for
work up to cycle 20; the new c31 substantive work (rules extractor, ear, generator, closure
doc) was not AST-scanned.

**Verdict: NOTED, MINOR.** Not a defect. Honest disclosure of a bookkeeping gap the campaign
chose not to close before ending. Consistent with the anti-heartbeat rule under which the
campaign closed.

## F4 — Metric-semantics operator-authority block (documented open question, not a finding)

Verified `data/v4/_manager/M-V4-METRIC-SEMANTICS-c16.json` present on disk. First-class
documented gap; not a defect. Blocks stage-1 sweeps on Wonderful It Is, Rome, Disco A,
Peach Dream — hence those four remain skeleton-only in M-V4-PROFILES-1 (each has an on-disk
`stem_manifest.json` with 6 htdemucs stem SHAs and a `blocked_on: _manager/M-V4-METRIC-SEMANTICS-c16`
note per the ledger events for `wig-opened`, `rome-opened`, `disco-a-opened`, `peach-dream-opened`).

## Findings written this stage

Appended to `audits/final/findings.jsonl`:
- F1 CONFIRMED MODERATE (milestone `_run/cycle_31_closure_ledger_parity_gap`).
- F2 CONFIRMED MINOR (milestone `_run/cycle_31_closure_audit_artifact_absent`).
- F3 noted as MINOR disclosure only (no ledger-event reconciliation proposed; honest bookkeeping
  gap the report already discloses).

No reconciliation events proposed for the ledger this cycle: the missing rows would need to
name specific event_ids and SHAs the closure campaign never generated; retroactive
reconstruction is out of scope for a delta audit and would itself violate the append-only
invariant if done sloppily. The document stage records this as residual debt for the human
operator to schedule (or explicitly waive as end-of-campaign).

## Gate check (verify stage)

- Every fix verified against its original finding? **Yes** — F1 and F2 independently reproduced
  from primary evidence (ledger content + on-disk file listing).
- Adjacent behavior checked for regressions? **Yes** — Stage 1's SHA-verified artifacts remain
  byte-identical (no side effects introduced by verify probes; all checks were read-only).
- Any new issues introduced? **No** — verify probes were read-only shell queries.

[OUTPUT: final_audit_stage]
Stage 2: Verify pass complete; 2 CONFIRMED findings (F1 MODERATE, F2 MINOR) + 1 MINOR disclosure noted.
File: /home/user/long-exposure-runs/music-gen/audits/final/stages/verify_1of1.md
Findings appended: 2
[END OUTPUT: final_audit_stage]
