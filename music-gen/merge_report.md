---
created: 2026-08-28T19:10:00Z
cycle: 16
run_id: run-2026-08-28T040704Z
agent: worker (clone-1, fork cc548ca0c2e5)
milestone: M-GEN-1/batch-v4-compound
---

# Merge Report — Fork cc548ca0c2e5, Clone 1 → M-GEN-1/batch-v4-compound

## Verdict

**CONFIRMS_H0_STRICT** at 0 observed collision pairs at N=8, with 12 of 32
`(salt, file_kind)` cells reproducing the I4-only anchor byte-identically
(4 `matches_i4_only` + 8 `matches_both`). The I3 corpus-side lever and the
I4 algorithmic lever compose **without interference** on this workload.

## What shipped

| Artifact | Path |
|---|---|
| Report | `docs/gen_batch_v4_compound_report.md` |
| 8-song grid figure | `docs/figures/batch_v4_grid.png` |
| Collision heatmap figure | `docs/figures/batch_v4_collision_heatmap.png` |
| Driver | `scripts/gen/batch_v4_compound.py` |
| Collision counter | `scripts/gen/collision_count_batch_v4.py` |
| Anchor comparator | `scripts/gen/batch_v4_anchor_check.py` |
| Plotter | `scripts/gen/plot_batch_v4.py` |
| Unit tests (6/6) | `tests/test_batch_v4_compound.py` |
| Cross-branch §31 | `tests/test_integration_cross_branch.py` (added 11 named checks) |
| Batch outputs | `data/gen/batch_v4/song_{0..7}/{musicxml,mid,bare.wav,effects.wav,scoring.json,coercions.json,sampling_manifest.json,rules.json}` |
| Batch aggregates | `data/gen/batch_v4/{batch_manifest,collision_analysis,collision_matrix.tsv,anchor_cross_reference,hypothesis_verdict,summary.tsv,provenance.jsonl}` |
| Byte-det proof | `data/gen/batch_v4/.byte_determinism_proof.json` |
| Anchor snapshots | `data/gen/batch_v4/.pre_run_anchors.json`, `.i4_sampler_anchor_sha256` |
| Plan of record | `plan_of_record.md` (Milestones + Sub-milestones rows for `M-GEN-1/batch-v4-compound`) |

## Ledger events emitted (per-clone shadow ledger, cc548ca0c2e5/clone-1)

1. `_plan/register-batch-v4-compound-milestone` — validated/high
2. `M-GEN-1/batch-v4-compound` — in-progress/medium (kickoff, investigation-first)
3. `M-GEN-1/batch-v4-compound` — in-progress/medium (first render + collision + anchor XREF; verdict CONFIRMS_H0_STRICT)
4. `M-GEN-1/batch-v4-compound` — in-progress/medium (second byte-det run byte-identical; anchor preservation runtime-enforced; §31 added)
5. `M-GEN-1/batch-v4-compound` — validated/high (terminal, verdict CONFIRMS_H0_STRICT with mechanistic interpretation and cycle-17 follow-up)
6. `_archive/batch-v4-scratch` — validated/high (one-shot emitters moved to `tools/stale/`)

## Sufficiency criteria — all met

- [x] `docs/gen_batch_v4_compound_report.md` published with verdict under frozen rubric
- [x] Verdict machine-readable from `hypothesis_verdict.json` + `collision_analysis.json`
- [x] 8 songs render non-silent (peak > 1e-4 asserted for both bare.wav and effects.wav)
- [x] Byte-deterministic × 2 across all 71 tracked artifacts
- [x] Anchor SHAs for `batch_v2`, `batch_v3_i3`, `batch_v3_i4` byte-identical before/after (runtime-enforced)
- [x] Both ledger files SHA-256-equal before/after (runtime-enforced)
- [x] `tests/test_batch_v4_compound.py` 6/6 pass
- [x] Cross-branch integration test §31 green (suite PASS overall)
- [x] `promise_check` 0 ERRORs (WARNs are pre-integration orphan artifacts adopted by the terminal event; fork integrator will resolve on merge, per cycle-13/15/21 pattern)
- [x] SHA-256 tiebreak, NO PRNG, no `sidecar_nonfactor` imports (AST-checked)

## Anchor-XREF distribution and mechanism (report §4, §7)

| Category | Count / 32 | Salts |
|---|---|---|
| matches_both | 8 | 0, 3 |
| matches_i4_only | 4 | 4 |
| matches_i3_only | 12 | 2, 5, 6 |
| novel | 8 | 1, 7 |

