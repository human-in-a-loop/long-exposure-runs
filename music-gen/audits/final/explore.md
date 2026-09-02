# Final audit — Stage 1 (Explore)

Cycle range: **1..54** (58 cycles per plan; last landed cycle=54).
Ledger events: **920**; distinct milestones: **762**; substantive `M-*`
milestones: **231**; `_infra`/`_plan`/`_manager`/`_run`/`_archive`
bookkeeping: **531**. Reports on disk: **32** (`reports/cycles/`); root
closure/supersedes docs: none (closure carried in-ledger under
`_manager/*` + `_plan/*-supersede` rows).

## Scope of this audit

Per role contract: **closing-the-books pass at run scope**. I audit the
run's structured commitments (plan_of_record milestones, ledger
supersedes/reconciliations, evidence files, `_manager/*` adjudications,
`_plan/*` amendments) — NOT the exploration mechanics themselves.

The ratings-audio egress block (HTTP 429 + `tv_embedded`) is a live
external constraint documented by ~10 `M-INGEST-1/egress-probe*` rows;
it does not itself constitute a defect and remains carried-forward at
run close.

## Latest-per-milestone status distribution

Substantive `M-*` (231):

| Root | validated | in-progress | invalidated | reopened | superseded |
|------|-----------|-------------|-------------|----------|------------|
| M-CLASS-1     | 1  | – | – | – | – |
| M-DAW-SPIKE-1 | 7  | 1 | 1 | – | – |
| M-EAR-1       | 27 | 3 | 3 | – | – |
| M-GEN-1       | 24 | 3 | – | – | – |
| M-HEUR-1      | 6  | – | – | – | – |
| M-INGEST-1    | 24 | 3 | – | 1 | – |
| M-RECREATE-1  | 13 | – | – | – | – |
| M-RECREATE-2  | 44 | 6 | – | – | – |
| M-RULES-1     | 28 | – | – | – | – |
| M-SCORE-1     | 16 | – | – | – | – |
| M-SEP-1       | 4  | – | – | – | – |
| M-TEX-1       | 9  | 1 | 1 | – | – |
| M-TRANS-1     | 4  | – | 1 | – | – |
| **totals**    | **207** | **17** | **6** | **1** | – |

Bookkeeping roots (531): `_archive` 115 (all validated),
`_infra` 183 (all validated), `_plan` 88 (all validated),
`_manager` 24 (21v/2ip/1sup), `_run` 121 (112v/9ip — 9
`_run/cycle_<N>_launched(-clone-<k>)?` rows never re-closed at
integration).

## Terminal-status classes to verify (verdict-pending items)

Distributed across verify stages 2..24 (23 slots ≈ 10 milestones/slot).

### VP-A. Invalidated (six first-class negative findings — verify they
are honestly narrated and not silently supplanted)

1. `M-TEX-1/panel/embedding` (c11) — CLAP fetchability fail; ladder →
   VGGish; c14 `content-flip-analysis` characterized the family-drift.
2. `M-TRANS-1/basic-pitch/octave-suppression` (c8) — +0.15 uplift below
   the +0.3 pre-registered bar; falsifiability escape hatch invoked.
3. `M-EAR-1/synthetic-label-stability-audit` (c22) — c6 CORN chassis
   fails C1/C2/C3 on 55-clip synthetic-label sweep.
4. `M-EAR-1/head-regularization-audit` (c23) — 3 regularized variants
   all fail C1'/C2'/C3'.
5. `M-EAR-1/feature-representation-audit` (c25) — HEUR-only and
   PANNs-only fail C2'.
6. `M-DAW-SPIKE-1/palette-schema-v2-hydration-render` (c35) —
   RENDER_FAILS on VST3 binary-internal nondeterminism; c36 M-DAW-SPIKE-1/
   `vst3-render-nondeterminism-characterization` (MIXED) is the follow-on.

### VP-B. In-progress at run close (17 rows — verify each has an honest
"carried over" narrative and no dangling supersede-pending status)

- `M-EAR-1` (parent, c26) — Path-B commit doc landed; parent stays
  in-progress by design pending real-label calibration.
- `M-EAR-1/training-loop` (c11) and `M-EAR-1/real-label-training-v2`
  (c45) — v2 is `EAR_v2_PARTIAL` per c46 adjudication; v2.1 sub-leaves
  validated at c47.
