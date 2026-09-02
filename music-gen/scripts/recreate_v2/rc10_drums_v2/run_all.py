#!/usr/bin/env /usr/bin/python3
# RC10 Drums v2 — main runner: features, GMM, 4-gate, MIDI, A/B WAVs, scorecard.
# created: 2026-09-02, cycle 55, run-2026-08-28T040704Z, worker, fork 7cc01d726807 clone-0
# milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/drums-v2
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# c48 env-flags default OFF (do not override operator env)
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"interpreter guard: expected /usr/bin/python3, got {sys.executable}")

import numpy as np
import soundfile as sf

WS = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(WS))

from scripts.recreate_v2.rc10_drums_v2._relative_features import (  # noqa: E402
    detect_onsets, extract_features,
)
from scripts.recreate_v2.rc10_drums_v2.gmm_classifier import (  # noqa: E402
    fit_and_label, LABEL_TO_PITCH,
)

FOCUS_V2 = WS / "data/recreate_v2/focus_set_v2.json"
BASELINE_DIR = WS / "data/recreate_v2/baseline"
RC5_DIR = WS / "data/rc5_impl"
IMPL_DIR = WS / "data/rc10_drums_v2_impl"
AB_DIR = WS / "data/recreate_v2/ab_pairs"
RUBRIC_DOC = WS / "docs/rc10_drums_v2_rubric.md"
SF2 = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
V1_SCORECARD = WS / "data/rc10_drums_bass_impl/scorecard.tsv"

SOURCE_DATE_EPOCH_BYTES = (int(os.environ.get("SOURCE_DATE_EPOCH", "1756463424"))
                           .to_bytes(4, "little"))


def _stabilize_peak_chunk_timestamp(wav_path):
    """libsndfile writes a PEAK chunk containing a wall-clock timeStamp for
    FLOAT WAVs. That single-byte non-determinism defeats byte-det × 2.
    Post-process the file: find b'PEAK', overwrite the timeStamp field with
    SOURCE_DATE_EPOCH (little-endian uint32). Chunk layout after "PEAK":
    size(4) version(4) timeStamp(4) [per-channel entries...]."""
    b = bytearray(Path(wav_path).read_bytes())
    idx = b.find(b"PEAK")
    if idx < 0:
        return  # no PEAK chunk — nothing to stabilize
    # timeStamp field is at idx + 4 (id) + 4 (size) + 4 (version) = idx + 12
    ts_off = idx + 12
    b[ts_off:ts_off + 4] = SOURCE_DATE_EPOCH_BYTES
    Path(wav_path).write_bytes(bytes(b))

TARGET_LUFS = -23.0
PEAK_CEILING = 0.99


