---
title: "Music-Gen — `M-GEN-1/batch-v3-i4` (cycle 1, fork 392503ab7d47, clone 1)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — `M-GEN-1/batch-v3-i4` (cycle 1, fork 392503ab7d47, clone 1)

## Abstract

Cycle 1 of clone 1 tested cycle-14 clone-1's I4 stratified rejection sampling intervention's specific numeric prediction — that dropping I4 into the frozen batch-v2 pipeline would drive the M-GEN-1 collision floor at N = 8 from 11 pairs to **0 pairs** (the analytic construction-proof claim from the cycle-14 investigation). The brief's frozen rubric was PASS if ≤ 3 pairs, PARTIAL if 4–7, FAIL if ≥ 8. `scripts/rules/sampling/i4_stratified.py` implements the I4 spec — SHA-256 tiebreak discipline, no PRNG anywhere, stratified per-rule_type without-replacement with a cross-salt `already_picked` set — and `scripts/gen/batch_v3_i4.py` renders the 8-song batch (salts 0..7) through cycle-13's batch-v2 render pipeline verbatim (only the sampler swaps). **Observed collision pairs: 0 raw / 0 coerced (PASS)**, matching the cycle-14 prediction exactly (Δ = −11 vs the batch-v2 baseline). Per-rule-type pairs are all zero, precisely tracking the I4 `predicted_per_type` block. Byte-determinism × 2 holds across 56 SHA-256 artefacts; salt=0 legacy anchor is byte-identical to `data/gen/batch_v2/song_0/*` on all four file kinds (`musicxml d3d75dfb…`, `midi 80dd3420…`, `bare 669fabde…`, `effects 918c8aaa…`), so the reduction is not a coincidence of a wholesale sampler change but a like-for-like comparison with the legacy anchor preserved; batch-v2 files are physically unmodified (mtime evidence pre-dates the sampler file). All 8 songs are byte-distinct across every file kind (no render-SHA collapse masking a hidden collision). Six unit tests are green (`test_salt0_matches_batch_v2_anchor`, `test_determinism_same_input_same_output`, `test_distinct_salts_distinct_outputs`, `test_stratification_predicate_on_synthetic_corpus`, `test_no_prng`, `test_no_sidecar_import`). Zero coherence-gate coercions fired on any salt — the "gate rewrites might introduce cross-type interactions" blind-spot flagged in cycle-14 §7.2 did not fire on this configuration, and the observation is honestly not generalised. Auditor verdict is **VALIDATED / COMPLETE** at `validated/high`. I4's analytic zero-floor construction proof from cycle 14 is now empirically confirmed.

## Introduction

Cycle 13 clone-0's batch-v2 audit found the M-GEN-1 collision floor at N = 8 on the cycle-12-expanded 76-row rules ledger to be **corpus-size-invariant** (11 pairs, not proportionally reduced by the 3× corpus expansion from cycle 9). Cycle 14 clone-1's root-cause investigation attributed 6 of those 11 pairs to a single dominant harmonic rule (`rule_0271c7a9f3b5f606`, F_major, song-scope) that wins the SHA-256 tiebreak at four of the eight salts, producing a `C(4, 2) = 6` clique. The investigation proposed two interventions with specific numeric predictions: **I3** (harmonic-corpus expansion, aggregate floor 9.64 → 8.24 at H = 10 or → 7.78 at H = 20 — a corpus-side lever) and **I4** (stratified rejection sampling inside `scripts/gen/sample_rules.py` — an algorithmic lever with an analytic zero-floor claim for within-rule_type collisions at N = 8, derived from a construction proof rather than a birthday-paradox estimate). This branch is the empirical test of the I4 prediction; the sibling clone-2 branch is the empirical test of the I3 prediction. Together they are the direct comparison the brief called for on the same source ledger and the same render pipeline.

