---
created: 2026-08-28T17:20:50Z
cycle: 21
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _run/post-merge-integration-fork-392503ab7d47
supersedes: fork-855d4c2e9945 capstone (cycle 14)
---

# Post-Merge Integration Report — fork 392503ab7d47 (cycle 21)

## Fanout outcome

Three clones landed with **zero cross-branch file-tree overlap on
deliverables**. The fanout conductor's automatic concat step was
SKIPPED with `LedgerConcatError` — see §Shadow-ledger reconciliation
below — and this cycle replays the three shadow ledgers into the main
promise ledger by serial `append_ledger_event` with a small
milestone-id normalization for the one auto-write mid that collided
across clones. No promises lost.

| Clone | Milestone                          | Verdict          | Deliverable                                   |
|-------|------------------------------------|------------------|-----------------------------------------------|
| 0     | _infra/ledger-schema-hardening-v3  | validated/high   | docs/ledger_schema_hardening_v3.md            |
| 1     | M-GEN-1/batch-v3-i4                | validated/high   | docs/gen_batch_v3_i4_report.md                |
| 2     | M-GEN-1/batch-v3-i3                | validated/high   | docs/gen_batch_v3_i3_report.md                |

## Per-clone summary

### Clone 0 — _infra/ledger-schema-hardening-v3

Completes the **4-cycle SSoT ledger-schema hardening arc**:

    writer (c10) -> concat (c12) -> field-type + enum (c14) -> transitions (c15)

Additive changes (all upstream at `/home/user/human-in-a-loop/long-exposure/`,
the established out-of-workspace exemption pattern):

- `long_exposure/tools/_ledger_schema.py`
    * `_STATE_TRANSITIONS`: frozenset of 15 canonical `(prev, next)`
      pairs — covers the brief-specified transitions plus two documented
      historical self-loops (`validated -> validated` parent rollup,
      `in-progress -> in-progress` progress-note update).
    * `validate_history(rows)` — groups by `milestone_id`, sorts by `ts`,
      returns illegal-transition errors annotated with `milestone_id +
      both event_ids + pair-name`.
- `long_exposure/workspace_bootstrap.py`
    * `append_ledger_event` splices new event onto prior same-milestone
      rows and runs `validate_history` **before** opening the ledger file
      (atomicity preserved on transition failure).
    * `_lint_clone_shadow` runs `validate_history` over the whole shadow
      after the per-row `validate_event` pass.
- `long_exposure/tools/promise_check.py`
    * `_check_lifecycle` retains the hand-coded backward-compat rule
      and defers to `validate_history` for the full transition graph.

Proof (from the shipped `docs/ledger_schema_hardening_v3.md`):

- (a) all 301 pre-existing per-milestone histories validate — **0 errors**
  via a dynamic sweep (no grandfathering).
- (b) the cycle-13 line-250 pattern (`validated -> in-progress` without
  `reopened`) rejects at **both** writer (writer suite test_19) **and**
  pre-concat lint (concat suite test_14), with milestone + event_ids +
  transition-pair-annotated messages.
- (c) existing suites remain green: writer 21/21, concat 15/15,
  integration cross-branch §1-§30 0 failures.
- (d) public API of `append_ledger_event` and `concat_clone_ledgers`
  unchanged — same signatures, same exception types, same return types,
  same atomicity contract.

Clone-0's honest surprise from cycle 14 (state-transition drift class
mistakenly diagnosed as enum drift) is now retired.

### Clone 1 — M-GEN-1/batch-v3-i4

Empirical **PASS** on cycle-14's I4 analytic zero-floor prediction
under the frozen `PASS ≤ 3, PARTIAL 4-7, FAIL ≥ 8` rubric:

| Prediction (cycle-14 clone-1 I4)                      | Observed              | Rubric  |
|-------------------------------------------------------|-----------------------|---------|
| **0 pairs** at N=8 (analytic construction proof)      | **0 raw / 0 coerced** | ✅ PASS |

Per-rule-type delta batch-v2 → batch-v3-i4:

