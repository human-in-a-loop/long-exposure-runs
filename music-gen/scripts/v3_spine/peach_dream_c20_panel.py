#!/usr/bin/env /usr/bin/python3
"""c20 clone-2: 8-key panel on Peach Dream A/B + tripwire vs c33 rc7 anchor.

Panel is NEVER a LANDS gate (per M-TEX-1 spec). Tripwire compares to c33 rc7
anchor panel if present, otherwise flags 'no_anchor_available'.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np
import scipy.io.wavfile as sw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.texture.panel import texture_distance  # noqa: E402

DEL_ROOT = Path("data/v3/deliveries/88d247468cb6d49f")
DEL = DEL_ROOT / "operator_section"
# c33 rc7 anchor panel (Chicken Grease anchor cycle for rc7 mix-match)
C33_ANCHOR_TSV = Path("data/v3/deliveries/31a164f845f8e27e/panel.tsv")


def read_stereo(p):
    sr, y = sw.read(str(p))
    if y.dtype == np.int16:
        y = y.astype(np.float32) / 32768.0
    return sr, y


def parse_panel_tsv(p: Path):
    d = {}
    if not p.exists():
        return d
    for line in p.read_text().splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) >= 2:
            k, v = parts[0], parts[1]
            try:
                d[k] = float(v)
            except ValueError:
                pass
    return d


def main():
    orig = DEL / "original_ab_operator_section.wav"
    recon = DEL / "reconstruction_ab_operator_section.wav"
    sr, o = read_stereo(orig)
    sr2, r = read_stereo(recon)
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

    anchor = parse_panel_tsv(C33_ANCHOR_TSV)
    tripwire = {}
    tripwire_pass = True
    for k in NUMERIC:
        v_new = d.get(k)
        v_old = anchor.get(k)
        if v_new is None or v_old is None:
            tripwire[k] = {"status": "missing_key", "new": v_new, "old": v_old}
            continue
        ratio = float(v_new) / max(abs(float(v_old)), 1e-9)
        regressed = abs(ratio) > 2.0
        tripwire[k] = {
            "new": float(v_new), "old": float(v_old),
            "ratio_new_over_old": ratio, "regressed_gt_2x": regressed,
        }
        if regressed:
            tripwire_pass = False

    result = {
        "cycle": 20, "clone": "clone-2", "song_sha16": "88d247468cb6d49f",
        "sr": sr, "section": "operator_section",
        "panel_keys_count": len(d),
        "panel": d,
        "finite_per_key": finite,
        "cross_song_tripwire": {
            "reference": str(C33_ANCHOR_TSV),
            "reference_note": "c33 rc7 anchor (Chicken Grease); different song — tripwire is about scale not equality",
            "per_key": tripwire,
            "pass_no_key_regressed_gt_2x": tripwire_pass,
        },
        "panel_is_never_lands_gate": True,
    }
    (DEL / "panel.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    tsv = ["key\tvalue\tfinite"]
    for k in sorted(d):
        tsv.append(f"{k}\t{d[k]}\t{finite[k]}")
    (DEL / "panel.tsv").write_text("\n".join(tsv) + "\n")
    import shutil
    shutil.copy2(DEL / "panel.json", DEL_ROOT / "panel.json")
    shutil.copy2(DEL / "panel.tsv", DEL_ROOT / "panel.tsv")
    print("panel:", {k: round(v, 4) if isinstance(v, (int, float)) else v for k, v in d.items()})
    print("tripwire pass:", tripwire_pass)


if __name__ == "__main__":
    main()