The brief's discipline was explicit: the rubric had to be frozen before the count landed, and if the prediction was falsified (≥ 8 pairs) the branch was to publish honestly as a valid null result — clone-1's structural attribution was descriptive; testing the proposed intervention is the empirical question this branch answered.

## Approach

**I4 sampler.** `scripts/rules/sampling/i4_stratified.py` implements the cycle-14 §I4 spec: per rule_type, rank the pool by SHA-256 of the canonical-JSON content, and draw without replacement using a cross-salt `already_picked` set so no rule_id is ever selected twice across an N-song batch. There is no PRNG anywhere — grep confirms zero imports of `random`, `numpy.random`, `secrets`, or `torch.*seed`; the only textual mention of `sidecar_nonfactor` in the whole module is a docstring line forbidding it, and the AST scan finds zero imports. The sampler raises `I4SamplerError` on pool exhaustion (unit-tested), which is the honest fail-loud path when a caller tries N > K on the smallest pool.

**Cycle-13 pipeline verbatim.** `scripts/gen/batch_v3_i4.py` imports `run_batch` from `scripts.gen.batch_v2` — only the sampler swaps. The cycle-9 pinned DawDreamer chain (Surge XT Chorus + Reverb + gain envelope) is imported unchanged; SF2 SHA `74594e8f…1cb0` is inherited via `batch_v2`; determinism pins are applied before any DawDreamer import; MIDI export goes through the M-SCORE-1 bridge; fluidsynth bare render + DawDreamer effects layer produce 44.1 kHz stereo × 1 323 000 samples per song; scoring goes through the M-HEUR-1 battery + M-TEX-1/panel + CORN head (uncalibrated-labels sentinel). The v3-i4 batch writes to a distinct root `data/gen/batch_v3_i4/`; batch-v2 anchor tree is physically untouched, verified by `find data/gen/batch_v2 -newer scripts/rules/sampling/i4_stratified.py` returning empty.

**Collision counting.** `scripts.gen.collision_analysis.analyze` is imported from cycle 13 — no reimplementation — so the v3-i4 count is a like-for-like comparison against the batch-v2 baseline of 11. The verdict function `_verdict()` encodes the brief's frozen rubric (PASS ≤ 3, PARTIAL 4–7, FAIL ≥ 8) verbatim.

**Determinism × 2.** Two independent runs into distinct output roots SHA-256 the 56-artefact contract set (8 songs × 7 artefacts each) and diff them.

**Salt=0 legacy anchor.** The I4 sampler must preserve batch-v2's salt=0 selection so the legacy identity path is intact and the pair-count reduction is genuinely from I4's algorithmic change rather than from a wholesale sampler replacement. `test_salt0_matches_batch_v2_anchor` verifies byte-identity of song_0 across all four file kinds.

**Interpreter and non-factor discipline.** Interpreter guard `assert sys.executable == "/usr/bin/python3"` in every new module. Non-factor AST isolation clean.

## Findings

### Prediction test

| Prediction (cycle-14 clone-1 I4) | Observed (this branch) | Rubric band |
|---|---|---|
| 0 pairs (analytic construction proof) | **0 raw / 0 coerced** | ✅ **PASS** |

Baseline delta: 11 (batch-v2) → 0 (batch-v3-i4), Δ = −11. Prediction hit exactly.

### Per-rule-type breakdown (matches I4 `predicted_per_type` exactly)

| rule_type | batch-v2 pairs | batch-v3-i4 pairs | Δ |
|---|---:|---:|---:|
| harmonic | 6 | 0 | −6 |
| rhythmic | 2 | 0 | −2 |
| melodic | 2 | 0 | −2 |
| form | 0 | 0 | 0 |
| arrangement | 1 | 0 | −1 |
| **total** | **11** | **0** | **−11** |

Every collision the batch-v2 floor exhibited is eliminated. The stratified-without-replacement mechanism cannot produce a within-rule_type collision at N ≤ K because the `already_picked` set forbids repeat selection; the empirical zero is the mechanical consequence of that construction, not a lucky sample.

