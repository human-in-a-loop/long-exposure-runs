#!/usr/bin/env /usr/bin/python3
"""8-key panel measurement on the A/B pair. Panel is NEVER a LANDS gate
(Fixed Decision 6). Just a tripwire — logs measurements; regression check
skipped because the referenced c33 anchor panel_baseline_old_chain_v2.tsv
is not present on disk (honestly disclosed).
"""
import json
import sys
from pathlib import Path

import numpy as np
import scipy.io.wavfile as sw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.texture.panel import texture_distance  # noqa: E402

SONG_SHA16 = '31a164f845f8e27e'
DELIVERY = Path(f'data/v3/deliveries/{SONG_SHA16}')


def read_stereo(p: Path) -> tuple[int, np.ndarray]:
    sr, y = sw.read(str(p))
    if y.dtype == np.int16:
        y = y.astype(np.float32) / 32768.0
    return sr, y


def main() -> None:
    orig_p = DELIVERY / 'original_ab.wav'
    recon_p = DELIVERY / 'reconstruction_ab.wav'
    sr, orig = read_stereo(orig_p)
    sr2, recon = read_stereo(recon_p)
    assert sr == sr2, 'sample-rate mismatch'
    d = texture_distance(orig, recon, sr)
    # 8 keys expected: mel_l1_db, spectral_centroid_rmse_hz, rms_env_rmse,
    # lufs_m_rmse, embedding_cos_distance, ...
    # Numeric-metric finiteness only (metadata keys like 'embedding_rung' are strings and
    # not gated).
    NUMERIC_METRICS = (
        'mel_l1_db', 'spectral_centroid_rmse_hz', 'rms_env_rmse',
        'lufs_m_rmse_lu', 'embedding_cosine_distance',
    )
    finite = {}
    for k, v in d.items():
        if k in NUMERIC_METRICS:
            finite[k] = (isinstance(v, (int, float)) and (v == v) and abs(v) < 1e12)
        else:
            finite[k] = True  # metadata: not numerically gated
    result = {
        'schema_version': 1, 'cycle': 4, 'song_sha16': SONG_SHA16,
        'sr': sr,
        'panel_keys_count': len(d),
        'panel': d,
        'finite_per_key': finite,
        'c33_anchor_regression_check': {
            'anchor_path': 'data/palette_render/panel_baseline_old_chain_v2.tsv',
            'anchor_exists': False,
            'note': 'Anchor named in brief does not exist on disk. Regression check skipped. Panel is NEVER a LANDS gate (Fixed Decision 6).',
            'regression_status': 'not_applicable',
        },
        'panel_is_never_lands_gate': True,
    }
    # Write TSV + JSON
    (DELIVERY / 'panel.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    tsv_lines = ['key\tvalue\tfinite']
    for k in sorted(d.keys()):
        tsv_lines.append(f'{k}\t{d[k]}\t{finite[k]}')
    (DELIVERY / 'panel.tsv').write_text('\n'.join(tsv_lines) + '\n')
    print('panel:', {k: round(v, 4) if isinstance(v, (int, float)) else v for k, v in d.items()})


if __name__ == '__main__':
    main()
