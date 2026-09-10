#!/usr/bin/python3
"""c89 P0: (1) turn-start READ-ONLY pins -> data/v5/gen/byte_determinism_c89.json; (2) F5 pre-registration
data/v5/gen/f5_prereg_c89.json written BEFORE any F5 code edit or render output (mtime gate). Expected output counts are
computed from the deterministic form-plan draws (plan_form on the iteration-5 tags) so the count is exact before rendering."""
import hashlib, json, os, subprocess, sys, time
from pathlib import Path
W = Path('/home/user/long-exposure-runs/music-gen'); os.chdir(W); sys.path.insert(0, str(W))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
now = lambda: time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
assert not Path('data/v5/gen/iteration_05').exists(), 'iteration_05 must not exist before the prereg'
assert not Path('data/v5/gen/f5_prereg_c89.json').exists()
assert not Path('scripts/v5/interpolate_v5.py').exists() and not Path('scripts/v5/repo_root.py').exists()
PRE_GEN = sha('scripts/v5/generate_v5.py')
assert PRE_GEN.startswith('3d0f3a24c2b87ed9'), PRE_GEN
PINS = {
    'generate_v5_pre_edit': 'scripts/v5/generate_v5.py', 'comping_gen_v5': 'scripts/v5/comping_gen_v5.py', 'comping_v5_json': 'data/v5/rules/comping_v5.json',
    'harmony_n23_chain': 'data/v5/rules/harmony_markov_v5_full_c86.json', 'groove_n23_model': 'data/v5/rules/groove_v5_v2_full_c86.json',
    'form_plan_v5': 'data/v5/rules/form_plan_v5.json', 'velocity_profiles_v5': 'data/v5/rules/velocity_profiles_v5.json',
    'tempo_overrides_c86': 'data/v5/corpus/tempo_overrides_c86.json', 'bass_pitch_v5': 'data/v5/rules/bass_pitch_v5.json',
    'melody_vomm_v5': 'data/v5/rules/melody_vomm_v5.json', 'velocity_v5_script': 'scripts/v5/velocity_v5.py',
    'serializer_v5': 'scripts/v5/midi_from_json_events_v5.py', 'c4_serializer': 'scripts/v3_spine/midi_from_json_events.py',
    'replay_py': 'scripts/sound_match/replay.py', 'harmony_prereg_c86': 'data/v5/rules/harmony_prereg_c86.json',
    'groove_prereg_c86': 'data/v5/rules/groove_prereg_c86.json', 'cg_guitar_profile': 'data/v4/profiles/31a164f845f8e27e/guitar.json',
    'cg_bass_v2_profile': 'data/v4/profiles/31a164f845f8e27e/bass_v2.json', 'pd_bass_profile': 'data/v4/profiles/88d247468cb6d49f/bass.json',
    'pd_drums_profile': 'data/v4/profiles/88d247468cb6d49f/drums.json', 'donor_map': 'data/v4/gen/donor_profile_map.json',
    'recanonicalization_blocked': 'data/v5/corpus/recanonicalization_blocked.json', 'groove_v5_v2_script': 'scripts/v5/groove_v5_v2.py',
    'harmony_v5_script': 'scripts/v5/harmony_v5.py', 'f3_prereg_c88': 'data/v5/gen/f3_prereg_c88.json', 'form_prereg_c85': 'data/v5/gen/form_prereg_c85.json',
    'f2_prereg_c86': 'data/v5/gen/f2_prereg_c86.json', 'plan_of_record_at_open': 'plan_of_record.md', 'iteration_04_rollup': 'data/v5/gen/iteration_04/iteration_rollup.json',
    'stall_counter_at_open': 'data/v5/gen/stall_counter.json',
}
pins = {k: {'path': p, 'sha256': sha(p)} for k, p in PINS.items()}
EXPECT = {'generate_v5_pre_edit': '3d0f3a24c2b87ed9', 'comping_gen_v5': '571cc0a4', 'comping_v5_json': '01024254', 'harmony_n23_chain': '330b9d46', 'groove_n23_model': '57072025',
          'form_plan_v5': 'd6c14f9a', 'velocity_profiles_v5': '6b2fc502', 'tempo_overrides_c86': 'ef52f2a0', 'bass_pitch_v5': '96d34b3b', 'melody_vomm_v5': '48157c6f',
          'velocity_v5_script': 'dd94336d', 'serializer_v5': '4ea85e0b', 'harmony_prereg_c86': 'b32cf397', 'groove_prereg_c86': '995acc5b', 'recanonicalization_blocked': 'eb78cfc0'}