### Anchor preservation

- **Batch-v2 anchor tree unmodified.** `find data/gen/batch_v2 -newer scripts/rules/sampling/i4_stratified.py` returns empty; 62 batch-v2 files unchanged since sampler creation.
- **Salt=0 legacy identity** across all four file kinds:

| Artefact | Batch-v2 song_0 SHA | Batch-v3-i4 song_0 SHA | Match |
|---|---|---|:---:|
| `musicxml` | `d3d75dfb…` | `d3d75dfb…` | ✅ |
| `midi` | `80dd3420…` | `80dd3420…` | ✅ |
| `bare_wav` | `669fabde…` | `669fabde…` | ✅ |
| `effects_wav` | `918c8aaa…` | `918c8aaa…` | ✅ |

- Cycle-9 pinned DawDreamer chain imported unchanged; `scripts/tex/render_effects_layered.py` not touched.
- Cycle-13 batch-v2 SHA anchors preserved by construction (distinct batch root).
- Source ledger `data/rules/ledger.jsonl` SHA `a6fd53e9…` unchanged.
- SF2 pin inherited via `batch_v2`.

### Distinctness (no hidden collision via render-SHA collapse)

All 8 songs are byte-distinct across every file kind (musicxml / midi / bare_wav / effects_wav): 8/8 distinct SHAs per artefact class. No two songs collapse to the same render, so the 0-pair count is not an artefact of the counter missing a hidden collision because two salts happened to produce identical renders.

### Byte-determinism × 2

56/56 SHA-256 matches across 8 songs × 7 artefacts each. The determinism harness runs the pipeline into two distinct output roots and diffs SHAs on every artefact.

### Coherence-gate observation (honestly not generalised)

The coherence gate applied *zero coercions* on every one of the 8 salts. The pre-registered blind spot from cycle-14 §7.2 — "gate rewrites might introduce cross-type interactions that mask hidden collisions" — did not fire on this configuration. The report explicitly does not generalise this to a "free consistency dividend" claim, because an expanded ledger (e.g., I3 augmented) with different rule distributions could re-activate the gate on some salt and reintroduce cross-type interaction that this run did not exercise.

### Test suite (6/6 pass)

- `test_salt0_matches_batch_v2_anchor` — salt=0 byte-identity to batch-v2 song_0.
- `test_determinism_same_input_same_output` — same seeds → same outputs.
- `test_distinct_salts_distinct_outputs` — different salts → different picks.
- `test_stratification_predicate_on_synthetic_corpus` — stratification predicate holds on a small synthetic pool.
- `test_no_prng` — grep guard rejects `random / numpy.random / secrets / torch.*seed` imports.
- `test_no_sidecar_import` — non-factor AST isolation.

### Validators

`promise_check` — 0 ERRORs; WARNs on this clone's 8 orphan artefacts (report, figures, sampler, driver, counter, test, sampling `__init__.py`, `summary.tsv`) — expected until post-merge integration concats the shadow ledger. Two pre-existing `_infra/*` "artifact missing" WARNs on the upstream `long_exposure/*` paths predate this branch. `org_check` flags the two new figures under `docs/figures/`, which matches the frozen batch-v2 convention (13 other figures live there).

### Auditor MINOR observations

- Report §10 has a duplicate list marker (two entries labeled "2.") — cosmetic.
- Report §3 "158 WARN" count drifted because sibling clone `i3` artefacts landed after this report was written. Not a defect.
- `SALTS = (0..7)` is a module-level tuple in `batch_v3_i4.py`, not CLI-exposed; the worker flagged the N > K = 10 harmonic-pool ceiling as a follow-up (expose `--n-salts` on the CLI so N > K fails loudly via the existing `I4SamplerError` rather than silently sampling a stale N = 8 default).

## Discussion

Three things about this branch are worth naming.

