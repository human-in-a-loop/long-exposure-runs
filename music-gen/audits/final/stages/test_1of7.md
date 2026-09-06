# Test Stage 1 of 7 — Adversarial: Validators + Silent-Supersession Scan

**Delta-audit mode.** Baseline committed 2026-09-05T00:44:35Z.
Verify slices 1..7 completed with 0 net-new findings across CG cell,
non-CG bass, showcase, EAR L119, showcase v2, and CLOSE + GEN + c78 + c47.

## 1. Validators run

### promise_check
- Total ERRORs: 133
- Class breakdown:
  - **75** events "missing required field 'agent'" — spread across cycles
    49, 50, 51, 60, 61, 62, 71, 72, 73, 77, 78.
    Delta-scope (post-baseline) subset: **10 events** (c77=4, c78=6).
  - **~56** events "milestone_id not in plan_of_record.md and not in a
    reserved namespace" — includes new sentinel namespaces `_lands/`
    and `_launches/` introduced in c52+ that were never registered as
    reserved prefixes. Also several unregistered leaf paths under
    `M-V4-PROFILES-1/*-{landed,revised,corrected}-c{22..70}` and
    `M-V4-SHOWCASE-1/*-retired-c70`.
  - **2** illegal state transitions
    `_manager/M-V4-CERT-fine-fit-sf2-{v2,guitar}-legacy-halt`:
    `action_required → action_required` on c47 omnibus cascade closure
    events landing on top of pre-existing action_required. Pre-baseline
    schema; not delta-introduced.

### org_check
- 53 WARNINGs, all of shape "figure in docs/: docs/run_archive/figures/*.png
  (figures should be co-located with their source script + data, not under
  docs/)". Pre-existing structural pattern from an archival sweep;
  no delta introductions.

## 2. Silent-supersession scan (closure documents)

| Doc | mtime (UTC) | Notes |
|---|---|---|
| docs/v4_completion_report_v3.md | 2026-09-06T00:36:59Z | c77 emit + c78 amendment; verify slice 7 already confirmed pre-amendment sha `d920c93328930556…` matches POR narrative and current on-disk sha `b900b0eeadc00095…` is c78 v3.1 amendment honestly disclosed. No silent supersession. |
| docs/v4_completion_report_v2.md | 2026-09-05T21:39:07Z | c71 append landed here; c71 amendment sha `341d5bbaf859c8ca…` matches POR narrative. |
| docs/v4_closure_completion_report.md | 2026-09-05T01:07:29Z | pre-baseline; superseded by v2 via `_plan/completion-report-v2-c71-amendment`. |

No closure-doc drift without a matching `_plan/` event.

## 3. Adversarial checks — additional

- **Ledger tail schema drift** — c77-c78 events lack `agent` per
  the c47 emitter-exemption policy's practical scope creep. The
  emitter-exemption policy (`docs/emitter_exemption_policy.md`)
  requires the 8-item contract to still be honored; the on-disk
  emitters have shed the `agent` field. All other 7 items
  (event_id UUID5, status enum, str `supersedes_path`, nested
  `confidence`, canonical JSON, `run_id`, `env_pin_sha256`, `cycle`)
  are honored. This is a MODERATE hygiene finding but does not
  invalidate any content verdict.

- **New namespace drift** — `_lands/` and `_launches/` sentinel
  events emitted c52-c57 use prefixes not in the reserved
  namespace list `[_plan/, _run/, _archive/, _orphan/, _manager/, _infra/]`.
  Per `_ledger_schema.py` these fire ERROR. Pre-baseline;
  documented here for the record.

- **c47 omnibus cascade transitions** — the two illegal
  action_required→action_required transitions on the fine-fit-v2
  and fine-fit-guitar halt memos originate at c47 omnibus closure
  event emission that did not use a transition status enum bridge.
  Pre-baseline; not delta.

## 4. Findings appended this stage

**1 new MODERATE finding** appended to
`audits/final/findings.jsonl`:

- `M-V4-CLOSE-ledger-agent-field-drift-c77-c78`: 10 delta-scope
  ledger events lack the `agent` field required by
  `long_exposure/tools/_ledger_schema.py`. The events themselves
  are content-validated by verify slices; this is a schema-hygiene
  drift, not a content defect. Recommendation: c78+ emitter
  templates should re-include `agent: "worker"` field before next
  substantive cycle.

Empty parseable findings.jsonl created here for consistency with
downstream test stages.
