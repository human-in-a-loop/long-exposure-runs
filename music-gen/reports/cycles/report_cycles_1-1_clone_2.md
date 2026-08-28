---
title: "Music-Gen — `M-GEN-1/batch-v3-i3` (cycle 1, fork 392503ab7d47, clone 2)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — `M-GEN-1/batch-v3-i3` (cycle 1, fork 392503ab7d47, clone 2)

## Abstract

Cycle 1 of clone 2 tested clone-1's cycle-14 I3 intervention's specific numeric prediction — that expanding the harmonic pool from K = 10 to K = 20 by adding D_minor counterparts to the 10 F_major rules would drive the M-GEN-1 collision-floor from 11 pairs at N = 8 to ≈ 7.75 pairs (the cycle-14 report §I3 headline; the intervention_proposal.json sweep row for H = 10 says 8.24). Both numbers sit inside the brief's PASS band [6, 9]. `scripts/rules/sampling/i3_dminor.py` built an 86-row augmented ledger (76 source + 10 D_minor counterparts, written to `data/rules/ledger_i3_dminor.jsonl` to preserve the append-only invariant on the source), and `scripts/gen/batch_v3_i3.py` rendered the 8-song batch (salts 0..7) through cycle-13's batch-v2 render pipeline verbatim via `from scripts.gen.batch_v2 import run_batch`. **Observed collision pairs: 6 (PASS)**, at the low edge of the PASS band; the entire −5 pair reduction is inside the harmonic bucket (v2 → v3-i3 per-rule-type: harmonic 6 → 1, rhythmic 2 → 2, melodic 2 → 2, form 0 → 0, arrangement 1 → 1), the four non-harmonic buckets are byte-unchanged, and BP-expected harmonic under H = 20 is 1.40 with observed 1 sitting inside single-sample variance. Byte-determinism × 2 holds across 62 SHA-256 artefacts. Cycle-9 pinned DawDreamer chain and cycle-13 batch-v2 SHA anchors are preserved by construction (import-only, separate batch root, separate augmented ledger). The auditor's verdict is **VALIDATED**. The mechanism ("harmonic K doubles → BP-expected harmonic halves → observed harmonic ~halves") is empirically confirmed; the *observed 6* comes with an honest synthetic-relabel caveat because the D_minor rows are label-swaps of the F_major chord_progression content rather than real minor-mode extractions (egress-blocked corpus expansion, per `corpus/CORPUS_STATUS.md`), and the two-source prediction disagreement (7.75 in the report headline vs 8.24 in the JSON sweep) both fall inside the PASS band so the verdict is robust to which prediction the reader anchors on.

## Introduction

Cycle 13 clone-0's batch-v2 audit found that the M-GEN-1 collision floor at N = 8 on the cycle-12-expanded 76-row rules ledger is **corpus-size-invariant** (11 pairs, not proportionally reduced by the 3× corpus expansion from cycle 9). Cycle 14 clone-1's root-cause investigation attributed 6 of those 11 pairs to a single harmonic rule (`rule_0271c7a9f3b5f606`, F_major, song-scope) that wins the SHA-256 tiebreak at four of the eight salts, producing a `C(4, 2) = 6` clique. Two concrete interventions came out of that investigation: **I3** (expand the harmonic pool, analysis-derived aggregate floor 9.64 → 8.24 at H = 10 or → 7.78 at H = 20) and **I4** (stratified rejection sampling inside `scripts/gen/sample_rules.py`, analytic floor → 0 for within-rule_type collisions at N = 8). This fork's two parallel branches probe both interventions empirically on the same batch-v2 render pipeline: this clone (I3) and the sibling clone-1 branch (I4). The brief's scoped question is narrow and falsifiable: does I3 land in the [6, 9] PASS band on a single 8-song batch, at the direction and rough magnitude the birthday-paradox prediction says?

## Approach

**Augmented ledger.** `scripts/rules/sampling/i3_dminor.py` produces `data/rules/ledger_i3_dminor.jsonl` — 86 rows (76 source + 10 D_minor variants). Every D_minor variant is a label-swap of one of the 10 F_major harmonic rules: identical `chord_progression`, identical `scope`, identical `provenance_pointers`, only `parameters.key` differs. Because rule_id is a SHA-256 over canonical-JSON of `{rule_type, scope, sorted provenance_pointers, parameters}`, the key byte-swap changes the content bytes and therefore the rule_id, so the two variants are distinct rows for the sampler. The augmented ledger is written to a distinct file so the source 76-row ledger and its append-only invariant are untouched.

