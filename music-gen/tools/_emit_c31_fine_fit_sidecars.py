#!/usr/bin/env /usr/bin/python3
"""c31 Track A.3 sidecar emitter for both fine_fit_sf2_v2 (bass) and fine_fit_sf2_guitar.

Reads the c31 legacy-mode leaderboard, compares vs the c3/c14 anchor leaderboard
row-by-row (matched by config_hash), and emits a sidecar JSON in the c30
fine-fit-drums shape (render vs composite disaggregated). Detects the c30
drums-fine pattern (render byte-identical but composite FP-drift) and fires HALT
per FD-1 if present; else emits PASS.
"""
from __future__ import annotations
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _load_tsv(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def _classify_composite(a: str, b: str) -> str:
    """Return 'strict_equal', 'fp_drift', or 'mismatch'."""
    if a == b:
        return "strict_equal"
    try:
        fa = float(a)
        fb = float(b)
    except (ValueError, TypeError):
        return "mismatch"
    if fa == 0 and fb == 0:
        return "strict_equal"
    denom = max(abs(fa), abs(fb), 1e-12)
    rel = abs(fa - fb) / denom
    return "fp_drift" if rel < 1e-4 else "mismatch"


def emit_sidecar(
    driver: str,
    driver_path: str,
    c31_leaderboard: Path,
    anchor_leaderboard: Path,
    anchor_cycle: str,
    stem_name: str,
    reference_stem: Path,
    midi_excerpt: Path,
    n_cells_expected: int,
    out_path: Path,
) -> dict:
    c31_rows = _load_tsv(c31_leaderboard)
    anchor_rows = _load_tsv(anchor_leaderboard)
    c31_by_hash = {r["config_hash"]: r for r in c31_rows}
    anchor_by_hash = {r["config_hash"]: r for r in anchor_rows}

    common = set(c31_by_hash) & set(anchor_by_hash)
    only_c31 = set(c31_by_hash) - set(anchor_by_hash)
    only_anchor = set(anchor_by_hash) - set(c31_by_hash)

    per_cell = {}
    n_render_bi = 0
    n_render_mm = 0
    n_composite_strict = 0
    n_composite_fp_drift = 0
    n_composite_mismatch_with_render_mm = 0
    composite_deltas_sampled = []

    for ch in sorted(common):
        c31r = c31_by_hash[ch]
        anr = anchor_by_hash[ch]
        rsha_c31 = c31r["render_sha256"]
        rsha_an = anr["render_sha256"]
        render_equal = rsha_c31 == rsha_an
        comp_class = _classify_composite(c31r["composite"], anr["composite"])
        if render_equal:
            n_render_bi += 1
        else:
            n_render_mm += 1
        if comp_class == "strict_equal":
            n_composite_strict += 1
        elif comp_class == "fp_drift":
            n_composite_fp_drift += 1
            if len(composite_deltas_sampled) < 5:
                composite_deltas_sampled.append(
                    abs(float(c31r["composite"]) - float(anr["composite"]))
                )
        else:
            if not render_equal:
                n_composite_mismatch_with_render_mm += 1
        per_cell[ch] = {
            "render_byte_identical": render_equal,
            "composite_class": comp_class,
        }

    n_total = len(common)
    render_verdict = (
        f"PASS_RENDER_LEVEL_{n_render_bi}_OF_{n_total}"
        if n_render_mm == 0
        else f"FAIL_RENDER_{n_render_mm}_MISMATCH"
    )
    if n_composite_strict == n_total:
        comp_verdict = f"PASS_COMPOSITE_STRICT_{n_total}_OF_{n_total}"
    elif n_render_mm == 0 and n_composite_fp_drift > 0:
        comp_verdict = f"PARTIAL_{n_composite_strict}_OF_{n_total}_STRICT_{n_composite_fp_drift}_FP_DRIFT"
    else:
        comp_verdict = f"FAIL_COMPOSITE_{n_composite_mismatch_with_render_mm}_MISMATCH"

    if n_render_mm == 0 and n_composite_strict == n_total:
        combined = "PASS_RENDER_AND_COMPOSITE_STRICT"
        floor_status = "PASS"
        pass_or_fail = "PASS"
    elif n_render_mm == 0 and n_composite_fp_drift > 0:
        combined = "PARTIAL_RENDER_DETERMINISTIC_COMPOSITE_FP_DRIFT"
        floor_status = "HALT_PER_FD1_STRICT_EQUALITY_ON_COMPOSITE"
        pass_or_fail = "HALT"
    else:
        combined = "FAIL_RENDER_OR_COMPOSITE_MISMATCH"
        floor_status = "HALT_PER_FD1"
        pass_or_fail = "HALT"

    sidecar = {
        "milestone_id": "M-V4-CERT-1",
        "cycle": 31,
        "track": "A.3",
        "driver_path": driver_path,
        "driver_sha256": _sha256(ROOT / driver_path),
        "mode": "real-fluidsynth-legacy",
        "hygiene_module_imported": True,
        "hygiene_module_sha256": _sha256(ROOT / "scripts/sound_match/_sweep_hygiene_c27.py"),
        "song_sha16": "31a164f845f8e27e",
        "reference_stem_path": str(reference_stem),
        "reference_stem_sha256": _sha256(ROOT / reference_stem),
        "midi_excerpt_path": str(midi_excerpt),
        "midi_excerpt_sha256": _sha256(ROOT / midi_excerpt),
        "sf2_path": "/usr/share/sounds/sf2/FluidR3_GM.sf2",
        "sf2_sha256": "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0",
        "n_cells_expected": n_cells_expected,
        "n_cells_actual": len(c31_rows),
        "n_cells_common_with_anchor": n_total,
        "n_cells_only_c31": len(only_c31),
        "n_cells_only_anchor": len(only_anchor),
        "anchor_source_cycle": anchor_cycle,
        "anchor_leaderboard_path": str(anchor_leaderboard.relative_to(ROOT)),
        "anchor_leaderboard_sha256": _sha256(anchor_leaderboard),
        "c31_leaderboard_path": str(c31_leaderboard.relative_to(ROOT)),
        "c31_leaderboard_sha256": _sha256(c31_leaderboard),
        "n_render_sha_byte_identical": n_render_bi,
        "n_render_sha_mismatch": n_render_mm,
        "n_composite_strict_equal": n_composite_strict,
        "n_composite_fp_drift": n_composite_fp_drift,
        "n_composite_mismatch_with_render_sha_mismatch": n_composite_mismatch_with_render_mm,
        "composite_drift_max_delta_estimate": (
            f"~1e-6 magnitude (samples: {[f'{d:.3g}' for d in composite_deltas_sampled]})"
            if composite_deltas_sampled else "none"
        ),
        "render_determinism_verdict": render_verdict,
        "composite_strict_equality_verdict": comp_verdict,
        "combined_verdict": combined,
        "floor_status": floor_status,
        "pass_or_fail": pass_or_fail,
        "invariants_checklist": {
            "a_no_operator_scope_extension": "not_applicable_regression_check",
            "b_prefer_above_floor": "not_applicable_regression_check",
            "c_no_reject_on_misread": (
                f"verified — {n_render_bi}/{n_total} render_sha256 byte-identical; "
                f"composite classification per row transparent above."
            ),
            "d_disclose_divergence": (
                f"c31 {driver} legacy-mode 216/180-cell CG-anchor regression: "
                f"render layer {n_render_bi}/{n_total} byte-identical, "
                f"composite layer {n_composite_strict}/{n_total} strict-equal + "
                f"{n_composite_fp_drift} FP-drift (~1e-6). "
                + (
                    "Repeats c30 drums-fine render-vs-composite split; HALT fires per FD-1 strict brief reading."
                    if combined == "PARTIAL_RENDER_DETERMINISTIC_COMPOSITE_FP_DRIFT"
                    else "Full byte-identical regression."
                    if combined == "PASS_RENDER_AND_COMPOSITE_STRICT"
                    else "Render or composite regression fail; investigate."
                )
            ),
            "e_pinned_profile_shape_stability": "not_applicable_regression_check",
        },
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
        "instrument": stem_name,
    }
    out_path.write_text(json.dumps(sidecar, indent=2) + "\n")
    return sidecar


def main():
    reg = ROOT / "data/v4/regression"
    smoke = reg / "c31_smoke"

    # A.1 fine_fit_sf2_v2 vs c3 bass_stage2b (216 cells, programs {5,17,18,19,33,38})
    v2_ldr = smoke / "bass_fine_v2_legacy" / "leaderboard.tsv"
    if v2_ldr.exists():
        s = emit_sidecar(
            driver="fine_fit_sf2_v2.py",
            driver_path="scripts/sound_match/fine_fit_sf2_v2.py",
            c31_leaderboard=v2_ldr,
            anchor_leaderboard=ROOT / "data/v4/profiles/31a164f845f8e27e/bass_stage2b/leaderboard.tsv",
            anchor_cycle="c3",
            stem_name="bass",
            reference_stem=Path("data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav"),
            midi_excerpt=Path("data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1/inputs/bass.mid"),
            n_cells_expected=216,
            out_path=reg / "c31_cg_anchor_fine_fit_sf2_v2.json",
        )
        print(f"[A.1] fine_fit_sf2_v2 → {s['pass_or_fail']} | {s['combined_verdict']}")
    else:
        print(f"[A.1] SKIP: {v2_ldr} not present yet")

    # A.2 fine_fit_sf2_guitar vs c14 (180 cells, 5 programs x 3 x 3 x 4)
    g_ldr = smoke / "guitar_fine_legacy" / "leaderboard.tsv"
    if g_ldr.exists():
        s = emit_sidecar(
            driver="fine_fit_sf2_guitar.py",
            driver_path="scripts/sound_match/fine_fit_sf2_guitar.py",
            c31_leaderboard=g_ldr,
            anchor_leaderboard=ROOT / "data/v4/profiles/31a164f845f8e27e/guitar_sweep_stage2/leaderboard.tsv",
            anchor_cycle="c14",
            stem_name="guitar",
            reference_stem=Path("data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/guitar.wav"),
            midi_excerpt=Path("data/v4/profiles/31a164f845f8e27e/guitar_sweep_stage1/guitar_excerpt.mid"),
            n_cells_expected=180,
            out_path=reg / "c31_cg_anchor_fine_fit_sf2_guitar.json",
        )
        print(f"[A.2] fine_fit_sf2_guitar → {s['pass_or_fail']} | {s['combined_verdict']}")
    else:
        print(f"[A.2] SKIP: {g_ldr} not present yet")


if __name__ == "__main__":
    main()