- `M-GEN-1/rule-composition-constraint` (c11),
  `M-GEN-1/batch-v3-i4` (c15), `M-GEN-1/batch-v6-unconditioned-n16`
  (c25) — verify their parent rollups closed the arc (collision-model
  BP campaign closed as `PARTIAL_BP_UNRESOLVED_SHAPE` c30).
- `M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation` (c13) — check
  whether the c13 REDEFINED_GAP verdict was recorded and the parent
  closed.
- `M-TEX-1/palette-driven-bare-render` (c33) — c34 cross-seed peer
  sub-sub validated; verify parent status is consistent.
- `M-INGEST-1/egress-probe` (c35) + `M-INGEST-1/egress-probe-cycle47-
  clone-2` (c47) — parent stays in-progress by construction (probe is
  never "done" until two consecutive `media_ok=true`); verify the
  narrative flags this.
- `M-RECREATE-2/accurate-small-set` parent (c49) + RC1/RC4/RC5/RC6
  (c49) + RC9 (c51) — RC1 and RC9 have c51 verdict-emitted
  sub-leaves under `-clone-0`; verify these roll up cleanly and that
  RC4/RC5/RC6 are honestly declared as c52+ deferred (RC6 depends on
  RC1–RC3 outputs).
- Nine `_run/cycle_<N>_launched*` rows (c29..c47) — pure
  cycle-open bookkeeping; verify these do not require closure events.
- `_manager/background-job-supervision-clone-0` (c36) — verify closure.
- `_manager/M-INGEST-1-corpus-expansion-plan-c48-queued-clone-1` (c48)
  — verify closure.

### VP-C. Reconciliation events (verify honesty and audit trail)

- `M-INGEST-1/egress-probe-clone-2` (c36) — status `reopened`;
  cross-check with the c36 `_infra/fanout-namespace-convention-v2`
  reconciliation and the retroactively-renamed `-clone-0/-clone-2`
  peers listed in plan.
- `_manager/M-EAR-1-real-label-training-v2-unfixable-by-audit-clone-1`
  (c46) — `superseded`; verify supersede pointer chain to c45
  `verdict-emitted` + c46 `mapping-clarified`.
- `_plan/git-log-gate-policy-amendment` (c46) — path-(ii) amendment
  (mtime-only when harness gates commit). Verify downstream cycles
  actually respect it.
- `_plan/m-recreate-2-rubric-v2-supersede` (c50) — v2 rubric
  supersedes v1. Verify `supersedes_path` is `str` per c14 lemma and
  v1 rubric SHA byte-identical pre==post at every subsequent event.
- `_plan/egress-retry-cadence-policy-formalized` (c49).

### VP-D. Terminal-validated but confidence≠high (per contract, low
confidence at terminal state is a first-class outcome — verify honest
narrative and non-silent supersession)

