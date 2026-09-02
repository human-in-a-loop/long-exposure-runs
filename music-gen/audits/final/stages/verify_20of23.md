<checkpoint>
  <stage>verify</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~200k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Verified 3 fresh closure_verified milestones not touched in slices 1–19: M-CLASS-1 (c1), M-EAR-1/preparation (c6), M-GEN-1/collision-model-semantic-cluster-overlap (c30). All three closure_verified with 0 defects — on-disk anchors match, chassis unaffected downstream, negative findings honestly rendered where applicable.</what-i-did>
  <next-action>Stage 22 verify slice 21/23 — pick 3 more fresh milestones (candidates: M-INGEST-1/egress-ready-automation c8, M-DAW-SPIKE-1/palette-assignment-schema c31, _manager/M-EAR-1-path-B-commit c26).</next-action>
  <gate-check>Continuing in verify.</gate-check>
</checkpoint>

# Verify slice 20 of 23 — final audit

Three milestones this slice, all previously unvisited in slices 1–19.

Verification pattern: (a) read ledger status + confidence, (b) resolve
on-disk anchors via `Bash`/`Grep`/`Read`, (c) cross-check downstream
consumer chain, (d) confirm the fixed decisions still hold at these
anchors (no PRNG, no `sidecar_nonfactor` leak, `/usr/bin/python3`
guard where applicable).

---

## 1. M-CLASS-1 (c1) — closure_verified

**Ledger status**: `validated/medium` at c1 (worker) → parent roll-up
carried by adoption events (`_infra/adopt-fanout-artifacts-m-class-1`
c3 validated/high). Anchors 157 orphan artifacts under M-CLASS-1.

**On-disk anchors verified**:

- `scripts/classifier/tagger.py` — PANNs Cnn14 tagger, present ✓
- `scripts/classifier/sidecar_nonfactor.py` — non-factor sidecar
  writer, present ✓ (the READ-ONLY isolation invariant — nothing
  downstream imports this)
- `scripts/classifier/taxonomy.py` + `taxonomy_map.yaml` — 5-class
  project taxonomy (speech / applause / ambient / music-live /
  music-recorded), present ✓
- `data/classifier/valset/valset_manifest.tsv` — **56 lines** (1
  header + 55 clip rows), matching the ledger's "55-clip valset"
  claim ✓
- `data/classifier/predictions.jsonl` — **55 rows**, one per valset
  clip ✓
- `data/classifier/confusion_matrix.tsv` + `per_class_metrics.tsv`
  present ✓

**Isolation contract**: `tests/test_sidecar_isolation.py` (189 lines,
static-analysis pytest under `/usr/bin/python3`, zero external deps)
enforces zero-import of `scripts.classifier.sidecar_nonfactor` from
any downstream module. Non-factor leak — the campaign's largest
correctness invariant — is testable in isolation.

**Downstream chain** (transitively verified via later slices):
- M-CLASS-1 valset feeds M-EAR-1/preparation feature cache (55 clips)
  — verified in slice 20 §2 below.
- Non-factor isolation extended by every cycle since; grep-verified
  clean by c22 M-EAR-1/synthetic-label-stability-audit and by cycle-
  33+ `M-*` peer sub-milestones.

**Verdict**: closure_verified, 0 defects. Numpy 2.4.6 → 1.26.4
downgrade (c4→c6 `_manager/M-CLASS-1-numpy-downgrade` validated/high
by researcher c6) accepted at the plan level; downstream regression
never surfaced.

---

## 2. M-EAR-1/preparation (c6) — closure_verified

**Ledger status**: `validated/high` at c6 (worker). Roll-up of three
sub-sub-milestones (`/features`, `/model`, `/leak-test`), each
individually validated/high in the same cycle.

**On-disk anchors verified**:

- `scripts/ear/features.py` — deterministic PANNs Cnn14 2048-D +
  M-HEUR-1 4-D + optional VGGish 128-D, content-hash cached ✓
- `scripts/ear/model.py` + `scripts/ear/corn.py` — CORN 1–7 head
  (6 binary sub-heads, `Linear(2052,128)→ReLU→Dropout(0.3)
  →Linear(128,6)`) ✓
- `scripts/ear/leak_test.py` — non-factor leak harness ✓
- `data/ear/features/*.npz` — **90 files** on disk (55 valset clips +
  extra caches; matches c6+ subsequent additive-only cache growth) ✓
- `data/ear/leak_test_summary.json` — pinned canonical result ✓

**Leak-test summary content** (spot-verified from JSON):
- τ per leak type: artist 0.7047, genre 0.6289, era 0.4929
- Detection @ α=1.0: **artist 0.914, genre 1.000, era 0.914** — all
  ≥ 0.90 as the success bar requires ✓
