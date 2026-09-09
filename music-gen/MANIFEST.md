# Music-Gen v4 closure campaign — MANIFEST

## Key Files

The following workspace files produced results cited in
final_report.md. Downstream packaging should include these; other
files are supporting or exploratory.

- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` — the
  Chicken Grease A/B showcase mix cited in §9.4 (SHA prefix
  `6e13e0075c5d8116…`, LUFS-I −15.32).
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.manifest.json` —
  inputs manifest for the showcase mix (§9.4).
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.replay_proof.json`
  — byte-identity replay proof for the showcase mix (§9.4).
- `scripts/sound_match/deliver_cg_ab_v4.py` — the delivery script
  whose smoke test reports every Chicken Grease cell terminal
  (§9.3, §9.4).
- `scripts/sound_match/pinned_profile_schema_v1.json` — the
  pinned-profile JSON schema validated as load-bearing for
  replay discipline (§9.3, §9.6).
- `scripts/sound_match/profile_validator.py` — validator for the
  pinned-profile schema (§9.3, §9.6).
- `scripts/sound_match/objective.py` — composite objective; the
  emission point named in the Path B remediation option for the
  metric-semantics escalation (§9.5, §10.3 item 1).
- `scripts/sound_match/embedding_panel.py` — embedding-cosine
  computation (`1 − cos(u, v)`) referenced in the same
  escalation (§9.5).
- `scripts/v4_rules/extract_v4.py` — the substantive v4-rules
  extractor whose audit-trail rows are the housekeeping gap
  named in §9.6 and §10.3 item 2.
- `scripts/v4_rules/__init__.py` — package init for the
  extractor above (§9.6).

Snapshot at on-disk cycle 86 close (harness cycle 130; counter offset 44,
disclosed). Scope: the v5 arc files produced or modified during on-disk
cycles 84–86 (harness 128–130). Earlier v4/v5 files are read-only anchors
and are listed only where a cycle-84–86 file consumes them. The "Key
Files" section above is preserved verbatim from the v4 close-out.

## Scripts (cycles 84–86)

### `scripts/v5/` — corpus, rules, generator

| file | lines | cycle | purpose |
|---|---|---|---|
| `restart_driver_c84.py` | 120 | 84 | verifies driver/hook SHAs + stage-cache env-pin key, relaunches the pinned c79 transcription command detached |
| `hook_at_birth_c84.py` | 76 | 84 | verifies every post-c83 landing carries a hook-at-birth reindex sidecar |
| `content_gate_v5.py` | 122 | 84 | pre-registered non-music content gate → `data/v5/corpus/content_blocked.json` |
| `content_blocked.py` | 45 | 84 | `ContentBlockedError` refusal shared by harmony/groove scripts |
| `groove_v5_full_c84.py` | 144 | 84 | full-corpus groove v2 with SHA-256 3-song hold-out fold |
| `harmony_v5.py` | 411 | 84–86 (additive) | full-corpus harmony Markov chain; `--eligible-from`, `--tempo-overrides`, `tempo_blocked_effective()` |
| `groove_v5_v2.py` | 338 | 84–86 (additive) | groove v2 conditionals; content refusal; tempo overrides; v5c dir preference |
| `groove_v5.py` | 217 | 84 (+4 lines) | content refusal wired in |
| `generate_v5.py` | 850 | 84–86 | groove-first generator: iteration 1 (AABA), `--form-plan` (F1), `--f2 / --velocity-mode / --rms-variance-test` (F2, default off) |
| `score_gen_batch_v5.py` | 154 | 85–86 | informational ear scoring; `--cycle` required |
| `deliver_v5_listening.py` | 71 | 85–86 | copies renders to `data/v4/generated/v5_iter_NN/`; `--cycle` required |
| `form_plan_v5.py` | 346 | 85 | F1 corpus form-plan model → `data/v5/rules/form_plan_v5.json` |
| `tempo_f4_adjudicate_c85.py` | 192 | 85 | pre-registered half/double-time check for PD + Disco A → `tempo_f4_verdict_c85.json` |
| `recanonicalize_tempo_v5.py` | 164 | 86 | re-serialises PD + Disco A at the operator-adopted BPM → `canonical_v5c_reindexed/` |
| `f2_route_gate_c86.py` | 93 | 86 | 10-minute F2 route decision (df, htdemucs import, WIG separation timing) |
| `velocity_v5.py` | 377 | 86 | Route-1 per-onset velocity extraction from stem audio + velocity profiles |
| `midi_from_json_events_v5.py` | 119 | 86 | sibling of the read-only c4 serializer that accepts velocities (byte-equal without them) |
| `bass_pitch_v5.py` | 385 | 86 | chord-conditioned bass pitch-class model → `bass_pitch_v5.json` |
| `melody_vomm_v5.py` | 352 | 86 | variable-order Markov melody model over scale degree × IOI → `melody_vomm_v5.json` |

### `data/v5/rules/` (executable wrappers co-located with data)

| file | lines | cycle | purpose |
|---|---|---|---|
| `groove_v5_full_c86.py` | — | 86 | n=23 groove re-run importing the c84 fold read-only |
| `plot_harmony_full_c84.py`, `plot_groove_v2_full_c84.py`, `plot_form_plan_corpus_c85.py`, `plot_harmony_n23_vs_n21_c86.py`, `plot_velocity_profiles_c86.py` | — | 84–86 | figure scripts (each takes `--out`) |

Also: `data/v5/corpus/plot_tempo_f4_c85.py`, `data/v5/gen/iteration_02/plot_iter02_arrangement_c85.py`, `data/v5/gen/iteration_03/plot_iter03_velocity_c86.py` (figure not yet produced).

### `tools/`

| file | lines | cycle | purpose |
|---|---|---|---|
| `_emit_c84_ledger_events.py` / `_register_c84_por_rows.py` | 289 / 73 | 84 | cycle-84 ledger + plan registration (run) |
| `_emit_c85_ledger_events.py` / `_register_c85_por_rows.py` | 234 / 58 | 85 | cycle-85 ledger + plan registration (run) |
| `_emit_c86_ledger_events.py` / `_register_c86_por_rows.py` | 340 / 72 | 86 | cycle-86 ledger + plan registration (NOT yet run; dedupe key fixed by the auditor) |
| `_launch_velocity_c86.py` | 29 | 86 | detached launcher for `velocity_v5.py` |

## Tests (cycles 84–86)

| file | tests | status at c86 close |
|---|---|---|
| `tests/test_c84_landing.py` | 8 | 7/8 — `test_02` pins the pre-amendment blocked-file SHA (re-pin owed) |
| `tests/test_c85_landing.py` | 10 | 8/10 — `test_01`, `test_08` pin the pre-F4-close state (re-pin owed) |
| `tests/test_c85_f4_m5.py` | 5 | 5/5 (`test_01` re-pinned to the stale copy) |
| `tests/test_c86_f4_close.py` | 6 | 6/6 |
| `tests/test_c86_f2_models.py` | 5 | 5/5 |
| `tests/test_c86_landing.py` | 10 | 3/10 — 7 wait on iteration-3 artifacts or stamp/guard fixes |

Adopted-suite regression at c84 close: 93/93 across 16 files (pre-existing historical failures elsewhere in `tests/` are not counted).

## Data artefacts (cycles 84–86)

- `data/v5/corpus/content_blocked.json`, `content_gate_prereg_c84.json` — content gate (1 song blocked).
- `data/v5/corpus/<sha16>/canonical_v5_reindexed/` + sidecars — 26/26 lossless full-length transcriptions.
- `data/v5/rules/eligible_c84.json`, `harmony_prereg_c84.json`, `harmony_markov_v5_full.json` (n=21), `per_song_c84/`, `groove_prereg_c84.json`, `groove_v5_v2_full.json`.
- `data/v5/gen/iteration_01/`, `iteration_02/` (5 renders + replay proofs + rollup each), `gen_v5_iter01_ear_scores_c84.json`, `gen_v5_iter02_ear_scores_c85.json`, `stall_counter.json` (2/12), `form_prereg_c85.json`, `data/v5/rules/form_plan_v5.json`.
- `data/v5/corpus/tempo_f4_prereg_c85.json`, `tempo_f4_verdict_c85.json` (AMBIGUOUS), `tempo_f4_operator_resolution_c86.json`, `tempo_overrides_c86.json`, `recanonicalization_blocked.json` (amended; pre-amend copy under `stale/`), `<PD|DiscoA>/canonical_v5c_reindexed/`.
- `data/v5/rules/eligible_c86.json`, `harmony_prereg_c86.json`, `harmony_markov_v5_full_c86.json` (n=23), `per_song_c86/`, `groove_prereg_c86.json`, `groove_v5_v2_full_c86.json`, `harmony_n23_vs_n21_diff_c86.json`.
- `data/v5/gen/f2_prereg_c86.json`, `f2_route_gate_c86.json`; `data/v5/corpus/<5 focus songs>/velocity_v5/velocities.json` + `canonical_v5_velocity/`; `data/v5/rules/velocity_profiles_v5.json`, `bass_pitch_v5.json`, `melody_vomm_v5.json`.
- Byte-determinism records: `data/v5/{gen,rules,corpus}/byte_determinism_c85.json`, `data/v5/corpus/byte_determinism_c86.json`, `data/v5/rules/byte_determinism_c86_f4.json`, `byte_determinism_c86_f2models.json`.
- Listening copies: `data/v4/generated/v5_iter_01/`, `v5_iter_02/` (5 WAVs each).

## Cumulative stats (cycles 84–86)

- New or extended scripts: 20 under `scripts/v5/` + 9 plot/wrapper scripts under `data/v5/` + 7 under `tools/`; ~6,100 lines added across the range.
- New tests: 6 files, 44 test functions.
- Figures: 6 committed with `--out` plot scripts (harmony n=21, groove n=21, form-plan corpus, iteration-2 arrangement, F4 tempo, harmony n=23 vs n=21); velocity-profile and iteration-3 figures pending.
- Ledger: 47 events (c84 32, c85 15); c86 events not yet emitted.

## Cross-references

- `eligible_c84.json` (n=21) → `harmony_markov_v5_full.json` + `groove_v5_v2_full.json` → `generate_v5.py` iterations 1–3, `form_plan_v5.py`, `bass_pitch_v5.py`, `melody_vomm_v5.py`.
- `tempo_f4_operator_resolution_c86.json` → `tempo_overrides_c86.json` → `recanonicalize_tempo_v5.py` → `canonical_v5c_reindexed/` → `eligible_c86.json` (n=23) → `harmony_markov_v5_full_c86.json` / `groove_v5_v2_full_c86.json` (consumed from iteration 4).
- `f2_route_gate_c86.json` → `velocity_v5.py` → `velocities.json` ×5 → `velocity_profiles_v5.json` → `generate_v5.py --f2` (iteration 3, pending).
- `recanonicalization_blocked.json` `blocked_songs` (kept) → `generate_v5.donor_tempo` frozen c22 anchors for PD/Disco A through iteration 3.
- Env pin `2ac444c36298d6ad…922ca` unchanged on every c84–c86 artefact.
