---
created: 2026-08-28T21:05:00+00:00
cycle: 25
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _run/post-merge-integration-fork-dc8cba4b79eb
supersedes_path: merge_report.md (cycle 24, fork 3fbd8c1ab57c)
---

# Post-Merge Integration Report — Fork dc8cba4b79eb (cycle 25)

## Scope

Worker-only integration cycle for fork `dc8cba4b79eb` (2 clones). Both
sub-cycles declared `done | deliverable=exists`. Researcher and auditor
were skipped per parallel_cycle_fanout collapse protocol.

## Clone verdicts

| Clone | Milestone | Verdict |
|---|---|---|
| 0 | `M-GEN-1/batch-v6-unconditioned-n16` | **validated/high** — verdict `REFUTES_PIGEONHOLE` |
| 1 | `M-EAR-1/feature-representation-audit` | **invalidated/high** — both audited representations FAIL C2' |

### Clone 0 — batch-v6 unconditioned N=16

Used cycle-13's unconditioned SHA-256-tiebreak sampler
(`scripts/gen/sample_rules.py`, no exclusion loop, no rejection) on the
86-row `data/rules/ledger_i3_dminor.jsonl` (live K distribution:
H=20, R=18, M=18, F=15, A=15 — cycle-12 breadth-expansion actuals, not
the brief's stated H=20/R=15/M=15/F=15/A=15). Rendered 16 songs (salts
0..15) through cycle-13's batch-v2 render pipeline verbatim. Cycle-15
`i4_stratified.py` NOT imported (AST + grep verified).

- **26 collision pairs** at N=16.
- Only **26.9%** ({form, arrangement}) — below the 60% PARTIAL bar.
- **76.9%** ({form, arrangement, rhythmic, melodic}) — below the 90%
  K15-FAMILY bar.
- **6/26 pairs are harmonic K=20 collisions** — pigeonhole-forbidden
  by strict pigeonhole prediction, present here anyway.
- Pattern is hash-birthday-shaped, not pigeonhole-concentrated.

Cycle-14's collision-floor **construction proof** survives as a lower
bound (form ≥ 1, arrangement ≥ 1) but **fails as a distributional-shape
predictor**. This is a first-class positive empirical falsification of
the cycle-14 pigeonhole-shape hypothesis at N=16 under the unconditioned
sampler.

Notable discovered facts:
- **K-distribution drift** vs the brief (see above). Verdict is
  unaffected because the rubric union is fixed rule_types, but cycle-26
  briefs must cite the live K distribution.
- **Salts 9 and 15 render collapse**: distinct MusicXML SHAs but
  byte-identical MIDI/bare/effects — mscore3 MIDI export collapses
  different scores to the same event stream. Attribution counts
  rule_ids, not render bytes, so not counted as a rule-collision.
- **Aggregation-method drift** on `data/gen/batch_v2/`: cycle-24
  formatter gets `2a2a30db5d3d9a76`; clone-0's formatter got
  `912e07feeb81c8b6`; this cycle's formatter gets
  `be5726ab1cc843cf`. **Per-file SHAs unchanged across all three**
  (9 aggregation formats probed by clone-0). Anchor-preservation
  contract satisfied.

### Clone 1 — feature-representation audit

Last cheap Path A probe on the ear-model chassis. Cycle-22 falsified
the cycle-6 CORN head chassis at τ ≥ 0.7 on N=55 synthetic labels;
cycle-23 falsified three orthogonal regularized head variants at the
relaxed τ ≥ 0.4 bar. This branch tested the mirror hypothesis: whether
the cycle-6 head over a slimmer feature representation would produce
recipe-invariant rank predictions under the same frozen instrument.

- **HEUR-only 4-D**: C1' PASS (best MAE 0.782 < cycle-6 anchor 0.891);
  **C2' FAIL** (mean τ = **−0.076**, bimodal span [−0.958, +0.951]);
  C3' PASS (`ec429bdf…5e8c`). Overall **FAIL**.
- **PANNs-only 2048-D**: C1' FAIL; **C2' FAIL** (mean τ = +0.006);
  C3' PASS (`f98a498c…d39e`). Overall **FAIL**.
- **VGGish-only 128-D**: **R3 DEFERRED** — cache has `has_vggish=False`
  (cycle-6 clone-2 chose not to invoke `use_vggish=True`); running the
  extractor over 55 clips is out-of-scope per the brief §2. Frontier
  plot carries a deferral marker.

The HEUR-only C1' PASS is scientifically interesting but **not a Path A
rescue**: mean τ near zero with symmetric bimodal span is the
underdetermined-regressor signature at extreme low D (4 features can fit
any per-recipe ordering the labels generate, and the fit picks a
different direction each time). The auditor's report frames this
correctly and does not spin it as a partial positive.

**Pre-registered interpretation rule 2 fires cleanly**: no representation
passes C2', so cycle 26 commits **Path B** (defer all ear calibration to
post-egress real labels). Path A on the ear-model chassis at N=55
synthetic labels is now closed comprehensively across three orthogonal
design axes:

| Cycle | Axis | Result |
|---|---|---|
| 22 | chassis (cycle-6 CORN head) | FAIL (mean τ = 0.059) at τ ≥ 0.7 |
| 23 | head-regularization (ridge / bottleneck / frozen-projector) | 3/3 FAIL at τ ≥ 0.4 |
| 25 | feature-representation (HEUR-4 / PANNs-2048) | 2/2 FAIL at τ ≥ 0.4 |

Six design points, all under the same frozen SHA-anchored / byte-det × 2
instrument, all failing the relaxed C2' bar. The pattern is not a
chassis choice, not a regularization choice, not a feature-dimension
choice — it is that N=55 synthetic labels do not carry recipe-invariant
ordinal information for any reasonable head over any reasonable slice
of the frozen cache.

## Cross-branch integration

**Disjoint file trees. Zero conflicts.**

| Branch | Files touched |
|---|---|
| clone-0 | `scripts/gen/batch_v6_*.py`, `scripts/gen/collision_count_batch_v6.py`, `scripts/gen/plot_batch_v6.py`, `tests/test_batch_v6_unconditioned.py`, `docs/gen_batch_v6_unconditioned_n16_report.md`, `docs/figures/batch_v6_{grid,collision_heatmap,attribution}.png`, `data/gen/batch_v6/*`, `tests/test_integration_cross_branch.py §35` |
| clone-1 | `scripts/ear/{feature_subset_adapter,representation_frontier,stability_audit_v3_representations}.py`, `tests/test_ear_feature_representation_audit.py`, `docs/ear_feature_representation_audit_report.md`, `docs/figures/ear_representation_{frontier,tau_per_variant}.png`, `data/ear/feature_representation_audit/*`, `tests/test_integration_cross_branch.py §36` |

Shared file `tests/test_integration_cross_branch.py` — clones extend
distinct sections; no merge conflict.

## Test suite results

All green:

| Suite | Result |
|---|---|
| `tests/test_batch_v6_unconditioned.py` | 7/7 PASS |
| `tests/test_ear_feature_representation_audit.py` | 7/7 PASS |
| `tests/test_integration_cross_branch.py` (§1–§36, incl. §35 batch-v6, §36 feat-rep) | 0 failures |
| `tests/test_ledger_writer_validation.py` | 21/21 PASS |
| `tests/test_fanout_concat_validation.py` | 17/17 PASS |
| `tests/test_harness_report_namespacing.py` | 7/7 PASS |

All run with `PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure` and
`/usr/bin/python3`.

## Batch-anchor invariance

File counts of prior batch directories unchanged since cycle 24:

| Batch | Files | Aggregate SHA (cycle-25 method) |
|---|---|---|
| `data/gen/batch_v2` | 62 | `be5726ab1cc843cf` |
| `data/gen/batch_v3_i3` | 62 | `42bdc33d33987f4e` |
| `data/gen/batch_v3_i4` | 62 | `b07c231b9373818a` |
| `data/gen/batch_v4` | 74 | `9e9444af3af4b5c1` |
| `data/gen/batch_v5_n16` | 129 | `2f17ab559c37881f` |
| `data/gen/batch_v6` (new) | 138 | `eeff1663d600a21d` |

Aggregate SHAs differ from cycle-24's recorded values because the
aggregation method differs (relative-path + SHA + newline + concat, then
SHA-256); per-file SHAs are unchanged. Clone-0's own harness
independently verified 5 batch anchors + 2 ledgers pre/post (7/7 PASS)
during its run.

## Shadow-ledger auto-concat

**Cycle-22 harness-auto-write-namespacing fix continues to work.**
13 shadow events (6 clone-0 + 7 clone-1) at
`/home/user/music-gen-instance/fork-dc8cba4b79eb/clone-{0,1}/promise_ledger.jsonl`
auto-concat'd into the main ledger. **0 shadow events missing** from the
main ledger. Third consecutive fork (after cc548ca0c2e5 and
3fbd8c1ab57c) auto-concat'd cleanly. Cycle-21 workaround remains
retired.

Ledger row count: 380 → 384 after this cycle's 4 integration events.

## Ledger events emitted this cycle

Via SSoT writer `long_exposure.workspace_bootstrap.append_ledger_event`:

1. `_infra/adopt-fanout-artifacts-fork-dc8cba4b79eb` — validated/high,
   29 orphans adopted (22 `gen_first_gen_*.npz` feature-cache
   side-writes from clone-0 batch-v6 render including 16 pre-existing +
   6 new this cycle; 5 `stability_audit_c3check/*` pre-existing carry-over;
   1 `tools/_audit_inspect.py` new this cycle; 1 `tools/_audit_probe.py`
   pre-existing carry-over).
2. `_infra/cross-branch-integration-test-cycle25` — validated/high.
3. `_run/post-merge-integration-fork-dc8cba4b79eb` — validated/high.
4. `_archive/integration-scratch-fork-dc8cba4b79eb` — validated/high.

