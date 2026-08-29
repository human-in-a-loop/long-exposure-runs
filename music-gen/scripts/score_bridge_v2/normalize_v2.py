#!/usr/bin/python3
# c39: Full P2 normalizer — extends c38 normalize.py with per-note
# <type>/<dot/> rewrite (and bounded tuplet insertion).
# Read-only import of c38 normalize.py (no edits to c38 anchor).
#
# Milestone: M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2
# Author: cyd7bevdr@mozmail.com, cycle 39.
import sys
assert sys.executable == '/usr/bin/python3', sys.executable

import re
from pathlib import Path

# READ-ONLY import of c38 anchor
from scripts.score_bridge_v2 import normalize as _normalize_v1

CANONICAL_DIVISIONS = 960  # supports 256th as integer ticks (=15)

# Standard MusicXML <type> base durations in quarter-length units.
TYPE_BASE_QL = {
    'whole': 4.0,
    'half': 2.0,
    'quarter': 1.0,
    'eighth': 0.5,
    '16th': 0.25,
    '32nd': 0.125,
    '64th': 0.0625,
    '128th': 0.03125,
    '256th': 0.015625,
}

# Frozen bounded tuplet ratios (actual, normal) per rubric §6 step 4.
TUPLET_RATIOS = [(3, 2), (5, 4), (7, 4), (6, 4)]


def build_duration_map(divs: int = CANONICAL_DIVISIONS):
    """Map integer ticks → (type_name, dot_count) for clean matches.

    Includes dots 0..3. Prefers fewer dots on tick-collision (rare/never
    for standard MusicXML types).
    """
    m = {}
    for name, base_ql in TYPE_BASE_QL.items():
        for dots in [0, 1, 2, 3]:
            mult = 2 - (2 ** -dots)
            ticks_f = base_ql * divs * mult
            if ticks_f == int(ticks_f):
                ticks = int(ticks_f)
                if ticks not in m:
                    m[ticks] = (name, dots)
    return m


def try_tuplet(duration_ticks: int, divs: int = CANONICAL_DIVISIONS):
    """Try to express duration as (type, dots, actual, normal) tuplet.

    Returns (type_name, dot_count, actual, normal) or None.
    Bounded ratios per rubric.
    """
    for actual, normal in TUPLET_RATIOS:
        # tuplet duration = base_type_ticks * (normal/actual)
        # so base_type_ticks = duration_ticks * (actual/normal)
        base_target_f = duration_ticks * actual / normal
        if abs(base_target_f - round(base_target_f)) > 1e-9:
            continue
        base_target = int(round(base_target_f))
        for name, base_ql in TYPE_BASE_QL.items():
            for dots in [0, 1, 2, 3]:
                mult = 2 - (2 ** -dots)
                type_ticks_f = base_ql * divs * mult
                if type_ticks_f == int(type_ticks_f) and int(type_ticks_f) == base_target:
                    return (name, dots, actual, normal)
    return None


# Regex: full <note ...>...</note> block (non-greedy).
_NOTE_RE = re.compile(r'(<note\b[^>]*>)(.*?)(</note>)', re.DOTALL)
_DUR_INNER_RE = re.compile(r'<duration>(\d+)</duration>')
_TYPE_INNER_RE = re.compile(r'<type>([^<]+)</type>')
_DOT_INNER_RE = re.compile(r'<dot\s*/>')
_TIME_MOD_RE = re.compile(r'<time-modification>.*?</time-modification>', re.DOTALL)
_GRACE_RE = re.compile(r'<grace\s*/>')


