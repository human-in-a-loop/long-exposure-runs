#!/usr/bin/env python3
"""c20 Rome: emit deliverables under data/v3/deliveries/51e433ade2a845e1/."""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
import numpy as np
import scipy.io.wavfile as sw

SHA16 = "51e433ade2a845e1"
SEC = Path(f"data/v3_spine/{SHA16}/operator_section")
FULL_SPINE = Path(f"data/v3_spine/{SHA16}/full_song")
DEL_ROOT = Path(f"data/v3/deliveries/{SHA16}")
DEL_OP = DEL_ROOT / "operator_section"
ORIG_MP3 = Path("corpus/ratings/5/012__gPp2KBV9zXk__Dojo_Cuts_-_Rome.mp3")
RECON = SEC / "render" / "full_reconstruction_operator_section.wav"
T_START = 62.74031746031746
T_END = 92.74031746031747
T_DUR = 30.0
SR = 44100


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def decode_mp3(mp3, out, t_start, t_dur):
    env = os.environ.copy()
    env.update({"PYTHONHASHSEED":"0","SOURCE_DATE_EPOCH":"1756463424","TZ":"UTC","LC_ALL":"C.UTF-8"})
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.parent / (out.name + ".tmp.wav")
    cmd = ["ffmpeg","-y","-ss",str(t_start)]
    if t_dur is not None:
        cmd += ["-t",str(t_dur)]
    cmd += ["-i",str(mp3),"-ac","2","-ar",str(SR),"-acodec","pcm_s16le",str(tmp)]
    r = subprocess.run(cmd, env=env, capture_output=True)
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
    DEL_OP.mkdir(parents=True, exist_ok=True)
    DEL_ROOT.mkdir(parents=True, exist_ok=True)

    # Chosen section A/B (30s)
    orig_ab = DEL_ROOT / "original_ab.wav"
    decode_mp3(ORIG_MP3, orig_ab, T_START, T_DUR)
    recon_ab = DEL_ROOT / "reconstruction_ab.wav"
    slice_wav(RECON, recon_ab, 0.0, T_DUR)

    # Also under operator_section/ for parity with c5
    op_orig = DEL_OP / "original_ab_operator_section.wav"
    shutil.copy2(orig_ab, op_orig)
    op_recon = DEL_OP / "reconstruction_ab_operator_section.wav"
    shutil.copy2(recon_ab, op_recon)

    # Full reconstruction WAV = the operator-section reconstruction (v3 chain
    # renders the operator's D1-chosen 30s window; the "full" delivery filename
    # names the top-of-tree canonical reconstruction, per c5 pattern).
    full_dst = DEL_ROOT / "full_reconstruction.wav"
    shutil.copy2(RECON, full_dst)
    op_full = DEL_OP / "full_reconstruction_operator_section.wav"
    shutil.copy2(RECON, op_full)

    # stems: copy under delivery
    stems_op = DEL_ROOT / "stems_6s"
    stems_op.mkdir(parents=True, exist_ok=True)
    for w in sorted((SEC / "rc9_6stem").glob("*.wav")):
        shutil.copy2(w, stems_op / w.name)
    stems_full = DEL_ROOT / "stems_6s_full_song"
    if (FULL_SPINE / "rc9_6stem").exists():
        stems_full.mkdir(parents=True, exist_ok=True)
        for w in sorted((FULL_SPINE / "rc9_6stem").glob("*.wav")):
            shutil.copy2(w, stems_full / w.name)

    # per_track renders
    pt_dst = DEL_ROOT / "per_track"
    pt_dst.mkdir(parents=True, exist_ok=True)
    for w in sorted((SEC / "render" / "per_track").glob("*.wav")):
        shutil.copy2(w, pt_dst / w.name)

    # muscriptor json+mid pairs
    ms_dst = DEL_ROOT / "muscriptor_operator_section"
    ms_dst.mkdir(parents=True, exist_ok=True)
    for f in sorted((SEC / "muscriptor").iterdir()):
        shutil.copy2(f, ms_dst / f.name)

    # merged.mid + tempo_choice + mix_match + rc7 loudness
    for src in [SEC / "merged.mid",
                SEC / "tempo_choice.json",
                SEC / "render" / "mix_match_operator_section.json",
                SEC / "rc7_per_stem_loudness_operator_section.json"]:
        if src.exists():
            shutil.copy2(src, DEL_ROOT / src.name)

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
        "cycle": 20,
        "song_sha16": SHA16,
        "song_title": "Dojo Cuts - Rome",
        "song_audio_path": str(ORIG_MP3),
        "ab_window_operator_section": {
            "t_start_s": T_START,
            "t_end_s": T_END,
            "duration_s": T_DUR,
            "note": "Rome operator D1-chosen peak+exposed section.",
        },
        "artifacts": {
            "original_ab_wav": {"path": str(orig_ab), "sha256": sha(orig_ab), "duration_s": dur(orig_ab), "peak": peak(orig_ab)},
            "reconstruction_ab_wav": {"path": str(recon_ab), "sha256": sha(recon_ab), "duration_s": dur(recon_ab), "peak": peak(recon_ab)},
            "full_reconstruction_wav": {"path": str(full_dst), "sha256": sha(full_dst), "duration_s": dur(full_dst), "peak": peak(full_dst)},
            "original_ab_operator_section_wav": {"path": str(op_orig), "sha256": sha(op_orig), "duration_s": dur(op_orig), "peak": peak(op_orig)},
            "reconstruction_ab_operator_section_wav": {"path": str(op_recon), "sha256": sha(op_recon), "duration_s": dur(op_recon), "peak": peak(op_recon)},
            "full_reconstruction_operator_section_wav": {"path": str(op_full), "sha256": sha(op_full), "duration_s": dur(op_full), "peak": peak(op_full)},
        },
        "per_stem_canonical_midi_sha": per_stem_canon,
        "tempo_choice": {"bpm": tempo["detected_bpm"], "meter": tempo["meter"], "source": tempo["source"]},
        "rubric_hash_v2": rubric_v2,
        "rubric_hash_v2_source_doc": "docs/v3_spine_rubric_v2.md",
        "muscriptor_debug_midi_shas": {
            "note": "non_factor_debug per operator OPTION A directive point 3",
            "shas": debug_midi,
        },
        "reference_delivery": {
            "path": "data/v3/deliveries/31a164f845f8e27e/",
            "note": "Chicken Grease c5 canonical delivery format used as template.",
        },
    }
    (DEL_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (DEL_OP / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    for p in [orig_ab, recon_ab, full_dst, op_orig, op_recon, op_full]:
        assert peak(p) > 1e-4, f"{p} silent"
    assert abs(dur(orig_ab) - T_DUR) < 0.005
    assert abs(dur(recon_ab) - T_DUR) < 0.005
    print(f"deliver ok: orig peak={peak(orig_ab):.4f} recon peak={peak(recon_ab):.4f}")


if __name__ == "__main__":
    main()