for k, pre in EXPECT.items():
    assert pins[k]['sha256'].startswith(pre), (k, pins[k]['sha256'][:16], pre)
roll4 = json.loads(Path('data/v5/gen/iteration_04/iteration_rollup.json').read_text())
anchors4 = {f"{s['generated_song_id']}_donor_{s['donor']}": s['ab_mix_sha256'] for s in roll4['songs']}
df = subprocess.run(['df', '-P', '.'], capture_output=True, text=True).stdout.strip().splitlines()[-1].split()
bd = {'schema_version': 1, 'cycle': 89, 'harness_cycle': 133, 'agent': 'worker', 'run_id': 'run-2026-09-06T000000Z',
      'env_pin_sha256': '2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca', 'turn_start_utc': now(),
      'df_at_open_after_prune': {'used_pct': int(df[4].rstrip('%')), 'avail_gb': round(int(df[3]) / 1e6, 3)},
      'turn_start_pins': pins, 'iteration_04_anchor_sha256': anchors4, 'entries': {},
      'note': 'turn-start READ-ONLY pins (c88 shape); entries filled by the c89 pipeline (iteration-5 x2 in-process replay, independent second process, iteration-4 flag-off regression, scores table x2); f5_enum_final folded in by bytedet_c89.py'}
Path('data/v5/gen/byte_determinism_c89.json').write_text(json.dumps(bd, sort_keys=True, indent=2) + '\n')

# ---- expected outputs: deterministic form-plan draws on the iteration-5 tags (plan_form is a pure function of the tag)
os.environ['SUPPRESS_INTERPRETER_GUARD'] = '1'
from scripts.v5.generate_v5 import plan_form  # READ-ONLY use; the import has no output side effects
fp = json.loads(Path('data/v5/rules/form_plan_v5.json').read_text())
donors = json.loads(Path('data/v4/gen/donor_profile_map.json').read_text())['songs']
A, B, T, SEED = '31a164f845f8e27e', '88d247468cb6d49f', 0.5, 4
DEMO_ID = 'gen_v5_interp_CG_PD_t050'
song_dirs = {}
for s in donors:
    gid = s['generated_song_id'].replace('gen_v4_', 'gen_v5_')
    tag = f"{gid}|donor={s['donor_song_sha16']}|seed={SEED}"
    pl = plan_form(fp, tag)
    song_dirs[f"{gid}_donor_{s['donor_song_sha16']}"] = {'n_sections': pl['n_sections'], 'labels': pl['labels'], 'files': 25 + 2 * pl['n_sections']}
tag_demo = f"{DEMO_ID}|donor={A}|seed={SEED}"
pl = plan_form(fp, tag_demo)
song_dirs[f"{DEMO_ID}_donor_{A}"] = {'n_sections': pl['n_sections'], 'labels': pl['labels'], 'files': 25 + 2 * pl['n_sections'] + 1, 'extra': 'f5_blend.json'}
n_dir = sum(v['files'] for v in song_dirs.values()) + 1  # + iteration_rollup.json
expected_outputs = {
    'per_song_file_formula': '25 + 2*n_sections (ab_mix.wav, ab_mix.manifest.json, ab_mix.replay_proof.json, ear_score_v5.json, generated_json/{7 stems + n_sections sections}, generated_midi/{7 stems + sections/n_sections}, per_track/{7 prog_forced.mid}); the demo dir adds f5_blend.json',
    'song_dirs': song_dirs, 'iteration_05_dir_total': n_dir,
    'outside_iteration_05': ['data/v5/gen/plot_iter05_parts_c89.py', 'data/v5/gen/fig_iter05_parts_c89.png', 'data/v5/gen/byte_determinism_c89.json (turn-start pins written with this prereg; entries filled later)',
                             'data/v5/gen/gen_v5_iter05_ear_scores_c89.json', 'data/v4/generated/v5_iter_05/ (6 listening copies + listening_manifest.json)',
                             'data/v4/generated/f5_interp_CG_PD_t050_c89/ (ab_mix.wav, ab_mix.manifest.json, ab_mix.replay_proof.json, f5_blend.json, f5_prereg_c89.json copy, delivery_manifest.json)'],
    'count_with_figure': n_dir + 2, 'note': 'c88 MINOR 7 closed: the figure + plot script are counted (iteration_05_dir_total + 2); the stale byte-det/score tables live outside the counted dir'}
