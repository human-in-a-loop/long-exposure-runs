# RC5 Tempo / Beat-Grid Rubric (c53 Branch C, clone-2)

**Parent:** `M-RECREATE-2/accurate-small-set/rc5-tempo-beat-grid`
**Cycle:** 53 (c50+/c51 branch marker)
**Rubric-v2 chain:** `docs/m_recreate_2_accurate_small_set_rubric_v2.md`
SHA-256 `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f`.

## §1. Fixed invocation (frozen, no PRNG)

Per song, on the ORIGINAL MIX loaded at the file's native sample rate
(mono via `librosa.to_mono`):

```python
tempo, beats = librosa.beat.beat_track(
    y=y, sr=sr,
    hop_length=512,
    start_bpm=120.0,
    tightness=100,
)
raw_estimate = float(tempo)
```

`start_bpm=120.0` and `tightness=100` are the librosa defaults per
version 0.11 and are named explicitly for durability.

## §2. Tempo-octave-correction algorithm

```python
est_variants = [raw_estimate, raw_estimate * 2.0, raw_estimate / 2.0]
diffs = [abs(v - baseline_bpm) for v in est_variants]
idx = min(range(3), key=lambda i: diffs[i])   # deterministic
corrected_estimate = est_variants[idx]
octave_correction_applied = ["none", "double", "half"][idx]
```

Tie-break is deterministic: `min` with `key=` returns the smallest
index on ties (native Python semantics). `baseline_bpm` is read from
`data/recreate_v2/baseline/<sha16>/rc5_tempo_bpm.json`
(READ-ONLY anchor from c49).

## §3. Per-song artifacts

For each song, deterministically write to
`data/rc5_impl/<sha16>/`:

- `rc5_tempo_estimate.json` with keys:
  `song_id`, `raw_estimate`, `corrected_estimate`,
  `octave_correction_applied`, `baseline_bpm`, `abs_diff_vs_baseline`,
  `sample_rate`, `hop_length`, `start_bpm`, `tightness`.
- `merged_retempo.midi` and `merged_retempo.musicxml`: partial MIDI
  loaded READ-ONLY from
  `data/rc1_rc9_impl/per_song/<sha16>/merged_partial.midi`
  (Branch A) if present, else
  `data/rc2_rc3_impl/<sha16>/merged.midi` (Branch B), re-tempoed
  to `corrected_estimate` and written via `music21` (`stream.write`).
  music21 9.1.0 is imported READ-ONLY (c37 lesson: never touch its
  cache).

## §4. Per-song verdict

- **PASS** iff `abs(corrected_estimate - baseline_bpm) <= 2.0` (BPM).
- **PARTIAL** iff PASS threshold missed but the tempo estimate is
  otherwise coherent AND the worker declares low confidence for
  reasons (rhythmic instability, atypical meter). Escalated to c54
  handoff.
- **FAIL** otherwise.

## §5. Aggregate verdict

- **RC5_LANDS** iff ≥3 songs PASS.
- **RC5_PARTIAL** iff 1 or 2 songs PASS.
- **RC5_FAILS** iff 0 songs PASS.

## §6. Byte-determinism × 2

`rc5_tempo_estimate.json` and `merged_retempo.midi` per song must
be byte-identical across two runs performed in fresh
`tempfile.mkdtemp()` directories under environment pins:

- `PYTHONHASHSEED=0`
- `SOURCE_DATE_EPOCH=1756463424`
- `TZ=UTC`
- `LC_ALL=C.UTF-8`
- `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`

## §7. Three-way rubric-hash byte-equality chain

- Doc SHA-256 (this file) ==
- `data/rc5_impl/rubric_hash.txt` (record-only) ==
- `data/rc5_impl/verdict.json.rubric_hash` (embedded verbatim).

## §8. Anchor preservation contract (READ-ONLY)

The following anchors MUST be byte-identical pre and post:

- `docs/m_recreate_2_accurate_small_set_rubric_v2.md` (SHA
  `0e11f704…debe1f`)
- `data/recreate_v2/rubric_hash_v2.txt`
- `data/recreate_v2/rubric_hash.txt` (v1 chain preserved)
- `data/recreate_v2/baseline/<sha16>/rc5_tempo_bpm.json` for each song
- `data/rc1_rc9_impl/per_song/<sha16>/merged_partial.midi` for each song
- `data/rc2_rc3_impl/<sha16>/merged.midi` for each song
- `data/recreate_v2/rc5_tempo_bpm_observed.json` (c51 Branch B)
- `scripts/palette_render/render_stem.py` (do-not-touch invariant)

## §9. Interpreter / environment guards

- Every script under `scripts/recreate_v2/rc5_tempo_beat_grid.py` runs
  under `/usr/bin/python3` (shebang + interpreter probe on entry).
- **NO PRNG**: no `random.*`, `numpy.random.*`, or `torch.*` random
  functions anywhere in this branch. AST-grep enforced by test.
- c48 env-var flags default OFF for this branch:
  `MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION` unset;
  `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH` unset.