First, the empirical zero-floor result confirms cycle-14's analytic construction proof exactly — but the confirmation is the interesting part *because* the design of the audit ruled out the two ways the number could be misleading. The salt=0 legacy anchor byte-identity across all four file kinds shows the reduction is not from a wholesale sampler replacement (batch-v2's salt=0 pick is preserved on the same content); the 8/8 distinct-SHA check per artefact class shows the counter did not miss a hidden collision because two salts collapsed to identical renders; the zero coherence-gate coercions across all 8 salts show the gate did not rewrite anything to mask a cross-type interaction. Any one of those checks could have been the mechanism by which a spurious zero appeared, and all three came back clean, so the 0-pair count is a like-for-like reduction from 11 rather than an artefact of the change of sampler.

Second, I4 and I3 are complementary rather than competing interventions and the two parallel branches show it. I4 (this branch) drives the within-rule_type contribution to zero via an algorithmic mechanism that cannot produce a within-rule_type collision at N ≤ K by construction. I3 (sibling clone-2) drives the within-rule_type contribution *for the dominant rule_type* down by widening K, and confirmed its mechanism on the harmonic bucket alone (6 → 1) at N = 8, but leaves the non-harmonic BP floor untouched. I4 alone hits zero at N = 8 but has a hard ceiling at the smallest K (harmonic K = 10 on the current source ledger, so N > 10 would raise `I4SamplerError`); I3 alone reduces the harmonic contribution but does not touch other rule_types. The natural cycle-16+ composition — run I3's augmented ledger through I4's stratified rejection sampler — should hit zero at N = 8 with headroom, and the smallest test is to run this branch's sampler against the sibling clone-2 branch's augmented ledger and re-count.

Third, the coherence-gate silence on this configuration is worth flagging as a not-yet-generalised observation rather than as a general property. Under I4 with the source 76-row ledger at N = 8, the picks the sampler produced were diverse enough that the gate had nothing to coerce; the gate is still wired in and would fire on a configuration where the picks triggered its coherence predicates (c1, c2, c3). Any future report that generalises "I4 makes the gate silent" should first check whether the gate fires under expanded ledgers or higher N. The report is careful about this in §8 and §9; the auditor's cumulative note reinforces the caveat.

The uncalibrated CORN head remains the campaign's biggest open credibility gap; every song in the v3-i4 batch inherits the `synthetic_labels_only` sentinel on its `scoring_v1.json`, and nothing in this branch changes that.

## Open Questions

- **I3 + I4 composition.** Run this branch's sampler against sibling clone-2's I3 augmented ledger (86 rows) at N = 8 and N = 12. I4 alone at N = 12 on the source ledger would fail loudly at the harmonic K = 10 ceiling; the augmented ledger's K = 20 in harmonic opens the headroom. Cheap; empirically informative.
- **Land I4 as the default sampler** behind a config knob (per auditor guidance): keep `sample_ruleset` for the batch-v2 regression path so the salt=0 legacy anchor and the cycle-13 collision baseline remain intact.
- **Promote `test_salt0_matches_batch_v2_anchor`** to `tests/test_integration_cross_branch.py` as a locked cross-branch regression. Cheap, catches any future accidental drift on the salt=0 identity path.
- **Expose `--n-salts` on the batch driver CLI** so `N > K` attempts fail loudly via the existing `I4SamplerError` rather than silently sampling a stale N = 8 default. Small ergonomics improvement, closes the module-level-tuple footgun.
- **Do not generalise the "free consistency dividend" claim** (report §8 item 2) beyond this exact configuration. Under an expanded ledger with different rule distributions, the coherence gate could re-activate and reintroduce cross-type interaction this run did not exercise.
- **CORN-head calibration** — still blocked on rated audio; will fire unattended through M-INGEST-1/egress-ready-automation when it triggers.

## Appendix: Provenance

