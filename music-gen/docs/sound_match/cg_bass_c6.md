---
created: 2026-09-03T00:00:00Z
cycle: 6
run_id: run-2026-09-03T000000Z
agent: worker
milestone: M-V4-PROFILES-1/cg-bass-family2-stem-sampled
---
# CG bass — cycle 6 (M-V4-PROFILES-1) two-task report

## 1. Opening

c6 is a two-task sequential cycle per the c5 auditor branching table:
Task 1 = fix `scripts/sound_match/replay.py` program-invariance CRITICAL;
Task 2 = family-2 stem-sampled builder for CG bass on the c5 spec foundation.
Sequential in-process (no fanout).

## 2. Task 1 outcome — REPLAY_FIX_LANDS

- **Verdict** (frozen 3-way): `REPLAY_FIX_LANDS`.
- **Rubric hash** (three-way byte-equal chain): doc `a9497ed5…4178ef` ==
  `data/v4/profiles/31a164f845f8e27e/replay_fix_c6_rubric_hash.txt` ==
  `replay_fix_verdict.json.rubric_hash`.
- **Pre-fix `replay.py` SHA**: `e03dad60…f1fbab`.
- **Post-fix `replay.py` SHA**: `419d9558…c9f545`.
- **Fix mechanism**: minimal patch to `_replay_sf2` L79-85. Replaced the
  discarded `_ = setup  # documentation` line with an in-memory `mido`
  MIDI rewrite that strips every existing `program_change` event and
  inserts a fresh `program_change(channel=0, program=profile.identity.program, time=0)`
  at tick 0 of the first note-carrying track. The rewritten MIDI is written
  next to the output WAV (deterministic pure function of source MIDI +
  program) and passed to fluidsynth as the input. Chose MIDI-rewrite over
  the brief's suggested `-o synth.default-preset=…` because fluidsynth has
  no such CLI setting; MIDI rewrite is the more robust deterministic path.
- **Test matrix** (3/3 PASS):
  | Test | Contract | Result |
  |------|----------|--------|
  | A (negative-inversion) | prog 17 vs prog 33 on stripped bass.mid → DIFFERENT SHAs | PASS: prog17=`c69775040c325b86…` ≠ prog33=`832868d0ea8a81ca…` |
  | B (positive determinism) | same profile ×2 fresh tempdirs → byte-identical SHAs | PASS: byte-det SHA `832868d0ea8a81ca…` |
  | C (existing-MIDI neutrality) | `bass_v2.json` vs bass.mid (embeds prog 33) matches profile-forced prog-33 SHA | PASS: both `832868d0ea8a81ca…` |
- **Pre-fix replay SHAs** (both proofs identical, the defect symptom):
  `bass=832868d0…3aeac5`, `bass_v2=832868d0…3aeac5`.
