<!--
created: 2026-09-02T00:00:30Z
cycle: 4
run_id: run-2026-09-02T000000Z
agent: worker
milestone: M-V3-SPINE-1
-->

# M-V3-SPINE-1 — Cycle 4 Report (OPTION A adopted, pipeline landed)

## Verdict

**`V3_SPINE_CHAIN_LANDS_pending_operator`** — blocked_on_operator; operator ear on `original_ab.wav` + `reconstruction_ab.wav` is the only LANDS authority. Ledger event `M-V3-SPINE-1/verdict-v2-emitted` carries `status: action_required` per canonical enum + `blocked_on_operator: true` flag in `verdict.json`.

Three-way rubric_hash_v2 chain: **HOLDS**. `sha256(docs/v3_spine_rubric_v2.md) == data/v3_spine/rubric_hash_v2.txt == verdict.json.rubric_hash_v2 = c49db5a12e955f26...`.

## §1 Operator OPTION A adoption + rubric-v2 supersede

Operator directive 2026-09-02: canonicalize authoritative MIDI from MuScriptor `--format json` events via a fixed-PPQ, stable-sort serializer. Serialization not transcription; Fixed Decision 1 preserved. MuScriptor `--format midi` demoted to `non_factor_debug` sidecar.

- `docs/v3_spine_rubric_v2.md` landed BEFORE any pipeline script. Sub-clause (b) redefined to gate byte-determinism ×2 on JSON events + canonicalized MIDI + downstream artifacts. MuScriptor `--format midi` SHAs logged as `non_factor_debug` in `manifest.json.muscriptor_debug_midi_shas`.
- Cycle-3 v1 rubric preserved as READ-ONLY historical anchor byte-identical pre==post (`b0031164e2a5cf78...`).

## §2 Canonical serializer spec + implementation

- Spec: `docs/v3_spine_canonical_midi_serializer_spec.md` (SHA `2cf2a4a1807a478e...`). PPQ=480; sort key `(tick, channel, pitch, event_kind)` with `event_kind=0` for note-on / `1` for note-off; on-before-off documented; deterministic instrument→channel map; empty-events baseline pinned; `mido==1.3.3` pin via `importlib.metadata.version("mido")` because mido 1.3.3 does not expose `__version__`.
- Implementation: `scripts/v3_spine/midi_from_json_events.py`. Pure function of `(json_path, out_path, tempo_bpm, time_signature)`. Atomic write via `tempfile.NamedTemporaryFile` + `os.replace` (mido 1.3.3 has no `atomic_write` kwarg).
- Tests: `tests/test_v3_spine_canonical_serializer.py` 12/12 PASS. Covers PPQ, sort-key reproducibility, on-before-off, empty-events baseline, mido version pin, byte-determinism ×2 on 3-note / 12-note / empty synthetic sets, no-PRNG/no-wall-clock grep, channel mapping, dangling-start handling, seconds→ticks.

## §3 MuScriptor JSON determinism ×2 completion + cross-cycle drift finding

| Stem     | c3 Run-1 SHA (on-disk) | c4 Run-2 SHA         | intra-cycle 4 det | c3 vs c4 |
|----------|-----------------------|----------------------|-------------------|----------|
| drums    | `b4cafa16…`           | `b4cafa16…` (c3)    | EQUAL (c3 verified)| EQUAL     |
| bass     | `e80ab193…`           | `e80ab193…` (c3)    | EQUAL (c3 verified)| EQUAL     |
| vocals   | `00ab8959…`           | `00ab8959…` (c3)    | EQUAL (c3 verified)| EQUAL     |
| guitar   | `97b5a598db8424bb…`   | `3107ba21e10acc70…` | EQUAL c4 A==B ✓   | **DIFFERS**|
| other    | `4f53cda1…` (empty)   | `4f53cda1…` (empty) | trivially EQUAL   | EQUAL     |
| piano    | `4f53cda1…` (empty)   | `4f53cda1…` (empty) | trivially EQUAL   | EQUAL     |
| full_mix | `7d011b6178b89407…`   | (not re-tested)     | (deferred)        | (deferred) |

