"""RC0 baseline capture for M-RECREATE-2 focus set.
For each focus song, compute per-stem SHAs + RC-specific reference
measurements against READ-ONLY htdemucs stems from c39-42.

Runs BEFORE any script under scripts/recreate_v2/. Scratchpad-only.

Baseline directory layout:
  data/recreate_v2/baseline/<sha16>/
    per_stem_manifest.json       # SHA/RMS/centroid/LUFS per stem
    rc1_vocals_voiced_time_s.json
    rc2_drum_onset_count.json
    rc3_bass_pyin_voiced_segments.json
    rc3_bass_low_band_energy.json
    rc5_tempo_bpm.json
    rc6_centroid_time_series.npy
    rc6_vggish_or_none.json      # honest None if VGGish not available
"""
import hashlib
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

assert sys.executable == "/usr/bin/python3", sys.executable

# BLAS pins.
for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[k] = "1"
os.environ["PYTHONHASHSEED"] = "0"
os.environ["SOURCE_DATE_EPOCH"] = "1756463424"
os.environ["TZ"] = "UTC"
os.environ["LC_ALL"] = "C.UTF-8"

import numpy as np
import soundfile as sf
import librosa
import pyloudnorm as pyln
import torch

torch.set_num_threads(1)
torch.manual_seed(0)

ROOT = Path("/home/user/long-exposure-runs/music-gen")
os.chdir(ROOT)

TRIM_S = 30.0

