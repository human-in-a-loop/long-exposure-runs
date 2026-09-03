---
title: "Music-Gen v4 closure campaign — cycles 1–3"
date: "2026-09-03"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v4 closure campaign — cycles 1–3

## Abstract

Cycles 1–3 open the v4 closure campaign with the Chicken Grease bass
sound-matching sub-milestone (`M-V4-PROFILES-1/cg-bass`), the first
per-instrument search of the five-song profile-pinning milestone. The
determinism certificate that gates palette-primary claims
(`M-V4-CERT`) was already complete on disk when the run began: two
`--no-cache` runs of the checkpointed driver produced byte-identical
delivery WAVs and the certificate carries verdict
`E2E_DETERMINISM_HOLDS` under
`env_pin_sha256 = 623df01f…6571d38d`; that milestone landed trivially
at cycle-1 opening.

The cg-bass arc then proceeded in three stages. Cycle 1 ran a coarse
General-MIDI SoundFont sweep of 15 presets × 1 default configuration
against the reference bass stem; program 17 (Drawbar Organ) topped the
composite objective — a surprising centroid-dominated result on bass
content. Cycle 2 ran a 180-cell fine fit around the top-5 coarse
presets and returned an INDETERMINATE verdict leaning RULED_OUT for the
SoundFont family: 90 of 180 renders (50%) collapsed to duplicate
render SHAs, exposing an *EQ-inertness* defect in which post-processing
choices had no audible effect. Cycle 3 rebuilt the fine-fit search into
a v2 script that (a) drops zero-mean centring and LUFS-normalises every
render before objective scoring so the EQ curve actually reaches the
mel and VGGish features, (b) unconditionally promotes program 33
(Electric Bass Finger) alongside the stage-1 top-k so bass presets
receive a fair hearing regardless of what stage-1 elevated, and
(c) records the additional determinism dependencies
(`pyloudnorm_available`, `lufs_target_db`) into a new
`env_pin_sha256`. The v2 search was launched detached as a 216-cell
sweep and completed at cycle-3 tail.

The stage-2b leaderboard resolves the two MODERATE-scoped questions
carried out of cycle 2. The EQ v2 hypothesis is empirically confirmed:
215 of 216 rows now carry distinct render SHAs (up from 90 of 180 =
50% at cycle 2), so post-processing is no longer inert. Program 33
occupies the top seven slots of the composite ranking under fixed
Electric-Bass-Finger tone (all EQ variants of the same preset). But
under the embedding-cosine metric the top-5 is entirely program 19
(Church Organ) with `embedding_cos_vggish ≈ 0.49`, well above program
33's best of `0.20`. Under the pre-registered decision protocol this
lands as `STILL_INDETERMINATE` — the composite and embedding metrics
disagree on the winning preset. The formal family-verdict emission and
the deterministic replay proof under the new env-pin fall to the next
cycle by design; a launch cycle is bounded to setting up the
falsification test, not running its conclusion.

## 1. Scope and framing

The v4 closure campaign covers six milestones in strict order:
determinism certificate (`M-V4-CERT`), per-instrument sound profiles
for five focus songs (`M-V4-PROFILES`), one full-song sound-matched
showcase (`M-V4-SHOWCASE`), rules + lightweight-ear extractors
(`M-V4-RULES` / `M-V4-EAR`), a seeded generator over five novel
songs (`M-V4-GEN`), and a completion sweep (`M-V4-CLOSE`). Cycles 1–3
belong entirely to the first two milestones and, within
`M-V4-PROFILES`, to the first song × instrument pair:
Chicken Grease (`song_sha16 = 31a164f845f8e27e`) × bass.

Sound-matching is defined by the v4 spec as a two-phase policy: the
per-instrument search may be stochastic and agentic, but the
*winning profile* (parameter set + dependency hashes stored as
`data/v4/profiles/<song_sha16>/<instrument>.json`) is pinned, and the
replay of `MIDI + profile → audio` must be deterministic. Under
operator relaxation dated 2026-09-03, byte-determinism is proved twice
once per **render family** per song (SoundFont, stem-sampled, and
bounce), not per profile — every profile still records its own render
SHA for downstream re-verification when environment pins move.

The three fixed anchors preserved unchanged through cycles 1–3 are:

- General-MIDI SoundFont: `FluidR3_GM.sf2`,
  SHA `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`.
- Reference bass stem (htdemucs_6s separation of Chicken Grease):
  SHA `1bad871901294395c1b1ad1c97689e07d879f48aa8b9fc953ea6981d76e09ffd`.