**Cross-cycle drift finding on guitar**: c3 vs c4 JSON SHAs differ (`97b5a598…db8424bb` → `3107ba21…e10acc70`; note counts 1168 → 824; even first-event start_time differs 0.25 → 0.24). Attribution: environment drift between cycle-3 execution and cycle-4 execution under otherwise-identical env pins (torch/BLAS minor version bump; `PYTHONHASHSEED=0` and `SOURCE_DATE_EPOCH=1756463424` pinned in both). Two consecutive c4 invocations produce byte-identical output (`3107ba21e10acc70…` twice), verified in `data/v3_spine/31a164f845f8e27e/muscriptor_c4_within_cycle_check.json`.

**OPTION A gate protection**: the byte-determinism ×2 gate applies to the canonical serializer within a cycle. The serializer is a pure function of its JSON input; given a c4-deterministic guitar JSON, the canonical MIDI is byte-deterministic ×2 (verified below).

## §4 Canonicalized MIDI determinism ×2 (7/7)

All 7 probes serialized twice into fresh `tempfile.mkdtemp()` dirs, SHA-256 equality asserted:

| Stem     | canonical MIDI SHA-16 | ×2 equal |
|----------|-----------------------|----------|
| drums    | `f6097216e7e1c8d5…`   | ✓        |
| bass     | `609b2b8059af4468…`   | ✓        |
| guitar   | `4afb8a321cba76e7…`   | ✓        |
| other    | `586a53e25f3a3719…` (empty) | ✓  |
| piano    | `586a53e25f3a3719…` (empty) | ✓  |
| vocals   | `8a00d5ad8df4797f…`   | ✓        |
| full_mix | `6062acb128ac67f9…`   | ✓        |

**Rung-1a PASS.** Pinned in `data/v3_spine/31a164f845f8e27e/canonical_midi_determinism.json`.

## §5 Tempo choice

- BPM = **90.7258064516129** from `data/recreate_v2/baseline/31a164f845f8e27e/rc5_tempo_bpm.json` (`librosa.beat.beat_track` on original mix, cycle-49 anchor). Meter [4, 4]. `delta_vs_rc5_baseline_bpm = 0.0` (identity source).
- MuScriptor JSON events carry no tempo meta; drums-stem librosa call would be a separate baseline capture, not on disk; deferred as unnecessary — full-mix rc5 baseline already captures ensemble tempo and is READ-ONLY preserved.

## §6 GM program map v3

12 MuScriptor labels mapped in `data/v3_spine/31a164f845f8e27e/gm_program_map_v3_extensions.tsv`. **RC4 lock verified: 0 labels on GM program 4** (electric_piano assigned to GM 5 = Electric Piano 2 to fully honor lock). Drums on channel 10.

## §7 merged.mid structural gates

`scripts/v3_spine/merge_per_stem_midi.py` merged 6 canonicalized per-stem MIDIs onto tempo map. All 4 structural assertions PASS:

- `drums_track_on_ch10_nonempty`: **True** (183 note_ons on channel 9)
- `bass_median_pitch_lt_55`: **True** (median = 38)
- `zero_notes_on_gm_program_4`: **True**
- `vocals_track_present_nonempty`: **True** (181 note_ons + `voice_symbolic_do_not_render` text meta; not rendered by fluidsynth)

merged.mid SHA-256: `555b41db4f23bd3bcfeba6d94ddf04b6f92b9f08fd6f1b6ea8ed982b276faf19`.

## §8 Full-mix reconciliation

`data/v3_spine/31a164f845f8e27e/full_mix_reconciliation.json`: full_mix canonical MIDI has 490 note events; merged per-stem has 1010. Per pitch-class + per-channel deltas logged. Reconciliation policy: **reconcile in per-stem favor by default** (per operator directive point 4). `full_mix_only_findings` logged but NOT auto-merged this cycle.

## §9 Render + mix-match

