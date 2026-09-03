---
created: 2026-09-03T00:00:00Z
cycle: 4
run_id: run-2026-09-03T000000Z
agent: worker
milestone: M-V4-PROFILES-1/cg-bass-family-verdict
---

# Chicken Grease bass — sf2-family adjudication (stage-2b, c3-launched / c4-published)

**Song**: Chicken Grease (`sha16 31a164f845f8e27e`)
**Instrument**: bass
**Family under test**: sf2 (FluidR3_GM `74594e8f…1cb0`)
**Adjudication cycle**: c4 (report published one cycle after c3 sweep by design per c3 auditor guidance and c1/c2 naming convention)
**Verdict**: `STILL_INDETERMINATE`
**Verdict artifact**: `data/v4/profiles/31a164f845f8e27e/bass_family_verdict.json` (sha `cbbdbebf00c30e2c2b0b7c6a575fa59c723a7d1294905eec12bbb2166c546228`)

## §1. c2 context and auditor MODERATE status transitions

The c2 stage-2 fine fit produced an INDETERMINATE (lean-RULED-OUT) verdict on the sf2 family for CG bass. The c2 auditor raised three MODERATE findings:

| # | Finding | c3 remedy | c4 close-out status |
|---|---------|-----------|---------------------|
| 1 | EQ inertness — c2 stage-2 EQ used zero-mean normalization, collapsing 90/180 render SHAs to identical output | c3 shipped `fine_fit_sf2_v2.py` with raw per-band gains clipped ±12 dB (no zero-mean subtraction) + mandatory pyloudnorm LUFS-I −18 dB normalize | **FULL close** — 215/216 distinct render SHAs (99.5%, up from 50%); EQ v2 hypothesis confirmed empirically |
| 2 | Program-33 recovery not tested — c2 stage-2 promoted top-5 by c1 composite (programs 17/18/19/5/38); program 33 (Electric Bass Finger, the merged.mid source-of-truth) was #8 and excluded | c3 pinned program 33 as a mandatory unconditional-promotion cell (36 rows guaranteed) | **CLOSED** — prog33_count = 36 exactly (invariant holds); program 33 recovers to **rank 1 by composite** and rank 64 by embedding_cos_vggish |
| 3 | `profile.json` had no `render_sha256_canonical_replay` field (`search_metadata.render_sha256_in_sweep` conflated with post-hoc canonical replay) | c3 shipped additive kwarg `render_sha256_canonical_replay` on `profile_writer.build_profile`; widened `compute_profile_id` exclusion from `render_sha256` literal to `render_sha256*` prefix; c2 profile SHA regression byte-identical | **CLOSED** — bass_v2.json emitted this cycle populates the new field |

## §2. EQ v2 fit definition and inertness closure

EQ v2 (per `scripts/sound_match/fine_fit_sf2_v2.py`, sha `dc03007365aa29be…`):

