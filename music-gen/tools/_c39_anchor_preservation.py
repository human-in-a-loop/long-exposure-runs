#!/usr/bin/python3
"""Emit data/score_bridge_real_audio_normalizer_v2/anchor_preservation.json."""
import hashlib
import json
import pathlib

ANCHORS = [
    # c8 score bridge
    ('scripts/score/bridge.py',
     'ed73482270db9f702ec082b597b95da9d92c8e80198a4cc0a8ac394aa536dbba'),
    # c37 clone-0 recreate_v0 anchors
    ('scripts/recreate_v0/run_pipeline.py',
     '9d7fa37e9466d562f5d767219303211b9c547d05b2ad2b24167049aa9cb2078b'),
    ('scripts/recreate_v0/run_all.py', None),
    ('scripts/recreate_v0/select_song.py', None),
    ('scripts/recreate_v0/__init__.py', None),
    # c37 fixture
    ('data/recreate_v0/per_stage/06_score/merged.musicxml',
     '95de5356fc127e8ff2b3c5153a950b35ddd4836b1ec1f40d658f41ebb73e1592'),
    # c38 score_bridge_v2 (all 8 files)
    ('scripts/score_bridge_v2/__init__.py', None),
    ('scripts/score_bridge_v2/_shared.py', None),
    ('scripts/score_bridge_v2/normalize.py',
     '23b852146e681b9fd0ce317b388d69af16c5abd5131086435659bf2712d5656b'),
    ('scripts/score_bridge_v2/probe_p1_mscore3_flags.py', None),
    ('scripts/score_bridge_v2/probe_p2_normalizer.py', None),
    ('scripts/score_bridge_v2/probe_p3_alternative_backends.py', None),
    ('scripts/score_bridge_v2/verdict.py', None),
    ('scripts/score_bridge_v2/run_all.py', None),
    # c38 data anchors
    ('data/score_bridge_real_audio/rubric_hash.txt', None),
    ('data/score_bridge_real_audio/verdict.json', None),
    ('data/score_bridge_real_audio/anchor_preservation.json', None),
    # c38 docs
    ('docs/score_bridge_real_audio_quantization_rubric.md',
     'bd5ce7d99cfd0a2bb65793e8cc3a93d91474c8ba6e598f0c570beccbd8427f88'),
    ('docs/score_bridge_real_audio_quantization_report.md', None),
]

root = pathlib.Path('.').resolve()
results = []
for rel, expected in ANCHORS:
    p = root / rel
    b = p.read_bytes()
    actual = hashlib.sha256(b).hexdigest()
    entry = {
        'path': rel,
        'sha256': actual,
        'bytes': len(b),
        'expected_sha256': expected,
    }
    if expected is not None:
        entry['byte_equal_to_expected'] = (actual == expected)
    else:
        entry['byte_equal_to_expected'] = None  # snapshot-only
    results.append(entry)

out = {
    'anchor_count': len(results),
    'anchors': results,
    'all_expected_match': all(
        r['byte_equal_to_expected'] is not False for r in results
    ),
    'expected_verified_count': sum(
        1 for r in results if r['byte_equal_to_expected'] is True
    ),
}
p_out = pathlib.Path(
    'data/score_bridge_real_audio_normalizer_v2/anchor_preservation.json'
)
p_out.write_text(json.dumps(out, indent=2, sort_keys=True))
print(json.dumps(out, indent=2, sort_keys=True))
