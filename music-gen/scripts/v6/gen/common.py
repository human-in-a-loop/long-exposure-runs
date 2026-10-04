#!/usr/bin/python3
"""v6 Phase 2 — shared helpers for the theory-grounded symbolic composer (scripts/v6/gen/).

created: 2026-10-04
milestone: M-V6-GEN-2/theory-grounded-composer

Binding conventions (identical to scripts/v5/generate_v5.py:84-102): the 7-key env pin via os.environ.setdefault, the
suppressible /usr/bin/python3 guard, and NO PRNG anywhere — every stochastic choice is a SHA-256 inverse-CDF draw on a
seed-derived tag string (`u`, `draw_row`, `draw_from`). Sorted-key atomic JSON with "schema_version". Chord-state syntax
is the v5 chain's "<rel_root>:<quality>" / "N" (scripts/v5/harmony_v5.py QUALITIES, re-declared here and asserted equal
by tests/test_v6_gen_harmony.py so this package never imports numpy/mido at module load).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
        "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
for _k, _v in PINS.items():
    os.environ.setdefault(_k, _v)
if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

WS = Path(__file__).resolve().parent.parent.parent.parent  # .../music-gen
if str(WS) not in sys.path:
    sys.path.insert(0, str(WS))

ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
SCHEMA_VERSION = 1
SLOTS = 16  # 16th slots per 4/4 bar
# v5 chain qualities (scripts/v5/harmony_v5.py QUALITIES) — re-declared, asserted equal in tests.
QUALITIES = {"maj": (0, 4, 7), "min": (0, 3, 7), "7": (0, 4, 7, 10), "min7": (0, 3, 7, 10),
             "maj7": (0, 4, 7, 11), "9": (0, 2, 4, 7, 10), "sus": (0, 5, 7)}
SCALES = {"major": (0, 2, 4, 5, 7, 9, 11), "minor": (0, 2, 3, 5, 7, 8, 10)}
INSTRUMENT = {"drums": "drums", "bass": "electric_bass", "keys": "electric_piano", "melody": "synth_lead"}
STEMS = ("drums", "bass", "keys", "melody")


# ------------------------------------------------------------------------------------------------------- sampling ----
def u(tag: str) -> float:
    """SHA-256 uniform in [0, 1) — identical to scripts.v5.groove_v5_v2.hash_uniform."""
    return int(hashlib.sha256(tag.encode()).hexdigest()[:16], 16) / float(1 << 64)


def draw_row(row: dict, tag: str) -> int:
    """Inverse-CDF over a groove-table row {str(int): prob} in numeric key order (= groove_v5_v2.draw)."""
    x = u(tag)
    acc = 0.0
    keys = sorted(row, key=int)
    for k in keys:
        acc += row[k]
        if x < acc:
            return int(k)
    return int(keys[-1])


def draw_from(weights: dict, tag: str):
    """Inverse-CDF over a {key: weight} dict in sorted-key order (= generate_v5.draw_from)."""
    keys = sorted(weights)
    tot = sum(weights[k] for k in keys) or 1.0
    x = u(tag)
    acc = 0.0
    for k in keys:
        acc += weights[k] / tot
        if x < acc:
            return k
    return keys[-1]


def draw_index(weights: list, tag: str) -> int:
    """Inverse-CDF over a list of weights (index returned)."""
    return int(draw_from({f"{i:04d}": float(w) for i, w in enumerate(weights)}, tag))


# ----------------------------------------------------------------------------------------------------------- io ----
def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def sha_text(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def canonical_json(obj, compact: bool = False) -> str:
    if compact:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return json.dumps(obj, sort_keys=True, indent=2) + "\n"


def write_json_atomic(path: Path, obj, compact: bool = False) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(obj, dict) and "schema_version" not in obj:
        obj = dict(obj, schema_version=SCHEMA_VERSION)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(canonical_json(obj, compact), encoding="utf-8")
    os.replace(tmp, path)


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


# ------------------------------------------------------------------------------------------------------- harmony ----
def state_root(state: str):
    return int(state.split(":")[0]) % 12 if state != "N" and ":" in state else None


def state_quality(state: str):
    return state.split(":")[1] if state != "N" and ":" in state else None


def state_pcs(state: str, tonic: int):
    """Absolute pitch classes of a chain state in a key, or None for 'N' (= generate_v5.state_pcs)."""
    if state == "N" or ":" not in state:
        return None
    r, q = state.split(":")
    root = (tonic + int(r)) % 12
    return [(root + iv) % 12 for iv in QUALITIES[q]]


def scale_for(mode: str) -> tuple:
    return SCALES.get(str(mode).lower(), SCALES["major"])


def degree_of(pitch: int, tonic: int, mode: str):
    """0-based scale degree of a pitch (0 = tonic) or None when chromatic."""
    sc = scale_for(mode)
    rel = (int(pitch) - int(tonic)) % 12
    return sc.index(rel) if rel in sc else None


def is_step(a: int, b: int) -> bool:
    return 1 <= abs(int(a) - int(b)) <= 2


def nearest_pitch(pc: int, anchor: int, lo: int, hi: int):
    """Nearest pitch with pitch class pc to anchor inside [lo, hi] (ties -> lower); None if none exists."""
    cands = [p for p in range(lo, hi + 1) if p % 12 == pc % 12]
    return min(cands, key=lambda p: (abs(p - anchor), p)) if cands else None


def seg_matrix(chain: dict) -> dict:
    """Segment-level (change-only) transition rows {s: {s': p}} with a zero diagonal; unseen rows uniform (as v5)."""
    states = chain["states"]
    C = chain["segment_level_counts"]
    P = {}
    for i, s in enumerate(states):
        row = {states[j]: float(C[i][j]) for j in range(len(states)) if j != i}
        tot = sum(row.values())
        if tot <= 0:
            row = {t: 1.0 for t in row}
            tot = sum(row.values())
        P[s] = {t: v / tot for t, v in row.items()}
        P[s][s] = 0.0
    return P


def hold_prob(chain: dict, state: str, beats: int = 4) -> float:
    """Probability of holding `state` for a whole bar, from the beat-level self-transition (p_self ** beats), capped 0.6."""
    i = chain["states"].index(state)
    p = float(chain["beat_level_row_normalized"][i][i])
    return min(0.6, p ** beats)
