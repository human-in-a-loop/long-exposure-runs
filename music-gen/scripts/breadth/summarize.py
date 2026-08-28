#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:30:00Z
# cycle: 10
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-INGEST-1/breadth-second-seeds
# ---
"""Cross-seed aggregation for the pipeline-breadth cycle.

Reads each seed's stage_manifest.jsonl + panel.tsv + summary.json and
emits data/breadth/summary.tsv (one row per seed) + a baseline row for
synth_030s pulled from data/tex/stage_by_stage_synth_030s.tsv.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

assert sys.executable == '/usr/bin/python3', sys.executable

ROOT = Path('/home/user/long-exposure-runs/music-gen')
BREADTH_ROOT = ROOT / 'data' / 'breadth'
OUT_TSV = BREADTH_ROOT / 'summary.tsv'

SEEDS = ['seed_mid_50s', 'synth_060s']

COLS = [
    'seed_id', 'duration_s', 'chunk_count',
    'dominant_class', 'dominant_class_prob',
    'notes_drums', 'notes_bass', 'notes_other',
    'panel_mel_l1_db', 'panel_spectral_centroid_rmse_hz',
    'panel_rms_env_rmse', 'panel_lufs_m_rmse_lu',
    'panel_embedding_cosine', 'embedding_rung',
    'provenance_class', 'all_stages_completed',
]


def _read_manifest(seed_dir: Path):
    lines = (seed_dir / 'stage_manifest.jsonl').read_text().splitlines()
    return [json.loads(l) for l in lines if l.strip()]


def _find(manifest, name):
    for m in manifest:
        if m.get('name') == name:
            return m
    return {}


def _panel_row(seed_dir: Path):
    tsv = seed_dir / 'panel.tsv'
    if not tsv.exists():
        return None
    lines = tsv.read_text().splitlines()
    if len(lines) < 2:
        return None
    headers = lines[0].split('\t')
    values = lines[1].split('\t')
    return dict(zip(headers, values))


def _provenance(seed_id: str) -> str:
    if seed_id.startswith('seed_'):
        return 'synth_seed_gen'
    if seed_id.startswith('synth_'):
        return 'synth_ground_truth'
    return 'unknown'


def summarize_one(seed_id: str) -> dict:
    seed_dir = BREADTH_ROOT / seed_id
    manifest = _read_manifest(seed_dir)
    prep = _find(manifest, 'prepare_audio')
    chunker = _find(manifest, 'chunker')
    classifier = _find(manifest, 'classifier')
    bp = _find(manifest, 'basic_pitch')
    panel = _panel_row(seed_dir)
    summary_json = json.loads((seed_dir / 'summary.json').read_text())
    stages = summary_json.get('stages', {})

    per_stem = (bp.get('per_stem') if bp.get('ok') else {}) or {}

    def _n(k):
        d = per_stem.get(k, {})
        return d.get('n_notes', 'null') if d.get('ok') else 'null'

    # Duration inferred from prepare_audio (n samples * 1/44100)
    # More reliably: read soundfile info on the original wav.
    import soundfile as sf
    orig = seed_dir / 'original.wav'
    dur = float(sf.info(str(orig)).duration) if orig.exists() else -1.0

    row = dict(
        seed_id=seed_id,
        duration_s=f'{dur:.3f}',
        chunk_count=chunker.get('chunk_count', 'null'),
        dominant_class=classifier.get('dominant_class', 'null'),
        dominant_class_prob=f"{classifier.get('dominant_class_prob', 0):.4f}"
                            if classifier.get('ok') else 'null',
        notes_drums=_n('drums'),
        notes_bass=_n('bass'),
        notes_other=_n('other'),
        panel_mel_l1_db=(panel or {}).get('mel_l1_db', 'null'),
        panel_spectral_centroid_rmse_hz=(panel or {}).get('spectral_centroid_rmse_hz', 'null'),
        panel_rms_env_rmse=(panel or {}).get('rms_env_rmse', 'null'),
        panel_lufs_m_rmse_lu=(panel or {}).get('lufs_m_rmse_lu', 'null'),
        panel_embedding_cosine=(panel or {}).get('embedding_cosine_distance', 'null'),
        embedding_rung=(panel or {}).get('embedding_rung', 'null'),
        provenance_class=_provenance(seed_id),
        all_stages_completed='true' if summary_json.get('all_ok') else 'false',
    )
    return row


def baseline_row() -> dict:
    """Pull the synth_030s original-vs-bare_midi row from cycle 9."""
    src = ROOT / 'data/tex/stage_by_stage_synth_030s.tsv'
    if not src.exists():
        return None
    lines = src.read_text().splitlines()
    headers = lines[0].split('\t')
    for l in lines[1:]:
        vals = l.split('\t')
        d = dict(zip(headers, vals))
        if d.get('a_stage') == 'original' and d.get('b_stage') == 'bare_midi':
            return dict(
                seed_id='synth_030s (baseline, cycle 9)',
                duration_s='30.000',
                chunk_count='null',
                dominant_class='null',
                dominant_class_prob='null',
                notes_drums='null',
                notes_bass='null',
                notes_other='null',
                panel_mel_l1_db=d.get('mel_l1_db', 'null'),
                panel_spectral_centroid_rmse_hz=d.get('spectral_centroid_rmse_hz', 'null'),
                panel_rms_env_rmse=d.get('rms_env_rmse', 'null'),
                panel_lufs_m_rmse_lu=d.get('lufs_m_rmse_lu', 'null'),
                panel_embedding_cosine=d.get('embedding_cosine_distance', 'null'),
                embedding_rung=d.get('embedding_rung', 'null'),
                provenance_class='synth_ground_truth',
                all_stages_completed='true',
            )
    return None


def main() -> None:
    rows = [summarize_one(s) for s in SEEDS]
    base = baseline_row()
    if base:
        rows.append(base)
    with OUT_TSV.open('w') as fh:
        fh.write('\t'.join(COLS) + '\n')
        for r in rows:
            fh.write('\t'.join(str(r[c]) for c in COLS) + '\n')
    print(f'wrote {OUT_TSV}')
    for r in rows:
        print(f"  {r['seed_id']:35s} mel_l1_db={r['panel_mel_l1_db']:>10s} "
              f"lufs_rmse={r['panel_lufs_m_rmse_lu']:>10s} "
              f"embed_cos={r['panel_embedding_cosine']:>10s}")


if __name__ == '__main__':
    main()