def sha_bytes(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def load_trim(path, target_sr=None, mono=False, trim_s=TRIM_S):
    y, sr = sf.read(str(path), always_2d=True)
    if target_sr and sr != target_sr:
        # keep native sr; measurements handle their own resampling
        pass
    n = int(trim_s * sr)
    y = y[:n]
    if mono:
        y = y.mean(axis=1)
    return y, sr

def rms_of(y):
    return float(np.sqrt(np.mean(y.astype(np.float64) ** 2)))

def centroid_mean(y_mono, sr):
    S = np.abs(librosa.stft(y_mono, n_fft=2048, hop_length=512))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    mag = S.sum(axis=0) + 1e-12
    per_frame = (freqs[:, None] * S).sum(axis=0) / mag
    return float(per_frame.mean())

def lufs_m_of(y_stereo, sr):
    # y_stereo shape (n, 2) linear float
    if y_stereo.ndim == 1:
        y_stereo = np.stack([y_stereo, y_stereo], axis=1)
    meter = pyln.Meter(sr)
    try:
        return float(meter.integrated_loudness(y_stereo.astype(np.float32)))
    except Exception:
        return None

def per_stem_manifest(stems_dir, out_path):
    manifest = {}
    for stem in ("vocals", "drums", "bass", "other"):
        p = stems_dir / f"{stem}.wav"
        if not p.exists():
            manifest[stem] = {"status": "MISSING"}
            continue
        y, sr = load_trim(p)
        y_mono = y.mean(axis=1) if y.ndim == 2 else y
        manifest[stem] = {
            "path": str(p.relative_to(ROOT)),
            "sha256": sha_bytes(p),
            "sample_rate": int(sr),
            "duration_s_trimmed": float(len(y) / sr),
            "rms": rms_of(y_mono),
            "spectral_centroid_mean_hz": centroid_mean(y_mono, sr),
            "lufs_m": lufs_m_of(y, sr),
        }
    out_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest

def rc1_vocals_voiced_time(stems_dir, out_path):
    vocals = stems_dir / "vocals.wav"
    y, sr = load_trim(vocals, mono=True)
    f0, voiced_flag, _ = librosa.pyin(
        y.astype(np.float32), fmin=float(librosa.note_to_hz("C2")),
        fmax=float(librosa.note_to_hz("C7")), sr=sr,
    )
    voiced_frames = int(np.sum(voiced_flag)) if voiced_flag is not None else 0
    total_frames = len(voiced_flag) if voiced_flag is not None else 0
    hop = 512
    voiced_time_s = float(voiced_frames * hop / sr)
    total_time_s = float(len(y) / sr)
    result = {
        "voiced_frames": voiced_frames,
        "total_frames": int(total_frames),
        "voiced_time_s": voiced_time_s,
        "total_time_s": total_time_s,
        "voiced_fraction": (voiced_time_s / total_time_s) if total_time_s > 0 else 0.0,
        "pyin_fmin_hz": float(librosa.note_to_hz("C2")),
        "pyin_fmax_hz": float(librosa.note_to_hz("C7")),
        "hop_length": hop,
    }
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result

def rc2_drum_onsets(stems_dir, out_path):
    drums = stems_dir / "drums.wav"
    y, sr = load_trim(drums, mono=True)
    onsets = librosa.onset.onset_detect(y=y.astype(np.float32), sr=sr, units="time")
    result = {
        "onset_count": int(len(onsets)),
        "onset_times_s": [float(x) for x in onsets],
        "sample_rate": int(sr),
        "duration_s": float(len(y) / sr),
        "onset_detector": "librosa.onset.onset_detect(units='time', default params)",
    }
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result

def rc3_bass_measurements(stems_dir, out_path_pyin, out_path_lowband):
    bass = stems_dir / "bass.wav"
    y, sr = load_trim(bass, mono=True)
    # pyin voiced segments
    f0, voiced_flag, _ = librosa.pyin(
        y.astype(np.float32), fmin=30.0, fmax=350.0, sr=sr,
    )
    # count contiguous voiced runs (=voiced-segment count)
    voiced = np.asarray(voiced_flag, dtype=bool) if voiced_flag is not None else np.array([], dtype=bool)
    if len(voiced) == 0:
        n_segments = 0
    else:
        d = np.diff(voiced.astype(int))
        n_segments = int(np.sum(d == 1) + (1 if voiced[0] else 0))
    hop = 512
    pyin_out = {
        "voiced_segments_count": n_segments,
        "voiced_frames": int(np.sum(voiced)),
        "total_frames": int(len(voiced)),
        "pyin_fmin_hz": 30.0, "pyin_fmax_hz": 350.0, "hop_length": hop,
    }
    out_path_pyin.write_text(json.dumps(pyin_out, indent=2, sort_keys=True) + "\n")
    # low-band (<250 Hz) energy envelope
    n_fft = 2048
    S = np.abs(librosa.stft(y.astype(np.float32), n_fft=n_fft, hop_length=hop))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    lowband_mask = freqs < 250.0
    lb_env = S[lowband_mask].sum(axis=0)
    total_energy_lb = float(np.sum(lb_env ** 2))
    lb_out = {
        "low_band_hz_upper": 250.0,
        "envelope_frames": int(len(lb_env)),
        "envelope_total_energy": total_energy_lb,
        "envelope_mean": float(lb_env.mean()),
        "envelope_std": float(lb_env.std()),
        "envelope_first_10": [float(x) for x in lb_env[:10]],
        "sample_rate": int(sr), "hop_length": hop, "n_fft": n_fft,
    }
    out_path_lowband.write_text(json.dumps(lb_out, indent=2, sort_keys=True) + "\n")
    return pyin_out, lb_out

def rc5_tempo(original_path, out_path):
    y, sr = load_trim(original_path, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y.astype(np.float32), sr=sr, units="time")
    tempo_scalar = float(tempo) if np.ndim(tempo) == 0 else float(np.asarray(tempo).ravel()[0])
    result = {
        "estimated_bpm": tempo_scalar,
        "beat_count": int(len(beats)),
        "beat_times_s_first_20": [float(x) for x in beats[:20]],
        "sample_rate": int(sr), "duration_s": float(len(y) / sr),
        "detector": "librosa.beat.beat_track(units='time')",
    }
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result

def rc6_centroid_series(original_path, out_path_ts, out_path_vggish_note):
    y, sr = load_trim(original_path, mono=True)
    S = np.abs(librosa.stft(y.astype(np.float32), n_fft=2048, hop_length=512))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    mag = S.sum(axis=0) + 1e-12
    centroid = (freqs[:, None] * S).sum(axis=0) / mag
    np.save(out_path_ts, centroid.astype(np.float32))
    # VGGish attempt (torchvggish etc.). Honest None if unavailable.
    vggish_note = {
        "status": "DEFERRED",
        "reason": (
            "c11 CLAP anti-pattern locked; VGGish rung was verified in the "
            "c14 embedding-content-flip work but its runtime output is "
            "content-dependent (see anti-pattern). c50+ RC6 branch owner "
            "must instantiate VGGish via the M-TEX-1/panel embedding "
            "surface (scripts.texture.panel) at RC6 landing, not here. "
            "This baseline pins the mel-family and centroid-family "
            "references; the embedding reference is captured by the RC6 "
            "branch itself when it wires in the panel."
        ),
        "centroid_time_series_shape": list(centroid.shape),
        "centroid_time_series_dtype": "float32",
        "hop_length": 512, "n_fft": 2048,
        "sample_rate": int(sr), "duration_s": float(len(y) / sr),
    }
    out_path_vggish_note.write_text(json.dumps(vggish_note, indent=2, sort_keys=True) + "\n")
    return {"centroid_frames": int(len(centroid))}

def process_song(song, target_dir):
    sha16 = song["audio_sha16"]
    band = song["rating_band"]
    stems_dir = ROOT / f"data/recreate_v0_full_corpus/per_song/{band}/{sha16}/per_stage/04_htdemucs"
    if not stems_dir.exists():
        return {"status": "STEMS_MISSING", "stems_dir": str(stems_dir.relative_to(ROOT))}

    song_dir = target_dir / sha16
    song_dir.mkdir(parents=True, exist_ok=True)

    manifest = per_stem_manifest(stems_dir, song_dir / "per_stem_manifest.json")
    rc1 = rc1_vocals_voiced_time(stems_dir, song_dir / "rc1_vocals_voiced_time_s.json")
    rc2 = rc2_drum_onsets(stems_dir, song_dir / "rc2_drum_onset_count.json")
    rc3_pyin, rc3_lb = rc3_bass_measurements(
        stems_dir,
        song_dir / "rc3_bass_pyin_voiced_segments.json",
        song_dir / "rc3_bass_low_band_energy.json",
    )
    original_path = ROOT / song["path"]
    rc5 = rc5_tempo(original_path, song_dir / "rc5_tempo_bpm.json")
    rc6 = rc6_centroid_series(
        original_path,
        song_dir / "rc6_centroid_time_series.npy",
        song_dir / "rc6_vggish_or_none.json",
    )
    summary = {
        "sha16": sha16, "band": band, "title": song["title"],
        "stems_dir": str(stems_dir.relative_to(ROOT)),
        "per_stem_manifest": manifest,
        "rc1_voiced_time_s": rc1["voiced_time_s"],
        "rc2_drum_onset_count": rc2["onset_count"],
        "rc3_bass_voiced_segments_count": rc3_pyin["voiced_segments_count"],
        "rc3_bass_low_band_mean": rc3_lb["envelope_mean"],
        "rc5_estimated_bpm": rc5["estimated_bpm"],
        "rc6_centroid_series_shape": rc6["centroid_frames"],
    }
    (song_dir / "baseline_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary

def dir_sha_manifest(dir_path):
    """Compute per-file SHAs for byte-determinism check."""
    manifest = {}
    for p in sorted(dir_path.rglob("*")):
        if p.is_file():
            manifest[str(p.relative_to(dir_path))] = sha_bytes(p)
    return manifest

def main():
    focus = json.loads(Path("data/recreate_v2/focus_set.json").read_text())
    songs = [s for s in focus["songs"] if s["exists"]]

    # Run 1: primary write to data/recreate_v2/baseline/
    target1 = ROOT / "data/recreate_v2/baseline"
    target1.mkdir(parents=True, exist_ok=True)
    summaries = []
    print(f"=== RUN 1: {len(songs)} songs ===")
    for s in songs:
        print(f"  processing {s['title']} ({s['audio_sha16']}) ...")
        summaries.append(process_song(s, target1))
    manifest1 = dir_sha_manifest(target1)
    (ROOT / "data/recreate_v2/baseline_manifest_run1.json").write_text(
        json.dumps(manifest1, indent=2, sort_keys=True) + "\n")

    # Run 2 for byte-determinism × 2: fresh tempfile.mkdtemp().
    tmp = Path(tempfile.mkdtemp(prefix="rc0_baseline_run2_"))
    print(f"=== RUN 2: fresh temp {tmp} ===")
    torch.manual_seed(0)
    for s in songs:
        process_song(s, tmp)
    manifest2 = dir_sha_manifest(tmp)
    (ROOT / "data/recreate_v2/baseline_manifest_run2.json").write_text(
        json.dumps(manifest2, indent=2, sort_keys=True) + "\n")

    # Byte-det × 2 check
    keys = sorted(set(manifest1) | set(manifest2))
    equal = [k for k in keys if manifest1.get(k) == manifest2.get(k)]
    diff  = [k for k in keys if manifest1.get(k) != manifest2.get(k)]
    result = {
        "run1_file_count": len(manifest1),
        "run2_file_count": len(manifest2),
        "equal_count": len(equal),
        "diff_count": len(diff),
        "diff_files": diff[:20],
        "byte_determinism_pass": (len(diff) == 0 and len(manifest1) == len(manifest2)),
    }
    (ROOT / "data/recreate_v2/baseline_byte_determinism.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"byte-det × 2: {result['byte_determinism_pass']} "
          f"({len(equal)}/{len(keys)} equal, {len(diff)} diff)")

    shutil.rmtree(tmp)

    # Roll up.
    rollup = {
        "cycle": 49,
        "n_focus_songs": len(songs),
        "songs_processed": [s["title"] for s in songs],
        "byte_determinism_pass": result["byte_determinism_pass"],
        "rubric_sha256": Path("data/recreate_v2/rubric_hash.txt").read_text().strip(),
        "per_song": summaries,
    }
    (ROOT / "data/recreate_v2/rc0_baseline_rollup.json").write_text(
        json.dumps(rollup, indent=2, sort_keys=True) + "\n")
    print("=== DONE ===")

if __name__ == "__main__":
    main()
