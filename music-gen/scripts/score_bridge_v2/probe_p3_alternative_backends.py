#!/usr/bin/python3
# P3 alternative MusicXML -> MIDI backend probe.
# Author: cyd7bevdr@mozmail.com, cycle 38, fork 33a2a8003c84 / clone-1.
import sys
assert sys.executable == '/usr/bin/python3', sys.executable

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from scripts.score_bridge_v2._shared import (
    FIXTURE_PATH, PROBE_DIR, determinism_env, sha256_file,
    compare_to_reference, append_fetchability,
)


def _run_music21(run_i: int) -> tuple:
    """Run music21.stream.Score.write('midi', ...) in a fresh subprocess
    to keep environment (PYTHONHASHSEED etc.) pinned per run.
    """
    with tempfile.TemporaryDirectory(prefix='p3a_m21_r' + str(run_i) + '_') as td:
        out = Path(td) / 'out.midi'
        code = (
            "import sys, os\n"
            "assert sys.executable == '/usr/bin/python3'\n"
            "from music21 import converter\n"
            "s = converter.parse(r'" + str(FIXTURE_PATH) + "')\n"
            "s.write('midi', fp=r'" + str(out) + "')\n"
        )
        proc = subprocess.run(
            ['/usr/bin/python3', '-c', code],
            env=determinism_env(), capture_output=True, text=True, timeout=180,
        )
        if proc.returncode != 0 or not out.exists():
            return (None, proc.returncode, proc.stderr[-500:])
        # Copy to a persistent path so the caller can compare across runs.
        persist = PROBE_DIR / ('p3_music21_r' + str(run_i) + '.midi')
        persist.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(out, persist)
        return (sha256_file(persist), proc.returncode, '')


def _run_lilypond(run_i: int) -> tuple:
    """Lilypond is not installed in this workspace — record fetch-fail."""
    return (None, 127, 'lilypond binary not on PATH (which lilypond -> nothing)')


def probe_music21():
    rows_shas = []
    rcs = []
    stderrs = []
    fidelity = None
    for run_i in range(2):
        sha, rc, err = _run_music21(run_i)
        rows_shas.append(sha)
        rcs.append(rc)
        stderrs.append(err)
    ok = all(s is not None for s in rows_shas)
    if ok:
        fidelity = compare_to_reference(PROBE_DIR / 'p3_music21_r0.midi')
    else:
        fidelity = {
            'event_count': 0,
            'onset_drift_ms_max': None,
            'duration_drift_ticks_max': None,
            'fidelity_pass_c8_tolerance': False,
            'reason': 'music21_run_failed:' + (stderrs[0] or '')[:200],
        }
    byte_det = ok and rows_shas[0] == rows_shas[1]
    append_fetchability({
        'probe': 'p3_music21',
        'fetch_status': 'FETCH_OK' if ok else 'FETCH_FAIL',
        'rc_run1': rcs[0], 'rc_run2': rcs[1],
        'note': stderrs[0][:200] if stderrs[0] else '',
    })
    return {
        'backend': 'music21',
        'fetch_status': 'FETCH_OK' if ok else 'FETCH_FAIL',
        'run1_midi_sha': rows_shas[0] or '',
        'run2_midi_sha': rows_shas[1] or '',
        'byte_deterministic': byte_det,
        'event_count': fidelity['event_count'],
        'onset_drift_ms_max': fidelity['onset_drift_ms_max'],
        'duration_drift_ticks_max': fidelity['duration_drift_ticks_max'],
        'fidelity_pass_c8_tolerance': fidelity['fidelity_pass_c8_tolerance'],
        'rc_run1': rcs[0],
        'rc_run2': rcs[1],
        'reason': fidelity.get('reason', ''),
    }


def probe_lilypond():
    shas = []
    rcs = []
    for run_i in range(2):
        sha, rc, err = _run_lilypond(run_i)
        shas.append(sha)
        rcs.append(rc)
    append_fetchability({
        'probe': 'p3_lilypond',
        'fetch_status': 'FETCH_FAIL',
        'rc_run1': rcs[0], 'rc_run2': rcs[1],
        'note': 'lilypond binary not on PATH',
    })
    return {
        'backend': 'lilypond',
        'fetch_status': 'FETCH_FAIL',
        'run1_midi_sha': '',
        'run2_midi_sha': '',
        'byte_deterministic': None,
        'event_count': None,
        'onset_drift_ms_max': None,
        'duration_drift_ticks_max': None,
        'fidelity_pass_c8_tolerance': None,
        'rc_run1': rcs[0],
        'rc_run2': rcs[1],
        'reason': 'lilypond binary not installed in workspace',
    }


def main():
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    rows = [probe_music21(), probe_lilypond()]
    tsv = PROBE_DIR / 'p3_alternative_backends.tsv'
    cols = [
        'backend', 'fetch_status', 'run1_midi_sha', 'run2_midi_sha',
        'byte_deterministic', 'event_count', 'onset_drift_ms_max',
        'duration_drift_ticks_max', 'fidelity_pass_c8_tolerance',
        'rc_run1', 'rc_run2', 'reason',
    ]
    with open(tsv, 'w') as f:
        f.write('\t'.join(cols) + '\n')
        for r in rows:
            f.write('\t'.join(str(r[c]) for c in cols) + '\n')
    winner = next(
        (r for r in rows if r.get('byte_deterministic')
         and r.get('fidelity_pass_c8_tolerance')),
        None,
    )
    summary = {'rows': rows, 'winning_row': winner}
    (PROBE_DIR / 'p3_summary.json').write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + '\n')
    print('P3 summary:', json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == '__main__':
    main()
