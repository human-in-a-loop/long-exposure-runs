#!/usr/bin/env python3
"""Pre-run anchor snapshot for c25 Peach Dream delivery.

Records ≥40 SHA-256 anchors covering: 6 c22+c23 read-only anchors, seeded
stems_6s (13 SHAs), c23 verdicts, c23 reproduce reports, c23 rules artifact,
c24 module SHAs, rubric hash chain files, focus_set_v2.
"""
from __future__ import annotations
import hashlib
import json
import pathlib


def sha(p):
    p = pathlib.Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def main() -> int:
    anchors = {}
    # 6 c22+c23 read-only anchors mandated by brief §Step 9
    anchors['scripts/v3_spine/recreate_v3.py'] = sha('scripts/v3_spine/recreate_v3.py')
    anchors['scripts/v3_spine/v3_pipeline/env_pin.py'] = sha('scripts/v3_spine/v3_pipeline/env_pin.py')
    anchors['scripts/v3_spine/midi_from_json_events.py'] = sha('scripts/v3_spine/midi_from_json_events.py')
    anchors['scripts/palette_render/render_stem.py'] = sha('scripts/palette_render/render_stem.py')
    anchors['data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav'] = sha(
        'data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav')
    anchors['data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json'] = sha(
        'data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json')

    # 12 seeded stems_6s SHAs (section.wav + 6 stems from c23 clone-1)
    seed = 'data/v3_spine/88d247468cb6d49f/operator_section_c23_unified'
    anchors[f'{seed}/section.wav'] = sha(f'{seed}/section.wav')
    for stem in ('drums', 'bass', 'other', 'vocals', 'guitar', 'piano'):
        anchors[f'{seed}/rc9_6stem/{stem}.wav'] = sha(f'{seed}/rc9_6stem/{stem}.wav')

    # c23 clone-1 verdict + related
    anchors['data/v3/deliveries/88d247468cb6d49f/cycle23/verdict.json'] = sha(
        'data/v3/deliveries/88d247468cb6d49f/cycle23/verdict.json')
    for song in ('31a164f845f8e27e', '51e433ade2a845e1'):
        p = f'data/v3/reproduce/c23/{song}/reproduce_report.json'
        anchors[p] = sha(p)

    # c23 clone-2 rules artifact
    anchors['data/v3/rules/rules_artifact.jsonl'] = sha('data/v3/rules/rules_artifact.jsonl')
    anchors['data/v3/rules/rubric_hash.txt'] = sha('data/v3/rules/rubric_hash.txt')

    # c24 modules
    anchors['scripts/v3_spine/stage_cache.py'] = sha('scripts/v3_spine/stage_cache.py')
    anchors['scripts/v3_spine/launch_detached.py'] = sha('scripts/v3_spine/launch_detached.py')
    anchors['scripts/v3_spine/recreate_v3_checkpointed.py'] = sha(
        'scripts/v3_spine/recreate_v3_checkpointed.py')
    anchors['scripts/v3_spine/resume_peach_dream_c24.sh'] = sha(
        'scripts/v3_spine/resume_peach_dream_c24.sh')

    # Rubric hash chain anchors
    anchors['data/v3_spine/rubric_hash_v2.txt'] = sha('data/v3_spine/rubric_hash_v2.txt')
    anchors['docs/v3_spine_rubric_v2.md'] = sha('docs/v3_spine_rubric_v2.md')
    anchors['docs/v3_spine_unified_driver_spec.md'] = sha('docs/v3_spine_unified_driver_spec.md')

    # focus_set_v2
    anchors['data/recreate_v2/focus_set_v2.json'] = sha('data/recreate_v2/focus_set_v2.json')

    # c5 CG delivery
    for p in [
        'data/v3/deliveries/31a164f845f8e27e/operator_section/manifest.json',
        'data/v3/deliveries/31a164f845f8e27e/operator_section/panel.json',
        'data/v3/deliveries/31a164f845f8e27e/operator_section/panel.tsv',
    ]:
        anchors[p] = sha(p)

    # c23 anchor preservation snapshots
    for p in [
        'data/v3/deliveries/88d247468cb6d49f/cycle23/anchor_preservation_pre.json',
        'data/v3/deliveries/88d247468cb6d49f/cycle23/anchor_preservation_post.json',
    ]:
        anchors[p] = sha(p)

    # c25 wrapper script we just wrote
    anchors['scripts/v3_spine/resume_peach_dream_c25.sh'] = sha(
        'scripts/v3_spine/resume_peach_dream_c25.sh')

    # FluidR3_GM.sf2 (look up common paths)
    for p in [
        'data/soundfonts/FluidR3_GM.sf2',
        'workspace/FluidR3_GM.sf2',
        'workspace/soundfonts/FluidR3_GM.sf2',
    ]:
        if pathlib.Path(p).is_file():
            anchors[p] = sha(p)
            break

    # c23 clone-1 muscriptor partial (drums+bass done before session boundary)
    ms = 'data/v3_spine/88d247468cb6d49f/operator_section_c23_unified/muscriptor'
    for name in ('drums.json', 'drums.mid', 'bass.json', 'bass.mid',
                 'guitar.json', 'guitar.mid', 'other.json'):
        p = f'{ms}/{name}'
        anchors[p] = sha(p)

    # c23 clone-2 rules delivery (additional artifacts)
    for p in ['data/v3/rules/rules_artifact.sha256',
              'data/v3/rules/verdict.json',
              'data/v3/rules/anchor_preservation_c23.json',
              'data/v3/rules/ledger_c23_clone_2.jsonl']:
        anchors[p] = sha(p)

    # c22 cycle22 partial artifacts (Peach Dream first attempt)
    for p in ['data/v3/deliveries/88d247468cb6d49f/cycle22/env_pin.json',
              'data/v3/deliveries/88d247468cb6d49f/cycle22/run_report.json',
              'data/v3/deliveries/88d247468cb6d49f/cycle22/run.log']:
        anchors[p] = sha(p)

    # c24 docs
    anchors['docs/v3_spine_stage_checkpointed_driver_spec.md'] = sha(
        'docs/v3_spine_stage_checkpointed_driver_spec.md')
    anchors['docs/freshness_cache_short_circuit_policy.md'] = sha(
        'docs/freshness_cache_short_circuit_policy.md')

    # c23 cycle23 run.log
    anchors['data/v3/deliveries/88d247468cb6d49f/cycle23/run.log'] = sha(
        'data/v3/deliveries/88d247468cb6d49f/cycle23/run.log')
    anchors['data/v3/deliveries/88d247468cb6d49f/cycle23/merge_report.md'] = sha(
        'data/v3/deliveries/88d247468cb6d49f/cycle23/merge_report.md')

    # c22 canonical read-only anchor (already in list but explicit as SHA prefix check)

    n_present = sum(1 for v in anchors.values() if v)
    n_missing = sum(1 for v in anchors.values() if v is None)
    out = pathlib.Path('data/v3/deliveries/88d247468cb6d49f/cycle25')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'anchor_preservation_pre.json').write_text(json.dumps({
        'anchors': anchors,
        'n_total': len(anchors),
        'n_present': n_present,
        'n_missing': n_missing,
    }, sort_keys=True, indent=2))
    print(f'anchors n_total={len(anchors)} n_present={n_present} n_missing={n_missing}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
