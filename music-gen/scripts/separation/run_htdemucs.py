"""
Run htdemucs (demucs 4.1.0) on each M-SEP-1 synth mix and save 4-stem WAVs.

Determinism: torch.manual_seed(0) before apply_model.
Interpreter: /usr/bin/python3.

Outputs:
    data/separation/runs/htdemucs/<mix_id>/{vocals,drums,bass,other}.wav
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

assert sys.executable == "/usr/bin/python3", sys.executable

from demucs.apply import apply_model  # noqa: E402
from demucs.pretrained import get_model  # noqa: E402

ROOT = Path("/home/user/long-exposure-runs/music-gen")
MANIFEST = ROOT / "data/separation/synth_mix/manifest.json"
OUT_ROOT = ROOT / "data/separation/runs/htdemucs"
MODEL_NAME = "htdemucs"


def load_mix(path: Path) -> tuple[torch.Tensor, int]:
    y, sr = sf.read(str(path), always_2d=True)
    if y.shape[1] == 1:
        y = np.concatenate([y, y], axis=1)
    # apply_model expects (batch, channels, samples)
    t = torch.from_numpy(y.T.astype(np.float32)).unsqueeze(0)
    return t, sr


def main() -> None:
    torch.manual_seed(0)
    manifest = json.loads(MANIFEST.read_text())
    model = get_model(MODEL_NAME)
    model.eval()
    sources = model.sources  # e.g. ['drums', 'bass', 'other', 'vocals']
    print("htdemucs sources:", sources)

    for mix in manifest["mixes"]:
        mix_path = ROOT / mix["mix"]["path"]
        mix_id = mix["mix_id"]
        out_dir = OUT_ROOT / mix_id
        out_dir.mkdir(parents=True, exist_ok=True)

        wav, sr = load_mix(mix_path)
        assert sr == 44100
        with torch.no_grad():
            estimates = apply_model(
                model, wav, device="cpu",
                shifts=0, split=True, overlap=0.25, num_workers=0, progress=False,
            )
        # estimates: (batch, sources, channels, samples)
        estimates = estimates[0].numpy()  # (sources, channels, samples)
        for i, name in enumerate(sources):
            stem = estimates[i].T  # (samples, channels)
            sf.write(str(out_dir / f"{name}.wav"), stem.astype(np.float32), sr, subtype="FLOAT")
        print(f"htdemucs {mix_id}: wrote {len(sources)} stems -> {out_dir}")


if __name__ == "__main__":
    main()
