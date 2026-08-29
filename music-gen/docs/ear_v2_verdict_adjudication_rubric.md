---
created: 2026-08-29T16:00:00Z
cycle: 46
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _manager/M-EAR-1-v2-verdict-adjudication-and-gate-closure
---

# Rubric — v2 verdict adjudication (c46)

Frozen BEFORE any script under `scripts/ear_v2/adjudication/` lands.
Git-log gate path (i): this rubric doc commits before any adjudication
script or reconciliation emitter. Test 02 in
`tests/test_ear_v2_real_label_training.py` enforces the git-log ordering
this cycle (no MERGE_DEFERRED).

Rubric SHA-256 pinned to `data/ear_v2/adjudication_rubric_hash.txt`
and embedded verbatim in
`data/ear_v2/adjudication_verdict.json.rubric_hash`.

## Scope

The c45 audit raised a CRITICAL "verdict mapping inconsistency"
against the c45 published `EAR_v2_PARTIAL` verdict on the grounds that
0 of 3 success bars passed and therefore INSUFFICIENT was the correct
label. This cycle adjudicates that claim against the rubric doc on
disk (`docs/ear_real_label_training_v2_rubric.md`).

## Verbatim quotes (frozen)

From `docs/ear_real_label_training_v2_rubric.md` §Success bars:

> **SB3** — F1 pooled-variance leak-detection statistic on artist
> (LIVE) at α=1.0. Statistic version `F1_pooled_variance_v1` per c38
> clone-0 lift; `detection_rate ≥ 0.90` AND `fpr ≤ 0.10`; τ = 90th
> percentile of 25 SHA-permutation null distributions; detection
> rate over 20 SHA-subsample repeats.

From `docs/ear_real_label_training_v2_rubric.md` §Three-verdict rubric:

> **`EAR_v2_PARTIAL`** — at least one of SB1/SB2/SB3 falls short AND
> at least one improves materially over v1. Improvement criteria
> (any of): SB1 margin `> −0.2093` (v1 baseline); SB2 mean τ
> `> −0.0987` (v1 baseline); SB3 F1 denominator `> 43` with a finite
> non-pinned value.

> **`EAR_v2_INSUFFICIENT`** — no SB improves over v1 within noise.

## Reconciliation determination (mechanical read of the rubric)

The rubric doc's SB3 atom IS compound (`detection ≥ 0.90 AND fpr ≤ 0.10`)
— this matches the c45 brief and the c46 auditor's reading. However,
the PARTIAL clause is not gated on SB pass count; it is gated on the
disjunction of THREE explicitly named IMPROVEMENT criteria that are
distinct from the SB pass thresholds:

| SB  | Pass threshold          | Improvement threshold (v1 baseline)    |
|-----|-------------------------|----------------------------------------|
| SB1 | margin > 0.5909         | margin > −0.2093                       |
| SB2 | mean τ ≥ 0.4            | mean τ > −0.0987                       |
| SB3 | detection ≥ 0.90 AND fpr ≤ 0.10 | denominator > 43 (finite non-pinned) |

Applied to c45 observed values (from `data/ear_v2/verdict.json`):

| SB  | Observed             | Pass?          | Improves over v1?    |
|-----|----------------------|----------------|----------------------|
| SB1 | margin −0.2341       | FAIL           | NO (−0.2341 not > −0.2093) |
| SB2 | mean τ −0.0314       | FAIL           | YES (−0.0314 > −0.0987)    |
| SB3 | det 1.000, FPR 0.120, denom 618 | FAIL (FPR overshoot) | YES (denom 618 > 43) |

Two of three SBs improve materially over v1; three of three fall
short of their pass thresholds. Under the rubric's PARTIAL clause
(≥1 shortfall AND ≥1 improvement) both preconditions are satisfied.

The c46 auditor's "0 of 3 SB pass → INSUFFICIENT" reading conflates
SB-pass with SB-improvement. The rubric on disk defines these as
distinct criteria. INSUFFICIENT applies only when "no SB improves
over v1 within noise" — which is not the case here.

**Reconciliation = (A) mapping-clarified.** The c45 `EAR_v2_PARTIAL`
verdict is consistent with the rubric doc. The plan-of-record row
for `M-EAR-1/real-label-training-v2` is amended in this cycle to
make the pass/improvement distinction explicit for downstream
readers.