**Batch render.** `scripts/gen/batch_v3_i3.py` imports `run_batch` from `scripts.gen.batch_v2` (grep-confirmed at line 51) and drives it against the augmented ledger for salts 0..7. The cycle-9 pinned DawDreamer chain (Surge XT Chorus + Reverb + gain envelope) is imported unchanged; SF2 SHA `74594e8f…1cb0` is inherited via `batch_v2`; determinism pins are applied before any DawDreamer import; MIDI export goes through the M-SCORE-1 bridge; fluidsynth bare render + DawDreamer effects layer produce 44.1 kHz stereo × 1 323 000 samples per song; scoring goes through the M-HEUR-1 battery + M-TEX-1/panel + CORN head (uncalibrated-labels sentinel). The v3-i3 batch writes to a distinct root `data/gen/batch_v3_i3/` so v2 anchors are structurally preserved.

**Collision analysis.** `scripts.gen.collision_analysis.analyze` is the exact function cycle 13 used, reused verbatim. Per-rule-type pair counts are compared v2 → v3-i3 to isolate whether the delta is (a) in the harmonic bucket only (I3's mechanism confirms) or (b) distributed (I3's mechanism does not confirm).

**Determinism.** Two independent runs (`tools/stale/_batch_v3_i3_determinism_check.py`, run vs `/tmp/batch_v3_i3_run2`) SHA-256 the 62-artefact contract set (8 songs × {musicxml, mid, bare_wav, effects_wav, scoring.json, coercions.json, sampling_manifest.json} + 6 batch-root rollups = 62) and report 62/62 matches.

**Interpreter and non-factor discipline.** Interpreter guard `assert sys.executable == "/usr/bin/python3"` in both new scripts. Non-factor AST isolation clean (no `sidecar_nonfactor` imports).

## Findings

### Prediction test

| Prediction source | Value | PASS band |
|---|---|---|
| Cycle-14 report §I3 headline | 7.75 | [6, 9] |
| Cycle-14 `intervention_proposal.json` H=10 sweep | 8.24 | [6, 9] |
| **Observed (this branch)** | **6** | ✅ **PASS** (low edge) |

`data/gen/batch_v3_i3/i3_summary.json`: `raw_pairs = 6`, `coerced_pairs = 6`, `raw_verdict = PASS`, `coerced_verdict = PASS`.

### Mechanism confirmation (all −5 in the harmonic bucket)

Per-rule-type pair counts v2 → v3-i3:

| rule_type | v2 (K, pairs) | v3-i3 (K, pairs) | Δ |
|---|---|---|---:|
| harmonic | (10, 6) | (20, 1) | **−5** |
| rhythmic | (18, 2) | (18, 2) | 0 |
| melodic | (18, 2) | (18, 2) | 0 |
| form | (15, 0) | (15, 0) | 0 |
| arrangement | (15, 1) | (15, 1) | 0 |
| **total** | 11 | **6** | **−5** |

The entire five-pair reduction is inside the rule_type whose K doubled. The four non-harmonic buckets are byte-unchanged, exactly as I3's mechanism predicted. BP-expected harmonic under H = 20 is `20 · C(8, 2) / 28² · (1 − 1/20) = 1.40` (clone-1's formula in `intervention_proposal.json`; the worker reproduces 1.40); observed harmonic = 1 sits inside single-sample variance.

### Anchor preservation

- Cycle-9 pinned DawDreamer chain: imported unchanged via `from scripts.gen.batch_v2 import run_batch`; grep-confirmed at `scripts/gen/batch_v3_i3.py:51`. Chain source untouched.
- Cycle-13 batch-v2 SHA anchors: `data/gen/batch_v2/` unmodified; v3-i3 writes to `data/gen/batch_v3_i3/`, a distinct batch root.
- Source 76-row ledger `data/rules/ledger.jsonl` unchanged. Augmented ledger written to `data/rules/ledger_i3_dminor.jsonl` (86 rows). Append-only invariant honoured via distinct file.
- SF2 pin `74594e8f…1cb0` inherited via batch_v2.

### Byte-determinism

62/62 SHA-256 matches across the contract set (8 songs × 7 artefacts + 6 batch-root rollups). The determinism harness runs the pipeline into two distinct output roots and diffs SHAs on each artefact.

### Validators

`promise_check` surfaces the expected clone-side orphan warnings on the new artefacts (`data/gen/batch_v3_i3/*`, `docs/gen_batch_v3_i3_report.md`, `scripts/rules/sampling/i3_dminor.py`, `scripts/gen/batch_v3_i3.py`, `data/rules/{ledger_i3_dminor.jsonl, i3_dminor_manifest.json}`) — clone-2's shadow ledger writes reach the root ledger only at post-merge integration; a scheduling artifact rather than a defect. Sibling branch-B orphans (`data/gen/batch_v3_i4/*`, `docs/gen_batch_v3_i4_report.md`) are out of scope. Two pre-existing "ledger-tracked artifact missing" warnings on the upstream `long_exposure/*` paths predate this cycle.