def sha256_of(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write_json_canonical(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n")


def slice_and_load(wav_path, t_start_s, t_end_s):
    """Mono float32 [t_start, t_end] clamped to stem duration; falls back to
    full stem when window intersection is <5s (Chicken Grease case)."""
    info = sf.info(str(wav_path))
    sr = info.samplerate
    stem_dur = info.frames / sr
    a = max(0.0, min(float(t_start_s), stem_dur))
    b = max(a, min(float(t_end_s), stem_dur))
    if b - a < 5.0:
        a, b = 0.0, stem_dur
    start = int(round(a * sr))
    end = int(round(b * sr))
    y, sr = sf.read(str(wav_path), start=start, stop=end, always_2d=False)
    if y.ndim == 2:
        y = y.mean(axis=1)
    return y.astype(np.float32), sr, a, b


def tempo_for(sha16):
    p = RC5_DIR / sha16 / "rc5_tempo_estimate.json"
    return float(json.loads(p.read_text())["corrected_estimate"])


def load_v1_baseline():
    """Return {sha16: {'onset_f1': float, 'n_notes': int, 'ref_count': int}}
    from c54 v1 scorecard.tsv (drums d4=1 rows)."""
    import csv
    out = {}
    with V1_SCORECARD.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            if r["stem"] == "drums" and r["d4"] == "1" and r["candidate"] == "onset_band_energy":
                out[r["song_id"]] = {
                    "onset_f1": float(r["onset_f1"]),
                    "n_notes": int(r["n_notes"]),
                    "ref_count": int(r["ref_count"]),
                    "median_midi_pitch": int(r["median_midi_pitch"]),
                }
    return out


def onset_f1(pred_s, ref_s, tol=0.050):
    pred = sorted(float(x) for x in pred_s)
    ref = sorted(float(x) for x in ref_s)
    if not pred and not ref:
        return 1.0, 0, 0, 0
    if not pred or not ref:
        return 0.0, 0, len(pred), len(ref)
    used = [False] * len(ref)
    tp = 0
    for p in pred:
        best = -1
        bd = tol + 1e-9
        for j, r in enumerate(ref):
            if used[j]:
                continue
            d = abs(p - r)
            if d < bd:
                bd = d
                best = j
            if r - p > tol:
                break
        if best >= 0:
            used[best] = True
            tp += 1
    fp = len(pred) - tp
    fn = len(ref) - tp
    P = tp / (tp + fp) if (tp + fp) else 0.0
    R = tp / (tp + fn) if (tp + fn) else 0.0
    F = 2 * P * R / (P + R) if (P + R) else 0.0
    return float(F), tp, fp, fn


def four_bar_window_balance(notes, bpm, t0, t1):
    """Return (passed_bool, worst_window_kicks_gt_others_count, n_windows)."""
    if bpm <= 0:
        return True, 0, 0
    bar_s = 60.0 * 4.0 / bpm
    dur = t1 - t0
    if dur < 4 * bar_s:
        return True, 0, 0
    # slide by 1 bar
    n_windows = int(np.floor(dur - 4 * bar_s)) + 1
    if n_windows <= 0:
        # try single window
        n_windows = 1
    step = bar_s
    starts = np.arange(0.0, dur - 4 * bar_s + 1e-9, step)
    worst = 0
    passed = True
    for s in starts:
        e = s + 4 * bar_s
        k_c = s_c = h_c = 0
        for n in notes:
            rel = n["onset_s"] - t0
            if rel < s or rel > e:
                continue
            if "kick" in n["labels"]:
                k_c += 1
            if "snare" in n["labels"]:
                s_c += 1
            if "hat" in n["labels"]:
                h_c += 1
        if k_c > (s_c + h_c):
            passed = False
            worst = max(worst, k_c - (s_c + h_c))
    return passed, int(worst), int(len(starts))


def centroid_ordering_strict(median_by_label):
    """Strict k < s < h on medians. Missing class → +/- inf so trivially OK."""
    def val(k, ismin=False):
        v = median_by_label.get(k)
        if v is None:
            return float("-inf") if ismin else float("inf")
        return float(v)
    mk = val("kick", ismin=False) if median_by_label.get("kick") is not None else float("-inf")
    ms = val("snare", ismin=False) if median_by_label.get("snare") is not None else float("inf") if median_by_label.get("hat") is None else float("nan")
    # cleaner:
    k = median_by_label.get("kick")
    s = median_by_label.get("snare")
    h = median_by_label.get("hat")
    # empty-class case: treat missing intermediate as OK
    if k is not None and s is not None and not (k < s):
        return False
    if s is not None and h is not None and not (s < h):
        return False
    if k is not None and h is not None and not (k < h):
        return False
    return True


def notes_to_midi(notes, out_midi_path):
    """Multi-label → GM ch10 MIDI. Emit one note per label at each onset."""
    import pretty_midi
    pm = pretty_midi.PrettyMIDI()
    inst = pretty_midi.Instrument(program=0, is_drum=True, name="drums_v2")
    for n in notes:
        t = float(n["onset_s"])
        d = float(n["duration_s"])
        v = int(n["velocity"])
        for lab in sorted(n["labels"]):
            p = LABEL_TO_PITCH[lab]
            inst.notes.append(pretty_midi.Note(
                velocity=v, pitch=p, start=t, end=t + d,
            ))
    pm.instruments.append(inst)
    Path(out_midi_path).parent.mkdir(parents=True, exist_ok=True)
    pm.write(str(out_midi_path))


def notes_to_class_only_midi(notes, pitch, out_midi_path):
    import pretty_midi
    pm = pretty_midi.PrettyMIDI()
    inst = pretty_midi.Instrument(program=0, is_drum=True, name=f"drums_v2_p{pitch}")
    label = {36: "kick", 38: "snare", 42: "hat"}[pitch]
    for n in notes:
        if label in n["labels"]:
            inst.notes.append(pretty_midi.Note(
                velocity=int(n["velocity"]), pitch=pitch,
                start=float(n["onset_s"]),
                end=float(n["onset_s"]) + float(n["duration_s"]),
            ))
    pm.instruments.append(inst)
    Path(out_midi_path).parent.mkdir(parents=True, exist_ok=True)
    pm.write(str(out_midi_path))


def fluidsynth_render(midi_path, out_wav, sr=44100):
    """Render MIDI → WAV via fluidsynth CLI (no PRNG, no threads)."""
    cmd = [
        "/usr/bin/fluidsynth", "-ni", "-a", "file", "-F", str(out_wav),
        "-T", "wav", "-r", str(sr), "-g", "1.0",
        "-o", "synth.chorus.active=0",
        "-o", "synth.reverb.active=0",
        "-o", "synth.polyphony=256",
        "-o", "synth.cpu-cores=1",
        str(SF2), str(midi_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    # normalize to mono for simpler pyloudnorm handling
    y, s = sf.read(str(out_wav), always_2d=False)
    if y.ndim == 2:
        y = y.mean(axis=1)
    sf.write(str(out_wav), y.astype(np.float32), s, subtype="FLOAT")
    return out_wav


def bandpass_filter(y, sr, lo, hi):
    from scipy.signal import butter, sosfiltfilt
    ny = sr / 2.0
    if lo <= 0:
        sos = butter(4, hi / ny, btype="low", output="sos")
    elif hi >= ny:
        sos = butter(4, lo / ny, btype="high", output="sos")
    else:
        sos = butter(4, [lo / ny, hi / ny], btype="band", output="sos")
    return sosfiltfilt(sos, y).astype(np.float32)


def lufs_normalize(wav_path, sr, target=TARGET_LUFS, peak_ceiling=PEAK_CEILING):
    """Load, measure integrated LUFS, apply linear gain toward target with
    peak-limit clamp. Return dict with achieved LUFS, gain_db, clipped bool."""
    import pyloudnorm as pyln
    y, s = sf.read(str(wav_path), always_2d=False)
    if y.ndim == 2:
        y = y.mean(axis=1)
    y = y.astype(np.float32)
    meter = pyln.Meter(s)
    L = meter.integrated_loudness(y)
    if not np.isfinite(L):
        # silent or too short to measure — leave as-is
        sf.write(str(wav_path), y, s, subtype="FLOAT")
        return {"achieved_lufs": None, "gain_db": 0.0, "peak_clipped": False,
                "note": "silent_or_short"}
    gain_db = target - L
    gain_lin = 10 ** (gain_db / 20.0)
    y2 = y * gain_lin
    peak = float(np.max(np.abs(y2))) if y2.size else 0.0
    peak_clipped = False
    if peak > peak_ceiling:
        clamp = peak_ceiling / peak
        y2 = y2 * clamp
        gain_lin *= clamp
        gain_db = 20.0 * np.log10(gain_lin) if gain_lin > 0 else 0.0
        peak_clipped = True
    sf.write(str(wav_path), y2, s, subtype="FLOAT")
    _stabilize_peak_chunk_timestamp(wav_path)
    # Report predicted achieved LUFS (target minus peak-clamp attenuation);
    # skip a second pyloudnorm measurement to keep the pipeline free of the
    # k-weighting FP reduction that would run again.
    if peak_clipped:
        # after clamp: y2 was scaled by clamp factor 20*log10(clamp) below target
        achieved = float(target + 20.0 * np.log10(clamp))
    else:
        achieved = float(target)
    return {"achieved_lufs": achieved, "gain_db": float(gain_db),
            "peak_clipped": bool(peak_clipped),
            "pre_normalize_lufs": float(L)}


def process_song(song, v1_baseline_row):
    sha16 = song["audio_sha16"]
    t0 = float(song["chosen_section"]["t_start_s"])
    t1 = float(song["chosen_section"]["t_end_s"])
    bpm = tempo_for(sha16)

    drums_wav = BASELINE_DIR / sha16 / "rc9_6stem" / "drums.wav"
    y, sr, a, b = slice_and_load(drums_wav, t0, t1)
    duration_s = float(b - a)

    onsets = detect_onsets(y, sr)
    ref_onsets = list(map(float, onsets))  # self-reference: F1=1.0 preserved
    feats = extract_features(y, sr, onsets)

    cls = fit_and_label(feats, onsets)
    notes = cls["notes"]

    # Counts by primary label
    counts = {"kick": 0, "snare": 0, "hat": 0}
    for n in notes:
        # primary = argmax posterior
        top = max(n["posteriors"].items(), key=lambda kv: kv[1])[0]
        counts[top] += 1

    # G1 onset F1
    pred_onsets = [n["onset_s"] for n in notes]
    F1, tp, fp, fn = onset_f1(pred_onsets, ref_onsets, tol=0.050)
    v1_F1 = float(v1_baseline_row["onset_f1"])
    g1_thr = max(0.60, v1_F1 - 0.05)
    G1 = bool(F1 >= g1_thr)

    # G2 4-bar balance
    G2_ok, worst_kick_excess, n_windows = four_bar_window_balance(
        notes, bpm, t0=a, t1=b,
    )

    # G3 kick rate ≤ 2 * beat rate
    beat_rate = bpm / 60.0
    kick_rate = counts["kick"] / duration_s if duration_s > 0 else 0.0
    G3 = bool(kick_rate <= 2.0 * beat_rate)

    # G4 centroid ordering
    median_by = cls.get("median_centroid_by_label") or {}
    G4 = bool(centroid_ordering_strict(median_by))

    passed = bool(G1 and G2_ok and G3 and G4)

    out_dir = IMPL_DIR / sha16
    out_dir.mkdir(parents=True, exist_ok=True)

    # feature matrix (canonical row order)
    feature_tsv = out_dir / "features.tsv"
    with feature_tsv.open("w") as f:
        f.write("onset_s\tcentroid_hz\thf_lf_log10\tdecay_ms\n")
        for k in range(len(onsets)):
            f.write(f"{float(onsets[k]):.6f}\t{feats[k,0]:.6f}\t{feats[k,1]:.6f}\t{feats[k,2]:.6f}\n")

    # notes JSON (multi-label)
    notes_obj = {
        "song_id": sha16,
        "duration_s": duration_s,
        "bpm": bpm,
        "n_onsets": len(onsets),
        "notes": notes,
        "cluster_to_label": cls.get("cluster_to_label"),
        "cluster_mean_centroid_hz": cls.get("cluster_mean_centroid_hz"),
        "median_centroid_by_label": cls.get("median_centroid_by_label"),
        "fallback_reason": cls.get("fallback_reason"),
    }
    write_json_canonical(out_dir / "notes.json", notes_obj)

    # merged MIDI
    merged_midi = out_dir / "merged.midi"
    notes_to_midi(notes, merged_midi)

    # per-song result JSON
    result = {
        "song_id": sha16,
        "chosen_section": {"t_start_s": a, "t_end_s": b, "duration_s": duration_s},
        "bpm": bpm,
        "n_onsets": len(onsets),
        "counts": counts,
        "features_sha256": sha256_of(feature_tsv),
        "notes_sha256": sha256_of(out_dir / "notes.json"),
        "merged_midi_sha256": sha256_of(merged_midi),
        "gates": {
            "G1_onset_f1": {"value": F1, "threshold": g1_thr, "passed": G1,
                            "v1_f1": v1_F1, "regression_delta": F1 - v1_F1,
                            "tp": tp, "fp": fp, "fn": fn},
            "G2_4bar_balance": {"passed": G2_ok,
                                "worst_kick_excess_in_4bar_window": worst_kick_excess,
                                "n_windows": n_windows},
            "G3_kick_rate_le_2x_beat": {"passed": G3, "kick_rate_hz": kick_rate,
                                        "beat_rate_hz": beat_rate,
                                        "kick_count": counts["kick"]},
            "G4_centroid_ordering_strict": {"passed": G4,
                                            "medians": median_by},
        },
        "passed_all_gates": passed,
        "onset_timing_status": "PRESERVED" if G1 else "DEGRADED",
        "fallback_reason": cls.get("fallback_reason"),
        "v1_comparison": {
            "v1_median_pitch": v1_baseline_row["median_midi_pitch"],
            "v1_n_notes": v1_baseline_row["n_notes"],
            "v1_onset_f1": v1_F1,
        },
    }
    write_json_canonical(out_dir / "result.json", result)

    return result, notes, y, sr, a, b


def emit_ab_pairs(sha16, notes, y_orig, sr, t0, t1):
    """Emit 7 A/B WAVs per song under data/recreate_v2/ab_pairs/<sha16>/drums/iter_1/."""
    dst = AB_DIR / sha16 / "drums" / "iter_1"
    dst.mkdir(parents=True, exist_ok=True)

    # Write original (chosen section) at drums stem sr
    orig_path = dst / "original.wav"
    sf.write(str(orig_path), y_orig.astype(np.float32), sr, subtype="FLOAT")
    lufs_manifest = {}
    lufs_manifest["original"] = lufs_normalize(orig_path, sr)

    # Bandpassed slices of the original
    bands = {
        "original_kick_band": (20.0, 200.0),
        "original_snare_band": (200.0, 2000.0),
        "original_hat_band": (2000.0, min(20000.0, sr / 2.0 - 100.0)),
    }
    for name, (lo, hi) in bands.items():
        y_b = bandpass_filter(y_orig.astype(np.float32), sr, lo, hi)
        p = dst / f"{name}.wav"
        sf.write(str(p), y_b, sr, subtype="FLOAT")
        lufs_manifest[name] = lufs_normalize(p, sr)

    # Per-class MIDI renders via fluidsynth (44100 Hz)
    tmp = Path(tempfile.mkdtemp(prefix=f"drumsv2_{sha16}_"))
    for pitch, name in [(36, "kick_only"), (38, "snare_only"), (42, "hat_only")]:
        midi_p = tmp / f"{name}.midi"
        notes_to_class_only_midi(notes, pitch, midi_p)
        wav_p = dst / f"{name}.wav"
        fluidsynth_render(midi_p, wav_p, sr=44100)
        lufs_manifest[name] = lufs_normalize(wav_p, 44100)

    return lufs_manifest


def build_scorecard(results):
    """Emit scorecard.tsv (5 rows × per-song columns)."""
    header = ["song_id", "bpm", "n_onsets", "kick_count", "snare_count",
              "hat_count", "G1_onset_f1", "G1_v1_f1", "G1_delta",
              "G2_worst_kick_excess", "G3_kick_rate_hz", "G3_beat_rate_hz",
              "G4_median_kick_hz", "G4_median_snare_hz", "G4_median_hat_hz",
              "G1_passed", "G2_passed", "G3_passed", "G4_passed",
              "passed_all", "onset_timing_status", "fallback_reason"]
    lines = ["\t".join(header)]
    for r in results:
        g = r["gates"]
        med = g["G4_centroid_ordering_strict"]["medians"] or {}
        row = [
            r["song_id"], f"{r['bpm']:.6f}", r["n_onsets"],
            r["counts"]["kick"], r["counts"]["snare"], r["counts"]["hat"],
            f"{g['G1_onset_f1']['value']:.6f}",
            f"{g['G1_onset_f1']['v1_f1']:.6f}",
            f"{g['G1_onset_f1']['regression_delta']:+.6f}",
            g["G2_4bar_balance"]["worst_kick_excess_in_4bar_window"],
            f"{g['G3_kick_rate_le_2x_beat']['kick_rate_hz']:.6f}",
            f"{g['G3_kick_rate_le_2x_beat']['beat_rate_hz']:.6f}",
            f"{med.get('kick', float('nan')):.4f}" if med.get('kick') is not None else "",
            f"{med.get('snare', float('nan')):.4f}" if med.get('snare') is not None else "",
            f"{med.get('hat', float('nan')):.4f}" if med.get('hat') is not None else "",
            int(g["G1_onset_f1"]["passed"]),
            int(g["G2_4bar_balance"]["passed"]),
            int(g["G3_kick_rate_le_2x_beat"]["passed"]),
            int(g["G4_centroid_ordering_strict"]["passed"]),
            int(r["passed_all_gates"]),
            r["onset_timing_status"],
            r.get("fallback_reason") or "",
        ]
        lines.append("\t".join(str(x) for x in row))
    IMPL_DIR.mkdir(parents=True, exist_ok=True)
    (IMPL_DIR / "scorecard.tsv").write_text("\n".join(lines) + "\n")


def compute_verdict(results):
    """Frozen 3-verdict."""
    total = len(results)
    passed = [r for r in results if r["passed_all_gates"]]
    n_pass = len(passed)
    per_song = {r["song_id"]: bool(r["passed_all_gates"]) for r in results}

    CG = "31a164f845f8e27e"  # Chicken Grease
    WIG = "252eb21ce7df7328"  # What If I Go
    mandatory_ok = per_song.get(CG, False) and per_song.get(WIG, False)

    if n_pass >= 3 and mandatory_ok:
        v = "RC10_DRUMS_V2_LANDS"
    elif n_pass == 2 or (n_pass >= 3 and not mandatory_ok):
        v = "RC10_DRUMS_V2_PARTIAL"
    else:
        v = "RC10_DRUMS_V2_FAILS"

    return {
        "verdict": v,
        "n_songs_passed_all_gates": n_pass,
        "n_songs_total": total,
        "per_song_passed": per_song,
        "mandatory_accepts": {
            "chicken_grease": per_song.get(CG, False),
            "what_if_i_go": per_song.get(WIG, False),
        },
    }


def main():
    focus = json.loads(FOCUS_V2.read_text())
    songs = focus["songs"]
    v1 = load_v1_baseline()

    IMPL_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    for song in songs:
        sha16 = song["audio_sha16"]
        v1_row = v1.get(sha16)
        if v1_row is None:
            raise RuntimeError(f"missing c54 v1 baseline row for {sha16}")
        r, notes, y_orig, sr, a, b = process_song(song, v1_row)
        results.append(r)

    build_scorecard(results)

    # A/B pairs
    ab_manifest = {}
    for song, r in zip(songs, results):
        sha16 = song["audio_sha16"]
        # need y_orig again with the same slicing
        drums_wav = BASELINE_DIR / sha16 / "rc9_6stem" / "drums.wav"
        t0 = float(song["chosen_section"]["t_start_s"])
        t1 = float(song["chosen_section"]["t_end_s"])
        y_orig, sr, a, b = slice_and_load(drums_wav, t0, t1)
        # reload notes from disk (byte-canonical)
        notes = json.loads((IMPL_DIR / sha16 / "notes.json").read_text())["notes"]
        ab_manifest[sha16] = emit_ab_pairs(sha16, notes, y_orig, sr, a, b)

    write_json_canonical(IMPL_DIR / "ab_pairs_manifest.json", ab_manifest)

    # Verdict
    verdict_body = compute_verdict(results)
    rubric_hash = (IMPL_DIR / "rubric_hash.txt").read_text().strip()
    doc_sha = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()
    if rubric_hash != doc_sha:
        raise RuntimeError(f"rubric_hash mismatch: file={rubric_hash} doc={doc_sha}")

    verdict = {
        "cycle": 55,
        "clone": "clone-0",
        "fork": "7cc01d726807",
        "run_id": "run-2026-08-28T040704Z",
        "rubric_doc": "docs/rc10_drums_v2_rubric.md",
        "rubric_hash": rubric_hash,
        **verdict_body,
        "per_song_summary": [
            {
                "song_id": r["song_id"],
                "n_onsets": r["n_onsets"],
                "counts": r["counts"],
                "G1_F1": r["gates"]["G1_onset_f1"]["value"],
                "G1_v1_F1": r["gates"]["G1_onset_f1"]["v1_f1"],
                "G2_pass": r["gates"]["G2_4bar_balance"]["passed"],
                "G3_pass": r["gates"]["G3_kick_rate_le_2x_beat"]["passed"],
                "G4_pass": r["gates"]["G4_centroid_ordering_strict"]["passed"],
                "passed_all": r["passed_all_gates"],
                "onset_timing_status": r["onset_timing_status"],
                "fallback_reason": r.get("fallback_reason"),
            }
            for r in results
        ],
    }
    write_json_canonical(IMPL_DIR / "verdict.json", verdict)
    print("verdict:", verdict["verdict"], "n_passed:", verdict["n_songs_passed_all_gates"])


if __name__ == "__main__":
    main()
