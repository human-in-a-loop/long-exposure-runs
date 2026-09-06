#!/usr/bin/python3
"""c81 P5 tests for scripts/v5/tempo_v5c.py + tempo_v5c_verdict.py.

created: 2026-09-06T17:20:00Z
cycle: 81
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle81-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_tempo_v5c.py
Encodes the FROZEN pre-registration; asserts the on-disk verdict verbatim (RULES_OUT on Disco A by 0.006) — no relaxation.
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

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
from scripts.v5 import tempo_v5c as T  # noqa: E402

CORPUS = _ROOT / "data/v5/corpus"
WIG, CG, PD, ROME, DISCO = ("252eb21ce7df7328", "31a164f845f8e27e", "88d247468cb6d49f", "51e433ade2a845e1", "cdd2717e52820ff6")
SHORT_SONG = "069ebba269efccc2"
_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
ENUM = ("SUPPORTED_ON_FIVE_ANCHORS", "RULES_OUT_AUTOCORR_DIRECT", "SUPPORTED_ON_ANCHORS_UNSTABLE_ELSEWHERE")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _synthetic_ac(period: float, n: int = 200, harmonic_gain: float = 0.7, hemiola_boost: float = 0.9) -> np.ndarray:
    """Comb of a 3:2 hierarchy (c80 shape) with a hemiola boost strong enough that the 1.5T lag is the STRONGEST
    single peak (v5 flat-band failure mode) while the true beat's T/2 and 2T remain real periodicities."""
    lags = np.arange(n, dtype=float)
    ac = np.zeros(n)
    for k in range(1, 12):
        ac += harmonic_gain ** k * np.exp(-0.5 * ((lags - k * period) / 0.6) ** 2)
        ac += 0.5 * harmonic_gain ** k * np.exp(-0.5 * ((lags - (k - 0.5) * period) / 0.6) ** 2)
    ac += hemiola_boost * np.exp(-0.5 * ((lags - 1.5 * period) / 0.6) ** 2)
    ac[0] = 1.0
    return ac


def test_01_on_disk_pd_lag21_half_period_now_read_from_autocorr() -> None:
    r = json.loads((CORPUS / PD / "tempo_v5c.json").read_text())
    c21 = next(c for c in r["candidates"] if c["lag_frames"] == 21)
    assert c21["lag_half_period"] == 10.5 and c21["half_in_autocorr"] is True and c21["ac_half_period"] > 0.0
    ac = np.asarray([1.0] + r["autocorr_lag_table"]["autocorr_norm"])
    v, ok = T.interp_ac(ac, 10.5)
    assert ok and abs(v - 0.5 * (ac[10] + ac[11])) < 1e-9 and abs(v - c21["ac_half_period"]) < 1e-5
    assert r["bpm_v5c"] == 123.046875 and r["winner"]["lag_frames"] == 21
    print(f"test_01 PASS: PD lag-21 T/2 term = interp ac(10.5) = {v:.4f} (> 0); PD picks 123.047")


def test_02_synthetic_3_2_with_period_21_now_prefers_true_beat() -> None:
    """period 21 is exactly the PD case v5b could not resolve (T/2 = 10.5 lags = 246 BPM outside [40,240])."""
    ac = _synthetic_ac(21.0)
    cands = {c["lag_frames"]: c for c in (T.harmonic_sum_direct(ac, lag) for lag in T.local_maxima(ac))}
    hem = next(l for l in (31, 32) if l in cands)
    assert 21 in cands and cands[hem]["ac_T"] > cands[21]["ac_T"], "3:2 lag must be the strongest single peak"
    assert cands[21]["s"] > cands[hem]["s"], "autocorr-direct harmonic sum must prefer the true beat"
    assert T.interp_ac(ac, 0.5) == (0.0, False) and T.interp_ac(ac, len(ac) + 1.0) == (0.0, False)
    print(f"test_02 PASS: synthetic period 21 — ac(T)={cands[21]['ac_T']:.3f} < ac(1.5T)={cands[hem]['ac_T']:.3f} but s(T)={cands[21]['s']:.3f} > {cands[hem]['s']:.3f}")


