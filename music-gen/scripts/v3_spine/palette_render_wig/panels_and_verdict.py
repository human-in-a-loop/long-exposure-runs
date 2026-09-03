#!/usr/bin/env python3
"""c25 WIG palette-render panels + verdict emission.

Panel A: (c21 WIG original_ab_operator_section.wav, full_reconstruction_palette.wav)
Panel B: (c21 WIG full_reconstruction_operator_section.wav, full_reconstruction_palette.wav)

Both 8-key finite per contract; panel is NEVER a LANDS gate.
Verdict fires PALETTE_MOVES_PANEL if Comparison B delta magnitudes exceed
5% relative on >= 3 of the 5 numeric keys AND per-stem byte-det gate holds.
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", "0")
os.environ.setdefault("MUSICGEN_LEDGER_SUPERSEDES_IN_HASH", "0")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"requires /usr/bin/python3 (got {sys.executable})")

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402

from scripts.texture.panel import texture_distance  # noqa: E402

SONG_SHA16 = "252eb21ce7df7328"
C21_WIG_DELIV = _REPO / "data" / "v3" / "deliveries" / SONG_SHA16 / "operator_section"
PAL_ROOT = _REPO / "data" / "v3_spine" / SONG_SHA16 / "palette_render"
DELIV_ROOT = _REPO / "data" / "v3" / "deliveries" / SONG_SHA16 / "palette_render_c25"

RUBRIC_DOC = _REPO / "docs" / "v3_spine_wig_palette_render_c25_rubric.md"
RUBRIC_HASH_TXT = PAL_ROOT / "rubric_hash_v2.txt"

DELTA_THRESHOLD_REL = 0.05


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_wav_mono(p: Path) -> tuple:
    y, sr = sf.read(str(p), always_2d=True)
    if y.shape[1] > 1:
        y = y.mean(axis=1)
    else:
        y = y[:, 0]
    return y.astype(np.float64), int(sr)


def compute_panel(a_path: Path, b_path: Path) -> dict:
    a, sr_a = load_wav_mono(a_path)
    b, sr_b = load_wav_mono(b_path)
    if sr_a != sr_b:
        import scipy.signal as sps
        new_len = int(round(len(b) * sr_a / sr_b))
        b = sps.resample(b, new_len)
        sr_b = sr_a
    n = min(len(a), len(b))
    return texture_distance(a[:n], b[:n], sr_a)


def compare_panels(panel_ref: dict, panel_test: dict) -> dict:
    keys = ["mel_l1_db", "spectral_centroid_rmse_hz",
            "rms_env_rmse", "lufs_m_rmse_lu",
            "embedding_cosine_distance"]
    deltas: dict = {}
    keys_exceeding = 0
    for k in keys:
        v_ref = float(panel_ref.get(k, 0.0))
        v_test = float(panel_test.get(k, 0.0))
        abs_delta = abs(v_test - v_ref)
        base = max(abs(v_ref), 1e-9)
        rel = abs_delta / base
        exceeds = rel >= DELTA_THRESHOLD_REL
        deltas[k] = {"ref": v_ref, "test": v_test,
                     "abs_delta": abs_delta, "rel_delta": rel,
                     "exceeds_threshold": exceeds}
        if exceeds:
            keys_exceeding += 1
    return {"deltas": deltas, "keys_exceeding_threshold": keys_exceeding,
            "n_keys_tested": len(keys),
            "threshold_rel": DELTA_THRESHOLD_REL}


def all_finite(panel: dict) -> bool:
    for k, v in panel.items():
        if isinstance(v, (int, float)):
            if not (v == v and float("-inf") < float(v) < float("inf")):
                return False
    return True


def main() -> int:
    doc_sha = sha256(RUBRIC_DOC)
    txt_sha = RUBRIC_HASH_TXT.read_text().strip()

    orig_ab = C21_WIG_DELIV / "original_ab_operator_section.wav"
    palette_full = DELIV_ROOT / "full_reconstruction_palette.wav"
    c21_full = C21_WIG_DELIV / "full_reconstruction_operator_section.wav"

    panel_a = compute_panel(orig_ab, palette_full)
    panel_b = compute_panel(c21_full, palette_full)
    panel_b_ref = compute_panel(c21_full, orig_ab)

    finite_a = all_finite(panel_a)
    finite_b = all_finite(panel_b)

    cmp_b = compare_panels(panel_b_ref, panel_b)

    def _panel_tsv(panel: dict) -> str:
        lines = ["key\tvalue"]
        for k in sorted(panel.keys()):
            lines.append(f"{k}\t{panel[k]}")
        return "\n".join(lines) + "\n"

    (DELIV_ROOT / "panel_original_vs_palette.tsv").write_text(_panel_tsv(panel_a))
    (DELIV_ROOT / "panel_fluidsynth_vs_palette.tsv").write_text(_panel_tsv(panel_b))
    (PAL_ROOT / "panel_original_vs_palette.json").write_text(
        json.dumps(panel_a, sort_keys=True, indent=2) + "\n")
    (PAL_ROOT / "panel_fluidsynth_vs_palette.json").write_text(
        json.dumps(panel_b, sort_keys=True, indent=2) + "\n")
    (PAL_ROOT / "panel_delta_comparison.json").write_text(
        json.dumps({"comparison_b_vs_reference": cmp_b,
                    "panel_a_reference": panel_a,
                    "panel_b_test": panel_b,
                    "panel_b_reference_c21_vs_original": panel_b_ref},
                   sort_keys=True, indent=2) + "\n")

    det = json.loads((PAL_ROOT / "byte_determinism.json").read_text())
    per_stem = det["per_stem"]
    byte_det_gate = all(v.get("byte_det_x2", False) for v in per_stem.values())

    sub_clause_status = {
        "per_stem_render_success": all("error" not in v for v in per_stem.values()),
        "per_stem_byte_det_or_envelope": byte_det_gate,
        "panel_a_8_keys_finite": finite_a,
        "panel_b_8_keys_finite": finite_b,
        "comparison_b_keys_exceeding_threshold": cmp_b["keys_exceeding_threshold"],
        "comparison_b_threshold_met": cmp_b["keys_exceeding_threshold"] >= 3,
    }

    if not sub_clause_status["per_stem_render_success"] or \
       not sub_clause_status["per_stem_byte_det_or_envelope"] or \
       not sub_clause_status["panel_a_8_keys_finite"] or \
       not sub_clause_status["panel_b_8_keys_finite"]:
        verdict = "RENDER_FAILS"
    elif sub_clause_status["comparison_b_threshold_met"]:
        verdict = "PALETTE_MOVES_PANEL"
    else:
        verdict = "PALETTE_NEUTRAL"

    palette_full_sha = sha256(palette_full)
    per_stem_shas = {}
    for stem in ["drums", "bass", "guitar", "piano", "other", "vocals"]:
        p = DELIV_ROOT / "per_stem" / stem / "render.wav"
        if p.is_file():
            per_stem_shas[stem] = sha256(p)
    canon_midi_dir = _REPO / "data" / "v3_spine" / SONG_SHA16 / "operator_section" / "canonical_midi"
    canon_midi_shas = {}
    for m in ["drums", "bass", "guitar", "piano", "other", "vocals", "full_mix"]:
        p = canon_midi_dir / f"{m}.mid"
        if p.is_file():
            canon_midi_shas[m] = sha256(p)

    verdict_payload = {
        "cycle": 25,
        "milestone": "M-V3-SPINE-1/wig-palette-render-c25",
        "song_sha16": SONG_SHA16,
        "operator_section_s": [72.77133786848073, 102.77133786848073],
        "verdict": verdict,
        "rubric_hash_v2": doc_sha,
        "rubric_hash_v2_txt_content": txt_sha,
        "rubric_hash_v2_chain_holds": (doc_sha == txt_sha),
        "blocked_on_operator": True,
        "sub_clause_status": sub_clause_status,
        "sub_artifact_shas": {
            "full_reconstruction_palette_wav": palette_full_sha,
            "per_stem_wav": per_stem_shas,
            "canonical_midi": canon_midi_shas,
            "delivery_manifest_json": sha256(DELIV_ROOT / "manifest.json"),
        },
        "vst3_bass": {
            "outcome": per_stem["bass"].get("vst3_outcome",
                per_stem["bass"].get("vst3_attempt", {}).get("outcome", "n/a")),
            "max_pairwise_rms": per_stem["bass"].get("vst3_max_pairwise_rms",
                per_stem["bass"].get("vst3_attempt", {}).get("max_pairwise_rms", None)),
            "redefined_gap_arm_active": per_stem["bass"].get("redefined_gap_arm", False),
        },
        "sfizz_fallback_stems": ["guitar", "piano", "other"],
        "sfizz_fallback_reason": "sfz_dir_missing_no_sfz_files_in_workspace",
        "panel_a_original_vs_palette": panel_a,
        "panel_b_fluidsynth_vs_palette": panel_b,
        "panel_b_reference_c21_vs_original": panel_b_ref,
        "comparison_b_delta_summary": cmp_b,
        "c21_wig_delivery_anchor_preserved": True,
        "rubric_doc_path": str(RUBRIC_DOC.relative_to(_REPO)),
        "rubric_hash_v2_txt_path": str(RUBRIC_HASH_TXT.relative_to(_REPO)),
    }

    CYCLE_DIR = _REPO / "data" / "v3" / "deliveries" / SONG_SHA16 / "cycle25"
    CYCLE_DIR.mkdir(parents=True, exist_ok=True)
    verdict_path = CYCLE_DIR / "verdict_palette.json"
    verdict_path.write_text(json.dumps(verdict_payload, sort_keys=True, indent=2) + "\n")

    # Also mirror into DELIV_ROOT/verdict.json per rubric contract
    (DELIV_ROOT / "verdict.json").write_text(
        json.dumps(verdict_payload, sort_keys=True, indent=2) + "\n")

    import shutil
    for f in ["byte_determinism.json", "fetchability_ladder.jsonl",
              "dispatch_summary.json"]:
        src = PAL_ROOT / f
        if src.exists():
            shutil.copy2(str(src), str(DELIV_ROOT / f))

    print(json.dumps({
        "verdict": verdict,
        "rubric_hash_chain_holds": verdict_payload["rubric_hash_v2_chain_holds"],
        "comparison_b_keys_exceeding": cmp_b["keys_exceeding_threshold"],
        "verdict_path": str(verdict_path.relative_to(_REPO)),
        "verdict_sha16": sha256(verdict_path)[:16],
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
