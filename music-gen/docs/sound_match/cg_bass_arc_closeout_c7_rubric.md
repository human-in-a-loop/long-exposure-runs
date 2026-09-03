<!-- created: 2026-09-03T22:00:00Z cycle: 7 run_id: run-2026-09-03T220000Z agent: worker milestone: M-V4-PROFILES-1 -->

# Chicken Grease Bass Profiling Arc — c7 Close-Out Rubric

## 1. Statement

The Chicken Grease (song sha16 `31a164f845f8e27e`) bass profiling arc has
evaluated two RENDER FAMILIES (per FD-16(c)) against the frozen
`embedding_cos_vggish` thresholds 0.60 (CONFIRMED) and 0.40 (RULED_OUT):

| Render family              | Cycle | Verdict                | Top-1 embedding_cos_vggish |
|----------------------------|-------|------------------------|----------------------------|
| sf2 (FluidR3_GM)           | c4    | STILL_INDETERMINATE    | 0.4946                     |
| stem_sampled_v1 (family-2) | c6    | FAMILY2_RULED_OUT      | 0.0896                     |

Neither family crossed the 0.60 CONFIRMED bar under the c5-spec lever set.
This is a first-class negative finding on the CG bass arc under FD-1 (no
tuning, no retry, no fallback).

## 2. Close-out verdict enum (informational)

The close-out verdict is bookkeeping — it is NOT a hidden LANDS gate for
M-V4-SHOWCASE-1 (operator ear is the only LANDS authority per FD-6).

- **CG_BASS_ARC_EXHAUSTED_NO_CONFIRMED** — both families verdicted
  honestly under the c5-spec lever sets; no CONFIRMED at the frozen
  0.60/0.40 thresholds; operator-policy call required to unblock
  M-V4-SHOWCASE-1. This is the c7 verdict absent an operator directive
  in c7 live_guidance.
- **CG_BASS_ARC_STILL_ACTIVE** — fires only if c7 Track 3 arms with an
  operator directive that reopens a family with a different lever set,
  a new render family, or a threshold override.

## 3. Three-way rubric_hash chain

The SHA-256 of this document is pinned to
`data/v4/profiles/31a164f845f8e27e/closeout_c7_rubric_hash.txt` BEFORE
any script or verdict file this cycle. Downstream:

```
sha256(docs/sound_match/cg_bass_arc_closeout_c7_rubric.md)
  == data/v4/profiles/31a164f845f8e27e/closeout_c7_rubric_hash.txt content
  == data/v4/profiles/31a164f845f8e27e/bass_arc_closeout.json.rubric_hash
```

Mtime gate hard; git-log gate advisory per c46 path (ii) amendment.

## 4. READ-ONLY anchors

These five anchors are preserved byte-identical pre==post c7 by
`anchor_preservation_pre_c7.json` and `anchor_preservation_post_c7.json`:

| Anchor                                                             | SHA-256                                                            |
|--------------------------------------------------------------------|--------------------------------------------------------------------|
| `data/v4/profiles/31a164f845f8e27e/bass.json`                      | `11747a42cb1a8f7f693f27c36f0c5e0fc60d0d44da13c877f984443487a8f1c9` |
| `data/v4/profiles/31a164f845f8e27e/bass_v2.json`                   | `2a1cb340bffd11016c566467b0d313fb002c5949ce881968702846867e090462` |
| `data/v4/profiles/31a164f845f8e27e/bass_family_verdict.json`       | `cbbdbebf00c30e2c2b0b7c6a575fa59c723a7d1294905eec12bbb2166c546228` |
| `data/v4/profiles/31a164f845f8e27e/bass_family2_verdict.json`      | `1c6967aa3dc2d092f9f5ea8bd1942ff2b142f9c6534ad61897c9bf49f1171a80` |
| `data/v4/profiles/31a164f845f8e27e/bass_family2_v1.json`           | `503284c5e3adb3fb1f1eaefde293f55dc465376d04a1203112ccf760ecc85561` |

Auxiliary anchors also preserved: `stems_6s/bass.wav`
(`1bad871901294395…6e09ffd`), c6-post-fix `scripts/sound_match/replay.py`
(`419d9558747eec61…c9f545`), c5 spike script
(`000c3ef68042f2da…6329e80`), c6 family-2 builder
(`eaa8fb6cb513f342…f8234`).

## 5. Downstream

This close-out does NOT invalidate the profile artifacts on disk.
`bass_v2.json` (sf2, program 33 Electric Bass Finger, top-1 by composite
objective on c3 stage-2b leaderboard; embedding_cos_vggish for prog 33 =
0.20353; STILL_INDETERMINATE against the 0.60/0.40 gate) remains the
strongest available CG bass profile candidate should the operator accept
it via Option 1 of the manager escalation.

`bass.json` (sf2, program 17 Drawbar Organ, c2 top-1 by composite;
STILL_INDETERMINATE) remains as the c2 legacy artifact.

`bass_family2_v1.json` (stem_sampled_v1; RULED_OUT) remains on disk as
provenance for the family-2 attempt.

Operator policy call on M-V4-SHOWCASE-1 acceptance is escalated in a
separate manager event (`_manager/M-V4-SHOWCASE-1-cg-bass-acceptance-policy`)
with three named options presented neutrally per FD-6.