The 4-cell `matches_i4_only` block on salt=4 is the direct CONFIRMS_H0_STRICT
witness: batch-v4 on the 86-row augmented ledger produces byte-identical
whole-song SHAs to batch-v3-i4 on the 76-row source ledger for all four file
kinds. I3's harmonic expansion left I4's rank-0 pick undisturbed after
rejection at that salt for every rule_type.

I3 augmentation only ADDED rules; it never removed or renumbered them. On
non-harmonic rule_types the source and augmented ledgers produce byte-
identical candidate lists → byte-identical hash rankings → byte-identical
I4 rejection behavior. On harmonic, 4 of 8 salts pick a new D_minor variant
(rule_ids in the augmentation manifest); the other 4 coincidentally re-select
an F_major rule. K_harmonic=20 ≥ N=8 keeps I4's 0-pair construction proof
intact; no stratum-shift edge case is tripped → CONFIRMS_H2 ruled out.

## Cycle-17 handoff (single item)

**`M-GEN-1/batch-v4-N16`** — extend the compound to salts 0..15 on the
augmented ledger. At N=16, K_harmonic=20 remains ≥ N; K_rhythmic=18 ≥ N;
K_melodic=18 ≥ N; but K_form=15 and K_arrangement=15 are BELOW N. Expected
outcome under I4's construction proof: collisions land entirely inside
form + arrangement (I4-limit indicators, unrelated to I3). If harmonic
collisions appear at N=16, that would be a genuine CONFIRMS_H2 signal this
branch could not reach. Either way, N=16 is the cheapest deterministic test
that extends the compositional envelope past the K=N boundary.

Alternative (cheaper, weaker): compound against
`data/rules/ledger_i3_expansion_v2.jsonl` with K_harmonic=30 and a
deliberately shrunk K_melodic=6 to probe stratum-shift interference under a
steeper compositional gradient.

## No cross-cycle handoffs required

- Cycle-21 handoff #1 (harness auto-write per-clone namespacing for
  `_run/report_cycles_*`) is unchanged; if this clone's shadow ledger
  collides on merge, the fork integrator reconciles it as cycle-21 did.
- No environment changes; python 3.11.15, torch 2.13.0+cpu, numpy 1.26.4,
  mscore3 3.2.3, DawDreamer 0.9.0, basic-pitch 0.4.0 quarantined venv,
  SF2 pin `74594e8f…1cb0`, single-thread BLAS pins.
- No changes to `data/gen/batch_v2/`, `data/gen/batch_v3_i3/`,
  `data/gen/batch_v3_i4/`, `data/rules/ledger.jsonl`,
  `data/rules/ledger_i3_dminor.jsonl`, `scripts/rules/sampling/i4_stratified.py`,
  `scripts/tex/render_effects_layered.py`, or any file under `long_exposure/`.

## Files touched

Added:
- `scripts/gen/batch_v4_compound.py`
- `scripts/gen/collision_count_batch_v4.py`
- `scripts/gen/batch_v4_anchor_check.py`
- `scripts/gen/plot_batch_v4.py`
- `tests/test_batch_v4_compound.py`
- `docs/gen_batch_v4_compound_report.md`
- `docs/figures/batch_v4_grid.png`
- `docs/figures/batch_v4_collision_heatmap.png`
- `data/gen/batch_v4/` (batch outputs, 8 songs × 8 files + 7 batch-level files)
- `tools/stale/_emit_batch_v4_events.py`
- `tools/stale/_emit_batch_v4_events_final.py`
- `tools/stale/_byte_determinism_check.py`

Modified:
- `plan_of_record.md` (Milestones + Sub-milestones rows for `M-GEN-1/batch-v4-compound`)
- `tests/test_integration_cross_branch.py` (added §31, 11 named checks)

Untouched (per anchor-preservation contract, runtime-enforced):
- `data/gen/batch_v2/`, `data/gen/batch_v3_i3/`, `data/gen/batch_v3_i4/`
- `data/rules/ledger.jsonl`, `data/rules/ledger_i3_dminor.jsonl`
- `scripts/rules/sampling/i4_stratified.py`
- `scripts/tex/render_effects_layered.py`
- `scripts/gen/render_pipeline.py`, `scripts/gen/batch_v2.py`, `scripts/gen/batch_v3_i4.py`, `scripts/gen/batch_v3_i3.py`