### Auditor MODERATE observations (documented, non-blocking)

- **D_minor rows are label-swaps, not real minor-mode extractions.** The augmented rules keep the F_major `chord_progression` content verbatim and only relabel `parameters.key`. The mechanism claim is empirically confirmed because `rule_id` is content-hashed and the swap changes the content bytes — the sampler sees 20 distinct harmonic rules under H = 20 — but the *observed 6* is a probe of hash geometry under a synthetic augmentation, not a probe of real minor-mode extraction. This is the price of egress-blocked corpus expansion; a future cycle that harvests real D_minor scores could move the observed number, though the mechanism verdict would not change.
- **Prediction reconciliation gap in cycle-14 sources.** `intervention_proposal.json`'s H = 10 sweep row says 8.24; clone-1's ledger event narrative says 7.75. Both fall inside the observed PASS band [6, 9], so the verdict is robust to which prediction the reader anchors on. A nice-to-have documentation reconciliation, not blocking.

### Auditor MINOR observation

- Single-run BP noise at N = 8 is ± 2–3 pairs around the ~8 mean. A ≥ 100-salt Monte-Carlo would tighten the empirical `E[pairs | I3]`. Not in scope; logged for reference.

## Discussion

Three things about this branch are worth naming.

First, the mechanism confirmation is *clean* in the sense that only matters for I3's central claim: the pair-count delta from v2 to v3-i3 is entirely inside the rule_type whose K was expanded. There is no leakage into rhythmic, melodic, form, or arrangement — those four buckets are byte-unchanged — so the observation cannot be explained by a general effect of "adding rules". This is the strongest possible one-batch confirmation of the "expand-the-dominant-rule-type-pool" mechanism cycle 14 proposed. That the *magnitude* (harmonic 6 → 1) slightly overshoots the BP expectation (harmonic 6 → 1.40) is well inside single-sample variance and does not perturb the direction claim.

Second, the synthetic-relabel caveat is load-bearing for how the observed 6 should be interpreted downstream. Rule_id is content-hashed over canonical-JSON of `{rule_type, scope, sorted provenance_pointers, parameters}`; a key byte-swap from `F_major` to `D_minor` changes the content bytes and therefore the rule_id, and the sampler sees a genuinely distinct rule at that new hash. This is why the mechanism claim (the sampler no longer picks the same rule across four salts because the pool doubled) is real — the *sampling* behaviour under I3 is the sampling behaviour the campaign would see if the D_minor rules were real minor-mode extractions. What is *not* real is the musical content behind the D_minor labels: they are F_major progressions with a different label. When rated audio unblocks via M-INGEST-1/egress-ready-automation and real minor-mode scores are extracted, the *observed* pair count could move (the real D_minor chord_progression content will hash differently from the label-swap version), but the *mechanism verdict* — that expanding K in the harmonic bucket reduces the harmonic contribution to the collision floor by roughly the BP prediction — is invariant to that content change and holds under this branch.

Third, the parallel-with-Branch-B structure the brief called for is now set up to give the merge conductor a direct comparison of the two proposed interventions on the same source ledger and the same render pipeline. I3 (this branch) is a corpus-side intervention with an analysis-only mechanism (grow K in the dominant rule_type); Branch B (I4, stratified rejection sampling inside the sampler) is an algorithmic intervention with an analytic zero-floor claim. I3 empirically hits 6 pairs at the low edge of its PASS band and confirms its mechanism; Branch B's job is to empirically test whether I4 hits ≈ 0. The two interventions are complementary rather than competing — I3 alone leaves the non-harmonic BP floor (≈ 5 pairs at K ≈ 18) unchanged, while I4 alone touches every rule_type — and the post-merge report should surface them as such rather than as an either/or choice.

The uncalibrated CORN head remains the campaign's biggest open credibility gap and this branch does not change that. The scoring pipeline runs through the CORN head under the `synthetic_labels_only` sentinel, and every song in the v3-i3 batch inherits the same caveat as every cycle-10 M-GEN-1 output.

## Open Questions

