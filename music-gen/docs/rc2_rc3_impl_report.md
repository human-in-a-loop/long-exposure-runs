# RC2 + RC3 Implementation Report — c51 clone-1

**Fork:** 38eba9f21a61 · **Clone:** 1 of 3 · **Cycle:** 51
**Milestones:** `M-RECREATE-2/accurate-small-set/rc2-drum-onset-transcription`, `M-RECREATE-2/accurate-small-set/rc3-bass-transcription`
**Verdict:** **RC2_RC3_LANDS** (4/5 focus songs pass BOTH RC2 and RC3; 5/5 pass RC2; 4/5 pass RC3)

## §1 Objective + inheritance

Kill the c37/c39-42 "5 drum notes in 30s" failure by re-transcribing drums via `librosa.onset.onset_detect` + per-onset band-energy classification (kick 36 / snare 38 / hihat 42 on GM channel 10), and re-transcribe bass via `librosa.pyin` monophonic (E1–E4). Inherits c50 clone parent context: rubric-v2 chain, focus_set_v2 (5 songs incl. Chicken Grease), RC0-v2 baselines per song, and the c48 env-var flags default-OFF discipline.

## §2 Pre-registration

| Artifact | SHA-256 |
|---|---|
| `docs/rc2_rc3_impl_rubric.md` (this rubric doc) | `08a79f51ba237221e252f496e7f90eefe765e477e060192949e05f7a2ae6b8ae` |
| `data/rc2_rc3_impl/rubric_hash.txt` | same as above (three-way byte-equality) |
| `data/rc2_rc3_impl/verdict.json.rubric_hash` | same as above (three-way byte-equality) |
| `data/recreate_v2/rc2_classifier_bands.json` | `68d715fb5d0be7062e4b93900987cedadb12090a78bbc3a87e936c1c1762a94e` |
| Parent v2 rubric (READ-ONLY anchor byte-preserved) | `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f` |
| RC3 approach doc `docs/rc3_bass_approach.md` | pyin monophonic (E1–E4) primary; lowered basic-pitch fallback |

Pre-registration mtime-hard verified in `tests/test_rc2_rc3_impl.py::test_01`.

## §3 RC2 implementation — per-song F1 table

Method: `librosa.onset.onset_detect(hop_length=512, delta=0.07, wait=10, backtrack=False, units='time')` on the 30 s trimmed drums stem; per onset, 50 ms window post-onset → FFT → band-RMS at kick[20,200] / snare[200,3000] / hihat[3000,22050] Hz → argmax → GM channel-10 note.

| Song (sha16) | Drum count | Baseline onset count | Count in [0.5×, 2×] | Onset F1 (±50ms) | RC2 accept |
|---|---:|---:|:---:|---:|:---:|
| `31a164f8` (Chicken Grease, band 6) | 92 | 109 | ✓ [55, 218] | **0.915** | ✓ |
| `cdd2717e` (Disco A, band 5) | 111 | 130 | ✓ | 0.921 | ✓ |
| `51e433ad` (Dojo Cuts, band 5) | 150 | 167 | ✓ | 0.946 | ✓ |
| `252eb21c` (Mura Masa, band 5) | 72 | 88 | ✓ | 0.900 | ✓ |
| `88d24746` (Peach Dream, band 6) | 79 | 80 | ✓ | 0.994 | ✓ |

**RC2 accepts: 5/5.** Chicken Grease: 92 drum notes vs 109-onset baseline — **kills the 5-notes-in-30s failure by an order of magnitude**.

## §4 RC3 implementation — per-song count + low-band correlation table

Method: `librosa.pyin(fmin=41.2Hz=E1, fmax=329.6Hz=E4, sr=44100, hop_length=512)` on the 30 s trimmed bass stem. Contiguous-voiced runs ≥ 60 ms grouped into one note; median f0 → MIDI (round). Segment velocity fixed 100. GM program **33** (Electric Bass). Rendered bass = `pretty_midi.synthesize(wave=np.sin)` at 44.1 kHz mono. Low-band correlation = Pearson on hop=512 RMS envelopes of scipy.signal.butter-order-4 lowpass (< 250 Hz) applied to baseline bass.wav vs rendered bass wav.

| Song | Bass note count | Baseline seg count | Count in band | Median MIDI (< 55) | Low-band corr (≥ 0.5) | RC3 accept |
|---|---:|---:|:---:|:---:|---:|:---:|
| `31a164f8` (Chicken Grease) | 18 | 14 | ✓ | 34 ✓ | 0.557 ✓ | ✓ |
| `cdd2717e` (Disco A) | 55 | 55 | ✓ | 37 ✓ | 0.739 ✓ | ✓ |
| `51e433ad` (Dojo Cuts) | 45 | 49 | ✓ | 37 ✓ | 0.884 ✓ | ✓ |
| `252eb21c` (Mura Masa) | 38 | 42 | ✓ | 41 ✓ | **0.480** ✗ | ✗ |
| `88d24746` (Peach Dream) | 4 | 2 | ✓ | 31 ✓ | 0.814 ✓ | ✓ |

**RC3 accepts: 4/5.** The one miss (`252eb21c`) narrowly misses the 0.5 correlation gate at 0.480 — count band and pitch sanity both pass. Not iterated further this cycle to preserve mtime-hard pre-registration; c52 threshold refinement candidate.

## §5 RC5 side-observation BPM (bookkeeping only)

Recorded per song via `librosa.beat.beat_track(y=bass_stem, sr=44100, hop_length=512, start_bpm=120)` — RC5 full implementation deferred to c52 (own rubric). File: `data/recreate_v2/rc5_tempo_bpm_observed.json`.