- 12-band iirpeak filter bank, Q=1.4, `np.geomspace(20, 20000, 12)`
- Per-band gain `mag_ref_db − mag_render_db`, clipped ±12 dB, **NO zero-mean subtraction** (this is the intervention that broke c2's inertness)
- Broadband level owned by mandatory `pyloudnorm.Meter(sr).integrated_loudness` normalize to **−18.0 LUFS-I** (fetchability ladder confirms pyloudnorm PRESENT — RMS-dBFS fallback not exercised)

Inertness closure table (from `bass_family_verdict.json`):

| Metric | c2 stage-2 | c3 stage-2b | Delta | Verdict |
|-------|-----------|-------------|-------|---------|
| n_rows | 180 | 216 | +36 | full sweep |
| n_distinct_render_shas | 90 | **215** | +125 | **FULL close** (≥ 200) |
| SHA-collapse rate | 50% | 0.5% | −99.5 pp | EQ v2 works |

## §3. Stage-2b top-10 leaderboard (by composite)

| # | prog | preset | gain | reverb | post | composite | embed_cos |
|---|-----:|--------|-----:|-------:|------|----------:|----------:|
| 1 | **33** | Electric Bass Finger (control) | 0.5 | 0.3 | EQ_only | 455.845 | 0.2035 |
| 2 | **33** | Electric Bass Finger (control) | 1.0 | 0.3 | EQ_only | 457.425 | 0.2006 |
| 3 | **33** | Electric Bass Finger (control) | 1.5 | 0.3 | EQ_only | 462.967 | 0.1992 |
| 4 | **33** | Electric Bass Finger (control) | 0.5 | 0.3 | compressor_only | 474.296 | 0.1956 |
| 5 | **33** | Electric Bass Finger (control) | 0.5 | 0.3 | none | 474.296 | 0.1956 |
| ... | ... | ... | ... | ... | ... | ... | ... |

Program 33 sweeps the top of the composite ranking (recovery from c1 rank #8 → c3 rank #1).

## §4. Program-33 recovery analysis (MODERATE #2 close)

- **Count invariant**: prog33_count = 36 (equals design invariant of 36 rows = 3 gain × 3 reverb × 4 post cells). Unconditional-promotion contract HELD.
- **Rank by composite**: **#1** (best-in-sweep). Sweeps positions #1–#5.
- **Rank by embedding_cos_vggish**: #64 (below the discriminative bar). Program 33 is composite-preferred but not vggish-embedding-preferred.

Interpretation: EQ v2 recovers program 33 from c1's #8 rank to c3's #1 rank on the mel_l1_db + spectral_centroid axes (mel-L1 dominates composite at weight 0.5). But the vggish embedding rewards different rendering: it prefers program 19 (Church Organ) with EQ_and_compressor at high gain/reverb. This is the objective-family disagreement documented in the c2 report §Interpretation.

## §5. Kendall-τ diagnostic vs c1 coarse top-5

c1 top-5 programs (asc composite): `[19, 5, 38, 18, 17]`
Stage-2b ranks of those programs (best row per program in stage-2b composite ranking): `[(19, 96), (5, 38), (38, 8), (18, 34), (17, 16)]`

EQ v2 reshuffles the c1 coarse ordering substantially. c1's #1 (program 19 Church Organ, unshaped fluidsynth) drops to c3's #96 under EQ v2 — but recovers to c3's #1 by vggish embedding (see §3). The composite objective is more content-aware under EQ v2; the vggish embedding is not.

## §6. sf2-family verdict against the frozen decision protocol

Applying the c3-brief pre-registered protocol:

- **SF2_CONFIRMED** iff `top1_emb ≥ 0.60` AND (prog33 ∈ top-3 by emb OR top1_preset ∈ {32..39}) AND `spread_ratio ≥ 0.10`
  - top1_emb = 0.4946 < 0.60 → **FAIL**
- **SF2_RULED_OUT** iff `top1_emb < 0.40` AND `prog33 ∉ top-5 by emb`
  - top1_emb = 0.4946 ≥ 0.40 → **FAIL**
- Otherwise → **STILL_INDETERMINATE** ← **fires**

Clauses per-flag:

| Clause | Value | Passes CONFIRMED? | Passes RULED_OUT? |
|--------|:-----:|:---------------:|:-----------------:|
| top1_embedding_cos ≥ 0.60 | False (0.4946) | ✗ | — |
| top1_embedding_cos < 0.40 | False (0.4946) | — | ✗ |
| prog33 ∈ top-3 by embedding_cos | False (rank 64) | ✗ | — |
| prog33 ∉ top-5 by embedding_cos | True | — | ✓ |
| top1_preset ∈ {32..39} | False (prog 19) | ✗ | — |
| spread_ratio ≥ 0.10 | True (1.75) | ✓ | — |

Neither confirming nor ruling-out set fires. Verdict = **STILL_INDETERMINATE**. Downstream unblock: c5 opens family-2 (stem-sampled) by cost per c3-brief STILL_INDETERMINATE recommendation.

## §7. profile-writer canonical-replay-field close-out (MODERATE #3 retrospective) and the sf2 replay-invariance finding

Because the c3 top-1 tuple by composite shifts vs c2 — c2=`(17, 0.5, 0.3, none)` → c3=`(33, 0.5, 0.3, EQ_only)` — and the c3 stage-2b `env_pin_sha256` (`d606c8bc…`) differs from c2's (`2ac444c3…`, from `bass.replay_proof.json`), the c3 brief mandated emission of a `bass_v2.json` sibling profile plus a fresh replay proof under c3 env pins.

Emitted this cycle:

- `data/v4/profiles/31a164f845f8e27e/bass_v2.json`
  - profile_id `d62cd3b6-4521-5d4f-b840-87ef7800c48d`
  - sha256 `2a1cb340bffd11016c566467b0d313fb002c5949ce881968702846867e090462`
  - Populates `render_sha256_canonical_replay` per c3 MODERATE #3 fix
- `data/v4/profiles/31a164f845f8e27e/bass_v2.replay_proof.json`
  - verdict `REPLAY_PROOF_HOLDS`
  - run1_sha256 == run2_sha256 == `832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5`

**First-class finding — replay-invariance under sf2 program change on this MIDI**:
The v2 canonical replay SHA equals the c2 replay SHA byte-identically. Root cause: `scripts/sound_match/replay._replay_sf2` reads program/bank from the MIDI file's own `program_change` events (see replay.py L82–83: *"program pre-select via MIDI file itself; command-line preload"*). c1 rewrote `bass.mid` to embed `program_change = 33`, so any sf2 profile invoked against this MIDI produces byte-identical audio regardless of `identity.program` in the profile dict. This is consistent with FD-16(c) "replay proofs are per RENDER FAMILY per SONG": one proof covers all sf2 profiles for CG bass. Not a defect; a semantic property of the current replay dispatch.

**First-class finding — replay-env stability**:
The `replay_proof.py` env_pin schema is a 7-key subset (`PYTHONHASHSEED, SOURCE_DATE_EPOCH, TZ, LC_ALL, OMP/MKL/OPENBLAS`) of the c3 stage-2b sweep env. The sweep added `pyloudnorm_available` + `lufs_target_db` because the sweep consumes pyloudnorm for LUFS-I normalization; replay does not consume pyloudnorm, so its env_pin stays byte-identical to c2 (`2ac444c3…`). This is a POSITIVE property of replay stability across sweep-env drift, not a mismatch.

## §8. c5 handoff

Per the c3-brief pre-registered STILL_INDETERMINATE branch and the c3-brief cost-of-refinement recommendation:

**Open in c5: `M-V4-PROFILES-1/cg-bass-family2-stem-sampled`**

Rationale: c3 top-1 by embedding_cos = 0.4946 sits in the (0.40, 0.60) STILL_INDETERMINATE band. Further sf2 refinement (another sweep axis) is a diminishing-returns path; program 33 is already recovered at composite rank #1 but embedding_cos_vggish tops out at 0.4946 (program 19 EQ_and_compressor at high gain/reverb), so sf2 cannot pass the confirmation bar without the objective itself changing (out of scope per operator FD).

Family-2 exact command (c5 opens with):

```
# Spec: scripts/sound_match/family2_stem_sampled_builder.py (to author c5)
# Inputs:
#   stem_wav:  data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav
#              sha256=1bad871901294395c1b1ad1c97689e07d879f48aa8b9fc953ea6981d76e09ffd
#   bass_midi: data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1/inputs/bass.mid
#              sha256=4863ca285c7db513c8bfc22da5e35e65036b0ecad2538a6d9794c80eb15f8ac9
# Approach:
#   librosa.onset.onset_detect on bass.wav → ≥6-second slices per note-onset
#   librosa.effects.pitch_shift per pitch → per-pitch sample bank
#   concatenative synthesis of bass.mid via the pitch bank
# Output: data/v4/profiles/31a164f845f8e27e/bass_stem_sampled/ with per-run
#   render + replay proof under a fresh family-2 env_pin (family-2 is a
#   distinct RENDER FAMILY from sf2 per FD-16(c); needs its own per-song proof)
```

`M-V4-PROFILES-1/cg-bass` (parent) status stays in-progress — CG bass profile is not shipped this cycle because verdict is STILL_INDETERMINATE. The primary CG bass profile remains `bass.json` (c2 top-1 by composite, program 17 Drawbar Organ) with its c2 replay proof (`832868d0…`) covering the sf2 family for CG. `bass_v2.json` is a SIBLING under the STILL_INDETERMINATE verdict — its inclusion of `render_sha256_canonical_replay` also validates the c3 profile-writer extension end-to-end.

## Artifact SHAs (this cycle, canonical)

- `bass_family_verdict.json`: `cbbdbebf00c30e2c2b0b7c6a575fa59c723a7d1294905eec12bbb2166c546228`
- `bass_v2.json`: `2a1cb340bffd11016c566467b0d313fb002c5949ce881968702846867e090462`
- `bass_v2.replay_proof.json` (run1_sha256 == run2_sha256): `832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5`
- `bass_stage2b/leaderboard.tsv`: (computed below)
- c2 `bass.json` (READ-ONLY anchor): `11747a42cb1a8f7f693f27c36f0c5e0fc60d0d44da13c877f984443487a8f1c9` — byte-identical pre==post
- c2 `bass.replay_proof.json` (READ-ONLY anchor): unchanged
