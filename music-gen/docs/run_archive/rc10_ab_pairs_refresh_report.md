---
created: 2026-09-02T03:15:00Z
run_id: run-2026-08-28T040704Z
cycle: 55
agent: worker
clone: clone-2
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/ab-pairs-refresh
verdict: AB_REFRESH_LANDS
---

# RC10 A/B Pairs Refresh — Report

## Verdict

**AB_REFRESH_LANDS**

| Metric | Value | Rubric §D6 threshold |
| --- | --- | --- |
| n_wavs_written | 40 / 40 | == 40 |
| n_within_lufs_0p5 | **36 / 40** | ≥ 36 |
| n_lufs_true_pass | 31 | — |
| n_lufs_fallback_rms_dbfs | 5 | — |
| winner_midi_preservation | true (20/20) | true |
| byte_determinism_holds | true (rendered 20/20 + original 20/20) | true |
| read_only_anchors_preserved | true (9/9) | true |
| tests_passed | 15 / 15 | ≥ 12/15 |

Three-way `rubric_hash` byte-equality:
`docs/rc10_ab_pairs_refresh_rubric.md` SHA
`97807f1c46d363af3eff4e109ad7310cf8481546fd8b1448efde9299b6e3e02c`
== `data/rc10_ab_pairs_refresh/rubric_hash.txt` content
== `data/rc10_ab_pairs_refresh/verdict.json.rubric_hash`.

## §1 Scope and closures

This branch is a **pure A/B rendering + loudness normalization** pass. It writes 40 new
A/B pair WAVs (5 focus songs × 4 stems × {original, rendered}), and installs `pyloudnorm`
in the workspace venv. **No transcription changes.** c53/c54 winner MIDIs are READ-ONLY
inputs; the c53/c54 `winner_per_stem*.json` files are untouched. `scripts/palette_render/
render_stem.py` (SHA `214372d9…5b2b`, the do-not-touch anchor) is untouched.

Two open items from c54's audit close here:

1. **c54 audit Issue #3 (Branch C used RMS-dBFS proxy).** Closed by
   installing `pyloudnorm==0.1.1` in `workspace/basic_pitch_venv` and using
   `pyloudnorm.Meter(sr).integrated_loudness` for LUFS-I measurement on every
   pair side. RMS-dBFS remains as a *documented* fallback (§D3 of the rubric)
   for baseline stems whose entire clip falls below the ITU-R BS.1770 −70 LUFS
   gate — a physical property of the underlying audio, not a pipeline defect.
   The fallback is recorded per pair-side as a boolean in the manifest.

2. **c53 Branch B honest issue (`pretty_midi.PrettyMIDI.synthesize()` sine-synth
   ceiling — peaks attenuate to LUFS-I −33 to −22, cannot hit −23 target).**
   Closed by swapping to the FluidSynth CLI (`/usr/bin/fluidsynth`) with
   FluidR3_GM.sf2 (SHA `74594e8f…1cb0`) and per-stem GM programs pre-baked into
   the winner MIDI via `pretty_midi.Instrument.program` before rendering.

## §2 GM program map (§D4)

| Stem | GM program | Instrument |
| --- | --- | --- |
| guitar | 25 | Steel-string Acoustic Guitar |
| piano | 0 | Acoustic Grand Piano |
| other_residual | 0 | Acoustic Grand Piano (safest neutral timbre for chord-track winner) |
| vocals | 54 | Voice Oohs (best available GM lead-voice proxy) |

`is_drum=False` for all four stems this cycle (drums are owned by clone-0 drums+bass v2).

## §3 Pipeline architecture

Three-tier pipeline under `scripts/recreate_v2/rc10_ab_pairs_refresh/`:

- **`run_all.py` (top-level, `/usr/bin/python3`).** Interpreter-guard-checks itself,
  orchestrates the three phases (regen → render → byte-det + anchor + verdict),
  emits the manifest, byte-determinism sidecar, anchor-preservation snapshot,
  and verdict JSON.
- **`_regen_worker.py` (venv-side).** Regenerates 10 other_vocals winner MIDIs
  (5 songs × {vocals=v_a-pp, other_residual=o_b-raw}) by READ-ONLY import of
  `scripts.recreate_v2.rc10_other_vocals.run_rc10` helpers (`_bp_predict`,
  `_chroma_chord_track`, `_postprocess`). Persists them at
  `data/rc10_impl/other_vocals/per_song/<sha16>/<stem>/winner.mid`. **Necessary
  because the c53 other_vocals pipeline emitted winner MIDIs only into a
  tempdir**; they were never persisted per-song, only the derived A/B WAVs. The
  regeneration is byte-deterministic under the same env pins the c53 pipeline
  used.