## Two-verdict rubric (frozen)

- **`ADJUDICATION_MAPPING_CLARIFIED`** — the rubric doc's PARTIAL
  clause is confirmed to use IMPROVEMENT criteria distinct from PASS
  criteria; c45 `EAR_v2_PARTIAL` verdict stands; plan-of-record and
  brief-canonical language updated to make the split explicit;
  `data/ear_v2/verdict.json` unchanged. Ledger event
  `M-EAR-1/real-label-training-v2/mapping-clarified` fires.

- **`ADJUDICATION_VERDICT_SUPERSEDED`** — reserved for the (B) path
  where the rubric doc's PARTIAL clause is read as requiring SB
  pass (compound-only intent). Under this reading `EAR_v2_PARTIAL`
  would be replaced by `EAR_v2_INSUFFICIENT` via a superseding
  verdict.json republish and a `M-EAR-1/real-label-training-v2/verdict-superseded-clone-<k>`
  event. Rubric quote does NOT support this reading, so (B) does
  not fire this cycle.

## Byte-determinism × 2 (mandatory)

- Run `scripts/ear_v2/determinism_check.py` twice into fresh
  `tempfile.mkdtemp()` dirs. Assert SHA-256 equality on
  `corn_head_v2.pt` + `training_result.json`.
- Emit `M-EAR-1/real-label-training-v2/determinism-verified` on equal;
  `M-EAR-1/real-label-training-v2/determinism-failed` on inequal.
- BLAS pins + `torch.manual_seed(0)` + `PYTHONHASHSEED=0` +
  `SOURCE_DATE_EPOCH` + `TZ=UTC` + `LC_ALL=C.UTF-8`.

## SB3 50-control widening (c45 audit MINOR)

- Extend c37/c38 leak-test denominator from 25 to 50 controls; c37 F1
  pooled-variance statistic unchanged (statistic-fix invariance).
- Emit `M-EAR-1/real-label-training-v2/sb3-control-widening` with
  `FPR_NARROWED_PASS` or `FPR_STILL_OVERSHOOT`.
- Byte-determinism × 2 on the widening probe outputs.

## Ledger event contract (this cycle)

Substantive events (auto-suffix `-clone-<k>` on infra families per c33):

1. `_plan/register-v2-adjudication-milestone`
2. `_manager/M-EAR-1-v2-verdict-adjudication-and-gate-closure/mapping-quoted-from-doc`
3. `M-EAR-1/real-label-training-v2/mapping-clarified` (reconciliation A)
4. `M-EAR-1/real-label-training-v2/determinism-verified` OR `/determinism-failed`
5. `M-EAR-1/real-label-training-v2/sb3-control-widening`
6. `_plan/git-log-gate-policy-decision` (path (i) landed)
7. `_manager/M-EAR-1-real-label-training-v2-unfixable-by-audit-clone-1` (retire)
8. `_manager/M-EAR-1-v2-verdict-adjudication-and-gate-closure/anchor-preservation-verified`
9. `_manager/M-EAR-1-v2-verdict-adjudication-and-gate-closure` (parent rollup)
10. `_infra/egress-failure-mode-registry` (lemma proposal)
11. `M-INGEST-1/egress-probe-cycle46` (directive-mandated retry)

Housekeeping (canonical tail):

12. `_run/cycle_46_closed`
13. `_archive/cycle-46-scratch`
14. `_infra/adopt-cycle46-tests`

## Anti-pattern lockouts (unchanged)

- c22/c23/c25 Path A exhaustion — chassis fixed; no re-attempt.
- c31 STILL_GAP AST-forbidden state-extraction methods — AST-grep zero
  under `scripts/ear_v2/` (`get_state`, `save_state`, `save_preset`,
  `load_state`, `set_state(bytes)`).
- c11 CLAP HF SSL — not in scope.
- c15 `i4_stratified.py` — NOT imported.
- No PRNG (SHA-256 tiebreak; `torch.manual_seed(0)` whitelist only).
- No `sidecar_nonfactor` imports.
- `/usr/bin/python3` interpreter guard on every `scripts/ear_v2/*.py`.
- Never delete files; scratch → `tools/stale/`.