| rule_type   | batch-v2 | batch-v3-i4 | Δ  |
|-------------|---------:|------------:|---:|
| harmonic    |        6 |           0 | −6 |
| rhythmic    |        2 |           0 | −2 |
| melodic     |        2 |           0 | −2 |
| form        |        0 |           0 |  0 |
| arrangement |        1 |           0 | −1 |
| **total**   |   **11** |       **0** | **−11** |

Design of the audit ruled out the three ways a spurious zero could
have appeared: (i) salt=0 legacy anchor is byte-identical to batch-v2
across all four file kinds (`musicxml d3d75dfb…`, `midi 80dd3420…`,
`bare 669fabde…`, `effects 918c8aaa…`), so the reduction is a
like-for-like comparison, not a wholesale sampler replacement;
(ii) 8/8 distinct SHAs per artefact class rules out hidden collisions
via render-SHA collapse; (iii) 0 coherence-gate coercions across all
8 salts (honestly not generalised beyond this configuration).
Byte-determinism × 2 across 56 SHA-256 artefacts. 6/6 i4 unit tests
green.

### Clone 2 — M-GEN-1/batch-v3-i3

Empirical **PASS** on cycle-14's I3 D_minor headline prediction of
7.75 pairs at N=8 under the frozen `PASS 6-9, PARTIAL {5,10}, FAIL
otherwise` rubric:

| Prediction source                                     | Value | Rubric  |
|-------------------------------------------------------|------:|---------|
| Cycle-14 report §I3 headline                          |  7.75 | in band |
| Cycle-14 `intervention_proposal.json` H=10 sweep      |  8.24 | in band |
| **Observed**                                          |  **6** | ✅ PASS (low edge) |

Per-rule-type v2 → v3-i3:

| rule_type   | v2 (K, pairs) | v3-i3 (K, pairs) | Δ   |
|-------------|:-------------:|:----------------:|----:|
| harmonic    |    (10, 6)    |     (20, 1)      | −5  |
| rhythmic    |    (18, 2)    |     (18, 2)      |  0  |
| melodic     |    (18, 2)    |     (18, 2)      |  0  |
| form        |    (15, 0)    |     (15, 0)      |  0  |
| arrangement |    (15, 1)    |     (15, 1)      |  0  |
| **total**   |    **11**     |     **6**        | **−5** |

The entire −5 delta is inside the rule_type whose K doubled — mechanism
cleanly confirmed. BP-expected harmonic under H=20 is 1.40; observed 1
is within single-sample variance. Augmented ledger (86 rows) lives in a
distinct file `data/rules/ledger_i3_dminor.jsonl` so the source ledger's
append-only invariant stays intact. Byte-determinism × 2 across 62
artefacts. **Synthetic-relabel caveat**: the 10 D_minor variants keep
the F_major `chord_progression` content verbatim and only change
`parameters.key`; `rule_id` shifts because it is content-hashed, so the
sampler sees 20 genuinely distinct harmonic rules — the mechanism claim
is real, but the observed 6 could move within BP variance once real
minor-mode scores harvest (egress-blocked).

## Shadow-ledger reconciliation

The fanout conductor's concat was skipped with:

    LedgerConcatError: per-milestone ts monotonicity violation on
    milestone_id '_run/report_cycles_1-1' between clone-1 (ts
    2026-08-28T16:59:57Z, promise_ledger.jsonl line 7) and
    clone-2 (ts 2026-08-28T16:54:07Z, line 4)

Root cause: the harness auto-writes a per-clone `_run/report_cycles_1-1`
row into each clone's shadow ledger at reporting time. File-order across
clones (0 → 1 → 2) is not monotonic in `ts` on that mid because clone-2
finished its report before clone-1 did. The concat's
per-candidate-milestone file-order check therefore rejects.

Reconciliation this cycle: rather than re-run concat, replay each
clone's shadow events serially via `append_ledger_event` with a small
milestone-id normalization on the one colliding auto-write mid:

    _run/report_cycles_1-1  →  _run/report_cycles_1-1_clone-{0,1,2}

Serial append uses the writer's own `validate_history`, which permits
the `validated -> validated` self-loop explicitly allowed in cycle-15
clone-0's `_STATE_TRANSITIONS` frozenset. All 3+7+4=14 shadow events
reach the main ledger; the three renamed rows land at
`_run/report_cycles_1-1_clone-{0,1,2}`. Recorded under
`_infra/shadow-concat-skip-reconciliation-fork-392503ab7d47`.

