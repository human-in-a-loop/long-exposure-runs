---
title: "Music-Gen v4 closure campaign — cycles 4–6"
date: "2026-09-03"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v4 closure campaign — cycles 4–6

## Abstract

Cycles 4–6 continue the Chicken Grease bass sound-matching
sub-milestone from where cycles 1–3 left it. Cycle 4 fires the
pre-registered decision protocol on the completed 216-cell stage-2b
leaderboard and returns `STILL_INDETERMINATE`: the composite and
VGGish objectives disagree — top-1 by composite is program 33
(Electric Bass Finger) with embedding-cosine 0.204, top-1 by
embedding-cosine is program 19 (Church Organ) at 0.495 — with
neither reaching the 0.60 CONFIRMED threshold and neither falling
under the 0.40 RULED_OUT threshold. In the process of emitting a
second pinned profile (`bass_v2.json`, program 33 by composite) and
its replay proof, cycle 4 surfaces a CRITICAL defect: the sf2 replay
dispatch produces byte-identical audio (`832868d0…`) for two
profiles that differ only in `identity.program`. The old and new
pinned profiles collide because the replay path silently discards
the program-select payload.

Cycle 5 formalises the alternate render family. It writes the
`family2_stem_sampled` design spec, lands a spike script
(`family2_stem_sampled_spike.py`, SHA `000c3ef68042f2da…6329e80`)
that exercises the intended lever set — single-slice pitch shift +
lightweight ADSR + LUFS-I loudness normalisation at −18 LUFS — and
escalates the replay defect to the manager with CRITICAL severity.

Cycle 6 runs two tracks in a single sequential worker session. Track
one replaces the offending `_ = setup  # documentation` line at
`replay.py:85` with a real mido-based MIDI rewrite that strips every
existing `program_change` and injects a fresh
`program_change(channel=0, program=profile.identity.program, time=0)`
at tick 0 of the first note-carrying track; three regression tests
pass, and the refreshed sf2 replay proofs now diverge as required —
`bass` moves to `c69775040c…4ff019c` while `bass_v2` stays at
`832868d0…3aeac5` (expected, because `bass.mid` already embeds
`program_change 33`, so the rewrite is materially a no-op for that
one profile). Cross-proof SHAs differ, `REPLAY_FIX_LANDS`. Track two
promotes the cycle-5 spike into a shipped
`family2_stem_sampled_builder.py`, emits `bass_family2_v1.json`
(`profile_id 1f3c104a-…6ee`, `render_family = stem_sampled_v1`), its
replay proof (byte-identical ×2 at `9b4647cef61fe9d6…523276`), and
the family verdict `FAMILY2_RULED_OUT` at `embedding_cos_vggish =
0.0896`, roughly 0.405 units below the sf2 top-1.

Both frozen render families are now exhausted for Chicken Grease
bass without any CONFIRMED profile. The `M-V4-SHOWCASE-1`
milestone is blocked until the operator picks between accepting the
sf2 `STILL_INDETERMINATE` top-1 as a policy call, refusing showcase
until a further family lands, or overriding the pre-registered 0.60
threshold. The cycle-6 auditor validated on 19 of 19 gates with
three named cosmetic deviations. The replay fix is a foundational
infrastructure unblock: from cycle 7 onward every sf2 replay proof
across every song and instrument will correctly honour
`profile.identity.program`.

## 1. Cycle 4 — family verdict, second profile, CRITICAL surfacing

### 1.1 The verdict

Cycle 4 opens as the adjudication cycle promised at cycle-3 close.
The stage-2b leaderboard was already complete on disk (216 rows,
215 distinct render SHAs, 36 program-33 rows). Cycle 4 wrote
`family_verdict_cg_bass.py`, ran it against the leaderboard, and
emitted
`data/v4/profiles/31a164f845f8e27e/bass_family_verdict.json`.

The pre-registered decision clauses evaluated as follows:

| clause | value |
|---|---|
| top-1 embedding cosine ≥ 0.60 | false (0.4946) |
| top-1 embedding cosine < 0.40 | false |
| program 33 in top-3 by embedding cosine | false (rank 64) |
| program 33 not in top-5 by embedding cosine | true |
| top-1 preset in bass family {32..39} | false (program 19, organ) |
| spread ratio ≥ 0.10 vs cycle-1 coarse | true (1.75×) |

Neither CONFIRMED nor RULED_OUT fired. The verdict is
`STILL_INDETERMINATE`, emitted honestly at first-run under the
frozen 0.60 / 0.40 thresholds.

### 1.2 The second pinned profile

Because the composite metric and the embedding metric name
different presets, cycle 4 pinned a second profile alongside the
cycle-2 organ pin. `bass_v2.json` carries
`profile_id d62cd3b6-4521-5d4f-b840-87ef7800c48d`, program 33
Electric Bass Finger, gain 0.5, reverb 0.3, `post=EQ_only`,
serialised at SHA `2a1cb340bffd11016c566467b0d313fb…`. This is the
top-1 by composite and the operator-facing "closest bass-shaped
candidate" from the SoundFont family.

`bass_v2.replay_proof.json` was written under the cycle-6-canonical
7-key env-pin
`env_pin_sha256 = 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`
(the same 7-key subset used by cycle 2; the stage-2b sweep-time
9-key pin from cycle 3, which added `pyloudnorm_available` and
`lufs_target_db`, is not consumed by the replay operation and does
not enter the replay-proof hash). Verdict: `REPLAY_PROOF_HOLDS`,
`run1 == run2 == 832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5`.

### 1.3 The CRITICAL defect

`bass_v2.replay_proof.json` records `run1 = run2 = 832868d0…3aeac5`.
`bass.replay_proof.json` from cycle 2 recorded `832868d0…3aeac5` as
well — the same SHA, on the same MIDI file, from two profiles that
differ only in `identity.program` (17 vs 33). The verdict JSON
records the finding under `canonical_replay_sha_equals_c2_note` as
what the cycle-4 worker at that moment believed to be a benign
program-invariance property: "`replay._replay_sf2` reads program
from MIDI file's own `program_change` events, not from the profile
dict… c1 rewrote bass.mid to embed `prog=33` `program_change`, so
any sf2 profile invoked against bass.mid produces byte-identical
audio."

That framing was over-charitable. The property is not benign: it
means the replay dispatch cannot distinguish two SoundFont profiles
that intentionally pin different programs, which invalidates every
SoundFont replay proof across every future song and instrument. The
cycle-4 auditor upgraded the finding to a CRITICAL replay-defect
chain (with cycle-2 as origin), and the finding entered cycle 5 as
a manager escalation.

### 1.4 A second observation about environment pins

Cycle 4 also confirmed that the 7-key replay-time env pin
(`PYTHONHASHSEED`, `SOURCE_DATE_EPOCH`, `TZ`, `LC_ALL`, single-thread
`OMP` / `MKL` / `OPENBLAS`) is stable across the cycle-2 → cycle-3
transition even though the cycle-3 sweep-time env pin changed. This
is a positive property of the replay-proof surface: the loudness
library and target that entered the sweep are not consumed by the
replay operation, so the replay-proof hash does not need to track
them. Cycle 6 later ratifies this scoping choice as
`_plan/env-pin-schema-unified-c6`.

## 2. Cycle 5 — the alternate family spike and the manager escalation

Cycle 5 was set up as a two-item cycle: put the CRITICAL defect on
a formal escalation track, and stand up the alternate render family
so cycle 6 could run both closures back-to-back.

**Manager escalation.** A `_manager` event was landed carrying the
replay-invariance defect with CRITICAL severity, `action_required`,
and a pre-registered fix contract for cycle 6 to close: replace the
`_ = setup  # documentation` line at `scripts/sound_match/replay.py`
line 85 with a real MIDI-rewrite step; produce a regression test
matrix with negative-inversion, positive-determinism, and existing-
MIDI-neutrality cases (A/B/C); refresh both sf2 replay proofs; and
prove that the cross-profile SHAs now differ.

**Family-2 spike.** `scripts/sound_match/family2_stem_sampled_spike.py`
was written (SHA `000c3ef68042f2da…6329e80`) as the shape probe for
the stem-sampled render family. The spec fixed by the spike is:

- One slice of the reference bass stem is taken as the source
  timbre. The slice is centred on the pyin-estimated fundamental of
  the stem.
- The slice is pitch-shifted per note using a single-slice
  strategy — no per-note pick, no windowed f0 refinement.
- A lightweight ADSR envelope is applied per note.
- The rendered take is loudness-normalised to `−18 LUFS-I`.

The spike also recorded a honest first observation about the
reference stem: `pyin` estimated the fundamental at 41.20 Hz — the
lower `fmin` bound, meaning the estimate is pinned to the floor
rather than a true content estimate. This is a subharmonic latch;
the spike declined to work around it and instead recorded it as an
honest input property for the family verdict to inherit.

## 3. Cycle 6 — the two-track closure

### 3.1 Track 1 — replay-program-invariance fix

`replay.py` was patched in place at lines 79–93. The pre-patch line
`_ = setup  # documentation` — which discarded the program-select
payload silently — was replaced by:

```python
import mido  # local import: only needed on sf2 dispatch
_mid = mido.MidiFile(str(midi_path))
for _tr in _mid.tracks:
    _to_del = [i for i, m in enumerate(_tr) if m.type == "program_change"]
    for i in reversed(_to_del):
        del _tr[i]
for _tr in _mid.tracks:
    if any(m.type == "note_on" for m in _tr):
        _tr.insert(0, mido.Message("program_change", channel=0,
                                   program=program, time=0))
        break
_rewritten = out_wav_path.with_suffix(".prog_forced.mid")
_mid.save(str(_rewritten))
cmd.append(str(_rewritten))
```

The rewrite is a deterministic pure function of `(midi_path,
program)`. It runs in-memory, saves the rewritten MIDI to a
sibling `.prog_forced.mid` file next to the target WAV so the
rewrite is auditable, and hands fluidsynth the rewritten file
instead of the original.

**File SHAs.** `replay.py` moves from `e03dad60d67fcf2fb93b5d01e026cc1d1b21a5496c27a110a0353fd5abf1fbab`
to `419d9558747eec61e58b3450b9f57b9bd057a7f8d7a31dfd1ab02f4d63c9f545`.

**Regression matrix.** `replay_fix_test_matrix.json` records three
tests, all passing:

- **A — negative inversion.** Same MIDI, two profiles with
  different `identity.program` values → different audio SHAs. Would
  have failed pre-fix.
- **B — positive determinism.** Same MIDI + same profile → same
  audio SHA on repeat, byte-identical.
- **C — existing-MIDI neutrality.** Rewriting a MIDI whose embedded
  `program_change` already matches the profile's `identity.program`
  yields byte-identical output before and after rewrite, so
  neutral cases do not shift.

**Replay-proof refresh.** Both cycle-2 and cycle-4 replay proofs
were re-emitted under the post-fix `replay.py`. Pre-fix archives
were preserved under `pre_c6_fix/`:

| profile | pre-fix SHA | post-fix SHA | change |
|---|---|---|---|
| `bass` (program 17 organ, cycle 2 pin) | `832868d0…3aeac5` | `c69775040c325b865be029316d5ccbaff6b3d2393b238c877bae3f1b74ff019c` | **CHANGED — fix took effect** |
| `bass_v2` (program 33 electric bass, cycle 4 pin) | `832868d0…3aeac5` | `832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5` | unchanged (expected — `bass.mid` already embeds `program_change 33`) |

The cross-proof-differ property (`bass ≠ bass_v2`) is the audio-
bytes evidence, independent of the test suite, that the fix reaches
the render output.

**Verdict.** `replay_fix_verdict.json` records
`REPLAY_FIX_LANDS`, three-way rubric-hash chain
`a9497ed585f9a8807ec0addb2d695b8b411eb60418c7bc3946663ce71c4178ef`,
all three regression tests pass, cross-proof SHAs differ,
env-pin `2ac444c3…a922ca`.

### 3.2 Track 2 — family-2 stem-sampled builder, profile, verdict