**Cycle range:** cycle 1 of fork `392503ab7d47`, clone 1.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** researcher `5b392017-f49d-4053-9c9c-37f3d128ac96`, worker `4447207c-fb43-437b-9ade-b327e7ab7ca2`, auditor `6ffff05c-35b5-4f57-8582-8ba609057c82`.
**Auditor verdict:** **VALIDATED / COMPLETE**. Sub-milestone `M-GEN-1/batch-v3-i4` closes at `validated/high`.

**Deliverables on disk.**

- Code: `scripts/rules/sampling/i4_stratified.py` (interpreter-guarded, PRNG-free by grep + unit test, no `sidecar_nonfactor` imports); `scripts/gen/batch_v3_i4.py` (imports `run_batch` from `scripts.gen.batch_v2` verbatim, batch driver); `scripts/gen/collision_count_batch_v3_i4.py` (thin wrapper around `scripts.gen.collision_analysis.analyze` with the frozen rubric).
- Data: `data/gen/batch_v3_i4/{summary.tsv, provenance.jsonl, collision_analysis.json, 8 song sub-directories}`.
- Figures: `docs/figures/batch_v3_i4_collision_heatmap.png` (collision heatmap) + one 8-song grid figure.
- Report: `docs/gen_batch_v3_i4_report.md` (15 081 bytes).
- Tests: `tests/test_i4_stratified.py` (6/6 pass).

**Load-bearing runtime evidence.**

- Collision count: raw pairs 0 / coerced pairs 0 / verdict PASS; per-rule-type pairs all 0.
- Baseline delta: 11 → 0, Δ = −11.
- Determinism × 2: 56/56 SHA-256 matches across 8 songs × 7 artefacts.
- Salt=0 legacy anchor: 4/4 SHAs match batch-v2 song_0 (`musicxml d3d75dfb…`, `midi 80dd3420…`, `bare 669fabde…`, `effects 918c8aaa…`).
- All 8 songs byte-distinct across every file kind (8/8 distinct SHAs per artefact class).
- Batch-v2 tree unmodified: `find data/gen/batch_v2 -newer scripts/rules/sampling/i4_stratified.py` returns empty.
- Source ledger unchanged: `data/rules/ledger.jsonl` SHA `a6fd53e9…`.
- Coherence-gate coercions per salt: 0 across all 8 salts (honestly not generalised).
- Unit tests: 6/6 pass (`test_salt0_matches_batch_v2_anchor`, `test_determinism_same_input_same_output`, `test_distinct_salts_distinct_outputs`, `test_stratification_predicate_on_synthetic_corpus`, `test_no_prng`, `test_no_sidecar_import`).

**Ledger routing.** Four lifecycle shadow-ledger events emitted at `/home/user/music-gen-instance/fork-392503ab7d47/clone-1/promise_ledger.jsonl` (`_plan/register-batch-v3-i4-submilestone`, `M-GEN-1/batch-v3-i4` in-progress → validated/high with `supersedes_path` back to cycle-14 clone-1's `intervention_proposal.json`, `_archive/batch-v3-i4-scratch`). Clone-side orphan warnings will clear at post-merge integration when the fanout conductor collapses the shadow ledger via the cycle-13-validated `_infra/fanout-concat-hardening` machinery.

**Environment stack unchanged since cycle 10.** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`; VGGish rung on the texture panel; CORN head under the `synthetic_labels_only` sentinel. Single-thread BLAS pins throughout.

**Handoff.** Merge report at `/home/user/music-gen-instance/fork-392503ab7d47/clone-1/merge_report.md`. The post-merge conductor should pair this branch's batch-v3-i4 verdict (0-pair PASS) with the sibling clone-2 branch's batch-v3-i3 verdict (6-pair PASS) at fanout collapse, publish the direct intervention comparison the brief called for, fold the four clone-1 shadow events into the root ledger via `_infra/fanout-concat-hardening`, and consider the cycle-16+ composition test (I3 augmented ledger through I4 sampler) as the natural follow-up.

<verdict>validated</verdict>
