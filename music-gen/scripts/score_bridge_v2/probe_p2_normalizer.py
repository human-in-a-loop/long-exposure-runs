#!/usr/bin/python3
# P2 pre-mscore3 MusicXML normalizer probe.
# Author: cyd7bevdr@mozmail.com, cycle 38, fork 33a2a8003c84 / clone-1.
import sys
assert sys.executable == '/usr/bin/python3', sys.executable

import json
import re
import tempfile
from pathlib import Path

from scripts.score_bridge_v2._shared import (
    FIXTURE_PATH, PROBE_DIR, REPO_ROOT, mscore3_convert, sha256_file,
    compare_to_reference,
)
from scripts.score_bridge_v2.normalize import normalize_file


def _attribute_properties():
    """Diff structural properties between the fixture and the c8 seed."""
    seed = REPO_ROOT / 'data/score_bridge_real_audio/inputs/seed_synthetic.musicxml'
    fixture = FIXTURE_PATH

    def props(p: Path):
        t = p.read_text(encoding='utf-8')
        return {
            'divisions_values': sorted(set(re.findall(r'<divisions>(\d+)</divisions>', t))),
            'divisions_count': len(re.findall(r'<divisions>\d+</divisions>', t)),
            'duration_count': len(re.findall(r'<duration>\d+</duration>', t)),
            'tie_count': len(re.findall(r'<tie(?:\s[^>]*)?/>', t)),
            'tied_count': len(re.findall(r'<tied(?:\s[^>]*)?/>', t)),
            'time_modification_count': len(re.findall(r'<time-modification>', t)),
            'note_close_count': len(re.findall(r'</note>', t)),
            'rest_count': len(re.findall(r'<rest\s*/>', t)),
            'part_count': len(re.findall(r'<score-part\s', t)),
            'bytes': p.stat().st_size,
        }

    fixture_props = props(fixture)
    seed_props = props(seed)
    hypotheses = []
    if fixture_props['divisions_values'] != seed_props['divisions_values']:
        hypotheses.append({
            'property': 'divisions',
            'fixture': fixture_props['divisions_values'],
            'seed': seed_props['divisions_values'],
            'candidate_pathology': True,
            'rationale': (
                'mscore3 rounding-error diagnostic uses denominators 20160 '
                'and 5040 for the fixture (which has divisions=10080 - LCM '
                'including 2^5*3^2*5*7 - and no tuplets). PPQ=480 (LCM of '
                '2^5*3*5) is mscore3\'s own default; rescaling to it '
                'eliminates the mismatch source.'
            ),
        })
    if fixture_props['tie_count'] + fixture_props['tied_count'] > 50 * (seed_props['tie_count'] + seed_props['tied_count'] + 1):
        hypotheses.append({
            'property': 'tie_density',
            'fixture_ties': fixture_props['tie_count'] + fixture_props['tied_count'],
            'seed_ties': seed_props['tie_count'] + seed_props['tied_count'],
            'candidate_pathology': False,
            'rationale': (
                'Higher tie density reflects real-audio onsets crossing '
                'bar-lines. Not the direct rounding-error source but may '
                'interact with divisions choice.'
            ),
        })
    if fixture_props['time_modification_count'] == 0 and any(
            'p[1] % 3 == 0' for p in []):
        pass  # placeholder for future tuplet analysis
    return {
        'fixture_props': fixture_props,
        'seed_props': seed_props,
        'candidate_hypotheses': hypotheses,
    }