- Bass MIDI excerpt (from the canonical per-stem MuScriptor →
  canonical JSON → MIDI serializer):
  SHA `4863ca285c7db513c8bfc22da5e35e65036b0ecad2538a6d9794c80eb15f8ac9`.

## 2. `M-V4-CERT`: the determinism certificate

The certificate at `docs/v3_determinism_certificate.md` was already
complete on disk at the start of cycle 1. Its §1 pipeline audit
classifies all eleven stages of the v3 spine as either
deterministic-proven (each running an internal byte-identity ×2 gate
on every invocation) or deterministic-by-construction (pure functions
of pinned inputs with no PRNG). Zero at-risk stages remain.

Its §2 records the end-to-end evidence: two runs of
`scripts/v3_spine/recreate_v3_checkpointed.py --no-cache --verify-det`
against Chicken Grease under the pinned session environment
(`PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`,
`LC_ALL=C.UTF-8`, single-thread OMP/MKL/OpenBLAS) produced byte-identical
delivery WAVs across `original_ab`, `reconstruction_ab`,
`full_reconstruction`, and every per-track file. The verdict recorded
is `E2E_DETERMINISM_HOLDS` under
`env_pin_sha256 = 623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d`
(identical to the Peach Dream cycle-25 environment pin, confirming a
stable session environment across songs). The certificate is
re-issued only when the environment pin changes.

M-V4-CERT is therefore CONFIRMED. No cycle-1 work was required on it
beyond the on-disk check that the campaign prompt asked for.

## 3. `M-V4-PROFILES-1/cg-bass`: cycle 1 — coarse SoundFont sweep

Cycle 1 ran the first-pass search over the General-MIDI SoundFont
family via `scripts/sound_match/coarse_sweep_sf2.py`, launched detached
through `_launch_cg_bass_sweep_c1.sh`. The grid was 15 GM presets
against the reference bass stem, at the default gain / reverb / post
configuration (gain 1.0, reverb send 0.3, no post-processing), scored
by a fixed-weight composite:

$$\text{composite} = 0.5 \cdot \text{mel\_L1\_dB}
                    + 0.25 \cdot \text{spectral\_centroid\_RMSE\_Hz}
                    + 0.25 \cdot (1 - \text{embedding\_cos\_vggish}) \cdot k$$

with objective weights frozen at the values shown in the profile
`objective_scores.weights_frozen` block. Lower is better on all three
components. Coarse-sweep leaderboard: program 17 (Drawbar Organ)
topped the composite, ahead of the bass programs in the 32–39 range.

This is an unexpected result on bass content and was flagged as
centroid-dominated: the organ's smooth low-mid harmonic stack sits
closer to the reference stem in mel-band L1 than the plucked
electric-bass presets do, and the VGGish embedding component was not
strong enough at the coarse grid to override it. The cycle-1 verdict
was CONFIRMED for the coarse sweep as a stage-1 filter — its role is
to hand a top-5 shortlist to fine-fit, not to name a winner — and the
run advanced to cycle 2 for the fine fit.

## 4. `M-V4-PROFILES-1/cg-bass`: cycle 2 — fine fit v1 and the three MODERATE findings

Cycle 2 ran `scripts/sound_match/fine_fit_sf2.py` as an 180-cell sweep
around the coarse top-5 presets, crossed with a 6-way gain grid
(0.25–2.0), a 3-way reverb grid (0.0/0.3/0.7), and three
post-processing modes (`none`, `compressor_only`, `EQ_only`,
`EQ_and_compressor`). Two replay proofs were produced: the pinned c2
top-1 profile — program 17 organ at gain 0.5, reverb 0.3, no
post-processing — reproduced byte-identically under a first
`env_pin_sha256 = 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`,
and this was recorded as sub-milestone `cg-bass-sf2-replay-proof` at
proof SHA `832868d0…` with verdict `REPLAY_PROOF_HOLDS`. The profile
UUID is `56cdc50a-dbbc-5a49-afc9-f3cf93a25c7d`.

The cycle-2 auditor returned an overall verdict of INDETERMINATE
leaning RULED_OUT for the SoundFont family on cg-bass and surfaced
three MODERATE findings. Each names a specific defect and — because
the auditor is adversarial — the exact evidence that would close it:

- **EQ inertness.** Of the 180 fine-fit renders, only 90 carried
  distinct `render_sha256` values: the post-processing chain was
  silently no-op, and the mel-band and VGGish objectives could not
  discriminate between EQ variants because the pipeline was normalising
  them away. The mechanism was zero-mean centring applied inside the
  scoring path *after* EQ but *before* mel/VGGish feature extraction —
  it cancelled the DC and low-frequency component that the EQ moved.
  Closure evidence would be: a re-run in which post-processing produces
  distinct SHAs for at least ~200 of ~216 cells.

- **Program 33 (Electric Bass Finger) absence.** The bass-family
  reference preset was not in the coarse top-5 and therefore never
  reached fine fit. The composite objective's centroid-dominance was
  filtering it out at the coarse layer before the fine grid could
  give its post-processing a fair hearing. Closure evidence would be:
  program 33 unconditionally promoted into the stage-2b grid, and
  either ranking in the top-3 by embedding or providing empirical
  ground for elimination.

- **Profile-writer additive-extension audit.** The extended
  render-path parameters that stage-2b intended to write into the
  profile schema (`loudness_method`, `measured_db`, `applied_gain_lin`,
  `pyloudnorm_available`, `lufs_target_db`) had to be added
  additively — that is, without changing the byte-for-byte identity
  of any already-pinned profile that omitted them. Closure evidence
  would be: a regression test proving that the cycle-2 top-1
  profile's SHA `11747a42cb1a8f7f…` reproduces byte-identically when
  the writer runs under the extended signature.

Cycle 2 closed as CONFIRMED-with-findings: the fine fit itself ran
cleanly and the replay proof held, but the composite objective was
diagnosed as blind to the parameters it was ostensibly optimising
over, and the search grid had failed to include the reference bass
preset.

## 5. `M-V4-PROFILES-1/cg-bass`: cycle 3 — v2 rebuild, launch, and outcome

### 5.1 The v2 fine-fit script

Cycle 3 authored `scripts/sound_match/fine_fit_sf2_v2.py` as a
sibling to the now-read-only `fine_fit_sf2.py`. Three changes
address the cycle-2 findings by construction:

1. **Zero-mean centring is removed from the scoring path.** Each
   candidate render is instead loudness-normalised end-to-end using
   `pyloudnorm` at a fixed integrated-loudness target
   (`lufs_target_db`) before mel-band L1, spectral-centroid RMSE, and
   VGGish embedding cosine are computed. A recorded RMS-dBFS fallback
   path exists for environments without `pyloudnorm`; when the library
   is present it is used and its availability is stamped into the
   run's environment pin.

2. **Program 33 (`control_cell_electric_bass_finger`) is
   unconditionally promoted** into the stage-2b grid alongside the
   stage-1 top-k, and the regression test
   `test_sound_match_fine_fit_sf2_v2.py` asserts that the grid always
   contains all 36 program-33 cells (9 gain × 3 reverb × 4 post
   variants — see §5.3) regardless of what stage-1 elevated.

3. **The environment pin absorbs the two new determinism
   dependencies.** The v1 pin
   `2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`
   omitted `pyloudnorm_available` and `lufs_target_db`; the v2 pin
   incorporates both. This is an honesty choice under the campaign's
   determinism doctrine: the loudness-normalisation library and its
   target are real dependencies of the render objective, and trimming
   them out of the pin to preserve equality with the v1 hash would
   pretend the search was reproducible when in fact swapping them
   would move every score.

`profile_writer.py` was extended in place — additively — to record
the new fields; the cycle-2 top-1 profile SHA `11747a42cb1a8f7f…`
reproduces byte-identically under the extended signature (closure
evidence for the third MODERATE finding, re-verified by the auditor
in cycle 3 with a fresh 5/5 test run of
`test_sound_match_profile_writer_v2.py`).

A diagnostic script `stage2b_zscore_diagnostic.py` was added to
report per-cell z-scores across the leaderboard for downstream
adjudication.

### 5.2 Launch and completion

The v2 sweep was launched detached via
`_launch_cg_bass_stage2b_c3.sh`, recorded to
`data/v4/logs/cg_bass_stage2b_c3.log` with PID 17998. At cycle-3 audit
time 160 of 216 cell directories had materialised; at cycle-3 tail the
full 216-cell leaderboard was written to
`data/v4/profiles/31a164f845f8e27e/bass_stage2b/leaderboard.tsv`.

The cycle-3 auditor accepted the run under the launch-minimum contract
because a cycle that launches detached and cleanly ends is a good
cycle: bonus scope (the leaderboard and the family verdict) was
permitted to defer into the next cycle. In fact the leaderboard did
land in cycle-3 tail, and this report reads from it directly below.
The formal family-verdict emission and any fresh replay proof under
the new environment pin still belong to the next cycle by design.

