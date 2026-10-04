#!/usr/bin/python3
"""v6 Phase 0 (data layer) — shared constants + helpers for the corpus/tempo/bootstrap scripts.

created: 2026-10-04
milestone: M-V6-DATA-0

Everything the Phase-0 scripts share: the 7-key env pin (identical to scripts/v5/tempo_v5.py:37-41), the
pinned env sha (asserted at import to equal the sha256 of the compact sorted JSON of that dict), the
suppressible interpreter guard, the focus-song table for the v6 corpus (CG + PD are ABSENT), the default
tempo overrides, sorted-key atomic JSON writes and sha256 helpers. No PRNG anywhere.

Import order matters: `pin_env()` must run before numpy/librosa are imported by the caller.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path

PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
        "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1"}
ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
assert hashlib.sha256(json.dumps(PINS, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == ENV_PIN_SHA256, \
    "env pin table drifted from the pinned sha (scripts/v5/tempo_v5.py:37-41)"

WS = Path(__file__).resolve().parent.parent.parent  # .../music-gen

# Focus songs present byte-identical in the 29-song corpus (priority order: WIG first, then Rome, Disco A).
FOCUS = {
    "252eb21ce7df7328": {"name": "What If I Go", "short": "WIG", "band": 5, "reference_bpm": 99.38},
    "51e433ade2a845e1": {"name": "Rome", "short": "Rome", "band": 5, "reference_bpm": 152.0},
    "cdd2717e52820ff6": {"name": "Disco A", "short": "DiscoA", "band": 5, "reference_bpm": 120.272335},
}
FOCUS_ORDER = ("252eb21ce7df7328", "51e433ade2a845e1", "cdd2717e52820ff6")
FOCUS_ABSENT = {"31a164f845f8e27e": "Chicken Grease", "88d247468cb6d49f": "Peach Dream"}  # v5 focus songs NOT in this corpus
EXEMPLARS = {"a9587ccde1b333f5": "Molasses", "467fbeb2e3b019a0": "Essence", "2b0370d9d0162c98": "Desire"}  # v4 ear exemplars
BAND_ORDER = (7, 5, 4)  # after the focus tier: band 7, then 5, then 4 (by playlist position within a band)

# Operator-adopted tempo overrides for v6 (bpm_v5 served to the v5 transcription driver). Disco A: the old librosa
# estimator returned 80.75 (3:2 error); the F4 operator-adopted value is 120.272335 (c86). WIG / Rome are added here
# only if the v6 estimator misses them by > 2 % (tempo_v6.py reports that; it does NOT auto-add).
TEMPO_OVERRIDES_DEFAULT = {"cdd2717e52820ff6": 120.272335}

SF2_PATH = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
SF2_SHA256_PINNED = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"

RECEIPTS = WS / "corpus" / "ratings" / "ingest_receipts.jsonl"
RATINGS_TSV = WS / "corpus" / "ratings" / "ratings_manifest.tsv"
V5_CORPUS = WS / "data" / "v5" / "corpus"
V6_CORPUS = WS / "data" / "v6" / "corpus"
MANIFEST_V5 = V5_CORPUS / "corpus_manifest.json"
MANIFEST_V6 = V6_CORPUS / "corpus_manifest_v6.json"
TEMPO_OVERRIDES_V6 = V6_CORPUS / "tempo_overrides_v6.json"


def pin_env() -> None:
    for k, v in PINS.items():
        os.environ.setdefault(k, v)


def interpreter_guard() -> None:
    if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
        print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
        sys.exit(2)


def sha256_file(path: str | os.PathLike, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def canonical_json(obj) -> str:
    """Sorted keys, 2-space indent, trailing newline — the byte layout every Phase-0 output uses."""
    return json.dumps(obj, sort_keys=True, indent=2, default=_json_default) + "\n"


def _json_default(o):
    try:
        import numpy as np
    except Exception:  # pragma: no cover
        np = None
    if np is not None:
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"not JSON serialisable: {type(o).__name__}")


def write_text_atomic(path: str | os.PathLike, text: str) -> bool:
    """Write via <path>.tmp + os.replace. Returns True if the file changed (content differs / was absent)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
    return True


def write_json_atomic(path: str | os.PathLike, obj) -> bool:
    return write_text_atomic(path, canonical_json(obj))


def read_json(path: str | os.PathLike):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_receipts(path: Path = RECEIPTS) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_ratings_tsv(path: Path = RATINGS_TSV) -> dict[str, dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return {r["video_id"]: r for r in csv.DictReader(fh, delimiter="\t")}


def load_manifest(path: Path = MANIFEST_V5) -> dict:
    return read_json(path)


def manifest_songs(path: Path = MANIFEST_V5) -> list[dict]:
    """Songs with in_v5_corpus, sorted by v5_priority_rank (the order every v5 consumer uses)."""
    man = load_manifest(path)
    return sorted([s for s in man["songs"] if s.get("in_v5_corpus")], key=lambda s: s["v5_priority_rank"])


def load_tempo_overrides(path: Path = TEMPO_OVERRIDES_V6) -> dict[str, float]:
    """Read data/v6/corpus/tempo_overrides_v6.json ({sha16: bpm} or {"overrides": {...}}); absent -> defaults."""
    if not Path(path).exists():
        return dict(TEMPO_OVERRIDES_DEFAULT)
    d = read_json(path)
    body = d.get("overrides", d) if isinstance(d, dict) else {}
    return {str(k): float(v) for k, v in body.items() if not str(k).startswith("_")}


def ensure_tempo_overrides_file(path: Path = TEMPO_OVERRIDES_V6) -> bool:
    """Ship the default overrides file if absent (data/ is gitignored, so the code is the source of truth)."""
    if Path(path).exists():
        return False
    body = {"schema_version": 1, "env_pin_sha256": ENV_PIN_SHA256,
            "overrides": dict(TEMPO_OVERRIDES_DEFAULT),
            "note": ("{sha16: bpm}. Applied by scripts/v6/tempo_v6.py AFTER estimation; the overridden value is what "
                     "data/v5/corpus/<sha16>/tempo_v5.json carries as bpm_v5. Disco A = F4 operator-adopted 120.272335 "
                     "(c86); the old librosa estimate 80.75 is a 3:2 error."),
            "sources": {"cdd2717e52820ff6": "docs/guidance/guidance_2026-09-09_F2_velocity_decision.txt addendum (F4 close, c86)"}}
    return write_json_atomic(path, body)
