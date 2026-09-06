#!/usr/bin/python3
"""c80 P5 tests for scripts/v5/tempo_v5b.py + tempo_v5b_verdict.py (>=4 named cases).

created: 2026-09-06T16:30:00Z
cycle: 80
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle80-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_tempo_v5b.py

Encodes the FROZEN pre-registration. Where the criterion FAILED on disk (PD /
Disco A unchanged at 80.75; Rome regressed to 103.36) the tests assert the
halt-honest record captures it verbatim; they do NOT relax targets.
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
from scripts.v5 import tempo_v5b as T  # noqa: E402

CORPUS = _ROOT / "data/v5/corpus"
WIG, CG, PD, ROME, DISCO = ("252eb21ce7df7328", "31a164f845f8e27e", "88d247468cb6d49f",
                            "51e433ade2a845e1", "cdd2717e52820ff6")
SHORT_SONG = "069ebba269efccc2"
_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _synthetic_ac(period: float, n: int = 200, harmonic_gain: float = 0.7) -> np.ndarray:
    """Comb-like autocorrelation of a 3:2 metrical hierarchy: beat peaks at every
    multiple of `period` (gain 0.7^k), eighth-note subdivision peaks at (k-0.5)*period
    (half height), and a hemiola boost at 1.5*period that makes it the STRONGEST
    single peak (the v5 flat-band failure mode). The true beat's T/2 and 2T are
    real periodicities; the hemiola's T/2 (0.75*period) is not."""
    lags = np.arange(n, dtype=float)
    ac = np.zeros(n)
    for k in range(1, 12):
        ac += harmonic_gain ** k * np.exp(-0.5 * ((lags - k * period) / 0.6) ** 2)
        ac += 0.5 * harmonic_gain ** k * np.exp(-0.5 * ((lags - (k - 0.5) * period) / 0.6) ** 2)
    ac += 0.5 * np.exp(-0.5 * ((lags - 1.5 * period) / 0.6) ** 2)  # 3:2 lag boost
    ac[0] = 1.0
    return ac


def test_01_harmonic_sum_prefers_true_beat_on_synthetic_3_2() -> None:
    """Synthetic: period 21 lags (123 BPM) with a stronger single 3:2 peak at 31.5 lags.
    Both 21 and 42 are in the [40,240] lag range (lag 21 T/2 = 10.5 -> 246 BPM is OUT,
    exactly the failure mode observed on PD), so we use period 24 (107.7 BPM; T/2 = 12
    -> 215 BPM in range) to test the mechanism as pre-registered."""
    ac = _synthetic_ac(24.0)
    cands = {c["lag_frames"]: c for c in (T.harmonic_sum(ac, lag) for lag in T.local_maxima(ac))}
    assert 24 in cands and 36 in cands, f"expected lags 24 and 36 among local maxima: {sorted(cands)}"
    assert cands[36]["ac_T"] > cands[24]["ac_T"], "the 3:2 lag must be the strongest single peak (v5 failure mode)"
    assert cands[24]["s"] > cands[36]["s"], "harmonic sum must prefer the true beat when its harmonics are in range"
    print(f"test_01 PASS: synthetic 3:2 — ac(T)={cands[24]['ac_T']:.3f} < ac(1.5T)={cands[36]['ac_T']:.3f} but "
          f"s(T)={cands[24]['s']:.3f} > s(1.5T)={cands[36]['s']:.3f}")


def test_02_out_of_range_harmonic_terms_contribute_zero() -> None:
    ac = _synthetic_ac(24.0)
    v, lag = T.harmonic_term(ac, 2 * 240.0)  # 480 BPM -> outside [40,240]
    assert v == 0.0 and lag is None
    v, lag = T.harmonic_term(ac, 39.0)  # below 40 BPM
    assert v == 0.0 and lag is None
    c21 = T.harmonic_sum(ac, 21)  # T/2 of lag 21 is lag 10.5 = 246 BPM -> zero (the PD mechanism)
    assert c21["ac_half_period"] == 0.0 and c21["lag_half_period"] is None
    r = json.loads((CORPUS / PD / "tempo_v5b.json").read_text())
    anchor_cand = [c for c in r["candidates"] if c["lag_frames"] == 21]
    assert anchor_cand and anchor_cand[0]["ac_half_period"] == 0.0, "on-disk PD lag-21 candidate must show the zeroed T/2 term"
    print("test_02 PASS: out-of-range harmonics contribute 0 (incl. the on-disk PD lag-21 T/2 term)")


