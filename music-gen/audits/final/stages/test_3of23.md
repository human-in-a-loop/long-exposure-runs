# Final Audit — Stage 27 of 48 (Test 3 of 23)

**Stage:** test (3/23) — adversarial plan/ledger consistency + verdict-SHA spot-check
**Working dir:** `/home/user/long-exposure-runs/music-gen`
**Preceding stage:** test_2of23 (sidecar isolation, PRNG, egress-probe honesty, trigger liveness)

## Probes run this stage

1. **Orphan-milestone scan** — ledger `milestone_id` values not present on any
   plan-of-record row. Categorized by prefix.
2. **Plan/ledger consistency** — POR-listed milestones with NO firing ledger event
   (accounting for `-clone-<k>` alternates).
3. **Test-suite invocation audit** — for each `tests/test_*.py`, is there a validated
   milestone/report referencing that file?
4. **Spot-sample verdict-SHA re-check** — 4 terminal-validated milestones re-hashed
   against their `rubric_hash.txt` and `verdict.json.rubric_hash` for byte-equality.

## Findings

| # | Severity | Verdict | Summary |
|---|----------|---------|---------|
| F10 | MODERATE | CONFIRMED | `M-RECREATE-2/accurate-small-set-v2` supersede parent never emitted a ledger event; all rc7/rc8/rc9/rc10 leaves fire under the v1 tree |
| F11 | MODERATE | CONFIRMED | Four c46/c47 clone-suffixed milestones registered in POR but never fired substantively (`_archive/deprecate-c45-…-clone-2`, `_infra/pin-source-date-epoch-anchor-clone-2`, `_infra/pre-registration-gate-policy-scope-verification-clone-1`, `_manager/M-EAR-1-v2-c45-deprecation-…-clone-2`) |
| F12 | MODERATE | CONFIRMED | `M-RECREATE-2/accurate-small-set/rc8-peak-section-selection` never fired — RC8 acceptance is functionally satisfied via `focus_set_v2.json.chosen_section` but no verdict event was emitted |
| F13 | INFO | CONFIRMED | `M-EAR-1/real-label-training-v2.1` parent milestone unfired; only `-clone-0` sub-leaves are on the ledger (c33-guard emission pattern) |
| F14 | INFO | CONFIRMED | 500 in-ledger orphans (not on POR rows), all housekeeping (`_infra`, `_run`, `_archive`, `_plan`, `_manager`); zero substantive `M-*` orphans |
| F15 | INFO | CONFIRMED | 4/4 spot-checked three-way rubric_hash byte-equality chains hold (RC7 v2, EAR v2, RC10 guitar/piano, palette-driven bare-render) |

### F10 — v2 supersede parent milestone never emitted

Plan-of-record cycle-50 rows include `M-RECREATE-2/accurate-small-set-v2` as a
peer sub-milestone under G1 (per c29 state-machine lemma), formalized by
`_plan/m-recreate-2-rubric-v2-supersede` (which fired, `status: validated`,
`supersedes_path: docs/m_recreate_2_accurate_small_set_rubric.md`).

Ledger scan: **no event has `milestone_id = "M-RECREATE-2/accurate-small-set-v2"`**.
Sub-leaves that the POR lists as children of the v2 parent (`rubric-v2-committed`,
`focus-set-v2-selected`, `rc0-v2-baseline-captured`, `rc7-*`, `rc8-*`, `rc9-*`,
`rc10-*`, `rc-v2-stubs-registered`) all fire under the v1 tree
(`M-RECREATE-2/accurate-small-set/…`) instead. The rubric-v2 chain is preserved
by the `_plan/…-supersede` row, but the aggregation parent under the v2 label
is empty at the ledger level. Downstream readers grepping for cycle-50+ v2
progress via `milestone_id` alone will miss the tree.

### F11 — Four c46/c47 clone-branch rows registered but unfired

POR enumerates these as clone-suffixed peer sub-milestones with concrete
success criteria. None of them appear as a `milestone_id` in the ledger
(searched both exact and `-clone-*` variants):

- `_archive/deprecate-c45-determinism-check-clone-2`
- `_infra/pin-source-date-epoch-anchor-clone-2`
- `_infra/pre-registration-gate-policy-scope-verification-clone-1`
- `_manager/M-EAR-1-v2-c45-deprecation-and-source-date-epoch-anchor-pin-clone-2`

The c47 Branch B verification report and its 5 scripts + 6 data artifacts
do exist on disk (see `docs/pre_registration_gate_policy_scope_verification*`),
but the ledger row for the parent milestone_id never landed. This is a fanout
merge-step drift: the POR row was registered by the c46/c47 researcher fanout
step but the shadow-ledger events from clones 1+2 either merged under a
different id, or the parent rollup was skipped. Impact is narrative-only —
the on-disk substantive artifacts pass their own three-way rubric_hash checks.

### F12 — RC8 peak-section-selection never emitted a verdict event