## promise_check final state

**0 ERRORs / 11 WARNs** (down from 40 pre-adoption).

All 11 remaining WARNs are pre-existing carry-over from prior cycles:
- 6 trailing-slash canonicalization (lines 10, 17, 88, 161, 265 — plus
  the second line-10 entry) — pre-existing artifact-path drift from
  early cycles.
- 1 `M-EAR-1` parent has no ledger events yet (roll-up event pending
  until real-label training loop fires post-egress).
- 4 `long_exposure/*` + `reports/cycles/report_cycles_13-15_clone_1.md`
  ledger-tracked-artifact-missing (established WARN exemption for
  upstream / prior-clone handoff artifacts).

## Handoff to cycle 26

1. **Path B commit for M-EAR-1.** Researcher should emit a
   `_plan/*` event superseding any assumption that Path A refinement
   remained open; commit to real-label ear calibration behind the
   egress-ready trigger. This is the pre-registered outcome of the
   feature-representation audit interpretation rules.
2. **Anti-patterns to lock for cycle 26** (per clone-1 report §Open
   Questions):
   - No 5th regularized head.
   - No further feature slicing.
   - No re-runs of cycle-22 harness with same features + head.
   - No synthetic-label re-audit variants.
   - The two-VALIDATED-audits × two-INVALIDATED-verdicts × orthogonal
     design axes structure is the strongest possible negative-finding
     structure without real labels. Additional Path A cycles produce
     diminishing information.
3. **Optional VGGish (R3) closure.** Cheap sanity probe if egress remains
   blocked and cycle 26 has spare budget. Would either strengthen the
   Path B commit or unexpectedly reveal a mid-D representation that
   passes. Low expected information; only if truly cheap.
4. **Cycle-26 batch-v7 candidates** (per clone-0 report §9,
   priority-ordered):
   1. **N=32 same sampler same ledger** — strict-pigeonhole
      fully-forced regime.
   2. **Per-K sensitivity sweep at N=16** — test whether primary
      attribution tracks ~N(N−1)/(2K) per rule_type.
   3. **Distributional-shape null model** — simulate SHA-256 tiebreak
      with synthetic ledger of controlled K; compare vs birthday null.
5. **Post-egress next step.** When `data/ear/rated_ready.flag` fires,
   `M-EAR-1/training-loop` real-label run becomes the credibility test.
   **Start from the cycle-6 chassis with the original 2052-D features**;
   do not inherit cycle-23 or cycle-25 negative findings into the
   real-label recipe. Those are chassis-stability findings under
   synthetic labels at N=55, not statements about the real-label recipe.
6. **Cosmetic documentation nits** (from clone-1 auditor MINOR):
   - `docs/ear_feature_representation_audit_report.md` §1.2 phrasing on
     `n_files = 84` covering the 55-clip valset (imprecise given
     disclosed concurrent-clone writes).
   - Front-matter cycle-6 baseline row's τ/MAE context (mixes
     cycle-22-observed τ with cycle-6-anchor MAE — labelled clearly
     in `frontier_summary.json` but a reader could conflate contexts).
   - Report references `docs/figures/ear_feature_representation_tau_{mae_frontier,per_representation}.png`
     but actual on-disk figure names are `docs/figures/ear_representation_{frontier,tau_per_variant}.png`
     (per PoR). Doc-drift only; figure files exist and are correct.
   - Neither of these is a correctness issue.
7. **Trailing-slash artifact canonicalization sweep.** 6 pre-existing
   WARNs from early cycles still open — mechanical fix, low priority.
8. **Cycle-24 handoff items** (still open):
   - Researcher's Path A vs B decision for M-EAR-1 (now definitively
     resolved by this cycle — Path B).
   - Cosmetic fix to `docs/ear_head_regularization_audit_report.md` §7
     line 241 (C1' methodology sentence conflation).
   - Clone-0's two paths for N > K construction proof (subsumed by
     this cycle's REFUTES_PIGEONHOLE finding — construction proof
     shown to be lower-bound only, not shape predictor).
   - Add `min_K < N` pre-flight guard to future batch-vN drivers.
   - Real-label re-run of cycle-23 variants when rated audio unblocks;
     don't inherit synthetic success bar.
   - Cycle-22 handoff items 1, 5 + cycle-21 items 2, 3, 5, 6, 7, 9.

## Environment (unchanged)

Python 3.11.15, torch 2.13.0+cpu, numpy 1.26.4, mscore3 3.2.3,
DawDreamer 0.9.0, basic-pitch 0.4.0 in `workspace/basic_pitch_venv`,
SF2 pin `74594e8f…1cb0`, VGGish rung with cycle-14 content-caveat,
single-thread BLAS pins (OMP/MKL/OPENBLAS=1). Rated audio remains
egress-blocked (`corpus/CORPUS_STATUS.md`); neither branch required it.
