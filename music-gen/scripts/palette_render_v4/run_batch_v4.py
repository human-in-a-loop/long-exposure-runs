#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T09:10:00Z
# cycle: 37
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v4
# ---
"""C37 clone-2 M-GEN-1/palette-driven-batch-v4 orchestrator.

Sequence:
  1. Sample per-salt rule triples via c35 sampler (READ-ONLY import),
     salts 0..7.
  2. Derive per-stem parameter_dict per salt via the rubric-fixed 8×8
     table.
  3. Render each salt TWICE into fresh tempfile.mkdtemp() dirs via the
     v4-extended render_stem (opcode-rewrite fallback active on sfizz).
  4. Assert SHA-256 equality per-salt across runs.
  5. Assert SHA-256 INequality between salts on bare_combined.wav.
  6. Measure M-TEX-1/panel on (original, palette-v4-bare) AND
     (c33 palette-v1-bare, palette-v4-bare) per salt.
  7. Snapshot anchor mtimes pre/post.
  8. Resolve verdict per the frozen rubric.
"""
from __future__ import annotations

import hashlib
import json
import shutil
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
from scripts.palette_render_v4.derive_parameter_dict_8x8 import (  # noqa: E402
    derive_per_salt, payload_sha256,
)

OUT_DIR = _REPO / "data" / "palette_render_v4"
SALTS = [0, 1, 2, 3, 4, 5, 6, 7]
NUMERIC_KEYS = ("mel_l1_db", "spectral_centroid_rmse_hz",
                "rms_env_rmse", "lufs_m_rmse_lu")

# c33 assignment (READ-ONLY): drums=fluidsynth_gm, bass=sfizz, other=sfizz.
PER_STEM_DISPATCH = {
    "drums": "fluidsynth_gm",
    "bass":  "sfizz",
    "other": "sfizz",
}

C33_ORIGINAL = _REPO / "data" / "tex" / "renders" / "synth_030s" / "original.wav"
C33_FLUIDSYNTH_BARE = _REPO / "data" / "tex" / "renders" / "synth_030s" / "bare_midi.wav"


def _read_wav(p: Path):
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
    dirs = ["scripts/palette",
            "scripts/palette_v2",
            "scripts/palette_probe",
            "scripts/palette_render",
            "scripts/palette_render_v3",
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
            "assignment_v4_sha": payload_sha256({
                "stem": stem, "instrument": inst,
                "rule_id": rid, "parameter_dict": pdict,
            }),
        })
    return rows