`M-CLASS-1` (validated/medium c1 — parent rollup; children high),
`M-DAW-SPIKE-1/gap-closure` (validated/medium c12; sub-sub c13 gap2
in-progress — dependency to check), `M-TEX-1/panel` (validated/medium
c4 — check whether c11 `M-TEX-1/panel/embedding` invalidation should
demote this parent's confidence in the audit narrative), and
`M-EAR-1/preparation/leak-test` (per docs — c37 F1 pooled-variance
statistic lifted; check that the c6 `_manager/M-EAR-1-leak-statistic-
substitution` decision is still auditable).

### VP-E. Figure/evidence coverage (spot-check)

35 figure files on disk; 73 unique figure paths referenced across
ledger `artifacts`; naïve set diff reports 0 orphans / 0 missing, but
the counts imply many-to-one referencing that warrants a real
per-milestone spot-check in the verify passes.

## Adversarial hooks for the test stage (2N+2 pass)

1. Run `python3 -m long_exposure.tools.promise_check .` — expect
   `0 ERROR` per c46, c47, c48 events.
2. Run `python3 -m long_exposure.tools.org_check .`.
3. Cross-check every `_plan/*-supersede` event actually superseded
   what it names (mtime + SHA-256 preserved on the pre-image).
4. Silent-supersession scan: any closure doc under `docs/*` with
   mtime after its `_plan/register-*` event but with no downstream
   supersede row is drift.
5. Orphan-milestone scan: any milestone referenced in ledger but not
   in plan_of_record.md.
6. `_run/cycle_<N>_launched*` orphan rollup scan: 9 rows carried as
   in-progress; verify these are structural (cycle-open markers) not
   dropped commitments.

## Slice plan for verify stages 2..24 (23 stages)

- **S2** Invalidated set (VP-A #1–3): TEX/embedding, TRANS/octave, EAR/
  synthetic-label-stability.
- **S3** Invalidated set (VP-A #4–6): EAR/head-regularization, EAR/
  feature-representation, DAW/palette-v2-hydration.
- **S4** M-EAR-1 tree (parent + v0 + v1 + v2 + v2.1 sub-leaves).
- **S5** M-EAR-1/preparation tree + armed-harness + fixture-reinforcement.
- **S6** M-GEN-1 collision-modeling arc (bp / shape-mechanism / hash-
  space-geometry / adjudication / semantic-cluster-overlap).
- **S7** M-GEN-1 batch series (v1 / v2 / v3-i3 / v3-i4 / v4-compound /
  v5-n16 / v6-unconditioned).
- **S8** M-GEN-1 palette-driven-batch series (v1 / v2 / v3 / v4 /
  rated-corpus-clone-0).
- **S9** M-RULES-1 tree (schema + extraction + breadth-seeds +
  rated-corpus + harmonic-window-refinement).
- **S10** M-SCORE-1 tree (round-trip / merged-full-song / bridge-api /
  bridge-api-real-audio-quantization + normalizer-v2).
- **S11** M-INGEST-1 core (chunker / provenance / harvester-parity /
  breadth-second-seeds / egress-ready-automation).
- **S12** M-INGEST-1 egress-probe series (all 10 clone/cycle rows +
  reopened row).
- **S13** M-SEP-1 tree (ground-truth / htdemucs-baseline / alternative)
  + M-HEUR-1 tree (melody / timbre / form / dynamics / meta-tracker).
- **S14** M-TEX-1 tree (panel + panel/{spectral,envelope,embedding} +
  content-flip-analysis + stage-by-stage/{seed_mid_50s, synth_060s} +
  palette-driven-bare-render + cross-seed).
- **S15** M-CLASS-1 + M-TRANS-1 tree (basic-pitch / alternative /
  six-axis-coverage / octave-suppression).
- **S16** M-DAW-SPIKE-1 tree (parent + gap-closure + gap2 + palette-
  assignment-schema + palette-instrument-determinism + palette-schema-
  v2 + palette-schema-v2-hydration-render + vst3-render-nondeterminism
  + dawdreamer-state-extraction-workaround).
- **S17** M-RECREATE-1 tree (first-real-audio + second-real-audio-batch
  + full-corpus-recreation, incl. clone-0/-2 suffixes).
- **S18** M-RECREATE-2 v1 tree (rubric + focus-set + rc0-baseline +
  rc-stubs + rc1..rc6 sub-milestones).
- **S19** M-RECREATE-2 v2 tree (rubric-v2 + focus-set-v2 + rc0-v2 +
  rc7 mix-balance + rc8 peak-section + rc9 first-class-parts).
- **S20** M-RECREATE-2 c51 rc7 sub-leaves (pre-registration +
  render-stem-signature-v3 + eq-curve-fitted + loudness-matched +
  anchor-preservation + verdict-emitted).
- **S21** M-RECREATE-2 c53 rc7-v2 + rc10 guitar-piano tree.
- **S22** `_manager/*` adjudications (M-EAR-1-v2-verdict-adjudication +
  Path-B-commit + c45..c48 handoffs).
- **S23** `_plan/*` amendments (rubric-v2 supersede + egress-retry-
  cadence + git-log-gate-policy + fanout-namespace-conventions).
- **S24** `_infra/*` hardening chain (ledger-schema-hardening + v2 +
  fanout-concat + harness-clone-namespace-guard + harness-auto-write-
  namespacing + anchor-manifest-v1 + harness-and-writer-hardening-v3 +
  pre-existing-test-drift-triage). Also: any residual figure-coverage
  gaps.

## Test stage (2N+2 pass — stages 25..47)

Adversarial validators (promise_check, org_check), silent-supersession
scans, orphan-milestone scan, and structural cross-checks are threaded
through the test slots; the document stage (48) commits reconciliation
events (`agent: "final_auditor"`) if any.

## Full milestone catalog

See `audits/final/tmp/mstable.md` (231 rows, one per substantive
milestone with status/confidence/cycle/first-artifact).

See `audits/final/audit_reports_index.md` (32 report files across
cycles 1..54).
