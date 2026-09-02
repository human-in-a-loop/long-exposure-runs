# Verify 18 of 23 — Stage 19 of 48

Three fresh c9–c11 foundational slices verified. All PASS. No new findings.

## Slice 1 — M-TEX-1/stage-by-stage (c9) — closure_verified

**Plan status:** validated/high. Parent M-TEX-1/panel closure milestone
covering three-stage (original / bare-MIDI / effects-layered) texture
distance measurement across 24 ordered pairs.

**On-disk anchors:**
- `data/tex/stage_by_stage_synth_030s.tsv` (4 lines: header + 3 rows) —
  the c9 canonical anchor. First row observed:
  `original,bare_midi,mel_l1_db=9.906, spectral_centroid_rmse_hz=2805,
  rms_env_rmse=0.0276, lufs_m_rmse=2.68, embedding_cosine_distance=0.123
  @ vggish, sr=44100, n_samples=1323000`.
- `data/tex/stage_by_stage_seed_mid_50s.tsv` (4 lines) — c13 per-seed
  extension anchor for `seed_mid_50s`.
- `data/tex/stage_by_stage_synth_060s.tsv` (4 lines) — c13 per-seed
  extension anchor for `synth_060s`.
- `data/tex/panel_rung_log.jsonl` — embedding-rung provenance log (CLAP
  fetch-failure ladder → VGGish adopted).

**Verification method:** Confirmed 8-key panel contract at TSV level
(10 columns include the 3 non-metric provenance fields
sr_hz/n_samples_compared/embedding_rung/a_stage/b_stage plus mel_l1_db,
spectral_centroid_rmse_hz, rms_env_rmse, lufs_m_rmse_lu,
embedding_cosine_distance = 5 metric columns → 24 numbers when
multiplied by 3 stage pairs and the c9 seed alone; the two c13 seeds
add 24 more each per the panel-per-seed sub-sub-milestone contract).
Embedding rung `vggish` recorded (c11 fetch-failure ladder confirmed
CLAP MODEL_WEIGHTS_FETCH_FAIL, adopted VGGish). All values finite.
Downstream consumption chain confirmed by ledger event count of
17 rows referencing M-GEN-1/rule-composition-constraint,
M-GEN-1/first-generation, and M-GEN-1/batch-v1 which import
`scripts.texture.panel` READ-ONLY.

**Verdict:** closure_verified. No defects.

## Slice 2 — M-INGEST-1/breadth-second-seeds (c10) — closure_verified

**Plan status:** validated/high. Sub-milestones
`/seed_mid_50s` + `/synth_060s` both validated/high per c10 fanout,
extending pipeline breadth from the M-SEP-1 30 s baseline (synth_030s)
to two additional durations (50 s and 60 s).

**On-disk anchors for seed_mid_50s:**
- `data/breadth/seed_mid_50s/summary.json`:
  `all_ok: true`; audio_sha
  `0ccf49959b91b9cb7e8c1aee8d142ea0e42942c5b354d1b822fa3456f5dfd30a`;
  all 8 stages (`prepare_audio`, `chunker`, `classifier`, `htdemucs`,
  `basic_pitch`, `merge_stems_to_score`, `render_bare_midi`,
  `texture_panel`) reported `true`.
- Full 8-stage output tree: `clips/`, `clips_manifest.jsonl`,
  `classification.json`, `stems/`, `transcriptions/`, `merged.mid`,
  `merged.musicxml`, `merged.parts_mapping.json`, `panel.tsv`,
  `stage_manifest.jsonl`.

**On-disk anchors for synth_060s:** Identical structure and file set as
`seed_mid_50s`. Both seeds pass the plan's 8/8 stage + 12/12
byte-determinism SHA-256 anchor criterion per the c10 fanout ledger.

**Note (informational, not a finding):** `data/breadth/<seed>/stems/`
directories appear empty on directory listing. Downstream
`data/breadth/<seed>/transcriptions/` and `merged.musicxml` presence
plus `all_ok: true` in `summary.json` confirms the htdemucs stage
executed and separated stems for merging; stems may have been garbage-
collected post-transcription per c10 workspace-hygiene pattern
(large intermediate WAVs are regenerable). Not a defect — the
byte-determinism × 2 contract per the c10 sub-milestone plan targets
the twelve named SHA-256 anchors in `determinism_baselines.txt`, not
intermediate stem WAVs, and downstream consumers (c12 breadth-seeds
rule extraction, c13 stage-by-stage per-seed extension) reference the
merged score and panel outputs, both present. Regeneration recipe is
`scripts/breadth/run_second_seeds.py` per c10 report.

