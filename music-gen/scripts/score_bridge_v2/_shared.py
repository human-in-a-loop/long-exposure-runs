#!/usr/bin/python3
# Shared helpers for M-SCORE-1/bridge-api-real-audio-quantization probes.
# Author: cyd7bevdr@mozmail.com, cycle 38, fork 33a2a8003c84 / clone-1.
import sys
assert sys.executable == '/usr/bin/python3', sys.executable

import hashlib
import os
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = REPO_ROOT / 'data/score_bridge_real_audio/inputs/merged_real_audio.musicxml'
FIXTURE_SHA = '95de5356fc127e8ff2b3c5153a950b35ddd4836b1ec1f40d658f41ebb73e1592'
REF_MIDI_PATH = REPO_ROOT / 'data/score_bridge_real_audio/inputs/fallback_reference.midi'
REF_MIDI_SHA = '5cccca6c48820e26be95aae125679b4002ccab1a28b9aea13500066d213ac599'
REF_NOTE_COUNT = 195
PROBE_DIR = REPO_ROOT / 'data/score_bridge_real_audio/probes'
FETCHABILITY_PATH = REPO_ROOT / 'data/score_bridge_real_audio/fetchability_ladder.jsonl'

# c8-frozen tolerance envelope
TOL_EVENT_COUNT_ABS = 0        # exact preservation
TOL_ONSET_MS = 2.0
TOL_DUR_TICKS_PPQ480 = 1


def determinism_env(extra=None):
    """Environment for byte-determinism × 2 protocol."""
    env = os.environ.copy()
    env.update({
        'PYTHONHASHSEED': '0',
        'SOURCE_DATE_EPOCH': '1577836800',
        'TZ': 'UTC',
        'LC_ALL': 'C.UTF-8',
        'OMP_NUM_THREADS': '1',
        'MKL_NUM_THREADS': '1',
        'OPENBLAS_NUM_THREADS': '1',
        'QT_QPA_PLATFORM': 'offscreen',
    })
    if extra:
        env.update(extra)
    return env


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(Path(p).read_bytes())


def mscore3_convert(inp: Path, out: Path, *, extra_argv=None, timeout_s=60) -> subprocess.CompletedProcess:
    """Invoke mscore3 to convert `inp` -> `out`. Returns CompletedProcess.
    Non-zero rc is NOT raised — caller inspects rc/stderr.
    """
    argv = ['mscore3']
    if extra_argv:
        argv.extend(extra_argv)
    argv.extend(['-o', str(out), str(inp)])
    return subprocess.run(argv, env=determinism_env(),
                          capture_output=True, timeout=timeout_s, check=False)


def load_midi_events(midi_path: Path):
    """Return list of (onset_s, dur_s, pitch, velocity, channel) tuples,
    for tolerance-envelope comparison. Uses mido; ignores meta events.
    """
    import mido
    mid = mido.MidiFile(str(midi_path))
    tpb = mid.ticks_per_beat
    tempo_us = 500000  # default 120 BPM
    events = []
    # Scan for first set_tempo (any track).
    for tr in mid.tracks:
        for msg in tr:
            if msg.type == 'set_tempo':
                tempo_us = msg.tempo
                break
        else:
            continue
        break
    spt = (tempo_us / 1_000_000.0) / tpb
    for tr in mid.tracks:
        abs_ticks = 0
        active = {}
        for msg in tr:
            abs_ticks += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                active[(msg.channel, msg.note)] = (abs_ticks, msg.velocity)
            elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in active:
                    onset_ticks, vel = active.pop(key)
                    dur_ticks = abs_ticks - onset_ticks
                    if dur_ticks <= 0:
                        continue
                    events.append((onset_ticks * spt, dur_ticks * spt,
                                   msg.note, vel, msg.channel))
    return events


def compare_to_reference(midi_path: Path, ref_note_count: int = REF_NOTE_COUNT):
    """Compare a candidate MIDI's note events against the pretty_midi
    reference. Returns dict with event_count, onset_drift_ms_max,
    duration_drift_ticks_max, fidelity_pass_c8_tolerance.

    Comparison is per-(pitch, channel_class) sorted by onset for the
    smaller of the two lists — a strict, permissive-to-order pairing.
    If event counts differ, drift stats fall back to positional pairing
    on the sorted-by-onset sequences up to min(len(a), len(b)).
    """
    if not midi_path.exists():
        return {
            'event_count': 0,
            'onset_drift_ms_max': None,
            'duration_drift_ticks_max': None,
            'fidelity_pass_c8_tolerance': False,
            'reason': 'output_midi_missing',
        }
    try:
        cand = load_midi_events(midi_path)
        ref = load_midi_events(REF_MIDI_PATH)
    except Exception as e:
        return {
            'event_count': 0,
            'onset_drift_ms_max': None,
            'duration_drift_ticks_max': None,
            'fidelity_pass_c8_tolerance': False,
            'reason': f'parse_error: {type(e).__name__}: {e}',
        }
    cand_sorted = sorted(cand, key=lambda x: (x[0], x[2]))
    ref_sorted = sorted(ref, key=lambda x: (x[0], x[2]))
    onset_diffs = []
    dur_diffs = []
    n = min(len(cand_sorted), len(ref_sorted))
    ppq480_tick_s = 60.0 / 120.0 / 480.0
    for i in range(n):
        c_onset, c_dur, _, _, _ = cand_sorted[i]
        r_onset, r_dur, _, _, _ = ref_sorted[i]
        onset_diffs.append(abs(c_onset - r_onset) * 1000.0)
        dur_diffs.append(abs(c_dur - r_dur) / ppq480_tick_s)
    onset_drift_ms_max = max(onset_diffs) if onset_diffs else None
    dur_drift_ticks_max = max(dur_diffs) if dur_diffs else None
    event_count = len(cand_sorted)
    count_ok = (event_count == ref_note_count)
    onset_ok = (onset_drift_ms_max is not None and onset_drift_ms_max <= TOL_ONSET_MS)
    dur_ok = (dur_drift_ticks_max is not None and dur_drift_ticks_max <= TOL_DUR_TICKS_PPQ480)
    return {
        'event_count': event_count,
        'onset_drift_ms_max': onset_drift_ms_max,
        'duration_drift_ticks_max': dur_drift_ticks_max,
        'fidelity_pass_c8_tolerance': bool(count_ok and onset_ok and dur_ok),
        'reason': (
            'ok' if (count_ok and onset_ok and dur_ok)
            else ('count_mismatch:{}!={}'.format(event_count, ref_note_count)
                  if not count_ok else
                  ('onset_drift_exceeds_2ms:{:.3f}'.format(onset_drift_ms_max)
                   if not onset_ok else 'duration_drift_exceeds_1tick:{:.3f}'.format(dur_drift_ticks_max)))
        ),
    }


def append_fetchability(entry: dict):
    """Append one JSONL row to the fetchability ladder."""
    import json
    FETCHABILITY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FETCHABILITY_PATH, 'a') as f:
        f.write(json.dumps(entry, sort_keys=True) + '\n')
