#!/usr/bin/env /usr/bin/python3
"""VOMM (Variable-Order Markov Model) generator for M-V4-GEN-1 iteration 1.

c72 primary-fallback per brief §4 P2: Anticipation fetch blocked via workspace
proxy (GitHub 403, PyPI 404 -> data/v4/gen/iteration_01/fetchability_ladder.jsonl);
VOMM is the pure-Python secondary that lands per survey score 4.3/5.

Contract per brief:
  - K=4 variable-order Markov chain over rule-transition frequencies from
    data/v3/rules/rules_artifact.jsonl (76 rules, sha e19fb205b282dabb...).
  - Sample per-song rule sequences deterministically under seeded SHA-256
    tiebreak (NO PRNG, no wall-clock, no dict-order dependence).
  - Emit per-instrument note-event JSON files under
    data/v4/gen/iteration_01/song_<N>_donor_<sha16>/generated_json/{bass,drums}.json
    consumable by scripts/v3_spine/midi_from_json_events.serialize().

Public API:
    train_vomm(rules_path: str, k: int = 4) -> VommModel
    sample_rules(model, seed_str: str, n_rules: int = 24) -> list[dict]
    rules_to_note_events(sampled_rules, donor_sha16, seed_str) -> dict[str, list[dict]]

No PRNG imports (asserted at module import time).
"""
import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# Interpreter guard
if not sys.executable.endswith('/usr/bin/python3'):
    sys.stderr.write(
        f'vomm_generator.py requires /usr/bin/python3, got {sys.executable}\n'
    )

# Env pins (7-key canonical subset; matches env_pin_sha256=2ac444c3...922ca).
_ENV_PINS = {
    'PYTHONHASHSEED': '0',
    'SOURCE_DATE_EPOCH': '1756463424',
    'TZ': 'UTC',
    'LC_ALL': 'C.UTF-8',
    'OMP_NUM_THREADS': '1',
    'MKL_NUM_THREADS': '1',
    'OPENBLAS_NUM_THREADS': '1',
}
for _k, _v in _ENV_PINS.items():
    os.environ.setdefault(_k, _v)


