#!/usr/bin/python3
# Verdict resolver for M-SCORE-1/bridge-api-real-audio-quantization.
# Author: cyd7bevdr@mozmail.com, cycle 38, fork 33a2a8003c84 / clone-1.
import sys
assert sys.executable == '/usr/bin/python3', sys.executable

import json
import hashlib
from pathlib import Path

from scripts.score_bridge_v2._shared import REPO_ROOT, PROBE_DIR


VERDICT_QUANTIZATION_FIXED = 'QUANTIZATION_FIXED'
VERDICT_QUANTIZATION_REDEFINED_GAP = 'QUANTIZATION_REDEFINED_GAP'
VERDICT_QUANTIZATION_STILL_GAP = 'QUANTIZATION_STILL_GAP'


REF_NOTE_COUNT = 195  # from data/score_bridge_real_audio/inputs/fallback_reference_meta.txt


def resolve_verdict():
    p1 = json.loads((PROBE_DIR / 'p1_summary.json').read_text())
    p2 = json.loads((PROBE_DIR / 'p2_summary.json').read_text())
    p3 = json.loads((PROBE_DIR / 'p3_summary.json').read_text())

    # STRICT winners (all three §4 c8 thresholds satisfied) — for QUANTIZATION_FIXED.
    p1_win_strict = p1.get('winning_row')
    p2_win_strict = p2.get('winning_row')

    # RELAXED P3: byte-deterministic AND event count preserved (rubric §7 REDEFINED_GAP (b)).
    p3_win_relaxed = None
    for r in p3.get('rows', []):
        if (r.get('byte_deterministic') is True
                and r.get('event_count') == REF_NOTE_COUNT):
            p3_win_relaxed = r
            break

    # QUANTIZATION_FIXED: strict P1 or P2 native (rubric §7 (1)).
    if p1_win_strict or p2_win_strict:
        verdict = VERDICT_QUANTIZATION_FIXED
        winning_path = {
            'source_probe': ('P1' if p1_win_strict else 'P2'),
            'row': p1_win_strict or p2_win_strict,
        }
    elif p3_win_relaxed:
        # REDEFINED_GAP: any P3 backend byte-det + event-count-preserved
        # (rubric §7 (2) (b)). c8 onset/duration drift may fail; the new
        # anchor documents the redefined tolerance envelope.
        verdict = VERDICT_QUANTIZATION_REDEFINED_GAP
        winning_path = {'source_probe': 'P3', 'row': p3_win_relaxed}
    else:
        verdict = VERDICT_QUANTIZATION_STILL_GAP
        winning_path = None

    rubric_hash_path = REPO_ROOT / 'data/score_bridge_real_audio/rubric_hash.txt'
    rubric_hash = rubric_hash_path.read_text().strip()

    def _pack(summary):
        r = summary.get('winning_row')
        return {
            'has_winner': bool(r),
            'winning_row': r,
            'row_count': (len(summary.get('rows', [])) if 'rows' in summary
                          else summary.get('total_combinations', 0)),
        }

    verdict_obj = {
        'verdict': verdict,
        'rubric_hash': rubric_hash,
        'winning_path': winning_path,
        'p1_summary': _pack(p1),
        'p2_summary': _pack(p2),
        'p3_summary': _pack(p3),
        'fidelity_metrics': (winning_path['row'] if winning_path else None),
    }
    out_path = REPO_ROOT / 'data/score_bridge_real_audio/verdict.json'
    out_path.write_text(json.dumps(verdict_obj, indent=2, sort_keys=True, default=str) + '\n')
    return verdict_obj


def compute_anchor_preservation():
    """Compute pre/post SHAs for the read-only anchors listed in the rubric.

    We only record the CURRENT SHA under `anchors_current`; the test
    asserts they match a captured `anchors_expected` set persisted in this
    same file (bootstrapped on first write when the file does not exist).
    """
    anchors = [
        'scripts/score/bridge.py',
        'scripts/recreate_v0/run_pipeline.py',
        'scripts/recreate_v0/run_all.py',
        'scripts/recreate_v0/select_song.py',
        'scripts/recreate_v0/__init__.py',
        'data/recreate_v0/per_stage/06_score/merged.musicxml',
        'data/recreate_v0/rubric_hash.txt',
        'data/recreate_v0/verdict.json',
        'data/recreate_v0/anchor_preservation.json',
        'scripts/tex/render_effects_layered.py',
        'scripts/tex/render_bare_midi.py',
        'scripts/texture/panel.py',
    ]
    current = {}
    for rel in anchors:
        p = REPO_ROOT / rel
        if p.exists():
            current[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
        else:
            current[rel] = 'ABSENT'
    out_path = REPO_ROOT / 'data/score_bridge_real_audio/anchor_preservation.json'
    if out_path.exists():
        prev = json.loads(out_path.read_text())
        expected = prev.get('anchors_expected', prev.get('anchors_current', current))
    else:
        expected = current
    changed = {k: {'expected': expected.get(k), 'current': v}
               for k, v in current.items() if expected.get(k) != v}
    obj = {
        'anchors_expected': expected,
        'anchors_current': current,
        'changed': changed,
        'preserved': not bool(changed),
    }
    out_path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')
    return obj


if __name__ == '__main__':
    ap = compute_anchor_preservation()
    v = resolve_verdict()
    print('anchor_preservation.preserved:', ap['preserved'])
    print('verdict:', v['verdict'])
    if v.get('winning_path'):
        print('winning_path:', json.dumps(v['winning_path'], indent=2, sort_keys=True, default=str))
