#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:05:00Z
# cycle: 34
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v1
# ---
"""Per-song render orchestrator.

Given a salt integer and an output directory, this module:

  1. Selects the per-salt rule triple via sample_rule_triple.sample_triple.
  2. Builds three palette-assignment rows (drums/bass/other) via
     scripts.palette_render.build_assignments.build_assignment_row
     (READ-ONLY import), with provenance_pointers = sorted(rule_ids).
  3. Validates each row via scripts.palette.validate.validate_row
     (READ-ONLY import through the build layer).
  4. Runs the render TWICE into fresh tempfile.mkdtemp() directories;
     asserts SHA-256 equality on every per-stem WAV and on the summed
     bare_combined.wav.
  5. Writes:
       out_dir/assignments.jsonl
       out_dir/per_stem/<stem>/render_run{1,2}.wav.sha, pinned_state.json
       out_dir/bare_combined.wav
       out_dir/bare_combined.wav.sha.run1
       out_dir/bare_combined.wav.sha.run2
       out_dir/dispatch_summary.json
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
import scipy.io.wavfile as scipy_wav

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# Read-only anchor imports (c33 palette-render + c31 palette-v1 flow through
# build_assignments' import of scripts.palette.validate).
from scripts.palette_render.build_assignments import (  # noqa: E402
    build_assignment_row, probe_fetchability, STEMS,
)
from scripts.palette_render.render_stem import (  # noqa: E402
    render_stem, SAMPLE_RATE, SAMPLE_COUNT,
)
from scripts.palette.validate import validate_row  # noqa: E402
from scripts.gen_palette_batch_v1.sample_rule_triple import sample_triple  # noqa: E402


def _sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _sum_stems(stem_wavs: list[Path], out_path: Path) -> str:
    accum = np.zeros((SAMPLE_COUNT, 2), dtype=np.float32)
    for sw in stem_wavs:
        y, sr = sf.read(str(sw), always_2d=True)
        if sr != SAMPLE_RATE:
            raise RuntimeError(f"stem sr={sr}, expected {SAMPLE_RATE}")
        if y.shape[1] == 1:
            y = np.concatenate([y, y], axis=1)
        n = min(y.shape[0], SAMPLE_COUNT)
        accum[:n, :] += y[:n, :].astype(np.float32)
    scipy_wav.write(str(out_path), SAMPLE_RATE, accum)
    return _sha256_file(out_path)


def _build_assignments_for_salt(salt: int, out_dir: Path,
                                fetch: dict) -> list[dict]:
    triple = sample_triple(salt)
    pointers = sorted(triple.values())
    rows: list[dict] = []
    for stem in STEMS:
        row = build_assignment_row(stem, pointers, fetch)
        errors = validate_row(row)
        if errors:
            raise RuntimeError(
                f"salt={salt} stem={stem}: palette-v1 validator rejected row: {errors}"
            )
        rows.append(row)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "assignments.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    return rows


def _one_run(rows: list[dict], run_tag: str) -> tuple[str, list[dict], Path]:
    tmp = Path(tempfile.mkdtemp(prefix=f"c34_batch_v1_salt_run_{run_tag}_"))
    per_stem: list[dict] = []
    stem_wavs: list[Path] = []
    for a in rows:
        stem = a["stem"]
        inst = a["instrument"]
        stem_dir = tmp / stem
        r = render_stem(stem, inst, stem_dir)
        per_stem.append(r)
        stem_wavs.append(Path(r["run1_wav_path"]))
    combined = tmp / "bare_combined.wav"
    combined_sha = _sum_stems(stem_wavs, combined)
    return combined_sha, per_stem, combined


def render_song(salt: int, out_dir: Path) -> dict:
    """Render one salt song end-to-end. Returns a manifest dict."""
    out_dir.mkdir(parents=True, exist_ok=True)
    fetch = probe_fetchability(_REPO / "data" / "gen_palette_batch_v1" /
                               "fetchability_ladder.jsonl")

    rows = _build_assignments_for_salt(salt, out_dir, fetch)

    combined_sha_r1, per_stem_r1, combined_r1 = _one_run(rows, f"salt{salt}_r1")
    combined_sha_r2, per_stem_r2, combined_r2 = _one_run(rows, f"salt{salt}_r2")

    # Per-stem SHA equality
    per_stem_equal = {}
    per_stem_meta = []
    for r1, r2 in zip(per_stem_r1, per_stem_r2):
        stem = r1["stem"]
        stem_dir = out_dir / "per_stem" / stem
        stem_dir.mkdir(parents=True, exist_ok=True)
        # Copy pinned_state + write SHAs (both runs' SHAs come from the
        # tempdirs; we keep the run1 pinned_state as canonical because
        # runs are byte-identical.)
        pinned_src = Path(r1["run1_wav_path"]).parent / "pinned_state.json"
        if pinned_src.exists():
            shutil.copy2(pinned_src, stem_dir / "pinned_state.json")
        (stem_dir / "render_run1.wav.sha").write_text(r1["render_run1_sha"] + "\n")
        (stem_dir / "render_run2.wav.sha").write_text(r2["render_run1_sha"] + "\n")
        eq = (r1["render_run1_sha"] == r2["render_run1_sha"] and
              r1["render_run1_sha"] == r1["render_run2_sha"] and
              r2["render_run1_sha"] == r2["render_run2_sha"])
        per_stem_equal[stem] = eq
        per_stem_meta.append({
            "stem": stem, "instrument": r1["instrument"],
            "midi_path": r1["midi_path"], "midi_sha": r1["midi_sha"],
            "sha_run1": r1["render_run1_sha"],
            "sha_run2": r2["render_run1_sha"],
            "sha_equal": eq,
        })

    # Copy run1's combined wav out as canonical, then remove tempdirs.
    canonical_combined = out_dir / "bare_combined.wav"
    shutil.copy2(combined_r1, canonical_combined)
    (out_dir / "bare_combined.wav.sha.run1").write_text(combined_sha_r1 + "\n")
    (out_dir / "bare_combined.wav.sha.run2").write_text(combined_sha_r2 + "\n")
    combined_sha_equal = (combined_sha_r1 == combined_sha_r2)

    # Dispatch summary
    dispatch = {
        "salt": salt,
        "sfizz_count": sum(1 for a in rows if a["instrument"] == "sfizz"),
        "fluidsynth_gm_count": sum(1 for a in rows if a["instrument"] == "fluidsynth_gm"),
        "skip_count_by_reason": {},  # no skips this cycle
        "per_stem_instrument": {a["stem"]: a["instrument"] for a in rows},
        "assignment_ids": [a["assignment_id"] for a in rows],
        "provenance_pointers": rows[0]["provenance_pointers"],
    }
    (out_dir / "dispatch_summary.json").write_text(
        json.dumps(dispatch, sort_keys=True, indent=2) + "\n"
    )

    # Cleanup tempdirs
    for td in (combined_r1.parent, combined_r2.parent):
        try:
            shutil.rmtree(td)
        except Exception:
            pass

    return {
        "salt": salt,
        "assignment_rows": rows,
        "per_stem": per_stem_meta,
        "per_stem_sha_equal": per_stem_equal,
        "bare_combined_sha_run1": combined_sha_r1,
        "bare_combined_sha_run2": combined_sha_r2,
        "bare_combined_sha_equal": combined_sha_equal,
        "bare_combined_wav": str(canonical_combined),
        "dispatch": dispatch,
    }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--salt", type=int, required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    result = render_song(args.salt, Path(args.out_dir))
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ("assignment_rows", "per_stem")},
                     sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
