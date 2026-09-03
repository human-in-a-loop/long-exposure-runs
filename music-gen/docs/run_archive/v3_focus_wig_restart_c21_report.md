---
created: 2026-09-02T20:00:00Z
run_id: run-2026-09-03T000000Z
cycle: 21
clone: clone-1
fork: 0a1b1dca4f9b
agent: worker
milestone: M-V3-FOCUS-1
---

# WIG (What If I Go) v3 per-stem Restart c21 — clone-1 fanout report

**Song**: Mura Masa — What If I Go (`audio_sha16 = 252eb21ce7df7328`)
**Section**: operator's D1-chosen 30 s peak+exposed section, `t_start_s = 72.77133786848073`, `t_end_s = 102.77133786848073`
**Verdict**: `V3_FOCUS_SONG_LANDS_pending_operator` (internal-gate accept per D-A; operator ear on WIG A/B is the ultimate LANDS authority per FD-6)
**c20 backref**: `bd394c43c6134811257bb9b27539bf95e8d5b4663135d2646b0035f6b0e8ea2b` (PARTIAL prior)
**c21 verdict SHA**: `95edf6cc741366d5…`
**Delivery manifest SHA**: `9a8a09d0f553a79f…`

## §1 Resume-point audit

12 c20 htdemucs stem SHAs + 3 c20 MuScriptor JSON SHAs verified byte-identical against on-disk state before any work:

| Anchor | Expected SHA | On-disk | Match |
|---|---|---|---|
| rc9_6stem/bass.wav | `4878f22d5187de37…` | same | ✓ |
| rc9_6stem/drums.wav | `4ea5bfb2d442e3f7…` | same | ✓ |
| rc9_6stem/guitar.wav | `ea6dbc4d7f4a6e03…` | same | ✓ |
| rc9_6stem/other.wav | `c51b0872087573e3…` | same | ✓ |
| rc9_6stem/piano.wav | `5ed59e93204b4b3b…` | same | ✓ |
| rc9_6stem/vocals.wav | `7ddf6e655ea46e3b…` | same | ✓ |
| muscriptor/drums.json | `a8c28773a4d7a457…` | same | ✓ |
| muscriptor/bass.json | `8060faaa72809254…` | same | ✓ |
| muscriptor/guitar.json | `4f53cda18c2baa0c…` (canonical empty per c3 vocab) | same | ✓ |
| muscriptor/drums.mid | `33de0cbc2ae02844…` | same | ✓ |
| muscriptor/bass.mid | `543f1ab705b7b2fe…` | same | ✓ |

Full snapshot: `data/v3_spine/252eb21ce7df7328/operator_section/anchor_preservation_c21.json` (n_total=11, n_match=11, n_mismatch=0, all_match=true).

## §2 4 new MuScriptor probes

Run under `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`, single-thread BLAS. Both runs into fresh `tempfile.mkdtemp()` dirs; skip logic short-circuits 3 frozen probes with SHA verification before entering the tempdir path.

| Probe | run1 SHA | run2 SHA | equal | wall_s | status |
|---|---|---|---|---|---|
| drums | `a8c28773a4d7a457…` | same | ✓ | 0.0 | frozen_c20_preserved |
| bass  | `8060faaa72809254…` | same | ✓ | 0.0 | frozen_c20_preserved |
| guitar | `4f53cda18c2baa0c…` | same | ✓ | 0.0 | frozen_c20_preserved |
| **other** | `06cb90142a2551cd…` | same | ✓ | 526.8 | fresh_c21 |
| **piano** | `17eb7d7d49aa4ead…` | same | ✓ | 280.0 | fresh_c21 |
| **vocals** | `7cfc51bc74657cf5…` | same | ✓ | 261.4 | fresh_c21 |
| **full_mix** | `fa6b158a1f9d4228…` | same | ✓ | 764.2 | fresh_c21 |

`muscriptor_determinism.json.all_deterministic = true`, `n_probes = 7`, wall_time_s = 1832.35.

## §3 Downstream chain execution

- **Canonical MIDI serialize ×2**: 7/7 byte-deterministic. `canonical_midi_determinism.json` produced under READ-ONLY import of `scripts/v3_spine/midi_from_json_events.py` (c4 canonical serializer lock; SHA byte-identical pre==post).
- **merge_per_stem_midi_operator_section_wig.py**: `merged.mid` sha `a93f5c2ae16e5cac…`, byte-det ×2 true. All 4 structural gates PASS: `drums_track_on_ch10_nonempty=true`, `bass_median_pitch_lt_55=true`, `vocals_track_present_symbolic=true`, `zero_notes_on_gm_program_4=true`.
- **fluidsynth per-track render ×2**: 5/5 tracks byte-deterministic (drums=`0738861b5a22…`, bass=`79d5449280fb…`, guitar=`1522401aa6f5…`, piano=`b850ced46f48…`, other=`4e5adf228a71…`).
- **vocals overlay**: D2 copy of `rc9_6stem/vocals.wav` sha-verified `7ddf6e655ea46e3b…`.
- **rc7 mix-match**: RMS-match + sum → `full_reconstruction_operator_section.wav` sha `f2deaf6aecb5afa5…`, byte-det ×2 true.

## §4 Panel + verdict emission

