#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T05:20:00Z
# cycle: 4
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel
# ---
"""Run all three validation pairs and emit result JSONs + panel_summary.tsv.

Pair 1 (matched): DAW-spike Ardour ↔ DawDreamer matched sine.
Pair 2 (known-different): fluidsynth ↔ sfizz on the same MIDI.
Pair 3 (self-distance): Ardour render vs itself.
"""
from __future__ import annotations

import json
import pathlib
import warnings

import numpy as np
import soundfile as sf

from scripts.texture.panel import texture_distance
from scripts.texture.spectral_panel import mel_l1_db_multiscale

warnings.filterwarnings("ignore")

ROOT = pathlib.Path(__file__).resolve().parents[2]
DAW = ROOT / "data" / "daw_spike"
TEX = ROOT / "data" / "texture"

REFERENCE = {  # from data/daw_spike/agreement.json
    "mel_l1_db": 3.130554437637329,
    "rms_env_rmse": 0.040991,
    "spectral_centroid_rmse_hz": 159.017,
}


def _load(path: pathlib.Path):
    a, sr = sf.read(str(path), always_2d=True)
    return a.astype(np.float32), int(sr)


def _write_pair(name: str, result: dict, extra: dict | None = None) -> pathlib.Path:
    out = TEX / f"results_{name}.json"
    payload = {"pair": name, "metrics": result}
    if extra:
        payload["extra"] = extra
    out.write_text(json.dumps(payload, indent=2, default=str))
    print(f"[OK] wrote {out}")
    return out


def main() -> int:
    TEX.mkdir(parents=True, exist_ok=True)

    # ------------------------------- Pair 1 -----------------------------------
    a1, sr1 = _load(DAW / "ardour_render.wav")
    b1, srb1 = _load(DAW / "dawdreamer_render_matched.wav")
    r1 = texture_distance(a1, b1, sr1, sr_b=srb1)
    # per-scale mel L1 (diagnostic)
    ms = mel_l1_db_multiscale(a1, b1, sr1)["per_scale"]
    r1_extra = {
        "reference": REFERENCE,
        "reproduction_ratios": {
            "mel_l1_db": r1["mel_l1_db"] / REFERENCE["mel_l1_db"],
            "rms_env_rmse": r1["rms_env_rmse"] / REFERENCE["rms_env_rmse"],
            "spectral_centroid_rmse_hz": r1["spectral_centroid_rmse_hz"] / REFERENCE["spectral_centroid_rmse_hz"],
        },
        "mel_l1_db_per_scale": {str(k): v for k, v in ms.items()},
    }
    _write_pair("matched", r1, r1_extra)

    # ------------------------------- Pair 2 -----------------------------------
    a2, sr2 = _load(TEX / "fluid_render.wav")
    b2, srb2 = _load(TEX / "sfizz_render.wav")
    r2 = texture_distance(a2, b2, sr2, sr_b=srb2)
    r2_extra = {
        "test_midi_sha256": (TEX / "test_midi_sha.txt").read_text().split()[0],
        "known_diff_vs_matched_ratios": {
            "mel_l1_db": r2["mel_l1_db"] / r1["mel_l1_db"],
            "spectral_centroid_rmse_hz": r2["spectral_centroid_rmse_hz"] / r1["spectral_centroid_rmse_hz"],
        },
    }
    _write_pair("known_diff", r2, r2_extra)

    # ------------------------------- Pair 3 -----------------------------------
    r3 = texture_distance(a1, a1, sr1, sr_b=sr1)
    _write_pair("self_distance", r3)

    # ------------------------------- Summary TSV ------------------------------
    tsv = TEX / "panel_summary.tsv"
    metrics = ["mel_l1_db", "spectral_centroid_rmse_hz", "rms_env_rmse",
               "lufs_m_rmse_lu", "embedding_cosine_distance", "embedding_rung"]
    header = ["pair"] + metrics
    rows = [
        ["matched"] + [r1[m] for m in metrics],
        ["known_diff"] + [r2[m] for m in metrics],
        ["self_distance"] + [r3[m] for m in metrics],
    ]
    with tsv.open("w") as f:
        f.write("\t".join(header) + "\n")
        for row in rows:
            f.write("\t".join(str(x) for x in row) + "\n")
    print(f"[OK] wrote {tsv}")

    # Sanity console summary
    for tag, r in (("matched", r1), ("known_diff", r2), ("self_distance", r3)):
        print(f"[{tag}] mel_l1_db={r['mel_l1_db']:.4f} "
              f"sc_rmse={r['spectral_centroid_rmse_hz']:.2f} "
              f"rms_rmse={r['rms_env_rmse']:.5f} "
              f"lufs_rmse={r['lufs_m_rmse_lu']:.3f} "
              f"emb={r['embedding_cosine_distance']} rung={r['embedding_rung']}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
