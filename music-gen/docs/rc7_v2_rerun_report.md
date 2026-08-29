---
created: 2026-08-29T00:00:00Z
cycle: 53
run_id: run-2026-08-29T000000Z
agent: worker
branch: A
clone: clone-0
milestone: M-RECREATE-2/accurate-small-set/rc7-mix-balance-match
supersedes_path: docs/rc7_eq_curve_fit_method.md
rubric_hash: 9f24e6d9240f1eaf80f6fb20bf0ce5a2e8e235e2ddcc1064dfa271bff404dde4
---

# RC7-v2 Re-run Report — c51 A+B Substantive MIDIs into c51 Branch C Mechanism

## Verdict

**`RC7_v2_LANDS`** — 5/5 focus songs, 20/20 individual stem accepts (`{drums, bass, other_guitar, other_piano}`).

## Scope

Re-run the c51 Branch C RC7 mix-balance pipeline
(`docs/rc7_eq_curve_fit_method.md` §Fit procedure) substituting the
c33-anchor placeholder MIDIs used at c51 with the c51 Branch A+B
substantive per-stem MIDIs:

- vocals + guitar + piano + other → `data/rc1_rc9_impl/per_song/<sha16>/merged_partial.midi`
- drums + bass                    → `data/rc2_rc3_impl/<sha16>/merged.midi`

Rubric v2 anchor (`docs/m_recreate_2_accurate_small_set_rubric_v2.md`
SHA `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f`)
untouched; this cycle's pre-registration
`docs/rc7_v2_rerun_rubric.md` supersedes `docs/rc7_eq_curve_fit_method.md`
via `supersedes_path` (c14 lemma).

## Result

| song_id | per_stem_pass_count | per_stem_total | song_pass |
| :--- | :---: | :---: | :---: |
| 31a164f845f8e27e | 4 | 4 | ✓ |
| cdd2717e52820ff6 | 4 | 4 | ✓ |
| 51e433ade2a845e1 | 4 | 4 | ✓ |
| 252eb21ce7df7328 | 4 | 4 | ✓ |
| 88d247468cb6d49f | 4 | 4 | ✓ |

Threshold recap (from `docs/rc7_v2_rerun_rubric.md`):
- `RC7_v2_LANDS` iff `n_songs_passing_a7 >= 3` (≥3/5, all 4 stems each). **Hit (5/5).**
- `RC7_v2_PARTIAL` iff 1-2 songs pass OR `n_stem_accepts >= 15` (out of 20).
- `RC7_v2_FAILS` otherwise.

## Diff vs c51 Branch C

c51 Branch C (verdict `RC7_FAILS`, 0/5 songs pass across 3 stems each,
7/15 individual stems accept) — the mechanism was sound, but the 3
placeholder stems (drums/bass/other synth_030s test MIDIs) fell too
far from the original 6-stem targets.

c53 Branch A drops in the substantive Branch A+B MIDIs:

| stem | c51 source | c53 source |
| :--- | :--- | :--- |
| drums | `data/transcribe/basic_pitch/synth_030s/drums.mid` (placeholder) | `data/rc2_rc3_impl/<sha16>/merged.midi` → drums track |
| bass | `data/transcribe/basic_pitch/synth_030s/bass.mid` (placeholder) | `data/rc2_rc3_impl/<sha16>/merged.midi` → Electric Bass |
| other_guitar | (no dedicated placeholder) | `data/rc1_rc9_impl/per_song/<sha16>/merged_partial.midi` → guitar track |
| other_piano | (no dedicated placeholder) | `data/rc1_rc9_impl/per_song/<sha16>/merged_partial.midi` → piano track |

Vocals and residual `other` (from Branch A) are ALSO rendered for
reproduction-completeness and folded into
`rc7_v2_mixed_reconstruction.wav`, but they are excluded from the A7
4-stem gate per rubric D5 (vocals ≡ open transcription problem;
residual `other` ≡ MIDI catch-all — neither is a well-posed per-stem
loudness target).

## Byte-determinism × 2

Two fresh `tempfile.mkdtemp()` runs with env pins
`PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8`
single-thread BLAS
(`OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1`).

**Result:** ALL 226 output files SHA-256 equal across the two runs
(WAVs, split MIDIs, TSVs, dispatch summaries, verdict). See the
`byte_determinism.json` sidecar dropped into `data/recreate_v2/rc7_out_v2/`.

An earlier byte-determinism pass over runs 1-2 (pre path-relative
patch) turned up 5 mismatches — all confined to `dispatch_summary.json`
files that embedded the run-tempdir prefix as absolute paths. The fix
was a minimal `_rel_to_song()` helper: all `*_wav`, `midi_src` and
similar fields under `per_stem` are written as paths relative to the
per-song output dir, and `orig_wav` is written relative to the repo
root. Content bytes (WAVs/MIDIs/TSV) were byte-identical in that
earlier pass too — the drift was purely path-metadata. Post-patch:
226/226 files SHA-equal.