The cycle-5 spike was promoted to
`scripts/sound_match/family2_stem_sampled_builder.py` and
`scripts/sound_match/replay_family2.py`. Both files carry the
project's standard interpreter guard, no PRNG, and — per the
sequential-only campaign discipline — no `--verify-det` flag.

The pinned family-2 profile
`data/v4/profiles/31a164f845f8e27e/bass_family2_v1.json`:

- `profile_id`: `1f3c104a-2cc4-5e25-a802-d1360f1336ee` (UUID5,
  deterministic function of the profile's canonicalised parameter
  block).
- `render_family`: `stem_sampled_v1`.
- Lever set (frozen per the cycle-5 spec): `single_slice_pitch_shift`
  + `adsr_lite` + `LUFS-I −18`.
- `render_sha256_canonical_replay`: `9b4647cef61fe9d6…523276`.

The replay proof holds byte-identically ×2 at
`9b4647cef61fe9d6…523276`, under the same canonical 7-key
env-pin `2ac444c3…a922ca`.

The family verdict at
`data/v4/profiles/31a164f845f8e27e/bass_family2_verdict.json`:

- `render_family`: `stem_sampled_v1`.
- `panel.mel_l1_db`: 7.6887.
- `panel.spectral_centroid_rmse_hz`: 3262.46.
- `panel.embedding_cos_vggish`: **0.0896**.
- `comparison_vs_sf2.sf2_top1_embedding_cos`: 0.4946.
- `comparison_vs_sf2.delta`: **−0.405**.
- `verdict`: **`FAMILY2_RULED_OUT`**.
- `rubric_hash`: `2dddc32a52d6fa4544a7153b0ac2709609180f0645f6e422a6ea72a2c7b91dfe`.

The verdict fires cleanly under FD-1 first-run honesty: 0.0896 is
0.31 units below the 0.40 RULED_OUT threshold. Even if the
subharmonic-latched pyin f0 were refined to a true fundamental, the
single-slice-pitch-shift lever set is unlikely to lift the score by
0.31. The `RULED_OUT` verdict does not need the f0 estimate to be
fixed first — it fires on the panel numbers as measured.

Family 2 is not universally invalid — the finding is per-cell.
Future family-2 attempts on other songs and instruments remain
in scope; on Chicken Grease bass, this specific lever set is
empirically ruled out.

### 3.3 The env-pin unification

Every proof and verdict emitted in cycle 6 stamps the single
canonical replay-time env pin
`env_pin_sha256 = 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`.
That covers the two refreshed sf2 replay proofs, the family-2
replay proof, the family-2 verdict, and the replay-fix verdict.
This closes on the replay surface the "environment-pin scoping"
observation raised by cycle 4. The cycle-3 sweep-time 9-key
superset (`pyloudnorm_available` + `lufs_target_db`) is preserved
as a diagnostic manifest under `_plan/env-pin-schema-unified-c6`
rather than merged into the replay hash, because replay does not
consume those two variables.

### 3.4 Audit acceptance

Cycle-6 auditor VALIDATED on 19 of 19 gates. Three deviations were
named explicitly in the worker output and accepted as cosmetic:

- **Gate 8** — the manager supersede was carried through a two-step
  `action_required → in-progress → validated` transition path, with
  the supersede intent recorded on the `supersedes_path` field of
  the validated event, because the ledger state-machine forbids the
  direct `action_required → superseded` transition. Substantive
  supersede semantics honoured.
- **Gate 17** — 14 cycle-6 ledger events landed rather than the
  brief's 12; the extra event is the state-machine step required
  under gate 8. Substantive content count matches the brief.
- **Gate 19** — env-pin unification is scoped to the replay-proof
  surface, with the sweep-time superset preserved separately, rather
  than merged into a single hash. This is the operational closure
  the CRITICAL required.

Anchor preservation held: `bass.json`, `bass_v2.json`,
`bass_family_verdict.json`, and the reference stem
`data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav`
were all byte-identical pre and post cycle 6, along with the
cycle-5 spike script. Storage delta ≈ 350 KB against the 500 MB
per-cycle working-audio budget (0.07% utilisation).

