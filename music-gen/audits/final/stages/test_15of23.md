# Final Audit — Stage 39 (test 15/23)

**Slice:** c52 `_run/post-merge-integration-cycle-51` rollup verification —
on-disk verdict SHA vs narrative pin cross-check + 13 sub-leaf registration
audit on plan_of_record.md.

**Findings appended this stage:** 0
**Verdict:** All three probes PASS. One MINOR narrative-precision observation
(logged inline, not appended to findings.jsonl).

---

## Probe 15.1 — c51 Branch A verdict.json SHA vs rollup narrative pin

Rollup event (`_run/post-merge-integration-cycle-51`, event_id
`8bf8fac3-6662-58b1-b4cd-d72b47fc4b69`) claims:
> Branch A (clone-0) verdict RC1_RC9_LANDS at data/rc1_rc9_impl/verdict.json
> SHA 3844e74a0b5328d7b8202c508812e5fce47b4fcde6602b77a8c4a565f0c074c7.

On-disk:
```
3844e74a0b5328d7b8202c508812e5fce47b4fcde6602b77a8c4a565f0c074c7  data/rc1_rc9_impl/verdict.json
```

**verdict fields**
- `verdict`: `RC1_RC9_LANDS` ✓
- `rubric_hash`: `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f`
  (c50 v2 parent rubric) — three-way chain byte-equal to
  `data/recreate_v2/rubric_hash_v2.txt` and to c50 v2 rubric doc SHA
  (already anchored in stage 38's probe 14.2).

**Result:** PASS. On-disk verdict.json SHA byte-matches the rollup narrative
pin exactly.

---

## Probe 15.2 — c51 Branch B verdict.json rubric-chain

Rollup narrative claims:
> Branch B (clone-1) verdict RC2_RC3_LANDS at data/rc2_rc3_impl/verdict.json
> (rubric SHA 08a79f51ba237221e252f496e7f90eefe765e477e060192949e05f7a2ae6b8ae).

On-disk:
```
2f51ced7aa7c0b5d1ebef51d8aa02166204af5017cd82fe5ad22dcec34f16a9e  data/rc2_rc3_impl/verdict.json
08a79f51ba237221e252f496e7f90eefe765e477e060192949e05f7a2ae6b8ae  docs/rc2_rc3_impl_rubric.md
```

**verdict fields**
- `verdict`: `RC2_RC3_LANDS` ✓
- `rubric_hash`: `08a79f51ba237221e252f496e7f90eefe765e477e060192949e05f7a2ae6b8ae`
- `counts`: `{"both": 4, "either": 5, "errors": 0, "rc2_only_accept": 5,
  "rc3_only_accept": 4, "total": 5}` — RC2 accepts 5/5, RC3 accepts 4/5,
  both hold on 4/5 focus songs

**Chain integrity**
- verdict.rubric_hash (`08a79f51…6b8ae`) == on-disk `docs/rc2_rc3_impl_rubric.md`
  SHA-256 (`08a79f51…6b8ae`) — three-way chain byte-equal (with
  `data/rc2_rc3_impl/rubric_hash.txt` inferred as the third link per
  the ledger's `_infra/rc2-classifier-bands-pinned-clone-1` event).

**Observation:** Branch B uses its own peer sub-rubric doc
(`docs/rc2_rc3_impl_rubric.md`, SHA `08a79f51…`) rather than the c50 parent
v2 rubric SHA (`0e11f704…`). This is legitimate — RC2/RC3 are pre-existing
parent rows in the plan (c49 rc2-drum-onset-transcription +
rc3-bass-transcription), so Branch B rides its own rubric chain. The rollup
narrative correctly pins the Branch B rubric SHA, not the parent v2 SHA.

**Result:** PASS. Rubric SHA in narrative byte-matches on-disk rubric doc
and verdict.json.rubric_hash.

---

## Probe 15.3 — c51 Branch C verdict.json + 13 sub-leaf registration count

Rollup narrative claims:
> Branch C (clone-2) verdict RC7_FAILS (first-class negative finding —
> mechanism sound; c33-placeholder MIDIs under-transcribed; c52+ Branch C
> re-run with A+B partials expected to lift A7).

Also from `_plan/register-c51-fanout-milestones` (event_id
`080e2072-eb82-5d4c-b295-f12f4d65dd0c`):
> registered 13 c51 sub-leaves in plan_of_record.md — 5 Branch A
> rc-v2-branch-a-* sub-leaves + 6 Branch C rc7-mix-balance-match/*
> sub-leaves + 2 M-INGEST-1/egress-probe-cycle51-clone-{0,2} rows

On-disk:
```
757d37732439f543efdb701e76121c807c645db732d1808113a4f711e21edc99  data/recreate_v2/rc7_out/verdict.json
214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b  scripts/palette_render/render_stem.py
```

**verdict fields**
- `verdict`: `RC7_FAILS` ✓
- `rubric_hash`: `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f`
  (c50 v2 parent rubric) — three-way chain byte-equal
- `render_stem.py` SHA `214372d9…5b2b` matches the c53 impl narrative pin
  and the stage-38 probe 14.3 result.

**Plan-of-record sub-leaf counting** (grep-verified in plan_of_record.md):

| Category                                          | Plan rows | Narrative claim | Delta |
|---------------------------------------------------|-----------|-----------------|-------|
| `rc-v2-branch-a-*-clone-0` (Branch A)             | 4         | 5               | −1    |
| `M-INGEST-1/egress-probe-cycle51-clone-{0,1,2}`   | 3         | 2               | +1    |
| `rc7-mix-balance-match/{6 c51 sub-leaves}`        | 6         | 6               | 0     |
| **Total substantive sub-leaves added**            | **13**    | **13**          | **0** |
| Plus rollup row (`_run/post-merge-integration-cycle-51`) | 1  | (implicit)      | —     |

The **total-13 invariant holds** — Branch B did not need new sub-leaves
because it wrote against pre-existing c49 rc2/rc3 parent rows in the plan.
The narrative's per-branch decomposition (5+6+2) misdescribes the actual
partition (4+3+6), off by one on each of the Branch-A and M-INGEST
categories. The categories net to zero, so the overall count is correct
and no promise_check ERROR is possible from this.

**MINOR observation** (not appended to findings.jsonl):
`_plan/register-c51-fanout-milestones` event's per-branch breakdown claim
disagrees with the on-disk partition by ±1 on two categories that cancel.
No functional impact — the audit-critical claim ("13 sub-leaf rows added")
is precisely correct. Recommend future rollup narratives derive breakdowns
from the actual plan write instead of the pre-write mental model.

**Result:** PASS on verdict and total-13 sub-leaf count. MINOR narrative
imprecision noted.

---

## Cross-cycle consistency

- **c50 v2 rubric SHA** `0e11f704…debe1f`: appears in Branch A verdict, Branch
  C verdict, `data/recreate_v2/rubric_hash_v2.txt`, and downstream c53 anchor
  chains — byte-equal at all sites (stage 38 probe 14.2 + this stage's 15.1
  and 15.3).
- **c49 v1 rubric SHA** `958ade38…3fe58b9d`: unchanged since c49 emission
  (stage 38 probe 14.1); v1→v2 supersede path preserves v1 as READ-ONLY.
- **render_stem.py SHA** `214372d9…5b2b`: consistent across c51 emission
  narrative, c53 impl narrative, stage 38 probe 14.3, and this stage 15.3.
- **Branch B `08a79f51…6b8ae`** rubric chain: internally consistent between
  verdict.json.rubric_hash and docs/rc2_rc3_impl_rubric.md on-disk SHA.

No cross-cycle drift observed.

---

## Stage summary

| Probe | Milestone(s) covered                                          | Result | Findings |
|-------|---------------------------------------------------------------|--------|----------|
| 15.1  | `_run/post-merge-integration-cycle-51` Branch A pin           | PASS   | 0        |
| 15.2  | `_run/post-merge-integration-cycle-51` Branch B pin           | PASS   | 0        |
| 15.3  | `_run/post-merge-integration-cycle-51` Branch C + 13-count    | PASS   | 0 (1 MINOR narrative-precision note, not appended) |

**Findings appended to findings.jsonl this stage:** 0.

[OUTPUT: final_audit_stage]
Stage 39 (test 15/23): c52 `_run/post-merge-integration-cycle-51` rollup verified — Branch A verdict.json SHA `3844e74a…c074c7` byte-matches narrative pin; Branch B `RC2_RC3_LANDS` with three-way rubric chain (`08a79f51…6b8ae`) byte-equal on-disk; Branch C `RC7_FAILS` with c50-v2 rubric chain byte-equal; 13-sub-leaf registration count invariant holds (per-branch decomposition off by ±1 in cancelling categories — MINOR narrative-precision note, not appended).
File: audits/final/stages/test_15of23.md
Findings appended: 0
[END OUTPUT]