| Song | Estimated BPM |
|---|---:|
| Chicken Grease | 178.21 (double-time detection artifact vs ~89 half-time; funk expected ~110) |
| Disco A | 95.70 |
| Dojo Cuts | 156.61 |
| Mura Masa | 99.38 |
| Peach Dream | 60.80 (half-time detection) |

## §6 Byte-determinism × 2

Two fresh runs (second inside a fresh `tempfile.mkdtemp()`, envs re-pinned via subprocess). SHA-256 asserted equal per song across all four tracked artifacts (`rc2_drum_notes.jsonl`, `rc3_bass_notes.jsonl`, `merged.midi`, `rc3_bass_rendered.wav`) — **5 songs × 4 anchors = 20 SHA equalities, ALL PASS**. Pinned in `data/rc2_rc3_impl/byte_determinism.json`.

Env pins: `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`, `OMP/MKL/OPENBLAS_NUM_THREADS=1`. NO PRNG called. `torch.manual_seed` unused (no torch on RC2/RC3 path).

## §7 Anchor preservation

47 anchor SHAs snapshotted in `data/rc2_rc3_impl/anchor_preservation.json`. Covers:
- c49 v1 rubric (`958ade38…3fe58b9d`) + `rubric_hash.txt`
- c50 v2 rubric (`0e11f704…debe1f`) + `rubric_hash_v2.txt`
- `focus_set.json` + `focus_set_v2.json`
- All 6 c50 sibling stubs (`rc1_v2_hybrid`, `rc4_v2_gm_program_map`, `rc6_v2_panel_gate`, `rc7_mix_balance`, `rc8_section_selection`, `rc9_first_class_parts`)
- All 5 focus songs × 6 RC0/RC0-v2 baseline files = 30 rows
- `scripts/palette_render/render_stem.py` (Branch C anchor, MUST NOT be touched)
- 3 rules ledgers + `anchor_manifest_v1.json`

## §8 Test coverage

`tests/test_rc2_rc3_impl.py`: **20/20 PASS** (target ≥15/20).

01 classifier-bands mtime-before-scripts · 02 three-way rubric_hash byte-equality · 03 parent rubric_v2 preserved · 04 c49 v1 rubric SHA unchanged · 05 NO PRNG · 06 no sidecar_nonfactor · 07 no render_effects_layered · 08 no palette_render · 09 interpreter guard · 10 byte-determinism × 2 · 11 RC2 F1 in [0,1] · 12 RC3 count ≥ 0 · 13 RC3 correlation in [-1,1] · 14 median MIDI < 55 · 15 RC5 BPM finite · 16 Chicken Grease count > 27 · 17 focus-set section preserved · 18 verdict in frozen enum · 19 anchor count ≥ 30 · 20 palette_render untouched.

## §9 Verdict + parent-chain preservation

- **Verdict: RC2_RC3_LANDS** (both = 4, either = 5, errors = 0; ≥3/5 with BOTH accept).
- `rubric_hash`: `08a79f51ba237221e252f496e7f90eefe765e477e060192949e05f7a2ae6b8ae` (this doc's SHA-256).
- `parent_rubric_hash_v2`: `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f` (c50 v2 anchor byte-preserved).
- Three-way chain enforced: doc SHA == `data/rc2_rc3_impl/rubric_hash.txt` == `verdict.json.rubric_hash`.
- File `data/rc2_rc3_impl/verdict.json` carries per-song RC2/RC3 accept table + counts rollup + env pins.

## §10 Handoff seeds for c52+

1. **RC5 full impl (c52 linear)**: fold `librosa.beat.beat_track` into merged.midi tempo events. This cycle only recorded side-observation. Double-time / half-time verdicts (Chicken Grease 178 BPM, Peach Dream 60 BPM) suggest a tempo octave-normalization pass at c52.
2. **RC3 correlation tightening for `252eb21c`** (0.480 vs 0.500 gate). Options: (a) longer segment min (>60ms), (b) tighter voiced-fraction filter, (c) alternate fallback via basic-pitch lowered thresholds per rubric.
3. **RC4 program-map assembly (c52+ Branch A/B/C integration)**: this cycle's `merged.midi` writes drums (channel 10, is_drum=True) + bass (GM 33). Branch A (RC1 vocals) needs to add vocal lead voice; Branch C's RC7 mix + D4 EQ will consume both.
4. **RC6-v2 panel gate (c52+ integration)**: not gated this cycle; requires VGGish rung wired in.
5. **Chicken Grease Chicken Grease-specific target ALREADY MET**: drum count 92, F1 0.915. c52 integration cycle can move directly to per-branch fold-in without RC2 iteration.
6. **Housekeeping**: c48 env-var flags remain default OFF; `scripts/palette_render/render_stem.py` untouched; c22 stability harness / c26-c30 collision utilities / M-EAR-1 / M-GEN-1 not opened.

## Ledger events emitted (8 total)

1. `M-RECREATE-2/accurate-small-set/rc2-drum-onset-transcription` — substantive, unsuffixed per c32 (status=validated, verdict RC2_RC3_LANDS).
2. `M-RECREATE-2/accurate-small-set/rc3-bass-transcription` — substantive, unsuffixed (status=validated).
3. `_infra/rc2-classifier-bands-pinned-clone-1`
4. `_infra/rc2-rc3-anchor-preservation-verified-clone-1`
5. `_run/rc2-rc3-byte-determinism-verified-clone-1`
6. `_run/cycle_51_closed-clone-1`
7. `_archive/cycle-51-scratch-clone-1`
8. `_infra/adopt-cycle51-tests-clone-1`

Plus egress probe tail: `M-INGEST-1/egress-probe-cycle51-clone-1`.