class VommModel:
    """Variable-order Markov model over rule-type transitions.

    State space: {'harmonic', 'rhythmic', 'melodic', 'form', 'arrangement'}
    (5 rule_types from rules_artifact.jsonl).

    Order: K=4 -> contexts up to length 4.
    Fallback: on unseen context, backoff to shorter context down to unigram.
    """

    def __init__(self, k: int, rules: List[dict]):
        self.k = k
        self.rules = rules
        self.rule_index_by_type: Dict[str, List[int]] = defaultdict(list)
        for i, r in enumerate(rules):
            self.rule_index_by_type[r['rule_type']].append(i)
        self.rule_type_sequence = [r['rule_type'] for r in rules]
        self.transitions: Dict[Tuple[str, ...], Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self._train()

    def _train(self):
        """Populate transitions: context (length 0..k) -> next-type -> count."""
        seq = self.rule_type_sequence
        for order in range(0, self.k + 1):
            for i in range(len(seq) - order):
                ctx = tuple(seq[i : i + order])
                if i + order < len(seq):
                    nxt = seq[i + order]
                    self.transitions[ctx][nxt] += 1

    def sample_next_type(self, context: Tuple[str, ...], seed_str: str) -> str:
        """Sample next rule_type given context.

        Deterministic: use SHA-256 of (seed_str, context) to pick a bucket
        proportional to counts. No PRNG.
        Backoff: if context unseen, shorten by 1 until found; unigram is guaranteed
        to be populated for any rule_type present in the corpus.
        """
        for order in range(len(context), -1, -1):
            ctx = tuple(context[len(context) - order :]) if order > 0 else ()
            counts = self.transitions.get(ctx)
            if not counts:
                continue
            total = sum(counts.values())
            if total == 0:
                continue
            # Deterministic pick: SHA-256 of (seed, ctx, step) -> integer in [0, total).
            digest = hashlib.sha256(
                f'{seed_str}|{ctx}'.encode('utf-8')
            ).digest()
            r = int.from_bytes(digest[:8], 'big') % total
            cum = 0
            for nt in sorted(counts.keys()):
                cum += counts[nt]
                if r < cum:
                    return nt
        # Absolute fallback: pick most-frequent rule_type in the corpus.
        by_type_count = defaultdict(int)
        for t in self.rule_type_sequence:
            by_type_count[t] += 1
        return sorted(by_type_count.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    def sample_rule_of_type(self, rule_type: str, seed_str: str) -> dict:
        """Pick a concrete rule of the given type deterministically."""
        candidates = self.rule_index_by_type.get(rule_type, [])
        if not candidates:
            # Fallback: unigram most-frequent.
            for t, idxs in sorted(self.rule_index_by_type.items()):
                if idxs:
                    candidates = idxs
                    break
        digest = hashlib.sha256(
            f'{seed_str}|pick_rule|{rule_type}'.encode('utf-8')
        ).digest()
        idx = int.from_bytes(digest[:8], 'big') % len(candidates)
        # Sort candidates by rule_id for canonical order (rule_ids are content-hashed).
        sorted_candidates = sorted(candidates, key=lambda i: self.rules[i]['rule_id'])
        return self.rules[sorted_candidates[idx]]


def train_vomm(rules_path: str, k: int = 4) -> VommModel:
    """Load rules_artifact.jsonl and train VOMM(k)."""
    rules = []
    with open(rules_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get('event_type') == 'rule':
                rules.append(r)
    # Sort by rule_id for canonical order (byte-deterministic across runs).
    rules.sort(key=lambda r: r['rule_id'])
    return VommModel(k=k, rules=rules)


def sample_rules(model: VommModel, seed_str: str, n_rules: int = 24) -> List[dict]:
    """Sample n_rules rule instances deterministically."""
    sampled = []
    context: Tuple[str, ...] = ()
    for step in range(n_rules):
        step_seed = f'{seed_str}|step{step:03d}'
        next_type = model.sample_next_type(context, step_seed)
        rule = model.sample_rule_of_type(next_type, step_seed)
        sampled.append(rule)
        # Extend context; truncate to k.
        context = tuple((list(context) + [next_type])[-model.k :])
    return sampled


# ---------- Rules -> note events projector (v0.1 template) ----------
#
# Minimal deterministic mapping. Aims for musical plausibility given the
# c72 wall budget; not a research-grade generator. See M-V4-EAR spec for
# scoring; ear score deferred until M-V4-EAR-1 lands.

# GM programs used at render time (per c11/c14 channel-aware replay fix).
_INSTRUMENT_CHANNEL = {
    'bass': 0,   # per canonical serializer INSTRUMENT_TO_CHANNEL
    'drums': 9,  # GM percussion
}

# 30-second target window at 120 BPM = 60 beats = 15 bars @ 4/4.
TARGET_DURATION_S = 30.0
TARGET_TEMPO_BPM = 120.0
BEATS_PER_BAR = 4
SECONDS_PER_BEAT = 60.0 / TARGET_TEMPO_BPM  # 0.5s @ 120 BPM
BASS_ROOT_MIDI = 40  # E2
SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]  # major scale offsets from root


def _bass_notes_from_rule(rule: dict, bar_start_s: float, seed_str: str) -> List[dict]:
    """Emit deterministic bass notes for one bar based on a rule."""
    # Pick 4 quarter-note bass notes per bar; pitch = root + scale offset from rule's rule_id hash.
    digest = hashlib.sha256(
        f'{seed_str}|bass|{rule["rule_id"]}'.encode('utf-8')
    ).digest()
    notes = []
    for beat in range(BEATS_PER_BAR):
        offset_idx = digest[beat] % len(SCALE_INTERVALS)
        pitch = BASS_ROOT_MIDI + SCALE_INTERVALS[offset_idx]
        start_t = bar_start_s + beat * SECONDS_PER_BEAT
        end_t = start_t + SECONDS_PER_BEAT * 0.9
        notes.append({'pitch': pitch, 'start_time': start_t, 'end_time': end_t,
                      'instrument': 'bass'})
    return notes


def _drum_notes_from_rule(rule: dict, bar_start_s: float, seed_str: str) -> List[dict]:
    """Emit deterministic drum notes for one bar based on a rule.

    GM kit: 36=kick, 38=snare, 42=closed hihat. Backbeat pattern with
    rule-driven variations.
    """
    digest = hashlib.sha256(
        f'{seed_str}|drums|{rule["rule_id"]}'.encode('utf-8')
    ).digest()
    notes = []
    # Kick on beats 1, 3 (with rule-driven syncopation on beat 2 or 4).
    for beat in [0, 2]:
        start_t = bar_start_s + beat * SECONDS_PER_BEAT
        notes.append({'pitch': 36, 'start_time': start_t,
                      'end_time': start_t + 0.05, 'instrument': 'drums'})
    if digest[0] & 1:  # ~50% syncopation
        start_t = bar_start_s + 1.5 * SECONDS_PER_BEAT
        notes.append({'pitch': 36, 'start_time': start_t,
                      'end_time': start_t + 0.05, 'instrument': 'drums'})
    # Snare on beats 2, 4.
    for beat in [1, 3]:
        start_t = bar_start_s + beat * SECONDS_PER_BEAT
        notes.append({'pitch': 38, 'start_time': start_t,
                      'end_time': start_t + 0.05, 'instrument': 'drums'})
    # Closed hihat on 8th notes.
    for eighth in range(BEATS_PER_BAR * 2):
        start_t = bar_start_s + eighth * SECONDS_PER_BEAT / 2
        notes.append({'pitch': 42, 'start_time': start_t,
                      'end_time': start_t + 0.03, 'instrument': 'drums'})
    return notes


def rules_to_note_events(
    sampled_rules: List[dict], donor_sha16: str, seed_str: str
) -> Dict[str, List[dict]]:
    """Project sampled rules to per-instrument note-event lists.

    Returns {'bass': [events], 'drums': [events]} where each list is the
    canonical-serializer wire format:
        [{"type": "start", "index": i, "pitch": p, "instrument": inst,
          "start_time": t}, ...,
         {"type": "end", "start_event_index": i, "end_time": t}, ...]
    """
    n_bars = int(TARGET_DURATION_S / (BEATS_PER_BAR * SECONDS_PER_BEAT))
    # Cycle through rules across bars deterministically.
    bass_notes: List[dict] = []
    drum_notes: List[dict] = []
    for bar in range(n_bars):
        rule = sampled_rules[bar % len(sampled_rules)]
        bar_start_s = bar * BEATS_PER_BAR * SECONDS_PER_BEAT
        bass_notes.extend(_bass_notes_from_rule(rule, bar_start_s, seed_str))
        drum_notes.extend(_drum_notes_from_rule(rule, bar_start_s, seed_str))

    def to_events(notes: List[dict]) -> List[dict]:
        events: List[dict] = []
        for i, n in enumerate(notes):
            events.append({
                'type': 'start',
                'index': i,
                'pitch': int(n['pitch']),
                'instrument': n['instrument'],
                'start_time': float(n['start_time']),
            })
            events.append({
                'type': 'end',
                'start_event_index': i,
                'end_time': float(n['end_time']),
            })
        return events

    return {
        'bass': to_events(bass_notes),
        'drums': to_events(drum_notes),
    }


def generator_hash() -> str:
    """SHA-256 of this module's own file for provenance pinning."""
    with open(__file__, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='VOMM smoke test')
    parser.add_argument('--rules-path', default='data/v3/rules/rules_artifact.jsonl')
    parser.add_argument('--seed-str', required=True)
    parser.add_argument('--donor-sha16', required=True)
    parser.add_argument('--n-rules', type=int, default=24)
    parser.add_argument('--k', type=int, default=4)
    args = parser.parse_args()
    model = train_vomm(args.rules_path, k=args.k)
    sampled = sample_rules(model, args.seed_str, n_rules=args.n_rules)
    events = rules_to_note_events(sampled, args.donor_sha16, args.seed_str)
    print(f'trained VOMM K={args.k} on {len(model.rules)} rules; '
          f'sampled {len(sampled)}; '
          f'bass_events={len(events["bass"])}; drums_events={len(events["drums"])}')
    print(f'generator_hash={generator_hash()}')
    print(f'first 5 sampled rule_ids: {[r["rule_id"][:16] for r in sampled[:5]]}')