def test_03_prereg_mtime_gate_frozen_enum_and_rules_out_branch() -> None:
    prereg = CORPUS / "tempo_v5c_preregistration.json"
    man = json.loads((CORPUS / "corpus_manifest.json").read_text())
    outs = [CORPUS / s["sha16"] / "tempo_v5c.json" for s in man["songs"]]
    assert len(outs) == 26 and all(p.exists() for p in outs)
    assert prereg.stat().st_mtime < min(p.stat().st_mtime for p in outs)
    f = json.loads((CORPUS / "tempo_v5c_falsification.json").read_text())
    assert f["preregistration_gate"]["prereg_precedes_all_outputs"] is True and f["verdict"] in ENUM
    targets = json.loads(prereg.read_text())["falsification_targets_fixed_before_run"]
    missed = [s for s in targets if not f["per_song"][s]["hit"]]
    assert sorted(missed) == sorted(f["missed_targets"])
    if missed:
        assert f["verdict"] == "RULES_OUT_AUTOCORR_DIRECT"
        blocked = json.loads((CORPUS / "recanonicalization_blocked.json").read_text())
        assert PD in blocked["blocked_songs"] and DISCO in blocked["blocked_songs"], "blocked file must stay unchanged under RULES_OUT"
        assert not any((CORPUS / s["sha16"] / "canonical_v5c_reindexed").exists() for s in man["songs"]), "no re-canonicalization under RULES_OUT"
    for s in (WIG, CG, PD, ROME):
        assert f["per_song"][s]["hit"] is True
    print(f"test_03 PASS: prereg mtime gate; verdict={f['verdict']}; missed={missed}; blocked file unchanged")


def test_04_rome_hemiola_secondary_check_explicit() -> None:
    r = json.loads((CORPUS / ROME / "tempo_v5c.json").read_text())
    c = r["contested_lags_17_25"]
    assert abs(c["17"]["bpm"] - 151.999081) < 1e-3 and abs(c["25"]["bpm"] - 103.359375) < 1e-3
    assert c["17"]["s"] > c["25"]["s"] and r["bpm_v5c"] == c["17"]["bpm"]
    f = json.loads((CORPUS / "tempo_v5c_falsification.json").read_text())
    assert f["per_song"][ROME]["secondary_check_rome_hemiola"]["17"]["s"] == c["17"]["s"]
    print(f"test_04 PASS: Rome s(lag17=152)={c['17']['s']:.4f} > s(lag25=103)={c['25']['s']:.4f}; recorded in verdict")


def test_05_byte_determinism_x2() -> None:
    bd = json.loads((CORPUS / "tempo_v5c_byte_determinism.json").read_text())
    assert bd["byte_determinism_holds"] is True and bd["n_equal"] == bd["n_files_compared"] == 27
    with tempfile.TemporaryDirectory(prefix="tempo_v5c_t05_") as td:
        env = os.environ.copy(); env.update(_PINS); env.pop("SUPPRESS_INTERPRETER_GUARD", None)
        r = subprocess.run(["/usr/bin/python3", "scripts/v5/tempo_v5c.py", "--songs", SHORT_SONG, "--out-dir", td,
                            "--summary-name", "s.tsv"], env=env, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-1500:]
        assert _sha(Path(td) / SHORT_SONG / "tempo_v5c.json") == _sha(CORPUS / SHORT_SONG / "tempo_v5c.json")
    print(f"test_05 PASS: byte-det {bd['n_equal']}/{bd['n_files_compared']}; fresh subprocess on {SHORT_SONG}")


def test_06_ast_discipline_on_c81_scripts() -> None:
    forbidden_mods = {"random", "secrets"}
    forbidden_names = {"sidecar_nonfactor", "get_state", "save_state", "save_preset", "load_state", "set_state"}
    for path in ("scripts/v5/tempo_v5c.py", "scripts/v5/tempo_v5c_verdict.py", "scripts/v5/groove_v5.py",
                 "scripts/v5/reindex_fidelity_c81.py", "scripts/v5/ear_probe_v5.py", "scripts/v5/reindex_hook.py"):
        src = (_ROOT / path).read_text()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [x.name for x in node.names] + ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
                for n in names:
                    assert n.split(".")[0] not in forbidden_mods, (path, n)
                    assert "sidecar_nonfactor" not in n
            if isinstance(node, ast.Attribute):
                assert node.attr not in forbidden_names, (path, node.attr)
        assert src.splitlines()[0].startswith("#!/usr/bin/python3") and 'sys.executable != "/usr/bin/python3"' in src
    print("test_06 PASS: AST scan clean (no PRNG / sidecar_nonfactor / VST3 state APIs) on 6 c81 scripts")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"\n{len(tests)}/{len(tests)} tempo_v5c tests PASS")
