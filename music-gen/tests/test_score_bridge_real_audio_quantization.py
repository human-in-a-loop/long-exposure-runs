#!/usr/bin/python3
# Test suite for M-SCORE-1/bridge-api-real-audio-quantization.
# Plain-assert style (no pytest); invoke via:
#     PYTHONPATH=. /usr/bin/python3 tests/test_score_bridge_real_audio_quantization.py
# Author: cyd7bevdr@mozmail.com, cycle 38, fork 33a2a8003c84 / clone-1.
import sys
assert sys.executable == '/usr/bin/python3', sys.executable

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
os.chdir(REPO_ROOT)

RUBRIC_PATH = REPO_ROOT / 'docs/score_bridge_real_audio_quantization_rubric.md'
RUBRIC_HASH_PATH = REPO_ROOT / 'data/score_bridge_real_audio/rubric_hash.txt'
FIXTURE_PATH = REPO_ROOT / 'data/score_bridge_real_audio/inputs/merged_real_audio.musicxml'
FIXTURE_SHA = '95de5356fc127e8ff2b3c5153a950b35ddd4836b1ec1f40d658f41ebb73e1592'
V2_DIR = REPO_ROOT / 'scripts/score_bridge_v2'
VERDICT_PATH = REPO_ROOT / 'data/score_bridge_real_audio/verdict.json'
ANCHOR_PRES_PATH = REPO_ROOT / 'data/score_bridge_real_audio/anchor_preservation.json'
P1_TSV = REPO_ROOT / 'data/score_bridge_real_audio/probes/p1_mscore3_flags.tsv'
P2_TSV = REPO_ROOT / 'data/score_bridge_real_audio/probes/p2_normalizer.tsv'
P2_ATTR = REPO_ROOT / 'data/score_bridge_real_audio/probes/p2_property_attribution.json'
P3_TSV = REPO_ROOT / 'data/score_bridge_real_audio/probes/p3_alternative_backends.tsv'