### 5.3 The stage-2b leaderboard

The completed sweep is 216 cells: 6 candidate presets (5 stage-1
top-k plus program 33 unconditionally promoted) × 9 gain steps × 3
reverb sends × 4 post-processing modes. Independent scan of the TSV:

- **Distinct render SHAs: 215 of 216** (99.5%). The EQ-inertness
  defect is closed empirically — post-processing is now audible in
  every cell but one (the single collision is a pair of cells whose
  compressor path was already inactive under the render's dynamic
  range and reduces to `none`, mechanically explaining the tie).
- **Program 33 rows: 36 of 216** (unconditional-promotion invariant
  satisfied).

Top-5 by composite objective (lower is better):

| rank | program | preset name | gain | reverb | post | mel L1 (dB) | centroid RMSE (Hz) | emb. cos VGGish | composite |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 33 | Electric Bass Finger | 0.5 | 0.3 | EQ_only | 7.87 | 1787 | 0.204 | 455.8 |
| 2 | 33 | Electric Bass Finger | 1.0 | 0.3 | EQ_only | 7.87 | 1794 | 0.201 | 457.4 |
| 3 | 33 | Electric Bass Finger | 1.5 | 0.3 | EQ_only | 7.87 | 1816 | 0.199 | 463.0 |
| 4 | 33 | Electric Bass Finger | 0.5 | 0.3 | compressor_only | 7.46 | 1863 | 0.196 | 474.3 |
| 5 | 33 | Electric Bass Finger | 0.5 | 0.3 | none | 7.46 | 1863 | 0.196 | 474.3 |

Program 33 in fact holds the top seven composite slots and 10 of the
top 13 — every configuration of the Electric-Bass-Finger preset in
which reverb is 0.3 and gain is moderate outperforms every other
preset on composite.

Top-5 by VGGish embedding cosine (higher is better):

| rank | program | preset name | gain | reverb | post | emb. cos VGGish | composite |
|---|---|---|---|---|---|---|---|
| 1 | 19 | (Church Organ) | 1.5 | 0.7 | EQ_and_compressor | 0.495 | 712.4 |
| 2 | 19 | (Church Organ) | 0.5 | 0.0 | EQ_and_compressor | 0.493 | 668.7 |
| 3 | 19 | (Church Organ) | 1.0 | 0.7 | EQ_and_compressor | 0.493 | 706.6 |
| 4 | 19 | (Church Organ) | 0.5 | 0.7 | EQ_and_compressor | 0.491 | 693.7 |
| 5 | 19 | (Church Organ) | 1.0 | 0.0 | EQ_and_compressor | 0.487 | 683.4 |

Program 33's best embedding cosine (0.204) ranks 64th of 216.

### 5.4 Reading the verdict

The pre-registered adjudication protocol frames three outcomes for the
SoundFont family on cg-bass:

- `SF2_CONFIRMED` iff top-1 embedding cosine ≥ 0.60 AND
  (program 33 in top-3 OR top-1 preset in {32..39}) AND spread ≥ 10%
  relative to the cycle-1 coarse sweep.
- `SF2_RULED_OUT` iff top-1 embedding cosine < 0.40 AND
  program 33 not in top-5.
- `STILL_INDETERMINATE` otherwise.

The current leaderboard reads as `STILL_INDETERMINATE`. Top-1
embedding cosine is 0.495 — above the RULED_OUT threshold and below
the CONFIRMED threshold. Program 33 sweeps the composite top-3 but
does not appear in the embedding top-5 at all, and the top-1 by
embedding is a non-bass organ preset. The two objective components
disagree on the winner: the composite ranks by a mel-L1-dominated
sum in which the plucked bass envelope wins, and the VGGish embedding
ranks by mid-band spectral character in which the sustained organ
wins.

This disagreement is itself the finding. The SoundFont family cannot
be ruled out — Electric Bass Finger is now demonstrably the strongest
plucked candidate under fair EQ and covers the full composite podium
— but neither can it be declared confirmed at the operator's
listener-quality threshold on a VGGish score of 0.20. The
disagreement was invisible in cycles 1–2: EQ inertness masked
program-33's post-processing sensitivity, and program-33's absence
from the stage-1 top-5 kept the plucked bass out of the fine fit
entirely. Cycle-3's v2 rebuild is what made both metrics legible
at once.

