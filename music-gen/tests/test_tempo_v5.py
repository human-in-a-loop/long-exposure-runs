#!/usr/bin/python3
"""c79 P2 tests for scripts/v5/tempo_v5.py (>=6 named cases).

created: 2026-09-06T00:00:00Z
cycle: 79
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle79-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_tempo_v5.py

The suite encodes the FROZEN falsification targets. Where a target FAILED on
disk (Peach Dream / Disco A non-octave regression), the test asserts that the
halt-honest record captures the failure verbatim — it does not paper over it.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))

CORPUS = _ROOT / "data/v5/corpus"
WIG, CG, PD, ROME, DISCO = ("252eb21ce7df7328", "31a164f845f8e27e", "88d247468cb6d49f",
                            "51e433ade2a845e1", "cdd2717e52820ff6")
SHORT_SONG = "069ebba269efccc2"  # '05 02', 59 s — cheapest determinism probe
ENV_PIN_ANCHOR = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}


def _load(s: str) -> dict:
    return json.loads((CORPUS / s / "tempo_v5.json").read_text())


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_01_wig_not_half_time() -> None:
    t = _load(WIG)
    assert not (45.0 <= t["bpm_v5"] <= 56.0), f"WIG still half-time: {t['bpm_v5']}"
    assert abs(t["bpm_v5"] - 100.35) <= 3.0, f"WIG bpm_v5 {t['bpm_v5']} not within 3 of 2x50.17"
    probe = json.loads((CORPUS / WIG / "tempo_v5_wig_mechanism_probe.json").read_text())
    d = probe["probes"]["drums_operator_section_c20"]
    assert d["bpm_librosa"] < 56.0, "drums-section probe should reproduce the c20 half-time baseline"
    assert not (45.0 <= d["bpm_v5"] <= 56.0), f"drums-section probe not resolved: {d['bpm_v5']}"
    print(f"test_01 PASS: WIG full={t['bpm_v5']:.3f}; drums-section {d['bpm_librosa']:.3f}->{d['bpm_v5']:.3f}")


def test_02_cg_anchor_within_2bpm() -> None:
    t = _load(CG)
    assert abs(t["bpm_v5"] - 90.7258064516129) <= 2.0, f"CG delta {t['delta_vs_anchor_bpm']}"
    assert t["within_anchor_tolerance"] is True
    print(f"test_02 PASS: CG bpm_v5={t['bpm_v5']:.3f} delta={t['delta_vs_anchor_bpm']:+.3f}")


def test_03_pd_anchor_target_recorded_honestly() -> None:
    """Frozen target: |bpm_v5 - 123.05| <= 2. On disk this target FAILED
    (non-octave regression). The test asserts the halt-honest record states
    exactly that; it does NOT relax the target."""
    t = _load(PD)
    f = json.loads((CORPUS / "tempo_v5_falsification.json").read_text())
    within = abs(t["bpm_v5"] - 123.046875) <= 2.0
    assert t["within_anchor_tolerance"] == within
    if within:
        assert PD not in f["failing_songs"]
        print(f"test_03 PASS: PD within 2 BPM ({t['bpm_v5']:.3f})")
    else:
        assert PD in f["failing_songs"], "PD failed the anchor but is not recorded as failing"
        assert f["verdict"] == "RULES_OUT_CRITERION_TOO_PERMISSIVE"
        assert f["per_song"][PD]["non_octave_regression_gt_2bpm"] is True
        assert abs(f["per_song"][PD]["bpm_librosa"] - 123.046875) <= 2.0, "librosa baseline should match anchor"
        assert PD in f["lag_tables_failing"] and len(f["lag_tables_failing"][PD]) > 10
        print(f"test_03 PASS (target FAILED, recorded halt-honest): PD bpm_v5={t['bpm_v5']:.3f} "
              f"delta={t['delta_vs_anchor_bpm']:+.3f} verdict={f['verdict']}")


def test_04_candidate_set_contains_octave_relations() -> None:
    for s in (WIG, CG, PD, ROME, DISCO):
        t = _load(s)
        c = t["candidates"]
        for k in ("librosa_x_half", "librosa_x_same", "librosa_x_double", "librosa_x_four_thirds", "librosa_x_three_quarters"):
            assert k in c, f"{s} missing candidate {k}"
        # candidate bpm values are rounded to 6 dp independently -> allow 1e-4
        assert abs(c["librosa_x_double"]["bpm"] - 2 * c["librosa_x_same"]["bpm"]) < 1e-4
        assert abs(c["librosa_x_half"]["bpm"] - 0.5 * c["librosa_x_same"]["bpm"]) < 1e-4
        assert any(k.startswith("ac_peak_") for k in c), f"{s} has no autocorr peak candidates"
        for v in c.values():
            assert v["plausibility_weight"] in (0.0, 0.5, 1.0)
        assert t["octave_relation_to_librosa"] in ("same", "double", "half", "other")
    print("test_04 PASS: octave candidate set + plausibility weights on 5 focus songs")


def test_05_byte_determinism_x2_fresh_subprocess() -> None:
    with tempfile.TemporaryDirectory(prefix="tempo_v5_t05_") as td:
        env = os.environ.copy()
        env.update(_PINS)
        r = subprocess.run(["/usr/bin/python3", "scripts/v5/tempo_v5.py", "--songs", SHORT_SONG, "--out-dir", td,
                            "--summary-name", "s.tsv"], env=env, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-1500:]
        fresh = Path(td) / SHORT_SONG / "tempo_v5.json"
        assert _sha(fresh) == _sha(CORPUS / SHORT_SONG / "tempo_v5.json"), "tempo_v5.json not byte-identical across fresh run"
    bd = json.loads((CORPUS / "tempo_v5_byte_determinism.json").read_text())
    assert bd["byte_determinism_holds"] is True and bd["n_equal"] == bd["n_files_compared"] == 27
    print(f"test_05 PASS: fresh-subprocess byte-det on {SHORT_SONG}; corpus-wide {bd['n_equal']}/{bd['n_files_compared']}")


def test_06_ast_discipline_scan() -> None:
    forbidden_mods = {"random", "secrets"}
    forbidden_names = {"sidecar_nonfactor", "get_state", "save_state", "save_preset", "load_state", "set_state"}
    for path in ("scripts/v5/tempo_v5.py", "scripts/v5/corpus_manifest.py", "scripts/v5/transcribe_full_length.py",
                 "scripts/v5/tempo_v5_verdict.py"):
        src = (_ROOT / path).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] + ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
                for n in names:
                    assert n.split(".")[0] not in forbidden_mods, f"{path} imports PRNG module {n}"
                    assert "sidecar_nonfactor" not in n, f"{path} imports sidecar_nonfactor"
            if isinstance(node, ast.Attribute):
                assert node.attr not in forbidden_names, f"{path} references {node.attr}"
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert not (node.func.attr == "random"), f"{path} calls .random()"
        assert src.splitlines()[0].startswith("#!/usr/bin/python3"), f"{path} lacks /usr/bin/python3 shebang"
        assert 'sys.executable != "/usr/bin/python3"' in src, f"{path} lacks interpreter guard"
    print("test_06 PASS: AST scan (no PRNG / sidecar_nonfactor / VST3 state APIs; interpreter guards)")


def test_07_env_pin_and_manifest_shape() -> None:
    m = json.loads((CORPUS / "corpus_manifest.json").read_text())
    assert m["env_pin_sha256"] == ENV_PIN_ANCHOR
    assert m["count_disclosure"]["total_enumerated"] == len(m["songs"]) >= 7
    ranks = [s["v5_priority_rank"] for s in m["songs"]]
    assert ranks == list(range(1, len(ranks) + 1))
    assert m["songs"][0]["sha16"] == WIG, "WIG must be first per brief §P3 item 4"
    for s in m["songs"]:
        for k in ("sha16", "audio_sha256", "duration_s", "band", "in_v5_corpus", "asset_inventory"):
            assert k in s, f"manifest row missing {k}"
        assert s["in_v5_corpus"] is True
    for s in (WIG, CG, PD, ROME, DISCO):
        assert _load(s)["env_pin_sha256"] == ENV_PIN_ANCHOR
    print(f"test_07 PASS: env_pin canonical; manifest {len(m['songs'])} songs, WIG first")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"\n{len(tests)}/{len(tests)} tempo_v5 tests PASS")
