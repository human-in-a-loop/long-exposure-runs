#!/usr/bin/python3
# ---
# cycle: 21
# milestone: M-V4-GEN-1/interpolation-hybrid
# purpose: ONE interpolation-hybrid demo per campaign prompt.
#          generator(rules_A × rules_B, seed) — Model A (statistical
#          scaffolding: key/tempo/scale) from donor A; Model B (CA
#          bar-transition tables) from donor B. Deterministic,
#          seeded, ear-scored.
# ---
"""M-V4-GEN-1 interpolation-hybrid demo.

Blend rules_A × rules_B via:
  * key/tempo from donor A's Model A
  * per-instrument CA tables from donor B's Model B
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

sys.path.insert(0, os.getcwd())
from scripts.v4_gen.gen import (
    _assert_env, _canonical_json, _sha256_file, HashStream,
    _load_rules, _rules_hash, _key_to_pitch_scale, _generate_bars,
    _write_merged_midi, _fluidsynth_render, _score_wav_ear,
    CANONICAL_ENV_PIN_SHA, SF2_PATH,
)


def generate_hybrid(seed: str, donor_a: str, donor_b: str, out_dir: Path,
                    n_bars: int = 16, sr: int = 44100, gain: float = 0.5,
                    tpb: int = 480):
    _assert_env()
    out_dir.mkdir(parents=True, exist_ok=True)
    hs = HashStream(seed)
    stat, seq = _load_rules()

    # Model A from donor A
    if donor_a not in stat["per_song"]:
        raise RuntimeError(f"unknown donor_a {donor_a}")
    a = stat["per_song"][donor_a]
    ke = a["key_estimate"]
    root, mode = int(ke["root_pc"]), str(ke["mode"])
    bpm = int(round(a["midi_bpm"]))
    pitch_scale = _key_to_pitch_scale(root, mode)

    # Model B from donor B — reuse _generate_bars but pass donor_b as
    # the seq lookup key (it reads seq_model[donor_b].per_instrument).
    if donor_b not in seq["per_song"]:
        raise RuntimeError(f"unknown donor_b {donor_b}")

    bar_grids = {}
    for stem in ("drums", "bass", "guitar", "piano", "other"):
        bar_grids[stem] = _generate_bars(seq, donor_b, stem, n_bars, hs)

    midi_path = out_dir / "merged.mid"
    _write_merged_midi(midi_path, bar_grids, tpb, bpm, pitch_scale, hs)
    midi_sha = _sha256_file(midi_path)

    wav_path = out_dir / "song.wav"
    _fluidsynth_render(midi_path, wav_path, sr=sr, gain=gain)
    wav_sha = _sha256_file(wav_path)

    scoring = _score_wav_ear(wav_path)

    manifest = {
        "schema_v": 1,
        "milestone_id": "M-V4-GEN-1/interpolation-hybrid",
        "seed": seed,
        "donor_a": donor_a,
        "donor_b": donor_b,
        "hybrid_composition": (
            "Model A (key/tempo/scale) from donor A; Model B (CA "
            "bar-transition tables per instrument) from donor B"
        ),
        "midi_bpm": bpm,
        "key_estimate_from_donor_a": {"root_pc": root, "mode": mode},
        "n_bars": n_bars,
        "tpb": tpb,
        "generator_hash": _sha256_file(Path("scripts/v4_gen/gen.py")),
        "hybrid_hash": _sha256_file(Path("scripts/v4_gen/hybrid.py")),
        "rules_hash": _rules_hash(),
        "sf2_path": SF2_PATH,
        "sf2_sha256": _sha256_file(Path(SF2_PATH)),
        "midi_sha256": midi_sha,
        "song_wav_sha256": wav_sha,
        "ear": scoring,
        "structural_gates_warn_not_halt": True,
        "instrumental_vocals_empty": True,
        "env_pin_sha256": CANONICAL_ENV_PIN_SHA,
        "ts": "2026-09-04T07:55:00Z",
    }
    (out_dir / "manifest.json").write_text(_canonical_json(manifest), encoding="ascii")
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--donor-a", required=True)
    ap.add_argument("--donor-b", required=True)
    ap.add_argument("--n-bars", type=int, default=16)
    args = ap.parse_args()
    m = generate_hybrid(args.seed, args.donor_a, args.donor_b,
                        args.out_dir.resolve(), n_bars=args.n_bars)
    sys.stdout.write(_canonical_json({
        "score_1_7": m["ear"]["score_1_7"],
        "midi_sha256": m["midi_sha256"],
        "song_wav_sha256": m["song_wav_sha256"],
    }) + "\n")


if __name__ == "__main__":
    _assert_env()
    main()
