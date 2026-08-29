#!/usr/bin/python3
# P2 MusicXML normalizer for M-SCORE-1/bridge-api-real-audio-quantization.
# Author: cyd7bevdr@mozmail.com, cycle 38, fork 33a2a8003c84 / clone-1.
#
# Rewrites <divisions>10080</divisions> to a canonical PPQ=480, rescales
# every <duration> proportionally, and snaps sub-tick residuals to the
# nearest integer tick at the new divisions. The c37 clone-0 fixture has
# 0 <time-modification> elements (no tuplets) so 480 is safe.
import sys
assert sys.executable == '/usr/bin/python3', sys.executable

import re
from pathlib import Path

CANONICAL_DIVISIONS = 480


_DIV_RE = re.compile(r'(<divisions>)(\d+)(</divisions>)')
_DUR_RE = re.compile(r'(<duration>)(\d+)(</duration>)')


def normalize_xml_text(xml_text: str, *, target_divisions: int = CANONICAL_DIVISIONS) -> tuple:
    """Return (new_xml_text, stats_dict) where stats records rescale factors.

    Contract:
      - Find every <divisions>N</divisions>. For each, rewrite N ->
        target_divisions and rescale every subsequent <duration>D</duration>
        (up to the next <divisions> tag) by factor target_divisions / N.
      - Round with `int(round(D * factor))`; min 1.
      - No structural changes to elements, notes, ties, or attributes.
    """
    # Since MusicXML always has divisions before the durations they scope,
    # we do a single scan and stateful rewrite.
    parts = []
    stats = {
        'divisions_before': [],
        'divisions_after': target_divisions,
        'durations_rewritten': 0,
        'max_pre_snap_error_ticks': 0.0,
    }
    current_scale = None  # multiplier: new = old * factor
    i = 0
    tokens = re.split(r'(<divisions>\d+</divisions>|<duration>\d+</duration>)', xml_text)
    out = []
    for tok in tokens:
        m_div = _DIV_RE.fullmatch(tok)
        m_dur = _DUR_RE.fullmatch(tok)
        if m_div:
            old_n = int(m_div.group(2))
            stats['divisions_before'].append(old_n)
            current_scale = target_divisions / float(old_n)
            out.append('<divisions>' + str(target_divisions) + '</divisions>')
        elif m_dur:
            if current_scale is None:
                # No divisions seen yet — pass through unchanged.
                out.append(tok)
                continue
            old_d = int(m_dur.group(2))
            new_d_f = old_d * current_scale
            new_d = max(1, int(round(new_d_f)))
            err = abs(new_d_f - new_d)
            if err > stats['max_pre_snap_error_ticks']:
                stats['max_pre_snap_error_ticks'] = err
            stats['durations_rewritten'] += 1
            out.append('<duration>' + str(new_d) + '</duration>')
        else:
            out.append(tok)
    return ''.join(out), stats


def normalize_file(in_path, out_path, *, target_divisions: int = CANONICAL_DIVISIONS) -> dict:
    in_path = Path(in_path)
    out_path = Path(out_path)
    text = in_path.read_text(encoding='utf-8')
    new_text, stats = normalize_xml_text(text, target_divisions=target_divisions)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(new_text, encoding='utf-8')
    return stats


if __name__ == '__main__':
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('output')
    ap.add_argument('--divisions', type=int, default=CANONICAL_DIVISIONS)
    args = ap.parse_args()
    stats = normalize_file(args.input, args.output, target_divisions=args.divisions)
    print(json.dumps(stats, indent=2, sort_keys=True))