def run_probe():
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    attr = _attribute_properties()

    rows = []
    # Baseline row: unnormalized fixture through mscore3 default (matches P1 row).
    for label, in_path in [('unnormalized_baseline', FIXTURE_PATH)]:
        shas = []
        rcs = []
        fidelity = None
        for run_i in range(2):
            with tempfile.TemporaryDirectory(prefix='p2_' + label + '_r' + str(run_i) + '_') as td:
                out = Path(td) / 'out.midi'
                proc = mscore3_convert(in_path, out, timeout_s=60)
                rcs.append(proc.returncode)
                if proc.returncode == 0 and out.exists():
                    shas.append(sha256_file(out))
                    if run_i == 0:
                        fidelity = compare_to_reference(out)
                else:
                    shas.append(None)
                    if run_i == 0:
                        fidelity = {
                            'event_count': 0,
                            'onset_drift_ms_max': None,
                            'duration_drift_ticks_max': None,
                            'fidelity_pass_c8_tolerance': False,
                            'reason': 'mscore3_rc_' + str(proc.returncode),
                        }
        byte_det = (shas[0] is not None and shas[0] == shas[1])
        rows.append({
            'label': label,
            'run1_midi_sha': shas[0] or '',
            'run2_midi_sha': shas[1] or '',
            'byte_deterministic': byte_det,
            'event_count': fidelity['event_count'],
            'onset_drift_ms_max': fidelity['onset_drift_ms_max'],
            'duration_drift_ticks_max': fidelity['duration_drift_ticks_max'],
            'fidelity_pass_c8_tolerance': fidelity['fidelity_pass_c8_tolerance'],
            'rc_run1': rcs[0],
            'rc_run2': rcs[1],
            'reason': fidelity.get('reason', ''),
            'normalize_stats': {},
        })

    # Normalize the fixture to PPQ=480 and re-run.
    with tempfile.TemporaryDirectory(prefix='p2_normalize_') as td:
        norm_xml = Path(td) / 'normalized.musicxml'
        stats = normalize_file(FIXTURE_PATH, norm_xml, target_divisions=480)
        # Persist a copy of the normalized XML for the report.
        persisted = PROBE_DIR / 'p2_normalized.musicxml'
        persisted.write_bytes(norm_xml.read_bytes())
        norm_sha = sha256_file(persisted)

        shas = []
        rcs = []
        fidelity = None
        for run_i in range(2):
            with tempfile.TemporaryDirectory(prefix='p2_norm_r' + str(run_i) + '_') as td2:
                out = Path(td2) / 'out.midi'
                proc = mscore3_convert(norm_xml, out, timeout_s=60)
                rcs.append(proc.returncode)
                if proc.returncode == 0 and out.exists():
                    shas.append(sha256_file(out))
                    if run_i == 0:
                        fidelity = compare_to_reference(out)
                else:
                    shas.append(None)
                    if run_i == 0:
                        fidelity = {
                            'event_count': 0,
                            'onset_drift_ms_max': None,
                            'duration_drift_ticks_max': None,
                            'fidelity_pass_c8_tolerance': False,
                            'reason': 'mscore3_rc_' + str(proc.returncode),
                        }
        byte_det = (shas[0] is not None and shas[0] == shas[1])
        rows.append({
            'label': 'normalized_ppq480',
            'run1_midi_sha': shas[0] or '',
            'run2_midi_sha': shas[1] or '',
            'byte_deterministic': byte_det,
            'event_count': fidelity['event_count'],
            'onset_drift_ms_max': fidelity['onset_drift_ms_max'],
            'duration_drift_ticks_max': fidelity['duration_drift_ticks_max'],
            'fidelity_pass_c8_tolerance': fidelity['fidelity_pass_c8_tolerance'],
            'rc_run1': rcs[0],
            'rc_run2': rcs[1],
            'reason': fidelity.get('reason', ''),
            'normalize_stats': stats,
            'normalized_xml_sha': norm_sha,
        })

    tsv = PROBE_DIR / 'p2_normalizer.tsv'
    cols = [
        'label', 'run1_midi_sha', 'run2_midi_sha', 'byte_deterministic',
        'event_count', 'onset_drift_ms_max', 'duration_drift_ticks_max',
        'fidelity_pass_c8_tolerance', 'rc_run1', 'rc_run2', 'reason',
    ]
    with open(tsv, 'w') as f:
        f.write('\t'.join(cols) + '\n')
        for r in rows:
            f.write('\t'.join(str(r[c]) for c in cols) + '\n')

    (PROBE_DIR / 'p2_property_attribution.json').write_text(
        json.dumps(attr, indent=2, sort_keys=True) + '\n')

    winner = next(
        (r for r in rows if r['label'] == 'normalized_ppq480'
         and r['byte_deterministic'] and r['fidelity_pass_c8_tolerance']),
        None,
    )
    summary = {
        'rows': rows,
        'winning_row': winner,
        'attribution': attr,
    }
    (PROBE_DIR / 'p2_summary.json').write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + '\n')
    return summary


if __name__ == '__main__':
    s = run_probe()
    print('P2 winning:', s['winning_row'])