def _render_one_salt_run(assignments: list[dict], tag: str) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix=f"c37b_v4_{tag}_"))
    per_stem = []
    stem_wavs = []
    dispatch_records = []
    for a in assignments:
        stem_dir = tmp / a["stem"]
        try:
            r = render_stem(a["stem"], a["instrument"], stem_dir,
                            parameter_dict=a["parameter_dict"])
            threaded_note = None
            if a["instrument"] in ("fluidsynth", "fluidsynth_gm"):
                threaded_note = ("gain+chorus+reverb threaded via -o CLI opts; "
                                 "lp_cutoff+hp_cutoff recorded for provenance only "
                                 "(fluidsynth CLI has no direct LP/HP filter opcode; "
                                 "c38+ can promote via synth.reverb.damp / synth.chorus.speed).")
            elif a["instrument"] == "sfizz":
                threaded_note = ("master_volume threaded post-render (dB scale); "
                                 "cutoff+resonance threaded via c37 opcode-rewrite "
                                 "fallback (temp SFZ with fil_cutoff/fil_resonance).")
            dispatch_records.append({
                "stem": a["stem"],
                "instrument_used": a["instrument"],
                "instrument_requested": a["instrument"],
                "parameter_dict_threaded": a["parameter_dict"],
                "threaded_note": threaded_note,
                "sfizz_opcode_rewrite_active": (
                    a["instrument"] == "sfizz" and
                    ("cutoff" in a["parameter_dict"] or
                     "resonance" in a["parameter_dict"])
                ),
                "vst3_deferred": None,
            })
        except NotImplementedError as e:
            raise RuntimeError(f"VST3 branch triggered on stem {a['stem']} — rubric violation") from e
        per_stem.append(r)
        stem_wavs.append(Path(r["run1_wav_path"]))
    combined = tmp / "bare_combined.wav"
    combined_sha = _sum_stems(stem_wavs, combined)
    keep = OUT_DIR / f"_tmp_combined_{tag}.wav"
    shutil.copy2(combined, keep)
    return {"tag": tag, "per_stem": per_stem, "combined_sha": combined_sha,
            "combined_wav": str(keep), "tempdir": str(tmp),
            "dispatch_records": dispatch_records}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    anchor_pre = _snapshot_anchor_shas()

    triples = sample_triples(SALTS)  # {salt: {rule_type: rule_id}}

    per_salt_params = {
        s: derive_per_salt(triples[s], PER_STEM_DISPATCH) for s in SALTS
    }
    per_salt_assignments = {
        s: _build_assignments(triples[s], per_salt_params[s]) for s in SALTS
    }

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

    per_salt_run1: dict[int, dict] = {}
    per_salt_run2: dict[int, dict] = {}
    for s in SALTS:
        per_salt_run1[s] = _render_one_salt_run(per_salt_assignments[s], f"s{s}_r1")
        per_salt_run2[s] = _render_one_salt_run(per_salt_assignments[s], f"s{s}_r2")

    per_salt_determinism: dict[int, bool] = {}
    for s in SALTS:
        r1c = per_salt_run1[s]["combined_sha"]
        r2c = per_salt_run2[s]["combined_sha"]
        per_salt_determinism[s] = (r1c == r2c)
        song_dir = per_song_dir / str(s)
        (song_dir / "bare_combined.wav.sha.run1").write_text(r1c + "\n")
        (song_dir / "bare_combined.wav.sha.run2").write_text(r2c + "\n")
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
        (song_dir / "dispatch_summary.json").write_text(
            json.dumps({"salt": s,
                        "records": per_salt_run1[s]["dispatch_records"]},
                       sort_keys=True, indent=2) + "\n"
        )

    # Cross-salt inequality on bare_combined: C(8,2)=28 pairs.
    cross_salt_pairs = []
    for a in range(len(SALTS)):
        for b in range(a + 1, len(SALTS)):
            sa = per_salt_run1[SALTS[a]]["combined_sha"]
            sb = per_salt_run1[SALTS[b]]["combined_sha"]
            cross_salt_pairs.append({
                "salt_a": SALTS[a], "salt_b": SALTS[b],
                "sha_a": sa, "sha_b": sb, "distinct": sa != sb,
            })
    distinct_pair_count = sum(1 for p in cross_salt_pairs if p["distinct"])

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
        "cross_salt_pair_count": len(cross_salt_pairs),
        "cross_salt_distinct_count": distinct_pair_count,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (OUT_DIR / "batch_manifest.json").write_text(
        json.dumps(batch_manifest, sort_keys=True, indent=2) + "\n"
    )

    # summary.tsv
    lines = ["\t".join(["salt", "combined_sha_r1", "combined_sha_r2", "det_equal"])]
    for s in SALTS:
        c1 = per_salt_run1[s]["combined_sha"]
        c2 = per_salt_run2[s]["combined_sha"]
        lines.append("\t".join([str(s), c1, c2, str(c1 == c2)]))
    (OUT_DIR / "summary.tsv").write_text("\n".join(lines) + "\n")

    rubric_hash = (OUT_DIR / "rubric_hash.txt").read_text().strip()
    bc = json.loads((OUT_DIR / "backwards_compat_check.json").read_text())

    verdict = None
    justification: dict = {}
    if not bc.get("all_match"):
        verdict = "RENDER_FAILS"
        justification = {"reason": "backwards_compat_check failed",
                         "backwards_compat_check": bc}
    elif not all(per_salt_determinism.values()):
        verdict = "RENDER_FAILS"
        justification = {"reason": "per-salt determinism failure",
                         "per_salt_determinism": per_salt_determinism}
    else:
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
            if distinct_pair_count >= 22:
                verdict = "PARAM_MOVES_AUDIO"
                justification = {
                    "reason": f"{distinct_pair_count}/28 cross-salt bare_combined pairs distinct "
                              f"(>= 22 threshold; deeper 8×8 perturbation + sfizz opcode-rewrite "
                              f"diversifies audio).",
                    "cross_salt_distinct_count": distinct_pair_count,
                }
            else:
                verdict = "PARAM_NEUTRAL"
                justification = {
                    "reason": f"{distinct_pair_count}/28 cross-salt bare_combined pairs distinct "
                              f"(< 22 threshold; deeper table + opcode rewrite did not diversify "
                              f"beyond noise).",
                    "cross_salt_distinct_count": distinct_pair_count,
                }

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
            "sha_pre_run": anchor_pre.get(render_stem_rel),
            "sha_post_run": anchor_post.get(render_stem_rel),
            "description": ("v4 grows sfizz dispatch branch to invoke opcode-rewrite "
                            "fallback (lazy import of scripts.palette_render_v4."
                            "extend_sfizz_opcode_rewrite.rewrite_sfz_to_temp when "
                            "parameter_dict contains 'cutoff' or 'resonance'). VST3 "
                            "branches unchanged (still raise NotImplementedError). "
                            "c33 anchor path (parameter_dict=None) byte-identical "
                            "per backwards_compat_check.json."),
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
        "cross_salt_pair_count": len(cross_salt_pairs),
        "cross_salt_distinct_count": distinct_pair_count,
        "cross_salt_pairs": cross_salt_pairs,
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

    for s in SALTS:
        for tag in (f"s{s}_r1", f"s{s}_r2"):
            p = OUT_DIR / f"_tmp_combined_{tag}.wav"
            if p.exists():
                p.unlink()

    print(json.dumps({"verdict": verdict, "rubric_hash": rubric_hash,
                      "backwards_compat_pass": bc.get("all_match"),
                      "per_salt_determinism_all": all(per_salt_determinism.values()),
                      "cross_salt_pair_count": len(cross_salt_pairs),
                      "cross_salt_distinct_count": distinct_pair_count},
                     sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