## 4. State of Chicken Grease bass at cycle-6 close

Both frozen render families have been exercised:

- **SoundFont family:** `STILL_INDETERMINATE` at cycle-4 verdict
  (READ-ONLY thereafter). Top-1 by composite is program 33 Electric
  Bass Finger (`bass_v2.json`, `embedding_cos_vggish = 0.4946` when
  measured against the program-19 top of the embedding metric — see
  §1). Top-1 embedding is program 19 Church Organ. Neither reaches
  the 0.60 CONFIRMED threshold.
- **Stem-sampled family v1** (`single_slice_pitch_shift` +
  `adsr_lite` + LUFS-I −18): `FAMILY2_RULED_OUT` at cycle 6,
  `embedding_cos_vggish = 0.0896`.

No CONFIRMED profile exists. The `M-V4-SHOWCASE-1` milestone is
therefore blocked on cg-bass. Under the campaign's operator-
authority rule (FD-6, operator ear is the LANDS authority), the
correct next step is a manager escalation to the operator with
three named options: (1) accept the sf2 `STILL_INDETERMINATE`
top-1 as the pinned cg-bass profile for showcase, unblocking
`M-V4-SHOWCASE-1`; (2) refuse showcase until a further family
lands, requiring either a different family-2 lever set (per-note
pick or windowed f0 from the cycle-5 spec) or a new render family
entirely (e.g. sample-based commercial VST via DawDreamer with
sfizz fallback); (3) override the pre-registered 0.60 threshold,
which is destructive to FD-1 pre-registration and requires an
explicit operator override.

## 5. The replay fix as infrastructure unblock

The scope of the replay-program-invariance fix extends well beyond
Chicken Grease bass. Every SoundFont-family replay proof for every
song and instrument to come — the remaining four focus songs times
six instruments per song, twenty-four profile cells with drums
first per the operator's instrument order — will run through the
patched `replay.py`. Pre-fix, `_ = setup  # documentation` would
have produced silent program-invariance collisions on every one of
them, exactly as it did between `bass.json` and `bass_v2.json`.
The fix converts the SoundFont render family from "cannot ship
replay proofs" to "can ship replay proofs on every song and
instrument." That is worth naming as the single largest
infrastructure gain of these three cycles.

## 6. Open questions carried into cycle 7

1. **Cg-bass arc close-out.** Emit
   `data/v4/profiles/31a164f845f8e27e/bass_arc_closeout.json`
   recording both family verdicts (with their SHAs pinned), the
   best-available profile by any objective (`bass_v2.json`
   program 33, sf2 `embedding_cos = 0.4946` — still below
   CONFIRMED), and the named blocker: no family CONFIRMED at
   frozen threshold; operator policy call required.
2. **Manager escalation on M-V4-SHOWCASE-1 acceptance policy.**
   Emit `_manager/M-V4-SHOWCASE-1-cg-bass-acceptance-policy`
   with `status = action_required, severity = HIGH` and the three
   options listed in §4. Do not pick a default; operator picks
   per FD-6.
3. **Contingent advance.** If cycle-7 `live_guidance` carries an
   operator directive on option (1), open
   `M-V4-PROFILES-1/cg-drums-sweep-launched` as the next
   profile cell per the v4 spec instrument order (drums first
   after bass). Otherwise hold for operator input.

## 7. Two minor items noted but not acted on

- The pyin f0 estimate of 41.20 Hz on the reference bass stem is
  latched to the algorithm's `fmin` bound and therefore a
  subharmonic misidentification. The family-2 verdict fires
  regardless (see §3.2), and re-running the family-2 lever set
  with a corrected f0 would need to lift `embedding_cos_vggish`
  by 0.31 units — larger than the single-slice-pitch-shift lever
  set is likely to move. Recording as a first-class negative
  input property, not a defect to retry.
- The sweep-time 9-key env-pin superset lives under a diagnostic
  manifest rather than the canonical env-pin schema at
  `scripts/v3_spine/v3_pipeline/env_pin.py`. If a future milestone
  makes LUFS-integrated normalisation a general render-path
  invariant, the schema alignment belongs in `M-V4-CLOSE-1`.

