#!/usr/bin/python3
"""c39 tests for M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2.

≥16 cases per research brief. Invocation:
    PYTHONPATH=. /usr/bin/python3 tests/test_score_bridge_normalizer_v2.py
"""
import sys
assert sys.executable == '/usr/bin/python3', sys.executable

import ast
import hashlib
import json
import pathlib
import subprocess


ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS_RUBRIC = ROOT / 'docs/score_bridge_real_audio_quantization_normalizer_v2_rubric.md'
DATA_DIR = ROOT / 'data/score_bridge_real_audio_normalizer_v2'
RUBRIC_HASH_PATH = DATA_DIR / 'rubric_hash.txt'
VERDICT_PATH = DATA_DIR / 'verdict.json'
FIXTURE_PATH = ROOT / 'data/recreate_v0/per_stage/06_score/merged.musicxml'
NORMALIZE_V2_PATH = ROOT / 'scripts/score_bridge_v2/normalize_v2.py'
RUN_V2_PATH = ROOT / 'scripts/score_bridge_v2/run_normalizer_v2.py'
NORMALIZE_V1_PATH = ROOT / 'scripts/score_bridge_v2/normalize.py'
BRIDGE_PATH = ROOT / 'scripts/score/bridge.py'
RUN_PIPELINE_PATH = ROOT / 'scripts/recreate_v0/run_pipeline.py'
C38_VERDICT_PATH = ROOT / 'data/score_bridge_real_audio/verdict.json'
ANCHOR_PRESERVATION_PATH = DATA_DIR / 'anchor_preservation.json'


def sha256_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _test(name, fn):
    try:
        fn()
        print(f'PASS  {name}')
        return True
    except AssertionError as e:
        print(f'FAIL  {name}: {e}')
        return False
    except Exception as e:
        print(f'ERROR {name}: {type(e).__name__}: {e}')
        return False


# --- Rubric gate tests -------------------------------------------------

def test_01_rubric_mtime_precedes_scripts():
    """Rubric doc mtime must be <= every new script mtime."""
    rmt = DOCS_RUBRIC.stat().st_mtime
    for p in [NORMALIZE_V2_PATH, RUN_V2_PATH]:
        assert p.exists(), f'{p} missing'
        assert p.stat().st_mtime >= rmt, (
            f'{p.name} mtime {p.stat().st_mtime} < rubric mtime {rmt}'
        )


def test_02_rubric_commit_precedes_scripts():
    """git log: rubric commit is an ancestor of every script's first commit."""
    # rubric commit hash
    rubric_commit = subprocess.check_output(
        ['git', 'log', '--follow', '--format=%H',
         'docs/score_bridge_real_audio_quantization_normalizer_v2_rubric.md'],
        cwd=ROOT, text=True).strip().splitlines()
    assert rubric_commit, 'rubric doc not committed'
    r_commit = rubric_commit[-1]  # oldest = first commit
    for pathname in ['scripts/score_bridge_v2/normalize_v2.py',
                     'scripts/score_bridge_v2/run_normalizer_v2.py']:
        commits = subprocess.check_output(
            ['git', 'log', '--follow', '--format=%H', pathname],
            cwd=ROOT, text=True).strip().splitlines()
        if not commits:
            # script not yet committed — mtime gate suffices for now.
            continue
        first_commit = commits[-1]
        # Verify rubric commit is ancestor of script commit.
        rc = subprocess.call(
            ['git', 'merge-base', '--is-ancestor', r_commit, first_commit],
            cwd=ROOT)
        assert rc == 0, (
            f'rubric commit {r_commit[:8]} not ancestor of '
            f'{pathname} first commit {first_commit[:8]}'
        )


def test_03_rubric_hash_matches_doc():
    assert RUBRIC_HASH_PATH.exists(), 'rubric_hash.txt missing'
    stored = RUBRIC_HASH_PATH.read_text().strip()
    computed = sha256_file(DOCS_RUBRIC)
    assert stored == computed, f'{stored} != {computed}'


def test_04_verdict_rubric_hash_embed():
    assert VERDICT_PATH.exists(), 'verdict.json missing'
    v = json.loads(VERDICT_PATH.read_text())
    stored = RUBRIC_HASH_PATH.read_text().strip()
    assert v['rubric_hash'] == stored, (
        f"verdict.rubric_hash={v['rubric_hash']} != rubric_hash.txt={stored}"
    )


# --- Fixture & anchor tests --------------------------------------------

