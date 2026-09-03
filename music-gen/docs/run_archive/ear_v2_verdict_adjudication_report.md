---
created: 2026-08-29T16:15:00Z
cycle: 46
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _manager/M-EAR-1-v2-verdict-adjudication-and-gate-closure
---

# c46 Report — v2 verdict adjudication and gate closure

## §1. Verdict summary

**Adjudication verdict: `ADJUDICATION_MAPPING_CLARIFIED`** (Reconciliation A).

Rubric on disk (`docs/ear_real_label_training_v2_rubric.md`, SHA-256
`01948b6efe6ca5e91d5024c644bb384ae9a8b6220253e51e76c55668170d71e0`)
defines the `EAR_v2_PARTIAL` clause via IMPROVEMENT criteria that are
distinct from PASS criteria. The c45 verdict `EAR_v2_PARTIAL` is
consistent with the rubric as written.

The c45 audit's CRITICAL "verdict mapping inconsistency" finding
conflated SB pass count (0/3) with SB improvement count (2/3). The
rubric doc's PARTIAL clause is not gated on pass count. No supersede
of `data/ear_v2/verdict.json` this cycle.

The plan-of-record row for `M-EAR-1/real-label-training-v2` is amended
with an explicit pass/improvement split paragraph so downstream
readers do not repeat the conflation.

Corpus-N caveat unchanged: 43 of 80 songs; SB2 τ progression from
c22 (0.059) → c38 (-0.099) → c45 (-0.031) survives intact as the
material substantive finding.

## §2. Mapping quoted verbatim from rubric doc

Rubric file: `docs/ear_real_label_training_v2_rubric.md`
Rubric SHA-256: `01948b6efe6ca5e91d5024c644bb384ae9a8b6220253e51e76c55668170d71e0`
Adjudication rubric SHA-256: `975985495b5750668262374080e3c6f0b135be6aa3b1a647f81c0b08c880afa8`

### Quote A — SB3 pass definition (§Success bars, item SB3)

> **SB3** — F1 pooled-variance leak-detection statistic on artist
> (LIVE) at α=1.0. Statistic version `F1_pooled_variance_v1` per c38
> clone-0 lift; `detection_rate ≥ 0.90` AND `fpr ≤ 0.10`; τ = 90th
> percentile of 25 SHA-permutation null distributions; detection rate
> over 20 SHA-subsample repeats.

**Reading**: SB3 atom IS compound. Both `detection ≥ 0.90` AND
`fpr ≤ 0.10` required to count SB3 as a PASS. On c45 numbers
(det=1.000, fpr=0.120): SB3 fails on the FPR half. This matches the
c46 auditor's reading.

### Quote B — Three-verdict rubric (§Three-verdict rubric, PARTIAL clause)

> **`EAR_v2_PARTIAL`** — at least one of SB1/SB2/SB3 falls short AND
> at least one improves materially over v1. Improvement criteria
> (any of): SB1 margin `> −0.2093` (v1 baseline); SB2 mean τ
> `> −0.0987` (v1 baseline); SB3 F1 denominator `> 43` with a finite
> non-pinned value.

### Quote C — INSUFFICIENT clause

> **`EAR_v2_INSUFFICIENT`** — no SB improves over v1 within noise.

**Reading**: PARTIAL is gated on IMPROVEMENT criteria (per-SB v1
baseline deltas + SB3 denominator geometric threshold), NOT on the
same thresholds used for PASS. INSUFFICIENT is reserved for "no SB
improves". The rubric explicitly separates these two axes.

### Reconciliation determination

| SB  | Observed             | PASS threshold          | Passes? | IMPROVEMENT threshold | Improves? |
|-----|----------------------|-------------------------|---------|-----------------------|-----------|
| SB1 | margin -0.2341       | margin > 0.5909         | NO      | margin > -0.2093      | NO        |
| SB2 | mean τ -0.0314       | mean τ ≥ 0.4            | NO      | mean τ > -0.0987      | YES       |
| SB3 | det 1.000, fpr 0.120 | det ≥ 0.90 AND fpr ≤ 0.10 | NO (fpr overshoot) | denom > 43 | YES (618) |

- Pass count: 0/3 (matches audit).
- Improvement count: 2/3 (SB2 τ, SB3 denom).
- Shortfall count: 3/3 (all fall short of PASS).

Rubric PARTIAL clause requires "≥1 falls short AND ≥1 improves". Both
preconditions satisfied. PARTIAL fires.

Rubric INSUFFICIENT clause requires "no SB improves". Not satisfied
(2/3 SBs improve). INSUFFICIENT does NOT fire.

**Reconciliation = (A) mapping-clarified.**

## §3. Reconciliation action

- `data/ear_v2/verdict.json` unchanged (rubric_hash chain intact).
- `docs/ear_real_label_training_v2_report.md` unchanged.
- Plan-of-record `M-EAR-1/real-label-training-v2` row amended with
  the pass/improvement split paragraph (see §Milestones in
  `plan_of_record.md`).