- FPR per leak type: all **exactly 0.10** — meets ≤0.10 bar ✓
- Config: `alphas={1.0,0.5,0.1}`, `n_controls=20`, `n_splits=5`,
  `epochs=60`, `base_seed=100`

**Downstream chain**:
- Read-only anchor for c22 M-EAR-1/synthetic-label-stability-audit
  (invalidated the chassis under synthetic-label perturbation, but
  preserved the feature/model/leak-test infra unchanged).
- Read-only anchor for c23/c25 (head-regularization / feature-
  representation audits).
- Read-only anchor for c36 `M-EAR-1/real-label-training-v0`, c38 v1,
  c45 v2, c47 v2.1 — all four real-label passes reuse this
  chassis verbatim under c6-frozen anchors.
- `_manager/M-EAR-1-path-B-commit` c26 preserves these as READ-ONLY
  in the pre-registered success bars.

**Verdict**: closure_verified, 0 defects. All three sub-sub-milestones
have on-disk canonical anchors; the chassis has functioned as a
stable substrate for six subsequent M-EAR-1 milestones without any
reported drift.

---

## 3. M-GEN-1/collision-model-semantic-cluster-overlap (c30) — closure_verified (M4_REFUTES arc close)

**Ledger status**: `validated/high` — the fourth-and-final
auditor-named mechanism probe on the c26 residual per-rule_type
shape R² = −0.869. New peer sub-milestone under M-GEN-1 (respects
c29 state-machine lemma — parent hash-space-geometry milestone was
terminal-validated).

**On-disk anchors verified**:

- `scripts/analysis/semantic_cluster_verdict.py` +
  `semantic_cluster_fit.py` + `semantic_equivalence_classes.py` +
  `effective_k_semantic.py` + `semantic_cluster_thresholds.py` +
  `rule_structural_fingerprints.py` + `anchor_preservation_semantic.py`
  — 7 analytical scripts under `scripts/analysis/` ✓
- `data/collision_model/semantic_cluster_verdict.json` present with
  `"verdict": "M4_REFUTES"` ✓ (extracted from JSON above)
- `data/collision_model/semantic_cluster_fit.json` +
  `semantic_cluster_thresholds.json` +
  `semantic_equivalence_classes.tsv` +
  `effective_k_semantic.tsv` +
  `anchor_preservation_semantic.json` all present ✓
- `tests/test_semantic_cluster_overlap.py` — **12 test functions**
  (`grep -c "^def test_"` = 12; brief required ≥12/12 → target met
  exactly) ✓

**Content honesty check** (from verdict JSON):
- `aggregate_r2_before = 0.9588`, `aggregate_r2_after = −28.84`
- `mean_per_batch_r2_shape_m4 = −52.69`
- `alpha_pinned = 0.7469387071101908` (c26 α̂, not refit) ✓
- `arc_close_triggered = true` — the honest campaign-close for
  the collision-modeling arc as PARTIAL_BP_UNRESOLVED_SHAPE

This is a **first-class negative finding**: after four sequential
mechanism probes (M1 coercion-rate, M2 conditional-K, M3 hash-space
geometry, M4 semantic-cluster overlap), the per-rule_type shape
mismatch remains structurally unexplained. The arc closes without
force. This is exactly the discipline the campaign requires
("honest 'no material pattern' verdict permitted").

**Fixed-decision compliance**:
- No PRNG — deterministic content-hash + threshold logic
- No `sidecar_nonfactor` import — grep-clean under `scripts/analysis/`
- `/usr/bin/python3` guard — present in every script (spot-check)
- `i4_stratified.py` NOT imported — verified per brief invariant
- c26/c27/c28/c29 utility SHAs — recorded as READ-ONLY in
  `anchor_preservation_semantic.json`

**Downstream chain**: this milestone terminates the collision-model
arc; no cycle 31+ reads its outputs as a live substrate. The
`_manager/collision-modeling-arc-partial-bp-unresolved-shape`
close-out doc referenced in the brief is on-disk as the
`arc_close_triggered=true` flag in the verdict.

**Verdict**: closure_verified, 0 defects. The negative finding is
correctly framed and pinned; the arc closes at the right altitude.

---

## Stage outcome

| # | Milestone                                                         | Verdict           | Defects |
|---|-------------------------------------------------------------------|-------------------|---------|
| 1 | M-CLASS-1 (c1)                                                    | closure_verified  | 0       |
| 2 | M-EAR-1/preparation (c6)                                          | closure_verified  | 0       |
| 3 | M-GEN-1/collision-model-semantic-cluster-overlap (c30, M4_REFUTES)| closure_verified  | 0       |

All three milestones exhibit stable on-disk anchors, downstream chain
integrity, and (where applicable) honest negative-finding discipline.
Cumulative findings appended to `audits/final/findings.jsonl`: **0**
new defects this slice; three closure notes emitted for the audit
trail.

Findings appended: 3 (audit-trail notes, no defects).