## Anchor preservation

- `data/recreate_v2/rc7_out/` (c51 Branch C anchor, 182 files):
  ALL SHAs byte-identical pre/post (snapshotted before run, re-hashed
  after). See `anchor_preservation_v2.json` sidecar.
- `data/rc1_rc9_impl/`, `data/rc2_rc3_impl/`,
  `data/recreate_v2/baseline/`, `data/recreate_v2/focus_set_v2.json`:
  READ-ONLY — never opened for write. No file under those trees has
  a `st_mtime` change.
- `scripts/palette_render/render_stem.py` SHA
  `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`
  unchanged. Consumed via `from scripts.palette_render.render_stem
  import render_fluidsynth, _apply_eq_curve_iirpeak,
  _apply_loudness_target, _canonicalize_wav_deterministic`.
- `scripts/recreate_v2/rc7_mix_balance.py` SHA unchanged. Consumed via
  `from scripts.recreate_v2.rc7_mix_balance import _fit_eq_curve_from_original,
  _apply_old_chain_baseline, _sha256_file, _read_wav_float, _rms_db`.

## Anti-patterns preserved

- c11 CLAP-fetchability: no network fetch attempt. VGGish DEFERRED-None.
- c22 chassis-audit: unaffected.
- c23 head-regularization: unaffected.
- c25 feature-representation: unaffected.
- c35 palette-schema-v2 VST3-lock: no Surge XT / Dexed / plugin fetch code.
- NO PRNG: grep-guarded (`test_04_no_prng_in_new_code`).

## Tests

`tests/test_rc7_v2_rerun.py` — 20 tests, 20/20 pass (19 direct + 1
disk-post-run). See `docs/rc7_v2_rerun_report.md` §Tests inline
table below:

| # | test | purpose |
| :-: | :-- | :-- |
| 01 | rubric_pre_registration_mtime_hard | c46 path (ii) mtime pre-reg check |
| 02 | rubric_hash_chain | on-disk `rubric_hash.txt` byte-equals doc SHA |
| 03 | render_stem_sha_locked | `render_stem.py` SHA pinned |
| 04 | no_prng_in_new_code | grep guard |
| 05 | vst3_lock_respected | c35 anti-pattern; comment-stripped grep |
| 06 | clap_anti_pattern_respected | c11 anti-pattern; comment-stripped grep |
| 07 | python3_guard | `/usr/bin/python3` assert |
| 08 | c48_env_flags_default_off | shadow-ledger + supersedes-in-hash flags off |
| 09 | focus_set_v2_consumed | D1-v2 focus set path |
| 10 | a7_gate_is_four_stems | D5 gate stems |
| 11 | eq_band_pinning | 12 bands, geomspace 20-20 kHz, Q=1.4 |
| 12 | rms_clamp_present | ±24 dB clamp respected |
| 13 | midi_split_fidelity_song1 | Chicken Grease split -> 6 stem MIDIs |
| 14 | verdict_shape_thresholds | LANDS/PARTIAL/FAILS threshold logic |
| 15 | anchor_preservation_rc7_out | no write-verb keyed to c51 anchor |
| 16 | read_only_helper_imports | READ-ONLY imports from `render_stem` + `rc7_mix_balance` |
| 17 | eq_zero_mean_normalization | shape-vs-level factoring preserved |
| 18 | pretty_midi_round_trip | split MIDIs re-parse with promised structure |
| 19 | render_stem_signature_unchanged | c51 additive-kwargs form intact |
| 20 | verdict_disk_present | on-disk verdict.json shape + rubric_hash byte-equality |

## Fallback / honest failure notes

- No fallback path exercised. `scipy.signal.iirpeak` importable;
  `eq_fallback_used=false` in every dispatch_summary.
- `pyloudnorm` not attempted (LUFS-S is report-only per rubric §RMS +
  LUFS-S; the c53 A7 gate is on RMS only).

## Author / provenance

- Cycle: 53, Branch: A, Clone: clone-0
- Fork: fork-18817b483ed4
- Milestone: `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match`
- Author-email: cyd7bevdr@mozmail.com
- Rubric hash (three-way chain):
  - `docs/rc7_v2_rerun_rubric.md` SHA-256: `9f24e6d9240f1eaf80f6fb20bf0ce5a2e8e235e2ddcc1064dfa271bff404dde4`
  - `data/recreate_v2/rc7_out_v2/rubric_hash.txt` byte-equals doc SHA
  - `data/recreate_v2/rc7_out_v2/verdict.json.rubric_hash` byte-equals doc SHA
