#!/usr/bin/env python3
"""One-shot finding emitter for verify_4of5 Slice D."""
import json
import time
from pathlib import Path

findings_path = Path('/home/user/long-exposure-runs/music-gen/audits/final/findings.jsonl')
ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

new_finding = {
    'ts': ts,
    'stage': 'verify_4of5',
    'slice': 'D',
    'milestone_id': 'M-V4-PROFILES-1/cg-bass-sf2-replay-proof-v2',
    'finding_kind': 'por_anchor_drift',
    'severity': 'MINOR',
    'narrative': (
        'POR c4 row pins bass_v2.replay_proof.json at SHA-256 '
        '86948709746b966a766f731aa0d118e52a2d74dec716c99f742404d2a725ec7d. '
        'On-disk full SHA-256 is '
        '4b9eea98052d6b2f54dcc7b87af334614c5ad56fb8c159eb6563c21533d5817f '
        '(no first-16-hex collision, full divergence). '
        'File is present and substantively coherent: internal '
        'run1_sha256 == run2_sha256 == '
        '832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5 '
        '(byte-identical to c2 bass replay proof render SHA per POR c4 narrative), '
        'verdict=REPLAY_PROOF_HOLDS, env_pin_sha256 canonical 7-key. '
        'Substantive REPLAY_PROOF claim in POR narrative is TRUE; only the '
        'FILE-LEVEL SHA-256 anchor in POR text does not match on-disk. '
        'Same POR-transcription-drift pattern class as c12 audit disclosure for '
        'drums.json + drums.replay_proof.json first-16-hex-collision cases, '
        'though here the divergence is full-SHA (no prefix collision). '
        'Delta-audit new: file-level POR anchor drift only; no substantive '
        'REPLAY_PROOF invalidation.'
    ),
    'on_disk_full_sha': '4b9eea98052d6b2f54dcc7b87af334614c5ad56fb8c159eb6563c21533d5817f',
    'por_pinned_full_sha': '86948709746b966a766f731aa0d118e52a2d74dec716c99f742404d2a725ec7d',
    'reconcile': False,
}

with findings_path.open('a') as fh:
    fh.write(json.dumps(new_finding) + '\n')

print('Appended 1 MINOR finding to', findings_path)
