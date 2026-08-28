#!/usr/bin/env python3
# ---
# created: 2026-08-28T04:38:00Z
# cycle: 1
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1
# ---
"""Ardour ↔ DawDreamer agreement panel.

Compares:
    data/daw_spike/ardour_render.wav
    data/daw_spike/dawdreamer_render_matched.wav   (matched sine source)

Also reports the same panel comparing:
    data/daw_spike/ardour_render.wav
    data/daw_spike/dawdreamer_render.wav           (MIDI-Surge source; expected
                                                    to disagree — for reference)

Metrics:
    - mel-spectral L1 (128 mel bins, log-mel)
    - RMS-envelope RMSE (hop 512)
    - spectral-centroid RMSE
    - peak cross-correlation lag (samples)

Writes:
    data/daw_spike/agreement.json
    data/daw_spike/agreement.png
"""
from __future__ import annotations

import json
import pathlib

import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "daw_spike"
SR = 48000


def load_mono(path: pathlib.Path) -> np.ndarray:
    audio, sr = sf.read(str(path))
    assert sr == SR, f"expected {SR}, got {sr}"
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    return audio.astype(np.float32)


def compare(a: np.ndarray, b: np.ndarray) -> dict:
    # Trim to same length.
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]

    # Mel-spectral L1 (log-mel dB space).
    mel_a = librosa.feature.melspectrogram(y=a, sr=SR, n_mels=128, hop_length=512, n_fft=2048)
    mel_b = librosa.feature.melspectrogram(y=b, sr=SR, n_mels=128, hop_length=512, n_fft=2048)
    log_a = librosa.power_to_db(mel_a + 1e-10)
    log_b = librosa.power_to_db(mel_b + 1e-10)
    mel_l1 = float(np.mean(np.abs(log_a - log_b)))

    # RMS-envelope RMSE (linear amplitude).
    rms_a = librosa.feature.rms(y=a, hop_length=512)[0]
    rms_b = librosa.feature.rms(y=b, hop_length=512)[0]
    n_frames = min(len(rms_a), len(rms_b))
    rms_rmse = float(np.sqrt(np.mean((rms_a[:n_frames] - rms_b[:n_frames]) ** 2)))

    # Spectral-centroid RMSE.
    sc_a = librosa.feature.spectral_centroid(y=a, sr=SR, hop_length=512)[0]
    sc_b = librosa.feature.spectral_centroid(y=b, sr=SR, hop_length=512)[0]
    n_frames = min(len(sc_a), len(sc_b))
    sc_rmse = float(np.sqrt(np.mean((sc_a[:n_frames] - sc_b[:n_frames]) ** 2)))

    # Peak cross-correlation lag on peak-normalized signals (windowed to ±0.5 s).
    a_n = a / (np.max(np.abs(a)) + 1e-12)
    b_n = b / (np.max(np.abs(b)) + 1e-12)
    lag_window = int(0.5 * SR)
    corr = np.correlate(a_n[:5 * SR], b_n[:5 * SR], mode="full")
    center = len(corr) // 2
    lo, hi = center - lag_window, center + lag_window + 1
    corr_win = corr[lo:hi]
    lag_samples = int(np.argmax(corr_win) - lag_window)

    return {
        "mel_l1_db": mel_l1,
        "rms_env_rmse": rms_rmse,
        "spectral_centroid_rmse_hz": sc_rmse,
        "peak_xcorr_lag_samples": lag_samples,
        "n_samples_compared": int(n),
    }


def main() -> None:
    ard = load_mono(OUT / "ardour_render.wav")
    daw_matched = load_mono(OUT / "dawdreamer_render_matched.wav")
    daw_midi = load_mono(OUT / "dawdreamer_render.wav")

    matched_panel = compare(ard, daw_matched)
    ref_panel = compare(ard, daw_midi)

    result = {
        "matched": {
            "ardour": "data/daw_spike/ardour_render.wav (SinGen 220Hz)",
            "dawdreamer": "data/daw_spike/dawdreamer_render_matched.wav (sine 220Hz PlaybackProcessor)",
            "metrics": matched_panel,
            "interpretation": (
                "Both engines process a 220 Hz sine through the SAME Surge XT Effects"
                " VST3 chain (Chorus + Reverb + Output Mix automation) plus a track-gain"
                " ramp. Mel-L1 < 3 dB and rms-env-rmse < 0.05 are the target 'in the same"
                " neighbourhood' bounds — bigger differences reflect (a) different phase"
                " of the SinGen vs sample-perfect sine, (b) block-boundary automation-"
                " timing offsets, (c) Surge XT Effects internal chorus modulation state."
            ),
        },
        "reference_disagreement": {
            "ardour": "data/daw_spike/ardour_render.wav (SinGen 220Hz)",
            "dawdreamer": "data/daw_spike/dawdreamer_render.wav (Surge XT synth on MIDI)",
            "metrics": ref_panel,
            "note": "Expected LARGE disagreement — sources differ (sine vs full MIDI note stream). Reported as reference floor.",
        },
    }
    (OUT / "agreement.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

    # Plot: waveform overlay + RMS envelopes.
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    t = np.arange(len(ard)) / SR
    axes[0].plot(t, ard, label="Ardour render", alpha=0.7, color="tab:blue")
    axes[0].plot(t[:len(daw_matched)], daw_matched, label="DawDreamer matched", alpha=0.7, color="tab:orange")
    axes[0].set_ylabel("amplitude")
    axes[0].set_title("Ardour vs DawDreamer (matched sine 220Hz source)")
    axes[0].legend(loc="upper left")
    axes[0].grid(alpha=0.3)

    rms_a = librosa.feature.rms(y=ard, hop_length=512)[0]
    rms_d = librosa.feature.rms(y=daw_matched, hop_length=512)[0]
    tr = np.arange(len(rms_a)) * 512 / SR
    axes[1].plot(tr, rms_a, label="Ardour rms", color="tab:blue")
    axes[1].plot(tr[:len(rms_d)], rms_d, label="DawDreamer matched rms", color="tab:orange")
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel("rms")
    axes[1].set_title(
        f"RMS envelopes  |  mel-L1={matched_panel['mel_l1_db']:.2f} dB  "
        f"rms-rmse={matched_panel['rms_env_rmse']:.4f}  "
        f"sc-rmse={matched_panel['spectral_centroid_rmse_hz']:.0f} Hz  "
        f"lag={matched_panel['peak_xcorr_lag_samples']} samples"
    )
    axes[1].legend(loc="upper left")
    axes[1].grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUT / "agreement.png", dpi=110)
    plt.close(fig)
    print(f"[OK] wrote {OUT/'agreement.png'}")


if __name__ == "__main__":
    main()
