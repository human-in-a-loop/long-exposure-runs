---
created: 2026-08-29T00:00:00Z
cycle: 53
run_id: run-2026-08-29T000000Z
agent: worker
branch: A
clone: clone-0
milestone: M-RECREATE-2/accurate-small-set/rc7-mix-balance-match
supersedes_path: docs/rc7_eq_curve_fit_method.md
---

# RC7-v2 Re-run Rubric — c51 Branch C Mechanism × c51 A+B Substantive MIDIs

**Pre-registration (mtime hard):** this document lands BEFORE any edit under
`scripts/recreate_v2/rc7_v2_*.py`, `scripts/recreate_v2/rc7_mix_balance.py`,
or `scripts/palette_render/render_stem.py` (c46 path (ii): mtime hard,
git-log advisory).

## Scope

Re-run the c51 Branch C RC7 mix-balance pipeline (`docs/rc7_eq_curve_fit_method.md`)
substituting the c33-anchor **placeholder** MIDIs with the c51 Branch A+B
**substantive** per-stem MIDIs:

- vocals + guitar + piano + other  → `data/rc1_rc9_impl/per_song/<sha16>/merged_partial.midi`
  (c51 Branch A output; READ-ONLY).
- drums + bass                     → `data/rc2_rc3_impl/<sha16>/merged.midi`
  (c51 Branch B output; READ-ONLY).

The mechanism (12-band iirpeak EQ, RMS + LUFS-S loudness match) is
UNCHANGED from `docs/rc7_eq_curve_fit_method.md`; ONLY the MIDI inputs
change.

## Frozen decisions (D-block)

- **D1** (input source): merged MIDI per song is split into 4 stems for
  A7 accept — drums, bass, `other_guitar`, `other_piano`. Vocals and the
  Branch-A `other` bucket are rendered for reproduction fidelity but NOT
  counted in the A7 4-stem pass gate (see D5 rationale below).
- **D2** (stem naming): output directories under
  `data/recreate_v2/rc7_out_v2/<sha16>/` are `bare_<stem>/`,
  `matched_<stem>/`, `old_chain_<stem>/` for stem ∈
  {drums, bass, other_guitar, other_piano}. Naming mirrors c51 Branch C
  suffix pattern so anchors are trivially diff-able.
- **D3** (render_stem contract): consume
  `scripts/palette_render/render_stem.py` SHA
  `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`
  in the c51-extended additive-kwargs form READ-ONLY:
  `render_stem(stem, instrument, out_dir, *, parameter_dict=None, eq_curve=None, loudness_target=None) -> dict`.
- **D4** (old-chain diagnostic): the c33 old chorus+reverb chain is
  applied to bare renders and dumped as `panel_baseline_old_chain_v2.tsv`
  DIAGNOSTIC ONLY — never a LANDS deliverable.
- **D5** (4-stem A7 gate): guitar and piano are pulled from the Branch-A
  `other` bucket via first-class part decomposition. The Branch-A
  `vocals` and residual `other` tracks are rendered but excluded from
  the A7 4-stem pass count because (i) Branch A's vocals melody
  extraction is heuristic (transcribing sung vocals to MIDI is a
  separate open problem not adjudicated in this milestone), and (ii)
  the residual `other` bucket is a MIDI catch-all whose per-stem
  loudness match is not a well-posed target. Vocals + other are still
  written to bare/matched/old-chain directories for completeness of the
  reconstruction sum.

## Pipeline (per focus song)

1. **Load** `focus_set_v2.json.chosen_section` (30 s window).
2. **Split** merged MIDI into per-instrument single-track MIDIs
   (drums, bass, guitar, piano):
   - drums = pretty_midi instrument with `is_drum=True` from Branch B.
   - bass = program 33 (Electric Bass) instrument from Branch B.
   - guitar = instrument with `name=='guitar'` from Branch A.
   - piano = instrument with `name=='piano'` from Branch A.
   - vocals, other = written for completeness; not in A7 gate.
3. **Bare render** each stem via `render_stem(..., parameter_dict=None,
   eq_curve=None, loudness_target=None)` — the c33 all-None dispatch
   path (VST3-locked; c35 anti-pattern preserved).
