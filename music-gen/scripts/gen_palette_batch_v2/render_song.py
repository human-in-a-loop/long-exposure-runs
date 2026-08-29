#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T06:11:00Z
# cycle: 35
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v2-sampler-diversified
# ---
"""Per-song render for batch-v2.

Signature-compatible with c34 clone-2's render_song, extended to:

  * Consume per-salt DIFFERENT rule triples from sample_rule_triple_v2.
  * Author BOTH per-stem palette-v1 assignment rows (bass/drums/other,
    consumed by c33 render_stem) AND — where the c33 dawdreamer_state
    P1 anchor is available — per-plugin palette-v2 payloads
    (surge_xt / dexed) via perturb_pinned_state. The v2 payloads are
    written to `per_song/<salt>/v2_perturbed/<plugin>.json` as a
    first-class artifact and are validated at authoring time, but do
    NOT flow into audio bytes this cycle (c33 render_stem dispatches
    on (stem, instrument) alone; palette-v2 payloads are ready for a
    c36 renderer that consumes them).

Renders each salt TWICE into fresh tempfile.mkdtemp() dirs; asserts
per-stem and combined-WAV SHA-256 equality across runs.
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

# Read-only anchor imports.
from scripts.palette_render.build_assignments import (  # noqa: E402
    build_assignment_row, probe_fetchability, STEMS,
)
from scripts.palette_render.render_stem import (  # noqa: E402
    render_stem, SAMPLE_RATE, SAMPLE_COUNT,
)
from scripts.palette.validate import validate_row as validate_row_v1  # noqa: E402
from scripts.gen_palette_batch_v2.sample_rule_triple_v2 import (  # noqa: E402
    sample_triples,
)
from scripts.gen_palette_batch_v2.perturb_pinned_state import (  # noqa: E402
    build_v2_assignment_row, PALETTE_V2_PLUGINS,
)


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


def _build_v1_assignments_for_salt(salt: int, triple: dict[str, str],
                                   out_dir: Path, fetch: dict) -> list[dict]:
    """Author per-stem palette-v1 rows with the salt's rule triple as
    provenance_pointers, then validate through palette-v1 Layer 1+2.
    """
    pointers = sorted(triple.values())
    rows: list[dict] = []
    for stem in STEMS:
        row = build_assignment_row(stem, pointers, fetch)
        errors = validate_row_v1(row)
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


def _author_v2_perturbed_payloads(salt: int, triple: dict[str, str],
                                  out_dir: Path) -> dict:
    """For each palette_v2-eligible plugin, author a perturbed v2 payload
    using the salt's harmonic rule_id (an arbitrary but stable choice —
    documented). Payloads are validated through palette_v2 at build time.

    Writes:
      per_song/<salt>/v2_perturbed/<plugin>.json
      per_song/<salt>/v2_perturbed/<plugin>.sha
    Returns {plugin_name: {"assignment_id_v2", "iteration_sha_256"}}.
    """
    from scripts.dawdreamer_state._shared import canonical_json_bytes  # noqa: E402
    v2_dir = out_dir / "v2_perturbed"
    v2_dir.mkdir(parents=True, exist_ok=True)
    seed_rule_id = triple["harmonic"]  # Salient-per-salt rule_id anchor.
    pointers = sorted(triple.values())
    summary: dict = {}
    for plugin_name in PALETTE_V2_PLUGINS:
        # `stem="mono"` per palette_v2 schema: VST3 plugins serve as
        # full-range assignments without a per-stem role.
        row = build_v2_assignment_row("mono", plugin_name, seed_rule_id,
                                      pointers)
        payload_path = v2_dir / f"{plugin_name}.json"
        payload_path.write_bytes(canonical_json_bytes(row))
        sha = _sha256_file(payload_path)
        (v2_dir / f"{plugin_name}.sha").write_text(sha + "\n")
        summary[plugin_name] = {
            "assignment_id_v2": row["assignment_id_v2"],
            "iteration_sha_256": row["pinned_state"]["iteration_sha_256"],
            "iteration_size": row["pinned_state"]["iteration_size"],
            "path": str(payload_path.relative_to(_REPO)),
            "sha": sha,
        }
    return summary


def _one_run(v1_rows: list[dict], run_tag: str) -> tuple[str, list[dict], Path]:
    tmp = Path(tempfile.mkdtemp(prefix=f"c35_batch_v2_salt_run_{run_tag}_"))
    per_stem: list[dict] = []
    stem_wavs: list[Path] = []
    for a in v1_rows:
        stem = a["stem"]
        inst = a["instrument"]
        stem_dir = tmp / stem
        r = render_stem(stem, inst, stem_dir)
        per_stem.append(r)
        stem_wavs.append(Path(r["run1_wav_path"]))
    combined = tmp / "bare_combined.wav"
    combined_sha = _sum_stems(stem_wavs, combined)
    return combined_sha, per_stem, combined


def render_song(salt: int, out_dir: Path,
                triple: dict[str, str] | None = None) -> dict:
    """Render one salt song end-to-end. Returns a manifest dict."""
    out_dir.mkdir(parents=True, exist_ok=True)
    fetch = probe_fetchability(_REPO / "data" / "gen_palette_batch_v2" /
                               "fetchability_ladder.jsonl")

    if triple is None:
        # Single-salt-only fallback: build a distinctness-of-one triple.
        triples = sample_triples([salt])
        triple = triples[salt]

    v1_rows = _build_v1_assignments_for_salt(salt, triple, out_dir, fetch)
    v2_summary = _author_v2_perturbed_payloads(salt, triple, out_dir)

    combined_sha_r1, per_stem_r1, combined_r1 = _one_run(v1_rows, f"salt{salt}_r1")
    combined_sha_r2, per_stem_r2, combined_r2 = _one_run(v1_rows, f"salt{salt}_r2")

    per_stem_equal = {}
    per_stem_meta = []
    for r1, r2 in zip(per_stem_r1, per_stem_r2):
        stem = r1["stem"]
        stem_dir = out_dir / "per_stem" / stem
        stem_dir.mkdir(parents=True, exist_ok=True)
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

    canonical_combined = out_dir / "bare_combined.wav"
    shutil.copy2(combined_r1, canonical_combined)
    (out_dir / "bare_combined.wav.sha.run1").write_text(combined_sha_r1 + "\n")
    (out_dir / "bare_combined.wav.sha.run2").write_text(combined_sha_r2 + "\n")
    combined_sha_equal = (combined_sha_r1 == combined_sha_r2)

    dispatch = {
        "salt": salt,
        "sfizz_count": sum(1 for a in v1_rows if a["instrument"] == "sfizz"),
        "fluidsynth_gm_count": sum(1 for a in v1_rows
                                   if a["instrument"] == "fluidsynth_gm"),
        "v2_payloads_authored": sorted(v2_summary.keys()),
        "skip_count_by_reason": {},
        "per_stem_instrument": {a["stem"]: a["instrument"] for a in v1_rows},
        "assignment_ids": [a["assignment_id"] for a in v1_rows],
        "provenance_pointers": v1_rows[0]["provenance_pointers"],
        "rule_triple": triple,
    }
    (out_dir / "dispatch_summary.json").write_text(
        json.dumps(dispatch, sort_keys=True, indent=2) + "\n"
    )

    for td in (combined_r1.parent, combined_r2.parent):
        try:
            shutil.rmtree(td)
        except Exception:
            pass

    return {
        "salt": salt,
        "rule_triple": triple,
        "assignment_rows_v1": v1_rows,
        "v2_perturbed_summary": v2_summary,
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
                      if k not in ("assignment_rows_v1", "per_stem",
                                   "v2_perturbed_summary")},
                     sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
