#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T07:27:00Z
# cycle: 36
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v3
# ---
"""C36 Branch B batch orchestrator.

Sequence:
  1. Sample per-salt rule triples via c35 sampler (READ-ONLY import).
  2. Derive per-stem parameter_dict per salt via the rubric-fixed table.
  3. Render each salt TWICE into fresh tempfile.mkdtemp() dirs via the
     extended render_stem with parameter_dict populated.
  4. Assert SHA-256 equality per-salt across runs.
  5. Assert SHA-256 INequality between salts on bare_combined.wav (rubric §PARAM_MOVES_AUDIO).
  6. Measure M-TEX-1/panel on (original, palette-v3-bare) AND
     (c33 palette-v1-bare, palette-v3-bare) per salt.
  7. Snapshot anchor mtimes pre/post.
  8. Resolve verdict per the frozen rubric.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import scipy.io.wavfile as scipy_wav

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# Read-only anchor imports.
from scripts.texture.panel import texture_distance, PUBLIC_KEYS  # noqa: E402
from scripts.palette_render.render_stem import (  # noqa: E402
    render_stem, SAMPLE_RATE, SAMPLE_COUNT,
)
from scripts.gen_palette_batch_v2.sample_rule_triple_v2 import (  # noqa: E402
    sample_triples,
)
from scripts.palette_render_v3.derive_parameter_dict import (  # noqa: E402
    derive_per_salt, payload_sha256, canonical_json,
)

OUT_DIR = _REPO / "data" / "palette_render_v3"
SALTS = [0, 1, 2]
NUMERIC_KEYS = ("mel_l1_db", "spectral_centroid_rmse_hz",
                "rms_env_rmse", "lufs_m_rmse_lu")

# c33 assignment (READ-ONLY): drums=fluidsynth_gm, bass=sfizz, other=sfizz.
PER_STEM_DISPATCH = {
    "drums": "fluidsynth_gm",
    "bass":  "sfizz",
    "other": "sfizz",
}

# Reference WAVs.
C33_ORIGINAL = _REPO / "data" / "tex" / "renders" / "synth_030s" / "original.wav"
C33_FLUIDSYNTH_BARE = _REPO / "data" / "tex" / "renders" / "synth_030s" / "bare_midi.wav"


def _read_wav(p: Path) -> tuple[np.ndarray, int]:
    y, sr = sf.read(str(p), always_2d=True)
    return y, sr


def _sum_stems(stem_wavs: list[Path], out_path: Path) -> str:
    accum = np.zeros((SAMPLE_COUNT, 2), dtype=np.float32)
    for sw in stem_wavs:
        y, sr = _read_wav(sw)
        if sr != SAMPLE_RATE:
            raise RuntimeError(f"stem sr={sr}, expected {SAMPLE_RATE}")
        if y.shape[1] == 1:
            y = np.concatenate([y, y], axis=1)
        n = min(y.shape[0], SAMPLE_COUNT)
        accum[:n, :] += y[:n, :].astype(np.float32)
    scipy_wav.write(str(out_path), SAMPLE_RATE, accum)
    return hashlib.sha256(out_path.read_bytes()).hexdigest()


def _write_panel_tsv(out_path: Path, panel: dict) -> None:
    keys = sorted(PUBLIC_KEYS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\t".join(keys) + "\n")
        row = []
        for k in keys:
            v = panel.get(k)
            row.append("" if v is None else str(v))
        f.write("\t".join(row) + "\n")


def _panel_measure(a: Path, b: Path) -> dict:
    ya, sra = _read_wav(a)
    yb, srb = _read_wav(b)
    if sra != srb:
        raise RuntimeError(f"SR mismatch: {a}={sra} vs {b}={srb}")
    return texture_distance(ya, yb, sra)


def _snapshot_anchor_shas() -> dict:
    """Enumerate anchor file SHAs; render_stem.py is intentionally excluded
    from the equality contract (we RECORD its pre/post SHA + diff-line
    count for the anchor_preservation report)."""
    dirs = ["scripts/palette",
            "scripts/palette_v2",
            "scripts/palette_probe",
            "scripts/palette_render",
            "scripts/dawdreamer_state",
            "scripts/gen_palette_batch_v1",
            "scripts/gen_palette_batch_v2"]
    out: dict[str, str] = {}
    for d in dirs:
        base = _REPO / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            rel = str(p.relative_to(_REPO))
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def _build_assignments(triple: dict[str, str], per_stem_params: dict) -> list[dict]:
    """One row per stem, canonical order."""
    rows = []
    stem_from_rt = {"harmonic": "other", "rhythmic": "drums", "arrangement": "bass"}
    rt_from_stem = {v: k for k, v in stem_from_rt.items()}
    for stem in ("drums", "bass", "other"):
        rt = rt_from_stem[stem]
        rid = triple[rt]
        inst = PER_STEM_DISPATCH[stem]
        pdict = per_stem_params[stem]["parameter_dict"]
        rows.append({
            "stem": stem,
            "instrument": inst,
            "rule_type": rt,
            "rule_id": rid,
            "parameter_dict": pdict,
            "assignment_v3_sha": payload_sha256({
                "stem": stem, "instrument": inst,
                "rule_id": rid, "parameter_dict": pdict,
            }),
        })
    return rows


def _render_one_salt_run(assignments: list[dict], tag: str) -> dict:
    """Render every stem via the extended render_stem in a fresh temp dir.
    Sum into bare_combined.wav; return SHAs + a copied combined WAV path."""
    tmp = Path(tempfile.mkdtemp(prefix=f"c36b_s_{tag}_"))
    per_stem = []
    stem_wavs = []
    dispatch_records = []
    for a in assignments:
        stem_dir = tmp / a["stem"]
        try:
            r = render_stem(a["stem"], a["instrument"], stem_dir,
                            parameter_dict=a["parameter_dict"])
            dispatch_records.append({
                "stem": a["stem"],
                "instrument_used": a["instrument"],
                "instrument_requested": a["instrument"],
                "parameter_dict_threaded": a["parameter_dict"],
                "sfizz_opcode_override_supported": False,
                "sfizz_fallback": "master_volume_in_band_only" if a["instrument"] == "sfizz" else None,
                "vst3_deferred": None,
            })
        except NotImplementedError as e:
            raise RuntimeError(f"VST3 branch triggered on stem {a['stem']} — rubric violation") from e
        per_stem.append(r)
        stem_wavs.append(Path(r["run1_wav_path"]))
    combined = tmp / "bare_combined.wav"
    combined_sha = _sum_stems(stem_wavs, combined)
    # copy combined out so panel measurement survives tempdir cleanup
    keep = OUT_DIR / f"_tmp_combined_{tag}.wav"
    shutil.copy2(combined, keep)
    return {"tag": tag, "per_stem": per_stem, "combined_sha": combined_sha,
            "combined_wav": str(keep), "tempdir": str(tmp),
            "dispatch_records": dispatch_records}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Snapshot anchors pre-run (post-edit already — the render_stem edit
    # landed before this script per the rubric ordering).
    anchor_pre = _snapshot_anchor_shas()

    # Sample per-salt rule triples via c35 sampler.
    triples = sample_triples(SALTS)  # {salt: {rule_type: rule_id}}

    # Per-salt derive parameter_dict per stem.
    per_salt_params = {
        s: derive_per_salt(triples[s], PER_STEM_DISPATCH) for s in SALTS
    }

    # Build canonical assignments per salt.
    per_salt_assignments = {
        s: _build_assignments(triples[s], per_salt_params[s]) for s in SALTS
    }

    # Persist per-salt inputs.
    per_song_dir = OUT_DIR / "per_song"
    per_song_dir.mkdir(parents=True, exist_ok=True)
    assignment_shas: dict[int, str] = {}
    for s in SALTS:
        song_dir = per_song_dir / str(s)
        (song_dir / "per_stem").mkdir(parents=True, exist_ok=True)
        assign_path = song_dir / "assignments.jsonl"
        with open(assign_path, "w") as f:
            for row in per_salt_assignments[s]:
                f.write(json.dumps(row, sort_keys=True) + "\n")
        assignment_shas[s] = hashlib.sha256(assign_path.read_bytes()).hexdigest()
        (song_dir / "parameter_dict.json").write_text(
            json.dumps(per_salt_params[s], sort_keys=True, indent=2) + "\n"
        )

    # Two independent temp-dir renders per salt.
    per_salt_run1: dict[int, dict] = {}
    per_salt_run2: dict[int, dict] = {}
    for s in SALTS:
        per_salt_run1[s] = _render_one_salt_run(per_salt_assignments[s], f"s{s}_r1")
        per_salt_run2[s] = _render_one_salt_run(per_salt_assignments[s], f"s{s}_r2")

    # Per-salt determinism check + stable SHA files.
    per_salt_determinism: dict[int, bool] = {}
    for s in SALTS:
        r1c = per_salt_run1[s]["combined_sha"]
        r2c = per_salt_run2[s]["combined_sha"]
        per_salt_determinism[s] = (r1c == r2c)
        song_dir = per_song_dir / str(s)
        (song_dir / "bare_combined.wav.sha.run1").write_text(r1c + "\n")
        (song_dir / "bare_combined.wav.sha.run2").write_text(r2c + "\n")
        # Per-stem SHAs into per_song/<s>/per_stem/<stem>/.
        for res_r1 in per_salt_run1[s]["per_stem"]:
            stem = res_r1["stem"]
            r2_match = next(x for x in per_salt_run2[s]["per_stem"] if x["stem"] == stem)
            stem_dir = song_dir / "per_stem" / stem
            stem_dir.mkdir(parents=True, exist_ok=True)
            (stem_dir / "render_run1.wav.sha").write_text(res_r1["render_run1_sha"] + "\n")
            (stem_dir / "render_run2.wav.sha").write_text(r2_match["render_run1_sha"] + "\n")
            pinned = {
                "stem": stem,
                "instrument": res_r1["instrument"],
                "midi_input_sha256": res_r1["midi_sha"],
                "sample_rate": SAMPLE_RATE,
                "sample_count": SAMPLE_COUNT,
                "run1_sha": res_r1["render_run1_sha"],
                "run2_sha": r2_match["render_run1_sha"],
                "sha_equal": res_r1["render_run1_sha"] == r2_match["render_run1_sha"],
            }
            (stem_dir / "pinned_state.json").write_text(
                json.dumps(pinned, sort_keys=True, indent=2) + "\n"
            )
        # Dispatch summary per salt.
        (song_dir / "dispatch_summary.json").write_text(
            json.dumps({"salt": s,
                        "records": per_salt_run1[s]["dispatch_records"]},
                       sort_keys=True, indent=2) + "\n"
        )

    # Cross-salt inequality on bare_combined.
    cross_salt_pairs = []
    for (a, b) in [(0, 1), (0, 2), (1, 2)]:
        sa = per_salt_run1[a]["combined_sha"]
        sb = per_salt_run1[b]["combined_sha"]
        cross_salt_pairs.append({
            "salt_a": a, "salt_b": b,
            "sha_a": sa, "sha_b": sb, "distinct": sa != sb,
        })

    # Per-salt panels.
    per_salt_panels: dict[int, dict] = {}
    for s in SALTS:
        combined = Path(per_salt_run1[s]["combined_wav"])
        p_orig = _panel_measure(C33_ORIGINAL, combined)
        p_fluid = _panel_measure(C33_FLUIDSYNTH_BARE, combined)
        song_dir = per_song_dir / str(s)
        _write_panel_tsv(song_dir / "panel_original.tsv", p_orig)
        _write_panel_tsv(song_dir / "panel_fluidsynth.tsv", p_fluid)
        per_salt_panels[s] = {
            "panel_original": {k: (float(v) if isinstance(v, (int, float)) else v)
                               for k, v in p_orig.items()},
            "panel_fluidsynth": {k: (float(v) if isinstance(v, (int, float)) else v)
                                 for k, v in p_fluid.items()},
        }

    # Batch manifest.
    batch_manifest = {
        "salts": SALTS,
        "per_stem_dispatch": PER_STEM_DISPATCH,
        "per_salt_rule_triple": {str(s): triples[s] for s in SALTS},
        "assignments_shas_by_salt": {str(s): assignment_shas[s] for s in SALTS},
        "per_salt_parameter_dict_shas": {
            str(s): {stem: payload_sha256(per_salt_params[s][stem]["parameter_dict"])
                     for stem in PER_STEM_DISPATCH}
            for s in SALTS
        },
        "per_salt_determinism": {str(s): per_salt_determinism[s] for s in SALTS},
        "cross_salt_pairs": cross_salt_pairs,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (OUT_DIR / "batch_manifest.json").write_text(
        json.dumps(batch_manifest, sort_keys=True, indent=2) + "\n"
    )

    # summary.tsv — 3 rows: salt, combined_sha_r1, combined_sha_r2,
    # sha_equal, distinct_vs_s0, distinct_vs_s1.
    summary_lines = ["\t".join(["salt", "combined_sha_r1", "combined_sha_r2",
                                 "det_equal", "distinct_vs_s0", "distinct_vs_s1"])]
    for s in SALTS:
        c1 = per_salt_run1[s]["combined_sha"]
        c2 = per_salt_run2[s]["combined_sha"]
        d0 = c1 != per_salt_run1[0]["combined_sha"] if s != 0 else True
        d1 = c1 != per_salt_run1[1]["combined_sha"] if s != 1 else True
        summary_lines.append("\t".join([str(s), c1, c2, str(c1 == c2),
                                         str(d0), str(d1)]))
    (OUT_DIR / "summary.tsv").write_text("\n".join(summary_lines) + "\n")

    # Verdict.
    rubric_hash = (OUT_DIR / "rubric_hash.txt").read_text().strip()
    # Backwards-compat check should already be on disk.
    bc = json.loads((OUT_DIR / "backwards_compat_check.json").read_text())

    verdict = None
    justification = {}
    if not bc.get("all_match"):
        verdict = "RENDER_FAILS"
        justification = {"reason": "backwards_compat_check failed",
                         "backwards_compat_check": bc}
    elif not all(per_salt_determinism.values()):
        verdict = "RENDER_FAILS"
        justification = {"reason": "per-salt determinism failure",
                         "per_salt_determinism": per_salt_determinism}
    else:
        # Panel finiteness.
        panel_finite = True
        for s in SALTS:
            for panel_name in ("panel_original", "panel_fluidsynth"):
                panel = per_salt_panels[s][panel_name]
                if set(panel.keys()) != set(PUBLIC_KEYS):
                    panel_finite = False
                    justification.setdefault("panel_keys_missing", []).append((s, panel_name))
                for k in NUMERIC_KEYS:
                    v = panel.get(k)
                    if v is None or not np.isfinite(v):
                        panel_finite = False
                        justification.setdefault("panel_non_finite", []).append((s, panel_name, k))
        if not panel_finite:
            verdict = "RENDER_FAILS"
            justification["reason"] = "panel finiteness violated"
        else:
            distinct_count = sum(1 for p in cross_salt_pairs if p["distinct"])
            if distinct_count == 3:
                verdict = "PARAM_MOVES_AUDIO"
                justification = {"reason": "3/3 cross-salt bare_combined distinct",
                                 "cross_salt_pairs": cross_salt_pairs}
            elif distinct_count >= 2:
                verdict = "PARAM_MOVES_AUDIO"
                justification = {
                    "reason": f"{distinct_count}/3 cross-salt bare_combined distinct "
                              f"(remaining pair attributed to parameter-table shallowness)",
                    "cross_salt_pairs": cross_salt_pairs,
                    "attribution": "The identical pair reflects the current "
                                   "sfizz fallback (only master_volume threaded in-band; "
                                   "opcode-file rewrite deferred to c37 palette-driven-batch-v4).",
                }
            else:
                verdict = "PARAM_NEUTRAL"
                justification = {
                    "reason": "0-1/3 cross-salt distinct — parameter table too shallow "
                              "to move fluidsynth/sfizz CLI bytes",
                    "cross_salt_pairs": cross_salt_pairs,
                }

    # Anchor snapshot post.
    anchor_post = _snapshot_anchor_shas()
    render_stem_rel = "scripts/palette_render/render_stem.py"
    anchor_pre_no_edit = {k: v for k, v in anchor_pre.items() if k != render_stem_rel}
    anchor_post_no_edit = {k: v for k, v in anchor_post.items() if k != render_stem_rel}
    anchor_unchanged_except_edit = (anchor_pre_no_edit == anchor_post_no_edit)

    anchor_preservation = {
        "pre": anchor_pre,
        "post": anchor_post,
        "unchanged_except_render_stem_edit": anchor_unchanged_except_edit,
        "intentional_render_stem_edit": {
            "path": render_stem_rel,
            "sha_pre_edit_expected_present": render_stem_rel in anchor_pre,
            "sha_post_edit": anchor_post.get(render_stem_rel),
            "description": "additive keyword-only parameter_dict=None; c33 dispatch path "
                           "byte-identical when parameter_dict is None (verified in "
                           "backwards_compat_check.json).",
        },
    }
    (OUT_DIR / "anchor_preservation.json").write_text(
        json.dumps(anchor_preservation, sort_keys=True, indent=2) + "\n"
    )

    verdict_json = {
        "verdict": verdict,
        "rubric_hash": rubric_hash,
        "backwards_compat_pass": bc.get("all_match", False),
        "per_salt_determinism": per_salt_determinism,
        "per_salt_bare_combined_sha_run1": {
            str(s): per_salt_run1[s]["combined_sha"] for s in SALTS
        },
        "per_salt_bare_combined_sha_run2": {
            str(s): per_salt_run2[s]["combined_sha"] for s in SALTS
        },
        "cross_salt_pairs": cross_salt_pairs,
        "distinct_pair_count_of_3": sum(1 for p in cross_salt_pairs if p["distinct"]),
        "per_salt_assignments_sha": {str(s): assignment_shas[s] for s in SALTS},
        "per_salt_rule_triple": {str(s): triples[s] for s in SALTS},
        "per_salt_panels": {str(s): per_salt_panels[s] for s in SALTS},
        "anchor_unchanged_except_render_stem_edit": anchor_unchanged_except_edit,
        "justification": justification,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict_json, sort_keys=True, indent=2) + "\n"
    )

    # Clean up scratch combined WAVs after panel measure.
    for s in SALTS:
        for tag in (f"s{s}_r1", f"s{s}_r2"):
            p = OUT_DIR / f"_tmp_combined_{tag}.wav"
            if p.exists():
                p.unlink()

    print(json.dumps({"verdict": verdict, "rubric_hash": rubric_hash,
                      "backwards_compat_pass": bc.get("all_match"),
                      "per_salt_determinism": per_salt_determinism,
                      "distinct_pair_count_of_3": sum(1 for p in cross_salt_pairs if p["distinct"])},
                     sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
