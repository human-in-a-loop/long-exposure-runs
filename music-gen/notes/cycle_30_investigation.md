---
created: 2026-08-29T00:00:00Z
cycle: 30
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/collision-model-semantic-cluster-overlap
---

# Cycle 30 investigation notes — M4 semantic-cluster overlap

Read-only orientation pass before any script lands.

## Cycle-27 shape-mechanism baseline

`data/collision_model/shape_mechanism_verdict.json` verdict:
`NEITHER_EXPLAINS` (R2_M1_mean = -6.273; R2_M2_mean = -10.695;
threshold 0.60).

`data/collision_model/shape_mechanism_fit.json` per-batch shape
R²_scaled (cycle-26 baseline column):

- batch_v2: +0.09705609888773847 (H=6, R=2, M=2, F=0, A=1)
- batch_v3_i3: -0.2522824360406397 (H=1, R=2, M=2, F=0, A=1)
- batch_v6: -0.86898347298394610 (H=6, R=6, M=7, F=3, A=4)

Aggregate mean per-batch shape R²_scaled = -0.3414.

Cycle-30 target: replace K with K_eff-semantic per rule_type per
ledger, α pinned at 0.7469387071101908, and check whether shape R²
lifts.

## Ledger schema (76-row `ledger.jsonl`)

- harmonic: 10 rows. Parameters: key (str, e.g. "F_major"),
  chord_progression (list of str, roman numerals), cadence (str).
- rhythmic: 18 rows. Parameters: meter (str, "num/den"), tempo_bpm
  (float), swing_ratio (float), pattern (list of str tokens).
- melodic: 18 rows. Parameters: contour (enum), range_semitones
  (int), pitch_class_histogram (12-vector summing to 1.0).
- form: 15 rows. Parameters: sections (list of {start_measure,
  end_measure, label}).
- arrangement: 15 rows. Parameters: instrumentation (list of str),
  density_over_time (list of float in [0,1]), layer_events (list of
  {t_s, layer, op}).

Batch source ledger mapping (from
`data/collision_model/bp_fit_results.json`):

- batch_v2 → 76-row `ledger.jsonl` (K: A=15, F=15, H=10, M=18, R=18)
- batch_v3_i3, batch_v4, batch_v5_n16, batch_v6 → 86-row
  `ledger_i3_dminor.jsonl` (K: A=15, F=15, H=20, M=18, R=18)

`ledger_i3_dminor.jsonl` counts confirmed: A=15, F=15, H=20, M=18,
R=18.

## Hash-uniformity cross-reference (cycle-28)

Which cells were most non-uniform (rank-1 was batch_v2 × harmonic at
raw p=0.048716, dominated by rule_0271c7a9f3b5f606 — cycle-13
4-salt clique on pre-I3 76-row ledger, dissolves under I3). If M4
co-varies with hash geometry, the harmonic-batch_v2 shape signature
should be dominated by that rule's semantic cluster.

## Fingerprint plan

Per §<frozen_verdict_rubric>: concatenate typed numeric vectors per
rule_type; cosine distance on L2-normalized concat vector; per
rule_type 20th-percentile of pairwise distances on 76-row ledger
becomes the threshold (locked before any batch-v6 analysis).

Vocabulary handling:
- Roman-numeral bag: {I, i, II, ii, III, iii, IV, iv, V, v, VI, vi,
  VII, vii} (14 dims).
- Cadence one-hot: {none, PAC, IAC, HC, DC, PC, other} (7 dims).
- Rhythmic pattern bag: {kick, snare, hihat, cymbal, tom, rest}
  (6 dims).
- Contour class: {arch, ascending, descending, static, undulating}
  (5 dims).
- Instrumentation multi-hot: {drums, bass, other} (3 dims).

Deterministic (SHA-256 tiebreak on ties; NO PRNG anywhere).

## Anti-pattern watch

- Do NOT read `ledger_i3_dminor.jsonl` in the threshold script.
- Do NOT refit α.
- Do NOT assume post-hoc rule_id remapping.
- Do NOT open sub-sub-milestone under
  `M-GEN-1/collision-model-hash-space-geometry/*` — that milestone
  is terminal-validated (cycle-29 state-machine finding).
- New peer sub-milestone
  `M-GEN-1/collision-model-semantic-cluster-overlap` under M-GEN-1.