## Ledger + validator state

- promise_ledger: **301 → 321** rows (+14 shadow + +6 rollup)
- `promise_check`: **0 ERRORs**; 17 WARNs, all pre-existing categories
  (6 trailing-slash canonicalization; 1 `M-EAR-1` parent roll-up
  pending; 7 `data/ear/features/gen_first_gen_*.npz` orphans; 3
  upstream `long_exposure/*` out-of-workspace exemption — clone-0
  additively references `long_exposure/tools/promise_check.py`, so
  this count moved 2→3 as expected)
- `tests/test_integration_cross_branch.py`: PASS (0 failures §1-§30)
- `tests/test_ledger_writer_validation.py`: 21/21 pass (18 → 21;
  clone-0 added state-transition cases 19-21)
- `tests/test_fanout_concat_validation.py`: 15/15 pass (13 → 15;
  clone-0 added cases 14-15)
- `tests/test_i4_stratified.py`: 6/6 pass (clone-1 new)

## Handoff to cycle 22 (researcher)

1. **Harness auto-write per-clone namespacing** — the concat-skip root
   cause is not clone behaviour; the harness writes
   `_run/report_cycles_1-1` under a shared mid across clones. Namespace
   the mid at write time (`_run/report_cycles_1-1_clone-<k>`) so future
   fork merges do not require this reconciliation. Small; blocks nothing.
2. **`concat_clone_ledgers` transition sweep** — pre-concat lint runs
   `validate_history` at the emit boundary but concat itself does not.
   Defense-in-depth would add a second pass; touches concat's public
   behaviour surface, so merits its own cycle. (Clone-0 §7 follow-up 1.)
3. **`_INFRA_DRIFT_CLASSES` enumeration index** — cycles 10 / 12 / 14 /
   15 each closed one drift class. A frozenset with representative-test
   pointers would make future audits' cross-cycle triage O(1).
   Documentation-only. (Clone-0 §7 follow-up 2.)
4. **I3 + I4 composition** — the natural next empirical test: run this
   fork's I4 stratified sampler against clone-2's I3 augmented ledger
   (86 rows) at N=8 and N=12. Analytic prediction: composed floor sits
   at the between-rule_type contribution only, ≈0 pairs. Cheap and
   informative. (Both clone reports flag this in their Open Questions.)
5. **`--n-salts` CLI on batch drivers** — expose so `N > K` (harmonic
   K=10 hard ceiling on the source ledger) fails loudly via the existing
   `I4SamplerError` rather than silently defaulting. Small ergonomics.
6. **Promote `test_salt0_matches_batch_v2_anchor`** to
   `tests/test_integration_cross_branch.py` as a locked cross-branch
   regression on the salt=0 legacy anchor. Cheap; catches drift.
7. **VGGish content-caveat surfacing** at M-GEN-1 scoring — still open
   from cycle 14; docstring caveat draft in cycle-14 clone-2 §8 is
   ready to ship.
8. **`M-EAR-1` parent roll-up** — clears one standing WARN; cheap
   documentation-only close.
9. **Real minor-mode extraction** — when rated audio unblocks via
   `M-INGEST-1/egress-ready-automation`, rerun clone-2's I3 with real
   D_minor scores. Mechanism verdict is invariant; observed count could
   move within BP variance. Retires the synthetic-relabel caveat.
10. **CORN-head calibration** — remains the campaign's biggest open
    credibility gap; egress-blocked and armed-not-fired.

## Environment

Unchanged since cycle 10. python 3.11.15 / `/usr/bin/python3`;
torch 2.13.0+cpu; torchvision 0.28.0 workaround; numpy 1.26.4;
music21 9.1.0; mir_eval 0.8.2; mscore3 3.2.3
(`QT_QPA_PLATFORM=offscreen`); fluidsynth with pinned SF2
`74594e8f…1cb0`; DawDreamer 0.9.0; Surge XT Effects.vst3 at
`/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`;
VGGish rung on the texture panel with cycle-14 content-caveat;
single-thread BLAS pins throughout. Egress: **still blocked** per
`corpus/CORPUS_STATUS.md`.
