#!/usr/bin/python3
# c39 runner: normalize_v2 fixture, invoke mscore3 x2, compute SHAs +
# fidelity, emit verdict.json + normalizer_v2_run.tsv +
# type_dot_reconstruction_log.json.
#
# Milestone: M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2
# Author: cyd7bevdr@mozmail.com, cycle 39.
import sys
assert sys.executable == '/usr/bin/python3', sys.executable

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from scripts.score_bridge_v2 import normalize_v2 as nv2
from scripts.score_bridge_v2._shared import (
    determinism_env,
    load_midi_events,
    REF_MIDI_PATH,
    REF_NOTE_COUNT,
    TOL_ONSET_MS,
    TOL_DUR_TICKS_PPQ480,
    FIXTURE_PATH,
)


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / 'data/score_bridge_real_audio_normalizer_v2'
INPUTS_DIR = OUT_DIR / 'inputs'
RESULTS_DIR = OUT_DIR / 'results'
RUBRIC_HASH_PATH = OUT_DIR / 'rubric_hash.txt'


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def _paired_drift(cand, ref):
    """Positional pairing drift on sorted-by-onset lists. Only valid on
    equal-length lists; caller checks event_count first.
    """
    cs = sorted(cand, key=lambda x: (x[0], x[2]))
    rs = sorted(ref, key=lambda x: (x[0], x[2]))
    n = min(len(cs), len(rs))
    ppq480_tick_s = 60.0 / 120.0 / 480.0
    onsets, durs = [], []
    for i in range(n):
        onsets.append(abs(cs[i][0] - rs[i][0]) * 1000.0)
        durs.append(abs(cs[i][1] - rs[i][1]) / ppq480_tick_s)
    return (
        max(onsets) if onsets else None,
        max(durs) if durs else None,
        (sum(onsets) / len(onsets)) if onsets else None,
        (sum(durs) / len(durs)) if durs else None,
    )


def _mscore3_run(xml_path: Path, out_midi: Path) -> int:
    argv = ['mscore3', '-F', '-o', str(out_midi), str(xml_path)]
    res = subprocess.run(argv, env=determinism_env(),
                         capture_output=True, timeout=180, check=False)
    return res.returncode


def resolve_verdict(rc1, rc2, sha1, sha2, event_count,
                    onset_drift, dur_drift):
    """Rubric §7 verdict ladder."""
    if (rc1 == 0 and rc2 == 0 and sha1 == sha2 and event_count == REF_NOTE_COUNT
            and onset_drift is not None and onset_drift <= TOL_ONSET_MS
            and dur_drift is not None and dur_drift <= TOL_DUR_TICKS_PPQ480):
        return ('QUANTIZATION_FIXED_NORMALIZER_V2', None)
    if (rc1 == 0 and rc2 == 0 and sha1 == sha2
            and event_count == REF_NOTE_COUNT):
        return ('QUANTIZATION_STILL_REDEFINED_GAP', None)
    # FAILS
    if rc1 != 0 or rc2 != 0:
        return ('QUANTIZATION_NORMALIZER_V2_FAILS', 'rc_nonzero')
    if sha1 != sha2:
        return ('QUANTIZATION_NORMALIZER_V2_FAILS', 'sha_mismatch')
    return ('QUANTIZATION_NORMALIZER_V2_FAILS', 'event_count_wrong')


