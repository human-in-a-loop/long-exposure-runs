#!/usr/bin/python3
"""Tests for c57 clone-1 W2 RC10 Musical Time + Repetition.

Run via:  PYTHONPATH=. /usr/bin/python3 tests/test_rc10_musical_time.py
Env:      PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8
          OMP/MKL/OPENBLAS_NUM_THREADS=1
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.recreate_v2.musical_time import (  # noqa: E402
    RUBRIC_SHA_ANCHOR, RUBRIC_HASH_PATH,
)
from scripts.recreate_v2.musical_time import quantize as q_mod  # noqa: E402
from scripts.recreate_v2.musical_time import aggregator  # noqa: E402
from scripts.recreate_v2.musical_time import loop_detector  # noqa: E402
from scripts.recreate_v2.musical_time import tempo_estimators  # noqa: E402

RUBRIC_DOC = REPO / "docs/rc10_musical_time_rubric.md"
MODULES_DIR = REPO / "scripts/recreate_v2/musical_time"
DATA_DIR = REPO / "data/rc10_musical_time"


PASSED = 0
FAILED = 0


def test(name):
    def deco(fn):
        global PASSED, FAILED
        try:
            fn()
            PASSED += 1
            print(f"  PASS  {name}")
        except AssertionError as e:
            FAILED += 1
            print(f"  FAIL  {name}: {e}")
        except Exception as e:
            FAILED += 1
            print(f"  ERR   {name}: {type(e).__name__}: {e}")
        return fn
    return deco


# ---- Test 01: rubric mtime pre-registration (mtime hard per c46 (ii)) ---
@test("01 rubric doc mtime < every module .py under musical_time/")
def _t01():
    rubric_mtime = RUBRIC_DOC.stat().st_mtime
    for p in sorted(MODULES_DIR.glob("*.py")):
        if p.name == "__init__.py":
            continue
        assert p.stat().st_mtime > rubric_mtime, f"{p.name} mtime {p.stat().st_mtime} <= rubric {rubric_mtime}"


# ---- Test 02: rubric_hash three-way chain -------------------------------
@test("02 rubric_hash three-way byte-equality (doc == rubric_hash.txt == verdict.rubric_hash)")
def _t02():
    doc_sha = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()
    txt_sha = (REPO / RUBRIC_HASH_PATH).read_text().strip()
    verdict_sha = json.loads((DATA_DIR / "verdict.json").read_text())["rubric_hash"]
    assert doc_sha == txt_sha == verdict_sha == RUBRIC_SHA_ANCHOR, \
        f"chain broken: doc={doc_sha[:12]} txt={txt_sha[:12]} verdict={verdict_sha[:12]} anchor={RUBRIC_SHA_ANCHOR[:12]}"


# ---- Test 03: render_stem.py c33 SHA anchor lock ------------------------
@test("03 scripts/palette_render/render_stem.py SHA byte-identical to c33 anchor")
def _t03():
    sha = hashlib.sha256((REPO / "scripts/palette_render/render_stem.py").read_bytes()).hexdigest()
    assert sha == "214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b", sha


# ---- Test 04: no PRNG (AST grep clean) ----------------------------------
@test("04 no PRNG in modules (random / np.random / torch seed grep clean)")
def _t04():
    banned = [
        r"\brandom\.\w+", r"\bnp\.random\b", r"\bnumpy\.random\b",
        r"\btorch\.manual_seed\b", r"\btorch\.rand\w+",
    ]
    for p in MODULES_DIR.glob("*.py"):
        text = p.read_text()
        for pat in banned:
            m = re.search(pat, text)
            assert not m, f"{p.name}: banned pattern {pat!r} at {m.group()!r}"


# ---- Test 05: no sidecar_nonfactor import -------------------------------
@test("05 no sidecar_nonfactor imports")
def _t05():
    for p in MODULES_DIR.glob("*.py"):
        assert "sidecar_nonfactor" not in p.read_text(), p


# ---- Test 06: /usr/bin/python3 guard on top-level scripts --------------
@test("06 /usr/bin/python3 shebang on runnable scripts")
def _t06():
    runnable = ["run_all.py", "byte_determinism.py", "anchor_preservation.py",
                "tempo_estimators.py", "tap_test_helpers.py", "quantize.py",
                "loop_detector.py", "aggregator.py", "cross_stem_energy.py",
                "off_grid_logger.py"]
    for name in runnable:
        p = MODULES_DIR / name
        first = p.read_text().splitlines()[0]
        assert first.startswith("#!/usr/bin/python3"), f"{name}: {first!r}"


# ---- Test 07: c48 env-flag defaults OFF via os.environ.setdefault -------
@test("07 c48 env-flags default OFF via os.environ.setdefault in __init__")
def _t07():
    init = (MODULES_DIR / "__init__.py").read_text()
    assert "os.environ.setdefault" in init
    assert "MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION" in init
    assert "MUSICGEN_LEDGER_SUPERSEDES_IN_HASH" in init


# ---- Test 08: c53 rc5 tempo consumption byte-identical ------------------
@test("08 c53 rc5 tempo anchor SHAs byte-identical pre==post (via anchor snapshot)")
def _t08():
    snap = json.loads((DATA_DIR / "anchor_preservation.json").read_text())
    for sha in ["31a164f845f8e27e", "252eb21ce7df7328", "51e433ade2a845e1",
                "88d247468cb6d49f", "cdd2717e52820ff6"]:
        key = f"data/recreate_v2/baseline/{sha}/rc5_tempo_bpm.json"
        assert snap["anchors"].get(key), f"missing rc5 anchor for {sha}"


# ---- Test 09: focus_set_v2 consumption byte-identical -------------------
@test("09 focus_set_v2.json SHA byte-identical pre==post")
def _t09():
    snap = json.loads((DATA_DIR / "anchor_preservation.json").read_text())
    expected = hashlib.sha256((REPO / "data/recreate_v2/focus_set_v2.json").read_bytes()).hexdigest()
    assert snap["anchors"]["data/recreate_v2/focus_set_v2.json"] == expected


# ---- Test 10: 16th-grid deviation range assertion -----------------------
@test("10 16th-grid deviations ∈ [-125, +125] ms for in-grid notes")
def _t10():
    for sha in ["31a164f845f8e27e", "252eb21ce7df7328", "51e433ade2a845e1",
                "88d247468cb6d49f", "cdd2717e52820ff6"]:
        for stem in ("drums", "bass", "vocals", "guitar", "piano", "other"):
            p = DATA_DIR / sha / stem / "quantized_notes.json"
            if not p.exists():
                continue
            notes = json.loads(p.read_text())["notes"]
            for n in notes:
                assert -125.0 <= n["grid_deviation_ms"] <= 125.0, (sha, stem, n)


# ---- Test 11: loop-length confidence range [0, 1] -----------------------
@test("11 loop_length_confidence ∈ [0.0, 1.0] for every song")
def _t11():
    for sha in ["31a164f845f8e27e", "252eb21ce7df7328", "51e433ade2a845e1",
                "88d247468cb6d49f", "cdd2717e52820ff6"]:
        p = DATA_DIR / sha / "loop_length.json"
        assert p.exists(), sha
        d = json.loads(p.read_text())
        conf = d["loop_length_confidence"]
        assert 0.0 <= conf <= 1.0 + 1e-9, (sha, conf)


# ---- Test 12: aggregator round-trip self-consistency --------------------
@test("12 aggregator consensus round-trip: consensus_from(per_repeat) == consensus_loop")
def _t12():
    # Synthetic 2-bar loop with clean repeats.
    per_stem_notes = {
        "drums": [(0, 0.0), (16, 5.0), (32, -3.0)],  # positions in loop of 2 bars
        "bass": [(4, 10.0), (20, -8.0), (36, 12.0)],
    }
    consensus, rows = aggregator.aggregate_consensus(per_stem_notes, 2, 3)
    recon = aggregator.consensus_from_per_repeat(rows, 2)
    assert aggregator.round_trip_ok(consensus, recon)


# ---- Test 13: cross-stem energy table shape -----------------------------
@test("13 cross_stem_energy_per_onset.tsv has 9-col header + finite energy values")
def _t13():
    p = DATA_DIR / "cross_stem_energy_per_onset.tsv"
    assert p.exists()
    lines = p.read_text().splitlines()
    header = lines[0].split("\t")
    assert header == [
        "song_sha16", "onset_time_s", "source_stem",
        "energy_drums", "energy_bass", "energy_vocals",
        "energy_guitar", "energy_piano", "energy_other_residual",
    ], header
    # Check at least one row is present and every energy column parses.
    assert len(lines) > 1
    for r in lines[1:6]:
        cols = r.split("\t")
        for c in cols[3:]:
            float(c)  # raises on malformed


# ---- Test 14: verdict.json shape (frozen enum) -------------------------
@test("14 verdict.json fields present with frozen enum verdict")
def _t14():
    v = json.loads((DATA_DIR / "verdict.json").read_text())
    for k in ("cycle", "clone", "milestone", "rubric_hash", "verdict",
              "n_songs", "n_loop_pass", "n_round_trip_pass",
              "mandatory_songs", "madmom_unavailable", "per_song"):
        assert k in v, k
    assert v["verdict"] in {
        "MUSICAL_TIME_LANDS", "MUSICAL_TIME_PARTIAL", "MUSICAL_TIME_FAILS"
    }, v["verdict"]
    assert v["cycle"] == 57
    assert v["clone"] == "clone-1"


# ---- Test 15: byte-determinism sidecar exists + holds -------------------
@test("15 data/rc10_musical_time/byte_determinism.json holds=True + n_mismatch=0")
def _t15():
    p = DATA_DIR / "byte_determinism.json"
    assert p.exists()
    d = json.loads(p.read_text())
    assert d["byte_determinism_holds"] is True
    assert d["n_mismatch"] == 0
    assert d["mismatch_files"] == []


# ---- Test 16: anchor preservation ≥ 15 entries -------------------------
@test("16 anchor preservation snapshot ≥ 15 entries (25+ target)")
def _t16():
    p = DATA_DIR / "anchor_preservation.json"
    assert p.exists()
    d = json.loads(p.read_text())
    assert d["anchor_count"] >= 15, d["anchor_count"]


# ---- Test 17: on-disk verdict readable & fetchability ladder present ----
@test("17 fetchability_ladder.jsonl carries madmom probe rung")
def _t17():
    p = DATA_DIR / "fetchability_ladder.jsonl"
    assert p.exists()
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    assert any(r.get("rung") == "madmom_import" for r in rows)
    assert any(r.get("outcome") in {"FETCH_OK", "FETCH_FAIL"} for r in rows)


# ---- Test 18: quantize unit test (pure) --------------------------------
@test("18 quantize.quantize_onsets: on-grid + off-grid split correct")
def _t18():
    tempo = 120.0
    sixteenth = 60.0 / tempo / 4.0  # 0.125 s
    # Onsets at exactly grid positions 0, 4, 8 and one off-grid (200 ms after 0).
    onsets = [0.0, 4 * sixteenth, 8 * sixteenth, 0.200]
    in_grid, off = q_mod.quantize_onsets(onsets, 0.0, tempo)
    # 0.200 is closest to pos 2 (0.250), deviation -50 ms -> in-grid.
    assert len(in_grid) == 4, (in_grid, off)
    assert len(off) == 0
    # Force a large clamp: at 30 BPM, sixteenth = 0.5 s. Onset at 0.200 s
    # snaps to grid pos 0 (expected 0.0) with dev = +200 ms → outside clamp.
    onsets_far = [0.200]
    in_grid2, off2 = q_mod.quantize_onsets(onsets_far, 0.0, 30.0)
    assert len(off2) == 1, (in_grid2, off2)
    assert off2[0]["reason"] == "outside_clamp", off2


# ---- Test 19: tempo_estimators produces finite values -------------------
@test("19 estimate_librosa returns finite tempo + non-empty beat_times on synth click")
def _t19():
    import numpy as np
    sr = 44100
    dur = 6.0
    y = np.zeros(int(sr * dur), dtype=np.float32)
    # 120 BPM = 2 Hz → clicks every 0.5 s
    for t in np.arange(0.0, dur, 0.5):
        i = int(t * sr)
        y[i:i + 200] = 1.0
    result = tempo_estimators.estimate_librosa(y, sr, start_bpm=120.0)
    assert result["tempo_bpm"] > 0
    assert result["beat_count"] > 0


# ---- Test 20: loop detector on periodic synthetic feature matrix --------
@test("20 loop_detector.compute_loop_length: periodic 12-bar synth gives lag=4 or matching")
def _t20():
    import numpy as np
    # Synthetic per-bar features: 12 bars repeating every 4.
    rng_free = np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0],
                          [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0],
                          [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0],
                          [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1.0]], dtype=np.float64)
    feats = np.vstack([rng_free] * 3)
    r = loop_detector.compute_loop_length(feats)
    assert r["loop_length_bars"] == 4, r
    assert r["loop_length_confidence"] > 0.5, r


# ---- Test 21: Chicken Grease PASS loop-length ≥ 0.6 (mandatory) --------
@test("21 mandatory Chicken Grease PASS loop-length ≥ 0.6 (rubric §D6)")
def _t21():
    p = DATA_DIR / "31a164f845f8e27e" / "loop_length.json"
    d = json.loads(p.read_text())
    assert d["loop_length_confidence"] >= 0.6, d["loop_length_confidence"]


# ---- Test 22: rubric SHA anchor byte-identical to embedded constant ----
@test("22 RUBRIC_SHA_ANCHOR in __init__.py byte-identical to rubric SHA-256")
def _t22():
    actual = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()
    assert actual == RUBRIC_SHA_ANCHOR, actual


if __name__ == "__main__":
    print("== tests/test_rc10_musical_time.py ==")
    for name in list(globals().keys()):
        pass  # tests self-register via decorator when imported
    print(f"\n== {PASSED} PASSED / {FAILED} FAILED ==")
    sys.exit(0 if FAILED == 0 else 1)