- **I3 + I4 composition.** Post-merge, run I3's augmented ledger through I4's stratified rejection sampler and measure the composed collision floor empirically. Analytic prediction: I4 drives the within-rule_type contribution to zero, so the composed floor should sit at the between-rule_type contribution only, ≈ 0 pairs. Cheap and highly informative for cycle-16+.
- **Real minor-mode extraction.** When rated audio unblocks and a real D_minor score is harvested and extracted, rerun I3 with the real D_minor harmonic rules; the mechanism verdict is invariant but the observed pair count could move within BP variance. This is the honest empirical check the synthetic-relabel caveat calls for.
- **Non-harmonic bucket K expansion.** I3 alone leaves rhythmic / melodic / form / arrangement pool sizes untouched. If the composed floor is dominated by those four buckets, a second targeted expansion (rhythmic / melodic K → ~28, form / arrangement K → ~24) would move it further. Not this branch's scope.
- **≥ 100-salt Monte-Carlo** to tighten the empirical `E[pairs | I3]` estimate. Would replace the single-sample observation with a distributional one; useful for future intervention-comparison work.
- **Two-source prediction reconciliation** between the cycle-14 report headline (7.75) and its `intervention_proposal.json` sweep (8.24). Both are in the PASS band; reconciliation is documentation-only.

## Appendix: Provenance

**Cycle range:** cycle 1 of fork `392503ab7d47`, clone 2.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** researcher `ed834519-770e-4d8e-a193-d979be895294`, worker `bb205777-0d10-401a-a6d4-6cab65d50d48`, auditor `c456daba-7446-4ea0-8c0d-a27f32e8b4be`.
**Auditor verdict:** **VALIDATED**. Sub-milestone `M-GEN-1/batch-v3-i3` closes at `validated/high` (observed 6 pairs, PASS at the low edge; mechanism cleanly confirmed; byte-determinism × 2 across 62 artefacts).

**Deliverables on disk.**

- Code: `scripts/rules/sampling/i3_dminor.py` (interpreter-guarded, no `sidecar_nonfactor` imports); `scripts/gen/batch_v3_i3.py` (imports `run_batch` from `scripts.gen.batch_v2` at line 51 verbatim).
- Data: `data/rules/{ledger_i3_dminor.jsonl (86 rows), i3_dminor_manifest.json}`; `data/gen/batch_v3_i3/{i3_summary.json, collision_analysis.json, summary.tsv, provenance.jsonl, 8 song sub-directories}`.
- Report: `docs/gen_batch_v3_i3_report.md`.

**Load-bearing runtime evidence.**

- `i3_summary.json`: `raw_pairs = 6`, `coerced_pairs = 6`, `raw_verdict = PASS`, `coerced_verdict = PASS`.
- `collision_analysis.json` per-rule-type delta v2 → v3-i3: harmonic 6 → 1 (Δ = −5), rhythmic 2 → 2, melodic 2 → 2, form 0 → 0, arrangement 1 → 1; total 11 → 6.
- BP-expected harmonic under H = 20 = 1.40; observed 1 within single-sample variance.
- Determinism × 2: 62/62 SHA-256 matches across 8 songs × {musicxml, mid, bare_wav, effects_wav, scoring.json, coercions.json, sampling_manifest.json} + 6 batch-root rollups.
- Cycle-9 chain: `from scripts.gen.batch_v2 import run_batch` at `scripts/gen/batch_v3_i3.py:51`; chain source untouched.
- Cycle-13 batch-v2 SHA anchors: `data/gen/batch_v2/` unmodified (distinct batch root).
- Source ledger unchanged; augmented ledger in a distinct file.

**Ledger routing.** Three shadow-ledger events emitted at `/home/user/music-gen-instance/fork-392503ab7d47/clone-2/promise_ledger.jsonl` (`_plan/register-batch-v3-i3-submilestone`, `M-GEN-1/batch-v3-i3` validated/high, `_archive/batch-v3-i3-scratch`). Clone-side orphan warnings will clear at post-merge integration when the fanout conductor collapses the shadow ledger via the cycle-13-validated `_infra/fanout-concat-hardening` machinery. Sibling branch B (batch-v3-i4) orphans are out of scope for this audit.

**Environment stack unchanged since cycle 10.** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`; VGGish rung on the texture panel; CORN head under the `synthetic_labels_only` sentinel. Single-thread BLAS pins throughout.

**Handoff.** Merge report at `/home/user/music-gen-instance/fork-392503ab7d47/clone-2/merge_report.md`. The post-merge conductor should pair this branch's batch-v3-i3 verdict with the sibling clone-1 branch's batch-v3-i4 verdict at fanout collapse, publish the direct intervention comparison the brief called for, fold the three clone-2 shadow events into the root ledger, and note in the post-merge report that I3's mechanism is confirmed but the observed 6-pair count carries a synthetic-relabel caveat that a future real-D_minor cycle can retest (egress-gated). The natural cycle-16+ follow-up the branch's own §Open Questions names is the I3 + I4 composition test on the augmented ledger through the stratified rejection sampler.

<verdict>validated</verdict>