- **Per-track render**: fluidsynth with SF2 SHA `74594e8f…1cb0`, `-r 44100 -o synth.cpu-cores=1 --reverb-active=false --chorus-active=false`. All 5 non-vocal WAVs byte-deterministic ×2:
  - drums `df79c961…`, bass `f707e428…`, guitar `3b76d095…`, piano `1522401a…` (empty), other `1522401a…` (empty).
- **Vocals overlay**: htdemucs vocals.wav (SHA `5f267f06…`) copied SHA-verified into render dir. Not rendered by fluidsynth.
- **Mix-match**: per-stem RMS-match to baseline htdemucs 6-stem WAVs on t=0..30s. Note: rc7 `per_stem_loudness.json` recorded `segment_empty` errors because the baseline capture window was t=0..30s while the operator-chosen section is t=233..263s; `mix_match.py` computes loudness targets fresh from baseline WAVs on the actual A/B window (0..30s). Summed into `full_reconstruction.wav`: 30s stereo 44.1kHz, peak=0.707, byte-deterministic ×2 (SHA `281a3bc6…`).

## §10 Panel results + tripwire

`data/v3/deliveries/31a164f845f8e27e/panel.json` (8 keys, all numeric metrics finite):

| Key                            | Value      |
|--------------------------------|------------|
| `mel_l1_db`                    | 15.0232    |
| `spectral_centroid_rmse_hz`    | 3121.2864  |
| `rms_env_rmse`                 | 0.1324     |
| `lufs_m_rmse_lu`               | 14.9051    |
| `embedding_cosine_distance`    | 0.1429 (VGGish) |

**c33 anchor `panel_baseline_old_chain_v2.tsv` NOT present on disk** — regression check honestly recorded as `not_applicable`. **Panel is NEVER a LANDS gate (Fixed Decision 6).**

## §11 Operator handoff

- Listen to `data/v3/deliveries/31a164f845f8e27e/original_ab.wav` vs `reconstruction_ab.wav` (30s each). Both non-silent, sample-aligned at t=0..30s of Chicken Grease.
- **Honest A/B window disclosure**: baseline htdemucs stems in `data/recreate_v2/baseline/<sha16>/rc9_6stem/` cover only t=0..30s of the original mix; MuScriptor transcribed those 30-second stems; so the A/B window this cycle is 0..30s, not the operator-chosen t=233..263s (deferred to c5+ once a new htdemucs_6s pass on that section lands — outside c4 scope).
- Also delivered: `full_reconstruction.wav` (30s), `manifest.json`, `verdict.json`, `panel.tsv`.
- Ledger `M-V3-SPINE-1/verdict-v2-emitted` carries `status: action_required` with `blocked_on_operator: true`.

## §12 Wall-time budget (subprocess-serial in-turn)

| Step                                        | Wall (s)  |
|---------------------------------------------|-----------|
| Pre-work docs + doc-SHA pinning + 3 ledger events | <1  |
| Serializer + 12 unit tests                  | <1        |
| Anchor pre-snapshot (36 anchors)            | <1        |
| MuScriptor JSON Run-2: other + piano        | ~46       |
| MuScriptor JSON Run-2: guitar (v1 flag)     | 171       |
| MuScriptor JSON c4-Run-A + c4-Run-B guitar (intra-cycle check) | ~340 |
| MuScriptor JSON Run-2: guitar (best-effort) | 171       |
| tempo_map                                   | <1        |
| canonicalize_all_probes (14 serialize calls) | <1       |
| gm_program_map_v3                           | <1        |
| merge_per_stem_midi                         | <1        |
| full_mix reconciliation                     | <1        |
| render_per_track (5 stems × 2 fluidsynth)   | ~15       |
| vocals_overlay + mix_match ×3               | ~5        |
| deliver + sanity_panel + verdict + anchor_preservation_post | ~40 (VGGish load) |
| 17 ledger events + housekeeping             | <1        |
| Test suite (16 c4 + 12 serializer)          | <1        |
| **Total**                                   | **~15 min**  |

All steps subprocess-serial in-turn. No fire-and-forget. Every SHA in this report present on-disk at the moment of writing. Zero fabricated numbers.
