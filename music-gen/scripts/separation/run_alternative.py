"""
Run open-unmix UMXHQ on each M-SEP-1 synth mix and save 4-stem WAVs.

UMXHQ was chosen after the fetchability probe cleared both the wheel
(openunmix 1.3.0) and the Zenodo weights (34 MB per target).
All openunmix deps were already satisfied in the top-level env, so no
workspace/separation_venv/ was needed.

Determinism: torch.manual_seed(0) before separator.forward.
Interpreter: /usr/bin/python3.

Outputs:
    data/separation/runs/openunmix/<mix_id>/{vocals,drums,bass,other}.wav
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

assert sys.executable == "/usr/bin/python3", sys.executable

# Point torch.hub at a workspace-local cache so weight fetches are recorded.
os.environ.setdefault("TORCH_HOME", str(Path(__file__).resolve().parents[2] / "workspace/_probe/torch_home"))
os.makedirs(os.environ["TORCH_HOME"], exist_ok=True)

import openunmix  # noqa: E402

ROOT = Path("/home/user/long-exposure-runs/music-gen")
MANIFEST = ROOT / "data/separation/synth_mix/manifest.json"
OUT_ROOT = ROOT / "data/separation/runs/openunmix"
STEM_ORDER = ["vocals", "drums", "bass", "other"]


def main() -> None:
    torch.manual_seed(0)
    manifest = json.loads(MANIFEST.read_text())
    sep = openunmix.umxhq(targets=STEM_ORDER, niter=1, residual=False)
    sep.eval()

    for mix in manifest["mixes"]:
        mix_path = ROOT / mix["mix"]["path"]
        mix_id = mix["mix_id"]
        out_dir = OUT_ROOT / mix_id
        out_dir.mkdir(parents=True, exist_ok=True)

        y, sr = sf.read(str(mix_path), always_2d=True)
        assert sr == 44100
        if y.shape[1] == 1:
            y = np.concatenate([y, y], axis=1)
        # separator expects (nb_samples, nb_channels, nb_timesteps)
        wav = torch.from_numpy(y.T.astype(np.float32)).unsqueeze(0)
        with torch.no_grad():
            estimates = sep(wav)
        # estimates shape: (nb_samples, nb_targets, nb_channels, nb_timesteps)
        arr = estimates[0].numpy()  # (nb_targets, nb_channels, nb_timesteps)
        for i, name in enumerate(STEM_ORDER):
            stem = arr[i].T  # (samples, channels)
            sf.write(str(out_dir / f"{name}.wav"), stem.astype(np.float32), sr, subtype="FLOAT")
        print(f"openunmix {mix_id}: wrote {len(STEM_ORDER)} stems -> {out_dir}")


if __name__ == "__main__":
    main()
