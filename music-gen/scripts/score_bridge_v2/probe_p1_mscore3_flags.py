#!/usr/bin/python3
# P1 mscore3 flag matrix probe for M-SCORE-1/bridge-api-real-audio-quantization.
# Author: cyd7bevdr@mozmail.com, cycle 38, fork 33a2a8003c84 / clone-1.
import sys
assert sys.executable == '/usr/bin/python3', sys.executable

import itertools
import json
import tempfile
from pathlib import Path

from scripts.score_bridge_v2._shared import (
    FIXTURE_PATH, PROBE_DIR, mscore3_convert, sha256_file,
    compare_to_reference,
)

# Flag axes actually supported by mscore3 3.2.3 (see rubric §6 P1).
# Each axis is a list of (label, argv_slice).
_AXIS_A = [('noF', []),          ('F', ['-F'])]           # factory-settings
_AXIS_B = [('noR', []),          ('R', ['-R'])]           # revert-settings
_AXIS_C = [('noE', []),          ('E', ['-e'])]           # experimental
_AXIS_D = [('noT', []),          ('T', ['-t'])]           # test-mode


def enumerate_combos():
    for a, b, c, d in itertools.product(_AXIS_A, _AXIS_B, _AXIS_C, _AXIS_D):
        label = a[0] + '_' + b[0] + '_' + c[0] + '_' + d[0]
        argv = list(a[1]) + list(b[1]) + list(c[1]) + list(d[1])
        yield label, argv


def run_one(label, argv):
    """Two independent runs into fresh temp dirs; report SHAs + fidelity."""
    shas = []
    rcs = []
    fidelity = None
    for run_i in range(2):
        with tempfile.TemporaryDirectory(prefix='p1_' + label + '_r' + str(run_i) + '_') as td:
            out = Path(td) / 'out.midi'
            proc = mscore3_convert(FIXTURE_PATH, out, extra_argv=argv, timeout_s=60)
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
    return {
        'flag_combination': label,
        'argv': ' '.join(argv) or '(default)',
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
    }


def main():
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    combos = sorted(enumerate_combos())
    for label, argv in combos:
        print('P1', label, argv)
        rows.append(run_one(label, argv))
    tsv = PROBE_DIR / 'p1_mscore3_flags.tsv'
    cols = [
        'flag_combination', 'argv', 'run1_midi_sha', 'run2_midi_sha',
        'byte_deterministic', 'event_count', 'onset_drift_ms_max',
        'duration_drift_ticks_max', 'fidelity_pass_c8_tolerance',
        'rc_run1', 'rc_run2', 'reason',
    ]
    with open(tsv, 'w') as f:
        f.write('\t'.join(cols) + '\n')
        for r in rows:
            f.write('\t'.join(str(r[c]) for c in cols) + '\n')
    # Winner: first in canonical order with byte_deterministic AND fidelity_pass.
    winner = next(
        (r for r in rows if r['byte_deterministic'] and r['fidelity_pass_c8_tolerance']),
        None,
    )
    summary = {
        'total_combinations': len(rows),
        'byte_deterministic_count': sum(1 for r in rows if r['byte_deterministic']),
        'fidelity_pass_count': sum(1 for r in rows if r['fidelity_pass_c8_tolerance']),
        'rc_zero_count': sum(1 for r in rows if r['rc_run1'] == 0 and r['rc_run2'] == 0),
        'winning_row': winner,
    }
    (PROBE_DIR / 'p1_summary.json').write_text(
        json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print('P1 summary:', json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == '__main__':
    main()