4. **EQ fit + apply**: for each stem, fit 12-band iirpeak curve (Q=1.4,
   `np.geomspace(20, 20000, 12)`) against the ORIGINAL 6-stem baseline
   spectrum on the chosen section (`data/recreate_v2/baseline/<sha16>/rc7_per_stem_loudness.json`
   supplies target log-magnitude; if unavailable at per-band resolution,
   re-derive from the source stem WAV). Method identical to
   `docs/rc7_eq_curve_fit_method.md` §Fit procedure — clamped ±12 dB per band.
5. **RMS + LUFS-S match**: scale to the baseline `rc7_per_stem_loudness.json`
   target RMS; measure LUFS-S report-only. Clamp scalar ±24 dB.
6. **D4 old chain**: also route bare renders through the c33 chorus+reverb
   chain and dump `panel_baseline_old_chain_v2.tsv` (diagnostic).
7. **Sum**: `matched_drums.wav + matched_bass.wav + matched_other_guitar.wav
   + matched_other_piano.wav + matched_vocals.wav + matched_other.wav`
   → `rc7_v2_mixed_reconstruction.wav`. Peak-normalize to −1 dBFS if the
   sum clips (`abs.max() > 0.999`); otherwise leave un-normalized.

## A7 accept gate (per-stem, per-song)

Per stem s ∈ {drums, bass, other_guitar, other_piano}:
- `|measured_rms_db(matched_s) − baseline_target_rms_db(s)| ≤ 3.0 dB`
- `|measured_lufs_s(matched_s) − baseline_target_lufs_s(s)| ≤ 3.0 LU`
  (REPORT-ONLY; not gate)

Song passes A7 iff all 4 stems pass the RMS gate. Individual stem accepts
are tallied for the `RC7_v2_PARTIAL` fallback.

## Verdict schema

`data/recreate_v2/rc7_out_v2/verdict.json`:

```json
{
  "milestone_id": "M-RECREATE-2/accurate-small-set/rc7-mix-balance-match",
  "cycle": 53,
  "branch": "A",
  "clone": "clone-0",
  "supersedes_verdict": "data/recreate_v2/rc7_out/verdict.json",
  "eq_curve_method": "iirpeak_12band_log_spaced_Q1.4",
  "acceptance_criterion": "per-stem RMS <= 3 dB vs baseline over 4 stems {drums,bass,other_guitar,other_piano}; LUFS-S report-only",
  "n_songs_total": 5,
  "n_songs_passing_a7": <int>,
  "n_stem_accepts": <int>,
  "n_stem_total": 20,
  "per_song_passes": [
    {"song_id": "...", "per_stem_pass_count": <0-4>, "per_stem_total": 4, "song_pass": <bool>},
    ...
  ],
  "verdict": "RC7_v2_LANDS" | "RC7_v2_PARTIAL" | "RC7_v2_FAILS",
  "d4_old_chain_baseline_present": true,
  "rubric_hash": "<sha256 of docs/rc7_v2_rerun_rubric.md>"
}
```

Verdict thresholds:
- `RC7_v2_LANDS` iff `n_songs_passing_a7 >= 3` (≥3/5 songs, all 4 stems each).
- `RC7_v2_PARTIAL` iff `1 <= n_songs_passing_a7 <= 2` OR `n_stem_accepts >= 15`.
- `RC7_v2_FAILS` otherwise.

## Byte-determinism × 2

Fresh `tempfile.mkdtemp()` twice per run; env pins
`PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8`
single-thread BLAS (`OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
OMP_NUM_THREADS=1`). All output SHA-256 equal across runs. NO PRNG.

## Anchor preservation

`data/recreate_v2/rc7_out/` — c51 Branch C 95-entry anchor — all
existing SHAs byte-identical pre/post. `data/rc1_rc9_impl/`,
`data/rc2_rc3_impl/`, `data/recreate_v2/baseline/`,
`data/recreate_v2/focus_set_v2.json` READ-ONLY.

## Anti-patterns preserved

- c11 CLAP-fetchability: VGGish DEFERRED-None (no network fetch).
- c35 palette-schema-v2 VST3-lock: no plugin fetch attempt.
- c22 chassis-audit, c23 head-reg, c25 feature-representation: untouched.
- NO PRNG anywhere (grep guard in test).

## Author

- Cycle: 53, Branch: A, Clone: clone-0
- Fork: fork-18817b483ed4
- Author-email: cyd7bevdr@mozmail.com
- Milestone: `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match`
