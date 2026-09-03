# Refactor inventory — 2026-09-03

Disposition of every scripts/ dir, major data/ dir, and workspace item.
DELETE = removed from working tree, recoverable from git history at the
commit noted in the log; REGEN = additionally regenerable by re-running a
named deterministic command. KEEP = untouched. ARCHIVE = moved, not deleted.

## scripts/ (48 dirs → ~20)

| dir | disposition | reason / successor |
|---|---|---|
| v3_spine | KEEP | core: unified + checkpointed drivers, palette_render, merge, verdicts |
| recreate_v2 | KEEP | proven modules: rc1 hybrid, rc4 GM map, rc5 grid, rc6 panel, rc7 mix, rc8 section, rc9 6-stem, rc10 gold set |
| separation | KEEP | htdemucs driver (system demucs binary) |
| ingest | KEEP | corpus ingest/receipts (feature) |
| score / score_bridge_v2 | KEEP | MusicXML/score export (feature; bridge_v2 is current) |
| v3_rules | KEEP | current rules milestone (deterministic extractor spec era) |
| rules_rated_corpus | KEEP | latest data-backed rules extraction |
| ear_v2p1 | KEEP | latest ear trainer (v2p1) |
| ear | KEEP | ear base package/defs |
| gen | KEEP | generation stage (feature) |
| palette | KEEP | palette base definitions |
| palette_render_v4 | KEEP | latest standalone palette renderer |
| dawdreamer_state | KEEP | DawDreamer state capture (palette dependency) |
| daw | KEEP | Ardour/daw integration (feature) |
| anchor_manifest | KEEP | anchor tooling (regenerate manifest post-refactor) |
| fanout_namespace_v3 | KEEP | engine ledger-namespace convention |
| analysis | KEEP | misc analysis utils (small) |
| heuristics | KEEP | shared heuristics utils (small) |
| vst3_nondeterminism | KEEP | evidence scripts for the Surge nondeterminism finding (cited by determinism certificate) |
| ear_v0, ear_v1, ear_v2, ear_sb3_fallback | DELETE | superseded by ear_v2p1 |
| palette_probe, palette_render, palette_render_cross_seed, palette_render_v3, palette_v2, palette_v2_render | DELETE | superseded by palette_render_v4 + v3_spine/palette_render |
| gen_palette_batch_v1, gen_palette_batch_v2, gen_palette_batch_rated_corpus | DELETE | superseded batch outputs' drivers; gen/ + driver replace |
| rules, rules_harmonic_window_v2 | DELETE | superseded by rules_rated_corpus + v3_rules |
| recreate_v0 | DELETE | dead v0 pipeline (re-created by a clone after the pivot deletion) |
| transcribe | DELETE | dead basic-pitch survey era (re-created by a clone) |
| rc2_rc3_run | DELETE | dead v0-era runner (re-created by a clone) |
| tex, texture | DELETE | RC7-condemned global effects wash era |
| classifier | DELETE | dead drum-classifier era (pre-MuScriptor) |
| breadth | DELETE | pre-pivot breadth planning one-offs |
| corpus_expansion_plan | DELETE | plan captured in docs; scripts stale |
| daw_spike | DELETE | spike superseded by daw + dawdreamer_state |
| deprecation_and_anchor_pin | DELETE | one-off migration, completed |
| egress_ready | DELETE | one-off egress probes, findings in docs |
| pre_reg_policy_verify | DELETE | one-off policy verification, completed |
| v3_reproduce_c23 | DELETE | one-off, superseded by checkpointed driver --no-cache |

## data/

| path | disposition | notes |
|---|---|---|
| v3/deliveries/*/ A/B + full_reconstruction + manifests + panels + MIDI | KEEP | operator-approved deliverables |
| v3/deliveries/*/per_track, stems_6s_full_song | DELETE/REGEN | regenerable by checkpointed driver / demucs; tombstoned |
| v3_spine/<song>/rc9_6stem (operator section) + muscriptor/*.json + merged.mid + tempo/env manifests | KEEP | references for the sound-matching layer |
| v3_spine/<song>/ render intermediates, full_song stems, duplicate run dirs | DELETE/REGEN | tombstoned |
| separation/ | DELETE/REGEN | v0-era separations, superseded by v3_spine stems |
| recreate_v2/ | DELETE/REGEN | v2-era baselines; anchor_manifest_v1 retired with it (regenerate for v4) |
| rc10_gold_set, ingestion, gen, ear_*, v3 (rest) | KEEP | |
| vst3_nondeterminism, daw_spike | KEEP JSON, DELETE WAV payloads | evidence stays, audio regenerable |

## workspace/ & environment

| item | disposition |
|---|---|
| learned_transcribers_venv, models/ (MuScriptor weights) | KEEP |
| _probe (137 MB) | DELETE |
| stray merge_report_*.md in workspace root | ARCHIVE → docs/run_archive |
| smoke_test.py, provision.sh, PROVISIONING_REPORT.md, MUSCRIPTOR_RECEIPTS.md, harvest_playlists.sh | KEEP |
| /home/user/music-gen-instance (24K stale) | DELETE |
| music-gen-instance-run1-archive | KEEP (history, 53 MB) |
| music-gen-instance-v3: exploration_state, sessions.db, latest log | KEEP; collapsed fork-* dirs + old resume logs DELETE |
| pip/uv caches | DELETE; torch-hub + huggingface caches KEEP (demucs/vggish weights) |

## docs/ — nothing deleted
Top level keeps operator/architecture/decision docs; ~200 run-generated
reports/rubrics move to docs/run_archive/; guidance snapshots to
docs/guidance/.