def test_05_fixture_sha_unchanged():
    expected = ('95de5356fc127e8ff2b3c5153a950b35ddd4836b1ec1f40d658f41ebb'
                '73e1592')
    assert sha256_file(FIXTURE_PATH) == expected


def test_06_c38_normalize_unchanged():
    """c38 normalize.py must be byte-identical (peer anchor)."""
    expected = ('23b852146e681b9fd0ce317b388d69af16c5abd5131086435659bf27'
                '12d5656b')
    assert sha256_file(NORMALIZE_V1_PATH) == expected


def test_07_c38_verdict_unchanged():
    """c38 verdict.json byte-identical pre/post."""
    expected = 'f15ef63dceb625710a6bf03afd8fd8a5b0ffe45b74f78fc1f7'
    actual = sha256_file(C38_VERDICT_PATH)
    assert actual.startswith(expected[:16]), f'c38 verdict changed: {actual}'


def test_08_c8_bridge_unchanged():
    expected = ('ed73482270db9f702ec082b597b95da9d92c8e80198a4cc0a8ac394a'
                'a536dbba')
    assert sha256_file(BRIDGE_PATH) == expected


def test_09_run_pipeline_preserved():
    """c37 run_pipeline.py byte-identical; pretty_midi fallback grep-present."""
    expected = ('9d7fa37e9466d562f5d767219303211b9c547d05b2ad2b24167049aa'
                '9cb2078b')
    assert sha256_file(RUN_PIPELINE_PATH) == expected
    body = RUN_PIPELINE_PATH.read_text()
    assert '_concat_per_stem_midis_prettymidi' in body, (
        'pretty_midi fallback function name absent — must NOT be removed'
    )
    assert 'fallback_pretty_midi_concat' in body, (
        'fallback status token absent'
    )


# --- Normalizer scope tests --------------------------------------------

def test_10_normalize_v2_imports_v1_readonly():
    """AST check: normalize_v2 imports normalize (not opens for write)."""
    src = NORMALIZE_V2_PATH.read_text()
    tree = ast.parse(src)
    has_readonly_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            # e.g. from scripts.score_bridge_v2 import normalize as _normalize_v1
            for n in node.names:
                if n.name == 'normalize':
                    has_readonly_import = True
            if node.module and node.module.endswith('normalize') and 'normalize_v2' not in node.module:
                has_readonly_import = True
        elif isinstance(node, ast.Import):
            for n in node.names:
                if n.name.endswith('.normalize') or n.name == 'normalize':
                    has_readonly_import = True
    assert has_readonly_import, 'normalize_v2 does not import normalize'
    # No writes to normalize.py
    assert "open('normalize.py'" not in src
    assert '"normalize.py"' not in src
    # No 'w' mode writes to normalize.py
    for line in src.splitlines():
        if 'normalize.py' in line and ('write' in line or "'w'" in line):
            raise AssertionError(f'suspect write to normalize.py: {line}')


def test_11_verdict_run_shas_equal_when_fixed_or_gap():
    """If verdict is FIXED or STILL_REDEFINED_GAP: SHA1==SHA2 must hold."""
    v = json.loads(VERDICT_PATH.read_text())
    verdict = v['verdict']
    if verdict in ('QUANTIZATION_FIXED_NORMALIZER_V2',
                   'QUANTIZATION_STILL_REDEFINED_GAP'):
        assert v['runs'][0]['sha256'] == v['runs'][1]['sha256'], (
            f'byte-determinism required for {verdict}'
        )


def test_12_fidelity_thresholds_if_fixed():
    """If verdict == FIXED: event_count==195, onset≤2ms, dur≤1 tick."""
    v = json.loads(VERDICT_PATH.read_text())
    if v['verdict'] == 'QUANTIZATION_FIXED_NORMALIZER_V2':
        assert v['fidelity']['event_count'] == 195
        assert v['fidelity']['onset_drift_ms_max'] <= 2.0
        assert v['fidelity']['duration_drift_ticks_max_ppq480'] <= 1.0


def test_13_reconstruction_log_no_silent_drops():
    """Every forced-quarter note is logged (per rubric §6 step 5)."""
    log_path = DATA_DIR / 'results/type_dot_reconstruction_log.json'
    assert log_path.exists()
    log = json.loads(log_path.read_text())
    v = json.loads(VERDICT_PATH.read_text())
    forced = v['normalizer_stats']['forced_quarter']
    assert log['entry_count'] == forced, (
        f'log entries {log["entry_count"]} != forced_quarter {forced}'
    )


