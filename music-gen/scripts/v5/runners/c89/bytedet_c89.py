"""Assemble data/v5/gen/byte_determinism_c89.json entries from the on-disk x2 records (post-edit image) and fold the independent-process +
F5-off clauses into f5_enum_final; stamp the verdict into the stall-counter F5 history entry."""
import hashlib, json, os, time
from pathlib import Path
W = Path('/home/user/long-exposure-runs/music-gen'); os.chdir(W)
S = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
now = lambda: time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
BD = Path('data/v5/gen/byte_determinism_c89.json')
bd = json.loads(BD.read_text())
ent = bd.get('entries') or {}
post = sha('scripts/v5/generate_v5.py')
fo = json.loads((S / 'flagoff_c89.json').read_text())
ind = json.loads((S / 'indep_c89.json').read_text())
assert fo['generate_v5_sha256'] == post == ind['generate_v5_sha256'], 'generator image changed after the x2 / flag-off runs'
ent['iteration_04_flag_off_replay'] = {**fo['runs']['iteration_04'], 'checked_utc': fo['checked_utc'], 'generate_v5_sha256': post,
                                       'note': 'POST-EDIT c89 generate_v5.py (F5 code present, --f5 absent; --prove-replay omitted — result-neutral) reproduces the 5 c88 iteration-4 ab_mix.wav SHAs'}
roll = json.loads(Path('data/v5/gen/iteration_05/iteration_rollup.json').read_text())
assert roll['generator_hash'] == post
per = {}
for s in roll['songs']:
    k = f"{s['generated_song_id']}_donor_{s['donor']}"
    pr = json.loads(Path(f'data/v5/gen/iteration_05/{k}/ab_mix.replay_proof.json').read_text())
    per[k] = {'run1_sha256': pr['run1_sha256'], 'run2_sha256': pr['run2_sha256'], 'equal': pr['verdict'] == 'REPLAY_PROOF_HOLDS', 'tempdir_run2': pr['run2_tempdir'],
              'on_disk_sha256': sha(f'data/v5/gen/iteration_05/{k}/ab_mix.wav'), 'duration_s': s['duration_s'], 'form': ''.join(s['form']), 'n_bars': s['n_bars'],
              'tempo_bpm': s['tempo_bpm'], 'tempo_source': s['tempo_source'], 'is_demo': 'f5' in s}
    if 'f5' in s:
        per[k]['f5'] = s['f5']
ent['iteration_05_renders'] = {'checked_utc': now(), 'command': json.loads(Path('data/v5/gen/f5_prereg_c89.json').read_text())['generator_flags']['iteration_5_command'],
                               'generate_v5_sha256': post, 'generate_v5_sha256_in_rollup': roll['generator_hash'], 'interpolate_v5_sha256': sha('scripts/v5/interpolate_v5.py'),
                               'repo_root_sha256': sha('scripts/v5/repo_root.py'), 'serializer_v5_sha256': sha('scripts/v5/midi_from_json_events_v5.py'),
                               'harmony_n23_sha256': roll['rules_sha256']['harmony_chain'], 'groove_n23_sha256': roll['rules_sha256']['groove_model'],
                               'per_song': per, 'n_equal': sum(v['equal'] for v in per.values()), 'n_songs': len(per), 'all_equal': all(v['equal'] for v in per.values()),
                               'f5_enum_pending_bytedet': roll['f5']['f5_enum_pending_bytedet'], 'tempo_overrides': roll['tempo_overrides']}
ent['iteration_05_independent_process'] = {**ind, 'note': 'the exact iteration-5 command re-run in a SEPARATE process into a fresh tempfile.mkdtemp(); ab_mix + per-stem MIDI + per-track SHAs compared for all 6 renders'}
r1 = 'data/v5/gen/gen_v5_iter05_ear_scores_c89.json'
r2 = sorted(Path('/tmp').glob('score_iter05_c89_run2_*/table.json'), key=lambda p: p.stat().st_mtime)
ent['iteration_05_ear_scores_table'] = {'checked_utc': now(), 'run1_sha256': sha(r1), 'run2_sha256': sha(r2[-1]) if r2 else None, 'equal': bool(r2) and sha(r1) == sha(r2[-1]),
                                        'tempdir_run2': str(r2[-1].parent) if r2 else None, 'informational_only': True}
demo_k = next(k for k, v in per.items() if v['is_demo'])
demo_bd = per[demo_k]['equal'] and ind['per_song'][demo_k]['equal']
regression = ent['iteration_04_flag_off_replay']['all_equal']
aud = roll['f5']['audibility_all']
if demo_bd and regression:
    final = 'F5_LANDS' if aud else 'F5_PARTIAL'
else:
    final = 'F5_FAILS'
bd.update({'entries': ent, 'post_edit_script_sha256': {'generate_v5': post, 'interpolate_v5': sha('scripts/v5/interpolate_v5.py'), 'repo_root': sha('scripts/v5/repo_root.py'),
                                                      'midi_from_json_events_v5': sha('scripts/v5/midi_from_json_events_v5.py'), 'comping_gen_v5': sha('scripts/v5/comping_gen_v5.py')},
           'f5_demo_dir': demo_k, 'f5_demo_byte_det_x2': {'in_process_replay': per[demo_k]['equal'], 'independent_process': ind['per_song'][demo_k]['equal']},
           'f5_flag_off_regression_5_of_5': regression, 'f5_audibility_all_clauses': aud, 'f5_audibility_clauses': roll['f5']['audibility_clauses'],
           'f5_enum_final': final,
           'f5_enum_rule': 'F5_LANDS iff demo byte-det x2 (in-process replay AND independent process) AND replay proof x2 AND iteration-4 flag-off 5/5 AND every raw-render audibility clause; F5_PARTIAL iff byte-det + regression pass but an audibility clause fails; else F5_FAILS (data/v5/gen/f5_prereg_c89.json)',
           'assembled_utc': now()})
BD.write_text(json.dumps(bd, sort_keys=True, indent=2) + '\n')
sc_p = Path('data/v5/gen/stall_counter.json')
sc = json.loads(sc_p.read_text())
h = sc['history'][-1]
assert h['iteration'] == 5 and 'f5' in h
h['f5']['verdict'] = final
h['f5']['flag_off_iteration_04_5_of_5'] = regression
h['f5']['independent_process_equal'] = ind['per_song'][demo_k]['equal']
sc_p.write_text(json.dumps(sc, indent=2) + '\n')
print(json.dumps({'post_edit': post[:16], 'iter5_x2_inproc': ent['iteration_05_renders']['n_equal'], 'indep': ind['n_equal'], 'flagoff_it4': fo['runs']['iteration_04']['n_equal'],
                  'ear_x2': ent['iteration_05_ear_scores_table']['equal'], 'audibility': roll['f5']['audibility_clauses'], 'f5_enum_final': final}))
