# Merge Report — c57 Branch B (clone-1, fork f3cd021663f4)

**Objective:** W2 Musical Time + Repetition (operator directive priority 2).
**Verdict:** `MUSICAL_TIME_PARTIAL`.
**Deliverable:** `docs/rc10_musical_time_report.md`.

## Landing summary

| stage | status |
|---|---|
| Rubric pre-registration (mtime hard, git-log advisory) | ✓ |
| Three-way rubric_hash byte-equality (doc == txt == verdict) | ✓ SHA `635499e6…f07a1ee6` |
| D1 tempo/beat/downbeat survey | ✓ librosa (madmom FETCH_FAIL logged) |
| D2 16th-note grid + micro-timing offsets | ✓ 30 files, deviations ∈ [-125, +125] ms |
| D3 loop-length detection | ✓ 2/5 pass ≥ 0.6 conf |
| D4 consensus aggregator + round-trip contract | ✓ 5/5 round-trip PASS |
| D5 cross-stem energy seed table | ✓ 6,367 rows |
| D6 verdict emission | ✓ `MUSICAL_TIME_PARTIAL` |
| Byte-determinism × 2 | ✓ n_mismatch=0 |
| Anchor preservation (48 SHAs) | ✓ pre==post byte-exact |
| Test suite | ✓ 22/22 PASS |
| promise_check | ✓ 0-ERROR post plan-of-record registration |

## Cross-branch conflict scan

**None.** This branch writes only to `docs/rc10_musical_time_{rubric,report}.md`,
`scripts/recreate_v2/musical_time/*`, `data/rc10_musical_time/*`,
`tests/test_rc10_musical_time.py`, and `tools/stale/c57_musical_time_emit_events.py`.

- Clone-0 (Branch A gold-set) wrote to `data/rc10_gold_set/*` and
  `docs/rc10_gold_set_*`. No overlap.
- READ-ONLY anchors verified byte-identical: c33 render_stem.py, c50 v2
  rubric, c49 v1 rubric, focus_set_v2.json, 30 baseline rc9_6stem WAVs,
  5 rc5_tempo_bpm.json, c55 v2 winner verdicts (drums-v2 PARTIAL, bass-v2
  FAILS, ab-refresh LANDS).

## Ledger events emitted (9 total)

Landed at lines 962-970 of `promise_ledger.jsonl`:

1. `M-RECREATE-2/.../musical-time/pre-registration`
2. `M-RECREATE-2/.../musical-time/tempo-survey-emitted`
3. `M-RECREATE-2/.../musical-time/grid-quantized`
4. `M-RECREATE-2/.../musical-time/loop-length-detected`
5. `M-RECREATE-2/.../musical-time/aggregator-round-tripped`
6. `M-RECREATE-2/.../musical-time/verdict-emitted`
7. `_archive/cycle-57-scratch-clone-1`
8. `_infra/adopt-cycle57-tests-clone-1`
9. `M-INGEST-1/egress-probe-cycle57-clone-1`

Substantive `M-*` sub-leaves + egress-probe registered in
`plan_of_record.md` under the 5-col Milestones table (7 new rows appended
after the clone-0 registration block).

## Handoffs for c58 integrator + operator

1. **What If I Go loop confidence 0.424 blocks LANDS.** Sole mandatory
   failure. Candidates: halve tempo to 100.4 BPM and retry; researcher
   tap-test the 198 vs 100 BPM options; accept PARTIAL as first-class
   negative and revise the rubric LANDS threshold for c58.
2. **Peach Dream loop confidence 0.147.** Chosen_section may be a
   bridge/solo. Try alternative bar features (MFCC-delta or chroma-only).
3. **W4 concatenative resynthesis (c58) can consume this branch's outputs
   directly.** `consensus_loop.json` + `per_repeat_deviations.tsv` +
   16th-grid quantized notes are the substrate.
4. **Cross-stem energy seed table** ready for c58 cross-stem
   reconciliation lemma (root cause of the c54 kick over-classification
   the operator surfaced).
5. **madmom quarantined venv** — if operator wants an ensemble candidate,
   install into a new `workspace/madmom_venv` following c6 basic-pitch
   precedent. Egress currently blocked.

## Environmental notes

- Egress: HTTP 429 + tv_embedded unchanged (24+ cycles). Path-A probe fired
  per c49 policy.
- No PRNG, no `sidecar_nonfactor` import, `/usr/bin/python3` guards
  present, c48 env-flag defaults OFF.
- Determinism env pins: `OMP=MKL=OPENBLAS_NUM_THREADS=1` +
  `PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1756463424` + `TZ=UTC` +
  `LC_ALL=C.UTF-8`.

## Attribution

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012fmwHN7SrwdbP3sjkjeCxy