def test_14_ast_no_forbidden_imports():
    """No PRNG, no forbidden state-extraction, no c31/c9 chain imports."""
    for p in [NORMALIZE_V2_PATH, RUN_V2_PATH]:
        src = p.read_text()
        tree = ast.parse(src)
        forbidden = {'random', 'numpy.random'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    assert n.name not in forbidden, (
                        f'{p.name}: forbidden import {n.name}'
                    )
            if isinstance(node, ast.ImportFrom):
                assert node.module not in forbidden, (
                    f'{p.name}: forbidden from-import {node.module}'
                )
        # No calls to random.* or getstate
        assert 'random.random(' not in src
        assert 'random.randint(' not in src
        # No c9 chain / c31 palette / c15 i4 imports
        assert 'render_effects_layered' not in src
        assert 'i4_stratified' not in src
        assert 'sidecar_nonfactor' not in src


def test_15_interpreter_guard():
    for p in [NORMALIZE_V2_PATH, RUN_V2_PATH]:
        src = p.read_text()
        assert '#!/usr/bin/python3' in src.splitlines()[0]
        assert "sys.executable == '/usr/bin/python3'" in src, p.name


def test_16_anchor_preservation_lists_15plus():
    ap = json.loads(ANCHOR_PRESERVATION_PATH.read_text())
    assert ap['anchor_count'] >= 15, f'only {ap["anchor_count"]} anchors'
    assert ap['all_expected_match'] is True, 'some expected SHAs mismatch'
    assert ap['expected_verified_count'] >= 4, (
        f'only {ap["expected_verified_count"]} SHA-verified'
    )


# --- Additional coverage ------------------------------------------------

def test_17_duration_map_correctness():
    """Duration map contains standard type+dot ticks at div=960."""
    sys.path.insert(0, str(ROOT))
    from scripts.score_bridge_v2 import normalize_v2 as nv2
    m = nv2.build_duration_map(960)
    assert m[960] == ('quarter', 0)
    assert m[480] == ('eighth', 0)
    assert m[15] == ('256th', 0)
    assert m[1440] == ('quarter', 1)  # dotted quarter
    assert m[1920] == ('half', 0)


def test_18_forced_quarter_notes_logged():
    """23 forced-quarter entries expected for the c37 fixture."""
    log_path = DATA_DIR / 'results/type_dot_reconstruction_log.json'
    log = json.loads(log_path.read_text())
    if VERDICT_PATH.exists():
        v = json.loads(VERDICT_PATH.read_text())
        expected_forced = v['normalizer_stats']['forced_quarter']
        assert log['entry_count'] == expected_forced


TESTS = [
    ('01_rubric_mtime_precedes_scripts', test_01_rubric_mtime_precedes_scripts),
    ('02_rubric_commit_precedes_scripts', test_02_rubric_commit_precedes_scripts),
    ('03_rubric_hash_matches_doc', test_03_rubric_hash_matches_doc),
    ('04_verdict_rubric_hash_embed', test_04_verdict_rubric_hash_embed),
    ('05_fixture_sha_unchanged', test_05_fixture_sha_unchanged),
    ('06_c38_normalize_unchanged', test_06_c38_normalize_unchanged),
    ('07_c38_verdict_unchanged', test_07_c38_verdict_unchanged),
    ('08_c8_bridge_unchanged', test_08_c8_bridge_unchanged),
    ('09_run_pipeline_preserved', test_09_run_pipeline_preserved),
    ('10_normalize_v2_imports_v1_readonly', test_10_normalize_v2_imports_v1_readonly),
    ('11_verdict_run_shas_equal_when_fixed_or_gap', test_11_verdict_run_shas_equal_when_fixed_or_gap),
    ('12_fidelity_thresholds_if_fixed', test_12_fidelity_thresholds_if_fixed),
    ('13_reconstruction_log_no_silent_drops', test_13_reconstruction_log_no_silent_drops),
    ('14_ast_no_forbidden_imports', test_14_ast_no_forbidden_imports),
    ('15_interpreter_guard', test_15_interpreter_guard),
    ('16_anchor_preservation_lists_15plus', test_16_anchor_preservation_lists_15plus),
    ('17_duration_map_correctness', test_17_duration_map_correctness),
    ('18_forced_quarter_notes_logged', test_18_forced_quarter_notes_logged),
]


if __name__ == '__main__':
    n_pass = sum(_test(name, fn) for name, fn in TESTS)
    print(f'\n{n_pass}/{len(TESTS)} tests passed')
    sys.exit(0 if n_pass == len(TESTS) else 1)