- **Post-fix replay SHAs** (now differ, the fix worked):
  `bass=c69775040c325b865be029316d5ccbaff6b3d2393b238c877bae3f1b74ff019c`,
  `bass_v2=832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5`.
  Cross-proof SHAs differ, proving the fix took effect. bass_v2's SHA is
  unchanged (expected: profile prog 33 matches bass.mid's embedded prog 33).
- **Both proofs recompute** `REPLAY_PROOF_HOLDS` under `env_pin_sha256 =
  2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`.
- **Manager event supersede**: `_manager/M-V4-PROFILES-1-replay-program-invariance-critical`
  moves from `action_required/CRITICAL` (c4/c5) to `superseded`, with
  `supersedes_path` carried as `str` per c14 lemma.
- Pre-fix replay proofs archived at
  `data/v4/profiles/31a164f845f8e27e/pre_c6_fix/{bass,bass_v2}.replay_proof.json`.

## 3. Task 2 outcome — FAMILY2_RULED_OUT (first-class negative)

- **Verdict** (frozen 3-way): `FAMILY2_RULED_OUT` per the frozen rubric
  (embedding_cos_vggish ≤ 0.40 AND panel finite AND replay HOLDS).
- **Rubric hash** (three-way): doc `2dddc32a…91dfe` ==
  `family2_builder_c6_rubric_hash.txt` == `bass_family2_verdict.json.rubric_hash`.
- **Profile**: `data/v4/profiles/31a164f845f8e27e/bass_family2_v1.json`,
  `profile_id = 1f3c104a-2cc4-5e25-a802-d1360f1336ee`,
  `render_family = "stem_sampled_v1"`,
  `render_sha256_canonical_replay = 9b4647cef61fe9d65698d7484551c9d25b70445b8de91d0d34169e2c62523276`.
  Design levers frozen per rubric §3: `single_slice_pitch_shift` +
  `adsr_lite` + LUFS-I −18 dB.
- **Reference f0** (stem): `41.20 Hz` via `librosa.pyin(fmin=E1, fmax=E4)`.
  Notable: pyin locked to the lower bound (E1 = 41.20 Hz exactly), which
  hints at strong subharmonic energy in the 6-second reference stem — a
  first-class honest disclosure of the algorithm's behavior on this
  content, not a defect to retry.
- **Family-2 replay proof**: `REPLAY_PROOF_HOLDS` at
  `data/v4/profiles/31a164f845f8e27e/bass_family2_v1.replay_proof.json`.
  Byte-identical ×2 fresh `tempfile.mkdtemp()` runs
  (`run1 = run2 = 9b4647cef61fe9d65698d7484551c9d25b70445b8de91d0d34169e2c62523276`).
  Family-2 replay is a distinct RENDER FAMILY per FD-16(c); this is its own
  proof, NOT covered by the sf2 proofs.
- **Panel** (frozen weights 0.5 / 0.25 / 0.25):
  | Key | Value |
  |-----|-------|
  | mel_l1_db | 7.6887 |
  | spectral_centroid_rmse_hz | 3262.46 |
  | embedding_cos_vggish | **0.0896** |
- **Comparison vs sf2**: sf2 top-1 embedding_cos = 0.4946 (c4 bass_v2);
  family-2 embedding_cos = 0.0896; **delta = −0.405**. Family-2
  substantially underperforms sf2 on VGGish similarity for CG bass.

## 4. env_pin schema note

The c4 auditor's MODERATE #1 flagged a schema drift between sweep-time
(c3 stage-2b: 9-key including `pyloudnorm_available` + `lufs_target_db`)
and replay-time (7-key subset). c6 preserves the 7-key replay-time
canonical env_pin_sha256 as the authority for replay proofs
(`2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`), the
sweep-time 9-key superset remains available as a downstream-audit richer
manifest describing the same set of bind-time environment variables. Both
proofs (bass, bass_v2, and family-2) carry the identical 7-key hash. This
constitutes closure of MODERATE #1 by explicit scoping: canonical replay
uses the 7-key set; the 9-key sweep-time set is a diagnostic superset.

## 5. Anchor preservation (4 anchors READ-ONLY, byte-identical pre==post)

| File | SHA |
|---|---|
| `data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav` | `1bad871901294395…` |
| `data/v4/profiles/31a164f845f8e27e/bass_family_verdict.json` | `cbbdbebf00c30e2c…` |
| `data/v4/profiles/31a164f845f8e27e/bass.json` | `11747a42cb1a8f7f…` |
| `data/v4/profiles/31a164f845f8e27e/bass_v2.json` | `2a1cb340bffd1101…` |

Plus: `family2_stem_sampled_spike.py` (`000c3ef6…6329e80`) byte-identical
pre==post. bass.replay_proof.json and bass_v2.replay_proof.json ARE expected
to change under the fix and are NOT in the read-only anchor set; their
pre-fix versions live in `pre_c6_fix/`.

## 6. Storage accounting

- df before: `83%`.
- df after: `83%` (unchanged).
- Total new deterministic audio added: family-2 `render.wav` (~350 KB
  under output cap). Well under 500 MB working-audio budget; nowhere
  near 90% ceiling.

## 7. Downstream branch per outcome combination

Outcome: **Task1=LANDS + Task2=FAMILY2_RULED_OUT** →
**c7 opens honest close-out for CG bass**: "neither family
CONFIRMED"; operator escalation ticket for M-V4-SHOWCASE-1 acceptance
policy (should the sf2 top-1 INDETERMINATE profile be pinned as the CG
bass profile despite embedding_cos_vggish=0.4946 being below the 0.60
CONFIRMED threshold?). Family-2 first-cut lever set (single stable slice
at t=0..3s + adsr_lite + LUFS-I −18) is now empirically anti-patterned
for CG bass; any future family-2 attempt on CG bass must justify why
different levers (per-note reference-slice picking, windowed f0 gate,
alternate slice offsets) would materially improve the embedding_cos
above 0.40. Per FD-1 no retry within this cycle.

## 8. Deliverables inventory

Task 1:
- `docs/sound_match/replay_program_invariance_fix_c6_rubric.md` (SHA `a9497ed5…`)
- `scripts/sound_match/replay.py` (post-fix SHA `419d9558…`)
- `tests/test_sound_match_replay_program_invariance.py` (3/3 PASS)
- `data/v4/profiles/31a164f845f8e27e/replay_fix_test_matrix.json`
- `data/v4/profiles/31a164f845f8e27e/replay_fix_verdict.json`
- Refreshed `bass.replay_proof.json` + `bass_v2.replay_proof.json`
  (pre-fix versions in `pre_c6_fix/`)
- Manager event supersede

Task 2:
- `docs/sound_match/family2_stem_sampled_builder_c6_rubric.md` (SHA `2dddc32a…`)
- `scripts/sound_match/family2_stem_sampled_builder.py`
- `scripts/sound_match/replay_family2.py`
- `data/v4/profiles/31a164f845f8e27e/bass_family2_v1.json`
- `data/v4/profiles/31a164f845f8e27e/bass_family2_v1.replay_proof.json`
- `data/v4/profiles/31a164f845f8e27e/bass_family2_v1/render.wav`
- `data/v4/profiles/31a164f845f8e27e/bass_family2_verdict.json`

Envelope:
- `data/v4/profiles/31a164f845f8e27e/anchor_preservation_pre_c6.json`
- `data/v4/profiles/31a164f845f8e27e/anchor_preservation_post_c6.json`
- One-line plan_of_record tail-append
- This report

## 9. Binding constraints held

- FD-1 (no tuning, no retry, no fallback): honored on both tests and
  family-2 verdict; FAMILY2_RULED_OUT emitted as first-class outcome.
- FD-6 (operator ear as LANDS authority): both refreshed proofs and
  family-2 verdict are internal-only; operator ear is the campaign LANDS
  authority.
- FD-16(a): env_pin retained (replay-time 7-key canonical); no drift.
- FD-16(b): never passed `--verify-det` — held.
- FD-16(c): family-2 has its own replay proof (`bass_family2_v1.replay_proof.json`);
  sf2 proofs cover sf2 only.
- Sequential only (no `<parallel_cycle_fanout>` emitted).
- No writes into `data/v3/deliveries/*`.
- No edit to `family2_stem_sampled_spike.py` (byte-identical pre==post).
- No sf2 c4 re-open.
- No sweep this cycle.
- No family-2 sweep this cycle (single-shot builder).
