---
created: 2026-09-02T22:00:00Z
cycle: 20
run_id: run-2026-09-02T210000Z
agent: worker
milestone: M-V3-FOCUS-1
---

# c20 Rome (Dojo Cuts — sha16 51e433ade2a845e1) — v3 per-stem chain end-to-end

Fanout clone-1 of fork 88d75f9754c3. Sibling of the c5 Chicken Grease
Method A chain: htdemucs_6s → MuScriptor per-stem whitelist → canonical
MIDI → per-stem merge (4/4 gates) → tempo choice (librosa on chosen-section
drums) → fluidsynth per-track → D2 vocals overlay from SHA-verified
htdemucs vocals → rc7 mix-match (plain RMS-match, c5 Method A pattern)
→ 30 s A/B deliverables + full-mix reconstruction WAV + manifest.

## Chosen section (D1 auto-pick, focus_set_v2.json)

- `t_start_s = 62.74031746031746`
- `t_end_s = 92.74031746031747`
- `duration_s = 30.0`
- `combined_score = 1.474` (rms_score 2.43, onset_density 0.517, w=0.5/0.5)

## Discipline

- All discipline gates from v3 prompt.md apply verbatim.
- FD-1: no tuning, no retry on nondeterminism.
- FD-6: operator ear is the ONLY LANDS authority. Panel is NEVER a
  LANDS gate — it fires ONLY as a tripwire ≥2× regression vs c33 rc7
  anchor.
- Byte-determinism × 2 REQUIRED across all deterministic artifacts:
  6 stems × 2 (section + full) = 24 stem SHAs; 7 MuScriptor probes ×
  {json,mid}; 6 canonical MIDIs; 5 per-track WAVs; full-mix WAV.
- Rubric_hash_v2 three-way byte-equality chain: `docs/v3_spine_rubric_v2.md`
  SHA `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a`
  = `data/v3_spine/rubric_hash_v2.txt` = `verdict.rubric_hash_v2`.
- READ-ONLY imports of c5 sibling scripts (`mix_match_operator_section.py`,
  `rc7_v2_rerun_v3_paths.py`) — SHAs byte-identical pre==post.
- `render_stem.py` SHA `214372d9…5b2b` unchanged.

## Deliverables

Under `data/v3/deliveries/51e433ade2a845e1/`:

- `original_ab.wav` — 30 s original chosen-section slice
- `reconstruction_ab.wav` — 30 s reconstructed chosen-section
- `full_reconstruction.wav` — full v3 reconstruction
- `stems_6s/` — 6 htdemucs_6s stems (section)
- `stems_6s_full_song/` — 6 htdemucs_6s stems (full)
- `per_track/` — 5 fluidsynth per-track renders
- `muscriptor_operator_section/` — 7 JSON + 7 MID pairs
- `merged.mid` — merged canonical MIDI
- `tempo_choice.json` — 151.999 BPM, meter 4/4
- `mix_match_operator_section.json` — RMS-match log
- `rc7_per_stem_loudness_operator_section.json` — fresh per-stem loudness
- `panel.json` + `panel.tsv` — 8-key texture panel (NOT a LANDS gate)
- `manifest.json` — full delivery inventory
- `cycle20/verdict.json` — c20 verdict (V3_FOCUS_SONG_LANDS_pending_operator
  / PARTIAL / FAILS)

## Tests

`tests/test_v3_focus_rome_c20.py` — 12 cases covering htdemucs section +
full byte-det, MuScriptor byte-det (7 probes), canonical MIDI byte-det,
per-track + full-reconstruction WAV byte-det, structural gates on
merged.mid, mido==1.3.3 pin, vocals symbolic track, A/B 30 s ±5 ms,
panel 8-key finite, rubric_hash_v2 chain + c19 backref, verdict shape +
no-PRNG hygiene grep across all Rome sibling scripts.

## Ledger events (strict order, 8 events per brief)

Under `run_id=run-2026-09-02T210000Z`, per c32 fanout-namespace
convention (`_infra/*`, `_plan/*`, `_archive/*` suffixed `-clone-1`;
substantive `M-*` unsuffixed):

1. `M-V3-FOCUS-1/rome-htdemucs-section-completed` — validated
2. `M-V3-FOCUS-1/rome-htdemucs-full-song-completed` — validated
3. `M-V3-FOCUS-1/rome-muscriptor-completed` — validated
4. `M-V3-FOCUS-1/rome-verdict-emitted` — action_required
5. `M-INGEST-1/egress-probe-cycle20-clone-1` — validated (HTTP 429 + tv_embedded, unchanged)
6. `_plan/register-c20-v3-focus-rome-sub-leaves-clone-1` — validated
7. `_infra/adopt-cycle20-rome-tests-clone-1` — validated
8. `_archive/cycle-20-rome-scratch-clone-1` — validated

## Merge report

`/home/user/music-gen-instance-v3/fork-88d75f9754c3/clone-1/merge_report.md`
— written for root conductor.