def main():
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Normalize
    norm_out = INPUTS_DIR / 'merged_normalized_v2.musicxml'
    stats = nv2.normalize_v2_file(FIXTURE_PATH, norm_out)

    # Persist reconstruction log
    log_path = RESULTS_DIR / 'type_dot_reconstruction_log.json'
    log_path.write_text(json.dumps({
        'canonical_divisions': nv2.CANONICAL_DIVISIONS,
        'entries': stats['reconstruction_log'],
        'entry_count': len(stats['reconstruction_log']),
        'summary_counts': {
            'notes_scanned': stats['notes_scanned'],
            'type_rewrites': stats['type_rewrites'],
            'dot_injections': stats['dot_injections'],
            'tuplet_insertions': stats['tuplet_insertions'],
            'forced_quarter': stats['forced_quarter'],
        },
    }, indent=2, sort_keys=True))

    # 2. mscore3 x 2 in fresh temp dirs
    d1 = Path(tempfile.mkdtemp(prefix='c39_run1_'))
    d2 = Path(tempfile.mkdtemp(prefix='c39_run2_'))
    out1 = d1 / 'out.mid'
    out2 = d2 / 'out.mid'
    rc1 = _mscore3_run(norm_out, out1)
    rc2 = _mscore3_run(norm_out, out2)
    sha1 = sha256_file(out1) if out1.exists() else None
    sha2 = sha256_file(out2) if out2.exists() else None

    # 3. Fidelity from run1
    event_count = None
    onset_max = onset_mean = None
    dur_max = dur_mean = None
    if out1.exists():
        cand = load_midi_events(out1)
        ref = load_midi_events(REF_MIDI_PATH)
        event_count = len(cand)
        onset_max, dur_max, onset_mean, dur_mean = _paired_drift(cand, ref)

    # 4. Verdict
    verdict, failure_mode = resolve_verdict(
        rc1, rc2, sha1, sha2, event_count, onset_max, dur_max)

    # 5. TSV
    tsv_path = RESULTS_DIR / 'normalizer_v2_run.tsv'
    tsv_lines = [
        '\t'.join(['run', 'rc', 'sha256', 'bytes']),
        '\t'.join(['1', str(rc1), sha1 or '', str(out1.stat().st_size if out1.exists() else 0)]),
        '\t'.join(['2', str(rc2), sha2 or '', str(out2.stat().st_size if out2.exists() else 0)]),
    ]
    tsv_path.write_text('\n'.join(tsv_lines) + '\n')

    # 6. verdict.json
    rubric_hash = RUBRIC_HASH_PATH.read_text().strip()
    verdict_obj = {
        'verdict': verdict,
        'failure_mode': failure_mode,
        'rubric_hash': rubric_hash,
        'canonical_divisions': nv2.CANONICAL_DIVISIONS,
        'fixture_sha256': sha256_file(FIXTURE_PATH),
        'normalized_v2_sha256': sha256_file(norm_out),
        'reference_sha256': sha256_file(REF_MIDI_PATH),
        'reference_event_count': REF_NOTE_COUNT,
        'mscore3_flag_row': '-F',
        'runs': [
            {'run': 1, 'rc': rc1, 'sha256': sha1,
             'bytes': out1.stat().st_size if out1.exists() else 0},
            {'run': 2, 'rc': rc2, 'sha256': sha2,
             'bytes': out2.stat().st_size if out2.exists() else 0},
        ],
        'byte_deterministic_x2': (sha1 is not None and sha1 == sha2),
        'fidelity': {
            'event_count': event_count,
            'event_count_match': event_count == REF_NOTE_COUNT,
            'onset_drift_ms_max': onset_max,
            'onset_drift_ms_mean': onset_mean,
            'duration_drift_ticks_max_ppq480': dur_max,
            'duration_drift_ticks_mean_ppq480': dur_mean,
            'onset_pass_strict_c8': (onset_max is not None
                                     and onset_max <= TOL_ONSET_MS),
            'duration_pass_strict_c8': (dur_max is not None
                                        and dur_max <= TOL_DUR_TICKS_PPQ480),
        },
        'normalizer_stats': {
            'notes_scanned': stats['notes_scanned'],
            'type_rewrites': stats['type_rewrites'],
            'dot_injections': stats['dot_injections'],
            'tuplet_insertions': stats['tuplet_insertions'],
            'forced_quarter': stats['forced_quarter'],
        },
    }
    verdict_path = OUT_DIR / 'verdict.json'
    verdict_path.write_text(json.dumps(verdict_obj, indent=2, sort_keys=True))

    print(json.dumps(verdict_obj, indent=2, sort_keys=True))
    return verdict


if __name__ == '__main__':
    main()
