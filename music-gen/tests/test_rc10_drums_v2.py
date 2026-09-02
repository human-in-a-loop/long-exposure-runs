#!/usr/bin/env /usr/bin/python3
"""c55 clone-0 RC10 drums v2 test suite. 15 cases minimum."""
import hashlib
import json
import re
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WS))


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def test_01_rubric_doc_mtime_before_scripts():
    """Hard: rubric doc mtime < every .py under scripts/recreate_v2/rc10_drums_v2/."""
    doc = WS / 'docs/rc10_drums_v2_rubric.md'
    assert doc.exists(), "rubric doc missing"
    doc_mtime = doc.stat().st_mtime
    scripts = list((WS / 'scripts/recreate_v2/rc10_drums_v2').glob('*.py'))
    assert len(scripts) >= 3, f"expected ≥3 scripts, got {len(scripts)}"
    for p in scripts:
        if p.name == '__init__.py':
            continue
        assert doc_mtime < p.stat().st_mtime, (
            f"rubric mtime {doc_mtime} >= script mtime {p.stat().st_mtime} "
            f"for {p}"
        )


def test_02_three_way_rubric_hash_byte_equality():
    doc_sha = _sha(WS / 'docs/rc10_drums_v2_rubric.md')
    file_sha = (WS / 'data/rc10_drums_v2_impl/rubric_hash.txt').read_text().strip()
    verdict = json.loads((WS / 'data/rc10_drums_v2_impl/verdict.json').read_text())
    assert doc_sha == file_sha == verdict['rubric_hash'], (
        f"three-way mismatch: doc={doc_sha[:16]} file={file_sha[:16]} "
        f"verdict={verdict['rubric_hash'][:16]}"
    )


def test_03_verdict_in_frozen_enum():
    v = json.loads((WS / 'data/rc10_drums_v2_impl/verdict.json').read_text())
    assert v['verdict'] in {
        'RC10_DRUMS_V2_LANDS', 'RC10_DRUMS_V2_PARTIAL', 'RC10_DRUMS_V2_FAILS',
    }, f"unknown verdict {v['verdict']!r}"


def test_04_byte_determinism_holds():
    b = json.loads((WS / 'data/rc10_drums_v2_impl/byte_determinism.json').read_text())
    assert b['byte_determinism_holds'] is True
    assert b['n_mismatch'] == 0
    assert b['n_tracked_files'] >= 30, f"expected ≥30, got {b['n_tracked_files']}"


def test_05_anchor_preservation_holds():
    a = json.loads((WS / 'data/rc10_drums_v2_impl/anchor_preservation.json').read_text())
    assert a['preservation_holds'] is True, (
        f"anchors modified: {[k for k,v in a['anchors'].items() if v['status']!='byte_identical']}"
    )
    assert a['n_entries'] >= 25, f"want ≥25 anchors, got {a['n_entries']}"


def test_06_c54_v1_rubric_untouched():
    sha = _sha(WS / 'docs/rc10_drums_bass_rubric.md')
    assert sha == 'a79bee01b4c97a1282f476a01915f4f9119fa23d369e5be2b0b72fbee05fd919'


def test_07_c50_v2_rubric_untouched():
    sha = _sha(WS / 'docs/m_recreate_2_accurate_small_set_rubric_v2.md')
    assert sha == '0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f'


def test_08_c49_v1_rubric_untouched():
    sha = _sha(WS / 'docs/m_recreate_2_accurate_small_set_rubric.md')
    assert sha == '958ade3886eba560df284878ff5d351e3f6186159ed598f68b82fc7c3fe58b9d'


def test_09_c33_render_stem_untouched():
    sha = _sha(WS / 'scripts/palette_render/render_stem.py')
    assert sha == '214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b'


def test_10_no_prng_except_gmm_random_state_0():
    """AST-grep style: no PRNG imports/calls except allowlist."""
    forbidden = re.compile(
        r'\b(random\.random|random\.randint|random\.choice|random\.seed|'
        r'np\.random\.|numpy\.random\.|torch\.rand|tf\.random)\b'
    )
    for p in (WS / 'scripts/recreate_v2/rc10_drums_v2').glob('*.py'):
        text = p.read_text()
        for m in forbidden.finditer(text):
            raise AssertionError(f"forbidden PRNG in {p}: {m.group(0)}")
    # allow GMM's single-site random_state=0 (in actual code, not the
    # commented allowlist-explanation on the import line)
    gmm_text = (WS / 'scripts/recreate_v2/rc10_drums_v2/gmm_classifier.py').read_text()
    assert 'random_state=0' in gmm_text
    # count non-comment lines only
    code_lines = [ln for ln in gmm_text.split('\n')
                  if 'random_state=' in ln and not ln.lstrip().startswith('#')
                  and '#' not in ln.split('random_state=')[0][-2:]]
    # single actual call-site (line ~53); the import-line mention is in a trailing comment
    assert 'random_state=0' in ''.join(code_lines), (
        "GMM random_state=0 must appear in code"
    )


