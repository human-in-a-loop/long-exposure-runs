# Stage 5 of 48 — Verify 4 of 23

Slice: M-RECREATE-1 arc — three validated milestones sharing the c37→c38→c39 recreate_v0 chain.

## Milestones examined

### 1. M-RECREATE-1/first-real-audio-clone-0 (c37, fork 675abd086911 clone-0)

- Ledger status: `validated/high`, verdict = `RECREATION_LANDS`.
- Rubric doc: `docs/recreate_v0_first_real_audio_rubric.md`.
- Three-way `rubric_hash` chain (doc SHA / rubric_hash.txt / verdict.json.rubric_hash) all byte-equal `78c61c5d…c2dab9`. PASS.
- Chosen song: `corpus/ratings/7/016__LOCAL__05_02.mp3` (band-7, sha16 `069ebba2…`); SHA-256 tiebreak over 43 candidates; trim 30 s.
- Panels (original vs bare / original vs effects):
  - mel_l1_db: 31.229 / 25.323 → Δ +5.906 dB (rubric threshold ≥ 0.5, satisfied).
  - VGGish cos: 0.2946 / 0.3325; RMS-env: 0.294 / 0.284; centroid_rmse_hz: 1678 / 1929; lufs_m_rmse: 22.99 / 22.85.
- Determinism: 4/4 anchors SHA-equal × 2 (musicxml, midi, bare.wav, effects.wav).
- `preview_untrained_ear=true` caveat present in verdict (M-EAR-1/real-label-training-v0 INSUFFICIENT).
- `anchors_unchanged=true`.
- Verdict CONFIRMED.

### 2. M-RECREATE-1/second-real-audio-batch-clone-2 (c38, fork 33a2a8003c84 clone-2)

- Ledger status: `validated/high`, verdict = `BATCH_LANDS`.
- Rubric doc: `docs/recreate_v0_batch_rubric.md`.
- Three-way `rubric_hash` chain byte-equal `be65f7cb…b718d`. PASS.
- 5 songs selected by SHA-256 tiebreak per band, excluding c37 clone-0 song:
  - band-4 `1d0f6dbb…` Mariah Carey Shake It Off: Δ +7.983 dB
  - band-5 `18fe981c…` Dayme Arocena La Rumba: Δ +2.879 dB
  - band-6 `087687c3…` Tom Misch Red Moon: Δ +5.217 dB
  - band-7 `1d9ac896…` Oba La Vem Ela: Δ +4.670 dB
  - band-6 `0e1e8f20…` Bieber YUKON Live Grammys 2026: Δ +4.425 dB
- 5/5 pipeline OK, 5/5 byte-det × 2, 20/20 anchors, 5/5 positive Δ mel.
- `anchors_unchanged=true`. Wall 848 s.
- Verdict CONFIRMED.

### 3. M-RECREATE-1/full-corpus-recreation-clone-0 (c39, fork c320de981fda clone-0)

- Ledger status: `validated/high`, verdict = `FULL_CORPUS_LANDS`.
- Rubric doc: `docs/recreate_v0_full_corpus_rubric.md`.
- Three-way `rubric_hash` chain byte-equal `4cfca25d…954a2`. PASS.
- 37-song selection (43 corpus − 1 c37 − 5 c38). Threshold: n_positive_mel_delta ≥ 33.
- 37/37 pipeline OK; 148/148 byte-det anchors; 37/37 byte-det × 2.
- 36/37 positive Δ mel; one negative outlier: band-6 `78bdd2ce…` FKJ 10 Years Ago at −1.341 dB (`delta_positive=false`). Passes threshold with margin (36 ≥ 33).
- Per-band: band-4 9/9, band-5 9/9, band-6 10/11 (FKJ negative), band-7 8/8.
- `anchors_unchanged=true`; `n_pipeline_fail=0`; `n_byte_det_x2_fail=0`; `per_anchor_byte_det_failures=[]`.
- Verdict CONFIRMED.

## Cross-arc observations

- Recreation chain c37 → c38 → c39 is architecturally identical (8-stage pipeline, cycle-9 pinned DawDreamer chain, pretty_midi c38 handoff #1 disclosed).
- FKJ single-song regression at c39 is honestly recorded and threshold-absorbed; not a finding.
- Untrained-ear caveat preserved across all three via c36 M-EAR-1/real-label-training-v0 INSUFFICIENT reference — mel-L1 is the only structural verdict anchor. Consistent with c50 rubric-v2 supersede (mel-L1-only gate replaced under M-RECREATE-2, but M-RECREATE-1 verdicts stand on their contemporaneous rubric).
- All three milestones' evidence exists on disk, three-way rubric_hash chain verified.

## Findings

3/3 CONFIRMED; 0 CRITICAL, 0 MODERATE, 0 MINOR emitted this stage.
