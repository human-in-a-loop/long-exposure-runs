#!/usr/bin/env /usr/bin/python3
"""Compare full-mix canonicalized MIDI vs merged per-stem MIDI.

Emits a reconciliation report. Per operator directive point 4, reconcile in
per-stem's favor by default; log full_mix_only_findings for review — do
NOT auto-merge them this cycle.
"""
import json
from collections import Counter
from pathlib import Path

import mido

SONG_SHA16 = '31a164f845f8e27e'


def count_notes(path: Path):
    mf = mido.MidiFile(path)
    count = 0
    pc = Counter()  # pitch class (%12)
    parts = Counter()  # by channel
    for track in mf.tracks:
        for m in track:
            if m.type == 'note_on':
                count += 1
                pc[m.note % 12] += 1
                parts[m.channel] += 1
    return count, pc, parts


def main() -> None:
    full = Path(f'data/v3_spine/{SONG_SHA16}/canonical_midi/full_mix.mid')
    merged = Path(f'data/v3_spine/{SONG_SHA16}/merged.mid')
    fm_count, fm_pc, fm_parts = count_notes(full)
    m_count, m_pc, m_parts = count_notes(merged)
    # per pitch class delta
    all_pcs = set(fm_pc) | set(m_pc)
    pc_delta = {int(p): fm_pc.get(p, 0) - m_pc.get(p, 0) for p in sorted(all_pcs)}
    # parts present in full_mix but not in merged (by channel)
    fm_ch = set(fm_parts.keys())
    m_ch = set(m_parts.keys())
    only_fm = sorted(fm_ch - m_ch)
    only_merged = sorted(m_ch - fm_ch)

    findings = []
    if only_fm:
        findings.append({
            'kind': 'channels_in_full_mix_only',
            'channels': only_fm,
            'note_counts_by_channel': {ch: fm_parts[ch] for ch in only_fm},
        })

    payload = {
        'schema_version': 1, 'cycle': 4, 'song_sha16': SONG_SHA16,
        'full_mix_note_count': fm_count,
        'merged_note_count': m_count,
        'per_pitch_class_delta_full_minus_merged': pc_delta,
        'parts_present_in_full_mix_absent_in_merged': only_fm,
        'parts_present_in_merged_absent_in_full_mix': only_merged,
        'full_mix_only_findings': findings,
        'reconciliation_policy': 'reconcile_in_per_stem_favor_default_per_operator_directive_point_4',
        'auto_merge_this_cycle': False,
    }
    out = Path(f'data/v3_spine/{SONG_SHA16}/full_mix_reconciliation.json')
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print(f'wrote {out}: full_mix={fm_count} merged={m_count}')
    if findings:
        print(f'{len(findings)} full_mix_only_findings logged (NOT auto-merged this cycle)')


if __name__ == '__main__':
    main()