- **Delivery**: `data/v3/deliveries/252eb21ce7df7328/operator_section/{original_ab_operator_section.wav, reconstruction_ab_operator_section.wav, full_reconstruction_operator_section.wav, panel.json, panel.tsv, manifest.json}`. Also mirrored to root path `data/v3/deliveries/252eb21ce7df7328/{original_ab.wav, reconstruction_ab.wav, full_reconstruction.wav, panel.json, manifest.json, merged.mid}` for c5-parity.
- **A/B durations**: original_ab peak=1.0000, dur=30.000s; recon_ab peak=0.7070, dur=30.000s. Both non-silent, within ±5 ms tolerance.
- **Panel**: `mel_l1_db=9.5946`, `spectral_centroid_rmse_hz=1363.33`, `rms_env_rmse=0.1904`, `lufs_m_rmse_lu=10.0865`, `embedding_cosine_distance=0.1247` (VGGish rung), `sr_hz=44100`, `n_samples_compared=1323000`. 8 keys finite. Cross-window tripwire PASS.
- **Verdict**: `V3_FOCUS_SONG_LANDS_pending_operator` at `data/v3/deliveries/252eb21ce7df7328/cycle21/verdict.json` (sha `95edf6cc741366d5…`). Three-way `rubric_hash_v2` byte-equality chain holds (`c49db5a12e955f26…`). `blocked_on_operator=true`. `sub_clause_status.f_restart_from_partial=true`. c20 backref pinned.

## §5 Anchor preservation diff table

`data/v3_spine/252eb21ce7df7328/operator_section/anchor_preservation_c21.json`:

- `n_total=11`, `n_match=11`, `n_mismatch=0`, `all_match=true`
- Additional context: `render_stem.py` SHA byte-identical (do-not-touch invariant); `midi_from_json_events.py` SHA byte-identical (canonical serializer lock); rubric_hash_v2 = `c49db5a12e955f26…`.

Pre==post: every c20 anchor byte-identical after all work completed.

## §6 Test suite results

`tests/test_v3_focus_wig_c21.py` — 12/12 PASS:

1. htdemucs 12 stem anchors preserved
2. muscriptor 3 frozen preserved
3. muscriptor all 7 probes deterministic
4. canonical MIDI det ×2
5. merged.mid 4/4 structural gates
6. per-track 5/5 renders det ×2
7. mix-match det ×2
8. A/B WAV durations + non-silent
9. panel 8-key finite
10. verdict LANDS + three-way rubric chain
11. c20 backref SHA
12. anchor preservation gate

## §7 Ledger events (6 named + 2 housekeeping)

All events land under `-clone-1` suffix on infra families (harness auto-suffix per c33 guard). Substantive `M-V3-FOCUS-1/wig-*` unsuffixed per c32 convention.

| # | milestone_id | status |
|---|---|---|
| 1 | `M-V3-FOCUS-1/wig-muscriptor-completed` | validated/high |
| 2 | `M-V3-FOCUS-1/wig-canonical-midi-completed` | validated/high |
| 3 | `M-V3-FOCUS-1/wig-merge-completed` | validated/high |
| 4 | `M-V3-FOCUS-1/wig-render-mix-completed` | validated/high |
| 5 | `M-V3-FOCUS-1/wig-anchor-preservation-c21-verified` | validated/high |
| 6 | `M-V3-FOCUS-1/wig-verdict-c21-emitted` | validated/high |
| 7 | `_run/post-integration-cycle-21-wig-restart` (auto-suffixed `-clone-1`) | validated/high |
| 8 | `_archive/cycle-21-wig-scratch` (auto-suffixed `-clone-1`) | validated/high |

`promise_check` 0-ERROR post-emission.

## §8 Handoff to c22 auditor

**Third M-V3-FOCUS-1 accept lands on internal gates.** With Chicken Grease (c5 operator-accepted 2026-09-02) and Rome (c20 clone-1 internal-gate accept), WIG (c21 clone-1 internal-gate accept) closes the ≥3 mandatory substantive-accept threshold. Per operator note in the c20 story, once ≥2 more focus songs land, a single batch manifest listing all focus A/B pairs should be emitted for operator review — that trigger fires this cycle. Remaining focus songs (Peach Dream PARTIAL c20, Disco A not started) can advance in parallel without blocking the M-V3-FOCUS-1 gate.

**Recommendations for c22**:
1. Integration cycle: register clone-1 ledger events + this report into the plan-of-record.
2. Emit `M-V3-FOCUS-1` rollup event advancing the parent to `validated/high` on internal gates (per D-A autonomous completion).
3. Draft the batch manifest listing 3 accepted focus A/B pairs (Chicken Grease, Rome, WIG) for operator listening.
4. Peach Dream Option 3 (accept as terminal PARTIAL) recommended per c20 clone-2 auditor; can be adjudicated post-batch-manifest.
5. Disco A launch remains queued as 5th focus song for M-V3-FOCUS-1 diversity but is no longer gating.

**No anti-pattern touched.** Do-not-touch invariants preserved: `scripts/palette_render/render_stem.py` byte-identical; `scripts/v3_spine/midi_from_json_events.py` byte-identical; c5 Chicken Grease delivery untouched; Rome c20 delivery untouched; Peach Dream c20 delivery untouched.