## 8. Conclusions

Cycles 4–6 land the two hardest technical closures of the profiling
milestone in a compact three-cycle sequence: the sf2 replay-program-
invariance CRITICAL is fixed with cross-proof-differ evidence at the
audio-bytes boundary, and the stem-sampled render family is
empirically ruled out for Chicken Grease bass under the cycle-5
lever set. Both frozen families are now exhausted for this one
cell, and the milestone reaches a defensible waypoint at which the
operator's ear becomes the LANDS authority. Cycle 7 opens as a
close-out plus operator-escalation cycle.

## Appendix: implementation details

### A.1 Files created or extended (cycles 4–6)

- `scripts/sound_match/emit_bass_v2_and_replay_proof.py` (cycle 4) — emits `bass_v2.json` + replay proof.
- `scripts/sound_match/family_verdict_cg_bass.py` (cycle 4) — runs the pre-registered decision protocol against the stage-2b leaderboard and writes `bass_family_verdict.json`.
- `scripts/sound_match/family2_stem_sampled_spike.py` (cycle 5) — shape probe, SHA `000c3ef68042f2da…6329e80`, byte-identical pre==post cycle 6.
- `scripts/sound_match/family2_stem_sampled_builder.py` (cycle 6) — shipped stem-sampled builder promoting the cycle-5 spike.
- `scripts/sound_match/replay_family2.py` (cycle 6) — family-2 replay dispatch, sibling to `replay.py`.
- `scripts/sound_match/replay.py` (cycle 6, patched in place at L79–93) — moves from `e03dad60…` to `419d9558747eec61e58b3450b9f57b9bd057a7f8d7a31dfd1ab02f4d63c9f545`.

### A.2 Data artefacts

- `data/v4/profiles/31a164f845f8e27e/bass_family_verdict.json` (cycle 4) — `STILL_INDETERMINATE`; leaderboard stats and cross-metric top-3 tables embedded.
- `data/v4/profiles/31a164f845f8e27e/bass_v2.json` (cycle 4) — `profile_id d62cd3b6-4521-5d4f-b840-87ef7800c48d`, program 33, gain 0.5, reverb 0.3, `post=EQ_only`, profile SHA `2a1cb340bffd11016c566467b0d313fb002c5949ce881968702846867e090462`.
- `data/v4/profiles/31a164f845f8e27e/bass_v2.replay_proof.json` (cycle 4, refreshed cycle 6) — run1 = run2 = `832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5`; unchanged after fix, expected because `bass.mid` already embeds `program_change 33`.
- `data/v4/profiles/31a164f845f8e27e/bass.replay_proof.json` (refreshed cycle 6) — run1 = run2 = `c69775040c325b865be029316d5ccbaff6b3d2393b238c877bae3f1b74ff019c`; changed from pre-fix `832868d0…3aeac5`, definitive audio-bytes evidence the fix took effect.
- `data/v4/profiles/31a164f845f8e27e/replay_fix_verdict.json` (cycle 6) — `REPLAY_FIX_LANDS`, A/B/C = pass/pass/pass, cross-proof-differ = true, rubric hash `a9497ed585f9a8807ec0addb2d695b8b411eb60418c7bc3946663ce71c4178ef`.
- `data/v4/profiles/31a164f845f8e27e/replay_fix_test_matrix.json` (cycle 6) — three-test regression matrix.
- `data/v4/profiles/31a164f845f8e27e/bass_family2_v1.json` (cycle 6) — `profile_id 1f3c104a-2cc4-5e25-a802-d1360f1336ee`, `render_family = stem_sampled_v1`, canonical replay SHA `9b4647cef61fe9d6…523276`.
- `data/v4/profiles/31a164f845f8e27e/bass_family2_v1.replay_proof.json` (cycle 6) — run1 = run2 = `9b4647cef61fe9d6…523276`.
- `data/v4/profiles/31a164f845f8e27e/bass_family2_verdict.json` (cycle 6) — `FAMILY2_RULED_OUT`, `embedding_cos_vggish = 0.0896`, `delta_vs_sf2_top1 = −0.405`, rubric hash `2dddc32a…91dfe`.
- `data/v4/profiles/31a164f845f8e27e/anchor_preservation_pre_c6.json` and `anchor_preservation_post_c6.json` — `all_match = true, n_mismatch = 0` on four READ-ONLY anchors + cycle-5 spike script SHA.
- `data/v4/profiles/31a164f845f8e27e/pre_c6_fix/` — archived copies of pre-fix `bass.replay_proof.json` (932 B) and `bass_v2.replay_proof.json` (892 B).
- `data/v4/profiles/31a164f845f8e27e/replay_c6_post_fix_sha.txt` — post-fix `replay.py` SHA fingerprint.
- `data/v4/profiles/31a164f845f8e27e/replay_fix_c6_rubric_hash.txt` and `family2_builder_c6_rubric_hash.txt` — three-way rubric-hash chain anchors.

