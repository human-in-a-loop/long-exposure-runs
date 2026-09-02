#!/usr/bin/env python3
"""c5 Track B: emit operator-section deliverables under data/v3/deliveries/<sha16>/operator_section/."""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
import numpy as np
import scipy.io.wavfile as sw

SEC = Path("data/v3_spine/31a164f845f8e27e/operator_section")
DEL = Path("data/v3/deliveries/31a164f845f8e27e/operator_section")
ORIG_MP3 = Path("corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3")
RECON = SEC / "render" / "full_reconstruction_operator_section.wav"
T_START = 233.63918367346938
T_DUR = 30.0
SR = 44100


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def decode_mp3(mp3: Path, out: Path, t_start: float, t_dur: float):
    env = os.environ.copy()
    env.update({"PYTHONHASHSEED":"0","SOURCE_DATE_EPOCH":"1756463424","TZ":"UTC","LC_ALL":"C.UTF-8"})
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.parent / (out.name + ".tmp.wav")
    r = subprocess.run(
        ["ffmpeg","-y","-ss",str(t_start),"-t",str(t_dur),
         "-i",str(mp3),"-ac","2","-ar",str(SR),"-acodec","pcm_s16le",str(tmp)],
        env=env, capture_output=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg rc={r.returncode}: {r.stderr.decode()[-400:]}")
    tmp.replace(out)


def slice_wav(src, dst, t_start, t_dur):
    sr, y = sw.read(str(src))
    a = int(round(t_start * sr))
    b = int(round((t_start + t_dur) * sr))
    seg = y[a:b]
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".wav.tmp")
    sw.write(str(tmp), sr, seg)
    tmp.replace(dst)


def peak(p):
    _, y = sw.read(str(p))
    if y.dtype == np.int16:
        return float(np.max(np.abs(y.astype(np.float32) / 32768.0)))
    return float(np.max(np.abs(y.astype(np.float32))))


def dur(p):
    sr, y = sw.read(str(p))
    return y.shape[0] / sr


def main():
    DEL.mkdir(parents=True, exist_ok=True)
    orig_ab = DEL / "original_ab_operator_section.wav"
    decode_mp3(ORIG_MP3, orig_ab, T_START, T_DUR)
    recon_ab = DEL / "reconstruction_ab_operator_section.wav"
    slice_wav(RECON, recon_ab, 0.0, T_DUR)
    full_dst = DEL / "full_reconstruction_operator_section.wav"
    shutil.copy2(RECON, full_dst)

    rubric_v2 = Path("data/v3_spine/rubric_hash_v2.txt").read_text().strip()
    canon = json.loads((SEC / "canonical_midi_determinism.json").read_text())
    per_stem_canon = {s: r["final_out_sha256"] for s, r in canon["results"].items()
                      if r.get("status") != "missing_input"}
    debug_midi = {}
    ms_dir = SEC / "muscriptor"
    for f in sorted(ms_dir.glob("*.mid")):
        debug_midi[f.stem] = sha(f)
    tempo = json.loads((SEC / "tempo_choice.json").read_text())

    manifest = {
        "schema_version": 1,
        "cycle": 5,
        "song_sha16": "31a164f845f8e27e",
        "song_title": "Chicken Grease",
        "song_audio_path": str(ORIG_MP3),
        "ab_window_operator_section": {
            "t_start_s": T_START,
            "t_end_s": T_START + T_DUR,
            "duration_s": T_DUR,
            "note": (
                "Operator's D1 auto-picker chose this peak+exposed section for "
                "Chicken Grease. This cycle runs htdemucs_6s + MuScriptor + canonical "
                "serializer end-to-end on the operator's chosen window."
            ),
        },
        "artifacts": {
            "original_ab_operator_section_wav": {
                "path": str(orig_ab), "sha256": sha(orig_ab),
                "duration_s": dur(orig_ab), "peak": peak(orig_ab),
            },
            "reconstruction_ab_operator_section_wav": {
                "path": str(recon_ab), "sha256": sha(recon_ab),
                "duration_s": dur(recon_ab), "peak": peak(recon_ab),
            },
            "full_reconstruction_operator_section_wav": {
                "path": str(full_dst), "sha256": sha(full_dst),
                "duration_s": dur(full_dst), "peak": peak(full_dst),
            },
        },
        "per_stem_canonical_midi_sha": per_stem_canon,
        "tempo_choice": {
            "bpm": tempo["detected_bpm"], "meter": tempo["meter"],
            "source": tempo["source"],
        },
        "rubric_hash_v2": rubric_v2,
        "rubric_hash_v2_source_doc": "docs/v3_spine_rubric_v2.md",
        "muscriptor_debug_midi_shas": {
            "note": "non_factor_debug per operator OPTION A directive point 3",
            "shas": debug_midi,
        },
        "c4_delivery_reference": {
            "path": "data/v3/deliveries/31a164f845f8e27e/",
            "note": "c4 A/B (t=0..30s) preserved READ-ONLY as historical anchor",
        },
    }
    (DEL / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    for p in [orig_ab, recon_ab, full_dst]:
        assert peak(p) > 1e-4, f"{p} silent"
    assert abs(dur(orig_ab) - T_DUR) < 0.005
    assert abs(dur(recon_ab) - T_DUR) < 0.005
    print(f"deliver ok: orig_ab peak={peak(orig_ab):.4f} recon_ab peak={peak(recon_ab):.4f}")


if __name__ == "__main__":
    main()
