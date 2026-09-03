---
created: 2026-09-03T00:00:00Z
cycle: 5
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-V4-PROFILES-1/cg-bass-family2-stem-sampled
---

# CG bass family-2 (stem-sampled) — c5 cycle report

## Opening

**c5 is a spec + spike cycle, not a fit or a proof.** No family-2 profile is pinned
this cycle, no family-2 `replay_proof.json` is emitted, no sweep is run. The c4 sf2
verdict `STILL_INDETERMINATE` (`data/v4/profiles/31a164f845f8e27e/bass_family_verdict.json`,
sha `cbbdbebf00c30e2c2b0b7c6a575fa59c723a7d1294905eec12bbb2166c546228`) is a
READ-ONLY anchor and is not re-analyzed here. sf2 refinement is separately blocked
on the CRITICAL manager event
`_manager/M-V4-PROFILES-1-replay-program-invariance-critical` and does not resume
until `scripts/sound_match/replay.py` is fixed with the regression contract named in
that event.

## Reference anchors (READ-ONLY)

- **Reference stem:** `data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav`
  sha256 `1bad871901294395c1b1ad1c97689e07d879f48aa8b9fc953ea6981d76e09ffd`.
- **Reference MIDI:** c1 bass excerpt, sha16 `4863ca285c7db513`, full sha
  `4863ca285c7db513c8bfc22da5e35e65036b0ecad2538a6d9794c80eb15f8ac9`.
- **Song sha16:** `31a164f845f8e27e` (Chicken Grease).

## Spike panel numbers (raw)

Panel measured on `data/v4/profiles/31a164f845f8e27e/bass_family2_spike/spike.wav`
vs the reference stem:

| Metric                        | Value    |
|-------------------------------|----------|
| `mel_l1_db`                   | 9.3608   |
| `spectral_centroid_rmse_hz`   | 2578.8290 |
| `embedding_cos_vggish`        | 0.3933   |

Composite is not reported at spike stage; the spec's frozen weights (0.5 / 0.25 /
0.25) are search-ordering machinery for c6+, not a c5 gate.

## Spike artifact

- Path: `data/v4/profiles/31a164f845f8e27e/bass_family2_spike/spike.wav`.
- SHA-256: `8a110c06ad9d3e1823b466687276ff723c59ea566ff06e0ed1d1ccfb0c6623ff`.
- Bytes: **141164** (well under the 5 MB budget).
- Sample rate: **44100 Hz**, mono, PCM_16.
- Stem f0 (librosa.pyin, voiced-median): **34.45 Hz** (bass fundamental at the very
  bottom of the pyin range; a first-class quirk of this particular 6-second stem
  captured verbatim, not a bug — c6+ builder cycle may prefer a different f0
  estimator or a per-note reference-slice strategy).
- LUFS-I normalize method: **pyloudnorm** (module PRESENT — probe returned finite
  LUFS on the summed spike; RMS-dBFS fallback code path exists and is unit-tested
  with a zero-signal case in this cycle's spike script).
- Pre-normalize measured LUFS-I: **-32.01 dB** (post-normalize: target -18.00 dB).

Sidecar `spike_summary.json` pins the same numbers plus env pins for the auditor.

## Verdict

`verdict: NOT_APPLICABLE (spike cycle — no profile pinned)`.

The 3-way sf2 family rubric (`SF2_CONFIRMED / SF2_RULED_OUT / STILL_INDETERMINATE`)
is a family-2 rubric only for a family-2 profile, which does not exist yet. The
c5 spike is a mechanism proof; the panel numbers above are for c6 handoff-band
reasoning, not for a verdict.

**Handoff-band call.** `embedding_cos_vggish = 0.3933` falls in the informative
[0.15, 0.75] band from the c5 auditor-handoff downstream-branch rule (it is not
degenerate 0.0/NaN, which is the only band that would route to a spike-fix cycle
instead). Per that rule, c6 opens as the family-2 builder implementation cycle
(and, as its independent second task, the `replay.py` fix cycle). See §c5 auditor
handoff in the c5 brief for the exact branching table.

## READ-ONLY anchor from c4

Referenced only as a preservation contract; not re-analyzed:

- `data/v4/profiles/31a164f845f8e27e/bass_family_verdict.json` sha
  `cbbdbebf00c30e2c2b0b7c6a575fa59c723a7d1294905eec12bbb2166c546228`.
- `data/v4/profiles/31a164f845f8e27e/bass.json` (c2 primary), `bass_v2.json` (c4
  sibling), and both replay proofs are all READ-ONLY and byte-identical
  pre-vs-post c5.

## Replay defect — CRITICAL escalation (blocks c6+ sf2, NOT family-2)

The CRITICAL manager event
`_manager/M-V4-PROFILES-1-replay-program-invariance-critical` — emitted FIRST this
cycle before any other c5 action per §manager_event of the c5 brief — records that
`scripts/sound_match/replay.py::_replay_sf2` L79-85 builds a program-select setup
string and immediately discards it via `_ = setup`. Fluidsynth then honors only the
MIDI-embedded `program_change`, not `profile.identity.program`. Empirical: c2
`bass.replay_proof.json` (profile prog=17) and c4 `bass_v2.replay_proof.json`
(profile prog=33) both produce SHA
`832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5` because
`bass.mid` embeds `program_change=33` (c1 rewrite). Fix scope + regression contract
are named in the event; c6 owns the fix. c5 makes no code change to `replay.py`.

## Storage accounting

| Item                          | Value              |
|-------------------------------|--------------------|
| df before                     | 83% used (`/dev/vda 252G / 31G / 6.7G`)   |
| df after                      | 83% used (spike footprint too small to move the % column) |
| Total new disk this cycle     | **148 KB** under `data/v4/profiles/31a164f845f8e27e/bass_family2_spike/` (spike.wav 141164 B + spike_summary.json) |

The 148 KB spike footprint is orders of magnitude under the 5 MB spike budget and
under the 500 MB per-instrument working-audio cap; disk stayed well below the 90%
ceiling. SWEEP-STORAGE HYGIENE PROC (2026-09-03) is now adopted in
`plan_of_record.md` and applies to every c6+ sweep.
