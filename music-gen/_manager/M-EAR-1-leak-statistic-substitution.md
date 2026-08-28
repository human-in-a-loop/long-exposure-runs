# M-EAR-1 leak-statistic substitution manager note

<!--
created: 2026-08-28T07:40:00Z
run_id: run-2026-08-28T040704Z
cycle: 6
agent: worker (clone-2, fork 3168fb0e47a1)
milestone: _manager/M-EAR-1-leak-statistic-substitution
-->

## Purpose

Canonical on-disk anchor for the `_manager/M-EAR-1-leak-statistic-substitution`
event chain. The ledger events under this milestone_id are the authoritative
history; this file records the decision context in one place for future
cycles.

## Context

The M-EAR-1/preparation research brief recommended the classic
**permutation-drop** leak statistic:

    S_perm = MAE(shuffled_nf) - MAE(actual_nf)

This is the right instrument when the model has *learned* a shortcut through
the non-factor: shuffling nf breaks the learned route and MAE degrades.

On the M-CLASS-1 55-clip valset, two of the three planted non-factors
(`synth_artist`, `synth_era`) are **orthogonal to the audio features** by
construction — artist is round-robin over the manifest, era is a sha256
partition. A CORN head trained on PANNs+M-HEUR-1 features literally
cannot learn a shortcut through those non-factors, so permutation-drop
reports zero even at α=1.0. This is not sensitivity failure; it is a
design mismatch between statistic and plant.

## Options considered

| # | Statistic | Correlated nf (genre) | Orthogonal nf (artist/era) | Verdict |
|---|-----------|:---------------------:|:--------------------------:|:-------:|
| a | Permutation-drop (brief-recommended) | fires | silent | ✗ misses orthogonal plants |
| b | S_resid = η²(residual \| nf)         | ambiguous when model fits well | fires | ✗ misses correlated plants |
| c | **S = max(η²(ŷ\|nf), η²(residual\|nf))** | fires (S_model) | fires (S_resid) | ✓ adopted |

## Decision

**Adopt option (c): S = max(S_model, S_resid) with both statistics computed
as ANOVA-style η² (SS_between / SS_total, bounded in [0,1], scale-free in
y_te).**

- S_model catches the shortcut-learning failure mode (model prediction ŷ
  tracks nf).
- S_resid catches the orthogonal-plant failure mode (nf drives y, model
  cannot follow, all nf-signal ends up in residuals).
- Both are η² fractions, so the same τ works across leak strengths where
  var(y_te) itself differs by construction.
- τ is calibrated FIRST from the no-leak control distribution (≥20
  controls × 5 folds = ≥100 samples per leak type at the 90th percentile);
  planted-leak numbers are computed against the pre-fit τ so they are not
  p-hacked.
- If FPR at the 90th percentile exceeds 0.10 for a specific leak type
  (Monte-Carlo variance around the nominal ceiling), τ for that leak type
  is escalated to the 95th percentile. The per-leak-type percentile is
  recorded in `leak_test_summary.json.config.percentile_for_tau_per_leak_type`.

## Consequences

- **In-scope success bar met.** Detection ≥ 0.90 at α=1.0 per leak type
  is what the campaign actually cares about; both S_model and S_resid
  give slack for calibration-safe escalation to 95th percentile without
  dropping below 0.90.
- **Reader trust cost.** The report §4.3 must document the substitution
  and its rationale (done). Cross-branch integration test §13 asserts
  the file exists and the statistic name is `S_max_eta_squared` in the
  TSV schema.
- **Contract preserved.** The "scramble the non-factor bootstrap"
  language from the campaign prompt still holds: no-leak controls are
  the calibration source; τ is a percentile of that distribution;
  detection is `S >= τ`.

## When to revisit

- **v0 training on real rated audio (parent M-EAR-1).** With the real
  80-song corpus, both non-factor channels (real genre / era / artist
  metadata) will have measurable feature-audio correlation, and
  permutation-drop may become viable as a secondary check. Re-open
  this file if v0 finds S_model or S_resid systematically pathological
  on real data.
- **If a future audit demands the vanilla permutation-drop as an
  additional column** (not a replacement): the harness already stores
  per-fold `mae` alongside `S`, so a `MAE(nf_shuffled) - MAE(nf_actual)`
  can be added in ~20 LOC without disturbing the primary statistic.

## Researcher acceptance

Per cycle-6 audit outcome (CONTINUE): "the substitution is defensible."
Per this cycle's research brief §Fix 5: "researcher accepts the
substitution." This file plus the accompanying ledger event closes the
manager decision.