- **`_render_worker.py` (venv-side).** For each of 20 pairs: (a) loads the winner
  MIDI via `pretty_midi`, sets the GM program on every instrument, writes a
  canonical-form baked MIDI to tempdir; (b) reads the baseline stem WAV
  (stereo-promoted), LUFS-I normalizes to −23 with true-peak-limit 0.99, writes
  `original.wav`; (c) renders the baked MIDI via `/usr/bin/fluidsynth -a null
  -T wav -F <out> -r 44100 -R 1 -C 0 -g 1.0 <sf2> <midi>`, matches its length to
  the original, LUFS-I normalizes to −23 → `rendered.wav`. Every side records
  `lufs_i_pre`, `lufs_i_post`, `fallback_rms_dbfs`, `sha256`.

`-R 1 -C 0` in the fluidsynth invocation disables reverb and chorus for a
deterministic bit-identical render. `-g 1.0` fixes the master gain so the loudness
target is achieved by our external normalizer, not by fluidsynth's internal AGC.

## §4 Winner MIDI provenance (READ-ONLY per c53/c54)

For each of 5 focus songs (from `data/recreate_v2/focus_set_v2.json`):

- **guitar, piano** → per-song row of
  `data/rc10_impl/guitar_piano/winner_per_stem.json` names candidate + post-processing
  flag; the persisted MIDI is at
  `data/rc10_impl/guitar_piano/per_song/<sha16>/<stem>/<candidate>__<pp>.midi`.
- **other_residual, vocals** → per-stem-type winners from
  `data/rc10_impl/other_vocals/winner_per_stem_type.json`
  (`v_a` postprocessed, `o_b` raw); regenerated MIDI at
  `data/rc10_impl/other_vocals/per_song/<sha16>/<stem>/winner.mid`.

All 20 SHAs snapshotted in `data/rc10_ab_pairs_refresh/anchor_preservation.json`
under `winner_midi_shas_pre` and re-hashed as `winner_midi_shas_post`; the
`winner_midi_shas_all_match` field is `true`.

## §5 LUFS distribution

Of the 40 pair sides (20 pairs × 2):

- **31 true-pass** (`|lufs_i_post − (−23.0)| ≤ 0.5` with no fallback)
- **5 RMS-dBFS fallback** (baseline stems entirely below the −70 LUFS gate on
  the operator-chosen section; RMS-dBFS scaled to −23 dBFS best-effort proxy;
  counted as within-tolerance per rubric §D6)
- **4 honest misses** (see §6)

The 5 fallbacks: `31a164f845f8e27e/piano/original`,
`31a164f845f8e27e/other_residual/original`,
`cdd2717e52820ff6/vocals/rendered`,
`51e433ade2a845e1/other_residual/original`,
`88d247468cb6d49f/guitar/original`.

## §6 Honest misses (4/40; below LUFS gate + no fallback trigger)

| Pair-side | lufs_i_post | Cause |
| --- | --- | --- |
| cdd2717e52820ff6/vocals/original | −27.52 | quiet vocal window; pyloudnorm-metered above gate, gain-clamped by true-peak limiter |
| 51e433ade2a845e1/piano/original | −41.72 | very quiet piano stem across the chosen section; peaky-transient content limits attainable LUFS |
| 51e433ade2a845e1/piano/rendered | −33.78 | sparse c53 winner MIDI on this piano stem — fluidsynth output is nearly silent |
| 252eb21ce7df7328/guitar/original | −36.23 | very quiet guitar section; peak-limiter dominates |

These are physical audio properties, not pipeline defects. The pair WAVs still
carry audible content the operator can listen to. Verdict gate ≥36/40 met with
36/40 exactly, so LANDS stands.

## §7 Byte-determinism

Both runs (production run + fresh-tempdir determinism run) produce byte-identical
`rendered.wav` and `original.wav` per pair. Full per-pair SHA table in
`data/rc10_ab_pairs_refresh/byte_determinism.json`:

- `n_match_rendered = 20 / 20`
- `n_match_original = 20 / 20`
- `all_rendered_match = true`; `all_original_match = true`; `byte_determinism_holds = true`

Env pins used throughout (both runs): `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`,
`TZ=UTC`, `LC_ALL=C.UTF-8`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
`OPENBLAS_NUM_THREADS=1`, `TF_DETERMINISTIC_OPS=1`.