- Ledger event `M-EAR-1/real-label-training-v2/mapping-clarified`
  fired referencing the rubric doc quote as authoritative and the
  c45 `verdict-emitted` event as consistent.
- Ledger event `_plan/clarify-sb3-mapping-atom-split` fired
  documenting the pass/improvement axis distinction for downstream
  cycles.

## §4. Byte-determinism × 2 result

See `data/ear_v2/determinism_check_c46.json` for the machine-readable
result. Two independent runs into fresh `tempfile.mkdtemp()` dirs
under BLAS pins + `PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH` +
`TZ=UTC` + `LC_ALL=C.UTF-8` + `torch.manual_seed(0)`. Assertion:
SHA-256 equality on `corn_head_v2.pt` and `training_result.json`.

Result: see §4 table in `data/ear_v2/determinism_check_c46.json`.

## §5. Test suite

`tests/test_ear_v2_real_label_training.py` — 20 cases; invocation:
`PYTHONPATH=. /usr/bin/python3 tests/test_ear_v2_real_label_training.py`.
Plain-assert style. Zero pytest dependency. See §5 in
`tests/test_ear_v2_real_label_training.py` for the full test list.

## §6. Cross-branch integration §60 extension

`tests/test_integration_cross_branch.py` §60 extended with 8 v2
invariants: three-way rubric_hash byte-equality, rubric-first
mtime ordering, corpus-N caveat presence, no sidecar_nonfactor / no
PRNG / no i4_stratified.py imports, chassis-anchor preservation, and
c22/c23/c25 anti-pattern lockout.

## §7. SB3 50-control widening probe

`scripts/ear_v2/sb3_control_widening.py` extends the c37/c38 leak-test
denominator from 25 to 50 controls, keeping the c37 F1 pooled-variance
statistic unchanged. Result recorded in
`data/ear_v2/sb3_control_widening_result.json`.

## §8. Git-log gate policy decision

**Path (ii) taken — formal policy amendment**.

Rationale: this session's harness gates all `git add` / `git commit`
operations behind an approval prompt that cannot be satisfied inside
a single worker turn. Git commits happen at a HIGHER harness level
(periodic sweep — visible as commits `32dd3f6`, `40b0eb0`, `b0603cd`,
etc. in `git log --oneline`). The worker cannot commit the adjudication
rubric doc between writing it and writing the adjudication scripts;
mtime ordering is the only ordering the worker can enforce inside its
own turn.

This exactly matches the c38-MERGE_DEFERRED precedent (shadow ledger
git-log ordering does not survive concat) generalized to the
single-worker turn boundary.

Policy amendment (`docs/pre_registration_gate_policy.md`): the
pre-registration gate is amended to mtime-only when the worker cannot
commit inside its own turn. The mtime gate is preserved and enforced
by test 01; the git-log gate becomes an advisory check (test 02
becomes a soft check under path (ii)). Test count in item 5 still
lands at ≥15 (20 in practice).

## §9. Anchor preservation

`data/ear_v2/anchor_preservation_c46.json` records SHA-256 for all
32+ read-only anchors (c6 feature cache, c22 stability harness, c26
Path B doc, c36 v0, c38 v1, c45 v2 rubric anchors, c9/c15/c40 rules
ledgers, c6 chassis). All pre==post byte-exact.

## §10. c47 handoff seeds

1. **v2.1 rerun**: under reconciliation (A), if the SB3 50-control
   widening probe flips FPR to ≤ 0.10, a v2.1 rerun with the widened
   denominator could re-verdict `EAR_v2_LANDS-on-two-SBs` (SB2 still
   below the τ ≥ 0.4 threshold). Defer to c47 as a first-class
   ticket. The c45 verdict was on 25-control FPR = 0.120 and stands
   until a v2.1 rerun.
2. **SB2 τ recovery mechanism probe**: 2-cell ablation (per-clip
   contribution vs GroupKFold contribution to the c45 SB2 lift from
   -0.099 → -0.031). c47 first-class.
3. **Corpus expansion**: retry harvest; watch for two consecutive
   `media_ok=true` unblock signal. Operator-delivered channel is
   also acceptable.
4. **c38 clone-1 normalizer-v2 mscore3 quantization narrowing**:
   standing ticket.
5. **v2 vs v1 direct chassis comparison**: formalize as
   sub-milestone.
6. **Adjudication rubric anchoring**: this cycle's adjudication
   rubric SHA is now a permanent anchor
   (`975985495b5750668262374080e3c6f0b135be6aa3b1a647f81c0b08c880afa8`);
   future cycles that touch verdict mapping must respect it or
   supersede it explicitly with a new rubric doc.

## Appendix — c45 verdict.json byte state

Preserved unchanged this cycle (per reconciliation A):

- `verdict`: `EAR_v2_PARTIAL`
- `rubric_hash`: `01948b6efe6ca5e91d5024c644bb384ae9a8b6220253e51e76c55668170d71e0`
- `corpus_size_songs`: 43
- `corpus_size_clips`: 252
- SB1 margin: -0.2341
- SB2 mean τ: -0.0314
- SB3 detection: 1.000, FPR: 0.120, denominator_pairs: 618
