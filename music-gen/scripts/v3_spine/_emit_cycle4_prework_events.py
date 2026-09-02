"""One-shot emitter for cycle-4 pre-work ledger events (spec + rubric-v2 + option-a-adopted)."""
from pathlib import Path

from long_exposure.workspace_bootstrap import append_ledger_event


def main() -> None:
    ws = Path('.')
    evs = [
        {
            'ts': '2026-09-02T00:00:01Z',
            'run_id': 'run-2026-09-02T000000Z',
            'cycle': 59,
            'agent': 'worker',
            'milestone_id': 'M-V3-SPINE-1/canonical-serializer-spec-committed',
            'status': 'validated',
            'confidence': {
                'level': 'high',
                'rationale': 'doc landed on disk with SHA pinned to three-way chain anchor before any script under scripts/v3_spine/midi_from_json_events*',
                'assessor': 'worker',
            },
            'narrative': (
                'docs/v3_spine_canonical_midi_serializer_spec.md landed; SHA pinned to '
                'data/v3_spine/canonical_serializer_spec_hash.txt. Specifies PPQ=480, '
                'sort key (tick, channel, pitch, event_kind) with on-before-off, '
                'mido==1.3.3 pin (via importlib.metadata), tempo/TS meta from drums-stem '
                'detected tempo with rc5 baseline fallback, JSON canonicalization for cache '
                'invariance, atomic write via tempfile+os.replace (mido 1.3.3 lacks atomic_write kwarg). '
                'Public API serialize(json_events_path, out_midi_path, tempo_bpm, time_signature).'
            ),
            'artifacts': [
                'docs/v3_spine_canonical_midi_serializer_spec.md',
                'data/v3_spine/canonical_serializer_spec_hash.txt',
            ],
        },
        {
            'ts': '2026-09-02T00:00:02Z',
            'run_id': 'run-2026-09-02T000000Z',
            'cycle': 59,
            'agent': 'worker',
            'milestone_id': 'M-V3-SPINE-1/rubric-v2-committed',
            'status': 'validated',
            'confidence': {
                'level': 'high',
                'rationale': 'v2 doc landed with SHA pinned; three-way chain anchor established',
                'assessor': 'worker',
            },
            'narrative': (
                'docs/v3_spine_rubric_v2.md landed; SHA pinned to data/v3_spine/rubric_hash_v2.txt. '
                'v1 rubric preserved as READ-ONLY historical anchor byte-identical pre==post. '
                'Frozen 3-verdict rubric unchanged in structure; sub-clause (b) rewritten to '
                'gate byte-determinism x2 on JSON events + canonicalized MIDI (three surfaces), '
                'demote MuScriptor --format midi to non_factor_debug sidecar.'
            ),
            'supersedes_path': 'docs/v3_spine_rubric.md',
            'artifacts': [
                'docs/v3_spine_rubric_v2.md',
                'data/v3_spine/rubric_hash_v2.txt',
            ],
        },
        {
            'ts': '2026-09-02T00:00:03Z',
            'run_id': 'run-2026-09-02T000000Z',
            'cycle': 59,
            'agent': 'worker',
            'milestone_id': 'M-V3-SPINE-1/option-a-adopted',
            'status': 'validated',
            'confidence': {
                'level': 'high',
                'rationale': 'operator directive verbatim recorded; sub-leaves pinned; unblock signal fired',
                'assessor': 'worker',
            },
            'narrative': (
                'M-V3-SPINE-1 unblocked under OPTION A. Sub-leaves this cycle: '
                'canonical-serializer-spec-committed, rubric-v2-committed, '
                'anchor-preservation-pre-v2-verified, muscriptor-json-determinism-completed, '
                'canonical-serializer-implemented, canonical-midi-determinism-verified, '
                'tempo-map-chosen, gm-program-map-v3-extended, per-stem-midi-merged, '
                'full-mix-reconciliation-emitted, render-plus-vocals-overlay, mix-match-applied, '
                'ab-delivery-emitted, panel-regression-checked, verdict-v2-emitted '
                '(status action_required with blocked_on_operator flag), '
                'anchor-preservation-post-v2-verified.'
            ),
            'artifacts': [
                'docs/v3_spine_canonical_midi_serializer_spec.md',
                'docs/v3_spine_rubric_v2.md',
            ],
        },
    ]
    for ev in evs:
        append_ledger_event(ws, ev)
        print('ok', ev['milestone_id'])


if __name__ == '__main__':
    main()
