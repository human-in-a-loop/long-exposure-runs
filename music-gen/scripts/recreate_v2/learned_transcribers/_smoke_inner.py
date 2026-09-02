#!/usr/bin/env python3
# created: 2026-09-02T07:15:00Z
# cycle: 57 clone-2
# agent: worker
# milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/learned-transcribers
"""Venv-inner smoke-test driver. Called via subprocess from the /usr/bin/python3
orchestrator with (model, stem_wav, out_json) args. Env pins + torch.manual_seed(0)
applied here at entry (single allowlisted PRNG-seed site).

Guard: this file must run under the quarantined venv python, not system python.
"""
import argparse
import hashlib
import json
import os
import pathlib
import sys

# c48 env-flags default OFF
os.environ.setdefault("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", "0")
os.environ.setdefault("MUSICGEN_LEDGER_SUPERSEDES_IN_HASH", "0")

def _venv_guard():
    """Verify inner-python's sys.path contains the quarantined venv
    site-packages. sys.executable is a symlink to /usr/bin/python3.11 so
    check the resolved venv site-packages string instead."""
    marker = "workspace/learned_transcribers_venv"
    hits = [p for p in sys.path if marker in p]
    if not hits:
        raise RuntimeError(f"venv guard: no {marker} entry in sys.path: {sys.path}")


def _seed():
    # Single allowlisted torch PRNG-seed site.
    try:
        import torch
        torch.manual_seed(0)
    except ImportError:
        pass


def smoke_torchcrepe(stem_wav, out_json):
    import numpy as np
    import soundfile as sf
    import torch
    import torchcrepe

    audio, sr = sf.read(str(stem_wav), dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    # Resample to 16k for crepe
    if sr != 16000:
        # simple linear resample via numpy (deterministic)
        n_new = int(round(len(audio) * 16000 / sr))
        idx = np.linspace(0, len(audio) - 1, n_new)
        audio = np.interp(idx, np.arange(len(audio)), audio).astype("float32")
        sr = 16000
    x = torch.tensor(audio).unsqueeze(0)
    hop = 160  # 10 ms @16k
    # tiny model to reduce weight download; deterministic
    pitch, periodicity = torchcrepe.predict(
        x, sr, hop, fmin=50.0, fmax=1100.0, model="tiny",
        return_periodicity=True, device="cpu", batch_size=512,
    )
    notes = []
    p = pitch[0].numpy()
    per = periodicity[0].numpy()
    # simple segmentation: voiced when periodicity > 0.5 and pitch finite
    voiced = (per > 0.5) & np.isfinite(p) & (p > 40)
    # find contiguous voiced regions with roughly-stable pitch (± 50 cents)
    i = 0
    while i < len(voiced):
        if not voiced[i]:
            i += 1
            continue
        j = i
        anchor = p[i]
        while j < len(voiced) and voiced[j] and abs(1200 * np.log2(p[j] / max(anchor, 1e-6))) < 100:
            j += 1
        onset_s = i * hop / sr
        dur_s = (j - i) * hop / sr
        if dur_s >= 0.04:
            midi = int(round(69 + 12 * np.log2(np.mean(p[i:j]) / 440.0)))
            notes.append({
                "onset_s": float(onset_s),
                "duration_s": float(dur_s),
                "midi": midi,
                "articulation": "sustained",
            })
        i = j
    out = {
        "model": "torchcrepe==0.0.24",
        "model_variant": "tiny",
        "stem": str(stem_wav),
        "sample_rate_in": sr,
        "notes_count": len(notes),
        "notes": notes,
        "vocabulary": "f0_pitch_midi",
    }
    pathlib.Path(out_json).write_text(json.dumps(out, sort_keys=True, separators=(",", ":")))
    return out


def smoke_piano_bytedance(stem_wav, out_json):
    # Bundled inference wrapper attempts to download the CRNN weights on init.
    # This will FETCH_FAIL if the CDN is blocked by the workspace proxy.
    import piano_transcription_inference as pti
    import librosa

    audio, _ = librosa.core.load(str(stem_wav), sr=pti.sample_rate, mono=True)
    # PianoTranscription() downloads weights at __init__ time
    transcriptor = pti.PianoTranscription(device="cpu", checkpoint_path=None)
    tmp_mid = pathlib.Path(out_json).with_suffix(".mid")
    out = transcriptor.transcribe(audio, str(tmp_mid))
    # `out` includes est_note_events; serialize a canonical subset
    notes = []
    if hasattr(out, "get") and out.get("est_note_events") is not None:
        for e in out["est_note_events"]:
            notes.append({
                "onset_s": float(e.get("onset_time", 0.0)),
                "duration_s": float(e.get("offset_time", 0.0) - e.get("onset_time", 0.0)),
                "midi": int(e.get("midi_note", 0)),
                "velocity": int(e.get("velocity", 0)),
            })
    canon = {
        "model": "piano_transcription_inference",
        "stem": str(stem_wav),
        "sample_rate_in": pti.sample_rate,
        "notes_count": len(notes),
        "notes": notes,
        "vocabulary": "88_key_piano",
    }
    pathlib.Path(out_json).write_text(json.dumps(canon, sort_keys=True, separators=(",", ":")))
    return canon


def main():
    _venv_guard()
    _seed()
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=["torchcrepe", "piano_bytedance"])
    ap.add_argument("--stem", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.model == "torchcrepe":
        smoke_torchcrepe(a.stem, a.out)
    elif a.model == "piano_bytedance":
        smoke_piano_bytedance(a.stem, a.out)
    print(json.dumps({"ok": True, "out": a.out, "sha256": hashlib.sha256(pathlib.Path(a.out).read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
