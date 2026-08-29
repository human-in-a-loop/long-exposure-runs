#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T14:35:00Z
# cycle: 43
# run_id: fork-c320de981fda-clone-0
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-rated-corpus
# ---
"""c43 rated-corpus palette-driven batch orchestrator.

Sequence:
  1. Sample per-salt rule triples via c43 rated-corpus sampler.
  2. Derive per-stem parameter_dict per salt (c36 4×4 table verbatim).
  3. Render each salt TWICE into fresh tempfile.mkdtemp() dirs via c33
     render_stem (READ-ONLY import, parameter_dict populated).
  4. Assert SHA-256 equality per-salt across runs.
  5. Assert SHA-256 INequality between salts on bare_combined.wav.
  6. Measure M-TEX-1/panel on (original, palette-bare) AND
     (c9 fluidsynth-only, palette-bare) per salt.
  7. Snapshot anchor mtimes+SHAs pre/post.
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
from scripts.gen_palette_batch_rated_corpus.sample_rule_triple import (  # noqa: E402
    sample_triples, LEDGER_PATH as RATED_CORPUS_LEDGER,
)
from scripts.gen_palette_batch_rated_corpus.derive_parameter_dict import (  # noqa: E402
    derive_per_salt, payload_sha256,
)
from scripts.gen_palette_batch_rated_corpus.anchor_preservation import (  # noqa: E402
    write_pre as anchor_write_pre,
    write_post as anchor_write_post,
)

OUT_DIR = _REPO / "data" / "gen_palette_batch_rated_corpus"
SALTS = [0, 1, 2]
NUMERIC_KEYS = ("mel_l1_db", "spectral_centroid_rmse_hz",
                "rms_env_rmse", "lufs_m_rmse_lu")

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


def _sum_stems(stem_wavs, out_path: Path) -> str:
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


def _build_assignments(triple, per_stem_params):
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
            "assignment_sha": payload_sha256({
                "stem": stem, "instrument": inst,
                "rule_id": rid, "parameter_dict": pdict,
            }),
        })
    return rows


def _render_one_salt_run(assignments, tag: str) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix=f"c43_s_{tag}_"))
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
    keep = OUT_DIR / f"_tmp_combined_{tag}.wav"
    shutil.copy2(combined, keep)
    return {"tag": tag, "per_stem": per_stem, "combined_sha": combined_sha,
            "combined_wav": str(keep), "tempdir": str(tmp),
            "dispatch_records": dispatch_records}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Snapshot anchors PRE.
    _ = anchor_write_pre(OUT_DIR)
    pre = json.loads((OUT_DIR / "_anchor_pre.json").read_text())

    # Sample per-salt rule triples.
    triples = sample_triples(SALTS)
    per_salt_params = {s: derive_per_salt(triples[s], PER_STEM_DISPATCH) for s in SALTS}
    per_salt_assignments = {s: _build_assignments(triples[s], per_salt_params[s]) for s in SALTS}

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
    per_salt_run1 = {s: _render_one_salt_run(per_salt_assignments[s], f"s{s}_r1") for s in SALTS}
    per_salt_run2 = {s: _render_one_salt_run(per_salt_assignments[s], f"s{s}_r2") for s in SALTS}

    # Per-salt determinism + stable SHA files.
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

    # Rules-source pin: c40 anchor SHA.
    rules_source_sha = hashlib.sha256(RATED_CORPUS_LEDGER.read_bytes()).hexdigest()
    batch_manifest = {
        "rules_source_path": str(RATED_CORPUS_LEDGER.relative_to(_REPO)),
        "rules_source_sha256": rules_source_sha,
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

    # summary.tsv
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

    # Spread analysis.
    from scripts.gen_palette_batch_rated_corpus.spread_analysis import compute_spread
    spread = compute_spread(per_salt_panels)
    (OUT_DIR / "spread_analysis.json").write_text(
        json.dumps(spread, sort_keys=True, indent=2) + "\n"
    )

    # Verdict.
    rubric_hash = (OUT_DIR / "rubric_hash.txt").read_text().strip()
    verdict = None
    justification = {}

    if not all(per_salt_determinism.values()):
        verdict = "RATED_CORPUS_BATCH_FAILS"
        justification = {"reason": "per-salt determinism failure",
                         "per_salt_determinism": per_salt_determinism}
    else:
        panel_finite = True
        finite_counts = {"panel_original": 0, "panel_fluidsynth": 0}
        for s in SALTS:
            for panel_name in ("panel_original", "panel_fluidsynth"):
                panel = per_salt_panels[s][panel_name]
                if set(panel.keys()) != set(PUBLIC_KEYS):
                    panel_finite = False
                    justification.setdefault("panel_keys_missing", []).append((s, panel_name))
                per_salt_finite = True
                for k in NUMERIC_KEYS:
                    v = panel.get(k)
                    if v is None or not np.isfinite(v):
                        per_salt_finite = False
                        justification.setdefault("panel_non_finite", []).append((s, panel_name, k))
                if per_salt_finite:
                    finite_counts[panel_name] += 1

        distinct_count = sum(1 for p in cross_salt_pairs if p["distinct"])

        if not panel_finite:
            # Panel not finite on at least one salt-panel combo.
            # Per rubric §1: PARTIAL iff panel finite on ONLY ONE of the
            # two comparisons per salt, else FAILS.
            if (finite_counts["panel_original"] == len(SALTS)) ^ (finite_counts["panel_fluidsynth"] == len(SALTS)):
                verdict = "RATED_CORPUS_BATCH_PARTIAL"
                justification["reason"] = "panel finite on only one of two comparisons per salt"
                justification["cross_salt_pairs"] = cross_salt_pairs
            else:
                verdict = "RATED_CORPUS_BATCH_FAILS"
                justification["reason"] = "panel finiteness violated"
        elif distinct_count == 3:
            verdict = "RATED_CORPUS_BATCH_LANDS"
            justification = {"reason": "3/3 cross-salt bare_combined distinct",
                             "cross_salt_pairs": cross_salt_pairs,
                             "distinct_pair_count_of_3": 3}
        elif distinct_count == 2:
            verdict = "RATED_CORPUS_BATCH_PARTIAL"
            justification = {
                "reason": "2/3 cross-salt bare_combined distinct "
                          "(identical pair attributed to sfizz opcode-file "
                          "rewrite absence per c36 §7 fallback ladder)",
                "cross_salt_pairs": cross_salt_pairs,
                "distinct_pair_count_of_3": 2,
            }
        else:
            verdict = "RATED_CORPUS_BATCH_FAILS"
            justification = {
                "reason": f"{distinct_count}/3 cross-salt distinct — SPREAD_STILL_COLLAPSED family",
                "cross_salt_pairs": cross_salt_pairs,
                "distinct_pair_count_of_3": distinct_count,
            }

    # Anchor snapshot POST.
    post_result = anchor_write_post(OUT_DIR, pre)

    # Check rules-source preservation.
    rules_source_sha_post = hashlib.sha256(RATED_CORPUS_LEDGER.read_bytes()).hexdigest()
    if rules_source_sha != rules_source_sha_post:
        verdict = "RATED_CORPUS_BATCH_FAILS"
        justification["rules_source_drift"] = {
            "pre": rules_source_sha, "post": rules_source_sha_post,
        }

    if not post_result["unchanged"] and verdict != "RATED_CORPUS_BATCH_FAILS":
        # Any anchor drift → FAILS per rubric §1.
        verdict = "RATED_CORPUS_BATCH_FAILS"
        justification["anchor_drift"] = post_result["drift_rows"]

    verdict_json = {
        "verdict": verdict,
        "rubric_hash": rubric_hash,
        "rules_source_path": batch_manifest["rules_source_path"],
        "rules_source_sha256_pre": rules_source_sha,
        "rules_source_sha256_post": rules_source_sha_post,
        "rules_source_unchanged": rules_source_sha == rules_source_sha_post,
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
        "anchor_preservation": post_result,
        "justification": justification,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict_json, sort_keys=True, indent=2) + "\n"
    )

    # Clean up scratch combined WAVs.
    for s in SALTS:
        for tag in (f"s{s}_r1", f"s{s}_r2"):
            p = OUT_DIR / f"_tmp_combined_{tag}.wav"
            if p.exists():
                p.unlink()

    print(json.dumps({"verdict": verdict, "rubric_hash": rubric_hash,
                      "per_salt_determinism": per_salt_determinism,
                      "distinct_pair_count_of_3": sum(1 for p in cross_salt_pairs if p["distinct"]),
                      "anchor_unchanged": post_result["unchanged"],
                      "rules_source_unchanged": rules_source_sha == rules_source_sha_post},
                     sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