def _rewrite_note_body(body: str, duration_map: dict, stats: dict, note_index: int) -> str:
    """Rewrite one <note> element's inner XML: fix <type> and <dot/>s.
    Body preserves leading/trailing whitespace by keeping the regex-matched
    interior string.
    """
    if _GRACE_RE.search(body):
        stats['grace_notes'] += 1
        return body  # grace notes have no <duration>; leave untouched
    m_dur = _DUR_INNER_RE.search(body)
    if not m_dur:
        return body
    d = int(m_dur.group(1))

    if d in duration_map:
        type_name, dot_count = duration_map[d]
        tuplet = None
    else:
        tuplet = try_tuplet(d)
        if tuplet:
            type_name, dot_count, _tup_a, _tup_n = tuplet
            stats['tuplet_insertions'] += 1
        else:
            type_name, dot_count = 'quarter', 0
            stats['forced_quarter'] += 1
            stats['reconstruction_log'].append({
                'note_index': note_index,
                'duration_ticks': d,
                'reason': 'no_clean_type_dot_or_tuplet',
            })

    # Remove existing <dot/>s.
    n_dots_removed = 0
    while True:
        new_body, k = _DOT_INNER_RE.subn('', body, count=1)
        if k == 0:
            break
        body = new_body
        n_dots_removed += 1

    # Rewrite / inject <type>.
    m_type = _TYPE_INNER_RE.search(body)
    if m_type:
        old_type_name = m_type.group(1)
        if old_type_name != type_name:
            body = body[:m_type.start()] + f'<type>{type_name}</type>' + body[m_type.end():]
            stats['type_rewrites'] += 1
        m_type = _TYPE_INNER_RE.search(body)
        type_end = m_type.end()
    else:
        # Inject <type> after <duration> (and any immediately-following
        # <tie type="..."/> elements).
        m_dur = _DUR_INNER_RE.search(body)
        insert_at = m_dur.end()
        # Skip immediately-following <tie ../> siblings.
        tail = body[insert_at:]
        m_ties = re.match(r'(\s*<tie\b[^/]*/>)+', tail)
        if m_ties:
            insert_at += m_ties.end()
        # Preserve the trailing newline+indent style of the enclosing element.
        # Detect indentation from the line containing <duration>.
        line_start = body.rfind('\n', 0, m_dur.start()) + 1
        indent = ''
        j = line_start
        while j < len(body) and body[j] in ' \t':
            indent += body[j]
            j += 1
        insertion = f'\n{indent}<type>{type_name}</type>'
        body = body[:insert_at] + insertion + body[insert_at:]
        stats['type_rewrites'] += 1
        # Re-find <type>.
        m_type = _TYPE_INNER_RE.search(body)
        type_end = m_type.end()

    # Insert dot_count new <dot/> after <type>.
    if dot_count > 0:
        line_start = body.rfind('\n', 0, m_type.start()) + 1
        indent = ''
        j = line_start
        while j < len(body) and body[j] in ' \t':
            indent += body[j]
            j += 1
        dot_str = ''
        for _ in range(dot_count):
            dot_str += f'\n{indent}<dot/>'
            stats['dot_injections'] += 1
        body = body[:type_end] + dot_str + body[type_end:]

    return body


def normalize_v2_xml_text(xml_text: str, *, target_divisions: int = CANONICAL_DIVISIONS):
    """Full c39 normalize: divisions/duration + type+dot rewrite.

    Returns (new_xml_text, stats_dict).
    """
    v1_text, v1_stats = _normalize_v1.normalize_xml_text(
        xml_text, target_divisions=target_divisions)
    dmap = build_duration_map(target_divisions)
    stats = {
        'v1': v1_stats,
        'canonical_divisions': target_divisions,
        'duration_map_size': len(dmap),
        'notes_scanned': 0,
        'grace_notes': 0,
        'type_rewrites': 0,
        'dot_injections': 0,
        'tuplet_insertions': 0,
        'forced_quarter': 0,
        'reconstruction_log': [],
    }

    counter = {'i': 0}

    def _sub(match):
        head, body, tail = match.group(1), match.group(2), match.group(3)
        stats['notes_scanned'] += 1
        new_body = _rewrite_note_body(body, dmap, stats, counter['i'])
        counter['i'] += 1
        return head + new_body + tail

    new_text = _NOTE_RE.sub(_sub, v1_text)
    return new_text, stats


def normalize_v2_file(in_path, out_path, *, target_divisions: int = CANONICAL_DIVISIONS):
    in_path = Path(in_path)
    out_path = Path(out_path)
    text = in_path.read_text(encoding='utf-8')
    new_text, stats = normalize_v2_xml_text(text, target_divisions=target_divisions)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(new_text, encoding='utf-8')
    return stats


if __name__ == '__main__':
    import argparse
    import json
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('output')
    ap.add_argument('--divisions', type=int, default=CANONICAL_DIVISIONS)
    args = ap.parse_args()
    stats = normalize_v2_file(args.input, args.output, target_divisions=args.divisions)
    # Strip verbose reconstruction_log for stdout; keep counts.
    summary = {k: v for k, v in stats.items() if k != 'reconstruction_log'}
    summary['reconstruction_log_count'] = len(stats['reconstruction_log'])
    print(json.dumps(summary, indent=2, sort_keys=True))
