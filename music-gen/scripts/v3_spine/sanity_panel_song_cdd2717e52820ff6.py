#!/usr/bin/env python3
"""c20 Rome: 8-key panel on operator-section A/B (sibling of c5). Panel is NEVER a LANDS gate."""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np
import scipy.io.wavfile as sw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.texture.panel import texture_distance  # noqa: E402

SHA16 = "cdd2717e52820ff6"
DEL_ROOT = Path(f"data/v3/deliveries/{SHA16}")
DEL_OP = DEL_ROOT / "operator_section"


def read_stereo(p):
    sr, y = sw.read(str(p))
    if y.dtype == np.int16:
        y = y.astype(np.float32) / 32768.0
    return sr, y


def emit_panel(orig_wav, recon_wav, out_json, out_tsv, section_tag):
    sr, o = read_stereo(orig_wav)
    sr2, r = read_stereo(recon_wav)
    assert sr == sr2
    d = texture_distance(o, r, sr)
    NUMERIC = ("mel_l1_db", "spectral_centroid_rmse_hz", "rms_env_rmse",
               "lufs_m_rmse_lu", "embedding_cosine_distance")
    finite = {}
    for k, v in d.items():
        if k in NUMERIC:
            finite[k] = isinstance(v, (int, float)) and (v == v) and abs(v) < 1e12
        else:
            finite[k] = True
    result = {
        "cycle": 20,
        "song_sha16": SHA16,
        "sr": sr,
        "section": section_tag,
        "panel_keys_count": len(d),
        "panel": d,
        "finite_per_key": finite,
        "panel_is_never_lands_gate": True,
    }
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    tsv = ["key\tvalue\tfinite"]
    for k in sorted(d):
        tsv.append(f"{k}\t{d[k]}\t{finite[k]}")
    out_tsv.write_text("\n".join(tsv) + "\n")
    return result


def main():
    res_root = emit_panel(
        DEL_ROOT / "original_ab.wav", DEL_ROOT / "reconstruction_ab.wav",
        DEL_ROOT / "panel.json", DEL_ROOT / "panel.tsv", "operator_section",
    )
    res_op = emit_panel(
        DEL_OP / "original_ab_operator_section.wav",
        DEL_OP / "reconstruction_ab_operator_section.wav",
        DEL_OP / "panel.json", DEL_OP / "panel.tsv", "operator_section",
    )
    print("panel:", {k: round(v, 4) if isinstance(v, (int, float)) else v for k, v in res_root["panel"].items()})


if __name__ == "__main__":
    main()