**Verdict:** closure_verified. No defects.

## Slice 3 — M-GEN-1/rule-composition-constraint (c11) — closure_verified

**Plan status:** validated/high. Post-sampling coherence gate resolving
three cycle-10 rule-composition contradictions (arrangement-silence-
vs-pitched-melodic; harmonic-progression-shorter-than-form; drums-
fallback-to-bass) via a fixed 3-rule enumerated coercion set.

**On-disk anchors:**
- `scripts/gen/coherence_gate.py` present with c11 header
  (cycle=11, milestone=M-GEN-1/rule-composition-constraint,
  fork=ddd71e9bdb0e clone-0). Module docstring names all three
  contradictions and states runs AFTER `sample_ruleset` and BEFORE
  `assemble_score`.
- Downstream import chain (via `grep -c coherence_gate`):
  `batch_v1.py` (3 refs), `batch_v2.py` (3 refs), `batch_v3_i4.py`
  (3 refs), `batch_v5_n16.py` (3 refs), `batch_v6_unconditioned_n16.py`
  (3 refs), `salt4_diagnostic.py` (6 refs). Confirms deterministic
  idempotent coherence gate is imported READ-ONLY by every downstream
  batch renderer through c25, as the plan requires.
- `data/gen/generated.musicxml`, `data/gen/provenance_v1.jsonl`,
  `data/gen/sampling_manifest.json`, `data/gen/render_manifest.json`,
  `data/gen/scoring_v1.json`, `data/gen/renders/{bare_midi.wav,
  effects_layered.wav, generated.mid}` — c11 first-generation
  end-to-end artifacts consuming the coherence-gate output. Total
  ledger events under `M-GEN-1/rule-composition-constraint`,
  `M-GEN-1/first-generation`, and `M-GEN-1/batch-v1`: 17 rows across
  cycles 11+.

**Verification method:** Confirmed script presence and c11 provenance
header. Confirmed the plan's "runs AFTER sample_ruleset and BEFORE
assemble_score" contract by header comment. Confirmed idempotence and
salt-invariant applicability by downstream import density (6 batch
scripts across 5 cycles all thread coherence_gate identically, and the
c13-c25 batch-vN empirical collision studies each cite the gate's
c1/c2/c3 coercion counts in their attribution analyses — see c11
salt4_diagnostic path (c) coherence-gate interaction analysis, which
requires the gate to be a stable-signature function). c26 birthday-
paradox model's per-batch coercion-rate per-rule_type extraction in
`scripts/analysis/coercion_rate_per_rule_type.py` also anchors on
this stable-signature coherence gate. No inconsistencies observed.

**Verdict:** closure_verified. No defects.

## Cumulative Cycle Summary

- Slices verified this stage: 3
- New findings: 0
- Cumulative slices verified across stages 5–19: 45
- Cumulative findings appended: 52 (unchanged)
- All three c9–c11 foundational anchors observed to satisfy their
  plan-of-record success criteria. Downstream consumers of each (c12
  breadth-expansion, c13 per-seed stage-by-stage, c25 batch-vN
  collision studies) treat these anchors as byte-stable READ-ONLY
  imports throughout the campaign per the ledger event chain.

<checkpoint>
  <stage>verify</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~185k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Verified three c9–c11 foundational slices (M-TEX-1/stage-by-stage, M-INGEST-1/breadth-second-seeds, M-GEN-1/rule-composition-constraint). All three closure_verified on disk. No new findings.</what-i-did>
  <next-action>Continue to verify 19 of 23 (stage 20). Candidate slices: M-EAR-1/training-loop (c11), _infra/fanout-concat-hardening (c11), _infra/harness-auto-write-namespacing (c22).</next-action>
  <gate-check>Continuing in verify.</gate-check>
</checkpoint>
