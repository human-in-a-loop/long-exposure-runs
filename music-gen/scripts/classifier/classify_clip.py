#!/usr/bin/env -S /usr/bin/python3
"""CLI: classify one WAV clip via PANNs → project taxonomy.

Usage:
    /usr/bin/python3 -m scripts.classifier.classify_clip <wav> [--out clip.json]
"""
from __future__ import annotations
from . import _interp  # noqa: F401

import argparse, json, sys
from pathlib import Path

import numpy as np
import soundfile as sf

from .taxonomy import TaxonomyMapper
from .tagger import Tagger, MODEL_ID


AUDIOSET_CSV = Path("/root/panns_data/class_labels_indices.csv")
TAX_YAML = Path(__file__).parent / "taxonomy_map.yaml"


def classify_file(wav_path: Path, tagger: Tagger, mapper: TaxonomyMapper) -> dict:
    audio, sr = sf.read(str(wav_path), dtype="float32", always_2d=False)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    dist527 = tagger.tag(audio, sr=sr)
    decision = mapper.reduce(dist527)
    return {
        "clip_path": str(wav_path),
        "clip_id": wav_path.stem,
        "sr_in": int(sr),
        "n_samples": int(len(audio)),
        "duration_s": float(len(audio) / sr),
        "model_id": MODEL_ID,
        "weights_sha256": tagger.weights_sha256,
        **decision.to_dict(),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("wav", type=Path)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args(argv)

    tagger = Tagger()
    mapper = TaxonomyMapper(AUDIOSET_CSV, TAX_YAML)
    result = classify_file(args.wav, tagger, mapper)
    text = json.dumps(result, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
