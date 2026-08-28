"""PANNs Cnn14 wrapper — AudioSet-527 tag distribution over a waveform.

Model: Cnn14 (mAP=0.431 on AudioSet), sampling rate 32000 Hz.
Weights fetched at first use to ~/panns_data/ by the panns_inference
package (from Zenodo/GCS). We record the checkpoint SHA-256 on first
load.
"""
from __future__ import annotations
from . import _interp  # noqa: F401 — interpreter guard

import hashlib
from pathlib import Path
from typing import Optional

import numpy as np


MODEL_ID = "panns-cnn14-mAP=0.431"
MODEL_SR = 32000
DEFAULT_WEIGHTS = Path("/root/panns_data/Cnn14_mAP=0.431.pth")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Tagger:
    def __init__(self, weights_path: Optional[Path] = None) -> None:
        # Import lazily to keep interpreter guard fast for --help paths.
        from panns_inference import AudioTagging

        self._weights_path = Path(weights_path) if weights_path else DEFAULT_WEIGHTS
        self._at = AudioTagging(
            checkpoint_path=str(self._weights_path) if self._weights_path.exists() else None,
            device="cpu",
        )
        # panns_inference stores at ~/panns_data by default; grab the actual file.
        if not self._weights_path.exists():
            self._weights_path = DEFAULT_WEIGHTS  # what the package wrote
        self.weights_sha256 = sha256_of(self._weights_path)
        self.model_id = MODEL_ID
        self.sample_rate = MODEL_SR

    def tag(self, waveform: np.ndarray, sr: int = MODEL_SR) -> np.ndarray:
        """Return (527,) AudioSet class distribution for the clip."""
        wav = _prep_waveform(waveform, sr, MODEL_SR)
        # panns_inference API: (batch, T) float32 -> (clipwise_output (B, 527), embedding)
        batch = wav[None, :].astype(np.float32)
        clipwise, _ = self._at.inference(batch)
        return clipwise[0]


def _prep_waveform(waveform: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    import librosa
    if waveform.ndim == 2:
        waveform = np.mean(waveform, axis=0)
    waveform = waveform.astype(np.float32, copy=False)
    if sr_in != sr_out:
        waveform = librosa.resample(waveform, orig_sr=sr_in, target_sr=sr_out)
    # Clip length: PANNs handles arbitrary; 30 s at 32 kHz = 960k samples.
    return waveform