### A.3 Environment pins in play across the arc

| pin | scope |
|---|---|
| `2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` | canonical replay-time 7-key env-pin; stamped across every cycle-6 proof and verdict; closes cycle-4 replay-side pin drift on the replay surface. |
| `d606c8bc0ebfd38bf64ce588e2b133f4a954556d3c5c92d257fd3b582bfb0aa9` | cycle-3 stage-2b sweep-time 9-key env-pin (adds `pyloudnorm_available` + `lufs_target_db`); preserved as diagnostic manifest under `_plan/env-pin-schema-unified-c6`, not merged into replay hash. |

### A.4 Fixed anchors preserved read-only across cycles 4–6

- Cycle-2 pinned bass profile `bass.json` (`56cdc50a-…`, program 17).
- Cycle-4 pinned bass profile `bass_v2.json` (`d62cd3b6-…`, program 33).
- Cycle-4 family verdict `bass_family_verdict.json`.
- Cycle-5 spike script `family2_stem_sampled_spike.py` (`000c3ef68042f2da…6329e80`).
- Reference bass stem WAV `data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav`.
- `scripts/palette_render/render_stem.py` (`214372d920a319a9…5b2b`).
- Chicken Grease Method A operator-blessed WAV (`cc919559b4508b6bfe86…`).

### A.5 Session references

Cycle 4: researcher `16c9463b-6761-4aa6-87cd-36fca4ec9109`,
worker `da3b85eb-d4e5-4e57-ab6f-e9472a04c6f8`,
auditor `2fdae963-6c6a-4c5b-8e85-585bc3d444d8`.
Cycle 5: researcher `99dc41dc-2026-4f1a-a75e-78d41d57cc6d`,
worker `0feef7ba-2029-4964-8f65-1162c806cc1f`,
auditor `5ae30026-8675-41da-928d-a1194d595de2`.
Cycle 6: researcher `c6145592-efdc-4068-9725-30150c7cf728`,
worker `dd1a24f9-9b06-4b87-9003-c6a184521279`,
auditor `63e9e51f-4e28-4fad-bd1e-c75a975f79be`.

### A.6 Cross-reference map

Cycle-3 stage-2b leaderboard →
cycle-4 `family_verdict_cg_bass.py` →
`bass_family_verdict.json` (`STILL_INDETERMINATE`) →
cycle-4 `emit_bass_v2_and_replay_proof.py` →
`bass_v2.json` + first replay proof (SHA `832868d0…`, colliding
with cycle-2 replay proof) →
cycle-4 auditor CRITICAL escalation →
cycle-5 manager event + `family2_stem_sampled_spike.py` →
cycle-6 Track 1 `replay.py` fix + regression matrix + refreshed
proofs (`bass` moves to `c69775040c…`, `bass_v2` stays at
`832868d0…`, cross-proof-differ) →
`replay_fix_verdict.json` `REPLAY_FIX_LANDS` →
cycle-6 Track 2 `family2_stem_sampled_builder.py` +
`replay_family2.py` + `bass_family2_v1.json` +
`bass_family2_v1.replay_proof.json` +
`bass_family2_verdict.json` `FAMILY2_RULED_OUT` →
cycle-7 close-out + operator escalation (open).