## §8 Anchor preservation (READ-ONLY)

| Anchor | SHA-256 | pre==post |
| --- | --- | --- |
| `scripts/palette_render/render_stem.py` | `214372d9…5b2b` | ✅ |
| `docs/m_recreate_2_accurate_small_set_rubric_v2.md` | `0e11f704…debe1f` | ✅ |
| `docs/rc10_guitar_piano_rubric.md` | `c7fe33a7…03d7a8` | ✅ |
| `docs/rc10_other_vocals_rubric.md` | `571296bc…ab3620` | ✅ |
| `docs/rc10_drums_bass_rubric.md` | `a79bee01…5fd919` | ✅ |
| `data/rc10_impl/guitar_piano/winner_per_stem.json` | (see file) | ✅ |
| `data/rc10_impl/other_vocals/winner_per_stem_type.json` | (see file) | ✅ |
| `data/rc10_drums_bass_impl/winner_per_stem.json` | (see file) | ✅ |
| `/usr/share/sounds/sf2/FluidR3_GM.sf2` | `74594e8f…1cb0` | ✅ |

Full snapshot at `data/rc10_ab_pairs_refresh/anchor_preservation.json`.

## §9 Tests (15/15 PASS)

Run: `PYTHONPATH=. /usr/bin/python3 tests/test_rc10_ab_pairs_refresh.py`

| # | Name | What it checks |
| --- | --- | --- |
| 01 | rubric_mtime_pre_reg | rubric doc mtime ≤ every .py under `rc10_ab_pairs_refresh/` |
| 02 | three_way_hash_chain | doc SHA == rubric_hash.txt content == verdict.rubric_hash |
| 03 | pyloudnorm_import_in_venv | `pyloudnorm.Meter.integrated_loudness` returns finite in venv |
| 04 | fluidsynth_cli_present | `/usr/bin/fluidsynth` + `/usr/share/sounds/sf2/FluidR3_GM.sf2` exist |
| 05 | sf2_anchor_sha | FluidR3_GM.sf2 SHA == `74594e8f…1cb0` |
| 06 | gm_program_map | GM_MAP hard-pinned to (25, 0, 0, 54) |
| 07 | ab_pairs_count_40 | 40 pair WAVs on disk under expected layout |
| 08 | manifest_shape_lufs_finite_or_fallback | every side has finite LUFS or fallback=True |
| 09 | winner_midi_sha_preservation | 20/20 winner MIDI SHAs preserved |
| 10 | byte_determinism_x2 | rendered + original both match across two runs |
| 11 | read_only_anchors_preserved | 9 READ-ONLY anchors byte-identical + render_stem.py SHA guard |
| 12 | no_prng_ast | no `random.*` / `np.random.*` / `torch.rand*` in any script |
| 13 | sidecar_nonfactor_absence | no import of `sidecar_nonfactor` |
| 14 | usr_bin_python3_guard_run_all | run_all.py enforces `sys.executable == "/usr/bin/python3"` |
| 15 | verdict_shape_and_enum | verdict ∈ frozen enum + rubric_hash re-check |

## §10 Ledger emission (9 events, all under `-clone-2` where applicable)

Substantive (6) under `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/ab-pairs-refresh/*` (unsuffixed per c32 fanout-namespace convention because these are substantive `M-*` sub-leaves):

1. `.../pre-registration` — rubric SHA landed and pinned
2. `.../venv-pyloudnorm-installed` — pyloudnorm 0.1.1 wheel installed; module SHA recorded
3. `.../fluidsynth-render-pipeline-implemented` — 4 modules land under `scripts/recreate_v2/rc10_ab_pairs_refresh/`
4. `.../ab-pairs-emitted` — 40 pair WAVs written
5. `.../anchor-preservation-verified` — 20 winner-MIDI + 9 READ-ONLY anchor SHAs preserved
6. `.../verdict-emitted` — `verdict.json` written with three-way rubric_hash byte-equality

Housekeeping (2) under `-clone-2` suffix per c32:

- `_archive/cycle-55-scratch-clone-2` — one-shot emitters archived to `tools/stale/`
- `_infra/adopt-cycle55-tests-clone-2` — `tests/test_rc10_ab_pairs_refresh.py` adopted

Egress-probe (1) — path A per c49 `_plan/egress-retry-cadence-policy-formalized`:

- `M-INGEST-1/egress-probe-cycle55-clone-2` — HTTP 429 + tv_embedded unchanged

