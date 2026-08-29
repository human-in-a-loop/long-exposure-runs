#!/usr/bin/env -S /usr/bin/python3
"""One-shot backwards-compat check for palette-driven-batch-v4.

Verifies that render_stem(parameter_dict=None) reproduces the 3 c33
anchor SHAs (bass, other, combined). Writes
data/palette_render_v4/backwards_compat_check.json. Archives to
tools/stale/ after use.
"""
from __future__ import annotations
import hashlib, json, shutil, sys, tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO))

from scripts.palette_render.render_stem import render_stem, SAMPLE_RATE, SAMPLE_COUNT
import numpy as np
import soundfile as sf
import scipy.io.wavfile as scipy_wav

ANCHORS = {
    "bass":     "6b9a5219e761854bdcf42a87f370a283e3fb096faf64648eb198c98520540280",
    "other":    "a2e5d0585404b448a2120c3c4bd6432ec1962ed82c3a7a74dd7518ed3d10f621",
    "combined": "a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794",
}
DISPATCH = {"bass": "sfizz", "other": "sfizz", "drums": "fluidsynth_gm"}


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="bc_check_"))
    per_stem_sha = {}
    stem_wavs = []
    for stem in ("drums", "bass", "other"):
        d = tmp / stem
        r = render_stem(stem, DISPATCH[stem], d, parameter_dict=None)
        per_stem_sha[stem] = r["render_run1_sha"]
        stem_wavs.append(Path(r["run1_wav_path"]))
    accum = np.zeros((SAMPLE_COUNT, 2), dtype=np.float32)
    for sw in stem_wavs:
        y, sr = sf.read(str(sw), always_2d=True)
        if y.shape[1] == 1:
            y = np.concatenate([y, y], axis=1)
        n = min(y.shape[0], SAMPLE_COUNT)
        accum[:n, :] += y[:n, :].astype(np.float32)
    combined = tmp / "bare_combined.wav"
    scipy_wav.write(str(combined), SAMPLE_RATE, accum)
    combined_sha = hashlib.sha256(combined.read_bytes()).hexdigest()

    result = {
        "anchors": ANCHORS,
        "observed": {
            "bass": per_stem_sha["bass"],
            "other": per_stem_sha["other"],
            "combined": combined_sha,
        },
        "matches": {
            "bass": per_stem_sha["bass"] == ANCHORS["bass"],
            "other": per_stem_sha["other"] == ANCHORS["other"],
            "combined": combined_sha == ANCHORS["combined"],
        },
    }
    result["all_match"] = all(result["matches"].values())
    out = _REPO / "data" / "palette_render_v4" / "backwards_compat_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    shutil.rmtree(tmp)
    return 0 if result["all_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