def test_03_tiebreak_determinism_and_no_prng() -> None:
    ac = _synthetic_ac(24.0)
    a = T.harmonic_sum(ac, 24)
    b = T.harmonic_sum(ac, 24)
    assert a == b
    assert T.tiebreak("x", 100.0) == T.tiebreak("x", 100.0) != T.tiebreak("y", 100.0)
    forbidden_mods = {"random", "secrets"}
    forbidden_names = {"sidecar_nonfactor", "get_state", "save_state", "save_preset", "load_state", "set_state"}
    for path in ("scripts/v5/tempo_v5b.py", "scripts/v5/tempo_v5b_verdict.py", "scripts/v5/harmony_v5.py"):
        src = (_ROOT / path).read_text()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [x.name for x in node.names] + ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
                for n in names:
                    assert n.split(".")[0] not in forbidden_mods, f"{path} imports {n}"
                    assert "sidecar_nonfactor" not in n
            if isinstance(node, ast.Attribute):
                assert node.attr not in forbidden_names, f"{path} references {node.attr}"
        assert src.splitlines()[0].startswith("#!/usr/bin/python3")
        assert 'sys.executable != "/usr/bin/python3"' in src
    print("test_03 PASS: deterministic scoring + SHA tiebreak; AST scan clean on 3 c80 scripts")


def test_04_preregistration_mtime_precedes_outputs_and_verdict_is_frozen_enum() -> None:
    prereg = CORPUS / "tempo_v5b_preregistration.json"
    man = json.loads((CORPUS / "corpus_manifest.json").read_text())
    outs = [CORPUS / s["sha16"] / "tempo_v5b.json" for s in man["songs"]]
    assert len(outs) == 26 and all(p.exists() for p in outs)
    assert prereg.stat().st_mtime < min(p.stat().st_mtime for p in outs), "pre-registration must precede every output"
    f = json.loads((CORPUS / "tempo_v5b_falsification.json").read_text())
    assert f["preregistration_gate"]["prereg_precedes_all_outputs"] is True
    assert f["verdict"] in ("SUPPORTED_ON_FIVE_ANCHORS", "RULES_OUT_HARMONIC_SUM", "SUPPORTED_ON_ANCHORS_UNSTABLE_ELSEWHERE")
    # halt-honest: the on-disk verdict reflects the per-song hits verbatim
    targets = json.loads(prereg.read_text())["falsification_targets_fixed_before_run"]
    missed = [s for s in targets if not f["per_song"][s]["hit"]]
    assert sorted(missed) == sorted(f["missed_targets"])
    if missed:
        assert f["verdict"] == "RULES_OUT_HARMONIC_SUM"
        for s in (PD, DISCO):
            assert s in missed, f"{s} must be recorded as missed (80.75 != anchor)"
        blocked = json.loads((CORPUS / "recanonicalization_blocked.json").read_text())
        assert PD in blocked["blocked_songs"] and DISCO in blocked["blocked_songs"]
        assert ROME not in blocked["blocked_songs"] and CG not in blocked["blocked_songs"]
    print(f"test_04 PASS: prereg mtime gate; verdict={f['verdict']}; missed={missed}")


def test_05_anchored_songs_recorded_verbatim() -> None:
    f = json.loads((CORPUS / "tempo_v5b_falsification.json").read_text())
    w = json.loads((CORPUS / WIG / "tempo_v5b.json").read_text())
    assert not (45.0 <= w["bpm_v5b"] <= 56.0) and abs(w["bpm_v5b"] - 99.384014) <= 2.0
    c = json.loads((CORPUS / CG / "tempo_v5b.json").read_text())
    assert abs(c["bpm_v5b"] - 90.7258064516129) <= 2.0
    for s in (WIG, CG, PD, ROME, DISCO):
        r = json.loads((CORPUS / s / "tempo_v5b.json").read_text())
        assert r["bpm_v5b"] == f["per_song"][s]["bpm_v5b"]
        assert r["winner"]["in_pick_band"] and 70.0 <= r["bpm_v5b"] <= 180.0
        assert r["s_scores_top3"][0]["bpm"] == r["bpm_v5b"]
    print("test_05 PASS: WIG/CG hit; all five anchored songs recorded verbatim in the verdict")


def test_06_byte_determinism_x2() -> None:
    bd = json.loads((CORPUS / "tempo_v5b_byte_determinism.json").read_text())
    assert bd["byte_determinism_holds"] is True and bd["n_equal"] == bd["n_files_compared"] == 27
    with tempfile.TemporaryDirectory(prefix="tempo_v5b_t06_") as td:
        env = os.environ.copy()
        env.update(_PINS)
        env.pop("SUPPRESS_INTERPRETER_GUARD", None)
        r = subprocess.run(["/usr/bin/python3", "scripts/v5/tempo_v5b.py", "--songs", SHORT_SONG, "--out-dir", td,
                            "--summary-name", "s.tsv"], env=env, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-1500:]
        assert _sha(Path(td) / SHORT_SONG / "tempo_v5b.json") == _sha(CORPUS / SHORT_SONG / "tempo_v5b.json")
    print(f"test_06 PASS: corpus-wide byte-det {bd['n_equal']}/{bd['n_files_compared']}; fresh subprocess on {SHORT_SONG}")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"\n{len(tests)}/{len(tests)} tempo_v5b tests PASS")