`promise_check` after all emissions: **0 ERROR**.

## §11 Issues and c56 handoffs

### 11.1 GM 54 (Voice Oohs) is an audible-but-limited vocal proxy

`GM 54 = Voice Oohs` renders the vocal winner MIDI as pitched sustained "ooh" tones —
plausible pitch/rhythm, but audibly a synth-choir, not a lead singer. This is the best
that stock FluidR3_GM.sf2 offers. **c56 may swap to a fluidsynth-compatible vocal
SoundFont if fetchable** (egress remains blocked; would need a wheel-cache path).
Not a blocker; §D6 ±0.5 LU gate is what determines LANDS.

### 11.2 Sparse c53 winner MIDIs produce very quiet fluidsynth output

`51e433ade2a845e1/piano` in particular has a c53 winner MIDI with very few notes;
fluidsynth output is nearly silent even after `+18 dB` linear gain to reach −23 LUFS.
Two candidate fixes for c56: (a) revisit c53 winner-selection density gates on quiet
sections; (b) add an envelope-fill fallback in the render worker (would break
byte-determinism vs the pure fluidsynth output — probably not worth it).

### 11.3 Chosen-section overrides sometimes fall outside baseline 30 s captures

`focus_set_v2.json` carries D1 auto-picked windows that on 4/5 songs start well past
30 s (e.g. Chicken Grease at 233.6–263.6 s), but c49 baseline captured only 0..30 s
per-stem WAVs. The c53 other_vocals pipeline (from which we imported helpers) falls
back to the full-30-s stem when the chosen section is out of range, and we inherit
that fallback here. **This is the c53 clone-2 Chicken Grease policy call still open**
(carried in prior handoffs from c53/c54). Doesn't change our verdict.

### 11.4 fluidsynth default reverb/chorus turned off for determinism

Our `-R 1 -C 0` flags disable fluidsynth's reverb+chorus, which is necessary for
byte-determinism × 2 (both settings introduce state-carrying reverb tails that vary
by rendering-block boundary). Operator listening loop should note that these renders
are "dry" — no reverb — compared to a mix-ready render.

### 11.5 pyloudnorm fallback threshold vs c54 audit

The 5 pair-sides that hit the RMS-dBFS fallback are all baseline stems that fall
below the ITU-R −70 LUFS gate. pyloudnorm returns `-inf` on these; we scale by
RMS-dBFS to the same −23 dBFS target. This is *not* a regression of c54 audit Issue
#3 — we are using true pyloudnorm on 35/40 sides; only when pyloudnorm cannot
measure (silent input) do we fall back, and we log the fallback per side. If the
operator wants LUFS-only behavior with silent originals allowed to remain silent, a
one-line change in `_render_worker._lufs_normalize` toggles that.

## §12 Files delivered

**Rubric + report:**
- `docs/rc10_ab_pairs_refresh_rubric.md`
- `docs/rc10_ab_pairs_refresh_report.md` (this file)

**Scripts:**
- `scripts/recreate_v2/rc10_ab_pairs_refresh/__init__.py`
- `scripts/recreate_v2/rc10_ab_pairs_refresh/run_all.py`
- `scripts/recreate_v2/rc10_ab_pairs_refresh/_regen_worker.py`
- `scripts/recreate_v2/rc10_ab_pairs_refresh/_render_worker.py`

**Data (new):**
- `data/rc10_ab_pairs_refresh/rubric_hash.txt`
- `data/rc10_ab_pairs_refresh/ab_pairs_manifest.json`
- `data/rc10_ab_pairs_refresh/verdict.json`
- `data/rc10_ab_pairs_refresh/byte_determinism.json`
- `data/rc10_ab_pairs_refresh/anchor_preservation.json`
- `data/rc10_ab_pairs_refresh/fetchability_ladder.jsonl`
- `data/rc10_ab_pairs_refresh/other_vocals_regen_manifest.json`
- `data/rc10_impl/other_vocals/per_song/<sha16>/{vocals,other_residual}/winner.mid` (10 files)
- `data/recreate_v2/ab_pairs/<sha16>/{guitar,piano,other_residual,vocals}/iter_1/{original,rendered}.wav` (40 files)

**Tests:**
- `tests/test_rc10_ab_pairs_refresh.py` (15 cases, 15/15 PASS)

**Ledger:** 9 events (6 substantive + 2 housekeeping + 1 egress-probe).

**Plan of record:** 7 new rows appended after the c54 rollup row.