The RC8 acceptance-criterion contract calls for a per-song chosen-section
metadata block reproducible from `focus_set_v2.json.chosen_section` byte-for-byte.
The `focus_set_v2.json` file **does contain** `chosen_section` per song under
D1 (auto-picked peak 30 s window by combined RMS + onset density), and the
`M-RECREATE-2/accurate-small-set/focus-set-v2-selected` event (c50) validated
this. However, no dedicated `rc8-peak-section-selection` verdict event ever
emitted. Functionally the RC8 gate is satisfied via focus_set_v2 provenance;
formally, the row is unfired. This is a bookkeeping gap, not a capability gap.

### F13 — `M-EAR-1/real-label-training-v2.1` parent unfired (INFO)

POR lists both the parent and 6 sub-leaves for the c47 clone-0 Branch A
`v2.1` re-verdict pass. The parent row is unfired. The sub-leaves all fire
under their `-clone-0` suffix (c33 harness auto-suffix path). Given the c33
namespace-guard's design (infra-family ids under a clone context are
auto-suffixed; substantive `M-*` ids are not unless the c48 substantive
exemption flag is off), the parent's absence is expected under c47's default
flag state — a promotion event under the unsuffixed parent id would need to
land in a non-clone context. INFO-severity because the aggregation is implicit
in the sub-leaves' collective status.

### F14 — 500 orphan `milestone_id` values in ledger (INFO)

Prefix distribution:

| Prefix       | Count | Nature |
|--------------|-------|--------|
| `_infra/`    | 164   | Per-cycle `adopt-cycle<N>-tests`, harness fixes, one-shot tooling |
| `_run/`      | 118   | `report_cycles_*`, `post-merge-integration-*`, `start`, harness-emitted rollups |
| `_archive/`  | 115   | Per-cycle `cycle-<N>-scratch` housekeeping |
| `_plan/`     | 85    | Plan-file registration events, gate-policy edits, correction batches |
| `_manager/`  | 18    | Cross-cycle escalation tickets |
| `M-*`        | 0     | No substantive-milestone orphans |

The housekeeping-event pattern documented in POR §"Housekeeping event pattern"
gives stable naming (`_archive/cycle-<N>-scratch`, `_infra/adopt-cycle<N>-tests`)
without requiring each cycle's instance to be enumerated in the Milestones
table. The 500 orphans are pattern-conforming and grep-discoverable. No defect.

### F15 — Three-way rubric_hash byte-equality: 4/4 PASS

Sampled a mix of eras and branches:

| Milestone                    | doc SHA (16 hex)  | rubric_hash.txt   | verdict.rubric_hash |
|------------------------------|-------------------|-------------------|---------------------|
| c53 RC7 v2                   | `9f24e6d9240f1eaf`| `9f24e6d9240f1eaf`| `9f24e6d9240f1eaf`  |
| c45 EAR v2                   | `01948b6efe6ca5e9`| `01948b6efe6ca5e9`| `01948b6efe6ca5e9`  |
| c53 RC10 guitar/piano        | `c7fe33a742a98f9b`| `c7fe33a742a98f9b`| `c7fe33a742a98f9b`  |
| c33 palette-driven bare-render | `ae2f3b50e89d1659`| `ae2f3b50e89d1659`| `ae2f3b50e89d1659`  |

All chains byte-equal. The rubric-hash discipline held end-to-end from c33
through c53, spanning ~20 cycles of independent worker/auditor turns.

## Gate check (test stage)

- Every fix from prior stages verified? — N/A: audit-only probes.
- Adjacent behavior checked? — Yes: verdict-SHA chain sampled across four eras
  (c33 → c53), plan/ledger inspected in both directions (orphans + unfired).
- New issues classified? — Yes: F10 MODERATE, F11 MODERATE, F12 MODERATE,
  F13 INFO, F14 INFO, F15 INFO.

## What's next (stage 28 = test 4/23)

Planned probes:
- Egress-probe cadence audit: verify per-cycle rows in `egress_status.jsonl`
  align with `_plan/egress-retry-cadence-policy-formalized` (path A vs path B).
- Anchor-preservation contract audit: sample 5+ `anchor_preservation*.json`
  files; re-hash claimed anchor files vs recorded pre-hash values.
- Rubric-doc mtime discipline: sample 5+ rubric docs; verify mtime < any
  script/impl file under the corresponding milestone directory.
- Report-glob coverage: `reports/cycles/` scan for gaps in cycle numbering
  or missing per-cycle final reports.

<checkpoint>
  <stage>test (3/23) — stage 27/48</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~197k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Ran 4 probes: orphan-milestones scan (500 orphans, all housekeeping — no M-* orphans); plan/ledger consistency (9 truly-unfired POR rows including v2 supersede parent + 4 c46/c47 branch rows + RC8); test-suite audit (74 files, 2 flagged then cleared via docs/reports refs); spot-sample rubric_hash chain (4/4 byte-equal across c33→c53).</what-i-did>
  <next-action>Advance to stage 28 (test 4/23): egress cadence audit, anchor-preservation sample re-hash, rubric mtime discipline, report-glob coverage.</next-action>
  <gate-check>All findings classified with severity + verdict; findings.jsonl appended with 6 new rows (F10 MODERATE, F11 MODERATE, F12 MODERATE, F13 INFO, F14 INFO, F15 INFO); no fixes applied (audit-only stage).</gate-check>
</checkpoint>
