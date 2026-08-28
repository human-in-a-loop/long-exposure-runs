#!/usr/bin/env -S /usr/bin/python3
"""Write one non-factor sidecar per validation clip.

Populates only the model-derived fields (non-music-class posteriors).
All curatorial labels (genre/country/date/language/instrumental/artist)
are None this cycle — the labels don't exist yet in this workspace;
what's being validated is the ARCHITECTURAL CONTRACT of the sidecar.
"""
from __future__ import annotations
from . import _interp  # noqa: F401

import json
from pathlib import Path

from .sidecar_nonfactor import NONFACTOR_ROOT, write_sidecar
from .tagger import MODEL_ID, Tagger, sha256_of, DEFAULT_WEIGHTS


PREDS = Path("data/classifier/predictions.jsonl")


def main() -> int:
    NONFACTOR_ROOT.mkdir(parents=True, exist_ok=True)
    # Weights sha for provenance (avoid re-loading the model).
    weights_sha = sha256_of(DEFAULT_WEIGHTS) if DEFAULT_WEIGHTS.exists() else "unknown"
    n = 0
    for line in PREDS.read_text().splitlines():
        r = json.loads(line)
        probs = r["class_probs"]
        write_sidecar(
            clip_id=r["clip_id"],
            genre=None,                    # labels do not exist yet
            country=None,
            date_released=None,
            language=None,
            instrumental_vs_lyrics=None,
            live_vs_recorded=None,
            artist=None,
            prob_speech=probs["SPEECH"],
            prob_applause=probs["APPLAUSE"],
            prob_ambient=probs["AMBIENT"],
            model_id=MODEL_ID,
            weights_sha256=weights_sha,
        )
        n += 1
    print(f"[sidecar] wrote {n} sidecars to {NONFACTOR_ROOT}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