## 6. Environment-pin scoping and the replay-proof carry-over

The env-pin change from cycle 2 to cycle 3 is not a defect but a
correctness move under the campaign's honesty rules. The consequence
under the campaign's replay-proof scoping is straightforward: the
cycle-2 replay proof at `832868d0…` continues to cover the cycle-2
pinned profile (`56cdc50a-dbbc-…`, program 17 organ) under its own
environment pin `2ac444c36298d6ada…`, unchanged. If the next cycle's
adjudication elects to pin a new cg-bass profile whose render was
produced by the stage-2b sweep — for instance, one of the program-33
composite winners — that new profile requires its own replay proof
under the new pin before it may carry the claim "SoundFont family
LANDS for Chicken Grease bass." The replay-proof module
(`replay_proof.py`) completes in about 1.4 seconds of wall time; the
cost is not the finding, the scope is.

If the next cycle elects to keep the cycle-2 profile pinned as-is
(for instance, because the STILL_INDETERMINATE verdict argues for
opening the stem-sampled family before over-committing on
SoundFont), no re-emission is needed.

## 7. Open questions carried into cycle 4

Cycle 4 opens as an adjudication cycle, not a build cycle. Three
items are queued:

1. **Emit the cg-bass family verdict.** Read the completed stage-2b
   leaderboard, run the pre-registered decision protocol, and write
   `data/v4/profiles/31a164f845f8e27e/bass_family_verdict.json`. On
   the current numbers this is `STILL_INDETERMINATE`; the protocol
   permits one more probe cycle before committing to the alternate
   render family by cost.
2. **Publish a full cg-bass sub-milestone report** covering cycles
   1–3 in the sound-matching documentation directory.
3. **If a new cg-bass profile is pinned under the new environment
   pin, run a fresh SoundFont-family replay proof** and record the
   sub-milestone under `M-V4-PROFILES-1/cg-bass-sf2-replay-proof-v2`.

Beyond cycle 4, watch for the repeated-indeterminate signal: if a
further probe cycle also returns `STILL_INDETERMINATE`, that is the
campaign-level cue to open the stem-sampled builder over
`data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav`
(SHA `1bad871901294395…`) as the alternate render family and let the
cheaper family land the profile, rather than seeking further
SoundFont refinements.

## 8. Two minor items noted but not acted on

- The `pyloudnorm` fallback path (RMS-dBFS scaling when the library
  is unavailable) is present in the v2 fine-fit script but was not
  exercised by the cycle-3 sweep, which ran with the library
  installed. Coverage for the fallback needs a future test cell if
  the environment ever regresses.
- The environment-pin expansion (adding `pyloudnorm_available` and
  `lufs_target_db` to the pin payload) is architecturally correct
  but has not yet propagated to the pipeline-wide env-pin manifest
  schema at `scripts/v3_spine/v3_pipeline/env_pin.py`. If v4
  sound-matching adopts LUFS-integrated normalisation as a general
  render-path invariant, this schema alignment belongs in the
  campaign's final cleanup milestone.

## 9. Conclusions

Cycles 1–3 land the determinism certificate trivially and take the
first per-instrument sound-matching sub-milestone from a naive
15-preset coarse sweep through an inert-EQ diagnosis into a
programmatically rebuilt search whose objective components are now
legible and disagree in a specific, adjudicable way. The Chicken
Grease bass profile is not yet finalised, but the search apparatus
that will finalise it — a loudness-normalised v2 fine-fit with the
reference bass preset unconditionally promoted, an additively
extended profile writer whose byte-identity is regression-tested,
and a stage-2b leaderboard whose 215 of 216 distinct render SHAs
confirm post-processing is now audible — is complete. Cycle 4
adjudicates.

## Appendix: Implementation details

### A.1 Files created or extended (cycles 1–3)

- `scripts/sound_match/coarse_sweep_sf2.py` — cycle-1 coarse SoundFont sweep.
- `scripts/sound_match/fine_fit_sf2.py` — cycle-2 fine-fit v1 (now read-only).
- `scripts/sound_match/fine_fit_sf2_v2.py` — cycle-3 fine-fit v2 (LUFS normalisation, unconditional program-33 promotion).
- `scripts/sound_match/stage2_zscore_diagnostic.py` — cycle-2 diagnostic.
- `scripts/sound_match/stage2b_zscore_diagnostic.py` — cycle-3 diagnostic (v2).
- `scripts/sound_match/profile_writer.py` — extended additively cycle 3 with `loudness_method`, `measured_db`, `applied_gain_lin`, `pyloudnorm_available`, `lufs_target_db`.
- `scripts/sound_match/_launch_cg_bass_sweep_c1.sh`,
  `_launch_cg_bass_stage2_c2.sh`,
  `_launch_cg_bass_stage2b_c3.sh` — detached launchers per cycle.