def test_11_no_sidecar_nonfactor_import():
    for p in (WS / 'scripts/recreate_v2/rc10_drums_v2').glob('*.py'):
        text = p.read_text()
        assert 'sidecar_nonfactor' not in text, (
            f"forbidden sidecar_nonfactor import in {p}"
        )


def test_12_interpreter_guard_present():
    """/usr/bin/python3 guard on top-level scripts."""
    for name in ('run_all.py', '_relative_features.py', 'gmm_classifier.py'):
        text = (WS / 'scripts/recreate_v2/rc10_drums_v2' / name).read_text()
        assert '/usr/bin/python3' in text, f"missing interpreter guard in {name}"


def test_13_c48_env_flag_defaults_off():
    """os.environ.setdefault used (not overwrite)."""
    text = (WS / 'scripts/recreate_v2/rc10_drums_v2/run_all.py').read_text()
    for flag in ('PYTHONHASHSEED', 'SOURCE_DATE_EPOCH', 'TZ', 'LC_ALL',
                 'OPENBLAS_NUM_THREADS'):
        assert f'os.environ.setdefault("{flag}"' in text, (
            f"missing setdefault for {flag}"
        )


def test_14_ab_pairs_35_files_present():
    """5 songs × 7 files = 35."""
    total = 0
    for sha16 in ['31a164f845f8e27e', 'cdd2717e52820ff6', '51e433ade2a845e1',
                  '252eb21ce7df7328', '88d247468cb6d49f']:
        d = WS / 'data/recreate_v2/ab_pairs' / sha16 / 'drums' / 'iter_1'
        for name in ('original.wav', 'kick_only.wav', 'snare_only.wav',
                     'hat_only.wav', 'original_kick_band.wav',
                     'original_snare_band.wav', 'original_hat_band.wav'):
            f = d / name
            assert f.exists(), f"missing {f}"
            total += 1
    assert total == 35, f"expected 35 A/B files, got {total}"


def test_15_mandatory_accepts_pinned_in_verdict():
    """Chicken Grease + What If I Go both present in per-song table."""
    v = json.loads((WS / 'data/rc10_drums_v2_impl/verdict.json').read_text())
    assert 'chicken_grease' in v['mandatory_accepts']
    assert 'what_if_i_go' in v['mandatory_accepts']
    ids_in_summary = {r['song_id'] for r in v['per_song_summary']}
    assert '31a164f845f8e27e' in ids_in_summary  # CG
    assert '252eb21ce7df7328' in ids_in_summary  # WIG


def test_16_onset_timing_regression_report_per_song():
    v = json.loads((WS / 'data/rc10_drums_v2_impl/verdict.json').read_text())
    for r in v['per_song_summary']:
        assert 'G1_F1' in r and 'G1_v1_F1' in r, r
        # regression clause: F1_v2 >= max(0.60, F1_v1 - 0.05)
        thr = max(0.60, float(r['G1_v1_F1']) - 0.05)
        assert float(r['G1_F1']) >= thr, (
            f"{r['song_id']} onset F1 regression: {r['G1_F1']} < {thr}"
        )


def test_17_scorecard_shape_and_columns():
    text = (WS / 'data/rc10_drums_v2_impl/scorecard.tsv').read_text()
    lines = text.strip().split('\n')
    assert len(lines) == 6, f"expected 5 rows + header, got {len(lines)}"
    header = lines[0].split('\t')
    for col in ('song_id', 'bpm', 'n_onsets', 'kick_count', 'snare_count',
                'hat_count', 'G1_onset_f1', 'G1_v1_f1', 'G4_median_kick_hz',
                'passed_all', 'onset_timing_status'):
        assert col in header, f"missing column {col!r}"


if __name__ == '__main__':
    tests = [(name, fn) for name, fn in globals().items()
             if name.startswith('test_') and callable(fn)]
    tests.sort()
    n_pass = 0
    n_fail = 0
    for name, fn in tests:
        try:
            fn()
            print(f'PASS  {name}')
            n_pass += 1
        except Exception as e:
            print(f'FAIL  {name}: {e}')
            n_fail += 1
    print(f'\n{n_pass}/{len(tests)} passed, {n_fail} failed')
    sys.exit(1 if n_fail else 0)
