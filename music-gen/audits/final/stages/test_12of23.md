# Stage 36 — test (12/23)

Scope: adversarial verification of the ear v2 / v2.1 three-way `rubric_hash`
byte-equality chains, the c46 mapping-clarified paragraph on-disk placement,
and closure-doc ↔ ledger consistency.

## Probes executed

### P1 — Closure doc ↔ ledger consistency

Enumerated `docs/` filenames containing CLOSURE or SUPERSEDES (case-insensitive).
Three matched:

| Doc                                                 | mtime      | Ledger event present? |
|-----------------------------------------------------|------------|-----------------------|
| `daw_spike_gap_closure_report.md`                   | 1787924922 | YES — `M-DAW-SPIKE-1/gap-closure` validated (c12) |
| `daw_spike_gap2_dawdreamer_closure_report.md`       | 1787928491 | YES — `M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation` validated (c13) |
| `ear_v2_verdict_adjudication_report.md`             | 1788020157 | YES — `_manager/M-EAR-1-v2-verdict-adjudication-and-gate-closure` chain (c46) |

Verdict: **PASS** — every closure doc anchored by a matching ledger event; no
silent supersession detected.

### P2 — Ear v2 three-way rubric_hash byte-equality

```
doc SHA-256(docs/ear_real_label_training_v2_rubric.md)
    = 01948b6efe6ca5e91d5024c644bb384ae9a8b6220253e51e76c55668170d71e0
content(data/ear_v2/rubric_hash.txt)
    = 01948b6efe6ca5e91d5024c644bb384ae9a8b6220253e51e76c55668170d71e0
data/ear_v2/verdict.json .rubric_hash
    = 01948b6efe6ca5e91d5024c644bb384ae9a8b6220253e51e76c55668170d71e0
```

Verdict field: `EAR_v2_PARTIAL`. Three-way chain **HOLDS byte-identically**.

### P3 — c46 mapping-clarified paragraph on-disk placement

`docs/ear_v2_verdict_adjudication_report.md` §2 ("Mapping quoted verbatim
from rubric doc") contains verbatim:

- Quote A (SB3 pass definition, compound `det ≥ 0.90 AND fpr ≤ 0.10`)
- Quote B (PARTIAL clause with IMPROVEMENT criteria: SB1 margin > −0.2093,
  SB2 mean τ > −0.0987, SB3 F1 denom > 43)
- Quote C (INSUFFICIENT clause: "no SB improves over v1 within noise")

§2 reconciliation table shows 0/3 PASS + 2/3 IMPROVEMENT (SB2 τ, SB3 denom),
concluding `Reconciliation = (A) mapping-clarified`. §3 records:

- `data/ear_v2/verdict.json` unchanged (rubric_hash chain intact) ✓
- Plan-of-record row for `M-EAR-1/real-label-training-v2` amended with the
  pass/improvement split — verified in plan_of_record.md milestone row

Verdict: **PASS** — verbatim clauses on-disk, reconciliation determination
matches the c46 ledger event narrative.

### P4 — Ear v2.1 three-way rubric_hash byte-equality (extension)

```
doc SHA-256(docs/ear_real_label_training_v2p1_rubric.md)
    = 2920875671ea98b127a585bf42ed401110a724b0b6b61fc5aa1bca0cff2abafa
content(data/ear_v2p1/rubric_hash.txt)
    = 2920875671ea98b127a585bf42ed401110a724b0b6b61fc5aa1bca0cff2abafa
data/ear_v2p1/verdict.json .rubric_hash
    = 2920875671ea98b127a585bf42ed401110a724b0b6b61fc5aa1bca0cff2abafa
```

Verdict field: `EAR_v2p1_STABLE_FPR_PASS`; `mapping_label`:
`EAR_v2p1_PARTIAL_WITH_SB3_PASS`. Both runs FPR=0.1 exactly (boundary tip),
`byte_determinism_x2=True`, `fpr_boundary_delta=0.0`. `sb1_status` and
`sb2_status` remain `FAIL_unchanged_from_c45` per c47 brief (do NOT re-verdict
SB1/SB2). Corpus caveat `preview_partial_corpus_v2p1` (43/80) present.

Three-way chain **HOLDS byte-identically**.

Note: verdict is exactly on the 0.10 rubric boundary. The rubric doc's
`STABLE_FPR_PASS` condition is `FPR ≤ 0.10` (inclusive), so an exact-boundary
observation satisfies it. This is honestly labeled as a boundary result via
the `mapping_label` field and `fpr_boundary_delta` sidecar. Not a defect.

## Findings this stage

None. All four probes PASS.

| ID | Severity | Milestone | Kind |
|----|----------|-----------|------|

## Running totals
- Findings file: 111 rows (unchanged).
- Cumulative: 5 CRITICAL, ~14 MODERATE, 28 INFO (approx.; retracted F40 not
  counted).

<checkpoint>
  <stage>test</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~200k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Verified v2 + v2.1 three-way rubric_hash chains byte-identically, confirmed §2 mapping-clarified verbatim quotes, cross-checked 3 closure docs against ledger events. All PASS.</what-i-did>
  <next-action>Stage 37 (test 13/23) — probe c47 anchor_manifest_v1 append-only integrity (18→19 entry expansion at c47 clone-2) and c48 harness-v3 baseline replay claim (793 rows unchanged pre/post edits).</next-action>
  <gate-check>Continuing in test.</gate-check>
</checkpoint>