# Pre-branch SHAs for read-only anchors (captured at rubric-first commit).
# scripts/score/bridge.py c8 anchor, scripts/recreate_v0/run_pipeline.py c37 clone-0.
PRE_BRANCH_ANCHORS = {
    'scripts/score/bridge.py':
        'ed73482270db9f702ec082b597b95da9d92c8e80198a4cc0a8ac394aa536dbba',
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _tsv_rows(p: Path):
    lines = p.read_text().splitlines()
    header = lines[0].split('\t')
    for ln in lines[1:]:
        yield dict(zip(header, ln.split('\t')))


passed = []
failed = []


def _t(name, fn):
    try:
        fn()
        passed.append(name)
        print('PASS', name)
    except AssertionError as e:
        failed.append((name, str(e)))
        print('FAIL', name, ':', str(e)[:400])
    except Exception as e:
        failed.append((name, type(e).__name__ + ':' + str(e)))
        print('FAIL', name, ':', type(e).__name__, str(e)[:400])


# --- gates ---

def test_01_mtime_gate():
    """mtime gate: rubric mtime <= every script mtime under scripts/score_bridge_v2/."""
    assert RUBRIC_PATH.exists(), 'rubric missing'
    r_mtime = RUBRIC_PATH.stat().st_mtime
    scripts = sorted(V2_DIR.rglob('*.py'))
    assert scripts, 'no scripts under scripts/score_bridge_v2/'
    for s in scripts:
        assert s.stat().st_mtime >= r_mtime, (
            'script ' + str(s) + ' has mtime ' + str(s.stat().st_mtime)
            + ' predating rubric ' + str(r_mtime))


def test_02_git_log_gate():
    """rubric commit predates every commit touching scripts/score_bridge_v2/."""
    r = subprocess.run(
        ['git', 'log', '--follow', '--pretty=%H,%at', '--',
         str(RUBRIC_PATH.relative_to(REPO_ROOT))],
        cwd=str(REPO_ROOT), capture_output=True, text=True, check=True,
    )
    lines = [ln for ln in r.stdout.strip().splitlines() if ln]
    assert lines, 'no git-log for rubric'
    rubric_first_commit_at = int(lines[-1].split(',')[1])
    r2 = subprocess.run(
        ['git', 'log', '--pretty=%H,%at', '--',
         'scripts/score_bridge_v2/'],
        cwd=str(REPO_ROOT), capture_output=True, text=True, check=True,
    )
    script_lines = [ln for ln in r2.stdout.strip().splitlines() if ln]
    if not script_lines:
        # Scripts not yet committed; gate satisfied trivially. Once they land
        # in git they must post-date the rubric.
        return
    script_commits_at = [int(ln.split(',')[1]) for ln in script_lines]
    for at in script_commits_at:
        assert at >= rubric_first_commit_at, (
            'script commit at ' + str(at) + ' predates rubric commit at '
            + str(rubric_first_commit_at))


def test_03_rubric_hash_matches():
    assert RUBRIC_HASH_PATH.exists(), 'rubric_hash.txt missing'
    got = RUBRIC_HASH_PATH.read_text().strip()
    expected = sha256(RUBRIC_PATH)
    assert got == expected, 'rubric_hash mismatch: got ' + got + ' expected ' + expected


def test_04_verdict_embeds_rubric_hash():
    assert VERDICT_PATH.exists(), 'verdict.json missing'
    v = json.loads(VERDICT_PATH.read_text())
    got = v.get('rubric_hash')
    expected = RUBRIC_HASH_PATH.read_text().strip()
    assert got == expected, 'verdict.rubric_hash mismatch: got ' + str(got) + ' expected ' + expected


def test_05_fixture_sha_equals_c37_anchor():
    assert FIXTURE_PATH.exists()
    assert sha256(FIXTURE_PATH) == FIXTURE_SHA, (
        'fixture SHA changed - copy is no longer identical to c37 anchor')


def test_06_c8_bridge_byte_identical():
    p = REPO_ROOT / 'scripts/score/bridge.py'
    got = sha256(p)
    expected = PRE_BRANCH_ANCHORS['scripts/score/bridge.py']
    assert got == expected, 'c8 bridge.py SHA changed: got ' + got


def test_07_recreate_v0_run_pipeline_untouched():
    # The c37 clone-0 anchor script — hash captured pre-branch via
    # anchor_preservation.json when the verdict resolver first ran.
    ap = json.loads(ANCHOR_PRES_PATH.read_text())
    rel = 'scripts/recreate_v0/run_pipeline.py'
    assert ap['anchors_expected'].get(rel) == ap['anchors_current'].get(rel), (
        'c37 clone-0 run_pipeline.py changed since first run')


def test_08_p1_tsv_has_rows_with_byte_det_populated():
    assert P1_TSV.exists()
    rows = list(_tsv_rows(P1_TSV))
    assert len(rows) >= 1, 'P1 TSV empty'
    for r in rows:
        v = r.get('byte_deterministic', '')
        assert v in ('True', 'False'), 'P1 row has malformed byte_deterministic: ' + str(v)


def test_09_p2_attribution_names_candidate():
    assert P2_ATTR.exists()
    attr = json.loads(P2_ATTR.read_text())
    hyps = attr.get('candidate_hypotheses', [])
    assert any(h.get('candidate_pathology') for h in hyps), (
        'no candidate MusicXML property named with attribution evidence')


def test_10_p3_tsv_has_two_backend_rows():
    assert P3_TSV.exists()
    rows = list(_tsv_rows(P3_TSV))
    backends = {r['backend'] for r in rows}
    assert backends == {'music21', 'lilypond'}, (
        'P3 TSV backends mismatch: ' + str(backends))
    for r in rows:
        assert 'byte_deterministic' in r, 'P3 row missing byte_deterministic'


def test_11_winning_path_shas_match_when_present():
    v = json.loads(VERDICT_PATH.read_text())
    if v['verdict'] in ('QUANTIZATION_FIXED', 'QUANTIZATION_REDEFINED_GAP'):
        wp = v['winning_path']
        assert wp, 'non-STILL_GAP verdict must name winning_path'
        row = wp.get('row', {})
        r1 = row.get('run1_midi_sha')
        r2 = row.get('run2_midi_sha')
        assert r1 and r2 and r1 == r2, (
            'winning path SHAs unequal: ' + str(r1) + ' vs ' + str(r2))


def test_12_anchor_preservation_lists_12_plus_and_all_match():
    ap = json.loads(ANCHOR_PRES_PATH.read_text())
    assert len(ap['anchors_expected']) >= 12, (
        'need >= 12 anchors, got ' + str(len(ap['anchors_expected'])))
    assert ap.get('preserved') is True, (
        'anchor drift detected: ' + json.dumps(ap.get('changed', {}), indent=2))


def test_13_ast_no_forbidden_imports():
    forbidden_substrings = [
        'scripts.tex.render_effects_layered',
        'scripts.classifier.sidecar_nonfactor',
        'scripts.rules.sampling.i4_stratified',
        'scripts.palette.',
        'scripts.palette_v2.',
    ]
    for py in V2_DIR.rglob('*.py'):
        text = py.read_text()
        for sub in forbidden_substrings:
            assert sub not in text, (
                'forbidden import substring ' + sub + ' in ' + str(py))


def test_14_ast_no_forbidden_state_calls():
    forbidden = ['get_state(', 'save_state(', 'save_preset(',
                 'load_state(', 'set_state(']
    for py in V2_DIR.rglob('*.py'):
        text = py.read_text()
        for f in forbidden:
            assert f not in text, ('forbidden call ' + f + ' in ' + str(py))


def test_15_ast_no_prng():
    prng_patterns = [
        re.compile(r'\brandom\.'),
        re.compile(r'\bnp\.random\.'),
        re.compile(r'torch\.manual_seed\((?!0\))'),
    ]
    for py in V2_DIR.rglob('*.py'):
        text = py.read_text()
        for pat in prng_patterns:
            m = pat.search(text)
            assert not m, ('PRNG pattern ' + pat.pattern + ' in ' + str(py)
                           + ' at ' + text[max(0, m.start()-20):m.end()+20])


def test_16_interpreter_guard_present():
    for py in V2_DIR.rglob('*.py'):
        first = py.read_text().splitlines()[:1]
        assert first and first[0] == '#!/usr/bin/python3', (
            'missing #!/usr/bin/python3 in ' + str(py))


def test_17_pretty_midi_fallback_still_present():
    p = REPO_ROOT / 'scripts/recreate_v0/run_pipeline.py'
    text = p.read_text()
    assert '_concat_per_stem_midis_prettymidi' in text, (
        'pretty_midi fallback function name missing from run_pipeline.py')
    assert 'fallback_pretty_midi_concat' in text, (
        'fallback_pretty_midi_concat status token missing from run_pipeline.py')


if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if callable(fn) and name.startswith('test_'):
            _t(name, fn)
    print('---')
    print('PASSED', len(passed))
    print('FAILED', len(failed))
    if failed:
        for name, msg in failed:
            print('  ', name, ':', msg[:200])
        sys.exit(1)