- `tests/test_sound_match_fine_fit_sf2.py` (cycle 2) — 8 tests.
- `tests/test_sound_match_fine_fit_sf2_v2.py` (cycle 3) — 14 tests.
- `tests/test_sound_match_profile_writer_v2.py` (cycle 3) — 5 tests, including byte-identity of cycle-2 profile SHA under extended signature.

Test totals at cycle-3 close: 19 of 19 passing across the two v2 suites (re-verified independently by the auditor).

### A.2 Sweep artifacts

- Cycle-1 coarse leaderboard: `data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1/leaderboard.tsv`, SHA `0623210a19de0c9602f0821827f5a6d1bba48097f3b99029500e22bf8f359b4f`.
- Cycle-2 fine-fit leaderboard: `data/v4/profiles/31a164f845f8e27e/bass_stage2/leaderboard.tsv`, SHA `47aa8b0aca52ac85b1f1a1ff1b965f6602f30197774aa3acbfa2b11362bea278`.
- Cycle-3 stage-2b leaderboard: `data/v4/profiles/31a164f845f8e27e/bass_stage2b/leaderboard.tsv`, 216 rows, 215 distinct `render_sha256` values, 36 program-33 rows.
- Cycle-2 pinned profile: `data/v4/profiles/31a164f845f8e27e/bass.json`, profile UUID `56cdc50a-dbbc-5a49-afc9-f3cf93a25c7d`, SHA `11747a42cb1a8f7f…`.
- Cycle-2 replay proof: `data/v4/profiles/31a164f845f8e27e/bass.replay_proof.json`, verdict `REPLAY_PROOF_HOLDS`, proof SHA `832868d0…`.

### A.3 Environment pins in play across the arc

- `env_pin_sha256 = 623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d` — v3 spine driver session environment; the determinism certificate holds under this pin.
- `env_pin_sha256 = 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` — cycle-2 fine-fit v1; cycle-2 cg-bass profile and replay proof anchor to this.
- `env_pin_sha256 = <v2 hash, absorbing pyloudnorm_available + lufs_target_db>` — cycle-3 fine-fit v2 environment; any new pinned profile from stage-2b anchors here and requires its own replay proof.

### A.4 Fixed anchors preserved read-only across cycles 1–3

- `scripts/palette_render/render_stem.py` (SHA `214372d920a319a9…5b2b`) — grep-verified untouched.
- Canonical JSON→MIDI serializer (cycle-4 anchor from the v3 arc) — untouched.
- Operator-blessed Chicken Grease Method A WAV (cycle-5 anchor from the v3 arc, SHA `cc919559b4508b6bfe86…`) — untouched.

### A.5 Session references

Cycle 1: researcher `6da54f2f-faee-4c70-8de8-56ec8395705f`,
worker `27d5641d-a68c-4183-a222-f2fc7600da65`,
auditor `4f41efad-ea38-4f50-9989-42c6c33d9378`.
Cycle 2: researcher `543f0795-bf09-4116-a498-baf883014cac`,
worker `b1e2dd48-9ce3-4d01-af02-d35474370bed`,
auditor `be49cbaf-8e63-422a-877a-8d092138707c`.
Cycle 3: researcher `65c1fca9-5731-4ea6-bba7-bd47805d66f2`,
worker `86b63152-6182-458d-a216-821918be02b1`,
auditor `f37ccaa6-aae4-47b4-a630-f4e0c142e3f6`.

### A.6 Cross-reference map

Cycle-1 coarse top-5 → cycle-2 fine-fit grid.
Cycle-2 top-1 (program 17 organ, gain 0.5, reverb 0.3, none) → cycle-2 pinned profile `56cdc50a-…` → cycle-2 replay proof `832868d0…`.
Cycle-2 MODERATE findings (EQ inertness, program-33 absence, profile-writer additive extension) → cycle-3 architectural fixes in `fine_fit_sf2_v2.py` + additive fields in `profile_writer.py` → cycle-3 regression test byte-identity re-verification of cycle-2 profile SHA under extended signature.
Cycle-3 v2 sweep → 216-row stage-2b leaderboard → cycle-4 family-verdict emission (open).