prereg = {
    'schema_version': 1, 'kind': 'pre_registration_written_before_any_F5_code_edit_or_render_output', 'feature': 'F5', 'cycle': 89, 'harness_cycle': 133,
    'iteration': 5, 'seed': SEED, 'created': now(), 'ts': now(), 'agent': 'worker', 'run_id': 'run-2026-09-06T000000Z', 'milestone': 'M-V5-GEN-1/F5-interpolation-demo',
    'env_pin_sha256': '2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca',
    'donors': {'A': {'song': 'CG', 'title': 'Chicken Grease', 'id': A}, 'B': {'song': 'PD', 'title': 'Peach Dream', 'id': B}}, 't': T,
    'demo_song_id': DEMO_ID, 'demo_dir': f'data/v5/gen/iteration_05/{DEMO_ID}_donor_{A}', 'demo_tag': tag_demo,
    'generator_pre_edit_sha256': PRE_GEN, 'generator_post_edit_sha256': 'recorded in byte_determinism_c89.json post_edit_script_sha256 + every iteration-5 manifest generator_hash (addendum; not known before the edit)',
    'new_module': {'path': 'scripts/v5/interpolate_v5.py', 'imported': 'only under --f5 (generate_v5.main)', 'sha256': 'recorded in the addendum'},
    'repo_root_helper': {'path': 'scripts/v5/repo_root.py', 'purpose': 'c88 MINOR (b): repo_root(start) walks up to the promise_ledger.jsonl + scripts/v5 marker; the c89 plot script must use it (no parents[N] literal)'},
    'blend_semantics': {
        'no_note_level_mean': 'NO arithmetic mean of two rendered note streams or of two sampled chord/groove sequences is performed anywhere (c78 ban, FD-1); blending happens ONLY at model-parameter level, then ONE sequence is sampled from the blended model',
        'donor_conditioning_source': {
            'definition': 'a donor-conditioned distribution = the n=23 model construction (same alphabet, phase alignment, alpha=0.5 smoothing, template matching, exclusion rule, functional states relative to the donor KK tonic) applied to that donor\'s OWN lossless canonical MIDI (the per-song factor of the n=23 model), obtained by READ-ONLY import of scripts/v5/groove_v5_v2.load_song/table and scripts/v5/harmony_v5.analyse_song',
            'A_midi': 'data/v5/corpus/31a164f845f8e27e/canonical_v5_reindexed/ at bpm_v5 92.285156', 'B_midi': 'data/v5/corpus/88d247468cb6d49f/canonical_v5c_reindexed/ at the adopted 122.197271 (tempo_overrides_c86.json; load_song/analyse_song assert the v5c dir)'},
        'groove': {'model': 'blend of the four conditional tables kick_marginal, snare16|kick8, hat16|kick8+snare16, bass16|kick8',
                   'rule': 'P_mix(o|c) = t*P_A(o|c) + (1-t)*P_B(o|c) over the UNION outcome vocabulary of the two donor tables; P_X(o|c) = the donor table row (alpha=0.5-smoothed over the donor vocab) when context c is seen in donor X, else uniform over the donor X vocab (groove_v5_v2.row_for convention); an outcome absent from a donor vocab contributes 0 from that donor; contexts seen in NEITHER donor fall back to uniform over the union vocab (the generator\'s existing row_for path)',
                   'sampling': 'identical to iteration 4: scripts.v5.groove_v5_v2.draw (inverse-CDF in sorted-key order) on u = SHA-256 of the same per-bar tags generate_v5.sample_bar already uses; no PRNG',
                   'n23_corpus_tables_role': 'NOT consulted for the demo groove (the demo is the donor pair); they remain the model for the 5 regular iteration-5 songs'},
        'harmony': {'model': 'blend of segment-level transition rows + start distribution over the n=23 chain state set (81 functional states); donor states are asserted to be a subset',
                    'rule': 'for state s: n_X(s) = donor X segment count leaving s; P_X(s,.) = row-normalised donor X segment transitions if n_X(s) > 0 else the n=23 chain segment row (backoff, disclosed per state); row_mix(s) = t*P_A + (1-t)*P_B; the blended chain stores segment_level_counts[s] = n_mix(s) * row_mix(s) with n_mix(s) = t*n_A(s) + (1-t)*n_B(s), so generate_v5.seg_matrix recovers row_mix and the F1 contrast rule (>= 8 segments) reads the blended support; start/stationary weights pi_mix = t*pi_A + (1-t)*pi_B where pi_X = donor X normalised segment-state frequencies; states with n_mix(s) = 0 keep the generator\'s uniform-row convention',
                    'decoding': 'the same SHA-256 inverse-CDF draw_from as every other v5 chord draw (tags unchanged: <tag>|chord<i>|from=<state>); DEVIATION from the brief\'s recommended argmax-with-tiebreak decoder, declared here: argmax decoding of a Markov chain collapses to a fixed 1-2 state cycle and would not be a chord progression; the prereg (not the brief) governs',
                    'tonic_mode': 'donor A (CG, F# minor) — states are functional (relative to tonic) so the blend is key-independent; a tonic cannot be averaged'},
        'model_parameter_fallback': 'c78 per-position SHA-256 selection would be declared here for any model where parameter blending is ill-defined; NOT needed: both models blend at parameter level as above'},
    'demo_render_policy': {'form': 'F1 form plan drawn with the demo tag (plan_form); labels generated once, repeated literally; contrast rule + arrangement as iteration 4',
                           'tempo': 'donor A tempo via donor_tempo (tempo_v5.bpm_v5 = 92.285156; CG has no override entry) — tempi are NOT averaged', 'tonic': 'donor A KK key (F# minor) from the n=23 chain per_song',
                           'profiles': 'donor A: bass_v2.json (pinned), drums GM Standard Kit shim (CG OPT3), guitar.json pinned prog 28, piano/other GM shims 0/89 (F3 policy), keys/melody GM shims 4/11',
                           'f2_f3': 'the demo is a full iteration-5 render: --f2 velocity_mode f2 (bass pitch model, VOMM melody, velocity ladders) + --f3 comping over the BLENDED chord sequence; only the groove tables and the harmony chain are blended',
                           'regular_songs': 'the 5 regular iteration-5 songs (seed 4) use the UNBLENDED n=23 models exactly as iteration 4; the demo is appended as a 6th spec (generated_song_id gen_v5_interp_CG_PD_t050, donor_song_sha16 = A)'},
    'held_constant': {k: pins[k]['sha256'] for k in ('form_plan_v5', 'velocity_profiles_v5', 'comping_v5_json', 'comping_gen_v5', 'bass_pitch_v5', 'melody_vomm_v5', 'tempo_overrides_c86', 'velocity_v5_script', 'serializer_v5', 'c4_serializer', 'replay_py', 'harmony_n23_chain', 'groove_n23_model', 'donor_map', 'cg_bass_v2_profile', 'cg_guitar_profile', 'pd_bass_profile', 'pd_drums_profile')},
    'held_constant_env_pin': '2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca',
    'verdict_enum': {'F5_LANDS': 'demo byte-det x2 (in-process --prove-replay AND an independent second process into a fresh tempfile.mkdtemp) AND replay proof x2 passes AND flag-off regression 5/5 (iteration-4 command without --f5 under the post-edit image reproduces the 5 iteration-4 ab_mix SHAs) AND every audibility clause holds on the raw render',
                     'F5_PARTIAL': 'byte-det + regression pass but an audibility clause fails, or one replay proof fails on a non-determinism-related cause',
                     'F5_FAILS': 'byte-det or the flag-off regression fails', 'note': 'no fourth value; nothing retuned after seeing the renders (FD-1)'},
    'audibility_clause_raw_render': {
        'i_raw_rms': 'every demo stem (drums, bass, keys, melody, guitar, piano, other) has raw render RMS (pre-normalisation, measured on the per-track WAV before rms_norm) > -60 dBFS; recorded per stem in the manifest f5.raw_render_rms_dbfs',
        'ii_groove': 'd(t) = mean drum onsets per bar (popcount kick8 + snare16 + hat16) over the demo\'s composed bars (all sections, pre-arrangement); the same composition (same tags, same form plan) is re-run with the A-only (t=1) and B-only (t=0) blended tables; clause |d(0.5) - (0.5*d(1) + 0.5*d(0))| <= 2.0 onsets/bar; bass-kick lock reported informationally',
        'iii_harmony': 'h_A = Hamming fraction between the demo chord sequence and the A-only (t=1) sequence composed with the same tags; h_B likewise vs B-only; clause 0 < h_A < 1 AND 0 < h_B < 1 AND |h_A - h_B| <= 0.35 (the blend is distinct from both donors and not lopsided)',
        'tolerances_note': 'pre-declared; recorded in the manifest f5.audibility and the rollup; a failing clause -> F5_PARTIAL, never retuned', 'ear_score': 'informational only (FD-6, c76 L119)'},
    'expected_outputs': expected_outputs,
    'regression_targets': {'iteration_04_ab_mix_sha256': anchors4, 'command': 'the iteration-4 command from f3_prereg_c88.json generator_flags.iteration_4_command with --out <mkdtemp> --no-stall-update and WITHOUT --prove-replay (result-neutral), under the post-edit image'},
    'generator_flags': {'--f5': 'default OFF; store_true; zero change to any code path when absent', '--interp-a/--interp-b': 'donor A/B (short name CG/PD or sha16); argparse error without --f5', '--interp-t': 'blend weight t (float); argparse error without --f5',
                        '--f5-prereg': 'path pinned into rules_sha256 + manifests; argparse error without --f5',
                        'iteration_5_command': f'/usr/bin/python3 scripts/v5/generate_v5.py --iteration 5 --seed {SEED} --form-plan data/v5/rules/form_plan_v5.json --f2 --velocity-mode f2 --f3 --comping-model data/v5/rules/comping_v5.json --harmony data/v5/rules/harmony_markov_v5_full_c86.json --groove data/v5/rules/groove_v5_v2_full_c86.json --harmony-prereg data/v5/rules/harmony_prereg_c86.json --groove-prereg data/v5/rules/groove_prereg_c86.json --tempo-overrides data/v5/corpus/tempo_overrides_c86.json --f5 --interp-a CG --interp-b PD --interp-t {T} --f5-prereg data/v5/gen/f5_prereg_c89.json --prove-replay --cycle 89 --out data/v5/gen/iteration_05'},
    'stall': 'stall_counter 4/12 -> 5/12 with the F6 history entry {iteration 5, feature F5, donors CG/PD, t 0.5, form/harmony/groove/comping/prereg SHAs, verdict}',
    'mtime_gate': 'this file\'s mtime must precede every file under data/v5/gen/iteration_05/, scripts/v5/interpolate_v5.py, scripts/v5/repo_root.py and the post-edit generate_v5.py (tests/test_c89_landing.py asserts it)',
    'fd1': 'no weight, tolerance, tempo or program is changed after seeing the renders; a failing clause is recorded, not retuned; t = 0.5 fixed by the POR (no sweep)',
    'authority': {'por_row': 'M-V5-GEN-1/F5-interpolation-demo', 'backlog_guidance_sha16': sha('docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt')[:16],
                  'c131_guidance_sha16': sha('docs/guidance/guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt')[:16], 'c78_precedent': 'scripts/gen/interpolate_v4.py (per-position SHA-256 tiebreak fallback; arithmetic-mean fabrication BANNED)',
                  'c86_minor_7': 'discharged this cycle (own prereg)'},
}
Path('data/v5/gen/f5_prereg_c89.json').write_text(json.dumps(prereg, sort_keys=True, indent=2) + '\n')
print(json.dumps({'prereg_sha256': sha('data/v5/gen/f5_prereg_c89.json'), 'bytedet_sha256': sha('data/v5/gen/byte_determinism_c89.json'), 'df': bd['df_at_open_after_prune'],
                  'song_dirs': {k: (v['n_sections'], ''.join(v['labels'])) for k, v in song_dirs.items()}, 'iteration_05_dir_total': n_dir, 'count_with_figure': n_dir + 2}, indent=1))
